"""Controlled Codex execution adapter for supervised pipeline sessions."""

from __future__ import annotations

import hashlib
import inspect
import re
import shlex
import subprocess
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ai_project_ctl import task_reports as task_report_service
from ai_project_ctl.core.store import StoreError, read_json_file

from .codex_summary_parser import (
    CODEX_SUMMARY_BLOCK_MISSING,
    parse_codex_summary_stdout,
)
from .policy import CodexAdapterMode, CodexExecutionMode, PipelinePolicy, PromptTransport
from .report_builder import ReportBuilderError, build_task_report_payload
from .state import task_reports_state_path, tasks_state_path
from .token_budget import PASS as TOKEN_BUDGET_PASS
from .token_budget import TokenBudgetGateResult


CODE_DRY_RUN = "CODEX_ADAPTER_DRY_RUN"
CODE_MANUAL_HANDOFF = "CODEX_ADAPTER_MANUAL_HANDOFF_REQUIRED"
CODE_POLICY_DENIED = "CODEX_ADAPTER_POLICY_DENIED"
CODE_PROMPT_MISSING = "CODEX_ADAPTER_PROMPT_MISSING"
CODE_PROMPT_STALE = "CODEX_ADAPTER_PROMPT_STALE"
CODE_LOCAL_COMMAND_FAILED = "CODEX_ADAPTER_LOCAL_COMMAND_FAILED"
CODE_SANDBOX_UNAVAILABLE = "CODEX_ADAPTER_SANDBOX_UNAVAILABLE"
CODE_LOCAL_COMMAND_TIMEOUT = "CODEX_ADAPTER_TIMEOUT"
CODE_REPORT_MISSING = "CODEX_ADAPTER_REPORT_MISSING"
CODE_REPORT_INVALID = "CODEX_ADAPTER_REPORT_INVALID"
CODE_SUMMARY_MISSING = "CODEX_ADAPTER_SUMMARY_MISSING"
CODE_SUMMARY_INVALID = "CODEX_ADAPTER_SUMMARY_INVALID"
CODE_LOCAL_COMMAND_PASSED = "CODEX_ADAPTER_LOCAL_COMMAND_PASSED"
OUTPUT_SNIPPET_BYTES = 1200

PROMPT_TASK_RE = re.compile(
    r"^(?:Source ID|Source Task|Task ID):\s*`?(?P<task>[A-Za-z0-9_-]+)`?\s*$",
    re.MULTILINE,
)
SANDBOX_UNAVAILABLE_RE = re.compile(
    r"bwrap|bubblewrap|loopback|RTM_NEWADDR|Operation not permitted|user namespace|userns|unshare",
    re.IGNORECASE,
)
OutputRunner = Callable[..., subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class CodexAdapterResult:
    """Bounded result metadata safe to store in pipeline gate details."""

    status: str
    code: str
    reason: str
    mode: str
    started_at: str
    finished_at: str
    duration_sec: float
    prompt_path: str = ""
    prompt_sha256: str = ""
    prompt_transport: str = ""
    command: tuple[str, ...] = ()
    command_ref: str = ""
    timeout_sec: int = 0
    timed_out: bool = False
    returncode: int | None = None
    stdout_ref: str = ""
    stderr_ref: str = ""
    stdout_snippet: str = ""
    stderr_snippet: str = ""
    stdout_bytes: int = 0
    stderr_bytes: int = 0
    runtime_logs: Mapping[str, Any] = field(default_factory=dict)
    report_required: bool = True
    before_report_id: str = ""
    after_report_id: str = ""
    report_id: str = ""
    report_parse_code: str = ""
    report_parse_issue: Mapping[str, Any] = field(default_factory=dict)
    report_submission_error: str = ""
    report_builder_evidence: Mapping[str, Any] = field(default_factory=dict)
    report_instruction: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "passed"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "code": self.code,
            "reason": self.reason,
            "mode": self.mode,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_sec": self.duration_sec,
            "prompt_path": self.prompt_path,
            "prompt_sha256": self.prompt_sha256,
            "prompt_transport": self.prompt_transport,
            "command": list(self.command),
            "command_ref": self.command_ref,
            "timeout_sec": self.timeout_sec,
            "timed_out": self.timed_out,
            "returncode": self.returncode,
            "stdout_ref": self.stdout_ref,
            "stderr_ref": self.stderr_ref,
            "stdout_snippet": self.stdout_snippet,
            "stderr_snippet": self.stderr_snippet,
            "stdout_bytes": self.stdout_bytes,
            "stderr_bytes": self.stderr_bytes,
            "runtime_logs": dict(self.runtime_logs),
            "report_required": self.report_required,
            "before_report_id": self.before_report_id,
            "after_report_id": self.after_report_id,
            "report_id": self.report_id,
            "report_parse_code": self.report_parse_code,
            "report_parse_issue": dict(self.report_parse_issue),
            "report_submission_error": self.report_submission_error,
            "report_builder_evidence": dict(self.report_builder_evidence),
            "report_instruction": self.report_instruction,
        }


def run_codex_adapter(
    *,
    root: str | Path = ".",
    task_id: str,
    policy: PipelinePolicy,
    token_gate: TokenBudgetGateResult,
    runner: OutputRunner | None = None,
    session_id: str = "",
) -> CodexAdapterResult:
    """Run or prepare Codex execution after policy and token gates pass."""

    root_path = Path(root).resolve()
    started_monotonic = time.monotonic()
    started_at = _utc_now()
    prompt_path = Path(token_gate.prompt_path) if token_gate.prompt_path else _default_prompt(root_path)
    if not prompt_path.is_absolute():
        prompt_path = root_path / prompt_path
    prompt_path = prompt_path.resolve()
    prompt_text = ""

    def finish(
        *,
        status: str,
        code: str,
        reason: str,
        command: Sequence[str] = (),
        timed_out: bool = False,
        returncode: int | None = None,
        stdout: str = "",
        stderr: str = "",
        runtime_logs: Mapping[str, Any] | None = None,
        before_report_id: str = "",
        after_report_id: str = "",
        report_id: str = "",
        report_parse_code: str = "",
        report_parse_issue: Mapping[str, Any] | None = None,
        report_submission_error: str = "",
        report_builder_evidence: Mapping[str, Any] | None = None,
        report_instruction: str = "",
    ) -> CodexAdapterResult:
        finished_at = _utc_now()
        duration = max(0.0, time.monotonic() - started_monotonic)
        stdout_bytes, stdout_ref = _output_ref("stdout", stdout)
        stderr_bytes, stderr_ref = _output_ref("stderr", stderr)
        stdout_snippet = _output_snippet(stdout, prompt_text)
        stderr_snippet = _output_snippet(stderr, prompt_text)
        command_tuple = tuple(str(part) for part in command)
        return CodexAdapterResult(
            status=status,
            code=code,
            reason=reason,
            mode=policy.codex.adapter_mode.value,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=round(duration, 6),
            prompt_path=str(prompt_path),
            prompt_sha256=token_gate.prompt_sha256,
            prompt_transport=policy.codex.prompt_transport.value,
            command=command_tuple,
            command_ref=shlex.join(command_tuple) if command_tuple else "",
            timeout_sec=policy.codex.timeout_sec,
            timed_out=timed_out,
            returncode=returncode,
            stdout_ref=stdout_ref,
            stderr_ref=stderr_ref,
            stdout_snippet=stdout_snippet,
            stderr_snippet=stderr_snippet,
            stdout_bytes=stdout_bytes,
            stderr_bytes=stderr_bytes,
            runtime_logs=dict(runtime_logs or {}),
            report_required=policy.codex.require_report,
            before_report_id=before_report_id,
            after_report_id=after_report_id,
            report_id=report_id,
            report_parse_code=report_parse_code,
            report_parse_issue=dict(report_parse_issue or {}),
            report_submission_error=report_submission_error,
            report_builder_evidence=dict(report_builder_evidence or {}),
            report_instruction=report_instruction,
        )

    if policy.codex.mode != CodexExecutionMode.RUN_CODEX:
        return finish(
            status="blocked",
            code=CODE_POLICY_DENIED,
            reason="policy_mode_does_not_allow_codex_execution",
        )
    if token_gate.status != TOKEN_BUDGET_PASS:
        return finish(
            status="blocked",
            code=CODE_POLICY_DENIED,
            reason="token_budget_gate_not_passed",
        )

    prompt_check, prompt_text = _validate_prompt(
        prompt_path, task_id, token_gate.prompt_sha256
    )
    if prompt_check:
        return finish(**prompt_check)

    instruction = _report_instruction(task_id)
    if policy.codex.adapter_mode == CodexAdapterMode.DRY_RUN:
        return finish(
            status="blocked",
            code=CODE_DRY_RUN,
            reason="dry_run_no_external_execution",
            report_instruction=instruction,
        )
    if policy.codex.adapter_mode == CodexAdapterMode.MANUAL_HANDOFF:
        return finish(
            status="blocked",
            code=CODE_MANUAL_HANDOFF,
            reason="manual_handoff_required",
            report_instruction=instruction,
        )
    if policy.codex.adapter_mode != CodexAdapterMode.LOCAL_COMMAND:
        return finish(
            status="failed",
            code=CODE_POLICY_DENIED,
            reason="unsupported_adapter_mode",
            report_instruction=instruction,
        )
    if policy.codex.prompt_transport != PromptTransport.STDIN:
        return finish(
            status="failed",
            code=CODE_POLICY_DENIED,
            reason="unsupported_prompt_transport",
            report_instruction=instruction,
        )

    command = tuple(policy.codex.local_command)
    command_key = shlex.join(command)
    if not command or command_key not in set(policy.codex.command_allowlist):
        return finish(
            status="failed",
            code=CODE_POLICY_DENIED,
            reason="local_command_not_allowlisted",
            command=command,
            report_instruction=instruction,
        )

    before_report = _latest_report_id(root_path, task_id)
    try:
        command_run = _run_local_command(
            command,
            root=root_path,
            timeout_sec=policy.codex.timeout_sec,
            prompt_text=prompt_text,
            prompt_transport=policy.codex.prompt_transport,
            runner=runner,
            session_id=session_id,
            task_id=task_id,
        )
    except subprocess.TimeoutExpired as exc:
        after_report = _latest_report_id(root_path, task_id)
        return finish(
            status="failed",
            code=CODE_LOCAL_COMMAND_TIMEOUT,
            reason="local_command_timeout",
            command=command,
            timed_out=True,
            stdout=_decode_output(exc.stdout),
            stderr=_decode_output(exc.stderr),
            runtime_logs=getattr(exc, "runtime_logs", {}),
            before_report_id=before_report,
            after_report_id=after_report,
            report_instruction=instruction,
        )

    completed = command_run.completed
    runtime_logs = command_run.runtime_logs
    stdout = _decode_output(completed.stdout)
    stderr = _decode_output(completed.stderr)
    if completed.returncode != 0:
        after_report = _latest_report_id(root_path, task_id)
        if _is_sandbox_unavailable(stdout, stderr):
            return finish(
                status="blocked",
                code=CODE_SANDBOX_UNAVAILABLE,
                reason="codex_sandbox_unavailable",
                command=command,
                returncode=completed.returncode,
                stdout=stdout,
                stderr=stderr,
                runtime_logs=runtime_logs,
                before_report_id=before_report,
                after_report_id=after_report,
                report_instruction=instruction,
            )
        return finish(
            status="failed",
            code=CODE_LOCAL_COMMAND_FAILED,
            reason="local_command_nonzero_exit",
            command=command,
            returncode=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            runtime_logs=runtime_logs,
            before_report_id=before_report,
            after_report_id=after_report,
            report_instruction=instruction,
        )

    after_report = _latest_report_id(root_path, task_id)
    if after_report and after_report != before_report:
        report_id = after_report
        return finish(
            status="passed",
            code=CODE_LOCAL_COMMAND_PASSED,
            reason="local_command_completed_with_report",
            command=command,
            returncode=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            runtime_logs=runtime_logs,
            before_report_id=before_report,
            after_report_id=after_report,
            report_id=report_id,
            report_instruction=instruction,
        )

    summary_parse = parse_codex_summary_stdout(stdout)
    if summary_parse.ok:
        try:
            submission, builder_evidence = _submit_built_summary_report(
                root_path,
                task_id=task_id,
                summary=summary_parse.summary or {},
                token_gate=token_gate,
                command=command,
                started_monotonic=started_monotonic,
                returncode=completed.returncode,
                stdout=stdout,
                stderr=stderr,
                runtime_logs=runtime_logs,
                session_id=session_id,
            )
        except ReportBuilderError as exc:
            return finish(
                status="blocked",
                code=CODE_REPORT_INVALID,
                reason="built_execution_report_invalid",
                command=command,
                returncode=completed.returncode,
                stdout=stdout,
                stderr=stderr,
                runtime_logs=runtime_logs,
                before_report_id=before_report,
                after_report_id=after_report,
                report_parse_code=summary_parse.code,
                report_submission_error=str(exc),
                report_instruction=instruction,
            )
        except task_report_service.TaskReportError as exc:
            return finish(
                status="blocked",
                code=CODE_REPORT_INVALID,
                reason="built_execution_report_rejected",
                command=command,
                returncode=completed.returncode,
                stdout=stdout,
                stderr=stderr,
                runtime_logs=runtime_logs,
                before_report_id=before_report,
                after_report_id=after_report,
                report_parse_code=summary_parse.code,
                report_submission_error=str(exc),
                report_instruction=instruction,
            )
        after_report = submission.report_id
    elif summary_parse.code == CODEX_SUMMARY_BLOCK_MISSING:
        return finish(
            status="blocked",
            code=CODE_SUMMARY_MISSING,
            reason="codex_execution_summary_missing",
            command=command,
            returncode=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            runtime_logs=runtime_logs,
            before_report_id=before_report,
            after_report_id=after_report,
            report_parse_code=summary_parse.code,
            report_parse_issue=(
                summary_parse.issue.to_dict() if summary_parse.issue is not None else {}
            ),
            report_instruction=instruction,
        )
    else:
        return finish(
            status="blocked",
            code=CODE_SUMMARY_INVALID,
            reason="codex_execution_summary_invalid",
            command=command,
            returncode=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            runtime_logs=runtime_logs,
            before_report_id=before_report,
            after_report_id=after_report,
            report_parse_code=summary_parse.code,
            report_parse_issue=(
                summary_parse.issue.to_dict() if summary_parse.issue is not None else {}
            ),
            report_instruction=instruction,
        )

    if policy.codex.require_report and (not after_report or after_report == before_report):
        return finish(
            status="blocked",
            code=CODE_REPORT_MISSING,
            reason="structured_execution_report_missing",
            command=command,
            returncode=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            runtime_logs=runtime_logs,
            before_report_id=before_report,
            after_report_id=after_report,
            report_instruction=instruction,
        )

    report_id = (
        after_report
        if after_report
        and (not policy.codex.require_report or after_report != before_report)
        else ""
    )
    return finish(
        status="passed",
        code=CODE_LOCAL_COMMAND_PASSED,
        reason="local_command_completed_with_report",
        command=command,
        returncode=completed.returncode,
        stdout=stdout,
        stderr=stderr,
        runtime_logs=runtime_logs,
        before_report_id=before_report,
        after_report_id=after_report,
        report_id=report_id,
        report_parse_code=summary_parse.code if summary_parse.ok else "",
        report_builder_evidence=builder_evidence if summary_parse.ok else {},
        report_instruction=instruction,
    )


@dataclass(frozen=True)
class _LocalCommandRun:
    completed: subprocess.CompletedProcess[str]
    runtime_logs: Mapping[str, Any]


class _LocalCommandTimeout(subprocess.TimeoutExpired):
    def __init__(
        self,
        *,
        cmd: Sequence[str],
        timeout: int,
        output: bytes,
        stderr: bytes,
        runtime_logs: Mapping[str, Any],
    ) -> None:
        super().__init__(cmd=cmd, timeout=timeout, output=output, stderr=stderr)
        self.runtime_logs = runtime_logs


def _validate_prompt(
    prompt_path: Path,
    task_id: str,
    expected_sha256: str,
) -> tuple[dict[str, Any], str]:
    if not prompt_path.exists():
        return (
            {
                "status": "failed",
                "code": CODE_PROMPT_MISSING,
                "reason": "prompt_missing",
            },
            "",
        )

    prompt_bytes = prompt_path.read_bytes()
    actual_sha = hashlib.sha256(prompt_bytes).hexdigest()
    if expected_sha256 and actual_sha != expected_sha256:
        return (
            {
                "status": "failed",
                "code": CODE_PROMPT_STALE,
                "reason": "prompt_changed_after_token_gate",
            },
            "",
        )
    prompt_text = prompt_bytes.decode("utf-8", errors="replace")
    task_ids = {
        match.group("task") for match in PROMPT_TASK_RE.finditer(prompt_text[:8000])
    }
    if task_ids and task_id not in task_ids:
        return (
            {
                "status": "failed",
                "code": CODE_PROMPT_STALE,
                "reason": "prompt_task_mismatch",
            },
            "",
        )
    if not task_ids and task_id not in prompt_text[:4000]:
        return (
            {
                "status": "failed",
                "code": CODE_PROMPT_STALE,
                "reason": "prompt_task_id_missing",
            },
            "",
        )
    return {}, prompt_text


def _run_local_command(
    command: Sequence[str],
    *,
    root: Path,
    timeout_sec: int,
    prompt_text: str,
    prompt_transport: PromptTransport,
    runner: OutputRunner | None,
    session_id: str,
    task_id: str,
) -> _LocalCommandRun:
    if prompt_transport != PromptTransport.STDIN:
        raise ValueError(
            "unsupported prompt transport: {}".format(prompt_transport.value)
        )
    if runner is not None:
        completed = _call_runner(runner, tuple(command), prompt_text)
        return _completed_runner_with_runtime_logs(
            completed,
            root=root,
            session_id=session_id,
            task_id=task_id,
        )
    return _run_process_with_runtime_logs(
        command,
        root=root,
        timeout_sec=timeout_sec,
        prompt_text=prompt_text,
        session_id=session_id,
        task_id=task_id,
    )


def _completed_runner_with_runtime_logs(
    completed: subprocess.CompletedProcess[str],
    *,
    root: Path,
    session_id: str,
    task_id: str,
) -> _LocalCommandRun:
    stdout_text = _decode_output(completed.stdout)
    stderr_text = _decode_output(completed.stderr)
    logs = _write_completed_runtime_logs(
        root,
        session_id=session_id,
        task_id=task_id,
        stdout=stdout_text.encode("utf-8"),
        stderr=stderr_text.encode("utf-8"),
    )
    normalized = subprocess.CompletedProcess(
        args=completed.args,
        returncode=completed.returncode,
        stdout=stdout_text,
        stderr=stderr_text,
    )
    return _LocalCommandRun(completed=normalized, runtime_logs=logs)


def _run_process_with_runtime_logs(
    command: Sequence[str],
    *,
    root: Path,
    timeout_sec: int,
    prompt_text: str,
    session_id: str,
    task_id: str,
) -> _LocalCommandRun:
    stdout_path, stderr_path = _runtime_log_paths(root, session_id, task_id)
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    stdout_start = _file_size(stdout_path)
    stderr_start = _file_size(stderr_path)
    stdout_buffer = bytearray()
    stderr_buffer = bytearray()
    prompt_bytes = prompt_text.encode("utf-8")

    with stdout_path.open("ab", buffering=0) as stdout_log, stderr_path.open(
        "ab", buffering=0
    ) as stderr_log:
        process = subprocess.Popen(
            list(command),
            cwd=str(root),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout_thread = threading.Thread(
            target=_pump_stream,
            args=(process.stdout, stdout_log, stdout_buffer),
            daemon=True,
        )
        stderr_thread = threading.Thread(
            target=_pump_stream,
            args=(process.stderr, stderr_log, stderr_buffer),
            daemon=True,
        )
        stdin_thread = threading.Thread(
            target=_write_stdin,
            args=(process.stdin, prompt_bytes),
            daemon=True,
        )
        stdout_thread.start()
        stderr_thread.start()
        stdin_thread.start()
        try:
            returncode = process.wait(timeout=timeout_sec)
        except subprocess.TimeoutExpired as exc:
            process.kill()
            process.wait()
            stdin_thread.join(timeout=1)
            stdout_thread.join()
            stderr_thread.join()
            logs = _runtime_log_metadata(
                root,
                stdout_path=stdout_path,
                stdout_start=stdout_start,
                stdout_bytes=len(stdout_buffer),
                stderr_path=stderr_path,
                stderr_start=stderr_start,
                stderr_bytes=len(stderr_buffer),
            )
            raise _LocalCommandTimeout(
                cmd=list(command),
                timeout=timeout_sec,
                output=bytes(stdout_buffer),
                stderr=bytes(stderr_buffer),
                runtime_logs=logs,
            ) from exc

        stdin_thread.join(timeout=1)
        stdout_thread.join()
        stderr_thread.join()

    logs = _runtime_log_metadata(
        root,
        stdout_path=stdout_path,
        stdout_start=stdout_start,
        stdout_bytes=len(stdout_buffer),
        stderr_path=stderr_path,
        stderr_start=stderr_start,
        stderr_bytes=len(stderr_buffer),
    )
    completed = subprocess.CompletedProcess(
        args=list(command),
        returncode=returncode,
        stdout=bytes(stdout_buffer).decode("utf-8", errors="replace"),
        stderr=bytes(stderr_buffer).decode("utf-8", errors="replace"),
    )
    return _LocalCommandRun(completed=completed, runtime_logs=logs)


def _pump_stream(stream: Any, log_file: Any, captured: bytearray) -> None:
    if stream is None:
        return
    try:
        while True:
            chunk = stream.read(8192)
            if not chunk:
                return
            captured.extend(chunk)
            log_file.write(chunk)
    finally:
        try:
            stream.close()
        except OSError:
            return


def _write_stdin(stdin: Any, payload: bytes) -> None:
    if stdin is None:
        return
    try:
        stdin.write(payload)
        stdin.close()
    except (BrokenPipeError, OSError):
        return


def _write_completed_runtime_logs(
    root: Path,
    *,
    session_id: str,
    task_id: str,
    stdout: bytes,
    stderr: bytes,
) -> Mapping[str, Any]:
    stdout_path, stderr_path = _runtime_log_paths(root, session_id, task_id)
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    stdout_start = _file_size(stdout_path)
    stderr_start = _file_size(stderr_path)
    with stdout_path.open("ab") as handle:
        if stdout:
            handle.write(stdout)
    with stderr_path.open("ab") as handle:
        if stderr:
            handle.write(stderr)
    return _runtime_log_metadata(
        root,
        stdout_path=stdout_path,
        stdout_start=stdout_start,
        stdout_bytes=len(stdout),
        stderr_path=stderr_path,
        stderr_start=stderr_start,
        stderr_bytes=len(stderr),
    )


def _call_runner(
    runner: OutputRunner,
    command: tuple[str, ...],
    prompt_text: str,
) -> subprocess.CompletedProcess[str]:
    if _runner_accepts_prompt(runner):
        return runner(command, prompt_text)
    return runner(command)


def _runner_accepts_prompt(runner: OutputRunner) -> bool:
    try:
        signature = inspect.signature(runner)
    except (TypeError, ValueError):
        return True
    positional_capacity = 0
    for parameter in signature.parameters.values():
        if parameter.kind == inspect.Parameter.VAR_POSITIONAL:
            return True
        if parameter.kind in {
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        }:
            positional_capacity += 1
    return positional_capacity >= 2


def _latest_report_id(root: Path, task_id: str) -> str:
    path = task_reports_state_path(root)
    if not path.exists():
        return ""
    data = read_json_file(path)
    if not isinstance(data, Mapping):
        return ""
    latest = data.get("latest_by_task")
    if isinstance(latest, Mapping):
        report_id = latest.get(task_id)
        if isinstance(report_id, str) and report_id.strip():
            return report_id
    reports = data.get("reports")
    if not isinstance(reports, list):
        return ""
    matches = [
        report
        for report in reports
        if isinstance(report, Mapping) and report.get("task_id") == task_id
    ]
    if not matches:
        return ""
    matches.sort(key=lambda item: str(item.get("submitted_at") or ""))
    return str(matches[-1].get("id") or "")


def _submit_built_summary_report(
    root: Path,
    *,
    task_id: str,
    summary: Mapping[str, Any],
    token_gate: TokenBudgetGateResult,
    command: Sequence[str],
    started_monotonic: float,
    returncode: int | None,
    stdout: str,
    stderr: str,
    runtime_logs: Mapping[str, Any],
    session_id: str,
) -> tuple[task_report_service.TaskReportSubmission, dict[str, Any]]:
    tasks_state = _load_tasks_state(root)
    task = _resolve_task(tasks_state, task_id)
    policy_evidence = _report_builder_policy_evidence(
        token_gate=token_gate,
        command=command,
        started_monotonic=started_monotonic,
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
        runtime_logs=runtime_logs,
    )
    adapter_evidence = policy_evidence["codex_adapter_gate"]
    report_payload = build_task_report_payload(
        session={"id": session_id},
        task=task,
        adapter_result=adapter_evidence,
        summary=summary,
        policy_evidence=policy_evidence,
    )
    submission = task_report_service.submit_task_report(
        root=root,
        tasks_state=tasks_state,
        task=task,
        report_payload=report_payload,
        source_file=_stdout_report_source(stdout),
        actor="codex",
        command="codex_adapter.report.auto_submit",
    )
    builder_evidence = _report_builder_evidence(
        task=task,
        report_payload=report_payload,
        policy_evidence=policy_evidence,
        stdout=stdout,
    )
    builder_evidence["built_report_id"] = submission.report_id
    return submission, builder_evidence


def _report_builder_policy_evidence(
    *,
    token_gate: TokenBudgetGateResult,
    command: Sequence[str],
    started_monotonic: float,
    returncode: int | None,
    stdout: str,
    stderr: str,
    runtime_logs: Mapping[str, Any],
) -> dict[str, Any]:
    stdout_bytes, stdout_ref = _output_ref("stdout", stdout)
    stderr_bytes, stderr_ref = _output_ref("stderr", stderr)
    adapter_evidence = {
        "status": "passed",
        "code": CODE_LOCAL_COMMAND_PASSED,
        "reason": "local_command_completed",
        "command": list(command),
        "command_ref": shlex.join(tuple(str(part) for part in command)),
        "returncode": returncode,
        "duration_sec": round(max(0.0, time.monotonic() - started_monotonic), 6),
        "stdout_ref": stdout_ref,
        "stderr_ref": stderr_ref,
        "stdout_bytes": stdout_bytes,
        "stderr_bytes": stderr_bytes,
        "runtime_logs": dict(runtime_logs),
    }
    return {
        "token_budget_gate": token_gate.to_dict(),
        "codex_adapter_gate": adapter_evidence,
    }


def _report_builder_evidence(
    *,
    task: Mapping[str, Any],
    report_payload: Mapping[str, Any],
    policy_evidence: Mapping[str, Any],
    stdout: str,
) -> dict[str, Any]:
    checks = [
        check
        for check in report_payload.get("checks", [])
        if isinstance(check, Mapping)
    ]
    return {
        "builder": "build_task_report_payload",
        "source_file": _stdout_report_source(stdout),
        "task_id": str(task.get("id") or ""),
        "task_ref": str(task.get("ref") or ""),
        "policy_evidence_keys": sorted(str(key) for key in policy_evidence.keys()),
        "check_names": [str(check.get("name") or "") for check in checks],
        "check_results": [str(check.get("result") or "") for check in checks],
        "changed_files_count": len(report_payload.get("changed_files") or []),
        "generated_files_count": len(report_payload.get("generated_files") or []),
        "warning_count": len(report_payload.get("warnings") or []),
        "blocker_count": len(report_payload.get("blockers") or []),
    }


def _load_tasks_state(root: Path) -> Mapping[str, Any]:
    path = tasks_state_path(root)
    try:
        data = read_json_file(path, missing_code="TASKS_NOT_INITIALIZED")
    except StoreError as exc:
        raise task_report_service.TaskReportError(str(exc)) from exc
    if not isinstance(data, Mapping):
        raise task_report_service.TaskReportError(
            "TASKS_STATE_INVALID: {} must contain a JSON object".format(path)
        )
    return data


def _resolve_task(tasks_state: Mapping[str, Any], task_id: str) -> Mapping[str, Any]:
    matches = [
        task
        for task in tasks_state.get("tasks", [])
        if isinstance(task, Mapping) and task_id in _task_reference_values(task)
    ]
    if not matches:
        raise task_report_service.TaskReportError(
            "TASK_REF_NOT_FOUND: {}".format(task_id)
        )
    if len(matches) > 1:
        ids = ", ".join(str(task.get("id") or "") for task in matches)
        raise task_report_service.TaskReportError(
            "AMBIGUOUS_TASK_REF: {} ({})".format(task_id, ids)
        )
    return matches[0]


def _task_reference_values(task: Mapping[str, Any]) -> set[str]:
    values = {
        str(task.get("id") or ""),
        str(task.get("ref") or ""),
        str(task.get("uid") or ""),
        str(task.get("legacy_id") or ""),
    }
    aliases = task.get("aliases")
    if isinstance(aliases, Sequence) and not isinstance(aliases, (str, bytes)):
        values.update(str(alias) for alias in aliases if str(alias).strip())
    values.discard("")
    return values


def _stdout_report_source(stdout: str) -> str:
    digest = hashlib.sha256(stdout.encode("utf-8")).hexdigest()
    return "captured:stdout:sha256:{}".format(digest)


def _report_instruction(task_id: str) -> str:
    return (
        "In local-command mode, Codex receives "
        "AI_PROJECT/generated/CODEX_PROMPT.md on stdin. "
        "Submit a structured execution report before downstream gates can pass: "
        "python scripts/aictl.py task report submit --task {} --file <REPORT.json> --confirm"
    ).format(task_id)


def _output_ref(stream_name: str, text: str) -> tuple[int, str]:
    encoded = text.encode("utf-8")
    if not encoded:
        return 0, ""
    digest = hashlib.sha256(encoded).hexdigest()
    return len(encoded), "captured:{}:sha256:{}".format(stream_name, digest)


def _runtime_log_paths(root: Path, session_id: str, task_id: str) -> tuple[Path, Path]:
    session_segment = _safe_log_segment(session_id) if session_id else "no-session"
    task_segment = _safe_log_segment(task_id) if task_id else "unknown-task"
    directory = root / "AI_PROJECT" / "logs" / "codex" / session_segment
    return (
        directory / "{}-stdout.log".format(task_segment),
        directory / "{}-stderr.log".format(task_segment),
    )


def _runtime_log_metadata(
    root: Path,
    *,
    stdout_path: Path,
    stdout_start: int,
    stdout_bytes: int,
    stderr_path: Path,
    stderr_start: int,
    stderr_bytes: int,
) -> dict[str, Any]:
    return {
        "stdout": _runtime_log_stream_metadata(
            root,
            path=stdout_path,
            start_offset=stdout_start,
            byte_count=stdout_bytes,
        ),
        "stderr": _runtime_log_stream_metadata(
            root,
            path=stderr_path,
            start_offset=stderr_start,
            byte_count=stderr_bytes,
        ),
    }


def _runtime_log_stream_metadata(
    root: Path,
    *,
    path: Path,
    start_offset: int,
    byte_count: int,
) -> dict[str, Any]:
    end_offset = start_offset + byte_count
    return {
        "path": _repo_path(root, path),
        "start_offset": start_offset,
        "end_offset": end_offset,
        "bytes": byte_count,
    }


def _file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except FileNotFoundError:
        return 0


def _safe_log_segment(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    cleaned = cleaned.strip(".-")
    return cleaned or "unknown"


def _repo_path(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _output_snippet(text: str, prompt_text: str) -> str:
    if not text:
        return ""
    redacted = _redact_prompt_echo(text, prompt_text)
    encoded = redacted.encode("utf-8")
    if len(encoded) <= OUTPUT_SNIPPET_BYTES:
        return redacted
    snippet = encoded[:OUTPUT_SNIPPET_BYTES].decode("utf-8", errors="replace")
    return "{}\n[truncated: {} bytes total]".format(snippet, len(encoded))


def _redact_prompt_echo(text: str, prompt_text: str) -> str:
    if not prompt_text:
        return text
    redacted = text
    if prompt_text in redacted:
        redacted = redacted.replace(prompt_text, "[redacted: prompt input]")
    for line in prompt_text.splitlines():
        cleaned = line.strip()
        if len(cleaned) >= 80:
            redacted = redacted.replace(cleaned, "[redacted: prompt line]")
    return redacted


def _is_sandbox_unavailable(stdout: str, stderr: str) -> bool:
    return is_sandbox_unavailable_output(stdout, stderr)


def is_sandbox_unavailable_output(stdout: str, stderr: str) -> bool:
    """Return true when captured Codex output indicates sandbox incompatibility."""

    return bool(SANDBOX_UNAVAILABLE_RE.search("\n".join((stdout, stderr))))


def _decode_output(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _default_prompt(root: Path) -> Path:
    return root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

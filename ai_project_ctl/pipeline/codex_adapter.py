"""Controlled Codex execution adapter for supervised pipeline sessions."""

from __future__ import annotations

import hashlib
import inspect
import re
import shlex
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ai_project_ctl.core.store import read_json_file

from .policy import CodexAdapterMode, CodexExecutionMode, PipelinePolicy, PromptTransport
from .state import task_reports_state_path
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
    report_required: bool = True
    before_report_id: str = ""
    after_report_id: str = ""
    report_id: str = ""
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
            "report_required": self.report_required,
            "before_report_id": self.before_report_id,
            "after_report_id": self.after_report_id,
            "report_id": self.report_id,
            "report_instruction": self.report_instruction,
        }


def run_codex_adapter(
    *,
    root: str | Path = ".",
    task_id: str,
    policy: PipelinePolicy,
    token_gate: TokenBudgetGateResult,
    runner: OutputRunner | None = None,
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
        before_report_id: str = "",
        after_report_id: str = "",
        report_id: str = "",
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
            report_required=policy.codex.require_report,
            before_report_id=before_report_id,
            after_report_id=after_report_id,
            report_id=report_id,
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
        completed = _run_local_command(
            command,
            root=root_path,
            timeout_sec=policy.codex.timeout_sec,
            prompt_text=prompt_text,
            prompt_transport=policy.codex.prompt_transport,
            runner=runner,
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
            before_report_id=before_report,
            after_report_id=after_report,
            report_instruction=instruction,
        )

    stdout = _decode_output(completed.stdout)
    stderr = _decode_output(completed.stderr)
    after_report = _latest_report_id(root_path, task_id)
    if completed.returncode != 0:
        if _is_sandbox_unavailable(stdout, stderr):
            return finish(
                status="blocked",
                code=CODE_SANDBOX_UNAVAILABLE,
                reason="codex_sandbox_unavailable",
                command=command,
                returncode=completed.returncode,
                stdout=stdout,
                stderr=stderr,
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
            before_report_id=before_report,
            after_report_id=after_report,
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
        before_report_id=before_report,
        after_report_id=after_report,
        report_id=report_id,
        report_instruction=instruction,
    )


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
) -> subprocess.CompletedProcess[str]:
    if prompt_transport != PromptTransport.STDIN:
        raise ValueError(
            "unsupported prompt transport: {}".format(prompt_transport.value)
        )
    if runner is not None:
        return _call_runner(runner, tuple(command), prompt_text)
    return subprocess.run(
        list(command),
        cwd=str(root),
        text=True,
        input=prompt_text,
        capture_output=True,
        timeout=timeout_sec,
        check=False,
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

"""Deterministic Machine Review gate for supervised pipeline runs."""

from __future__ import annotations

import fnmatch
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .policy import PipelinePolicy
from .report_gate import FAIL as REPORT_GATE_FAIL
from .report_gate import WARN as REPORT_GATE_WARN
from .report_gate import ReportGateResult, evaluate_report_gate


PASS = "pass"
WARN = "warn"
FAIL = "fail"

CODE_PASS = "MACHINE_REVIEW_PASS"
CODE_WARN = "MACHINE_REVIEW_WARN"
CODE_REPORT_GATE_FAILED = "MACHINE_REVIEW_REPORT_GATE_FAILED"
CODE_COMMAND_FAILED = "MACHINE_REVIEW_COMMAND_FAILED"
CODE_COMMAND_ERROR = "MACHINE_REVIEW_COMMAND_ERROR"
CODE_UNSAFE_TEST_COMMAND = "MACHINE_REVIEW_UNSAFE_TEST_COMMAND"
CODE_OUT_OF_SCOPE_FILE = "MACHINE_REVIEW_OUT_OF_SCOPE_FILE"
CODE_PROTECTED_FILE_REPORTED = "MACHINE_REVIEW_PROTECTED_FILE_REPORTED"
CODE_TOKEN_USAGE_REQUIRED = "MACHINE_REVIEW_TOKEN_USAGE_REQUIRED"

SUMMARY_LIMIT = 1200
DEFAULT_COMMAND_TIMEOUT_SEC = 300

CommandRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class MachineCheckEvidence:
    name: str
    status: str
    code: str
    reason: str
    blocking: bool = True
    command: tuple[str, ...] = ()
    returncode: int | None = None
    duration_sec: float | None = None
    stdout_summary: str = ""
    stderr_summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "name": self.name,
            "status": self.status,
            "code": self.code,
            "reason": self.reason,
            "blocking": self.blocking,
        }
        if self.command:
            data["command"] = list(self.command)
        if self.returncode is not None:
            data["returncode"] = self.returncode
        if self.duration_sec is not None:
            data["duration_sec"] = self.duration_sec
        if self.stdout_summary:
            data["stdout_summary"] = self.stdout_summary
        if self.stderr_summary:
            data["stderr_summary"] = self.stderr_summary
        return data


@dataclass(frozen=True)
class MachineReviewResult:
    status: str
    code: str
    reason: str
    task_id: str
    report_id: str
    checks: tuple[MachineCheckEvidence, ...]

    @property
    def ok(self) -> bool:
        return self.status in {PASS, WARN}

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "code": self.code,
            "reason": self.reason,
            "task_id": self.task_id,
            "report_id": self.report_id,
            "checks": [check.to_dict() for check in self.checks],
        }


def evaluate_machine_review(
    *,
    root: str | Path,
    task: Mapping[str, Any],
    policy: PipelinePolicy,
    report_gate: ReportGateResult | None = None,
    runner: CommandRunner | None = None,
    python_executable: str | None = None,
    test_commands: Sequence[Sequence[str] | str] = (),
    run_report_declared_tests: bool = True,
    command_timeout_sec: int = DEFAULT_COMMAND_TIMEOUT_SEC,
) -> MachineReviewResult:
    """Run deterministic machine checks before semantic review or auto-close."""

    root_path = Path(root).resolve()
    python_bin = python_executable or sys.executable
    task_id = str(task.get("id") or "")
    selected_report_gate = report_gate or evaluate_report_gate(
        root=root_path,
        task=task,
        policy=policy,
    )

    checks: list[MachineCheckEvidence] = [_report_gate_evidence(selected_report_gate)]
    if selected_report_gate.status == REPORT_GATE_FAIL:
        return _finish(task_id=task_id, report_gate=selected_report_gate, checks=checks)

    checks.append(_protected_files_evidence(selected_report_gate))
    checks.append(_allowed_files_evidence(task, selected_report_gate))
    checks.append(_token_usage_evidence(policy, selected_report_gate))

    for name, argv in _project_control_commands(root_path, python_bin):
        checks.append(
            _run_command(
                name,
                argv,
                root=root_path,
                runner=runner,
                timeout_sec=command_timeout_sec,
            )
        )

    for name, argv in _test_commands(
        selected_report_gate,
        configured=test_commands,
        run_report_declared=run_report_declared_tests,
    ):
        if not _is_safe_test_command(argv, python_bin):
            checks.append(
                MachineCheckEvidence(
                    name=name,
                    status=WARN,
                    code=CODE_UNSAFE_TEST_COMMAND,
                    reason="test_command_skipped_as_unsafe",
                    blocking=False,
                    command=tuple(argv),
                )
            )
            continue
        checks.append(
            _run_command(
                name,
                argv,
                root=root_path,
                runner=runner,
                timeout_sec=command_timeout_sec,
            )
        )

    return _finish(task_id=task_id, report_gate=selected_report_gate, checks=checks)


def _project_control_commands(root: Path, python_bin: str) -> tuple[tuple[str, tuple[str, ...]], ...]:
    scripts = root / "scripts"
    return (
        ("task_validate", (python_bin, str(scripts / "taskctl.py"), "validate")),
        (
            "task_graph_validate",
            (python_bin, str(scripts / "taskctl.py"), "task", "graph", "validate"),
        ),
        (
            "task_check_generated",
            (python_bin, str(scripts / "taskctl.py"), "check-generated"),
        ),
        ("evolution_validate", (python_bin, str(scripts / "evolutionctl.py"), "validate")),
        (
            "evolution_check_generated",
            (python_bin, str(scripts / "evolutionctl.py"), "check-generated"),
        ),
        ("context_validate", (python_bin, str(scripts / "contextctl.py"), "validate")),
        (
            "context_check_generated",
            (python_bin, str(scripts / "contextctl.py"), "check-generated"),
        ),
        (
            "project_doctor",
            (python_bin, str(scripts / "aictl.py"), "project", "doctor"),
        ),
        (
            "protected_file_check",
            (python_bin, str(scripts / "aictl.py"), "project", "protected-check"),
        ),
    )


def _run_command(
    name: str,
    argv: Sequence[str],
    *,
    root: Path,
    runner: CommandRunner | None,
    timeout_sec: int,
) -> MachineCheckEvidence:
    command = tuple(str(part) for part in argv)
    started = time.monotonic()
    try:
        if runner is not None:
            completed = runner(command)
        else:
            completed = subprocess.run(
                list(command),
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_sec,
                check=False,
            )
    except subprocess.TimeoutExpired as exc:
        return MachineCheckEvidence(
            name=name,
            status=FAIL,
            code=CODE_COMMAND_FAILED,
            reason="command_timed_out",
            command=command,
            duration_sec=_elapsed(started),
            stdout_summary=_summary(exc.stdout),
            stderr_summary=_summary(exc.stderr),
        )
    except OSError as exc:
        return MachineCheckEvidence(
            name=name,
            status=FAIL,
            code=CODE_COMMAND_ERROR,
            reason=str(exc),
            command=command,
            duration_sec=_elapsed(started),
        )

    returncode = int(completed.returncode)
    status = PASS if returncode == 0 else FAIL
    return MachineCheckEvidence(
        name=name,
        status=status,
        code=CODE_PASS if status == PASS else CODE_COMMAND_FAILED,
        reason="command_succeeded" if status == PASS else "command_failed",
        command=command,
        returncode=returncode,
        duration_sec=_elapsed(started),
        stdout_summary=_summary(completed.stdout),
        stderr_summary=_summary(completed.stderr),
    )


def _report_gate_evidence(report_gate: ReportGateResult) -> MachineCheckEvidence:
    if report_gate.status == REPORT_GATE_FAIL:
        status = FAIL
        code = CODE_REPORT_GATE_FAILED
    elif report_gate.status == REPORT_GATE_WARN:
        status = WARN
        code = CODE_WARN
    else:
        status = PASS
        code = CODE_PASS
    return MachineCheckEvidence(
        name="codex_report_gate",
        status=status,
        code=code,
        reason=report_gate.reason,
        blocking=True,
    )


def _allowed_files_evidence(
    task: Mapping[str, Any],
    report_gate: ReportGateResult,
) -> MachineCheckEvidence:
    allowed_patterns = _allowed_file_patterns(task.get("allowed_files"))
    generated_set = {_normalize_path(path) for path in report_gate.generated_files}
    violations: list[str] = []
    for path in report_gate.changed_files:
        normalized = _normalize_path(path)
        if _matches_allowed_file(normalized, allowed_patterns):
            continue
        if normalized in generated_set and _is_generated_path(normalized):
            continue
        violations.append(path)

    if violations:
        return MachineCheckEvidence(
            name="allowed_files_scope",
            status=FAIL,
            code=CODE_OUT_OF_SCOPE_FILE,
            reason="changed files outside task allowed_files: {}".format(
                ", ".join(violations)
            ),
            blocking=True,
        )
    return MachineCheckEvidence(
        name="allowed_files_scope",
        status=PASS,
        code=CODE_PASS,
        reason="changed files are within task allowed_files or governed generated output",
        blocking=True,
    )


def _protected_files_evidence(report_gate: ReportGateResult) -> MachineCheckEvidence:
    generated_set = {_normalize_path(path) for path in report_gate.generated_files}
    violations: list[str] = []
    for path in report_gate.changed_files:
        normalized = _normalize_path(path)
        if _is_state_or_event_path(normalized):
            violations.append(path)
        elif _is_generated_path(normalized) and normalized not in generated_set:
            violations.append(path)

    if violations:
        return MachineCheckEvidence(
            name="reported_protected_files",
            status=FAIL,
            code=CODE_PROTECTED_FILE_REPORTED,
            reason="report lists protected file changes without governed generated output: {}".format(
                ", ".join(violations)
            ),
            blocking=True,
        )
    return MachineCheckEvidence(
        name="reported_protected_files",
        status=PASS,
        code=CODE_PASS,
        reason="report does not list protected state/event edits",
        blocking=True,
    )


def _token_usage_evidence(
    policy: PipelinePolicy,
    report_gate: ReportGateResult,
) -> MachineCheckEvidence:
    token_usage = dict(report_gate.token_usage or {})
    if policy.token_budget.require_gate_pass:
        if not token_usage:
            return MachineCheckEvidence(
                name="report_token_usage",
                status=FAIL,
                code=CODE_TOKEN_USAGE_REQUIRED,
                reason="token usage evidence is required by policy",
                blocking=True,
            )
        if token_usage.get("token_count_unavailable") is True:
            return MachineCheckEvidence(
                name="report_token_usage",
                status=FAIL,
                code=CODE_TOKEN_USAGE_REQUIRED,
                reason="token usage is unavailable while policy requires token evidence",
                blocking=True,
            )
    return MachineCheckEvidence(
        name="report_token_usage",
        status=PASS,
        code=CODE_PASS,
        reason="token usage evidence satisfies policy",
        blocking=True,
    )


def _test_commands(
    report_gate: ReportGateResult,
    *,
    configured: Sequence[Sequence[str] | str],
    run_report_declared: bool,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    commands: list[tuple[str, tuple[str, ...]]] = []
    seen: set[tuple[str, ...]] = set()

    for index, command in enumerate(configured, start=1):
        argv = _coerce_command(command)
        if argv and argv not in seen:
            commands.append(("configured_test_{}".format(index), argv))
            seen.add(argv)

    if run_report_declared:
        for index, check in enumerate(getattr(report_gate, "checks", ()), start=1):
            command = check.get("command") if isinstance(check, Mapping) else None
            argv = _coerce_command(command)
            if argv and argv not in seen:
                commands.append(("report_declared_test_{}".format(index), argv))
                seen.add(argv)

    return tuple(commands)


def _coerce_command(command: Sequence[str] | str | Any) -> tuple[str, ...]:
    if isinstance(command, str):
        try:
            return tuple(shlex.split(command))
        except ValueError:
            return ()
    if isinstance(command, Sequence) and not isinstance(command, (bytes, bytearray)):
        return tuple(str(part) for part in command if str(part).strip())
    return ()


def _is_safe_test_command(argv: Sequence[str], python_bin: str) -> bool:
    if not argv:
        return False
    executable = Path(str(argv[0])).name
    configured_python = Path(str(python_bin)).name
    python_names = {"python", "python3", configured_python}

    if executable in python_names:
        if len(argv) >= 3 and argv[1] == "-m" and argv[2] in {"unittest", "pytest"}:
            return True
        if len(argv) >= 2 and _is_safe_script_command(str(argv[1]), argv[2:]):
            return True
    if executable in {"pytest"}:
        return True
    return False


def _is_safe_script_command(script: str, tail: Sequence[str]) -> bool:
    script_name = Path(script).name
    tail_tuple = tuple(str(part) for part in tail)
    if script_name in {"taskctl.py", "evolutionctl.py", "contextctl.py"}:
        return tail_tuple in {
            ("validate",),
            ("check-generated",),
            ("task", "graph", "validate"),
        }
    if script_name == "aictl.py":
        return tail_tuple in {
            ("project", "doctor"),
            ("project", "protected-check"),
        }
    return False


def _finish(
    *,
    task_id: str,
    report_gate: ReportGateResult,
    checks: Sequence[MachineCheckEvidence],
) -> MachineReviewResult:
    blocking_failures = [
        check for check in checks if check.blocking and check.status == FAIL
    ]
    warnings = [check for check in checks if check.status == WARN]
    if blocking_failures:
        first = blocking_failures[0]
        return MachineReviewResult(
            status=FAIL,
            code=first.code,
            reason=first.reason,
            task_id=task_id,
            report_id=report_gate.report_id,
            checks=tuple(checks),
        )
    if warnings:
        first = warnings[0]
        return MachineReviewResult(
            status=WARN,
            code=CODE_WARN,
            reason=first.reason,
            task_id=task_id,
            report_id=report_gate.report_id,
            checks=tuple(checks),
        )
    return MachineReviewResult(
        status=PASS,
        code=CODE_PASS,
        reason="All blocking machine checks passed.",
        task_id=task_id,
        report_id=report_gate.report_id,
        checks=tuple(checks),
    )


def _allowed_file_patterns(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    patterns: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        pattern = item.strip()
        if not pattern:
            continue
        if " if " in pattern:
            pattern = pattern.split(" if ", 1)[0].strip()
        patterns.append(_normalize_path(pattern))
    return tuple(patterns)


def _matches_allowed_file(path: str, patterns: Sequence[str]) -> bool:
    for pattern in patterns:
        if pattern.endswith("/**"):
            prefix = pattern[:-3].rstrip("/")
            if path == prefix or path.startswith(prefix + "/"):
                return True
        if fnmatch.fnmatchcase(path, pattern):
            return True
    return False


def _normalize_path(path: str) -> str:
    text = str(path).strip().replace("\\", "/")
    marker = "/AI_PROJECT/"
    if marker in text:
        return "AI_PROJECT/" + text.split(marker, 1)[1]
    if text.startswith("./"):
        text = text[2:]
    return text.lstrip("/")


def _is_state_or_event_path(path: str) -> bool:
    return path.startswith("AI_PROJECT/state/") or path.startswith("AI_PROJECT/events/")


def _is_generated_path(path: str) -> bool:
    return path.startswith("AI_PROJECT/generated/")


def _summary(value: Any) -> str:
    if value is None:
        return ""
    text = value.decode("utf-8", errors="replace") if isinstance(value, bytes) else str(value)
    text = text.strip()
    if len(text) <= SUMMARY_LIMIT:
        return text
    return text[: SUMMARY_LIMIT - 3].rstrip() + "..."


def _elapsed(started: float) -> float:
    return round(time.monotonic() - started, 3)

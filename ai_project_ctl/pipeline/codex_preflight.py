"""Codex local command preflight for UI-triggered executable runs."""

from __future__ import annotations

import hashlib
import inspect
import shlex
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

from ai_project_ctl.core.result import CommandError, CommandMessage, CommandResult
from ai_project_ctl.ui_settings import (
    load_ui_settings,
    ui_command_line_argv,
    ui_settings_path,
    ui_settings_source,
)

from .codex_adapter import is_sandbox_unavailable_output


CODE_PREFLIGHT_PASSED = "CODEX_PREFLIGHT_PASSED"
CODE_PREFLIGHT_SANDBOX_UNAVAILABLE = "CODEX_PREFLIGHT_SANDBOX_UNAVAILABLE"
CODE_PREFLIGHT_COMMAND_FAILED = "CODEX_PREFLIGHT_COMMAND_FAILED"
CODE_PREFLIGHT_TIMEOUT = "CODEX_PREFLIGHT_TIMEOUT"
CODE_PREFLIGHT_EXEC_FAILED = "CODEX_PREFLIGHT_EXEC_FAILED"
DEFAULT_PREFLIGHT_TIMEOUT_SEC = 30
PREFLIGHT_PROMPT = (
    "Codex executable preflight only. Reply with OK. "
    "Do not inspect or modify repository files.\n"
)
OUTPUT_SNIPPET_BYTES = 1200

PreflightRunner = Callable[..., subprocess.CompletedProcess[str]]


def run_codex_preflight(
    *,
    root: str | Path = ".",
    timeout_sec: int = DEFAULT_PREFLIGHT_TIMEOUT_SEC,
    runner: PreflightRunner | None = None,
) -> CommandResult:
    """Run a minimal prompt through the effective UI command_line."""

    root_path = Path(root).resolve()
    started_monotonic = time.monotonic()
    started_at = _utc_now()
    try:
        settings = load_ui_settings(root=root_path)
        command = ui_command_line_argv(settings)
    except CommandError as exc:
        return _failure_result(
            "UI command_line is not executable.",
            code=exc.code,
            reason="settings_invalid",
            started_at=started_at,
            started_monotonic=started_monotonic,
            settings_source=ui_settings_source(root=root_path),
            settings_path=ui_settings_path(root_path),
            timeout_sec=timeout_sec,
            errors=[exc.to_message()],
        )

    try:
        completed = _run_command(
            command,
            root=root_path,
            timeout_sec=timeout_sec,
            runner=runner,
        )
    except subprocess.TimeoutExpired as exc:
        return _failure_result(
            "Codex preflight failed: configured command timed out.",
            code=CODE_PREFLIGHT_TIMEOUT,
            reason="command_timeout",
            started_at=started_at,
            started_monotonic=started_monotonic,
            settings_source=ui_settings_source(root=root_path),
            settings_path=ui_settings_path(root_path),
            command=command,
            timeout_sec=timeout_sec,
            timed_out=True,
            stdout=_decode_output(exc.stdout),
            stderr=_decode_output(exc.stderr),
            errors=[
                CommandMessage(
                    CODE_PREFLIGHT_TIMEOUT,
                    "Configured command timed out during Codex preflight.",
                )
            ],
        )
    except OSError as exc:
        return _failure_result(
            "Codex preflight failed: configured command could not be executed.",
            code=CODE_PREFLIGHT_EXEC_FAILED,
            reason="command_exec_failed",
            started_at=started_at,
            started_monotonic=started_monotonic,
            settings_source=ui_settings_source(root=root_path),
            settings_path=ui_settings_path(root_path),
            command=command,
            timeout_sec=timeout_sec,
            stderr=str(exc),
            errors=[
                CommandMessage(
                    CODE_PREFLIGHT_EXEC_FAILED,
                    "Configured command could not be executed: {}".format(exc),
                )
            ],
        )

    stdout = _decode_output(completed.stdout)
    stderr = _decode_output(completed.stderr)
    common = {
        "started_at": started_at,
        "started_monotonic": started_monotonic,
        "settings_source": ui_settings_source(root=root_path),
        "settings_path": ui_settings_path(root_path),
        "command": command,
        "timeout_sec": timeout_sec,
        "returncode": completed.returncode,
        "stdout": stdout,
        "stderr": stderr,
    }
    if completed.returncode == 0:
        return _success_result(
            "Codex preflight passed: configured command exited successfully.",
            code=CODE_PREFLIGHT_PASSED,
            status="passed",
            reason="command_completed",
            **common,
        )
    if is_sandbox_unavailable_output(stdout, stderr):
        result = _success_result(
            "Codex preflight blocked: local Codex sandbox is unavailable.",
            code=CODE_PREFLIGHT_SANDBOX_UNAVAILABLE,
            status="blocked",
            reason="sandbox_unavailable",
            **common,
        )
        result.owner_action_required = (
            "Fix local sandbox support or change the UI command_line before running executable Codex."
        )
        return result
    return _failure_result(
        "Codex preflight failed: configured command exited non-zero.",
        code=CODE_PREFLIGHT_COMMAND_FAILED,
        reason="command_nonzero_exit",
        errors=[
            CommandMessage(
                CODE_PREFLIGHT_COMMAND_FAILED,
                "Configured command exited with code {}.".format(completed.returncode),
            )
        ],
        **common,
    )


def _run_command(
    command: Sequence[str],
    *,
    root: Path,
    timeout_sec: int,
    runner: PreflightRunner | None,
) -> subprocess.CompletedProcess[str]:
    command_tuple = tuple(str(part) for part in command)
    if runner is not None:
        return _call_runner(runner, command_tuple, PREFLIGHT_PROMPT)
    return subprocess.run(
        list(command_tuple),
        cwd=str(root),
        text=True,
        input=PREFLIGHT_PROMPT,
        capture_output=True,
        timeout=timeout_sec,
        check=False,
    )


def _call_runner(
    runner: PreflightRunner,
    command: tuple[str, ...],
    prompt_text: str,
) -> subprocess.CompletedProcess[str]:
    if _runner_accepts_prompt(runner):
        return runner(command, prompt_text)
    return runner(command)


def _runner_accepts_prompt(runner: PreflightRunner) -> bool:
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


def _success_result(
    message: str,
    *,
    code: str,
    status: str,
    reason: str,
    started_at: str,
    started_monotonic: float,
    settings_source: str,
    settings_path: Path,
    command: Sequence[str],
    timeout_sec: int,
    returncode: int | None,
    stdout: str,
    stderr: str,
) -> CommandResult:
    return CommandResult.success(
        command="ui.preflight",
        domain="ui",
        message=message,
        data=_result_data(
            status=status,
            code=code,
            reason=reason,
            started_at=started_at,
            started_monotonic=started_monotonic,
            settings_source=settings_source,
            settings_path=settings_path,
            command=command,
            timeout_sec=timeout_sec,
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
        ),
    )


def _failure_result(
    message: str,
    *,
    code: str,
    reason: str,
    started_at: str,
    started_monotonic: float,
    settings_source: str,
    settings_path: Path,
    command: Sequence[str] = (),
    timeout_sec: int = DEFAULT_PREFLIGHT_TIMEOUT_SEC,
    timed_out: bool = False,
    returncode: int | None = None,
    stdout: str = "",
    stderr: str = "",
    errors: list[CommandMessage] | None = None,
) -> CommandResult:
    result = CommandResult.failure(
        command="ui.preflight",
        domain="ui",
        message=message,
        errors=errors,
    )
    result.data = _result_data(
        status="failed",
        code=code,
        reason=reason,
        started_at=started_at,
        started_monotonic=started_monotonic,
        settings_source=settings_source,
        settings_path=settings_path,
        command=command,
        timeout_sec=timeout_sec,
        timed_out=timed_out,
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )
    return result


def _result_data(
    *,
    status: str,
    code: str,
    reason: str,
    started_at: str,
    started_monotonic: float,
    settings_source: str,
    settings_path: Path,
    command: Sequence[str],
    timeout_sec: int,
    timed_out: bool = False,
    returncode: int | None = None,
    stdout: str = "",
    stderr: str = "",
) -> dict[str, Any]:
    finished_at = _utc_now()
    duration = max(0.0, time.monotonic() - started_monotonic)
    command_tuple = tuple(str(part) for part in command)
    stdout_bytes, stdout_ref = _output_ref("stdout", stdout)
    stderr_bytes, stderr_ref = _output_ref("stderr", stderr)
    return {
        "status": status,
        "phase_status": status,
        "code": code,
        "reason": reason,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_sec": round(duration, 6),
        "settings_source": settings_source,
        "settings_path": str(settings_path),
        "command": list(command_tuple),
        "command_ref": shlex.join(command_tuple) if command_tuple else "",
        "timeout_sec": timeout_sec,
        "timed_out": timed_out,
        "returncode": returncode,
        "stdout_ref": stdout_ref,
        "stderr_ref": stderr_ref,
        "stdout_snippet": _output_snippet(stdout),
        "stderr_snippet": _output_snippet(stderr),
        "stdout_bytes": stdout_bytes,
        "stderr_bytes": stderr_bytes,
    }


def _output_ref(stream_name: str, text: str) -> tuple[int, str]:
    encoded = text.encode("utf-8")
    if not encoded:
        return 0, ""
    digest = hashlib.sha256(encoded).hexdigest()
    return len(encoded), "captured:{}:sha256:{}".format(stream_name, digest)


def _output_snippet(text: str) -> str:
    if not text:
        return ""
    encoded = text.encode("utf-8")
    if len(encoded) <= OUTPUT_SNIPPET_BYTES:
        return text
    snippet = encoded[:OUTPUT_SNIPPET_BYTES].decode("utf-8", errors="replace")
    return "{}\n[truncated: {} bytes total]".format(snippet, len(encoded))


def _decode_output(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

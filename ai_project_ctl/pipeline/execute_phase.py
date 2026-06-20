"""Pipeline execute phase service.

The execute phase consumes prepare-phase artifact evidence from a pipeline
session and delegates only to the Codex execution adapter. It does not run
report collection, verification, review, close, or commit gates.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Callable, Mapping

from ai_project_ctl.core.result import CommandMessage, CommandResult

from .codex_adapter import (
    CODE_MANUAL_HANDOFF,
    CODE_REPORT_MISSING,
    CodexAdapterResult,
    OutputRunner,
    run_codex_adapter,
)
from .phase import PhaseResult
from .policy import CodexExecutionMode, PipelinePolicy
from .session import record_phase_result
from .state import load_pipeline_state, pipeline_state_path
from .token_budget import PASS as TOKEN_BUDGET_PASS
from .token_budget import TokenBudgetGateResult, evaluate_token_budget


COMMAND_NAME = "pipeline.phase.execute"
PHASE_NAME = "execute"
PREPARE_PHASE_NAME = "prepare"

CodexAdapter = Callable[..., CodexAdapterResult]


def execute_phase(
    session_id: str = "",
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    codex_adapter: CodexAdapter | None = None,
    execution_runner: OutputRunner | None = None,
) -> CommandResult:
    """Run the prepared Codex adapter without downstream pipeline gates."""

    root_path = Path(root).resolve()
    session_result = _resolve_session(root_path, session_id)
    if not session_result.ok:
        return session_result

    session = session_result.data["session"]
    selected_session_id = str(session.get("id") or "")
    prepare_result = _latest_prepare_result(session)
    if prepare_result is None:
        return _blocked(
            "PREPARE_PHASE_REQUIRED",
            "Prepare phase evidence is missing for this session.",
            session_id=selected_session_id,
            root=root_path,
            actor=actor,
            next_action="Run pipeline phase prepare before execute.",
        )

    prepare_artifacts = _mapping(
        prepare_result.get("artifacts"),
        default={},
    )
    artifact_check = _prepared_artifact_check(
        root_path,
        session,
        prepare_result,
        prepare_artifacts,
        actor=actor,
    )
    if artifact_check is not None:
        return artifact_check

    task_id = str(prepare_artifacts["task_id"])

    try:
        policy = PipelinePolicy.from_dict(
            _required_mapping(session.get("policy_snapshot"), "policy_snapshot")
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _failure(
            "PIPELINE_EXECUTE_POLICY_INVALID",
            "Session policy snapshot is invalid: {}".format(exc),
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
        )

    validation = policy.validate()
    if not validation.ok:
        return _blocked(
            "PIPELINE_EXECUTE_POLICY_INVALID",
            "Session policy does not pass validation.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                "policy": policy.name,
                "policy_errors": [
                    issue.to_message().to_dict() for issue in validation.errors
                ],
                "codex_adapter_called": False,
            },
            next_action="Fix or recreate the session with a valid pipeline policy.",
        )

    prompt_path = _artifact_path(root_path, prepare_artifacts["prompt_path"])
    prepared_sha256 = str(prepare_artifacts["prompt_sha256"])

    if policy.codex.mode != CodexExecutionMode.RUN_CODEX:
        return _blocked(
            "CODEX_EXECUTION_POLICY_DENIED",
            "Session policy does not allow Codex execution.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                "policy": policy.name,
                "codex_mode": policy.codex.mode.value,
                "prepare_artifacts": _bounded_prepare_artifacts(prepare_artifacts),
                "codex_adapter_called": False,
            },
            next_action=(
                "Select an executable policy or use the prepared prompt for manual "
                "execution outside this phase."
            ),
        )

    token_gate = evaluate_token_budget(
        root=root_path,
        policy=policy.token_budget,
        prompt_path=prompt_path,
        strict=True,
    )
    token_artifacts = {
        "policy": policy.name,
        "prepare_artifacts": _bounded_prepare_artifacts(prepare_artifacts),
        "token_budget": token_gate.to_dict(),
        "codex_adapter_called": False,
    }
    if token_gate.status != TOKEN_BUDGET_PASS:
        return _blocked(
            "TOKEN_BUDGET_FAILURE",
            "Token Budget Gate failed: {}".format(token_gate.reason),
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts=token_artifacts,
            next_action="Fix the prompt/context size or policy, then rerun execute.",
        )
    if token_gate.prompt_sha256 != prepared_sha256:
        return _blocked(
            "PREPARE_ARTIFACT_STALE",
            "Prepared prompt changed after the prepare phase.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                **token_artifacts,
                "expected_prompt_sha256": prepared_sha256,
                "actual_prompt_sha256": token_gate.prompt_sha256,
            },
            next_action="Rerun pipeline phase prepare, then execute again.",
        )

    adapter = codex_adapter or run_codex_adapter
    adapter_result = adapter(
        root=root_path,
        task_id=task_id,
        policy=policy,
        token_gate=token_gate,
        runner=execution_runner,
    )
    return _adapter_phase_result(
        adapter_result,
        session_id=selected_session_id,
        task_id=task_id,
        policy=policy,
        prepare_artifacts=prepare_artifacts,
        token_gate=token_gate,
        root=root_path,
        actor=actor,
    )


def _adapter_phase_result(
    adapter_result: CodexAdapterResult,
    *,
    session_id: str,
    task_id: str,
    policy: PipelinePolicy,
    prepare_artifacts: Mapping[str, Any],
    token_gate: TokenBudgetGateResult,
    root: Path,
    actor: str,
) -> CommandResult:
    adapter_data = adapter_result.to_dict()
    if adapter_result.code == CODE_MANUAL_HANDOFF:
        prompt_path = _manual_prompt_path(root, adapter_result, prepare_artifacts)
        report_command = _report_submission_command(task_id)
        next_action = _manual_handoff_next_action(prompt_path, report_command)
        adapter_data["report_instruction"] = next_action
        artifacts = _adapter_artifacts(
            adapter_result,
            adapter_data=adapter_data,
            session_id=session_id,
            task_id=task_id,
            policy=policy,
            prepare_artifacts=prepare_artifacts,
            token_gate=token_gate,
        )
        phase = PhaseResult.blocked(
            PHASE_NAME,
            reason=_adapter_phase_reason(
                "Manual Codex handoff is required.",
                adapter_result,
            ),
            next_action=next_action,
            artifacts={
                "blocked_by": "MANUAL_HANDOFF_REQUIRED",
                "prompt_path": prompt_path,
                "prompt_sha256": adapter_result.prompt_sha256
                or token_gate.prompt_sha256,
                "manual_handoff_instruction": (
                    "Run Codex manually with the prompt at {}."
                ).format(prompt_path),
                "report_submission_command": report_command,
                "report_submission_instruction": (
                    "After Codex finishes, submit the structured execution "
                    "report with: {}"
                ).format(report_command),
                **artifacts,
            },
        )
        return _phase_command(
            phase,
            session_id=session_id,
            task_id=task_id,
            root=root,
            actor=actor,
        )

    artifacts = _adapter_artifacts(
        adapter_result,
        adapter_data=adapter_data,
        session_id=session_id,
        task_id=task_id,
        policy=policy,
        prepare_artifacts=prepare_artifacts,
        token_gate=token_gate,
    )
    if adapter_result.status == "passed":
        phase = PhaseResult.passed(
            PHASE_NAME,
            reason=_adapter_phase_reason(
                "Codex execution adapter passed.",
                adapter_result,
            ),
            next_action="Run pipeline phase collect-report.",
            artifacts=artifacts,
        )
    elif (
        adapter_result.status == "blocked"
        and adapter_result.code == CODE_REPORT_MISSING
        and adapter_result.returncode == 0
    ):
        phase = PhaseResult.passed(
            PHASE_NAME,
            reason=(
                _adapter_phase_reason(
                    "Codex execution adapter completed; structured report "
                    "collection is pending.",
                    adapter_result,
                )
            ),
            next_action="Run pipeline phase collect-report.",
            artifacts=artifacts,
        )
    elif adapter_result.status == "blocked":
        phase = PhaseResult.blocked(
            PHASE_NAME,
            reason=_adapter_phase_reason(
                "Codex execution adapter blocked: {}".format(
                    adapter_result.reason
                ),
                adapter_result,
            ),
            next_action=adapter_result.report_instruction
            or "Resolve the adapter blocker, then rerun execute.",
            artifacts={"blocked_by": adapter_result.code, **artifacts},
        )
    else:
        phase = PhaseResult.failed(
            PHASE_NAME,
            reason=_adapter_phase_reason(
                "Codex execution adapter failed: {}".format(adapter_result.reason),
                adapter_result,
            ),
            next_action=adapter_result.report_instruction
            or "Fix the adapter failure, then rerun execute.",
            artifacts={"error_code": adapter_result.code, **artifacts},
        )
    return _phase_command(
        phase,
        session_id=session_id,
        task_id=task_id,
        root=root,
        actor=actor,
    )


def _adapter_artifacts(
    adapter_result: CodexAdapterResult,
    *,
    adapter_data: Mapping[str, Any],
    session_id: str,
    task_id: str,
    policy: PipelinePolicy,
    prepare_artifacts: Mapping[str, Any],
    token_gate: TokenBudgetGateResult,
) -> dict[str, Any]:
    artifacts = {
        "session_id": session_id,
        "task_id": task_id,
        "policy": policy.name,
        "prepare_artifacts": _bounded_prepare_artifacts(prepare_artifacts),
        "token_budget": token_gate.to_dict(),
        "codex_adapter_called": True,
        "execute_evidence": _adapter_evidence(adapter_result),
        "adapter": adapter_data,
        "adapter_summary": {
            "status": adapter_result.status,
            "code": adapter_result.code,
            "reason": adapter_result.reason,
            "command": list(adapter_result.command),
            "command_ref": adapter_result.command_ref,
            "returncode": adapter_result.returncode,
            "duration_sec": adapter_result.duration_sec,
            "stdout_ref": adapter_result.stdout_ref,
            "stderr_ref": adapter_result.stderr_ref,
            "stdout_snippet": adapter_result.stdout_snippet,
            "stderr_snippet": adapter_result.stderr_snippet,
            "stdout_bytes": adapter_result.stdout_bytes,
            "stderr_bytes": adapter_result.stderr_bytes,
            "report_required": adapter_result.report_required,
            "before_report_id": adapter_result.before_report_id,
            "after_report_id": adapter_result.after_report_id,
            "report_id": adapter_result.report_id,
            "report_ids": _adapter_report_ids(adapter_result),
        },
    }
    return artifacts


def _adapter_evidence(adapter_result: CodexAdapterResult) -> dict[str, Any]:
    return {
        "status": adapter_result.status,
        "code": adapter_result.code,
        "reason": adapter_result.reason,
        "command_ref": adapter_result.command_ref,
        "returncode": adapter_result.returncode,
        "duration_sec": adapter_result.duration_sec,
        "stdout_ref": adapter_result.stdout_ref,
        "stderr_ref": adapter_result.stderr_ref,
        "stdout_snippet": adapter_result.stdout_snippet,
        "stderr_snippet": adapter_result.stderr_snippet,
        "stdout_bytes": adapter_result.stdout_bytes,
        "stderr_bytes": adapter_result.stderr_bytes,
        "report_ids": _adapter_report_ids(adapter_result),
        "report_required": adapter_result.report_required,
    }


def _adapter_report_ids(adapter_result: CodexAdapterResult) -> list[str]:
    result: list[str] = []
    for value in (
        adapter_result.before_report_id,
        adapter_result.after_report_id,
        adapter_result.report_id,
    ):
        text = str(value or "")
        if text and text not in result:
            result.append(text)
    return result


def _adapter_phase_reason(prefix: str, adapter_result: CodexAdapterResult) -> str:
    details = [
        "status={}".format(adapter_result.status),
        "code={}".format(adapter_result.code),
        "returncode={}".format(
            adapter_result.returncode
            if adapter_result.returncode is not None
            else "none"
        ),
    ]
    return "{} ({})".format(prefix, ", ".join(details))


def _manual_prompt_path(
    root: Path,
    adapter_result: CodexAdapterResult,
    prepare_artifacts: Mapping[str, Any],
) -> str:
    prompt_value = adapter_result.prompt_path or str(
        prepare_artifacts.get("prompt_path") or ""
    )
    if not prompt_value:
        return ""
    return _repo_path(root, _artifact_path(root, prompt_value))


def _report_submission_command(task_id: str) -> str:
    return (
        "python scripts/aictl.py task report submit "
        "--task {} --file <REPORT.json> --confirm"
    ).format(task_id)


def _manual_handoff_next_action(prompt_path: str, report_command: str) -> str:
    return (
        "Run Codex manually with the prompt at {}, then submit the structured "
        "execution report: {}"
    ).format(prompt_path, report_command)


def _prepared_artifact_check(
    root: Path,
    session: Mapping[str, Any],
    prepare_result: Mapping[str, Any],
    artifacts: Mapping[str, Any],
    actor: str,
) -> CommandResult | None:
    session_id = str(session.get("id") or "")
    if str(prepare_result.get("status") or "") != "passed":
        return _blocked(
            "PREPARE_PHASE_NOT_PASSED",
            "Latest prepare phase did not pass.",
            session_id=session_id,
            root=root,
            actor=actor,
            artifacts={
                "prepare_status": str(prepare_result.get("status") or ""),
                "prepare_reason": str(prepare_result.get("reason") or ""),
                "codex_adapter_called": False,
            },
            next_action="Rerun pipeline phase prepare until it passes.",
        )

    missing = [
        field
        for field in ("task_id", "prompt_path", "prompt_sha256")
        if not str(artifacts.get(field) or "").strip()
    ]
    if missing:
        return _blocked(
            "PREPARE_ARTIFACT_MISSING",
            "Prepare phase evidence is missing required field(s): {}".format(
                ", ".join(missing)
            ),
            session_id=session_id,
            root=root,
            actor=actor,
            artifacts={"missing": missing, "codex_adapter_called": False},
            next_action="Rerun pipeline phase prepare to refresh artifact evidence.",
        )

    task_id = str(artifacts["task_id"])
    session_task_id = str(session.get("current_task_id") or "")
    if session_task_id and session_task_id != task_id:
        return _blocked(
            "PREPARE_ARTIFACT_TASK_MISMATCH",
            "Prepare evidence does not match the session current task.",
            session_id=session_id,
            task_id=task_id,
            root=root,
            actor=actor,
            artifacts={
                "session_task_id": session_task_id,
                "prepared_task_id": task_id,
                "codex_adapter_called": False,
            },
            next_action="Rerun pipeline phase prepare for the selected session task.",
        )

    prompt_path = _artifact_path(root, artifacts["prompt_path"])
    if not prompt_path.exists():
        return _blocked(
            "PREPARE_PROMPT_MISSING",
            "Prepared prompt file is missing.",
            session_id=session_id,
            task_id=task_id,
            root=root,
            actor=actor,
            artifacts={
                "prompt_path": _repo_path(root, prompt_path),
                "codex_adapter_called": False,
            },
            next_action="Rerun pipeline phase prepare to rebuild the prompt.",
        )

    actual_sha256 = _sha256(prompt_path)
    expected_sha256 = str(artifacts["prompt_sha256"])
    if actual_sha256 != expected_sha256:
        return _blocked(
            "PREPARE_ARTIFACT_STALE",
            "Prepared prompt checksum no longer matches the prompt file.",
            session_id=session_id,
            task_id=task_id,
            root=root,
            actor=actor,
            artifacts={
                "prompt_path": _repo_path(root, prompt_path),
                "expected_prompt_sha256": expected_sha256,
                "actual_prompt_sha256": actual_sha256,
                "codex_adapter_called": False,
            },
            next_action="Rerun pipeline phase prepare, then execute again.",
        )
    return None


def _resolve_session(root: Path, session_id: str) -> CommandResult:
    state = load_pipeline_state(root)
    selected_id = session_id.strip() or str(state.get("current_session_id") or "")
    if not selected_id:
        return _failure(
            "PIPELINE_SESSION_REQUIRED",
            "Pass a session id or set a current pipeline session before execute.",
            details={"state_path": str(pipeline_state_path(root))},
        )
    for session in state.get("sessions", []):
        if isinstance(session, Mapping) and session.get("id") == selected_id:
            return CommandResult.success(
                command=COMMAND_NAME,
                domain="pipeline",
                message="Pipeline session loaded.",
                data={"session": dict(session)},
            )
    return _failure(
        "PIPELINE_SESSION_NOT_FOUND",
        "pipeline session not found: {}".format(selected_id),
        details={"session_id": selected_id},
    )


def _latest_prepare_result(session: Mapping[str, Any]) -> Mapping[str, Any] | None:
    history = session.get("phase_history")
    if not isinstance(history, list):
        return None
    for entry in reversed(history):
        if (
            isinstance(entry, Mapping)
            and str(entry.get("phase") or "") == PREPARE_PHASE_NAME
        ):
            return entry
    return None


def _phase_command(
    phase: PhaseResult,
    *,
    session_id: str,
    task_id: str = "",
    root: Path | None = None,
    actor: str = "human_owner",
) -> CommandResult:
    if root is not None and session_id:
        result = record_phase_result(
            session_id,
            phase,
            root=root,
            actor=actor,
            task_id=task_id,
            command=COMMAND_NAME,
        )
        if not result.ok:
            return result
        result.message = phase.reason
        if phase.status.value == "failed":
            result.ok = False
        if phase.next_action and phase.next_action not in result.next_actions:
            result.next_actions.append(phase.next_action)
        return result

    result = CommandResult.success(
        command=COMMAND_NAME,
        domain="pipeline",
        message=phase.reason,
        data={
            "phase_result": phase.to_dict(),
            "session_id": session_id,
            "task_id": task_id,
        },
    )
    if phase.status.value == "failed":
        result.ok = False
    if phase.next_action:
        result.next_actions.append(phase.next_action)
    return result


def _blocked(
    code: str,
    message: str,
    *,
    session_id: str,
    task_id: str = "",
    root: Path,
    actor: str,
    artifacts: Mapping[str, Any] | None = None,
    next_action: str,
) -> CommandResult:
    phase = PhaseResult.blocked(
        PHASE_NAME,
        reason=message,
        next_action=next_action,
        artifacts={"blocked_by": code, **dict(artifacts or {})},
    )
    return _phase_command(
        phase,
        session_id=session_id,
        task_id=task_id,
        root=root,
        actor=actor,
    )


def _failure(
    code: str,
    message: str,
    *,
    details: Mapping[str, Any] | None = None,
    session_id: str = "",
    task_id: str = "",
    root: Path | None = None,
    actor: str = "human_owner",
) -> CommandResult:
    phase = PhaseResult.failed(
        PHASE_NAME,
        reason=message,
        next_action="Fix the execute input and rerun the phase.",
        artifacts={"error_code": code, **dict(details or {})},
    )
    if root is not None and session_id:
        result = _phase_command(
            phase,
            session_id=session_id,
            task_id=task_id,
            root=root,
            actor=actor,
        )
        result.ok = False
        result.errors.append(
            CommandMessage(code, message, details=dict(details or {}))
        )
        return result

    result = CommandResult.failure(
        command=COMMAND_NAME,
        domain="pipeline",
        message=message,
        errors=[CommandMessage(code, message, details=dict(details or {}))],
    )
    result.data = {"phase_result": phase.to_dict()}
    if session_id:
        result.data["session_id"] = session_id
    return result


def _bounded_prepare_artifacts(artifacts: Mapping[str, Any]) -> dict[str, Any]:
    allowed = ("task_id", "context_pack_path", "prompt_path", "prompt_sha256")
    return {key: artifacts[key] for key in allowed if key in artifacts}


def _required_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    raise TypeError("{} must be a mapping".format(name))


def _mapping(value: Any, *, default: Mapping[str, Any]) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else default


def _artifact_path(root: Path, value: Any) -> Path:
    path = Path(str(value))
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def _repo_path(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


__all__ = ["execute_phase"]

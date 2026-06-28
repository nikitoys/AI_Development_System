"""Supervised one-step pipeline runner.

The runner advances at most one pipeline step. It records every gate through
the governed pipeline session service and delegates lifecycle mutations to
existing workflow commands.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from ai_project_ctl.core.result import CommandMessage, CommandResult
from ai_project_ctl.core.store import read_json_file
from ai_project_ctl.core.workflows import Runner, run_workflow

from .close_policy import (
    CODE_TASK_AUTO_CLOSED,
    CODE_REVIEW_CLOSE_WORKFLOW_FAILED,
    decide_review_close,
    run_review_close_workflow,
)
from .codex_adapter import CodexAdapterResult, run_codex_adapter
from .codex_review import BLOCKED as CODEX_REVIEW_BLOCKED_STATUS
from .codex_review import FAIL as CODEX_REVIEW_FAIL
from .codex_review import PASS as CODEX_REVIEW_PASS
from .codex_review import VERDICT_BLOCKED
from .codex_review import VERDICT_REQUEST_CHANGES
from .codex_review import evaluate_codex_review
from .machine_review import FAIL as MACHINE_REVIEW_FAIL
from .machine_review import evaluate_machine_review
from .policy import CodexExecutionMode, PipelinePolicy
from .queue import QueuePlannerRequest, QueuePreview, QueuePreviewItem, preview_queue
from .report_gate import FAIL as REPORT_GATE_FAIL
from .report_gate import evaluate_report_gate
from .git_commit import PASS as COMMIT_PASS
from .git_commit import run_local_commit
from .session import (
    ensure_file_evidence_baseline,
    record_phase_result,
    record_step_result,
)
from .state import (
    load_pipeline_state,
    load_reference_state,
    pipeline_state_path,
)
from .token_budget import PASS as TOKEN_BUDGET_PASS
from .token_budget import evaluate_token_budget


RUN_NEXT_STEP = "run_next"
TERMINAL_CHANGE_STATUSES = {"approved", "in_progress", "in_review", "accepted"}
SESSION_APPROVAL_CHANGE_STATUSES = {"ready", "proposed"}
SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"


def run_next(
    session_id: str = "",
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    python_executable: str | None = None,
    runner: Runner | None = None,
    codex_adapter=None,
    codex_reviewer=None,
) -> CommandResult:
    """Dispatch exactly one next required pipeline phase."""

    root_path = Path(root).resolve()
    selected = _resolve_session(root_path, session_id)
    if not selected.ok:
        return selected

    session = dict(selected.data["session"])
    selected_session_id = str(session["id"])
    status = str(session.get("status") or "")
    if status not in ACTIVE_RUN_NEXT_STATUSES:
        return _terminal_run_next_result(
            selected_session_id,
            status=status,
            reason="Pipeline session is not runnable: {}".format(status),
        )

    baseline = ensure_file_evidence_baseline(
        selected_session_id,
        root=root_path,
        actor=actor,
    )
    if not baseline.ok:
        return baseline
    effects = [baseline] if baseline.changed_files or baseline.events else []

    phase_name = _next_required_phase(session)
    delegated = _dispatch_run_next_phase(
        phase_name,
        selected_session_id,
        root=root_path,
        actor=actor,
        python_executable=python_executable or sys.executable,
        runner=runner,
        codex_adapter=codex_adapter,
        codex_reviewer=codex_reviewer,
    )
    delegated = _ensure_dispatched_phase_recorded(
        delegated,
        session_id=selected_session_id,
        root=root_path,
        actor=actor,
    )
    effects.append(delegated)
    return _phase_dispatch_result(
        delegated,
        phase_name=phase_name,
        session=session,
        effects=effects,
    )


RUN_NEXT_PHASE_SEQUENCE = (
    "queue_preview",
    "prepare",
    "execute",
    "collect_report",
    "verify",
    "review",
    "close",
)
RUN_NEXT_PHASE_ALIASES = {
    "queue": "queue_preview",
    "queue-preview": "queue_preview",
    "collect-report": "collect_report",
}
ACTIVE_RUN_NEXT_STATUSES = {"planned", "running", "stopped", "blocked", "failed"}


def _next_required_phase(session: Mapping[str, Any]) -> str:
    latest = _latest_known_phase(session)
    if latest is None:
        return "queue_preview"

    phase = _normalized_phase_name(latest.get("phase"))
    status = str(latest.get("status") or "")
    if status in {"blocked", "failed"}:
        return _phase_after_blocker(phase, latest) or phase
    if status in {"passed", "skipped"}:
        return _phase_after(phase)
    return phase or "queue_preview"


def _latest_known_phase(session: Mapping[str, Any]) -> Mapping[str, Any] | None:
    history = session.get("phase_history")
    if not isinstance(history, Sequence) or isinstance(history, (str, bytes)):
        return None
    for entry in reversed(history):
        if not isinstance(entry, Mapping):
            continue
        phase = _normalized_phase_name(entry.get("phase"))
        if phase in RUN_NEXT_PHASE_SEQUENCE:
            return entry
    return None


def _phase_after(phase: str) -> str:
    selected = _normalized_phase_name(phase)
    if selected not in RUN_NEXT_PHASE_SEQUENCE:
        return "queue_preview"
    if selected == "close":
        return "queue_preview"
    index = RUN_NEXT_PHASE_SEQUENCE.index(selected)
    return RUN_NEXT_PHASE_SEQUENCE[index + 1]


def _phase_after_blocker(
    phase: str,
    phase_result: Mapping[str, Any],
) -> str:
    blocked_by = _phase_blocked_by(phase_result)
    if phase == "execute" and blocked_by in {
        "MANUAL_HANDOFF_REQUIRED",
        "CODEX_ADAPTER_MANUAL_HANDOFF_REQUIRED",
    }:
        return "collect_report"
    return ""


def _dispatch_run_next_phase(
    phase_name: str,
    session_id: str,
    *,
    root: Path,
    actor: str,
    python_executable: str,
    runner: Runner | None,
    codex_adapter,
    codex_reviewer,
) -> CommandResult:
    if phase_name == "queue_preview":
        from .queue_phase import preview_queue_phase

        preview = preview_queue_phase(session_id, root=root)
        return _record_queue_preview_dispatch(
            preview,
            session_id=session_id,
            root=root,
            actor=actor,
        )
    if phase_name == "prepare":
        from .prepare_phase import prepare_phase

        return prepare_phase(
            session_id,
            root=root,
            actor=actor,
            python_executable=python_executable,
            runner=runner,
        )
    if phase_name == "execute":
        from .execute_phase import execute_phase

        return execute_phase(
            session_id,
            root=root,
            actor=actor,
            codex_adapter=codex_adapter,
            execution_runner=runner,
        )
    if phase_name == "collect_report":
        from .report_phase import collect_report_phase

        return collect_report_phase(session_id, root=root, actor=actor)
    if phase_name == "verify":
        from .verify_phase import verify_phase

        return verify_phase(session_id, root=root, actor=actor)
    if phase_name == "review":
        from .review_phase import review_phase

        if codex_reviewer is not None:
            return _review_callable_not_supported(
                session_id,
                root=root,
                actor=actor,
            )
        return review_phase(
            session_id,
            root=root,
            actor=actor,
            build_prompt_only=True,
        )
    if phase_name == "close":
        from .close_phase import close_phase

        return close_phase(session_id, root=root, actor=actor, confirmed=True)
    return CommandResult.failure(
        command="pipeline.run_next",
        domain="pipeline",
        message="Unsupported pipeline phase: {}".format(phase_name),
        errors=[
            CommandMessage(
                "PIPELINE_PHASE_UNSUPPORTED",
                "run-next cannot dispatch phase: {}".format(phase_name),
                details={"phase": phase_name},
            )
        ],
    )


def _record_queue_preview_dispatch(
    preview: CommandResult,
    *,
    session_id: str,
    root: Path,
    actor: str,
) -> CommandResult:
    phase_result = _phase_result_payload(preview)
    if not phase_result:
        return preview

    recorded = record_phase_result(
        session_id,
        phase_result,
        root=root,
        actor=actor,
        command="pipeline.phase.queue_preview",
    )
    recorded.message = preview.message
    recorded.ok = preview.ok and str(phase_result.get("status") or "") != "failed"
    recorded.errors.extend(preview.errors)
    recorded.warnings.extend(preview.warnings)
    recorded.data["queue_preview"] = dict(preview.data.get("queue_preview") or {})
    recorded.data["queue_source"] = str(preview.data.get("queue_source") or "")
    next_action = str(phase_result.get("next_action") or "")
    if next_action and next_action not in recorded.next_actions:
        recorded.next_actions.append(next_action)
    return recorded


def _review_callable_not_supported(
    session_id: str,
    *,
    root: Path,
    actor: str,
) -> CommandResult:
    from .phase import PhaseResult

    phase = PhaseResult.blocked(
        "review",
        reason=(
            "Review phase dispatch does not support an in-process reviewer callable; "
            "use review phase build-prompt-only, manual-review-file, or reviewer-command."
        ),
        next_action=(
            "Run pipeline phase review with build-prompt-only and provide the "
            "review result through an approved review input."
        ),
        artifacts={
            "blocked_by": "REVIEW_CALLABLE_UNSUPPORTED",
            "session_id": session_id,
        },
    )
    result = record_phase_result(
        session_id,
        phase,
        root=root,
        actor=actor,
        command="pipeline.phase.review",
    )
    result.message = phase.reason
    result.owner_action_required = phase.reason
    if phase.next_action:
        result.next_actions.append(phase.next_action)
    return result


def _phase_dispatch_result(
    delegated: CommandResult,
    *,
    phase_name: str,
    session: Mapping[str, Any],
    effects: Sequence[CommandResult],
) -> CommandResult:
    phase_result = _phase_result_payload(delegated)
    if not phase_result:
        result = CommandResult.failure(
            command="pipeline.run_next",
            domain="pipeline",
            message="Delegated phase did not return a phase_result payload.",
            errors=list(delegated.errors)
            or [
                CommandMessage(
                    "PIPELINE_PHASE_RESULT_MISSING",
                    "Delegated phase did not return data.phase_result.",
                    details={"phase": phase_name, "command": delegated.command},
                )
            ],
        )
        result.data = {"session_id": str(session.get("id") or ""), "phase": phase_name}
        _merge_effects(result, effects)
        return result

    artifacts = _mapping_or_empty(phase_result.get("artifacts"))
    status = str(phase_result.get("status") or "")
    reason = str(phase_result.get("reason") or delegated.message or "")
    next_action = str(phase_result.get("next_action") or "")
    blocked_by = _phase_blocked_by(phase_result)
    selected_task = _phase_selected_task(phase_result, delegated, session)
    stop_code = _phase_stop_code(status, blocked_by)

    result = CommandResult(
        ok=delegated.ok,
        command="pipeline.run_next",
        domain="pipeline",
        message=reason or delegated.message,
        data={
            "session_id": str(session.get("id") or ""),
            "dispatched_phase": str(phase_result.get("phase") or phase_name),
            "phase_status": status,
            "phase_result": phase_result,
            "blocked_by": blocked_by,
            "next_action": next_action,
            "selected_task": selected_task,
            "queue_counts": _mapping_or_empty(artifacts.get("queue_counts")),
            "side_effects": [effect.to_dict() for effect in effects],
        },
        warnings=list(delegated.warnings),
        errors=list(delegated.errors),
        revision_before=delegated.revision_before,
        revision_after=delegated.revision_after,
    )
    if stop_code:
        result.data["stop_code"] = stop_code
        result.data["stop_reason"] = reason
        result.owner_action_required = reason
    close_status = _mapping_or_empty(artifacts.get("close_status"))
    if close_status:
        result.data["close_status"] = close_status
        result.data["close_outcome"] = str(close_status.get("outcome") or "")
        result.data["commit_status"] = str(close_status.get("commit_status") or "")
    if next_action:
        result.next_actions.append(next_action)
    _merge_effects(result, effects)
    return result


def _ensure_dispatched_phase_recorded(
    delegated: CommandResult,
    *,
    session_id: str,
    root: Path,
    actor: str,
) -> CommandResult:
    phase_result = _phase_result_payload(delegated)
    if not phase_result:
        return delegated
    session = _session_by_id(root, session_id)
    if _latest_phase_matches(session, phase_result):
        return delegated

    recorded = record_phase_result(
        session_id,
        phase_result,
        root=root,
        actor=actor,
        task_id=_phase_task_id(phase_result, delegated, session),
        command=str(delegated.command or "pipeline.run_next"),
    )
    delegated.data.setdefault("side_effects", []).append(recorded.to_dict())
    _merge_effects(delegated, (recorded,))
    if not recorded.ok:
        delegated.ok = False
        delegated.errors.extend(recorded.errors)
    return delegated


def _terminal_run_next_result(
    session_id: str,
    *,
    status: str,
    reason: str,
) -> CommandResult:
    stop_code = "QUEUE_COMPLETE" if status == "completed" else "SESSION_NOT_RUNNABLE"
    result = CommandResult.success(
        command="pipeline.run_next",
        domain="pipeline",
        message="{}: {}".format(stop_code, reason),
        data={
            "session_id": session_id,
            "stop_code": stop_code,
            "stop_reason": reason,
            "phase_result": {
                "phase": "run_next",
                "status": "blocked",
                "reason": reason,
                "next_action": "Create or select an active pipeline session before rerunning.",
                "blocked_by": stop_code,
                "artifacts": {"blocked_by": stop_code, "session_status": status},
                "changed_files": [],
                "generated_files": [],
                "events": [],
            },
            "blocked_by": stop_code,
            "next_action": "Create or select an active pipeline session before rerunning.",
        },
    )
    result.owner_action_required = reason
    result.next_actions.append("Create or select an active pipeline session before rerunning.")
    return result


def _phase_result_payload(result: CommandResult) -> dict[str, Any]:
    data = result.data if isinstance(result.data, Mapping) else {}
    raw = data.get("phase_result")
    if not isinstance(raw, Mapping):
        return {}
    payload = dict(raw)
    artifacts = _mapping_or_empty(payload.get("artifacts"))
    blocked_by = str(payload.get("blocked_by") or artifacts.get("blocked_by") or "")
    if blocked_by:
        artifacts["blocked_by"] = blocked_by
    payload["artifacts"] = artifacts
    from .phase import PhaseResult

    normalized = PhaseResult.from_dict(payload).to_dict()
    if blocked_by:
        normalized["blocked_by"] = blocked_by
    return normalized


def _phase_blocked_by(phase_result: Mapping[str, Any]) -> str:
    artifacts = _mapping_or_empty(phase_result.get("artifacts"))
    return str(phase_result.get("blocked_by") or artifacts.get("blocked_by") or "")


def _phase_stop_code(status: str, blocked_by: str) -> str:
    if status == "blocked":
        return blocked_by or "PIPELINE_PHASE_BLOCKED"
    if status == "failed":
        return blocked_by or "PIPELINE_PHASE_FAILED"
    return ""


def _phase_selected_task(
    phase_result: Mapping[str, Any],
    delegated: CommandResult,
    session: Mapping[str, Any],
) -> Mapping[str, Any] | None:
    artifacts = _mapping_or_empty(phase_result.get("artifacts"))
    for key in ("selected_task", "next_task"):
        value = artifacts.get(key)
        if isinstance(value, Mapping):
            return dict(value)
    value = delegated.data.get("selected_task") if isinstance(delegated.data, Mapping) else None
    if isinstance(value, Mapping):
        return dict(value)
    task_id = str(
        artifacts.get("task_id")
        or delegated.data.get("task_id")
        or session.get("current_task_id")
        or ""
    )
    if not task_id:
        return None
    return {"id": task_id, "ref": str(session.get("current_task_ref") or task_id)}


def _phase_task_id(
    phase_result: Mapping[str, Any],
    delegated: CommandResult,
    session: Mapping[str, Any],
) -> str:
    selected = _phase_selected_task(phase_result, delegated, session)
    if isinstance(selected, Mapping):
        return str(selected.get("id") or "")
    return ""


def _session_by_id(root: Path, session_id: str) -> Mapping[str, Any]:
    for session in load_pipeline_state(root).get("sessions", []):
        if isinstance(session, Mapping) and session.get("id") == session_id:
            return session
    return {}


def _latest_phase_matches(
    session: Mapping[str, Any],
    phase_result: Mapping[str, Any],
) -> bool:
    latest = _latest_known_phase(session)
    if latest is None:
        return False
    return (
        _normalized_phase_name(latest.get("phase"))
        == _normalized_phase_name(phase_result.get("phase"))
        and str(latest.get("status") or "") == str(phase_result.get("status") or "")
        and str(latest.get("reason") or "") == str(phase_result.get("reason") or "")
    )


def _normalized_phase_name(value: Any) -> str:
    selected = str(value or "").strip()
    return RUN_NEXT_PHASE_ALIASES.get(selected, selected)


def _mapping_or_empty(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _apply_review_close_policy(
    *,
    session: Mapping[str, Any],
    policy: PipelinePolicy,
    report_gate,
    machine_review,
    codex_review,
    gate_details: Mapping[str, Any],
    selected_session_id: str,
    selected: QueuePreviewItem,
    queue_preview: QueuePreview,
    side_effects: list[CommandResult],
    root: Path,
    actor: str,
    python_executable: str,
    runner: Runner | None,
) -> CommandResult:
    decision = decide_review_close(
        policy=policy,
        report_gate=report_gate,
        machine_review=machine_review,
        codex_review=codex_review,
        session=session,
    )
    close_details: dict[str, Any] = {
        **dict(gate_details),
        "close_policy": decision.to_dict(),
    }

    workflow = run_review_close_workflow(
        decision,
        root=root,
        actor=actor,
        task_id=str(selected.id or ""),
        python_executable=python_executable,
        runner=runner,
    )
    if decision.should_run_workflow or not workflow.ok:
        side_effects.append(workflow)
        close_details["close_policy_workflow"] = workflow.to_dict()

    if not workflow.ok:
        return _record_stop(
            selected_session_id,
            stop_code=CODE_REVIEW_CLOSE_WORKFLOW_FAILED,
            stop_reason=workflow.message,
            result_status="blocked",
            gate_name="review_close_gate",
            gate_status="fail",
            gate_details=close_details,
            selected_task=selected,
            policy_name=policy.name,
            queue_preview=queue_preview,
            side_effects=side_effects,
            root=root,
            actor=actor,
            report_ids=(codex_review.report_id,) if codex_review.report_id else (),
            review_ids=(codex_review.review_id,) if codex_review.review_id else (),
        )

    return _record_stop(
        selected_session_id,
        stop_code=decision.stop_code,
        stop_reason=decision.reason,
        result_status=decision.result_status,
        gate_name="review_close_gate",
        gate_status=decision.gate_status,
        gate_details=close_details,
        selected_task=selected,
        policy_name=policy.name,
        queue_preview=queue_preview,
        side_effects=side_effects,
        root=root,
        actor=actor,
        report_ids=(codex_review.report_id,) if codex_review.report_id else (),
        review_ids=(codex_review.review_id,) if codex_review.review_id else (),
    )


def _apply_local_commit_policy(
    *,
    policy: PipelinePolicy,
    report_gate,
    machine_review,
    codex_review,
    gate_details: Mapping[str, Any],
    selected_session_id: str,
    selected: QueuePreviewItem,
    queue_preview: QueuePreview,
    side_effects: list[CommandResult],
    root: Path,
    actor: str,
    runner: Runner | None,
) -> CommandResult:
    commit_result = run_local_commit(
        root=root,
        task_id=str(selected.id or ""),
        session_id=selected_session_id,
        policy=policy,
        report_gate=report_gate,
        machine_review=machine_review,
        codex_review=codex_review,
        side_effects=side_effects,
        runner=runner,
    )
    commit_details = {
        **dict(gate_details),
        "commit": commit_result.to_dict(),
    }
    if commit_result.status == COMMIT_PASS:
        return _record_stop(
            selected_session_id,
            stop_code=commit_result.code,
            stop_reason=commit_result.reason,
            result_status="passed",
            gate_name="commit_gate",
            gate_status="pass",
            gate_details=commit_details,
            selected_task=selected,
            policy_name=policy.name,
            queue_preview=queue_preview,
            side_effects=side_effects,
            root=root,
            actor=actor,
            report_ids=(report_gate.report_id,) if report_gate.report_id else (),
            review_ids=(codex_review.review_id,) if codex_review.review_id else (),
            commit_ids=(commit_result.commit_hash,) if commit_result.commit_hash else (),
        )

    return _record_stop(
        selected_session_id,
        stop_code=commit_result.code,
        stop_reason=commit_result.reason,
        result_status="failed" if commit_result.status == "fail" else "blocked",
        gate_name="commit_gate",
        gate_status="fail" if commit_result.status == "fail" else "blocked",
        gate_details=commit_details,
        selected_task=selected,
        policy_name=policy.name,
        queue_preview=queue_preview,
        side_effects=side_effects,
        root=root,
        actor=actor,
        report_ids=(report_gate.report_id,) if report_gate.report_id else (),
        review_ids=(codex_review.review_id,) if codex_review.review_id else (),
    )


def _resolve_session(root: Path, session_id: str) -> CommandResult:
    state = load_pipeline_state(root)
    sessions = [
        session
        for session in state.get("sessions", [])
        if isinstance(session, Mapping)
    ]
    selected_id = session_id or str(state.get("current_session_id") or "")
    if not selected_id:
        return CommandResult.failure(
            command="pipeline.run_next",
            domain="pipeline",
            message="No pipeline session selected.",
            errors=[
                CommandMessage(
                    "PIPELINE_NO_SESSION_SELECTED",
                    "Pass a session id or create a current pipeline session first.",
                    details={"state_path": str(pipeline_state_path(root))},
                )
            ],
        )
    for session in sessions:
        if session.get("id") == selected_id:
            return CommandResult.success(
                command="pipeline.run_next",
                domain="pipeline",
                message="Pipeline session loaded.",
                data={"session": dict(session)},
            )
    return CommandResult.failure(
        command="pipeline.run_next",
        domain="pipeline",
        message="Pipeline session not found.",
        errors=[
            CommandMessage(
                "PIPELINE_SESSION_NOT_FOUND",
                "pipeline session not found: {}".format(selected_id),
                details={"session_id": selected_id},
            )
        ],
    )


def _preview_session_queue(
    session: Mapping[str, Any],
    policy: PipelinePolicy,
    tasks_state: Mapping[str, Any],
    plan: Mapping[str, Any] | None,
) -> QueuePreview:
    queue = _mapping(session.get("selected_queue"), "selected_queue")
    request = QueuePlannerRequest(
        task_refs=_string_tuple(queue.get("task_refs")),
        epic_ids=_string_tuple(queue.get("epic_ids")),
        statuses=_string_tuple(queue.get("statuses")),
        max_tasks=_optional_int(queue.get("max_tasks")),
        order_by=str(queue.get("order_by") or "execution"),
    )
    return preview_queue(tasks_state, plan, policy=policy, request=request)


def _ensure_approved_changes_for_queue(
    queue_preview: QueuePreview,
    policy: PipelinePolicy,
    evolution_state: Any,
    *,
    session_id: str,
    root: Path,
    actor: str,
    python_executable: str,
    runner: Runner | None,
) -> CommandResult:
    return _ensure_approved_changes_for_tasks(
        _queue_task_ids(queue_preview),
        _queue_task_ref_map(queue_preview),
        policy,
        evolution_state,
        session_id=session_id,
        root=root,
        actor=actor,
        python_executable=python_executable,
        runner=runner,
        scope="selected_queue",
        preflight_requires_session_action=True,
        disabled_message="Queue-wide Change preflight is not enabled by policy.",
        approval_message="Owner-approved session Change approval completed for selected queue.",
        pass_message="Approved Change gate passed for selected queue.",
    )


def _ensure_approved_change_for_selected_task(
    selected_task: QueuePreviewItem,
    policy: PipelinePolicy,
    evolution_state: Any,
    *,
    session_id: str,
    root: Path,
    actor: str,
    python_executable: str,
    runner: Runner | None,
) -> CommandResult:
    task_id = str(selected_task.id or "")
    task_ref = str(selected_task.ref or selected_task.selected_ref or task_id)
    if not task_id:
        result = CommandResult.failure(
            command="pipeline.change_gate",
            domain="pipeline",
            message="Selected task has no stable task id.",
            errors=[
                CommandMessage(
                    "PIPELINE_SELECTED_TASK_ID_MISSING",
                    "Queue planner selected a task without a stable task id.",
                )
            ],
        )
        result.data = {
            "required": True,
            "scope": "selected_task",
            "stop_code": "UNSAFE_CONDITION",
            "selected_task_id": "",
            "selected_task_ref": task_ref,
            "inspected_task_ids": [],
            "linked_changes_inspected": [],
        }
        return result
    return _ensure_approved_changes_for_tasks(
        (task_id,),
        {task_id: task_ref},
        policy,
        evolution_state,
        session_id=session_id,
        root=root,
        actor=actor,
        python_executable=python_executable,
        runner=runner,
        scope="selected_task",
        preflight_requires_session_action=False,
        disabled_message="Selected-task Change gate is not enabled by policy.",
        approval_message="Owner-approved session Change approval completed for selected task.",
        pass_message="Approved Change gate passed for selected task.",
    )


def _ensure_approved_changes_for_tasks(
    task_ids: Sequence[str],
    task_refs: Mapping[str, str],
    policy: PipelinePolicy,
    evolution_state: Any,
    *,
    session_id: str,
    root: Path,
    actor: str,
    python_executable: str,
    runner: Runner | None,
    scope: str,
    preflight_requires_session_action: bool,
    disabled_message: str,
    approval_message: str,
    pass_message: str,
) -> CommandResult:
    inspected_task_ids: list[str] = []
    for task_id in task_ids:
        normalized = str(task_id or "")
        if normalized and normalized not in inspected_task_ids:
            inspected_task_ids.append(normalized)

    linked_changes_inspected: list[dict[str, Any]] = []

    def context_data() -> dict[str, Any]:
        data: dict[str, Any] = {
            "scope": scope,
            "inspected_task_ids": list(inspected_task_ids),
            "linked_changes_inspected": [dict(item) for item in linked_changes_inspected],
        }
        if scope == "selected_task" and inspected_task_ids:
            selected_task_id = inspected_task_ids[0]
            data["selected_task_id"] = selected_task_id
            data["selected_task_ref"] = task_refs.get(selected_task_id, selected_task_id)
        return data

    owner_approval_enabled = (
        policy.evolution.owner_approve_required_changes_for_session
    )
    approval_note = policy.evolution.owner_approval_note.strip()
    if (
        preflight_requires_session_action
        and not policy.evolution.create_missing_change
        and not owner_approval_enabled
    ):
        return CommandResult.success(
            command="pipeline.change_gate",
            domain="pipeline",
            message=disabled_message,
            data={"required": False, **context_data()},
        )
    if not policy.evolution.require_approved_change_for_execution:
        return CommandResult.success(
            command="pipeline.change_gate",
            domain="pipeline",
            message="Approved Change gate is not required by policy.",
            data={"required": False, **context_data()},
        )

    created_change_ids: list[str] = []
    linked_change_ids: list[str] = []
    tasks_requiring_approval: list[str] = []
    approval_candidates: list[dict[str, str]] = []
    unapprovable_changes: list[dict[str, str]] = []
    workflows: list[dict[str, Any]] = []
    effects: list[CommandResult] = []

    for task_id in inspected_task_ids:
        linked = _linked_changes_for_task(task_id, evolution_state)
        linked_for_task = [
            str(change.get("id"))
            for change in linked
            if str(change.get("id") or "")
        ]
        inspected_entry: dict[str, Any] = {
            "task_id": task_id,
            "task_ref": task_refs.get(task_id, task_id),
            "change_ids": linked_for_task,
        }
        linked_changes_inspected.append(inspected_entry)
        approved = [
            change
            for change in linked
            if str(change.get("status") or "") in TERMINAL_CHANGE_STATUSES
        ]
        if approved:
            _extend_unique(linked_change_ids, [str(change.get("id")) for change in approved])
            continue
        if linked:
            _extend_unique(linked_change_ids, [str(change.get("id")) for change in linked])
            tasks_requiring_approval.append(task_id)
            for change in linked:
                change_id = str(change.get("id") or "")
                status = str(change.get("status") or "")
                if status in SESSION_APPROVAL_CHANGE_STATUSES:
                    approval_candidates.append(
                        {
                            "change_id": change_id,
                            "task_id": task_id,
                            "task_ref": task_refs.get(task_id, task_id),
                            "status": status,
                        }
                    )
                else:
                    unapprovable_changes.append(
                        {
                            "change_id": change_id,
                            "task_id": task_id,
                            "task_ref": task_refs.get(task_id, task_id),
                            "status": status,
                        }
                    )
            continue

        if not policy.evolution.create_missing_change:
            tasks_requiring_approval.append(task_id)
            continue

        created = run_workflow(
            "evolution.create_for_task",
            task_ref=task_id,
            root=root,
            actor=actor,
            confirmed=True,
            python_executable=python_executable,
            runner=runner,
        )
        effects.append(created)
        workflows.append(_workflow_summary(created))
        if not created.ok:
            result = CommandResult.failure(
                command="pipeline.change_gate",
                domain="pipeline",
                message="Evolution Change creation workflow failed.",
                errors=list(created.errors)
                or [
                    CommandMessage(
                        "PIPELINE_CHANGE_CREATE_FAILED",
                        "Could not create required Evolution Change for task {}.".format(task_id),
                    )
                ],
            )
            result.data = {
                "required": True,
                "stop_code": "BLOCKED",
                **context_data(),
                "task_id": task_id,
                "workflows": workflows,
            }
            _merge_effects(result, effects)
            return result
        change_id = str(created.data.get("change_id") or "")
        if change_id:
            created_change_ids.append(change_id)
            linked_change_ids.append(change_id)
            inspected_entry.setdefault("created_change_ids", []).append(change_id)
            approval_candidates.append(
                {
                    "change_id": change_id,
                    "task_id": task_id,
                    "task_ref": task_refs.get(task_id, task_id),
                    "status": "ready",
                }
            )
        tasks_requiring_approval.append(task_id)

    if created_change_ids or tasks_requiring_approval:
        if owner_approval_enabled and not approval_note:
            result = CommandResult.failure(
                command="pipeline.change_gate",
                domain="pipeline",
                message="Owner-approved session Change approval requires an approval note.",
                errors=[
                    CommandMessage(
                        "PIPELINE_OWNER_APPROVAL_NOTE_REQUIRED",
                        "Provide --approval-note when owner-approved Change approval is enabled.",
                    )
                ],
            )
            result.data = {
                "required": True,
                "stop_code": "BLOCKED",
                **context_data(),
                "created_change_ids": created_change_ids,
                "linked_change_ids": linked_change_ids,
                "change_ids": linked_change_ids,
                "tasks_requiring_approval": tasks_requiring_approval,
                "workflows": workflows,
            }
            _merge_effects(result, effects)
            return result
        if owner_approval_enabled and unapprovable_changes:
            result = CommandResult.failure(
                command="pipeline.change_gate",
                domain="pipeline",
                message="Some linked Evolution Changes are not ready for owner session approval.",
                errors=[
                    CommandMessage(
                        "PIPELINE_CHANGE_NOT_SESSION_APPROVABLE",
                        "Only ready or proposed linked Changes can be approved by the session approval policy.",
                    )
                ],
            )
            result.data = {
                "required": True,
                "stop_code": "BLOCKED",
                **context_data(),
                "created_change_ids": created_change_ids,
                "linked_change_ids": linked_change_ids,
                "change_ids": linked_change_ids,
                "tasks_requiring_approval": tasks_requiring_approval,
                "unapprovable_changes": unapprovable_changes,
                "workflows": workflows,
            }
            _merge_effects(result, effects)
            return result
        if owner_approval_enabled and approval_candidates:
            approvals = _approve_session_changes(
                approval_candidates,
                approval_note=approval_note,
                session_id=session_id,
                root=root,
                actor=actor,
                python_executable=python_executable,
                runner=runner,
            )
            effects.extend(approvals["effects"])
            workflows.extend(approvals["workflows"])
            if approvals["failed_result"] is not None:
                failed = approvals["failed_result"]
                failed.data.update(
                    {
                        "required": True,
                        "stop_code": "BLOCKED",
                        **context_data(),
                        "created_change_ids": created_change_ids,
                        "linked_change_ids": linked_change_ids,
                        "change_ids": linked_change_ids,
                        "tasks_requiring_approval": tasks_requiring_approval,
                        "approved_change_ids": approvals["approved_change_ids"],
                        "approved_task_refs": approvals["approved_task_refs"],
                        "workflows": workflows,
                    }
                )
                _merge_effects(failed, effects)
                return failed
            approved_change_ids = approvals["approved_change_ids"]
            result = CommandResult.success(
                command="pipeline.change_gate",
                domain="pipeline",
                message=approval_message,
                data={
                    "required": True,
                    **context_data(),
                    "created_change_ids": created_change_ids,
                    "linked_change_ids": linked_change_ids,
                    "change_ids": linked_change_ids,
                    "tasks_requiring_approval": tasks_requiring_approval,
                    "approved_change_ids": approved_change_ids,
                    "approved_task_refs": approvals["approved_task_refs"],
                    "owner_approval": {
                        "actor": actor,
                        "approval_note": approval_note,
                        "session_id": session_id,
                    },
                    "workflows": workflows,
                    "state_changed": bool(created_change_ids or approved_change_ids),
                },
            )
            _merge_effects(result, effects)
            return result
        message = (
            "Evolution Changes were created and now require Human Owner approval."
            if created_change_ids
            else "Approved linked Evolution Changes are required before execution."
        )
        result = CommandResult.failure(
            command="pipeline.change_gate",
            domain="pipeline",
            message=message,
            errors=[
                CommandMessage(
                    "PIPELINE_CHANGE_APPROVAL_REQUIRED",
                    "Approve linked Changes before Codex execution.",
                )
            ],
        )
        result.data = {
            "required": True,
            "stop_code": "BLOCKED",
            **context_data(),
            "created_change_ids": created_change_ids,
            "linked_change_ids": linked_change_ids,
            "change_ids": linked_change_ids,
            "tasks_requiring_approval": tasks_requiring_approval,
            "workflows": workflows,
        }
        _merge_effects(result, effects)
        return result

    return CommandResult.success(
        command="pipeline.change_gate",
        domain="pipeline",
        message=pass_message,
        data={
            "required": True,
            **context_data(),
            "change_ids": linked_change_ids,
        },
    )


def _approve_session_changes(
    approval_candidates: Sequence[Mapping[str, str]],
    *,
    approval_note: str,
    session_id: str,
    root: Path,
    actor: str,
    python_executable: str,
    runner: Runner | None,
) -> dict[str, Any]:
    effects: list[CommandResult] = []
    workflows: list[dict[str, Any]] = []
    approved_change_ids: list[str] = []
    approved_task_refs: list[str] = []
    failed_result: CommandResult | None = None

    seen_changes: set[str] = set()
    for candidate in approval_candidates:
        change_id = str(candidate.get("change_id") or "")
        if not change_id or change_id in seen_changes:
            continue
        seen_changes.add(change_id)
        status = str(candidate.get("status") or "")
        task_ref = str(candidate.get("task_ref") or candidate.get("task_id") or "")

        if status == "proposed":
            for target_status in ("draft", "ready"):
                transition = _run_change_transition(
                    change_id,
                    target_status,
                    root=root,
                    actor=actor,
                    python_executable=python_executable,
                    runner=runner,
                )
                effects.append(transition)
                workflows.append(_workflow_summary(transition))
                if not transition.ok:
                    failed_result = CommandResult.failure(
                        command="pipeline.change_gate",
                        domain="pipeline",
                        message="Evolution Change preparation for approval failed.",
                        errors=list(transition.errors)
                        or [
                            CommandMessage(
                                "PIPELINE_CHANGE_PREPARE_FAILED",
                                "Could not move Change {} to {}.".format(
                                    change_id,
                                    target_status,
                                ),
                            )
                        ],
                    )
                    return {
                        "effects": effects,
                        "workflows": workflows,
                        "approved_change_ids": approved_change_ids,
                        "approved_task_refs": approved_task_refs,
                        "failed_result": failed_result,
                    }

        approve = run_workflow(
            "evolution.approve_change",
            change_ref=change_id,
            notes="{} (pipeline session {})".format(approval_note, session_id),
            root=root,
            actor=actor,
            confirmed=True,
            python_executable=python_executable,
            runner=runner,
        )
        effects.append(approve)
        workflows.append(_workflow_summary(approve))
        if not approve.ok:
            failed_result = CommandResult.failure(
                command="pipeline.change_gate",
                domain="pipeline",
                message="Owner-approved session Change approval workflow failed.",
                errors=list(approve.errors)
                or [
                    CommandMessage(
                        "PIPELINE_CHANGE_APPROVAL_FAILED",
                        "Could not approve Change {}.".format(change_id),
                    )
                ],
            )
            return {
                "effects": effects,
                "workflows": workflows,
                "approved_change_ids": approved_change_ids,
                "approved_task_refs": approved_task_refs,
                "failed_result": failed_result,
            }
        approved_change_ids.append(change_id)
        if task_ref:
            approved_task_refs.append(task_ref)

    return {
        "effects": effects,
        "workflows": workflows,
        "approved_change_ids": approved_change_ids,
        "approved_task_refs": approved_task_refs,
        "failed_result": failed_result,
    }


def _run_change_transition(
    change_id: str,
    target_status: str,
    *,
    root: Path,
    actor: str,
    python_executable: str,
    runner: Runner | None,
) -> CommandResult:
    argv = (
        python_executable,
        str(SCRIPTS_DIR / "evolutionctl.py"),
        "--root",
        str(root),
        "--actor",
        actor,
        "change",
        "transition",
        change_id,
        "--to",
        target_status,
    )
    executor = runner or _run_subprocess
    completed = executor(argv)
    if completed.returncode == 0:
        return CommandResult.success(
            command="evolutionctl.change.transition",
            domain="evolution",
            message=completed.stdout.strip() or "OK",
            data={
                "change_id": change_id,
                "status": target_status,
            },
        )
    return CommandResult.failure(
        command="evolutionctl.change.transition",
        domain="evolution",
        message="Evolution Change transition failed.",
        errors=[
            CommandMessage(
                "PIPELINE_CHANGE_TRANSITION_FAILED",
                "Could not move Change {} to {}.".format(change_id, target_status),
                details={
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                },
            )
        ],
    )


def _run_subprocess(argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(argv),
        cwd=str(SCRIPTS_DIR.parent),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _ensure_approved_change(
    task_id: str,
    policy: PipelinePolicy,
    evolution_state: Any,
    *,
    root: Path,
    actor: str,
    python_executable: str,
    runner: Runner | None,
) -> CommandResult:
    if not policy.evolution.require_approved_change_for_execution:
        return CommandResult.success(
            command="pipeline.change_gate",
            domain="pipeline",
            message="Approved Change gate is not required by policy.",
            data={"required": False},
        )

    linked = _linked_changes_for_task(task_id, evolution_state)
    approved = [
        change
        for change in linked
        if str(change.get("status") or "") in TERMINAL_CHANGE_STATUSES
    ]
    if approved:
        return CommandResult.success(
            command="pipeline.change_gate",
            domain="pipeline",
            message="Approved Change gate passed.",
            data={
                "required": True,
                "change_ids": [str(change.get("id")) for change in approved],
            },
        )

    if policy.evolution.create_missing_change:
        created = run_workflow(
            "evolution.create_for_task",
            task_ref=task_id,
            root=root,
            actor=actor,
            confirmed=True,
            python_executable=python_executable,
            runner=runner,
        )
        if created.ok:
            result = CommandResult.failure(
                command="pipeline.change_gate",
                domain="pipeline",
                message="Evolution Change was created and now requires Human Owner approval.",
                errors=[
                    CommandMessage(
                        "PIPELINE_CHANGE_APPROVAL_REQUIRED",
                        "Approve the created Change before Codex execution.",
                    )
                ],
            )
            result.data = {
                "required": True,
                "stop_code": "BLOCKED",
                "created_change_id": created.data.get("change_id", ""),
                "workflow": _workflow_summary(created),
            }
            result.changed_files.extend(created.changed_files)
            result.generated_files.extend(created.generated_files)
            result.events.extend(created.events)
            return result
        result = CommandResult.failure(
            command="pipeline.change_gate",
            domain="pipeline",
            message="Evolution Change creation workflow failed.",
            errors=list(created.errors)
            or [
                CommandMessage(
                    "PIPELINE_CHANGE_CREATE_FAILED",
                    "Could not create required Evolution Change.",
                )
            ],
        )
        result.data = {
            "required": True,
            "stop_code": "BLOCKED",
            "workflow": _workflow_summary(created),
        }
        return result

    result = CommandResult.failure(
        command="pipeline.change_gate",
        domain="pipeline",
        message="Approved linked Evolution Change is required before execution.",
        errors=[
            CommandMessage(
                "PIPELINE_APPROVED_CHANGE_REQUIRED",
                "Task {} has no linked approved Change.".format(task_id),
            )
        ],
    )
    result.data = {
        "required": True,
        "stop_code": "BLOCKED",
        "linked_change_ids": [str(change.get("id")) for change in linked],
    }
    return result


def _queue_task_ids(queue_preview: QueuePreview) -> tuple[str, ...]:
    task_ids: list[str] = []
    for item in (
        *queue_preview.executable,
        *queue_preview.waiting,
        *queue_preview.blocked,
    ):
        task_id = str(item.id or "")
        if task_id and task_id not in task_ids:
            task_ids.append(task_id)
    if not task_ids and queue_preview.next_task and queue_preview.next_task.id:
        task_ids.append(str(queue_preview.next_task.id))
    return tuple(task_ids)


def _queue_task_ref_map(queue_preview: QueuePreview) -> dict[str, str]:
    task_refs: dict[str, str] = {}
    for item in (
        *queue_preview.executable,
        *queue_preview.waiting,
        *queue_preview.blocked,
    ):
        task_id = str(item.id or "")
        if task_id:
            task_refs[task_id] = str(item.ref or item.selected_ref or task_id)
    if queue_preview.next_task and queue_preview.next_task.id:
        task_id = str(queue_preview.next_task.id)
        task_refs.setdefault(
            task_id,
            str(queue_preview.next_task.ref or queue_preview.next_task.selected_ref or task_id),
        )
    return task_refs


def _linked_changes_for_task(task_id: str, evolution_state: Any) -> list[Mapping[str, Any]]:
    if not isinstance(evolution_state, Mapping):
        return []
    linked: list[Mapping[str, Any]] = []
    for change in evolution_state.get("changes", []):
        if not isinstance(change, Mapping):
            continue
        linked_tasks = change.get("linked_tasks") or []
        if isinstance(linked_tasks, Sequence) and not isinstance(linked_tasks, (str, bytes)):
            if task_id in {str(item) for item in linked_tasks}:
                linked.append(change)
    return linked


def _record_stop(
    session_id: str,
    *,
    stop_code: str,
    stop_reason: str,
    result_status: str,
    gate_name: str,
    gate_status: str,
    gate_details: Mapping[str, Any],
    selected_task: QueuePreviewItem | None,
    policy_name: str,
    queue_preview: QueuePreview | None,
    side_effects: list[CommandResult],
    root: Path,
    actor: str,
    linked_change_ids: Sequence[str] = (),
    report_ids: Sequence[str] = (),
    review_ids: Sequence[str] = (),
    commit_ids: Sequence[str] = (),
) -> CommandResult:
    recorded = record_step_result(
        session_id,
        RUN_NEXT_STEP,
        result_status,
        root=root,
        actor=actor,
        task_id=str(selected_task.id or "") if selected_task else "",
        gate_name=gate_name,
        gate_status=gate_status,
        gate_details={
            **dict(gate_details),
            "stop_code": stop_code,
            "stop_reason": stop_reason,
        },
        stop_reason="{}: {}".format(stop_code, stop_reason),
        linked_change_ids=linked_change_ids,
        report_ids=report_ids,
        review_ids=review_ids,
        commit_ids=commit_ids,
    )
    side_effects.append(recorded)
    if not recorded.ok:
        return _aggregate_failure(
            "pipeline.run_next",
            "Failed to record pipeline run-next result.",
            session_id,
            side_effects,
        )
    return _safe_stop_result(
        session_id=session_id,
        stop_code=stop_code,
        stop_reason=stop_reason,
        selected_task=selected_task,
        policy_name=policy_name,
        queue_preview=queue_preview,
        side_effects=side_effects,
    )


def _safe_stop_result(
    *,
    session_id: str,
    stop_code: str,
    stop_reason: str,
    selected_task: QueuePreviewItem | None,
    policy_name: str,
    queue_preview: QueuePreview | None,
    side_effects: Sequence[CommandResult],
) -> CommandResult:
    result = CommandResult.success(
        command="pipeline.run_next",
        domain="pipeline",
        message="{}: {}".format(stop_code, stop_reason),
        data={
            "session_id": session_id,
            "stop_code": stop_code,
            "stop_reason": stop_reason,
            "policy": policy_name,
            "selected_task": selected_task.to_dict() if selected_task else None,
            "queue_counts": _queue_counts(queue_preview),
            "side_effects": [effect.to_dict() for effect in side_effects],
        },
    )
    _merge_effects(result, side_effects)
    if stop_code in {
        "NOT_IMPLEMENTED",
        "BLOCKED",
        "TOKEN_BUDGET_FAILURE",
        "CODEX_REPORT_GATE_FAILURE",
        "MACHINE_REVIEW_FAILURE",
        "CODEX_REVIEW_GATE_FAILURE",
        "CODEX_REVIEW_REQUEST_CHANGES",
        "CODEX_REVIEW_BLOCKED",
        "REVIEW_CLOSE_POLICY_BLOCKED",
        "REVIEW_CLOSE_WORKFLOW_FAILED",
        "REWORK_LIMIT_REACHED",
        "REWORK_POLICY_DISABLED",
        "COMMIT_READINESS_FAILED",
        "COMMIT_GIT_COMMAND_FAILED",
    }:
        result.owner_action_required = stop_reason
    return result


def _aggregate_failure(
    command: str,
    message: str,
    session_id: str,
    side_effects: Sequence[CommandResult],
) -> CommandResult:
    errors: list[CommandMessage] = []
    for effect in side_effects:
        errors.extend(effect.errors)
    result = CommandResult.failure(
        command=command,
        domain="pipeline",
        message=message,
        errors=errors
        or [
            CommandMessage(
                "PIPELINE_RUN_NEXT_FAILED",
                message,
                details={"session_id": session_id},
            )
        ],
    )
    result.data = {
        "session_id": session_id,
        "side_effects": [effect.to_dict() for effect in side_effects],
    }
    _merge_effects(result, side_effects)
    return result


def _merge_effects(target: CommandResult, effects: Sequence[CommandResult]) -> None:
    for effect in effects:
        _extend_unique(target.changed_files, effect.changed_files)
        _extend_unique(target.generated_files, effect.generated_files)
        _extend_unique(target.events, effect.events)
        target.warnings.extend(effect.warnings)


def _gate_details(
    policy_name: str,
    queue_preview: QueuePreview,
    selected_task: QueuePreviewItem | None,
    *,
    change_gate: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    data = {
        "policy": policy_name,
        "selected_task": selected_task.to_dict() if selected_task else None,
        "queue_counts": _queue_counts(queue_preview),
    }
    if change_gate:
        data["change_gate"] = dict(change_gate)
    return data


def _queue_counts(queue_preview: QueuePreview | None) -> dict[str, int]:
    if queue_preview is None:
        return {}
    return {
        "executable": len(queue_preview.executable),
        "waiting": len(queue_preview.waiting),
        "blocked": len(queue_preview.blocked),
        "skipped": len(queue_preview.skipped),
    }


def _workflow_summary(result: CommandResult) -> dict[str, Any]:
    steps = result.data.get("steps") if isinstance(result.data, Mapping) else []
    steps = steps or []
    return {
        "ok": result.ok,
        "message": result.message,
        "steps": [
            {
                "id": str(step.get("id") or ""),
                "status": str(step.get("status") or ""),
            }
            for step in steps
            if isinstance(step, Mapping)
        ],
        "errors": [error.to_dict() for error in result.errors],
    }


def _load_plan(root: Path) -> Mapping[str, Any] | None:
    path = root / "AI_PROJECT" / "state" / "plan.json"
    if not path.exists():
        return None
    data = read_json_file(path, missing_code="PLAN_NOT_INITIALIZED")
    return data if isinstance(data, Mapping) else None


def _task_by_id(tasks_state: Mapping[str, Any], task_id: str) -> Mapping[str, Any]:
    for task in tasks_state.get("tasks", []):
        if isinstance(task, Mapping) and task.get("id") == task_id:
            return task
    return {"id": task_id}


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    raise TypeError("{} must be a mapping".format(name))


def _string_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    return tuple(str(item) for item in value if str(item).strip())


def _optional_int(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _policy_name(session: Mapping[str, Any]) -> str:
    snapshot = session.get("policy_snapshot")
    if isinstance(snapshot, Mapping):
        return str(snapshot.get("name") or "")
    return ""


def _adapter_gate_status(result: CodexAdapterResult) -> str:
    if result.status == "passed":
        return "pass"
    if result.status == "failed":
        return "fail"
    return "blocked"


def _adapter_step_status(result: CodexAdapterResult) -> str:
    return "failed" if result.status == "failed" else "blocked"


def _adapter_stop_code(result: CodexAdapterResult) -> str:
    return "UNSAFE_CONDITION" if result.status == "failed" else "BLOCKED"


def _extend_unique(target: list[str], values: Sequence[str]) -> None:
    seen = set(target)
    for value in values:
        text = str(value)
        if text and text not in seen:
            target.append(text)
            seen.add(text)

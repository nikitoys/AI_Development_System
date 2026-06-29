"""Supervised batch runner for pipeline sessions.

The batch runner composes the existing one-step runner. It does not add new
gate behavior; it repeats ``run_next`` until the selected queue completes,
the policy limit is reached, or the first blocker/failure appears.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from ai_project_ctl.core.result import CommandMessage, CommandResult
from ai_project_ctl.core.workflows import Runner

from .git_status import GitStatusError, capture_git_status_snapshot
from .policy import PipelinePolicy
from .queue import QueuePlannerRequest, QueuePreview, QueuePreviewItem, preview_queue
from .runner import run_next
from .session import stop_session, successful_committed_close_status
from .state import load_pipeline_state, load_reference_state


CONTINUE_CODES = {"TASK_AUTO_CLOSED", "LOCAL_COMMIT_CREATED"}
CONTINUE_PHASE_STATUSES = {"passed", "skipped"}
STOP_PHASE_STATUSES = {"blocked", "failed"}
POST_TASK_DIRTY_WORKTREE = "POST_TASK_DIRTY_WORKTREE"
POST_TASK_WORKTREE_STATUS_UNAVAILABLE = "POST_TASK_WORKTREE_STATUS_UNAVAILABLE"


def run_until_blocker(
    session_id: str = "",
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    confirmed: bool = False,
    python_executable: str | None = None,
    runner: Runner | None = None,
    codex_adapter=None,
    codex_reviewer=None,
) -> CommandResult:
    """Run one session until completion, limit, or first blocker."""

    root_path = Path(root).resolve()
    if not confirmed:
        result = CommandResult.failure(
            command="pipeline.run_until_blocker",
            domain="pipeline",
            message="Pipeline batch runner requires explicit confirmation.",
            errors=[
                CommandMessage(
                    "PIPELINE_BATCH_CONFIRMATION_REQUIRED",
                    "Rerun with --confirm after reviewing the selected session and policy.",
                )
            ],
        )
        result.data = {"session_id": session_id or _current_session_id(root_path)}
        result.owner_action_required = "Review the pipeline session and rerun with --confirm."
        return result

    selected = _load_session(root_path, session_id)
    if not selected.ok:
        return selected

    selected_session_id = str(selected.data["session"]["id"])
    try:
        policy = _session_policy(selected.data["session"])
    except ValueError as exc:
        return CommandResult.failure(
            command="pipeline.run_until_blocker",
            domain="pipeline",
            message="Pipeline session has an invalid policy snapshot.",
            errors=[CommandMessage("PIPELINE_INVALID_POLICY_SNAPSHOT", str(exc))],
        )
    summary = _initial_summary(selected_session_id, policy, selected.data["session"])
    effects: list[CommandResult] = []
    failures = 0

    while True:
        session = _find_session(root_path, selected_session_id)
        if session is None:
            return _failure(
                selected_session_id,
                summary,
                effects,
                "PIPELINE_SESSION_NOT_FOUND",
                "Pipeline session disappeared during batch run.",
            )

        if str(session.get("status") or "") == "completed":
            return _success(
                selected_session_id,
                "QUEUE_COMPLETE",
                "Selected queue completed.",
                summary,
                effects,
                session=session,
                owner_action_required="Review the completed pipeline session.",
            )

        committed_close = successful_committed_close_status(session)
        if committed_close:
            _merge_committed_close_into_summary(summary, session, committed_close)
            _merge_session_lists(summary, session, root_path)
            if _committed_close_finishes_selected_queue(
                summary,
                session,
                policy,
                root_path,
            ):
                completed_session = _committed_close_completion_view(
                    session,
                    committed_close,
                )
                return _success(
                    selected_session_id,
                    "QUEUE_COMPLETE",
                    "Committed close completed the selected pipeline session.",
                    summary,
                    effects,
                    session=completed_session,
                    owner_action_required=(
                        committed_close.get("owner_next_action")
                        or "Review the completed pipeline session."
                    ),
                )
            if _latest_phase_name(session) == "close":
                handoff_blocker = _post_task_worktree_handoff_blocker(
                    root=root_path,
                    runner=runner,
                    completed_task_id=str(
                        committed_close.get("task_id")
                        or session.get("current_task_id")
                        or ""
                    ),
                    commit_hash=str(committed_close.get("commit_hash") or ""),
                )
                if handoff_blocker:
                    return _post_task_worktree_stop(
                        selected_session_id,
                        summary,
                        effects,
                        handoff_blocker,
                        root=root_path,
                        actor=actor,
                        session=session,
                    )

        if _attempt_count(session) >= policy.batch.max_steps:
            stopped = stop_session(
                selected_session_id,
                "MAX_STEPS_REACHED: Batch runner reached max_steps {}.".format(
                    policy.batch.max_steps
                ),
                root=root_path,
                actor=actor,
                status="stopped",
            )
            effects.append(stopped)
            _merge_effects_into_summary(summary, stopped)
            return _success(
                selected_session_id,
                "MAX_STEPS_REACHED",
                "Batch runner reached max_steps {}.".format(policy.batch.max_steps),
                summary,
                effects,
                session=_find_session(root_path, selected_session_id) or session,
                owner_action_required="Inspect the session before resuming with a new run.",
            )

        if _failure_count(session) >= policy.batch.max_failures:
            summary["failures"] = _failure_count(session)
            stopped = stop_session(
                selected_session_id,
                "MAX_FAILURES_REACHED: Batch runner reached max_failures {}.".format(
                    policy.batch.max_failures
                ),
                root=root_path,
                actor=actor,
                status="stopped",
            )
            effects.append(stopped)
            _merge_effects_into_summary(summary, stopped)
            return _success(
                selected_session_id,
                "MAX_FAILURES_REACHED",
                "Batch runner reached max_failures {}.".format(
                    policy.batch.max_failures
                ),
                summary,
                effects,
                session=_find_session(root_path, selected_session_id) or session,
                owner_action_required=(
                    "Inspect failed pipeline phase attempts before resuming."
                ),
            )

        step = run_next(
            selected_session_id,
            root=root_path,
            actor=actor,
            python_executable=python_executable or sys.executable,
            runner=runner,
            codex_adapter=codex_adapter,
            codex_reviewer=codex_reviewer,
        )
        effects.append(step)
        summary["steps_run"] += 1
        summary["step_results"].append(_step_summary(step))
        _merge_effects_into_summary(summary, step)

        session = _find_session(root_path, selected_session_id) or session
        _merge_session_lists(summary, session, root_path)

        phase_result = _phase_result(step)
        phase_status = _phase_status(step, phase_result)
        if phase_status in STOP_PHASE_STATUSES:
            if phase_status == "failed":
                failures = max(failures + 1, _failure_count(session))
                summary["failures"] = failures
            summary["blockers"].append(_phase_blocker(step, phase_result))
            return _success(
                selected_session_id,
                _phase_stop_code(step, phase_result),
                _phase_stop_reason(step, phase_result),
                summary,
                effects,
                session=session,
                owner_action_required=_phase_owner_action_required(step, phase_result),
            )

        if not step.ok:
            failures += 1
            summary["failures"] = failures
            return _failure(
                selected_session_id,
                summary,
                effects,
                "PIPELINE_BATCH_STEP_FAILED",
                "Batch runner stopped after a run-next command failure.",
            )

        if str(session.get("status") or "") == "completed":
            return _success(
                selected_session_id,
                "QUEUE_COMPLETE",
                "Selected queue completed.",
                summary,
                effects,
                session=session,
                owner_action_required="Review the completed pipeline session.",
            )

        if phase_status in CONTINUE_PHASE_STATUSES:
            selected_task = _selected_task_id(step)
            if _phase_name(phase_result) == "close" and selected_task:
                if selected_task not in summary["completed_tasks"]:
                    summary["completed_tasks"].append(selected_task)
                if selected_task not in summary["changed_tasks"]:
                    summary["changed_tasks"].append(selected_task)
            continue

        stop_code = str(step.data.get("stop_code") or "")
        selected_task = _selected_task_id(step)
        if stop_code in CONTINUE_CODES:
            if selected_task and selected_task not in summary["completed_tasks"]:
                summary["completed_tasks"].append(selected_task)
            if selected_task and selected_task not in summary["changed_tasks"]:
                summary["changed_tasks"].append(selected_task)
            if (
                stop_code == "LOCAL_COMMIT_CREATED"
                and not _committed_close_finishes_selected_queue(
                    summary,
                    session,
                    policy,
                    root_path,
                )
            ):
                handoff_blocker = _post_task_worktree_handoff_blocker(
                    root=root_path,
                    runner=runner,
                    completed_task_id=selected_task,
                    commit_hash=str(
                        step.data.get("commit_hash")
                        or summary.get("commit_hash")
                        or ""
                    ),
                )
                if handoff_blocker:
                    return _post_task_worktree_stop(
                        selected_session_id,
                        summary,
                        effects,
                        handoff_blocker,
                        root=root_path,
                        actor=actor,
                        session=session,
                    )
            continue

        if stop_code == "CODEX_REVIEW_REQUEST_CHANGES" and selected_task:
            summary["requested_changes"].append(selected_task)
            if selected_task not in summary["changed_tasks"]:
                summary["changed_tasks"].append(selected_task)

        if stop_code:
            summary["blockers"].append(
                {
                    "code": stop_code,
                    "reason": step.data.get("stop_reason") or step.message,
                    "task_id": selected_task,
                }
            )
        return _success(
            selected_session_id,
            stop_code or "BLOCKED",
            str(step.data.get("stop_reason") or step.message),
            summary,
            effects,
            session=session,
            owner_action_required=step.owner_action_required
            or str(step.data.get("stop_reason") or step.message),
        )


def _current_session_id(root: Path) -> str:
    state = load_pipeline_state(root)
    return str(state.get("current_session_id") or "")


def _load_session(root: Path, session_id: str) -> CommandResult:
    selected_id = session_id or _current_session_id(root)
    if not selected_id:
        return CommandResult.failure(
            command="pipeline.run_until_blocker",
            domain="pipeline",
            message="No pipeline session selected.",
            errors=[
                CommandMessage(
                    "PIPELINE_NO_SESSION_SELECTED",
                    "Pass a session id or create a current pipeline session first.",
                )
            ],
        )
    session = _find_session(root, selected_id)
    if session is None:
        return CommandResult.failure(
            command="pipeline.run_until_blocker",
            domain="pipeline",
            message="Pipeline session not found.",
            errors=[
                CommandMessage(
                    "PIPELINE_SESSION_NOT_FOUND",
                    "pipeline session not found: {}".format(selected_id),
                )
            ],
        )
    return CommandResult.success(
        command="pipeline.run_until_blocker",
        domain="pipeline",
        message="Pipeline session loaded.",
        data={"session": session},
    )


def _find_session(root: Path, session_id: str) -> dict[str, Any] | None:
    state = load_pipeline_state(root)
    for session in state.get("sessions", []):
        if isinstance(session, Mapping) and session.get("id") == session_id:
            return dict(session)
    return None


def _session_policy(session: Mapping[str, Any]) -> PipelinePolicy:
    value = session.get("policy_snapshot")
    if not isinstance(value, Mapping):
        raise ValueError("Pipeline session policy_snapshot is missing or invalid.")
    return PipelinePolicy.from_dict(value)


def _initial_summary(
    session_id: str,
    policy: PipelinePolicy,
    session: Mapping[str, Any],
) -> dict[str, Any]:
    selected_queue = session.get("selected_queue") if isinstance(session.get("selected_queue"), Mapping) else {}
    return {
        "session_id": session_id,
        "policy": policy.name,
        "limits": {
            "max_steps": policy.batch.max_steps,
            "max_failures": policy.batch.max_failures,
            "max_tasks": selected_queue.get("max_tasks") or policy.queue.max_tasks,
            "max_rework_attempts": policy.rework.max_rework_attempts,
        },
        "steps_run": 0,
        "failures": 0,
        "completed_tasks": [],
        "changed_tasks": [],
        "requested_changes": [],
        "accepted_changes": [],
        "commits": [],
        "blockers": [],
        "step_results": [],
        "changed_files": [],
        "generated_files": [],
        "events": [],
    }


def _step_count(session: Mapping[str, Any]) -> int:
    counters = session.get("attempt_counters")
    if isinstance(counters, Mapping):
        try:
            return int(counters.get("steps", 0))
        except (TypeError, ValueError):
            return 0
    return 0


def _attempt_count(session: Mapping[str, Any]) -> int:
    return max(_step_count(session), len(_phase_history(session)))


def _failure_count(session: Mapping[str, Any]) -> int:
    phase_failures = sum(
        1
        for item in _phase_history(session)
        if str(item.get("status") or "") == "failed"
    )
    step_failures = sum(
        1
        for item in _step_history(session)
        if str(item.get("status") or "") == "failed"
    )
    return max(
        phase_failures,
        step_failures,
    )


def _phase_history(session: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    history = session.get("phase_history")
    if not isinstance(history, Sequence) or isinstance(history, (str, bytes)):
        return []
    return [item for item in history if isinstance(item, Mapping)]


def _step_history(session: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    history = session.get("steps")
    if not isinstance(history, Sequence) or isinstance(history, (str, bytes)):
        return []
    return [item for item in history if isinstance(item, Mapping)]


def _selected_task_id(result: CommandResult) -> str:
    selected = result.data.get("selected_task")
    if isinstance(selected, Mapping):
        return str(selected.get("id") or "")
    phase_result = _phase_result(result)
    artifacts = phase_result.get("artifacts")
    if isinstance(artifacts, Mapping):
        for key in ("selected_task", "next_task"):
            selected = artifacts.get(key)
            if isinstance(selected, Mapping):
                return str(selected.get("id") or "")
        task_id = str(artifacts.get("task_id") or "")
        if task_id:
            return task_id
    return ""


def _step_summary(result: CommandResult) -> dict[str, Any]:
    phase_result = _phase_result(result)
    return {
        "ok": result.ok,
        "stop_code": result.data.get("stop_code"),
        "stop_reason": result.data.get("stop_reason"),
        "dispatched_phase": result.data.get("dispatched_phase")
        or phase_result.get("phase"),
        "phase_status": result.data.get("phase_status")
        or phase_result.get("status"),
        "next_action": result.data.get("next_action")
        or phase_result.get("next_action"),
        "selected_task": result.data.get("selected_task"),
        "queue_counts": result.data.get("queue_counts"),
    }


def _phase_result(result: CommandResult) -> dict[str, Any]:
    raw = result.data.get("phase_result")
    return dict(raw) if isinstance(raw, Mapping) else {}


def _phase_name(phase_result: Mapping[str, Any]) -> str:
    return str(phase_result.get("phase") or "")


def _latest_phase_name(session: Mapping[str, Any]) -> str:
    history = _phase_history(session)
    if not history:
        return ""
    return str(history[-1].get("phase") or "")


def _phase_status(
    result: CommandResult,
    phase_result: Mapping[str, Any],
) -> str:
    return str(result.data.get("phase_status") or phase_result.get("status") or "")


def _phase_stop_code(
    result: CommandResult,
    phase_result: Mapping[str, Any],
) -> str:
    stop_code = str(result.data.get("stop_code") or "")
    if stop_code:
        return stop_code
    artifacts = phase_result.get("artifacts")
    blocked_by = ""
    if isinstance(artifacts, Mapping):
        blocked_by = str(artifacts.get("blocked_by") or "")
    blocked_by = str(phase_result.get("blocked_by") or blocked_by)
    status = str(phase_result.get("status") or "")
    if status == "blocked":
        return blocked_by or "PIPELINE_PHASE_BLOCKED"
    if status == "failed":
        return blocked_by or "PIPELINE_PHASE_FAILED"
    return "PIPELINE_PHASE_STOPPED"


def _phase_stop_reason(
    result: CommandResult,
    phase_result: Mapping[str, Any],
) -> str:
    return str(
        phase_result.get("reason")
        or result.data.get("stop_reason")
        or result.message
        or "Pipeline phase stopped the batch runner."
    )


def _phase_owner_action_required(
    result: CommandResult,
    phase_result: Mapping[str, Any],
) -> str:
    return str(
        phase_result.get("next_action")
        or result.data.get("next_action")
        or result.owner_action_required
        or _phase_stop_reason(result, phase_result)
    )


def _phase_blocker(
    result: CommandResult,
    phase_result: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "code": _phase_stop_code(result, phase_result),
        "reason": _phase_stop_reason(result, phase_result),
        "task_id": _selected_task_id(result),
        "phase": _phase_name(phase_result),
        "status": str(phase_result.get("status") or ""),
        "next_action": str(
            phase_result.get("next_action") or result.data.get("next_action") or ""
        ),
    }


def _merge_effects_into_summary(summary: dict[str, Any], result: CommandResult) -> None:
    _extend_unique(summary["changed_files"], result.changed_files)
    _extend_unique(summary["generated_files"], result.generated_files)
    _extend_unique(summary["events"], result.events)


def _merge_session_lists(
    summary: dict[str, Any],
    session: Mapping[str, Any],
    root: Path,
) -> None:
    task_ids = [
        *summary["completed_tasks"],
        *summary["changed_tasks"],
        str(session.get("current_task_id") or ""),
    ]
    _extend_unique(summary["accepted_changes"], _accepted_change_ids(session, root, task_ids))
    _extend_unique(summary["commits"], _string_list(session.get("commit_ids")))


def _accepted_change_ids(
    session: Mapping[str, Any],
    root: Path,
    task_ids: Sequence[str],
) -> list[str]:
    linked = set(_string_list(session.get("linked_change_ids")))
    tasks = {str(task_id) for task_id in task_ids if str(task_id)}
    evolution = load_reference_state(root).get("evolution")
    if not isinstance(evolution, Mapping):
        return []
    accepted: list[str] = []
    for change in evolution.get("changes", []):
        if not isinstance(change, Mapping):
            continue
        change_id = str(change.get("id") or "")
        linked_tasks = set(_string_list(change.get("linked_tasks")))
        if (
            change_id
            and str(change.get("status") or "") == "accepted"
            and (change_id in linked or bool(tasks & linked_tasks))
        ):
            accepted.append(change_id)
    return accepted


def _merge_committed_close_into_summary(
    summary: dict[str, Any],
    session: Mapping[str, Any],
    close_status: Mapping[str, Any],
) -> None:
    task_id = str(close_status.get("task_id") or session.get("current_task_id") or "")
    if task_id and task_id not in summary["completed_tasks"]:
        summary["completed_tasks"].append(task_id)
    if task_id and task_id not in summary["changed_tasks"]:
        summary["changed_tasks"].append(task_id)

    commit_hash = str(close_status.get("commit_hash") or "").strip()
    if commit_hash:
        _extend_unique(summary["commits"], [commit_hash])

    summary["close_status"] = dict(close_status)
    summary["close_outcome"] = str(close_status.get("outcome") or "")
    summary["commit_status"] = str(close_status.get("commit_status") or "")
    summary["commit_code"] = str(close_status.get("commit_code") or "")
    summary["commit_hash"] = commit_hash


def _committed_close_finishes_selected_queue(
    summary: Mapping[str, Any],
    session: Mapping[str, Any],
    policy: PipelinePolicy,
    root: Path,
) -> bool:
    max_tasks = _selected_max_tasks(session, policy)
    completed_tasks = {
        str(task_id)
        for task_id in summary.get("completed_tasks", [])
        if str(task_id)
    }
    if len(completed_tasks) >= max_tasks:
        return True

    queue_preview = _preview_committed_close_queue(session, policy, root)
    if queue_preview is None:
        return False

    for item in queue_preview.items:
        task_id = str(item.id or "")
        if task_id in completed_tasks:
            continue
        if _queue_item_keeps_session_open(item):
            return False
    return True


def _preview_committed_close_queue(
    session: Mapping[str, Any],
    policy: PipelinePolicy,
    root: Path,
) -> QueuePreview | None:
    refs = load_reference_state(root)
    tasks_state = refs.get("tasks")
    if not isinstance(tasks_state, Mapping):
        return None
    plan = refs.get("plan")
    selected_queue = (
        session.get("selected_queue")
        if isinstance(session.get("selected_queue"), Mapping)
        else {}
    )
    try:
        return preview_queue(
            tasks_state,
            plan if isinstance(plan, Mapping) else None,
            policy=policy,
            request=QueuePlannerRequest(
                task_refs=tuple(_string_list(selected_queue.get("task_refs"))),
                epic_ids=tuple(_string_list(selected_queue.get("epic_ids"))),
                statuses=tuple(_string_list(selected_queue.get("statuses"))),
                max_tasks=_optional_int(selected_queue.get("max_tasks")),
                order_by=str(selected_queue.get("order_by") or "execution"),
            ),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _queue_item_keeps_session_open(item: QueuePreviewItem) -> bool:
    if item.executable or item.category in {"waiting", "blocked"}:
        return True
    reason_codes = {
        str(reason.get("code") or "")
        for reason in item.reasons
        if isinstance(reason, Mapping)
    }
    if "policy_max_tasks_exceeded" in reason_codes:
        return False
    if (
        "status_not_executable" in reason_codes
        and str(item.status or "") in {"done", "deferred", "archived"}
    ):
        return False
    return bool(item.id or reason_codes)


def _selected_max_tasks(session: Mapping[str, Any], policy: PipelinePolicy) -> int:
    selected_queue = (
        session.get("selected_queue")
        if isinstance(session.get("selected_queue"), Mapping)
        else {}
    )
    return _optional_int(selected_queue.get("max_tasks")) or policy.queue.max_tasks


def _optional_int(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _committed_close_completion_reason(close_status: Mapping[str, Any]) -> str:
    commit_hash = str(close_status.get("commit_hash") or "").strip()
    if commit_hash:
        return "Close passed and local commit {} was created.".format(commit_hash)
    return "Close passed and a local commit was created."


def _committed_close_completion_view(
    session: Mapping[str, Any],
    close_status: Mapping[str, Any],
) -> dict[str, Any]:
    completed = dict(session)
    completed["status"] = "completed"
    completed["stop_reason"] = _committed_close_completion_reason(close_status)
    if not completed.get("current_step"):
        completed["current_step_status"] = "passed"
    return completed


def _post_task_worktree_handoff_blocker(
    *,
    root: Path,
    runner: Runner | None,
    completed_task_id: str,
    commit_hash: str,
) -> dict[str, Any]:
    try:
        snapshot = capture_git_status_snapshot(root=root, runner=runner)
    except GitStatusError as exc:
        return {
            "code": POST_TASK_WORKTREE_STATUS_UNAVAILABLE,
            "reason": (
                "Post-task git status could not be captured after committed "
                "task {}.".format(completed_task_id or "unknown")
            ),
            "task_id": completed_task_id,
            "completed_task_id": completed_task_id,
            "commit_hash": commit_hash,
            "dirty_paths": [],
            "error": str(exc),
        }

    dirty_paths = list(snapshot.dirty_paths)
    if not dirty_paths:
        return {}

    return {
        "code": POST_TASK_DIRTY_WORKTREE,
        "reason": (
            "Committed task {} left a dirty worktree after local commit."
        ).format(completed_task_id or "unknown"),
        "task_id": completed_task_id,
        "completed_task_id": completed_task_id,
        "commit_hash": commit_hash,
        "dirty_paths": dirty_paths,
        "git_status": snapshot.to_dict(),
    }


def _post_task_worktree_stop(
    session_id: str,
    summary: dict[str, Any],
    effects: list[CommandResult],
    blocker: Mapping[str, Any],
    *,
    root: Path,
    actor: str,
    session: Mapping[str, Any],
) -> CommandResult:
    summary["blockers"].append(dict(blocker))
    summary["completed_task_id"] = blocker.get("completed_task_id") or ""
    summary["dirty_paths"] = list(blocker.get("dirty_paths") or [])
    summary["post_task_handoff"] = dict(blocker)
    code = str(blocker.get("code") or POST_TASK_DIRTY_WORKTREE)
    reason = str(blocker.get("reason") or "Post-task worktree handoff blocked.")
    stopped = stop_session(
        session_id,
        "{}: {}".format(code, reason),
        root=root,
        actor=actor,
        status="stopped",
    )
    effects.append(stopped)
    _merge_effects_into_summary(summary, stopped)
    stopped_session = _find_session(root, session_id) or dict(session)
    return _success(
        session_id,
        code,
        reason,
        summary,
        effects,
        session=stopped_session,
        owner_action_required="Inspect the post-task worktree before resuming the batch.",
    )


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item) for item in value if str(item)]


def _success(
    session_id: str,
    stop_code: str,
    stop_reason: str,
    summary: Mapping[str, Any],
    effects: Sequence[CommandResult],
    *,
    session: Mapping[str, Any],
    owner_action_required: str,
) -> CommandResult:
    data = {
        **dict(summary),
        "session_id": session_id,
        "stop_code": stop_code,
        "stop_reason": stop_reason,
        "session_status": session.get("status"),
        "current_task_id": session.get("current_task_id"),
        "current_step": session.get("current_step"),
        "current_step_status": session.get("current_step_status"),
        "side_effects": [effect.to_dict() for effect in effects],
    }
    result = CommandResult.success(
        command="pipeline.run_until_blocker",
        domain="pipeline",
        message="{}: {}".format(stop_code, stop_reason),
        data=data,
    )
    result.owner_action_required = owner_action_required
    _merge_effects(result, effects)
    return result


def _failure(
    session_id: str,
    summary: Mapping[str, Any],
    effects: Sequence[CommandResult],
    code: str,
    message: str,
) -> CommandResult:
    errors: list[CommandMessage] = []
    for effect in effects:
        errors.extend(effect.errors)
    if not errors:
        errors.append(CommandMessage(code, message))
    result = CommandResult.failure(
        command="pipeline.run_until_blocker",
        domain="pipeline",
        message=message,
        errors=errors,
    )
    result.data = {
        **dict(summary),
        "session_id": session_id,
        "stop_code": code,
        "stop_reason": message,
        "side_effects": [effect.to_dict() for effect in effects],
    }
    result.owner_action_required = message
    _merge_effects(result, effects)
    return result


def _merge_effects(target: CommandResult, effects: Sequence[CommandResult]) -> None:
    for effect in effects:
        _extend_unique(target.changed_files, effect.changed_files)
        _extend_unique(target.generated_files, effect.generated_files)
        _extend_unique(target.events, effect.events)
        target.warnings.extend(effect.warnings)


def _extend_unique(target: list[str], values: Sequence[str]) -> None:
    seen = set(target)
    for value in values:
        text = str(value)
        if text and text not in seen:
            target.append(text)
            seen.add(text)

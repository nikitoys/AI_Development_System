"""Pipeline prepare phase service.

The prepare phase resolves one selected task, checks its Evolution Change gate,
and delegates context/prompt setup to the existing prepare-for-Codex workflow.
It intentionally stops before any Codex execution adapter or downstream gates.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from ai_project_ctl.core.paths import ProjectPaths
from ai_project_ctl.core.result import CommandMessage, CommandResult
from ai_project_ctl.core.store import StoreError, read_json_file
from ai_project_ctl.core.workflows import Runner, run_workflow

from .phase import PhaseResult
from .policy import PipelinePolicy
from .queue import QueuePlannerRequest, QueuePreview, QueuePreviewItem, preview_queue
from .runner import _ensure_approved_change_for_selected_task
from .session import record_phase_result
from .state import load_pipeline_state, load_reference_state, pipeline_state_path


COMMAND_NAME = "pipeline.phase.prepare"
PHASE_NAME = "prepare"
PREPARE_WORKFLOW = "task.prepare_for_codex"
NO_EXECUTABLE_TASK = "NO_EXECUTABLE_TASK"
PREPARABLE_STATUSES = {
    "planned",
    "ready",
    "in_progress",
    "blocked",
    "in_review",
    "changes_requested",
}
PREPARABLE_REASON_CODES = {"status_not_executable"}
CODEX_READY = "CODEX_READY"
READY_STATUS = "ready"


def prepare_phase(
    session_id: str = "",
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    python_executable: str | None = None,
    runner: Runner | None = None,
    task_refs: Sequence[str] = (),
    epic_ids: Sequence[str] = (),
    statuses: Sequence[str] = (),
    max_tasks: int | None = None,
    order_by: str = "execution",
) -> CommandResult:
    """Prepare the selected pipeline task without invoking Codex execution."""

    root_path = Path(root).resolve()
    python_bin = python_executable or sys.executable

    refs = load_reference_state(root_path)
    tasks_state = refs.get("tasks")
    if not isinstance(tasks_state, Mapping):
        return _failure(
            "PIPELINE_TASKS_STATE_NOT_FOUND",
            "Task state is required to prepare a pipeline task.",
            details={
                "state_path": str(
                    ProjectPaths.from_root(root_path).state_file("tasks.json")
                )
            },
        )

    try:
        selection = _resolve_selection(
            root_path,
            session_id,
            tasks_state,
            task_refs=task_refs,
            epic_ids=epic_ids,
            statuses=statuses,
            max_tasks=max_tasks,
            order_by=order_by,
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _failure(
            "PIPELINE_PREPARE_SELECTION_FAILED",
            "Could not resolve selected task safely: {}".format(exc),
        )

    if not selection.ok:
        return selection

    data = selection.data
    queue_preview = data["queue_preview"]
    policy = data["policy"]
    session = data.get("session") if isinstance(data.get("session"), Mapping) else {}
    selected = _selected_prepare_task(
        queue_preview,
        allow_status_fallback=bool(data.get("allow_preparable_fallback")),
    )
    selected_session_id = str(session.get("id") or "")
    source = str(data.get("source") or "")

    if selected is None:
        phase = PhaseResult.blocked(
            PHASE_NAME,
            reason="No executable task is available in the selected queue.",
            next_action="Create or unblock a ready task, then rerun prepare.",
            artifacts={
                "blocked_by": NO_EXECUTABLE_TASK,
                "source": source,
                "session_id": selected_session_id,
                "queue_counts": _queue_counts(queue_preview),
                "queue_preview": queue_preview.to_dict(),
                "allow_preparable_fallback": bool(
                    data.get("allow_preparable_fallback")
                ),
            },
        )
        return _phase_command(
            phase,
            message=phase.reason,
            data={
                "session_id": selected_session_id,
                "queue_source": source,
                "queue_preview": queue_preview.to_dict(),
            },
        )

    task_id = str(selected.id or "")
    if not task_id:
        return _failure(
            "PIPELINE_SELECTED_TASK_ID_MISSING",
            "Queue planner selected a task without a stable task id.",
            details={"selected_task": selected.to_dict()},
        )

    change_check = _ensure_approved_change_for_selected_task(
        selected,
        policy,
        refs.get("evolution"),
        session_id=selected_session_id,
        root=root_path,
        actor=actor,
        python_executable=python_bin,
        runner=runner,
    )
    side_effects: list[CommandResult] = [change_check]
    if not change_check.ok:
        phase = PhaseResult.blocked(
            PHASE_NAME,
            reason=change_check.message,
            next_action=(
                "Satisfy the selected-task Change gate, then rerun prepare."
            ),
            artifacts={
                "blocked_by": str(change_check.data.get("stop_code") or "BLOCKED"),
                "source": source,
                "session_id": selected_session_id,
                "selected_task": selected.to_dict(),
                "queue_counts": _queue_counts(queue_preview),
                "change_gate": dict(change_check.data),
            },
            changed_files=_changed_files(side_effects),
            generated_files=_generated_files(side_effects),
            events=_events(side_effects),
        )
        result = _phase_command(
            phase,
            message=phase.reason,
            data={
                "session_id": selected_session_id,
                "selected_task": selected.to_dict(),
                "queue_source": source,
                "change_gate": dict(change_check.data),
                "side_effects": _effects(side_effects),
            },
        )
        result.owner_action_required = phase.reason
        return result

    freshness = _prepare_artifact_freshness(root_path, task_id, tasks_state)
    if freshness["fresh"]:
        workflow = _reused_workflow_summary(freshness)
        artifacts_rebuilt = False
    else:
        prepare = run_workflow(
            PREPARE_WORKFLOW,
            task_ref=task_id,
            root=root_path,
            actor=actor,
            confirmed=True,
            python_executable=python_bin,
            runner=runner,
        )
        side_effects.append(prepare)
        workflow = _workflow_summary(prepare)
        artifacts_rebuilt = True

        if not prepare.ok:
            phase = PhaseResult.blocked(
                PHASE_NAME,
                reason="Task preparation workflow failed.",
                next_action="Fix the prepare workflow failure, then rerun prepare.",
                artifacts={
                    "blocked_by": "TASK_PREPARE_WORKFLOW_FAILED",
                    "source": source,
                    "session_id": selected_session_id,
                    "selected_task": selected.to_dict(),
                    "queue_counts": _queue_counts(queue_preview),
                    "change_gate": dict(change_check.data),
                    "workflow": workflow,
                    "artifact_freshness": _freshness_report(
                        freshness,
                        rebuilt=artifacts_rebuilt,
                    ),
                },
                changed_files=_changed_files(side_effects),
                generated_files=_generated_files(side_effects),
                events=_events(side_effects),
            )
            result = _phase_command(
                phase,
                message=phase.reason,
                data={
                    "session_id": selected_session_id,
                    "selected_task": selected.to_dict(),
                    "queue_source": source,
                    "change_gate": dict(change_check.data),
                    "workflow": workflow,
                    "artifact_freshness": _freshness_report(
                        freshness,
                        rebuilt=artifacts_rebuilt,
                    ),
                    "side_effects": _effects(side_effects),
                },
            )
            result.owner_action_required = phase.reason
            return result

    try:
        prepare_artifacts = _prepare_artifacts(root_path, task_id)
    except FileNotFoundError as exc:
        phase = PhaseResult.blocked(
            PHASE_NAME,
            reason="Task preparation workflow did not produce a Codex prompt.",
            next_action="Rebuild the Codex prompt package, then rerun prepare.",
            artifacts={
                "blocked_by": "PREPARE_ARTIFACT_MISSING",
                "source": source,
                "session_id": selected_session_id,
                "selected_task": selected.to_dict(),
                "queue_counts": _queue_counts(queue_preview),
                "change_gate": dict(change_check.data),
                "workflow": workflow,
                "artifact_freshness": _freshness_report(
                    freshness,
                    rebuilt=artifacts_rebuilt,
                ),
                "missing_path": _repo_path(root_path, Path(exc.filename or "")),
            },
            changed_files=_changed_files(side_effects),
            generated_files=_generated_files(side_effects),
            events=_events(side_effects),
        )
        result = _phase_command(
            phase,
            message=phase.reason,
            data={
                "session_id": selected_session_id,
                "selected_task": selected.to_dict(),
                "queue_source": source,
                "change_gate": dict(change_check.data),
                "workflow": workflow,
                "artifact_freshness": _freshness_report(
                    freshness,
                    rebuilt=artifacts_rebuilt,
                ),
                "side_effects": _effects(side_effects),
            },
        )
        result.owner_action_required = phase.reason
        return result

    freshness_report = _freshness_report(freshness, rebuilt=artifacts_rebuilt)
    phase = PhaseResult.passed(
        PHASE_NAME,
        reason=_prepare_success_reason(artifacts_rebuilt),
        next_action=(
            "Run pipeline phase execute using {prompt_path} "
            "(sha256 {prompt_sha256})."
        ).format(**prepare_artifacts),
        artifacts={
            "source": source,
            "session_id": selected_session_id,
            **prepare_artifacts,
            "artifact_freshness": freshness_report,
            "selected_task": selected.to_dict(),
            "queue_counts": _queue_counts(queue_preview),
            "change_gate": dict(change_check.data),
            "workflow": workflow,
            "codex_adapter_called": False,
        },
        changed_files=_changed_files(side_effects),
        generated_files=_generated_files(side_effects),
        events=_events(side_effects),
    )
    phase_record = _record_phase_for_session(
        selected_session_id,
        phase,
        root=root_path,
        actor=actor,
        task_id=task_id,
    )
    if phase_record is not None:
        side_effects.append(phase_record)
        if not phase_record.ok:
            return _aggregate_failure(
                "PIPELINE_PREPARE_PHASE_HISTORY_FAILED",
                "Task preparation completed, but session phase history was not recorded.",
                side_effects,
            )

    result = _phase_command(
        phase,
        message=phase.reason,
        data={
            "session_id": selected_session_id,
            **prepare_artifacts,
            "selected_task": selected.to_dict(),
            "queue_source": source,
            "change_gate": dict(change_check.data),
            "workflow": workflow,
            "artifact_freshness": freshness_report,
            "session_phase_recorded": phase_record is not None,
            "side_effects": _effects(side_effects),
        },
    )
    _merge_result_effects(result, side_effects)
    return result


def _resolve_selection(
    root: Path,
    session_id: str,
    tasks_state: Mapping[str, Any],
    *,
    task_refs: Sequence[str],
    epic_ids: Sequence[str],
    statuses: Sequence[str],
    max_tasks: int | None,
    order_by: str,
) -> CommandResult:
    plan = _load_plan(root)
    selected_session_id = session_id.strip()
    has_explicit_queue = _has_explicit_queue(
        task_refs=task_refs,
        epic_ids=epic_ids,
        statuses=statuses,
        max_tasks=max_tasks,
    )
    if selected_session_id and has_explicit_queue:
        return _failure(
            "PIPELINE_QUEUE_SOURCE_AMBIGUOUS",
            "Pass either a session id or explicit queue filters, not both.",
            details={"session_id": selected_session_id},
        )

    if has_explicit_queue:
        policy = PipelinePolicy.default()
        preview = preview_queue(
            tasks_state,
            plan,
            policy=policy,
            request=QueuePlannerRequest(
                task_refs=_string_tuple(task_refs),
                epic_ids=_string_tuple(epic_ids),
                statuses=_string_tuple(statuses),
                max_tasks=max_tasks,
                order_by=order_by,
            ),
        )
        return CommandResult.success(
            command=COMMAND_NAME,
            domain="pipeline",
            message="Pipeline prepare selection resolved.",
            data={
                "source": "explicit_filters",
                "policy": policy,
                "queue_preview": preview,
                "session": {},
                "allow_preparable_fallback": True,
            },
        )

    session_result = _resolve_session(root, selected_session_id)
    if not session_result.ok:
        return session_result

    session = dict(session_result.data["session"])
    policy = PipelinePolicy.from_dict(_mapping(session.get("policy_snapshot"), "policy_snapshot"))
    queue = _mapping(session.get("selected_queue"), "selected_queue")
    queue_selection = str(queue.get("selection") or "")
    preview = preview_queue(
        tasks_state,
        plan,
        policy=policy,
        request=QueuePlannerRequest(
            task_refs=_string_tuple(queue.get("task_refs")),
            epic_ids=_string_tuple(queue.get("epic_ids")),
            statuses=_string_tuple(queue.get("statuses")),
            max_tasks=_optional_int(queue.get("max_tasks")),
            order_by=str(queue.get("order_by") or "execution"),
        ),
    )
    return CommandResult.success(
        command=COMMAND_NAME,
        domain="pipeline",
        message="Pipeline prepare selection resolved.",
        data={
            "source": "session",
            "policy": policy,
            "queue_preview": preview,
            "session": session,
            "allow_preparable_fallback": bool(_string_tuple(queue.get("task_refs")))
            or queue_selection == "current_task",
        },
    )


def _resolve_session(root: Path, session_id: str) -> CommandResult:
    state = load_pipeline_state(root)
    selected_id = session_id or str(state.get("current_session_id") or "")
    if not selected_id:
        return _failure(
            "PIPELINE_NO_QUEUE_SOURCE",
            "Pass a session id or explicit queue filters for prepare.",
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


def _failure(
    code: str,
    message: str,
    *,
    details: Mapping[str, Any] | None = None,
) -> CommandResult:
    phase = PhaseResult.failed(
        PHASE_NAME,
        reason=message,
        next_action="Fix the prepare input and rerun the phase.",
        artifacts={"error_code": code, **dict(details or {})},
    )
    result = CommandResult.failure(
        command=COMMAND_NAME,
        domain="pipeline",
        message=message,
        errors=[CommandMessage(code, message, details=dict(details or {}))],
    )
    result.data = {"phase_result": phase.to_dict()}
    return result


def _phase_command(
    phase: PhaseResult,
    *,
    message: str,
    data: Mapping[str, Any],
) -> CommandResult:
    ok = phase.status.value != "failed"
    result = CommandResult.success(
        command=COMMAND_NAME,
        domain="pipeline",
        message=message,
        data={"phase_result": phase.to_dict(), **_json_data(data)},
    )
    if not ok:
        result.ok = False
    result.changed_files.extend(phase.changed_files)
    result.generated_files.extend(phase.generated_files)
    result.events.extend(phase.events)
    if phase.next_action:
        result.next_actions.append(phase.next_action)
    return result


def _load_plan(root: Path) -> Mapping[str, Any] | None:
    path = ProjectPaths.from_root(root).state_file("plan.json")
    if not path.exists():
        return None
    data = read_json_file(path, missing_code="PLAN_NOT_INITIALIZED")
    return data if isinstance(data, Mapping) else None


def _workflow_summary(result: CommandResult) -> dict[str, Any]:
    steps = result.data.get("steps") if isinstance(result.data, Mapping) else []
    return {
        "ok": result.ok,
        "message": result.message,
        "steps": [
            {
                "id": str(step.get("id") or ""),
                "status": str(step.get("status") or ""),
            }
            for step in (steps or [])
            if isinstance(step, Mapping)
        ],
        "errors": [error.to_dict() for error in result.errors],
    }


def _prepare_artifacts(root: Path, task_id: str) -> dict[str, str]:
    paths = ProjectPaths.from_root(root)
    execution = _load_current_execution(root)
    context_pack = (
        execution.get("context_pack")
        if isinstance(execution.get("context_pack"), Mapping)
        else {}
    )
    prompt_path = _artifact_path(
        root,
        execution.get("prompt_path") if isinstance(execution, Mapping) else "",
        default=paths.generated_file("CODEX_PROMPT.md"),
    )
    if not prompt_path.exists():
        raise FileNotFoundError(2, "No such file or directory", str(prompt_path))
    context_path_value = ""
    if isinstance(context_pack, Mapping):
        context_path_value = (
            context_pack.get("relative_path") or context_pack.get("path") or ""
        )
    context_path = _artifact_path(
        root,
        context_path_value,
        default=paths.generated_file("CONTEXT_PACK.md"),
    )
    return {
        "task_id": task_id,
        "context_pack_path": _repo_path(root, context_path),
        "prompt_path": _repo_path(root, prompt_path),
        "prompt_sha256": _sha256(prompt_path),
    }


def _prepare_artifact_freshness(
    root: Path,
    task_id: str,
    tasks_state: Mapping[str, Any],
) -> dict[str, Any]:
    paths = ProjectPaths.from_root(root)
    execution = _load_current_execution(root)
    if not execution:
        return _stale("current_execution_missing")

    prompt_path = _artifact_path(
        root,
        execution.get("prompt_path"),
        default=paths.generated_file("CODEX_PROMPT.md"),
    )
    if str(execution.get("status") or "") != READY_STATUS:
        return _stale(
            "codex_status_not_ready",
            status=str(execution.get("status") or ""),
        )
    if str(execution.get("code") or "") != CODEX_READY:
        return _stale("codex_code_not_ready", code=str(execution.get("code") or ""))
    if str(execution.get("source_type") or "") != "task":
        return _stale(
            "source_type_mismatch",
            source_type=str(execution.get("source_type") or ""),
        )
    if str(execution.get("source_id") or "") != task_id:
        return _stale(
            "selected_task_changed",
            expected_task_id=task_id,
            artifact_task_id=str(execution.get("source_id") or ""),
        )
    if not prompt_path.exists():
        return _stale("prompt_missing", prompt_path=_repo_path(root, prompt_path))
    if execution.get("prompt_exists") is False:
        return _stale(
            "prompt_state_says_missing",
            prompt_path=_repo_path(root, prompt_path),
        )
    if not _prompt_mentions_task(prompt_path, task_id):
        return _stale("prompt_task_mismatch", prompt_path=_repo_path(root, prompt_path))

    context_pack = (
        execution.get("context_pack")
        if isinstance(execution.get("context_pack"), Mapping)
        else {}
    )
    if not context_pack:
        return _stale("context_pack_metadata_missing")
    context_task_id = str(context_pack.get("task_id") or "")
    if context_task_id != task_id:
        return _stale(
            "context_task_mismatch",
            expected_task_id=task_id,
            artifact_task_id=context_task_id,
        )
    if str(context_pack.get("mode") or "") != "task":
        return _stale(
            "context_mode_mismatch",
            mode=str(context_pack.get("mode") or ""),
        )

    context_path = _artifact_path(
        root,
        context_pack.get("path") or context_pack.get("relative_path"),
        default=paths.generated_file("CONTEXT_PACK.md"),
    )
    if not context_path.exists():
        return _stale(
            "context_pack_missing",
            context_pack_path=_repo_path(root, context_path),
        )

    expected_context_hash = str(context_pack.get("sha256") or "")
    if not expected_context_hash:
        return _stale("context_pack_hash_missing")
    actual_context_hash = _sha256(context_path)
    if actual_context_hash != expected_context_hash:
        return _stale(
            "context_pack_hash_mismatch",
            expected_sha256=expected_context_hash,
            actual_sha256=actual_context_hash,
        )

    current_tasks_revision = _metadata_int(tasks_state.get("revision"))
    context_tasks_revision = _metadata_int(context_pack.get("tasks_revision"))
    if context_tasks_revision != current_tasks_revision:
        return _stale(
            "context_tasks_revision_stale",
            expected_revision=current_tasks_revision,
            artifact_revision=context_tasks_revision,
        )

    docs_revision = _load_state_revision(root, "docs.json")
    context_docs_revision = _metadata_int(context_pack.get("docs_revision"))
    if docs_revision is None:
        return _stale("docs_state_missing")
    if context_docs_revision != docs_revision:
        return _stale(
            "context_docs_revision_stale",
            expected_revision=docs_revision,
            artifact_revision=context_docs_revision,
        )

    return {
        "fresh": True,
        "reason": "fresh_artifacts_match_selected_task",
        "prompt_path": _repo_path(root, prompt_path),
        "context_pack_path": _repo_path(root, context_path),
        "task_id": task_id,
    }


def _stale(reason: str, **details: Any) -> dict[str, Any]:
    return {"fresh": False, "reason": reason, **details}


def _freshness_report(
    freshness: Mapping[str, Any],
    *,
    rebuilt: bool,
) -> dict[str, Any]:
    return {
        "status": "rebuilt" if rebuilt else "reused",
        "reason": str(freshness.get("reason") or ""),
        "rebuild_required_before_prepare": not bool(freshness.get("fresh")),
        "fresh_before_prepare": bool(freshness.get("fresh")),
    }


def _prepare_success_reason(rebuilt: bool) -> str:
    if rebuilt:
        return "Task preparation rebuilt artifacts; Codex execution has not been started."
    return "Task preparation reused fresh artifacts; Codex execution has not been started."


def _reused_workflow_summary(freshness: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "message": "Fresh prepare artifacts reused; prepare workflow was not rerun.",
        "steps": [],
        "reused": True,
        "artifact_freshness": dict(freshness),
    }


def _prompt_mentions_task(path: Path, task_id: str) -> bool:
    try:
        text = path.read_text(encoding="utf-8")[:8192]
    except UnicodeDecodeError:
        return False
    markers = (
        "Task: {}".format(task_id),
        "Task ID: {}".format(task_id),
        "Source ID: {}".format(task_id),
    )
    return any(marker in text for marker in markers)


def _load_state_revision(root: Path, filename: str) -> int | None:
    path = ProjectPaths.from_root(root).state_file(filename)
    if not path.exists():
        return None
    try:
        data = read_json_file(path, missing_code="STATE_NOT_FOUND")
    except StoreError:
        return None
    if not isinstance(data, Mapping):
        return None
    return _metadata_int(data.get("revision"))


def _metadata_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = value.strip()
        if text.isdigit():
            return int(text)
    return None


def _load_current_execution(root: Path) -> Mapping[str, Any]:
    path = ProjectPaths.from_root(root).state_file("current_execution.json")
    if not path.exists():
        return {}
    data = read_json_file(path, missing_code="CODEX_CURRENT_EXECUTION_NOT_FOUND")
    return data if isinstance(data, Mapping) else {}


def _artifact_path(root: Path, value: Any, *, default: Path) -> Path:
    text = str(value or "").strip()
    path = Path(text) if text else default
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def _repo_path(root: Path, path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _record_phase_for_session(
    session_id: str,
    phase: PhaseResult,
    *,
    root: Path,
    actor: str,
    task_id: str,
) -> CommandResult | None:
    if not session_id:
        return None
    return record_phase_result(
        session_id,
        phase,
        root=root,
        actor=actor,
        task_id=task_id,
    )


def _aggregate_failure(
    code: str,
    message: str,
    effects: Sequence[CommandResult],
) -> CommandResult:
    result = CommandResult.failure(
        command=COMMAND_NAME,
        domain="pipeline",
        message=message,
        errors=[
            CommandMessage(
                code,
                message,
                details={"side_effects": _effects(effects)},
            )
        ],
    )
    result.changed_files.extend(_changed_files(effects))
    result.generated_files.extend(_generated_files(effects))
    result.events.extend(_events(effects))
    return result


def _merge_result_effects(
    result: CommandResult,
    effects: Sequence[CommandResult],
) -> None:
    for value in _changed_files(effects):
        _append_unique(result.changed_files, value)
    for value in _generated_files(effects):
        _append_unique(result.generated_files, value)
    for value in _events(effects):
        _append_unique(result.events, value)


def _effects(effects: Sequence[CommandResult]) -> list[dict[str, Any]]:
    return [effect.to_dict() for effect in effects]


def _changed_files(effects: Sequence[CommandResult]) -> tuple[str, ...]:
    return _merged_result_field(effects, "changed_files")


def _generated_files(effects: Sequence[CommandResult]) -> tuple[str, ...]:
    return _merged_result_field(effects, "generated_files")


def _events(effects: Sequence[CommandResult]) -> tuple[str, ...]:
    return _merged_result_field(effects, "events")


def _merged_result_field(
    effects: Sequence[CommandResult],
    field_name: str,
) -> tuple[str, ...]:
    values: list[str] = []
    for effect in effects:
        for value in getattr(effect, field_name):
            _append_unique(values, str(value))
    return tuple(values)


def _queue_counts(queue_preview: QueuePreview) -> dict[str, int]:
    return {
        "executable": len(queue_preview.executable),
        "waiting": len(queue_preview.waiting),
        "blocked": len(queue_preview.blocked),
        "skipped": len(queue_preview.skipped),
    }


def _selected_prepare_task(
    queue_preview: QueuePreview,
    *,
    allow_status_fallback: bool,
) -> QueuePreviewItem | None:
    if queue_preview.next_task is not None:
        return queue_preview.next_task
    if not allow_status_fallback:
        return None
    selected_items = [
        item
        for item in queue_preview.items
        if item.id
        and item.status in PREPARABLE_STATUSES
        and _reason_codes(item).issubset(PREPARABLE_REASON_CODES)
    ]
    if len(selected_items) == 1:
        return selected_items[0]
    return None


def _reason_codes(item: QueuePreviewItem) -> set[str]:
    return {str(reason.get("code") or "") for reason in item.reasons}


def _json_data(data: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, QueuePreview):
            result[key] = value.to_dict()
        elif isinstance(value, QueuePreviewItem):
            result[key] = value.to_dict()
        elif isinstance(value, PipelinePolicy):
            result[key] = value.to_dict()
        else:
            result[key] = value
    return result


def _has_explicit_queue(
    *,
    task_refs: Sequence[str],
    epic_ids: Sequence[str],
    statuses: Sequence[str],
    max_tasks: int | None,
) -> bool:
    return bool(
        _string_tuple(task_refs)
        or _string_tuple(epic_ids)
        or _string_tuple(statuses)
        or max_tasks is not None
    )


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    raise TypeError("{} must be a mapping".format(name))


def _string_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    return tuple(str(item).strip() for item in value if str(item).strip())


def _optional_int(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _append_unique(target: list[str], value: str) -> None:
    if value and value not in target:
        target.append(value)


__all__ = ["prepare_phase"]

"""Governed pipeline session mutations and generated status output."""

from __future__ import annotations

import copy
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from ai_project_ctl.core.events import AuditEvent, AuditLog, new_event_id, utc_now
from ai_project_ctl.core.locks import FileLock
from ai_project_ctl.core.paths import ProjectPaths
from ai_project_ctl.core.result import CommandError, CommandMessage, CommandResult
from ai_project_ctl.core.store import write_json_file, atomic_write_text
from ai_project_ctl.core.validation import ValidationResult

from .phase import PhaseResult
from .policy import PipelinePolicy, QueuePolicy, QueueSelection, policy_preset
from .audit import (
    build_pipeline_audit_payload,
    pipeline_audit_path,
    read_pipeline_audit_events,
    render_pipeline_audit,
    validate_pipeline_audit_events,
)
from .state import (
    ACTIVE_SESSION_STATUSES,
    GATE_STATUSES,
    SESSION_STATUSES,
    STEP_STATUSES,
    load_pipeline_state,
    load_reference_state,
    normalize_pipeline_phase_fields,
    pipeline_events_path,
    pipeline_state_path,
    pipeline_status_path,
    render_pipeline_status,
    session_summary,
    validate_pipeline_state,
)


SESSION_ID_PREFIX = "PSESS-"


class PipelineSessionError(CommandError):
    """Stable pipeline session service error."""


def create_session(
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    policy: PipelinePolicy | None = None,
    policy_name: str = "dry_run",
    selected_queue: Mapping[str, Any] | None = None,
    task_refs: Sequence[str] = (),
    epic_ids: Sequence[str] = (),
    statuses: Sequence[str] = (),
    max_tasks: int | None = None,
    order_by: str = "execution",
    current_task_id: str = "",
    current_task_ref: str = "",
    linked_change_ids: Sequence[str] = (),
    report_ids: Sequence[str] = (),
    review_ids: Sequence[str] = (),
    commit_ids: Sequence[str] = (),
    auto_create_missing_changes: bool = False,
    owner_approve_required_changes: bool = False,
    approval_note: str = "",
    auto_close_note: str = "",
    status: str = "planned",
) -> CommandResult:
    """Create one governed pipeline session."""

    selected_policy = policy or policy_preset(policy_name)
    if auto_create_missing_changes or owner_approve_required_changes or approval_note:
        evolution = selected_policy.evolution
        selected_policy = replace(
            selected_policy,
            evolution=replace(
                evolution,
                create_missing_change=evolution.create_missing_change
                or auto_create_missing_changes,
                owner_approve_required_changes_for_session=(
                    evolution.owner_approve_required_changes_for_session
                    or owner_approve_required_changes
                ),
                owner_approval_note=approval_note or evolution.owner_approval_note,
            ),
        )
    if auto_close_note:
        selected_policy = replace(
            selected_policy,
            closure=replace(
                selected_policy.closure,
                owner_approval_note=auto_close_note,
            ),
        )
    queue = _queue_snapshot(
        selected_policy.queue,
        selected_queue=selected_queue,
        task_refs=task_refs,
        epic_ids=epic_ids,
        statuses=statuses,
        max_tasks=max_tasks,
        order_by=order_by,
    )

    def mutate(state: dict[str, Any], event_id: str, now: str) -> dict[str, Any]:
        session_id = _next_session_id(state.get("sessions", []))
        session = _new_session(
            session_id,
            now=now,
            status=status,
            selected_queue=queue,
            policy=selected_policy,
            current_task_id=current_task_id,
            current_task_ref=current_task_ref,
            linked_change_ids=linked_change_ids,
            report_ids=report_ids,
            review_ids=review_ids,
            commit_ids=commit_ids,
            audit_event_id=event_id,
        )
        state.setdefault("sessions", []).append(session)
        state["current_session_id"] = session_id
        return {
            "session_id": session_id,
            "session": session_summary(session),
            "linked_change_ids": list(linked_change_ids),
            "report_ids": list(report_ids),
            "review_ids": list(review_ids),
            "commit_ids": list(commit_ids),
        }

    return _mutate_pipeline_state(
        root=root,
        actor=actor,
        command="pipeline.session.create",
        entity_id="new",
        mutate=mutate,
    )


def start_step(
    session_id: str,
    step_name: str,
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    task_id: str = "",
) -> CommandResult:
    """Record the start of one pipeline step."""

    _require_non_empty(session_id, "session_id")
    _require_non_empty(step_name, "step_name")

    def mutate(state: dict[str, Any], event_id: str, now: str) -> dict[str, Any]:
        session = _require_session(state, session_id)
        _require_active_session(session)
        step = {
            "name": step_name,
            "status": "running",
            "started_at": now,
            "finished_at": "",
            "task_id": task_id,
            "gate_outcomes": [],
            "result": {},
            "stop_reason": "",
            "audit_event_ids": [event_id],
        }
        session.setdefault("steps", []).append(step)
        session["status"] = "running"
        session["started_at"] = session.get("started_at") or now
        session["current_step"] = step_name
        session["current_step_status"] = "running"
        if task_id:
            session["current_task_id"] = task_id
        counters = session.setdefault("attempt_counters", {})
        counters["steps"] = int(counters.get("steps", 0)) + 1
        _touch_session(session, now, event_id)
        state["current_session_id"] = session_id
        return {"session_id": session_id, "step": dict(step)}

    return _mutate_pipeline_state(
        root=root,
        actor=actor,
        command="pipeline.step.start",
        entity_id=session_id,
        mutate=mutate,
    )


def record_step_result(
    session_id: str,
    step_name: str,
    result_status: str,
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    task_id: str = "",
    gate_name: str = "",
    gate_status: str = "",
    gate_details: Mapping[str, Any] | None = None,
    stop_reason: str = "",
    linked_change_ids: Sequence[str] = (),
    report_ids: Sequence[str] = (),
    review_ids: Sequence[str] = (),
    commit_ids: Sequence[str] = (),
) -> CommandResult:
    """Record the result of one pipeline step."""

    _require_non_empty(session_id, "session_id")
    _require_non_empty(step_name, "step_name")
    if result_status not in STEP_STATUSES - {"planned", "running"}:
        raise PipelineSessionError(
            "PIPELINE_INVALID_STEP_RESULT",
            "step result must be one of: {}".format(
                ", ".join(sorted(STEP_STATUSES - {"planned", "running"}))
            ),
        )

    def mutate(state: dict[str, Any], event_id: str, now: str) -> dict[str, Any]:
        session = _require_session(state, session_id)
        _require_active_session(session)
        step = _find_latest_step(session, step_name)
        if step is None:
            raise PipelineSessionError(
                "PIPELINE_STEP_NOT_FOUND",
                "session {} has no step named {}".format(session_id, step_name),
            )

        step["status"] = result_status
        step["finished_at"] = now
        if task_id:
            step["task_id"] = task_id
            session["current_task_id"] = task_id
        step["stop_reason"] = stop_reason
        step.setdefault("audit_event_ids", []).append(event_id)

        gate = _gate_outcome(gate_name, gate_status, gate_details, now=now)
        if gate:
            step.setdefault("gate_outcomes", []).append(gate)
            session.setdefault("gate_outcomes", []).append(gate)

        _extend_unique(session.setdefault("linked_change_ids", []), linked_change_ids)
        _extend_unique(session.setdefault("report_ids", []), report_ids)
        _extend_unique(session.setdefault("review_ids", []), review_ids)
        _extend_unique(session.setdefault("commit_ids", []), commit_ids)

        session["current_step"] = step_name
        session["current_step_status"] = result_status
        if result_status == "blocked":
            session["status"] = "blocked"
        elif result_status == "failed":
            session["status"] = "failed"
        elif result_status == "stopped":
            session["status"] = "stopped"
        if stop_reason:
            session["stop_reason"] = stop_reason
            if session["status"] == "running" and result_status in {"blocked", "failed", "stopped"}:
                session["finished_at"] = now
        _touch_session(session, now, event_id)

        return {
            "session_id": session_id,
            "step": dict(step),
            "gate_outcome": gate or {},
            "linked_change_ids": list(linked_change_ids),
            "report_ids": list(report_ids),
            "review_ids": list(review_ids),
            "commit_ids": list(commit_ids),
        }

    return _mutate_pipeline_state(
        root=root,
        actor=actor,
        command="pipeline.step.result",
        entity_id=session_id,
        mutate=mutate,
    )


def record_phase_result(
    session_id: str,
    phase_result: PhaseResult | Mapping[str, Any],
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    task_id: str = "",
    command: str = "pipeline.phase.prepare",
) -> CommandResult:
    """Append one phase result to a governed pipeline session."""

    _require_non_empty(session_id, "session_id")
    phase = _phase_result_dict(phase_result)

    def mutate(state: dict[str, Any], event_id: str, now: str) -> dict[str, Any]:
        session = _require_session(state, session_id)
        _require_active_session(session)
        entry = copy.deepcopy(phase)
        entry.setdefault("artifacts", {})
        entry.setdefault("changed_files", [])
        entry.setdefault("generated_files", [])
        entry.setdefault("events", [])
        entry["events"] = _unique_strings([*entry.get("events", []), event_id])

        session.setdefault("phase_history", []).append(entry)
        session["current_phase"] = str(entry.get("phase") or "")
        session["current_phase_status"] = str(entry.get("status") or "")
        artifacts = (
            entry.get("artifacts")
            if isinstance(entry.get("artifacts"), Mapping)
            else {}
        )
        blocked_by = str(artifacts.get("blocked_by") or "")
        session["blocked_by"] = blocked_by
        session["next_action"] = str(entry.get("next_action") or "")
        if task_id:
            session["current_task_id"] = task_id

        status = str(entry.get("status") or "")
        if status == "blocked":
            session["status"] = "blocked"
            session["stop_reason"] = str(entry.get("reason") or "")
        elif status == "failed":
            session["status"] = "failed"
            session["stop_reason"] = str(entry.get("reason") or "")
        elif status == "passed":
            if session.get("status") in {"planned", "stopped", "blocked", "failed"}:
                session["status"] = "running"
            session["blocked_by"] = ""
            session["stop_reason"] = ""
        session["started_at"] = session.get("started_at") or now
        _touch_session(session, now, event_id)
        state["current_session_id"] = session_id
        return {"session_id": session_id, "phase_result": entry}

    return _mutate_pipeline_state(
        root=root,
        actor=actor,
        command=command,
        entity_id=session_id,
        mutate=mutate,
    )


def stop_session(
    session_id: str,
    reason: str,
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    status: str = "stopped",
) -> CommandResult:
    """Stop one active pipeline session."""

    _require_non_empty(session_id, "session_id")
    _require_non_empty(reason, "reason")
    if status not in {"stopped", "blocked", "failed"}:
        raise PipelineSessionError(
            "PIPELINE_INVALID_STOP_STATUS",
            "stop status must be stopped, blocked, or failed",
        )

    def mutate(state: dict[str, Any], event_id: str, now: str) -> dict[str, Any]:
        session = _require_session(state, session_id)
        _require_active_session(session)
        session["status"] = status
        session["stop_reason"] = reason
        session["current_step_status"] = "stopped"
        session["finished_at"] = now
        _touch_session(session, now, event_id)
        return {"session_id": session_id, "status": status, "stop_reason": reason}

    return _mutate_pipeline_state(
        root=root,
        actor=actor,
        command="pipeline.session.stop",
        entity_id=session_id,
        mutate=mutate,
    )


def complete_session(
    session_id: str,
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    reason: str = "completed",
) -> CommandResult:
    """Mark one active pipeline session completed."""

    _require_non_empty(session_id, "session_id")

    def mutate(state: dict[str, Any], event_id: str, now: str) -> dict[str, Any]:
        session = _require_session(state, session_id)
        _require_active_session(session)
        session["status"] = "completed"
        session["stop_reason"] = reason
        session["finished_at"] = now
        session["current_step_status"] = (
            session.get("current_step_status") if session.get("current_step") else "passed"
        )
        _touch_session(session, now, event_id)
        if state.get("current_session_id") == session_id:
            state["current_session_id"] = None
        return {"session_id": session_id, "status": "completed"}

    return _mutate_pipeline_state(
        root=root,
        actor=actor,
        command="pipeline.session.complete",
        entity_id=session_id,
        mutate=mutate,
    )


def validate_sessions(*, root: str | Path = ".") -> ValidationResult:
    state = load_pipeline_state(root)
    refs = load_reference_state(root)
    result = validate_pipeline_state(
        state,
        tasks_state=refs["tasks"],
        evolution_state=refs["evolution"],
        task_reports_state=refs["task_reports"],
    )
    result.extend(validate_pipeline_audit_events(read_pipeline_audit_events(root), state=state))
    return result


def render_status(*, root: str | Path = ".") -> str:
    state = load_pipeline_state(root)
    result = validate_sessions(root=root)
    result.require_ok()
    text = render_pipeline_status(state)
    audit_text = render_pipeline_audit(read_pipeline_audit_events(root), state=state)
    ProjectPaths.from_root(root).ensure_project_dirs()
    atomic_write_text(pipeline_status_path(root), text)
    atomic_write_text(pipeline_audit_path(root), audit_text)
    return text


def check_generated(*, root: str | Path = ".") -> ValidationResult:
    state = load_pipeline_state(root)
    result = validate_sessions(root=root)
    if not result.ok:
        return result
    path = pipeline_status_path(root)
    if not path.exists():
        result.add_error(
            "PIPELINE_STATUS_MISSING",
            "missing generated file: {}".format(path),
            path=str(path),
        )
        return result
    expected = render_pipeline_status(state)
    actual = path.read_text(encoding="utf-8")
    if actual != expected:
        result.add_error(
            "PIPELINE_STATUS_OUTDATED",
            "outdated generated file: {}".format(path),
            path=str(path),
        )
    audit_path = pipeline_audit_path(root)
    if not audit_path.exists():
        result.add_error(
            "PIPELINE_AUDIT_MISSING",
            "missing generated file: {}".format(audit_path),
            path=str(audit_path),
        )
        return result
    expected_audit = render_pipeline_audit(read_pipeline_audit_events(root), state=state)
    actual_audit = audit_path.read_text(encoding="utf-8")
    if actual_audit != expected_audit:
        result.add_error(
            "PIPELINE_AUDIT_OUTDATED",
            "outdated generated file: {}".format(audit_path),
            path=str(audit_path),
        )
    return result


def status_payload(*, root: str | Path = ".") -> dict[str, Any]:
    state = load_pipeline_state(root)
    sessions = [session for session in state.get("sessions", []) if isinstance(session, Mapping)]
    current_session_id = state.get("current_session_id")
    current = next(
        (session for session in sessions if session.get("id") == current_session_id),
        None,
    )
    return {
        "state_path": str(pipeline_state_path(root)),
        "events_path": str(pipeline_events_path(root)),
        "generated_status_path": str(pipeline_status_path(root)),
        "generated_audit_path": str(pipeline_audit_path(root)),
        "revision": state.get("revision", 0),
        "current_session_id": current_session_id,
        "current_session": session_summary(current) if current else None,
        "sessions": [session_summary(session) for session in sessions],
    }


def _mutate_pipeline_state(
    *,
    root: str | Path,
    actor: str,
    command: str,
    entity_id: str,
    mutate,
) -> CommandResult:
    root_path = Path(root).resolve()
    paths = ProjectPaths.from_root(root_path)
    paths.ensure_project_dirs()
    lock = FileLock(paths.lock_file("pipeline_sessions"))

    with lock:
        state = load_pipeline_state(root_path)
        refs = load_reference_state(root_path)
        before = validate_pipeline_state(
            state,
            tasks_state=refs["tasks"],
            evolution_state=refs["evolution"],
            task_reports_state=refs["task_reports"],
        )
        if not before.ok:
            return _validation_failure(command, before, state.get("revision"))

        next_state = copy.deepcopy(state)
        normalize_pipeline_phase_fields(next_state)
        revision_before = int(next_state.get("revision", 0))
        event_id = new_event_id()
        now = utc_now()
        mutation_data = mutate(next_state, event_id, now) or {}
        normalize_pipeline_phase_fields(next_state)
        next_state["revision"] = revision_before + 1
        next_state["updated_at"] = now

        after = validate_pipeline_state(
            next_state,
            tasks_state=refs["tasks"],
            evolution_state=refs["evolution"],
            task_reports_state=refs["task_reports"],
        )
        if not after.ok:
            return _validation_failure(command, after, revision_before)

        state_path = pipeline_state_path(root_path)
        events_path = pipeline_events_path(root_path)
        status_path = pipeline_status_path(root_path)
        audit_path = pipeline_audit_path(root_path)
        write_json_file(state_path, next_state)
        audit_payload = build_pipeline_audit_payload(command, mutation_data)
        event = AuditEvent(
            actor=actor,
            command=command,
            entity_type="pipeline_session",
            entity_id=str(mutation_data.get("session_id") or entity_id),
            revision_before=revision_before,
            revision_after=next_state["revision"],
            payload=audit_payload,
            event_id=event_id,
            timestamp=now,
        )
        AuditLog(events_path).append(event)
        atomic_write_text(status_path, render_pipeline_status(next_state))
        atomic_write_text(
            audit_path,
            render_pipeline_audit(read_pipeline_audit_events(root_path), state=next_state),
        )

        result = CommandResult.success(
            command=command,
            domain="pipeline",
            message="OK: {} revision {} -> {}".format(
                command,
                revision_before,
                next_state["revision"],
            ),
            data=mutation_data,
            revision_before=revision_before,
            revision_after=next_state["revision"],
        )
        result.changed_files.extend(
            [str(state_path), str(events_path), str(status_path), str(audit_path)]
        )
        result.generated_files.extend([str(status_path), str(audit_path)])
        result.events.append(event_id)
        result.warnings.extend(before.warning_messages())
        result.warnings.extend(after.warning_messages())
        return result


def _validation_failure(
    command: str,
    validation: ValidationResult,
    revision_before: int | None,
) -> CommandResult:
    return CommandResult.failure(
        command=command,
        domain="pipeline",
        message="VALIDATION_FAILED",
        errors=[
            CommandMessage(issue.code, issue.message, issue.path)
            for issue in validation.errors
        ],
        revision_before=revision_before,
        revision_after=revision_before,
    )


def _new_session(
    session_id: str,
    *,
    now: str,
    status: str,
    selected_queue: Mapping[str, Any],
    policy: PipelinePolicy,
    current_task_id: str,
    current_task_ref: str,
    linked_change_ids: Sequence[str],
    report_ids: Sequence[str],
    review_ids: Sequence[str],
    commit_ids: Sequence[str],
    audit_event_id: str,
) -> dict[str, Any]:
    if status not in SESSION_STATUSES:
        raise PipelineSessionError(
            "PIPELINE_INVALID_SESSION_STATUS",
            "session status must be one of: {}".format(", ".join(sorted(SESSION_STATUSES))),
        )
    return {
        "id": session_id,
        "status": status,
        "selected_queue": dict(selected_queue),
        "policy_snapshot": policy.to_dict(),
        "current_task_id": current_task_id,
        "current_task_ref": current_task_ref,
        "current_phase": "",
        "current_phase_status": "",
        "blocked_by": "",
        "next_action": "",
        "phase_history": [],
        "current_step": "",
        "current_step_status": "planned",
        "attempt_counters": {"steps": 0, "tasks": 0, "rework": 0},
        "gate_outcomes": [],
        "steps": [],
        "linked_change_ids": list(linked_change_ids),
        "report_ids": list(report_ids),
        "review_ids": list(review_ids),
        "commit_ids": list(commit_ids),
        "audit_event_ids": [audit_event_id],
        "stop_reason": "",
        "created_at": now,
        "updated_at": now,
        "started_at": "",
        "finished_at": "",
    }


def _queue_snapshot(
    policy: QueuePolicy,
    *,
    selected_queue: Mapping[str, Any] | None,
    task_refs: Sequence[str],
    epic_ids: Sequence[str],
    statuses: Sequence[str],
    max_tasks: int | None,
    order_by: str,
) -> dict[str, Any]:
    if selected_queue is not None:
        return dict(selected_queue)
    return {
        "selection": policy.selection.value
        if isinstance(policy.selection, QueueSelection)
        else str(policy.selection),
        "task_refs": [str(ref) for ref in task_refs],
        "epic_ids": [str(epic_id) for epic_id in epic_ids],
        "statuses": [str(status) for status in statuses],
        "max_tasks": max_tasks if max_tasks is not None else policy.max_tasks,
        "order_by": order_by,
        "include_blocked_tasks": policy.include_blocked_tasks,
    }


def _next_session_id(sessions: Sequence[Any]) -> str:
    max_id = 0
    for session in sessions:
        if not isinstance(session, Mapping):
            continue
        raw = str(session.get("id") or "")
        if not raw.startswith(SESSION_ID_PREFIX):
            continue
        suffix = raw[len(SESSION_ID_PREFIX) :]
        if suffix.isdigit():
            max_id = max(max_id, int(suffix))
    return "{}{:03d}".format(SESSION_ID_PREFIX, max_id + 1)


def _require_session(state: Mapping[str, Any], session_id: str) -> dict[str, Any]:
    for session in state.get("sessions", []):
        if isinstance(session, dict) and session.get("id") == session_id:
            return session
    raise PipelineSessionError(
        "PIPELINE_SESSION_NOT_FOUND",
        "pipeline session not found: {}".format(session_id),
    )


def _require_active_session(session: Mapping[str, Any]) -> None:
    if session.get("status") not in ACTIVE_SESSION_STATUSES:
        raise PipelineSessionError(
            "PIPELINE_SESSION_NOT_ACTIVE",
            "pipeline session {} is not active: {}".format(
                session.get("id"),
                session.get("status"),
            ),
        )


def _find_latest_step(session: Mapping[str, Any], step_name: str) -> dict[str, Any] | None:
    for step in reversed(session.get("steps", [])):
        if isinstance(step, dict) and step.get("name") == step_name:
            return step
    return None


def _touch_session(session: dict[str, Any], now: str, event_id: str) -> None:
    session["updated_at"] = now
    session.setdefault("audit_event_ids", []).append(event_id)


def _gate_outcome(
    name: str,
    status: str,
    details: Mapping[str, Any] | None,
    *,
    now: str,
) -> dict[str, Any] | None:
    if not name and not status and not details:
        return None
    if not name:
        raise PipelineSessionError("PIPELINE_GATE_NAME_REQUIRED", "gate name is required")
    selected_status = status or "unknown"
    if selected_status not in GATE_STATUSES:
        raise PipelineSessionError(
            "PIPELINE_INVALID_GATE_STATUS",
            "gate status must be one of: {}".format(", ".join(sorted(GATE_STATUSES))),
        )
    return {
        "name": name,
        "status": selected_status,
        "recorded_at": now,
        "details": dict(details or {}),
    }


def _phase_result_dict(value: PhaseResult | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(value, PhaseResult):
        return value.to_dict()
    return PhaseResult.from_dict(value).to_dict()


def _unique_strings(values: Sequence[Any]) -> list[str]:
    result: list[str] = []
    for value in values:
        text = str(value)
        if text and text not in result:
            result.append(text)
    return result


def _extend_unique(target: list[Any], values: Sequence[str]) -> None:
    seen = {str(item) for item in target}
    for value in values:
        text = str(value)
        if text and text not in seen:
            target.append(text)
            seen.add(text)


def _require_non_empty(value: str, field: str) -> None:
    if not str(value or "").strip():
        raise PipelineSessionError(
            "PIPELINE_MISSING_REQUIRED_ARGUMENT",
            "{} is required".format(field),
        )

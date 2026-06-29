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
from .git_status import GitStatusError, capture_git_status_snapshot
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
LIVE_PHASE_STATUS = "running"
CODE_AUTO_CLOSE_OWNER_NOTE_REQUIRED = "PIPELINE_AUTO_CLOSE_OWNER_NOTE_REQUIRED"
FILE_EVIDENCE_KEY = "file_evidence"
GIT_STATUS_BASELINE_KEY = "git_status_baseline"
LATEST_GIT_STATUS_KEY = "latest_git_status"
PRE_EXISTING_DIRTY_FILES_KEY = "pre_existing_dirty_files"
SESSION_OWNED_CHANGED_FILES_KEY = "session_owned_changed_files"
PHASE_DELTAS_KEY = "phase_deltas"
CLOSE_STATUS_KEY = "close_status"
PIPELINE_BOOKKEEPING_PATHS = frozenset(
    {
        "AI_PROJECT/state/pipeline_sessions.json",
        "AI_PROJECT/events/pipeline-events.jsonl",
        "AI_PROJECT/generated/PIPELINE_STATUS.md",
        "AI_PROJECT/generated/PIPELINE_AUDIT.md",
    }
)


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

    root_path = Path(root).resolve()
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
    if (
        selected_policy.closure.auto_close_task
        and not selected_policy.closure.owner_approval_note.strip()
    ):
        return _auto_close_owner_note_required_failure(selected_policy)
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
        _ensure_session_file_evidence_baseline(
            session,
            root=root_path,
            now=now,
            baseline=_capture_git_status_evidence(root=root_path, now=now),
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
        root=root_path,
        actor=actor,
        command="pipeline.session.create",
        entity_id="new",
        mutate=mutate,
    )


def ensure_file_evidence_baseline(
    session_id: str,
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
) -> CommandResult:
    """Ensure an existing session has a git status baseline before dispatch."""

    _require_non_empty(session_id, "session_id")
    root_path = Path(root).resolve()
    state = load_pipeline_state(root_path)
    session = _find_session_by_id(state, session_id)
    if session is None:
        return CommandResult.failure(
            command="pipeline.session.git_baseline",
            domain="pipeline",
            message="Pipeline session not found.",
            errors=[
                CommandMessage(
                    "PIPELINE_SESSION_NOT_FOUND",
                    "pipeline session not found: {}".format(session_id),
                    details={"session_id": session_id},
                )
            ],
            revision_before=state.get("revision") if isinstance(state, Mapping) else None,
            revision_after=state.get("revision") if isinstance(state, Mapping) else None,
        )
    if _has_git_status_baseline(session):
        return CommandResult.success(
            command="pipeline.session.git_baseline",
            domain="pipeline",
            message="OK: pipeline session git status baseline already recorded",
            data={
                "session_id": session_id,
                "baseline_recorded": False,
                "file_evidence": _file_evidence_status_payload(session),
            },
            revision_before=state.get("revision"),
            revision_after=state.get("revision"),
        )

    def mutate(next_state: dict[str, Any], event_id: str, now: str) -> dict[str, Any]:
        selected = _require_session(next_state, session_id)
        _require_active_session(selected)
        baseline = _capture_git_status_evidence(root=root_path, now=now)
        _ensure_session_file_evidence_baseline(
            selected,
            root=root_path,
            now=now,
            baseline=baseline,
        )
        _touch_session(selected, now, event_id)
        return {
            "session_id": session_id,
            "baseline_recorded": True,
            "file_evidence": _file_evidence_status_payload(selected),
        }

    return _mutate_pipeline_state(
        root=root_path,
        actor=actor,
        command="pipeline.session.git_baseline",
        entity_id=session_id,
        mutate=mutate,
    )


def _auto_close_owner_note_required_failure(policy: PipelinePolicy) -> CommandResult:
    next_action = (
        "Recreate the pipeline session with an explicit Human Owner auto-close "
        "note, for example --auto-close-note <OWNER_NOTE>."
    )
    result = CommandResult.failure(
        command="pipeline.session.create",
        domain="pipeline",
        message=CODE_AUTO_CLOSE_OWNER_NOTE_REQUIRED,
        errors=[
            CommandMessage(
                CODE_AUTO_CLOSE_OWNER_NOTE_REQUIRED,
                "Auto-close pipeline sessions require an explicit Human Owner auto-close note.",
                path="closure.owner_approval_note",
                details={
                    "policy": policy.name,
                    "auto_close_task": True,
                    "owner_approval_note_present": False,
                    "required_argument": "auto_close_note",
                    "next_action": next_action,
                },
            )
        ],
    )
    result.owner_action_required = "Provide Human Owner auto-close approval note."
    result.next_actions.append(next_action)
    return result


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
    current_step_name: str = "",
    command: str = "pipeline.phase.prepare",
) -> CommandResult:
    """Append one phase result to a governed pipeline session."""

    _require_non_empty(session_id, "session_id")
    root_path = Path(root).resolve()
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
        file_delta = _record_session_file_delta(
            session,
            root=root_path,
            now=now,
            event_id=event_id,
            phase_entry=entry,
        )
        if file_delta:
            artifacts = dict(entry.get("artifacts") or {})
            artifacts["file_delta"] = file_delta
            entry["artifacts"] = artifacts

        history = session.setdefault("phase_history", [])
        replaced_running_phase = _replace_latest_running_phase(history, entry)
        if not replaced_running_phase:
            history.append(entry)
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
        if status == LIVE_PHASE_STATUS:
            session["status"] = "running"
            session["blocked_by"] = ""
            session["stop_reason"] = ""
            step_name = current_step_name or session.get("current_step") or entry.get("phase")
            session["current_step"] = str(step_name or "")
            session["current_step_status"] = LIVE_PHASE_STATUS
        elif status == "blocked":
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
        if replaced_running_phase and session.get("current_step_status") == LIVE_PHASE_STATUS:
            session["current_step_status"] = status
        session["started_at"] = session.get("started_at") or now
        _touch_session(session, now, event_id)
        state["current_session_id"] = session_id
        return {"session_id": session_id, "phase_result": entry}

    return _mutate_pipeline_state(
        root=root_path,
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
    result = _validate_pipeline_state_for_session_service(
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
        "current_session": _status_session_summary(current) if current else None,
        "sessions": [_status_session_summary(session) for session in sessions],
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
        before = _validate_pipeline_state_for_session_service(
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

        after = _validate_pipeline_state_for_session_service(
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


def _capture_git_status_evidence(*, root: Path, now: str) -> dict[str, Any]:
    try:
        snapshot = capture_git_status_snapshot(root=root)
    except GitStatusError as exc:
        return {
            "captured_at": now,
            "ok": False,
            "error": str(exc),
            "entries": [],
            "dirty_paths": [],
        }
    entries = [
        entry.to_dict()
        for entry in snapshot.entries
        if not _is_transient_file_evidence_path(entry.path)
    ]
    data = {
        "entries": entries,
        "dirty_paths": _unique_strings(entry["path"] for entry in entries),
    }
    data["captured_at"] = now
    data["ok"] = True
    data["error"] = ""
    return data


def _ensure_session_file_evidence_baseline(
    session: dict[str, Any],
    *,
    root: Path,
    now: str,
    baseline: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    evidence = session.get(FILE_EVIDENCE_KEY)
    if not isinstance(evidence, dict):
        evidence = {}
        session[FILE_EVIDENCE_KEY] = evidence

    baseline_evidence = evidence.get(GIT_STATUS_BASELINE_KEY)
    if not isinstance(baseline_evidence, Mapping):
        baseline_evidence = dict(baseline or _capture_git_status_evidence(root=root, now=now))
        evidence[GIT_STATUS_BASELINE_KEY] = baseline_evidence
        evidence[LATEST_GIT_STATUS_KEY] = dict(baseline_evidence)

    pre_existing = _dirty_paths_from_git_status_evidence(baseline_evidence)
    evidence[PRE_EXISTING_DIRTY_FILES_KEY] = pre_existing
    evidence.setdefault(SESSION_OWNED_CHANGED_FILES_KEY, [])
    evidence.setdefault(PHASE_DELTAS_KEY, [])
    return evidence


def _record_session_file_delta(
    session: dict[str, Any],
    *,
    root: Path,
    now: str,
    event_id: str,
    phase_entry: Mapping[str, Any],
) -> dict[str, Any]:
    evidence = _ensure_session_file_evidence_baseline(session, root=root, now=now)
    baseline = _mapping_or_empty(evidence.get(GIT_STATUS_BASELINE_KEY))
    current = _capture_git_status_evidence(root=root, now=now)
    pre_existing = _dirty_paths_from_git_status_evidence(baseline)
    current_dirty = _dirty_paths_from_git_status_evidence(current)
    pre_existing_set = set(pre_existing)
    session_owned = _unique_strings(
        [
            *(path for path in current_dirty if path not in pre_existing_set),
            *_explicit_session_owned_bookkeeping_paths(root, phase_entry),
        ]
    )

    evidence[LATEST_GIT_STATUS_KEY] = current
    evidence[PRE_EXISTING_DIRTY_FILES_KEY] = pre_existing
    evidence[SESSION_OWNED_CHANGED_FILES_KEY] = session_owned
    phase_delta = {
        "phase": str(phase_entry.get("phase") or ""),
        "status": str(phase_entry.get("status") or ""),
        "captured_at": current.get("captured_at") or now,
        "event_id": event_id,
        "git_status": current,
        PRE_EXISTING_DIRTY_FILES_KEY: pre_existing,
        SESSION_OWNED_CHANGED_FILES_KEY: session_owned,
    }
    deltas = evidence.setdefault(PHASE_DELTAS_KEY, [])
    if isinstance(deltas, list):
        deltas.append(phase_delta)
    else:
        evidence[PHASE_DELTAS_KEY] = [phase_delta]

    return {
        "git_status_baseline": _compact_git_status_evidence(baseline),
        "latest_git_status": _compact_git_status_evidence(current),
        PRE_EXISTING_DIRTY_FILES_KEY: pre_existing,
        SESSION_OWNED_CHANGED_FILES_KEY: session_owned,
    }


def _status_session_summary(session: Mapping[str, Any]) -> dict[str, Any]:
    summary = session_summary(session)
    close_status = _latest_close_status(session)
    if close_status:
        summary[CLOSE_STATUS_KEY] = close_status
        summary["close_outcome"] = str(close_status.get("outcome") or "")
        summary["commit_status"] = str(close_status.get("commit_status") or "")
        summary["commit_code"] = str(close_status.get("commit_code") or "")
    evidence = _file_evidence_status_payload(session)
    if evidence:
        summary[FILE_EVIDENCE_KEY] = evidence
        summary[PRE_EXISTING_DIRTY_FILES_KEY] = evidence[PRE_EXISTING_DIRTY_FILES_KEY]
        summary[SESSION_OWNED_CHANGED_FILES_KEY] = evidence[
            SESSION_OWNED_CHANGED_FILES_KEY
        ]
    return summary


def _latest_close_status(session: Mapping[str, Any]) -> dict[str, Any]:
    entry = _latest_close_phase(session)
    if not entry:
        return {}
    artifacts = _mapping_or_empty(entry.get("artifacts"))
    close_status = artifacts.get(CLOSE_STATUS_KEY)
    if isinstance(close_status, Mapping):
        data = dict(close_status)
        data.setdefault("owner_next_action", str(entry.get("next_action") or ""))
        return data
    return _derive_close_status_from_artifacts(artifacts, entry)


def successful_committed_close_status(session: Mapping[str, Any]) -> dict[str, Any]:
    """Return close status when the latest close passed with a local commit."""

    entry = _latest_close_phase(session)
    if not entry or str(entry.get("status") or "") != "passed":
        return {}

    artifacts = _mapping_or_empty(entry.get("artifacts"))
    close_status = _latest_close_status(session)
    local_commit = _mapping_or_empty(artifacts.get("local_commit"))
    commit_hash = str(
        local_commit.get("commit_hash")
        or close_status.get("commit_hash")
        or artifacts.get("commit_hash")
        or ""
    ).strip()
    if not commit_hash:
        return {}

    commit_status = str(
        local_commit.get("status") or close_status.get("commit_status") or ""
    ).lower()
    close_outcome = str(
        close_status.get("outcome") or artifacts.get("close_outcome") or ""
    ).lower()
    if commit_status != "pass" and close_outcome != "closed_with_local_commit":
        return {}

    data = dict(close_status)
    task_id = str(artifacts.get("task_id") or session.get("current_task_id") or "")
    if task_id:
        data["task_id"] = task_id
    data["commit_hash"] = commit_hash
    if not data.get("commit_status"):
        data["commit_status"] = commit_status
    data.setdefault("owner_next_action", str(entry.get("next_action") or ""))
    return data


def _latest_close_phase(session: Mapping[str, Any]) -> Mapping[str, Any]:
    history = session.get("phase_history")
    if not isinstance(history, Sequence) or isinstance(history, (str, bytes)):
        return {}
    for entry in reversed(history):
        if not isinstance(entry, Mapping):
            continue
        if str(entry.get("phase") or "") != "close":
            continue
        return entry
    return {}


def _derive_close_status_from_artifacts(
    artifacts: Mapping[str, Any],
    entry: Mapping[str, Any],
) -> dict[str, Any]:
    local_commit = artifacts.get("local_commit")
    if not isinstance(local_commit, Mapping):
        return {}
    readiness = _mapping_or_empty(local_commit.get("readiness"))
    commit_status = str(local_commit.get("status") or "")
    return {
        "outcome": _close_outcome_for_commit_status(commit_status),
        "task_closed": bool(artifacts.get("task_closed", True)),
        "task_status": "done" if artifacts.get("task_closed", True) else "",
        "commit_status": commit_status,
        "commit_code": str(local_commit.get("code") or ""),
        "commit_hash": str(local_commit.get("commit_hash") or ""),
        "commit_readiness_status": str(readiness.get("status") or ""),
        "commit_readiness_code": str(readiness.get("code") or ""),
        "owner_next_action": str(
            artifacts.get("owner_next_action") or entry.get("next_action") or ""
        ),
    }


def _close_outcome_for_commit_status(commit_status: str) -> str:
    if commit_status == "pass":
        return "closed_with_local_commit"
    if commit_status == "blocked":
        return "done_but_commit_blocked"
    if commit_status == "fail":
        return "done_but_commit_failed"
    if commit_status == "skipped":
        return "done_without_local_commit"
    return "done_commit_unknown"


def _file_evidence_status_payload(session: Mapping[str, Any]) -> dict[str, Any]:
    evidence = session.get(FILE_EVIDENCE_KEY)
    if not isinstance(evidence, Mapping):
        return {}
    baseline = _mapping_or_empty(evidence.get(GIT_STATUS_BASELINE_KEY))
    latest = _mapping_or_empty(evidence.get(LATEST_GIT_STATUS_KEY))
    pre_existing = _unique_strings(
        evidence.get(PRE_EXISTING_DIRTY_FILES_KEY)
        or _dirty_paths_from_git_status_evidence(baseline)
    )
    session_owned = _unique_strings(evidence.get(SESSION_OWNED_CHANGED_FILES_KEY) or [])
    phase_deltas = evidence.get(PHASE_DELTAS_KEY)
    return {
        "git_status_baseline": _compact_git_status_evidence(baseline),
        "latest_git_status": _compact_git_status_evidence(latest),
        PRE_EXISTING_DIRTY_FILES_KEY: pre_existing,
        SESSION_OWNED_CHANGED_FILES_KEY: session_owned,
        "phase_delta_count": len(phase_deltas) if isinstance(phase_deltas, list) else 0,
    }


def _compact_git_status_evidence(evidence: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(evidence, Mapping):
        return {
            "captured_at": "",
            "ok": False,
            "error": "",
            "dirty_paths": [],
        }
    return {
        "captured_at": str(evidence.get("captured_at") or ""),
        "ok": bool(evidence.get("ok")),
        "error": str(evidence.get("error") or ""),
        "dirty_paths": _dirty_paths_from_git_status_evidence(evidence),
    }


def _dirty_paths_from_git_status_evidence(evidence: Mapping[str, Any]) -> list[str]:
    if not isinstance(evidence, Mapping):
        return []
    return _unique_strings(evidence.get("dirty_paths") or [])


def _explicit_session_owned_bookkeeping_paths(
    root: Path,
    phase_entry: Mapping[str, Any],
) -> list[str]:
    declared_paths = [
        *_sequence_strings(phase_entry.get("changed_files")),
        *_sequence_strings(phase_entry.get("generated_files")),
    ]
    return [
        normalized
        for normalized in (_normalize_session_path(root, path) for path in declared_paths)
        if normalized in PIPELINE_BOOKKEEPING_PATHS
    ]


def _sequence_strings(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return _unique_strings(str(item) for item in value)


def _normalize_session_path(root: Path, path: str | Path) -> str:
    raw = Path(str(path))
    if raw.is_absolute():
        try:
            return raw.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            return raw.as_posix().lstrip("/")
    text = raw.as_posix()
    if text.startswith("./"):
        text = text[2:]
    return text.lstrip("/")


def _has_git_status_baseline(session: Mapping[str, Any]) -> bool:
    evidence = session.get(FILE_EVIDENCE_KEY)
    return isinstance(evidence, Mapping) and isinstance(
        evidence.get(GIT_STATUS_BASELINE_KEY),
        Mapping,
    )


def _find_session_by_id(
    state: Mapping[str, Any],
    session_id: str,
) -> Mapping[str, Any] | None:
    for session in state.get("sessions", []):
        if isinstance(session, Mapping) and session.get("id") == session_id:
            return session
    return None


def _mapping_or_empty(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _is_transient_file_evidence_path(path: str) -> bool:
    return str(path).startswith("AI_PROJECT/.locks/")


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
    if isinstance(value, Mapping) and str(value.get("status") or "") == LIVE_PHASE_STATUS:
        return _live_phase_result_dict(value)
    return PhaseResult.from_dict(value).to_dict()


def _live_phase_result_dict(value: Mapping[str, Any]) -> dict[str, Any]:
    validation_payload = dict(value)
    validation_payload["status"] = "skipped"
    result = PhaseResult.from_dict(validation_payload).to_dict()
    result["status"] = LIVE_PHASE_STATUS
    return result


def _replace_latest_running_phase(
    history: list[Any],
    entry: dict[str, Any],
) -> bool:
    status = str(entry.get("status") or "")
    if status == LIVE_PHASE_STATUS:
        return False
    phase_name = str(entry.get("phase") or "")
    if not phase_name:
        return False
    for index in range(len(history) - 1, -1, -1):
        existing = history[index]
        if not isinstance(existing, Mapping):
            continue
        if str(existing.get("phase") or "") != phase_name:
            return False
        if str(existing.get("status") or "") != LIVE_PHASE_STATUS:
            return False
        entry["events"] = _unique_strings(
            [
                *existing.get("events", []),
                *entry.get("events", []),
            ]
        )
        history[index] = entry
        return True
    return False


def _validate_pipeline_state_for_session_service(
    state: Mapping[str, Any],
    *,
    tasks_state: Mapping[str, Any] | None = None,
    evolution_state: Mapping[str, Any] | None = None,
    task_reports_state: Mapping[str, Any] | None = None,
) -> ValidationResult:
    return validate_pipeline_state(
        _state_with_live_phase_statuses_normalized(state),
        tasks_state=tasks_state,
        evolution_state=evolution_state,
        task_reports_state=task_reports_state,
    )


def _state_with_live_phase_statuses_normalized(
    state: Mapping[str, Any],
) -> Mapping[str, Any]:
    sessions = state.get("sessions")
    if not isinstance(sessions, list):
        return state
    normalized = copy.deepcopy(state)
    for session in normalized.get("sessions", []):
        if not isinstance(session, dict):
            continue
        if session.get("current_phase_status") == LIVE_PHASE_STATUS:
            session["current_phase_status"] = "skipped"
        history = session.get("phase_history")
        if not isinstance(history, list):
            continue
        for entry in history:
            if isinstance(entry, dict) and entry.get("status") == LIVE_PHASE_STATUS:
                entry["status"] = "skipped"
    return normalized


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

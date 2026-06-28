"""Shared helpers for UI-triggered single-task pipeline runs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from ai_project_ctl.core.paths import ProjectPaths
from ai_project_ctl.core.store import read_json_file

from .policy import PipelinePolicy
from .state import load_pipeline_state, session_summary


UI_RUN_NOT_RUN_TASK_STATUSES = {"done", "deferred", "archived"}
UI_RUN_REUSABLE_SESSION_STATUSES = {"planned", "running", "stopped", "blocked"}


@dataclass(frozen=True)
class UIRunSelectionResolution:
    """Resolved selected-task state for a UI-triggered run."""

    outcome: str
    task_ref: str
    task_id: str = ""
    task_status: str = ""
    session: Mapping[str, Any] | None = None

    @property
    def should_run(self) -> bool:
        return self.outcome == "run"

    @property
    def session_id(self) -> str:
        session = self.session if isinstance(self.session, Mapping) else {}
        return str(session.get("id") or "")

    @property
    def session_status(self) -> str:
        session = self.session if isinstance(self.session, Mapping) else {}
        return str(session.get("status") or "")

    def session_summary(self) -> dict[str, Any]:
        session = self.session if isinstance(self.session, Mapping) else {}
        return session_summary(session) if session else {}


def build_ui_run_selected_queue(
    policy: PipelinePolicy,
    task_ref: str,
    *,
    confirmed: bool,
    allow_internal_change_gate_bypass: bool,
) -> dict[str, Any]:
    """Build selected_queue metadata for one UI-selected task."""

    selection = getattr(policy.queue.selection, "value", policy.queue.selection)
    return {
        "selection": str(selection),
        "task_refs": [task_ref],
        "epic_ids": [],
        "statuses": [],
        "max_tasks": 1,
        "order_by": "selected",
        "include_blocked_tasks": policy.queue.include_blocked_tasks,
        "created_by_command": "ui.run",
        "ui_run_confirmed": bool(confirmed),
        "allow_internal_change_gate_bypass": bool(
            allow_internal_change_gate_bypass
        ),
    }


def resolve_ui_run_selection(
    root: str | Path,
    task_ref: str,
) -> UIRunSelectionResolution:
    """Resolve whether a selected UI run should create a new session."""

    normalized_ref = str(task_ref or "").strip()
    task = _resolve_task(root, normalized_ref)
    if not task:
        return UIRunSelectionResolution(outcome="run", task_ref=normalized_ref)

    task_refs = _task_reference_values(task)
    task_id = str(task.get("id") or "")
    task_status = str(task.get("status") or "")
    latest_reusable = _latest_session_for_task_refs(
        root,
        task_refs,
        statuses=UI_RUN_REUSABLE_SESSION_STATUSES,
    )

    if task_status in UI_RUN_NOT_RUN_TASK_STATUSES:
        return UIRunSelectionResolution(
            outcome="not_run",
            task_ref=normalized_ref,
            task_id=task_id,
            task_status=task_status,
            session=latest_reusable
            or _latest_session_for_task_refs(root, task_refs, statuses=None),
        )

    if latest_reusable:
        return UIRunSelectionResolution(
            outcome="existing_session",
            task_ref=normalized_ref,
            task_id=task_id,
            task_status=task_status,
            session=latest_reusable,
        )

    return UIRunSelectionResolution(
        outcome="run",
        task_ref=normalized_ref,
        task_id=task_id,
        task_status=task_status,
    )


def _resolve_task(root: str | Path, task_ref: str) -> Mapping[str, Any] | None:
    if not task_ref:
        return None
    tasks_path = ProjectPaths.from_root(root).state_file("tasks.json")
    if not tasks_path.exists():
        return None
    state = read_json_file(tasks_path, missing_code="TASKS_NOT_INITIALIZED")
    tasks = state.get("tasks") if isinstance(state, Mapping) else None
    if not isinstance(tasks, list):
        return None
    matches = [
        task
        for task in tasks
        if isinstance(task, Mapping) and task_ref in _task_reference_values(task)
    ]
    if len(matches) == 1:
        return matches[0]
    return None


def _task_reference_values(task: Mapping[str, Any]) -> set[str]:
    values = {
        str(task.get("id") or ""),
        str(task.get("uid") or ""),
        str(task.get("ref") or ""),
        str(task.get("legacy_id") or ""),
    }
    aliases = task.get("aliases")
    if isinstance(aliases, list):
        values.update(str(alias or "") for alias in aliases)
    return {value.strip() for value in values if value.strip()}


def _latest_session_for_task_refs(
    root: str | Path,
    task_refs: set[str],
    *,
    statuses: set[str] | None,
) -> Mapping[str, Any] | None:
    if not task_refs:
        return None
    state = load_pipeline_state(root)
    sessions = state.get("sessions")
    if not isinstance(sessions, list):
        return None
    for session in reversed(sessions):
        if not isinstance(session, Mapping):
            continue
        status = str(session.get("status") or "")
        if statuses is not None and status not in statuses:
            continue
        if _session_matches_task_refs(session, task_refs):
            return session
    return None


def _session_matches_task_refs(
    session: Mapping[str, Any],
    task_refs: set[str],
) -> bool:
    direct_refs = {
        str(session.get("current_task_id") or ""),
        str(session.get("current_task_ref") or ""),
    }
    if task_refs.intersection(ref for ref in direct_refs if ref):
        return True
    queue = session.get("selected_queue")
    if not isinstance(queue, Mapping):
        return False
    queue_task_refs = queue.get("task_refs")
    if not isinstance(queue_task_refs, list):
        return False
    return bool(task_refs.intersection(str(ref or "") for ref in queue_task_refs))

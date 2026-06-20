"""Pipeline session state schema, validation, and status rendering."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from ai_project_ctl.core.events import utc_now
from ai_project_ctl.core.paths import ProjectPaths
from ai_project_ctl.core.store import read_json_file
from ai_project_ctl.core.validation import ValidationResult

from .policy import PipelinePolicy


PIPELINE_SESSION_SCHEMA_VERSION = 1
GENERATED_HEADER = "<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->"
GENERATED_SOURCE = "<!-- Source: AI_PROJECT/state/pipeline_sessions.json -->"

SESSION_STATUSES = {
    "planned",
    "running",
    "stopped",
    "blocked",
    "failed",
    "completed",
    "archived",
}
ACTIVE_SESSION_STATUSES = {"planned", "running", "stopped", "blocked", "failed"}
STEP_STATUSES = {"planned", "running", "passed", "failed", "blocked", "skipped", "stopped"}
GATE_STATUSES = {"pass", "warn", "fail", "blocked", "skipped", "unknown"}

REFERENCE_LIST_FIELDS = (
    "linked_change_ids",
    "report_ids",
    "review_ids",
    "commit_ids",
    "audit_event_ids",
)
FORBIDDEN_PAYLOAD_KEYS = {
    "api_key",
    "password",
    "prompt_payload",
    "prompt_text",
    "raw_prompt",
    "secret",
}
MAX_STORED_STRING_LENGTH = 6000


def pipeline_state_path(root: str | Path) -> Path:
    return ProjectPaths.from_root(root).state_file("pipeline_sessions.json")


def pipeline_events_path(root: str | Path) -> Path:
    return ProjectPaths.from_root(root).event_file("pipeline-events.jsonl")


def pipeline_status_path(root: str | Path) -> Path:
    return ProjectPaths.from_root(root).generated_file("PIPELINE_STATUS.md")


def tasks_state_path(root: str | Path) -> Path:
    return ProjectPaths.from_root(root).state_file("tasks.json")


def evolution_state_path(root: str | Path) -> Path:
    return ProjectPaths.from_root(root).state_file("evolution.json")


def task_reports_state_path(root: str | Path) -> Path:
    return ProjectPaths.from_root(root).state_file("task_reports.json")


def default_pipeline_state(*, now: str | None = None) -> dict[str, Any]:
    timestamp = now or utc_now()
    return {
        "schema_version": PIPELINE_SESSION_SCHEMA_VERSION,
        "revision": 0,
        "created_at": timestamp,
        "updated_at": timestamp,
        "current_session_id": None,
        "sessions": [],
    }


def load_pipeline_state(root: str | Path, *, required: bool = False) -> dict[str, Any]:
    path = pipeline_state_path(root)
    if not path.exists():
        if required:
            raise FileNotFoundError(path)
        return default_pipeline_state()
    data = read_json_file(path, missing_code="PIPELINE_SESSIONS_NOT_INITIALIZED")
    return data if isinstance(data, dict) else {}


def load_reference_state(root: str | Path) -> dict[str, Any]:
    return {
        "tasks": _load_optional_json(tasks_state_path(root)),
        "evolution": _load_optional_json(evolution_state_path(root)),
        "task_reports": _load_optional_json(task_reports_state_path(root)),
    }


def validate_pipeline_state(
    state: Mapping[str, Any],
    *,
    tasks_state: Mapping[str, Any] | None = None,
    evolution_state: Mapping[str, Any] | None = None,
    task_reports_state: Mapping[str, Any] | None = None,
) -> ValidationResult:
    result = ValidationResult()

    if not isinstance(state, Mapping):
        result.add_error("PIPELINE_STATE_NOT_OBJECT", "pipeline session state must be an object")
        return result

    if state.get("schema_version") != PIPELINE_SESSION_SCHEMA_VERSION:
        result.add_error(
            "PIPELINE_INVALID_SCHEMA_VERSION",
            "pipeline_sessions.schema_version must be {}".format(
                PIPELINE_SESSION_SCHEMA_VERSION
            ),
            path="schema_version",
        )

    revision = state.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0:
        result.add_error(
            "PIPELINE_INVALID_REVISION",
            "pipeline_sessions.revision must be a non-negative integer",
            path="revision",
        )

    for field in ("created_at", "updated_at"):
        _require_string(result, state.get(field), field, allow_empty=False)

    sessions = state.get("sessions")
    if not isinstance(sessions, list):
        result.add_error(
            "PIPELINE_INVALID_SESSIONS",
            "pipeline_sessions.sessions must be a list",
            path="sessions",
        )
        sessions = []

    session_ids: set[str] = set()
    for index, session in enumerate(sessions):
        path = "sessions[{}]".format(index)
        if not isinstance(session, Mapping):
            result.add_error(
                "PIPELINE_INVALID_SESSION",
                "{} must be an object".format(path),
                path=path,
            )
            continue
        _validate_session(
            result,
            session,
            path=path,
            session_ids=session_ids,
            tasks_state=tasks_state,
            evolution_state=evolution_state,
            task_reports_state=task_reports_state,
        )
        _check_forbidden_payload(result, session, path)

    current = state.get("current_session_id")
    if current is not None:
        _require_string(result, current, "current_session_id", allow_empty=False)
        if isinstance(current, str) and current not in session_ids:
            result.add_error(
                "PIPELINE_CURRENT_SESSION_MISSING",
                "current_session_id references missing session: {}".format(current),
                path="current_session_id",
            )

    return result


def render_pipeline_status(state: Mapping[str, Any]) -> str:
    sessions = [session for session in state.get("sessions", []) if isinstance(session, Mapping)]
    current = _find_session(sessions, state.get("current_session_id"))
    lines = [
        GENERATED_HEADER,
        GENERATED_SOURCE,
        "",
        "# Pipeline Status",
        "",
        "Revision: `{}`".format(state.get("revision", 0)),
        "Current session: `{}`".format(state.get("current_session_id") or "none"),
        "Sessions: `{}`".format(len(sessions)),
        "",
    ]

    if current:
        lines.extend(
            [
                "## Current Session",
                "",
                "- ID: `{}`".format(current.get("id")),
                "- Status: `{}`".format(current.get("status")),
                "- Policy: `{}`".format(
                    _policy_name(current.get("policy_snapshot"))
                ),
                "- Current task: `{}`".format(current.get("current_task_id") or "none"),
                "- Current step: `{}`".format(current.get("current_step") or "none"),
                "- Step status: `{}`".format(current.get("current_step_status") or "none"),
                "- Stop reason: `{}`".format(current.get("stop_reason") or "none"),
                "",
            ]
        )

    lines.extend(["## Sessions", ""])
    if not sessions:
        lines.append("_No pipeline sessions recorded._")
    else:
        lines.append(
            "| Session | Status | Policy | Current Task | Current Step | Stop Reason |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for session in sessions:
            lines.append(
                "| `{}` | `{}` | `{}` | `{}` | `{}` | {} |".format(
                    session.get("id") or "",
                    session.get("status") or "",
                    _policy_name(session.get("policy_snapshot")),
                    session.get("current_task_id") or "",
                    session.get("current_step") or "",
                    _markdown_cell(session.get("stop_reason") or ""),
                )
            )

    lines.append("")
    return "\n".join(lines)


def expected_pipeline_outputs(state: Mapping[str, Any]) -> dict[str, str]:
    return {"PIPELINE_STATUS.md": render_pipeline_status(state)}


def session_summary(session: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": session.get("id"),
        "status": session.get("status"),
        "policy": _policy_name(session.get("policy_snapshot")),
        "current_task_id": session.get("current_task_id"),
        "current_step": session.get("current_step"),
        "current_step_status": session.get("current_step_status"),
        "stop_reason": session.get("stop_reason"),
    }


def _validate_session(
    result: ValidationResult,
    session: Mapping[str, Any],
    *,
    path: str,
    session_ids: set[str],
    tasks_state: Mapping[str, Any] | None,
    evolution_state: Mapping[str, Any] | None,
    task_reports_state: Mapping[str, Any] | None,
) -> None:
    session_id = session.get("id")
    _require_string(result, session_id, path + ".id", allow_empty=False)
    if isinstance(session_id, str) and session_id:
        if session_id in session_ids:
            result.add_error(
                "PIPELINE_DUPLICATE_SESSION_ID",
                "duplicate pipeline session id: {}".format(session_id),
                path=path + ".id",
            )
        session_ids.add(session_id)

    status = session.get("status")
    if status not in SESSION_STATUSES:
        result.add_error(
            "PIPELINE_INVALID_SESSION_STATUS",
            "{}.status must be one of {}".format(path, ", ".join(sorted(SESSION_STATUSES))),
            path=path + ".status",
        )

    for field in ("created_at", "updated_at"):
        _require_string(result, session.get(field), path + "." + field, allow_empty=False)
    for field in ("started_at", "finished_at", "current_task_id", "current_task_ref", "current_step", "stop_reason"):
        _require_optional_string(result, session.get(field), path + "." + field)

    step_status = session.get("current_step_status")
    if step_status not in STEP_STATUSES:
        result.add_error(
            "PIPELINE_INVALID_STEP_STATUS",
            "{}.current_step_status must be one of {}".format(
                path,
                ", ".join(sorted(STEP_STATUSES)),
            ),
            path=path + ".current_step_status",
        )

    _validate_queue(result, session.get("selected_queue"), path + ".selected_queue", tasks_state)
    _validate_policy_snapshot(result, session.get("policy_snapshot"), path + ".policy_snapshot")
    _validate_attempt_counters(result, session.get("attempt_counters"), path + ".attempt_counters")
    _validate_steps(result, session.get("steps"), path + ".steps", tasks_state)
    _validate_gate_outcomes(result, session.get("gate_outcomes"), path + ".gate_outcomes")

    current_task_id = session.get("current_task_id")
    if current_task_id and tasks_state is not None and current_task_id not in _task_id_set(tasks_state):
        result.add_error(
            "PIPELINE_DANGLING_TASK_REFERENCE",
            "{}.current_task_id references missing task: {}".format(path, current_task_id),
            path=path + ".current_task_id",
        )

    for field in REFERENCE_LIST_FIELDS:
        _validate_string_list(result, session.get(field), path + "." + field)

    _validate_change_refs(
        result,
        session.get("linked_change_ids"),
        path + ".linked_change_ids",
        evolution_state,
    )
    _validate_report_refs(
        result,
        session.get("report_ids"),
        path + ".report_ids",
        task_reports_state,
    )


def _validate_queue(
    result: ValidationResult,
    value: Any,
    path: str,
    tasks_state: Mapping[str, Any] | None,
) -> None:
    if not isinstance(value, Mapping):
        result.add_error("PIPELINE_INVALID_QUEUE", "{} must be an object".format(path), path=path)
        return
    selection = value.get("selection")
    _require_string(result, selection, path + ".selection", allow_empty=False)
    for field in ("task_refs", "epic_ids", "statuses"):
        _validate_string_list(result, value.get(field), path + "." + field)
    max_tasks = value.get("max_tasks")
    if max_tasks is not None and (
        not isinstance(max_tasks, int) or isinstance(max_tasks, bool) or max_tasks < 1
    ):
        result.add_error(
            "PIPELINE_INVALID_QUEUE_LIMIT",
            "{}.max_tasks must be null or a positive integer".format(path),
            path=path + ".max_tasks",
        )
    _require_string(result, value.get("order_by"), path + ".order_by", allow_empty=False)

    if tasks_state is not None:
        known_refs = _task_reference_set(tasks_state)
        for index, task_ref in enumerate(value.get("task_refs") or []):
            if task_ref not in known_refs:
                result.add_error(
                    "PIPELINE_DANGLING_TASK_REFERENCE",
                    "{}.task_refs[{}] references missing task: {}".format(
                        path,
                        index,
                        task_ref,
                    ),
                    path="{}.task_refs[{}]".format(path, index),
                )


def _validate_policy_snapshot(result: ValidationResult, value: Any, path: str) -> None:
    if not isinstance(value, Mapping):
        result.add_error(
            "PIPELINE_INVALID_POLICY_SNAPSHOT",
            "{} must be an object".format(path),
            path=path,
        )
        return
    try:
        policy = PipelinePolicy.from_dict(value)
    except (KeyError, TypeError, ValueError) as exc:
        result.add_error(
            "PIPELINE_INVALID_POLICY_SNAPSHOT",
            "{} is not a valid pipeline policy snapshot: {}".format(path, exc),
            path=path,
        )
        return
    policy_result = policy.validate()
    for issue in policy_result.errors:
        result.add_error(issue.code, issue.message, path=path + "." + issue.path)
    for issue in policy_result.warnings:
        result.add_warning(issue.code, issue.message, path=path + "." + issue.path)


def _validate_attempt_counters(result: ValidationResult, value: Any, path: str) -> None:
    if not isinstance(value, Mapping):
        result.add_error(
            "PIPELINE_INVALID_ATTEMPT_COUNTERS",
            "{} must be an object".format(path),
            path=path,
        )
        return
    for field in ("steps", "tasks", "rework"):
        count = value.get(field)
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            result.add_error(
                "PIPELINE_INVALID_ATTEMPT_COUNTER",
                "{}.{} must be a non-negative integer".format(path, field),
                path=path + "." + field,
            )


def _validate_steps(
    result: ValidationResult,
    value: Any,
    path: str,
    tasks_state: Mapping[str, Any] | None,
) -> None:
    if not isinstance(value, list):
        result.add_error("PIPELINE_INVALID_STEPS", "{} must be a list".format(path), path=path)
        return
    known_tasks = _task_id_set(tasks_state) if tasks_state is not None else None
    for index, step in enumerate(value):
        step_path = "{}[{}]".format(path, index)
        if not isinstance(step, Mapping):
            result.add_error("PIPELINE_INVALID_STEP", "{} must be an object".format(step_path), path=step_path)
            continue
        _require_string(result, step.get("name"), step_path + ".name", allow_empty=False)
        if step.get("status") not in STEP_STATUSES:
            result.add_error(
                "PIPELINE_INVALID_STEP_STATUS",
                "{}.status must be one of {}".format(step_path, ", ".join(sorted(STEP_STATUSES))),
                path=step_path + ".status",
            )
        for field in ("started_at", "finished_at", "task_id", "stop_reason"):
            _require_optional_string(result, step.get(field), step_path + "." + field)
        if known_tasks is not None and step.get("task_id") and step.get("task_id") not in known_tasks:
            result.add_error(
                "PIPELINE_DANGLING_TASK_REFERENCE",
                "{}.task_id references missing task: {}".format(step_path, step.get("task_id")),
                path=step_path + ".task_id",
            )
        _validate_gate_outcomes(result, step.get("gate_outcomes", []), step_path + ".gate_outcomes")
        _validate_string_list(result, step.get("audit_event_ids", []), step_path + ".audit_event_ids")


def _validate_gate_outcomes(result: ValidationResult, value: Any, path: str) -> None:
    if not isinstance(value, list):
        result.add_error(
            "PIPELINE_INVALID_GATE_OUTCOMES",
            "{} must be a list".format(path),
            path=path,
        )
        return
    for index, outcome in enumerate(value):
        outcome_path = "{}[{}]".format(path, index)
        if not isinstance(outcome, Mapping):
            result.add_error(
                "PIPELINE_INVALID_GATE_OUTCOME",
                "{} must be an object".format(outcome_path),
                path=outcome_path,
            )
            continue
        _require_string(result, outcome.get("name"), outcome_path + ".name", allow_empty=False)
        if outcome.get("status") not in GATE_STATUSES:
            result.add_error(
                "PIPELINE_INVALID_GATE_STATUS",
                "{}.status must be one of {}".format(outcome_path, ", ".join(sorted(GATE_STATUSES))),
                path=outcome_path + ".status",
            )
        _require_string(result, outcome.get("recorded_at"), outcome_path + ".recorded_at", allow_empty=False)
        details = outcome.get("details", {})
        if not isinstance(details, Mapping):
            result.add_error(
                "PIPELINE_INVALID_GATE_DETAILS",
                "{}.details must be an object".format(outcome_path),
                path=outcome_path + ".details",
            )


def _validate_change_refs(
    result: ValidationResult,
    value: Any,
    path: str,
    evolution_state: Mapping[str, Any] | None,
) -> None:
    if evolution_state is None:
        return
    known = {
        str(change.get("id"))
        for change in evolution_state.get("changes", [])
        if isinstance(change, Mapping) and change.get("id")
    }
    for index, change_id in enumerate(value or []):
        if change_id not in known:
            result.add_error(
                "PIPELINE_DANGLING_CHANGE_REFERENCE",
                "{}[{}] references missing Change: {}".format(path, index, change_id),
                path="{}[{}]".format(path, index),
            )


def _validate_report_refs(
    result: ValidationResult,
    value: Any,
    path: str,
    task_reports_state: Mapping[str, Any] | None,
) -> None:
    if task_reports_state is None:
        return
    known = {
        str(report.get("id"))
        for report in task_reports_state.get("reports", [])
        if isinstance(report, Mapping) and report.get("id")
    }
    for index, report_id in enumerate(value or []):
        if report_id not in known:
            result.add_error(
                "PIPELINE_DANGLING_REPORT_REFERENCE",
                "{}[{}] references missing task report: {}".format(path, index, report_id),
                path="{}[{}]".format(path, index),
            )


def _task_id_set(tasks_state: Mapping[str, Any] | None) -> set[str]:
    if not tasks_state:
        return set()
    return {
        str(task.get("id"))
        for task in tasks_state.get("tasks", [])
        if isinstance(task, Mapping) and task.get("id")
    }


def _task_reference_set(tasks_state: Mapping[str, Any] | None) -> set[str]:
    refs: set[str] = set()
    if not tasks_state:
        return refs
    for task in tasks_state.get("tasks", []):
        if not isinstance(task, Mapping):
            continue
        for field in ("id", "ref", "uid", "legacy_id"):
            value = task.get(field)
            if value:
                refs.add(str(value))
        aliases = task.get("aliases") or []
        if isinstance(aliases, Sequence) and not isinstance(aliases, (str, bytes)):
            refs.update(str(alias) for alias in aliases if str(alias).strip())
    return refs


def _validate_string_list(result: ValidationResult, value: Any, path: str) -> None:
    if not isinstance(value, list):
        result.add_error(
            "PIPELINE_INVALID_STRING_LIST",
            "{} must be a list".format(path),
            path=path,
        )
        return
    for index, item in enumerate(value):
        _require_string(result, item, "{}[{}]".format(path, index), allow_empty=False)


def _require_optional_string(result: ValidationResult, value: Any, path: str) -> None:
    if value is None:
        return
    _require_string(result, value, path)


def _require_string(
    result: ValidationResult,
    value: Any,
    path: str,
    *,
    allow_empty: bool = True,
) -> None:
    if not isinstance(value, str):
        result.add_error(
            "PIPELINE_INVALID_STRING",
            "{} must be a string".format(path),
            path=path,
        )
        return
    if not allow_empty and not value.strip():
        result.add_error(
            "PIPELINE_EMPTY_STRING",
            "{} must not be empty".format(path),
            path=path,
        )


def _check_forbidden_payload(result: ValidationResult, value: Any, path: str) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            key_lower = key_text.lower()
            nested_path = "{}.{}".format(path, key_text)
            if key_lower in FORBIDDEN_PAYLOAD_KEYS:
                result.add_error(
                    "PIPELINE_FORBIDDEN_PAYLOAD_FIELD",
                    "{} must not be stored in pipeline session state".format(nested_path),
                    path=nested_path,
                )
            _check_forbidden_payload(result, nested, nested_path)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _check_forbidden_payload(result, nested, "{}[{}]".format(path, index))
    elif isinstance(value, str) and len(value) > MAX_STORED_STRING_LENGTH:
        result.add_error(
            "PIPELINE_OVERSIZED_TEXT_PAYLOAD",
            "{} stores an oversized string payload".format(path),
            path=path,
        )


def _find_session(sessions: Sequence[Mapping[str, Any]], session_id: Any) -> Mapping[str, Any] | None:
    if not session_id:
        return None
    for session in sessions:
        if session.get("id") == session_id:
            return session
    return None


def _policy_name(value: Any) -> str:
    if isinstance(value, Mapping):
        name = value.get("name")
        if isinstance(name, str) and name:
            return name
    return ""


def _markdown_cell(value: Any) -> str:
    text = str(value or "")
    return text.replace("|", "\\|").replace("\n", " ")


def _load_optional_json(path: Path) -> Mapping[str, Any] | None:
    if not path.exists():
        return None
    data = read_json_file(path)
    return data if isinstance(data, Mapping) else None

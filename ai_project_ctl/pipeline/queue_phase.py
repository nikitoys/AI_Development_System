"""Read-only pipeline queue preview phase service."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from ai_project_ctl.core.paths import ProjectPaths
from ai_project_ctl.core.result import CommandMessage, CommandResult
from ai_project_ctl.core.store import read_json_file

from .policy import PipelinePolicy
from .queue import QueuePlannerRequest, preview_queue
from .state import load_pipeline_state, load_reference_state, pipeline_state_path


COMMAND_NAME = "pipeline.phase.queue_preview"
PHASE_NAME = "queue_preview"
NO_EXECUTABLE_TASK = "NO_EXECUTABLE_TASK"
QUEUE_OUTPUT_CATEGORIES = ("executable", "waiting", "blocked", "skipped")
QUEUE_ITEM_FIELDS = (
    "id",
    "ref",
    "uid",
    "legacy_id",
    "title",
    "status",
    "epic_id",
    "selected_ref",
)


def preview_queue_phase(
    session_id: str = "",
    *,
    root: str | Path = ".",
    task_refs: Sequence[str] = (),
    epic_ids: Sequence[str] = (),
    statuses: Sequence[str] = (),
    max_tasks: int | None = None,
    order_by: str = "execution",
) -> CommandResult:
    """Preview the next pipeline queue item without writing project state."""

    root_path = Path(root).resolve()
    refs = load_reference_state(root_path)
    tasks_state = refs.get("tasks")
    if not isinstance(tasks_state, Mapping):
        return _failure(
            "PIPELINE_TASKS_STATE_NOT_FOUND",
            "Task state is required to preview the pipeline queue.",
            details={
                "state_path": str(
                    ProjectPaths.from_root(root_path).state_file("tasks.json")
                )
            },
        )

    plan = _load_plan(root_path)
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

    try:
        if has_explicit_queue:
            preview = preview_queue(
                tasks_state,
                plan,
                request=QueuePlannerRequest(
                    task_refs=_string_tuple(task_refs),
                    epic_ids=_string_tuple(epic_ids),
                    statuses=_string_tuple(statuses),
                    max_tasks=max_tasks,
                    order_by=order_by,
                ),
            )
            return _success(
                _normalize_queue_output(preview.to_dict()),
                session=None,
                source="explicit_filters",
            )

        session_result = _resolve_session(root_path, selected_session_id)
        if not session_result.ok:
            return session_result
        session = dict(session_result.data["session"])
        policy = PipelinePolicy.from_dict(
            _mapping(session.get("policy_snapshot"), "policy_snapshot")
        )
        queue = _mapping(session.get("selected_queue"), "selected_queue")
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
        return _success(
            _normalize_queue_output(preview.to_dict()),
            session=session,
            source="session",
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _failure(
            "PIPELINE_QUEUE_PREVIEW_FAILED",
            "Could not preview pipeline queue safely: {}".format(exc),
        )


def _success(
    queue_preview: Mapping[str, Any],
    *,
    session: Mapping[str, Any] | None,
    source: str,
) -> CommandResult:
    next_task = queue_preview.get("next_task")
    has_next_task = isinstance(next_task, Mapping)
    phase_status = "passed" if has_next_task else "blocked"
    blocked_by = "" if has_next_task else NO_EXECUTABLE_TASK
    reason = (
        "Next executable task is available."
        if has_next_task
        else "No executable task is available in the selected queue."
    )
    next_action = (
        "Run pipeline run-next when ready."
        if has_next_task
        else "Create or unblock a ready task, then rerun queue preview."
    )
    phase_result = {
        "phase": PHASE_NAME,
        "status": phase_status,
        "blocked_by": blocked_by,
        "reason": reason,
        "next_action": next_action,
        "artifacts": {
            "source": source,
            "session_id": str(session.get("id") or "") if session else "",
            "next_task": next_task,
            "queue_counts": _queue_counts(queue_preview),
            "queue_categories": _queue_artifact_categories(queue_preview),
            "reason_summary": _reason_summary_artifacts(queue_preview),
        },
        "changed_files": [],
        "generated_files": [],
        "events": [],
    }
    return CommandResult.success(
        command=COMMAND_NAME,
        domain="pipeline",
        message=reason,
        data={
            "phase_result": phase_result,
            "session_id": str(session.get("id") or "") if session else "",
            "queue_source": source,
            "queue_preview": dict(queue_preview),
        },
    )


def _failure(
    code: str,
    message: str,
    *,
    details: Mapping[str, Any] | None = None,
) -> CommandResult:
    phase_result = {
        "phase": PHASE_NAME,
        "status": "failed",
        "blocked_by": "",
        "reason": message,
        "next_action": "Fix the preview input and rerun the read-only command.",
        "artifacts": {"error_code": code, **dict(details or {})},
        "changed_files": [],
        "generated_files": [],
        "events": [],
    }
    return CommandResult(
        ok=False,
        command=COMMAND_NAME,
        domain="pipeline",
        message=message,
        data={"phase_result": phase_result},
        errors=[CommandMessage(code, message, details=dict(details or {}))],
    )


def _resolve_session(root: Path, session_id: str) -> CommandResult:
    state = load_pipeline_state(root)
    selected_id = session_id or str(state.get("current_session_id") or "")
    if not selected_id:
        return _failure(
            "PIPELINE_NO_QUEUE_SOURCE",
            "Pass a session id or explicit queue filters for queue preview.",
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


def _load_plan(root: Path) -> Mapping[str, Any] | None:
    path = ProjectPaths.from_root(root).state_file("plan.json")
    if not path.exists():
        return None
    data = read_json_file(path, missing_code="PLAN_NOT_INITIALIZED")
    return data if isinstance(data, Mapping) else None


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


def _normalize_queue_output(queue_preview: Mapping[str, Any]) -> dict[str, Any]:
    categories = _queue_categories(queue_preview)
    normalized = {
        category: [
            _normalize_queue_item(item, category=category)
            for item in _sequence(categories.get(category))
            if isinstance(item, Mapping)
        ]
        for category in QUEUE_OUTPUT_CATEGORIES
    }
    next_task = queue_preview.get("next_task")
    return {
        "next_task": _normalize_queue_item(next_task, category="executable")
        if isinstance(next_task, Mapping)
        else None,
        **normalized,
        "reasons": _reason_summaries(normalized),
    }


def _queue_categories(
    queue_preview: Mapping[str, Any],
) -> dict[str, list[Mapping[str, Any]]]:
    categories = queue_preview.get("categories")
    if isinstance(categories, Mapping):
        return {
            category: [
                item
                for item in _sequence(categories.get(category))
                if isinstance(item, Mapping)
            ]
            for category in QUEUE_OUTPUT_CATEGORIES
        }

    grouped: dict[str, list[Mapping[str, Any]]] = {
        category: [] for category in QUEUE_OUTPUT_CATEGORIES
    }
    for item in _sequence(queue_preview.get("items")):
        if not isinstance(item, Mapping):
            continue
        category = str(item.get("category") or "")
        if category in grouped:
            grouped[category].append(item)
    return grouped


def _normalize_queue_item(item: Mapping[str, Any], *, category: str) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for field in QUEUE_ITEM_FIELDS:
        value = item.get(field)
        if value is not None and value != "":
            normalized[field] = value

    reasons = _normalize_reasons(item.get("reasons"))
    if category != "executable" and not reasons:
        reasons = [{"code": "reason_unavailable"}]
    if reasons:
        normalized["reason_codes"] = _reason_codes(reasons)
        normalized["reasons"] = reasons
    return normalized


def _normalize_reasons(value: Any) -> list[dict[str, Any]]:
    reasons: list[dict[str, Any]] = []
    for reason in _sequence(value):
        if not isinstance(reason, Mapping):
            continue
        code = str(reason.get("code") or "").strip()
        if not code:
            continue
        normalized = {"code": code}
        for key in sorted(reason):
            if key == "code":
                continue
            reason_value = reason.get(key)
            if _is_compact_json_value(reason_value):
                normalized[str(key)] = reason_value
        reasons.append(normalized)
    return reasons


def _reason_codes(reasons: Sequence[Mapping[str, Any]]) -> list[str]:
    codes: list[str] = []
    for reason in reasons:
        code = str(reason.get("code") or "")
        if code and code not in codes:
            codes.append(code)
    return codes


def _reason_summaries(
    normalized: Mapping[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    for category in ("waiting", "blocked", "skipped"):
        for item in normalized.get(category, []):
            for code in item.get("reason_codes", []):
                reason_code = str(code)
                summary = summaries.setdefault(
                    reason_code,
                    {"code": reason_code, "count": 0, "categories": []},
                )
                summary["count"] += 1
                if category not in summary["categories"]:
                    summary["categories"].append(category)
    return [summaries[code] for code in sorted(summaries)]


def _queue_artifact_categories(
    queue_preview: Mapping[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    return {
        category: [
            _queue_reason_artifact(item)
            for item in _sequence(queue_preview.get(category))
            if isinstance(item, Mapping)
        ]
        for category in QUEUE_OUTPUT_CATEGORIES
    }


def _queue_reason_artifact(item: Mapping[str, Any]) -> dict[str, Any]:
    artifact: dict[str, Any] = {}
    for field in QUEUE_ITEM_FIELDS:
        value = item.get(field)
        if value is not None and value != "":
            artifact[field] = value
    if item.get("reason_codes"):
        artifact["reason_codes"] = list(item.get("reason_codes") or [])
    if item.get("reasons"):
        artifact["reasons"] = [
            dict(reason)
            for reason in _sequence(item.get("reasons"))
            if isinstance(reason, Mapping)
        ]
    return artifact


def _reason_summary_artifacts(queue_preview: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        dict(summary)
        for summary in _sequence(queue_preview.get("reasons"))
        if isinstance(summary, Mapping)
    ]


def _is_compact_json_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (str, int, float, bool)):
        return True
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return all(isinstance(item, (str, int, float, bool)) for item in value)
    return False


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return value
    return ()


def _queue_counts(queue_preview: Mapping[str, Any]) -> dict[str, int]:
    categories = {
        category: queue_preview.get(category) for category in QUEUE_OUTPUT_CATEGORIES
    }
    if not any(isinstance(items, Sequence) for items in categories.values()):
        categories = queue_preview.get("categories")
    if not isinstance(categories, Mapping):
        return {}
    return {
        str(category): len(items) if isinstance(items, Sequence) else 0
        for category, items in categories.items()
        if not isinstance(items, (str, bytes))
    }


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


__all__ = ["preview_queue_phase"]

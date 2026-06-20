"""Pipeline audit event classification, validation, and timeline rendering."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from ai_project_ctl.core.paths import ProjectPaths
from ai_project_ctl.core.validation import ValidationResult

from .state import GENERATED_HEADER, pipeline_events_path


GENERATED_AUDIT_SOURCE = "<!-- Source: AI_PROJECT/events/pipeline-events.jsonl -->"
PIPELINE_AUDIT_PATH_NAME = "PIPELINE_AUDIT.md"
MAX_AUDIT_STRING_LENGTH = 1200
MAX_AUDIT_LIST_LENGTH = 50

SESSION_CREATE = "session.create"
POLICY_SELECTED = "policy.selected"
QUEUE_PLANNED = "queue.planned"
TASK_SELECTED = "task.selected"
CHANGE_CREATED = "change.created"
CHANGE_APPROVED = "change.approved"
CHANGE_ACCEPTED = "change.accepted"
CONTEXT_BUILT = "context.built"
TOKEN_GATE_RESULT = "token_gate.result"
CODEX_RUN_RESULT = "codex_run.result"
REPORT_GATE_RESULT = "report_gate.result"
MACHINE_REVIEW_RESULT = "machine_review.result"
CODEX_REVIEW_RESULT = "codex_review.result"
CLOSE_REWORK_DECISION = "close_rework.decision"
COMMIT_READINESS_RESULT = "commit_readiness.result"
COMMIT_RESULT = "commit.result"
STOP = "stop"
COMPLETION = "completion"
STEP_STARTED = "step.started"
STEP_RESULT = "step.result"

PIPELINE_AUDIT_EVENT_TYPES = {
    SESSION_CREATE,
    POLICY_SELECTED,
    QUEUE_PLANNED,
    TASK_SELECTED,
    CHANGE_CREATED,
    CHANGE_APPROVED,
    CHANGE_ACCEPTED,
    CONTEXT_BUILT,
    TOKEN_GATE_RESULT,
    CODEX_RUN_RESULT,
    REPORT_GATE_RESULT,
    MACHINE_REVIEW_RESULT,
    CODEX_REVIEW_RESULT,
    CLOSE_REWORK_DECISION,
    COMMIT_READINESS_RESULT,
    COMMIT_RESULT,
    STOP,
    COMPLETION,
    STEP_STARTED,
    STEP_RESULT,
}

COMMAND_EVENT_TYPES = {
    "pipeline.session.create": SESSION_CREATE,
    "pipeline.step.start": STEP_STARTED,
    "pipeline.step.result": STEP_RESULT,
    "pipeline.session.stop": STOP,
    "pipeline.session.complete": COMPLETION,
}

GATE_EVENT_TYPES = {
    "policy_validation": POLICY_SELECTED,
    "queue_planner": QUEUE_PLANNED,
    "evolution_change_gate": CHANGE_APPROVED,
    "task_prepare_for_codex": CONTEXT_BUILT,
    "token_budget_gate": TOKEN_GATE_RESULT,
    "codex_execution_policy": CODEX_RUN_RESULT,
    "codex_execution_adapter": CODEX_RUN_RESULT,
    "codex_report_gate": REPORT_GATE_RESULT,
    "machine_review_gate": MACHINE_REVIEW_RESULT,
    "codex_review_gate": CODEX_REVIEW_RESULT,
    "review_close_gate": CLOSE_REWORK_DECISION,
    "commit_gate": COMMIT_RESULT,
    "pipeline_policy": STOP,
}

FORBIDDEN_AUDIT_PAYLOAD_KEYS = {
    "api_key",
    "access_token",
    "password",
    "prompt_payload",
    "prompt_text",
    "raw_prompt",
    "refresh_token",
    "secret",
}


def pipeline_audit_path(root: str | Path) -> Path:
    return ProjectPaths.from_root(root).generated_file(PIPELINE_AUDIT_PATH_NAME)


def build_pipeline_audit_payload(
    command: str,
    mutation_data: Mapping[str, Any],
) -> dict[str, Any]:
    """Return a sanitized audit payload with event type and stable references."""

    sanitized = sanitize_audit_payload(mutation_data)
    event_type = classify_pipeline_event(command, sanitized)
    event_types = _event_types_for_payload(command, sanitized, primary=event_type)
    refs = extract_pipeline_refs(sanitized)
    payload = dict(sanitized)
    payload["event_type"] = event_type
    payload["event_types"] = event_types
    payload["refs"] = refs
    return payload


def sanitize_audit_payload(value: Any) -> Any:
    """Redact forbidden fields and replace large strings with hashes."""

    return _sanitize_value(value, path="payload")


def classify_pipeline_event(command: str, payload: Mapping[str, Any]) -> str:
    gate = _gate_from_payload(payload)
    gate_name = str(gate.get("name") or "") if gate else ""
    if gate_name in GATE_EVENT_TYPES:
        return GATE_EVENT_TYPES[gate_name]
    return COMMAND_EVENT_TYPES.get(command, STEP_RESULT)


def extract_pipeline_refs(payload: Mapping[str, Any]) -> dict[str, Any]:
    refs: dict[str, Any] = {
        "session_id": str(payload.get("session_id") or ""),
        "task_id": "",
        "change_ids": [],
        "report_ids": [],
        "review_ids": [],
        "commit_ids": [],
        "gate": "",
    }

    session = _mapping(payload.get("session"))
    step = _mapping(payload.get("step"))
    gate = _gate_from_payload(payload)
    refs["task_id"] = str(
        payload.get("task_id")
        or step.get("task_id")
        or session.get("current_task_id")
        or ""
    )
    if gate:
        refs["gate"] = str(gate.get("name") or "")

    _collect_refs(payload, refs)
    return refs


def read_pipeline_audit_events(root: str | Path) -> list[dict[str, Any]]:
    path = pipeline_events_path(root)
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            events.append({"_invalid_line": index, "_raw": line})
            continue
        events.append(event if isinstance(event, dict) else {"_invalid_line": index, "_raw": line})
    return events


def validate_pipeline_audit_events(
    events: Sequence[Mapping[str, Any]],
    *,
    state: Mapping[str, Any] | None = None,
) -> ValidationResult:
    result = ValidationResult()
    event_ids: set[str] = set()

    for index, event in enumerate(events):
        path = "events[{}]".format(index)
        if "_invalid_line" in event:
            result.add_error(
                "PIPELINE_INVALID_AUDIT_EVENT",
                "pipeline audit event line is not valid JSON",
                path=path,
            )
            continue

        for field in ("event_id", "timestamp", "actor", "command", "entity_type", "entity_id"):
            value = event.get(field)
            if not isinstance(value, str) or not value.strip():
                result.add_error(
                    "PIPELINE_INVALID_AUDIT_EVENT",
                    "{}.{} must be a non-empty string".format(path, field),
                    path=path + "." + field,
                )
        event_id = event.get("event_id")
        if isinstance(event_id, str) and event_id:
            if event_id in event_ids:
                result.add_error(
                    "PIPELINE_DUPLICATE_AUDIT_EVENT_ID",
                    "duplicate pipeline audit event id: {}".format(event_id),
                    path=path + ".event_id",
                )
            event_ids.add(event_id)

        payload = event.get("payload", {})
        if not isinstance(payload, Mapping):
            result.add_error(
                "PIPELINE_INVALID_AUDIT_PAYLOAD",
                "{}.payload must be an object".format(path),
                path=path + ".payload",
            )
            continue
        _check_audit_payload(result, payload, path + ".payload")

        event_type = payload.get("event_type")
        if event_type is not None and event_type not in PIPELINE_AUDIT_EVENT_TYPES:
            result.add_error(
                "PIPELINE_INVALID_AUDIT_EVENT_TYPE",
                "{}.payload.event_type is not known: {}".format(path, event_type),
                path=path + ".payload.event_type",
            )

        event_types = payload.get("event_types")
        if event_types is not None:
            if not isinstance(event_types, list):
                result.add_error(
                    "PIPELINE_INVALID_AUDIT_EVENT_TYPES",
                    "{}.payload.event_types must be a list".format(path),
                    path=path + ".payload.event_types",
                )
            else:
                for type_index, item in enumerate(event_types):
                    if item not in PIPELINE_AUDIT_EVENT_TYPES:
                        result.add_error(
                            "PIPELINE_INVALID_AUDIT_EVENT_TYPE",
                            "{}.payload.event_types[{}] is not known: {}".format(
                                path,
                                type_index,
                                item,
                            ),
                            path="{}.payload.event_types[{}]".format(path, type_index),
                        )

    if state is not None:
        for expected_id in _state_audit_event_ids(state):
            if expected_id not in event_ids:
                result.add_error(
                    "PIPELINE_MISSING_AUDIT_EVENT",
                    "pipeline state references missing audit event: {}".format(expected_id),
                    path="audit_event_ids",
                )

    return result


def render_pipeline_audit(
    events: Sequence[Mapping[str, Any]],
    *,
    state: Mapping[str, Any] | None = None,
) -> str:
    lines = [
        GENERATED_HEADER,
        GENERATED_AUDIT_SOURCE,
        "",
        "# Pipeline Audit",
        "",
        "Events: `{}`".format(len(events)),
    ]
    if state is not None:
        lines.append("State revision: `{}`".format(state.get("revision", 0)))
        lines.append("Current session: `{}`".format(state.get("current_session_id") or "none"))
    lines.extend(["", "## Timeline", ""])

    if not events:
        lines.append("_No pipeline audit events recorded._")
        lines.append("")
        return "\n".join(lines)

    lines.append("| Time | Event Type | Command | Session | Task | Gate | Summary |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for event in events:
        if "_invalid_line" in event:
            lines.append(
                "|  | `invalid` |  |  |  |  | {} |".format(
                    _markdown_cell(str(event.get("_raw") or "")[:120])
                )
            )
            continue
        payload = _mapping(event.get("payload"))
        refs = extract_pipeline_refs(payload)
        event_type = str(payload.get("event_type") or classify_pipeline_event(str(event.get("command") or ""), payload))
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | {} |".format(
                event.get("timestamp") or "",
                event_type,
                event.get("command") or "",
                refs.get("session_id") or event.get("entity_id") or "",
                refs.get("task_id") or "",
                refs.get("gate") or "",
                _markdown_cell(_event_summary(event, payload, refs)),
            )
        )

    lines.extend(["", "## Event Type Coverage", ""])
    covered = sorted(
        {
            str(event_type)
            for event in events
            for event_type in _event_types_from_event(event)
            if event_type
        }
    )
    if covered:
        for event_type in covered:
            lines.append("- `{}`".format(event_type))
    else:
        lines.append("_No classified pipeline event types recorded._")
    lines.append("")
    return "\n".join(lines)


def _event_types_for_payload(
    command: str,
    payload: Mapping[str, Any],
    *,
    primary: str,
) -> list[str]:
    event_types = [primary]
    if command == "pipeline.session.create":
        session = _mapping(payload.get("session"))
        if session.get("policy"):
            event_types.append(POLICY_SELECTED)
        event_types.append(QUEUE_PLANNED)
        if session.get("current_task_id") or payload.get("current_task_id"):
            event_types.append(TASK_SELECTED)

    gate = _gate_from_payload(payload)
    if gate:
        gate_name = str(gate.get("name") or "")
        details = _mapping(gate.get("details"))
        if gate_name == "queue_planner":
            event_types.append(QUEUE_PLANNED)
            selected = _mapping(details.get("selected_task"))
            if selected.get("id") or selected.get("ref"):
                event_types.append(TASK_SELECTED)
        if gate_name == "evolution_change_gate":
            _extend_event_types_from_change_gate(event_types, details)
        if gate_name == "task_prepare_for_codex":
            event_types.append(CONTEXT_BUILT)
        if gate_name == "commit_gate":
            event_types.append(COMMIT_READINESS_RESULT)
            event_types.append(COMMIT_RESULT)
        if payload.get("step", {}).get("stop_reason") or details.get("stop_reason"):
            event_types.append(STOP)

    if command == "pipeline.session.stop":
        event_types.append(STOP)
    if command == "pipeline.session.complete":
        event_types.append(COMPLETION)
    return _dedupe(event_types)


def _extend_event_types_from_change_gate(event_types: list[str], details: Mapping[str, Any]) -> None:
    change_gate = _mapping(details.get("change_gate"))
    commands = _string_values(change_gate)
    if any("change create" in value or "change.create" in value for value in commands):
        event_types.append(CHANGE_CREATED)
    if any("change approve" in value or "approve_change" in value for value in commands):
        event_types.append(CHANGE_APPROVED)
    if any("accept" in value for value in commands):
        event_types.append(CHANGE_ACCEPTED)
    if CHANGE_APPROVED not in event_types:
        event_types.append(CHANGE_APPROVED)


def _event_types_from_event(event: Mapping[str, Any]) -> list[str]:
    payload = _mapping(event.get("payload"))
    raw_types = payload.get("event_types")
    if isinstance(raw_types, list):
        return [str(item) for item in raw_types]
    event_type = payload.get("event_type")
    if isinstance(event_type, str) and event_type:
        return [event_type]
    return [classify_pipeline_event(str(event.get("command") or ""), payload)]


def _gate_from_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    gate = payload.get("gate_outcome")
    if isinstance(gate, Mapping):
        return gate
    step = payload.get("step")
    if isinstance(step, Mapping):
        gates = step.get("gate_outcomes")
        if isinstance(gates, list) and gates:
            last = gates[-1]
            if isinstance(last, Mapping):
                return last
    return {}


def _collect_refs(value: Any, refs: dict[str, Any]) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            if key_text in {"linked_change_ids", "change_ids"}:
                _extend_unique(refs["change_ids"], _as_string_list(nested))
            elif key_text == "change_id":
                _extend_unique(refs["change_ids"], [str(nested)])
            elif key_text == "report_ids":
                _extend_unique(refs["report_ids"], _as_string_list(nested))
            elif key_text == "report_id":
                _extend_unique(refs["report_ids"], [str(nested)])
            elif key_text == "review_ids":
                _extend_unique(refs["review_ids"], _as_string_list(nested))
            elif key_text == "review_id":
                _extend_unique(refs["review_ids"], [str(nested)])
            elif key_text == "commit_ids":
                _extend_unique(refs["commit_ids"], _as_string_list(nested))
            elif key_text in {"commit_id", "commit_hash"}:
                _extend_unique(refs["commit_ids"], [str(nested)])
            _collect_refs(nested, refs)
    elif isinstance(value, list):
        for nested in value:
            _collect_refs(nested, refs)


def _sanitize_value(value: Any, *, path: str) -> Any:
    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        redacted_index = 1
        for key, nested in value.items():
            key_text = str(key)
            if _is_forbidden_key(key_text):
                redacted_key = "redacted_field"
                while redacted_key in sanitized:
                    redacted_index += 1
                    redacted_key = "redacted_field_{}".format(redacted_index)
                sanitized[redacted_key] = {
                    "redacted": "forbidden_payload_field",
                    "field_sha256": _hash_text(key_text),
                }
                continue
            sanitized[key_text] = _sanitize_value(nested, path="{}.{}".format(path, key_text))
        return sanitized
    if isinstance(value, list):
        items = [
            _sanitize_value(item, path="{}[{}]".format(path, index))
            for index, item in enumerate(value[:MAX_AUDIT_LIST_LENGTH])
        ]
        if len(value) > MAX_AUDIT_LIST_LENGTH:
            items.append({"redacted": "list_truncated", "omitted": len(value) - MAX_AUDIT_LIST_LENGTH})
        return items
    if isinstance(value, str) and len(value) > MAX_AUDIT_STRING_LENGTH:
        return {
            "redacted": "oversized_string",
            "length": len(value),
            "sha256": _hash_text(value),
        }
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _check_audit_payload(result: ValidationResult, value: Any, path: str) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            nested_path = "{}.{}".format(path, key_text)
            if _is_forbidden_key(key_text):
                result.add_error(
                    "PIPELINE_FORBIDDEN_AUDIT_PAYLOAD_FIELD",
                    "{} must not be stored in pipeline audit events".format(nested_path),
                    path=nested_path,
                )
            _check_audit_payload(result, nested, nested_path)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _check_audit_payload(result, nested, "{}[{}]".format(path, index))
    elif isinstance(value, str) and len(value) > MAX_AUDIT_STRING_LENGTH:
        result.add_error(
            "PIPELINE_OVERSIZED_AUDIT_PAYLOAD",
            "{} stores an oversized audit string payload".format(path),
            path=path,
        )


def _state_audit_event_ids(state: Mapping[str, Any]) -> set[str]:
    ids: set[str] = set()
    for session in state.get("sessions", []):
        if not isinstance(session, Mapping):
            continue
        _extend_unique(ids, _as_string_list(session.get("audit_event_ids")))
        for step in session.get("steps", []):
            if isinstance(step, Mapping):
                _extend_unique(ids, _as_string_list(step.get("audit_event_ids")))
    return ids


def _event_summary(event: Mapping[str, Any], payload: Mapping[str, Any], refs: Mapping[str, Any]) -> str:
    gate = _gate_from_payload(payload)
    details = _mapping(gate.get("details")) if gate else {}
    step = _mapping(payload.get("step"))
    session = _mapping(payload.get("session"))

    reason = (
        details.get("stop_reason")
        or step.get("stop_reason")
        or payload.get("stop_reason")
        or session.get("stop_reason")
        or details.get("reason")
        or ""
    )
    pieces = []
    if gate:
        pieces.append("{} {}".format(gate.get("name") or "gate", gate.get("status") or "unknown"))
    elif payload.get("status"):
        pieces.append(str(payload.get("status")))
    if refs.get("change_ids"):
        pieces.append("changes={}".format(",".join(refs["change_ids"])))
    if refs.get("report_ids"):
        pieces.append("reports={}".format(",".join(refs["report_ids"])))
    if refs.get("review_ids"):
        pieces.append("reviews={}".format(",".join(refs["review_ids"])))
    if refs.get("commit_ids"):
        pieces.append("commits={}".format(",".join(refs["commit_ids"])))
    if reason:
        pieces.append(str(reason))
    if not pieces:
        pieces.append(str(event.get("entity_id") or "pipeline event"))
    return " | ".join(pieces)


def _is_forbidden_key(key: str) -> bool:
    key_lower = key.lower()
    if key_lower in FORBIDDEN_AUDIT_PAYLOAD_KEYS:
        return True
    return (
        "secret" in key_lower
        or key_lower.endswith("_token")
        or key_lower in {"token", "credential", "credentials"}
    )


def _as_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value:
        return [value]
    return []


def _string_values(value: Any) -> list[str]:
    values: list[str] = []
    if isinstance(value, Mapping):
        for nested in value.values():
            values.extend(_string_values(nested))
    elif isinstance(value, list):
        for nested in value:
            values.extend(_string_values(nested))
    elif isinstance(value, str):
        values.append(value)
    return values


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _extend_unique(target: list[str] | set[str], values: Sequence[str]) -> None:
    if isinstance(target, set):
        for value in values:
            text = str(value)
            if text:
                target.add(text)
        return
    seen = set(target)
    for value in values:
        text = str(value)
        if text and text not in seen:
            target.append(text)
            seen.add(text)


def _dedupe(values: Sequence[str]) -> list[str]:
    result: list[str] = []
    _extend_unique(result, values)
    return result


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _markdown_cell(value: Any) -> str:
    text = str(value or "")
    return text.replace("|", "\\|").replace("\n", " ")

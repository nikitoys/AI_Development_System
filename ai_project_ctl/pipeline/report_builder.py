"""Build TaskReport payloads from trusted pipeline evidence."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Mapping, Sequence

from ai_project_ctl.task_reports import (
    REPORT_CHECK_RESULTS,
    REPORT_TOKEN_USAGE_BOOL_KEYS,
    REPORT_TOKEN_USAGE_NUMBER_KEYS,
    REPORT_TOKEN_USAGE_STRING_KEYS,
    TASK_REPORT_SCHEMA_VERSION,
)


CHECK_RESULT_BY_STATUS = {
    "ok": "pass",
    "pass": "pass",
    "passed": "pass",
    "success": "pass",
    "succeeded": "pass",
    "warn": "warn",
    "warning": "warn",
    "fail": "fail",
    "failed": "fail",
    "failure": "fail",
    "error": "error",
    "errored": "error",
    "skip": "skipped",
    "skipped": "skipped",
    "not_run": "skipped",
    "not run": "skipped",
    "not-run": "skipped",
    "blocked": "skipped",
    "unknown": "skipped",
    "planned": "skipped",
    "running": "skipped",
    "stopped": "skipped",
}

GATE_EVIDENCE_KEYS = (
    "token_budget_gate",
    "codex_adapter_gate",
    "report_gate",
    "git_diff_gate",
    "protected_files_gate",
    "allowed_files_gate",
)


class ReportBuilderError(ValueError):
    """Raised when trusted task state is not sufficient to build a report."""


def build_task_report_payload(
    *,
    session: Mapping[str, Any] | Any | None = None,
    task: Mapping[str, Any],
    adapter_result: Mapping[str, Any] | Any | None = None,
    summary: Mapping[str, Any] | None = None,
    policy_evidence: Mapping[str, Any] | Any | None = None,
) -> dict[str, Any]:
    """Assemble a TaskReport-compatible payload from non-AI schema evidence."""

    task_state = _object_mapping(task)
    task_id = _text(task_state.get("id"))
    if not task_id:
        raise ReportBuilderError("TASK_REPORT_BUILDER_TASK_ID_REQUIRED")
    task_ref = _text(task_state.get("ref"))

    summary_data = _object_mapping(summary)
    evidence = _object_mapping(policy_evidence)
    session_data = _object_mapping(session)
    adapter_data = _object_mapping(adapter_result)

    return {
        "schema_version": TASK_REPORT_SCHEMA_VERSION,
        "task_id": task_id,
        "task_ref": task_ref,
        "implementation_summary": _implementation_summary(summary_data),
        "changed_files": _changed_files(session_data, evidence),
        "generated_files": _generated_files(session_data, evidence),
        "checks": _checks(adapter_data, evidence),
        "warnings": _summary_list(summary_data.get("warnings")),
        "blockers": _summary_list(summary_data.get("blockers")),
        "notes": _summary_list(summary_data.get("notes")),
        "owner_decision_required": _owner_decision_required(session_data, evidence),
        "token_usage": _token_usage(evidence),
    }


def _implementation_summary(summary: Mapping[str, Any]) -> str:
    value = summary.get("implementation_summary")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return "Codex execution completed without a parsed implementation summary."


def _checks(
    adapter: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    adapter_check = _adapter_check(adapter)
    if adapter_check:
        checks.append(adapter_check)

    checks.extend(_evidence_checks(evidence))
    return _dedupe_checks(checks)


def _adapter_check(adapter: Mapping[str, Any]) -> dict[str, Any]:
    if not adapter:
        return {}
    status = _text(adapter.get("status") or adapter.get("result"))
    code = _text(adapter.get("code"))
    reason = _text(adapter.get("reason"))
    if not status and not code and not reason:
        return {}

    check = {
        "name": "codex_adapter",
        "command": _command_text(adapter),
        "result": _check_result(status or code),
        "duration_sec": _duration(adapter.get("duration_sec")),
        "blocking": True,
        "details": _join_details(code, reason),
    }
    return check


def _evidence_checks(evidence: Mapping[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    checks.extend(_check_list(evidence.get("checks")))
    checks.extend(_check_list(evidence.get("policy_checks")))

    gates = evidence.get("gates")
    if isinstance(gates, Sequence) and not isinstance(gates, (str, bytes, bytearray)):
        for index, gate in enumerate(gates):
            gate_check = _gate_check(
                _object_mapping(gate),
                default_name="gate_{}".format(index + 1),
            )
            if gate_check:
                checks.append(gate_check)

    for key in GATE_EVIDENCE_KEYS:
        gate_check = _gate_check(_object_mapping(evidence.get(key)), default_name=key)
        if gate_check:
            checks.append(gate_check)

    project_tests = _object_mapping(evidence.get("project_tests"))
    if project_tests:
        checks.extend(_check_list(project_tests.get("reported_checks")))
        project_check = _gate_check(project_tests, default_name="project_tests")
        if project_check:
            checks.append(project_check)

    return checks


def _check_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    checks: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        source = _object_mapping(item)
        check = _single_check(source, default_name="check_{}".format(index + 1))
        if check:
            checks.append(check)
    return checks


def _single_check(source: Mapping[str, Any], *, default_name: str) -> dict[str, Any]:
    if not source:
        return {}
    name = _text(source.get("name")) or default_name
    result_source = source.get("result", source.get("status", source.get("outcome")))
    result = _check_result(result_source)
    return {
        "name": name,
        "command": _text(source.get("command")),
        "result": result,
        "duration_sec": _duration(source.get("duration_sec")),
        "blocking": _bool(source.get("blocking"), default=False),
        "details": _join_details(source.get("code"), source.get("reason") or source.get("details")),
    }


def _gate_check(source: Mapping[str, Any], *, default_name: str) -> dict[str, Any]:
    if not source:
        return {}
    status = _text(source.get("status") or source.get("result") or source.get("outcome"))
    code = _text(source.get("code") or source.get("reason_code"))
    reason = _text(source.get("reason") or source.get("message"))
    if not status and not code and not reason:
        return {}
    return {
        "name": _text(source.get("name")) or default_name,
        "command": _text(source.get("command")),
        "result": _check_result(status or code),
        "duration_sec": _duration(source.get("duration_sec")),
        "blocking": _bool(source.get("blocking"), default=True),
        "details": _join_details(code, reason),
    }


def _check_result(value: Any) -> str:
    text = _text(value).strip().lower()
    normalized = CHECK_RESULT_BY_STATUS.get(text, text)
    if normalized in REPORT_CHECK_RESULTS:
        return normalized
    return "skipped"


def _changed_files(
    session: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> list[str]:
    values: list[str] = []
    values.extend(_string_list(evidence.get("changed_files")))
    values.extend(_string_list(_object_mapping(evidence.get("git_diff_gate")).get("actual_changed_files")))
    values.extend(_string_list(_object_mapping(evidence.get("git_diff_gate")).get("tracked_files")))
    values.extend(_string_list(session.get("changed_files")))
    return _dedupe_strings(values)


def _generated_files(
    session: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> list[str]:
    values: list[str] = []
    values.extend(_string_list(evidence.get("generated_files")))
    values.extend(
        _string_list(
            _object_mapping(evidence.get("protected_files_gate")).get(
                "allowed_protected_files"
            )
        )
    )
    values.extend(_string_list(session.get("generated_files")))
    return _dedupe_strings(values)


def _owner_decision_required(
    session: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> bool:
    if "owner_decision_required" in evidence:
        return _bool(evidence.get("owner_decision_required"), default=False)
    if "owner_decision_required" in session:
        return _bool(session.get("owner_decision_required"), default=False)
    return False


def _token_usage(evidence: Mapping[str, Any]) -> dict[str, Any]:
    token_evidence = _object_mapping(evidence.get("token_usage"))
    if not token_evidence:
        token_evidence = _object_mapping(evidence.get("token_budget_gate"))
    normalized = _normalize_token_usage(token_evidence)
    if normalized:
        return _with_token_defaults(normalized, evidence)
    return _default_token_usage(evidence)


def _normalize_token_usage(value: Mapping[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key in sorted(REPORT_TOKEN_USAGE_NUMBER_KEYS & set(value.keys())):
        number = value.get(key)
        if isinstance(number, int) and not isinstance(number, bool) and number >= 0:
            normalized[key] = number
    for key in sorted(REPORT_TOKEN_USAGE_BOOL_KEYS & set(value.keys())):
        flag = value.get(key)
        if isinstance(flag, bool):
            normalized[key] = flag
    for key in sorted(REPORT_TOKEN_USAGE_STRING_KEYS & set(value.keys())):
        text = value.get(key)
        if isinstance(text, str):
            normalized[key] = text
    return normalized


def _with_token_defaults(
    token_usage: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    result = _default_token_usage(evidence)
    result.update(token_usage)
    return result


def _default_token_usage(evidence: Mapping[str, Any]) -> dict[str, Any]:
    policy = _object_mapping(evidence.get("token_budget"))
    return {
        "prompt_tokens": 0,
        "context_tokens": 0,
        "completion_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "remaining_tokens": 0,
        "model_context_limit": 0,
        "max_context_tokens": _non_negative_int(policy.get("max_context_tokens")),
        "reserved_output_tokens": _non_negative_int(policy.get("reserved_output_tokens")),
        "min_remaining_tokens": _non_negative_int(policy.get("min_remaining_tokens")),
        "token_count_strategy": "pipeline_report_builder_default",
        "token_count_estimated": True,
        "token_count_unavailable": False,
        "token_count_unavailable_reason": (
            "Precise token evidence unavailable; defaulted to a zero-count estimate."
        ),
    }


def _summary_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _dedupe_strings(values: Sequence[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result


def _dedupe_checks(checks: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for check in checks:
        name = _text(check.get("name"))
        command = _text(check.get("command"))
        details = _text(check.get("details"))
        key = (name, command, details)
        if not name or key in seen:
            continue
        seen.add(key)
        result.append(dict(check))
    return result


def _object_mapping(value: Any) -> Mapping[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return value
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        data = to_dict()
        return data if isinstance(data, Mapping) else {}
    if is_dataclass(value):
        data = asdict(value)
        return data if isinstance(data, Mapping) else {}
    return {}


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _bool(value: Any, *, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    return default


def _duration(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0:
        return value
    return None


def _non_negative_int(value: Any) -> int:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return 0


def _command_text(source: Mapping[str, Any]) -> str:
    command_ref = _text(source.get("command_ref"))
    if command_ref:
        return command_ref
    command = source.get("command")
    if isinstance(command, Sequence) and not isinstance(command, (str, bytes, bytearray)):
        return " ".join(str(part) for part in command if str(part).strip())
    return _text(command)


def _join_details(*parts: Any) -> str:
    return " ".join(_text(part) for part in parts if _text(part))


__all__ = [
    "CHECK_RESULT_BY_STATUS",
    "ReportBuilderError",
    "build_task_report_payload",
]

"""Reusable task report submission service."""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from ai_project_ctl.core.legacy import append_audit_event, ensure_project_dirs, utc_now
from ai_project_ctl.core.paths import ProjectPaths
from ai_project_ctl.core.store import write_json_file


TASK_REPORT_SCHEMA_VERSION = 1

REPORT_TOP_LEVEL_KEYS = {
    "schema_version",
    "task_id",
    "task_ref",
    "implementation_summary",
    "changed_files",
    "generated_files",
    "checks",
    "warnings",
    "blockers",
    "notes",
    "owner_decision_required",
    "token_usage",
}
REPORT_REQUIRED_KEYS = {
    "task_id",
    "implementation_summary",
    "changed_files",
    "generated_files",
    "checks",
    "warnings",
    "blockers",
    "notes",
    "owner_decision_required",
}
REPORT_CHECK_KEYS = {
    "name",
    "command",
    "result",
    "duration_sec",
    "blocking",
    "details",
}
REPORT_CHECK_REQUIRED_KEYS = {"name", "result"}
REPORT_CHECK_RESULTS = {
    "pass",
    "passed",
    "fail",
    "failed",
    "warn",
    "warning",
    "skipped",
    "error",
}
REPORT_TOKEN_USAGE_NUMBER_KEYS = {
    "prompt_tokens",
    "context_tokens",
    "completion_tokens",
    "output_tokens",
    "total_tokens",
    "remaining_tokens",
    "model_context_limit",
    "max_context_tokens",
    "reserved_output_tokens",
    "min_remaining_tokens",
}
REPORT_TOKEN_USAGE_BOOL_KEYS = {
    "token_count_estimated",
    "token_count_unavailable",
}
REPORT_TOKEN_USAGE_STRING_KEYS = {
    "token_count_strategy",
    "token_count_unavailable_reason",
}
REPORT_TOKEN_USAGE_KEYS = (
    REPORT_TOKEN_USAGE_NUMBER_KEYS
    | REPORT_TOKEN_USAGE_BOOL_KEYS
    | REPORT_TOKEN_USAGE_STRING_KEYS
)


class TaskReportError(Exception):
    """Task report submission or validation error."""


@dataclass(frozen=True)
class TaskReportSubmission:
    report_id: str
    task_id: str
    task_ref: str
    revision_before: int
    revision_after: int
    owner_decision_required: bool
    state_path: str
    event_path: str
    source_file: str
    event_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "task_id": self.task_id,
            "task_ref": self.task_ref,
            "revision_before": self.revision_before,
            "revision_after": self.revision_after,
            "owner_decision_required": self.owner_decision_required,
            "state_path": self.state_path,
            "event_path": self.event_path,
            "source_file": self.source_file,
            "event_id": self.event_id,
        }


def task_reports_path(root: str | Path) -> Path:
    return ProjectPaths.from_root(root).state_file("task_reports.json")


def task_report_events_path(root: str | Path) -> Path:
    return ProjectPaths.from_root(root).event_file("task-report-events.jsonl")


def default_task_reports_state() -> dict[str, Any]:
    now = utc_now()
    return {
        "schema_version": TASK_REPORT_SCHEMA_VERSION,
        "revision": 0,
        "created_at": now,
        "updated_at": now,
        "reports": [],
        "latest_by_task": {},
    }


def read_report_payload(path_text: str | Path) -> dict[str, Any]:
    path = Path(path_text)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise TaskReportError("REPORT_FILE_NOT_FOUND: {}".format(path)) from exc
    except json.JSONDecodeError as exc:
        raise TaskReportError(
            "INVALID_REPORT_JSON: {}:{}:{} {}".format(
                path,
                exc.lineno,
                exc.colno,
                exc.msg,
            )
        ) from exc
    if not isinstance(payload, dict):
        raise TaskReportError("INVALID_REPORT_SCHEMA: report must be a JSON object")
    return payload


def load_task_reports(root: str | Path, required: bool = False) -> dict[str, Any]:
    path = task_reports_path(root)
    if not path.exists():
        if required:
            raise TaskReportError("TASK_REPORTS_NOT_INITIALIZED: {}".format(path))
        return default_task_reports_state()
    return _read_json(path, "TASK_REPORTS_NOT_INITIALIZED")


def save_task_reports(root: str | Path, state: Mapping[str, Any]) -> None:
    write_json_file(task_reports_path(root), state)


def submit_task_report(
    *,
    root: str | Path,
    tasks_state: Mapping[str, Any],
    task: Mapping[str, Any],
    report_payload: Mapping[str, Any],
    source_file: str | Path,
    actor: str = "human_owner",
    command: str = "task.report.submit",
) -> TaskReportSubmission:
    """Validate and persist a structured execution report for one task."""

    root_path = Path(root).resolve()
    normalized_report = normalize_task_report_payload(report_payload, task)

    report_state = load_task_reports(root_path, required=False)
    existing_errors = validate_task_reports(report_state, tasks_state)
    if existing_errors:
        raise TaskReportError(
            "TASK_REPORTS_VALIDATION_FAILED:\n- " + "\n- ".join(existing_errors)
        )

    revision_before = int(report_state.get("revision", 0))
    revision_after = revision_before + 1
    report_id = next_report_id(report_state.get("reports", []))
    submitted_at = utc_now()
    resolved_source_file = normalize_report_source(source_file)
    task_id = str(task.get("id") or "")
    task_ref = str(task.get("ref") or "")
    record = {
        "id": report_id,
        "task_id": task_id,
        "task_ref": task_ref,
        "submitted_at": submitted_at,
        "submitted_by": actor,
        "source_file": resolved_source_file,
        "report": normalized_report,
    }

    proposed = copy.deepcopy(report_state)
    proposed["revision"] = revision_after
    proposed["updated_at"] = submitted_at
    proposed.setdefault("reports", []).append(record)
    proposed.setdefault("latest_by_task", {})[task_id] = report_id

    proposed_errors = validate_task_reports(proposed, tasks_state)
    if proposed_errors:
        raise TaskReportError(
            "TASK_REPORTS_VALIDATION_FAILED:\n- " + "\n- ".join(proposed_errors)
        )

    ensure_project_dirs(root_path)
    save_task_reports(root_path, proposed)
    event_id = append_audit_event(
        task_report_events_path(root_path),
        actor=actor,
        command=command,
        entity_type="task_report",
        entity_id=report_id,
        revision_before=revision_before,
        revision_after=revision_after,
        payload={
            "task_id": task_id,
            "task_ref": task_ref,
            "report_id": report_id,
            "source_file": resolved_source_file,
            "owner_decision_required": normalized_report.get(
                "owner_decision_required"
            ),
        },
    )

    return TaskReportSubmission(
        report_id=report_id,
        task_id=task_id,
        task_ref=task_ref,
        revision_before=revision_before,
        revision_after=revision_after,
        owner_decision_required=bool(normalized_report.get("owner_decision_required")),
        state_path=str(task_reports_path(root_path)),
        event_path=str(task_report_events_path(root_path)),
        source_file=resolved_source_file,
        event_id=event_id,
    )


def next_report_id(reports: Any) -> str:
    max_num = 0
    head = "RPT-"
    if not isinstance(reports, list):
        reports = []
    for report in reports:
        if not isinstance(report, Mapping):
            continue
        report_id = str(report.get("id", ""))
        if report_id.startswith(head):
            suffix = report_id[len(head) :]
            if suffix.isdigit():
                max_num = max(max_num, int(suffix))
    return "{}{:03d}".format(head, max_num + 1)


def normalize_report_source(source_file: str | Path) -> str:
    text = str(source_file)
    if text.startswith("captured:"):
        return text
    return str(Path(source_file).resolve())


def normalize_report_token_usage(
    value: Any,
    errors: list[str],
    path: str = "report.token_usage",
) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        errors.append("{} must be an object".format(path))
        return {}

    unknown = sorted(set(value.keys()) - REPORT_TOKEN_USAGE_KEYS)
    if unknown:
        errors.append("{} has unknown field(s): {}".format(path, ", ".join(unknown)))

    normalized: dict[str, Any] = {}
    for key in sorted(REPORT_TOKEN_USAGE_NUMBER_KEYS & set(value.keys())):
        number = value.get(key)
        if not isinstance(number, int) or isinstance(number, bool) or number < 0:
            errors.append("{}.{} must be a non-negative integer".format(path, key))
        else:
            normalized[key] = number
    for key in sorted(REPORT_TOKEN_USAGE_BOOL_KEYS & set(value.keys())):
        flag = value.get(key)
        if not isinstance(flag, bool):
            errors.append("{}.{} must be a boolean".format(path, key))
        else:
            normalized[key] = flag
    for key in sorted(REPORT_TOKEN_USAGE_STRING_KEYS & set(value.keys())):
        text = value.get(key)
        if not isinstance(text, str):
            errors.append("{}.{} must be a string".format(path, key))
        else:
            normalized[key] = text
    return normalized


def normalize_task_report_payload(
    payload: Mapping[str, Any],
    task: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise TaskReportError("INVALID_REPORT_SCHEMA: report must be a JSON object")

    errors: list[str] = []
    unknown = sorted(set(payload.keys()) - REPORT_TOP_LEVEL_KEYS)
    if unknown:
        errors.append("report has unknown field(s): {}".format(", ".join(unknown)))

    missing = sorted(REPORT_REQUIRED_KEYS - set(payload.keys()))
    if missing:
        errors.append("report missing required field(s): {}".format(", ".join(missing)))

    schema_version = payload.get("schema_version", TASK_REPORT_SCHEMA_VERSION)
    if schema_version != TASK_REPORT_SCHEMA_VERSION:
        errors.append("schema_version must be {}".format(TASK_REPORT_SCHEMA_VERSION))

    task_id = payload.get("task_id")
    _require_string(task_id, "report.task_id", errors, allow_empty=False)
    if (
        isinstance(task_id, str)
        and task_id.strip()
        and not task_report_reference_matches(task, task_id)
    ):
        errors.append("report.task_id does not match target task: {}".format(task_id))

    task_ref = payload.get("task_ref", "")
    if task_ref != "":
        _require_string(task_ref, "report.task_ref", errors, allow_empty=False)
        if (
            isinstance(task_ref, str)
            and task_ref.strip()
            and not task_report_reference_matches(task, task_ref)
        ):
            errors.append("report.task_ref does not match target task: {}".format(task_ref))

    implementation_summary = payload.get("implementation_summary")
    _require_string(
        implementation_summary,
        "report.implementation_summary",
        errors,
        allow_empty=False,
    )

    for field in ["changed_files", "generated_files", "warnings", "blockers", "notes"]:
        _require_string_list(payload.get(field), "report." + field, errors)

    _require_bool(
        payload.get("owner_decision_required"),
        "report.owner_decision_required",
        errors,
    )
    token_usage = normalize_report_token_usage(payload.get("token_usage"), errors)

    checks = payload.get("checks")
    if not isinstance(checks, list):
        errors.append("report.checks must be a list")
        checks = []

    normalized_checks = []
    for index, check in enumerate(checks):
        path = "report.checks[{}]".format(index)
        if not isinstance(check, dict):
            errors.append("{} must be an object".format(path))
            continue
        unknown_check_keys = sorted(set(check.keys()) - REPORT_CHECK_KEYS)
        if unknown_check_keys:
            errors.append(
                "{} has unknown field(s): {}".format(
                    path,
                    ", ".join(unknown_check_keys),
                )
            )
        missing_check_keys = sorted(REPORT_CHECK_REQUIRED_KEYS - set(check.keys()))
        if missing_check_keys:
            errors.append(
                "{} missing required field(s): {}".format(
                    path,
                    ", ".join(missing_check_keys),
                )
            )
        _require_string(check.get("name"), path + ".name", errors, allow_empty=False)
        _require_string(check.get("result"), path + ".result", errors, allow_empty=False)
        result = str(check.get("result") or "").strip().lower()
        if result and result not in REPORT_CHECK_RESULTS:
            errors.append(
                "{}.result must be one of {}".format(
                    path,
                    ", ".join(sorted(REPORT_CHECK_RESULTS)),
                )
            )
        if "command" in check:
            _require_string(check.get("command"), path + ".command", errors)
        if "details" in check:
            _require_string(check.get("details"), path + ".details", errors)
        duration = check.get("duration_sec")
        if duration is not None:
            if (
                not isinstance(duration, (int, float))
                or isinstance(duration, bool)
                or duration < 0
            ):
                errors.append(path + ".duration_sec must be a non-negative number")
        blocking = check.get("blocking", False)
        if not isinstance(blocking, bool):
            errors.append(path + ".blocking must be a boolean")
        normalized_checks.append(
            {
                "name": str(check.get("name") or ""),
                "command": str(check.get("command") or ""),
                "result": result,
                "duration_sec": duration,
                "blocking": blocking,
                "details": str(check.get("details") or ""),
            }
        )

    if errors:
        raise TaskReportError("INVALID_REPORT_SCHEMA:\n- " + "\n- ".join(errors))

    return {
        "schema_version": TASK_REPORT_SCHEMA_VERSION,
        "task_id": task.get("id"),
        "task_ref": task.get("ref") or "",
        "reported_task_id": task_id,
        "reported_task_ref": task_ref,
        "implementation_summary": implementation_summary,
        "changed_files": list(payload.get("changed_files") or []),
        "generated_files": list(payload.get("generated_files") or []),
        "checks": normalized_checks,
        "warnings": list(payload.get("warnings") or []),
        "blockers": list(payload.get("blockers") or []),
        "notes": list(payload.get("notes") or []),
        "owner_decision_required": payload.get("owner_decision_required"),
        "token_usage": token_usage,
    }


def validate_task_reports(
    report_state: Mapping[str, Any],
    tasks_state: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    _require_keys(
        report_state,
        [
            "schema_version",
            "revision",
            "created_at",
            "updated_at",
            "reports",
            "latest_by_task",
        ],
        "task_reports_state",
        errors,
    )
    if errors:
        return errors

    if report_state.get("schema_version") != TASK_REPORT_SCHEMA_VERSION:
        errors.append(
            "task_reports.schema_version must be {}".format(
                TASK_REPORT_SCHEMA_VERSION
            )
        )
    if not isinstance(report_state.get("revision"), int) or report_state.get("revision") < 0:
        errors.append("task_reports.revision must be a non-negative integer")
    _require_string(report_state.get("created_at"), "task_reports.created_at", errors)
    _require_string(report_state.get("updated_at"), "task_reports.updated_at", errors)

    reports = report_state.get("reports")
    if not isinstance(reports, list):
        errors.append("task_reports.reports must be a list")
        reports = []
    latest_by_task = report_state.get("latest_by_task")
    if not isinstance(latest_by_task, dict):
        errors.append("task_reports.latest_by_task must be an object")
        latest_by_task = {}

    tasks_by_id = _task_id_map(tasks_state.get("tasks", []))
    reports_by_id = {}

    for index, record in enumerate(reports):
        path = "task_reports.reports[{}]".format(index)
        _require_keys(
            record,
            [
                "id",
                "task_id",
                "task_ref",
                "submitted_at",
                "submitted_by",
                "source_file",
                "report",
            ],
            path,
            errors,
        )
        if not isinstance(record, dict):
            continue
        report_id = record.get("id")
        _require_string(report_id, path + ".id", errors, allow_empty=False)
        if isinstance(report_id, str) and report_id.strip():
            if report_id in reports_by_id:
                errors.append("duplicate task report id: {}".format(report_id))
            else:
                reports_by_id[report_id] = record

        task_id = record.get("task_id")
        _require_string(task_id, path + ".task_id", errors, allow_empty=False)
        if isinstance(task_id, str) and task_id.strip() and task_id not in tasks_by_id:
            errors.append("{}.task_id references missing task: {}".format(path, task_id))

        for field in ["task_ref", "submitted_at", "submitted_by", "source_file"]:
            _require_string(record.get(field), path + "." + field, errors)

        report = record.get("report")
        if not isinstance(report, dict):
            errors.append(path + ".report must be an object")
            continue

        report_task_id = report.get("task_id")
        if report_task_id != task_id:
            errors.append(path + ".report.task_id must match record task_id")

        for field in ["changed_files", "generated_files", "warnings", "blockers", "notes"]:
            _require_string_list(report.get(field), path + ".report." + field, errors)
        _require_string(
            report.get("implementation_summary"),
            path + ".report.implementation_summary",
            errors,
            allow_empty=False,
        )
        _require_bool(
            report.get("owner_decision_required"),
            path + ".report.owner_decision_required",
            errors,
        )
        normalize_report_token_usage(
            report.get("token_usage"),
            errors,
            path=path + ".report.token_usage",
        )
        checks = report.get("checks")
        if not isinstance(checks, list):
            errors.append(path + ".report.checks must be a list")
        else:
            for check_index, check in enumerate(checks):
                check_path = "{}.report.checks[{}]".format(path, check_index)
                if not isinstance(check, dict):
                    errors.append(check_path + " must be an object")
                    continue
                _require_string(
                    check.get("name"),
                    check_path + ".name",
                    errors,
                    allow_empty=False,
                )
                _require_string(
                    check.get("result"),
                    check_path + ".result",
                    errors,
                    allow_empty=False,
                )

    for task_id, report_id in latest_by_task.items():
        if not isinstance(task_id, str) or not task_id.strip():
            errors.append("task_reports.latest_by_task keys must be non-empty strings")
            continue
        if not isinstance(report_id, str) or not report_id.strip():
            errors.append(
                "task_reports.latest_by_task[{}] must be a non-empty string".format(
                    task_id
                )
            )
            continue
        report = reports_by_id.get(report_id)
        if report is None:
            errors.append(
                "task_reports.latest_by_task[{}] references missing report: {}".format(
                    task_id,
                    report_id,
                )
            )
        elif report.get("task_id") != task_id:
            errors.append(
                "task_reports.latest_by_task[{}] points to report for {}".format(
                    task_id,
                    report.get("task_id"),
                )
            )

    return errors


def task_report_reference_matches(task: Mapping[str, Any], value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    return value.strip() in set(_task_reference_values(task))


def _read_json(path: Path, missing_message: str) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise TaskReportError(missing_message) from exc
    except json.JSONDecodeError as exc:
        raise TaskReportError(
            "INVALID_JSON: {}:{}:{} {}".format(path, exc.lineno, exc.colno, exc.msg)
        ) from exc


def _require_keys(obj: Any, keys: list[str], path: str, errors: list[str]) -> None:
    if not isinstance(obj, dict):
        errors.append("{} must be an object".format(path))
        return

    for key in keys:
        if key not in obj:
            errors.append("{} missing required key `{}`".format(path, key))


def _require_string(
    value: Any,
    path: str,
    errors: list[str],
    allow_empty: bool = True,
) -> None:
    if not isinstance(value, str):
        errors.append("{} must be a string".format(path))
        return

    if not allow_empty and not value.strip():
        errors.append("{} must not be empty".format(path))


def _require_string_list(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("{} must be a list".format(path))
        return

    for index, item in enumerate(value):
        if not isinstance(item, str):
            errors.append("{}[{}] must be a string".format(path, index))


def _require_bool(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, bool):
        errors.append("{} must be a boolean".format(path))


def _task_reference_values(task: Mapping[str, Any]):
    for field in ["id", "uid", "ref", "legacy_id"]:
        value = task.get(field)

        if isinstance(value, str) and value.strip():
            yield value

    aliases = task.get("aliases", [])

    if isinstance(aliases, list):
        for alias in aliases:
            if isinstance(alias, str) and alias.strip():
                yield alias


def _task_id_map(tasks: Any) -> dict[str, Mapping[str, Any]]:
    return {
        task.get("id"): task
        for task in tasks
        if isinstance(task, dict) and isinstance(task.get("id"), str) and task.get("id")
    }

"""Codex execution report gate for supervised pipeline runs."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from ai_project_ctl.core.store import read_json_file

from .policy import PipelinePolicy
from .state import task_reports_state_path


PASS = "pass"
WARN = "warn"
FAIL = "fail"

CODE_PASS = "CODEX_REPORT_PASS"
CODE_WARN = "CODEX_REPORT_WARN"
CODE_REPORT_MISSING = "CODEX_REPORT_MISSING"
CODE_INVALID_SCHEMA = "CODEX_REPORT_INVALID_SCHEMA"
CODE_TASK_MISMATCH = "CODEX_REPORT_TASK_MISMATCH"
CODE_BLOCKERS_PRESENT = "CODEX_REPORT_BLOCKERS_PRESENT"
CODE_TOKEN_USAGE_REQUIRED = "CODEX_REPORT_TOKEN_USAGE_REQUIRED"
CODE_OUT_OF_SCOPE_FILE = "CODEX_REPORT_OUT_OF_SCOPE_FILE"
CODE_BLOCKING_CHECK_FAILED = "CODEX_REPORT_BLOCKING_CHECK_FAILED"

REPORT_SCHEMA_VERSION = 1
FAIL_CHECK_RESULTS = {"fail", "failed", "error"}
WARN_CHECK_RESULTS = {"warn", "warning", "skipped"}
CHECK_RESULTS = FAIL_CHECK_RESULTS | WARN_CHECK_RESULTS | {"pass", "passed"}

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
REPORT_ALLOWED_KEYS = REPORT_REQUIRED_KEYS | {
    "schema_version",
    "task_ref",
    "reported_task_id",
    "reported_task_ref",
    "token_usage",
}
CHECK_REQUIRED_KEYS = {"name", "result"}
CHECK_ALLOWED_KEYS = {
    "name",
    "command",
    "result",
    "duration_sec",
    "blocking",
    "details",
}
TOKEN_USAGE_REQUIRED_KEYS = {
    "prompt_tokens",
    "context_tokens",
    "token_count_strategy",
    "token_count_estimated",
}
TOKEN_USAGE_NUMBER_KEYS = {
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
TOKEN_USAGE_BOOL_KEYS = {"token_count_estimated", "token_count_unavailable"}
TOKEN_USAGE_STRING_KEYS = {
    "token_count_strategy",
    "token_count_unavailable_reason",
}
TOKEN_USAGE_ALLOWED_KEYS = (
    TOKEN_USAGE_NUMBER_KEYS | TOKEN_USAGE_BOOL_KEYS | TOKEN_USAGE_STRING_KEYS
)


@dataclass(frozen=True)
class ReportGateIssue:
    code: str
    message: str
    path: str = ""

    def to_dict(self) -> dict[str, str]:
        data = {"code": self.code, "message": self.message}
        if self.path:
            data["path"] = self.path
        return data


@dataclass(frozen=True)
class ReportGateResult:
    status: str
    code: str
    reason: str
    report_id: str
    task_id: str
    issues: tuple[ReportGateIssue, ...] = ()
    warnings: tuple[ReportGateIssue, ...] = ()
    changed_files: tuple[str, ...] = ()
    generated_files: tuple[str, ...] = ()
    token_usage: Mapping[str, Any] | None = None
    checks: tuple[Mapping[str, Any], ...] = ()

    @property
    def ok(self) -> bool:
        return self.status in {PASS, WARN}

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "code": self.code,
            "reason": self.reason,
            "report_id": self.report_id,
            "task_id": self.task_id,
            "issues": [issue.to_dict() for issue in self.issues],
            "warnings": [warning.to_dict() for warning in self.warnings],
            "changed_files": list(self.changed_files),
            "generated_files": list(self.generated_files),
            "token_usage": dict(self.token_usage or {}),
            "checks": [dict(check) for check in self.checks],
        }


@dataclass(frozen=True)
class ReportGateAcceptance:
    allow: bool
    reason: str
    policy: str
    report_gate_status: str
    report_gate_code: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "allow": self.allow,
            "reason": self.reason,
            "policy": self.policy,
            "report_gate_status": self.report_gate_status,
            "report_gate_code": self.report_gate_code,
        }


def evaluate_report_gate_acceptance(
    report_gate: ReportGateResult,
    policy: PipelinePolicy,
) -> ReportGateAcceptance:
    """Decide whether a report gate result may continue to downstream phases."""

    if report_gate.status == PASS and report_gate.code == CODE_PASS:
        return ReportGateAcceptance(
            allow=True,
            reason="Report gate passed.",
            policy="report_gate_pass_allows_downstream",
            report_gate_status=report_gate.status,
            report_gate_code=report_gate.code,
        )

    if report_gate.status == WARN and report_gate.code == CODE_WARN:
        allow = bool(policy.verify.allow_report_warnings)
        return ReportGateAcceptance(
            allow=allow,
            reason=(
                "policy.verify.allow_report_warnings is true"
                if allow
                else "policy.verify.allow_report_warnings is false"
            ),
            policy=(
                "report_gate_warn_allowed_by_policy"
                if allow
                else "report_gate_warn_blocks_downstream"
            ),
            report_gate_status=report_gate.status,
            report_gate_code=report_gate.code,
        )

    return ReportGateAcceptance(
        allow=False,
        reason=report_gate.reason,
        policy="report_gate_result_blocks_downstream",
        report_gate_status=report_gate.status,
        report_gate_code=report_gate.code,
    )


def evaluate_report_gate(
    *,
    root: str | Path,
    task: Mapping[str, Any],
    policy: PipelinePolicy,
) -> ReportGateResult:
    """Validate the latest structured Codex report for one selected task."""

    task_id = str(task.get("id") or "")
    if not task_id:
        return _fail(
            CODE_INVALID_SCHEMA,
            "Selected task has no stable task id.",
            task_id=task_id,
            report_id="",
        )

    record_result = _latest_report_record(Path(root).resolve(), task_id)
    if isinstance(record_result, ReportGateResult):
        return record_result
    record = record_result
    report_id = str(record.get("id") or "")
    report = record.get("report")

    issues: list[ReportGateIssue] = []
    warnings: list[ReportGateIssue] = []
    if not isinstance(report, Mapping):
        issues.append(
            ReportGateIssue(
                CODE_INVALID_SCHEMA,
                "Latest task report record does not contain a structured report object.",
                "report",
            )
        )
        return _finish(
            task_id=task_id,
            report_id=report_id,
            issues=issues,
            warnings=warnings,
            changed_files=(),
            generated_files=(),
            token_usage={},
        )

    _validate_report_schema(report, task, policy=policy, issues=issues, warnings=warnings)

    changed_files = tuple(_string_list(report.get("changed_files")))
    generated_files = tuple(_string_list(report.get("generated_files")))
    _validate_file_scope(
        changed_files,
        generated_files,
        task,
        issues=issues,
    )

    blockers = _string_list(report.get("blockers"))
    if blockers:
        issues.append(
            ReportGateIssue(
                CODE_BLOCKERS_PRESENT,
                "Report contains blocker(s): {}".format("; ".join(blockers)),
                "blockers",
            )
        )

    report_checks = _report_checks(report.get("checks"))
    _validate_checks(report.get("checks"), issues=issues, warnings=warnings)

    report_warnings = _string_list(report.get("warnings"))
    if report_warnings:
        warnings.append(
            ReportGateIssue(
                CODE_WARN,
                "Report contains warning(s): {}".format("; ".join(report_warnings)),
                "warnings",
            )
        )
    if report.get("owner_decision_required") is True:
        warnings.append(
            ReportGateIssue(
                CODE_WARN,
                "Report marks owner_decision_required as true.",
                "owner_decision_required",
            )
        )

    return _finish(
        task_id=task_id,
        report_id=report_id,
        issues=issues,
        warnings=warnings,
        changed_files=changed_files,
        generated_files=generated_files,
        token_usage=_mapping_or_empty(report.get("token_usage")),
        checks=report_checks,
    )


def _latest_report_record(root: Path, task_id: str) -> Mapping[str, Any] | ReportGateResult:
    path = task_reports_state_path(root)
    if not path.exists():
        return _fail(
            CODE_REPORT_MISSING,
            "No task report state exists for selected task.",
            task_id=task_id,
            report_id="",
        )
    data = read_json_file(path)
    if not isinstance(data, Mapping):
        return _fail(
            CODE_INVALID_SCHEMA,
            "Task report state is not an object.",
            task_id=task_id,
            report_id="",
        )
    reports = data.get("reports")
    if not isinstance(reports, list):
        return _fail(
            CODE_INVALID_SCHEMA,
            "task_reports.reports must be a list.",
            task_id=task_id,
            report_id="",
        )

    latest = data.get("latest_by_task")
    if isinstance(latest, Mapping):
        report_id = latest.get(task_id)
        if isinstance(report_id, str) and report_id.strip():
            for record in reports:
                if isinstance(record, Mapping) and record.get("id") == report_id:
                    return record
            return _fail(
                CODE_REPORT_MISSING,
                "latest_by_task points to a missing report: {}".format(report_id),
                task_id=task_id,
                report_id=report_id,
            )

    matches = [
        record
        for record in reports
        if isinstance(record, Mapping) and record.get("task_id") == task_id
    ]
    if not matches:
        return _fail(
            CODE_REPORT_MISSING,
            "No structured execution report exists for selected task.",
            task_id=task_id,
            report_id="",
        )
    matches.sort(key=lambda item: str(item.get("submitted_at") or ""))
    return matches[-1]


def _validate_report_schema(
    report: Mapping[str, Any],
    task: Mapping[str, Any],
    *,
    policy: PipelinePolicy,
    issues: list[ReportGateIssue],
    warnings: list[ReportGateIssue],
) -> None:
    unknown = sorted(set(report.keys()) - REPORT_ALLOWED_KEYS)
    if unknown:
        issues.append(
            ReportGateIssue(
                CODE_INVALID_SCHEMA,
                "Report has unknown field(s): {}".format(", ".join(unknown)),
                "report",
            )
        )

    missing = sorted(REPORT_REQUIRED_KEYS - set(report.keys()))
    if missing:
        issues.append(
            ReportGateIssue(
                CODE_INVALID_SCHEMA,
                "Report missing required field(s): {}".format(", ".join(missing)),
                "report",
            )
        )

    schema_version = report.get("schema_version", REPORT_SCHEMA_VERSION)
    if schema_version != REPORT_SCHEMA_VERSION:
        issues.append(
            ReportGateIssue(
                CODE_INVALID_SCHEMA,
                "schema_version must be {}".format(REPORT_SCHEMA_VERSION),
                "schema_version",
            )
        )

    task_id = str(task.get("id") or "")
    task_ref = str(task.get("ref") or "")
    if report.get("task_id") != task_id:
        issues.append(
            ReportGateIssue(
                CODE_TASK_MISMATCH,
                "report.task_id does not match selected task: {}".format(report.get("task_id")),
                "task_id",
            )
        )
    reported_task_id = report.get("reported_task_id")
    if isinstance(reported_task_id, str) and reported_task_id.strip():
        if not _task_reference_matches(task, reported_task_id):
            issues.append(
                ReportGateIssue(
                    CODE_TASK_MISMATCH,
                    "report.reported_task_id does not match selected task: {}".format(
                        reported_task_id
                    ),
                    "reported_task_id",
                )
            )
    report_task_ref = report.get("task_ref", "")
    if report_task_ref and task_ref and report_task_ref != task_ref:
        issues.append(
            ReportGateIssue(
                CODE_TASK_MISMATCH,
                "report.task_ref does not match selected task: {}".format(report_task_ref),
                "task_ref",
            )
        )
    reported_task_ref = report.get("reported_task_ref")
    if isinstance(reported_task_ref, str) and reported_task_ref.strip():
        if not _task_reference_matches(task, reported_task_ref):
            issues.append(
                ReportGateIssue(
                    CODE_TASK_MISMATCH,
                    "report.reported_task_ref does not match selected task: {}".format(
                        reported_task_ref
                    ),
                    "reported_task_ref",
                )
            )

    _require_string(report.get("implementation_summary"), "implementation_summary", issues)
    for field in ("changed_files", "generated_files", "warnings", "blockers", "notes"):
        if not _is_string_list(report.get(field)):
            issues.append(
                ReportGateIssue(
                    CODE_INVALID_SCHEMA,
                    "report.{} must be a list of strings".format(field),
                    field,
                )
            )
    if not isinstance(report.get("owner_decision_required"), bool):
        issues.append(
            ReportGateIssue(
                CODE_INVALID_SCHEMA,
                "report.owner_decision_required must be a boolean",
                "owner_decision_required",
            )
        )

    checks = report.get("checks")
    if not isinstance(checks, list):
        issues.append(
            ReportGateIssue(
                CODE_INVALID_SCHEMA,
                "report.checks must be a list",
                "checks",
            )
        )

    token_usage = report.get("token_usage")
    if policy.token_budget.require_gate_pass:
        _validate_token_usage(token_usage, issues=issues, required=True)
    elif token_usage is not None:
        _validate_token_usage(token_usage, issues=issues, required=False)

    if not report.get("checks"):
        warnings.append(
            ReportGateIssue(
                CODE_WARN,
                "Report includes no verification checks.",
                "checks",
            )
        )


def _validate_checks(
    checks: Any,
    *,
    issues: list[ReportGateIssue],
    warnings: list[ReportGateIssue],
) -> None:
    if not isinstance(checks, list):
        return
    for index, check in enumerate(checks):
        path = "checks[{}]".format(index)
        if not isinstance(check, Mapping):
            issues.append(
                ReportGateIssue(CODE_INVALID_SCHEMA, "{} must be an object".format(path), path)
            )
            continue
        unknown = sorted(set(check.keys()) - CHECK_ALLOWED_KEYS)
        if unknown:
            issues.append(
                ReportGateIssue(
                    CODE_INVALID_SCHEMA,
                    "{} has unknown field(s): {}".format(path, ", ".join(unknown)),
                    path,
                )
            )
        missing = sorted(CHECK_REQUIRED_KEYS - set(check.keys()))
        if missing:
            issues.append(
                ReportGateIssue(
                    CODE_INVALID_SCHEMA,
                    "{} missing required field(s): {}".format(path, ", ".join(missing)),
                    path,
                )
            )
        _require_string(check.get("name"), path + ".name", issues)
        _require_string(check.get("result"), path + ".result", issues)
        result = str(check.get("result") or "").strip().lower()
        if result and result not in CHECK_RESULTS:
            issues.append(
                ReportGateIssue(
                    CODE_INVALID_SCHEMA,
                    "{}.result is not a recognized check result: {}".format(path, result),
                    path + ".result",
                )
            )
        duration = check.get("duration_sec")
        if duration is not None:
            if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration < 0:
                issues.append(
                    ReportGateIssue(
                        CODE_INVALID_SCHEMA,
                        "{}.duration_sec must be a non-negative number".format(path),
                        path + ".duration_sec",
                    )
                )
        blocking = check.get("blocking", False)
        if not isinstance(blocking, bool):
            issues.append(
                ReportGateIssue(
                    CODE_INVALID_SCHEMA,
                    "{}.blocking must be a boolean".format(path),
                    path + ".blocking",
                )
            )
        if result in FAIL_CHECK_RESULTS and blocking is True:
            issues.append(
                ReportGateIssue(
                    CODE_BLOCKING_CHECK_FAILED,
                    "{} is a blocking failed check: {}".format(path, result),
                    path,
                )
            )
        elif result in WARN_CHECK_RESULTS:
            warnings.append(
                ReportGateIssue(
                    CODE_WARN,
                    "{} reported {}".format(path, result),
                    path,
                )
            )


def _report_checks(value: Any) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, list):
        return ()
    return tuple(dict(item) for item in value if isinstance(item, Mapping))


def _validate_token_usage(
    token_usage: Any,
    *,
    issues: list[ReportGateIssue],
    required: bool,
) -> None:
    if token_usage is None:
        if required:
            issues.append(
                ReportGateIssue(
                    CODE_TOKEN_USAGE_REQUIRED,
                    "Report token_usage is required by the pipeline token policy.",
                    "token_usage",
                )
            )
        return
    if not isinstance(token_usage, Mapping):
        issues.append(
            ReportGateIssue(
                CODE_INVALID_SCHEMA,
                "report.token_usage must be an object",
                "token_usage",
            )
        )
        return

    if required:
        missing = sorted(TOKEN_USAGE_REQUIRED_KEYS - set(token_usage.keys()))
        if missing:
            issues.append(
                ReportGateIssue(
                    CODE_TOKEN_USAGE_REQUIRED,
                    "report.token_usage missing required field(s): {}".format(
                        ", ".join(missing)
                    ),
                    "token_usage",
                )
            )

    unknown = sorted(set(token_usage.keys()) - TOKEN_USAGE_ALLOWED_KEYS)
    if unknown:
        issues.append(
            ReportGateIssue(
                CODE_INVALID_SCHEMA,
                "report.token_usage has unknown field(s): {}".format(", ".join(unknown)),
                "token_usage",
            )
        )

    for field in sorted(TOKEN_USAGE_NUMBER_KEYS & set(token_usage.keys())):
        value = token_usage.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            issues.append(
                ReportGateIssue(
                    CODE_INVALID_SCHEMA,
                    "report.token_usage.{} must be a non-negative integer".format(field),
                    "token_usage." + field,
                )
            )
    for field in sorted(TOKEN_USAGE_BOOL_KEYS & set(token_usage.keys())):
        if not isinstance(token_usage.get(field), bool):
            issues.append(
                ReportGateIssue(
                    CODE_INVALID_SCHEMA,
                    "report.token_usage.{} must be a boolean".format(field),
                    "token_usage." + field,
                )
            )
    for field in sorted(TOKEN_USAGE_STRING_KEYS & set(token_usage.keys())):
        value = token_usage.get(field)
        if not isinstance(value, str):
            issues.append(
                ReportGateIssue(
                    CODE_INVALID_SCHEMA,
                    "report.token_usage.{} must be a string".format(field),
                    "token_usage." + field,
                )
            )
    if token_usage.get("token_count_unavailable") is True and required:
        issues.append(
            ReportGateIssue(
                CODE_TOKEN_USAGE_REQUIRED,
                "Token usage cannot be unavailable when policy requires token evidence.",
                "token_usage.token_count_unavailable",
            )
        )


def _validate_file_scope(
    changed_files: Sequence[str],
    generated_files: Sequence[str],
    task: Mapping[str, Any],
    *,
    issues: list[ReportGateIssue],
) -> None:
    allowed_patterns = _allowed_file_patterns(task.get("allowed_files"))
    generated_set = {_normalize_reported_path(path) for path in generated_files}
    for path in changed_files:
        normalized = _normalize_reported_path(path)
        if _matches_allowed_file(normalized, allowed_patterns):
            continue
        if normalized in generated_set:
            continue
        if _is_governed_project_output(normalized):
            continue
        issues.append(
            ReportGateIssue(
                CODE_OUT_OF_SCOPE_FILE,
                "Changed file is outside task allowed_files: {}".format(path),
                "changed_files",
            )
        )

    for path in generated_files:
        normalized = _normalize_reported_path(path)
        if _matches_allowed_file(normalized, allowed_patterns):
            continue
        if _is_governed_project_output(normalized):
            continue
        issues.append(
            ReportGateIssue(
                CODE_OUT_OF_SCOPE_FILE,
                "Generated file is outside governed output or task allowed_files: {}".format(path),
                "generated_files",
            )
        )


def _allowed_file_patterns(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    patterns: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        pattern = item.strip()
        if not pattern:
            continue
        if " if " in pattern:
            pattern = pattern.split(" if ", 1)[0].strip()
        patterns.append(_normalize_reported_path(pattern))
    return tuple(patterns)


def _matches_allowed_file(path: str, patterns: Sequence[str]) -> bool:
    for pattern in patterns:
        if pattern.endswith("/**"):
            prefix = pattern[:-3].rstrip("/")
            if path == prefix or path.startswith(prefix + "/"):
                return True
        if fnmatch.fnmatchcase(path, pattern):
            return True
    return False


def _is_governed_project_output(path: str) -> bool:
    return path.startswith("AI_PROJECT/state/") or path.startswith(
        "AI_PROJECT/events/"
    ) or path.startswith("AI_PROJECT/generated/")


def _task_reference_matches(task: Mapping[str, Any], ref: str) -> bool:
    candidates = {
        str(task.get("id") or ""),
        str(task.get("ref") or ""),
        str(task.get("uid") or ""),
        str(task.get("legacy_id") or ""),
    }
    aliases = task.get("aliases")
    if isinstance(aliases, list):
        candidates.update(str(alias) for alias in aliases if alias)
    return ref in candidates


def _require_string(value: Any, path: str, issues: list[ReportGateIssue]) -> None:
    if not isinstance(value, str) or not value.strip():
        issues.append(
            ReportGateIssue(
                CODE_INVALID_SCHEMA,
                "report.{} must be a non-empty string".format(path),
                path,
            )
        )


def _is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str)]


def _mapping_or_empty(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _normalize_reported_path(path: str) -> str:
    text = str(path).strip().replace("\\", "/")
    marker = "/AI_PROJECT/"
    if marker in text:
        return "AI_PROJECT/" + text.split(marker, 1)[1]
    if text.startswith("./"):
        text = text[2:]
    return text.lstrip("/")


def _finish(
    *,
    task_id: str,
    report_id: str,
    issues: Sequence[ReportGateIssue],
    warnings: Sequence[ReportGateIssue],
    changed_files: Sequence[str],
    generated_files: Sequence[str],
    token_usage: Mapping[str, Any],
    checks: Sequence[Mapping[str, Any]] = (),
) -> ReportGateResult:
    if issues:
        return ReportGateResult(
            status=FAIL,
            code=issues[0].code,
            reason=issues[0].message,
            report_id=report_id,
            task_id=task_id,
            issues=tuple(issues),
            warnings=tuple(warnings),
            changed_files=tuple(changed_files),
            generated_files=tuple(generated_files),
            token_usage=token_usage,
            checks=tuple(dict(check) for check in checks),
        )
    if warnings:
        return ReportGateResult(
            status=WARN,
            code=CODE_WARN,
            reason=warnings[0].message,
            report_id=report_id,
            task_id=task_id,
            warnings=tuple(warnings),
            changed_files=tuple(changed_files),
            generated_files=tuple(generated_files),
            token_usage=token_usage,
            checks=tuple(dict(check) for check in checks),
        )
    return ReportGateResult(
        status=PASS,
        code=CODE_PASS,
        reason="Structured Codex execution report passed gate checks.",
        report_id=report_id,
        task_id=task_id,
        changed_files=tuple(changed_files),
        generated_files=tuple(generated_files),
        token_usage=token_usage,
        checks=tuple(dict(check) for check in checks),
    )


def _fail(code: str, reason: str, *, task_id: str, report_id: str) -> ReportGateResult:
    issue = ReportGateIssue(code, reason)
    return ReportGateResult(
        status=FAIL,
        code=code,
        reason=reason,
        report_id=report_id,
        task_id=task_id,
        issues=(issue,),
    )

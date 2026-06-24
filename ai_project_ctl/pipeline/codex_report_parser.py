"""Parse structured Codex execution reports from local-command stdout."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Mapping


REPORT_MARKER = "CODEX_REPORT_JSON:"

CODEX_REPORT_PARSE_OK = "CODEX_REPORT_PARSE_OK"
CODEX_REPORT_BLOCK_MISSING = "CODEX_REPORT_BLOCK_MISSING"
CODEX_REPORT_BLOCK_DUPLICATE = "CODEX_REPORT_BLOCK_DUPLICATE"
CODEX_REPORT_BLOCK_MALFORMED = "CODEX_REPORT_BLOCK_MALFORMED"
CODEX_REPORT_JSON_MALFORMED = "CODEX_REPORT_JSON_MALFORMED"
CODEX_REPORT_JSON_NOT_OBJECT = "CODEX_REPORT_JSON_NOT_OBJECT"
CODEX_REPORT_FIELDS_MISSING = "CODEX_REPORT_FIELDS_MISSING"
CODEX_REPORT_FIELDS_UNKNOWN = "CODEX_REPORT_FIELDS_UNKNOWN"

EXPECTED_REPORT_FIELDS = frozenset(
    {
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
)

_MARKER_LINE_RE = re.compile(r"(?m)^CODEX_REPORT_JSON:[ \t]*$")
_REPORT_BLOCK_RE = re.compile(
    r"(?ms)^CODEX_REPORT_JSON:[ \t]*\r?\n"
    r"```json[ \t]*\r?\n"
    r"(?P<json>.*?)"
    r"\r?\n```[ \t]*(?:\r?\n)?"
)


@dataclass(frozen=True)
class CodexReportParseIssue:
    """Stable parse issue for machine callers and tests."""

    code: str
    message: str
    details: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.details:
            data["details"] = dict(self.details)
        return data


@dataclass(frozen=True)
class CodexReportParseResult:
    """Result of extracting the structured report block from stdout."""

    ok: bool
    code: str
    report: Mapping[str, Any] | None = None
    issue: CodexReportParseIssue | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "ok": self.ok,
            "code": self.code,
            "report": dict(self.report or {}),
        }
        if self.issue is not None:
            data["issue"] = self.issue.to_dict()
        return data


def parse_codex_report_stdout(stdout: str) -> CodexReportParseResult:
    """Extract and validate one explicit structured report JSON block."""

    text = stdout or ""
    marker_count = len(_MARKER_LINE_RE.findall(text))
    if marker_count == 0:
        return _failure(
            CODEX_REPORT_BLOCK_MISSING,
            "No CODEX_REPORT_JSON report block was found in stdout.",
        )
    if marker_count > 1:
        return _failure(
            CODEX_REPORT_BLOCK_DUPLICATE,
            "Multiple CODEX_REPORT_JSON report markers were found in stdout.",
            marker_count=marker_count,
        )

    matches = list(_REPORT_BLOCK_RE.finditer(text))
    if not matches:
        return _failure(
            CODEX_REPORT_BLOCK_MALFORMED,
            "The CODEX_REPORT_JSON marker was not followed by one fenced json block.",
        )
    if len(matches) > 1:
        return _failure(
            CODEX_REPORT_BLOCK_DUPLICATE,
            "Multiple CODEX_REPORT_JSON report blocks were found in stdout.",
            block_count=len(matches),
        )

    json_text = matches[0].group("json").strip()
    try:
        decoded = json.loads(json_text)
    except json.JSONDecodeError as exc:
        return _failure(
            CODEX_REPORT_JSON_MALFORMED,
            "The CODEX_REPORT_JSON block does not contain valid JSON.",
            line=exc.lineno,
            column=exc.colno,
            error=exc.msg,
        )

    if not isinstance(decoded, dict):
        return _failure(
            CODEX_REPORT_JSON_NOT_OBJECT,
            "The CODEX_REPORT_JSON value must be a JSON object.",
            value_type=type(decoded).__name__,
        )

    fields = set(decoded)
    missing = sorted(EXPECTED_REPORT_FIELDS - fields)
    if missing:
        return _failure(
            CODEX_REPORT_FIELDS_MISSING,
            "The CODEX_REPORT_JSON object is missing expected top-level fields.",
            missing=missing,
        )

    unknown = sorted(fields - EXPECTED_REPORT_FIELDS)
    if unknown:
        return _failure(
            CODEX_REPORT_FIELDS_UNKNOWN,
            "The CODEX_REPORT_JSON object contains unknown top-level fields.",
            unknown=unknown,
        )

    return CodexReportParseResult(
        ok=True,
        code=CODEX_REPORT_PARSE_OK,
        report=decoded,
    )


def _failure(code: str, message: str, **details: Any) -> CodexReportParseResult:
    return CodexReportParseResult(
        ok=False,
        code=code,
        issue=CodexReportParseIssue(code=code, message=message, details=details),
    )


__all__ = [
    "CODEX_REPORT_BLOCK_DUPLICATE",
    "CODEX_REPORT_BLOCK_MALFORMED",
    "CODEX_REPORT_BLOCK_MISSING",
    "CODEX_REPORT_FIELDS_MISSING",
    "CODEX_REPORT_FIELDS_UNKNOWN",
    "CODEX_REPORT_JSON_MALFORMED",
    "CODEX_REPORT_JSON_NOT_OBJECT",
    "CODEX_REPORT_PARSE_OK",
    "CodexReportParseIssue",
    "CodexReportParseResult",
    "EXPECTED_REPORT_FIELDS",
    "REPORT_MARKER",
    "parse_codex_report_stdout",
]

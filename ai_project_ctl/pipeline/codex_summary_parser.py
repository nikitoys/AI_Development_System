"""Parse minimal Codex execution summaries from local-command stdout."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Mapping


SUMMARY_MARKER = "CODEX_EXECUTION_SUMMARY_JSON:"

CODEX_SUMMARY_PARSE_OK = "CODEX_SUMMARY_PARSE_OK"
CODEX_SUMMARY_BLOCK_MISSING = "CODEX_SUMMARY_BLOCK_MISSING"
CODEX_SUMMARY_BLOCK_DUPLICATE = "CODEX_SUMMARY_BLOCK_DUPLICATE"
CODEX_SUMMARY_BLOCK_MALFORMED = "CODEX_SUMMARY_BLOCK_MALFORMED"
CODEX_SUMMARY_JSON_MALFORMED = "CODEX_SUMMARY_JSON_MALFORMED"
CODEX_SUMMARY_JSON_NOT_OBJECT = "CODEX_SUMMARY_JSON_NOT_OBJECT"
CODEX_SUMMARY_FIELDS_MISSING = "CODEX_SUMMARY_FIELDS_MISSING"
CODEX_SUMMARY_FIELDS_UNKNOWN = "CODEX_SUMMARY_FIELDS_UNKNOWN"

EXPECTED_SUMMARY_FIELDS = frozenset(
    {
        "implementation_summary",
        "notes",
        "warnings",
        "blockers",
    }
)

_MARKER_LINE_RE = re.compile(r"(?m)^CODEX_EXECUTION_SUMMARY_JSON:[ \t]*$")
_SUMMARY_BLOCK_RE = re.compile(
    r"(?ms)^CODEX_EXECUTION_SUMMARY_JSON:[ \t]*\r?\n"
    r"```json[ \t]*\r?\n"
    r"(?P<json>.*?)"
    r"\r?\n```[ \t]*(?:\r?\n)?"
)


@dataclass(frozen=True)
class CodexSummaryParseIssue:
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
class CodexSummaryParseResult:
    """Result of extracting the minimal execution summary block from stdout."""

    ok: bool
    code: str
    summary: Mapping[str, Any] | None = None
    issue: CodexSummaryParseIssue | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "ok": self.ok,
            "code": self.code,
            "summary": dict(self.summary or {}),
        }
        if self.issue is not None:
            data["issue"] = self.issue.to_dict()
        return data


def parse_codex_summary_stdout(stdout: str) -> CodexSummaryParseResult:
    """Extract and validate one explicit minimal execution summary JSON block."""

    text = stdout or ""
    marker_count = len(_MARKER_LINE_RE.findall(text))
    if marker_count == 0:
        return _failure(
            CODEX_SUMMARY_BLOCK_MISSING,
            "No CODEX_EXECUTION_SUMMARY_JSON summary block was found in stdout.",
        )
    if marker_count > 1:
        return _failure(
            CODEX_SUMMARY_BLOCK_DUPLICATE,
            "Multiple CODEX_EXECUTION_SUMMARY_JSON summary markers were found in stdout.",
            marker_count=marker_count,
        )

    matches = list(_SUMMARY_BLOCK_RE.finditer(text))
    if not matches:
        return _failure(
            CODEX_SUMMARY_BLOCK_MALFORMED,
            "The CODEX_EXECUTION_SUMMARY_JSON marker was not followed by one fenced json block.",
        )
    if len(matches) > 1:
        return _failure(
            CODEX_SUMMARY_BLOCK_DUPLICATE,
            "Multiple CODEX_EXECUTION_SUMMARY_JSON summary blocks were found in stdout.",
            block_count=len(matches),
        )

    json_text = matches[0].group("json").strip()
    try:
        decoded = json.loads(json_text)
    except json.JSONDecodeError as exc:
        return _failure(
            CODEX_SUMMARY_JSON_MALFORMED,
            "The CODEX_EXECUTION_SUMMARY_JSON block does not contain valid JSON.",
            line=exc.lineno,
            column=exc.colno,
            error=exc.msg,
        )

    if not isinstance(decoded, dict):
        return _failure(
            CODEX_SUMMARY_JSON_NOT_OBJECT,
            "The CODEX_EXECUTION_SUMMARY_JSON value must be a JSON object.",
            value_type=type(decoded).__name__,
        )

    fields = set(decoded)
    missing = sorted(EXPECTED_SUMMARY_FIELDS - fields)
    if missing:
        return _failure(
            CODEX_SUMMARY_FIELDS_MISSING,
            "The CODEX_EXECUTION_SUMMARY_JSON object is missing expected top-level fields.",
            missing=missing,
        )

    unknown = sorted(fields - EXPECTED_SUMMARY_FIELDS)
    if unknown:
        return _failure(
            CODEX_SUMMARY_FIELDS_UNKNOWN,
            "The CODEX_EXECUTION_SUMMARY_JSON object contains unknown top-level fields.",
            unknown=unknown,
        )

    return CodexSummaryParseResult(
        ok=True,
        code=CODEX_SUMMARY_PARSE_OK,
        summary=decoded,
    )


def _failure(code: str, message: str, **details: Any) -> CodexSummaryParseResult:
    return CodexSummaryParseResult(
        ok=False,
        code=code,
        issue=CodexSummaryParseIssue(code=code, message=message, details=details),
    )


__all__ = [
    "CODEX_SUMMARY_BLOCK_DUPLICATE",
    "CODEX_SUMMARY_BLOCK_MALFORMED",
    "CODEX_SUMMARY_BLOCK_MISSING",
    "CODEX_SUMMARY_FIELDS_MISSING",
    "CODEX_SUMMARY_FIELDS_UNKNOWN",
    "CODEX_SUMMARY_JSON_MALFORMED",
    "CODEX_SUMMARY_JSON_NOT_OBJECT",
    "CODEX_SUMMARY_PARSE_OK",
    "CodexSummaryParseIssue",
    "CodexSummaryParseResult",
    "EXPECTED_SUMMARY_FIELDS",
    "SUMMARY_MARKER",
    "parse_codex_summary_stdout",
]

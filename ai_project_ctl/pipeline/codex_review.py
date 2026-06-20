"""Semantic Codex Review gate for supervised pipeline runs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ai_project_ctl.core.store import read_json_file

from .machine_review import FAIL as MACHINE_REVIEW_FAIL
from .machine_review import PASS as MACHINE_REVIEW_PASS
from .machine_review import MachineReviewResult
from .report_gate import ReportGateResult
from .state import task_reports_state_path


PASS = "pass"
BLOCKED = "blocked"
FAIL = "fail"

VERDICT_APPROVE = "APPROVE"
VERDICT_REQUEST_CHANGES = "REQUEST_CHANGES"
VERDICT_BLOCKED = "BLOCKED"
VALID_VERDICTS = {VERDICT_APPROVE, VERDICT_REQUEST_CHANGES, VERDICT_BLOCKED}
BLOCKING_VERDICTS = {VERDICT_REQUEST_CHANGES, VERDICT_BLOCKED}

CODE_PASS = "CODEX_REVIEW_APPROVE"
CODE_REQUEST_CHANGES = "CODEX_REVIEW_REQUEST_CHANGES"
CODE_BLOCKED = "CODEX_REVIEW_BLOCKED"
CODE_OUTPUT_MISSING = "CODEX_REVIEW_OUTPUT_MISSING"
CODE_MALFORMED_OUTPUT = "CODEX_REVIEW_MALFORMED_OUTPUT"
CODE_EVIDENCE_CONTRADICTION = "CODEX_REVIEW_EVIDENCE_CONTRADICTION"
CODE_REVIEWER_ERROR = "CODEX_REVIEWER_ERROR"

SEVERITIES = {"Critical", "Major", "Minor", "Suggestion"}
BLOCKING_SEVERITIES = {"Critical", "Major"}
SUMMARY_LIMIT = 1200
PROMPT_VERSION = 1
ReviewerRunner = Callable[[str], str | Mapping[str, Any]]


@dataclass(frozen=True)
class CodexReviewFinding:
    severity: str
    message: str
    file: str = ""
    criterion: str = ""

    def to_dict(self) -> dict[str, str]:
        data = {"severity": self.severity, "message": self.message}
        if self.file:
            data["file"] = self.file
        if self.criterion:
            data["criterion"] = self.criterion
        return data


@dataclass(frozen=True)
class CodexReviewResult:
    status: str
    code: str
    reason: str
    verdict: str
    task_id: str
    report_id: str
    review_id: str
    prompt_sha256: str
    prompt_bytes: int
    summary: str = ""
    findings: tuple[CodexReviewFinding, ...] = ()
    risks: tuple[str, ...] = ()
    evidence: Mapping[str, Any] | None = None

    @property
    def ok(self) -> bool:
        return self.status == PASS

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "code": self.code,
            "reason": self.reason,
            "verdict": self.verdict,
            "task_id": self.task_id,
            "report_id": self.report_id,
            "review_id": self.review_id,
            "prompt_sha256": self.prompt_sha256,
            "prompt_bytes": self.prompt_bytes,
            "summary": self.summary,
            "findings": [finding.to_dict() for finding in self.findings],
            "risks": list(self.risks),
            "evidence": dict(self.evidence or {}),
        }


def evaluate_codex_review(
    *,
    root: str | Path,
    task: Mapping[str, Any],
    report_gate: ReportGateResult,
    machine_review: MachineReviewResult,
    reviewer: ReviewerRunner | None = None,
    reviewer_output: str | Mapping[str, Any] | None = None,
) -> CodexReviewResult:
    """Build and optionally run a read-only semantic reviewer prompt."""

    root_path = Path(root).resolve()
    prompt = build_codex_review_prompt(
        root=root_path,
        task=task,
        report_gate=report_gate,
        machine_review=machine_review,
    )
    prompt_bytes = len(prompt.encode("utf-8"))
    prompt_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    task_id = str(task.get("id") or machine_review.task_id or report_gate.task_id)
    report_id = str(report_gate.report_id or machine_review.report_id)

    if reviewer_output is None and reviewer is not None:
        try:
            reviewer_output = reviewer(prompt)
        except Exception as exc:  # pragma: no cover - defensive boundary.
            return _result(
                status=FAIL,
                code=CODE_REVIEWER_ERROR,
                reason="reviewer_runner_failed: {}".format(exc),
                verdict="",
                task_id=task_id,
                report_id=report_id,
                prompt_sha256=prompt_sha,
                prompt_bytes=prompt_bytes,
            )

    if reviewer_output is None or (
        isinstance(reviewer_output, str) and not reviewer_output.strip()
    ):
        return _result(
            status=FAIL,
            code=CODE_OUTPUT_MISSING,
            reason="reviewer_output_missing",
            verdict="",
            task_id=task_id,
            report_id=report_id,
            prompt_sha256=prompt_sha,
            prompt_bytes=prompt_bytes,
        )

    parsed = _parse_reviewer_output(reviewer_output)
    if isinstance(parsed, str):
        return _result(
            status=FAIL,
            code=CODE_MALFORMED_OUTPUT,
            reason=parsed,
            verdict="",
            task_id=task_id,
            report_id=report_id,
            prompt_sha256=prompt_sha,
            prompt_bytes=prompt_bytes,
        )

    malformed = _schema_error(parsed)
    if malformed:
        return _result(
            status=FAIL,
            code=CODE_MALFORMED_OUTPUT,
            reason=malformed,
            verdict=str(parsed.get("verdict") or ""),
            task_id=task_id,
            report_id=report_id,
            prompt_sha256=prompt_sha,
            prompt_bytes=prompt_bytes,
        )

    findings = _findings(parsed.get("findings"))
    risks = tuple(_string_list(parsed.get("risks")))
    evidence = _mapping(parsed.get("evidence"))
    verdict = str(parsed["verdict"])
    contradiction = _evidence_contradiction(
        parsed,
        evidence=evidence,
        task_id=task_id,
        report_gate=report_gate,
        machine_review=machine_review,
        findings=findings,
    )
    if contradiction:
        return _result(
            status=FAIL,
            code=CODE_EVIDENCE_CONTRADICTION,
            reason=contradiction,
            verdict=verdict,
            task_id=task_id,
            report_id=report_id,
            prompt_sha256=prompt_sha,
            prompt_bytes=prompt_bytes,
            summary=_summary(parsed.get("summary")),
            findings=findings,
            risks=risks,
            evidence=evidence,
        )

    if verdict == VERDICT_APPROVE:
        return _result(
            status=PASS,
            code=CODE_PASS,
            reason="Codex Reviewer approved the semantic review gate.",
            verdict=verdict,
            task_id=task_id,
            report_id=report_id,
            prompt_sha256=prompt_sha,
            prompt_bytes=prompt_bytes,
            summary=_summary(parsed.get("summary")),
            findings=findings,
            risks=risks,
            evidence=evidence,
        )

    code = CODE_REQUEST_CHANGES if verdict == VERDICT_REQUEST_CHANGES else CODE_BLOCKED
    return _result(
        status=BLOCKED,
        code=code,
        reason=_blocking_reason(verdict, findings),
        verdict=verdict,
        task_id=task_id,
        report_id=report_id,
        prompt_sha256=prompt_sha,
        prompt_bytes=prompt_bytes,
        summary=_summary(parsed.get("summary")),
        findings=findings,
        risks=risks,
        evidence=evidence,
    )


def build_codex_review_prompt(
    *,
    root: str | Path,
    task: Mapping[str, Any],
    report_gate: ReportGateResult,
    machine_review: MachineReviewResult,
) -> str:
    """Create the read-only prompt package sent to the semantic reviewer."""

    root_path = Path(root).resolve()
    task_id = str(task.get("id") or machine_review.task_id or report_gate.task_id)
    report_id = str(report_gate.report_id or machine_review.report_id)
    evidence = {
        "schema_version": PROMPT_VERSION,
        "task": {
            "id": task_id,
            "ref": str(task.get("ref") or ""),
            "title": str(task.get("title") or ""),
            "status": str(task.get("status") or ""),
            "active_document": str(task.get("active_document") or ""),
        },
        "execution_report": _execution_report_summary(
            root_path,
            task_id=task_id,
            report_id=report_id,
        ),
        "report_gate": {
            "status": report_gate.status,
            "code": report_gate.code,
            "reason": report_gate.reason,
            "report_id": report_gate.report_id,
            "changed_files": list(report_gate.changed_files),
            "generated_files": list(report_gate.generated_files),
            "checks": [dict(check) for check in report_gate.checks],
            "warnings": [warning.to_dict() for warning in report_gate.warnings],
        },
        "machine_review": {
            "status": machine_review.status,
            "code": machine_review.code,
            "reason": machine_review.reason,
            "report_id": machine_review.report_id,
            "checks": [check.to_dict() for check in machine_review.checks],
        },
        "context_references": _context_references(root_path),
    }
    expected = {
        "verdict": "APPROVE | REQUEST_CHANGES | BLOCKED",
        "summary": "One concise semantic review summary.",
        "evidence": {
            "task_id": task_id,
            "report_id": report_id,
            "report_gate_status": report_gate.status,
            "machine_review_status": machine_review.status,
        },
        "findings": [
            {
                "severity": "Critical | Major | Minor | Suggestion",
                "message": "Finding text.",
                "file": "Optional repository path.",
                "criterion": "Optional acceptance criterion.",
            }
        ],
        "risks": ["Optional residual risk."],
    }
    return "\n".join(
        [
            "[REVIEW]",
            "",
            "Active Role: Codex Reviewer / QA",
            "Active Stage: Semantic Codex Review Gate",
            "Active Document: {}".format(task.get("active_document") or task_id),
            "Expected Result: Structured read-only verdict for {}".format(task_id),
            "",
            "Repository: current repository",
            "",
            "Source Documents:",
            "- AI_PROJECT/generated/CODEX_PROMPT.md (read-only execution contract)",
            "- AI_PROJECT/generated/CONTEXT_PACK.md (read-only retrieved context, if present)",
            "- Latest structured Codex execution report",
            "- Machine Review evidence",
            "",
            "Task:",
            _bullet_block([str(task.get("summary") or task.get("description") or task_id)]),
            "",
            "Scope:",
            _bullet_block(_string_list(task.get("scope"))),
            "",
            "Out of Scope:",
            _bullet_block(_string_list(task.get("out_of_scope"))),
            "",
            "Allowed Files (Read-Only Inspection Only):",
            _bullet_block(_string_list(task.get("allowed_files"))),
            "",
            "Forbidden Actions:",
            "- Do not edit files.",
            "- Do not run lifecycle transitions.",
            "- Do not commit.",
            "- Do not approve as Human Owner.",
            "- Do not override Machine Review FAIL/WARN evidence with a semantic approval.",
            "- Do not expand task scope, allowed files, or acceptance criteria.",
            "",
            "Acceptance Criteria:",
            _bullet_block(_string_list(task.get("acceptance_criteria"))),
            "",
            "Review Instructions:",
            _bullet_block(_string_list(task.get("review_instructions"))),
            "",
            "Evidence:",
            "```json",
            json.dumps(evidence, indent=2, sort_keys=True),
            "```",
            "",
            "Expected Output:",
            "Return JSON only. Do not include Markdown or prose outside the JSON object.",
            "The JSON schema is:",
            "```json",
            json.dumps(expected, indent=2),
            "```",
            "",
            "Verdict Rules:",
            "- APPROVE means semantic review found no required changes; it is not Human Owner approval.",
            "- REQUEST_CHANGES means required implementation or evidence fixes were found.",
            "- BLOCKED means review cannot be completed from the provided evidence.",
            "- Critical or Major findings must not be combined with APPROVE.",
            "- The evidence object must match the task_id, report_id, report_gate_status, and machine_review_status shown above.",
        ]
    )


def _result(
    *,
    status: str,
    code: str,
    reason: str,
    verdict: str,
    task_id: str,
    report_id: str,
    prompt_sha256: str,
    prompt_bytes: int,
    summary: str = "",
    findings: Sequence[CodexReviewFinding] = (),
    risks: Sequence[str] = (),
    evidence: Mapping[str, Any] | None = None,
) -> CodexReviewResult:
    review_id = _review_id(
        task_id=task_id,
        report_id=report_id,
        prompt_sha256=prompt_sha256,
        verdict=verdict,
        code=code,
        summary=summary,
    )
    return CodexReviewResult(
        status=status,
        code=code,
        reason=reason,
        verdict=verdict,
        task_id=task_id,
        report_id=report_id,
        review_id=review_id,
        prompt_sha256=prompt_sha256,
        prompt_bytes=prompt_bytes,
        summary=summary,
        findings=tuple(findings),
        risks=tuple(risks),
        evidence=evidence,
    )


def _parse_reviewer_output(value: str | Mapping[str, Any]) -> Mapping[str, Any] | str:
    if isinstance(value, Mapping):
        return value
    text = str(value).strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        return "reviewer_output_is_not_valid_json: {}".format(exc)
    if not isinstance(parsed, Mapping):
        return "reviewer_output_must_be_json_object"
    return parsed


def _schema_error(data: Mapping[str, Any]) -> str:
    verdict = data.get("verdict")
    if verdict not in VALID_VERDICTS:
        return "verdict_must_be_one_of: {}".format(", ".join(sorted(VALID_VERDICTS)))
    evidence = data.get("evidence")
    if not isinstance(evidence, Mapping):
        return "evidence_must_be_object"
    if "summary" in data and not isinstance(data.get("summary"), str):
        return "summary_must_be_string"
    try:
        findings = _findings(data.get("findings"))
    except ValueError as exc:
        return str(exc)
    if verdict in BLOCKING_VERDICTS and not findings:
        return "blocking_verdict_requires_at_least_one_finding"
    if "risks" in data and not isinstance(data.get("risks"), list):
        return "risks_must_be_list"
    return ""


def _evidence_contradiction(
    data: Mapping[str, Any],
    *,
    evidence: Mapping[str, Any],
    task_id: str,
    report_gate: ReportGateResult,
    machine_review: MachineReviewResult,
    findings: Sequence[CodexReviewFinding],
) -> str:
    expected = {
        "task_id": task_id,
        "report_id": str(report_gate.report_id or machine_review.report_id),
        "report_gate_status": report_gate.status,
        "machine_review_status": machine_review.status,
    }
    for key, expected_value in expected.items():
        actual = evidence.get(key)
        if str(actual) != str(expected_value):
            return "{}_mismatch: expected {!r}, got {!r}".format(
                key,
                expected_value,
                actual,
            )
    verdict = str(data["verdict"])
    if verdict == VERDICT_APPROVE and machine_review.status != MACHINE_REVIEW_PASS:
        return "approve_verdict_cannot_override_machine_review_{}".format(
            machine_review.status or "unknown"
        )
    if verdict == VERDICT_APPROVE and report_gate.status != PASS:
        return "approve_verdict_cannot_override_report_gate_{}".format(
            report_gate.status or "unknown"
        )
    if verdict == VERDICT_APPROVE:
        blocking = [
            finding.severity for finding in findings if finding.severity in BLOCKING_SEVERITIES
        ]
        if blocking:
            return "approve_verdict_has_blocking_findings: {}".format(
                ", ".join(blocking)
            )
    if machine_review.status == MACHINE_REVIEW_FAIL and verdict == VERDICT_APPROVE:
        return "approve_verdict_cannot_override_machine_review_fail"
    return ""


def _findings(value: Any) -> tuple[CodexReviewFinding, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError("findings_must_be_list")
    findings: list[CodexReviewFinding] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError("findings[{}]_must_be_object".format(index))
        severity = str(item.get("severity") or "")
        message = str(item.get("message") or "").strip()
        if severity not in SEVERITIES:
            raise ValueError(
                "findings[{}].severity_must_be_one_of: {}".format(
                    index,
                    ", ".join(sorted(SEVERITIES)),
                )
            )
        if not message:
            raise ValueError("findings[{}].message_required".format(index))
        findings.append(
            CodexReviewFinding(
                severity=severity,
                message=message,
                file=str(item.get("file") or ""),
                criterion=str(item.get("criterion") or ""),
            )
        )
    return tuple(findings)


def _execution_report_summary(root: Path, *, task_id: str, report_id: str) -> dict[str, Any]:
    path = task_reports_state_path(root)
    if not path.exists():
        return {"available": False, "reason": "task_reports_state_missing"}
    data = read_json_file(path, missing_code="TASK_REPORTS_NOT_INITIALIZED")
    if not isinstance(data, Mapping):
        return {"available": False, "reason": "task_reports_state_not_object"}
    for record in data.get("reports", []):
        if not isinstance(record, Mapping):
            continue
        if str(record.get("id") or "") != report_id:
            continue
        report = record.get("report")
        if not isinstance(report, Mapping):
            return {"available": False, "reason": "report_record_missing_report"}
        return {
            "available": True,
            "report_id": report_id,
            "task_id": task_id,
            "implementation_summary": _summary(report.get("implementation_summary")),
            "warnings": _string_list(report.get("warnings")),
            "blockers": _string_list(report.get("blockers")),
            "notes": _string_list(report.get("notes")),
            "owner_decision_required": report.get("owner_decision_required") is True,
        }
    return {"available": False, "reason": "report_record_not_found", "report_id": report_id}


def _context_references(root: Path) -> list[dict[str, Any]]:
    references: list[dict[str, Any]] = []
    for relative in (
        "AI_PROJECT/generated/CODEX_PROMPT.md",
        "AI_PROJECT/generated/CONTEXT_PACK.md",
    ):
        path = root / relative
        if not path.exists():
            continue
        payload = path.read_bytes()
        references.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
            }
        )
    return references


def _blocking_reason(
    verdict: str,
    findings: Sequence[CodexReviewFinding],
) -> str:
    if not findings:
        return "Codex Reviewer returned {}.".format(verdict)
    first = findings[0]
    return "Codex Reviewer returned {}: [{}] {}".format(
        verdict,
        first.severity,
        first.message,
    )


def _review_id(
    *,
    task_id: str,
    report_id: str,
    prompt_sha256: str,
    verdict: str,
    code: str,
    summary: str,
) -> str:
    payload = "|".join((task_id, report_id, prompt_sha256, verdict, code, summary))
    return "CREV-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12].upper()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [str(item) for item in value if str(item).strip()]


def _summary(value: Any) -> str:
    text = str(value or "").strip()
    if len(text) <= SUMMARY_LIMIT:
        return text
    return text[: SUMMARY_LIMIT - 3].rstrip() + "..."


def _bullet_block(items: Sequence[str]) -> str:
    clean = [str(item).strip() for item in items if str(item).strip()]
    if not clean:
        return "- Not specified."
    return "\n".join("- {}".format(item) for item in clean)

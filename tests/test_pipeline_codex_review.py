import json
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline.codex_review import (
    BLOCKED,
    CODE_BLOCKED,
    CODE_EVIDENCE_CONTRADICTION,
    CODE_MALFORMED_OUTPUT,
    CODE_OUTPUT_MISSING,
    CODE_PASS,
    CODE_REQUEST_CHANGES,
    FAIL,
    PASS,
    VERDICT_APPROVE,
    VERDICT_BLOCKED,
    VERDICT_REQUEST_CHANGES,
    evaluate_codex_review,
)
from ai_project_ctl.pipeline.machine_review import (
    CODE_COMMAND_FAILED,
    CODE_PASS as MACHINE_CODE_PASS,
    FAIL as MACHINE_FAIL,
    PASS as MACHINE_PASS,
    MachineCheckEvidence,
    MachineReviewResult,
)
from ai_project_ctl.pipeline.report_gate import (
    CODE_PASS as REPORT_CODE_PASS,
    PASS as REPORT_PASS,
    ReportGateResult,
)


def task():
    return {
        "id": "TASK-001",
        "ref": "APP-01",
        "title": "Review gate task",
        "status": "in_progress",
        "summary": "Add semantic review.",
        "scope": ["Create a narrow read-only review prompt."],
        "out_of_scope": ["Do not let reviewer edit files."],
        "allowed_files": ["ai_project_ctl/pipeline/codex_review.py", "tests/**"],
        "acceptance_criteria": ["Reviewer cannot mutate files."],
        "review_instructions": ["Verify semantic verdict cannot override Machine Review FAIL."],
        "active_document": "ai_project_ctl/pipeline/codex_review.py",
    }


def report_gate():
    return ReportGateResult(
        status=REPORT_PASS,
        code=REPORT_CODE_PASS,
        reason="report passed",
        report_id="RPT-001",
        task_id="TASK-001",
        changed_files=("ai_project_ctl/pipeline/codex_review.py",),
        generated_files=(),
        checks=({"name": "unit", "result": "pass", "blocking": True},),
    )


def machine_review(status=MACHINE_PASS, code=MACHINE_CODE_PASS, reason="machine passed"):
    return MachineReviewResult(
        status=status,
        code=code,
        reason=reason,
        task_id="TASK-001",
        report_id="RPT-001",
        checks=(
            MachineCheckEvidence(
                name="protected_file_check",
                status=status,
                code=code,
                reason=reason,
            ),
        ),
    )


def reviewer_output(verdict, *, findings=(), machine_status=MACHINE_PASS):
    return {
        "verdict": verdict,
        "summary": "Reviewed the implementation evidence.",
        "evidence": {
            "task_id": "TASK-001",
            "report_id": "RPT-001",
            "report_gate_status": REPORT_PASS,
            "machine_review_status": machine_status,
        },
        "findings": list(findings),
        "risks": [],
    }


class PipelineCodexReviewTests(unittest.TestCase):
    def test_codex_review_approves_structured_verdict(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompts = []

            def fake_reviewer(prompt):
                prompts.append(prompt)
                return reviewer_output(VERDICT_APPROVE)

            result = evaluate_codex_review(
                root=Path(tmp),
                task=task(),
                report_gate=report_gate(),
                machine_review=machine_review(),
                reviewer=fake_reviewer,
            )

            self.assertEqual(result.status, PASS)
            self.assertEqual(result.code, CODE_PASS)
            self.assertEqual(result.verdict, VERDICT_APPROVE)
            self.assertTrue(result.review_id.startswith("CREV-"))
            self.assertIn("[REVIEW]", prompts[0])
            self.assertIn("Allowed Files (Read-Only Inspection Only)", prompts[0])
            self.assertIn("Do not edit files.", prompts[0])
            self.assertIn("Do not run lifecycle transitions.", prompts[0])
            self.assertIn("Do not commit.", prompts[0])
            self.assertNotIn("prompt_text", result.to_dict())

    def test_codex_review_blocks_request_changes_with_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = evaluate_codex_review(
                root=Path(tmp),
                task=task(),
                report_gate=report_gate(),
                machine_review=machine_review(),
                reviewer_output=reviewer_output(
                    VERDICT_REQUEST_CHANGES,
                    findings=(
                        {
                            "severity": "Major",
                            "message": "Acceptance criterion is not demonstrated.",
                            "file": "ai_project_ctl/pipeline/codex_review.py",
                        },
                    ),
                ),
            )

            self.assertEqual(result.status, BLOCKED)
            self.assertEqual(result.code, CODE_REQUEST_CHANGES)
            self.assertEqual(result.verdict, VERDICT_REQUEST_CHANGES)
            self.assertIn("REQUEST_CHANGES", result.reason)

    def test_codex_review_blocks_blocked_verdict_with_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = evaluate_codex_review(
                root=Path(tmp),
                task=task(),
                report_gate=report_gate(),
                machine_review=machine_review(),
                reviewer_output=reviewer_output(
                    VERDICT_BLOCKED,
                    findings=(
                        {
                            "severity": "Critical",
                            "message": "Machine evidence is missing required command output.",
                        },
                    ),
                ),
            )

            self.assertEqual(result.status, BLOCKED)
            self.assertEqual(result.code, CODE_BLOCKED)
            self.assertEqual(result.verdict, VERDICT_BLOCKED)

    def test_codex_review_fails_malformed_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = evaluate_codex_review(
                root=Path(tmp),
                task=task(),
                report_gate=report_gate(),
                machine_review=machine_review(),
                reviewer_output="{not json",
            )

            self.assertEqual(result.status, FAIL)
            self.assertEqual(result.code, CODE_MALFORMED_OUTPUT)

    def test_codex_review_fails_missing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = evaluate_codex_review(
                root=Path(tmp),
                task=task(),
                report_gate=report_gate(),
                machine_review=machine_review(),
            )

            self.assertEqual(result.status, FAIL)
            self.assertEqual(result.code, CODE_OUTPUT_MISSING)

    def test_codex_review_cannot_approve_failed_machine_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = evaluate_codex_review(
                root=Path(tmp),
                task=task(),
                report_gate=report_gate(),
                machine_review=machine_review(
                    status=MACHINE_FAIL,
                    code=CODE_COMMAND_FAILED,
                    reason="protected files check failed",
                ),
                reviewer_output=json.dumps(
                    reviewer_output(VERDICT_APPROVE, machine_status=MACHINE_FAIL)
                ),
            )

            self.assertEqual(result.status, FAIL)
            self.assertEqual(result.code, CODE_EVIDENCE_CONTRADICTION)
            self.assertIn("machine_review_fail", result.reason)


if __name__ == "__main__":
    unittest.main()

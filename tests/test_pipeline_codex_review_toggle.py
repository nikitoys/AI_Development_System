import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ai_project_ctl.pipeline.codex_review import CodexReviewResult
from ai_project_ctl.pipeline.close_phase import _preflight_evidence
from ai_project_ctl.pipeline.git_commit import (
    CODE_CODEX_REVIEW_NOT_APPROVED,
    CODE_READY,
    evaluate_commit_readiness,
)
from ai_project_ctl.pipeline.machine_review import (
    PASS as MACHINE_PASS,
    MachineCheckEvidence,
    MachineReviewResult,
)
from ai_project_ctl.pipeline.phase import PhaseResult
from ai_project_ctl.pipeline.policy import (
    CodexReviewDecision,
    ReviewPolicy,
    apply_codex_review_requirement,
    policy_preset,
)
from ai_project_ctl.pipeline.report_gate import (
    CODE_PASS as REPORT_CODE_PASS,
    PASS as REPORT_PASS,
    ReportGateResult,
)
from ai_project_ctl.pipeline.review_phase import review_phase
from ai_project_ctl.pipeline.session import create_session, record_phase_result
from ai_project_ctl.pipeline.state import pipeline_state_path
from ai_project_ctl.pipeline.ui_policy import resolve_pipeline_policy_from_settings


TASK_ID = "TASK-001"
REPORT_ID = "RPT-001"
CHANGED_FILE = "ai_project_ctl/pipeline/review_phase.py"


def completed(stdout="OK\n", returncode=0, stderr=""):
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def disabled_codex_policy(name="toggle_disabled", *, preset="supervised_autoclose"):
    policy = apply_codex_review_requirement(
        policy_preset(preset),
        require_codex_review=False,
    )
    return replace(policy, name=name)


def required_codex_policy(name="toggle_required"):
    return replace(policy_preset("supervised_autoclose"), name=name)


def write_reference_state(root: Path, *, task_status: str = "ready") -> None:
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True)
    (state_dir / "plan.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "initiatives": [{"id": "INIT-001", "status": "active"}],
                "epics": [
                    {
                        "id": "EPIC-001",
                        "initiative_id": "INIT-001",
                        "status": "planned",
                        "key": "APP",
                        "order": 1,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (state_dir / "tasks.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "current_task_id": None,
                "tasks": [
                    {
                        "id": TASK_ID,
                        "ref": "APP-01",
                        "uid": "uid_task_001",
                        "legacy_id": TASK_ID,
                        "aliases": [TASK_ID],
                        "title": "Toggle Codex Review",
                        "status": task_status,
                        "epic_id": "EPIC-001",
                        "priority": 1,
                        "order": 1,
                        "local_seq": 1,
                        "depends_on": [],
                        "scope": ["Exercise Codex Review toggle."],
                        "out_of_scope": ["Do not disable Machine Review."],
                        "allowed_files": [CHANGED_FILE, "tests/**"],
                        "acceptance_criteria": ["Machine Review remains required."],
                        "review_instructions": ["Check Codex Review toggle behavior."],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (state_dir / "evolution.json").write_text(
        json.dumps({"schema_version": 1, "revision": 1, "changes": []}),
        encoding="utf-8",
    )


def write_report_state(root: Path) -> None:
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "task_reports.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "latest_by_task": {TASK_ID: REPORT_ID},
                "reports": [
                    {
                        "id": REPORT_ID,
                        "task_id": TASK_ID,
                        "task_ref": "APP-01",
                        "submitted_at": "2026-06-24T00:00:00Z",
                        "submitted_by": "tester",
                        "source_file": "/tmp/report.json",
                        "report": valid_report(),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def valid_report() -> dict:
    return {
        "schema_version": 1,
        "task_id": TASK_ID,
        "task_ref": "APP-01",
        "implementation_summary": "Implemented the selected task.",
        "changed_files": [CHANGED_FILE],
        "generated_files": [],
        "checks": [
            {
                "name": "unit",
                "command": "python -m unittest tests.test_pipeline_codex_review_toggle",
                "result": "pass",
                "duration_sec": 0.1,
                "blocking": True,
            }
        ],
        "warnings": [],
        "blockers": [],
        "notes": [],
        "owner_decision_required": False,
        "token_usage": {
            "prompt_tokens": 100,
            "context_tokens": 20,
            "remaining_tokens": 1000,
            "token_count_strategy": "local_byte_estimate",
            "token_count_estimated": True,
            "token_count_unavailable": False,
        },
    }


def create_pipeline_session(root: Path, policy) -> str:
    session = create_session(
        root=root,
        actor="tester",
        policy=policy,
        current_task_id=TASK_ID,
        current_task_ref="APP-01",
        auto_close_note="Owner approved auto-close for this test.",
    )
    assert session.ok, session.errors
    return session.data["session_id"]


def record_required_preflight_phases(root: Path, session_id: str) -> None:
    for phase_name in ("prepare", "execute", "collect_report"):
        record_phase_result(
            session_id,
            PhaseResult.passed(
                phase_name,
                reason="{} passed".format(phase_name),
                artifacts={"task_id": TASK_ID, "report_id": REPORT_ID},
            ),
            root=root,
            actor="tester",
            task_id=TASK_ID,
            command="pipeline.phase.{}".format(phase_name),
        )
    record_phase_result(
        session_id,
        PhaseResult.passed(
            "verify",
            reason="verify passed",
            artifacts={
                "task_id": TASK_ID,
                "report_id": REPORT_ID,
                "verify_evidence": {
                    "report_id": REPORT_ID,
                    "report_gate": {
                        "status": "pass",
                        "code": "CODEX_REPORT_PASS",
                        "reason": "report passed",
                    },
                },
            },
        ),
        root=root,
        actor="tester",
        task_id=TASK_ID,
        command="pipeline.phase.verify",
    )


def load_session(root: Path) -> dict:
    return json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))["sessions"][0]


def report_gate() -> ReportGateResult:
    return ReportGateResult(
        status=REPORT_PASS,
        code=REPORT_CODE_PASS,
        reason="report passed",
        report_id=REPORT_ID,
        task_id=TASK_ID,
        changed_files=(CHANGED_FILE,),
    )


def machine_review(status=MACHINE_PASS) -> MachineReviewResult:
    checks = tuple(
        MachineCheckEvidence(
            name=name,
            status=status,
            code="{}_{}".format(name.upper(), status.upper()),
            reason="{} {}".format(name, status),
        )
        for name in (
            "task_check_generated",
            "evolution_check_generated",
            "context_check_generated",
            "protected_file_check",
        )
    )
    return MachineReviewResult(
        status=status,
        code="MACHINE_REVIEW_{}".format(status.upper()),
        reason="machine {}".format(status),
        task_id=TASK_ID,
        report_id=REPORT_ID,
        checks=checks,
    )


def missing_codex_review() -> CodexReviewResult:
    return CodexReviewResult(
        status="",
        code="",
        reason="",
        verdict="",
        task_id=TASK_ID,
        report_id=REPORT_ID,
        review_id="",
        prompt_sha256="",
        prompt_bytes=0,
    )


class PipelineCodexReviewToggleTests(unittest.TestCase):
    def test_ui_policy_false_disables_codex_review_but_keeps_machine_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            policy = resolve_pipeline_policy_from_settings(
                {
                    "default_policy": "supervised_executable_local_commit",
                    "command_line": "codex exec",
                    "require_codex_review": False,
                },
                root=Path(tmp),
            )

            self.assertTrue(policy.validate().ok)
            self.assertTrue(policy.review.require_machine_review)
            self.assertFalse(policy.review.require_codex_review)
            self.assertEqual(policy.review.required_codex_decision, CodexReviewDecision.NONE)

            required = resolve_pipeline_policy_from_settings(
                {
                    "default_policy": "supervised_executable_local_commit",
                    "command_line": "codex exec",
                    "require_codex_review": "true",
                },
                root=Path(tmp),
            )

            self.assertTrue(required.review.require_codex_review)
            self.assertEqual(
                required.review.required_codex_decision,
                CodexReviewDecision.APPROVE,
            )

    def test_review_phase_skips_without_building_prompt_when_policy_disables_codex(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_reference_state(root)
            write_report_state(root)
            session_id = create_pipeline_session(root, disabled_codex_policy("review_skip"))
            record_required_preflight_phases(root, session_id)

            result = review_phase(session_id, root=root, actor="tester", build_prompt_only=True)

            self.assertTrue(result.ok)
            phase = result.data["phase_result"]
            artifacts = phase["artifacts"]
            self.assertEqual(phase["status"], "skipped")
            self.assertFalse(artifacts["codex_review_required"])
            self.assertEqual(artifacts["skip_reason"], "disabled_by_policy")
            self.assertFalse(artifacts["review_prompt_built"])
            self.assertFalse(artifacts["review_prompt_returned"])
            self.assertNotIn("review_prompt", result.data)

    def test_close_preflight_accepts_skipped_review_only_when_policy_disables_codex(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_reference_state(root)
            write_report_state(root)
            disabled_session_id = create_pipeline_session(root, disabled_codex_policy("close_skip"))
            record_required_preflight_phases(root, disabled_session_id)
            review_phase(disabled_session_id, root=root, actor="tester", build_prompt_only=True)

            disabled_evidence = _preflight_evidence(load_session(root), TASK_ID)

            self.assertTrue(disabled_evidence["preflight_passed"])
            self.assertFalse(disabled_evidence["codex_review_required"])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_reference_state(root)
            required_session_id = create_pipeline_session(root, required_codex_policy("close_required"))
            record_required_preflight_phases(root, required_session_id)
            record_phase_result(
                required_session_id,
                PhaseResult.skipped(
                    "review",
                    reason="skipped",
                    artifacts={
                        "task_id": TASK_ID,
                        "report_id": REPORT_ID,
                        "codex_review_required": False,
                        "policy_require_codex_review": False,
                        "skip_reason": "disabled_by_policy",
                        "review_status": "skipped",
                        "review_prompt_built": False,
                        "review_prompt_returned": False,
                    },
                ),
                root=root,
                actor="tester",
                task_id=TASK_ID,
                command="pipeline.phase.review",
            )

            required_evidence = _preflight_evidence(load_session(root), TASK_ID)
            codes = {gate["code"] for gate in required_evidence["missing_gates"]}

            self.assertFalse(required_evidence["preflight_passed"])
            self.assertIn("PHASE_NOT_PASSED", codes)
            self.assertIn("REVIEW_APPROVE_REQUIRED", codes)

    def test_commit_readiness_skips_codex_only_when_policy_disables_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_reference_state(root, task_status="done")
            disabled = disabled_codex_policy(
                "commit_skip",
                preset="supervised_local_commit",
            )

            ready = evaluate_commit_readiness(
                root=root,
                task_id=TASK_ID,
                policy=disabled,
                report_gate=report_gate(),
                machine_review=machine_review(),
                codex_review=missing_codex_review(),
                runner=lambda argv: completed(stdout=" M {}\n".format(CHANGED_FILE)),
            )

            self.assertEqual(ready.status, "pass")
            self.assertEqual(ready.code, CODE_READY)

            required = replace(
                disabled,
                review=ReviewPolicy(
                    require_machine_review=True,
                    required_machine_outcome=disabled.review.required_machine_outcome,
                    require_codex_review=True,
                    required_codex_decision=CodexReviewDecision.APPROVE,
                ),
            )

            blocked = evaluate_commit_readiness(
                root=root,
                task_id=TASK_ID,
                policy=required,
                report_gate=report_gate(),
                machine_review=machine_review(),
                codex_review=missing_codex_review(),
                runner=lambda argv: completed(stdout=" M {}\n".format(CHANGED_FILE)),
            )

            self.assertEqual(blocked.status, "blocked")
            self.assertEqual(blocked.code, CODE_CODEX_REVIEW_NOT_APPROVED)


if __name__ == "__main__":
    unittest.main()

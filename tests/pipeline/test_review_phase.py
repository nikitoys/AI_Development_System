import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from ai_project_ctl.pipeline.phase import PhaseResult
from ai_project_ctl.pipeline.policy import PipelinePolicy, policy_preset
from ai_project_ctl.pipeline.report_gate import CODE_BLOCKERS_PRESENT
from ai_project_ctl.pipeline.report_gate import CODE_PASS as REPORT_CODE_PASS
from ai_project_ctl.pipeline.report_gate import CODE_WARN as REPORT_CODE_WARN
from ai_project_ctl.pipeline.report_gate import (
    evaluate_report_gate_acceptance as real_evaluate_report_gate_acceptance,
)
from ai_project_ctl.pipeline.review_phase import review_phase
from ai_project_ctl.pipeline.session import create_session, record_phase_result


TASK_ID = "TASK-001"
TASK_REF = "APP-01"
REPORT_ID = "RPT-001"
CHANGED_FILE = "ai_project_ctl/pipeline/review_phase.py"


def _policy(*, allow_report_warnings: bool) -> PipelinePolicy:
    base = policy_preset("supervised")
    return replace(
        base,
        name="review_allow_report_warnings"
        if allow_report_warnings
        else "review_block_report_warnings",
        verify=replace(base.verify, allow_report_warnings=allow_report_warnings),
    )


def _write_reference_state(root: Path) -> None:
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
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
                "current_task_id": TASK_ID,
                "tasks": [
                    {
                        "id": TASK_ID,
                        "ref": TASK_REF,
                        "uid": "uid_task_001",
                        "legacy_id": TASK_ID,
                        "aliases": [TASK_ID],
                        "title": "Review phase task",
                        "status": "in_progress",
                        "epic_id": "EPIC-001",
                        "priority": 1,
                        "order": 1,
                        "local_seq": 1,
                        "depends_on": [],
                        "scope": ["Update review phase report gate handling."],
                        "out_of_scope": ["Do not change verify or close phases."],
                        "allowed_files": [
                            CHANGED_FILE,
                            "tests/pipeline/test_review_phase.py",
                        ],
                        "acceptance_criteria": [
                            "Review phase honors report warning policy."
                        ],
                        "review_instructions": ["Check report gate revalidation evidence."],
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


def _write_report_state(
    root: Path,
    *,
    latest_report_id: str = REPORT_ID,
    warnings: list[str] | None = None,
    blockers: list[str] | None = None,
) -> None:
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    reports = [
        _report_record(
            REPORT_ID,
            submitted_at="2026-06-25T00:00:00Z",
            warnings=warnings if latest_report_id == REPORT_ID else None,
            blockers=blockers if latest_report_id == REPORT_ID else None,
        )
    ]
    if latest_report_id != REPORT_ID:
        reports.append(
            _report_record(
                latest_report_id,
                submitted_at="2026-06-25T00:01:00Z",
                warnings=warnings,
                blockers=blockers,
            )
        )
    (state_dir / "task_reports.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "latest_by_task": {TASK_ID: latest_report_id},
                "reports": reports,
            }
        ),
        encoding="utf-8",
    )


def _report_record(
    report_id: str,
    *,
    submitted_at: str,
    warnings: list[str] | None = None,
    blockers: list[str] | None = None,
) -> dict:
    return {
        "id": report_id,
        "task_id": TASK_ID,
        "task_ref": TASK_REF,
        "submitted_at": submitted_at,
        "submitted_by": "tester",
        "source_file": "/tmp/report.json",
        "report": {
            "schema_version": 1,
            "task_id": TASK_ID,
            "task_ref": TASK_REF,
            "implementation_summary": "Implemented review phase behavior.",
            "changed_files": [CHANGED_FILE],
            "generated_files": [],
            "checks": [
                {
                    "name": "unit",
                    "command": "python -m unittest tests.pipeline.test_review_phase",
                    "result": "pass",
                    "duration_sec": 0.1,
                    "blocking": True,
                }
            ],
            "warnings": list(warnings or []),
            "blockers": list(blockers or []),
            "notes": [],
            "owner_decision_required": False,
            "token_usage": {
                "prompt_tokens": 100,
                "context_tokens": 20,
                "remaining_tokens": 1000,
                "token_count_strategy": "test fixture",
                "token_count_estimated": False,
                "token_count_unavailable": False,
            },
        },
    }


def _create_session(root: Path, policy: PipelinePolicy) -> str:
    result = create_session(
        root=root,
        actor="tester",
        policy=policy,
        current_task_id=TASK_ID,
        current_task_ref=TASK_REF,
    )
    if not result.ok:
        raise AssertionError(result.errors)
    return str(result.data["session_id"])


def _record_verified_report(
    root: Path,
    session_id: str,
    *,
    report_id: str = REPORT_ID,
    gate_status: str = "pass",
    gate_code: str = REPORT_CODE_PASS,
) -> None:
    result = record_phase_result(
        session_id,
        PhaseResult.passed(
            "verify",
            reason="verify passed",
            artifacts={
                "session_id": session_id,
                "task_id": TASK_ID,
                "report_id": report_id,
                "verify_evidence": {
                    "report_id": report_id,
                    "report_gate": {
                        "status": gate_status,
                        "code": gate_code,
                        "reason": "verified report gate {}".format(gate_status),
                        "report_id": report_id,
                        "task_id": TASK_ID,
                    },
                },
            },
        ),
        root=root,
        actor="tester",
        task_id=TASK_ID,
        command="pipeline.phase.verify",
    )
    if not result.ok:
        raise AssertionError(result.errors)


class ReviewPhaseReportGateAcceptanceTests(unittest.TestCase):
    def test_advisory_report_warning_allowed_after_verify_builds_review_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_reference_state(root)
            _write_report_state(root, warnings=["advisory report warning"])
            session_id = _create_session(root, _policy(allow_report_warnings=True))
            _record_verified_report(
                root,
                session_id,
                gate_status="warn",
                gate_code=REPORT_CODE_WARN,
            )

            with mock.patch(
                "ai_project_ctl.pipeline.review_phase.evaluate_report_gate_acceptance",
                wraps=real_evaluate_report_gate_acceptance,
            ) as acceptance_helper:
                result = review_phase(
                    session_id,
                    root=root,
                    actor="tester",
                    build_prompt_only=True,
                )

            phase = result.data["phase_result"]
            artifacts = phase["artifacts"]

        self.assertTrue(result.ok)
        self.assertEqual(phase["status"], "passed")
        self.assertEqual(acceptance_helper.call_count, 1)
        self.assertEqual(artifacts["report_gate_status"], "warn")
        self.assertTrue(artifacts["report_gate_acceptance"]["allow"])
        self.assertEqual(
            artifacts["report_gate_acceptance"]["policy"],
            "report_gate_warn_allowed_by_policy",
        )
        self.assertIn("review_prompt", result.data)

    def test_advisory_report_warning_disabled_blocks_after_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_reference_state(root)
            _write_report_state(root, warnings=["advisory report warning"])
            session_id = _create_session(root, _policy(allow_report_warnings=False))
            _record_verified_report(
                root,
                session_id,
                gate_status="warn",
                gate_code=REPORT_CODE_WARN,
            )

            result = review_phase(
                session_id,
                root=root,
                actor="tester",
                build_prompt_only=True,
            )
            phase = result.data["phase_result"]
            artifacts = phase["artifacts"]

        self.assertTrue(result.ok)
        self.assertEqual(phase["status"], "blocked")
        self.assertEqual(
            artifacts["blocked_by"],
            "REPORT_GATE_NOT_PASSED_AFTER_VERIFY",
        )
        self.assertEqual(artifacts["report_gate_status"], "warn")
        self.assertFalse(artifacts["report_gate_acceptance"]["allow"])
        self.assertEqual(
            artifacts["report_gate_acceptance"]["policy"],
            "report_gate_warn_blocks_downstream",
        )
        self.assertNotIn("review_prompt", result.data)

    def test_latest_report_id_change_still_blocks_after_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_reference_state(root)
            _write_report_state(root, latest_report_id="RPT-002")
            session_id = _create_session(root, _policy(allow_report_warnings=True))
            _record_verified_report(root, session_id, report_id=REPORT_ID)

            result = review_phase(
                session_id,
                root=root,
                actor="tester",
                build_prompt_only=True,
            )
            phase = result.data["phase_result"]
            artifacts = phase["artifacts"]

        self.assertTrue(result.ok)
        self.assertEqual(phase["status"], "blocked")
        self.assertEqual(artifacts["blocked_by"], "REPORT_CHANGED_AFTER_VERIFY")
        self.assertEqual(artifacts["verified_report_id"], REPORT_ID)
        self.assertEqual(artifacts["latest_report_id"], "RPT-002")

    def test_report_gate_fail_still_blocks_after_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_reference_state(root)
            _write_report_state(root, blockers=["must fix"])
            session_id = _create_session(root, _policy(allow_report_warnings=True))
            _record_verified_report(
                root,
                session_id,
                gate_status="fail",
                gate_code=CODE_BLOCKERS_PRESENT,
            )

            result = review_phase(
                session_id,
                root=root,
                actor="tester",
                build_prompt_only=True,
            )
            phase = result.data["phase_result"]
            artifacts = phase["artifacts"]

        self.assertTrue(result.ok)
        self.assertEqual(phase["status"], "blocked")
        self.assertEqual(
            artifacts["blocked_by"],
            "REPORT_GATE_NOT_PASSED_AFTER_VERIFY",
        )
        self.assertEqual(artifacts["report_gate_status"], "fail")
        self.assertEqual(artifacts["report_gate_code"], CODE_BLOCKERS_PRESENT)
        self.assertFalse(artifacts["report_gate_acceptance"]["allow"])


if __name__ == "__main__":
    unittest.main()

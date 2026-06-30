import json
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline.phase import PhaseResult
from ai_project_ctl.pipeline.report_phase import REPORT_STALE, collect_report_phase
from ai_project_ctl.pipeline.session import create_session, record_phase_result


TASK_ID = "TASK-001"
TASK_REF = "APP-01"


def write_project_state(root: Path) -> None:
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
                        "ref": TASK_REF,
                        "uid": "uid_task_001",
                        "legacy_id": TASK_ID,
                        "aliases": [TASK_ID],
                        "title": "Collect report recovery metadata",
                        "summary": "Exercise collect-report recovery binding.",
                        "description": "",
                        "scope": ["Record recovery metadata."],
                        "out_of_scope": ["Do not close the task."],
                        "acceptance_criteria": ["Recovery metadata is recorded."],
                        "review_instructions": [],
                        "status": "ready",
                        "epic_id": "EPIC-001",
                        "priority": 1,
                        "order": 1,
                        "local_seq": 1,
                        "depends_on": [],
                        "allowed_files": [
                            "ai_project_ctl/pipeline/report_phase.py",
                            "tests/test_pipeline_report_phase.py",
                        ],
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


def create_current_task_session(root: Path) -> str:
    result = create_session(
        root=root,
        actor="tester",
        policy_name="supervised",
        current_task_id=TASK_ID,
        current_task_ref=TASK_REF,
    )
    if not result.ok:
        raise AssertionError(result.errors)
    return str(result.data["session_id"])


def report_record(report_id: str, submitted_at: str) -> dict:
    return {
        "id": report_id,
        "task_id": TASK_ID,
        "task_ref": TASK_REF,
        "submitted_at": submitted_at,
        "submitted_by": "tester",
        "source_file": "/tmp/report.json",
        "report": {
            "task_id": TASK_ID,
            "task_ref": TASK_REF,
            "reported_task_id": TASK_ID,
            "reported_task_ref": TASK_REF,
        },
    }


def write_report_state(
    root: Path,
    *,
    latest_report_id: str,
    reports: list[dict],
) -> None:
    path = root / "AI_PROJECT" / "state" / "task_reports.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "created_at": "2026-06-25T00:00:00Z",
                "updated_at": "2026-06-25T00:00:10Z",
                "latest_by_task": {TASK_ID: latest_report_id},
                "reports": reports,
            }
        ),
        encoding="utf-8",
    )


def record_execute_report(root: Path, session_id: str, *, report_id: str) -> None:
    result = record_phase_result(
        session_id,
        PhaseResult.passed(
            "execute",
            reason="Fake execution completed.",
            artifacts={
                "task_id": TASK_ID,
                "execute_started_at": "2026-06-25T00:00:00Z",
                "execute_finished_at": "2026-06-25T00:00:05Z",
                "before_report_id": "",
                "after_report_id": report_id,
                "report_id": report_id,
                "execute_evidence": {
                    "started_at": "2026-06-25T00:00:00Z",
                    "finished_at": "2026-06-25T00:00:05Z",
                    "report_id": report_id,
                },
            },
        ),
        root=root,
        actor="tester",
        task_id=TASK_ID,
        command="pipeline.phase.execute",
    )
    if not result.ok:
        raise AssertionError(result.errors)


class PipelineReportPhaseRecoveryTests(unittest.TestCase):
    def test_collect_report_normal_fresh_report_has_no_recovery_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root)
            write_report_state(
                root,
                latest_report_id="RPT-EXEC",
                reports=[
                    report_record("RPT-EXEC", "2026-06-25T00:00:10Z"),
                ],
            )
            session_id = create_current_task_session(root)
            record_execute_report(root, session_id, report_id="RPT-EXEC")

            result = collect_report_phase(session_id, root=root, actor="tester")

            phase = result.data["phase_result"]
            artifacts = phase["artifacts"]

            self.assertTrue(result.ok)
            self.assertEqual(phase["status"], "passed")
            self.assertEqual(artifacts["report_id"], "RPT-EXEC")
            self.assertEqual(artifacts["freshness"]["basis"], "report_id")
            self.assertFalse(artifacts["allow_existing_report"])
            self.assertNotIn("recovery", artifacts)

    def test_collect_report_blocks_stale_replacement_without_recovery_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root)
            write_report_state(
                root,
                latest_report_id="RPT-RECOVERY",
                reports=[
                    report_record("RPT-RECOVERY", "2026-06-24T23:59:00Z"),
                ],
            )
            session_id = create_current_task_session(root)
            record_execute_report(root, session_id, report_id="RPT-EXEC")

            result = collect_report_phase(session_id, root=root, actor="tester")

            phase = result.data["phase_result"]
            artifacts = phase["artifacts"]

            self.assertTrue(result.ok)
            self.assertEqual(phase["status"], "blocked")
            self.assertEqual(artifacts["blocked_by"], REPORT_STALE)
            self.assertEqual(artifacts["freshness"]["fresh"], False)
            self.assertEqual(artifacts["freshness"]["basis"], "timestamp")
            self.assertNotIn("recovery", artifacts)

    def test_collect_report_recovery_override_records_replacement_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root)
            write_report_state(
                root,
                latest_report_id="RPT-RECOVERY",
                reports=[
                    report_record("RPT-RECOVERY", "2026-06-24T23:59:00Z"),
                ],
            )
            session_id = create_current_task_session(root)
            record_execute_report(root, session_id, report_id="RPT-EXEC")

            result = collect_report_phase(
                session_id,
                root=root,
                actor="tester",
                allow_existing_report=True,
            )

            phase = result.data["phase_result"]
            artifacts = phase["artifacts"]

            self.assertTrue(result.ok)
            self.assertEqual(phase["status"], "passed")
            self.assertEqual(artifacts["report_id"], "RPT-RECOVERY")
            self.assertEqual(artifacts["freshness_basis"], "recovery_override")
            self.assertEqual(
                artifacts["recovery"],
                {
                    "session_id": session_id,
                    "task_id": TASK_ID,
                    "owner_confirmed": True,
                    "recovery_basis": "recovery_override",
                    "recovery_report_id": "RPT-RECOVERY",
                    "replaced_execute_report_id": "RPT-EXEC",
                },
            )


if __name__ == "__main__":
    unittest.main()

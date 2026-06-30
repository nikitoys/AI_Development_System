import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline.phase import PhaseResult
from ai_project_ctl.pipeline.policy import policy_preset
from ai_project_ctl.pipeline.report_gate import (
    CODE_WARN,
    evaluate_report_gate,
)
from ai_project_ctl.pipeline.report_phase import collect_report_phase
from ai_project_ctl.pipeline.report_recovery import (
    REPORT_GATE_RECOVERY_TOKEN_STRATEGY,
    ReportRecoveryError,
    submit_report_gate_recovery_report,
)
from ai_project_ctl.pipeline.session import create_session, record_phase_result
from ai_project_ctl.pipeline.verify_phase import verify_phase


ROOT = Path(__file__).resolve().parents[1]
AICTL = ROOT / "scripts" / "aictl.py"
TASK_ID = "TASK-001"
TASK_REF = "APP-01"


def task_record(**overrides):
    task = {
        "id": TASK_ID,
        "ref": TASK_REF,
        "uid": "uid_task_001",
        "legacy_id": TASK_ID,
        "aliases": [TASK_ID],
        "title": "Recover report gate",
        "summary": "Exercise governed report recovery.",
        "description": "",
        "scope": ["Recover report gate evidence."],
        "out_of_scope": ["Do not bypass verification."],
        "acceptance_criteria": ["Recovery report is valid."],
        "review_instructions": [],
        "status": "in_progress",
        "epic_id": "EPIC-001",
        "priority": 1,
        "order": 1,
        "local_seq": 1,
        "depends_on": [],
        "allowed_files": ["ai_project_ctl/pipeline/report_recovery.py", "tests/**"],
    }
    task.update(overrides)
    return task


def write_project_state(root: Path, *, tasks=None) -> None:
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
                "current_task_id": TASK_ID,
                "tasks": list(tasks or [task_record()]),
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
        policy=policy_preset("supervised"),
        policy_name="supervised",
        current_task_id=TASK_ID,
        current_task_ref=TASK_REF,
    )
    if not result.ok:
        raise AssertionError(result.errors)
    return str(result.data["session_id"])


def report_payload(**overrides):
    report = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "task_ref": TASK_REF,
        "implementation_summary": "Recovered report gate fixture.",
        "changed_files": ["ai_project_ctl/pipeline/report_recovery.py"],
        "generated_files": [],
        "checks": [
            {
                "name": "unit",
                "command": "python -m unittest tests.test_pipeline_report_recovery",
                "result": "pass",
                "duration_sec": 0.1,
                "blocking": True,
                "details": "",
            }
        ],
        "warnings": [],
        "blockers": [],
        "notes": [],
        "owner_decision_required": False,
        "token_usage": {
            "prompt_tokens": 10,
            "context_tokens": 20,
            "token_count_strategy": "test_fixture",
            "token_count_estimated": True,
            "token_count_unavailable": False,
            "token_count_unavailable_reason": "",
        },
    }
    report.update(overrides)
    return report


def write_report_state(root: Path, report: dict) -> None:
    path = root / "AI_PROJECT" / "state" / "task_reports.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "created_at": "2026-06-30T00:00:00Z",
                "updated_at": "2026-06-30T00:00:00Z",
                "latest_by_task": {TASK_ID: "RPT-001"},
                "reports": [
                    {
                        "id": "RPT-001",
                        "task_id": TASK_ID,
                        "task_ref": TASK_REF,
                        "submitted_at": "2026-06-30T00:00:10Z",
                        "submitted_by": "tester",
                        "source_file": "/tmp/report.json",
                        "report": report,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def record_execute_report(root: Path, session_id: str) -> None:
    result = record_phase_result(
        session_id,
        PhaseResult.passed(
            "execute",
            artifacts={
                "task_id": TASK_ID,
                "execute_started_at": "2026-06-30T00:00:00Z",
                "execute_finished_at": "2026-06-30T00:00:05Z",
                "before_report_id": "",
                "after_report_id": "RPT-001",
                "report_id": "RPT-001",
                "execute_evidence": {
                    "started_at": "2026-06-30T00:00:00Z",
                    "finished_at": "2026-06-30T00:00:05Z",
                    "before_report_id": "",
                    "after_report_id": "RPT-001",
                    "report_id": "RPT-001",
                },
            },
        ),
        root=root,
        actor="tester",
        task_id=TASK_ID,
        command="test.execute",
    )
    if not result.ok:
        raise AssertionError(result.errors)


def prepare_blocked_verify_session(root: Path, report: dict) -> str:
    write_project_state(root)
    write_report_state(root, report)
    session_id = create_current_task_session(root)
    record_execute_report(root, session_id)
    collect = collect_report_phase(session_id, root=root, actor="tester")
    if not collect.ok:
        raise AssertionError(collect.errors)
    verify = verify_phase(session_id, root=root, actor="tester")
    if not verify.ok:
        raise AssertionError(verify.errors)
    return session_id


def latest_report(root: Path) -> dict:
    state = json.loads(
        (root / "AI_PROJECT" / "state" / "task_reports.json").read_text(
            encoding="utf-8"
        )
    )
    latest_id = state["latest_by_task"][TASK_ID]
    for record in state["reports"]:
        if record["id"] == latest_id:
            return record
    raise AssertionError("latest report missing")


def duplicate_session(root: Path, session_id: str) -> None:
    path = root / "AI_PROJECT" / "state" / "pipeline_sessions.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    for session in state["sessions"]:
        if session["id"] == session_id:
            state["sessions"].append(dict(session))
            break
    else:
        raise AssertionError("session missing")
    path.write_text(json.dumps(state), encoding="utf-8")


class PipelineReportRecoveryTests(unittest.TestCase):
    def test_recovery_requires_owner_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ReportRecoveryError) as raised:
                submit_report_gate_recovery_report(
                    "PSESS-001",
                    root=Path(tmp),
                    actor="tester",
                    expected_task_id=TASK_ID,
                    expected_task_ref=TASK_REF,
                    recovery_reason="Owner has not confirmed recovery.",
                )

            self.assertIn(
                "REPORT_GATE_RECOVERY_CONFIRMATION_REQUIRED",
                str(raised.exception),
            )

    def test_aictl_recover_adds_estimated_token_usage_and_collect_report_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = report_payload()
            del report["token_usage"]
            session_id = prepare_blocked_verify_session(root, report)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(AICTL),
                    "--root",
                    str(root),
                    "--actor",
                    "tester",
                    "--json",
                    "pipeline",
                    "report",
                    "recover",
                    session_id,
                    "--expected-task-id",
                    TASK_ID,
                    "--expected-task-ref",
                    TASK_REF,
                    "--reason",
                    "Owner confirmed the recovery report should use estimated token usage.",
                    "--confirm",
                ],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["data"]["replaced_report_id"], "RPT-001")
            self.assertIn("--allow-existing-report", payload["next_actions"][0])

            recovered = latest_report(root)
            self.assertEqual(recovered["id"], "RPT-002")
            token_usage = recovered["report"]["token_usage"]
            self.assertEqual(
                token_usage["token_count_strategy"],
                REPORT_GATE_RECOVERY_TOKEN_STRATEGY,
            )
            self.assertTrue(token_usage["token_count_estimated"])
            self.assertFalse(token_usage["token_count_unavailable"])

            gate = evaluate_report_gate(
                root=root,
                task=task_record(),
                policy=policy_preset("supervised"),
            )
            self.assertEqual(gate.code, CODE_WARN)
            self.assertFalse(gate.issues)

            collect = collect_report_phase(
                session_id,
                root=root,
                actor="tester",
                allow_existing_report=True,
            )
            artifacts = collect.data["phase_result"]["artifacts"]
            self.assertEqual(artifacts["recovery"]["recovery_report_id"], "RPT-002")
            self.assertEqual(artifacts["recovery"]["replaced_execute_report_id"], "RPT-001")

    def test_owner_warning_required_before_triaging_blockers_and_failed_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session_id = prepare_blocked_verify_session(
                root,
                report_payload(
                    blockers=["Owner must classify this blocker before recovery."],
                    checks=[
                        {
                            "name": "focused tests",
                            "command": "python -m unittest tests.test_pipeline_report_recovery",
                            "result": "fail",
                            "duration_sec": 0.1,
                            "blocking": True,
                            "details": "Test failed before owner triage.",
                        }
                    ],
                ),
            )

            with self.assertRaises(ReportRecoveryError) as raised:
                submit_report_gate_recovery_report(
                    session_id,
                    root=root,
                    actor="tester",
                    expected_task_id=TASK_ID,
                    expected_task_ref=TASK_REF,
                    recovery_reason="Owner reviewed the failed check.",
                    owner_confirmed=True,
                )
            self.assertIn("REPORT_GATE_RECOVERY_WARNING_REQUIRED", str(raised.exception))

            result = submit_report_gate_recovery_report(
                session_id,
                root=root,
                actor="tester",
                expected_task_id=TASK_ID,
                expected_task_ref=TASK_REF,
                recovery_reason="Owner reviewed and classified the failed check as nonblocking.",
                warning_texts=("Nonblocking warning confirmed by owner.",),
                owner_confirmed=True,
            )

            self.assertTrue(result.ok)
            recovered = latest_report(root)["report"]
            self.assertEqual(recovered["blockers"], [])
            self.assertIn("Nonblocking warning confirmed by owner.", recovered["warnings"])
            self.assertTrue(
                any("original blocker" in warning for warning in recovered["warnings"])
            )
            self.assertEqual(recovered["checks"][0]["result"], "warn")
            self.assertFalse(recovered["checks"][0]["blocking"])

            gate = evaluate_report_gate(
                root=root,
                task=task_record(),
                policy=policy_preset("supervised"),
            )
            self.assertEqual(gate.code, CODE_WARN)
            self.assertFalse(gate.issues)

    def test_recovery_refuses_ambiguous_session_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session_id = prepare_blocked_verify_session(root, report_payload(blockers=["Needs triage."]))
            duplicate_session(root, session_id)

            with self.assertRaises(ReportRecoveryError) as raised:
                submit_report_gate_recovery_report(
                    session_id,
                    root=root,
                    actor="tester",
                    expected_task_id=TASK_ID,
                    expected_task_ref=TASK_REF,
                    recovery_reason="Owner cannot resolve ambiguous session identity.",
                    warning_texts=("Nonblocking warning confirmed by owner.",),
                    owner_confirmed=True,
                )

            self.assertIn("REPORT_RECOVERY_SESSION_AMBIGUOUS", str(raised.exception))

    def test_recovery_refuses_ambiguous_task_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session_id = prepare_blocked_verify_session(root, report_payload(blockers=["Needs triage."]))
            write_project_state(
                root,
                tasks=[
                    task_record(),
                    task_record(id="TASK-002", ref="APP-02", aliases=[TASK_ID]),
                ],
            )

            with self.assertRaises(ReportRecoveryError) as raised:
                submit_report_gate_recovery_report(
                    session_id,
                    root=root,
                    actor="tester",
                    expected_task_id=TASK_ID,
                    expected_task_ref=TASK_REF,
                    recovery_reason="Owner cannot resolve ambiguous task identity.",
                    warning_texts=("Nonblocking warning confirmed by owner.",),
                    owner_confirmed=True,
                )

            self.assertIn("REPORT_RECOVERY_TASK_AMBIGUOUS", str(raised.exception))


if __name__ == "__main__":
    unittest.main()

import json
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline import policy_preset
from ai_project_ctl.pipeline.batch import run_until_blocker
from ai_project_ctl.pipeline.runner import run_next
from ai_project_ctl.pipeline.session import create_session
from ai_project_ctl.pipeline.state import pipeline_events_path, pipeline_state_path

from tests.test_pipeline_batch import (
    batch_review_output,
    batch_workflow_runner,
    write_batch_project_state,
)


class PipelineEndToEndTests(unittest.TestCase):
    def test_executable_autoclose_processes_two_task_queue_with_fake_codex(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_batch_project_state(root, task_count=2, change_status="accepted")
            policy = policy_preset("supervised_executable_autoclose")
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                max_tasks=2,
                auto_close_note="Owner approved auto-close for this selected session.",
            )
            calls = []
            fake_runner, task_status = batch_workflow_runner(calls, root=root)

            result = run_until_blocker(
                session.data["session_id"],
                root=root,
                actor="tester",
                confirmed=True,
                runner=fake_runner,
                codex_reviewer=batch_review_output,
            )
            state = json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))
            latest = state["sessions"][0]
            first_gates = latest["steps"][0]["gate_outcomes"]
            event_text = pipeline_events_path(root).read_text(encoding="utf-8")

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "QUEUE_COMPLETE")
            self.assertEqual(result.data["completed_tasks"], ["TASK-001", "TASK-002"])
            self.assertEqual(task_status["TASK-001"], "done")
            self.assertEqual(task_status["TASK-002"], "done")
            self.assertEqual(latest["status"], "completed")
            self.assertEqual(
                [gate["name"] for gate in first_gates],
                [
                    "token_budget_gate",
                    "codex_execution_adapter",
                    "codex_report_gate",
                    "machine_review_gate",
                    "codex_review_gate",
                    "review_close_gate",
                ],
            )
            self.assertEqual(first_gates[-1]["status"], "pass")
            self.assertIn("RPT-001", latest["report_ids"])
            self.assertIn("pipeline.step.result", event_text)
            self.assertIn("pipeline.session.complete", event_text)
            self.assertTrue(any(call == ["codex", "exec"] for call in calls))
            forbidden = {"push", "merge", "reset", "rebase", "clean", "restore"}
            self.assertFalse(any(forbidden & set(call) for call in calls))

    def test_executable_autoclose_requires_owner_auto_close_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_batch_project_state(root, task_count=1, change_status="accepted")
            policy = policy_preset("supervised_executable_autoclose")
            session = create_session(root=root, actor="tester", policy=policy, max_tasks=1)
            calls = []
            fake_runner, task_status = batch_workflow_runner(calls, root=root)

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=fake_runner,
                codex_reviewer=batch_review_output,
            )
            latest = json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))["sessions"][0]
            close_gate = latest["steps"][0]["gate_outcomes"][-1]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "AUTO_CLOSE_OWNER_NOTE_REQUIRED")
            self.assertEqual(close_gate["name"], "review_close_gate")
            self.assertEqual(close_gate["status"], "blocked")
            self.assertNotEqual(task_status["TASK-001"], "done")


if __name__ == "__main__":
    unittest.main()

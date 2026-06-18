import subprocess
import unittest
from pathlib import Path

from ai_project_ctl.core.workflows import (
    run_workflow,
    workflow_describe,
    workflow_list,
)


def completed(stdout="OK\n", returncode=0, stderr=""):
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


class WorkflowTests(unittest.TestCase):
    def test_workflow_list_and_describe_expose_task_workflows(self):
        names = [workflow["name"] for workflow in workflow_list()]
        descriptor = workflow_describe("task.prepare_for_codex")

        self.assertIn("task.prepare_for_codex", names)
        self.assertIn("task.refresh_execution_context", names)
        self.assertIn("task.submit_for_review", names)
        self.assertTrue(descriptor["confirmation_required"])
        self.assertIn("steps", descriptor)

    def test_workflow_run_requires_confirmation_before_runner_is_called(self):
        calls = []

        result = run_workflow(
            "task.refresh_execution_context",
            task_ref="WFA-01",
            confirmed=False,
            runner=lambda argv: calls.append(argv) or completed(),
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.errors[0].code, "WORKFLOW_CONFIRMATION_REQUIRED")
        self.assertEqual(calls, [])
        self.assertIn("steps", result.data)

    def test_prepare_for_codex_skips_in_progress_transition(self):
        calls = []

        def fake_run(argv):
            calls.append(list(argv))
            if Path(argv[1]).name == "taskctl.py" and "resolve" in argv:
                return completed(
                    '{"id": "TASK-032", "ref": "WFA-01", "status": "in_progress"}\n'
                )
            return completed('{"ok": true}\n')

        result = run_workflow(
            "task.prepare_for_codex",
            task_ref="WFA-01",
            confirmed=True,
            runner=fake_run,
        )

        tails = [" ".join(call[-6:]) for call in calls]
        statuses = {step["id"]: step["status"] for step in result.data["steps"]}

        self.assertTrue(result.ok)
        self.assertEqual(statuses["task_in_progress"], "skipped")
        self.assertFalse(any("task transition TASK-032 --to in_progress" in tail for tail in tails))
        self.assertTrue(any("context build --task TASK-032 --write" in tail for tail in tails))
        self.assertTrue(any("prompt build --task TASK-032 --with-context" in tail for tail in tails))

    def test_workflow_stops_on_first_blocking_failure(self):
        calls = []

        def fake_run(argv):
            calls.append(list(argv))
            if Path(argv[1]).name == "taskctl.py" and "resolve" in argv:
                return completed(
                    '{"id": "TASK-032", "ref": "WFA-01", "status": "in_progress"}\n'
                )
            return completed("context failed\n", returncode=2)

        result = run_workflow(
            "task.refresh_execution_context",
            task_ref="WFA-01",
            confirmed=True,
            runner=fake_run,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.errors[0].code, "WORKFLOW_STEP_FAILED")
        self.assertEqual([step["id"] for step in result.data["steps"]], ["resolve", "context_build"])
        self.assertEqual(len(calls), 2)


if __name__ == "__main__":
    unittest.main()

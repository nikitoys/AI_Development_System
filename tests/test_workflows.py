import subprocess
import unittest
from pathlib import Path

from ai_project_ctl.core.workflows import (
    TaskCreateRequest,
    run_workflow,
    run_task_create_workflow,
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
        self.assertIn("task.create_single", names)
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

    def test_task_create_workflow_requires_confirmation_before_runner_is_called(self):
        calls = []

        result = run_task_create_workflow(
            TaskCreateRequest(epic="EPIC-006", title="New task"),
            confirmed=False,
            runner=lambda argv: calls.append(argv) or completed(),
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.errors[0].code, "WORKFLOW_CONFIRMATION_REQUIRED")
        self.assertEqual(calls, [])
        self.assertTrue(result.data["create_only"])
        self.assertEqual(result.data["steps"][0]["id"], "task_create")

    def test_task_create_workflow_creates_task_adds_dependencies_and_does_not_start_it(self):
        calls = []

        def fake_run(argv):
            calls.append(list(argv))
            if Path(argv[1]).name == "taskctl.py" and list(argv[6:8]) == ["task", "create"]:
                return completed("OK: task.create revision 1 -> 2\nCreated: WFA-07 (TASK-099)\n")
            return completed("OK\n")

        result = run_task_create_workflow(
            TaskCreateRequest(
                epic="EPIC-006",
                title="Create from workflow",
                summary="Short task.",
                scope=("Do one thing",),
                allowed_files=("README.md",),
                acceptance=("Validation passes",),
                depends_on=("TASK-032",),
                dependency_reason="Requires WFA foundation.",
            ),
            confirmed=True,
            runner=fake_run,
        )

        command_tails = [" ".join(call[6:]) for call in calls]

        self.assertTrue(result.ok)
        self.assertEqual(result.data["created_task_id"], "TASK-099")
        self.assertTrue(result.data["create_only"])
        self.assertIn(
            "task deps add TASK-099 --after TASK-032 --type hard --reason Requires WFA foundation.",
            command_tails,
        )
        self.assertIn("task graph validate", command_tails)
        self.assertIn("check-generated", command_tails)
        self.assertFalse(any("current set" in tail for tail in command_tails))
        self.assertFalse(any("task transition" in tail for tail in command_tails))
        self.assertTrue(any("task.prepare_for_codex" in action for action in result.next_actions))


if __name__ == "__main__":
    unittest.main()

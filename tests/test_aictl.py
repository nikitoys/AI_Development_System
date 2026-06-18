import importlib.util
import io
import json
import subprocess
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
AICTL_PATH = ROOT / "scripts" / "aictl.py"


def load_aictl():
    spec = importlib.util.spec_from_file_location("aictl_test_module", AICTL_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AictlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aictl = load_aictl()

    def run_main(self, argv, completed=None):
        stdout = io.StringIO()
        if completed is None:
            with redirect_stdout(stdout):
                code = self.aictl.main(argv)
            return code, stdout.getvalue(), None

        with patch.object(self.aictl.subprocess, "run", return_value=completed) as run:
            with redirect_stdout(stdout):
                code = self.aictl.main(argv)
        return code, stdout.getvalue(), run

    def test_command_list_json_uses_registry(self):
        code, stdout, _run = self.run_main(["--json", "command", "list"])

        payload = json.loads(stdout)
        names = [command["name"] for command in payload["data"]["commands"]]

        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertIn("command.describe", names)
        self.assertIn("project.render", names)
        self.assertIn("task.transition", names)

    def test_command_describe_human_output(self):
        code, stdout, _run = self.run_main(["command", "describe", "task.transition"])

        self.assertEqual(code, 0)
        self.assertIn("task.transition (write, implemented)", stdout)
        self.assertIn("Transition a Task", stdout)
        self.assertIn("Legacy: python scripts/taskctl.py", stdout)

    def test_task_list_delegates_with_native_json(self):
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='[{"id": "TASK-001"}]\n',
            stderr="",
        )

        code, stdout, run = self.run_main(
            ["--root", "/tmp/project", "--actor", "tester", "--json", "task", "list", "--status", "ready"],
            completed,
        )

        argv = run.call_args.args[0]
        payload = json.loads(stdout)

        self.assertEqual(code, 0)
        self.assertIn("taskctl.py", argv[1])
        self.assertEqual(argv[2:6], ["--root", "/tmp/project", "--actor", "tester"])
        self.assertEqual(argv[-5:], ["task", "list", "--status", "ready", "--json"])
        self.assertEqual(payload["data"]["result"], [{"id": "TASK-001"}])

    def test_task_transition_delegates_write_without_native_json(self):
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="OK: transitioned CTL-06 from in_progress to in_review\n",
            stderr="",
        )

        code, stdout, run = self.run_main(
            ["--json", "task", "transition", "CTL-06", "--to", "in_review"],
            completed,
        )

        argv = run.call_args.args[0]
        payload = json.loads(stdout)

        self.assertEqual(code, 0)
        self.assertEqual(argv[-5:], ["task", "transition", "CTL-06", "--to", "in_review"])
        self.assertNotIn("--json", argv)
        self.assertTrue(payload["ok"])
        self.assertIn("transitioned CTL-06", payload["data"]["stdout"])

    def test_codex_prompt_build_resolves_task_ref_before_delegating(self):
        resolve = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"id": "TASK-024", "ref": "CTL-06"}\n',
            stderr="",
        )
        build = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="OK: CODEX_READY\n",
            stderr="",
        )
        stdout = io.StringIO()

        with patch.object(self.aictl.subprocess, "run", side_effect=[resolve, build]) as run:
            with redirect_stdout(stdout):
                code = self.aictl.main(
                    ["--json", "codex", "prompt", "build", "--task", "CTL-06"]
                )

        first_argv = run.call_args_list[0].args[0]
        second_argv = run.call_args_list[1].args[0]
        payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(first_argv[-4:], ["task", "resolve", "CTL-06", "--json"])
        self.assertEqual(second_argv[-3:], ["build", "--task", "TASK-024"])
        self.assertTrue(payload["ok"])

    def test_project_doctor_delegates_to_protected_file_check(self):
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"ok": true, "errors": []}\n',
            stderr="",
        )

        code, stdout, run = self.run_main(["--json", "project", "doctor"], completed)

        argv = run.call_args.args[0]
        payload = json.loads(stdout)

        self.assertEqual(code, 0)
        self.assertIn("check-protected-project-files.py", argv[1])
        self.assertNotIn("--actor", argv)
        self.assertEqual(argv[-1], "--json")
        self.assertEqual(payload["data"]["result"]["ok"], True)

    def test_project_render_runs_legacy_render_steps(self):
        completed = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="OK: rendered plan\n", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="OK: rendered tasks\n", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="OK: rendered docs\n", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="OK: rendered context\n", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="OK: rendered evolution\n", stderr=""),
        ]
        stdout = io.StringIO()

        with patch.object(self.aictl.subprocess, "run", side_effect=completed) as run:
            with redirect_stdout(stdout):
                code = self.aictl.main(["--json", "project", "render"])

        payload = json.loads(stdout.getvalue())
        scripts = [Path(call.args[0][1]).name for call in run.call_args_list]

        self.assertEqual(code, 0)
        self.assertEqual(
            scripts,
            ["planctl.py", "taskctl.py", "docctl.py", "contextctl.py", "evolutionctl.py"],
        )
        self.assertTrue(payload["ok"])
        self.assertEqual(len(payload["data"]["steps"]), 5)


if __name__ == "__main__":
    unittest.main()

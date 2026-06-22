import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ai_project_ctl.core.result import CommandResult
from ai_project_ctl.pipeline.codex_preflight import (
    CODE_PREFLIGHT_COMMAND_FAILED,
    CODE_PREFLIGHT_PASSED,
    CODE_PREFLIGHT_SANDBOX_UNAVAILABLE,
    PREFLIGHT_PROMPT,
    run_codex_preflight,
)
from ai_project_ctl.pipeline.state import pipeline_state_path
from ai_project_ctl.ui_settings import ui_settings_path
from scripts import aictl
from tests.test_pipeline_batch import write_batch_project_state


REPO_ROOT = Path(__file__).resolve().parents[2]
AICTL = REPO_ROOT / "scripts" / "aictl.py"


def completed(stdout="OK\n", returncode=0, stderr=""):
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def write_settings(root: Path, payload: dict) -> None:
    path = ui_settings_path(root)
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def run_aictl(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(AICTL), "--root", str(root), *args],
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class CodexPreflightTests(unittest.TestCase):
    def test_preflight_passes_prompt_to_effective_command_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_settings(
                root,
                {
                    "command_line": "codex exec --json",
                    "default_policy": "supervised_executable_local_commit",
                },
            )
            calls = []
            stdin_values = []

            def fake_runner(argv, stdin_text):
                calls.append(list(argv))
                stdin_values.append(stdin_text)
                return completed(stdout="ready\n")

            result = run_codex_preflight(root=root, runner=fake_runner)

        self.assertTrue(result.ok)
        self.assertEqual(result.data["status"], "passed")
        self.assertEqual(result.data["code"], CODE_PREFLIGHT_PASSED)
        self.assertEqual(result.data["command"], ["codex", "exec", "--json"])
        self.assertEqual(result.data["command_ref"], "codex exec --json")
        self.assertEqual(calls, [["codex", "exec", "--json"]])
        self.assertEqual(stdin_values, [PREFLIGHT_PROMPT])

    def test_preflight_blocks_known_sandbox_unavailable_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = run_codex_preflight(
                root=root,
                runner=lambda argv, stdin_text: completed(
                    returncode=1,
                    stderr=(
                        "bwrap: RTM_NEWADDR failed: Operation not permitted; "
                        "user namespace unavailable\n"
                    ),
                ),
            )

        self.assertTrue(result.ok)
        self.assertEqual(result.data["status"], "blocked")
        self.assertEqual(result.data["code"], CODE_PREFLIGHT_SANDBOX_UNAVAILABLE)
        self.assertIn("bwrap", result.data["stderr_snippet"])
        self.assertIsNotNone(result.owner_action_required)

    def test_preflight_fails_non_sandbox_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = run_codex_preflight(
                root=root,
                runner=lambda argv, stdin_text: completed(
                    returncode=2,
                    stderr="ordinary command failure\n",
                ),
            )

        self.assertFalse(result.ok)
        self.assertEqual(result.data["status"], "failed")
        self.assertEqual(result.data["code"], CODE_PREFLIGHT_COMMAND_FAILED)
        self.assertEqual(result.errors[0].code, CODE_PREFLIGHT_COMMAND_FAILED)

    def test_aictl_ui_preflight_uses_configured_command_without_state_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_settings(
                root,
                {
                    "command_line": (
                        "{} -c \"import sys; sys.stdin.read(); print('ready')\""
                    ).format(sys.executable),
                    "default_policy": "supervised_executable_local_commit",
                },
            )

            completed_process = run_aictl(root, "--json", "ui", "preflight")

            self.assertEqual(completed_process.returncode, 0, completed_process.stderr)
            payload = json.loads(completed_process.stdout)
            self.assertEqual(payload["data"]["status"], "passed")
            self.assertFalse((root / "AI_PROJECT" / "state").exists())
            self.assertFalse((root / "AI_PROJECT" / "generated").exists())

    def test_ui_run_preflight_blocks_before_session_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_batch_project_state(root, task_count=1)
            blocked = CommandResult.success(
                command="ui.preflight",
                domain="ui",
                message="Codex preflight blocked: local Codex sandbox is unavailable.",
                data={
                    "status": "blocked",
                    "phase_status": "blocked",
                    "code": CODE_PREFLIGHT_SANDBOX_UNAVAILABLE,
                    "reason": "sandbox_unavailable",
                },
            )
            blocked.owner_action_required = "Fix local sandbox support."
            args = aictl.build_parser().parse_args(
                [
                    "--root",
                    str(root),
                    "--actor",
                    "tester",
                    "ui",
                    "run",
                    "APP-01",
                    "--confirm",
                    "--preflight",
                ]
            )
            args.json = True

            stdout = io.StringIO()
            with mock.patch.object(aictl, "run_codex_preflight", return_value=blocked):
                with mock.patch.object(aictl, "create_session") as create_session:
                    with contextlib.redirect_stdout(stdout):
                        exit_code = args.func(args)

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["data"]["outcome"], "blocked")
            create_session.assert_not_called()
            self.assertFalse(pipeline_state_path(root).exists())


if __name__ == "__main__":
    unittest.main()

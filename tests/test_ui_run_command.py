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
from ai_project_ctl.pipeline.state import pipeline_state_path
from ai_project_ctl.ui_settings import ui_settings_path
from scripts import aictl
from tests.test_pipeline_batch import write_batch_project_state


REPO_ROOT = Path(__file__).resolve().parents[1]
AICTL = REPO_ROOT / "scripts" / "aictl.py"


def run_aictl(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(AICTL), "--root", str(root), *args],
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def write_settings(root: Path, payload: dict) -> None:
    path = ui_settings_path(root)
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class UIRunCommandTests(unittest.TestCase):
    def test_ui_run_creates_single_task_session_and_requires_confirm(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_batch_project_state(root, task_count=1)

            completed = run_aictl(root, "--json", "ui", "run", "APP-01")

            self.assertEqual(completed.returncode, 1)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["command"], "ui.run")
            self.assertEqual(payload["data"]["outcome"], "confirmation_required")
            self.assertEqual(payload["errors"][0]["code"], "UI_RUN_CONFIRMATION_REQUIRED")

            state = json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))
            session = state["sessions"][0]
            self.assertEqual(session["selected_queue"]["task_refs"], ["APP-01"])
            self.assertEqual(session["selected_queue"]["max_tasks"], 1)
            self.assertEqual(session["selected_queue"]["order_by"], "selected")

    def test_ui_run_confirm_uses_effective_executable_policy_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_batch_project_state(root, task_count=1)
            write_settings(
                root,
                {
                    "default_policy": "supervised_executable_local_commit",
                    "command_line": "codex exec --json",
                },
            )
            run_result = CommandResult.success(
                command="pipeline.run_until_blocker",
                domain="pipeline",
                message="QUEUE_COMPLETE: Selected queue completed.",
                data={
                    "session_id": "PSESS-001",
                    "stop_code": "QUEUE_COMPLETE",
                    "session_status": "completed",
                },
            )
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
                ]
            )
            args.json = True

            stdout = io.StringIO()
            with mock.patch.object(
                aictl,
                "run_pipeline_until_blocker",
                return_value=run_result,
            ) as runner:
                with contextlib.redirect_stdout(stdout):
                    exit_code = args.func(args)

            self.assertEqual(exit_code, 0)
            runner.assert_called_once_with(
                "PSESS-001",
                root=str(root),
                actor="tester",
                confirmed=True,
            )
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["data"]["outcome"], "completed")

            state = json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))
            session = state["sessions"][0]
            self.assertEqual(
                session["policy_snapshot"]["codex"]["local_command"],
                ["codex", "exec", "--json"],
            )
            self.assertEqual(
                session["policy_snapshot"]["codex"]["command_allowlist"],
                ["codex exec --json"],
            )
            self.assertEqual(session["selected_queue"]["task_refs"], ["APP-01"])
            self.assertEqual(session["selected_queue"]["max_tasks"], 1)

    def test_ui_run_reports_blocked_and_failed_outcomes_clearly(self):
        blocked = CommandResult.success(
            command="pipeline.run_until_blocker",
            domain="pipeline",
            message="TOKEN_GATE_BLOCKED: needs owner action",
            data={
                "session_id": "PSESS-001",
                "stop_code": "TOKEN_GATE_BLOCKED",
                "session_status": "blocked",
            },
        )
        failed = CommandResult.failure(
            command="pipeline.run_until_blocker",
            domain="pipeline",
            message="Batch runner failed.",
        )

        blocked_result = aictl._ui_run_result("APP-01", "supervised", blocked, blocked)
        failed_result = aictl._ui_run_result("APP-01", "supervised", failed, failed)

        self.assertTrue(blocked_result.ok)
        self.assertEqual(blocked_result.data["outcome"], "blocked")
        self.assertIn("UI run blocked", blocked_result.message)
        self.assertFalse(failed_result.ok)
        self.assertEqual(failed_result.data["outcome"], "failed")
        self.assertIn("UI run failed", failed_result.message)


if __name__ == "__main__":
    unittest.main()

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from ai_project_ctl.core.result import CommandResult
from ai_project_ctl.pipeline.git_status import capture_worktree_dirty_preflight
from ai_project_ctl.pipeline.policy import QueuePolicy, QueueSelection, policy_preset
from ai_project_ctl.pipeline.queue_phase import preview_queue_phase
from ai_project_ctl.pipeline.session import create_session
from ai_project_ctl.pipeline.state import pipeline_state_path
from ai_project_ctl.pipeline.ui_run import (
    build_ui_run_batch_queue,
    build_ui_run_selected_queue,
    resolve_ui_run_selection,
)
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
    def test_ui_run_batch_queue_builds_multiple_task_refs(self):
        queue = build_ui_run_batch_queue(
            policy_preset("supervised"),
            task_refs=("APP-01", "APP-02"),
            max_tasks=2,
            order_by="selected",
            confirmed=True,
            allow_internal_change_gate_bypass=True,
        )

        self.assertEqual(
            queue,
            {
                "selection": "ready_queue",
                "task_refs": ["APP-01", "APP-02"],
                "epic_ids": [],
                "statuses": [],
                "max_tasks": 2,
                "order_by": "selected",
                "include_blocked_tasks": False,
                "created_by_command": "ui.run_task_batch",
                "ui_run_confirmed": True,
                "allow_internal_change_gate_bypass": True,
            },
        )

    def test_ui_run_batch_queue_builds_epic_status_selection(self):
        queue = build_ui_run_batch_queue(
            policy_preset("supervised"),
            epic_ids=("EPIC-009",),
            statuses=("ready", "in_progress"),
            max_tasks="3",
            confirmed=False,
            allow_internal_change_gate_bypass=False,
        )

        self.assertEqual(queue["task_refs"], [])
        self.assertEqual(queue["epic_ids"], ["EPIC-009"])
        self.assertEqual(queue["statuses"], ["ready", "in_progress"])
        self.assertEqual(queue["max_tasks"], 3)
        self.assertEqual(queue["order_by"], "execution")
        self.assertFalse(queue["ui_run_confirmed"])
        self.assertFalse(queue["allow_internal_change_gate_bypass"])

    def test_ui_run_batch_queue_is_session_and_preview_compatible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_batch_project_state(root, task_count=2)
            queue = build_ui_run_batch_queue(
                policy_preset("supervised"),
                task_refs=("APP-02", "APP-01"),
                max_tasks=2,
                order_by="selected",
                confirmed=True,
                allow_internal_change_gate_bypass=False,
            )

            created = create_session(
                root=root,
                actor="tester",
                policy_name="supervised",
                selected_queue=queue,
            )
            preview = preview_queue_phase(root=root)

            self.assertTrue(created.ok, created.errors)
            self.assertTrue(preview.ok, preview.errors)
            state = json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))
            self.assertEqual(state["sessions"][0]["selected_queue"]["max_tasks"], 2)
            executable_refs = [
                item["ref"]
                for item in preview.data["queue_preview"]["executable"]
            ]
            self.assertEqual(executable_refs, ["APP-02", "APP-01"])

    def test_ui_run_batch_queue_preserves_policy_defaults_when_omitted(self):
        policy = replace(
            policy_preset("supervised"),
            queue=QueuePolicy(
                selection=QueueSelection.MANUAL,
                max_tasks=4,
                include_blocked_tasks=True,
            ),
        )

        queue = build_ui_run_batch_queue(
            policy,
            statuses=("ready",),
            confirmed=True,
            allow_internal_change_gate_bypass=False,
        )

        self.assertEqual(queue["selection"], "manual")
        self.assertEqual(queue["max_tasks"], 4)
        self.assertEqual(queue["include_blocked_tasks"], True)
        self.assertEqual(queue["order_by"], "execution")

    def test_ui_run_batch_queue_rejects_non_positive_max_tasks(self):
        invalid_values = (0, -1, "0", "abc", True)

        for invalid in invalid_values:
            with self.subTest(max_tasks=invalid):
                with self.assertRaises(ValueError):
                    build_ui_run_batch_queue(
                        policy_preset("supervised"),
                        task_refs=("APP-01",),
                        max_tasks=invalid,
                        confirmed=True,
                        allow_internal_change_gate_bypass=False,
                    )

    def test_ui_run_selected_queue_remains_single_task(self):
        queue = build_ui_run_selected_queue(
            policy_preset("supervised"),
            "APP-01",
            confirmed=True,
            allow_internal_change_gate_bypass=True,
        )

        self.assertEqual(queue["task_refs"], ["APP-01"])
        self.assertEqual(queue["max_tasks"], 1)
        self.assertEqual(queue["order_by"], "selected")

    def test_worktree_dirty_preflight_reports_git_status_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(
                ["git", "init"],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            (root / "dirty.txt").write_text("dirty\n", encoding="utf-8")
            (root / "nested").mkdir()
            (root / "nested" / "new.txt").write_text("new\n", encoding="utf-8")

            dirty = capture_worktree_dirty_preflight(root=root)

            self.assertTrue(dirty.checked)
            self.assertTrue(dirty.available)
            self.assertEqual(dirty.reason, "worktree_dirty")
            self.assertEqual(dirty.dirty_paths, ("dirty.txt", "nested/new.txt"))
            self.assertCountEqual(
                [entry.to_dict() for entry in dirty.entries],
                [
                    {"status": "??", "path": "dirty.txt"},
                    {"status": "??", "path": "nested/new.txt"},
                ],
            )

    def test_worktree_dirty_preflight_allows_non_git_test_roots(self):
        with tempfile.TemporaryDirectory() as tmp:
            preflight = capture_worktree_dirty_preflight(root=Path(tmp))

        self.assertFalse(preflight.checked)
        self.assertFalse(preflight.available)
        self.assertFalse(preflight.should_block)
        self.assertEqual(preflight.reason, "worktree_clean")

    def test_ui_run_selection_resolves_done_task_without_creating_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_batch_project_state(root, task_count=1)
            tasks_path = root / "AI_PROJECT" / "state" / "tasks.json"
            tasks_state = json.loads(tasks_path.read_text(encoding="utf-8"))
            tasks_state["tasks"][0]["status"] = "done"
            tasks_path.write_text(json.dumps(tasks_state), encoding="utf-8")

            resolution = resolve_ui_run_selection(root, "APP-01")

            self.assertEqual(resolution.outcome, "not_run")
            self.assertEqual(resolution.task_id, "TASK-001")
            self.assertEqual(resolution.task_status, "done")
            self.assertEqual(resolution.session_id, "")
            self.assertFalse(pipeline_state_path(root).exists())

    def test_ui_run_selection_returns_existing_reusable_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_batch_project_state(root, task_count=1)
            pipeline_path = pipeline_state_path(root)
            pipeline_path.parent.mkdir(parents=True, exist_ok=True)
            pipeline_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "revision": 1,
                        "current_session_id": "PSESS-007",
                        "sessions": [
                            {
                                "id": "PSESS-007",
                                "status": "blocked",
                                "selected_queue": {"task_refs": ["APP-01"]},
                                "current_task_id": "TASK-001",
                                "current_task_ref": "APP-01",
                                "current_step": "run_next",
                                "current_step_status": "blocked",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            resolution = resolve_ui_run_selection(root, "TASK-001")

            self.assertEqual(resolution.outcome, "existing_session")
            self.assertEqual(resolution.session_id, "PSESS-007")
            self.assertEqual(resolution.session_status, "blocked")

    def test_ui_run_creates_single_task_session_and_requires_confirm(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_batch_project_state(root, task_count=1)
            write_settings(root, {"default_policy": "supervised"})

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
            self.assertEqual(session["selected_queue"]["created_by_command"], "ui.run")
            self.assertFalse(session["selected_queue"]["ui_run_confirmed"])
            self.assertFalse(
                session["selected_queue"]["allow_internal_change_gate_bypass"]
            )

    def test_ui_run_confirm_uses_effective_executable_policy_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_batch_project_state(root, task_count=1)
            write_settings(
                root,
                {
                    "default_policy": "supervised_executable_local_commit",
                    "command_line": "codex exec --json",
                    "execution_timeout_sec": "1200",
                    "allow_internal_change_gate_bypass": "true",
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
                    "--auto-close-note",
                    "Owner approved auto-close for UI run.",
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
            self.assertEqual(session["policy_snapshot"]["codex"]["timeout_sec"], 1200)
            self.assertEqual(session["selected_queue"]["task_refs"], ["APP-01"])
            self.assertEqual(session["selected_queue"]["max_tasks"], 1)
            self.assertTrue(session["selected_queue"]["ui_run_confirmed"])
            self.assertTrue(
                session["selected_queue"]["allow_internal_change_gate_bypass"]
            )

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

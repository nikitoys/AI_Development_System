import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ai_project_ctl.pipeline import BatchPolicy, CodexAdapterMode, CodexExecutionMode, policy_preset
from ai_project_ctl.pipeline.batch import run_until_blocker
from ai_project_ctl.pipeline.session import create_session
from ai_project_ctl.pipeline.state import pipeline_state_path

from tests.test_pipeline_runner import completed


def write_batch_project_state(root: Path, *, task_count: int = 2, change_status: str = "approved") -> None:
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True)
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
    tasks = []
    changes = []
    for index in range(1, task_count + 1):
        task_id = "TASK-{0:03d}".format(index)
        ref = "APP-{0:02d}".format(index)
        tasks.append(
            {
                "id": task_id,
                "ref": ref,
                "uid": "uid_task_{0:03d}".format(index),
                "legacy_id": task_id,
                "aliases": [task_id],
                "title": "Runnable task {}".format(index),
                "status": "ready",
                "epic_id": "EPIC-001",
                "priority": 1,
                "order": index,
                "local_seq": index,
                "depends_on": [],
                "allowed_files": [
                    "ai_project_ctl/pipeline/report_gate.py",
                    "tests/**",
                ],
            }
        )
        changes.append(
            {
                "id": "CHG-{0:03d}".format(index),
                "status": change_status,
                "linked_tasks": [task_id],
            }
        )
    (state_dir / "tasks.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "current_task_id": None,
                "tasks": tasks,
            }
        ),
        encoding="utf-8",
    )
    (state_dir / "evolution.json").write_text(
        json.dumps({"schema_version": 1, "revision": 1, "changes": changes}),
        encoding="utf-8",
    )


def write_report_state(root: Path, task_id: str, report_id: str) -> None:
    task_ref = "APP-{0:02d}".format(int(task_id.split("-")[1]))
    state_dir = root / "AI_PROJECT" / "state"
    existing = state_dir / "task_reports.json"
    if existing.exists():
        state = json.loads(existing.read_text(encoding="utf-8"))
    else:
        state = {
            "schema_version": 1,
            "revision": 0,
            "created_at": "2026-06-19T00:00:00Z",
            "updated_at": "2026-06-19T00:00:00Z",
            "latest_by_task": {},
            "reports": [],
        }
    state["revision"] += 1
    state["latest_by_task"][task_id] = report_id
    state["reports"].append(
        {
            "id": report_id,
            "task_id": task_id,
            "task_ref": task_ref,
            "submitted_at": "2026-06-19T00:00:00Z",
            "submitted_by": "tester",
            "source_file": "/tmp/report.json",
            "report": {
                "schema_version": 1,
                "task_id": task_id,
                "task_ref": task_ref,
                "reported_task_id": task_id,
                "reported_task_ref": task_ref,
                "implementation_summary": "Implemented the selected task.",
                "changed_files": ["ai_project_ctl/pipeline/report_gate.py"],
                "generated_files": ["AI_PROJECT/generated/PIPELINE_STATUS.md"],
                "checks": [
                    {
                        "name": "unit",
                        "command": "python -m unittest tests.test_pipeline_batch",
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
                    "prompt_tokens": 100,
                    "context_tokens": 20,
                    "remaining_tokens": 1000,
                    "token_count_strategy": "local_byte_estimate",
                    "token_count_estimated": True,
                    "token_count_unavailable": False,
                },
            },
        }
    )
    existing.write_text(json.dumps(state), encoding="utf-8")


def batch_workflow_runner(calls, *, root: Path):
    task_status = {"TASK-001": "ready", "TASK-002": "ready", "TASK-003": "ready"}

    def fake_run(argv):
        args = list(argv)
        calls.append(args)
        if len(args) > 1 and Path(args[1]).name == "taskctl.py" and "resolve" in args:
            task_id = args[args.index("resolve") + 1]
            index = int(task_id.split("-")[1])
            return completed(
                json.dumps(
                    {
                        "id": task_id,
                        "ref": "APP-{0:02d}".format(index),
                        "status": task_status[task_id],
                    }
                )
                + "\n"
            )
        if "codex" in args and "build" in args:
            task_id = args[args.index("--task") + 1] if "--task" in args else "TASK-001"
            prompt = root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"
            prompt.parent.mkdir(parents=True, exist_ok=True)
            prompt.write_text("Source ID: {}\n\nSmall prompt.".format(task_id), encoding="utf-8")
        if args == ["codex", "exec"]:
            ready = sorted(task_id for task_id, status in task_status.items() if status != "done")
            task_id = ready[0]
            write_report_state(root, task_id, "RPT-{}".format(task_id.split("-")[1]))
            return completed(stdout="codex adapter finished\n")
        if "task" in args and "transition" in args and "--to" in args:
            task_id = args[args.index("transition") + 1]
            status = args[args.index("--to") + 1]
            task_status[task_id] = status
            if status == "done":
                _write_task_status(root, task_id, status)
        return completed('{"ok": true}\n')

    return fake_run, task_status


def _write_task_status(root: Path, task_id: str, status: str) -> None:
    path = root / "AI_PROJECT" / "state" / "tasks.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    for task in state["tasks"]:
        if task.get("id") == task_id:
            task["status"] = status
    path.write_text(json.dumps(state), encoding="utf-8")


def batch_review_output(prompt: str) -> str:
    task_id = "TASK-002" if "TASK-002" in prompt else "TASK-001"
    report_id = "RPT-{}".format(task_id.split("-")[1])
    return json.dumps(
        {
            "verdict": "APPROVE",
            "summary": "Semantic review completed.",
            "evidence": {
                "task_id": task_id,
                "report_id": report_id,
                "report_gate_status": "pass",
                "machine_review_status": "pass",
            },
            "findings": [],
            "risks": [],
        }
    )


class PipelineBatchTests(unittest.TestCase):
    def test_run_until_blocker_requires_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_batch_project_state(root, task_count=1)
            session = create_session(root=root, actor="tester", policy_name="dry_run")

            result = run_until_blocker(session.data["session_id"], root=root, actor="tester")

            self.assertFalse(result.ok)
            self.assertEqual(result.errors[0].code, "PIPELINE_BATCH_CONFIRMATION_REQUIRED")
            self.assertFalse(pipeline_state_path(root).exists() is False)

    def test_run_until_blocker_completes_selected_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_batch_project_state(root, task_count=2, change_status="accepted")
            supervised = policy_preset("supervised_autoclose")
            policy = replace(
                supervised,
                name="batch_autoclose",
                batch=BatchPolicy(max_steps=5, max_failures=1),
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                ),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                max_tasks=2,
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
            latest = json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))["sessions"][0]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "QUEUE_COMPLETE")
            self.assertEqual(result.data["completed_tasks"], ["TASK-001", "TASK-002"])
            self.assertEqual(task_status["TASK-001"], "done")
            self.assertEqual(task_status["TASK-002"], "done")
            self.assertEqual(latest["status"], "completed")
            self.assertEqual(result.data["steps_run"], 3)
            self.assertEqual(result.data["accepted_changes"], ["CHG-001", "CHG-002"])

    def test_run_until_blocker_stops_on_first_blocker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_batch_project_state(root, task_count=1, change_status="approved")
            session = create_session(root=root, actor="tester", policy_name="supervised")
            calls = []
            fake_runner, _task_status = batch_workflow_runner(calls, root=root)

            result = run_until_blocker(
                session.data["session_id"],
                root=root,
                actor="tester",
                confirmed=True,
                runner=fake_runner,
            )

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertEqual(result.data["steps_run"], 1)
            self.assertEqual(len(result.data["blockers"]), 1)
            self.assertIn("policy stops before Codex execution", result.data["stop_reason"])

    def test_run_until_blocker_enforces_max_steps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_batch_project_state(root, task_count=2, change_status="approved")
            supervised = policy_preset("supervised_autoclose")
            policy = replace(
                supervised,
                name="batch_max_steps",
                batch=BatchPolicy(max_steps=1, max_failures=1),
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                ),
            )
            session = create_session(root=root, actor="tester", policy=policy, max_tasks=2)
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
            latest = json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))["sessions"][0]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "MAX_STEPS_REACHED")
            self.assertEqual(result.data["completed_tasks"], ["TASK-001"])
            self.assertEqual(result.data["accepted_changes"], [])
            self.assertEqual(task_status["TASK-001"], "done")
            self.assertEqual(task_status["TASK-002"], "ready")
            self.assertEqual(latest["status"], "stopped")


if __name__ == "__main__":
    unittest.main()

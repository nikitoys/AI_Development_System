import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ai_project_ctl.pipeline import (
    BatchPolicy,
    CodexAdapterMode,
    CodexExecutionMode,
    policy_preset,
)
from ai_project_ctl.pipeline.batch import run_until_blocker
from ai_project_ctl.pipeline.codex_adapter import (
    CODE_REPORT_MISSING as CODEX_ADAPTER_REPORT_MISSING,
)
from ai_project_ctl.pipeline.runner import run_next
from ai_project_ctl.pipeline.session import create_session
from ai_project_ctl.pipeline.state import pipeline_state_path


def completed(stdout="OK\n", returncode=0, stderr=""):
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def write_project_state(root: Path, *, change_status: str | None = "approved") -> None:
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
    (state_dir / "tasks.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "current_task_id": None,
                "tasks": [
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "uid": "uid_task_001",
                        "legacy_id": "TASK-001",
                        "aliases": ["TASK-001"],
                        "title": "Runnable task",
                        "status": "ready",
                        "epic_id": "EPIC-001",
                        "priority": 1,
                        "order": 1,
                        "local_seq": 1,
                        "depends_on": [],
                        "allowed_files": [
                            "ai_project_ctl/pipeline/report_gate.py",
                            "tests/**",
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    changes = []
    if change_status:
        changes.append(
            {
                "id": "CHG-001",
                "status": change_status,
                "linked_tasks": ["TASK-001"],
            }
        )
    (state_dir / "evolution.json").write_text(
        json.dumps({"schema_version": 1, "revision": 1, "changes": changes}),
        encoding="utf-8",
    )


def write_multi_task_project_state(
    root: Path,
    *,
    task_count: int = 5,
    task_status: str = "ready",
) -> None:
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
    for index in range(1, task_count + 1):
        task_id = "TASK-{0:03d}".format(index)
        tasks.append(
            {
                "id": task_id,
                "ref": "APP-{0:02d}".format(index),
                "uid": "uid_task_{0:03d}".format(index),
                "legacy_id": task_id,
                "aliases": [task_id],
                "title": "Runnable task {}".format(index),
                "summary": "Prepare task {}".format(index),
                "description": "Task {} needs a linked Change.".format(index),
                "scope": ["Implement task {}".format(index)],
                "out_of_scope": ["Do not approve Evolution Changes."],
                "acceptance_criteria": ["Created Change is linked."],
                "review_instructions": ["Check owner approval remains separate."],
                "status": task_status,
                "epic_id": "EPIC-001",
                "priority": 1,
                "order": index,
                "local_seq": index,
                "depends_on": [],
                "allowed_files": [
                    "ai_project_ctl/pipeline/runner.py",
                    "tests/test_pipeline_runner.py",
                ],
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
        json.dumps({"schema_version": 1, "revision": 1, "changes": []}),
        encoding="utf-8",
    )


def successful_workflow_runner(
    calls,
    *,
    root: Path | None = None,
    prompt_text: str = "Source ID: TASK-001\n\nSmall prompt.",
    report_on_local_codex: bool = False,
):
    def fake_run(argv):
        calls.append(list(argv))
        if list(argv) == ["codex", "exec"]:
            if root is not None and report_on_local_codex:
                write_report_state(root, "TASK-001", "RPT-001")
            return completed(stdout="codex adapter finished\n")
        if Path(argv[1]).name == "taskctl.py" and "resolve" in argv:
            return completed(
                json.dumps(
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "status": "ready",
                    }
                )
                + "\n"
            )
        if root is not None and "codex" in argv and "build" in argv:
            prompt = root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"
            prompt.parent.mkdir(parents=True, exist_ok=True)
            prompt.write_text(prompt_text, encoding="utf-8")
        return completed('{"ok": true}\n')

    return fake_run


def codex_stdout_for_report(report: dict) -> str:
    return "Codex finished.\nCODEX_REPORT_JSON:\n```json\n{}\n```\n".format(
        json.dumps(report, indent=2, sort_keys=True)
    )


def emitted_codex_report(
    task_id: str = "TASK-001",
    task_ref: str = "APP-01",
) -> dict:
    return {
        "schema_version": 1,
        "task_id": task_id,
        "task_ref": task_ref,
        "implementation_summary": "Implemented the selected task.",
        "changed_files": [],
        "generated_files": [],
        "checks": [
            {
                "name": "unit",
                "command": "python -m unittest tests.test_pipeline_runner",
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
            "completion_tokens": 10,
            "output_tokens": 5,
            "total_tokens": 135,
            "remaining_tokens": 1000,
            "model_context_limit": 2000,
            "max_context_tokens": 1500,
            "reserved_output_tokens": 200,
            "min_remaining_tokens": 100,
            "token_count_strategy": "test_fixture",
            "token_count_estimated": True,
            "token_count_unavailable": False,
            "token_count_unavailable_reason": "",
        },
    }


def structured_report_workflow_runner(
    calls,
    *,
    root: Path,
    codex_stdout: str,
    prompt_text: str = "Source ID: TASK-001\n\nSmall prompt.",
):
    def fake_run(argv):
        args = list(argv)
        calls.append(args)
        script = Path(args[1]).name if len(args) > 1 else ""
        if script == "taskctl.py" and "resolve" in args:
            return completed(
                json.dumps(
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "status": "ready",
                    }
                )
                + "\n"
            )
        if "codex" in args and "build" in args:
            prompt = root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"
            prompt.parent.mkdir(parents=True, exist_ok=True)
            prompt.write_text(prompt_text, encoding="utf-8")
        if args == ["codex", "exec"]:
            return completed(stdout=codex_stdout)
        return completed('{"ok": true}\n')

    return fake_run


def auto_create_change_runner(calls, *, root: Path, allow_approval: bool = False):
    def fake_run(argv):
        args = list(argv)
        calls.append(args)
        script = Path(args[1]).name if len(args) > 1 else ""
        if script == "taskctl.py" and "resolve" in args:
            task_ref = args[args.index("resolve") + 1]
            task = _task_by_ref(root, task_ref)
            return completed(
                json.dumps(
                    {
                        "id": task["id"],
                        "ref": task.get("ref") or task["id"],
                        "status": task["status"],
                    }
                )
                + "\n"
            )
        if script == "taskctl.py":
            return completed("OK\n")
        if script == "evolutionctl.py":
            change_command = (
                args[args.index("change") + 1]
                if "change" in args and args.index("change") + 1 < len(args)
                else ""
            )
            if change_command in {"approve", "accept"}:
                if change_command == "accept" or not allow_approval:
                    raise AssertionError("pipeline must not approve or accept changes")
                change_id = args[args.index("approve") + 1]
                _update_change(root, change_id, status="approved")
                return completed("OK: change.approve revision 1 -> 2\n")
            if args[-1] == "validate":
                return completed("OK: evolution is valid\n")
            if args[-1] == "check-generated":
                return completed("OK: generated evolution file is up to date\n")
            if "create" in args:
                change_id = _append_change(root)
                return completed(
                    "OK: change.create revision 1 -> 2\nCreated: {}\n".format(change_id)
                )
            if "link-task" in args:
                change_id = args[args.index("link-task") + 1]
                task_id = args[args.index("--task") + 1]
                _update_change(root, change_id, linked_task=task_id)
                return completed("OK\n")
            if "transition" in args and "--to" in args:
                change_id = args[args.index("transition") + 1]
                _update_change(root, change_id, status=args[args.index("--to") + 1])
                return completed("OK\n")
            if any(command in args for command in ("add-affected-file", "add-risk", "add-impact")):
                return completed("OK\n")
        if script == "aictl.py":
            return completed('{"ok": true}\n')
        raise AssertionError("unexpected command: {}".format(args))

    return fake_run


def _task_by_ref(root: Path, task_ref: str) -> dict:
    state = json.loads((root / "AI_PROJECT" / "state" / "tasks.json").read_text(encoding="utf-8"))
    for task in state["tasks"]:
        refs = {task.get("id"), task.get("ref"), task.get("uid"), task.get("legacy_id")}
        refs.update(task.get("aliases") or [])
        if task_ref in refs:
            return task
    raise AssertionError("missing task ref: {}".format(task_ref))


def _append_change(root: Path) -> str:
    path = root / "AI_PROJECT" / "state" / "evolution.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    change_id = "CHG-{0:03d}".format(len(state.get("changes", [])) + 1)
    state.setdefault("changes", []).append(
        {
            "id": change_id,
            "status": "draft",
            "title": "Generated Change {}".format(change_id),
            "linked_tasks": [],
        }
    )
    state["revision"] = int(state.get("revision", 0)) + 1
    path.write_text(json.dumps(state), encoding="utf-8")
    return change_id


def _update_change(root: Path, change_id: str, *, linked_task: str = "", status: str = "") -> None:
    path = root / "AI_PROJECT" / "state" / "evolution.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    for change in state.get("changes", []):
        if change.get("id") != change_id:
            continue
        if linked_task and linked_task not in change.setdefault("linked_tasks", []):
            change["linked_tasks"].append(linked_task)
        if status:
            change["status"] = status
    state["revision"] = int(state.get("revision", 0)) + 1
    path.write_text(json.dumps(state), encoding="utf-8")


def stateful_workflow_runner(
    calls,
    *,
    root: Path,
    prompt_text: str = "Source ID: TASK-001\n\nSmall prompt.",
):
    task_status = {"value": "ready"}

    def fake_run(argv):
        args = list(argv)
        calls.append(args)
        if args == ["codex", "exec"]:
            write_report_state(root, "TASK-001", "RPT-001")
            return completed(stdout="codex adapter finished\n")
        if len(args) > 1 and Path(args[1]).name == "taskctl.py" and "resolve" in args:
            return completed(
                json.dumps(
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "status": task_status["value"],
                    }
                )
                + "\n"
            )
        if "codex" in args and "build" in args:
            prompt = root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"
            prompt.parent.mkdir(parents=True, exist_ok=True)
            prompt.write_text(prompt_text, encoding="utf-8")
        if "task" in args and "transition" in args and "TASK-001" in args and "--to" in args:
            task_status["value"] = args[args.index("--to") + 1]
        return completed('{"ok": true}\n')

    return fake_run, task_status


def committing_workflow_runner(
    calls,
    *,
    root: Path,
    prompt_text: str = "Source ID: TASK-001\n\nSmall prompt.",
    git_status_stdout: str = " M ai_project_ctl/pipeline/report_gate.py\n",
):
    task_status = {"value": "ready"}

    def fake_run(argv):
        args = list(argv)
        if args and args[0] == "git":
            calls.append(args)
            if args == ["git", "status", "--short", "--untracked-files=all"]:
                return completed(stdout=git_status_stdout)
            if args[:3] == ["git", "add", "--"]:
                return completed(stdout="")
            if args[:3] == ["git", "commit", "-m"]:
                return completed(stdout="[main abc1234] pipeline commit\n")
            if args == ["git", "rev-parse", "--verify", "HEAD"]:
                return completed(stdout="abc1234deadbeef\n")
            return completed(returncode=1, stderr="unexpected git command\n")

        calls.append(args)
        if args == ["codex", "exec"]:
            write_report_state(root, "TASK-001", "RPT-001")
            return completed(stdout="codex adapter finished\n")
        if len(args) > 1 and Path(args[1]).name == "taskctl.py" and "resolve" in args:
            return completed(
                json.dumps(
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "status": task_status["value"],
                    }
                )
                + "\n"
            )
        if "codex" in args and "build" in args:
            prompt = root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"
            prompt.parent.mkdir(parents=True, exist_ok=True)
            prompt.write_text(prompt_text, encoding="utf-8")
        if "task" in args and "transition" in args and "TASK-001" in args and "--to" in args:
            task_status["value"] = args[args.index("--to") + 1]
            _write_task_status(root, task_status["value"])
        return completed('{"ok": true}\n')

    return fake_run


def _write_task_status(root: Path, status: str) -> None:
    path = root / "AI_PROJECT" / "state" / "tasks.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    for task in state["tasks"]:
        if task.get("id") == "TASK-001":
            task["status"] = status
    path.write_text(json.dumps(state), encoding="utf-8")


def valid_report(task_id: str) -> dict:
    return {
        "schema_version": 1,
        "task_id": task_id,
        "task_ref": "APP-01",
        "reported_task_id": task_id,
        "reported_task_ref": "APP-01",
        "implementation_summary": "Implemented the selected task.",
        "changed_files": ["ai_project_ctl/pipeline/report_gate.py"],
        "generated_files": ["AI_PROJECT/generated/PIPELINE_STATUS.md"],
        "checks": [
            {
                "name": "unit",
                "command": "python -m unittest tests.test_pipeline_runner",
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
    }


def valid_review_output(verdict="APPROVE", findings=None) -> str:
    return json.dumps(
        {
            "verdict": verdict,
            "summary": "Semantic review completed.",
            "evidence": {
                "task_id": "TASK-001",
                "report_id": "RPT-001",
                "report_gate_status": "pass",
                "machine_review_status": "pass",
            },
            "findings": list(findings or []),
            "risks": [],
        }
    )


def write_report_state(root: Path, task_id: str, report_id: str, report: dict | None = None) -> None:
    report_data = report or valid_report(task_id)
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "task_reports.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "created_at": "2026-06-19T00:00:00Z",
                "updated_at": "2026-06-19T00:00:00Z",
                "latest_by_task": {task_id: report_id},
                "reports": [
                    {
                        "id": report_id,
                        "task_id": task_id,
                        "task_ref": "APP-01",
                        "submitted_at": "2026-06-19T00:00:00Z",
                        "submitted_by": "tester",
                        "source_file": "/tmp/report.json",
                        "report": report_data,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def load_pipeline(root: Path):
    return json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))


class PipelineRunnerTests(unittest.TestCase):
    def test_dry_run_records_selected_task_and_stops_without_prepare(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root)
            session = create_session(
                root=root,
                actor="tester",
                policy_name="dry_run",
                task_refs=("APP-01",),
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=successful_workflow_runner(calls),
            )
            state = load_pipeline(root)
            latest = state["sessions"][0]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertEqual(result.data["selected_task"]["id"], "TASK-001")
            self.assertEqual(calls, [])
            self.assertEqual(latest["steps"][0]["status"], "stopped")
            self.assertEqual(latest["steps"][0]["gate_outcomes"][0]["name"], "codex_execution_policy")

    def test_supervised_blocks_when_approved_change_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status=None)
            session = create_session(root=root, actor="tester", policy_name="supervised")
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=successful_workflow_runner(calls),
            )
            state = load_pipeline(root)

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertIn("Approved linked Evolution Change", result.data["stop_reason"])
            self.assertEqual(calls, [])
            self.assertEqual(state["sessions"][0]["status"], "blocked")
            self.assertEqual(state["sessions"][0]["steps"][0]["gate_outcomes"][0]["name"], "evolution_change_gate")

    def test_auto_create_missing_change_creates_linked_change_and_blocks_for_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status=None)
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="auto_create_missing_change",
                evolution=replace(supervised.evolution, create_missing_change=True),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                task_refs=("APP-01",),
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=auto_create_change_runner(calls, root=root),
            )
            state = load_pipeline(root)
            latest = state["sessions"][0]
            changes = json.loads(
                (root / "AI_PROJECT" / "state" / "evolution.json").read_text(
                    encoding="utf-8"
                )
            )["changes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertIn("Human Owner approval", result.data["stop_reason"])
            self.assertEqual(changes[0]["id"], "CHG-001")
            self.assertEqual(changes[0]["status"], "ready")
            self.assertEqual(changes[0]["linked_tasks"], ["TASK-001"])
            self.assertEqual(latest["linked_change_ids"], ["CHG-001"])
            change_gate = latest["steps"][0]["gate_outcomes"][0]["details"]["change_gate"]
            self.assertEqual(change_gate["created_change_ids"], ["CHG-001"])
            self.assertEqual(change_gate["tasks_requiring_approval"], ["TASK-001"])
            command_texts = [" ".join(call) for call in calls]
            self.assertFalse(any(" change approve " in text for text in command_texts))
            self.assertFalse(any(" change accept " in text for text in command_texts))

    def test_auto_create_missing_changes_preflights_multiple_selected_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_multi_task_project_state(root, task_count=5)
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="auto_create_missing_changes",
                evolution=replace(supervised.evolution, create_missing_change=True),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                task_refs=("APP-01", "APP-02", "APP-03", "APP-04", "APP-05"),
                max_tasks=5,
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=auto_create_change_runner(calls, root=root),
            )
            state = load_pipeline(root)
            latest = state["sessions"][0]
            changes = json.loads(
                (root / "AI_PROJECT" / "state" / "evolution.json").read_text(
                    encoding="utf-8"
                )
            )["changes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertEqual(
                [change["id"] for change in changes],
                ["CHG-001", "CHG-002", "CHG-003", "CHG-004", "CHG-005"],
            )
            self.assertEqual(
                [change["linked_tasks"] for change in changes],
                [["TASK-001"], ["TASK-002"], ["TASK-003"], ["TASK-004"], ["TASK-005"]],
            )
            self.assertEqual(
                latest["linked_change_ids"],
                ["CHG-001", "CHG-002", "CHG-003", "CHG-004", "CHG-005"],
            )
            change_gate = latest["steps"][0]["gate_outcomes"][0]["details"]["change_gate"]
            self.assertEqual(
                change_gate["created_change_ids"],
                ["CHG-001", "CHG-002", "CHG-003", "CHG-004", "CHG-005"],
            )
            self.assertEqual(
                change_gate["tasks_requiring_approval"],
                ["TASK-001", "TASK-002", "TASK-003", "TASK-004", "TASK-005"],
            )
            self.assertFalse(any("codexctl.py" in " ".join(call) for call in calls))

    def test_auto_create_missing_changes_preflights_blocked_selected_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_multi_task_project_state(root, task_count=2, task_status="planned")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="auto_create_blocked_selected_changes",
                evolution=replace(supervised.evolution, create_missing_change=True),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                task_refs=("APP-01", "APP-02"),
                max_tasks=2,
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=auto_create_change_runner(calls, root=root),
            )
            state = load_pipeline(root)
            latest = state["sessions"][0]
            changes = json.loads(
                (root / "AI_PROJECT" / "state" / "evolution.json").read_text(
                    encoding="utf-8"
                )
            )["changes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertEqual([change["id"] for change in changes], ["CHG-001", "CHG-002"])
            self.assertEqual(latest["linked_change_ids"], ["CHG-001", "CHG-002"])
            change_gate = latest["steps"][0]["gate_outcomes"][0]["details"]["change_gate"]
            self.assertEqual(change_gate["created_change_ids"], ["CHG-001", "CHG-002"])

    def test_owner_approval_policy_approves_selected_queue_changes_and_continues(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_multi_task_project_state(root, task_count=5)
            evolution_path = root / "AI_PROJECT" / "state" / "evolution.json"
            evolution = json.loads(evolution_path.read_text(encoding="utf-8"))
            evolution["changes"] = [
                {
                    "id": "CHG-001",
                    "status": "proposed",
                    "title": "Existing proposed",
                    "linked_tasks": ["TASK-003"],
                },
                {
                    "id": "CHG-002",
                    "status": "ready",
                    "title": "Existing ready",
                    "linked_tasks": ["TASK-004"],
                },
                {
                    "id": "CHG-999",
                    "status": "ready",
                    "title": "Unrelated ready",
                    "linked_tasks": ["TASK-999"],
                },
            ]
            evolution_path.write_text(json.dumps(evolution), encoding="utf-8")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="owner_approved_session_changes",
                evolution=replace(
                    supervised.evolution,
                    create_missing_change=True,
                    owner_approve_required_changes_for_session=True,
                    owner_approval_note="Owner approved this selected queue.",
                ),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                task_refs=("APP-01", "APP-02", "APP-03", "APP-04", "APP-05"),
                max_tasks=5,
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=auto_create_change_runner(calls, root=root, allow_approval=True),
            )
            state = load_pipeline(root)
            latest = state["sessions"][0]
            changes = {
                change["id"]: change
                for change in json.loads(evolution_path.read_text(encoding="utf-8"))[
                    "changes"
                ]
            }
            gate_details = latest["steps"][0]["gate_outcomes"][0]["details"]
            change_gate = gate_details["change_gate"]
            command_texts = [" ".join(call) for call in calls]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertIn("policy stops before Codex execution", result.data["stop_reason"])
            self.assertEqual(changes["CHG-001"]["status"], "approved")
            self.assertEqual(changes["CHG-002"]["status"], "approved")
            self.assertEqual(changes["CHG-999"]["status"], "ready")
            self.assertEqual(changes["CHG-004"]["status"], "approved")
            self.assertEqual(changes["CHG-005"]["status"], "approved")
            self.assertEqual(changes["CHG-006"]["status"], "approved")
            self.assertEqual(
                change_gate["approved_change_ids"],
                ["CHG-004", "CHG-005", "CHG-001", "CHG-002", "CHG-006"],
            )
            self.assertEqual(
                change_gate["approved_task_refs"],
                ["APP-01", "APP-02", "APP-03", "APP-04", "APP-05"],
            )
            self.assertEqual(
                change_gate["owner_approval"]["approval_note"],
                "Owner approved this selected queue.",
            )
            self.assertEqual(change_gate["owner_approval"]["session_id"], "PSESS-001")
            self.assertTrue(any(" change approve CHG-001 " in text for text in command_texts))
            self.assertTrue(any(" change approve CHG-002 " in text for text in command_texts))
            self.assertFalse(any(" change approve CHG-999 " in text for text in command_texts))
            self.assertTrue(any(" current set TASK-001" in text for text in command_texts))

    def test_supervised_builds_prompt_and_stops_before_codex_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            session = create_session(root=root, actor="tester", policy_name="supervised")
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=successful_workflow_runner(calls),
            )
            step = load_pipeline(root)["sessions"][0]["steps"][0]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertIn("policy stops before Codex execution", result.data["stop_reason"])
            self.assertTrue(calls)
            self.assertTrue(any("context" in call for call in calls))
            self.assertEqual(step["status"], "passed")
            self.assertEqual(step["gate_outcomes"][0]["status"], "skipped")

    def test_run_until_blocker_collects_auto_submitted_stdout_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="phase_auto_collect_report_test",
                batch=BatchPolicy(max_steps=4, max_failures=1),
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                    require_report=True,
                ),
            )
            session = create_session(root=root, actor="tester", policy=policy)
            calls = []

            result = run_until_blocker(
                session.data["session_id"],
                root=root,
                actor="tester",
                confirmed=True,
                runner=structured_report_workflow_runner(
                    calls,
                    root=root,
                    codex_stdout=codex_stdout_for_report(emitted_codex_report()),
                ),
            )
            latest = load_pipeline(root)["sessions"][0]
            phases = {entry["phase"]: entry for entry in latest["phase_history"]}
            execute = phases["execute"]
            collect_report = phases["collect_report"]
            report_state = json.loads(
                (root / "AI_PROJECT" / "state" / "task_reports.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "MAX_STEPS_REACHED")
            self.assertEqual(
                [entry["phase"] for entry in latest["phase_history"]],
                ["queue_preview", "prepare", "execute", "collect_report"],
            )
            self.assertEqual(execute["status"], "passed")
            self.assertEqual(
                execute["artifacts"]["adapter"]["code"],
                "CODEX_ADAPTER_LOCAL_COMMAND_PASSED",
            )
            self.assertEqual(execute["artifacts"]["report_id"], "RPT-001")
            self.assertEqual(execute["artifacts"]["after_report_id"], "RPT-001")
            self.assertEqual(
                execute["artifacts"]["adapter_summary"]["report_ids"],
                ["RPT-001"],
            )
            self.assertEqual(collect_report["status"], "passed")
            self.assertEqual(collect_report["artifacts"]["report_id"], "RPT-001")
            self.assertTrue(collect_report["artifacts"]["report_found"])
            self.assertEqual(collect_report["artifacts"]["freshness_basis"], "report_id")
            self.assertEqual(report_state["latest_by_task"], {"TASK-001": "RPT-001"})
            self.assertEqual(
                report_state["reports"][0]["report"]["reported_task_id"],
                "TASK-001",
            )
            self.assertTrue(
                report_state["reports"][0]["source_file"].startswith(
                    "captured:stdout:sha256:"
                )
            )
            self.assertIn(["codex", "exec"], calls)

    def test_run_until_blocker_no_report_stdout_keeps_adapter_missing_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="phase_auto_collect_missing_report_test",
                batch=BatchPolicy(max_steps=4, max_failures=1),
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                    require_report=True,
                ),
            )
            session = create_session(root=root, actor="tester", policy=policy)
            calls = []

            result = run_until_blocker(
                session.data["session_id"],
                root=root,
                actor="tester",
                confirmed=True,
                runner=structured_report_workflow_runner(
                    calls,
                    root=root,
                    codex_stdout="Codex finished without structured report.\n",
                ),
            )
            latest = load_pipeline(root)["sessions"][0]
            phases = {entry["phase"]: entry for entry in latest["phase_history"]}
            execute = phases["execute"]
            collect_report = phases["collect_report"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "REPORT_MISSING")
            self.assertEqual(execute["status"], "passed")
            self.assertEqual(
                execute["artifacts"]["adapter"]["code"],
                CODEX_ADAPTER_REPORT_MISSING,
            )
            self.assertEqual(execute["artifacts"]["adapter"]["report_id"], "")
            self.assertEqual(collect_report["status"], "blocked")
            self.assertEqual(collect_report["artifacts"]["blocked_by"], "REPORT_MISSING")
            self.assertFalse(
                (root / "AI_PROJECT" / "state" / "task_reports.json").exists()
            )
            self.assertIn(["codex", "exec"], calls)

    def test_run_codex_records_token_gate_pass_before_manual_adapter_blocker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="run_codex_test",
                codex=replace(supervised.codex, mode=CodexExecutionMode.RUN_CODEX),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=successful_workflow_runner(calls, root=root),
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertEqual(gates[0]["name"], "token_budget_gate")
            self.assertEqual(gates[0]["status"], "pass")
            self.assertEqual(gates[0]["details"]["token_budget"]["code"], "TOKEN_BUDGET_PASS")
            self.assertEqual(gates[1]["name"], "codex_execution_adapter")
            self.assertEqual(gates[1]["status"], "blocked")
            self.assertTrue(gates[1]["details"]["codex_adapter_called"])
            self.assertEqual(
                gates[1]["details"]["adapter"]["code"],
                "CODEX_ADAPTER_MANUAL_HANDOFF_REQUIRED",
            )

    def test_run_codex_local_adapter_records_codex_review_pass_then_policy_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="run_codex_local_adapter_test",
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
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=successful_workflow_runner(
                    calls,
                    root=root,
                    report_on_local_codex=True,
                ),
                codex_reviewer=lambda prompt: valid_review_output(),
            )
            latest = load_pipeline(root)["sessions"][0]
            gates = latest["steps"][0]["gate_outcomes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertIn("policy stops before auto-close", result.data["stop_reason"])
            self.assertEqual(gates[1]["name"], "codex_execution_adapter")
            self.assertEqual(gates[1]["status"], "pass")
            self.assertEqual(gates[1]["details"]["adapter"]["report_id"], "RPT-001")
            self.assertEqual(gates[2]["name"], "codex_report_gate")
            self.assertEqual(gates[2]["status"], "pass")
            self.assertEqual(gates[2]["details"]["report_gate"]["report_id"], "RPT-001")
            self.assertEqual(gates[3]["name"], "machine_review_gate")
            self.assertEqual(gates[3]["status"], "pass")
            self.assertEqual(gates[4]["name"], "codex_review_gate")
            self.assertEqual(gates[4]["status"], "pass")
            self.assertEqual(gates[4]["details"]["codex_review"]["verdict"], "APPROVE")
            self.assertEqual(gates[5]["name"], "pipeline_policy")
            self.assertEqual(gates[5]["status"], "skipped")
            self.assertEqual(latest["report_ids"], ["RPT-001"])
            self.assertEqual(len(latest["review_ids"]), 1)
            self.assertIn(["codex", "exec"], calls)

    def test_run_codex_blocks_when_codex_review_output_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="run_codex_missing_review_test",
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
                auto_close_note="Owner approved auto-close for this test session.",
            )

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=successful_workflow_runner(
                    [],
                    root=root,
                    report_on_local_codex=True,
                ),
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "CODEX_REVIEW_GATE_FAILURE")
            self.assertEqual(gates[4]["name"], "codex_review_gate")
            self.assertEqual(gates[4]["status"], "fail")
            self.assertEqual(
                gates[4]["details"]["codex_review"]["code"],
                "CODEX_REVIEW_OUTPUT_MISSING",
            )

    def test_run_codex_request_changes_blocks_before_policy_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="run_codex_request_changes_review_test",
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
                auto_close_note="Owner approved auto-close for this test session.",
            )

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=successful_workflow_runner(
                    [],
                    root=root,
                    report_on_local_codex=True,
                ),
                codex_reviewer=lambda prompt: valid_review_output(
                    "REQUEST_CHANGES",
                    findings=(
                        {
                            "severity": "Major",
                            "message": "Acceptance evidence is incomplete.",
                            "file": "ai_project_ctl/pipeline/codex_review.py",
                        },
                    ),
                ),
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "CODEX_REVIEW_REQUEST_CHANGES")
            self.assertEqual(gates[4]["name"], "codex_review_gate")
            self.assertEqual(gates[4]["status"], "blocked")
            self.assertEqual(len(gates), 5)

    def test_autoclose_policy_closes_after_machine_pass_and_codex_approve(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised_autoclose")
            policy = replace(
                supervised,
                name="run_codex_autoclose_close_test",
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
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []
            fake_runner, task_status = stateful_workflow_runner(calls, root=root)

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=fake_runner,
                codex_reviewer=lambda prompt: valid_review_output(),
            )
            latest = load_pipeline(root)["sessions"][0]
            gates = latest["steps"][0]["gate_outcomes"]
            commands = [" ".join(call) for call in calls]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "TASK_AUTO_CLOSED")
            self.assertEqual(task_status["value"], "done")
            self.assertEqual(gates[5]["name"], "review_close_gate")
            self.assertEqual(gates[5]["status"], "pass")
            self.assertEqual(gates[5]["details"]["close_policy"]["action"], "close_task")
            self.assertTrue(any("task transition TASK-001 --to in_review" in command for command in commands))
            self.assertTrue(any("task approve TASK-001 --notes Owner auto-close note=Owner approved auto-close for this test session." in command for command in commands))
            self.assertTrue(any("Pipeline policy=run_codex_autoclose_close_test" in command for command in commands))
            self.assertTrue(any("machine_gate=pass/MACHINE_REVIEW_PASS" in command for command in commands))
            self.assertTrue(any("codex_review=APPROVE/CODEX_REVIEW_APPROVE" in command for command in commands))
            self.assertTrue(any("report_id=RPT-001" in command for command in commands))
            self.assertTrue(any("task transition TASK-001 --to done" in command for command in commands))

    def test_autoclose_policy_requests_changes_when_review_requests_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised_autoclose")
            policy = replace(
                supervised,
                name="run_codex_autoclose_rework_test",
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
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []
            fake_runner, task_status = stateful_workflow_runner(calls, root=root)

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=fake_runner,
                codex_reviewer=lambda prompt: valid_review_output(
                    "REQUEST_CHANGES",
                    findings=(
                        {
                            "severity": "Major",
                            "message": "Acceptance evidence is incomplete.",
                            "file": "ai_project_ctl/pipeline/close_policy.py",
                        },
                    ),
                ),
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]
            commands = [" ".join(call) for call in calls]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "CODEX_REVIEW_REQUEST_CHANGES")
            self.assertEqual(task_status["value"], "changes_requested")
            self.assertEqual(gates[4]["name"], "codex_review_gate")
            self.assertEqual(gates[4]["status"], "blocked")
            self.assertEqual(gates[5]["name"], "review_close_gate")
            self.assertEqual(gates[5]["status"], "blocked")
            self.assertEqual(gates[5]["details"]["close_policy"]["action"], "request_changes")
            self.assertTrue(any("task transition TASK-001 --to in_review" in command for command in commands))
            self.assertTrue(any("task add-note TASK-001 --text Owner auto-close note=Owner approved auto-close for this test session." in command for command in commands))
            self.assertTrue(any("Pipeline policy=run_codex_autoclose_rework_test" in command for command in commands))
            self.assertTrue(any("task transition TASK-001 --to changes_requested" in command for command in commands))

    def test_autoclose_policy_stops_when_codex_review_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised_autoclose")
            policy = replace(
                supervised,
                name="run_codex_autoclose_blocked_review_test",
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
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []
            fake_runner, _task_status = stateful_workflow_runner(calls, root=root)

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=fake_runner,
                codex_reviewer=lambda prompt: valid_review_output(
                    "BLOCKED",
                    findings=(
                        {
                            "severity": "Major",
                            "message": "Semantic review could not be completed.",
                            "file": "ai_project_ctl/pipeline/close_policy.py",
                        },
                    ),
                ),
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]
            commands = [" ".join(call) for call in calls]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "CODEX_REVIEW_BLOCKED")
            self.assertEqual(gates[4]["name"], "codex_review_gate")
            self.assertEqual(gates[4]["status"], "blocked")
            self.assertEqual(len(gates), 5)
            self.assertFalse(any("task approve TASK-001" in command for command in commands))
            self.assertFalse(any("task transition TASK-001 --to changes_requested" in command for command in commands))

    def test_autoclose_policy_does_not_close_after_machine_review_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised_autoclose")
            policy = replace(
                supervised,
                name="run_codex_autoclose_machine_fail_test",
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
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []
            base_runner, _task_status = stateful_workflow_runner(calls, root=root)

            def fake_runner(argv):
                if tuple(argv)[-2:] == ("project", "protected-check"):
                    calls.append(list(argv))
                    return completed(returncode=1, stderr="protected drift\n")
                return base_runner(argv)

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=fake_runner,
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]
            commands = [" ".join(call) for call in calls]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "MACHINE_REVIEW_FAILURE")
            self.assertEqual(gates[3]["name"], "machine_review_gate")
            self.assertEqual(gates[3]["status"], "fail")
            self.assertFalse(any("task approve TASK-001" in command for command in commands))
            self.assertFalse(any("review_close_gate" == gate["name"] for gate in gates))

    def test_autoclose_policy_stops_when_rework_limit_is_reached(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised_autoclose")
            policy = replace(
                supervised,
                name="run_codex_autoclose_rework_limit_test",
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                ),
                rework=replace(supervised.rework, max_rework_attempts=1),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            state_path = pipeline_state_path(root)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["sessions"][0]["attempt_counters"]["rework"] = 1
            state_path.write_text(json.dumps(state), encoding="utf-8")
            calls = []
            fake_runner, task_status = stateful_workflow_runner(calls, root=root)

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=fake_runner,
                codex_reviewer=lambda prompt: valid_review_output(
                    "REQUEST_CHANGES",
                    findings=(
                        {
                            "severity": "Major",
                            "message": "Acceptance evidence is incomplete.",
                            "file": "ai_project_ctl/pipeline/close_policy.py",
                        },
                    ),
                ),
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]
            commands = [" ".join(call) for call in calls]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "REWORK_LIMIT_REACHED")
            self.assertEqual(task_status["value"], "in_progress")
            self.assertEqual(gates[5]["name"], "review_close_gate")
            self.assertEqual(gates[5]["status"], "blocked")
            self.assertEqual(gates[5]["details"]["close_policy"]["action"], "stop")
            self.assertFalse(any("task transition TASK-001 --to changes_requested" in command for command in commands))

    def test_run_codex_blocks_downstream_when_machine_review_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="run_codex_machine_review_failure_test",
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
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []
            base_runner = successful_workflow_runner(
                calls,
                root=root,
                report_on_local_codex=True,
            )

            def fake_runner(argv):
                if tuple(argv)[-2:] == ("project", "protected-check"):
                    return completed(returncode=1, stderr="protected drift\n")
                return base_runner(argv)

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=fake_runner,
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "MACHINE_REVIEW_FAILURE")
            self.assertEqual(gates[3]["name"], "machine_review_gate")
            self.assertEqual(gates[3]["status"], "fail")
            self.assertNotIn("codex_review_gate", [gate["name"] for gate in gates])

    def test_run_codex_blocks_downstream_when_report_gate_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="run_codex_report_gate_failure_test",
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
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []
            report = valid_report("TASK-001")
            report["blockers"] = ["Manual blocker."]
            base_runner = successful_workflow_runner(calls, root=root)

            def fake_runner(argv):
                if list(argv) == ["codex", "exec"]:
                    calls.append(list(argv))
                    write_report_state(root, "TASK-001", "RPT-001", report=report)
                    return completed(stdout="report submitted\n")
                return base_runner(argv)

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=fake_runner,
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "CODEX_REPORT_GATE_FAILURE")
            self.assertEqual(gates[2]["name"], "codex_report_gate")
            self.assertEqual(gates[2]["status"], "fail")
            self.assertNotIn("codex_review_gate", [gate["name"] for gate in gates])
            self.assertIn(["codex", "exec"], calls)

    def test_run_codex_stops_on_token_budget_failure_before_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="run_codex_low_budget_test",
                codex=replace(supervised.codex, mode=CodexExecutionMode.RUN_CODEX),
                token_budget=replace(
                    supervised.token_budget,
                    max_prompt_tokens=30,
                    max_context_tokens=30,
                    min_remaining_tokens=20,
                ),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=successful_workflow_runner(calls, root=root, prompt_text="x" * 80),
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "TOKEN_BUDGET_FAILURE")
            self.assertEqual(gates[0]["name"], "token_budget_gate")
            self.assertEqual(gates[0]["status"], "fail")
            self.assertEqual(
                gates[0]["details"]["token_budget"]["code"],
                "TOKEN_BUDGET_LOW_REMAINING",
            )
            self.assertEqual(len(gates), 1)

    def test_autoclose_policy_stops_when_build_prompt_only_cannot_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            session = create_session(
                root=root,
                actor="tester",
                policy_name="supervised_autoclose",
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=successful_workflow_runner(calls),
            )
            gate = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"][0]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "NOT_IMPLEMENTED")
            self.assertEqual(gate["name"], "review_close_gate")
            self.assertIn("requires Codex execution", result.data["stop_reason"])

    def test_local_commit_policy_commits_after_close_and_green_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="accepted")
            supervised = policy_preset("supervised_local_commit")
            policy = replace(
                supervised,
                name="run_codex_local_commit_test",
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
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=committing_workflow_runner(calls, root=root),
                codex_reviewer=lambda prompt: valid_review_output(),
            )
            latest = load_pipeline(root)["sessions"][0]
            gates = latest["steps"][0]["gate_outcomes"]
            git_calls = [call for call in calls if call and call[0] == "git"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "LOCAL_COMMIT_CREATED")
            self.assertEqual(gates[5]["name"], "review_close_gate")
            self.assertEqual(gates[5]["status"], "pass")
            self.assertEqual(gates[6]["name"], "commit_gate")
            self.assertEqual(gates[6]["status"], "pass")
            self.assertEqual(latest["commit_ids"], ["abc1234deadbeef"])
            self.assertEqual(git_calls[0], ["git", "status", "--short", "--untracked-files=all"])
            self.assertEqual(git_calls[1], ["git", "add", "--", "ai_project_ctl/pipeline/report_gate.py"])
            self.assertEqual(git_calls[2][:3], ["git", "commit", "-m"])
            self.assertEqual(git_calls[3], ["git", "rev-parse", "--verify", "HEAD"])
            self.assertFalse(any("push" in call for call in git_calls))
            self.assertFalse(any("reset" in call for call in git_calls))

    def test_local_commit_blocks_until_linked_change_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised_local_commit")
            policy = replace(
                supervised,
                name="run_codex_local_commit_change_gate_test",
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
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=committing_workflow_runner(calls, root=root),
                codex_reviewer=lambda prompt: valid_review_output(),
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]
            git_calls = [call for call in calls if call and call[0] == "git"]
            commit = gates[6]["details"]["commit"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "COMMIT_READINESS_FAILED")
            self.assertEqual(gates[6]["name"], "commit_gate")
            self.assertEqual(gates[6]["status"], "blocked")
            self.assertEqual(commit["readiness"]["code"], "COMMIT_CHANGE_NOT_ACCEPTED")
            self.assertEqual(git_calls, [])

    def test_local_commit_refuses_unapproved_dirty_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="accepted")
            supervised = policy_preset("supervised_local_commit")
            policy = replace(
                supervised,
                name="run_codex_local_commit_unrelated_files_test",
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
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=committing_workflow_runner(
                    calls,
                    root=root,
                    git_status_stdout=(
                        " M ai_project_ctl/pipeline/report_gate.py\n"
                        " M README.md\n"
                    ),
                ),
                codex_reviewer=lambda prompt: valid_review_output(),
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]
            git_calls = [call for call in calls if call and call[0] == "git"]
            commit = gates[6]["details"]["commit"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "COMMIT_READINESS_FAILED")
            self.assertEqual(commit["readiness"]["code"], "COMMIT_UNRELATED_FILES")
            self.assertIn("README.md", commit["readiness"]["blockers"])
            self.assertEqual(git_calls, [["git", "status", "--short", "--untracked-files=all"]])


if __name__ == "__main__":
    unittest.main()

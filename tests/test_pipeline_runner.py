import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ai_project_ctl.pipeline import CodexAdapterMode, CodexExecutionMode, policy_preset
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
            session = create_session(root=root, actor="tester", policy=policy)
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

    def test_run_codex_local_adapter_records_report_gate_pass_then_stops_at_review_gate(self):
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
            session = create_session(root=root, actor="tester", policy=policy)
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
            )
            latest = load_pipeline(root)["sessions"][0]
            gates = latest["steps"][0]["gate_outcomes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "NOT_IMPLEMENTED")
            self.assertEqual(gates[1]["name"], "codex_execution_adapter")
            self.assertEqual(gates[1]["status"], "pass")
            self.assertEqual(gates[1]["details"]["adapter"]["report_id"], "RPT-001")
            self.assertEqual(gates[2]["name"], "codex_report_gate")
            self.assertEqual(gates[2]["status"], "pass")
            self.assertEqual(gates[2]["details"]["report_gate"]["report_id"], "RPT-001")
            self.assertEqual(gates[3]["name"], "machine_review_gate")
            self.assertEqual(gates[3]["status"], "pass")
            self.assertEqual(gates[4]["name"], "codex_review_gate")
            self.assertEqual(latest["report_ids"], ["RPT-001"])
            self.assertIn(["codex", "exec"], calls)

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
            session = create_session(root=root, actor="tester", policy=policy)
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
            session = create_session(root=root, actor="tester", policy=policy)
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
            session = create_session(root=root, actor="tester", policy=policy)
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

    def test_autoclose_policy_stops_when_review_gates_are_unimplemented(self):
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
            self.assertIn("not implemented", result.data["stop_reason"])


if __name__ == "__main__":
    unittest.main()

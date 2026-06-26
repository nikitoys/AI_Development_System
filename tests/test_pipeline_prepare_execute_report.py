import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from ai_project_ctl.pipeline import CodexAdapterMode, CodexExecutionMode, policy_preset
from ai_project_ctl.pipeline.codex_adapter import (
    CODE_LOCAL_COMMAND_PASSED,
    CodexAdapterResult,
)
from ai_project_ctl.pipeline.execute_phase import execute_phase
from ai_project_ctl.pipeline.phase import PhaseResult
from ai_project_ctl.pipeline.prepare_phase import prepare_phase
from ai_project_ctl.pipeline.report_phase import REPORT_MISSING, collect_report_phase
from ai_project_ctl.pipeline.session import create_session, record_phase_result
from ai_project_ctl.pipeline.state import pipeline_state_path


TIMESTAMP = "2026-06-25T00:00:00Z"
TASK_ID = "TASK-001"
TASK_REF = "APP-01"


def write_project_state(root: Path, *, changes: list[dict] | None = None) -> None:
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
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
                        "key": "PIPE",
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
                        "id": TASK_ID,
                        "ref": TASK_REF,
                        "uid": "uid_task_001",
                        "legacy_id": TASK_ID,
                        "aliases": [TASK_ID],
                        "title": "Pipeline phase boundary task",
                        "summary": "Exercise phase boundaries.",
                        "description": "Test phase boundaries with fake adapters.",
                        "scope": ["Test queue, prepare, execute, and report phases."],
                        "out_of_scope": ["Do not run downstream gates."],
                        "acceptance_criteria": ["Phase boundary behavior is covered."],
                        "review_instructions": ["Check boundary assertions."],
                        "status": "ready",
                        "epic_id": "EPIC-001",
                        "priority": 1,
                        "order": 1,
                        "local_seq": 1,
                        "depends_on": [],
                        "allowed_files": [
                            "tests/test_pipeline_queue_phase.py",
                            "tests/test_pipeline_prepare_execute_report.py",
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (state_dir / "evolution.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "changes": list(changes or []),
            }
        ),
        encoding="utf-8",
    )


def write_empty_task_reports(root: Path) -> None:
    path = root / "AI_PROJECT" / "state" / "task_reports.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "created_at": TIMESTAMP,
                "updated_at": TIMESTAMP,
                "latest_by_task": {},
                "reports": [],
            }
        ),
        encoding="utf-8",
    )


def write_prompt(root: Path, text: str = "Source ID: TASK-001\n\nSmall prompt.") -> str:
    prompt = root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"
    prompt.parent.mkdir(parents=True, exist_ok=True)
    prompt.write_text(text, encoding="utf-8")
    return hashlib.sha256(prompt.read_bytes()).hexdigest()


def executable_policy():
    supervised = policy_preset("supervised")
    return replace(
        supervised,
        name="phase_boundary_executable",
        codex=replace(
            supervised.codex,
            mode=CodexExecutionMode.RUN_CODEX,
            adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
            local_command=("codex", "exec"),
            command_allowlist=("codex exec",),
            timeout_sec=30,
            require_report=True,
        ),
    )


def create_current_task_session(root: Path, *, policy=None) -> str:
    result = create_session(
        root=root,
        actor="tester",
        policy=policy,
        current_task_id=TASK_ID,
        current_task_ref=TASK_REF,
    )
    if not result.ok:
        raise AssertionError(result.errors)
    return str(result.data["session_id"])


def write_report_state(
    root: Path,
    *,
    report_id: str = "RPT-001",
    task_id: str = TASK_ID,
    task_ref: str = TASK_REF,
) -> None:
    path = root / "AI_PROJECT" / "state" / "task_reports.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "created_at": TIMESTAMP,
                "updated_at": "2026-06-25T00:00:10Z",
                "latest_by_task": {task_id: report_id},
                "reports": [
                    {
                        "id": report_id,
                        "task_id": task_id,
                        "task_ref": task_ref,
                        "submitted_at": "2026-06-25T00:00:10Z",
                        "submitted_by": "tester",
                        "source_file": "/tmp/report.json",
                        "report": {
                            "task_id": task_id,
                            "task_ref": task_ref,
                            "reported_task_id": task_id,
                            "reported_task_ref": task_ref,
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def load_pipeline(root: Path) -> dict:
    return json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))


class PipelinePrepareExecuteReportBoundaryTests(unittest.TestCase):
    def test_prepare_blocks_on_missing_approved_change_before_codex_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root)
            session = create_session(
                root=root,
                actor="tester",
                policy_name="supervised",
                task_refs=(TASK_REF,),
                max_tasks=1,
                order_by="selected",
            )
            self.assertTrue(session.ok)
            runner_calls = []

            def forbidden_runner(argv):
                runner_calls.append(list(argv))
                raise AssertionError("prepare must block before workflow execution")

            with patch("ai_project_ctl.pipeline.codex_adapter.run_codex_adapter") as adapter:
                adapter.side_effect = AssertionError("prepare must not call Codex")

                result = prepare_phase(
                    str(session.data["session_id"]),
                    root=root,
                    actor="tester",
                    runner=forbidden_runner,
                )

                adapter.assert_not_called()

            phase = result.data["phase_result"]
            change_gate = phase["artifacts"]["change_gate"]

            self.assertTrue(result.ok)
            self.assertEqual(phase["status"], "blocked")
            self.assertEqual(phase["artifacts"]["blocked_by"], "BLOCKED")
            self.assertEqual(change_gate["tasks_requiring_approval"], [TASK_ID])
            self.assertEqual(change_gate["linked_change_ids"], [])
            self.assertEqual(runner_calls, [])

    def test_execute_records_fake_adapter_evidence_without_report_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root)
            write_empty_task_reports(root)
            prompt_sha = write_prompt(root)
            session_id = create_current_task_session(root, policy=executable_policy())
            prepared = record_phase_result(
                session_id,
                PhaseResult.passed(
                    "prepare",
                    reason="Prompt ready",
                    artifacts={
                        "task_id": TASK_ID,
                        "prompt_path": "AI_PROJECT/generated/CODEX_PROMPT.md",
                        "prompt_sha256": prompt_sha,
                    },
                ),
                root=root,
                actor="tester",
                task_id=TASK_ID,
                command="pipeline.phase.prepare",
            )
            self.assertTrue(prepared.ok)
            adapter_calls = []

            def fake_adapter(**kwargs):
                adapter_calls.append(kwargs)
                policy = kwargs["policy"]
                token_gate = kwargs["token_gate"]
                return CodexAdapterResult(
                    status="passed",
                    code=CODE_LOCAL_COMMAND_PASSED,
                    reason="fake_adapter_passed",
                    mode=policy.codex.adapter_mode.value,
                    started_at="2026-06-25T00:00:00Z",
                    finished_at="2026-06-25T00:00:01Z",
                    duration_sec=1.0,
                    prompt_path=token_gate.prompt_path,
                    prompt_sha256=token_gate.prompt_sha256,
                    prompt_transport=policy.codex.prompt_transport.value,
                    command=("codex", "exec"),
                    command_ref="codex exec",
                    timeout_sec=policy.codex.timeout_sec,
                    returncode=0,
                    stdout_ref="fake:stdout",
                    stderr_ref="fake:stderr",
                    stdout_snippet="fake stdout",
                    stderr_snippet="",
                    stdout_bytes=11,
                    stderr_bytes=0,
                    runtime_logs={
                        "stdout": {"path": "fake/stdout.log", "bytes": 11},
                        "stderr": {"path": "fake/stderr.log", "bytes": 0},
                    },
                    before_report_id="",
                    after_report_id="RPT-FAKE",
                    report_id="RPT-FAKE",
                )

            with patch("ai_project_ctl.pipeline.report_gate.evaluate_report_gate") as report_gate:
                report_gate.side_effect = AssertionError(
                    "execute must not run report gate"
                )

                result = execute_phase(
                    session_id,
                    root=root,
                    actor="tester",
                    codex_adapter=fake_adapter,
                )

                report_gate.assert_not_called()

            phase = result.data["phase_result"]
            artifacts = phase["artifacts"]
            state = load_pipeline(root)
            execute_phases = [
                item
                for item in state["sessions"][0]["phase_history"]
                if item["phase"] == "execute"
            ]

            self.assertTrue(result.ok)
            self.assertEqual(len(adapter_calls), 1)
            self.assertEqual(adapter_calls[0]["session_id"], session_id)
            self.assertEqual(phase["status"], "passed")
            self.assertEqual(len(execute_phases), 1)
            self.assertTrue(artifacts["codex_adapter_called"])
            self.assertEqual(artifacts["execute_evidence"]["code"], CODE_LOCAL_COMMAND_PASSED)
            self.assertEqual(artifacts["execute_evidence"]["report_id"], "RPT-FAKE")
            self.assertEqual(artifacts["adapter_summary"]["reason"], "fake_adapter_passed")
            self.assertEqual(artifacts["adapter_summary"]["stdout_snippet"], "fake stdout")

    def test_collect_report_blocks_for_missing_report_for_selected_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root)
            session_id = create_current_task_session(root)

            result = collect_report_phase(session_id, root=root, actor="tester")

            phase = result.data["phase_result"]
            artifacts = phase["artifacts"]

            self.assertTrue(result.ok)
            self.assertEqual(phase["status"], "blocked")
            self.assertEqual(artifacts["blocked_by"], REPORT_MISSING)
            self.assertEqual(result.data["task_id"], TASK_ID)
            self.assertEqual(result.data["report_id"], "")
            self.assertEqual(artifacts["task_id"], TASK_ID)
            self.assertEqual(artifacts["report_id"], "")

    def test_collect_report_passes_for_matching_fresh_report_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root)
            write_report_state(root)
            session_id = create_current_task_session(root)
            executed = record_phase_result(
                session_id,
                PhaseResult.passed(
                    "execute",
                    reason="Fake execution completed.",
                    artifacts={
                        "task_id": TASK_ID,
                        "execute_started_at": "2026-06-25T00:00:00Z",
                        "execute_finished_at": "2026-06-25T00:00:05Z",
                        "before_report_id": "",
                        "after_report_id": "RPT-001",
                        "report_id": "RPT-001",
                        "execute_evidence": {
                            "started_at": "2026-06-25T00:00:00Z",
                            "finished_at": "2026-06-25T00:00:05Z",
                            "report_id": "RPT-001",
                        },
                    },
                ),
                root=root,
                actor="tester",
                task_id=TASK_ID,
                command="pipeline.phase.execute",
            )
            self.assertTrue(executed.ok)

            result = collect_report_phase(session_id, root=root, actor="tester")

            phase = result.data["phase_result"]
            artifacts = phase["artifacts"]

            self.assertTrue(result.ok)
            self.assertEqual(phase["status"], "passed")
            self.assertEqual(result.data["task_id"], TASK_ID)
            self.assertEqual(result.data["report_id"], "RPT-001")
            self.assertEqual(artifacts["task_id"], TASK_ID)
            self.assertEqual(artifacts["report_id"], "RPT-001")
            self.assertEqual(artifacts["expected_task_id"], TASK_ID)
            self.assertEqual(artifacts["selected_task_ref"], TASK_REF)
            self.assertEqual(artifacts["structured_report_task_id"], TASK_ID)
            self.assertEqual(artifacts["structured_report_task_ref"], TASK_REF)
            self.assertEqual(artifacts["reported_task_id"], TASK_ID)
            self.assertEqual(artifacts["reported_task_ref"], TASK_REF)
            self.assertTrue(artifacts["report_found"])
            self.assertEqual(artifacts["freshness"]["basis"], "report_id")


if __name__ == "__main__":
    unittest.main()

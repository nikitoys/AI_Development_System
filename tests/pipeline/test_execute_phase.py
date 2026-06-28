import hashlib
import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ai_project_ctl.pipeline import CodexAdapterMode, CodexExecutionMode, policy_preset
from ai_project_ctl.pipeline.codex_adapter import (
    CODE_LOCAL_COMMAND_PASSED,
    CodexAdapterResult,
)
from ai_project_ctl.pipeline.execute_phase import execute_phase
from ai_project_ctl.pipeline.phase import PhaseResult
from ai_project_ctl.pipeline.report_gate import CODE_PASS as REPORT_GATE_PASS_CODE
from ai_project_ctl.pipeline.report_gate import PASS as REPORT_GATE_PASS
from ai_project_ctl.pipeline.report_gate import evaluate_report_gate
from ai_project_ctl.pipeline.session import (
    create_session,
    record_phase_result,
    validate_sessions,
)
from ai_project_ctl.pipeline.state import pipeline_state_path


def write_execute_project_state(
    root: Path,
    *,
    allowed_files: list[str] | None = None,
) -> str:
    state_dir = root / "AI_PROJECT" / "state"
    generated_dir = root / "AI_PROJECT" / "generated"
    state_dir.mkdir(parents=True, exist_ok=True)
    generated_dir.mkdir(parents=True, exist_ok=True)

    (state_dir / "tasks.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "created_at": "2026-06-24T00:00:00Z",
                "updated_at": "2026-06-24T00:00:00Z",
                "current_task_id": None,
                "tasks": [
                    {
                        "id": "TASK-001",
                        "ref": "PIPE-001",
                        "uid": "uid_task_001",
                        "legacy_id": "TASK-001",
                        "aliases": ["TASK-001"],
                        "status": "ready",
                        "allowed_files": list(allowed_files or []),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (state_dir / "evolution.json").write_text(
        json.dumps({"schema_version": 1, "revision": 1, "changes": []}),
        encoding="utf-8",
    )
    (state_dir / "task_reports.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "created_at": "2026-06-24T00:00:00Z",
                "updated_at": "2026-06-24T00:00:00Z",
                "latest_by_task": {},
                "reports": [],
            }
        ),
        encoding="utf-8",
    )
    prompt = generated_dir / "CODEX_PROMPT.md"
    prompt.write_text("Source ID: TASK-001\n\nPrepared prompt.", encoding="utf-8")
    return hashlib.sha256(prompt.read_bytes()).hexdigest()


def executable_policy():
    supervised = policy_preset("supervised")
    return replace(
        supervised,
        name="execute_phase_runtime_logs_test",
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


def load_pipeline(root: Path) -> dict:
    return json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))


def load_task_reports(root: Path) -> dict:
    return json.loads(
        (root / "AI_PROJECT" / "state" / "task_reports.json").read_text(
            encoding="utf-8"
        )
    )


def init_git(root: Path) -> None:
    subprocess.run(
        ["git", "init"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def stdout_for_summary(**overrides) -> str:
    payload = {
        "implementation_summary": "Generated smoke artifact.",
        "notes": [],
        "warnings": [],
        "blockers": [],
    }
    payload.update(overrides)
    return "Codex done.\nCODEX_EXECUTION_SUMMARY_JSON:\n```json\n{}\n```\n".format(
        json.dumps(payload, indent=2, sort_keys=True)
    )


def protected_check_stdout() -> str:
    return json.dumps({"ok": True, "errors": [], "warnings": [], "checked": []})


class ExecutePhaseRuntimeLogTests(unittest.TestCase):
    def test_execute_artifacts_include_runtime_log_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prompt_sha256 = write_execute_project_state(root)
            session = create_session(
                root=root,
                actor="tester",
                policy=executable_policy(),
                current_task_id="TASK-001",
            )
            session_id = str(session.data["session_id"])
            prepare = record_phase_result(
                session_id,
                PhaseResult.passed(
                    "prepare",
                    reason="Prompt ready",
                    artifacts={
                        "task_id": "TASK-001",
                        "prompt_path": "AI_PROJECT/generated/CODEX_PROMPT.md",
                        "prompt_sha256": prompt_sha256,
                    },
                ),
                root=root,
                actor="tester",
                task_id="TASK-001",
                command="pipeline.phase.prepare",
            )
            self.assertTrue(prepare.ok)

            runtime_logs = {
                "stdout": {
                    "path": "AI_PROJECT/logs/codex/PSESS-001/TASK-001-stdout.log",
                    "start_offset": 12,
                    "end_offset": 48,
                    "bytes": 36,
                },
                "stderr": {
                    "path": "AI_PROJECT/logs/codex/PSESS-001/TASK-001-stderr.log",
                    "start_offset": 3,
                    "end_offset": 7,
                    "bytes": 4,
                },
            }
            seen = {}
            live_state = {}

            def fake_adapter(**kwargs):
                seen.update(kwargs)
                live_state.update(load_pipeline(root)["sessions"][0])
                self.assertTrue(validate_sessions(root=root).ok)
                policy = kwargs["policy"]
                token_gate = kwargs["token_gate"]
                return CodexAdapterResult(
                    status="passed",
                    code=CODE_LOCAL_COMMAND_PASSED,
                    reason="local_command_completed_with_report",
                    mode=policy.codex.adapter_mode.value,
                    started_at="2026-06-24T00:00:00Z",
                    finished_at="2026-06-24T00:00:01Z",
                    duration_sec=1.0,
                    prompt_path=token_gate.prompt_path,
                    prompt_sha256=token_gate.prompt_sha256,
                    prompt_transport=policy.codex.prompt_transport.value,
                    command=("codex", "exec"),
                    command_ref="codex exec",
                    timeout_sec=policy.codex.timeout_sec,
                    returncode=0,
                    stdout_ref="captured:stdout:sha256:abc",
                    stderr_ref="captured:stderr:sha256:def",
                    stdout_snippet="runtime stdout",
                    stderr_snippet="runtime stderr",
                    stdout_bytes=36,
                    stderr_bytes=4,
                    runtime_logs=runtime_logs,
                    before_report_id="",
                    after_report_id="RPT-001",
                    report_id="RPT-001",
                )

            def protected_runner(argv, stdin_text=None):
                return subprocess.CompletedProcess(
                    args=list(argv),
                    returncode=0,
                    stdout=protected_check_stdout(),
                    stderr="",
                )

            result = execute_phase(
                session_id,
                root=root,
                actor="tester",
                codex_adapter=fake_adapter,
                execution_runner=protected_runner,
            )
            latest_phase = load_pipeline(root)["sessions"][0]["phase_history"][-1]
            session_state = load_pipeline(root)["sessions"][0]
            artifacts = latest_phase["artifacts"]

            self.assertTrue(result.ok)
            self.assertEqual(seen["session_id"], session_id)
            self.assertEqual(live_state["current_phase"], "execute")
            self.assertEqual(live_state["current_phase_status"], "running")
            self.assertEqual(live_state["current_step"], "execute")
            self.assertEqual(live_state["current_step_status"], "running")
            live_phase = live_state["phase_history"][-1]
            self.assertEqual(live_phase["phase"], "execute")
            self.assertEqual(live_phase["status"], "running")
            live_artifacts = live_phase["artifacts"]
            self.assertEqual(live_artifacts["session_id"], session_id)
            self.assertEqual(live_artifacts["task_id"], "TASK-001")
            self.assertEqual(live_artifacts["adapter"]["mode"], "local_command")
            self.assertEqual(live_artifacts["adapter"]["command_ref"], "codex exec")
            self.assertEqual(live_artifacts["adapter"]["timeout_sec"], 30)
            self.assertEqual(
                live_artifacts["runtime_logs"]["stdout"]["path"],
                "AI_PROJECT/logs/codex/PSESS-001/TASK-001-stdout.log",
            )
            self.assertEqual(
                live_artifacts["runtime_logs"]["stderr"]["path"],
                "AI_PROJECT/logs/codex/PSESS-001/TASK-001-stderr.log",
            )
            self.assertEqual(
                live_artifacts["execute_evidence"]["command_ref"],
                "codex exec",
            )
            self.assertEqual(latest_phase["status"], "passed")
            self.assertEqual(session_state["current_phase"], "execute")
            self.assertEqual(session_state["current_phase_status"], "passed")
            self.assertEqual(session_state["current_step_status"], "passed")
            execute_phases = [
                phase
                for phase in session_state["phase_history"]
                if phase["phase"] == "execute"
            ]
            self.assertEqual(len(execute_phases), 1)
            self.assertEqual(artifacts["runtime_logs"], runtime_logs)
            self.assertEqual(artifacts["adapter"]["runtime_logs"], runtime_logs)
            self.assertEqual(
                artifacts["adapter_summary"]["runtime_logs"],
                runtime_logs,
            )
            self.assertEqual(
                artifacts["execute_evidence"]["runtime_logs"],
                runtime_logs,
            )
            self.assertEqual(
                artifacts["execute_evidence"]["stdout_ref"],
                "captured:stdout:sha256:abc",
            )

    def test_local_command_created_allowed_file_is_added_to_report_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_git(root)
            smoke_file = "tmp/run-smoke/web-run-smoke.md"
            prompt_sha256 = write_execute_project_state(
                root,
                allowed_files=[smoke_file],
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=executable_policy(),
                current_task_id="TASK-001",
            )
            session_id = str(session.data["session_id"])
            prepare = record_phase_result(
                session_id,
                PhaseResult.passed(
                    "prepare",
                    reason="Prompt ready",
                    artifacts={
                        "task_id": "TASK-001",
                        "prompt_path": "AI_PROJECT/generated/CODEX_PROMPT.md",
                        "prompt_sha256": prompt_sha256,
                    },
                ),
                root=root,
                actor="tester",
                task_id="TASK-001",
                command="pipeline.phase.prepare",
            )
            self.assertTrue(prepare.ok)

            def runner(argv, stdin_text=None):
                command = tuple(str(part) for part in argv)
                if command[-2:] == ("project", "protected-check"):
                    return subprocess.CompletedProcess(
                        args=list(command),
                        returncode=0,
                        stdout=protected_check_stdout(),
                        stderr="",
                    )
                self.assertEqual(command, ("codex", "exec"))
                path = root / smoke_file
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("smoke artifact\n", encoding="utf-8")
                return subprocess.CompletedProcess(
                    args=list(command),
                    returncode=0,
                    stdout=stdout_for_summary(),
                    stderr="",
                )

            result = execute_phase(
                session_id,
                root=root,
                actor="tester",
                execution_runner=runner,
            )
            reports = load_task_reports(root)
            latest_id = reports["latest_by_task"]["TASK-001"]
            latest = next(
                record for record in reports["reports"] if record["id"] == latest_id
            )
            report = latest["report"]
            session_state = load_pipeline(root)["sessions"][0]
            artifacts = session_state["phase_history"][-1]["artifacts"]
            task_payload = json.loads(
                (root / "AI_PROJECT" / "state" / "tasks.json").read_text(
                    encoding="utf-8"
                )
            )["tasks"][0]
            report_gate = evaluate_report_gate(
                root=root,
                task=task_payload,
                policy=executable_policy(),
            )

            self.assertTrue(result.ok, result.to_dict())
            self.assertEqual(latest_id, "RPT-002")
            self.assertEqual(report["changed_files"], [smoke_file])
            self.assertEqual(report["warnings"], [])
            self.assertEqual(report_gate.status, REPORT_GATE_PASS)
            self.assertEqual(report_gate.code, REPORT_GATE_PASS_CODE)
            self.assertEqual(report_gate.changed_files, (smoke_file,))
            self.assertEqual(
                artifacts["execute_file_delta"]["allowed_changed_files"],
                [smoke_file],
            )
            self.assertEqual(artifacts["report_id"], "RPT-002")

    def test_local_command_out_of_scope_file_is_reported_but_not_approved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_git(root)
            outside_file = "tmp/run-smoke/outside.md"
            prompt_sha256 = write_execute_project_state(
                root,
                allowed_files=["tmp/run-smoke/web-run-smoke.md"],
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=executable_policy(),
                current_task_id="TASK-001",
            )
            session_id = str(session.data["session_id"])
            prepare = record_phase_result(
                session_id,
                PhaseResult.passed(
                    "prepare",
                    reason="Prompt ready",
                    artifacts={
                        "task_id": "TASK-001",
                        "prompt_path": "AI_PROJECT/generated/CODEX_PROMPT.md",
                        "prompt_sha256": prompt_sha256,
                    },
                ),
                root=root,
                actor="tester",
                task_id="TASK-001",
                command="pipeline.phase.prepare",
            )
            self.assertTrue(prepare.ok)

            def runner(argv, stdin_text=None):
                command = tuple(str(part) for part in argv)
                if command[-2:] == ("project", "protected-check"):
                    return subprocess.CompletedProcess(
                        args=list(command),
                        returncode=0,
                        stdout=protected_check_stdout(),
                        stderr="",
                    )
                self.assertEqual(command, ("codex", "exec"))
                path = root / outside_file
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("out of scope\n", encoding="utf-8")
                return subprocess.CompletedProcess(
                    args=list(command),
                    returncode=0,
                    stdout=stdout_for_summary(),
                    stderr="",
                )

            result = execute_phase(
                session_id,
                root=root,
                actor="tester",
                execution_runner=runner,
            )
            reports = load_task_reports(root)
            latest_id = reports["latest_by_task"]["TASK-001"]
            latest = next(
                record for record in reports["reports"] if record["id"] == latest_id
            )
            report = latest["report"]
            session_state = load_pipeline(root)["sessions"][0]
            artifacts = session_state["phase_history"][-1]["artifacts"]
            task_payload = json.loads(
                (root / "AI_PROJECT" / "state" / "tasks.json").read_text(
                    encoding="utf-8"
                )
            )["tasks"][0]
            report_gate = evaluate_report_gate(
                root=root,
                task=task_payload,
                policy=executable_policy(),
            )

            self.assertTrue(result.ok, result.to_dict())
            self.assertEqual(latest_id, "RPT-002")
            self.assertEqual(report["changed_files"], [])
            self.assertIn(outside_file, report["warnings"][0])
            self.assertEqual(report_gate.status, "warn")
            self.assertEqual(
                artifacts["execute_file_delta"]["out_of_scope_changed_files"],
                [outside_file],
            )
            self.assertNotIn(
                outside_file,
                artifacts["execute_file_delta"]["allowed_changed_files"],
            )


if __name__ == "__main__":
    unittest.main()

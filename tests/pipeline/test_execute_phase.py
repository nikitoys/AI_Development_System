import hashlib
import json
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
from ai_project_ctl.pipeline.session import create_session, record_phase_result
from ai_project_ctl.pipeline.state import pipeline_state_path


def write_execute_project_state(root: Path) -> str:
    state_dir = root / "AI_PROJECT" / "state"
    generated_dir = root / "AI_PROJECT" / "generated"
    state_dir.mkdir(parents=True, exist_ok=True)
    generated_dir.mkdir(parents=True, exist_ok=True)

    (state_dir / "tasks.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "current_task_id": None,
                "tasks": [
                    {
                        "id": "TASK-001",
                        "ref": "PIPE-001",
                        "uid": "uid_task_001",
                        "legacy_id": "TASK-001",
                        "aliases": ["TASK-001"],
                        "status": "ready",
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

            def fake_adapter(**kwargs):
                seen.update(kwargs)
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

            result = execute_phase(
                session_id,
                root=root,
                actor="tester",
                codex_adapter=fake_adapter,
            )
            latest_phase = load_pipeline(root)["sessions"][0]["phase_history"][-1]
            artifacts = latest_phase["artifacts"]

            self.assertTrue(result.ok)
            self.assertEqual(seen["session_id"], session_id)
            self.assertEqual(latest_phase["status"], "passed")
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


if __name__ == "__main__":
    unittest.main()

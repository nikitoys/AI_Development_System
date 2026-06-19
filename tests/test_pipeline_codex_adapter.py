import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ai_project_ctl.pipeline import CodexAdapterMode, CodexExecutionMode, policy_preset
from ai_project_ctl.pipeline.codex_adapter import (
    CODE_LOCAL_COMMAND_PASSED,
    CODE_MANUAL_HANDOFF,
    CODE_PROMPT_STALE,
    CODE_REPORT_MISSING,
    run_codex_adapter,
)
from ai_project_ctl.pipeline.token_budget import evaluate_token_budget


def completed(stdout="OK\n", returncode=0, stderr=""):
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def write_prompt(root: Path, task_id: str = "TASK-001", text: str | None = None) -> Path:
    path = root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text or "Source ID: {}\n\nSmall prompt.\n".format(task_id), encoding="utf-8")
    return path


def write_report_state(root: Path, task_id: str, report_id: str) -> None:
    path = root / "AI_PROJECT" / "state" / "task_reports.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
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
                        "submitted_at": "2026-06-19T00:00:00Z",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def run_codex_policy(adapter_mode=CodexAdapterMode.MANUAL_HANDOFF):
    supervised = policy_preset("supervised")
    return replace(
        supervised,
        name="run_codex_adapter_test",
        codex=replace(
            supervised.codex,
            mode=CodexExecutionMode.RUN_CODEX,
            adapter_mode=adapter_mode,
            local_command=("codex", "exec"),
            command_allowlist=("codex exec",),
            timeout_sec=30,
        ),
    )


class PipelineCodexAdapterTests(unittest.TestCase):
    def test_default_manual_handoff_does_not_call_external_runner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prompt(root)
            policy = run_codex_policy()
            token_gate = evaluate_token_budget(root=root, policy=policy.token_budget)
            calls = []

            result = run_codex_adapter(
                root=root,
                task_id="TASK-001",
                policy=policy,
                token_gate=token_gate,
                runner=lambda argv: calls.append(list(argv)) or completed(),
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.status, "blocked")
            self.assertEqual(result.code, CODE_MANUAL_HANDOFF)
            self.assertEqual(calls, [])
            self.assertIn("task report submit", result.report_instruction)

    def test_local_command_requires_new_structured_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prompt(root)
            policy = run_codex_policy(CodexAdapterMode.LOCAL_COMMAND)
            token_gate = evaluate_token_budget(root=root, policy=policy.token_budget)

            result = run_codex_adapter(
                root=root,
                task_id="TASK-001",
                policy=policy,
                token_gate=token_gate,
                runner=lambda argv: completed(stdout="Codex finished without report\n"),
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.status, "blocked")
            self.assertEqual(result.code, CODE_REPORT_MISSING)
            self.assertEqual(result.returncode, 0)
            self.assertTrue(result.stdout_ref)

    def test_local_command_passes_when_report_is_submitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prompt(root)
            policy = run_codex_policy(CodexAdapterMode.LOCAL_COMMAND)
            token_gate = evaluate_token_budget(root=root, policy=policy.token_budget)
            calls = []

            def fake_runner(argv):
                calls.append(list(argv))
                write_report_state(root, "TASK-001", "RPT-001")
                return completed(stdout="report submitted\n")

            result = run_codex_adapter(
                root=root,
                task_id="TASK-001",
                policy=policy,
                token_gate=token_gate,
                runner=fake_runner,
            )

            self.assertTrue(result.ok)
            self.assertEqual(result.code, CODE_LOCAL_COMMAND_PASSED)
            self.assertEqual(result.report_id, "RPT-001")
            self.assertEqual(calls, [["codex", "exec"]])

    def test_prompt_change_after_token_gate_is_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prompt = write_prompt(root)
            policy = run_codex_policy(CodexAdapterMode.LOCAL_COMMAND)
            token_gate = evaluate_token_budget(root=root, policy=policy.token_budget)
            prompt.write_text("Source ID: TASK-001\n\nChanged prompt.\n", encoding="utf-8")

            result = run_codex_adapter(
                root=root,
                task_id="TASK-001",
                policy=policy,
                token_gate=token_gate,
                runner=lambda argv: completed(),
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.status, "failed")
            self.assertEqual(result.code, CODE_PROMPT_STALE)


if __name__ == "__main__":
    unittest.main()

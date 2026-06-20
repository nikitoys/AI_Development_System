import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ai_project_ctl.pipeline import CodexAdapterMode, CodexExecutionMode, policy_preset
from ai_project_ctl.pipeline.codex_adapter import (
    CODE_LOCAL_COMMAND_PASSED,
    CODE_LOCAL_COMMAND_FAILED,
    CODE_LOCAL_COMMAND_TIMEOUT,
    CODE_MANUAL_HANDOFF,
    CODE_POLICY_DENIED,
    CODE_PROMPT_STALE,
    CODE_REPORT_MISSING,
    CODE_SANDBOX_UNAVAILABLE,
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


def run_codex_policy(
    adapter_mode=CodexAdapterMode.MANUAL_HANDOFF,
    *,
    local_command=("codex", "exec"),
    command_allowlist=("codex exec",),
):
    supervised = policy_preset("supervised")
    return replace(
        supervised,
        name="run_codex_adapter_test",
        codex=replace(
            supervised.codex,
            mode=CodexExecutionMode.RUN_CODEX,
            adapter_mode=adapter_mode,
            local_command=local_command,
            command_allowlist=command_allowlist,
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
            self.assertIn("Codex finished without report", result.stdout_snippet)
            self.assertEqual(result.prompt_transport, "stdin")

    def test_local_command_passes_prompt_on_stdin_when_report_is_submitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prompt_text = "Source ID: TASK-001\n\nUnique stdin prompt body.\n"
            write_prompt(root, text=prompt_text)
            policy = run_codex_policy(CodexAdapterMode.LOCAL_COMMAND)
            token_gate = evaluate_token_budget(root=root, policy=policy.token_budget)
            calls = []
            stdin_values = []

            def fake_runner(argv, stdin_text):
                calls.append(list(argv))
                stdin_values.append(stdin_text)
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
            self.assertEqual(stdin_values, [prompt_text])
            self.assertNotIn("Unique stdin prompt body", result.to_dict()["stdout_snippet"])

    def test_local_command_with_owner_configured_sandbox_flags_is_allowlisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prompt_text = "Source ID: TASK-001\n\nSandbox flag prompt.\n"
            write_prompt(root, text=prompt_text)
            policy = run_codex_policy(
                CodexAdapterMode.LOCAL_COMMAND,
                local_command=("codex", "exec", "-s", "workspace-write"),
                command_allowlist=("codex exec -s workspace-write",),
            )
            token_gate = evaluate_token_budget(root=root, policy=policy.token_budget)
            calls = []

            def fake_runner(argv, stdin_text):
                calls.append(list(argv))
                self.assertEqual(stdin_text, prompt_text)
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
            self.assertEqual(calls, [["codex", "exec", "-s", "workspace-write"]])

    def test_local_command_refuses_non_allowlisted_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prompt(root)
            policy = run_codex_policy(
                CodexAdapterMode.LOCAL_COMMAND,
                local_command=("codex", "exec", "-s", "danger-full-access"),
                command_allowlist=("codex exec",),
            )
            token_gate = evaluate_token_budget(root=root, policy=policy.token_budget)
            calls = []

            result = run_codex_adapter(
                root=root,
                task_id="TASK-001",
                policy=policy,
                token_gate=token_gate,
                runner=lambda argv, stdin_text: calls.append(list(argv)) or completed(),
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.status, "failed")
            self.assertEqual(result.code, CODE_POLICY_DENIED)
            self.assertEqual(result.reason, "local_command_not_allowlisted")
            self.assertEqual(calls, [])

    def test_local_command_nonzero_exit_includes_bounded_stderr_snippet(self):
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
                runner=lambda argv, stdin_text: completed(
                    returncode=7,
                    stdout="short stdout\n",
                    stderr="readable stderr diagnostic\n" + ("x" * 2000),
                ),
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.status, "failed")
            self.assertEqual(result.code, CODE_LOCAL_COMMAND_FAILED)
            self.assertEqual(result.reason, "local_command_nonzero_exit")
            self.assertEqual(result.returncode, 7)
            self.assertTrue(result.stderr_ref)
            self.assertIn("readable stderr diagnostic", result.stderr_snippet)
            self.assertIn("[truncated:", result.stderr_snippet)

    def test_local_command_sandbox_failure_is_reported_as_compatibility_blocker(self):
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
                runner=lambda argv, stdin_text: completed(
                    returncode=1,
                    stderr=(
                        "bwrap: RTM_NEWADDR failed: Operation not permitted; "
                        "user namespace unavailable\n"
                    ),
                ),
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.status, "blocked")
            self.assertEqual(result.code, CODE_SANDBOX_UNAVAILABLE)
            self.assertEqual(result.reason, "codex_sandbox_unavailable")
            self.assertIn("bwrap", result.stderr_snippet)

    def test_local_command_timeout_keeps_bounded_output_diagnostics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prompt(root)
            policy = run_codex_policy(CodexAdapterMode.LOCAL_COMMAND)
            token_gate = evaluate_token_budget(root=root, policy=policy.token_budget)

            def timeout_runner(argv, stdin_text):
                raise subprocess.TimeoutExpired(
                    cmd=list(argv),
                    timeout=30,
                    output=b"partial stdout\n",
                    stderr=b"partial stderr\n",
                )

            result = run_codex_adapter(
                root=root,
                task_id="TASK-001",
                policy=policy,
                token_gate=token_gate,
                runner=timeout_runner,
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.status, "failed")
            self.assertEqual(result.code, CODE_LOCAL_COMMAND_TIMEOUT)
            self.assertTrue(result.timed_out)
            self.assertIn("partial stdout", result.stdout_snippet)
            self.assertIn("partial stderr", result.stderr_snippet)

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

    def test_wrong_task_prompt_is_rejected_before_local_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prompt(root, task_id="TASK-999")
            policy = run_codex_policy(CodexAdapterMode.LOCAL_COMMAND)
            token_gate = evaluate_token_budget(root=root, policy=policy.token_budget)
            calls = []

            result = run_codex_adapter(
                root=root,
                task_id="TASK-001",
                policy=policy,
                token_gate=token_gate,
                runner=lambda argv, stdin_text: calls.append(list(argv)) or completed(),
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.status, "failed")
            self.assertEqual(result.code, CODE_PROMPT_STALE)
            self.assertEqual(result.reason, "prompt_task_mismatch")
            self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()

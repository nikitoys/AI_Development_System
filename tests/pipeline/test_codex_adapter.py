import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ai_project_ctl.pipeline import CodexAdapterMode, CodexExecutionMode, policy_preset
from ai_project_ctl.pipeline.codex_adapter import (
    CODE_LOCAL_COMMAND_FAILED,
    CODE_LOCAL_COMMAND_PASSED,
    CODE_REPORT_INVALID,
    CODE_REPORT_MISSING,
    run_codex_adapter,
)
from ai_project_ctl.pipeline.codex_report_parser import (
    CODEX_REPORT_JSON_MALFORMED,
    CODEX_REPORT_PARSE_OK,
)
from ai_project_ctl.pipeline.token_budget import evaluate_token_budget


def completed(stdout="OK\n", returncode=0, stderr=""):
    return subprocess.CompletedProcess(
        args=[],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def write_prompt(root: Path, task_id: str = "TASK-001") -> Path:
    path = root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "Source ID: {}\n\nSmall prompt.\n".format(task_id),
        encoding="utf-8",
    )
    return path


def write_task_state(root: Path, task_id: str = "TASK-001", task_ref: str = "APP-01"):
    path = root / "AI_PROJECT" / "state" / "tasks.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "created_at": "2026-06-24T00:00:00Z",
                "updated_at": "2026-06-24T00:00:00Z",
                "current_task_id": task_id,
                "tasks": [
                    {
                        "id": task_id,
                        "uid": "tsk_001",
                        "ref": task_ref,
                        "legacy_id": task_id,
                        "aliases": [task_id],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def report_payload(**overrides):
    payload = {
        "schema_version": 1,
        "task_id": "TASK-001",
        "task_ref": "APP-01",
        "implementation_summary": "Implemented adapter auto-submit.",
        "changed_files": ["ai_project_ctl/pipeline/codex_adapter.py"],
        "generated_files": [],
        "checks": [
            {
                "name": "unit",
                "command": "python -m unittest tests.pipeline.test_codex_adapter",
                "result": "passed",
            }
        ],
        "warnings": [],
        "blockers": [],
        "notes": [],
        "owner_decision_required": False,
        "token_usage": {
            "prompt_tokens": 1,
            "context_tokens": 1,
            "completion_tokens": 1,
            "output_tokens": 1,
            "total_tokens": 4,
            "remaining_tokens": 1,
            "model_context_limit": 10,
            "max_context_tokens": 10,
            "reserved_output_tokens": 1,
            "min_remaining_tokens": 0,
            "token_count_strategy": "test_fixture",
            "token_count_estimated": True,
            "token_count_unavailable": False,
            "token_count_unavailable_reason": "",
        },
    }
    payload.update(overrides)
    return payload


def stdout_for_report(payload):
    return "Codex finished.\nCODEX_REPORT_JSON:\n```json\n{}\n```\n".format(
        json.dumps(payload, indent=2, sort_keys=True)
    )


def run_codex_policy():
    supervised = policy_preset("supervised")
    return replace(
        supervised,
        name="codex_adapter_auto_submit_test",
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


class CodexAdapterAutoSubmitTests(unittest.TestCase):
    def test_successful_local_command_auto_submits_structured_stdout_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prompt(root)
            write_task_state(root)
            policy = run_codex_policy()
            token_gate = evaluate_token_budget(root=root, policy=policy.token_budget)

            result = run_codex_adapter(
                root=root,
                task_id="TASK-001",
                policy=policy,
                token_gate=token_gate,
                runner=lambda argv, stdin_text: completed(
                    stdout=stdout_for_report(report_payload())
                ),
            )

            state = json.loads(
                (root / "AI_PROJECT" / "state" / "task_reports.json").read_text(
                    encoding="utf-8"
                )
            )
            events = [
                json.loads(line)
                for line in (
                    root / "AI_PROJECT" / "events" / "task-report-events.jsonl"
                )
                .read_text(encoding="utf-8")
                .splitlines()
                if line.strip()
            ]

            self.assertTrue(result.ok)
            self.assertEqual(result.code, CODE_LOCAL_COMMAND_PASSED)
            self.assertEqual(result.report_id, "RPT-001")
            self.assertEqual(result.after_report_id, "RPT-001")
            self.assertEqual(result.report_parse_code, CODEX_REPORT_PARSE_OK)
            self.assertEqual(state["latest_by_task"], {"TASK-001": "RPT-001"})
            self.assertEqual(state["reports"][0]["report"]["reported_task_id"], "TASK-001")
            self.assertTrue(
                state["reports"][0]["source_file"].startswith(
                    "captured:stdout:sha256:"
                )
            )
            self.assertEqual(events[0]["command"], "codex_adapter.report.auto_submit")

    def test_successful_local_command_without_structured_report_still_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prompt(root)
            policy = run_codex_policy()
            token_gate = evaluate_token_budget(root=root, policy=policy.token_budget)

            result = run_codex_adapter(
                root=root,
                task_id="TASK-001",
                policy=policy,
                token_gate=token_gate,
                runner=lambda argv, stdin_text: completed(
                    stdout="Codex finished without structured report.\n"
                ),
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.status, "blocked")
            self.assertEqual(result.code, CODE_REPORT_MISSING)
            self.assertEqual(result.reason, "structured_execution_report_missing")
            self.assertFalse(
                (root / "AI_PROJECT" / "state" / "task_reports.json").exists()
            )

    def test_malformed_structured_report_blocks_with_parse_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prompt(root)
            write_task_state(root)
            policy = run_codex_policy()
            token_gate = evaluate_token_budget(root=root, policy=policy.token_budget)

            result = run_codex_adapter(
                root=root,
                task_id="TASK-001",
                policy=policy,
                token_gate=token_gate,
                runner=lambda argv, stdin_text: completed(
                    stdout="CODEX_REPORT_JSON:\n```json\n{\"task_id\": \n```\n"
                ),
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.status, "blocked")
            self.assertEqual(result.code, CODE_REPORT_INVALID)
            self.assertEqual(result.reason, "structured_execution_report_invalid")
            self.assertEqual(result.report_parse_code, CODEX_REPORT_JSON_MALFORMED)
            self.assertEqual(
                result.report_parse_issue["code"],
                CODEX_REPORT_JSON_MALFORMED,
            )
            self.assertFalse(
                (root / "AI_PROJECT" / "state" / "task_reports.json").exists()
            )

    def test_nonzero_local_command_does_not_auto_submit_stdout_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prompt(root)
            write_task_state(root)
            policy = run_codex_policy()
            token_gate = evaluate_token_budget(root=root, policy=policy.token_budget)

            result = run_codex_adapter(
                root=root,
                task_id="TASK-001",
                policy=policy,
                token_gate=token_gate,
                runner=lambda argv, stdin_text: completed(
                    returncode=7,
                    stdout=stdout_for_report(report_payload()),
                    stderr="command failed\n",
                ),
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.status, "failed")
            self.assertEqual(result.code, CODE_LOCAL_COMMAND_FAILED)
            self.assertFalse(
                (root / "AI_PROJECT" / "state" / "task_reports.json").exists()
            )


if __name__ == "__main__":
    unittest.main()

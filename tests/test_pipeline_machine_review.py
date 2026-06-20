import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ai_project_ctl.pipeline import CodexExecutionMode, policy_preset
from ai_project_ctl.pipeline.machine_review import (
    CODE_COMMAND_FAILED,
    CODE_PASS,
    CODE_PROTECTED_FILE_REPORTED,
    CODE_REPORT_GATE_FAILED,
    FAIL,
    PASS,
    WARN,
    evaluate_machine_review,
)
from ai_project_ctl.pipeline.report_gate import (
    CODE_OUT_OF_SCOPE_FILE,
    FAIL as REPORT_FAIL,
    PASS as REPORT_PASS,
    ReportGateIssue,
    ReportGateResult,
)


def completed(stdout="OK\n", returncode=0, stderr=""):
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def task():
    return {
        "id": "TASK-001",
        "ref": "APP-01",
        "allowed_files": [
            "ai_project_ctl/pipeline/machine_review.py",
            "tests/**",
        ],
    }


def run_codex_policy():
    supervised = policy_preset("supervised")
    return replace(
        supervised,
        codex=replace(supervised.codex, mode=CodexExecutionMode.RUN_CODEX),
    )


def report_gate(**overrides):
    data = {
        "status": REPORT_PASS,
        "code": "CODEX_REPORT_PASS",
        "reason": "report passed",
        "report_id": "RPT-001",
        "task_id": "TASK-001",
        "changed_files": ("ai_project_ctl/pipeline/machine_review.py",),
        "generated_files": ("AI_PROJECT/generated/PIPELINE_STATUS.md",),
        "token_usage": {
            "prompt_tokens": 100,
            "context_tokens": 20,
            "remaining_tokens": 1000,
            "token_count_strategy": "local_byte_estimate",
            "token_count_estimated": True,
            "token_count_unavailable": False,
        },
        "checks": (
            {
                "name": "unit",
                "command": "python -m unittest tests.test_pipeline_machine_review",
                "result": "pass",
                "blocking": True,
            },
        ),
    }
    data.update(overrides)
    return ReportGateResult(**data)


def passing_runner(calls):
    def fake_run(argv):
        calls.append(tuple(argv))
        return completed()

    return fake_run


class PipelineMachineReviewTests(unittest.TestCase):
    def test_machine_review_passes_when_all_blocking_checks_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls = []
            result = evaluate_machine_review(
                root=Path(tmp),
                task=task(),
                policy=run_codex_policy(),
                report_gate=report_gate(),
                runner=passing_runner(calls),
                python_executable="python",
            )

            self.assertEqual(result.status, PASS)
            self.assertEqual(result.code, CODE_PASS)
            names = [check.name for check in result.checks]
            self.assertIn("task_validate", names)
            self.assertIn("task_graph_validate", names)
            self.assertIn("protected_file_check", names)
            self.assertIn("report_declared_test_1", names)
            self.assertTrue(calls)

    def test_machine_review_fails_on_blocking_command_failure(self):
        def fake_run(argv):
            if tuple(argv)[-2:] == ("project", "protected-check"):
                return completed(returncode=1, stderr="protected drift\n")
            return completed()

        with tempfile.TemporaryDirectory() as tmp:
            result = evaluate_machine_review(
                root=Path(tmp),
                task=task(),
                policy=run_codex_policy(),
                report_gate=report_gate(),
                runner=fake_run,
                python_executable="python",
            )

            self.assertEqual(result.status, FAIL)
            self.assertEqual(result.code, CODE_COMMAND_FAILED)
            self.assertIn("command_failed", result.reason)

    def test_machine_review_fails_before_commands_when_report_gate_failed(self):
        calls = []
        failed_report = report_gate(
            status=REPORT_FAIL,
            code=CODE_OUT_OF_SCOPE_FILE,
            reason="Changed file is outside task allowed_files.",
            issues=(ReportGateIssue(CODE_OUT_OF_SCOPE_FILE, "out of scope"),),
        )

        with tempfile.TemporaryDirectory() as tmp:
            result = evaluate_machine_review(
                root=Path(tmp),
                task=task(),
                policy=run_codex_policy(),
                report_gate=failed_report,
                runner=passing_runner(calls),
                python_executable="python",
            )

            self.assertEqual(result.status, FAIL)
            self.assertEqual(result.code, CODE_REPORT_GATE_FAILED)
            self.assertEqual(calls, [])

    def test_machine_review_blocks_reported_protected_state_edits(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = evaluate_machine_review(
                root=Path(tmp),
                task=task(),
                policy=run_codex_policy(),
                report_gate=report_gate(changed_files=("AI_PROJECT/state/tasks.json",)),
                runner=passing_runner([]),
                python_executable="python",
            )

            self.assertEqual(result.status, FAIL)
            self.assertEqual(result.code, CODE_PROTECTED_FILE_REPORTED)

    def test_unsafe_report_declared_command_is_warning_not_pass(self):
        unsafe = report_gate(
            checks=(
                {
                    "name": "bad",
                    "command": "rm -rf /tmp/example",
                    "result": "pass",
                    "blocking": True,
                },
            )
        )

        with tempfile.TemporaryDirectory() as tmp:
            result = evaluate_machine_review(
                root=Path(tmp),
                task=task(),
                policy=run_codex_policy(),
                report_gate=unsafe,
                runner=passing_runner([]),
                python_executable="python",
            )

            self.assertEqual(result.status, WARN)
            self.assertIn("test_command_skipped_as_unsafe", result.reason)


if __name__ == "__main__":
    unittest.main()

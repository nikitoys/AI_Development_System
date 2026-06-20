import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ai_project_ctl.pipeline import CodexExecutionMode, policy_preset
from ai_project_ctl.pipeline.report_gate import (
    CODE_BLOCKERS_PRESENT,
    CODE_INVALID_SCHEMA,
    CODE_OUT_OF_SCOPE_FILE,
    CODE_PASS,
    CODE_REPORT_MISSING,
    CODE_TASK_MISMATCH,
    CODE_TOKEN_USAGE_REQUIRED,
    FAIL,
    PASS,
    evaluate_report_gate,
)


def task():
    return {
        "id": "TASK-001",
        "ref": "APP-01",
        "uid": "uid_task_001",
        "legacy_id": "TASK-001",
        "aliases": ["TASK-001"],
        "allowed_files": [
            "ai_project_ctl/pipeline/report_gate.py",
            "tests/**",
        ],
    }


def run_codex_policy():
    supervised = policy_preset("supervised")
    return replace(
        supervised,
        codex=replace(supervised.codex, mode=CodexExecutionMode.RUN_CODEX),
    )


def valid_report(**overrides):
    report = {
        "schema_version": 1,
        "task_id": "TASK-001",
        "task_ref": "APP-01",
        "reported_task_id": "TASK-001",
        "reported_task_ref": "APP-01",
        "implementation_summary": "Implemented report gate.",
        "changed_files": ["ai_project_ctl/pipeline/report_gate.py"],
        "generated_files": ["AI_PROJECT/generated/PIPELINE_STATUS.md"],
        "checks": [
            {
                "name": "unit",
                "command": "python -m unittest tests.test_pipeline_report_gate",
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
    report.update(overrides)
    return report


def write_report_state(root: Path, report, *, report_id="RPT-001", task_id="TASK-001"):
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
                        "task_ref": "APP-01",
                        "submitted_at": "2026-06-19T00:00:00Z",
                        "submitted_by": "tester",
                        "source_file": "/tmp/report.json",
                        "report": report,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


class PipelineReportGateTests(unittest.TestCase):
    def test_missing_report_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = evaluate_report_gate(
                root=Path(tmp),
                task=task(),
                policy=run_codex_policy(),
            )

            self.assertEqual(result.status, FAIL)
            self.assertEqual(result.code, CODE_REPORT_MISSING)

    def test_invalid_schema_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = valid_report()
            del report["implementation_summary"]
            write_report_state(root, report)

            result = evaluate_report_gate(
                root=root,
                task=task(),
                policy=run_codex_policy(),
            )

            self.assertEqual(result.status, FAIL)
            self.assertEqual(result.code, CODE_INVALID_SCHEMA)

    def test_mismatched_task_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_report_state(root, valid_report(task_id="TASK-999"))

            result = evaluate_report_gate(
                root=root,
                task=task(),
                policy=run_codex_policy(),
            )

            self.assertEqual(result.status, FAIL)
            self.assertEqual(result.code, CODE_TASK_MISMATCH)

    def test_blockers_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_report_state(root, valid_report(blockers=["Manual blocker."]))

            result = evaluate_report_gate(
                root=root,
                task=task(),
                policy=run_codex_policy(),
            )

            self.assertEqual(result.status, FAIL)
            self.assertEqual(result.code, CODE_BLOCKERS_PRESENT)

    def test_missing_token_usage_fails_when_policy_requires_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = valid_report()
            del report["token_usage"]
            write_report_state(root, report)

            result = evaluate_report_gate(
                root=root,
                task=task(),
                policy=run_codex_policy(),
            )

            self.assertEqual(result.status, FAIL)
            self.assertEqual(result.code, CODE_TOKEN_USAGE_REQUIRED)

    def test_out_of_scope_changed_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_report_state(root, valid_report(changed_files=["scripts/taskctl.py"]))

            result = evaluate_report_gate(
                root=root,
                task=task(),
                policy=run_codex_policy(),
            )

            self.assertEqual(result.status, FAIL)
            self.assertEqual(result.code, CODE_OUT_OF_SCOPE_FILE)

    def test_valid_report_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_report_state(root, valid_report())

            result = evaluate_report_gate(
                root=root,
                task=task(),
                policy=run_codex_policy(),
            )

            self.assertEqual(result.status, PASS)
            self.assertEqual(result.code, CODE_PASS)
            self.assertEqual(result.report_id, "RPT-001")


if __name__ == "__main__":
    unittest.main()

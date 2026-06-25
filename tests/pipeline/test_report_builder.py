import json
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline.report_builder import build_task_report_payload
from ai_project_ctl.task_reports import REPORT_CHECK_RESULTS, submit_task_report


def task():
    return {
        "id": "TASK-167",
        "uid": "tsk_8af8c1dfb7bc",
        "ref": "PIPEF-86",
        "legacy_id": "TASK-167",
        "aliases": ["TASK-167"],
    }


def summary(**overrides):
    payload = {
        "implementation_summary": "Implemented evidence-based report building.",
        "notes": ["Builder used trusted pipeline evidence."],
        "warnings": [],
        "blockers": [],
    }
    payload.update(overrides)
    return payload


def adapter(**overrides):
    payload = {
        "status": "passed",
        "code": "CODE_LOCAL_COMMAND_PASSED",
        "reason": "local_command_completed_with_report",
        "command_ref": "codex exec",
        "duration_sec": 1.25,
    }
    payload.update(overrides)
    return payload


def submit_payload(root: Path, payload: dict):
    task_state = {"tasks": [task()]}
    return submit_task_report(
        root=root,
        tasks_state=task_state,
        task=task(),
        report_payload=payload,
        source_file=root / "report.json",
        actor="tester",
    )


class PipelineReportBuilderTests(unittest.TestCase):
    def test_successful_adapter_result_builds_valid_task_report_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            payload = build_task_report_payload(
                session={"id": "PSESS-001"},
                task=task(),
                adapter_result=adapter(),
                summary=summary(
                    task_id="MALICIOUS",
                    changed_files=["outside-scope.py"],
                    token_usage={"prompt_tokens": -1},
                ),
                policy_evidence={
                    "changed_files": ["ai_project_ctl/pipeline/report_builder.py"],
                    "checks": [
                        {
                            "name": "unit",
                            "command": "python -m unittest tests.pipeline.test_report_builder",
                            "result": "passed",
                            "duration_sec": 0.5,
                            "blocking": True,
                        }
                    ],
                    "token_usage": {
                        "prompt_tokens": 12,
                        "context_tokens": 34,
                        "token_count_strategy": "test_fixture",
                        "token_count_estimated": True,
                    },
                },
            )

            result = submit_payload(root, payload)
            state = json.loads(
                (root / "AI_PROJECT" / "state" / "task_reports.json").read_text(
                    encoding="utf-8"
                )
            )
            report = state["reports"][0]["report"]

            self.assertEqual(result.report_id, "RPT-001")
            self.assertEqual(payload["task_id"], "TASK-167")
            self.assertEqual(payload["task_ref"], "PIPEF-86")
            self.assertEqual(report["reported_task_id"], "TASK-167")
            self.assertEqual(report["reported_task_ref"], "PIPEF-86")
            self.assertEqual(
                payload["changed_files"],
                ["ai_project_ctl/pipeline/report_builder.py"],
            )
            self.assertEqual(payload["token_usage"]["prompt_tokens"], 12)
            self.assertNotIn("MALICIOUS", json.dumps(payload))
            self.assertNotIn("outside-scope.py", payload["changed_files"])

    def test_uses_task_identity_when_summary_omits_identity_fields(self):
        payload = build_task_report_payload(
            session={},
            task=task(),
            adapter_result=adapter(),
            summary=summary(),
            policy_evidence={},
        )

        self.assertEqual(payload["task_id"], "TASK-167")
        self.assertEqual(payload["task_ref"], "PIPEF-86")
        self.assertEqual(
            payload["implementation_summary"],
            "Implemented evidence-based report building.",
        )

    def test_normalizes_not_run_and_blocked_check_results_to_allowed_values(self):
        payload = build_task_report_payload(
            session={},
            task=task(),
            adapter_result=adapter(status="not_run"),
            summary=summary(),
            policy_evidence={
                "checks": [
                    {
                        "name": "project_tests",
                        "result": "not_run",
                        "blocking": True,
                    }
                ],
                "token_budget_gate": {
                    "status": "blocked",
                    "reason": "token evidence unavailable",
                },
            },
        )

        results = [check["result"] for check in payload["checks"]]
        self.assertNotIn("not_run", results)
        for result in results:
            self.assertIn(result, REPORT_CHECK_RESULTS)

    def test_defaults_token_usage_to_allowed_object_when_precise_evidence_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            payload = build_task_report_payload(
                session={},
                task=task(),
                adapter_result=adapter(),
                summary=summary(),
                policy_evidence={
                    "token_budget": {
                        "max_context_tokens": 24000,
                        "reserved_output_tokens": 1000,
                        "min_remaining_tokens": 6000,
                    }
                },
            )

            submit_payload(root, payload)
            token_usage = payload["token_usage"]

            self.assertEqual(token_usage["prompt_tokens"], 0)
            self.assertEqual(token_usage["context_tokens"], 0)
            self.assertEqual(token_usage["max_context_tokens"], 24000)
            self.assertEqual(token_usage["reserved_output_tokens"], 1000)
            self.assertEqual(token_usage["min_remaining_tokens"], 6000)
            self.assertEqual(
                token_usage["token_count_strategy"],
                "pipeline_report_builder_default",
            )
            self.assertTrue(token_usage["token_count_estimated"])


if __name__ == "__main__":
    unittest.main()

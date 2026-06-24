import json
import unittest

from ai_project_ctl.pipeline.codex_report_parser import (
    CODEX_REPORT_BLOCK_DUPLICATE,
    CODEX_REPORT_BLOCK_MISSING,
    CODEX_REPORT_FIELDS_MISSING,
    CODEX_REPORT_JSON_MALFORMED,
    CODEX_REPORT_JSON_NOT_OBJECT,
    CODEX_REPORT_PARSE_OK,
    parse_codex_report_stdout,
)


def report_payload(**overrides):
    payload = {
        "schema_version": 1,
        "task_id": "TASK-152",
        "task_ref": "PIPEF-73",
        "implementation_summary": "Implemented the parser.",
        "changed_files": ["ai_project_ctl/pipeline/codex_report_parser.py"],
        "generated_files": [],
        "checks": [
            {
                "name": "unit",
                "command": "python -m unittest tests.pipeline.test_codex_report_parser",
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
            "token_count_strategy": "estimated",
            "token_count_estimated": True,
            "token_count_unavailable": False,
            "token_count_unavailable_reason": "",
        },
    }
    payload.update(overrides)
    return payload


def stdout_for(payload):
    return "human-readable text before the report\nCODEX_REPORT_JSON:\n```json\n{}\n```\n".format(
        json.dumps(payload, indent=2, sort_keys=True)
    )


class CodexReportParserTests(unittest.TestCase):
    def test_extracts_valid_fenced_report_json_object(self):
        payload = report_payload()

        result = parse_codex_report_stdout(stdout_for(payload))

        self.assertTrue(result.ok)
        self.assertEqual(result.code, CODEX_REPORT_PARSE_OK)
        self.assertEqual(dict(result.report or {}), payload)
        self.assertIsNone(result.issue)

    def test_missing_report_block_returns_stable_parse_result(self):
        result = parse_codex_report_stdout("ordinary stdout without structured report")

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODEX_REPORT_BLOCK_MISSING)
        self.assertEqual(result.issue.code, CODEX_REPORT_BLOCK_MISSING)
        self.assertIsNone(result.report)

    def test_duplicate_report_blocks_are_rejected(self):
        payload = report_payload()
        stdout = stdout_for(payload) + "\n" + stdout_for(payload)

        result = parse_codex_report_stdout(stdout)

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODEX_REPORT_BLOCK_DUPLICATE)
        self.assertEqual(result.issue.details["marker_count"], 2)

    def test_malformed_json_is_rejected_with_stable_error_code(self):
        stdout = "CODEX_REPORT_JSON:\n```json\n{\"task_id\": \n```\n"

        result = parse_codex_report_stdout(stdout)

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODEX_REPORT_JSON_MALFORMED)
        self.assertEqual(result.issue.code, CODEX_REPORT_JSON_MALFORMED)
        self.assertIn("line", result.issue.details)
        self.assertIn("column", result.issue.details)

    def test_non_object_json_is_rejected(self):
        result = parse_codex_report_stdout("CODEX_REPORT_JSON:\n```json\n[]\n```\n")

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODEX_REPORT_JSON_NOT_OBJECT)
        self.assertEqual(result.issue.details["value_type"], "list")

    def test_missing_top_level_report_fields_are_rejected(self):
        payload = report_payload()
        payload.pop("token_usage")

        result = parse_codex_report_stdout(stdout_for(payload))

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODEX_REPORT_FIELDS_MISSING)
        self.assertEqual(result.issue.details["missing"], ["token_usage"])


if __name__ == "__main__":
    unittest.main()

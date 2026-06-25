import json
import unittest

from ai_project_ctl.pipeline.codex_summary_parser import (
    CODEX_SUMMARY_BLOCK_MISSING,
    CODEX_SUMMARY_FIELDS_MISSING,
    CODEX_SUMMARY_FIELDS_UNKNOWN,
    CODEX_SUMMARY_JSON_MALFORMED,
    CODEX_SUMMARY_PARSE_OK,
    parse_codex_summary_stdout,
)


def summary_payload(**overrides):
    payload = {
        "implementation_summary": "Implemented the selected task.",
        "notes": ["No follow-up required."],
        "warnings": [],
        "blockers": [],
    }
    payload.update(overrides)
    return payload


def stdout_for(payload):
    return (
        "human-readable text before the summary\n"
        "CODEX_EXECUTION_SUMMARY_JSON:\n"
        "```json\n{}\n```\n"
    ).format(json.dumps(payload, indent=2, sort_keys=True))


class CodexSummaryParserTests(unittest.TestCase):
    def test_extracts_valid_fenced_summary_json_object(self):
        payload = summary_payload()

        result = parse_codex_summary_stdout(stdout_for(payload))

        self.assertTrue(result.ok)
        self.assertEqual(result.code, CODEX_SUMMARY_PARSE_OK)
        self.assertEqual(dict(result.summary or {}), payload)
        self.assertIsNone(result.issue)

    def test_missing_summary_block_returns_stable_parse_result(self):
        result = parse_codex_summary_stdout("ordinary stdout without structured summary")

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODEX_SUMMARY_BLOCK_MISSING)
        self.assertEqual(result.issue.code, CODEX_SUMMARY_BLOCK_MISSING)
        self.assertIsNone(result.summary)

    def test_malformed_json_is_rejected_with_stable_error_code(self):
        stdout = "CODEX_EXECUTION_SUMMARY_JSON:\n```json\n{\"notes\": \n```\n"

        result = parse_codex_summary_stdout(stdout)

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODEX_SUMMARY_JSON_MALFORMED)
        self.assertEqual(result.issue.code, CODEX_SUMMARY_JSON_MALFORMED)
        self.assertIn("line", result.issue.details)
        self.assertIn("column", result.issue.details)

    def test_missing_top_level_summary_fields_are_rejected(self):
        payload = summary_payload()
        payload.pop("blockers")

        result = parse_codex_summary_stdout(stdout_for(payload))

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODEX_SUMMARY_FIELDS_MISSING)
        self.assertEqual(result.issue.details["missing"], ["blockers"])

    def test_unknown_top_level_summary_fields_are_rejected(self):
        payload = summary_payload(task_id="TASK-166", changed_files=[], token_usage={})

        result = parse_codex_summary_stdout(stdout_for(payload))

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODEX_SUMMARY_FIELDS_UNKNOWN)
        self.assertEqual(
            result.issue.details["unknown"],
            ["changed_files", "task_id", "token_usage"],
        )


if __name__ == "__main__":
    unittest.main()

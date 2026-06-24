import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEXCTL_PATH = ROOT / "scripts" / "codexctl.py"


def load_codexctl():
    spec = importlib.util.spec_from_file_location("codexctl_report_contract", CODEXCTL_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


codexctl = load_codexctl()


def rendered_task_prompt():
    task = {
        "id": "TASK-151",
        "ref": "PIPEF-72",
        "status": "in_progress",
        "title": "Structured report contract",
        "summary": "Update Codex prompt generation with a structured report contract.",
        "scope": ["Replace the plain bullet-only Final Report section."],
        "out_of_scope": ["Do not implement stdout parsing."],
        "allowed_files": [
            "scripts/codexctl.py",
            "tests/test_codex_prompt_report_contract.py",
        ],
        "acceptance_criteria": [
            "Generated CODEX_PROMPT.md contains a clearly delimited machine-readable report JSON instruction.",
            "The prompt still tells Codex not to self-approve.",
        ],
        "verification_mode": "strict",
    }
    return codexctl.render_prompt(codexctl.task_prompt_model(task))


def extract_report_contract(prompt):
    marker = "CODEX_REPORT_JSON:"
    _, marker_tail = prompt.split(marker, 1)
    block = marker_tail.strip()
    assert block.startswith("```json\n")
    assert block.endswith("```")
    return json.loads(block[len("```json\n") : -len("```")].strip())


class CodexPromptReportContractTests(unittest.TestCase):
    def test_final_report_contract_is_machine_readable_json(self):
        prompt = rendered_task_prompt()

        self.assertIn("## Final Report", prompt)
        self.assertIn("CODEX_REPORT_JSON:", prompt)
        self.assertRegex(prompt, r"CODEX_REPORT_JSON:\n```json\n\{")
        self.assertTrue(prompt.rstrip().endswith("```"))
        self.assertNotIn("- Summary:\n- Changed files:", prompt)

        report = extract_report_contract(prompt)
        self.assertEqual(
            set(report),
            {
                "schema_version",
                "task_id",
                "task_ref",
                "implementation_summary",
                "changed_files",
                "generated_files",
                "checks",
                "warnings",
                "blockers",
                "notes",
                "owner_decision_required",
                "token_usage",
            },
        )
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["task_id"], "TASK-151")
        self.assertEqual(report["task_ref"], "PIPEF-72")
        for field in ["changed_files", "generated_files", "checks", "warnings", "blockers", "notes"]:
            self.assertIsInstance(report[field], list)
        self.assertIsInstance(report["owner_decision_required"], bool)

        token_usage = report["token_usage"]
        self.assertIn("prompt_tokens", token_usage)
        self.assertIn("context_tokens", token_usage)
        self.assertIn("token_count_strategy", token_usage)
        self.assertIn("token_count_estimated", token_usage)

    def test_existing_prompt_sections_and_self_approval_warning_remain(self):
        prompt = rendered_task_prompt()

        self.assertIn("You are Codex Executor. Execute one bounded task. Do not self-approve.", prompt)
        self.assertIn("## Scope\n\n- Replace the plain bullet-only Final Report section.", prompt)
        self.assertIn("## Allowed Files\n\nEditable:", prompt)
        self.assertIn("- scripts/codexctl.py", prompt)
        self.assertIn("- tests/test_codex_prompt_report_contract.py", prompt)
        self.assertIn("## Acceptance Criteria", prompt)
        self.assertIn(
            "- Generated CODEX_PROMPT.md contains a clearly delimited machine-readable report JSON instruction.",
            prompt,
        )


if __name__ == "__main__":
    unittest.main()

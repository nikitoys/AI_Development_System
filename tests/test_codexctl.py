import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEXCTL_PATH = ROOT / "scripts" / "codexctl.py"


def load_codexctl():
    spec = importlib.util.spec_from_file_location("codexctl_summary_contract", CODEXCTL_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


codexctl = load_codexctl()


def rendered_task_prompt():
    task = {
        "id": "TASK-166",
        "ref": "PIPEF-85",
        "status": "in_progress",
        "title": "Add Codex execution summary block contract",
        "summary": "Introduce a minimal Codex execution summary block.",
        "scope": ["Define a compact AI execution summary JSON block contract."],
        "out_of_scope": ["Do not build or submit TaskReport payloads."],
        "allowed_files": [
            "scripts/codexctl.py",
            "ai_project_ctl/pipeline/codex_summary_parser.py",
            "tests/pipeline/test_codex_summary_parser.py",
            "tests/test_codexctl.py",
        ],
        "acceptance_criteria": [
            "Codex prompt output asks for a minimal execution summary block rather than a full structured TaskReport.",
        ],
        "verification_mode": "strict",
    }
    return codexctl.render_prompt(codexctl.task_prompt_model(task))


def extract_summary_contract(prompt):
    marker = "CODEX_EXECUTION_SUMMARY_JSON:"
    _, marker_tail = prompt.split(marker, 1)
    block = marker_tail.strip()
    assert block.startswith("```json\n")
    assert block.endswith("```")
    return json.loads(block[len("```json\n") : -len("```")].strip())


class CodexPromptSummaryContractTests(unittest.TestCase):
    def test_final_contract_is_minimal_execution_summary_json(self):
        prompt = rendered_task_prompt()

        self.assertIn("## Execution Summary", prompt)
        self.assertIn("CODEX_EXECUTION_SUMMARY_JSON:", prompt)
        self.assertNotIn("CODEX_REPORT_JSON:", prompt)
        self.assertIn("Do not emit a full TaskReport payload.", prompt)
        self.assertRegex(prompt, r"CODEX_EXECUTION_SUMMARY_JSON:\n```json\n\{")
        self.assertTrue(prompt.rstrip().endswith("```"))

        summary = extract_summary_contract(prompt)
        self.assertEqual(
            set(summary),
            {
                "implementation_summary",
                "notes",
                "warnings",
                "blockers",
            },
        )
        self.assertNotIn("task_id", summary)
        self.assertNotIn("changed_files", summary)
        self.assertNotIn("checks", summary)
        self.assertNotIn("token_usage", summary)
        for field in ["notes", "warnings", "blockers"]:
            self.assertIsInstance(summary[field], list)

    def test_existing_prompt_sections_and_self_approval_warning_remain(self):
        prompt = rendered_task_prompt()

        self.assertIn("You are Codex Executor. Execute one bounded task. Do not self-approve.", prompt)
        self.assertIn(
            "## Scope\n\n- Define a compact AI execution summary JSON block contract.",
            prompt,
        )
        self.assertIn("## Allowed Files\n\nEditable:", prompt)
        self.assertIn("- scripts/codexctl.py", prompt)
        self.assertIn("- tests/test_codexctl.py", prompt)
        self.assertIn("## Acceptance Criteria", prompt)


if __name__ == "__main__":
    unittest.main()

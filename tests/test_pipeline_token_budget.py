import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline.policy import TokenBudgetPolicy
from ai_project_ctl.pipeline.token_budget import (
    CODE_CONTEXT_REQUIRES_COMPACT_SPLIT,
    CODE_LOW_REMAINING,
    CODE_PASS,
    CODE_PROMPT_TOO_LARGE,
    CODE_TOKEN_COUNT_UNAVAILABLE,
    TokenCount,
    evaluate_token_budget,
)


class UnavailableCounter:
    def count(self, text: str) -> TokenCount:
        return TokenCount(
            tokens=None,
            strategy="test_unavailable",
            estimated=False,
            unavailable_reason="test counter unavailable",
        )


class PipelineTokenBudgetTests(unittest.TestCase):
    def test_gate_passes_for_prompt_with_remaining_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prompt(root, "Short prompt payload.")

            result = evaluate_token_budget(
                root=root,
                policy=TokenBudgetPolicy(
                    require_gate_pass=True,
                    max_prompt_tokens=100,
                    max_context_tokens=100,
                    min_remaining_tokens=10,
                    reserved_output_tokens=5,
                ),
            )

            self.assertTrue(result.ok)
            self.assertEqual(result.status, "pass")
            self.assertEqual(result.code, CODE_PASS)
            self.assertGreater(result.prompt_bytes, 0)
            self.assertIsNotNone(result.prompt_tokens)
            self.assertGreaterEqual(result.remaining_tokens, 10)

    def test_gate_fails_when_prompt_does_not_fit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prompt(root, "x" * 120)

            result = evaluate_token_budget(
                root=root,
                policy=TokenBudgetPolicy(
                    require_gate_pass=True,
                    max_prompt_tokens=20,
                    max_context_tokens=20,
                    min_remaining_tokens=0,
                ),
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.status, "fail")
            self.assertEqual(result.code, CODE_PROMPT_TOO_LARGE)
            self.assertEqual(result.reason, "prompt_does_not_fit")

    def test_gate_fails_when_remaining_tokens_are_below_threshold(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prompt(root, "x" * 80)

            result = evaluate_token_budget(
                root=root,
                policy=TokenBudgetPolicy(
                    require_gate_pass=True,
                    max_prompt_tokens=40,
                    max_context_tokens=40,
                    min_remaining_tokens=25,
                ),
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.code, CODE_LOW_REMAINING)
            self.assertEqual(result.reason, "remaining_tokens_below_threshold")
            self.assertLess(result.remaining_tokens, result.min_remaining_tokens)

    def test_gate_fails_when_counter_is_unavailable_in_strict_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prompt(root, "Short prompt payload.")

            result = evaluate_token_budget(
                root=root,
                policy=TokenBudgetPolicy(require_gate_pass=True),
                token_counter=UnavailableCounter(),
                strict=True,
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.code, CODE_TOKEN_COUNT_UNAVAILABLE)
            self.assertTrue(result.token_count_unavailable)
            self.assertEqual(
                result.token_count_unavailable_reason,
                "test counter unavailable",
            )

    def test_gate_blocks_when_context_requires_compact_or_split(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prompt(
                root,
                "\n".join(
                    [
                        "[SYSTEM]",
                        "",
                        "Retrieved Context Pack Content:",
                        "````text",
                        "x" * 120,
                        "````",
                        "",
                        "Acceptance Criteria:",
                        "- Gate blocks.",
                    ]
                ),
            )

            result = evaluate_token_budget(
                root=root,
                policy=TokenBudgetPolicy(
                    require_gate_pass=True,
                    max_prompt_tokens=100,
                    max_context_tokens=5,
                    min_remaining_tokens=0,
                ),
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.code, CODE_CONTEXT_REQUIRES_COMPACT_SPLIT)
            self.assertTrue(result.context_requires_compact_or_split)
            self.assertIn(
                "context_tokens_exceed_threshold",
                result.context_requirement_reasons,
            )


def write_prompt(root: Path, text: str) -> Path:
    path = root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


if __name__ == "__main__":
    unittest.main()

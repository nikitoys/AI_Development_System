import subprocess
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from ai_project_ctl.pipeline.git_diff_gate import (
    BLOCKED,
    CODE_ALLOWED_FILES_OUT_OF_SCOPE,
    CODE_DIFF_MISMATCH,
    CODE_PASS,
    CODE_PROTECTED_FILES_BLOCKED,
    PASS,
    REASON_PROTECTED_EVENT_CHANGED,
    REASON_PROTECTED_STATE_CHANGED,
    REASON_REPORTED_PROTECTED_EVENT_CHANGED,
    REASON_REPORTED_PROTECTED_STATE_CHANGED,
    REASON_UNGOVERNED_GENERATED_CHANGED,
    evaluate_allowed_files_gate,
    evaluate_git_diff_gate,
    evaluate_protected_files_gate,
)
from ai_project_ctl.pipeline.verify_phase import _report_git_diff_comparison


@dataclass(frozen=True)
class _Report:
    changed_files: tuple[str, ...] = ()
    generated_files: tuple[str, ...] = ()


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args),
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def _init_repo(root: Path) -> None:
    _git(root, "init")
    _git(root, "config", "user.email", "codex-test@example.invalid")
    _git(root, "config", "user.name", "Codex Test")
    (root / "tracked.txt").write_text("initial\n", encoding="utf-8")
    _git(root, "add", "tracked.txt")
    _git(root, "commit", "-m", "initial")


class GitDiffGateActualWorkingTreeTests(unittest.TestCase):
    def test_clean_working_tree_passes_with_empty_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo(root)

            result = evaluate_git_diff_gate(root=root)

            self.assertEqual(result.status, PASS)
            self.assertEqual(result.code, CODE_PASS)
            self.assertEqual(result.reason, "working_tree_clean")
            self.assertEqual(result.changed_files, ())
            self.assertEqual(result.tracked_files, ())
            self.assertEqual(result.untracked_files, ())

    def test_reported_tracked_file_matches_actual_diff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo(root)
            (root / "tracked.txt").write_text("changed\n", encoding="utf-8")

            result = evaluate_git_diff_gate(
                root=root,
                expected_files=("tracked.txt",),
            )

            self.assertEqual(result.status, PASS)
            self.assertEqual(result.code, CODE_PASS)
            self.assertEqual(result.changed_files, ("tracked.txt",))
            self.assertEqual(result.tracked_files, ("tracked.txt",))
            self.assertEqual(result.unstaged_files, ("tracked.txt",))
            self.assertEqual(result.untracked_files, ())

    def test_reported_untracked_file_matches_actual_diff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo(root)
            (root / "new-file.txt").write_text("new\n", encoding="utf-8")

            result = evaluate_git_diff_gate(
                root=root,
                expected_files=("new-file.txt",),
            )

            self.assertEqual(result.status, PASS)
            self.assertEqual(result.code, CODE_PASS)
            self.assertEqual(result.changed_files, ("new-file.txt",))
            self.assertEqual(result.tracked_files, ())
            self.assertEqual(result.untracked_files, ("new-file.txt",))

    def test_actual_diff_missing_from_report_blocks_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo(root)
            (root / "tracked.txt").write_text("changed\n", encoding="utf-8")

            result = evaluate_git_diff_gate(root=root, expected_files=())
            comparison = _report_git_diff_comparison(_Report(), result)

            self.assertEqual(result.status, BLOCKED)
            self.assertEqual(result.code, CODE_DIFF_MISMATCH)
            self.assertEqual(result.unexpected_files, ("tracked.txt",))
            self.assertEqual(result.missing_files, ())
            self.assertEqual(comparison["status"], "blocked")
            self.assertEqual(comparison["missing_from_report"], ["tracked.txt"])
            self.assertEqual(comparison["extra_in_report"], [])


class GitDiffGateScopeTests(unittest.TestCase):
    def test_allowed_files_gate_blocks_out_of_scope_actual_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = evaluate_allowed_files_gate(
                root=root,
                changed_files=("tests/allowed_test.py", "src/out_of_scope.py"),
                allowed_files=("tests/allowed_test.py",),
            )

            self.assertEqual(result.status, BLOCKED)
            self.assertEqual(result.code, CODE_ALLOWED_FILES_OUT_OF_SCOPE)
            self.assertEqual(result.allowed_files, ("tests/allowed_test.py",))
            self.assertEqual(result.out_of_scope_files, ("src/out_of_scope.py",))

    def test_protected_files_gate_blocks_stable_reason_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = evaluate_protected_files_gate(
                root=root,
                changed_files=(
                    "AI_PROJECT/state/manual.json",
                    "AI_PROJECT/events/manual-events.jsonl",
                    "AI_PROJECT/generated/manual.md",
                    "AI_PROJECT/state/tasks.json",
                    "AI_PROJECT/events/task-events.jsonl",
                ),
                reported_changed_files=(
                    "AI_PROJECT/state/tasks.json",
                    "AI_PROJECT/events/task-events.jsonl",
                ),
            )

            reason_codes = {
                violation.path: violation.reason_code
                for violation in result.violations
            }
            self.assertEqual(result.status, BLOCKED)
            self.assertEqual(result.code, CODE_PROTECTED_FILES_BLOCKED)
            self.assertEqual(
                reason_codes,
                {
                    "AI_PROJECT/events/manual-events.jsonl": (
                        REASON_PROTECTED_EVENT_CHANGED
                    ),
                    "AI_PROJECT/events/task-events.jsonl": (
                        REASON_REPORTED_PROTECTED_EVENT_CHANGED
                    ),
                    "AI_PROJECT/generated/manual.md": (
                        REASON_UNGOVERNED_GENERATED_CHANGED
                    ),
                    "AI_PROJECT/state/manual.json": (
                        REASON_PROTECTED_STATE_CHANGED
                    ),
                    "AI_PROJECT/state/tasks.json": (
                        REASON_REPORTED_PROTECTED_STATE_CHANGED
                    ),
                },
            )


if __name__ == "__main__":
    unittest.main()

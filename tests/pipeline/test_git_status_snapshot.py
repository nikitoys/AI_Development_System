import subprocess
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline.git_status import (
    GIT_STATUS_SHORT_COMMAND,
    capture_git_status_snapshot,
    dirty_paths_after_baseline,
    parse_git_status_snapshot,
)


def completed(stdout: str = "", returncode: int = 0, stderr: str = ""):
    return subprocess.CompletedProcess(
        args=[],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


class GitStatusSnapshotTests(unittest.TestCase):
    def test_parse_modified_untracked_deleted_and_renamed_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stdout = "\n".join(
                (
                    " M ./src/modified.py",
                    "?? tests/new_test.py",
                    " D docs/removed.md",
                    "R  docs/old.md -> docs/renamed.md",
                    "",
                )
            )

            snapshot = parse_git_status_snapshot(stdout, root=root)

        self.assertEqual(
            tuple(entry.to_dict() for entry in snapshot.entries),
            (
                {"status": "M", "path": "src/modified.py"},
                {"status": "??", "path": "tests/new_test.py"},
                {"status": "D", "path": "docs/removed.md"},
                {"status": "R", "path": "docs/renamed.md"},
            ),
        )
        self.assertEqual(
            snapshot.dirty_paths,
            (
                "docs/removed.md",
                "docs/renamed.md",
                "src/modified.py",
                "tests/new_test.py",
            ),
        )

    def test_absolute_paths_are_normalized_relative_to_repo_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stdout = " M {}\n".format(root / "ai_project_ctl/pipeline/git_status.py")

            snapshot = parse_git_status_snapshot(stdout, root=root)

        self.assertEqual(
            snapshot.dirty_paths,
            ("ai_project_ctl/pipeline/git_status.py",),
        )

    def test_dirty_paths_after_baseline_excludes_preexisting_dirty_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = parse_git_status_snapshot(
                "\n".join(
                    (
                        " M preexisting.py",
                        "?? scratch.txt",
                    )
                ),
                root=root,
            )
            current = parse_git_status_snapshot(
                "\n".join(
                    (
                        " M preexisting.py",
                        "?? scratch.txt",
                        " M changed.py",
                        "?? added.py",
                        " D deleted.py",
                        "R  old_name.py -> renamed.py",
                    )
                ),
                root=root,
            )

            changed_after_baseline = dirty_paths_after_baseline(baseline, current)

        self.assertEqual(
            changed_after_baseline,
            ("added.py", "changed.py", "deleted.py", "renamed.py"),
        )

    def test_capture_uses_short_untracked_all_command(self):
        commands = []

        def runner(argv):
            commands.append(tuple(argv))
            return completed(stdout=" M ./changed.py\n")

        with tempfile.TemporaryDirectory() as tmp:
            snapshot = capture_git_status_snapshot(root=Path(tmp), runner=runner)

        self.assertEqual(commands, [GIT_STATUS_SHORT_COMMAND])
        self.assertEqual(snapshot.dirty_paths, ("changed.py",))


if __name__ == "__main__":
    unittest.main()

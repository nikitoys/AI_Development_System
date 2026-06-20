import subprocess
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline.git_commit import run_git_command


def completed(stdout="", returncode=0, stderr=""):
    return subprocess.CompletedProcess(
        args=[],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


class PipelineGitCommitTests(unittest.TestCase):
    def test_git_command_rejects_forbidden_subcommands_without_runner(self):
        calls = []

        def fake_runner(argv):
            calls.append(list(argv))
            return completed()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for subcommand in ("push", "merge", "reset", "checkout", "rebase", "clean"):
                with self.subTest(subcommand=subcommand):
                    result = run_git_command(
                        ("git", subcommand),
                        root=root,
                        runner=fake_runner,
                    )

                    self.assertFalse(result.ok)
                    self.assertEqual(result.code, "COMMIT_FORBIDDEN_GIT_COMMAND")

        self.assertEqual(calls, [])

    def test_git_add_requires_explicit_paths_after_separator(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run_git_command(
                ("git", "add", "."),
                root=root,
                runner=lambda argv: completed(),
            )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "COMMIT_FORBIDDEN_GIT_COMMAND")


if __name__ == "__main__":
    unittest.main()

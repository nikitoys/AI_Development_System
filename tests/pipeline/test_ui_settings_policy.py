import json
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline import (
    CodexAdapterMode,
    CodexExecutionMode,
    policy_preset,
)
from ai_project_ctl.pipeline.ui_policy import (
    UIPipelinePolicyError,
    resolve_pipeline_policy_from_settings,
    resolve_ui_pipeline_policy,
)
from ai_project_ctl.ui_settings import ui_settings_path


def write_settings(root: Path, payload: dict) -> None:
    path = ui_settings_path(root)
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class UIPipelinePolicyTests(unittest.TestCase):
    def test_missing_settings_file_resolves_default_executable_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            policy = resolve_ui_pipeline_policy(root=Path(tmp))

        self.assertEqual(policy.name, "supervised_executable_local_commit")
        self.assertEqual(policy.codex.mode, CodexExecutionMode.RUN_CODEX)
        self.assertEqual(policy.codex.adapter_mode, CodexAdapterMode.LOCAL_COMMAND)
        self.assertEqual(policy.codex.local_command, ("codex", "exec"))
        self.assertEqual(policy.codex.command_allowlist, ("codex exec",))
        self.assertTrue(policy.validate().ok)

    def test_command_line_replaces_executable_local_command_and_allowlist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_settings(
                root,
                {
                    "default_policy": "supervised_executable_local_commit",
                    "command_line": "codex exec --json",
                },
            )

            policy = resolve_ui_pipeline_policy(root=root)

        self.assertEqual(policy.codex.local_command, ("codex", "exec", "--json"))
        self.assertEqual(policy.codex.command_allowlist, ("codex exec --json",))
        self.assertTrue(policy.validate().ok)

    def test_non_executable_policy_does_not_require_command_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_settings(
                root,
                {
                    "default_policy": "supervised",
                    "command_line": "",
                },
            )

            policy = resolve_ui_pipeline_policy(root=root)

        self.assertEqual(policy.name, "supervised")
        self.assertEqual(policy.codex.mode, CodexExecutionMode.BUILD_PROMPT_ONLY)
        self.assertEqual(policy.codex.local_command, ())
        self.assertTrue(policy.validate().ok)

    def test_unknown_default_policy_fails_with_clear_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_settings(
                root,
                {
                    "default_policy": "reckless",
                    "command_line": "codex exec",
                },
            )

            with self.assertRaises(UIPipelinePolicyError) as raised:
                resolve_ui_pipeline_policy(root=root)

        self.assertEqual(raised.exception.code, "UI_POLICY_DEFAULT_POLICY_UNKNOWN")
        self.assertIn("reckless", raised.exception.message)

    def test_missing_default_policy_fails_with_clear_error(self):
        with self.assertRaises(UIPipelinePolicyError) as raised:
            resolve_pipeline_policy_from_settings({"command_line": "codex exec"})

        self.assertEqual(raised.exception.code, "UI_POLICY_DEFAULT_POLICY_REQUIRED")

    def test_empty_command_line_fails_for_executable_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_settings(
                root,
                {
                    "default_policy": "supervised_executable_local_commit",
                    "command_line": " ",
                },
            )

            with self.assertRaises(UIPipelinePolicyError) as raised:
                resolve_ui_pipeline_policy(root=root)

        self.assertEqual(raised.exception.code, "UI_POLICY_COMMAND_LINE_REQUIRED")

    def test_resolver_does_not_mutate_builtin_policy_presets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_settings(
                root,
                {
                    "default_policy": "supervised_executable_local_commit",
                    "command_line": "codex exec --json",
                },
            )

            resolved = resolve_ui_pipeline_policy(root=root)
            builtin = policy_preset("supervised_executable_local_commit")

        self.assertEqual(resolved.codex.local_command, ("codex", "exec", "--json"))
        self.assertEqual(builtin.codex.local_command, ("codex", "exec"))
        self.assertEqual(builtin.codex.command_allowlist, ("codex exec",))


if __name__ == "__main__":
    unittest.main()

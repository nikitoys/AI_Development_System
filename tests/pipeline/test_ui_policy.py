import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline.policy import policy_behavior_label, policy_preset
from ai_project_ctl.pipeline.ui_policy import resolve_ui_pipeline_policy
from ai_project_ctl.ui_settings import (
    ALLOW_REPORT_WARNINGS_SETTING,
    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
    UISettingsError,
    apply_ui_settings,
    load_ui_settings,
    ui_settings_path,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
AICTL = REPO_ROOT / "scripts" / "aictl.py"


def run_aictl(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(AICTL), "--root", str(root), *args],
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class UIRelaxedGitDiffPolicyTests(unittest.TestCase):
    def test_cli_ui_setting_accepts_relaxed_git_diff_boolean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            enabled_process = run_aictl(
                root,
                "--json",
                "ui",
                "settings",
                "set",
                ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
                "true",
            )
            enabled_payload = json.loads(enabled_process.stdout)
            enabled = load_ui_settings(root=root)
            disabled_process = run_aictl(
                root,
                "--json",
                "ui",
                "settings",
                "set",
                ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
                "0",
            )
            disabled = load_ui_settings(root=root)

        self.assertEqual(enabled_process.returncode, 0, enabled_process.stderr)
        self.assertEqual(disabled_process.returncode, 0, disabled_process.stderr)
        self.assertIs(
            enabled_payload["data"]["settings"][
                ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING
            ],
            True,
        )
        self.assertIs(enabled[ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING], True)
        self.assertIs(disabled[ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING], False)

    def test_apply_ui_settings_accepts_relaxed_git_diff_when_allowlisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            apply_ui_settings(
                {ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING: "true"},
                allowed_keys=(ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,),
                root=root,
            )
            settings = load_ui_settings(root=root)

        self.assertIs(settings[ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING], True)

    def test_cli_ui_setting_accepts_report_warnings_boolean_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            enabled_process = run_aictl(
                root,
                "--json",
                "ui",
                "settings",
                "set",
                ALLOW_REPORT_WARNINGS_SETTING,
                "true",
            )
            enabled_payload = json.loads(enabled_process.stdout)
            enabled = load_ui_settings(root=root)
            disabled_process = run_aictl(
                root,
                "--json",
                "ui",
                "settings",
                "set",
                ALLOW_REPORT_WARNINGS_SETTING,
                "0",
            )
            disabled = load_ui_settings(root=root)

        self.assertEqual(enabled_process.returncode, 0, enabled_process.stderr)
        self.assertEqual(disabled_process.returncode, 0, disabled_process.stderr)
        self.assertIs(
            enabled_payload["data"]["settings"][ALLOW_REPORT_WARNINGS_SETTING],
            True,
        )
        self.assertIs(enabled[ALLOW_REPORT_WARNINGS_SETTING], True)
        self.assertIs(disabled[ALLOW_REPORT_WARNINGS_SETTING], False)

    def test_apply_ui_settings_accepts_report_warnings_boolean_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            apply_ui_settings(
                {ALLOW_REPORT_WARNINGS_SETTING: True},
                allowed_keys=(ALLOW_REPORT_WARNINGS_SETTING,),
                root=root,
            )
            enabled = load_ui_settings(root=root)

            apply_ui_settings(
                {ALLOW_REPORT_WARNINGS_SETTING: "0"},
                allowed_keys=(ALLOW_REPORT_WARNINGS_SETTING,),
                root=root,
            )
            disabled = load_ui_settings(root=root)

        self.assertIs(enabled[ALLOW_REPORT_WARNINGS_SETTING], True)
        self.assertIs(disabled[ALLOW_REPORT_WARNINGS_SETTING], False)

    def test_invalid_report_warnings_value_uses_ui_boolean_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = ui_settings_path(root)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps({ALLOW_REPORT_WARNINGS_SETTING: "maybe"}),
                encoding="utf-8",
            )

            with self.assertRaises(UISettingsError) as raised:
                load_ui_settings(root=root)

        self.assertEqual(raised.exception.code, "UI_SETTINGS_BOOLEAN_INVALID")
        self.assertEqual(raised.exception.path, ALLOW_REPORT_WARNINGS_SETTING)
        self.assertIn("true, false, 1, 0", raised.exception.message)

    def test_default_ui_policy_keeps_strict_git_diff_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            settings = load_ui_settings(root=root)
            policy = resolve_ui_pipeline_policy(root=root)

        self.assertIs(settings[ALLOW_REPORT_WARNINGS_SETTING], False)
        self.assertTrue(policy.verify.run_git_diff_gates)
        self.assertTrue(policy.verify.block_report_warnings)
        self.assertFalse(policy.verify.allow_report_warnings)
        self.assertNotIn("verify", policy.to_dict())
        self.assertNotIn("relaxed-verify", policy_behavior_label(policy))
        self.assertNotIn("report-warnings-allowed", policy_behavior_label(policy))
        self.assertNotIn("report-warnings-advisory", policy_behavior_label(policy))

    def test_relaxed_ui_setting_updates_effective_policy_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            apply_ui_settings(
                {
                    "command_line": "codex exec",
                    "default_policy": "supervised_executable_local_commit",
                    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING: "true",
                },
                allowed_keys=(
                    "command_line",
                    "default_policy",
                    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
                ),
                root=root,
            )

            policy = resolve_ui_pipeline_policy(root=root)

        self.assertFalse(policy.verify.run_git_diff_gates)
        self.assertFalse(policy.verify.allow_report_warnings)
        self.assertTrue(policy.verify.block_report_warnings)
        self.assertEqual(policy.to_dict()["verify"], {"run_git_diff_gates": False})
        self.assertIn("relaxed-verify", policy_behavior_label(policy))
        self.assertNotIn("report-warnings-allowed", policy_behavior_label(policy))
        self.assertNotIn("report-warnings-advisory", policy_behavior_label(policy))

    def test_report_warnings_updates_effective_policy_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            apply_ui_settings(
                {
                    "command_line": "codex exec",
                    "default_policy": "supervised_executable_local_commit",
                    ALLOW_REPORT_WARNINGS_SETTING: "true",
                },
                allowed_keys=(
                    "command_line",
                    "default_policy",
                    ALLOW_REPORT_WARNINGS_SETTING,
                ),
                root=root,
            )

            policy = resolve_ui_pipeline_policy(root=root)

        self.assertTrue(policy.verify.run_git_diff_gates)
        self.assertTrue(policy.verify.block_report_warnings)
        self.assertTrue(policy.verify.allow_report_warnings)
        self.assertEqual(policy.to_dict()["verify"], {"allow_report_warnings": True})
        self.assertNotIn("relaxed-verify", policy_behavior_label(policy))
        self.assertIn("report-warnings-allowed", policy_behavior_label(policy))
        self.assertNotIn("report-warnings-advisory", policy_behavior_label(policy))

    def test_combined_relaxed_settings_preserve_both_verify_overrides(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            apply_ui_settings(
                {
                    "command_line": "codex exec",
                    "default_policy": "supervised_executable_local_commit",
                    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING: "true",
                    ALLOW_REPORT_WARNINGS_SETTING: "true",
                },
                allowed_keys=(
                    "command_line",
                    "default_policy",
                    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
                    ALLOW_REPORT_WARNINGS_SETTING,
                ),
                root=root,
            )

            policy = resolve_ui_pipeline_policy(root=root)

        self.assertFalse(policy.verify.run_git_diff_gates)
        self.assertTrue(policy.verify.block_report_warnings)
        self.assertTrue(policy.verify.allow_report_warnings)
        self.assertEqual(
            policy.to_dict()["verify"],
            {
                "run_git_diff_gates": False,
                "allow_report_warnings": True,
            },
        )

    def test_non_ui_policy_preset_stays_strict_when_ui_setting_is_enabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = ui_settings_path(root)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                (
                    "{"
                    '"allow_relaxed_git_diff_verification": true,'
                    '"allow_report_warnings": true,'
                    '"command_line": "codex exec",'
                    '"default_policy": "supervised_executable_local_commit"'
                    "}"
                ),
                encoding="utf-8",
            )

            ui_policy = resolve_ui_pipeline_policy(root=root)
            non_ui_policy = policy_preset("supervised_executable_local_commit")

        self.assertFalse(ui_policy.verify.run_git_diff_gates)
        self.assertTrue(ui_policy.verify.block_report_warnings)
        self.assertTrue(ui_policy.verify.allow_report_warnings)
        self.assertTrue(non_ui_policy.verify.run_git_diff_gates)
        self.assertTrue(non_ui_policy.verify.block_report_warnings)
        self.assertFalse(non_ui_policy.verify.allow_report_warnings)
        self.assertNotIn("verify", non_ui_policy.to_dict())


if __name__ == "__main__":
    unittest.main()

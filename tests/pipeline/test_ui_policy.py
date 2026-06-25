import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline.policy import policy_behavior_label, policy_preset
from ai_project_ctl.pipeline.ui_policy import resolve_ui_pipeline_policy
from ai_project_ctl.ui_settings import (
    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
    ALLOW_RELAXED_REPORT_WARNINGS_SETTING,
    apply_ui_settings,
    load_ui_settings,
    ui_settings_path,
)
from ai_project_ctl.web.actions import UI_SETTINGS_WEB_ALLOWED_KEYS


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

    def test_cli_ui_setting_accepts_relaxed_report_warnings_boolean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            enabled_process = run_aictl(
                root,
                "--json",
                "ui",
                "settings",
                "set",
                ALLOW_RELAXED_REPORT_WARNINGS_SETTING,
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
                ALLOW_RELAXED_REPORT_WARNINGS_SETTING,
                "0",
            )
            disabled = load_ui_settings(root=root)

        self.assertEqual(enabled_process.returncode, 0, enabled_process.stderr)
        self.assertEqual(disabled_process.returncode, 0, disabled_process.stderr)
        self.assertIs(
            enabled_payload["data"]["settings"][
                ALLOW_RELAXED_REPORT_WARNINGS_SETTING
            ],
            True,
        )
        self.assertIs(enabled[ALLOW_RELAXED_REPORT_WARNINGS_SETTING], True)
        self.assertIs(disabled[ALLOW_RELAXED_REPORT_WARNINGS_SETTING], False)

    def test_apply_ui_settings_accepts_relaxed_report_warnings_when_allowlisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            apply_ui_settings(
                {ALLOW_RELAXED_REPORT_WARNINGS_SETTING: "true"},
                allowed_keys=(ALLOW_RELAXED_REPORT_WARNINGS_SETTING,),
                root=root,
            )
            settings = load_ui_settings(root=root)

        self.assertIs(settings[ALLOW_RELAXED_REPORT_WARNINGS_SETTING], True)

    def test_web_ui_settings_allowlist_includes_relaxed_report_warnings(self):
        self.assertIn(
            ALLOW_RELAXED_REPORT_WARNINGS_SETTING,
            UI_SETTINGS_WEB_ALLOWED_KEYS,
        )

    def test_default_ui_policy_keeps_strict_git_diff_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            policy = resolve_ui_pipeline_policy(root=Path(tmp))

        self.assertTrue(policy.verify.run_git_diff_gates)
        self.assertTrue(policy.verify.block_report_warnings)
        self.assertNotIn("verify", policy.to_dict())
        self.assertNotIn("relaxed-verify", policy_behavior_label(policy))
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
        self.assertEqual(policy.to_dict()["verify"], {"run_git_diff_gates": False})
        self.assertIn("relaxed-verify", policy_behavior_label(policy))
        self.assertNotIn("report-warnings-advisory", policy_behavior_label(policy))

    def test_relaxed_report_warnings_updates_effective_policy_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            apply_ui_settings(
                {
                    "command_line": "codex exec",
                    "default_policy": "supervised_executable_local_commit",
                    ALLOW_RELAXED_REPORT_WARNINGS_SETTING: "true",
                },
                allowed_keys=(
                    "command_line",
                    "default_policy",
                    ALLOW_RELAXED_REPORT_WARNINGS_SETTING,
                ),
                root=root,
            )

            policy = resolve_ui_pipeline_policy(root=root)

        self.assertTrue(policy.verify.run_git_diff_gates)
        self.assertFalse(policy.verify.block_report_warnings)
        self.assertEqual(policy.to_dict()["verify"], {"block_report_warnings": False})
        self.assertNotIn("relaxed-verify", policy_behavior_label(policy))
        self.assertIn("report-warnings-advisory", policy_behavior_label(policy))

    def test_combined_relaxed_settings_preserve_both_verify_overrides(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            apply_ui_settings(
                {
                    "command_line": "codex exec",
                    "default_policy": "supervised_executable_local_commit",
                    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING: "true",
                    ALLOW_RELAXED_REPORT_WARNINGS_SETTING: "true",
                },
                allowed_keys=(
                    "command_line",
                    "default_policy",
                    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
                    ALLOW_RELAXED_REPORT_WARNINGS_SETTING,
                ),
                root=root,
            )

            policy = resolve_ui_pipeline_policy(root=root)

        self.assertFalse(policy.verify.run_git_diff_gates)
        self.assertFalse(policy.verify.block_report_warnings)
        self.assertEqual(
            policy.to_dict()["verify"],
            {
                "run_git_diff_gates": False,
                "block_report_warnings": False,
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
                    '"allow_relaxed_report_warnings": true,'
                    '"command_line": "codex exec",'
                    '"default_policy": "supervised_executable_local_commit"'
                    "}"
                ),
                encoding="utf-8",
            )

            ui_policy = resolve_ui_pipeline_policy(root=root)
            non_ui_policy = policy_preset("supervised_executable_local_commit")

        self.assertFalse(ui_policy.verify.run_git_diff_gates)
        self.assertFalse(ui_policy.verify.block_report_warnings)
        self.assertTrue(non_ui_policy.verify.run_git_diff_gates)
        self.assertTrue(non_ui_policy.verify.block_report_warnings)
        self.assertNotIn("verify", non_ui_policy.to_dict())


if __name__ == "__main__":
    unittest.main()

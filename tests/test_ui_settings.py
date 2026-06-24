import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.ui_settings import (
    UISettingsError,
    default_ui_settings,
    init_ui_settings,
    load_ui_settings,
    optional_ui_timeout_sec,
    upsert_ui_setting,
    ui_settings_path,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
AICTL = REPO_ROOT / "scripts" / "aictl.py"


def run_aictl(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(AICTL), "--root", str(root), *args],
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class UISettingsTests(unittest.TestCase):
    def test_defaults_include_command_line_and_policy(self):
        settings = default_ui_settings()

        self.assertEqual(settings["command_line"], "codex exec")
        self.assertEqual(settings["default_policy"], "supervised_executable_local_commit")

    def test_missing_project_or_settings_file_returns_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            self.assertEqual(load_ui_settings(root=root), default_ui_settings())

            (root / "AI_PROJECT" / "config").mkdir(parents=True)
            self.assertEqual(load_ui_settings(root=root), default_ui_settings())

    def test_project_settings_override_defaults_and_preserve_extra_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = ui_settings_path(root)
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps(
                    {
                        "command_line": "codex exec --json",
                        "default_policy": "supervised",
                        "schema_version": 1,
                        "custom_label": "pilot",
                    }
                ),
                encoding="utf-8",
            )

            settings = load_ui_settings(root=root)

            self.assertEqual(settings["command_line"], "codex exec --json")
            self.assertEqual(settings["default_policy"], "supervised")
            self.assertEqual(settings["schema_version"], 1)
            self.assertEqual(settings["custom_label"], "pilot")

    def test_optional_timeout_settings_accept_integer_strings(self):
        settings = {
            "execution_timeout_sec": "3600",
            "preflight_timeout_sec": 45,
        }

        self.assertEqual(
            optional_ui_timeout_sec(settings, "execution_timeout_sec"),
            3600,
        )
        self.assertEqual(optional_ui_timeout_sec(settings, "preflight_timeout_sec"), 45)
        self.assertIsNone(optional_ui_timeout_sec(settings, "missing_timeout_sec"))

    def test_invalid_timeout_setting_fails_with_clear_error(self):
        with self.assertRaises(UISettingsError) as raised:
            optional_ui_timeout_sec(
                {"execution_timeout_sec": "slow"},
                "execution_timeout_sec",
            )

        self.assertEqual(raised.exception.code, "UI_SETTINGS_TIMEOUT_INVALID")
        self.assertEqual(raised.exception.path, "execution_timeout_sec")
        self.assertIn("integer number of seconds", raised.exception.message)

    def test_non_object_settings_file_fails_with_clear_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = ui_settings_path(root)
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")

            with self.assertRaises(UISettingsError) as raised:
                load_ui_settings(root=root)

            self.assertEqual(raised.exception.code, "UI_SETTINGS_NOT_OBJECT")
            self.assertIn("JSON object", raised.exception.message)

    def test_init_requires_confirm_and_writes_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = ui_settings_path(root)

            with self.assertRaises(UISettingsError) as raised:
                init_ui_settings(root=root)

            self.assertEqual(raised.exception.code, "UI_SETTINGS_CONFIRM_REQUIRED")
            self.assertFalse(path.exists())

            init_ui_settings(root=root, confirm=True)

            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), default_ui_settings())

    def test_init_refuses_to_overwrite_existing_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = ui_settings_path(root)
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"schema_version": 1}), encoding="utf-8")

            with self.assertRaises(UISettingsError) as raised:
                init_ui_settings(root=root, confirm=True)

            self.assertEqual(raised.exception.code, "UI_SETTINGS_ALREADY_EXISTS")
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                {"schema_version": 1},
            )

    def test_upsert_creates_and_updates_unknown_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = ui_settings_path(root)

            upsert_ui_setting("some_random_key", "value", root=root)

            settings = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(settings["command_line"], "codex exec")
            self.assertEqual(settings["some_random_key"], "value")

            upsert_ui_setting("command_line", "codex exec --json", root=root)

            settings = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(settings["command_line"], "codex exec --json")
            self.assertEqual(settings["some_random_key"], "value")

    def test_upsert_preserves_existing_schema_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = ui_settings_path(root)
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps({"schema_version": 3, "command_line": "old"}),
                encoding="utf-8",
            )

            upsert_ui_setting("some_random_key", "value", root=root)

            settings = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(settings["schema_version"], 3)
            self.assertEqual(settings["some_random_key"], "value")

    def test_aictl_show_reports_default_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            completed = run_aictl(root, "--json", "ui", "settings", "show")

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["data"]["source"], "defaults")
            self.assertEqual(payload["data"]["settings"], default_ui_settings())

    def test_aictl_init_without_confirm_refuses_to_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            completed = run_aictl(root, "ui", "settings", "init")

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("UI_SETTINGS_CONFIRM_REQUIRED", completed.stderr)
            self.assertFalse(ui_settings_path(root).exists())

    def test_aictl_init_confirm_creates_settings_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            completed = run_aictl(root, "ui", "settings", "init", "--confirm")

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(
                json.loads(ui_settings_path(root).read_text(encoding="utf-8")),
                default_ui_settings(),
            )

    def test_aictl_set_upserts_unknown_key_and_preserves_schema_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = ui_settings_path(root)
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps({"schema_version": 1, "command_line": "old"}),
                encoding="utf-8",
            )

            completed = run_aictl(
                root,
                "ui",
                "settings",
                "set",
                "some_random_key",
                "value",
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            settings = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(settings["schema_version"], 1)
            self.assertEqual(settings["some_random_key"], "value")

            completed = run_aictl(
                root,
                "ui",
                "settings",
                "set",
                "command_line",
                "codex exec",
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            settings = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(settings["schema_version"], 1)
            self.assertEqual(settings["command_line"], "codex exec")


if __name__ == "__main__":
    unittest.main()

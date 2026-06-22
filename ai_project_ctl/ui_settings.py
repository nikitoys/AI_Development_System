"""Read-only UI settings defaults and project-local overrides."""

from __future__ import annotations

import copy
import shlex
from pathlib import Path
from typing import Any, Mapping

from ai_project_ctl.core.result import CommandError
from ai_project_ctl.core.store import StoreError, read_json_file, write_json_file


UI_SETTINGS_FILE_NAME = "ui_settings.json"
DEFAULT_UI_SETTINGS: dict[str, Any] = {
    "command_line": "codex exec",
    "default_policy": "supervised_executable_local_commit",
}
SOURCE_DEFAULTS = "defaults"
SOURCE_PROJECT_FILE = "project_file"


class UISettingsError(CommandError):
    """Stable UI settings loading error."""


def ui_settings_path(root: str | Path = ".") -> Path:
    return Path(root).resolve() / "AI_PROJECT" / "config" / UI_SETTINGS_FILE_NAME


def default_ui_settings() -> dict[str, Any]:
    return copy.deepcopy(DEFAULT_UI_SETTINGS)


def _read_project_settings(path: Path) -> dict[str, Any]:
    try:
        loaded = read_json_file(path, missing_code="UI_SETTINGS_NOT_FOUND")
    except StoreError as exc:
        if exc.code == "INVALID_JSON":
            raise UISettingsError(
                "UI_SETTINGS_INVALID_JSON",
                "UI settings file is not valid JSON: {}".format(path),
                path=str(path),
            ) from exc
        raise

    if not isinstance(loaded, dict):
        raise UISettingsError(
            "UI_SETTINGS_NOT_OBJECT",
            "UI settings file must contain a JSON object: {}".format(path),
            path=str(path),
        )
    return loaded


def ui_settings_source(*, root: str | Path = ".") -> str:
    return SOURCE_PROJECT_FILE if ui_settings_path(root).exists() else SOURCE_DEFAULTS


def load_ui_settings(*, root: str | Path = ".") -> dict[str, Any]:
    """Return effective UI settings from defaults plus optional project override."""

    path = ui_settings_path(root)
    if not path.exists():
        return default_ui_settings()

    loaded = _read_project_settings(path)

    effective = default_ui_settings()
    effective.update(loaded)
    return effective


def ui_command_line_argv(
    settings: Mapping[str, Any] | None = None,
    *,
    root: str | Path = ".",
) -> tuple[str, ...]:
    """Return the effective UI command_line as argv."""

    effective = load_ui_settings(root=root) if settings is None else settings
    command_line = effective.get("command_line")
    if not isinstance(command_line, str) or not command_line.strip():
        raise UISettingsError(
            "UI_SETTINGS_COMMAND_LINE_REQUIRED",
            "UI setting command_line must be a non-empty string.",
            path="command_line",
        )
    try:
        command = tuple(shlex.split(command_line))
    except ValueError as exc:
        raise UISettingsError(
            "UI_SETTINGS_COMMAND_LINE_INVALID",
            "UI setting command_line is not a valid shell-style command line.",
            path="command_line",
            details={"command_line": command_line, "error": str(exc)},
        ) from exc
    if not command or any(not part.strip() for part in command):
        raise UISettingsError(
            "UI_SETTINGS_COMMAND_LINE_REQUIRED",
            "UI setting command_line must produce a non-empty command.",
            path="command_line",
        )
    return command


def init_ui_settings(*, root: str | Path = ".", confirm: bool = False) -> Path:
    path = ui_settings_path(root)
    if not confirm:
        raise UISettingsError(
            "UI_SETTINGS_CONFIRM_REQUIRED",
            "Refusing to write UI settings without --confirm.",
            path=str(path),
        )
    if path.exists():
        raise UISettingsError(
            "UI_SETTINGS_ALREADY_EXISTS",
            "UI settings file already exists: {}".format(path),
            path=str(path),
        )
    write_json_file(path, default_ui_settings())
    return path


def upsert_ui_setting(key: str, value: str, *, root: str | Path = ".") -> Path:
    path = ui_settings_path(root)
    if path.exists():
        settings = default_ui_settings()
        settings.update(_read_project_settings(path))
    else:
        settings = default_ui_settings()
    settings[key] = value
    write_json_file(path, settings)
    return path

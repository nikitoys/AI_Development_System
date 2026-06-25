"""Read-only UI settings defaults and project-local overrides."""

from __future__ import annotations

import copy
import shlex
from pathlib import Path
from typing import Any, Mapping, Sequence

from ai_project_ctl.core.result import CommandError
from ai_project_ctl.core.store import StoreError, read_json_file, write_json_file


UI_SETTINGS_FILE_NAME = "ui_settings.json"
TIMEOUT_SETTING_MIN_SEC = 1
TIMEOUT_SETTING_MAX_SEC = 3600
INTERNAL_CHANGE_GATE_BYPASS_SETTING = "allow_internal_change_gate_bypass"
REQUIRE_CODEX_REVIEW_SETTING = "require_codex_review"
ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING = (
    "allow_relaxed_git_diff_verification"
)
BOOLEAN_UI_SETTING_KEYS = (
    INTERNAL_CHANGE_GATE_BYPASS_SETTING,
    REQUIRE_CODEX_REVIEW_SETTING,
    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
)
BOOLEAN_SETTING_FALSE_STRINGS = {"0", "false"}
BOOLEAN_SETTING_TRUE_STRINGS = {"1", "true"}
DEFAULT_UI_SETTINGS: dict[str, Any] = {
    "command_line": "codex exec",
    "default_policy": "supervised_executable_local_commit",
    REQUIRE_CODEX_REVIEW_SETTING: True,
    INTERNAL_CHANGE_GATE_BYPASS_SETTING: False,
    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING: False,
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
    _normalize_boolean_settings(effective)
    return effective


def _normalize_boolean_settings(settings: dict[str, Any]) -> None:
    for key in BOOLEAN_UI_SETTING_KEYS:
        settings[key] = _ui_boolean_setting(settings, key)


def _ui_boolean_setting(settings: Mapping[str, Any], key: str) -> bool:
    return _parse_ui_boolean_value(key, settings.get(key))


def _parse_ui_boolean_value(key: str, value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in BOOLEAN_SETTING_TRUE_STRINGS:
            return True
        if normalized in BOOLEAN_SETTING_FALSE_STRINGS:
            return False
    raise UISettingsError(
        "UI_SETTINGS_BOOLEAN_INVALID",
        "UI setting {} must be a boolean or one of: true, false, 1, 0.".format(key),
        path=key,
        details={
            "setting": key,
            "value": value,
            "allowed_values": ["true", "false", "1", "0"],
        },
    )


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


def optional_ui_timeout_sec(settings: Mapping[str, Any], key: str) -> int | None:
    """Return an optional UI timeout setting as integer seconds."""

    if key not in settings or settings.get(key) is None:
        return None

    value = settings[key]
    if isinstance(value, bool):
        _raise_timeout_setting_error(key, value)
    elif isinstance(value, int):
        timeout_sec = value
    elif isinstance(value, str):
        text = value.strip()
        if not text or not text.isdecimal():
            _raise_timeout_setting_error(key, value)
        timeout_sec = int(text)
    else:
        _raise_timeout_setting_error(key, value)

    if timeout_sec < TIMEOUT_SETTING_MIN_SEC or timeout_sec > TIMEOUT_SETTING_MAX_SEC:
        _raise_timeout_setting_error(key, value)
    return timeout_sec


def _raise_timeout_setting_error(key: str, value: Any) -> None:
    raise UISettingsError(
        "UI_SETTINGS_TIMEOUT_INVALID",
        (
            "UI setting {} must be an integer number of seconds between {} and {}."
        ).format(key, TIMEOUT_SETTING_MIN_SEC, TIMEOUT_SETTING_MAX_SEC),
        path=key,
        details={
            "setting": key,
            "value": value,
            "min_sec": TIMEOUT_SETTING_MIN_SEC,
            "max_sec": TIMEOUT_SETTING_MAX_SEC,
        },
    )


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


def apply_ui_settings(
    values: Mapping[str, Any],
    *,
    allowed_keys: Sequence[str],
    root: str | Path = ".",
) -> Path:
    """Apply allowlisted UI settings in one project-local write."""

    allowed = tuple(allowed_keys)
    disallowed = sorted(str(key) for key in values if key not in allowed)
    if disallowed:
        raise UISettingsError(
            "UI_SETTINGS_KEY_NOT_ALLOWED",
            "UI settings apply received keys outside the allowlist.",
            details={
                "keys": disallowed,
                "allowed_keys": list(allowed),
            },
        )

    path = ui_settings_path(root)
    if path.exists():
        settings = default_ui_settings()
        settings.update(_read_project_settings(path))
    else:
        settings = default_ui_settings()

    for key in allowed:
        if key in values:
            _set_ui_setting_value(settings, key, values[key])

    _normalize_boolean_settings(settings)
    write_json_file(path, settings)
    return path


def upsert_ui_setting(key: str, value: str, *, root: str | Path = ".") -> Path:
    path = ui_settings_path(root)
    if path.exists():
        settings = default_ui_settings()
        settings.update(_read_project_settings(path))
    else:
        settings = default_ui_settings()
    _set_ui_setting_value(settings, key, value)
    _normalize_boolean_settings(settings)
    write_json_file(path, settings)
    return path


def _set_ui_setting_value(settings: dict[str, Any], key: str, value: Any) -> None:
    if key in BOOLEAN_UI_SETTING_KEYS:
        settings[key] = _parse_ui_boolean_value(key, value)
    else:
        settings[key] = value

"""Resolve pipeline policies from project-local UI settings."""

from __future__ import annotations

import shlex
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

from ai_project_ctl.core.result import CommandError
from ai_project_ctl.ui_settings import (
    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
    ALLOW_RELAXED_REPORT_WARNINGS_SETTING,
    INTERNAL_CHANGE_GATE_BYPASS_SETTING,
    REQUIRE_CODEX_REVIEW_SETTING,
    UISettingsError,
    load_ui_settings,
    optional_ui_timeout_sec,
)

from .policy import CodexAdapterMode, CodexExecutionMode, PipelinePolicy
from .policy import apply_codex_review_requirement
from .policy_store import load_policy_preset


class UIPipelinePolicyError(CommandError):
    """Stable UI settings to pipeline policy resolution error."""


def resolve_ui_pipeline_policy(*, root: str | Path = ".") -> PipelinePolicy:
    """Return the effective pipeline policy selected by UI settings."""

    return resolve_pipeline_policy_from_settings(load_ui_settings(root=root), root=root)


def ui_internal_change_gate_bypass_enabled(*, root: str | Path = ".") -> bool:
    """Return whether UI runs may bypass Change gates for internal tasks."""

    settings = load_ui_settings(root=root)
    return bool(settings.get(INTERNAL_CHANGE_GATE_BYPASS_SETTING) is True)


def resolve_pipeline_policy_from_settings(
    settings: Mapping[str, Any],
    *,
    root: str | Path = ".",
) -> PipelinePolicy:
    """Resolve a pipeline policy from effective UI settings."""

    if not isinstance(settings, Mapping):
        raise UIPipelinePolicyError(
            "UI_POLICY_SETTINGS_NOT_OBJECT",
            "Effective UI settings must be a mapping.",
            path="settings",
        )

    policy_name = _required_text(settings, "default_policy")
    policy = _load_policy(policy_name, root=root)
    policy = apply_codex_review_requirement(
        policy,
        require_codex_review=_require_codex_review(settings),
    )
    if _allow_relaxed_git_diff_verification(settings):
        policy = replace(
            policy,
            verify=replace(policy.verify, run_git_diff_gates=False),
        )
    if _allow_relaxed_report_warnings(settings):
        policy = replace(
            policy,
            verify=replace(policy.verify, block_report_warnings=False),
        )
    execution_timeout_sec = _execution_timeout_sec(settings)
    if execution_timeout_sec is not None:
        policy = replace(
            policy,
            codex=replace(policy.codex, timeout_sec=execution_timeout_sec),
        )
    if not _requires_local_command(policy):
        return policy

    command = _command_line_argv(settings)
    command_key = shlex.join(command)
    return replace(
        policy,
        codex=replace(
            policy.codex,
            local_command=command,
            command_allowlist=(command_key,),
        ),
    )


def _require_codex_review(settings: Mapping[str, Any]) -> bool:
    value = settings.get(REQUIRE_CODEX_REVIEW_SETTING, True)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true"}
    return bool(value)


def _allow_relaxed_git_diff_verification(settings: Mapping[str, Any]) -> bool:
    value = settings.get(ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING, False)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true"}
    return bool(value)


def _allow_relaxed_report_warnings(settings: Mapping[str, Any]) -> bool:
    value = settings.get(ALLOW_RELAXED_REPORT_WARNINGS_SETTING, False)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true"}
    return bool(value)


def _load_policy(policy_name: str, *, root: str | Path) -> PipelinePolicy:
    try:
        return load_policy_preset(policy_name, root=root)
    except CommandError as exc:
        raise UIPipelinePolicyError(
            "UI_POLICY_DEFAULT_POLICY_UNKNOWN",
            "Unknown UI default_policy pipeline preset: {}".format(policy_name),
            path="default_policy",
            details={"default_policy": policy_name, "source_code": exc.code},
        ) from exc
    except (KeyError, TypeError, ValueError) as exc:
        raise UIPipelinePolicyError(
            "UI_POLICY_DEFAULT_POLICY_INVALID",
            "UI default_policy is not a valid pipeline preset: {}".format(policy_name),
            path="default_policy",
            details={"default_policy": policy_name, "error": str(exc)},
        ) from exc


def _requires_local_command(policy: PipelinePolicy) -> bool:
    return (
        policy.codex.mode == CodexExecutionMode.RUN_CODEX
        and policy.codex.adapter_mode == CodexAdapterMode.LOCAL_COMMAND
    )


def _command_line_argv(settings: Mapping[str, Any]) -> tuple[str, ...]:
    command_line = _required_text(settings, "command_line")
    try:
        command = tuple(shlex.split(command_line))
    except ValueError as exc:
        raise UIPipelinePolicyError(
            "UI_POLICY_COMMAND_LINE_INVALID",
            "UI command_line is not a valid shell-style command line.",
            path="command_line",
            details={"command_line": command_line, "error": str(exc)},
        ) from exc

    if not command or any(not part.strip() for part in command):
        raise UIPipelinePolicyError(
            "UI_POLICY_COMMAND_LINE_REQUIRED",
            "Executable pipeline policy requires a non-empty command_line.",
            path="command_line",
        )
    return command


def _execution_timeout_sec(settings: Mapping[str, Any]) -> int | None:
    try:
        return optional_ui_timeout_sec(settings, "execution_timeout_sec")
    except UISettingsError as exc:
        raise UIPipelinePolicyError(
            "UI_POLICY_EXECUTION_TIMEOUT_INVALID",
            exc.message,
            path=exc.path,
            details={"source_code": exc.code, **exc.details},
        ) from exc


def _required_text(settings: Mapping[str, Any], key: str) -> str:
    value = settings.get(key)
    if not isinstance(value, str) or not value.strip():
        code = (
            "UI_POLICY_COMMAND_LINE_REQUIRED"
            if key == "command_line"
            else "UI_POLICY_DEFAULT_POLICY_REQUIRED"
        )
        raise UIPipelinePolicyError(
            code,
            "UI setting {} must be a non-empty string.".format(key),
            path=key,
        )
    return value.strip()

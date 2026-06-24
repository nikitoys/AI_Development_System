"""Confirmed write actions for the local Web Control Center."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ai_project_ctl.core.registry import command_describe
from ai_project_ctl.core.result import CommandError, CommandResult
from ai_project_ctl.pipeline.batch import run_until_blocker
from ai_project_ctl.pipeline.session import create_session
from ai_project_ctl.pipeline.ui_policy import resolve_ui_pipeline_policy
from ai_project_ctl.ui_settings import (
    INTERNAL_CHANGE_GATE_BYPASS_SETTING,
    REQUIRE_CODEX_REVIEW_SETTING,
    apply_ui_settings,
    load_ui_settings,
    ui_settings_source,
    upsert_ui_setting,
)


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PACKAGE_ROOT / "scripts"

ACTION_KINDS = {"write", "render", "validation"}
CONFIRM_VALUES = {"yes", "true", "confirmed"}
FORBIDDEN_FILE_WRITE_FIELDS = {"content", "file", "filename", "path"}
TASK_TRANSITION_ALLOWED_TARGETS = {
    "planned",
    "ready",
    "in_progress",
    "blocked",
    "in_review",
    "changes_requested",
    "deferred",
}
PIPELINE_SESSION_STATUSES = {
    "planned",
    "running",
    "stopped",
    "blocked",
    "failed",
    "completed",
    "archived",
}
PIPELINE_STOP_STATUSES = {"stopped", "blocked", "failed"}
PIPELINE_ORDER_OPTIONS = {"execution", "owner", "selected"}
UI_SETTINGS_WEB_ALLOWED_KEYS = (
    "command_line",
    "default_policy",
    REQUIRE_CODEX_REVIEW_SETTING,
    INTERNAL_CHANGE_GATE_BYPASS_SETTING,
    "execution_timeout_sec",
    "preflight_timeout_sec",
)
LOCAL_ACTION_DESCRIPTORS: dict[str, dict[str, Any]] = {
    "ui.settings.set": {
        "name": "ui.settings.set",
        "domain": "ui",
        "description": "Update one allowlisted project-local UI setting.",
        "kind": "write",
        "arguments": [
            {
                "name": "key",
                "description": "Allowlisted UI setting key.",
                "type": "string",
                "required": True,
                "repeatable": False,
                "choices": list(UI_SETTINGS_WEB_ALLOWED_KEYS),
            },
            {
                "name": "value",
                "description": "New setting value.",
                "type": "string",
                "required": True,
                "repeatable": False,
            },
        ],
        "read_write": {
            "mutates_state": True,
            "writes_events": False,
            "renders_generated": False,
            "validates": False,
        },
        "legacy_command": ["python scripts/aictl.py ui settings set <key> <value>"],
        "availability": "implemented",
    },
    "ui.settings.apply": {
        "name": "ui.settings.apply",
        "domain": "ui",
        "description": "Apply submitted allowlisted project-local UI settings in one write.",
        "kind": "write",
        "arguments": [
            {
                "name": key,
                "description": "Allowlisted UI setting value.",
                "type": "string",
                "required": False,
                "repeatable": False,
            }
            for key in UI_SETTINGS_WEB_ALLOWED_KEYS
        ],
        "read_write": {
            "mutates_state": True,
            "writes_events": False,
            "renders_generated": False,
            "validates": False,
        },
        "legacy_command": ["python scripts/aictl.py ui settings apply --setting <key=value>"],
        "availability": "implemented",
    }
}


class WebActionError(CommandError):
    """Stable web write-action error."""


@dataclass(frozen=True)
class ActionProcessResult:
    """Captured write command result."""

    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


@dataclass(frozen=True)
class WebAction:
    """One allowed confirmed web write action."""

    action_id: str
    command_name: str
    label: str
    builder: Callable[[Mapping[str, str]], list[str]]
    confirmation_required: bool = True


@dataclass(frozen=True)
class WebActionResult:
    """Structured action response for HTTP rendering."""

    action: WebAction
    process: ActionProcessResult
    descriptor: Mapping[str, Any]
    parsed_stdout: Any | None

    @property
    def ok(self) -> bool:
        return self.process.ok

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "ok": self.ok,
            "action": self.action.action_id,
            "command": self.action.command_name,
            "label": self.action.label,
            "delegate": self.process.command,
            "returncode": self.process.returncode,
            "stdout": self.process.stdout,
            "stderr": self.process.stderr,
            "registered_command": {
                "name": self.descriptor.get("name"),
                "kind": self.descriptor.get("kind"),
                "read_write": self.descriptor.get("read_write"),
                "legacy_command": self.descriptor.get("legacy_command"),
            },
        }
        if self.parsed_stdout is not None:
            payload["result"] = self.parsed_stdout
            payload["summary"] = _action_result_summary(
                self.action,
                self.process.ok,
                self.parsed_stdout,
            )
        return payload


def available_actions() -> list[dict[str, Any]]:
    """Return safe write actions for rendering and discovery."""

    rows = []
    for action in ACTIONS.values():
        descriptor = describe_web_action(action)
        rows.append(
            {
                "id": action.action_id,
                "label": action.label,
                "command": action.command_name,
                "kind": descriptor.get("kind"),
                "read_write": descriptor.get("read_write"),
                "arguments": descriptor.get("arguments") or [],
            }
        )
    return rows


def describe_web_action(action: WebAction) -> dict[str, Any]:
    """Return metadata for registered and Web-local write actions."""

    local_descriptor = LOCAL_ACTION_DESCRIPTORS.get(action.command_name)
    if local_descriptor is not None:
        return dict(local_descriptor)
    return require_web_write_command(action.command_name)


def require_web_write_command(command_name: str) -> dict[str, Any]:
    """Return command metadata only when the command is safe to invoke as a web write."""

    descriptor = command_describe(command_name)
    read_write = descriptor.get("read_write") or {}
    if descriptor.get("availability") != "implemented":
        raise WebActionError(
            "WEB_ACTION_COMMAND_NOT_IMPLEMENTED",
            "Web action cannot execute planned command: {}".format(command_name),
            details={"command": command_name},
        )
    if descriptor.get("kind") not in ACTION_KINDS:
        raise WebActionError(
            "WEB_ACTION_COMMAND_NOT_ACTION",
            "Web action command is not a registered write/render/validation command: {}".format(
                command_name
            ),
            details={"command": command_name, "kind": descriptor.get("kind")},
        )
    if not any(
        bool(read_write.get(flag))
        for flag in ("mutates_state", "writes_events", "renders_generated")
    ):
        if descriptor.get("kind") != "validation" or not bool(read_write.get("validates")):
            raise WebActionError(
                "WEB_ACTION_COMMAND_HAS_NO_CONTROL_EFFECT",
                "Web action command does not declare a controlled effect: {}".format(
                    command_name
                ),
                details={"command": command_name, "read_write": read_write},
            )
    return descriptor


class WebActionExecutor:
    """Execute explicitly confirmed web actions through the aictl facade."""

    def __init__(
        self,
        root: str | Path = ".",
        *,
        actor: str = "human_owner",
        python_executable: str | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.actor = actor
        self.python_executable = python_executable or sys.executable

    def execute(self, fields: Mapping[str, str]) -> WebActionResult:
        action_id = _require_field(fields, "action")
        forbidden_fields = sorted(
            name for name in FORBIDDEN_FILE_WRITE_FIELDS if _field(fields, name)
        )
        if forbidden_fields:
            raise WebActionError(
                "WEB_FILE_WRITE_ARGUMENT_REJECTED",
                "Web actions do not accept arbitrary file write arguments.",
                details={"fields": forbidden_fields, "action": action_id},
            )
        try:
            action = ACTIONS[action_id]
        except KeyError as exc:
            raise WebActionError(
                "WEB_UNKNOWN_ACTION",
                "Unknown or unsupported web write action: {}".format(action_id),
                details={"action": action_id},
            ) from exc
        if action.confirmation_required and _field(fields, "confirm").lower() not in CONFIRM_VALUES:
            raise WebActionError(
                "WEB_ACTION_CONFIRMATION_REQUIRED",
                "Write action requires explicit confirmation.",
                details={"action": action_id},
            )

        descriptor = describe_web_action(action)
        if action.action_id == "ui.run_selected_task":
            process = self._create_ui_selected_task_session(fields)
        elif action.action_id == "ui.settings.set":
            process = self._update_ui_setting(fields)
        elif action.action_id == "ui.settings.apply":
            process = self._apply_ui_settings(fields)
        else:
            command = [
                self.python_executable,
                str(SCRIPTS_DIR / "aictl.py"),
                "--root",
                str(self.root),
                "--actor",
                self.actor,
                "--json",
                *action.builder(fields),
            ]
            process = self._run(command)
        parsed = _parse_json(process.stdout)
        if not process.ok:
            raise WebActionError(
                "WEB_ACTION_COMMAND_FAILED",
                "Web write action failed through registered command: {}".format(
                    action.command_name
                ),
                details={
                    "action": action.action_id,
                    "command": process.command,
                    "returncode": process.returncode,
                    "stdout": process.stdout,
                    "stderr": process.stderr,
                    "result": parsed,
                },
            )
        return WebActionResult(
            action=action,
            process=process,
            descriptor=descriptor,
            parsed_stdout=parsed,
        )

    def _create_ui_selected_task_session(
        self,
        fields: Mapping[str, str],
    ) -> ActionProcessResult:
        task_ref = _task_ref(fields)
        try:
            selected_policy = resolve_ui_pipeline_policy(root=self.root)
            session_result = create_session(
                root=self.root,
                actor=self.actor,
                policy=selected_policy,
                policy_name=selected_policy.name,
                task_refs=(task_ref,),
                max_tasks=1,
                order_by="selected",
            )
        except CommandError as exc:
            raise WebActionError(
                exc.code,
                exc.message,
                path=exc.path,
                details={"action": "ui.run_selected_task", **exc.details},
            ) from exc

        result = session_result
        if session_result.ok:
            session_id = str(session_result.data.get("session_id") or "")
            result = run_until_blocker(
                session_id,
                root=self.root,
                actor=self.actor,
                confirmed=True,
            )
            _merge_command_result_effects(result, session_result)
            result.data.setdefault("created_session", session_result.data.get("session"))

        result.data.setdefault("task_ref", task_ref)
        result.data.setdefault("policy", selected_policy.name)
        session_id = str(result.data.get("session_id") or "")
        if session_id:
            target = "/pipeline/sessions/{}".format(session_id)
            result.data["session_href"] = target
            result.data["redirect_target"] = target
            next_action = "Open pipeline session {}.".format(session_id)
            if next_action not in result.next_actions:
                result.next_actions.append(next_action)
        command = [
            self.python_executable,
            str(SCRIPTS_DIR / "aictl.py"),
            "--root",
            str(self.root),
            "--actor",
            self.actor,
            "--json",
            "ui",
            "run",
            task_ref,
            "--confirm",
        ]
        return ActionProcessResult(
            command=command,
            returncode=0 if result.ok else 1,
            stdout=json.dumps(
                result.to_dict(),
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n",
            stderr="",
        )

    def _update_ui_setting(self, fields: Mapping[str, str]) -> ActionProcessResult:
        key = _allowed_ui_setting_key(fields)
        value = _require_field(fields, "value")
        try:
            path = upsert_ui_setting(key, value, root=self.root)
            result = CommandResult.success(
                command="ui.settings.set",
                domain="ui",
                message="OK: updated UI setting {}".format(key),
                data={
                    "key": key,
                    "value": value,
                    "path": str(path),
                    "settings": load_ui_settings(root=self.root),
                    "source": ui_settings_source(root=self.root),
                },
            )
            result.changed_files.append(str(path))
        except CommandError as exc:
            raise WebActionError(
                exc.code,
                exc.message,
                path=exc.path,
                details={"action": "ui.settings.set", **exc.details},
            ) from exc

        command = [
            self.python_executable,
            str(SCRIPTS_DIR / "aictl.py"),
            "--root",
            str(self.root),
            "--actor",
            self.actor,
            "--json",
            "ui",
            "settings",
            "set",
            key,
            value,
        ]
        return ActionProcessResult(
            command=command,
            returncode=0,
            stdout=json.dumps(result.to_dict(), ensure_ascii=False, sort_keys=True)
            + "\n",
            stderr="",
        )

    def _apply_ui_settings(self, fields: Mapping[str, str]) -> ActionProcessResult:
        values = _allowed_ui_settings_values(fields)
        try:
            path = apply_ui_settings(
                values,
                allowed_keys=UI_SETTINGS_WEB_ALLOWED_KEYS,
                root=self.root,
            )
            effective = load_ui_settings(root=self.root)
            result = CommandResult.success(
                command="ui.settings.apply",
                domain="ui",
                message="OK: applied UI settings",
                data={
                    "applied_keys": list(values),
                    "path": str(path),
                    "settings": effective,
                    "source": ui_settings_source(root=self.root),
                },
            )
            result.changed_files.append(str(path))
        except CommandError as exc:
            raise WebActionError(
                exc.code,
                exc.message,
                path=exc.path,
                details={"action": "ui.settings.apply", **exc.details},
            ) from exc

        command = [
            self.python_executable,
            str(SCRIPTS_DIR / "aictl.py"),
            "--root",
            str(self.root),
            "--actor",
            self.actor,
            "--json",
            *_build_ui_settings_apply(fields),
        ]
        return ActionProcessResult(
            command=command,
            returncode=0,
            stdout=json.dumps(result.to_dict(), ensure_ascii=False, sort_keys=True)
            + "\n",
            stderr="",
        )

    def _run(self, command: Sequence[str]) -> ActionProcessResult:
        completed = subprocess.run(
            list(command),
            cwd=str(PACKAGE_ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return ActionProcessResult(
            command=list(command),
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )


def _build_task_transition(fields: Mapping[str, str]) -> list[str]:
    task_ref = _task_ref(fields)
    target = _require_field(fields, "to")
    if target not in TASK_TRANSITION_ALLOWED_TARGETS:
        raise WebActionError(
            "WEB_UNSAFE_TASK_TRANSITION",
            "Web task transition target is not allowed: {}".format(target),
            details={
                "target": target,
                "allowed_targets": sorted(TASK_TRANSITION_ALLOWED_TARGETS),
            },
        )
    return ["task", "transition", task_ref, "--to", target]


def _build_task_create(fields: Mapping[str, str]) -> list[str]:
    args = [
        "task",
        "create",
        "--confirm",
        "--epic",
        _require_field(fields, "epic"),
        "--title",
        _require_field(fields, "title"),
    ]
    for field_name, flag in (
        ("summary", "--summary"),
        ("description", "--description"),
        ("status", "--status"),
        ("active_role", "--active-role"),
        ("active_stage", "--active-stage"),
        ("active_document", "--active-document"),
        ("expected_result", "--expected-result"),
        ("verification_mode", "--verification-mode"),
        ("dependency_reason", "--dependency-reason"),
    ):
        value = _field(fields, field_name)
        if value:
            args.extend([flag, value])
    for field_name, flag in (
        ("scope", "--scope"),
        ("out_of_scope", "--out-of-scope"),
        ("allowed_file", "--allowed-file"),
        ("acceptance", "--acceptance"),
        ("review_instruction", "--review-instruction"),
        ("note", "--note"),
        ("depends_on", "--depends-on"),
    ):
        for value in _multiline_values(fields, field_name):
            args.extend([flag, value])
    return args


def _build_task_import(fields: Mapping[str, str]) -> list[str]:
    args = ["task", "import", "--text", _require_field(fields, "import_text")]
    if _field(fields, "confirm").lower() in CONFIRM_VALUES:
        args.append("--confirm")
    else:
        args.append("--preview")
    return args


def _build_current_set(fields: Mapping[str, str]) -> list[str]:
    return ["current", "set", _task_ref(fields)]


def _build_current_clear(fields: Mapping[str, str]) -> list[str]:
    return ["current", "clear"]


def _build_project_render(fields: Mapping[str, str]) -> list[str]:
    return ["project", "render"]


def _build_project_doctor(fields: Mapping[str, str]) -> list[str]:
    return ["project", "doctor"]


def _build_project_protected_check(fields: Mapping[str, str]) -> list[str]:
    return ["project", "protected-check"]


def _build_docs_render(fields: Mapping[str, str]) -> list[str]:
    return ["docs", "render"]


def _build_context_build(fields: Mapping[str, str]) -> list[str]:
    task_ref = _task_ref(fields)
    args = ["context", "build", "--task", task_ref, "--write"]
    limit = _field(fields, "limit")
    if limit:
        if not limit.isdigit() or int(limit) < 1:
            raise WebActionError(
                "WEB_INVALID_ACTION_ARGUMENT",
                "Context build limit must be a positive integer.",
                details={"limit": limit},
            )
        args.extend(["--limit", limit])
    return args


def _build_codex_prompt_build(fields: Mapping[str, str]) -> list[str]:
    args = ["codex", "prompt", "build", "--task", _task_ref(fields)]
    if _field(fields, "with_context").lower() in CONFIRM_VALUES:
        args.append("--with-context")
    return args


def _build_pipeline_session_create(fields: Mapping[str, str]) -> list[str]:
    args = [
        "pipeline",
        "session",
        "create",
        "--policy",
        _field(fields, "policy") or "dry_run",
    ]
    if _field(fields, "auto_create_missing_changes").lower() in CONFIRM_VALUES:
        args.append("--auto-create-missing-changes")
    if _field(fields, "owner_approve_required_changes").lower() in CONFIRM_VALUES:
        args.append("--owner-approve-required-changes")
        args.extend(["--approval-note", _require_field(fields, "approval_note")])
    auto_close_note = _field(fields, "auto_close_note")
    if auto_close_note:
        args.extend(["--auto-close-note", auto_close_note])
    for value in _split_values(fields, "task_ref"):
        args.extend(["--task-ref", value])
    for value in _split_values(fields, "epic"):
        args.extend(["--epic", value])
    for value in _split_values(fields, "status_filter"):
        args.extend(["--status-filter", value])
    max_tasks = _field(fields, "max_tasks")
    if max_tasks:
        if not max_tasks.isdigit() or int(max_tasks) < 1:
            raise WebActionError(
                "WEB_INVALID_ACTION_ARGUMENT",
                "Pipeline max tasks must be a positive integer.",
                details={"max_tasks": max_tasks},
            )
        args.extend(["--max-tasks", max_tasks])
    order_by = _field(fields, "order_by")
    if order_by:
        if order_by not in PIPELINE_ORDER_OPTIONS:
            raise WebActionError(
                "WEB_INVALID_ACTION_ARGUMENT",
                "Pipeline order_by is not allowed: {}".format(order_by),
                details={"order_by": order_by, "allowed": sorted(PIPELINE_ORDER_OPTIONS)},
            )
        args.extend(["--order-by", order_by])
    for field_name, flag in (
        ("current_task_id", "--current-task-id"),
        ("current_task_ref", "--current-task-ref"),
    ):
        value = _field(fields, field_name)
        if value:
            args.extend([flag, value])
    for value in _split_values(fields, "change"):
        args.extend(["--change", value])
    for value in _split_values(fields, "report"):
        args.extend(["--report", value])
    status = _field(fields, "status")
    if status:
        if status not in PIPELINE_SESSION_STATUSES:
            raise WebActionError(
                "WEB_INVALID_ACTION_ARGUMENT",
                "Pipeline session status is not allowed: {}".format(status),
                details={"status": status, "allowed": sorted(PIPELINE_SESSION_STATUSES)},
            )
        args.extend(["--status", status])
    return args


def _build_ui_run_selected_task(fields: Mapping[str, str]) -> list[str]:
    return ["ui", "run", _task_ref(fields), "--confirm"]


def _build_ui_settings_set(fields: Mapping[str, str]) -> list[str]:
    return [
        "ui",
        "settings",
        "set",
        _allowed_ui_setting_key(fields),
        _require_field(fields, "value"),
    ]


def _build_ui_settings_apply(fields: Mapping[str, str]) -> list[str]:
    args = ["ui", "settings", "apply"]
    for key, value in _allowed_ui_settings_values(fields).items():
        args.extend(["--setting", "{}={}".format(key, value)])
    return args


def _build_pipeline_run_next(fields: Mapping[str, str]) -> list[str]:
    args = ["pipeline", "run-next"]
    session_id = _field(fields, "session_id")
    if session_id:
        args.append(session_id)
    return args


def _build_pipeline_run_until_blocker(fields: Mapping[str, str]) -> list[str]:
    args = ["pipeline", "run-until-blocker"]
    session_id = _field(fields, "session_id")
    if session_id:
        args.append(session_id)
    args.append("--confirm")
    return args


def _build_pipeline_session_stop(fields: Mapping[str, str]) -> list[str]:
    status = _field(fields, "status") or "stopped"
    if status not in PIPELINE_STOP_STATUSES:
        raise WebActionError(
            "WEB_INVALID_ACTION_ARGUMENT",
            "Pipeline stop status is not allowed: {}".format(status),
            details={"status": status, "allowed": sorted(PIPELINE_STOP_STATUSES)},
        )
    return [
        "pipeline",
        "session",
        "stop",
        _require_field(fields, "session_id"),
        "--reason",
        _require_field(fields, "reason"),
        "--status",
        status,
    ]


def _build_pipeline_render(fields: Mapping[str, str]) -> list[str]:
    return ["pipeline", "render"]


def _build_workflow(
    workflow_name: str,
    *,
    target_field: str = "task",
    include_notes: bool = False,
) -> Callable[[Mapping[str, str]], list[str]]:
    def build(fields: Mapping[str, str]) -> list[str]:
        if target_field == "task":
            target = _task_ref(fields)
        else:
            target = _require_field(fields, target_field)
        args = [
            "workflow",
            "run",
            workflow_name,
            "--{}".format(target_field),
            target,
        ]
        if include_notes:
            args.extend(["--notes", _require_field(fields, "notes")])
        args.append("--confirm")
        return args

    return build


def _task_ref(fields: Mapping[str, str]) -> str:
    return _field(fields, "task") or _require_field(fields, "task_id")


def _allowed_ui_setting_key(fields: Mapping[str, str]) -> str:
    key = _require_field(fields, "key")
    if key not in UI_SETTINGS_WEB_ALLOWED_KEYS:
        raise WebActionError(
            "WEB_UI_SETTING_KEY_NOT_ALLOWED",
            "Web UI settings action cannot update setting key: {}".format(key),
            path=key,
            details={
                "key": key,
                "allowed_keys": list(UI_SETTINGS_WEB_ALLOWED_KEYS),
            },
        )
    return key


def _allowed_ui_settings_values(fields: Mapping[str, str]) -> dict[str, str]:
    control_fields = {"action", "confirm"}
    unexpected = sorted(
        key
        for key in fields
        if key not in control_fields and key not in UI_SETTINGS_WEB_ALLOWED_KEYS
    )
    if unexpected:
        raise WebActionError(
            "WEB_UI_SETTING_KEY_NOT_ALLOWED",
            "Web UI settings apply cannot update setting keys outside the allowlist.",
            details={
                "keys": unexpected,
                "allowed_keys": list(UI_SETTINGS_WEB_ALLOWED_KEYS),
            },
        )
    return {
        key: _field(fields, key)
        for key in UI_SETTINGS_WEB_ALLOWED_KEYS
        if key in fields
    }


def _require_field(fields: Mapping[str, str], name: str) -> str:
    value = _field(fields, name)
    if not value:
        raise WebActionError(
            "WEB_MISSING_ACTION_ARGUMENT",
            "Web write action is missing required argument: {}".format(name),
            details={"argument": name},
        )
    return value


def _field(fields: Mapping[str, str], name: str) -> str:
    return str(fields.get(name) or "").strip()


def _multiline_values(fields: Mapping[str, str], name: str) -> list[str]:
    return [
        line.strip()
        for line in _field(fields, name).splitlines()
        if line.strip()
    ]


def _split_values(fields: Mapping[str, str], name: str) -> list[str]:
    values: list[str] = []
    for line in _field(fields, name).splitlines():
        for value in line.split(","):
            text = value.strip()
            if text:
                values.append(text)
    return values


def _parse_json(text: str) -> Any | None:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return None


def _action_result_summary(
    action: WebAction,
    ok: bool,
    parsed_stdout: Any,
) -> dict[str, Any]:
    if not isinstance(parsed_stdout, Mapping):
        return {}

    data = parsed_stdout.get("data")
    data_mapping = data if isinstance(data, Mapping) else {}
    steps = data_mapping.get("steps")
    summary: dict[str, Any] = {
        "ok": ok,
        "message": str(parsed_stdout.get("message") or ""),
        "owner_action_required": str(parsed_stdout.get("owner_action_required") or ""),
        "next_actions": _string_list(parsed_stdout.get("next_actions")),
    }
    if isinstance(steps, list):
        summary["steps"] = [
            {
                "id": str(step.get("id") or ""),
                "title": str(step.get("title") or ""),
                "status": str(step.get("status") or ""),
            }
            for step in steps
            if isinstance(step, Mapping)
        ]
        summary["step_counts"] = _step_counts(summary["steps"])

    if action.action_id == "task.prepare_for_codex" and ok:
        instruction = "Read AI_PROJECT/generated/CODEX_PROMPT.md and execute it."
        summary["next_codex_instruction"] = instruction
        if instruction not in summary["next_actions"]:
            summary["next_actions"].append(instruction)

    return summary


def _merge_command_result_effects(
    target: CommandResult,
    *sources: CommandResult,
) -> None:
    for source in sources:
        _extend_unique(target.changed_files, source.changed_files)
        _extend_unique(target.generated_files, source.generated_files)
        _extend_unique(target.events, source.events)
        target.warnings.extend(source.warnings)


def _extend_unique(target: list[str], values: Sequence[str]) -> None:
    seen = set(target)
    for value in values:
        text = str(value)
        if text and text not in seen:
            target.append(text)
            seen.add(text)


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _step_counts(steps: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for step in steps:
        status = str(step.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


ACTIONS: dict[str, WebAction] = {
    "task.create": WebAction(
        action_id="task.create",
        command_name="task.create",
        label="Create task",
        builder=_build_task_create,
    ),
    "task.import": WebAction(
        action_id="task.import",
        command_name="task.import",
        label="Bulk import tasks",
        builder=_build_task_import,
        confirmation_required=False,
    ),
    "task.transition": WebAction(
        action_id="task.transition",
        command_name="task.transition",
        label="Task transition",
        builder=_build_task_transition,
    ),
    "current.set": WebAction(
        action_id="current.set",
        command_name="current.set",
        label="Set current task",
        builder=_build_current_set,
    ),
    "current.clear": WebAction(
        action_id="current.clear",
        command_name="current.clear",
        label="Clear current task",
        builder=_build_current_clear,
    ),
    "project.render": WebAction(
        action_id="project.render",
        command_name="project.render",
        label="Regenerate project views",
        builder=_build_project_render,
    ),
    "project.doctor": WebAction(
        action_id="project.doctor",
        command_name="project.doctor",
        label="Run Doctor",
        builder=_build_project_doctor,
    ),
    "project.protected_check": WebAction(
        action_id="project.protected_check",
        command_name="project.protected_check",
        label="Check protected files",
        builder=_build_project_protected_check,
    ),
    "docs.render": WebAction(
        action_id="docs.render",
        command_name="docs.render",
        label="Render docs",
        builder=_build_docs_render,
    ),
    "context.build": WebAction(
        action_id="context.build",
        command_name="context.build",
        label="Build task context",
        builder=_build_context_build,
    ),
    "codex.prompt.build": WebAction(
        action_id="codex.prompt.build",
        command_name="codex.prompt.build",
        label="Build Codex prompt",
        builder=_build_codex_prompt_build,
    ),
    "pipeline.session.create": WebAction(
        action_id="pipeline.session.create",
        command_name="pipeline.session.create",
        label="Create pipeline session",
        builder=_build_pipeline_session_create,
    ),
    "ui.run_selected_task": WebAction(
        action_id="ui.run_selected_task",
        command_name="pipeline.run_until_blocker",
        label="Run selected task",
        builder=_build_ui_run_selected_task,
    ),
    "ui.settings.set": WebAction(
        action_id="ui.settings.set",
        command_name="ui.settings.set",
        label="Update UI setting",
        builder=_build_ui_settings_set,
    ),
    "ui.settings.apply": WebAction(
        action_id="ui.settings.apply",
        command_name="ui.settings.apply",
        label="Apply UI settings",
        builder=_build_ui_settings_apply,
    ),
    "pipeline.run_next": WebAction(
        action_id="pipeline.run_next",
        command_name="pipeline.run_next",
        label="Run next pipeline step",
        builder=_build_pipeline_run_next,
    ),
    "pipeline.run_until_blocker": WebAction(
        action_id="pipeline.run_until_blocker",
        command_name="pipeline.run_until_blocker",
        label="Run until blocker",
        builder=_build_pipeline_run_until_blocker,
    ),
    "pipeline.session.stop": WebAction(
        action_id="pipeline.session.stop",
        command_name="pipeline.session.stop",
        label="Stop pipeline session",
        builder=_build_pipeline_session_stop,
    ),
    "pipeline.render": WebAction(
        action_id="pipeline.render",
        command_name="pipeline.render",
        label="Refresh pipeline status",
        builder=_build_pipeline_render,
    ),
    "task.prepare_for_codex": WebAction(
        action_id="task.prepare_for_codex",
        command_name="task.prepare_for_codex",
        label="Prepare for Codex",
        builder=_build_workflow("task.prepare_for_codex"),
    ),
    "task.refresh_execution_context": WebAction(
        action_id="task.refresh_execution_context",
        command_name="task.refresh_execution_context",
        label="Refresh execution context",
        builder=_build_workflow("task.refresh_execution_context"),
    ),
    "task.submit_for_review": WebAction(
        action_id="task.submit_for_review",
        command_name="task.submit_for_review",
        label="Submit for review",
        builder=_build_workflow("task.submit_for_review"),
    ),
    "task.close_reviewed": WebAction(
        action_id="task.close_reviewed",
        command_name="task.close_reviewed",
        label="Approve & Done",
        builder=_build_workflow("task.close_reviewed", include_notes=True),
    ),
    "task.request_changes": WebAction(
        action_id="task.request_changes",
        command_name="task.request_changes",
        label="Request Changes",
        builder=_build_workflow("task.request_changes", include_notes=True),
    ),
    "evolution.create_for_task": WebAction(
        action_id="evolution.create_for_task",
        command_name="evolution.create_for_task",
        label="Create Evolution Change",
        builder=_build_workflow("evolution.create_for_task"),
    ),
    "evolution.approve_change": WebAction(
        action_id="evolution.approve_change",
        command_name="evolution.approve_change",
        label="Approve Evolution Change",
        builder=_build_workflow(
            "evolution.approve_change",
            target_field="change",
            include_notes=True,
        ),
    ),
    "evolution.move_to_review": WebAction(
        action_id="evolution.move_to_review",
        command_name="evolution.move_to_review",
        label="Move Evolution Change to Review",
        builder=_build_workflow("evolution.move_to_review", target_field="change"),
    ),
    "evolution.accept_change": WebAction(
        action_id="evolution.accept_change",
        command_name="evolution.accept_change",
        label="Accept Evolution Change",
        builder=_build_workflow(
            "evolution.accept_change",
            target_field="change",
            include_notes=True,
        ),
    ),
    "epic.close_if_complete": WebAction(
        action_id="epic.close_if_complete",
        command_name="epic.close_if_complete",
        label="Close Epic If Complete",
        builder=_build_workflow("epic.close_if_complete", target_field="epic"),
    ),
}

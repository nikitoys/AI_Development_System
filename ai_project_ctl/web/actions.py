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
from ai_project_ctl.pipeline.git_commit import (
    CODE_CHECKPOINT_CLEAN,
    CODE_CHECKPOINT_CREATED,
    create_checkpoint_commit,
)
from ai_project_ctl.pipeline.git_status import (
    WorktreeDirtyPreflight,
    capture_worktree_dirty_preflight,
)
from ai_project_ctl.pipeline.policy import with_effective_batch_max_steps
from ai_project_ctl.pipeline.policy_store import load_policy_preset
from ai_project_ctl.pipeline.report_recovery import (
    ReportRecoveryError,
    submit_recovered_report,
)
from ai_project_ctl.pipeline.runner import RUN_NEXT_PHASE_SEQUENCE
from ai_project_ctl.pipeline.session import create_session
from ai_project_ctl.pipeline.ui_policy import (
    resolve_ui_pipeline_policy,
    ui_internal_change_gate_bypass_enabled,
)
from ai_project_ctl.pipeline.ui_run import (
    UIRunSelectionResolution,
    build_ui_run_batch_queue,
    build_ui_run_selected_queue,
    resolve_ui_run_selection,
)
from ai_project_ctl.ui_settings import (
    ALLOW_REPORT_WARNINGS_SETTING,
    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
    ALLOW_RELAXED_REPORT_WARNINGS_SETTING,
    BATCH_MAX_FAILURES_SETTING,
    BATCH_MAX_STEPS_SETTING,
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
INCOMPLETE_RUN_CONFIRM_FIELD = "incomplete_run_confirm"
MANUAL_CHECKPOINT_COMMANDS = (
    "git status --short --untracked-files=all",
    "git add -A",
    'git commit -m "Checkpoint before Web Run"',
)
UI_SETTINGS_WEB_ALLOWED_KEYS = (
    "command_line",
    "default_policy",
    BATCH_MAX_STEPS_SETTING,
    BATCH_MAX_FAILURES_SETTING,
    REQUIRE_CODEX_REVIEW_SETTING,
    INTERNAL_CHANGE_GATE_BYPASS_SETTING,
    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
    ALLOW_REPORT_WARNINGS_SETTING,
    ALLOW_RELAXED_REPORT_WARNINGS_SETTING,
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
    },
    "pipeline.report_recovery.submit": {
        "name": "pipeline.report_recovery.submit",
        "domain": "pipeline",
        "description": "Submit an owner-confirmed recovered draft report for a REPORT_MISSING session.",
        "kind": "write",
        "arguments": [
            {
                "name": "session_id",
                "description": "Pipeline session ID blocked by REPORT_MISSING.",
                "type": "string",
                "required": True,
                "repeatable": False,
            },
            {
                "name": "task_id",
                "description": "Selected task ID shown in the recovery draft.",
                "type": "string",
                "required": False,
                "repeatable": False,
            },
            {
                "name": "task_ref",
                "description": "Selected task ref shown in the recovery draft.",
                "type": "string",
                "required": False,
                "repeatable": False,
            },
        ],
        "read_write": {
            "mutates_state": True,
            "writes_events": True,
            "renders_generated": False,
            "validates": True,
        },
        "legacy_command": [
            "Web-only recovery action; submits through ai_project_ctl.task_reports."
        ],
        "availability": "implemented",
    },
    "ui.checkpoint_commit": {
        "name": "ui.checkpoint_commit",
        "domain": "ui",
        "description": "Create an owner-confirmed checkpoint git commit before Web Run.",
        "kind": "write",
        "arguments": [
            {
                "name": "task",
                "description": "Selected task ref to run again after the checkpoint.",
                "type": "string",
                "required": False,
                "repeatable": False,
            },
            {
                "name": "task_id",
                "description": "Selected task ID to run again after the checkpoint.",
                "type": "string",
                "required": False,
                "repeatable": False,
            },
        ],
        "read_write": {
            "mutates_state": True,
            "writes_events": False,
            "renders_generated": False,
            "validates": False,
        },
        "legacy_command": [
            "git status --short --untracked-files=all",
            "git add -A",
            'git commit -m "Checkpoint before Web Run"',
        ],
        "availability": "implemented",
    },
    "ui.run_task_batch": {
        "name": "ui.run_task_batch",
        "domain": "ui",
        "description": (
            "Create and run an owner-confirmed multi-task pipeline session using "
            "effective UI pipeline settings."
        ),
        "kind": "write",
        "arguments": [
            {
                "name": "task_ref",
                "description": "Optional task refs to seed the batch queue.",
                "type": "string",
                "required": False,
                "repeatable": True,
            },
            {
                "name": "epic",
                "description": "Optional epic IDs to filter the batch queue.",
                "type": "string",
                "required": False,
                "repeatable": True,
            },
            {
                "name": "status_filter",
                "description": "Optional task statuses to filter the batch queue.",
                "type": "string",
                "required": False,
                "repeatable": True,
            },
            {
                "name": "max_tasks",
                "description": "Maximum tasks to select for the batch session.",
                "type": "integer",
                "required": False,
                "repeatable": False,
            },
            {
                "name": "order_by",
                "description": "Queue ordering mode.",
                "type": "string",
                "required": False,
                "repeatable": False,
                "choices": sorted(PIPELINE_ORDER_OPTIONS),
            },
            {
                "name": "auto_close_note",
                "description": "Human Owner note required by auto-close policies.",
                "type": "string",
                "required": False,
                "repeatable": False,
            },
        ],
        "read_write": {
            "mutates_state": True,
            "writes_events": True,
            "renders_generated": True,
            "validates": True,
        },
        "legacy_command": [
            "Web-only action; creates a UI batch session and delegates to pipeline.run_until_blocker."
        ],
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
        elif action.action_id == "ui.run_task_batch":
            process = self._create_ui_task_batch_session(fields)
        elif action.action_id == "ui.checkpoint_commit":
            process = self._create_checkpoint_commit(fields)
        elif action.action_id == "ui.settings.set":
            process = self._update_ui_setting(fields)
        elif action.action_id == "ui.settings.apply":
            process = self._apply_ui_settings(fields)
        elif action.action_id == "pipeline.report_recovery.submit":
            process = self._submit_recovered_report(fields)
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
        auto_close_note = _field(fields, "auto_close_note")
        try:
            selection = resolve_ui_run_selection(self.root, task_ref)
            if not selection.should_run:
                result = _ui_run_selection_not_run_result(selection)
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
                ]
                if auto_close_note:
                    command.extend(["--auto-close-note", auto_close_note])
                command.append("--confirm")
                return ActionProcessResult(
                    command=command,
                    returncode=0,
                    stdout=json.dumps(
                        result.to_dict(),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    stderr="",
                )

            dirty_preflight = capture_worktree_dirty_preflight(root=self.root)
            if dirty_preflight.should_block:
                result = _ui_run_worktree_preflight_not_run_result(
                    selection,
                    dirty_preflight,
                )
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
                ]
                if auto_close_note:
                    command.extend(["--auto-close-note", auto_close_note])
                command.append("--confirm")
                return ActionProcessResult(
                    command=command,
                    returncode=0,
                    stdout=json.dumps(
                        result.to_dict(),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    stderr="",
                )

            selected_policy = resolve_ui_pipeline_policy(root=self.root)
            _require_incomplete_run_confirmation(selected_policy, fields)
            session_result = create_session(
                root=self.root,
                actor=self.actor,
                policy=selected_policy,
                policy_name=selected_policy.name,
                auto_close_note=auto_close_note,
                selected_queue=build_ui_run_selected_queue(
                    selected_policy,
                    task_ref,
                    confirmed=True,
                    allow_internal_change_gate_bypass=(
                        ui_internal_change_gate_bypass_enabled(root=self.root)
                    ),
                ),
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
            created_session = session_result.data.get("session")
            result.data.setdefault("created_session", created_session)
            _apply_committed_close_action_view(result, created_session)

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
        ]
        if auto_close_note:
            command.extend(["--auto-close-note", auto_close_note])
        command.append("--confirm")
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

    def _create_ui_task_batch_session(
        self,
        fields: Mapping[str, str],
    ) -> ActionProcessResult:
        auto_close_note = _field(fields, "auto_close_note")
        command = _build_ui_run_task_batch(fields)
        requested_queue_inputs = _ui_task_batch_requested_inputs(fields)
        dirty_preflight = capture_worktree_dirty_preflight(root=self.root)
        if dirty_preflight.should_block:
            result = _ui_run_batch_worktree_preflight_not_run_result(
                requested_queue_inputs,
                dirty_preflight,
            )
            return ActionProcessResult(
                command=command,
                returncode=0,
                stdout=json.dumps(
                    result.to_dict(),
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n",
                stderr="",
            )
        try:
            selected_policy = resolve_ui_pipeline_policy(root=self.root)
            selected_queue = build_ui_run_batch_queue(
                selected_policy,
                task_refs=requested_queue_inputs["task_ref"],
                epic_ids=requested_queue_inputs["epic"],
                statuses=requested_queue_inputs["status_filter"],
                max_tasks=requested_queue_inputs["max_tasks"] or None,
                order_by=requested_queue_inputs["order_by"] or None,
                confirmed=True,
                allow_internal_change_gate_bypass=(
                    ui_internal_change_gate_bypass_enabled(root=self.root)
                ),
            )
            effective_policy, effective_max_steps = with_effective_batch_max_steps(
                selected_policy,
                max_tasks=int(selected_queue["max_tasks"]),
                phase_count=len(RUN_NEXT_PHASE_SEQUENCE),
            )
            session_result = create_session(
                root=self.root,
                actor=self.actor,
                policy=effective_policy,
                policy_name=effective_policy.name,
                auto_close_note=auto_close_note,
                selected_queue=selected_queue,
            )
        except ValueError as exc:
            raise WebActionError(
                "WEB_INVALID_ACTION_ARGUMENT",
                str(exc),
                details={"action": "ui.run_task_batch"},
            ) from exc
        except CommandError as exc:
            raise WebActionError(
                exc.code,
                exc.message,
                path=exc.path,
                details={"action": "ui.run_task_batch", **exc.details},
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

        result.data.setdefault("policy", selected_policy.name)
        result.data.setdefault("selected_policy", selected_policy.name)
        result.data.setdefault("effective_batch_max_steps", effective_max_steps)
        result.data.setdefault("requested_queue_inputs", requested_queue_inputs)
        result.data.setdefault("selected_queue", selected_queue)
        session_id = str(
            result.data.get("session_id")
            or session_result.data.get("session_id")
            or ""
        )
        if session_id:
            result.data["session_id"] = session_id
            target = "/pipeline/sessions/{}".format(session_id)
            result.data["session_href"] = target
            result.data["redirect_target"] = target
            next_action = "Open pipeline session {}.".format(session_id)
            if next_action not in result.next_actions:
                result.next_actions.append(next_action)
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

    def _create_checkpoint_commit(
        self,
        fields: Mapping[str, str],
    ) -> ActionProcessResult:
        task_ref = _task_ref(fields)
        task_id = _field(fields, "task_id")
        selected_task = _selected_task_label(task_ref, task_id)
        checkpoint = create_checkpoint_commit(root=self.root, task_ref=task_ref)
        dirty_files = [item.path for item in checkpoint.dirty_files]
        if checkpoint.code == CODE_CHECKPOINT_CREATED:
            outcome = "checkpoint_commit_created"
        elif checkpoint.code == CODE_CHECKPOINT_CLEAN:
            outcome = "worktree_clean"
        else:
            outcome = "checkpoint_commit_failed"
        data: dict[str, Any] = {
            "task_ref": task_ref,
            "task_id": task_id,
            "selected_task": selected_task,
            "outcome": outcome,
            "not_run": checkpoint.code == CODE_CHECKPOINT_CLEAN,
            "status": checkpoint.status,
            "code": checkpoint.code,
            "reason": checkpoint.reason,
            "commit_hash": checkpoint.commit_hash,
            "dirty_files": dirty_files,
            "git_status_entries": [item.to_dict() for item in checkpoint.dirty_files],
            "checkpoint_message": checkpoint.message,
            "commands": [command.to_dict() for command in checkpoint.commands],
            "next_action": "Run selected task {} again.".format(selected_task),
        }
        if checkpoint.code == CODE_CHECKPOINT_CLEAN:
            data["stop_code"] = "WORKTREE_CLEAN"
        if checkpoint.code == CODE_CHECKPOINT_CREATED:
            message = "Created checkpoint commit {} before Web Run.".format(
                checkpoint.commit_hash
            )
        elif checkpoint.code == CODE_CHECKPOINT_CLEAN:
            message = "NOT RUN: worktree is already clean; no checkpoint commit was created."
        else:
            message = checkpoint.reason

        if checkpoint.ok:
            result = CommandResult.success(
                command="ui.checkpoint_commit",
                domain="ui",
                message=message,
                data=data,
            )
            result.next_actions.append(data["next_action"])
        else:
            result = CommandResult.failure(
                command="ui.checkpoint_commit",
                domain="ui",
                message=message,
            )
            result.data.update(data)
        command = ["ui.checkpoint_commit", task_ref]
        return ActionProcessResult(
            command=command,
            returncode=0 if result.ok else 1,
            stdout=json.dumps(result.to_dict(), ensure_ascii=False, sort_keys=True)
            + "\n",
            stderr="",
        )

    def _update_ui_setting(self, fields: Mapping[str, str]) -> ActionProcessResult:
        key = _allowed_ui_setting_key(fields)
        value = _require_field(fields, "value")
        if key == "default_policy":
            _validate_default_policy_value(value, root=self.root)
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

    def _submit_recovered_report(self, fields: Mapping[str, str]) -> ActionProcessResult:
        session_id = _require_field(fields, "session_id")
        try:
            result = submit_recovered_report(
                session_id,
                root=self.root,
                actor=self.actor,
                expected_task_id=_field(fields, "task_id"),
                expected_task_ref=_field(fields, "task_ref"),
            )
        except ReportRecoveryError as exc:
            raise WebActionError(
                "WEB_REPORT_RECOVERY_FAILED",
                str(exc),
                details={
                    "action": "pipeline.report_recovery.submit",
                    "session_id": session_id,
                },
            ) from exc

        command = ["pipeline.report_recovery.submit", session_id]
        return ActionProcessResult(
            command=command,
            returncode=0,
            stdout=json.dumps(result.to_dict(), ensure_ascii=False, sort_keys=True)
            + "\n",
            stderr="",
        )

    def _apply_ui_settings(self, fields: Mapping[str, str]) -> ActionProcessResult:
        values = _allowed_ui_settings_values(fields)
        if "default_policy" in values:
            _validate_default_policy_value(values["default_policy"], root=self.root)
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
    args = ["ui", "run", _task_ref(fields)]
    auto_close_note = _field(fields, "auto_close_note")
    if auto_close_note:
        args.extend(["--auto-close-note", auto_close_note])
    args.append("--confirm")
    return args


def _build_ui_run_task_batch(fields: Mapping[str, str]) -> list[str]:
    args = ["ui.run_task_batch"]
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
                "UI batch max_tasks must be a positive integer.",
                details={"max_tasks": max_tasks},
            )
        args.extend(["--max-tasks", max_tasks])
    order_by = _field(fields, "order_by")
    if order_by:
        if order_by not in PIPELINE_ORDER_OPTIONS:
            raise WebActionError(
                "WEB_INVALID_ACTION_ARGUMENT",
                "UI batch order_by is not allowed: {}".format(order_by),
                details={"order_by": order_by, "allowed": sorted(PIPELINE_ORDER_OPTIONS)},
            )
        args.extend(["--order-by", order_by])
    auto_close_note = _field(fields, "auto_close_note")
    if auto_close_note:
        args.extend(["--auto-close-note", auto_close_note])
    args.append("--confirm")
    return args


def _build_ui_checkpoint_commit(fields: Mapping[str, str]) -> list[str]:
    return ["ui", "checkpoint-commit", _task_ref(fields), "--confirm"]


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


def _validate_default_policy_value(value: str, *, root: str | Path) -> None:
    policy_name = str(value or "")
    if not policy_name:
        raise WebActionError(
            "WEB_UI_DEFAULT_POLICY_REQUIRED",
            "Web UI default_policy must be a registered pipeline policy preset.",
            path="default_policy",
            details={"default_policy": policy_name},
        )
    try:
        load_policy_preset(policy_name, root=root)
    except CommandError as exc:
        if exc.code == "POLICY_PRESET_NOT_FOUND":
            raise WebActionError(
                "WEB_UI_DEFAULT_POLICY_UNKNOWN",
                "Web UI default_policy is not a registered pipeline policy preset: {}".format(
                    policy_name
                ),
                path="default_policy",
                details={"default_policy": policy_name, "source_code": exc.code},
            ) from exc
        raise WebActionError(
            "WEB_UI_DEFAULT_POLICY_INVALID",
            "Web UI default_policy could not be validated: {}".format(policy_name),
            path="default_policy",
            details={"default_policy": policy_name, "source_code": exc.code},
        ) from exc
    except (KeyError, TypeError, ValueError) as exc:
        raise WebActionError(
            "WEB_UI_DEFAULT_POLICY_INVALID",
            "Web UI default_policy is not a valid pipeline policy preset: {}".format(
                policy_name
            ),
            path="default_policy",
            details={"default_policy": policy_name, "error": str(exc)},
        ) from exc


def _require_incomplete_run_confirmation(policy, fields: Mapping[str, str]) -> None:
    max_steps = int(policy.batch.max_steps)
    phase_count = len(RUN_NEXT_PHASE_SEQUENCE)
    if max_steps >= phase_count:
        return
    if _field(fields, INCOMPLETE_RUN_CONFIRM_FIELD).lower() in CONFIRM_VALUES:
        return
    raise WebActionError(
        "WEB_INCOMPLETE_RUN_CONFIRMATION_REQUIRED",
        (
            "Effective Web run policy batch.max_steps is {max_steps}, but a full "
            "pipeline run has {phase_count} phases. Risk: review and close may not "
            "run in one batch. Resume Session can continue the next phase."
        ).format(max_steps=max_steps, phase_count=phase_count),
        path=INCOMPLETE_RUN_CONFIRM_FIELD,
        details={
            "policy": policy.name,
            "max_steps": max_steps,
            "phase_count": phase_count,
            "phase_sequence": list(RUN_NEXT_PHASE_SEQUENCE),
            "required_confirmation": INCOMPLETE_RUN_CONFIRM_FIELD,
        },
    )


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


def _ui_task_batch_requested_inputs(fields: Mapping[str, str]) -> dict[str, Any]:
    max_tasks = _field(fields, "max_tasks")
    order_by = _field(fields, "order_by")
    return {
        "task_ref": _split_values(fields, "task_ref"),
        "epic": _split_values(fields, "epic"),
        "status_filter": _split_values(fields, "status_filter"),
        "max_tasks": max_tasks,
        "order_by": order_by,
        "auto_close_note": _field(fields, "auto_close_note"),
    }


def _parse_json(text: str) -> Any | None:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return None


def _ui_run_selection_not_run_result(
    selection: UIRunSelectionResolution,
) -> CommandResult:
    task_label = selection.task_id or selection.task_ref or "selected task"
    session_id = selection.session_id
    data: dict[str, Any] = {
        "task_ref": selection.task_ref,
        "task_id": selection.task_id,
        "task_status": selection.task_status,
        "outcome": selection.outcome,
        "not_run": True,
        "session_id": session_id,
        "session_status": selection.session_status,
        "session": selection.session_summary() or None,
    }
    if session_id:
        target = "/pipeline/sessions/{}".format(session_id)
        data["session_href"] = target
        data["redirect_target"] = target

    if selection.outcome == "existing_session":
        message = (
            "NOT RUN: selected task {} already has pipeline session {}{}.".format(
                task_label,
                session_id or "(unknown)",
                " ({})".format(selection.session_status)
                if selection.session_status
                else "",
            )
        )
        owner_action = (
            "Open the existing pipeline session instead of starting a duplicate run."
        )
    else:
        message = "NOT RUN: selected task {} is {}.".format(
            task_label,
            selection.task_status or "not executable",
        )
        owner_action = "Select a planned or ready task before starting a Web Run."

    result = CommandResult.success(
        command="ui.run",
        domain="ui",
        message=message,
        data=data,
    )
    result.owner_action_required = owner_action
    if session_id:
        result.next_actions.append("Open pipeline session {}.".format(session_id))
    return result


def _ui_run_worktree_preflight_not_run_result(
    selection: UIRunSelectionResolution,
    preflight: WorktreeDirtyPreflight,
) -> CommandResult:
    task_label = _selected_task_label(selection.task_ref, selection.task_id)
    dirty_paths = list(preflight.dirty_paths)
    reason = preflight.reason
    if reason == "worktree_dirty":
        message = (
            "NOT RUN: Web Run did not start for selected task {} because the "
            "worktree is dirty.".format(task_label)
        )
        checkpoint_action = "Create checkpoint commit for selected task {}.".format(
            task_label
        )
        rerun_action = (
            "After checkpoint commit succeeds, run selected task {} again.".format(
                task_label
            )
        )
        owner_action = (
            "Web Run must start from a clean worktree. {} Or clean the worktree, "
            "then run selected task {} again.".format(checkpoint_action, task_label)
        )
    else:
        message = (
            "NOT RUN: Web Run did not start for selected task {} because git status "
            "could not be checked.".format(task_label)
        )
        checkpoint_action = ""
        rerun_action = ""
        owner_action = "Resolve git status errors, then rerun Web Run."

    data: dict[str, Any] = {
        "task_ref": selection.task_ref,
        "task_id": selection.task_id,
        "selected_task": task_label,
        "task_status": selection.task_status,
        "outcome": reason,
        "reason": reason,
        "not_run": True,
        "stop_code": "WORKTREE_DIRTY"
        if reason == "worktree_dirty"
        else "WORKTREE_STATUS_UNAVAILABLE",
        "blocked_by": "WORKTREE_DIRTY"
        if reason == "worktree_dirty"
        else "WORKTREE_STATUS_UNAVAILABLE",
        "dirty_files": dirty_paths,
        "git_status_entries": [entry.to_dict() for entry in preflight.entries],
        "suggested_checkpoint_commands": list(MANUAL_CHECKPOINT_COMMANDS),
    }
    if checkpoint_action:
        data["checkpoint_action"] = "ui.checkpoint_commit"
        data["next_action"] = "{} {}".format(checkpoint_action, rerun_action)
    if preflight.error:
        data["git_status_error"] = preflight.error

    result = CommandResult.success(
        command="ui.run",
        domain="ui",
        message=message,
        data=data,
    )
    result.owner_action_required = owner_action
    if checkpoint_action:
        result.next_actions.extend([checkpoint_action, rerun_action])
    result.next_actions.extend(MANUAL_CHECKPOINT_COMMANDS)
    return result


def _ui_run_batch_worktree_preflight_not_run_result(
    requested_queue_inputs: Mapping[str, Any],
    preflight: WorktreeDirtyPreflight,
) -> CommandResult:
    dirty_paths = list(preflight.dirty_paths)
    reason = preflight.reason
    batch_label = "task batch"
    if reason == "worktree_dirty":
        message = (
            "NOT RUN: Web Run did not start for task batch because the worktree is "
            "dirty."
        )
        checkpoint_action = "Create checkpoint commit before task batch."
        rerun_action = "After checkpoint commit succeeds, run task batch again."
        owner_action = (
            "Web batch runs must start from a clean worktree. Create a checkpoint "
            "commit or clean the worktree, then run task batch again."
        )
    else:
        message = (
            "NOT RUN: Web Run did not start for task batch because git status could "
            "not be checked."
        )
        checkpoint_action = ""
        rerun_action = ""
        owner_action = "Resolve git status errors, then rerun task batch."

    data: dict[str, Any] = {
        "task_ref": batch_label,
        "selected_task": batch_label,
        "batch_run": True,
        "requested_queue_inputs": dict(requested_queue_inputs),
        "outcome": reason,
        "reason": reason,
        "not_run": True,
        "stop_code": "WORKTREE_DIRTY"
        if reason == "worktree_dirty"
        else "WORKTREE_STATUS_UNAVAILABLE",
        "blocked_by": "WORKTREE_DIRTY"
        if reason == "worktree_dirty"
        else "WORKTREE_STATUS_UNAVAILABLE",
        "dirty_files": dirty_paths,
        "git_status_entries": [entry.to_dict() for entry in preflight.entries],
        "suggested_checkpoint_commands": list(MANUAL_CHECKPOINT_COMMANDS),
    }
    if checkpoint_action:
        data["checkpoint_action"] = "ui.checkpoint_commit"
        data["next_action"] = "{} {}".format(checkpoint_action, rerun_action)
    if preflight.error:
        data["git_status_error"] = preflight.error

    result = CommandResult.success(
        command="ui.run_task_batch",
        domain="ui",
        message=message,
        data=data,
    )
    result.owner_action_required = owner_action
    if checkpoint_action:
        result.next_actions.extend([checkpoint_action, rerun_action])
    result.next_actions.extend(MANUAL_CHECKPOINT_COMMANDS)
    return result


def _selected_task_label(task_ref: str, task_id: str = "") -> str:
    selected_ref = str(task_ref or "").strip()
    selected_id = str(task_id or "").strip()
    if selected_ref and selected_id and selected_ref != selected_id:
        return "{} ({})".format(selected_ref, selected_id)
    return selected_ref or selected_id or "selected task"


def _apply_committed_close_action_view(
    result: CommandResult,
    created_session: Any,
) -> None:
    close_status = _mapping_or_empty(result.data.get("close_status"))
    if not _is_successful_committed_close(close_status):
        return

    session = dict(_mapping_or_empty(result.data.get("session")))
    if not session:
        session = dict(_mapping_or_empty(created_session))
    completed_task_id = str(
        close_status.get("task_id")
        or result.data.get("task_id")
        or result.data.get("current_task_id")
        or session.get("current_task_id")
        or ""
    ).strip()
    commit_hash = str(close_status.get("commit_hash") or "").strip()

    session["status"] = "completed"
    session["stop_reason"] = _committed_close_action_reason(commit_hash)
    if completed_task_id:
        session["current_task_id"] = completed_task_id
    if not session.get("current_step_status"):
        session["current_step_status"] = "passed"

    result.data["session"] = session
    result.data["outcome"] = "completed"
    result.data["session_status"] = "completed"
    result.data.setdefault("stop_code", "QUEUE_COMPLETE")
    result.data.setdefault("stop_reason", session["stop_reason"])
    if completed_task_id:
        result.data["task_id"] = completed_task_id
        result.data.setdefault("current_task_id", completed_task_id)
        _extend_unique(
            result.data.setdefault("completed_tasks", []),
            [completed_task_id],
        )
    result.data["close_outcome"] = str(close_status.get("outcome") or "")
    result.data["commit_status"] = str(close_status.get("commit_status") or "")
    result.data["commit_code"] = str(close_status.get("commit_code") or "")
    result.data["commit_hash"] = commit_hash
    _extend_unique(result.data.setdefault("commits", []), [commit_hash])


def _mapping_or_empty(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _is_successful_committed_close(close_status: Mapping[str, Any]) -> bool:
    commit_hash = str(close_status.get("commit_hash") or "").strip()
    if not commit_hash:
        return False
    return (
        str(close_status.get("outcome") or "").lower()
        == "closed_with_local_commit"
        and str(close_status.get("commit_status") or "").lower() == "pass"
        and str(close_status.get("commit_code") or "") == "LOCAL_COMMIT_CREATED"
    )


def _committed_close_action_reason(commit_hash: str) -> str:
    if commit_hash:
        return "Close passed and local commit {} was created.".format(commit_hash)
    return "Close passed and a local commit was created."


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
    "ui.run_task_batch": WebAction(
        action_id="ui.run_task_batch",
        command_name="ui.run_task_batch",
        label="Run task batch",
        builder=_build_ui_run_task_batch,
    ),
    "ui.checkpoint_commit": WebAction(
        action_id="ui.checkpoint_commit",
        command_name="ui.checkpoint_commit",
        label="Create checkpoint commit",
        builder=_build_ui_checkpoint_commit,
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
    "pipeline.report_recovery.submit": WebAction(
        action_id="pipeline.report_recovery.submit",
        command_name="pipeline.report_recovery.submit",
        label="Submit recovered report",
        builder=lambda fields: [
            "pipeline",
            "report-recovery",
            "submit",
            _require_field(fields, "session_id"),
        ],
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

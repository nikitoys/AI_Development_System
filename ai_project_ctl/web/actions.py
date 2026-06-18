"""Confirmed write actions for the local Web Control Center."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ai_project_ctl.core.registry import command_describe
from ai_project_ctl.core.result import CommandError


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PACKAGE_ROOT / "scripts"

WRITE_KINDS = {"write", "render"}
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
        return payload


def available_actions() -> list[dict[str, Any]]:
    """Return safe write actions for rendering and discovery."""

    rows = []
    for action in ACTIONS.values():
        descriptor = require_web_write_command(action.command_name)
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
    if descriptor.get("kind") not in WRITE_KINDS:
        raise WebActionError(
            "WEB_ACTION_COMMAND_NOT_WRITE",
            "Web action command is not a registered write/render command: {}".format(
                command_name
            ),
            details={"command": command_name, "kind": descriptor.get("kind")},
        )
    if not any(
        bool(read_write.get(flag))
        for flag in ("mutates_state", "writes_events", "renders_generated")
    ):
        raise WebActionError(
            "WEB_ACTION_COMMAND_HAS_NO_WRITE_EFFECT",
            "Web action command does not declare a controlled write effect: {}".format(
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
        if _field(fields, "confirm").lower() not in CONFIRM_VALUES:
            raise WebActionError(
                "WEB_ACTION_CONFIRMATION_REQUIRED",
                "Write action requires explicit confirmation.",
                details={"action": action_id},
            )

        try:
            action = ACTIONS[action_id]
        except KeyError as exc:
            raise WebActionError(
                "WEB_UNKNOWN_ACTION",
                "Unknown or unsupported web write action: {}".format(action_id),
                details={"action": action_id},
            ) from exc

        descriptor = require_web_write_command(action.command_name)
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


def _build_current_set(fields: Mapping[str, str]) -> list[str]:
    return ["current", "set", _task_ref(fields)]


def _build_current_clear(fields: Mapping[str, str]) -> list[str]:
    return ["current", "clear"]


def _build_project_render(fields: Mapping[str, str]) -> list[str]:
    return ["project", "render"]


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


def _task_ref(fields: Mapping[str, str]) -> str:
    return _field(fields, "task") or _require_field(fields, "task_id")


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


def _parse_json(text: str) -> Any | None:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return None


ACTIONS: dict[str, WebAction] = {
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
}

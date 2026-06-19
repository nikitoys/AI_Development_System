"""Project-control read data for the local Web Control Center."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import threading
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from ai_project_ctl.core.paths import ProjectPaths
from ai_project_ctl.core.registry import command_describe, command_list
from ai_project_ctl.core.result import CommandError
from ai_project_ctl.core.workflows import workflow_list


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PACKAGE_ROOT / "scripts"

READ_ONLY_KINDS = {"read", "validation", "audit", "utility"}
DOCTOR_CACHE_TTL_SECONDS = 20.0

GENERATED_VIEW_FILES = (
    "CODEX_CURRENT.md",
    "CODEX_TASKS.md",
    "TASK_EXECUTION_QUEUE.md",
    "CODEX_STATUS.md",
    "CODEX_PROMPT.md",
    "CONTEXT_STATUS.md",
    "CONTEXT_PACK.md",
    "EVOLUTION.md",
    "CODEX_PLAN.md",
    "DOCS_INDEX.md",
    "DOCS_GAPS.md",
)

AUDIT_COMMANDS = (
    ("plan", "planctl.py", ("audit",)),
    ("task", "taskctl.py", ("audit",)),
    ("doc", "docctl.py", ("audit",)),
    ("context", "contextctl.py", ("audit",)),
    ("evolution", "evolutionctl.py", ("audit",)),
)

EXECUTABLE_QUEUE_STATUSES = (
    "ready",
    "in_progress",
    "blocked",
    "in_review",
    "changes_requested",
)


class WebControlError(CommandError):
    """Stable web-control read error."""


@dataclass(frozen=True)
class ProcessResult:
    """Captured read command output."""

    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


@dataclass(frozen=True)
class DoctorCacheEntry:
    """One cached project doctor result."""

    data: dict[str, Any]
    captured_at: datetime
    captured_monotonic: float


def require_read_only_command(command_name: str) -> dict[str, Any]:
    """Return command metadata only when it cannot mutate project state."""

    descriptor = command_describe(command_name)
    read_write = descriptor.get("read_write") or {}
    if descriptor.get("availability") != "implemented":
        raise WebControlError(
            "WEB_COMMAND_NOT_IMPLEMENTED",
            "Web read model cannot execute planned command: {}".format(command_name),
            details={"command": command_name},
        )
    if descriptor.get("kind") not in READ_ONLY_KINDS:
        raise WebControlError(
            "WEB_COMMAND_NOT_READ_ONLY",
            "Web read model command is not read-only: {}".format(command_name),
            details={"command": command_name, "kind": descriptor.get("kind")},
        )
    if any(
        bool(read_write.get(flag))
        for flag in ("mutates_state", "writes_events", "renders_generated")
    ):
        raise WebControlError(
            "WEB_COMMAND_MUTATES_STATE",
            "Web read model command can mutate project-control files: {}".format(
                command_name
            ),
            details={"command": command_name, "read_write": read_write},
        )
    return descriptor


def _parse_json_output(text: str, *, command: Sequence[str]) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise WebControlError(
            "WEB_INVALID_JSON",
            "Read-only command did not return valid JSON.",
            details={"command": list(command), "error": str(exc), "stdout": text},
        ) from exc


def _iso_mtime(path: Path) -> str:
    return (
        datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _first_heading(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:140]
    return ""


def _task_sort_key(task: Mapping[str, Any]) -> tuple[str, int, str]:
    return (
        str(task.get("epic_id") or ""),
        int(task.get("order") or 0),
        str(task.get("id") or ""),
    )


def _epic_sort_key(epic: Mapping[str, Any]) -> tuple[str, int, str]:
    return (
        str(epic.get("initiative_id") or ""),
        int(epic.get("order") or 0),
        str(epic.get("id") or ""),
    )


def _initiative_sort_key(initiative: Mapping[str, Any]) -> tuple[int, str]:
    return (
        int(initiative.get("order") or 0),
        str(initiative.get("id") or ""),
    )


class ReadOnlyProjectModel:
    """Build page data without writing protected project-control files."""

    def __init__(
        self,
        root: str | Path = ".",
        *,
        actor: str = "human_owner",
        python_executable: str | None = None,
        doctor_ttl_seconds: float = DOCTOR_CACHE_TTL_SECONDS,
    ) -> None:
        self.paths = ProjectPaths.from_root(root)
        self.actor = actor
        self.python_executable = python_executable or sys.executable
        self.doctor_ttl_seconds = doctor_ttl_seconds
        self._cache_lock = threading.Lock()
        self._doctor_cache: DoctorCacheEntry | None = None

    @property
    def root(self) -> Path:
        return self.paths.root

    def dashboard(
        self,
        *,
        refresh_doctor: bool = False,
        include_events: bool = False,
    ) -> dict[str, Any]:
        tasks = self.tasks()
        current_task = self.current_task(tasks)
        initiatives = self.initiatives()
        epics = self.epics()
        doctor = self.doctor(refresh=refresh_doctor)
        generated = self.generated_views()
        events = self.audit_events(last=5) if include_events else []
        commands = command_list(include_planned=True)
        return {
            "root": str(self.root),
            "current_task": current_task,
            "tasks": tasks,
            "task_counts": dict(Counter(task.get("status", "unknown") for task in tasks)),
            "queue": self.executable_queue(tasks),
            "initiatives": initiatives,
            "epics": epics,
            "epic_counts": dict(Counter(epic.get("status", "unknown") for epic in epics)),
            "doctor": doctor,
            "generated": generated,
            "events": events,
            "events_loaded": include_events,
            "workflows": workflow_list(),
            "review_commands": [
                command for command in commands if command.get("domain") == "review"
            ],
            "read_only": {
                "methods": ["GET", "HEAD"],
                "blocked_methods": ["PUT", "PATCH", "DELETE"],
                "write_actions": True,
                "write_route": "/actions",
            },
        }

    def tasks(self) -> list[dict[str, Any]]:
        state = self._state_json("tasks.json")
        tasks = state.get("tasks")
        if not isinstance(tasks, list):
            return []
        return sorted(
            [dict(task) for task in tasks if isinstance(task, dict)],
            key=_task_sort_key,
        )

    def current_task(self, tasks: Sequence[Mapping[str, Any]] | None = None) -> dict[str, Any]:
        state = self._state_json("tasks.json")
        current_task_id = state.get("current_task_id")
        if current_task_id:
            for task in tasks or state.get("tasks", []):
                if task.get("id") == current_task_id:
                    return dict(task)

        for task in tasks or ():
            if task.get("status") == "in_progress":
                return dict(task)
        return {}

    def epics(self) -> list[dict[str, Any]]:
        state = self._state_json("plan.json")
        epics = state.get("epics")
        if not isinstance(epics, list):
            return []
        return sorted(
            [dict(epic) for epic in epics if isinstance(epic, dict)],
            key=_epic_sort_key,
        )

    def initiatives(self) -> list[dict[str, Any]]:
        state = self._state_json("plan.json")
        initiatives = state.get("initiatives")
        if not isinstance(initiatives, list):
            return []
        return sorted(
            [dict(initiative) for initiative in initiatives if isinstance(initiative, dict)],
            key=_initiative_sort_key,
        )

    def doctor(self, *, refresh: bool = False) -> dict[str, Any]:
        if refresh:
            data = self._run_doctor()
            entry = DoctorCacheEntry(
                data=copy.deepcopy(data),
                captured_at=datetime.now(timezone.utc).replace(microsecond=0),
                captured_monotonic=time.monotonic(),
            )
            with self._cache_lock:
                self._doctor_cache = entry
            return self._doctor_payload(entry)

        with self._cache_lock:
            entry = self._doctor_cache
        if entry is None:
            return self._empty_doctor_payload()
        return self._doctor_payload(entry)

    def invalidate_caches(self) -> None:
        """Clear read-model caches after controlled project-control writes."""

        with self._cache_lock:
            self._doctor_cache = None

    def _run_doctor(self) -> dict[str, Any]:
        payload = self._facade_json("project.doctor", ("project", "doctor"))
        if isinstance(payload, dict):
            data = payload.get("data")
            if isinstance(data, dict):
                return dict(data)
        return {}

    def _doctor_payload(self, entry: DoctorCacheEntry) -> dict[str, Any]:
        payload = copy.deepcopy(entry.data)
        age_seconds = max(0.0, time.monotonic() - entry.captured_monotonic)
        payload["cache"] = {
            "cached": True,
            "generated_at": entry.captured_at.isoformat().replace("+00:00", "Z"),
            "age_seconds": round(age_seconds, 3),
            "ttl_seconds": self.doctor_ttl_seconds,
            "stale": age_seconds > self.doctor_ttl_seconds,
        }
        return payload

    def _empty_doctor_payload(self) -> dict[str, Any]:
        return {
            "overall_status": "UNKNOWN",
            "summary": {"PASS": 0, "WARN": 0, "FAIL": 0},
            "root": str(self.root),
            "findings": [],
            "cache": {
                "cached": False,
                "generated_at": "",
                "age_seconds": None,
                "ttl_seconds": self.doctor_ttl_seconds,
                "stale": True,
            },
        }

    def _state_json(self, name: str) -> dict[str, Any]:
        path = self.paths.state_file(name)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise WebControlError(
                "WEB_STATE_FILE_MISSING",
                "Project-control state file is missing: {}".format(path),
                details={"path": str(path)},
            ) from exc
        except json.JSONDecodeError as exc:
            raise WebControlError(
                "WEB_INVALID_STATE_JSON",
                "Project-control state file is not valid JSON: {}".format(path),
                details={"path": str(path), "error": str(exc)},
            ) from exc
        if not isinstance(payload, dict):
            raise WebControlError(
                "WEB_INVALID_STATE_SHAPE",
                "Project-control state file must contain a JSON object: {}".format(path),
                details={"path": str(path)},
            )
        return payload

    def executable_queue(
        self,
        tasks: Sequence[Mapping[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        selected = [
            dict(task)
            for task in (tasks if tasks is not None else self.tasks())
            if task.get("status") in EXECUTABLE_QUEUE_STATUSES
        ]
        return sorted(
            selected,
            key=lambda task: (
                str(task.get("epic_key") or task.get("epic_id") or ""),
                int(task.get("local_seq") or task.get("order") or 0),
                str(task.get("id") or ""),
            ),
        )

    def generated_views(self) -> list[dict[str, Any]]:
        views = []
        for name in GENERATED_VIEW_FILES:
            path = self.paths.generated_file(name)
            item: dict[str, Any] = {
                "name": name,
                "label": "AI_PROJECT/generated/{}".format(name),
                "derived": True,
                "exists": path.exists(),
                "size": 0,
                "mtime": "",
                "heading": "",
                "preview": "",
            }
            if path.exists():
                text = _read_text(path)
                item.update(
                    {
                        "size": path.stat().st_size,
                        "mtime": _iso_mtime(path),
                        "heading": _first_heading(text),
                        "preview": "\n".join(text.splitlines()[:12]),
                    }
                )
            views.append(item)
        return views

    def audit_events(self, *, last: int = 10) -> list[dict[str, Any]]:
        events = []
        for domain, script_name, base_args in AUDIT_COMMANDS:
            result = self._script_text(script_name, (*base_args, "--last", str(last)))
            events.append(
                {
                    "domain": domain,
                    "command": " ".join(result.command),
                    "ok": result.ok,
                    "lines": [line for line in result.stdout.splitlines() if line.strip()],
                    "error": result.stderr.strip(),
                }
            )
        return events

    def command_catalog(self) -> list[dict[str, Any]]:
        return command_list(include_planned=True)

    def _facade_json(self, command_name: str, args: Sequence[str]) -> Any:
        require_read_only_command(command_name)
        result = self._run(
            [
                self.python_executable,
                str(SCRIPTS_DIR / "aictl.py"),
                "--root",
                str(self.root),
                "--actor",
                self.actor,
                "--json",
                *args,
            ]
        )
        if not result.ok:
            raise WebControlError(
                "WEB_READ_COMMAND_FAILED",
                "Read-only facade command failed: {}".format(command_name),
                details={
                    "command": result.command,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                },
            )
        return _parse_json_output(result.stdout, command=result.command)

    def _script_text(self, script_name: str, args: Sequence[str]) -> ProcessResult:
        return self._run(
            [
                self.python_executable,
                str(SCRIPTS_DIR / script_name),
                "--root",
                str(self.root),
                "--actor",
                self.actor,
                *args,
            ]
        )

    def _run(self, command: Sequence[str]) -> ProcessResult:
        completed = subprocess.run(
            list(command),
            cwd=str(PACKAGE_ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return ProcessResult(
            command=list(command),
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        return ""

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
from ai_project_ctl.core.workflows import (
    CHANGE_ACCEPTABLE_STATUSES,
    CHANGE_APPROVE_REQUIRED_STATUS,
    CHANGE_DONE_TASK_STATUSES,
    CHANGE_REVIEWABLE_STATUSES,
    EPIC_CLOSED_TASK_STATUSES,
    EPIC_CLOSABLE_STATUSES,
    workflow_list,
)


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

COMMIT_COMPLETED_TASK_STATUSES = {"done"}
COMMIT_ACCEPTED_CHANGE_STATUSES = {"accepted"}

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
TASK_PREPARE_STATUSES = {"planned", "ready", "changes_requested"}
TASK_DEPENDENCY_SATISFIED_STATUSES = {"done"}
TASK_APPROVED_CHANGE_STATUSES = {"approved", "in_review", "accepted"}
CHANGE_CLOSED_STATUSES = {"accepted", "rejected", "archived"}


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


def _change_sort_key(change: Mapping[str, Any]) -> tuple[int, str]:
    return (
        int(change.get("order") or 0),
        str(change.get("id") or ""),
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
        latest_reports = self.latest_task_reports_by_task()
        tasks = attach_latest_task_reports(tasks, latest_reports)
        current_task = self.current_task(tasks)
        initiatives = self.initiatives()
        epics = self.epics()
        changes = self.changes()
        execution = self.execution_status()
        tasks_revision = self._state_revision("tasks.json")
        docs_revision = self._state_revision("docs.json")
        tasks = task_hints(
            tasks,
            current_task=current_task,
            changes=changes,
            execution=execution,
            tasks_revision=tasks_revision,
            docs_revision=docs_revision,
        )
        current_task = _enriched_current_task(current_task, tasks)
        execution_context = execution_context_summary(
            current_task,
            execution,
            tasks_revision=tasks_revision,
            docs_revision=docs_revision,
            root=self.root,
        )
        epics = epic_hints(epics, tasks, changes)
        changes = change_hints(changes, tasks)
        doctor = self.doctor(refresh=refresh_doctor)
        generated = self.generated_views()
        health = project_health_summary(
            doctor,
            generated,
            execution_context=execution_context,
            current_task=current_task,
        )
        events = self.audit_events(last=5) if include_events else []
        commands = command_list(include_planned=True)
        return {
            "root": str(self.root),
            "current_task": current_task,
            "tasks": tasks,
            "task_reports": self.task_reports(),
            "task_counts": dict(Counter(task.get("status", "unknown") for task in tasks)),
            "queue": self.executable_queue(tasks),
            "initiatives": initiatives,
            "epics": epics,
            "epic_counts": dict(Counter(epic.get("status", "unknown") for epic in epics)),
            "changes": changes,
            "change_counts": dict(
                Counter(change.get("status", "unknown") for change in changes)
            ),
            "doctor": doctor,
            "health": health,
            "execution": execution,
            "execution_context": execution_context,
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

    def changes(self) -> list[dict[str, Any]]:
        try:
            state = self._state_json("evolution.json")
        except WebControlError as exc:
            if exc.code == "WEB_STATE_FILE_MISSING":
                return []
            raise
        changes = state.get("changes")
        if not isinstance(changes, list):
            return []
        return sorted(
            [dict(change) for change in changes if isinstance(change, dict)],
            key=_change_sort_key,
        )

    def task_reports(self) -> list[dict[str, Any]]:
        try:
            state = self._state_json("task_reports.json")
        except WebControlError as exc:
            if exc.code == "WEB_STATE_FILE_MISSING":
                return []
            raise
        reports = state.get("reports")
        if not isinstance(reports, list):
            return []
        return [dict(report) for report in reports if isinstance(report, dict)]

    def latest_task_reports_by_task(self) -> dict[str, dict[str, Any]]:
        try:
            state = self._state_json("task_reports.json")
        except WebControlError as exc:
            if exc.code == "WEB_STATE_FILE_MISSING":
                return {}
            raise
        reports = [
            dict(report)
            for report in state.get("reports", [])
            if isinstance(report, dict)
        ]
        reports_by_id = {
            str(report.get("id") or ""): report
            for report in reports
            if str(report.get("id") or "")
        }
        latest: dict[str, dict[str, Any]] = {}
        latest_by_task = state.get("latest_by_task")
        if isinstance(latest_by_task, Mapping):
            for task_id, report_id in latest_by_task.items():
                report = reports_by_id.get(str(report_id or ""))
                if report:
                    latest[str(task_id)] = _task_report_summary(report)

        for report in reports:
            task_id = str(report.get("task_id") or "")
            if task_id and task_id not in latest:
                latest[task_id] = _task_report_summary(report)
        return latest

    def execution_status(self) -> dict[str, Any]:
        try:
            return self._state_json("current_execution.json")
        except WebControlError as exc:
            if exc.code == "WEB_STATE_FILE_MISSING":
                return {
                    "status": "missing",
                    "code": "CODEX_STATUS_MISSING",
                    "prompt_exists": False,
                    "source_type": "",
                    "source_id": "",
                    "source_status": "",
                    "blocked_reason": "No current Codex prompt state exists.",
                    "context_pack": {},
                }
            raise

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

    def _state_revision(self, name: str) -> int | None:
        try:
            revision = self._state_json(name).get("revision")
        except WebControlError as exc:
            if exc.code == "WEB_STATE_FILE_MISSING":
                return None
            raise
        return int(revision) if isinstance(revision, int) else None

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

    def commit_readiness(self, *, refresh_doctor: bool = False) -> dict[str, Any]:
        """Return a read-only readiness snapshot for a human-run git commit."""

        tasks = self.tasks()
        changes = self.changes()
        doctor = self.doctor(refresh=refresh_doctor)
        git = self.git_status()
        completed_tasks = _recent_completed_tasks(tasks)
        accepted_changes = _recent_accepted_changes(changes)
        validation = _commit_validation_sections(doctor)
        status, message = _commit_readiness_status(git, doctor, validation)
        return {
            "root": str(self.root),
            "status": status,
            "message": message,
            "git": git,
            "doctor": doctor,
            "validation": validation,
            "completed_tasks": completed_tasks,
            "accepted_changes": accepted_changes,
            "suggested_commit_message": _suggest_commit_message(
                completed_tasks,
                accepted_changes,
            ),
        }

    def git_status(self) -> dict[str, Any]:
        """Read git porcelain status without running any write-capable git command."""

        command = ["git", "status", "--short", "--untracked-files=all"]
        result = self._run_at_root(command, cwd=self.root)
        if not result.ok:
            return {
                "status": "unavailable",
                "message": result.stderr.strip()
                or result.stdout.strip()
                or "Git status is unavailable.",
                "changed_files": [],
                "command": " ".join(command),
            }
        changed_files = _parse_git_short_status(result.stdout)
        if changed_files:
            return {
                "status": "changed",
                "message": "{} changed file(s).".format(len(changed_files)),
                "changed_files": changed_files,
                "command": " ".join(command),
            }
        return {
            "status": "clean",
            "message": "No changed files reported by git status.",
            "changed_files": [],
            "command": " ".join(command),
        }

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
        return self._run_at_root(command, cwd=PACKAGE_ROOT)

    def _run_at_root(self, command: Sequence[str], *, cwd: Path) -> ProcessResult:
        completed = subprocess.run(
            list(command),
            cwd=str(cwd),
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


def task_hints(
    tasks: Sequence[Mapping[str, Any]],
    *,
    current_task: Mapping[str, Any],
    changes: Sequence[Mapping[str, Any]],
    execution: Mapping[str, Any],
    tasks_revision: int | None,
    docs_revision: int | None,
) -> list[dict[str, Any]]:
    tasks_by_ref = _tasks_by_ref(tasks)
    enriched = []
    for task in tasks:
        item = dict(task)
        item["pipeline_hints"] = _task_pipeline_hints(
            item,
            tasks_by_ref=tasks_by_ref,
            current_task=current_task,
            changes=changes,
            execution=execution,
            tasks_revision=tasks_revision,
            docs_revision=docs_revision,
        )
        enriched.append(item)
    return enriched


def attach_latest_task_reports(
    tasks: Sequence[Mapping[str, Any]],
    latest_reports: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    enriched = []
    for task in tasks:
        item = dict(task)
        report = latest_reports.get(str(task.get("id") or ""))
        if report:
            item["latest_report"] = dict(report)
        enriched.append(item)
    return enriched


def change_hints(
    changes: Sequence[Mapping[str, Any]],
    tasks: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    tasks_by_ref = _tasks_by_ref(tasks)
    enriched = []
    for change in changes:
        item = dict(change)
        item["pipeline_hints"] = _change_pipeline_hints(item, tasks_by_ref)
        enriched.append(item)
    return enriched


def epic_hints(
    epics: Sequence[Mapping[str, Any]],
    tasks: Sequence[Mapping[str, Any]],
    changes: Sequence[Mapping[str, Any]] = (),
) -> list[dict[str, Any]]:
    enriched = []
    for epic in epics:
        item = dict(epic)
        child_tasks = [
            task
            for task in tasks
            if str(task.get("epic_id") or "") == str(epic.get("id") or "")
        ]
        hints = _epic_pipeline_hints(item, child_tasks, changes)
        item["pipeline_hints"] = hints
        item["task_completion"] = hints["completion"]
        enriched.append(item)
    return enriched


def _task_pipeline_hints(
    task: Mapping[str, Any],
    *,
    tasks_by_ref: Mapping[str, Mapping[str, Any]],
    current_task: Mapping[str, Any],
    changes: Sequence[Mapping[str, Any]],
    execution: Mapping[str, Any],
    tasks_revision: int | None,
    docs_revision: int | None,
) -> dict[str, Any]:
    status = str(task.get("status") or "unknown")
    blockers = _blocking_dependencies(task, tasks_by_ref)
    linked_changes = _linked_changes_for_task(task, changes)
    requires_change = _task_requires_change(task, linked_changes)
    change_blocker = _task_change_blocker(requires_change, linked_changes)
    current_blocker = _current_task_blocker(task, current_task)
    context_reason = _execution_stale_reason(
        task,
        execution,
        tasks_revision=tasks_revision,
        docs_revision=docs_revision,
    )

    prepare_reasons = []
    if status not in TASK_PREPARE_STATUSES:
        prepare_reasons.append("task status is {}".format(status))
    prepare_reasons.extend(blockers)
    if change_blocker:
        prepare_reasons.append(change_blocker)
    if current_blocker:
        prepare_reasons.append(current_blocker)

    submit_reasons = []
    if status != "in_progress":
        submit_reasons.append("task status is {}".format(status))
    elif context_reason:
        submit_reasons.append(context_reason)

    close_reasons = []
    if status != "in_review":
        close_reasons.append("task status is {}".format(status))

    refresh_available = status == "in_progress" or (
        status == "in_review"
        and bool(context_reason)
        and _is_same_task(task, current_task)
    )
    refresh_reason = ""
    if not refresh_available:
        if status not in {"in_progress", "in_review"}:
            refresh_reason = "task status is {}".format(status)
        elif not _is_same_task(task, current_task):
            refresh_reason = current_blocker or "no current task is selected"
        else:
            refresh_reason = "execution context is ready"

    actions = [
        _action_hint(
            "Create Change",
            "evolution.create_for_task",
            requires_change and not linked_changes,
            _create_change_reason(requires_change, linked_changes),
        ),
        _action_hint(
            "Approve Change",
            "evolution.approve_change",
            any(str(change.get("status") or "") == "ready" for change in linked_changes),
            _approve_change_reason(requires_change, linked_changes),
        ),
        _action_hint(
            "Prepare for Codex",
            "task.prepare_for_codex",
            not prepare_reasons,
            "; ".join(prepare_reasons),
        ),
        _action_hint(
            "Refresh Context",
            "task.refresh_execution_context",
            refresh_available,
            refresh_reason,
        ),
        _action_hint(
            "Submit for Review",
            "task.submit_for_review",
            not submit_reasons,
            "; ".join(submit_reasons),
        ),
        _action_hint(
            "Approve & Done",
            "task.close_reviewed",
            not close_reasons,
            "; ".join(close_reasons),
        ),
        _action_hint(
            "Accept Change",
            "evolution.accept_change",
            status == "done"
            and any(
                str(change.get("status") or "") in CHANGE_ACCEPTABLE_STATUSES
                for change in linked_changes
            ),
            _task_accept_change_reason(status, linked_changes, requires_change),
        ),
    ]
    blocked_reasons = [
        "{} unavailable: {}".format(action["label"], action["reason"])
        for action in actions
        if not action["available"] and action["reason"]
    ]
    next_actions = _task_next_actions(
        task,
        actions,
        linked_changes,
        requires_change=requires_change,
        context_reason=context_reason,
    )
    return {
        "next_actions": next_actions,
        "blocked_reasons": blocked_reasons,
        "actions": actions,
        "dependencies": {
            "blocked": bool(blockers),
            "blocking": blockers,
        },
        "linked_changes": [_change_summary(change) for change in linked_changes],
        "requires_evolution_change": requires_change,
        "context": {
            "stale": bool(context_reason),
            "reason": context_reason,
        },
    }


def _change_pipeline_hints(
    change: Mapping[str, Any],
    tasks_by_ref: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    status = str(change.get("status") or "unknown")
    linked_task_reasons = _change_linked_task_blockers(change, tasks_by_ref)
    approve_reason = (
        "" if status == CHANGE_APPROVE_REQUIRED_STATUS else "change status is {}".format(status)
    )
    move_reason = (
        ""
        if status in CHANGE_REVIEWABLE_STATUSES and status != "in_review"
        else "change status is {}".format(status)
    )
    accept_reasons = []
    if status not in CHANGE_ACCEPTABLE_STATUSES:
        accept_reasons.append("change status is {}".format(status))
    accept_reasons.extend(linked_task_reasons)
    actions = [
        _action_hint(
            "Approve Change",
            "evolution.approve_change",
            status == CHANGE_APPROVE_REQUIRED_STATUS,
            approve_reason,
        ),
        _action_hint(
            "Move to Review",
            "evolution.move_to_review",
            status in CHANGE_REVIEWABLE_STATUSES and status != "in_review",
            move_reason,
        ),
        _action_hint(
            "Accept Change",
            "evolution.accept_change",
            status in CHANGE_ACCEPTABLE_STATUSES and not linked_task_reasons,
            "; ".join(accept_reasons),
        ),
    ]
    blocked_reasons = [
        "{} unavailable: {}".format(action["label"], action["reason"])
        for action in actions
        if not action["available"] and action["reason"]
    ]
    return {
        "next_actions": [action["label"] for action in actions if action["available"]],
        "blocked_reasons": blocked_reasons,
        "actions": actions,
        "linked_task_blockers": linked_task_reasons,
    }


def _epic_pipeline_hints(
    epic: Mapping[str, Any],
    child_tasks: Sequence[Mapping[str, Any]],
    changes: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    status = str(epic.get("status") or "unknown")
    completion = _epic_task_completion(child_tasks)
    open_changes = _epic_open_changes(child_tasks, changes)
    blockers = []
    if status not in EPIC_CLOSABLE_STATUSES:
        blockers.append("epic status is {}".format(status))
    blockers.extend(
        "{} status is {}".format(task["ref"], task["status"])
        for task in completion["incomplete_tasks"]
    )
    action = _action_hint(
        "Close Epic If Complete",
        "epic.close_if_complete",
        not blockers,
        "; ".join(blockers),
    )
    return {
        "next_actions": ["Close Epic If Complete"] if action["available"] else [],
        "blocked_reasons": [
            "Close Epic If Complete unavailable: {}".format(action["reason"])
        ]
        if action["reason"]
        else [],
        "actions": [action],
        "completion": completion,
        "linked_changes": [_change_summary(change) for change in open_changes],
    }


def _epic_task_completion(
    child_tasks: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    counts = Counter(str(task.get("status") or "unknown") for task in child_tasks)
    closed = sum(counts.get(status, 0) for status in EPIC_CLOSED_TASK_STATUSES)
    incomplete = [
        {
            "id": str(task.get("id") or ""),
            "ref": _task_display_ref(task),
            "status": str(task.get("status") or "unknown"),
            "title": str(task.get("title") or ""),
        }
        for task in child_tasks
        if str(task.get("status") or "") not in EPIC_CLOSED_TASK_STATUSES
    ]
    total = len(child_tasks)
    return {
        "total": total,
        "closed": closed,
        "open": total - closed,
        "counts": dict(counts),
        "incomplete_tasks": incomplete,
    }


def _epic_open_changes(
    child_tasks: Sequence[Mapping[str, Any]],
    changes: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    child_refs: set[str] = set()
    for task in child_tasks:
        child_refs.update(_task_refs(task))
    if not child_refs:
        return []

    linked = []
    seen: set[str] = set()
    for change in changes:
        status = str(change.get("status") or "unknown")
        if status in CHANGE_CLOSED_STATUSES:
            continue
        if not child_refs.intersection(_string_list(change.get("linked_tasks"))):
            continue
        change_id = str(change.get("id") or "")
        dedupe_key = change_id or repr(sorted(change.items()))
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        linked.append(change)
    return linked


def _task_next_actions(
    task: Mapping[str, Any],
    actions: Sequence[Mapping[str, Any]],
    linked_changes: Sequence[Mapping[str, Any]],
    *,
    requires_change: bool,
    context_reason: str,
) -> list[str]:
    available = {str(action["label"]): bool(action["available"]) for action in actions}
    status = str(task.get("status") or "")
    if requires_change and not linked_changes and available.get("Create Change"):
        return ["Create Change"]
    if available.get("Approve Change"):
        return ["Approve Change"]
    if available.get("Prepare for Codex"):
        return ["Prepare for Codex"]
    if status == "in_progress":
        if context_reason and available.get("Refresh Context"):
            return ["Refresh Context"]
        if available.get("Submit for Review"):
            return ["Submit for Review"]
    if status == "in_review" and context_reason and available.get("Refresh Context"):
        return ["Refresh Context"]
    if available.get("Approve & Done"):
        return ["Approve & Done"]
    if available.get("Accept Change"):
        return ["Accept Change"]
    return []


def _action_hint(label: str, action: str, available: bool, reason: str) -> dict[str, Any]:
    return {
        "label": label,
        "action": action,
        "available": bool(available),
        "reason": reason,
    }


def _blocking_dependencies(
    task: Mapping[str, Any],
    tasks_by_ref: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    blockers = []
    for dependency in _dependency_refs(task):
        dep_task = tasks_by_ref.get(dependency)
        if dep_task is None:
            blockers.append("{} missing".format(dependency))
            continue
        status = str(dep_task.get("status") or "unknown")
        if status not in TASK_DEPENDENCY_SATISFIED_STATUSES:
            blockers.append("{} status is {}".format(_task_display_ref(dep_task), status))
    return blockers


def _dependency_refs(task: Mapping[str, Any]) -> list[str]:
    refs = []
    for key in ("depends_on", "dependencies"):
        value = task.get(key)
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            continue
        for dependency in value:
            if isinstance(dependency, Mapping):
                ref = str(
                    dependency.get("task_id")
                    or dependency.get("task")
                    or dependency.get("id")
                    or dependency.get("ref")
                    or ""
                )
            else:
                ref = str(dependency or "")
            if ref:
                refs.append(ref)
    return refs


def _linked_changes_for_task(
    task: Mapping[str, Any],
    changes: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    refs = _task_refs(task)
    linked = []
    for change in changes:
        linked_tasks = set(_string_list(change.get("linked_tasks")))
        if refs.intersection(linked_tasks):
            linked.append(change)
    return linked


def _task_requires_change(
    task: Mapping[str, Any],
    linked_changes: Sequence[Mapping[str, Any]],
) -> bool:
    if linked_changes:
        return True
    text_parts = []
    for key in ("title", "summary", "description", "active_document", "expected_result"):
        text_parts.append(str(task.get(key) or ""))
    for key in ("notes", "scope", "acceptance_criteria"):
        text_parts.extend(_string_list(task.get(key)))
    text = " ".join(text_parts).lower()
    return (
        "requires approved evolution change" in text
        or "requires an approved evolution change" in text
        or "requires an explicit evolution change" in text
        or "evolution change proposal before implementation" in text
    )


def _task_change_blocker(
    requires_change: bool,
    linked_changes: Sequence[Mapping[str, Any]],
) -> str:
    if not requires_change:
        return ""
    if not linked_changes:
        return "linked Evolution Change is missing"
    approved = [
        change
        for change in linked_changes
        if str(change.get("status") or "") in TASK_APPROVED_CHANGE_STATUSES
    ]
    if approved:
        return ""
    return "linked Change {} needs approval".format(
        ", ".join(
            "{} {}".format(change.get("id") or "", change.get("status") or "unknown").strip()
            for change in linked_changes
        )
    )


def _create_change_reason(
    requires_change: bool,
    linked_changes: Sequence[Mapping[str, Any]],
) -> str:
    if not requires_change:
        return ""
    if linked_changes:
        return "linked Evolution Change already exists"
    return ""


def _approve_change_reason(
    requires_change: bool,
    linked_changes: Sequence[Mapping[str, Any]],
) -> str:
    if not requires_change and not linked_changes:
        return ""
    if not linked_changes:
        return "linked Evolution Change is missing"
    statuses = ", ".join(
        "{} {}".format(change.get("id") or "", change.get("status") or "unknown").strip()
        for change in linked_changes
    )
    return "no linked Change is ready for approval ({})".format(statuses)


def _task_accept_change_reason(
    task_status: str,
    linked_changes: Sequence[Mapping[str, Any]],
    requires_change: bool,
) -> str:
    if not requires_change and not linked_changes:
        return ""
    if task_status != "done":
        return "task status is {}".format(task_status)
    if not linked_changes:
        return "linked Evolution Change is missing"
    statuses = ", ".join(
        "{} {}".format(change.get("id") or "", change.get("status") or "unknown").strip()
        for change in linked_changes
    )
    return "no linked Change is ready for acceptance ({})".format(statuses)


def _current_task_blocker(
    task: Mapping[str, Any],
    current_task: Mapping[str, Any],
) -> str:
    current_id = str(current_task.get("id") or "")
    task_id = str(task.get("id") or "")
    if not current_id or not task_id or current_id == task_id:
        return ""
    return "another current task is {}".format(_task_display_ref(current_task))


def _is_same_task(task: Mapping[str, Any], other: Mapping[str, Any]) -> bool:
    return bool(_task_refs(task).intersection(_task_refs(other)))


def _execution_stale_reason(
    task: Mapping[str, Any],
    execution: Mapping[str, Any],
    *,
    tasks_revision: int | None,
    docs_revision: int | None,
) -> str:
    if not execution or str(execution.get("status") or "") == "missing":
        return "no current Codex prompt state exists"
    if str(execution.get("status") or "").lower() != "ready":
        return str(execution.get("blocked_reason") or "Codex prompt status is {}".format(execution.get("status")))
    if not bool(execution.get("prompt_exists")):
        return "Codex prompt file is missing"
    refs = _task_refs(task)
    source_id = str(execution.get("source_id") or "")
    if source_id not in refs:
        return "Codex prompt targets {}".format(source_id or "another task")
    source_status = str(execution.get("source_status") or "")
    task_status = str(task.get("status") or "")
    if source_status and source_status != task_status:
        return "Codex prompt has task status {}, current status is {}".format(
            source_status,
            task_status,
        )
    context_pack = execution.get("context_pack") if isinstance(execution.get("context_pack"), Mapping) else {}
    if not context_pack:
        return "Context Pack is missing"
    context_task = str(context_pack.get("task_id") or "")
    if context_task and context_task not in refs:
        return "Context Pack targets {}".format(context_task)
    context_tasks_revision = context_pack.get("tasks_revision")
    if (
        tasks_revision is not None
        and isinstance(context_tasks_revision, int)
        and context_tasks_revision != tasks_revision
    ):
        return "Context Pack tasks revision is {} but current is {}".format(
            context_tasks_revision,
            tasks_revision,
        )
    context_docs_revision = context_pack.get("docs_revision")
    if (
        docs_revision is not None
        and isinstance(context_docs_revision, int)
        and context_docs_revision != docs_revision
    ):
        return "Context Pack docs revision is {} but current is {}".format(
            context_docs_revision,
            docs_revision,
        )
    return ""


def execution_context_summary(
    current_task: Mapping[str, Any],
    execution: Mapping[str, Any],
    *,
    tasks_revision: int | None,
    docs_revision: int | None,
    root: Path,
) -> dict[str, Any]:
    """Return UI-focused status for the current Codex handoff context."""

    current = dict(current_task)
    prompt_path = _display_project_path(
        root,
        str(execution.get("prompt_path") or ""),
        fallback="AI_PROJECT/generated/CODEX_PROMPT.md",
    )
    context_pack = (
        execution.get("context_pack")
        if isinstance(execution.get("context_pack"), Mapping)
        else {}
    )
    context_path = _display_project_path(
        root,
        str(context_pack.get("path") or ""),
        fallback="AI_PROJECT/generated/CONTEXT_PACK.md",
    )
    prompt_status, prompt_reason = _prompt_readiness(current, execution)
    context_status, context_reason = _context_readiness(
        current,
        context_pack,
        tasks_revision=tasks_revision,
        docs_revision=docs_revision,
    )
    warnings = [
        reason
        for reason in (prompt_reason, context_reason)
        if reason and reason not in {"No current task selected."}
    ]
    copy_instruction = (
        "Read {} and execute it.".format(prompt_path)
        if prompt_status == "ready"
        else ""
    )
    return {
        "current_task": current,
        "prompt": {
            "status": prompt_status,
            "reason": prompt_reason,
            "path": prompt_path,
            "raw_status": str(execution.get("status") or "unknown"),
            "code": str(execution.get("code") or ""),
            "exists": bool(execution.get("prompt_exists")),
            "copy_instruction": copy_instruction,
        },
        "context_pack": {
            "status": context_status,
            "reason": context_reason,
            "path": context_path,
            "sha256": str(context_pack.get("sha256") or context_pack.get("sha_256") or ""),
            "task_id": str(context_pack.get("task_id") or ""),
            "docs_revision": context_pack.get("docs_revision"),
            "tasks_revision": context_pack.get("tasks_revision"),
            "selected_sources": context_pack.get("selected_sources"),
        },
        "warnings": warnings,
        "updated_at": str(execution.get("updated_at") or ""),
    }


def _prompt_readiness(
    current_task: Mapping[str, Any],
    execution: Mapping[str, Any],
) -> tuple[str, str]:
    if not current_task:
        return "unknown", "No current task selected."
    if not execution or str(execution.get("status") or "") == "missing":
        return "missing", "No current Codex prompt state exists."
    raw_status = str(execution.get("status") or "").lower()
    if raw_status != "ready":
        return "blocked", str(
            execution.get("blocked_reason")
            or "Codex prompt status is {}".format(execution.get("status") or "unknown")
        )
    if not bool(execution.get("prompt_exists")):
        return "missing", "Codex prompt file is missing."
    refs = _task_refs(current_task)
    source_id = str(execution.get("source_id") or "")
    if source_id not in refs:
        return "stale", "Codex prompt targets {}".format(source_id or "another task")
    source_status = str(execution.get("source_status") or "")
    task_status = str(current_task.get("status") or "")
    if source_status and task_status and source_status != task_status:
        return "stale", "Codex prompt has task status {}, current status is {}".format(
            source_status,
            task_status,
        )
    return "ready", ""


def _context_readiness(
    current_task: Mapping[str, Any],
    context_pack: Mapping[str, Any],
    *,
    tasks_revision: int | None,
    docs_revision: int | None,
) -> tuple[str, str]:
    if not current_task:
        return "unknown", "No current task selected."
    if not context_pack:
        return "missing", "No Context Pack metadata exists."
    refs = _task_refs(current_task)
    context_task = str(context_pack.get("task_id") or "")
    if context_task and context_task not in refs:
        return "stale", "Context Pack targets {}".format(context_task)
    context_tasks_revision = context_pack.get("tasks_revision")
    if (
        tasks_revision is not None
        and isinstance(context_tasks_revision, int)
        and context_tasks_revision != tasks_revision
    ):
        return "stale", "Context Pack tasks revision is {} but current is {}".format(
            context_tasks_revision,
            tasks_revision,
        )
    context_docs_revision = context_pack.get("docs_revision")
    if (
        docs_revision is not None
        and isinstance(context_docs_revision, int)
        and context_docs_revision != docs_revision
    ):
        return "stale", "Context Pack docs revision is {} but current is {}".format(
            context_docs_revision,
            docs_revision,
        )
    return "ready", ""


def project_health_summary(
    doctor: Mapping[str, Any],
    generated: Sequence[Mapping[str, Any]],
    *,
    execution_context: Mapping[str, Any],
    current_task: Mapping[str, Any],
) -> dict[str, Any]:
    """Return UI-focused health and repair hints without running checks."""

    generated_by_name = {
        str(item.get("name") or ""): item
        for item in generated
        if isinstance(item, Mapping)
    }
    doctor_status = str(doctor.get("overall_status") or "UNKNOWN")
    doctor_cached = bool(_mapping(doctor.get("cache")).get("cached"))
    task_ref = str(current_task.get("ref") or current_task.get("id") or "")
    return {
        "doctor": {
            "label": "Project Doctor",
            "status": doctor_status,
            "message": _doctor_health_message(doctor, doctor_cached),
            "action": "project.doctor",
            "action_label": "Run Doctor",
            "available": True,
            "reason": "",
        },
        "artifacts": [
            _doctor_backed_artifact(
                doctor,
                generated_by_name,
                key="task_generated",
                label="Task generated views",
                checks=("task generated output",),
                files=("CODEX_TASKS.md", "CODEX_CURRENT.md", "TASK_EXECUTION_QUEUE.md"),
                action="project.render",
                action_label="Render project views",
                doctor_cached=doctor_cached,
            ),
            _doctor_backed_artifact(
                doctor,
                generated_by_name,
                key="docs_generated",
                label="Docs generated views",
                checks=("docs generated output", "docs validation"),
                files=("DOCS_INDEX.md", "DOCS_GAPS.md"),
                action="docs.render",
                action_label="Render Docs",
                doctor_cached=doctor_cached,
            ),
            _execution_artifact(
                key="context_pack",
                label="Context Pack",
                status=str(_mapping(execution_context.get("context_pack")).get("status") or "unknown"),
                reason=str(_mapping(execution_context.get("context_pack")).get("reason") or ""),
                path=str(_mapping(execution_context.get("context_pack")).get("path") or ""),
                task_ref=task_ref,
                action="task.refresh_execution_context",
                action_label="Refresh Context/Codex",
            ),
            _execution_artifact(
                key="codex_prompt",
                label="Codex prompt",
                status=str(_mapping(execution_context.get("prompt")).get("status") or "unknown"),
                reason=str(_mapping(execution_context.get("prompt")).get("reason") or ""),
                path=str(_mapping(execution_context.get("prompt")).get("path") or ""),
                task_ref=task_ref,
                action="codex.prompt.build",
                action_label="Refresh Codex Prompt",
            ),
            _doctor_backed_artifact(
                doctor,
                generated_by_name,
                key="evolution_generated",
                label="Evolution generated view",
                checks=("evolution generated output", "evolution validation"),
                files=("EVOLUTION.md",),
                action="project.render",
                action_label="Render project views",
                doctor_cached=doctor_cached,
            ),
            _doctor_backed_artifact(
                doctor,
                generated_by_name,
                key="protected_files",
                label="Protected files",
                checks=("protected project files",),
                files=(),
                action="project.protected_check",
                action_label="Check Protected Files",
                doctor_cached=doctor_cached,
            ),
        ],
    }


def _doctor_health_message(doctor: Mapping[str, Any], cached: bool) -> str:
    if not cached:
        return "Doctor has not been run in this web session."
    summary = _mapping(doctor.get("summary"))
    return "{} PASS, {} WARN, {} FAIL".format(
        summary.get("PASS", 0),
        summary.get("WARN", 0),
        summary.get("FAIL", 0),
    )


def _doctor_backed_artifact(
    doctor: Mapping[str, Any],
    generated_by_name: Mapping[str, Mapping[str, Any]],
    *,
    key: str,
    label: str,
    checks: Sequence[str],
    files: Sequence[str],
    action: str,
    action_label: str,
    doctor_cached: bool,
) -> dict[str, Any]:
    finding = _doctor_finding(doctor, checks)
    missing = [
        "AI_PROJECT/generated/{}".format(name)
        for name in files
        if not bool(_mapping(generated_by_name.get(name)).get("exists"))
    ]
    if finding:
        status = str(finding.get("status") or "UNKNOWN")
        message = str(finding.get("message") or "")
    elif missing:
        status = "WARN"
        message = "Missing generated view(s): {}".format(", ".join(missing))
    elif doctor_cached:
        status = "PASS"
        message = "No stale state detected by the latest doctor run."
    else:
        status = "UNKNOWN"
        message = "Run Doctor to detect stale or failed generated output."
    return {
        "key": key,
        "label": label,
        "status": status,
        "message": message,
        "files": list(files),
        "action": action,
        "action_label": action_label,
        "available": True,
        "reason": "",
    }


def _execution_artifact(
    *,
    key: str,
    label: str,
    status: str,
    reason: str,
    path: str,
    task_ref: str,
    action: str,
    action_label: str,
) -> dict[str, Any]:
    available = bool(task_ref)
    if not available:
        reason = "No current task selected."
    return {
        "key": key,
        "label": label,
        "status": _execution_health_status(status),
        "message": reason or "Ready for the current task.",
        "path": path,
        "task": task_ref,
        "action": action,
        "action_label": action_label,
        "available": available,
        "reason": "" if available else reason,
    }


def _execution_health_status(status: str) -> str:
    normalized = status.lower()
    if normalized == "ready":
        return "PASS"
    if normalized in {"stale", "missing", "blocked"}:
        return "WARN"
    return "UNKNOWN"


def _doctor_finding(
    doctor: Mapping[str, Any],
    checks: Sequence[str],
) -> Mapping[str, Any]:
    wanted = {check.lower() for check in checks}
    for finding in doctor.get("findings") or []:
        if not isinstance(finding, Mapping):
            continue
        if str(finding.get("check") or "").lower() in wanted:
            return finding
    return {}


def _display_project_path(root: Path, value: str, *, fallback: str) -> str:
    text = value.strip() or fallback
    path = Path(text)
    if path.is_absolute():
        try:
            return path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            return path.as_posix()
    return path.as_posix()


def _change_linked_task_blockers(
    change: Mapping[str, Any],
    tasks_by_ref: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    linked_tasks = _string_list(change.get("linked_tasks"))
    if not linked_tasks:
        return ["linked Tasks are missing"]
    blockers = []
    for task_ref in linked_tasks:
        task = tasks_by_ref.get(task_ref)
        if task is None:
            blockers.append("{} missing".format(task_ref))
            continue
        status = str(task.get("status") or "unknown")
        if status not in CHANGE_DONE_TASK_STATUSES:
            blockers.append("{} status is {}".format(_task_display_ref(task), status))
    return blockers


def _change_summary(change: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": str(change.get("id") or ""),
        "status": str(change.get("status") or "unknown"),
        "title": str(change.get("title") or ""),
    }


def _task_report_summary(report_record: Mapping[str, Any]) -> dict[str, Any]:
    report = report_record.get("report")
    report_data = report if isinstance(report, Mapping) else {}
    checks = [
        dict(check)
        for check in report_data.get("checks", [])
        if isinstance(check, Mapping)
    ]
    check_counts = Counter(str(check.get("result") or "unknown") for check in checks)
    blocking_failures = [
        check
        for check in checks
        if bool(check.get("blocking"))
        and str(check.get("result") or "").lower() in {"fail", "failed", "error"}
    ]
    return {
        "id": str(report_record.get("id") or ""),
        "task_id": str(report_record.get("task_id") or ""),
        "task_ref": str(report_record.get("task_ref") or ""),
        "submitted_at": str(report_record.get("submitted_at") or ""),
        "submitted_by": str(report_record.get("submitted_by") or ""),
        "source_file": str(report_record.get("source_file") or ""),
        "implementation_summary": str(report_data.get("implementation_summary") or ""),
        "changed_files": _string_list(report_data.get("changed_files")),
        "generated_files": _string_list(report_data.get("generated_files")),
        "warnings": _string_list(report_data.get("warnings")),
        "blockers": _string_list(report_data.get("blockers")),
        "notes": _string_list(report_data.get("notes")),
        "owner_decision_required": bool(report_data.get("owner_decision_required")),
        "checks": checks,
        "check_counts": dict(check_counts),
        "blocking_failures": len(blocking_failures),
        "has_blockers": bool(_string_list(report_data.get("blockers")) or blocking_failures),
    }


def _enriched_current_task(
    current_task: Mapping[str, Any],
    tasks: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    current_id = str(current_task.get("id") or "")
    if current_id:
        for task in tasks:
            if str(task.get("id") or "") == current_id:
                return dict(task)
    return dict(current_task)


def _tasks_by_ref(tasks: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    mapped = {}
    for task in tasks:
        for ref in _task_refs(task):
            mapped[ref] = task
    return mapped


def _task_refs(task: Mapping[str, Any]) -> set[str]:
    refs = {
        str(task.get(field) or "")
        for field in ("id", "uid", "ref", "legacy_id")
        if task.get(field)
    }
    refs.update(_string_list(task.get("aliases")))
    return {ref for ref in refs if ref}


def _task_display_ref(task: Mapping[str, Any]) -> str:
    return str(
        task.get("ref")
        or task.get("legacy_id")
        or task.get("id")
        or "unknown task"
    )


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item) for item in value if str(item).strip()]


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _parse_git_short_status(stdout: str) -> list[dict[str, str]]:
    files = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        status = line[:2].strip() or line[:2]
        path = line[3:].strip() if len(line) > 3 else ""
        if not path:
            continue
        files.append({"status": status, "path": path})
    return files


def _recent_completed_tasks(tasks: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    completed = [
        task
        for task in tasks
        if str(task.get("status") or "") in COMMIT_COMPLETED_TASK_STATUSES
    ]
    return [
        {
            "id": str(task.get("id") or ""),
            "ref": _task_display_ref(task),
            "title": str(task.get("title") or ""),
            "updated_at": str(task.get("updated_at") or ""),
        }
        for task in sorted(
            completed,
            key=lambda task: (
                str(task.get("updated_at") or ""),
                int(task.get("order") or 0),
                str(task.get("id") or ""),
            ),
            reverse=True,
        )[:8]
    ]


def _recent_accepted_changes(
    changes: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    accepted = [
        change
        for change in changes
        if str(change.get("status") or "") in COMMIT_ACCEPTED_CHANGE_STATUSES
    ]
    return [
        {
            "id": str(change.get("id") or ""),
            "title": str(change.get("title") or ""),
            "accepted_at": str(change.get("accepted_at") or ""),
            "updated_at": str(change.get("updated_at") or ""),
            "linked_tasks": _string_list(change.get("linked_tasks")),
        }
        for change in sorted(
            accepted,
            key=lambda change: (
                str(change.get("accepted_at") or change.get("updated_at") or ""),
                int(change.get("order") or 0),
                str(change.get("id") or ""),
            ),
            reverse=True,
        )[:8]
    ]


def _commit_validation_sections(doctor: Mapping[str, Any]) -> dict[str, Any]:
    findings = [
        finding
        for finding in doctor.get("findings") or []
        if isinstance(finding, Mapping)
    ]
    return {
        "project": _commit_finding_group(
            findings,
            (
                "plan validation",
                "task validation",
                "task dependency graph",
                "docs validation",
                "evolution validation",
                "context validation",
            ),
            empty_label="Project validation",
        ),
        "generated": _commit_finding_group(
            findings,
            (
                "task generated output",
                "docs generated output",
                "evolution generated output",
                "context generated output",
            ),
            empty_label="Generated artifacts",
        ),
        "protected_files": _commit_finding_group(
            findings,
            ("protected project files",),
            empty_label="Protected files",
        ),
    }


def _commit_finding_group(
    findings: Sequence[Mapping[str, Any]],
    checks: Sequence[str],
    *,
    empty_label: str,
) -> dict[str, Any]:
    wanted = {check.lower() for check in checks}
    selected = [
        _commit_finding_summary(finding)
        for finding in findings
        if str(finding.get("check") or "").lower() in wanted
    ]
    if selected:
        status = _worst_commit_status([item["status"] for item in selected])
        message = _commit_group_message(status)
    else:
        status = "UNKNOWN"
        message = "Run readiness checks to populate {}.".format(empty_label.lower())
    return {
        "label": empty_label,
        "status": status,
        "message": message,
        "findings": selected,
    }


def _commit_finding_summary(finding: Mapping[str, Any]) -> dict[str, str]:
    return {
        "check": str(finding.get("check") or ""),
        "status": str(finding.get("status") or "UNKNOWN"),
        "message": str(finding.get("message") or ""),
    }


def _worst_commit_status(statuses: Sequence[str]) -> str:
    rank = {"FAIL": 3, "WARN": 2, "UNKNOWN": 1, "PASS": 0}
    worst = "PASS"
    for status in statuses:
        normalized = str(status or "UNKNOWN").upper()
        if rank.get(normalized, 1) > rank.get(worst, 0):
            worst = normalized
    return worst


def _commit_group_message(status: str) -> str:
    if status == "PASS":
        return "Checks are passing."
    if status == "WARN":
        return "Warnings are visible."
    if status == "FAIL":
        return "Blocking failures are visible."
    return "Run readiness checks to populate this status."


def _commit_readiness_status(
    git: Mapping[str, Any],
    doctor: Mapping[str, Any],
    validation: Mapping[str, Any],
) -> tuple[str, str]:
    if str(git.get("status") or "") == "unavailable":
        return "WARN", "Git status is unavailable; no commit command was run."

    statuses = [
        str(group.get("status") or "UNKNOWN")
        for group in validation.values()
        if isinstance(group, Mapping)
    ]
    doctor_cached = bool(_mapping(doctor.get("cache")).get("cached"))
    if not doctor_cached:
        return "UNKNOWN", "Run readiness checks before committing."
    worst = _worst_commit_status(statuses)
    if worst == "FAIL":
        return "FAIL", "Resolve blocking project-control failures before committing."
    if worst == "WARN":
        return "WARN", "Review warnings before committing."
    if str(git.get("status") or "") == "clean":
        return "PASS", "Project checks pass; git reports no changed files."
    return "PASS", "Project checks pass and changed files are visible."


def _suggest_commit_message(
    completed_tasks: Sequence[Mapping[str, Any]],
    accepted_changes: Sequence[Mapping[str, Any]],
) -> str:
    subject = ""
    if accepted_changes:
        change = accepted_changes[0]
        subject = str(change.get("title") or change.get("id") or "").strip()
    elif completed_tasks:
        task = completed_tasks[0]
        subject = str(task.get("title") or task.get("ref") or "").strip()
    if not subject:
        return "Update project control worktree"
    normalized = _trim_commit_subject(subject)
    if normalized.lower().startswith(("add ", "fix ", "update ", "implement ")):
        return normalized
    return "Update {}".format(normalized[:1].lower() + normalized[1:])


def _trim_commit_subject(value: str) -> str:
    subject = " ".join(str(value or "").split())
    for prefix in ("UIX-", "WFA-", "CTL-", "TIG-", "DOC-"):
        if subject.startswith(prefix):
            parts = subject.split(" ", 1)
            if len(parts) == 2:
                return parts[1]
    return subject

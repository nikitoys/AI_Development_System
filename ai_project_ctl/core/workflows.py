"""Safe workflow orchestration over existing project-control commands."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ai_project_ctl.core.registry import command_describe
from ai_project_ctl.core.result import CommandError, CommandMessage, CommandResult


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PACKAGE_ROOT / "scripts"

CONFIRM_VALUES = {"yes", "true", "confirmed"}

REGISTERED = "registered"
VALIDATED_CTL = "validated_ctl"
READ_ONLY_CTL = "read_only_ctl"

TASK_REVIEW_DECISION_REQUIRED_STATUS = "in_review"
TASK_CLOSE_REQUIRED_STATUS = TASK_REVIEW_DECISION_REQUIRED_STATUS
CHANGE_APPROVE_REQUIRED_STATUS = "ready"
CHANGE_ACCEPTABLE_STATUSES = {"approved", "in_review"}
CHANGE_REVIEWABLE_STATUSES = {"approved", "in_progress", "in_review"}
CHANGE_DONE_TASK_STATUSES = {"done", "archived"}
EPIC_CLOSED_TASK_STATUSES = {"done", "deferred", "archived"}
EPIC_CLOSABLE_STATUSES = {"active", "done"}


class WorkflowError(CommandError):
    """Stable workflow orchestration error."""


@dataclass(frozen=True)
class WorkflowStepTemplate:
    """Human-readable workflow step metadata."""

    step_id: str
    title: str
    command_name: str
    route: str
    command_template: tuple[str, ...]
    blocking: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.step_id,
            "title": self.title,
            "command_name": self.command_name,
            "route": self.route,
            "command_template": list(self.command_template),
            "blocking": self.blocking,
        }


@dataclass(frozen=True)
class WorkflowDescriptor:
    """A controlled high-level workflow composed from lower-level commands."""

    name: str
    label: str
    description: str
    confirmation_required: bool
    arguments: tuple[dict[str, Any], ...]
    steps: tuple[WorkflowStepTemplate, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "label": self.label,
            "description": self.description,
            "confirmation_required": self.confirmation_required,
            "arguments": [dict(argument) for argument in self.arguments],
            "steps": [step.to_dict() for step in self.steps],
        }


@dataclass(frozen=True)
class TaskCreateRequest:
    """Owner-facing task creation fields for the create-only workflow."""

    epic: str
    title: str
    summary: str = ""
    description: str = ""
    priority: int = 1
    status: str = "planned"
    active_role: str = ""
    active_stage: str = ""
    active_document: str = ""
    expected_result: str = ""
    verification_mode: str = "standard"
    scope: tuple[str, ...] = ()
    out_of_scope: tuple[str, ...] = ()
    allowed_files: tuple[str, ...] = ()
    acceptance: tuple[str, ...] = ()
    review_instructions: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    dependency_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "epic": self.epic,
            "title": self.title,
            "summary": self.summary,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "active_role": self.active_role,
            "active_stage": self.active_stage,
            "active_document": self.active_document,
            "expected_result": self.expected_result,
            "verification_mode": self.verification_mode,
            "scope": list(self.scope),
            "out_of_scope": list(self.out_of_scope),
            "allowed_files": list(self.allowed_files),
            "acceptance": list(self.acceptance),
            "review_instructions": list(self.review_instructions),
            "notes": list(self.notes),
            "depends_on": list(self.depends_on),
            "dependency_reason": self.dependency_reason,
        }


@dataclass(frozen=True)
class TaskBulkImportRequest:
    """Structured text payload for previewing or importing multiple Tasks."""

    source_text: str

    def to_dict(self) -> dict[str, Any]:
        return {"source_text_bytes": len(self.source_text.encode("utf-8"))}


@dataclass(frozen=True)
class WorkflowStep:
    """Concrete executable workflow step."""

    step_id: str
    title: str
    command_name: str
    route: str
    argv: tuple[str, ...]
    blocking: bool = True
    skip_reason: str = ""
    prompt_context_errors_are_warnings: bool = False

    def preview_dict(self) -> dict[str, Any]:
        data = {
            "id": self.step_id,
            "title": self.title,
            "command_name": self.command_name,
            "route": self.route,
            "command": _display_argv(self.argv),
            "blocking": self.blocking,
            "skip_reason": self.skip_reason,
        }
        if self.prompt_context_errors_are_warnings:
            data["prompt_context_errors_are_warnings"] = True
        return data


@dataclass(frozen=True)
class WorkflowStepResult:
    """Captured result for one workflow step."""

    step: WorkflowStep
    status: str
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""

    @property
    def ok(self) -> bool:
        return self.status in {"ok", "skipped"}

    def to_dict(self) -> dict[str, Any]:
        data = self.step.preview_dict()
        data.update(
            {
                "status": self.status,
                "returncode": self.returncode,
                "stdout": self.stdout,
                "stderr": self.stderr,
            }
        )
        return data


Runner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


def workflow_list() -> list[dict[str, Any]]:
    """List available high-level workflows."""

    return [descriptor.to_dict() for descriptor in _workflow_descriptors()]


def workflow_describe(name: str) -> dict[str, Any]:
    """Describe one high-level workflow."""

    return _get_workflow_descriptor(name).to_dict()


def workflow_preview(
    name: str,
    *,
    task_ref: str | None = None,
    change_ref: str | None = None,
    epic_ref: str | None = None,
    notes: str = "",
    root: str | Path = ".",
    actor: str = "human_owner",
    python_executable: str | None = None,
) -> dict[str, Any]:
    """Return a non-mutating step preview for a workflow."""

    descriptor = _get_workflow_descriptor(name)
    task = {
        "id": task_ref or "<task>",
        "status": "<resolved-status>",
    }
    change = {
        "id": change_ref or "<change>",
        "status": "<resolved-status>",
    }
    epic = {
        "id": epic_ref or "<epic>",
        "status": "<resolved-status>",
    }
    change_preview: dict[str, Any] | None = None
    if descriptor.name == "evolution.create_for_task" and task_ref:
        task = _load_task_for_preview(Path(root).resolve(), task_ref) or task
        change_preview = _derive_evolution_change(task)
    root_path = Path(root).resolve()
    python_bin = python_executable or sys.executable
    if descriptor.name == "evolution.approve_change":
        steps = _build_change_approve_steps(
            change,
            root=root_path,
            actor=actor,
            python_executable=python_bin,
            notes=notes,
        )
    elif descriptor.name == "evolution.move_to_review":
        steps = _build_change_review_steps(
            change,
            root=root_path,
            actor=actor,
            python_executable=python_bin,
        )
    elif descriptor.name == "evolution.accept_change":
        steps = _build_change_accept_steps(
            change,
            root=root_path,
            actor=actor,
            python_executable=python_bin,
            notes=notes,
        )
    elif descriptor.name == "epic.close_if_complete":
        steps = _build_epic_close_steps(
            epic,
            root=root_path,
            actor=actor,
            python_executable=python_bin,
        )
    else:
        steps = _build_steps(
            descriptor.name,
            task=task,
            root=root_path,
            actor=actor,
            python_executable=python_bin,
            include_resolve=True,
            change_preview=change_preview,
            notes=notes,
        )
    payload = {
        "workflow": descriptor.to_dict(),
        "task_ref": task_ref or "",
        "change_ref": change_ref or "",
        "epic_ref": epic_ref or "",
        "task": task,
        "change": change,
        "epic": epic,
        "notes_required": descriptor.name
        in {
            "task.close_reviewed",
            "task.request_changes",
            "evolution.approve_change",
            "evolution.accept_change",
        },
        "steps": [step.preview_dict() for step in steps],
    }
    if change_preview is not None:
        payload["change_preview"] = change_preview
    return payload


def task_create_preview(
    request: TaskCreateRequest,
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    python_executable: str | None = None,
) -> dict[str, Any]:
    """Return a non-mutating preview for the create-only task workflow."""

    descriptor = _get_workflow_descriptor("task.create_single")
    steps = _build_task_create_steps(
        request,
        root=Path(root).resolve(),
        actor=actor,
        python_executable=python_executable or sys.executable,
        created_task_id="<CREATED_TASK>",
    )
    return {
        "workflow": descriptor.to_dict(),
        "request": request.to_dict(),
        "create_only": True,
        "steps": [step.preview_dict() for step in steps],
    }


def task_bulk_import_preview(
    request: TaskBulkImportRequest,
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    python_executable: str | None = None,
) -> dict[str, Any]:
    """Return a non-mutating preview for a bulk task import payload."""

    _requests, preview = _prepare_task_bulk_import(
        request,
        root=Path(root).resolve(),
        actor=actor,
        python_executable=python_executable or sys.executable,
    )
    return preview


def run_task_bulk_import_workflow(
    request: TaskBulkImportRequest,
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    confirmed: bool = False,
    python_executable: str | None = None,
    runner: Runner | None = None,
) -> CommandResult:
    """Preview or create multiple Tasks through the governed task create path."""

    try:
        task_requests, preview = _prepare_task_bulk_import(
            request,
            root=Path(root).resolve(),
            actor=actor,
            python_executable=python_executable or sys.executable,
        )
    except WorkflowError as exc:
        result = CommandResult.failure(
            command="task.import",
            domain="workflow",
            message="Bulk task import is invalid.",
            errors=[exc.to_message()],
        )
        result.data = {"request": request.to_dict()}
        return result

    if not confirmed:
        result = CommandResult.success(
            command="task.import",
            domain="workflow",
            message="Bulk task import preview is ready. No tasks were created.",
            data=preview,
        )
        result.owner_action_required = (
            "Review the import preview and rerun with --confirm to create tasks."
        )
        return result

    step_results: list[dict[str, Any]] = []
    child_results: list[dict[str, Any]] = []
    created_task_ids: list[str] = []
    for index, task_request in enumerate(task_requests, start=1):
        child = run_task_create_workflow(
            task_request,
            root=root,
            actor=actor,
            confirmed=True,
            python_executable=python_executable,
            runner=runner,
        )
        child_data = child.to_dict()
        child_data["import_index"] = index
        child_results.append(child_data)
        for step in child.data.get("steps") or []:
            item = dict(step)
            item["import_index"] = index
            item["import_title"] = task_request.title
            step_results.append(item)
        created_task_id = str(child.data.get("created_task_id") or "")
        if created_task_id:
            created_task_ids.append(created_task_id)
        if not child.ok:
            result = CommandResult.failure(
                command="task.import",
                domain="workflow",
                message="Bulk task import stopped while creating task {}.".format(index),
                errors=list(child.errors),
            )
            result.data = {
                **preview,
                "dry_run": False,
                "created_task_ids": created_task_ids,
                "child_results": child_results,
                "steps": step_results,
            }
            result.generated_files = [
                "AI_PROJECT/generated/CODEX_TASKS.md",
                "AI_PROJECT/generated/CODEX_CURRENT.md",
                "AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md",
            ]
            result.events = ["AI_PROJECT/events/task-events.jsonl"]
            result.owner_action_required = (
                "Inspect created tasks and failed step output before retrying."
            )
            return result

    result = CommandResult.success(
        command="task.import",
        domain="workflow",
        message="Bulk task import completed. Tasks were created without selecting or starting them.",
        data={
            **preview,
            "dry_run": False,
            "created_task_ids": created_task_ids,
            "child_results": child_results,
            "steps": step_results,
        },
    )
    result.generated_files = [
        "AI_PROJECT/generated/CODEX_TASKS.md",
        "AI_PROJECT/generated/CODEX_CURRENT.md",
        "AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md",
    ]
    result.events = ["AI_PROJECT/events/task-events.jsonl"]
    result.owner_action_required = (
        "Review created tasks {}; prepare individual tasks for Codex only when intended."
    ).format(", ".join(created_task_ids))
    result.next_actions.extend(
        "python scripts/aictl.py workflow run task.prepare_for_codex --task {} --confirm".format(
            task_id
        )
        for task_id in created_task_ids
    )
    return result


def run_task_create_workflow(
    request: TaskCreateRequest,
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    confirmed: bool = False,
    python_executable: str | None = None,
    runner: Runner | None = None,
) -> CommandResult:
    """Create one task through taskctl.py and optional dependency commands."""

    descriptor = _get_workflow_descriptor("task.create_single")
    preview = task_create_preview(
        request,
        root=root,
        actor=actor,
        python_executable=python_executable,
    )
    if descriptor.confirmation_required and not confirmed:
        result = CommandResult.failure(
            command=descriptor.name,
            domain="workflow",
            message="Workflow requires explicit confirmation.",
            errors=[
                CommandMessage(
                    code="WORKFLOW_CONFIRMATION_REQUIRED",
                    message="Rerun with --confirm after reviewing the task creation preview.",
                    details={"workflow": descriptor.name},
                )
            ],
        )
        result.data = preview
        result.owner_action_required = "Review the task creation preview and rerun with --confirm."
        return result

    executor = WorkflowExecutor(
        root=root,
        actor=actor,
        python_executable=python_executable,
        runner=runner,
    )
    step_results: list[WorkflowStepResult] = []
    create_step = _task_create_step(
        request,
        executor.root,
        executor.actor,
        executor.python_executable,
    )
    create_result = executor._execute_step(create_step)
    step_results.append(create_result)
    created_task_id = ""

    if create_result.ok:
        try:
            created_task_id = _parse_created_task_id(create_result.stdout)
        except WorkflowError as exc:
            failed_step = WorkflowStep(
                step_id="parse_task_id",
                title="Parse created Task ID",
                command_name="task.create.parse_task_id",
                route=READ_ONLY_CTL,
                argv=("parse", "taskctl output"),
            )
            step_results.append(
                WorkflowStepResult(
                    step=failed_step,
                    status="failed",
                    returncode=1,
                    stderr=exc.message,
                )
            )
            result = _task_create_result(
                descriptor,
                request,
                created_task_id=created_task_id,
                step_results=step_results,
                message="Workflow stopped after creating a Task because its ID could not be parsed.",
            )
            result.errors.append(exc.to_message())
            result.owner_action_required = (
                "Inspect taskctl output and continue manually through taskctl.py if needed."
            )
            return result

    if not create_result.ok:
        return _task_create_result(
            descriptor,
            request,
            created_task_id=created_task_id,
            step_results=step_results,
            message="Workflow stopped while creating the Task.",
        )

    followup_steps = _build_task_create_steps(
        request,
        root=executor.root,
        actor=executor.actor,
        python_executable=executor.python_executable,
        created_task_id=created_task_id,
        include_create=False,
    )
    for step in followup_steps:
        step_result = executor._execute_step(step)
        step_results.append(step_result)
        if not step_result.ok and step_result.step.blocking:
            return _task_create_result(
                descriptor,
                request,
                created_task_id=created_task_id,
                step_results=step_results,
                message="Workflow stopped on blocking step: {}".format(step.title),
            )

    result = _task_create_result(
        descriptor,
        request,
        created_task_id=created_task_id,
        step_results=step_results,
        message="Workflow completed. Task was created without selecting or starting it.",
    )
    result.next_actions.extend(
        [
            "python scripts/aictl.py workflow run task.prepare_for_codex --task {} --confirm".format(
                created_task_id
            ),
            "python scripts/aictl.py workflow run evolution.create_for_task --task {} --confirm".format(
                created_task_id
            ),
        ]
    )
    result.owner_action_required = (
        "Review created task {}; run a prepare or evolution workflow only when intended."
    ).format(created_task_id)
    return result


def run_workflow(
    name: str,
    *,
    task_ref: str = "",
    change_ref: str = "",
    epic_ref: str = "",
    notes: str = "",
    root: str | Path = ".",
    actor: str = "human_owner",
    confirmed: bool = False,
    python_executable: str | None = None,
    runner: Runner | None = None,
) -> CommandResult:
    """Execute a confirmed high-level workflow through existing commands."""

    descriptor = _get_workflow_descriptor(name)
    preview = workflow_preview(
        name,
        task_ref=task_ref or None,
        change_ref=change_ref or None,
        epic_ref=epic_ref or None,
        notes=notes,
        root=root,
        actor=actor,
        python_executable=python_executable,
    )
    target_error = _workflow_target_error(
        descriptor.name,
        task_ref=task_ref,
        change_ref=change_ref,
        epic_ref=epic_ref,
    )
    if target_error is not None:
        result = CommandResult.failure(
            command=descriptor.name,
            domain="workflow",
            message="Workflow target is missing.",
            errors=[target_error.to_message()],
        )
        result.data = preview
        return result
    if descriptor.confirmation_required and not confirmed:
        result = CommandResult.failure(
            command=descriptor.name,
            domain="workflow",
            message="Workflow requires explicit confirmation.",
            errors=[
                CommandMessage(
                    code="WORKFLOW_CONFIRMATION_REQUIRED",
                    message="Rerun with --confirm after reviewing the workflow steps.",
                    details={"workflow": descriptor.name},
                )
            ],
        )
        result.data = preview
        result.owner_action_required = "Review the step preview and rerun with --confirm."
        return result

    executor = WorkflowExecutor(
        root=root,
        actor=actor,
        python_executable=python_executable,
        runner=runner,
    )
    return executor.run(
        descriptor,
        task_ref=task_ref,
        change_ref=change_ref,
        epic_ref=epic_ref,
        notes=notes,
    )


class WorkflowExecutor:
    """Execute workflows as ordered subprocess steps."""

    def __init__(
        self,
        root: str | Path = ".",
        *,
        actor: str = "human_owner",
        python_executable: str | None = None,
        runner: Runner | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.actor = actor
        self.python_executable = python_executable or sys.executable
        self.runner = runner or self._run_subprocess

    def run(
        self,
        descriptor: WorkflowDescriptor,
        *,
        task_ref: str = "",
        change_ref: str = "",
        epic_ref: str = "",
        notes: str = "",
    ) -> CommandResult:
        if descriptor.name == "evolution.create_for_task":
            return self._run_evolution_create_for_task(descriptor, task_ref=task_ref)
        if descriptor.name == "evolution.approve_change":
            return self._run_evolution_approve_change(
                descriptor,
                change_ref=change_ref,
                notes=notes,
            )
        if descriptor.name == "evolution.move_to_review":
            return self._run_evolution_move_to_review(
                descriptor,
                change_ref=change_ref,
            )
        if descriptor.name == "evolution.accept_change":
            return self._run_evolution_accept_change(
                descriptor,
                change_ref=change_ref,
                notes=notes,
            )
        if descriptor.name == "epic.close_if_complete":
            return self._run_epic_close_if_complete(
                descriptor,
                epic_ref=epic_ref,
            )

        resolve_step = _resolve_step(
            task_ref,
            root=self.root,
            actor=self.actor,
            python_executable=self.python_executable,
        )
        resolve_result = self._execute_step(resolve_step)
        step_results = [resolve_result]
        if not resolve_result.ok:
            return self._result(
                descriptor,
                task_ref=task_ref,
                task={},
                step_results=step_results,
                message="Workflow stopped while resolving task reference.",
            )

        task = _parse_resolved_task(resolve_result.stdout, task_ref=task_ref)
        if descriptor.name in {"task.close_reviewed", "task.request_changes"}:
            if descriptor.name == "task.request_changes":
                preflight = _task_request_changes_preflight_step_result(task, notes)
                preflight_error = _task_request_changes_preflight_error(task, notes)
                stopped_message = "Workflow stopped before request-changes preflight."
            else:
                preflight = _task_close_preflight_step_result(task, notes)
                preflight_error = _task_close_preflight_error(task, notes)
                stopped_message = "Workflow stopped before task closure preflight."
            step_results.append(preflight)
            if not preflight.ok:
                return self._preflight_result(
                    descriptor,
                    task_ref=task_ref,
                    task=task,
                    step_results=step_results,
                    error=preflight_error,
                    message=stopped_message,
                )
        steps = _build_steps(
            descriptor.name,
            task=task,
            root=self.root,
            actor=self.actor,
            python_executable=self.python_executable,
            include_resolve=False,
            notes=notes,
        )
        for step in steps:
            step_result = self._execute_step(step)
            step_results.append(step_result)
            if not step_result.ok and step_result.step.blocking:
                return self._result(
                    descriptor,
                    task_ref=task_ref,
                    task=task,
                    step_results=step_results,
                    message="Workflow stopped on blocking step: {}".format(step.title),
                )

        result = self._result(
            descriptor,
            task_ref=task_ref,
            task=task,
            step_results=step_results,
            message="Workflow completed.",
        )
        if result.ok and descriptor.name == "task.close_reviewed":
            _add_task_close_next_actions(result, self.root, task)
        elif result.ok and descriptor.name == "task.request_changes":
            _add_task_request_changes_next_actions(result, task)
        return result

    def _run_evolution_create_for_task(
        self,
        descriptor: WorkflowDescriptor,
        *,
        task_ref: str,
    ) -> CommandResult:
        resolve_step = _resolve_step(
            task_ref,
            root=self.root,
            actor=self.actor,
            python_executable=self.python_executable,
        )
        resolve_result = self._execute_step(resolve_step)
        step_results = [resolve_result]
        task: dict[str, Any] = {}
        change_preview: dict[str, Any] = {}
        change_id = ""

        if not resolve_result.ok:
            return self._result(
                descriptor,
                task_ref=task_ref,
                task=task,
                step_results=step_results,
                message="Workflow stopped while resolving task reference.",
            )

        try:
            resolved = _parse_resolved_task(resolve_result.stdout, task_ref=task_ref)
            task = _load_task_by_id(self.root, str(resolved.get("id") or ""))
            change_preview = _derive_evolution_change(task)
        except WorkflowError as exc:
            failed_step = WorkflowStep(
                step_id="derive_change",
                title="Derive Evolution Change preview",
                command_name="evolution.create_for_task.derive",
                route=READ_ONLY_CTL,
                argv=("read", "AI_PROJECT/state/tasks.json"),
            )
            step_results.append(
                WorkflowStepResult(
                    step=failed_step,
                    status="failed",
                    returncode=1,
                    stderr=exc.message,
                )
            )
            result = self._result(
                descriptor,
                task_ref=task_ref,
                task=task,
                step_results=step_results,
                message="Workflow stopped while deriving Evolution Change preview.",
            )
            result.errors.append(exc.to_message())
            return result

        create_step = _evolution_change_create_step(
            task,
            change_preview,
            self.root,
            self.actor,
            self.python_executable,
        )
        create_result = self._execute_step(create_step)
        step_results.append(create_result)
        if not create_result.ok:
            result = self._result(
                descriptor,
                task_ref=task_ref,
                task=task,
                step_results=step_results,
                message="Workflow stopped while creating Evolution Change Proposal.",
            )
            result.data["change_preview"] = change_preview
            return result

        try:
            change_id = _parse_created_change_id(create_result.stdout)
        except WorkflowError as exc:
            failed_step = WorkflowStep(
                step_id="parse_change_id",
                title="Parse created Change ID",
                command_name="evolution.create_for_task.parse_change_id",
                route=READ_ONLY_CTL,
                argv=("parse", "evolutionctl output"),
            )
            step_results.append(
                WorkflowStepResult(
                    step=failed_step,
                    status="failed",
                    returncode=1,
                    stderr=exc.message,
                )
            )
            result = self._result(
                descriptor,
                task_ref=task_ref,
                task=task,
                step_results=step_results,
                message="Workflow stopped after creating a Change Proposal because its ID could not be parsed.",
            )
            result.data["change_preview"] = change_preview
            result.errors.append(exc.to_message())
            result.owner_action_required = (
                "Inspect evolutionctl output and continue manually through evolutionctl.py."
            )
            return result

        steps = _evolution_change_followup_steps(
            task,
            change_preview,
            change_id,
            self.root,
            self.actor,
            self.python_executable,
        )
        for step in steps:
            step_result = self._execute_step(step)
            step_results.append(step_result)
            if not step_result.ok and step_result.step.blocking:
                result = self._result(
                    descriptor,
                    task_ref=task_ref,
                    task=task,
                    step_results=step_results,
                    message="Workflow stopped on blocking step: {}".format(step.title),
                )
                result.data["change_id"] = change_id
                result.data["change_preview"] = change_preview
                result.owner_action_required = (
                    "Review Change Proposal {} and continue manually through evolutionctl.py."
                ).format(change_id)
                return result

        result = self._result(
            descriptor,
            task_ref=task_ref,
            task=task,
            step_results=step_results,
            message="Workflow completed. Evolution Change Proposal is ready for Human Owner approval.",
        )
        result.data["change_id"] = change_id
        result.data["change_preview"] = change_preview
        result.owner_action_required = (
            "Review Change Proposal {change_id}; approve explicitly only if appropriate: "
            "python scripts/evolutionctl.py change approve {change_id} --notes \"Approved\""
        ).format(change_id=change_id)
        result.next_actions.append(
            "python scripts/evolutionctl.py change approve {} --notes \"Approved\"".format(
                change_id
            )
        )
        return result

    def _run_evolution_approve_change(
        self,
        descriptor: WorkflowDescriptor,
        *,
        change_ref: str,
        notes: str,
    ) -> CommandResult:
        try:
            change = _load_change_context(self.root, change_ref)
            error = _change_approve_preflight_error(change, notes)
        except WorkflowError as exc:
            change = {"id": change_ref, "status": ""}
            error = exc

        preflight = _local_check_step_result(
            "change_approve_preflight",
            "Check Change approval gates",
            "evolution.approve_change.preflight",
            error=error,
        )
        step_results = [preflight]
        if error is not None:
            return self._preflight_result(
                descriptor,
                task_ref="",
                task={},
                step_results=step_results,
                error=error,
                message="Workflow stopped before Evolution Change approval.",
                extra_data={"change_ref": change_ref, "change": dict(change)},
            )

        steps = _build_change_approve_steps(
            change,
            root=self.root,
            actor=self.actor,
            python_executable=self.python_executable,
            notes=notes,
        )
        for step in steps:
            step_result = self._execute_step(step)
            step_results.append(step_result)
            if not step_result.ok and step_result.step.blocking:
                return self._result(
                    descriptor,
                    task_ref="",
                    task={},
                    step_results=step_results,
                    message="Workflow stopped on blocking step: {}".format(step.title),
                    extra_data={"change_ref": change_ref, "change": dict(change)},
                )

        result = self._result(
            descriptor,
            task_ref="",
            task={},
            step_results=step_results,
            message="Workflow completed. Evolution Change was approved through evolutionctl.py.",
            extra_data={"change_ref": change_ref, "change": dict(change)},
        )
        result.owner_action_required = (
            "Approved Change remains separate from implementation and acceptance; continue only through governed task/evolution workflows."
        )
        return result

    def _run_evolution_move_to_review(
        self,
        descriptor: WorkflowDescriptor,
        *,
        change_ref: str,
    ) -> CommandResult:
        try:
            change = _load_change_context(self.root, change_ref)
            error = _change_review_preflight_error(change)
        except WorkflowError as exc:
            change = {"id": change_ref, "status": ""}
            error = exc

        preflight = _local_check_step_result(
            "change_review_preflight",
            "Check Change review gates",
            "evolution.move_to_review.preflight",
            error=error,
        )
        step_results = [preflight]
        if error is not None:
            return self._preflight_result(
                descriptor,
                task_ref="",
                task={},
                step_results=step_results,
                error=error,
                message="Workflow stopped before Evolution Change review transition.",
                extra_data={"change_ref": change_ref, "change": dict(change)},
            )

        steps = _build_change_review_steps(
            change,
            root=self.root,
            actor=self.actor,
            python_executable=self.python_executable,
        )
        for step in steps:
            step_result = self._execute_step(step)
            step_results.append(step_result)
            if not step_result.ok and step_result.step.blocking:
                return self._result(
                    descriptor,
                    task_ref="",
                    task={},
                    step_results=step_results,
                    message="Workflow stopped on blocking step: {}".format(step.title),
                    extra_data={"change_ref": change_ref, "change": dict(change)},
                )

        return self._result(
            descriptor,
            task_ref="",
            task={},
            step_results=step_results,
            message="Workflow completed. Evolution Change was moved toward review through evolutionctl.py.",
            extra_data={"change_ref": change_ref, "change": dict(change)},
        )

    def _run_evolution_accept_change(
        self,
        descriptor: WorkflowDescriptor,
        *,
        change_ref: str,
        notes: str,
    ) -> CommandResult:
        try:
            change, tasks = _load_change_accept_context(self.root, change_ref)
            error = _change_accept_preflight_error(change, tasks, notes)
        except WorkflowError as exc:
            change = {"id": change_ref, "status": ""}
            error = exc

        preflight = _local_check_step_result(
            "change_accept_preflight",
            "Check Change acceptance gates",
            "evolution.accept_change.preflight",
            error=error,
        )
        step_results = [preflight]
        if error is not None:
            return self._preflight_result(
                descriptor,
                task_ref="",
                task={},
                step_results=step_results,
                error=error,
                message="Workflow stopped before Evolution Change acceptance.",
                extra_data={"change_ref": change_ref, "change": dict(change)},
            )

        steps = _build_change_accept_steps(
            change,
            root=self.root,
            actor=self.actor,
            python_executable=self.python_executable,
            notes=notes,
        )
        for step in steps:
            step_result = self._execute_step(step)
            step_results.append(step_result)
            if not step_result.ok and step_result.step.blocking:
                return self._result(
                    descriptor,
                    task_ref="",
                    task={},
                    step_results=step_results,
                    message="Workflow stopped on blocking step: {}".format(step.title),
                    extra_data={"change_ref": change_ref, "change": dict(change)},
                )

        return self._result(
            descriptor,
            task_ref="",
            task={},
            step_results=step_results,
            message="Workflow completed. Evolution Change was accepted through evolutionctl.py.",
            extra_data={"change_ref": change_ref, "change": dict(change)},
        )

    def _run_epic_close_if_complete(
        self,
        descriptor: WorkflowDescriptor,
        *,
        epic_ref: str,
    ) -> CommandResult:
        try:
            epic, child_tasks = _load_epic_close_context(self.root, epic_ref)
            error = _epic_close_preflight_error(epic, child_tasks)
        except WorkflowError as exc:
            epic = {"id": epic_ref, "status": ""}
            error = exc

        preflight = _local_check_step_result(
            "epic_close_preflight",
            "Check Epic closure gates",
            "epic.close_if_complete.preflight",
            error=error,
        )
        step_results = [preflight]
        if error is not None:
            return self._preflight_result(
                descriptor,
                task_ref="",
                task={},
                step_results=step_results,
                error=error,
                message="Workflow stopped before Epic closure.",
                extra_data={"epic_ref": epic_ref, "epic": dict(epic)},
            )

        steps = _build_epic_close_steps(
            epic,
            root=self.root,
            actor=self.actor,
            python_executable=self.python_executable,
        )
        for step in steps:
            step_result = self._execute_step(step)
            step_results.append(step_result)
            if not step_result.ok and step_result.step.blocking:
                return self._result(
                    descriptor,
                    task_ref="",
                    task={},
                    step_results=step_results,
                    message="Workflow stopped on blocking step: {}".format(step.title),
                    extra_data={"epic_ref": epic_ref, "epic": dict(epic)},
                )

        return self._result(
            descriptor,
            task_ref="",
            task={},
            step_results=step_results,
            message="Workflow completed. Epic closure checks passed.",
            extra_data={"epic_ref": epic_ref, "epic": dict(epic)},
        )

    def _execute_step(self, step: WorkflowStep) -> WorkflowStepResult:
        if step.skip_reason:
            return WorkflowStepResult(step=step, status="skipped")
        _validate_step_route(step)
        completed = self.runner(step.argv)
        if step.prompt_context_errors_are_warnings:
            warning_result = _protected_prompt_context_warning_result(step, completed)
            if warning_result is not None:
                return warning_result
        return WorkflowStepResult(
            step=step,
            status="ok" if completed.returncode == 0 else "failed",
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    def _run_subprocess(self, argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(argv),
            cwd=str(PACKAGE_ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def _result(
        self,
        descriptor: WorkflowDescriptor,
        *,
        task_ref: str,
        task: Mapping[str, Any],
        step_results: Sequence[WorkflowStepResult],
        message: str,
        extra_data: Mapping[str, Any] | None = None,
    ) -> CommandResult:
        failed = next(
            (item for item in step_results if not item.ok and item.step.blocking),
            None,
        )
        warning_steps = [
            item for item in step_results if not item.ok and not item.step.blocking
        ]
        result = CommandResult(
            ok=failed is None,
            command=descriptor.name,
            domain="workflow",
            message=message,
            data={
                "workflow": descriptor.to_dict(),
                "task_ref": task_ref,
                "task": dict(task),
                "steps": [item.to_dict() for item in step_results],
            },
        )
        for warning_step in warning_steps:
            result.warnings.append(
                CommandMessage(
                    code="WORKFLOW_NON_BLOCKING_STEP_FAILED",
                    message="Non-blocking workflow step reported a warning: {}".format(
                        warning_step.step.title
                    ),
                    details={
                        "step": warning_step.step.step_id,
                        "command_name": warning_step.step.command_name,
                        "returncode": warning_step.returncode,
                        "stdout": warning_step.stdout,
                        "stderr": warning_step.stderr,
                    },
                )
            )
        if extra_data:
            result.data.update(dict(extra_data))
        if failed is not None:
            result.errors.append(
                CommandMessage(
                    code="WORKFLOW_STEP_FAILED",
                    message="Workflow step failed: {}".format(failed.step.title),
                    details={
                        "step": failed.step.step_id,
                        "command_name": failed.step.command_name,
                        "returncode": failed.returncode,
                        "stdout": failed.stdout,
                        "stderr": failed.stderr,
                    },
                )
            )
        return result

    def _preflight_result(
        self,
        descriptor: WorkflowDescriptor,
        *,
        task_ref: str,
        task: Mapping[str, Any],
        step_results: Sequence[WorkflowStepResult],
        error: WorkflowError,
        message: str,
        extra_data: Mapping[str, Any] | None = None,
    ) -> CommandResult:
        result = self._result(
            descriptor,
            task_ref=task_ref,
            task=task,
            step_results=step_results,
            message=message,
            extra_data=extra_data,
        )
        result.errors.insert(0, error.to_message())
        return result


def _workflow_descriptors() -> tuple[WorkflowDescriptor, ...]:
    task_argument = (
        {
            "name": "task",
            "description": "Task ID, ref, UID, legacy ID, or alias.",
            "required": True,
        },
    )
    return (
        WorkflowDescriptor(
            name="task.create_single",
            label="Create task",
            description=(
                "Create one Task through taskctl.py, optionally add dependencies, "
                "validate task state, and leave the task unselected and unstarted."
            ),
            confirmation_required=True,
            arguments=(
                {
                    "name": "epic",
                    "description": "Parent Epic ID or key.",
                    "required": True,
                },
                {
                    "name": "title",
                    "description": "Task title.",
                    "required": True,
                },
                {
                    "name": "depends_on",
                    "description": "Optional dependency task refs.",
                    "required": False,
                    "repeatable": True,
                },
            ),
            steps=(
                _template("task_create", "Create task", "task.create", VALIDATED_CTL, "python scripts/taskctl.py task create --epic <EPIC> --title <TITLE>"),
                _template("add_dependencies", "Add dependencies", "taskctl.task.deps.add", VALIDATED_CTL, "python scripts/taskctl.py task deps add <CREATED_TASK> --after <DEPENDENCY>"),
                _template("task_validate", "Validate task state", "taskctl.validate", VALIDATED_CTL, "python scripts/taskctl.py validate"),
                _template("task_graph", "Validate task graph", "taskctl.task.graph.validate", VALIDATED_CTL, "python scripts/taskctl.py task graph validate"),
                _template("task_generated", "Check generated task output", "taskctl.check-generated", VALIDATED_CTL, "python scripts/taskctl.py check-generated"),
            ),
        ),
        WorkflowDescriptor(
            name="task.prepare_for_codex",
            label="Prepare for Codex",
            description=(
                "Set and validate the current task, move it to in_progress when "
                "needed, rebuild context, rebuild the Codex prompt, and run doctor."
            ),
            confirmation_required=True,
            arguments=task_argument,
            steps=(
                _template("resolve", "Resolve task reference", "taskctl.task.resolve", READ_ONLY_CTL, "python scripts/taskctl.py task resolve <TASK> --json"),
                _template("current_set", "Set current task", "current.set", REGISTERED, "python scripts/aictl.py current set <TASK>"),
                _template("task_validate", "Validate task state", "taskctl.validate", VALIDATED_CTL, "python scripts/taskctl.py validate"),
                _template("task_graph", "Validate task graph", "taskctl.task.graph.validate", VALIDATED_CTL, "python scripts/taskctl.py task graph validate"),
                _template("task_in_progress", "Move task to in_progress when needed", "task.transition", REGISTERED, "python scripts/aictl.py task transition <TASK> --to in_progress"),
                _template("context_build", "Build task Context Pack", "context.build", REGISTERED, "python scripts/aictl.py context build --task <TASK> --write"),
                _template("codex_build", "Build Codex prompt with context", "codex.prompt.build", REGISTERED, "python scripts/aictl.py codex prompt build --task <TASK> --with-context"),
                _template("doctor", "Run project doctor", "project.doctor", REGISTERED, "python scripts/aictl.py project doctor"),
            ),
        ),
        WorkflowDescriptor(
            name="task.refresh_execution_context",
            label="Refresh execution context",
            description="Rebuild the task Context Pack and Codex prompt package.",
            confirmation_required=True,
            arguments=task_argument,
            steps=(
                _template("resolve", "Resolve task reference", "taskctl.task.resolve", READ_ONLY_CTL, "python scripts/taskctl.py task resolve <TASK> --json"),
                _template("context_build", "Build task Context Pack", "context.build", REGISTERED, "python scripts/aictl.py context build --task <TASK> --write"),
                _template("context_check", "Check generated context output", "contextctl.check-generated", VALIDATED_CTL, "python scripts/contextctl.py check-generated"),
                _template("codex_build", "Build Codex prompt with context", "codex.prompt.build", REGISTERED, "python scripts/aictl.py codex prompt build --task <TASK> --with-context"),
            ),
        ),
        WorkflowDescriptor(
            name="task.submit_for_review",
            label="Submit for review",
            description=(
                "Run blocking validation checks, then transition the task to "
                "in_review only when they pass."
            ),
            confirmation_required=True,
            arguments=task_argument,
            steps=(
                _template("resolve", "Resolve task reference", "taskctl.task.resolve", READ_ONLY_CTL, "python scripts/taskctl.py task resolve <TASK> --json"),
                _template("task_validate", "Validate task state", "taskctl.validate", VALIDATED_CTL, "python scripts/taskctl.py validate"),
                _template("task_graph", "Validate task graph", "taskctl.task.graph.validate", VALIDATED_CTL, "python scripts/taskctl.py task graph validate"),
                _template("task_generated", "Check generated task output", "taskctl.check-generated", VALIDATED_CTL, "python scripts/taskctl.py check-generated"),
                _template("context_validate", "Validate context control", "contextctl.validate", VALIDATED_CTL, "python scripts/contextctl.py validate"),
                _template("context_generated", "Check generated context output", "contextctl.check-generated", VALIDATED_CTL, "python scripts/contextctl.py check-generated"),
                _template("evolution_validate", "Validate evolution state", "evolutionctl.validate", VALIDATED_CTL, "python scripts/evolutionctl.py validate"),
                _template("evolution_generated", "Check generated evolution output", "evolutionctl.check-generated", VALIDATED_CTL, "python scripts/evolutionctl.py check-generated"),
                _template("protected", "Check protected project files", "protected.check", VALIDATED_CTL, "python scripts/check-protected-project-files.py --json"),
                _template("doctor", "Run project doctor", "project.doctor", REGISTERED, "python scripts/aictl.py project doctor"),
                _template("task_review", "Move task to in_review", "task.transition", REGISTERED, "python scripts/aictl.py task transition <TASK> --to in_review"),
            ),
        ),
        WorkflowDescriptor(
            name="task.close_reviewed",
            label="Close reviewed task",
            description=(
                "Run blocking close checks, approve an in_review task with explicit "
                "owner notes, and transition it to done through validated commands."
            ),
            confirmation_required=True,
            arguments=(
                *task_argument,
                {
                    "name": "notes",
                    "description": "Required approval notes.",
                    "required": True,
                },
            ),
            steps=(
                _template("resolve", "Resolve task reference", "taskctl.task.resolve", READ_ONLY_CTL, "python scripts/taskctl.py task resolve <TASK> --json"),
                _template("preflight", "Check task close gates", "task.close_reviewed.preflight", READ_ONLY_CTL, "check task status and approval notes"),
                _template("task_validate", "Validate task state", "taskctl.validate", VALIDATED_CTL, "python scripts/taskctl.py validate"),
                _template("task_graph", "Validate task graph", "taskctl.task.graph.validate", VALIDATED_CTL, "python scripts/taskctl.py task graph validate"),
                _template("task_generated", "Check generated task output", "taskctl.check-generated", VALIDATED_CTL, "python scripts/taskctl.py check-generated"),
                _template("context_validate", "Validate context control", "contextctl.validate", VALIDATED_CTL, "python scripts/contextctl.py validate"),
                _template("context_generated", "Check generated context output", "contextctl.check-generated", VALIDATED_CTL, "python scripts/contextctl.py check-generated", blocking=False),
                _template("evolution_validate", "Validate evolution state", "evolutionctl.validate", VALIDATED_CTL, "python scripts/evolutionctl.py validate"),
                _template("evolution_generated", "Check generated evolution output", "evolutionctl.check-generated", VALIDATED_CTL, "python scripts/evolutionctl.py check-generated"),
                _template("protected", "Check protected project files", "protected.check", VALIDATED_CTL, "python scripts/check-protected-project-files.py --json"),
                _template("doctor", "Run project doctor", "project.doctor", REGISTERED, "python scripts/aictl.py project doctor", blocking=False),
                _template("task_approve", "Approve task with owner notes", "taskctl.task.approve", VALIDATED_CTL, "python scripts/taskctl.py task approve <TASK> --notes <NOTES>"),
                _template("task_done", "Move task to done", "task.transition", REGISTERED, "python scripts/aictl.py task transition <TASK> --to done"),
                _template("codex_clear", "Clear closed-task Codex execution state", "codexctl.clear", VALIDATED_CTL, "python scripts/codexctl.py clear"),
                _template("task_validate_after", "Validate task state after close", "taskctl.validate", VALIDATED_CTL, "python scripts/taskctl.py validate"),
                _template("task_generated_after", "Check generated task output after close", "taskctl.check-generated", VALIDATED_CTL, "python scripts/taskctl.py check-generated"),
            ),
        ),
        WorkflowDescriptor(
            name="task.request_changes",
            label="Request changes",
            description=(
                "Record owner change-request notes and transition an in_review "
                "task to changes_requested through validated commands."
            ),
            confirmation_required=True,
            arguments=(
                *task_argument,
                {
                    "name": "notes",
                    "description": "Required change-request notes.",
                    "required": True,
                },
            ),
            steps=(
                _template("resolve", "Resolve task reference", "taskctl.task.resolve", READ_ONLY_CTL, "python scripts/taskctl.py task resolve <TASK> --json"),
                _template("preflight", "Check request-changes gates", "task.request_changes.preflight", READ_ONLY_CTL, "check task status and request notes"),
                _template("task_validate", "Validate task state", "taskctl.validate", VALIDATED_CTL, "python scripts/taskctl.py validate"),
                _template("task_graph", "Validate task graph", "taskctl.task.graph.validate", VALIDATED_CTL, "python scripts/taskctl.py task graph validate"),
                _template("task_generated", "Check generated task output", "taskctl.check-generated", VALIDATED_CTL, "python scripts/taskctl.py check-generated"),
                _template("doctor", "Run project doctor", "project.doctor", REGISTERED, "python scripts/aictl.py project doctor"),
                _template("task_note", "Record change-request notes", "taskctl.task.add_note", VALIDATED_CTL, "python scripts/taskctl.py task add-note <TASK> --text <NOTES>"),
                _template("task_changes_requested", "Move task to changes_requested", "task.transition", REGISTERED, "python scripts/aictl.py task transition <TASK> --to changes_requested"),
                _template("task_validate_after", "Validate task state after request", "taskctl.validate", VALIDATED_CTL, "python scripts/taskctl.py validate"),
                _template("task_generated_after", "Check generated task output after request", "taskctl.check-generated", VALIDATED_CTL, "python scripts/taskctl.py check-generated"),
            ),
        ),
        WorkflowDescriptor(
            name="evolution.create_for_task",
            label="Create Evolution Change",
            description=(
                "Draft an Evolution Change Proposal from a selected Task, add "
                "derived files/risks/impact, link the Task, validate, and move "
                "the Change to ready for separate Human Owner approval."
            ),
            confirmation_required=True,
            arguments=task_argument,
            steps=(
                _template("resolve", "Resolve task reference", "taskctl.task.resolve", READ_ONLY_CTL, "python scripts/taskctl.py task resolve <TASK> --json"),
                _template("change_create", "Create draft Change Proposal", "evolutionctl.change.create", VALIDATED_CTL, "python scripts/evolutionctl.py change create --title <TITLE> --type <TYPE> --status draft --problem <PROBLEM> --proposal <PROPOSAL> --rationale <RATIONALE>"),
                _template("add_affected_files", "Add affected files", "evolutionctl.change.add_affected_file", VALIDATED_CTL, "python scripts/evolutionctl.py change add-affected-file <CHANGE> --text <FILE>"),
                _template("add_risks", "Add risks", "evolutionctl.change.add_risk", VALIDATED_CTL, "python scripts/evolutionctl.py change add-risk <CHANGE> --text <RISK>"),
                _template("add_impact", "Add impact", "evolutionctl.change.add_impact", VALIDATED_CTL, "python scripts/evolutionctl.py change add-impact <CHANGE> --text <IMPACT>"),
                _template("link_task", "Link legacy task ID", "evolutionctl.change.link_task", VALIDATED_CTL, "python scripts/evolutionctl.py change link-task <CHANGE> --task <TASK>"),
                _template("validate_before_ready", "Validate evolution state before ready", "evolutionctl.validate", VALIDATED_CTL, "python scripts/evolutionctl.py validate"),
                _template("ready", "Move Change Proposal to ready", "evolutionctl.change.transition", VALIDATED_CTL, "python scripts/evolutionctl.py change transition <CHANGE> --to ready"),
                _template("validate", "Validate evolution state", "evolutionctl.validate", VALIDATED_CTL, "python scripts/evolutionctl.py validate"),
                _template("check_generated", "Check generated evolution output", "evolutionctl.check-generated", VALIDATED_CTL, "python scripts/evolutionctl.py check-generated"),
            ),
        ),
        WorkflowDescriptor(
            name="evolution.approve_change",
            label="Approve Evolution Change",
            description=(
                "Approve a ready Evolution Change with explicit owner notes "
                "through evolutionctl.py."
            ),
            confirmation_required=True,
            arguments=(
                {
                    "name": "change",
                    "description": "Evolution Change ID.",
                    "required": True,
                },
                {
                    "name": "notes",
                    "description": "Required approval notes.",
                    "required": True,
                },
            ),
            steps=(
                _template("preflight", "Check Change approval gates", "evolution.approve_change.preflight", READ_ONLY_CTL, "check change status and approval notes"),
                _template("evolution_validate", "Validate evolution state", "evolutionctl.validate", VALIDATED_CTL, "python scripts/evolutionctl.py validate"),
                _template("change_approve", "Approve Evolution Change", "evolutionctl.change.approve", VALIDATED_CTL, "python scripts/evolutionctl.py change approve <CHANGE> --notes <NOTES>"),
                _template("evolution_validate_after", "Validate evolution state after approval", "evolutionctl.validate", VALIDATED_CTL, "python scripts/evolutionctl.py validate"),
                _template("evolution_generated_after", "Check generated evolution output after approval", "evolutionctl.check-generated", VALIDATED_CTL, "python scripts/evolutionctl.py check-generated"),
            ),
        ),
        WorkflowDescriptor(
            name="evolution.move_to_review",
            label="Move Evolution Change to review",
            description=(
                "Move an approved or in_progress Evolution Change toward "
                "in_review through valid evolutionctl.py transitions."
            ),
            confirmation_required=True,
            arguments=(
                {
                    "name": "change",
                    "description": "Evolution Change ID.",
                    "required": True,
                },
            ),
            steps=(
                _template("preflight", "Check Change review gates", "evolution.move_to_review.preflight", READ_ONLY_CTL, "check change status"),
                _template("evolution_validate", "Validate evolution state", "evolutionctl.validate", VALIDATED_CTL, "python scripts/evolutionctl.py validate"),
                _template("change_in_progress", "Move approved Change to in_progress if needed", "evolutionctl.change.transition", VALIDATED_CTL, "python scripts/evolutionctl.py change transition <CHANGE> --to in_progress"),
                _template("change_in_review", "Move Change to in_review if needed", "evolutionctl.change.transition", VALIDATED_CTL, "python scripts/evolutionctl.py change transition <CHANGE> --to in_review"),
                _template("evolution_validate_after", "Validate evolution state after review transition", "evolutionctl.validate", VALIDATED_CTL, "python scripts/evolutionctl.py validate"),
                _template("evolution_generated_after", "Check generated evolution output after review transition", "evolutionctl.check-generated", VALIDATED_CTL, "python scripts/evolutionctl.py check-generated"),
            ),
        ),
        WorkflowDescriptor(
            name="evolution.accept_change",
            label="Accept Evolution Change",
            description=(
                "Accept an approved or in_review Evolution Change only after linked "
                "task completion checks pass; no task waivers or skip-task-check are used."
            ),
            confirmation_required=True,
            arguments=(
                {
                    "name": "change",
                    "description": "Evolution Change ID.",
                    "required": True,
                },
                {
                    "name": "notes",
                    "description": "Required acceptance notes.",
                    "required": True,
                },
            ),
            steps=(
                _template("preflight", "Check Change acceptance gates", "evolution.accept_change.preflight", READ_ONLY_CTL, "check change status and linked tasks"),
                _template("evolution_validate", "Validate evolution state", "evolutionctl.validate", VALIDATED_CTL, "python scripts/evolutionctl.py validate"),
                _template("change_in_progress", "Move approved Change to in_progress if needed", "evolutionctl.change.transition", VALIDATED_CTL, "python scripts/evolutionctl.py change transition <CHANGE> --to in_progress"),
                _template("change_in_review", "Move Change to in_review if needed", "evolutionctl.change.transition", VALIDATED_CTL, "python scripts/evolutionctl.py change transition <CHANGE> --to in_review"),
                _template("change_accept", "Accept Evolution Change", "evolutionctl.change.accept", VALIDATED_CTL, "python scripts/evolutionctl.py change accept <CHANGE> --notes <NOTES>"),
                _template("evolution_validate_after", "Validate evolution state after acceptance", "evolutionctl.validate", VALIDATED_CTL, "python scripts/evolutionctl.py validate"),
                _template("evolution_generated_after", "Check generated evolution output after acceptance", "evolutionctl.check-generated", VALIDATED_CTL, "python scripts/evolutionctl.py check-generated"),
            ),
        ),
        WorkflowDescriptor(
            name="epic.close_if_complete",
            label="Close Epic if complete",
            description=(
                "Transition an active Epic to done only when all child Tasks are "
                "done, deferred, or archived."
            ),
            confirmation_required=True,
            arguments=(
                {
                    "name": "epic",
                    "description": "Epic ID or key.",
                    "required": True,
                },
            ),
            steps=(
                _template("preflight", "Check Epic closure gates", "epic.close_if_complete.preflight", READ_ONLY_CTL, "check epic child task statuses"),
                _template("plan_validate", "Validate plan state", "planctl.validate", VALIDATED_CTL, "python scripts/planctl.py validate"),
                _template("task_validate", "Validate task state", "taskctl.validate", VALIDATED_CTL, "python scripts/taskctl.py validate"),
                _template("epic_done", "Move Epic to done", "planctl.epic.status", VALIDATED_CTL, "python scripts/planctl.py epic status <EPIC> --to done"),
                _template("plan_validate_after", "Validate plan state after close", "planctl.validate", VALIDATED_CTL, "python scripts/planctl.py validate"),
                _template("plan_render", "Render plan generated output", "planctl.render", VALIDATED_CTL, "python scripts/planctl.py render"),
            ),
        ),
    )


def _template(
    step_id: str,
    title: str,
    command_name: str,
    route: str,
    command_template: str,
    *,
    blocking: bool = True,
) -> WorkflowStepTemplate:
    return WorkflowStepTemplate(
        step_id=step_id,
        title=title,
        command_name=command_name,
        route=route,
        command_template=tuple(command_template.split()),
        blocking=blocking,
    )


def _get_workflow_descriptor(name: str) -> WorkflowDescriptor:
    for descriptor in _workflow_descriptors():
        if descriptor.name == name:
            return descriptor
    raise WorkflowError("WORKFLOW_NOT_FOUND", "Unknown workflow: {}".format(name))


def _build_steps(
    workflow_name: str,
    *,
    task: Mapping[str, Any],
    root: Path,
    actor: str,
    python_executable: str,
    include_resolve: bool,
    change_preview: Mapping[str, Any] | None = None,
    change_id: str = "<CHANGE>",
    notes: str = "",
) -> list[WorkflowStep]:
    task_id = str(task.get("id") or "<task>")
    status = str(task.get("status") or "")
    steps: list[WorkflowStep] = []
    if include_resolve:
        steps.append(
            _resolve_step(
                task_id,
                root=root,
                actor=actor,
                python_executable=python_executable,
            )
        )

    if workflow_name == "task.prepare_for_codex":
        steps.extend(
            [
                _aictl_step("current_set", "Set current task", "current.set", root, actor, python_executable, "current", "set", task_id),
                _ctl_step("task_validate", "Validate task state", "taskctl.validate", "taskctl.py", root, actor, python_executable, "validate"),
                _ctl_step("task_graph", "Validate task graph", "taskctl.task.graph.validate", "taskctl.py", root, actor, python_executable, "task", "graph", "validate"),
                _aictl_step(
                    "task_in_progress",
                    "Move task to in_progress when needed",
                    "task.transition",
                    root,
                    actor,
                    python_executable,
                    "task",
                    "transition",
                    task_id,
                    "--to",
                    "in_progress",
                    skip_reason=(
                        "Task is already in_progress."
                        if status == "in_progress"
                        else ""
                    ),
                ),
                _aictl_step("context_build", "Build task Context Pack", "context.build", root, actor, python_executable, "context", "build", "--task", task_id, "--write"),
                _aictl_step("codex_build", "Build Codex prompt with context", "codex.prompt.build", root, actor, python_executable, "codex", "prompt", "build", "--task", task_id, "--with-context"),
                _aictl_step("doctor", "Run project doctor", "project.doctor", root, actor, python_executable, "project", "doctor"),
            ]
        )
        return steps

    if workflow_name == "task.refresh_execution_context":
        steps.extend(
            [
                _aictl_step("context_build", "Build task Context Pack", "context.build", root, actor, python_executable, "context", "build", "--task", task_id, "--write"),
                _ctl_step("context_check", "Check generated context output", "contextctl.check-generated", "contextctl.py", root, actor, python_executable, "check-generated"),
                _aictl_step("codex_build", "Build Codex prompt with context", "codex.prompt.build", root, actor, python_executable, "codex", "prompt", "build", "--task", task_id, "--with-context"),
            ]
        )
        return steps

    if workflow_name == "task.submit_for_review":
        steps.extend(
            [
                _ctl_step("task_validate", "Validate task state", "taskctl.validate", "taskctl.py", root, actor, python_executable, "validate"),
                _ctl_step("task_graph", "Validate task graph", "taskctl.task.graph.validate", "taskctl.py", root, actor, python_executable, "task", "graph", "validate"),
                _ctl_step("task_generated", "Check generated task output", "taskctl.check-generated", "taskctl.py", root, actor, python_executable, "check-generated"),
                _ctl_step("context_validate", "Validate context control", "contextctl.validate", "contextctl.py", root, actor, python_executable, "validate"),
                _ctl_step("context_generated", "Check generated context output", "contextctl.check-generated", "contextctl.py", root, actor, python_executable, "check-generated"),
                _ctl_step("evolution_validate", "Validate evolution state", "evolutionctl.validate", "evolutionctl.py", root, actor, python_executable, "validate"),
                _ctl_step("evolution_generated", "Check generated evolution output", "evolutionctl.check-generated", "evolutionctl.py", root, actor, python_executable, "check-generated"),
                _protected_step(root, python_executable),
                _aictl_step("doctor", "Run project doctor", "project.doctor", root, actor, python_executable, "project", "doctor"),
                _aictl_step(
                    "task_review",
                    "Move task to in_review",
                    "task.transition",
                    root,
                    actor,
                    python_executable,
                    "task",
                    "transition",
                    task_id,
                    "--to",
                    "in_review",
                    skip_reason=(
                        "Task is already in_review."
                        if status == "in_review"
                        else ""
                    ),
                ),
            ]
        )
        return steps

    if workflow_name == "task.close_reviewed":
        steps.extend(
            [
                _ctl_step("task_validate", "Validate task state", "taskctl.validate", "taskctl.py", root, actor, python_executable, "validate"),
                _ctl_step("task_graph", "Validate task graph", "taskctl.task.graph.validate", "taskctl.py", root, actor, python_executable, "task", "graph", "validate"),
                _ctl_step("task_generated", "Check generated task output", "taskctl.check-generated", "taskctl.py", root, actor, python_executable, "check-generated"),
                _ctl_step("context_validate", "Validate context control", "contextctl.validate", "contextctl.py", root, actor, python_executable, "validate"),
                _ctl_step(
                    "context_generated",
                    "Check generated context output",
                    "contextctl.check-generated",
                    "contextctl.py",
                    root,
                    actor,
                    python_executable,
                    "check-generated",
                    blocking=False,
                ),
                _ctl_step("evolution_validate", "Validate evolution state", "evolutionctl.validate", "evolutionctl.py", root, actor, python_executable, "validate"),
                _ctl_step("evolution_generated", "Check generated evolution output", "evolutionctl.check-generated", "evolutionctl.py", root, actor, python_executable, "check-generated"),
                _protected_step(
                    root,
                    python_executable,
                    prompt_context_errors_are_warnings=True,
                ),
                _aictl_step("doctor", "Run project doctor", "project.doctor", root, actor, python_executable, "project", "doctor", blocking=False),
                _ctl_step("task_approve", "Approve task with owner notes", "taskctl.task.approve", "taskctl.py", root, actor, python_executable, "task", "approve", task_id, "--notes", notes),
                _aictl_step("task_done", "Move task to done", "task.transition", root, actor, python_executable, "task", "transition", task_id, "--to", "done"),
                _ctl_step(
                    "codex_clear",
                    "Clear closed-task Codex execution state",
                    "codexctl.clear",
                    "codexctl.py",
                    root,
                    actor,
                    python_executable,
                    "clear",
                    skip_reason=(
                        ""
                        if _current_execution_targets_task(root, task)
                        else "Current Codex execution does not target this task."
                    ),
                ),
                _ctl_step("task_validate_after", "Validate task state after close", "taskctl.validate", "taskctl.py", root, actor, python_executable, "validate"),
                _ctl_step("task_generated_after", "Check generated task output after close", "taskctl.check-generated", "taskctl.py", root, actor, python_executable, "check-generated"),
            ]
        )
        return steps

    if workflow_name == "task.request_changes":
        steps.extend(
            [
                _ctl_step("task_validate", "Validate task state", "taskctl.validate", "taskctl.py", root, actor, python_executable, "validate"),
                _ctl_step("task_graph", "Validate task graph", "taskctl.task.graph.validate", "taskctl.py", root, actor, python_executable, "task", "graph", "validate"),
                _ctl_step("task_generated", "Check generated task output", "taskctl.check-generated", "taskctl.py", root, actor, python_executable, "check-generated"),
                _aictl_step("doctor", "Run project doctor", "project.doctor", root, actor, python_executable, "project", "doctor"),
                _ctl_step("task_note", "Record change-request notes", "taskctl.task.add_note", "taskctl.py", root, actor, python_executable, "task", "add-note", task_id, "--text", notes),
                _aictl_step("task_changes_requested", "Move task to changes_requested", "task.transition", root, actor, python_executable, "task", "transition", task_id, "--to", "changes_requested"),
                _ctl_step("task_validate_after", "Validate task state after request", "taskctl.validate", "taskctl.py", root, actor, python_executable, "validate"),
                _ctl_step("task_generated_after", "Check generated task output after request", "taskctl.check-generated", "taskctl.py", root, actor, python_executable, "check-generated"),
            ]
        )
        return steps

    if workflow_name == "evolution.create_for_task":
        preview = dict(change_preview or _derive_evolution_change(task))
        steps.append(
            _evolution_change_create_step(
                task,
                preview,
                root,
                actor,
                python_executable,
            )
        )
        steps.extend(
            _evolution_change_followup_steps(
                task,
                preview,
                change_id,
                root,
                actor,
                python_executable,
            )
        )
        return steps

    raise WorkflowError("WORKFLOW_NOT_FOUND", "Unknown workflow: {}".format(workflow_name))


def _build_change_approve_steps(
    change: Mapping[str, Any],
    *,
    root: Path,
    actor: str,
    python_executable: str,
    notes: str,
) -> list[WorkflowStep]:
    change_id = str(change.get("id") or "<change>")
    return [
        _ctl_step(
            "evolution_validate",
            "Validate evolution state",
            "evolutionctl.validate",
            "evolutionctl.py",
            root,
            actor,
            python_executable,
            "validate",
        ),
        _ctl_step(
            "change_approve",
            "Approve Evolution Change",
            "evolutionctl.change.approve",
            "evolutionctl.py",
            root,
            actor,
            python_executable,
            "change",
            "approve",
            change_id,
            "--notes",
            notes,
        ),
        _ctl_step(
            "evolution_validate_after",
            "Validate evolution state after approval",
            "evolutionctl.validate",
            "evolutionctl.py",
            root,
            actor,
            python_executable,
            "validate",
        ),
        _ctl_step(
            "evolution_generated_after",
            "Check generated evolution output after approval",
            "evolutionctl.check-generated",
            "evolutionctl.py",
            root,
            actor,
            python_executable,
            "check-generated",
        ),
    ]


def _build_change_review_steps(
    change: Mapping[str, Any],
    *,
    root: Path,
    actor: str,
    python_executable: str,
) -> list[WorkflowStep]:
    change_id = str(change.get("id") or "<change>")
    status = str(change.get("status") or "")
    return [
        _ctl_step(
            "evolution_validate",
            "Validate evolution state",
            "evolutionctl.validate",
            "evolutionctl.py",
            root,
            actor,
            python_executable,
            "validate",
        ),
        _ctl_step(
            "change_in_progress",
            "Move approved Change to in_progress",
            "evolutionctl.change.transition",
            "evolutionctl.py",
            root,
            actor,
            python_executable,
            "change",
            "transition",
            change_id,
            "--to",
            "in_progress",
            skip_reason=(
                "Change is already in_progress or in_review."
                if status in {"in_progress", "in_review"}
                else ""
            ),
        ),
        _ctl_step(
            "change_in_review",
            "Move Change to in_review",
            "evolutionctl.change.transition",
            "evolutionctl.py",
            root,
            actor,
            python_executable,
            "change",
            "transition",
            change_id,
            "--to",
            "in_review",
            skip_reason="Change is already in_review." if status == "in_review" else "",
        ),
        _ctl_step(
            "evolution_validate_after",
            "Validate evolution state after review transition",
            "evolutionctl.validate",
            "evolutionctl.py",
            root,
            actor,
            python_executable,
            "validate",
        ),
        _ctl_step(
            "evolution_generated_after",
            "Check generated evolution output after review transition",
            "evolutionctl.check-generated",
            "evolutionctl.py",
            root,
            actor,
            python_executable,
            "check-generated",
        ),
    ]


def _build_change_accept_steps(
    change: Mapping[str, Any],
    *,
    root: Path,
    actor: str,
    python_executable: str,
    notes: str,
) -> list[WorkflowStep]:
    change_id = str(change.get("id") or "<change>")
    status = str(change.get("status") or "")
    steps = [
        _ctl_step(
            "evolution_validate",
            "Validate evolution state",
            "evolutionctl.validate",
            "evolutionctl.py",
            root,
            actor,
            python_executable,
            "validate",
        )
    ]
    if status == "approved":
        steps.extend(
            [
                _ctl_step(
                    "change_in_progress",
                    "Move approved Change to in_progress",
                    "evolutionctl.change.transition",
                    "evolutionctl.py",
                    root,
                    actor,
                    python_executable,
                    "change",
                    "transition",
                    change_id,
                    "--to",
                    "in_progress",
                ),
                _ctl_step(
                    "change_in_review",
                    "Move Change to in_review",
                    "evolutionctl.change.transition",
                    "evolutionctl.py",
                    root,
                    actor,
                    python_executable,
                    "change",
                    "transition",
                    change_id,
                    "--to",
                    "in_review",
                ),
            ]
        )
    steps.extend(
        [
            _ctl_step(
                "change_accept",
                "Accept Evolution Change",
                "evolutionctl.change.accept",
                "evolutionctl.py",
                root,
                actor,
                python_executable,
                "change",
                "accept",
                change_id,
                "--notes",
                notes,
            ),
            _ctl_step(
                "evolution_validate_after",
                "Validate evolution state after acceptance",
                "evolutionctl.validate",
                "evolutionctl.py",
                root,
                actor,
                python_executable,
                "validate",
            ),
            _ctl_step(
                "evolution_generated_after",
                "Check generated evolution output after acceptance",
                "evolutionctl.check-generated",
                "evolutionctl.py",
                root,
                actor,
                python_executable,
                "check-generated",
            ),
        ]
    )
    return steps


def _build_epic_close_steps(
    epic: Mapping[str, Any],
    *,
    root: Path,
    actor: str,
    python_executable: str,
) -> list[WorkflowStep]:
    epic_id = str(epic.get("id") or "<epic>")
    status = str(epic.get("status") or "")
    return [
        _ctl_step(
            "plan_validate",
            "Validate plan state",
            "planctl.validate",
            "planctl.py",
            root,
            actor,
            python_executable,
            "validate",
        ),
        _ctl_step(
            "task_validate",
            "Validate task state",
            "taskctl.validate",
            "taskctl.py",
            root,
            actor,
            python_executable,
            "validate",
        ),
        _ctl_step(
            "epic_done",
            "Move Epic to done",
            "planctl.epic.status",
            "planctl.py",
            root,
            actor,
            python_executable,
            "epic",
            "status",
            epic_id,
            "--to",
            "done",
        )
        if status != "done"
        else WorkflowStep(
            step_id="epic_done",
            title="Move Epic to done",
            command_name="planctl.epic.status",
            route=VALIDATED_CTL,
            argv=(
                python_executable,
                str(root / "scripts" / "planctl.py"),
                "--root",
                str(root),
                "--actor",
                actor,
                "epic",
                "status",
                epic_id,
                "--to",
                "done",
            ),
            skip_reason="Epic is already done.",
        ),
        _ctl_step(
            "plan_validate_after",
            "Validate plan state after close",
            "planctl.validate",
            "planctl.py",
            root,
            actor,
            python_executable,
            "validate",
        ),
        _ctl_step(
            "plan_render",
            "Render plan generated output",
            "planctl.render",
            "planctl.py",
            root,
            actor,
            python_executable,
            "render",
        ),
    ]


def _build_task_create_steps(
    request: TaskCreateRequest,
    *,
    root: Path,
    actor: str,
    python_executable: str,
    created_task_id: str,
    include_create: bool = True,
) -> list[WorkflowStep]:
    steps: list[WorkflowStep] = []
    if include_create:
        steps.append(_task_create_step(request, root, actor, python_executable))
    for index, dependency in enumerate(request.depends_on, start=1):
        steps.append(
            _task_dependency_step(
                request,
                created_task_id,
                dependency,
                index,
                root,
                actor,
                python_executable,
            )
        )
    steps.extend(
        [
            _ctl_step(
                "task_validate",
                "Validate task state",
                "taskctl.validate",
                "taskctl.py",
                root,
                actor,
                python_executable,
                "validate",
            ),
            _ctl_step(
                "task_graph",
                "Validate task graph",
                "taskctl.task.graph.validate",
                "taskctl.py",
                root,
                actor,
                python_executable,
                "task",
                "graph",
                "validate",
            ),
            _ctl_step(
                "task_generated",
                "Check generated task output",
                "taskctl.check-generated",
                "taskctl.py",
                root,
                actor,
                python_executable,
                "check-generated",
            ),
        ]
    )
    return steps


def _task_create_step(
    request: TaskCreateRequest,
    root: Path,
    actor: str,
    python_executable: str,
) -> WorkflowStep:
    args = [
        "task",
        "create",
        "--epic",
        request.epic,
        "--title",
        request.title,
        "--priority",
        str(request.priority),
        "--status",
        request.status,
        "--verification-mode",
        request.verification_mode,
    ]
    for flag, value in (
        ("--summary", request.summary),
        ("--description", request.description),
        ("--active-role", request.active_role),
        ("--active-stage", request.active_stage),
        ("--active-document", request.active_document),
        ("--expected-result", request.expected_result),
    ):
        if value:
            args.extend([flag, value])
    _extend_repeated(args, "--scope", request.scope)
    _extend_repeated(args, "--out-of-scope", request.out_of_scope)
    _extend_repeated(args, "--allowed-file", request.allowed_files)
    _extend_repeated(args, "--acceptance", request.acceptance)
    _extend_repeated(args, "--review-instruction", request.review_instructions)
    _extend_repeated(args, "--note", request.notes)

    return _ctl_step(
        "task_create",
        "Create task",
        "task.create",
        "taskctl.py",
        root,
        actor,
        python_executable,
        *args,
    )


def _task_dependency_step(
    request: TaskCreateRequest,
    created_task_id: str,
    dependency: str,
    index: int,
    root: Path,
    actor: str,
    python_executable: str,
) -> WorkflowStep:
    args = [
        "task",
        "deps",
        "add",
        created_task_id,
        "--after",
        dependency,
        "--type",
        "hard",
    ]
    if request.dependency_reason:
        args.extend(["--reason", request.dependency_reason])
    return _ctl_step(
        "task_dependency_{}".format(index),
        "Add task dependency",
        "taskctl.task.deps.add",
        "taskctl.py",
        root,
        actor,
        python_executable,
        *args,
    )


def _extend_repeated(args: list[str], flag: str, values: Sequence[str]) -> None:
    for value in values:
        text = str(value).strip()
        if text:
            args.extend([flag, text])


def _task_create_result(
    descriptor: WorkflowDescriptor,
    request: TaskCreateRequest,
    *,
    created_task_id: str,
    step_results: Sequence[WorkflowStepResult],
    message: str,
) -> CommandResult:
    failed = next((item for item in step_results if not item.ok), None)
    result = CommandResult(
        ok=failed is None,
        command=descriptor.name,
        domain="workflow",
        message=message,
        data={
            "workflow": descriptor.to_dict(),
            "request": request.to_dict(),
            "created_task_id": created_task_id,
            "create_only": True,
            "steps": [item.to_dict() for item in step_results],
        },
        generated_files=[
            "AI_PROJECT/generated/CODEX_TASKS.md",
            "AI_PROJECT/generated/CODEX_CURRENT.md",
            "AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md",
        ],
        events=["AI_PROJECT/events/task-events.jsonl"],
    )
    if failed is not None:
        result.errors.append(
            CommandMessage(
                code="WORKFLOW_STEP_FAILED",
                message="Workflow step failed: {}".format(failed.step.title),
                details={
                    "step": failed.step.step_id,
                    "command_name": failed.step.command_name,
                    "returncode": failed.returncode,
                    "stdout": failed.stdout,
                    "stderr": failed.stderr,
                },
            )
        )
    return result


BULK_IMPORT_MAX_BYTES = 262_144
BULK_IMPORT_MAX_TASKS = 50
BULK_IMPORT_ALLOWED_STATUSES = {"proposed", "planned", "ready"}
BULK_IMPORT_ALLOWED_VERIFICATION_MODES = {"light", "manual", "none", "standard", "strict"}
BULK_IMPORT_ALLOWED_FIELDS = {
    "acceptance",
    "acceptance_criteria",
    "active_document",
    "active_role",
    "active_stage",
    "allowed_file",
    "allowed_files",
    "dependencies",
    "dependency_reason",
    "depends_on",
    "description",
    "epic",
    "expected_result",
    "notes",
    "out_of_scope",
    "priority",
    "review",
    "review_instruction",
    "review_instructions",
    "scope",
    "status",
    "summary",
    "title",
    "verification_mode",
}


def _prepare_task_bulk_import(
    request: TaskBulkImportRequest,
    *,
    root: Path,
    actor: str,
    python_executable: str,
) -> tuple[tuple[TaskCreateRequest, ...], dict[str, Any]]:
    task_requests = _parse_task_bulk_import_requests(request)
    _validate_task_bulk_import_references(root, task_requests)
    steps = _task_bulk_import_steps(
        task_requests,
        root=root,
        actor=actor,
        python_executable=python_executable,
    )
    preview_tasks = []
    for index, task_request in enumerate(task_requests, start=1):
        preview_tasks.append(
            {
                "index": index,
                "task": task_request.to_dict(),
                "dependencies": list(task_request.depends_on),
            }
        )
    return task_requests, {
        "request": request.to_dict(),
        "format": "json",
        "task_count": len(task_requests),
        "create_only": True,
        "dry_run": True,
        "tasks": preview_tasks,
        "steps": steps,
    }


def _parse_task_bulk_import_requests(
    request: TaskBulkImportRequest,
) -> tuple[TaskCreateRequest, ...]:
    text = request.source_text.strip()
    if not text:
        raise WorkflowError(
            "TASK_IMPORT_EMPTY",
            "Bulk task import payload is empty.",
        )
    if len(text.encode("utf-8")) > BULK_IMPORT_MAX_BYTES:
        raise WorkflowError(
            "TASK_IMPORT_TOO_LARGE",
            "Bulk task import payload is too large.",
            details={"max_bytes": BULK_IMPORT_MAX_BYTES},
        )

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise WorkflowError(
            "TASK_IMPORT_INVALID_JSON",
            "Bulk task import payload must be JSON.",
            details={"error": str(exc)},
        ) from exc

    if isinstance(payload, list):
        raw_tasks = payload
    elif isinstance(payload, dict):
        if "tasks" in payload:
            unknown = sorted(set(payload) - {"tasks"})
            if unknown:
                raise WorkflowError(
                    "TASK_IMPORT_UNKNOWN_FIELD",
                    "Bulk task import top-level object has unsupported fields.",
                    details={"fields": unknown},
                )
            raw_tasks = payload.get("tasks")
        elif {"epic", "title"}.issubset(payload):
            raw_tasks = [payload]
        else:
            raise WorkflowError(
                "TASK_IMPORT_MISSING_TASKS",
                "Bulk task import JSON must be an array or an object with a tasks array.",
            )
    else:
        raise WorkflowError(
            "TASK_IMPORT_INVALID_SHAPE",
            "Bulk task import JSON must be an array or object.",
        )

    if not isinstance(raw_tasks, list):
        raise WorkflowError(
            "TASK_IMPORT_INVALID_TASKS",
            "Bulk task import tasks field must be an array.",
        )
    if not raw_tasks:
        raise WorkflowError(
            "TASK_IMPORT_EMPTY_TASKS",
            "Bulk task import must include at least one task.",
        )
    if len(raw_tasks) > BULK_IMPORT_MAX_TASKS:
        raise WorkflowError(
            "TASK_IMPORT_TOO_MANY_TASKS",
            "Bulk task import includes too many tasks.",
            details={"max_tasks": BULK_IMPORT_MAX_TASKS, "task_count": len(raw_tasks)},
        )

    parsed: list[TaskCreateRequest] = []
    for index, item in enumerate(raw_tasks, start=1):
        path = "tasks[{}]".format(index - 1)
        if not isinstance(item, dict):
            raise WorkflowError(
                "TASK_IMPORT_INVALID_TASK",
                "Imported task must be a JSON object.",
                path=path,
            )
        parsed.append(_parse_task_import_item(item, path=path))
    return tuple(parsed)


def _parse_task_import_item(item: Mapping[str, Any], *, path: str) -> TaskCreateRequest:
    unknown = sorted(set(item) - BULK_IMPORT_ALLOWED_FIELDS)
    if unknown:
        raise WorkflowError(
            "TASK_IMPORT_UNKNOWN_FIELD",
            "Imported task has unsupported fields.",
            path=path,
            details={"fields": unknown},
        )

    status = _optional_import_string(item, "status", path=path) or "planned"
    if status not in BULK_IMPORT_ALLOWED_STATUSES:
        raise WorkflowError(
            "TASK_IMPORT_UNSAFE_STATUS",
            "Bulk import may only create proposed, planned, or ready tasks.",
            path="{}.status".format(path),
            details={
                "status": status,
                "allowed": sorted(BULK_IMPORT_ALLOWED_STATUSES),
            },
        )

    verification_mode = (
        _optional_import_string(item, "verification_mode", path=path) or "standard"
    )
    if verification_mode not in BULK_IMPORT_ALLOWED_VERIFICATION_MODES:
        raise WorkflowError(
            "TASK_IMPORT_INVALID_VERIFICATION_MODE",
            "Bulk import verification mode is not supported.",
            path="{}.verification_mode".format(path),
            details={
                "verification_mode": verification_mode,
                "allowed": sorted(BULK_IMPORT_ALLOWED_VERIFICATION_MODES),
            },
        )

    return TaskCreateRequest(
        epic=_required_import_string(item, "epic", path=path),
        title=_required_import_string(item, "title", path=path),
        summary=_optional_import_string(item, "summary", path=path),
        description=_optional_import_string(item, "description", path=path),
        priority=_optional_import_int(item, "priority", path=path, default=1),
        status=status,
        active_role=_optional_import_string(item, "active_role", path=path),
        active_stage=_optional_import_string(item, "active_stage", path=path),
        active_document=_optional_import_string(item, "active_document", path=path),
        expected_result=_optional_import_string(item, "expected_result", path=path),
        verification_mode=verification_mode,
        scope=_import_string_list(item, path=path, names=("scope",)),
        out_of_scope=_import_string_list(item, path=path, names=("out_of_scope",)),
        allowed_files=_import_string_list(
            item,
            path=path,
            names=("allowed_files", "allowed_file"),
        ),
        acceptance=_import_string_list(
            item,
            path=path,
            names=("acceptance_criteria", "acceptance"),
        ),
        review_instructions=_import_string_list(
            item,
            path=path,
            names=("review_instructions", "review_instruction", "review"),
        ),
        notes=_import_string_list(item, path=path, names=("notes",)),
        depends_on=_import_string_list(
            item,
            path=path,
            names=("dependencies", "depends_on"),
        ),
        dependency_reason=_optional_import_string(item, "dependency_reason", path=path),
    )


def _required_import_string(
    item: Mapping[str, Any],
    name: str,
    *,
    path: str,
) -> str:
    value = _optional_import_string(item, name, path=path)
    if not value:
        raise WorkflowError(
            "TASK_IMPORT_MISSING_REQUIRED_FIELD",
            "Imported task is missing required field: {}".format(name),
            path="{}.{}".format(path, name),
        )
    return value


def _optional_import_string(
    item: Mapping[str, Any],
    name: str,
    *,
    path: str,
) -> str:
    if name not in item or item.get(name) is None:
        return ""
    value = item.get(name)
    if not isinstance(value, str):
        raise WorkflowError(
            "TASK_IMPORT_INVALID_FIELD_TYPE",
            "Imported task field must be a string: {}".format(name),
            path="{}.{}".format(path, name),
            details={"type": type(value).__name__},
        )
    return value.strip()


def _optional_import_int(
    item: Mapping[str, Any],
    name: str,
    *,
    path: str,
    default: int,
) -> int:
    if name not in item or item.get(name) is None:
        return default
    value = item.get(name)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    raise WorkflowError(
        "TASK_IMPORT_INVALID_FIELD_TYPE",
        "Imported task field must be an integer: {}".format(name),
        path="{}.{}".format(path, name),
        details={"type": type(value).__name__},
    )


def _import_string_list(
    item: Mapping[str, Any],
    *,
    path: str,
    names: Sequence[str],
) -> tuple[str, ...]:
    values: list[str] = []
    for name in names:
        if name not in item or item.get(name) is None:
            continue
        value = item.get(name)
        field_path = "{}.{}".format(path, name)
        if isinstance(value, str):
            values.extend(line.strip() for line in value.splitlines() if line.strip())
            continue
        if isinstance(value, list):
            for list_index, child in enumerate(value):
                if not isinstance(child, str):
                    raise WorkflowError(
                        "TASK_IMPORT_INVALID_FIELD_TYPE",
                        "Imported list field items must be strings.",
                        path="{}[{}]".format(field_path, list_index),
                        details={"type": type(child).__name__},
                    )
                text = child.strip()
                if text:
                    values.append(text)
            continue
        raise WorkflowError(
            "TASK_IMPORT_INVALID_FIELD_TYPE",
            "Imported task field must be a string or string array.",
            path=field_path,
            details={"type": type(value).__name__},
        )
    return tuple(values)


def _validate_task_bulk_import_references(
    root: Path,
    task_requests: Sequence[TaskCreateRequest],
) -> None:
    epic_refs = _load_importable_epic_refs(root)
    tasks = _load_import_dependency_tasks(root)
    for index, request in enumerate(task_requests, start=1):
        path = "tasks[{}]".format(index - 1)
        if request.epic not in epic_refs:
            raise WorkflowError(
                "TASK_IMPORT_UNKNOWN_EPIC",
                "Imported task references an unknown or inactive Epic.",
                path="{}.epic".format(path),
                details={"epic": request.epic},
            )
        for dependency in request.depends_on:
            if not any(_task_matches_ref(task, dependency) for task in tasks):
                raise WorkflowError(
                    "TASK_IMPORT_UNKNOWN_DEPENDENCY",
                    "Imported task dependency does not reference an existing Task.",
                    path="{}.dependencies".format(path),
                    details={"dependency": dependency},
                )


def _load_importable_epic_refs(root: Path) -> set[str]:
    path = root / "AI_PROJECT" / "state" / "plan.json"
    payload = _load_json_object(path, code_prefix="TASK_IMPORT_PLAN")
    epics = payload.get("epics")
    if not isinstance(epics, list):
        raise WorkflowError(
            "TASK_IMPORT_PLAN_INVALID_SHAPE",
            "Plan state must contain an epics list.",
            details={"path": str(path)},
        )
    refs: set[str] = set()
    for epic in epics:
        if not isinstance(epic, dict):
            continue
        status = str(epic.get("status") or "")
        if status in {"done", "deferred", "archived"}:
            continue
        for field in ("id", "key"):
            ref = str(epic.get(field) or "").strip()
            if ref:
                refs.add(ref)
    return refs


def _load_import_dependency_tasks(root: Path) -> list[dict[str, Any]]:
    path = root / "AI_PROJECT" / "state" / "tasks.json"
    payload = _load_json_object(path, code_prefix="TASK_IMPORT_TASK")
    tasks = payload.get("tasks")
    if not isinstance(tasks, list):
        raise WorkflowError(
            "TASK_IMPORT_TASK_STATE_INVALID_SHAPE",
            "Task state must contain a tasks list.",
            details={"path": str(path)},
        )
    return [dict(task) for task in tasks if isinstance(task, dict)]


def _load_json_object(path: Path, *, code_prefix: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise WorkflowError(
            "{}_STATE_MISSING".format(code_prefix),
            "Project-control state file is missing: {}".format(path),
            details={"path": str(path)},
        ) from exc
    except json.JSONDecodeError as exc:
        raise WorkflowError(
            "{}_STATE_INVALID_JSON".format(code_prefix),
            "Project-control state file is not valid JSON: {}".format(path),
            details={"path": str(path), "error": str(exc)},
        ) from exc
    if not isinstance(payload, dict):
        raise WorkflowError(
            "{}_STATE_INVALID_SHAPE".format(code_prefix),
            "Project-control state file must contain a JSON object: {}".format(path),
            details={"path": str(path)},
        )
    return payload


def _task_bulk_import_steps(
    task_requests: Sequence[TaskCreateRequest],
    *,
    root: Path,
    actor: str,
    python_executable: str,
) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for index, task_request in enumerate(task_requests, start=1):
        task_placeholder = "<TASK_{}>".format(index)
        for step in _build_task_create_steps(
            task_request,
            root=root,
            actor=actor,
            python_executable=python_executable,
            created_task_id=task_placeholder,
        ):
            data = step.preview_dict()
            data["import_index"] = index
            data["import_title"] = task_request.title
            steps.append(data)
    return steps


def _load_task_for_preview(root: Path, task_ref: str) -> dict[str, Any] | None:
    try:
        return _load_task_from_state(root, task_ref)
    except WorkflowError:
        return None


def _load_task_by_id(root: Path, task_id: str) -> dict[str, Any]:
    return _load_task_from_state(root, task_id, exact_id=True)


def _load_task_from_state(
    root: Path,
    task_ref: str,
    *,
    exact_id: bool = False,
) -> dict[str, Any]:
    path = root / "AI_PROJECT" / "state" / "tasks.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise WorkflowError(
            "WORKFLOW_TASK_STATE_MISSING",
            "Task state is missing: {}".format(path),
            details={"path": str(path)},
        ) from exc
    except json.JSONDecodeError as exc:
        raise WorkflowError(
            "WORKFLOW_TASK_STATE_INVALID_JSON",
            "Task state is not valid JSON: {}".format(path),
            details={"path": str(path), "error": str(exc)},
        ) from exc

    tasks = payload.get("tasks")
    if not isinstance(tasks, list):
        raise WorkflowError(
            "WORKFLOW_TASK_STATE_INVALID_SHAPE",
            "Task state must contain a tasks list.",
            details={"path": str(path)},
        )

    for task in tasks:
        if not isinstance(task, dict):
            continue
        if exact_id and task.get("id") == task_ref:
            return dict(task)
        if not exact_id and _task_matches_ref(task, task_ref):
            return dict(task)

    raise WorkflowError(
        "WORKFLOW_TASK_NOT_FOUND",
        "Task was not found in task state: {}".format(task_ref),
        details={"task_ref": task_ref, "path": str(path)},
    )


def _load_json_state(root: Path, filename: str, *, expected_list: str) -> dict[str, Any]:
    path = root / "AI_PROJECT" / "state" / filename
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise WorkflowError(
            "WORKFLOW_STATE_MISSING",
            "Project-control state is missing: {}".format(path),
            details={"path": str(path)},
        ) from exc
    except json.JSONDecodeError as exc:
        raise WorkflowError(
            "WORKFLOW_STATE_INVALID_JSON",
            "Project-control state is not valid JSON: {}".format(path),
            details={"path": str(path), "error": str(exc)},
        ) from exc
    if not isinstance(payload.get(expected_list), list):
        raise WorkflowError(
            "WORKFLOW_STATE_INVALID_SHAPE",
            "Project-control state must contain a {} list: {}".format(
                expected_list,
                path,
            ),
            details={"path": str(path), "field": expected_list},
        )
    return payload


def _load_change_accept_context(
    root: Path,
    change_ref: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    evolution = _load_json_state(root, "evolution.json", expected_list="changes")
    tasks_state = _load_json_state(root, "tasks.json", expected_list="tasks")
    change = _find_change(evolution.get("changes", []), change_ref)
    tasks = [
        dict(task)
        for task in tasks_state.get("tasks", [])
        if isinstance(task, dict)
    ]
    return change, tasks


def _load_change_context(
    root: Path,
    change_ref: str,
) -> dict[str, Any]:
    evolution = _load_json_state(root, "evolution.json", expected_list="changes")
    return _find_change(evolution.get("changes", []), change_ref)


def _load_epic_close_context(
    root: Path,
    epic_ref: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    plan = _load_json_state(root, "plan.json", expected_list="epics")
    tasks_state = _load_json_state(root, "tasks.json", expected_list="tasks")
    epic = _find_epic(plan.get("epics", []), epic_ref)
    child_tasks = [
        dict(task)
        for task in tasks_state.get("tasks", [])
        if isinstance(task, dict) and task.get("epic_id") == epic.get("id")
    ]
    return epic, child_tasks


def _find_change(changes: Sequence[Any], change_ref: str) -> dict[str, Any]:
    for change in changes:
        if isinstance(change, dict) and str(change.get("id") or "") == change_ref:
            return dict(change)
    raise WorkflowError(
        "WORKFLOW_CHANGE_NOT_FOUND",
        "Evolution Change was not found: {}".format(change_ref),
        details={"change": change_ref},
    )


def _find_epic(epics: Sequence[Any], epic_ref: str) -> dict[str, Any]:
    for epic in epics:
        if not isinstance(epic, dict):
            continue
        if str(epic.get("id") or "") == epic_ref or str(epic.get("key") or "") == epic_ref:
            return dict(epic)
    raise WorkflowError(
        "WORKFLOW_EPIC_NOT_FOUND",
        "Epic was not found: {}".format(epic_ref),
        details={"epic": epic_ref},
    )


def _find_task(tasks: Sequence[Mapping[str, Any]], task_ref: str) -> dict[str, Any] | None:
    for task in tasks:
        if _task_matches_ref(task, task_ref):
            return dict(task)
    return None


def _add_task_close_next_actions(
    result: CommandResult,
    root: Path,
    task: Mapping[str, Any],
) -> None:
    task_label = _task_label(task)
    linked_changes = _linked_change_ids_for_task(root, task)
    if linked_changes:
        for change_id in linked_changes:
            result.next_actions.append(
                'python scripts/aictl.py workflow run evolution.accept_change --change {} --notes "Accepted after task {} review" --confirm'.format(
                    change_id,
                    task_label,
                )
            )
        result.owner_action_required = (
            "Task is done. Accept linked Evolution Changes separately only if the Human Owner agrees."
        )
    else:
        result.owner_action_required = (
            "Task is done. Review the queue and explicitly select the next task when ready."
        )
    result.next_actions.append("python scripts/aictl.py task list --status ready")


def _add_task_request_changes_next_actions(
    result: CommandResult,
    task: Mapping[str, Any],
) -> None:
    task_label = _task_label(task)
    result.owner_action_required = (
        "Changes were requested. Rework must be explicitly prepared before another execution attempt."
    )
    result.next_actions.append(
        "python scripts/aictl.py workflow run task.prepare_for_codex --task {} --confirm".format(
            task_label,
        )
    )


def _linked_change_ids_for_task(root: Path, task: Mapping[str, Any]) -> list[str]:
    try:
        evolution = _load_json_state(root, "evolution.json", expected_list="changes")
    except WorkflowError:
        return []
    task_refs = {str(value) for value in (_task_label(task), _legacy_task_id(task), task.get("id")) if value}
    linked: list[str] = []
    for change in evolution.get("changes", []):
        if not isinstance(change, Mapping):
            continue
        linked_tasks = set(_string_list(change.get("linked_tasks")))
        if task_refs.intersection(linked_tasks):
            change_id = str(change.get("id") or "")
            if change_id:
                linked.append(change_id)
    return linked


def _task_matches_ref(task: Mapping[str, Any], task_ref: str) -> bool:
    for field in ("id", "uid", "ref", "legacy_id"):
        if str(task.get(field) or "") == task_ref:
            return True
    aliases = task.get("aliases") or []
    return isinstance(aliases, list) and task_ref in [str(alias) for alias in aliases]


def _current_execution_targets_task(root: Path, task: Mapping[str, Any]) -> bool:
    path = root / "AI_PROJECT" / "state" / "current_execution.json"
    if not path.exists():
        return False
    try:
        execution = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(execution, Mapping):
        return False
    source_type = str(execution.get("source_type") or "")
    if source_type and source_type != "task":
        return False
    return str(execution.get("source_id") or "") in _task_refs(task)


def _task_refs(task: Mapping[str, Any]) -> set[str]:
    refs = {
        str(task.get(field) or "").strip()
        for field in ("id", "uid", "ref", "legacy_id")
    }
    refs.update(_string_list(task.get("aliases")))
    refs.discard("")
    return refs


def _workflow_target_error(
    workflow_name: str,
    *,
    task_ref: str,
    change_ref: str,
    epic_ref: str,
) -> WorkflowError | None:
    if workflow_name in {
        "task.prepare_for_codex",
        "task.refresh_execution_context",
        "task.submit_for_review",
        "task.close_reviewed",
        "task.request_changes",
        "evolution.create_for_task",
    } and not task_ref:
        return WorkflowError(
            "WORKFLOW_TASK_REQUIRED",
            "Workflow requires --task.",
            details={"workflow": workflow_name},
        )
    if workflow_name in {
        "evolution.approve_change",
        "evolution.move_to_review",
        "evolution.accept_change",
    } and not change_ref:
        return WorkflowError(
            "WORKFLOW_CHANGE_REQUIRED",
            "Workflow requires --change.",
            details={"workflow": workflow_name},
        )
    if workflow_name == "epic.close_if_complete" and not epic_ref:
        return WorkflowError(
            "WORKFLOW_EPIC_REQUIRED",
            "Workflow requires --epic.",
            details={"workflow": workflow_name},
        )
    return None


def _task_close_preflight_error(
    task: Mapping[str, Any],
    notes: str,
) -> WorkflowError | None:
    if not notes.strip():
        return WorkflowError(
            "WORKFLOW_APPROVAL_NOTES_REQUIRED",
            "Closing a reviewed Task requires non-empty approval notes.",
            details={"task": _task_label(task)},
        )
    if task.get("status") != TASK_CLOSE_REQUIRED_STATUS:
        return WorkflowError(
            "WORKFLOW_TASK_NOT_IN_REVIEW",
            "Task must be in_review before it can be closed.",
            details={
                "task": _task_label(task),
                "status": str(task.get("status") or ""),
                "required_status": TASK_CLOSE_REQUIRED_STATUS,
            },
        )
    return None


def _task_close_preflight_step_result(
    task: Mapping[str, Any],
    notes: str,
) -> WorkflowStepResult:
    return _local_check_step_result(
        "task_close_preflight",
        "Check task close gates",
        "task.close_reviewed.preflight",
        error=_task_close_preflight_error(task, notes),
    )


def _task_request_changes_preflight_error(
    task: Mapping[str, Any],
    notes: str,
) -> WorkflowError | None:
    if not notes.strip():
        return WorkflowError(
            "WORKFLOW_REQUEST_CHANGES_NOTES_REQUIRED",
            "Requesting changes for a reviewed Task requires non-empty owner notes.",
            details={"task": _task_label(task)},
        )
    if task.get("status") != TASK_REVIEW_DECISION_REQUIRED_STATUS:
        return WorkflowError(
            "WORKFLOW_TASK_NOT_IN_REVIEW",
            "Task must be in_review before changes can be requested.",
            details={
                "task": _task_label(task),
                "status": str(task.get("status") or ""),
                "required_status": TASK_REVIEW_DECISION_REQUIRED_STATUS,
            },
        )
    return None


def _task_request_changes_preflight_step_result(
    task: Mapping[str, Any],
    notes: str,
) -> WorkflowStepResult:
    return _local_check_step_result(
        "task_request_changes_preflight",
        "Check request-changes gates",
        "task.request_changes.preflight",
        error=_task_request_changes_preflight_error(task, notes),
    )


def _change_approve_preflight_error(
    change: Mapping[str, Any],
    notes: str,
) -> WorkflowError | None:
    if not notes.strip():
        return WorkflowError(
            "WORKFLOW_CHANGE_APPROVAL_NOTES_REQUIRED",
            "Approving an Evolution Change requires non-empty approval notes.",
            details={"change": str(change.get("id") or "")},
        )
    status = str(change.get("status") or "")
    if status != CHANGE_APPROVE_REQUIRED_STATUS:
        return WorkflowError(
            "WORKFLOW_CHANGE_NOT_READY",
            "Evolution Change must be ready before approval.",
            details={
                "change": str(change.get("id") or ""),
                "status": status,
                "required_status": CHANGE_APPROVE_REQUIRED_STATUS,
            },
        )
    return None


def _change_review_preflight_error(
    change: Mapping[str, Any],
) -> WorkflowError | None:
    status = str(change.get("status") or "")
    if status not in CHANGE_REVIEWABLE_STATUSES:
        return WorkflowError(
            "WORKFLOW_CHANGE_NOT_REVIEWABLE",
            "Evolution Change must be approved, in_progress, or in_review before moving to review.",
            details={
                "change": str(change.get("id") or ""),
                "status": status,
                "allowed_statuses": sorted(CHANGE_REVIEWABLE_STATUSES),
            },
        )
    return None


def _change_accept_preflight_error(
    change: Mapping[str, Any],
    tasks: Sequence[Mapping[str, Any]],
    notes: str,
) -> WorkflowError | None:
    if not notes.strip():
        return WorkflowError(
            "WORKFLOW_ACCEPTANCE_NOTES_REQUIRED",
            "Accepting an Evolution Change requires non-empty acceptance notes.",
            details={"change": str(change.get("id") or "")},
        )
    status = str(change.get("status") or "")
    if status not in CHANGE_ACCEPTABLE_STATUSES:
        return WorkflowError(
            "WORKFLOW_CHANGE_NOT_ACCEPTABLE",
            "Evolution Change must be approved or in_review before acceptance.",
            details={
                "change": str(change.get("id") or ""),
                "status": status,
                "allowed_statuses": sorted(CHANGE_ACCEPTABLE_STATUSES),
            },
        )
    linked_tasks = _string_list(change.get("linked_tasks"))
    if not linked_tasks:
        return WorkflowError(
            "WORKFLOW_CHANGE_HAS_NO_LINKED_TASKS",
            "Evolution Change acceptance requires linked completed Tasks.",
            details={"change": str(change.get("id") or "")},
        )
    blocking: list[str] = []
    for task_ref in linked_tasks:
        task = _find_task(tasks, task_ref)
        if task is None:
            blocking.append("{} missing".format(task_ref))
        elif str(task.get("status") or "") not in CHANGE_DONE_TASK_STATUSES:
            blocking.append("{} status is {}".format(task_ref, task.get("status")))
    if blocking:
        return WorkflowError(
            "WORKFLOW_LINKED_TASKS_NOT_COMPLETE",
            "Evolution Change linked Tasks must be complete before acceptance.",
            details={
                "change": str(change.get("id") or ""),
                "blocking": blocking,
                "done_statuses": sorted(CHANGE_DONE_TASK_STATUSES),
            },
        )
    return None


def _epic_close_preflight_error(
    epic: Mapping[str, Any],
    child_tasks: Sequence[Mapping[str, Any]],
) -> WorkflowError | None:
    status = str(epic.get("status") or "")
    if status not in EPIC_CLOSABLE_STATUSES:
        return WorkflowError(
            "WORKFLOW_EPIC_NOT_CLOSABLE",
            "Epic must be active or already done before the close helper can run.",
            details={
                "epic": str(epic.get("id") or ""),
                "status": status,
                "allowed_statuses": sorted(EPIC_CLOSABLE_STATUSES),
            },
        )
    active_children = [
        "{} status is {}".format(
            task.get("ref") or task.get("legacy_id") or task.get("id"),
            task.get("status"),
        )
        for task in child_tasks
        if str(task.get("status") or "") not in EPIC_CLOSED_TASK_STATUSES
    ]
    if active_children:
        return WorkflowError(
            "WORKFLOW_EPIC_HAS_ACTIVE_TASKS",
            "Epic can close only when all child Tasks are done, deferred, or archived.",
            details={
                "epic": str(epic.get("id") or ""),
                "blocking": active_children,
                "closed_statuses": sorted(EPIC_CLOSED_TASK_STATUSES),
            },
        )
    return None


def _local_check_step_result(
    step_id: str,
    title: str,
    command_name: str,
    *,
    error: WorkflowError | None,
) -> WorkflowStepResult:
    step = WorkflowStep(
        step_id=step_id,
        title=title,
        command_name=command_name,
        route=READ_ONLY_CTL,
        argv=("read", "project-control state"),
    )
    if error is None:
        return WorkflowStepResult(
            step=step,
            status="ok",
            returncode=0,
            stdout="OK\n",
        )
    return WorkflowStepResult(
        step=step,
        status="failed",
        returncode=1,
        stderr="{}: {}\n".format(error.code, error.message),
    )


def _derive_evolution_change(task: Mapping[str, Any]) -> dict[str, Any]:
    title = str(task.get("title") or "Evolution Change for {}".format(_task_label(task)))
    summary = str(task.get("summary") or "").strip()
    description = str(task.get("description") or "").strip()
    expected = str(task.get("expected_result") or "").strip()
    scope = _string_list(task.get("scope"))
    out_of_scope = _string_list(task.get("out_of_scope"))
    allowed_files = _string_list(task.get("allowed_files"))
    acceptance = _string_list(task.get("acceptance_criteria"))
    review = _string_list(task.get("review_instructions"))

    problem_source = summary or description or expected or "Task requires controlled system evolution."
    problem = (
        "Task {task} requires an explicit Evolution Change Proposal before "
        "implementation: {text}"
    ).format(task=_task_label(task), text=problem_source)

    proposal_items = scope or [description or summary or "Implement the bounded task scope."]
    proposal = "Implement the bounded task scope: {}".format("; ".join(proposal_items))

    rationale = description or expected or summary or (
        "A ready Change Proposal keeps system evolution auditable and separate "
        "from Human Owner approval."
    )

    risks = _unique_text_items(
        [_risk_from_boundary(item) for item in out_of_scope]
        + review
        + [
            "Generated Change Proposal fields may need Human Owner review before approval.",
            "Workflow must delegate all protected project-control mutations to evolutionctl.py.",
        ]
    )

    impact = _unique_text_items(
        [
            "Creates an Evolution Change Proposal linked to task {}.".format(
                _legacy_task_id(task)
            ),
            "Keeps Change approval as a separate explicit Human Owner action.",
        ]
        + scope[:5]
        + acceptance[:3]
    )

    return {
        "title": title,
        "change_type": _infer_change_type(allowed_files),
        "problem": problem,
        "proposal": proposal,
        "rationale": rationale,
        "affected_files": _unique_text_items(allowed_files),
        "risks": risks,
        "impact": impact,
        "linked_task": _legacy_task_id(task),
    }


def _task_label(task: Mapping[str, Any]) -> str:
    return str(task.get("ref") or task.get("legacy_id") or task.get("id") or "<task>")


def _legacy_task_id(task: Mapping[str, Any]) -> str:
    return str(task.get("legacy_id") or task.get("id") or _task_label(task))


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _unique_text_items(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    unique = []
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        unique.append(text)
    return unique


def _risk_from_boundary(text: str) -> str:
    stripped = text.strip()
    if stripped.lower().startswith("do not "):
        return "Boundary risk: {}".format(stripped)
    return stripped


def _infer_change_type(allowed_files: Sequence[str]) -> str:
    paths = [path.lower() for path in allowed_files]
    if any(path.startswith("ai-system/") or path.startswith("docs/") for path in paths):
        return "docs"
    if any("skill" in path for path in paths):
        return "plugin"
    if any("template" in path for path in paths):
        return "template"
    if any("security" in path or "privacy" in path for path in paths):
        return "security"
    if any(path.startswith("spec/") or path.endswith(".schema.json") for path in paths):
        return "schema"
    if any(path.startswith("scripts/") or path.startswith("ai_project_ctl/") for path in paths):
        return "tooling"
    return "process"


def _evolution_change_create_step(
    task: Mapping[str, Any],
    change_preview: Mapping[str, Any],
    root: Path,
    actor: str,
    python_executable: str,
) -> WorkflowStep:
    return _ctl_step(
        "change_create",
        "Create draft Change Proposal",
        "evolutionctl.change.create",
        "evolutionctl.py",
        root,
        actor,
        python_executable,
        "change",
        "create",
        "--title",
        str(change_preview.get("title") or "Evolution Change for {}".format(_task_label(task))),
        "--type",
        str(change_preview.get("change_type") or "process"),
        "--status",
        "draft",
        "--problem",
        str(change_preview.get("problem") or ""),
        "--proposal",
        str(change_preview.get("proposal") or ""),
        "--rationale",
        str(change_preview.get("rationale") or ""),
    )


def _evolution_change_followup_steps(
    task: Mapping[str, Any],
    change_preview: Mapping[str, Any],
    change_id: str,
    root: Path,
    actor: str,
    python_executable: str,
) -> list[WorkflowStep]:
    steps: list[WorkflowStep] = []
    for index, text in enumerate(_string_list(change_preview.get("affected_files")), start=1):
        steps.append(
            _evolution_list_step(
                "add_affected_file_{}".format(index),
                "Add affected file",
                "evolutionctl.change.add_affected_file",
                root,
                actor,
                python_executable,
                "add-affected-file",
                change_id,
                text,
            )
        )
    for index, text in enumerate(_string_list(change_preview.get("risks")), start=1):
        steps.append(
            _evolution_list_step(
                "add_risk_{}".format(index),
                "Add risk",
                "evolutionctl.change.add_risk",
                root,
                actor,
                python_executable,
                "add-risk",
                change_id,
                text,
            )
        )
    for index, text in enumerate(_string_list(change_preview.get("impact")), start=1):
        steps.append(
            _evolution_list_step(
                "add_impact_{}".format(index),
                "Add impact",
                "evolutionctl.change.add_impact",
                root,
                actor,
                python_executable,
                "add-impact",
                change_id,
                text,
            )
        )

    steps.append(
        _ctl_step(
            "link_task",
            "Link legacy task ID",
            "evolutionctl.change.link_task",
            "evolutionctl.py",
            root,
            actor,
            python_executable,
            "change",
            "link-task",
            change_id,
            "--task",
            str(change_preview.get("linked_task") or _legacy_task_id(task)),
        )
    )
    steps.extend(
        [
            _ctl_step(
                "validate_before_ready",
                "Validate evolution state before ready",
                "evolutionctl.validate",
                "evolutionctl.py",
                root,
                actor,
                python_executable,
                "validate",
            ),
            _ctl_step(
                "ready",
                "Move Change Proposal to ready",
                "evolutionctl.change.transition",
                "evolutionctl.py",
                root,
                actor,
                python_executable,
                "change",
                "transition",
                change_id,
                "--to",
                "ready",
            ),
            _ctl_step(
                "validate",
                "Validate evolution state",
                "evolutionctl.validate",
                "evolutionctl.py",
                root,
                actor,
                python_executable,
                "validate",
            ),
            _ctl_step(
                "check_generated",
                "Check generated evolution output",
                "evolutionctl.check-generated",
                "evolutionctl.py",
                root,
                actor,
                python_executable,
                "check-generated",
            ),
        ]
    )
    return steps


def _evolution_list_step(
    step_id: str,
    title: str,
    command_name: str,
    root: Path,
    actor: str,
    python_executable: str,
    command: str,
    change_id: str,
    text: str,
) -> WorkflowStep:
    return _ctl_step(
        step_id,
        title,
        command_name,
        "evolutionctl.py",
        root,
        actor,
        python_executable,
        "change",
        command,
        change_id,
        "--text",
        text,
    )


def _parse_created_change_id(stdout: str) -> str:
    for line in stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("Created:"):
            candidate = stripped.split(":", 1)[1].strip()
            if candidate.startswith("CHG-"):
                return candidate
    for token in stdout.replace("\n", " ").split():
        candidate = token.strip(".,;")
        if candidate.startswith("CHG-"):
            return candidate
    raise WorkflowError(
        "WORKFLOW_CHANGE_ID_NOT_FOUND",
        "Could not find created Change ID in evolutionctl output.",
        details={"stdout": stdout},
    )


def _parse_created_task_id(stdout: str) -> str:
    match = re.search(r"\((TASK-\d+)\)", stdout)
    if match:
        return match.group(1)
    match = re.search(r"\bTASK-\d+\b", stdout)
    if match:
        return match.group(0)
    raise WorkflowError(
        "WORKFLOW_TASK_ID_NOT_FOUND",
        "Could not find created Task ID in taskctl output.",
        details={"stdout": stdout},
    )


def _resolve_step(
    task_ref: str,
    *,
    root: Path,
    actor: str,
    python_executable: str,
) -> WorkflowStep:
    return WorkflowStep(
        step_id="resolve",
        title="Resolve task reference",
        command_name="taskctl.task.resolve",
        route=READ_ONLY_CTL,
        argv=(
            python_executable,
            str(SCRIPTS_DIR / "taskctl.py"),
            "--root",
            str(root),
            "--actor",
            actor,
            "task",
            "resolve",
            task_ref,
            "--json",
        ),
    )


def _aictl_step(
    step_id: str,
    title: str,
    command_name: str,
    root: Path,
    actor: str,
    python_executable: str,
    *args: str,
    skip_reason: str = "",
    blocking: bool = True,
) -> WorkflowStep:
    return WorkflowStep(
        step_id=step_id,
        title=title,
        command_name=command_name,
        route=REGISTERED,
        argv=(
            python_executable,
            str(SCRIPTS_DIR / "aictl.py"),
            "--root",
            str(root),
            "--actor",
            actor,
            "--json",
            *args,
        ),
        skip_reason=skip_reason,
        blocking=blocking,
    )


def _ctl_step(
    step_id: str,
    title: str,
    command_name: str,
    script_name: str,
    root: Path,
    actor: str,
    python_executable: str,
    *args: str,
    skip_reason: str = "",
    blocking: bool = True,
) -> WorkflowStep:
    return WorkflowStep(
        step_id=step_id,
        title=title,
        command_name=command_name,
        route=VALIDATED_CTL,
        argv=(
            python_executable,
            str(SCRIPTS_DIR / script_name),
            "--root",
            str(root),
            "--actor",
            actor,
            *args,
        ),
        skip_reason=skip_reason,
        blocking=blocking,
    )


def _protected_step(
    root: Path,
    python_executable: str,
    *,
    prompt_context_errors_are_warnings: bool = False,
) -> WorkflowStep:
    return WorkflowStep(
        step_id="protected",
        title="Check protected project files",
        command_name="protected.check",
        route=VALIDATED_CTL,
        argv=(
            python_executable,
            str(SCRIPTS_DIR / "check-protected-project-files.py"),
            "--root",
            str(root),
            "--json",
        ),
        prompt_context_errors_are_warnings=prompt_context_errors_are_warnings,
    )


def _protected_prompt_context_warning_result(
    step: WorkflowStep,
    completed: subprocess.CompletedProcess[str],
) -> WorkflowStepResult | None:
    if completed.returncode == 0:
        return None
    try:
        parsed = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, Mapping):
        return None
    errors = [str(error) for error in parsed.get("errors") or []]
    prompt_context_warnings = [
        error for error in errors if _protected_error_is_prompt_context_warning(error)
    ]
    blocking_errors = [
        error for error in errors if error not in prompt_context_warnings
    ]
    if not prompt_context_warnings or blocking_errors:
        return None
    warning_step = replace(step, blocking=False)
    stderr = completed.stderr or (
        "Protected-file check reported only stale prompt/context warnings."
    )
    return WorkflowStepResult(
        step=warning_step,
        status="failed",
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=stderr,
    )


def _protected_error_is_prompt_context_warning(error: str) -> bool:
    warning_fragments = (
        "MISSING_GENERATED_PROMPT:",
        "ORPHAN_GENERATED_PROMPT:",
        "OUTDATED_GENERATED_FILE: AI_PROJECT/generated/CODEX_PROMPT.md",
        "CODEX_PROMPT_RENDER_FAILED: STALE_CONTEXT_PACK:",
        "CODEX_EXECUTION_CONTEXT_MISMATCH:",
    )
    return any(fragment in error for fragment in warning_fragments)


def _validate_step_route(step: WorkflowStep) -> None:
    if step.route != REGISTERED:
        return
    descriptor = command_describe(step.command_name)
    if descriptor.get("availability") != "implemented":
        raise WorkflowError(
            "WORKFLOW_STEP_NOT_IMPLEMENTED",
            "Workflow step command is not implemented: {}".format(step.command_name),
            details={"step": step.step_id, "command": step.command_name},
        )


def _parse_resolved_task(stdout: str, *, task_ref: str) -> dict[str, Any]:
    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise WorkflowError(
            "WORKFLOW_TASK_RESOLVE_INVALID_JSON",
            "Task resolve did not return valid JSON for: {}".format(task_ref),
            details={"stdout": stdout},
        ) from exc
    if not isinstance(parsed, dict) or not parsed.get("id"):
        raise WorkflowError(
            "WORKFLOW_TASK_RESOLVE_INVALID_OUTPUT",
            "Task resolve did not return a task id for: {}".format(task_ref),
            details={"stdout": stdout},
        )
    return dict(parsed)


def _display_argv(argv: Sequence[str]) -> list[str]:
    display = []
    for index, value in enumerate(argv):
        if index == 0:
            display.append("python")
            continue
        try:
            path = Path(value)
            if path.is_absolute():
                display.append(str(path.relative_to(PACKAGE_ROOT)))
                continue
        except ValueError:
            pass
        display.append(value)
    return display

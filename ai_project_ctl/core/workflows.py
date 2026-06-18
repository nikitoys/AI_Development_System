"""Safe workflow orchestration over existing project-control commands."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
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
class WorkflowStep:
    """Concrete executable workflow step."""

    step_id: str
    title: str
    command_name: str
    route: str
    argv: tuple[str, ...]
    blocking: bool = True
    skip_reason: str = ""

    def preview_dict(self) -> dict[str, Any]:
        return {
            "id": self.step_id,
            "title": self.title,
            "command_name": self.command_name,
            "route": self.route,
            "command": _display_argv(self.argv),
            "blocking": self.blocking,
            "skip_reason": self.skip_reason,
        }


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
    steps = _build_steps(
        descriptor.name,
        task=task,
        root=Path(root).resolve(),
        actor=actor,
        python_executable=python_executable or sys.executable,
        include_resolve=True,
    )
    return {
        "workflow": descriptor.to_dict(),
        "task_ref": task_ref or "",
        "steps": [step.preview_dict() for step in steps],
    }


def run_workflow(
    name: str,
    *,
    task_ref: str,
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
        task_ref=task_ref,
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
    return executor.run(descriptor, task_ref=task_ref)


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

    def run(self, descriptor: WorkflowDescriptor, *, task_ref: str) -> CommandResult:
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
        steps = _build_steps(
            descriptor.name,
            task=task,
            root=self.root,
            actor=self.actor,
            python_executable=self.python_executable,
            include_resolve=False,
        )
        for step in steps:
            step_result = self._execute_step(step)
            step_results.append(step_result)
            if not step_result.ok and step.blocking:
                return self._result(
                    descriptor,
                    task_ref=task_ref,
                    task=task,
                    step_results=step_results,
                    message="Workflow stopped on blocking step: {}".format(step.title),
                )

        return self._result(
            descriptor,
            task_ref=task_ref,
            task=task,
            step_results=step_results,
            message="Workflow completed.",
        )

    def _execute_step(self, step: WorkflowStep) -> WorkflowStepResult:
        if step.skip_reason:
            return WorkflowStepResult(step=step, status="skipped")
        _validate_step_route(step)
        completed = self.runner(step.argv)
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
    ) -> CommandResult:
        failed = next((item for item in step_results if not item.ok), None)
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
    )


def _template(
    step_id: str,
    title: str,
    command_name: str,
    route: str,
    command_template: str,
) -> WorkflowStepTemplate:
    return WorkflowStepTemplate(
        step_id=step_id,
        title=title,
        command_name=command_name,
        route=route,
        command_template=tuple(command_template.split()),
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

    raise WorkflowError("WORKFLOW_NOT_FOUND", "Unknown workflow: {}".format(workflow_name))


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
    )


def _protected_step(root: Path, python_executable: str) -> WorkflowStep:
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
    )


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

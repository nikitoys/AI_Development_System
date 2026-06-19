"""Command registry metadata for the future unified control plane."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping

from .result import CommandError


class RegistryError(CommandError):
    """Registry lookup or descriptor validation error."""


class CommandKind(str, Enum):
    READ = "read"
    WRITE = "write"
    RENDER = "render"
    VALIDATION = "validation"
    AUDIT = "audit"
    UTILITY = "utility"


class CommandAvailability(str, Enum):
    IMPLEMENTED = "implemented"
    PLANNED = "planned"


@dataclass(frozen=True)
class ArgumentSpec:
    """Small JSON-schema-like command argument descriptor."""

    name: str
    description: str
    value_type: str = "string"
    required: bool = False
    default: Any = None
    choices: tuple[str, ...] = ()
    repeatable: bool = False

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "type": self.value_type,
            "required": self.required,
            "repeatable": self.repeatable,
        }
        if self.default is not None:
            data["default"] = self.default
        if self.choices:
            data["choices"] = list(self.choices)
        return data


@dataclass(frozen=True)
class OutputSpec:
    """Describes supported output formats and result shape."""

    description: str
    formats: tuple[str, ...] = ("human", "json")
    schema: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "description": self.description,
            "formats": list(self.formats),
        }
        if self.schema:
            data["schema"] = dict(self.schema)
        return data


@dataclass(frozen=True)
class CommandDescriptor:
    """Metadata for one allowed or planned project-control command."""

    name: str
    domain: str
    description: str
    kind: CommandKind
    arguments: tuple[ArgumentSpec, ...] = ()
    reads_state: tuple[str, ...] = ()
    writes_state: tuple[str, ...] = ()
    event_logs: tuple[str, ...] = ()
    generated_files: tuple[str, ...] = ()
    output: OutputSpec = field(
        default_factory=lambda: OutputSpec("Human-readable command result.")
    )
    validators: tuple[str, ...] = ()
    lock_scope: str = ""
    owner_approval: str = ""
    dry_run: bool = False
    json_output: bool = True
    availability: CommandAvailability = CommandAvailability.IMPLEMENTED
    legacy_command: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    @property
    def mutates_state(self) -> bool:
        return bool(self.writes_state)

    @property
    def writes_events(self) -> bool:
        return bool(self.event_logs)

    @property
    def renders_generated(self) -> bool:
        return bool(self.generated_files)

    @property
    def validates(self) -> bool:
        return self.kind == CommandKind.VALIDATION or bool(self.validators)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "domain": self.domain,
            "description": self.description,
            "kind": self.kind.value,
            "arguments": [argument.to_dict() for argument in self.arguments],
            "reads_state": list(self.reads_state),
            "writes_state": list(self.writes_state),
            "read_write": {
                "mutates_state": self.mutates_state,
                "writes_events": self.writes_events,
                "renders_generated": self.renders_generated,
                "validates": self.validates,
            },
            "event_logs": list(self.event_logs),
            "generated_files": list(self.generated_files),
            "output": self.output.to_dict(),
            "validators": list(self.validators),
            "lock_scope": self.lock_scope,
            "owner_approval": self.owner_approval,
            "dry_run": self.dry_run,
            "json_output": self.json_output,
            "availability": self.availability.value,
            "legacy_command": list(self.legacy_command),
            "notes": list(self.notes),
        }


class CommandRegistry:
    """In-memory catalog for command discovery and description."""

    def __init__(self, descriptors: Iterable[CommandDescriptor] = ()) -> None:
        self._commands: dict[str, CommandDescriptor] = {}
        for descriptor in descriptors:
            self.register(descriptor)

    def register(self, descriptor: CommandDescriptor) -> None:
        _validate_descriptor(descriptor)
        if descriptor.name in self._commands:
            raise RegistryError(
                "DUPLICATE_COMMAND",
                f"Command is already registered: {descriptor.name}",
            )
        self._commands[descriptor.name] = descriptor

    def get(self, name: str) -> CommandDescriptor:
        try:
            return self._commands[name]
        except KeyError as exc:
            raise RegistryError("COMMAND_NOT_FOUND", f"Unknown command: {name}") from exc

    def describe(self, name: str) -> dict[str, Any]:
        return self.get(name).to_dict()

    def list_commands(
        self,
        *,
        domain: str | None = None,
        include_planned: bool = True,
    ) -> list[CommandDescriptor]:
        commands = self._commands.values()
        if domain is not None:
            commands = [command for command in commands if command.domain == domain]
        if not include_planned:
            commands = [
                command
                for command in commands
                if command.availability == CommandAvailability.IMPLEMENTED
            ]
        return sorted(commands, key=lambda command: command.name)

    def list_command_names(
        self,
        *,
        domain: str | None = None,
        include_planned: bool = True,
    ) -> list[str]:
        return [
            command.name
            for command in self.list_commands(
                domain=domain,
                include_planned=include_planned,
            )
        ]

    def domains(self, *, include_planned: bool = True) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    command.domain
                    for command in self.list_commands(include_planned=include_planned)
                }
            )
        )

    def to_list(
        self,
        *,
        domain: str | None = None,
        include_planned: bool = True,
    ) -> list[dict[str, Any]]:
        return [
            command.to_dict()
            for command in self.list_commands(
                domain=domain,
                include_planned=include_planned,
            )
        ]


def default_command_registry() -> CommandRegistry:
    """Return the foundation registry without mutating project-control state."""

    return CommandRegistry(_default_descriptors())


def command_list(
    registry: CommandRegistry | None = None,
    *,
    domain: str | None = None,
    include_planned: bool = True,
) -> list[dict[str, Any]]:
    """List registered command metadata for future CLI/API surfaces."""

    selected = registry or default_command_registry()
    return selected.to_list(domain=domain, include_planned=include_planned)


def command_describe(
    name: str,
    registry: CommandRegistry | None = None,
) -> dict[str, Any]:
    """Describe one registered command for future CLI/API surfaces."""

    selected = registry or default_command_registry()
    return selected.describe(name)


def _validate_descriptor(descriptor: CommandDescriptor) -> None:
    if not descriptor.name or "." not in descriptor.name:
        raise RegistryError(
            "INVALID_COMMAND_NAME",
            "Command name must be dotted, such as task.show",
        )
    if not descriptor.domain:
        raise RegistryError("INVALID_COMMAND_DOMAIN", "Command domain is required")
    if not descriptor.name.startswith(f"{descriptor.domain}."):
        raise RegistryError(
            "COMMAND_DOMAIN_MISMATCH",
            f"{descriptor.name} does not belong to domain {descriptor.domain}",
        )
    argument_names = [argument.name for argument in descriptor.arguments]
    if len(argument_names) != len(set(argument_names)):
        raise RegistryError(
            "DUPLICATE_COMMAND_ARGUMENT",
            f"Command has duplicate argument names: {descriptor.name}",
        )


def _arg(
    name: str,
    description: str,
    *,
    value_type: str = "string",
    required: bool = False,
    default: Any = None,
    repeatable: bool = False,
    choices: tuple[str, ...] = (),
) -> ArgumentSpec:
    return ArgumentSpec(
        name=name,
        description=description,
        value_type=value_type,
        required=required,
        default=default,
        repeatable=repeatable,
        choices=choices,
    )


def _output(description: str, *, fields: tuple[str, ...] = ()) -> OutputSpec:
    schema: dict[str, Any] = {}
    if fields:
        schema["fields"] = list(fields)
    return OutputSpec(description, schema=schema)


def _default_descriptors() -> tuple[CommandDescriptor, ...]:
    state_tasks = "AI_PROJECT/state/tasks.json"
    state_task_reports = "AI_PROJECT/state/task_reports.json"
    state_plan = "AI_PROJECT/state/plan.json"
    state_evolution = "AI_PROJECT/state/evolution.json"
    state_docs = "AI_PROJECT/state/docs.json"
    state_execution = "AI_PROJECT/state/current_execution.json"

    return (
        CommandDescriptor(
            name="command.list",
            domain="command",
            description="List registered project-control command metadata.",
            kind=CommandKind.READ,
            arguments=(
                _arg("domain", "Optional command domain filter."),
                _arg("include_planned", "Include planned, non-executable commands.", value_type="boolean"),
            ),
            output=_output("Registered command descriptors.", fields=("commands",)),
            notes=("Metadata-only registry operation; does not mutate state.",),
        ),
        CommandDescriptor(
            name="command.describe",
            domain="command",
            description="Describe one registered project-control command.",
            kind=CommandKind.READ,
            arguments=(_arg("name", "Dotted command name to describe.", required=True),),
            output=_output("Single command descriptor.", fields=("command",)),
            notes=("Metadata-only registry operation; does not mutate state.",),
        ),
        CommandDescriptor(
            name="workflow.list",
            domain="workflow",
            description="List high-level workflow automation metadata.",
            kind=CommandKind.READ,
            output=_output("Workflow descriptors.", fields=("workflows",)),
            notes=("Metadata-only workflow discovery; does not mutate state.",),
        ),
        CommandDescriptor(
            name="workflow.describe",
            domain="workflow",
            description="Describe one high-level workflow automation command.",
            kind=CommandKind.READ,
            arguments=(_arg("name", "Workflow command name.", required=True),),
            output=_output("Workflow descriptor.", fields=("workflow",)),
            notes=("Metadata-only workflow description; does not mutate state.",),
        ),
        CommandDescriptor(
            name="task.list",
            domain="task",
            description="List executable Tasks managed by taskctl.py.",
            kind=CommandKind.READ,
            arguments=(
                _arg("status", "Optional task status filter."),
                _arg("epic", "Optional parent Epic ID or key filter."),
            ),
            reads_state=(state_tasks, state_plan),
            output=_output("Task list.", fields=("tasks",)),
            validators=("task_state", "plan_references"),
            legacy_command=("python scripts/taskctl.py task list",),
        ),
        CommandDescriptor(
            name="task.show",
            domain="task",
            description="Show one Task by ID, ref, UID, legacy ID, or alias.",
            kind=CommandKind.READ,
            arguments=(_arg("task_id", "Task ID, ref, UID, legacy ID, or alias.", required=True),),
            reads_state=(state_tasks, state_plan),
            output=_output("Task detail.", fields=("task",)),
            validators=("task_state", "plan_references", "task_identity"),
            legacy_command=("python scripts/taskctl.py task show <TASK_ID>",),
        ),
        CommandDescriptor(
            name="task.create",
            domain="task",
            description="Create one bounded Task under an Epic through the create-only task workflow.",
            kind=CommandKind.WRITE,
            arguments=(
                _arg("epic", "Parent Epic ID.", required=True),
                _arg("title", "Task title.", required=True),
                _arg("summary", "Task summary."),
                _arg("description", "Task description."),
                _arg("scope", "Scope item.", repeatable=True),
                _arg("out_of_scope", "Out-of-scope item.", repeatable=True),
                _arg("allowed_file", "Allowed file path.", repeatable=True),
                _arg("acceptance", "Acceptance criterion.", repeatable=True),
                _arg("review_instruction", "Review instruction.", repeatable=True),
                _arg("note", "Task note.", repeatable=True),
                _arg("depends_on", "Dependency task ref.", repeatable=True),
                _arg("dependency_reason", "Reason applied to added dependencies."),
                _arg("verification_mode", "Verification mode."),
                _arg("status", "Initial task status."),
                _arg("confirm", "Required explicit confirmation.", value_type="boolean", required=True),
            ),
            reads_state=(state_tasks, state_plan),
            writes_state=(state_tasks,),
            event_logs=("AI_PROJECT/events/task-events.jsonl",),
            generated_files=(
                "AI_PROJECT/generated/CODEX_TASKS.md",
                "AI_PROJECT/generated/CODEX_CURRENT.md",
                "AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md",
            ),
            output=_output("Created task result.", fields=("task_id", "ref", "uid")),
            validators=("task_state", "plan_references", "task_required_fields"),
            lock_scope="workflow",
            owner_approval="Explicit confirmation is required; created tasks are not auto-started.",
            dry_run=True,
            legacy_command=("python scripts/aictl.py task create --confirm",),
            notes=(
                "Create-only route: does not set current task and does not transition task status after creation.",
                "Delegates creation to taskctl.py task create and dependency additions to taskctl.py task deps add.",
                "Runs task validation, dependency graph validation, and generated task output checks after creation.",
            ),
        ),
        CommandDescriptor(
            name="task.import",
            domain="task",
            description="Preview or create multiple bounded Tasks from a JSON import payload.",
            kind=CommandKind.WRITE,
            arguments=(
                _arg("text", "JSON import payload."),
                _arg("file", "UTF-8 JSON import payload file."),
                _arg("preview", "Validate and show the command plan without creating tasks.", value_type="boolean"),
                _arg("confirm", "Required explicit confirmation before creating tasks.", value_type="boolean"),
            ),
            reads_state=(state_tasks, state_plan),
            writes_state=(state_tasks,),
            event_logs=("AI_PROJECT/events/task-events.jsonl",),
            generated_files=(
                "AI_PROJECT/generated/CODEX_TASKS.md",
                "AI_PROJECT/generated/CODEX_CURRENT.md",
                "AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md",
            ),
            output=_output("Bulk task import preview or creation result.", fields=("tasks", "steps", "created_task_ids")),
            validators=("task_state", "plan_references", "task_dependencies", "generated_output"),
            lock_scope="workflow",
            owner_approval=(
                "Preview is allowed without confirmation; explicit confirmation is required before any task is created."
            ),
            dry_run=True,
            legacy_command=("python scripts/aictl.py task import --text <JSON> --confirm",),
            notes=(
                "Accepts JSON only and rejects unknown task fields.",
                "Validates all Epic and dependency references before creating any task.",
                "Delegates every created task to the existing create-only task workflow.",
                "Does not set current task, start tasks, approve tasks, or execute imported content.",
            ),
        ),
        CommandDescriptor(
            name="task.transition",
            domain="task",
            description="Transition a Task through the validated task lifecycle.",
            kind=CommandKind.WRITE,
            arguments=(
                _arg("task_id", "Task ID, ref, UID, legacy ID, or alias.", required=True),
                _arg("to", "Target task status.", required=True),
            ),
            reads_state=(state_tasks, state_plan),
            writes_state=(state_tasks,),
            event_logs=("AI_PROJECT/events/task-events.jsonl",),
            generated_files=(
                "AI_PROJECT/generated/CODEX_TASKS.md",
                "AI_PROJECT/generated/CODEX_CURRENT.md",
                "AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md",
            ),
            output=_output("Task lifecycle transition result.", fields=("task_id", "from", "to")),
            validators=("task_state", "plan_references", "task_lifecycle"),
            lock_scope="task",
            owner_approval="Approval and done states remain Human Owner/review gates.",
            dry_run=True,
            legacy_command=("python scripts/taskctl.py task transition <TASK_ID> --to <STATUS>",),
        ),
        CommandDescriptor(
            name="task.report.submit",
            domain="task",
            description="Submit a structured Codex execution report for one Task.",
            kind=CommandKind.WRITE,
            arguments=(
                _arg("task", "Task ID, ref, UID, legacy ID, or alias.", required=True),
                _arg("file", "UTF-8 JSON execution report file.", required=True),
                _arg("confirm", "Required explicit confirmation.", value_type="boolean", required=True),
            ),
            reads_state=(state_tasks, state_plan, state_task_reports),
            writes_state=(state_task_reports,),
            event_logs=("AI_PROJECT/events/task-report-events.jsonl",),
            output=_output(
                "Stored execution report result.",
                fields=("report_id", "task_id", "owner_decision_required"),
            ),
            validators=("task_state", "plan_references", "execution_report_schema"),
            lock_scope="task_report",
            owner_approval=(
                "Explicit confirmation is required; submitted reports do not approve, close, or accept tasks."
            ),
            dry_run=True,
            legacy_command=(
                "python scripts/aictl.py task report submit --task <TASK_ID> --file <REPORT.json> --confirm",
            ),
            notes=(
                "Delegates storage to taskctl.py and writes task_reports.json plus task-report-events.jsonl.",
                "Validates report schema and task identity before storing anything.",
                "Does not modify tasks.json and does not change task lifecycle status.",
            ),
        ),
        CommandDescriptor(
            name="task.prepare_for_codex",
            domain="task",
            description="Run the confirmed prepare-for-Codex workflow for one Task.",
            kind=CommandKind.WRITE,
            arguments=(
                _arg("task", "Task ID, ref, UID, legacy ID, or alias.", required=True),
                _arg("confirm", "Required explicit confirmation.", value_type="boolean", required=True),
            ),
            reads_state=(state_tasks, state_plan, state_docs, state_evolution, state_execution),
            writes_state=(state_tasks, state_execution),
            event_logs=(
                "AI_PROJECT/events/task-events.jsonl",
                "AI_PROJECT/events/context-events.jsonl",
                "AI_PROJECT/events/codex-events.jsonl",
            ),
            generated_files=(
                "AI_PROJECT/generated/CODEX_TASKS.md",
                "AI_PROJECT/generated/CODEX_CURRENT.md",
                "AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md",
                "AI_PROJECT/generated/CONTEXT_PACK.md",
                "AI_PROJECT/generated/CONTEXT_STATUS.md",
                "AI_PROJECT/generated/CODEX_PROMPT.md",
                "AI_PROJECT/generated/CODEX_STATUS.md",
            ),
            output=_output("Step-by-step workflow result.", fields=("steps",)),
            validators=("task_state", "plan_references", "context_pack_freshness", "project_doctor"),
            lock_scope="workflow",
            owner_approval="Explicit confirmation is required before writes.",
            dry_run=True,
            legacy_command=("python scripts/aictl.py workflow run task.prepare_for_codex --task <TASK_ID> --confirm",),
            notes=(
                "Composes current.set, task.transition, context.build, codex.prompt.build and project.doctor.",
                "Does not directly edit protected project-control files.",
            ),
        ),
        CommandDescriptor(
            name="task.refresh_execution_context",
            domain="task",
            description="Run the confirmed execution-context refresh workflow for one Task.",
            kind=CommandKind.WRITE,
            arguments=(
                _arg("task", "Task ID, ref, UID, legacy ID, or alias.", required=True),
                _arg("confirm", "Required explicit confirmation.", value_type="boolean", required=True),
            ),
            reads_state=(state_tasks, state_plan, state_docs, state_execution),
            writes_state=(state_execution,),
            event_logs=(
                "AI_PROJECT/events/context-events.jsonl",
                "AI_PROJECT/events/codex-events.jsonl",
            ),
            generated_files=(
                "AI_PROJECT/generated/CONTEXT_PACK.md",
                "AI_PROJECT/generated/CONTEXT_STATUS.md",
                "AI_PROJECT/generated/CODEX_PROMPT.md",
                "AI_PROJECT/generated/CODEX_STATUS.md",
            ),
            output=_output("Step-by-step workflow result.", fields=("steps",)),
            validators=("task_state", "docs_state", "context_pack_freshness"),
            lock_scope="workflow",
            owner_approval="Explicit confirmation is required before writes.",
            dry_run=True,
            legacy_command=("python scripts/aictl.py workflow run task.refresh_execution_context --task <TASK_ID> --confirm",),
            notes=(
                "Composes context.build, context generated checks and codex.prompt.build.",
                "Does not directly edit protected project-control files.",
            ),
        ),
        CommandDescriptor(
            name="task.submit_for_review",
            domain="task",
            description="Run blocking validation checks and submit one Task for review.",
            kind=CommandKind.WRITE,
            arguments=(
                _arg("task", "Task ID, ref, UID, legacy ID, or alias.", required=True),
                _arg("confirm", "Required explicit confirmation.", value_type="boolean", required=True),
            ),
            reads_state=(state_tasks, state_plan, state_docs, state_evolution, state_execution),
            writes_state=(state_tasks,),
            event_logs=("AI_PROJECT/events/task-events.jsonl",),
            generated_files=(
                "AI_PROJECT/generated/CODEX_TASKS.md",
                "AI_PROJECT/generated/CODEX_CURRENT.md",
                "AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md",
            ),
            output=_output("Step-by-step workflow result.", fields=("steps",)),
            validators=(
                "task_state",
                "task_dependencies",
                "generated_output",
                "protected_files",
                "project_doctor",
            ),
            lock_scope="workflow",
            owner_approval="Explicit confirmation is required before writes.",
            dry_run=True,
            legacy_command=("python scripts/aictl.py workflow run task.submit_for_review --task <TASK_ID> --confirm",),
            notes=(
                "Moves the task to in_review only after blocking checks pass.",
                "Does not approve, close, or accept the task.",
            ),
        ),
        CommandDescriptor(
            name="task.close_reviewed",
            domain="task",
            description=(
                "Run close checks, approve an in_review Task with owner notes, "
                "and transition it to done."
            ),
            kind=CommandKind.WRITE,
            arguments=(
                _arg("task", "Task ID, ref, UID, legacy ID, or alias.", required=True),
                _arg("notes", "Required approval notes.", required=True),
                _arg("confirm", "Required explicit confirmation.", value_type="boolean", required=True),
            ),
            reads_state=(state_tasks, state_plan, state_docs, state_evolution, state_execution),
            writes_state=(state_tasks,),
            event_logs=("AI_PROJECT/events/task-events.jsonl",),
            generated_files=(
                "AI_PROJECT/generated/CODEX_TASKS.md",
                "AI_PROJECT/generated/CODEX_CURRENT.md",
                "AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md",
            ),
            output=_output("Step-by-step workflow result.", fields=("steps",)),
            validators=(
                "task_state",
                "task_lifecycle",
                "generated_output",
                "protected_files",
                "project_doctor",
            ),
            lock_scope="workflow",
            owner_approval=(
                "Explicit confirmation and non-empty approval notes are required before approval and done transition."
            ),
            dry_run=True,
            legacy_command=("python scripts/aictl.py workflow run task.close_reviewed --task <TASK_ID> --notes <NOTES> --confirm",),
            notes=(
                "Preflight rejects tasks that are not in_review.",
                "Delegates approval to taskctl.py task approve and done transition to the registered task.transition path.",
            ),
        ),
        CommandDescriptor(
            name="task.request_changes",
            domain="task",
            description=(
                "Record owner change-request notes and move an in_review Task "
                "to changes_requested through validated workflow steps."
            ),
            kind=CommandKind.WRITE,
            arguments=(
                _arg("task", "Task ID, ref, UID, legacy ID, or alias.", required=True),
                _arg("notes", "Required change-request notes.", required=True),
                _arg("confirm", "Required explicit confirmation.", value_type="boolean", required=True),
            ),
            reads_state=(state_tasks, state_plan, state_execution),
            writes_state=(state_tasks,),
            event_logs=("AI_PROJECT/events/task-events.jsonl",),
            generated_files=(
                "AI_PROJECT/generated/CODEX_TASKS.md",
                "AI_PROJECT/generated/CODEX_CURRENT.md",
                "AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md",
            ),
            output=_output("Step-by-step workflow result.", fields=("steps",)),
            validators=(
                "task_state",
                "task_lifecycle",
                "generated_output",
                "protected_files",
                "project_doctor",
            ),
            lock_scope="workflow",
            owner_approval=(
                "Explicit confirmation and non-empty owner notes are required before requesting changes."
            ),
            dry_run=True,
            legacy_command=("python scripts/aictl.py workflow run task.request_changes --task <TASK_ID> --notes <NOTES> --confirm",),
            notes=(
                "Preflight rejects tasks that are not in_review.",
                "Records owner notes through taskctl.py task add-note.",
                "Delegates the changes_requested transition to the registered task.transition path.",
            ),
        ),
        CommandDescriptor(
            name="evolution.create_for_task",
            domain="evolution",
            description=(
                "Draft and prepare an Evolution Change Proposal from one Task "
                "without approving it."
            ),
            kind=CommandKind.WRITE,
            arguments=(
                _arg("task", "Task ID, ref, UID, legacy ID, or alias.", required=True),
                _arg("confirm", "Required explicit confirmation.", value_type="boolean", required=True),
            ),
            reads_state=(state_tasks, state_evolution),
            writes_state=(state_evolution,),
            event_logs=("AI_PROJECT/events/evolution-events.jsonl",),
            generated_files=("AI_PROJECT/generated/EVOLUTION.md",),
            output=_output("Step-by-step workflow result.", fields=("steps", "change_id", "change_preview")),
            validators=("task_state", "evolution_state", "linked_task_references"),
            lock_scope="workflow",
            owner_approval=(
                "Explicit confirmation is required to create and prepare the "
                "Change; approval remains a separate Human Owner action."
            ),
            dry_run=True,
            legacy_command=("python scripts/aictl.py workflow run evolution.create_for_task --task <TASK_ID> --confirm",),
            notes=(
                "Composes evolutionctl.py change create/add/link/transition commands.",
                "Moves the Change Proposal only to ready; it does not approve, accept, or close the Change.",
            ),
        ),
        CommandDescriptor(
            name="evolution.approve_change",
            domain="evolution",
            description="Approve a ready Evolution Change with explicit owner notes.",
            kind=CommandKind.WRITE,
            arguments=(
                _arg("change", "Evolution Change ID.", required=True),
                _arg("notes", "Required approval notes.", required=True),
                _arg("confirm", "Required explicit confirmation.", value_type="boolean", required=True),
            ),
            reads_state=(state_evolution, state_tasks),
            writes_state=(state_evolution,),
            event_logs=("AI_PROJECT/events/evolution-events.jsonl",),
            generated_files=("AI_PROJECT/generated/EVOLUTION.md",),
            output=_output("Step-by-step workflow result.", fields=("steps", "change")),
            validators=("evolution_state", "linked_task_references", "evolution_lifecycle"),
            lock_scope="workflow",
            owner_approval=(
                "Explicit confirmation and non-empty approval notes are required; Change must be ready."
            ),
            dry_run=True,
            legacy_command=("python scripts/aictl.py workflow run evolution.approve_change --change <CHANGE_ID> --notes <NOTES> --confirm",),
            notes=(
                "Delegates approval to evolutionctl.py change approve.",
                "Does not start implementation or accept the Change.",
            ),
        ),
        CommandDescriptor(
            name="evolution.move_to_review",
            domain="evolution",
            description=(
                "Move an approved or in_progress Evolution Change toward in_review through validated lifecycle transitions."
            ),
            kind=CommandKind.WRITE,
            arguments=(
                _arg("change", "Evolution Change ID.", required=True),
                _arg("confirm", "Required explicit confirmation.", value_type="boolean", required=True),
            ),
            reads_state=(state_evolution,),
            writes_state=(state_evolution,),
            event_logs=("AI_PROJECT/events/evolution-events.jsonl",),
            generated_files=("AI_PROJECT/generated/EVOLUTION.md",),
            output=_output("Step-by-step workflow result.", fields=("steps", "change")),
            validators=("evolution_state", "evolution_lifecycle"),
            lock_scope="workflow",
            owner_approval=(
                "Explicit confirmation is required; only valid approved/in_progress/in_review Changes can move toward review."
            ),
            dry_run=True,
            legacy_command=("python scripts/aictl.py workflow run evolution.move_to_review --change <CHANGE_ID> --confirm",),
            notes=(
                "Approved Changes are moved to in_progress and then in_review.",
                "Does not accept the Change.",
            ),
        ),
        CommandDescriptor(
            name="evolution.accept_change",
            domain="evolution",
            description=(
                "Accept an approved or in_review Evolution Change only when linked Tasks are complete."
            ),
            kind=CommandKind.WRITE,
            arguments=(
                _arg("change", "Evolution Change ID.", required=True),
                _arg("notes", "Required acceptance notes.", required=True),
                _arg("confirm", "Required explicit confirmation.", value_type="boolean", required=True),
            ),
            reads_state=(state_evolution, state_tasks),
            writes_state=(state_evolution,),
            event_logs=("AI_PROJECT/events/evolution-events.jsonl",),
            generated_files=("AI_PROJECT/generated/EVOLUTION.md",),
            output=_output("Step-by-step workflow result.", fields=("steps", "change")),
            validators=("evolution_state", "linked_task_references", "task_completion"),
            lock_scope="workflow",
            owner_approval=(
                "Explicit confirmation and non-empty acceptance notes are required; linked Tasks must be complete."
            ),
            dry_run=True,
            legacy_command=("python scripts/aictl.py workflow run evolution.accept_change --change <CHANGE_ID> --notes <NOTES> --confirm",),
            notes=(
                "Does not use task waivers or --skip-task-check.",
                "Approved Changes are moved through in_progress and in_review before acceptance.",
            ),
        ),
        CommandDescriptor(
            name="epic.close_if_complete",
            domain="epic",
            description="Close an Epic only when all child Tasks are done, deferred, or archived.",
            kind=CommandKind.WRITE,
            arguments=(
                _arg("epic", "Epic ID or key.", required=True),
                _arg("confirm", "Required explicit confirmation.", value_type="boolean", required=True),
            ),
            reads_state=(state_plan, state_tasks),
            writes_state=(state_plan,),
            event_logs=("AI_PROJECT/events/plan-events.jsonl",),
            generated_files=("AI_PROJECT/generated/CODEX_PLAN.md",),
            output=_output("Step-by-step workflow result.", fields=("steps", "epic")),
            validators=("plan_state", "task_state", "child_task_completion"),
            lock_scope="workflow",
            owner_approval=(
                "Explicit confirmation is required; active child Tasks block Epic closure."
            ),
            dry_run=True,
            legacy_command=("python scripts/aictl.py workflow run epic.close_if_complete --epic <EPIC_ID> --confirm",),
            notes=(
                "Preflight rejects Epics with active child Tasks.",
                "Delegates closure to planctl.py epic status <EPIC> --to done.",
            ),
        ),
        CommandDescriptor(
            name="current.set",
            domain="current",
            description="Set the current executable Task through taskctl.py.",
            kind=CommandKind.WRITE,
            arguments=(
                _arg("task_id", "Task ID, ref, UID, legacy ID, or alias.", required=True),
            ),
            reads_state=(state_tasks, state_plan),
            writes_state=(state_tasks,),
            event_logs=("AI_PROJECT/events/task-events.jsonl",),
            generated_files=(
                "AI_PROJECT/generated/CODEX_TASKS.md",
                "AI_PROJECT/generated/CODEX_CURRENT.md",
                "AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md",
            ),
            output=_output("Current task selection result.", fields=("task_id",)),
            validators=("task_state", "plan_references", "task_dependencies"),
            lock_scope="task",
            owner_approval="Current task selection must follow Human Owner-selected work.",
            legacy_command=("python scripts/taskctl.py current set <TASK_ID>",),
        ),
        CommandDescriptor(
            name="current.clear",
            domain="current",
            description="Clear the current executable Task through taskctl.py.",
            kind=CommandKind.WRITE,
            reads_state=(state_tasks, state_plan),
            writes_state=(state_tasks,),
            event_logs=("AI_PROJECT/events/task-events.jsonl",),
            generated_files=(
                "AI_PROJECT/generated/CODEX_TASKS.md",
                "AI_PROJECT/generated/CODEX_CURRENT.md",
                "AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md",
            ),
            output=_output("Current task clear result.", fields=("previous",)),
            validators=("task_state", "plan_references"),
            lock_scope="task",
            owner_approval="Clearing current task must not imply task acceptance or completion.",
            legacy_command=("python scripts/taskctl.py current clear",),
        ),
        CommandDescriptor(
            name="epic.list",
            domain="epic",
            description="List planning Epics managed by planctl.py.",
            kind=CommandKind.READ,
            arguments=(_arg("initiative", "Optional parent Initiative ID filter."),),
            reads_state=(state_plan,),
            output=_output("Epic list.", fields=("epics",)),
            validators=("plan_state",),
            legacy_command=("python scripts/planctl.py epic list",),
        ),
        CommandDescriptor(
            name="change.create",
            domain="change",
            description="Create an Evolution Change Proposal through evolutionctl.py.",
            kind=CommandKind.WRITE,
            arguments=(
                _arg("title", "Change Proposal title.", required=True),
                _arg("type", "Change type.", required=True),
                _arg("problem", "Problem statement.", required=True),
                _arg("proposal", "Proposed change.", required=True),
            ),
            reads_state=(state_evolution, state_tasks),
            writes_state=(state_evolution,),
            event_logs=("AI_PROJECT/events/evolution-events.jsonl",),
            generated_files=("AI_PROJECT/generated/EVOLUTION.md",),
            output=_output("Created Change Proposal.", fields=("change_id",)),
            validators=("evolution_state", "linked_task_references"),
            lock_scope="evolution",
            owner_approval="Human Owner approval required before implementation.",
            dry_run=True,
            legacy_command=("python scripts/evolutionctl.py change create",),
        ),
        CommandDescriptor(
            name="context.build",
            domain="context",
            description="Build deterministic Context Pack generated output.",
            kind=CommandKind.RENDER,
            arguments=(
                _arg("task", "Optional task-scoped context pack."),
                _arg("query", "Optional query-scoped context pack."),
                _arg("write", "Write generated context files.", value_type="boolean"),
            ),
            reads_state=(state_docs, state_tasks),
            event_logs=("AI_PROJECT/events/context-events.jsonl",),
            generated_files=(
                "AI_PROJECT/generated/CONTEXT_PACK.md",
                "AI_PROJECT/generated/CONTEXT_STATUS.md",
            ),
            output=_output("Context Pack build result.", fields=("context_pack", "context_status")),
            validators=("docs_state", "tasks_state", "context_pack_metadata"),
            lock_scope="context",
            legacy_command=("python scripts/contextctl.py pack build",),
            notes=("Generated context is read-only and cannot expand Task scope.",),
        ),
        CommandDescriptor(
            name="codex.prompt.build",
            domain="codex",
            description="Build the current Codex execution prompt package.",
            kind=CommandKind.WRITE,
            arguments=(
                _arg("task", "Task ID for prompt build.", required=True),
                _arg("with_context", "Include default generated Context Pack.", value_type="boolean"),
                _arg("context_pack", "Explicit Context Pack path."),
            ),
            reads_state=(state_tasks, state_plan),
            writes_state=(state_execution,),
            event_logs=("AI_PROJECT/events/codex-events.jsonl",),
            generated_files=(
                "AI_PROJECT/generated/CODEX_PROMPT.md",
                "AI_PROJECT/generated/CODEX_STATUS.md",
            ),
            output=_output("Codex prompt build result.", fields=("task_id", "prompt_path", "status_path")),
            validators=("task_state", "plan_references", "context_pack_freshness"),
            lock_scope="codex",
            owner_approval="Prompt build must not override Task scope or Human Owner gates.",
            legacy_command=("python scripts/codexctl.py build --task <TASK_ID>",),
            notes=("Context inclusion is read-only and validated by codexctl.py.",),
        ),
        CommandDescriptor(
            name="docs.render",
            domain="docs",
            description="Render generated documentation-control views through docctl.py.",
            kind=CommandKind.RENDER,
            reads_state=(state_docs,),
            generated_files=(
                "AI_PROJECT/generated/DOCS_INDEX.md",
                "AI_PROJECT/generated/DOCS_GAPS.md",
            ),
            output=_output("Documentation render result.", fields=("delegate", "returncode")),
            validators=("docs_state", "generated_output"),
            lock_scope="docs",
            legacy_command=("python scripts/docctl.py render",),
            notes=(
                "Delegates rendering to docctl.py.",
                "Does not edit documentation source files.",
            ),
        ),
        CommandDescriptor(
            name="project.doctor",
            domain="project",
            description="Run cross-domain project-control health checks.",
            kind=CommandKind.VALIDATION,
            reads_state=(
                state_plan,
                state_tasks,
                state_evolution,
                state_docs,
                state_execution,
            ),
            output=_output("Project-control health findings.", fields=("findings",)),
            validators=("plan_state", "task_state", "evolution_state", "generated_output"),
            legacy_command=("python scripts/check-protected-project-files.py --verbose",),
            notes=(
                "Aggregates existing validation commands and protected-file checks.",
                "Reports explicit PASS/WARN/FAIL diagnostics.",
                "Does not mutate project-control state.",
            ),
        ),
        CommandDescriptor(
            name="project.protected_check",
            domain="project",
            description="Run protected project-control file validation.",
            kind=CommandKind.VALIDATION,
            reads_state=(
                state_plan,
                state_tasks,
                state_evolution,
                state_docs,
                state_execution,
            ),
            output=_output(
                "Protected-file validation result.",
                fields=("checked", "warnings", "errors"),
            ),
            validators=("protected_files", "generated_output"),
            legacy_command=("python scripts/check-protected-project-files.py --verbose",),
            notes=(
                "Validation-only action; does not mutate protected files.",
                "Does not accept an audit actor because the protected-file checker is read-only.",
            ),
        ),
        CommandDescriptor(
            name="project.render",
            domain="project",
            description="Render generated project-control views through existing ctl scripts.",
            kind=CommandKind.RENDER,
            reads_state=(
                state_plan,
                state_tasks,
                state_evolution,
                state_docs,
                state_execution,
            ),
            event_logs=(
                "AI_PROJECT/events/context-events.jsonl",
            ),
            generated_files=(
                "AI_PROJECT/generated/CODEX_PLAN.md",
                "AI_PROJECT/generated/CODEX_TASKS.md",
                "AI_PROJECT/generated/CODEX_CURRENT.md",
                "AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md",
                "AI_PROJECT/generated/DOCS_INDEX.md",
                "AI_PROJECT/generated/DOCS_GAPS.md",
                "AI_PROJECT/generated/CONTEXT_PACK.md",
                "AI_PROJECT/generated/CONTEXT_STATUS.md",
                "AI_PROJECT/generated/EVOLUTION.md",
            ),
            output=_output("Project-control render result.", fields=("steps",)),
            validators=("plan_state", "task_state", "docs_state", "evolution_state"),
            lock_scope="project",
            legacy_command=(
                "python scripts/planctl.py render",
                "python scripts/taskctl.py render",
                "python scripts/docctl.py render",
                "python scripts/contextctl.py render",
                "python scripts/evolutionctl.py render",
            ),
            notes=(
                "Facade-only orchestration over existing render commands.",
                "Each delegated ctl script remains responsible for its own validation and writes.",
            ),
        ),
        CommandDescriptor(
            name="web.serve",
            domain="web",
            description="Serve the local loopback Web Control Center.",
            kind=CommandKind.READ,
            arguments=(
                _arg("host", "Loopback host to bind.", default="127.0.0.1"),
                _arg("port", "Local port to bind.", value_type="integer", default=8765),
            ),
            reads_state=(
                state_plan,
                state_tasks,
                state_evolution,
                state_docs,
                state_execution,
            ),
            output=_output("Local web dashboard.", fields=("url",)),
            validators=("command_registry", "confirmed_write_routes", "loopback_host"),
            legacy_command=("python scripts/aictl.py web --host 127.0.0.1 --port 8765",),
            notes=(
                "Loopback-only surface with confirmed POST /actions write routes.",
                "Web writes route through registered commands and existing ctl/aictl paths.",
                "Generated Markdown is displayed as derived output only.",
            ),
        ),
        CommandDescriptor(
            name="review.list",
            domain="review",
            description="Planned review-domain list command for future review lifecycle state.",
            kind=CommandKind.READ,
            output=_output("Review records.", fields=("reviews",)),
            availability=CommandAvailability.PLANNED,
            notes=(
                "Review lifecycle state is not implemented in current ctl scripts.",
                "Registered as planned metadata only.",
            ),
        ),
    )

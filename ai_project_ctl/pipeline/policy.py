"""Automation policy model for supervised batch pipeline execution.

The policy is a declarative safety contract. It can describe future pipeline
behavior, but it does not select tasks, launch Codex, close work, or commit.
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Mapping

from ai_project_ctl.core.validation import ValidationResult


class QueueSelection(str, Enum):
    MANUAL = "manual"
    CURRENT_TASK = "current_task"
    READY_QUEUE = "ready_queue"


class CodexExecutionMode(str, Enum):
    DISABLED = "disabled"
    BUILD_PROMPT_ONLY = "build_prompt_only"
    RUN_CODEX = "run_codex"


class CodexAdapterMode(str, Enum):
    DRY_RUN = "dry_run"
    MANUAL_HANDOFF = "manual_handoff"
    LOCAL_COMMAND = "local_command"


class PromptTransport(str, Enum):
    STDIN = "stdin"


class MachineReviewOutcome(str, Enum):
    NONE = "none"
    PASS = "pass"


class CodexReviewDecision(str, Enum):
    NONE = "none"
    APPROVE = "approve"


class CommitMode(str, Enum):
    DISABLED = "disabled"
    LOCAL_ONLY = "local_only"


@dataclass(frozen=True)
class QueuePolicy:
    selection: QueueSelection = QueueSelection.MANUAL
    max_tasks: int = 1
    include_blocked_tasks: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "selection": self.selection.value,
            "max_tasks": self.max_tasks,
            "include_blocked_tasks": self.include_blocked_tasks,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "QueuePolicy":
        return cls(
            selection=_enum_value(QueueSelection, data, "selection"),
            max_tasks=int(data["max_tasks"]),
            include_blocked_tasks=bool(data["include_blocked_tasks"]),
        )


@dataclass(frozen=True)
class EvolutionChangePolicy:
    create_missing_change: bool = False
    approve_linked_change: bool = False
    accept_linked_change: bool = False
    require_approved_change_for_execution: bool = True
    owner_approve_required_changes_for_session: bool = False
    owner_approval_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "create_missing_change": self.create_missing_change,
            "approve_linked_change": self.approve_linked_change,
            "accept_linked_change": self.accept_linked_change,
            "require_approved_change_for_execution": self.require_approved_change_for_execution,
            "owner_approve_required_changes_for_session": self.owner_approve_required_changes_for_session,
            "owner_approval_note": self.owner_approval_note,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "EvolutionChangePolicy":
        return cls(
            create_missing_change=bool(data.get("create_missing_change", False)),
            approve_linked_change=bool(data.get("approve_linked_change", False)),
            accept_linked_change=bool(data.get("accept_linked_change", False)),
            require_approved_change_for_execution=bool(
                data.get("require_approved_change_for_execution", True)
            ),
            owner_approve_required_changes_for_session=bool(
                data.get("owner_approve_required_changes_for_session", False)
            ),
            owner_approval_note=str(data.get("owner_approval_note") or ""),
        )


@dataclass(frozen=True)
class TokenBudgetPolicy:
    require_gate_pass: bool = False
    max_prompt_tokens: int = 32000
    max_context_tokens: int = 24000
    min_remaining_tokens: int = 6000
    reserved_output_tokens: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "require_gate_pass": self.require_gate_pass,
            "max_prompt_tokens": self.max_prompt_tokens,
            "max_context_tokens": self.max_context_tokens,
            "min_remaining_tokens": self.min_remaining_tokens,
            "reserved_output_tokens": self.reserved_output_tokens,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "TokenBudgetPolicy":
        return cls(
            require_gate_pass=bool(data["require_gate_pass"]),
            max_prompt_tokens=int(data["max_prompt_tokens"]),
            max_context_tokens=int(data["max_context_tokens"]),
            min_remaining_tokens=int(data["min_remaining_tokens"]),
            reserved_output_tokens=int(data.get("reserved_output_tokens", 0)),
        )


@dataclass(frozen=True)
class CodexExecutionPolicy:
    mode: CodexExecutionMode = CodexExecutionMode.DISABLED
    require_human_selected_policy: bool = True
    adapter_mode: CodexAdapterMode = CodexAdapterMode.MANUAL_HANDOFF
    prompt_transport: PromptTransport = PromptTransport.STDIN
    local_command: tuple[str, ...] = ()
    command_allowlist: tuple[str, ...] = ()
    timeout_sec: int = 300
    require_report: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode.value,
            "require_human_selected_policy": self.require_human_selected_policy,
            "adapter_mode": self.adapter_mode.value,
            "prompt_transport": self.prompt_transport.value,
            "local_command": list(self.local_command),
            "command_allowlist": list(self.command_allowlist),
            "timeout_sec": self.timeout_sec,
            "require_report": self.require_report,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CodexExecutionPolicy":
        return cls(
            mode=_enum_value(CodexExecutionMode, data, "mode"),
            require_human_selected_policy=bool(data["require_human_selected_policy"]),
            adapter_mode=_enum_value(
                CodexAdapterMode,
                data,
                "adapter_mode",
                default=CodexAdapterMode.MANUAL_HANDOFF,
            ),
            prompt_transport=_enum_value(
                PromptTransport,
                data,
                "prompt_transport",
                default=PromptTransport.STDIN,
            ),
            local_command=_string_tuple(data.get("local_command", ())),
            command_allowlist=_string_tuple(data.get("command_allowlist", ())),
            timeout_sec=int(data.get("timeout_sec", 300)),
            require_report=bool(data.get("require_report", True)),
        )


@dataclass(frozen=True)
class ReviewPolicy:
    require_machine_review: bool = False
    required_machine_outcome: MachineReviewOutcome = MachineReviewOutcome.NONE
    require_codex_review: bool = False
    required_codex_decision: CodexReviewDecision = CodexReviewDecision.NONE

    def to_dict(self) -> dict[str, Any]:
        return {
            "require_machine_review": self.require_machine_review,
            "required_machine_outcome": self.required_machine_outcome.value,
            "require_codex_review": self.require_codex_review,
            "required_codex_decision": self.required_codex_decision.value,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ReviewPolicy":
        return cls(
            require_machine_review=bool(data["require_machine_review"]),
            required_machine_outcome=_enum_value(
                MachineReviewOutcome, data, "required_machine_outcome"
            ),
            require_codex_review=bool(data["require_codex_review"]),
            required_codex_decision=_enum_value(
                CodexReviewDecision, data, "required_codex_decision"
            ),
        )


@dataclass(frozen=True)
class ReworkPolicy:
    allow_rework_loop: bool = False
    max_rework_attempts: int = 0
    require_owner_decision_for_rework: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "allow_rework_loop": self.allow_rework_loop,
            "max_rework_attempts": self.max_rework_attempts,
            "require_owner_decision_for_rework": self.require_owner_decision_for_rework,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ReworkPolicy":
        return cls(
            allow_rework_loop=bool(data["allow_rework_loop"]),
            max_rework_attempts=int(data["max_rework_attempts"]),
            require_owner_decision_for_rework=bool(
                data["require_owner_decision_for_rework"]
            ),
        )


@dataclass(frozen=True)
class BatchPolicy:
    max_steps: int = 5
    max_failures: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_steps": self.max_steps,
            "max_failures": self.max_failures,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> "BatchPolicy":
        value = data or {}
        return cls(
            max_steps=int(value.get("max_steps", cls.max_steps)),
            max_failures=int(value.get("max_failures", cls.max_failures)),
        )


@dataclass(frozen=True)
class TaskClosurePolicy:
    auto_close_task: bool = False
    owner_approval_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "auto_close_task": self.auto_close_task,
            "owner_approval_note": self.owner_approval_note,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "TaskClosurePolicy":
        return cls(
            auto_close_task=bool(data["auto_close_task"]),
            owner_approval_note=str(data.get("owner_approval_note") or ""),
        )


@dataclass(frozen=True)
class CommitPolicy:
    create_local_commit: bool = False
    mode: CommitMode = CommitMode.DISABLED
    require_commit_readiness: bool = False
    allow_push: bool = False
    allow_merge: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "create_local_commit": self.create_local_commit,
            "mode": self.mode.value,
            "require_commit_readiness": self.require_commit_readiness,
            "allow_push": self.allow_push,
            "allow_merge": self.allow_merge,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CommitPolicy":
        return cls(
            create_local_commit=bool(data["create_local_commit"]),
            mode=_enum_value(CommitMode, data, "mode"),
            require_commit_readiness=bool(data["require_commit_readiness"]),
            allow_push=bool(data["allow_push"]),
            allow_merge=bool(data["allow_merge"]),
        )


@dataclass(frozen=True)
class PipelinePolicy:
    name: str = "default"
    queue: QueuePolicy = QueuePolicy()
    evolution: EvolutionChangePolicy = EvolutionChangePolicy()
    token_budget: TokenBudgetPolicy = TokenBudgetPolicy()
    codex: CodexExecutionPolicy = CodexExecutionPolicy()
    review: ReviewPolicy = ReviewPolicy()
    rework: ReworkPolicy = ReworkPolicy()
    batch: BatchPolicy = BatchPolicy()
    closure: TaskClosurePolicy = TaskClosurePolicy()
    commit: CommitPolicy = CommitPolicy()

    @classmethod
    def default(cls) -> "PipelinePolicy":
        return cls()

    def validate(self) -> ValidationResult:
        return validate_policy(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "queue": self.queue.to_dict(),
            "evolution": self.evolution.to_dict(),
            "token_budget": self.token_budget.to_dict(),
            "codex": self.codex.to_dict(),
            "review": self.review.to_dict(),
            "rework": self.rework.to_dict(),
            "batch": self.batch.to_dict(),
            "closure": self.closure.to_dict(),
            "commit": self.commit.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PipelinePolicy":
        return cls(
            name=str(data["name"]),
            queue=QueuePolicy.from_dict(_mapping(data, "queue")),
            evolution=EvolutionChangePolicy.from_dict(_mapping(data, "evolution")),
            token_budget=TokenBudgetPolicy.from_dict(_mapping(data, "token_budget")),
            codex=CodexExecutionPolicy.from_dict(_mapping(data, "codex")),
            review=ReviewPolicy.from_dict(_mapping(data, "review")),
            rework=ReworkPolicy.from_dict(_mapping(data, "rework")),
            batch=BatchPolicy.from_dict(data.get("batch") if isinstance(data, Mapping) else None),
            closure=TaskClosurePolicy.from_dict(_mapping(data, "closure")),
            commit=CommitPolicy.from_dict(_mapping(data, "commit")),
        )


def validate_policy(policy: PipelinePolicy) -> ValidationResult:
    """Validate a pipeline policy without mutating project-control state."""

    result = ValidationResult()

    if policy.queue.max_tasks < 1:
        result.add_error(
            "POLICY_INVALID_QUEUE_LIMIT",
            "Queue policy must select at least one task when a queue is used.",
            path="queue.max_tasks",
        )
    if policy.queue.include_blocked_tasks:
        result.add_error(
            "POLICY_QUEUE_INCLUDES_BLOCKED_TASKS",
            "Pipeline policy must not select blocked tasks automatically.",
            path="queue.include_blocked_tasks",
        )

    if policy.evolution.approve_linked_change:
        result.add_error(
            "POLICY_APPROVES_EVOLUTION_CHANGE",
            "Pipeline policy must not approve Evolution Changes automatically.",
            path="evolution.approve_linked_change",
        )
    if policy.evolution.accept_linked_change:
        result.add_error(
            "POLICY_ACCEPTS_EVOLUTION_CHANGE",
            "Pipeline policy must not accept Evolution Changes automatically.",
            path="evolution.accept_linked_change",
        )
    if (
        policy.evolution.owner_approve_required_changes_for_session
        and not policy.evolution.owner_approval_note.strip()
    ):
        result.add_error(
            "POLICY_OWNER_CHANGE_APPROVAL_NOTE_REQUIRED",
            "Owner-approved session Change approval requires a non-empty approval note.",
            path="evolution.owner_approval_note",
        )
    if (
        policy.codex.mode != CodexExecutionMode.DISABLED
        and not policy.evolution.require_approved_change_for_execution
    ):
        result.add_error(
            "POLICY_EXECUTION_WITHOUT_APPROVED_CHANGE_GATE",
            "Codex execution policy must require an approved linked Evolution Change.",
            path="evolution.require_approved_change_for_execution",
        )

    _validate_token_thresholds(policy, result)

    if (
        policy.codex.mode == CodexExecutionMode.RUN_CODEX
        and not policy.token_budget.require_gate_pass
    ):
        result.add_error(
            "POLICY_EXECUTION_WITHOUT_TOKEN_GATE",
            "Codex execution must require Token Budget Gate PASS.",
            path="token_budget.require_gate_pass",
        )
    if policy.codex.mode != CodexExecutionMode.DISABLED:
        if not policy.codex.require_human_selected_policy:
            result.add_error(
                "POLICY_EXECUTION_WITHOUT_HUMAN_POLICY_SELECTION",
                "Codex execution must require an explicitly selected Human Owner policy.",
                path="codex.require_human_selected_policy",
            )
    _validate_codex_adapter_policy(policy, result)

    if policy.closure.auto_close_task:
        _validate_auto_close(policy, result)

    if policy.rework.allow_rework_loop:
        if policy.rework.max_rework_attempts < 1:
            result.add_error(
                "POLICY_REWORK_LOOP_REQUIRES_BOUND",
                "Rework loop must define at least one bounded attempt.",
                path="rework.max_rework_attempts",
            )
        if not policy.rework.require_owner_decision_for_rework:
            result.add_error(
                "POLICY_REWORK_LOOP_REQUIRES_OWNER_DECISION",
                "Rework loop must keep Human Owner decision in the loop.",
                path="rework.require_owner_decision_for_rework",
            )

    _validate_batch_policy(policy, result)
    _validate_commit_policy(policy, result)

    return result


def preset_names() -> tuple[str, ...]:
    return tuple(_LISTED_PRESETS)


def builtin_preset_names(*, include_unlisted: bool = False) -> tuple[str, ...]:
    if include_unlisted:
        return tuple(_PRESETS)
    return preset_names()


def is_builtin_preset_name(name: str) -> bool:
    return name in _PRESETS


def policy_preset(name: str) -> PipelinePolicy:
    try:
        return _PRESETS[name]()
    except KeyError as exc:
        allowed = ", ".join(preset_names())
        raise ValueError(f"Unknown pipeline policy preset: {name}. Expected one of: {allowed}") from exc


def _dry_run() -> PipelinePolicy:
    return PipelinePolicy(name="dry_run")


def _supervised() -> PipelinePolicy:
    return PipelinePolicy(
        name="supervised",
        queue=QueuePolicy(
            selection=QueueSelection.READY_QUEUE,
            max_tasks=1,
            include_blocked_tasks=False,
        ),
        evolution=EvolutionChangePolicy(
            create_missing_change=False,
            approve_linked_change=False,
            accept_linked_change=False,
            require_approved_change_for_execution=True,
        ),
        token_budget=TokenBudgetPolicy(require_gate_pass=True),
        codex=CodexExecutionPolicy(
            mode=CodexExecutionMode.BUILD_PROMPT_ONLY,
            require_human_selected_policy=True,
        ),
        review=_passing_review_policy(),
        rework=ReworkPolicy(
            allow_rework_loop=True,
            max_rework_attempts=1,
            require_owner_decision_for_rework=True,
        ),
    )


def _supervised_autoclose() -> PipelinePolicy:
    return replace(
        _supervised(),
        name="supervised_autoclose",
        closure=TaskClosurePolicy(auto_close_task=True),
    )


def _supervised_auto_create_changes() -> PipelinePolicy:
    base = _supervised()
    return replace(
        base,
        name="supervised_auto_create_changes",
        evolution=replace(base.evolution, create_missing_change=True),
    )


def _supervised_local_commit() -> PipelinePolicy:
    return replace(
        _supervised_autoclose(),
        name="supervised_local_commit",
        commit=CommitPolicy(
            create_local_commit=True,
            mode=CommitMode.LOCAL_ONLY,
            require_commit_readiness=True,
            allow_push=False,
            allow_merge=False,
        ),
    )


def _with_local_codex(policy: PipelinePolicy) -> PipelinePolicy:
    return replace(
        policy,
        codex=replace(
            policy.codex,
            mode=CodexExecutionMode.RUN_CODEX,
            adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
            local_command=("codex", "exec"),
            command_allowlist=("codex exec",),
            require_report=True,
        ),
    )


def _supervised_executable() -> PipelinePolicy:
    return replace(
        _with_local_codex(_supervised()),
        name="supervised_executable",
    )


def _supervised_executable_autoclose() -> PipelinePolicy:
    return replace(
        _with_local_codex(_supervised_autoclose()),
        name="supervised_executable_autoclose",
    )


def _supervised_executable_local_commit() -> PipelinePolicy:
    return replace(
        _with_local_codex(_supervised_local_commit()),
        name="supervised_executable_local_commit",
    )


def _passing_review_policy() -> ReviewPolicy:
    return ReviewPolicy(
        require_machine_review=True,
        required_machine_outcome=MachineReviewOutcome.PASS,
        require_codex_review=True,
        required_codex_decision=CodexReviewDecision.APPROVE,
    )


def _validate_token_thresholds(
    policy: PipelinePolicy,
    result: ValidationResult,
) -> None:
    thresholds = {
        "token_budget.max_prompt_tokens": policy.token_budget.max_prompt_tokens,
        "token_budget.max_context_tokens": policy.token_budget.max_context_tokens,
        "token_budget.min_remaining_tokens": policy.token_budget.min_remaining_tokens,
        "token_budget.reserved_output_tokens": policy.token_budget.reserved_output_tokens,
    }
    for path, value in thresholds.items():
        if value < 0:
            result.add_error(
                "POLICY_INVALID_TOKEN_THRESHOLD",
                "Token budget thresholds must be zero or greater.",
                path=path,
            )
    if policy.token_budget.max_context_tokens > policy.token_budget.max_prompt_tokens:
        result.add_error(
            "POLICY_CONTEXT_EXCEEDS_PROMPT_BUDGET",
            "Context token threshold must not exceed total prompt token threshold.",
            path="token_budget.max_context_tokens",
        )


def _validate_auto_close(policy: PipelinePolicy, result: ValidationResult) -> None:
    if (
        not policy.review.require_machine_review
        or policy.review.required_machine_outcome != MachineReviewOutcome.PASS
    ):
        result.add_error(
            "POLICY_AUTO_CLOSE_REQUIRES_MACHINE_REVIEW_PASS",
            "Auto-close requires Machine Review PASS.",
            path="review.required_machine_outcome",
        )
    if (
        not policy.review.require_codex_review
        or policy.review.required_codex_decision != CodexReviewDecision.APPROVE
    ):
        result.add_error(
            "POLICY_AUTO_CLOSE_REQUIRES_CODEX_REVIEW_APPROVE",
            "Auto-close requires Codex Review APPROVE.",
            path="review.required_codex_decision",
        )


def _validate_commit_policy(policy: PipelinePolicy, result: ValidationResult) -> None:
    if policy.commit.allow_push:
        result.add_error(
            "POLICY_PUSH_FORBIDDEN",
            "Pipeline policy must not authorize push.",
            path="commit.allow_push",
        )
    if policy.commit.allow_merge:
        result.add_error(
            "POLICY_MERGE_FORBIDDEN",
            "Pipeline policy must not authorize merge.",
            path="commit.allow_merge",
        )
    if not policy.commit.create_local_commit:
        if policy.commit.mode != CommitMode.DISABLED:
            result.add_error(
                "POLICY_COMMIT_DISABLED_MODE_MISMATCH",
                "Disabled commit policy must use disabled mode.",
                path="commit.mode",
            )
        return

    if policy.commit.mode != CommitMode.LOCAL_ONLY:
        result.add_error(
            "POLICY_COMMIT_MUST_BE_LOCAL_ONLY",
            "Commit policy must be local-only.",
            path="commit.mode",
        )
    if not policy.commit.require_commit_readiness:
        result.add_error(
            "POLICY_COMMIT_REQUIRES_COMMIT_READINESS",
            "Local commit policy must require commit readiness.",
            path="commit.require_commit_readiness",
        )
    if not _requires_approved_reviews(policy):
        result.add_error(
            "POLICY_COMMIT_REQUIRES_APPROVED_REVIEWS",
            "Local commit policy must require Machine Review PASS and Codex Review APPROVE.",
            path="review",
        )


def _validate_batch_policy(policy: PipelinePolicy, result: ValidationResult) -> None:
    if policy.batch.max_steps < 1:
        result.add_error(
            "POLICY_BATCH_INVALID_MAX_STEPS",
            "Batch runner max_steps must be at least one.",
            path="batch.max_steps",
        )
    if policy.batch.max_steps > 50:
        result.add_error(
            "POLICY_BATCH_MAX_STEPS_TOO_LARGE",
            "Batch runner max_steps must not exceed 50.",
            path="batch.max_steps",
        )
    if policy.batch.max_failures < 1:
        result.add_error(
            "POLICY_BATCH_INVALID_MAX_FAILURES",
            "Batch runner max_failures must be at least one.",
            path="batch.max_failures",
        )
    if policy.batch.max_failures > 10:
        result.add_error(
            "POLICY_BATCH_MAX_FAILURES_TOO_LARGE",
            "Batch runner max_failures must not exceed 10.",
            path="batch.max_failures",
        )


def _validate_codex_adapter_policy(policy: PipelinePolicy, result: ValidationResult) -> None:
    if policy.codex.timeout_sec < 1:
        result.add_error(
            "POLICY_CODEX_INVALID_TIMEOUT",
            "Codex adapter timeout must be at least one second.",
            path="codex.timeout_sec",
        )
    if policy.codex.timeout_sec > 3600:
        result.add_error(
            "POLICY_CODEX_TIMEOUT_TOO_LARGE",
            "Codex adapter timeout must not exceed 3600 seconds.",
            path="codex.timeout_sec",
        )

    if policy.codex.mode != CodexExecutionMode.RUN_CODEX:
        return

    if not policy.codex.require_report:
        result.add_error(
            "POLICY_CODEX_REQUIRES_REPORT",
            "Codex execution must require a structured execution report.",
            path="codex.require_report",
        )

    if policy.codex.adapter_mode != CodexAdapterMode.LOCAL_COMMAND:
        return

    if policy.codex.prompt_transport != PromptTransport.STDIN:
        result.add_error(
            "POLICY_CODEX_UNSUPPORTED_PROMPT_TRANSPORT",
            "Local-command Codex execution currently supports stdin prompt transport only.",
            path="codex.prompt_transport",
        )

    if not policy.codex.local_command:
        result.add_error(
            "POLICY_CODEX_LOCAL_COMMAND_REQUIRED",
            "Local-command adapter mode requires an explicit command.",
            path="codex.local_command",
        )
        return

    command_key = shlex.join(policy.codex.local_command)
    if command_key not in set(policy.codex.command_allowlist):
        result.add_error(
            "POLICY_CODEX_COMMAND_NOT_ALLOWLISTED",
            "Local Codex command must exactly match the policy command allowlist.",
            path="codex.command_allowlist",
        )


def _requires_approved_reviews(policy: PipelinePolicy) -> bool:
    return (
        policy.review.require_machine_review
        and policy.review.required_machine_outcome == MachineReviewOutcome.PASS
        and policy.review.require_codex_review
        and policy.review.required_codex_decision == CodexReviewDecision.APPROVE
    )


def _mapping(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = data[key]
    if not isinstance(value, Mapping):
        raise TypeError(f"Expected mapping for policy field: {key}")
    return value


def _enum_value(
    enum_type: type[Enum],
    data: Mapping[str, Any],
    key: str,
    *,
    default: Enum | None = None,
) -> Any:
    if key not in data and default is not None:
        return default
    return enum_type(data[key])


def _string_tuple(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,) if value.strip() else ()
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item) for item in value if str(item).strip())


def policy_behavior_label(policy: PipelinePolicy) -> str:
    """Human-facing policy summary for CLI and Web Control Center choices."""

    labels: list[str] = []
    if policy.codex.mode == CodexExecutionMode.DISABLED:
        labels.append("dry-run")
    elif policy.codex.mode == CodexExecutionMode.BUILD_PROMPT_ONLY:
        labels.append("prompt-only")
    elif policy.codex.mode == CodexExecutionMode.RUN_CODEX:
        if policy.codex.adapter_mode == CodexAdapterMode.LOCAL_COMMAND:
            labels.append("executable")
        elif policy.codex.adapter_mode == CodexAdapterMode.MANUAL_HANDOFF:
            labels.append("manual-handoff")
        else:
            labels.append("run-codex")
    else:
        labels.append(policy.codex.mode.value)

    if policy.closure.auto_close_task:
        if policy.codex.mode == CodexExecutionMode.BUILD_PROMPT_ONLY:
            labels.append("auto-close blocked")
        elif not policy.closure.owner_approval_note.strip():
            labels.append("auto-close needs note")
        else:
            labels.append("auto-close")
    if policy.commit.create_local_commit:
        if policy.codex.mode == CodexExecutionMode.BUILD_PROMPT_ONLY:
            labels.append("local-commit blocked")
        else:
            labels.append("local-commit")
    return " / ".join(labels)


_PRESETS = {
    "dry_run": _dry_run,
    "supervised": _supervised,
    "supervised_auto_create_changes": _supervised_auto_create_changes,
    "supervised_autoclose": _supervised_autoclose,
    "supervised_local_commit": _supervised_local_commit,
    "supervised_executable": _supervised_executable,
    "supervised_executable_autoclose": _supervised_executable_autoclose,
    "supervised_executable_local_commit": _supervised_executable_local_commit,
}

_LISTED_PRESETS = (
    "dry_run",
    "supervised",
    "supervised_executable",
    "supervised_autoclose",
    "supervised_executable_autoclose",
    "supervised_local_commit",
    "supervised_executable_local_commit",
)

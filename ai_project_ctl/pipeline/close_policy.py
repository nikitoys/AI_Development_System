"""Policy-controlled task close and request-changes decisions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from ai_project_ctl.core.result import CommandMessage, CommandResult
from ai_project_ctl.core.workflows import Runner, run_workflow

from .codex_review import (
    PASS as CODEX_REVIEW_PASS,
    VERDICT_APPROVE,
    VERDICT_REQUEST_CHANGES,
    CodexReviewResult,
)
from .machine_review import PASS as MACHINE_REVIEW_PASS
from .machine_review import MachineReviewResult
from .policy import PipelinePolicy
from .report_gate import PASS as REPORT_GATE_PASS
from .report_gate import ReportGateResult


ACTION_CLOSE_TASK = "close_task"
ACTION_REQUEST_CHANGES = "request_changes"
ACTION_STOP = "stop"

CODE_TASK_AUTO_CLOSED = "TASK_AUTO_CLOSED"
CODE_REQUEST_CHANGES = "CODEX_REVIEW_REQUEST_CHANGES"
CODE_OWNER_NOTE_REQUIRED = "AUTO_CLOSE_OWNER_NOTE_REQUIRED"
CODE_REWORK_LIMIT_REACHED = "REWORK_LIMIT_REACHED"
CODE_REWORK_POLICY_DISABLED = "REWORK_POLICY_DISABLED"
CODE_REVIEW_CLOSE_BLOCKED = "REVIEW_CLOSE_POLICY_BLOCKED"
CODE_REVIEW_CLOSE_WORKFLOW_FAILED = "REVIEW_CLOSE_WORKFLOW_FAILED"


@dataclass(frozen=True)
class ReviewCloseDecision:
    """Decision produced after Machine Review and Codex Review gates."""

    action: str
    stop_code: str
    reason: str
    result_status: str
    gate_status: str
    notes: str
    details: Mapping[str, Any]

    @property
    def should_run_workflow(self) -> bool:
        return self.action in {ACTION_CLOSE_TASK, ACTION_REQUEST_CHANGES}

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "stop_code": self.stop_code,
            "reason": self.reason,
            "result_status": self.result_status,
            "gate_status": self.gate_status,
            "notes": self.notes,
            "details": dict(self.details),
        }


def decide_review_close(
    *,
    policy: PipelinePolicy,
    report_gate: ReportGateResult,
    machine_review: MachineReviewResult,
    codex_review: CodexReviewResult,
    session: Mapping[str, Any],
) -> ReviewCloseDecision:
    """Map review gate outcomes to close, request-changes, or stop."""

    details = _decision_details(policy, report_gate, machine_review, codex_review, session)
    notes = _audit_notes(policy, report_gate, machine_review, codex_review)

    if not policy.closure.auto_close_task:
        return _stop(
            CODE_REVIEW_CLOSE_BLOCKED,
            "Task auto-close is disabled by pipeline policy.",
            details=details,
            notes=notes,
            result_status="passed",
            gate_status="skipped",
        )

    if not policy.closure.owner_approval_note.strip():
        return _stop(
            CODE_OWNER_NOTE_REQUIRED,
            "Task auto-close requires an explicit Human Owner approval note.",
            details=details,
            notes=notes,
        )

    if report_gate.status != REPORT_GATE_PASS:
        return _stop(
            CODE_REVIEW_CLOSE_BLOCKED,
            "Task auto-close blocked because Codex Report Gate is not PASS: {}".format(
                report_gate.status
            ),
            details=details,
            notes=notes,
        )

    if machine_review.status != MACHINE_REVIEW_PASS:
        return _stop(
            CODE_REVIEW_CLOSE_BLOCKED,
            "Task auto-close blocked because Machine Review is not PASS: {}".format(
                machine_review.status
            ),
            details=details,
            notes=notes,
        )

    if codex_review.status == CODEX_REVIEW_PASS and codex_review.verdict == VERDICT_APPROVE:
        return ReviewCloseDecision(
            action=ACTION_CLOSE_TASK,
            stop_code=CODE_TASK_AUTO_CLOSED,
            reason=(
                "Task auto-close completed after policy permission, "
                "Machine Review PASS, and Codex Review APPROVE."
            ),
            result_status="passed",
            gate_status="pass",
            notes=notes,
            details=details,
        )

    if codex_review.verdict == VERDICT_REQUEST_CHANGES:
        if not policy.rework.allow_rework_loop:
            return _stop(
                CODE_REWORK_POLICY_DISABLED,
                "Codex Review requested changes, but policy does not allow a rework loop.",
                details=details,
                notes=notes,
            )

        current_rework = _rework_count(session)
        max_rework = int(policy.rework.max_rework_attempts)
        if current_rework >= max_rework:
            return _stop(
                CODE_REWORK_LIMIT_REACHED,
                "Codex Review requested changes, but rework limit is reached: {}/{}.".format(
                    current_rework,
                    max_rework,
                ),
                details={
                    **details,
                    "rework_attempts_used": current_rework,
                    "max_rework_attempts": max_rework,
                },
                notes=notes,
            )

        return ReviewCloseDecision(
            action=ACTION_REQUEST_CHANGES,
            stop_code=CODE_REQUEST_CHANGES,
            reason=(
                "Codex Review requested changes; task was moved to changes_requested "
                "through governed workflow."
            ),
            result_status="blocked",
            gate_status="blocked",
            notes=notes,
            details={
                **details,
                "rework_attempt": current_rework + 1,
                "max_rework_attempts": max_rework,
            },
        )

    return _stop(
        CODE_REVIEW_CLOSE_BLOCKED,
        "Task auto-close blocked because Codex Review did not approve the task.",
        details=details,
        notes=notes,
    )


def run_review_close_workflow(
    decision: ReviewCloseDecision,
    *,
    root: str | Path,
    actor: str,
    task_id: str,
    python_executable: str,
    runner: Runner | None,
) -> CommandResult:
    """Apply a close-policy decision through governed workflows."""

    if not decision.should_run_workflow:
        return CommandResult.success(
            command="pipeline.review_close_policy",
            domain="pipeline",
            message=decision.reason,
            data={"decision": decision.to_dict(), "workflows": []},
        )

    workflow_results: list[CommandResult] = []
    submit = run_workflow(
        "task.submit_for_review",
        task_ref=task_id,
        root=root,
        actor=actor,
        confirmed=True,
        python_executable=python_executable,
        runner=runner,
    )
    workflow_results.append(submit)
    if not submit.ok:
        return _workflow_failure(decision, workflow_results, "task.submit_for_review")

    workflow_name = (
        "task.close_reviewed"
        if decision.action == ACTION_CLOSE_TASK
        else "task.request_changes"
    )
    applied = run_workflow(
        workflow_name,
        task_ref=task_id,
        notes=decision.notes,
        root=root,
        actor=actor,
        confirmed=True,
        python_executable=python_executable,
        runner=runner,
    )
    workflow_results.append(applied)
    if not applied.ok:
        return _workflow_failure(decision, workflow_results, workflow_name)

    result = CommandResult.success(
        command="pipeline.review_close_policy",
        domain="pipeline",
        message=decision.reason,
        data={
            "decision": decision.to_dict(),
            "workflows": [item.to_dict() for item in workflow_results],
        },
    )
    _merge_workflow_effects(result, workflow_results)
    if decision.action == ACTION_REQUEST_CHANGES:
        result.owner_action_required = (
            "Task is changes_requested; Human Owner must decide whether to prepare rework."
        )
    return result


def _stop(
    stop_code: str,
    reason: str,
    *,
    details: Mapping[str, Any],
    notes: str,
    result_status: str = "blocked",
    gate_status: str = "blocked",
) -> ReviewCloseDecision:
    return ReviewCloseDecision(
        action=ACTION_STOP,
        stop_code=stop_code,
        reason=reason,
        result_status=result_status,
        gate_status=gate_status,
        notes=notes,
        details=details,
    )


def _decision_details(
    policy: PipelinePolicy,
    report_gate: ReportGateResult,
    machine_review: MachineReviewResult,
    codex_review: CodexReviewResult,
    session: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "policy": policy.name,
        "report_id": report_gate.report_id,
        "report_gate_status": report_gate.status,
        "report_gate_code": report_gate.code,
        "machine_review_status": machine_review.status,
        "machine_review_code": machine_review.code,
        "codex_review_status": codex_review.status,
        "codex_review_code": codex_review.code,
        "codex_review_verdict": codex_review.verdict,
        "review_id": codex_review.review_id,
        "session_id": str(session.get("id") or ""),
        "rework_attempts_used": _rework_count(session),
        "max_rework_attempts": int(policy.rework.max_rework_attempts),
        "owner_auto_close_note": policy.closure.owner_approval_note.strip(),
    }


def _audit_notes(
    policy: PipelinePolicy,
    report_gate: ReportGateResult,
    machine_review: MachineReviewResult,
    codex_review: CodexReviewResult,
) -> str:
    return (
        "Owner auto-close note={owner_note}; "
        "Pipeline policy={policy}; machine_gate={machine_status}/{machine_code}; "
        "codex_review={verdict}/{review_code}; report_id={report_id}; "
        "review_id={review_id}"
    ).format(
        owner_note=policy.closure.owner_approval_note.strip() or "missing",
        policy=policy.name,
        machine_status=machine_review.status,
        machine_code=machine_review.code,
        verdict=codex_review.verdict or codex_review.status,
        review_code=codex_review.code,
        report_id=report_gate.report_id or codex_review.report_id,
        review_id=codex_review.review_id or "none",
    )


def _rework_count(session: Mapping[str, Any]) -> int:
    counters = session.get("attempt_counters")
    value = counters.get("rework") if isinstance(counters, Mapping) else 0
    try:
        counter_value = int(value)
    except (TypeError, ValueError):
        counter_value = 0

    gate_count = 0
    for step in session.get("steps", []):
        if not isinstance(step, Mapping):
            continue
        for gate in step.get("gate_outcomes", []):
            if not isinstance(gate, Mapping):
                continue
            if gate.get("name") != "review_close_gate":
                continue
            details = gate.get("details")
            if not isinstance(details, Mapping):
                continue
            close_policy = details.get("close_policy")
            if isinstance(close_policy, Mapping) and close_policy.get("action") == ACTION_REQUEST_CHANGES:
                gate_count += 1
    return max(counter_value, gate_count)


def _workflow_failure(
    decision: ReviewCloseDecision,
    workflow_results: Sequence[CommandResult],
    workflow_name: str,
) -> CommandResult:
    errors: list[CommandMessage] = []
    for item in workflow_results:
        errors.extend(item.errors)
    if not errors:
        errors.append(
            CommandMessage(
                CODE_REVIEW_CLOSE_WORKFLOW_FAILED,
                "Review close workflow failed: {}".format(workflow_name),
            )
        )
    result = CommandResult.failure(
        command="pipeline.review_close_policy",
        domain="pipeline",
        message="Review close workflow failed: {}".format(workflow_name),
        errors=errors,
    )
    result.data = {
        "decision": decision.to_dict(),
        "failed_workflow": workflow_name,
        "workflows": [item.to_dict() for item in workflow_results],
    }
    _merge_workflow_effects(result, workflow_results)
    return result


def _merge_workflow_effects(
    target: CommandResult,
    workflow_results: Sequence[CommandResult],
) -> None:
    for item in workflow_results:
        _extend_unique(target.changed_files, item.changed_files)
        _extend_unique(target.generated_files, item.generated_files)
        _extend_unique(target.events, item.events)
        target.warnings.extend(item.warnings)
        target.next_actions.extend(item.next_actions)


def _extend_unique(target: list[str], values: Sequence[str]) -> None:
    for value in values:
        if value not in target:
            target.append(value)

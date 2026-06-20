"""Supervised one-step pipeline runner.

The runner advances at most one pipeline step. It records every gate through
the governed pipeline session service and delegates lifecycle mutations to
existing workflow commands.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from ai_project_ctl.core.result import CommandMessage, CommandResult
from ai_project_ctl.core.store import read_json_file
from ai_project_ctl.core.workflows import Runner, run_workflow

from .codex_adapter import CodexAdapterResult, run_codex_adapter
from .codex_review import BLOCKED as CODEX_REVIEW_BLOCKED_STATUS
from .codex_review import FAIL as CODEX_REVIEW_FAIL
from .codex_review import PASS as CODEX_REVIEW_PASS
from .codex_review import VERDICT_BLOCKED
from .codex_review import VERDICT_REQUEST_CHANGES
from .codex_review import evaluate_codex_review
from .machine_review import FAIL as MACHINE_REVIEW_FAIL
from .machine_review import evaluate_machine_review
from .policy import CodexExecutionMode, PipelinePolicy
from .queue import QueuePlannerRequest, QueuePreview, QueuePreviewItem, preview_queue
from .report_gate import FAIL as REPORT_GATE_FAIL
from .report_gate import evaluate_report_gate
from .session import (
    complete_session,
    record_step_result,
    start_step,
)
from .state import (
    load_pipeline_state,
    load_reference_state,
    pipeline_state_path,
)
from .token_budget import PASS as TOKEN_BUDGET_PASS
from .token_budget import evaluate_token_budget


RUN_NEXT_STEP = "run_next"
ACTIVE_RUN_NEXT_STATUSES = {"planned", "running"}
TERMINAL_CHANGE_STATUSES = {"approved", "in_progress", "in_review", "accepted"}


def run_next(
    session_id: str = "",
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    python_executable: str | None = None,
    runner: Runner | None = None,
    codex_adapter=None,
    codex_reviewer=None,
) -> CommandResult:
    """Advance one supervised pipeline session step and stop on blockers."""

    root_path = Path(root).resolve()
    python_bin = python_executable or sys.executable
    execution_runner = runner

    session_context = _resolve_session(root_path, session_id)
    if not session_context.ok:
        return session_context

    session = dict(session_context.data["session"])
    selected_session_id = str(session["id"])
    if str(session.get("status") or "") not in ACTIVE_RUN_NEXT_STATUSES:
        return _safe_stop_result(
            session_id=selected_session_id,
            stop_code="BLOCKED",
            stop_reason="Pipeline session is not runnable: {}".format(session.get("status")),
            selected_task=None,
            policy_name=_policy_name(session),
            queue_preview=None,
            side_effects=[],
        )

    side_effects: list[CommandResult] = []
    started = start_step(
        selected_session_id,
        RUN_NEXT_STEP,
        root=root_path,
        actor=actor,
    )
    side_effects.append(started)
    if not started.ok:
        return _aggregate_failure(
            "pipeline.run_next",
            "Failed to start pipeline step.",
            selected_session_id,
            side_effects,
        )

    try:
        policy = PipelinePolicy.from_dict(_mapping(session.get("policy_snapshot"), "policy_snapshot"))
    except (KeyError, TypeError, ValueError) as exc:
        return _record_stop(
            selected_session_id,
            stop_code="POLICY_VIOLATION",
            stop_reason="Pipeline policy snapshot is invalid: {}".format(exc),
            result_status="failed",
            gate_name="policy_validation",
            gate_status="fail",
            gate_details={"policy": _policy_name(session), "error": str(exc)},
            selected_task=None,
            policy_name=_policy_name(session),
            queue_preview=None,
            side_effects=side_effects,
            root=root_path,
            actor=actor,
        )
    policy_result = policy.validate()
    if not policy_result.ok:
        return _record_stop(
            selected_session_id,
            stop_code="POLICY_VIOLATION",
            stop_reason="Pipeline policy is invalid.",
            result_status="failed",
            gate_name="policy_validation",
            gate_status="fail",
            gate_details={
                "policy": policy.name,
                "errors": [issue.code for issue in policy_result.errors],
            },
            selected_task=None,
            policy_name=policy.name,
            queue_preview=None,
            side_effects=side_effects,
            root=root_path,
            actor=actor,
        )

    refs = load_reference_state(root_path)
    try:
        tasks_state = _mapping(refs.get("tasks"), "tasks")
        plan = _load_plan(root_path)
        queue_preview = _preview_session_queue(session, policy, tasks_state, plan)
    except (KeyError, TypeError, ValueError) as exc:
        return _record_stop(
            selected_session_id,
            stop_code="UNSAFE_CONDITION",
            stop_reason="Could not resolve selected queue safely: {}".format(exc),
            result_status="failed",
            gate_name="queue_planner",
            gate_status="fail",
            gate_details={"policy": policy.name, "error": str(exc)},
            selected_task=None,
            policy_name=policy.name,
            queue_preview=None,
            side_effects=side_effects,
            root=root_path,
            actor=actor,
        )
    selected = queue_preview.next_task

    if selected is None:
        completed = _record_stop(
            selected_session_id,
            stop_code="BLOCKED",
            stop_reason="No executable task is available in the selected queue.",
            result_status="blocked",
            gate_name="queue_planner",
            gate_status="blocked",
            gate_details=_gate_details(policy.name, queue_preview, selected),
            selected_task=None,
            policy_name=policy.name,
            queue_preview=queue_preview,
            side_effects=side_effects,
            root=root_path,
            actor=actor,
        )
        if completed.ok:
            final = complete_session(
                selected_session_id,
                root=root_path,
                actor=actor,
                reason="queue_complete",
            )
            completed.data.setdefault("side_effects", []).append(final.to_dict())
            _merge_effects(completed, [final])
        return completed

    task_id = str(selected.id or "")
    if not task_id:
        return _record_stop(
            selected_session_id,
            stop_code="UNSAFE_CONDITION",
            stop_reason="Queue planner selected a task without a stable task id.",
            result_status="failed",
            gate_name="queue_planner",
            gate_status="fail",
            gate_details=_gate_details(policy.name, queue_preview, selected),
            selected_task=selected,
            policy_name=policy.name,
            queue_preview=queue_preview,
            side_effects=side_effects,
            root=root_path,
            actor=actor,
        )

    if policy.codex.mode == CodexExecutionMode.DISABLED:
        return _record_stop(
            selected_session_id,
            stop_code="BLOCKED",
            stop_reason="Codex execution is disabled by pipeline policy.",
            result_status="stopped",
            gate_name="codex_execution_policy",
            gate_status="skipped",
            gate_details=_gate_details(policy.name, queue_preview, selected),
            selected_task=selected,
            policy_name=policy.name,
            queue_preview=queue_preview,
            side_effects=side_effects,
            root=root_path,
            actor=actor,
        )

    change_check = _ensure_approved_change(
        task_id,
        policy,
        refs.get("evolution"),
        root=root_path,
        actor=actor,
        python_executable=python_bin,
        runner=execution_runner,
    )
    if not change_check.ok:
        change_check.data.setdefault("side_effects", [])
        return _record_stop(
            selected_session_id,
            stop_code=str(change_check.data.get("stop_code") or "BLOCKED"),
            stop_reason=change_check.message,
            result_status="blocked",
            gate_name="evolution_change_gate",
            gate_status="blocked",
            gate_details={
                **_gate_details(policy.name, queue_preview, selected),
                "change_gate": change_check.data,
            },
            selected_task=selected,
            policy_name=policy.name,
            queue_preview=queue_preview,
            side_effects=[*side_effects, change_check],
            root=root_path,
            actor=actor,
        )

    prepare = run_workflow(
        "task.prepare_for_codex",
        task_ref=task_id,
        root=root_path,
        actor=actor,
        confirmed=True,
        python_executable=python_bin,
        runner=execution_runner,
    )
    side_effects.append(prepare)
    if not prepare.ok:
        return _record_stop(
            selected_session_id,
            stop_code="BLOCKED",
            stop_reason="Task preparation workflow failed.",
            result_status="blocked",
            gate_name="task_prepare_for_codex",
            gate_status="blocked",
            gate_details={
                **_gate_details(policy.name, queue_preview, selected),
                "workflow": _workflow_summary(prepare),
            },
            selected_task=selected,
            policy_name=policy.name,
            queue_preview=queue_preview,
            side_effects=side_effects,
            root=root_path,
            actor=actor,
        )

    if policy.codex.mode == CodexExecutionMode.BUILD_PROMPT_ONLY:
        if policy.closure.auto_close_task:
            return _record_stop(
                selected_session_id,
                stop_code="NOT_IMPLEMENTED",
                stop_reason=(
                    "Auto-close requires Codex execution, Codex Report, "
                    "Machine Review, Codex Review and a close action."
                ),
                result_status="blocked",
                gate_name="review_close_gate",
                gate_status="blocked",
                gate_details={
                    **_gate_details(policy.name, queue_preview, selected),
                    "workflow": _workflow_summary(prepare),
                },
                selected_task=selected,
                policy_name=policy.name,
                queue_preview=queue_preview,
                side_effects=side_effects,
                root=root_path,
                actor=actor,
            )
        if policy.commit.create_local_commit:
            return _record_stop(
                selected_session_id,
                stop_code="NOT_IMPLEMENTED",
                stop_reason="Local commit readiness and commit action are not implemented yet.",
                result_status="blocked",
                gate_name="commit_gate",
                gate_status="blocked",
                gate_details={
                    **_gate_details(policy.name, queue_preview, selected),
                    "workflow": _workflow_summary(prepare),
                },
                selected_task=selected,
                policy_name=policy.name,
                queue_preview=queue_preview,
                side_effects=side_effects,
                root=root_path,
                actor=actor,
            )
        return _record_stop(
            selected_session_id,
            stop_code="BLOCKED",
            stop_reason="Codex prompt was built; policy stops before Codex execution.",
            result_status="passed",
            gate_name="codex_execution_policy",
            gate_status="skipped",
            gate_details={
                **_gate_details(policy.name, queue_preview, selected),
                "workflow": _workflow_summary(prepare),
            },
            selected_task=selected,
            policy_name=policy.name,
            queue_preview=queue_preview,
            side_effects=side_effects,
            root=root_path,
            actor=actor,
        )

    if policy.codex.mode == CodexExecutionMode.RUN_CODEX:
        token_gate = evaluate_token_budget(
            root=root_path,
            policy=policy.token_budget,
            strict=True,
        )
        token_gate_details = {
            **_gate_details(policy.name, queue_preview, selected),
            "workflow": _workflow_summary(prepare),
            "token_budget": token_gate.to_dict(),
            "codex_adapter_called": False,
        }
        if token_gate.status != TOKEN_BUDGET_PASS:
            return _record_stop(
                selected_session_id,
                stop_code="TOKEN_BUDGET_FAILURE",
                stop_reason="Token Budget Gate failed: {}".format(token_gate.reason),
                result_status="blocked",
                gate_name="token_budget_gate",
                gate_status=token_gate.status,
                gate_details=token_gate_details,
                selected_task=selected,
                policy_name=policy.name,
                queue_preview=queue_preview,
                side_effects=side_effects,
                root=root_path,
                actor=actor,
            )

        token_recorded = record_step_result(
            selected_session_id,
            RUN_NEXT_STEP,
            "passed",
            root=root_path,
            actor=actor,
            task_id=task_id,
            gate_name="token_budget_gate",
            gate_status=token_gate.status,
            gate_details=token_gate_details,
        )
        side_effects.append(token_recorded)
        if not token_recorded.ok:
            return _aggregate_failure(
                "pipeline.run_next",
                "Failed to record Token Budget Gate result.",
                selected_session_id,
                side_effects,
            )

        adapter = codex_adapter or run_codex_adapter
        adapter_result: CodexAdapterResult = adapter(
            root=root_path,
            task_id=task_id,
            policy=policy,
            token_gate=token_gate,
            runner=execution_runner,
        )
        adapter_details = {
            **_gate_details(policy.name, queue_preview, selected),
            "workflow": _workflow_summary(prepare),
            "token_budget": token_gate.to_dict(),
            "codex_adapter_called": True,
            "adapter": adapter_result.to_dict(),
        }
        if not adapter_result.ok:
            return _record_stop(
                selected_session_id,
                stop_code=_adapter_stop_code(adapter_result),
                stop_reason="Codex Execution Adapter stopped: {}".format(
                    adapter_result.reason
                ),
                result_status=_adapter_step_status(adapter_result),
                gate_name="codex_execution_adapter",
                gate_status=_adapter_gate_status(adapter_result),
                gate_details=adapter_details,
                selected_task=selected,
                policy_name=policy.name,
                queue_preview=queue_preview,
                side_effects=side_effects,
                root=root_path,
                actor=actor,
            )

        adapter_recorded = record_step_result(
            selected_session_id,
            RUN_NEXT_STEP,
            "passed",
            root=root_path,
            actor=actor,
            task_id=task_id,
            gate_name="codex_execution_adapter",
            gate_status="pass",
            gate_details=adapter_details,
            report_ids=(adapter_result.report_id,) if adapter_result.report_id else (),
        )
        side_effects.append(adapter_recorded)
        if not adapter_recorded.ok:
            return _aggregate_failure(
                "pipeline.run_next",
                "Failed to record Codex Execution Adapter result.",
                selected_session_id,
                side_effects,
            )

        report_gate = evaluate_report_gate(
            root=root_path,
            task=_task_by_id(tasks_state, task_id),
            policy=policy,
        )
        report_gate_details = {
            **adapter_details,
            "report_gate": report_gate.to_dict(),
            "report_id": report_gate.report_id or adapter_result.report_id,
        }
        if report_gate.status == REPORT_GATE_FAIL:
            return _record_stop(
                selected_session_id,
                stop_code="CODEX_REPORT_GATE_FAILURE",
                stop_reason="Codex Report Gate failed: {}".format(report_gate.reason),
                result_status="blocked",
                gate_name="codex_report_gate",
                gate_status=report_gate.status,
                gate_details=report_gate_details,
                selected_task=selected,
                policy_name=policy.name,
                queue_preview=queue_preview,
                side_effects=side_effects,
                root=root_path,
                actor=actor,
            )

        report_recorded = record_step_result(
            selected_session_id,
            RUN_NEXT_STEP,
            "passed",
            root=root_path,
            actor=actor,
            task_id=task_id,
            gate_name="codex_report_gate",
            gate_status=report_gate.status,
            gate_details=report_gate_details,
            report_ids=(report_gate.report_id,) if report_gate.report_id else (),
        )
        side_effects.append(report_recorded)
        if not report_recorded.ok:
            return _aggregate_failure(
                "pipeline.run_next",
                "Failed to record Codex Report Gate result.",
                selected_session_id,
                side_effects,
            )

        machine_review = evaluate_machine_review(
            root=root_path,
            task=_task_by_id(tasks_state, task_id),
            policy=policy,
            report_gate=report_gate,
            runner=execution_runner,
            python_executable=python_bin,
            run_report_declared_tests=True,
        )
        machine_review_details = {
            **report_gate_details,
            "machine_review": machine_review.to_dict(),
        }
        if machine_review.status == MACHINE_REVIEW_FAIL:
            return _record_stop(
                selected_session_id,
                stop_code="MACHINE_REVIEW_FAILURE",
                stop_reason="Machine Review Gate failed: {}".format(machine_review.reason),
                result_status="blocked",
                gate_name="machine_review_gate",
                gate_status=machine_review.status,
                gate_details=machine_review_details,
                selected_task=selected,
                policy_name=policy.name,
                queue_preview=queue_preview,
                side_effects=side_effects,
                root=root_path,
                actor=actor,
            )

        machine_review_recorded = record_step_result(
            selected_session_id,
            RUN_NEXT_STEP,
            "passed",
            root=root_path,
            actor=actor,
            task_id=task_id,
            gate_name="machine_review_gate",
            gate_status=machine_review.status,
            gate_details=machine_review_details,
            report_ids=(machine_review.report_id,) if machine_review.report_id else (),
        )
        side_effects.append(machine_review_recorded)
        if not machine_review_recorded.ok:
            return _aggregate_failure(
                "pipeline.run_next",
                "Failed to record Machine Review Gate result.",
                selected_session_id,
                side_effects,
            )

        codex_review = evaluate_codex_review(
            root=root_path,
            task=_task_by_id(tasks_state, task_id),
            report_gate=report_gate,
            machine_review=machine_review,
            reviewer=codex_reviewer,
        )
        codex_review_details = {
            **machine_review_details,
            "codex_review": codex_review.to_dict(),
        }
        if codex_review.status == CODEX_REVIEW_FAIL:
            return _record_stop(
                selected_session_id,
                stop_code="CODEX_REVIEW_GATE_FAILURE",
                stop_reason="Codex Review Gate failed: {}".format(codex_review.reason),
                result_status="blocked",
                gate_name="codex_review_gate",
                gate_status="fail",
                gate_details=codex_review_details,
                selected_task=selected,
                policy_name=policy.name,
                queue_preview=queue_preview,
                side_effects=side_effects,
                root=root_path,
                actor=actor,
                report_ids=(codex_review.report_id,) if codex_review.report_id else (),
                review_ids=(codex_review.review_id,) if codex_review.review_id else (),
            )
        if codex_review.status == CODEX_REVIEW_BLOCKED_STATUS:
            if codex_review.verdict == VERDICT_REQUEST_CHANGES:
                stop_code = "CODEX_REVIEW_REQUEST_CHANGES"
            elif codex_review.verdict == VERDICT_BLOCKED:
                stop_code = "CODEX_REVIEW_BLOCKED"
            else:
                stop_code = "CODEX_REVIEW_GATE_FAILURE"
            return _record_stop(
                selected_session_id,
                stop_code=stop_code,
                stop_reason=codex_review.reason,
                result_status="blocked",
                gate_name="codex_review_gate",
                gate_status="blocked",
                gate_details=codex_review_details,
                selected_task=selected,
                policy_name=policy.name,
                queue_preview=queue_preview,
                side_effects=side_effects,
                root=root_path,
                actor=actor,
                report_ids=(codex_review.report_id,) if codex_review.report_id else (),
                review_ids=(codex_review.review_id,) if codex_review.review_id else (),
            )

        codex_review_recorded = record_step_result(
            selected_session_id,
            RUN_NEXT_STEP,
            "passed",
            root=root_path,
            actor=actor,
            task_id=task_id,
            gate_name="codex_review_gate",
            gate_status=CODEX_REVIEW_PASS,
            gate_details=codex_review_details,
            report_ids=(codex_review.report_id,) if codex_review.report_id else (),
            review_ids=(codex_review.review_id,) if codex_review.review_id else (),
        )
        side_effects.append(codex_review_recorded)
        if not codex_review_recorded.ok:
            return _aggregate_failure(
                "pipeline.run_next",
                "Failed to record Codex Review Gate result.",
                selected_session_id,
                side_effects,
            )

        if policy.closure.auto_close_task:
            return _record_stop(
                selected_session_id,
                stop_code="NOT_IMPLEMENTED",
                stop_reason="Task auto-close action is not implemented in this task.",
                result_status="blocked",
                gate_name="review_close_gate",
                gate_status="blocked",
                gate_details=codex_review_details,
                selected_task=selected,
                policy_name=policy.name,
                queue_preview=queue_preview,
                side_effects=side_effects,
                root=root_path,
                actor=actor,
            )
        if policy.commit.create_local_commit:
            return _record_stop(
                selected_session_id,
                stop_code="NOT_IMPLEMENTED",
                stop_reason="Local commit readiness and commit action are not implemented yet.",
                result_status="blocked",
                gate_name="commit_gate",
                gate_status="blocked",
                gate_details=codex_review_details,
                selected_task=selected,
                policy_name=policy.name,
                queue_preview=queue_preview,
                side_effects=side_effects,
                root=root_path,
                actor=actor,
            )

        return _record_stop(
            selected_session_id,
            stop_code="BLOCKED",
            stop_reason="Codex Review Gate approved; policy stops before auto-close or commit.",
            result_status="passed",
            gate_name="pipeline_policy",
            gate_status="skipped",
            gate_details=codex_review_details,
            selected_task=selected,
            policy_name=policy.name,
            queue_preview=queue_preview,
            side_effects=side_effects,
            root=root_path,
            actor=actor,
        )

    return _record_stop(
        selected_session_id,
        stop_code="POLICY_VIOLATION",
        stop_reason="Unsupported Codex execution mode: {}".format(policy.codex.mode.value),
        result_status="failed",
        gate_name="codex_execution_policy",
        gate_status="fail",
        gate_details=_gate_details(policy.name, queue_preview, selected),
        selected_task=selected,
        policy_name=policy.name,
        queue_preview=queue_preview,
        side_effects=side_effects,
        root=root_path,
        actor=actor,
    )


def _resolve_session(root: Path, session_id: str) -> CommandResult:
    state = load_pipeline_state(root)
    sessions = [
        session
        for session in state.get("sessions", [])
        if isinstance(session, Mapping)
    ]
    selected_id = session_id or str(state.get("current_session_id") or "")
    if not selected_id:
        return CommandResult.failure(
            command="pipeline.run_next",
            domain="pipeline",
            message="No pipeline session selected.",
            errors=[
                CommandMessage(
                    "PIPELINE_NO_SESSION_SELECTED",
                    "Pass a session id or create a current pipeline session first.",
                    details={"state_path": str(pipeline_state_path(root))},
                )
            ],
        )
    for session in sessions:
        if session.get("id") == selected_id:
            return CommandResult.success(
                command="pipeline.run_next",
                domain="pipeline",
                message="Pipeline session loaded.",
                data={"session": dict(session)},
            )
    return CommandResult.failure(
        command="pipeline.run_next",
        domain="pipeline",
        message="Pipeline session not found.",
        errors=[
            CommandMessage(
                "PIPELINE_SESSION_NOT_FOUND",
                "pipeline session not found: {}".format(selected_id),
                details={"session_id": selected_id},
            )
        ],
    )


def _preview_session_queue(
    session: Mapping[str, Any],
    policy: PipelinePolicy,
    tasks_state: Mapping[str, Any],
    plan: Mapping[str, Any] | None,
) -> QueuePreview:
    queue = _mapping(session.get("selected_queue"), "selected_queue")
    request = QueuePlannerRequest(
        task_refs=_string_tuple(queue.get("task_refs")),
        epic_ids=_string_tuple(queue.get("epic_ids")),
        statuses=_string_tuple(queue.get("statuses")),
        max_tasks=_optional_int(queue.get("max_tasks")),
        order_by=str(queue.get("order_by") or "execution"),
    )
    return preview_queue(tasks_state, plan, policy=policy, request=request)


def _ensure_approved_change(
    task_id: str,
    policy: PipelinePolicy,
    evolution_state: Any,
    *,
    root: Path,
    actor: str,
    python_executable: str,
    runner: Runner | None,
) -> CommandResult:
    if not policy.evolution.require_approved_change_for_execution:
        return CommandResult.success(
            command="pipeline.change_gate",
            domain="pipeline",
            message="Approved Change gate is not required by policy.",
            data={"required": False},
        )

    linked = _linked_changes_for_task(task_id, evolution_state)
    approved = [
        change
        for change in linked
        if str(change.get("status") or "") in TERMINAL_CHANGE_STATUSES
    ]
    if approved:
        return CommandResult.success(
            command="pipeline.change_gate",
            domain="pipeline",
            message="Approved Change gate passed.",
            data={
                "required": True,
                "change_ids": [str(change.get("id")) for change in approved],
            },
        )

    if policy.evolution.create_missing_change:
        created = run_workflow(
            "evolution.create_for_task",
            task_ref=task_id,
            root=root,
            actor=actor,
            confirmed=True,
            python_executable=python_executable,
            runner=runner,
        )
        if created.ok:
            result = CommandResult.failure(
                command="pipeline.change_gate",
                domain="pipeline",
                message="Evolution Change was created and now requires Human Owner approval.",
                errors=[
                    CommandMessage(
                        "PIPELINE_CHANGE_APPROVAL_REQUIRED",
                        "Approve the created Change before Codex execution.",
                    )
                ],
            )
            result.data = {
                "required": True,
                "stop_code": "BLOCKED",
                "created_change_id": created.data.get("change_id", ""),
                "workflow": _workflow_summary(created),
            }
            result.changed_files.extend(created.changed_files)
            result.generated_files.extend(created.generated_files)
            result.events.extend(created.events)
            return result
        result = CommandResult.failure(
            command="pipeline.change_gate",
            domain="pipeline",
            message="Evolution Change creation workflow failed.",
            errors=list(created.errors)
            or [
                CommandMessage(
                    "PIPELINE_CHANGE_CREATE_FAILED",
                    "Could not create required Evolution Change.",
                )
            ],
        )
        result.data = {
            "required": True,
            "stop_code": "BLOCKED",
            "workflow": _workflow_summary(created),
        }
        return result

    result = CommandResult.failure(
        command="pipeline.change_gate",
        domain="pipeline",
        message="Approved linked Evolution Change is required before execution.",
        errors=[
            CommandMessage(
                "PIPELINE_APPROVED_CHANGE_REQUIRED",
                "Task {} has no linked approved Change.".format(task_id),
            )
        ],
    )
    result.data = {
        "required": True,
        "stop_code": "BLOCKED",
        "linked_change_ids": [str(change.get("id")) for change in linked],
    }
    return result


def _linked_changes_for_task(task_id: str, evolution_state: Any) -> list[Mapping[str, Any]]:
    if not isinstance(evolution_state, Mapping):
        return []
    linked: list[Mapping[str, Any]] = []
    for change in evolution_state.get("changes", []):
        if not isinstance(change, Mapping):
            continue
        linked_tasks = change.get("linked_tasks") or []
        if isinstance(linked_tasks, Sequence) and not isinstance(linked_tasks, (str, bytes)):
            if task_id in {str(item) for item in linked_tasks}:
                linked.append(change)
    return linked


def _record_stop(
    session_id: str,
    *,
    stop_code: str,
    stop_reason: str,
    result_status: str,
    gate_name: str,
    gate_status: str,
    gate_details: Mapping[str, Any],
    selected_task: QueuePreviewItem | None,
    policy_name: str,
    queue_preview: QueuePreview | None,
    side_effects: list[CommandResult],
    root: Path,
    actor: str,
    linked_change_ids: Sequence[str] = (),
    report_ids: Sequence[str] = (),
    review_ids: Sequence[str] = (),
    commit_ids: Sequence[str] = (),
) -> CommandResult:
    recorded = record_step_result(
        session_id,
        RUN_NEXT_STEP,
        result_status,
        root=root,
        actor=actor,
        task_id=str(selected_task.id or "") if selected_task else "",
        gate_name=gate_name,
        gate_status=gate_status,
        gate_details={
            **dict(gate_details),
            "stop_code": stop_code,
            "stop_reason": stop_reason,
        },
        stop_reason="{}: {}".format(stop_code, stop_reason),
        linked_change_ids=linked_change_ids,
        report_ids=report_ids,
        review_ids=review_ids,
        commit_ids=commit_ids,
    )
    side_effects.append(recorded)
    if not recorded.ok:
        return _aggregate_failure(
            "pipeline.run_next",
            "Failed to record pipeline run-next result.",
            session_id,
            side_effects,
        )
    return _safe_stop_result(
        session_id=session_id,
        stop_code=stop_code,
        stop_reason=stop_reason,
        selected_task=selected_task,
        policy_name=policy_name,
        queue_preview=queue_preview,
        side_effects=side_effects,
    )


def _safe_stop_result(
    *,
    session_id: str,
    stop_code: str,
    stop_reason: str,
    selected_task: QueuePreviewItem | None,
    policy_name: str,
    queue_preview: QueuePreview | None,
    side_effects: Sequence[CommandResult],
) -> CommandResult:
    result = CommandResult.success(
        command="pipeline.run_next",
        domain="pipeline",
        message="{}: {}".format(stop_code, stop_reason),
        data={
            "session_id": session_id,
            "stop_code": stop_code,
            "stop_reason": stop_reason,
            "policy": policy_name,
            "selected_task": selected_task.to_dict() if selected_task else None,
            "queue_counts": _queue_counts(queue_preview),
            "side_effects": [effect.to_dict() for effect in side_effects],
        },
    )
    _merge_effects(result, side_effects)
    if stop_code in {
        "NOT_IMPLEMENTED",
        "BLOCKED",
        "TOKEN_BUDGET_FAILURE",
        "CODEX_REPORT_GATE_FAILURE",
        "MACHINE_REVIEW_FAILURE",
        "CODEX_REVIEW_GATE_FAILURE",
        "CODEX_REVIEW_REQUEST_CHANGES",
        "CODEX_REVIEW_BLOCKED",
    }:
        result.owner_action_required = stop_reason
    return result


def _aggregate_failure(
    command: str,
    message: str,
    session_id: str,
    side_effects: Sequence[CommandResult],
) -> CommandResult:
    errors: list[CommandMessage] = []
    for effect in side_effects:
        errors.extend(effect.errors)
    result = CommandResult.failure(
        command=command,
        domain="pipeline",
        message=message,
        errors=errors
        or [
            CommandMessage(
                "PIPELINE_RUN_NEXT_FAILED",
                message,
                details={"session_id": session_id},
            )
        ],
    )
    result.data = {
        "session_id": session_id,
        "side_effects": [effect.to_dict() for effect in side_effects],
    }
    _merge_effects(result, side_effects)
    return result


def _merge_effects(target: CommandResult, effects: Sequence[CommandResult]) -> None:
    for effect in effects:
        _extend_unique(target.changed_files, effect.changed_files)
        _extend_unique(target.generated_files, effect.generated_files)
        _extend_unique(target.events, effect.events)
        target.warnings.extend(effect.warnings)


def _gate_details(
    policy_name: str,
    queue_preview: QueuePreview,
    selected_task: QueuePreviewItem | None,
) -> dict[str, Any]:
    return {
        "policy": policy_name,
        "selected_task": selected_task.to_dict() if selected_task else None,
        "queue_counts": _queue_counts(queue_preview),
    }


def _queue_counts(queue_preview: QueuePreview | None) -> dict[str, int]:
    if queue_preview is None:
        return {}
    return {
        "executable": len(queue_preview.executable),
        "waiting": len(queue_preview.waiting),
        "blocked": len(queue_preview.blocked),
        "skipped": len(queue_preview.skipped),
    }


def _workflow_summary(result: CommandResult) -> dict[str, Any]:
    steps = result.data.get("steps") if isinstance(result.data, Mapping) else []
    return {
        "ok": result.ok,
        "message": result.message,
        "steps": [
            {
                "id": str(step.get("id") or ""),
                "status": str(step.get("status") or ""),
            }
            for step in steps
            if isinstance(step, Mapping)
        ],
        "errors": [error.to_dict() for error in result.errors],
    }


def _load_plan(root: Path) -> Mapping[str, Any] | None:
    path = root / "AI_PROJECT" / "state" / "plan.json"
    if not path.exists():
        return None
    data = read_json_file(path, missing_code="PLAN_NOT_INITIALIZED")
    return data if isinstance(data, Mapping) else None


def _task_by_id(tasks_state: Mapping[str, Any], task_id: str) -> Mapping[str, Any]:
    for task in tasks_state.get("tasks", []):
        if isinstance(task, Mapping) and task.get("id") == task_id:
            return task
    return {"id": task_id}


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    raise TypeError("{} must be a mapping".format(name))


def _string_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    return tuple(str(item) for item in value if str(item).strip())


def _optional_int(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _policy_name(session: Mapping[str, Any]) -> str:
    snapshot = session.get("policy_snapshot")
    if isinstance(snapshot, Mapping):
        return str(snapshot.get("name") or "")
    return ""


def _adapter_gate_status(result: CodexAdapterResult) -> str:
    if result.status == "passed":
        return "pass"
    if result.status == "failed":
        return "fail"
    return "blocked"


def _adapter_step_status(result: CodexAdapterResult) -> str:
    return "failed" if result.status == "failed" else "blocked"


def _adapter_stop_code(result: CodexAdapterResult) -> str:
    return "UNSAFE_CONDITION" if result.status == "failed" else "BLOCKED"


def _extend_unique(target: list[str], values: Sequence[str]) -> None:
    seen = set(target)
    for value in values:
        text = str(value)
        if text and text not in seen:
            target.append(text)
            seen.add(text)

"""Supervised one-step pipeline runner.

The runner advances at most one pipeline step. It records every gate through
the governed pipeline session service and delegates lifecycle mutations to
existing workflow commands.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from ai_project_ctl.core.result import CommandMessage, CommandResult
from ai_project_ctl.core.store import read_json_file
from ai_project_ctl.core.workflows import Runner, run_workflow

from .close_policy import (
    CODE_TASK_AUTO_CLOSED,
    CODE_REVIEW_CLOSE_WORKFLOW_FAILED,
    decide_review_close,
    run_review_close_workflow,
)
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
from .git_commit import PASS as COMMIT_PASS
from .git_commit import run_local_commit
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
SESSION_APPROVAL_CHANGE_STATUSES = {"ready", "proposed"}
SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"


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

    queue_change_check = _ensure_approved_changes_for_queue(
        queue_preview,
        policy,
        refs.get("evolution"),
        session_id=selected_session_id,
        root=root_path,
        actor=actor,
        python_executable=python_bin,
        runner=execution_runner,
    )
    if not queue_change_check.ok:
        queue_change_check.data.setdefault("side_effects", [])
        return _record_stop(
            selected_session_id,
            stop_code=str(queue_change_check.data.get("stop_code") or "BLOCKED"),
            stop_reason=queue_change_check.message,
            result_status="blocked",
            gate_name="evolution_change_gate",
            gate_status="blocked",
            gate_details={
                **_gate_details(policy.name, queue_preview, queue_preview.next_task),
                "change_gate": queue_change_check.data,
            },
            selected_task=queue_preview.next_task,
            policy_name=policy.name,
            queue_preview=queue_preview,
            side_effects=[*side_effects, queue_change_check],
            root=root_path,
            actor=actor,
            linked_change_ids=_string_tuple(queue_change_check.data.get("change_ids")),
        )
    if queue_change_check.data.get("state_changed"):
        refs = load_reference_state(root_path)
    queue_change_gate = (
        dict(queue_change_check.data)
        if queue_change_check.data.get("required")
        else {}
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
            gate_details=_gate_details(
                policy.name,
                queue_preview,
                selected,
                change_gate=queue_change_gate,
            ),
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
            gate_details=_gate_details(
                policy.name,
                queue_preview,
                selected,
                change_gate=queue_change_gate,
            ),
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
            gate_details=_gate_details(
                policy.name,
                queue_preview,
                selected,
                change_gate=queue_change_gate,
            ),
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
                **_gate_details(
                    policy.name,
                    queue_preview,
                    selected,
                    change_gate=queue_change_gate,
                ),
                "change_gate": change_check.data,
            },
            selected_task=selected,
            policy_name=policy.name,
            queue_preview=queue_preview,
            side_effects=[*side_effects, change_check],
            root=root_path,
            actor=actor,
            linked_change_ids=_string_tuple(change_check.data.get("change_ids")),
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
                **_gate_details(
                    policy.name,
                    queue_preview,
                    selected,
                    change_gate=queue_change_gate,
                ),
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
                    **_gate_details(
                        policy.name,
                        queue_preview,
                        selected,
                        change_gate=queue_change_gate,
                    ),
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
                stop_code="COMMIT_READINESS_FAILED",
                stop_reason=(
                    "Local commit requires Codex execution, Machine Review PASS, "
                    "Codex Review APPROVE and a closed task."
                ),
                result_status="blocked",
                gate_name="commit_gate",
                gate_status="blocked",
                gate_details={
                    **_gate_details(
                        policy.name,
                        queue_preview,
                        selected,
                        change_gate=queue_change_gate,
                    ),
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
                **_gate_details(
                    policy.name,
                    queue_preview,
                    selected,
                    change_gate=queue_change_gate,
                ),
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
            **_gate_details(
                policy.name,
                queue_preview,
                selected,
                change_gate=queue_change_gate,
            ),
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
            **_gate_details(
                policy.name,
                queue_preview,
                selected,
                change_gate=queue_change_gate,
            ),
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
            if policy.closure.auto_close_task and codex_review.verdict == VERDICT_REQUEST_CHANGES:
                codex_review_recorded = record_step_result(
                    selected_session_id,
                    RUN_NEXT_STEP,
                    "passed",
                    root=root_path,
                    actor=actor,
                    task_id=task_id,
                    gate_name="codex_review_gate",
                    gate_status="blocked",
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
                return _apply_review_close_policy(
                    session=session,
                    policy=policy,
                    report_gate=report_gate,
                    machine_review=machine_review,
                    codex_review=codex_review,
                    gate_details=codex_review_details,
                    selected_session_id=selected_session_id,
                    selected=selected,
                    queue_preview=queue_preview,
                    side_effects=side_effects,
                    root=root_path,
                    actor=actor,
                    python_executable=python_bin,
                    runner=execution_runner,
                )

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
            close_result = _apply_review_close_policy(
                session=session,
                policy=policy,
                report_gate=report_gate,
                machine_review=machine_review,
                codex_review=codex_review,
                gate_details=codex_review_details,
                selected_session_id=selected_session_id,
                selected=selected,
                queue_preview=queue_preview,
                side_effects=side_effects,
                root=root_path,
                actor=actor,
                python_executable=python_bin,
                runner=execution_runner,
            )
            if (
                not policy.commit.create_local_commit
                or not close_result.ok
                or close_result.data.get("stop_code") != CODE_TASK_AUTO_CLOSED
            ):
                return close_result
            return _apply_local_commit_policy(
                policy=policy,
                report_gate=report_gate,
                machine_review=machine_review,
                codex_review=codex_review,
                gate_details=codex_review_details,
                selected_session_id=selected_session_id,
                selected=selected,
                queue_preview=queue_preview,
                side_effects=side_effects,
                root=root_path,
                actor=actor,
                runner=execution_runner,
            )
        if policy.commit.create_local_commit:
            return _apply_local_commit_policy(
                policy=policy,
                report_gate=report_gate,
                machine_review=machine_review,
                codex_review=codex_review,
                gate_details=codex_review_details,
                selected_session_id=selected_session_id,
                selected=selected,
                queue_preview=queue_preview,
                side_effects=side_effects,
                root=root_path,
                actor=actor,
                runner=execution_runner,
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
        gate_details=_gate_details(
            policy.name,
            queue_preview,
            selected,
            change_gate=queue_change_gate,
        ),
        selected_task=selected,
        policy_name=policy.name,
        queue_preview=queue_preview,
        side_effects=side_effects,
        root=root_path,
        actor=actor,
    )


def _apply_review_close_policy(
    *,
    session: Mapping[str, Any],
    policy: PipelinePolicy,
    report_gate,
    machine_review,
    codex_review,
    gate_details: Mapping[str, Any],
    selected_session_id: str,
    selected: QueuePreviewItem,
    queue_preview: QueuePreview,
    side_effects: list[CommandResult],
    root: Path,
    actor: str,
    python_executable: str,
    runner: Runner | None,
) -> CommandResult:
    decision = decide_review_close(
        policy=policy,
        report_gate=report_gate,
        machine_review=machine_review,
        codex_review=codex_review,
        session=session,
    )
    close_details: dict[str, Any] = {
        **dict(gate_details),
        "close_policy": decision.to_dict(),
    }

    workflow = run_review_close_workflow(
        decision,
        root=root,
        actor=actor,
        task_id=str(selected.id or ""),
        python_executable=python_executable,
        runner=runner,
    )
    if decision.should_run_workflow or not workflow.ok:
        side_effects.append(workflow)
        close_details["close_policy_workflow"] = workflow.to_dict()

    if not workflow.ok:
        return _record_stop(
            selected_session_id,
            stop_code=CODE_REVIEW_CLOSE_WORKFLOW_FAILED,
            stop_reason=workflow.message,
            result_status="blocked",
            gate_name="review_close_gate",
            gate_status="fail",
            gate_details=close_details,
            selected_task=selected,
            policy_name=policy.name,
            queue_preview=queue_preview,
            side_effects=side_effects,
            root=root,
            actor=actor,
            report_ids=(codex_review.report_id,) if codex_review.report_id else (),
            review_ids=(codex_review.review_id,) if codex_review.review_id else (),
        )

    return _record_stop(
        selected_session_id,
        stop_code=decision.stop_code,
        stop_reason=decision.reason,
        result_status=decision.result_status,
        gate_name="review_close_gate",
        gate_status=decision.gate_status,
        gate_details=close_details,
        selected_task=selected,
        policy_name=policy.name,
        queue_preview=queue_preview,
        side_effects=side_effects,
        root=root,
        actor=actor,
        report_ids=(codex_review.report_id,) if codex_review.report_id else (),
        review_ids=(codex_review.review_id,) if codex_review.review_id else (),
    )


def _apply_local_commit_policy(
    *,
    policy: PipelinePolicy,
    report_gate,
    machine_review,
    codex_review,
    gate_details: Mapping[str, Any],
    selected_session_id: str,
    selected: QueuePreviewItem,
    queue_preview: QueuePreview,
    side_effects: list[CommandResult],
    root: Path,
    actor: str,
    runner: Runner | None,
) -> CommandResult:
    commit_result = run_local_commit(
        root=root,
        task_id=str(selected.id or ""),
        session_id=selected_session_id,
        policy=policy,
        report_gate=report_gate,
        machine_review=machine_review,
        codex_review=codex_review,
        side_effects=side_effects,
        runner=runner,
    )
    commit_details = {
        **dict(gate_details),
        "commit": commit_result.to_dict(),
    }
    if commit_result.status == COMMIT_PASS:
        return _record_stop(
            selected_session_id,
            stop_code=commit_result.code,
            stop_reason=commit_result.reason,
            result_status="passed",
            gate_name="commit_gate",
            gate_status="pass",
            gate_details=commit_details,
            selected_task=selected,
            policy_name=policy.name,
            queue_preview=queue_preview,
            side_effects=side_effects,
            root=root,
            actor=actor,
            report_ids=(report_gate.report_id,) if report_gate.report_id else (),
            review_ids=(codex_review.review_id,) if codex_review.review_id else (),
            commit_ids=(commit_result.commit_hash,) if commit_result.commit_hash else (),
        )

    return _record_stop(
        selected_session_id,
        stop_code=commit_result.code,
        stop_reason=commit_result.reason,
        result_status="failed" if commit_result.status == "fail" else "blocked",
        gate_name="commit_gate",
        gate_status="fail" if commit_result.status == "fail" else "blocked",
        gate_details=commit_details,
        selected_task=selected,
        policy_name=policy.name,
        queue_preview=queue_preview,
        side_effects=side_effects,
        root=root,
        actor=actor,
        report_ids=(report_gate.report_id,) if report_gate.report_id else (),
        review_ids=(codex_review.review_id,) if codex_review.review_id else (),
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


def _ensure_approved_changes_for_queue(
    queue_preview: QueuePreview,
    policy: PipelinePolicy,
    evolution_state: Any,
    *,
    session_id: str,
    root: Path,
    actor: str,
    python_executable: str,
    runner: Runner | None,
) -> CommandResult:
    owner_approval_enabled = (
        policy.evolution.owner_approve_required_changes_for_session
    )
    approval_note = policy.evolution.owner_approval_note.strip()
    if not policy.evolution.create_missing_change and not owner_approval_enabled:
        return CommandResult.success(
            command="pipeline.change_gate",
            domain="pipeline",
            message="Queue-wide Change preflight is not enabled by policy.",
            data={"required": False},
        )
    if not policy.evolution.require_approved_change_for_execution:
        return CommandResult.success(
            command="pipeline.change_gate",
            domain="pipeline",
            message="Approved Change gate is not required by policy.",
            data={"required": False},
        )

    created_change_ids: list[str] = []
    linked_change_ids: list[str] = []
    tasks_requiring_approval: list[str] = []
    approval_candidates: list[dict[str, str]] = []
    unapprovable_changes: list[dict[str, str]] = []
    workflows: list[dict[str, Any]] = []
    effects: list[CommandResult] = []
    task_refs = _queue_task_ref_map(queue_preview)

    for task_id in _queue_task_ids(queue_preview):
        linked = _linked_changes_for_task(task_id, evolution_state)
        approved = [
            change
            for change in linked
            if str(change.get("status") or "") in TERMINAL_CHANGE_STATUSES
        ]
        if approved:
            _extend_unique(linked_change_ids, [str(change.get("id")) for change in approved])
            continue
        if linked:
            _extend_unique(linked_change_ids, [str(change.get("id")) for change in linked])
            tasks_requiring_approval.append(task_id)
            for change in linked:
                change_id = str(change.get("id") or "")
                status = str(change.get("status") or "")
                if status in SESSION_APPROVAL_CHANGE_STATUSES:
                    approval_candidates.append(
                        {
                            "change_id": change_id,
                            "task_id": task_id,
                            "task_ref": task_refs.get(task_id, task_id),
                            "status": status,
                        }
                    )
                else:
                    unapprovable_changes.append(
                        {
                            "change_id": change_id,
                            "task_id": task_id,
                            "task_ref": task_refs.get(task_id, task_id),
                            "status": status,
                        }
                    )
            continue

        if not policy.evolution.create_missing_change:
            tasks_requiring_approval.append(task_id)
            continue

        created = run_workflow(
            "evolution.create_for_task",
            task_ref=task_id,
            root=root,
            actor=actor,
            confirmed=True,
            python_executable=python_executable,
            runner=runner,
        )
        effects.append(created)
        workflows.append(_workflow_summary(created))
        if not created.ok:
            result = CommandResult.failure(
                command="pipeline.change_gate",
                domain="pipeline",
                message="Evolution Change creation workflow failed.",
                errors=list(created.errors)
                or [
                    CommandMessage(
                        "PIPELINE_CHANGE_CREATE_FAILED",
                        "Could not create required Evolution Change for task {}.".format(task_id),
                    )
                ],
            )
            result.data = {
                "required": True,
                "stop_code": "BLOCKED",
                "task_id": task_id,
                "workflows": workflows,
            }
            _merge_effects(result, effects)
            return result
        change_id = str(created.data.get("change_id") or "")
        if change_id:
            created_change_ids.append(change_id)
            linked_change_ids.append(change_id)
            approval_candidates.append(
                {
                    "change_id": change_id,
                    "task_id": task_id,
                    "task_ref": task_refs.get(task_id, task_id),
                    "status": "ready",
                }
            )
        tasks_requiring_approval.append(task_id)

    if created_change_ids or tasks_requiring_approval:
        if owner_approval_enabled and not approval_note:
            result = CommandResult.failure(
                command="pipeline.change_gate",
                domain="pipeline",
                message="Owner-approved session Change approval requires an approval note.",
                errors=[
                    CommandMessage(
                        "PIPELINE_OWNER_APPROVAL_NOTE_REQUIRED",
                        "Provide --approval-note when owner-approved Change approval is enabled.",
                    )
                ],
            )
            result.data = {
                "required": True,
                "stop_code": "BLOCKED",
                "created_change_ids": created_change_ids,
                "linked_change_ids": linked_change_ids,
                "change_ids": linked_change_ids,
                "tasks_requiring_approval": tasks_requiring_approval,
                "workflows": workflows,
            }
            _merge_effects(result, effects)
            return result
        if owner_approval_enabled and unapprovable_changes:
            result = CommandResult.failure(
                command="pipeline.change_gate",
                domain="pipeline",
                message="Some linked Evolution Changes are not ready for owner session approval.",
                errors=[
                    CommandMessage(
                        "PIPELINE_CHANGE_NOT_SESSION_APPROVABLE",
                        "Only ready or proposed linked Changes can be approved by the session approval policy.",
                    )
                ],
            )
            result.data = {
                "required": True,
                "stop_code": "BLOCKED",
                "created_change_ids": created_change_ids,
                "linked_change_ids": linked_change_ids,
                "change_ids": linked_change_ids,
                "tasks_requiring_approval": tasks_requiring_approval,
                "unapprovable_changes": unapprovable_changes,
                "workflows": workflows,
            }
            _merge_effects(result, effects)
            return result
        if owner_approval_enabled and approval_candidates:
            approvals = _approve_session_changes(
                approval_candidates,
                approval_note=approval_note,
                session_id=session_id,
                root=root,
                actor=actor,
                python_executable=python_executable,
                runner=runner,
            )
            effects.extend(approvals["effects"])
            workflows.extend(approvals["workflows"])
            if approvals["failed_result"] is not None:
                failed = approvals["failed_result"]
                failed.data.update(
                    {
                        "required": True,
                        "stop_code": "BLOCKED",
                        "created_change_ids": created_change_ids,
                        "linked_change_ids": linked_change_ids,
                        "change_ids": linked_change_ids,
                        "tasks_requiring_approval": tasks_requiring_approval,
                        "approved_change_ids": approvals["approved_change_ids"],
                        "approved_task_refs": approvals["approved_task_refs"],
                        "workflows": workflows,
                    }
                )
                _merge_effects(failed, effects)
                return failed
            approved_change_ids = approvals["approved_change_ids"]
            result = CommandResult.success(
                command="pipeline.change_gate",
                domain="pipeline",
                message="Owner-approved session Change approval completed for selected queue.",
                data={
                    "required": True,
                    "created_change_ids": created_change_ids,
                    "linked_change_ids": linked_change_ids,
                    "change_ids": linked_change_ids,
                    "tasks_requiring_approval": tasks_requiring_approval,
                    "approved_change_ids": approved_change_ids,
                    "approved_task_refs": approvals["approved_task_refs"],
                    "owner_approval": {
                        "actor": actor,
                        "approval_note": approval_note,
                        "session_id": session_id,
                    },
                    "workflows": workflows,
                    "state_changed": bool(created_change_ids or approved_change_ids),
                },
            )
            _merge_effects(result, effects)
            return result
        message = (
            "Evolution Changes were created and now require Human Owner approval."
            if created_change_ids
            else "Approved linked Evolution Changes are required before execution."
        )
        result = CommandResult.failure(
            command="pipeline.change_gate",
            domain="pipeline",
            message=message,
            errors=[
                CommandMessage(
                    "PIPELINE_CHANGE_APPROVAL_REQUIRED",
                    "Approve linked Changes before Codex execution.",
                )
            ],
        )
        result.data = {
            "required": True,
            "stop_code": "BLOCKED",
            "created_change_ids": created_change_ids,
            "linked_change_ids": linked_change_ids,
            "change_ids": linked_change_ids,
            "tasks_requiring_approval": tasks_requiring_approval,
            "workflows": workflows,
        }
        _merge_effects(result, effects)
        return result

    return CommandResult.success(
        command="pipeline.change_gate",
        domain="pipeline",
        message="Approved Change gate passed for selected queue.",
        data={
            "required": True,
            "change_ids": linked_change_ids,
        },
    )


def _approve_session_changes(
    approval_candidates: Sequence[Mapping[str, str]],
    *,
    approval_note: str,
    session_id: str,
    root: Path,
    actor: str,
    python_executable: str,
    runner: Runner | None,
) -> dict[str, Any]:
    effects: list[CommandResult] = []
    workflows: list[dict[str, Any]] = []
    approved_change_ids: list[str] = []
    approved_task_refs: list[str] = []
    failed_result: CommandResult | None = None

    seen_changes: set[str] = set()
    for candidate in approval_candidates:
        change_id = str(candidate.get("change_id") or "")
        if not change_id or change_id in seen_changes:
            continue
        seen_changes.add(change_id)
        status = str(candidate.get("status") or "")
        task_ref = str(candidate.get("task_ref") or candidate.get("task_id") or "")

        if status == "proposed":
            for target_status in ("draft", "ready"):
                transition = _run_change_transition(
                    change_id,
                    target_status,
                    root=root,
                    actor=actor,
                    python_executable=python_executable,
                    runner=runner,
                )
                effects.append(transition)
                workflows.append(_workflow_summary(transition))
                if not transition.ok:
                    failed_result = CommandResult.failure(
                        command="pipeline.change_gate",
                        domain="pipeline",
                        message="Evolution Change preparation for approval failed.",
                        errors=list(transition.errors)
                        or [
                            CommandMessage(
                                "PIPELINE_CHANGE_PREPARE_FAILED",
                                "Could not move Change {} to {}.".format(
                                    change_id,
                                    target_status,
                                ),
                            )
                        ],
                    )
                    return {
                        "effects": effects,
                        "workflows": workflows,
                        "approved_change_ids": approved_change_ids,
                        "approved_task_refs": approved_task_refs,
                        "failed_result": failed_result,
                    }

        approve = run_workflow(
            "evolution.approve_change",
            change_ref=change_id,
            notes="{} (pipeline session {})".format(approval_note, session_id),
            root=root,
            actor=actor,
            confirmed=True,
            python_executable=python_executable,
            runner=runner,
        )
        effects.append(approve)
        workflows.append(_workflow_summary(approve))
        if not approve.ok:
            failed_result = CommandResult.failure(
                command="pipeline.change_gate",
                domain="pipeline",
                message="Owner-approved session Change approval workflow failed.",
                errors=list(approve.errors)
                or [
                    CommandMessage(
                        "PIPELINE_CHANGE_APPROVAL_FAILED",
                        "Could not approve Change {}.".format(change_id),
                    )
                ],
            )
            return {
                "effects": effects,
                "workflows": workflows,
                "approved_change_ids": approved_change_ids,
                "approved_task_refs": approved_task_refs,
                "failed_result": failed_result,
            }
        approved_change_ids.append(change_id)
        if task_ref:
            approved_task_refs.append(task_ref)

    return {
        "effects": effects,
        "workflows": workflows,
        "approved_change_ids": approved_change_ids,
        "approved_task_refs": approved_task_refs,
        "failed_result": failed_result,
    }


def _run_change_transition(
    change_id: str,
    target_status: str,
    *,
    root: Path,
    actor: str,
    python_executable: str,
    runner: Runner | None,
) -> CommandResult:
    argv = (
        python_executable,
        str(SCRIPTS_DIR / "evolutionctl.py"),
        "--root",
        str(root),
        "--actor",
        actor,
        "change",
        "transition",
        change_id,
        "--to",
        target_status,
    )
    executor = runner or _run_subprocess
    completed = executor(argv)
    if completed.returncode == 0:
        return CommandResult.success(
            command="evolutionctl.change.transition",
            domain="evolution",
            message=completed.stdout.strip() or "OK",
            data={
                "change_id": change_id,
                "status": target_status,
            },
        )
    return CommandResult.failure(
        command="evolutionctl.change.transition",
        domain="evolution",
        message="Evolution Change transition failed.",
        errors=[
            CommandMessage(
                "PIPELINE_CHANGE_TRANSITION_FAILED",
                "Could not move Change {} to {}.".format(change_id, target_status),
                details={
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                },
            )
        ],
    )


def _run_subprocess(argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(argv),
        cwd=str(SCRIPTS_DIR.parent),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


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


def _queue_task_ids(queue_preview: QueuePreview) -> tuple[str, ...]:
    task_ids: list[str] = []
    for item in (
        *queue_preview.executable,
        *queue_preview.waiting,
        *queue_preview.blocked,
    ):
        task_id = str(item.id or "")
        if task_id and task_id not in task_ids:
            task_ids.append(task_id)
    if not task_ids and queue_preview.next_task and queue_preview.next_task.id:
        task_ids.append(str(queue_preview.next_task.id))
    return tuple(task_ids)


def _queue_task_ref_map(queue_preview: QueuePreview) -> dict[str, str]:
    task_refs: dict[str, str] = {}
    for item in (
        *queue_preview.executable,
        *queue_preview.waiting,
        *queue_preview.blocked,
    ):
        task_id = str(item.id or "")
        if task_id:
            task_refs[task_id] = str(item.ref or item.selected_ref or task_id)
    if queue_preview.next_task and queue_preview.next_task.id:
        task_id = str(queue_preview.next_task.id)
        task_refs.setdefault(
            task_id,
            str(queue_preview.next_task.ref or queue_preview.next_task.selected_ref or task_id),
        )
    return task_refs


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
        "REVIEW_CLOSE_POLICY_BLOCKED",
        "REVIEW_CLOSE_WORKFLOW_FAILED",
        "REWORK_LIMIT_REACHED",
        "REWORK_POLICY_DISABLED",
        "COMMIT_READINESS_FAILED",
        "COMMIT_GIT_COMMAND_FAILED",
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
    *,
    change_gate: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    data = {
        "policy": policy_name,
        "selected_task": selected_task.to_dict() if selected_task else None,
        "queue_counts": _queue_counts(queue_preview),
    }
    if change_gate:
        data["change_gate"] = dict(change_gate)
    return data


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
    steps = steps or []
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

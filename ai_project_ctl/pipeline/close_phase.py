"""Pipeline close phase service.

The close phase validates phase history, then uses governed workflows to approve
and mark the reviewed task done before optionally accepting linked Evolution
Changes and creating a local-only commit when policy and readiness allow it.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

from ai_project_ctl.core.result import CommandMessage, CommandResult
from ai_project_ctl.core.workflows import run_workflow

from .artifact_bounds import bound_pipeline_artifact
from .close_policy import (
    ACTION_CLOSE_TASK,
    CODE_TASK_AUTO_CLOSED,
    ReviewCloseDecision,
    run_review_close_workflow,
)
from .codex_review import VERDICT_APPROVE, CodexReviewFinding, CodexReviewResult
from .git_commit import (
    BLOCKED as COMMIT_BLOCKED,
    FAIL as COMMIT_FAIL,
    PASS as COMMIT_PASS,
    CODE_DISABLED as COMMIT_DISABLED,
    CODE_POLICY_INVALID as COMMIT_POLICY_INVALID,
    LocalCommitResult,
    run_local_commit,
)
from .machine_review import evaluate_machine_review
from .phase import PhaseResult
from .policy import PipelinePolicy, disables_codex_review_by_policy
from .report_gate import evaluate_report_gate
from .session import record_phase_result
from .state import load_pipeline_state, load_reference_state, pipeline_state_path


COMMAND_NAME = "pipeline.phase.close"
PHASE_NAME = "close"
CONTEXT_REFRESH_COMMAND = "pipeline.close.context_refresh"
CONTEXT_REFRESH_FAILED = "CLOSE_CONTEXT_REFRESH_FAILED"
CONTEXT_REFRESH_GENERATED_FILES = (
    "AI_PROJECT/generated/CONTEXT_PACK.md",
    "AI_PROJECT/generated/CONTEXT_STATUS.md",
)
CONTEXT_REFRESH_EVENT_FILE = "AI_PROJECT/events/context-events.jsonl"
CONTEXT_REFRESH_OUTPUT_LIMIT = 1200
REQUIRED_PASSED_PHASES = ("prepare", "execute", "collect_report", "verify")
REVIEW_PHASE_NAME = "review"
REQUIRED_PHASE_ORDER = (*REQUIRED_PASSED_PHASES, REVIEW_PHASE_NAME)
CHANGE_ACCEPTABLE_STATUSES = {"approved", "in_review"}
CHANGE_ALREADY_ACCEPTED_STATUS = "accepted"
CODEX_CLEAR_STEP_ID = "codex_clear"
SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"


def close_phase(
    session_id: str = "",
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    confirmed: bool = False,
) -> CommandResult:
    """Close reviewed task work after required pipeline gates pass."""

    if not confirmed:
        return _failure(
            "PIPELINE_CLOSE_CONFIRM_REQUIRED",
            "Close preflight requires --confirm.",
            details={
                "next_action": (
                    "Rerun with --confirm after verifying that close preflight "
                    "is intended."
                )
            },
        )

    root_path = Path(root).resolve()
    session_result = _resolve_session(root_path, session_id)
    if not session_result.ok:
        return session_result

    session = session_result.data["session"]
    selected_session_id = str(session.get("id") or "")
    task_id = str(session.get("current_task_id") or "").strip()
    task_ref = str(session.get("current_task_ref") or "").strip()
    if not task_id:
        return _blocked(
            "SESSION_TASK_MISSING",
            "Pipeline session does not have a current task.",
            session_id=selected_session_id,
            root=root_path,
            actor=actor,
            artifacts={"session_id": selected_session_id},
            next_action="Run pipeline phase prepare or recreate the session with a task.",
        )

    evidence = _preflight_evidence(session, task_id)
    if evidence["missing_gates"]:
        phase = PhaseResult.blocked(
            PHASE_NAME,
            reason="Close preflight blocked: required phase evidence is incomplete.",
            next_action=_blocked_next_action(evidence["missing_gates"]),
            artifacts={
                "blocked_by": "CLOSE_PREFLIGHT_INCOMPLETE",
                "session_id": selected_session_id,
                "task_id": task_id,
                "task_ref": task_ref,
                **evidence,
            },
        )
        return _phase_command(
            phase,
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
        )

    close_policy = _close_policy(session)
    if not close_policy["auto_close_task"]:
        phase = PhaseResult.blocked(
            PHASE_NAME,
            reason="Close blocked: pipeline policy does not allow task auto-close.",
            next_action=(
                "Use an owner-approved close workflow manually or recreate the "
                "session with a policy that enables task auto-close."
            ),
            artifacts={
                "blocked_by": "CLOSE_POLICY_DISABLED",
                "session_id": selected_session_id,
                "task_id": task_id,
                "task_ref": task_ref,
                "close_policy": _safe_close_policy(close_policy),
                **evidence,
            },
        )
        return _phase_command(
            phase,
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
        )

    approval_notes = close_policy["owner_approval_note"]
    if not approval_notes:
        phase = PhaseResult.blocked(
            PHASE_NAME,
            reason="Close blocked: task closure requires owner approval notes.",
            next_action=(
                "Recreate or update the pipeline session with an explicit "
                "auto-close owner note before rerunning close."
            ),
            artifacts={
                "blocked_by": "CLOSE_OWNER_NOTES_REQUIRED",
                "session_id": selected_session_id,
                "task_id": task_id,
                "task_ref": task_ref,
                "close_policy": {
                    **close_policy,
                    "owner_approval_note": "",
                    "owner_approval_note_present": False,
                },
                **evidence,
            },
        )
        return _phase_command(
            phase,
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
        )

    workflow = _run_close_workflow(
        session=session,
        session_id=selected_session_id,
        task_id=task_id,
        task_ref=task_ref,
        evidence=evidence,
        close_policy=close_policy,
        approval_notes=approval_notes,
        root=root_path,
        actor=actor,
    )
    if not workflow.ok:
        phase = PhaseResult.blocked(
            PHASE_NAME,
            reason="Close workflow blocked: {}".format(workflow.message),
            next_action="Resolve the close workflow blocker, then rerun pipeline close.",
            artifacts={
                "blocked_by": "CLOSE_WORKFLOW_BLOCKED",
                "session_id": selected_session_id,
                "task_id": task_id,
                "task_ref": task_ref,
                "close_policy": _safe_close_policy(close_policy),
                "close_workflow": workflow.to_dict(),
                **_close_recovery_artifacts(workflow),
                "codex_execution_cleanup": _codex_execution_cleanup_report(
                    workflow,
                    task_id,
                ),
                **evidence,
            },
            changed_files=workflow.changed_files,
            generated_files=workflow.generated_files,
            events=workflow.events,
        )
        result = _phase_command(
            phase,
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
        )
        _merge_command_effects(result, (workflow,))
        return result

    change_acceptance, acceptance_results = _accept_linked_changes_after_close(
        session=session,
        task_id=task_id,
        task_ref=task_ref,
        close_policy=close_policy,
        approval_notes=approval_notes,
        root=root_path,
        actor=actor,
    )
    side_effects: list[CommandResult] = [workflow, *acceptance_results]
    local_commit = _local_commit_skipped(session, task_id)
    phase_artifacts = {
        "session_id": selected_session_id,
        "task_id": task_id,
        "task_ref": task_ref,
        "preflight_passed": True,
        "close_policy": _safe_close_policy(close_policy),
        "close_workflow": workflow.to_dict(),
        **_close_recovery_artifacts(workflow),
        "codex_execution_cleanup": _codex_execution_cleanup_report(
            workflow,
            task_id,
        ),
        "change_acceptance": change_acceptance,
        "accepted_change_ids": list(change_acceptance["accepted_change_ids"]),
        "local_commit": local_commit.to_dict(),
        **evidence,
    }
    if change_acceptance["status"] == "blocked":
        phase = PhaseResult.blocked(
            PHASE_NAME,
            reason=(
                "Close completed, but linked Evolution Change acceptance was blocked."
            ),
            next_action=(
                "Resolve linked Evolution Change blockers, then rerun pipeline close."
            ),
            artifacts={
                "blocked_by": "LINKED_CHANGE_ACCEPTANCE_BLOCKED",
                **phase_artifacts,
            },
            changed_files=workflow.changed_files,
            generated_files=workflow.generated_files,
            events=workflow.events,
        )
    else:
        context_refresh = _refresh_context_after_close(
            task_id=task_id,
            root=root_path,
            actor=actor,
        )
        side_effects.append(context_refresh)
        phase_artifacts["context_refresh"] = context_refresh.to_dict()
        if not context_refresh.ok:
            phase = PhaseResult.blocked(
                PHASE_NAME,
                reason=(
                    "Close completed, but context refresh was blocked: {}".format(
                        context_refresh.message
                    )
                ),
                next_action=(
                    "Resolve the context refresh blocker, then rerun pipeline close."
                ),
                artifacts={
                    "blocked_by": CONTEXT_REFRESH_FAILED,
                    **phase_artifacts,
                },
                changed_files=_side_effect_changed_files(side_effects),
                generated_files=_side_effect_generated_files(side_effects),
                events=_side_effect_events(side_effects),
            )
        elif _commit_policy_enabled(session):
            local_commit = _run_local_commit_after_close(
                session=session,
                session_id=selected_session_id,
                task_id=task_id,
                root=root_path,
                side_effects=tuple(side_effects),
            )
            phase_artifacts["local_commit"] = local_commit.to_dict()
            if local_commit.commit_hash:
                phase_artifacts["commit_hash"] = local_commit.commit_hash

        if context_refresh.ok and local_commit.status == COMMIT_FAIL:
            phase = PhaseResult.failed(
                PHASE_NAME,
                reason="Close completed, but local commit failed: {}".format(
                    local_commit.reason
                ),
                next_action=(
                    "Resolve the local commit failure, then rerun pipeline close."
                ),
                artifacts={
                    "error_code": local_commit.code,
                    **phase_artifacts,
                },
                changed_files=workflow.changed_files,
                generated_files=workflow.generated_files,
                events=workflow.events,
            )
        elif context_refresh.ok and local_commit.status == COMMIT_BLOCKED:
            phase = PhaseResult.blocked(
                PHASE_NAME,
                reason="Close completed, but local commit was blocked: {}".format(
                    local_commit.reason
                ),
                next_action=(
                    "Resolve local commit readiness blockers, then rerun "
                    "pipeline close."
                ),
                artifacts={
                    "blocked_by": local_commit.code,
                    **phase_artifacts,
                },
                changed_files=workflow.changed_files,
                generated_files=workflow.generated_files,
                events=workflow.events,
            )
        elif context_refresh.ok:
            phase = PhaseResult.passed(
                PHASE_NAME,
                reason=_close_success_reason(
                    change_acceptance,
                    local_commit,
                    already_closed=bool(
                        phase_artifacts.get("already_closed_by_previous_attempt")
                    ),
                ),
                next_action=_close_success_next_action(change_acceptance, local_commit),
                artifacts=phase_artifacts,
                changed_files=workflow.changed_files,
                generated_files=workflow.generated_files,
                events=workflow.events,
            )
    result = _phase_command(
        phase,
        session_id=selected_session_id,
        task_id=task_id,
        root=root_path,
        actor=actor,
    )
    _merge_command_effects(result, tuple(side_effects))
    return result


def _accept_linked_changes_after_close(
    *,
    session: Mapping[str, Any],
    task_id: str,
    task_ref: str,
    close_policy: Mapping[str, Any],
    approval_notes: str,
    root: Path,
    actor: str,
) -> tuple[dict[str, Any], tuple[CommandResult, ...]]:
    linked = _linked_changes_for_task(session, task_id, task_ref, root)
    outcomes: list[dict[str, Any]] = []
    workflow_results: list[CommandResult] = []
    accepted_change_ids: list[str] = []

    if not linked["linked_change_ids"]:
        return (
            _change_acceptance_report(
                status="skipped",
                reason="No linked Evolution Changes were found for the closed task.",
                policy=close_policy,
                linked=linked,
                outcomes=outcomes,
                accepted_change_ids=accepted_change_ids,
            ),
            (),
        )

    if not close_policy["auto_accept_linked_changes"]:
        for change in linked["changes"]:
            outcomes.append(
                _change_outcome(
                    change,
                    "skipped",
                    "CHANGE_ACCEPTANCE_POLICY_DISABLED",
                    "Linked Change acceptance is disabled by close policy.",
                )
            )
        for change_id in linked["missing_change_ids"]:
            outcomes.append(
                {
                    "change_id": change_id,
                    "status": "skipped",
                    "code": "LINKED_CHANGE_NOT_FOUND",
                    "reason": "Linked Change was not found in evolution state.",
                }
            )
        return (
            _change_acceptance_report(
                status="skipped",
                reason="Linked Change acceptance is disabled by close policy.",
                policy=close_policy,
                linked=linked,
                outcomes=outcomes,
                accepted_change_ids=accepted_change_ids,
            ),
            (),
        )

    if not approval_notes.strip():
        outcomes.extend(
            _blocked_outcomes_for_linked_changes(
                linked,
                "CHANGE_ACCEPTANCE_NOTES_REQUIRED",
                "Linked Change acceptance requires owner approval notes.",
            )
        )
        return (
            _change_acceptance_report(
                status="blocked",
                reason="Linked Change acceptance requires owner approval notes.",
                policy=close_policy,
                linked=linked,
                outcomes=outcomes,
                accepted_change_ids=accepted_change_ids,
            ),
            (),
        )

    for change_id in linked["missing_change_ids"]:
        outcomes.append(
            {
                "change_id": change_id,
                "status": "blocked",
                "code": "LINKED_CHANGE_NOT_FOUND",
                "reason": "Linked Change was not found in evolution state.",
            }
        )

    for change in linked["changes"]:
        if not change["linked_to_selected_task"]:
            outcomes.append(
                _change_outcome(
                    change,
                    "blocked",
                    "CHANGE_NOT_LINKED_TO_SELECTED_TASK",
                    "Linked Change does not reference the selected closed task.",
                )
            )
            continue

        status = str(change.get("status") or "")
        if status == CHANGE_ALREADY_ACCEPTED_STATUS:
            accepted_change_ids.append(str(change.get("id") or ""))
            outcomes.append(
                _change_outcome(
                    change,
                    "skipped",
                    "CHANGE_ALREADY_ACCEPTED",
                    "Linked Change is already accepted.",
                )
            )
            continue

        if status not in CHANGE_ACCEPTABLE_STATUSES:
            outcomes.append(
                _change_outcome(
                    change,
                    "blocked",
                    "CHANGE_NOT_ACCEPTABLE",
                    "Linked Change status is not acceptable for acceptance.",
                    allowed_statuses=sorted(CHANGE_ACCEPTABLE_STATUSES),
                )
            )
            continue

        workflow = run_workflow(
            "evolution.accept_change",
            change_ref=str(change.get("id") or ""),
            notes=_change_acceptance_notes(approval_notes, task_id, task_ref),
            root=root,
            actor=actor,
            confirmed=True,
            python_executable=sys.executable,
            runner=None,
        )
        workflow_results.append(workflow)
        if workflow.ok:
            accepted_change_ids.append(str(change.get("id") or ""))
            outcomes.append(
                _change_outcome(
                    change,
                    "accepted",
                    "CHANGE_ACCEPTED",
                    "Linked Change accepted after task close succeeded.",
                    workflow=workflow.to_dict(),
                )
            )
        else:
            outcomes.append(
                _change_outcome(
                    change,
                    "blocked",
                    "CHANGE_ACCEPT_WORKFLOW_BLOCKED",
                    workflow.message,
                    workflow=workflow.to_dict(),
                )
            )

    blocked = [item for item in outcomes if item.get("status") == "blocked"]
    accepted = [item for item in outcomes if item.get("status") == "accepted"]
    final_status = "blocked" if blocked else ("accepted" if accepted else "skipped")
    reason = (
        "One or more linked Evolution Changes could not be accepted."
        if blocked
        else (
            "Linked Evolution Changes were accepted."
            if accepted
            else "No linked Evolution Changes needed acceptance."
        )
    )
    return (
        _change_acceptance_report(
            status=final_status,
            reason=reason,
            policy=close_policy,
            linked=linked,
            outcomes=outcomes,
            accepted_change_ids=accepted_change_ids,
        ),
        tuple(workflow_results),
    )


def _linked_changes_for_task(
    session: Mapping[str, Any],
    task_id: str,
    task_ref: str,
    root: Path,
) -> dict[str, Any]:
    refs = load_reference_state(root)
    evolution = _mapping(refs.get("evolution"))
    changes = [
        change
        for change in evolution.get("changes", [])
        if isinstance(change, Mapping)
    ]
    by_id = {
        str(change.get("id") or ""): change
        for change in changes
        if str(change.get("id") or "")
    }
    task_refs = _task_reference_values(refs.get("tasks"), task_id, task_ref)
    session_change_ids = _string_list(session.get("linked_change_ids"))
    task_change_ids = [
        str(change.get("id") or "")
        for change in changes
        if _change_links_task(change, task_refs) and str(change.get("id") or "")
    ]
    linked_change_ids = _unique_strings([*session_change_ids, *task_change_ids])

    resolved: list[dict[str, Any]] = []
    missing: list[str] = []
    for change_id in linked_change_ids:
        change = by_id.get(change_id)
        if change is None:
            missing.append(change_id)
            continue
        linked_tasks = _string_list(change.get("linked_tasks"))
        resolved.append(
            {
                "id": change_id,
                "status": str(change.get("status") or ""),
                "linked_tasks": linked_tasks,
                "linked_to_selected_task": bool(set(linked_tasks) & set(task_refs)),
            }
        )

    return {
        "task_refs": task_refs,
        "session_linked_change_ids": session_change_ids,
        "task_linked_change_ids": task_change_ids,
        "linked_change_ids": linked_change_ids,
        "missing_change_ids": missing,
        "changes": resolved,
    }


def _task_reference_values(
    tasks_state: Any,
    task_id: str,
    task_ref: str,
) -> list[str]:
    refs = _unique_strings([task_id, task_ref])
    tasks = []
    if isinstance(tasks_state, Mapping) and isinstance(tasks_state.get("tasks"), list):
        tasks = tasks_state.get("tasks") or []

    for task in tasks:
        if not isinstance(task, Mapping):
            continue
        candidates = _task_ref_candidates(task)
        if task_id in candidates or (task_ref and task_ref in candidates):
            return _unique_strings([*refs, *candidates])
    return refs


def _task_ref_candidates(task: Mapping[str, Any]) -> list[str]:
    candidates = [
        str(task.get("id") or ""),
        str(task.get("ref") or ""),
        str(task.get("uid") or ""),
        str(task.get("legacy_id") or ""),
    ]
    candidates.extend(_string_list(task.get("aliases")))
    return _unique_strings(candidates)


def _change_links_task(change: Mapping[str, Any], task_refs: list[str]) -> bool:
    linked_tasks = set(_string_list(change.get("linked_tasks")))
    return bool(linked_tasks & set(task_refs))


def _change_acceptance_report(
    *,
    status: str,
    reason: str,
    policy: Mapping[str, Any],
    linked: Mapping[str, Any],
    outcomes: list[dict[str, Any]],
    accepted_change_ids: list[str],
) -> dict[str, Any]:
    newly_accepted = [
        str(outcome.get("change_id") or "")
        for outcome in outcomes
        if outcome.get("status") == "accepted" and outcome.get("change_id")
    ]
    return {
        "status": status,
        "reason": reason,
        "policy": _safe_close_policy(policy),
        "task_refs": list(linked.get("task_refs") or []),
        "linked_change_ids": list(linked.get("linked_change_ids") or []),
        "missing_change_ids": list(linked.get("missing_change_ids") or []),
        "accepted_change_ids": _unique_strings(accepted_change_ids),
        "newly_accepted_change_ids": _unique_strings(newly_accepted),
        "outcomes": outcomes,
    }


def _change_outcome(
    change: Mapping[str, Any],
    status: str,
    code: str,
    reason: str,
    **details: Any,
) -> dict[str, Any]:
    outcome: dict[str, Any] = {
        "change_id": str(change.get("id") or ""),
        "change_status": str(change.get("status") or ""),
        "status": status,
        "code": code,
        "reason": reason,
        "linked_tasks": _string_list(change.get("linked_tasks")),
        "linked_to_selected_task": bool(change.get("linked_to_selected_task")),
    }
    outcome.update(details)
    return outcome


def _blocked_outcomes_for_linked_changes(
    linked: Mapping[str, Any],
    code: str,
    reason: str,
) -> list[dict[str, Any]]:
    outcomes = [
        _change_outcome(change, "blocked", code, reason)
        for change in linked.get("changes") or []
        if isinstance(change, Mapping)
    ]
    for change_id in linked.get("missing_change_ids") or []:
        outcomes.append(
            {
                "change_id": str(change_id),
                "status": "blocked",
                "code": "LINKED_CHANGE_NOT_FOUND",
                "reason": "Linked Change was not found in evolution state.",
            }
        )
    return outcomes


def _change_acceptance_notes(
    approval_notes: str,
    task_id: str,
    task_ref: str,
) -> str:
    task_label = task_ref or task_id
    return "{}; linked Change accepted after task {} close succeeded.".format(
        approval_notes.strip(),
        task_label,
    )


def _refresh_context_after_close(
    *,
    task_id: str,
    root: Path,
    actor: str,
) -> CommandResult:
    """Refresh generated Context Pack outputs after task close mutates state."""

    build_argv = (
        sys.executable,
        str(SCRIPTS_DIR / "contextctl.py"),
        "--root",
        str(root),
        "--actor",
        actor,
        "pack",
        "build",
        "--task",
        task_id,
        "--write",
    )
    build_step = _run_context_refresh_step(
        "context_build",
        "Build task Context Pack after close",
        build_argv,
        root=root,
    )
    if build_step["returncode"] != 0:
        return _context_refresh_failure(task_id, build_step, steps=[build_step])

    check_argv = (
        sys.executable,
        str(SCRIPTS_DIR / "contextctl.py"),
        "--root",
        str(root),
        "--actor",
        actor,
        "check-generated",
    )
    check_step = _run_context_refresh_step(
        "context_check",
        "Check generated context output after close",
        check_argv,
        root=root,
    )
    steps = [build_step, check_step]
    if check_step["returncode"] != 0:
        return _context_refresh_failure(task_id, check_step, steps=steps)

    result = CommandResult.success(
        command=CONTEXT_REFRESH_COMMAND,
        domain="context",
        message="Context Pack refreshed after task close.",
        data={
            "task_id": task_id,
            "steps": steps,
            "generated_files": list(CONTEXT_REFRESH_GENERATED_FILES),
            "events": [CONTEXT_REFRESH_EVENT_FILE],
        },
    )
    result.generated_files = list(CONTEXT_REFRESH_GENERATED_FILES)
    result.changed_files = [CONTEXT_REFRESH_EVENT_FILE]
    result.events = [CONTEXT_REFRESH_EVENT_FILE]
    return result


def _context_refresh_failure(
    task_id: str,
    failed_step: Mapping[str, Any],
    *,
    steps: list[Mapping[str, Any]],
) -> CommandResult:
    result = CommandResult.failure(
        command=CONTEXT_REFRESH_COMMAND,
        domain="context",
        message="Context refresh failed after task close.",
        errors=[
            CommandMessage(
                CONTEXT_REFRESH_FAILED,
                "Context refresh command failed after task close.",
                details={
                    "task_id": task_id,
                    "failed_step": str(failed_step.get("step") or ""),
                    "returncode": int(failed_step.get("returncode") or 0),
                    "stdout": failed_step.get("stdout"),
                    "stderr": failed_step.get("stderr"),
                },
            )
        ],
    )
    result.data = {
        "task_id": task_id,
        "failed_step": str(failed_step.get("step") or ""),
        "steps": list(steps),
    }
    if str(failed_step.get("step") or "") == "context_check":
        result.generated_files = list(CONTEXT_REFRESH_GENERATED_FILES)
        result.changed_files = [CONTEXT_REFRESH_EVENT_FILE]
        result.events = [CONTEXT_REFRESH_EVENT_FILE]
    return result


def _run_context_refresh_step(
    step: str,
    title: str,
    argv: tuple[str, ...],
    *,
    root: Path,
) -> dict[str, Any]:
    try:
        completed = _run_context_refresh_command(argv, root=root)
    except (OSError, subprocess.TimeoutExpired) as exc:
        completed = subprocess.CompletedProcess(
            args=list(argv),
            returncode=1,
            stdout="",
            stderr=str(exc),
        )
    return {
        "step": step,
        "title": title,
        "command": list(argv),
        "returncode": int(completed.returncode),
        "stdout": _compact_context_refresh_output(str(completed.stdout or "")),
        "stderr": _compact_context_refresh_output(str(completed.stderr or "")),
    }


def _run_context_refresh_command(
    argv: tuple[str, ...],
    *,
    root: Path,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(argv),
        cwd=str(SCRIPTS_DIR.parent),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=300,
        check=False,
    )


def _compact_context_refresh_output(value: str) -> str | dict[str, Any]:
    if len(value) <= CONTEXT_REFRESH_OUTPUT_LIMIT:
        return value
    return {
        "truncated": True,
        "original_size": len(value),
        "stored_size": CONTEXT_REFRESH_OUTPUT_LIMIT,
        "snippet": value[:CONTEXT_REFRESH_OUTPUT_LIMIT],
    }


def _side_effect_changed_files(results: list[CommandResult]) -> list[str]:
    values: list[str] = []
    for result in results:
        _extend_unique(values, result.changed_files)
    return values


def _side_effect_generated_files(results: list[CommandResult]) -> list[str]:
    values: list[str] = []
    for result in results:
        _extend_unique(values, result.generated_files)
    return values


def _side_effect_events(results: list[CommandResult]) -> list[str]:
    values: list[str] = []
    for result in results:
        _extend_unique(values, result.events)
    return values


def _run_local_commit_after_close(
    *,
    session: Mapping[str, Any],
    session_id: str,
    task_id: str,
    root: Path,
    side_effects: tuple[CommandResult, ...],
) -> LocalCommitResult:
    policy_result = _pipeline_policy(session, task_id)
    if isinstance(policy_result, LocalCommitResult):
        return policy_result
    policy = policy_result

    refs = load_reference_state(root)
    task = _task_by_id(refs.get("tasks"), task_id)
    if not task:
        return LocalCommitResult(
            status=COMMIT_BLOCKED,
            code="COMMIT_TASK_NOT_FOUND",
            reason="Selected task was not found for local commit readiness.",
            task_id=task_id,
        )

    report_gate = evaluate_report_gate(root=root, task=task, policy=policy)
    machine_review = evaluate_machine_review(
        root=root,
        task=task,
        policy=policy,
        report_gate=report_gate,
        python_executable=sys.executable,
    )
    codex_review = _codex_review_from_phase(
        _latest_phase_result(session, REVIEW_PHASE_NAME),
        task_id=task_id,
        report_id=report_gate.report_id,
    )
    return run_local_commit(
        root=root,
        task_id=task_id,
        session_id=session_id,
        policy=policy,
        report_gate=report_gate,
        machine_review=machine_review,
        codex_review=codex_review,
        side_effects=side_effects,
    )


def _pipeline_policy(
    session: Mapping[str, Any],
    task_id: str,
) -> PipelinePolicy | LocalCommitResult:
    try:
        return PipelinePolicy.from_dict(
            _required_mapping(session.get("policy_snapshot"), "policy_snapshot")
        )
    except (KeyError, TypeError, ValueError) as exc:
        return LocalCommitResult(
            status=COMMIT_BLOCKED,
            code=COMMIT_POLICY_INVALID,
            reason=(
                "Pipeline policy snapshot is invalid for local commit: {}".format(exc)
            ),
            task_id=task_id,
        )


def _codex_review_from_phase(
    review_phase: Mapping[str, Any] | None,
    *,
    task_id: str,
    report_id: str,
) -> CodexReviewResult:
    artifacts = _mapping(review_phase.get("artifacts")) if review_phase else {}
    return CodexReviewResult(
        status=str(artifacts.get("review_status") or ""),
        code=str(artifacts.get("review_code") or ""),
        reason=str(
            artifacts.get("review_reason") or (review_phase or {}).get("reason") or ""
        ),
        verdict=str(artifacts.get("verdict") or ""),
        task_id=str(artifacts.get("task_id") or task_id),
        report_id=str(artifacts.get("report_id") or report_id),
        review_id=str(artifacts.get("review_id") or ""),
        prompt_sha256=str(
            artifacts.get("prompt_sha256")
            or artifacts.get("review_prompt_sha256")
            or ""
        ),
        prompt_bytes=_optional_int(artifacts.get("prompt_bytes"))
        or _optional_int(artifacts.get("review_prompt_bytes"))
        or 0,
        summary=str(artifacts.get("summary") or ""),
        findings=tuple(_codex_review_findings(artifacts.get("findings"))),
        risks=tuple(_string_list(artifacts.get("risks"))),
        evidence=_mapping(artifacts.get("reviewer_evidence")),
    )


def _codex_review_findings(value: Any) -> list[CodexReviewFinding]:
    if not isinstance(value, list):
        return []
    findings: list[CodexReviewFinding] = []
    for item in value:
        if not isinstance(item, Mapping):
            continue
        findings.append(
            CodexReviewFinding(
                severity=str(item.get("severity") or ""),
                message=str(item.get("message") or ""),
                file=str(item.get("file") or ""),
                criterion=str(item.get("criterion") or ""),
            )
        )
    return findings


def _local_commit_skipped(
    session: Mapping[str, Any],
    task_id: str,
) -> LocalCommitResult:
    return LocalCommitResult(
        status="skipped",
        code=COMMIT_DISABLED,
        reason="Local commit is disabled by policy.",
        task_id=task_id,
        readiness=None,
        commands=(),
        message="",
    )


def _commit_policy_enabled(session: Mapping[str, Any]) -> bool:
    policy = _mapping(session.get("policy_snapshot"))
    commit = _mapping(policy.get("commit"))
    return bool(commit.get("create_local_commit"))


def _task_by_id(tasks_state: Any, task_id: str) -> Mapping[str, Any]:
    if not isinstance(tasks_state, Mapping):
        return {}
    for task in tasks_state.get("tasks", []):
        if isinstance(task, Mapping) and str(task.get("id") or "") == task_id:
            return task
    return {}


def _required_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    raise TypeError("{} must be a mapping".format(name))


def _optional_int(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _close_success_reason(
    change_acceptance: Mapping[str, Any],
    local_commit: LocalCommitResult,
    *,
    already_closed: bool = False,
) -> str:
    if local_commit.status == COMMIT_PASS:
        if already_closed:
            return "Close recovered an already-done task and local commit was created."
        return "Close completed and local commit was created."
    status = str(change_acceptance.get("status") or "")
    if already_closed:
        if status == "accepted":
            return (
                "Close recovered an already-done task with matching owner "
                "approval evidence and linked Evolution Changes were accepted."
            )
        if status == "skipped":
            return (
                "Close recovered an already-done task with matching owner "
                "approval evidence and linked Evolution Change acceptance was skipped."
            )
        return (
            "Close recovered an already-done task with matching owner "
            "approval evidence."
        )
    if status == "accepted":
        return (
            "Close completed: the governed task close workflow marked the task "
            "done and linked Evolution Changes were accepted."
        )
    if status == "skipped":
        return (
            "Close completed: the governed task close workflow marked the task "
            "done and linked Evolution Change acceptance was skipped."
        )
    return (
        "Close completed: review APPROVE evidence existed and the governed task "
        "close workflow marked the task done."
    )


def _close_success_next_action(
    change_acceptance: Mapping[str, Any],
    local_commit: LocalCommitResult,
) -> str:
    if local_commit.status == COMMIT_PASS:
        return (
            "Review the close artifacts and local commit hash, then select "
            "the next task."
        )
    status = str(change_acceptance.get("status") or "")
    linked_change_ids = list(change_acceptance.get("linked_change_ids") or [])
    if status == "accepted":
        return "Review the close artifacts, then continue with the next selected task."
    if linked_change_ids:
        return (
            "Review the close workflow evidence and handle any skipped linked "
            "Evolution Changes only with Human Owner approval."
        )
    return "Review the close workflow evidence and select the next task when ready."


def _preflight_evidence(
    session: Mapping[str, Any],
    task_id: str,
) -> dict[str, Any]:
    phases = {
        phase_name: _latest_phase_result(session, phase_name)
        for phase_name in REQUIRED_PHASE_ORDER
    }
    statuses = {
        phase_name: _phase_summary(phase)
        for phase_name, phase in phases.items()
    }
    missing = []
    policy_result = _preflight_policy(session)
    if isinstance(policy_result, dict):
        missing.append(
            _missing_gate(
                "policy",
                "POLICY_SNAPSHOT_INVALID",
                "Session policy snapshot is invalid.",
                **policy_result,
            )
        )
        codex_review_disabled = False
    else:
        codex_review_disabled = disables_codex_review_by_policy(policy_result)

    for phase_name in REQUIRED_PASSED_PHASES:
        phase = phases[phase_name]
        if phase is None:
            missing.append(
                _missing_gate(
                    phase_name,
                    "PHASE_EVIDENCE_MISSING",
                    "Phase evidence is missing.",
                )
            )
            continue
        status = str(phase.get("status") or "")
        if status != "passed":
            missing.append(
                _missing_gate(
                    phase_name,
                    "PHASE_NOT_PASSED",
                    "Phase status must be passed before close.",
                    observed_status=status,
                )
            )
        task_mismatch = _task_mismatch(phase, task_id)
        if task_mismatch:
            missing.append(
                _missing_gate(
                    phase_name,
                    "PHASE_TASK_MISMATCH",
                    "Phase evidence does not match the session current task.",
                    **task_mismatch,
                )
            )

    review_phase = phases[REVIEW_PHASE_NAME]
    if review_phase is None:
        missing.append(
            _missing_gate(
                REVIEW_PHASE_NAME,
                "PHASE_EVIDENCE_MISSING",
                "Review evidence is missing.",
            )
        )
    else:
        review_status = str(review_phase.get("status") or "")
        review_artifacts = _mapping(review_phase.get("artifacts"))
        verdict = str(review_artifacts.get("verdict") or "").strip()
        if codex_review_disabled:
            if review_status != "skipped":
                missing.append(
                    _missing_gate(
                        REVIEW_PHASE_NAME,
                        "REVIEW_SKIP_REQUIRED",
                        (
                            "Review phase must be skipped when Codex Review is "
                            "disabled by policy."
                        ),
                        observed_status=review_status,
                    )
                )
            if not _review_skip_matches_policy(review_artifacts):
                missing.append(
                    _missing_gate(
                        REVIEW_PHASE_NAME,
                        "REVIEW_SKIP_POLICY_MISMATCH",
                        (
                            "Skipped review evidence must explicitly record the "
                            "Codex Review disable policy."
                        ),
                        observed_skip_reason=str(review_artifacts.get("skip_reason") or ""),
                    )
                )
        else:
            if review_status != "passed":
                missing.append(
                    _missing_gate(
                        REVIEW_PHASE_NAME,
                        "PHASE_NOT_PASSED",
                        "Review phase must pass before close.",
                        observed_status=review_status,
                    )
                )
            if verdict != VERDICT_APPROVE:
                missing.append(
                    _missing_gate(
                        REVIEW_PHASE_NAME,
                        "REVIEW_APPROVE_REQUIRED",
                        "Review verdict must be APPROVE before close.",
                        observed_verdict=verdict,
                    )
                )
        task_mismatch = _task_mismatch(review_phase, task_id)
        if task_mismatch:
            missing.append(
                _missing_gate(
                    REVIEW_PHASE_NAME,
                    "PHASE_TASK_MISMATCH",
                    "Review evidence does not match the session current task.",
                    **task_mismatch,
                )
            )

    report_consistency = _report_consistency(statuses)
    missing.extend(report_consistency["missing_gates"])

    return {
        "preflight_passed": not missing,
        "required_phases": list(REQUIRED_PHASE_ORDER),
        "codex_review_required": not codex_review_disabled,
        "missing_gates": missing,
        "phase_statuses": statuses,
        "report_consistency": report_consistency["details"],
    }


def _run_close_workflow(
    *,
    session: Mapping[str, Any],
    session_id: str,
    task_id: str,
    task_ref: str,
    evidence: Mapping[str, Any],
    close_policy: Mapping[str, Any],
    approval_notes: str,
    root: Path,
    actor: str,
) -> CommandResult:
    decision = ReviewCloseDecision(
        action=ACTION_CLOSE_TASK,
        stop_code=CODE_TASK_AUTO_CLOSED,
        reason=_close_workflow_reason(evidence),
        result_status="passed",
        gate_status="pass",
        notes=approval_notes,
        details={
            "source": COMMAND_NAME,
            "session_id": session_id,
            "task_id": task_id,
            "task_ref": task_ref,
            "policy": str(_mapping(session.get("policy_snapshot")).get("name") or ""),
            "close_policy": _safe_close_policy(close_policy),
            "preflight": dict(evidence),
        },
    )
    recovery = _already_closed_task_recovery_result(
        task_id=task_id,
        task_ref=task_ref,
        approval_notes=approval_notes,
        root=root,
        decision=decision,
    )
    if recovery is not None:
        return recovery
    return run_review_close_workflow(
        decision,
        root=root,
        actor=actor,
        task_id=task_id,
        python_executable=sys.executable,
        runner=None,
    )


def _already_closed_task_recovery_result(
    *,
    task_id: str,
    task_ref: str,
    approval_notes: str,
    root: Path,
    decision: ReviewCloseDecision,
) -> CommandResult | None:
    refs = load_reference_state(root)
    task = _task_by_id(refs.get("tasks"), task_id)
    if str(task.get("status") or "") != "done":
        return None

    recovery = _already_closed_recovery_evidence(
        task=task,
        task_id=task_id,
        task_ref=task_ref,
        approval_notes=approval_notes,
    )
    if recovery["status"] != "recovered":
        result = CommandResult.failure(
            command="pipeline.review_close_policy",
            domain="pipeline",
            message="Already-closed task recovery blocked.",
            errors=[
                CommandMessage(
                    str(recovery["code"]),
                    "Selected task is already done but lacks owner approval "
                    "evidence matching this close attempt.",
                    details=recovery,
                )
            ],
        )
        result.data = {
            "decision": decision.to_dict(),
            "workflows": [],
            "already_closed_by_previous_attempt": False,
            "recovery": recovery,
        }
        return result

    return CommandResult.success(
        command="pipeline.review_close_policy",
        domain="pipeline",
        message=(
            "Task is already done with matching owner approval evidence; "
            "skipped duplicate close workflows."
        ),
        data={
            "decision": decision.to_dict(),
            "workflows": [],
            "already_closed_by_previous_attempt": True,
            "recovery": recovery,
        },
    )


def _already_closed_recovery_evidence(
    *,
    task: Mapping[str, Any],
    task_id: str,
    task_ref: str,
    approval_notes: str,
) -> dict[str, Any]:
    approved_by = str(task.get("approved_by") or "").strip()
    approved_at = str(task.get("approved_at") or "").strip()
    stored_notes = str(task.get("approval_notes") or "").strip()
    current_notes = approval_notes.strip()
    notes_match = bool(stored_notes and stored_notes == current_notes)
    missing_evidence = not (
        approved_by
        and approved_at
        and stored_notes
        and current_notes
    )
    code = "TASK_ALREADY_CLOSED_BY_PREVIOUS_ATTEMPT"
    status = "recovered"
    if missing_evidence:
        code = "TASK_ALREADY_DONE_APPROVAL_EVIDENCE_MISSING"
        status = "blocked"
    elif not notes_match:
        code = "TASK_ALREADY_DONE_APPROVAL_EVIDENCE_MISMATCH"
        status = "blocked"

    return {
        "status": status,
        "code": code,
        "task_id": task_id,
        "task_ref": task_ref,
        "task_status": "done",
        "approved_by": approved_by,
        "approved_at": approved_at,
        "approval_notes_present": bool(stored_notes),
        "current_owner_approval_note_present": bool(current_notes),
        "approval_notes_match_current_intent": notes_match,
        "skipped_workflows": ["task.submit_for_review", "task.close_reviewed"],
    }


def _close_workflow_reason(evidence: Mapping[str, Any]) -> str:
    if evidence.get("codex_review_required") is False:
        return (
            "Task close completed after close phase preflight, skipped Codex Review "
            "policy evidence, Machine Review evidence, and owner approval notes."
        )
    return (
        "Task close completed after close phase preflight, review APPROVE "
        "evidence, and owner approval notes."
    )


def _codex_execution_cleanup_report(
    workflow: CommandResult,
    task_id: str,
) -> dict[str, Any]:
    step = _workflow_step_by_id(workflow, CODEX_CLEAR_STEP_ID)
    if not step:
        return {
            "status": "not_reached",
            "code": "CODEX_EXECUTION_CLEANUP_NOT_REACHED",
            "reason": "Close workflow did not reach Codex execution cleanup.",
            "task_id": task_id,
            "step_id": CODEX_CLEAR_STEP_ID,
        }

    status = str(step.get("status") or "unknown")
    skip_reason = str(step.get("skip_reason") or "").strip()
    report: dict[str, Any] = {
        "status": status,
        "code": _codex_cleanup_code(status),
        "reason": _codex_cleanup_reason(status, skip_reason),
        "task_id": task_id,
        "step_id": CODEX_CLEAR_STEP_ID,
        "command_name": str(step.get("command_name") or ""),
        "command": str(step.get("command") or ""),
    }
    returncode = step.get("returncode")
    if isinstance(returncode, int):
        report["returncode"] = returncode
    if skip_reason:
        report["skip_reason"] = skip_reason
    return report


def _workflow_step_by_id(
    workflow: CommandResult,
    step_id: str,
) -> Mapping[str, Any]:
    pending: list[Mapping[str, Any]] = [workflow.to_dict()]
    while pending:
        item = pending.pop(0)
        data = _mapping(item.get("data"))
        steps = data.get("steps")
        if isinstance(steps, list):
            for step in steps:
                if isinstance(step, Mapping) and step.get("id") == step_id:
                    return step
        nested = data.get("workflows")
        if isinstance(nested, list):
            pending.extend(item for item in nested if isinstance(item, Mapping))
    return {}


def _codex_cleanup_code(status: str) -> str:
    if status == "ok":
        return "CODEX_EXECUTION_CLEARED"
    if status == "skipped":
        return "CODEX_EXECUTION_CLEANUP_SKIPPED"
    if status == "failed":
        return "CODEX_EXECUTION_CLEANUP_FAILED"
    return "CODEX_EXECUTION_CLEANUP_UNKNOWN"


def _codex_cleanup_reason(status: str, skip_reason: str) -> str:
    if status == "ok":
        return "Closed-task Codex execution state was cleared through codexctl.py."
    if status == "skipped":
        return skip_reason or "Codex execution cleanup was skipped."
    if status == "failed":
        return "Codex execution cleanup command failed."
    return "Codex execution cleanup status is unknown."


def _close_recovery_artifacts(workflow: CommandResult) -> dict[str, Any]:
    data = _mapping(workflow.data)
    recovery = _mapping(data.get("recovery"))
    if not recovery:
        return {}
    return {
        "already_closed_by_previous_attempt": bool(
            data.get("already_closed_by_previous_attempt")
        ),
        "close_recovery": dict(recovery),
    }


def _close_policy(session: Mapping[str, Any]) -> dict[str, Any]:
    policy = _mapping(session.get("policy_snapshot"))
    closure = _mapping(policy.get("closure"))
    owner_note = str(closure.get("owner_approval_note") or "").strip()
    auto_close_task = bool(closure.get("auto_close_task"))
    return {
        "policy": str(policy.get("name") or ""),
        "auto_close_task": auto_close_task,
        "auto_accept_linked_changes": bool(auto_close_task and owner_note),
        "auto_accept_source": "closure.auto_close_task_with_owner_approval_note",
        "owner_approval_note": owner_note,
        "owner_approval_note_present": bool(owner_note),
    }


def _safe_close_policy(close_policy: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "policy": str(close_policy.get("policy") or ""),
        "auto_close_task": bool(close_policy.get("auto_close_task")),
        "auto_accept_linked_changes": bool(
            close_policy.get("auto_accept_linked_changes")
        ),
        "auto_accept_source": str(close_policy.get("auto_accept_source") or ""),
        "owner_approval_note_present": bool(
            close_policy.get("owner_approval_note_present")
        ),
    }


def _string_list(value: Any) -> list[str]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(
        value,
        (list, tuple, set),
    ):
        return []
    return _unique_strings(str(item) for item in value)


def _unique_strings(values: Any) -> list[str]:
    result: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in result:
            result.append(text)
    return result


def _preflight_policy(session: Mapping[str, Any]) -> PipelinePolicy | dict[str, Any]:
    try:
        policy = PipelinePolicy.from_dict(
            _required_mapping(session.get("policy_snapshot"), "policy_snapshot")
        )
    except (KeyError, TypeError, ValueError) as exc:
        return {"error": str(exc)}

    validation = policy.validate()
    if not validation.ok:
        return {
            "policy": policy.name,
            "policy_errors": [issue.to_message().to_dict() for issue in validation.errors],
        }
    return policy


def _review_skip_matches_policy(artifacts: Mapping[str, Any]) -> bool:
    return (
        artifacts.get("codex_review_required") is False
        and artifacts.get("policy_require_codex_review") is False
        and str(artifacts.get("skip_reason") or "") == "disabled_by_policy"
        and str(artifacts.get("review_status") or "") == "skipped"
        and str(artifacts.get("review_prompt_built") or "").lower() in {"", "false"}
        and str(artifacts.get("review_prompt_returned") or "").lower() in {"", "false"}
    )


def _report_consistency(
    statuses: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    observed = {
        name: str(summary.get("report_id") or "")
        for name, summary in statuses.items()
        if str(summary.get("report_id") or "")
    }
    report_ids = sorted(set(observed.values()))
    if len(report_ids) <= 1:
        return {
            "missing_gates": [],
            "details": {
                "status": "passed",
                "report_id": report_ids[0] if report_ids else "",
                "observed_report_ids": observed,
            },
        }
    return {
        "missing_gates": [
            _missing_gate(
                "close",
                "REPORT_EVIDENCE_MISMATCH",
                "Required phases reference different report ids.",
                observed_report_ids=observed,
            )
        ],
        "details": {
            "status": "blocked",
            "report_id": "",
            "observed_report_ids": observed,
        },
    }


def _task_mismatch(
    phase: Mapping[str, Any],
    expected_task_id: str,
) -> dict[str, str]:
    artifacts = _mapping(phase.get("artifacts"))
    observed = str(artifacts.get("task_id") or "").strip()
    if not observed or observed == expected_task_id:
        return {}
    return {
        "expected_task_id": expected_task_id,
        "observed_task_id": observed,
    }


def _missing_gate(
    phase: str,
    code: str,
    message: str,
    **details: Any,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "phase": phase,
        "code": code,
        "message": message,
    }
    result.update(details)
    return result


def _blocked_next_action(missing_gates: list[Mapping[str, Any]]) -> str:
    phase_order = []
    for gate in missing_gates:
        phase = str(gate.get("phase") or "")
        if phase and phase not in phase_order:
            phase_order.append(phase)
    if not phase_order:
        return "Resolve close preflight blockers, then rerun pipeline close --confirm."
    return (
        "Resolve required phase evidence for: {}; then rerun pipeline close --confirm."
    ).format(", ".join(phase_order))


def _resolve_session(root: Path, session_id: str) -> CommandResult:
    state = load_pipeline_state(root)
    selected_id = session_id.strip() or str(state.get("current_session_id") or "")
    if not selected_id:
        return _failure(
            "PIPELINE_SESSION_REQUIRED",
            "Pass a session id or set a current pipeline session before close.",
            details={"state_path": str(pipeline_state_path(root))},
        )
    for session in state.get("sessions", []):
        if isinstance(session, Mapping) and session.get("id") == selected_id:
            return CommandResult.success(
                command=COMMAND_NAME,
                domain="pipeline",
                message="Pipeline session loaded.",
                data={"session": dict(session)},
            )
    return _failure(
        "PIPELINE_SESSION_NOT_FOUND",
        "pipeline session not found: {}".format(selected_id),
        details={"session_id": selected_id},
    )


def _phase_command(
    phase: PhaseResult,
    *,
    session_id: str,
    task_id: str,
    root: Path,
    actor: str,
) -> CommandResult:
    phase = _bound_close_phase_artifacts(phase)
    result = record_phase_result(
        session_id,
        phase,
        root=root,
        actor=actor,
        task_id=task_id,
        command=COMMAND_NAME,
    )
    if not result.ok:
        return result
    result.message = phase.reason
    if phase.status.value == "failed":
        result.ok = False
    if phase.next_action and phase.next_action not in result.next_actions:
        result.next_actions.append(phase.next_action)
    data = result.data if isinstance(result.data, Mapping) else {}
    phase_result = data.get("phase_result") if isinstance(data, Mapping) else {}
    artifacts = (
        phase_result.get("artifacts") if isinstance(phase_result, Mapping) else {}
    )
    if isinstance(artifacts, Mapping):
        result.data["session_id"] = session_id
        result.data["task_id"] = str(artifacts.get("task_id") or task_id)
        result.data["preflight_passed"] = bool(artifacts.get("preflight_passed"))
        result.data["missing_gates"] = list(artifacts.get("missing_gates") or [])
        local_commit = artifacts.get("local_commit")
        if isinstance(local_commit, Mapping):
            result.data["local_commit"] = dict(local_commit)
            result.data["commit_hash"] = str(local_commit.get("commit_hash") or "")
    return result


def _bound_close_phase_artifacts(phase: PhaseResult) -> PhaseResult:
    return PhaseResult(
        phase=phase.phase,
        status=phase.status,
        reason=phase.reason,
        next_action=phase.next_action,
        artifacts=bound_pipeline_artifact(phase.artifacts),
        changed_files=phase.changed_files,
        generated_files=phase.generated_files,
        events=phase.events,
    )


def _merge_command_effects(
    target: CommandResult,
    results: tuple[CommandResult, ...],
) -> None:
    for result in results:
        _extend_unique(target.changed_files, result.changed_files)
        _extend_unique(target.generated_files, result.generated_files)
        _extend_unique(target.events, result.events)
        target.warnings.extend(result.warnings)
        target.errors.extend(result.errors)
        _extend_unique(target.next_actions, result.next_actions)
        if result.owner_action_required:
            target.owner_action_required = result.owner_action_required


def _extend_unique(target: list[str], values: list[str]) -> None:
    for value in values:
        if value not in target:
            target.append(value)


def _blocked(
    code: str,
    message: str,
    *,
    session_id: str,
    task_id: str = "",
    root: Path,
    actor: str,
    artifacts: Mapping[str, Any] | None = None,
    next_action: str,
) -> CommandResult:
    phase = PhaseResult.blocked(
        PHASE_NAME,
        reason=message,
        next_action=next_action,
        artifacts={"blocked_by": code, **dict(artifacts or {})},
    )
    return _phase_command(
        phase,
        session_id=session_id,
        task_id=task_id,
        root=root,
        actor=actor,
    )


def _failure(
    code: str,
    message: str,
    *,
    details: Mapping[str, Any] | None = None,
) -> CommandResult:
    phase = PhaseResult.failed(
        PHASE_NAME,
        reason=message,
        next_action=str(
            dict(details or {}).get("next_action")
            or "Fix the close input and rerun."
        ),
        artifacts={"error_code": code, **dict(details or {})},
    )
    result = CommandResult.failure(
        command=COMMAND_NAME,
        domain="pipeline",
        message=message,
        errors=[CommandMessage(code, message, details=dict(details or {}))],
    )
    result.data = {"phase_result": phase.to_dict()}
    return result


def _latest_phase_result(
    session: Mapping[str, Any],
    phase_name: str,
) -> Mapping[str, Any] | None:
    history = session.get("phase_history")
    if not isinstance(history, list):
        return None
    for entry in reversed(history):
        if isinstance(entry, Mapping) and entry.get("phase") == phase_name:
            return entry
    return None


def _phase_summary(phase: Mapping[str, Any] | None) -> dict[str, Any]:
    if phase is None:
        return {
            "present": False,
            "phase": "",
            "status": "",
            "reason": "",
            "task_id": "",
            "report_id": "",
            "review_id": "",
            "verdict": "",
        }
    artifacts = _mapping(phase.get("artifacts"))
    return {
        "present": True,
        "phase": str(phase.get("phase") or ""),
        "status": str(phase.get("status") or ""),
        "reason": str(phase.get("reason") or ""),
        "task_id": str(artifacts.get("task_id") or ""),
        "report_id": str(artifacts.get("report_id") or ""),
        "review_id": str(artifacts.get("review_id") or ""),
        "verdict": str(artifacts.get("verdict") or ""),
        "skip_reason": str(artifacts.get("skip_reason") or ""),
        "codex_review_required": artifacts.get("codex_review_required"),
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


__all__ = ["close_phase"]

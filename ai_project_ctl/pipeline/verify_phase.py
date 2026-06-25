"""Pipeline verify phase service.

The verify phase starts with the structured execution report gate. It consumes
the report collected by the collect-report phase and records compact gate
evidence for later pipeline phases.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from ai_project_ctl.core.result import CommandMessage, CommandResult

from .git_diff_gate import BLOCKED as GIT_DIFF_BLOCKED
from .git_diff_gate import CODE_DIFF_MISMATCH as GIT_DIFF_CODE_DIFF_MISMATCH
from .git_diff_gate import CODE_PASS as GIT_DIFF_CODE_PASS
from .git_diff_gate import FAIL as GIT_DIFF_FAIL
from .git_diff_gate import PASS as GIT_DIFF_PASS
from .git_diff_gate import AllowedFilesGateResult
from .git_diff_gate import GitDiffGateResult
from .git_diff_gate import ProtectedFilesGateResult
from .git_diff_gate import evaluate_allowed_files_gate
from .git_diff_gate import evaluate_git_diff_gate
from .git_diff_gate import evaluate_protected_files_gate
from .phase import PhaseResult
from .policy import PipelinePolicy
from .report_gate import FAIL as REPORT_FAIL
from .report_gate import PASS as REPORT_PASS
from .report_gate import WARN as REPORT_WARN
from .report_gate import evaluate_report_gate
from .session import record_phase_result
from .state import load_pipeline_state, load_reference_state, pipeline_state_path


COMMAND_NAME = "pipeline.phase.verify"
PHASE_NAME = "verify"
COLLECT_REPORT_PHASE_NAME = "collect_report"
VERIFY_EVIDENCE_SCHEMA_VERSION = 1
MAX_EVIDENCE_ITEMS = 50
MAX_EVIDENCE_CHECKS = 20
MAX_EVIDENCE_TEXT = 240
RUNTIME_LOG_PATH_PREFIX = "AI_PROJECT/logs/"
GIT_DIFF_GATES_POLICY_KEY = "git_diff_gates_policy"
SKIPPED_GATES_KEY = "skipped_gates"
GIT_DIFF_GATES_DISABLED_REASON = "policy.verify.run_git_diff_gates is false"
GIT_DIFF_BASED_GATE_NAMES = (
    "git_diff_gate",
    "protected_files_gate",
    "allowed_files_gate",
)


def verify_phase(
    session_id: str = "",
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
) -> CommandResult:
    """Run the structured report gate for the collected execution report."""

    root_path = Path(root).resolve()
    session_result = _resolve_session(root_path, session_id)
    if not session_result.ok:
        return session_result

    session = session_result.data["session"]
    selected_session_id = str(session.get("id") or "")
    task_id = str(session.get("current_task_id") or "").strip()
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

    collect_phase = _latest_phase_result(session, COLLECT_REPORT_PHASE_NAME)
    if collect_phase is None:
        return _blocked(
            "COLLECT_REPORT_PHASE_REQUIRED",
            "Collect-report phase evidence is missing for this session.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={"session_id": selected_session_id, "task_id": task_id},
            next_action="Run pipeline phase collect-report before verify.",
        )

    collect_artifacts = _mapping(collect_phase.get("artifacts"))
    if str(collect_phase.get("status") or "") != "passed":
        return _blocked(
            "COLLECT_REPORT_NOT_PASSED",
            "Collect-report phase has not passed for this session.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                "session_id": selected_session_id,
                "task_id": task_id,
                "collect_report_phase": _phase_summary(collect_phase),
            },
            next_action="Resolve collect-report, then rerun verify.",
        )

    collected_report_id = str(collect_artifacts.get("report_id") or "").strip()
    if not collected_report_id:
        return _blocked(
            "COLLECT_REPORT_ID_MISSING",
            "Collect-report phase did not record a report id.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                "session_id": selected_session_id,
                "task_id": task_id,
                "collect_report_phase": _phase_summary(collect_phase),
            },
            next_action="Rerun collect-report so verify can bind to a report id.",
        )

    refs = load_reference_state(root_path)
    tasks_state = refs.get("tasks")
    if not isinstance(tasks_state, Mapping):
        return _blocked(
            "PIPELINE_TASKS_STATE_NOT_FOUND",
            "Task state is required to verify a pipeline task.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={"session_id": selected_session_id, "task_id": task_id},
            next_action="Restore task state, then rerun verify.",
        )

    task = _task_by_id(tasks_state, task_id)
    if task is None:
        return _blocked(
            "PIPELINE_TASK_NOT_FOUND",
            "Pipeline session current task is missing from task state.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={"session_id": selected_session_id, "task_id": task_id},
            next_action="Fix the pipeline session task selection, then rerun verify.",
        )

    try:
        policy = PipelinePolicy.from_dict(
            _required_mapping(session.get("policy_snapshot"), "policy_snapshot")
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _blocked(
            "PIPELINE_VERIFY_POLICY_INVALID",
            "Session policy snapshot is invalid: {}".format(exc),
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={"session_id": selected_session_id, "task_id": task_id},
            next_action="Fix or recreate the session with a valid pipeline policy.",
        )

    validation = policy.validate()
    if not validation.ok:
        return _blocked(
            "PIPELINE_VERIFY_POLICY_INVALID",
            "Session policy does not pass validation.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                "session_id": selected_session_id,
                "task_id": task_id,
                "policy": policy.name,
                "policy_errors": [
                    issue.to_message().to_dict() for issue in validation.errors
                ],
            },
            next_action="Fix or recreate the session with a valid pipeline policy.",
        )

    report_gate = evaluate_report_gate(root=root_path, task=task, policy=policy)
    report_artifacts = {
        "session_id": selected_session_id,
        "task_id": task_id,
        "report_id": report_gate.report_id,
        "collected_report_id": collected_report_id,
        "policy": policy.name,
        "collect_report_phase": _phase_summary(collect_phase),
        "report_gate_status": report_gate.status,
        "report_gate_code": report_gate.code,
        "report_gate": report_gate.to_dict(),
    }
    project_tests = _project_tests_evidence(policy, report_gate)
    if project_tests:
        report_artifacts["project_tests"] = project_tests

    if report_gate.report_id and report_gate.report_id != collected_report_id:
        return _blocked(
            "REPORT_CHANGED_AFTER_COLLECT",
            "Latest report gate target differs from the collected report.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                "blocked_by": "REPORT_CHANGED_AFTER_COLLECT",
                **report_artifacts,
            },
            next_action="Rerun collect-report, then rerun verify.",
        )

    if report_gate.status in {REPORT_PASS, REPORT_WARN}:
        if policy.verify.run_git_diff_gates:
            phase = _phase_with_git_diff_gates(
                root_path=root_path,
                session=session,
                task=task,
                report_gate=report_gate,
                report_artifacts=report_artifacts,
            )
        else:
            phase = _phase_with_git_diff_gates_skipped(
                policy=policy,
                report_gate=report_gate,
                report_artifacts=report_artifacts,
            )
    elif report_gate.status == REPORT_FAIL:
        phase = PhaseResult.blocked(
            PHASE_NAME,
            reason="Report gate failed: {}".format(report_gate.reason),
            next_action="Fix the structured report or task output, then rerun verify.",
            artifacts={"blocked_by": report_gate.code, **report_artifacts},
            changed_files=report_gate.changed_files,
            generated_files=report_gate.generated_files,
        )
    else:
        phase = PhaseResult.failed(
            PHASE_NAME,
            reason="Report gate returned unknown status: {}".format(
                report_gate.status
            ),
            next_action="Fix report gate status handling, then rerun verify.",
            artifacts={"error_code": "REPORT_GATE_UNKNOWN_STATUS", **report_artifacts},
        )

    return _phase_command(
        phase,
        session_id=selected_session_id,
        task_id=task_id,
        root=root_path,
        actor=actor,
    )


def _resolve_session(root: Path, session_id: str) -> CommandResult:
    state = load_pipeline_state(root)
    selected_id = session_id.strip() or str(state.get("current_session_id") or "")
    if not selected_id:
        return _failure(
            "PIPELINE_SESSION_REQUIRED",
            "Pass a session id or set a current pipeline session before verify.",
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
    phase = _phase_with_verify_evidence(phase)
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
        result.data["report_id"] = str(artifacts.get("report_id") or "")
        result.data["report_gate_status"] = str(
            artifacts.get("report_gate_status") or ""
        )
        result.data["report_gate_code"] = str(
            artifacts.get("report_gate_code") or ""
        )
        result.data["git_diff_gate_status"] = str(
            artifacts.get("git_diff_gate_status") or ""
        )
        result.data["git_diff_gate_code"] = str(
            artifacts.get("git_diff_gate_code") or ""
        )
        result.data["allowed_files_gate_status"] = str(
            artifacts.get("allowed_files_gate_status") or ""
        )
        result.data["allowed_files_gate_code"] = str(
            artifacts.get("allowed_files_gate_code") or ""
        )
        result.data["protected_files_gate_status"] = str(
            artifacts.get("protected_files_gate_status") or ""
        )
        result.data["protected_files_gate_code"] = str(
            artifacts.get("protected_files_gate_code") or ""
        )
        git_diff_policy = artifacts.get(GIT_DIFF_GATES_POLICY_KEY)
        if isinstance(git_diff_policy, Mapping):
            result.data[GIT_DIFF_GATES_POLICY_KEY] = dict(git_diff_policy)
        skipped_gates = artifacts.get(SKIPPED_GATES_KEY)
        if isinstance(skipped_gates, list):
            result.data[SKIPPED_GATES_KEY] = [
                dict(item) for item in skipped_gates if isinstance(item, Mapping)
            ]
        verification = artifacts.get("verify_evidence")
        if isinstance(verification, Mapping):
            result.data["verification"] = dict(verification)
            result.data["verify_evidence"] = dict(verification)
    return result


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
        next_action="Fix the verify input and rerun the phase.",
        artifacts={"error_code": code, **dict(details or {})},
    )
    phase = _phase_with_verify_evidence(phase)
    result = CommandResult.failure(
        command=COMMAND_NAME,
        domain="pipeline",
        message=message,
        errors=[CommandMessage(code, message, details=dict(details or {}))],
    )
    verification = phase.artifacts.get("verify_evidence")
    result.data = {
        "phase_result": phase.to_dict(),
        "verification": dict(verification) if isinstance(verification, Mapping) else {},
        "verify_evidence": dict(verification) if isinstance(verification, Mapping) else {},
    }
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


def _task_by_id(
    tasks_state: Mapping[str, Any],
    task_id: str,
) -> Mapping[str, Any] | None:
    tasks = tasks_state.get("tasks")
    if not isinstance(tasks, list):
        return None
    for task in tasks:
        if isinstance(task, Mapping) and task.get("id") == task_id:
            return task
    return None


def _required_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError("{} must be an object".format(field_name))
    return value


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _phase_summary(phase: Mapping[str, Any]) -> dict[str, Any]:
    artifacts = _mapping(phase.get("artifacts"))
    return {
        "phase": str(phase.get("phase") or ""),
        "status": str(phase.get("status") or ""),
        "reason": str(phase.get("reason") or ""),
        "report_id": str(artifacts.get("report_id") or ""),
        "task_id": str(artifacts.get("task_id") or ""),
    }


def _reported_diff_files(report_gate: Any) -> tuple[str, ...]:
    return _exclude_runtime_log_paths(
        _sorted_unique((*report_gate.changed_files, *report_gate.generated_files))
    )


def _phase_with_git_diff_gates(
    *,
    root_path: Path,
    session: Mapping[str, Any],
    task: Mapping[str, Any],
    report_gate: Any,
    report_artifacts: Mapping[str, Any],
) -> PhaseResult:
    git_diff_gate = evaluate_git_diff_gate(
        root=root_path,
        expected_files=_reported_diff_files(report_gate),
    )
    git_diff_gate = _exclude_runtime_logs_from_git_diff(git_diff_gate)
    comparison = _report_git_diff_comparison(report_gate, git_diff_gate)
    git_diff_artifacts = {
        **dict(report_artifacts),
        "git_diff_gate_status": git_diff_gate.status,
        "git_diff_gate_code": git_diff_gate.code,
        "git_diff_gate": git_diff_gate.to_dict(),
        "report_git_diff_comparison": comparison,
    }
    protected_files_gate = evaluate_protected_files_gate(
        root=git_diff_gate.repo_root or root_path,
        changed_files=git_diff_gate.changed_files,
        reported_changed_files=report_gate.changed_files,
        reported_generated_files=report_gate.generated_files,
        governed_control_files=_governed_phase_changed_files(session),
        governed_generated_files=_governed_phase_generated_files(session),
    )
    protected_artifacts = {
        **git_diff_artifacts,
        "protected_files_gate_status": protected_files_gate.status,
        "protected_files_gate_code": protected_files_gate.code,
        "protected_files_gate": protected_files_gate.to_dict(),
    }
    if not protected_files_gate.ok:
        return PhaseResult.blocked(
            PHASE_NAME,
            reason=_protected_files_blocked_reason(protected_files_gate),
            next_action=(
                "Move protected project-control changes out of executor scope "
                "or regenerate them through governed control commands, then rerun verify."
            ),
            artifacts={
                "blocked_by": protected_files_gate.code,
                "protected_files_policy": (
                    "actual_git_diff_must_not_include_protected_executor_edits"
                ),
                **protected_artifacts,
            },
            changed_files=report_gate.changed_files,
            generated_files=report_gate.generated_files,
        )
    if git_diff_gate.status == GIT_DIFF_PASS:
        allowed_files_gate = evaluate_allowed_files_gate(
            root=git_diff_gate.repo_root or root_path,
            changed_files=git_diff_gate.changed_files,
            allowed_files=_string_list(task.get("allowed_files")),
            generated_files=report_gate.generated_files,
        )
        gated_artifacts = {
            **protected_artifacts,
            "allowed_files_gate_status": allowed_files_gate.status,
            "allowed_files_gate_code": allowed_files_gate.code,
            "allowed_files_gate": allowed_files_gate.to_dict(),
        }
        if not allowed_files_gate.ok:
            return PhaseResult.blocked(
                PHASE_NAME,
                reason=_allowed_files_blocked_reason(allowed_files_gate),
                next_action=(
                    "Move out-of-scope working-tree changes out of this task "
                    "or update task allowed_files through project control, then rerun verify."
                ),
                artifacts={
                    "blocked_by": allowed_files_gate.code,
                    "scope_policy": "actual_git_diff_must_match_task_allowed_files",
                    **gated_artifacts,
                },
                changed_files=report_gate.changed_files,
                generated_files=report_gate.generated_files,
            )
        if report_gate.status == REPORT_PASS:
            return PhaseResult.passed(
                PHASE_NAME,
                reason=(
                    "Report gate, git diff gate, protected-files gate, and "
                    "allowed-files gate passed."
                ),
                next_action="Run pipeline phase review.",
                artifacts=gated_artifacts,
                changed_files=report_gate.changed_files,
                generated_files=report_gate.generated_files,
            )
        return PhaseResult.blocked(
            PHASE_NAME,
            reason="Report gate returned warning(s): {}".format(report_gate.reason),
            next_action=(
                "Resolve report gate warnings or define an explicit follow-up "
                "policy, then rerun verify."
            ),
            artifacts={
                "blocked_by": report_gate.code,
                "warn_policy": "report_gate_warn_blocks_verify",
                **gated_artifacts,
            },
            changed_files=report_gate.changed_files,
            generated_files=report_gate.generated_files,
        )
    if git_diff_gate.status in {GIT_DIFF_BLOCKED, GIT_DIFF_FAIL}:
        return PhaseResult.blocked(
            PHASE_NAME,
            reason=_git_diff_blocked_reason(comparison),
            next_action=(
                "Update the structured report file lists or resolve unintended "
                "working-tree changes, then rerun verify."
            ),
            artifacts={
                "blocked_by": git_diff_gate.code,
                "mismatch_policy": "git_diff_mismatch_blocks_verify",
                **protected_artifacts,
            },
            changed_files=report_gate.changed_files,
            generated_files=report_gate.generated_files,
        )
    return PhaseResult.failed(
        PHASE_NAME,
        reason="Git diff gate returned unknown status: {}".format(git_diff_gate.status),
        next_action="Fix git diff gate status handling, then rerun verify.",
        artifacts={
            "error_code": "GIT_DIFF_GATE_UNKNOWN_STATUS",
            **protected_artifacts,
        },
    )


def _phase_with_git_diff_gates_skipped(
    *,
    policy: PipelinePolicy,
    report_gate: Any,
    report_artifacts: Mapping[str, Any],
) -> PhaseResult:
    relaxed_artifacts = {
        **dict(report_artifacts),
        GIT_DIFF_GATES_POLICY_KEY: _git_diff_gates_policy_artifact(policy),
        SKIPPED_GATES_KEY: _skipped_git_diff_gate_artifacts(),
    }
    if report_gate.status == REPORT_PASS:
        return PhaseResult.passed(
            PHASE_NAME,
            reason=(
                "Report gate passed; git diff, protected-files, and "
                "allowed-files gates were skipped by policy."
            ),
            next_action="Run pipeline phase review.",
            artifacts=relaxed_artifacts,
            changed_files=report_gate.changed_files,
            generated_files=report_gate.generated_files,
        )
    return PhaseResult.blocked(
        PHASE_NAME,
        reason="Report gate returned warning(s): {}".format(report_gate.reason),
        next_action=(
            "Resolve report gate warnings or define an explicit follow-up "
            "policy, then rerun verify."
        ),
        artifacts={
            "blocked_by": report_gate.code,
            "warn_policy": "report_gate_warn_blocks_verify",
            **relaxed_artifacts,
        },
        changed_files=report_gate.changed_files,
        generated_files=report_gate.generated_files,
    )


def _git_diff_gates_policy_artifact(policy: PipelinePolicy) -> dict[str, Any]:
    return {
        "run_git_diff_gates": bool(policy.verify.run_git_diff_gates),
        "mode": "strict" if policy.verify.run_git_diff_gates else "relaxed",
        "reason": "" if policy.verify.run_git_diff_gates else GIT_DIFF_GATES_DISABLED_REASON,
    }


def _skipped_git_diff_gate_artifacts() -> list[dict[str, str]]:
    return [
        {
            "name": name,
            "status": "skipped",
            "code": "{}_SKIPPED_BY_POLICY".format(name.upper()),
            "reason": GIT_DIFF_GATES_DISABLED_REASON,
        }
        for name in GIT_DIFF_BASED_GATE_NAMES
    ]


def _exclude_runtime_logs_from_git_diff(
    git_diff_gate: GitDiffGateResult,
) -> GitDiffGateResult:
    # UI-triggered runs and Codex pipeline execution logs are runtime artifacts
    # under AI_PROJECT/logs/**; they are excluded from task diff coverage without
    # relaxing gates for source, tests, docs or protected project-control state.
    if not _git_diff_gate_has_runtime_logs(git_diff_gate):
        return git_diff_gate

    expected_files = _exclude_runtime_log_paths(git_diff_gate.expected_files)
    changed_files = _exclude_runtime_log_paths(git_diff_gate.changed_files)
    tracked_files = _exclude_runtime_log_paths(git_diff_gate.tracked_files)
    staged_files = _exclude_runtime_log_paths(git_diff_gate.staged_files)
    unstaged_files = _exclude_runtime_log_paths(git_diff_gate.unstaged_files)
    untracked_files = _exclude_runtime_log_paths(git_diff_gate.untracked_files)
    status_entries = tuple(
        entry
        for entry in git_diff_gate.status_entries
        if not _is_runtime_log_path(entry.path)
    )
    unexpected_files = _sorted_unique(set(changed_files) - set(expected_files))
    missing_files = _sorted_unique(set(expected_files) - set(changed_files))

    status = git_diff_gate.status
    code = git_diff_gate.code
    reason = git_diff_gate.reason
    if code == GIT_DIFF_CODE_DIFF_MISMATCH:
        if unexpected_files or missing_files:
            reason = "working_tree_diff_does_not_match_expected_files"
        else:
            status = GIT_DIFF_PASS
            code = GIT_DIFF_CODE_PASS
            reason = (
                "working_tree_clean"
                if not changed_files
                else "working_tree_matches_expected_files"
            )

    return replace(
        git_diff_gate,
        status=status,
        code=code,
        reason=reason,
        expected_files=expected_files,
        changed_files=changed_files,
        tracked_files=tracked_files,
        staged_files=staged_files,
        unstaged_files=unstaged_files,
        untracked_files=untracked_files,
        unexpected_files=unexpected_files,
        missing_files=missing_files,
        status_entries=status_entries,
    )


def _git_diff_gate_has_runtime_logs(git_diff_gate: GitDiffGateResult) -> bool:
    path_groups = (
        git_diff_gate.expected_files,
        git_diff_gate.changed_files,
        git_diff_gate.tracked_files,
        git_diff_gate.staged_files,
        git_diff_gate.unstaged_files,
        git_diff_gate.untracked_files,
        git_diff_gate.unexpected_files,
        git_diff_gate.missing_files,
    )
    return any(
        _is_runtime_log_path(path)
        for paths in path_groups
        for path in paths
    ) or any(
        _is_runtime_log_path(entry.path) for entry in git_diff_gate.status_entries
    )


def _exclude_runtime_log_paths(paths: Sequence[str | Path]) -> tuple[str, ...]:
    return _sorted_unique(path for path in paths if not _is_runtime_log_path(path))


def _is_runtime_log_path(path: str | Path) -> bool:
    text = str(path).strip().replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text == RUNTIME_LOG_PATH_PREFIX.rstrip("/") or text.startswith(
        RUNTIME_LOG_PATH_PREFIX
    )


def _report_git_diff_comparison(
    report_gate: Any,
    git_diff_gate: GitDiffGateResult,
) -> dict[str, Any]:
    return {
        "status": "pass" if git_diff_gate.status == GIT_DIFF_PASS else "blocked",
        "policy": "reported_files_must_match_actual_git_diff",
        "report_changed_files": list(report_gate.changed_files),
        "report_generated_files": list(report_gate.generated_files),
        "reported_files": list(git_diff_gate.expected_files),
        "actual_changed_files": list(git_diff_gate.changed_files),
        "missing_from_report": list(git_diff_gate.unexpected_files),
        "extra_in_report": list(git_diff_gate.missing_files),
    }


def _git_diff_blocked_reason(comparison: Mapping[str, Any]) -> str:
    missing = _string_list(comparison.get("missing_from_report"))
    extra = _string_list(comparison.get("extra_in_report"))
    if missing or extra:
        parts = []
        if missing:
            parts.append("missing_from_report: {}".format(", ".join(missing)))
        if extra:
            parts.append("extra_in_report: {}".format(", ".join(extra)))
        return "Git diff gate blocked: {}.".format("; ".join(parts))
    return "Git diff gate blocked: report file evidence does not match actual diff."


def _allowed_files_blocked_reason(
    allowed_files_gate: AllowedFilesGateResult,
) -> str:
    out_of_scope = list(allowed_files_gate.out_of_scope_files)
    if out_of_scope:
        return "Allowed-files gate blocked: out_of_scope_files: {}.".format(
            ", ".join(out_of_scope)
        )
    return "Allowed-files gate blocked: actual diff is outside task allowed_files."


def _protected_files_blocked_reason(
    protected_files_gate: ProtectedFilesGateResult,
) -> str:
    violations = list(protected_files_gate.violations)
    if violations:
        details = ", ".join(
            "{} ({})".format(violation.path, violation.reason_code)
            for violation in violations
        )
        return "Protected-files gate blocked: {}.".format(details)
    return "Protected-files gate blocked: protected project-control file violation."


def _governed_phase_changed_files(session: Mapping[str, Any]) -> tuple[str, ...]:
    return _phase_history_files(session, "changed_files")


def _governed_phase_generated_files(session: Mapping[str, Any]) -> tuple[str, ...]:
    return _phase_history_files(session, "generated_files")


def _phase_history_files(
    session: Mapping[str, Any],
    field_name: str,
) -> tuple[str, ...]:
    history = session.get("phase_history")
    if not isinstance(history, list):
        return ()
    values: list[str] = []
    for entry in history:
        if not isinstance(entry, Mapping):
            continue
        entry_values = entry.get(field_name)
        if not isinstance(entry_values, list):
            continue
        values.extend(str(item) for item in entry_values if isinstance(item, str))
    return _sorted_unique(values)


def _phase_with_verify_evidence(phase: PhaseResult) -> PhaseResult:
    artifacts = dict(phase.artifacts)
    artifacts["verify_evidence"] = _verify_evidence(phase, artifacts)
    return PhaseResult(
        phase=phase.phase,
        status=phase.status,
        reason=phase.reason,
        next_action=phase.next_action,
        artifacts=artifacts,
        changed_files=phase.changed_files,
        generated_files=phase.generated_files,
        events=phase.events,
    )


def _verify_evidence(
    phase: PhaseResult,
    artifacts: Mapping[str, Any],
) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "schema_version": VERIFY_EVIDENCE_SCHEMA_VERSION,
        "phase": phase.phase,
        "status": phase.status.value,
        "task_id": str(artifacts.get("task_id") or ""),
        "report_id": str(artifacts.get("report_id") or ""),
        "blocked_by": str(
            artifacts.get("blocked_by") or artifacts.get("error_code") or ""
        ),
    }
    for key, value in (
        ("report_gate", _report_gate_evidence(artifacts)),
        ("git_diff_gate", _git_diff_gate_evidence(artifacts)),
        ("protected_files_gate", _protected_files_gate_evidence(artifacts)),
        ("allowed_files_gate", _allowed_files_gate_evidence(artifacts)),
    ):
        if value:
            evidence[key] = value
    project_tests = artifacts.get("project_tests")
    if isinstance(project_tests, Mapping):
        evidence["project_tests"] = dict(project_tests)
    git_diff_policy = artifacts.get(GIT_DIFF_GATES_POLICY_KEY)
    if isinstance(git_diff_policy, Mapping):
        evidence[GIT_DIFF_GATES_POLICY_KEY] = dict(git_diff_policy)
    skipped_gates = artifacts.get(SKIPPED_GATES_KEY)
    if isinstance(skipped_gates, list):
        evidence[SKIPPED_GATES_KEY] = [
            dict(item) for item in skipped_gates if isinstance(item, Mapping)
        ]
    return evidence


def _report_gate_evidence(artifacts: Mapping[str, Any]) -> dict[str, Any]:
    gate = _mapping(artifacts.get("report_gate"))
    status = str(artifacts.get("report_gate_status") or gate.get("status") or "")
    code = str(artifacts.get("report_gate_code") or gate.get("code") or "")
    if not status and not code:
        return {}
    return {
        "status": status,
        "code": code,
        "reason": _short_text(gate.get("reason")),
        "report_id": str(gate.get("report_id") or artifacts.get("report_id") or ""),
        "task_id": str(gate.get("task_id") or artifacts.get("task_id") or ""),
        "changed_files": _limited_strings(gate.get("changed_files")),
        "generated_files": _limited_strings(gate.get("generated_files")),
        "issues": _compact_messages(gate.get("issues")),
        "warnings": _compact_messages(gate.get("warnings")),
        "checks": _compact_checks(gate.get("checks")),
    }


def _git_diff_gate_evidence(artifacts: Mapping[str, Any]) -> dict[str, Any]:
    gate = _mapping(artifacts.get("git_diff_gate"))
    status = str(artifacts.get("git_diff_gate_status") or gate.get("status") or "")
    code = str(artifacts.get("git_diff_gate_code") or gate.get("code") or "")
    if not status and not code:
        return {}
    return {
        "status": status,
        "code": code,
        "reason": _short_text(gate.get("reason")),
        "expected_files": _limited_strings(gate.get("expected_files")),
        "actual_changed_files": _limited_strings(gate.get("changed_files")),
        "tracked_files": _limited_strings(gate.get("tracked_files")),
        "staged_files": _limited_strings(gate.get("staged_files")),
        "unstaged_files": _limited_strings(gate.get("unstaged_files")),
        "untracked_files": _limited_strings(gate.get("untracked_files")),
        "missing_from_report": _limited_strings(gate.get("unexpected_files")),
        "extra_in_report": _limited_strings(gate.get("missing_files")),
        "command_count": _list_count(gate.get("commands")),
    }


def _protected_files_gate_evidence(artifacts: Mapping[str, Any]) -> dict[str, Any]:
    gate = _mapping(artifacts.get("protected_files_gate"))
    status = str(artifacts.get("protected_files_gate_status") or gate.get("status") or "")
    code = str(artifacts.get("protected_files_gate_code") or gate.get("code") or "")
    if not status and not code:
        return {}
    return {
        "status": status,
        "code": code,
        "reason": _short_text(gate.get("reason")),
        "actual_changed_files": _limited_strings(gate.get("actual_changed_files")),
        "reported_files": _limited_strings(gate.get("reported_files")),
        "allowed_protected_files": _limited_strings(gate.get("allowed_protected_files")),
        "violations": _compact_messages(gate.get("violations")),
    }


def _allowed_files_gate_evidence(artifacts: Mapping[str, Any]) -> dict[str, Any]:
    gate = _mapping(artifacts.get("allowed_files_gate"))
    status = str(artifacts.get("allowed_files_gate_status") or gate.get("status") or "")
    code = str(artifacts.get("allowed_files_gate_code") or gate.get("code") or "")
    if not status and not code:
        return {}
    return {
        "status": status,
        "code": code,
        "reason": _short_text(gate.get("reason")),
        "actual_changed_files": _limited_strings(gate.get("actual_changed_files")),
        "allowed_patterns": _limited_strings(gate.get("allowed_patterns")),
        "allowed_files": _limited_strings(gate.get("allowed_files")),
        "governed_generated_matches": _limited_strings(
            gate.get("governed_generated_matches")
        ),
        "out_of_scope_files": _limited_strings(gate.get("out_of_scope_files")),
    }


def _project_tests_evidence(policy: PipelinePolicy, report_gate: Any) -> dict[str, Any]:
    commands = _command_list(policy.project_tests.commands)
    if not commands:
        return {}
    return {
        "configured": True,
        "blocking": bool(policy.project_tests.blocking),
        "timeout_sec": int(policy.project_tests.timeout_sec),
        "command_count": len(commands),
        "commands": [list(command) for command in commands[:MAX_EVIDENCE_CHECKS]],
        "reported_checks": _compact_checks(getattr(report_gate, "checks", ())),
    }


def _command_list(value: Any) -> list[tuple[str, ...]]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        return []
    commands: list[tuple[str, ...]] = []
    for command in value:
        if isinstance(command, (str, bytes, bytearray)) or not isinstance(command, Sequence):
            continue
        argv = tuple(str(part) for part in command if str(part).strip())
        if argv:
            commands.append(argv)
    return commands


def _compact_checks(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    checks: list[dict[str, Any]] = []
    for item in value[:MAX_EVIDENCE_CHECKS]:
        if not isinstance(item, Mapping):
            continue
        check: dict[str, Any] = {
            "name": _short_text(item.get("name")),
            "result": _short_text(item.get("result")),
            "blocking": bool(item.get("blocking", False)),
        }
        command = item.get("command")
        if command:
            check["command"] = _short_text(command)
        duration = item.get("duration_sec")
        if isinstance(duration, (int, float)) and not isinstance(duration, bool):
            check["duration_sec"] = duration
        checks.append(check)
    return checks


def _compact_messages(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    messages: list[dict[str, str]] = []
    for item in value[:MAX_EVIDENCE_CHECKS]:
        if not isinstance(item, Mapping):
            continue
        message: dict[str, str] = {}
        for key in ("code", "reason_code", "message", "reason", "path"):
            text = _short_text(item.get(key))
            if text:
                message[key] = text
        if message:
            messages.append(message)
    return messages


def _limited_strings(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    result: list[str] = []
    for item in value[:MAX_EVIDENCE_ITEMS]:
        text = _short_text(item)
        if text:
            result.append(text)
    return result


def _list_count(value: Any) -> int:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return len(value)
    return 0


def _short_text(value: Any) -> str:
    text = str(value or "").replace("\n", " ").strip()
    if len(text) > MAX_EVIDENCE_TEXT:
        return text[: MAX_EVIDENCE_TEXT - 3].rstrip() + "..."
    return text


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str)]


def _sorted_unique(values: Any) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values if str(value).strip()}))


__all__ = ["verify_phase"]

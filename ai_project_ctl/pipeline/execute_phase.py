"""Pipeline execute phase service.

The execute phase consumes prepare-phase artifact evidence from a pipeline
session and delegates only to the Codex execution adapter. It does not run
report collection, verification, review, close, or commit gates.
"""

from __future__ import annotations

from dataclasses import replace
import hashlib
import inspect
import json
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ai_project_ctl import task_reports as task_report_service
from ai_project_ctl.core.events import utc_now
from ai_project_ctl.core.result import CommandMessage, CommandResult

from .codex_adapter import (
    CODE_MANUAL_HANDOFF,
    CODE_REPORT_MISSING,
    CODE_REPORT_INVALID,
    CodexAdapterResult,
    OutputRunner,
    run_codex_adapter,
)
from .git_status import (
    GitStatusError,
    GitStatusSnapshot,
    capture_git_status_snapshot,
    dirty_paths_after_baseline,
    filter_paths_by_allowed_files,
)
from .phase import PhaseResult
from .policy import CodexAdapterMode, CodexExecutionMode, PipelinePolicy
from .report_builder import report_payload_with_captured_changed_files
from .session import record_phase_result
from .state import load_pipeline_state, load_reference_state, pipeline_state_path
from .token_budget import PASS as TOKEN_BUDGET_PASS
from .token_budget import TokenBudgetGateResult, evaluate_token_budget


COMMAND_NAME = "pipeline.phase.execute"
PHASE_NAME = "execute"
PREPARE_PHASE_NAME = "prepare"
LIVE_EXECUTE_STEP_NAME = "execute"
PROTECTED_CHECK_FAILED = "PROTECTED_GENERATED_FRESHNESS_FAILED"
PROTECTED_CHECK_TIMEOUT_SEC = 300
PROTECTED_CHECK_TEXT_LIMIT = 1200
PROTECTED_CHECK_ITEMS_LIMIT = 8
EXECUTE_FILE_DELTA_UNAVAILABLE = "EXECUTE_FILE_DELTA_UNAVAILABLE"
EXECUTE_FILE_DELTA_CAPTURED = "EXECUTE_FILE_DELTA_CAPTURED"
EXECUTE_FILE_DELTA_SKIPPED = "EXECUTE_FILE_DELTA_SKIPPED"
IGNORED_EXECUTE_FILE_PREFIXES = ("AI_PROJECT/.locks/", "AI_PROJECT/logs/")
GOVERNED_PROJECT_CONTROL_PREFIXES = (
    "AI_PROJECT/state/",
    "AI_PROJECT/events/",
    "AI_PROJECT/generated/",
)

CodexAdapter = Callable[..., CodexAdapterResult]


def execute_phase(
    session_id: str = "",
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    codex_adapter: CodexAdapter | None = None,
    execution_runner: OutputRunner | None = None,
) -> CommandResult:
    """Run the prepared Codex adapter without downstream pipeline gates."""

    root_path = Path(root).resolve()
    session_result = _resolve_session(root_path, session_id)
    if not session_result.ok:
        return session_result

    session = session_result.data["session"]
    selected_session_id = str(session.get("id") or "")
    prepare_result = _latest_prepare_result(session)
    if prepare_result is None:
        return _blocked(
            "PREPARE_PHASE_REQUIRED",
            "Prepare phase evidence is missing for this session.",
            session_id=selected_session_id,
            root=root_path,
            actor=actor,
            next_action="Run pipeline phase prepare before execute.",
        )

    prepare_artifacts = _mapping(
        prepare_result.get("artifacts"),
        default={},
    )
    artifact_check = _prepared_artifact_check(
        root_path,
        session,
        prepare_result,
        prepare_artifacts,
        actor=actor,
    )
    if artifact_check is not None:
        return artifact_check

    task_id = str(prepare_artifacts["task_id"])

    try:
        policy = PipelinePolicy.from_dict(
            _required_mapping(session.get("policy_snapshot"), "policy_snapshot")
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _failure(
            "PIPELINE_EXECUTE_POLICY_INVALID",
            "Session policy snapshot is invalid: {}".format(exc),
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
        )

    validation = policy.validate()
    if not validation.ok:
        return _blocked(
            "PIPELINE_EXECUTE_POLICY_INVALID",
            "Session policy does not pass validation.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                "policy": policy.name,
                "policy_errors": [
                    issue.to_message().to_dict() for issue in validation.errors
                ],
                "codex_adapter_called": False,
            },
            next_action="Fix or recreate the session with a valid pipeline policy.",
        )

    prompt_path = _artifact_path(root_path, prepare_artifacts["prompt_path"])
    prepared_sha256 = str(prepare_artifacts["prompt_sha256"])

    if policy.codex.mode != CodexExecutionMode.RUN_CODEX:
        return _blocked(
            "CODEX_EXECUTION_POLICY_DENIED",
            "Session policy does not allow Codex execution.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                "policy": policy.name,
                "codex_mode": policy.codex.mode.value,
                "prepare_artifacts": _bounded_prepare_artifacts(prepare_artifacts),
                "codex_adapter_called": False,
            },
            next_action=(
                "Select an executable policy or use the prepared prompt for manual "
                "execution outside this phase."
            ),
        )

    protected_check = _run_protected_freshness_check(
        root_path,
        runner=execution_runner,
    )
    if not protected_check["ok"]:
        return _blocked(
            PROTECTED_CHECK_FAILED,
            "Protected/generated freshness check failed before Codex execution.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                "policy": policy.name,
                "prepare_artifacts": _bounded_prepare_artifacts(prepare_artifacts),
                "protected_check": protected_check,
                "protected_check_command": protected_check["command"],
                "protected_check_returncode": protected_check["returncode"],
                "codex_adapter_called": False,
            },
            next_action=(
                "Refresh or repair protected generated outputs through the owning "
                "CLI, then rerun execute."
            ),
        )

    token_gate = evaluate_token_budget(
        root=root_path,
        policy=policy.token_budget,
        prompt_path=prompt_path,
        strict=True,
    )
    token_artifacts = {
        "policy": policy.name,
        "prepare_artifacts": _bounded_prepare_artifacts(prepare_artifacts),
        "token_budget": token_gate.to_dict(),
        "codex_adapter_called": False,
    }
    if token_gate.status != TOKEN_BUDGET_PASS:
        return _blocked(
            "TOKEN_BUDGET_FAILURE",
            "Token Budget Gate failed: {}".format(token_gate.reason),
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts=token_artifacts,
            next_action="Fix the prompt/context size or policy, then rerun execute.",
        )
    if token_gate.prompt_sha256 != prepared_sha256:
        return _blocked(
            "PREPARE_ARTIFACT_STALE",
            "Prepared prompt changed after the prepare phase.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                **token_artifacts,
                "expected_prompt_sha256": prepared_sha256,
                "actual_prompt_sha256": token_gate.prompt_sha256,
            },
            next_action="Rerun pipeline phase prepare, then execute again.",
        )

    running_record = _record_execute_running(
        session_id=selected_session_id,
        task_id=task_id,
        policy=policy,
        prepare_artifacts=prepare_artifacts,
        token_gate=token_gate,
        root=root_path,
        actor=actor,
    )
    if not running_record.ok:
        return running_record

    task = _task_by_id(load_reference_state(root_path).get("tasks"), task_id)
    before_file_snapshot = _capture_execute_file_snapshot(
        root_path,
        policy=policy,
        position="before",
    )
    adapter = codex_adapter or run_codex_adapter
    adapter_result = _call_codex_adapter(
        adapter,
        root=root_path,
        task_id=task_id,
        policy=policy,
        token_gate=token_gate,
        runner=execution_runner,
        session_id=selected_session_id,
    )
    execute_file_delta = _execute_file_delta_evidence(
        root=root_path,
        policy=policy,
        task=task,
        before=before_file_snapshot,
    )
    adapter_result = _adapter_result_with_enriched_report(
        adapter_result,
        root=root_path,
        task=task,
        task_id=task_id,
        execute_file_delta=execute_file_delta,
    )
    return _adapter_phase_result(
        adapter_result,
        session_id=selected_session_id,
        task_id=task_id,
        policy=policy,
        prepare_artifacts=prepare_artifacts,
        token_gate=token_gate,
        execute_file_delta=execute_file_delta,
        root=root_path,
        actor=actor,
    )


def _record_execute_running(
    *,
    session_id: str,
    task_id: str,
    policy: PipelinePolicy,
    prepare_artifacts: Mapping[str, Any],
    token_gate: TokenBudgetGateResult,
    root: Path,
    actor: str,
) -> CommandResult:
    started_at = utc_now()
    runtime_logs = _expected_runtime_logs(root, session_id, task_id)
    command_ref = _policy_command_ref(policy)
    adapter_mode = policy.codex.adapter_mode.value
    artifacts = {
        "session_id": session_id,
        "task_id": task_id,
        "policy": policy.name,
        "prepare_artifacts": _bounded_prepare_artifacts(prepare_artifacts),
        "token_budget": token_gate.to_dict(),
        "codex_adapter_called": True,
        "codex_adapter_active": True,
        "execute_started_at": started_at,
        "execute_finished_at": "",
        "runtime_logs": runtime_logs,
        "execute_evidence": {
            "status": "running",
            "code": "CODEX_ADAPTER_RUNNING",
            "reason": "codex_adapter_running",
            "adapter_mode": adapter_mode,
            "command_ref": command_ref,
            "returncode": None,
            "runtime_logs": runtime_logs,
            "started_at": started_at,
            "finished_at": "",
            "task_id": task_id,
            "session_id": session_id,
        },
        "adapter": {
            "status": "running",
            "mode": adapter_mode,
            "command": list(policy.codex.local_command),
            "command_ref": command_ref,
            "timeout_sec": policy.codex.timeout_sec,
            "runtime_logs": runtime_logs,
            "started_at": started_at,
            "finished_at": "",
        },
        "adapter_summary": {
            "status": "running",
            "code": "CODEX_ADAPTER_RUNNING",
            "reason": "codex_adapter_running",
            "command": list(policy.codex.local_command),
            "command_ref": command_ref,
            "returncode": None,
            "duration_sec": 0.0,
            "runtime_logs": runtime_logs,
        },
    }
    return record_phase_result(
        session_id,
        {
            "phase": PHASE_NAME,
            "status": "running",
            "reason": "Codex execution adapter is running.",
            "next_action": "Wait for Codex execution adapter completion.",
            "artifacts": artifacts,
            "changed_files": [],
            "generated_files": [],
            "events": [],
        },
        root=root,
        actor=actor,
        task_id=task_id,
        current_step_name=LIVE_EXECUTE_STEP_NAME,
        command=COMMAND_NAME,
    )


def _call_codex_adapter(adapter: CodexAdapter, **kwargs: Any) -> CodexAdapterResult:
    if _callable_accepts_keyword(adapter, "session_id"):
        return adapter(**kwargs)
    legacy_kwargs = dict(kwargs)
    legacy_kwargs.pop("session_id", None)
    return adapter(**legacy_kwargs)


def _callable_accepts_keyword(callback: Callable[..., Any], keyword: str) -> bool:
    try:
        signature = inspect.signature(callback)
    except (TypeError, ValueError):
        return True
    for parameter in signature.parameters.values():
        if parameter.kind == inspect.Parameter.VAR_KEYWORD:
            return True
        if (
            parameter.kind
            in {
                inspect.Parameter.KEYWORD_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            }
            and parameter.name == keyword
        ):
            return True
    return False


def _capture_execute_file_snapshot(
    root: Path,
    *,
    policy: PipelinePolicy,
    position: str,
) -> tuple[GitStatusSnapshot | None, dict[str, Any]]:
    if policy.codex.adapter_mode != CodexAdapterMode.LOCAL_COMMAND:
        return (
            None,
            {
                "ok": False,
                "status": "skipped",
                "code": EXECUTE_FILE_DELTA_SKIPPED,
                "reason": "adapter_mode_is_not_local_command",
                "position": position,
                "entries": [],
                "dirty_paths": [],
            },
        )
    try:
        snapshot = capture_git_status_snapshot(root=root)
    except GitStatusError as exc:
        return (
            None,
            {
                "ok": False,
                "status": "unavailable",
                "code": EXECUTE_FILE_DELTA_UNAVAILABLE,
                "reason": str(exc),
                "position": position,
                "entries": [],
                "dirty_paths": [],
            },
        )
    return (
        snapshot,
        {
            "ok": True,
            "status": "captured",
            "code": EXECUTE_FILE_DELTA_CAPTURED,
            "reason": "git_status_snapshot_captured",
            "position": position,
            **snapshot.to_dict(),
        },
    )


def _execute_file_delta_evidence(
    *,
    root: Path,
    policy: PipelinePolicy,
    task: Mapping[str, Any],
    before: tuple[GitStatusSnapshot | None, Mapping[str, Any]],
) -> dict[str, Any]:
    before_snapshot, before_evidence = before
    after_snapshot, after_evidence = _capture_execute_file_snapshot(
        root,
        policy=policy,
        position="after",
    )
    allowed_files = _task_allowed_files(task)
    base = {
        "capture_enabled": policy.codex.adapter_mode == CodexAdapterMode.LOCAL_COMMAND,
        "adapter_mode": policy.codex.adapter_mode.value,
        "before": dict(before_evidence),
        "after": dict(after_evidence),
        "allowed_files": list(allowed_files),
        "allowed_patterns": [],
        "changed_paths": [],
        "allowed_changed_files": [],
        "out_of_scope_changed_files": [],
        "ignored_changed_files": [],
        "governed_project_control_files": [],
    }
    if policy.codex.adapter_mode != CodexAdapterMode.LOCAL_COMMAND:
        return {
            **base,
            "status": "skipped",
            "code": EXECUTE_FILE_DELTA_SKIPPED,
            "reason": "adapter_mode_is_not_local_command",
        }
    if before_snapshot is None or after_snapshot is None:
        return {
            **base,
            "status": "unavailable",
            "code": EXECUTE_FILE_DELTA_UNAVAILABLE,
            "reason": "git_status_snapshot_unavailable",
        }

    changed_paths = dirty_paths_after_baseline(before_snapshot, after_snapshot)
    runtime_ignored = [
        path for path in changed_paths if _is_ignored_execute_file_path(path)
    ]
    runtime_ignored_set = set(runtime_ignored)
    candidate_paths = [
        path for path in changed_paths if path not in runtime_ignored_set
    ]
    filtered = filter_paths_by_allowed_files(
        candidate_paths,
        allowed_files,
        root=root,
    )
    governed_unallowed = [
        path
        for path in filtered.out_of_scope_paths
        if _is_governed_project_control_path(path)
    ]
    governed_unallowed_set = set(governed_unallowed)
    out_of_scope = [
        path
        for path in filtered.out_of_scope_paths
        if path not in governed_unallowed_set
    ]
    ignored = _unique_strings([*runtime_ignored, *governed_unallowed])
    return {
        **base,
        "status": "captured",
        "code": EXECUTE_FILE_DELTA_CAPTURED,
        "reason": "git_status_delta_captured",
        "allowed_patterns": list(filtered.allowed_patterns),
        "changed_paths": list(changed_paths),
        "allowed_changed_files": list(filtered.allowed_paths),
        "out_of_scope_changed_files": list(out_of_scope),
        "ignored_changed_files": ignored,
        "governed_project_control_files": list(governed_unallowed),
    }


def _adapter_result_with_enriched_report(
    adapter_result: CodexAdapterResult,
    *,
    root: Path,
    task: Mapping[str, Any],
    task_id: str,
    execute_file_delta: Mapping[str, Any],
) -> CodexAdapterResult:
    changed_files = _string_sequence(execute_file_delta.get("allowed_changed_files"))
    out_of_scope_files = _string_sequence(
        execute_file_delta.get("out_of_scope_changed_files")
    )
    if not changed_files and not out_of_scope_files:
        return adapter_result
    report_id = adapter_result.report_id or adapter_result.after_report_id
    if not report_id:
        return adapter_result

    refs = load_reference_state(root)
    tasks_state = refs.get("tasks")
    if not isinstance(tasks_state, Mapping):
        return _report_enrichment_blocked(
            adapter_result,
            "TASKS_STATE_MISSING",
            "tasks_state_unavailable",
            execute_file_delta=execute_file_delta,
        )
    selected_task = task if task else _task_by_id(tasks_state, task_id)
    if not selected_task:
        return _report_enrichment_blocked(
            adapter_result,
            "TASK_STATE_MISSING",
            "task_state_unavailable",
            execute_file_delta=execute_file_delta,
        )

    record = _report_record_by_id(refs.get("task_reports"), report_id)
    report = _report_from_record(record)
    if not report:
        return _report_enrichment_blocked(
            adapter_result,
            "REPORT_RECORD_MISSING",
            "report_record_unavailable",
            execute_file_delta=execute_file_delta,
        )

    payload = report_payload_with_captured_changed_files(
        report,
        changed_files=changed_files,
        out_of_scope_files=out_of_scope_files,
    )
    if payload == report:
        return adapter_result

    try:
        submission = task_report_service.submit_task_report(
            root=root,
            tasks_state=tasks_state,
            task=selected_task,
            report_payload=payload,
            source_file="captured:execute-file-delta:{}".format(report_id),
            actor="codex",
            command="codex_adapter.report.enrich_execute_delta",
        )
    except task_report_service.TaskReportError as exc:
        return _report_enrichment_blocked(
            adapter_result,
            "REPORT_ENRICHMENT_FAILED",
            str(exc),
            execute_file_delta=execute_file_delta,
        )

    builder_evidence = dict(adapter_result.report_builder_evidence)
    builder_evidence["execute_file_delta"] = {
        "source_report_id": report_id,
        "enriched_report_id": submission.report_id,
        "allowed_changed_files": list(changed_files),
        "out_of_scope_changed_files": list(out_of_scope_files),
    }
    builder_evidence["built_report_id"] = submission.report_id
    builder_evidence["changed_files_count"] = len(payload.get("changed_files") or [])
    return replace(
        adapter_result,
        after_report_id=submission.report_id,
        report_id=submission.report_id,
        report_builder_evidence=builder_evidence,
    )


def _report_enrichment_blocked(
    adapter_result: CodexAdapterResult,
    code: str,
    reason: str,
    *,
    execute_file_delta: Mapping[str, Any],
) -> CodexAdapterResult:
    builder_evidence = dict(adapter_result.report_builder_evidence)
    builder_evidence["execute_file_delta"] = dict(execute_file_delta)
    builder_evidence["report_enrichment_error"] = {
        "code": code,
        "reason": reason,
    }
    return replace(
        adapter_result,
        status="blocked",
        code=CODE_REPORT_INVALID,
        reason="execute_file_delta_report_enrichment_failed",
        report_submission_error=reason,
        report_builder_evidence=builder_evidence,
    )


def _adapter_phase_result(
    adapter_result: CodexAdapterResult,
    *,
    session_id: str,
    task_id: str,
    policy: PipelinePolicy,
    prepare_artifacts: Mapping[str, Any],
    token_gate: TokenBudgetGateResult,
    execute_file_delta: Mapping[str, Any],
    root: Path,
    actor: str,
) -> CommandResult:
    adapter_data = adapter_result.to_dict()
    if adapter_result.code == CODE_MANUAL_HANDOFF:
        prompt_path = _manual_prompt_path(root, adapter_result, prepare_artifacts)
        report_command = _report_submission_command(task_id)
        next_action = _manual_handoff_next_action(prompt_path, report_command)
        adapter_data["report_instruction"] = next_action
        artifacts = _adapter_artifacts(
            adapter_result,
            adapter_data=adapter_data,
            session_id=session_id,
            task_id=task_id,
            policy=policy,
            prepare_artifacts=prepare_artifacts,
            token_gate=token_gate,
            execute_file_delta=execute_file_delta,
        )
        phase = PhaseResult.blocked(
            PHASE_NAME,
            reason=_adapter_phase_reason(
                "Manual Codex handoff is required.",
                adapter_result,
            ),
            next_action=next_action,
            artifacts={
                "blocked_by": "MANUAL_HANDOFF_REQUIRED",
                "prompt_path": prompt_path,
                "prompt_sha256": adapter_result.prompt_sha256
                or token_gate.prompt_sha256,
                "manual_handoff_instruction": (
                    "Run Codex manually with the prompt at {}."
                ).format(prompt_path),
                "report_submission_command": report_command,
                "report_submission_instruction": (
                    "After Codex finishes, submit the structured execution "
                    "report with: {}"
                ).format(report_command),
                **artifacts,
            },
        )
        return _phase_command(
            phase,
            session_id=session_id,
            task_id=task_id,
            root=root,
            actor=actor,
        )

    artifacts = _adapter_artifacts(
        adapter_result,
        adapter_data=adapter_data,
        session_id=session_id,
        task_id=task_id,
        policy=policy,
        prepare_artifacts=prepare_artifacts,
        token_gate=token_gate,
        execute_file_delta=execute_file_delta,
    )
    if adapter_result.status == "passed":
        phase = PhaseResult.passed(
            PHASE_NAME,
            reason=_adapter_phase_reason(
                "Codex execution adapter passed.",
                adapter_result,
            ),
            next_action="Run pipeline phase collect-report.",
            artifacts=artifacts,
        )
    elif (
        adapter_result.status == "blocked"
        and adapter_result.code == CODE_REPORT_MISSING
        and adapter_result.returncode == 0
    ):
        phase = PhaseResult.passed(
            PHASE_NAME,
            reason=(
                _adapter_phase_reason(
                    "Codex execution adapter completed; structured report "
                    "collection is pending.",
                    adapter_result,
                )
            ),
            next_action="Run pipeline phase collect-report.",
            artifacts=artifacts,
        )
    elif adapter_result.status == "blocked":
        phase = PhaseResult.blocked(
            PHASE_NAME,
            reason=_adapter_phase_reason(
                "Codex execution adapter blocked: {}".format(
                    adapter_result.reason
                ),
                adapter_result,
            ),
            next_action=adapter_result.report_instruction
            or "Resolve the adapter blocker, then rerun execute.",
            artifacts={"blocked_by": adapter_result.code, **artifacts},
        )
    else:
        phase = PhaseResult.failed(
            PHASE_NAME,
            reason=_adapter_phase_reason(
                "Codex execution adapter failed: {}".format(adapter_result.reason),
                adapter_result,
            ),
            next_action=adapter_result.report_instruction
            or "Fix the adapter failure, then rerun execute.",
            artifacts={"error_code": adapter_result.code, **artifacts},
        )
    return _phase_command(
        phase,
        session_id=session_id,
        task_id=task_id,
        root=root,
        actor=actor,
    )


def _adapter_artifacts(
    adapter_result: CodexAdapterResult,
    *,
    adapter_data: Mapping[str, Any],
    session_id: str,
    task_id: str,
    policy: PipelinePolicy,
    prepare_artifacts: Mapping[str, Any],
    token_gate: TokenBudgetGateResult,
    execute_file_delta: Mapping[str, Any],
) -> dict[str, Any]:
    artifacts = {
        "session_id": session_id,
        "task_id": task_id,
        "policy": policy.name,
        "prepare_artifacts": _bounded_prepare_artifacts(prepare_artifacts),
        "token_budget": token_gate.to_dict(),
        "codex_adapter_called": True,
        "execute_started_at": adapter_result.started_at,
        "execute_finished_at": adapter_result.finished_at,
        "before_report_id": adapter_result.before_report_id,
        "after_report_id": adapter_result.after_report_id,
        "report_id": adapter_result.report_id,
        "execute_file_delta": dict(execute_file_delta),
        "execute_evidence": _adapter_evidence(
            adapter_result,
            execute_file_delta=execute_file_delta,
        ),
        "runtime_logs": dict(adapter_result.runtime_logs),
        "adapter": adapter_data,
        "adapter_summary": {
            "status": adapter_result.status,
            "code": adapter_result.code,
            "reason": adapter_result.reason,
            "command": list(adapter_result.command),
            "command_ref": adapter_result.command_ref,
            "returncode": adapter_result.returncode,
            "duration_sec": adapter_result.duration_sec,
            "stdout_ref": adapter_result.stdout_ref,
            "stderr_ref": adapter_result.stderr_ref,
            "stdout_snippet": adapter_result.stdout_snippet,
            "stderr_snippet": adapter_result.stderr_snippet,
            "stdout_bytes": adapter_result.stdout_bytes,
            "stderr_bytes": adapter_result.stderr_bytes,
            "runtime_logs": dict(adapter_result.runtime_logs),
            "report_required": adapter_result.report_required,
            "before_report_id": adapter_result.before_report_id,
            "after_report_id": adapter_result.after_report_id,
            "report_id": adapter_result.report_id,
            "report_ids": _adapter_report_ids(adapter_result),
            "execute_file_delta": dict(execute_file_delta),
        },
    }
    return artifacts


def _adapter_evidence(
    adapter_result: CodexAdapterResult,
    *,
    execute_file_delta: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "status": adapter_result.status,
        "code": adapter_result.code,
        "reason": adapter_result.reason,
        "command_ref": adapter_result.command_ref,
        "returncode": adapter_result.returncode,
        "duration_sec": adapter_result.duration_sec,
        "stdout_ref": adapter_result.stdout_ref,
        "stderr_ref": adapter_result.stderr_ref,
        "stdout_snippet": adapter_result.stdout_snippet,
        "stderr_snippet": adapter_result.stderr_snippet,
        "stdout_bytes": adapter_result.stdout_bytes,
        "stderr_bytes": adapter_result.stderr_bytes,
        "runtime_logs": dict(adapter_result.runtime_logs),
        "report_ids": _adapter_report_ids(adapter_result),
        "report_required": adapter_result.report_required,
        "started_at": adapter_result.started_at,
        "finished_at": adapter_result.finished_at,
        "before_report_id": adapter_result.before_report_id,
        "after_report_id": adapter_result.after_report_id,
        "report_id": adapter_result.report_id,
        "execute_file_delta": dict(execute_file_delta),
    }


def _adapter_report_ids(adapter_result: CodexAdapterResult) -> list[str]:
    result: list[str] = []
    for value in (
        adapter_result.before_report_id,
        adapter_result.after_report_id,
        adapter_result.report_id,
    ):
        text = str(value or "")
        if text and text not in result:
            result.append(text)
    return result


def _adapter_phase_reason(prefix: str, adapter_result: CodexAdapterResult) -> str:
    details = [
        "status={}".format(adapter_result.status),
        "code={}".format(adapter_result.code),
        "returncode={}".format(
            adapter_result.returncode
            if adapter_result.returncode is not None
            else "none"
        ),
    ]
    return "{} ({})".format(prefix, ", ".join(details))


def _run_protected_freshness_check(
    root: Path,
    *,
    runner: OutputRunner | None,
) -> dict[str, Any]:
    command = _protected_check_command(root)
    started = time.monotonic()
    try:
        if runner is not None:
            completed = runner(tuple(command))
        else:
            completed = subprocess.run(
                command,
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=PROTECTED_CHECK_TIMEOUT_SEC,
                check=False,
            )
    except subprocess.TimeoutExpired as exc:
        return _protected_check_result(
            command,
            returncode=None,
            duration_sec=_elapsed(started),
            stdout=_coerce_text(exc.stdout),
            stderr=_coerce_text(exc.stderr),
            code="PROTECTED_CHECK_TIMEOUT",
            reason="protected_check_timed_out",
        )
    except OSError as exc:
        return _protected_check_result(
            command,
            returncode=None,
            duration_sec=_elapsed(started),
            stdout="",
            stderr=str(exc),
            code="PROTECTED_CHECK_ERROR",
            reason="protected_check_error",
        )

    return _protected_check_result(
        command,
        returncode=int(completed.returncode),
        duration_sec=_elapsed(started),
        stdout=_coerce_text(completed.stdout),
        stderr=_coerce_text(completed.stderr),
        code=(
            "PROTECTED_CHECK_PASS"
            if int(completed.returncode) == 0
            else "PROTECTED_CHECK_FAILED"
        ),
        reason=(
            "protected_check_passed"
            if int(completed.returncode) == 0
            else "protected_check_failed"
        ),
    )


def _protected_check_command(root: Path) -> list[str]:
    return [
        sys.executable,
        str(root / "scripts" / "aictl.py"),
        "--root",
        str(root),
        "--json",
        "project",
        "protected-check",
    ]


def _protected_check_result(
    command: list[str],
    *,
    returncode: int | None,
    duration_sec: float,
    stdout: str,
    stderr: str,
    code: str,
    reason: str,
) -> dict[str, Any]:
    parsed = _parse_protected_check_payload(stdout)
    errors = _limited_strings(parsed.get("errors") if parsed else ())
    warnings = _limited_strings(parsed.get("warnings") if parsed else ())
    checked = _limited_strings(parsed.get("checked") if parsed else ())
    return {
        "ok": returncode == 0,
        "status": "pass" if returncode == 0 else "fail",
        "code": code,
        "reason": reason,
        "command": list(command),
        "returncode": returncode,
        "duration_sec": duration_sec,
        "stdout_summary": _bounded_text(stdout),
        "stderr_summary": _bounded_text(stderr),
        "stdout_bytes": _byte_len(stdout),
        "stderr_bytes": _byte_len(stderr),
        "stdout_truncated": len(stdout) > PROTECTED_CHECK_TEXT_LIMIT,
        "stderr_truncated": len(stderr) > PROTECTED_CHECK_TEXT_LIMIT,
        "errors": errors,
        "warnings": warnings,
        "checked": checked,
        "error_count": _list_count(parsed.get("errors") if parsed else ()),
        "warning_count": _list_count(parsed.get("warnings") if parsed else ()),
        "checked_count": _list_count(parsed.get("checked") if parsed else ()),
    }


def _parse_protected_check_payload(stdout: str) -> Mapping[str, Any]:
    try:
        parsed = json.loads(stdout)
    except (TypeError, json.JSONDecodeError):
        return {}
    if not isinstance(parsed, Mapping):
        return {}
    data = parsed.get("data")
    if isinstance(data, Mapping):
        delegated = data.get("result")
        if isinstance(delegated, Mapping):
            return delegated
    return parsed


def _limited_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value[:PROTECTED_CHECK_ITEMS_LIMIT]:
        result.append(_bounded_text(str(item)))
    return result


def _list_count(value: Any) -> int:
    return len(value) if isinstance(value, list) else 0


def _bounded_text(value: str) -> str:
    text = str(value or "").strip()
    if len(text) <= PROTECTED_CHECK_TEXT_LIMIT:
        return text
    return text[:PROTECTED_CHECK_TEXT_LIMIT] + "...[truncated]"


def _byte_len(value: str) -> int:
    return len(str(value or "").encode("utf-8"))


def _elapsed(started: float) -> float:
    return round(max(0.0, time.monotonic() - started), 6)


def _coerce_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _manual_prompt_path(
    root: Path,
    adapter_result: CodexAdapterResult,
    prepare_artifacts: Mapping[str, Any],
) -> str:
    prompt_value = adapter_result.prompt_path or str(
        prepare_artifacts.get("prompt_path") or ""
    )
    if not prompt_value:
        return ""
    return _repo_path(root, _artifact_path(root, prompt_value))


def _report_submission_command(task_id: str) -> str:
    return (
        "python scripts/aictl.py task report submit "
        "--task {} --file <REPORT.json> --confirm"
    ).format(task_id)


def _manual_handoff_next_action(prompt_path: str, report_command: str) -> str:
    return (
        "Run Codex manually with the prompt at {}, then submit the structured "
        "execution report: {}"
    ).format(prompt_path, report_command)


def _prepared_artifact_check(
    root: Path,
    session: Mapping[str, Any],
    prepare_result: Mapping[str, Any],
    artifacts: Mapping[str, Any],
    actor: str,
) -> CommandResult | None:
    session_id = str(session.get("id") or "")
    if str(prepare_result.get("status") or "") != "passed":
        return _blocked(
            "PREPARE_PHASE_NOT_PASSED",
            "Latest prepare phase did not pass.",
            session_id=session_id,
            root=root,
            actor=actor,
            artifacts={
                "prepare_status": str(prepare_result.get("status") or ""),
                "prepare_reason": str(prepare_result.get("reason") or ""),
                "codex_adapter_called": False,
            },
            next_action="Rerun pipeline phase prepare until it passes.",
        )

    missing = [
        field
        for field in ("task_id", "prompt_path", "prompt_sha256")
        if not str(artifacts.get(field) or "").strip()
    ]
    if missing:
        return _blocked(
            "PREPARE_ARTIFACT_MISSING",
            "Prepare phase evidence is missing required field(s): {}".format(
                ", ".join(missing)
            ),
            session_id=session_id,
            root=root,
            actor=actor,
            artifacts={"missing": missing, "codex_adapter_called": False},
            next_action="Rerun pipeline phase prepare to refresh artifact evidence.",
        )

    task_id = str(artifacts["task_id"])
    session_task_id = str(session.get("current_task_id") or "")
    if session_task_id and session_task_id != task_id:
        return _blocked(
            "PREPARE_ARTIFACT_TASK_MISMATCH",
            "Prepare evidence does not match the session current task.",
            session_id=session_id,
            task_id=task_id,
            root=root,
            actor=actor,
            artifacts={
                "session_task_id": session_task_id,
                "prepared_task_id": task_id,
                "codex_adapter_called": False,
            },
            next_action="Rerun pipeline phase prepare for the selected session task.",
        )

    prompt_path = _artifact_path(root, artifacts["prompt_path"])
    if not prompt_path.exists():
        return _blocked(
            "PREPARE_PROMPT_MISSING",
            "Prepared prompt file is missing.",
            session_id=session_id,
            task_id=task_id,
            root=root,
            actor=actor,
            artifacts={
                "prompt_path": _repo_path(root, prompt_path),
                "codex_adapter_called": False,
            },
            next_action="Rerun pipeline phase prepare to rebuild the prompt.",
        )

    actual_sha256 = _sha256(prompt_path)
    expected_sha256 = str(artifacts["prompt_sha256"])
    if actual_sha256 != expected_sha256:
        return _blocked(
            "PREPARE_ARTIFACT_STALE",
            "Prepared prompt checksum no longer matches the prompt file.",
            session_id=session_id,
            task_id=task_id,
            root=root,
            actor=actor,
            artifacts={
                "prompt_path": _repo_path(root, prompt_path),
                "expected_prompt_sha256": expected_sha256,
                "actual_prompt_sha256": actual_sha256,
                "codex_adapter_called": False,
            },
            next_action="Rerun pipeline phase prepare, then execute again.",
        )
    return None


def _resolve_session(root: Path, session_id: str) -> CommandResult:
    state = load_pipeline_state(root)
    selected_id = session_id.strip() or str(state.get("current_session_id") or "")
    if not selected_id:
        return _failure(
            "PIPELINE_SESSION_REQUIRED",
            "Pass a session id or set a current pipeline session before execute.",
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


def _latest_prepare_result(session: Mapping[str, Any]) -> Mapping[str, Any] | None:
    history = session.get("phase_history")
    if not isinstance(history, list):
        return None
    for entry in reversed(history):
        if (
            isinstance(entry, Mapping)
            and str(entry.get("phase") or "") == PREPARE_PHASE_NAME
        ):
            return entry
    return None


def _phase_command(
    phase: PhaseResult,
    *,
    session_id: str,
    task_id: str = "",
    root: Path | None = None,
    actor: str = "human_owner",
) -> CommandResult:
    if root is not None and session_id:
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
        return result

    result = CommandResult.success(
        command=COMMAND_NAME,
        domain="pipeline",
        message=phase.reason,
        data={
            "phase_result": phase.to_dict(),
            "session_id": session_id,
            "task_id": task_id,
        },
    )
    if phase.status.value == "failed":
        result.ok = False
    if phase.next_action:
        result.next_actions.append(phase.next_action)
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
    session_id: str = "",
    task_id: str = "",
    root: Path | None = None,
    actor: str = "human_owner",
) -> CommandResult:
    phase = PhaseResult.failed(
        PHASE_NAME,
        reason=message,
        next_action="Fix the execute input and rerun the phase.",
        artifacts={"error_code": code, **dict(details or {})},
    )
    if root is not None and session_id:
        result = _phase_command(
            phase,
            session_id=session_id,
            task_id=task_id,
            root=root,
            actor=actor,
        )
        result.ok = False
        result.errors.append(
            CommandMessage(code, message, details=dict(details or {}))
        )
        return result

    result = CommandResult.failure(
        command=COMMAND_NAME,
        domain="pipeline",
        message=message,
        errors=[CommandMessage(code, message, details=dict(details or {}))],
    )
    result.data = {"phase_result": phase.to_dict()}
    if session_id:
        result.data["session_id"] = session_id
    return result


def _bounded_prepare_artifacts(artifacts: Mapping[str, Any]) -> dict[str, Any]:
    allowed = ("task_id", "context_pack_path", "prompt_path", "prompt_sha256")
    return {key: artifacts[key] for key in allowed if key in artifacts}


def _expected_runtime_logs(root: Path, session_id: str, task_id: str) -> dict[str, Any]:
    stdout_path, stderr_path = _runtime_log_paths(root, session_id, task_id)
    return {
        "stdout": _runtime_log_stream_metadata(root, stdout_path),
        "stderr": _runtime_log_stream_metadata(root, stderr_path),
    }


def _runtime_log_stream_metadata(root: Path, path: Path) -> dict[str, Any]:
    start_offset = _file_size(path)
    return {
        "path": _repo_path(root, path),
        "start_offset": start_offset,
        "end_offset": start_offset,
        "bytes": 0,
    }


def _runtime_log_paths(root: Path, session_id: str, task_id: str) -> tuple[Path, Path]:
    session_segment = _safe_log_segment(session_id) if session_id else "no-session"
    task_segment = _safe_log_segment(task_id) if task_id else "unknown-task"
    directory = root / "AI_PROJECT" / "logs" / "codex" / session_segment
    return (
        directory / "{}-stdout.log".format(task_segment),
        directory / "{}-stderr.log".format(task_segment),
    )


def _safe_log_segment(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    cleaned = cleaned.strip(".-")
    return cleaned or "unknown"


def _file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except FileNotFoundError:
        return 0


def _policy_command_ref(policy: PipelinePolicy) -> str:
    command = tuple(str(part) for part in policy.codex.local_command)
    return shlex.join(command) if command else policy.codex.adapter_mode.value


def _required_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    raise TypeError("{} must be a mapping".format(name))


def _mapping(value: Any, *, default: Mapping[str, Any]) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else default


def _task_by_id(tasks_state: Any, task_id: str) -> Mapping[str, Any]:
    if not isinstance(tasks_state, Mapping):
        return {}
    for task in tasks_state.get("tasks", []):
        if isinstance(task, Mapping) and str(task.get("id") or "") == task_id:
            return task
    return {}


def _task_allowed_files(task: Mapping[str, Any]) -> tuple[str, ...]:
    values = task.get("allowed_files")
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes, bytearray)):
        return ()
    return tuple(_unique_strings(values))


def _report_record_by_id(report_state: Any, report_id: str) -> Mapping[str, Any]:
    if not isinstance(report_state, Mapping):
        return {}
    reports = report_state.get("reports")
    if not isinstance(reports, list):
        return {}
    for record in reports:
        if isinstance(record, Mapping) and str(record.get("id") or "") == report_id:
            return record
    return {}


def _report_from_record(record: Mapping[str, Any]) -> Mapping[str, Any]:
    report = record.get("report") if isinstance(record, Mapping) else None
    return report if isinstance(report, Mapping) else {}


def _is_ignored_execute_file_path(path: str) -> bool:
    return str(path).startswith(IGNORED_EXECUTE_FILE_PREFIXES)


def _is_governed_project_control_path(path: str) -> bool:
    return str(path).startswith(GOVERNED_PROJECT_CONTROL_PREFIXES)


def _string_sequence(value: Any) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    return tuple(_unique_strings(value))


def _unique_strings(values: Sequence[Any]) -> list[str]:
    result: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in result:
            result.append(text)
    return result


def _artifact_path(root: Path, value: Any) -> Path:
    path = Path(str(value))
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def _repo_path(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


__all__ = ["execute_phase"]

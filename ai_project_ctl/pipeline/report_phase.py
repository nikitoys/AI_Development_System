"""Pipeline collect-report phase service.

The collect-report phase records whether a structured execution report exists
for the current pipeline task. It deliberately does not run report schema
validation, project tests, or downstream verification gates.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from ai_project_ctl.core.result import CommandMessage, CommandResult
from ai_project_ctl.core.store import StoreError, read_json_file

from .phase import PhaseResult
from .session import record_phase_result
from .state import load_pipeline_state, pipeline_state_path, task_reports_state_path


COMMAND_NAME = "pipeline.phase.collect_report"
PHASE_NAME = "collect_report"
EXECUTE_PHASE_NAME = "execute"
REPORT_MISSING = "REPORT_MISSING"
REPORT_TASK_MISMATCH = "REPORT_TASK_MISMATCH"
REPORT_STALE = "REPORT_STALE"


def collect_report_phase(
    session_id: str = "",
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    allow_existing_report: bool = False,
) -> CommandResult:
    """Collect the latest structured report for the selected session task."""

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

    record_result = _latest_report_record(root_path, task_id)
    if isinstance(record_result, CommandResult):
        if not record_result.ok:
            return record_result
        phase = PhaseResult.blocked(
            PHASE_NAME,
            reason=record_result.message,
            next_action=_report_next_action(task_id),
            artifacts={
                "blocked_by": REPORT_MISSING,
                "session_id": selected_session_id,
                "task_id": task_id,
                **record_result.data,
            },
        )
        return _phase_command(
            phase,
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
        )

    record = record_result
    report_id = str(record.get("id") or "")
    report_task_id = str(record.get("task_id") or "")
    identity_evidence = _report_identity_evidence(
        record,
        expected_task_id=task_id,
        selected_task_ref=task_ref,
    )
    if report_task_id != task_id:
        return _blocked(
            REPORT_TASK_MISMATCH,
            "Latest report does not belong to the selected pipeline task.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                "session_id": selected_session_id,
                **identity_evidence,
            },
            next_action="Submit a report for the selected task, then rerun collect-report.",
        )

    report = record.get("report")
    if not isinstance(report, Mapping):
        return _blocked(
            REPORT_MISSING,
            "Latest task report record does not contain a structured report object.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                "session_id": selected_session_id,
                "task_id": task_id,
                "report_id": report_id,
                **identity_evidence,
            },
            next_action=_report_next_action(task_id),
        )

    identity_evidence = _report_identity_evidence(
        record,
        report=report,
        expected_task_id=task_id,
        selected_task_ref=task_ref,
    )
    mismatch_field = _report_identity_mismatch(
        identity_evidence,
        expected_task_id=task_id,
        selected_task_ref=task_ref,
    )
    if mismatch_field:
        return _blocked(
            REPORT_TASK_MISMATCH,
            "Structured report identity does not belong to the selected pipeline task.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                "session_id": selected_session_id,
                "identity_mismatch_field": mismatch_field,
                **identity_evidence,
            },
            next_action="Submit a report for the selected task, then rerun collect-report.",
        )

    freshness = _report_freshness(
        session,
        record,
        allow_existing_report=allow_existing_report,
    )
    if not bool(freshness.get("fresh")):
        return _blocked(
            REPORT_STALE,
            "Structured report is older than the current execute phase.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                "session_id": selected_session_id,
                **identity_evidence,
                "freshness": freshness,
            },
            next_action=(
                "Submit a fresh report for the current execute phase, then rerun "
                "collect-report. For supervised recovery only, rerun with "
                "--allow-existing-report."
            ),
        )

    phase = PhaseResult.passed(
        PHASE_NAME,
        reason=(
            "Structured execution report collected for selected task "
            "(freshness_basis={})."
        ).format(freshness.get("basis") or "unknown"),
        next_action="Run pipeline phase verify.",
        artifacts={
            "session_id": selected_session_id,
            "task_id": task_id,
            "report_id": report_id,
            "report_task_id": report_task_id,
            **identity_evidence,
            "submitted_at": str(record.get("submitted_at") or ""),
            "submitted_by": str(record.get("submitted_by") or ""),
            "source_file": str(record.get("source_file") or ""),
            "report_found": True,
            "freshness": freshness,
            "freshness_basis": str(freshness.get("basis") or ""),
            "allow_existing_report": allow_existing_report,
        },
    )
    return _phase_command(
        phase,
        session_id=selected_session_id,
        task_id=task_id,
        root=root_path,
        actor=actor,
    )


def _latest_report_record(root: Path, task_id: str) -> Mapping[str, Any] | CommandResult:
    path = task_reports_state_path(root)
    if not path.exists():
        return _missing(
            "No task report state exists for selected task.",
            task_id=task_id,
            details={"state_path": _repo_path(root, path)},
        )

    try:
        data = read_json_file(path)
    except StoreError as exc:
        return CommandResult.failure(
            command=COMMAND_NAME,
            domain="pipeline",
            message=exc.message,
            errors=[exc.to_message()],
        )

    if not isinstance(data, Mapping):
        return _invalid_state("Task report state is not an object.", task_id=task_id)

    reports = data.get("reports")
    if not isinstance(reports, list):
        return _invalid_state("task_reports.reports must be a list.", task_id=task_id)

    latest = data.get("latest_by_task")
    if isinstance(latest, Mapping):
        report_id = latest.get(task_id)
        if isinstance(report_id, str) and report_id.strip():
            record = _record_by_id(reports, report_id)
            if record is None:
                return _missing(
                    "latest_by_task points to a missing report: {}".format(report_id),
                    task_id=task_id,
                    details={"report_id": report_id},
                )
            return record

    matches = [
        record
        for record in reports
        if isinstance(record, Mapping) and record.get("task_id") == task_id
    ]
    if not matches:
        return _missing(
            "No structured execution report exists for selected task.",
            task_id=task_id,
        )
    matches.sort(key=lambda item: str(item.get("submitted_at") or ""))
    return matches[-1]


def _record_by_id(reports: list[Any], report_id: str) -> Mapping[str, Any] | None:
    for record in reports:
        if isinstance(record, Mapping) and record.get("id") == report_id:
            return record
    return None


def _report_identity_evidence(
    record: Mapping[str, Any],
    *,
    expected_task_id: str,
    selected_task_ref: str = "",
    report: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    evidence = {
        "expected_task_id": expected_task_id,
        "selected_task_ref": selected_task_ref,
        "report_id": str(record.get("id") or ""),
        "report_task_id": str(record.get("task_id") or ""),
        "record_task_id": str(record.get("task_id") or ""),
        "record_task_ref": str(record.get("task_ref") or ""),
        "observed_report_task_id": str(record.get("task_id") or ""),
    }
    if report is not None:
        structured_task_id = _identity_value(report.get("task_id"))
        evidence.update(
            {
                "structured_report_task_id": structured_task_id,
                "structured_report_task_ref": _identity_value(report.get("task_ref")),
                "reported_task_id": _identity_value(report.get("reported_task_id")),
                "reported_task_ref": _identity_value(report.get("reported_task_ref")),
                "observed_report_task_id": structured_task_id,
            }
        )
    return evidence


def _report_identity_mismatch(
    evidence: Mapping[str, str],
    *,
    expected_task_id: str,
    selected_task_ref: str = "",
) -> str:
    expected_refs = {expected_task_id}
    if selected_task_ref:
        expected_refs.add(selected_task_ref)

    structured_task_id = evidence.get("structured_report_task_id", "")
    if structured_task_id and structured_task_id != expected_task_id:
        return "task_id"

    reported_task_id = evidence.get("reported_task_id", "")
    if reported_task_id and reported_task_id not in expected_refs:
        return "reported_task_id"

    structured_task_ref = evidence.get("structured_report_task_ref", "")
    if (
        structured_task_ref
        and selected_task_ref
        and structured_task_ref != selected_task_ref
    ):
        return "task_ref"

    reported_task_ref = evidence.get("reported_task_ref", "")
    if (
        reported_task_ref
        and selected_task_ref
        and reported_task_ref not in expected_refs
    ):
        return "reported_task_ref"

    return ""


def _report_freshness(
    session: Mapping[str, Any],
    record: Mapping[str, Any],
    *,
    allow_existing_report: bool,
) -> dict[str, Any]:
    execute = _latest_execute_evidence(session)
    check = {
        "fresh": False,
        "basis": "",
        "reason": "",
        "allow_existing_report": allow_existing_report,
        "report_id": str(record.get("id") or ""),
        "report_submitted_at": str(record.get("submitted_at") or ""),
        "execute_started_at": str(execute.get("started_at") or ""),
        "execute_finished_at": str(execute.get("finished_at") or ""),
        "execute_before_report_id": str(execute.get("before_report_id") or ""),
        "execute_after_report_id": str(execute.get("after_report_id") or ""),
        "execute_report_id": str(execute.get("report_id") or ""),
        "execute_phase_status": str(execute.get("phase_status") or ""),
    }
    if allow_existing_report:
        check["fresh"] = True
        check["basis"] = "recovery_override"
        check["reason"] = "allow_existing_report override was explicitly used."
        return check

    report_id = check["report_id"]
    before_report_id = check["execute_before_report_id"]
    after_report_id = check["execute_after_report_id"]
    execute_report_id = check["execute_report_id"]

    if execute_report_id and report_id == execute_report_id:
        check["fresh"] = True
        check["basis"] = "report_id"
        check["reason"] = "Report id matches the report produced by execute."
        return check
    if (
        after_report_id
        and after_report_id != before_report_id
        and report_id == after_report_id
    ):
        check["fresh"] = True
        check["basis"] = "report_id"
        check["reason"] = "Report id changed during execute."
        return check
    if before_report_id and report_id == before_report_id:
        check["basis"] = "report_id"
        check["reason"] = "Report id was already present before execute."
        return check

    submitted_at = _parse_utc_instant(check["report_submitted_at"])
    execute_started_at = _parse_utc_instant(check["execute_started_at"])
    if submitted_at is not None and execute_started_at is not None:
        check["basis"] = "timestamp"
        if submitted_at >= execute_started_at:
            check["fresh"] = True
            check["reason"] = "Report timestamp is at or after execute start."
        else:
            check["reason"] = "Report timestamp predates execute start."
        return check

    if not check["execute_started_at"]:
        check["reason"] = "No execute phase evidence is available."
    elif not check["report_submitted_at"]:
        check["reason"] = "Report timestamp is missing."
    else:
        check["reason"] = (
            "Report or execute timestamp is not a timezone-aware ISO instant."
        )
    return check


def _latest_execute_evidence(session: Mapping[str, Any]) -> dict[str, Any]:
    history = session.get("phase_history")
    if not isinstance(history, list):
        return {}
    for entry in reversed(history):
        if not isinstance(entry, Mapping):
            continue
        if str(entry.get("phase") or "") != EXECUTE_PHASE_NAME:
            continue
        artifacts = entry.get("artifacts")
        if not isinstance(artifacts, Mapping):
            artifacts = {}
        evidence = artifacts.get("execute_evidence")
        if not isinstance(evidence, Mapping):
            evidence = {}
        adapter = artifacts.get("adapter")
        if not isinstance(adapter, Mapping):
            adapter = {}
        adapter_summary = artifacts.get("adapter_summary")
        if not isinstance(adapter_summary, Mapping):
            adapter_summary = {}
        return {
            "phase_status": str(entry.get("status") or ""),
            "started_at": _first_text(
                artifacts.get("execute_started_at"),
                evidence.get("started_at"),
                adapter.get("started_at"),
            ),
            "finished_at": _first_text(
                artifacts.get("execute_finished_at"),
                evidence.get("finished_at"),
                adapter.get("finished_at"),
            ),
            "before_report_id": _first_text(
                artifacts.get("before_report_id"),
                evidence.get("before_report_id"),
                adapter_summary.get("before_report_id"),
                adapter.get("before_report_id"),
            ),
            "after_report_id": _first_text(
                artifacts.get("after_report_id"),
                evidence.get("after_report_id"),
                adapter_summary.get("after_report_id"),
                adapter.get("after_report_id"),
            ),
            "report_id": _first_text(
                artifacts.get("report_id"),
                evidence.get("report_id"),
                adapter_summary.get("report_id"),
                adapter.get("report_id"),
            ),
        }
    return {}


def _first_text(*values: Any) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _parse_utc_instant(value: str) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = "{}+00:00".format(text[:-1])
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _identity_value(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _missing(
    message: str,
    *,
    task_id: str,
    details: Mapping[str, Any] | None = None,
) -> CommandResult:
    return CommandResult.success(
        command=COMMAND_NAME,
        domain="pipeline",
        message=message,
        data={"task_id": task_id, "report_id": "", **dict(details or {})},
    )


def _invalid_state(message: str, *, task_id: str) -> CommandResult:
    return CommandResult.failure(
        command=COMMAND_NAME,
        domain="pipeline",
        message=message,
        errors=[
            CommandMessage(
                "TASK_REPORT_STATE_INVALID",
                message,
                details={"task_id": task_id},
            )
        ],
    )


def _resolve_session(root: Path, session_id: str) -> CommandResult:
    state = load_pipeline_state(root)
    selected_id = session_id.strip() or str(state.get("current_session_id") or "")
    if not selected_id:
        return _failure(
            "PIPELINE_SESSION_REQUIRED",
            "Pass a session id or set a current pipeline session before collect-report.",
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
        data = result.data if isinstance(result.data, Mapping) else {}
        phase_result = data.get("phase_result") if isinstance(data, Mapping) else {}
        artifacts = (
            phase_result.get("artifacts")
            if isinstance(phase_result, Mapping)
            else {}
        )
        if isinstance(artifacts, Mapping):
            result.data["task_id"] = str(artifacts.get("task_id") or task_id)
            result.data["report_id"] = str(artifacts.get("report_id") or "")
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
) -> CommandResult:
    phase = PhaseResult.failed(
        PHASE_NAME,
        reason=message,
        next_action="Fix the collect-report input and rerun the phase.",
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


def _report_next_action(task_id: str) -> str:
    return (
        "Submit a structured execution report, then rerun collect-report: "
        "python scripts/aictl.py task report submit --task {} "
        "--file <REPORT.json> --confirm"
    ).format(task_id)


def _repo_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


__all__ = ["collect_report_phase"]

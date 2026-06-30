"""Draft and submit owner-confirmed recovered task reports."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from ai_project_ctl import task_reports as task_report_service
from ai_project_ctl.core.result import CommandMessage, CommandResult
from ai_project_ctl.core.store import StoreError, read_json_file

from .state import load_pipeline_state, tasks_state_path


COMMAND_NAME = "pipeline.report_recovery.submit"
REPORT_GATE_RECOVERY_COMMAND_NAME = "pipeline.report.recover"
REPORT_MISSING = "REPORT_MISSING"
CODEX_ADAPTER_REPORT_MISSING = "CODEX_ADAPTER_REPORT_MISSING"
CODEX_REPORT_BLOCKERS_PRESENT = "CODEX_REPORT_BLOCKERS_PRESENT"
CODEX_REPORT_BLOCKING_CHECK_FAILED = "CODEX_REPORT_BLOCKING_CHECK_FAILED"
CODEX_REPORT_TOKEN_USAGE_REQUIRED = "CODEX_REPORT_TOKEN_USAGE_REQUIRED"
CODEX_REPORT_OUT_OF_SCOPE_FILE = "CODEX_REPORT_OUT_OF_SCOPE_FILE"
CODEX_REPORT_TASK_MISMATCH = "CODEX_REPORT_TASK_MISMATCH"
REPORT_GATE_RECOVERY_BASIS = "report_gate_owner_triage"
REPORT_GATE_RECOVERY_TOKEN_STRATEGY = "report_gate_recovery_estimated_v1"
REPORT_GATE_RECOVERABLE_CODES = {
    CODEX_REPORT_BLOCKERS_PRESENT,
    CODEX_REPORT_BLOCKING_CHECK_FAILED,
    CODEX_REPORT_TOKEN_USAGE_REQUIRED,
}
REPORT_GATE_REFUSED_CODES = {
    CODEX_REPORT_OUT_OF_SCOPE_FILE,
    CODEX_REPORT_TASK_MISMATCH,
}
FAILED_CHECK_RESULTS = {"fail", "failed", "error"}
STDOUT_RECOVERY_LIMIT = 65_536
STDOUT_PREVIEW_LIMIT = 2_000
PATH_RE = re.compile(
    r"(?<![\w./-])([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+\."
    r"(?:py|md|json|yml|yaml|toml|txt|css|js|jsx|ts|tsx|html))"
)
TOKEN_RE = re.compile(
    r"(?i)\b(?:total[_ -]?tokens?|tokens used|token usage)\b[^0-9]{0,24}([0-9][0-9,_]*)"
)


class ReportRecoveryError(task_report_service.TaskReportError):
    """Stable report recovery error."""


@dataclass(frozen=True)
class RecoveryDraft:
    """Owner-reviewable draft report plus recovery evidence."""

    session_id: str
    task_id: str
    task_ref: str
    report: Mapping[str, Any]
    warnings: tuple[str, ...]
    inferred_fields: tuple[str, ...]
    evidence: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "task_id": self.task_id,
            "task_ref": self.task_ref,
            "report": dict(self.report),
            "warnings": list(self.warnings),
            "inferred_fields": list(self.inferred_fields),
            "evidence": dict(self.evidence),
        }


def session_supports_report_recovery(session: Mapping[str, Any]) -> bool:
    """Return whether a session is blocked on missing structured report evidence."""

    if str(session.get("blocked_by") or "") == REPORT_MISSING:
        return True
    if str(session.get("status") or "") not in {"blocked", "stopped", "failed"}:
        return False
    for phase in reversed(_phase_history(session)):
        artifacts = _mapping(phase.get("artifacts"))
        if str(artifacts.get("blocked_by") or "") == REPORT_MISSING:
            return True
        execute_evidence = _mapping(artifacts.get("execute_evidence"))
        adapter = _mapping(artifacts.get("adapter"))
        adapter_summary = _mapping(artifacts.get("adapter_summary"))
        for source in (execute_evidence, adapter, adapter_summary):
            if str(source.get("code") or "") == CODEX_ADAPTER_REPORT_MISSING:
                return True
    return False


def draft_report_from_session(
    session: Mapping[str, Any],
    task: Mapping[str, Any],
    *,
    root: str | Path | None = None,
) -> RecoveryDraft:
    """Build a cautious structured report draft from captured Codex evidence."""

    session_id = str(session.get("id") or "")
    task_id = str(task.get("id") or session.get("current_task_id") or "")
    task_ref = str(task.get("ref") or session.get("current_task_ref") or "")
    execute_phase = _latest_phase(session, "execute")
    artifacts = _mapping(execute_phase.get("artifacts"))
    stdout, source_file, stdout_ref = _captured_stdout(
        artifacts,
        root=Path(root).resolve() if root is not None else None,
    )
    inferred_fields: list[str] = []
    warnings: list[str] = [
        "Draft report was recovered from captured Codex output; owner review is required before relying on inferred fields.",
        "Free-text Codex output is not authoritative structured report evidence.",
    ]

    summary = _summary_from_stdout(stdout)
    if summary:
        inferred_fields.append("implementation_summary")
    else:
        summary = (
            "Recovered draft report for {} from captured Codex output. "
            "Owner must verify the implementation summary."
        ).format(task_ref or task_id)
        inferred_fields.append("implementation_summary")
        warnings.append("implementation_summary was generated because no clear summary was found in captured stdout.")

    changed_files = _report_files(
        stdout,
        section_names=("changed files", "changed_files", "files changed"),
        fallback=_collect_changed_files(execute_phase, artifacts),
    )
    generated_files = [
        item for item in changed_files if item.startswith("AI_PROJECT/generated/")
    ]
    changed_files = [
        item for item in changed_files if not item.startswith("AI_PROJECT/generated/")
    ]
    if changed_files:
        inferred_fields.append("changed_files")
        warnings.append("changed_files were inferred from captured stdout or session evidence.")
    else:
        warnings.append("changed_files could not be inferred from captured output.")

    checks = _checks_from_stdout(stdout)
    if checks:
        inferred_fields.append("checks")
        warnings.append("checks were inferred from captured stdout and should be verified by the owner.")
    else:
        checks = [
            {
                "name": "captured Codex output review",
                "result": "warn",
                "blocking": False,
                "details": "No structured check evidence was found; owner must inspect captured stdout.",
            }
        ]
        inferred_fields.append("checks")
        warnings.append("checks were not found in captured output; a warning check was added.")

    parsed_warnings = _section_items(stdout, ("warnings", "runtime warnings"))
    parsed_blockers = _section_items(stdout, ("blockers", "errors", "questions"))
    token_usage = _token_usage_from_stdout(stdout)
    inferred_fields.append("token_usage")
    warnings.append("token_usage is estimated because Codex did not submit a structured report.")

    report_warnings = _unique_strings([*parsed_warnings, *warnings])
    report = {
        "schema_version": task_report_service.TASK_REPORT_SCHEMA_VERSION,
        "task_id": task_id,
        "task_ref": task_ref,
        "implementation_summary": summary,
        "changed_files": changed_files,
        "generated_files": generated_files,
        "checks": checks,
        "warnings": report_warnings,
        "blockers": parsed_blockers,
        "notes": _recovery_notes(session_id, source_file, stdout_ref),
        "owner_decision_required": True,
        "token_usage": token_usage,
    }
    return RecoveryDraft(
        session_id=session_id,
        task_id=task_id,
        task_ref=task_ref,
        report=report,
        warnings=tuple(report_warnings),
        inferred_fields=tuple(_unique_strings(inferred_fields)),
        evidence={
            "source_file": source_file,
            "stdout_ref": stdout_ref,
            "stdout_preview": _bounded(stdout, STDOUT_PREVIEW_LIMIT),
        },
    )


def submit_recovered_report(
    session_id: str,
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    expected_task_id: str = "",
    expected_task_ref: str = "",
) -> CommandResult:
    """Submit an owner-confirmed recovered draft report for one pipeline session."""

    root_path = Path(root).resolve()
    session = _resolve_session(root_path, session_id)
    if not session_supports_report_recovery(session):
        raise ReportRecoveryError(
            "REPORT_RECOVERY_NOT_AVAILABLE: session is not blocked by REPORT_MISSING"
        )

    tasks_state = _load_tasks_state(root_path)
    task = _resolve_task_for_session(tasks_state, session)
    task_id = str(task.get("id") or "")
    task_ref = str(task.get("ref") or "")
    if expected_task_id and expected_task_id != task_id:
        raise ReportRecoveryError(
            "REPORT_RECOVERY_TASK_MISMATCH: expected task_id {} but session selected {}".format(
                expected_task_id,
                task_id,
            )
        )
    if expected_task_ref and expected_task_ref not in _task_reference_values(task):
        raise ReportRecoveryError(
            "REPORT_RECOVERY_TASK_MISMATCH: expected task_ref {} does not match selected task".format(
                expected_task_ref
            )
        )

    draft = draft_report_from_session(session, task, root=root_path)
    submission = task_report_service.submit_task_report(
        root=root_path,
        tasks_state=tasks_state,
        task=task,
        report_payload=draft.report,
        source_file=str(draft.evidence.get("source_file") or ""),
        actor=actor,
        command=COMMAND_NAME,
    )
    result = CommandResult.success(
        command=COMMAND_NAME,
        domain="pipeline",
        message="OK: submitted recovered draft report {}".format(submission.report_id),
        data={
            "session_id": str(session.get("id") or ""),
            "task_id": task_id,
            "task_ref": task_ref,
            "report_id": submission.report_id,
            "draft_report": draft.to_dict(),
            "source_file": submission.source_file,
            "event_id": submission.event_id,
        },
        revision_before=submission.revision_before,
        revision_after=submission.revision_after,
    )
    result.changed_files.append(submission.state_path)
    result.events.append(submission.event_id)
    result.owner_action_required = (
        "Rerun collect-report for session {}; then run verify if collect-report passes."
    ).format(str(session.get("id") or ""))
    result.next_actions.extend(
        [
            "Rerun collect-report for session {}.".format(str(session.get("id") or "")),
            "Do not skip verify after collect-report passes.",
        ]
    )
    for warning in draft.warnings:
        result.warnings.append(
            CommandMessage(
                code="REPORT_RECOVERY_INFERRED_FIELD",
                message=warning,
            )
        )
    return result


def submit_report_gate_recovery_report(
    session_id: str,
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    expected_task_id: str = "",
    expected_task_ref: str = "",
    recovery_reason: str = "",
    warning_texts: Sequence[str] = (),
    owner_confirmed: bool = False,
) -> CommandResult:
    """Submit an owner-confirmed replacement report for a report-gate blocker."""

    if not owner_confirmed:
        raise ReportRecoveryError(
            "REPORT_GATE_RECOVERY_CONFIRMATION_REQUIRED: pass --confirm after owner review"
        )
    reason = str(recovery_reason or "").strip()
    if not reason:
        raise ReportRecoveryError(
            "REPORT_GATE_RECOVERY_REASON_REQUIRED: recovery reason is required"
        )
    owner_warnings = _unique_strings(warning_texts)

    root_path = Path(root).resolve()
    session = _resolve_session(root_path, session_id)
    gate = _report_gate_recovery_evidence(session)
    if not gate:
        raise ReportRecoveryError(
            "REPORT_GATE_RECOVERY_NOT_AVAILABLE: session is not blocked by a report gate"
        )
    gate_code = str(gate.get("report_gate_code") or "")
    if gate_code in REPORT_GATE_REFUSED_CODES:
        raise ReportRecoveryError(
            "REPORT_GATE_RECOVERY_REFUSED: {} requires fixing task identity or scope".format(
                gate_code
            )
        )
    if gate_code not in REPORT_GATE_RECOVERABLE_CODES:
        raise ReportRecoveryError(
            "REPORT_GATE_RECOVERY_NOT_AVAILABLE: unsupported report gate code {}".format(
                gate_code or "unknown"
            )
        )

    tasks_state = _load_tasks_state(root_path)
    task = _resolve_task_for_session(tasks_state, session)
    task_id = str(task.get("id") or "")
    task_ref = str(task.get("ref") or "")
    if expected_task_id and expected_task_id != task_id:
        raise ReportRecoveryError(
            "REPORT_RECOVERY_TASK_MISMATCH: expected task_id {} but session selected {}".format(
                expected_task_id,
                task_id,
            )
        )
    if expected_task_ref and expected_task_ref not in _task_reference_values(task):
        raise ReportRecoveryError(
            "REPORT_RECOVERY_TASK_MISMATCH: expected task_ref {} does not match selected task".format(
                expected_task_ref
            )
        )

    report_state = task_report_service.load_task_reports(root_path, required=True)
    replaced_report_id = str(gate.get("report_id") or "")
    record = _resolve_report_record(report_state, task_id, replaced_report_id)
    original_report = _mapping(record.get("report"))
    if not original_report:
        raise ReportRecoveryError(
            "REPORT_GATE_RECOVERY_REPORT_INVALID: selected report has no structured report object"
        )

    requires_warning = bool(_string_items(original_report.get("blockers"))) or bool(
        _failed_blocking_checks(original_report.get("checks"))
    )
    if requires_warning and not owner_warnings:
        raise ReportRecoveryError(
            "REPORT_GATE_RECOVERY_WARNING_REQUIRED: pass --warning to record owner-confirmed nonblocking warning text"
        )

    recovery_report = _report_gate_recovery_report(
        session=session,
        task=task,
        original_report=original_report,
        report_gate=gate,
        recovery_reason=reason,
        owner_warnings=owner_warnings,
        replaced_report_id=replaced_report_id,
    )
    source_file = _report_gate_recovery_source(
        session_id=str(session.get("id") or ""),
        task_id=task_id,
        report_id=replaced_report_id,
        recovery_reason=reason,
        owner_warnings=owner_warnings,
    )
    submission = task_report_service.submit_task_report(
        root=root_path,
        tasks_state=tasks_state,
        task=task,
        report_payload=recovery_report,
        source_file=source_file,
        actor=actor,
        command=REPORT_GATE_RECOVERY_COMMAND_NAME,
    )
    selected_session_id = str(session.get("id") or "")
    result = CommandResult.success(
        command=REPORT_GATE_RECOVERY_COMMAND_NAME,
        domain="pipeline",
        message="OK: submitted owner-confirmed report-gate recovery report {}".format(
            submission.report_id
        ),
        data={
            "session_id": selected_session_id,
            "task_id": task_id,
            "task_ref": task_ref,
            "report_id": submission.report_id,
            "recovery_report_id": submission.report_id,
            "replaced_report_id": replaced_report_id,
            "recovery_basis": REPORT_GATE_RECOVERY_BASIS,
            "report_gate_code": gate_code,
            "source_file": submission.source_file,
            "event_id": submission.event_id,
        },
        revision_before=submission.revision_before,
        revision_after=submission.revision_after,
    )
    result.changed_files.append(submission.state_path)
    result.events.append(submission.event_id)
    result.owner_action_required = (
        "Rerun collect-report for session {} with --allow-existing-report; "
        "then rerun verify."
    ).format(selected_session_id)
    result.next_actions.extend(
        [
            "python scripts/aictl.py pipeline phase collect-report {} --allow-existing-report".format(
                selected_session_id
            ),
            "python scripts/aictl.py pipeline phase verify {}".format(selected_session_id),
        ]
    )
    result.warnings.append(
        CommandMessage(
            code="REPORT_GATE_RECOVERY_OWNER_CONFIRMED",
            message=(
                "Recovery report uses owner-confirmed report-gate triage; "
                "downstream gates must still run."
            ),
        )
    )
    return result


def _resolve_session(root: Path, session_id: str) -> Mapping[str, Any]:
    requested = str(session_id or "").strip()
    if not requested:
        raise ReportRecoveryError("REPORT_RECOVERY_SESSION_REQUIRED: session_id is required")
    state = load_pipeline_state(root, required=True)
    matches = [
        session
        for session in state.get("sessions", [])
        if isinstance(session, Mapping) and str(session.get("id") or "") == requested
    ]
    if not matches:
        raise ReportRecoveryError(
            "REPORT_RECOVERY_SESSION_NOT_FOUND: {}".format(requested)
        )
    if len(matches) > 1:
        raise ReportRecoveryError(
            "REPORT_RECOVERY_SESSION_AMBIGUOUS: {}".format(requested)
        )
    return matches[0]


def _report_gate_recovery_evidence(session: Mapping[str, Any]) -> Mapping[str, Any]:
    for phase in reversed(_phase_history(session)):
        if str(phase.get("phase") or "") != "verify":
            continue
        if str(phase.get("status") or "") != "blocked":
            continue
        artifacts = _mapping(phase.get("artifacts"))
        report_gate = _mapping(artifacts.get("report_gate"))
        gate_code = _first_nonempty(
            report_gate.get("code"),
            artifacts.get("report_gate_code"),
            artifacts.get("blocked_by"),
        )
        if not gate_code.startswith("CODEX_REPORT_"):
            continue
        return {
            "phase": "verify",
            "phase_status": str(phase.get("status") or ""),
            "blocked_by": str(artifacts.get("blocked_by") or ""),
            "report_gate_status": _first_nonempty(
                report_gate.get("status"),
                artifacts.get("report_gate_status"),
            ),
            "report_gate_code": gate_code,
            "report_id": _first_nonempty(
                report_gate.get("report_id"),
                artifacts.get("report_id"),
                artifacts.get("collected_report_id"),
            ),
            "collected_report_id": str(artifacts.get("collected_report_id") or ""),
            "report_gate": dict(report_gate),
        }
    return {}


def _load_tasks_state(root: Path) -> Mapping[str, Any]:
    path = tasks_state_path(root)
    try:
        data = read_json_file(path, missing_code="TASKS_NOT_INITIALIZED")
    except StoreError as exc:
        raise ReportRecoveryError(str(exc)) from exc
    if not isinstance(data, Mapping):
        raise ReportRecoveryError(
            "TASKS_STATE_INVALID: {} must contain a JSON object".format(path)
        )
    return data


def _resolve_task_for_session(
    tasks_state: Mapping[str, Any],
    session: Mapping[str, Any],
) -> Mapping[str, Any]:
    candidates = _unique_strings(
        [
            str(session.get("current_task_id") or ""),
            str(session.get("current_task_ref") or ""),
        ]
    )
    matches = [
        task
        for task in tasks_state.get("tasks", [])
        if isinstance(task, Mapping)
        and any(candidate in _task_reference_values(task) for candidate in candidates)
    ]
    if not matches:
        raise ReportRecoveryError(
            "REPORT_RECOVERY_TASK_NOT_FOUND: {}".format(", ".join(candidates) or "none")
        )
    if len(matches) > 1:
        raise ReportRecoveryError(
            "REPORT_RECOVERY_TASK_AMBIGUOUS: {}".format(
                ", ".join(str(task.get("id") or "") for task in matches)
            )
        )
    return matches[0]


def _resolve_report_record(
    report_state: Mapping[str, Any],
    task_id: str,
    report_id: str,
) -> Mapping[str, Any]:
    selected_report_id = str(report_id or "").strip()
    if not selected_report_id:
        latest = report_state.get("latest_by_task")
        if isinstance(latest, Mapping):
            selected_report_id = str(latest.get(task_id) or "").strip()
    if not selected_report_id:
        raise ReportRecoveryError(
            "REPORT_GATE_RECOVERY_REPORT_REQUIRED: report gate did not identify a report"
        )

    matches = [
        record
        for record in report_state.get("reports", [])
        if isinstance(record, Mapping)
        and str(record.get("id") or "") == selected_report_id
        and str(record.get("task_id") or "") == task_id
    ]
    if not matches:
        raise ReportRecoveryError(
            "REPORT_GATE_RECOVERY_REPORT_NOT_FOUND: {}".format(selected_report_id)
        )
    if len(matches) > 1:
        raise ReportRecoveryError(
            "REPORT_GATE_RECOVERY_REPORT_AMBIGUOUS: {}".format(selected_report_id)
        )
    return matches[0]


def _task_reference_values(task: Mapping[str, Any]) -> set[str]:
    values = {
        str(task.get("id") or ""),
        str(task.get("ref") or ""),
        str(task.get("uid") or ""),
        str(task.get("legacy_id") or ""),
    }
    aliases = task.get("aliases")
    if isinstance(aliases, Sequence) and not isinstance(aliases, (str, bytes)):
        values.update(str(alias) for alias in aliases if str(alias).strip())
    values.discard("")
    return values


def _phase_history(session: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    history = session.get("phase_history")
    if not isinstance(history, Sequence) or isinstance(history, (str, bytes)):
        return []
    return [phase for phase in history if isinstance(phase, Mapping)]


def _latest_phase(session: Mapping[str, Any], phase_name: str) -> Mapping[str, Any]:
    for phase in reversed(_phase_history(session)):
        if str(phase.get("phase") or "") == phase_name:
            return phase
    return {}


def _captured_stdout(
    artifacts: Mapping[str, Any],
    *,
    root: Path | None,
) -> tuple[str, str, str]:
    stdout_ref = _first_nonempty(
        _mapping(artifacts.get("execute_evidence")).get("stdout_ref"),
        _mapping(artifacts.get("adapter_summary")).get("stdout_ref"),
        _mapping(artifacts.get("adapter")).get("stdout_ref"),
    )
    stdout = _read_runtime_stdout(root, artifacts) if root is not None else ""
    if not stdout:
        stdout = _first_nonempty(
            _mapping(artifacts.get("execute_evidence")).get("stdout_snippet"),
            _mapping(artifacts.get("adapter_summary")).get("stdout_snippet"),
            _mapping(artifacts.get("adapter")).get("stdout_snippet"),
        )
    if not stdout_ref and stdout:
        stdout_ref = "captured:stdout:sha256:{}".format(
            hashlib.sha256(stdout.encode("utf-8")).hexdigest()
        )
    source_file = stdout_ref or "captured:stdout:sha256:missing"
    return stdout, source_file, stdout_ref


def _read_runtime_stdout(root: Path | None, artifacts: Mapping[str, Any]) -> str:
    if root is None:
        return ""
    metadata = _runtime_log_metadata(artifacts, "stdout")
    path_text = str(metadata.get("path") or "").strip()
    if not path_text:
        return ""
    try:
        path = (root / path_text).resolve()
        path.relative_to(root)
    except ValueError:
        return ""
    start = _non_negative_int(metadata.get("start_offset"))
    end = _non_negative_int(metadata.get("end_offset"))
    limit = STDOUT_RECOVERY_LIMIT
    try:
        with path.open("rb") as handle:
            handle.seek(start)
            if end > start:
                raw = handle.read(min(limit, end - start))
            else:
                raw = handle.read(limit)
    except OSError:
        return ""
    return raw.decode("utf-8", errors="replace")


def _runtime_log_metadata(
    artifacts: Mapping[str, Any],
    stream: str,
) -> Mapping[str, Any]:
    for candidate in (
        artifacts.get("runtime_logs"),
        _mapping(artifacts.get("execute_evidence")).get("runtime_logs"),
        _mapping(artifacts.get("adapter_summary")).get("runtime_logs"),
        _mapping(artifacts.get("adapter")).get("runtime_logs"),
    ):
        metadata = _mapping(_mapping(candidate).get(stream))
        if metadata:
            return metadata
    return {}


def _summary_from_stdout(stdout: str) -> str:
    items = _section_items(stdout, ("implementation summary", "summary"))
    if items:
        return _bounded(" ".join(items), 700)
    for line in stdout.splitlines():
        text = _clean_list_item(line)
        if text and not text.startswith(("CODEX_REPORT_JSON", "```")):
            return _bounded(text, 700)
    return ""


def _report_files(
    stdout: str,
    *,
    section_names: Sequence[str],
    fallback: Sequence[str],
) -> list[str]:
    files = []
    for item in _section_items(stdout, section_names):
        files.extend(PATH_RE.findall(item))
    files.extend(fallback)
    return [
        item
        for item in _unique_strings(files)
        if not item.startswith("AI_PROJECT/state/")
        and not item.startswith("AI_PROJECT/events/")
    ]


def _collect_changed_files(
    phase: Mapping[str, Any],
    artifacts: Mapping[str, Any],
) -> list[str]:
    files = []
    files.extend(_string_items(phase.get("changed_files")))
    files.extend(_string_items(artifacts.get("changed_files")))
    return _unique_strings(files)


def _checks_from_stdout(stdout: str) -> list[dict[str, Any]]:
    checks = []
    for item in _section_items(stdout, ("checks", "tests", "verification")):
        lower = item.lower()
        if "fail" in lower or "error" in lower:
            result = "fail"
            blocking = True
        elif "skip" in lower:
            result = "skipped"
            blocking = False
        elif "warn" in lower:
            result = "warn"
            blocking = False
        elif "pass" in lower or "ok" in lower:
            result = "pass"
            blocking = True
        else:
            result = "warn"
            blocking = False
        name = re.sub(r"\s*[:\-]\s*(pass|passed|fail|failed|warn|warning|skipped|ok|error).*$", "", item, flags=re.I).strip()
        checks.append(
            {
                "name": _bounded(name or item, 160),
                "result": result,
                "blocking": blocking,
                "details": _bounded(item, 500),
            }
        )
    return checks


def _token_usage_from_stdout(stdout: str) -> dict[str, Any]:
    total = 0
    match = TOKEN_RE.search(stdout or "")
    if match:
        total = int(match.group(1).replace(",", "").replace("_", ""))
    context_tokens = 0 if total else _estimate_token_count(stdout or "report recovery")
    estimated_total = total or context_tokens
    return {
        "prompt_tokens": 0,
        "context_tokens": context_tokens,
        "completion_tokens": 0,
        "output_tokens": 0,
        "total_tokens": estimated_total,
        "remaining_tokens": 0,
        "model_context_limit": 0,
        "max_context_tokens": 0,
        "reserved_output_tokens": 0,
        "min_remaining_tokens": 0,
        "token_count_strategy": "report_recovery_estimated_v1",
        "token_count_estimated": True,
        "token_count_unavailable": False,
        "token_count_unavailable_reason": "",
    }


def _report_gate_recovery_report(
    *,
    session: Mapping[str, Any],
    task: Mapping[str, Any],
    original_report: Mapping[str, Any],
    report_gate: Mapping[str, Any],
    recovery_reason: str,
    owner_warnings: Sequence[str],
    replaced_report_id: str,
) -> dict[str, Any]:
    original_blockers = _string_items(original_report.get("blockers"))
    checks, check_warnings = _recovered_checks(original_report.get("checks"), recovery_reason)
    warnings = _unique_strings(
        [
            *_string_items(original_report.get("warnings")),
            "Owner-confirmed report-gate recovery reason: {}".format(recovery_reason),
            *owner_warnings,
            *[
                "Owner-confirmed original blocker triaged as nonblocking: {}".format(
                    blocker
                )
                for blocker in original_blockers
            ],
            *check_warnings,
            *[
                "Report-gate issue reviewed during recovery: {}".format(issue)
                for issue in _report_gate_issue_summaries(report_gate)
            ],
            "token_usage estimated by {}.".format(REPORT_GATE_RECOVERY_TOKEN_STRATEGY),
        ]
    )
    notes = _unique_strings(
        [
            *_string_items(original_report.get("notes")),
            "Owner-confirmed report-gate recovery report created for pipeline session {}.".format(
                str(session.get("id") or "unknown")
            ),
            "Recovery basis: {}.".format(REPORT_GATE_RECOVERY_BASIS),
            "Recovery source report id: {}.".format(replaced_report_id or "unknown"),
            "Recovered report gate code: {}.".format(
                str(report_gate.get("report_gate_code") or "unknown")
            ),
            "Recovery reason: {}.".format(recovery_reason),
            "After submission, rerun collect-report with --allow-existing-report; this action did not run collect-report or verify.",
        ]
    )
    report = {
        "schema_version": task_report_service.TASK_REPORT_SCHEMA_VERSION,
        "task_id": str(task.get("id") or ""),
        "task_ref": str(task.get("ref") or ""),
        "implementation_summary": _first_nonempty(
            original_report.get("implementation_summary"),
            "Owner-confirmed report-gate recovery for {}".format(
                str(task.get("ref") or task.get("id") or "selected task")
            ),
        ),
        "changed_files": _string_items(original_report.get("changed_files"))
        or _string_items(report_gate.get("changed_files")),
        "generated_files": _string_items(original_report.get("generated_files"))
        or _string_items(report_gate.get("generated_files")),
        "checks": checks,
        "warnings": warnings,
        "blockers": [],
        "notes": notes,
        "owner_decision_required": True,
    }
    report["token_usage"] = _estimated_recovery_token_usage(
        report=report,
        report_gate=report_gate,
        recovery_reason=recovery_reason,
        owner_warnings=owner_warnings,
    )
    return report


def _recovered_checks(
    value: Any,
    recovery_reason: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    checks = []
    warnings = []
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return checks, warnings
    for item in value:
        if not isinstance(item, Mapping):
            continue
        check = {
            "name": str(item.get("name") or ""),
            "command": str(item.get("command") or ""),
            "result": str(item.get("result") or "").strip().lower(),
            "duration_sec": item.get("duration_sec"),
            "blocking": bool(item.get("blocking", False)),
            "details": str(item.get("details") or ""),
        }
        if check["result"] in FAILED_CHECK_RESULTS and check["blocking"] is True:
            original_result = check["result"]
            check["result"] = "warn"
            check["blocking"] = False
            check["details"] = _join_sentence_parts(
                check["details"],
                "Owner-confirmed report-gate recovery: {}".format(recovery_reason),
            )
            warnings.append(
                "Owner-confirmed failed blocking check triaged as nonblocking: {} ({})".format(
                    check["name"] or "unnamed check",
                    original_result,
                )
            )
        checks.append(check)
    return checks, warnings


def _failed_blocking_checks(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [
        check
        for check in value
        if isinstance(check, Mapping)
        and str(check.get("result") or "").strip().lower() in FAILED_CHECK_RESULTS
        and check.get("blocking") is True
    ]


def _report_gate_issue_summaries(report_gate: Mapping[str, Any]) -> list[str]:
    gate = _mapping(report_gate.get("report_gate"))
    issues = gate.get("issues")
    if not isinstance(issues, Sequence) or isinstance(issues, (str, bytes)):
        return []
    result = []
    for issue in issues:
        if not isinstance(issue, Mapping):
            continue
        code = str(issue.get("code") or "").strip()
        message = str(issue.get("message") or "").strip()
        if code and message:
            result.append("{}: {}".format(code, message))
        elif code or message:
            result.append(code or message)
    return _unique_strings(result)


def _estimated_recovery_token_usage(
    *,
    report: Mapping[str, Any],
    report_gate: Mapping[str, Any],
    recovery_reason: str,
    owner_warnings: Sequence[str],
) -> dict[str, Any]:
    owner_text = "\n".join([recovery_reason, *owner_warnings])
    evidence_text = json.dumps(
        {"report": dict(report), "report_gate": dict(report_gate)},
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    prompt_tokens = _estimate_token_count(owner_text or "owner recovery")
    context_tokens = _estimate_token_count(evidence_text)
    total_tokens = prompt_tokens + context_tokens
    return {
        "prompt_tokens": prompt_tokens,
        "context_tokens": context_tokens,
        "completion_tokens": 0,
        "output_tokens": 0,
        "total_tokens": total_tokens,
        "remaining_tokens": 0,
        "model_context_limit": 0,
        "max_context_tokens": 0,
        "reserved_output_tokens": 0,
        "min_remaining_tokens": 0,
        "token_count_strategy": REPORT_GATE_RECOVERY_TOKEN_STRATEGY,
        "token_count_estimated": True,
        "token_count_unavailable": False,
        "token_count_unavailable_reason": "",
    }


def _report_gate_recovery_source(
    *,
    session_id: str,
    task_id: str,
    report_id: str,
    recovery_reason: str,
    owner_warnings: Sequence[str],
) -> str:
    digest = hashlib.sha256(
        json.dumps(
            {
                "session_id": session_id,
                "task_id": task_id,
                "report_id": report_id,
                "recovery_reason": recovery_reason,
                "owner_warnings": list(owner_warnings),
            },
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    return "captured:report-gate-recovery:{}:{}:sha256:{}".format(
        session_id or "unknown",
        report_id or "unknown",
        digest,
    )


def _estimate_token_count(text: str) -> int:
    return max(1, (len(str(text).encode("utf-8")) + 3) // 4)


def _join_sentence_parts(*parts: str) -> str:
    return " ".join(part.strip() for part in parts if str(part or "").strip())


def _section_items(stdout: str, section_names: Sequence[str]) -> list[str]:
    names = {name.lower().replace("_", " ") for name in section_names}
    lines = stdout.splitlines()
    items: list[str] = []
    capture = False
    for line in lines:
        stripped = line.strip()
        normalized = stripped.lstrip("#").strip().rstrip(":").lower().replace("_", " ")
        if normalized in names:
            capture = True
            continue
        if capture and _looks_like_heading(stripped):
            break
        if capture:
            item = _clean_list_item(stripped)
            if item:
                items.append(item)
    return items


def _looks_like_heading(line: str) -> bool:
    text = line.strip()
    if not text:
        return True
    if text.startswith(("-", "*")):
        return False
    if text.startswith("#"):
        return True
    return bool(re.match(r"^[A-Za-z][A-Za-z _/-]{1,40}:$", text))


def _clean_list_item(line: str) -> str:
    text = line.strip()
    text = re.sub(r"^[-*]\s+", "", text)
    text = re.sub(r"^\d+[.)]\s+", "", text)
    return text.strip()


def _recovery_notes(session_id: str, source_file: str, stdout_ref: str) -> list[str]:
    notes = [
        "Draft structured report created by Web report recovery for pipeline session {}.".format(
            session_id or "unknown"
        ),
        "Owner confirmation was required before submission.",
        "After submission, rerun collect-report; this action did not run collect-report or verify.",
    ]
    if source_file:
        notes.append("Source evidence: {}.".format(source_file))
    if stdout_ref and stdout_ref != source_file:
        notes.append("Captured stdout reference: {}.".format(stdout_ref))
    return notes


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_items(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _unique_strings(values: Sequence[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in seen:
            result.append(text)
            seen.add(text)
    return result


def _first_nonempty(*values: Any) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _non_negative_int(value: Any) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return max(0, value)
    text = str(value or "").strip()
    return int(text) if text.isdigit() else 0


def _bounded(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return "{}\n[truncated: {} bytes total]".format(
        text[:limit],
        len(text.encode("utf-8")),
    )


def draft_json(draft: RecoveryDraft) -> str:
    """Return the owner-reviewable report JSON body."""

    return json.dumps(draft.report, ensure_ascii=False, indent=2, sort_keys=True)

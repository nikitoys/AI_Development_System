"""Pipeline review phase service.

The build-prompt-only mode exposes the semantic Codex review prompt as a
controlled, read-only artifact without running a reviewer or changing task
approval state.
"""

from __future__ import annotations

import hashlib
import json
import shlex
import subprocess
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

from ai_project_ctl.core.result import CommandMessage, CommandResult

from .codex_review import BLOCKED as CODEX_REVIEW_BLOCKED
from .codex_review import CODE_MALFORMED_OUTPUT
from .codex_review import FAIL as CODEX_REVIEW_FAIL
from .codex_review import PASS as CODEX_REVIEW_PASS
from .codex_review import VERDICT_BLOCKED
from .codex_review import VERDICT_REQUEST_CHANGES
from .codex_review import build_codex_review_prompt
from .codex_review import evaluate_codex_review
from .machine_review import FAIL as MACHINE_REVIEW_FAIL
from .machine_review import PASS as MACHINE_REVIEW_PASS
from .machine_review import WARN as MACHINE_REVIEW_WARN
from .machine_review import MachineCheckEvidence, MachineReviewResult
from .phase import PhaseResult
from .policy import PipelinePolicy
from .report_gate import PASS as REPORT_GATE_PASS
from .report_gate import evaluate_report_gate
from .session import record_phase_result
from .state import load_pipeline_state, load_reference_state, pipeline_state_path


COMMAND_NAME = "pipeline.phase.review"
PHASE_NAME = "review"
VERIFY_PHASE_NAME = "verify"
ARTIFACT_TEXT_LIMIT = 1200
ARTIFACT_ITEM_LIMIT = 20
REVIEWER_COMMAND_TIMEOUT_SEC = 300


def review_phase(
    session_id: str = "",
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
    build_prompt_only: bool = False,
    manual_review_file: str | Path | None = None,
    reviewer_command: str | Sequence[str] | None = None,
    reviewer_timeout_sec: int = REVIEWER_COMMAND_TIMEOUT_SEC,
) -> CommandResult:
    """Build or evaluate the semantic review gate for a verified pipeline task."""

    selected_modes = sum(
        1
        for selected in (
            build_prompt_only,
            bool(manual_review_file),
            bool(reviewer_command),
        )
        if selected
    )
    if selected_modes > 1:
        return _failure(
            "PIPELINE_REVIEW_MODE_CONFLICT",
            (
                "Use only one of --build-prompt-only, --manual-review-file, "
                "or --reviewer-command."
            ),
            details={"next_action": "Choose one review phase mode and rerun."},
        )
    if selected_modes == 0:
        return _failure(
            "PIPELINE_REVIEW_INPUT_REQUIRED",
            (
                "Review phase requires --build-prompt-only, --manual-review-file, "
                "or --reviewer-command."
            ),
            details={
                "next_action": (
                    "Rerun with --build-prompt-only to create a prompt, or "
                    "--manual-review-file/--reviewer-command to evaluate a JSON "
                    "review verdict."
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

    verify_phase = _latest_phase_result(session, VERIFY_PHASE_NAME)
    if verify_phase is None:
        return _blocked(
            "VERIFY_PHASE_REQUIRED",
            "Verify phase evidence is missing for this session.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={"session_id": selected_session_id, "task_id": task_id},
            next_action="Run pipeline phase verify before review.",
        )

    verify_artifacts = _mapping(verify_phase.get("artifacts"))
    verify_evidence = _mapping(verify_artifacts.get("verify_evidence"))
    if str(verify_phase.get("status") or "") != "passed":
        return _blocked(
            "VERIFY_PHASE_NOT_PASSED",
            "Verify phase has not passed for this session.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                "session_id": selected_session_id,
                "task_id": task_id,
                "verify_phase": _phase_summary(verify_phase),
            },
            next_action="Resolve verify, then rerun review.",
        )
    if not verify_evidence:
        return _blocked(
            "VERIFY_EVIDENCE_MISSING",
            "Passed verify phase does not contain compact verify evidence.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                "session_id": selected_session_id,
                "task_id": task_id,
                "verify_phase": _phase_summary(verify_phase),
            },
            next_action="Rerun pipeline phase verify before review.",
        )

    verified_report_id = str(
        verify_evidence.get("report_id") or verify_artifacts.get("report_id") or ""
    ).strip()
    if not verified_report_id:
        return _blocked(
            "VERIFY_REPORT_ID_MISSING",
            "Verify evidence does not include a report id.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                "session_id": selected_session_id,
                "task_id": task_id,
                "verify_evidence": dict(verify_evidence),
            },
            next_action="Rerun collect-report and verify so review can bind to a report id.",
        )

    refs = load_reference_state(root_path)
    tasks_state = refs.get("tasks")
    if not isinstance(tasks_state, Mapping):
        return _blocked(
            "PIPELINE_TASKS_STATE_NOT_FOUND",
            "Task state is required to build a review prompt.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={"session_id": selected_session_id, "task_id": task_id},
            next_action="Restore task state, then rerun review.",
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
            next_action="Fix the pipeline session task selection, then rerun review.",
        )

    try:
        policy = PipelinePolicy.from_dict(
            _required_mapping(session.get("policy_snapshot"), "policy_snapshot")
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _blocked(
            "PIPELINE_REVIEW_POLICY_INVALID",
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
            "PIPELINE_REVIEW_POLICY_INVALID",
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
    if report_gate.report_id != verified_report_id:
        return _blocked(
            "REPORT_CHANGED_AFTER_VERIFY",
            "Latest report gate target differs from the verified report.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                "session_id": selected_session_id,
                "task_id": task_id,
                "verified_report_id": verified_report_id,
                "latest_report_id": report_gate.report_id,
                "report_gate": report_gate.to_dict(),
            },
            next_action="Rerun collect-report and verify, then rebuild the review prompt.",
        )
    if report_gate.status != REPORT_GATE_PASS:
        return _blocked(
            "REPORT_GATE_NOT_PASSED_AFTER_VERIFY",
            "Latest report gate no longer passes.",
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
            artifacts={
                "session_id": selected_session_id,
                "task_id": task_id,
                "verified_report_id": verified_report_id,
                "report_gate": report_gate.to_dict(),
            },
            next_action="Resolve report gate issues and rerun verify before review.",
        )

    machine_review = _machine_review_from_verify(
        verify_phase,
        verify_evidence=verify_evidence,
        task_id=task_id,
        report_id=verified_report_id,
    )

    prompt = build_codex_review_prompt(
        root=root_path,
        task=task,
        report_gate=report_gate,
        machine_review=machine_review,
    )
    prompt_bytes = len(prompt.encode("utf-8"))
    prompt_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    if manual_review_file:
        manual = _read_manual_review_file(root_path, manual_review_file)
        if manual["error_code"]:
            return _review_failure(
                str(manual["error_code"]),
                str(manual["error_message"]),
                session_id=selected_session_id,
                task_id=task_id,
                root=root_path,
                actor=actor,
                artifacts={
                    "session_id": selected_session_id,
                    "task_id": task_id,
                    "report_id": verified_report_id,
                    **_mapping(manual.get("artifacts")),
                    "source_verify_phase": _phase_summary(verify_phase),
                },
            )

        codex_review = evaluate_codex_review(
            root=root_path,
            task=task,
            report_gate=report_gate,
            machine_review=machine_review,
            reviewer_output=_required_mapping(
                manual.get("reviewer_output"),
                "manual_review_file",
            ),
        )
        phase = _phase_from_codex_review(
            codex_review,
            review_input_artifacts=_mapping(manual.get("artifacts")),
            verify_phase=verify_phase,
            report_gate=report_gate,
            machine_review=machine_review,
            session_id=selected_session_id,
        )
        result = _phase_command(
            phase,
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
        )
        if codex_review.status == CODEX_REVIEW_FAIL and result.command == COMMAND_NAME:
            result.errors.append(
                CommandMessage(
                    codex_review.code,
                    codex_review.reason,
                    details={
                        "review_id": codex_review.review_id,
                        "verdict": codex_review.verdict,
                    },
                )
            )
        return result

    if reviewer_command:
        command_result = _run_reviewer_command(
            reviewer_command,
            prompt,
            root=root_path,
            timeout_sec=reviewer_timeout_sec,
        )
        if command_result["error_code"]:
            return _review_failure(
                str(command_result["error_code"]),
                str(command_result["error_message"]),
                session_id=selected_session_id,
                task_id=task_id,
                root=root_path,
                actor=actor,
                artifacts={
                    "session_id": selected_session_id,
                    "task_id": task_id,
                    "report_id": verified_report_id,
                    "review_prompt_sha256": prompt_sha,
                    "review_prompt_bytes": prompt_bytes,
                    **_mapping(command_result.get("artifacts")),
                    "source_verify_phase": _phase_summary(verify_phase),
                },
                next_action="Fix the reviewer command and rerun review.",
            )

        codex_review = evaluate_codex_review(
            root=root_path,
            task=task,
            report_gate=report_gate,
            machine_review=machine_review,
            reviewer_output=str(command_result.get("stdout") or ""),
        )
        phase = _phase_from_codex_review(
            codex_review,
            review_input_artifacts=_mapping(command_result.get("artifacts")),
            verify_phase=verify_phase,
            report_gate=report_gate,
            machine_review=machine_review,
            session_id=selected_session_id,
        )
        result = _phase_command(
            phase,
            session_id=selected_session_id,
            task_id=task_id,
            root=root_path,
            actor=actor,
        )
        if codex_review.status == CODEX_REVIEW_FAIL and result.command == COMMAND_NAME:
            result.errors.append(
                CommandMessage(
                    codex_review.code,
                    codex_review.reason,
                    details={
                        "review_id": codex_review.review_id,
                        "verdict": codex_review.verdict,
                    },
                )
            )
        return result

    artifacts = {
        "session_id": selected_session_id,
        "task_id": task_id,
        "report_id": verified_report_id,
        "build_prompt_only": True,
        "review_prompt_returned": True,
        "review_prompt_json_field": "data.review_prompt",
        "review_prompt_sha256": prompt_sha,
        "review_prompt_bytes": prompt_bytes,
        "review_prompt_schema": "codex_review_json_verdict_v1",
        "report_gate_status": report_gate.status,
        "report_gate_code": report_gate.code,
        "machine_review_status": machine_review.status,
        "machine_review_code": machine_review.code,
        "source_verify_phase": _phase_summary(verify_phase),
    }
    phase = PhaseResult.passed(
        PHASE_NAME,
        reason="Semantic Codex review prompt built without running a reviewer.",
        next_action=(
            "Send data.review_prompt to a read-only Codex Reviewer, then record "
            "the resulting review through an approved review workflow."
        ),
        artifacts=artifacts,
    )
    result = _phase_command(
        phase,
        session_id=selected_session_id,
        task_id=task_id,
        root=root_path,
        actor=actor,
    )
    if result.ok:
        result.data["review_prompt"] = prompt
        result.data["review_prompt_sha256"] = prompt_sha
        result.data["review_prompt_bytes"] = prompt_bytes
        result.data["review_prompt_json_field"] = "data.review_prompt"
    return result


def _read_manual_review_file(
    root: Path,
    manual_review_file: str | Path,
) -> dict[str, Any]:
    path = Path(manual_review_file).expanduser()
    if not path.is_absolute():
        path = root / path
    artifacts: dict[str, Any] = {
        "manual_review_file": _display_path(root, path),
        "manual_review_json_only": True,
    }
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "reviewer_output": {},
            "artifacts": artifacts,
            "error_code": "MANUAL_REVIEW_FILE_NOT_FOUND",
            "error_message": "manual review file not found: {}".format(
                artifacts["manual_review_file"]
            ),
        }
    except OSError as exc:
        return {
            "reviewer_output": {},
            "artifacts": artifacts,
            "error_code": "MANUAL_REVIEW_FILE_READ_FAILED",
            "error_message": "manual review file could not be read: {}".format(exc),
        }

    payload = text.encode("utf-8")
    artifacts.update(
        {
            "manual_review_sha256": hashlib.sha256(payload).hexdigest(),
            "manual_review_bytes": len(payload),
        }
    )
    try:
        reviewer_output = json.loads(text)
    except json.JSONDecodeError as exc:
        return {
            "reviewer_output": {},
            "artifacts": artifacts,
            "error_code": CODE_MALFORMED_OUTPUT,
            "error_message": "reviewer_output_is_not_valid_json: line {} column {} {}".format(
                exc.lineno,
                exc.colno,
                exc.msg,
            ),
        }
    if not isinstance(reviewer_output, Mapping):
        return {
            "reviewer_output": {},
            "artifacts": artifacts,
            "error_code": CODE_MALFORMED_OUTPUT,
            "error_message": "reviewer_output_must_be_json_object",
    }
    return {
        "reviewer_output": reviewer_output,
        "artifacts": artifacts,
        "error_code": "",
        "error_message": "",
    }


def _run_reviewer_command(
    reviewer_command: str | Sequence[str],
    prompt: str,
    *,
    root: Path,
    timeout_sec: int,
) -> dict[str, Any]:
    try:
        argv = _reviewer_argv(reviewer_command)
    except ValueError as exc:
        artifacts = _reviewer_command_artifacts(
            (),
            timeout_sec=timeout_sec,
            returncode=None,
            duration_sec=None,
            stdout="",
            stderr=str(exc),
        )
        return {
            "stdout": "",
            "artifacts": artifacts,
            "error_code": "REVIEWER_COMMAND_INVALID",
            "error_message": "reviewer_command_invalid: {}".format(exc),
        }
    artifacts = _reviewer_command_artifacts(
        argv,
        timeout_sec=timeout_sec,
        returncode=None,
        duration_sec=None,
        stdout="",
        stderr="",
    )
    if not argv:
        return {
            "stdout": "",
            "artifacts": artifacts,
            "error_code": "REVIEWER_COMMAND_EMPTY",
            "error_message": "reviewer_command_must_not_be_empty",
        }

    started = time.monotonic()
    try:
        completed = subprocess.run(
            list(argv),
            cwd=root,
            input=prompt,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=max(1, int(timeout_sec)),
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = _process_text(exc.stdout)
        stderr = _process_text(exc.stderr)
        artifacts = _reviewer_command_artifacts(
            argv,
            timeout_sec=timeout_sec,
            returncode=None,
            duration_sec=_elapsed(started),
            stdout=stdout,
            stderr=stderr,
            timed_out=True,
        )
        return {
            "stdout": stdout,
            "artifacts": artifacts,
            "error_code": "REVIEWER_COMMAND_TIMEOUT",
            "error_message": "reviewer_command_timed_out",
        }
    except OSError as exc:
        artifacts = _reviewer_command_artifacts(
            argv,
            timeout_sec=timeout_sec,
            returncode=None,
            duration_sec=_elapsed(started),
            stdout="",
            stderr=str(exc),
        )
        return {
            "stdout": "",
            "artifacts": artifacts,
            "error_code": "REVIEWER_COMMAND_ERROR",
            "error_message": "reviewer_command_failed_to_start: {}".format(exc),
        }

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    artifacts = _reviewer_command_artifacts(
        argv,
        timeout_sec=timeout_sec,
        returncode=int(completed.returncode),
        duration_sec=_elapsed(started),
        stdout=stdout,
        stderr=stderr,
    )
    if completed.returncode != 0:
        return {
            "stdout": stdout,
            "artifacts": artifacts,
            "error_code": "REVIEWER_COMMAND_NONZERO_EXIT",
            "error_message": "reviewer_command_exited_nonzero: {}".format(
                completed.returncode
            ),
        }
    return {
        "stdout": stdout,
        "artifacts": artifacts,
        "error_code": "",
        "error_message": "",
    }


def _reviewer_argv(reviewer_command: str | Sequence[str]) -> tuple[str, ...]:
    if isinstance(reviewer_command, str):
        return tuple(shlex.split(reviewer_command))
    return tuple(str(part) for part in reviewer_command if str(part).strip())


def _reviewer_command_artifacts(
    argv: Sequence[str],
    *,
    timeout_sec: int,
    returncode: int | None,
    duration_sec: float | None,
    stdout: str,
    stderr: str,
    timed_out: bool = False,
) -> dict[str, Any]:
    bounded_argv = [_bounded_text(part) for part in argv]
    artifacts: dict[str, Any] = {
        "reviewer_command": bounded_argv,
        "reviewer_command_truncated": bounded_argv != list(argv),
        "reviewer_command_prompt_stdin": True,
        "reviewer_command_timeout_sec": max(1, int(timeout_sec)),
        "reviewer_command_stdout_bytes": len(stdout.encode("utf-8")),
        "reviewer_command_stderr_bytes": len(stderr.encode("utf-8")),
        "reviewer_command_stdout_summary": _bounded_text(stdout),
        "reviewer_command_stderr_summary": _bounded_text(stderr),
        "reviewer_command_stdout_truncated": len(stdout) > ARTIFACT_TEXT_LIMIT,
        "reviewer_command_stderr_truncated": len(stderr) > ARTIFACT_TEXT_LIMIT,
    }
    if returncode is not None:
        artifacts["reviewer_command_returncode"] = returncode
    if duration_sec is not None:
        artifacts["reviewer_command_duration_sec"] = duration_sec
    if timed_out:
        artifacts["reviewer_command_timed_out"] = True
    return artifacts


def _phase_from_codex_review(
    codex_review,
    *,
    review_input_artifacts: Mapping[str, Any],
    verify_phase: Mapping[str, Any],
    report_gate,
    machine_review: MachineReviewResult,
    session_id: str,
) -> PhaseResult:
    artifacts = {
        "session_id": session_id,
        "task_id": codex_review.task_id,
        "report_id": codex_review.report_id,
        "review_id": codex_review.review_id,
        "verdict": codex_review.verdict,
        "review_status": codex_review.status,
        "review_code": codex_review.code,
        "review_reason": _bounded_text(codex_review.reason),
        "summary": _bounded_text(codex_review.summary),
        "findings": _bounded_findings(codex_review.findings),
        "risks": _bounded_strings(codex_review.risks),
        "reviewer_evidence": _bounded_json(dict(codex_review.evidence or {})),
        "prompt_sha256": codex_review.prompt_sha256,
        "prompt_bytes": codex_review.prompt_bytes,
        "report_gate_status": report_gate.status,
        "report_gate_code": report_gate.code,
        "machine_review_status": machine_review.status,
        "machine_review_code": machine_review.code,
        "source_verify_phase": _phase_summary(verify_phase),
        **dict(review_input_artifacts),
    }
    if codex_review.status == CODEX_REVIEW_PASS:
        return PhaseResult.passed(
            PHASE_NAME,
            reason=_bounded_text(codex_review.reason),
            next_action=(
                "Review gate passed with APPROVE. Continue only through the "
                "governed close phase; this is not Human Owner approval."
            ),
            artifacts=artifacts,
        )
    if codex_review.status == CODEX_REVIEW_BLOCKED:
        blocked_artifacts = {"blocked_by": codex_review.code, **artifacts}
        if codex_review.verdict == VERDICT_REQUEST_CHANGES:
            blocked_artifacts["rework_required"] = True
            blocked_artifacts["rework_planning"] = {
                "next_action": (
                    "Create rework or move the task to changes_requested through "
                    "the governed workflow."
                ),
                "findings": list(artifacts["findings"]),
                "risks": list(artifacts["risks"]),
            }
        return PhaseResult.blocked(
            PHASE_NAME,
            reason=_bounded_text(codex_review.reason),
            next_action=_blocked_review_next_action(codex_review.verdict),
            artifacts=blocked_artifacts,
        )
    return PhaseResult.failed(
        PHASE_NAME,
        reason=_bounded_text(codex_review.reason),
        next_action="Fix the review JSON output and rerun review.",
        artifacts={"error_code": codex_review.code, **artifacts},
    )


def _blocked_review_next_action(verdict: str) -> str:
    if verdict == VERDICT_REQUEST_CHANGES:
        return (
            "Create rework or move the task to changes_requested through the "
            "governed workflow, using reviewer findings and risks for planning; "
            "then rerun verification and review."
        )
    if verdict == VERDICT_BLOCKED:
        return "Resolve the reviewer blocker, then rerun review."
    return "Fix the review output, then rerun review."


def _review_failure(
    code: str,
    message: str,
    *,
    session_id: str,
    task_id: str,
    root: Path,
    actor: str,
    artifacts: Mapping[str, Any],
    next_action: str = "Fix the manual review JSON file and rerun review.",
) -> CommandResult:
    phase = PhaseResult.failed(
        PHASE_NAME,
        reason=_bounded_text(message),
        next_action=next_action,
        artifacts={"error_code": code, **dict(artifacts)},
    )
    result = _phase_command(
        phase,
        session_id=session_id,
        task_id=task_id,
        root=root,
        actor=actor,
    )
    if result.command == COMMAND_NAME:
        result.errors.append(CommandMessage(code, message, details=dict(artifacts)))
        result.ok = False
    return result


def _display_path(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path)


def _bounded_findings(findings) -> list[dict[str, str]]:
    bounded = []
    for finding in list(findings)[:ARTIFACT_ITEM_LIMIT]:
        data = finding.to_dict()
        bounded.append(
            {
                key: _bounded_text(value)
                for key, value in data.items()
                if isinstance(key, str)
            }
        )
    return bounded


def _bounded_strings(values) -> list[str]:
    return [_bounded_text(value) for value in list(values)[:ARTIFACT_ITEM_LIMIT]]


def _bounded_text(value: Any, limit: int = ARTIFACT_TEXT_LIMIT) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _process_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _elapsed(started: float) -> float:
    return round(time.monotonic() - started, 3)


def _bounded_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _bounded_json(item)
            for key, item in list(value.items())[:ARTIFACT_ITEM_LIMIT]
        }
    if isinstance(value, list):
        return [_bounded_json(item) for item in value[:ARTIFACT_ITEM_LIMIT]]
    if isinstance(value, (str, int, float, bool)) or value is None:
        if isinstance(value, str):
            return _bounded_text(value)
        return value
    return _bounded_text(value)


def _resolve_session(root: Path, session_id: str) -> CommandResult:
    state = load_pipeline_state(root)
    selected_id = session_id.strip() or str(state.get("current_session_id") or "")
    if not selected_id:
        return _failure(
            "PIPELINE_SESSION_REQUIRED",
            "Pass a session id or set a current pipeline session before review.",
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
        result.data["review_prompt_sha256"] = str(
            artifacts.get("review_prompt_sha256") or ""
        )
        result.data["review_prompt_bytes"] = int(
            artifacts.get("review_prompt_bytes") or 0
        )
        result.data["review_prompt_json_field"] = str(
            artifacts.get("review_prompt_json_field") or ""
        )
        result.data["review_id"] = str(artifacts.get("review_id") or "")
        result.data["verdict"] = str(artifacts.get("verdict") or "")
        result.data["review_code"] = str(artifacts.get("review_code") or "")
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
        next_action="Fix the review input and rerun the phase.",
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


def _machine_review_from_verify(
    verify_phase: Mapping[str, Any],
    *,
    verify_evidence: Mapping[str, Any],
    task_id: str,
    report_id: str,
) -> MachineReviewResult:
    checks = [
        MachineCheckEvidence(
            name="verify_phase",
            status=MACHINE_REVIEW_PASS,
            code="VERIFY_PHASE_PASSED",
            reason=str(verify_phase.get("reason") or "verify phase passed"),
            blocking=True,
        )
    ]
    for name in (
        "report_gate",
        "git_diff_gate",
        "protected_files_gate",
        "allowed_files_gate",
    ):
        gate = _mapping(verify_evidence.get(name))
        if gate:
            checks.append(_machine_check_from_gate(name, gate))
    return MachineReviewResult(
        status=MACHINE_REVIEW_PASS,
        code="VERIFY_EVIDENCE_PASS",
        reason="Review prompt built from passed verify phase evidence.",
        task_id=task_id,
        report_id=report_id,
        checks=tuple(checks),
    )


def _machine_check_from_gate(name: str, gate: Mapping[str, Any]) -> MachineCheckEvidence:
    gate_status = str(gate.get("status") or "")
    status = _machine_status(gate_status)
    code = str(gate.get("code") or "{}_{}".format(name.upper(), status.upper()))
    reason = str(gate.get("reason") or gate_status or "verify evidence")
    return MachineCheckEvidence(
        name=name,
        status=status,
        code=code,
        reason=reason,
        blocking=True,
    )


def _machine_status(value: str) -> str:
    normalized = value.strip().lower()
    if normalized in {"pass", "passed"}:
        return MACHINE_REVIEW_PASS
    if normalized in {"warn", "warning"}:
        return MACHINE_REVIEW_WARN
    return MACHINE_REVIEW_FAIL


def _phase_summary(phase: Mapping[str, Any]) -> dict[str, Any]:
    artifacts = _mapping(phase.get("artifacts"))
    return {
        "phase": str(phase.get("phase") or ""),
        "status": str(phase.get("status") or ""),
        "reason": str(phase.get("reason") or ""),
        "task_id": str(artifacts.get("task_id") or ""),
        "report_id": str(artifacts.get("report_id") or ""),
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


__all__ = ["review_phase"]

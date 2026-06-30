"""Controlled local git commit action for supervised pipeline sessions."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ai_project_ctl.core.result import CommandResult

from .codex_review import PASS as CODEX_REVIEW_PASS
from .codex_review import VERDICT_APPROVE
from .codex_review import CodexReviewResult
from .machine_review import FAIL as MACHINE_REVIEW_FAIL
from .machine_review import PASS as MACHINE_REVIEW_PASS
from .machine_review import WARN as MACHINE_REVIEW_WARN
from .machine_review import MachineCheckEvidence
from .machine_review import MachineReviewResult
from .policy import (
    CommitMode,
    PipelinePolicy,
    disables_codex_review_by_policy,
    requires_codex_review_approve,
)
from .report_gate import ReportGateResult
from .report_gate import WARN as REPORT_GATE_WARN
from .report_gate import evaluate_report_gate_acceptance
from .state import load_pipeline_state, load_reference_state


PASS = "pass"
BLOCKED = "blocked"
FAIL = "fail"

CODE_READY = "COMMIT_READINESS_PASS"
CODE_DISABLED = "COMMIT_DISABLED_BY_POLICY"
CODE_POLICY_INVALID = "COMMIT_POLICY_INVALID"
CODE_REPORT_NOT_PASS = "COMMIT_REPORT_GATE_NOT_PASS"
CODE_MACHINE_REVIEW_NOT_PASS = "COMMIT_MACHINE_REVIEW_NOT_PASS"
CODE_CODEX_REVIEW_NOT_APPROVED = "COMMIT_CODEX_REVIEW_NOT_APPROVED"
CODE_REQUIRED_CHECK_MISSING = "COMMIT_REQUIRED_CHECK_MISSING"
CODE_REQUIRED_CHECK_NOT_PASS = "COMMIT_REQUIRED_CHECK_NOT_PASS"
CODE_TASK_NOT_DONE = "COMMIT_TASK_NOT_DONE"
CODE_CHANGE_NOT_ACCEPTED = "COMMIT_CHANGE_NOT_ACCEPTED"
CODE_GIT_STATUS_FAILED = "COMMIT_GIT_STATUS_FAILED"
CODE_NO_CHANGES = "COMMIT_NO_CHANGES"
CODE_UNRELATED_FILES = "COMMIT_UNRELATED_FILES"
CODE_FORBIDDEN_GIT_COMMAND = "COMMIT_FORBIDDEN_GIT_COMMAND"
CODE_GIT_COMMAND_FAILED = "COMMIT_GIT_COMMAND_FAILED"
CODE_COMMIT_CREATED = "LOCAL_COMMIT_CREATED"
CODE_CHECKPOINT_CREATED = "CHECKPOINT_COMMIT_CREATED"
CODE_CHECKPOINT_CLEAN = "CHECKPOINT_WORKTREE_CLEAN"
CODE_CHECKPOINT_STATUS_FAILED = "CHECKPOINT_GIT_STATUS_FAILED"
CODE_CHECKPOINT_FAILED = "CHECKPOINT_COMMIT_FAILED"
NOT_RUN = "not_run"

FORBIDDEN_GIT_SUBCOMMANDS = {
    "push",
    "merge",
    "reset",
    "checkout",
    "rebase",
    "switch",
    "restore",
    "clean",
    "rm",
}
REQUIRED_MACHINE_CHECKS = {
    "task_check_generated",
    "evolution_check_generated",
    "context_check_generated",
    "protected_file_check",
}
MACHINE_DIAGNOSTIC_SUMMARY_LIMIT = 1200
FILE_EVIDENCE_KEY = "file_evidence"
PRE_EXISTING_DIRTY_FILES_KEY = "pre_existing_dirty_files"
SESSION_OWNED_CHANGED_FILES_KEY = "session_owned_changed_files"
GOVERNED_PROJECT_CONTROL_PREFIXES = (
    "AI_PROJECT/state/",
    "AI_PROJECT/events/",
    "AI_PROJECT/generated/",
)

GitRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class GitStatusFile:
    """One path reported by git status --short."""

    status: str
    path: str

    def to_dict(self) -> dict[str, str]:
        return {"status": self.status, "path": self.path}


@dataclass(frozen=True)
class GitCommandResult:
    """Safe git command result."""

    ok: bool
    code: str
    reason: str
    command: tuple[str, ...]
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "code": self.code,
            "reason": self.reason,
            "command": list(self.command),
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


@dataclass(frozen=True)
class CommitReadinessResult:
    """Readiness evidence for a local commit."""

    status: str
    code: str
    reason: str
    task_id: str
    change_ids: tuple[str, ...] = ()
    accepted_change_ids: tuple[str, ...] = ()
    approved_files: tuple[str, ...] = ()
    changed_files: tuple[GitStatusFile, ...] = ()
    blockers: tuple[str, ...] = ()
    git_status: GitCommandResult | None = None
    machine_review_diagnostics: tuple[Mapping[str, Any], ...] = ()
    blocking_non_pass_checks: tuple[Mapping[str, Any], ...] = ()
    advisory_non_pass_checks: tuple[Mapping[str, Any], ...] = ()

    @property
    def ok(self) -> bool:
        return self.status == PASS

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "status": self.status,
            "code": self.code,
            "reason": self.reason,
            "task_id": self.task_id,
            "change_ids": list(self.change_ids),
            "accepted_change_ids": list(self.accepted_change_ids),
            "approved_files": list(self.approved_files),
            "changed_files": [item.to_dict() for item in self.changed_files],
            "blockers": list(self.blockers),
            "git_status": self.git_status.to_dict() if self.git_status else None,
        }
        diagnostics = [dict(item) for item in self.machine_review_diagnostics]
        blocking_checks = [dict(item) for item in self.blocking_non_pass_checks]
        advisory_checks = [dict(item) for item in self.advisory_non_pass_checks]
        if diagnostics or blocking_checks or advisory_checks:
            data["machine_review_diagnostics"] = diagnostics
            data["blocking_non_pass_checks"] = blocking_checks
            data["advisory_non_pass_checks"] = advisory_checks
        return data


@dataclass(frozen=True)
class LocalCommitResult:
    """Outcome of a guarded local git commit attempt."""

    status: str
    code: str
    reason: str
    task_id: str
    commit_hash: str = ""
    staged_files: tuple[str, ...] = ()
    message: str = ""
    readiness: CommitReadinessResult | None = None
    commands: tuple[GitCommandResult, ...] = ()

    @property
    def ok(self) -> bool:
        return self.status == PASS

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "code": self.code,
            "reason": self.reason,
            "task_id": self.task_id,
            "commit_hash": self.commit_hash,
            "staged_files": list(self.staged_files),
            "message": self.message,
            "readiness": self.readiness.to_dict() if self.readiness else None,
            "commands": [command.to_dict() for command in self.commands],
        }


@dataclass(frozen=True)
class CheckpointCommitResult:
    """Outcome of an owner-confirmed checkpoint commit before Web Run."""

    status: str
    code: str
    reason: str
    task_ref: str = ""
    commit_hash: str = ""
    dirty_files: tuple[GitStatusFile, ...] = ()
    message: str = ""
    commands: tuple[GitCommandResult, ...] = ()

    @property
    def ok(self) -> bool:
        return self.status in {PASS, NOT_RUN}

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "code": self.code,
            "reason": self.reason,
            "task_ref": self.task_ref,
            "commit_hash": self.commit_hash,
            "dirty_files": [item.to_dict() for item in self.dirty_files],
            "message": self.message,
            "commands": [command.to_dict() for command in self.commands],
        }


def evaluate_commit_readiness(
    *,
    root: str | Path,
    task_id: str,
    policy: PipelinePolicy,
    report_gate: ReportGateResult,
    machine_review: MachineReviewResult,
    codex_review: CodexReviewResult,
    side_effects: Sequence[CommandResult] = (),
    session: Mapping[str, Any] | None = None,
    runner: GitRunner | None = None,
) -> CommitReadinessResult:
    """Verify that a local commit is allowed and only approved files are dirty."""

    root_path = Path(root).resolve()
    refs = load_reference_state(root_path)
    task = _task_by_id(refs.get("tasks"), task_id)
    task_refs = _task_reference_values(task, task_id)
    linked_changes = _linked_changes_for_task(task_refs, refs.get("evolution"))
    accepted_changes = [
        change
        for change in linked_changes
        if str(change.get("status") or "") == "accepted"
    ]
    change_ids = tuple(
        str(change.get("id")) for change in linked_changes if change.get("id")
    )
    accepted_change_ids = tuple(
        str(change.get("id")) for change in accepted_changes if change.get("id")
    )

    blockers = _policy_blockers(policy)
    if blockers:
        return _readiness(
            BLOCKED,
            CODE_POLICY_INVALID,
            "Local commit policy is not safe.",
            task_id=task_id,
            change_ids=change_ids,
            accepted_change_ids=accepted_change_ids,
            blockers=tuple(blockers),
        )
    if not policy.commit.create_local_commit:
        return _readiness(
            BLOCKED,
            CODE_DISABLED,
            "Local commit is disabled by policy.",
            task_id=task_id,
            change_ids=change_ids,
            accepted_change_ids=accepted_change_ids,
        )

    machine_diagnostics = _machine_review_diagnostic_kwargs(
        policy,
        report_gate,
        machine_review,
    )
    gate_blocker = _gate_blocker(policy, report_gate, machine_review, codex_review)
    if gate_blocker:
        code, reason = gate_blocker
        return _readiness(
            BLOCKED,
            code,
            reason,
            task_id=task_id,
            change_ids=change_ids,
            accepted_change_ids=accepted_change_ids,
            **machine_diagnostics,
        )

    machine_blocker = _machine_check_blocker(machine_review)
    if machine_blocker:
        code, reason = machine_blocker
        return _readiness(
            BLOCKED,
            code,
            reason,
            task_id=task_id,
            change_ids=change_ids,
            accepted_change_ids=accepted_change_ids,
            **machine_diagnostics,
        )

    machine_warning_blocker = _machine_warning_blocker(policy, report_gate, machine_review)
    if machine_warning_blocker:
        code, reason = machine_warning_blocker
        return _readiness(
            BLOCKED,
            code,
            reason,
            task_id=task_id,
            change_ids=change_ids,
            accepted_change_ids=accepted_change_ids,
            **machine_diagnostics,
        )

    if str(task.get("status") or "") != "done":
        return _readiness(
            BLOCKED,
            CODE_TASK_NOT_DONE,
            "Selected task must be done before local commit.",
            task_id=task_id,
            change_ids=change_ids,
            accepted_change_ids=accepted_change_ids,
            blockers=(str(task.get("status") or "missing"),),
            **machine_diagnostics,
        )
    if linked_changes and not accepted_changes:
        return _readiness(
            BLOCKED,
            CODE_CHANGE_NOT_ACCEPTED,
            "Linked Evolution Change must be accepted before local commit.",
            task_id=task_id,
            change_ids=change_ids,
            accepted_change_ids=accepted_change_ids,
            blockers=change_ids,
            **machine_diagnostics,
        )

    git_status = run_git_command(
        ("git", "status", "--short", "--untracked-files=all"),
        root=root_path,
        runner=runner,
    )
    if not git_status.ok:
        return _readiness(
            BLOCKED,
            CODE_GIT_STATUS_FAILED,
            "Git status check failed.",
            task_id=task_id,
            change_ids=change_ids,
            accepted_change_ids=accepted_change_ids,
            git_status=git_status,
            **machine_diagnostics,
        )

    changed_files = tuple(_parse_git_status(git_status.stdout))
    if not changed_files:
        return _readiness(
            BLOCKED,
            CODE_NO_CHANGES,
            "No changed files are available for local commit.",
            task_id=task_id,
            change_ids=change_ids,
            accepted_change_ids=accepted_change_ids,
            git_status=git_status,
            **machine_diagnostics,
        )

    approved_files = _approved_files(
        root_path,
        report_gate,
        side_effects,
        session=session,
    )
    unrelated = [
        item.path for item in changed_files if _normalize_path(root_path, item.path) not in approved_files
    ]
    if unrelated:
        return _readiness(
            BLOCKED,
            CODE_UNRELATED_FILES,
            "Dirty files include paths that are not approved by report or session evidence.",
            task_id=task_id,
            change_ids=change_ids,
            accepted_change_ids=accepted_change_ids,
            approved_files=tuple(sorted(approved_files)),
            changed_files=changed_files,
            blockers=tuple(unrelated),
            git_status=git_status,
            **machine_diagnostics,
        )

    if not _target_task_artifact_evidence(root_path, report_gate):
        return _readiness(
            BLOCKED,
            CODE_UNRELATED_FILES,
            (
                "Local commit requires target task artifact evidence from the "
                "Codex report before committing governed session side effects."
            ),
            task_id=task_id,
            change_ids=change_ids,
            accepted_change_ids=accepted_change_ids,
            approved_files=tuple(sorted(approved_files)),
            changed_files=changed_files,
            blockers=("target_task_artifact_missing",),
            git_status=git_status,
            **machine_diagnostics,
        )

    reason = "Local commit readiness is green."
    if machine_review.status == MACHINE_REVIEW_WARN:
        reason = (
            "Local commit readiness is green; Machine Review WARN contains only "
            "nonblocking or policy-accepted warning evidence."
        )

    return _readiness(
        PASS,
        CODE_READY,
        reason,
        task_id=task_id,
        change_ids=change_ids,
        accepted_change_ids=accepted_change_ids,
        approved_files=tuple(sorted(approved_files)),
        changed_files=changed_files,
        git_status=git_status,
        **machine_diagnostics,
    )


def create_checkpoint_commit(
    *,
    root: str | Path,
    task_ref: str = "",
    message: str | None = None,
    runner: GitRunner | None = None,
) -> CheckpointCommitResult:
    """Create an owner-confirmed checkpoint commit from the current worktree."""

    root_path = Path(root).resolve()
    commit_message = message or _checkpoint_commit_message(task_ref)
    commands: list[GitCommandResult] = []

    git_status = _run_checkpoint_git_command(
        ("git", "status", "--short", "--untracked-files=all"),
        root=root_path,
        runner=runner,
    )
    commands.append(git_status)
    if not git_status.ok:
        return CheckpointCommitResult(
            status=FAIL,
            code=CODE_CHECKPOINT_STATUS_FAILED,
            reason="Git status check failed before checkpoint commit.",
            task_ref=task_ref,
            message=commit_message,
            commands=tuple(commands),
        )

    dirty_files = tuple(_parse_git_status(git_status.stdout))
    if not dirty_files:
        return CheckpointCommitResult(
            status=NOT_RUN,
            code=CODE_CHECKPOINT_CLEAN,
            reason="Worktree is already clean; checkpoint commit was not created.",
            task_ref=task_ref,
            message=commit_message,
            commands=tuple(commands),
        )

    add = _run_checkpoint_git_command(
        ("git", "add", "-A"),
        root=root_path,
        runner=runner,
    )
    commands.append(add)
    if not add.ok:
        return _checkpoint_commit_failure(
            task_ref,
            "Failed to stage all current changes for checkpoint commit.",
            dirty_files,
            commit_message,
            commands,
        )

    commit = _run_checkpoint_git_command(
        ("git", "commit", "-m", commit_message),
        root=root_path,
        runner=runner,
    )
    commands.append(commit)
    if not commit.ok:
        return _checkpoint_commit_failure(
            task_ref,
            "Checkpoint git commit failed.",
            dirty_files,
            commit_message,
            commands,
        )

    rev_parse = _run_checkpoint_git_command(
        ("git", "rev-parse", "--verify", "HEAD"),
        root=root_path,
        runner=runner,
    )
    commands.append(rev_parse)
    if not rev_parse.ok:
        return _checkpoint_commit_failure(
            task_ref,
            "Checkpoint commit hash could not be read.",
            dirty_files,
            commit_message,
            commands,
        )

    commit_hash = (
        rev_parse.stdout.strip().splitlines()[0] if rev_parse.stdout.strip() else ""
    )
    if not commit_hash:
        return _checkpoint_commit_failure(
            task_ref,
            "Checkpoint commit hash was empty.",
            dirty_files,
            commit_message,
            commands,
        )

    return CheckpointCommitResult(
        status=PASS,
        code=CODE_CHECKPOINT_CREATED,
        reason="Checkpoint commit created before Web Run.",
        task_ref=task_ref,
        commit_hash=commit_hash,
        dirty_files=dirty_files,
        message=commit_message,
        commands=tuple(commands),
    )


def run_local_commit(
    *,
    root: str | Path,
    task_id: str,
    session_id: str,
    policy: PipelinePolicy,
    report_gate: ReportGateResult,
    machine_review: MachineReviewResult,
    codex_review: CodexReviewResult,
    side_effects: Sequence[CommandResult] = (),
    session: Mapping[str, Any] | None = None,
    runner: GitRunner | None = None,
) -> LocalCommitResult:
    """Create a local commit after readiness passes."""

    root_path = Path(root).resolve()
    readiness = evaluate_commit_readiness(
        root=root_path,
        task_id=task_id,
        policy=policy,
        report_gate=report_gate,
        machine_review=machine_review,
        codex_review=codex_review,
        side_effects=side_effects,
        session=session or _session_by_id(load_pipeline_state(root_path), session_id),
        runner=runner,
    )
    if not readiness.ok:
        return LocalCommitResult(
            status=BLOCKED,
            code="COMMIT_READINESS_FAILED",
            reason=readiness.reason,
            task_id=task_id,
            readiness=readiness,
        )

    staged_files = tuple(
        sorted(_normalize_path(root_path, item.path) for item in readiness.changed_files)
    )
    message = _commit_message(root_path, task_id, session_id, readiness.accepted_change_ids)
    commands: list[GitCommandResult] = []

    add = run_git_command(("git", "add", "--", *staged_files), root=root_path, runner=runner)
    commands.append(add)
    if not add.ok:
        return _commit_failure(root_path, task_id, "Failed to stage approved files.", readiness, commands)

    commit = run_git_command(("git", "commit", "-m", message), root=root_path, runner=runner)
    commands.append(commit)
    if not commit.ok:
        return _commit_failure(root_path, task_id, "Local git commit failed.", readiness, commands)

    rev_parse = run_git_command(
        ("git", "rev-parse", "--verify", "HEAD"),
        root=root_path,
        runner=runner,
    )
    commands.append(rev_parse)
    if not rev_parse.ok:
        return _commit_failure(root_path, task_id, "Local commit hash could not be read.", readiness, commands)

    commit_hash = rev_parse.stdout.strip().splitlines()[0] if rev_parse.stdout.strip() else ""
    return LocalCommitResult(
        status=PASS,
        code=CODE_COMMIT_CREATED,
        reason="Local commit created.",
        task_id=task_id,
        commit_hash=commit_hash,
        staged_files=staged_files,
        message=message,
        readiness=readiness,
        commands=tuple(commands),
    )


def run_git_command(
    argv: Sequence[str],
    *,
    root: str | Path,
    runner: GitRunner | None = None,
    timeout_sec: int = 300,
) -> GitCommandResult:
    """Run one allowlisted git command or reject it before execution."""

    command = tuple(str(part) for part in argv if str(part).strip())
    validation_error = _git_command_error(command)
    if validation_error:
        return GitCommandResult(
            ok=False,
            code=CODE_FORBIDDEN_GIT_COMMAND,
            reason=validation_error,
            command=command,
        )

    root_path = Path(root).resolve()
    try:
        if runner is not None:
            completed = runner(command)
        else:
            completed = subprocess.run(
                list(command),
                cwd=root_path,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_sec,
                check=False,
            )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return GitCommandResult(
            ok=False,
            code=CODE_GIT_COMMAND_FAILED,
            reason=str(exc),
            command=command,
        )

    returncode = int(completed.returncode)
    ok = returncode == 0
    return GitCommandResult(
        ok=ok,
        code=CODE_READY if ok else CODE_GIT_COMMAND_FAILED,
        reason="command_succeeded" if ok else "command_failed",
        command=command,
        returncode=returncode,
        stdout=str(completed.stdout or ""),
        stderr=str(completed.stderr or ""),
    )


def _run_checkpoint_git_command(
    argv: Sequence[str],
    *,
    root: str | Path,
    runner: GitRunner | None = None,
    timeout_sec: int = 300,
) -> GitCommandResult:
    """Run the narrow git command set needed for owner checkpoint commits."""

    command = tuple(str(part) for part in argv if str(part).strip())
    validation_error = _checkpoint_git_command_error(command)
    if validation_error:
        return GitCommandResult(
            ok=False,
            code=CODE_FORBIDDEN_GIT_COMMAND,
            reason=validation_error,
            command=command,
        )

    root_path = Path(root).resolve()
    try:
        if runner is not None:
            completed = runner(command)
        else:
            completed = subprocess.run(
                list(command),
                cwd=root_path,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_sec,
                check=False,
            )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return GitCommandResult(
            ok=False,
            code=CODE_GIT_COMMAND_FAILED,
            reason=str(exc),
            command=command,
        )

    returncode = int(completed.returncode)
    ok = returncode == 0
    return GitCommandResult(
        ok=ok,
        code=CODE_READY if ok else CODE_GIT_COMMAND_FAILED,
        reason="command_succeeded" if ok else "command_failed",
        command=command,
        returncode=returncode,
        stdout=str(completed.stdout or ""),
        stderr=str(completed.stderr or ""),
    )


def _checkpoint_git_command_error(command: Sequence[str]) -> str:
    if len(command) < 2 or command[0] != "git":
        return "Only git subcommands through the git executable are allowed."
    subcommand = command[1]
    if subcommand in FORBIDDEN_GIT_SUBCOMMANDS:
        return "Forbidden git subcommand: {}".format(subcommand)
    if subcommand == "status":
        if tuple(command[2:]) == ("--short", "--untracked-files=all"):
            return ""
        return "Only read-only git status --short --untracked-files=all is allowed."
    if subcommand == "add":
        if tuple(command[2:]) == ("-A",):
            return ""
        return "Checkpoint commit staging must use git add -A."
    if subcommand == "commit":
        if len(command) == 4 and command[2] == "-m" and str(command[3]).strip():
            return ""
        return "git commit must use exactly one explicit -m message."
    if subcommand == "rev-parse":
        if tuple(command[2:]) == ("--verify", "HEAD"):
            return ""
        return "Only git rev-parse --verify HEAD is allowed."
    return "Unsupported git subcommand: {}".format(subcommand)


def _checkpoint_commit_failure(
    task_ref: str,
    reason: str,
    dirty_files: Sequence[GitStatusFile],
    message: str,
    commands: Sequence[GitCommandResult],
) -> CheckpointCommitResult:
    return CheckpointCommitResult(
        status=FAIL,
        code=CODE_CHECKPOINT_FAILED,
        reason=reason,
        task_ref=task_ref,
        dirty_files=tuple(dirty_files),
        message=message,
        commands=tuple(commands),
    )


def _commit_failure(
    root: Path,
    task_id: str,
    reason: str,
    readiness: CommitReadinessResult,
    commands: Sequence[GitCommandResult],
) -> LocalCommitResult:
    return LocalCommitResult(
        status=FAIL,
        code=CODE_GIT_COMMAND_FAILED,
        reason=reason,
        task_id=task_id,
        staged_files=tuple(
            sorted(_normalize_path(root, item.path) for item in readiness.changed_files)
        ),
        readiness=readiness,
        commands=tuple(commands),
    )


def _readiness(
    status: str,
    code: str,
    reason: str,
    *,
    task_id: str,
    change_ids: Sequence[str] = (),
    accepted_change_ids: Sequence[str] = (),
    approved_files: Sequence[str] = (),
    changed_files: Sequence[GitStatusFile] = (),
    blockers: Sequence[str] = (),
    git_status: GitCommandResult | None = None,
    machine_review_diagnostics: Sequence[Mapping[str, Any]] = (),
    blocking_non_pass_checks: Sequence[Mapping[str, Any]] = (),
    advisory_non_pass_checks: Sequence[Mapping[str, Any]] = (),
) -> CommitReadinessResult:
    return CommitReadinessResult(
        status=status,
        code=code,
        reason=reason,
        task_id=task_id,
        change_ids=tuple(change_ids),
        accepted_change_ids=tuple(accepted_change_ids),
        approved_files=tuple(approved_files),
        changed_files=tuple(changed_files),
        blockers=tuple(blockers),
        git_status=git_status,
        machine_review_diagnostics=tuple(machine_review_diagnostics),
        blocking_non_pass_checks=tuple(blocking_non_pass_checks),
        advisory_non_pass_checks=tuple(advisory_non_pass_checks),
    )


def _policy_blockers(policy: PipelinePolicy) -> list[str]:
    blockers: list[str] = []
    if policy.commit.allow_push:
        blockers.append("commit.allow_push")
    if policy.commit.allow_merge:
        blockers.append("commit.allow_merge")
    if policy.commit.create_local_commit and policy.commit.mode != CommitMode.LOCAL_ONLY:
        blockers.append("commit.mode")
    if policy.commit.create_local_commit and not policy.commit.require_commit_readiness:
        blockers.append("commit.require_commit_readiness")
    return blockers


def _gate_blocker(
    policy: PipelinePolicy,
    report_gate: ReportGateResult,
    machine_review: MachineReviewResult,
    codex_review: CodexReviewResult,
) -> tuple[str, str] | None:
    report_gate_acceptance = evaluate_report_gate_acceptance(report_gate, policy)
    if not report_gate_acceptance.allow:
        return (
            CODE_REPORT_NOT_PASS,
            "Codex Report Gate is not accepted for local commit: {}".format(
                report_gate_acceptance.reason
            ),
        )
    if machine_review.status == MACHINE_REVIEW_FAIL:
        return CODE_MACHINE_REVIEW_NOT_PASS, "Machine Review FAIL blocks local commit."
    if machine_review.status not in {MACHINE_REVIEW_PASS, MACHINE_REVIEW_WARN}:
        return (
            CODE_MACHINE_REVIEW_NOT_PASS,
            "Machine Review status is not accepted for local commit: {}".format(
                machine_review.status or "missing"
            ),
        )
    if disables_codex_review_by_policy(policy):
        return None
    if not requires_codex_review_approve(policy):
        return (
            CODE_POLICY_INVALID,
            "Local commit policy must explicitly require or disable Codex Review.",
        )
    if codex_review.status != CODEX_REVIEW_PASS or codex_review.verdict != VERDICT_APPROVE:
        return (
            CODE_CODEX_REVIEW_NOT_APPROVED,
            "Codex Review must APPROVE before local commit.",
        )
    return None


def _machine_warning_blocker(
    policy: PipelinePolicy,
    report_gate: ReportGateResult,
    machine_review: MachineReviewResult,
) -> tuple[str, str] | None:
    if machine_review.status != MACHINE_REVIEW_WARN:
        return None

    warning_checks = [
        check
        for check in machine_review.checks
        if check.blocking and check.status == MACHINE_REVIEW_WARN
    ]
    if not warning_checks:
        return None

    unsafe = [
        _machine_check_summary(check)
        for check in warning_checks
        if not _machine_warning_is_allowed(policy, report_gate, check)
    ]
    if unsafe:
        return (
            CODE_MACHINE_REVIEW_NOT_PASS,
            (
                "Machine Review WARN is not accepted for local commit; "
                "unapproved warning evidence: {}. Allowed warning evidence must "
                "be the policy-approved codex_report_gate report warning."
            ).format(", ".join(unsafe)),
        )
    return None


def _machine_warning_is_allowed(
    policy: PipelinePolicy,
    report_gate: ReportGateResult,
    check: MachineCheckEvidence,
) -> bool:
    if check.status != MACHINE_REVIEW_WARN:
        return True
    if check.name == "codex_report_gate" and report_gate.status == REPORT_GATE_WARN:
        return evaluate_report_gate_acceptance(report_gate, policy).allow
    return False


def _machine_check_summary(check: MachineCheckEvidence) -> str:
    return "{}={} code={} blocking={}".format(
        check.name,
        check.status,
        check.code,
        check.blocking,
    )


def _machine_review_diagnostics(
    machine_review: MachineReviewResult,
) -> tuple[dict[str, Any], ...]:
    return tuple(
        _machine_check_diagnostic(check)
        for check in machine_review.checks
        if check.status != MACHINE_REVIEW_PASS
    )


def _machine_review_diagnostic_kwargs(
    policy: PipelinePolicy,
    report_gate: ReportGateResult,
    machine_review: MachineReviewResult,
) -> dict[str, tuple[dict[str, Any], ...]]:
    diagnostics, blocking_checks, advisory_checks = _machine_review_diagnostic_groups(
        policy,
        report_gate,
        machine_review,
    )
    if not diagnostics and not blocking_checks and not advisory_checks:
        return {}
    return {
        "machine_review_diagnostics": diagnostics,
        "blocking_non_pass_checks": blocking_checks,
        "advisory_non_pass_checks": advisory_checks,
    }


def _machine_review_diagnostic_groups(
    policy: PipelinePolicy,
    report_gate: ReportGateResult,
    machine_review: MachineReviewResult,
) -> tuple[tuple[dict[str, Any], ...], tuple[dict[str, Any], ...], tuple[dict[str, Any], ...]]:
    diagnostics: list[dict[str, Any]] = []
    blocking_checks: list[dict[str, Any]] = []
    advisory_checks: list[dict[str, Any]] = []
    for check in machine_review.checks:
        if check.status == MACHINE_REVIEW_PASS:
            continue
        diagnostic = _machine_check_diagnostic(check)
        diagnostics.append(diagnostic)
        if _machine_check_blocks_commit(policy, report_gate, check):
            blocking_checks.append(diagnostic)
        else:
            advisory_checks.append(diagnostic)
    return tuple(diagnostics), tuple(blocking_checks), tuple(advisory_checks)


def _machine_check_blocks_commit(
    policy: PipelinePolicy,
    report_gate: ReportGateResult,
    check: MachineCheckEvidence,
) -> bool:
    if check.status == MACHINE_REVIEW_PASS:
        return False
    if check.name in REQUIRED_MACHINE_CHECKS:
        return True
    if check.status == MACHINE_REVIEW_WARN:
        return bool(check.blocking) and not _machine_warning_is_allowed(
            policy,
            report_gate,
            check,
        )
    return bool(check.blocking)


def _machine_check_diagnostic(check: MachineCheckEvidence) -> dict[str, Any]:
    data: dict[str, Any] = {
        "name": check.name,
        "status": check.status,
        "code": check.code,
        "reason": _bounded_machine_diagnostic_text(check.reason),
        "blocking": check.blocking,
        "command": list(check.command),
    }
    stdout_summary = _bounded_machine_diagnostic_text(check.stdout_summary)
    stderr_summary = _bounded_machine_diagnostic_text(check.stderr_summary)
    if stdout_summary:
        data["stdout_summary"] = stdout_summary
    if stderr_summary:
        data["stderr_summary"] = stderr_summary
    return data


def _bounded_machine_diagnostic_text(value: Any) -> str:
    text = str(value or "").strip()
    if len(text) <= MACHINE_DIAGNOSTIC_SUMMARY_LIMIT:
        return text
    return text[: MACHINE_DIAGNOSTIC_SUMMARY_LIMIT - 3].rstrip() + "..."


def _machine_check_blocker(
    machine_review: MachineReviewResult,
) -> tuple[str, str] | None:
    checks = {check.name: check for check in machine_review.checks}
    blocking_failures = [
        _machine_check_summary(check)
        for check in machine_review.checks
        if check.blocking and check.status == MACHINE_REVIEW_FAIL
    ]
    if blocking_failures:
        return (
            CODE_MACHINE_REVIEW_NOT_PASS,
            "Blocking Machine Review failure evidence blocks local commit: {}".format(
                ", ".join(blocking_failures)
            ),
        )
    missing = sorted(REQUIRED_MACHINE_CHECKS - set(checks))
    if missing:
        return (
            CODE_REQUIRED_CHECK_MISSING,
            "Machine Review did not include required commit readiness check(s): {}".format(
                ", ".join(missing)
            ),
        )
    not_pass = [
        "{}={}".format(name, checks[name].status)
        for name in sorted(REQUIRED_MACHINE_CHECKS)
        if checks[name].status != MACHINE_REVIEW_PASS
    ]
    if not_pass:
        return (
            CODE_REQUIRED_CHECK_NOT_PASS,
            "Required commit readiness check(s) are not PASS: {}".format(
                ", ".join(not_pass)
            ),
        )
    return None


def _approved_files(
    root: Path,
    report_gate: ReportGateResult,
    side_effects: Sequence[CommandResult],
    *,
    session: Mapping[str, Any] | None = None,
) -> set[str]:
    approved = {
        _normalize_path(root, path)
        for path in (*report_gate.changed_files, *report_gate.generated_files)
        if str(path).strip()
    }
    for effect in side_effects:
        for path in (*effect.changed_files, *effect.generated_files):
            if str(path).strip():
                approved.add(_normalize_path(root, path))
    approved.update(_session_owned_governed_control_files(root, session))
    approved.difference_update(_session_pre_existing_dirty_files(root, session))
    return approved


def _session_owned_governed_control_files(
    root: Path,
    session: Mapping[str, Any] | None,
) -> set[str]:
    evidence = _session_file_evidence(session)
    owned_files = _string_values(evidence.get(SESSION_OWNED_CHANGED_FILES_KEY))
    pre_existing = {
        _normalize_path(root, path)
        for path in _string_values(evidence.get(PRE_EXISTING_DIRTY_FILES_KEY))
    }
    return {
        normalized
        for normalized in (_normalize_path(root, path) for path in owned_files)
        if normalized not in pre_existing and _is_governed_project_control_file(normalized)
    }


def _session_pre_existing_dirty_files(
    root: Path,
    session: Mapping[str, Any] | None,
) -> set[str]:
    evidence = _session_file_evidence(session)
    return {
        _normalize_path(root, path)
        for path in _string_values(evidence.get(PRE_EXISTING_DIRTY_FILES_KEY))
    }


def _session_file_evidence(
    session: Mapping[str, Any] | None,
) -> Mapping[str, Any]:
    if not isinstance(session, Mapping):
        return {}
    evidence = session.get(FILE_EVIDENCE_KEY)
    return evidence if isinstance(evidence, Mapping) else {}


def _target_task_artifact_evidence(
    root: Path,
    report_gate: ReportGateResult,
) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                normalized
                for normalized in (
                    _normalize_path(root, path)
                    for path in (*report_gate.changed_files, *report_gate.generated_files)
                )
                if normalized and not _is_governed_project_control_file(normalized)
            }
        )
    )


def _is_governed_project_control_file(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in GOVERNED_PROJECT_CONTROL_PREFIXES)


def _session_by_id(
    state: Mapping[str, Any],
    session_id: str,
) -> Mapping[str, Any] | None:
    if not session_id:
        return None
    sessions = state.get("sessions")
    if not isinstance(sessions, Sequence) or isinstance(sessions, (str, bytes)):
        return None
    for session in sessions:
        if isinstance(session, Mapping) and str(session.get("id") or "") == session_id:
            return session
    return None


def _string_values(value: Any) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    return tuple(_unique_strings(str(item) for item in value))


def _parse_git_status(stdout: str) -> list[GitStatusFile]:
    files: list[GitStatusFile] = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        status = line[:2].strip() or line[:2]
        path = line[3:].strip() if len(line) > 3 else ""
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[1]
        if path:
            files.append(GitStatusFile(status=status, path=path))
    return files


def _git_command_error(command: Sequence[str]) -> str:
    if len(command) < 2 or command[0] != "git":
        return "Only git subcommands through the git executable are allowed."
    subcommand = command[1]
    if subcommand in FORBIDDEN_GIT_SUBCOMMANDS:
        return "Forbidden git subcommand: {}".format(subcommand)
    if subcommand == "status":
        if tuple(command[2:]) == ("--short", "--untracked-files=all"):
            return ""
        return "Only read-only git status --short --untracked-files=all is allowed."
    if subcommand == "add":
        if len(command) < 4 or command[2] != "--":
            return "git add must use an explicit path list after --."
        if any(str(path).startswith("-") or str(path) in {".", "/"} for path in command[3:]):
            return "git add paths must be explicit file paths, not options or roots."
        return ""
    if subcommand == "commit":
        if len(command) == 4 and command[2] == "-m" and str(command[3]).strip():
            return ""
        return "git commit must use exactly one explicit -m message."
    if subcommand == "rev-parse":
        if tuple(command[2:]) == ("--verify", "HEAD"):
            return ""
        return "Only git rev-parse --verify HEAD is allowed."
    return "Unsupported git subcommand: {}".format(subcommand)


def _checkpoint_commit_message(task_ref: str) -> str:
    task_text = " ".join(str(task_ref or "").split())
    subject = "Checkpoint before Web Run"
    if task_text:
        subject = "{}: {}".format(subject, task_text)
    if len(subject) > 72:
        subject = subject[:69].rstrip() + "..."
    return subject


def _task_by_id(tasks_state: Any, task_id: str) -> Mapping[str, Any]:
    if not isinstance(tasks_state, Mapping):
        return {}
    for task in tasks_state.get("tasks", []):
        if isinstance(task, Mapping) and str(task.get("id") or "") == task_id:
            return task
    return {}


def _linked_changes_for_task(
    task_refs: Sequence[str],
    evolution_state: Any,
) -> list[Mapping[str, Any]]:
    if not isinstance(evolution_state, Mapping):
        return []
    selected_refs = {str(item) for item in task_refs if str(item).strip()}
    linked: list[Mapping[str, Any]] = []
    for change in evolution_state.get("changes", []):
        if not isinstance(change, Mapping):
            continue
        linked_tasks = change.get("linked_tasks") or []
        if isinstance(linked_tasks, Sequence) and not isinstance(
            linked_tasks,
            (str, bytes),
        ):
            if selected_refs & {str(item) for item in linked_tasks}:
                linked.append(change)
    return linked


def _task_reference_values(task: Mapping[str, Any], task_id: str) -> tuple[str, ...]:
    refs = [
        task_id,
        str(task.get("id") or ""),
        str(task.get("ref") or ""),
        str(task.get("uid") or ""),
        str(task.get("legacy_id") or ""),
    ]
    aliases = task.get("aliases")
    if isinstance(aliases, Sequence) and not isinstance(aliases, (str, bytes)):
        refs.extend(str(alias) for alias in aliases)
    return tuple(_unique_strings(refs))


def _unique_strings(values: Sequence[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in result:
            result.append(text)
    return result


def _commit_message(
    root: Path,
    task_id: str,
    session_id: str,
    accepted_change_ids: Sequence[str],
) -> str:
    task = _task_by_id(load_reference_state(root).get("tasks"), task_id)
    task_ref = str(task.get("ref") or task.get("legacy_id") or task.get("id") or task_id)
    title = " ".join(str(task.get("title") or "completed pipeline task").split())
    subject = "{}: {}".format(task_ref, title)
    if len(subject) > 72:
        subject = subject[:69].rstrip() + "..."
    lines = [
        subject,
        "",
        "Task: {}".format(task_id),
        "Ref: {}".format(task_ref),
        "Pipeline-Session: {}".format(session_id),
    ]
    if accepted_change_ids:
        lines.append("Changes: {}".format(", ".join(accepted_change_ids)))
    return "\n".join(lines)


def _normalize_path(root: Path, path: str | Path) -> str:
    raw = Path(str(path))
    if raw.is_absolute():
        try:
            return raw.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            return raw.as_posix().lstrip("/")
    text = raw.as_posix()
    if text.startswith("./"):
        text = text[2:]
    return text.lstrip("/")

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
from .machine_review import PASS as MACHINE_REVIEW_PASS
from .machine_review import MachineReviewResult
from .policy import (
    CommitMode,
    PipelinePolicy,
    disables_codex_review_by_policy,
    requires_codex_review_approve,
)
from .report_gate import PASS as REPORT_GATE_PASS
from .report_gate import ReportGateResult
from .state import load_reference_state


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

    @property
    def ok(self) -> bool:
        return self.status == PASS

    def to_dict(self) -> dict[str, Any]:
        return {
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


def evaluate_commit_readiness(
    *,
    root: str | Path,
    task_id: str,
    policy: PipelinePolicy,
    report_gate: ReportGateResult,
    machine_review: MachineReviewResult,
    codex_review: CodexReviewResult,
    side_effects: Sequence[CommandResult] = (),
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
        )

    approved_files = _approved_files(root_path, report_gate, side_effects)
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
        )

    return _readiness(
        PASS,
        CODE_READY,
        "Local commit readiness is green.",
        task_id=task_id,
        change_ids=change_ids,
        accepted_change_ids=accepted_change_ids,
        approved_files=tuple(sorted(approved_files)),
        changed_files=changed_files,
        git_status=git_status,
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
    if report_gate.status != REPORT_GATE_PASS:
        return CODE_REPORT_NOT_PASS, "Codex Report Gate must be PASS before local commit."
    if machine_review.status != MACHINE_REVIEW_PASS:
        return CODE_MACHINE_REVIEW_NOT_PASS, "Machine Review must be PASS before local commit."
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


def _machine_check_blocker(
    machine_review: MachineReviewResult,
) -> tuple[str, str] | None:
    checks = {check.name: check for check in machine_review.checks}
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
    return approved


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

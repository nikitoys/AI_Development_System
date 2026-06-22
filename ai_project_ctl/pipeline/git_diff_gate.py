"""Read-only git diff evidence gate for supervised pipeline runs."""

from __future__ import annotations

import fnmatch
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Sequence


PASS = "pass"
BLOCKED = "blocked"
FAIL = "fail"

CODE_PASS = "GIT_DIFF_GATE_PASS"
CODE_DIFF_MISMATCH = "GIT_DIFF_GATE_DIFF_MISMATCH"
CODE_NOT_REPOSITORY = "GIT_DIFF_GATE_NOT_REPOSITORY"
CODE_GIT_UNAVAILABLE = "GIT_DIFF_GATE_GIT_UNAVAILABLE"
CODE_GIT_COMMAND_FAILED = "GIT_DIFF_GATE_COMMAND_FAILED"
CODE_FORBIDDEN_GIT_COMMAND = "GIT_DIFF_GATE_FORBIDDEN_GIT_COMMAND"
CODE_ALLOWED_FILES_PASS = "ALLOWED_FILES_GATE_PASS"
CODE_ALLOWED_FILES_OUT_OF_SCOPE = "ALLOWED_FILES_GATE_OUT_OF_SCOPE"
CODE_PROTECTED_FILES_PASS = "PROTECTED_FILES_GATE_PASS"
CODE_PROTECTED_FILES_BLOCKED = "PROTECTED_FILES_GATE_BLOCKED"

REASON_PROTECTED_STATE_CHANGED = "protected_state_changed"
REASON_PROTECTED_EVENT_CHANGED = "protected_event_changed"
REASON_REPORTED_PROTECTED_STATE_CHANGED = "reported_protected_state_changed"
REASON_REPORTED_PROTECTED_EVENT_CHANGED = "reported_protected_event_changed"
REASON_UNGOVERNED_GENERATED_CHANGED = "ungoverned_generated_changed"

DEFAULT_GOVERNED_GENERATED_FILES = (
    "AI_PROJECT/generated/PIPELINE_AUDIT.md",
)

DEFAULT_TIMEOUT_SEC = 30

GitRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class GitCommandResult:
    """Result from one read-only git command."""

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
class GitStatusEntry:
    """One file entry from git status porcelain output."""

    status: str
    path: str

    @property
    def index_status(self) -> str:
        return self.status[0] if self.status else " "

    @property
    def worktree_status(self) -> str:
        return self.status[1] if len(self.status) > 1 else " "

    @property
    def is_untracked(self) -> bool:
        return self.status == "??"

    @property
    def is_ignored(self) -> bool:
        return self.status == "!!"

    @property
    def is_staged(self) -> bool:
        return self.index_status not in {" ", "?", "!"}

    @property
    def is_unstaged(self) -> bool:
        return self.worktree_status not in {" ", "?", "!"}

    @property
    def is_tracked_change(self) -> bool:
        return not self.is_untracked and not self.is_ignored

    def to_dict(self) -> dict[str, str]:
        return {"status": self.status, "path": self.path}


@dataclass(frozen=True)
class GitDiffGateResult:
    """Compact gate result with normalized working-tree evidence."""

    status: str
    code: str
    reason: str
    repo_root: str
    expected_files: tuple[str, ...] = ()
    changed_files: tuple[str, ...] = ()
    tracked_files: tuple[str, ...] = ()
    staged_files: tuple[str, ...] = ()
    unstaged_files: tuple[str, ...] = ()
    untracked_files: tuple[str, ...] = ()
    unexpected_files: tuple[str, ...] = ()
    missing_files: tuple[str, ...] = ()
    status_entries: tuple[GitStatusEntry, ...] = ()
    commands: tuple[GitCommandResult, ...] = ()

    @property
    def ok(self) -> bool:
        return self.status == PASS

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "code": self.code,
            "reason": self.reason,
            "repo_root": self.repo_root,
            "expected_files": list(self.expected_files),
            "changed_files": list(self.changed_files),
            "tracked_files": list(self.tracked_files),
            "staged_files": list(self.staged_files),
            "unstaged_files": list(self.unstaged_files),
            "untracked_files": list(self.untracked_files),
            "unexpected_files": list(self.unexpected_files),
            "missing_files": list(self.missing_files),
            "status_entries": [entry.to_dict() for entry in self.status_entries],
            "commands": [command.to_dict() for command in self.commands],
        }


@dataclass(frozen=True)
class AllowedFilesGateResult:
    """Actual-diff file-scope evidence for the selected task."""

    status: str
    code: str
    reason: str
    actual_changed_files: tuple[str, ...] = ()
    allowed_patterns: tuple[str, ...] = ()
    governed_generated_files: tuple[str, ...] = ()
    allowed_files: tuple[str, ...] = ()
    governed_generated_matches: tuple[str, ...] = ()
    out_of_scope_files: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.status == PASS

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "code": self.code,
            "reason": self.reason,
            "actual_changed_files": list(self.actual_changed_files),
            "allowed_patterns": list(self.allowed_patterns),
            "governed_generated_files": list(self.governed_generated_files),
            "allowed_files": list(self.allowed_files),
            "governed_generated_matches": list(self.governed_generated_matches),
            "out_of_scope_files": list(self.out_of_scope_files),
        }


@dataclass(frozen=True)
class ProtectedFileViolation:
    """One protected project-control path violation."""

    path: str
    reason_code: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {
            "path": self.path,
            "reason_code": self.reason_code,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ProtectedFilesGateResult:
    """Actual-diff protected project-control evidence for verify."""

    status: str
    code: str
    reason: str
    actual_changed_files: tuple[str, ...] = ()
    reported_files: tuple[str, ...] = ()
    governed_control_files: tuple[str, ...] = ()
    governed_generated_files: tuple[str, ...] = ()
    allowed_protected_files: tuple[str, ...] = ()
    violations: tuple[ProtectedFileViolation, ...] = ()

    @property
    def ok(self) -> bool:
        return self.status == PASS

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "code": self.code,
            "reason": self.reason,
            "actual_changed_files": list(self.actual_changed_files),
            "reported_files": list(self.reported_files),
            "governed_control_files": list(self.governed_control_files),
            "governed_generated_files": list(self.governed_generated_files),
            "allowed_protected_files": list(self.allowed_protected_files),
            "violations": [violation.to_dict() for violation in self.violations],
        }


def evaluate_git_diff_gate(
    *,
    root: str | Path,
    expected_files: Sequence[str | Path] = (),
    runner: GitRunner | None = None,
    timeout_sec: int = DEFAULT_TIMEOUT_SEC,
) -> GitDiffGateResult:
    """Inspect the working tree and compare actual dirty files to expectations.

    `expected_files` is the complete dirty-file set expected by the caller. The
    default empty expectation means a clean working tree is required.
    """

    root_path = Path(root).resolve()
    commands: list[GitCommandResult] = []
    if not root_path.is_dir():
        return _result(
            BLOCKED,
            CODE_NOT_REPOSITORY,
            "path_is_not_git_repository",
            repo_root="",
            commands=commands,
        )

    repo_result = _run_git(
        ("git", "rev-parse", "--show-toplevel"),
        cwd=root_path,
        runner=runner,
        timeout_sec=timeout_sec,
    )
    commands.append(repo_result)
    if not repo_result.ok:
        if repo_result.code == CODE_GIT_UNAVAILABLE:
            return _result(
                FAIL,
                CODE_GIT_UNAVAILABLE,
                "git_unavailable",
                repo_root="",
                commands=commands,
            )
        return _result(
            BLOCKED,
            CODE_NOT_REPOSITORY,
            "path_is_not_git_repository",
            repo_root="",
            commands=commands,
        )

    repo_root = Path(repo_result.stdout.strip().splitlines()[0]).resolve()
    status_result = _run_git(
        ("git", "status", "--porcelain=v1", "-z", "--untracked-files=all"),
        cwd=repo_root,
        runner=runner,
        timeout_sec=timeout_sec,
    )
    staged_diff_result = _run_git(
        ("git", "diff", "--cached", "--name-only", "-z", "--"),
        cwd=repo_root,
        runner=runner,
        timeout_sec=timeout_sec,
    )
    unstaged_diff_result = _run_git(
        ("git", "diff", "--name-only", "-z", "--"),
        cwd=repo_root,
        runner=runner,
        timeout_sec=timeout_sec,
    )
    commands.extend((status_result, staged_diff_result, unstaged_diff_result))

    failed = next((command for command in commands if not command.ok), None)
    if failed is not None:
        return _result(
            FAIL,
            failed.code,
            failed.reason,
            repo_root=str(repo_root),
            commands=commands,
        )

    status_entries = tuple(_parse_status_entries(status_result.stdout, repo_root))
    staged_from_status = {
        entry.path
        for entry in status_entries
        if entry.is_tracked_change and entry.is_staged
    }
    unstaged_from_status = {
        entry.path
        for entry in status_entries
        if entry.is_tracked_change and entry.is_unstaged
    }
    tracked_from_status = {
        entry.path for entry in status_entries if entry.is_tracked_change
    }
    untracked_files = _sorted_unique(
        entry.path for entry in status_entries if entry.is_untracked
    )
    staged_files = _sorted_unique(
        (*staged_from_status, *_parse_nul_paths(staged_diff_result.stdout, repo_root))
    )
    unstaged_files = _sorted_unique(
        (
            *unstaged_from_status,
            *_parse_nul_paths(unstaged_diff_result.stdout, repo_root),
        )
    )
    tracked_files = _sorted_unique(
        (*tracked_from_status, *staged_files, *unstaged_files)
    )
    changed_files = _sorted_unique((*tracked_files, *untracked_files))
    normalized_expected = _sorted_unique(
        _normalize_path(repo_root, path) for path in expected_files
    )

    actual_set = set(changed_files)
    expected_set = set(normalized_expected)
    unexpected_files = _sorted_unique(actual_set - expected_set)
    missing_files = _sorted_unique(expected_set - actual_set)

    if unexpected_files or missing_files:
        return _result(
            BLOCKED,
            CODE_DIFF_MISMATCH,
            "working_tree_diff_does_not_match_expected_files",
            repo_root=str(repo_root),
            expected_files=normalized_expected,
            changed_files=changed_files,
            tracked_files=tracked_files,
            staged_files=staged_files,
            unstaged_files=unstaged_files,
            untracked_files=untracked_files,
            unexpected_files=unexpected_files,
            missing_files=missing_files,
            status_entries=status_entries,
            commands=commands,
        )

    reason = (
        "working_tree_clean"
        if not changed_files
        else "working_tree_matches_expected_files"
    )
    return _result(
        PASS,
        CODE_PASS,
        reason,
        repo_root=str(repo_root),
        expected_files=normalized_expected,
        changed_files=changed_files,
        tracked_files=tracked_files,
        staged_files=staged_files,
        unstaged_files=unstaged_files,
        untracked_files=untracked_files,
        status_entries=status_entries,
        commands=commands,
    )


def evaluate_protected_files_gate(
    *,
    root: str | Path,
    changed_files: Sequence[str | Path],
    reported_changed_files: Sequence[str | Path] = (),
    reported_generated_files: Sequence[str | Path] = (),
    governed_control_files: Sequence[str | Path] = (),
    governed_generated_files: Sequence[str | Path] = (),
) -> ProtectedFilesGateResult:
    """Check actual dirty files for protected project-control violations."""

    root_path = Path(root).resolve()
    actual_files = _sorted_unique(
        _normalize_path(root_path, path) for path in changed_files
    )
    reported_files = _sorted_unique(
        (
            *(_normalize_path(root_path, path) for path in reported_changed_files),
            *(_normalize_path(root_path, path) for path in reported_generated_files),
        )
    )
    reported_set = set(reported_files)
    governed_control_set = set(
        _sorted_unique(
            (
                *_registered_governed_control_files(root_path),
                *(_normalize_path(root_path, path) for path in governed_control_files),
            )
        )
    )
    governed_generated_set = set(
        _sorted_unique(
            (
                *_registered_governed_generated_files(root_path),
                *(
                    _normalize_path(root_path, path)
                    for path in DEFAULT_GOVERNED_GENERATED_FILES
                ),
                *(
                    _normalize_path(root_path, path)
                    for path in governed_generated_files
                ),
            )
        )
    )

    allowed: list[str] = []
    violations: list[ProtectedFileViolation] = []
    for path in actual_files:
        if _is_state_path(path):
            if path in reported_set:
                violations.append(
                    ProtectedFileViolation(
                        path=path,
                        reason_code=REASON_REPORTED_PROTECTED_STATE_CHANGED,
                        reason="reported change to protected project-control state",
                    )
                )
            elif path in governed_control_set:
                allowed.append(path)
            else:
                violations.append(
                    ProtectedFileViolation(
                        path=path,
                        reason_code=REASON_PROTECTED_STATE_CHANGED,
                        reason="actual change to protected project-control state",
                    )
                )
        elif _is_event_path(path):
            if path in reported_set:
                violations.append(
                    ProtectedFileViolation(
                        path=path,
                        reason_code=REASON_REPORTED_PROTECTED_EVENT_CHANGED,
                        reason="reported change to protected project-control events",
                    )
                )
            elif path in governed_control_set:
                allowed.append(path)
            else:
                violations.append(
                    ProtectedFileViolation(
                        path=path,
                        reason_code=REASON_PROTECTED_EVENT_CHANGED,
                        reason="actual change to protected project-control events",
                    )
                )
        elif _is_generated_path(path):
            if path in governed_generated_set:
                allowed.append(path)
            else:
                violations.append(
                    ProtectedFileViolation(
                        path=path,
                        reason_code=REASON_UNGOVERNED_GENERATED_CHANGED,
                        reason="actual change to ungoverned generated project-control output",
                    )
                )

    if violations:
        blocked_paths = ", ".join(violation.path for violation in violations)
        return ProtectedFilesGateResult(
            status=BLOCKED,
            code=CODE_PROTECTED_FILES_BLOCKED,
            reason="protected project-control files changed: {}".format(blocked_paths),
            actual_changed_files=actual_files,
            reported_files=reported_files,
            governed_control_files=tuple(sorted(governed_control_set)),
            governed_generated_files=tuple(sorted(governed_generated_set)),
            allowed_protected_files=_sorted_unique(allowed),
            violations=tuple(violations),
        )

    return ProtectedFilesGateResult(
        status=PASS,
        code=CODE_PROTECTED_FILES_PASS,
        reason="protected project-control file changes are governed or absent",
        actual_changed_files=actual_files,
        reported_files=reported_files,
        governed_control_files=tuple(sorted(governed_control_set)),
        governed_generated_files=tuple(sorted(governed_generated_set)),
        allowed_protected_files=_sorted_unique(allowed),
    )


def evaluate_allowed_files_gate(
    *,
    root: str | Path,
    changed_files: Sequence[str | Path],
    allowed_files: Sequence[str] = (),
    generated_files: Sequence[str | Path] = (),
) -> AllowedFilesGateResult:
    """Check actual dirty files against task allowed_files and generated evidence."""

    root_path = Path(root).resolve()
    actual_files = _sorted_unique(
        _normalize_path(root_path, path) for path in changed_files
    )
    allowed_patterns = _allowed_file_patterns(root_path, allowed_files)
    governed_generated_files = _sorted_unique(
        normalized
        for normalized in (_normalize_path(root_path, path) for path in generated_files)
        if _is_generated_path(normalized)
    )
    governed_generated_set = set(governed_generated_files)

    allowed_matches: list[str] = []
    generated_matches: list[str] = []
    out_of_scope: list[str] = []
    for path in actual_files:
        if _matches_allowed_file(path, allowed_patterns):
            allowed_matches.append(path)
        elif path in governed_generated_set:
            generated_matches.append(path)
        else:
            out_of_scope.append(path)

    if out_of_scope:
        out_of_scope_files = _sorted_unique(out_of_scope)
        return AllowedFilesGateResult(
            status=BLOCKED,
            code=CODE_ALLOWED_FILES_OUT_OF_SCOPE,
            reason="actual changed files outside task allowed_files: {}".format(
                ", ".join(out_of_scope_files)
            ),
            actual_changed_files=actual_files,
            allowed_patterns=allowed_patterns,
            governed_generated_files=governed_generated_files,
            allowed_files=_sorted_unique(allowed_matches),
            governed_generated_matches=_sorted_unique(generated_matches),
            out_of_scope_files=out_of_scope_files,
        )

    return AllowedFilesGateResult(
        status=PASS,
        code=CODE_ALLOWED_FILES_PASS,
        reason=(
            "actual changed files are within task allowed_files or explicit "
            "generated output evidence"
        ),
        actual_changed_files=actual_files,
        allowed_patterns=allowed_patterns,
        governed_generated_files=governed_generated_files,
        allowed_files=_sorted_unique(allowed_matches),
        governed_generated_matches=_sorted_unique(generated_matches),
    )


def _run_git(
    argv: Sequence[str],
    *,
    cwd: Path,
    runner: GitRunner | None,
    timeout_sec: int,
) -> GitCommandResult:
    command = tuple(str(part) for part in argv if str(part).strip())
    validation_error = _read_only_git_command_error(command)
    if validation_error:
        return GitCommandResult(
            ok=False,
            code=CODE_FORBIDDEN_GIT_COMMAND,
            reason=validation_error,
            command=command,
        )

    try:
        if runner is not None:
            completed = runner(command)
        else:
            completed = subprocess.run(
                list(command),
                cwd=cwd,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_sec,
                check=False,
            )
    except FileNotFoundError:
        return GitCommandResult(
            ok=False,
            code=CODE_GIT_UNAVAILABLE,
            reason="git_unavailable",
            command=command,
        )
    except subprocess.TimeoutExpired:
        return GitCommandResult(
            ok=False,
            code=CODE_GIT_COMMAND_FAILED,
            reason="git_command_timed_out",
            command=command,
        )
    except OSError:
        return GitCommandResult(
            ok=False,
            code=CODE_GIT_COMMAND_FAILED,
            reason="git_command_error",
            command=command,
        )

    returncode = int(completed.returncode)
    return GitCommandResult(
        ok=returncode == 0,
        code=CODE_PASS if returncode == 0 else CODE_GIT_COMMAND_FAILED,
        reason="command_succeeded" if returncode == 0 else "git_command_failed",
        command=command,
        returncode=returncode,
        stdout=str(completed.stdout or ""),
        stderr=str(completed.stderr or ""),
    )


def _read_only_git_command_error(command: Sequence[str]) -> str:
    if len(command) < 2 or command[0] != "git":
        return "Only git commands through the git executable are allowed."
    subcommand = command[1]
    allowed = {
        ("git", "rev-parse", "--show-toplevel"),
        ("git", "status", "--porcelain=v1", "-z", "--untracked-files=all"),
        ("git", "diff", "--cached", "--name-only", "-z", "--"),
        ("git", "diff", "--name-only", "-z", "--"),
    }
    if tuple(command) in allowed:
        return ""
    return "Unsupported read-only git command: {}".format(" ".join(command))


def _parse_status_entries(stdout: str, repo_root: Path) -> list[GitStatusEntry]:
    entries: list[GitStatusEntry] = []
    records = stdout.split("\0")
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        status = record[:2]
        path = record[3:] if len(record) > 3 else ""
        if "R" in status or "C" in status:
            index += 1
        normalized = _normalize_path(repo_root, path)
        if normalized:
            entries.append(GitStatusEntry(status=status, path=normalized))
    return entries


def _parse_nul_paths(stdout: str, repo_root: Path) -> tuple[str, ...]:
    return tuple(
        _normalize_path(repo_root, item)
        for item in stdout.split("\0")
        if item.strip()
    )


def _normalize_path(repo_root: Path, path: str | Path) -> str:
    text = str(path).strip().replace("\\", "/")
    if not text:
        return ""
    candidate = Path(text)
    try:
        if candidate.is_absolute():
            return candidate.resolve(strict=False).relative_to(repo_root).as_posix()
        return (repo_root / candidate).resolve(strict=False).relative_to(repo_root).as_posix()
    except ValueError:
        normalized = PurePosixPath(text).as_posix()
        while normalized.startswith("./"):
            normalized = normalized[2:]
        return normalized


def _allowed_file_patterns(repo_root: Path, value: Sequence[str]) -> tuple[str, ...]:
    patterns: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        pattern = item.strip()
        if not pattern:
            continue
        if " if " in pattern:
            pattern = pattern.split(" if ", 1)[0].strip()
        patterns.append(_normalize_path(repo_root, pattern))
    return _sorted_unique(patterns)


def _matches_allowed_file(path: str, patterns: Sequence[str]) -> bool:
    for pattern in patterns:
        if pattern.endswith("/**"):
            prefix = pattern[:-3].rstrip("/")
            if path == prefix or path.startswith(prefix + "/"):
                return True
        if fnmatch.fnmatchcase(path, pattern):
            return True
    return False


def _is_generated_path(path: str) -> bool:
    return path.startswith("AI_PROJECT/generated/")


def _is_state_path(path: str) -> bool:
    return path.startswith("AI_PROJECT/state/")


def _is_event_path(path: str) -> bool:
    return path.startswith("AI_PROJECT/events/")


def _registered_governed_control_files(repo_root: Path) -> tuple[str, ...]:
    values: list[str] = []
    for descriptor in _registered_command_descriptors():
        for field in ("writes_state", "event_logs"):
            items = descriptor.get(field)
            if isinstance(items, list):
                values.extend(
                    _normalize_path(repo_root, item)
                    for item in items
                    if isinstance(item, str)
                )
    return _sorted_unique(values)


def _registered_governed_generated_files(repo_root: Path) -> tuple[str, ...]:
    values: list[str] = []
    for descriptor in _registered_command_descriptors():
        items = descriptor.get("generated_files")
        if isinstance(items, list):
            values.extend(
                _normalize_path(repo_root, item)
                for item in items
                if isinstance(item, str)
            )
    return _sorted_unique(values)


def _registered_command_descriptors() -> tuple[dict[str, Any], ...]:
    try:
        from ai_project_ctl.core.registry import command_list
    except Exception:
        return ()
    try:
        return tuple(
            item for item in command_list(include_planned=False) if isinstance(item, dict)
        )
    except Exception:
        return ()


def _sorted_unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values if str(value).strip()}))


def _result(
    status: str,
    code: str,
    reason: str,
    *,
    repo_root: str,
    expected_files: Sequence[str] = (),
    changed_files: Sequence[str] = (),
    tracked_files: Sequence[str] = (),
    staged_files: Sequence[str] = (),
    unstaged_files: Sequence[str] = (),
    untracked_files: Sequence[str] = (),
    unexpected_files: Sequence[str] = (),
    missing_files: Sequence[str] = (),
    status_entries: Sequence[GitStatusEntry] = (),
    commands: Sequence[GitCommandResult] = (),
) -> GitDiffGateResult:
    return GitDiffGateResult(
        status=status,
        code=code,
        reason=reason,
        repo_root=repo_root,
        expected_files=tuple(expected_files),
        changed_files=tuple(changed_files),
        tracked_files=tuple(tracked_files),
        staged_files=tuple(staged_files),
        unstaged_files=tuple(unstaged_files),
        untracked_files=tuple(untracked_files),
        unexpected_files=tuple(unexpected_files),
        missing_files=tuple(missing_files),
        status_entries=tuple(status_entries),
        commands=tuple(commands),
    )

"""Reusable git status snapshot helpers for pipeline file evidence."""

from __future__ import annotations

import fnmatch
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence


GIT_STATUS_SHORT_COMMAND = ("git", "status", "--short", "--untracked-files=all")
DEFAULT_TIMEOUT_SEC = 300

GitRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


class GitStatusError(RuntimeError):
    """Raised when a git status snapshot cannot be captured."""


@dataclass(frozen=True)
class GitStatusEntry:
    """One normalized path entry from git status --short output."""

    status: str
    path: str

    def to_dict(self) -> dict[str, str]:
        return {"status": self.status, "path": self.path}


@dataclass(frozen=True)
class GitStatusSnapshot:
    """Normalized dirty-file snapshot from git status --short output."""

    entries: tuple[GitStatusEntry, ...] = ()

    @property
    def dirty_paths(self) -> tuple[str, ...]:
        return _sorted_unique(entry.path for entry in self.entries)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entries": [entry.to_dict() for entry in self.entries],
            "dirty_paths": list(self.dirty_paths),
        }


@dataclass(frozen=True)
class GitStatusAllowedFiles:
    """File delta split against a task allowed_files contract."""

    allowed_paths: tuple[str, ...] = ()
    out_of_scope_paths: tuple[str, ...] = ()
    allowed_patterns: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed_paths": list(self.allowed_paths),
            "out_of_scope_paths": list(self.out_of_scope_paths),
            "allowed_patterns": list(self.allowed_patterns),
        }


@dataclass(frozen=True)
class WorktreeDirtyPreflight:
    """Preflight result for blocking new runs on a dirty git worktree."""

    checked: bool
    available: bool
    entries: tuple[GitStatusEntry, ...] = ()
    dirty_paths: tuple[str, ...] = ()
    error: str = ""

    @property
    def should_block(self) -> bool:
        return bool(self.dirty_paths) or (self.checked and not self.available)

    @property
    def reason(self) -> str:
        if self.dirty_paths:
            return "worktree_dirty"
        if self.checked and not self.available:
            return "worktree_status_unavailable"
        return "worktree_clean"

    def to_dict(self) -> dict[str, Any]:
        return {
            "checked": self.checked,
            "available": self.available,
            "entries": [entry.to_dict() for entry in self.entries],
            "dirty_paths": list(self.dirty_paths),
            "reason": self.reason,
            "error": self.error,
        }


def capture_git_status_snapshot(
    *,
    root: str | Path,
    runner: GitRunner | None = None,
    timeout_sec: int = DEFAULT_TIMEOUT_SEC,
) -> GitStatusSnapshot:
    """Run git status --short --untracked-files=all and parse a snapshot."""

    root_path = Path(root).resolve()
    try:
        if runner is not None:
            completed = runner(GIT_STATUS_SHORT_COMMAND)
        else:
            completed = subprocess.run(
                list(GIT_STATUS_SHORT_COMMAND),
                cwd=root_path,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_sec,
                check=False,
            )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GitStatusError(str(exc)) from exc

    returncode = int(completed.returncode)
    if returncode != 0:
        reason = str(completed.stderr or "").strip() or "git status failed"
        raise GitStatusError(reason)
    return parse_git_status_snapshot(str(completed.stdout or ""), root=root_path)


def capture_worktree_dirty_preflight(
    *,
    root: str | Path,
    runner: GitRunner | None = None,
    timeout_sec: int = DEFAULT_TIMEOUT_SEC,
) -> WorktreeDirtyPreflight:
    """Capture dirty worktree state for pre-run safety checks."""

    root_path = Path(root).resolve()
    if runner is None and not _looks_like_git_worktree(root_path):
        return WorktreeDirtyPreflight(checked=False, available=False)
    try:
        snapshot = capture_git_status_snapshot(
            root=root_path,
            runner=runner,
            timeout_sec=timeout_sec,
        )
    except GitStatusError as exc:
        return WorktreeDirtyPreflight(
            checked=True,
            available=False,
            error=str(exc),
        )
    return WorktreeDirtyPreflight(
        checked=True,
        available=True,
        entries=snapshot.entries,
        dirty_paths=snapshot.dirty_paths,
    )


def parse_git_status_snapshot(stdout: str, *, root: str | Path) -> GitStatusSnapshot:
    """Parse git status --short output into normalized repository-relative paths."""

    entries: list[GitStatusEntry] = []
    root_path = Path(root).resolve()
    for line in stdout.splitlines():
        if not line.strip():
            continue
        status = line[:2].strip() or line[:2]
        path = line[3:].strip() if len(line) > 3 else ""
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[1]
        if not path:
            continue
        normalized = normalize_git_status_path(root_path, path)
        if normalized:
            entries.append(GitStatusEntry(status=status, path=normalized))
    return GitStatusSnapshot(entries=tuple(entries))


def dirty_paths_after_baseline(
    baseline: GitStatusSnapshot,
    current: GitStatusSnapshot,
) -> tuple[str, ...]:
    """Return dirty paths present after baseline, excluding pre-existing dirt."""

    baseline_paths = set(baseline.dirty_paths)
    return _sorted_unique(
        path for path in current.dirty_paths if path not in baseline_paths
    )


def filter_paths_by_allowed_files(
    paths: Sequence[str | Path],
    allowed_files: Sequence[str],
    *,
    root: str | Path = ".",
) -> GitStatusAllowedFiles:
    """Split repository-relative paths by task allowed_files patterns."""

    root_path = Path(root).resolve()
    normalized_paths = _sorted_unique(
        normalize_git_status_path(root_path, path) for path in paths
    )
    allowed_patterns = _allowed_file_patterns(root_path, allowed_files)
    allowed: list[str] = []
    out_of_scope: list[str] = []
    for path in normalized_paths:
        if _matches_allowed_file(path, allowed_patterns):
            allowed.append(path)
        else:
            out_of_scope.append(path)
    return GitStatusAllowedFiles(
        allowed_paths=_sorted_unique(allowed),
        out_of_scope_paths=_sorted_unique(out_of_scope),
        allowed_patterns=allowed_patterns,
    )


def normalize_git_status_path(root: str | Path, path: str | Path) -> str:
    """Normalize paths the same way commit readiness normalizes status paths."""

    root_path = Path(root)
    raw = Path(str(path))
    if raw.is_absolute():
        try:
            return raw.resolve().relative_to(root_path.resolve()).as_posix()
        except ValueError:
            return raw.as_posix().lstrip("/")
    text = raw.as_posix()
    if text.startswith("./"):
        text = text[2:]
    return text.lstrip("/")


def _allowed_file_patterns(
    root: Path,
    allowed_files: Sequence[str],
) -> tuple[str, ...]:
    patterns: list[str] = []
    for item in allowed_files:
        if not isinstance(item, str):
            continue
        pattern = item.strip()
        if not pattern:
            continue
        if " if " in pattern:
            pattern = pattern.split(" if ", 1)[0].strip()
        patterns.append(normalize_git_status_path(root, pattern))
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


def _looks_like_git_worktree(root: Path) -> bool:
    current = root
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return True
    return False


def _sorted_unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values if str(value).strip()}))


__all__ = [
    "DEFAULT_TIMEOUT_SEC",
    "GIT_STATUS_SHORT_COMMAND",
    "GitRunner",
    "GitStatusAllowedFiles",
    "GitStatusEntry",
    "GitStatusError",
    "GitStatusSnapshot",
    "WorktreeDirtyPreflight",
    "capture_git_status_snapshot",
    "capture_worktree_dirty_preflight",
    "dirty_paths_after_baseline",
    "filter_paths_by_allowed_files",
    "normalize_git_status_path",
    "parse_git_status_snapshot",
]

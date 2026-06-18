"""Local file lock primitive for future shared mutations."""

from __future__ import annotations

import os
from pathlib import Path

from .result import CommandError

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX fallback is best effort.
    fcntl = None  # type: ignore[assignment]


class LockError(CommandError):
    """Lock acquisition or release error."""


class FileLock:
    """Advisory local file lock."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._fd: int | None = None

    @property
    def held(self) -> bool:
        return self._fd is not None

    def acquire(self, *, blocking: bool = True) -> "FileLock":
        if self._fd is not None:
            return self
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(self.path), os.O_CREAT | os.O_RDWR, 0o644)
        try:
            if fcntl is not None:
                flags = fcntl.LOCK_EX
                if not blocking:
                    flags |= fcntl.LOCK_NB
                fcntl.flock(fd, flags)
            self._fd = fd
            return self
        except BlockingIOError as exc:
            os.close(fd)
            raise LockError("LOCK_BUSY", f"Lock is already held: {self.path}") from exc
        except OSError as exc:
            os.close(fd)
            raise LockError("LOCK_FAILED", f"Could not acquire lock: {self.path}") from exc

    def release(self) -> None:
        if self._fd is None:
            return
        fd = self._fd
        self._fd = None
        try:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)

    def __enter__(self) -> "FileLock":
        return self.acquire()

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.release()


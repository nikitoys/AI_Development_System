"""Local file lock primitive for shared project-control mutations."""

from __future__ import annotations

import json
import os
from pathlib import Path
import time
from typing import Any

from .result import CommandError

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX fallback is best effort.
    fcntl = None  # type: ignore[assignment]


class LockError(CommandError):
    """Lock acquisition or release error."""


class FileLock:
    """Advisory local file lock with readable contention errors."""

    def __init__(
        self,
        path: str | Path,
        *,
        stale_after: float | None = None,
        poll_interval: float = 0.05,
    ) -> None:
        self.path = Path(path)
        self.stale_after = stale_after
        self.poll_interval = poll_interval
        self._fd: int | None = None
        self._remove_on_release = False

    @property
    def held(self) -> bool:
        return self._fd is not None

    def acquire(self, *, blocking: bool = True, timeout: float | None = None) -> "FileLock":
        if self._fd is not None:
            return self
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if fcntl is None:
            return self._acquire_by_lockfile(blocking=blocking, timeout=timeout)
        return self._acquire_by_flock(blocking=blocking, timeout=timeout)

    def release(self) -> None:
        if self._fd is None:
            return
        fd = self._fd
        self._fd = None
        try:
            if fcntl is not None:
                self._clear_metadata(fd)
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)
            if self._remove_on_release:
                try:
                    self.path.unlink()
                except FileNotFoundError:
                    pass
                self._remove_on_release = False

    def __enter__(self) -> "FileLock":
        return self.acquire()

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.release()

    def _acquire_by_flock(self, *, blocking: bool, timeout: float | None) -> "FileLock":
        fd = os.open(str(self.path), os.O_CREAT | os.O_RDWR, 0o644)
        deadline = _deadline(timeout)
        try:
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self._write_metadata(fd)
                    self._fd = fd
                    self._remove_on_release = False
                    return self
                except BlockingIOError as exc:
                    if not blocking or _timed_out(deadline):
                        raise self._busy_error() from exc
                    time.sleep(self.poll_interval)
        except Exception:
            os.close(fd)
            raise

    def _acquire_by_lockfile(self, *, blocking: bool, timeout: float | None) -> "FileLock":
        deadline = _deadline(timeout)
        while True:
            try:
                fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o644)
            except FileExistsError as exc:
                if self._is_stale():
                    try:
                        self.path.unlink()
                        continue
                    except OSError:
                        pass
                if not blocking or _timed_out(deadline):
                    raise self._busy_error() from exc
                time.sleep(self.poll_interval)
                continue
            except OSError as exc:
                raise LockError("LOCK_FAILED", f"Could not acquire lock: {self.path}") from exc

            try:
                self._write_metadata(fd)
                self._fd = fd
                self._remove_on_release = True
                return self
            except Exception:
                os.close(fd)
                try:
                    self.path.unlink()
                except FileNotFoundError:
                    pass
                raise

    def _write_metadata(self, fd: int) -> None:
        metadata = {
            "pid": os.getpid(),
            "acquired_at": time.time(),
            "path": str(self.path),
        }
        raw = json.dumps(metadata, ensure_ascii=False, sort_keys=True).encode("utf-8")
        os.ftruncate(fd, 0)
        os.lseek(fd, 0, os.SEEK_SET)
        _write_all(fd, raw + b"\n")
        os.fsync(fd)

    def _clear_metadata(self, fd: int) -> None:
        try:
            os.ftruncate(fd, 0)
            os.fsync(fd)
        except OSError:
            pass

    def _busy_error(self) -> LockError:
        metadata = self._read_metadata()
        details = {"lock_path": str(self.path)}
        if metadata:
            details.update(metadata)
        if self._is_stale(metadata):
            return LockError(
                "LOCK_STALE",
                f"Lock appears stale: {self.path}",
                path=str(self.path),
                details=details,
            )
        return LockError(
            "LOCK_BUSY",
            f"Lock is already held: {self.path}",
            path=str(self.path),
            details=details,
        )

    def _read_metadata(self) -> dict[str, Any]:
        try:
            raw = self.path.read_text(encoding="utf-8").strip()
        except OSError:
            return {}
        if not raw:
            return {}
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        return data if isinstance(data, dict) else {}

    def _is_stale(self, metadata: dict[str, Any] | None = None) -> bool:
        if self.stale_after is None:
            return False
        data = metadata if metadata is not None else self._read_metadata()
        acquired_at = data.get("acquired_at") if data else None
        if isinstance(acquired_at, (int, float)):
            return time.time() - float(acquired_at) > self.stale_after
        try:
            return time.time() - self.path.stat().st_mtime > self.stale_after
        except OSError:
            return False


def _deadline(timeout: float | None) -> float | None:
    return None if timeout is None else time.monotonic() + timeout


def _timed_out(deadline: float | None) -> bool:
    return deadline is not None and time.monotonic() >= deadline


def _write_all(fd: int, data: bytes) -> None:
    view = memoryview(data)
    total = 0
    while total < len(view):
        written = os.write(fd, view[total:])
        if written == 0:
            raise OSError("zero-byte lock metadata write")
        total += written

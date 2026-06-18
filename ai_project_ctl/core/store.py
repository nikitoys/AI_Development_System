"""JSON state loading and atomic write helpers."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .result import CommandError


class StoreError(CommandError):
    """State store error with stable code."""


def atomic_write_text(path: str | Path, text: str) -> None:
    """Write text with temp-file, fsync, and atomic replace."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f"{target.name}.",
        suffix=".tmp",
        dir=str(target.parent),
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, str(target))
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def read_json_file(path: str | Path, *, missing_code: str = "STATE_NOT_FOUND") -> Any:
    target = Path(path)
    try:
        with target.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise StoreError(missing_code, f"Missing state file: {target}") from exc
    except json.JSONDecodeError as exc:
        raise StoreError(
            "INVALID_JSON",
            f"{target}:{exc.lineno}:{exc.colno} {exc.msg}",
            path=str(target),
        ) from exc


def write_json_file(path: str | Path, data: Any) -> None:
    atomic_write_text(
        path,
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    )


class JsonStore:
    """Small state-store wrapper around one JSON file."""

    def __init__(self, path: str | Path, *, missing_code: str = "STATE_NOT_FOUND") -> None:
        self.path = Path(path)
        self.missing_code = missing_code

    def load(self) -> Any:
        return read_json_file(self.path, missing_code=self.missing_code)

    def save(self, data: Any) -> None:
        write_json_file(self.path, data)

    def exists(self) -> bool:
        return self.path.exists()


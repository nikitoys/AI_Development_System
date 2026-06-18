"""Append-only audit event primitives."""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_event_id(prefix: str = "EVT") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"


@dataclass(frozen=True)
class AuditEvent:
    """One append-only audit event."""

    actor: str
    command: str
    entity_type: str
    entity_id: str
    revision_before: int | None
    revision_after: int | None
    payload: Mapping[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=new_event_id)
    timestamp: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "command": self.command,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "revision_before": self.revision_before,
            "revision_after": self.revision_after,
            "payload": dict(self.payload),
        }

    def to_json_line(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, separators=(",", ":")) + "\n"


class AuditLog:
    """Append-only JSONL audit log."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, event: AuditEvent) -> str:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        raw = event.to_json_line().encode("utf-8")
        fd = os.open(str(self.path), os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o644)
        try:
            _write_all(fd, raw)
            os.fsync(fd)
        finally:
            os.close(fd)
        return event.event_id

    def append_event(
        self,
        *,
        actor: str,
        command: str,
        entity_type: str,
        entity_id: str,
        revision_before: int | None,
        revision_after: int | None,
        payload: Mapping[str, Any] | None = None,
    ) -> str:
        event = AuditEvent(
            actor=actor,
            command=command,
            entity_type=entity_type,
            entity_id=entity_id,
            revision_before=revision_before,
            revision_after=revision_after,
            payload=dict(payload or {}),
        )
        return self.append(event)


def _write_all(fd: int, data: bytes) -> None:
    view = memoryview(data)
    total = 0
    while total < len(view):
        written = os.write(fd, view[total:])
        if written == 0:
            raise OSError("zero-byte audit event write")
        total += written

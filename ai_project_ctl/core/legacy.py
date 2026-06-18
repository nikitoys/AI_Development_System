"""Compatibility helpers for legacy ``*ctl.py`` entrypoints.

These helpers intentionally point legacy scripts directly at shared core
services. They must not delegate to ``scripts/aictl.py`` because the facade
still delegates back to the legacy scripts for compatibility commands.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .events import AuditLog, utc_now
from .paths import ProjectPaths
from .store import atomic_write_text


def project_paths(root: str | Path) -> ProjectPaths:
    return ProjectPaths.from_root(root)


def state_dir(root: str | Path) -> Path:
    return project_paths(root).state_dir


def events_dir(root: str | Path) -> Path:
    return project_paths(root).events_dir


def generated_dir(root: str | Path) -> Path:
    return project_paths(root).generated_dir


def ensure_project_dirs(root: str | Path) -> None:
    project_paths(root).ensure_project_dirs()


def append_audit_event(
    event_path: str | Path,
    *,
    actor: str,
    command: str,
    entity_type: str,
    entity_id: str,
    revision_before: int | None,
    revision_after: int | None,
    payload: Mapping[str, Any] | None = None,
) -> str:
    return AuditLog(event_path).append_event(
        actor=actor,
        command=command,
        entity_type=entity_type,
        entity_id=entity_id,
        revision_before=revision_before,
        revision_after=revision_after,
        payload=dict(payload or {}),
    )

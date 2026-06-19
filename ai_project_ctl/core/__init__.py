"""Core primitives for future project-control command services."""

from .events import AuditEvent, AuditLog, new_event_id, utc_now
from .ids import (
    IdentityError,
    IdentityIndex,
    allocate_numeric_id,
    allocate_uid,
    build_identity_index,
    format_scoped_ref,
)
from .locks import FileLock, LockError
from .paths import ProjectPaths
from .result import CommandError, CommandMessage, CommandResult
from .store import JsonStore, StoreError, atomic_write_text, read_json_file, write_json_file
from .transactions import MutationTransaction, RenderTrigger
from .validation import ValidationError, ValidationIssue, ValidationResult, require_fields

__all__ = [
    "AuditEvent",
    "AuditLog",
    "CommandError",
    "CommandMessage",
    "CommandResult",
    "FileLock",
    "IdentityError",
    "IdentityIndex",
    "JsonStore",
    "LockError",
    "MutationTransaction",
    "ProjectPaths",
    "RenderTrigger",
    "StoreError",
    "ValidationError",
    "ValidationIssue",
    "ValidationResult",
    "allocate_numeric_id",
    "allocate_uid",
    "atomic_write_text",
    "build_identity_index",
    "format_scoped_ref",
    "new_event_id",
    "read_json_file",
    "require_fields",
    "utc_now",
    "write_json_file",
]


"""Stable command result and error primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class CommandMessage:
    """Machine-readable command warning or error."""

    code: str
    message: str
    path: str = ""
    details: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.path:
            data["path"] = self.path
        if self.details:
            data["details"] = dict(self.details)
        return data


class CommandError(Exception):
    """Exception carrying a stable project-control error code."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        path: str = "",
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(f"{code}: {message}" if message else code)
        self.code = code
        self.message = message
        self.path = path
        self.details = dict(details or {})

    def to_message(self) -> CommandMessage:
        return CommandMessage(
            code=self.code,
            message=self.message,
            path=self.path,
            details=self.details,
        )


@dataclass
class CommandResult:
    """Structured result shared by CLI wrappers and future facades."""

    ok: bool
    command: str
    domain: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    warnings: list[CommandMessage] = field(default_factory=list)
    errors: list[CommandMessage] = field(default_factory=list)
    changed_files: list[str] = field(default_factory=list)
    generated_files: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    revision_before: int | None = None
    revision_after: int | None = None
    owner_action_required: str | None = None
    next_actions: list[str] = field(default_factory=list)

    @classmethod
    def success(
        cls,
        *,
        command: str,
        domain: str,
        message: str,
        data: Mapping[str, Any] | None = None,
        revision_before: int | None = None,
        revision_after: int | None = None,
    ) -> "CommandResult":
        return cls(
            ok=True,
            command=command,
            domain=domain,
            message=message,
            data=dict(data or {}),
            revision_before=revision_before,
            revision_after=revision_after,
        )

    @classmethod
    def failure(
        cls,
        *,
        command: str,
        domain: str,
        message: str,
        errors: list[CommandMessage] | None = None,
        revision_before: int | None = None,
        revision_after: int | None = None,
    ) -> "CommandResult":
        return cls(
            ok=False,
            command=command,
            domain=domain,
            message=message,
            errors=list(errors or []),
            revision_before=revision_before,
            revision_after=revision_after,
        )

    def add_warning(self, code: str, message: str, *, path: str = "") -> None:
        self.warnings.append(CommandMessage(code=code, message=message, path=path))

    def add_error(self, code: str, message: str, *, path: str = "") -> None:
        self.errors.append(CommandMessage(code=code, message=message, path=path))
        self.ok = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "command": self.command,
            "domain": self.domain,
            "message": self.message,
            "data": self.data,
            "warnings": [warning.to_dict() for warning in self.warnings],
            "errors": [error.to_dict() for error in self.errors],
            "changed_files": list(self.changed_files),
            "generated_files": list(self.generated_files),
            "events": list(self.events),
            "revision_before": self.revision_before,
            "revision_after": self.revision_after,
            "owner_action_required": self.owner_action_required,
            "next_actions": list(self.next_actions),
        }


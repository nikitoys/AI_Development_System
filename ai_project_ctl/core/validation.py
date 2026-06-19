"""Reusable validation result primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

from .result import CommandError, CommandMessage


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    path: str = ""
    blocking: bool = True

    def to_message(self) -> CommandMessage:
        return CommandMessage(code=self.code, message=self.message, path=self.path)


class ValidationError(CommandError):
    """Raised when validation issues block command execution."""

    def __init__(self, result: "ValidationResult") -> None:
        messages = "; ".join(issue.message for issue in result.errors)
        super().__init__("VALIDATION_FAILED", messages or "Validation failed")
        self.result = result


@dataclass
class ValidationResult:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def errors(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.blocking]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if not issue.blocking]

    def add_error(self, code: str, message: str, *, path: str = "") -> None:
        self.issues.append(ValidationIssue(code=code, message=message, path=path, blocking=True))

    def add_warning(self, code: str, message: str, *, path: str = "") -> None:
        self.issues.append(ValidationIssue(code=code, message=message, path=path, blocking=False))

    def extend(self, other: "ValidationResult") -> None:
        self.issues.extend(other.issues)

    def require_ok(self) -> None:
        if not self.ok:
            raise ValidationError(self)

    def error_messages(self) -> list[CommandMessage]:
        return [issue.to_message() for issue in self.errors]

    def warning_messages(self) -> list[CommandMessage]:
        return [issue.to_message() for issue in self.warnings]


def require_fields(mapping: Mapping[str, object], fields: Sequence[str], *, prefix: str = "") -> ValidationResult:
    result = ValidationResult()
    for field in fields:
        if field not in mapping:
            result.add_error(
                "MISSING_REQUIRED_FIELD",
                f"Missing required field: {field}",
                path=f"{prefix}.{field}" if prefix else field,
            )
    return result


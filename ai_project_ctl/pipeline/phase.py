"""Reusable outcome contract for pipeline phases."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from ai_project_ctl.core.result import CommandError


class PhaseStatus(str, Enum):
    """Stable status values returned by pipeline phases."""

    PASSED = "passed"
    BLOCKED = "blocked"
    FAILED = "failed"
    SKIPPED = "skipped"


PHASE_STATUSES = tuple(status.value for status in PhaseStatus)
CI_EXIT_PASSED = 0
CI_EXIT_FAILED = 1
CI_EXIT_BLOCKED = 2
_PHASE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class PipelinePhaseError(CommandError):
    """Stable pipeline phase result error."""


@dataclass(frozen=True)
class PhaseResult:
    """Compact JSON-compatible result for one pipeline phase."""

    phase: str
    status: PhaseStatus | str
    reason: str = ""
    next_action: str = ""
    artifacts: Mapping[str, Any] = field(default_factory=dict)
    changed_files: Sequence[str] = ()
    generated_files: Sequence[str] = ()
    events: Sequence[str] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "phase", _phase_name(self.phase))
        object.__setattr__(self, "status", _phase_status(self.status))
        object.__setattr__(self, "reason", _optional_text(self.reason, "reason"))
        object.__setattr__(
            self,
            "next_action",
            _optional_text(self.next_action, "next_action"),
        )
        object.__setattr__(self, "artifacts", _artifacts(self.artifacts))
        object.__setattr__(
            self,
            "changed_files",
            _string_tuple(self.changed_files, "changed_files"),
        )
        object.__setattr__(
            self,
            "generated_files",
            _string_tuple(self.generated_files, "generated_files"),
        )
        object.__setattr__(self, "events", _string_tuple(self.events, "events"))

    @classmethod
    def passed(cls, phase: str, **kwargs: Any) -> "PhaseResult":
        return cls(phase=phase, status=PhaseStatus.PASSED, **kwargs)

    @classmethod
    def blocked(cls, phase: str, **kwargs: Any) -> "PhaseResult":
        return cls(phase=phase, status=PhaseStatus.BLOCKED, **kwargs)

    @classmethod
    def failed(cls, phase: str, **kwargs: Any) -> "PhaseResult":
        return cls(phase=phase, status=PhaseStatus.FAILED, **kwargs)

    @classmethod
    def skipped(cls, phase: str, **kwargs: Any) -> "PhaseResult":
        return cls(phase=phase, status=PhaseStatus.SKIPPED, **kwargs)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PhaseResult":
        """Load a phase result from its serialized payload."""

        if not isinstance(data, Mapping):
            raise PipelinePhaseError(
                "PIPELINE_PHASE_RESULT_NOT_OBJECT",
                "phase result payload must be an object",
            )
        missing = [
            field_name
            for field_name in ("phase", "status")
            if field_name not in data
        ]
        if missing:
            raise PipelinePhaseError(
                "PIPELINE_PHASE_REQUIRED_FIELD",
                "phase result missing required field(s): {}".format(
                    ", ".join(missing)
                ),
                details={"fields": missing},
            )
        return cls(
            phase=data["phase"],
            status=data["status"],
            reason=data.get("reason", ""),
            next_action=data.get("next_action", ""),
            artifacts=data.get("artifacts", {}),
            changed_files=data.get("changed_files", ()),
            generated_files=data.get("generated_files", ()),
            events=data.get("events", ()),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the canonical JSON-compatible phase result shape."""

        return {
            "phase": self.phase,
            "status": self.status.value,
            "reason": self.reason,
            "next_action": self.next_action,
            "artifacts": dict(self.artifacts),
            "changed_files": list(self.changed_files),
            "generated_files": list(self.generated_files),
            "events": list(self.events),
        }

    def to_command_data(self) -> dict[str, Any]:
        """Return a compact payload suitable for ``CommandResult.data``."""

        return {"phase_result": self.to_dict()}

    def to_command_result_fields(self) -> dict[str, Any]:
        """Return fields that can be merged into a ``CommandResult`` payload."""

        return {
            "data": self.to_command_data(),
            "changed_files": list(self.changed_files),
            "generated_files": list(self.generated_files),
            "events": list(self.events),
            "next_actions": [self.next_action] if self.next_action else [],
        }


def pipeline_ci_exit_code(result: object) -> int:
    """Return CI exit code for pipeline command outcomes.

    CI mode maps passed and completed outcomes to 0, failed outcomes to 1,
    and blocked safe-stop outcomes to 2.
    """

    data = getattr(result, "data", {})
    if not isinstance(data, Mapping):
        data = {}
    if not bool(getattr(result, "ok", False)):
        return CI_EXIT_FAILED

    outcome = _pipeline_ci_outcome(data)
    if outcome in {"passed", "completed"}:
        return CI_EXIT_PASSED
    if outcome == "failed":
        return CI_EXIT_FAILED
    if outcome == "blocked":
        return CI_EXIT_BLOCKED
    return CI_EXIT_PASSED


def _pipeline_ci_outcome(data: Mapping[str, Any]) -> str:
    stop_code = str(data.get("stop_code") or "").strip()
    if stop_code == "QUEUE_COMPLETE":
        return "completed"

    for value in (
        data.get("phase_status"),
        _phase_result_status(data.get("phase_result")),
        _latest_step_phase_status(data.get("step_results")),
        data.get("session_status"),
        data.get("current_step_status"),
    ):
        selected = _pipeline_ci_status(value)
        if selected:
            return selected

    if stop_code:
        return "blocked"
    return "passed"


def _phase_result_status(value: object) -> object:
    if isinstance(value, Mapping):
        return value.get("status")
    return None


def _latest_step_phase_status(value: object) -> object:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return None
    for item in reversed(value):
        if isinstance(item, Mapping):
            return item.get("phase_status")
    return None


def _pipeline_ci_status(value: object) -> str:
    selected = str(value or "").strip().lower()
    if selected in {"passed", "completed", "failed", "blocked"}:
        return selected
    return ""


def _phase_name(value: object) -> str:
    if not isinstance(value, str):
        raise PipelinePhaseError(
            "PIPELINE_PHASE_NAME_REQUIRED",
            "phase name must be a string",
            path="phase",
        )
    phase = value.strip()
    if not phase:
        raise PipelinePhaseError(
            "PIPELINE_PHASE_NAME_REQUIRED",
            "phase name is required",
            path="phase",
        )
    if not _PHASE_NAME_RE.match(phase):
        raise PipelinePhaseError(
            "PIPELINE_PHASE_INVALID_NAME",
            "phase name must start with a letter or number and contain only "
            "letters, numbers, dots, dashes, or underscores",
            path="phase",
            details={"allowed_pattern": _PHASE_NAME_RE.pattern},
        )
    return phase


def _phase_status(value: object) -> PhaseStatus:
    if isinstance(value, PhaseStatus):
        return value
    if not isinstance(value, str):
        raise PipelinePhaseError(
            "PIPELINE_PHASE_INVALID_STATUS",
            "phase status must be one of: {}".format(", ".join(PHASE_STATUSES)),
            path="status",
            details={"allowed": PHASE_STATUSES},
        )
    selected = value.strip()
    try:
        return PhaseStatus(selected)
    except ValueError as exc:
        raise PipelinePhaseError(
            "PIPELINE_PHASE_INVALID_STATUS",
            "phase status must be one of: {}".format(", ".join(PHASE_STATUSES)),
            path="status",
            details={"allowed": PHASE_STATUSES},
        ) from exc


def _optional_text(value: object, field_name: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise PipelinePhaseError(
            "PIPELINE_PHASE_INVALID_FIELD",
            "{} must be a string".format(field_name),
            path=field_name,
        )
    return value.strip()


def _artifacts(value: object) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PipelinePhaseError(
            "PIPELINE_PHASE_INVALID_ARTIFACTS",
            "artifacts must be an object",
            path="artifacts",
        )
    return _json_value(value, "artifacts")


def _json_value(value: object, path: str) -> Any:
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise PipelinePhaseError(
                "PIPELINE_PHASE_INVALID_ARTIFACT",
                "artifact value must be JSON-compatible",
                path=path,
            )
        return value
    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise PipelinePhaseError(
                    "PIPELINE_PHASE_INVALID_ARTIFACT",
                    "artifact keys must be strings",
                    path=path,
                )
            result[key] = _json_value(item, "{}.{}".format(path, key))
        return result
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [
            _json_value(item, "{}[{}]".format(path, index))
            for index, item in enumerate(value)
        ]
    raise PipelinePhaseError(
        "PIPELINE_PHASE_INVALID_ARTIFACT",
        "artifact value must be JSON-compatible",
        path=path,
    )


def _string_tuple(value: object, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise PipelinePhaseError(
            "PIPELINE_PHASE_INVALID_LIST",
            "{} must be a list of strings".format(field_name),
            path=field_name,
        )
    items: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise PipelinePhaseError(
                "PIPELINE_PHASE_INVALID_LIST_ITEM",
                "{}[{}] must be a string".format(field_name, index),
                path="{}[{}]".format(field_name, index),
            )
        selected = item.strip()
        if not selected:
            raise PipelinePhaseError(
                "PIPELINE_PHASE_INVALID_LIST_ITEM",
                "{}[{}] must not be empty".format(field_name, index),
                path="{}[{}]".format(field_name, index),
            )
        items.append(selected)
    return tuple(items)


__all__ = [
    "CI_EXIT_BLOCKED",
    "CI_EXIT_FAILED",
    "CI_EXIT_PASSED",
    "PHASE_STATUSES",
    "PhaseResult",
    "PhaseStatus",
    "PipelinePhaseError",
    "pipeline_ci_exit_code",
]

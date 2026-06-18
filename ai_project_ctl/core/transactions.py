"""Foundation transaction runner for future command services."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, MutableMapping

from .events import AuditLog
from .locks import FileLock
from .result import CommandError, CommandMessage, CommandResult
from .store import JsonStore, atomic_write_text
from .validation import ValidationResult

State = MutableMapping[str, Any]
Validator = Callable[[Mapping[str, Any]], ValidationResult | None]
Mutator = Callable[[State], Mapping[str, Any] | None]


@dataclass(frozen=True)
class RenderTrigger:
    """Render one generated file from a validated state snapshot."""

    path: Path
    render: Callable[[Mapping[str, Any]], str]

    def run(self, state: Mapping[str, Any]) -> str:
        atomic_write_text(self.path, self.render(state))
        return str(self.path)


class MutationTransaction:
    """Load, validate, mutate, save, audit, and render one state file.

    This runner is intentionally small and not wired into legacy ctl scripts by
    CTL-04. It gives future domain services one tested path to build on.
    """

    def __init__(
        self,
        store: JsonStore,
        *,
        event_log: AuditLog | None = None,
        lock: FileLock | None = None,
    ) -> None:
        self.store = store
        self.event_log = event_log
        self.lock = lock

    def run(
        self,
        *,
        command: str,
        domain: str,
        actor: str,
        entity_type: str,
        entity_id: str,
        mutate: Mutator,
        validate_before: Validator | None = None,
        validate_after: Validator | None = None,
        renderers: Iterable[RenderTrigger] = (),
        event_payload: Mapping[str, Any] | None = None,
    ) -> CommandResult:
        if self.lock is None:
            return self._run_unlocked(
                command=command,
                domain=domain,
                actor=actor,
                entity_type=entity_type,
                entity_id=entity_id,
                mutate=mutate,
                validate_before=validate_before,
                validate_after=validate_after,
                renderers=renderers,
                event_payload=event_payload,
            )

        with self.lock:
            return self._run_unlocked(
                command=command,
                domain=domain,
                actor=actor,
                entity_type=entity_type,
                entity_id=entity_id,
                mutate=mutate,
                validate_before=validate_before,
                validate_after=validate_after,
                renderers=renderers,
                event_payload=event_payload,
            )

    def _run_unlocked(
        self,
        *,
        command: str,
        domain: str,
        actor: str,
        entity_type: str,
        entity_id: str,
        mutate: Mutator,
        validate_before: Validator | None,
        validate_after: Validator | None,
        renderers: Iterable[RenderTrigger],
        event_payload: Mapping[str, Any] | None,
    ) -> CommandResult:
        try:
            current_state = self.store.load()
            if not isinstance(current_state, dict):
                raise CommandError("INVALID_STATE", "State root must be an object")

            revision_before = _revision(current_state)
            before = _validate(validate_before, current_state)
            if not before.ok:
                return _validation_failure(command, domain, before, revision_before)

            next_state = copy.deepcopy(current_state)
            mutation_data = dict(mutate(next_state) or {})
            after = _validate(validate_after, next_state)
            if not after.ok:
                return _validation_failure(command, domain, after, revision_before)

            revision_after = _revision(next_state)
            self.store.save(next_state)

            result = CommandResult.success(
                command=command,
                domain=domain,
                message=f"OK: {command}",
                data=mutation_data,
                revision_before=revision_before,
                revision_after=revision_after,
            )
            result.changed_files.append(str(self.store.path))
            result.warnings.extend(before.warning_messages())
            result.warnings.extend(after.warning_messages())

            if self.event_log is not None:
                event_id = self.event_log.append_event(
                    actor=actor,
                    command=command,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    revision_before=revision_before,
                    revision_after=revision_after,
                    payload=dict(event_payload or mutation_data),
                )
                result.events.append(event_id)
                result.changed_files.append(str(self.event_log.path))

            for renderer in renderers:
                generated = renderer.run(next_state)
                result.generated_files.append(generated)
                result.changed_files.append(generated)

            return result
        except CommandError as exc:
            return CommandResult.failure(
                command=command,
                domain=domain,
                message=exc.code,
                errors=[exc.to_message()],
            )


def _revision(state: Mapping[str, Any]) -> int | None:
    value = state.get("revision")
    return value if isinstance(value, int) else None


def _validate(validator: Validator | None, state: Mapping[str, Any]) -> ValidationResult:
    if validator is None:
        return ValidationResult()
    return validator(state) or ValidationResult()


def _validation_failure(
    command: str,
    domain: str,
    result: ValidationResult,
    revision_before: int | None,
) -> CommandResult:
    return CommandResult.failure(
        command=command,
        domain=domain,
        message="VALIDATION_FAILED",
        errors=[CommandMessage(issue.code, issue.message, issue.path) for issue in result.errors],
        revision_before=revision_before,
        revision_after=revision_before,
    )


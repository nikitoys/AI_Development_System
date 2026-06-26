"""Governed custom pipeline policy preset storage."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ai_project_ctl.core.events import AuditEvent, AuditLog, new_event_id, utc_now
from ai_project_ctl.core.locks import FileLock
from ai_project_ctl.core.paths import ProjectPaths
from ai_project_ctl.core.result import CommandError, CommandMessage, CommandResult
from ai_project_ctl.core.store import atomic_write_text, read_json_file, write_json_file
from ai_project_ctl.core.validation import ValidationResult

from .policy import (
    PipelinePolicy,
    is_builtin_preset_name,
    policy_behavior_label,
    policy_preset,
    preset_names,
)
from .state import GENERATED_HEADER


POLICY_STORE_SCHEMA_VERSION = 1
POLICY_STORE_FILE_NAME = "pipeline_policy_presets.json"
POLICY_EVENTS_FILE_NAME = "pipeline-policy-events.jsonl"
POLICY_GENERATED_FILE_NAME = "PIPELINE_POLICIES.md"
GENERATED_SOURCE = "<!-- Source: AI_PROJECT/state/pipeline_policy_presets.json -->"

POLICY_PRESET_EVENT_TYPES = {
    "policy_preset.created",
    "policy_preset.updated",
    "policy_preset.deleted",
}

CUSTOM_PRESET_NAME_RE = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")


class PipelinePolicyStoreError(CommandError):
    """Stable custom policy preset store error."""


def pipeline_policy_store_path(root: str | Path) -> Path:
    return ProjectPaths.from_root(root).state_file(POLICY_STORE_FILE_NAME)


def pipeline_policy_events_path(root: str | Path) -> Path:
    return ProjectPaths.from_root(root).event_file(POLICY_EVENTS_FILE_NAME)


def pipeline_policy_status_path(root: str | Path) -> Path:
    return ProjectPaths.from_root(root).generated_file(POLICY_GENERATED_FILE_NAME)


def default_policy_store_state(*, now: str | None = None) -> dict[str, Any]:
    timestamp = now or utc_now()
    return {
        "schema_version": POLICY_STORE_SCHEMA_VERSION,
        "revision": 0,
        "created_at": timestamp,
        "updated_at": timestamp,
        "presets": [],
    }


def load_policy_store_state(root: str | Path, *, required: bool = False) -> dict[str, Any]:
    path = pipeline_policy_store_path(root)
    if not path.exists():
        if required:
            raise FileNotFoundError(path)
        return default_policy_store_state()
    data = read_json_file(path, missing_code="PIPELINE_POLICY_PRESETS_NOT_INITIALIZED")
    return data if isinstance(data, dict) else {}


def load_policy_preset(name: str, *, root: str | Path = ".") -> PipelinePolicy:
    """Load a built-in or custom policy preset by name."""

    if is_builtin_preset_name(name):
        return policy_preset(name)

    state = load_policy_store_state(root)
    validation = validate_policy_store_state(state)
    validation.require_ok()
    entry = _find_entry(state, name)
    if entry is None:
        raise PipelinePolicyStoreError(
            "POLICY_PRESET_NOT_FOUND",
            "Unknown pipeline policy preset: {}".format(name),
            path="name",
        )
    return PipelinePolicy.from_dict(_policy_mapping(entry, "policy"))


def status_payload(*, root: str | Path = ".") -> dict[str, Any]:
    state = load_policy_store_state(root)
    validation = validate_policy_store_state(state)
    validation.require_ok()
    custom_entries = [
        _policy_summary(
            name=str(entry.get("name") or ""),
            policy=PipelinePolicy.from_dict(_policy_mapping(entry, "policy")),
            kind="custom",
            entry=entry,
        )
        for entry in state.get("presets", [])
        if isinstance(entry, Mapping)
    ]
    return {
        "state_path": str(pipeline_policy_store_path(root)),
        "events_path": str(pipeline_policy_events_path(root)),
        "generated_path": str(pipeline_policy_status_path(root)),
        "revision": state.get("revision", 0),
        "builtins": [
            _policy_summary(name=name, policy=policy_preset(name), kind="built_in")
            for name in preset_names()
        ],
        "custom": custom_entries,
    }


def policy_catalog_payload(*, root: str | Path = ".") -> dict[str, Any]:
    """Return compact built-in and custom policy metadata for Web selection."""

    state = load_policy_store_state(root)
    validation = validate_policy_store_state(state)
    validation.require_ok()

    builtins = [
        _policy_catalog_item(name=name, policy=policy_preset(name), kind="built_in")
        for name in preset_names()
    ]
    custom = []
    for entry in state.get("presets", []):
        if isinstance(entry, Mapping):
            custom.append(
                _policy_catalog_item(
                    name=str(entry.get("name") or ""),
                    policy=PipelinePolicy.from_dict(_policy_mapping(entry, "policy")),
                    kind="custom",
                )
            )
    custom.sort(key=lambda item: item["name"])
    policies = [*builtins, *custom]
    return {
        "revision": state.get("revision", 0),
        "state_path": str(pipeline_policy_store_path(root)),
        "policies": policies,
        "counts": {
            "built_in": len(builtins),
            "custom": len(custom),
            "total": len(policies),
        },
    }


def save_policy_preset(
    name: str,
    policy: PipelinePolicy | Mapping[str, Any],
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
) -> CommandResult:
    command = "pipeline.policy.save"
    try:
        normalized_name = _normalize_name(name)
        selected_policy = _coerce_policy(policy)
        _validate_custom_name_or_raise(normalized_name)
        if selected_policy.name != normalized_name:
            raise PipelinePolicyStoreError(
                "POLICY_PRESET_NAME_MISMATCH",
                "Policy payload name must match the preset name.",
                path="policy.name",
                details={"expected": normalized_name, "actual": selected_policy.name},
            )
        policy_validation = selected_policy.validate()
        if not policy_validation.ok:
            return _validation_failure(command, policy_validation, None)

        def mutate(state: dict[str, Any], event_id: str, now: str) -> dict[str, Any]:
            presets = _custom_presets(state)
            existing = _find_entry(state, normalized_name)
            action = "updated" if existing is not None else "created"
            entry = {
                "name": normalized_name,
                "policy": selected_policy.to_dict(),
                "created_at": str(existing.get("created_at") or now) if existing else now,
                "updated_at": now,
            }
            if existing is None:
                presets.append(entry)
            else:
                presets[presets.index(existing)] = entry
            return {
                "name": normalized_name,
                "action": action,
                "event_type": "policy_preset.{}".format(action),
                "policy": selected_policy.to_dict(),
                "summary": _policy_summary(
                    name=normalized_name,
                    policy=selected_policy,
                    kind="custom",
                    entry=entry,
                ),
            }

        return _mutate_policy_store(
            root=root,
            actor=actor,
            command=command,
            entity_id=normalized_name,
            mutate=mutate,
        )
    except CommandError as exc:
        return _command_failure(command, exc)
    except (KeyError, TypeError, ValueError) as exc:
        return _command_failure(
            command,
            PipelinePolicyStoreError(
                "POLICY_PRESET_INVALID_POLICY",
                "Policy payload is not a valid pipeline policy: {}".format(exc),
                path="policy",
            ),
        )


def delete_policy_preset(
    name: str,
    *,
    root: str | Path = ".",
    actor: str = "human_owner",
) -> CommandResult:
    command = "pipeline.policy.delete"
    try:
        normalized_name = _normalize_name(name)
        _validate_custom_name_or_raise(normalized_name)

        def mutate(state: dict[str, Any], event_id: str, now: str) -> dict[str, Any]:
            presets = _custom_presets(state)
            existing = _find_entry(state, normalized_name)
            if existing is None:
                raise PipelinePolicyStoreError(
                    "POLICY_PRESET_NOT_FOUND",
                    "Unknown custom pipeline policy preset: {}".format(normalized_name),
                    path="name",
                )
            presets.remove(existing)
            return {
                "name": normalized_name,
                "action": "deleted",
                "event_type": "policy_preset.deleted",
                "policy": dict(_policy_mapping(existing, "policy")),
            }

        return _mutate_policy_store(
            root=root,
            actor=actor,
            command=command,
            entity_id=normalized_name,
            mutate=mutate,
        )
    except CommandError as exc:
        return _command_failure(command, exc)


def validate_policy_store(*, root: str | Path = ".") -> ValidationResult:
    state = load_policy_store_state(root)
    result = validate_policy_store_state(state)
    result.extend(validate_policy_events(read_policy_events(root), state=state))
    return result


def validate_policy_store_state(state: Mapping[str, Any]) -> ValidationResult:
    result = ValidationResult()
    if not isinstance(state, Mapping):
        result.add_error(
            "PIPELINE_POLICY_STORE_NOT_OBJECT",
            "pipeline policy preset state must be an object",
        )
        return result

    if state.get("schema_version") != POLICY_STORE_SCHEMA_VERSION:
        result.add_error(
            "PIPELINE_POLICY_STORE_INVALID_SCHEMA_VERSION",
            "pipeline_policy_presets.schema_version must be {}".format(
                POLICY_STORE_SCHEMA_VERSION
            ),
            path="schema_version",
        )

    revision = state.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0:
        result.add_error(
            "PIPELINE_POLICY_STORE_INVALID_REVISION",
            "pipeline_policy_presets.revision must be a non-negative integer",
            path="revision",
        )

    for field in ("created_at", "updated_at"):
        if not isinstance(state.get(field), str) or not str(state.get(field)).strip():
            result.add_error(
                "PIPELINE_POLICY_STORE_INVALID_TIMESTAMP",
                "{} must be a non-empty string".format(field),
                path=field,
            )

    presets = state.get("presets")
    if not isinstance(presets, list):
        result.add_error(
            "PIPELINE_POLICY_STORE_INVALID_PRESETS",
            "pipeline_policy_presets.presets must be a list",
            path="presets",
        )
        return result

    seen: set[str] = set()
    for index, entry in enumerate(presets):
        path = "presets[{}]".format(index)
        if not isinstance(entry, Mapping):
            result.add_error(
                "PIPELINE_POLICY_STORE_INVALID_PRESET",
                "{} must be an object".format(path),
                path=path,
            )
            continue

        name = _normalize_name(entry.get("name"))
        _append_name_validation(result, name, path + ".name")
        if name in seen:
            result.add_error(
                "PIPELINE_POLICY_STORE_DUPLICATE_PRESET",
                "duplicate custom policy preset: {}".format(name),
                path=path + ".name",
            )
        seen.add(name)

        for field in ("created_at", "updated_at"):
            if not isinstance(entry.get(field), str) or not str(entry.get(field)).strip():
                result.add_error(
                    "PIPELINE_POLICY_STORE_INVALID_PRESET_TIMESTAMP",
                    "{}.{} must be a non-empty string".format(path, field),
                    path=path + "." + field,
                )

        try:
            policy = PipelinePolicy.from_dict(_policy_mapping(entry, "policy"))
        except (KeyError, TypeError, ValueError) as exc:
            result.add_error(
                "PIPELINE_POLICY_STORE_INVALID_POLICY",
                "{}.policy is not a valid pipeline policy: {}".format(path, exc),
                path=path + ".policy",
            )
            continue

        if policy.name != name:
            result.add_error(
                "PIPELINE_POLICY_STORE_POLICY_NAME_MISMATCH",
                "{}.policy.name must match preset name".format(path),
                path=path + ".policy.name",
            )
        policy_result = policy.validate()
        for issue in policy_result.errors:
            result.add_error(issue.code, issue.message, path=path + ".policy." + issue.path)
        for issue in policy_result.warnings:
            result.add_warning(issue.code, issue.message, path=path + ".policy." + issue.path)

    return result


def read_policy_events(root: str | Path) -> list[dict[str, Any]]:
    path = pipeline_policy_events_path(root)
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            events.append({"_invalid_line": index, "_raw": line})
            continue
        events.append(event if isinstance(event, dict) else {"_invalid_line": index, "_raw": line})
    return events


def validate_policy_events(
    events: Sequence[Mapping[str, Any]],
    *,
    state: Mapping[str, Any] | None = None,
) -> ValidationResult:
    result = ValidationResult()
    known_names = {
        str(entry.get("name") or "")
        for entry in (state or {}).get("presets", [])
        if isinstance(entry, Mapping)
    }
    for index, event in enumerate(events):
        path = "events[{}]".format(index)
        if event.get("_invalid_line"):
            result.add_error(
                "PIPELINE_POLICY_EVENT_INVALID_JSON",
                "pipeline policy audit event line is not valid JSON",
                path=path,
            )
            continue
        for field in ("event_id", "timestamp", "actor", "command", "entity_type", "entity_id"):
            if not isinstance(event.get(field), str) or not str(event.get(field)).strip():
                result.add_error(
                    "PIPELINE_POLICY_EVENT_MISSING_FIELD",
                    "{}.{} must be a non-empty string".format(path, field),
                    path=path + "." + field,
                )
        payload = event.get("payload")
        if not isinstance(payload, Mapping):
            result.add_error(
                "PIPELINE_POLICY_EVENT_INVALID_PAYLOAD",
                "{}.payload must be an object".format(path),
                path=path + ".payload",
            )
            continue
        event_type = payload.get("event_type")
        if event_type not in POLICY_PRESET_EVENT_TYPES:
            result.add_error(
                "PIPELINE_POLICY_EVENT_INVALID_TYPE",
                "{}.payload.event_type must be a known policy preset event".format(path),
                path=path + ".payload.event_type",
            )
        entity_id = str(event.get("entity_id") or "")
        if (
            event_type != "policy_preset.deleted"
            and known_names
            and entity_id
            and entity_id not in known_names
        ):
            result.add_warning(
                "PIPELINE_POLICY_EVENT_UNKNOWN_PRESET",
                "{} references a custom policy preset not present in current state".format(path),
                path=path + ".entity_id",
            )
    return result


def render_policy_store(*, root: str | Path = ".") -> str:
    state = load_policy_store_state(root)
    result = validate_policy_store(root=root)
    result.require_ok()
    text = render_policy_store_status(state)
    ProjectPaths.from_root(root).ensure_project_dirs()
    atomic_write_text(pipeline_policy_status_path(root), text)
    return text


def render_policy_store_status(state: Mapping[str, Any]) -> str:
    custom = []
    for entry in state.get("presets", []):
        if isinstance(entry, Mapping):
            custom.append(
                _policy_summary(
                    name=str(entry.get("name") or ""),
                    policy=PipelinePolicy.from_dict(_policy_mapping(entry, "policy")),
                    kind="custom",
                    entry=entry,
                )
            )

    lines = [
        GENERATED_HEADER,
        GENERATED_SOURCE,
        "",
        "# Pipeline Policy Presets",
        "",
        "Revision: `{}`".format(state.get("revision", 0)),
        "Custom presets: `{}`".format(len(custom)),
        "",
        "## Built-In Presets",
        "",
        (
            "| Name | Immutable | Behavior | Codex Mode | Project Tests | "
            "Token Gate | Reviews | Auto Close | Local Commit |"
        ),
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name in preset_names():
        lines.append(
            _summary_row(
                _policy_summary(
                    name=name,
                    policy=policy_preset(name),
                    kind="built_in",
                )
            )
        )

    lines.extend(["", "## Custom Presets", ""])
    if not custom:
        lines.append("_No custom pipeline policy presets recorded._")
    else:
        lines.append(
            "| Name | Updated | Behavior | Codex Mode | Project Tests | "
            "Token Gate | Reviews | Auto Close | Local Commit |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for summary in custom:
            lines.append(_summary_row(summary, include_updated=True))
    lines.append("")
    return "\n".join(lines)


def check_generated(*, root: str | Path = ".") -> ValidationResult:
    state = load_policy_store_state(root)
    result = validate_policy_store(root=root)
    if not result.ok:
        return result
    path = pipeline_policy_status_path(root)
    if not path.exists():
        result.add_error(
            "PIPELINE_POLICIES_MISSING",
            "missing generated file: {}".format(path),
            path=str(path),
        )
        return result
    expected = render_policy_store_status(state)
    actual = path.read_text(encoding="utf-8")
    if actual != expected:
        result.add_error(
            "PIPELINE_POLICIES_OUTDATED",
            "outdated generated file: {}".format(path),
            path=str(path),
        )
    return result


def _mutate_policy_store(
    *,
    root: str | Path,
    actor: str,
    command: str,
    entity_id: str,
    mutate: Callable[[dict[str, Any], str, str], Mapping[str, Any] | None],
) -> CommandResult:
    root_path = Path(root).resolve()
    paths = ProjectPaths.from_root(root_path)
    paths.ensure_project_dirs()
    lock = FileLock(paths.lock_file("pipeline_policy_presets"))

    try:
        with lock:
            state = load_policy_store_state(root_path)
            before = validate_policy_store_state(state)
            if not before.ok:
                return _validation_failure(command, before, _revision(state))

            next_state = copy.deepcopy(state)
            revision_before = int(next_state.get("revision", 0))
            event_id = new_event_id()
            now = utc_now()
            mutation_data = dict(mutate(next_state, event_id, now) or {})
            next_state["revision"] = revision_before + 1
            next_state["updated_at"] = now

            after = validate_policy_store_state(next_state)
            if not after.ok:
                return _validation_failure(command, after, revision_before)

            state_path = pipeline_policy_store_path(root_path)
            events_path = pipeline_policy_events_path(root_path)
            generated_path = pipeline_policy_status_path(root_path)
            write_json_file(state_path, next_state)

            event = AuditEvent(
                actor=actor,
                command=command,
                entity_type="pipeline_policy_preset",
                entity_id=entity_id,
                revision_before=revision_before,
                revision_after=next_state["revision"],
                payload=_event_payload(mutation_data),
                event_id=event_id,
                timestamp=now,
            )
            AuditLog(events_path).append(event)
            atomic_write_text(generated_path, render_policy_store_status(next_state))

            result = CommandResult.success(
                command=command,
                domain="pipeline",
                message="OK: {} revision {} -> {}".format(
                    command,
                    revision_before,
                    next_state["revision"],
                ),
                data=mutation_data,
                revision_before=revision_before,
                revision_after=next_state["revision"],
            )
            result.changed_files.extend([str(state_path), str(events_path), str(generated_path)])
            result.generated_files.append(str(generated_path))
            result.events.append(event_id)
            result.warnings.extend(before.warning_messages())
            result.warnings.extend(after.warning_messages())
            return result
    except CommandError as exc:
        return _command_failure(command, exc)


def _validation_failure(
    command: str,
    validation: ValidationResult,
    revision_before: int | None,
) -> CommandResult:
    return CommandResult.failure(
        command=command,
        domain="pipeline",
        message="VALIDATION_FAILED",
        errors=[
            CommandMessage(issue.code, issue.message, issue.path)
            for issue in validation.errors
        ],
        revision_before=revision_before,
        revision_after=revision_before,
    )


def _command_failure(command: str, error: CommandError) -> CommandResult:
    return CommandResult.failure(
        command=command,
        domain="pipeline",
        message=error.code,
        errors=[error.to_message()],
    )


def _event_payload(mutation_data: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "event_type": mutation_data.get("event_type") or "policy_preset.updated",
        "action": mutation_data.get("action") or "",
        "name": mutation_data.get("name") or "",
        "summary": mutation_data.get("summary") or {},
    }


def _policy_summary(
    *,
    name: str,
    policy: PipelinePolicy,
    kind: str,
    entry: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    validation = policy.validate()
    return {
        "name": name,
        "kind": kind,
        "immutable": kind == "built_in",
        "valid": validation.ok,
        "error_codes": [issue.code for issue in validation.errors],
        "queue_selection": policy.queue.selection.value,
        "queue_max_tasks": policy.queue.max_tasks,
        "codex_mode": policy.codex.mode.value,
        "codex_adapter_mode": policy.codex.adapter_mode.value,
        "behavior_label": policy_behavior_label(policy),
        "project_test_commands": len(policy.project_tests.commands),
        "project_tests_blocking": policy.project_tests.blocking,
        "project_tests_timeout_sec": policy.project_tests.timeout_sec,
        "requires_token_gate": policy.token_budget.require_gate_pass,
        "requires_approved_change": policy.evolution.require_approved_change_for_execution,
        "requires_machine_review": policy.review.require_machine_review,
        "requires_codex_review": policy.review.require_codex_review,
        "auto_close_task": policy.closure.auto_close_task,
        "local_commit": policy.commit.create_local_commit,
        "allow_push": policy.commit.allow_push,
        "allow_merge": policy.commit.allow_merge,
        "created_at": str((entry or {}).get("created_at") or ""),
        "updated_at": str((entry or {}).get("updated_at") or ""),
        "policy": policy.to_dict(),
    }


def _policy_catalog_item(
    *,
    name: str,
    policy: PipelinePolicy,
    kind: str,
) -> dict[str, Any]:
    validation = policy.validate()
    return {
        "name": name,
        "kind": kind,
        "behavior_label": policy_behavior_label(policy),
        "valid": validation.ok,
        "selectable": validation.ok,
        "error_codes": [issue.code for issue in validation.errors],
        "warning_codes": [issue.code for issue in validation.warnings],
        "effective_summary": {
            "queue": {
                "selection": policy.queue.selection.value,
                "max_tasks": policy.queue.max_tasks,
            },
            "codex": {
                "mode": policy.codex.mode.value,
                "adapter_mode": policy.codex.adapter_mode.value,
            },
            "review": {
                "machine_review_required": policy.review.require_machine_review,
                "machine_review_outcome": policy.review.required_machine_outcome.value,
                "codex_review_required": policy.review.require_codex_review,
                "codex_review_decision": policy.review.required_codex_decision.value,
            },
            "close": {
                "auto_close_task": policy.closure.auto_close_task,
                "owner_approval_note_present": bool(
                    policy.closure.owner_approval_note.strip()
                ),
            },
            "commit": {
                "create_local_commit": policy.commit.create_local_commit,
                "mode": policy.commit.mode.value,
                "require_commit_readiness": policy.commit.require_commit_readiness,
                "allow_push": policy.commit.allow_push,
                "allow_merge": policy.commit.allow_merge,
            },
            "batch": {
                "max_steps": policy.batch.max_steps,
                "max_failures": policy.batch.max_failures,
            },
        },
    }


def _summary_row(summary: Mapping[str, Any], *, include_updated: bool = False) -> str:
    review = "{} / {}".format(
        "machine" if summary.get("requires_machine_review") else "no-machine",
        "codex" if summary.get("requires_codex_review") else "no-codex",
    )
    cells = [
        "`{}`".format(summary.get("name") or ""),
        "`{}`".format(summary.get("updated_at") or "") if include_updated else "`yes`",
        "`{}`".format(summary.get("behavior_label") or ""),
        "`{}`".format(summary.get("codex_mode") or ""),
        "`{}`".format(_project_tests_label(summary)),
        "`{}`".format("yes" if summary.get("requires_token_gate") else "no"),
        "`{}`".format(review),
        "`{}`".format("yes" if summary.get("auto_close_task") else "no"),
        "`{}`".format("yes" if summary.get("local_commit") else "no"),
    ]
    return "| {} |".format(" | ".join(cells))


def _project_tests_label(summary: Mapping[str, Any]) -> str:
    count = summary.get("project_test_commands") or 0
    if not count:
        return "none"
    mode = "blocking" if summary.get("project_tests_blocking") else "advisory"
    return "{} command(s), {}, {}s".format(
        count,
        mode,
        summary.get("project_tests_timeout_sec") or "",
    )


def _coerce_policy(policy: PipelinePolicy | Mapping[str, Any]) -> PipelinePolicy:
    if isinstance(policy, PipelinePolicy):
        return policy
    if isinstance(policy, Mapping):
        return PipelinePolicy.from_dict(policy)
    raise PipelinePolicyStoreError(
        "POLICY_PRESET_INVALID_POLICY",
        "Policy payload must be a PipelinePolicy or mapping.",
        path="policy",
    )


def _custom_presets(state: dict[str, Any]) -> list[dict[str, Any]]:
    presets = state.setdefault("presets", [])
    if not isinstance(presets, list):
        raise PipelinePolicyStoreError(
            "PIPELINE_POLICY_STORE_INVALID_PRESETS",
            "pipeline_policy_presets.presets must be a list",
            path="presets",
        )
    return presets


def _find_entry(state: Mapping[str, Any], name: str) -> dict[str, Any] | None:
    for entry in state.get("presets", []):
        if isinstance(entry, dict) and entry.get("name") == name:
            return entry
    return None


def _policy_mapping(entry: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = entry[key]
    if not isinstance(value, Mapping):
        raise TypeError("Expected mapping for policy preset field: {}".format(key))
    return value


def _normalize_name(value: Any) -> str:
    return str(value or "").strip()


def _validate_custom_name_or_raise(name: str) -> None:
    result = ValidationResult()
    _append_name_validation(result, name, "name")
    if not result.ok:
        issue = result.errors[0]
        raise PipelinePolicyStoreError(issue.code, issue.message, path=issue.path)


def _append_name_validation(result: ValidationResult, name: str, path: str) -> None:
    if not name:
        result.add_error(
            "POLICY_PRESET_INVALID_NAME",
            "Custom pipeline policy preset name is required.",
            path=path,
        )
        return
    if not CUSTOM_PRESET_NAME_RE.match(name):
        result.add_error(
            "POLICY_PRESET_INVALID_NAME",
            "Custom pipeline policy preset names must use lowercase letters, digits, underscores or hyphens.",
            path=path,
        )
    if is_builtin_preset_name(name):
        result.add_error(
            "POLICY_PRESET_BUILTIN_IMMUTABLE",
            "Built-in pipeline policy presets cannot be overwritten or deleted.",
            path=path,
        )


def _revision(state: Mapping[str, Any]) -> int | None:
    value = state.get("revision")
    return value if isinstance(value, int) else None

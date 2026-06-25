"""Read-only structured execution report template helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from ai_project_ctl.core.result import CommandError
from ai_project_ctl.core.store import read_json_file

from .report_gate import REPORT_SCHEMA_VERSION
from .state import tasks_state_path


class ReportTemplateError(CommandError):
    """Stable error for report template generation."""


def build_report_template(
    task_ref: str = "",
    *,
    root: str | Path = ".",
) -> dict[str, Any]:
    """Build a read-only structured report skeleton for one task."""

    task = _resolve_task(root=Path(root).resolve(), task_ref=task_ref)
    task_id = str(task.get("id") or "")
    task_ref_value = str(task.get("ref") or "")
    template: dict[str, Any] = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "task_id": task_id,
        "task_ref": task_ref_value,
        "implementation_summary": (
            "TODO: summarize implementation before submitting this report."
        ),
        "changed_files": [],
        "generated_files": [],
        "checks": [],
        "warnings": [],
        "blockers": [],
        "notes": [],
        "owner_decision_required": False,
        "token_usage": {
            "prompt_tokens": 0,
            "context_tokens": 0,
            "completion_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "remaining_tokens": 0,
            "model_context_limit": 0,
            "max_context_tokens": 0,
            "reserved_output_tokens": 0,
            "min_remaining_tokens": 0,
            "token_count_strategy": "template_placeholder",
            "token_count_estimated": True,
            "token_count_unavailable": False,
            "token_count_unavailable_reason": "",
        },
    }
    return template


def _resolve_task(*, root: Path, task_ref: str) -> Mapping[str, Any]:
    state = _load_tasks_state(root)
    selected_ref = task_ref.strip() or str(state.get("current_task_id") or "").strip()
    if not selected_ref:
        raise ReportTemplateError(
            "PIPELINE_REPORT_TEMPLATE_TASK_REQUIRED",
            "Pass --task or set a current task before building a report template.",
        )

    matches = [
        task
        for task in state.get("tasks", [])
        if isinstance(task, Mapping) and selected_ref in _task_reference_values(task)
    ]
    if not matches:
        raise ReportTemplateError(
            "PIPELINE_REPORT_TEMPLATE_TASK_NOT_FOUND",
            "Task reference not found: {}".format(selected_ref),
            details={"task_ref": selected_ref, "state_path": str(tasks_state_path(root))},
        )
    if len(matches) > 1:
        raise ReportTemplateError(
            "PIPELINE_REPORT_TEMPLATE_TASK_AMBIGUOUS",
            "Task reference is ambiguous: {}".format(selected_ref),
            details={
                "task_ref": selected_ref,
                "matches": [str(task.get("id") or "") for task in matches],
            },
        )
    return matches[0]


def _load_tasks_state(root: Path) -> Mapping[str, Any]:
    path = tasks_state_path(root)
    if not path.exists():
        raise ReportTemplateError(
            "PIPELINE_REPORT_TEMPLATE_TASKS_MISSING",
            "Task state file is missing.",
            details={"state_path": str(path)},
        )
    data = read_json_file(path, missing_code="PIPELINE_REPORT_TEMPLATE_TASKS_MISSING")
    if not isinstance(data, Mapping):
        raise ReportTemplateError(
            "PIPELINE_REPORT_TEMPLATE_TASKS_INVALID",
            "Task state file must contain a JSON object.",
            details={"state_path": str(path)},
        )
    return data


def _task_reference_values(task: Mapping[str, Any]) -> set[str]:
    values = {
        str(task.get("id") or ""),
        str(task.get("ref") or ""),
        str(task.get("uid") or ""),
        str(task.get("legacy_id") or ""),
    }
    aliases = task.get("aliases")
    if isinstance(aliases, Sequence) and not isinstance(aliases, (str, bytes)):
        values.update(str(alias) for alias in aliases if str(alias).strip())
    values.discard("")
    return values


__all__ = ["ReportTemplateError", "build_report_template"]

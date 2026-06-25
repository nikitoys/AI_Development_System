"""Shared helpers for UI-triggered single-task pipeline runs."""

from __future__ import annotations

from typing import Any

from .policy import PipelinePolicy


def build_ui_run_selected_queue(
    policy: PipelinePolicy,
    task_ref: str,
    *,
    confirmed: bool,
    allow_internal_change_gate_bypass: bool,
) -> dict[str, Any]:
    """Build selected_queue metadata for one UI-selected task."""

    selection = getattr(policy.queue.selection, "value", policy.queue.selection)
    return {
        "selection": str(selection),
        "task_refs": [task_ref],
        "epic_ids": [],
        "statuses": [],
        "max_tasks": 1,
        "order_by": "selected",
        "include_blocked_tasks": policy.queue.include_blocked_tasks,
        "created_by_command": "ui.run",
        "ui_run_confirmed": bool(confirmed),
        "allow_internal_change_gate_bypass": bool(
            allow_internal_change_gate_bypass
        ),
    }

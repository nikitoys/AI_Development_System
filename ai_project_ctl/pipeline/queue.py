"""Read-only planner for supervised pipeline task queues.

The planner builds on the existing taskctl execution queue rules. It narrows
that queue with owner-selected refs, filters, and pipeline policy constraints,
then selects at most one next executable task without mutating lifecycle state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from scripts import taskctl

from .policy import PipelinePolicy, QueuePolicy, QueueSelection


QUEUE_CATEGORIES = ("executable", "waiting", "blocked", "skipped")
DEPENDENCY_REASON_CODES = {"dependency_not_done", "dependency_missing"}
BLOCKING_REASON_CODES = {"parent_epic_not_executable", "current_task_conflict"}
SKIPPED_REASON_CODES = {
    "status_not_executable",
    "status_filter_mismatch",
    "epic_filter_mismatch",
    "policy_max_tasks_exceeded",
}


@dataclass(frozen=True)
class QueuePlannerRequest:
    """Owner-selected queue inputs for a read-only preview."""

    task_refs: tuple[str, ...] = ()
    epic_ids: tuple[str, ...] = ()
    statuses: tuple[str, ...] = ()
    max_tasks: int | None = None
    order_by: str = "execution"


@dataclass(frozen=True)
class QueuePreviewItem:
    """One task or selected ref in a queue preview."""

    category: str
    executable: bool
    reasons: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    id: str | None = None
    ref: str | None = None
    uid: str | None = None
    legacy_id: str | None = None
    title: str | None = None
    status: str | None = None
    epic_id: str | None = None
    priority: int | None = None
    order: int | None = None
    local_seq: int | None = None
    selected_ref: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "executable": self.executable,
            "id": self.id,
            "ref": self.ref,
            "uid": self.uid,
            "legacy_id": self.legacy_id,
            "title": self.title,
            "status": self.status,
            "epic_id": self.epic_id,
            "priority": self.priority,
            "order": self.order,
            "local_seq": self.local_seq,
            "selected_ref": self.selected_ref,
            "reasons": [dict(reason) for reason in self.reasons],
        }


@dataclass(frozen=True)
class QueuePreview:
    """Deterministic queue preview plus the selected run-next task."""

    items: tuple[QueuePreviewItem, ...]
    next_task: QueuePreviewItem | None
    policy: dict[str, Any]
    request: dict[str, Any]

    @property
    def executable(self) -> tuple[QueuePreviewItem, ...]:
        return self.by_category("executable")

    @property
    def waiting(self) -> tuple[QueuePreviewItem, ...]:
        return self.by_category("waiting")

    @property
    def blocked(self) -> tuple[QueuePreviewItem, ...]:
        return self.by_category("blocked")

    @property
    def skipped(self) -> tuple[QueuePreviewItem, ...]:
        return self.by_category("skipped")

    def by_category(self, category: str) -> tuple[QueuePreviewItem, ...]:
        return tuple(item for item in self.items if item.category == category)

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy": dict(self.policy),
            "request": dict(self.request),
            "next_task": self.next_task.to_dict() if self.next_task else None,
            "items": [item.to_dict() for item in self.items],
            "categories": {
                category: [item.to_dict() for item in self.by_category(category)]
                for category in QUEUE_CATEGORIES
            },
        }


def preview_queue(
    tasks_state: Mapping[str, Any],
    plan: Mapping[str, Any] | None = None,
    *,
    policy: PipelinePolicy | QueuePolicy | None = None,
    request: QueuePlannerRequest | None = None,
    task_refs: Sequence[str] = (),
    epic_ids: Sequence[str] = (),
    statuses: Sequence[str] = (),
    max_tasks: int | None = None,
    order_by: str = "execution",
) -> QueuePreview:
    """Return a deterministic read-only queue preview.

    Args:
        tasks_state: The loaded ``AI_PROJECT/state/tasks.json`` object.
        plan: The loaded ``AI_PROJECT/state/plan.json`` object, if available.
        policy: Pipeline or queue policy. ``QueueSelection.READY_QUEUE`` uses
            every task, ``CURRENT_TASK`` uses only the current task, and
            ``MANUAL`` uses explicit refs or filters.
        request: Optional bundled request. Explicit keyword arguments are used
            only when ``request`` is not provided.
    """

    queue_policy = _queue_policy(policy)
    queue_request = request or QueuePlannerRequest(
        task_refs=tuple(str(ref) for ref in task_refs),
        epic_ids=tuple(str(epic_id) for epic_id in epic_ids),
        statuses=tuple(str(status) for status in statuses),
        max_tasks=max_tasks,
        order_by=order_by,
    )
    limit = queue_request.max_tasks
    if limit is None:
        limit = queue_policy.max_tasks
    if limit < 1:
        raise ValueError("Queue max_tasks must be at least 1.")

    tasks = _task_list(tasks_state)
    entries_by_id = {
        str(entry["id"]): entry
        for entry in taskctl.build_execution_queue(dict(tasks_state), plan=plan)
        if entry.get("id")
    }
    current_task = _current_task(tasks_state, tasks)
    selected_refs, invalid_ref_items = _resolve_selected_refs(tasks, queue_request.task_refs)

    candidates = _base_candidates(
        tasks,
        selected_tasks=selected_refs,
        current_task=current_task,
        selection=queue_policy.selection,
        request=queue_request,
        plan=plan,
    )
    candidates = _ordered_candidates(candidates, queue_request.order_by, plan=plan)

    items: list[QueuePreviewItem] = list(invalid_ref_items)
    accepted_count = 0

    for task, selected_ref in candidates:
        entry = dict(entries_by_id.get(str(task.get("id") or ""), {}))
        if not entry:
            entry = taskctl.task_queue_entry(task, dict(tasks_state), plan=plan)

        reasons = [dict(reason) for reason in entry.get("reasons", [])]
        reasons.extend(_filter_reasons(task, queue_request, selected_ref=selected_ref))

        if not _has_reasons(reasons, {"status_filter_mismatch", "epic_filter_mismatch"}):
            if accepted_count >= limit:
                reasons.append(
                    {
                        "code": "policy_max_tasks_exceeded",
                        "detail": "queue policy max_tasks {} already reached".format(limit),
                    }
                )
            else:
                accepted_count += 1

        current_reason = _current_task_conflict_reason(task, current_task)
        if current_reason:
            reasons.append(current_reason)

        items.append(_preview_item(entry, reasons, selected_ref=selected_ref))

    next_task = next((item for item in items if item.executable), None)
    return QueuePreview(
        items=tuple(items),
        next_task=next_task,
        policy=queue_policy.to_dict(),
        request={
            "task_refs": list(queue_request.task_refs),
            "epic_ids": list(queue_request.epic_ids),
            "statuses": list(queue_request.statuses),
            "max_tasks": limit,
            "order_by": queue_request.order_by,
        },
    )


def _queue_policy(policy: PipelinePolicy | QueuePolicy | None) -> QueuePolicy:
    if policy is None:
        return QueuePolicy()
    if isinstance(policy, PipelinePolicy):
        return policy.queue
    return policy


def _task_list(tasks_state: Mapping[str, Any]) -> list[dict[str, Any]]:
    tasks = tasks_state.get("tasks", [])
    if not isinstance(tasks, Sequence) or isinstance(tasks, (str, bytes)):
        return []
    return [dict(task) for task in tasks if isinstance(task, Mapping)]


def _current_task(
    tasks_state: Mapping[str, Any],
    tasks: Sequence[Mapping[str, Any]],
) -> dict[str, Any] | None:
    current_id = tasks_state.get("current_task_id")
    if not current_id:
        return None
    for task in tasks:
        if task.get("id") == current_id:
            return dict(task)
    return None


def _resolve_selected_refs(
    tasks: Sequence[Mapping[str, Any]],
    refs: Sequence[str],
) -> tuple[list[tuple[dict[str, Any], str]], list[QueuePreviewItem]]:
    selected: list[tuple[dict[str, Any], str]] = []
    invalid: list[QueuePreviewItem] = []
    seen_ids: set[str] = set()

    for raw_ref in refs:
        ref = str(raw_ref).strip()
        if not ref:
            invalid.append(_invalid_ref_item(ref, "task_ref_empty"))
            continue

        matches = [
            task
            for task in tasks
            if ref in set(taskctl.task_reference_values(dict(task)))
        ]
        if not matches:
            invalid.append(_invalid_ref_item(ref, "task_ref_not_found"))
            continue
        if len(matches) > 1:
            invalid.append(_invalid_ref_item(ref, "task_ref_ambiguous"))
            continue

        task = dict(matches[0])
        task_id = str(task.get("id") or "")
        if task_id in seen_ids:
            continue
        seen_ids.add(task_id)
        selected.append((task, ref))

    return selected, invalid


def _base_candidates(
    tasks: Sequence[dict[str, Any]],
    *,
    selected_tasks: Sequence[tuple[dict[str, Any], str]],
    current_task: Mapping[str, Any] | None,
    selection: QueueSelection,
    request: QueuePlannerRequest,
    plan: Mapping[str, Any] | None,
) -> list[tuple[dict[str, Any], str | None]]:
    if selected_tasks:
        return list(selected_tasks)
    if request.task_refs:
        return []
    if selection == QueueSelection.CURRENT_TASK:
        return [(dict(current_task), None)] if current_task else []
    if selection == QueueSelection.MANUAL and not request.epic_ids and not request.statuses:
        return []

    sorted_tasks = taskctl.sort_execution_tasks(list(tasks), plan=plan)
    return [(dict(task), None) for task in sorted_tasks]


def _ordered_candidates(
    candidates: Sequence[tuple[dict[str, Any], str | None]],
    order_by: str,
    *,
    plan: Mapping[str, Any] | None,
) -> list[tuple[dict[str, Any], str | None]]:
    if order_by in {"owner", "selected"}:
        return [(dict(task), selected_ref) for task, selected_ref in candidates]
    if order_by != "execution":
        raise ValueError("Unknown queue order_by: {}".format(order_by))
    return sorted(
        ((dict(task), selected_ref) for task, selected_ref in candidates),
        key=lambda item: taskctl.task_execution_sort_key(item[0], plan=plan),
    )


def _filter_reasons(
    task: Mapping[str, Any],
    request: QueuePlannerRequest,
    *,
    selected_ref: str | None,
) -> list[dict[str, Any]]:
    reasons = []
    if request.epic_ids and str(task.get("epic_id") or "") not in set(request.epic_ids):
        reasons.append(
            {
                "code": "epic_filter_mismatch",
                "detail": "epic {} is outside selected epics: {}".format(
                    task.get("epic_id") or "unknown",
                    ", ".join(request.epic_ids),
                ),
            }
        )
    if request.statuses and str(task.get("status") or "") not in set(request.statuses):
        reasons.append(
            {
                "code": "status_filter_mismatch",
                "detail": "status {} is outside selected statuses: {}".format(
                    task.get("status") or "unknown",
                    ", ".join(request.statuses),
                ),
            }
        )
    if selected_ref:
        for reason in reasons:
            reason["selected_ref"] = selected_ref
    return reasons


def _current_task_conflict_reason(
    task: Mapping[str, Any],
    current_task: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    if not current_task:
        return None
    task_id = str(task.get("id") or "")
    current_id = str(current_task.get("id") or "")
    if not task_id or not current_id or task_id == current_id:
        return None
    return {
        "code": "current_task_conflict",
        "current_task_id": current_id,
        "detail": "another current task is {}".format(taskctl.task_display_label(dict(current_task))),
    }


def _preview_item(
    entry: Mapping[str, Any],
    reasons: Sequence[Mapping[str, Any]],
    *,
    selected_ref: str | None,
) -> QueuePreviewItem:
    reason_tuple = tuple(dict(reason) for reason in reasons)
    executable = not reason_tuple
    return QueuePreviewItem(
        category=_category(reason_tuple),
        executable=executable,
        reasons=reason_tuple,
        id=_optional_str(entry.get("id")),
        ref=_optional_str(entry.get("ref")),
        uid=_optional_str(entry.get("uid")),
        legacy_id=_optional_str(entry.get("legacy_id")),
        title=_optional_str(entry.get("title")),
        status=_optional_str(entry.get("status")),
        epic_id=_optional_str(entry.get("epic_id")),
        priority=_optional_int(entry.get("priority")),
        order=_optional_int(entry.get("order")),
        local_seq=_optional_int(entry.get("local_seq")),
        selected_ref=selected_ref,
    )


def _invalid_ref_item(ref: str, code: str) -> QueuePreviewItem:
    detail = {
        "task_ref_empty": "selected task ref is empty",
        "task_ref_not_found": "selected task ref not found: {}".format(ref),
        "task_ref_ambiguous": "selected task ref is ambiguous: {}".format(ref),
    }[code]
    return QueuePreviewItem(
        category="skipped",
        executable=False,
        selected_ref=ref,
        reasons=({"code": code, "detail": detail},),
    )


def _category(reasons: Sequence[Mapping[str, Any]]) -> str:
    if not reasons:
        return "executable"
    codes = {str(reason.get("code") or "") for reason in reasons}
    if codes.intersection(SKIPPED_REASON_CODES):
        return "skipped"
    if codes and codes.issubset(DEPENDENCY_REASON_CODES):
        return "waiting"
    if codes.intersection(BLOCKING_REASON_CODES):
        return "blocked"
    if codes.intersection(DEPENDENCY_REASON_CODES):
        return "waiting"
    return "blocked"


def _has_reasons(reasons: Sequence[Mapping[str, Any]], codes: set[str]) -> bool:
    return any(str(reason.get("code") or "") in codes for reason in reasons)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _optional_int(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None

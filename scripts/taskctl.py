#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
taskctl.py — strict CLI gateway for AI_PROJECT/state/tasks.json

Управляет исполняемыми задачами проекта:
- Task
- Current Task
- Codex prompt package

НЕ управляет верхним планом Project/Idea/Goal/Strategy/Initiative/Epic.
Для верхнего плана используй scripts/planctl.py.

Файлы:
  AI_PROJECT/state/tasks.json
  AI_PROJECT/events/task-events.jsonl
  AI_PROJECT/generated/CODEX_TASKS.md
  AI_PROJECT/generated/CODEX_CURRENT.md
  AI_PROJECT/generated/CODEX_PROMPT.md
  AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md

Примеры:

  python scripts/taskctl.py init

  python scripts/taskctl.py task create \
    --epic EPIC-001 \
    --title "Implement task control CLI" \
    --summary "Create strict gateway for executable tasks" \
    --scope "Create scripts/taskctl.py" \
    --allowed-file "scripts/taskctl.py" \
    --acceptance "tasks.json is validated" \
    --acceptance "CODEX_CURRENT.md is generated"

  python scripts/taskctl.py task transition TASK-001 --to ready
  python scripts/taskctl.py current set TASK-001
  python scripts/taskctl.py prompt build --write

  python scripts/taskctl.py task transition TASK-001 --to in_progress
  python scripts/taskctl.py task transition TASK-001 --to in_review
  python scripts/taskctl.py task approve TASK-001 --notes "Looks good"
  python scripts/taskctl.py task transition TASK-001 --to done

  python scripts/taskctl.py validate
  python scripts/taskctl.py render
  python scripts/taskctl.py audit --last 20
"""

import argparse
import copy
import json
import os
import re
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ai_project_ctl.core.legacy import (  # noqa: E402
    append_audit_event,
    atomic_write_text as core_atomic_write_text,
    ensure_project_dirs as core_ensure_project_dirs,
    events_dir as core_events_dir,
    generated_dir as core_generated_dir,
    state_dir as core_state_dir,
    utc_now as core_utc_now,
)


TASK_SCHEMA_VERSION = 1
PLAN_SCHEMA_VERSION = 1
TASK_REPORT_SCHEMA_VERSION = 1
TASK_UID_PREFIX = "tsk_"
TASK_REF_RE = re.compile(r"^([A-Z][A-Z0-9]{1,11})-(\d+)$")
TASK_REF_SUFFIX_WIDTH = 2

TASK_STATUSES = {
    "proposed",
    "planned",
    "ready",
    "in_progress",
    "blocked",
    "in_review",
    "changes_requested",
    "approved",
    "done",
    "deferred",
    "archived",
}

TASK_STATUS_TRANSITIONS = {
    "proposed": {"planned", "ready", "deferred", "archived"},
    "planned": {"ready", "in_progress", "blocked", "deferred", "archived"},
    "ready": {"in_progress", "blocked", "deferred", "archived"},
    "in_progress": {"blocked", "in_review", "deferred", "archived"},
    "blocked": {"ready", "in_progress", "deferred", "archived"},
    "in_review": {"changes_requested", "approved", "in_progress", "deferred", "archived"},
    "changes_requested": {"in_progress", "blocked", "deferred", "archived"},
    "approved": {"done", "archived"},
    "done": {"archived"},
    "deferred": {"planned", "ready", "archived"},
    "archived": set(),
}

PLAN_TERMINAL_OR_INACTIVE = {"done", "deferred", "archived"}
TASK_TERMINAL_OR_INACTIVE = {"done", "deferred", "archived"}
CURRENT_ALLOWED_STATUSES = {
    "planned",
    "ready",
    "in_progress",
    "blocked",
    "in_review",
    "changes_requested",
}
EXECUTABLE_CANDIDATE_STATUSES = {"planned", "ready", "changes_requested"}
PARENT_EXECUTABLE_EPIC_STATUSES = {"planned", "active"}
DEPENDENCY_TYPES = {"hard"}
DEPENDENCY_SATISFIED_STATUS = "done"

VERIFICATION_MODES = {"none", "manual", "light", "standard", "strict"}

TASK_LIST_FIELDS = {
    "scope": "Scope",
    "out_of_scope": "Out of scope",
    "allowed_files": "Allowed files",
    "acceptance_criteria": "Acceptance criteria",
    "review_instructions": "Review instructions",
    "notes": "Notes",
}

REPORT_TOP_LEVEL_KEYS = {
    "schema_version",
    "task_id",
    "task_ref",
    "implementation_summary",
    "changed_files",
    "generated_files",
    "checks",
    "warnings",
    "blockers",
    "notes",
    "owner_decision_required",
}
REPORT_REQUIRED_KEYS = {
    "task_id",
    "implementation_summary",
    "changed_files",
    "generated_files",
    "checks",
    "warnings",
    "blockers",
    "notes",
    "owner_decision_required",
}
REPORT_CHECK_KEYS = {
    "name",
    "command",
    "result",
    "duration_sec",
    "blocking",
    "details",
}
REPORT_CHECK_REQUIRED_KEYS = {"name", "result"}
REPORT_CHECK_RESULTS = {
    "pass",
    "passed",
    "fail",
    "failed",
    "warn",
    "warning",
    "skipped",
    "error",
}


class TaskError(Exception):
    pass


class PlanRefError(Exception):
    pass


def utc_now():
    return core_utc_now()


def repo_root(args):
    return Path(args.root).resolve()


def state_dir(root):
    return core_state_dir(root)


def events_dir(root):
    return core_events_dir(root)


def generated_dir(root):
    return core_generated_dir(root)


def tasks_path(root):
    return state_dir(root) / "tasks.json"


def task_events_path(root):
    return events_dir(root) / "task-events.jsonl"


def task_reports_path(root):
    return state_dir(root) / "task_reports.json"


def task_report_events_path(root):
    return events_dir(root) / "task-report-events.jsonl"


def plan_path(root):
    return state_dir(root) / "plan.json"


def generated_tasks_path(root):
    return generated_dir(root) / "CODEX_TASKS.md"


def generated_current_path(root):
    return generated_dir(root) / "CODEX_CURRENT.md"


def generated_prompt_path(root):
    return generated_dir(root) / "CODEX_PROMPT.md"


def generated_execution_queue_path(root):
    return generated_dir(root) / "TASK_EXECUTION_QUEUE.md"


def aictl_script_name():
    return "aictl" + ".py"


def ensure_project_dirs(root):
    core_ensure_project_dirs(root)


def atomic_write_text(path, text):
    core_atomic_write_text(path, text)


def write_json(path, data):
    atomic_write_text(
        path,
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    )


def read_json(path, missing_message):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise TaskError(missing_message)
    except json.JSONDecodeError as e:
        raise TaskError(
            "INVALID_JSON: {}:{}:{} {}".format(path, e.lineno, e.colno, e.msg)
        )


def load_tasks(root):
    return read_json(
        tasks_path(root),
        "TASKS_NOT_INITIALIZED: run `python scripts/taskctl.py init` first",
    )


def save_tasks(root, state):
    write_json(tasks_path(root), state)


def load_plan(root, required=True):
    path = plan_path(root)

    if not path.exists():
        if required:
            raise TaskError("PLAN_NOT_INITIALIZED: run `python scripts/planctl.py init` first")
        return None

    return read_json(path, "PLAN_NOT_INITIALIZED")


def append_event(root, actor, command, entity_type, entity_id, revision_before, revision_after, payload):
    append_audit_event(
        task_events_path(root),
        actor=actor,
        command=command,
        entity_type=entity_type,
        entity_id=entity_id,
        revision_before=revision_before,
        revision_after=revision_after,
        payload=payload,
    )


def append_report_event(root, actor, command, entity_type, entity_id, revision_before, revision_after, payload):
    append_audit_event(
        task_report_events_path(root),
        actor=actor,
        command=command,
        entity_type=entity_type,
        entity_id=entity_id,
        revision_before=revision_before,
        revision_after=revision_after,
        payload=payload,
    )


def default_tasks_state():
    now = utc_now()

    return {
        "schema_version": TASK_SCHEMA_VERSION,
        "revision": 0,
        "current_task_id": None,
        "created_at": now,
        "updated_at": now,
        "tasks": [],
    }


def default_task_reports_state():
    now = utc_now()
    return {
        "schema_version": TASK_REPORT_SCHEMA_VERSION,
        "revision": 0,
        "created_at": now,
        "updated_at": now,
        "reports": [],
        "latest_by_task": {},
    }


def load_task_reports(root, required=False):
    path = task_reports_path(root)
    if not path.exists():
        if required:
            raise TaskError("TASK_REPORTS_NOT_INITIALIZED: {}".format(path))
        return default_task_reports_state()
    return read_json(path, "TASK_REPORTS_NOT_INITIALIZED")


def save_task_reports(root, state):
    write_json(task_reports_path(root), state)


def require_keys(obj, keys, path, errors):
    if not isinstance(obj, dict):
        errors.append("{} must be an object".format(path))
        return

    for key in keys:
        if key not in obj:
            errors.append("{} missing required key `{}`".format(path, key))


def require_string(value, path, errors, allow_empty=True):
    if not isinstance(value, str):
        errors.append("{} must be a string".format(path))
        return

    if not allow_empty and not value.strip():
        errors.append("{} must not be empty".format(path))


def require_string_list(value, path, errors):
    if not isinstance(value, list):
        errors.append("{} must be a list".format(path))
        return

    for i, item in enumerate(value):
        if not isinstance(item, str):
            errors.append("{}[{}] must be a string".format(path, i))


def require_bool(value, path, errors):
    if not isinstance(value, bool):
        errors.append("{} must be a boolean".format(path))


def require_non_empty_string_list(value, path, errors):
    if not isinstance(value, list):
        errors.append("{} must be a list".format(path))
        return

    for i, item in enumerate(value):
        if not isinstance(item, str):
            errors.append("{}[{}] must be a string".format(path, i))
        elif not item.strip():
            errors.append("{}[{}] must not be empty".format(path, i))


def find_item(items, item_id, required=True):
    for item in items:
        if item.get("id") == item_id:
            return item

    if required:
        raise TaskError("ENTITY_NOT_FOUND: {}".format(item_id))

    return None


def task_reference_values(task):
    for field in ["id", "uid", "ref", "legacy_id"]:
        value = task.get(field)

        if isinstance(value, str) and value.strip():
            yield value

    aliases = task.get("aliases", [])

    if isinstance(aliases, list):
        for alias in aliases:
            if isinstance(alias, str) and alias.strip():
                yield alias


def task_identity_summary(task):
    parts = ["id={}".format(task.get("id"))]

    if task.get("ref"):
        parts.append("ref={}".format(task.get("ref")))

    if task.get("uid"):
        parts.append("uid={}".format(task.get("uid")))

    if task.get("legacy_id"):
        parts.append("legacy_id={}".format(task.get("legacy_id")))

    if task.get("aliases"):
        parts.append("aliases=[{}]".format(", ".join(task.get("aliases", []))))

    return ", ".join(parts)


def validate_unique_task_references(tasks):
    errors = []
    owners = {}

    for task in tasks:
        if not isinstance(task, dict):
            continue

        task_id = task.get("id")
        seen_for_task = set()

        for value in task_reference_values(task):
            if value in seen_for_task:
                continue

            seen_for_task.add(value)

            if value in owners and owners[value] != task_id:
                errors.append(
                    "duplicate task reference value: {} used by {} and {}".format(
                        value,
                        owners[value],
                        task_id,
                    )
                )
                continue

            owners[value] = task_id

    return errors


def resolve_task_ref(tasks, task_ref):
    if not isinstance(task_ref, str) or not task_ref.strip():
        raise TaskError("TASK_REF_EMPTY")

    ref = task_ref.strip()
    matches = []

    for task in tasks:
        if not isinstance(task, dict):
            continue

        if any(value == ref for value in task_reference_values(task)):
            matches.append(task)

    if not matches:
        raise TaskError("TASK_REF_NOT_FOUND: {}".format(ref))

    if len(matches) > 1:
        details = "\n- " + "\n- ".join(task_identity_summary(task) for task in matches)
        raise TaskError("AMBIGUOUS_TASK_REF: {}{}".format(ref, details))

    return matches[0]


def task_report_reference_matches(task, value):
    if not isinstance(value, str) or not value.strip():
        return False
    return value.strip() in set(task_reference_values(task))


def next_report_id(reports):
    max_num = 0
    head = "RPT-"
    for report in reports:
        report_id = str(report.get("id", ""))
        if report_id.startswith(head):
            suffix = report_id[len(head):]
            if suffix.isdigit():
                max_num = max(max_num, int(suffix))
    return "{}{:03d}".format(head, max_num + 1)


def read_report_payload(path_text):
    path = Path(path_text)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise TaskError("REPORT_FILE_NOT_FOUND: {}".format(path))
    except json.JSONDecodeError as e:
        raise TaskError(
            "INVALID_REPORT_JSON: {}:{}:{} {}".format(path, e.lineno, e.colno, e.msg)
        )
    if not isinstance(payload, dict):
        raise TaskError("INVALID_REPORT_SCHEMA: report must be a JSON object")
    return payload


def normalize_task_report_payload(payload, task):
    errors = []
    unknown = sorted(set(payload.keys()) - REPORT_TOP_LEVEL_KEYS)
    if unknown:
        errors.append("report has unknown field(s): {}".format(", ".join(unknown)))

    missing = sorted(REPORT_REQUIRED_KEYS - set(payload.keys()))
    if missing:
        errors.append("report missing required field(s): {}".format(", ".join(missing)))

    schema_version = payload.get("schema_version", TASK_REPORT_SCHEMA_VERSION)
    if schema_version != TASK_REPORT_SCHEMA_VERSION:
        errors.append("schema_version must be {}".format(TASK_REPORT_SCHEMA_VERSION))

    task_id = payload.get("task_id")
    require_string(task_id, "report.task_id", errors, allow_empty=False)
    if isinstance(task_id, str) and task_id.strip() and not task_report_reference_matches(task, task_id):
        errors.append("report.task_id does not match target task: {}".format(task_id))

    task_ref = payload.get("task_ref", "")
    if task_ref != "":
        require_string(task_ref, "report.task_ref", errors, allow_empty=False)
        if isinstance(task_ref, str) and task_ref.strip() and not task_report_reference_matches(task, task_ref):
            errors.append("report.task_ref does not match target task: {}".format(task_ref))

    implementation_summary = payload.get("implementation_summary")
    require_string(
        implementation_summary,
        "report.implementation_summary",
        errors,
        allow_empty=False,
    )

    for field in ["changed_files", "generated_files", "warnings", "blockers", "notes"]:
        require_string_list(payload.get(field), "report." + field, errors)

    require_bool(
        payload.get("owner_decision_required"),
        "report.owner_decision_required",
        errors,
    )

    checks = payload.get("checks")
    if not isinstance(checks, list):
        errors.append("report.checks must be a list")
        checks = []

    normalized_checks = []
    for index, check in enumerate(checks):
        path = "report.checks[{}]".format(index)
        if not isinstance(check, dict):
            errors.append("{} must be an object".format(path))
            continue
        unknown_check_keys = sorted(set(check.keys()) - REPORT_CHECK_KEYS)
        if unknown_check_keys:
            errors.append(
                "{} has unknown field(s): {}".format(
                    path,
                    ", ".join(unknown_check_keys),
                )
            )
        missing_check_keys = sorted(REPORT_CHECK_REQUIRED_KEYS - set(check.keys()))
        if missing_check_keys:
            errors.append(
                "{} missing required field(s): {}".format(
                    path,
                    ", ".join(missing_check_keys),
                )
            )
        require_string(check.get("name"), path + ".name", errors, allow_empty=False)
        require_string(check.get("result"), path + ".result", errors, allow_empty=False)
        result = str(check.get("result") or "").strip().lower()
        if result and result not in REPORT_CHECK_RESULTS:
            errors.append(
                "{}.result must be one of {}".format(
                    path,
                    ", ".join(sorted(REPORT_CHECK_RESULTS)),
                )
            )
        if "command" in check:
            require_string(check.get("command"), path + ".command", errors)
        if "details" in check:
            require_string(check.get("details"), path + ".details", errors)
        duration = check.get("duration_sec")
        if duration is not None:
            if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration < 0:
                errors.append(path + ".duration_sec must be a non-negative number")
        blocking = check.get("blocking", False)
        if not isinstance(blocking, bool):
            errors.append(path + ".blocking must be a boolean")
        normalized_checks.append(
            {
                "name": str(check.get("name") or ""),
                "command": str(check.get("command") or ""),
                "result": result,
                "duration_sec": duration,
                "blocking": blocking,
                "details": str(check.get("details") or ""),
            }
        )

    if errors:
        raise TaskError("INVALID_REPORT_SCHEMA:\n- " + "\n- ".join(errors))

    return {
        "schema_version": TASK_REPORT_SCHEMA_VERSION,
        "task_id": task.get("id"),
        "task_ref": task.get("ref") or "",
        "reported_task_id": task_id,
        "reported_task_ref": task_ref,
        "implementation_summary": implementation_summary,
        "changed_files": list(payload.get("changed_files") or []),
        "generated_files": list(payload.get("generated_files") or []),
        "checks": normalized_checks,
        "warnings": list(payload.get("warnings") or []),
        "blockers": list(payload.get("blockers") or []),
        "notes": list(payload.get("notes") or []),
        "owner_decision_required": payload.get("owner_decision_required"),
    }


def task_id_map(tasks):
    return {
        task.get("id"): task
        for task in tasks
        if isinstance(task, dict) and isinstance(task.get("id"), str) and task.get("id")
    }


def task_dependency_list(task):
    deps = task.get("depends_on", [])
    return deps if isinstance(deps, list) else []


def hard_dependency_edges(tasks):
    tasks_by_id = task_id_map(tasks)
    edges = {}

    for task in tasks:
        if not isinstance(task, dict):
            continue

        task_id = task.get("id")

        if not task_id:
            continue

        edges.setdefault(task_id, [])

        for dep in task_dependency_list(task):
            if not isinstance(dep, dict):
                continue

            dep_task_id = dep.get("task_id")

            if dep.get("type") == "hard" and dep_task_id in tasks_by_id:
                edges[task_id].append(dep_task_id)

    return edges


def find_hard_dependency_cycle(tasks):
    edges = hard_dependency_edges(tasks)
    visiting = set()
    visited = set()
    stack = []

    def visit(task_id):
        if task_id in visiting:
            start = stack.index(task_id)
            return stack[start:] + [task_id]

        if task_id in visited:
            return None

        visiting.add(task_id)
        stack.append(task_id)

        for dep_task_id in sorted(edges.get(task_id, [])):
            cycle = visit(dep_task_id)

            if cycle:
                return cycle

        stack.pop()
        visiting.remove(task_id)
        visited.add(task_id)
        return None

    for task_id in sorted(edges):
        cycle = visit(task_id)

        if cycle:
            return cycle

    return None


def format_task_id_path(task_ids, tasks_by_id):
    labels = []

    for task_id in task_ids:
        task = tasks_by_id.get(task_id) or {"id": task_id}
        labels.append(task_display_label(task))

    return " -> ".join(labels)


def validate_task_dependencies(tasks):
    errors = []
    tasks_by_id = task_id_map(tasks)

    for i, task in enumerate(tasks):
        if not isinstance(task, dict):
            continue

        path = "tasks[{}]".format(i)
        task_id = task.get("id")

        if "depends_on" not in task:
            continue

        deps = task.get("depends_on")

        if not isinstance(deps, list):
            errors.append("{}.depends_on must be a list".format(path))
            continue

        seen = set()

        for j, dep in enumerate(deps):
            dep_path = "{}.depends_on[{}]".format(path, j)

            if not isinstance(dep, dict):
                errors.append("{} must be an object".format(dep_path))
                continue

            dep_task_id = dep.get("task_id")

            if not isinstance(dep_task_id, str) or not dep_task_id.strip():
                errors.append("{}.task_id must be a non-empty string".format(dep_path))
            elif dep_task_id not in tasks_by_id:
                errors.append("{}.task_id references missing task: {}".format(dep_path, dep_task_id))
            elif dep_task_id == task_id:
                errors.append("{}.task_id must not reference itself: {}".format(dep_path, dep_task_id))

            if isinstance(dep_task_id, str) and dep_task_id.strip():
                if dep_task_id in seen:
                    errors.append("duplicate dependency for task {}: {}".format(task_id, dep_task_id))
                else:
                    seen.add(dep_task_id)

            dep_type = dep.get("type")

            if dep_type not in DEPENDENCY_TYPES:
                errors.append("{}.type must be hard".format(dep_path))

            if "reason" in dep and not isinstance(dep.get("reason"), str):
                errors.append("{}.reason must be a string".format(dep_path))

            if "created_at" in dep and not isinstance(dep.get("created_at"), str):
                errors.append("{}.created_at must be a string".format(dep_path))

    cycle = find_hard_dependency_cycle(tasks)

    if cycle:
        errors.append("hard dependency cycle: {}".format(format_task_id_path(cycle, tasks_by_id)))

    return errors


def next_id(prefix, items):
    max_num = 0
    head = prefix + "-"

    for item in items:
        item_id = str(item.get("id", ""))

        if item_id.startswith(head):
            suffix = item_id[len(head):]

            if suffix.isdigit():
                max_num = max(max_num, int(suffix))

    return "{}-{:03d}".format(prefix, max_num + 1)


def next_order(items, parent_key=None, parent_id=None):
    selected = items

    if parent_key is not None:
        selected = [x for x in items if x.get(parent_key) == parent_id]

    if not selected:
        return 1

    return max(int(x.get("order", 0)) for x in selected) + 1


def generate_task_uid(tasks):
    existing = {
        task.get("uid")
        for task in tasks
        if isinstance(task, dict) and isinstance(task.get("uid"), str)
    }

    while True:
        uid = TASK_UID_PREFIX + uuid.uuid4().hex[:12]

        if uid not in existing:
            return uid


def format_task_ref(epic_key, local_seq):
    return "{}-{:0{}d}".format(epic_key, local_seq, TASK_REF_SUFFIX_WIDTH)


def task_ref_sequence(value, epic_key):
    if not isinstance(value, str):
        return None

    match = TASK_REF_RE.fullmatch(value.strip())

    if not match:
        return None

    if match.group(1) != epic_key:
        return None

    return int(match.group(2))


def task_ref_sequences_in_text(value, epic_key):
    if not isinstance(value, str) or not epic_key:
        return set()

    pattern = re.compile(r"(?<![A-Z0-9]){}-(\d+)(?![A-Z0-9])".format(re.escape(epic_key)))
    return {int(match.group(1)) for match in pattern.finditer(value)}


def used_local_sequences(tasks, epic_id, epic_key):
    used = set()

    for task in tasks:
        if not isinstance(task, dict):
            continue

        local_seq = task.get("local_seq")

        if task.get("epic_key") == epic_key and isinstance(local_seq, int) and not isinstance(local_seq, bool) and local_seq > 0:
            used.add(local_seq)

        ref_seq = task_ref_sequence(task.get("ref"), epic_key)

        if ref_seq:
            used.add(ref_seq)

        if task.get("epic_id") == epic_id:
            used.update(task_ref_sequences_in_text(task.get("title"), epic_key))
            used.update(task_ref_sequences_in_text(task.get("summary"), epic_key))

            for note in task.get("notes", []):
                used.update(task_ref_sequences_in_text(note, epic_key))

    return used


def allocate_local_seq(tasks, epic_id, epic_key):
    used = used_local_sequences(tasks, epic_id, epic_key)
    return max(used or {0}) + 1


IDENTITY_MIGRATION_FIELDS = [
    "uid",
    "legacy_id",
    "aliases",
    "epic_key",
    "local_seq",
    "ref",
]


def task_identity_field_changes(before, after):
    fields = {}

    for field in IDENTITY_MIGRATION_FIELDS:
        if before.get(field) != after.get(field):
            fields[field] = {
                "before": before.get(field),
                "after": after.get(field),
            }

    return fields


def plan_epic_key_map(plan):
    return {
        epic.get("id"): epic.get("key")
        for epic in plan_epics(plan)
        if isinstance(epic, dict) and isinstance(epic.get("id"), str)
    }


def validate_identity_migration_preconditions(state, plan):
    errors = []
    epic_keys = plan_epic_key_map(plan)
    order_by_epic = {}

    for task in state.get("tasks", []):
        if not isinstance(task, dict):
            continue

        task_id = task.get("id")
        epic_id = task.get("epic_id")
        epic_key = epic_keys.get(epic_id)
        order = task.get("order")

        if epic_key:
            if not isinstance(order, int) or isinstance(order, bool) or order < 1:
                errors.append(
                    "{} cannot receive deterministic ref for epic {}/{}: order must be positive integer".format(
                        task_id,
                        epic_id,
                        epic_key,
                    )
                )
                continue

            epic_orders = order_by_epic.setdefault(epic_id, {})

            if order in epic_orders:
                errors.append(
                    "duplicate task order in epic {}/{}: {} used by {} and {}".format(
                        epic_id,
                        epic_key,
                        order,
                        epic_orders[order],
                        task_id,
                    )
                )
            else:
                epic_orders[order] = task_id

            expected_ref = format_task_ref(epic_key, order)

            if "epic_key" in task and task.get("epic_key") != epic_key:
                errors.append(
                    "{} existing epic_key must be {} for parent epic {}: {}".format(
                        task_id,
                        epic_key,
                        epic_id,
                        task.get("epic_key"),
                    )
                )

            if "local_seq" in task and task.get("local_seq") != order:
                errors.append(
                    "{} existing local_seq must match order {}: {}".format(
                        task_id,
                        order,
                        task.get("local_seq"),
                    )
                )

            if "ref" in task and task.get("ref") != expected_ref:
                errors.append(
                    "{} existing ref must be {} from epic key/order: {}".format(
                        task_id,
                        expected_ref,
                        task.get("ref"),
                    )
                )
        elif any(field in task for field in ["epic_key", "local_seq", "ref"]):
            errors.append(
                "{} belongs to unkeyed epic {} and must not already carry epic_key/local_seq/ref".format(
                    task_id,
                    epic_id,
                )
            )

    return errors


def validate_migrated_identity_state(state, plan):
    errors = validate_tasks(state, plan=plan, check_plan=True)
    tasks = state.get("tasks", [])

    for task in tasks:
        if not isinstance(task, dict):
            continue

        legacy_id = task.get("legacy_id")

        if not legacy_id:
            continue

        try:
            resolved = resolve_task_ref(tasks, legacy_id)
        except TaskError as exc:
            errors.append("{} legacy_id is not resolvable: {}".format(task.get("id"), exc))
            continue

        if resolved.get("id") != task.get("id"):
            errors.append(
                "{} legacy_id resolves to {} instead of itself".format(
                    task.get("id"),
                    resolved.get("id"),
                )
            )

    return errors


def require_valid_migrated_identity_state(state, plan):
    errors = validate_migrated_identity_state(state, plan)

    if errors:
        raise TaskError("IDENTITY_MIGRATION_VALIDATION_FAILED:\n- " + "\n- ".join(errors))


def apply_identity_migration(state, plan):
    precondition_errors = validate_identity_migration_preconditions(state, plan)

    if precondition_errors:
        raise TaskError("IDENTITY_MIGRATION_UNSAFE:\n- " + "\n- ".join(precondition_errors))

    epic_keys = plan_epic_key_map(plan)
    tasks = state.get("tasks", [])
    now = utc_now()
    changes = []

    for task in tasks:
        if not isinstance(task, dict):
            continue

        before = copy.deepcopy(task)
        task_id = task.get("id")

        if not task.get("uid"):
            task["uid"] = generate_task_uid(tasks)

        if not task.get("legacy_id"):
            task["legacy_id"] = task_id

        aliases = task.get("aliases")

        if aliases is None:
            aliases = []
        else:
            aliases = list(aliases)

        if task_id not in aliases:
            aliases.append(task_id)

        task["aliases"] = aliases

        epic_key = epic_keys.get(task.get("epic_id"))

        if epic_key:
            local_seq = task.get("order")
            task["epic_key"] = epic_key
            task["local_seq"] = local_seq
            task["ref"] = format_task_ref(epic_key, local_seq)

        fields = task_identity_field_changes(before, task)

        if fields:
            task["updated_at"] = now
            changes.append(
                {
                    "id": task_id,
                    "before_label": task_display_label(before),
                    "after_label": task_display_label(task),
                    "fields": fields,
                }
            )

    require_valid_migrated_identity_state(state, plan)
    return changes


def identity_migration_report(changes, dry_run=False):
    lines = []
    lines.append("Migration: identity")
    lines.append("Mode: {}".format("dry-run" if dry_run else "apply"))
    lines.append("Changed tasks: {}".format(len(changes)))

    if not changes:
        lines.append("No identity changes needed.")
        return "\n".join(lines)

    for change in changes:
        rendered_fields = []

        for field in IDENTITY_MIGRATION_FIELDS:
            if field not in change.get("fields", {}):
                continue

            field_change = change["fields"][field]
            rendered_fields.append(
                "{}: {} -> {}".format(
                    field,
                    json.dumps(field_change.get("before"), ensure_ascii=False),
                    json.dumps(field_change.get("after"), ensure_ascii=False),
                )
            )

        lines.append(
            "- {}: {}".format(
                change.get("id"),
                "; ".join(rendered_fields),
            )
        )

    return "\n".join(lines)


def task_display_label(task):
    ref = task.get("ref")
    task_id = task.get("id")

    if ref:
        return "{} ({})".format(ref, task_id)

    return task_id


def task_epic_label(task, plan=None):
    epic_id = task.get("epic_id")
    epic_key = task.get("epic_key")

    if not epic_key and plan:
        epic = find_plan_epic(plan, epic_id)

        if epic:
            epic_key = epic.get("key")

    if epic_key:
        return "{}/{}".format(epic_id, epic_key)

    return epic_id


def plan_epics(plan):
    if not isinstance(plan, dict):
        return []

    epics = plan.get("epics", [])
    return epics if isinstance(epics, list) else []


def plan_initiatives(plan):
    if not isinstance(plan, dict):
        return []

    initiatives = plan.get("initiatives", [])
    return initiatives if isinstance(initiatives, list) else []


def find_plan_epic(plan, epic_id):
    for epic in plan_epics(plan):
        if epic.get("id") == epic_id:
            return epic

    return None


def find_plan_initiative(plan, initiative_id):
    for initiative in plan_initiatives(plan):
        if initiative.get("id") == initiative_id:
            return initiative

    return None


def task_execution_sort_key(task, plan=None):
    epic = find_plan_epic(plan, task.get("epic_id")) if plan else None
    priority = task.get("priority") if isinstance(task.get("priority"), int) else 999999
    epic_order = epic.get("order") if epic and isinstance(epic.get("order"), int) else 999999
    local_or_task_order = task.get("local_seq")

    if not isinstance(local_or_task_order, int) or isinstance(local_or_task_order, bool):
        local_or_task_order = task.get("order") if isinstance(task.get("order"), int) else 999999

    ref_or_id = task.get("ref") or task.get("id") or ""
    uid_or_id = task.get("uid") or task.get("id") or ""

    return (priority, epic_order, local_or_task_order, ref_or_id, uid_or_id)


def sort_execution_tasks(tasks, plan=None):
    return sorted(tasks, key=lambda task: task_execution_sort_key(task, plan=plan))


def task_dependency_blockers(task, tasks):
    blockers = []
    tasks_by_id = task_id_map(tasks)

    for dep in task_dependency_list(task):
        if not isinstance(dep, dict) or dep.get("type") != "hard":
            continue

        dep_task_id = dep.get("task_id")
        dep_task = tasks_by_id.get(dep_task_id)

        if dep_task is None:
            blockers.append(
                {
                    "code": "dependency_missing",
                    "dependency_id": dep_task_id,
                    "detail": "depends on missing task {}".format(dep_task_id),
                }
            )
            continue

        if dep_task.get("status") != DEPENDENCY_SATISFIED_STATUS:
            blockers.append(
                {
                    "code": "dependency_not_done",
                    "dependency_id": dep_task_id,
                    "detail": "depends on {} with status {}".format(
                        task_display_label(dep_task),
                        dep_task.get("status"),
                    ),
                }
            )

    return blockers


def ensure_task_dependencies_satisfied(state, task):
    blockers = task_dependency_blockers(task, state.get("tasks", []))

    if not blockers:
        return

    blocker = blockers[0]

    if blocker["code"] == "dependency_missing":
        raise TaskError(
            "TASK_DEPENDENCY_MISSING: {} depends on {}".format(
                task_display_label(task),
                blocker.get("dependency_id"),
            )
        )

    raise TaskError(
        "TASK_DEPENDENCY_NOT_DONE: {} depends on {}".format(
            task_display_label(task),
            blocker.get("dependency_id"),
        )
    )


def task_executable_reasons(task, state, plan=None):
    reasons = []
    status = task.get("status")

    if status not in EXECUTABLE_CANDIDATE_STATUSES:
        reasons.append(
            {
                "code": "status_not_executable",
                "detail": "status is {}".format(status),
            }
        )

    epic = find_plan_epic(plan, task.get("epic_id")) if plan else None

    if epic is None:
        reasons.append(
            {
                "code": "parent_epic_not_executable",
                "detail": "parent epic missing: {}".format(task.get("epic_id")),
            }
        )
    elif epic.get("status") not in PARENT_EXECUTABLE_EPIC_STATUSES:
        reasons.append(
            {
                "code": "parent_epic_not_executable",
                "detail": "parent epic {} status is {}".format(epic.get("id"), epic.get("status")),
            }
        )
    else:
        initiative = find_plan_initiative(plan, epic.get("initiative_id")) if plan else None

        if initiative and initiative.get("status") == "archived":
            reasons.append(
                {
                    "code": "parent_epic_not_executable",
                    "detail": "parent initiative {} is archived".format(initiative.get("id")),
                }
            )

    reasons.extend(task_dependency_blockers(task, state.get("tasks", [])))
    return reasons


def task_queue_entry(task, state, plan=None):
    reasons = task_executable_reasons(task, state, plan=plan)

    return {
        "id": task.get("id"),
        "ref": task.get("ref"),
        "uid": task.get("uid"),
        "legacy_id": task.get("legacy_id"),
        "title": task.get("title"),
        "status": task.get("status"),
        "epic_id": task.get("epic_id"),
        "priority": task.get("priority"),
        "order": task.get("order"),
        "local_seq": task.get("local_seq"),
        "executable": not reasons,
        "reasons": reasons,
    }


def build_execution_queue(state, plan=None):
    entries = [
        task_queue_entry(task, state, plan=plan)
        for task in sort_execution_tasks(state.get("tasks", []), plan=plan)
    ]

    return entries


def queue_entry_has_reason(entry, codes):
    return any(reason.get("code") in codes for reason in entry.get("reasons", []))


def validate_plan_refs_for_tasks(state, plan):
    errors = []

    if plan is None:
        if state.get("tasks"):
            errors.append("plan.json is required when tasks exist")
        return errors

    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        errors.append("plan.schema_version must be {}".format(PLAN_SCHEMA_VERSION))

    epic_ids = set()

    for epic in plan_epics(plan):
        epic_id = epic.get("id")

        if epic_id:
            epic_ids.add(epic_id)

    for i, task in enumerate(state.get("tasks", [])):
        path = "tasks[{}]".format(i)
        epic_id = task.get("epic_id")

        if epic_id not in epic_ids:
            errors.append("{}.epic_id references missing epic: {}".format(path, epic_id))
            continue

        epic = find_plan_epic(plan, epic_id)
        task_status = task.get("status")

        if epic and epic.get("status") in PLAN_TERMINAL_OR_INACTIVE and task_status not in TASK_TERMINAL_OR_INACTIVE:
            errors.append(
                "task {} is {} under inactive epic {} ({})".format(
                    task.get("id"),
                    task_status,
                    epic_id,
                    epic.get("status"),
                )
            )

        if epic:
            initiative = find_plan_initiative(plan, epic.get("initiative_id"))

            if initiative and initiative.get("status") == "archived" and task_status not in TASK_TERMINAL_OR_INACTIVE:
                errors.append(
                    "task {} is {} under epic {} whose initiative {} is archived".format(
                        task.get("id"),
                        task_status,
                        epic_id,
                        initiative.get("id"),
                    )
                )

    return errors


def validate_tasks(state, plan=None, check_plan=True):
    errors = []

    require_keys(
        state,
        [
            "schema_version",
            "revision",
            "current_task_id",
            "created_at",
            "updated_at",
            "tasks",
        ],
        "tasks_state",
        errors,
    )

    if errors:
        return errors

    if state.get("schema_version") != TASK_SCHEMA_VERSION:
        errors.append("schema_version must be {}".format(TASK_SCHEMA_VERSION))

    if not isinstance(state.get("revision"), int) or state.get("revision") < 0:
        errors.append("revision must be a non-negative integer")

    current_task_id = state.get("current_task_id")

    if current_task_id is not None and not isinstance(current_task_id, str):
        errors.append("current_task_id must be null or string")

    tasks = state.get("tasks")

    if not isinstance(tasks, list):
        errors.append("tasks must be a list")
        tasks = []

    task_ids = set()
    task_uids = {}
    task_refs = {}
    task_aliases = {}
    task_local_seqs = {}

    for i, task in enumerate(tasks):
        path = "tasks[{}]".format(i)

        require_keys(
            task,
            [
                "id",
                "epic_id",
                "title",
                "status",
                "summary",
                "description",
                "priority",
                "order",
                "active_role",
                "active_stage",
                "active_document",
                "expected_result",
                "verification_mode",
                "scope",
                "out_of_scope",
                "allowed_files",
                "acceptance_criteria",
                "review_instructions",
                "notes",
                "created_at",
                "updated_at",
            ],
            path,
            errors,
        )

        if not isinstance(task, dict):
            continue

        task_id = task.get("id")

        if task_id in task_ids:
            errors.append("duplicate task id: {}".format(task_id))

        task_ids.add(task_id)

        require_string(task.get("id"), path + ".id", errors, allow_empty=False)
        require_string(task.get("epic_id"), path + ".epic_id", errors, allow_empty=False)
        require_string(task.get("title"), path + ".title", errors, allow_empty=False)
        require_string(task.get("summary"), path + ".summary", errors)
        require_string(task.get("description"), path + ".description", errors)
        require_string(task.get("active_role"), path + ".active_role", errors)
        require_string(task.get("active_stage"), path + ".active_stage", errors)
        require_string(task.get("active_document"), path + ".active_document", errors)
        require_string(task.get("expected_result"), path + ".expected_result", errors)

        if task.get("status") not in TASK_STATUSES:
            errors.append("{}.status is invalid: {}".format(path, task.get("status")))

        if task.get("verification_mode") not in VERIFICATION_MODES:
            errors.append("{}.verification_mode is invalid: {}".format(path, task.get("verification_mode")))

        if not isinstance(task.get("priority"), int):
            errors.append("{}.priority must be integer".format(path))

        if not isinstance(task.get("order"), int):
            errors.append("{}.order must be integer".format(path))

        for field in TASK_LIST_FIELDS:
            require_string_list(task.get(field), path + "." + field, errors)

        if "uid" in task:
            uid = task.get("uid")
            require_string(uid, path + ".uid", errors, allow_empty=False)

            if isinstance(uid, str) and uid.strip():
                if uid in task_uids:
                    errors.append("duplicate task uid: {} used by {} and {}".format(uid, task_uids[uid], task_id))
                else:
                    task_uids[uid] = task_id

        if "ref" in task:
            ref = task.get("ref")
            require_string(ref, path + ".ref", errors, allow_empty=False)

            if isinstance(ref, str) and ref.strip():
                if ref in task_refs:
                    errors.append("duplicate task ref: {} used by {} and {}".format(ref, task_refs[ref], task_id))
                else:
                    task_refs[ref] = task_id

        if "legacy_id" in task:
            require_string(task.get("legacy_id"), path + ".legacy_id", errors, allow_empty=False)

        if "aliases" in task:
            aliases = task.get("aliases")
            require_non_empty_string_list(aliases, path + ".aliases", errors)

            if isinstance(aliases, list):
                for alias in aliases:
                    if not isinstance(alias, str) or not alias.strip():
                        continue

                    if alias in task_aliases:
                        errors.append(
                            "duplicate task alias: {} used by {} and {}".format(
                                alias,
                                task_aliases[alias],
                                task_id,
                            )
                        )
                    else:
                        task_aliases[alias] = task_id

        epic_key = task.get("epic_key")

        if "epic_key" in task:
            require_string(epic_key, path + ".epic_key", errors, allow_empty=False)

            if check_plan and plan:
                epic = find_plan_epic(plan, task.get("epic_id"))
                expected_key = epic.get("key") if epic else None

                if epic and expected_key != epic_key:
                    errors.append(
                        "{}.epic_key must match parent epic key {}: {}".format(
                            path,
                            expected_key,
                            epic_key,
                        )
                    )

        local_seq = task.get("local_seq")
        local_seq_valid = True

        if "local_seq" in task:
            if not isinstance(local_seq, int) or isinstance(local_seq, bool) or local_seq < 1:
                errors.append("{}.local_seq must be a positive integer".format(path))
                local_seq_valid = False

            if "epic_key" not in task:
                errors.append("{}.local_seq requires epic_key".format(path))
                local_seq_valid = False

        if "epic_key" in task and "local_seq" in task and local_seq_valid:
            key = (epic_key, local_seq)

            if key in task_local_seqs:
                errors.append(
                    "duplicate task local_seq for epic_key {}: {} used by {} and {}".format(
                        epic_key,
                        local_seq,
                        task_local_seqs[key],
                        task_id,
                    )
                )
            else:
                task_local_seqs[key] = task_id

        if "ref" in task and "epic_key" in task and "local_seq" in task and local_seq_valid:
            expected_ref = format_task_ref(epic_key, local_seq)

            if task.get("ref") != expected_ref:
                errors.append("{}.ref must be {} for epic_key/local_seq".format(path, expected_ref))

        if task.get("status") == "approved":
            if not task.get("approved_by") or not task.get("approved_at"):
                errors.append("{} approved task must have approved_by and approved_at".format(path))

    errors.extend(validate_unique_task_references(tasks))
    errors.extend(validate_task_dependencies(tasks))

    if current_task_id:
        current = find_item(tasks, current_task_id, required=False)

        if current is None:
            errors.append("current_task_id references missing task: {}".format(current_task_id))
        elif current.get("status") not in CURRENT_ALLOWED_STATUSES:
            errors.append(
                "current_task_id references task with non-current status: {} ({})".format(
                    current_task_id,
                    current.get("status"),
                )
            )

    if check_plan:
        errors.extend(validate_plan_refs_for_tasks(state, plan))

    return errors


def validate_task_reports(report_state, tasks_state):
    errors = []
    require_keys(
        report_state,
        [
            "schema_version",
            "revision",
            "created_at",
            "updated_at",
            "reports",
            "latest_by_task",
        ],
        "task_reports_state",
        errors,
    )
    if errors:
        return errors

    if report_state.get("schema_version") != TASK_REPORT_SCHEMA_VERSION:
        errors.append(
            "task_reports.schema_version must be {}".format(TASK_REPORT_SCHEMA_VERSION)
        )
    if not isinstance(report_state.get("revision"), int) or report_state.get("revision") < 0:
        errors.append("task_reports.revision must be a non-negative integer")
    require_string(report_state.get("created_at"), "task_reports.created_at", errors)
    require_string(report_state.get("updated_at"), "task_reports.updated_at", errors)

    reports = report_state.get("reports")
    if not isinstance(reports, list):
        errors.append("task_reports.reports must be a list")
        reports = []
    latest_by_task = report_state.get("latest_by_task")
    if not isinstance(latest_by_task, dict):
        errors.append("task_reports.latest_by_task must be an object")
        latest_by_task = {}

    tasks_by_id = task_id_map(tasks_state.get("tasks", []))
    reports_by_id = {}

    for index, record in enumerate(reports):
        path = "task_reports.reports[{}]".format(index)
        require_keys(
            record,
            [
                "id",
                "task_id",
                "task_ref",
                "submitted_at",
                "submitted_by",
                "source_file",
                "report",
            ],
            path,
            errors,
        )
        if not isinstance(record, dict):
            continue
        report_id = record.get("id")
        require_string(report_id, path + ".id", errors, allow_empty=False)
        if isinstance(report_id, str) and report_id.strip():
            if report_id in reports_by_id:
                errors.append("duplicate task report id: {}".format(report_id))
            else:
                reports_by_id[report_id] = record

        task_id = record.get("task_id")
        require_string(task_id, path + ".task_id", errors, allow_empty=False)
        if isinstance(task_id, str) and task_id.strip() and task_id not in tasks_by_id:
            errors.append("{}.task_id references missing task: {}".format(path, task_id))

        for field in ["task_ref", "submitted_at", "submitted_by", "source_file"]:
            require_string(record.get(field), path + "." + field, errors)

        report = record.get("report")
        if not isinstance(report, dict):
            errors.append(path + ".report must be an object")
            continue

        report_task_id = report.get("task_id")
        if report_task_id != task_id:
            errors.append(path + ".report.task_id must match record task_id")

        for field in ["changed_files", "generated_files", "warnings", "blockers", "notes"]:
            require_string_list(report.get(field), path + ".report." + field, errors)
        require_string(
            report.get("implementation_summary"),
            path + ".report.implementation_summary",
            errors,
            allow_empty=False,
        )
        require_bool(
            report.get("owner_decision_required"),
            path + ".report.owner_decision_required",
            errors,
        )
        checks = report.get("checks")
        if not isinstance(checks, list):
            errors.append(path + ".report.checks must be a list")
        else:
            for check_index, check in enumerate(checks):
                check_path = "{}.report.checks[{}]".format(path, check_index)
                if not isinstance(check, dict):
                    errors.append(check_path + " must be an object")
                    continue
                require_string(check.get("name"), check_path + ".name", errors, allow_empty=False)
                require_string(check.get("result"), check_path + ".result", errors, allow_empty=False)

    for task_id, report_id in latest_by_task.items():
        if not isinstance(task_id, str) or not task_id.strip():
            errors.append("task_reports.latest_by_task keys must be non-empty strings")
            continue
        if not isinstance(report_id, str) or not report_id.strip():
            errors.append(
                "task_reports.latest_by_task[{}] must be a non-empty string".format(task_id)
            )
            continue
        report = reports_by_id.get(report_id)
        if report is None:
            errors.append(
                "task_reports.latest_by_task[{}] references missing report: {}".format(
                    task_id,
                    report_id,
                )
            )
        elif report.get("task_id") != task_id:
            errors.append(
                "task_reports.latest_by_task[{}] points to report for {}".format(
                    task_id,
                    report.get("task_id"),
                )
            )

    return errors


def validate_optional_task_reports(root, tasks_state):
    path = task_reports_path(root)
    if not path.exists():
        return []
    report_state = read_json(path, "TASK_REPORTS_NOT_INITIALIZED")
    return validate_task_reports(report_state, tasks_state)


def require_valid_tasks(state, plan=None, check_plan=True):
    errors = validate_tasks(state, plan=plan, check_plan=check_plan)

    if errors:
        raise TaskError("VALIDATION_FAILED:\n- " + "\n- ".join(errors))


def ensure_task_status_transition(current, new):
    if new not in TASK_STATUSES:
        raise TaskError("INVALID_STATUS: {}".format(new))

    if current == new:
        return

    if new not in TASK_STATUS_TRANSITIONS.get(current, set()):
        raise TaskError("INVALID_STATUS_TRANSITION: {} -> {}".format(current, new))


def ensure_task_mutable(task):
    if task.get("status") == "archived":
        raise TaskError("ARCHIVED_ENTITY_IS_IMMUTABLE")

    if task.get("status") == "done":
        raise TaskError("DONE_TASK_IS_IMMUTABLE: archive it or create a follow-up task")


def ensure_epic_can_accept_task(plan, epic_id, new_task_status):
    epic = find_plan_epic(plan, epic_id)

    if epic is None:
        raise TaskError("EPIC_NOT_FOUND: {}".format(epic_id))

    if epic.get("status") in PLAN_TERMINAL_OR_INACTIVE and new_task_status not in TASK_TERMINAL_OR_INACTIVE:
        raise TaskError(
            "CANNOT_USE_INACTIVE_EPIC: {} status is {}".format(
                epic_id,
                epic.get("status"),
            )
        )

    initiative = find_plan_initiative(plan, epic.get("initiative_id"))

    if initiative and initiative.get("status") == "archived" and new_task_status not in TASK_TERMINAL_OR_INACTIVE:
        raise TaskError(
            "CANNOT_USE_EPIC_UNDER_ARCHIVED_INITIATIVE: {} -> {}".format(
                epic_id,
                initiative.get("id"),
            )
        )


def sort_tasks(tasks):
    return sorted(
        tasks,
        key=lambda x: (x.get("epic_id", ""), x.get("order", 0), x.get("id", "")),
    )


def markdown_list(lines, items, empty_text):
    if not items:
        lines.append(empty_text)
        lines.append("")
        return

    for item in items:
        lines.append("- {}".format(item))

    lines.append("")


def render_tasks_markdown(state):
    lines = []

    lines.append("<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->")
    lines.append("<!-- Source: AI_PROJECT/state/tasks.json -->")
    lines.append("")
    lines.append("# Project Tasks")
    lines.append("")
    lines.append("Revision: `{}`".format(state.get("revision", 0)))
    lines.append("Current task: `{}`".format(state.get("current_task_id") or "none"))
    lines.append("")

    tasks = sort_tasks(state.get("tasks", []))

    if not tasks:
        lines.append("_No tasks defined._")
        lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    grouped = {}

    for task in tasks:
        grouped.setdefault(task.get("epic_id", "NO-EPIC"), []).append(task)

    for epic_id in sorted(grouped):
        lines.append("## Epic `{}`".format(epic_id))
        lines.append("")

        for task in grouped[epic_id]:
            marker = " ⭐" if task.get("id") == state.get("current_task_id") else ""
            lines.append("### {} — {}{}".format(task_display_label(task), task.get("title"), marker))
            lines.append("")
            lines.append("Status: `{}`".format(task.get("status")))
            lines.append("Priority: `{}`".format(task.get("priority")))
            lines.append("Verification: `{}`".format(task.get("verification_mode")))

            identity = []

            if task.get("uid"):
                identity.append("uid `{}`".format(task.get("uid")))

            if task.get("legacy_id"):
                identity.append("legacy `{}`".format(task.get("legacy_id")))

            if task.get("aliases"):
                identity.append("aliases `{}`".format("`, `".join(task.get("aliases", []))))

            if task.get("epic_key") and task.get("local_seq"):
                identity.append("local `{}` / `{}`".format(task.get("epic_key"), task.get("local_seq")))

            if identity:
                lines.append("Identity: {}".format(", ".join(identity)))

            if task.get("summary"):
                lines.append("")
                lines.append(task.get("summary"))

            if task.get("acceptance_criteria"):
                lines.append("")
                lines.append("Acceptance criteria:")
                lines.append("")

                for item in task.get("acceptance_criteria", []):
                    lines.append("- {}".format(item))

            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_current_markdown(state):
    lines = []

    lines.append("<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->")
    lines.append("<!-- Source: AI_PROJECT/state/tasks.json -->")
    lines.append("")
    lines.append("# Current Codex Task")
    lines.append("")
    lines.append("Revision: `{}`".format(state.get("revision", 0)))
    lines.append("")

    current_task_id = state.get("current_task_id")

    if not current_task_id:
        lines.append("_No current task selected._")
        lines.append("")
        lines.append("Set current task:")
        lines.append("")
        lines.append("```bash")
        lines.append("python scripts/taskctl.py current set TASK-001")
        lines.append("```")
        lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    task = find_item(state.get("tasks", []), current_task_id)

    lines.append("Task: `{}` — **{}**".format(task_display_label(task), task.get("title")))
    lines.append("Epic: `{}`".format(task.get("epic_id")))
    lines.append("Status: `{}`".format(task.get("status")))
    lines.append("Verification: `{}`".format(task.get("verification_mode")))

    if task.get("ref"):
        lines.append("Ref: `{}`".format(task.get("ref")))

    if task.get("uid"):
        lines.append("UID: `{}`".format(task.get("uid")))

    if task.get("legacy_id"):
        lines.append("Legacy ID: `{}`".format(task.get("legacy_id")))

    if task.get("aliases"):
        lines.append("Aliases: `{}`".format("`, `".join(task.get("aliases", []))))

    if task.get("epic_key") and task.get("local_seq"):
        lines.append("Epic Key / Local Seq: `{}` / `{}`".format(task.get("epic_key"), task.get("local_seq")))

    lines.append("")

    lines.append("## Prompt Control Fields")
    lines.append("")
    lines.append("Active Role: `{}`".format(task.get("active_role") or "Codex Executor"))
    lines.append("Active Stage: `{}`".format(task.get("active_stage") or "Task Execution"))
    lines.append("Active Document: `{}`".format(task.get("active_document") or "AI_PROJECT/generated/CODEX_CURRENT.md"))
    lines.append("Expected Result: `{}`".format(task.get("expected_result") or "Task completed according to acceptance criteria"))
    lines.append("")

    if task.get("summary"):
        lines.append("## Summary")
        lines.append("")
        lines.append(task.get("summary"))
        lines.append("")

    if task.get("description"):
        lines.append("## Description")
        lines.append("")
        lines.append(task.get("description"))
        lines.append("")

    lines.append("## Scope")
    lines.append("")
    markdown_list(lines, task.get("scope", []), "_No scope defined._")

    lines.append("## Out of Scope")
    lines.append("")
    markdown_list(lines, task.get("out_of_scope", []), "_No out-of-scope items defined._")

    lines.append("## Allowed Files")
    lines.append("")
    markdown_list(lines, task.get("allowed_files", []), "_No allowed files defined._")

    lines.append("## Acceptance Criteria")
    lines.append("")
    markdown_list(lines, task.get("acceptance_criteria", []), "_No acceptance criteria defined._")

    if task.get("review_instructions"):
        lines.append("## Review Instructions")
        lines.append("")
        markdown_list(lines, task.get("review_instructions", []), "")

    if task.get("notes"):
        lines.append("## Notes")
        lines.append("")
        markdown_list(lines, task.get("notes", []), "")

    lines.append("## Useful CLI")
    lines.append("")
    lines.append("```bash")
    lines.append("python scripts/taskctl.py task transition {} --to in_progress".format(task.get("id")))
    lines.append("python scripts/taskctl.py task transition {} --to in_review".format(task.get("id")))
    lines.append("python scripts/taskctl.py task approve {} --notes \"...\"".format(task.get("id")))
    lines.append("python scripts/taskctl.py task transition {} --to done".format(task.get("id")))
    lines.append("python scripts/{} task report submit --task {} --file /path/to/report.json --confirm".format(aictl_script_name(), task.get("id")))
    lines.append("python scripts/taskctl.py prompt build --write")
    lines.append("```")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def queue_entry_label(entry):
    if entry.get("ref"):
        return "{} ({})".format(entry.get("ref"), entry.get("id"))

    return entry.get("id") or "-"


def append_queue_entries(lines, entries, empty_text, include_reasons=False):
    if not entries:
        lines.append(empty_text)
        lines.append("")
        return

    for entry in entries:
        lines.append(
            "- `{}` [{}] `{}` priority `{}` — {}".format(
                queue_entry_label(entry),
                entry.get("status"),
                entry.get("epic_id"),
                entry.get("priority"),
                entry.get("title"),
            )
        )

        if include_reasons:
            for reason in entry.get("reasons", []):
                lines.append("  - `{}`: {}".format(reason.get("code"), reason.get("detail")))

    lines.append("")


def render_execution_queue_markdown(state, plan=None):
    entries = build_execution_queue(state, plan=plan)
    executable = [entry for entry in entries if entry.get("executable")]
    waiting = [
        entry
        for entry in entries
        if not entry.get("executable")
        and not queue_entry_has_reason(entry, {"status_not_executable", "parent_epic_not_executable"})
        and queue_entry_has_reason(entry, {"dependency_not_done", "dependency_missing"})
    ]
    not_executable = [
        entry
        for entry in entries
        if not entry.get("executable")
        and queue_entry_has_reason(entry, {"status_not_executable", "parent_epic_not_executable"})
    ]

    lines = []
    lines.append("<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->")
    lines.append("<!-- Source: AI_PROJECT/state/tasks.json -->")
    lines.append("")
    lines.append("# Task Execution Queue")
    lines.append("")
    lines.append("Revision: `{}`".format(state.get("revision", 0)))
    lines.append("")
    lines.append("## Executable Now")
    lines.append("")
    append_queue_entries(lines, executable, "_No executable tasks._")
    lines.append("## Waiting For Dependencies")
    lines.append("")
    append_queue_entries(lines, waiting, "_No tasks waiting only on dependencies._", include_reasons=True)
    lines.append("## Not Executable Due To Status Or Parent State")
    lines.append("")
    append_queue_entries(lines, not_executable, "_No tasks blocked by status or parent state._", include_reasons=True)

    return "\n".join(lines).rstrip() + "\n"


def render_task_outputs(root, state, plan=None, check_plan=True):
    require_valid_tasks(state, plan=plan, check_plan=check_plan)
    atomic_write_text(generated_tasks_path(root), render_tasks_markdown(state))
    atomic_write_text(generated_current_path(root), render_current_markdown(state))
    atomic_write_text(generated_execution_queue_path(root), render_execution_queue_markdown(state, plan=plan))


def build_prompt_text(state, task, plan=None):
    epic = find_plan_epic(plan, task.get("epic_id")) if plan else None
    initiative = find_plan_initiative(plan, epic.get("initiative_id")) if epic else None

    lines = []

    lines.append("[SYSTEM]")
    lines.append("")
    lines.append("Active Role: {}".format(task.get("active_role") or "Codex Executor"))
    lines.append("Active Stage: {}".format(task.get("active_stage") or "Task Execution"))
    lines.append("Active Document: {}".format(task.get("active_document") or "AI_PROJECT/generated/CODEX_CURRENT.md"))
    lines.append("Expected Result: {}".format(task.get("expected_result") or "Task completed according to acceptance criteria"))
    lines.append("")
    lines.append("Repository: current repository")
    lines.append("Task ID: {}".format(task.get("id")))

    if task.get("ref"):
        lines.append("Task Ref: {}".format(task.get("ref")))

    if task.get("uid"):
        lines.append("Task UID: {}".format(task.get("uid")))

    if task.get("legacy_id"):
        lines.append("Legacy Task ID: {}".format(task.get("legacy_id")))

    if task.get("aliases"):
        lines.append("Task Aliases: {}".format(", ".join(task.get("aliases", []))))

    if task.get("epic_key") and task.get("local_seq"):
        lines.append("Task Epic Key / Local Seq: {} / {}".format(task.get("epic_key"), task.get("local_seq")))

    lines.append("Task Title: {}".format(task.get("title")))
    lines.append("Task Status: {}".format(task.get("status")))
    lines.append("Verification Mode: {}".format(task.get("verification_mode")))
    lines.append("")

    if initiative:
        lines.append("Initiative: {} — {}".format(initiative.get("id"), initiative.get("title")))

    if epic:
        lines.append("Epic: {} — {}".format(epic.get("id"), epic.get("title")))
    else:
        lines.append("Epic: {}".format(task.get("epic_id")))

    lines.append("")

    lines.append("Context:")
    lines.append(task.get("summary") or "No summary provided.")
    lines.append("")

    if task.get("description"):
        lines.append("Details:")
        lines.append(task.get("description"))
        lines.append("")

    lines.append("Scope:")
    if task.get("scope"):
        for item in task.get("scope", []):
            lines.append("- {}".format(item))
    else:
        lines.append("- No explicit scope defined. Ask Human Owner before making broad changes.")
    lines.append("")

    lines.append("Out of Scope:")
    if task.get("out_of_scope"):
        for item in task.get("out_of_scope", []):
            lines.append("- {}".format(item))
    else:
        lines.append("- Anything not required by the task and acceptance criteria.")
    lines.append("")

    lines.append("Allowed Files:")
    if task.get("allowed_files"):
        for item in task.get("allowed_files", []):
            lines.append("- {}".format(item))
    else:
        lines.append("- Not specified. Do not edit files until allowed files are clarified.")
    lines.append("")

    lines.append("Acceptance Criteria:")
    if task.get("acceptance_criteria"):
        for item in task.get("acceptance_criteria", []):
            lines.append("- {}".format(item))
    else:
        lines.append("- Task is completed without breaking validation.")
        lines.append("- Generated files are updated only through CLI/render commands.")
    lines.append("")

    if task.get("review_instructions"):
        lines.append("Review Instructions:")
        for item in task.get("review_instructions", []):
            lines.append("- {}".format(item))
        lines.append("")

    lines.append("Execution Rules:")
    lines.append("- Do not edit AI_PROJECT/state/*.json manually.")
    lines.append("- Do not edit AI_PROJECT/events/*.jsonl manually.")
    lines.append("- Do not edit AI_PROJECT/generated/*.md manually unless explicitly instructed; prefer CLI render/build commands.")
    lines.append("- Stay within Allowed Files and Scope.")
    lines.append("- If task state must change, report the required taskctl command instead of editing state by hand.")
    lines.append("- If `python scripts/{} task report submit --task {} --file <REPORT.json> --confirm` exists, submit a structured execution report through it instead of editing report state directly.".format(aictl_script_name(), task.get("id")))
    lines.append("- At the end, report changed files, checks run, result, and any unresolved risks.")
    lines.append("")

    lines.append("Suggested lifecycle commands:")
    lines.append("```bash")
    lines.append("python scripts/taskctl.py task transition {} --to in_progress".format(task.get("id")))
    lines.append("python scripts/taskctl.py task transition {} --to in_review".format(task.get("id")))
    lines.append("python scripts/{} task report submit --task {} --file /path/to/report.json --confirm".format(aictl_script_name(), task.get("id")))
    lines.append("python scripts/taskctl.py validate")
    lines.append("```")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def mutate(args, command, entity_type, entity_id, payload, mutator, check_plan=True, emit=True):
    root = repo_root(args)

    ensure_project_dirs(root)

    state = load_tasks(root)
    plan = load_plan(root, required=check_plan)

    require_valid_tasks(state, plan=plan, check_plan=check_plan)

    revision_before = state.get("revision", 0)

    result = mutator(state, plan) or {}

    state["revision"] = revision_before + 1
    state["updated_at"] = utc_now()

    require_valid_tasks(state, plan=plan, check_plan=check_plan)

    save_tasks(root, state)

    event_entity_id = result.get("entity_id", entity_id)
    event_payload = dict(payload or {})
    event_payload.update(result.get("payload", {}))

    append_event(
        root=root,
        actor=args.actor,
        command=command,
        entity_type=entity_type,
        entity_id=event_entity_id,
        revision_before=revision_before,
        revision_after=state["revision"],
        payload=event_payload,
    )

    render_task_outputs(root, state, plan=plan, check_plan=check_plan)

    if emit:
        print("OK: {} revision {} -> {}".format(command, revision_before, state["revision"]))

    if emit and result.get("message"):
        print(result["message"])

    return {
        "revision_before": revision_before,
        "revision_after": state["revision"],
        "entity_id": event_entity_id,
        "payload": event_payload,
        "result": result,
    }


def print_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def new_task_item(
    task_id,
    epic_id,
    title,
    status,
    summary,
    description,
    priority,
    order,
    active_role,
    active_stage,
    active_document,
    expected_result,
    verification_mode,
    scope,
    out_of_scope,
    allowed_files,
    acceptance_criteria,
    review_instructions,
    notes,
    uid=None,
    ref=None,
    legacy_id=None,
    aliases=None,
    epic_key=None,
    local_seq=None,
):
    now = utc_now()

    task = {
        "id": task_id,
        "epic_id": epic_id,
        "title": title,
        "status": status,
        "summary": summary or "",
        "description": description or "",
        "priority": priority,
        "order": order,
        "active_role": active_role or "Codex Executor",
        "active_stage": active_stage or "Task Execution",
        "active_document": active_document or "AI_PROJECT/generated/CODEX_CURRENT.md",
        "expected_result": expected_result or "Task completed according to acceptance criteria",
        "verification_mode": verification_mode,
        "scope": scope or [],
        "out_of_scope": out_of_scope or [],
        "allowed_files": allowed_files or [],
        "acceptance_criteria": acceptance_criteria or [],
        "review_instructions": review_instructions or [],
        "notes": notes or [],
        "depends_on": [],
        "approved_by": "",
        "approved_at": "",
        "approval_notes": "",
        "created_at": now,
        "updated_at": now,
    }

    if uid:
        task["uid"] = uid

    if ref:
        task["ref"] = ref

    if legacy_id:
        task["legacy_id"] = legacy_id

    if aliases is not None:
        task["aliases"] = aliases

    if epic_key:
        task["epic_key"] = epic_key

    if local_seq is not None:
        task["local_seq"] = local_seq

    return task


def cmd_init(args):
    root = repo_root(args)

    ensure_project_dirs(root)

    path = tasks_path(root)
    events_path = task_events_path(root)

    if path.exists() and not args.force:
        raise TaskError("TASKS_ALREADY_EXISTS: use --force to overwrite")

    if path.exists() and args.force and events_path.exists() and not args.reset_events:
        raise TaskError("TASK_EVENTS_ALREADY_EXIST: use --reset-events with --force to reset audit log")

    if args.force and args.reset_events and events_path.exists():
        backup = events_path.with_name(events_path.name + "." + datetime.now().strftime("%Y%m%d%H%M%S") + ".bak")
        os.replace(str(events_path), str(backup))

    state = default_tasks_state()

    require_valid_tasks(state, plan=None, check_plan=False)
    save_tasks(root, state)

    append_event(
        root=root,
        actor=args.actor,
        command="tasks.init",
        entity_type="tasks",
        entity_id="tasks",
        revision_before=None,
        revision_after=state["revision"],
        payload={"force": bool(args.force), "reset_events": bool(args.reset_events)},
    )

    render_task_outputs(root, state, plan=None, check_plan=False)

    print("OK: initialized {}".format(path))


def cmd_show(args):
    root = repo_root(args)
    state = load_tasks(root)
    plan = load_plan(root, required=False)
    require_valid_tasks(state, plan=plan, check_plan=not args.skip_plan_check)

    if args.json:
        print_json(state)
        return

    print("Tasks revision: {}".format(state.get("revision")))
    print("Current task:   {}".format(state.get("current_task_id") or "—"))
    print("Tasks:          {}".format(len(state.get("tasks", []))))

    counts = {}

    for task in state.get("tasks", []):
        counts[task.get("status")] = counts.get(task.get("status"), 0) + 1

    if counts:
        print("\nBy status:")

        for status in sorted(counts):
            print("  {}: {}".format(status, counts[status]))


def cmd_status(args):
    root = repo_root(args)

    print("Root:       {}".format(root))
    print("Tasks:      {}".format(tasks_path(root)))
    print("Reports:    {}".format(task_reports_path(root)))
    print("Plan:       {}".format(plan_path(root)))
    print("Events:     {}".format(task_events_path(root)))
    print("ReportEvents: {}".format(task_report_events_path(root)))
    print("Generated:  {}".format(generated_tasks_path(root)))
    print("Current:    {}".format(generated_current_path(root)))
    print("Prompt:     {}".format(generated_prompt_path(root)))
    print("Queue:      {}".format(generated_execution_queue_path(root)))

    state = load_tasks(root)
    plan = load_plan(root, required=False)
    errors = validate_tasks(state, plan=plan, check_plan=not args.skip_plan_check)
    errors.extend(validate_optional_task_reports(root, state))

    print("Revision:   {}".format(state.get("revision")))
    print("Current:    {}".format(state.get("current_task_id") or "—"))
    print("Valid:      {}".format("yes" if not errors else "no"))

    if errors:
        for error in errors:
            print("- {}".format(error))


def cmd_validate(args):
    root = repo_root(args)
    state = load_tasks(root)
    plan = load_plan(root, required=False)
    errors = validate_tasks(state, plan=plan, check_plan=not args.skip_plan_check)
    errors.extend(validate_optional_task_reports(root, state))

    if errors:
        print("VALIDATION_FAILED:", file=sys.stderr)

        for error in errors:
            print("- {}".format(error), file=sys.stderr)

        return 1

    print("OK: tasks are valid")
    return 0


def cmd_render(args):
    root = repo_root(args)
    state = load_tasks(root)
    plan = load_plan(root, required=False)

    render_task_outputs(root, state, plan=plan, check_plan=not args.skip_plan_check)

    print(
        "OK: rendered {}, {} and {}".format(
            generated_tasks_path(root),
            generated_current_path(root),
            generated_execution_queue_path(root),
        )
    )


def cmd_check_generated(args):
    root = repo_root(args)
    state = load_tasks(root)
    plan = load_plan(root, required=False)

    require_valid_tasks(state, plan=plan, check_plan=not args.skip_plan_check)

    expected_tasks = render_tasks_markdown(state)
    expected_current = render_current_markdown(state)
    expected_queue = render_execution_queue_markdown(state, plan=plan)

    checks = [
        (generated_tasks_path(root), expected_tasks),
        (generated_current_path(root), expected_current),
        (generated_execution_queue_path(root), expected_queue),
    ]

    failed = []

    for path, expected in checks:
        if not path.exists():
            failed.append("missing generated file: {}".format(path))
            continue

        actual = path.read_text(encoding="utf-8")

        if actual != expected:
            failed.append("outdated generated file: {}".format(path))

    if failed:
        print("GENERATED_CHECK_FAILED:", file=sys.stderr)

        for item in failed:
            print("- {}".format(item), file=sys.stderr)

        return 1

    print("OK: generated task files are up to date")
    return 0


def cmd_migrate_identity(args):
    root = repo_root(args)

    ensure_project_dirs(root)

    state = load_tasks(root)
    plan = load_plan(root, required=True)

    require_valid_tasks(state, plan=plan, check_plan=True)

    proposed = copy.deepcopy(state)
    changes = apply_identity_migration(proposed, plan)

    if args.dry_run:
        result = {
            "migration": "identity",
            "dry_run": True,
            "changed_count": len(changes),
            "changed_tasks": changes,
        }

        if args.json:
            print_json(result)
        else:
            print(identity_migration_report(changes, dry_run=True))
            print("No files changed.")

        return 0

    if not changes:
        revision = state.get("revision", 0)

        render_task_outputs(root, state, plan=plan, check_plan=True)
        append_event(
            root=root,
            actor=args.actor,
            command="migrate.identity",
            entity_type="task_migration",
            entity_id="identity",
            revision_before=revision,
            revision_after=revision,
            payload={
                "changed_count": 0,
                "changed_tasks": [],
                "no_changes": True,
            },
        )

        result = {
            "migration": "identity",
            "dry_run": False,
            "changed_count": 0,
            "changed_tasks": [],
            "revision_before": revision,
            "revision_after": revision,
            "generated_refreshed": True,
        }

        if args.json:
            print_json(result)
        else:
            print("OK: migrate.identity no changes at revision {}".format(revision))
            print(identity_migration_report(changes, dry_run=False))
            print("Generated task outputs refreshed.")

        return 0

    def apply(state, plan):
        applied_changes = apply_identity_migration(state, plan)

        return {
            "entity_id": "identity",
            "payload": {
                "changed_count": len(applied_changes),
                "changed_tasks": applied_changes,
            },
            "message": identity_migration_report(applied_changes, dry_run=False),
        }

    mutation = mutate(
        args=args,
        command="migrate.identity",
        entity_type="task_migration",
        entity_id="identity",
        payload={"migration": "identity"},
        mutator=apply,
        check_plan=True,
        emit=not args.json,
    )

    if args.json:
        result = {
            "migration": "identity",
            "dry_run": False,
            "changed_count": mutation["payload"].get("changed_count", 0),
            "changed_tasks": mutation["payload"].get("changed_tasks", []),
            "revision_before": mutation["revision_before"],
            "revision_after": mutation["revision_after"],
            "generated_refreshed": True,
        }
        print_json(result)

    return 0


def cmd_audit(args):
    path = task_events_path(repo_root(args))

    if not path.exists():
        print("No audit events yet.")
        return

    events = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                print("INVALID_EVENT_LINE: {}".format(line.rstrip()), file=sys.stderr)
                continue

            if args.entity and event.get("entity_id") != args.entity:
                continue

            events.append(event)

    if args.last is not None:
        events = events[-args.last:]

    for event in events:
        print(
            "{timestamp} {event_id} {actor} {command} "
            "{entity_type}:{entity_id} rev {revision_before}->{revision_after}".format(
                **event
            )
        )


def cmd_task_list(args):
    root = repo_root(args)
    state = load_tasks(root)
    plan = load_plan(root, required=False)
    require_valid_tasks(state, plan=plan, check_plan=not args.skip_plan_check)

    tasks = state.get("tasks", [])

    if args.epic:
        tasks = [t for t in tasks if t.get("epic_id") == args.epic]

    if args.status:
        tasks = [t for t in tasks if t.get("status") == args.status]

    if args.current:
        tasks = [t for t in tasks if t.get("id") == state.get("current_task_id")]

    tasks = sort_tasks(tasks)

    if args.json:
        print_json(tasks)
        return

    if not tasks:
        print("No tasks.")
        return

    for task in tasks:
        marker = " *current*" if task.get("id") == state.get("current_task_id") else ""
        print(
            "{} [{}] {} -> {}{}".format(
                task_display_label(task),
                task.get("status"),
                task_epic_label(task, plan=plan),
                task.get("title"),
                marker,
            )
        )


def cmd_task_show(args):
    state = load_tasks(repo_root(args))
    task = resolve_task_ref(state.get("tasks", []), args.task_ref)
    print_json(task)


def cmd_task_resolve(args):
    state = load_tasks(repo_root(args))
    task = resolve_task_ref(state.get("tasks", []), args.task_ref)

    if args.json:
        print_json(
            {
                "id": task.get("id"),
                "ref": task.get("ref"),
                "uid": task.get("uid"),
                "legacy_id": task.get("legacy_id"),
                "aliases": task.get("aliases", []),
                "epic_id": task.get("epic_id"),
                "title": task.get("title"),
                "status": task.get("status"),
            }
        )
        return

    print("Canonical ID: {}".format(task.get("id")))
    print("Ref:          {}".format(task.get("ref") or "-"))
    print("UID:          {}".format(task.get("uid") or "-"))
    print("Legacy ID:    {}".format(task.get("legacy_id") or "-"))
    print("Aliases:      {}".format(", ".join(task.get("aliases", [])) if task.get("aliases") else "-"))
    print("Epic Key:     {}".format(task.get("epic_key") or "-"))
    print("Local Seq:    {}".format(task.get("local_seq") or "-"))
    print("Epic:         {}".format(task.get("epic_id")))
    print("Title:        {}".format(task.get("title")))
    print("Status:       {}".format(task.get("status")))


def cmd_task_create(args):
    def apply(state, plan):
        ensure_epic_can_accept_task(plan, args.epic, args.status)

        task_id = next_id("TASK", state["tasks"])
        epic = find_plan_epic(plan, args.epic)
        epic_key = epic.get("key") if epic else None
        local_seq = None
        ref = None

        if epic_key:
            local_seq = allocate_local_seq(state["tasks"], args.epic, epic_key)
            ref = format_task_ref(epic_key, local_seq)

        task = new_task_item(
            task_id=task_id,
            epic_id=args.epic,
            title=args.title,
            status=args.status,
            summary=args.summary,
            description=args.description,
            priority=args.priority,
            order=next_order(state["tasks"], "epic_id", args.epic),
            active_role=args.active_role,
            active_stage=args.active_stage,
            active_document=args.active_document,
            expected_result=args.expected_result,
            verification_mode=args.verification_mode,
            scope=args.scope,
            out_of_scope=args.out_of_scope,
            allowed_files=args.allowed_file,
            acceptance_criteria=args.acceptance,
            review_instructions=args.review_instruction,
            notes=args.note,
            uid=generate_task_uid(state["tasks"]),
            ref=ref,
            legacy_id=task_id,
            aliases=[task_id],
            epic_key=epic_key,
            local_seq=local_seq,
        )

        state["tasks"].append(task)

        payload = {"task_id": task_id}

        if ref:
            payload["ref"] = ref

        return {
            "entity_id": task_id,
            "payload": payload,
            "message": "Created: {}".format(task_display_label(task)),
        }

    mutate(
        args=args,
        command="task.create",
        entity_type="task",
        entity_id="NEW",
        payload={
            "epic_id": args.epic,
            "title": args.title,
            "status": args.status,
            "priority": args.priority,
        },
        mutator=apply,
    )


def cmd_task_rename(args):
    def apply(state, plan):
        task = resolve_task_ref(state["tasks"], args.task_ref)
        ensure_task_mutable(task)

        task["title"] = args.title
        task["updated_at"] = utc_now()
        return {"entity_id": task.get("id")}

    mutate(
        args=args,
        command="task.rename",
        entity_type="task",
        entity_id=args.task_ref,
        payload={"title": args.title},
        mutator=apply,
    )


def cmd_task_update_summary(args):
    def apply(state, plan):
        task = resolve_task_ref(state["tasks"], args.task_ref)
        ensure_task_mutable(task)

        task["summary"] = args.text
        task["updated_at"] = utc_now()
        return {"entity_id": task.get("id")}

    mutate(
        args=args,
        command="task.update_summary",
        entity_type="task",
        entity_id=args.task_ref,
        payload={"summary": args.text},
        mutator=apply,
    )


def cmd_task_update_description(args):
    def apply(state, plan):
        task = resolve_task_ref(state["tasks"], args.task_ref)
        ensure_task_mutable(task)

        task["description"] = args.text
        task["updated_at"] = utc_now()
        return {"entity_id": task.get("id")}

    mutate(
        args=args,
        command="task.update_description",
        entity_type="task",
        entity_id=args.task_ref,
        payload={"description": args.text},
        mutator=apply,
    )


def cmd_task_set_prompt_fields(args):
    def apply(state, plan):
        task = resolve_task_ref(state["tasks"], args.task_ref)
        ensure_task_mutable(task)

        changed = {}

        for attr in ["active_role", "active_stage", "active_document", "expected_result", "verification_mode"]:
            value = getattr(args, attr)

            if value is not None:
                if attr == "verification_mode" and value not in VERIFICATION_MODES:
                    raise TaskError("INVALID_VERIFICATION_MODE: {}".format(value))

                task[attr] = value
                changed[attr] = value

        if not changed:
            raise TaskError("NO_FIELDS_TO_UPDATE")

        task["updated_at"] = utc_now()
        return {"entity_id": task.get("id"), "payload": {"changed": changed}}

    mutate(
        args=args,
        command="task.set_prompt_fields",
        entity_type="task",
        entity_id=args.task_ref,
        payload={},
        mutator=apply,
    )


def cmd_task_transition(args):
    def apply(state, plan):
        task = resolve_task_ref(state["tasks"], args.task_ref)
        task_id = task.get("id")
        old = task.get("status")

        ensure_task_status_transition(old, args.to)
        ensure_epic_can_accept_task(plan, task.get("epic_id"), args.to)

        if args.to == "approved":
            raise TaskError("USE_TASK_APPROVE_COMMAND_FOR_APPROVAL")

        if args.to == "in_progress":
            ensure_task_dependencies_satisfied(state, task)

        task["status"] = args.to
        task["updated_at"] = utc_now()

        if args.to != "approved":
            task["approved_by"] = "" if args.to not in {"done", "archived"} else task.get("approved_by", "")
            task["approved_at"] = "" if args.to not in {"done", "archived"} else task.get("approved_at", "")
            task["approval_notes"] = "" if args.to not in {"done", "archived"} else task.get("approval_notes", "")

        if state.get("current_task_id") == task_id and args.to not in CURRENT_ALLOWED_STATUSES:
            state["current_task_id"] = None

        return {"entity_id": task_id}

    mutate(
        args=args,
        command="task.transition",
        entity_type="task",
        entity_id=args.task_ref,
        payload={"to": args.to},
        mutator=apply,
    )


def cmd_task_approve(args):
    def apply(state, plan):
        task = resolve_task_ref(state["tasks"], args.task_ref)
        task_id = task.get("id")

        ensure_task_status_transition(task.get("status"), "approved")
        ensure_epic_can_accept_task(plan, task.get("epic_id"), "approved")

        task["status"] = "approved"
        task["approved_by"] = args.by or args.actor
        task["approved_at"] = utc_now()
        task["approval_notes"] = args.notes or ""
        task["updated_at"] = utc_now()

        if state.get("current_task_id") == task_id:
            state["current_task_id"] = None

        return {"entity_id": task_id, "payload": {"by": task["approved_by"], "notes": args.notes or ""}}

    mutate(
        args=args,
        command="task.approve",
        entity_type="task",
        entity_id=args.task_ref,
        payload={},
        mutator=apply,
    )


def cmd_task_archive(args):
    args.to = "archived"
    cmd_task_transition(args)


def task_add_list_item(args, field, command):
    def apply(state, plan):
        task = resolve_task_ref(state["tasks"], args.task_ref)
        ensure_task_mutable(task)

        task.setdefault(field, []).append(args.text)
        task["updated_at"] = utc_now()
        return {"entity_id": task.get("id")}

    mutate(
        args=args,
        command=command,
        entity_type="task",
        entity_id=args.task_ref,
        payload={"field": field, "text": args.text},
        mutator=apply,
    )


def task_remove_list_item(args, field, command):
    def apply(state, plan):
        task = resolve_task_ref(state["tasks"], args.task_ref)
        ensure_task_mutable(task)

        items = task.setdefault(field, [])
        index = args.index - 1

        if index < 0 or index >= len(items):
            raise TaskError("INDEX_OUT_OF_RANGE")

        removed = items.pop(index)
        task["updated_at"] = utc_now()

        return {
            "entity_id": task.get("id"),
            "payload": {"field": field, "index": args.index, "removed": removed},
        }

    mutate(
        args=args,
        command=command,
        entity_type="task",
        entity_id=args.task_ref,
        payload={},
        mutator=apply,
    )


def cmd_task_deps_list(args):
    root = repo_root(args)
    state = load_tasks(root)
    plan = load_plan(root, required=False)
    require_valid_tasks(state, plan=plan, check_plan=not args.skip_plan_check)

    task = resolve_task_ref(state.get("tasks", []), args.task_ref)
    deps = task_dependency_list(task)
    tasks_by_id = task_id_map(state.get("tasks", []))

    if args.json:
        items = []

        for dep in deps:
            dep_task = tasks_by_id.get(dep.get("task_id")) if isinstance(dep, dict) else None
            item = dict(dep) if isinstance(dep, dict) else {"invalid": dep}

            if dep_task:
                item["resolved"] = {
                    "id": dep_task.get("id"),
                    "ref": dep_task.get("ref"),
                    "title": dep_task.get("title"),
                    "status": dep_task.get("status"),
                }

            items.append(item)

        print_json(items)
        return

    if not deps:
        print("No dependencies.")
        return

    for dep in deps:
        dep_task = tasks_by_id.get(dep.get("task_id")) if isinstance(dep, dict) else None
        label = task_display_label(dep_task) if dep_task else dep.get("task_id")
        status = dep_task.get("status") if dep_task else "missing"
        reason = dep.get("reason", "") if isinstance(dep, dict) else ""
        suffix = " — {}".format(reason) if reason else ""
        print("{} [{}] type={}{}".format(label, status, dep.get("type"), suffix))


def cmd_task_deps_add(args):
    def apply(state, plan):
        task = resolve_task_ref(state["tasks"], args.task_ref)
        dep_task = resolve_task_ref(state["tasks"], args.after)
        ensure_task_mutable(task)

        task_id = task.get("id")
        dep_task_id = dep_task.get("id")

        if task_id == dep_task_id:
            raise TaskError("TASK_DEPENDENCY_SELF: {}".format(task_display_label(task)))

        deps = task.setdefault("depends_on", [])

        if not isinstance(deps, list):
            raise TaskError("INVALID_DEPENDENCIES: depends_on must be a list")

        for dep in deps:
            if isinstance(dep, dict) and dep.get("task_id") == dep_task_id:
                raise TaskError("DUPLICATE_TASK_DEPENDENCY: {} after {}".format(task_display_label(task), dep_task_id))

        dependency = {
            "task_id": dep_task_id,
            "type": args.type,
            "created_at": utc_now(),
        }

        if args.reason:
            dependency["reason"] = args.reason

        deps.append(dependency)
        task["updated_at"] = utc_now()

        return {
            "entity_id": task_id,
            "payload": {
                "after": dep_task_id,
                "type": args.type,
                "reason": args.reason or "",
            },
        }

    mutate(
        args=args,
        command="task.deps.add",
        entity_type="task",
        entity_id=args.task_ref,
        payload={},
        mutator=apply,
    )


def cmd_task_deps_remove(args):
    def apply(state, plan):
        task = resolve_task_ref(state["tasks"], args.task_ref)
        dep_task = resolve_task_ref(state["tasks"], args.after)
        ensure_task_mutable(task)

        dep_task_id = dep_task.get("id")
        deps = task.setdefault("depends_on", [])

        if not isinstance(deps, list):
            raise TaskError("INVALID_DEPENDENCIES: depends_on must be a list")

        for index, dep in enumerate(deps):
            if isinstance(dep, dict) and dep.get("task_id") == dep_task_id:
                removed = deps.pop(index)
                task["updated_at"] = utc_now()
                return {
                    "entity_id": task.get("id"),
                    "payload": {"after": dep_task_id, "removed": removed},
                }

        raise TaskError("TASK_DEPENDENCY_NOT_FOUND: {} after {}".format(task_display_label(task), dep_task_id))

    mutate(
        args=args,
        command="task.deps.remove",
        entity_type="task",
        entity_id=args.task_ref,
        payload={},
        mutator=apply,
    )


def cmd_task_graph_validate(args):
    root = repo_root(args)
    state = load_tasks(root)
    plan = load_plan(root, required=False)
    errors = validate_tasks(state, plan=plan, check_plan=not args.skip_plan_check)

    if errors:
        print("VALIDATION_FAILED:", file=sys.stderr)

        for error in errors:
            print("- {}".format(error), file=sys.stderr)

        return 1

    print("OK: task dependency graph is valid")
    return 0


def cmd_task_report_submit(args):
    if not args.confirm:
        raise TaskError("REPORT_SUBMIT_CONFIRMATION_REQUIRED: rerun with --confirm")

    root = repo_root(args)
    state = load_tasks(root)
    plan = load_plan(root, required=False)
    require_valid_tasks(state, plan=plan, check_plan=not args.skip_plan_check)

    task = resolve_task_ref(state.get("tasks", []), args.task)
    report_payload = read_report_payload(args.file)
    normalized_report = normalize_task_report_payload(report_payload, task)

    report_state = load_task_reports(root, required=False)
    existing_errors = validate_task_reports(report_state, state)
    if existing_errors:
        raise TaskError("TASK_REPORTS_VALIDATION_FAILED:\n- " + "\n- ".join(existing_errors))

    revision_before = report_state.get("revision", 0)
    revision_after = revision_before + 1
    report_id = next_report_id(report_state.get("reports", []))
    submitted_at = utc_now()
    source_file = str(Path(args.file).resolve())
    task_id = task.get("id")
    record = {
        "id": report_id,
        "task_id": task_id,
        "task_ref": task.get("ref") or "",
        "submitted_at": submitted_at,
        "submitted_by": args.actor,
        "source_file": source_file,
        "report": normalized_report,
    }

    proposed = copy.deepcopy(report_state)
    proposed["revision"] = revision_after
    proposed["updated_at"] = submitted_at
    proposed.setdefault("reports", []).append(record)
    proposed.setdefault("latest_by_task", {})[task_id] = report_id

    proposed_errors = validate_task_reports(proposed, state)
    if proposed_errors:
        raise TaskError("TASK_REPORTS_VALIDATION_FAILED:\n- " + "\n- ".join(proposed_errors))

    ensure_project_dirs(root)
    save_task_reports(root, proposed)
    append_report_event(
        root=root,
        actor=args.actor,
        command="task.report.submit",
        entity_type="task_report",
        entity_id=report_id,
        revision_before=revision_before,
        revision_after=revision_after,
        payload={
            "task_id": task_id,
            "task_ref": task.get("ref") or "",
            "report_id": report_id,
            "source_file": source_file,
            "owner_decision_required": normalized_report.get("owner_decision_required"),
        },
    )

    result = {
        "report_id": report_id,
        "task_id": task_id,
        "task_ref": task.get("ref") or "",
        "revision_before": revision_before,
        "revision_after": revision_after,
        "owner_decision_required": normalized_report.get("owner_decision_required"),
        "state_path": str(task_reports_path(root)),
        "event_path": str(task_report_events_path(root)),
    }

    if args.json:
        print_json(result)
        return 0

    print(
        "OK: task.report.submit revision {} -> {}".format(
            revision_before,
            revision_after,
        )
    )
    print("Report: {} for {}".format(report_id, task_display_label(task)))
    if normalized_report.get("owner_decision_required"):
        print("Owner decision required: yes")
    return 0


def cmd_task_executable(args):
    root = repo_root(args)
    state = load_tasks(root)
    plan = load_plan(root, required=False)
    require_valid_tasks(state, plan=plan, check_plan=not args.skip_plan_check)

    entries = [entry for entry in build_execution_queue(state, plan=plan) if entry.get("executable")]

    if args.json:
        print_json(entries)
        return

    if not entries:
        print("No executable tasks.")
        return

    for entry in entries:
        print(
            "{} [{}] {} -> {}".format(
                queue_entry_label(entry),
                entry.get("status"),
                entry.get("epic_id"),
                entry.get("title"),
            )
        )


def cmd_task_next(args):
    root = repo_root(args)
    state = load_tasks(root)
    plan = load_plan(root, required=False)
    require_valid_tasks(state, plan=plan, check_plan=not args.skip_plan_check)

    entries = [entry for entry in build_execution_queue(state, plan=plan) if entry.get("executable")]
    entry = entries[0] if entries else None

    if args.json:
        print_json(entry or {"task": None, "message": "No executable task."})
        return

    if entry is None:
        print("No executable task.")
        return

    print(
        "{} [{}] {} -> {}".format(
            queue_entry_label(entry),
            entry.get("status"),
            entry.get("epic_id"),
            entry.get("title"),
        )
    )


def cmd_current_show(args):
    state = load_tasks(repo_root(args))
    current_task_id = state.get("current_task_id")

    if not current_task_id:
        print("No current task.")
        return

    task = find_item(state.get("tasks", []), current_task_id)

    if args.json:
        print_json(task)
        return

    plan = load_plan(repo_root(args), required=False)
    print(
        "{} [{}] {} -> {}".format(
            task_display_label(task),
            task.get("status"),
            task_epic_label(task, plan=plan),
            task.get("title"),
        )
    )


def cmd_current_set(args):
    def apply(state, plan):
        task = resolve_task_ref(state["tasks"], args.task_ref)
        task_id = task.get("id")

        if task.get("status") not in CURRENT_ALLOWED_STATUSES:
            raise TaskError(
                "TASK_CANNOT_BE_CURRENT: {} status is {}".format(
                    task_id,
                    task.get("status"),
                )
            )

        ensure_epic_can_accept_task(plan, task.get("epic_id"), task.get("status"))

        if task.get("status") in EXECUTABLE_CANDIDATE_STATUSES:
            ensure_task_dependencies_satisfied(state, task)

        previous = state.get("current_task_id")
        state["current_task_id"] = task_id

        return {"entity_id": task_id, "payload": {"previous": previous, "current": task_id}}

    mutate(
        args=args,
        command="current.set",
        entity_type="current_task",
        entity_id=args.task_ref,
        payload={},
        mutator=apply,
    )


def cmd_current_clear(args):
    def apply(state, plan):
        previous = state.get("current_task_id")
        state["current_task_id"] = None

        return {"payload": {"previous": previous}}

    mutate(
        args=args,
        command="current.clear",
        entity_type="current_task",
        entity_id=load_tasks(repo_root(args)).get("current_task_id") or "none",
        payload={},
        mutator=apply,
    )


def cmd_prompt_build(args):
    root = repo_root(args)
    state = load_tasks(root)
    plan = load_plan(root, required=False)

    require_valid_tasks(state, plan=plan, check_plan=not args.skip_plan_check)

    task_ref = args.task or state.get("current_task_id")

    if not task_ref:
        raise TaskError("NO_TASK_SELECTED: use --task TASK-001 or `current set TASK-001`")

    task = resolve_task_ref(state.get("tasks", []), task_ref)
    task_id = task.get("id")

    if not args.allow_inactive and task.get("status") not in CURRENT_ALLOWED_STATUSES:
        raise TaskError("TASK_IS_NOT_EXECUTABLE: {} status is {}".format(task_id, task.get("status")))

    if not args.allow_inactive and task.get("status") in EXECUTABLE_CANDIDATE_STATUSES:
        ensure_task_dependencies_satisfied(state, task)

    text = build_prompt_text(state, task, plan=plan)

    if args.write or args.out:
        out_path = Path(args.out).resolve() if args.out else generated_prompt_path(root)
        atomic_write_text(out_path, text)

        append_event(
            root=root,
            actor=args.actor,
            command="prompt.build",
            entity_type="task",
            entity_id=task_id,
            revision_before=state.get("revision"),
            revision_after=state.get("revision"),
            payload={"out": str(out_path)},
        )

        print("OK: prompt written {}".format(out_path))
        return

    print(text)


def add_common_args(parser):
    parser.add_argument(
        "--root",
        default=".",
        help="Repository/project root. Default: current directory.",
    )

    parser.add_argument(
        "--actor",
        default=os.environ.get("AI_DEV_ACTOR", "human_owner"),
        help="Audit actor. Default: AI_DEV_ACTOR or human_owner.",
    )


def add_skip_plan_check(parser):
    parser.add_argument(
        "--skip-plan-check",
        action="store_true",
        help="Validate tasks without checking references to AI_PROJECT/state/plan.json.",
    )


def add_list_mutation_commands(task_sub, add_name, remove_name, field, add_command, remove_command, add_help):
    p = task_sub.add_parser(add_name, help=add_help)
    p.add_argument("task_ref")
    p.add_argument("--text", required=True)
    p.set_defaults(func=lambda a, f=field, c=add_command: task_add_list_item(a, f, c))

    p = task_sub.add_parser(remove_name, help="Remove item from {}".format(field))
    p.add_argument("task_ref")
    p.add_argument("--index", type=int, required=True)
    p.set_defaults(func=lambda a, f=field, c=remove_command: task_remove_list_item(a, f, c))


def build_parser():
    parser = argparse.ArgumentParser(
        description="Strict tasks.json control CLI for AI Development System"
    )

    add_common_args(parser)

    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="Initialize AI_PROJECT/state/tasks.json")
    p.add_argument("--force", action="store_true", help="Overwrite existing tasks.json")
    p.add_argument("--reset-events", action="store_true", help="Backup and reset existing task event log when using --force")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("show", help="Show task state summary")
    p.add_argument("--json", action="store_true")
    add_skip_plan_check(p)
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("status", help="Show file paths and validation status")
    add_skip_plan_check(p)
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("validate", help="Validate tasks.json and plan references")
    add_skip_plan_check(p)
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("render", help="Render generated task markdown files")
    add_skip_plan_check(p)
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("check-generated", help="Check generated task markdown is up to date")
    add_skip_plan_check(p)
    p.set_defaults(func=cmd_check_generated)

    p = sub.add_parser("audit", help="Show task audit events")
    p.add_argument("--last", type=int, default=20)
    p.add_argument("--entity", help="Filter by entity id")
    p.set_defaults(func=cmd_audit)

    migrate = sub.add_parser("migrate", help="Run task state migrations")
    migrate_sub = migrate.add_subparsers(dest="migrate_command", required=True)

    p = migrate_sub.add_parser("identity", help="Backfill task uid/ref/legacy identity fields")
    p.add_argument("--dry-run", action="store_true", help="Preview identity changes without writing files")
    p.add_argument("--json", action="store_true", help="Print machine-readable migration output")
    p.set_defaults(func=cmd_migrate_identity)

    task = sub.add_parser("task", help="Manage executable tasks")
    task_sub = task.add_subparsers(dest="task_command", required=True)

    p = task_sub.add_parser("list")
    p.add_argument("--epic")
    p.add_argument("--status", choices=sorted(TASK_STATUSES))
    p.add_argument("--current", action="store_true")
    p.add_argument("--json", action="store_true")
    add_skip_plan_check(p)
    p.set_defaults(func=cmd_task_list)

    p = task_sub.add_parser("show")
    p.add_argument("task_ref")
    p.set_defaults(func=cmd_task_show)

    p = task_sub.add_parser("resolve")
    p.add_argument("task_ref")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_task_resolve)

    deps = task_sub.add_parser("deps")
    deps_sub = deps.add_subparsers(dest="deps_command", required=True)

    p = deps_sub.add_parser("list")
    p.add_argument("task_ref")
    p.add_argument("--json", action="store_true")
    add_skip_plan_check(p)
    p.set_defaults(func=cmd_task_deps_list)

    p = deps_sub.add_parser("add")
    p.add_argument("task_ref")
    p.add_argument("--after", required=True)
    p.add_argument("--type", choices=sorted(DEPENDENCY_TYPES), default="hard")
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_task_deps_add)

    p = deps_sub.add_parser("remove")
    p.add_argument("task_ref")
    p.add_argument("--after", required=True)
    p.set_defaults(func=cmd_task_deps_remove)

    graph = task_sub.add_parser("graph")
    graph_sub = graph.add_subparsers(dest="graph_command", required=True)

    p = graph_sub.add_parser("validate")
    add_skip_plan_check(p)
    p.set_defaults(func=cmd_task_graph_validate)

    report = task_sub.add_parser("report")
    report_sub = report.add_subparsers(dest="report_command", required=True)

    p = report_sub.add_parser("submit")
    p.add_argument("--task", required=True, help="Task ref or id the report belongs to.")
    p.add_argument("--file", required=True, help="Structured JSON execution report file.")
    p.add_argument("--confirm", action="store_true", help="Required explicit confirmation.")
    p.add_argument("--json", action="store_true")
    add_skip_plan_check(p)
    p.set_defaults(func=cmd_task_report_submit)

    p = task_sub.add_parser("executable")
    p.add_argument("--json", action="store_true")
    add_skip_plan_check(p)
    p.set_defaults(func=cmd_task_executable)

    p = task_sub.add_parser("next")
    p.add_argument("--json", action="store_true")
    add_skip_plan_check(p)
    p.set_defaults(func=cmd_task_next)

    p = task_sub.add_parser("create")
    p.add_argument("--epic", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--summary", default="")
    p.add_argument("--description", default="")
    p.add_argument("--priority", type=int, default=1)
    p.add_argument("--status", choices=sorted(TASK_STATUSES), default="planned")
    p.add_argument("--active-role", default="Codex Executor")
    p.add_argument("--active-stage", default="Task Execution")
    p.add_argument("--active-document", default="AI_PROJECT/generated/CODEX_CURRENT.md")
    p.add_argument("--expected-result", default="Task completed according to acceptance criteria")
    p.add_argument("--verification-mode", choices=sorted(VERIFICATION_MODES), default="manual")
    p.add_argument("--scope", action="append", default=[])
    p.add_argument("--out-of-scope", action="append", default=[])
    p.add_argument("--allowed-file", action="append", default=[])
    p.add_argument("--acceptance", action="append", default=[])
    p.add_argument("--review-instruction", action="append", default=[])
    p.add_argument("--note", action="append", default=[])
    p.set_defaults(func=cmd_task_create)

    p = task_sub.add_parser("rename")
    p.add_argument("task_ref")
    p.add_argument("--title", required=True)
    p.set_defaults(func=cmd_task_rename)

    p = task_sub.add_parser("update-summary")
    p.add_argument("task_ref")
    p.add_argument("--text", required=True)
    p.set_defaults(func=cmd_task_update_summary)

    p = task_sub.add_parser("update-description")
    p.add_argument("task_ref")
    p.add_argument("--text", required=True)
    p.set_defaults(func=cmd_task_update_description)

    p = task_sub.add_parser("set-prompt-fields")
    p.add_argument("task_ref")
    p.add_argument("--active-role")
    p.add_argument("--active-stage")
    p.add_argument("--active-document")
    p.add_argument("--expected-result")
    p.add_argument("--verification-mode", choices=sorted(VERIFICATION_MODES))
    p.set_defaults(func=cmd_task_set_prompt_fields)

    p = task_sub.add_parser("transition")
    p.add_argument("task_ref")
    p.add_argument("--to", required=True, choices=sorted(TASK_STATUSES))
    p.set_defaults(func=cmd_task_transition)

    p = task_sub.add_parser("approve")
    p.add_argument("task_ref")
    p.add_argument("--by", default="")
    p.add_argument("--notes", default="")
    p.set_defaults(func=cmd_task_approve)

    p = task_sub.add_parser("archive")
    p.add_argument("task_ref")
    p.set_defaults(func=cmd_task_archive)

    add_list_mutation_commands(
        task_sub,
        "add-scope",
        "remove-scope",
        "scope",
        "task.add_scope",
        "task.remove_scope",
        "Add scope item",
    )
    add_list_mutation_commands(
        task_sub,
        "add-out-of-scope",
        "remove-out-of-scope",
        "out_of_scope",
        "task.add_out_of_scope",
        "task.remove_out_of_scope",
        "Add out-of-scope item",
    )
    add_list_mutation_commands(
        task_sub,
        "add-allowed-file",
        "remove-allowed-file",
        "allowed_files",
        "task.add_allowed_file",
        "task.remove_allowed_file",
        "Add allowed file",
    )
    add_list_mutation_commands(
        task_sub,
        "add-acceptance",
        "remove-acceptance",
        "acceptance_criteria",
        "task.add_acceptance",
        "task.remove_acceptance",
        "Add acceptance criterion",
    )
    add_list_mutation_commands(
        task_sub,
        "add-review-instruction",
        "remove-review-instruction",
        "review_instructions",
        "task.add_review_instruction",
        "task.remove_review_instruction",
        "Add review instruction",
    )
    add_list_mutation_commands(
        task_sub,
        "add-note",
        "remove-note",
        "notes",
        "task.add_note",
        "task.remove_note",
        "Add note",
    )

    current = sub.add_parser("current", help="Manage current executable task")
    current_sub = current.add_subparsers(dest="current_command", required=True)

    p = current_sub.add_parser("show")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_current_show)

    p = current_sub.add_parser("set")
    p.add_argument("task_ref")
    p.set_defaults(func=cmd_current_set)

    p = current_sub.add_parser("clear")
    p.set_defaults(func=cmd_current_clear)

    prompt = sub.add_parser("prompt", help="Build Codex prompt package")
    prompt_sub = prompt.add_subparsers(dest="prompt_command", required=True)

    p = prompt_sub.add_parser("build")
    p.add_argument("--task", help="Task ref or id. Defaults to current_task_id.")
    p.add_argument("--write", action="store_true", help="Write to AI_PROJECT/generated/CODEX_PROMPT.md")
    p.add_argument("--out", help="Write prompt to custom path")
    p.add_argument("--allow-inactive", action="store_true", help="Allow prompt build for non-executable statuses")
    add_skip_plan_check(p)
    p.set_defaults(func=cmd_prompt_build)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = args.func(args)
        return int(result or 0)
    except TaskError as e:
        print("ERROR: {}".format(e), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())

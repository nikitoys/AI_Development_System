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
import json
import os
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path


TASK_SCHEMA_VERSION = 1
PLAN_SCHEMA_VERSION = 1

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

VERIFICATION_MODES = {"none", "manual", "light", "standard", "strict"}

TASK_LIST_FIELDS = {
    "scope": "Scope",
    "out_of_scope": "Out of scope",
    "allowed_files": "Allowed files",
    "acceptance_criteria": "Acceptance criteria",
    "review_instructions": "Review instructions",
    "notes": "Notes",
}


class TaskError(Exception):
    pass


class PlanRefError(Exception):
    pass


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repo_root(args):
    return Path(args.root).resolve()


def state_dir(root):
    return root / "AI_PROJECT" / "state"


def events_dir(root):
    return root / "AI_PROJECT" / "events"


def generated_dir(root):
    return root / "AI_PROJECT" / "generated"


def tasks_path(root):
    return state_dir(root) / "tasks.json"


def task_events_path(root):
    return events_dir(root) / "task-events.jsonl"


def plan_path(root):
    return state_dir(root) / "plan.json"


def generated_tasks_path(root):
    return generated_dir(root) / "CODEX_TASKS.md"


def generated_current_path(root):
    return generated_dir(root) / "CODEX_CURRENT.md"


def generated_prompt_path(root):
    return generated_dir(root) / "CODEX_PROMPT.md"


def ensure_project_dirs(root):
    state_dir(root).mkdir(parents=True, exist_ok=True)
    events_dir(root).mkdir(parents=True, exist_ok=True)
    generated_dir(root).mkdir(parents=True, exist_ok=True)


def atomic_write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_name = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=".tmp",
        dir=str(path.parent),
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())

        os.replace(tmp_name, str(path))
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


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
    event = {
        "event_id": "EVT-" + uuid.uuid4().hex[:12].upper(),
        "timestamp": utc_now(),
        "actor": actor,
        "command": command,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "revision_before": revision_before,
        "revision_after": revision_after,
        "payload": payload,
    }

    line = json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"

    path = task_events_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(line)


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


def find_item(items, item_id, required=True):
    for item in items:
        if item.get("id") == item_id:
            return item

    if required:
        raise TaskError("ENTITY_NOT_FOUND: {}".format(item_id))

    return None


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

        if task.get("status") == "approved":
            if not task.get("approved_by") or not task.get("approved_at"):
                errors.append("{} approved task must have approved_by and approved_at".format(path))

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
            lines.append("### {} — {}{}".format(task.get("id"), task.get("title"), marker))
            lines.append("")
            lines.append("Status: `{}`  ".format(task.get("status")))
            lines.append("Priority: `{}`  ".format(task.get("priority")))
            lines.append("Verification: `{}`  ".format(task.get("verification_mode")))

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

    lines.append("Task: `{}` — **{}**".format(task.get("id"), task.get("title")))
    lines.append("Epic: `{}`".format(task.get("epic_id")))
    lines.append("Status: `{}`".format(task.get("status")))
    lines.append("Verification: `{}`".format(task.get("verification_mode")))
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
    lines.append("python scripts/taskctl.py prompt build --write")
    lines.append("```")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_task_outputs(root, state, plan=None, check_plan=True):
    require_valid_tasks(state, plan=plan, check_plan=check_plan)
    atomic_write_text(generated_tasks_path(root), render_tasks_markdown(state))
    atomic_write_text(generated_current_path(root), render_current_markdown(state))


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
    lines.append("- At the end, report changed files, checks run, result, and any unresolved risks.")
    lines.append("")

    lines.append("Suggested lifecycle commands:")
    lines.append("```bash")
    lines.append("python scripts/taskctl.py task transition {} --to in_progress".format(task.get("id")))
    lines.append("python scripts/taskctl.py task transition {} --to in_review".format(task.get("id")))
    lines.append("python scripts/taskctl.py validate")
    lines.append("```")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def mutate(args, command, entity_type, entity_id, payload, mutator, check_plan=True):
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

    print("OK: {} revision {} -> {}".format(command, revision_before, state["revision"]))

    if result.get("message"):
        print(result["message"])


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
):
    now = utc_now()

    return {
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
        "approved_by": "",
        "approved_at": "",
        "approval_notes": "",
        "created_at": now,
        "updated_at": now,
    }


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
    print("Plan:       {}".format(plan_path(root)))
    print("Events:     {}".format(task_events_path(root)))
    print("Generated:  {}".format(generated_tasks_path(root)))
    print("Current:    {}".format(generated_current_path(root)))
    print("Prompt:     {}".format(generated_prompt_path(root)))

    state = load_tasks(root)
    plan = load_plan(root, required=False)
    errors = validate_tasks(state, plan=plan, check_plan=not args.skip_plan_check)

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

    print("OK: rendered {} and {}".format(generated_tasks_path(root), generated_current_path(root)))


def cmd_check_generated(args):
    root = repo_root(args)
    state = load_tasks(root)
    plan = load_plan(root, required=False)

    require_valid_tasks(state, plan=plan, check_plan=not args.skip_plan_check)

    expected_tasks = render_tasks_markdown(state)
    expected_current = render_current_markdown(state)

    checks = [
        (generated_tasks_path(root), expected_tasks),
        (generated_current_path(root), expected_current),
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
                task.get("id"),
                task.get("status"),
                task.get("epic_id"),
                task.get("title"),
                marker,
            )
        )


def cmd_task_show(args):
    state = load_tasks(repo_root(args))
    task = find_item(state.get("tasks", []), args.task_id)
    print_json(task)


def cmd_task_create(args):
    def apply(state, plan):
        ensure_epic_can_accept_task(plan, args.epic, args.status)

        task_id = next_id("TASK", state["tasks"])

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
        )

        state["tasks"].append(task)

        return {
            "entity_id": task_id,
            "payload": {"task_id": task_id},
            "message": "Created: {}".format(task_id),
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
        task = find_item(state["tasks"], args.task_id)
        ensure_task_mutable(task)

        task["title"] = args.title
        task["updated_at"] = utc_now()

    mutate(
        args=args,
        command="task.rename",
        entity_type="task",
        entity_id=args.task_id,
        payload={"title": args.title},
        mutator=apply,
    )


def cmd_task_update_summary(args):
    def apply(state, plan):
        task = find_item(state["tasks"], args.task_id)
        ensure_task_mutable(task)

        task["summary"] = args.text
        task["updated_at"] = utc_now()

    mutate(
        args=args,
        command="task.update_summary",
        entity_type="task",
        entity_id=args.task_id,
        payload={"summary": args.text},
        mutator=apply,
    )


def cmd_task_update_description(args):
    def apply(state, plan):
        task = find_item(state["tasks"], args.task_id)
        ensure_task_mutable(task)

        task["description"] = args.text
        task["updated_at"] = utc_now()

    mutate(
        args=args,
        command="task.update_description",
        entity_type="task",
        entity_id=args.task_id,
        payload={"description": args.text},
        mutator=apply,
    )


def cmd_task_set_prompt_fields(args):
    def apply(state, plan):
        task = find_item(state["tasks"], args.task_id)
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
        return {"payload": {"changed": changed}}

    mutate(
        args=args,
        command="task.set_prompt_fields",
        entity_type="task",
        entity_id=args.task_id,
        payload={},
        mutator=apply,
    )


def cmd_task_transition(args):
    def apply(state, plan):
        task = find_item(state["tasks"], args.task_id)
        old = task.get("status")

        ensure_task_status_transition(old, args.to)
        ensure_epic_can_accept_task(plan, task.get("epic_id"), args.to)

        if args.to == "approved":
            raise TaskError("USE_TASK_APPROVE_COMMAND_FOR_APPROVAL")

        task["status"] = args.to
        task["updated_at"] = utc_now()

        if args.to != "approved":
            task["approved_by"] = "" if args.to not in {"done", "archived"} else task.get("approved_by", "")
            task["approved_at"] = "" if args.to not in {"done", "archived"} else task.get("approved_at", "")
            task["approval_notes"] = "" if args.to not in {"done", "archived"} else task.get("approval_notes", "")

        if state.get("current_task_id") == args.task_id and args.to not in CURRENT_ALLOWED_STATUSES:
            state["current_task_id"] = None

    mutate(
        args=args,
        command="task.transition",
        entity_type="task",
        entity_id=args.task_id,
        payload={"to": args.to},
        mutator=apply,
    )


def cmd_task_approve(args):
    def apply(state, plan):
        task = find_item(state["tasks"], args.task_id)

        ensure_task_status_transition(task.get("status"), "approved")
        ensure_epic_can_accept_task(plan, task.get("epic_id"), "approved")

        task["status"] = "approved"
        task["approved_by"] = args.by or args.actor
        task["approved_at"] = utc_now()
        task["approval_notes"] = args.notes or ""
        task["updated_at"] = utc_now()

        if state.get("current_task_id") == args.task_id:
            state["current_task_id"] = None

        return {"payload": {"by": task["approved_by"], "notes": args.notes or ""}}

    mutate(
        args=args,
        command="task.approve",
        entity_type="task",
        entity_id=args.task_id,
        payload={},
        mutator=apply,
    )


def cmd_task_archive(args):
    args.to = "archived"
    cmd_task_transition(args)


def task_add_list_item(args, field, command):
    def apply(state, plan):
        task = find_item(state["tasks"], args.task_id)
        ensure_task_mutable(task)

        task.setdefault(field, []).append(args.text)
        task["updated_at"] = utc_now()

    mutate(
        args=args,
        command=command,
        entity_type="task",
        entity_id=args.task_id,
        payload={"field": field, "text": args.text},
        mutator=apply,
    )


def task_remove_list_item(args, field, command):
    def apply(state, plan):
        task = find_item(state["tasks"], args.task_id)
        ensure_task_mutable(task)

        items = task.setdefault(field, [])
        index = args.index - 1

        if index < 0 or index >= len(items):
            raise TaskError("INDEX_OUT_OF_RANGE")

        removed = items.pop(index)
        task["updated_at"] = utc_now()

        return {"payload": {"field": field, "index": args.index, "removed": removed}}

    mutate(
        args=args,
        command=command,
        entity_type="task",
        entity_id=args.task_id,
        payload={},
        mutator=apply,
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

    print("{} [{}] {} -> {}".format(task.get("id"), task.get("status"), task.get("epic_id"), task.get("title")))


def cmd_current_set(args):
    def apply(state, plan):
        task = find_item(state["tasks"], args.task_id)

        if task.get("status") not in CURRENT_ALLOWED_STATUSES:
            raise TaskError(
                "TASK_CANNOT_BE_CURRENT: {} status is {}".format(
                    args.task_id,
                    task.get("status"),
                )
            )

        ensure_epic_can_accept_task(plan, task.get("epic_id"), task.get("status"))

        previous = state.get("current_task_id")
        state["current_task_id"] = args.task_id

        return {"payload": {"previous": previous, "current": args.task_id}}

    mutate(
        args=args,
        command="current.set",
        entity_type="current_task",
        entity_id=args.task_id,
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

    task_id = args.task or state.get("current_task_id")

    if not task_id:
        raise TaskError("NO_TASK_SELECTED: use --task TASK-001 or `current set TASK-001`")

    task = find_item(state.get("tasks", []), task_id)

    if not args.allow_inactive and task.get("status") not in CURRENT_ALLOWED_STATUSES:
        raise TaskError("TASK_IS_NOT_EXECUTABLE: {} status is {}".format(task_id, task.get("status")))

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
    p.add_argument("task_id")
    p.add_argument("--text", required=True)
    p.set_defaults(func=lambda a, f=field, c=add_command: task_add_list_item(a, f, c))

    p = task_sub.add_parser(remove_name, help="Remove item from {}".format(field))
    p.add_argument("task_id")
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
    p.add_argument("task_id")
    p.set_defaults(func=cmd_task_show)

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
    p.add_argument("task_id")
    p.add_argument("--title", required=True)
    p.set_defaults(func=cmd_task_rename)

    p = task_sub.add_parser("update-summary")
    p.add_argument("task_id")
    p.add_argument("--text", required=True)
    p.set_defaults(func=cmd_task_update_summary)

    p = task_sub.add_parser("update-description")
    p.add_argument("task_id")
    p.add_argument("--text", required=True)
    p.set_defaults(func=cmd_task_update_description)

    p = task_sub.add_parser("set-prompt-fields")
    p.add_argument("task_id")
    p.add_argument("--active-role")
    p.add_argument("--active-stage")
    p.add_argument("--active-document")
    p.add_argument("--expected-result")
    p.add_argument("--verification-mode", choices=sorted(VERIFICATION_MODES))
    p.set_defaults(func=cmd_task_set_prompt_fields)

    p = task_sub.add_parser("transition")
    p.add_argument("task_id")
    p.add_argument("--to", required=True, choices=sorted(TASK_STATUSES))
    p.set_defaults(func=cmd_task_transition)

    p = task_sub.add_parser("approve")
    p.add_argument("task_id")
    p.add_argument("--by", default="")
    p.add_argument("--notes", default="")
    p.set_defaults(func=cmd_task_approve)

    p = task_sub.add_parser("archive")
    p.add_argument("task_id")
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
    p.add_argument("task_id")
    p.set_defaults(func=cmd_current_set)

    p = current_sub.add_parser("clear")
    p.set_defaults(func=cmd_current_clear)

    prompt = sub.add_parser("prompt", help="Build Codex prompt package")
    prompt_sub = prompt.add_subparsers(dest="prompt_command", required=True)

    p = prompt_sub.add_parser("build")
    p.add_argument("--task", help="Task id. Defaults to current_task_id.")
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

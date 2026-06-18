#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
planctl.py — strict CLI gateway for AI_PROJECT/state/plan.json

Управляет только верхним планом:
- project
- idea
- goal
- strategy
- initiatives
- epics

НЕ управляет исполняемыми Task.
Task лучше вынести отдельно в AI_PROJECT/state/tasks.json.

Примеры:

  python scripts/planctl.py init --project-name "AI Development System"

  python scripts/planctl.py idea set --text "Создать управляемую AI Development System"
  python scripts/planctl.py goal set --text "Построить Project Control Gateway"

  python scripts/planctl.py strategy set-summary --text "Сначала CLI, потом Codex skill/plugin"
  python scripts/planctl.py strategy add-principle --text "Codex не редактирует state вручную"

  python scripts/planctl.py initiative create --title "Project Control Gateway"
  python scripts/planctl.py epic create --initiative INIT-001 --title "Plan Control CLI"

  python scripts/planctl.py show
  python scripts/planctl.py validate
  python scripts/planctl.py render
  python scripts/planctl.py audit --last 20
"""

import argparse
import json
import os
import re
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path


PLAN_SCHEMA_VERSION = 1
DEFAULT_PROJECT_ID = "PROJECT-001"

PLAN_STATUSES = {
    "proposed",
    "planned",
    "active",
    "blocked",
    "done",
    "deferred",
    "archived",
}

STATUS_TRANSITIONS = {
    "proposed": {"planned", "active", "deferred", "archived"},
    "planned": {"active", "blocked", "deferred", "archived"},
    "active": {"blocked", "done", "deferred", "archived"},
    "blocked": {"active", "deferred", "archived"},
    "done": {"archived"},
    "deferred": {"planned", "active", "archived"},
    "archived": set(),
}

TERMINAL_OR_INACTIVE = {"done", "deferred", "archived"}
EPIC_KEY_RE = re.compile(r"^[A-Z][A-Z0-9]{1,11}$")


class PlanError(Exception):
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


def plan_path(root):
    return state_dir(root) / "plan.json"


def plan_events_path(root):
    return events_dir(root) / "plan-events.jsonl"


def tasks_path(root):
    return state_dir(root) / "tasks.json"


def generated_plan_path(root):
    return generated_dir(root) / "CODEX_PLAN.md"


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


def read_json(path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise PlanError("PLAN_NOT_INITIALIZED: run `python scripts/planctl.py init` first")
    except json.JSONDecodeError as e:
        raise PlanError(
            "INVALID_JSON: {}:{}:{} {}".format(path, e.lineno, e.colno, e.msg)
        )


def read_optional_tasks(root):
    path = tasks_path(root)

    if not path.exists():
        return {"tasks": []}

    try:
        with path.open("r", encoding="utf-8") as f:
            state = json.load(f)
    except json.JSONDecodeError as e:
        raise PlanError(
            "INVALID_JSON: {}:{}:{} {}".format(path, e.lineno, e.colno, e.msg)
        )

    if not isinstance(state, dict) or not isinstance(state.get("tasks"), list):
        raise PlanError("TASK_STATE_INVALID: tasks must be a list")

    return state


def load_plan(root):
    return read_json(plan_path(root))


def save_plan(root, plan):
    write_json(plan_path(root), plan)


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

    path = plan_events_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(line)


def default_plan(project_name, project_id):
    now = utc_now()

    return {
        "schema_version": PLAN_SCHEMA_VERSION,
        "revision": 0,
        "project": {
            "id": project_id,
            "name": project_name,
            "status": "active",
            "created_at": now,
            "updated_at": now,
        },
        "idea": {
            "text": "",
            "updated_at": now,
        },
        "goal": {
            "text": "",
            "success_criteria": [],
            "updated_at": now,
        },
        "strategy": {
            "summary": "",
            "principles": [],
            "constraints": [],
            "updated_at": now,
        },
        "initiatives": [],
        "epics": [],
    }


def require_keys(obj, keys, path, errors):
    if not isinstance(obj, dict):
        errors.append("{} must be an object".format(path))
        return

    for key in keys:
        if key not in obj:
            errors.append("{} missing required key `{}`".format(path, key))


def find_item(items, item_id, required=True):
    for item in items:
        if item.get("id") == item_id:
            return item

    if required:
        raise PlanError("ENTITY_NOT_FOUND: {}".format(item_id))

    return None


def epic_key_errors(key, path):
    if not isinstance(key, str):
        return ["{}.key must be a string".format(path)]

    if not key:
        return ["{}.key must be non-empty".format(path)]

    if key != key.upper():
        return ["{}.key must be uppercase".format(path)]

    if not EPIC_KEY_RE.fullmatch(key):
        return [
            "{}.key must match {}".format(
                path,
                EPIC_KEY_RE.pattern,
            )
        ]

    return []


def require_valid_epic_key(key):
    errors = epic_key_errors(key, "epic")

    if errors:
        raise PlanError("INVALID_EPIC_KEY:\n- " + "\n- ".join(errors))

    return key


def epic_key_label(epic):
    if epic.get("key"):
        return "{} / {}".format(epic.get("id"), epic.get("key"))

    return epic.get("id")


def rendered_epic_label(epic):
    if epic.get("key"):
        return "`{}` / `{}`".format(epic.get("id"), epic.get("key"))

    return "`{}`".format(epic.get("id"))


def count_child_tasks(root, epic_id):
    state = read_optional_tasks(root)

    return len([
        task for task in state.get("tasks", [])
        if task.get("epic_id") == epic_id
    ])


def validate_plan(plan):
    errors = []

    require_keys(
        plan,
        [
            "schema_version",
            "revision",
            "project",
            "idea",
            "goal",
            "strategy",
            "initiatives",
            "epics",
        ],
        "plan",
        errors,
    )

    if errors:
        return errors

    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        errors.append("schema_version must be {}".format(PLAN_SCHEMA_VERSION))

    if not isinstance(plan.get("revision"), int) or plan.get("revision") < 0:
        errors.append("revision must be a non-negative integer")

    project = plan.get("project", {})
    require_keys(project, ["id", "name", "status"], "project", errors)

    if project.get("status") not in {"active", "archived"}:
        errors.append("project.status must be active or archived")

    idea = plan.get("idea", {})
    require_keys(idea, ["text"], "idea", errors)

    goal = plan.get("goal", {})
    require_keys(goal, ["text", "success_criteria"], "goal", errors)

    if not isinstance(goal.get("success_criteria"), list):
        errors.append("goal.success_criteria must be a list")

    strategy = plan.get("strategy", {})
    require_keys(strategy, ["summary", "principles", "constraints"], "strategy", errors)

    if not isinstance(strategy.get("principles"), list):
        errors.append("strategy.principles must be a list")

    if not isinstance(strategy.get("constraints"), list):
        errors.append("strategy.constraints must be a list")

    initiatives = plan.get("initiatives")
    epics = plan.get("epics")

    if not isinstance(initiatives, list):
        errors.append("initiatives must be a list")
        initiatives = []

    if not isinstance(epics, list):
        errors.append("epics must be a list")
        epics = []

    initiative_ids = set()

    for i, item in enumerate(initiatives):
        path = "initiatives[{}]".format(i)

        require_keys(
            item,
            ["id", "title", "status", "priority", "order"],
            path,
            errors,
        )

        item_id = item.get("id")

        if item_id in initiative_ids:
            errors.append("duplicate initiative id: {}".format(item_id))

        initiative_ids.add(item_id)

        if item.get("status") not in PLAN_STATUSES:
            errors.append("{}.status is invalid: {}".format(path, item.get("status")))

        if not isinstance(item.get("priority"), int):
            errors.append("{}.priority must be integer".format(path))

        if not isinstance(item.get("order"), int):
            errors.append("{}.order must be integer".format(path))

    epic_ids = set()
    epic_keys = {}

    for i, item in enumerate(epics):
        path = "epics[{}]".format(i)

        require_keys(
            item,
            ["id", "initiative_id", "title", "status", "priority", "order"],
            path,
            errors,
        )

        item_id = item.get("id")

        if item_id in epic_ids:
            errors.append("duplicate epic id: {}".format(item_id))

        epic_ids.add(item_id)

        if "key" in item:
            key_errors = epic_key_errors(item.get("key"), path)
            errors.extend(key_errors)

            if not key_errors:
                key = item.get("key")

                if key in epic_keys:
                    errors.append(
                        "{}.key duplicates epic key {} used by {}".format(
                            path,
                            key,
                            epic_keys[key],
                        )
                    )
                else:
                    epic_keys[key] = item_id

        if item.get("initiative_id") not in initiative_ids:
            errors.append(
                "{}.initiative_id references missing initiative: {}".format(
                    path,
                    item.get("initiative_id"),
                )
            )

        if item.get("status") not in PLAN_STATUSES:
            errors.append("{}.status is invalid: {}".format(path, item.get("status")))

        parent = find_item(initiatives, item.get("initiative_id"), required=False)

        if parent and parent.get("status") == "archived" and item.get("status") not in TERMINAL_OR_INACTIVE:
            errors.append(
                "epic {} is {} under archived initiative {}".format(
                    item.get("id"),
                    item.get("status"),
                    item.get("initiative_id"),
                )
            )

    return errors


def require_valid_plan(plan):
    errors = validate_plan(plan)

    if errors:
        raise PlanError("VALIDATION_FAILED:\n- " + "\n- ".join(errors))


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


def ensure_status_transition(current, new):
    if new not in PLAN_STATUSES:
        raise PlanError("INVALID_STATUS: {}".format(new))

    if current == new:
        return

    if new not in STATUS_TRANSITIONS.get(current, set()):
        raise PlanError("INVALID_STATUS_TRANSITION: {} -> {}".format(current, new))


def render_plan_markdown(plan):
    lines = []

    lines.append("<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->")
    lines.append("<!-- Source: AI_PROJECT/state/plan.json -->")
    lines.append("")
    lines.append("# Project Plan")
    lines.append("")
    lines.append("Project: **{}**".format(plan["project"].get("name", "")))
    lines.append("Status: `{}`".format(plan["project"].get("status", "")))
    lines.append("Revision: `{}`".format(plan.get("revision", 0)))
    lines.append("")

    lines.append("## Idea")
    lines.append("")
    lines.append(plan.get("idea", {}).get("text") or "_No idea defined._")
    lines.append("")

    lines.append("## Goal")
    lines.append("")
    lines.append(plan.get("goal", {}).get("text") or "_No goal defined._")
    lines.append("")

    criteria = plan.get("goal", {}).get("success_criteria", [])

    if criteria:
        lines.append("### Success Criteria")
        lines.append("")

        for item in criteria:
            lines.append("- {}".format(item))

        lines.append("")

    lines.append("## Strategy")
    lines.append("")
    lines.append(plan.get("strategy", {}).get("summary") or "_No strategy summary defined._")
    lines.append("")

    principles = plan.get("strategy", {}).get("principles", [])

    if principles:
        lines.append("### Principles")
        lines.append("")

        for item in principles:
            lines.append("- {}".format(item))

        lines.append("")

    constraints = plan.get("strategy", {}).get("constraints", [])

    if constraints:
        lines.append("### Constraints")
        lines.append("")

        for item in constraints:
            lines.append("- {}".format(item))

        lines.append("")

    lines.append("## Initiatives")
    lines.append("")

    initiatives = sorted(
        plan.get("initiatives", []),
        key=lambda x: (x.get("order", 0), x.get("id", "")),
    )

    epics = sorted(
        plan.get("epics", []),
        key=lambda x: (x.get("order", 0), x.get("id", "")),
    )

    if not initiatives:
        lines.append("_No initiatives defined._")
        lines.append("")
    else:
        for init in initiatives:
            lines.append("### {} — {}".format(init.get("id"), init.get("title")))
            lines.append("")
            lines.append("Status: `{}`  ".format(init.get("status")))
            lines.append("Priority: `{}`  ".format(init.get("priority")))

            if init.get("summary"):
                lines.append("")
                lines.append(init.get("summary"))

            child_epics = [
                e for e in epics
                if e.get("initiative_id") == init.get("id")
            ]

            lines.append("")

            if child_epics:
                lines.append("Epics:")
                lines.append("")

                for epic in child_epics:
                    lines.append(
                        "- {} — {} (`{}`)".format(
                            rendered_epic_label(epic),
                            epic.get("title"),
                            epic.get("status"),
                        )
                    )
            else:
                lines.append("_No epics._")

            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_plan(root, plan):
    require_valid_plan(plan)
    atomic_write_text(generated_plan_path(root), render_plan_markdown(plan))


def mutate(args, command, entity_type, entity_id, payload, mutator):
    root = repo_root(args)

    ensure_project_dirs(root)

    plan = load_plan(root)
    require_valid_plan(plan)

    revision_before = plan.get("revision", 0)

    mutator(plan)

    plan["revision"] = revision_before + 1
    plan["project"]["updated_at"] = utc_now()

    require_valid_plan(plan)

    save_plan(root, plan)

    append_event(
        root=root,
        actor=args.actor,
        command=command,
        entity_type=entity_type,
        entity_id=entity_id,
        revision_before=revision_before,
        revision_after=plan["revision"],
        payload=payload,
    )

    render_plan(root, plan)

    print("OK: {} revision {} -> {}".format(command, revision_before, plan["revision"]))


def print_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def new_plan_item(item_id, title, status, summary, priority, order, extra=None):
    now = utc_now()

    item = {
        "id": item_id,
        "title": title,
        "status": status,
        "summary": summary or "",
        "priority": priority,
        "order": order,
        "created_at": now,
        "updated_at": now,
    }

    if extra:
        item.update(extra)

    return item


def cmd_init(args):
    root = repo_root(args)

    ensure_project_dirs(root)

    path = plan_path(root)

    if path.exists() and not args.force:
        raise PlanError("PLAN_ALREADY_EXISTS: use --force to overwrite")

    plan = default_plan(args.project_name, args.project_id)

    require_valid_plan(plan)
    save_plan(root, plan)

    append_event(
        root=root,
        actor=args.actor,
        command="plan.init",
        entity_type="plan",
        entity_id=plan["project"]["id"],
        revision_before=None,
        revision_after=plan["revision"],
        payload={
            "project_id": args.project_id,
            "project_name": args.project_name,
            "force": bool(args.force),
        },
    )

    render_plan(root, plan)

    print("OK: initialized {}".format(path))


def cmd_show(args):
    plan = load_plan(repo_root(args))
    require_valid_plan(plan)

    if args.json:
        print_json(plan)
        return

    print("Project: {}".format(plan["project"].get("name")))
    print("ID:      {}".format(plan["project"].get("id")))
    print("Status:  {}".format(plan["project"].get("status")))
    print("Revision: {}".format(plan.get("revision")))
    print("Idea:    {}".format(plan.get("idea", {}).get("text") or "—"))
    print("Goal:    {}".format(plan.get("goal", {}).get("text") or "—"))
    print("Initiatives: {}".format(len(plan.get("initiatives", []))))
    print("Epics:       {}".format(len(plan.get("epics", []))))


def cmd_status(args):
    root = repo_root(args)

    print("Root:      {}".format(root))
    print("Plan:      {}".format(plan_path(root)))
    print("Events:    {}".format(plan_events_path(root)))
    print("Generated: {}".format(generated_plan_path(root)))

    plan = load_plan(root)
    errors = validate_plan(plan)

    print("Revision:  {}".format(plan.get("revision")))
    print("Valid:     {}".format("yes" if not errors else "no"))

    if errors:
        for error in errors:
            print("- {}".format(error))


def cmd_validate(args):
    plan = load_plan(repo_root(args))
    errors = validate_plan(plan)

    if errors:
        print("VALIDATION_FAILED:", file=sys.stderr)

        for error in errors:
            print("- {}".format(error), file=sys.stderr)

        return 1

    print("OK: plan is valid")
    return 0


def cmd_render(args):
    root = repo_root(args)
    plan = load_plan(root)

    render_plan(root, plan)

    print("OK: rendered {}".format(generated_plan_path(root)))


def cmd_audit(args):
    path = plan_events_path(repo_root(args))

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


def cmd_idea_show(args):
    plan = load_plan(repo_root(args))
    print(plan.get("idea", {}).get("text") or "")


def cmd_idea_set(args):
    def apply(plan):
        plan["idea"]["text"] = args.text
        plan["idea"]["updated_at"] = utc_now()

    mutate(
        args=args,
        command="idea.set",
        entity_type="idea",
        entity_id="idea",
        payload={"text": args.text},
        mutator=apply,
    )


def cmd_goal_show(args):
    goal = load_plan(repo_root(args)).get("goal", {})

    print(goal.get("text") or "")

    criteria = goal.get("success_criteria", [])

    if criteria:
        print("\nSuccess criteria:")

        for i, item in enumerate(criteria, start=1):
            print("{}. {}".format(i, item))


def cmd_goal_set(args):
    def apply(plan):
        plan["goal"]["text"] = args.text
        plan["goal"]["updated_at"] = utc_now()

    mutate(
        args=args,
        command="goal.set",
        entity_type="goal",
        entity_id="goal",
        payload={"text": args.text},
        mutator=apply,
    )


def cmd_goal_add_criterion(args):
    def apply(plan):
        plan["goal"].setdefault("success_criteria", []).append(args.text)
        plan["goal"]["updated_at"] = utc_now()

    mutate(
        args=args,
        command="goal.add_criterion",
        entity_type="goal",
        entity_id="goal",
        payload={"text": args.text},
        mutator=apply,
    )


def cmd_goal_remove_criterion(args):
    def apply(plan):
        items = plan["goal"].setdefault("success_criteria", [])
        index = args.index - 1

        if index < 0 or index >= len(items):
            raise PlanError("INDEX_OUT_OF_RANGE")

        items.pop(index)
        plan["goal"]["updated_at"] = utc_now()

    mutate(
        args=args,
        command="goal.remove_criterion",
        entity_type="goal",
        entity_id="goal",
        payload={"index": args.index},
        mutator=apply,
    )


def cmd_strategy_show(args):
    strategy = load_plan(repo_root(args)).get("strategy", {})

    print(strategy.get("summary") or "")

    principles = strategy.get("principles", [])

    if principles:
        print("\nPrinciples:")

        for i, item in enumerate(principles, start=1):
            print("{}. {}".format(i, item))

    constraints = strategy.get("constraints", [])

    if constraints:
        print("\nConstraints:")

        for i, item in enumerate(constraints, start=1):
            print("{}. {}".format(i, item))


def cmd_strategy_set_summary(args):
    def apply(plan):
        plan["strategy"]["summary"] = args.text
        plan["strategy"]["updated_at"] = utc_now()

    mutate(
        args=args,
        command="strategy.set_summary",
        entity_type="strategy",
        entity_id="strategy",
        payload={"text": args.text},
        mutator=apply,
    )


def strategy_add_list_item(args, field, command):
    def apply(plan):
        plan["strategy"].setdefault(field, []).append(args.text)
        plan["strategy"]["updated_at"] = utc_now()

    mutate(
        args=args,
        command=command,
        entity_type="strategy",
        entity_id="strategy",
        payload={"field": field, "text": args.text},
        mutator=apply,
    )


def strategy_remove_list_item(args, field, command):
    def apply(plan):
        items = plan["strategy"].setdefault(field, [])
        index = args.index - 1

        if index < 0 or index >= len(items):
            raise PlanError("INDEX_OUT_OF_RANGE")

        items.pop(index)
        plan["strategy"]["updated_at"] = utc_now()

    mutate(
        args=args,
        command=command,
        entity_type="strategy",
        entity_id="strategy",
        payload={"field": field, "index": args.index},
        mutator=apply,
    )


def cmd_initiative_list(args):
    initiatives = load_plan(repo_root(args)).get("initiatives", [])

    if args.json:
        print_json(initiatives)
        return

    if not initiatives:
        print("No initiatives.")
        return

    for item in sorted(initiatives, key=lambda x: (x.get("order", 0), x.get("id", ""))):
        print("{} [{}] {}".format(item.get("id"), item.get("status"), item.get("title")))


def cmd_initiative_show(args):
    plan = load_plan(repo_root(args))
    item = find_item(plan.get("initiatives", []), args.initiative_id)

    print_json(item)


def cmd_initiative_create(args):
    created = {"id": None}

    def apply(plan):
        item_id = next_id("INIT", plan["initiatives"])
        created["id"] = item_id

        item = new_plan_item(
            item_id=item_id,
            title=args.title,
            status=args.status,
            summary=args.summary,
            priority=args.priority,
            order=next_order(plan["initiatives"]),
        )

        plan["initiatives"].append(item)

    mutate(
        args=args,
        command="initiative.create",
        entity_type="initiative",
        entity_id="NEW",
        payload={
            "title": args.title,
            "status": args.status,
            "priority": args.priority,
        },
        mutator=apply,
    )

    print("Created: {}".format(created["id"]))


def cmd_initiative_rename(args):
    def apply(plan):
        item = find_item(plan["initiatives"], args.initiative_id)

        if item.get("status") == "archived":
            raise PlanError("ARCHIVED_ENTITY_IS_IMMUTABLE")

        item["title"] = args.title
        item["updated_at"] = utc_now()

    mutate(
        args=args,
        command="initiative.rename",
        entity_type="initiative",
        entity_id=args.initiative_id,
        payload={"title": args.title},
        mutator=apply,
    )


def cmd_initiative_summary(args):
    def apply(plan):
        item = find_item(plan["initiatives"], args.initiative_id)

        if item.get("status") == "archived":
            raise PlanError("ARCHIVED_ENTITY_IS_IMMUTABLE")

        item["summary"] = args.text
        item["updated_at"] = utc_now()

    mutate(
        args=args,
        command="initiative.summary",
        entity_type="initiative",
        entity_id=args.initiative_id,
        payload={"summary": args.text},
        mutator=apply,
    )


def cmd_initiative_status(args):
    def apply(plan):
        item = find_item(plan["initiatives"], args.initiative_id)

        old = item.get("status")
        ensure_status_transition(old, args.to)

        if args.to == "archived":
            blocking = [
                e for e in plan["epics"]
                if e.get("initiative_id") == args.initiative_id
                and e.get("status") not in TERMINAL_OR_INACTIVE
            ]

            if blocking and not args.force:
                raise PlanError(
                    "INITIATIVE_HAS_ACTIVE_EPICS: archive/defer/done child epics first or use --force"
                )

            if args.force:
                now = utc_now()

                for epic in blocking:
                    epic["status"] = "archived"
                    epic["updated_at"] = now

        item["status"] = args.to
        item["updated_at"] = utc_now()

    mutate(
        args=args,
        command="initiative.status",
        entity_type="initiative",
        entity_id=args.initiative_id,
        payload={"to": args.to, "force": args.force},
        mutator=apply,
    )


def cmd_initiative_archive(args):
    args.to = "archived"
    cmd_initiative_status(args)


def cmd_epic_list(args):
    plan = load_plan(repo_root(args))
    epics = plan.get("epics", [])

    if args.initiative:
        epics = [e for e in epics if e.get("initiative_id") == args.initiative]

    if args.json:
        print_json(epics)
        return

    if not epics:
        print("No epics.")
        return

    for item in sorted(
        epics,
        key=lambda x: (x.get("initiative_id", ""), x.get("order", 0), x.get("id", "")),
    ):
        print(
            "{} [{}] {} -> {}".format(
                epic_key_label(item),
                item.get("status"),
                item.get("initiative_id"),
                item.get("title"),
            )
        )


def cmd_epic_show(args):
    plan = load_plan(repo_root(args))
    item = find_item(plan.get("epics", []), args.epic_id)

    print_json(item)


def cmd_epic_create(args):
    created = {"id": None}

    def apply(plan):
        key = require_valid_epic_key(args.key) if args.key is not None else None
        initiative = find_item(plan["initiatives"], args.initiative)

        if initiative.get("status") == "archived":
            raise PlanError("CANNOT_CREATE_EPIC_UNDER_ARCHIVED_INITIATIVE")

        item_id = next_id("EPIC", plan["epics"])
        created["id"] = item_id
        extra = {"initiative_id": args.initiative}

        if key is not None:
            extra["key"] = key

        item = new_plan_item(
            item_id=item_id,
            title=args.title,
            status=args.status,
            summary=args.summary,
            priority=args.priority,
            order=next_order(plan["epics"], "initiative_id", args.initiative),
            extra=extra,
        )

        plan["epics"].append(item)

    mutate(
        args=args,
        command="epic.create",
        entity_type="epic",
        entity_id="NEW",
        payload={
            "initiative_id": args.initiative,
            "title": args.title,
            "status": args.status,
            "key": args.key,
        },
        mutator=apply,
    )

    print("Created: {}".format(created["id"]))


def cmd_epic_rename(args):
    def apply(plan):
        item = find_item(plan["epics"], args.epic_id)

        if item.get("status") == "archived":
            raise PlanError("ARCHIVED_ENTITY_IS_IMMUTABLE")

        item["title"] = args.title
        item["updated_at"] = utc_now()

    mutate(
        args=args,
        command="epic.rename",
        entity_type="epic",
        entity_id=args.epic_id,
        payload={"title": args.title},
        mutator=apply,
    )


def cmd_epic_summary(args):
    def apply(plan):
        item = find_item(plan["epics"], args.epic_id)

        if item.get("status") == "archived":
            raise PlanError("ARCHIVED_ENTITY_IS_IMMUTABLE")

        item["summary"] = args.text
        item["updated_at"] = utc_now()

    mutate(
        args=args,
        command="epic.summary",
        entity_type="epic",
        entity_id=args.epic_id,
        payload={"summary": args.text},
        mutator=apply,
    )


def cmd_epic_set_key(args):
    root = repo_root(args)
    new_key = require_valid_epic_key(args.key)
    payload = {
        "old_key": None,
        "key": new_key,
        "force_legacy_migration": bool(args.force_legacy_migration),
    }

    def apply(plan):
        item = find_item(plan["epics"], args.epic_id)

        if item.get("status") == "archived":
            raise PlanError("ARCHIVED_ENTITY_IS_IMMUTABLE")

        current_key = item.get("key")
        payload["old_key"] = current_key
        child_count = count_child_tasks(root, args.epic_id)

        if child_count and current_key:
            if current_key == new_key:
                raise PlanError(
                    "EPIC_KEY_ALREADY_SET: {} already has key {}".format(
                        args.epic_id,
                        current_key,
                    )
                )

            raise PlanError(
                "EPIC_KEY_IMMUTABLE: {} has {} child task(s) and key {}".format(
                    args.epic_id,
                    child_count,
                    current_key,
                )
            )

        if child_count and not args.force_legacy_migration:
            raise PlanError(
                "EPIC_KEY_LEGACY_MIGRATION_REQUIRES_FORCE: {} has {} child task(s)".format(
                    args.epic_id,
                    child_count,
                )
            )

        item["key"] = new_key
        item["updated_at"] = utc_now()

    mutate(
        args=args,
        command="epic.set_key",
        entity_type="epic",
        entity_id=args.epic_id,
        payload=payload,
        mutator=apply,
    )


def cmd_epic_status(args):
    def apply(plan):
        item = find_item(plan["epics"], args.epic_id)

        ensure_status_transition(item.get("status"), args.to)

        parent = find_item(plan["initiatives"], item.get("initiative_id"))

        if parent.get("status") == "archived" and args.to not in TERMINAL_OR_INACTIVE:
            raise PlanError("CANNOT_ACTIVATE_EPIC_UNDER_ARCHIVED_INITIATIVE")

        item["status"] = args.to
        item["updated_at"] = utc_now()

    mutate(
        args=args,
        command="epic.status",
        entity_type="epic",
        entity_id=args.epic_id,
        payload={"to": args.to},
        mutator=apply,
    )


def cmd_epic_archive(args):
    args.to = "archived"
    cmd_epic_status(args)


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


def build_parser():
    parser = argparse.ArgumentParser(
        description="Strict plan.json control CLI for AI Development System"
    )

    add_common_args(parser)

    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="Initialize AI_PROJECT/state/plan.json")
    p.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    p.add_argument("--project-name", default="AI Development System")
    p.add_argument("--force", action="store_true", help="Overwrite existing plan.json")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("show", help="Show plan summary")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("status", help="Show file paths and validation status")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("validate", help="Validate plan.json")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("render", help="Render generated/CODEX_PLAN.md")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("audit", help="Show audit events")
    p.add_argument("--last", type=int, default=20)
    p.add_argument("--entity", help="Filter by entity id")
    p.set_defaults(func=cmd_audit)

    idea = sub.add_parser("idea", help="Manage idea")
    idea_sub = idea.add_subparsers(dest="idea_command", required=True)

    p = idea_sub.add_parser("show")
    p.set_defaults(func=cmd_idea_show)

    p = idea_sub.add_parser("set")
    p.add_argument("--text", required=True)
    p.set_defaults(func=cmd_idea_set)

    goal = sub.add_parser("goal", help="Manage goal")
    goal_sub = goal.add_subparsers(dest="goal_command", required=True)

    p = goal_sub.add_parser("show")
    p.set_defaults(func=cmd_goal_show)

    p = goal_sub.add_parser("set")
    p.add_argument("--text", required=True)
    p.set_defaults(func=cmd_goal_set)

    p = goal_sub.add_parser("add-criterion")
    p.add_argument("--text", required=True)
    p.set_defaults(func=cmd_goal_add_criterion)

    p = goal_sub.add_parser("remove-criterion")
    p.add_argument("--index", type=int, required=True)
    p.set_defaults(func=cmd_goal_remove_criterion)

    strategy = sub.add_parser("strategy", help="Manage strategy")
    strategy_sub = strategy.add_subparsers(dest="strategy_command", required=True)

    p = strategy_sub.add_parser("show")
    p.set_defaults(func=cmd_strategy_show)

    p = strategy_sub.add_parser("set-summary")
    p.add_argument("--text", required=True)
    p.set_defaults(func=cmd_strategy_set_summary)

    p = strategy_sub.add_parser("add-principle")
    p.add_argument("--text", required=True)
    p.set_defaults(
        func=lambda a: strategy_add_list_item(
            a,
            "principles",
            "strategy.add_principle",
        )
    )

    p = strategy_sub.add_parser("remove-principle")
    p.add_argument("--index", type=int, required=True)
    p.set_defaults(
        func=lambda a: strategy_remove_list_item(
            a,
            "principles",
            "strategy.remove_principle",
        )
    )

    p = strategy_sub.add_parser("add-constraint")
    p.add_argument("--text", required=True)
    p.set_defaults(
        func=lambda a: strategy_add_list_item(
            a,
            "constraints",
            "strategy.add_constraint",
        )
    )

    p = strategy_sub.add_parser("remove-constraint")
    p.add_argument("--index", type=int, required=True)
    p.set_defaults(
        func=lambda a: strategy_remove_list_item(
            a,
            "constraints",
            "strategy.remove_constraint",
        )
    )

    initiative = sub.add_parser("initiative", help="Manage initiatives")
    init_sub = initiative.add_subparsers(dest="initiative_command", required=True)

    p = init_sub.add_parser("list")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_initiative_list)

    p = init_sub.add_parser("show")
    p.add_argument("initiative_id")
    p.set_defaults(func=cmd_initiative_show)

    p = init_sub.add_parser("create")
    p.add_argument("--title", required=True)
    p.add_argument("--summary", default="")
    p.add_argument("--priority", type=int, default=1)
    p.add_argument("--status", choices=sorted(PLAN_STATUSES), default="active")
    p.set_defaults(func=cmd_initiative_create)

    p = init_sub.add_parser("rename")
    p.add_argument("initiative_id")
    p.add_argument("--title", required=True)
    p.set_defaults(func=cmd_initiative_rename)

    p = init_sub.add_parser("summary")
    p.add_argument("initiative_id")
    p.add_argument("--text", required=True)
    p.set_defaults(func=cmd_initiative_summary)

    p = init_sub.add_parser("status")
    p.add_argument("initiative_id")
    p.add_argument("--to", required=True, choices=sorted(PLAN_STATUSES))
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_initiative_status)

    p = init_sub.add_parser("archive")
    p.add_argument("initiative_id")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_initiative_archive)

    epic = sub.add_parser("epic", help="Manage epics")
    epic_sub = epic.add_subparsers(dest="epic_command", required=True)

    p = epic_sub.add_parser("list")
    p.add_argument("--initiative")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_epic_list)

    p = epic_sub.add_parser("show")
    p.add_argument("epic_id")
    p.set_defaults(func=cmd_epic_show)

    p = epic_sub.add_parser("create")
    p.add_argument("--initiative", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--key")
    p.add_argument("--summary", default="")
    p.add_argument("--priority", type=int, default=1)
    p.add_argument("--status", choices=sorted(PLAN_STATUSES), default="planned")
    p.set_defaults(func=cmd_epic_create)

    p = epic_sub.add_parser("rename")
    p.add_argument("epic_id")
    p.add_argument("--title", required=True)
    p.set_defaults(func=cmd_epic_rename)

    p = epic_sub.add_parser("summary")
    p.add_argument("epic_id")
    p.add_argument("--text", required=True)
    p.set_defaults(func=cmd_epic_summary)

    p = epic_sub.add_parser("set-key")
    p.add_argument("epic_id")
    p.add_argument("--key", required=True)
    p.add_argument("--force-legacy-migration", action="store_true")
    p.set_defaults(func=cmd_epic_set_key)

    p = epic_sub.add_parser("status")
    p.add_argument("epic_id")
    p.add_argument("--to", required=True, choices=sorted(PLAN_STATUSES))
    p.set_defaults(func=cmd_epic_status)

    p = epic_sub.add_parser("archive")
    p.add_argument("epic_id")
    p.set_defaults(func=cmd_epic_archive)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = args.func(args)
        return int(result or 0)
    except PlanError as e:
        print("ERROR: {}".format(e), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())

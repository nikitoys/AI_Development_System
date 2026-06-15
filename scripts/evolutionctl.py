#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
evolutionctl.py — strict CLI gateway for AI_PROJECT/state/evolution.json

Управляет эволюцией самой AI Development System:

* Change Proposal
* Owner approval for system changes
* links from Change Proposal to implementation Tasks
* generated Evolution status document

НЕ управляет верхним планом Project/Idea/Goal/Strategy/Initiative/Epic.
Для верхнего плана используй scripts/planctl.py.

НЕ управляет исполнением задач.
Для задач используй scripts/taskctl.py.

Файлы:
AI_PROJECT/state/evolution.json
AI_PROJECT/events/evolution-events.jsonl
AI_PROJECT/generated/EVOLUTION.md

Примеры:

python scripts/evolutionctl.py init

python scripts/evolutionctl.py change create 
--title "Add protected files check" 
--type tooling 
--problem "Codex can still edit protected files manually" 
--proposal "Add protected project files checker"

python scripts/evolutionctl.py change add-affected-file CHG-001 
--text "scripts/check-protected-project-files.py"

python scripts/evolutionctl.py change transition CHG-001 --to ready
python scripts/evolutionctl.py change approve CHG-001 --notes "Approved for implementation"
python scripts/evolutionctl.py change link-task CHG-001 --task TASK-001
python scripts/evolutionctl.py change transition CHG-001 --to in_progress
python scripts/evolutionctl.py change transition CHG-001 --to in_review
python scripts/evolutionctl.py change accept CHG-001 --notes "Implemented and verified"

python scripts/evolutionctl.py validate
python scripts/evolutionctl.py render
python scripts/evolutionctl.py check-generated
python scripts/evolutionctl.py audit --last 20
"""

import argparse
import json
import os
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

EVOLUTION_SCHEMA_VERSION = 1
TASK_SCHEMA_VERSION = 1

CHANGE_TYPES = {
"tooling",
"docs",
"lifecycle",
"prompt",
"plugin",
"template",
"schema",
"security",
"integration",
"process",
"release",
"other",
}

CHANGE_STATUSES = {
"proposed",
"draft",
"ready",
"approved",
"in_progress",
"in_review",
"changes_requested",
"accepted",
"rejected",
"deferred",
"superseded",
"archived",
}

CHANGE_STATUS_TRANSITIONS = {
"proposed": {"draft", "rejected", "deferred"},
"draft": {"ready", "rejected", "deferred"},
"ready": {"approved", "rejected", "deferred"},
"approved": {"in_progress", "deferred", "superseded"},
"in_progress": {"in_review", "changes_requested", "deferred"},
"in_review": {"accepted", "changes_requested"},
"changes_requested": {"in_progress", "deferred"},
"accepted": {"archived"},
"rejected": {"archived"},
"deferred": {"draft", "ready", "archived"},
"superseded": {"archived"},
"archived": set(),
}

COMPATIBILITY_VALUES = {
"unknown",
"compatible",
"migration_required",
"breaking",
}

TASK_DONE_STATUSES = {"done", "archived"}

CHANGE_LIST_FIELDS = {
"affected_areas": "Affected areas",
"affected_files": "Affected files",
"risks": "Risks",
"impact": "Impact",
"linked_tasks": "Linked tasks",
"notes": "Notes",
}

class EvolutionError(Exception):
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

def evolution_path(root):
return state_dir(root) / "evolution.json"

def evolution_events_path(root):
return events_dir(root) / "evolution-events.jsonl"

def tasks_path(root):
return state_dir(root) / "tasks.json"

def generated_evolution_path(root):
return generated_dir(root) / "EVOLUTION.md"

def ensure_project_dirs(root):
state_dir(root).mkdir(parents=True, exist_ok=True)
events_dir(root).mkdir(parents=True, exist_ok=True)
generated_dir(root).mkdir(parents=True, exist_ok=True)

def atomic_write_text(path, text):
path.parent.mkdir(parents=True, exist_ok=True)

```
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
```

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
raise EvolutionError(missing_message)
except json.JSONDecodeError as e:
raise EvolutionError(
"INVALID_JSON: {}:{}:{} {}".format(path, e.lineno, e.colno, e.msg)
)

def load_evolution(root):
return read_json(
evolution_path(root),
"EVOLUTION_NOT_INITIALIZED: run `python scripts/evolutionctl.py init` first",
)

def save_evolution(root, state):
write_json(evolution_path(root), state)

def load_tasks(root, required=False):
path = tasks_path(root)

```
if not path.exists():
    if required:
        raise EvolutionError("TASKS_NOT_INITIALIZED: run `python scripts/taskctl.py init` first")
    return None

return read_json(path, "TASKS_NOT_INITIALIZED")
```

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

```
line = json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"

path = evolution_events_path(root)
path.parent.mkdir(parents=True, exist_ok=True)

with path.open("a", encoding="utf-8", newline="\n") as f:
    f.write(line)
```

def default_evolution_state():
now = utc_now()

```
return {
    "schema_version": EVOLUTION_SCHEMA_VERSION,
    "revision": 0,
    "created_at": now,
    "updated_at": now,
    "changes": [],
}
```

def require_keys(obj, keys, path, errors):
if not isinstance(obj, dict):
errors.append("{} must be an object".format(path))
return

```
for key in keys:
    if key not in obj:
        errors.append("{} missing required key `{}`".format(path, key))
```

def require_string(value, path, errors, allow_empty=True):
if not isinstance(value, str):
errors.append("{} must be a string".format(path))
return

```
if not allow_empty and not value.strip():
    errors.append("{} must not be empty".format(path))
```

def require_string_list(value, path, errors):
if not isinstance(value, list):
errors.append("{} must be a list".format(path))
return

```
for i, item in enumerate(value):
    if not isinstance(item, str):
        errors.append("{}[{}] must be a string".format(path, i))
```

def require_bool(value, path, errors):
if not isinstance(value, bool):
errors.append("{} must be boolean".format(path))

def find_item(items, item_id, required=True):
for item in items:
if item.get("id") == item_id:
return item

```
if required:
    raise EvolutionError("ENTITY_NOT_FOUND: {}".format(item_id))

return None
```

def find_task(tasks_state, task_id):
if not isinstance(tasks_state, dict):
return None

```
for task in tasks_state.get("tasks", []):
    if task.get("id") == task_id:
        return task

return None
```

def next_id(prefix, items):
max_num = 0
head = prefix + "-"

```
for item in items:
    item_id = str(item.get("id", ""))

    if item_id.startswith(head):
        suffix = item_id[len(head):]

        if suffix.isdigit():
            max_num = max(max_num, int(suffix))

return "{}-{:03d}".format(prefix, max_num + 1)
```

def next_order(items):
if not items:
return 1

```
return max(int(x.get("order", 0)) for x in items) + 1
```

def normalize_bool_text(value):
if isinstance(value, bool):
return value

```
normalized = str(value).strip().lower()

if normalized in {"1", "true", "yes", "y", "on"}:
    return True

if normalized in {"0", "false", "no", "n", "off"}:
    return False

raise EvolutionError("INVALID_BOOLEAN: {}".format(value))
```

def ensure_status_transition(current, new):
if new not in CHANGE_STATUSES:
raise EvolutionError("INVALID_STATUS: {}".format(new))

```
if current == new:
    return

if new not in CHANGE_STATUS_TRANSITIONS.get(current, set()):
    raise EvolutionError("INVALID_STATUS_TRANSITION: {} -> {}".format(current, new))
```

def ensure_change_content_mutable(change):
if change.get("status") in {"accepted", "rejected", "superseded", "archived"}:
raise EvolutionError(
"CHANGE_IS_IMMUTABLE: {} status is {}".format(
change.get("id"),
change.get("status"),
)
)

def validate_task_refs_for_changes(state, tasks_state, check_task_refs=True):
errors = []

```
linked_task_ids = []

for change in state.get("changes", []):
    for task_id in change.get("linked_tasks", []):
        linked_task_ids.append((change, task_id))

if not linked_task_ids:
    return errors

if not check_task_refs:
    return errors

if tasks_state is None:
    errors.append("tasks.json is required when changes link tasks")
    return errors

if tasks_state.get("schema_version") != TASK_SCHEMA_VERSION:
    errors.append("tasks.schema_version must be {}".format(TASK_SCHEMA_VERSION))

for change, task_id in linked_task_ids:
    task = find_task(tasks_state, task_id)

    if task is None:
        errors.append(
            "change {} links missing task: {}".format(
                change.get("id"),
                task_id,
            )
        )
        continue

    if change.get("status") == "accepted" and task.get("status") not in TASK_DONE_STATUSES:
        errors.append(
            "accepted change {} links non-completed task {} ({})".format(
                change.get("id"),
                task_id,
                task.get("status"),
            )
        )

return errors
```

def validate_evolution(state, tasks_state=None, check_task_refs=True):
errors = []

```
require_keys(
    state,
    [
        "schema_version",
        "revision",
        "created_at",
        "updated_at",
        "changes",
    ],
    "evolution_state",
    errors,
)

if errors:
    return errors

if state.get("schema_version") != EVOLUTION_SCHEMA_VERSION:
    errors.append("schema_version must be {}".format(EVOLUTION_SCHEMA_VERSION))

if not isinstance(state.get("revision"), int) or state.get("revision") < 0:
    errors.append("revision must be a non-negative integer")

changes = state.get("changes")

if not isinstance(changes, list):
    errors.append("changes must be a list")
    changes = []

change_ids = set()

for i, change in enumerate(changes):
    path = "changes[{}]".format(i)

    require_keys(
        change,
        [
            "id",
            "title",
            "status",
            "change_type",
            "rationale",
            "problem",
            "proposal",
            "affected_areas",
            "affected_files",
            "risks",
            "impact",
            "migration_required",
            "backward_compatibility",
            "linked_tasks",
            "implementation_waived",
            "implementation_waiver_reason",
            "superseded_by",
            "owner_approved_by",
            "owner_approved_at",
            "approval_notes",
            "accepted_by",
            "accepted_at",
            "acceptance_notes",
            "notes",
            "priority",
            "order",
            "created_at",
            "updated_at",
        ],
        path,
        errors,
    )

    change_id = change.get("id")

    if change_id in change_ids:
        errors.append("duplicate change id: {}".format(change_id))

    change_ids.add(change_id)

    require_string(change.get("id"), path + ".id", errors, allow_empty=False)
    require_string(change.get("title"), path + ".title", errors, allow_empty=False)
    require_string(change.get("rationale"), path + ".rationale", errors)
    require_string(change.get("problem"), path + ".problem", errors)
    require_string(change.get("proposal"), path + ".proposal", errors)
    require_string(change.get("backward_compatibility"), path + ".backward_compatibility", errors)
    require_string(change.get("superseded_by"), path + ".superseded_by", errors)
    require_string(change.get("owner_approved_by"), path + ".owner_approved_by", errors)
    require_string(change.get("owner_approved_at"), path + ".owner_approved_at", errors)
    require_string(change.get("approval_notes"), path + ".approval_notes", errors)
    require_string(change.get("accepted_by"), path + ".accepted_by", errors)
    require_string(change.get("accepted_at"), path + ".accepted_at", errors)
    require_string(change.get("acceptance_notes"), path + ".acceptance_notes", errors)
    require_string(change.get("implementation_waiver_reason"), path + ".implementation_waiver_reason", errors)

    if change.get("status") not in CHANGE_STATUSES:
        errors.append("{}.status is invalid: {}".format(path, change.get("status")))

    if change.get("change_type") not in CHANGE_TYPES:
        errors.append("{}.change_type is invalid: {}".format(path, change.get("change_type")))

    if change.get("backward_compatibility") not in COMPATIBILITY_VALUES:
        errors.append(
            "{}.backward_compatibility is invalid: {}".format(
                path,
                change.get("backward_compatibility"),
            )
        )

    require_bool(change.get("migration_required"), path + ".migration_required", errors)
    require_bool(change.get("implementation_waived"), path + ".implementation_waived", errors)

    if not isinstance(change.get("priority"), int):
        errors.append("{}.priority must be integer".format(path))

    if not isinstance(change.get("order"), int):
        errors.append("{}.order must be integer".format(path))

    for field in CHANGE_LIST_FIELDS:
        require_string_list(change.get(field), path + "." + field, errors)

    if change.get("status") in {"approved", "in_progress", "in_review", "changes_requested", "accepted"}:
        if not change.get("owner_approved_by") or not change.get("owner_approved_at"):
            errors.append("{} approved/evolving change must have owner_approved_by and owner_approved_at".format(path))

    if change.get("status") == "accepted":
        if not change.get("accepted_by") or not change.get("accepted_at"):
            errors.append("{} accepted change must have accepted_by and accepted_at".format(path))

        if not change.get("linked_tasks") and not change.get("implementation_waived"):
            errors.append("{} accepted change must have linked_tasks or implementation_waived=true".format(path))

    if change.get("implementation_waived") and not change.get("implementation_waiver_reason"):
        errors.append("{} implementation_waived change must have implementation_waiver_reason".format(path))

    if change.get("status") == "superseded":
        if not change.get("superseded_by"):
            errors.append("{} superseded change must have superseded_by".format(path))
        elif change.get("superseded_by") == change.get("id"):
            errors.append("{} cannot supersede itself".format(path))

for i, change in enumerate(changes):
    superseded_by = change.get("superseded_by")

    if superseded_by and superseded_by not in change_ids:
        errors.append("changes[{}].superseded_by references missing change: {}".format(i, superseded_by))

errors.extend(validate_task_refs_for_changes(state, tasks_state, check_task_refs=check_task_refs))

return errors
```

def require_valid_evolution(state, tasks_state=None, check_task_refs=True):
errors = validate_evolution(state, tasks_state=tasks_state, check_task_refs=check_task_refs)

```
if errors:
    raise EvolutionError("VALIDATION_FAILED:\n- " + "\n- ".join(errors))
```

def sort_changes(changes):
return sorted(
changes,
key=lambda x: (x.get("order", 0), x.get("id", "")),
)

def markdown_list(lines, items, empty_text):
if not items:
lines.append(empty_text)
lines.append("")
return

```
for item in items:
    lines.append("- {}".format(item))

lines.append("")
```

def render_evolution_markdown(state):
lines = []

```
lines.append("<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->")
lines.append("<!-- Source: AI_PROJECT/state/evolution.json -->")
lines.append("")
lines.append("# AI Development System Evolution")
lines.append("")
lines.append("Revision: `{}`".format(state.get("revision", 0)))
lines.append("Changes: `{}`".format(len(state.get("changes", []))))
lines.append("")

changes = sort_changes(state.get("changes", []))

if not changes:
    lines.append("_No evolution changes defined._")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"

counts = {}

for change in changes:
    counts[change.get("status")] = counts.get(change.get("status"), 0) + 1

lines.append("## Summary")
lines.append("")

for status in sorted(counts):
    lines.append("- `{}`: {}".format(status, counts[status]))

lines.append("")
lines.append("## Changes")
lines.append("")

for change in changes:
    lines.append("### {} — {}".format(change.get("id"), change.get("title")))
    lines.append("")
    lines.append("Status: `{}`  ".format(change.get("status")))
    lines.append("Type: `{}`  ".format(change.get("change_type")))
    lines.append("Priority: `{}`  ".format(change.get("priority")))
    lines.append("Backward compatibility: `{}`  ".format(change.get("backward_compatibility")))
    lines.append("Migration required: `{}`  ".format(str(change.get("migration_required", False)).lower()))
    lines.append("")

    if change.get("problem"):
        lines.append("Problem:")
        lines.append("")
        lines.append(change.get("problem"))
        lines.append("")

    if change.get("proposal"):
        lines.append("Proposal:")
        lines.append("")
        lines.append(change.get("proposal"))
        lines.append("")

    if change.get("rationale"):
        lines.append("Rationale:")
        lines.append("")
        lines.append(change.get("rationale"))
        lines.append("")

    if change.get("owner_approved_by"):
        lines.append("Approved by: `{}` at `{}`  ".format(change.get("owner_approved_by"), change.get("owner_approved_at")))

        if change.get("approval_notes"):
            lines.append("Approval notes: {}  ".format(change.get("approval_notes")))

        lines.append("")

    if change.get("accepted_by"):
        lines.append("Accepted by: `{}` at `{}`  ".format(change.get("accepted_by"), change.get("accepted_at")))

        if change.get("acceptance_notes"):
            lines.append("Acceptance notes: {}  ".format(change.get("acceptance_notes")))

        lines.append("")

    if change.get("superseded_by"):
        lines.append("Superseded by: `{}`".format(change.get("superseded_by")))
        lines.append("")

    if change.get("implementation_waived"):
        lines.append("Implementation waived: `true`  ")
        lines.append("Waiver reason: {}".format(change.get("implementation_waiver_reason") or "not specified"))
        lines.append("")

    for field, title in CHANGE_LIST_FIELDS.items():
        values = change.get(field, [])

        if values:
            lines.append(title + ":")
            lines.append("")

            for item in values:
                lines.append("- {}".format(item))

            lines.append("")

return "\n".join(lines).rstrip() + "\n"
```

def render_evolution(root, state, tasks_state=None, check_task_refs=True):
require_valid_evolution(state, tasks_state=tasks_state, check_task_refs=check_task_refs)
atomic_write_text(generated_evolution_path(root), render_evolution_markdown(state))

def mutate(args, command, entity_type, entity_id, payload, mutator, check_task_refs=True):
root = repo_root(args)

```
ensure_project_dirs(root)

state = load_evolution(root)
tasks_state = load_tasks(root, required=False)

require_valid_evolution(state, tasks_state=tasks_state, check_task_refs=check_task_refs)

revision_before = state.get("revision", 0)

result = mutator(state, tasks_state) or {}

state["revision"] = revision_before + 1
state["updated_at"] = utc_now()

require_valid_evolution(state, tasks_state=tasks_state, check_task_refs=check_task_refs)

save_evolution(root, state)

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

render_evolution(root, state, tasks_state=tasks_state, check_task_refs=check_task_refs)

print("OK: {} revision {} -> {}".format(command, revision_before, state["revision"]))

if result.get("message"):
    print(result["message"])
```

def print_json(data):
print(json.dumps(data, ensure_ascii=False, indent=2))

def new_change_item(change_id, title, change_type, priority, order, status, problem, proposal, rationale, compatibility, migration_required):
now = utc_now()

```
return {
    "id": change_id,
    "title": title,
    "status": status,
    "change_type": change_type,
    "rationale": rationale or "",
    "problem": problem or "",
    "proposal": proposal or "",
    "affected_areas": [],
    "affected_files": [],
    "risks": [],
    "impact": [],
    "migration_required": bool(migration_required),
    "backward_compatibility": compatibility,
    "linked_tasks": [],
    "implementation_waived": False,
    "implementation_waiver_reason": "",
    "superseded_by": "",
    "owner_approved_by": "",
    "owner_approved_at": "",
    "approval_notes": "",
    "accepted_by": "",
    "accepted_at": "",
    "acceptance_notes": "",
    "notes": [],
    "priority": priority,
    "order": order,
    "created_at": now,
    "updated_at": now,
}
```

def cmd_init(args):
root = repo_root(args)

```
ensure_project_dirs(root)

path = evolution_path(root)
events_path = evolution_events_path(root)

if path.exists() and not args.force:
    raise EvolutionError("EVOLUTION_ALREADY_EXISTS: use --force to overwrite")

if path.exists() and args.force and events_path.exists() and not args.reset_events:
    raise EvolutionError("EVOLUTION_EVENTS_ALREADY_EXIST: use --reset-events with --force to reset audit log")

if args.force and args.reset_events and events_path.exists():
    backup = events_path.with_name(events_path.name + "." + datetime.now().strftime("%Y%m%d%H%M%S") + ".bak")
    os.replace(str(events_path), str(backup))

state = default_evolution_state()

require_valid_evolution(state, tasks_state=None, check_task_refs=False)
save_evolution(root, state)

append_event(
    root=root,
    actor=args.actor,
    command="evolution.init",
    entity_type="evolution",
    entity_id="evolution",
    revision_before=None,
    revision_after=state["revision"],
    payload={"force": bool(args.force), "reset_events": bool(args.reset_events)},
)

render_evolution(root, state, tasks_state=None, check_task_refs=False)

print("OK: initialized {}".format(path))
```

def cmd_show(args):
root = repo_root(args)
state = load_evolution(root)
tasks_state = load_tasks(root, required=False)
require_valid_evolution(state, tasks_state=tasks_state, check_task_refs=not args.skip_task_check)

```
if args.json:
    print_json(state)
    return

print("Evolution revision: {}".format(state.get("revision")))
print("Changes:            {}".format(len(state.get("changes", []))))

counts = {}

for change in state.get("changes", []):
    counts[change.get("status")] = counts.get(change.get("status"), 0) + 1

if counts:
    print("\nBy status:")

    for status in sorted(counts):
        print("  {}: {}".format(status, counts[status]))
```

def cmd_status(args):
root = repo_root(args)

```
print("Root:       {}".format(root))
print("Evolution:  {}".format(evolution_path(root)))
print("Tasks:      {}".format(tasks_path(root)))
print("Events:     {}".format(evolution_events_path(root)))
print("Generated:  {}".format(generated_evolution_path(root)))

state = load_evolution(root)
tasks_state = load_tasks(root, required=False)
errors = validate_evolution(state, tasks_state=tasks_state, check_task_refs=not args.skip_task_check)

print("Revision:   {}".format(state.get("revision")))
print("Valid:      {}".format("yes" if not errors else "no"))

if errors:
    for error in errors:
        print("- {}".format(error))
```

def cmd_validate(args):
root = repo_root(args)
state = load_evolution(root)
tasks_state = load_tasks(root, required=False)
errors = validate_evolution(state, tasks_state=tasks_state, check_task_refs=not args.skip_task_check)

```
if errors:
    print("VALIDATION_FAILED:", file=sys.stderr)

    for error in errors:
        print("- {}".format(error), file=sys.stderr)

    return 1

print("OK: evolution is valid")
return 0
```

def cmd_render(args):
root = repo_root(args)
state = load_evolution(root)
tasks_state = load_tasks(root, required=False)

```
render_evolution(root, state, tasks_state=tasks_state, check_task_refs=not args.skip_task_check)

print("OK: rendered {}".format(generated_evolution_path(root)))
```

def cmd_check_generated(args):
root = repo_root(args)
state = load_evolution(root)
tasks_state = load_tasks(root, required=False)

```
require_valid_evolution(state, tasks_state=tasks_state, check_task_refs=not args.skip_task_check)

expected = render_evolution_markdown(state)
path = generated_evolution_path(root)

if not path.exists():
    print("GENERATED_CHECK_FAILED:", file=sys.stderr)
    print("- missing generated file: {}".format(path), file=sys.stderr)
    return 1

actual = path.read_text(encoding="utf-8")

if actual != expected:
    print("GENERATED_CHECK_FAILED:", file=sys.stderr)
    print("- outdated generated file: {}".format(path), file=sys.stderr)
    return 1

print("OK: generated evolution file is up to date")
return 0
```

def cmd_audit(args):
path = evolution_events_path(repo_root(args))

```
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
```

def cmd_change_list(args):
root = repo_root(args)
state = load_evolution(root)
tasks_state = load_tasks(root, required=False)
require_valid_evolution(state, tasks_state=tasks_state, check_task_refs=not args.skip_task_check)

```
changes = state.get("changes", [])

if args.status:
    changes = [c for c in changes if c.get("status") == args.status]

if args.type:
    changes = [c for c in changes if c.get("change_type") == args.type]

changes = sort_changes(changes)

if args.json:
    print_json(changes)
    return

if not changes:
    print("No changes.")
    return

for change in changes:
    print(
        "{} [{}] ({}) {}".format(
            change.get("id"),
            change.get("status"),
            change.get("change_type"),
            change.get("title"),
        )
    )
```

def cmd_change_show(args):
state = load_evolution(repo_root(args))
change = find_item(state.get("changes", []), args.change_id)
print_json(change)

def cmd_change_create(args):
def apply(state, tasks_state):
change_id = next_id("CHG", state["changes"])

```
    item = new_change_item(
        change_id=change_id,
        title=args.title,
        change_type=args.type,
        priority=args.priority,
        order=next_order(state["changes"]),
        status=args.status,
        problem=args.problem,
        proposal=args.proposal,
        rationale=args.rationale,
        compatibility=args.compatibility,
        migration_required=args.migration_required,
    )

    state["changes"].append(item)

    return {
        "entity_id": change_id,
        "payload": {"change_id": change_id},
        "message": "Created: {}".format(change_id),
    }

mutate(
    args=args,
    command="change.create",
    entity_type="change",
    entity_id="NEW",
    payload={
        "title": args.title,
        "type": args.type,
        "status": args.status,
        "priority": args.priority,
    },
    mutator=apply,
    check_task_refs=not args.skip_task_check,
)
```

def set_change_text_field(args, field, command):
def apply(state, tasks_state):
change = find_item(state["changes"], args.change_id)
ensure_change_content_mutable(change)

```
    change[field] = args.text
    change["updated_at"] = utc_now()

mutate(
    args=args,
    command=command,
    entity_type="change",
    entity_id=args.change_id,
    payload={field: args.text},
    mutator=apply,
    check_task_refs=not args.skip_task_check,
)
```

def cmd_change_rename(args):
def apply(state, tasks_state):
change = find_item(state["changes"], args.change_id)
ensure_change_content_mutable(change)

```
    change["title"] = args.title
    change["updated_at"] = utc_now()

mutate(
    args=args,
    command="change.rename",
    entity_type="change",
    entity_id=args.change_id,
    payload={"title": args.title},
    mutator=apply,
    check_task_refs=not args.skip_task_check,
)
```

def cmd_change_set_compatibility(args):
def apply(state, tasks_state):
change = find_item(state["changes"], args.change_id)
ensure_change_content_mutable(change)

```
    change["backward_compatibility"] = args.value
    change["updated_at"] = utc_now()

mutate(
    args=args,
    command="change.set_compatibility",
    entity_type="change",
    entity_id=args.change_id,
    payload={"value": args.value},
    mutator=apply,
    check_task_refs=not args.skip_task_check,
)
```

def cmd_change_set_migration(args):
required = normalize_bool_text(args.required)

```
def apply(state, tasks_state):
    change = find_item(state["changes"], args.change_id)
    ensure_change_content_mutable(change)

    change["migration_required"] = required
    change["updated_at"] = utc_now()

mutate(
    args=args,
    command="change.set_migration",
    entity_type="change",
    entity_id=args.change_id,
    payload={"required": required},
    mutator=apply,
    check_task_refs=not args.skip_task_check,
)
```

def change_add_list_item(args, field, command):
def apply(state, tasks_state):
change = find_item(state["changes"], args.change_id)
ensure_change_content_mutable(change)

```
    if args.text in change.setdefault(field, []):
        raise EvolutionError("DUPLICATE_LIST_ITEM: {} already exists in {}".format(args.text, field))

    change.setdefault(field, []).append(args.text)
    change["updated_at"] = utc_now()

mutate(
    args=args,
    command=command,
    entity_type="change",
    entity_id=args.change_id,
    payload={"field": field, "text": args.text},
    mutator=apply,
    check_task_refs=not args.skip_task_check,
)
```

def change_remove_list_item(args, field, command):
def apply(state, tasks_state):
change = find_item(state["changes"], args.change_id)
ensure_change_content_mutable(change)

```
    items = change.setdefault(field, [])
    index = args.index - 1

    if index < 0 or index >= len(items):
        raise EvolutionError("INDEX_OUT_OF_RANGE")

    removed = items.pop(index)
    change["updated_at"] = utc_now()

    return {"payload": {"field": field, "index": args.index, "removed": removed}}

mutate(
    args=args,
    command=command,
    entity_type="change",
    entity_id=args.change_id,
    payload={},
    mutator=apply,
    check_task_refs=not args.skip_task_check,
)
```

def cmd_change_transition(args):
def apply(state, tasks_state):
change = find_item(state["changes"], args.change_id)
old = change.get("status")

```
    ensure_status_transition(old, args.to)

    if args.to == "approved":
        raise EvolutionError("USE_CHANGE_APPROVE_COMMAND_FOR_APPROVAL")

    if args.to == "accepted":
        raise EvolutionError("USE_CHANGE_ACCEPT_COMMAND_FOR_ACCEPTANCE")

    if args.to == "superseded":
        if not args.superseded_by:
            raise EvolutionError("SUPERSEDED_CHANGE_REQUIRES_SUPERSEDED_BY")

        if args.superseded_by == args.change_id:
            raise EvolutionError("CHANGE_CANNOT_SUPERSEDE_ITSELF")

        find_item(state["changes"], args.superseded_by)
        change["superseded_by"] = args.superseded_by

    change["status"] = args.to
    change["updated_at"] = utc_now()

    return {"payload": {"from": old, "to": args.to, "superseded_by": args.superseded_by or ""}}

mutate(
    args=args,
    command="change.transition",
    entity_type="change",
    entity_id=args.change_id,
    payload={"to": args.to},
    mutator=apply,
    check_task_refs=not args.skip_task_check,
)
```

def cmd_change_approve(args):
def apply(state, tasks_state):
change = find_item(state["changes"], args.change_id)

```
    ensure_status_transition(change.get("status"), "approved")

    change["status"] = "approved"
    change["owner_approved_by"] = args.by or args.actor
    change["owner_approved_at"] = utc_now()
    change["approval_notes"] = args.notes or ""
    change["updated_at"] = utc_now()

    return {"payload": {"by": change["owner_approved_by"], "notes": args.notes or ""}}

mutate(
    args=args,
    command="change.approve",
    entity_type="change",
    entity_id=args.change_id,
    payload={},
    mutator=apply,
    check_task_refs=not args.skip_task_check,
)
```

def cmd_change_link_task(args):
def apply(state, tasks_state):
change = find_item(state["changes"], args.change_id)
ensure_change_content_mutable(change)

```
    if not args.skip_task_check:
        if tasks_state is None:
            raise EvolutionError("TASKS_NOT_INITIALIZED: cannot link task without tasks.json")

        if find_task(tasks_state, args.task) is None:
            raise EvolutionError("TASK_NOT_FOUND: {}".format(args.task))

    if args.task in change.setdefault("linked_tasks", []):
        raise EvolutionError("TASK_ALREADY_LINKED: {}".format(args.task))

    change["linked_tasks"].append(args.task)
    change["updated_at"] = utc_now()

mutate(
    args=args,
    command="change.link_task",
    entity_type="change",
    entity_id=args.change_id,
    payload={"task": args.task},
    mutator=apply,
    check_task_refs=not args.skip_task_check,
)
```

def cmd_change_unlink_task(args):
def apply(state, tasks_state):
change = find_item(state["changes"], args.change_id)
ensure_change_content_mutable(change)

```
    tasks = change.setdefault("linked_tasks", [])

    if args.task not in tasks:
        raise EvolutionError("TASK_NOT_LINKED: {}".format(args.task))

    tasks.remove(args.task)
    change["updated_at"] = utc_now()

mutate(
    args=args,
    command="change.unlink_task",
    entity_type="change",
    entity_id=args.change_id,
    payload={"task": args.task},
    mutator=apply,
    check_task_refs=not args.skip_task_check,
)
```

def cmd_change_waive_tasks(args):
def apply(state, tasks_state):
change = find_item(state["changes"], args.change_id)
ensure_change_content_mutable(change)

```
    change["implementation_waived"] = True
    change["implementation_waiver_reason"] = args.reason
    change["updated_at"] = utc_now()

mutate(
    args=args,
    command="change.waive_tasks",
    entity_type="change",
    entity_id=args.change_id,
    payload={"reason": args.reason},
    mutator=apply,
    check_task_refs=not args.skip_task_check,
)
```

def cmd_change_accept(args):
def apply(state, tasks_state):
change = find_item(state["changes"], args.change_id)

```
    ensure_status_transition(change.get("status"), "accepted")

    if args.waive_tasks:
        change["implementation_waived"] = True

        if args.waiver_reason:
            change["implementation_waiver_reason"] = args.waiver_reason
        elif not change.get("implementation_waiver_reason"):
            change["implementation_waiver_reason"] = "Accepted with explicit task waiver."

    if not change.get("linked_tasks") and not change.get("implementation_waived"):
        raise EvolutionError("CHANGE_ACCEPTANCE_REQUIRES_LINKED_TASK_OR_WAIVER")

    if change.get("linked_tasks") and not args.skip_task_check:
        if tasks_state is None:
            raise EvolutionError("TASKS_NOT_INITIALIZED: cannot verify linked tasks")

        blocking = []

        for task_id in change.get("linked_tasks", []):
            task = find_task(tasks_state, task_id)

            if task is None:
                blocking.append("{} missing".format(task_id))
            elif task.get("status") not in TASK_DONE_STATUSES:
                blocking.append("{} status is {}".format(task_id, task.get("status")))

        if blocking:
            raise EvolutionError("LINKED_TASKS_NOT_COMPLETE: " + "; ".join(blocking))

    change["status"] = "accepted"
    change["accepted_by"] = args.by or args.actor
    change["accepted_at"] = utc_now()
    change["acceptance_notes"] = args.notes or ""
    change["updated_at"] = utc_now()

    return {
        "payload": {
            "by": change["accepted_by"],
            "notes": args.notes or "",
            "waive_tasks": bool(args.waive_tasks),
        }
    }

mutate(
    args=args,
    command="change.accept",
    entity_type="change",
    entity_id=args.change_id,
    payload={},
    mutator=apply,
    check_task_refs=not args.skip_task_check,
)
```

def cmd_change_archive(args):
args.to = "archived"
args.superseded_by = ""
cmd_change_transition(args)

def add_common_args(parser):
parser.add_argument(
"--root",
default=".",
help="Repository/project root. Default: current directory.",
)

```
parser.add_argument(
    "--actor",
    default=os.environ.get("AI_DEV_ACTOR", "human_owner"),
    help="Audit actor. Default: AI_DEV_ACTOR or human_owner.",
)
```

def add_skip_task_check(parser):
parser.add_argument(
"--skip-task-check",
action="store_true",
help="Validate evolution without checking linked tasks against AI_PROJECT/state/tasks.json.",
)

def add_list_mutation_commands(change_sub, add_name, remove_name, field, add_command, remove_command, add_help):
p = change_sub.add_parser(add_name, help=add_help)
p.add_argument("change_id")
p.add_argument("--text", required=True)
add_skip_task_check(p)
p.set_defaults(func=lambda a, f=field, c=add_command: change_add_list_item(a, f, c))

```
p = change_sub.add_parser(remove_name, help="Remove item from {}".format(field))
p.add_argument("change_id")
p.add_argument("--index", type=int, required=True)
add_skip_task_check(p)
p.set_defaults(func=lambda a, f=field, c=remove_command: change_remove_list_item(a, f, c))
```

def build_parser():
parser = argparse.ArgumentParser(
description="Strict evolution.json control CLI for AI Development System"
)

```
add_common_args(parser)

sub = parser.add_subparsers(dest="command", required=True)

p = sub.add_parser("init", help="Initialize AI_PROJECT/state/evolution.json")
p.add_argument("--force", action="store_true", help="Overwrite existing evolution.json")
p.add_argument("--reset-events", action="store_true", help="Backup and reset existing evolution event log when using --force")
p.set_defaults(func=cmd_init)

p = sub.add_parser("show", help="Show evolution state summary")
p.add_argument("--json", action="store_true")
add_skip_task_check(p)
p.set_defaults(func=cmd_show)

p = sub.add_parser("status", help="Show file paths and validation status")
add_skip_task_check(p)
p.set_defaults(func=cmd_status)

p = sub.add_parser("validate", help="Validate evolution.json and linked task references")
add_skip_task_check(p)
p.set_defaults(func=cmd_validate)

p = sub.add_parser("render", help="Render generated evolution Markdown")
add_skip_task_check(p)
p.set_defaults(func=cmd_render)

p = sub.add_parser("check-generated", help="Check generated evolution Markdown is up to date")
add_skip_task_check(p)
p.set_defaults(func=cmd_check_generated)

p = sub.add_parser("audit", help="Show evolution audit events")
p.add_argument("--last", type=int, default=20)
p.add_argument("--entity", help="Filter by entity id")
p.set_defaults(func=cmd_audit)

change = sub.add_parser("change", help="Manage evolution Change Proposals")
change_sub = change.add_subparsers(dest="change_command", required=True)

p = change_sub.add_parser("list")
p.add_argument("--status", choices=sorted(CHANGE_STATUSES))
p.add_argument("--type", choices=sorted(CHANGE_TYPES))
p.add_argument("--json", action="store_true")
add_skip_task_check(p)
p.set_defaults(func=cmd_change_list)

p = change_sub.add_parser("show")
p.add_argument("change_id")
p.set_defaults(func=cmd_change_show)

p = change_sub.add_parser("create")
p.add_argument("--title", required=True)
p.add_argument("--type", required=True, choices=sorted(CHANGE_TYPES))
p.add_argument("--status", choices=sorted(CHANGE_STATUSES), default="proposed")
p.add_argument("--priority", type=int, default=1)
p.add_argument("--problem", default="")
p.add_argument("--proposal", default="")
p.add_argument("--rationale", default="")
p.add_argument("--compatibility", choices=sorted(COMPATIBILITY_VALUES), default="unknown")
p.add_argument("--migration-required", action="store_true")
add_skip_task_check(p)
p.set_defaults(func=cmd_change_create)

p = change_sub.add_parser("rename")
p.add_argument("change_id")
p.add_argument("--title", required=True)
add_skip_task_check(p)
p.set_defaults(func=cmd_change_rename)

for command_name, field, event_name in [
    ("set-problem", "problem", "change.set_problem"),
    ("set-rationale", "rationale", "change.set_rationale"),
    ("set-proposal", "proposal", "change.set_proposal"),
]:
    p = change_sub.add_parser(command_name)
    p.add_argument("change_id")
    p.add_argument("--text", required=True)
    add_skip_task_check(p)
    p.set_defaults(func=lambda a, f=field, c=event_name: set_change_text_field(a, f, c))

p = change_sub.add_parser("set-compatibility")
p.add_argument("change_id")
p.add_argument("--value", required=True, choices=sorted(COMPATIBILITY_VALUES))
add_skip_task_check(p)
p.set_defaults(func=cmd_change_set_compatibility)

p = change_sub.add_parser("set-migration")
p.add_argument("change_id")
p.add_argument("--required", required=True)
add_skip_task_check(p)
p.set_defaults(func=cmd_change_set_migration)

p = change_sub.add_parser("transition")
p.add_argument("change_id")
p.add_argument("--to", required=True, choices=sorted(CHANGE_STATUSES))
p.add_argument("--superseded-by", default="")
add_skip_task_check(p)
p.set_defaults(func=cmd_change_transition)

p = change_sub.add_parser("approve")
p.add_argument("change_id")
p.add_argument("--by", default="")
p.add_argument("--notes", default="")
add_skip_task_check(p)
p.set_defaults(func=cmd_change_approve)

p = change_sub.add_parser("link-task")
p.add_argument("change_id")
p.add_argument("--task", required=True)
add_skip_task_check(p)
p.set_defaults(func=cmd_change_link_task)

p = change_sub.add_parser("unlink-task")
p.add_argument("change_id")
p.add_argument("--task", required=True)
add_skip_task_check(p)
p.set_defaults(func=cmd_change_unlink_task)

p = change_sub.add_parser("waive-tasks")
p.add_argument("change_id")
p.add_argument("--reason", required=True)
add_skip_task_check(p)
p.set_defaults(func=cmd_change_waive_tasks)

p = change_sub.add_parser("accept")
p.add_argument("change_id")
p.add_argument("--by", default="")
p.add_argument("--notes", default="")
p.add_argument("--waive-tasks", action="store_true")
p.add_argument("--waiver-reason", default="")
add_skip_task_check(p)
p.set_defaults(func=cmd_change_accept)

p = change_sub.add_parser("archive")
p.add_argument("change_id")
add_skip_task_check(p)
p.set_defaults(func=cmd_change_archive)

add_list_mutation_commands(
    change_sub,
    "add-affected-area",
    "remove-affected-area",
    "affected_areas",
    "change.add_affected_area",
    "change.remove_affected_area",
    "Add affected area",
)
add_list_mutation_commands(
    change_sub,
    "add-affected-file",
    "remove-affected-file",
    "affected_files",
    "change.add_affected_file",
    "change.remove_affected_file",
    "Add affected file/path",
)
add_list_mutation_commands(
    change_sub,
    "add-risk",
    "remove-risk",
    "risks",
    "change.add_risk",
    "change.remove_risk",
    "Add risk",
)
add_list_mutation_commands(
    change_sub,
    "add-impact",
    "remove-impact",
    "impact",
    "change.add_impact",
    "change.remove_impact",
    "Add impact item",
)
add_list_mutation_commands(
    change_sub,
    "add-note",
    "remove-note",
    "notes",
    "change.add_note",
    "change.remove_note",
    "Add note",
)

return parser
```

def main(argv=None):
parser = build_parser()
args = parser.parse_args(argv)

```
try:
    result = args.func(args)
    return int(result or 0)
except EvolutionError as e:
    print("ERROR: {}".format(e), file=sys.stderr)
    return 2
except KeyboardInterrupt:
    print("Interrupted", file=sys.stderr)
    return 130
```

if **name** == "**main**":
sys.exit(main())

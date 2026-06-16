#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
codexctl.py - strict CLI gateway for Codex prompt packages.

Builds executable Codex prompt packages from existing project-control state.
It does not create Tasks or Evolution Changes; use taskctl.py and
evolutionctl.py for source-of-truth state.

Files:
  AI_PROJECT/state/current_execution.json
  AI_PROJECT/events/codex-events.jsonl
  AI_PROJECT/generated/CODEX_PROMPT.md
  AI_PROJECT/generated/CODEX_STATUS.md
"""

import argparse
import json
import os
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path


CODEX_SCHEMA_VERSION = 1

TASK_EXECUTABLE_STATUSES = {"ready", "approved", "in_progress", "in_review"}
CHANGE_EXECUTABLE_STATUSES = {"ready", "approved", "in_progress", "in_review"}

READY_STATUS = "ready"
BLOCKED_STATUS = "blocked"

CODEX_READY = "CODEX_READY"
CODEX_BLOCKED = "CODEX_BLOCKED"
CODEX_NO_PROMPT_PACKAGE = "CODEX_NO_PROMPT_PACKAGE"
CODEX_NO_EXECUTABLE_SOURCE = "CODEX_NO_EXECUTABLE_SOURCE"
CODEX_SOURCE_NOT_READY = "CODEX_SOURCE_NOT_READY"
CODEX_ENTITY_NOT_FOUND = "CODEX_ENTITY_NOT_FOUND"
CODEX_VALIDATION_FAILED = "CODEX_VALIDATION_FAILED"


class CodexError(Exception):
    def __init__(
        self,
        code,
        message,
        source_type="",
        source_id="",
        source_status="",
        details=None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.source_type = source_type
        self.source_id = source_id
        self.source_status = source_status
        self.details = details or []


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


def current_execution_path(root):
    return state_dir(root) / "current_execution.json"


def codex_events_path(root):
    return events_dir(root) / "codex-events.jsonl"


def generated_prompt_path(root):
    return generated_dir(root) / "CODEX_PROMPT.md"


def generated_status_path(root):
    return generated_dir(root) / "CODEX_STATUS.md"


def tasks_path(root):
    return state_dir(root) / "tasks.json"


def evolution_path(root):
    return state_dir(root) / "evolution.json"


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
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def read_json(path, missing_code, missing_message):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise CodexError(missing_code, missing_message)
    except json.JSONDecodeError as exc:
        raise CodexError(
            CODEX_VALIDATION_FAILED,
            "INVALID_JSON: {}:{}:{} {}".format(path, exc.lineno, exc.colno, exc.msg),
        )


def load_tasks(root):
    return read_json(
        tasks_path(root),
        CODEX_NO_EXECUTABLE_SOURCE,
        "TASKS_NOT_INITIALIZED: run `python scripts/taskctl.py init` first",
    )


def load_evolution(root):
    return read_json(
        evolution_path(root),
        CODEX_NO_EXECUTABLE_SOURCE,
        "EVOLUTION_NOT_INITIALIZED: run `python scripts/evolutionctl.py init` first",
    )


def load_current_execution(root):
    path = current_execution_path(root)

    if not path.exists():
        return None

    return read_json(
        path,
        CODEX_NO_PROMPT_PACKAGE,
        "CURRENT_EXECUTION_NOT_INITIALIZED",
    )


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
    path = codex_events_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(line)


def find_item(items, item_id):
    for item in items:
        if item.get("id") == item_id:
            return item

    return None


def as_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]

    if isinstance(value, str):
        return [value] if value.strip() else []

    return [str(value)]


def first_text(source, names, default=""):
    for name in names:
        value = source.get(name)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return default


def first_list(source, names):
    for name in names:
        values = as_list(source.get(name))

        if values:
            return values

    return []


def markdown_list(lines, items, empty_text):
    if not items:
        lines.append("- {}".format(empty_text))
        return

    for item in items:
        lines.append("- {}".format(item))


def validate_required(source_label, fields):
    missing = [name for name, value in fields if not value]

    if missing:
        raise CodexError(
            CODEX_VALIDATION_FAILED,
            "{} missing required fields: {}".format(source_label, ", ".join(missing)),
            details=missing,
        )


def task_prompt_model(task):
    title = first_text(task, ["title", "name", "summary"])
    summary = first_text(task, ["summary", "description", "body", "details"])
    description = first_text(task, ["description", "body", "details"])
    scope = first_list(task, ["scope", "scopes"])
    out_of_scope = first_list(task, ["out_of_scope", "exclusions"])
    allowed_files = first_list(task, ["allowed_files", "affected_files", "files"])
    acceptance = first_list(task, ["acceptance_criteria", "acceptance", "done_when"])
    verification = first_list(task, ["verification", "checks"])
    review = first_list(task, ["review_instructions", "review", "review_notes"])

    if not verification:
        mode = first_text(task, ["verification_mode"], "standard")
        verification = [
            "Use verification mode `{}`.".format(mode),
            "Run the validation commands required by the task and report results.",
        ]

    validate_required(
        "Task {}".format(task.get("id")),
        [
            ("title", title),
            ("scope", scope),
            ("allowed files", allowed_files),
            ("acceptance criteria", acceptance),
        ],
    )

    return {
        "source_type": "task",
        "source_id": task.get("id"),
        "source_status": task.get("status"),
        "active_role": first_text(task, ["active_role"], "Codex Executor"),
        "active_stage": first_text(task, ["active_stage"], "Implementation of approved bounded task"),
        "active_document": first_text(task, ["active_document"], "AI_PROJECT/state/tasks.json"),
        "expected_result": first_text(task, ["expected_result"], "Task completed according to acceptance criteria."),
        "title": title,
        "summary": summary or title,
        "description": description,
        "scope": scope,
        "out_of_scope": out_of_scope or ["Anything outside the source Task scope."],
        "allowed_files_heading": "Allowed Files",
        "allowed_files": allowed_files,
        "affected_areas": [],
        "implementation_instructions": default_implementation_instructions(),
        "acceptance": acceptance,
        "verification": verification,
        "review": review,
        "status_label": "Task Status",
        "source_label": "Source Task",
    }


def change_prompt_model(change):
    title = first_text(change, ["title", "name", "summary"])
    problem = first_text(change, ["problem", "description", "body", "details"])
    proposal = first_text(change, ["proposal", "summary", "description", "body", "details"])
    rationale = first_text(change, ["rationale"])
    affected_areas = first_list(change, ["affected_areas", "areas", "impacts"])
    allowed_files = first_list(change, ["allowed_files", "affected_files", "files"])
    impacts = first_list(change, ["acceptance_criteria", "acceptance", "done_when", "impact"])
    risks = first_list(change, ["risks"])
    linked_tasks = first_list(change, ["linked_tasks"])

    scope = []

    if proposal:
        scope.append(proposal)

    for area in affected_areas:
        scope.append("Affect area: {}".format(area))

    for task_id in linked_tasks:
        scope.append("Use linked implementation task: {}".format(task_id))

    acceptance = impacts[:]

    if not acceptance and proposal:
        acceptance.append("Implemented proposal: {}".format(proposal))

    acceptance.append("Implementation stays within affected files and preserves lifecycle boundaries.")

    verification = [
        "Run `python -m py_compile scripts/codexctl.py`.",
        "Run `python scripts/codexctl.py --help`.",
        "Run `python scripts/codexctl.py status`.",
        "Run `python scripts/codexctl.py build --change {}`.".format(change.get("id")),
        "Run `python scripts/codexctl.py clear`.",
        "Run relevant evolution and protected-files validation commands.",
    ]

    validate_required(
        "Evolution Change {}".format(change.get("id")),
        [
            ("title", title),
            ("proposal or problem", proposal or problem),
            ("scope", scope),
            ("affected files", allowed_files),
            ("acceptance criteria or impact", acceptance),
        ],
    )

    out_of_scope = [
        "Do not implement unrelated AI Development System changes.",
        "Do not modify source-of-truth project-control state manually.",
        "Do not change governance rules outside the approved Evolution Change.",
    ]

    if risks:
        out_of_scope.append("Do not ignore recorded risks; report unresolved risks explicitly.")

    return {
        "source_type": "evolution_change",
        "source_id": change.get("id"),
        "source_status": change.get("status"),
        "active_role": "Codex Executor",
        "active_stage": "Implementation of approved bounded change",
        "active_document": "AI_PROJECT/state/evolution.json / AI_PROJECT/generated/EVOLUTION.md",
        "expected_result": proposal or title,
        "title": title,
        "summary": problem or proposal or title,
        "description": "\n\n".join([text for text in [proposal, rationale] if text]),
        "scope": scope,
        "out_of_scope": out_of_scope,
        "allowed_files_heading": "Allowed Files / Affected Files",
        "allowed_files": allowed_files,
        "affected_areas": affected_areas,
        "implementation_instructions": default_implementation_instructions(),
        "acceptance": acceptance,
        "verification": verification,
        "review": [
            "Report changed files, commands run, verification result, blockers and risks.",
            "Do not mark the Evolution Change accepted without Human Owner decision.",
        ],
        "status_label": "Change Status",
        "source_label": "Source Evolution Change",
    }


def default_implementation_instructions():
    return [
        "Inspect current files before editing.",
        "Stay within allowed files.",
        "Preserve existing conventions.",
        "Prefer minimal, commit-ready changes.",
        "Do not perform unrelated refactors.",
        "Do not edit AI_PROJECT/state/**, AI_PROJECT/events/** or AI_PROJECT/generated/** manually.",
    ]


def render_prompt(model):
    generated = utc_now()
    lines = []

    lines.append("# Codex Prompt Package")
    lines.append("")
    lines.append("Generated: {}".format(generated))
    lines.append("Source Type: {}".format(model["source_type"]))
    lines.append("Source ID: {}".format(model["source_id"]))
    lines.append("Source Status: {}".format(model["source_status"]))
    lines.append("")
    lines.append("[SYSTEM]")
    lines.append("")
    lines.append("Active Role:")
    lines.append(model["active_role"])
    lines.append("")
    lines.append("Active Stage:")
    lines.append(model["active_stage"])
    lines.append("")
    lines.append("Active Document:")
    lines.append(model["active_document"])
    lines.append("")
    lines.append("Expected Result:")
    lines.append(model["expected_result"])
    lines.append("")
    lines.append("Repository Context:")
    lines.append("This repository is an AI Development System governance control plane.")
    lines.append("Project-control state is managed through Python CLI gateways; generated Markdown is derived output.")
    lines.append("")
    lines.append("Source:")
    lines.append("{}: {}".format(model["source_label"], model["source_id"]))
    lines.append("{}: {}".format(model["status_label"], model["source_status"]))
    lines.append("Title: {}".format(model["title"]))

    if model["summary"]:
        lines.append("")
        lines.append(model["summary"])

    if model["description"]:
        lines.append("")
        lines.append(model["description"])

    lines.append("")
    lines.append("Scope:")
    markdown_list(lines, model["scope"], "No explicit scope defined. Stop and ask before editing.")
    lines.append("")
    lines.append("Out of Scope:")
    markdown_list(lines, model["out_of_scope"], "Anything not required by the source entity.")
    lines.append("")
    lines.append(model["allowed_files_heading"] + ":")
    markdown_list(lines, model["allowed_files"], "No allowed files defined. Do not edit files.")

    if model["affected_areas"]:
        lines.append("")
        lines.append("Affected Areas:")
        markdown_list(lines, model["affected_areas"], "No affected areas defined.")

    lines.append("")
    lines.append("Implementation Instructions:")
    markdown_list(lines, model["implementation_instructions"], "Use existing conventions.")
    lines.append("")
    lines.append("Acceptance Criteria:")
    markdown_list(lines, model["acceptance"], "Source criteria must be satisfied.")
    lines.append("")
    lines.append("Verification:")
    markdown_list(lines, model["verification"], "Run relevant validation commands and report results.")
    lines.append("")
    lines.append("Result Format:")
    lines.append("- Summary")
    lines.append("- Changed files")
    lines.append("- Commands run")
    lines.append("- Verification result")
    lines.append("- Blockers or risks")

    if model["review"]:
        lines.append("")
        lines.append("Review / Result Format Notes:")
        markdown_list(lines, model["review"], "Report review notes.")

    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_status_markdown(state):
    lines = []

    lines.append("<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->")
    lines.append("<!-- Source: AI_PROJECT/state/current_execution.json -->")
    lines.append("")
    lines.append("# Codex Execution Status")
    lines.append("")
    lines.append("Status: `{}`".format(str(state.get("status", BLOCKED_STATUS)).upper()))
    lines.append("Code: `{}`".format(state.get("code") or CODEX_NO_PROMPT_PACKAGE))
    lines.append("Updated: `{}`".format(state.get("updated_at") or ""))
    lines.append("")
    lines.append("Prompt exists: `{}`".format(str(bool(state.get("prompt_exists"))).lower()))
    lines.append("Prompt path: `{}`".format(state.get("prompt_path") or ""))
    lines.append("")
    lines.append("Source type: `{}`".format(state.get("source_type") or "none"))
    lines.append("Source ID: `{}`".format(state.get("source_id") or "none"))
    lines.append("Source status: `{}`".format(state.get("source_status") or "unknown"))
    lines.append("")

    if state.get("blocked_reason"):
        lines.append("Blocked reason:")
        lines.append("")
        lines.append(state.get("blocked_reason"))
        lines.append("")

    details = as_list(state.get("details"))

    if details:
        lines.append("Details:")
        lines.append("")
        markdown_list(lines, details, "No details.")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_execution_state(
    root,
    actor,
    command,
    status,
    code,
    source_type="",
    source_id="",
    source_status="",
    blocked_reason="",
    details=None,
    prompt_text=None,
    remove_prompt=False,
):
    ensure_project_dirs(root)

    previous = load_current_execution(root)
    revision_before = previous.get("revision") if isinstance(previous, dict) else None
    revision_after = (revision_before or 0) + 1
    now = utc_now()
    prompt_path = generated_prompt_path(root)

    if remove_prompt and prompt_path.exists():
        prompt_path.unlink()

    if prompt_text is not None:
        atomic_write_text(prompt_path, prompt_text)

    state = {
        "schema_version": CODEX_SCHEMA_VERSION,
        "revision": revision_after,
        "status": status,
        "code": code,
        "source_type": source_type,
        "source_id": source_id,
        "source_status": source_status,
        "prompt_path": str(prompt_path),
        "status_path": str(generated_status_path(root)),
        "prompt_exists": prompt_path.exists(),
        "blocked_reason": blocked_reason,
        "details": details or [],
        "created_at": previous.get("created_at") if isinstance(previous, dict) else now,
        "updated_at": now,
    }

    if status == READY_STATUS:
        state["ready_at"] = now
        state["last_build_at"] = now

    if command == "codex.clear":
        state["cleared_at"] = now

    write_json(current_execution_path(root), state)
    atomic_write_text(generated_status_path(root), render_status_markdown(state))

    append_event(
        root=root,
        actor=actor,
        command=command,
        entity_type="codex_execution",
        entity_id=source_id or "none",
        revision_before=revision_before,
        revision_after=revision_after,
        payload={
            "status": status,
            "code": code,
            "source_type": source_type,
            "source_id": source_id,
            "prompt_path": str(prompt_path),
        },
    )

    return state


def validate_source_state(root, source_type, source_id):
    if source_type == "task":
        state = load_tasks(root)
        task = find_item(state.get("tasks", []), source_id)

        if task is None:
            raise CodexError(
                CODEX_ENTITY_NOT_FOUND,
                "{} not found".format(source_id),
                source_type=source_type,
                source_id=source_id,
            )

        status = task.get("status", "")

        if status not in TASK_EXECUTABLE_STATUSES:
            raise CodexError(
                CODEX_SOURCE_NOT_READY,
                "{} status={}".format(source_id, status),
                source_type=source_type,
                source_id=source_id,
                source_status=status,
            )

        return task

    if source_type == "evolution_change":
        state = load_evolution(root)
        change = find_item(state.get("changes", []), source_id)

        if change is None:
            raise CodexError(
                CODEX_ENTITY_NOT_FOUND,
                "{} not found".format(source_id),
                source_type=source_type,
                source_id=source_id,
            )

        status = change.get("status", "")

        if status not in CHANGE_EXECUTABLE_STATUSES:
            raise CodexError(
                CODEX_SOURCE_NOT_READY,
                "{} status={}".format(source_id, status),
                source_type=source_type,
                source_id=source_id,
                source_status=status,
            )

        return change

    raise CodexError(
        CODEX_NO_EXECUTABLE_SOURCE,
        "Unknown source type: {}".format(source_type or "none"),
        source_type=source_type,
        source_id=source_id,
    )


def build_from_task(root, task_id):
    task = validate_source_state(root, "task", task_id)
    return task_prompt_model(task)


def build_from_change(root, change_id):
    change = validate_source_state(root, "evolution_change", change_id)
    return change_prompt_model(change)


def print_status_report(state):
    code = state.get("code") or CODEX_NO_PROMPT_PACKAGE
    status = state.get("status") or BLOCKED_STATUS

    print(CODEX_READY if status == READY_STATUS else CODEX_BLOCKED)
    print("Code: {}".format(code))
    print("Status: {}".format(status.upper()))
    print("Prompt exists: {}".format("yes" if state.get("prompt_exists") else "no"))
    print("Prompt path: {}".format(state.get("prompt_path") or ""))
    print("Source type: {}".format(state.get("source_type") or "none"))
    print("Source ID: {}".format(state.get("source_id") or "none"))
    print("Source status: {}".format(state.get("source_status") or "unknown"))

    if state.get("blocked_reason"):
        print("Blocked reason: {}".format(state.get("blocked_reason")))


def calculated_status(root):
    prompt_path = generated_prompt_path(root)

    try:
        state = load_current_execution(root)
    except CodexError as exc:
        return {
            "status": BLOCKED_STATUS,
            "code": exc.code,
            "source_type": exc.source_type,
            "source_id": exc.source_id,
            "source_status": exc.source_status,
            "prompt_path": str(prompt_path),
            "prompt_exists": prompt_path.exists(),
            "blocked_reason": exc.message,
        }

    if state is None:
        code = CODEX_NO_PROMPT_PACKAGE
        reason = "No current Codex execution state exists."

        if prompt_path.exists():
            code = CODEX_NO_EXECUTABLE_SOURCE
            reason = "CODEX_PROMPT.md exists, but no current Codex execution source is recorded."

        return {
            "status": BLOCKED_STATUS,
            "code": code,
            "source_type": "",
            "source_id": "",
            "source_status": "",
            "prompt_path": str(prompt_path),
            "prompt_exists": prompt_path.exists(),
            "blocked_reason": reason,
        }

    state = dict(state)
    state["prompt_exists"] = prompt_path.exists()

    if state.get("status") != READY_STATUS:
        return state

    if not prompt_path.exists():
        state["status"] = BLOCKED_STATUS
        state["code"] = CODEX_NO_PROMPT_PACKAGE
        state["blocked_reason"] = "Ready state exists, but CODEX_PROMPT.md is missing."
        return state

    try:
        source = validate_source_state(root, state.get("source_type"), state.get("source_id"))
    except CodexError as exc:
        state["status"] = BLOCKED_STATUS
        state["code"] = exc.code
        state["source_status"] = exc.source_status
        state["blocked_reason"] = exc.message
        return state

    state["source_status"] = source.get("status", state.get("source_status", ""))
    state["code"] = CODEX_READY
    return state


def cmd_status(args):
    root = repo_root(args)
    print_status_report(calculated_status(root))
    return 0


def cmd_build(args):
    root = repo_root(args)

    try:
        if args.task:
            model = build_from_task(root, args.task)
        else:
            model = build_from_change(root, args.change)

        prompt_text = render_prompt(model)
        state = write_execution_state(
            root=root,
            actor=args.actor,
            command="codex.prompt.build",
            status=READY_STATUS,
            code=CODEX_READY,
            source_type=model["source_type"],
            source_id=model["source_id"],
            source_status=model["source_status"],
            prompt_text=prompt_text,
        )

        print("OK: {}".format(CODEX_READY))
        print("Prompt: {}".format(generated_prompt_path(root)))
        print("Status: {}".format(generated_status_path(root)))
        print("Source: {} {}".format(model["source_type"], model["source_id"]))
        return 0
    except CodexError as exc:
        write_execution_state(
            root=root,
            actor=args.actor,
            command="codex.prompt.blocked",
            status=BLOCKED_STATUS,
            code=exc.code,
            source_type=exc.source_type or ("task" if args.task else "evolution_change"),
            source_id=exc.source_id or args.task or args.change or "",
            source_status=exc.source_status,
            blocked_reason=exc.message,
            details=exc.details,
            remove_prompt=True,
        )
        print("ERROR: {}: {}".format(exc.code, exc.message), file=sys.stderr)
        return 1


def cmd_clear(args):
    root = repo_root(args)
    state = write_execution_state(
        root=root,
        actor=args.actor,
        command="codex.clear",
        status=BLOCKED_STATUS,
        code=CODEX_NO_PROMPT_PACKAGE,
        blocked_reason="No executable Codex prompt package is currently selected.",
        remove_prompt=True,
    )

    print("OK: codex prompt package cleared")
    print("Code: {}".format(state.get("code")))
    print("Status: {}".format(generated_status_path(root)))
    return 0


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
        description="Strict Codex prompt package CLI for AI Development System"
    )
    add_common_args(parser)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("status", help="Show current Codex prompt package status")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("build", help="Build Codex prompt package from a Task or Evolution Change")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--task", help="Task ID, for example TASK-001")
    group.add_argument("--change", help="Evolution Change ID, for example CHG-001")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("clear", help="Clear current generated Codex prompt package")
    p.set_defaults(func=cmd_clear)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.func(args)
    except CodexError as exc:
        print("ERROR: {}: {}".format(exc.code, exc.message), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

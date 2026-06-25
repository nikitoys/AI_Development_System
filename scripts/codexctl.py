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
import hashlib
import json
import os
import sys
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
CODEX_CONTEXT_PACK_MISSING = "CODEX_CONTEXT_PACK_MISSING"
CODEX_CONTEXT_PACK_INVALID = "CODEX_CONTEXT_PACK_INVALID"
CODEX_CONTEXT_PACK_STALE = "CODEX_CONTEXT_PACK_STALE"

CONTEXT_SCHEMA_VERSION = 1
CONTEXT_METADATA_PREFIX = "<!-- Context: "
CONTEXT_METADATA_SUFFIX = " -->"
GENERATED_HEADER = "<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->"


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
    return core_utc_now()


def repo_root(args):
    return Path(args.root).resolve()


def state_dir(root):
    return core_state_dir(root)


def events_dir(root):
    return core_events_dir(root)


def generated_dir(root):
    return core_generated_dir(root)


def current_execution_path(root):
    return state_dir(root) / "current_execution.json"


def codex_events_path(root):
    return events_dir(root) / "codex-events.jsonl"


def generated_prompt_path(root):
    return generated_dir(root) / "CODEX_PROMPT.md"


def generated_status_path(root):
    return generated_dir(root) / "CODEX_STATUS.md"


def generated_context_pack_path(root):
    return generated_dir(root) / "CONTEXT_PACK.md"


def docs_path(root):
    return state_dir(root) / "docs.json"


def tasks_path(root):
    return state_dir(root) / "tasks.json"


def evolution_path(root):
    return state_dir(root) / "evolution.json"


def ensure_project_dirs(root):
    core_ensure_project_dirs(root)


def atomic_write_text(path, text):
    core_atomic_write_text(path, text)


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


def load_docs(root):
    return read_json(
        docs_path(root),
        CODEX_CONTEXT_PACK_INVALID,
        "DOCS_NOT_INITIALIZED: run `python scripts/docctl.py init` first",
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
    append_audit_event(
        codex_events_path(root),
        actor=actor,
        command=command,
        entity_type=entity_type,
        entity_id=entity_id,
        revision_before=revision_before,
        revision_after=revision_after,
        payload=payload,
    )


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


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def short_hash(value):
    return str(value or "")[:12]


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


def parse_context_metadata(path, text):
    for line in text.splitlines()[:10]:
        if line.startswith(CONTEXT_METADATA_PREFIX) and line.endswith(CONTEXT_METADATA_SUFFIX):
            raw = line[len(CONTEXT_METADATA_PREFIX) : -len(CONTEXT_METADATA_SUFFIX)]
            try:
                metadata = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise CodexError(
                    CODEX_CONTEXT_PACK_INVALID,
                    "INVALID_CONTEXT_METADATA: {}".format(exc),
                    details=[str(path)],
                )

            if metadata.get("schema_version") != CONTEXT_SCHEMA_VERSION:
                raise CodexError(
                    CODEX_CONTEXT_PACK_INVALID,
                    "UNSUPPORTED_CONTEXT_METADATA_VERSION: {}".format(metadata.get("schema_version")),
                    details=[str(path)],
                )

            return metadata

    raise CodexError(
        CODEX_CONTEXT_PACK_INVALID,
        "MISSING_CONTEXT_METADATA: {}".format(path),
        details=[str(path)],
    )


def parse_backtick_field(text, label):
    prefix = "{}: `".format(label)

    for line in text.splitlines():
        if not line.startswith(prefix):
            continue
        value = line[len(prefix) :]
        if value.endswith("`"):
            value = value[:-1]
        return value

    return ""


def parse_int_field(text, label):
    value = parse_backtick_field(text, label)

    if not value or value == "none":
        return None

    try:
        return int(value)
    except ValueError:
        raise CodexError(
            CODEX_CONTEXT_PACK_INVALID,
            "INVALID_CONTEXT_FIELD: {} must be an integer or none".format(label),
        )


def parse_selected_sources(text):
    sources = []
    in_table = False

    for line in text.splitlines():
        if line == "## Selected Sources":
            in_table = True
            continue

        if not in_table:
            continue

        if line == "## Selected Context":
            break

        if not line.startswith("| ") or line.startswith("| ---") or line.startswith("| Score "):
            continue

        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 7:
            continue

        path = cells[1].strip("`")
        line_range = cells[3]
        start_line = ""
        end_line = ""

        if "-" in line_range:
            start_line, end_line = [part.strip() for part in line_range.split("-", 1)]

        sources.append(
            {
                "score": cells[0],
                "path": path,
                "heading": cells[2].replace("\\|", "|"),
                "start_line": start_line,
                "end_line": end_line,
                "content_hash": cells[4].strip("`"),
                "chunk_hash": cells[5].strip("`"),
                "reasons": cells[6],
            }
        )

    return sources


def context_pack_path(root, path_text):
    if not path_text:
        return generated_context_pack_path(root)

    raw = Path(path_text)
    path = raw if raw.is_absolute() else root / raw
    path = path.resolve()
    root = root.resolve()

    try:
        path.relative_to(root)
    except ValueError:
        raise CodexError(
            CODEX_CONTEXT_PACK_INVALID,
            "CONTEXT_PACK_OUTSIDE_REPOSITORY: {}".format(path),
            details=[str(path)],
        )

    return path


def validate_context_pack(root, path_text, expected_task_id=""):
    path = context_pack_path(root, path_text)

    if not path.exists():
        raise CodexError(
            CODEX_CONTEXT_PACK_MISSING,
            "NO_CONTEXT_PACK: build one with `python scripts/contextctl.py pack build --task {} --write`".format(
                expected_task_id or "<TASK_ID>"
            ),
            details=[str(path)],
        )

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise CodexError(
            CODEX_CONTEXT_PACK_INVALID,
            "INVALID_CONTEXT_PACK_ENCODING: {}".format(exc),
            details=[str(path)],
        )

    if not text.startswith(GENERATED_HEADER):
        raise CodexError(
            CODEX_CONTEXT_PACK_INVALID,
            "MISSING_GENERATED_HEADER: {}".format(path.relative_to(root)),
            details=[str(path)],
        )

    metadata = parse_context_metadata(path, text)
    mode = parse_backtick_field(text, "Mode")
    task_id = parse_backtick_field(text, "Task ID")
    docs_revision = parse_int_field(text, "Docs revision")
    tasks_revision = parse_int_field(text, "Tasks revision")

    if mode and metadata.get("mode") and mode != metadata.get("mode"):
        raise CodexError(
            CODEX_CONTEXT_PACK_INVALID,
            "CONTEXT_METADATA_MISMATCH: mode {} != {}".format(mode, metadata.get("mode")),
            details=[str(path)],
        )

    metadata_task_id = metadata.get("task_id") or "none"
    if task_id and task_id != metadata_task_id:
        raise CodexError(
            CODEX_CONTEXT_PACK_INVALID,
            "CONTEXT_METADATA_MISMATCH: task_id {} != {}".format(task_id, metadata_task_id),
            details=[str(path)],
        )

    if expected_task_id and metadata.get("mode") == "task" and metadata.get("task_id") != expected_task_id:
        raise CodexError(
            CODEX_CONTEXT_PACK_INVALID,
            "CONTEXT_TASK_MISMATCH: expected {} got {}".format(expected_task_id, metadata.get("task_id") or "none"),
            details=[str(path)],
        )

    if docs_revision is None:
        raise CodexError(
            CODEX_CONTEXT_PACK_INVALID,
            "MISSING_CONTEXT_FIELD: Docs revision",
            details=[str(path)],
        )

    docs_state = load_docs(root)
    current_docs_revision = int(docs_state.get("revision", 0))
    stale = []

    if docs_revision != current_docs_revision:
        stale.append("docs revision {} != current {}".format(docs_revision, current_docs_revision))

    if tasks_revision is not None:
        tasks_state = load_tasks(root)
        current_tasks_revision = int(tasks_state.get("revision", 0))
        if tasks_revision != current_tasks_revision:
            stale.append("tasks revision {} != current {}".format(tasks_revision, current_tasks_revision))

    if stale:
        raise CodexError(
            CODEX_CONTEXT_PACK_STALE,
            "STALE_CONTEXT_PACK: {}".format("; ".join(stale)),
            details=stale,
        )

    sources = parse_selected_sources(text)
    if "## Selected Sources" not in text or "## Selected Context" not in text:
        raise CodexError(
            CODEX_CONTEXT_PACK_INVALID,
            "INVALID_CONTEXT_PACK_STRUCTURE: missing selected sources or selected context section",
            details=[str(path)],
        )

    return {
        "path": path,
        "relative_path": str(path.relative_to(root)),
        "sha256": sha256_text(text),
        "metadata": metadata,
        "mode": metadata.get("mode") or mode,
        "task_id": metadata.get("task_id") or "",
        "docs_revision": docs_revision,
        "tasks_revision": tasks_revision,
        "selected_sources": sources,
        "text": text,
    }


def task_prompt_model(task):
    title = first_text(task, ["title", "name", "summary"])
    summary = first_text(task, ["summary", "description", "body", "details"])
    description = first_text(task, ["description", "body", "details"])
    scope = first_list(task, ["scope", "scopes"])
    out_of_scope = first_list(task, ["out_of_scope", "exclusions"])
    allowed_files = first_list(task, ["allowed_files", "affected_files", "files"])
    acceptance = first_list(task, ["acceptance_criteria", "acceptance", "done_when"])
    review = first_list(task, ["review_instructions", "review", "review_notes"])

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
        "source_ref": task.get("ref") or "",
        "source_status": task.get("status"),
        "source_kind_label": "Task",
        "revision_label": "tasks",
        "revision": task.get("_tasks_revision"),
        "active_role": first_text(task, ["active_role"], "Codex Executor"),
        "active_stage": first_text(task, ["active_stage"], "Implementation of approved bounded task"),
        "active_document": first_text(task, ["active_document"], "AI_PROJECT/state/tasks.json"),
        "expected_result": first_text(task, ["expected_result"], "Task completed according to acceptance criteria."),
        "title": title,
        "objective": summary or title,
        "summary": summary or title,
        "description": description,
        "scope": scope,
        "out_of_scope": out_of_scope or ["Anything outside the source Task scope."],
        "allowed_files_heading": "Allowed Files",
        "allowed_files": allowed_files,
        "affected_areas": [],
        "implementation_instructions": default_implementation_instructions(),
        "acceptance": acceptance,
        "verification_mode": first_text(task, ["verification_mode"], "standard"),
        "review": review,
        "context_pack": None,
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
        "source_ref": "",
        "source_status": change.get("status"),
        "source_kind_label": "Change",
        "revision_label": "evolution",
        "revision": change.get("_evolution_revision"),
        "active_role": "Codex Executor",
        "active_stage": "Implementation of approved bounded change",
        "active_document": "AI_PROJECT/state/evolution.json / AI_PROJECT/generated/EVOLUTION.md",
        "expected_result": proposal or title,
        "title": title,
        "objective": problem or proposal or title,
        "summary": problem or proposal or title,
        "description": "\n\n".join([text for text in [proposal, rationale] if text]),
        "scope": scope,
        "out_of_scope": out_of_scope,
        "allowed_files_heading": "Allowed Files / Affected Files",
        "allowed_files": allowed_files,
        "affected_areas": affected_areas,
        "implementation_instructions": default_implementation_instructions(),
        "acceptance": acceptance,
        "verification_mode": "standard",
        "review": [
            "Report changed files, commands run, verification result, blockers and risks.",
            "Do not mark the Evolution Change accepted without Human Owner decision.",
        ],
        "context_pack": None,
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


def source_identity(model):
    source_id = model["source_id"]
    source_ref = model.get("source_ref")
    if source_ref:
        return "{} / {}".format(source_id, source_ref)
    return source_id


def render_context(lines, context_pack):
    lines.append("## Context")
    lines.append("")

    if not context_pack:
        lines.append("No Context Pack attached.")
        lines.append("")
        return

    lines.append("Context Pack: {}".format(context_pack["relative_path"]))
    lines.append("Hash: {}".format(context_pack["sha256"]))
    lines.append(
        "Revisions: docs {}, tasks {}".format(
            context_pack.get("docs_revision"),
            context_pack.get("tasks_revision") if context_pack.get("tasks_revision") is not None else "none",
        )
    )
    lines.append("")
    lines.append("Refs:")

    selected_sources = context_pack.get("selected_sources", [])
    if not selected_sources:
        lines.append("- No selected source refs recorded.")
    else:
        for source in selected_sources:
            start_line = source.get("start_line") or "?"
            end_line = source.get("end_line") or "?"
            lines.append("- {} lines {}-{}".format(source.get("path"), start_line, end_line))

    lines.append("")
    lines.append("Context is read-only. It does not expand Scope, Allowed Files, or Acceptance Criteria.")
    lines.append("If context conflicts with this prompt, report the conflict.")
    lines.append("")


def summary_contract_template():
    return {
        "implementation_summary": "Summarize the completed implementation.",
        "notes": [],
        "warnings": [],
        "blockers": [],
    }


def render_execution_summary_contract(lines):
    lines.append("## Execution Summary")
    lines.append("")
    lines.append("Finish your response with a machine-readable execution summary block.")
    lines.append("Use the exact marker shown below followed by one fenced JSON block.")
    lines.append("No prose, Markdown bullets, or extra text may appear after the closing fence.")
    lines.append("Keep exactly the four JSON keys shown; replace placeholder values with actual results.")
    lines.append("Do not emit a full TaskReport payload.")
    lines.append(
        "Do not include task_id, changed_files, generated_files, checks, owner_decision_required, "
        "or token_usage; the pipeline records those separately."
    )
    lines.append("")
    lines.append("CODEX_EXECUTION_SUMMARY_JSON:")
    lines.append("```json")
    lines.extend(
        json.dumps(summary_contract_template(), ensure_ascii=False, indent=2).splitlines()
    )
    lines.append("```")


def render_prompt(model):
    generated = utc_now()
    lines = []

    lines.append("# Codex Prompt Package")
    lines.append("")
    lines.append("Generated: {}".format(generated))
    lines.append("")
    lines.append("Profile: execute")
    lines.append("{}: {}".format(model.get("source_kind_label", "Task"), source_identity(model)))
    lines.append("Status: {}".format(model["source_status"]))
    lines.append(
        "Revision: {} {}".format(
            model.get("revision_label") or "source",
            model.get("revision") if model.get("revision") is not None else "unknown",
        )
    )
    lines.append("Verification: {}".format(model["verification_mode"]))
    lines.append("")
    lines.append("## Role")
    lines.append("")
    lines.append("You are {}. Execute one bounded task. Do not self-approve.".format(model["active_role"]))
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append(model["objective"])
    lines.append("")
    lines.append("## Task Input")
    lines.append("")
    lines.append("{}: {}".format(model.get("source_kind_label", "Task"), model["source_id"]))
    lines.append("Summary: {}".format(model["summary"]))
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    markdown_list(lines, model["scope"], "No explicit scope defined. Stop and ask before editing.")
    lines.append("")
    lines.append("## Out of Scope")
    lines.append("")
    markdown_list(lines, model["out_of_scope"], "Anything not required by the source entity.")
    lines.append("")
    lines.append("## Allowed Files")
    lines.append("")
    lines.append("Editable:")
    markdown_list(lines, model["allowed_files"], "No allowed files defined. Do not edit files.")
    lines.append("")
    lines.append("Do not edit other files.")
    lines.append("")
    lines.append("## Acceptance Criteria")
    lines.append("")
    markdown_list(lines, model["acceptance"], "Source criteria must be satisfied.")
    lines.append("")
    lines.append("## Verification")
    lines.append("")
    lines.append("Mode: {}".format(model["verification_mode"]))
    lines.append("")
    lines.append("Run the smallest relevant checks for the changed files.")
    lines.append("If a check cannot be run, say why.")
    lines.append("")
    render_context(lines, model.get("context_pack"))
    lines.append("## Execution Rules")
    lines.append("")
    lines.append("Stay within Scope and Allowed Files.")
    lines.append("Do not edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**`, or `AI_PROJECT/generated/**` manually.")
    lines.append("Inspect before editing. Prefer minimal changes. Do not refactor unrelated code.")
    lines.append("")
    lines.append("## Missing Info")
    lines.append("")
    lines.append("Inspect available files first.")
    lines.append("If still blocked, stop and report the blocker.")
    lines.append("If safe to continue, make the smallest assumption and disclose it.")
    lines.append("")
    render_execution_summary_contract(lines)
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

    context_pack = state.get("context_pack") or {}

    if context_pack:
        lines.append("Context Pack:")
        lines.append("")
        lines.append("- Path: `{}`".format(context_pack.get("relative_path") or context_pack.get("path") or ""))
        lines.append("- SHA-256: `{}`".format(context_pack.get("sha256") or ""))
        lines.append("- Mode: `{}`".format(context_pack.get("mode") or "unknown"))
        lines.append("- Task ID: `{}`".format(context_pack.get("task_id") or "none"))
        lines.append("- Docs revision: `{}`".format(context_pack.get("docs_revision") or "unknown"))
        lines.append(
            "- Tasks revision: `{}`".format(
                context_pack.get("tasks_revision") if context_pack.get("tasks_revision") is not None else "none"
            )
        )
        lines.append("- Selected sources: `{}`".format(context_pack.get("selected_source_count", 0)))
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
    context_pack=None,
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

    if context_pack:
        state["context_pack"] = {
            "relative_path": context_pack.get("relative_path"),
            "path": str(context_pack.get("path")),
            "sha256": context_pack.get("sha256"),
            "mode": context_pack.get("mode"),
            "task_id": context_pack.get("task_id"),
            "docs_revision": context_pack.get("docs_revision"),
            "tasks_revision": context_pack.get("tasks_revision"),
            "selected_source_count": len(context_pack.get("selected_sources", [])),
        }

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
            "context_pack": state.get("context_pack", {}),
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

        task = dict(task)
        task["_tasks_revision"] = state.get("revision")
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

        change = dict(change)
        change["_evolution_revision"] = state.get("revision")
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

    context_pack = state.get("context_pack") or {}
    if context_pack:
        try:
            validate_context_pack(
                root,
                context_pack.get("path") or context_pack.get("relative_path"),
                state.get("source_id") if state.get("source_type") == "task" else "",
            )
        except CodexError as exc:
            state["status"] = BLOCKED_STATUS
            state["code"] = exc.code
            state["blocked_reason"] = exc.message
            state["details"] = exc.details
            return state

    state["code"] = CODEX_READY
    return state


def cmd_status(args):
    root = repo_root(args)
    print_status_report(calculated_status(root))
    return 0


def cmd_build(args):
    root = repo_root(args)

    try:
        if args.with_context and args.context_pack:
            raise CodexError(
                CODEX_CONTEXT_PACK_INVALID,
                "Use either --with-context or --context-pack, not both.",
            )

        if args.task:
            model = build_from_task(root, args.task)
        else:
            model = build_from_change(root, args.change)

        if args.with_context or args.context_pack:
            model["context_pack"] = validate_context_pack(
                root,
                args.context_pack,
                args.task or "",
            )

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
            context_pack=model.get("context_pack"),
        )

        print("OK: {}".format(CODEX_READY))
        print("Prompt: {}".format(generated_prompt_path(root)))
        print("Status: {}".format(generated_status_path(root)))
        print("Source: {} {}".format(model["source_type"], model["source_id"]))
        if model.get("context_pack"):
            print("Context Pack: {}".format(model["context_pack"]["relative_path"]))
            print("Context Pack SHA-256: {}".format(model["context_pack"]["sha256"]))
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
    p.add_argument(
        "--with-context",
        action="store_true",
        help="Include the default AI_PROJECT/generated/CONTEXT_PACK.md after validating it.",
    )
    p.add_argument(
        "--context-pack",
        help="Repository-relative or absolute Context Pack path to validate and include.",
    )
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

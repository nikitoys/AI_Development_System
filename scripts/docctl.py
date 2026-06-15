#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
docctl.py — strict CLI gateway for AI_PROJECT/state/docs.json

Controls documentation lifecycle state for AI Development System.

Files:
  AI_PROJECT/state/docs.json
  AI_PROJECT/events/doc-events.jsonl
  AI_PROJECT/generated/DOCS_INDEX.md
  AI_PROJECT/generated/DOCS_GAPS.md

Examples:
  python scripts/docctl.py init
  python scripts/docctl.py doc register --path ai-system/project-control/08-usage-guide.md --title "Project Control Usage Guide" --type guide --status planned
  python scripts/docctl.py doc status ai-system/project-control/01-overview.md --to active
  python scripts/docctl.py doc mark-reviewed ai-system/project-control/01-overview.md
  python scripts/docctl.py scan
  python scripts/docctl.py validate
  python scripts/docctl.py render
  python scripts/docctl.py check-generated
  python scripts/docctl.py audit --last 20
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
from urllib.parse import unquote, urlparse


DOC_SCHEMA_VERSION = 1

DOC_STATUSES = {
    "planned",
    "draft",
    "review",
    "active",
    "deprecated",
    "archived",
}

DOC_TYPES = {
    "overview",
    "guide",
    "process",
    "lifecycle",
    "reference",
    "template",
    "policy",
    "changelog",
    "generated",
}

GENERATED_HEADER = "<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->"

DEFAULT_DOCS = [
    (
        "ai-system/project-control/01-overview.md",
        "Project Control Gateway Overview",
        "overview",
        "active",
        True,
    ),
    (
        "ai-system/project-control/02-domain-model.md",
        "Project Control Domain Model",
        "reference",
        "active",
        True,
    ),
    (
        "ai-system/project-control/03-state-model.md",
        "Project Control State Model",
        "reference",
        "active",
        True,
    ),
    (
        "ai-system/project-control/04-command-catalog.md",
        "Project Control Command Catalog",
        "reference",
        "active",
        True,
    ),
    (
        "ai-system/project-control/05-lifecycle-rules.md",
        "Project Control Lifecycle Rules",
        "lifecycle",
        "active",
        True,
    ),
    (
        "ai-system/project-control/06-prompt-package-spec.md",
        "Project Control Prompt Package Specification",
        "reference",
        "active",
        True,
    ),
    (
        "ai-system/project-control/07-validation-and-tests.md",
        "Project Control Validation and Tests",
        "process",
        "active",
        True,
    ),
    (
        "ai-system/project-control/08-usage-guide.md",
        "Project Control Usage Guide",
        "guide",
        "planned",
        False,
    ),
]


class DocError(Exception):
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


def docs_path(root):
    return state_dir(root) / "docs.json"


def doc_events_path(root):
    return events_dir(root) / "doc-events.jsonl"


def generated_index_path(root):
    return generated_dir(root) / "DOCS_INDEX.md"


def generated_gaps_path(root):
    return generated_dir(root) / "DOCS_GAPS.md"


def ensure_project_dirs(root):
    state_dir(root).mkdir(parents=True, exist_ok=True)
    events_dir(root).mkdir(parents=True, exist_ok=True)
    generated_dir(root).mkdir(parents=True, exist_ok=True)


def atomic_write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))

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


def read_json(path, missing_message):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise DocError(missing_message)
    except json.JSONDecodeError as e:
        raise DocError("INVALID_JSON: {}:{}:{} {}".format(path, e.lineno, e.colno, e.msg))


def load_docs(root):
    return read_json(docs_path(root), "DOCS_NOT_INITIALIZED: run `python scripts/docctl.py init` first")


def save_docs(root, state):
    write_json(docs_path(root), state)


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
    path = doc_events_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(line)


def normalize_doc_path(path_text):
    path = Path(path_text)
    if path.is_absolute():
        raise DocError("INVALID_DOC_PATH: path must be repository-relative")
    normalized = path.as_posix().strip()
    if not normalized or normalized.startswith("../") or "/../" in normalized:
        raise DocError("INVALID_DOC_PATH: {}".format(path_text))
    return normalized


def default_docs_state():
    now = utc_now()
    docs = []

    for order, (path, title, doc_type, status, required) in enumerate(DEFAULT_DOCS, start=1):
        docs.append(
            {
                "id": "DOC-{:03d}".format(order),
                "path": path,
                "title": title,
                "type": doc_type,
                "status": status,
                "required": required,
                "owner": "AI System Maintainer",
                "last_reviewed_at": "",
                "last_reviewed_by": "",
                "notes": [],
                "created_at": now,
                "updated_at": now,
            }
        )

    return {
        "schema_version": DOC_SCHEMA_VERSION,
        "revision": 0,
        "created_at": now,
        "updated_at": now,
        "docs": docs,
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


def require_bool(value, path, errors):
    if not isinstance(value, bool):
        errors.append("{} must be boolean".format(path))


def require_string_list(value, path, errors):
    if not isinstance(value, list):
        errors.append("{} must be a list".format(path))
        return
    for i, item in enumerate(value):
        if not isinstance(item, str):
            errors.append("{}[{}] must be a string".format(path, i))


def find_doc(state, path_text, required=True):
    normalized = normalize_doc_path(path_text)
    for doc in state.get("docs", []):
        if doc.get("path") == normalized:
            return doc
    if required:
        raise DocError("DOC_NOT_FOUND: {}".format(normalized))
    return None


def next_id(docs):
    max_num = 0
    for doc in docs:
        doc_id = str(doc.get("id", ""))
        if doc_id.startswith("DOC-") and doc_id[4:].isdigit():
            max_num = max(max_num, int(doc_id[4:]))
    return "DOC-{:03d}".format(max_num + 1)


def infer_title(path):
    name = Path(path).stem.replace("-", " ").replace("_", " ")
    return name.title()


def infer_type(path):
    lower = path.lower()
    if "changelog" in lower:
        return "changelog"
    if "template" in lower:
        return "template"
    if "lifecycle" in lower:
        return "lifecycle"
    if "policy" in lower or "rules" in lower:
        return "policy"
    if "guide" in lower or "owner-guide" in lower:
        return "guide"
    if "process" in lower:
        return "process"
    if "overview" in lower:
        return "overview"
    return "reference"


def is_external_link(target):
    parsed = urlparse(target)
    return bool(parsed.scheme and parsed.scheme not in {"", "file"})


def local_markdown_links(text):
    pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    for match in pattern.finditer(text):
        target = match.group(1).strip()
        if not target or target.startswith("#") or is_external_link(target):
            continue
        if target.startswith("mailto:") or target.startswith("tel:"):
            continue
        target = target.split()[0]
        yield unquote(target.split("#", 1)[0])


def validate_markdown_links(root, doc_path, errors):
    full_path = root / doc_path
    try:
        text = full_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        errors.append("{} invalid text encoding: {}".format(doc_path, exc))
        return

    for target in local_markdown_links(text):
        if not target:
            continue
        candidate = (full_path.parent / target).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            errors.append("{} link escapes repository: {}".format(doc_path, target))
            continue
        if not candidate.exists():
            errors.append("{} broken local link: {}".format(doc_path, target))


def validate_no_unresolved_placeholders(root, doc, errors):
    path = doc.get("path")
    try:
        text = (root / path).read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        errors.append("{} invalid text encoding: {}".format(path, exc))
        return
    if re.search(r"\{\{[^{}\n]+\}\}", text):
        errors.append("{} contains unresolved {{PLACEHOLDER}}".format(path))


def validate_docs(state, root):
    errors = []
    require_keys(state, ["schema_version", "revision", "created_at", "updated_at", "docs"], "docs_state", errors)
    if errors:
        return errors

    if state.get("schema_version") != DOC_SCHEMA_VERSION:
        errors.append("schema_version must be {}".format(DOC_SCHEMA_VERSION))
    if not isinstance(state.get("revision"), int) or state.get("revision") < 0:
        errors.append("revision must be a non-negative integer")

    docs = state.get("docs")
    if not isinstance(docs, list):
        errors.append("docs must be a list")
        docs = []

    ids = set()
    paths = set()
    active_required_docs = []

    for i, doc in enumerate(docs):
        path_name = "docs[{}]".format(i)
        require_keys(
            doc,
            [
                "id",
                "path",
                "title",
                "type",
                "status",
                "required",
                "owner",
                "last_reviewed_at",
                "last_reviewed_by",
                "notes",
                "created_at",
                "updated_at",
            ],
            path_name,
            errors,
        )

        doc_id = doc.get("id")
        doc_path = doc.get("path")
        status = doc.get("status")
        doc_type = doc.get("type")

        if doc_id in ids:
            errors.append("duplicate doc id: {}".format(doc_id))
        ids.add(doc_id)
        if doc_path in paths:
            errors.append("duplicate doc path: {}".format(doc_path))
        paths.add(doc_path)

        require_string(doc_id, path_name + ".id", errors, allow_empty=False)
        require_string(doc_path, path_name + ".path", errors, allow_empty=False)
        require_string(doc.get("title"), path_name + ".title", errors, allow_empty=False)
        require_string(doc.get("owner"), path_name + ".owner", errors)
        require_string(doc.get("last_reviewed_at"), path_name + ".last_reviewed_at", errors)
        require_string(doc.get("last_reviewed_by"), path_name + ".last_reviewed_by", errors)
        require_bool(doc.get("required"), path_name + ".required", errors)
        require_string_list(doc.get("notes"), path_name + ".notes", errors)

        if status not in DOC_STATUSES:
            errors.append("{}.status is invalid: {}".format(path_name, status))
        if doc_type not in DOC_TYPES:
            errors.append("{}.type is invalid: {}".format(path_name, doc_type))

        try:
            normalized = normalize_doc_path(doc_path)
        except DocError as exc:
            errors.append(str(exc))
            continue

        exists = (root / normalized).exists()
        if status != "planned" and not exists:
            errors.append("{} registered doc does not exist: {}".format(path_name, normalized))
        if doc.get("required") and status == "active":
            active_required_docs.append(normalized)
        if exists and status != "planned":
            validate_markdown_links(root, normalized, errors)
        if exists and status == "active" and doc_type != "template":
            validate_no_unresolved_placeholders(root, doc, errors)

    if not active_required_docs:
        errors.append("at least one required active doc must exist")
    for doc_path in active_required_docs:
        if not (root / doc_path).exists():
            errors.append("required active doc does not exist: {}".format(doc_path))

    return errors


def require_valid_docs(state, root):
    errors = validate_docs(state, root)
    if errors:
        raise DocError("VALIDATION_FAILED:\n- " + "\n- ".join(errors))


def sorted_docs(state):
    return sorted(state.get("docs", []), key=lambda x: (x.get("status", ""), x.get("path", "")))


def docs_gaps(state, root):
    gaps = []
    for doc in sorted_docs(state):
        path = doc.get("path")
        exists = (root / path).exists()
        if doc.get("status") == "planned":
            gaps.append((doc, "planned document is not yet active"))
        elif not exists:
            gaps.append((doc, "registered document is missing"))
        elif doc.get("status") in {"draft", "review"}:
            gaps.append((doc, "document is not active"))
        elif doc.get("status") == "active" and not doc.get("last_reviewed_at"):
            gaps.append((doc, "active document has no recorded review"))
    return gaps


def render_index_markdown(state):
    lines = [
        GENERATED_HEADER,
        "<!-- Source: AI_PROJECT/state/docs.json -->",
        "",
        "# Documentation Index",
        "",
        "Revision: `{}`".format(state.get("revision", 0)),
        "Documents: `{}`".format(len(state.get("docs", []))),
        "",
        "| Path | Title | Type | Status | Required | Last reviewed |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for doc in sorted_docs(state):
        lines.append(
            "| `{}` | {} | `{}` | `{}` | `{}` | {} |".format(
                doc.get("path"),
                doc.get("title"),
                doc.get("type"),
                doc.get("status"),
                str(doc.get("required", False)).lower(),
                doc.get("last_reviewed_at") or "-",
            )
        )
    lines.append("")
    return "\n".join(lines)


def render_gaps_markdown(state, root):
    gaps = docs_gaps(state, root)
    lines = [
        GENERATED_HEADER,
        "<!-- Source: AI_PROJECT/state/docs.json -->",
        "",
        "# Documentation Gaps",
        "",
        "Revision: `{}`".format(state.get("revision", 0)),
        "Open gaps: `{}`".format(len(gaps)),
        "",
    ]
    if not gaps:
        lines.append("_No documentation gaps detected._")
        lines.append("")
        return "\n".join(lines)

    for doc, reason in gaps:
        lines.append("- `{}` ({}, {}): {}".format(doc.get("path"), doc.get("type"), doc.get("status"), reason))
    lines.append("")
    return "\n".join(lines)


def render_doc_outputs(root, state):
    require_valid_docs(state, root)
    atomic_write_text(generated_index_path(root), render_index_markdown(state))
    atomic_write_text(generated_gaps_path(root), render_gaps_markdown(state, root))


def mutate_state(args, command, entity_type, entity_id, payload, mutator):
    root = repo_root(args)
    state = load_docs(root)
    require_valid_docs(state, root)
    before = state["revision"]
    mutator(state)
    state["revision"] = before + 1
    state["updated_at"] = utc_now()
    require_valid_docs(state, root)
    save_docs(root, state)
    append_event(root, actor(args), command, entity_type, entity_id, before, state["revision"], payload)
    render_doc_outputs(root, state)
    print("OK: {} revision {} -> {}".format(command, before, state["revision"]))


def actor(args):
    return args.actor or os.environ.get("AI_DEV_ACTOR") or "human_owner"


def cmd_init(args):
    root = repo_root(args)
    ensure_project_dirs(root)
    path = docs_path(root)
    if path.exists() and not args.force:
        raise DocError("DOCS_ALREADY_EXISTS: use --force to reinitialize")
    state = default_docs_state()
    save_docs(root, state)
    append_event(root, actor(args), "init", "docs", "docs", None, 0, {"force": bool(args.force)})
    render_doc_outputs(root, state)
    print("OK: initialized docs revision 0")


def cmd_doc_register(args):
    root = repo_root(args)
    path = normalize_doc_path(args.path)
    status = args.status
    doc_type = args.type
    if status not in DOC_STATUSES:
        raise DocError("INVALID_STATUS: {}".format(status))
    if doc_type not in DOC_TYPES:
        raise DocError("INVALID_TYPE: {}".format(doc_type))

    def apply(state):
        if find_doc(state, path, required=False):
            raise DocError("DOC_ALREADY_REGISTERED: {}".format(path))
        now = utc_now()
        state["docs"].append(
            {
                "id": next_id(state.get("docs", [])),
                "path": path,
                "title": args.title or infer_title(path),
                "type": doc_type,
                "status": status,
                "required": bool(args.required),
                "owner": args.owner,
                "last_reviewed_at": "",
                "last_reviewed_by": "",
                "notes": list(args.note or []),
                "created_at": now,
                "updated_at": now,
            }
        )

    mutate_state(
        args,
        "doc register",
        "doc",
        path,
        {"path": path, "status": status, "type": doc_type},
        apply,
    )


def cmd_doc_status(args):
    if args.to not in DOC_STATUSES:
        raise DocError("INVALID_STATUS: {}".format(args.to))

    def apply(state):
        doc = find_doc(state, args.path)
        doc["status"] = args.to
        doc["updated_at"] = utc_now()

    mutate_state(args, "doc status", "doc", normalize_doc_path(args.path), {"to": args.to}, apply)


def cmd_doc_mark_reviewed(args):
    now = utc_now()

    def apply(state):
        doc = find_doc(state, args.path)
        doc["last_reviewed_at"] = now
        doc["last_reviewed_by"] = actor(args)
        doc["updated_at"] = now
        if args.note:
            doc.setdefault("notes", []).append(args.note)

    mutate_state(
        args,
        "doc mark-reviewed",
        "doc",
        normalize_doc_path(args.path),
        {"reviewed_at": now, "note": args.note or ""},
        apply,
    )


def cmd_scan(args):
    root = repo_root(args)
    markdown_files = sorted(
        path.relative_to(root).as_posix()
        for path in (root / "ai-system").rglob("*.md")
        if path.is_file()
    )
    added = []

    def apply(state):
        existing = {doc.get("path") for doc in state.get("docs", [])}
        for path in markdown_files:
            if path in existing:
                continue
            now = utc_now()
            state["docs"].append(
                {
                    "id": next_id(state.get("docs", [])),
                    "path": path,
                    "title": infer_title(path),
                    "type": infer_type(path),
                    "status": args.status,
                    "required": False,
                    "owner": args.owner,
                    "last_reviewed_at": "",
                    "last_reviewed_by": "",
                    "notes": [],
                    "created_at": now,
                    "updated_at": now,
                }
            )
            existing.add(path)
            added.append(path)

    mutate_state(args, "scan", "docs", "docs", {"added": added, "status": args.status}, apply)
    print("Added: {}".format(len(added)))


def cmd_validate(args):
    root = repo_root(args)
    state = load_docs(root)
    require_valid_docs(state, root)
    print("OK: docs are valid")


def cmd_render(args):
    root = repo_root(args)
    state = load_docs(root)
    render_doc_outputs(root, state)
    print("OK: rendered documentation outputs")


def cmd_check_generated(args):
    root = repo_root(args)
    state = load_docs(root)
    require_valid_docs(state, root)
    expected = {
        generated_index_path(root): render_index_markdown(state),
        generated_gaps_path(root): render_gaps_markdown(state, root),
    }
    errors = []
    for path, text in expected.items():
        if not path.exists():
            errors.append("MISSING_GENERATED_FILE: {}".format(path.relative_to(root)))
            continue
        actual = path.read_text(encoding="utf-8")
        if not actual.startswith(GENERATED_HEADER):
            errors.append("MISSING_GENERATED_HEADER: {}".format(path.relative_to(root)))
        if actual != text:
            errors.append("OUTDATED_GENERATED_FILE: {}".format(path.relative_to(root)))
    if errors:
        raise DocError("CHECK_GENERATED_FAILED:\n- " + "\n- ".join(errors))
    print("OK: generated documentation files are up to date")


def cmd_audit(args):
    root = repo_root(args)
    path = doc_events_path(root)
    if not path.exists():
        raise DocError("DOC_AUDIT_NOT_FOUND: no audit events")
    lines = [line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for line in lines[-args.last:]:
        event = json.loads(line)
        print(
            "{timestamp} {event_id} {actor} {command} {entity_type}:{entity_id} {before}->{after}".format(
                timestamp=event.get("timestamp"),
                event_id=event.get("event_id"),
                actor=event.get("actor"),
                command=event.get("command"),
                entity_type=event.get("entity_type"),
                entity_id=event.get("entity_id"),
                before=event.get("revision_before"),
                after=event.get("revision_after"),
            )
        )


def cmd_show(args):
    state = load_docs(repo_root(args))
    print(json.dumps(state, ensure_ascii=False, indent=2))


def cmd_status(args):
    root = repo_root(args)
    print("State: {}".format(docs_path(root)))
    print("Events: {}".format(doc_events_path(root)))
    print("Generated index: {}".format(generated_index_path(root)))
    print("Generated gaps: {}".format(generated_gaps_path(root)))
    try:
        state = load_docs(root)
        errors = validate_docs(state, root)
    except DocError as exc:
        print("Validation: ERROR {}".format(exc))
        return
    if errors:
        print("Validation: ERROR")
        for error in errors:
            print("- {}".format(error))
    else:
        print("Validation: OK")


def build_parser():
    parser = argparse.ArgumentParser(description="Strict docs.json control CLI for AI Development System")
    parser.add_argument("--root", default=".", help="Repository/project root. Default: current directory.")
    parser.add_argument("--actor", default=None, help="Audit actor. Default: AI_DEV_ACTOR or human_owner.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize AI_PROJECT/state/docs.json")
    p_init.add_argument("--force", action="store_true", help="Reinitialize docs state")
    p_init.set_defaults(func=cmd_init)

    p_show = sub.add_parser("show", help="Show docs state JSON")
    p_show.set_defaults(func=cmd_show)

    p_status = sub.add_parser("status", help="Show file paths and validation status")
    p_status.set_defaults(func=cmd_status)

    p_scan = sub.add_parser("scan", help="Register untracked ai-system Markdown documents")
    p_scan.add_argument("--status", default="draft", choices=sorted(DOC_STATUSES))
    p_scan.add_argument("--owner", default="AI System Maintainer")
    p_scan.set_defaults(func=cmd_scan)

    p_validate = sub.add_parser("validate", help="Validate docs.json and registered documents")
    p_validate.set_defaults(func=cmd_validate)

    p_render = sub.add_parser("render", help="Render generated documentation Markdown")
    p_render.set_defaults(func=cmd_render)

    p_check = sub.add_parser("check-generated", help="Check generated documentation Markdown is up to date")
    p_check.set_defaults(func=cmd_check_generated)

    p_audit = sub.add_parser("audit", help="Show doc audit events")
    p_audit.add_argument("--last", type=int, default=20)
    p_audit.set_defaults(func=cmd_audit)

    p_doc = sub.add_parser("doc", help="Manage registered documents")
    doc_sub = p_doc.add_subparsers(dest="doc_command", required=True)

    p_register = doc_sub.add_parser("register", help="Register a document")
    p_register.add_argument("--path", required=True)
    p_register.add_argument("--title", default="")
    p_register.add_argument("--type", default="reference", choices=sorted(DOC_TYPES))
    p_register.add_argument("--status", default="draft", choices=sorted(DOC_STATUSES))
    p_register.add_argument("--required", action="store_true")
    p_register.add_argument("--owner", default="AI System Maintainer")
    p_register.add_argument("--note", action="append")
    p_register.set_defaults(func=cmd_doc_register)

    p_doc_status = doc_sub.add_parser("status", help="Change document lifecycle status")
    p_doc_status.add_argument("path")
    p_doc_status.add_argument("--to", required=True, choices=sorted(DOC_STATUSES))
    p_doc_status.set_defaults(func=cmd_doc_status)

    p_reviewed = doc_sub.add_parser("mark-reviewed", help="Record document review")
    p_reviewed.add_argument("path")
    p_reviewed.add_argument("--note", default="")
    p_reviewed.set_defaults(func=cmd_doc_mark_reviewed)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except DocError as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

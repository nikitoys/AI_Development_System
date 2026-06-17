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
  python scripts/docctl.py scan --scope all
  python scripts/docctl.py validate
  python scripts/docctl.py render
  python scripts/docctl.py check-generated
  python scripts/docctl.py audit --last 20
"""

import argparse
import hashlib
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

DECLARED_STATUS_ALIASES = {
    "planned": "planned",
    "proposed": "planned",
    "draft": "draft",
    "in review": "review",
    "review": "review",
    "active": "active",
    "deprecated": "deprecated",
    "archived": "archived",
}

DOC_OPTIONAL_STRING_KEYS = (
    "content_hash",
    "last_reviewed_content_hash",
    "declared_status",
    "declared_status_raw",
    "declared_status_source",
)

DOC_GAP_CATEGORIES = (
    ("missing_file", "Missing File"),
    ("status_mismatch", "Status Mismatch"),
    ("active_not_reviewed", "Active Not Reviewed"),
    ("active_review_stale", "Active Review Stale"),
    ("unresolved_placeholder", "Unresolved Placeholder"),
    ("broken_local_link", "Broken Local Link"),
    ("content_hash_stale", "Stale Content Hash"),
    ("not_active", "Not Active"),
)

ROOT_DOC_PATTERNS = (
    "AGENTS.md",
    "README*.md",
)

SKILL_DOC_PATTERNS = (
    ".agents/skills/**/SKILL.md",
    "plugins/**/skills/**/SKILL.md",
    "ai-system/skills/**/*.md",
)

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
                "content_hash": "",
                "last_reviewed_content_hash": "",
                "declared_status": "",
                "declared_status_raw": "",
                "declared_status_source": "",
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


def require_optional_string(obj, key, path, errors):
    if key in obj:
        require_string(obj.get(key), path + "." + key, errors)


def require_optional_hash(obj, key, path, errors):
    value = obj.get(key)
    if value in (None, ""):
        return
    if not isinstance(value, str):
        errors.append("{}.{} must be a string".format(path, key))
        return
    if not re.fullmatch(r"[0-9a-f]{64}", value):
        errors.append("{}.{} must be a sha256 hex digest".format(path, key))


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
    if lower.endswith("/skill.md") or lower == "skill.md":
        return "guide"
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


def short_hash(value):
    return value[:12] if value else "-"


def normalize_declared_status(value):
    cleaned = value.strip().strip("\"'`").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    normalized = cleaned.lower().replace("_", " ").replace("-", " ")
    return DECLARED_STATUS_ALIASES.get(normalized)


def parse_frontmatter_status(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            for frontmatter_line in lines[1:i]:
                match = re.match(r"\s*status\s*:\s*(.+?)\s*(?:#.*)?$", frontmatter_line, re.IGNORECASE)
                if match:
                    raw = match.group(1).strip()
                    return raw, normalize_declared_status(raw), "frontmatter"
            return None
    return None


def parse_status_field(text):
    for line in text.splitlines()[:40]:
        match = re.match(r"\s*Status\s*:\s*(.+?)\s*$", line, re.IGNORECASE)
        if match:
            raw = match.group(1).strip()
            return raw, normalize_declared_status(raw), "status_field"
    return None


def parse_status_section(text):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not re.match(r"^#{2,6}\s+Status\s*$", line.strip(), re.IGNORECASE):
            continue
        for next_line in lines[i + 1 :]:
            value = next_line.strip().strip("*_`")
            if not value:
                continue
            if value.startswith("#"):
                return None
            return value, normalize_declared_status(value), "status_section"
    return None


def parse_declared_status(text):
    for parser in (parse_frontmatter_status, parse_status_field, parse_status_section):
        parsed = parser(text)
        if parsed:
            return parsed
    return "", "", ""


def content_hash_for_path(root, path):
    full_path = root / path
    if not full_path.exists() or not full_path.is_file():
        return ""
    digest = hashlib.sha256()
    with full_path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def declared_status_for_path(root, path):
    full_path = root / path
    if not full_path.exists() or not full_path.is_file():
        return "", "", ""
    try:
        text = full_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "", "", ""
    return parse_declared_status(text)


def refresh_doc_metadata(root, state):
    changed = 0
    for doc in state.get("docs", []):
        path = doc.get("path", "")
        before = {key: doc.get(key) for key in DOC_OPTIONAL_STRING_KEYS}
        doc.setdefault("last_reviewed_content_hash", "")
        try:
            normalized = normalize_doc_path(path)
        except DocError:
            doc["content_hash"] = ""
            doc["declared_status"] = ""
            doc["declared_status_raw"] = ""
            doc["declared_status_source"] = ""
        else:
            doc["content_hash"] = content_hash_for_path(root, normalized)
            raw, declared_status, source = declared_status_for_path(root, normalized)
            doc["declared_status"] = declared_status or ""
            doc["declared_status_raw"] = raw or ""
            doc["declared_status_source"] = source or ""
        after = {key: doc.get(key) for key in DOC_OPTIONAL_STRING_KEYS}
        if before != after:
            changed += 1
    return changed


def scan_markdown_files(root, scope):
    paths = set()

    def add_path(path):
        if path.is_file():
            paths.add(path.relative_to(root).as_posix())

    if scope in {"ai-system", "all"}:
        ai_system = root / "ai-system"
        if ai_system.exists():
            for path in ai_system.rglob("*.md"):
                add_path(path)

    if scope in {"root", "all"}:
        for pattern in ROOT_DOC_PATTERNS:
            for path in root.glob(pattern):
                add_path(path)

    if scope in {"skills", "all"}:
        for pattern in SKILL_DOC_PATTERNS:
            for path in root.glob(pattern):
                add_path(path)

    return sorted(paths)


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


def markdown_link_errors(root, doc_path):
    errors = []
    full_path = root / doc_path
    try:
        text = full_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        errors.append("{} invalid text encoding: {}".format(doc_path, exc))
        return errors

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
    return errors


def validate_markdown_links(root, doc_path, errors):
    errors.extend(markdown_link_errors(root, doc_path))


def unresolved_placeholder_errors(root, doc):
    errors = []
    path = doc.get("path")
    try:
        text = (root / path).read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        errors.append("{} invalid text encoding: {}".format(path, exc))
        return errors
    if re.search(r"\{\{[^{}\n]+\}\}", text):
        errors.append("{} contains unresolved {{PLACEHOLDER}}".format(path))
    return errors


def validate_no_unresolved_placeholders(root, doc, errors):
    errors.extend(unresolved_placeholder_errors(root, doc))


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
        for key in DOC_OPTIONAL_STRING_KEYS:
            require_optional_string(doc, key, path_name, errors)
        require_optional_hash(doc, "content_hash", path_name, errors)
        require_optional_hash(doc, "last_reviewed_content_hash", path_name, errors)

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


def add_gap(gaps, category, doc, message):
    gaps.append({"category": category, "doc": doc, "message": message})


def docs_gaps(state, root):
    gaps = []
    for doc in sorted_docs(state):
        path = doc.get("path")
        status = doc.get("status")
        doc_type = doc.get("type")
        try:
            normalized = normalize_doc_path(path)
        except DocError as exc:
            add_gap(gaps, "missing_file", doc, str(exc))
            continue

        exists = (root / normalized).exists()
        if not exists and status != "planned":
            add_gap(gaps, "missing_file", doc, "registered document is missing")

        if exists:
            actual_hash = content_hash_for_path(root, normalized)
            stored_hash = doc.get("content_hash", "")
            if not stored_hash:
                add_gap(gaps, "content_hash_stale", doc, "current content hash is not recorded")
            elif actual_hash and stored_hash != actual_hash:
                add_gap(gaps, "content_hash_stale", doc, "recorded content hash does not match file content")

            raw_status, declared_status, source = declared_status_for_path(root, normalized)
            if raw_status:
                if not declared_status:
                    add_gap(
                        gaps,
                        "status_mismatch",
                        doc,
                        "declared status `{}` from {} is not supported by docctl".format(raw_status, source),
                    )
                elif declared_status != status:
                    add_gap(
                        gaps,
                        "status_mismatch",
                        doc,
                        "registry status `{}` differs from declared status `{}` from {}".format(
                            status, declared_status, source
                        ),
                    )

            if status != "planned":
                for error in markdown_link_errors(root, normalized):
                    add_gap(gaps, "broken_local_link", doc, error)
            if status == "active" and doc_type != "template":
                for error in unresolved_placeholder_errors(root, doc):
                    add_gap(gaps, "unresolved_placeholder", doc, error)

            if status == "active":
                if not doc.get("last_reviewed_at"):
                    add_gap(gaps, "active_not_reviewed", doc, "active document has no recorded review")
                elif doc.get("last_reviewed_content_hash") != actual_hash:
                    add_gap(gaps, "active_review_stale", doc, "active review does not match current content hash")

        if status == "planned":
            add_gap(gaps, "not_active", doc, "planned document is not yet active")
        elif status in {"draft", "review", "deprecated", "archived"}:
            add_gap(gaps, "not_active", doc, "document is not active")
    return gaps


def validation_warnings(state, root):
    warnings = []
    warning_categories = {"status_mismatch", "content_hash_stale", "active_review_stale"}
    for gap in docs_gaps(state, root):
        if gap.get("category") not in warning_categories:
            continue
        doc = gap.get("doc", {})
        warnings.append("{}: {}".format(doc.get("path"), gap.get("message")))
    return warnings


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
        "| Path | Title | Type | Status | Declared | Required | Content hash | Last reviewed | Reviewed hash |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for doc in sorted_docs(state):
        lines.append(
            "| `{}` | {} | `{}` | `{}` | {} | `{}` | `{}` | {} | `{}` |".format(
                doc.get("path"),
                doc.get("title"),
                doc.get("type"),
                doc.get("status"),
                "`{}`".format(doc.get("declared_status")) if doc.get("declared_status") else "-",
                str(doc.get("required", False)).lower(),
                short_hash(doc.get("content_hash")),
                doc.get("last_reviewed_at") or "-",
                short_hash(doc.get("last_reviewed_content_hash")),
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
        "Tracked categories: {}".format(", ".join("`{}`".format(title) for _, title in DOC_GAP_CATEGORIES)),
        "",
    ]
    if not gaps:
        lines.append("_No documentation gaps detected._")
        lines.append("")
        return "\n".join(lines)

    for category, title in DOC_GAP_CATEGORIES:
        lines.append("## {}".format(title))
        lines.append("")
        category_gaps = [gap for gap in gaps if gap.get("category") == category]
        if not category_gaps:
            lines.append("_No gaps._")
            lines.append("")
            continue
        for gap in category_gaps:
            doc = gap.get("doc", {})
            lines.append(
                "- `{}` ({}, {}): {}".format(
                    doc.get("path"), doc.get("type"), doc.get("status"), gap.get("message")
                )
            )
        lines.append("")
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
    refresh_doc_metadata(root, state)
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
    refresh_doc_metadata(root, state)
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
                "content_hash": "",
                "last_reviewed_content_hash": "",
                "declared_status": "",
                "declared_status_raw": "",
                "declared_status_source": "",
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
    root = repo_root(args)
    path = normalize_doc_path(args.path)
    reviewed_hash = content_hash_for_path(root, path)

    def apply(state):
        doc = find_doc(state, args.path)
        doc["content_hash"] = reviewed_hash
        doc["last_reviewed_at"] = now
        doc["last_reviewed_by"] = actor(args)
        doc["last_reviewed_content_hash"] = reviewed_hash
        doc["updated_at"] = now
        if args.note:
            doc.setdefault("notes", []).append(args.note)

    mutate_state(
        args,
        "doc mark-reviewed",
        "doc",
        path,
        {"reviewed_at": now, "content_hash": reviewed_hash, "note": args.note or ""},
        apply,
    )


def cmd_scan(args):
    root = repo_root(args)
    markdown_files = scan_markdown_files(root, args.scope)
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
                    "content_hash": "",
                    "last_reviewed_content_hash": "",
                    "declared_status": "",
                    "declared_status_raw": "",
                    "declared_status_source": "",
                    "notes": [],
                    "created_at": now,
                    "updated_at": now,
                }
            )
            existing.add(path)
            added.append(path)

    mutate_state(args, "scan", "docs", "docs", {"added": added, "status": args.status, "scope": args.scope}, apply)
    print("Added: {}".format(len(added)))


def cmd_validate(args):
    root = repo_root(args)
    state = load_docs(root)
    require_valid_docs(state, root)
    warnings = validation_warnings(state, root)
    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print("- {}".format(warning))
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
        warnings = validation_warnings(state, root)
        if warnings:
            print("Warnings:")
            for warning in warnings:
                print("- {}".format(warning))


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

    p_scan = sub.add_parser("scan", help="Register untracked Markdown documents and refresh doc metadata")
    p_scan.add_argument("--scope", default="ai-system", choices=["ai-system", "root", "skills", "all"])
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

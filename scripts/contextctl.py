#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
contextctl.py - deterministic Context Pack gateway.

Builds derived Context Packs from registered documentation and task state.
The generated Context Pack is readable output only; it is not source of truth
and does not expand task scope, allowed files, or acceptance criteria.

Files:
  AI_PROJECT/events/context-events.jsonl
  AI_PROJECT/generated/CONTEXT_PACK.md
  AI_PROJECT/generated/CONTEXT_STATUS.md
"""

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ai_project_ctl.core.legacy import (  # noqa: E402
    append_audit_event,
    atomic_write_text as core_atomic_write_text,
    events_dir as core_events_dir,
    generated_dir as core_generated_dir,
    state_dir as core_state_dir,
    utc_now as core_utc_now,
)


CONTEXT_SCHEMA_VERSION = 1
GENERATED_HEADER = "<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->"
CONTEXT_METADATA_PREFIX = "<!-- Context: "
CONTEXT_METADATA_SUFFIX = " -->"

ACTIVE_STATUS = "active"
INACTIVE_STATUSES = {"planned", "draft", "review"}
DEPRECATED_STATUSES = {"deprecated"}
ARCHIVED_STATUSES = {"archived"}

DEFAULT_LIMIT = 8
MAX_SNIPPET_CHARS = 1400
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_-]*", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


class ContextError(Exception):
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


def docs_path(root):
    return state_dir(root) / "docs.json"


def tasks_path(root):
    return state_dir(root) / "tasks.json"


def context_events_path(root):
    return events_dir(root) / "context-events.jsonl"


def generated_pack_path(root):
    return generated_dir(root) / "CONTEXT_PACK.md"


def generated_status_path(root):
    return generated_dir(root) / "CONTEXT_STATUS.md"


def ensure_project_dirs(root):
    events_dir(root).mkdir(parents=True, exist_ok=True)
    generated_dir(root).mkdir(parents=True, exist_ok=True)


def atomic_write_text(path, text):
    core_atomic_write_text(path, text)


def read_json(path, missing_message):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise ContextError(missing_message)
    except json.JSONDecodeError as exc:
        raise ContextError("INVALID_JSON: {}:{}:{} {}".format(path, exc.lineno, exc.colno, exc.msg))


def load_docs(root):
    return read_json(docs_path(root), "DOCS_NOT_INITIALIZED: run `python scripts/docctl.py init` first")


def load_tasks(root, required=True):
    path = tasks_path(root)
    if not path.exists():
        if required:
            raise ContextError("TASKS_NOT_INITIALIZED: run `python scripts/taskctl.py init` first")
        return None
    return read_json(path, "TASKS_NOT_INITIALIZED")


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def short_hash(value):
    return value[:12] if value else "-"


def normalize_repo_path(path_text):
    path = Path(path_text)
    if path.is_absolute():
        raise ContextError("INVALID_SOURCE_PATH: path must be repository-relative")
    normalized = path.as_posix().strip()
    if not normalized or normalized.startswith("../") or "/../" in normalized:
        raise ContextError("INVALID_SOURCE_PATH: {}".format(path_text))
    return normalized


def tokenize(text):
    return [match.group(0).lower() for match in TOKEN_RE.finditer(text or "")]


def trim_snippet(text, limit=MAX_SNIPPET_CHARS):
    cleaned = text.strip()
    if len(cleaned) <= limit:
        return cleaned
    trimmed = cleaned[:limit].rstrip()
    last_break = max(trimmed.rfind("\n"), trimmed.rfind(". "), trimmed.rfind("; "))
    if last_break > limit // 2:
        trimmed = trimmed[: last_break + 1].rstrip()
    return trimmed + "\n\n[...truncated by contextctl...]"


def markdown_chunks(path, text):
    lines = text.splitlines()
    chunks = []
    stack = []
    current_heading = "(preamble)"
    current_level = 0
    start_line = 1
    buffer = []

    def emit(end_line):
        body = "\n".join(buffer).strip()
        if not body:
            return
        heading_path = " > ".join(title for _, title in stack) if stack else current_heading
        chunks.append(
            {
                "path": path,
                "heading": heading_path,
                "level": current_level,
                "start_line": start_line,
                "end_line": end_line,
                "text": body,
                "chunk_hash": sha256_text("{}:{}:{}\n{}".format(path, start_line, heading_path, body)),
            }
        )

    for line_no, line in enumerate(lines, start=1):
        match = HEADING_RE.match(line)
        if match:
            emit(line_no - 1)
            level = len(match.group(1))
            title = match.group(2).strip()
            stack[:] = [(lvl, text) for lvl, text in stack if lvl < level]
            stack.append((level, title))
            current_heading = title
            current_level = level
            start_line = line_no
            buffer = [line]
            continue
        buffer.append(line)

    emit(len(lines))
    return chunks


def validate_docs_state(state):
    errors = []
    if not isinstance(state, dict):
        return ["docs state must be an object"]
    if "revision" not in state:
        errors.append("docs_state missing revision")
    if not isinstance(state.get("docs"), list):
        errors.append("docs_state.docs must be a list")
    for index, doc in enumerate(state.get("docs", [])):
        for key in ("path", "title", "type", "status"):
            if not isinstance(doc.get(key), str):
                errors.append("docs[{}].{} must be a string".format(index, key))
    return errors


def validate_tasks_state(state):
    if state is None:
        return []
    errors = []
    if not isinstance(state, dict):
        return ["tasks state must be an object"]
    if "revision" not in state:
        errors.append("tasks_state missing revision")
    if not isinstance(state.get("tasks"), list):
        errors.append("tasks_state.tasks must be a list")
    return errors


def is_generated_path(path, doc_type):
    return doc_type == "generated" or path.startswith("AI_PROJECT/generated/")


def is_template_path(path, doc_type):
    return doc_type == "template" or "/templates/" in path or path.startswith("ai-system/templates/")


def is_example_path(path):
    return path.startswith("examples/")


def inclusion_decision(doc, args):
    path = doc.get("path", "")
    status = doc.get("status", "")
    doc_type = doc.get("type", "")

    if is_generated_path(path, doc_type) and not args.include_generated:
        return False, "generated output excluded by default"
    if is_template_path(path, doc_type) and not args.include_templates:
        return False, "template document excluded by default"
    if is_example_path(path) and not args.include_examples:
        return False, "example document excluded by default"
    if status in ARCHIVED_STATUSES and not args.include_archived:
        return False, "archived document excluded by default"
    if status in DEPRECATED_STATUSES and not args.include_deprecated:
        return False, "deprecated document excluded by default"
    if status in INACTIVE_STATUSES and not args.include_inactive:
        return False, "inactive document excluded by default"
    if status != ACTIVE_STATUS and not (
        args.include_inactive or args.include_deprecated or args.include_archived
    ):
        return False, "non-active document excluded by default"
    return True, "included"


def filter_options(args):
    return {
        "include_archived": bool(args.include_archived),
        "include_deprecated": bool(args.include_deprecated),
        "include_examples": bool(args.include_examples),
        "include_generated": bool(args.include_generated),
        "include_inactive": bool(args.include_inactive),
        "include_templates": bool(args.include_templates),
    }


def build_context_index(root, args):
    docs_state = load_docs(root)
    errors = validate_docs_state(docs_state)
    if errors:
        raise ContextError("DOCS_VALIDATION_FAILED:\n- " + "\n- ".join(errors))

    included = []
    excluded = []
    chunks = []

    for doc in sorted(docs_state.get("docs", []), key=lambda item: item.get("path", "")):
        try:
            path = normalize_repo_path(doc.get("path", ""))
        except ContextError as exc:
            excluded.append({"path": doc.get("path", ""), "reason": str(exc)})
            continue

        include, reason = inclusion_decision(doc, args)
        full_path = root / path
        if not full_path.exists() or not full_path.is_file():
            excluded.append({"path": path, "reason": "source file missing"})
            continue
        if not include:
            excluded.append({"path": path, "reason": reason})
            continue

        try:
            text = full_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            excluded.append({"path": path, "reason": "invalid text encoding: {}".format(exc)})
            continue

        content_hash = sha256_file(full_path)
        doc_info = {
            "path": path,
            "title": doc.get("title") or path,
            "type": doc.get("type") or "",
            "status": doc.get("status") or "",
            "content_hash": content_hash,
            "registry_content_hash": doc.get("content_hash") or "",
        }
        included.append(doc_info)

        for chunk in markdown_chunks(path, text):
            metadata_text = " ".join(
                [
                    path,
                    doc_info["title"],
                    doc_info["type"],
                    doc_info["status"],
                    chunk["heading"],
                ]
            )
            chunk.update(
                {
                    "title": doc_info["title"],
                    "type": doc_info["type"],
                    "status": doc_info["status"],
                    "content_hash": content_hash,
                    "registry_content_hash": doc_info["registry_content_hash"],
                    "metadata_tokens": Counter(tokenize(metadata_text)),
                    "heading_tokens": Counter(tokenize(chunk["heading"])),
                    "content_tokens": Counter(tokenize(chunk["text"])),
                }
            )
            chunks.append(chunk)

    return {
        "docs_revision": docs_state.get("revision", 0),
        "included_docs": included,
        "excluded_sources": excluded,
        "chunks": chunks,
        "filters": filter_options(args),
    }


def score_chunk(chunk, query):
    query_tokens = Counter(tokenize(query))
    query_text = " ".join(tokenize(query))
    score = 0
    reasons = []

    heading_hits = []
    metadata_hits = []
    content_hits = []

    for token, count in sorted(query_tokens.items()):
        if token in chunk["heading_tokens"]:
            score += 4 * min(count, chunk["heading_tokens"][token])
            heading_hits.append(token)
        if token in chunk["metadata_tokens"]:
            score += 3 * min(count, chunk["metadata_tokens"][token])
            metadata_hits.append(token)
        if token in chunk["content_tokens"]:
            score += 2 * min(count, chunk["content_tokens"][token])
            content_hits.append(token)

    lower_query = query.strip().lower()
    if lower_query:
        if lower_query in chunk["heading"].lower():
            score += 10
            reasons.append("exact query phrase appears in heading")
        metadata_text = "{} {} {}".format(chunk["path"], chunk["title"], chunk["type"]).lower()
        if lower_query in metadata_text:
            score += 7
            reasons.append("exact query phrase appears in metadata")
        if lower_query in chunk["text"].lower():
            score += 5
            reasons.append("exact query phrase appears in content")

    if query_text:
        normalized_content = " ".join(tokenize(chunk["text"]))
        if query_text in normalized_content:
            score += 3
            reasons.append("normalized query tokens appear in content order")

    if heading_hits:
        reasons.append("heading token match: {}".format(", ".join(heading_hits[:8])))
    if metadata_hits:
        reasons.append("metadata token match: {}".format(", ".join(metadata_hits[:8])))
    if content_hits:
        reasons.append("content token match: {}".format(", ".join(content_hits[:8])))

    return score, reasons


def search_index(index, query, limit):
    results = []
    for chunk in index["chunks"]:
        score, reasons = score_chunk(chunk, query)
        if score <= 0:
            continue
        result = dict(chunk)
        result["score"] = score
        result["reasons"] = reasons or ["deterministic keyword match"]
        results.append(result)

    results.sort(
        key=lambda item: (
            -item["score"],
            item["path"],
            item["start_line"],
            item["heading"],
            item["chunk_hash"],
        )
    )
    return results[:limit]


def find_task(tasks_state, task_id):
    for task in tasks_state.get("tasks", []):
        if task.get("id") == task_id:
            return task
    raise ContextError("TASK_NOT_FOUND: {}".format(task_id))


def as_list(value):
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value]
    return []


def task_query(task):
    fields = [
        task.get("id", ""),
        task.get("title", ""),
        task.get("summary", ""),
        task.get("description", ""),
        task.get("active_document", ""),
        task.get("expected_result", ""),
    ]
    for key in ("scope", "out_of_scope", "allowed_files", "acceptance_criteria", "review_instructions"):
        fields.extend(as_list(task.get(key)))
    return " ".join(part for part in fields if part).strip()


def task_boundary(task):
    if not task:
        return None
    return {
        "id": task.get("id", ""),
        "status": task.get("status", ""),
        "title": task.get("title", ""),
        "scope": as_list(task.get("scope")),
        "out_of_scope": as_list(task.get("out_of_scope")),
        "allowed_files": as_list(task.get("allowed_files")),
        "acceptance_criteria": as_list(task.get("acceptance_criteria")),
    }


def metadata_from_args(args, query, task_id="", explicit_query=False):
    return {
        "schema_version": CONTEXT_SCHEMA_VERSION,
        "mode": "task" if task_id else "query",
        "task_id": task_id,
        "explicit_query": bool(explicit_query),
        "query": query,
        "limit": int(args.limit),
        "filters": filter_options(args),
    }


def metadata_args(namespace, metadata):
    args = argparse.Namespace(**vars(namespace))
    for key, value in metadata.get("filters", {}).items():
        setattr(args, key, value)
    args.limit = int(metadata.get("limit", DEFAULT_LIMIT))
    return args


def excluded_summary(excluded_sources):
    grouped = defaultdict(list)
    for item in excluded_sources:
        grouped[item.get("reason", "excluded")].append(item.get("path", ""))
    return [
        {
            "reason": reason,
            "count": len(paths),
            "sample_paths": sorted(paths)[:20],
        }
        for reason, paths in sorted(grouped.items())
    ]


def build_pack_model(root, args, metadata):
    local_args = metadata_args(args, metadata)
    index = build_context_index(root, local_args)
    tasks_state = load_tasks(root, required=False)
    task = None
    query = metadata.get("query", "")

    if metadata.get("mode") == "task":
        tasks_state = load_tasks(root, required=True)
        task = find_task(tasks_state, metadata.get("task_id", ""))
        if not metadata.get("explicit_query"):
            query = task_query(task)
            metadata = dict(metadata)
            metadata["query"] = query

    selected = search_index(index, query, int(metadata.get("limit", DEFAULT_LIMIT)))

    return {
        "metadata": metadata,
        "query": query,
        "docs_revision": index["docs_revision"],
        "tasks_revision": tasks_state.get("revision", 0) if tasks_state else None,
        "included_docs": index["included_docs"],
        "excluded_sources": index["excluded_sources"],
        "excluded_summary": excluded_summary(index["excluded_sources"]),
        "chunk_count": len(index["chunks"]),
        "selected": selected,
        "task_boundary": task_boundary(task),
    }


def metadata_comment(metadata):
    payload = json.dumps(metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "{}{}{}".format(CONTEXT_METADATA_PREFIX, payload, CONTEXT_METADATA_SUFFIX)


def parse_pack_metadata(path):
    if not path.exists():
        raise ContextError("NO_CONTEXT_PACK: build one with `python scripts/contextctl.py pack build --write`")
    for line in path.read_text(encoding="utf-8").splitlines()[:10]:
        if line.startswith(CONTEXT_METADATA_PREFIX) and line.endswith(CONTEXT_METADATA_SUFFIX):
            raw = line[len(CONTEXT_METADATA_PREFIX) : -len(CONTEXT_METADATA_SUFFIX)]
            try:
                metadata = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ContextError("INVALID_CONTEXT_METADATA: {}".format(exc))
            if metadata.get("schema_version") != CONTEXT_SCHEMA_VERSION:
                raise ContextError("UNSUPPORTED_CONTEXT_METADATA_VERSION: {}".format(metadata.get("schema_version")))
            return metadata
    raise ContextError("MISSING_CONTEXT_METADATA: {}".format(path))


def markdown_list(lines, items, empty_text):
    if not items:
        lines.append("- {}".format(empty_text))
        return
    for item in items:
        lines.append("- {}".format(item))


def render_pack_markdown(model):
    metadata = model["metadata"]
    boundary = model.get("task_boundary")
    lines = [
        GENERATED_HEADER,
        "<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->",
        metadata_comment(metadata),
        "",
        "# Context Pack",
        "",
        "This generated Context Pack is derived output only. It is not source of truth.",
        "It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.",
        "",
        "Mode: `{}`".format(metadata.get("mode")),
        "Task ID: `{}`".format(metadata.get("task_id") or "none"),
        "Explicit query: `{}`".format(str(metadata.get("explicit_query", False)).lower()),
        "Limit: `{}`".format(metadata.get("limit")),
        "Docs revision: `{}`".format(model.get("docs_revision")),
        "Tasks revision: `{}`".format(model.get("tasks_revision") if model.get("tasks_revision") is not None else "none"),
        "",
        "## Query",
        "",
        "```text",
        model.get("query", ""),
        "```",
        "",
    ]

    if boundary:
        lines.extend(
            [
                "## Task Boundary Snapshot",
                "",
                "Task: `{}` - {}".format(boundary.get("id"), boundary.get("title")),
                "Status: `{}`".format(boundary.get("status")),
                "",
                "Scope:",
            ]
        )
        markdown_list(lines, boundary.get("scope"), "_No scope recorded._")
        lines.append("")
        lines.append("Allowed Files:")
        markdown_list(lines, boundary.get("allowed_files"), "_No allowed files recorded._")
        lines.append("")
        lines.append("Acceptance Criteria:")
        markdown_list(lines, boundary.get("acceptance_criteria"), "_No acceptance criteria recorded._")
        lines.append("")

    lines.extend(
        [
            "## Index Summary",
            "",
            "Indexed source documents: `{}`".format(len(model.get("included_docs", []))),
            "Indexed chunks: `{}`".format(model.get("chunk_count", 0)),
            "Excluded registered sources: `{}`".format(len(model.get("excluded_sources", []))),
            "Selected chunks: `{}`".format(len(model.get("selected", []))),
            "",
            "Default exclusion policy: generated, inactive, archived, deprecated, template, and example documents are excluded unless explicitly allowed.",
            "",
            "## Selected Sources",
            "",
        ]
    )

    if not model.get("selected"):
        lines.append("_No matching chunks selected._")
        lines.append("")
    else:
        lines.append("| Score | Source | Heading | Lines | Content hash | Chunk hash | Reasons |")
        lines.append("| ---: | --- | --- | --- | --- | --- | --- |")
        for item in model["selected"]:
            lines.append(
                "| {} | `{}` | {} | {}-{} | `{}` | `{}` | {} |".format(
                    item.get("score"),
                    item.get("path"),
                    item.get("heading").replace("|", "\\|"),
                    item.get("start_line"),
                    item.get("end_line"),
                    short_hash(item.get("content_hash")),
                    short_hash(item.get("chunk_hash")),
                    "; ".join(item.get("reasons", [])).replace("|", "\\|"),
                )
            )
        lines.append("")

    lines.append("## Selected Context")
    lines.append("")
    for index, item in enumerate(model.get("selected", []), start=1):
        lines.append("### {}. `{}`".format(index, item.get("path")))
        lines.append("")
        lines.append("Title: {}".format(item.get("title")))
        lines.append("Status: `{}`  Type: `{}`".format(item.get("status"), item.get("type")))
        lines.append("Heading: {}".format(item.get("heading")))
        lines.append("Lines: `{}-{}`".format(item.get("start_line"), item.get("end_line")))
        lines.append("Score: `{}`".format(item.get("score")))
        lines.append("Content hash: `{}`".format(item.get("content_hash")))
        lines.append("Chunk hash: `{}`".format(item.get("chunk_hash")))
        lines.append("Reasons: {}".format("; ".join(item.get("reasons", []))))
        lines.append("")
        lines.append("```text")
        lines.append(trim_snippet(item.get("text", "")))
        lines.append("```")
        lines.append("")

    lines.append("## Excluded Source Summary")
    lines.append("")
    if not model.get("excluded_summary"):
        lines.append("_No registered sources were excluded._")
    else:
        for group in model["excluded_summary"]:
            lines.append("- {}: `{}`".format(group["reason"], group["count"]))
            for path in group["sample_paths"]:
                lines.append("  - `{}`".format(path))
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_status_markdown(model):
    metadata = model.get("metadata", {})
    lines = [
        GENERATED_HEADER,
        "<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->",
        metadata_comment(metadata),
        "",
        "# Context Status",
        "",
        "Context pack exists: `true`",
        "Mode: `{}`".format(metadata.get("mode")),
        "Task ID: `{}`".format(metadata.get("task_id") or "none"),
        "Limit: `{}`".format(metadata.get("limit")),
        "Docs revision: `{}`".format(model.get("docs_revision")),
        "Tasks revision: `{}`".format(model.get("tasks_revision") if model.get("tasks_revision") is not None else "none"),
        "Indexed source documents: `{}`".format(len(model.get("included_docs", []))),
        "Indexed chunks: `{}`".format(model.get("chunk_count", 0)),
        "Selected chunks: `{}`".format(len(model.get("selected", []))),
        "Excluded registered sources: `{}`".format(len(model.get("excluded_sources", []))),
        "",
        "## Selected Source Paths",
        "",
    ]
    selected_paths = sorted({item.get("path") for item in model.get("selected", [])})
    markdown_list(lines, selected_paths, "_No selected source paths._")
    lines.append("")
    lines.append("## Exclusion Reasons")
    lines.append("")
    for group in model.get("excluded_summary", []):
        lines.append("- {}: `{}`".format(group["reason"], group["count"]))
    if not model.get("excluded_summary"):
        lines.append("- _No exclusions._")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_empty_status_markdown(root):
    return "\n".join(
        [
            GENERATED_HEADER,
            "<!-- Source: contextctl.py status -->",
            "",
            "# Context Status",
            "",
            "Context pack exists: `false`",
            "Context pack path: `{}`".format(generated_pack_path(root)),
            "",
        ]
    )


def next_event_revision(root):
    path = context_events_path(root)
    if not path.exists():
        return None, 1
    count = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    return count, count + 1


def append_event(root, actor, command, entity_type, entity_id, payload):
    before, after = next_event_revision(root)
    append_audit_event(
        context_events_path(root),
        actor=actor,
        command=command,
        entity_type=entity_type,
        entity_id=entity_id,
        revision_before=before,
        revision_after=after,
        payload=payload,
    )


def write_context_outputs(root, args, model, command):
    ensure_project_dirs(root)
    atomic_write_text(generated_pack_path(root), render_pack_markdown(model))
    atomic_write_text(generated_status_path(root), render_status_markdown(model))
    append_event(
        root=root,
        actor=args.actor,
        command=command,
        entity_type="context_pack",
        entity_id=model["metadata"].get("task_id") or "query",
        payload={
            "mode": model["metadata"].get("mode"),
            "task_id": model["metadata"].get("task_id") or "",
            "query": model.get("query", ""),
            "pack_path": str(generated_pack_path(root)),
            "status_path": str(generated_status_path(root)),
            "selected_chunks": len(model.get("selected", [])),
        },
    )


def validate_event_log(root):
    errors = []
    path = context_events_path(root)
    if not path.exists():
        return errors
    required = {
        "event_id",
        "timestamp",
        "actor",
        "command",
        "entity_type",
        "entity_id",
        "revision_before",
        "revision_after",
        "payload",
    }
    seen = set()
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append("INVALID_EVENT_JSONL: {}:{} {}".format(path, line_no, exc))
            continue
        missing = sorted(required - set(event.keys()))
        if missing:
            errors.append("INVALID_EVENT_FIELDS: line {} missing {}".format(line_no, ", ".join(missing)))
        if event.get("event_id") in seen:
            errors.append("DUPLICATE_EVENT_ID: {}".format(event.get("event_id")))
        seen.add(event.get("event_id"))
        if not isinstance(event.get("payload", {}), dict):
            errors.append("INVALID_EVENT_PAYLOAD: line {} payload must be object".format(line_no))
    return errors


def expected_outputs_from_pack(root, args):
    metadata = parse_pack_metadata(generated_pack_path(root))
    model = build_pack_model(root, args, metadata)
    return {
        generated_pack_path(root): render_pack_markdown(model),
        generated_status_path(root): render_status_markdown(model),
    }


def cmd_status(args):
    root = repo_root(args)
    index = build_context_index(root, args)
    print("State docs: {}".format(docs_path(root)))
    print("State tasks: {}".format(tasks_path(root)))
    print("Events: {}".format(context_events_path(root)))
    print("Generated pack: {}".format(generated_pack_path(root)))
    print("Generated status: {}".format(generated_status_path(root)))
    print("Indexed source documents: {}".format(len(index["included_docs"])))
    print("Indexed chunks: {}".format(len(index["chunks"])))
    print("Excluded registered sources: {}".format(len(index["excluded_sources"])))
    if generated_pack_path(root).exists():
        try:
            metadata = parse_pack_metadata(generated_pack_path(root))
            print("Current context mode: {}".format(metadata.get("mode")))
            print("Current context task: {}".format(metadata.get("task_id") or "none"))
        except ContextError as exc:
            print("Current context metadata: ERROR {}".format(exc))
    else:
        print("Current context pack: none")


def cmd_index_build(args):
    root = repo_root(args)
    index = build_context_index(root, args)
    if args.json:
        print(
            json.dumps(
                {
                    "docs_revision": index["docs_revision"],
                    "included_documents": len(index["included_docs"]),
                    "indexed_chunks": len(index["chunks"]),
                    "excluded_sources": len(index["excluded_sources"]),
                    "filters": index["filters"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    print("OK: context index built")
    print("Docs revision: {}".format(index["docs_revision"]))
    print("Indexed source documents: {}".format(len(index["included_docs"])))
    print("Indexed chunks: {}".format(len(index["chunks"])))
    print("Excluded registered sources: {}".format(len(index["excluded_sources"])))
    for group in excluded_summary(index["excluded_sources"]):
        print("Excluded: {} ({})".format(group["reason"], group["count"]))


def cmd_search(args):
    root = repo_root(args)
    index = build_context_index(root, args)
    results = search_index(index, args.query, args.limit)
    if args.json:
        serializable = []
        for item in results:
            serializable.append(
                {
                    "score": item["score"],
                    "path": item["path"],
                    "heading": item["heading"],
                    "start_line": item["start_line"],
                    "end_line": item["end_line"],
                    "content_hash": item["content_hash"],
                    "chunk_hash": item["chunk_hash"],
                    "reasons": item["reasons"],
                }
            )
        print(json.dumps(serializable, ensure_ascii=False, indent=2))
        return
    print("Query: {}".format(args.query))
    print("Indexed source documents: {}".format(len(index["included_docs"])))
    print("Indexed chunks: {}".format(len(index["chunks"])))
    print("Matches: {}".format(len(results)))
    for item in results:
        print(
            "- score={} path={} lines={}-{} heading={} chunk={} reasons={}".format(
                item["score"],
                item["path"],
                item["start_line"],
                item["end_line"],
                item["heading"],
                short_hash(item["chunk_hash"]),
                "; ".join(item["reasons"]),
            )
        )


def cmd_pack_build(args):
    root = repo_root(args)
    if args.task:
        tasks_state = load_tasks(root, required=True)
        task = find_task(tasks_state, args.task)
        query = args.query.strip() if args.query else task_query(task)
        metadata = metadata_from_args(args, query=query, task_id=args.task, explicit_query=bool(args.query))
    else:
        query = args.query.strip()
        if not query:
            raise ContextError("MISSING_QUERY: use --query or --task")
        metadata = metadata_from_args(args, query=query)

    model = build_pack_model(root, args, metadata)
    if args.write:
        write_context_outputs(root, args, model, "context.pack.build")
        print("OK: context pack written {}".format(generated_pack_path(root)))
        print("OK: context status written {}".format(generated_status_path(root)))
        print("Selected chunks: {}".format(len(model["selected"])))
        return
    print(render_pack_markdown(model), end="")


def cmd_validate(args):
    root = repo_root(args)
    docs_state = load_docs(root)
    tasks_state = load_tasks(root, required=False)
    errors = []
    errors.extend(validate_docs_state(docs_state))
    errors.extend(validate_tasks_state(tasks_state))
    errors.extend(validate_event_log(root))
    for path in (generated_pack_path(root), generated_status_path(root)):
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith(GENERATED_HEADER):
            errors.append("MISSING_GENERATED_HEADER: {}".format(path))
    if generated_pack_path(root).exists():
        parse_pack_metadata(generated_pack_path(root))
    if errors:
        raise ContextError("VALIDATION_FAILED:\n- " + "\n- ".join(errors))
    print("OK: context control files are valid")


def cmd_render(args):
    root = repo_root(args)
    if not generated_pack_path(root).exists():
        ensure_project_dirs(root)
        atomic_write_text(generated_status_path(root), render_empty_status_markdown(root))
        append_event(
            root=root,
            actor=args.actor,
            command="context.render",
            entity_type="context_pack",
            entity_id="none",
            payload={"status_path": str(generated_status_path(root)), "pack_exists": False},
        )
        print("OK: rendered empty context status")
        return
    metadata = parse_pack_metadata(generated_pack_path(root))
    model = build_pack_model(root, args, metadata)
    write_context_outputs(root, args, model, "context.render")
    print("OK: rendered context outputs")


def cmd_check_generated(args):
    root = repo_root(args)
    expected = expected_outputs_from_pack(root, args)
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
        raise ContextError("CHECK_GENERATED_FAILED:\n- " + "\n- ".join(errors))
    print("OK: generated context files are up to date")


def cmd_audit(args):
    root = repo_root(args)
    path = context_events_path(root)
    if not path.exists():
        raise ContextError("CONTEXT_AUDIT_NOT_FOUND: no audit events")
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for line in lines[-args.last :]:
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


def add_common_args(parser):
    parser.add_argument("--root", default=".", help="Repository/project root. Default: current directory.")
    parser.add_argument("--actor", default=os.environ.get("AI_DEV_ACTOR", "human_owner"))


def add_filter_args(parser):
    parser.add_argument("--include-inactive", action="store_true", help="Include planned/draft/review registered docs")
    parser.add_argument("--include-deprecated", action="store_true", help="Include deprecated registered docs")
    parser.add_argument("--include-archived", action="store_true", help="Include archived registered docs")
    parser.add_argument("--include-templates", action="store_true", help="Include template documents")
    parser.add_argument("--include-generated", action="store_true", help="Include generated project-control docs")
    parser.add_argument("--include-examples", action="store_true", help="Include example documents")


def add_limit_arg(parser):
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Maximum selected chunks")


def build_parser():
    parser = argparse.ArgumentParser(description="Deterministic Context Pack CLI for AI Development System")
    add_common_args(parser)
    add_filter_args(parser)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("status", help="Show context-control status")
    p.set_defaults(func=cmd_status)

    p_index = sub.add_parser("index", help="Build derived context index")
    index_sub = p_index.add_subparsers(dest="index_command", required=True)
    p = index_sub.add_parser("build", help="Build the derived index and print a summary")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_index_build)

    p = sub.add_parser("search", help="Search registered source docs")
    p.add_argument("--query", required=True)
    add_limit_arg(p)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_search)

    p_pack = sub.add_parser("pack", help="Build Context Pack")
    pack_sub = p_pack.add_subparsers(dest="pack_command", required=True)
    p = pack_sub.add_parser("build", help="Build a Context Pack for a task or query")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--task", help="Task ID, for example TASK-009")
    group.add_argument("--query", help="Explicit search query")
    p.add_argument("--write", action="store_true", help="Write CONTEXT_PACK.md and CONTEXT_STATUS.md")
    add_limit_arg(p)
    p.set_defaults(func=cmd_pack_build)

    p = sub.add_parser("validate", help="Validate context-control files")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("render", help="Regenerate context generated outputs from existing metadata")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("check-generated", help="Check generated context files are up to date")
    p.set_defaults(func=cmd_check_generated)

    p = sub.add_parser("audit", help="Show context audit events")
    p.add_argument("--last", type=int, default=20)
    p.set_defaults(func=cmd_audit)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except ContextError as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

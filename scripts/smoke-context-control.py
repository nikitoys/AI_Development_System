#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Smoke test for context control.

Runs contextctl.py against a temporary project root and verifies:
- deterministic index/search behavior;
- default exclusion of inactive/template/example/deprecated/generated docs;
- Context Pack and Context Status generation;
- codexctl.py prompt generation with and without Context Pack;
- check-generated drift detection and render repair;
- context audit events.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CONTEXTCTL = REPO_ROOT / "scripts" / "contextctl.py"
CODEXCTL = REPO_ROOT / "scripts" / "codexctl.py"


def run_tool(tool, root, *args, expect_success=True, must_contain=None):
    command = [sys.executable, str(tool), "--root", str(root), "--actor", "smoke_test", *args]
    result = subprocess.run(command, cwd=str(REPO_ROOT), text=True, capture_output=True, check=False)
    output = (result.stdout or "") + (result.stderr or "")

    if expect_success and result.returncode != 0:
        raise SystemExit("command failed unexpectedly:\n{}\n{}".format(" ".join(command), output))
    if not expect_success and result.returncode == 0:
        raise SystemExit("command succeeded but failure was expected:\n{}\n{}".format(" ".join(command), output))

    if must_contain:
        items = [must_contain] if isinstance(must_contain, str) else must_contain
        for item in items:
            if item not in output:
                raise SystemExit("expected output to contain {!r}\ncommand: {}\noutput:\n{}".format(item, command, output))

    return output


def run(root, *args, expect_success=True, must_contain=None):
    return run_tool(CONTEXTCTL, root, *args, expect_success=expect_success, must_contain=must_contain)


def run_codex(root, *args, expect_success=True, must_contain=None):
    return run_tool(CODEXCTL, root, *args, expect_success=expect_success, must_contain=must_contain)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_fixture_file(root, path, text):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def fixture_doc(path, title, doc_type="reference", status="active"):
    return {
        "id": "DOC-" + str(abs(hash(path)) % 100000).zfill(5),
        "path": path,
        "title": title,
        "type": doc_type,
        "status": status,
        "required": False,
        "owner": "AI System Maintainer",
        "last_reviewed_at": "",
        "last_reviewed_by": "",
        "content_hash": "",
        "last_reviewed_content_hash": "",
        "declared_status": "",
        "declared_status_raw": "",
        "declared_status_source": "",
        "notes": [],
        "created_at": "2026-06-17T00:00:00Z",
        "updated_at": "2026-06-17T00:00:00Z",
    }


def setup_fixture(root):
    write_fixture_file(
        root,
        "ai-system/project-control/context-source.md",
        "# Context Source\n\n"
        "## Prompt Package Context Retrieval\n\n"
        "Deterministic context retrieval selects prompt package guidance from registered source documents.\n",
    )
    write_fixture_file(
        root,
        "ai-system/draft-only.md",
        "# Draft Only\n\n"
        "## Prompt Package Context Retrieval\n\n"
        "This inactive draft should not be selected by default.\n",
    )
    write_fixture_file(
        root,
        "ai-system/templates/template-only.md",
        "# Template Only\n\nPrompt package context retrieval template text.\n",
    )
    write_fixture_file(
        root,
        "examples/golden-project/example.md",
        "# Golden Example\n\nPrompt package context retrieval example text.\n",
    )
    write_fixture_file(
        root,
        "AI_PROJECT/generated/generated-only.md",
        "# Generated\n\nPrompt package context retrieval generated text.\n",
    )
    write_fixture_file(
        root,
        "ai-system/deprecated-only.md",
        "# Deprecated\n\nPrompt package context retrieval deprecated text.\n",
    )

    docs = {
        "schema_version": 1,
        "revision": 3,
        "created_at": "2026-06-17T00:00:00Z",
        "updated_at": "2026-06-17T00:00:00Z",
        "docs": [
            fixture_doc("ai-system/project-control/context-source.md", "Context Source"),
            fixture_doc("ai-system/draft-only.md", "Draft Only", status="draft"),
            fixture_doc("ai-system/templates/template-only.md", "Template Only", doc_type="template"),
            fixture_doc("examples/golden-project/example.md", "Golden Example"),
            fixture_doc("AI_PROJECT/generated/generated-only.md", "Generated Only", doc_type="generated"),
            fixture_doc("ai-system/deprecated-only.md", "Deprecated Only", status="deprecated"),
        ],
    }
    write_json(root / "AI_PROJECT" / "state" / "docs.json", docs)

    tasks = {
        "schema_version": 1,
        "revision": 2,
        "current_task_id": "TASK-001",
        "created_at": "2026-06-17T00:00:00Z",
        "updated_at": "2026-06-17T00:00:00Z",
        "tasks": [
            {
                "id": "TASK-001",
                "epic_id": "EPIC-001",
                "title": "Build prompt package context retrieval",
                "status": "in_progress",
                "summary": "Find prompt package context retrieval guidance.",
                "description": "Use deterministic retrieval.",
                "scope": ["Build a Context Pack."],
                "out_of_scope": ["No vector search."],
                "allowed_files": ["AI_PROJECT/generated/CONTEXT_PACK.md"],
                "acceptance_criteria": ["Selected chunks include source metadata."],
                "review_instructions": [],
                "active_document": "AI_PROJECT/generated/CONTEXT_PACK.md",
                "expected_result": "Context Pack generated.",
            }
        ],
    }
    write_json(root / "AI_PROJECT" / "state" / "tasks.json", tasks)


def read_text(path):
    return path.read_text(encoding="utf-8")


def assert_contains(text, expected, context):
    if expected not in text:
        raise SystemExit("expected {!r} in {}".format(expected, context))


def assert_not_contains(text, unexpected, context):
    if unexpected in text:
        raise SystemExit("did not expect {!r} in {}".format(unexpected, context))


def main():
    with tempfile.TemporaryDirectory(prefix="contextctl-smoke-") as tmp:
        root = Path(tmp)
        setup_fixture(root)

        run(root, "status", must_contain=["Indexed source documents: 1", "Excluded registered sources: 5"])
        run(root, "index", "build", must_contain=["OK: context index built", "Indexed source documents: 1"])
        run(
            root,
            "search",
            "--query",
            "prompt package context retrieval",
            "--limit",
            "1",
            must_contain=["Matches: 1", "ai-system/project-control/context-source.md"],
        )

        run(
            root,
            "pack",
            "build",
            "--task",
            "TASK-001",
            "--limit",
            "1",
            "--write",
            must_contain="OK: context pack written",
        )

        pack_path = root / "AI_PROJECT" / "generated" / "CONTEXT_PACK.md"
        status_path = root / "AI_PROJECT" / "generated" / "CONTEXT_STATUS.md"
        audit_path = root / "AI_PROJECT" / "events" / "context-events.jsonl"
        codex_audit_path = root / "AI_PROJECT" / "events" / "codex-events.jsonl"

        pack = read_text(pack_path)
        status = read_text(status_path)
        assert_contains(pack, "<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->", "CONTEXT_PACK.md")
        assert_contains(pack, "It does not expand task scope", "CONTEXT_PACK.md")
        assert_contains(pack, "ai-system/project-control/context-source.md", "CONTEXT_PACK.md")
        assert_contains(pack, "inactive document excluded by default", "CONTEXT_PACK.md")
        assert_contains(status, "Selected chunks: `1`", "CONTEXT_STATUS.md")
        assert_not_contains(
            pack.split("## Selected Context", 1)[0],
            "ai-system/draft-only.md",
            "selected source summary",
        )

        run(root, "validate", must_contain="OK: context control files are valid")
        run(root, "check-generated", must_contain="OK: generated context files are up to date")

        run_codex(
            root,
            "build",
            "--task",
            "TASK-001",
            must_contain=["OK: CODEX_READY", "Source: task TASK-001"],
        )
        prompt_path = root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"
        plain_prompt = read_text(prompt_path)
        assert_not_contains(plain_prompt, "Retrieved Context:", "plain CODEX_PROMPT.md")

        run_codex(
            root,
            "build",
            "--task",
            "TASK-001",
            "--context-pack",
            "AI_PROJECT/generated/CONTEXT_PACK.md",
            must_contain=["OK: CODEX_READY", "Context Pack: AI_PROJECT/generated/CONTEXT_PACK.md"],
        )
        context_prompt = read_text(prompt_path)
        assert_contains(context_prompt, "Retrieved Context:", "context CODEX_PROMPT.md")
        assert_contains(context_prompt, "Context Pack SHA-256:", "context CODEX_PROMPT.md")
        assert_contains(context_prompt, "Retrieved context is read-only.", "context CODEX_PROMPT.md")
        assert_contains(context_prompt, "Retrieved context does not expand Allowed Files.", "context CODEX_PROMPT.md")
        assert_contains(context_prompt, "ai-system/project-control/context-source.md", "context CODEX_PROMPT.md")

        run_codex(
            root,
            "build",
            "--task",
            "TASK-001",
            "--context-pack",
            "AI_PROJECT/generated/MISSING_CONTEXT_PACK.md",
            expect_success=False,
            must_contain="CODEX_CONTEXT_PACK_MISSING",
        )

        invalid_pack_path = root / "AI_PROJECT" / "generated" / "INVALID_CONTEXT_PACK.md"
        invalid_pack_path.write_text("# Not a generated context pack\n", encoding="utf-8")
        run_codex(
            root,
            "build",
            "--task",
            "TASK-001",
            "--context-pack",
            "AI_PROJECT/generated/INVALID_CONTEXT_PACK.md",
            expect_success=False,
            must_contain="CODEX_CONTEXT_PACK_INVALID",
        )

        tasks_state = json.loads(read_text(root / "AI_PROJECT" / "state" / "tasks.json"))
        tasks_state["revision"] = 3
        write_json(root / "AI_PROJECT" / "state" / "tasks.json", tasks_state)
        run_codex(
            root,
            "build",
            "--task",
            "TASK-001",
            "--context-pack",
            "AI_PROJECT/generated/CONTEXT_PACK.md",
            expect_success=False,
            must_contain="CODEX_CONTEXT_PACK_STALE",
        )
        run(root, "render", must_contain="OK: rendered context outputs")
        run(root, "check-generated", must_contain="OK: generated context files are up to date")

        with pack_path.open("a", encoding="utf-8", newline="\n") as f:
            f.write("\nmanual drift\n")

        run(root, "check-generated", expect_success=False, must_contain="CHECK_GENERATED_FAILED")
        run(root, "render", must_contain="OK: rendered context outputs")
        run(root, "check-generated", must_contain="OK: generated context files are up to date")

        audit = read_text(audit_path)
        assert_contains(audit, "context.pack.build", "context-events.jsonl")
        assert_contains(audit, "context.render", "context-events.jsonl")
        codex_audit = read_text(codex_audit_path)
        assert_contains(codex_audit, "codex.prompt.build", "codex-events.jsonl")
        assert_contains(codex_audit, "codex.prompt.blocked", "codex-events.jsonl")

    print("OK: context control smoke test passed")


if __name__ == "__main__":
    main()

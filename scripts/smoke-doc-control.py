#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Smoke test for documentation control.

Runs docctl.py against a temporary project root and verifies:
- init creates docs state;
- validate accepts default registered docs;
- render writes generated docs output;
- check-generated detects fresh output;
- audit can read recent events.
"""

import subprocess
import sys
import tempfile
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DOCCTL = REPO_ROOT / "scripts" / "docctl.py"

REQUIRED_DOCS = [
    "ai-system/project-control/01-overview.md",
    "ai-system/project-control/02-domain-model.md",
    "ai-system/project-control/03-state-model.md",
    "ai-system/project-control/04-command-catalog.md",
    "ai-system/project-control/05-lifecycle-rules.md",
    "ai-system/project-control/06-prompt-package-spec.md",
    "ai-system/project-control/07-validation-and-tests.md",
]


def run(root, *args):
    command = [sys.executable, str(DOCCTL), "--root", str(root), *args]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    return result.stdout


def main():
    with tempfile.TemporaryDirectory(prefix="docctl-smoke-") as tmp:
        root = Path(tmp)
        for doc_path in REQUIRED_DOCS:
            path = root / doc_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# {}\n\nSmoke fixture.\n".format(Path(doc_path).stem), encoding="utf-8")

        run(root, "init")
        state = json.loads(run(root, "show"))
        first_doc = state["docs"][0]
        if not first_doc.get("content_hash"):
            raise SystemExit("expected content_hash to be recorded during init")

        run(root, "validate")
        run(root, "render")
        run(root, "check-generated")

        mismatch_path = root / "ai-system" / "status-mismatch.md"
        mismatch_path.write_text("# Status Mismatch\n\nStatus: Draft\n\nSmoke fixture.\n", encoding="utf-8")
        run(
            root,
            "doc",
            "register",
            "--path",
            "ai-system/status-mismatch.md",
            "--title",
            "Status Mismatch",
            "--status",
            "active",
        )
        validation = run(root, "validate")
        if "registry status `active` differs from declared status `draft`" not in validation:
            raise SystemExit("expected validate warning for status mismatch")

        gaps = (root / "AI_PROJECT" / "generated" / "DOCS_GAPS.md").read_text(encoding="utf-8")
        if "## Status Mismatch" not in gaps:
            raise SystemExit("expected categorized status mismatch gap")

        run(root, "doc", "mark-reviewed", "ai-system/status-mismatch.md", "--note", "Smoke review.")
        state = json.loads(run(root, "show"))
        reviewed_doc = next(doc for doc in state["docs"] if doc["path"] == "ai-system/status-mismatch.md")
        if not reviewed_doc.get("last_reviewed_content_hash"):
            raise SystemExit("expected mark-reviewed to store last_reviewed_content_hash")

        mismatch_path.write_text("# Status Mismatch\n\nStatus: Active\n\nChanged smoke fixture.\n", encoding="utf-8")
        run(root, "render")
        gaps = (root / "AI_PROJECT" / "generated" / "DOCS_GAPS.md").read_text(encoding="utf-8")
        if "## Active Review Stale" not in gaps or "## Stale Content Hash" not in gaps:
            raise SystemExit("expected stale review and stale content hash gaps")

        (root / "AGENTS.md").write_text("# AGENTS\n\nStatus: Draft\n", encoding="utf-8")
        skill_path = root / ".agents" / "skills" / "example" / "SKILL.md"
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text("---\nstatus: Draft\n---\n\n# Example Skill\n", encoding="utf-8")
        run(root, "scan", "--scope", "all")
        state = json.loads(run(root, "show"))
        paths = {doc["path"] for doc in state["docs"]}
        if "AGENTS.md" not in paths:
            raise SystemExit("expected root document to be registered by scan --scope all")
        if ".agents/skills/example/SKILL.md" not in paths:
            raise SystemExit("expected skill document to be registered by scan --scope all")

        run(root, "render")
        run(root, "check-generated")
        audit = run(root, "audit", "--last", "20")

        if " init " not in audit:
            raise SystemExit("expected init event in audit output")

    print("OK: doc control smoke test passed")


if __name__ == "__main__":
    main()

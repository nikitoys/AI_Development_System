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
        run(root, "validate")
        run(root, "render")
        run(root, "check-generated")
        audit = run(root, "audit", "--last", "20")

        if " init " not in audit:
            raise SystemExit("expected init event in audit output")

    print("OK: doc control smoke test passed")


if __name__ == "__main__":
    main()

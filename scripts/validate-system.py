#!/usr/bin/env python3
"""Run read-only validation checks for the AI Development System.

This script validates repository documentation, specs, planning fixtures and
the golden project. It does not execute agents, create branches or worktrees,
merge changes, accept results or modify files.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_TEMPLATE_FILES = [
    "ai-system/templates/foldered/AI_PROJECT/AGENT_PLAN.md",
    "ai-system/templates/foldered/AI_PROJECT/AGENT_TASKS.md",
    "ai-system/templates/foldered/AI_PROJECT/AGENT_ASSIGNMENTS.md",
    "ai-system/templates/foldered/AI_PROJECT/AGENT_LOCKS.md",
    "ai-system/templates/foldered/AI_PROJECT/AGENT_RESULTS.md",
    "ai-system/templates/foldered/AI_PROJECT/AGENT_METRICS.md",
]

REQUIRED_GOLDEN_PROJECT_FILES = [
    "examples/golden-project/AI_PROJECT/AGENT_PLAN.md",
    "examples/golden-project/AI_PROJECT/AGENT_TASKS.md",
    "examples/golden-project/AI_PROJECT/AGENT_ASSIGNMENTS.md",
    "examples/golden-project/AI_PROJECT/AGENT_LOCKS.md",
    "examples/golden-project/AI_PROJECT/AGENT_RESULTS.md",
    "examples/golden-project/AI_PROJECT/AGENT_METRICS.md",
]


def run_command(name: str, args: list[str]) -> list[str]:
    print(f"RUN: {name}")
    result = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    if result.returncode == 0:
        print(f"PASS: {name}")
        return []

    print(f"FAIL: {name}")
    if result.stdout:
        print(result.stdout.rstrip())
    return [f"{name}: exited with {result.returncode}"]


def validate_json_specs() -> list[str]:
    print("RUN: JSON spec parse validation")
    errors: list[str] = []

    for spec_file in sorted((ROOT / "spec").rglob("*.json")):
        try:
            with spec_file.open("r", encoding="utf-8") as handle:
                json.load(handle)
        except json.JSONDecodeError as exc:
            errors.append(f"{spec_file.relative_to(ROOT)}: JSON parse failed: {exc}")

    if errors:
        print("FAIL: JSON spec parse validation")
        for error in errors:
            print(f"- {error}")
        return errors

    print("PASS: JSON spec parse validation")
    return []


def validate_required_files(name: str, paths: list[str]) -> list[str]:
    print(f"RUN: {name}")
    errors: list[str] = []

    for relative_path in paths:
        path = ROOT / relative_path
        if not path.exists():
            errors.append(f"{relative_path}: missing")
        elif path.is_file() and path.stat().st_size == 0:
            errors.append(f"{relative_path}: empty")

    if errors:
        print(f"FAIL: {name}")
        for error in errors:
            print(f"- {error}")
        return errors

    print(f"PASS: {name}")
    return []


def main() -> int:
    checks: list[list[str]] = [
        run_command(
            "Python compile checks",
            [
                sys.executable,
                "-m",
                "py_compile",
                "scripts/foldered-control-mvp.py",
                "scripts/agent-plan-mvp.py",
                "scripts/validate-agent-plan-fixtures.py",
                "scripts/validate-system.py",
            ],
        ),
        run_command("Documentation integrity", [sys.executable, "scripts/check-docs-integrity.py"]),
        validate_json_specs(),
        validate_required_files("AI_PROJECT agent template validation", REQUIRED_TEMPLATE_FILES),
        validate_required_files("Golden project agent file validation", REQUIRED_GOLDEN_PROJECT_FILES),
        run_command("Agent planning fixture validation", [sys.executable, "scripts/validate-agent-plan-fixtures.py"]),
        run_command(
            "Golden project dry-run validation",
            [
                sys.executable,
                "scripts/agent-plan-mvp.py",
                "validate",
                "--project-root",
                "examples/golden-project",
            ],
        ),
        run_command(
            "Golden project candidate parallel groups",
            [
                sys.executable,
                "scripts/agent-plan-mvp.py",
                "list-parallel-groups",
                "--project-root",
                "examples/golden-project",
            ],
        ),
    ]

    errors = [error for check in checks for error in check]
    if errors:
        print("\nSystem validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nSystem validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

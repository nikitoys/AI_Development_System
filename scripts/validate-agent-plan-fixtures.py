#!/usr/bin/env python3
"""Validate dry-run agent planning fixtures.

This runner executes scripts/agent-plan-mvp.py against local fixtures and
asserts expected dry-run output. It does not execute Codex, create branches,
merge changes, accept results or modify application code.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENT_PLAN = ROOT / "scripts/agent-plan-mvp.py"


@dataclass(frozen=True)
class Case:
    name: str
    command: str
    fixture: str
    expected_code: int
    must_contain: list[str] = field(default_factory=list)
    must_not_contain: list[str] = field(default_factory=list)


CASES = [
    Case(
        name="simple linear dependency",
        command="list-parallel-groups",
        fixture="simple-linear",
        expected_code=0,
        must_contain=[
            "ready_layer_1: AWP-BE-001",
            "AWP-QA-001: waiting for incomplete prerequisites: AWP-BE-001",
            "Candidate Parallel Groups: none; ready dependency layer has fewer than two packages",
        ],
    ),
    Case(
        name="simple parallel dependency",
        command="list-parallel-groups",
        fixture="simple-parallel",
        expected_code=0,
        must_contain=[
            "ready_layer_1: AWP-DOC-001, AWP-QA-001",
            "candidate_group_1: AWP-DOC-001, AWP-QA-001",
        ],
    ),
    Case(
        name="diamond dependency",
        command="list-parallel-groups",
        fixture="diamond",
        expected_code=0,
        must_contain=[
            "ready_layer_1: AWP-BE-001, AWP-FE-001",
            "candidate_group_1: AWP-BE-001, AWP-FE-001",
            "AWP-QA-001: waiting for incomplete prerequisites: AWP-BE-001, AWP-FE-001",
        ],
        must_not_contain=[
            "candidate_group_1: AWP-REQ-001, AWP-BE-001, AWP-FE-001, AWP-QA-001",
        ],
    ),
    Case(
        name="completed prerequisite unlocks parallel group",
        command="list-parallel-groups",
        fixture="accepted-prerequisite",
        expected_code=0,
        must_contain=[
            "Completed/Satisfied Prerequisites: AWP-REQ-001",
            "candidate_group_1: AWP-BE-001, AWP-FE-001",
        ],
        must_not_contain=[
            "candidate_group_1: AWP-REQ-001, AWP-BE-001, AWP-FE-001, AWP-QA-001",
        ],
    ),
    Case(
        name="blocked package excluded",
        command="list-parallel-groups",
        fixture="blocked-package",
        expected_code=0,
        must_contain=[
            "AWP-BE-001: excluded because status is blocked",
            "ready_layer_1: AWP-FE-001",
        ],
        must_not_contain=[
            "candidate_group_1: AWP-BE-001",
        ],
    ),
    Case(
        name="missing dependency fails",
        command="validate",
        fixture="missing-dependency",
        expected_code=1,
        must_contain=[
            "Dependency Validation: failed",
            "missing dependency for AWP-BE-001: AWP-MISSING-001",
        ],
    ),
    Case(
        name="cycle detection fails",
        command="validate",
        fixture="cycle",
        expected_code=1,
        must_contain=[
            "Dependency Validation: failed",
            "dependency cycle: AWP-REQ-001 -> AWP-QA-001 -> AWP-REQ-001",
        ],
    ),
]


def run_case(case: Case) -> list[str]:
    project_root = ROOT / "examples/agent-plan-fixtures" / case.fixture
    result = subprocess.run(
        [sys.executable, str(AGENT_PLAN), case.command, "--project-root", str(project_root)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    errors: list[str] = []
    output = result.stdout

    if result.returncode != case.expected_code:
        errors.append(f"{case.name}: expected exit {case.expected_code}, got {result.returncode}")

    for expected in case.must_contain:
        if expected not in output:
            errors.append(f"{case.name}: missing expected output: {expected}")

    for forbidden in case.must_not_contain:
        if forbidden in output:
            errors.append(f"{case.name}: found forbidden output: {forbidden}")

    if errors:
        print(f"\n--- output for failed case: {case.name} ---")
        print(output.rstrip())

    return errors


def main() -> int:
    all_errors: list[str] = []

    for case in CASES:
        errors = run_case(case)
        if errors:
            all_errors.extend(errors)
            print(f"FAIL: {case.name}")
        else:
            print(f"PASS: {case.name}")

    if all_errors:
        print("\nAgent plan fixture validation failed:")
        for error in all_errors:
            print(f"- {error}")
        return 1

    print("\nAgent plan fixture validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

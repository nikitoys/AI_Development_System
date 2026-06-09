#!/usr/bin/env python3
"""Dry-run helper for AI_PROJECT agent planning files.

This helper reads project-local AI_PROJECT/AGENT_* files and prints planning
reports. It never executes Codex, creates branches, merges changes, accepts
results or modifies application code.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path


AGENT_FILES = [
    Path("AGENT_PLAN.md"),
    Path("AGENT_TASKS.md"),
    Path("AGENT_LOCKS.md"),
    Path("AGENT_RESULTS.md"),
    Path("AGENT_METRICS.md"),
]

AWP_RE = re.compile(r"^AWP-[A-Za-z0-9_-]+$")
EMPTY_VALUES = {"", "tbd", "none", "not checked", "not proposed", "n/a", "-"}


@dataclass
class AgentPackage:
    id: str
    status: str = ""
    sop: str = ""
    role: str = ""
    parent_task: str = ""
    verification_mode: str = ""
    notes: str = ""
    allowed_files: list[str] = field(default_factory=list)
    locked_files: list[str] = field(default_factory=list)


def project_dir(project_root: Path) -> Path:
    return project_root.resolve() / "AI_PROJECT"


def read_agent_files(project_root: Path) -> tuple[dict[Path, str], list[Path]]:
    base = project_dir(project_root)
    present: dict[Path, str] = {}
    missing: list[Path] = []

    for relative in AGENT_FILES:
        path = base / relative
        if path.exists():
            present[relative] = path.read_text(encoding="utf-8")
        else:
            missing.append(relative)

    return present, missing


def table_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells or all(set(cell) <= {"-", " "} for cell in cells):
            continue
        rows.append(cells)
    return rows


def split_files(value: str) -> list[str]:
    if value.strip().lower() in EMPTY_VALUES:
        return []
    parts = re.split(r"[,;]", value)
    return [part.strip() for part in parts if part.strip() and part.strip().lower() not in EMPTY_VALUES]


def parse_agent_tasks(text: str) -> dict[str, AgentPackage]:
    packages: dict[str, AgentPackage] = {}

    for cells in table_rows(text):
        if len(cells) < 2 or not AWP_RE.match(cells[0]):
            continue

        package = AgentPackage(
            id=cells[0],
            status=cells[1] if len(cells) > 1 else "",
            sop=cells[2] if len(cells) > 2 else "",
            role=cells[3] if len(cells) > 3 else "",
            parent_task=cells[4] if len(cells) > 4 else "",
            verification_mode=cells[5] if len(cells) > 5 else "",
            notes=cells[6] if len(cells) > 6 else "",
        )
        packages[package.id] = package

    return packages


def parse_agent_locks(text: str) -> dict[str, tuple[list[str], list[str]]]:
    locks: dict[str, tuple[list[str], list[str]]] = {}

    for cells in table_rows(text):
        if len(cells) < 3 or not AWP_RE.match(cells[0]):
            continue
        locks[cells[0]] = (split_files(cells[1]), split_files(cells[2]))

    return locks


def load_packages(project_root: Path) -> tuple[dict[str, AgentPackage], dict[Path, str], list[Path]]:
    present, missing = read_agent_files(project_root)
    packages = parse_agent_tasks(present.get(Path("AGENT_TASKS.md"), ""))
    locks = parse_agent_locks(present.get(Path("AGENT_LOCKS.md"), ""))

    for package_id, (allowed_files, locked_files) in locks.items():
        package = packages.setdefault(package_id, AgentPackage(id=package_id))
        package.allowed_files = allowed_files
        package.locked_files = locked_files

    return packages, present, missing


def lock_conflicts(packages: dict[str, AgentPackage]) -> dict[str, list[str]]:
    by_file: dict[str, list[str]] = {}
    for package in packages.values():
        for locked_file in package.locked_files:
            by_file.setdefault(locked_file, []).append(package.id)
    return {path: ids for path, ids in by_file.items() if len(ids) > 1}


def print_boundary() -> None:
    print("Boundary:")
    print("- dry-run/reporting only")
    print("- does not execute Codex")
    print("- does not create branches, worktrees, commits or merges")
    print("- does not modify AI_PROJECT files or application code")
    print("- does not accept results")
    print("- candidate parallel groups are informational only")


def command_validate(args: argparse.Namespace) -> int:
    packages, present, missing = load_packages(args.project_root)

    print_boundary()
    print("Project Root:", args.project_root.resolve())
    print("AI_PROJECT:", project_dir(args.project_root))
    print("Agent Planning Files:")
    for relative in AGENT_FILES:
        status = "present" if relative in present else "missing"
        print(f"- {status}: AI_PROJECT/{relative.as_posix()}")

    print("Agent Work Packages:")
    if not packages:
        print("- none recognized in AI_PROJECT/AGENT_TASKS.md")
    else:
        for package in packages.values():
            incomplete = [
                name
                for name, value in [
                    ("status", package.status),
                    ("sop", package.sop),
                    ("role", package.role),
                    ("parent_task", package.parent_task),
                    ("verification_mode", package.verification_mode),
                ]
                if value.strip().lower() in EMPTY_VALUES
            ]
            suffix = f" incomplete: {', '.join(incomplete)}" if incomplete else " complete enough for planning"
            print(f"- {package.id}: {package.status or 'unknown'};{suffix}")

    return 0


def command_check_locks(args: argparse.Namespace) -> int:
    packages, _, missing = load_packages(args.project_root)
    print_boundary()

    if Path("AGENT_LOCKS.md") in missing:
        print("Lock Source: missing AI_PROJECT/AGENT_LOCKS.md")
    else:
        print("Lock Source: AI_PROJECT/AGENT_LOCKS.md")

    if not packages:
        print("Lock Check: no Agent Work Packages recognized")
        return 0

    for package in packages.values():
        allowed = ", ".join(package.allowed_files) if package.allowed_files else "none recorded"
        locked = ", ".join(package.locked_files) if package.locked_files else "none recorded"
        print(f"- {package.id}: allowed_files=[{allowed}] locked_files=[{locked}]")

    conflicts = lock_conflicts(packages)
    if not conflicts:
        print("Lock Conflicts: none detected from available data")
        return 0

    print("Lock Conflicts:")
    for locked_file, package_ids in conflicts.items():
        print(f"- {locked_file}: {', '.join(package_ids)}")
    return 0


def command_list_parallel_groups(args: argparse.Namespace) -> int:
    packages, _, _ = load_packages(args.project_root)
    print_boundary()
    print("Parallel Group Policy: informational only; not executable until Human Owner approval")

    if len(packages) < 2:
        print("Candidate Parallel Groups: none; fewer than two Agent Work Packages recognized")
        return 0

    conflicts = lock_conflicts(packages)
    if conflicts:
        print("Candidate Parallel Groups: none; locked-file conflicts must be resolved first")
        for locked_file, package_ids in conflicts.items():
            print(f"- conflict {locked_file}: {', '.join(package_ids)}")
        return 0

    ready = [
        package.id
        for package in packages.values()
        if package.status.strip().lower() not in {"blocked", "rejected", "archived"}
    ]
    if len(ready) < 2:
        print("Candidate Parallel Groups: none; fewer than two non-blocked packages")
        return 0

    print("Candidate Parallel Groups:")
    print(f"- candidate_group_1: {', '.join(ready)}")
    print("  status: informational_only")
    print("  execution_authorized: no")
    print("  human_owner_approval_required: yes")
    return 0


def prompt_ready(package: AgentPackage) -> bool:
    required = [package.id, package.status, package.sop, package.role, package.parent_task, package.verification_mode]
    return all(value.strip().lower() not in EMPTY_VALUES for value in required)


def command_generate_prompts(args: argparse.Namespace) -> int:
    packages, _, _ = load_packages(args.project_root)
    print_boundary()
    print("Prompt Drafts: generated for review only; not sent to Codex")

    if not packages:
        print("- none; no Agent Work Packages recognized")
        return 0

    generated = 0
    for package in packages.values():
        if not prompt_ready(package):
            print(f"- skipped {package.id}: insufficient package data for bounded prompt draft")
            continue

        generated += 1
        allowed = ", ".join(package.allowed_files) if package.allowed_files else "Use parent task allowed files; confirm before execution."
        locked = ", ".join(package.locked_files) if package.locked_files else "No locked files recorded; confirm before execution."
        print()
        print(f"## Prompt Draft: {package.id}")
        print("[CODEX]")
        print(f"Active Role: {package.role}")
        print("Active Stage: Agent Work Package Execution")
        print("Active Document: AI_PROJECT/AGENT_TASKS.md")
        print(f"Expected Result: bounded result for {package.id}; no automatic acceptance")
        print()
        print("Task:")
        print(f"- Parent task: {package.parent_task}")
        print(f"- SOP: {package.sop}")
        print(f"- Agent Work Package: {package.id}")
        print(f"- Verification Mode: {package.verification_mode}")
        print()
        print("Allowed Files:")
        print(f"- {allowed}")
        print()
        print("Locked Files:")
        print(f"- {locked}")
        print()
        print("Forbidden Actions:")
        print("- Do not execute unrelated work.")
        print("- Do not modify files outside allowed_files.")
        print("- Do not create branches, worktrees, commits or merges.")
        print("- Do not accept results automatically.")
        print()
        print("Expected Output:")
        print("- Changed files")
        print("- Summary")
        print("- Checks performed")
        print("- Errors or blockers")
        print("- Questions")
        print("- Diff or key changes")

    if generated == 0:
        print("No prompt drafts generated.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dry-run agent planning helper for AI_PROJECT files.")
    parser.add_argument(
        "command",
        choices=["validate", "check-locks", "list-parallel-groups", "generate-prompts"],
    )
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "validate":
        return command_validate(args)
    if args.command == "check-locks":
        return command_check_locks(args)
    if args.command == "list-parallel-groups":
        return command_list_parallel_groups(args)
    if args.command == "generate-prompts":
        return command_generate_prompts(args)

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())


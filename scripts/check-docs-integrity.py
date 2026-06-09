#!/usr/bin/env python3
"""Documentation integrity checks for AI_Development_System."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]

LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
PLACEHOLDER_RE = re.compile(r"(\{\{[^}]+\}\}|TODO\b|TBD\b|REPLACE_ME\b)", re.IGNORECASE)
VERSION_RE = re.compile(r"^Version:\s*(v\d+\.\d+\.\d+)\s*$", re.MULTILINE)
RU_VERSION_RE = re.compile(r"^Версия:\s*(v\d+\.\d+\.\d+)\s*$", re.MULTILINE)
CHANGELOG_VERSION_RE = re.compile(r"^##\s+(v\d+\.\d+\.\d+)\s*$", re.MULTILINE)

PLACEHOLDER_ALLOWED_PREFIXES = (
    Path("templates"),
    Path("ai-system/templates"),
    Path("ai-system/evolution/templates"),
)

PLACEHOLDER_ALLOWED_FILES = {
    "CODEX_CURRENT.md",
    "CODEX_PLAN.md",
    "CODEX_SESSION_LOG.md",
    "CODEX_TASKS.md",
    "PROJECT_GOAL.md",
}

INDEXED_EVOLUTION_FILES = (
    Path("ai-system/evolution/analysis-report-baseline.md"),
    Path("ai-system/evolution/evolution-backlog.md"),
    Path("ai-system/evolution/evolution-loop.md"),
    Path("ai-system/evolution/evolution-policy.md"),
    Path("ai-system/evolution/owner-evolution-plan.md"),
    Path("ai-system/evolution/owner-plan-intake.md"),
    Path("ai-system/evolution/roadmap.md"),
    Path("ai-system/evolution/system-health-check.md"),
)

INDEXED_EVOLUTION_TEMPLATE_FILES = (
    Path("ai-system/evolution/templates/evolution-task.md"),
    Path("ai-system/evolution/templates/owner-evolution-plan.md"),
    Path("ai-system/evolution/templates/system-change-proposal.md"),
)


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def markdown_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if ".git" not in path.parts
    )


def visible_lines(path: Path) -> list[tuple[int, str]]:
    in_fence = False
    result: list[tuple[int, str]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            result.append((number, line))
    return result


def is_external(target: str) -> bool:
    parsed = urlparse(target)
    return parsed.scheme in {"http", "https", "mailto"}


def check_links(errors: list[str]) -> None:
    for path in markdown_files():
        for line_number, line in visible_lines(path):
            for match in LINK_RE.finditer(line):
                target = match.group(1).strip("<>")
                if is_external(target) or target.startswith("#"):
                    continue
                target_path = unquote(target.split("#", 1)[0])
                if not target_path:
                    continue
                candidate = ROOT / target_path.lstrip("/") if target_path.startswith("/") else path.parent / target_path
                if not candidate.exists():
                    errors.append(f"{repo_path(path)}:{line_number}: broken markdown link: {target}")


def check_placeholders(errors: list[str]) -> None:
    for path in markdown_files():
        relative = path.relative_to(ROOT)
        if relative.as_posix() in PLACEHOLDER_ALLOWED_FILES:
            continue
        if any(relative.as_posix().startswith(prefix.as_posix() + "/") for prefix in PLACEHOLDER_ALLOWED_PREFIXES):
            continue
        for line_number, line in visible_lines(path):
            match = PLACEHOLDER_RE.search(line)
            if match:
                errors.append(f"{repo_path(path)}:{line_number}: unresolved placeholder marker: {match.group(1)}")


def require_index_entry(index_path: Path, required_path: Path, errors: list[str]) -> None:
    index_text = index_path.read_text(encoding="utf-8")
    required = repo_path(required_path)
    if required not in index_text and required_path.name not in index_text:
        errors.append(f"{repo_path(index_path)}: missing index entry for {required}")


def check_indexes(errors: list[str]) -> None:
    ai_index = ROOT / "ai-system/README.md"
    evolution_index = ROOT / "ai-system/evolution/README.md"

    for relative in INDEXED_EVOLUTION_FILES:
        path = ROOT / relative
        require_index_entry(ai_index, path, errors)
        require_index_entry(evolution_index, path, errors)

    for relative in INDEXED_EVOLUTION_TEMPLATE_FILES:
        path = ROOT / relative
        require_index_entry(ai_index, path, errors)
        require_index_entry(evolution_index, path, errors)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def single_match(pattern: re.Pattern[str], text: str, label: str, errors: list[str]) -> str | None:
    match = pattern.search(text)
    if not match:
        errors.append(f"{label}: missing version marker")
        return None
    return match.group(1)


def check_status_and_versions(errors: list[str]) -> None:
    changelog_version = single_match(
        CHANGELOG_VERSION_RE,
        read("ai-system/system-changelog.md"),
        "ai-system/system-changelog.md",
        errors,
    )
    version_targets = {
        "README.md": single_match(VERSION_RE, read("README.md"), "README.md", errors),
        "README.ru.md": single_match(RU_VERSION_RE, read("README.ru.md"), "README.ru.md", errors),
        "ai-system/README.md": single_match(VERSION_RE, read("ai-system/README.md"), "ai-system/README.md", errors),
    }
    if changelog_version:
        for path, version in version_targets.items():
            if version and version != changelog_version:
                errors.append(f"{path}: version {version} does not match changelog {changelog_version}")

    for path in sorted((ROOT / "ai-system/evolution").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        first_lines = text.splitlines()[:8]
        if not any(line.startswith("Status:") for line in first_lines):
            errors.append(f"{repo_path(path)}: missing Status field near top of file")
        if not any(line.startswith("Version:") for line in first_lines):
            errors.append(f"{repo_path(path)}: missing Version field near top of file")


def main() -> int:
    errors: list[str] = []
    check_links(errors)
    check_placeholders(errors)
    check_indexes(errors)
    check_status_and_versions(errors)

    if errors:
        print("Documentation integrity check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Documentation integrity check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

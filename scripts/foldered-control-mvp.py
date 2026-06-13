#!/usr/bin/env python3
"""Minimal foldered integration bootstrap/update helper.

This is intentionally a small script, not a packaged CLI. It supports dry-run
planning first, placeholder detection and AI_DEV_SYSTEM_VERSION tracking.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = REPO_ROOT / "ai-system/templates/foldered"
PROJECT_TEMPLATE_ROOT = TEMPLATE_ROOT / "AI_PROJECT"
CHANGELOG = REPO_ROOT / "ai-system/system-changelog.md"

PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}")
VERSION_RE = re.compile(r"^##\s+(v\d+\.\d+\.\d+)\s*$", re.MULTILINE)

TEMPLATE_FILES = [
    Path("AGENTS.md"),
    Path("PROJECT_OPERATION_PROFILE.md"),
    Path("PROJECT_GOAL.md"),
    Path("OWNER_PLAN.md"),
    Path("CODEX_COMMANDS.md"),
    Path("CODEX_WORKFLOW.md"),
    Path("CODEX_PLAN.md"),
    Path("CODEX_CURRENT.md"),
    Path("CODEX_TASKS.md"),
    Path("CODEX_SESSION_LOG.md"),
    Path("PROMPTS.md"),
    Path("AGENT_PLAN.md"),
    Path("AGENT_TASKS.md"),
    Path("AGENT_ASSIGNMENTS.md"),
    Path("AGENT_LOCKS.md"),
    Path("AGENT_RESULTS.md"),
    Path("AGENT_METRICS.md"),
    Path("AI_DEV_SYSTEM_VERSION.md"),
    Path("docs/verification-policy.md"),
]


def current_version() -> str:
    match = VERSION_RE.search(CHANGELOG.read_text(encoding="utf-8"))
    return match.group(1) if match else "unknown"


def current_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def replacements(args: argparse.Namespace) -> dict[str, str]:
    return {
        "{{PROJECT_NAME}}": args.project_name,
        "{{TARGET_APP_DIRECTORY}}": args.target_app_directory,
        "{{DEFAULT_VERIFICATION_MODE}}": args.verification_mode,
        "{{DEFAULT_VERIFICATION_BUDGET}}": args.verification_budget,
        "{{ALLOWED_SLOW_CHECKS}}": args.allowed_slow_checks,
        "{{RUNTIME_TRACKING}}": args.runtime_tracking,
        "{{BROWSER_CHECKS}}": args.browser_checks,
        "{{VISUAL_QA}}": args.visual_qa,
        "{{HUMAN_OWNER_LANGUAGE}}": args.owner_language,
        "{{ANSWER_DETAIL_LEVEL}}": args.answer_detail_level,
        "{{PROMPT_LANGUAGE}}": args.prompt_language,
        "{{CAN_MODIFY_APPLICATION_CODE}}": args.can_modify_application_code,
        "{{CAN_MODIFY_AI_PROJECT}}": args.can_modify_ai_project,
        "{{CAN_MODIFY_AI_DEVELOPMENT_SYSTEM}}": args.can_modify_ai_development_system,
        "{{CAN_INSTALL_DEPENDENCIES}}": args.can_install_dependencies,
        "{{CAN_COMMIT}}": args.can_commit,
        "{{CAN_PUSH_PR}}": args.can_push_pr,
        "{{AI_DEV_SYSTEM_SOURCE_BRANCH}}": args.source_branch,
        "{{AI_DEV_SYSTEM_VERSION}}": args.system_version,
        "{{AI_DEV_SYSTEM_SOURCE_COMMIT}}": args.source_commit,
        "{{AI_DEV_SYSTEM_UPDATE_METHOD}}": args.update_method,
        "{{AI_DEV_SYSTEM_LAST_UPDATED}}": args.last_updated,
        "{{PROJECT_MISSION}}": args.project_mission,
        "{{PROJECT_CONSTRAINTS}}": args.project_constraints,
        "{{PROJECT_NON_GOALS}}": args.project_non_goals,
        "{{PROJECT_SUCCESS_CRITERIA}}": args.project_success_criteria,
        "{{OWNER_PLAN_INTENT}}": args.owner_plan_intent,
        "{{OWNER_PLAN_MUST_HAVE}}": args.owner_plan_must_have,
        "{{OWNER_PLAN_NICE_TO_HAVE}}": args.owner_plan_nice_to_have,
        "{{OWNER_PLAN_CONSTRAINTS}}": args.owner_plan_constraints,
        "{{OWNER_PLAN_CURRENT_PRIORITY}}": args.owner_plan_current_priority,
    }


def render(template: Path, values: dict[str, str]) -> str:
    text = template.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace(key, value)
    return text


def unresolved_placeholders(text: str) -> list[str]:
    return sorted(set(PLACEHOLDER_RE.findall(text)))


def write_if_apply(path: Path, content: str, apply: bool) -> str:
    if path.exists():
        return "exists"
    if apply:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return "create" if apply else "would_create"


def render_root_agents(values: dict[str, str]) -> str:
    return render(TEMPLATE_ROOT / "AGENTS.root.md", values)


def render_project_file(relative: Path, values: dict[str, str]) -> str:
    return render(PROJECT_TEMPLATE_ROOT / relative, values)


def bootstrap(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    project_root = args.project_root.resolve()
    values = replacements(args)
    actions: list[str] = []
    placeholders: list[str] = []

    root_agents = render_root_agents(values)
    placeholders.extend(f"AGENTS.md: {item}" for item in unresolved_placeholders(root_agents))
    status = write_if_apply(project_root / "AGENTS.md", root_agents, args.apply)
    actions.append(f"{status}: AGENTS.md")

    for relative in TEMPLATE_FILES:
        content = render_project_file(relative, values)
        placeholders.extend(f"AI_PROJECT/{relative.as_posix()}: {item}" for item in unresolved_placeholders(content))
        status = write_if_apply(project_root / "AI_PROJECT" / relative, content, args.apply)
        actions.append(f"{status}: AI_PROJECT/{relative.as_posix()}")

    return actions, placeholders


def update(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    project_root = args.project_root.resolve()
    values = replacements(args)
    actions: list[str] = []
    placeholders: list[str] = []

    required = [Path("AGENTS.md")] + [Path("AI_PROJECT") / path for path in TEMPLATE_FILES]
    for relative in required:
        path = project_root / relative
        actions.append(("exists" if path.exists() else "missing") + f": {relative.as_posix()}")
        if path.exists():
            for item in unresolved_placeholders(path.read_text(encoding="utf-8")):
                placeholders.append(f"{relative.as_posix()}: {item}")

    version_content = render_project_file(Path("AI_DEV_SYSTEM_VERSION.md"), values)
    placeholders.extend(
        f"AI_PROJECT/AI_DEV_SYSTEM_VERSION.md: {item}"
        for item in unresolved_placeholders(version_content)
    )
    version_path = project_root / "AI_PROJECT/AI_DEV_SYSTEM_VERSION.md"
    if args.apply:
        version_path.parent.mkdir(parents=True, exist_ok=True)
        version_path.write_text(version_content, encoding="utf-8")
        actions.append("updated: AI_PROJECT/AI_DEV_SYSTEM_VERSION.md")
    else:
        actions.append("would_update: AI_PROJECT/AI_DEV_SYSTEM_VERSION.md")

    return actions, placeholders


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Minimal foldered integration bootstrap/update helper.")
    parser.add_argument("command", choices=["bootstrap", "update"])
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--project-name", default="Example Project")
    parser.add_argument("--target-app-directory", default="app")
    parser.add_argument("--owner-language", default="English")
    parser.add_argument("--answer-detail-level", default="Concise by default; expand when asked.")
    parser.add_argument("--prompt-language", default="English or bilingual when execution clarity benefits.")
    parser.add_argument("--verification-mode", default="FAST")
    parser.add_argument("--verification-budget", default="120 sec")
    parser.add_argument("--allowed-slow-checks", default="false")
    parser.add_argument("--runtime-tracking", default="enabled")
    parser.add_argument("--browser-checks", default="explicit request only")
    parser.add_argument("--visual-qa", default="explicit request only")
    parser.add_argument("--can-modify-application-code", default="only with approved task")
    parser.add_argument("--can-modify-ai-project", default="planning, state, prompts, verification policy or project control tasks only")
    parser.add_argument("--can-modify-ai-development-system", default="system update, synchronization or evolution tasks only")
    parser.add_argument("--can-install-dependencies", default="explicit approval only")
    parser.add_argument("--can-commit", default="explicit request only")
    parser.add_argument("--can-push-pr", default="explicit request only")
    parser.add_argument("--update-method", default="vendor-copy")
    parser.add_argument("--source-branch", default="ai-development-system")
    parser.add_argument("--system-version", default=current_version())
    parser.add_argument("--source-commit", default=current_commit())
    parser.add_argument("--last-updated", default=dt.date.today().isoformat())
    parser.add_argument("--project-mission", default="Describe the project mission before implementation.")
    parser.add_argument("--project-constraints", default="No application code changes during bootstrap or system update.")
    parser.add_argument("--project-non-goals", default="No product implementation during control-layer setup.")
    parser.add_argument("--project-success-criteria", default="Control files are complete and approved by the Human Owner.")
    parser.add_argument("--owner-plan-intent", default="Human Owner plan goes here.")
    parser.add_argument("--owner-plan-must-have", default="Convert owner plan items into approved bounded tasks.")
    parser.add_argument("--owner-plan-nice-to-have", default="Keep future improvements visible without expanding scope.")
    parser.add_argument("--owner-plan-constraints", default="One approved task at a time.")
    parser.add_argument("--owner-plan-current-priority", default="Approve the initialized control layer.")
    parser.add_argument("--apply", action="store_true", help="Apply changes. Default is dry-run.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.project_root = args.project_root.resolve()

    actions, placeholders = bootstrap(args) if args.command == "bootstrap" else update(args)

    print(f"Mode: {'apply' if args.apply else 'dry-run'}")
    print(f"Command: {args.command}")
    print(f"Project Root: {args.project_root}")
    print(f"AI System Version: {args.system_version}")
    print("Actions:")
    for action in actions:
        print(f"- {action}")

    print("Placeholder Check:")
    if placeholders:
        for placeholder in placeholders:
            print(f"- unresolved: {placeholder}")
        return 2

    print("- no unresolved placeholders detected")
    print("Application Code Modified: no")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

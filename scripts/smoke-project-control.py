#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
smoke-project-control.py — end-to-end smoke tests for Project Control Gateway.

Проверяет связку:

* scripts/planctl.py
* scripts/taskctl.py

Сценарии:

* happy path: plan -> initiative -> epic -> task -> current -> prompt -> validate
* invalid parent checks
* invalid lifecycle transition checks
* prompt build checks
* generated Markdown drift detection
* audit event checks

Запуск:

python scripts/smoke-project-control.py

Полезно для отладки:

python scripts/smoke-project-control.py --verbose
python scripts/smoke-project-control.py --keep-temp
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

class SmokeFailure(Exception):
    pass

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PLANCTL = SCRIPT_DIR / "planctl.py"
TASKCTL = SCRIPT_DIR / "taskctl.py"

def quote_cmd(cmd):
    return " ".join(str(part) for part in cmd)

def read_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def read_text(path):
    return path.read_text(encoding="utf-8")

def assert_exists(path):
    if not path.exists():
        raise SmokeFailure("Expected file does not exist: {}".format(path))

def assert_not_exists(path):
    if path.exists():
        raise SmokeFailure("Expected file not to exist: {}".format(path))

def assert_contains(text, expected, context):
    if expected not in text:
        raise SmokeFailure(
        "Expected text not found in {}:\nexpected: {}".format(
        context,
        expected,
        )
        )

def assert_file_contains(path, expected_items):
    assert_exists(path)

    text = read_text(path)

    for expected in expected_items:
        assert_contains(text, expected, str(path))

def assert_json_field(path, field, expected):
    data = read_json(path)
    value = data.get(field)

    if value != expected:
        raise SmokeFailure(
            "Unexpected value in {}: {} = {!r}, expected {!r}".format(
                path,
                field,
                value,
                expected,
            )
        )

def read_jsonl(path):
    assert_exists(path)

    events = []

    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                continue

            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise SmokeFailure(
                    "Invalid JSONL in {}:{}: {}".format(path, line_no, e)
                )

    return events

def assert_event_commands(path, expected_commands):
    events = read_jsonl(path)
    commands = [event.get("command") for event in events]

    missing = []

    for command in expected_commands:
        if command not in commands:
            missing.append(command)

    if missing:
        raise SmokeFailure(
            "Missing audit commands in {}: {}\nActual commands: {}".format(
                path,
                ", ".join(missing),
                ", ".join(commands),
            )
        )

def assert_event_command_absent(path, command):
    events = read_jsonl(path)
    commands = [event.get("command") for event in events]

    if command in commands:
        raise SmokeFailure(
            "Unexpected audit command in {}: {}".format(path, command)
        )

class SmokeContext:
    def __init__(self, args, base_root):
        self.args = args
        self.base_root = Path(base_root)

    @property
    def python(self):
        return self.args.python

    @property
    def verbose(self):
        return self.args.verbose

    def make_root(self, name):
        root = self.base_root / name
        root.mkdir(parents=True, exist_ok=True)
        return root

    def run(self, cmd, expect_success=True, must_contain=None):
        if self.verbose:
            print("")
            print("$ {}".format(quote_cmd(cmd)))

        proc = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        output = (proc.stdout or "") + (proc.stderr or "")

        if self.verbose and output:
            print(output.rstrip())

        if expect_success and proc.returncode != 0:
            raise SmokeFailure(
                "Command failed unexpectedly:\n{}\nexit code: {}\noutput:\n{}".format(
                    quote_cmd(cmd),
                    proc.returncode,
                    output,
                )
            )

        if not expect_success and proc.returncode == 0:
            raise SmokeFailure(
                "Command succeeded but failure was expected:\n{}\noutput:\n{}".format(
                    quote_cmd(cmd),
                    output,
                )
            )

        if must_contain is not None:
            items = must_contain

            if isinstance(items, str):
                items = [items]

            for item in items:
                if item not in output:
                    raise SmokeFailure(
                        "Command output does not contain expected text:\n"
                        "command: {}\nexpected: {}\noutput:\n{}".format(
                            quote_cmd(cmd),
                            item,
                            output,
                        )
                    )

        return output

    def plan(self, root, *args, **kwargs):
        cmd = [
            self.python,
            str(PLANCTL),
            "--root",
            str(root),
            "--actor",
            "smoke_test",
        ]
        cmd.extend(args)

        return self.run(cmd, **kwargs)

    def task(self, root, *args, **kwargs):
        cmd = [
            self.python,
            str(TASKCTL),
            "--root",
            str(root),
            "--actor",
            "smoke_test",
        ]
        cmd.extend(args)

        return self.run(cmd, **kwargs)

def assert_required_scripts_exist():
    if not PLANCTL.exists():
        raise SmokeFailure("Missing script: {}".format(PLANCTL))

    if not TASKCTL.exists():
        raise SmokeFailure("Missing script: {}".format(TASKCTL))

def test_happy_path(ctx):
    root = ctx.make_root("happy-path")

    ctx.plan(
        root,
        "init",
        "--project-name",
        "AI Development System Smoke Test",
        must_contain="OK: initialized",
    )

    ctx.plan(
        root,
        "idea",
        "set",
        "--text",
        "Create a controlled AI-assisted development system.",
        must_contain="OK: idea.set",
    )

    ctx.plan(
        root,
        "goal",
        "set",
        "--text",
        "Validate Project Control Gateway.",
        must_contain="OK: goal.set",
    )

    ctx.plan(
        root,
        "strategy",
        "set-summary",
        "--text",
        "Use CLI commands as the only mutation path.",
        must_contain="OK: strategy.set_summary",
    )

    ctx.plan(
        root,
        "initiative",
        "create",
        "--title",
        "Project Control Gateway",
        "--summary",
        "Validate strict project control through CLI.",
        must_contain=["OK: initiative.create", "Created: INIT-001"],
    )

    ctx.plan(
        root,
        "epic",
        "create",
        "--initiative",
        "INIT-001",
        "--title",
        "Task Control CLI",
        "--summary",
        "Validate executable task control.",
        must_contain=["OK: epic.create", "Created: EPIC-001"],
    )

    ctx.task(root, "init", must_contain="OK: initialized")

    ctx.task(
        root,
        "task",
        "create",
        "--epic",
        "EPIC-001",
        "--title",
        "Smoke Task",
        "--status",
        "ready",
        "--summary",
        "Validate end-to-end task workflow.",
        "--scope",
        "Create generated prompt package.",
        "--out-of-scope",
        "No application code changes.",
        "--allowed-file",
        "AI_PROJECT/generated/CODEX_PROMPT.md",
        "--acceptance",
        "Task validation passes.",
        "--acceptance",
        "Generated task files are up to date.",
        "--verification-mode",
        "standard",
        must_contain=["OK: task.create", "Created: TASK-001"],
    )

    ctx.task(root, "current", "set", "TASK-001", must_contain="OK: current.set")
    ctx.task(root, "prompt", "build", "--write", must_contain="OK: prompt written")

    ctx.plan(root, "validate", must_contain="OK: plan is valid")
    ctx.task(root, "validate", must_contain="OK: tasks are valid")
    ctx.task(root, "check-generated", must_contain="OK: generated task files are up to date")

    expected_files = [
        root / "AI_PROJECT" / "state" / "plan.json",
        root / "AI_PROJECT" / "state" / "tasks.json",
        root / "AI_PROJECT" / "events" / "plan-events.jsonl",
        root / "AI_PROJECT" / "events" / "task-events.jsonl",
        root / "AI_PROJECT" / "generated" / "CODEX_PLAN.md",
        root / "AI_PROJECT" / "generated" / "CODEX_TASKS.md",
        root / "AI_PROJECT" / "generated" / "CODEX_CURRENT.md",
        root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md",
    ]

    for path in expected_files:
        assert_exists(path)

    assert_json_field(
        root / "AI_PROJECT" / "state" / "tasks.json",
        "current_task_id",
        "TASK-001",
    )

    assert_file_contains(
        root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md",
        [
            "[SYSTEM]",
            "Task ID: TASK-001",
            "Task Title: Smoke Task",
            "Scope:",
            "Out of Scope:",
            "Allowed Files:",
            "Acceptance Criteria:",
            "Execution Rules:",
        ],
    )

    assert_event_commands(
        root / "AI_PROJECT" / "events" / "plan-events.jsonl",
        [
            "plan.init",
            "idea.set",
            "goal.set",
            "strategy.set_summary",
            "initiative.create",
            "epic.create",
        ],
    )

    assert_event_commands(
        root / "AI_PROJECT" / "events" / "task-events.jsonl",
        [
            "tasks.init",
            "task.create",
            "current.set",
            "prompt.build",
        ],
    )

def test_epic_missing_initiative_fails(ctx):
    root = ctx.make_root("epic-missing-initiative")

    ctx.plan(root, "init", must_contain="OK: initialized")

    ctx.plan(
        root,
        "epic",
        "create",
        "--initiative",
        "INIT-999",
        "--title",
        "Invalid Epic",
        expect_success=False,
        must_contain="ENTITY_NOT_FOUND",
    )

def test_task_missing_epic_fails(ctx):
    root = ctx.make_root("task-missing-epic")

    ctx.plan(root, "init", must_contain="OK: initialized")
    ctx.task(root, "init", must_contain="OK: initialized")

    ctx.task(
        root,
        "task",
        "create",
        "--epic",
        "EPIC-999",
        "--title",
        "Invalid Task",
        expect_success=False,
        must_contain="EPIC_NOT_FOUND",
    )

    tasks = read_json(root / "AI_PROJECT" / "state" / "tasks.json")
    if tasks.get("tasks"):
        raise SmokeFailure("Invalid task was persisted after failed create command")

def test_plan_invalid_transition_fails(ctx):
    root = ctx.make_root("plan-invalid-transition")

    ctx.plan(root, "init", must_contain="OK: initialized")

    ctx.plan(
        root,
        "initiative",
        "create",
        "--title",
        "Invalid Transition Test",
        "--status",
        "proposed",
        must_contain="Created: INIT-001",
    )

    ctx.plan(
        root,
        "initiative",
        "status",
        "INIT-001",
        "--to",
        "done",
        expect_success=False,
        must_contain="INVALID_STATUS_TRANSITION",
    )

def test_task_invalid_transition_fails(ctx):
    root = ctx.make_root("task-invalid-transition")

    ctx.plan(root, "init", must_contain="OK: initialized")
    ctx.plan(root, "initiative", "create", "--title", "Project Control")
    ctx.plan(root, "epic", "create", "--initiative", "INIT-001", "--title", "Task Control")

    ctx.task(root, "init", must_contain="OK: initialized")

    ctx.task(
        root,
        "task",
        "create",
        "--epic",
        "EPIC-001",
        "--title",
        "Invalid Task Transition",
        "--status",
        "proposed",
        must_contain="Created: TASK-001",
    )

    before = read_json(root / "AI_PROJECT" / "state" / "tasks.json").get("revision")

    ctx.task(
        root,
        "task",
        "transition",
        "TASK-001",
        "--to",
        "done",
        expect_success=False,
        must_contain="INVALID_STATUS_TRANSITION",
    )

    after = read_json(root / "AI_PROJECT" / "state" / "tasks.json").get("revision")

    if before != after:
        raise SmokeFailure(
            "Failed transition changed revision: before {}, after {}".format(
                before,
                after,
            )
        )

    assert_event_command_absent(
        root / "AI_PROJECT" / "events" / "task-events.jsonl",
        "task.transition",
    )

def test_generic_approved_transition_fails(ctx):
    root = ctx.make_root("task-approved-generic-transition")

    ctx.plan(root, "init")
    ctx.plan(root, "initiative", "create", "--title", "Project Control")
    ctx.plan(root, "epic", "create", "--initiative", "INIT-001", "--title", "Task Control")

    ctx.task(root, "init")

    ctx.task(
        root,
        "task",
        "create",
        "--epic",
        "EPIC-001",
        "--title",
        "Approval Test",
        "--status",
        "in_review",
        must_contain="Created: TASK-001",
    )

    ctx.task(
        root,
        "task",
        "transition",
        "TASK-001",
        "--to",
        "approved",
        expect_success=False,
        must_contain="USE_TASK_APPROVE_COMMAND_FOR_APPROVAL",
    )

def test_archived_initiative_rejects_new_epic(ctx):
    root = ctx.make_root("archived-initiative")

    ctx.plan(root, "init")
    ctx.plan(root, "initiative", "create", "--title", "Parent Initiative")
    ctx.plan(root, "initiative", "archive", "INIT-001")

    ctx.plan(
        root,
        "epic",
        "create",
        "--initiative",
        "INIT-001",
        "--title",
        "Invalid Epic",
        expect_success=False,
        must_contain="CANNOT_CREATE_EPIC_UNDER_ARCHIVED_INITIATIVE",
    )

def test_task_under_inactive_epic_fails(ctx):
    root = ctx.make_root("task-under-inactive-epic")

    ctx.plan(root, "init")
    ctx.plan(root, "initiative", "create", "--title", "Project Control")
    ctx.plan(root, "epic", "create", "--initiative", "INIT-001", "--title", "Inactive Epic")
    ctx.plan(root, "epic", "status", "EPIC-001", "--to", "deferred")

    ctx.task(root, "init")

    ctx.task(
        root,
        "task",
        "create",
        "--epic",
        "EPIC-001",
        "--title",
        "Invalid Task Under Deferred Epic",
        expect_success=False,
        must_contain="CANNOT_USE_INACTIVE_EPIC",
    )

def test_prompt_without_current_fails(ctx):
    root = ctx.make_root("prompt-without-current")

    ctx.task(root, "init", must_contain="OK: initialized")

    ctx.task(
        root,
        "prompt",
        "build",
        expect_success=False,
        must_contain="NO_TASK_SELECTED",
    )

def test_prompt_for_inactive_task_fails_unless_allowed(ctx):
    root = ctx.make_root("prompt-inactive-task")

    ctx.plan(root, "init")
    ctx.plan(root, "initiative", "create", "--title", "Project Control")
    ctx.plan(root, "epic", "create", "--initiative", "INIT-001", "--title", "Prompt Control")

    ctx.task(root, "init")

    ctx.task(
        root,
        "task",
        "create",
        "--epic",
        "EPIC-001",
        "--title",
        "Inactive Prompt Test",
        "--status",
        "deferred",
        must_contain="Created: TASK-001",
    )

    ctx.task(
        root,
        "prompt",
        "build",
        "--task",
        "TASK-001",
        expect_success=False,
        must_contain="TASK_IS_NOT_EXECUTABLE",
    )

    ctx.task(
        root,
        "prompt",
        "build",
        "--task",
        "TASK-001",
        "--allow-inactive",
        must_contain="Task ID: TASK-001",
    )

def test_generated_task_drift_is_detected_and_repaired(ctx):
    root = ctx.make_root("generated-drift")

    ctx.plan(root, "init")
    ctx.plan(root, "initiative", "create", "--title", "Project Control")
    ctx.plan(root, "epic", "create", "--initiative", "INIT-001", "--title", "Task Control")

    ctx.task(root, "init")

    ctx.task(
        root,
        "task",
        "create",
        "--epic",
        "EPIC-001",
        "--title",
        "Generated Drift Test",
        "--scope",
        "Do one thing.",
        "--allowed-file",
        "README.md",
        "--acceptance",
        "Generated drift is detected.",
        must_contain="Created: TASK-001",
    )

    ctx.task(root, "check-generated", must_contain="OK: generated task files are up to date")

    generated_tasks = root / "AI_PROJECT" / "generated" / "CODEX_TASKS.md"

    with generated_tasks.open("a", encoding="utf-8", newline="\n") as f:
        f.write("\nmanual edit\n")

    ctx.task(
        root,
        "check-generated",
        expect_success=False,
        must_contain="GENERATED_CHECK_FAILED",
    )

    ctx.task(root, "render", must_contain="OK: rendered")
    ctx.task(root, "check-generated", must_contain="OK: generated task files are up to date")

def test_done_task_is_immutable(ctx):
    root = ctx.make_root("done-task-immutable")

    ctx.plan(root, "init")
    ctx.plan(root, "initiative", "create", "--title", "Project Control")
    ctx.plan(root, "epic", "create", "--initiative", "INIT-001", "--title", "Task Control")

    ctx.task(root, "init")

    ctx.task(
        root,
        "task",
        "create",
        "--epic",
        "EPIC-001",
        "--title",
        "Done Task Test",
        "--status",
        "in_review",
        must_contain="Created: TASK-001",
    )

    ctx.task(root, "task", "approve", "TASK-001", "--notes", "Approved")
    ctx.task(root, "task", "transition", "TASK-001", "--to", "done")

    ctx.task(
        root,
        "task",
        "update-summary",
        "TASK-001",
        "--text",
        "Should fail",
        expect_success=False,
        must_contain="DONE_TASK_IS_IMMUTABLE",
    )

def run_tests(ctx):
    tests = [
    ("happy path", test_happy_path),
    ("epic missing initiative fails", test_epic_missing_initiative_fails),
    ("task missing epic fails", test_task_missing_epic_fails),
    ("plan invalid transition fails", test_plan_invalid_transition_fails),
    ("task invalid transition fails", test_task_invalid_transition_fails),
    ("generic approved transition fails", test_generic_approved_transition_fails),
    ("archived initiative rejects new epic", test_archived_initiative_rejects_new_epic),
    ("task under inactive epic fails", test_task_under_inactive_epic_fails),
    ("prompt without current fails", test_prompt_without_current_fails),
    ("prompt for inactive task fails unless allowed", test_prompt_for_inactive_task_fails_unless_allowed),
    ("generated task drift is detected and repaired", test_generated_task_drift_is_detected_and_repaired),
    ("done task is immutable", test_done_task_is_immutable),
    ]

    for name, func in tests:
        print("RUN: {}".format(name))
        func(ctx)
        print("OK:  {}".format(name))

def build_parser():
    parser = argparse.ArgumentParser(
    description="Run Project Control Gateway smoke tests."
    )

    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable to use. Default: current interpreter.",
    )

    parser.add_argument(
        "--work-root",
        default="",
        help="Optional root directory for smoke test data. Default: temp dir.",
    )

    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary smoke test directory after success.",
    )

    parser.add_argument(
        "--cleanup-on-failure",
        action="store_true",
        help="Delete temporary smoke test directory even when tests fail.",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print executed commands and their output.",
    )

    return parser

def main(argv=None):
    args = build_parser().parse_args(argv)

    assert_required_scripts_exist()

    if args.work_root:
        base_root = Path(args.work_root).resolve()
        base_root.mkdir(parents=True, exist_ok=True)
        created_temp = False
    else:
        base_root = Path(tempfile.mkdtemp(prefix="ai-dev-system-smoke-")).resolve()
        created_temp = True

    print("Smoke root: {}".format(base_root))

    ctx = SmokeContext(args=args, base_root=base_root)

    success = False

    try:
        run_tests(ctx)
        success = True
        print("")
        print("OK: project control smoke test passed")
        return 0
    except SmokeFailure as e:
        print("")
        print("FAILED: {}".format(e), file=sys.stderr)
        print("Smoke root kept for debugging: {}".format(base_root), file=sys.stderr)
        return 1
    finally:
        should_cleanup = False

        if created_temp and success and not args.keep_temp:
            should_cleanup = True

        if created_temp and not success and args.cleanup_on_failure:
            should_cleanup = True

        if should_cleanup:
            shutil.rmtree(str(base_root), ignore_errors=True)

if __name__ == "__main__":
    sys.exit(main())

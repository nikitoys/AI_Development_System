#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
check-protected-project-files.py — protected project-control files checker.

Проверяет защищённые зоны Project Control Gateway:

AI_PROJECT/state/**
AI_PROJECT/events/**
AI_PROJECT/generated/**

Что проверяет:

* plan.json валиден через planctl.validate_plan
* tasks.json валиден через taskctl.validate_tasks
* events/*.jsonl являются валидными JSONL audit logs
* CODEX_PLAN.md совпадает с render output planctl.py
* CODEX_TASKS.md совпадает с render output taskctl.py
* CODEX_CURRENT.md совпадает с render output taskctl.py
* CODEX_PROMPT.md, если возможно, совпадает с prompt build output для current task

Важно:
этот скрипт не может криптографически доказать, что state-файл не был
изменён руками. Он ловит практические признаки обхода:

* невалидный state;
* сломанный audit;
* stale/generated drift;
* несогласованность state и generated files.

Запуск:

python scripts/check-protected-project-files.py

Полезно:

python scripts/check-protected-project-files.py --verbose
python scripts/check-protected-project-files.py --json
python scripts/check-protected-project-files.py --allow-missing-generated
python scripts/check-protected-project-files.py --skip-plan-check
"""

import argparse
from datetime import datetime
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    import planctl
except Exception as exc:
    planctl = None
    PLANCTL_IMPORT_ERROR = exc
else:
    PLANCTL_IMPORT_ERROR = None

try:
    import taskctl
except Exception as exc:
    taskctl = None
    TASKCTL_IMPORT_ERROR = exc
else:
    TASKCTL_IMPORT_ERROR = None

try:
    import codexctl
except Exception as exc:
    codexctl = None
    CODEXCTL_IMPORT_ERROR = exc
else:
    CODEXCTL_IMPORT_ERROR = None

try:
    import docctl
except Exception as exc:
    docctl = None
    DOCCTL_IMPORT_ERROR = exc
else:
    DOCCTL_IMPORT_ERROR = None

REQUIRED_EVENT_FIELDS = {
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

class CheckResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.checked = []

    def error(self, message):
        self.errors.append(message)

    def warn(self, message):
        self.warnings.append(message)

    def ok(self, message):
        self.checked.append(message)

    @property
    def failed(self):
        return bool(self.errors)

def rel(root, path):
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)

def read_json(path, result):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        result.error("MISSING_FILE: {}".format(path))
    except json.JSONDecodeError as exc:
        result.error(
        "INVALID_JSON: {}:{}:{} {}".format(
        path,
        exc.lineno,
        exc.colno,
        exc.msg,
        )
        )

    return None

def read_text(path, result):
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        result.error("MISSING_FILE: {}".format(path))
    except UnicodeDecodeError as exc:
        result.error("INVALID_TEXT_ENCODING: {} {}".format(path, exc))

    return None

def compare_generated(root, path, expected, result, allow_missing=False):
    if not path.exists():
        message = "MISSING_GENERATED_FILE: {}".format(rel(root, path))

        if allow_missing:
            result.warn(message)
        else:
            result.error(message)

        return

    actual = read_text(path, result)

    if actual is None:
        return

    if actual != expected:
        result.error("OUTDATED_GENERATED_FILE: {}".format(rel(root, path)))
        return

    result.ok("generated up to date: {}".format(rel(root, path)))

def normalize_codex_prompt_generated_line(text):
    lines = text.splitlines()

    if len(lines) < 3:
        return None

    if lines[0] != "# Codex Prompt Package" or lines[1] != "":
        return None

    prefix = "Generated: "

    if not lines[2].startswith(prefix):
        return None

    timestamp = lines[2][len(prefix):].strip()

    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return None

    lines[2] = "Generated: <normalized>"
    normalized = "\n".join(lines)

    if text.endswith("\n"):
        normalized += "\n"

    return normalized

def compare_generated_variants(root, path, variants, result, allow_missing=False):
    if not path.exists():
        message = "MISSING_GENERATED_FILE: {}".format(rel(root, path))

        if allow_missing:
            result.warn(message)
        else:
            result.error(message)

        return False

    actual = read_text(path, result)

    if actual is None:
        return False

    labels = []

    for variant in variants:
        label = variant["label"]
        expected = variant["expected"]
        normalizer = variant.get("normalizer")
        labels.append(label)

        if normalizer is None:
            if actual == expected:
                result.ok(
                    "generated up to date: {} ({})".format(
                        rel(root, path),
                        label,
                    )
                )
                return True
            continue

        normalized_actual = normalizer(actual)
        normalized_expected = normalizer(expected)

        if normalized_actual is not None and normalized_actual == normalized_expected:
            result.ok(
                "generated up to date: {} ({})".format(
                    rel(root, path),
                    label,
                )
            )
            return True

    if labels:
        result.error(
            "OUTDATED_GENERATED_FILE: {} (expected one of: {})".format(
                rel(root, path),
                ", ".join(labels),
            )
        )
    else:
        result.error("PROMPT_RENDER_FAILED: no supported prompt renderer output available")

    return False

def check_generated_header(root, path, result, allow_missing=False):
    if not path.exists():
        if not allow_missing:
            result.error("MISSING_GENERATED_FILE: {}".format(rel(root, path)))
            return

    text = read_text(path, result)

    if text is None:
        return

    expected = "<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->"

    if not text.startswith(expected):
        result.error("MISSING_GENERATED_HEADER: {}".format(rel(root, path)))

def check_event_log(root, path, expected_revision, result, required_when_state_exists=True):
    if not path.exists():
        message = "MISSING_EVENT_LOG: {}".format(rel(root, path))

        if required_when_state_exists:
            result.error(message)
        else:
            result.warn(message)

        return []

    events = []
    seen_event_ids = set()

    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                continue

            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                result.error(
                    "INVALID_EVENT_JSONL: {}:{} {}".format(
                        rel(root, path),
                        line_no,
                        exc,
                    )
                )
                continue

            if not isinstance(event, dict):
                result.error(
                    "INVALID_EVENT_OBJECT: {}:{} event must be object".format(
                        rel(root, path),
                        line_no,
                    )
                )
                continue

            missing = sorted(REQUIRED_EVENT_FIELDS - set(event.keys()))

            if missing:
                result.error(
                    "INVALID_EVENT_FIELDS: {}:{} missing {}".format(
                        rel(root, path),
                        line_no,
                        ", ".join(missing),
                    )
                )

            event_id = event.get("event_id")

            if event_id in seen_event_ids:
                result.error(
                    "DUPLICATE_EVENT_ID: {}:{} {}".format(
                        rel(root, path),
                        line_no,
                        event_id,
                    )
                )

            if event_id:
                seen_event_ids.add(event_id)

            if not isinstance(event.get("payload", {}), dict):
                result.error(
                    "INVALID_EVENT_PAYLOAD: {}:{} payload must be object".format(
                        rel(root, path),
                        line_no,
                    )
                )

            for field in ["revision_before", "revision_after"]:
                value = event.get(field)

                if value is not None and not isinstance(value, int):
                    result.error(
                        "INVALID_EVENT_REVISION: {}:{} {} must be int or null".format(
                            rel(root, path),
                            line_no,
                            field,
                        )
                    )

            events.append(event)

    if not events:
        result.warn("EMPTY_EVENT_LOG: {}".format(rel(root, path)))
    else:
        result.ok("event log valid: {}".format(rel(root, path)))

    if expected_revision is not None:
        revisions_after = [
            event.get("revision_after")
            for event in events
            if isinstance(event.get("revision_after"), int)
        ]

        if expected_revision not in revisions_after:
            result.error(
                "STATE_REVISION_HAS_NO_AUDIT_EVENT: {} revision {}".format(
                    rel(root, path),
                    expected_revision,
                )
            )

    return events

def find_task(tasks_state, task_id):
    for task in tasks_state.get("tasks", []):
        if task.get("id") == task_id:
            return task

    return None

def check_plan(root, args, result):
    if PLANCTL_IMPORT_ERROR is not None:
        result.error("PLANCTL_IMPORT_FAILED: {}".format(PLANCTL_IMPORT_ERROR))
        return None

    plan_path = root / "AI_PROJECT" / "state" / "plan.json"
    plan_events = root / "AI_PROJECT" / "events" / "plan-events.jsonl"
    codex_plan = root / "AI_PROJECT" / "generated" / "CODEX_PLAN.md"

    if not plan_path.exists():
        if args.allow_uninitialized:
            result.warn("plan state not initialized: {}".format(rel(root, plan_path)))
            return None

        result.error("PLAN_NOT_INITIALIZED: {}".format(rel(root, plan_path)))
        return None

    plan = read_json(plan_path, result)

    if plan is None:
        return None

    errors = planctl.validate_plan(plan)

    if errors:
        for error in errors:
            result.error("PLAN_VALIDATION_FAILED: {}".format(error))
    else:
        result.ok("plan state valid: {}".format(rel(root, plan_path)))

    check_event_log(
        root=root,
        path=plan_events,
        expected_revision=plan.get("revision"),
        result=result,
        required_when_state_exists=True,
    )

    if not errors:
        expected_plan_md = planctl.render_plan_markdown(plan)

        compare_generated(
            root=root,
            path=codex_plan,
            expected=expected_plan_md,
            result=result,
            allow_missing=args.allow_missing_generated,
        )

        check_generated_header(
            root=root,
            path=codex_plan,
            result=result,
            allow_missing=args.allow_missing_generated,
        )

    return plan

def check_tasks(root, args, result, plan):
    if TASKCTL_IMPORT_ERROR is not None:
        result.error("TASKCTL_IMPORT_FAILED: {}".format(TASKCTL_IMPORT_ERROR))
        return None

    tasks_path = root / "AI_PROJECT" / "state" / "tasks.json"
    task_events = root / "AI_PROJECT" / "events" / "task-events.jsonl"
    codex_tasks = root / "AI_PROJECT" / "generated" / "CODEX_TASKS.md"
    codex_current = root / "AI_PROJECT" / "generated" / "CODEX_CURRENT.md"
    codex_prompt = root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"

    if not tasks_path.exists():
        if args.allow_uninitialized:
            result.warn("tasks state not initialized: {}".format(rel(root, tasks_path)))
            return None

        result.error("TASKS_NOT_INITIALIZED: {}".format(rel(root, tasks_path)))
        return None

    tasks_state = read_json(tasks_path, result)

    if tasks_state is None:
        return None

    check_plan = not args.skip_plan_check
    errors = taskctl.validate_tasks(tasks_state, plan=plan, check_plan=check_plan)

    if errors:
        for error in errors:
            result.error("TASKS_VALIDATION_FAILED: {}".format(error))
    else:
        result.ok("tasks state valid: {}".format(rel(root, tasks_path)))

    check_event_log(
        root=root,
        path=task_events,
        expected_revision=tasks_state.get("revision"),
        result=result,
        required_when_state_exists=True,
    )

    if not errors:
        expected_tasks_md = taskctl.render_tasks_markdown(tasks_state)
        expected_current_md = taskctl.render_current_markdown(tasks_state)

        compare_generated(
            root=root,
            path=codex_tasks,
            expected=expected_tasks_md,
            result=result,
            allow_missing=args.allow_missing_generated,
        )

        compare_generated(
            root=root,
            path=codex_current,
            expected=expected_current_md,
            result=result,
            allow_missing=args.allow_missing_generated,
        )

        check_generated_header(
            root=root,
            path=codex_tasks,
            result=result,
            allow_missing=args.allow_missing_generated,
        )

        check_generated_header(
            root=root,
            path=codex_current,
            result=result,
            allow_missing=args.allow_missing_generated,
        )

        check_prompt(root, args, result, tasks_state, plan, codex_prompt)

    return tasks_state

def check_prompt(root, args, result, tasks_state, plan, codex_prompt):
    if args.no_prompt_check:
        result.warn("prompt check skipped by --no-prompt-check")
        return

    current_task_id = tasks_state.get("current_task_id")

    if not codex_prompt.exists():
        if args.strict_prompt and current_task_id:
            result.error("MISSING_GENERATED_PROMPT: {}".format(rel(root, codex_prompt)))
        else:
            result.warn("prompt file not found: {}".format(rel(root, codex_prompt)))

        return

    if not current_task_id:
        if args.strict_prompt:
            result.error(
                "ORPHAN_GENERATED_PROMPT: {} exists but current_task_id is empty".format(
                    rel(root, codex_prompt),
                )
            )
        else:
            result.warn(
                "prompt exists but current_task_id is empty; freshness cannot be proven: {}".format(
                    rel(root, codex_prompt),
                )
            )

        return

    task = find_task(tasks_state, current_task_id)

    if task is None:
        result.error("CURRENT_TASK_NOT_FOUND_FOR_PROMPT: {}".format(current_task_id))
        return

    variants = []
    render_errors = []

    try:
        variants.append(
            {
                "label": "taskctl prompt build",
                "expected": taskctl.build_prompt_text(tasks_state, task, plan=plan),
            }
        )
    except Exception as exc:
        render_errors.append("TASKCTL_PROMPT_RENDER_FAILED: {}".format(exc))

    if CODEXCTL_IMPORT_ERROR is not None:
        render_errors.append("CODEXCTL_IMPORT_FAILED: {}".format(CODEXCTL_IMPORT_ERROR))
    else:
        try:
            execution_state = codexctl.load_current_execution(root)
        except codexctl.CodexError as exc:
            execution_state = None
            render_errors.append("CODEX_EXECUTION_STATE_INVALID: {}".format(exc.message))

        if execution_state:
            state_is_current_task = (
                execution_state.get("status") == codexctl.READY_STATUS
                and execution_state.get("code") == codexctl.CODEX_READY
                and execution_state.get("source_type") == "task"
                and execution_state.get("source_id") == current_task_id
            )

            if state_is_current_task:
                try:
                    codex_model = codexctl.build_from_task(root, current_task_id)
                    context_state = execution_state.get("context_pack") or {}

                    if context_state:
                        context_pack = codexctl.validate_context_pack(
                            root,
                            context_state.get("path") or context_state.get("relative_path"),
                            current_task_id,
                        )
                        context_mismatches = []

                        for key in [
                            "relative_path",
                            "sha256",
                            "mode",
                            "task_id",
                            "docs_revision",
                            "tasks_revision",
                        ]:
                            if context_state.get(key) != context_pack.get(key):
                                context_mismatches.append(
                                    "{} {} != {}".format(
                                        key,
                                        context_state.get(key),
                                        context_pack.get(key),
                                    )
                                )

                        if context_mismatches:
                            render_errors.append(
                                "CODEX_EXECUTION_CONTEXT_MISMATCH: {}".format(
                                    "; ".join(context_mismatches)
                                )
                            )
                        else:
                            codex_model = dict(codex_model)
                            codex_model["context_pack"] = context_pack
                            variants.append(
                                {
                                    "label": "codexctl build --task {} --context-pack {}".format(
                                        current_task_id,
                                        context_pack["relative_path"],
                                    ),
                                    "expected": codexctl.render_prompt(codex_model),
                                    "normalizer": normalize_codex_prompt_generated_line,
                                }
                            )
                    else:
                        variants.append(
                            {
                                "label": "codexctl build --task {}".format(current_task_id),
                                "expected": codexctl.render_prompt(codex_model),
                                "normalizer": normalize_codex_prompt_generated_line,
                            }
                        )
                except codexctl.CodexError as exc:
                    render_errors.append("CODEX_PROMPT_RENDER_FAILED: {}".format(exc.message))
                except Exception as exc:
                    render_errors.append("CODEX_PROMPT_RENDER_FAILED: {}".format(exc))

    matched = compare_generated_variants(
        root=root,
        path=codex_prompt,
        variants=variants,
        result=result,
        allow_missing=args.allow_missing_generated,
    )

    if not matched:
        for error in render_errors:
            result.error(error)

def check_docs(root, args, result):
    if DOCCTL_IMPORT_ERROR is not None:
        result.error("DOCCTL_IMPORT_FAILED: {}".format(DOCCTL_IMPORT_ERROR))
        return None

    docs_path = root / "AI_PROJECT" / "state" / "docs.json"
    doc_events = root / "AI_PROJECT" / "events" / "doc-events.jsonl"
    docs_index = root / "AI_PROJECT" / "generated" / "DOCS_INDEX.md"
    docs_gaps = root / "AI_PROJECT" / "generated" / "DOCS_GAPS.md"

    if not docs_path.exists():
        if args.allow_uninitialized:
            result.warn("docs state not initialized: {}".format(rel(root, docs_path)))
        return None

    docs_state = read_json(docs_path, result)

    if docs_state is None:
        return None

    errors = docctl.validate_docs(docs_state, root)

    if errors:
        for error in errors:
            result.error("DOCS_VALIDATION_FAILED: {}".format(error))
    else:
        result.ok("docs state valid: {}".format(rel(root, docs_path)))

    check_event_log(
        root=root,
        path=doc_events,
        expected_revision=docs_state.get("revision"),
        result=result,
        required_when_state_exists=True,
    )

    if not errors:
        compare_generated(
            root=root,
            path=docs_index,
            expected=docctl.render_index_markdown(docs_state),
            result=result,
            allow_missing=args.allow_missing_generated,
        )

        compare_generated(
            root=root,
            path=docs_gaps,
            expected=docctl.render_gaps_markdown(docs_state, root),
            result=result,
            allow_missing=args.allow_missing_generated,
        )

        check_generated_header(
            root=root,
            path=docs_index,
            result=result,
            allow_missing=args.allow_missing_generated,
        )

        check_generated_header(
            root=root,
            path=docs_gaps,
            result=result,
            allow_missing=args.allow_missing_generated,
        )

    return docs_state

def check_protected_dirs(root, args, result):
    ai_project = root / "AI_PROJECT"
    state = ai_project / "state"
    events = ai_project / "events"
    generated = ai_project / "generated"

    if not ai_project.exists():
        if args.allow_uninitialized:
            result.warn("AI_PROJECT directory does not exist")
            return

        result.error("AI_PROJECT_NOT_FOUND: {}".format(rel(root, ai_project)))
        return

    for path in [state, events, generated]:
        if not path.exists():
            if args.allow_uninitialized:
                result.warn("protected directory missing: {}".format(rel(root, path)))
            else:
                result.error("PROTECTED_DIRECTORY_MISSING: {}".format(rel(root, path)))
        elif not path.is_dir():
            result.error("PROTECTED_PATH_NOT_DIRECTORY: {}".format(rel(root, path)))
        else:
            result.ok("protected directory exists: {}".format(rel(root, path)))

def run_checks(args):
    root = Path(args.root).resolve()
    result = CheckResult()

    check_protected_dirs(root, args, result)

    plan = check_plan(root, args, result)
    check_tasks(root, args, result, plan)
    check_docs(root, args, result)

    return root, result

def print_text_report(root, result, verbose=False):
    if result.errors:
        print("PROTECTED_PROJECT_FILES_CHECK_FAILED:")
        for error in result.errors:
            print("- {}".format(error))
        else:
            print("OK: protected project files are valid")

    if result.warnings:
        print("")
        print("Warnings:")
        for warning in result.warnings:
            print("- {}".format(warning))

    if verbose and result.checked:
        print("")
        print("Checked:")
        for item in result.checked:
            print("- {}".format(item))

    print("")
    print("Root: {}".format(root))

def print_json_report(root, result):
    payload = {
    "ok": not result.failed,
    "root": str(root),
    "errors": result.errors,
    "warnings": result.warnings,
    "checked": result.checked,
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))

def build_parser():
    parser = argparse.ArgumentParser(
    description="Check protected Project Control Gateway files."
    )

    parser.add_argument(
        "--root",
        default=".",
        help="Repository/project root. Default: current directory.",
    )

    parser.add_argument(
        "--allow-uninitialized",
        action="store_true",
        help="Do not fail when AI_PROJECT or state files are not initialized.",
    )

    parser.add_argument(
        "--allow-missing-generated",
        action="store_true",
        help="Warn instead of failing when generated Markdown files are missing.",
    )

    parser.add_argument(
        "--skip-plan-check",
        action="store_true",
        help="Validate tasks without checking references to AI_PROJECT/state/plan.json.",
    )

    parser.add_argument(
        "--no-prompt-check",
        action="store_true",
        help="Skip CODEX_PROMPT.md freshness check.",
    )

    parser.add_argument(
        "--strict-prompt",
        action="store_true",
        help="Fail when current task exists but CODEX_PROMPT.md is missing, or prompt exists without current task.",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON report.",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print successful checks in text mode.",
    )

    return parser

def main(argv=None):
    args = build_parser().parse_args(argv)

    root, result = run_checks(args)

    if args.json:
        print_json_report(root, result)
    else:
        print_text_report(root, result, verbose=args.verbose)

    return 1 if result.failed else 0

if __name__ == "__main__":
    sys.exit(main())

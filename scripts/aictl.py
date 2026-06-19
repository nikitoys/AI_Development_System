#!/usr/bin/env python3
"""Unified facade over the existing project-control CLIs.

This entrypoint intentionally stays thin: registry-backed discovery is handled
in-process, while project-control behavior delegates to the validated legacy
ctl scripts.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ai_project_ctl.core.registry import (  # noqa: E402
    RegistryError,
    command_describe,
    command_list,
    default_command_registry,
)
from ai_project_ctl.core.result import CommandError, CommandMessage, CommandResult  # noqa: E402
from ai_project_ctl.core.workflows import (  # noqa: E402
    TaskBulkImportRequest,
    TaskCreateRequest,
    run_task_bulk_import_workflow,
    run_workflow,
    run_task_create_workflow,
    workflow_describe,
    workflow_list,
    workflow_preview,
)
from ai_project_ctl.pipeline.session import (  # noqa: E402
    check_generated as check_pipeline_generated,
    complete_session,
    create_session,
    record_step_result,
    render_status as render_pipeline_status,
    start_step,
    status_payload as pipeline_status_payload,
    stop_session,
    validate_sessions as validate_pipeline_sessions,
)
from ai_project_ctl.pipeline.runner import run_next as run_pipeline_next  # noqa: E402


class FacadeError(CommandError):
    """Stable error raised by the aictl facade."""


def _extract_json_flag(argv: Sequence[str]) -> tuple[list[str], bool]:
    filtered = []
    json_output = False
    for item in argv:
        if item == "--json":
            json_output = True
            continue
        filtered.append(item)
    return filtered, json_output


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _json_or_text(text: str) -> tuple[Any | None, str]:
    stripped = text.strip()
    if not stripped:
        return None, ""
    try:
        return json.loads(stripped), ""
    except json.JSONDecodeError:
        return None, text


def _display_argv(argv: Sequence[str]) -> list[str]:
    display = []
    for index, value in enumerate(argv):
        if index == 0:
            display.append("python")
            continue
        try:
            path = Path(value)
            if path.is_absolute():
                display.append(str(path.relative_to(REPO_ROOT)))
                continue
        except ValueError:
            pass
        display.append(value)
    return display


def _script_argv(
    script_name: str,
    args: argparse.Namespace,
    command_args: Iterable[str],
    *,
    include_actor: bool = True,
) -> list[str]:
    argv = [
        sys.executable,
        str(SCRIPTS_DIR / script_name),
        "--root",
        args.root,
    ]
    if include_actor:
        argv.extend(["--actor", args.actor])
    argv.extend(command_args)
    return argv


def _run_subprocess(argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(argv),
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _emit_human_process(completed: subprocess.CompletedProcess[str]) -> int:
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    return completed.returncode


def _delegated_result(
    command_name: str,
    domain: str,
    argv: Sequence[str],
    completed: subprocess.CompletedProcess[str],
) -> CommandResult:
    parsed_stdout, text_stdout = _json_or_text(completed.stdout)
    data: dict[str, Any] = {
        "delegate": _display_argv(argv),
        "returncode": completed.returncode,
    }
    if parsed_stdout is not None:
        data["result"] = parsed_stdout
    elif text_stdout:
        data["stdout"] = text_stdout
    if completed.stderr:
        data["stderr"] = completed.stderr

    result = CommandResult(
        ok=completed.returncode == 0,
        command=command_name,
        domain=domain,
        message=(
            "Delegated command completed."
            if completed.returncode == 0
            else "Delegated command failed."
        ),
        data=data,
    )
    if completed.returncode != 0:
        result.errors.append(
            CommandMessage(
                code="DELEGATE_FAILED",
                message="Delegated command exited with status {}".format(
                    completed.returncode
                ),
                details={"delegate": _display_argv(argv)},
            )
        )
    return result


def _run_delegated(
    command_name: str,
    domain: str,
    args: argparse.Namespace,
    argv: Sequence[str],
) -> int:
    completed = _run_subprocess(argv)
    if not args.json:
        return _emit_human_process(completed)

    _print_json(_delegated_result(command_name, domain, argv, completed).to_dict())
    return completed.returncode


DOCTOR_PASS = "PASS"
DOCTOR_WARN = "WARN"
DOCTOR_FAIL = "FAIL"

DOCTOR_CURRENT_STATUSES = {
    "planned",
    "ready",
    "in_progress",
    "blocked",
    "in_review",
    "changes_requested",
}


def _doctor_command_text(argv: Sequence[str]) -> str:
    return shlex.join(_display_argv(argv))


def _output_snippet(stdout: str, stderr: str, *, max_lines: int = 3) -> str:
    lines = []
    for text in (stdout, stderr):
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                lines.append(stripped)
            if len(lines) >= max_lines:
                return " | ".join(lines)
    return ""


def _doctor_finding(
    status: str,
    check: str,
    message: str,
    *,
    argv: Sequence[str] | None = None,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    finding: dict[str, Any] = {
        "status": status,
        "check": check,
        "message": message,
    }
    if argv:
        finding["command"] = _doctor_command_text(argv)
    if details:
        finding["details"] = dict(details)
    return finding


def _append_cli_diagnostic(
    findings: list[dict[str, Any]],
    args: argparse.Namespace,
    check: str,
    script_name: str,
    command_args: Sequence[str],
    pass_message: str,
    *,
    include_actor: bool = True,
    failure_status: str = DOCTOR_FAIL,
) -> subprocess.CompletedProcess[str]:
    argv = _script_argv(
        script_name,
        args,
        command_args,
        include_actor=include_actor,
    )
    completed = _run_subprocess(argv)
    snippet = _output_snippet(completed.stdout, completed.stderr)
    if completed.returncode == 0:
        findings.append(
            _doctor_finding(
                DOCTOR_PASS,
                check,
                snippet or pass_message,
                argv=argv,
                details={"returncode": completed.returncode},
            )
        )
    else:
        findings.append(
            _doctor_finding(
                failure_status,
                check,
                snippet or "Command failed.",
                argv=argv,
                details={
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                },
            )
        )
    return completed


def _protected_error_is_prompt_context_warning(error: str, *, strict_prompt: bool) -> bool:
    if strict_prompt:
        return False
    warning_fragments = (
        "MISSING_GENERATED_PROMPT:",
        "ORPHAN_GENERATED_PROMPT:",
        "OUTDATED_GENERATED_FILE: AI_PROJECT/generated/CODEX_PROMPT.md",
        "CODEX_PROMPT_RENDER_FAILED: STALE_CONTEXT_PACK:",
    )
    return any(fragment in error for fragment in warning_fragments)


def _doctor_counts(findings: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {
        DOCTOR_PASS: sum(1 for finding in findings if finding.get("status") == DOCTOR_PASS),
        DOCTOR_WARN: sum(1 for finding in findings if finding.get("status") == DOCTOR_WARN),
        DOCTOR_FAIL: sum(1 for finding in findings if finding.get("status") == DOCTOR_FAIL),
    }


def _doctor_overall_status(counts: Mapping[str, int]) -> str:
    if counts.get(DOCTOR_FAIL, 0):
        return DOCTOR_FAIL
    if counts.get(DOCTOR_WARN, 0):
        return DOCTOR_WARN
    return DOCTOR_PASS


def _parse_colon_lines(text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        parsed[key.strip().lower()] = value.strip()
    return parsed


def _read_text_optional(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        return ""


def _append_registry_diagnostic(findings: list[dict[str, Any]]) -> None:
    try:
        descriptor = _ensure_implemented("project.doctor")
    except CommandError as exc:
        findings.append(
            _doctor_finding(
                DOCTOR_FAIL,
                "command registry",
                exc.message,
                details={"code": exc.code, "command": "project.doctor"},
            )
        )
        return

    if descriptor.get("kind") != "validation":
        findings.append(
            _doctor_finding(
                DOCTOR_WARN,
                "command registry",
                "project.doctor is implemented but not classified as validation.",
                details={"kind": descriptor.get("kind")},
            )
        )
        return

    findings.append(
        _doctor_finding(
            DOCTOR_PASS,
            "command registry",
            "project.doctor is registered, implemented, and classified as validation.",
            details={"availability": descriptor.get("availability")},
        )
    )


def _append_protected_files_diagnostic(
    findings: list[dict[str, Any]],
    args: argparse.Namespace,
) -> None:
    command_args = []
    for flag in (
        "allow_uninitialized",
        "allow_missing_generated",
        "skip_plan_check",
        "no_prompt_check",
        "strict_prompt",
    ):
        if getattr(args, flag):
            command_args.append("--{}".format(flag.replace("_", "-")))
    command_args.append("--json")

    argv = _script_argv(
        "check-protected-project-files.py",
        args,
        command_args,
        include_actor=False,
    )
    completed = _run_subprocess(argv)
    parsed, text_stdout = _json_or_text(completed.stdout)
    details: dict[str, Any] = {
        "returncode": completed.returncode,
    }

    if isinstance(parsed, dict):
        errors = list(parsed.get("errors") or [])
        warnings = list(parsed.get("warnings") or [])
        checked = list(parsed.get("checked") or [])
        details.update(
            {
                "errors": errors,
                "warnings": warnings,
                "checked_count": len(checked),
            }
        )
        prompt_context_warnings = [
            error
            for error in errors
            if _protected_error_is_prompt_context_warning(
                error,
                strict_prompt=bool(args.strict_prompt),
            )
        ]
        blocking_errors = [
            error for error in errors if error not in prompt_context_warnings
        ]
        details["blocking_errors"] = blocking_errors
        details["prompt_context_warnings"] = prompt_context_warnings
        if blocking_errors or (completed.returncode != 0 and not errors):
            findings.append(
                _doctor_finding(
                    DOCTOR_FAIL,
                    "protected project files",
                    "Protected-file check failed with {} error(s).".format(
                        len(blocking_errors)
                    ),
                    argv=argv,
                    details=details,
                )
            )
        elif errors:
            findings.append(
                _doctor_finding(
                    DOCTOR_WARN,
                    "protected project files",
                    "Protected-file check found {} prompt/context warning(s).".format(
                        len(errors)
                    ),
                    argv=argv,
                    details=details,
                )
            )
        elif warnings:
            findings.append(
                _doctor_finding(
                    DOCTOR_WARN,
                    "protected project files",
                    "Protected-file check passed with {} warning(s).".format(
                        len(warnings)
                    ),
                    argv=argv,
                    details=details,
                )
            )
        else:
            findings.append(
                _doctor_finding(
                    DOCTOR_PASS,
                    "protected project files",
                    "Protected-file check passed with {} successful check(s).".format(
                        len(checked)
                    ),
                    argv=argv,
                    details=details,
                )
            )
        return

    details.update({"stdout": text_stdout or completed.stdout, "stderr": completed.stderr})
    findings.append(
        _doctor_finding(
            DOCTOR_FAIL,
            "protected project files",
            _output_snippet(completed.stdout, completed.stderr)
            or "Protected-file check did not return JSON.",
            argv=argv,
            details=details,
        )
    )


def _append_current_task_diagnostic(
    findings: list[dict[str, Any]],
    args: argparse.Namespace,
) -> str:
    argv = _script_argv("taskctl.py", args, ["current", "show", "--json"])
    completed = _run_subprocess(argv)
    parsed, text_stdout = _json_or_text(completed.stdout)

    if completed.returncode != 0:
        findings.append(
            _doctor_finding(
                DOCTOR_FAIL,
                "current task",
                _output_snippet(completed.stdout, completed.stderr)
                or "Current task command failed.",
                argv=argv,
                details={
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                },
            )
        )
        return ""

    if not isinstance(parsed, dict) or not parsed.get("id"):
        findings.append(
            _doctor_finding(
                DOCTOR_WARN,
                "current task",
                text_stdout.strip() or "No current task selected.",
                argv=argv,
                details={"returncode": completed.returncode},
            )
        )
        return ""

    task_id = str(parsed.get("id"))
    status = str(parsed.get("status") or "")
    if status in DOCTOR_CURRENT_STATUSES:
        findings.append(
            _doctor_finding(
                DOCTOR_PASS,
                "current task",
                "Current task {} is {}.".format(task_id, status),
                argv=argv,
                details={"task_id": task_id, "status": status},
            )
        )
    else:
        findings.append(
            _doctor_finding(
                DOCTOR_FAIL,
                "current task",
                "Current task {} has non-current-compatible status {}.".format(
                    task_id,
                    status or "unknown",
                ),
                argv=argv,
                details={"task_id": task_id, "status": status},
            )
        )
    return task_id


def _append_codex_status_diagnostic(
    findings: list[dict[str, Any]],
    args: argparse.Namespace,
    current_task_id: str,
) -> None:
    argv = _script_argv(
        "codexctl.py",
        args,
        ["status"],
    )
    completed = _run_subprocess(argv)
    fields = _parse_colon_lines(completed.stdout)
    status = fields.get("status", "").lower()
    code = fields.get("code", "")
    source_id = fields.get("source id", "")
    prompt_exists = fields.get("prompt exists", "")
    root = Path(args.root).resolve()
    status_path = root / "AI_PROJECT" / "generated" / "CODEX_STATUS.md"
    execution_path = root / "AI_PROJECT" / "state" / "current_execution.json"
    details = {
        "returncode": completed.returncode,
        "code": code,
        "status": status,
        "source_id": source_id,
        "prompt_exists": prompt_exists,
    }

    if completed.returncode != 0:
        findings.append(
            _doctor_finding(
                DOCTOR_WARN,
                "codex prompt/status",
                _output_snippet(completed.stdout, completed.stderr)
                or "Codex status command failed.",
                argv=argv,
                details=details,
            )
        )
        return

    warnings = []
    if status != "ready" or code != "CODEX_READY":
        warnings.append("Codex prompt package is not ready: {}".format(code or status or "unknown"))
    if current_task_id and source_id and source_id != current_task_id:
        warnings.append(
            "Codex source {} does not match current task {}.".format(
                source_id,
                current_task_id,
            )
        )
    if prompt_exists == "yes" and not execution_path.exists():
        warnings.append("CODEX_PROMPT.md exists without current_execution.json.")
    if execution_path.exists() and not status_path.exists():
        warnings.append("CODEX_STATUS.md is missing.")
    if status_path.exists():
        status_text = _read_text_optional(status_path)
        if source_id and "Source ID: `{}`".format(source_id) not in status_text:
            warnings.append("CODEX_STATUS.md may be stale for source {}.".format(source_id))
        if status and "Status: `{}`".format(status.upper()) not in status_text:
            warnings.append("CODEX_STATUS.md may be stale for status {}.".format(status))

    if warnings:
        findings.append(
            _doctor_finding(
                DOCTOR_WARN,
                "codex prompt/status",
                "; ".join(warnings),
                argv=argv,
                details=details,
            )
        )
    else:
        findings.append(
            _doctor_finding(
                DOCTOR_PASS,
                "codex prompt/status",
                "Codex prompt package is ready for {}.".format(source_id or "current source"),
                argv=argv,
                details=details,
            )
        )


def _append_context_status_diagnostic(
    findings: list[dict[str, Any]],
    args: argparse.Namespace,
    current_task_id: str,
) -> None:
    argv = _script_argv("contextctl.py", args, ["status"])
    completed = _run_subprocess(argv)
    fields = _parse_colon_lines(completed.stdout)
    context_task = fields.get("current context task", "")
    mode = fields.get("current context mode", "")
    details = {
        "returncode": completed.returncode,
        "mode": mode,
        "context_task": context_task,
    }

    if completed.returncode != 0:
        findings.append(
            _doctor_finding(
                DOCTOR_WARN,
                "context pack status",
                _output_snippet(completed.stdout, completed.stderr)
                or "Context status command failed.",
                argv=argv,
                details=details,
            )
        )
        return

    if current_task_id and mode == "task" and context_task and context_task != current_task_id:
        findings.append(
            _doctor_finding(
                DOCTOR_WARN,
                "context pack status",
                "Context Pack task {} does not match current task {}.".format(
                    context_task,
                    current_task_id,
                ),
                argv=argv,
                details=details,
            )
        )
    elif mode:
        findings.append(
            _doctor_finding(
                DOCTOR_PASS,
                "context pack status",
                "Context Pack mode is {}{}.".format(
                    mode,
                    " for {}".format(context_task) if context_task else "",
                ),
                argv=argv,
                details=details,
            )
        )
    else:
        findings.append(
            _doctor_finding(
                DOCTOR_WARN,
                "context pack status",
                "No current Context Pack metadata found.",
                argv=argv,
                details=details,
            )
        )


def _doctor_result(root: Path, findings: list[dict[str, Any]]) -> CommandResult:
    counts = _doctor_counts(findings)
    overall = _doctor_overall_status(counts)
    result = CommandResult(
        ok=overall != DOCTOR_FAIL,
        command="project.doctor",
        domain="project",
        message="Project doctor completed with overall status {}.".format(overall),
        data={
            "overall_status": overall,
            "summary": counts,
            "root": str(root),
            "findings": findings,
        },
    )

    for finding in findings:
        status = finding.get("status")
        message = "{}: {}".format(finding.get("check"), finding.get("message"))
        if status == DOCTOR_WARN:
            result.warnings.append(
                CommandMessage(
                    code="DOCTOR_WARN",
                    message=message,
                    details=finding,
                )
            )
        elif status == DOCTOR_FAIL:
            result.errors.append(
                CommandMessage(
                    code="DOCTOR_FAIL",
                    message=message,
                    details=finding,
                )
            )
    return result


def _emit_doctor_text(root: Path, findings: Sequence[Mapping[str, Any]]) -> None:
    counts = _doctor_counts(findings)
    overall = _doctor_overall_status(counts)
    print("Project Doctor: {}".format(overall))
    print(
        "Summary: {PASS} PASS, {WARN} WARN, {FAIL} FAIL".format(
            **counts,
        )
    )
    print("")
    for finding in findings:
        print("{:<4}  {}".format(finding.get("status"), finding.get("check")))
        print("      {}".format(finding.get("message")))
        if finding.get("command"):
            print("      command: {}".format(finding.get("command")))
    print("")
    print("Root: {}".format(root))


def _resolve_task_ref(args: argparse.Namespace, task_ref: str) -> str:
    argv = _script_argv(
        "taskctl.py",
        args,
        ["task", "resolve", task_ref, "--json"],
    )
    completed = _run_subprocess(argv)
    if completed.returncode != 0:
        raise FacadeError(
            "TASK_RESOLVE_FAILED",
            "Could not resolve task ref for facade delegation: {}".format(task_ref),
            details={
                "delegate": _display_argv(argv),
                "stderr": completed.stderr,
                "stdout": completed.stdout,
            },
        )

    parsed, text = _json_or_text(completed.stdout)
    if not isinstance(parsed, dict) or not parsed.get("id"):
        raise FacadeError(
            "TASK_RESOLVE_INVALID_OUTPUT",
            "taskctl.py task resolve did not return a task id.",
            details={"delegate": _display_argv(argv), "stdout": text or completed.stdout},
        )
    return str(parsed["id"])


def _command_error_result(
    command_name: str,
    domain: str,
    error: CommandError,
) -> CommandResult:
    return CommandResult.failure(
        command=command_name,
        domain=domain,
        message=error.message,
        errors=[error.to_message()],
    )


def _registry_descriptor(name: str) -> dict[str, Any]:
    return command_describe(name, registry=default_command_registry())


def _ensure_implemented(name: str) -> dict[str, Any]:
    descriptor = _registry_descriptor(name)
    if descriptor["availability"] != "implemented":
        raise FacadeError(
            "COMMAND_NOT_IMPLEMENTED",
            "Command is registered but not executable yet: {}".format(name),
            details={"command": name, "availability": descriptor["availability"]},
        )
    return descriptor


def cmd_command_list(args: argparse.Namespace) -> int:
    commands = command_list(
        domain=args.domain_filter,
        include_planned=not args.implemented_only,
    )
    if args.json:
        result = CommandResult.success(
            command="command.list",
            domain="command",
            message="Listed registered commands.",
            data={"commands": commands},
        )
        _print_json(result.to_dict())
        return 0

    if not commands:
        print("No commands registered.")
        return 0

    name_width = max(len(command["name"]) for command in commands)
    for command in commands:
        print(
            "{name:<{width}}  {kind:<10}  {availability:<11}  {description}".format(
                name=command["name"],
                width=name_width,
                kind=command["kind"],
                availability=command["availability"],
                description=command["description"],
            )
        )
    return 0


def cmd_command_describe(args: argparse.Namespace) -> int:
    descriptor = command_describe(args.name)
    if args.json:
        result = CommandResult.success(
            command="command.describe",
            domain="command",
            message="Described registered command.",
            data={"command": descriptor},
        )
        _print_json(result.to_dict())
        return 0

    print("{} ({}, {})".format(
        descriptor["name"],
        descriptor["kind"],
        descriptor["availability"],
    ))
    print(descriptor["description"])
    if descriptor["legacy_command"]:
        print("Legacy: {}".format("; ".join(descriptor["legacy_command"])))
    if descriptor["arguments"]:
        print("Arguments:")
        for argument in descriptor["arguments"]:
            required = "required" if argument["required"] else "optional"
            print("  --{} ({}) {}".format(argument["name"], required, argument["description"]))
    if descriptor["notes"]:
        print("Notes:")
        for note in descriptor["notes"]:
            print("  - {}".format(note))
    return 0


def cmd_workflow_list(args: argparse.Namespace) -> int:
    _ensure_implemented("workflow.list")
    workflows = workflow_list()
    if args.json:
        result = CommandResult.success(
            command="workflow.list",
            domain="workflow",
            message="Listed workflows.",
            data={"workflows": workflows},
        )
        _print_json(result.to_dict())
        return 0

    name_width = max(len(workflow["name"]) for workflow in workflows) if workflows else 8
    for workflow in workflows:
        confirmation = "confirm" if workflow.get("confirmation_required") else "no-confirm"
        print(
            "{name:<{width}}  {confirm:<10}  {description}".format(
                name=workflow["name"],
                width=name_width,
                confirm=confirmation,
                description=workflow["description"],
            )
        )
    return 0


def cmd_workflow_describe(args: argparse.Namespace) -> int:
    _ensure_implemented("workflow.describe")
    payload = (
        workflow_preview(
            args.name,
            task_ref=args.task,
            change_ref=args.change,
            epic_ref=args.epic,
            notes=args.notes or "",
            root=args.root,
            actor=args.actor,
        )
        if args.task or args.change or args.epic or args.notes
        else {"workflow": workflow_describe(args.name)}
    )
    if args.json:
        result = CommandResult.success(
            command="workflow.describe",
            domain="workflow",
            message="Described workflow.",
            data=payload,
        )
        _print_json(result.to_dict())
        return 0

    workflow = payload["workflow"]
    print("{} ({})".format(workflow["name"], workflow["label"]))
    print(workflow["description"])
    print("Confirmation required: {}".format("yes" if workflow["confirmation_required"] else "no"))
    print("Steps:")
    for step in payload.get("steps") or workflow.get("steps") or []:
        command = step.get("command") or step.get("command_template") or []
        print("  - {} [{}] {}".format(
            step.get("title"),
            step.get("route"),
            " ".join(command),
        ))
    return 0


def cmd_workflow_run(args: argparse.Namespace) -> int:
    _ensure_implemented(args.name)
    result = run_workflow(
        args.name,
        task_ref=args.task or "",
        change_ref=args.change or "",
        epic_ref=args.epic or "",
        notes=args.notes or "",
        root=args.root,
        actor=args.actor,
        confirmed=args.confirm,
    )
    if args.json:
        _print_json(result.to_dict())
        return 0 if result.ok else 1

    _emit_workflow_result(result)
    return 0 if result.ok else 1


def _emit_workflow_result(result: CommandResult) -> None:
    print("{}: {}".format("OK" if result.ok else "ERROR", result.message))
    print("Workflow: {}".format(result.command))
    task = result.data.get("task") or {}
    task_label = (
        task.get("ref")
        or task.get("id")
        or result.data.get("task_ref")
        or result.data.get("created_task_id")
        or ""
    )
    if task_label:
        print("Task: {}".format(task_label))
    change = result.data.get("change") or {}
    change_label = change.get("id") or result.data.get("change_ref") or ""
    if change_label:
        print("Change: {}".format(change_label))
    epic = result.data.get("epic") or {}
    epic_label = epic.get("key") or epic.get("id") or result.data.get("epic_ref") or ""
    if epic_label:
        print("Epic: {}".format(epic_label))

    steps = result.data.get("steps") or result.data.get("preview") or []
    if steps:
        print("Steps:")
        for index, step in enumerate(steps, start=1):
            status = step.get("status") or ("preview" if step.get("command") else "")
            command = step.get("command") or step.get("command_template") or []
            print("  {}. {} [{}]".format(index, step.get("title", ""), status))
            print("     {}".format(" ".join(command)))
            if step.get("skip_reason"):
                print("     skipped: {}".format(step["skip_reason"]))

    for error in result.errors:
        print("ERROR: {}: {}".format(error.code, error.message), file=sys.stderr)
    if result.owner_action_required:
        print("Owner action required: {}".format(result.owner_action_required))
    if result.next_actions:
        print("Next actions:")
        for action in result.next_actions:
            print("  - {}".format(action))


def _emit_command_result(result: CommandResult, args: argparse.Namespace) -> int:
    if args.json:
        _print_json(result.to_dict())
        return 0 if result.ok else 1
    print(result.message)
    if result.data.get("session_id"):
        print("Session: {}".format(result.data["session_id"]))
    for error in result.errors:
        print("ERROR: {}: {}".format(error.code, error.message), file=sys.stderr)
    return 0 if result.ok else 1


def _validation_result_to_command(
    command_name: str,
    domain: str,
    validation,
    *,
    ok_message: str,
) -> CommandResult:
    if validation.ok:
        return CommandResult.success(
            command=command_name,
            domain=domain,
            message=ok_message,
        )
    return CommandResult.failure(
        command=command_name,
        domain=domain,
        message="VALIDATION_FAILED",
        errors=[
            CommandMessage(issue.code, issue.message, issue.path)
            for issue in validation.errors
        ],
    )


def _json_mapping_arg(text: str | None) -> dict[str, Any]:
    if not text:
        return {}
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise FacadeError(
            "INVALID_JSON_ARGUMENT",
            "Expected JSON object argument: {}".format(exc),
        ) from exc
    if not isinstance(value, dict):
        raise FacadeError("INVALID_JSON_ARGUMENT", "Expected JSON object argument.")
    return value


def cmd_task_list(args: argparse.Namespace) -> int:
    _ensure_implemented("task.list")
    command_args = ["task", "list"]
    if args.epic:
        command_args.extend(["--epic", args.epic])
    if args.status:
        command_args.extend(["--status", args.status])
    if args.current:
        command_args.append("--current")
    if args.json:
        command_args.append("--json")
    return _run_delegated(
        "task.list",
        "task",
        args,
        _script_argv("taskctl.py", args, command_args),
    )


def cmd_task_show(args: argparse.Namespace) -> int:
    _ensure_implemented("task.show")
    return _run_delegated(
        "task.show",
        "task",
        args,
        _script_argv("taskctl.py", args, ["task", "show", args.task_ref]),
    )


def _tuple_or_empty(values: Sequence[str] | None) -> tuple[str, ...]:
    return tuple(str(value).strip() for value in values or () if str(value).strip())


def _task_create_request(args: argparse.Namespace) -> TaskCreateRequest:
    return TaskCreateRequest(
        epic=args.epic,
        title=args.title,
        summary=args.summary or "",
        description=args.description or "",
        priority=args.priority,
        status=args.status,
        active_role=args.active_role or "",
        active_stage=args.active_stage or "",
        active_document=args.active_document or "",
        expected_result=args.expected_result or "",
        verification_mode=args.verification_mode,
        scope=_tuple_or_empty(args.scope),
        out_of_scope=_tuple_or_empty(args.out_of_scope),
        allowed_files=_tuple_or_empty(args.allowed_file),
        acceptance=_tuple_or_empty(args.acceptance),
        review_instructions=_tuple_or_empty(args.review_instruction),
        notes=_tuple_or_empty(args.note),
        depends_on=_tuple_or_empty(args.depends_on),
        dependency_reason=args.dependency_reason or "",
    )


def cmd_task_create(args: argparse.Namespace) -> int:
    _ensure_implemented("task.create")
    result = run_task_create_workflow(
        _task_create_request(args),
        root=args.root,
        actor=args.actor,
        confirmed=args.confirm,
    )
    if args.json:
        _print_json(result.to_dict())
        return 0 if result.ok else 1

    _emit_workflow_result(result)
    return 0 if result.ok else 1


def _task_import_source_text(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if args.file is not None:
        try:
            return Path(args.file).read_text(encoding="utf-8")
        except OSError as exc:
            raise FacadeError(
                "TASK_IMPORT_FILE_READ_FAILED",
                "Could not read task import file: {}".format(args.file),
                details={"file": args.file, "error": str(exc)},
            ) from exc
    return sys.stdin.read()


def cmd_task_import(args: argparse.Namespace) -> int:
    _ensure_implemented("task.import")
    if args.preview and args.confirm:
        raise FacadeError(
            "TASK_IMPORT_CONFLICTING_FLAGS",
            "--preview and --confirm cannot be used together.",
        )
    result = run_task_bulk_import_workflow(
        TaskBulkImportRequest(source_text=_task_import_source_text(args)),
        root=args.root,
        actor=args.actor,
        confirmed=args.confirm,
    )
    if args.json:
        _print_json(result.to_dict())
        return 0 if result.ok else 1

    _emit_workflow_result(result)
    return 0 if result.ok else 1


def cmd_task_transition(args: argparse.Namespace) -> int:
    _ensure_implemented("task.transition")
    return _run_delegated(
        "task.transition",
        "task",
        args,
        _script_argv(
            "taskctl.py",
            args,
            ["task", "transition", args.task_ref, "--to", args.to],
        ),
    )


def cmd_task_report_submit(args: argparse.Namespace) -> int:
    _ensure_implemented("task.report.submit")
    command_args = [
        "task",
        "report",
        "submit",
        "--task",
        args.task,
        "--file",
        args.file,
    ]
    if args.confirm:
        command_args.append("--confirm")
    if args.json:
        command_args.append("--json")
    return _run_delegated(
        "task.report.submit",
        "task",
        args,
        _script_argv("taskctl.py", args, command_args),
    )


def cmd_pipeline_status(args: argparse.Namespace) -> int:
    _ensure_implemented("pipeline.status")
    payload = pipeline_status_payload(root=args.root)
    result = CommandResult.success(
        command="pipeline.status",
        domain="pipeline",
        message="Pipeline status loaded.",
        data=payload,
    )
    if args.json:
        _print_json(result.to_dict())
        return 0

    print("Pipeline sessions revision: {}".format(payload.get("revision", 0)))
    print("Current session: {}".format(payload.get("current_session_id") or "none"))
    print("Sessions: {}".format(len(payload.get("sessions", []))))
    for session in payload.get("sessions", []):
        print(
            "- {id} [{status}] task={task} step={step} stop={stop}".format(
                id=session.get("id"),
                status=session.get("status"),
                task=session.get("current_task_id") or "none",
                step=session.get("current_step") or "none",
                stop=session.get("stop_reason") or "none",
            )
        )
    return 0


def cmd_pipeline_validate(args: argparse.Namespace) -> int:
    _ensure_implemented("pipeline.validate")
    result = _validation_result_to_command(
        "pipeline.validate",
        "pipeline",
        validate_pipeline_sessions(root=args.root),
        ok_message="OK: pipeline sessions are valid",
    )
    return _emit_command_result(result, args)


def cmd_pipeline_render(args: argparse.Namespace) -> int:
    _ensure_implemented("pipeline.render")
    render_pipeline_status(root=args.root)
    result = CommandResult.success(
        command="pipeline.render",
        domain="pipeline",
        message="OK: rendered pipeline status",
        data={"path": str(Path(args.root).resolve() / "AI_PROJECT" / "generated" / "PIPELINE_STATUS.md")},
    )
    result.generated_files.append(result.data["path"])
    result.changed_files.append(result.data["path"])
    return _emit_command_result(result, args)


def cmd_pipeline_check_generated(args: argparse.Namespace) -> int:
    _ensure_implemented("pipeline.check_generated")
    result = _validation_result_to_command(
        "pipeline.check_generated",
        "pipeline",
        check_pipeline_generated(root=args.root),
        ok_message="OK: generated pipeline status is up to date",
    )
    return _emit_command_result(result, args)


def cmd_pipeline_session_create(args: argparse.Namespace) -> int:
    _ensure_implemented("pipeline.session.create")
    result = create_session(
        root=args.root,
        actor=args.actor,
        policy_name=args.policy,
        task_refs=_tuple_or_empty(args.task_ref),
        epic_ids=_tuple_or_empty(args.epic),
        statuses=_tuple_or_empty(args.status_filter),
        max_tasks=args.max_tasks,
        order_by=args.order_by,
        current_task_id=args.current_task_id or "",
        current_task_ref=args.current_task_ref or "",
        linked_change_ids=_tuple_or_empty(args.change),
        report_ids=_tuple_or_empty(args.report),
        review_ids=_tuple_or_empty(args.review),
        commit_ids=_tuple_or_empty(args.commit),
        status=args.status,
    )
    return _emit_command_result(result, args)


def cmd_pipeline_run_next(args: argparse.Namespace) -> int:
    _ensure_implemented("pipeline.run_next")
    result = run_pipeline_next(
        args.session_id or "",
        root=args.root,
        actor=args.actor,
    )
    return _emit_command_result(result, args)


def cmd_pipeline_step_start(args: argparse.Namespace) -> int:
    _ensure_implemented("pipeline.step.start")
    result = start_step(
        args.session_id,
        args.step,
        root=args.root,
        actor=args.actor,
        task_id=args.task or "",
    )
    return _emit_command_result(result, args)


def cmd_pipeline_step_result(args: argparse.Namespace) -> int:
    _ensure_implemented("pipeline.step.result")
    result = record_step_result(
        args.session_id,
        args.step,
        args.result,
        root=args.root,
        actor=args.actor,
        task_id=args.task or "",
        gate_name=args.gate_name or "",
        gate_status=args.gate_status or "",
        gate_details=_json_mapping_arg(args.gate_details),
        stop_reason=args.stop_reason or "",
        linked_change_ids=_tuple_or_empty(args.change),
        report_ids=_tuple_or_empty(args.report),
        review_ids=_tuple_or_empty(args.review),
        commit_ids=_tuple_or_empty(args.commit),
    )
    return _emit_command_result(result, args)


def cmd_pipeline_session_stop(args: argparse.Namespace) -> int:
    _ensure_implemented("pipeline.session.stop")
    result = stop_session(
        args.session_id,
        args.reason,
        root=args.root,
        actor=args.actor,
        status=args.status,
    )
    return _emit_command_result(result, args)


def cmd_pipeline_session_complete(args: argparse.Namespace) -> int:
    _ensure_implemented("pipeline.session.complete")
    result = complete_session(
        args.session_id,
        root=args.root,
        actor=args.actor,
        reason=args.reason or "completed",
    )
    return _emit_command_result(result, args)


def cmd_current_set(args: argparse.Namespace) -> int:
    _ensure_implemented("current.set")
    return _run_delegated(
        "current.set",
        "current",
        args,
        _script_argv("taskctl.py", args, ["current", "set", args.task_ref]),
    )


def cmd_current_clear(args: argparse.Namespace) -> int:
    _ensure_implemented("current.clear")
    return _run_delegated(
        "current.clear",
        "current",
        args,
        _script_argv("taskctl.py", args, ["current", "clear"]),
    )


def cmd_epic_list(args: argparse.Namespace) -> int:
    _ensure_implemented("epic.list")
    command_args = ["epic", "list"]
    if args.initiative:
        command_args.extend(["--initiative", args.initiative])
    if args.json:
        command_args.append("--json")
    return _run_delegated(
        "epic.list",
        "epic",
        args,
        _script_argv("planctl.py", args, command_args),
    )


def cmd_context_build(args: argparse.Namespace) -> int:
    _ensure_implemented("context.build")
    command_args = ["pack", "build"]
    if args.task:
        command_args.extend(["--task", _resolve_task_ref(args, args.task)])
    if args.query:
        command_args.extend(["--query", args.query])
    if args.write:
        command_args.append("--write")
    if args.limit is not None:
        command_args.extend(["--limit", str(args.limit)])
    return _run_delegated(
        "context.build",
        "context",
        args,
        _script_argv("contextctl.py", args, command_args),
    )


def cmd_codex_prompt_build(args: argparse.Namespace) -> int:
    _ensure_implemented("codex.prompt.build")
    command_args = ["build"]
    if args.task:
        command_args.extend(["--task", _resolve_task_ref(args, args.task)])
    if args.change:
        command_args.extend(["--change", args.change])
    if args.with_context:
        command_args.append("--with-context")
    if args.context_pack:
        command_args.extend(["--context-pack", args.context_pack])
    return _run_delegated(
        "codex.prompt.build",
        "codex",
        args,
        _script_argv("codexctl.py", args, command_args),
    )


def cmd_docs_render(args: argparse.Namespace) -> int:
    _ensure_implemented("docs.render")
    return _run_delegated(
        "docs.render",
        "docs",
        args,
        _script_argv("docctl.py", args, ["render"]),
    )


def cmd_project_doctor(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    findings: list[dict[str, Any]] = []

    _append_registry_diagnostic(findings)
    _append_cli_diagnostic(
        findings,
        args,
        "plan validation",
        "planctl.py",
        ["validate"],
        "Plan state is valid.",
    )
    _append_cli_diagnostic(
        findings,
        args,
        "task validation",
        "taskctl.py",
        ["validate"],
        "Task state is valid.",
    )
    _append_cli_diagnostic(
        findings,
        args,
        "task dependency graph",
        "taskctl.py",
        ["task", "graph", "validate"]
        + (["--skip-plan-check"] if args.skip_plan_check else []),
        "Task dependency graph is valid.",
    )
    _append_cli_diagnostic(
        findings,
        args,
        "task generated output",
        "taskctl.py",
        ["check-generated"],
        "Generated task files are up to date.",
    )
    _append_cli_diagnostic(
        findings,
        args,
        "docs validation",
        "docctl.py",
        ["validate"],
        "Documentation state is valid.",
    )
    _append_cli_diagnostic(
        findings,
        args,
        "docs generated output",
        "docctl.py",
        ["check-generated"],
        "Generated documentation files are up to date.",
    )
    _append_cli_diagnostic(
        findings,
        args,
        "evolution validation",
        "evolutionctl.py",
        ["validate"],
        "Evolution state is valid.",
    )
    _append_cli_diagnostic(
        findings,
        args,
        "evolution generated output",
        "evolutionctl.py",
        ["check-generated"],
        "Generated evolution files are up to date.",
    )
    _append_cli_diagnostic(
        findings,
        args,
        "context validation",
        "contextctl.py",
        ["validate"],
        "Context control files are valid.",
    )
    _append_cli_diagnostic(
        findings,
        args,
        "context generated output",
        "contextctl.py",
        ["check-generated"],
        "Generated context files are up to date.",
        failure_status=DOCTOR_WARN,
    )
    _append_protected_files_diagnostic(findings, args)
    current_task_id = _append_current_task_diagnostic(findings, args)
    _append_codex_status_diagnostic(findings, args, current_task_id)
    _append_context_status_diagnostic(findings, args, current_task_id)

    result = _doctor_result(root, findings)
    if args.json:
        _print_json(result.to_dict())
    else:
        _emit_doctor_text(root, findings)
    return 0 if result.ok else 1


def cmd_project_protected_check(args: argparse.Namespace) -> int:
    _ensure_implemented("project.protected_check")
    command_args = ["--verbose"]
    if args.json:
        command_args.append("--json")
    return _run_delegated(
        "project.protected_check",
        "project",
        args,
        _script_argv(
            "check-protected-project-files.py",
            args,
            command_args,
            include_actor=False,
        ),
    )


PROJECT_RENDER_STEPS = (
    ("plan.render", "planctl.py", ("render",)),
    ("task.render", "taskctl.py", ("render",)),
    ("doc.render", "docctl.py", ("render",)),
    ("context.render", "contextctl.py", ("render",)),
    ("evolution.render", "evolutionctl.py", ("render",)),
)


def cmd_project_render(args: argparse.Namespace) -> int:
    _ensure_implemented("project.render")
    steps = []
    for step_name, script_name, command_args in PROJECT_RENDER_STEPS:
        argv = _script_argv(script_name, args, command_args)
        completed = _run_subprocess(argv)
        step_result = _delegated_result(step_name, "project", argv, completed)
        steps.append(step_result.to_dict())

        if not args.json:
            print("== {} ==".format(step_name))
            _emit_human_process(completed)

        if completed.returncode != 0:
            if args.json:
                result = CommandResult(
                    ok=False,
                    command="project.render",
                    domain="project",
                    message="Project render failed.",
                    data={"steps": steps},
                    errors=[
                        CommandMessage(
                            code="PROJECT_RENDER_FAILED",
                            message="{} failed with status {}".format(
                                step_name,
                                completed.returncode,
                            ),
                        )
                    ],
                )
                _print_json(result.to_dict())
            return completed.returncode

    if args.json:
        result = CommandResult.success(
            command="project.render",
            domain="project",
            message="Project render completed.",
            data={"steps": steps},
        )
        _print_json(result.to_dict())
    return 0


def cmd_web(args: argparse.Namespace) -> int:
    _ensure_implemented("web.serve")
    if args.json:
        raise FacadeError(
            "WEB_JSON_UNSUPPORTED",
            "The web server is an interactive local process and does not support --json.",
        )

    from ai_project_ctl.web.server import run_server

    run_server(args.root, host=args.host, port=args.port, actor=args.actor)
    return 0


def _add_project_doctor_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--allow-uninitialized", action="store_true")
    parser.add_argument("--allow-missing-generated", action="store_true")
    parser.add_argument("--skip-plan-check", action="store_true")
    parser.add_argument("--no-prompt-check", action="store_true")
    parser.add_argument("--strict-prompt", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Unified facade for AI Development System project-control commands"
    )
    parser.add_argument("--root", default=".", help="Repository/project root. Default: current directory.")
    parser.add_argument(
        "--actor",
        default=os.environ.get("AI_DEV_ACTOR", "human_owner"),
        help="Audit actor. Default: AI_DEV_ACTOR or human_owner.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print a machine-readable result. May appear before or after the command.",
    )

    sub = parser.add_subparsers(dest="domain", required=True)

    command = sub.add_parser("command", help="Discover and describe registered commands")
    command_sub = command.add_subparsers(dest="command_action", required=True)

    p = command_sub.add_parser("list", help="List registered commands")
    p.add_argument("--domain", dest="domain_filter")
    p.add_argument("--implemented-only", action="store_true")
    p.set_defaults(func=cmd_command_list, facade_command="command.list")

    p = command_sub.add_parser("describe", help="Describe one registered command")
    p.add_argument("name")
    p.set_defaults(func=cmd_command_describe, facade_command="command.describe")

    workflow = sub.add_parser("workflow", help="Workflow automation commands")
    workflow_sub = workflow.add_subparsers(dest="workflow_action", required=True)

    p = workflow_sub.add_parser("list", help="List available workflows")
    p.set_defaults(func=cmd_workflow_list, facade_command="workflow.list")

    p = workflow_sub.add_parser("describe", help="Describe a workflow")
    p.add_argument("name")
    p.add_argument("--task", help="Optional task ref for concrete step preview.")
    p.add_argument("--change", help="Optional Change ID for concrete step preview.")
    p.add_argument("--epic", help="Optional Epic ID or key for concrete step preview.")
    p.add_argument("--notes", help="Optional notes for concrete step preview.")
    p.set_defaults(func=cmd_workflow_describe, facade_command="workflow.describe")

    p = workflow_sub.add_parser("run", help="Run a confirmed workflow")
    p.add_argument("name")
    p.add_argument("--task")
    p.add_argument("--change")
    p.add_argument("--epic")
    p.add_argument("--notes")
    p.add_argument("--confirm", action="store_true")
    p.set_defaults(func=cmd_workflow_run, facade_command="workflow.run")

    task = sub.add_parser("task", help="Task facade commands")
    task_sub = task.add_subparsers(dest="task_action", required=True)

    p = task_sub.add_parser("list", help="List tasks through taskctl.py")
    p.add_argument("--epic")
    p.add_argument("--status")
    p.add_argument("--current", action="store_true")
    p.set_defaults(func=cmd_task_list, facade_command="task.list")

    p = task_sub.add_parser("show", help="Show a task through taskctl.py")
    p.add_argument("task_ref")
    p.set_defaults(func=cmd_task_show, facade_command="task.show")

    p = task_sub.add_parser("create", help="Create one task through the governed create-only workflow")
    p.add_argument("--epic", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--summary")
    p.add_argument("--description")
    p.add_argument("--priority", type=int, default=1)
    p.add_argument(
        "--status",
        default="planned",
        choices=(
            "proposed",
            "planned",
            "ready",
            "in_progress",
            "blocked",
            "in_review",
            "changes_requested",
            "approved",
            "done",
            "deferred",
            "archived",
        ),
    )
    p.add_argument("--active-role")
    p.add_argument("--active-stage")
    p.add_argument("--active-document")
    p.add_argument("--expected-result")
    p.add_argument(
        "--verification-mode",
        default="standard",
        choices=("light", "manual", "none", "standard", "strict"),
    )
    p.add_argument("--scope", action="append")
    p.add_argument("--out-of-scope", action="append", dest="out_of_scope")
    p.add_argument("--allowed-file", action="append")
    p.add_argument("--acceptance", action="append")
    p.add_argument("--review-instruction", action="append")
    p.add_argument("--note", action="append")
    p.add_argument("--depends-on", action="append")
    p.add_argument("--dependency-reason")
    p.add_argument(
        "--create-only",
        action="store_true",
        help="Document intent: create the task without selecting or starting it. This is the default behavior.",
    )
    p.add_argument("--confirm", action="store_true")
    p.set_defaults(func=cmd_task_create, facade_command="task.create")

    p = task_sub.add_parser("import", help="Preview or create multiple tasks from JSON")
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--text", help="JSON import payload.")
    source.add_argument("--file", help="Read JSON import payload from a UTF-8 text file.")
    p.add_argument(
        "--preview",
        action="store_true",
        help="Validate and show the command plan without creating tasks. This is the default without --confirm.",
    )
    p.add_argument("--confirm", action="store_true")
    p.set_defaults(func=cmd_task_import, facade_command="task.import")

    p = task_sub.add_parser("transition", help="Transition a task through taskctl.py")
    p.add_argument("task_ref")
    p.add_argument("--to", required=True)
    p.set_defaults(func=cmd_task_transition, facade_command="task.transition")

    report = task_sub.add_parser("report", help="Task execution report facade commands")
    report_sub = report.add_subparsers(dest="task_report_action", required=True)

    p = report_sub.add_parser("submit", help="Submit a structured execution report through taskctl.py")
    p.add_argument("--task", required=True)
    p.add_argument("--file", required=True)
    p.add_argument("--confirm", action="store_true")
    p.set_defaults(func=cmd_task_report_submit, facade_command="task.report.submit")

    pipeline = sub.add_parser("pipeline", help="Pipeline session facade commands")
    pipeline_sub = pipeline.add_subparsers(dest="pipeline_action", required=True)

    p = pipeline_sub.add_parser("status", help="Show pipeline session state")
    p.set_defaults(func=cmd_pipeline_status, facade_command="pipeline.status")

    p = pipeline_sub.add_parser("validate", help="Validate pipeline session state")
    p.set_defaults(func=cmd_pipeline_validate, facade_command="pipeline.validate")

    p = pipeline_sub.add_parser("render", help="Render pipeline generated status")
    p.set_defaults(func=cmd_pipeline_render, facade_command="pipeline.render")

    p = pipeline_sub.add_parser("check-generated", help="Check pipeline generated status freshness")
    p.set_defaults(func=cmd_pipeline_check_generated, facade_command="pipeline.check_generated")

    p = pipeline_sub.add_parser("run-next", help="Run one guarded pipeline step")
    p.add_argument("session_id", nargs="?")
    p.set_defaults(func=cmd_pipeline_run_next, facade_command="pipeline.run_next")

    session = pipeline_sub.add_parser("session", help="Pipeline session mutations")
    session_sub = session.add_subparsers(dest="pipeline_session_action", required=True)

    p = session_sub.add_parser("create", help="Create a governed pipeline session")
    p.add_argument("--policy", default="dry_run")
    p.add_argument("--task-ref", action="append")
    p.add_argument("--epic", action="append")
    p.add_argument("--status-filter", action="append")
    p.add_argument("--max-tasks", type=int)
    p.add_argument(
        "--order-by",
        default="execution",
        choices=("execution", "owner", "selected"),
    )
    p.add_argument("--current-task-id")
    p.add_argument("--current-task-ref")
    p.add_argument("--change", action="append")
    p.add_argument("--report", action="append")
    p.add_argument("--review", action="append")
    p.add_argument("--commit", action="append")
    p.add_argument(
        "--status",
        default="planned",
        choices=("planned", "running", "stopped", "blocked", "failed", "completed", "archived"),
    )
    p.set_defaults(func=cmd_pipeline_session_create, facade_command="pipeline.session.create")

    p = session_sub.add_parser("start-step", help="Record pipeline step start")
    p.add_argument("session_id")
    p.add_argument("--step", required=True)
    p.add_argument("--task")
    p.set_defaults(func=cmd_pipeline_step_start, facade_command="pipeline.step.start")

    p = session_sub.add_parser("step-result", help="Record pipeline step result")
    p.add_argument("session_id")
    p.add_argument("--step", required=True)
    p.add_argument(
        "--result",
        required=True,
        choices=("passed", "failed", "blocked", "skipped", "stopped"),
    )
    p.add_argument("--task")
    p.add_argument("--gate-name")
    p.add_argument(
        "--gate-status",
        choices=("pass", "warn", "fail", "blocked", "skipped", "unknown"),
    )
    p.add_argument("--gate-details")
    p.add_argument("--stop-reason")
    p.add_argument("--change", action="append")
    p.add_argument("--report", action="append")
    p.add_argument("--review", action="append")
    p.add_argument("--commit", action="append")
    p.set_defaults(func=cmd_pipeline_step_result, facade_command="pipeline.step.result")

    p = session_sub.add_parser("stop", help="Stop a pipeline session")
    p.add_argument("session_id")
    p.add_argument("--reason", required=True)
    p.add_argument("--status", default="stopped", choices=("stopped", "blocked", "failed"))
    p.set_defaults(func=cmd_pipeline_session_stop, facade_command="pipeline.session.stop")

    p = session_sub.add_parser("complete", help="Mark a pipeline session completed")
    p.add_argument("session_id")
    p.add_argument("--reason")
    p.set_defaults(func=cmd_pipeline_session_complete, facade_command="pipeline.session.complete")

    current = sub.add_parser("current", help="Current task facade commands")
    current_sub = current.add_subparsers(dest="current_action", required=True)

    p = current_sub.add_parser("set", help="Set current task through taskctl.py")
    p.add_argument("task_ref")
    p.set_defaults(func=cmd_current_set, facade_command="current.set")

    p = current_sub.add_parser("clear", help="Clear current task through taskctl.py")
    p.set_defaults(func=cmd_current_clear, facade_command="current.clear")

    epic = sub.add_parser("epic", help="Epic facade commands")
    epic_sub = epic.add_subparsers(dest="epic_action", required=True)

    p = epic_sub.add_parser("list", help="List epics through planctl.py")
    p.add_argument("--initiative")
    p.set_defaults(func=cmd_epic_list, facade_command="epic.list")

    context = sub.add_parser("context", help="Context facade commands")
    context_sub = context.add_subparsers(dest="context_action", required=True)

    p = context_sub.add_parser("build", help="Build a Context Pack through contextctl.py")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--task")
    group.add_argument("--query")
    p.add_argument("--write", action="store_true")
    p.add_argument("--limit", type=int)
    p.set_defaults(func=cmd_context_build, facade_command="context.build")

    codex = sub.add_parser("codex", help="Codex prompt package facade commands")
    codex_sub = codex.add_subparsers(dest="codex_action", required=True)
    prompt = codex_sub.add_parser("prompt", help="Codex prompt commands")
    prompt_sub = prompt.add_subparsers(dest="prompt_action", required=True)

    p = prompt_sub.add_parser("build", help="Build a Codex prompt package through codexctl.py")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--task")
    group.add_argument("--change")
    p.add_argument("--with-context", action="store_true")
    p.add_argument("--context-pack")
    p.set_defaults(func=cmd_codex_prompt_build, facade_command="codex.prompt.build")

    docs = sub.add_parser("docs", help="Documentation-control facade commands")
    docs_sub = docs.add_subparsers(dest="docs_action", required=True)

    p = docs_sub.add_parser("render", help="Render documentation generated views through docctl.py")
    p.set_defaults(func=cmd_docs_render, facade_command="docs.render")

    project = sub.add_parser("project", help="Project-level facade commands")
    project_sub = project.add_subparsers(dest="project_action", required=True)

    p = project_sub.add_parser("doctor", help="Run project-control health checks")
    _add_project_doctor_flags(p)
    p.set_defaults(func=cmd_project_doctor, facade_command="project.doctor")

    p = project_sub.add_parser("protected-check", help="Run protected project-control file checks")
    p.set_defaults(func=cmd_project_protected_check, facade_command="project.protected_check")

    p = project_sub.add_parser("render", help="Render generated project-control views")
    p.set_defaults(func=cmd_project_render, facade_command="project.render")

    web = sub.add_parser("web", help="Run the local Web Control Center")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=8765)
    web.set_defaults(func=cmd_web, facade_command="web.serve")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    filtered_argv, json_output = _extract_json_flag(raw_argv)
    parser = build_parser()
    args = parser.parse_args(filtered_argv)
    args.json = bool(json_output or getattr(args, "json", False))

    try:
        return args.func(args)
    except RegistryError as exc:
        error = FacadeError(exc.code, exc.message, details=exc.details)
    except CommandError as exc:
        error = exc

    if args.json:
        command_name = getattr(args, "facade_command", getattr(args, "domain", "aictl"))
        domain = getattr(args, "domain", "aictl")
        _print_json(_command_error_result(command_name, domain, error).to_dict())
    else:
        print("ERROR: {}: {}".format(error.code, error.message), file=sys.stderr)
    return 1

if __name__ == "__main__":
    raise SystemExit(main())

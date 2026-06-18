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


def cmd_project_doctor(args: argparse.Namespace) -> int:
    _ensure_implemented("project.doctor")
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
    if args.json:
        command_args.append("--json")
    else:
        command_args.append("--verbose")
    return _run_delegated(
        "project.doctor",
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

    p = task_sub.add_parser("transition", help="Transition a task through taskctl.py")
    p.add_argument("task_ref")
    p.add_argument("--to", required=True)
    p.set_defaults(func=cmd_task_transition, facade_command="task.transition")

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

    project = sub.add_parser("project", help="Project-level facade commands")
    project_sub = project.add_subparsers(dest="project_action", required=True)

    p = project_sub.add_parser("doctor", help="Run project-control health checks")
    _add_project_doctor_flags(p)
    p.set_defaults(func=cmd_project_doctor, facade_command="project.doctor")

    p = project_sub.add_parser("render", help="Render generated project-control views")
    p.set_defaults(func=cmd_project_render, facade_command="project.render")

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

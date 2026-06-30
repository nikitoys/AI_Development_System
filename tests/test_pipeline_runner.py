import importlib.util
import hashlib
import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from ai_project_ctl.core.result import CommandMessage, CommandResult
import ai_project_ctl.pipeline.runner as runner_module
from ai_project_ctl.pipeline import (
    BatchPolicy,
    CodexAdapterMode,
    CodexExecutionMode,
    policy_preset,
)
from ai_project_ctl.pipeline.batch import run_until_blocker
from ai_project_ctl.pipeline.close_phase import close_phase
from ai_project_ctl.pipeline.codex_adapter import (
    CODE_REPORT_MISSING as CODEX_ADAPTER_REPORT_MISSING,
    CodexAdapterResult,
)
from ai_project_ctl.pipeline.codex_review import CodexReviewResult, VERDICT_APPROVE
from ai_project_ctl.pipeline.git_commit import (
    CODE_READY as COMMIT_READINESS_PASS,
    CODE_REPORT_NOT_PASS as COMMIT_REPORT_NOT_PASS,
    REQUIRED_MACHINE_CHECKS,
    evaluate_commit_readiness,
    run_local_commit,
)
from ai_project_ctl.pipeline.machine_review import (
    MachineCheckEvidence,
    MachineReviewResult,
)
from ai_project_ctl.pipeline.audit import pipeline_audit_path
from ai_project_ctl.pipeline.phase import PhaseResult
from ai_project_ctl.pipeline.report_gate import CODE_WARN as CODEX_REPORT_WARN
from ai_project_ctl.pipeline.report_gate import ReportGateResult
from ai_project_ctl.pipeline.runner import run_next
from ai_project_ctl.pipeline.session import create_session, record_phase_result
from ai_project_ctl.pipeline.state import (
    pipeline_events_path,
    pipeline_state_path,
    pipeline_status_path,
)
from ai_project_ctl.pipeline.verify_phase import (
    GIT_DIFF_GATES_POLICY_KEY,
    REPORT_WARNING_POLICY_KEY,
    SKIPPED_GATES_KEY,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
AICTL_PATH = REPO_ROOT / "scripts" / "aictl.py"


def completed(stdout="OK\n", returncode=0, stderr=""):
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def load_aictl_for_test():
    spec = importlib.util.spec_from_file_location("aictl_pipeline_runner_test_module", AICTL_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_aictl_json(aictl, argv):
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = aictl.main(argv)
    return code, json.loads(stdout.getvalue()), stderr.getvalue()


def write_ui_settings(root: Path, *, default_policy: str) -> None:
    config_dir = root / "AI_PROJECT" / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "ui_settings.json").write_text(
        json.dumps({"default_policy": default_policy}),
        encoding="utf-8",
    )


def write_project_state(root: Path, *, change_status: str | None = "approved") -> None:
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True)
    (state_dir / "plan.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "initiatives": [{"id": "INIT-001", "status": "active"}],
                "epics": [
                    {
                        "id": "EPIC-001",
                        "initiative_id": "INIT-001",
                        "status": "planned",
                        "key": "APP",
                        "order": 1,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (state_dir / "tasks.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "current_task_id": None,
                "tasks": [
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "uid": "uid_task_001",
                        "legacy_id": "TASK-001",
                        "aliases": ["TASK-001"],
                        "title": "Runnable task",
                        "status": "ready",
                        "epic_id": "EPIC-001",
                        "priority": 1,
                        "order": 1,
                        "local_seq": 1,
                        "depends_on": [],
                        "allowed_files": [
                            "ai_project_ctl/pipeline/report_gate.py",
                            "tests/**",
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    changes = []
    if change_status:
        changes.append(
            {
                "id": "CHG-001",
                "status": change_status,
                "linked_tasks": ["TASK-001"],
            }
        )
    (state_dir / "evolution.json").write_text(
        json.dumps({"schema_version": 1, "revision": 1, "changes": changes}),
        encoding="utf-8",
    )


def write_multi_task_project_state(
    root: Path,
    *,
    task_count: int = 5,
    task_status: str = "ready",
) -> None:
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True)
    (state_dir / "plan.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "initiatives": [{"id": "INIT-001", "status": "active"}],
                "epics": [
                    {
                        "id": "EPIC-001",
                        "initiative_id": "INIT-001",
                        "status": "planned",
                        "key": "APP",
                        "order": 1,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    tasks = []
    for index in range(1, task_count + 1):
        task_id = "TASK-{0:03d}".format(index)
        tasks.append(
            {
                "id": task_id,
                "ref": "APP-{0:02d}".format(index),
                "uid": "uid_task_{0:03d}".format(index),
                "legacy_id": task_id,
                "aliases": [task_id],
                "title": "Runnable task {}".format(index),
                "summary": "Prepare task {}".format(index),
                "description": "Task {} needs a linked Change.".format(index),
                "scope": ["Implement task {}".format(index)],
                "out_of_scope": ["Do not approve Evolution Changes."],
                "acceptance_criteria": ["Created Change is linked."],
                "review_instructions": ["Check owner approval remains separate."],
                "status": task_status,
                "epic_id": "EPIC-001",
                "priority": 1,
                "order": index,
                "local_seq": index,
                "depends_on": [],
                "allowed_files": [
                    "ai_project_ctl/pipeline/runner.py",
                    "tests/test_pipeline_runner.py",
                ],
            }
        )
    (state_dir / "tasks.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "current_task_id": None,
                "tasks": tasks,
            }
        ),
        encoding="utf-8",
    )
    (state_dir / "evolution.json").write_text(
        json.dumps({"schema_version": 1, "revision": 1, "changes": []}),
        encoding="utf-8",
    )


def successful_workflow_runner(
    calls,
    *,
    root: Path | None = None,
    prompt_text: str = "Source ID: TASK-001\n\nSmall prompt.",
    report_on_local_codex: bool = False,
):
    def fake_run(argv):
        calls.append(list(argv))
        if list(argv) == ["codex", "exec"]:
            if root is not None and report_on_local_codex:
                write_report_state(root, "TASK-001", "RPT-001")
            return completed(stdout="codex adapter finished\n")
        if Path(argv[1]).name == "taskctl.py" and "resolve" in argv:
            return completed(
                json.dumps(
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "status": "ready",
                    }
                )
                + "\n"
            )
        if root is not None and "codex" in argv and "build" in argv:
            prompt = root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"
            prompt.parent.mkdir(parents=True, exist_ok=True)
            prompt.write_text(prompt_text, encoding="utf-8")
        return completed('{"ok": true}\n')

    return fake_run


def codex_stdout_for_report(report: dict) -> str:
    return "Codex finished.\nCODEX_REPORT_JSON:\n```json\n{}\n```\n".format(
        json.dumps(report, indent=2, sort_keys=True)
    )


def emitted_codex_report(
    task_id: str = "TASK-001",
    task_ref: str = "APP-01",
) -> dict:
    return {
        "schema_version": 1,
        "task_id": task_id,
        "task_ref": task_ref,
        "implementation_summary": "Implemented the selected task.",
        "changed_files": [],
        "generated_files": [],
        "checks": [
            {
                "name": "unit",
                "command": "python -m unittest tests.test_pipeline_runner",
                "result": "pass",
                "duration_sec": 0.1,
                "blocking": True,
                "details": "",
            }
        ],
        "warnings": [],
        "blockers": [],
        "notes": [],
        "owner_decision_required": False,
        "token_usage": {
            "prompt_tokens": 100,
            "context_tokens": 20,
            "completion_tokens": 10,
            "output_tokens": 5,
            "total_tokens": 135,
            "remaining_tokens": 1000,
            "model_context_limit": 2000,
            "max_context_tokens": 1500,
            "reserved_output_tokens": 200,
            "min_remaining_tokens": 100,
            "token_count_strategy": "test_fixture",
            "token_count_estimated": True,
            "token_count_unavailable": False,
            "token_count_unavailable_reason": "",
        },
    }


def structured_report_workflow_runner(
    calls,
    *,
    root: Path,
    codex_stdout: str,
    prompt_text: str = "Source ID: TASK-001\n\nSmall prompt.",
):
    def fake_run(argv):
        args = list(argv)
        calls.append(args)
        script = Path(args[1]).name if len(args) > 1 else ""
        if script == "taskctl.py" and "resolve" in args:
            return completed(
                json.dumps(
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "status": "ready",
                    }
                )
                + "\n"
            )
        if "codex" in args and "build" in args:
            prompt = root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"
            prompt.parent.mkdir(parents=True, exist_ok=True)
            prompt.write_text(prompt_text, encoding="utf-8")
        if args == ["codex", "exec"]:
            return completed(stdout=codex_stdout)
        return completed('{"ok": true}\n')

    return fake_run


def auto_create_change_runner(calls, *, root: Path, allow_approval: bool = False):
    def fake_run(argv):
        args = list(argv)
        calls.append(args)
        script = Path(args[1]).name if len(args) > 1 else ""
        if script == "taskctl.py" and "resolve" in args:
            task_ref = args[args.index("resolve") + 1]
            task = _task_by_ref(root, task_ref)
            return completed(
                json.dumps(
                    {
                        "id": task["id"],
                        "ref": task.get("ref") or task["id"],
                        "status": task["status"],
                    }
                )
                + "\n"
            )
        if script == "taskctl.py":
            return completed("OK\n")
        if script == "evolutionctl.py":
            change_command = (
                args[args.index("change") + 1]
                if "change" in args and args.index("change") + 1 < len(args)
                else ""
            )
            if change_command in {"approve", "accept"}:
                if change_command == "accept" or not allow_approval:
                    raise AssertionError("pipeline must not approve or accept changes")
                change_id = args[args.index("approve") + 1]
                _update_change(root, change_id, status="approved")
                return completed("OK: change.approve revision 1 -> 2\n")
            if args[-1] == "validate":
                return completed("OK: evolution is valid\n")
            if args[-1] == "check-generated":
                return completed("OK: generated evolution file is up to date\n")
            if "create" in args:
                change_id = _append_change(root)
                return completed(
                    "OK: change.create revision 1 -> 2\nCreated: {}\n".format(change_id)
                )
            if "link-task" in args:
                change_id = args[args.index("link-task") + 1]
                task_id = args[args.index("--task") + 1]
                _update_change(root, change_id, linked_task=task_id)
                return completed("OK\n")
            if "transition" in args and "--to" in args:
                change_id = args[args.index("transition") + 1]
                _update_change(root, change_id, status=args[args.index("--to") + 1])
                return completed("OK\n")
            if any(command in args for command in ("add-affected-file", "add-risk", "add-impact")):
                return completed("OK\n")
        if script == "aictl.py":
            return completed('{"ok": true}\n')
        raise AssertionError("unexpected command: {}".format(args))

    return fake_run


def _task_by_ref(root: Path, task_ref: str) -> dict:
    state = json.loads((root / "AI_PROJECT" / "state" / "tasks.json").read_text(encoding="utf-8"))
    for task in state["tasks"]:
        refs = {task.get("id"), task.get("ref"), task.get("uid"), task.get("legacy_id")}
        refs.update(task.get("aliases") or [])
        if task_ref in refs:
            return task
    raise AssertionError("missing task ref: {}".format(task_ref))


def _append_change(root: Path) -> str:
    path = root / "AI_PROJECT" / "state" / "evolution.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    change_id = "CHG-{0:03d}".format(len(state.get("changes", [])) + 1)
    state.setdefault("changes", []).append(
        {
            "id": change_id,
            "status": "draft",
            "title": "Generated Change {}".format(change_id),
            "linked_tasks": [],
        }
    )
    state["revision"] = int(state.get("revision", 0)) + 1
    path.write_text(json.dumps(state), encoding="utf-8")
    return change_id


def _update_change(root: Path, change_id: str, *, linked_task: str = "", status: str = "") -> None:
    path = root / "AI_PROJECT" / "state" / "evolution.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    for change in state.get("changes", []):
        if change.get("id") != change_id:
            continue
        if linked_task and linked_task not in change.setdefault("linked_tasks", []):
            change["linked_tasks"].append(linked_task)
        if status:
            change["status"] = status
    state["revision"] = int(state.get("revision", 0)) + 1
    path.write_text(json.dumps(state), encoding="utf-8")


def stateful_workflow_runner(
    calls,
    *,
    root: Path,
    prompt_text: str = "Source ID: TASK-001\n\nSmall prompt.",
):
    task_status = {"value": "ready"}

    def fake_run(argv):
        args = list(argv)
        calls.append(args)
        if args == ["codex", "exec"]:
            write_report_state(root, "TASK-001", "RPT-001")
            return completed(stdout="codex adapter finished\n")
        if len(args) > 1 and Path(args[1]).name == "taskctl.py" and "resolve" in args:
            return completed(
                json.dumps(
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "status": task_status["value"],
                    }
                )
                + "\n"
            )
        if "codex" in args and "build" in args:
            prompt = root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"
            prompt.parent.mkdir(parents=True, exist_ok=True)
            prompt.write_text(prompt_text, encoding="utf-8")
        if "task" in args and "transition" in args and "TASK-001" in args and "--to" in args:
            task_status["value"] = args[args.index("--to") + 1]
        return completed('{"ok": true}\n')

    return fake_run, task_status


def committing_workflow_runner(
    calls,
    *,
    root: Path,
    prompt_text: str = "Source ID: TASK-001\n\nSmall prompt.",
    git_status_stdout: str = " M ai_project_ctl/pipeline/report_gate.py\n",
):
    task_status = {"value": "ready"}

    def fake_run(argv):
        args = list(argv)
        if args and args[0] == "git":
            calls.append(args)
            if args == ["git", "status", "--short", "--untracked-files=all"]:
                return completed(stdout=git_status_stdout)
            if args[:3] == ["git", "add", "--"]:
                return completed(stdout="")
            if args[:3] == ["git", "commit", "-m"]:
                return completed(stdout="[main abc1234] pipeline commit\n")
            if args == ["git", "rev-parse", "--verify", "HEAD"]:
                return completed(stdout="abc1234deadbeef\n")
            return completed(returncode=1, stderr="unexpected git command\n")

        calls.append(args)
        if args == ["codex", "exec"]:
            write_report_state(root, "TASK-001", "RPT-001")
            return completed(stdout="codex adapter finished\n")
        if len(args) > 1 and Path(args[1]).name == "taskctl.py" and "resolve" in args:
            return completed(
                json.dumps(
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "status": task_status["value"],
                    }
                )
                + "\n"
            )
        if "codex" in args and "build" in args:
            prompt = root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"
            prompt.parent.mkdir(parents=True, exist_ok=True)
            prompt.write_text(prompt_text, encoding="utf-8")
        if "task" in args and "transition" in args and "TASK-001" in args and "--to" in args:
            task_status["value"] = args[args.index("--to") + 1]
            _write_task_status(root, task_status["value"])
        return completed('{"ok": true}\n')

    return fake_run


def _write_task_status(root: Path, status: str) -> None:
    path = root / "AI_PROJECT" / "state" / "tasks.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    for task in state["tasks"]:
        if task.get("id") == "TASK-001":
            task["status"] = status
    path.write_text(json.dumps(state), encoding="utf-8")


def valid_report(task_id: str) -> dict:
    return {
        "schema_version": 1,
        "task_id": task_id,
        "task_ref": "APP-01",
        "reported_task_id": task_id,
        "reported_task_ref": "APP-01",
        "implementation_summary": "Implemented the selected task.",
        "changed_files": ["ai_project_ctl/pipeline/report_gate.py"],
        "generated_files": ["AI_PROJECT/generated/PIPELINE_STATUS.md"],
        "checks": [
            {
                "name": "unit",
                "command": "python -m unittest tests.test_pipeline_runner",
                "result": "pass",
                "duration_sec": 0.1,
                "blocking": True,
                "details": "",
            }
        ],
        "warnings": [],
        "blockers": [],
        "notes": [],
        "owner_decision_required": False,
        "token_usage": {
            "prompt_tokens": 100,
            "context_tokens": 20,
            "remaining_tokens": 1000,
            "token_count_strategy": "local_byte_estimate",
            "token_count_estimated": True,
            "token_count_unavailable": False,
        },
    }


def valid_review_output(verdict="APPROVE", findings=None) -> str:
    return json.dumps(
        {
            "verdict": verdict,
            "summary": "Semantic review completed.",
            "evidence": {
                "task_id": "TASK-001",
                "report_id": "RPT-001",
                "report_gate_status": "pass",
                "machine_review_status": "pass",
            },
            "findings": list(findings or []),
            "risks": [],
        }
    )


def warning_report_gate() -> ReportGateResult:
    return ReportGateResult(
        status="warn",
        code=CODEX_REPORT_WARN,
        reason="Report contains advisory warning(s).",
        report_id="RPT-001",
        task_id="TASK-001",
        changed_files=("ai_project_ctl/pipeline/report_gate.py",),
    )


def blocking_report_gate(status: str) -> ReportGateResult:
    return ReportGateResult(
        status=status,
        code="CODEX_REPORT_{}".format(status.upper()),
        reason="Report gate {} should block local commit.".format(status),
        report_id="RPT-001",
        task_id="TASK-001",
        changed_files=("ai_project_ctl/pipeline/report_gate.py",),
    )


def passing_report_gate(
    *,
    changed_files=("ai_project_ctl/pipeline/report_gate.py",),
    generated_files=(),
) -> ReportGateResult:
    return ReportGateResult(
        status="pass",
        code="CODEX_REPORT_PASS",
        reason="Report gate passed.",
        report_id="RPT-001",
        task_id="TASK-001",
        changed_files=tuple(changed_files),
        generated_files=tuple(generated_files),
    )


def governed_side_effect(
    *,
    changed_files=(),
    generated_files=(),
) -> CommandResult:
    result = CommandResult.success(
        command="test.governed_side_effect",
        domain="test",
        message="governed side effect",
    )
    result.changed_files.extend(str(path) for path in changed_files)
    result.generated_files.extend(str(path) for path in generated_files)
    return result


def passing_machine_review() -> MachineReviewResult:
    return MachineReviewResult(
        status="pass",
        code="MACHINE_REVIEW_PASS",
        reason="Machine Review passed.",
        task_id="TASK-001",
        report_id="RPT-001",
        checks=tuple(
            MachineCheckEvidence(
                name=name,
                status="pass",
                code="MACHINE_REVIEW_PASS",
                reason="{} passed.".format(name),
            )
            for name in sorted(REQUIRED_MACHINE_CHECKS)
        ),
    )


def approved_codex_review() -> CodexReviewResult:
    return CodexReviewResult(
        status="pass",
        code="CODEX_REVIEW_APPROVE",
        reason="Codex Review approved the task.",
        verdict=VERDICT_APPROVE,
        task_id="TASK-001",
        report_id="RPT-001",
        review_id="REV-001",
        prompt_sha256="sha256",
        prompt_bytes=1,
    )


def write_report_state(root: Path, task_id: str, report_id: str, report: dict | None = None) -> None:
    report_data = report or valid_report(task_id)
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "task_reports.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "created_at": "2026-06-19T00:00:00Z",
                "updated_at": "2026-06-19T00:00:00Z",
                "latest_by_task": {task_id: report_id},
                "reports": [
                    {
                        "id": report_id,
                        "task_id": task_id,
                        "task_ref": "APP-01",
                        "submitted_at": "2026-06-19T00:00:00Z",
                        "submitted_by": "tester",
                        "source_file": "/tmp/report.json",
                        "report": report_data,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def record_collected_report(root: Path, session_id: str, report_id: str = "RPT-001") -> None:
    result = record_phase_result(
        session_id,
        PhaseResult.passed(
            "collect_report",
            reason="Structured execution report collected for selected task.",
            next_action="Run pipeline phase verify.",
            artifacts={
                "session_id": session_id,
                "task_id": "TASK-001",
                "report_id": report_id,
                "report_found": True,
                "freshness_basis": "report_id",
            },
        ),
        root=root,
        actor="tester",
        task_id="TASK-001",
        command="pipeline.phase.collect_report",
    )
    if not result.ok:
        raise AssertionError(result.errors)


def force_auto_close_policy_note(root: Path, owner_note: str) -> None:
    state_path = pipeline_state_path(root)
    state = json.loads(state_path.read_text(encoding="utf-8"))
    policy = state["sessions"][0]["policy_snapshot"]
    policy["name"] = "supervised_autoclose"
    closure = policy["closure"]
    closure["auto_close_task"] = True
    closure["owner_approval_note"] = owner_note
    state_path.write_text(json.dumps(state), encoding="utf-8")


def record_close_ready_phase_history(
    root: Path,
    session_id: str,
    *,
    report_id: str = "RPT-001",
) -> None:
    phase_specs = (
        ("prepare", "Task prepared for close preflight."),
        ("execute", "Execution phase evidence recorded for close preflight."),
        ("collect_report", "Structured report collected for close preflight."),
        ("verify", "Machine verification passed for close preflight."),
    )
    for phase_name, reason in phase_specs:
        result = record_phase_result(
            session_id,
            PhaseResult.passed(
                phase_name,
                reason=reason,
                next_action="Continue close preflight.",
                artifacts={
                    "session_id": session_id,
                    "task_id": "TASK-001",
                    "task_ref": "APP-01",
                    "report_id": report_id,
                },
            ),
            root=root,
            actor="tester",
            task_id="TASK-001",
            command="pipeline.phase.{}".format(phase_name),
        )
        if not result.ok:
            raise AssertionError(result.errors)

    result = record_phase_result(
        session_id,
        PhaseResult.passed(
            "review",
            reason="Codex Review approved the selected task.",
            next_action="Close reviewed task.",
            artifacts={
                "session_id": session_id,
                "task_id": "TASK-001",
                "task_ref": "APP-01",
                "report_id": report_id,
                "review_id": "REV-001",
                "review_status": "pass",
                "review_code": "CODEX_REVIEW_APPROVE",
                "review_reason": "Reviewer approved the task.",
                "verdict": "APPROVE",
            },
        ),
        root=root,
        actor="tester",
        task_id="TASK-001",
        command="pipeline.phase.review",
    )
    if not result.ok:
        raise AssertionError(result.errors)


def load_pipeline(root: Path):
    return json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))


def pipeline_bookkeeping_snapshot(root: Path) -> dict[str, str]:
    paths = {
        "state": pipeline_state_path(root),
        "events": pipeline_events_path(root),
        "status": pipeline_status_path(root),
        "audit": pipeline_audit_path(root),
    }
    return {name: path.read_text(encoding="utf-8") for name, path in paths.items()}


class PipelineRunnerTests(unittest.TestCase):
    def test_run_next_dispatch_result_exposes_close_commit_blocked_status(self):
        close_status = {
            "outcome": "done_but_commit_blocked",
            "task_closed": True,
            "task_status": "done",
            "commit_status": "blocked",
            "commit_code": "COMMIT_READINESS_FAILED",
            "commit_hash": "",
            "commit_readiness_status": "blocked",
            "commit_readiness_code": "COMMIT_MACHINE_REVIEW_NOT_PASS",
            "owner_next_action": (
                "Task is done, but local commit is blocked by commit readiness."
            ),
        }
        phase_result = {
            "phase": "close",
            "status": "blocked",
            "reason": (
                "Close completed, but local commit was blocked: Machine Review "
                "WARN is not accepted for local commit."
            ),
            "next_action": close_status["owner_next_action"],
            "artifacts": {
                "blocked_by": "COMMIT_READINESS_FAILED",
                "close_status": close_status,
                "local_commit": {
                    "status": "blocked",
                    "code": "COMMIT_READINESS_FAILED",
                },
            },
            "changed_files": [],
            "generated_files": [],
            "events": [],
        }
        delegated = CommandResult.success(
            command="pipeline.phase.close",
            domain="pipeline",
            message=phase_result["reason"],
            data={"phase_result": phase_result},
        )

        result = runner_module._phase_dispatch_result(
            delegated,
            phase_name="close",
            session={"id": "PSESS-001", "current_task_id": "TASK-001"},
            effects=(delegated,),
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.data["stop_code"], "COMMIT_READINESS_FAILED")
        self.assertEqual(result.data["close_status"], close_status)
        self.assertEqual(result.data["close_outcome"], "done_but_commit_blocked")
        self.assertEqual(result.data["commit_status"], "blocked")
        self.assertEqual(
            result.next_actions,
            [close_status["owner_next_action"]],
        )

    def test_dry_run_records_selected_task_and_stops_without_prepare(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root)
            session = create_session(
                root=root,
                actor="tester",
                policy_name="dry_run",
                task_refs=("APP-01",),
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=successful_workflow_runner(calls),
            )
            state = load_pipeline(root)
            latest = state["sessions"][0]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertEqual(result.data["selected_task"]["id"], "TASK-001")
            self.assertEqual(calls, [])
            self.assertEqual(latest["steps"][0]["status"], "stopped")
            self.assertEqual(latest["steps"][0]["gate_outcomes"][0]["name"], "codex_execution_policy")

    def test_autoclose_session_creation_requires_owner_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")

            result = create_session(
                root=root,
                actor="tester",
                policy_name="supervised_autoclose",
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.message, "PIPELINE_AUTO_CLOSE_OWNER_NOTE_REQUIRED")
            self.assertEqual(len(result.errors), 1)
            error = result.errors[0]
            self.assertEqual(error.code, "PIPELINE_AUTO_CLOSE_OWNER_NOTE_REQUIRED")
            self.assertEqual(error.path, "closure.owner_approval_note")
            self.assertEqual(error.details["policy"], "supervised_autoclose")
            self.assertTrue(error.details["auto_close_task"])
            self.assertFalse(error.details["owner_approval_note_present"])
            self.assertEqual(error.details["required_argument"], "auto_close_note")
            self.assertIn("--auto-close-note", error.details["next_action"])
            self.assertEqual(result.next_actions, [error.details["next_action"]])
            self.assertFalse(pipeline_state_path(root).exists())

            allowed = create_session(root=root, actor="tester", policy_name="supervised")
            self.assertTrue(allowed.ok)
            closure = load_pipeline(root)["sessions"][0]["policy_snapshot"]["closure"]
            self.assertFalse(closure["auto_close_task"])
            self.assertEqual(closure["owner_approval_note"], "")

    def test_autoclose_session_creation_stores_owner_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            note = "Owner approved auto-close for this test session."

            result = create_session(
                root=root,
                actor="tester",
                policy_name="supervised_autoclose",
                auto_close_note=note,
            )

            self.assertTrue(result.ok)
            state = load_pipeline(root)
            closure = state["sessions"][0]["policy_snapshot"]["closure"]
            self.assertTrue(closure["auto_close_task"])
            self.assertEqual(closure["owner_approval_note"], note)

    def test_close_phase_blocks_with_owner_notes_required_when_note_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status=None)
            session = create_session(
                root=root,
                actor="tester",
                policy_name="supervised",
                current_task_id="TASK-001",
                current_task_ref="APP-01",
            )
            self.assertTrue(session.ok)
            force_auto_close_policy_note(root, "")
            record_close_ready_phase_history(root, session.data["session_id"])

            with patch(
                "ai_project_ctl.pipeline.close_phase.run_review_close_workflow",
                side_effect=AssertionError("close workflow must not run without owner note"),
            ):
                result = close_phase(
                    session.data["session_id"],
                    root=root,
                    actor="tester",
                    confirmed=True,
                )

            latest_phase = load_pipeline(root)["sessions"][0]["phase_history"][-1]
            artifacts = latest_phase["artifacts"]

            self.assertTrue(result.ok)
            self.assertEqual(latest_phase["phase"], "close")
            self.assertEqual(latest_phase["status"], "blocked")
            self.assertTrue(artifacts["preflight_passed"])
            self.assertEqual(artifacts["missing_gates"], [])
            self.assertEqual(artifacts["blocked_by"], "CLOSE_OWNER_NOTES_REQUIRED")
            self.assertFalse(artifacts["close_policy"]["owner_approval_note_present"])

    def test_close_phase_reaches_close_workflow_when_owner_note_is_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status=None)
            session = create_session(
                root=root,
                actor="tester",
                policy_name="supervised",
                current_task_id="TASK-001",
                current_task_ref="APP-01",
            )
            self.assertTrue(session.ok)
            note = "Owner approved auto-close for this close phase regression."
            force_auto_close_policy_note(root, note)
            record_close_ready_phase_history(root, session.data["session_id"])
            workflow = CommandResult.success(
                command="pipeline.review_close_policy",
                domain="pipeline",
                message="Task close workflow reached.",
                data={"decision": {"action": "close_task"}, "workflows": []},
            )

            with patch(
                "ai_project_ctl.pipeline.close_phase.run_review_close_workflow",
                return_value=workflow,
            ) as close_workflow:
                result = close_phase(
                    session.data["session_id"],
                    root=root,
                    actor="tester",
                    confirmed=True,
                )

            latest_phase = load_pipeline(root)["sessions"][0]["phase_history"][-1]
            artifacts = latest_phase["artifacts"]

            self.assertTrue(result.ok)
            self.assertEqual(latest_phase["phase"], "close")
            self.assertEqual(latest_phase["status"], "passed")
            self.assertTrue(artifacts["preflight_passed"])
            self.assertEqual(artifacts["missing_gates"], [])
            self.assertNotEqual(artifacts.get("blocked_by"), "CLOSE_OWNER_NOTES_REQUIRED")
            self.assertTrue(artifacts["close_policy"]["owner_approval_note_present"])
            self.assertEqual(
                artifacts["close_workflow"]["message"],
                "Task close workflow reached.",
            )
            close_workflow.assert_called_once()

    def test_ui_run_autoclose_requires_owner_note_before_session_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            write_ui_settings(root, default_policy="supervised_executable_autoclose")
            aictl = load_aictl_for_test()

            with patch.object(
                aictl,
                "run_codex_preflight",
                side_effect=AssertionError("ui run must not run Codex preflight"),
            ), patch.object(
                aictl,
                "run_pipeline_until_blocker",
                side_effect=AssertionError("ui run must not start execution"),
            ):
                code, payload, _stderr = run_aictl_json(
                    aictl,
                    [
                        "--root",
                        str(root),
                        "--actor",
                        "tester",
                        "--json",
                        "ui",
                        "run",
                        "APP-01",
                        "--confirm",
                        "--preflight",
                    ],
                )

            self.assertEqual(code, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["data"]["policy"], "supervised_executable_autoclose")
            self.assertEqual(
                payload["errors"][0]["code"],
                "PIPELINE_AUTO_CLOSE_OWNER_NOTE_REQUIRED",
            )
            self.assertFalse(pipeline_state_path(root).exists())

    def test_ui_run_autoclose_stores_owner_note_in_created_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            write_ui_settings(root, default_policy="supervised_autoclose")
            aictl = load_aictl_for_test()
            note = "Owner approved auto-close for this UI run."

            code, payload, _stderr = run_aictl_json(
                aictl,
                [
                    "--root",
                    str(root),
                    "--actor",
                    "tester",
                    "--json",
                    "ui",
                    "run",
                    "APP-01",
                    "--auto-close-note",
                    note,
                ],
            )

            self.assertEqual(code, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["errors"][0]["code"], "UI_RUN_CONFIRMATION_REQUIRED")
            self.assertEqual(payload["data"]["session_id"], "PSESS-001")
            closure = load_pipeline(root)["sessions"][0]["policy_snapshot"]["closure"]
            self.assertTrue(closure["auto_close_task"])
            self.assertEqual(closure["owner_approval_note"], note)

    def test_ui_run_non_autoclose_policy_still_allows_missing_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            write_ui_settings(root, default_policy="supervised")
            aictl = load_aictl_for_test()

            code, payload, _stderr = run_aictl_json(
                aictl,
                [
                    "--root",
                    str(root),
                    "--actor",
                    "tester",
                    "--json",
                    "ui",
                    "run",
                    "APP-01",
                ],
            )

            self.assertEqual(code, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["errors"][0]["code"], "UI_RUN_CONFIRMATION_REQUIRED")
            self.assertEqual(payload["data"]["session_id"], "PSESS-001")
            closure = load_pipeline(root)["sessions"][0]["policy_snapshot"]["closure"]
            self.assertFalse(closure["auto_close_task"])
            self.assertEqual(closure["owner_approval_note"], "")

    def test_supervised_blocks_when_approved_change_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status=None)
            session = create_session(root=root, actor="tester", policy_name="supervised")
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=successful_workflow_runner(calls),
            )
            state = load_pipeline(root)

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertIn("Approved linked Evolution Change", result.data["stop_reason"])
            self.assertEqual(calls, [])
            self.assertEqual(state["sessions"][0]["status"], "blocked")
            self.assertEqual(state["sessions"][0]["steps"][0]["gate_outcomes"][0]["name"], "evolution_change_gate")

    def test_auto_create_missing_change_creates_linked_change_and_blocks_for_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status=None)
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="auto_create_missing_change",
                evolution=replace(supervised.evolution, create_missing_change=True),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                task_refs=("APP-01",),
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=auto_create_change_runner(calls, root=root),
            )
            state = load_pipeline(root)
            latest = state["sessions"][0]
            changes = json.loads(
                (root / "AI_PROJECT" / "state" / "evolution.json").read_text(
                    encoding="utf-8"
                )
            )["changes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertIn("Human Owner approval", result.data["stop_reason"])
            self.assertEqual(changes[0]["id"], "CHG-001")
            self.assertEqual(changes[0]["status"], "ready")
            self.assertEqual(changes[0]["linked_tasks"], ["TASK-001"])
            self.assertEqual(latest["linked_change_ids"], ["CHG-001"])
            change_gate = latest["steps"][0]["gate_outcomes"][0]["details"]["change_gate"]
            self.assertEqual(change_gate["created_change_ids"], ["CHG-001"])
            self.assertEqual(change_gate["tasks_requiring_approval"], ["TASK-001"])
            command_texts = [" ".join(call) for call in calls]
            self.assertFalse(any(" change approve " in text for text in command_texts))
            self.assertFalse(any(" change accept " in text for text in command_texts))

    def test_auto_create_missing_changes_preflights_multiple_selected_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_multi_task_project_state(root, task_count=5)
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="auto_create_missing_changes",
                evolution=replace(supervised.evolution, create_missing_change=True),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                task_refs=("APP-01", "APP-02", "APP-03", "APP-04", "APP-05"),
                max_tasks=5,
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=auto_create_change_runner(calls, root=root),
            )
            state = load_pipeline(root)
            latest = state["sessions"][0]
            changes = json.loads(
                (root / "AI_PROJECT" / "state" / "evolution.json").read_text(
                    encoding="utf-8"
                )
            )["changes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertEqual(
                [change["id"] for change in changes],
                ["CHG-001", "CHG-002", "CHG-003", "CHG-004", "CHG-005"],
            )
            self.assertEqual(
                [change["linked_tasks"] for change in changes],
                [["TASK-001"], ["TASK-002"], ["TASK-003"], ["TASK-004"], ["TASK-005"]],
            )
            self.assertEqual(
                latest["linked_change_ids"],
                ["CHG-001", "CHG-002", "CHG-003", "CHG-004", "CHG-005"],
            )
            change_gate = latest["steps"][0]["gate_outcomes"][0]["details"]["change_gate"]
            self.assertEqual(
                change_gate["created_change_ids"],
                ["CHG-001", "CHG-002", "CHG-003", "CHG-004", "CHG-005"],
            )
            self.assertEqual(
                change_gate["tasks_requiring_approval"],
                ["TASK-001", "TASK-002", "TASK-003", "TASK-004", "TASK-005"],
            )
            self.assertFalse(any("codexctl.py" in " ".join(call) for call in calls))

    def test_auto_create_missing_changes_preflights_blocked_selected_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_multi_task_project_state(root, task_count=2, task_status="planned")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="auto_create_blocked_selected_changes",
                evolution=replace(supervised.evolution, create_missing_change=True),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                task_refs=("APP-01", "APP-02"),
                max_tasks=2,
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=auto_create_change_runner(calls, root=root),
            )
            state = load_pipeline(root)
            latest = state["sessions"][0]
            changes = json.loads(
                (root / "AI_PROJECT" / "state" / "evolution.json").read_text(
                    encoding="utf-8"
                )
            )["changes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertEqual([change["id"] for change in changes], ["CHG-001", "CHG-002"])
            self.assertEqual(latest["linked_change_ids"], ["CHG-001", "CHG-002"])
            change_gate = latest["steps"][0]["gate_outcomes"][0]["details"]["change_gate"]
            self.assertEqual(change_gate["created_change_ids"], ["CHG-001", "CHG-002"])

    def test_owner_approval_policy_approves_selected_queue_changes_and_continues(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_multi_task_project_state(root, task_count=5)
            evolution_path = root / "AI_PROJECT" / "state" / "evolution.json"
            evolution = json.loads(evolution_path.read_text(encoding="utf-8"))
            evolution["changes"] = [
                {
                    "id": "CHG-001",
                    "status": "proposed",
                    "title": "Existing proposed",
                    "linked_tasks": ["TASK-003"],
                },
                {
                    "id": "CHG-002",
                    "status": "ready",
                    "title": "Existing ready",
                    "linked_tasks": ["TASK-004"],
                },
                {
                    "id": "CHG-999",
                    "status": "ready",
                    "title": "Unrelated ready",
                    "linked_tasks": ["TASK-999"],
                },
            ]
            evolution_path.write_text(json.dumps(evolution), encoding="utf-8")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="owner_approved_session_changes",
                evolution=replace(
                    supervised.evolution,
                    create_missing_change=True,
                    owner_approve_required_changes_for_session=True,
                    owner_approval_note="Owner approved this selected queue.",
                ),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                task_refs=("APP-01", "APP-02", "APP-03", "APP-04", "APP-05"),
                max_tasks=5,
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=auto_create_change_runner(calls, root=root, allow_approval=True),
            )
            state = load_pipeline(root)
            latest = state["sessions"][0]
            changes = {
                change["id"]: change
                for change in json.loads(evolution_path.read_text(encoding="utf-8"))[
                    "changes"
                ]
            }
            gate_details = latest["steps"][0]["gate_outcomes"][0]["details"]
            change_gate = gate_details["change_gate"]
            command_texts = [" ".join(call) for call in calls]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertIn("policy stops before Codex execution", result.data["stop_reason"])
            self.assertEqual(changes["CHG-001"]["status"], "approved")
            self.assertEqual(changes["CHG-002"]["status"], "approved")
            self.assertEqual(changes["CHG-999"]["status"], "ready")
            self.assertEqual(changes["CHG-004"]["status"], "approved")
            self.assertEqual(changes["CHG-005"]["status"], "approved")
            self.assertEqual(changes["CHG-006"]["status"], "approved")
            self.assertEqual(
                change_gate["approved_change_ids"],
                ["CHG-004", "CHG-005", "CHG-001", "CHG-002", "CHG-006"],
            )
            self.assertEqual(
                change_gate["approved_task_refs"],
                ["APP-01", "APP-02", "APP-03", "APP-04", "APP-05"],
            )
            self.assertEqual(
                change_gate["owner_approval"]["approval_note"],
                "Owner approved this selected queue.",
            )
            self.assertEqual(change_gate["owner_approval"]["session_id"], "PSESS-001")
            self.assertTrue(any(" change approve CHG-001 " in text for text in command_texts))
            self.assertTrue(any(" change approve CHG-002 " in text for text in command_texts))
            self.assertFalse(any(" change approve CHG-999 " in text for text in command_texts))
            self.assertTrue(any(" current set TASK-001" in text for text in command_texts))

    def test_supervised_builds_prompt_and_stops_before_codex_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            session = create_session(root=root, actor="tester", policy_name="supervised")
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=successful_workflow_runner(calls),
            )
            step = load_pipeline(root)["sessions"][0]["steps"][0]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertIn("policy stops before Codex execution", result.data["stop_reason"])
            self.assertTrue(calls)
            self.assertTrue(any("context" in call for call in calls))
            self.assertEqual(step["status"], "passed")
            self.assertEqual(step["gate_outcomes"][0]["status"], "skipped")

    def test_run_until_blocker_collects_auto_submitted_stdout_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="phase_auto_collect_report_test",
                batch=BatchPolicy(max_steps=4, max_failures=1),
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                    require_report=True,
                ),
            )
            session = create_session(root=root, actor="tester", policy=policy)
            calls = []

            result = run_until_blocker(
                session.data["session_id"],
                root=root,
                actor="tester",
                confirmed=True,
                runner=structured_report_workflow_runner(
                    calls,
                    root=root,
                    codex_stdout=codex_stdout_for_report(emitted_codex_report()),
                ),
            )
            latest = load_pipeline(root)["sessions"][0]
            phases = {entry["phase"]: entry for entry in latest["phase_history"]}
            execute = phases["execute"]
            collect_report = phases["collect_report"]
            report_state = json.loads(
                (root / "AI_PROJECT" / "state" / "task_reports.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "MAX_STEPS_REACHED")
            self.assertEqual(
                [entry["phase"] for entry in latest["phase_history"]],
                ["queue_preview", "prepare", "execute", "collect_report"],
            )
            self.assertEqual(execute["status"], "passed")
            self.assertEqual(
                execute["artifacts"]["adapter"]["code"],
                "CODEX_ADAPTER_LOCAL_COMMAND_PASSED",
            )
            self.assertEqual(execute["artifacts"]["report_id"], "RPT-001")
            self.assertEqual(execute["artifacts"]["after_report_id"], "RPT-001")
            self.assertEqual(
                execute["artifacts"]["adapter_summary"]["report_ids"],
                ["RPT-001"],
            )
            self.assertEqual(collect_report["status"], "passed")
            self.assertEqual(collect_report["artifacts"]["report_id"], "RPT-001")
            self.assertTrue(collect_report["artifacts"]["report_found"])
            self.assertEqual(collect_report["artifacts"]["freshness_basis"], "report_id")
            self.assertEqual(report_state["latest_by_task"], {"TASK-001": "RPT-001"})
            self.assertEqual(
                report_state["reports"][0]["report"]["reported_task_id"],
                "TASK-001",
            )
            self.assertTrue(
                report_state["reports"][0]["source_file"].startswith(
                    "captured:stdout:sha256:"
                )
            )
            self.assertIn(["codex", "exec"], calls)

    def test_run_until_blocker_keeps_max_steps_for_incomplete_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="incomplete_max_steps_regression",
                batch=BatchPolicy(max_steps=1, max_failures=1),
            )
            session = create_session(root=root, actor="tester", policy=policy)
            session_id = session.data["session_id"]
            recorded = record_phase_result(
                session_id,
                PhaseResult.passed(
                    "prepare",
                    reason="Task preparation completed.",
                    next_action="Continue pipeline execution.",
                    artifacts={
                        "session_id": session_id,
                        "task_id": "TASK-001",
                        "task_ref": "APP-01",
                    },
                ),
                root=root,
                actor="tester",
                task_id="TASK-001",
                command="pipeline.phase.prepare",
            )
            self.assertTrue(recorded.ok)

            result = run_until_blocker(
                session_id,
                root=root,
                actor="tester",
                confirmed=True,
            )
            latest = load_pipeline(root)["sessions"][0]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "MAX_STEPS_REACHED")
            self.assertEqual(result.data["session_status"], "stopped")
            self.assertEqual(latest["status"], "stopped")
            self.assertIn("MAX_STEPS_REACHED", latest["stop_reason"])

    def test_run_until_blocker_completes_committed_close_before_max_steps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="accepted")
            supervised = policy_preset("supervised_local_commit")
            policy = replace(
                supervised,
                name="committed_close_max_steps_regression",
                batch=BatchPolicy(max_steps=1, max_failures=1),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            session_id = session.data["session_id"]
            commit_hash = "abc1234deadbeef"
            close_status = {
                "outcome": "closed_with_local_commit",
                "task_closed": True,
                "task_status": "done",
                "commit_status": "pass",
                "commit_code": "LOCAL_COMMIT_CREATED",
                "commit_hash": commit_hash,
                "commit_readiness_status": "pass",
                "commit_readiness_code": "COMMIT_READY",
                "owner_next_action": "Review the completed pipeline session.",
            }
            recorded = record_phase_result(
                session_id,
                PhaseResult.passed(
                    "close",
                    reason="Close completed and local commit was created.",
                    next_action=close_status["owner_next_action"],
                    artifacts={
                        "session_id": session_id,
                        "task_id": "TASK-001",
                        "task_ref": "APP-01",
                        "close_status": close_status,
                        "local_commit": {
                            "status": "pass",
                            "code": "LOCAL_COMMIT_CREATED",
                            "commit_hash": commit_hash,
                        },
                    },
                ),
                root=root,
                actor="tester",
                task_id="TASK-001",
                command="pipeline.phase.close",
            )
            self.assertTrue(recorded.ok)
            before_bookkeeping = pipeline_bookkeeping_snapshot(root)
            git_calls = []

            def clean_post_commit_status(argv):
                args = list(argv)
                if args == ["git", "status", "--short", "--untracked-files=all"]:
                    git_calls.append(args)
                    return completed(stdout="")
                return completed('{"ok": true}\n')

            result = run_until_blocker(
                session_id,
                root=root,
                actor="tester",
                confirmed=True,
                runner=clean_post_commit_status,
            )
            latest = load_pipeline(root)["sessions"][0]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["session_status"], "completed")
            self.assertEqual(result.data["stop_code"], "QUEUE_COMPLETE")
            self.assertNotEqual(result.data["stop_code"], "MAX_STEPS_REACHED")
            self.assertEqual(result.data["commit_hash"], commit_hash)
            self.assertEqual(result.data["close_status"]["commit_hash"], commit_hash)
            self.assertIn("TASK-001", result.data["completed_tasks"])
            self.assertIn("TASK-001", result.data["changed_tasks"])
            self.assertIn(commit_hash, result.data["commits"])
            self.assertEqual(result.data["side_effects"], [])
            self.assertEqual(result.changed_files, [])
            self.assertEqual(result.generated_files, [])
            self.assertEqual(result.events, [])
            self.assertEqual(pipeline_bookkeeping_snapshot(root), before_bookkeeping)
            self.assertEqual(
                git_calls,
                [["git", "status", "--short", "--untracked-files=all"]],
            )
            self.assertEqual(latest["status"], "running")
            self.assertNotIn("MAX_STEPS_REACHED", latest.get("stop_reason", ""))

    def test_run_until_blocker_returns_committed_close_complete_without_bookkeeping_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="accepted")
            _write_task_status(root, "done")
            supervised = policy_preset("supervised_local_commit")
            policy = replace(
                supervised,
                name="committed_close_no_post_commit_bookkeeping",
                batch=BatchPolicy(max_steps=2, max_failures=1),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            session_id = session.data["session_id"]
            precommit = record_phase_result(
                session_id,
                {
                    "phase": "close",
                    "status": "running",
                    "reason": "Close task state rendered before local commit readiness.",
                    "next_action": "Create the local commit.",
                    "artifacts": {
                        "session_id": session_id,
                        "task_id": "TASK-001",
                        "task_ref": "APP-01",
                    },
                    "changed_files": [],
                    "generated_files": [],
                    "events": [],
                },
                root=root,
                actor="tester",
                task_id="TASK-001",
                command="pipeline.phase.close",
            )
            self.assertTrue(precommit.ok)
            before_bookkeeping = pipeline_bookkeeping_snapshot(root)
            commit_hash = "abc1234deadbeef"
            close_status = {
                "outcome": "closed_with_local_commit",
                "task_closed": True,
                "task_status": "done",
                "commit_status": "pass",
                "commit_code": "LOCAL_COMMIT_CREATED",
                "commit_hash": commit_hash,
                "commit_readiness_status": "pass",
                "commit_readiness_code": "COMMIT_READY",
                "owner_next_action": "Review the completed pipeline session.",
            }
            final_close_phase = {
                "phase": "close",
                "status": "passed",
                "reason": "Close completed and local commit was created.",
                "next_action": close_status["owner_next_action"],
                "artifacts": {
                    "session_id": session_id,
                    "task_id": "TASK-001",
                    "task_ref": "APP-01",
                    "close_status": close_status,
                    "local_commit": {
                        "status": "pass",
                        "code": "LOCAL_COMMIT_CREATED",
                        "commit_hash": commit_hash,
                    },
                },
                "changed_files": [],
                "generated_files": [],
                "events": [],
            }
            step = CommandResult.success(
                command="pipeline.run_next",
                domain="pipeline",
                message="Close completed and local commit was created.",
                data={
                    "session_id": session_id,
                    "dispatched_phase": "close",
                    "phase_status": "passed",
                    "phase_result": final_close_phase,
                    "selected_task": {"id": "TASK-001", "ref": "APP-01"},
                    "side_effects": [],
                },
            )
            git_calls = []

            def clean_post_commit_status(argv):
                args = list(argv)
                if args == ["git", "status", "--short", "--untracked-files=all"]:
                    git_calls.append(args)
                    return completed(stdout="")
                return completed('{"ok": true}\n')

            with patch("ai_project_ctl.pipeline.batch.run_next", return_value=step):
                result = run_until_blocker(
                    session_id,
                    root=root,
                    actor="tester",
                    confirmed=True,
                    runner=clean_post_commit_status,
                )
            latest = load_pipeline(root)["sessions"][0]
            event_commands = [
                json.loads(line)["command"]
                for line in pipeline_events_path(root).read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["session_status"], "completed")
            self.assertEqual(result.data["stop_code"], "QUEUE_COMPLETE")
            self.assertEqual(result.data["commit_hash"], commit_hash)
            self.assertEqual(result.data["close_status"]["commit_hash"], commit_hash)
            self.assertIn("TASK-001", result.data["completed_tasks"])
            self.assertIn("TASK-001", result.data["changed_tasks"])
            self.assertIn(commit_hash, result.data["commits"])
            self.assertEqual(result.changed_files, [])
            self.assertEqual(result.generated_files, [])
            self.assertEqual(result.events, [])
            self.assertEqual(pipeline_bookkeeping_snapshot(root), before_bookkeeping)
            self.assertNotIn("pipeline.session.complete", event_commands)
            self.assertEqual(latest["status"], "running")
            self.assertEqual(latest["phase_history"][-1]["status"], "running")
            self.assertEqual(
                git_calls,
                [["git", "status", "--short", "--untracked-files=all"]],
            )

    def test_run_until_blocker_persists_non_local_commit_queue_completion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="accepted")
            _write_task_status(root, "done")
            session = create_session(root=root, actor="tester", policy_name="supervised")
            session_id = session.data["session_id"]
            close_status = {
                "outcome": "done_without_local_commit",
                "task_closed": True,
                "task_status": "done",
                "commit_status": "skipped",
                "commit_code": "LOCAL_COMMIT_DISABLED",
                "commit_hash": "",
                "commit_readiness_status": "",
                "commit_readiness_code": "",
                "owner_next_action": "Review the completed pipeline session.",
            }
            recorded = record_phase_result(
                session_id,
                PhaseResult.passed(
                    "close",
                    reason="Close completed without a local commit.",
                    next_action=close_status["owner_next_action"],
                    artifacts={
                        "session_id": session_id,
                        "task_id": "TASK-001",
                        "task_ref": "APP-01",
                        "close_status": close_status,
                        "local_commit": {
                            "status": "skipped",
                            "code": "LOCAL_COMMIT_DISABLED",
                            "commit_hash": "",
                        },
                    },
                ),
                root=root,
                actor="tester",
                task_id="TASK-001",
                command="pipeline.phase.close",
            )
            self.assertTrue(recorded.ok)
            before_bookkeeping = pipeline_bookkeeping_snapshot(root)

            result = run_until_blocker(
                session_id,
                root=root,
                actor="tester",
                confirmed=True,
            )
            latest = load_pipeline(root)["sessions"][0]
            event_commands = [
                json.loads(line)["command"]
                for line in pipeline_events_path(root).read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["session_status"], "completed")
            self.assertEqual(result.data["stop_code"], "QUEUE_COMPLETE")
            self.assertEqual(result.data["close_status"]["outcome"], "done_without_local_commit")
            self.assertEqual(result.data["commit_hash"], "")
            self.assertIn("TASK-001", result.data["completed_tasks"])
            self.assertIn("TASK-001", result.data["changed_tasks"])
            self.assertEqual(latest["status"], "completed")
            self.assertIn("pipeline.session.complete", event_commands)
            self.assertNotEqual(pipeline_bookkeeping_snapshot(root), before_bookkeeping)
            self.assertTrue(
                any(path.endswith("AI_PROJECT/state/pipeline_sessions.json") for path in result.changed_files)
            )
            self.assertTrue(
                any(path.endswith("AI_PROJECT/events/pipeline-events.jsonl") for path in result.changed_files)
            )
            self.assertTrue(
                any(path.endswith("AI_PROJECT/generated/PIPELINE_STATUS.md") for path in result.generated_files)
            )
            self.assertTrue(
                any(path.endswith("AI_PROJECT/generated/PIPELINE_AUDIT.md") for path in result.generated_files)
            )

    def test_run_until_blocker_stops_final_committed_close_with_dirty_worktree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="accepted")
            supervised = policy_preset("supervised_local_commit")
            policy = replace(
                supervised,
                name="committed_close_final_dirty_worktree",
                batch=BatchPolicy(max_steps=1, max_failures=1),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            session_id = session.data["session_id"]
            commit_hash = "abc1234deadbeef"
            close_status = {
                "outcome": "closed_with_local_commit",
                "task_closed": True,
                "task_status": "done",
                "commit_status": "pass",
                "commit_code": "LOCAL_COMMIT_CREATED",
                "commit_hash": commit_hash,
                "commit_readiness_status": "pass",
                "commit_readiness_code": "COMMIT_READY",
                "owner_next_action": "Review the completed pipeline session.",
            }
            recorded = record_phase_result(
                session_id,
                PhaseResult.passed(
                    "close",
                    reason="Close completed and local commit was created.",
                    next_action=close_status["owner_next_action"],
                    artifacts={
                        "session_id": session_id,
                        "task_id": "TASK-001",
                        "task_ref": "APP-01",
                        "close_status": close_status,
                        "local_commit": {
                            "status": "pass",
                            "code": "LOCAL_COMMIT_CREATED",
                            "commit_hash": commit_hash,
                        },
                    },
                ),
                root=root,
                actor="tester",
                task_id="TASK-001",
                command="pipeline.phase.close",
            )
            self.assertTrue(recorded.ok)
            git_calls = []

            def dirty_post_commit_status(argv):
                args = list(argv)
                if args == ["git", "status", "--short", "--untracked-files=all"]:
                    git_calls.append(args)
                    return completed(
                        stdout=(
                            " M AI_PROJECT/state/pipeline_sessions.json\n"
                            " M AI_PROJECT/generated/PIPELINE_STATUS.md\n"
                            "?? scratch.txt\n"
                        )
                    )
                return completed('{"ok": true}\n')

            result = run_until_blocker(
                session_id,
                root=root,
                actor="tester",
                confirmed=True,
                runner=dirty_post_commit_status,
            )
            latest = load_pipeline(root)["sessions"][0]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["session_status"], "stopped")
            self.assertEqual(result.data["stop_code"], "POST_COMMIT_DIRTY_WORKTREE")
            self.assertEqual(result.data["blocked_by"], "POST_COMMIT_DIRTY_WORKTREE")
            self.assertEqual(result.data["completed_task_id"], "TASK-001")
            self.assertEqual(
                result.data["dirty_paths"],
                [
                    "AI_PROJECT/generated/PIPELINE_STATUS.md",
                    "AI_PROJECT/state/pipeline_sessions.json",
                ],
            )
            self.assertEqual(result.data["dirty_files"], result.data["dirty_paths"])
            self.assertEqual(
                result.data["post_commit_worktree"]["git_status"][
                    "tracked_dirty_paths"
                ],
                result.data["dirty_paths"],
            )
            self.assertIn(
                "scratch.txt",
                result.data["post_commit_worktree"]["git_status"]["dirty_paths"],
            )
            self.assertNotIn("scratch.txt", result.data["dirty_paths"])
            self.assertEqual(latest["status"], "stopped")
            self.assertIn("POST_COMMIT_DIRTY_WORKTREE", latest["stop_reason"])
            self.assertIn("TASK-001", result.data["completed_tasks"])
            self.assertIn("TASK-001", result.data["changed_tasks"])
            self.assertEqual(result.data["commit_status"], "blocked")
            self.assertEqual(result.data["commit_code"], "POST_COMMIT_DIRTY_WORKTREE")
            self.assertEqual(result.data["close_status"]["commit_status"], "pass")
            self.assertEqual(result.data["commit_hash"], commit_hash)
            self.assertIn(commit_hash, result.data["commits"])
            self.assertEqual(
                git_calls,
                [["git", "status", "--short", "--untracked-files=all"]],
            )

    def test_run_until_blocker_continues_after_committed_close_with_next_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_multi_task_project_state(root, task_count=2)
            _write_task_status(root, "done")
            supervised = policy_preset("supervised_local_commit")
            policy = replace(
                supervised,
                name="committed_close_continues_to_next_task",
                batch=BatchPolicy(max_steps=2, max_failures=1),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                task_refs=("APP-01", "APP-02"),
                max_tasks=2,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            session_id = session.data["session_id"]
            commit_hash = "abc1234deadbeef"
            close_status = {
                "outcome": "closed_with_local_commit",
                "task_closed": True,
                "task_status": "done",
                "commit_status": "pass",
                "commit_code": "LOCAL_COMMIT_CREATED",
                "commit_hash": commit_hash,
                "commit_readiness_status": "pass",
                "commit_readiness_code": "COMMIT_READY",
                "owner_next_action": "Continue with the selected queue.",
            }
            recorded = record_phase_result(
                session_id,
                PhaseResult.passed(
                    "close",
                    reason="Close completed and local commit was created.",
                    next_action=close_status["owner_next_action"],
                    artifacts={
                        "session_id": session_id,
                        "task_id": "TASK-001",
                        "task_ref": "APP-01",
                        "close_status": close_status,
                        "local_commit": {
                            "status": "pass",
                            "code": "LOCAL_COMMIT_CREATED",
                            "commit_hash": commit_hash,
                        },
                    },
                ),
                root=root,
                actor="tester",
                task_id="TASK-001",
                command="pipeline.phase.close",
            )
            self.assertTrue(recorded.ok)
            git_calls = []

            def clean_post_task_status(argv):
                args = list(argv)
                if args == ["git", "status", "--short", "--untracked-files=all"]:
                    git_calls.append(args)
                    return completed(stdout="")
                return completed('{"ok": true}\n')

            result = run_until_blocker(
                session_id,
                root=root,
                actor="tester",
                confirmed=True,
                runner=clean_post_task_status,
            )
            latest = load_pipeline(root)["sessions"][0]
            queue_preview = latest["phase_history"][-1]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["session_status"], "stopped")
            self.assertEqual(result.data["stop_code"], "MAX_STEPS_REACHED")
            self.assertEqual(latest["status"], "stopped")
            self.assertEqual(queue_preview["phase"], "queue_preview")
            self.assertEqual(
                queue_preview["artifacts"]["next_task"]["id"],
                "TASK-002",
            )
            self.assertIn("TASK-001", result.data["completed_tasks"])
            self.assertIn("TASK-001", result.data["changed_tasks"])
            self.assertNotIn("TASK-002", result.data["completed_tasks"])
            self.assertNotIn("TASK-002", result.data["changed_tasks"])
            self.assertEqual(result.data["commit_hash"], commit_hash)
            self.assertIn(commit_hash, result.data["commits"])
            self.assertEqual(
                git_calls,
                [["git", "status", "--short", "--untracked-files=all"]],
            )

    def test_run_until_blocker_stops_after_committed_close_with_dirty_handoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_multi_task_project_state(root, task_count=2)
            _write_task_status(root, "done")
            supervised = policy_preset("supervised_local_commit")
            policy = replace(
                supervised,
                name="committed_close_dirty_handoff_stops",
                batch=BatchPolicy(max_steps=2, max_failures=1),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                task_refs=("APP-01", "APP-02"),
                max_tasks=2,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            session_id = session.data["session_id"]
            commit_hash = "abc1234deadbeef"
            close_status = {
                "outcome": "closed_with_local_commit",
                "task_closed": True,
                "task_status": "done",
                "commit_status": "pass",
                "commit_code": "LOCAL_COMMIT_CREATED",
                "commit_hash": commit_hash,
                "commit_readiness_status": "pass",
                "commit_readiness_code": "COMMIT_READY",
                "owner_next_action": "Continue with the selected queue.",
            }
            recorded = record_phase_result(
                session_id,
                PhaseResult.passed(
                    "close",
                    reason="Close completed and local commit was created.",
                    next_action=close_status["owner_next_action"],
                    artifacts={
                        "session_id": session_id,
                        "task_id": "TASK-001",
                        "task_ref": "APP-01",
                        "close_status": close_status,
                        "local_commit": {
                            "status": "pass",
                            "code": "LOCAL_COMMIT_CREATED",
                            "commit_hash": commit_hash,
                        },
                    },
                ),
                root=root,
                actor="tester",
                task_id="TASK-001",
                command="pipeline.phase.close",
            )
            self.assertTrue(recorded.ok)
            git_calls = []

            def dirty_post_task_status(argv):
                args = list(argv)
                if args == ["git", "status", "--short", "--untracked-files=all"]:
                    git_calls.append(args)
                    return completed(stdout=" M README.md\n?? scratch.txt\n")
                return completed('{"ok": true}\n')

            result = run_until_blocker(
                session_id,
                root=root,
                actor="tester",
                confirmed=True,
                runner=dirty_post_task_status,
            )
            latest = load_pipeline(root)["sessions"][0]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["session_status"], "stopped")
            self.assertEqual(result.data["stop_code"], "POST_COMMIT_DIRTY_WORKTREE")
            self.assertEqual(result.data["blocked_by"], "POST_COMMIT_DIRTY_WORKTREE")
            self.assertEqual(result.data["completed_task_id"], "TASK-001")
            self.assertEqual(result.data["dirty_paths"], ["README.md"])
            self.assertEqual(result.data["dirty_files"], ["README.md"])
            self.assertEqual(
                result.data["post_commit_worktree"]["dirty_paths"],
                ["README.md"],
            )
            self.assertIn(
                "scratch.txt",
                result.data["post_commit_worktree"]["git_status"]["dirty_paths"],
            )
            self.assertEqual(result.data["blockers"][0]["completed_task_id"], "TASK-001")
            self.assertEqual(latest["status"], "stopped")
            self.assertEqual(latest["phase_history"][-1]["phase"], "close")
            self.assertIn("TASK-001", result.data["completed_tasks"])
            self.assertIn("TASK-001", result.data["changed_tasks"])
            self.assertEqual(result.data["commit_status"], "blocked")
            self.assertEqual(result.data["commit_code"], "POST_COMMIT_DIRTY_WORKTREE")
            self.assertEqual(result.data["close_status"]["commit_status"], "pass")
            self.assertNotIn("TASK-002", result.data["completed_tasks"])
            self.assertNotIn("TASK-002", result.data["changed_tasks"])
            self.assertEqual(
                git_calls,
                [["git", "status", "--short", "--untracked-files=all"]],
            )

    def test_run_next_summary_keeps_recovered_close_warnings_technical_only(self):
        recovered_warning = CommandMessage(
            "WORKFLOW_NON_BLOCKING_STEP_FAILED",
            "Non-blocking workflow step reported a warning: Check generated context output",
            details={
                "step": "context_generated",
                "command_name": "contextctl.check-generated",
                "returncode": 1,
                "stdout": "stale context before post-close refresh",
                "stderr": "",
            },
        )
        delegated = CommandResult.success(
            command="pipeline.phase.close",
            domain="pipeline",
            message="Close passed.",
            data={
                "phase_result": {
                    "phase": "close",
                    "status": "passed",
                    "reason": "Close passed.",
                    "next_action": "Review completed session.",
                    "artifacts": {
                        "context_refresh": {"ok": True},
                        "close_workflow": {
                            "warnings": [recovered_warning.to_dict()],
                        },
                        "recovered_close_warnings": [
                            {
                                "code": "CLOSE_RECOVERED_NON_BLOCKING_WARNING",
                                "recovered_by": "pipeline.close.context_refresh",
                                "source_command": "pipeline.review_close_policy",
                                "warning": recovered_warning.to_dict(),
                            }
                        ],
                    },
                    "changed_files": [],
                    "generated_files": [],
                    "events": [],
                }
            },
        )

        result = runner_module._phase_dispatch_result(
            delegated,
            phase_name="close",
            session={
                "id": "PSESS-001",
                "current_task_id": "TASK-001",
                "current_task_ref": "APP-01",
            },
            effects=[delegated],
        )

        self.assertEqual(result.warnings, [])
        self.assertEqual(result.data["dispatched_phase"], "close")
        side_effect = result.data["side_effects"][0]
        artifacts = side_effect["data"]["phase_result"]["artifacts"]
        self.assertEqual(len(artifacts["close_workflow"]["warnings"]), 1)
        self.assertEqual(len(artifacts["recovered_close_warnings"]), 1)

    def test_run_until_blocker_no_report_stdout_keeps_adapter_missing_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="phase_auto_collect_missing_report_test",
                batch=BatchPolicy(max_steps=4, max_failures=1),
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                    require_report=True,
                ),
            )
            session = create_session(root=root, actor="tester", policy=policy)
            calls = []

            result = run_until_blocker(
                session.data["session_id"],
                root=root,
                actor="tester",
                confirmed=True,
                runner=structured_report_workflow_runner(
                    calls,
                    root=root,
                    codex_stdout="Codex finished without structured report.\n",
                ),
            )
            latest = load_pipeline(root)["sessions"][0]
            phases = {entry["phase"]: entry for entry in latest["phase_history"]}
            execute = phases["execute"]
            collect_report = phases["collect_report"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "REPORT_MISSING")
            self.assertEqual(execute["status"], "passed")
            self.assertEqual(
                execute["artifacts"]["adapter"]["code"],
                CODEX_ADAPTER_REPORT_MISSING,
            )
            self.assertEqual(execute["artifacts"]["adapter"]["report_id"], "")
            self.assertEqual(collect_report["status"], "blocked")
            self.assertEqual(collect_report["artifacts"]["blocked_by"], "REPORT_MISSING")
            self.assertFalse(
                (root / "AI_PROJECT" / "state" / "task_reports.json").exists()
            )
            self.assertIn(["codex", "exec"], calls)

    def test_run_next_verify_review_allows_advisory_report_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="run_next_advisory_report_warning_test",
                verify=replace(
                    supervised.verify,
                    allow_report_warnings=True,
                    block_report_warnings=False,
                    run_git_diff_gates=False,
                ),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                current_task_id="TASK-001",
                current_task_ref="APP-01",
            )
            report = valid_report("TASK-001")
            report["warnings"] = ["advisory report warning"]
            report["blockers"] = []
            write_report_state(root, "TASK-001", "RPT-001", report=report)
            record_collected_report(root, session.data["session_id"])
            external_calls = []

            def external_runner(argv):
                external_calls.append(list(argv))
                raise AssertionError("external command should not run")

            verify_result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=external_runner,
            )
            review_result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=external_runner,
            )
            latest = load_pipeline(root)["sessions"][0]
            phases = {entry["phase"]: entry for entry in latest["phase_history"]}
            verify_phase = phases["verify"]
            review_phase = phases["review"]
            verify_artifacts = verify_phase["artifacts"]
            review_artifacts = review_phase["artifacts"]

        self.assertTrue(verify_result.ok)
        self.assertEqual(verify_result.data["dispatched_phase"], "verify")
        self.assertEqual(verify_result.data["phase_status"], "passed")
        self.assertEqual(verify_phase["status"], "passed")
        self.assertEqual(verify_artifacts["report_gate_status"], "warn")
        self.assertEqual(verify_artifacts["report_gate_code"], CODEX_REPORT_WARN)
        self.assertEqual(
            verify_artifacts["warn_policy"],
            "report_gate_warnings_allowed_by_policy",
        )
        self.assertEqual(
            verify_artifacts[REPORT_WARNING_POLICY_KEY],
            {
                "allow_report_warnings": True,
                "block_report_warnings": False,
                "decision": "allowed",
                "policy": "report_gate_warnings_allowed_by_policy",
                "reason": "policy.verify.allow_report_warnings is true",
                "report_gate_status": "warn",
                "report_gate_code": CODEX_REPORT_WARN,
            },
        )
        self.assertEqual(
            verify_artifacts[GIT_DIFF_GATES_POLICY_KEY]["mode"],
            "relaxed",
        )
        self.assertEqual(
            [gate["status"] for gate in verify_artifacts[SKIPPED_GATES_KEY]],
            ["skipped", "skipped", "skipped"],
        )
        self.assertEqual(
            verify_artifacts["verify_evidence"][REPORT_WARNING_POLICY_KEY],
            verify_artifacts[REPORT_WARNING_POLICY_KEY],
        )
        self.assertEqual(
            verify_artifacts["verify_evidence"]["report_gate"]["warnings"][0]["message"],
            "Report contains warning(s): advisory report warning",
        )
        self.assertTrue(review_result.ok)
        self.assertEqual(review_result.data["dispatched_phase"], "review")
        self.assertEqual(review_result.data["phase_status"], "passed")
        self.assertEqual(review_phase["status"], "passed")
        self.assertEqual(review_artifacts.get("blocked_by", ""), "")
        self.assertNotEqual(
            review_result.data.get("stop_code"),
            "REPORT_GATE_NOT_PASSED_AFTER_VERIFY",
        )
        self.assertEqual(review_artifacts["report_gate_status"], "warn")
        self.assertTrue(review_artifacts["report_gate_acceptance"]["allow"])
        self.assertEqual(
            review_artifacts["report_gate_acceptance"]["policy"],
            "report_gate_warn_allowed_by_policy",
        )
        self.assertTrue(review_artifacts["build_prompt_only"])
        self.assertEqual(external_calls, [])

    def test_run_codex_records_token_gate_pass_before_manual_adapter_blocker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="run_codex_test",
                codex=replace(supervised.codex, mode=CodexExecutionMode.RUN_CODEX),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=successful_workflow_runner(calls, root=root),
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertEqual(gates[0]["name"], "token_budget_gate")
            self.assertEqual(gates[0]["status"], "pass")
            self.assertEqual(gates[0]["details"]["token_budget"]["code"], "TOKEN_BUDGET_PASS")
            self.assertEqual(gates[1]["name"], "codex_execution_adapter")
            self.assertEqual(gates[1]["status"], "blocked")
            self.assertTrue(gates[1]["details"]["codex_adapter_called"])
            self.assertEqual(
                gates[1]["details"]["adapter"]["code"],
                "CODEX_ADAPTER_MANUAL_HANDOFF_REQUIRED",
            )

    def test_run_codex_local_adapter_records_codex_review_pass_then_policy_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="run_codex_local_adapter_test",
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                ),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=successful_workflow_runner(
                    calls,
                    root=root,
                    report_on_local_codex=True,
                ),
                codex_reviewer=lambda prompt: valid_review_output(),
            )
            latest = load_pipeline(root)["sessions"][0]
            gates = latest["steps"][0]["gate_outcomes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "BLOCKED")
            self.assertIn("policy stops before auto-close", result.data["stop_reason"])
            self.assertEqual(gates[1]["name"], "codex_execution_adapter")
            self.assertEqual(gates[1]["status"], "pass")
            self.assertEqual(gates[1]["details"]["adapter"]["report_id"], "RPT-001")
            self.assertEqual(gates[2]["name"], "codex_report_gate")
            self.assertEqual(gates[2]["status"], "pass")
            self.assertEqual(gates[2]["details"]["report_gate"]["report_id"], "RPT-001")
            self.assertEqual(gates[3]["name"], "machine_review_gate")
            self.assertEqual(gates[3]["status"], "pass")
            self.assertEqual(gates[4]["name"], "codex_review_gate")
            self.assertEqual(gates[4]["status"], "pass")
            self.assertEqual(gates[4]["details"]["codex_review"]["verdict"], "APPROVE")
            self.assertEqual(gates[5]["name"], "pipeline_policy")
            self.assertEqual(gates[5]["status"], "skipped")
            self.assertEqual(latest["report_ids"], ["RPT-001"])
            self.assertEqual(len(latest["review_ids"]), 1)
            self.assertIn(["codex", "exec"], calls)

    def test_run_codex_blocks_when_codex_review_output_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="run_codex_missing_review_test",
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                ),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=successful_workflow_runner(
                    [],
                    root=root,
                    report_on_local_codex=True,
                ),
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "CODEX_REVIEW_GATE_FAILURE")
            self.assertEqual(gates[4]["name"], "codex_review_gate")
            self.assertEqual(gates[4]["status"], "fail")
            self.assertEqual(
                gates[4]["details"]["codex_review"]["code"],
                "CODEX_REVIEW_OUTPUT_MISSING",
            )

    def test_run_codex_request_changes_blocks_before_policy_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="run_codex_request_changes_review_test",
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                ),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=successful_workflow_runner(
                    [],
                    root=root,
                    report_on_local_codex=True,
                ),
                codex_reviewer=lambda prompt: valid_review_output(
                    "REQUEST_CHANGES",
                    findings=(
                        {
                            "severity": "Major",
                            "message": "Acceptance evidence is incomplete.",
                            "file": "ai_project_ctl/pipeline/codex_review.py",
                        },
                    ),
                ),
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "CODEX_REVIEW_REQUEST_CHANGES")
            self.assertEqual(gates[4]["name"], "codex_review_gate")
            self.assertEqual(gates[4]["status"], "blocked")
            self.assertEqual(len(gates), 5)

    def test_autoclose_policy_closes_after_machine_pass_and_codex_approve(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised_autoclose")
            policy = replace(
                supervised,
                name="run_codex_autoclose_close_test",
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                ),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []
            fake_runner, task_status = stateful_workflow_runner(calls, root=root)

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=fake_runner,
                codex_reviewer=lambda prompt: valid_review_output(),
            )
            latest = load_pipeline(root)["sessions"][0]
            gates = latest["steps"][0]["gate_outcomes"]
            commands = [" ".join(call) for call in calls]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "TASK_AUTO_CLOSED")
            self.assertEqual(task_status["value"], "done")
            self.assertEqual(gates[5]["name"], "review_close_gate")
            self.assertEqual(gates[5]["status"], "pass")
            self.assertEqual(gates[5]["details"]["close_policy"]["action"], "close_task")
            self.assertTrue(any("task transition TASK-001 --to in_review" in command for command in commands))
            self.assertTrue(any("task approve TASK-001 --notes Owner auto-close note=Owner approved auto-close for this test session." in command for command in commands))
            self.assertTrue(any("Pipeline policy=run_codex_autoclose_close_test" in command for command in commands))
            self.assertTrue(any("machine_gate=pass/MACHINE_REVIEW_PASS" in command for command in commands))
            self.assertTrue(any("codex_review=APPROVE/CODEX_REVIEW_APPROVE" in command for command in commands))
            self.assertTrue(any("report_id=RPT-001" in command for command in commands))
            self.assertTrue(any("task transition TASK-001 --to done" in command for command in commands))

    def test_autoclose_policy_requests_changes_when_review_requests_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised_autoclose")
            policy = replace(
                supervised,
                name="run_codex_autoclose_rework_test",
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                ),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []
            fake_runner, task_status = stateful_workflow_runner(calls, root=root)

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=fake_runner,
                codex_reviewer=lambda prompt: valid_review_output(
                    "REQUEST_CHANGES",
                    findings=(
                        {
                            "severity": "Major",
                            "message": "Acceptance evidence is incomplete.",
                            "file": "ai_project_ctl/pipeline/close_policy.py",
                        },
                    ),
                ),
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]
            commands = [" ".join(call) for call in calls]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "CODEX_REVIEW_REQUEST_CHANGES")
            self.assertEqual(task_status["value"], "changes_requested")
            self.assertEqual(gates[4]["name"], "codex_review_gate")
            self.assertEqual(gates[4]["status"], "blocked")
            self.assertEqual(gates[5]["name"], "review_close_gate")
            self.assertEqual(gates[5]["status"], "blocked")
            self.assertEqual(gates[5]["details"]["close_policy"]["action"], "request_changes")
            self.assertTrue(any("task transition TASK-001 --to in_review" in command for command in commands))
            self.assertTrue(any("task add-note TASK-001 --text Owner auto-close note=Owner approved auto-close for this test session." in command for command in commands))
            self.assertTrue(any("Pipeline policy=run_codex_autoclose_rework_test" in command for command in commands))
            self.assertTrue(any("task transition TASK-001 --to changes_requested" in command for command in commands))

    def test_autoclose_policy_stops_when_codex_review_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised_autoclose")
            policy = replace(
                supervised,
                name="run_codex_autoclose_blocked_review_test",
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                ),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []
            fake_runner, _task_status = stateful_workflow_runner(calls, root=root)

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=fake_runner,
                codex_reviewer=lambda prompt: valid_review_output(
                    "BLOCKED",
                    findings=(
                        {
                            "severity": "Major",
                            "message": "Semantic review could not be completed.",
                            "file": "ai_project_ctl/pipeline/close_policy.py",
                        },
                    ),
                ),
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]
            commands = [" ".join(call) for call in calls]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "CODEX_REVIEW_BLOCKED")
            self.assertEqual(gates[4]["name"], "codex_review_gate")
            self.assertEqual(gates[4]["status"], "blocked")
            self.assertEqual(len(gates), 5)
            self.assertFalse(any("task approve TASK-001" in command for command in commands))
            self.assertFalse(any("task transition TASK-001 --to changes_requested" in command for command in commands))

    def test_autoclose_policy_does_not_close_after_machine_review_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised_autoclose")
            policy = replace(
                supervised,
                name="run_codex_autoclose_machine_fail_test",
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                ),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []
            base_runner, _task_status = stateful_workflow_runner(calls, root=root)

            def fake_runner(argv):
                if tuple(argv)[-2:] == ("project", "protected-check"):
                    calls.append(list(argv))
                    return completed(returncode=1, stderr="protected drift\n")
                return base_runner(argv)

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=fake_runner,
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]
            commands = [" ".join(call) for call in calls]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "MACHINE_REVIEW_FAILURE")
            self.assertEqual(gates[3]["name"], "machine_review_gate")
            self.assertEqual(gates[3]["status"], "fail")
            self.assertFalse(any("task approve TASK-001" in command for command in commands))
            self.assertFalse(any("review_close_gate" == gate["name"] for gate in gates))

    def test_autoclose_policy_stops_when_rework_limit_is_reached(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised_autoclose")
            policy = replace(
                supervised,
                name="run_codex_autoclose_rework_limit_test",
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                ),
                rework=replace(supervised.rework, max_rework_attempts=1),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            state_path = pipeline_state_path(root)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["sessions"][0]["attempt_counters"]["rework"] = 1
            state_path.write_text(json.dumps(state), encoding="utf-8")
            calls = []
            fake_runner, task_status = stateful_workflow_runner(calls, root=root)

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=fake_runner,
                codex_reviewer=lambda prompt: valid_review_output(
                    "REQUEST_CHANGES",
                    findings=(
                        {
                            "severity": "Major",
                            "message": "Acceptance evidence is incomplete.",
                            "file": "ai_project_ctl/pipeline/close_policy.py",
                        },
                    ),
                ),
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]
            commands = [" ".join(call) for call in calls]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "REWORK_LIMIT_REACHED")
            self.assertEqual(task_status["value"], "in_progress")
            self.assertEqual(gates[5]["name"], "review_close_gate")
            self.assertEqual(gates[5]["status"], "blocked")
            self.assertEqual(gates[5]["details"]["close_policy"]["action"], "stop")
            self.assertFalse(any("task transition TASK-001 --to changes_requested" in command for command in commands))

    def test_run_codex_blocks_downstream_when_machine_review_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="run_codex_machine_review_failure_test",
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                ),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []
            base_runner = successful_workflow_runner(
                calls,
                root=root,
                report_on_local_codex=True,
            )

            def fake_runner(argv):
                if tuple(argv)[-2:] == ("project", "protected-check"):
                    return completed(returncode=1, stderr="protected drift\n")
                return base_runner(argv)

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=fake_runner,
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "MACHINE_REVIEW_FAILURE")
            self.assertEqual(gates[3]["name"], "machine_review_gate")
            self.assertEqual(gates[3]["status"], "fail")
            self.assertNotIn("codex_review_gate", [gate["name"] for gate in gates])

    def test_run_codex_blocks_downstream_when_report_gate_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="run_codex_report_gate_failure_test",
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                ),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []
            report = valid_report("TASK-001")
            report["blockers"] = ["Manual blocker."]
            base_runner = successful_workflow_runner(calls, root=root)

            def fake_runner(argv):
                if list(argv) == ["codex", "exec"]:
                    calls.append(list(argv))
                    write_report_state(root, "TASK-001", "RPT-001", report=report)
                    return completed(stdout="report submitted\n")
                return base_runner(argv)

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=fake_runner,
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "CODEX_REPORT_GATE_FAILURE")
            self.assertEqual(gates[2]["name"], "codex_report_gate")
            self.assertEqual(gates[2]["status"], "fail")
            self.assertNotIn("codex_review_gate", [gate["name"] for gate in gates])
            self.assertIn(["codex", "exec"], calls)

    def test_run_codex_stops_on_token_budget_failure_before_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="run_codex_low_budget_test",
                codex=replace(supervised.codex, mode=CodexExecutionMode.RUN_CODEX),
                token_budget=replace(
                    supervised.token_budget,
                    max_prompt_tokens=30,
                    max_context_tokens=30,
                    min_remaining_tokens=20,
                ),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=successful_workflow_runner(calls, root=root, prompt_text="x" * 80),
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "TOKEN_BUDGET_FAILURE")
            self.assertEqual(gates[0]["name"], "token_budget_gate")
            self.assertEqual(gates[0]["status"], "fail")
            self.assertEqual(
                gates[0]["details"]["token_budget"]["code"],
                "TOKEN_BUDGET_LOW_REMAINING",
            )
            self.assertEqual(len(gates), 1)

    def test_execute_blocks_on_stale_protected_outputs_before_token_budget_and_codex(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="run_codex_stale_protected_outputs_test",
                codex=replace(supervised.codex, mode=CodexExecutionMode.RUN_CODEX),
                token_budget=replace(
                    supervised.token_budget,
                    max_prompt_tokens=30,
                    max_context_tokens=30,
                    min_remaining_tokens=20,
                ),
            )
            session = create_session(root=root, actor="tester", policy=policy)
            prompt_path = root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"
            prompt_text = "Source ID: TASK-001\n\n" + ("x" * 80)
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text(prompt_text, encoding="utf-8")
            prompt_sha256 = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
            prepared = record_phase_result(
                session.data["session_id"],
                PhaseResult.passed(
                    "prepare",
                    reason="Task prepared for execute regression.",
                    next_action="Run pipeline phase execute.",
                    artifacts={
                        "session_id": session.data["session_id"],
                        "task_id": "TASK-001",
                        "prompt_path": "AI_PROJECT/generated/CODEX_PROMPT.md",
                        "prompt_sha256": prompt_sha256,
                    },
                ),
                root=root,
                actor="tester",
                task_id="TASK-001",
                command="pipeline.phase.prepare",
            )
            self.assertTrue(prepared.ok)
            calls = []

            def fake_runner(argv):
                args = list(argv)
                calls.append(args)
                if tuple(args[-2:]) == ("project", "protected-check"):
                    return completed(
                        stdout=json.dumps(
                            {
                                "ok": False,
                                "errors": [
                                    "OUTDATED_GENERATED_FILE: AI_PROJECT/generated/DOCS_GAPS.md"
                                ],
                                "warnings": [],
                                "checked": ["generated output check reached"],
                            }
                        )
                        + "\n",
                        returncode=1,
                    )
                if args == ["codex", "exec"]:
                    raise AssertionError("Codex adapter must not be called")
                raise AssertionError("unexpected command: {}".format(args))

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=fake_runner,
            )
            latest = load_pipeline(root)["sessions"][0]
            execute = latest["phase_history"][-1]
            artifacts = execute["artifacts"]
            protected_check = artifacts["protected_check"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["dispatched_phase"], "execute")
            self.assertEqual(result.data["stop_code"], "PROTECTED_GENERATED_FRESHNESS_FAILED")
            self.assertEqual(execute["phase"], "execute")
            self.assertEqual(execute["status"], "blocked")
            self.assertEqual(
                artifacts["blocked_by"],
                "PROTECTED_GENERATED_FRESHNESS_FAILED",
            )
            self.assertFalse(artifacts["codex_adapter_called"])
            self.assertNotIn("token_budget", artifacts)
            self.assertEqual(protected_check["returncode"], 1)
            self.assertEqual(tuple(protected_check["command"][-2:]), ("project", "protected-check"))
            self.assertIn("OUTDATED_GENERATED_FILE", protected_check["errors"][0])
            self.assertFalse(any(call == ["codex", "exec"] for call in calls))

    def test_execute_continues_to_token_budget_and_adapter_when_protected_check_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised")
            policy = replace(
                supervised,
                name="run_codex_protected_check_pass_test",
                codex=replace(supervised.codex, mode=CodexExecutionMode.RUN_CODEX),
            )
            session = create_session(root=root, actor="tester", policy=policy)
            prompt_path = root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"
            prompt_text = "Source ID: TASK-001\n\nSmall prompt."
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text(prompt_text, encoding="utf-8")
            prompt_sha256 = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
            prepared = record_phase_result(
                session.data["session_id"],
                PhaseResult.passed(
                    "prepare",
                    reason="Task prepared for protected pass regression.",
                    next_action="Run pipeline phase execute.",
                    artifacts={
                        "session_id": session.data["session_id"],
                        "task_id": "TASK-001",
                        "prompt_path": "AI_PROJECT/generated/CODEX_PROMPT.md",
                        "prompt_sha256": prompt_sha256,
                    },
                ),
                root=root,
                actor="tester",
                task_id="TASK-001",
                command="pipeline.phase.prepare",
            )
            self.assertTrue(prepared.ok)
            calls = []
            adapter_called = {"value": False}

            def fake_runner(argv):
                args = list(argv)
                calls.append(args)
                if tuple(args[-2:]) == ("project", "protected-check"):
                    return completed(
                        stdout=json.dumps(
                            {
                                "ok": True,
                                "errors": [],
                                "warnings": [],
                                "checked": ["protected files are fresh"],
                            }
                        )
                        + "\n"
                    )
                raise AssertionError("unexpected command: {}".format(args))

            def fake_adapter(**kwargs):
                adapter_called["value"] = True
                token_gate = kwargs["token_gate"]
                return CodexAdapterResult(
                    status="blocked",
                    code="TEST_ADAPTER_REACHED",
                    reason="adapter_reached_after_protected_check",
                    mode="test",
                    started_at="2026-06-26T00:00:00Z",
                    finished_at="2026-06-26T00:00:00Z",
                    duration_sec=0.0,
                    prompt_path=token_gate.prompt_path,
                    prompt_sha256=token_gate.prompt_sha256,
                )

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=fake_runner,
                codex_adapter=fake_adapter,
            )
            latest = load_pipeline(root)["sessions"][0]
            execute = latest["phase_history"][-1]
            artifacts = execute["artifacts"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "TEST_ADAPTER_REACHED")
            self.assertTrue(adapter_called["value"])
            self.assertTrue(artifacts["codex_adapter_called"])
            self.assertIn("token_budget", artifacts)
            self.assertEqual(artifacts["adapter"]["code"], "TEST_ADAPTER_REACHED")
            self.assertTrue(any(tuple(call[-2:]) == ("project", "protected-check") for call in calls))

    def test_autoclose_policy_blocks_build_prompt_only_session_without_owner_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            result = create_session(
                root=root,
                actor="tester",
                policy_name="supervised_autoclose",
            )

            self.assertFalse(result.ok)
            self.assertEqual(
                result.errors[0].code,
                "PIPELINE_AUTO_CLOSE_OWNER_NOTE_REQUIRED",
            )
            self.assertFalse(pipeline_state_path(root).exists())

    def test_local_commit_policy_commits_after_close_and_green_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="accepted")
            supervised = policy_preset("supervised_local_commit")
            policy = replace(
                supervised,
                name="run_codex_local_commit_test",
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                ),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=committing_workflow_runner(calls, root=root),
                codex_reviewer=lambda prompt: valid_review_output(),
            )
            latest = load_pipeline(root)["sessions"][0]
            gates = latest["steps"][0]["gate_outcomes"]
            git_calls = [call for call in calls if call and call[0] == "git"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "LOCAL_COMMIT_CREATED")
            self.assertEqual(gates[5]["name"], "review_close_gate")
            self.assertEqual(gates[5]["status"], "pass")
            self.assertEqual(gates[6]["name"], "commit_gate")
            self.assertEqual(gates[6]["status"], "pass")
            self.assertEqual(latest["commit_ids"], ["abc1234deadbeef"])
            self.assertEqual(git_calls[0], ["git", "status", "--short", "--untracked-files=all"])
            self.assertEqual(git_calls[1], ["git", "add", "--", "ai_project_ctl/pipeline/report_gate.py"])
            self.assertEqual(git_calls[2][:3], ["git", "commit", "-m"])
            self.assertEqual(git_calls[3], ["git", "rev-parse", "--verify", "HEAD"])
            self.assertFalse(any("push" in call for call in git_calls))
            self.assertFalse(any("reset" in call for call in git_calls))

    def test_commit_readiness_allows_warn_report_gate_when_policy_allows_advisory_warnings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="accepted")
            _write_task_status(root, "done")
            supervised = policy_preset("supervised_local_commit")
            policy = replace(
                supervised,
                verify=replace(
                    supervised.verify,
                    allow_report_warnings=True,
                    block_report_warnings=False,
                ),
            )
            git_calls = []

            def git_status_runner(argv):
                git_calls.append(list(argv))
                return completed(stdout=" M ai_project_ctl/pipeline/report_gate.py\n")

            result = evaluate_commit_readiness(
                root=root,
                task_id="TASK-001",
                policy=policy,
                report_gate=warning_report_gate(),
                machine_review=passing_machine_review(),
                codex_review=approved_codex_review(),
                runner=git_status_runner,
            )

            self.assertTrue(result.ok)
            self.assertEqual(result.code, COMMIT_READINESS_PASS)
            self.assertEqual(
                git_calls,
                [["git", "status", "--short", "--untracked-files=all"]],
            )
            self.assertEqual(
                result.approved_files,
                ("ai_project_ctl/pipeline/report_gate.py",),
            )

    def test_commit_readiness_blocks_warn_report_gate_when_policy_disallows_advisory_warnings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="accepted")
            _write_task_status(root, "done")

            def git_status_runner(argv):
                raise AssertionError("git status should not run after report gate blocker")

            result = evaluate_commit_readiness(
                root=root,
                task_id="TASK-001",
                policy=policy_preset("supervised_local_commit"),
                report_gate=warning_report_gate(),
                machine_review=passing_machine_review(),
                codex_review=approved_codex_review(),
                runner=git_status_runner,
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.code, COMMIT_REPORT_NOT_PASS)
            self.assertIn("policy.verify.allow_report_warnings is false", result.reason)

    def test_commit_readiness_blocks_report_failure_even_when_warning_policy_allows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="accepted")
            _write_task_status(root, "done")
            supervised = policy_preset("supervised_local_commit")
            policy = replace(
                supervised,
                verify=replace(
                    supervised.verify,
                    allow_report_warnings=True,
                    block_report_warnings=False,
                ),
            )

            def git_status_runner(argv):
                raise AssertionError("git status should not run after report gate blocker")

            for status in ("fail", "blocked"):
                with self.subTest(status=status):
                    result = evaluate_commit_readiness(
                        root=root,
                        task_id="TASK-001",
                        policy=policy,
                        report_gate=blocking_report_gate(status),
                        machine_review=passing_machine_review(),
                        codex_review=approved_codex_review(),
                        runner=git_status_runner,
                    )

                    self.assertFalse(result.ok)
                    self.assertEqual(result.code, COMMIT_REPORT_NOT_PASS)
                    self.assertIn("Report gate {} should block".format(status), result.reason)

    def test_local_commit_stages_current_session_governed_side_effects(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="accepted")
            _write_task_status(root, "done")
            artifact = "ai_project_ctl/pipeline/report_gate.py"
            governed_changed = (
                "AI_PROJECT/state/tasks.json",
                "AI_PROJECT/events/task-events.jsonl",
                "AI_PROJECT/state/task_reports.json",
                "AI_PROJECT/events/task-report-events.jsonl",
                "AI_PROJECT/state/current_execution.json",
                "AI_PROJECT/events/codex-events.jsonl",
                "AI_PROJECT/events/context-events.jsonl",
                "AI_PROJECT/state/evolution.json",
                "AI_PROJECT/events/evolution-events.jsonl",
                "AI_PROJECT/state/pipeline_sessions.json",
                "AI_PROJECT/events/pipeline-events.jsonl",
            )
            governed_generated = (
                "AI_PROJECT/generated/CODEX_CURRENT.md",
                "AI_PROJECT/generated/CODEX_STATUS.md",
                "AI_PROJECT/generated/CODEX_TASKS.md",
                "AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md",
                "AI_PROJECT/generated/CONTEXT_PACK.md",
                "AI_PROJECT/generated/CONTEXT_STATUS.md",
                "AI_PROJECT/generated/EVOLUTION.md",
                "AI_PROJECT/generated/PIPELINE_STATUS.md",
                "AI_PROJECT/generated/PIPELINE_AUDIT.md",
            )
            approved_paths = (artifact, *governed_changed, *governed_generated)
            calls = []

            def git_runner(argv):
                args = list(argv)
                calls.append(args)
                if args == ["git", "status", "--short", "--untracked-files=all"]:
                    return completed(
                        stdout="".join(" M {}\n".format(path) for path in approved_paths)
                    )
                if args[:3] == ["git", "add", "--"]:
                    return completed(stdout="")
                if args[:3] == ["git", "commit", "-m"]:
                    return completed(stdout="[main abc1234] pipeline commit\n")
                if args == ["git", "rev-parse", "--verify", "HEAD"]:
                    return completed(stdout="abc1234deadbeef\n")
                return completed(returncode=1, stderr="unexpected git command\n")

            result = run_local_commit(
                root=root,
                task_id="TASK-001",
                session_id="PSESS-001",
                policy=policy_preset("supervised_local_commit"),
                report_gate=passing_report_gate(changed_files=(artifact,)),
                machine_review=passing_machine_review(),
                codex_review=approved_codex_review(),
                side_effects=(
                    governed_side_effect(
                        changed_files=governed_changed,
                        generated_files=governed_generated,
                    ),
                ),
                session={
                    "id": "PSESS-001",
                    "file_evidence": {
                        "pre_existing_dirty_files": [],
                        "session_owned_changed_files": [
                            *governed_changed,
                            *governed_generated,
                        ],
                    },
                },
                runner=git_runner,
            )

            expected_staged = tuple(sorted(approved_paths))
            self.assertTrue(result.ok)
            self.assertEqual(result.code, "LOCAL_COMMIT_CREATED")
            self.assertEqual(result.staged_files, expected_staged)
            self.assertEqual(result.readiness.approved_files, expected_staged)
            self.assertEqual(calls[1], ["git", "add", "--", *expected_staged])

    def test_commit_readiness_blocks_pre_existing_governed_side_effect_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="accepted")
            _write_task_status(root, "done")
            artifact = "ai_project_ctl/pipeline/report_gate.py"
            governed = "AI_PROJECT/state/tasks.json"

            result = evaluate_commit_readiness(
                root=root,
                task_id="TASK-001",
                policy=policy_preset("supervised_local_commit"),
                report_gate=passing_report_gate(changed_files=(artifact,)),
                machine_review=passing_machine_review(),
                codex_review=approved_codex_review(),
                side_effects=(governed_side_effect(changed_files=(governed,)),),
                session={
                    "id": "PSESS-001",
                    "file_evidence": {
                        "pre_existing_dirty_files": [governed],
                        "session_owned_changed_files": [],
                    },
                },
                runner=lambda argv: completed(
                    stdout=" M {}\n M {}\n".format(artifact, governed)
                ),
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.code, "COMMIT_UNRELATED_FILES")
            self.assertIn(governed, result.blockers)

    def test_commit_readiness_blocks_non_session_owned_ai_project_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="accepted")
            _write_task_status(root, "done")
            artifact = "ai_project_ctl/pipeline/report_gate.py"
            owned = "AI_PROJECT/state/tasks.json"
            unrelated = "AI_PROJECT/generated/DOCS_INDEX.md"

            result = evaluate_commit_readiness(
                root=root,
                task_id="TASK-001",
                policy=policy_preset("supervised_local_commit"),
                report_gate=passing_report_gate(changed_files=(artifact,)),
                machine_review=passing_machine_review(),
                codex_review=approved_codex_review(),
                side_effects=(governed_side_effect(changed_files=(owned,)),),
                session={
                    "id": "PSESS-001",
                    "file_evidence": {
                        "pre_existing_dirty_files": [],
                        "session_owned_changed_files": [owned],
                    },
                },
                runner=lambda argv: completed(
                    stdout=" M {}\n M {}\n M {}\n".format(
                        artifact,
                        owned,
                        unrelated,
                    )
                ),
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.code, "COMMIT_UNRELATED_FILES")
            self.assertIn(unrelated, result.blockers)

    def test_commit_readiness_blocks_governed_only_session_side_effects(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="accepted")
            _write_task_status(root, "done")
            governed = "AI_PROJECT/state/tasks.json"

            result = evaluate_commit_readiness(
                root=root,
                task_id="TASK-001",
                policy=policy_preset("supervised_local_commit"),
                report_gate=passing_report_gate(changed_files=()),
                machine_review=passing_machine_review(),
                codex_review=approved_codex_review(),
                side_effects=(governed_side_effect(changed_files=(governed,)),),
                session={
                    "id": "PSESS-001",
                    "file_evidence": {
                        "pre_existing_dirty_files": [],
                        "session_owned_changed_files": [governed],
                    },
                },
                runner=lambda argv: completed(stdout=" M {}\n".format(governed)),
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.code, "COMMIT_UNRELATED_FILES")
            self.assertEqual(result.blockers, ("target_task_artifact_missing",))

    def test_local_commit_blocks_until_linked_change_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="approved")
            supervised = policy_preset("supervised_local_commit")
            policy = replace(
                supervised,
                name="run_codex_local_commit_change_gate_test",
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                ),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=committing_workflow_runner(calls, root=root),
                codex_reviewer=lambda prompt: valid_review_output(),
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]
            git_calls = [call for call in calls if call and call[0] == "git"]
            commit = gates[6]["details"]["commit"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "COMMIT_READINESS_FAILED")
            self.assertEqual(gates[6]["name"], "commit_gate")
            self.assertEqual(gates[6]["status"], "blocked")
            self.assertEqual(commit["readiness"]["code"], "COMMIT_CHANGE_NOT_ACCEPTED")
            self.assertEqual(git_calls, [])

    def test_local_commit_refuses_unapproved_dirty_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root, change_status="accepted")
            supervised = policy_preset("supervised_local_commit")
            policy = replace(
                supervised,
                name="run_codex_local_commit_unrelated_files_test",
                codex=replace(
                    supervised.codex,
                    mode=CodexExecutionMode.RUN_CODEX,
                    adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                    local_command=("codex", "exec"),
                    command_allowlist=("codex exec",),
                ),
            )
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                auto_close_note="Owner approved auto-close for this test session.",
            )
            calls = []

            result = run_next(
                session.data["session_id"],
                root=root,
                actor="tester",
                runner=committing_workflow_runner(
                    calls,
                    root=root,
                    git_status_stdout=(
                        " M ai_project_ctl/pipeline/report_gate.py\n"
                        " M README.md\n"
                    ),
                ),
                codex_reviewer=lambda prompt: valid_review_output(),
            )
            gates = load_pipeline(root)["sessions"][0]["steps"][0]["gate_outcomes"]
            git_calls = [call for call in calls if call and call[0] == "git"]
            commit = gates[6]["details"]["commit"]

            self.assertTrue(result.ok)
            self.assertEqual(result.data["stop_code"], "COMMIT_READINESS_FAILED")
            self.assertEqual(commit["readiness"]["code"], "COMMIT_UNRELATED_FILES")
            self.assertIn("README.md", commit["readiness"]["blockers"])
            self.assertEqual(git_calls, [["git", "status", "--short", "--untracked-files=all"]])


if __name__ == "__main__":
    unittest.main()

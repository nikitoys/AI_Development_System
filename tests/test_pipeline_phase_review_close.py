import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from ai_project_ctl.core import workflows as workflow_module
from ai_project_ctl.pipeline import policy_preset
from ai_project_ctl.pipeline.close_phase import close_phase
from ai_project_ctl.pipeline.codex_adapter import (
    CODE_LOCAL_COMMAND_PASSED,
    CodexAdapterResult,
)
from ai_project_ctl.pipeline.git_commit import (
    CODE_COMMIT_CREATED,
    CODE_MACHINE_REVIEW_NOT_PASS,
    CODE_READY as COMMIT_READINESS_PASS,
    GitCommandResult,
    REQUIRED_MACHINE_CHECKS,
)
from ai_project_ctl.pipeline.machine_review import (
    MachineCheckEvidence,
    MachineReviewResult,
)
from ai_project_ctl.pipeline.phase import PhaseResult
from ai_project_ctl.pipeline.report_gate import ReportGateResult
from ai_project_ctl.pipeline.review_phase import review_phase
from ai_project_ctl.pipeline.runner import run_next
from ai_project_ctl.pipeline.session import (
    create_session,
    record_phase_result,
    validate_sessions,
)
from ai_project_ctl.pipeline.state import MAX_STORED_STRING_LENGTH, pipeline_state_path
from ai_project_ctl.task_reports import submit_task_report


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
TASK_ID = "TASK-001"
CHANGED_FILE = "tests/test_pipeline_phase_review_close.py"
CONTEXT_PACK_FILE = "AI_PROJECT/generated/CONTEXT_PACK.md"
CONTEXT_STATUS_FILE = "AI_PROJECT/generated/CONTEXT_STATUS.md"
CONTEXT_EVENT_FILE = "AI_PROJECT/events/context-events.jsonl"
OWNER_APPROVAL_NOTE = "Owner approved auto-close for this temp session."


class PipelinePhaseReviewCloseTests(unittest.TestCase):
    def test_fake_reviewer_approve_reaches_governed_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_temp_project(root)
            policy = policy_preset("supervised_executable_autoclose")
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                task_refs=(TASK_ID,),
                max_tasks=1,
                order_by="selected",
                auto_close_note=OWNER_APPROVAL_NOTE,
            )
            self.assertTrue(session.ok, session.errors)
            session_id = str(session.data["session_id"])

            _run_git(root, "init")
            _commit_paths(root, ".", message="baseline temp project")

            adapter_calls = []

            def fake_codex_adapter(**kwargs):
                adapter_calls.append(kwargs)
                changed = root / CHANGED_FILE
                changed.parent.mkdir(parents=True, exist_ok=True)
                changed.write_text("fake implementation evidence\n", encoding="utf-8")
                task = _task(root)
                token_gate = kwargs["token_gate"]
                submission = submit_task_report(
                    root=root,
                    tasks_state=_read_tasks_state(root),
                    task=task,
                    report_payload=_report_payload(
                        token_gate.to_dict(),
                        task_ref=str(task.get("ref") or TASK_ID),
                    ),
                    source_file="captured:fake-codex-report",
                    actor="fake_codex",
                    command="fake.codex.report.submit",
                )
                policy = kwargs["policy"]
                return CodexAdapterResult(
                    status="passed",
                    code=CODE_LOCAL_COMMAND_PASSED,
                    reason="fake_codex_wrote_allowed_file_and_report",
                    mode=policy.codex.adapter_mode.value,
                    started_at="2026-06-25T00:00:00Z",
                    finished_at="2026-06-25T00:00:01Z",
                    duration_sec=1.0,
                    prompt_path=token_gate.prompt_path,
                    prompt_sha256=token_gate.prompt_sha256,
                    prompt_transport=policy.codex.prompt_transport.value,
                    command=("fake-codex", "exec"),
                    command_ref="fake-codex exec",
                    timeout_sec=policy.codex.timeout_sec,
                    returncode=0,
                    stdout_ref="captured:stdout:sha256:fake",
                    stderr_ref="captured:stderr:sha256:fake",
                    stdout_snippet="fake report submitted",
                    stderr_snippet="",
                    stdout_bytes=21,
                    stderr_bytes=0,
                    runtime_logs={},
                    before_report_id="",
                    after_report_id=submission.report_id,
                    report_id=submission.report_id,
                )

            for expected_phase in (
                "queue_preview",
                "prepare",
                "execute",
                "collect_report",
            ):
                runner = (
                    _protected_check_pass_runner
                    if expected_phase == "execute"
                    else None
                )
                result = run_next(
                    session_id,
                    root=root,
                    actor="tester",
                    runner=runner,
                    codex_adapter=fake_codex_adapter,
                )
                self.assertTrue(result.ok, result.errors)
                self.assertEqual(result.data["dispatched_phase"], expected_phase)
                self.assertEqual(result.data["phase_status"], "passed")

            self.assertEqual(len(adapter_calls), 1)
            _commit_paths(
                root,
                "AI_PROJECT",
                message="baseline governed pipeline evidence",
            )

            verify = run_next(
                session_id,
                root=root,
                actor="tester",
                codex_adapter=fake_codex_adapter,
            )
            self.assertTrue(verify.ok, verify.errors)
            self.assertEqual(verify.data["dispatched_phase"], "verify")
            self.assertEqual(verify.data["phase_status"], "passed")

            verify_artifacts = verify.data["phase_result"]["artifacts"]
            reviewer = _write_fake_reviewer(
                root,
                report_id=str(verify_artifacts["report_id"]),
            )
            review = review_phase(
                session_id,
                root=root,
                actor="tester",
                reviewer_command=(sys.executable, str(reviewer)),
            )
            self.assertTrue(review.ok, review.errors)
            self.assertEqual(review.data["verdict"], "APPROVE")
            self.assertTrue(review.data["review_id"].startswith("CREV-"))

            with mock.patch.object(
                workflow_module.WorkflowExecutor,
                "_run_subprocess",
                _workflow_subprocess_with_oversized_doctor_output,
            ):
                close = close_phase(
                    session_id,
                    root=root,
                    actor="tester",
                    confirmed=True,
                )
            self.assertTrue(close.ok, close.errors)
            self.assertTrue(close.data["preflight_passed"])
            self.assertEqual(close.data["missing_gates"], [])

            task = _task(root)
            self.assertEqual(task["status"], "done")

            latest = _pipeline_session(root)
            history = latest["phase_history"]
            self.assertEqual(
                [(item["phase"], item["status"]) for item in history],
                [
                    ("queue_preview", "passed"),
                    ("prepare", "passed"),
                    ("execute", "passed"),
                    ("collect_report", "passed"),
                    ("verify", "passed"),
                    ("review", "passed"),
                    ("close", "passed"),
                ],
            )
            review_artifacts = history[-2]["artifacts"]
            close_artifacts = history[-1]["artifacts"]
            review_id = review_artifacts["review_id"]
            self.assertEqual(review_id, review.data["review_id"])
            self.assertEqual(
                close_artifacts["phase_statuses"]["review"]["review_id"],
                review_id,
            )
            self.assertTrue(close_artifacts["preflight_passed"])
            self.assertEqual(close_artifacts["missing_gates"], [])
            self.assertEqual(
                close_artifacts["close_workflow"]["data"]["decision"]["action"],
                "close_task",
            )
            doctor_steps = _workflow_steps_by_id(
                close_artifacts["close_workflow"],
                "doctor",
            )
            self.assertTrue(doctor_steps)
            doctor_step = doctor_steps[0]
            self.assertEqual(doctor_step["command_name"], "project.doctor")
            self.assertEqual(doctor_step["returncode"], 0)
            self.assertEqual(doctor_step["stdout"]["field"], "stdout")
            self.assertEqual(doctor_step["stderr"]["field"], "stderr")
            self.assertTrue(doctor_step["stdout"]["truncated"])
            self.assertTrue(doctor_step["stderr"]["truncated"])
            self.assertGreater(
                doctor_step["stdout"]["original_size"],
                MAX_STORED_STRING_LENGTH,
            )
            self.assertGreater(
                doctor_step["stderr"]["original_size"],
                MAX_STORED_STRING_LENGTH,
            )
            raw_pipeline_state = pipeline_state_path(root).read_text(encoding="utf-8")
            self.assertNotIn(_oversized_text("stdout"), raw_pipeline_state)
            self.assertNotIn(_oversized_text("stderr"), raw_pipeline_state)
            self.assertTrue(validate_sessions(root=root).ok)
            _run_script(root, "aictl.py", "pipeline", "validate")
            self.assertEqual(
                close_artifacts["close_policy"]["auto_close_task"],
                True,
            )

    def test_close_retry_recovers_already_done_task_with_matching_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_temp_project(root)
            session_id = _create_close_session(root)
            _record_close_preflight_history(root, session_id)
            _mark_task_done(root, notes=OWNER_APPROVAL_NOTE)

            with mock.patch(
                "ai_project_ctl.pipeline.close_phase.run_review_close_workflow",
                side_effect=AssertionError("close retry must not rerun task workflows"),
            ):
                close = close_phase(
                    session_id,
                    root=root,
                    actor="tester",
                    confirmed=True,
                )

            self.assertTrue(close.ok, close.errors)
            artifacts = close.data["phase_result"]["artifacts"]
            self.assertTrue(artifacts["preflight_passed"])
            self.assertTrue(artifacts["already_closed_by_previous_attempt"])
            self.assertEqual(
                artifacts["close_recovery"]["code"],
                "TASK_ALREADY_CLOSED_BY_PREVIOUS_ATTEMPT",
            )
            self.assertEqual(
                artifacts["close_recovery"]["skipped_workflows"],
                ["task.submit_for_review", "task.close_reviewed"],
            )
            self.assertEqual(artifacts["close_workflow"]["data"]["workflows"], [])
            self.assertEqual(
                artifacts["change_acceptance"]["accepted_change_ids"],
                ["CHG-001"],
            )
            self.assertEqual(_task(root)["status"], "done")
            self.assertEqual(_change(root, "CHG-001")["status"], "accepted")

    def test_close_retry_blocks_done_task_without_approval_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_temp_project(root)
            session_id = _create_close_session(root)
            _record_close_preflight_history(root, session_id)
            _mark_task_done(root, notes="")

            with mock.patch(
                "ai_project_ctl.pipeline.close_phase.run_review_close_workflow",
                side_effect=AssertionError("blocked retry must not rerun task workflows"),
            ):
                close = close_phase(
                    session_id,
                    root=root,
                    actor="tester",
                    confirmed=True,
                )

            self.assertTrue(close.ok, close.errors)
            phase_result = close.data["phase_result"]
            self.assertEqual(phase_result["status"], "blocked")
            artifacts = phase_result["artifacts"]
            self.assertEqual(artifacts["blocked_by"], "CLOSE_WORKFLOW_BLOCKED")
            self.assertFalse(artifacts["already_closed_by_previous_attempt"])
            self.assertEqual(
                artifacts["close_recovery"]["code"],
                "TASK_ALREADY_DONE_APPROVAL_EVIDENCE_MISSING",
            )
            self.assertEqual(artifacts["close_workflow"]["data"]["workflows"], [])

    def test_close_local_commit_allows_policy_approved_machine_review_warn(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_temp_project(root)
            _prepare_auto_close_workflow(root)
            session_id = _create_close_session(
                root,
                policy=_local_commit_warning_policy(),
            )
            _record_close_preflight_history(root, session_id)
            report_gate = _warning_report_gate()
            machine_review = _machine_review_with_warning(
                MachineCheckEvidence(
                    name="codex_report_gate",
                    status="warn",
                    code="CODEX_REPORT_WARN",
                    reason="Report warning is policy-approved for commit readiness.",
                    blocking=True,
                )
            )
            git_commands: list[list[str]] = []

            with (
                mock.patch.object(
                    workflow_module.WorkflowExecutor,
                    "_run_subprocess",
                    _workflow_subprocess_with_oversized_doctor_output,
                ),
                mock.patch(
                    "ai_project_ctl.pipeline.close_phase.evaluate_report_gate",
                    return_value=report_gate,
                ),
                mock.patch(
                    "ai_project_ctl.pipeline.close_phase.evaluate_machine_review",
                    return_value=machine_review,
                ),
                mock.patch(
                    "ai_project_ctl.pipeline.git_commit.run_git_command",
                    side_effect=_fake_git_command_runner(git_commands),
                ),
            ):
                close = close_phase(
                    session_id,
                    root=root,
                    actor="tester",
                    confirmed=True,
                )

            self.assertTrue(close.ok, close.errors)
            phase_result = close.data["phase_result"]
            self.assertEqual(phase_result["status"], "passed")
            artifacts = phase_result["artifacts"]
            local_commit = artifacts["local_commit"]
            self.assertEqual(local_commit["status"], "pass")
            self.assertEqual(local_commit["code"], CODE_COMMIT_CREATED)
            self.assertEqual(local_commit["readiness"]["status"], "pass")
            self.assertEqual(
                local_commit["readiness"]["code"],
                COMMIT_READINESS_PASS,
            )
            self.assertEqual(local_commit["commit_hash"], "abc1234deadbeef")
            self.assertNotIn(
                CODE_MACHINE_REVIEW_NOT_PASS,
                json.dumps(artifacts, sort_keys=True),
            )
            self.assertEqual(
                git_commands,
                [
                    ["git", "status", "--short", "--untracked-files=all"],
                    ["git", "add", "--", CHANGED_FILE],
                    ["git", "commit", "-m", local_commit["message"]],
                    ["git", "rev-parse", "--verify", "HEAD"],
                ],
            )

    def test_close_local_commit_refreshes_context_before_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_temp_project(root)
            _prepare_auto_close_workflow(root)
            session_id = _create_close_session(
                root,
                policy=_local_commit_warning_policy(),
            )
            _record_close_preflight_history(root, session_id)
            report_gate = _warning_report_gate()
            machine_review = _machine_review_with_warning(
                MachineCheckEvidence(
                    name="codex_report_gate",
                    status="warn",
                    code="CODEX_REPORT_WARN",
                    reason="Report warning is policy-approved for commit readiness.",
                    blocking=True,
                )
            )
            git_commands: list[list[str]] = []
            git_status_stdout = (
                " M {}\n"
                " M {}\n"
                " M {}\n"
                " M {}\n"
            ).format(
                CHANGED_FILE,
                CONTEXT_PACK_FILE,
                CONTEXT_STATUS_FILE,
                CONTEXT_EVENT_FILE,
            )

            def assert_context_refreshed() -> None:
                pack_text = (root / CONTEXT_PACK_FILE).read_text(encoding="utf-8")
                self.assertNotIn("Status: `in_progress`", pack_text)
                self.assertIn("Status: `done`", pack_text)

            with (
                mock.patch.object(
                    workflow_module.WorkflowExecutor,
                    "_run_subprocess",
                    _workflow_subprocess_with_oversized_doctor_output,
                ),
                mock.patch(
                    "ai_project_ctl.pipeline.close_phase.evaluate_report_gate",
                    return_value=report_gate,
                ),
                mock.patch(
                    "ai_project_ctl.pipeline.close_phase.evaluate_machine_review",
                    return_value=machine_review,
                ),
                mock.patch(
                    "ai_project_ctl.pipeline.git_commit.run_git_command",
                    side_effect=_fake_git_command_runner(
                        git_commands,
                        git_status_stdout=git_status_stdout,
                        before_git_status=assert_context_refreshed,
                    ),
                ),
            ):
                close = close_phase(
                    session_id,
                    root=root,
                    actor="tester",
                    confirmed=True,
                )

            self.assertTrue(close.ok, close.errors)
            phase_result = close.data["phase_result"]
            self.assertEqual(phase_result["status"], "passed")
            artifacts = phase_result["artifacts"]
            self.assertTrue(artifacts["context_refresh"]["ok"])
            local_commit = artifacts["local_commit"]
            self.assertEqual(local_commit["status"], "pass")
            self.assertEqual(local_commit["readiness"]["code"], COMMIT_READINESS_PASS)
            self.assertEqual(
                sorted(local_commit["readiness"]["approved_files"]),
                sorted(
                    [
                        CHANGED_FILE,
                        CONTEXT_EVENT_FILE,
                        CONTEXT_PACK_FILE,
                        CONTEXT_STATUS_FILE,
                    ]
                ),
            )
            self.assertEqual(
                git_commands[1],
                [
                    "git",
                    "add",
                    "--",
                    CONTEXT_EVENT_FILE,
                    CONTEXT_PACK_FILE,
                    CONTEXT_STATUS_FILE,
                    CHANGED_FILE,
                ],
            )

    def test_close_blocks_when_context_refresh_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_temp_project(root)
            _prepare_auto_close_workflow(root)
            session_id = _create_close_session(root)
            _record_close_preflight_history(root, session_id)

            def fail_context_build(
                argv: tuple[str, ...],
                *,
                root: Path,
            ) -> subprocess.CompletedProcess[str]:
                return subprocess.CompletedProcess(
                    args=list(argv),
                    returncode=1,
                    stdout="",
                    stderr="context build failed\n",
                )

            with (
                mock.patch.object(
                    workflow_module.WorkflowExecutor,
                    "_run_subprocess",
                    _workflow_subprocess_with_oversized_doctor_output,
                ),
                mock.patch(
                    "ai_project_ctl.pipeline.close_phase._run_context_refresh_command",
                    side_effect=fail_context_build,
                ),
            ):
                close = close_phase(
                    session_id,
                    root=root,
                    actor="tester",
                    confirmed=True,
                )

            self.assertTrue(close.ok, close.errors)
            phase_result = close.data["phase_result"]
            self.assertEqual(phase_result["status"], "blocked")
            artifacts = phase_result["artifacts"]
            self.assertEqual(artifacts["blocked_by"], "CLOSE_CONTEXT_REFRESH_FAILED")
            context_refresh = artifacts["context_refresh"]
            self.assertFalse(context_refresh["ok"])
            self.assertEqual(context_refresh["data"]["failed_step"], "context_build")
            self.assertEqual(
                context_refresh["errors"][0]["code"],
                "CLOSE_CONTEXT_REFRESH_FAILED",
            )
            self.assertEqual(
                context_refresh["errors"][0]["details"]["stderr"],
                "context build failed\n",
            )

    def test_close_local_commit_blocks_unsafe_machine_review_warn(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_temp_project(root)
            _prepare_auto_close_workflow(root)
            session_id = _create_close_session(
                root,
                policy=_local_commit_warning_policy(),
            )
            _record_close_preflight_history(root, session_id)
            report_gate = _warning_report_gate()
            machine_review = _machine_review_with_warning(
                MachineCheckEvidence(
                    name="unapproved_commit_warning",
                    status="warn",
                    code="UNAPPROVED_COMMIT_WARNING",
                    reason="Blocking Machine Review warning is not policy-approved.",
                    blocking=True,
                )
            )
            git_commands: list[list[str]] = []

            with (
                mock.patch.object(
                    workflow_module.WorkflowExecutor,
                    "_run_subprocess",
                    _workflow_subprocess_with_oversized_doctor_output,
                ),
                mock.patch(
                    "ai_project_ctl.pipeline.close_phase.evaluate_report_gate",
                    return_value=report_gate,
                ),
                mock.patch(
                    "ai_project_ctl.pipeline.close_phase.evaluate_machine_review",
                    return_value=machine_review,
                ),
                mock.patch(
                    "ai_project_ctl.pipeline.git_commit.run_git_command",
                    side_effect=_fake_git_command_runner(git_commands),
                ),
            ):
                close = close_phase(
                    session_id,
                    root=root,
                    actor="tester",
                    confirmed=True,
                )

            self.assertTrue(close.ok, close.errors)
            phase_result = close.data["phase_result"]
            self.assertEqual(phase_result["status"], "blocked")
            artifacts = phase_result["artifacts"]
            local_commit = artifacts["local_commit"]
            self.assertEqual(local_commit["status"], "blocked")
            self.assertEqual(local_commit["code"], "COMMIT_READINESS_FAILED")
            self.assertEqual(
                local_commit["readiness"]["code"],
                CODE_MACHINE_REVIEW_NOT_PASS,
            )
            self.assertEqual(git_commands, [])

    def test_close_local_commit_artifacts_include_context_check_generated_diagnostics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_temp_project(root)
            _prepare_auto_close_workflow(root)
            session_id = _create_close_session(
                root,
                policy=_local_commit_warning_policy(),
            )
            _record_close_preflight_history(root, session_id)
            report_gate = ReportGateResult(
                status="pass",
                code="CODEX_REPORT_PASS",
                reason="Report gate passed.",
                report_id="RPT-001",
                task_id=TASK_ID,
                changed_files=(CHANGED_FILE,),
            )
            machine_review = _machine_review_with_context_check_failure(
                stdout_summary=(
                    "context stdout "
                    + ("x" * (MAX_STORED_STRING_LENGTH + 1))
                    + " stdout-tail"
                ),
                stderr_summary="context stderr explains generated drift",
            )

            with (
                mock.patch.object(
                    workflow_module.WorkflowExecutor,
                    "_run_subprocess",
                    _workflow_subprocess_with_oversized_doctor_output,
                ),
                mock.patch(
                    "ai_project_ctl.pipeline.close_phase.evaluate_report_gate",
                    return_value=report_gate,
                ),
                mock.patch(
                    "ai_project_ctl.pipeline.close_phase.evaluate_machine_review",
                    return_value=machine_review,
                ),
                mock.patch(
                    "ai_project_ctl.pipeline.git_commit.run_git_command",
                    side_effect=AssertionError(
                        "git must not run after Machine Review blocks readiness"
                    ),
                ),
            ):
                close = close_phase(
                    session_id,
                    root=root,
                    actor="tester",
                    confirmed=True,
                )

            self.assertTrue(close.ok, close.errors)
            phase_result = close.data["phase_result"]
            self.assertEqual(phase_result["status"], "blocked")
            artifacts = phase_result["artifacts"]
            local_commit = artifacts["local_commit"]
            self.assertEqual(local_commit["status"], "blocked")
            self.assertEqual(local_commit["code"], "COMMIT_READINESS_FAILED")
            diagnostics = local_commit["readiness"]["machine_review_diagnostics"]
            self.assertEqual(len(diagnostics), 1)
            self.assertEqual(diagnostics[0]["name"], "context_check_generated")
            self.assertEqual(diagnostics[0]["status"], "fail")
            self.assertEqual(diagnostics[0]["code"], "CONTEXT_CHECK_GENERATED_FAILED")
            self.assertEqual(
                diagnostics[0]["command"],
                [sys.executable, "scripts/contextctl.py", "check-generated"],
            )
            self.assertIn("context stdout", diagnostics[0]["stdout_summary"])
            self.assertIn("context stderr", diagnostics[0]["stderr_summary"])
            self.assertNotIn("stdout-tail", json.dumps(artifacts, sort_keys=True))


def _write_temp_project(root: Path) -> None:
    _run_script(root, "planctl.py", "init", "--project-name", "Pipeline Review Close")
    _run_script(root, "planctl.py", "initiative", "create", "--title", "Pipeline")
    _run_script(
        root,
        "planctl.py",
        "epic",
        "create",
        "--initiative",
        "INIT-001",
        "--title",
        "Review Close",
    )
    _write_docs_fixture(root)
    _run_script(root, "taskctl.py", "init")
    _run_script(
        root,
        "taskctl.py",
        "task",
        "create",
        "--epic",
        "EPIC-001",
        "--title",
        "Pipeline review close integration",
        "--status",
        "ready",
        "--summary",
        "Verify fake Codex evidence, fake reviewer approval, and governed close.",
        "--description",
        "Integration fixture for review APPROVE followed by close preflight.",
        "--scope",
        "Write the allowed test file and submit a structured report.",
        "--out-of-scope",
        "Do not run external Codex.",
        "--allowed-file",
        CHANGED_FILE,
        "--acceptance",
        "Review APPROVE reaches governed close.",
        "--review-instruction",
        "Check review_id and close artifacts in phase history.",
        "--verification-mode",
        "strict",
    )
    _run_script(root, "evolutionctl.py", "init")
    _run_script(
        root,
        "evolutionctl.py",
        "change",
        "create",
        "--title",
        "Approve temp pipeline test task",
        "--type",
        "tooling",
        "--status",
        "draft",
        "--problem",
        "The temp task needs an approved Change gate for execution.",
        "--proposal",
        "Approve the isolated temp pipeline task.",
    )
    _run_script(
        root,
        "evolutionctl.py",
        "change",
        "add-affected-file",
        "CHG-001",
        "--text",
        CHANGED_FILE,
    )
    _run_script(
        root,
        "evolutionctl.py",
        "change",
        "link-task",
        "CHG-001",
        "--task",
        TASK_ID,
    )
    _run_script(
        root,
        "evolutionctl.py",
        "change",
        "transition",
        "CHG-001",
        "--to",
        "ready",
    )
    _run_script(
        root,
        "evolutionctl.py",
        "change",
        "approve",
        "CHG-001",
        "--notes",
        "Owner approved temp execution.",
    )


def _create_close_session(root: Path, *, policy=None) -> str:
    if policy is None:
        policy = policy_preset("supervised_executable_autoclose")
    session = create_session(
        root=root,
        actor="tester",
        policy=policy,
        task_refs=(TASK_ID,),
        max_tasks=1,
        order_by="selected",
        current_task_id=TASK_ID,
        current_task_ref=TASK_ID,
        auto_close_note=OWNER_APPROVAL_NOTE,
    )
    if not session.ok:
        raise AssertionError(session.errors)
    return str(session.data["session_id"])


def _record_close_preflight_history(root: Path, session_id: str) -> None:
    report_id = "RPT-001"
    for phase_name in ("prepare", "execute", "collect_report", "verify"):
        _record_phase(
            root,
            session_id,
            PhaseResult.passed(
                phase_name,
                reason="{} fixture passed.".format(phase_name),
                artifacts={"task_id": TASK_ID, "report_id": report_id},
            ),
        )
    _record_phase(
        root,
        session_id,
        PhaseResult.passed(
            "review",
            reason="Review fixture approved.",
            artifacts={
                "task_id": TASK_ID,
                "report_id": report_id,
                "review_id": "CREV-001",
                "review_status": "pass",
                "review_code": "CODEX_REVIEW_APPROVE",
                "verdict": "APPROVE",
            },
        ),
    )


def _record_phase(root: Path, session_id: str, phase: PhaseResult) -> None:
    result = record_phase_result(
        session_id,
        phase,
        root=root,
        actor="tester",
        task_id=TASK_ID,
        command="test.pipeline.phase.{}".format(phase.phase),
    )
    if not result.ok:
        raise AssertionError(result.errors)


def _prepare_auto_close_workflow(root: Path) -> None:
    _run_script(
        root,
        "taskctl.py",
        "task",
        "transition",
        TASK_ID,
        "--to",
        "in_progress",
    )
    _run_script(
        root,
        "contextctl.py",
        "pack",
        "build",
        "--task",
        TASK_ID,
        "--write",
    )


def _local_commit_warning_policy():
    policy = policy_preset("supervised_local_commit")
    return replace(
        policy,
        verify=replace(
            policy.verify,
            allow_report_warnings=True,
            block_report_warnings=False,
        ),
    )


def _warning_report_gate() -> ReportGateResult:
    return ReportGateResult(
        status="warn",
        code="CODEX_REPORT_WARN",
        reason="Report contains advisory warning evidence accepted by policy.",
        report_id="RPT-001",
        task_id=TASK_ID,
        changed_files=(CHANGED_FILE,),
    )


def _machine_review_with_warning(
    warning: MachineCheckEvidence,
) -> MachineReviewResult:
    checks = [
        MachineCheckEvidence(
            name=name,
            status="pass",
            code="MACHINE_REVIEW_PASS",
            reason="{} passed.".format(name),
        )
        for name in sorted(REQUIRED_MACHINE_CHECKS)
    ]
    checks.append(warning)
    return MachineReviewResult(
        status="warn",
        code="MACHINE_REVIEW_WARN",
        reason="Machine Review returned warning evidence.",
        task_id=TASK_ID,
        report_id="RPT-001",
        checks=tuple(checks),
    )


def _machine_review_with_context_check_failure(
    *,
    stdout_summary: str = "",
    stderr_summary: str = "",
) -> MachineReviewResult:
    checks = [
        MachineCheckEvidence(
            name=name,
            status="pass",
            code="MACHINE_REVIEW_PASS",
            reason="{} passed.".format(name),
        )
        for name in sorted(REQUIRED_MACHINE_CHECKS)
        if name != "context_check_generated"
    ]
    checks.append(
        MachineCheckEvidence(
            name="context_check_generated",
            status="fail",
            code="CONTEXT_CHECK_GENERATED_FAILED",
            reason="Context generated output is stale.",
            command=(sys.executable, "scripts/contextctl.py", "check-generated"),
            returncode=1,
            stdout_summary=stdout_summary,
            stderr_summary=stderr_summary,
        )
    )
    return MachineReviewResult(
        status="fail",
        code="CONTEXT_CHECK_GENERATED_FAILED",
        reason="Context generated output is stale.",
        task_id=TASK_ID,
        report_id="RPT-001",
        checks=tuple(checks),
    )


def _fake_git_command_runner(
    calls: list[list[str]],
    *,
    git_status_stdout: str | None = None,
    before_git_status=None,
):
    def runner(command, **_kwargs) -> GitCommandResult:
        argv = tuple(str(part) for part in command)
        calls.append(list(argv))
        if argv == ("git", "status", "--short", "--untracked-files=all"):
            if before_git_status is not None:
                before_git_status()
            return GitCommandResult(
                ok=True,
                code="GIT_STATUS_PASS",
                reason="Fake git status found approved file changes.",
                command=argv,
                returncode=0,
                stdout=git_status_stdout or " M {}\n".format(CHANGED_FILE),
            )
        if len(argv) >= 4 and argv[:3] == ("git", "add", "--"):
            return GitCommandResult(
                ok=True,
                code="GIT_ADD_PASS",
                reason="Fake git add staged approved files.",
                command=argv,
                returncode=0,
            )
        if len(argv) >= 4 and argv[:3] == ("git", "commit", "-m"):
            return GitCommandResult(
                ok=True,
                code="GIT_COMMIT_PASS",
                reason="Fake git commit succeeded.",
                command=argv,
                returncode=0,
            )
        if argv == ("git", "rev-parse", "--verify", "HEAD"):
            return GitCommandResult(
                ok=True,
                code="GIT_REV_PARSE_PASS",
                reason="Fake git rev-parse returned a local commit hash.",
                command=argv,
                returncode=0,
                stdout="abc1234deadbeef\n",
            )
        return GitCommandResult(
            ok=False,
            code="UNEXPECTED_GIT_COMMAND",
            reason="Unexpected fake git command: {}".format(" ".join(argv)),
            command=argv,
            returncode=1,
        )

    return runner


def _mark_task_done(root: Path, *, notes: str) -> None:
    _run_script(root, "taskctl.py", "task", "transition", TASK_ID, "--to", "in_progress")
    _run_script(root, "taskctl.py", "task", "transition", TASK_ID, "--to", "in_review")
    _run_script(root, "taskctl.py", "task", "approve", TASK_ID, "--notes", notes)
    _run_script(root, "taskctl.py", "task", "transition", TASK_ID, "--to", "done")


def _write_docs_fixture(root: Path) -> None:
    docs_dir = root / "docs"
    state_dir = root / "AI_PROJECT" / "state"
    docs_dir.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "test.md").write_text("# Test Doc\n\nStatus: Active\n", encoding="utf-8")
    now = "2026-06-25T00:00:00Z"
    (state_dir / "docs.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "created_at": now,
                "updated_at": now,
                "docs": [
                    {
                        "id": "DOC-001",
                        "path": "docs/test.md",
                        "title": "Test Doc",
                        "type": "guide",
                        "status": "active",
                        "required": True,
                        "owner": "tester",
                        "last_reviewed_at": "",
                        "last_reviewed_by": "",
                        "content_hash": "",
                        "last_reviewed_content_hash": "",
                        "declared_status": "",
                        "declared_status_raw": "",
                        "declared_status_source": "",
                        "notes": [],
                        "created_at": now,
                        "updated_at": now,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    _run_script(
        root,
        "docctl.py",
        "doc",
        "mark-reviewed",
        "docs/test.md",
        "--note",
        "reviewed for temp fixture",
    )


def _write_fake_reviewer(root: Path, *, report_id: str) -> Path:
    path = root / "fake_reviewer.py"
    path.write_text(
        "\n".join(
            [
                "import json",
                "import sys",
                "sys.stdin.read()",
                "print(json.dumps({",
                "    'verdict': 'APPROVE',",
                "    'summary': 'Fake reviewer approved verified evidence.',",
                "    'evidence': {",
                "        'task_id': {!r},".format(TASK_ID),
                "        'report_id': {!r},".format(report_id),
                "        'report_gate_status': 'pass',",
                "        'machine_review_status': 'pass',",
                "    },",
                "    'findings': [],",
                "    'risks': [],",
                "}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def _report_payload(token_gate: dict, *, task_ref: str) -> dict:
    return {
        "schema_version": 1,
        "task_id": TASK_ID,
        "task_ref": task_ref,
        "implementation_summary": "Fake Codex wrote the allowed file.",
        "changed_files": [CHANGED_FILE],
        "generated_files": [],
        "checks": [
            {
                "name": "fake-codex-check",
                "command": "fake-codex exec",
                "result": "pass",
                "duration_sec": 0.1,
                "blocking": True,
                "details": "local fake adapter only",
            }
        ],
        "warnings": [],
        "blockers": [],
        "notes": [],
        "owner_decision_required": False,
        "token_usage": {
            "prompt_tokens": token_gate["prompt_tokens"],
            "context_tokens": token_gate["context_tokens"],
            "completion_tokens": 0,
            "output_tokens": 0,
            "total_tokens": token_gate["prompt_tokens"] + token_gate["context_tokens"],
            "remaining_tokens": token_gate["remaining_tokens"],
            "model_context_limit": token_gate["model_context_limit"],
            "max_context_tokens": token_gate["max_context_tokens"],
            "reserved_output_tokens": token_gate["reserved_output_tokens"],
            "min_remaining_tokens": token_gate["min_remaining_tokens"],
            "token_count_strategy": token_gate["token_count_strategy"],
            "token_count_estimated": token_gate["token_count_estimated"],
            "token_count_unavailable": False,
            "token_count_unavailable_reason": "",
        },
    }


def _run_script(
    root: Path,
    script_name: str,
    *args: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / script_name),
            "--root",
            str(root),
            "--actor",
            "tester",
            *args,
        ],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )


def _workflow_subprocess_with_oversized_doctor_output(
    _executor,
    argv: list[str] | tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        list(argv),
        cwd=str(workflow_module.PACKAGE_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    script = Path(argv[1]).name if len(argv) > 1 else ""
    is_doctor = script == "aictl.py" and "project" in argv and "doctor" in argv
    if not is_doctor:
        return completed
    return subprocess.CompletedProcess(
        args=completed.args,
        returncode=completed.returncode,
        stdout=_oversized_text("stdout"),
        stderr=_oversized_text("stderr"),
    )


def _oversized_text(label: str) -> str:
    return "{}:{}".format(label, label[:1] * (MAX_STORED_STRING_LENGTH + 1))


def _protected_check_pass_runner(
    argv: list[str] | tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    args = list(argv)
    if tuple(args[-2:]) != ("project", "protected-check"):
        raise AssertionError("unexpected execute runner command: {}".format(args))
    return subprocess.CompletedProcess(
        args=args,
        returncode=0,
        stdout=json.dumps(
            {
                "ok": True,
                "errors": [],
                "warnings": [],
                "checked": ["protected generated outputs are fresh"],
            }
        )
        + "\n",
        stderr="",
    )


def _workflow_steps_by_id(workflow: dict, step_id: str) -> list[dict]:
    matches: list[dict] = []
    pending = [workflow]
    while pending:
        item = pending.pop(0)
        data = item.get("data") if isinstance(item, dict) else {}
        if not isinstance(data, dict):
            continue
        steps = data.get("steps")
        if isinstance(steps, list):
            matches.extend(
                step
                for step in steps
                if isinstance(step, dict) and step.get("id") == step_id
            )
        nested = data.get("workflows")
        if isinstance(nested, list):
            pending.extend(item for item in nested if isinstance(item, dict))
    return matches


def _read_tasks_state(root: Path) -> dict:
    return json.loads(
        (root / "AI_PROJECT" / "state" / "tasks.json").read_text(encoding="utf-8")
    )


def _task(root: Path) -> dict:
    return _read_tasks_state(root)["tasks"][0]


def _read_evolution_state(root: Path) -> dict:
    return json.loads(
        (root / "AI_PROJECT" / "state" / "evolution.json").read_text(encoding="utf-8")
    )


def _change(root: Path, change_id: str) -> dict:
    for change in _read_evolution_state(root)["changes"]:
        if change["id"] == change_id:
            return change
    raise AssertionError("missing change {}".format(change_id))


def _pipeline_session(root: Path) -> dict:
    state = json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))
    return state["sessions"][0]


def _commit_paths(root: Path, *paths: str, message: str) -> None:
    _run_git(root, "add", *paths)
    _run_git(
        root,
        "-c",
        "user.email=tester@example.com",
        "-c",
        "user.name=Tester",
        "commit",
        "-m",
        message,
    )


def _run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )


if __name__ == "__main__":
    unittest.main()

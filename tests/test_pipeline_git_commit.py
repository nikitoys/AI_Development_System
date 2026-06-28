import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ai_project_ctl.core.result import CommandResult
from ai_project_ctl.pipeline.codex_review import (
    CODE_PASS as CODEX_REVIEW_CODE_PASS,
    PASS as CODEX_REVIEW_PASS,
    VERDICT_APPROVE,
    CodexReviewResult,
)
from ai_project_ctl.pipeline.git_commit import (
    CODE_MACHINE_REVIEW_NOT_PASS,
    CODE_READY,
    CODE_REPORT_NOT_PASS,
    CODE_REQUIRED_CHECK_NOT_PASS,
    CODE_UNRELATED_FILES,
    MACHINE_DIAGNOSTIC_SUMMARY_LIMIT,
    REQUIRED_MACHINE_CHECKS,
    evaluate_commit_readiness,
    run_git_command,
)
from ai_project_ctl.pipeline.machine_review import (
    CODE_PASS as MACHINE_REVIEW_CODE_PASS,
    CODE_UNSAFE_TEST_COMMAND,
    CODE_WARN as MACHINE_REVIEW_CODE_WARN,
    FAIL as MACHINE_REVIEW_FAIL,
    PASS as MACHINE_REVIEW_PASS,
    WARN as MACHINE_REVIEW_WARN,
    MachineCheckEvidence,
    MachineReviewResult,
)
from ai_project_ctl.pipeline.policy import policy_preset
from ai_project_ctl.pipeline.report_gate import (
    CODE_BLOCKERS_PRESENT,
    CODE_PASS as REPORT_CODE_PASS,
    CODE_WARN as REPORT_CODE_WARN,
    FAIL as REPORT_FAIL,
    PASS as REPORT_PASS,
    WARN as REPORT_WARN,
    ReportGateResult,
)


TASK_ID = "TASK-001"
REPORT_ID = "RPT-001"
CHANGED_FILE = "ai_project_ctl/pipeline/git_commit.py"
CONTROL_STATE_FILE = "AI_PROJECT/state/tasks.json"
CONTROL_EVENT_FILE = "AI_PROJECT/events/task-events.jsonl"
CONTROL_GENERATED_FILE = "AI_PROJECT/generated/CODEX_TASKS.md"
UNRELATED_FILE = "tests/unrelated_dirty_file.py"


def completed(stdout="", returncode=0, stderr=""):
    return subprocess.CompletedProcess(
        args=[],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def _write_task_state(root: Path):
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "tasks.json").write_text(
        json.dumps(
            {
                "tasks": [
                    {
                        "id": TASK_ID,
                        "status": "done",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def _policy(*, allow_report_warnings: bool = False):
    policy = policy_preset("supervised_local_commit")
    return replace(
        policy,
        verify=replace(
            policy.verify,
            allow_report_warnings=allow_report_warnings,
        ),
    )


def _report_gate(
    *,
    status: str = REPORT_PASS,
    code: str = REPORT_CODE_PASS,
    changed_files: tuple[str, ...] = (CHANGED_FILE,),
    generated_files: tuple[str, ...] = (),
) -> ReportGateResult:
    return ReportGateResult(
        status=status,
        code=code,
        reason="report gate {}".format(status),
        report_id=REPORT_ID,
        task_id=TASK_ID,
        changed_files=changed_files,
        generated_files=generated_files,
    )


def _machine_review(
    *,
    status: str = MACHINE_REVIEW_PASS,
    code: str = MACHINE_REVIEW_CODE_PASS,
    required_statuses: dict[str, str] | None = None,
    extra_checks: tuple[MachineCheckEvidence, ...] = (),
) -> MachineReviewResult:
    required = required_statuses or {}
    checks = []
    for name in sorted(REQUIRED_MACHINE_CHECKS):
        check_status = required.get(name, MACHINE_REVIEW_PASS)
        checks.append(
            MachineCheckEvidence(
                name=name,
                status=check_status,
                code="{}_{}".format(name.upper(), check_status.upper()),
                reason="{} {}".format(name, check_status),
            )
        )
    return MachineReviewResult(
        status=status,
        code=code,
        reason="Machine Review {}.".format(status),
        task_id=TASK_ID,
        report_id=REPORT_ID,
        checks=tuple(checks) + tuple(extra_checks),
    )


def _nonblocking_report_declared_warning() -> MachineCheckEvidence:
    return MachineCheckEvidence(
        name="report_declared_test_1",
        status=MACHINE_REVIEW_WARN,
        code=CODE_UNSAFE_TEST_COMMAND,
        reason="test_command_skipped_as_unsafe",
        blocking=False,
    )


def _codex_review() -> CodexReviewResult:
    return CodexReviewResult(
        status=CODEX_REVIEW_PASS,
        code=CODEX_REVIEW_CODE_PASS,
        reason="Codex Review approved.",
        verdict=VERDICT_APPROVE,
        task_id=TASK_ID,
        report_id=REPORT_ID,
        review_id="REV-001",
        prompt_sha256="0" * 64,
        prompt_bytes=1,
    )


def _git_status_with_changed_file(argv):
    if tuple(argv) != ("git", "status", "--short", "--untracked-files=all"):
        raise AssertionError("unexpected git command: {}".format(argv))
    return completed(stdout=" M {}\n".format(CHANGED_FILE))


def _git_status_for_paths(*paths: str):
    def runner(argv):
        if tuple(argv) != ("git", "status", "--short", "--untracked-files=all"):
            raise AssertionError("unexpected git command: {}".format(argv))
        return completed(stdout="".join(" M {}\n".format(path) for path in paths))

    return runner


def _unexpected_git_runner(argv):
    raise AssertionError("git should not run after readiness blocker: {}".format(argv))


def _evaluate_commit_readiness_for_report_gate(
    root: Path,
    report_gate: ReportGateResult,
    *,
    allow_report_warnings: bool = False,
    runner=_git_status_with_changed_file,
):
    return evaluate_commit_readiness(
        root=root,
        task_id=TASK_ID,
        policy=_policy(allow_report_warnings=allow_report_warnings),
        report_gate=report_gate,
        machine_review=_machine_review(),
        codex_review=_codex_review(),
        runner=runner,
    )


def _evaluate_commit_readiness_for_machine_review(
    root: Path,
    machine_review: MachineReviewResult,
    *,
    report_gate: ReportGateResult | None = None,
    allow_report_warnings: bool = False,
    runner=_git_status_with_changed_file,
):
    return evaluate_commit_readiness(
        root=root,
        task_id=TASK_ID,
        policy=_policy(allow_report_warnings=allow_report_warnings),
        report_gate=report_gate or _report_gate(),
        machine_review=machine_review,
        codex_review=_codex_review(),
        runner=runner,
    )


def _session_file_evidence(
    *,
    pre_existing: tuple[str, ...] = (),
    session_owned: tuple[str, ...] = (),
) -> dict:
    return {
        "id": "PSESS-001",
        "file_evidence": {
            "pre_existing_dirty_files": list(pre_existing),
            "session_owned_changed_files": list(session_owned),
        },
    }


def _side_effect(
    *,
    changed_files: tuple[str, ...] = (),
    generated_files: tuple[str, ...] = (),
) -> CommandResult:
    result = CommandResult.success(
        command="test.side.effect",
        domain="test",
        message="side effect",
    )
    result.changed_files.extend(changed_files)
    result.generated_files.extend(generated_files)
    return result


class PipelineGitCommitTests(unittest.TestCase):
    def test_commit_readiness_accepts_report_gate_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = _evaluate_commit_readiness_for_report_gate(
                root,
                _report_gate(status=REPORT_PASS, code=REPORT_CODE_PASS),
            )

        self.assertTrue(result.ok)
        self.assertEqual(result.code, CODE_READY)

    def test_commit_readiness_accepts_session_owned_governed_control_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = evaluate_commit_readiness(
                root=root,
                task_id=TASK_ID,
                policy=_policy(),
                report_gate=_report_gate(),
                machine_review=_machine_review(),
                codex_review=_codex_review(),
                session=_session_file_evidence(
                    session_owned=(
                        CONTROL_STATE_FILE,
                        CONTROL_EVENT_FILE,
                        CONTROL_GENERATED_FILE,
                    )
                ),
                runner=_git_status_for_paths(
                    CHANGED_FILE,
                    CONTROL_STATE_FILE,
                    CONTROL_EVENT_FILE,
                    CONTROL_GENERATED_FILE,
                ),
            )

        self.assertTrue(result.ok)
        self.assertEqual(result.code, CODE_READY)
        self.assertEqual(
            sorted(result.approved_files),
            sorted(
                [
                    CHANGED_FILE,
                    CONTROL_STATE_FILE,
                    CONTROL_EVENT_FILE,
                    CONTROL_GENERATED_FILE,
                ]
            ),
        )

    def test_commit_readiness_blocks_pre_existing_control_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = evaluate_commit_readiness(
                root=root,
                task_id=TASK_ID,
                policy=_policy(),
                report_gate=_report_gate(),
                machine_review=_machine_review(),
                codex_review=_codex_review(),
                side_effects=(
                    _side_effect(
                        changed_files=(CONTROL_STATE_FILE, CONTROL_EVENT_FILE)
                    ),
                ),
                session=_session_file_evidence(
                    pre_existing=(CONTROL_STATE_FILE,),
                    session_owned=(CONTROL_EVENT_FILE,),
                ),
                runner=_git_status_for_paths(
                    CHANGED_FILE,
                    CONTROL_STATE_FILE,
                    CONTROL_EVENT_FILE,
                ),
            )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODE_UNRELATED_FILES)
        self.assertEqual(result.blockers, (CONTROL_STATE_FILE,))
        self.assertNotIn(CONTROL_STATE_FILE, result.approved_files)
        self.assertIn(CONTROL_EVENT_FILE, result.approved_files)

    def test_commit_readiness_blocks_unrelated_code_with_session_owned_control_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = evaluate_commit_readiness(
                root=root,
                task_id=TASK_ID,
                policy=_policy(),
                report_gate=_report_gate(),
                machine_review=_machine_review(),
                codex_review=_codex_review(),
                session=_session_file_evidence(session_owned=(CONTROL_STATE_FILE,)),
                runner=_git_status_for_paths(
                    CHANGED_FILE,
                    CONTROL_STATE_FILE,
                    UNRELATED_FILE,
                ),
            )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODE_UNRELATED_FILES)
        self.assertEqual(result.blockers, (UNRELATED_FILE,))
        self.assertIn(CONTROL_STATE_FILE, result.approved_files)

    def test_commit_readiness_requires_report_task_artifact_with_session_control_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = evaluate_commit_readiness(
                root=root,
                task_id=TASK_ID,
                policy=_policy(),
                report_gate=_report_gate(changed_files=()),
                machine_review=_machine_review(),
                codex_review=_codex_review(),
                session=_session_file_evidence(session_owned=(CONTROL_STATE_FILE,)),
                runner=_git_status_for_paths(CONTROL_STATE_FILE),
            )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODE_UNRELATED_FILES)
        self.assertEqual(result.blockers, ("target_task_artifact_missing",))

    def test_commit_readiness_accepts_report_gate_warn_when_policy_allows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = _evaluate_commit_readiness_for_report_gate(
                root,
                _report_gate(status=REPORT_WARN, code=REPORT_CODE_WARN),
                allow_report_warnings=True,
            )

        self.assertTrue(result.ok)
        self.assertEqual(result.code, CODE_READY)

    def test_commit_readiness_blocks_report_gate_warn_when_policy_disallows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = _evaluate_commit_readiness_for_report_gate(
                root,
                _report_gate(status=REPORT_WARN, code=REPORT_CODE_WARN),
                runner=_unexpected_git_runner,
            )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODE_REPORT_NOT_PASS)
        self.assertIn("allow_report_warnings is false", result.reason)

    def test_commit_readiness_blocks_unknown_report_gate_warn_when_policy_allows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = _evaluate_commit_readiness_for_report_gate(
                root,
                _report_gate(status=REPORT_WARN, code="CUSTOM_REPORT_WARN"),
                allow_report_warnings=True,
                runner=_unexpected_git_runner,
            )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODE_REPORT_NOT_PASS)

    def test_commit_readiness_blocks_report_gate_fail_when_policy_allows_warnings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = _evaluate_commit_readiness_for_report_gate(
                root,
                _report_gate(status=REPORT_FAIL, code=CODE_BLOCKERS_PRESENT),
                allow_report_warnings=True,
                runner=_unexpected_git_runner,
            )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODE_REPORT_NOT_PASS)

    def test_commit_readiness_accepts_machine_review_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = _evaluate_commit_readiness_for_machine_review(
                root,
                _machine_review(),
            )

        self.assertTrue(result.ok)
        self.assertEqual(result.code, CODE_READY)

    def test_commit_readiness_accepts_machine_review_warn_with_nonblocking_warning(self):
        advisory = _nonblocking_report_declared_warning()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = _evaluate_commit_readiness_for_machine_review(
                root,
                _machine_review(
                    status=MACHINE_REVIEW_WARN,
                    code=MACHINE_REVIEW_CODE_WARN,
                    extra_checks=(advisory,),
                ),
            )

        self.assertTrue(result.ok)
        self.assertEqual(result.code, CODE_READY)
        self.assertNotIn("unapproved warning evidence", result.reason)
        self.assertNotIn("report_declared_test_1", result.reason)
        payload = result.to_dict()
        self.assertEqual(payload["blocking_non_pass_checks"], [])
        self.assertEqual(
            [check["name"] for check in payload["advisory_non_pass_checks"]],
            ["report_declared_test_1"],
        )

    def test_commit_readiness_accepts_machine_review_warn_with_policy_approved_report_warning(self):
        report_warning = MachineCheckEvidence(
            name="codex_report_gate",
            status=MACHINE_REVIEW_WARN,
            code=MACHINE_REVIEW_CODE_WARN,
            reason="Report gate warning is policy-approved.",
            blocking=True,
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = _evaluate_commit_readiness_for_machine_review(
                root,
                _machine_review(
                    status=MACHINE_REVIEW_WARN,
                    code=MACHINE_REVIEW_CODE_WARN,
                    extra_checks=(report_warning,),
                ),
                report_gate=_report_gate(status=REPORT_WARN, code=REPORT_CODE_WARN),
                allow_report_warnings=True,
            )

        self.assertTrue(result.ok)
        self.assertEqual(result.code, CODE_READY)

    def test_commit_readiness_accepts_policy_approved_report_warning_with_nonblocking_warning(self):
        report_warning = MachineCheckEvidence(
            name="codex_report_gate",
            status=MACHINE_REVIEW_WARN,
            code=MACHINE_REVIEW_CODE_WARN,
            reason="Report gate warning is policy-approved.",
            blocking=True,
        )
        advisory = _nonblocking_report_declared_warning()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = _evaluate_commit_readiness_for_machine_review(
                root,
                _machine_review(
                    status=MACHINE_REVIEW_WARN,
                    code=MACHINE_REVIEW_CODE_WARN,
                    extra_checks=(report_warning, advisory),
                ),
                report_gate=_report_gate(status=REPORT_WARN, code=REPORT_CODE_WARN),
                allow_report_warnings=True,
            )

        self.assertTrue(result.ok)
        self.assertEqual(result.code, CODE_READY)
        self.assertNotIn("report_declared_test_1", result.reason)
        payload = result.to_dict()
        self.assertEqual(payload["blocking_non_pass_checks"], [])
        self.assertEqual(
            [check["name"] for check in payload["advisory_non_pass_checks"]],
            ["codex_report_gate", "report_declared_test_1"],
        )

    def test_commit_readiness_blocks_policy_approved_report_warning_with_blocking_unsafe_warning(self):
        report_warning = MachineCheckEvidence(
            name="codex_report_gate",
            status=MACHINE_REVIEW_WARN,
            code=MACHINE_REVIEW_CODE_WARN,
            reason="Report gate warning is policy-approved.",
            blocking=True,
        )
        unsafe_warning = replace(_nonblocking_report_declared_warning(), blocking=True)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = _evaluate_commit_readiness_for_machine_review(
                root,
                _machine_review(
                    status=MACHINE_REVIEW_WARN,
                    code=MACHINE_REVIEW_CODE_WARN,
                    extra_checks=(report_warning, unsafe_warning),
                ),
                report_gate=_report_gate(status=REPORT_WARN, code=REPORT_CODE_WARN),
                allow_report_warnings=True,
                runner=_unexpected_git_runner,
            )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODE_MACHINE_REVIEW_NOT_PASS)
        self.assertIn("unapproved warning evidence", result.reason)
        self.assertIn("report_declared_test_1", result.reason)
        self.assertIn("blocking=True", result.reason)
        payload = result.to_dict()
        self.assertEqual(
            [check["name"] for check in payload["blocking_non_pass_checks"]],
            ["report_declared_test_1"],
        )
        self.assertEqual(
            [check["name"] for check in payload["advisory_non_pass_checks"]],
            ["codex_report_gate"],
        )

    def test_commit_readiness_blocks_machine_review_report_warn_when_policy_disallows(self):
        report_warning = MachineCheckEvidence(
            name="codex_report_gate",
            status=MACHINE_REVIEW_WARN,
            code=MACHINE_REVIEW_CODE_WARN,
            reason="Report gate warning is not policy-approved.",
            blocking=True,
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = _evaluate_commit_readiness_for_machine_review(
                root,
                _machine_review(
                    status=MACHINE_REVIEW_WARN,
                    code=MACHINE_REVIEW_CODE_WARN,
                    extra_checks=(report_warning,),
                ),
                report_gate=_report_gate(status=REPORT_WARN, code=REPORT_CODE_WARN),
                runner=_unexpected_git_runner,
            )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODE_REPORT_NOT_PASS)
        self.assertIn("allow_report_warnings is false", result.reason)

    def test_commit_readiness_blocks_machine_review_warn_with_blocking_warning(self):
        blocking_warning = MachineCheckEvidence(
            name="project_doctor",
            status=MACHINE_REVIEW_WARN,
            code=MACHINE_REVIEW_CODE_WARN,
            reason="Project doctor warning needs review.",
            blocking=True,
        )
        advisory = _nonblocking_report_declared_warning()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = _evaluate_commit_readiness_for_machine_review(
                root,
                _machine_review(
                    status=MACHINE_REVIEW_WARN,
                    code=MACHINE_REVIEW_CODE_WARN,
                    extra_checks=(blocking_warning, advisory),
                ),
                runner=_unexpected_git_runner,
            )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODE_MACHINE_REVIEW_NOT_PASS)
        self.assertIn("unapproved warning evidence", result.reason)
        self.assertIn("project_doctor", result.reason)
        self.assertNotIn("report_declared_test_1", result.reason)
        payload = result.to_dict()
        self.assertEqual(
            [check["name"] for check in payload["blocking_non_pass_checks"]],
            ["project_doctor"],
        )
        self.assertEqual(
            [check["name"] for check in payload["advisory_non_pass_checks"]],
            ["report_declared_test_1"],
        )

    def test_commit_readiness_blocks_machine_review_warn_when_required_check_is_not_pass(self):
        required_check = sorted(REQUIRED_MACHINE_CHECKS)[0]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = _evaluate_commit_readiness_for_machine_review(
                root,
                _machine_review(
                    status=MACHINE_REVIEW_WARN,
                    code=MACHINE_REVIEW_CODE_WARN,
                    required_statuses={required_check: MACHINE_REVIEW_WARN},
                ),
                runner=_unexpected_git_runner,
            )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODE_REQUIRED_CHECK_NOT_PASS)
        self.assertIn(required_check, result.reason)

    def test_commit_readiness_blocks_machine_review_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = _evaluate_commit_readiness_for_machine_review(
                root,
                _machine_review(
                    status=MACHINE_REVIEW_FAIL,
                    code="MACHINE_REVIEW_FAIL",
                ),
                runner=_unexpected_git_runner,
            )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODE_MACHINE_REVIEW_NOT_PASS)
        self.assertIn("FAIL blocks", result.reason)

    def test_commit_readiness_serializes_compact_machine_review_diagnostics(self):
        stdout = "stdout-start " + ("x" * (MACHINE_DIAGNOSTIC_SUMMARY_LIMIT + 20)) + " stdout-tail"
        stderr = "stderr-start " + ("y" * (MACHINE_DIAGNOSTIC_SUMMARY_LIMIT + 20)) + " stderr-tail"
        checks = [
            MachineCheckEvidence(
                name=name,
                status=MACHINE_REVIEW_PASS,
                code=MACHINE_REVIEW_CODE_PASS,
                reason="{} passed.".format(name),
            )
            for name in sorted(REQUIRED_MACHINE_CHECKS)
            if name != "context_check_generated"
        ]
        checks.append(
            MachineCheckEvidence(
                name="context_check_generated",
                status=MACHINE_REVIEW_FAIL,
                code="CONTEXT_CHECK_GENERATED_FAILED",
                reason="Context generated output is stale.",
                command=("python", "scripts/contextctl.py", "check-generated"),
                returncode=1,
                stdout_summary=stdout,
                stderr_summary=stderr,
            )
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = _evaluate_commit_readiness_for_machine_review(
                root,
                MachineReviewResult(
                    status=MACHINE_REVIEW_FAIL,
                    code="MACHINE_REVIEW_FAIL",
                    reason="Machine Review failed.",
                    task_id=TASK_ID,
                    report_id=REPORT_ID,
                    checks=tuple(checks),
                ),
                runner=_unexpected_git_runner,
            )

        payload = result.to_dict()
        diagnostics = payload["machine_review_diagnostics"]
        blocking_checks = payload["blocking_non_pass_checks"]
        advisory_checks = payload["advisory_non_pass_checks"]

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODE_MACHINE_REVIEW_NOT_PASS)
        self.assertEqual(len(diagnostics), 1)
        self.assertEqual(len(blocking_checks), 1)
        self.assertEqual(advisory_checks, [])
        self.assertEqual(diagnostics[0]["name"], "context_check_generated")
        self.assertEqual(blocking_checks[0]["name"], "context_check_generated")
        self.assertEqual(diagnostics[0]["status"], MACHINE_REVIEW_FAIL)
        self.assertEqual(diagnostics[0]["code"], "CONTEXT_CHECK_GENERATED_FAILED")
        self.assertEqual(diagnostics[0]["reason"], "Context generated output is stale.")
        self.assertTrue(diagnostics[0]["blocking"])
        self.assertEqual(
            diagnostics[0]["command"],
            ["python", "scripts/contextctl.py", "check-generated"],
        )
        self.assertLessEqual(
            len(diagnostics[0]["stdout_summary"]),
            MACHINE_DIAGNOSTIC_SUMMARY_LIMIT,
        )
        self.assertLessEqual(
            len(diagnostics[0]["stderr_summary"]),
            MACHINE_DIAGNOSTIC_SUMMARY_LIMIT,
        )
        self.assertIn("stdout-start", diagnostics[0]["stdout_summary"])
        self.assertIn("stderr-start", diagnostics[0]["stderr_summary"])
        self.assertNotIn("stdout-tail", json.dumps(payload))
        self.assertNotIn("stderr-tail", json.dumps(payload))

    def test_commit_readiness_blocks_machine_review_blocking_failure_evidence(self):
        blocking_failure = MachineCheckEvidence(
            name="project_doctor",
            status=MACHINE_REVIEW_FAIL,
            code="PROJECT_DOCTOR_FAILED",
            reason="Project doctor failed.",
            blocking=True,
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = _evaluate_commit_readiness_for_machine_review(
                root,
                _machine_review(
                    status=MACHINE_REVIEW_WARN,
                    code=MACHINE_REVIEW_CODE_WARN,
                    extra_checks=(blocking_failure,),
                ),
                runner=_unexpected_git_runner,
            )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODE_MACHINE_REVIEW_NOT_PASS)
        self.assertIn("Blocking Machine Review failure", result.reason)
        self.assertIn("project_doctor", result.reason)

    def test_git_command_rejects_forbidden_subcommands_without_runner(self):
        calls = []

        def fake_runner(argv):
            calls.append(list(argv))
            return completed()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for subcommand in ("push", "merge", "reset", "checkout", "rebase", "clean"):
                with self.subTest(subcommand=subcommand):
                    result = run_git_command(
                        ("git", subcommand),
                        root=root,
                        runner=fake_runner,
                    )

                    self.assertFalse(result.ok)
                    self.assertEqual(result.code, "COMMIT_FORBIDDEN_GIT_COMMAND")

        self.assertEqual(calls, [])

    def test_git_add_requires_explicit_paths_after_separator(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run_git_command(
                ("git", "add", "."),
                root=root,
                runner=lambda argv: completed(),
            )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, "COMMIT_FORBIDDEN_GIT_COMMAND")


if __name__ == "__main__":
    unittest.main()

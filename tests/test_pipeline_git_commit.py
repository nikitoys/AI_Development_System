import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

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
) -> ReportGateResult:
    return ReportGateResult(
        status=status,
        code=code,
        reason="report gate {}".format(status),
        report_id=REPORT_ID,
        task_id=TASK_ID,
        changed_files=(CHANGED_FILE,),
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

    def test_commit_readiness_blocks_machine_review_warn_with_nonreport_warning(self):
        advisory = MachineCheckEvidence(
            name="report_declared_test_1",
            status=MACHINE_REVIEW_WARN,
            code=CODE_UNSAFE_TEST_COMMAND,
            reason="test_command_skipped_as_unsafe",
            blocking=False,
        )
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
                runner=_unexpected_git_runner,
            )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODE_MACHINE_REVIEW_NOT_PASS)
        self.assertIn("report_declared_test_1", result.reason)

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
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_task_state(root)

            result = _evaluate_commit_readiness_for_machine_review(
                root,
                _machine_review(
                    status=MACHINE_REVIEW_WARN,
                    code=MACHINE_REVIEW_CODE_WARN,
                    extra_checks=(blocking_warning,),
                ),
                runner=_unexpected_git_runner,
            )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODE_MACHINE_REVIEW_NOT_PASS)
        self.assertIn("unapproved warning evidence", result.reason)
        self.assertIn("project_doctor", result.reason)

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

        self.assertFalse(result.ok)
        self.assertEqual(result.code, CODE_MACHINE_REVIEW_NOT_PASS)
        self.assertEqual(len(diagnostics), 1)
        self.assertEqual(diagnostics[0]["name"], "context_check_generated")
        self.assertEqual(diagnostics[0]["status"], MACHINE_REVIEW_FAIL)
        self.assertEqual(diagnostics[0]["code"], "CONTEXT_CHECK_GENERATED_FAILED")
        self.assertEqual(diagnostics[0]["reason"], "Context generated output is stale.")
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

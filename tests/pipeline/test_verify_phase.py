import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from ai_project_ctl.pipeline.git_diff_gate import (
    BLOCKED,
    CODE_ALLOWED_FILES_OUT_OF_SCOPE,
    CODE_DIFF_MISMATCH,
    CODE_PASS,
    GitDiffGateResult,
    GitStatusEntry,
    PASS,
    evaluate_allowed_files_gate,
)
from ai_project_ctl.pipeline.phase import PhaseResult
from ai_project_ctl.pipeline.policy import PipelinePolicy
from ai_project_ctl.pipeline.report_gate import CODE_BLOCKERS_PRESENT
from ai_project_ctl.pipeline.report_gate import CODE_WARN as CODEX_REPORT_WARN
from ai_project_ctl.pipeline.session import create_session, record_phase_result
from ai_project_ctl.pipeline.state import pipeline_state_path
from ai_project_ctl.pipeline.verify_phase import (
    GIT_DIFF_BASED_GATE_NAMES,
    GIT_DIFF_GATES_POLICY_KEY,
    REPORT_WARNING_POLICY_KEY,
    SKIPPED_GATES_KEY,
    _exclude_runtime_logs_from_git_diff,
    _report_git_diff_comparison,
    verify_phase,
)


class VerifyPhaseRuntimeLogDiffGateTests(unittest.TestCase):
    def test_runtime_logs_are_removed_from_missing_report_comparison(self):
        result = GitDiffGateResult(
            status=BLOCKED,
            code=CODE_DIFF_MISMATCH,
            reason="working_tree_diff_does_not_match_expected_files",
            repo_root="/repo",
            expected_files=("ai_project_ctl/pipeline/verify_phase.py",),
            changed_files=(
                "AI_PROJECT/logs/codex/PSESS-001/TASK-001-stdout.log",
                "AI_PROJECT/logs/ui_run/PSESS-001-verify.json",
                "ai_project_ctl/pipeline/verify_phase.py",
            ),
            tracked_files=(
                "AI_PROJECT/logs/ui_run/PSESS-001-verify.json",
                "ai_project_ctl/pipeline/verify_phase.py",
            ),
            untracked_files=(
                "AI_PROJECT/logs/codex/PSESS-001/TASK-001-stdout.log",
            ),
            unexpected_files=(
                "AI_PROJECT/logs/codex/PSESS-001/TASK-001-stdout.log",
                "AI_PROJECT/logs/ui_run/PSESS-001-verify.json",
            ),
            status_entries=(
                GitStatusEntry(
                    "??",
                    "AI_PROJECT/logs/codex/PSESS-001/TASK-001-stdout.log",
                ),
                GitStatusEntry(" M", "AI_PROJECT/logs/ui_run/PSESS-001-verify.json"),
                GitStatusEntry(" M", "ai_project_ctl/pipeline/verify_phase.py"),
            ),
        )

        filtered = _exclude_runtime_logs_from_git_diff(result)
        comparison = _report_git_diff_comparison(_Report(), filtered)

        self.assertEqual(filtered.status, PASS)
        self.assertEqual(filtered.code, CODE_PASS)
        self.assertEqual(
            filtered.changed_files,
            ("ai_project_ctl/pipeline/verify_phase.py",),
        )
        self.assertEqual(filtered.unexpected_files, ())
        self.assertEqual(comparison["missing_from_report"], [])
        self.assertNotIn(
            "AI_PROJECT/logs/ui_run/PSESS-001-verify.json",
            filtered.tracked_files,
        )

    def test_real_source_test_and_doc_diffs_still_block_when_not_reported(self):
        result = GitDiffGateResult(
            status=BLOCKED,
            code=CODE_DIFF_MISMATCH,
            reason="working_tree_diff_does_not_match_expected_files",
            repo_root="/repo",
            expected_files=(),
            changed_files=(
                "AI_PROJECT/logs/codex/PSESS-001/TASK-001-stderr.log",
                "ai-system/rules.md",
                "ai_project_ctl/pipeline/verify_phase.py",
                "tests/pipeline/test_verify_phase.py",
            ),
            tracked_files=(
                "ai-system/rules.md",
                "ai_project_ctl/pipeline/verify_phase.py",
                "tests/pipeline/test_verify_phase.py",
            ),
            untracked_files=(
                "AI_PROJECT/logs/codex/PSESS-001/TASK-001-stderr.log",
            ),
            unexpected_files=(
                "AI_PROJECT/logs/codex/PSESS-001/TASK-001-stderr.log",
                "ai-system/rules.md",
                "ai_project_ctl/pipeline/verify_phase.py",
                "tests/pipeline/test_verify_phase.py",
            ),
            status_entries=(
                GitStatusEntry(
                    "??",
                    "AI_PROJECT/logs/codex/PSESS-001/TASK-001-stderr.log",
                ),
                GitStatusEntry(" M", "ai-system/rules.md"),
                GitStatusEntry(" M", "ai_project_ctl/pipeline/verify_phase.py"),
                GitStatusEntry(" M", "tests/pipeline/test_verify_phase.py"),
            ),
        )

        filtered = _exclude_runtime_logs_from_git_diff(result)
        comparison = _report_git_diff_comparison(_Report(), filtered)

        self.assertEqual(filtered.status, BLOCKED)
        self.assertEqual(filtered.code, CODE_DIFF_MISMATCH)
        self.assertEqual(
            filtered.unexpected_files,
            (
                "ai-system/rules.md",
                "ai_project_ctl/pipeline/verify_phase.py",
                "tests/pipeline/test_verify_phase.py",
            ),
        )
        self.assertEqual(
            comparison["missing_from_report"],
            [
                "ai-system/rules.md",
                "ai_project_ctl/pipeline/verify_phase.py",
                "tests/pipeline/test_verify_phase.py",
            ],
        )


class VerifyPhaseGitDiffPolicyTests(unittest.TestCase):
    def test_default_policy_is_strict_and_relaxed_policy_serializes_explicitly(self):
        strict = PipelinePolicy.default()
        relaxed = replace(
            strict,
            name="relaxed_verify",
            verify=replace(strict.verify, run_git_diff_gates=False),
        )

        self.assertTrue(strict.verify.run_git_diff_gates)
        self.assertTrue(strict.verify.block_report_warnings)
        self.assertNotIn("verify", strict.to_dict())
        self.assertTrue(PipelinePolicy.from_dict(strict.to_dict()).verify.run_git_diff_gates)
        self.assertTrue(
            PipelinePolicy.from_dict(strict.to_dict()).verify.block_report_warnings
        )
        self.assertEqual(
            relaxed.to_dict()["verify"],
            {"run_git_diff_gates": False},
        )
        self.assertFalse(PipelinePolicy.from_dict(relaxed.to_dict()).verify.run_git_diff_gates)
        self.assertTrue(PipelinePolicy.from_dict(relaxed.to_dict()).verify.block_report_warnings)

        relaxed_warnings = replace(
            strict,
            name="relaxed_report_warnings",
            verify=replace(strict.verify, block_report_warnings=False),
        )
        self.assertEqual(
            relaxed_warnings.to_dict()["verify"],
            {"block_report_warnings": False},
        )
        self.assertFalse(
            PipelinePolicy.from_dict(
                relaxed_warnings.to_dict()
            ).verify.block_report_warnings
        )

    def test_strict_policy_blocks_when_actual_diff_is_missing_from_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session_id = _prepare_verify_session(root, PipelinePolicy.default())
            _write_report_state(root)
            _commit_current_fixture(root)
            (root / "outside.txt").write_text("dirty\n", encoding="utf-8")

            result = verify_phase(session_id, root=root, actor="tester")
            phase = result.data["phase_result"]
            artifacts = phase["artifacts"]

            self.assertTrue(result.ok)
            self.assertEqual(phase["status"], "blocked")
            self.assertEqual(artifacts["blocked_by"], CODE_DIFF_MISMATCH)
            self.assertIn(
                "outside.txt",
                artifacts["report_git_diff_comparison"]["missing_from_report"],
            )
            self.assertEqual(
                artifacts["verify_evidence"]["git_diff_gate"]["status"],
                BLOCKED,
            )
            self.assertNotIn(SKIPPED_GATES_KEY, artifacts["verify_evidence"])

    def test_relaxed_policy_skips_git_diff_gates_after_report_passes(self):
        strict = PipelinePolicy.default()
        relaxed = replace(
            strict,
            name="relaxed_verify",
            verify=replace(strict.verify, run_git_diff_gates=False),
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session_id = _prepare_verify_session(root, relaxed)
            _write_report_state(root)
            _commit_current_fixture(root)
            (root / "outside.txt").write_text("dirty\n", encoding="utf-8")

            result = verify_phase(session_id, root=root, actor="tester")
            phase = result.data["phase_result"]
            artifacts = phase["artifacts"]
            snapshot = _policy_snapshot(root)

            self.assertTrue(result.ok)
            self.assertEqual(phase["status"], "passed")
            self.assertEqual(snapshot["verify"], {"run_git_diff_gates": False})
            self.assertEqual(
                artifacts[GIT_DIFF_GATES_POLICY_KEY],
                {
                    "run_git_diff_gates": False,
                    "mode": "relaxed",
                    "reason": "policy.verify.run_git_diff_gates is false",
                },
            )
            self.assertEqual(
                [gate["name"] for gate in artifacts[SKIPPED_GATES_KEY]],
                list(GIT_DIFF_BASED_GATE_NAMES),
            )
            self.assertNotIn("git_diff_gate", artifacts["verify_evidence"])
            self.assertEqual(
                artifacts["verify_evidence"][SKIPPED_GATES_KEY],
                artifacts[SKIPPED_GATES_KEY],
            )

    def test_default_policy_blocks_when_report_gate_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session_id = _prepare_verify_session(root, PipelinePolicy.default())
            _write_report_state(root, warnings=["advisory warning"])
            _commit_current_fixture(root)

            result = verify_phase(session_id, root=root, actor="tester")
            phase = result.data["phase_result"]
            artifacts = phase["artifacts"]

        self.assertTrue(result.ok)
        self.assertEqual(phase["status"], "blocked")
        self.assertEqual(artifacts["blocked_by"], CODEX_REPORT_WARN)
        self.assertEqual(artifacts["report_gate_status"], "warn")
        self.assertEqual(
            artifacts[REPORT_WARNING_POLICY_KEY],
            {
                "block_report_warnings": True,
                "decision": "blocked",
                "reason": "",
                "report_gate_status": "warn",
                "report_gate_code": CODEX_REPORT_WARN,
            },
        )

    def test_relaxed_report_warning_policy_allows_advisory_warning(self):
        strict = PipelinePolicy.default()
        relaxed = replace(
            strict,
            name="relaxed_report_warnings",
            verify=replace(strict.verify, block_report_warnings=False),
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session_id = _prepare_verify_session(root, relaxed)
            _write_report_state(root, warnings=["advisory warning"])
            _commit_current_fixture(root)

            result = verify_phase(session_id, root=root, actor="tester")
            phase = result.data["phase_result"]
            artifacts = phase["artifacts"]
            warning_policy = artifacts[REPORT_WARNING_POLICY_KEY]

        self.assertTrue(result.ok)
        self.assertEqual(phase["status"], "passed")
        self.assertEqual(artifacts["report_gate_status"], "warn")
        self.assertEqual(warning_policy["block_report_warnings"], False)
        self.assertEqual(warning_policy["decision"], "advisory")
        self.assertEqual(
            warning_policy["reason"],
            "policy.verify.block_report_warnings is false",
        )
        self.assertEqual(
            artifacts["verify_evidence"][REPORT_WARNING_POLICY_KEY],
            warning_policy,
        )
        self.assertEqual(
            result.data[REPORT_WARNING_POLICY_KEY],
            warning_policy,
        )

    def test_report_failures_remain_blocking_with_report_warnings_relaxed(self):
        strict = PipelinePolicy.default()
        relaxed = replace(
            strict,
            name="relaxed_report_warnings",
            verify=replace(strict.verify, block_report_warnings=False),
        )
        for policy in (strict, relaxed):
            with self.subTest(policy=policy.name):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    session_id = _prepare_verify_session(root, policy)
                    _write_report_state(root, blockers=["must fix"])

                    result = verify_phase(session_id, root=root, actor="tester")
                    phase = result.data["phase_result"]
                    artifacts = phase["artifacts"]

                self.assertTrue(result.ok)
                self.assertEqual(phase["status"], "blocked")
                self.assertEqual(artifacts["blocked_by"], CODE_BLOCKERS_PRESENT)
                self.assertEqual(artifacts["report_gate_status"], "fail")
                self.assertNotIn(REPORT_WARNING_POLICY_KEY, artifacts)

    def test_invalid_report_gate_status_blocks_when_report_warnings_relaxed(self):
        strict = PipelinePolicy.default()
        relaxed = replace(
            strict,
            name="relaxed_report_warnings",
            verify=replace(strict.verify, block_report_warnings=False),
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session_id = _prepare_verify_session(root, relaxed)
            _write_report_state(root)
            report_gate = _FakeReportGate(status="invalid")

            with mock.patch(
                "ai_project_ctl.pipeline.verify_phase.evaluate_report_gate",
                return_value=report_gate,
            ):
                result = verify_phase(session_id, root=root, actor="tester")
            phase = result.data["phase_result"]
            artifacts = phase["artifacts"]

        self.assertTrue(result.ok)
        self.assertEqual(phase["status"], "blocked")
        self.assertEqual(artifacts["blocked_by"], "REPORT_GATE_UNKNOWN_STATUS")
        self.assertEqual(artifacts["report_gate_status"], "invalid")

    def test_allowed_files_gate_still_blocks_out_of_scope_actual_diff(self):
        gate = evaluate_allowed_files_gate(
            root="/repo",
            changed_files=("docs/out-of-scope.md",),
            allowed_files=("src/**",),
            generated_files=(),
        )

        self.assertEqual(gate.status, BLOCKED)
        self.assertEqual(gate.code, CODE_ALLOWED_FILES_OUT_OF_SCOPE)
        self.assertEqual(gate.out_of_scope_files, ("docs/out-of-scope.md",))


class _Report:
    changed_files = ()
    generated_files = ()


class _FakeReportGate:
    def __init__(self, *, status: str) -> None:
        self.status = status
        self.code = "CODEX_REPORT_UNKNOWN"
        self.reason = "Unknown report status."
        self.report_id = "RPT-001"
        self.task_id = "TASK-001"
        self.changed_files = ()
        self.generated_files = ()
        self.checks = ()

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "code": self.code,
            "reason": self.reason,
            "report_id": self.report_id,
            "task_id": self.task_id,
            "issues": [],
            "warnings": [],
            "changed_files": [],
            "generated_files": [],
            "token_usage": {},
            "checks": [],
        }


def _prepare_verify_session(root: Path, policy: PipelinePolicy) -> str:
    _write_task_state(root)
    result = create_session(
        root=root,
        actor="tester",
        policy=policy,
        current_task_id="TASK-001",
        current_task_ref="APP-01",
    )
    if not result.ok:
        raise AssertionError(result.errors)
    session_id = result.data["session_id"]
    collect = record_phase_result(
        session_id,
        PhaseResult.passed(
            "collect_report",
            artifacts={
                "session_id": session_id,
                "task_id": "TASK-001",
                "report_id": "RPT-001",
                "report_found": True,
            },
        ),
        root=root,
        actor="tester",
        task_id="TASK-001",
        command="test.collect_report",
    )
    if not collect.ok:
        raise AssertionError(collect.errors)
    return session_id


def _write_task_state(root: Path) -> None:
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "tasks.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "current_task_id": "TASK-001",
                "tasks": [
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "uid": "uid_task_001",
                        "legacy_id": "TASK-001",
                        "aliases": ["TASK-001"],
                        "title": "Verify task",
                        "status": "in_progress",
                        "epic_id": "EPIC-001",
                        "priority": 1,
                        "order": 1,
                        "local_seq": 1,
                        "depends_on": [],
                        "allowed_files": ["src/**"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def _write_report_state(
    root: Path,
    *,
    warnings: list[str] | None = None,
    blockers: list[str] | None = None,
    checks: list[dict] | None = None,
) -> None:
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    report_checks = checks
    if report_checks is None:
        report_checks = [
            {
                "name": "unit",
                "command": "python -m unittest tests.pipeline.test_verify_phase",
                "result": "pass",
                "duration_sec": 0.1,
                "blocking": True,
            }
        ]
    report = {
        "schema_version": 1,
        "task_id": "TASK-001",
        "task_ref": "APP-01",
        "implementation_summary": "Verified task output.",
        "changed_files": [],
        "generated_files": [],
        "checks": report_checks,
        "warnings": list(warnings or []),
        "blockers": list(blockers or []),
        "notes": [],
        "owner_decision_required": False,
    }
    (state_dir / "task_reports.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "latest_by_task": {"TASK-001": "RPT-001"},
                "reports": [
                    {
                        "id": "RPT-001",
                        "task_id": "TASK-001",
                        "task_ref": "APP-01",
                        "submitted_at": "2026-06-25T00:00:00Z",
                        "submitted_by": "tester",
                        "source_file": "/tmp/report.json",
                        "report": report,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def _commit_current_fixture(root: Path) -> None:
    _run_git(root, "init")
    _run_git(root, "add", "AI_PROJECT")
    _run_git(
        root,
        "-c",
        "user.email=tester@example.com",
        "-c",
        "user.name=Tester",
        "commit",
        "-m",
        "fixture",
    )


def _run_git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )


def _policy_snapshot(root: Path) -> dict:
    state = json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))
    return state["sessions"][0]["policy_snapshot"]


if __name__ == "__main__":
    unittest.main()

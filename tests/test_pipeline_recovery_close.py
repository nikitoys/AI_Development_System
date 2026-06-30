import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from ai_project_ctl.core.result import CommandResult
from ai_project_ctl.pipeline.batch import run_until_blocker
from ai_project_ctl.pipeline.close_phase import close_phase
from ai_project_ctl.pipeline.git_commit import (
    CODE_COMMIT_CREATED,
    CODE_READY,
    PASS as COMMIT_PASS,
    CommitReadinessResult,
    LocalCommitResult,
)
from ai_project_ctl.pipeline.phase import PhaseResult
from ai_project_ctl.pipeline.policy import (
    BatchPolicy,
    apply_codex_review_requirement,
    policy_preset,
)
from ai_project_ctl.pipeline.report_phase import collect_report_phase
from ai_project_ctl.pipeline.report_recovery import submit_report_gate_recovery_report
from ai_project_ctl.pipeline.review_phase import review_phase
from ai_project_ctl.pipeline.session import create_session, record_phase_result
from ai_project_ctl.pipeline.state import pipeline_state_path
from ai_project_ctl.pipeline.verify_phase import (
    REPORT_WARNING_POLICY_KEY,
    SKIPPED_GATES_KEY,
    verify_phase,
)


TASK_ID = "TASK-001"
TASK_REF = "APP-01"
CHANGED_FILE = "ai_project_ctl/pipeline/report_gate.py"
EXECUTE_REPORT_ID = "RPT-001"
RECOVERY_REPORT_ID = "RPT-002"


def completed(stdout="OK\n", returncode=0, stderr=""):
    return subprocess.CompletedProcess(
        args=[],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def recovery_close_policy(name="recovery_close_policy"):
    supervised = policy_preset("supervised_local_commit")
    policy = apply_codex_review_requirement(supervised, require_codex_review=False)
    return replace(
        policy,
        name=name,
        verify=replace(
            policy.verify,
            allow_report_warnings=True,
            block_report_warnings=False,
            run_git_diff_gates=False,
        ),
        batch=BatchPolicy(max_steps=20, max_failures=1),
    )


def write_project_state(root: Path, *, task_status: str = "in_review") -> None:
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
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
                "current_task_id": TASK_ID,
                "tasks": [
                    {
                        "id": TASK_ID,
                        "ref": TASK_REF,
                        "uid": "uid_task_001",
                        "legacy_id": TASK_ID,
                        "aliases": [TASK_ID],
                        "title": "Recovery close regression",
                        "summary": "Exercise recovery report close path.",
                        "description": "",
                        "scope": ["Close through owner-confirmed report recovery."],
                        "out_of_scope": ["Do not bypass close preflight."],
                        "acceptance_criteria": ["Recovery close reaches close."],
                        "review_instructions": [
                            "Verify skipped review evidence remains valid."
                        ],
                        "status": task_status,
                        "epic_id": "EPIC-001",
                        "priority": 1,
                        "order": 1,
                        "local_seq": 1,
                        "depends_on": [],
                        "allowed_files": [CHANGED_FILE, "tests/**"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (state_dir / "evolution.json").write_text(
        json.dumps({"schema_version": 1, "revision": 1, "changes": []}),
        encoding="utf-8",
    )


def create_pipeline_session(root: Path) -> str:
    result = create_session(
        root=root,
        actor="tester",
        policy=recovery_close_policy(),
        current_task_id=TASK_ID,
        current_task_ref=TASK_REF,
        auto_close_note="Owner approved auto-close for recovery close regression.",
    )
    if not result.ok:
        raise AssertionError(result.errors)
    return str(result.data["session_id"])


def report_payload(*, include_token_usage: bool = True) -> dict:
    report = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "task_ref": TASK_REF,
        "reported_task_id": TASK_ID,
        "reported_task_ref": TASK_REF,
        "implementation_summary": "Implemented the selected task.",
        "changed_files": [CHANGED_FILE],
        "generated_files": [],
        "checks": [
            {
                "name": "focused recovery close regression",
                "command": "python -m unittest tests.test_pipeline_recovery_close",
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
    }
    if include_token_usage:
        report["token_usage"] = {
            "prompt_tokens": 100,
            "context_tokens": 20,
            "token_count_strategy": "test_fixture",
            "token_count_estimated": True,
            "token_count_unavailable": False,
            "token_count_unavailable_reason": "",
        }
    return report


def report_record(report_id: str, *, submitted_at: str, report: dict) -> dict:
    return {
        "id": report_id,
        "task_id": TASK_ID,
        "task_ref": TASK_REF,
        "submitted_at": submitted_at,
        "submitted_by": "tester",
        "source_file": "/tmp/report.json",
        "report": report,
    }


def write_report_state(
    root: Path,
    *,
    latest_report_id: str,
    reports: list[dict],
) -> None:
    path = root / "AI_PROJECT" / "state" / "task_reports.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "created_at": "2026-06-30T00:00:00Z",
                "updated_at": "2026-06-30T00:00:10Z",
                "latest_by_task": {TASK_ID: latest_report_id},
                "reports": reports,
            }
        ),
        encoding="utf-8",
    )


def record_prepare_phase(root: Path, session_id: str) -> None:
    _record_phase(
        root,
        session_id,
        PhaseResult.passed(
            "prepare",
            reason="Task prepared for recovery close regression.",
            next_action="Run execute.",
            artifacts={
                "session_id": session_id,
                "task_id": TASK_ID,
                "task_ref": TASK_REF,
            },
        ),
    )


def record_execute_report(root: Path, session_id: str, *, report_id: str) -> None:
    _record_phase(
        root,
        session_id,
        PhaseResult.passed(
            "execute",
            reason="Execution recorded original structured report evidence.",
            next_action="Run collect-report.",
            artifacts={
                "session_id": session_id,
                "task_id": TASK_ID,
                "task_ref": TASK_REF,
                "execute_started_at": "2026-06-30T00:00:00Z",
                "execute_finished_at": "2026-06-30T00:00:05Z",
                "before_report_id": "",
                "after_report_id": report_id,
                "report_id": report_id,
                "execute_evidence": {
                    "started_at": "2026-06-30T00:00:00Z",
                    "finished_at": "2026-06-30T00:00:05Z",
                    "before_report_id": "",
                    "after_report_id": report_id,
                    "report_id": report_id,
                },
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
        command="pipeline.phase.{}".format(phase.phase),
    )
    if not result.ok:
        raise AssertionError(result.errors)


def latest_session(root: Path) -> dict:
    state = json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))
    return state["sessions"][0]


def phases_by_name(root: Path) -> dict[str, dict]:
    return {phase["phase"]: phase for phase in latest_session(root)["phase_history"]}


def fake_close_workflow(*args, **kwargs) -> CommandResult:
    result = CommandResult.success(
        command="pipeline.review_close_policy",
        domain="pipeline",
        message="Task close workflow reached.",
        data={"decision": {"action": "close_task"}, "workflows": []},
    )
    result.changed_files = [
        "AI_PROJECT/state/tasks.json",
        "AI_PROJECT/events/task-events.jsonl",
    ]
    result.generated_files = [
        "AI_PROJECT/generated/CODEX_TASKS.md",
        "AI_PROJECT/generated/CODEX_CURRENT.md",
        "AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md",
    ]
    result.events = ["AI_PROJECT/events/task-events.jsonl"]
    return result


def fake_context_refresh(*, task_id: str, root: Path, actor: str) -> CommandResult:
    result = CommandResult.success(
        command="pipeline.close.context_refresh",
        domain="context",
        message="Context Pack refreshed after task close.",
        data={"task_id": task_id},
    )
    result.changed_files = ["AI_PROJECT/events/context-events.jsonl"]
    result.generated_files = [
        "AI_PROJECT/generated/CONTEXT_PACK.md",
        "AI_PROJECT/generated/CONTEXT_STATUS.md",
    ]
    result.events = ["AI_PROJECT/events/context-events.jsonl"]
    return result


def fake_local_commit(*, task_id: str, **kwargs) -> LocalCommitResult:
    readiness = CommitReadinessResult(
        status=COMMIT_PASS,
        code=CODE_READY,
        reason="Local commit readiness is green.",
        task_id=task_id,
        approved_files=(CHANGED_FILE,),
    )
    return LocalCommitResult(
        status=COMMIT_PASS,
        code=CODE_COMMIT_CREATED,
        reason="Local commit created.",
        task_id=task_id,
        commit_hash="abc1234deadbeef",
        staged_files=(CHANGED_FILE,),
        message="TASK-001 recovery close",
        readiness=readiness,
    )


class PipelineRecoveryCloseTests(unittest.TestCase):
    def test_owner_recovery_report_collect_verify_skipped_review_close_and_clean_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root)
            write_report_state(
                root,
                latest_report_id=EXECUTE_REPORT_ID,
                reports=[
                    report_record(
                        EXECUTE_REPORT_ID,
                        submitted_at="2026-06-30T00:00:05Z",
                        report=report_payload(include_token_usage=False),
                    )
                ],
            )
            session_id = create_pipeline_session(root)
            record_prepare_phase(root, session_id)
            record_execute_report(root, session_id, report_id=EXECUTE_REPORT_ID)

            collect_original = collect_report_phase(
                session_id,
                root=root,
                actor="tester",
            )
            verify_blocked = verify_phase(session_id, root=root, actor="tester")
            recovery = submit_report_gate_recovery_report(
                session_id,
                root=root,
                actor="tester",
                expected_task_id=TASK_ID,
                expected_task_ref=TASK_REF,
                recovery_reason=(
                    "Owner confirmed the missing token evidence was recovered "
                    "from reviewed report-gate context."
                ),
                owner_confirmed=True,
            )
            collect_recovery = collect_report_phase(
                session_id,
                root=root,
                actor="tester",
                allow_existing_report=True,
            )
            verify_recovery = verify_phase(session_id, root=root, actor="tester")
            review = review_phase(session_id, root=root, actor="tester")

            git_calls = []

            def clean_post_commit_runner(argv):
                args = list(argv)
                if args == ["git", "status", "--short", "--untracked-files=all"]:
                    git_calls.append(args)
                    return completed(stdout="")
                raise AssertionError("unexpected post-commit command: {}".format(args))

            with (
                patch(
                    "ai_project_ctl.pipeline.close_phase.run_review_close_workflow",
                    side_effect=fake_close_workflow,
                ),
                patch(
                    "ai_project_ctl.pipeline.close_phase._refresh_context_after_close",
                    side_effect=fake_context_refresh,
                ),
                patch(
                    "ai_project_ctl.pipeline.close_phase.run_local_commit",
                    side_effect=fake_local_commit,
                ),
            ):
                closed = run_until_blocker(
                    session_id,
                    root=root,
                    actor="tester",
                    confirmed=True,
                    runner=clean_post_commit_runner,
                )

            phases = phases_by_name(root)
            execute_artifacts = phases["execute"]["artifacts"]
            collect_artifacts = collect_recovery.data["phase_result"]["artifacts"]
            verify_artifacts = verify_recovery.data["phase_result"]["artifacts"]
            review_phase_payload = review.data["phase_result"]
            review_artifacts = review_phase_payload["artifacts"]
            close_phase_payload = phases["close"]
            close_artifacts = close_phase_payload["artifacts"]

            self.assertTrue(collect_original.ok, collect_original.errors)
            self.assertEqual(
                collect_original.data["phase_result"]["artifacts"]["report_id"],
                EXECUTE_REPORT_ID,
            )
            self.assertEqual(
                verify_blocked.data["phase_result"]["artifacts"]["blocked_by"],
                "CODEX_REPORT_TOKEN_USAGE_REQUIRED",
            )
            self.assertTrue(recovery.ok, recovery.errors)
            self.assertEqual(recovery.data["replaced_report_id"], EXECUTE_REPORT_ID)
            self.assertEqual(recovery.data["recovery_report_id"], RECOVERY_REPORT_ID)
            self.assertEqual(execute_artifacts["report_id"], EXECUTE_REPORT_ID)
            self.assertEqual(collect_artifacts["report_id"], RECOVERY_REPORT_ID)
            self.assertEqual(
                collect_artifacts["recovery"],
                {
                    "session_id": session_id,
                    "task_id": TASK_ID,
                    "owner_confirmed": True,
                    "recovery_basis": "recovery_override",
                    "recovery_report_id": RECOVERY_REPORT_ID,
                    "replaced_execute_report_id": EXECUTE_REPORT_ID,
                },
            )
            self.assertEqual(verify_recovery.data["phase_result"]["status"], "passed")
            self.assertEqual(verify_artifacts["report_id"], RECOVERY_REPORT_ID)
            self.assertEqual(
                verify_artifacts[REPORT_WARNING_POLICY_KEY]["decision"],
                "allowed",
            )
            self.assertEqual(
                [gate["status"] for gate in verify_artifacts[SKIPPED_GATES_KEY]],
                ["skipped", "skipped", "skipped"],
            )
            self.assertEqual(review_phase_payload["status"], "skipped")
            self.assertFalse(review_artifacts["codex_review_required"])
            self.assertFalse(review_artifacts["policy_require_codex_review"])
            self.assertEqual(review_artifacts["skip_reason"], "disabled_by_policy")
            self.assertEqual(review_artifacts["review_status"], "skipped")
            self.assertFalse(review_artifacts["review_prompt_built"])
            self.assertFalse(review_artifacts["review_prompt_returned"])

            self.assertTrue(closed.ok, closed.errors)
            self.assertEqual(closed.data["stop_code"], "QUEUE_COMPLETE")
            self.assertEqual(closed.data["commit_hash"], "abc1234deadbeef")
            self.assertEqual(closed.data["close_status"]["outcome"], "closed_with_local_commit")
            self.assertEqual(closed.data["close_status"]["commit_status"], "pass")
            self.assertEqual(closed.data["step_results"][0]["dispatched_phase"], "close")
            self.assertEqual(closed.data["step_results"][0]["phase_status"], "passed")
            self.assertNotIn("post_commit_worktree", closed.data)
            self.assertEqual(git_calls, [["git", "status", "--short", "--untracked-files=all"]])
            self.assertEqual(close_phase_payload["status"], "running")
            self.assertNotEqual(close_artifacts.get("blocked_by"), "CLOSE_PREFLIGHT_INCOMPLETE")
            self.assertEqual(close_artifacts["missing_gates"], [])
            self.assertEqual(
                close_artifacts["report_consistency"]["recovery_replacement"]["status"],
                "accepted",
            )

    def test_accidental_report_mismatch_without_recovery_metadata_blocks_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root)
            write_report_state(
                root,
                latest_report_id=RECOVERY_REPORT_ID,
                reports=[
                    report_record(
                        EXECUTE_REPORT_ID,
                        submitted_at="2026-06-30T00:00:05Z",
                        report=report_payload(),
                    ),
                    report_record(
                        RECOVERY_REPORT_ID,
                        submitted_at="2026-06-30T00:00:10Z",
                        report=report_payload(),
                    ),
                ],
            )
            session_id = create_pipeline_session(root)
            record_prepare_phase(root, session_id)
            record_execute_report(root, session_id, report_id=EXECUTE_REPORT_ID)

            collect = collect_report_phase(session_id, root=root, actor="tester")
            verify = verify_phase(session_id, root=root, actor="tester")
            review = review_phase(session_id, root=root, actor="tester")
            result = close_phase(
                session_id,
                root=root,
                actor="tester",
                confirmed=True,
            )

            phases = phases_by_name(root)
            artifacts = result.data["phase_result"]["artifacts"]
            review_artifacts = review.data["phase_result"]["artifacts"]

            self.assertTrue(collect.ok, collect.errors)
            self.assertEqual(collect.data["phase_result"]["status"], "passed")
            self.assertEqual(
                collect.data["phase_result"]["artifacts"]["report_id"],
                RECOVERY_REPORT_ID,
            )
            self.assertNotIn("recovery", collect.data["phase_result"]["artifacts"])
            self.assertEqual(verify.data["phase_result"]["status"], "passed")
            self.assertEqual(review.data["phase_result"]["status"], "skipped")
            self.assertEqual(review_artifacts["skip_reason"], "disabled_by_policy")

            self.assertTrue(result.ok, result.errors)
            self.assertEqual(result.data["phase_result"]["status"], "blocked")
            self.assertEqual(artifacts["blocked_by"], "CLOSE_PREFLIGHT_INCOMPLETE")
            self.assertIn("close:REPORT_EVIDENCE_MISMATCH", artifacts["missing_gate_codes"])
            self.assertEqual(artifacts["report_consistency"]["status"], "blocked")
            self.assertEqual(
                artifacts["report_consistency"]["recovery_replacement"],
                {
                    "status": "missing",
                    "reason": "collect_report_recovery_missing",
                },
            )
            self.assertEqual(phases["execute"]["artifacts"]["report_id"], EXECUTE_REPORT_ID)
            self.assertEqual(phases["collect_report"]["artifacts"]["report_id"], RECOVERY_REPORT_ID)
            self.assertEqual(phases["verify"]["artifacts"]["report_id"], RECOVERY_REPORT_ID)
            self.assertEqual(phases["review"]["artifacts"]["report_id"], RECOVERY_REPORT_ID)


if __name__ == "__main__":
    unittest.main()

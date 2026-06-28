import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline.codex_review import CodexReviewResult
from ai_project_ctl.pipeline.git_commit import (
    CODE_READY as COMMIT_READINESS_PASS,
    REQUIRED_MACHINE_CHECKS,
    evaluate_commit_readiness,
)
from ai_project_ctl.pipeline.machine_review import (
    MachineCheckEvidence,
    MachineReviewResult,
)
from ai_project_ctl.pipeline.report_builder import build_task_report_payload
from ai_project_ctl.pipeline.report_gate import (
    CODE_PASS as REPORT_GATE_PASS_CODE,
    PASS as REPORT_GATE_PASS,
    evaluate_report_gate,
)
from ai_project_ctl.pipeline.policy import policy_preset
from ai_project_ctl.task_reports import REPORT_CHECK_RESULTS, submit_task_report


def task():
    return {
        "id": "TASK-167",
        "uid": "tsk_8af8c1dfb7bc",
        "ref": "PIPEF-86",
        "legacy_id": "TASK-167",
        "aliases": ["TASK-167"],
    }


def summary(**overrides):
    payload = {
        "implementation_summary": "Implemented evidence-based report building.",
        "notes": ["Builder used trusted pipeline evidence."],
        "warnings": [],
        "blockers": [],
    }
    payload.update(overrides)
    return payload


def adapter(**overrides):
    payload = {
        "status": "passed",
        "code": "CODE_LOCAL_COMMAND_PASSED",
        "reason": "local_command_completed_with_report",
        "command_ref": "codex exec",
        "duration_sec": 1.25,
    }
    payload.update(overrides)
    return payload


def submit_payload(root: Path, payload: dict, task_payload: dict | None = None):
    selected_task = task_payload or task()
    task_state = {"tasks": [selected_task]}
    return submit_task_report(
        root=root,
        tasks_state=task_state,
        task=selected_task,
        report_payload=payload,
        source_file=root / "report.json",
        actor="tester",
    )


def write_task_state(root: Path, selected_task: dict) -> None:
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "tasks.json").write_text(
        json.dumps({"schema_version": 1, "tasks": [selected_task]}),
        encoding="utf-8",
    )


def passing_machine_review(report_id: str = "RPT-001") -> MachineReviewResult:
    return MachineReviewResult(
        status="pass",
        code="MACHINE_REVIEW_PASS",
        reason="Machine Review passed.",
        task_id="TASK-167",
        report_id=report_id,
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


def approved_codex_review(report_id: str = "RPT-001") -> CodexReviewResult:
    return CodexReviewResult(
        status="pass",
        code="CODEX_REVIEW_PASS",
        reason="Codex Review approved.",
        verdict="APPROVE",
        task_id="TASK-167",
        report_id=report_id,
        review_id="REV-001",
        prompt_sha256="0" * 64,
        prompt_bytes=1,
    )


class PipelineReportBuilderTests(unittest.TestCase):
    def test_successful_adapter_result_builds_valid_task_report_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            payload = build_task_report_payload(
                session={"id": "PSESS-001"},
                task=task(),
                adapter_result=adapter(),
                summary=summary(
                    task_id="MALICIOUS",
                    token_usage={"prompt_tokens": -1},
                ),
                policy_evidence={
                    "changed_files": ["ai_project_ctl/pipeline/report_builder.py"],
                    "checks": [
                        {
                            "name": "unit",
                            "command": "python -m unittest tests.pipeline.test_report_builder",
                            "result": "passed",
                            "duration_sec": 0.5,
                            "blocking": True,
                        }
                    ],
                    "token_usage": {
                        "prompt_tokens": 12,
                        "context_tokens": 34,
                        "token_count_strategy": "test_fixture",
                        "token_count_estimated": True,
                    },
                },
            )

            result = submit_payload(root, payload)
            state = json.loads(
                (root / "AI_PROJECT" / "state" / "task_reports.json").read_text(
                    encoding="utf-8"
                )
            )
            report = state["reports"][0]["report"]

            self.assertEqual(result.report_id, "RPT-001")
            self.assertEqual(payload["task_id"], "TASK-167")
            self.assertEqual(payload["task_ref"], "PIPEF-86")
            self.assertEqual(report["reported_task_id"], "TASK-167")
            self.assertEqual(report["reported_task_ref"], "PIPEF-86")
            self.assertEqual(
                payload["changed_files"],
                ["ai_project_ctl/pipeline/report_builder.py"],
            )
            self.assertEqual(payload["token_usage"]["prompt_tokens"], 12)
            self.assertNotIn("MALICIOUS", json.dumps(payload))

    def test_preserves_summary_changed_files_and_dedupes_fallback_sources(self):
        payload = build_task_report_payload(
            session={"changed_files": ["app/session.py", "app/summary.py"]},
            task=task(),
            adapter_result=adapter(),
            summary=summary(
                changed_files=["app/summary.py", "tests/test_summary.py"]
            ),
            policy_evidence={
                "changed_files": ["tests/test_summary.py", "app/policy.py"]
            },
        )

        self.assertEqual(
            payload["changed_files"],
            [
                "app/summary.py",
                "tests/test_summary.py",
                "app/policy.py",
                "app/session.py",
            ],
        )

    def test_summary_file_lists_reach_report_gate_and_commit_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            changed_files = [
                "ai_project_ctl/pipeline/report_builder.py",
                "tests/pipeline/test_report_builder.py",
            ]
            generated_files = ["AI_PROJECT/generated/CODEX_STATUS.md"]
            selected_task = {
                **task(),
                "status": "done",
                "allowed_files": changed_files,
            }
            policy = policy_preset("supervised_local_commit")
            write_task_state(root, selected_task)
            payload = build_task_report_payload(
                session={},
                task=selected_task,
                adapter_result=adapter(),
                summary=summary(
                    changed_files=changed_files,
                    generated_files=generated_files,
                ),
                policy_evidence={},
            )
            submission = submit_payload(root, payload, task_payload=selected_task)
            report_gate = evaluate_report_gate(
                root=root,
                task=selected_task,
                policy=policy,
            )
            git_calls = []

            def git_status_runner(argv):
                git_calls.append(list(argv))
                return subprocess.CompletedProcess(
                    args=list(argv),
                    returncode=0,
                    stdout=(
                        " M ai_project_ctl/pipeline/report_builder.py\n"
                        " M tests/pipeline/test_report_builder.py\n"
                        " M AI_PROJECT/generated/CODEX_STATUS.md\n"
                    ),
                    stderr="",
                )

            readiness = evaluate_commit_readiness(
                root=root,
                task_id="TASK-167",
                policy=policy,
                report_gate=report_gate,
                machine_review=passing_machine_review(
                    report_id=submission.report_id
                ),
                codex_review=approved_codex_review(report_id=submission.report_id),
                runner=git_status_runner,
            )

            self.assertEqual(submission.report_id, "RPT-001")
            self.assertEqual(payload["changed_files"], changed_files)
            self.assertEqual(payload["generated_files"], generated_files)
            self.assertEqual(report_gate.status, REPORT_GATE_PASS)
            self.assertEqual(report_gate.code, REPORT_GATE_PASS_CODE)
            self.assertEqual(report_gate.changed_files, tuple(changed_files))
            self.assertEqual(report_gate.generated_files, tuple(generated_files))
            self.assertTrue(readiness.ok, readiness.to_dict())
            self.assertEqual(readiness.code, COMMIT_READINESS_PASS)
            self.assertEqual(
                readiness.approved_files,
                (
                    "AI_PROJECT/generated/CODEX_STATUS.md",
                    "ai_project_ctl/pipeline/report_builder.py",
                    "tests/pipeline/test_report_builder.py",
                ),
            )
            self.assertEqual(
                git_calls,
                [["git", "status", "--short", "--untracked-files=all"]],
            )

    def test_preserves_summary_generated_files_and_dedupes_fallback_sources(self):
        payload = build_task_report_payload(
            session={"generated_files": ["AI_PROJECT/generated/SESSION.md"]},
            task=task(),
            adapter_result=adapter(),
            summary=summary(
                generated_files=[
                    "AI_PROJECT/generated/CODEX_STATUS.md",
                    "AI_PROJECT/generated/REPORT.md",
                ]
            ),
            policy_evidence={
                "generated_files": [
                    "AI_PROJECT/generated/REPORT.md",
                    "AI_PROJECT/generated/POLICY.md",
                ],
                "protected_files_gate": {
                    "allowed_protected_files": [
                        "AI_PROJECT/generated/CODEX_STATUS.md",
                        "AI_PROJECT/generated/PROTECTED.md",
                    ]
                },
            },
        )

        self.assertEqual(
            payload["generated_files"],
            [
                "AI_PROJECT/generated/CODEX_STATUS.md",
                "AI_PROJECT/generated/REPORT.md",
                "AI_PROJECT/generated/POLICY.md",
                "AI_PROJECT/generated/PROTECTED.md",
                "AI_PROJECT/generated/SESSION.md",
            ],
        )

    def test_does_not_extract_file_lists_from_implementation_summary_text(self):
        payload = build_task_report_payload(
            session={},
            task=task(),
            adapter_result=adapter(),
            summary=summary(
                implementation_summary=(
                    "Changed ai_project_ctl/pipeline/report_builder.py in prose only."
                )
            ),
            policy_evidence={},
        )

        self.assertEqual(payload["changed_files"], [])
        self.assertEqual(payload["generated_files"], [])

    def test_uses_task_identity_when_summary_omits_identity_fields(self):
        payload = build_task_report_payload(
            session={},
            task=task(),
            adapter_result=adapter(),
            summary=summary(),
            policy_evidence={},
        )

        self.assertEqual(payload["task_id"], "TASK-167")
        self.assertEqual(payload["task_ref"], "PIPEF-86")
        self.assertEqual(
            payload["implementation_summary"],
            "Implemented evidence-based report building.",
        )

    def test_normalizes_not_run_and_blocked_check_results_to_allowed_values(self):
        payload = build_task_report_payload(
            session={},
            task=task(),
            adapter_result=adapter(status="not_run"),
            summary=summary(),
            policy_evidence={
                "checks": [
                    {
                        "name": "project_tests",
                        "result": "not_run",
                        "blocking": True,
                    }
                ],
                "token_budget_gate": {
                    "status": "blocked",
                    "reason": "token evidence unavailable",
                },
            },
        )

        results = [check["result"] for check in payload["checks"]]
        self.assertNotIn("not_run", results)
        for result in results:
            self.assertIn(result, REPORT_CHECK_RESULTS)

    def test_defaults_token_usage_to_allowed_object_when_precise_evidence_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            payload = build_task_report_payload(
                session={},
                task=task(),
                adapter_result=adapter(),
                summary=summary(),
                policy_evidence={
                    "token_budget": {
                        "max_context_tokens": 24000,
                        "reserved_output_tokens": 1000,
                        "min_remaining_tokens": 6000,
                    }
                },
            )

            submit_payload(root, payload)
            token_usage = payload["token_usage"]

            self.assertEqual(token_usage["prompt_tokens"], 0)
            self.assertEqual(token_usage["context_tokens"], 0)
            self.assertEqual(token_usage["max_context_tokens"], 24000)
            self.assertEqual(token_usage["reserved_output_tokens"], 1000)
            self.assertEqual(token_usage["min_remaining_tokens"], 6000)
            self.assertEqual(
                token_usage["token_count_strategy"],
                "pipeline_report_builder_default",
            )
            self.assertTrue(token_usage["token_count_estimated"])


if __name__ == "__main__":
    unittest.main()

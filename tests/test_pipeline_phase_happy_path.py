import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline import policy_preset
from ai_project_ctl.pipeline.codex_adapter import (
    CODE_LOCAL_COMMAND_PASSED,
    CodexAdapterResult,
)
from ai_project_ctl.pipeline.runner import run_next
from ai_project_ctl.pipeline.session import create_session
from ai_project_ctl.pipeline.state import pipeline_state_path
from ai_project_ctl.task_reports import submit_task_report


TASK_ID = "TASK-001"
TASK_REF = "PIPE-001"
CHANGED_FILE = "tests/test_pipeline_phase_happy_path.py"


class PipelinePhaseHappyPathTests(unittest.TestCase):
    def test_fake_codex_report_advances_pipeline_through_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_project_state(root)
            _write_fresh_prepare_artifacts(root)
            policy = policy_preset("supervised_executable")
            session = create_session(
                root=root,
                actor="tester",
                policy=policy,
                task_refs=(TASK_REF,),
                max_tasks=1,
                order_by="selected",
            )
            self.assertTrue(session.ok, session.errors)
            session_id = str(session.data["session_id"])

            _run_git(root, "init")
            _commit_paths(root, "AI_PROJECT", message="baseline pipeline state")

            adapter_calls = []

            def fake_codex_adapter(**kwargs):
                adapter_calls.append(kwargs)
                changed = root / CHANGED_FILE
                changed.parent.mkdir(parents=True, exist_ok=True)
                changed.write_text(
                    "fake Codex wrote the allowed file\n",
                    encoding="utf-8",
                )
                submission = submit_task_report(
                    root=root,
                    tasks_state=_read_tasks_state(root),
                    task=_task(root),
                    report_payload=_report_payload(kwargs["token_gate"].to_dict()),
                    source_file="captured:fake-codex-report",
                    actor="fake_codex",
                    command="fake.codex.report.submit",
                )
                token_gate = kwargs["token_gate"]
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

            def no_external_workflow(argv):
                raise AssertionError("unexpected external workflow: {}".format(argv))

            results = [
                run_next(
                    session_id,
                    root=root,
                    actor="tester",
                    runner=no_external_workflow,
                    codex_adapter=fake_codex_adapter,
                )
                for _ in range(4)
            ]

            for result, expected_phase in zip(
                results,
                ("queue_preview", "prepare", "execute", "collect_report"),
            ):
                self.assertTrue(result.ok, result.errors)
                self.assertEqual(result.data["dispatched_phase"], expected_phase)
                self.assertEqual(result.data["phase_status"], "passed")

            self.assertEqual(len(adapter_calls), 1)
            self.assertEqual(adapter_calls[0]["task_id"], TASK_ID)

            _commit_paths(
                root,
                "AI_PROJECT",
                message="baseline governed pipeline evidence",
            )

            verify = run_next(
                session_id,
                root=root,
                actor="tester",
                runner=no_external_workflow,
                codex_adapter=fake_codex_adapter,
            )
            self.assertTrue(verify.ok, verify.errors)
            self.assertEqual(verify.data["dispatched_phase"], "verify")
            self.assertEqual(verify.data["phase_status"], "passed")

            pipeline = json.loads(
                pipeline_state_path(root).read_text(encoding="utf-8")
            )
            history = pipeline["sessions"][0]["phase_history"]
            self.assertEqual(
                [(phase["phase"], phase["status"]) for phase in history],
                [
                    ("queue_preview", "passed"),
                    ("prepare", "passed"),
                    ("execute", "passed"),
                    ("collect_report", "passed"),
                    ("verify", "passed"),
                ],
            )

            report = _latest_report(root)
            self.assertEqual(report["changed_files"], [CHANGED_FILE])
            verify_artifacts = history[-1]["artifacts"]
            self.assertEqual(
                verify_artifacts["git_diff_gate"]["changed_files"],
                [CHANGED_FILE],
            )
            comparison = verify_artifacts["report_git_diff_comparison"]
            self.assertEqual(comparison["status"], "pass")
            self.assertEqual(comparison["reported_files"], [CHANGED_FILE])
            self.assertEqual(comparison["actual_changed_files"], [CHANGED_FILE])
            self.assertEqual(comparison["missing_from_report"], [])
            self.assertEqual(comparison["extra_in_report"], [])


def _write_project_state(root: Path) -> None:
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
                        "key": "PIPE",
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
                "tasks": [_task_payload()],
            }
        ),
        encoding="utf-8",
    )
    (state_dir / "docs.json").write_text(
        json.dumps({"schema_version": 1, "revision": 1, "documents": []}),
        encoding="utf-8",
    )
    (state_dir / "evolution.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "changes": [
                    {
                        "id": "CHG-001",
                        "status": "approved",
                        "linked_tasks": [TASK_ID],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def _write_fresh_prepare_artifacts(root: Path) -> None:
    generated_dir = root / "AI_PROJECT" / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)
    context = generated_dir / "CONTEXT_PACK.md"
    context.write_text(
        "<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->\n"
        "Context for TASK-001.\n",
        encoding="utf-8",
    )
    prompt = generated_dir / "CODEX_PROMPT.md"
    prompt.write_text(
        "# Codex Prompt Package\n\nTask: TASK-001\n\nSource ID: TASK-001\n",
        encoding="utf-8",
    )
    current_execution = {
        "status": "ready",
        "code": "CODEX_READY",
        "prompt_exists": True,
        "prompt_path": "AI_PROJECT/generated/CODEX_PROMPT.md",
        "source_type": "task",
        "source_id": TASK_ID,
        "context_pack": {
            "path": "AI_PROJECT/generated/CONTEXT_PACK.md",
            "relative_path": "AI_PROJECT/generated/CONTEXT_PACK.md",
            "sha256": hashlib.sha256(context.read_bytes()).hexdigest(),
            "mode": "task",
            "task_id": TASK_ID,
            "docs_revision": 1,
            "tasks_revision": 1,
        },
    }
    (root / "AI_PROJECT" / "state" / "current_execution.json").write_text(
        json.dumps(current_execution),
        encoding="utf-8",
    )


def _task_payload() -> dict:
    return {
        "id": TASK_ID,
        "ref": TASK_REF,
        "uid": "uid_task_001",
        "legacy_id": TASK_ID,
        "aliases": [TASK_ID],
        "title": "Fake Codex happy path",
        "summary": "Exercise pipeline phases with fake Codex.",
        "description": "Prove fake Codex execution can reach verify.",
        "scope": ["Write the allowed test file and submit a report."],
        "out_of_scope": ["Do not run external Codex."],
        "acceptance_criteria": ["Pipeline reaches verify passed."],
        "review_instructions": ["Check report and git diff alignment."],
        "status": "ready",
        "epic_id": "EPIC-001",
        "priority": 1,
        "order": 1,
        "local_seq": 1,
        "depends_on": [],
        "allowed_files": [CHANGED_FILE],
    }


def _report_payload(token_gate: dict) -> dict:
    return {
        "schema_version": 1,
        "task_id": TASK_ID,
        "task_ref": TASK_REF,
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


def _read_tasks_state(root: Path) -> dict:
    return json.loads(
        (root / "AI_PROJECT" / "state" / "tasks.json").read_text(encoding="utf-8")
    )


def _task(root: Path) -> dict:
    return _read_tasks_state(root)["tasks"][0]


def _latest_report(root: Path) -> dict:
    state = json.loads(
        (root / "AI_PROJECT" / "state" / "task_reports.json").read_text(
            encoding="utf-8"
        )
    )
    report_id = state["latest_by_task"][TASK_ID]
    for record in state["reports"]:
        if record["id"] == report_id:
            return record["report"]
    raise AssertionError("missing report: {}".format(report_id))


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


def _run_git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )


if __name__ == "__main__":
    unittest.main()

import json
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline.phase import PhaseResult
from ai_project_ctl.pipeline.session import (
    PipelineSessionError,
    complete_session,
    create_session,
    record_phase_result,
)
from ai_project_ctl.pipeline.state import (
    default_pipeline_state,
    pipeline_events_path,
    pipeline_state_path,
    validate_pipeline_state,
)


def write_reference_state(root: Path) -> None:
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True)
    (state_dir / "tasks.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "current_task_id": None,
                "tasks": [
                    {
                        "id": "TASK-001",
                        "ref": "PIPE-001",
                        "uid": "uid_task_001",
                        "legacy_id": "TASK-001",
                        "aliases": ["TASK-001"],
                        "status": "ready",
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
    (state_dir / "task_reports.json").write_text(
        json.dumps({"schema_version": 1, "revision": 1, "reports": []}),
        encoding="utf-8",
    )


def load_pipeline(root: Path) -> dict:
    return json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))


def load_events(root: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in pipeline_events_path(root).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class PipelineSessionPhaseTests(unittest.TestCase):
    def test_create_session_initializes_phase_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_reference_state(root)

            result = create_session(root=root, actor="tester", current_task_id="TASK-001")

            self.assertTrue(result.ok)
            session = load_pipeline(root)["sessions"][0]
            self.assertEqual(session["current_phase"], "")
            self.assertEqual(session["current_phase_status"], "")
            self.assertEqual(session["blocked_by"], "")
            self.assertEqual(session["next_action"], "")
            self.assertEqual(session["phase_history"], [])

    def test_legacy_session_without_phase_fields_remains_valid(self):
        state = default_pipeline_state(now="2026-06-23T00:00:00Z")
        state["sessions"].append(
            {
                "id": "PSESS-001",
                "status": "planned",
                "selected_queue": {
                    "selection": "manual",
                    "task_refs": [],
                    "epic_ids": [],
                    "statuses": [],
                    "max_tasks": 1,
                    "order_by": "execution",
                },
                "policy_snapshot": policy_snapshot(),
                "current_task_id": "",
                "current_task_ref": "",
                "current_step": "",
                "current_step_status": "planned",
                "attempt_counters": {"steps": 0, "tasks": 0, "rework": 0},
                "gate_outcomes": [],
                "steps": [],
                "linked_change_ids": [],
                "report_ids": [],
                "review_ids": [],
                "commit_ids": [],
                "audit_event_ids": ["EVT-001"],
                "stop_reason": "",
                "created_at": "2026-06-23T00:00:00Z",
                "updated_at": "2026-06-23T00:00:00Z",
                "started_at": "",
                "finished_at": "",
            }
        )

        result = validate_pipeline_state(state)

        self.assertTrue(result.ok, [error.to_dict() for error in result.errors])

    def test_record_phase_result_appends_history_and_updates_current_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_reference_state(root)
            session_id = create_session(
                root=root,
                actor="tester",
                current_task_id="TASK-001",
            ).data["session_id"]

            first = record_phase_result(
                session_id,
                PhaseResult.passed(
                    "prepare",
                    reason="Prompt ready",
                    next_action="Run execute.",
                    changed_files=("AI_PROJECT/generated/CODEX_PROMPT.md",),
                ),
                root=root,
                actor="tester",
                command="pipeline.phase.prepare",
            )
            second = record_phase_result(
                session_id,
                {
                    "phase": "execute",
                    "status": "blocked",
                    "reason": "Owner input required",
                    "next_action": "Provide execution report.",
                    "artifacts": {"blocked_by": "human_owner"},
                },
                root=root,
                actor="tester",
                command="pipeline.phase.execute",
            )

            self.assertTrue(first.ok)
            self.assertTrue(second.ok)
            session = load_pipeline(root)["sessions"][0]
            history = session["phase_history"]

            self.assertEqual(len(history), 2)
            self.assertEqual(history[0]["phase"], "prepare")
            self.assertEqual(history[0]["status"], "passed")
            self.assertEqual(history[0]["events"], first.events)
            self.assertEqual(history[1]["phase"], "execute")
            self.assertEqual(history[1]["status"], "blocked")
            self.assertEqual(history[1]["events"], second.events)
            self.assertEqual(session["current_phase"], "execute")
            self.assertEqual(session["current_phase_status"], "blocked")
            self.assertEqual(session["blocked_by"], "human_owner")
            self.assertEqual(session["next_action"], "Provide execution report.")
            self.assertEqual(session["status"], "blocked")

            commands = [event["command"] for event in load_events(root)]
            self.assertEqual(
                commands,
                [
                    "pipeline.session.create",
                    "pipeline.phase.prepare",
                    "pipeline.phase.execute",
                ],
            )

    def test_terminal_session_rejects_phase_result_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_reference_state(root)
            session_id = create_session(root=root, actor="tester").data["session_id"]
            complete_session(session_id, root=root, actor="tester")

            with self.assertRaises(PipelineSessionError) as raised:
                record_phase_result(
                    session_id,
                    PhaseResult.passed("prepare"),
                    root=root,
                    actor="tester",
                    command="pipeline.phase.prepare",
                )

            self.assertEqual(raised.exception.code, "PIPELINE_SESSION_NOT_ACTIVE")


def policy_snapshot() -> dict:
    return {
        "name": "dry_run",
        "queue": {
            "selection": "manual",
            "max_tasks": 1,
            "include_blocked_tasks": False,
        },
        "evolution": {
            "create_missing_change": False,
            "approve_linked_change": False,
            "accept_linked_change": False,
            "require_approved_change_for_execution": True,
        },
        "token_budget": {
            "require_gate_pass": False,
            "max_prompt_tokens": 32000,
            "max_context_tokens": 24000,
            "min_remaining_tokens": 6000,
        },
        "codex": {
            "mode": "disabled",
            "require_human_selected_policy": True,
        },
        "review": {
            "require_machine_review": False,
            "required_machine_outcome": "none",
            "require_codex_review": False,
            "required_codex_decision": "none",
        },
        "rework": {
            "allow_rework_loop": False,
            "max_rework_attempts": 0,
            "require_owner_decision_for_rework": True,
        },
        "closure": {"auto_close_task": False},
        "commit": {
            "create_local_commit": False,
            "mode": "disabled",
            "require_commit_readiness": False,
            "allow_push": False,
            "allow_merge": False,
        },
    }


if __name__ == "__main__":
    unittest.main()

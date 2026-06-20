import json
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline.session import (
    check_generated,
    complete_session,
    create_session,
    record_step_result,
    render_status,
    start_step,
    stop_session,
    validate_sessions,
)
from ai_project_ctl.pipeline.audit import (
    MAX_AUDIT_STRING_LENGTH,
    build_pipeline_audit_payload,
    pipeline_audit_path,
    read_pipeline_audit_events,
    validate_pipeline_audit_events,
)
from ai_project_ctl.pipeline.state import (
    default_pipeline_state,
    pipeline_events_path,
    pipeline_state_path,
    pipeline_status_path,
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
                        "ref": "APP-01",
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
        json.dumps({"schema_version": 1, "revision": 1, "changes": [{"id": "CHG-001"}]}),
        encoding="utf-8",
    )
    (state_dir / "task_reports.json").write_text(
        json.dumps({"schema_version": 1, "revision": 1, "reports": [{"id": "REPORT-001"}]}),
        encoding="utf-8",
    )


def load_events(root: Path):
    return [
        json.loads(line)
        for line in pipeline_events_path(root).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class PipelineSessionTests(unittest.TestCase):
    def test_create_session_writes_state_event_and_generated_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_reference_state(root)

            result = create_session(
                root=root,
                actor="tester",
                policy_name="supervised",
                task_refs=("APP-01",),
                current_task_id="TASK-001",
                linked_change_ids=("CHG-001",),
                report_ids=("REPORT-001",),
            )

            self.assertTrue(result.ok)
            self.assertEqual(result.data["session_id"], "PSESS-001")
            self.assertTrue(pipeline_state_path(root).exists())
            self.assertTrue(pipeline_status_path(root).exists())
            self.assertTrue(pipeline_audit_path(root).exists())

            state = json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))
            session = state["sessions"][0]
            events = load_events(root)

            self.assertEqual(state["current_session_id"], "PSESS-001")
            self.assertEqual(session["policy_snapshot"]["name"], "supervised")
            self.assertEqual(session["selected_queue"]["task_refs"], ["APP-01"])
            self.assertEqual(session["current_task_id"], "TASK-001")
            self.assertEqual(session["linked_change_ids"], ["CHG-001"])
            self.assertEqual(session["report_ids"], ["REPORT-001"])
            self.assertEqual(events[0]["command"], "pipeline.session.create")
            self.assertEqual(events[0]["payload"]["event_type"], "session.create")
            self.assertIn("policy.selected", events[0]["payload"]["event_types"])
            self.assertIn("queue.planned", events[0]["payload"]["event_types"])
            self.assertIn("task.selected", events[0]["payload"]["event_types"])
            self.assertEqual(events[0]["payload"]["refs"]["session_id"], "PSESS-001")
            self.assertEqual(events[0]["payload"]["refs"]["task_id"], "TASK-001")
            self.assertEqual(events[0]["payload"]["refs"]["change_ids"], ["CHG-001"])
            self.assertEqual(events[0]["payload"]["refs"]["report_ids"], ["REPORT-001"])
            self.assertIn(events[0]["event_id"], session["audit_event_ids"])
            self.assertTrue(check_generated(root=root).ok)

    def test_step_start_result_stop_and_completion_are_audited(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_reference_state(root)

            first = create_session(root=root, actor="tester", current_task_id="TASK-001")
            stop_session(
                first.data["session_id"],
                "operator stopped after preview",
                root=root,
                actor="tester",
            )

            second = create_session(root=root, actor="tester", current_task_id="TASK-001")
            session_id = second.data["session_id"]
            start_step(session_id, "build_prompt", root=root, actor="tester", task_id="TASK-001")
            record_step_result(
                session_id,
                "build_prompt",
                "passed",
                root=root,
                actor="tester",
                task_id="TASK-001",
                gate_name="prompt_ready",
                gate_status="pass",
                gate_details={"status": "ready"},
            )
            complete_session(session_id, root=root, actor="tester")

            state = json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))
            completed = state["sessions"][1]
            commands = [event["command"] for event in load_events(root)]

            self.assertEqual(state["sessions"][0]["status"], "stopped")
            self.assertEqual(completed["status"], "completed")
            self.assertEqual(completed["steps"][0]["status"], "passed")
            self.assertEqual(completed["gate_outcomes"][0]["name"], "prompt_ready")
            self.assertEqual(events := load_events(root), read_pipeline_audit_events(root))
            self.assertEqual(events[4]["payload"]["refs"]["gate"], "prompt_ready")
            self.assertIn("step.result", events[4]["payload"]["event_types"])
            self.assertEqual(events[5]["payload"]["event_type"], "completion")
            self.assertEqual(
                commands,
                [
                    "pipeline.session.create",
                    "pipeline.session.stop",
                    "pipeline.session.create",
                    "pipeline.step.start",
                    "pipeline.step.result",
                    "pipeline.session.complete",
                ],
            )

    def test_validation_catches_dangling_task_change_and_report_refs(self):
        state = default_pipeline_state(now="2026-06-19T00:00:00Z")
        state["sessions"].append(
            {
                "id": "PSESS-001",
                "status": "planned",
                "selected_queue": {
                    "selection": "manual",
                    "task_refs": ["MISSING-01"],
                    "epic_ids": [],
                    "statuses": [],
                    "max_tasks": 1,
                    "order_by": "execution",
                },
                "policy_snapshot": create_session_policy_snapshot(),
                "current_task_id": "TASK-MISSING",
                "current_task_ref": "",
                "current_step": "",
                "current_step_status": "planned",
                "attempt_counters": {"steps": 0, "tasks": 0, "rework": 0},
                "gate_outcomes": [],
                "steps": [],
                "linked_change_ids": ["CHG-MISSING"],
                "report_ids": ["REPORT-MISSING"],
                "review_ids": [],
                "commit_ids": [],
                "audit_event_ids": ["EVT-1"],
                "stop_reason": "",
                "created_at": "2026-06-19T00:00:00Z",
                "updated_at": "2026-06-19T00:00:00Z",
                "started_at": "",
                "finished_at": "",
            }
        )

        result = validate_pipeline_state(
            state,
            tasks_state={"tasks": [{"id": "TASK-001", "ref": "APP-01"}]},
            evolution_state={"changes": [{"id": "CHG-001"}]},
            task_reports_state={"reports": [{"id": "REPORT-001"}]},
        )
        codes = [issue.code for issue in result.errors]

        self.assertIn("PIPELINE_DANGLING_TASK_REFERENCE", codes)
        self.assertIn("PIPELINE_DANGLING_CHANGE_REFERENCE", codes)
        self.assertIn("PIPELINE_DANGLING_REPORT_REFERENCE", codes)

    def test_render_and_check_generated_detect_status_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_reference_state(root)
            create_session(root=root, actor="tester", current_task_id="TASK-001")

            render_status(root=root)
            self.assertTrue(check_generated(root=root).ok)

            pipeline_status_path(root).write_text("manual drift\n", encoding="utf-8")

            result = check_generated(root=root)
            self.assertFalse(result.ok)
            self.assertEqual(result.errors[0].code, "PIPELINE_STATUS_OUTDATED")
            self.assertTrue(validate_sessions(root=root).ok)

            render_status(root=root)
            self.assertTrue(check_generated(root=root).ok)
            pipeline_audit_path(root).write_text("manual drift\n", encoding="utf-8")

            audit_result = check_generated(root=root)
            self.assertFalse(audit_result.ok)
            self.assertEqual(audit_result.errors[0].code, "PIPELINE_AUDIT_OUTDATED")

    def test_audit_payload_sanitizes_forbidden_fields_and_oversized_strings(self):
        oversized = "x" * (MAX_AUDIT_STRING_LENGTH + 1)
        payload = build_pipeline_audit_payload(
            "pipeline.step.result",
            {
                "session_id": "PSESS-001",
                "step": {
                    "task_id": "TASK-001",
                    "gate_outcomes": [
                        {
                            "name": "codex_execution_adapter",
                            "status": "pass",
                            "details": {
                                "prompt_text": "do not store",
                                "summary": oversized,
                            },
                        }
                    ],
                },
                "report_ids": ["REPORT-001"],
            },
        )

        raw = json.dumps(payload, sort_keys=True)
        self.assertNotIn("do not store", raw)
        self.assertNotIn("prompt_text", raw)
        self.assertNotIn(oversized, raw)
        self.assertEqual(payload["event_type"], "codex_run.result")
        self.assertEqual(payload["refs"]["task_id"], "TASK-001")
        self.assertEqual(payload["refs"]["report_ids"], ["REPORT-001"])

    def test_audit_validation_rejects_raw_secret_payloads(self):
        result = validate_pipeline_audit_events(
            [
                {
                    "event_id": "EVT-001",
                    "timestamp": "2026-06-20T00:00:00Z",
                    "actor": "tester",
                    "command": "pipeline.step.result",
                    "entity_type": "pipeline_session",
                    "entity_id": "PSESS-001",
                    "payload": {
                        "event_type": "codex_run.result",
                        "secret": "raw secret",
                    },
                }
            ]
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.errors[0].code, "PIPELINE_FORBIDDEN_AUDIT_PAYLOAD_FIELD")


def create_session_policy_snapshot():
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

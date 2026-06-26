import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline import policy_preset
from ai_project_ctl.pipeline.queue_phase import preview_queue_phase


TIMESTAMP = "2026-06-25T00:00:00Z"


def write_queue_state(root: Path) -> None:
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
                "tasks": [
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "uid": "uid_task_001",
                        "legacy_id": "TASK-001",
                        "aliases": ["TASK-001"],
                        "title": "Queue phase boundary task",
                        "status": "ready",
                        "epic_id": "EPIC-001",
                        "priority": 1,
                        "order": 1,
                        "local_seq": 1,
                        "depends_on": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def write_pipeline_session(root: Path) -> None:
    state_dir = root / "AI_PROJECT" / "state"
    (state_dir / "pipeline_sessions.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "created_at": TIMESTAMP,
                "updated_at": TIMESTAMP,
                "current_session_id": "PSESS-001",
                "sessions": [
                    {
                        "id": "PSESS-001",
                        "status": "planned",
                        "created_at": TIMESTAMP,
                        "updated_at": TIMESTAMP,
                        "started_at": "",
                        "finished_at": "",
                        "selected_queue": {
                            "selection": "ready_queue",
                            "task_refs": ["APP-01"],
                            "epic_ids": [],
                            "statuses": [],
                            "max_tasks": 1,
                            "order_by": "selected",
                            "include_blocked_tasks": False,
                        },
                        "policy_snapshot": policy_preset("supervised").to_dict(),
                        "current_task_id": "",
                        "current_task_ref": "",
                        "current_step": "",
                        "current_step_status": "planned",
                        "stop_reason": "",
                        "attempt_counters": {
                            "steps": 0,
                            "tasks": 0,
                            "rework": 0,
                        },
                        "steps": [],
                        "gate_outcomes": [],
                        "linked_change_ids": [],
                        "report_ids": [],
                        "review_ids": [],
                        "commit_ids": [],
                        "audit_event_ids": [],
                        "current_phase": "",
                        "current_phase_status": "",
                        "blocked_by": "",
                        "next_action": "",
                        "phase_history": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def snapshot_project_files(root: Path) -> dict[str, str]:
    project = root / "AI_PROJECT"
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(project.rglob("*"))
        if path.is_file()
    }


class PipelineQueuePhaseBoundaryTests(unittest.TestCase):
    def test_explicit_preview_does_not_create_state_events_or_generated_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_queue_state(root)
            before = snapshot_project_files(root)

            result = preview_queue_phase(
                root=root,
                task_refs=("APP-01",),
                max_tasks=1,
                order_by="selected",
            )

            phase = result.data["phase_result"]
            after = snapshot_project_files(root)

            self.assertTrue(result.ok)
            self.assertEqual(phase["status"], "passed")
            self.assertEqual(phase["artifacts"]["next_task"]["id"], "TASK-001")
            self.assertEqual(result.changed_files, [])
            self.assertEqual(result.generated_files, [])
            self.assertEqual(result.events, [])
            self.assertEqual(phase["changed_files"], [])
            self.assertEqual(phase["generated_files"], [])
            self.assertEqual(phase["events"], [])
            self.assertEqual(after, before)
            self.assertFalse((root / "AI_PROJECT" / "events").exists())
            self.assertFalse((root / "AI_PROJECT" / "generated").exists())
            self.assertFalse(
                (root / "AI_PROJECT" / "state" / "pipeline_sessions.json").exists()
            )

    def test_session_preview_does_not_rewrite_existing_state_or_generated_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_queue_state(root)
            write_pipeline_session(root)
            generated = root / "AI_PROJECT" / "generated"
            generated.mkdir(parents=True)
            (generated / "PIPELINE_STATUS.md").write_text(
                "sentinel generated status\n",
                encoding="utf-8",
            )
            before = snapshot_project_files(root)

            result = preview_queue_phase("PSESS-001", root=root)

            phase = result.data["phase_result"]
            after = snapshot_project_files(root)

            self.assertTrue(result.ok)
            self.assertEqual(result.data["queue_source"], "session")
            self.assertEqual(phase["status"], "passed")
            self.assertEqual(phase["artifacts"]["session_id"], "PSESS-001")
            self.assertEqual(phase["artifacts"]["next_task"]["id"], "TASK-001")
            self.assertEqual(result.changed_files, [])
            self.assertEqual(result.generated_files, [])
            self.assertEqual(result.events, [])
            self.assertEqual(after, before)
            self.assertFalse((root / "AI_PROJECT" / "events").exists())


if __name__ == "__main__":
    unittest.main()

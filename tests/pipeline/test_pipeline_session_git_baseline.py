import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline import policy_preset
from ai_project_ctl.pipeline.phase import PhaseResult
from ai_project_ctl.pipeline.runner import run_next
from ai_project_ctl.pipeline.session import (
    create_session,
    record_phase_result,
    status_payload,
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
                "current_task_id": None,
                "tasks": [
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "uid": "uid_task_001",
                        "legacy_id": "TASK-001",
                        "aliases": ["TASK-001"],
                        "title": "Runnable task",
                        "status": "ready",
                        "epic_id": "EPIC-001",
                        "priority": 1,
                        "order": 1,
                        "local_seq": 1,
                        "depends_on": [],
                        "allowed_files": ["owned.txt"],
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


def write_pipeline(root: Path, state: dict) -> None:
    pipeline_state_path(root).write_text(json.dumps(state, indent=2), encoding="utf-8")


def load_events(root: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in pipeline_events_path(root).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def run_git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def init_git(root: Path) -> None:
    run_git(root, "init")


def commit_all(root: Path, message: str) -> None:
    run_git(root, "add", ".")
    run_git(
        root,
        "-c",
        "user.name=Pipeline Test",
        "-c",
        "user.email=pipeline-test@example.com",
        "commit",
        "-m",
        message,
    )


class PipelineSessionGitBaselineTests(unittest.TestCase):
    def test_session_records_baseline_and_post_phase_session_owned_delta(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_reference_state(root)
            init_git(root)
            commit_all(root, "baseline project state")
            (root / "preexisting.txt").write_text("dirty before session\n", encoding="utf-8")

            created = create_session(
                root=root,
                actor="tester",
                task_refs=("APP-01",),
                current_task_id="TASK-001",
            )
            self.assertTrue(created.ok)
            session_id = created.data["session_id"]
            session = load_pipeline(root)["sessions"][0]
            baseline = session["file_evidence"]["git_status_baseline"]

            self.assertTrue(baseline["ok"])
            self.assertEqual(baseline["dirty_paths"], ["preexisting.txt"])

            (root / "owned.txt").write_text("created during session\n", encoding="utf-8")
            recorded = record_phase_result(
                session_id,
                PhaseResult.passed(
                    "prepare",
                    reason="Prompt package prepared.",
                    changed_files=("owned.txt",),
                ),
                root=root,
                actor="tester",
                task_id="TASK-001",
                command="pipeline.phase.prepare",
            )
            self.assertTrue(recorded.ok)

            session = load_pipeline(root)["sessions"][0]
            evidence = session["file_evidence"]
            owned = evidence["session_owned_changed_files"]
            delta = session["phase_history"][-1]["artifacts"]["file_delta"]
            payload_session = status_payload(root=root)["current_session"]

            self.assertIn("owned.txt", owned)
            self.assertNotIn("preexisting.txt", owned)
            self.assertEqual(evidence["pre_existing_dirty_files"], ["preexisting.txt"])
            self.assertIn("owned.txt", delta["session_owned_changed_files"])
            self.assertEqual(delta["pre_existing_dirty_files"], ["preexisting.txt"])
            self.assertIn("owned.txt", payload_session["session_owned_changed_files"])
            self.assertEqual(payload_session["pre_existing_dirty_files"], ["preexisting.txt"])
            self.assertEqual(payload_session["file_evidence"]["phase_delta_count"], 1)

    def test_legacy_session_without_baseline_remains_valid_and_status_readable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = default_pipeline_state(now="2026-06-28T00:00:00Z")
            state["current_session_id"] = "PSESS-001"
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
                    "policy_snapshot": policy_preset("dry_run").to_dict(),
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
                    "created_at": "2026-06-28T00:00:00Z",
                    "updated_at": "2026-06-28T00:00:00Z",
                    "started_at": "",
                    "finished_at": "",
                }
            )
            pipeline_state_path(root).parent.mkdir(parents=True)
            write_pipeline(root, state)

            validation = validate_pipeline_state(state)
            payload = status_payload(root=root)

            self.assertTrue(validation.ok, [error.to_dict() for error in validation.errors])
            self.assertEqual(payload["current_session"]["id"], "PSESS-001")
            self.assertNotIn("file_evidence", payload["current_session"])

    def test_run_next_backfills_missing_baseline_before_phase_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_reference_state(root)
            init_git(root)
            commit_all(root, "baseline project state")
            created = create_session(
                root=root,
                actor="tester",
                task_refs=("APP-01",),
                current_task_id="TASK-001",
            )
            self.assertTrue(created.ok)
            session_id = created.data["session_id"]
            state = load_pipeline(root)
            state["sessions"][0].pop("file_evidence")
            write_pipeline(root, state)
            commit_all(root, "legacy session without baseline")
            (root / "preexisting.txt").write_text("dirty before run\n", encoding="utf-8")

            result = run_next(session_id, root=root, actor="tester")

            self.assertTrue(result.ok)
            state = load_pipeline(root)
            evidence = state["sessions"][0]["file_evidence"]
            commands = [event["command"] for event in load_events(root)]

            self.assertEqual(
                evidence["git_status_baseline"]["dirty_paths"],
                ["preexisting.txt"],
            )
            self.assertLess(
                commands.index("pipeline.session.git_baseline"),
                commands.index("pipeline.phase.queue_preview"),
            )
            self.assertNotIn(
                "preexisting.txt",
                evidence["session_owned_changed_files"],
            )


if __name__ == "__main__":
    unittest.main()

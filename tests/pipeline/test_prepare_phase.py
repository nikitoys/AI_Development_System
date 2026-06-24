import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline.prepare_phase import prepare_phase
from ai_project_ctl.pipeline.session import create_session
from ai_project_ctl.pipeline.state import pipeline_state_path


def write_prepare_project_state(root: Path, *, allowed_files: list[str]) -> None:
    state_dir = root / "AI_PROJECT" / "state"
    generated_dir = root / "AI_PROJECT" / "generated"
    state_dir.mkdir(parents=True)
    generated_dir.mkdir(parents=True)

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
                        "title": "Prepare phase task",
                        "status": "ready",
                        "epic_id": "EPIC-001",
                        "priority": 1,
                        "order": 1,
                        "local_seq": 1,
                        "depends_on": [],
                        "allowed_files": allowed_files,
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
    (state_dir / "docs.json").write_text(
        json.dumps({"schema_version": 1, "revision": 1, "documents": []}),
        encoding="utf-8",
    )

    prompt = generated_dir / "CODEX_PROMPT.md"
    prompt.write_text("Task: TASK-001\n\nPrepared prompt.", encoding="utf-8")
    context = generated_dir / "CONTEXT_PACK.md"
    context.write_text("Context for TASK-001.", encoding="utf-8")
    context_hash = hashlib.sha256(context.read_bytes()).hexdigest()
    (state_dir / "current_execution.json").write_text(
        json.dumps(
            {
                "status": "ready",
                "code": "CODEX_READY",
                "source_type": "task",
                "source_id": "TASK-001",
                "prompt_path": "AI_PROJECT/generated/CODEX_PROMPT.md",
                "prompt_exists": True,
                "context_pack": {
                    "path": "AI_PROJECT/generated/CONTEXT_PACK.md",
                    "sha256": context_hash,
                    "mode": "task",
                    "task_id": "TASK-001",
                    "tasks_revision": 1,
                    "docs_revision": 1,
                },
            }
        ),
        encoding="utf-8",
    )


def create_ui_prepare_session(
    root: Path,
    *,
    confirmed: bool = True,
    bypass_enabled: bool = False,
) -> str:
    session = create_session(
        root=root,
        actor="tester",
        policy_name="supervised",
        selected_queue={
            "selection": "ready_queue",
            "task_refs": ["APP-01"],
            "epic_ids": [],
            "statuses": [],
            "max_tasks": 1,
            "order_by": "selected",
            "include_blocked_tasks": False,
            "created_by_command": "ui.run",
            "ui_run_confirmed": confirmed,
            "allow_internal_change_gate_bypass": bypass_enabled,
        },
    )
    return str(session.data["session_id"])


class PreparePhaseInternalChangeGateBypassTests(unittest.TestCase):
    def test_disabled_ui_bypass_still_blocks_without_approved_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prepare_project_state(
                root,
                allowed_files=["ai_project_ctl/pipeline/prepare_phase.py"],
            )
            session_id = create_ui_prepare_session(root, bypass_enabled=False)

            result = prepare_phase(session_id, root=root, actor="tester")

            phase = result.data["phase_result"]
            change_gate = phase["artifacts"]["change_gate"]
            self.assertTrue(result.ok)
            self.assertEqual(phase["status"], "blocked")
            self.assertEqual(change_gate["tasks_requiring_approval"], ["TASK-001"])
            self.assertNotIn("bypassed", change_gate)

    def test_enabled_ui_bypass_passes_for_internal_project_control_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prepare_project_state(
                root,
                allowed_files=[
                    "ai_project_ctl/pipeline/prepare_phase.py",
                    "scripts/aictl.py",
                    "tests/pipeline/test_prepare_phase.py",
                ],
            )
            session_id = create_ui_prepare_session(root, bypass_enabled=True)

            result = prepare_phase(session_id, root=root, actor="tester")

            phase = result.data["phase_result"]
            change_gate = phase["artifacts"]["change_gate"]
            state = json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))
            recorded_gate = state["sessions"][0]["phase_history"][0]["artifacts"][
                "change_gate"
            ]

            self.assertTrue(result.ok)
            self.assertEqual(phase["status"], "passed")
            self.assertTrue(change_gate["bypassed"])
            self.assertEqual(
                change_gate["bypass"]["reason"],
                "confirmed_ui_internal_project_control_task",
            )
            self.assertTrue(recorded_gate["bypassed"])
            self.assertEqual(
                recorded_gate["bypass"]["setting"],
                "allow_internal_change_gate_bypass",
            )

    def test_enabled_ui_bypass_blocks_for_non_internal_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prepare_project_state(root, allowed_files=["src/product.py"])
            session_id = create_ui_prepare_session(root, bypass_enabled=True)

            result = prepare_phase(session_id, root=root, actor="tester")

            phase = result.data["phase_result"]
            change_gate = phase["artifacts"]["change_gate"]
            self.assertTrue(result.ok)
            self.assertEqual(phase["status"], "blocked")
            self.assertEqual(change_gate["tasks_requiring_approval"], ["TASK-001"])
            self.assertNotIn("bypassed", change_gate)

    def test_plain_pipeline_session_does_not_use_ui_bypass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_prepare_project_state(
                root,
                allowed_files=["ai_project_ctl/pipeline/prepare_phase.py"],
            )
            settings_path = root / "AI_PROJECT" / "config" / "ui_settings.json"
            settings_path.parent.mkdir(parents=True)
            settings_path.write_text(
                json.dumps(
                    {
                        "default_policy": "supervised_executable_local_commit",
                        "command_line": "codex exec",
                        "allow_internal_change_gate_bypass": True,
                    }
                ),
                encoding="utf-8",
            )
            session = create_session(
                root=root,
                actor="tester",
                policy_name="supervised",
                task_refs=("APP-01",),
                max_tasks=1,
                order_by="selected",
            )

            result = prepare_phase(
                str(session.data["session_id"]),
                root=root,
                actor="tester",
            )

            phase = result.data["phase_result"]
            change_gate = phase["artifacts"]["change_gate"]
            self.assertTrue(result.ok)
            self.assertEqual(phase["status"], "blocked")
            self.assertEqual(change_gate["tasks_requiring_approval"], ["TASK-001"])
            self.assertNotIn("bypassed", change_gate)


if __name__ == "__main__":
    unittest.main()

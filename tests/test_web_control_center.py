import json
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from ai_project_ctl.core.registry import command_describe
from ai_project_ctl.web.actions import WebActionError, WebActionExecutor
from ai_project_ctl.web.read_model import (
    ReadOnlyProjectModel,
    WebControlError,
    require_read_only_command,
)
from ai_project_ctl.web.server import (
    WEB_IMPORT_FILE_MAX_BYTES,
    WebServerError,
    make_handler,
    render_action_error,
    render_action_result,
    route,
)


class WebControlCenterTests(unittest.TestCase):
    def test_web_registry_command_serves_loopback_control_center(self):
        descriptor = command_describe("web.serve")

        self.assertEqual(descriptor["kind"], "read")
        self.assertFalse(descriptor["read_write"]["mutates_state"])
        self.assertFalse(descriptor["read_write"]["writes_events"])
        self.assertFalse(descriptor["read_write"]["renders_generated"])
        self.assertIn("loopback", " ".join(descriptor["notes"]).lower())

    def test_read_model_rejects_write_registry_command(self):
        with self.assertRaises(WebControlError) as raised:
            require_read_only_command("task.transition")

        self.assertEqual(raised.exception.code, "WEB_COMMAND_NOT_READ_ONLY")

    def test_dashboard_uses_read_only_state_without_subprocesses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-001",
                        "ref": "CTL-01",
                        "status": "ready",
                        "title": "Ready task",
                        "epic_id": "EPIC-001",
                        "order": 1,
                    }
                ],
                current_task_id="TASK-001",
                epics=[{"id": "EPIC-001", "status": "active", "order": 1}],
            )
            model = ReadOnlyProjectModel(root, actor="tester")
            with patch("ai_project_ctl.web.read_model.subprocess.run") as run:
                data = model.dashboard()
                run.assert_not_called()

        self.assertEqual(data["doctor"]["overall_status"], "UNKNOWN")
        self.assertFalse(data["doctor"]["cache"]["cached"])
        self.assertEqual(data["queue"][0]["id"], "TASK-001")

    def test_dashboard_and_data_routes_do_not_refresh_doctor_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root)
            model = ReadOnlyProjectModel(root, actor="tester")
            with patch("ai_project_ctl.web.read_model.subprocess.run") as run:
                dashboard_status, _, _ = route("/", model)
                data_status, _, data_body = route("/data.json", model)
                run.assert_not_called()

        payload = json.loads(data_body)

        self.assertEqual(dashboard_status.value, 200)
        self.assertEqual(data_status.value, 200)
        self.assertEqual(payload["doctor"]["overall_status"], "UNKNOWN")
        self.assertFalse(payload["doctor"]["cache"]["cached"])

    def test_tasks_page_filters_searches_groups_and_shows_readable_refs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root, **large_task_view_state())
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route(
                "/tasks?initiative=INIT-002&epic=EPIC-006&status=in_progress&q=TASK-038&group=status",
                model,
            )

        self.assertEqual(status.value, 200)
        self.assertIn("WFA-07", body)
        self.assertIn("TASK-038", body)
        self.assertIn("UIX-01 Improve Tasks filtering grouping and collapse", body)
        self.assertIn('<details class="task-group task-group-in-progress" open>', body)
        self.assertIn('value="INIT-002" selected', body)
        self.assertIn('value="EPIC-006" selected', body)
        self.assertNotIn("WFA-06 Documentation Audit", body)
        self.assertNotIn("CTL-10 Completed Control Task", body)
        self.assertNotIn("DOC-01 Usage Guide", body)

    def test_tasks_page_groups_epic_005_and_006_and_hides_done_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root, **large_task_view_state())
            model = ReadOnlyProjectModel(root, actor="tester")

            default_status, _, default_body = route("/tasks", model)
            grouped_status, _, grouped_body = route(
                "/tasks?initiative=INIT-002&show_done=1&group=epic",
                model,
            )
            done_status, _, done_body = route("/tasks?status=done&group=status", model)

        self.assertEqual(default_status.value, 200)
        self.assertIn("WFA-07", default_body)
        self.assertIn("WFA-06", default_body)
        self.assertIn("done hidden", default_body)
        self.assertNotIn("CTL-10 Completed Control Task", default_body)

        self.assertEqual(grouped_status.value, 200)
        self.assertIn("CTL (EPIC-005) - Implement unified aictl", grouped_body)
        self.assertIn("WFA (EPIC-006) - Control Plane Workflow Automation", grouped_body)
        self.assertIn("CTL-10 Completed Control Task", grouped_body)

        self.assertEqual(done_status.value, 200)
        self.assertIn("CTL-10 Completed Control Task", done_body)
        self.assertIn('<details class="task-group task-group-done">', done_body)
        self.assertIn("done visible", done_body)

    def test_tasks_page_shows_status_aware_row_workflow_buttons(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root, **large_task_view_state())
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/tasks?show_done=1", model)

        self.assertEqual(status.value, 200)
        self.assertIn("Prepare for Codex", body)
        self.assertIn("Prepare for Codex unavailable: another current task is WFA-07", body)
        self.assertNotIn('value="task.prepare_for_codex"', body)
        self.assertIn("Refresh Context", body)
        self.assertIn('value="task.refresh_execution_context"', body)
        self.assertIn("Submit for Review", body)
        self.assertIn("Submit for Review unavailable: no current Codex prompt state exists", body)
        self.assertNotIn('value="task.submit_for_review"', body)
        self.assertIn("Approve &amp; Done", body)
        self.assertIn('value="task.close_reviewed"', body)
        self.assertIn("Request Changes", body)
        self.assertIn('value="task.request_changes"', body)
        self.assertIn("Build Codex prompt with context", body)
        self.assertIn('name="confirm" value="yes" required', body)

    def test_current_execution_panel_shows_ready_prompt_and_copy_instruction(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prompt_path = root / "AI_PROJECT/generated/CODEX_PROMPT.md"
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-048",
                        "ref": "WFA-17",
                        "legacy_id": "TASK-048",
                        "status": "in_progress",
                        "title": "Current execution panel",
                        "summary": "Show execution status.",
                        "epic_id": "EPIC-006",
                        "epic_key": "WFA",
                    }
                ],
                current_task_id="TASK-048",
                epics=[{"id": "EPIC-006", "key": "WFA", "status": "active"}],
                execution={
                    "status": "READY",
                    "code": "CODEX_READY",
                    "updated_at": "2026-06-19T13:35:28Z",
                    "prompt_exists": True,
                    "prompt_path": str(prompt_path),
                    "source_type": "task",
                    "source_id": "TASK-048",
                    "source_status": "in_progress",
                    "context_pack": {
                        "path": "AI_PROJECT/generated/CONTEXT_PACK.md",
                        "task_id": "TASK-048",
                        "tasks_revision": 1,
                        "docs_revision": 23,
                    },
                },
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            data_status, _, data_body = route("/data.json", model)
            dashboard_status, _, dashboard_body = route("/", model)
            tasks_status, _, tasks_body = route("/tasks?q=WFA-17", model)

        payload = json.loads(data_body)

        self.assertEqual(data_status.value, 200)
        self.assertEqual(dashboard_status.value, 200)
        self.assertEqual(tasks_status.value, 200)
        self.assertEqual(payload["execution_context"]["prompt"]["status"], "ready")
        self.assertEqual(payload["execution_context"]["context_pack"]["status"], "ready")
        self.assertIn("Current Execution", dashboard_body)
        self.assertIn("Codex Prompt", dashboard_body)
        self.assertIn("Context Pack", dashboard_body)
        self.assertIn("Copy Codex Instruction", dashboard_body)
        self.assertIn(
            "Read AI_PROJECT/generated/CODEX_PROMPT.md and execute it.",
            dashboard_body,
        )
        self.assertIn("Refresh Context", dashboard_body)
        self.assertIn("Refresh Prompt", dashboard_body)
        self.assertIn("Clear Current", dashboard_body)
        self.assertIn("Current Execution", tasks_body)

    def test_current_execution_panel_shows_stale_prompt_context_and_selection_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-048",
                        "ref": "WFA-17",
                        "legacy_id": "TASK-048",
                        "status": "in_progress",
                        "title": "Current task",
                        "epic_id": "EPIC-006",
                        "epic_key": "WFA",
                    },
                    {
                        "id": "TASK-049",
                        "ref": "WFA-18",
                        "legacy_id": "TASK-049",
                        "status": "ready",
                        "title": "Selected task",
                        "epic_id": "EPIC-006",
                        "epic_key": "WFA",
                    },
                ],
                current_task_id="TASK-048",
                epics=[{"id": "EPIC-006", "key": "WFA", "status": "active"}],
                execution={
                    "status": "READY",
                    "code": "CODEX_READY",
                    "prompt_exists": True,
                    "prompt_path": "AI_PROJECT/generated/CODEX_PROMPT.md",
                    "source_type": "task",
                    "source_id": "TASK-999",
                    "source_status": "in_progress",
                    "context_pack": {
                        "path": "AI_PROJECT/generated/CONTEXT_PACK.md",
                        "task_id": "TASK-048",
                        "tasks_revision": 0,
                    },
                },
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            data_status, _, data_body = route("/data.json", model)
            tasks_status, _, tasks_body = route("/tasks?q=WFA-18&group=none", model)

        payload = json.loads(data_body)

        self.assertEqual(data_status.value, 200)
        self.assertEqual(tasks_status.value, 200)
        self.assertEqual(payload["execution_context"]["prompt"]["status"], "stale")
        self.assertEqual(payload["execution_context"]["context_pack"]["status"], "stale")
        self.assertIn("Codex prompt targets TASK-999", tasks_body)
        self.assertIn("Context Pack tasks revision is 0 but current is 1", tasks_body)
        self.assertIn(
            "Selected task WFA-18 differs from current task WFA-17.",
            tasks_body,
        )
        self.assertNotIn("Copy Codex Instruction", tasks_body)

    def test_current_execution_panel_shows_missing_prompt_and_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-048",
                        "ref": "WFA-17",
                        "legacy_id": "TASK-048",
                        "status": "in_progress",
                        "title": "Missing execution state",
                        "epic_id": "EPIC-006",
                    }
                ],
                current_task_id="TASK-048",
                epics=[{"id": "EPIC-006", "status": "active"}],
            )

            data_status, _, data_body = route(
                "/data.json",
                ReadOnlyProjectModel(root, actor="tester"),
            )
            dashboard_status, _, dashboard_body = route(
                "/",
                ReadOnlyProjectModel(root, actor="tester"),
            )

        payload = json.loads(data_body)

        self.assertEqual(data_status.value, 200)
        self.assertEqual(dashboard_status.value, 200)
        self.assertEqual(payload["execution_context"]["prompt"]["status"], "missing")
        self.assertEqual(payload["execution_context"]["context_pack"]["status"], "missing")
        self.assertIn("No current Codex prompt state exists.", dashboard_body)
        self.assertIn("No Context Pack metadata exists.", dashboard_body)
        self.assertNotIn("Copy Codex Instruction", dashboard_body)

    def test_current_execution_panel_shows_no_current_task_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-001",
                        "ref": "DOC-01",
                        "legacy_id": "TASK-001",
                        "status": "ready",
                        "title": "Ready but not current",
                        "epic_id": "EPIC-001",
                    }
                ],
                epics=[{"id": "EPIC-001", "status": "active"}],
            )

            data_status, _, data_body = route(
                "/data.json",
                ReadOnlyProjectModel(root, actor="tester"),
            )
            dashboard_status, _, dashboard_body = route(
                "/",
                ReadOnlyProjectModel(root, actor="tester"),
            )

        payload = json.loads(data_body)

        self.assertEqual(data_status.value, 200)
        self.assertEqual(dashboard_status.value, 200)
        self.assertEqual(payload["execution_context"]["prompt"]["status"], "unknown")
        self.assertEqual(payload["execution_context"]["context_pack"]["status"], "unknown")
        self.assertIn("No current task selected.", dashboard_body)
        self.assertNotIn('value="current.clear"', dashboard_body)

    def test_dashboard_exposes_latest_task_execution_report(self):
        report_state = {
            "schema_version": 1,
            "revision": 1,
            "created_at": "2026-06-19T12:00:00Z",
            "updated_at": "2026-06-19T12:00:00Z",
            "latest_by_task": {"TASK-001": "RPT-001"},
            "reports": [
                {
                    "id": "RPT-001",
                    "task_id": "TASK-001",
                    "task_ref": "DOC-01",
                    "submitted_at": "2026-06-19T12:00:00Z",
                    "submitted_by": "codex",
                    "source_file": "/tmp/report.json",
                    "report": {
                        "task_id": "TASK-001",
                        "task_ref": "DOC-01",
                        "implementation_summary": "Implemented report flow.",
                        "changed_files": ["scripts/taskctl.py"],
                        "generated_files": [],
                        "checks": [
                            {
                                "name": "unit",
                                "result": "pass",
                                "blocking": True,
                                "duration_sec": 1.2,
                            }
                        ],
                        "warnings": [],
                        "blockers": [],
                        "notes": ["Ready for review."],
                        "owner_decision_required": True,
                    },
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-001",
                        "ref": "DOC-01",
                        "status": "in_review",
                        "title": "Task with report",
                        "epic_id": "EPIC-001",
                        "order": 1,
                    }
                ],
                epics=[{"id": "EPIC-001", "status": "active", "order": 1}],
                task_reports=report_state,
            )
            model = ReadOnlyProjectModel(root, actor="tester")
            data = model.dashboard()

        latest = data["tasks"][0]["latest_report"]
        self.assertEqual(latest["id"], "RPT-001")
        self.assertEqual(latest["implementation_summary"], "Implemented report flow.")
        self.assertEqual(latest["check_counts"]["pass"], 1)
        self.assertTrue(latest["owner_decision_required"])

    def test_reviews_page_shows_task_review_package_with_report(self):
        task = {
            "id": "TASK-047",
            "ref": "WFA-16",
            "legacy_id": "TASK-047",
            "status": "in_review",
            "title": "UIX-10 Add Task Review Package View",
            "summary": "Review task changes in one place.",
            "epic_id": "EPIC-006",
            "epic_key": "WFA",
            "active_stage": "Task Execution",
            "scope": ["Show review metadata.", "Show report details."],
            "acceptance_criteria": ["Owner can understand the decision."],
            "order": 16,
        }
        report_state = review_report_state(
            task_id="TASK-047",
            task_ref="WFA-16",
            summary="Implemented the review package.",
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[task],
                epics=[{"id": "EPIC-006", "status": "active", "order": 1}],
                task_reports=report_state,
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/reviews", model)

        self.assertEqual(status.value, 200)
        self.assertIn("Task Review Packages", body)
        self.assertIn("UIX-10 Add Task Review Package View", body)
        self.assertIn("WFA-16", body)
        self.assertIn("TASK-047", body)
        self.assertIn("Review task changes in one place.", body)
        self.assertIn("Show review metadata.", body)
        self.assertIn("Owner can understand the decision.", body)
        self.assertIn("Implemented the review package.", body)
        self.assertIn("ai_project_ctl/web/server.py", body)
        self.assertIn("AI_PROJECT/generated/CODEX_PROMPT.md", body)
        self.assertIn("unit", body)
        self.assertIn("warn", body)
        self.assertIn("Review warning.", body)
        self.assertIn("Manual blocker.", body)
        self.assertIn("Ready for owner decision.", body)
        self.assertIn("Approve &amp; Done", body)
        self.assertIn('value="task.close_reviewed"', body)
        self.assertIn("Request Changes", body)
        self.assertIn('value="task.request_changes"', body)
        self.assertIn('name="confirm" value="yes" required', body)
        self.assertIn('textarea name="notes" rows="2"', body)

    def test_reviews_page_shows_missing_report_clearly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-047",
                        "ref": "WFA-16",
                        "legacy_id": "TASK-047",
                        "status": "in_review",
                        "title": "Review without report",
                        "summary": "No report yet.",
                        "epic_id": "EPIC-006",
                        "order": 16,
                    }
                ],
                epics=[{"id": "EPIC-006", "status": "active", "order": 1}],
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/reviews", model)

        self.assertEqual(status.value, 200)
        self.assertIn("Review without report", body)
        self.assertIn("No Codex execution report submitted for this task.", body)

    def test_reviews_page_shows_linked_change_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-047",
                        "ref": "WFA-16",
                        "legacy_id": "TASK-047",
                        "status": "in_review",
                        "title": "Review with change",
                        "epic_id": "EPIC-006",
                        "order": 16,
                    }
                ],
                epics=[{"id": "EPIC-006", "status": "active", "order": 1}],
                changes=[
                    {
                        "id": "CHG-026",
                        "status": "approved",
                        "title": "UIX-10 Add Task Review Package View",
                        "linked_tasks": ["TASK-047"],
                        "order": 26,
                    }
                ],
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/reviews", model)

        self.assertEqual(status.value, 200)
        self.assertIn("Linked Evolution Change", body)
        self.assertIn("CHG-026", body)
        self.assertIn("approved", body)
        self.assertIn("UIX-10 Add Task Review Package View", body)

    def test_reviews_page_hides_decision_controls_for_invalid_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-001",
                        "ref": "DOC-01",
                        "legacy_id": "TASK-001",
                        "status": "ready",
                        "title": "Ready task",
                        "epic_id": "EPIC-001",
                        "order": 1,
                    }
                ],
                epics=[{"id": "EPIC-001", "status": "active", "order": 1}],
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/reviews?task=DOC-01", model)

        self.assertEqual(status.value, 200)
        self.assertIn("Ready task", body)
        self.assertIn(
            "Review decision controls unavailable: task status is ready.",
            body,
        )
        self.assertNotIn('value="task.close_reviewed"', body)
        self.assertNotIn('value="task.request_changes"', body)

    def test_tasks_page_shows_dependency_and_missing_change_blockers(self):
        tasks = [
            {
                "id": "TASK-099",
                "ref": "WFA-09",
                "legacy_id": "TASK-099",
                "status": "in_progress",
                "title": "Dependency task",
                "epic_id": "EPIC-006",
                "epic_key": "WFA",
            },
            {
                "id": "TASK-100",
                "ref": "WFA-10",
                "legacy_id": "TASK-100",
                "status": "ready",
                "title": "Needs change and dependency",
                "summary": "Ready but blocked.",
                "epic_id": "EPIC-006",
                "epic_key": "WFA",
                "notes": ["Requires approved Evolution Change before execution."],
                "depends_on": [{"task_id": "TASK-099", "type": "hard"}],
            },
            {
                "id": "TASK-200",
                "ref": "WFA-20",
                "legacy_id": "TASK-200",
                "status": "in_progress",
                "title": "Current task",
                "epic_id": "EPIC-006",
                "epic_key": "WFA",
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=tasks,
                current_task_id="TASK-200",
                epics=[{"id": "EPIC-006", "key": "WFA", "status": "active"}],
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/tasks?status=ready&group=none", model)

        self.assertEqual(status.value, 200)
        self.assertIn("Next:</strong> Create Change", body)
        self.assertIn("Prepare for Codex unavailable", body)
        self.assertIn("WFA-09 status is in_progress", body)
        self.assertIn("linked Evolution Change is missing", body)
        self.assertIn("another current task is WFA-20", body)
        self.assertNotIn('value="task.prepare_for_codex"', body)

    def test_tasks_page_shows_linked_change_status_and_approval_hint(self):
        tasks = [
            {
                "id": "TASK-100",
                "ref": "WFA-10",
                "legacy_id": "TASK-100",
                "status": "ready",
                "title": "Needs approved change",
                "epic_id": "EPIC-006",
                "epic_key": "WFA",
                "notes": ["Requires approved Evolution Change before execution."],
            }
        ]
        changes = [
            {
                "id": "CHG-050",
                "status": "ready",
                "change_type": "tooling",
                "title": "Ready task change",
                "linked_tasks": ["TASK-100"],
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=tasks,
                changes=changes,
                epics=[{"id": "EPIC-006", "key": "WFA", "status": "active"}],
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/tasks?group=none", model)

        self.assertEqual(status.value, 200)
        self.assertIn("Next:</strong> Approve Change", body)
        self.assertIn("Linked Change:</strong> CHG-050 ready", body)
        self.assertIn("linked Change CHG-050 ready needs approval", body)
        self.assertNotIn('value="task.prepare_for_codex"', body)

    def test_tasks_page_suggests_prepare_for_changes_requested(self):
        tasks = [
            {
                "id": "TASK-100",
                "ref": "WFA-10",
                "legacy_id": "TASK-100",
                "status": "changes_requested",
                "title": "Needs rework",
                "epic_id": "EPIC-006",
                "epic_key": "WFA",
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=tasks,
                epics=[{"id": "EPIC-006", "key": "WFA", "status": "active"}],
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/tasks?group=none", model)

        self.assertEqual(status.value, 200)
        self.assertIn("Next:</strong> Prepare for Codex", body)
        self.assertIn('value="task.prepare_for_codex"', body)

    def test_tasks_page_shows_only_review_decision_workflows_for_in_review_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root, **large_task_view_state())
            model = ReadOnlyProjectModel(root, actor="tester")

            review_status, _, review_body = route(
                "/tasks?status=in_review&group=none",
                model,
            )

        self.assertEqual(review_status.value, 200)
        self.assertIn("Approve &amp; Done", review_body)
        self.assertIn('value="task.close_reviewed"', review_body)
        self.assertIn("Approval Notes", review_body)
        self.assertIn("Request Changes", review_body)
        self.assertIn('value="task.request_changes"', review_body)
        self.assertIn("Change Request Notes", review_body)
        self.assertIn('name="notes" rows="2"', review_body)
        self.assertNotIn('value="task.prepare_for_codex"', review_body)
        self.assertNotIn('value="task.refresh_execution_context"', review_body)
        self.assertNotIn('value="task.submit_for_review"', review_body)

    def test_tasks_page_suggests_refresh_for_current_review_task_with_stale_context(self):
        tasks = [
            {
                "id": "TASK-100",
                "ref": "WFA-10",
                "legacy_id": "TASK-100",
                "status": "in_review",
                "title": "Review task with stale context",
                "epic_id": "EPIC-006",
                "epic_key": "WFA",
            }
        ]
        execution = {
            "status": "READY",
            "code": "CODEX_READY",
            "prompt_exists": True,
            "source_type": "task",
            "source_id": "TASK-100",
            "source_status": "in_review",
            "context_pack": {
                "task_id": "TASK-100",
                "tasks_revision": 0,
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=tasks,
                current_task_id="TASK-100",
                epics=[{"id": "EPIC-006", "key": "WFA", "status": "active"}],
                execution=execution,
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/tasks?status=in_review&group=none", model)

        self.assertEqual(status.value, 200)
        self.assertIn("Next:</strong> Refresh Context", body)
        self.assertIn('value="task.refresh_execution_context"', body)
        self.assertIn("Context Pack tasks revision is 0 but current is 1", body)
        self.assertNotIn("Refresh Context unavailable: task status is in_review", body)

    def test_tasks_page_hides_row_workflows_for_done_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root, **large_task_view_state())
            model = ReadOnlyProjectModel(root, actor="tester")

            done_status, _, done_body = route(
                "/tasks?status=done&show_done=1&group=none",
                model,
            )

        self.assertEqual(done_status.value, 200)
        self.assertIn("No row workflows", done_body)
        self.assertNotIn('value="task.prepare_for_codex"', done_body)
        self.assertNotIn('value="task.refresh_execution_context"', done_body)
        self.assertNotIn('value="task.submit_for_review"', done_body)
        self.assertNotIn('value="task.close_reviewed"', done_body)
        self.assertNotIn('value="task.request_changes"', done_body)

    def test_evolution_page_filters_and_shows_change_actions(self):
        changes = [
            {
                "id": "CHG-041",
                "status": "ready",
                "change_type": "tooling",
                "title": "Ready change",
                "linked_tasks": ["TASK-041"],
                "affected_files": ["ai_project_ctl/web/server.py"],
                "risks": ["Needs owner approval."],
            },
            {
                "id": "CHG-042",
                "status": "accepted",
                "change_type": "docs",
                "title": "Accepted docs change",
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root, **large_task_view_state(), changes=changes)
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route(
                "/evolution?status=ready&type=tooling&q=server",
                model,
            )
            data_status, _, data_body = route("/data.json", model)

        payload = json.loads(data_body)

        self.assertEqual(status.value, 200)
        self.assertEqual(data_status.value, 200)
        self.assertEqual(len(payload["changes"]), 2)
        self.assertIn("Evolution Filters", body)
        self.assertIn("CHG-041", body)
        self.assertIn("Ready change", body)
        self.assertIn("TASK-041", body)
        self.assertIn("ai_project_ctl/web/server.py", body)
        self.assertIn('value="evolution.create_for_task"', body)
        self.assertIn('value="evolution.approve_change"', body)
        self.assertIn("Approval Notes", body)
        self.assertNotIn("Accepted docs change", body)

    def test_evolution_page_shows_review_and_accept_actions(self):
        state = large_task_view_state()
        state["tasks"].append(
            {
                "id": "TASK-044",
                "ref": "WFA-13",
                "legacy_id": "TASK-044",
                "status": "done",
                "title": "Done review controls",
                "epic_id": "EPIC-006",
                "epic_key": "WFA",
            }
        )
        changes = [
            {
                "id": "CHG-043",
                "status": "approved",
                "change_type": "tooling",
                "title": "Approved change",
                "linked_tasks": ["TASK-037"],
            },
            {
                "id": "CHG-044",
                "status": "in_review",
                "change_type": "tooling",
                "title": "Review change",
                "linked_tasks": ["TASK-044"],
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root, **state, changes=changes)
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/evolution", model)

        self.assertEqual(status.value, 200)
        self.assertIn('value="evolution.move_to_review"', body)
        self.assertIn("Move to Review", body)
        self.assertIn("Accept Change unavailable: WFA-06 status is in_review", body)
        self.assertIn('value="evolution.accept_change"', body)
        self.assertIn("Acceptance Notes", body)

    def test_epics_page_shows_close_hints_and_blockers(self):
        tasks = [
            {
                "id": "TASK-100",
                "ref": "WFA-10",
                "status": "in_progress",
                "epic_id": "EPIC-006",
            },
            {
                "id": "TASK-200",
                "ref": "DOC-02",
                "status": "done",
                "epic_id": "EPIC-001",
            },
        ]
        changes = [
            {
                "id": "CHG-050",
                "status": "ready",
                "title": "Review WFA close blockers",
                "linked_tasks": ["TASK-100"],
            }
        ]
        epics = [
            {"id": "EPIC-001", "key": "DOC", "status": "active", "title": "Docs"},
            {"id": "EPIC-006", "key": "WFA", "status": "active", "title": "Workflow"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root, tasks=tasks, epics=epics, changes=changes)
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/epics", model)

        self.assertEqual(status.value, 200)
        self.assertIn("Tasks", body)
        self.assertIn("Open Changes", body)
        self.assertIn("1 / 1 closed", body)
        self.assertIn("0 / 1 closed", body)
        self.assertIn("1 open", body)
        self.assertIn("done 1", body)
        self.assertIn("in_progress 1", body)
        self.assertIn("Next:</strong> Close Epic If Complete", body)
        self.assertIn('value="epic.close_if_complete"', body)
        self.assertIn('name="epic" value="DOC"', body)
        self.assertIn("Confirm", body)
        self.assertIn(
            "Close Epic If Complete unavailable: WFA-10 status is in_progress",
            body,
        )
        self.assertIn("CHG-050 ready", body)
        self.assertIn("Review WFA close blockers", body)

    def test_doctor_refresh_runs_diagnostics_and_reuses_cache(self):
        calls = []

        def fake_run(argv, **_kwargs):
            calls.append(argv)
            script = Path(argv[1]).name
            tail = argv[argv.index("--json") + 1 :] if "--json" in argv else argv[-3:]
            if script == "aictl.py" and tail == ["project", "doctor"]:
                return completed(
                    {
                        "data": {
                            "overall_status": "WARN",
                            "summary": {"PASS": 1, "WARN": 1, "FAIL": 0},
                            "findings": [
                                {
                                    "status": "WARN",
                                    "check": "context generated output",
                                    "message": "Generated context files are stale.",
                                }
                            ],
                        }
                    }
                )
            if script.endswith("ctl.py"):
                return process(stdout="")
            raise AssertionError("unexpected command: {}".format(argv))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root)
            model = ReadOnlyProjectModel(root, actor="tester")
            with patch("ai_project_ctl.web.read_model.subprocess.run", side_effect=fake_run):
                doctor_status, _, doctor_body = route("/doctor?refresh=1", model)
                data_status, _, data_body = route("/data.json", model)

        doctor_calls = [
            call
            for call in calls
            if Path(call[1]).name == "aictl.py" and call[-2:] == ["project", "doctor"]
        ]
        payload = json.loads(data_body)

        self.assertEqual(doctor_status.value, 200)
        self.assertEqual(data_status.value, 200)
        self.assertIn("Generated context files are stale.", doctor_body)
        self.assertEqual(len(doctor_calls), 1)
        self.assertEqual(payload["doctor"]["overall_status"], "WARN")
        self.assertTrue(payload["doctor"]["cache"]["cached"])

    def test_project_health_panel_shows_warn_fail_and_repair_actions(self):
        def fake_run(argv, **_kwargs):
            tail = argv[argv.index("--json") + 1 :] if "--json" in argv else argv[-3:]
            if Path(argv[1]).name == "aictl.py" and tail == ["project", "doctor"]:
                return completed(
                    {
                        "data": {
                            "overall_status": "FAIL",
                            "summary": {"PASS": 1, "WARN": 1, "FAIL": 1},
                            "findings": [
                                {
                                    "status": "WARN",
                                    "check": "docs generated output",
                                    "message": "Generated docs are stale.",
                                },
                                {
                                    "status": "FAIL",
                                    "check": "protected project files",
                                    "message": "Protected-file check failed.",
                                },
                            ],
                        }
                    }
                )
            raise AssertionError("unexpected command: {}".format(argv))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root)
            model = ReadOnlyProjectModel(root, actor="tester")
            with patch("ai_project_ctl.web.read_model.subprocess.run", side_effect=fake_run):
                status, _, body = route("/doctor?refresh=1", model)

        self.assertEqual(status.value, 200)
        self.assertIn("Project Health", body)
        self.assertIn("Generated docs are stale.", body)
        self.assertIn("Protected-file check failed.", body)
        self.assertIn("Render Docs", body)
        self.assertIn('value="docs.render"', body)
        self.assertIn("Check Protected Files", body)
        self.assertIn('value="project.protected_check"', body)
        self.assertIn("FAIL", body)

    def test_tasks_page_health_actions_use_single_selected_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-049",
                        "ref": "WFA-18",
                        "legacy_id": "TASK-049",
                        "status": "ready",
                        "title": "Selected repair target",
                        "epic_id": "EPIC-006",
                    }
                ],
                epics=[{"id": "EPIC-006", "key": "WFA", "status": "active"}],
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/tasks?q=WFA-18", model)

        self.assertEqual(status.value, 200)
        self.assertIn("Refresh Context/Codex", body)
        self.assertIn('value="task.refresh_execution_context"', body)
        self.assertIn('name="task" value="WFA-18"', body)

    def test_dashboard_health_actions_reject_missing_task_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root)
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/", model)

        self.assertEqual(status.value, 200)
        self.assertIn("No safe target task exists.", body)
        self.assertNotIn('value="task.refresh_execution_context"', body)

    def test_post_action_invalidates_doctor_cache(self):
        def fake_doctor_run(argv, **_kwargs):
            tail = argv[argv.index("--json") + 1 :] if "--json" in argv else argv[-3:]
            if Path(argv[1]).name == "aictl.py" and tail == ["project", "doctor"]:
                return completed(
                    {
                        "data": {
                            "overall_status": "PASS",
                            "summary": {"PASS": 1, "WARN": 0, "FAIL": 0},
                            "findings": [],
                        }
                    }
                )
            raise AssertionError("unexpected command: {}".format(argv))

        def fake_action_run(argv, **_kwargs):
            return process(
                stdout=json.dumps(
                    {
                        "ok": True,
                        "data": {
                            "delegate": ["python", "scripts/taskctl.py"],
                            "stdout": "OK: task.transition revision 1 -> 2\n",
                        },
                    }
                )
                + "\n"
            )

        with tempfile.TemporaryDirectory() as tmp:
            model = ReadOnlyProjectModel(tmp, actor="tester")
            with patch(
                "ai_project_ctl.web.read_model.subprocess.run",
                side_effect=fake_doctor_run,
            ):
                model.doctor(refresh=True)

            self.assertTrue(model.doctor()["cache"]["cached"])

            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(model))
            thread = threading.Thread(target=server.serve_forever)
            thread.daemon = True
            thread.start()
            try:
                url = "http://127.0.0.1:{}/actions".format(server.server_address[1])
                body = json.dumps(
                    {
                        "action": "task.transition",
                        "confirm": "yes",
                        "task": "TASK-001",
                        "to": "in_review",
                    }
                ).encode("utf-8")
                request = urllib.request.Request(
                    url,
                    data=body,
                    method="POST",
                    headers={"Content-Type": "application/json"},
                )
                with patch(
                    "ai_project_ctl.web.actions.subprocess.run",
                    side_effect=fake_action_run,
                ):
                    response = urllib.request.urlopen(request, timeout=5)
                    body = response.read().decode("utf-8")

                self.assertEqual(response.status, 200)
                self.assertEqual(response.headers["Content-Type"], "text/html; charset=utf-8")
                self.assertIn("Action Result", body)
                self.assertIn("Task transition", body)
                self.assertFalse(model.doctor()["cache"]["cached"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_unknown_post_route_is_rejected_without_model_reads(self):
        class ExplodingModel:
            def dashboard(self):
                raise AssertionError("POST should not read the model")

        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(ExplodingModel()))
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        try:
            url = "http://127.0.0.1:{}/tasks".format(server.server_address[1])
            request = urllib.request.Request(url, data=b"x", method="POST")
            with self.assertRaises(urllib.error.HTTPError) as raised:
                urllib.request.urlopen(request, timeout=5)

            self.assertEqual(raised.exception.code, 404)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_unsafe_methods_are_rejected(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(ReadOnlyProjectModel(".")))
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        try:
            url = "http://127.0.0.1:{}/actions".format(server.server_address[1])
            request = urllib.request.Request(url, data=b"x", method="PUT")
            with self.assertRaises(urllib.error.HTTPError) as raised:
                urllib.request.urlopen(request, timeout=5)

            self.assertEqual(raised.exception.code, 405)
            self.assertEqual(raised.exception.headers["Allow"], "GET, HEAD, POST")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_post_action_requires_confirmation_before_delegating(self):
        with tempfile.TemporaryDirectory() as tmp:
            server = ThreadingHTTPServer(
                ("127.0.0.1", 0),
                make_handler(ReadOnlyProjectModel(tmp, actor="tester")),
            )
            thread = threading.Thread(target=server.serve_forever)
            thread.daemon = True
            thread.start()
            try:
                url = "http://127.0.0.1:{}/actions".format(server.server_address[1])
                body = json.dumps(
                    {
                        "action": "task.transition",
                        "task": "TASK-001",
                        "to": "in_review",
                    }
                ).encode("utf-8")
                request = urllib.request.Request(
                    url,
                    data=body,
                    method="POST",
                    headers={"Content-Type": "application/json"},
                )
                with self.assertRaises(urllib.error.HTTPError) as raised:
                    urllib.request.urlopen(request, timeout=5)

                body = raised.exception.read().decode("utf-8")
                self.assertEqual(raised.exception.code, 400)
                self.assertIn("Action failed", body)
                self.assertIn("WEB_ACTION_CONFIRMATION_REQUIRED", body)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_post_allowed_action_delegates_through_aictl(self):
        calls = []

        def fake_run(argv, **_kwargs):
            calls.append(argv)
            return process(
                stdout=json.dumps(
                    {
                        "ok": True,
                        "data": {
                            "delegate": ["python", "scripts/taskctl.py"],
                            "stdout": "OK: task.transition revision 1 -> 2\n",
                        },
                    }
                )
                + "\n"
            )

        with tempfile.TemporaryDirectory() as tmp:
            server = ThreadingHTTPServer(
                ("127.0.0.1", 0),
                make_handler(ReadOnlyProjectModel(tmp, actor="tester")),
            )
            thread = threading.Thread(target=server.serve_forever)
            thread.daemon = True
            thread.start()
            try:
                url = "http://127.0.0.1:{}/actions".format(server.server_address[1])
                body = json.dumps(
                    {
                        "action": "task.transition",
                        "confirm": "yes",
                        "task": "TASK-001",
                        "to": "in_review",
                    }
                ).encode("utf-8")
                request = urllib.request.Request(
                    url,
                    data=body,
                    method="POST",
                    headers={"Content-Type": "application/json"},
                )
                with patch("ai_project_ctl.web.actions.subprocess.run", side_effect=fake_run):
                    response = urllib.request.urlopen(request, timeout=5)
                    body = response.read().decode("utf-8")

                self.assertEqual(response.status, 200)
                self.assertEqual(response.headers["Content-Type"], "text/html; charset=utf-8")
                self.assertIn("Action Result", body)
                self.assertIn("Task transition", body)
                self.assertEqual(Path(calls[0][1]).name, "aictl.py")
                self.assertEqual(
                    calls[0][-5:],
                    ["task", "transition", "TASK-001", "--to", "in_review"],
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_task_create_web_action_delegates_to_aictl_create_only_workflow(self):
        calls = []

        def fake_run(argv, **_kwargs):
            calls.append(argv)
            return process(
                stdout=json.dumps(
                    {
                        "ok": True,
                        "data": {
                            "created_task_id": "TASK-099",
                            "create_only": True,
                            "steps": [],
                        },
                    }
                )
                + "\n"
            )

        with patch("ai_project_ctl.web.actions.subprocess.run", side_effect=fake_run):
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "task.create",
                    "confirm": "yes",
                    "epic": "EPIC-006",
                    "title": "Create task from web",
                    "summary": "Short summary",
                    "scope": "Do one thing\nDo another thing",
                    "allowed_file": "README.md",
                    "acceptance": "Validation passes",
                    "depends_on": "TASK-032",
                    "dependency_reason": "Needs WFA-01.",
                }
            )

        argv = calls[0]

        self.assertTrue(result.ok)
        self.assertEqual(Path(argv[1]).name, "aictl.py")
        self.assertIn("--json", argv)
        self.assertEqual(argv[argv.index("--json") + 1 : argv.index("--json") + 4], ["task", "create", "--confirm"])
        self.assertIn("--scope", argv)
        self.assertIn("Do one thing", argv)
        self.assertIn("Do another thing", argv)
        self.assertIn("--depends-on", argv)
        self.assertIn("TASK-032", argv)

    def test_actions_page_renders_task_create_form_with_epic_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                epics=[
                    {
                        "id": "EPIC-006",
                        "key": "WFA",
                        "status": "active",
                        "title": "Workflow Automation",
                    }
                ],
            )
            status, _, body = route(
                "/actions",
                ReadOnlyProjectModel(root, actor="tester"),
            )

        self.assertEqual(status.value, 200)
        self.assertIn("Create Task", body)
        self.assertIn('value="task.create"', body)
        self.assertIn('name="epic"', body)
        self.assertIn('value="EPIC-006"', body)
        self.assertIn("Workflow Automation", body)

    def test_task_import_web_action_previews_without_confirmation(self):
        calls = []
        payload = '{"tasks":[{"epic":"EPIC-006","title":"Imported"}]}'

        def fake_run(argv, **_kwargs):
            calls.append(argv)
            return process(
                stdout=json.dumps(
                    {
                        "ok": True,
                        "data": {
                            "dry_run": True,
                            "task_count": 1,
                            "steps": [],
                        },
                    }
                )
                + "\n"
            )

        with patch("ai_project_ctl.web.actions.subprocess.run", side_effect=fake_run):
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "task.import",
                    "import_text": payload,
                }
            )

        argv = calls[0]

        self.assertTrue(result.ok)
        self.assertEqual(Path(argv[1]).name, "aictl.py")
        self.assertIn("--json", argv)
        tail = argv[argv.index("--json") + 1 :]
        self.assertEqual(tail[:4], ["task", "import", "--text", payload])
        self.assertIn("--preview", tail)
        self.assertNotIn("--confirm", tail)

    def test_task_import_web_action_confirms_before_creation(self):
        calls = []
        payload = '{"tasks":[{"epic":"EPIC-006","title":"Imported"}]}'

        def fake_run(argv, **_kwargs):
            calls.append(argv)
            return process(
                stdout=json.dumps(
                    {
                        "ok": True,
                        "data": {
                            "dry_run": False,
                            "created_task_ids": ["TASK-099"],
                            "steps": [],
                        },
                    }
                )
                + "\n"
            )

        with patch("ai_project_ctl.web.actions.subprocess.run", side_effect=fake_run):
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "task.import",
                    "confirm": "yes",
                    "import_text": payload,
                }
            )

        argv = calls[0]
        tail = argv[argv.index("--json") + 1 :]

        self.assertTrue(result.ok)
        self.assertEqual(tail[:4], ["task", "import", "--text", payload])
        self.assertIn("--confirm", tail)
        self.assertNotIn("--preview", tail)

    def test_task_import_multipart_file_upload_previews_via_text_payload(self):
        calls = []
        payload = '{"tasks":[{"epic":"EPIC-006","title":"Imported from file"}]}'

        def fake_run(argv, **_kwargs):
            calls.append(argv)
            return process(
                stdout=json.dumps(
                    {
                        "ok": True,
                        "data": {
                            "dry_run": True,
                            "task_count": 1,
                            "steps": [],
                        },
                    }
                )
                + "\n"
            )

        with tempfile.TemporaryDirectory() as tmp:
            server = ThreadingHTTPServer(
                ("127.0.0.1", 0),
                make_handler(ReadOnlyProjectModel(tmp, actor="tester")),
            )
            thread = threading.Thread(target=server.serve_forever)
            thread.daemon = True
            thread.start()
            try:
                url = "http://127.0.0.1:{}/actions".format(server.server_address[1])
                boundary, body = multipart_body(
                    {"action": "task.import"},
                    {"import_file": ("tasks.json", "application/json", payload)},
                )
                request = urllib.request.Request(
                    url,
                    data=body,
                    method="POST",
                    headers={
                        "Content-Type": "multipart/form-data; boundary={}".format(
                            boundary
                        )
                    },
                )
                with patch(
                    "ai_project_ctl.web.actions.subprocess.run",
                    side_effect=fake_run,
                ):
                    response = urllib.request.urlopen(request, timeout=5)
                    body_html = response.read().decode("utf-8")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        tail = calls[0][calls[0].index("--json") + 1 :]

        self.assertEqual(response.status, 200)
        self.assertIn("Bulk import tasks", body_html)
        self.assertEqual(tail[:4], ["task", "import", "--text", payload])
        self.assertIn("--preview", tail)
        self.assertNotIn("--file", tail)

    def test_task_import_upload_rejects_unsupported_file_type_before_delegating(self):
        calls = []

        with tempfile.TemporaryDirectory() as tmp:
            server = ThreadingHTTPServer(
                ("127.0.0.1", 0),
                make_handler(ReadOnlyProjectModel(tmp, actor="tester")),
            )
            thread = threading.Thread(target=server.serve_forever)
            thread.daemon = True
            thread.start()
            try:
                url = "http://127.0.0.1:{}/actions".format(server.server_address[1])
                boundary, body = multipart_body(
                    {"action": "task.import"},
                    {"import_file": ("tasks.py", "text/x-python", '{"tasks": []}')},
                )
                request = urllib.request.Request(
                    url,
                    data=body,
                    method="POST",
                    headers={
                        "Content-Type": "multipart/form-data; boundary={}".format(
                            boundary
                        )
                    },
                )
                with patch(
                    "ai_project_ctl.web.actions.subprocess.run",
                    side_effect=calls.append,
                ):
                    with self.assertRaises(urllib.error.HTTPError) as raised:
                        urllib.request.urlopen(request, timeout=5)
                    body_html = raised.exception.read().decode("utf-8")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(raised.exception.code, 400)
        self.assertIn("WEB_IMPORT_FILE_TYPE_REJECTED", body_html)
        self.assertEqual(calls, [])

    def test_task_import_upload_rejects_oversized_file_before_delegating(self):
        calls = []
        oversized = b"[" + b" " * WEB_IMPORT_FILE_MAX_BYTES + b"]"

        with tempfile.TemporaryDirectory() as tmp:
            server = ThreadingHTTPServer(
                ("127.0.0.1", 0),
                make_handler(ReadOnlyProjectModel(tmp, actor="tester")),
            )
            thread = threading.Thread(target=server.serve_forever)
            thread.daemon = True
            thread.start()
            try:
                url = "http://127.0.0.1:{}/actions".format(server.server_address[1])
                boundary, body = multipart_body(
                    {"action": "task.import"},
                    {"import_file": ("tasks.json", "application/json", oversized)},
                )
                request = urllib.request.Request(
                    url,
                    data=body,
                    method="POST",
                    headers={
                        "Content-Type": "multipart/form-data; boundary={}".format(
                            boundary
                        )
                    },
                )
                with patch(
                    "ai_project_ctl.web.actions.subprocess.run",
                    side_effect=calls.append,
                ):
                    with self.assertRaises(urllib.error.HTTPError) as raised:
                        urllib.request.urlopen(request, timeout=5)
                    body_html = raised.exception.read().decode("utf-8")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(raised.exception.code, 400)
        self.assertIn("WEB_IMPORT_FILE_TOO_LARGE", body_html)
        self.assertEqual(calls, [])

    def test_actions_page_renders_bulk_import_form(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root)
            status, _, body = route("/actions", ReadOnlyProjectModel(root, actor="tester"))

        self.assertEqual(status.value, 200)
        self.assertIn("Bulk Task Import", body)
        self.assertIn('value="task.import"', body)
        self.assertIn('name="import_text"', body)
        self.assertIn('enctype="multipart/form-data"', body)
        self.assertIn('type="file" name="import_file"', body)
        self.assertIn('accept=".json,.txt,application/json,text/plain"', body)
        self.assertIn("Preview / Import", body)

    def test_unknown_web_action_does_not_edit_protected_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            protected = root / "AI_PROJECT/state/tasks.json"
            protected.parent.mkdir(parents=True)
            protected.write_text("sentinel\n", encoding="utf-8")

            executor = WebActionExecutor(root, actor="tester")
            with self.assertRaises(WebActionError) as raised:
                executor.execute(
                    {
                        "action": "project.render",
                        "confirm": "yes",
                        "path": "AI_PROJECT/state/tasks.json",
                        "content": "{}",
                    }
                )

            self.assertEqual(raised.exception.code, "WEB_FILE_WRITE_ARGUMENT_REJECTED")
            self.assertEqual(protected.read_text(encoding="utf-8"), "sentinel\n")

    def test_close_epic_web_action_rejects_direct_file_write_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            protected = root / "AI_PROJECT/state/plan.json"
            protected.parent.mkdir(parents=True)
            protected.write_text("sentinel\n", encoding="utf-8")

            executor = WebActionExecutor(root, actor="tester")
            with patch("ai_project_ctl.web.actions.subprocess.run") as run:
                with self.assertRaises(WebActionError) as raised:
                    executor.execute(
                        {
                            "action": "epic.close_if_complete",
                            "confirm": "yes",
                            "epic": "WFA",
                            "path": "AI_PROJECT/state/plan.json",
                            "content": "{}",
                        }
                    )

                self.assertEqual(raised.exception.code, "WEB_FILE_WRITE_ARGUMENT_REJECTED")
                self.assertEqual(protected.read_text(encoding="utf-8"), "sentinel\n")
                run.assert_not_called()

    def test_unsafe_task_transition_target_is_rejected_before_subprocess(self):
        executor = WebActionExecutor(".", actor="tester")
        with patch("ai_project_ctl.web.actions.subprocess.run") as run:
            with self.assertRaises(WebActionError) as raised:
                executor.execute(
                    {
                        "action": "task.transition",
                        "confirm": "yes",
                        "task": "TASK-001",
                        "to": "done",
                    }
                )

        self.assertEqual(raised.exception.code, "WEB_UNSAFE_TASK_TRANSITION")
        run.assert_not_called()

    def test_successful_task_transition_writes_audit_event_through_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_ctl(root, "planctl.py", "init")
            run_ctl(root, "planctl.py", "initiative", "create", "--title", "Control")
            run_ctl(root, "planctl.py", "epic", "create", "--initiative", "INIT-001", "--title", "Tasks")
            run_ctl(root, "taskctl.py", "init")
            run_ctl(
                root,
                "taskctl.py",
                "task",
                "create",
                "--epic",
                "EPIC-001",
                "--title",
                "Audit task",
                "--status",
                "ready",
                "--scope",
                "Transition task",
                "--allowed-file",
                "README.md",
                "--acceptance",
                "Audit event exists",
            )

            result = WebActionExecutor(root, actor="tester").execute(
                {
                    "action": "task.transition",
                    "confirm": "yes",
                    "task": "TASK-001",
                    "to": "in_progress",
                }
            )

            events = [
                json.loads(line)
                for line in (root / "AI_PROJECT/events/task-events.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
                if line.strip()
            ]
            self.assertTrue(result.ok)
            self.assertIn("task.transition", [event.get("command") for event in events])

    def test_task_report_submit_stores_report_without_touching_tasks_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_basic_task_project(root)
            report_file = write_execution_report(root / "report.json", task_id="TASK-001")
            tasks_path = root / "AI_PROJECT/state/tasks.json"
            tasks_before = tasks_path.read_text(encoding="utf-8")

            completed = run_ctl(
                root,
                "taskctl.py",
                "task",
                "report",
                "submit",
                "--task",
                "TASK-001",
                "--file",
                str(report_file),
                "--confirm",
                "--json",
            )

            payload = json.loads(completed.stdout)
            reports_state = json.loads(
                (root / "AI_PROJECT/state/task_reports.json").read_text(encoding="utf-8")
            )
            events = [
                json.loads(line)
                for line in (root / "AI_PROJECT/events/task-report-events.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
                if line.strip()
            ]
            model = ReadOnlyProjectModel(root, actor="tester")
            task = model.dashboard()["tasks"][0]
            tasks_after = tasks_path.read_text(encoding="utf-8")

        self.assertEqual(payload["report_id"], "RPT-001")
        self.assertEqual(reports_state["latest_by_task"]["TASK-001"], "RPT-001")
        self.assertEqual(events[-1]["command"], "task.report.submit")
        self.assertEqual(tasks_after, tasks_before)
        self.assertEqual(task["latest_report"]["id"], "RPT-001")

    def test_task_report_submit_rejects_invalid_task_without_persistent_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_basic_task_project(root)
            report_file = write_execution_report(root / "report.json", task_id="TASK-999")

            completed = run_ctl_raw(
                root,
                "taskctl.py",
                "task",
                "report",
                "submit",
                "--task",
                "TASK-001",
                "--file",
                str(report_file),
                "--confirm",
            )
            report_state_exists = (root / "AI_PROJECT/state/task_reports.json").exists()

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("INVALID_REPORT_SCHEMA", completed.stderr)
        self.assertFalse(report_state_exists)

    def test_task_report_submit_rejects_invalid_schema_without_persistent_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_basic_task_project(root)
            report_file = root / "bad-report.json"
            report_file.write_text(
                json.dumps(
                    {
                        "task_id": "TASK-001",
                        "implementation_summary": "Missing required lists.",
                        "commands": ["python scripts/taskctl.py task transition TASK-001 --to done"],
                    }
                ),
                encoding="utf-8",
            )

            completed = run_ctl_raw(
                root,
                "taskctl.py",
                "task",
                "report",
                "submit",
                "--task",
                "TASK-001",
                "--file",
                str(report_file),
                "--confirm",
            )
            report_state_exists = (root / "AI_PROJECT/state/task_reports.json").exists()

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("INVALID_REPORT_SCHEMA", completed.stderr)
        self.assertFalse(report_state_exists)

    def test_task_report_submit_rejects_missing_file_without_persistent_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_basic_task_project(root)

            completed = run_ctl_raw(
                root,
                "taskctl.py",
                "task",
                "report",
                "submit",
                "--task",
                "TASK-001",
                "--file",
                str(root / "missing-report.json"),
                "--confirm",
            )
            report_state_exists = (root / "AI_PROJECT/state/task_reports.json").exists()

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("REPORT_FILE_NOT_FOUND", completed.stderr)
        self.assertFalse(report_state_exists)

    def test_workflow_web_action_delegates_to_confirmed_aictl_workflow(self):
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"ok": true, "data": {"steps": []}}\n',
            stderr="",
        )

        with patch("ai_project_ctl.web.actions.subprocess.run", return_value=completed_process) as run:
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "task.refresh_execution_context",
                    "confirm": "yes",
                    "task": "WFA-01",
                }
            )

        argv = run.call_args.args[0]

        self.assertTrue(result.ok)
        self.assertEqual(Path(argv[1]).name, "aictl.py")
        self.assertEqual(
            argv[-6:],
            [
                "workflow",
                "run",
                "task.refresh_execution_context",
                "--task",
                "WFA-01",
                "--confirm",
            ],
        )

    def test_health_repair_web_actions_delegate_to_aictl(self):
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"ok": true, "data": {"delegate": ["python"]}}\n',
            stderr="",
        )

        cases = [
            ("project.doctor", ["project", "doctor"]),
            ("project.protected_check", ["project", "protected-check"]),
            ("docs.render", ["docs", "render"]),
        ]
        for action, expected_tail in cases:
            with self.subTest(action=action):
                with patch(
                    "ai_project_ctl.web.actions.subprocess.run",
                    return_value=completed_process,
                ) as run:
                    result = WebActionExecutor("/tmp/project", actor="tester").execute(
                        {
                            "action": action,
                            "confirm": "yes",
                        }
                    )

                argv = run.call_args.args[0]

                self.assertTrue(result.ok)
                self.assertEqual(Path(argv[1]).name, "aictl.py")
                self.assertEqual(argv[-len(expected_tail) :], expected_tail)

    def test_prepare_for_codex_action_result_includes_next_instruction(self):
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps(
                {
                    "ok": True,
                    "command": "task.prepare_for_codex",
                    "domain": "workflow",
                    "message": "Workflow completed.",
                    "data": {
                        "steps": [
                            {
                                "id": "current_set",
                                "title": "Set current task",
                                "status": "ok",
                            },
                            {
                                "id": "codex_build",
                                "title": "Build Codex prompt with context",
                                "status": "ok",
                            },
                        ]
                    },
                    "next_actions": [],
                    "owner_action_required": None,
                }
            )
            + "\n",
            stderr="",
        )

        with patch("ai_project_ctl.web.actions.subprocess.run", return_value=completed_process):
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "task.prepare_for_codex",
                    "confirm": "yes",
                    "task": "WFA-08",
                }
            )

        payload = result.to_dict()

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["summary"]["step_counts"]["ok"], 2)
        self.assertEqual(
            payload["summary"]["next_codex_instruction"],
            "Read AI_PROJECT/generated/CODEX_PROMPT.md and execute it.",
        )
        self.assertIn(
            "Read AI_PROJECT/generated/CODEX_PROMPT.md and execute it.",
            payload["summary"]["next_actions"],
        )

    def test_action_result_panel_shows_steps_files_messages_and_copy_instruction(self):
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps(
                {
                    "ok": True,
                    "command": "task.prepare_for_codex",
                    "domain": "workflow",
                    "message": "Workflow completed.",
                    "data": {
                        "workflow": {
                            "name": "task.prepare_for_codex",
                            "label": "Prepare for Codex",
                        },
                        "task_ref": "WFA-09",
                        "task": {"id": "TASK-040", "ref": "WFA-09"},
                        "steps": [
                            {
                                "id": "current_set",
                                "title": "Set current task",
                                "status": "ok",
                            },
                            {
                                "id": "task_in_progress",
                                "title": "Move task to in_progress when needed",
                                "status": "skipped",
                                "skip_reason": "Task already in progress.",
                            },
                        ],
                    },
                    "warnings": [
                        {
                            "code": "CHECK_WARN",
                            "message": "Advisory check reported a warning.",
                        }
                    ],
                    "changed_files": ["ai_project_ctl/web/server.py"],
                    "generated_files": ["AI_PROJECT/generated/CODEX_PROMPT.md"],
                    "next_actions": [],
                    "owner_action_required": "Open the generated prompt in Codex.",
                }
            )
            + "\n",
            stderr="",
        )

        with patch("ai_project_ctl.web.actions.subprocess.run", return_value=completed_process):
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "task.prepare_for_codex",
                    "confirm": "yes",
                    "task": "WFA-09",
                }
            )

        body = render_action_result(result)

        self.assertIn("task.prepare_for_codex", body)
        self.assertIn("Task WFA-09", body)
        self.assertIn("PASS", body)
        self.assertIn("WARN", body)
        self.assertIn("ai_project_ctl/web/server.py", body)
        self.assertIn("AI_PROJECT/generated/CODEX_PROMPT.md", body)
        self.assertIn("CHECK_WARN", body)
        self.assertIn("Open the generated prompt in Codex.", body)
        self.assertIn("textarea readonly", body)
        self.assertIn("Read AI_PROJECT/generated/CODEX_PROMPT.md and execute it.", body)
        self.assertNotIn("scripts/aictl.py", body)

    def test_action_error_panel_keeps_failed_workflow_step_visible(self):
        error = WebActionError(
            "WEB_ACTION_COMMAND_FAILED",
            "Web write action failed through registered command: task.prepare_for_codex",
            details={
                "action": "task.prepare_for_codex",
                "command": ["python", "scripts/aictl.py", "workflow"],
                "returncode": 2,
                "result": {
                    "ok": False,
                    "command": "task.prepare_for_codex",
                    "domain": "workflow",
                    "message": "Workflow stopped on blocking step: Build task Context Pack",
                    "data": {
                        "workflow": {"name": "task.prepare_for_codex"},
                        "task_ref": "WFA-09",
                        "steps": [
                            {
                                "id": "resolve",
                                "title": "Resolve task reference",
                                "status": "ok",
                            },
                            {
                                "id": "context_build",
                                "title": "Build task Context Pack",
                                "status": "failed",
                                "command": ["python", "scripts/contextctl.py"],
                            },
                        ],
                    },
                    "errors": [
                        {
                            "code": "WORKFLOW_STEP_FAILED",
                            "message": "Workflow step failed: Build task Context Pack",
                        }
                    ],
                },
            },
        )

        body = render_action_error(error)

        self.assertIn("Action failed", body)
        self.assertIn("Build task Context Pack", body)
        self.assertIn("FAIL", body)
        self.assertIn("WORKFLOW_STEP_FAILED", body)
        self.assertNotIn("scripts/aictl.py", body)
        self.assertNotIn("scripts/contextctl.py", body)

    def test_evolution_workflow_web_action_delegates_to_confirmed_aictl_workflow(self):
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"ok": true, "data": {"change_id": "CHG-099", "steps": []}}\n',
            stderr="",
        )

        with patch("ai_project_ctl.web.actions.subprocess.run", return_value=completed_process) as run:
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "evolution.create_for_task",
                    "confirm": "yes",
                    "task": "WFA-02",
                }
            )

        argv = run.call_args.args[0]

        self.assertTrue(result.ok)
        self.assertEqual(Path(argv[1]).name, "aictl.py")
        self.assertEqual(
            argv[-6:],
            [
                "workflow",
                "run",
                "evolution.create_for_task",
                "--task",
                "WFA-02",
                "--confirm",
            ],
        )

    def test_close_reviewed_web_action_delegates_with_notes(self):
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"ok": true, "data": {"steps": []}}\n',
            stderr="",
        )

        with patch("ai_project_ctl.web.actions.subprocess.run", return_value=completed_process) as run:
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "task.close_reviewed",
                    "confirm": "yes",
                    "task": "WFA-05",
                    "notes": "Reviewed and accepted.",
                }
            )

        argv = run.call_args.args[0]

        self.assertTrue(result.ok)
        self.assertEqual(Path(argv[1]).name, "aictl.py")
        self.assertEqual(
            argv[-8:],
            [
                "workflow",
                "run",
                "task.close_reviewed",
                "--task",
                "WFA-05",
                "--notes",
                "Reviewed and accepted.",
                "--confirm",
            ],
        )
        self.assertIn("--notes", argv)

    def test_request_changes_web_action_delegates_with_notes(self):
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"ok": true, "data": {"steps": []}}\n',
            stderr="",
        )

        with patch("ai_project_ctl.web.actions.subprocess.run", return_value=completed_process) as run:
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "task.request_changes",
                    "confirm": "yes",
                    "task": "WFA-05",
                    "notes": "Needs rework.",
                }
            )

        argv = run.call_args.args[0]

        self.assertTrue(result.ok)
        self.assertEqual(Path(argv[1]).name, "aictl.py")
        self.assertEqual(
            argv[-8:],
            [
                "workflow",
                "run",
                "task.request_changes",
                "--task",
                "WFA-05",
                "--notes",
                "Needs rework.",
                "--confirm",
            ],
        )

    def test_request_changes_web_action_requires_notes(self):
        with self.assertRaises(WebActionError) as context:
            WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "task.request_changes",
                    "confirm": "yes",
                    "task": "WFA-05",
                }
            )

        self.assertEqual(context.exception.code, "WEB_MISSING_ACTION_ARGUMENT")
        self.assertEqual(context.exception.details["argument"], "notes")

    def test_accept_change_web_action_delegates_with_change_and_notes(self):
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"ok": true, "data": {"steps": []}}\n',
            stderr="",
        )

        with patch("ai_project_ctl.web.actions.subprocess.run", return_value=completed_process) as run:
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "evolution.accept_change",
                    "confirm": "yes",
                    "change": "CHG-018",
                    "notes": "Accepted after review.",
                }
            )

        argv = run.call_args.args[0]

        self.assertTrue(result.ok)
        self.assertEqual(Path(argv[1]).name, "aictl.py")
        self.assertIn("evolution.accept_change", argv)
        self.assertIn("--change", argv)
        self.assertIn("CHG-018", argv)
        self.assertIn("--notes", argv)

    def test_approve_change_web_action_delegates_with_change_and_notes(self):
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"ok": true, "data": {"steps": []}}\n',
            stderr="",
        )

        with patch("ai_project_ctl.web.actions.subprocess.run", return_value=completed_process) as run:
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "evolution.approve_change",
                    "confirm": "yes",
                    "change": "CHG-041",
                    "notes": "Approved by owner.",
                }
            )

        argv = run.call_args.args[0]

        self.assertTrue(result.ok)
        self.assertEqual(Path(argv[1]).name, "aictl.py")
        self.assertEqual(
            argv[-8:],
            [
                "workflow",
                "run",
                "evolution.approve_change",
                "--change",
                "CHG-041",
                "--notes",
                "Approved by owner.",
                "--confirm",
            ],
        )

    def test_move_change_to_review_web_action_delegates_with_change_target(self):
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"ok": true, "data": {"steps": []}}\n',
            stderr="",
        )

        with patch("ai_project_ctl.web.actions.subprocess.run", return_value=completed_process) as run:
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "evolution.move_to_review",
                    "confirm": "yes",
                    "change": "CHG-041",
                }
            )

        argv = run.call_args.args[0]

        self.assertTrue(result.ok)
        self.assertEqual(Path(argv[1]).name, "aictl.py")
        self.assertEqual(
            argv[-6:],
            [
                "workflow",
                "run",
                "evolution.move_to_review",
                "--change",
                "CHG-041",
                "--confirm",
            ],
        )

    def test_close_epic_web_action_delegates_with_epic_target(self):
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"ok": true, "data": {"steps": []}}\n',
            stderr="",
        )

        with patch("ai_project_ctl.web.actions.subprocess.run", return_value=completed_process) as run:
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "epic.close_if_complete",
                    "confirm": "yes",
                    "epic": "WFA",
                }
            )

        argv = run.call_args.args[0]

        self.assertTrue(result.ok)
        self.assertEqual(Path(argv[1]).name, "aictl.py")
        self.assertEqual(
            argv[-6:],
            [
                "workflow",
                "run",
                "epic.close_if_complete",
                "--epic",
                "WFA",
                "--confirm",
            ],
        )

    def test_health_route_is_json_read_only(self):
        status, content_type, body = route("/healthz", object())

        self.assertEqual(status.value, 200)
        self.assertEqual(content_type, "application/json; charset=utf-8")
        self.assertEqual(json.loads(body)["mode"], "controlled-writes")

    def test_non_loopback_host_is_rejected(self):
        from ai_project_ctl.web.server import _require_loopback_host

        with self.assertRaises(WebServerError):
            _require_loopback_host("0.0.0.0")


def completed(payload):
    return process(stdout=json.dumps(payload) + "\n")


def process(stdout="", stderr="", returncode=0):
    class Completed:
        pass

    item = Completed()
    item.returncode = returncode
    item.stdout = stdout
    item.stderr = stderr
    return item


def large_task_view_state():
    return {
        "initiatives": [
            {
                "id": "INIT-001",
                "title": "AI Development System Evolution",
                "status": "active",
                "order": 1,
            },
            {
                "id": "INIT-002",
                "title": "Centralized AI Project Control Plane",
                "status": "planned",
                "order": 2,
            },
        ],
        "epics": [
            {
                "id": "EPIC-001",
                "key": "DOC",
                "initiative_id": "INIT-001",
                "status": "active",
                "title": "Documentation Rails",
                "order": 1,
            },
            {
                "id": "EPIC-005",
                "key": "CTL",
                "initiative_id": "INIT-002",
                "status": "planned",
                "title": "Implement unified aictl",
                "order": 1,
            },
            {
                "id": "EPIC-006",
                "key": "WFA",
                "initiative_id": "INIT-002",
                "status": "planned",
                "title": "Control Plane Workflow Automation",
                "order": 2,
            },
        ],
        "tasks": [
            {
                "id": "TASK-001",
                "ref": "DOC-01",
                "legacy_id": "TASK-001",
                "status": "ready",
                "title": "DOC-01 Usage Guide",
                "summary": "Write the missing practical usage guide.",
                "epic_id": "EPIC-001",
                "epic_key": "DOC",
                "order": 1,
                "local_seq": 1,
            },
            {
                "id": "TASK-028",
                "ref": "CTL-10",
                "legacy_id": "TASK-028",
                "status": "done",
                "title": "CTL-10 Completed Control Task",
                "summary": "Add read-only local Web Control Center MVP.",
                "epic_id": "EPIC-005",
                "epic_key": "CTL",
                "order": 10,
                "local_seq": 10,
            },
            {
                "id": "TASK-037",
                "ref": "WFA-06",
                "legacy_id": "TASK-037",
                "status": "in_review",
                "title": "WFA-06 Documentation Audit",
                "summary": "Audit workflow automation documentation.",
                "epic_id": "EPIC-006",
                "epic_key": "WFA",
                "order": 6,
                "local_seq": 6,
            },
            {
                "id": "TASK-038",
                "ref": "WFA-07",
                "legacy_id": "TASK-038",
                "aliases": ["TASK-038"],
                "status": "in_progress",
                "title": "UIX-01 Improve Tasks filtering grouping and collapse",
                "summary": "Make the Tasks page usable for large projects.",
                "epic_id": "EPIC-006",
                "epic_key": "WFA",
                "order": 7,
                "local_seq": 7,
            },
        ],
        "current_task_id": "TASK-038",
    }


def write_web_state(
    root,
    *,
    tasks=None,
    current_task_id=None,
    epics=None,
    initiatives=None,
    changes=None,
    execution=None,
    task_reports=None,
):
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "tasks.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "current_task_id": current_task_id,
                "tasks": tasks or [],
            }
        ),
        encoding="utf-8",
    )
    if execution is not None:
        (state_dir / "current_execution.json").write_text(
            json.dumps(execution),
            encoding="utf-8",
        )
    (state_dir / "evolution.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "changes": changes or [],
            }
        ),
        encoding="utf-8",
    )
    (state_dir / "plan.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "initiatives": initiatives or [],
                "epics": epics or [],
            }
        ),
        encoding="utf-8",
    )
    if task_reports is not None:
        (state_dir / "task_reports.json").write_text(
            json.dumps(task_reports),
            encoding="utf-8",
        )


def multipart_body(fields, files):
    boundary = "ai-project-test-boundary"
    chunks = []
    for name, value in fields.items():
        chunks.extend(
            [
                "--{}\r\n".format(boundary).encode("utf-8"),
                'Content-Disposition: form-data; name="{}"\r\n\r\n'.format(
                    name
                ).encode("utf-8"),
                str(value).encode("utf-8"),
                b"\r\n",
            ]
        )
    for name, (filename, content_type, content) in files.items():
        payload = (
            content if isinstance(content, bytes) else str(content).encode("utf-8")
        )
        chunks.extend(
            [
                "--{}\r\n".format(boundary).encode("utf-8"),
                (
                    'Content-Disposition: form-data; name="{}"; filename="{}"\r\n'
                ).format(name, filename).encode("utf-8"),
                "Content-Type: {}\r\n\r\n".format(content_type).encode("utf-8"),
                payload,
                b"\r\n",
            ]
        )
    chunks.append("--{}--\r\n".format(boundary).encode("utf-8"))
    return boundary, b"".join(chunks)


def run_ctl(root, script, *args):
    completed = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "scripts" / script),
            "--root",
            str(root),
            "--actor",
            "tester",
            *args,
        ],
        cwd=str(Path(__file__).resolve().parents[1]),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise AssertionError(
            "{} failed:\nSTDOUT:\n{}\nSTDERR:\n{}".format(
                script,
                completed.stdout,
                completed.stderr,
            )
        )
    return completed


def run_ctl_raw(root, script, *args):
    return subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "scripts" / script),
            "--root",
            str(root),
            "--actor",
            "tester",
            *args,
        ],
        cwd=str(Path(__file__).resolve().parents[1]),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def init_basic_task_project(root):
    run_ctl(root, "planctl.py", "init")
    run_ctl(root, "planctl.py", "initiative", "create", "--title", "Control")
    run_ctl(root, "planctl.py", "epic", "create", "--initiative", "INIT-001", "--title", "Tasks")
    run_ctl(root, "taskctl.py", "init")
    run_ctl(
        root,
        "taskctl.py",
        "task",
        "create",
        "--epic",
        "EPIC-001",
        "--title",
        "Report task",
        "--status",
        "in_progress",
        "--scope",
        "Submit report",
        "--allowed-file",
        "scripts/taskctl.py",
        "--acceptance",
        "Report state exists",
    )


def write_execution_report(path, *, task_id="TASK-001"):
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "task_id": task_id,
                "implementation_summary": "Implemented structured report submission.",
                "changed_files": ["scripts/taskctl.py"],
                "generated_files": [],
                "checks": [
                    {
                        "name": "unit",
                        "command": "python -m unittest",
                        "result": "pass",
                        "duration_sec": 1.0,
                        "blocking": True,
                        "details": "Selected tests passed.",
                    }
                ],
                "warnings": [],
                "blockers": [],
                "notes": ["Submitted through CLI."],
                "owner_decision_required": True,
            }
        ),
        encoding="utf-8",
    )
    return path


def review_report_state(*, task_id, task_ref, summary):
    return {
        "schema_version": 1,
        "revision": 1,
        "created_at": "2026-06-19T12:00:00Z",
        "updated_at": "2026-06-19T12:00:00Z",
        "latest_by_task": {task_id: "RPT-001"},
        "reports": [
            {
                "id": "RPT-001",
                "task_id": task_id,
                "task_ref": task_ref,
                "submitted_at": "2026-06-19T12:00:00Z",
                "submitted_by": "codex",
                "source_file": "/tmp/report.json",
                "report": {
                    "task_id": task_id,
                    "task_ref": task_ref,
                    "implementation_summary": summary,
                    "changed_files": ["ai_project_ctl/web/server.py"],
                    "generated_files": ["AI_PROJECT/generated/CODEX_PROMPT.md"],
                    "checks": [
                        {
                            "name": "unit",
                            "command": "python -m unittest",
                            "result": "pass",
                            "duration_sec": 1.0,
                            "blocking": True,
                        },
                        {
                            "name": "docs",
                            "details": "Documentation warning.",
                            "result": "warn",
                            "blocking": False,
                        },
                    ],
                    "warnings": ["Review warning."],
                    "blockers": ["Manual blocker."],
                    "notes": ["Ready for owner decision."],
                    "owner_decision_required": True,
                },
            }
        ],
    }


if __name__ == "__main__":
    unittest.main()

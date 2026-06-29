import json
import re
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from dataclasses import replace
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from ai_project_ctl.core.registry import command_describe
from ai_project_ctl.core.result import CommandResult
from ai_project_ctl.core.validation import ValidationError
from ai_project_ctl.pipeline.git_status import GitStatusEntry, WorktreeDirtyPreflight
from ai_project_ctl.pipeline.policy import policy_preset
from ai_project_ctl.pipeline.policy_store import (
    pipeline_policy_store_path,
    save_policy_preset,
)
from ai_project_ctl.ui_settings import (
    ALLOW_REPORT_WARNINGS_SETTING,
    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
    ALLOW_RELAXED_REPORT_WARNINGS_SETTING,
    BATCH_MAX_FAILURES_SETTING,
    BATCH_MAX_STEPS_SETTING,
    INTERNAL_CHANGE_GATE_BYPASS_SETTING,
    REQUIRE_CODEX_REVIEW_SETTING,
    ui_settings_path,
)
from ai_project_ctl.web.actions import (
    WebActionError,
    WebActionExecutor,
    available_actions,
)
from ai_project_ctl.web.read_model import (
    PIPELINE_RUNTIME_LOG_TAIL_MAX_BYTES,
    ReadOnlyProjectModel,
    WebControlError,
    require_read_only_command,
)
from ai_project_ctl.web.server import (
    PIPELINE_LOG_SNIPPET_LIMIT,
    WEB_IMPORT_FILE_MAX_BYTES,
    WebServerError,
    filter_tasks,
    make_handler,
    render_action_error,
    render_action_result,
    route,
    task_action_metric_counts,
    task_action_queue_groups,
    task_filter_state,
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

    def test_owner_cockpit_shell_renders_core_routes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-230",
                        "ref": "CTL-30",
                        "legacy_id": "TASK-230",
                        "status": "in_progress",
                        "title": "Owner UI regression tests",
                        "epic_id": "EPIC-005",
                        "epic_key": "CTL",
                    },
                    {
                        "id": "TASK-231",
                        "ref": "CTL-31",
                        "legacy_id": "TASK-231",
                        "status": "ready",
                        "title": "Ready cockpit follow-up",
                        "epic_id": "EPIC-005",
                        "epic_key": "CTL",
                    },
                    {
                        "id": "TASK-232",
                        "ref": "CTL-32",
                        "legacy_id": "TASK-232",
                        "status": "in_review",
                        "title": "Reviewed cockpit follow-up",
                        "epic_id": "EPIC-005",
                        "epic_key": "CTL",
                    },
                ],
                current_task_id="TASK-230",
                epics=[{"id": "EPIC-005", "key": "CTL", "status": "active"}],
                changes=[
                    {
                        "id": "CHG-230",
                        "status": "ready",
                        "type": "tooling",
                        "title": "Owner cockpit route safety",
                    }
                ],
            )

            routes = {
                "/": "Owner Cockpit",
                "/tasks": "Tasks",
                "/pipeline": "Pipeline",
                "/reviews": "Reviews",
                "/evolution": "Evolution",
                "/settings": "Settings",
                "/doctor": "Doctor",
            }
            for path, title in routes.items():
                with self.subTest(path=path):
                    status, content_type, body = route(
                        path,
                        ReadOnlyProjectModel(root, actor="tester"),
                    )

                self.assertEqual(status.value, 200)
                self.assertEqual(content_type, "text/html; charset=utf-8")
                self.assertIn('<div class="app-shell">', body)
                self.assertIn(
                    '<aside class="sidebar" aria-label="Web Control Center navigation">',
                    body,
                )
                self.assertIn('<main class="main-content">', body)
                self.assertIn('<a class="brand" href="/">AI Control Center</a>', body)
                self.assertIn("<h1>{}</h1>".format(title), body)
                self.assertIn(
                    'href="{}" class="active">{}</a>'.format(path, title),
                    body,
                )
                for nav_label in (
                    "Owner Cockpit",
                    "Tasks",
                    "Pipeline",
                    "Reviews",
                    "Evolution",
                    "Doctor",
                    "Settings",
                ):
                    self.assertIn(">{}</a>".format(nav_label), body)
                assert_no_restricted_git_actions(self, body)

    def test_dashboard_renders_compact_health_current_execution_and_safe_actions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prompt_path = root / "AI_PROJECT/generated/CODEX_PROMPT.md"
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-230",
                        "ref": "CTL-30",
                        "legacy_id": "TASK-230",
                        "status": "in_progress",
                        "title": "Owner UI regression tests",
                        "epic_id": "EPIC-005",
                        "epic_key": "CTL",
                    }
                ],
                current_task_id="TASK-230",
                epics=[{"id": "EPIC-005", "key": "CTL", "status": "active"}],
                execution={
                    "status": "READY",
                    "code": "CODEX_READY",
                    "updated_at": "2026-06-27T17:21:09Z",
                    "prompt_exists": True,
                    "prompt_path": str(prompt_path),
                    "source_type": "task",
                    "source_id": "TASK-230",
                    "source_status": "in_progress",
                    "context_pack": {
                        "path": "AI_PROJECT/generated/CONTEXT_PACK.md",
                        "task_id": "TASK-230",
                        "tasks_revision": 1,
                        "docs_revision": 28,
                    },
                },
            )

            status, _, body = route("/", ReadOnlyProjectModel(root, actor="tester"))

        self.assertEqual(status.value, 200)
        self.assertIn('class="current-execution-bar"', body)
        self.assertIn("Current Execution", body)
        self.assertIn("CTL-30", body)
        self.assertIn("CODEX_READY", body)
        self.assertIn("tasks rev 1, docs rev 28", body)
        self.assertIn(
            'class="panel health-panel health-panel-compact" id="owner-health"',
            body,
        )
        self.assertIn('class="health-summary-counts"', body)
        self.assertIn("Project Doctor", body)
        self.assertIn('class="panel owner-queue-section owner-queue-current"', body)

        action_forms = [
            form
            for form in post_forms(body)
            if 'name="action" value="' in form
        ]
        self.assertGreater(len(action_forms), 0)
        for form in action_forms:
            self.assertIn('action="/actions"', form)

        current_clear_forms = [
            form
            for form in action_forms
            if 'name="action" value="current.clear"' in form
        ]
        self.assertGreater(len(current_clear_forms), 0)
        for form in current_clear_forms:
            self.assertIn('data-confirm-modal="action"', form)
            self.assertIn('name="confirm" value="yes" required', form)

    def test_task_action_queue_groups_follow_available_owner_actions(self):
        def queue_task(ref, status, *, label="", action="", title=""):
            task = {
                "id": "TASK-{}".format(ref),
                "ref": ref,
                "status": status,
                "title": title or ref,
            }
            if label or action:
                task["pipeline_hints"] = {
                    "next_actions": [label] if label else [],
                    "actions": [
                        {
                            "label": label,
                            "action": action,
                            "available": True,
                            "reason": "",
                        }
                    ],
                }
            return task

        tasks = [
            queue_task(
                "PREP-01",
                "planned",
                label="Prepare for Codex",
                action="task.prepare_for_codex",
            ),
            queue_task(
                "RUN-01",
                "planned",
                label="Run",
                action="ui.run_selected_task",
            ),
            queue_task(
                "DECIDE-01",
                "ready",
                label="Approve Change",
                action="evolution.approve_change",
            ),
            queue_task(
                "REVIEW-01",
                "ready",
                label="Request Changes",
                action="task.request_changes",
            ),
            queue_task(
                "CUR-01",
                "ready",
                label="Prepare for Codex",
                action="task.prepare_for_codex",
            ),
            queue_task("PROG-01", "in_progress"),
            queue_task(
                "BLOCK-01",
                "blocked",
                label="Run",
                action="ui.run_selected_task",
            ),
            queue_task("DEFER-01", "deferred"),
        ]
        data = {
            "tasks": tasks,
            "epics": [],
            "current_task": {"id": "TASK-CUR-01", "ref": "CUR-01"},
        }

        default_filters = task_filter_state(data, {})
        visible_tasks = filter_tasks(tasks, data, default_filters)
        groups = task_action_queue_groups(visible_tasks, data)
        refs_by_group = {
            key: {str(task.get("ref") or "") for task in grouped}
            for key, grouped in groups.items()
        }

        self.assertEqual(refs_by_group["ready_to_run"], {"PREP-01", "RUN-01"})
        self.assertEqual(refs_by_group["needs_decision"], {"DECIDE-01", "REVIEW-01"})
        self.assertEqual(refs_by_group["current"], {"CUR-01", "PROG-01"})
        self.assertEqual(refs_by_group["blocked"], {"BLOCK-01"})
        self.assertNotIn("DEFER-01", set().union(*refs_by_group.values()))

        deferred_filters = task_filter_state(data, {"status": ["deferred"]})
        deferred_tasks = filter_tasks(tasks, data, deferred_filters)

        self.assertEqual([task["ref"] for task in deferred_tasks], ["DEFER-01"])

    def test_tasks_page_default_metrics_show_owner_action_counts(self):
        tasks = [
            {
                "id": "TASK-RUN",
                "ref": "RUN-01",
                "legacy_id": "TASK-RUN",
                "status": "ready",
                "title": "Runnable task",
                "epic_id": "EPIC-001",
            },
            {
                "id": "TASK-CURRENT",
                "ref": "CUR-01",
                "legacy_id": "TASK-CURRENT",
                "status": "ready",
                "title": "Current task",
                "epic_id": "EPIC-001",
            },
            {
                "id": "TASK-PROGRESS",
                "ref": "PROG-01",
                "legacy_id": "TASK-PROGRESS",
                "status": "in_progress",
                "title": "In-progress task",
                "epic_id": "EPIC-001",
            },
            {
                "id": "TASK-REVIEW",
                "ref": "REV-01",
                "legacy_id": "TASK-REVIEW",
                "status": "in_review",
                "title": "Review decision task",
                "epic_id": "EPIC-001",
            },
            {
                "id": "TASK-BLOCKED",
                "ref": "BLOCK-01",
                "legacy_id": "TASK-BLOCKED",
                "status": "blocked",
                "title": "Blocked task",
                "epic_id": "EPIC-001",
            },
            {
                "id": "TASK-DONE",
                "ref": "DONE-01",
                "legacy_id": "TASK-DONE",
                "status": "done",
                "title": "Done inventory task",
                "epic_id": "EPIC-001",
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=tasks,
                current_task_id="TASK-CURRENT",
                epics=[{"id": "EPIC-001", "status": "active"}],
            )
            model = ReadOnlyProjectModel(root, actor="tester")
            data = model.dashboard(include_events=True)
            status, _, body = route("/tasks", model)
            inventory_status, _, inventory_body = route(
                "/tasks?view=inventory&show_done=1",
                model,
            )

        filters = task_filter_state(data, {})
        visible_tasks = filter_tasks(data["tasks"], data, filters)
        groups = task_action_queue_groups(visible_tasks, data)
        expected = task_action_metric_counts(visible_tasks, data)
        metrics = summary_grid_metrics(body)
        inventory_metrics = summary_grid_metrics(inventory_body)

        self.assertEqual(status.value, 200)
        self.assertEqual(inventory_status.value, 200)
        self.assertEqual(metrics["Needs Decision"], str(len(groups["needs_decision"])))
        self.assertEqual(metrics["Ready To Run"], str(len(groups["ready_to_run"])))
        self.assertEqual(metrics["Current"], str(len(groups["current"])))
        self.assertEqual(metrics["Blocked"], str(len(groups["blocked"])))
        self.assertEqual(metrics["Health Issues"], str(expected["health_issues"]))
        self.assertNotIn("done", metrics)
        self.assertNotIn("Visible", metrics)
        self.assertIn("done", inventory_metrics)
        self.assertIn("Visible", inventory_metrics)

    def test_tasks_page_action_metrics_remain_usable_without_current_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-READY",
                        "ref": "READY-01",
                        "legacy_id": "TASK-READY",
                        "status": "ready",
                        "title": "Ready without current",
                        "epic_id": "EPIC-001",
                    }
                ],
                current_task_id=None,
                epics=[{"id": "EPIC-001", "status": "active"}],
            )
            status, _, body = route(
                "/tasks",
                ReadOnlyProjectModel(root, actor="tester"),
            )

        metrics = summary_grid_metrics(body)

        self.assertEqual(status.value, 200)
        self.assertEqual(metrics["Current"], "0")
        self.assertEqual(metrics["Ready To Run"], "1")
        self.assertIn("Health Issues", metrics)

    def test_tasks_ready_to_run_rows_show_run_prepare_and_details(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-RUN",
                        "ref": "RUN-01",
                        "legacy_id": "TASK-RUN",
                        "status": "ready",
                        "title": "Ready runnable task",
                        "epic_id": "EPIC-001",
                    },
                    {
                        "id": "TASK-BLOCK",
                        "ref": "BLOCK-01",
                        "legacy_id": "TASK-BLOCK",
                        "status": "blocked",
                        "title": "Blocked task",
                        "epic_id": "EPIC-001",
                    },
                ],
                epics=[{"id": "EPIC-001", "status": "active"}],
            )
            status, _, body = route(
                "/tasks",
                ReadOnlyProjectModel(root, actor="tester"),
            )

        rows = re.findall(r"<tr>.*?</tr>", body, flags=re.DOTALL)
        ready_row = next(row for row in rows if "RUN-01" in row)
        blocked_row = next(row for row in rows if "BLOCK-01" in row)

        self.assertEqual(status.value, 200)
        self.assertIn("Ready To Run", body)
        self.assertIn('data-confirm-effective-policy-summary="', body)
        self.assertIn("batch.max_steps:", body)
        self.assertIn("submitInProgress", body)
        self.assertIn('value="ui.run_selected_task"', ready_row)
        self.assertIn('name="task" value="TASK-RUN"', ready_row)
        self.assertIn('data-confirm-modal="action"', ready_row)
        self.assertIn('data-submit-once="action"', ready_row)
        self.assertIn('<button type="submit">Run</button>', ready_row)
        self.assertIn('value="task.prepare_for_codex"', ready_row)
        self.assertIn('<button type="submit">Prepare</button>', ready_row)
        self.assertIn("Details", ready_row)
        self.assertIn("Open Details", blocked_row)
        self.assertNotIn('value="ui.run_selected_task"', blocked_row)
        self.assertNotIn('<button type="submit">Run</button>', blocked_row)

    def test_current_execution_bar_shows_run_current_for_current_ready_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-CURRENT",
                        "ref": "CUR-01",
                        "legacy_id": "TASK-CURRENT",
                        "status": "ready",
                        "title": "Current runnable task",
                        "epic_id": "EPIC-001",
                    }
                ],
                current_task_id="TASK-CURRENT",
                epics=[{"id": "EPIC-001", "status": "active"}],
            )
            status, _, body = route(
                "/tasks",
                ReadOnlyProjectModel(root, actor="tester"),
            )

        current_bar = re.search(
            r'<section class="current-execution-bar".*?</section>',
            body,
            flags=re.DOTALL,
        )
        current_html = current_bar.group(0) if current_bar else ""

        self.assertEqual(status.value, 200)
        self.assertIn("Run Current", current_html)
        self.assertIn('value="ui.run_selected_task"', current_html)
        self.assertIn('name="task" value="TASK-CURRENT"', current_html)
        self.assertIn('data-confirm-modal="action"', current_html)

    def test_settings_page_renders_default_ui_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root)
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/settings", model)

        self.assertEqual(status.value, 200)
        self.assertIn('href="/settings" class="active">Settings</a>', body)
        self.assertIn("defaults", body)
        self.assertIn(str(ui_settings_path(root)), body)
        self.assertEqual(body.count('class="panel settings-panel"'), 1)
        self.assertEqual(body.count('method="post" action="/actions"'), 1)
        self.assertEqual(body.count('<button type="submit">Apply Settings</button>'), 1)
        self.assertIn("Pipeline", body)
        self.assertIn("Batch Run", body)
        self.assertIn("Review Gates", body)
        self.assertIn("Timeouts", body)
        self.assertIn("Advanced", body)
        self.assertIn("Effective Policy Summary", body)
        self.assertIn("<dt>Policy</dt><dd>supervised_executable_local_commit</dd>", body)
        self.assertIn("<dt>batch.max_steps</dt><dd>5</dd>", body)
        self.assertIn("<dt>batch.max_failures</dt><dd>1</dd>", body)
        self.assertIn("<dt>Codex Review</dt><dd>required (approve)</dd>", body)
        self.assertIn("<dt>Auto-close</dt><dd>enabled (note required)</dd>", body)
        self.assertIn("<dt>Local Commit</dt><dd>enabled (local_only)</dd>", body)
        self.assertIn("<dt>Report Warnings</dt><dd>strict (blocking)</dd>", body)
        self.assertIn("<dt>Git Diff Gates</dt><dd>strict (required)</dd>", body)
        self.assertIn("Incomplete Web Run", body)
        self.assertIn("review and close may not run in one batch", body)
        self.assertIn("Resume Session can continue the next phase", body)
        self.assertIn("<code>command_line</code>", body)
        self.assertIn('name="command_line" value="codex exec"', body)
        self.assertIn("<code>default_policy</code>", body)
        self.assertIn('<select name="default_policy">', body)
        for policy_name in (
            "dry_run",
            "supervised",
            "supervised_executable",
            "supervised_autoclose",
            "supervised_executable_autoclose",
            "supervised_local_commit",
            "supervised_executable_local_commit",
        ):
            self.assertIn('<option value="{}"'.format(policy_name), body)
        self.assertIn(
            '<option value="supervised_executable_local_commit" selected>',
            body,
        )
        self.assertNotIn('<input type="text" name="default_policy"', body)
        self.assertIn("<code>batch_max_steps</code>", body)
        self.assertIn(
            "Optional Web-run override for policy batch.max_steps.",
            body,
        )
        self.assertIn('name="batch_max_steps" value=""', body)
        self.assertIn("<code>batch_max_failures</code>", body)
        self.assertIn(
            "Optional Web-run override for policy batch.max_failures.",
            body,
        )
        self.assertIn('name="batch_max_failures" value=""', body)
        self.assertIn("Machine Review", body)
        self.assertIn("<code>machine_review</code>", body)
        self.assertIn('<input type="checkbox" checked disabled>Locked ON', body)
        self.assertIn("Require Codex Review before close", body)
        self.assertIn("Disable to skip semantic LLM review and save tokens.", body)
        self.assertIn(
            'type="hidden" name="require_codex_review" value="false"',
            body,
        )
        self.assertIn(
            'type="checkbox" name="require_codex_review" value="true" checked>'
            "Require Codex Review before close",
            body,
        )
        self.assertIn("<code>allow_relaxed_git_diff_verification</code>", body)
        self.assertIn(
            "Strict git diff verification remains the default",
            body,
        )
        self.assertIn(
            'type="hidden" name="allow_relaxed_git_diff_verification" value="false"',
            body,
        )
        self.assertIn(
            'type="checkbox" name="allow_relaxed_git_diff_verification" value="true">'
            "Allow relaxed git diff verification for UI runs",
            body,
        )
        self.assertNotIn(
            'type="checkbox" name="allow_relaxed_git_diff_verification" value="true" checked>'
            "Allow relaxed git diff verification for UI runs",
            body,
        )
        self.assertIn("<code>allow_report_warnings</code>", body)
        self.assertIn(
            "Report warnings may pass verification",
            body,
        )
        self.assertIn(
            'type="hidden" name="allow_report_warnings" value="false"',
            body,
        )
        self.assertIn(
            'type="checkbox" name="allow_report_warnings" value="true">'
            "Allow report-warning pass behavior for UI runs",
            body,
        )
        self.assertNotIn(
            'type="checkbox" name="allow_report_warnings" value="true" checked>'
            "Allow report-warning pass behavior for UI runs",
            body,
        )
        self.assertIn("<code>allow_relaxed_report_warnings</code>", body)
        self.assertIn(
            "Fast UI runs only. Report warnings become advisory",
            body,
        )
        self.assertIn(
            'type="hidden" name="allow_relaxed_report_warnings" value="false"',
            body,
        )
        self.assertIn(
            'type="checkbox" name="allow_relaxed_report_warnings" value="true">'
            "Allow relaxed report warnings for fast UI runs",
            body,
        )
        self.assertNotIn(
            'type="checkbox" name="allow_relaxed_report_warnings" value="true" checked>'
            "Allow relaxed report warnings for fast UI runs",
            body,
        )
        self.assertIn("<code>allow_internal_change_gate_bypass</code>", body)
        self.assertIn(
            "Internal project-control tasks only. Does not approve Changes",
            body,
        )
        self.assertIn(
            'type="hidden" name="allow_internal_change_gate_bypass" value="false"',
            body,
        )
        self.assertIn(
            'type="checkbox" name="allow_internal_change_gate_bypass" value="true">'
            "Allow internal Change gate bypass",
            body,
        )
        self.assertNotIn(
            'type="checkbox" name="allow_internal_change_gate_bypass" value="true" checked>'
            "Allow internal Change gate bypass",
            body,
        )
        self.assertIn('value="ui.settings.apply"', body)
        self.assertIn('href="/settings">Reset</a>', body)
        self.assertIn('name="confirm" value="yes" required', body)
        self.assertNotIn('name="change_gate"', body)
        self.assertNotIn('name="bypass"', body)
        self.assertNotIn("Effective UI Settings", body)
        self.assertNotIn("Internal Change Gate Bypass", body)
        self.assertNotIn("Update UI Setting", body)
        self.assertNotIn('value="ui.settings.set"', body)
        self.assertNotIn('<select name="key"', body)
        self.assertNotIn('value="ui.settings.init"', body)

    def test_settings_page_renders_project_file_ui_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root)
            path = write_ui_settings(
                root,
                {
                    "command_line": "codex exec --json",
                    "default_policy": "supervised",
                    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING: "true",
                    ALLOW_REPORT_WARNINGS_SETTING: "true",
                    ALLOW_RELAXED_REPORT_WARNINGS_SETTING: "true",
                    INTERNAL_CHANGE_GATE_BYPASS_SETTING: "true",
                    BATCH_MAX_STEPS_SETTING: "9",
                    BATCH_MAX_FAILURES_SETTING: 2,
                    "execution_timeout_sec": "1800",
                    "preflight_timeout_sec": 45,
                },
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/settings", model)

        self.assertEqual(status.value, 200)
        self.assertIn("project_file", body)
        self.assertIn(str(path), body)
        self.assertEqual(body.count('class="panel settings-panel"'), 1)
        self.assertEqual(body.count('<button type="submit">Apply Settings</button>'), 1)
        self.assertIn("Pipeline", body)
        self.assertIn("Batch Run", body)
        self.assertIn("Review Gates", body)
        self.assertIn("Timeouts", body)
        self.assertIn("Advanced", body)
        self.assertIn("<code>command_line</code>", body)
        self.assertIn('name="command_line" value="codex exec --json"', body)
        self.assertIn("<code>default_policy</code>", body)
        self.assertIn('<select name="default_policy">', body)
        self.assertIn('<option value="supervised" selected>', body)
        self.assertNotIn('<input type="text" name="default_policy"', body)
        self.assertIn("<dt>batch.max_steps</dt><dd>9</dd>", body)
        self.assertIn("<dt>batch.max_failures</dt><dd>2</dd>", body)
        self.assertIn("<code>batch_max_steps</code>", body)
        self.assertIn('name="batch_max_steps" value="9"', body)
        self.assertIn("<code>batch_max_failures</code>", body)
        self.assertIn('name="batch_max_failures" value="2"', body)
        self.assertIn("Machine Review", body)
        self.assertIn('<input type="checkbox" checked disabled>Locked ON', body)
        self.assertIn(
            'type="checkbox" name="require_codex_review" value="true" checked>'
            "Require Codex Review before close",
            body,
        )
        self.assertIn("<code>allow_relaxed_git_diff_verification</code>", body)
        self.assertIn(
            'type="checkbox" name="allow_relaxed_git_diff_verification" value="true" checked>'
            "Allow relaxed git diff verification for UI runs",
            body,
        )
        self.assertIn("<code>allow_report_warnings</code>", body)
        self.assertIn(
            'type="checkbox" name="allow_report_warnings" value="true" checked>'
            "Allow report-warning pass behavior for UI runs",
            body,
        )
        self.assertIn("<code>allow_relaxed_report_warnings</code>", body)
        self.assertIn(
            "Report warnings become advisory",
            body,
        )
        self.assertIn(
            'type="checkbox" name="allow_relaxed_report_warnings" value="true" checked>'
            "Allow relaxed report warnings for fast UI runs",
            body,
        )
        self.assertIn("<code>allow_internal_change_gate_bypass</code>", body)
        self.assertIn(
            "Internal project-control tasks only. Does not approve Changes",
            body,
        )
        self.assertIn(
            'type="hidden" name="allow_internal_change_gate_bypass" value="false"',
            body,
        )
        self.assertIn(
            'type="checkbox" name="allow_internal_change_gate_bypass" value="true" checked>'
            "Allow internal Change gate bypass",
            body,
        )
        self.assertIn("<code>execution_timeout_sec</code>", body)
        self.assertIn('name="execution_timeout_sec" value="1800"', body)
        self.assertIn("<code>preflight_timeout_sec</code>", body)
        self.assertIn('name="preflight_timeout_sec" value="45"', body)
        self.assertIn('value="ui.settings.apply"', body)
        self.assertNotIn("Effective UI Settings", body)
        self.assertNotIn("Internal Change Gate Bypass", body)
        self.assertNotIn("Update UI Setting", body)
        self.assertNotIn('value="ui.settings.set"', body)
        self.assertNotIn('<option value="execution_timeout_sec">execution_timeout_sec</option>', body)
        self.assertNotIn('<option value="preflight_timeout_sec">preflight_timeout_sec</option>', body)
        self.assertNotIn('value="ui.settings.init"', body)
        self.assertNotIn('name="change_gate"', body)
        self.assertNotIn('name="bypass"', body)

    def test_settings_page_policy_dropdown_includes_custom_presets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root)
            write_ui_settings(root, {"default_policy": "owner_supervised"})
            base = policy_preset("supervised")
            custom = replace(
                base,
                name="owner_supervised",
                batch=replace(base.batch, max_steps=9, max_failures=2),
            )
            result = save_policy_preset(
                "owner_supervised",
                custom,
                root=root,
                actor="tester",
            )
            self.assertTrue(result.ok)
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/settings", model)

        self.assertEqual(status.value, 200)
        self.assertIn('<select name="default_policy">', body)
        self.assertIn('<option value="owner_supervised" selected>', body)
        self.assertIn("<dt>Policy</dt><dd>owner_supervised</dd>", body)
        self.assertIn("<dt>batch.max_steps</dt><dd>9</dd>", body)
        self.assertIn("<dt>batch.max_failures</dt><dd>2</dd>", body)
        self.assertNotIn('<input type="text" name="default_policy"', body)

    def test_settings_read_model_returns_effective_allow_report_warnings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root)
            write_ui_settings(root, {ALLOW_REPORT_WARNINGS_SETTING: "true"})

            data = ReadOnlyProjectModel(root, actor="tester").ui_settings()

        self.assertIs(data["settings"][ALLOW_REPORT_WARNINGS_SETTING], True)
        self.assertIs(
            data["settings"][ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING],
            False,
        )
        self.assertEqual(data["source"], "project_file")

    def test_settings_effective_policy_summary_applies_ui_overrides(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root)
            write_ui_settings(
                root,
                {
                    "default_policy": "supervised",
                    REQUIRE_CODEX_REVIEW_SETTING: "false",
                    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING: "true",
                    ALLOW_REPORT_WARNINGS_SETTING: "true",
                    ALLOW_RELAXED_REPORT_WARNINGS_SETTING: "true",
                    BATCH_MAX_STEPS_SETTING: "8",
                    BATCH_MAX_FAILURES_SETTING: "3",
                },
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            data = model.ui_settings()
            status, _, body = route("/settings", model)

        self.assertEqual(status.value, 200)
        summary = data["policy_catalog"]["effective_policy"]
        self.assertEqual(summary["name"], "supervised")
        self.assertEqual(summary["batch"], {"max_steps": 8, "max_failures": 3})
        self.assertEqual(
            summary["review"],
            {
                "machine_review_required": True,
                "machine_review_outcome": "pass",
                "codex_review_required": False,
                "codex_review_decision": "none",
            },
        )
        self.assertEqual(
            summary["verify"],
            {
                "run_git_diff_gates": False,
                "block_report_warnings": False,
                "allow_report_warnings": True,
            },
        )
        selected = next(
            policy
            for policy in data["policy_catalog"]["policies"]
            if policy["selected"]
        )
        self.assertEqual(selected["effective_summary"], summary)
        self.assertIn("<dt>Policy</dt><dd>supervised</dd>", body)
        self.assertIn("<dt>batch.max_steps</dt><dd>8</dd>", body)
        self.assertIn("<dt>batch.max_failures</dt><dd>3</dd>", body)
        self.assertIn("<dt>Codex Review</dt><dd>skipped</dd>", body)
        self.assertIn(
            "<dt>Report Warnings</dt><dd>relaxed (allowed / advisory)</dd>",
            body,
        )
        self.assertIn("<dt>Git Diff Gates</dt><dd>relaxed (not run)</dd>", body)
        self.assertNotIn("Incomplete Web Run", body)

    def test_settings_read_model_exposes_builtin_policy_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root)

            data = ReadOnlyProjectModel(root, actor="tester").ui_settings()

        catalog = data["policy_catalog"]
        policies = catalog["policies"]
        names = [policy["name"] for policy in policies]
        self.assertEqual(
            names,
            [
                "dry_run",
                "supervised",
                "supervised_executable",
                "supervised_autoclose",
                "supervised_executable_autoclose",
                "supervised_local_commit",
                "supervised_executable_local_commit",
            ],
        )
        self.assertEqual(
            catalog["counts"],
            {"built_in": 7, "custom": 0, "total": 7},
        )
        self.assertEqual(
            catalog["selected_policy"],
            "supervised_executable_local_commit",
        )
        self.assertTrue(catalog["selected_known"])

        selected = next(policy for policy in policies if policy["selected"])
        self.assertEqual(selected["kind"], "built_in")
        self.assertEqual(
            selected["behavior_label"],
            "executable / auto-close needs note / local-commit",
        )
        summary = selected["effective_summary"]
        self.assertEqual(
            summary["review"],
            {
                "machine_review_required": True,
                "machine_review_outcome": "pass",
                "codex_review_required": True,
                "codex_review_decision": "approve",
            },
        )
        self.assertEqual(
            summary["close"],
            {
                "auto_close_task": True,
                "owner_approval_note_present": False,
            },
        )
        self.assertEqual(
            summary["commit"],
            {
                "create_local_commit": True,
                "mode": "local_only",
                "require_commit_readiness": True,
                "allow_push": False,
                "allow_merge": False,
            },
        )
        self.assertEqual(summary["batch"], {"max_steps": 5, "max_failures": 1})
        self.assertEqual(
            summary["verify"],
            {
                "run_git_diff_gates": True,
                "block_report_warnings": True,
                "allow_report_warnings": False,
            },
        )
        self.assertEqual(catalog["effective_policy"], summary)

    def test_settings_read_model_policy_catalog_includes_custom_presets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root)
            write_ui_settings(root, {"default_policy": "owner_supervised"})
            base = policy_preset("supervised")
            custom = replace(
                base,
                name="owner_supervised",
                batch=replace(base.batch, max_steps=9, max_failures=2),
            )
            result = save_policy_preset(
                "owner_supervised",
                custom,
                root=root,
                actor="tester",
            )
            self.assertTrue(result.ok)

            data = ReadOnlyProjectModel(root, actor="tester").ui_settings()

        catalog = data["policy_catalog"]
        self.assertEqual(catalog["counts"], {"built_in": 7, "custom": 1, "total": 8})
        self.assertEqual(catalog["policies"][-1]["name"], "owner_supervised")
        custom_item = catalog["policies"][-1]
        self.assertEqual(custom_item["kind"], "custom")
        self.assertEqual(custom_item["behavior_label"], "prompt-only")
        self.assertTrue(custom_item["selected"])
        self.assertEqual(
            custom_item["effective_summary"]["batch"],
            {"max_steps": 9, "max_failures": 2},
        )
        self.assertEqual(
            custom_item["effective_summary"]["review"],
            {
                "machine_review_required": True,
                "machine_review_outcome": "pass",
                "codex_review_required": True,
                "codex_review_decision": "approve",
            },
        )

    def test_settings_read_model_policy_catalog_uses_store_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root)
            path = pipeline_policy_store_path(root)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "revision": 1,
                        "created_at": "2026-06-20T00:00:00Z",
                        "updated_at": "2026-06-20T00:00:00Z",
                        "presets": [
                            {
                                "name": "dry_run",
                                "policy": policy_preset("dry_run").to_dict(),
                                "created_at": "2026-06-20T00:00:00Z",
                                "updated_at": "2026-06-20T00:00:00Z",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaises(ValidationError) as raised:
                ReadOnlyProjectModel(root, actor="tester").ui_settings()

        self.assertEqual(
            raised.exception.result.errors[0].code,
            "POLICY_PRESET_BUILTIN_IMMUTABLE",
        )

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
        self.assertNotIn("Prepare for Codex unavailable:", body)
        self.assertNotIn('value="task.prepare_for_codex"', body)
        self.assertIn("Refresh Context", body)
        self.assertIn('value="task.refresh_execution_context"', body)
        self.assertIn("Submit for Review", body)
        self.assertNotIn("Submit for Review unavailable:", body)
        self.assertIn("no current Codex prompt state exists", body)
        self.assertNotIn('value="task.submit_for_review"', body)
        self.assertIn("Approve &amp; Done", body)
        self.assertIn('value="task.close_reviewed"', body)
        self.assertNotIn('value="task.request_changes"', body)
        self.assertIn('name="confirm" value="yes" required', body)
        action_forms = [
            form
            for form in post_forms(body)
            if 'name="action" value="' in form
        ]
        self.assertGreater(len(action_forms), 0)
        for form in action_forms:
            self.assertIn('action="/actions"', form)
            self.assertIn('name="confirm" value="yes" required', form)

    def test_tasks_page_renders_selected_task_details_drawer(self):
        tasks = [
            {
                "id": "TASK-300",
                "ref": "DRAW-01",
                "legacy_id": "TASK-300",
                "status": "ready",
                "title": "Drawer task",
                "summary": "Drawer summary text.",
                "description": "Drawer description text.",
                "scope": ["Drawer scope item."],
                "acceptance_criteria": ["Drawer acceptance item."],
                "blockers": ["Waiting on owner input."],
                "epic_id": "EPIC-DRAW",
                "epic_key": "DRAW",
                "pipeline_hints": {
                    "actions": [
                        {
                            "label": "Prepare for Codex",
                            "action": "task.prepare_for_codex",
                            "available": True,
                            "reason": "Ready to prepare.",
                        }
                    ],
                    "linked_changes": [
                        {
                            "id": "CHG-777",
                            "status": "ready",
                            "title": "Drawer linked change",
                        }
                    ],
                },
            },
            {
                "id": "TASK-301",
                "ref": "DRAW-02",
                "legacy_id": "TASK-301",
                "status": "ready",
                "title": "Other drawer task",
                "epic_id": "EPIC-DRAW",
                "epic_key": "DRAW",
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=tasks,
                changes=[
                    {
                        "id": "CHG-777",
                        "status": "ready",
                        "title": "Drawer linked change",
                        "linked_tasks": ["DRAW-01"],
                    }
                ],
                epics=[{"id": "EPIC-DRAW", "key": "DRAW", "status": "active"}],
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/tasks?task=DRAW-01", model)

        self.assertEqual(status.value, 200)
        self.assertIn('class="task-page-layout"', body)
        self.assertIn(
            '<aside class="drawer task-detail-drawer" id="task-details-drawer"',
            body,
        )
        self.assertIn("Selected task inspection stays outside the table rows.", body)
        self.assertIn("Drawer summary text.", body)
        self.assertIn("Drawer scope item.", body)
        self.assertIn("Drawer acceptance item.", body)
        self.assertIn("Waiting on owner input.", body)
        self.assertIn("CHG-777 ready", body)
        self.assertIn("Prepare for Codex", body)
        self.assertIn(
            'href="/tasks?view=queue&amp;group=epic&amp;task=DRAW-01#task-details-drawer"',
            body,
        )
        drawer = re.search(
            r'<aside class="drawer task-detail-drawer".*?</aside>',
            body,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(drawer)
        drawer_html = drawer.group(0) if drawer else ""
        self.assertIn("Effective Run Policy", drawer_html)
        self.assertIn("<dt>batch.max_steps</dt>", drawer_html)
        self.assertIn(
            '<details class="task-detail-section task-diagnostic-section task-diagnostic-generated-files">',
            drawer_html,
        )
        self.assertIn(
            '<details class="task-detail-section task-diagnostic-section task-diagnostic-health">',
            drawer_html,
        )
        self.assertIn(
            '<details class="task-detail-section task-diagnostic-section task-diagnostic-recent-events">',
            drawer_html,
        )
        self.assertIn("<span>Generated Files</span>", drawer_html)
        self.assertIn("<span>Health</span>", drawer_html)
        self.assertIn("<span>Recent Events</span>", drawer_html)
        diagnostic_sections = re.findall(
            r'<details class="task-detail-section task-diagnostic-section task-diagnostic-[^"]*".*?</details>',
            drawer_html,
            flags=re.DOTALL,
        )
        self.assertEqual(len(diagnostic_sections), 3)
        for section in diagnostic_sections:
            self.assertNotIn(" open", section.split(">", 1)[0])
        self.assertEqual(body.count("<h2>Project Health</h2>"), 1)
        detail_rows = [
            row for row in re.findall(r"<tr>.*?</tr>", body, flags=re.DOTALL)
            if 'class="button-link secondary task-detail-link"' in row
        ]
        for row in detail_rows:
            self.assertNotIn("Effective Run Policy", row)
            self.assertNotIn("batch.max_steps", row)
            self.assertNotIn("Generated Files", row)
            self.assertNotIn("Recent Events", row)
            self.assertNotIn("Project Health", row)

    def test_tasks_page_keeps_action_queue_rows_compact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-302",
                        "ref": "DRAW-03",
                        "legacy_id": "TASK-302",
                        "status": "ready",
                        "title": "Compact row task",
                        "summary": "Large inline detail should not be inside the row.",
                        "scope": ["Compact row scope."],
                        "acceptance_criteria": ["Compact row acceptance."],
                        "epic_id": "EPIC-DRAW",
                        "epic_key": "DRAW",
                    }
                ],
                epics=[{"id": "EPIC-DRAW", "key": "DRAW", "status": "active"}],
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/tasks", model)

        self.assertEqual(status.value, 200)
        self.assertIn(
            "<th>Task</th><th>Status</th><th>Title</th><th>Next</th><th>Primary Action</th><th>Details</th>",
            body,
        )
        self.assertNotIn("<th>Summary</th>", body)
        self.assertNotIn("<th>Stage</th>", body)
        self.assertNotIn('<details class="task-detail-panel"', body)
        detail_rows = [
            row for row in re.findall(r"<tr>.*?</tr>", body, flags=re.DOTALL)
            if 'class="button-link secondary task-detail-link"' in row
        ]
        self.assertEqual(len(detail_rows), 1)
        self.assertIn("DRAW-03", detail_rows[0])
        self.assertNotIn("Compact row scope.", detail_rows[0])
        self.assertLessEqual(detail_rows[0].count('<button type="submit">'), 2)
        self.assertIn('value="ui.run_selected_task"', detail_rows[0])
        self.assertIn('value="task.prepare_for_codex"', detail_rows[0])
        self.assertNotIn("unavailable:", detail_rows[0])
        self.assertNotIn("Effective Run Policy", detail_rows[0])
        self.assertNotIn("batch.max_steps", detail_rows[0])
        self.assertNotIn("Generated Files", detail_rows[0])
        self.assertNotIn("Recent Events", detail_rows[0])
        self.assertNotIn("Project Health", detail_rows[0])
        self.assertIn("Compact row scope.", body)

    def test_tasks_page_keeps_policy_summary_out_of_queue_rows_and_in_modal(self):
        tasks = [
            {
                "id": "TASK-303",
                "ref": "POL-01",
                "legacy_id": "TASK-303",
                "status": "ready",
                "title": "Prepare policy task",
                "epic_id": "EPIC-POL",
                "epic_key": "POL",
                "pipeline_hints": {
                    "actions": [
                        {
                            "label": "Prepare for Codex",
                            "action": "task.prepare_for_codex",
                            "available": True,
                            "reason": "Ready to prepare.",
                        }
                    ],
                },
            },
            {
                "id": "TASK-304",
                "ref": "POL-02",
                "legacy_id": "TASK-304",
                "status": "ready",
                "title": "Run policy task",
                "epic_id": "EPIC-POL",
                "epic_key": "POL",
                "pipeline_hints": {
                    "actions": [
                        {
                            "label": "Run",
                            "action": "ui.run_selected_task",
                            "available": True,
                            "reason": "Ready to run.",
                        }
                    ],
                },
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=tasks,
                epics=[{"id": "EPIC-POL", "key": "POL", "status": "active"}],
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/tasks", model)

        self.assertEqual(status.value, 200)
        self.assertIn('data-confirm-effective-policy-summary="', body)
        self.assertIn("batch.max_steps:", body)
        self.assertNotIn("data-confirm-policy-summary", body)
        self.assertIn('value="task.prepare_for_codex"', body)
        self.assertIn('data-confirm-action-id="task.prepare_for_codex"', body)

        detail_rows = [
            row for row in re.findall(r"<tr>.*?</tr>", body, flags=re.DOTALL)
            if 'class="button-link secondary task-detail-link"' in row
        ]
        self.assertEqual(len(detail_rows), 2)
        for row in detail_rows:
            self.assertNotIn("Effective Run Policy", row)
            self.assertNotIn("batch.max_steps", row)
            self.assertNotIn("Codex Review", row)

    def test_tasks_page_shows_task_row_run_resume_and_terminal_visibility(self):
        pipeline = pipeline_detail_state(
            status="blocked",
            step_status="blocked",
            finished_at="",
            current_step_status="blocked",
            stop_reason="Waiting for owner action.",
            next_action="Resolve owner blocker, then resume.",
        )
        pipeline["current_session_id"] = "PSESS-ROW"
        session = pipeline["sessions"][0]
        session["id"] = "PSESS-ROW"
        session["current_task_id"] = "TASK-203"
        session["current_task_ref"] = "RUN-01"
        session["selected_queue"]["task_refs"] = ["RUN-01"]
        session["selected_queue"]["epic_ids"] = ["EPIC-ROW"]

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-201",
                        "ref": "PLAN-01",
                        "legacy_id": "TASK-201",
                        "status": "planned",
                        "title": "Planned row run",
                        "epic_id": "EPIC-ROW",
                        "epic_key": "ROW",
                        "order": 1,
                    },
                    {
                        "id": "TASK-202",
                        "ref": "READY-01",
                        "legacy_id": "TASK-202",
                        "status": "ready",
                        "title": "Ready row run",
                        "summary": "Requires an approved Evolution Change.",
                        "epic_id": "EPIC-ROW",
                        "epic_key": "ROW",
                        "order": 2,
                    },
                    {
                        "id": "TASK-203",
                        "ref": "RUN-01",
                        "legacy_id": "TASK-203",
                        "status": "in_progress",
                        "title": "In progress row resume",
                        "epic_id": "EPIC-ROW",
                        "epic_key": "ROW",
                        "order": 3,
                    },
                    {
                        "id": "TASK-204",
                        "ref": "DONE-01",
                        "legacy_id": "TASK-204",
                        "status": "done",
                        "title": "Done row terminal",
                        "epic_id": "EPIC-ROW",
                        "epic_key": "ROW",
                        "order": 4,
                    },
                ],
                current_task_id="TASK-203",
                epics=[
                    {
                        "id": "EPIC-ROW",
                        "key": "ROW",
                        "status": "active",
                        "title": "Row Controls",
                    }
                ],
                changes=[
                    {
                        "id": "CHG-201",
                        "status": "ready",
                        "title": "Ready row required change",
                        "linked_tasks": ["READY-01"],
                    }
                ],
                pipeline=pipeline,
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/tasks?show_done=1&group=none", model)

        self.assertEqual(status.value, 200)
        self.assertNotIn('value="task.prepare_for_codex"', body)
        self.assertNotIn('name="task" value="PLAN-01"', body)
        self.assertNotIn('name="task" value="READY-01"', body)
        self.assertIn("Effective Run Policy", body)
        self.assertIn("<dt>batch.max_steps</dt><dd>5</dd>", body)
        self.assertIn("<dt>Codex Review</dt><dd>required (approve)</dd>", body)
        self.assertIn("<dt>Auto-close</dt><dd>enabled (note required)</dd>", body)
        self.assertIn("<dt>Local Commit</dt><dd>enabled (local_only)</dd>", body)
        self.assertIn("<dt>Report Warnings</dt><dd>strict (blocking)</dd>", body)
        self.assertIn("<dt>Git Diff Gates</dt><dd>strict (required)</dd>", body)
        self.assertNotIn("Incomplete Web Run", body)
        self.assertNotIn('name="incomplete_run_confirm" value="yes" required', body)
        self.assertNotIn(
            "Requires approved linked Evolution Change before execution.",
            body,
        )
        self.assertIn('data-confirm-action-id="evolution.approve_change"', body)
        self.assertIn('name="change" value="CHG-201"', body)
        self.assertIn("<button type=\"submit\">Resume</button>", body)
        self.assertIn('value="pipeline.run_next"', body)
        self.assertIn('name="session_id" value="PSESS-ROW"', body)
        self.assertIn('name="confirm" value="yes" required', body)
        self.assertIn("DONE-01", body)
        self.assertNotIn('name="task" value="DONE-01"', body)

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
        self.assertEqual(tasks_body.count("Current Execution"), 1)
        self.assertIn('class="current-execution-bar"', tasks_body)
        self.assertNotIn('class="panel execution-panel"', tasks_body)
        self.assertIn("WFA-17 in_progress", tasks_body)
        self.assertRegex(
            tasks_body,
            r'<div class="current-execution-next">Next owner action: <span>[^<]+</span></div>',
        )
        self.assertIn("Codex Prompt", tasks_body)
        self.assertIn("Context Pack", tasks_body)
        self.assertIn('class="current-execution-actions"', tasks_body)
        self.assertRegex(
            tasks_body,
            r'class="current-execution-actions"[\s\S]*Open (Task|Review|Change)',
        )

    def test_pipeline_page_shows_policy_queue_session_audit_and_actions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-064",
                        "ref": "PIPE-13",
                        "legacy_id": "TASK-064",
                        "status": "ready",
                        "title": "PIPE-13 Pipeline UI Dashboard",
                        "summary": "Add a pipeline dashboard.",
                        "epic_id": "EPIC-007",
                        "epic_key": "PIPE",
                        "order": 13,
                        "local_seq": 13,
                    }
                ],
                current_task_id="TASK-064",
                epics=[
                    {
                        "id": "EPIC-007",
                        "key": "PIPE",
                        "status": "active",
                        "title": "Pipeline Automation",
                        "order": 7,
                    }
                ],
                changes=[
                    {
                        "id": "CHG-047",
                        "status": "approved",
                        "title": "PIPE-13 Pipeline UI Dashboard",
                        "linked_tasks": ["TASK-064"],
                        "order": 47,
                    }
                ],
                pipeline={
                    "schema_version": 1,
                    "revision": 2,
                    "created_at": "2026-06-20T09:00:00Z",
                    "updated_at": "2026-06-20T09:05:00Z",
                    "current_session_id": "PSESS-001",
                    "sessions": [
                        {
                            "id": "PSESS-001",
                            "status": "blocked",
                            "selected_queue": {
                                "selection": "ready_queue",
                                "task_refs": ["PIPE-13"],
                                "epic_ids": [],
                                "statuses": ["ready"],
                                "max_tasks": 2,
                                "order_by": "execution",
                                "include_blocked_tasks": False,
                            },
                            "policy_snapshot": {"name": "supervised"},
                            "current_task_id": "TASK-064",
                            "current_task_ref": "PIPE-13",
                            "current_step": "run_next",
                            "current_step_status": "blocked",
                            "attempt_counters": {"steps": 1, "tasks": 0, "rework": 0},
                            "gate_outcomes": [
                                {
                                    "name": "token_budget",
                                    "status": "blocked",
                                    "recorded_at": "2026-06-20T09:05:00Z",
                                    "details": {
                                        "stop_code": "TOKEN_BUDGET_FAILURE",
                                        "stop_reason": "Token Budget Gate failed.",
                                    },
                                }
                            ],
                            "steps": [
                                {
                                    "name": "run_next",
                                    "status": "blocked",
                                    "task_id": "TASK-064",
                                    "stop_reason": "TOKEN_BUDGET_FAILURE: Token Budget Gate failed.",
                                    "gate_outcomes": [],
                                }
                            ],
                            "linked_change_ids": ["CHG-047"],
                            "report_ids": ["RPT-001"],
                            "review_ids": ["REV-001"],
                            "commit_ids": [],
                            "audit_event_ids": ["EVT-001"],
                            "stop_reason": "TOKEN_BUDGET_FAILURE: Token Budget Gate failed.",
                            "created_at": "2026-06-20T09:00:00Z",
                            "updated_at": "2026-06-20T09:05:00Z",
                            "started_at": "2026-06-20T09:04:00Z",
                            "finished_at": "",
                        }
                    ],
                },
                pipeline_events=[
                    {
                        "event_id": "EVT-001",
                        "timestamp": "2026-06-20T09:05:00Z",
                        "actor": "tester",
                        "command": "pipeline.step.result",
                        "entity_type": "pipeline_session",
                        "entity_id": "PSESS-001",
                        "revision_before": 1,
                        "revision_after": 2,
                        "payload": {
                            "session_id": "PSESS-001",
                            "step": {"name": "run_next", "status": "blocked"},
                            "gate_outcome": {"name": "token_budget", "status": "blocked"},
                        },
                    }
                ],
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route(
                "/pipeline?policy=supervised&status=ready&max_tasks=2&auto_create_missing_changes=yes&owner_approve_required_changes=yes&approval_note=Owner%20approved",
                model,
            )

        self.assertEqual(status.value, 200)
        self.assertIn("Pipeline Queue Selector", body)
        self.assertIn("Policy Preset Preview", body)
        self.assertIn("supervised (prompt-only)", body)
        self.assertIn("supervised_executable (executable)", body)
        self.assertIn("<td>Behavior</td><td>prompt-only</td>", body)
        self.assertIn("Auto Create Missing Changes", body)
        self.assertIn("Owner Session Change Approval", body)
        self.assertIn("Approval Note Required", body)
        self.assertIn("<td>yes</td>", body)
        self.assertIn('name="auto_create_missing_changes" value="yes" checked', body)
        self.assertIn(
            'name="owner_approve_required_changes" value="yes" checked',
            body,
        )
        self.assertIn('name="approval_note" value="Owner approved"', body)
        self.assertIn('name="auto_close_note" value=""', body)
        self.assertIn("Queue Preview", body)
        self.assertIn("PIPE-13", body)
        self.assertIn("PSESS-001", body)
        self.assertIn('href="/pipeline/sessions/PSESS-001"', body)
        self.assertIn("TOKEN_BUDGET_FAILURE", body)
        self.assertIn("Latest Pipeline Audit", body)
        self.assertIn("pipeline.step.result", body)
        self.assertIn('value="pipeline.session.create"', body)
        self.assertIn("Create Session", body)
        self.assertIn('value="pipeline.run_next"', body)
        self.assertIn("Resume Session", body)
        self.assertNotIn('value="pipeline.run_until_blocker"', body)
        self.assertNotIn("<button type=\"submit\">Run Next</button>", body)
        self.assertNotIn('value="pipeline.session.stop"', body)
        self.assertIn("Stop Session is unavailable for status blocked.", body)
        self.assertIn('value="pipeline.render"', body)
        self.assertIn("Refresh Status", body)
        self.assertIn('name="confirm" value="yes" required', body)

    def test_pipeline_page_shows_failed_execute_guidance_without_run_controls(self):
        phase_history = [
            {
                "phase": "queue_preview",
                "status": "passed",
                "reason": "Queue selected PIPE-27.",
                "next_action": "Prepare Codex prompt.",
            },
            {
                "phase": "execute",
                "status": "failed",
                "reason": "Codex Execute failed.",
                "next_action": "Inspect execution failure.",
                "artifacts": {"blocked_by": "codex_adapter"},
            },
        ]
        pipeline = pipeline_detail_state(
            status="failed",
            step_status="failed",
            finished_at="2026-06-20T13:30:00Z",
            current_step_status="failed",
            stop_reason="Codex Execute failed.",
            next_action="",
            steps=[],
            gate_outcomes=[],
            phase_history=phase_history,
        )
        pipeline["sessions"][0]["next_action"] = ""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-078",
                        "ref": "PIPE-27",
                        "legacy_id": "TASK-078",
                        "status": "in_progress",
                        "title": "Persistent session detail page",
                        "epic_id": "EPIC-007",
                        "order": 27,
                    }
                ],
                pipeline=pipeline,
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/pipeline", model)

        self.assertEqual(status.value, 200)
        self.assertIn(
            "<span>Next Action</span><strong>Inspect execution failure.</strong>",
            body,
        )
        self.assertIn("<strong>Owner guidance:</strong> Inspect execution failure.", body)
        self.assertIn("Run actions are unavailable for status failed.", body)
        self.assertNotIn("<button type=\"submit\">Run Next</button>", body)
        self.assertNotIn("<button type=\"submit\">Resume Session</button>", body)
        self.assertNotIn('value="pipeline.run_until_blocker"', body)
        self.assertNotIn('value="pipeline.session.stop"', body)
        self.assertIn("Stop Session is unavailable for status failed.", body)

    def test_pipeline_page_shows_resume_for_blocked_prepare_phase(self):
        phase_history = [
            {
                "phase": "queue_preview",
                "status": "passed",
                "reason": "Queue selected PIPE-27.",
                "next_action": "Prepare Codex prompt.",
            },
            {
                "phase": "prepare",
                "status": "blocked",
                "reason": "Prompt package blocked.",
                "next_action": "Resolve prompt blocker.",
                "artifacts": {"blocked_by": "owner"},
            },
        ]
        pipeline = pipeline_detail_state(
            status="blocked",
            step_status="blocked",
            finished_at="",
            current_step_status="blocked",
            stop_reason="Prompt package blocked.",
            next_action="",
            steps=[],
            gate_outcomes=[],
            phase_history=phase_history,
        )
        pipeline["sessions"][0]["next_action"] = ""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-078",
                        "ref": "PIPE-27",
                        "legacy_id": "TASK-078",
                        "status": "in_progress",
                        "title": "Persistent session detail page",
                        "epic_id": "EPIC-007",
                        "order": 27,
                    }
                ],
                pipeline=pipeline,
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/pipeline", model)

        self.assertEqual(status.value, 200)
        self.assertIn(
            "<span>Next Action</span><strong>Resolve prompt blocker.</strong>",
            body,
        )
        self.assertIn("<strong>Owner guidance:</strong> Resolve prompt blocker.", body)
        self.assertIn('value="pipeline.run_next"', body)
        self.assertIn("<button type=\"submit\">Resume Session</button>", body)
        self.assertIn('name="confirm" value="yes" required', body)
        self.assertNotIn("<button type=\"submit\">Run Next</button>", body)
        self.assertNotIn('value="pipeline.run_until_blocker"', body)
        self.assertNotIn('value="pipeline.session.stop"', body)
        self.assertIn("Stop Session is unavailable for status blocked.", body)

    def test_pipeline_session_detail_route_renders_running_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-078",
                        "ref": "PIPE-27",
                        "legacy_id": "TASK-078",
                        "status": "in_review",
                        "title": "Persistent session detail page",
                        "summary": "Add per-session Pipeline pages.",
                        "epic_id": "EPIC-007",
                        "epic_key": "PIPE",
                        "order": 27,
                    }
                ],
                current_task_id="TASK-078",
                changes=[
                    {
                        "id": "CHG-061",
                        "status": "ready",
                        "title": "PIPE-27 session detail page",
                        "linked_tasks": ["TASK-078"],
                        "order": 61,
                    }
                ],
                task_reports={
                    "schema_version": 1,
                    "revision": 1,
                    "reports": [
                        {
                            "id": "RPT-001",
                            "task_id": "TASK-078",
                            "task_ref": "PIPE-27",
                            "submitted_at": "2026-06-20T13:20:00Z",
                            "report": {
                                "changed_files": ["ai_project_ctl/web/server.py"],
                                "generated_files": ["AI_PROJECT/generated/PIPELINE_STATUS.md"],
                                "warnings": ["Review owner approval evidence."],
                                "blockers": [],
                                "checks": [],
                            },
                        }
                    ],
                },
                pipeline=pipeline_detail_state(
                    status="running",
                    step_status="running",
                    finished_at="",
                    current_step_status="running",
                ),
                pipeline_events=[
                    pipeline_detail_event(
                        "EVT-101",
                        "PSESS-020",
                        "pipeline.step.result",
                        {"name": "codex_execution_adapter", "status": "warn"},
                    )
                ],
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/pipeline/sessions/PSESS-020", model)

        self.assertEqual(status.value, 200)
        self.assertIn('data-auto-refresh="2"', body)
        self.assertIn('data-pipeline-session-poll', body)
        self.assertIn('data-session-id="PSESS-020"', body)
        self.assertIn(
            'data-status-url="/pipeline/sessions/PSESS-020/status.json"',
            body,
        )
        self.assertIn('data-poll-ms="2000"', body)
        self.assertIn('data-stop-statuses="blocked failed completed stopped"', body)
        self.assertIn('data-poll-enabled="1"', body)
        self.assertIn('data-pipeline-status-field="status"', body)
        self.assertIn('data-pipeline-status-field="current_phase"', body)
        self.assertIn('data-pipeline-status-field="current_phase_status"', body)
        self.assertIn('data-pipeline-status-field="stop_reason"', body)
        self.assertIn('data-pipeline-status-field="next_action"', body)
        self.assertIn('data-pipeline-status-field="polling"', body)
        self.assertIn('data-pipeline-status-overview-content', body)
        self.assertIn('data-pipeline-owner-next-action', body)
        self.assertIn("fetch(statusUrl", body)
        self.assertIn("window.setTimeout(tick, pollMs)", body)
        self.assertIn("shouldStop(payload.status)", body)
        self.assertNotIn("window.location.reload", body)
        self.assertIn("Status Overview", body)
        self.assertIn("Current Live Step", body)
        self.assertIn("Steps", body)
        self.assertIn("Artifacts", body)
        self.assertIn("Queue Snapshot", body)
        self.assertIn("Audit Events", body)
        self.assertIn("Files Changed During Session", body)
        self.assertIn("Problems / Blockers", body)
        self.assertIn("Raw Debug", body)
        self.assertIn("Run Next", body)
        self.assertIn("Run Until Blocker", body)
        self.assertIn("Stop Session", body)
        self.assertIn("Approve Required Changes", body)
        self.assertIn("Approve Auto-close", body)
        self.assertIn("Close Reviewed Task", body)
        self.assertIn('name="confirm" value="yes" required', body)
        self.assertIn("stdout diagnostic", body)
        self.assertIn("stderr diagnostic", body)
        self.assertIn("captured:stdout:sha256:abc", body)
        self.assertIn("status_not_executable", body)
        self.assertIn("ai_project_ctl/web/server.py", body)
        self.assertIn("AI_PROJECT/generated/CODEX_PROMPT.md", body)
        self.assertNotIn("FULL CODEX PROMPT BODY", body)

    def test_pipeline_session_status_json_returns_compact_live_status(self):
        phase_history = [
            {
                "phase": "queue_preview",
                "status": "passed",
                "reason": "Queue selected PIPE-27.",
                "next_action": "Prepare Codex prompt.",
                "changed_files": [],
                "generated_files": [],
                "events": ["EVT-200"],
            },
            {
                "phase": "execute",
                "status": "running",
                "reason": "Codex Execute is running.",
                "next_action": "Watch Codex output.",
                "changed_files": ["ai_project_ctl/web/server.py"],
                "generated_files": [],
                "events": ["EVT-201", "EVT-202"],
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                pipeline=pipeline_detail_state(
                    status="running",
                    step_status="running",
                    finished_at="",
                    current_step_status="running",
                    phase_history=phase_history,
                ),
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, content_type, body = route(
                "/pipeline/sessions/PSESS-020/status.json",
                model,
            )

        payload = json.loads(body)

        self.assertEqual(status.value, 200)
        self.assertEqual(content_type, "application/json; charset=utf-8")
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["session_id"], "PSESS-020")
        self.assertEqual(payload["status"], "running")
        self.assertEqual(payload["current_task"], {"id": "TASK-078", "ref": "PIPE-27"})
        self.assertEqual(payload["current_phase"], "execute")
        self.assertEqual(payload["current_phase_status"], "running")
        self.assertEqual(payload["stop_reason"], "")
        self.assertEqual(payload["next_action"], "Watch Codex output.")
        self.assertEqual(payload["phase_history"]["total"], 2)
        self.assertEqual(payload["phase_history"]["counts_by_status"]["passed"], 1)
        self.assertEqual(payload["phase_history"]["counts_by_status"]["running"], 1)
        self.assertEqual(payload["phase_history"]["latest"]["phase"], "execute")
        self.assertEqual(
            payload["phase_history"]["latest"]["changed_files_count"],
            1,
        )
        self.assertEqual(payload["phase_history"]["latest"]["event_count"], 2)
        self.assertNotIn("<section", body)
        self.assertNotIn("Status Overview", body)

    def test_pipeline_session_status_json_returns_stable_missing_session_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                pipeline=pipeline_detail_state(
                    status="running",
                    step_status="running",
                    finished_at="",
                    current_step_status="running",
                ),
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, content_type, body = route(
                "/pipeline/sessions/PSESS-MISSING/status.json",
                model,
            )

        payload = json.loads(body)

        self.assertEqual(status.value, 404)
        self.assertEqual(content_type, "application/json; charset=utf-8")
        self.assertFalse(payload["ok"])
        self.assertEqual(
            payload["error"]["code"],
            "WEB_PIPELINE_SESSION_NOT_FOUND",
        )
        self.assertEqual(payload["error"]["details"]["session_id"], "PSESS-MISSING")
        self.assertNotIn("<section", body)

    def test_pipeline_session_detail_renders_phase_history_without_fake_step(self):
        phase_history = [
            {
                "phase": "queue_preview",
                "status": "passed",
                "reason": "Queue selected PIPE-27.",
                "next_action": "Prepare Codex prompt.",
                "changed_files": [],
                "generated_files": [],
                "events": ["EVT-200"],
            },
            {
                "phase": "prepare",
                "status": "passed",
                "reason": "Prompt package ready.",
                "next_action": "Run Codex execute.",
                "changed_files": [],
                "generated_files": ["AI_PROJECT/generated/CODEX_PROMPT.md"],
                "events": ["EVT-201"],
            },
            {
                "phase": "execute",
                "status": "failed",
                "reason": "Codex Execute failed.",
                "next_action": "Inspect execution failure.",
                "artifacts": {"blocked_by": "codex_adapter"},
                "changed_files": ["ai_project_ctl/web/server.py"],
                "generated_files": [],
                "events": ["EVT-202"],
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-078",
                        "ref": "PIPE-27",
                        "legacy_id": "TASK-078",
                        "status": "in_progress",
                        "title": "Persistent session detail page",
                        "epic_id": "EPIC-007",
                        "order": 27,
                    }
                ],
                pipeline=pipeline_detail_state(
                    status="failed",
                    step_status="planned",
                    finished_at="",
                    current_step_status="failed",
                    stop_reason="Codex Execute failed.",
                    next_action="Inspect execution failure.",
                    steps=[],
                    gate_outcomes=[],
                    phase_history=phase_history,
                ),
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            detail = model.pipeline_session_detail("PSESS-020")
            status, _, body = route("/pipeline/sessions/PSESS-020", model)

        self.assertEqual(status.value, 200)
        self.assertEqual(
            [row["label"] for row in detail["session"]["phase_rows"]],
            ["Queue Preview", "Prepare", "Codex Execute"],
        )
        self.assertIn("3 of 7 pipeline phases have recorded outcomes.", body)
        self.assertIn("Queue Preview", body)
        self.assertIn("Prepare", body)
        self.assertIn("Codex Execute", body)
        self.assertIn('<span class="badge passed">passed</span>', body)
        self.assertIn('<span class="badge failed">failed</span>', body)
        self.assertIn("<span>Current Phase</span><strong>execute</strong>", body)
        self.assertIn("<span>Phase Status</span><strong>failed</strong>", body)
        self.assertIn("<span>Stop Reason</span><strong>Codex Execute failed.</strong>", body)
        self.assertIn("<span>Next Action</span><strong>Inspect execution failure.</strong>", body)
        self.assertNotIn("planned</span><span>run_next", body)
        self.assertNotIn("flow checkpoints have recorded outcomes", body)

    def test_pipeline_session_detail_renders_execute_phase_evidence(self):
        long_stderr = (
            "stderr-start "
            + ("x" * (PIPELINE_LOG_SNIPPET_LIMIT + 20))
            + " stderr-tail"
        )
        phase_history = [
            {
                "phase": "execute",
                "status": "failed",
                "reason": "Codex adapter timed out.",
                "next_action": "Inspect execution failure.",
                "artifacts": {
                    "error_code": "CODEX_ADAPTER_TIMEOUT",
                    "execute_evidence": {
                        "code": "CODEX_ADAPTER_TIMEOUT",
                        "reason": "Codex command exceeded timeout.",
                        "command_ref": "codex exec --json",
                        "duration_sec": 301.25,
                        "stdout_snippet": "stdout diagnostic",
                        "stderr_snippet": long_stderr,
                        "stderr_ref": "captured:stderr:sha256:timeout",
                    },
                    "adapter": {
                        "code": "CODEX_ADAPTER_TIMEOUT",
                        "command_ref": "codex exec --json",
                        "timeout_sec": 300,
                        "duration_sec": 301.25,
                        "prompt_path": "AI_PROJECT/generated/CODEX_PROMPT.md",
                        "report_instruction": "Submit the task report after execution.",
                    },
                    "prepare_artifacts": {
                        "prompt_path": "AI_PROJECT/generated/CODEX_PROMPT.md",
                        "context_pack_path": "AI_PROJECT/generated/CONTEXT_PACK.md",
                    },
                },
                "changed_files": [],
                "generated_files": [],
                "events": ["EVT-202"],
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-078",
                        "ref": "PIPE-27",
                        "legacy_id": "TASK-078",
                        "status": "in_progress",
                        "title": "Persistent session detail page",
                        "epic_id": "EPIC-007",
                        "order": 27,
                    }
                ],
                pipeline=pipeline_detail_state(
                    status="failed",
                    step_status="planned",
                    finished_at="",
                    current_step_status="failed",
                    stop_reason="Codex adapter timed out.",
                    next_action="Inspect execution failure.",
                    steps=[],
                    gate_outcomes=[],
                    phase_history=phase_history,
                ),
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/pipeline/sessions/PSESS-020", model)

        self.assertEqual(status.value, 200)
        self.assertIn("Execution Evidence", body)
        self.assertIn("CODEX_ADAPTER_TIMEOUT", body)
        self.assertIn("<span>Timeout</span><div>300</div>", body)
        self.assertIn("<span>Duration</span><div>301.25</div>", body)
        self.assertIn("codex exec --json", body)
        self.assertIn("AI_PROJECT/generated/CODEX_PROMPT.md", body)
        self.assertIn("AI_PROJECT/generated/CONTEXT_PACK.md", body)
        self.assertIn("Submit the task report after execution.", body)
        self.assertIn("stdout diagnostic", body)
        self.assertIn("stderr-start", body)
        self.assertIn("captured:stderr:sha256:timeout", body)
        self.assertIn("[truncated:", body)
        self.assertNotIn("stderr-tail", body)

    def test_pipeline_session_detail_renders_machine_review_diagnostic_summaries(self):
        phase_history = [
            {
                "phase": "close",
                "status": "blocked",
                "reason": "Close completed, but local commit was blocked.",
                "next_action": "Resolve local commit readiness blockers.",
                "artifacts": {
                    "blocked_by": "COMMIT_READINESS_FAILED",
                    "local_commit": {
                        "status": "blocked",
                        "code": "COMMIT_READINESS_FAILED",
                        "reason": "Machine Review FAIL blocks local commit.",
                        "readiness": {
                            "status": "blocked",
                            "code": "COMMIT_MACHINE_REVIEW_NOT_PASS",
                            "reason": "Machine Review FAIL blocks local commit.",
                            "machine_review_diagnostics": [
                                {
                                    "name": "context_check_generated",
                                    "status": "fail",
                                    "code": "CONTEXT_CHECK_GENERATED_FAILED",
                                    "reason": "Context generated output is stale.",
                                    "command": [
                                        "python",
                                        "scripts/contextctl.py",
                                        "check-generated",
                                    ],
                                    "stdout_summary": "context stdout summary",
                                    "stderr_summary": "context stderr summary",
                                },
                                {
                                    "name": "report_declared_test_1",
                                    "status": "warn",
                                    "code": "MACHINE_REVIEW_UNSAFE_TEST_COMMAND",
                                    "reason": "test_command_skipped_as_unsafe",
                                    "blocking": False,
                                },
                            ],
                            "blocking_non_pass_checks": [
                                {
                                    "name": "context_check_generated",
                                    "status": "fail",
                                    "code": "CONTEXT_CHECK_GENERATED_FAILED",
                                    "reason": "Context generated output is stale.",
                                    "blocking": True,
                                    "command": [
                                        "python",
                                        "scripts/contextctl.py",
                                        "check-generated",
                                    ],
                                    "stdout_summary": "context stdout summary",
                                    "stderr_summary": "context stderr summary",
                                }
                            ],
                            "advisory_non_pass_checks": [
                                {
                                    "name": "report_declared_test_1",
                                    "status": "warn",
                                    "code": "MACHINE_REVIEW_UNSAFE_TEST_COMMAND",
                                    "reason": "test_command_skipped_as_unsafe",
                                    "blocking": False,
                                }
                            ],
                        },
                    },
                },
                "changed_files": [],
                "generated_files": [],
                "events": ["EVT-202"],
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-078",
                        "ref": "PIPE-27",
                        "legacy_id": "TASK-078",
                        "status": "done",
                        "title": "Persistent session detail page",
                        "epic_id": "EPIC-007",
                        "order": 27,
                    }
                ],
                pipeline=pipeline_detail_state(
                    status="blocked",
                    step_status="planned",
                    finished_at="",
                    current_step_status="blocked",
                    stop_reason="Close completed, but local commit was blocked.",
                    next_action="Resolve local commit readiness blockers.",
                    steps=[],
                    gate_outcomes=[],
                    phase_history=phase_history,
                ),
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/pipeline/sessions/PSESS-020", model)

        self.assertEqual(status.value, 200)
        self.assertIn("Local Commit Diagnostics", body)
        self.assertIn("Blocking Non-pass Checks", body)
        self.assertIn("Advisory Non-pass Checks", body)
        self.assertIn("context_check_generated stdout", body)
        self.assertIn("context stdout summary", body)
        self.assertIn("context_check_generated stderr", body)
        self.assertIn("context stderr summary", body)
        self.assertIn("report_declared_test_1", body)
        self.assertIn("test_command_skipped_as_unsafe", body)

    def test_pipeline_session_detail_renders_report_recovery_action(self):
        stdout = (
            "Implementation summary:\n"
            "- Added a Web recovery action.\n"
            "Changed files:\n"
            "- ai_project_ctl/web/actions.py\n"
            "- ai_project_ctl/pipeline/report_recovery.py\n"
            "Checks:\n"
            "- python -m unittest tests.test_web_control_center passed\n"
        )
        phase_history = [
            {
                "phase": "execute",
                "status": "passed",
                "reason": "Codex completed without structured report.",
                "next_action": "Run pipeline phase collect-report.",
                "artifacts": {
                    "execute_evidence": {
                        "code": "CODEX_ADAPTER_REPORT_MISSING",
                        "reason": "structured_execution_report_missing",
                        "stdout_ref": "captured:stdout:sha256:abc",
                        "stdout_snippet": stdout,
                    },
                    "adapter_summary": {
                        "code": "CODEX_ADAPTER_REPORT_MISSING",
                        "stdout_ref": "captured:stdout:sha256:abc",
                        "stdout_snippet": stdout,
                    },
                },
                "changed_files": [],
                "generated_files": [],
                "events": ["EVT-202"],
            },
            {
                "phase": "collect_report",
                "status": "blocked",
                "reason": "No task report state exists for selected task.",
                "next_action": "Submit a report for TASK-078, then rerun collect-report.",
                "artifacts": {
                    "blocked_by": "REPORT_MISSING",
                    "session_id": "PSESS-020",
                    "task_id": "TASK-078",
                },
                "changed_files": [],
                "generated_files": [],
                "events": ["EVT-203"],
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-078",
                        "ref": "PIPE-27",
                        "legacy_id": "TASK-078",
                        "status": "in_progress",
                        "title": "Persistent session detail page",
                        "epic_id": "EPIC-007",
                        "order": 27,
                    }
                ],
                pipeline=pipeline_detail_state(
                    status="blocked",
                    step_status="planned",
                    finished_at="",
                    current_step_status="blocked",
                    stop_reason="No task report state exists for selected task.",
                    next_action="Submit a report for TASK-078, then rerun collect-report.",
                    steps=[],
                    gate_outcomes=[],
                    phase_history=phase_history,
                ),
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/pipeline/sessions/PSESS-020", model)

        self.assertEqual(status.value, 200)
        self.assertIn("Report Recovery", body)
        self.assertIn('value="pipeline.report_recovery.submit"', body)
        self.assertIn('name="session_id" value="PSESS-020"', body)
        self.assertIn('name="task_id" value="TASK-078"', body)
        self.assertIn('name="task_ref" value="PIPE-27"', body)
        self.assertIn("Draft structured report JSON", body)
        self.assertIn("&quot;task_id&quot;: &quot;TASK-078&quot;", body)
        self.assertIn("&quot;task_ref&quot;: &quot;PIPE-27&quot;", body)
        self.assertIn("ai_project_ctl/web/actions.py", body)
        self.assertIn("token_count_estimated", body)
        self.assertIn("inferred fields and estimated token_usage", body)
        self.assertIn("Submit recovered report", body)
        self.assertIn('name="confirm" value="yes" required', body)

    def test_report_recovery_action_requires_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-078",
                        "ref": "PIPE-27",
                        "legacy_id": "TASK-078",
                        "status": "in_progress",
                        "title": "Persistent session detail page",
                        "epic_id": "EPIC-007",
                        "order": 27,
                    }
                ],
                pipeline=report_missing_pipeline_state(),
            )

            with self.assertRaises(WebActionError) as raised:
                WebActionExecutor(root, actor="tester").execute(
                    {
                        "action": "pipeline.report_recovery.submit",
                        "session_id": "PSESS-020",
                        "task_id": "TASK-078",
                        "task_ref": "PIPE-27",
                    }
                )

            report_state_exists = (root / "AI_PROJECT/state/task_reports.json").exists()

        self.assertEqual(raised.exception.code, "WEB_ACTION_CONFIRMATION_REQUIRED")
        self.assertFalse(report_state_exists)

    def test_report_recovery_action_submits_draft_and_guides_collect_report(self):
        stdout = (
            "Summary:\n"
            "- Implemented recovered report submission.\n"
            "Changed files:\n"
            "- ai_project_ctl/web/actions.py\n"
            "- ai_project_ctl/web/server.py\n"
            "Checks:\n"
            "- focused web tests passed\n"
            "Total tokens: 12,345\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = root / "AI_PROJECT/logs/codex/PSESS-020/TASK-078-stdout.log"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(stdout, encoding="utf-8")
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-078",
                        "ref": "PIPE-27",
                        "legacy_id": "TASK-078",
                        "status": "in_progress",
                        "title": "Persistent session detail page",
                        "epic_id": "EPIC-007",
                        "order": 27,
                    }
                ],
                pipeline=report_missing_pipeline_state(
                    stdout=stdout,
                    stdout_log="AI_PROJECT/logs/codex/PSESS-020/TASK-078-stdout.log",
                ),
            )

            result = WebActionExecutor(root, actor="tester").execute(
                {
                    "action": "pipeline.report_recovery.submit",
                    "confirm": "yes",
                    "session_id": "PSESS-020",
                    "task_id": "TASK-078",
                    "task_ref": "PIPE-27",
                }
            )
            report_state = json.loads(
                (root / "AI_PROJECT/state/task_reports.json").read_text(
                    encoding="utf-8"
                )
            )
            body = render_action_result(result)

        self.assertTrue(result.ok)
        self.assertIn("Rerun collect-report", body)
        self.assertIn("Do not skip verify", body)
        self.assertEqual(report_state["latest_by_task"]["TASK-078"], "RPT-001")
        record = report_state["reports"][0]
        report = record["report"]
        self.assertEqual(record["task_id"], "TASK-078")
        self.assertEqual(report["reported_task_id"], "TASK-078")
        self.assertEqual(report["reported_task_ref"], "PIPE-27")
        self.assertEqual(
            report["changed_files"],
            ["ai_project_ctl/web/actions.py", "ai_project_ctl/web/server.py"],
        )
        self.assertEqual(report["checks"][0]["result"], "pass")
        self.assertEqual(report["token_usage"]["total_tokens"], 12345)
        self.assertTrue(report["token_usage"]["token_count_estimated"])
        self.assertIn("token_usage is estimated", " ".join(report["warnings"]))
        self.assertIn("captured:stdout:sha256:", record["source_file"])

    def test_pipeline_session_detail_renders_live_execute_log_panel(self):
        phase_history = [
            {
                "phase": "execute",
                "status": "running",
                "reason": "Codex Execute is running.",
                "next_action": "Watch Codex output.",
                "artifacts": {
                    "execute_started_at": "2026-06-20T13:20:00Z",
                    "runtime_logs": {
                        "stdout": {
                            "path": (
                                "AI_PROJECT/logs/codex/"
                                "PSESS-020/TASK-078-stdout.log"
                            ),
                            "start_offset": 7,
                            "end_offset": 7,
                            "bytes": 0,
                        },
                        "stderr": {
                            "path": (
                                "AI_PROJECT/logs/codex/"
                                "PSESS-020/TASK-078-stderr.log"
                            ),
                            "start_offset": 11,
                            "end_offset": 11,
                            "bytes": 0,
                        },
                    },
                    "execute_evidence": {
                        "command_ref": "codex exec --json",
                        "duration_sec": 12.5,
                        "stdout_snippet": "captured stdout after completion",
                    },
                    "adapter": {
                        "timeout_sec": 300,
                    },
                },
                "changed_files": [],
                "generated_files": [],
                "events": ["EVT-202"],
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-078",
                        "ref": "PIPE-27",
                        "legacy_id": "TASK-078",
                        "status": "in_progress",
                        "title": "Persistent session detail page",
                        "epic_id": "EPIC-007",
                        "order": 27,
                    }
                ],
                pipeline=pipeline_detail_state(
                    status="running",
                    step_status="running",
                    finished_at="",
                    current_step_status="running",
                    next_action="Watch Codex output.",
                    phase_history=phase_history,
                ),
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/pipeline/sessions/PSESS-020", model)

        self.assertEqual(status.value, 200)
        self.assertIn("Codex Execute running", body)
        self.assertIn('data-live-log-panel', body)
        self.assertIn('data-live-log-refresh="active"', body)
        self.assertIn('data-log-url="/pipeline/sessions/PSESS-020/logs/execute/stdout"', body)
        self.assertIn('data-log-url="/pipeline/sessions/PSESS-020/logs/execute/stderr"', body)
        self.assertIn('data-offset="7"', body)
        self.assertIn('data-offset="11"', body)
        self.assertIn("<span>Command</span><div>codex exec --json</div>", body)
        self.assertIn("<span>Elapsed</span><div>12.5s</div>", body)
        self.assertIn("<span>Timeout</span><div>300</div>", body)
        self.assertIn("<span>Running</span><div>yes</div>", body)
        self.assertIn("output.textContent += chunk.slice", body)
        self.assertIn("captured stdout after completion", body)

    def test_pipeline_session_log_tail_route_returns_next_bounded_chunk(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = (
                root
                / "AI_PROJECT"
                / "logs"
                / "codex"
                / "PSESS-020"
                / "TASK-078-stdout.log"
            )
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_bytes(
                b"prefix:" + (b"x" * (PIPELINE_RUNTIME_LOG_TAIL_MAX_BYTES + 5))
            )
            phase_history = [
                {
                    "phase": "execute",
                    "status": "passed",
                    "reason": "Codex execute is running.",
                    "next_action": "",
                    "artifacts": {
                        "runtime_logs": {
                            "stdout": {
                                "path": (
                                    "AI_PROJECT/logs/codex/"
                                    "PSESS-020/TASK-078-stdout.log"
                                ),
                                "start_offset": 0,
                                "end_offset": 0,
                                "bytes": 0,
                            }
                        }
                    },
                    "changed_files": [],
                    "generated_files": [],
                    "events": [],
                }
            ]
            pipeline = pipeline_detail_state(
                status="running",
                step_status="running",
                finished_at="",
                current_step_status="running",
                phase_history=phase_history,
            )
            pipeline["sessions"][0]["current_phase_status"] = "running"
            write_web_state(root, pipeline=pipeline)
            model = ReadOnlyProjectModel(root, actor="tester")

            status, content_type, body = route(
                "/pipeline/sessions/PSESS-020/logs/execute/stdout?offset=7",
                model,
            )

        payload = json.loads(body)

        self.assertEqual(status.value, 200)
        self.assertEqual(content_type, "application/json; charset=utf-8")
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["session_id"], "PSESS-020")
        self.assertEqual(payload["phase"], "execute")
        self.assertEqual(payload["stream"], "stdout")
        self.assertEqual(payload["offset"], 7)
        self.assertEqual(payload["bytes"], PIPELINE_RUNTIME_LOG_TAIL_MAX_BYTES)
        self.assertEqual(
            payload["next_offset"],
            7 + PIPELINE_RUNTIME_LOG_TAIL_MAX_BYTES,
        )
        self.assertEqual(payload["chunk"], "x" * PIPELINE_RUNTIME_LOG_TAIL_MAX_BYTES)
        self.assertFalse(payload["eof"])
        self.assertTrue(payload["running"])
        self.assertNotIn("path", payload)

    def test_pipeline_session_log_tail_rejects_invalid_stream(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = ReadOnlyProjectModel(Path(tmp), actor="tester")

            status, content_type, body = route(
                "/pipeline/sessions/PSESS-020/logs/execute/stdin?offset=0",
                model,
            )

        payload = json.loads(body)

        self.assertEqual(status.value, 400)
        self.assertEqual(content_type, "application/json; charset=utf-8")
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["code"], "WEB_INVALID_PIPELINE_LOG_STREAM")

    def test_pipeline_session_log_tail_rejects_invalid_offset(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = ReadOnlyProjectModel(Path(tmp), actor="tester")

            status, _, body = route(
                "/pipeline/sessions/PSESS-020/logs/execute/stdout?offset=-1",
                model,
            )

        payload = json.loads(body)

        self.assertEqual(status.value, 400)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["code"], "WEB_INVALID_PIPELINE_LOG_OFFSET")

    def test_pipeline_session_log_tail_returns_stable_missing_log_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                pipeline=pipeline_detail_state(
                    status="running",
                    step_status="running",
                    finished_at="",
                    current_step_status="running",
                    phase_history=[],
                ),
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route(
                "/pipeline/sessions/PSESS-020/logs/execute/stdout?offset=0",
                model,
            )

        payload = json.loads(body)

        self.assertEqual(status.value, 404)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["code"], "WEB_PIPELINE_RUNTIME_LOG_MISSING")

    def test_pipeline_session_log_tail_rejects_paths_outside_runtime_log_area(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            phase_history = [
                {
                    "phase": "execute",
                    "status": "failed",
                    "reason": "Codex failed.",
                    "next_action": "",
                    "artifacts": {
                        "runtime_logs": {
                            "stdout": {
                                "path": "AI_PROJECT/state/tasks.json",
                                "start_offset": 0,
                                "end_offset": 0,
                                "bytes": 0,
                            }
                        }
                    },
                    "changed_files": [],
                    "generated_files": [],
                    "events": [],
                }
            ]
            write_web_state(
                root,
                pipeline=pipeline_detail_state(
                    status="failed",
                    step_status="failed",
                    finished_at="2026-06-20T13:25:00Z",
                    current_step_status="failed",
                    phase_history=phase_history,
                ),
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route(
                "/pipeline/sessions/PSESS-020/logs/execute/stdout?offset=0",
                model,
            )

        payload = json.loads(body)

        self.assertEqual(status.value, 403)
        self.assertFalse(payload["ok"])
        self.assertEqual(
            payload["error"]["code"],
            "WEB_PIPELINE_RUNTIME_LOG_PATH_REJECTED",
        )
        self.assertNotIn("tasks.json", body)

    def test_pipeline_session_detail_keeps_legacy_steps_without_phase_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-078",
                        "ref": "PIPE-27",
                        "legacy_id": "TASK-078",
                        "status": "in_progress",
                        "title": "Persistent session detail page",
                        "epic_id": "EPIC-007",
                        "order": 27,
                    }
                ],
                pipeline=pipeline_detail_state(
                    status="blocked",
                    step_status="blocked",
                    finished_at="",
                    current_step_status="blocked",
                    stop_reason="BLOCKED: owner action required",
                ),
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            detail = model.pipeline_session_detail("PSESS-020")
            status, _, body = route("/pipeline/sessions/PSESS-020", model)

        self.assertEqual(status.value, 200)
        self.assertEqual(detail["session"]["phase_rows"], [])
        self.assertEqual(detail["session"]["steps"][0]["name"], "run_next")
        self.assertIn("Gate Flow", body)
        self.assertIn("token_budget_gate", body)
        self.assertIn("run_next", body)

    def test_pipeline_session_detail_shows_resume_for_blocked_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-078",
                        "ref": "PIPE-27",
                        "legacy_id": "TASK-078",
                        "status": "in_progress",
                        "title": "Persistent session detail page",
                        "epic_id": "EPIC-007",
                        "order": 27,
                    }
                ],
                pipeline=pipeline_detail_state(
                    status="blocked",
                    step_status="blocked",
                    finished_at="",
                    current_step_status="blocked",
                    stop_reason="BLOCKED: owner action required",
                ),
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/pipeline/sessions/PSESS-020", model)

        self.assertEqual(status.value, 200)
        self.assertNotIn('data-auto-refresh="2"', body)
        self.assertIn('data-pipeline-session-poll', body)
        self.assertIn('data-poll-enabled="0"', body)
        self.assertIn('data-session-status="blocked"', body)
        self.assertIn("Auto-refresh stopped", body)
        self.assertIn("Resume Session", body)
        self.assertIn('value="pipeline.run_next"', body)
        self.assertNotIn("<button type=\"submit\">Run Next</button>", body)
        self.assertNotIn('value="pipeline.run_until_blocker"', body)
        self.assertNotIn('value="pipeline.session.stop"', body)
        self.assertIn("Stop Session is unavailable for status blocked.", body)

    def test_pipeline_session_detail_renders_completed_historical_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-078",
                        "ref": "PIPE-27",
                        "legacy_id": "TASK-078",
                        "status": "done",
                        "title": "Persistent session detail page",
                        "epic_id": "EPIC-007",
                        "order": 27,
                    }
                ],
                pipeline=pipeline_detail_state(
                    status="completed",
                    step_status="passed",
                    finished_at="2026-06-20T13:30:00Z",
                    current_step_status="passed",
                    stop_reason="queue_complete",
                ),
            )
            model = ReadOnlyProjectModel(root, actor="tester")

            status, _, body = route("/pipeline/sessions/PSESS-020", model)

        self.assertEqual(status.value, 200)
        self.assertIn("PSESS-020", body)
        self.assertIn("completed", body)
        self.assertIn("queue_complete", body)
        self.assertIn("Auto-refresh stopped", body)
        self.assertNotIn('data-auto-refresh="2"', body)
        self.assertIn("Session JSON", body)

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
            tasks_status, _, tasks_body = route(
                "/tasks",
                ReadOnlyProjectModel(root, actor="tester"),
            )

        payload = json.loads(data_body)

        self.assertEqual(data_status.value, 200)
        self.assertEqual(dashboard_status.value, 200)
        self.assertEqual(tasks_status.value, 200)
        self.assertEqual(payload["execution_context"]["prompt"]["status"], "unknown")
        self.assertEqual(payload["execution_context"]["context_pack"]["status"], "unknown")
        self.assertIn("No current task selected.", dashboard_body)
        self.assertNotIn('value="current.clear"', dashboard_body)
        self.assertEqual(tasks_body.count("Current Execution"), 1)
        self.assertIn('class="current-execution-bar no-current"', tasks_body)
        self.assertIn("No current task", tasks_body)
        self.assertIn("Next owner action", tasks_body)
        self.assertIn("Select a task to prepare or execute.", tasks_body)
        self.assertNotIn('class="panel execution-panel"', tasks_body)

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
        self.assertNotIn("Prepare for Codex unavailable", body)
        self.assertIn("WFA-09 status is in_progress", body)
        self.assertIn("linked Evolution Change is missing", body)
        self.assertIn("another current task is WFA-20", body)
        self.assertIn('value="evolution.create_for_task"', body)
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
        self.assertIn('value="evolution.approve_change"', body)
        self.assertIn('name="change" value="CHG-050"', body)
        self.assertIn('name="notes" rows="2"', body)
        self.assertIn('data-confirm-modal="action"', body)
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
        self.assertNotIn('value="task.request_changes"', review_body)
        self.assertIn('name="notes" rows="2"', review_body)
        self.assertNotIn('value="task.prepare_for_codex"', review_body)
        self.assertNotIn('value="task.refresh_execution_context"', review_body)
        self.assertNotIn('value="task.submit_for_review"', review_body)

    def test_tasks_page_keeps_approve_done_primary_for_review_task_with_stale_context(self):
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
        self.assertIn("Next:</strong> Approve &amp; Done", body)
        self.assertIn('value="task.close_reviewed"', body)
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

    def test_commit_readiness_view_shows_read_only_status_checks_and_suggestion(self):
        calls = []

        def fake_run(argv, **_kwargs):
            calls.append(argv)
            if argv[0] == "git":
                return process(
                    stdout=(
                        " M ai_project_ctl/web/server.py\n"
                        "?? tests/test_web_control_center.py\n"
                    )
                )
            tail = argv[argv.index("--json") + 1 :] if "--json" in argv else []
            if Path(argv[1]).name == "aictl.py" and tail == ["project", "doctor"]:
                return completed(
                    {
                        "data": {
                            "overall_status": "WARN",
                            "summary": {"PASS": 2, "WARN": 1, "FAIL": 0},
                            "findings": [
                                {
                                    "status": "PASS",
                                    "check": "task validation",
                                    "message": "Task state is valid.",
                                },
                                {
                                    "status": "WARN",
                                    "check": "task generated output",
                                    "message": "Generated task files are stale.",
                                },
                                {
                                    "status": "PASS",
                                    "check": "protected project files",
                                    "message": "Protected-file check passed.",
                                },
                            ],
                        }
                    }
                )
            raise AssertionError("unexpected command: {}".format(argv))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-051",
                        "ref": "WFA-20",
                        "legacy_id": "TASK-051",
                        "status": "done",
                        "title": "UIX-14 Add Commit Readiness View",
                        "epic_id": "EPIC-006",
                        "updated_at": "2026-06-19T15:50:00Z",
                    }
                ],
                epics=[{"id": "EPIC-006", "key": "WFA", "status": "active"}],
                changes=[
                    {
                        "id": "CHG-034",
                        "status": "accepted",
                        "title": "UIX-14 Add Commit Readiness View",
                        "linked_tasks": ["TASK-051", "WFA-20"],
                        "accepted_at": "2026-06-19T15:55:00Z",
                    }
                ],
            )
            model = ReadOnlyProjectModel(root, actor="tester")
            with patch("ai_project_ctl.web.read_model.subprocess.run", side_effect=fake_run):
                status, _, body = route("/commit?refresh=1", model)

        git_calls = [call for call in calls if call and call[0] == "git"]

        self.assertEqual(status.value, 200)
        self.assertEqual(git_calls, [["git", "status", "--short", "--untracked-files=all"]])
        self.assertIn("Commit Readiness", body)
        self.assertIn("ai_project_ctl/web/server.py", body)
        self.assertIn("tests/test_web_control_center.py", body)
        self.assertIn("Read command", body)
        self.assertIn("Project validation", body)
        self.assertIn("Protected files", body)
        self.assertIn("Generated artifacts", body)
        self.assertIn("Generated task files are stale.", body)
        self.assertIn("WFA-20", body)
        self.assertIn("CHG-034", body)
        self.assertIn("Suggested Commit Message (not executed)", body)
        self.assertIn("Add Commit Readiness View", body)
        self.assertNotIn("git commit", " ".join(" ".join(call) for call in calls))
        self.assertNotIn("git push", " ".join(" ".join(call) for call in calls))
        self.assertNotIn("git add", " ".join(" ".join(call) for call in calls))
        self.assertNotIn("git reset", " ".join(" ".join(call) for call in calls))

    def test_commit_readiness_handles_git_unavailable_without_refreshing_doctor(self):
        calls = []

        def fake_run(argv, **_kwargs):
            calls.append(argv)
            if argv[0] == "git":
                return process(stderr="fatal: not a git repository\n", returncode=128)
            raise AssertionError("unexpected command: {}".format(argv))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(root)
            model = ReadOnlyProjectModel(root, actor="tester")
            with patch("ai_project_ctl.web.read_model.subprocess.run", side_effect=fake_run):
                data = model.commit_readiness()

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0], ["git", "status", "--short", "--untracked-files=all"])
        self.assertEqual(data["git"]["status"], "unavailable")
        self.assertEqual(data["status"], "WARN")
        self.assertIn("not a git repository", data["git"]["message"])
        self.assertFalse(data["doctor"]["cache"]["cached"])

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

    def test_actions_page_renders_run_selected_task_form(self):
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
                    }
                ],
                current_task_id="TASK-001",
            )
            status, _, body = route(
                "/actions",
                ReadOnlyProjectModel(root, actor="tester"),
            )

        self.assertEqual(status.value, 200)
        self.assertIn("Run Selected Task", body)
        self.assertIn('value="ui.run_selected_task"', body)
        self.assertIn('name="task" value="CTL-01"', body)
        self.assertIn('value="task.prepare_for_codex"', body)
        self.assertIn('data-confirm-effective-policy-summary="', body)
        self.assertIn("batch.max_steps:", body)
        self.assertNotIn("data-confirm-policy-summary", body)
        self.assertIn("Auto-close Owner Note", body)
        self.assertIn('name="auto_close_note"', body)

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

    def test_ui_settings_web_action_updates_allowlisted_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = ui_settings_path(root)

            result = WebActionExecutor(root, actor="tester").execute(
                {
                    "action": "ui.settings.set",
                    "confirm": "yes",
                    "key": "command_line",
                    "value": "codex exec --json",
                }
            )

            settings = json.loads(path.read_text(encoding="utf-8"))
            payload = result.to_dict()
            data = payload["result"]["data"]
            body = render_action_result(result)

        self.assertTrue(result.ok)
        self.assertEqual(settings["command_line"], "codex exec --json")
        self.assertEqual(settings["default_policy"], "supervised_executable_local_commit")
        self.assertEqual(data["key"], "command_line")
        self.assertEqual(data["value"], "codex exec --json")
        self.assertEqual(data["path"], str(path))
        self.assertIn(str(path), payload["result"]["changed_files"])
        self.assertEqual(payload["registered_command"]["name"], "ui.settings.set")
        self.assertIn("UI Setting", body)
        self.assertIn("Updated key", body)
        self.assertIn("command_line", body)
        self.assertIn("New value", body)
        self.assertIn("codex exec --json", body)
        self.assertIn(str(path), body)

    def test_ui_settings_web_action_rejects_unknown_default_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = ui_settings_path(root)

            with self.assertRaises(WebActionError) as raised:
                WebActionExecutor(root, actor="tester").execute(
                    {
                        "action": "ui.settings.set",
                        "confirm": "yes",
                        "key": "default_policy",
                        "value": "reckless",
                    }
                )
            self.assertFalse(path.exists())

        self.assertEqual(raised.exception.code, "WEB_UI_DEFAULT_POLICY_UNKNOWN")
        self.assertEqual(raised.exception.path, "default_policy")
        self.assertEqual(raised.exception.details["default_policy"], "reckless")

    def test_ui_settings_web_action_metadata_includes_boolean_settings(self):
        settings_action = next(
            action
            for action in available_actions()
            if action["id"] == "ui.settings.set"
        )
        key_argument = next(
            argument
            for argument in settings_action["arguments"]
            if argument["name"] == "key"
        )

        self.assertIn(
            INTERNAL_CHANGE_GATE_BYPASS_SETTING,
            key_argument["choices"],
        )
        self.assertIn(
            REQUIRE_CODEX_REVIEW_SETTING,
            key_argument["choices"],
        )
        self.assertIn(
            ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
            key_argument["choices"],
        )
        self.assertIn(
            ALLOW_REPORT_WARNINGS_SETTING,
            key_argument["choices"],
        )
        self.assertIn(
            ALLOW_RELAXED_REPORT_WARNINGS_SETTING,
            key_argument["choices"],
        )

    def test_ui_settings_web_action_updates_internal_change_gate_bypass_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = ui_settings_path(root)
            executor = WebActionExecutor(root, actor="tester")

            true_result = executor.execute(
                {
                    "action": "ui.settings.set",
                    "confirm": "yes",
                    "key": INTERNAL_CHANGE_GATE_BYPASS_SETTING,
                    "value": "true",
                }
            )
            true_settings = json.loads(path.read_text(encoding="utf-8"))
            true_data = true_result.to_dict()["result"]["data"]

            false_result = executor.execute(
                {
                    "action": "ui.settings.set",
                    "confirm": "yes",
                    "key": INTERNAL_CHANGE_GATE_BYPASS_SETTING,
                    "value": "false",
                }
            )
            false_settings = json.loads(path.read_text(encoding="utf-8"))
            false_data = false_result.to_dict()["result"]["data"]

        self.assertTrue(true_result.ok)
        self.assertIs(true_settings[INTERNAL_CHANGE_GATE_BYPASS_SETTING], True)
        self.assertIs(true_data["settings"][INTERNAL_CHANGE_GATE_BYPASS_SETTING], True)
        self.assertEqual(true_data["key"], INTERNAL_CHANGE_GATE_BYPASS_SETTING)
        self.assertEqual(true_data["value"], "true")
        self.assertTrue(false_result.ok)
        self.assertIs(false_settings[INTERNAL_CHANGE_GATE_BYPASS_SETTING], False)
        self.assertIs(false_data["settings"][INTERNAL_CHANGE_GATE_BYPASS_SETTING], False)
        self.assertEqual(false_data["key"], INTERNAL_CHANGE_GATE_BYPASS_SETTING)
        self.assertEqual(false_data["value"], "false")

    def test_ui_settings_web_action_updates_require_codex_review_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = ui_settings_path(root)
            executor = WebActionExecutor(root, actor="tester")

            false_result = executor.execute(
                {
                    "action": "ui.settings.set",
                    "confirm": "yes",
                    "key": REQUIRE_CODEX_REVIEW_SETTING,
                    "value": "false",
                }
            )
            false_settings = json.loads(path.read_text(encoding="utf-8"))
            false_data = false_result.to_dict()["result"]["data"]

            true_result = executor.execute(
                {
                    "action": "ui.settings.set",
                    "confirm": "yes",
                    "key": REQUIRE_CODEX_REVIEW_SETTING,
                    "value": "1",
                }
            )
            true_settings = json.loads(path.read_text(encoding="utf-8"))
            true_data = true_result.to_dict()["result"]["data"]

        self.assertTrue(false_result.ok)
        self.assertIs(false_settings[REQUIRE_CODEX_REVIEW_SETTING], False)
        self.assertIs(false_data["settings"][REQUIRE_CODEX_REVIEW_SETTING], False)
        self.assertEqual(false_data["key"], REQUIRE_CODEX_REVIEW_SETTING)
        self.assertEqual(false_data["value"], "false")
        self.assertTrue(true_result.ok)
        self.assertIs(true_settings[REQUIRE_CODEX_REVIEW_SETTING], True)
        self.assertIs(true_data["settings"][REQUIRE_CODEX_REVIEW_SETTING], True)
        self.assertEqual(true_data["key"], REQUIRE_CODEX_REVIEW_SETTING)
        self.assertEqual(true_data["value"], "1")

    def test_ui_settings_web_action_updates_relaxed_git_diff_verification_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = ui_settings_path(root)
            executor = WebActionExecutor(root, actor="tester")

            true_result = executor.execute(
                {
                    "action": "ui.settings.set",
                    "confirm": "yes",
                    "key": ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
                    "value": "true",
                }
            )
            true_settings = json.loads(path.read_text(encoding="utf-8"))
            true_data = true_result.to_dict()["result"]["data"]

            false_result = executor.execute(
                {
                    "action": "ui.settings.set",
                    "confirm": "yes",
                    "key": ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
                    "value": "false",
                }
            )
            false_settings = json.loads(path.read_text(encoding="utf-8"))
            false_data = false_result.to_dict()["result"]["data"]

        self.assertTrue(true_result.ok)
        self.assertIs(true_settings[ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING], True)
        self.assertIs(
            true_data["settings"][ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING],
            True,
        )
        self.assertEqual(
            true_data["key"],
            ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
        )
        self.assertEqual(true_data["value"], "true")
        self.assertTrue(false_result.ok)
        self.assertIs(false_settings[ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING], False)
        self.assertIs(
            false_data["settings"][ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING],
            False,
        )
        self.assertEqual(
            false_data["key"],
            ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
        )
        self.assertEqual(false_data["value"], "false")

    def test_ui_settings_web_action_updates_report_warning_allowance_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = ui_settings_path(root)
            executor = WebActionExecutor(root, actor="tester")

            true_result = executor.execute(
                {
                    "action": "ui.settings.set",
                    "confirm": "yes",
                    "key": ALLOW_REPORT_WARNINGS_SETTING,
                    "value": "true",
                }
            )
            true_settings = json.loads(path.read_text(encoding="utf-8"))
            true_data = true_result.to_dict()["result"]["data"]

            false_result = executor.execute(
                {
                    "action": "ui.settings.set",
                    "confirm": "yes",
                    "key": ALLOW_REPORT_WARNINGS_SETTING,
                    "value": "false",
                }
            )
            false_settings = json.loads(path.read_text(encoding="utf-8"))
            false_data = false_result.to_dict()["result"]["data"]

        self.assertTrue(true_result.ok)
        self.assertIs(true_settings[ALLOW_REPORT_WARNINGS_SETTING], True)
        self.assertIs(
            true_data["settings"][ALLOW_REPORT_WARNINGS_SETTING],
            True,
        )
        self.assertIs(
            true_data["settings"][ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING],
            False,
        )
        self.assertEqual(true_data["key"], ALLOW_REPORT_WARNINGS_SETTING)
        self.assertEqual(true_data["value"], "true")
        self.assertTrue(false_result.ok)
        self.assertIs(false_settings[ALLOW_REPORT_WARNINGS_SETTING], False)
        self.assertIs(
            false_data["settings"][ALLOW_REPORT_WARNINGS_SETTING],
            False,
        )
        self.assertIs(
            false_data["settings"][ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING],
            False,
        )
        self.assertEqual(false_data["key"], ALLOW_REPORT_WARNINGS_SETTING)
        self.assertEqual(false_data["value"], "false")

    def test_ui_settings_apply_web_action_saves_allowlisted_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = ui_settings_path(root)

            result = WebActionExecutor(root, actor="tester").execute(
                {
                    "action": "ui.settings.apply",
                    "confirm": "yes",
                    "command_line": "codex exec --json",
                    "default_policy": "supervised",
                    BATCH_MAX_STEPS_SETTING: "9",
                    BATCH_MAX_FAILURES_SETTING: "2",
                    REQUIRE_CODEX_REVIEW_SETTING: "false",
                    INTERNAL_CHANGE_GATE_BYPASS_SETTING: "false",
                    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING: "true",
                    ALLOW_REPORT_WARNINGS_SETTING: "true",
                    ALLOW_RELAXED_REPORT_WARNINGS_SETTING: "true",
                    "execution_timeout_sec": "1800",
                    "preflight_timeout_sec": "45",
                }
            )

            settings = json.loads(path.read_text(encoding="utf-8"))
            payload = result.to_dict()
            data = payload["result"]["data"]

        self.assertTrue(result.ok)
        self.assertEqual(settings["command_line"], "codex exec --json")
        self.assertEqual(settings["default_policy"], "supervised")
        self.assertEqual(settings[BATCH_MAX_STEPS_SETTING], 9)
        self.assertEqual(settings[BATCH_MAX_FAILURES_SETTING], 2)
        self.assertIs(settings[REQUIRE_CODEX_REVIEW_SETTING], False)
        self.assertIs(settings[INTERNAL_CHANGE_GATE_BYPASS_SETTING], False)
        self.assertIs(settings[ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING], True)
        self.assertIs(settings[ALLOW_REPORT_WARNINGS_SETTING], True)
        self.assertIs(settings[ALLOW_RELAXED_REPORT_WARNINGS_SETTING], True)
        self.assertEqual(settings["execution_timeout_sec"], "1800")
        self.assertEqual(settings["preflight_timeout_sec"], "45")
        self.assertEqual(data["settings"], settings)
        self.assertEqual(data["path"], str(path))
        self.assertIn(str(path), payload["result"]["changed_files"])
        self.assertEqual(payload["registered_command"]["name"], "ui.settings.apply")
        self.assertEqual(
            data["applied_keys"],
            [
                "command_line",
                "default_policy",
                BATCH_MAX_STEPS_SETTING,
                BATCH_MAX_FAILURES_SETTING,
                REQUIRE_CODEX_REVIEW_SETTING,
                INTERNAL_CHANGE_GATE_BYPASS_SETTING,
                ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
                ALLOW_REPORT_WARNINGS_SETTING,
                ALLOW_RELAXED_REPORT_WARNINGS_SETTING,
                "execution_timeout_sec",
                "preflight_timeout_sec",
            ],
        )

    def test_ui_settings_apply_web_action_rejects_unknown_default_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = ui_settings_path(root)

            with self.assertRaises(WebActionError) as raised:
                WebActionExecutor(root, actor="tester").execute(
                    {
                        "action": "ui.settings.apply",
                        "confirm": "yes",
                        "command_line": "codex exec --json",
                        "default_policy": "reckless",
                    }
                )
            self.assertFalse(path.exists())

        self.assertEqual(raised.exception.code, "WEB_UI_DEFAULT_POLICY_UNKNOWN")
        self.assertEqual(raised.exception.path, "default_policy")
        self.assertEqual(raised.exception.details["default_policy"], "reckless")

    def test_ui_settings_apply_web_action_rejects_invalid_batch_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = ui_settings_path(root)

            with self.assertRaises(WebActionError) as raised:
                WebActionExecutor(root, actor="tester").execute(
                    {
                        "action": "ui.settings.apply",
                        "confirm": "yes",
                        "command_line": "codex exec --json",
                        "default_policy": "supervised",
                        BATCH_MAX_STEPS_SETTING: "0",
                    }
                )
            self.assertFalse(path.exists())

        self.assertEqual(raised.exception.code, "UI_SETTINGS_BATCH_LIMIT_INVALID")
        self.assertEqual(raised.exception.path, BATCH_MAX_STEPS_SETTING)
        self.assertEqual(raised.exception.details["setting"], BATCH_MAX_STEPS_SETTING)

    def test_ui_settings_apply_web_action_rejects_disallowed_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            with self.assertRaises(WebActionError) as raised:
                WebActionExecutor(root, actor="tester").execute(
                    {
                        "action": "ui.settings.apply",
                        "confirm": "yes",
                        "some_random_key": "value",
                    }
                )

            self.assertEqual(raised.exception.code, "WEB_UI_SETTING_KEY_NOT_ALLOWED")
            self.assertIn(
                REQUIRE_CODEX_REVIEW_SETTING,
                raised.exception.details["allowed_keys"],
            )
            self.assertFalse(ui_settings_path(root).exists())

    def test_ui_settings_web_action_requires_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(WebActionError) as raised:
                WebActionExecutor(root, actor="tester").execute(
                    {
                        "action": "ui.settings.set",
                        "key": "command_line",
                        "value": "codex exec --json",
                    }
                )

            self.assertEqual(raised.exception.code, "WEB_ACTION_CONFIRMATION_REQUIRED")
            self.assertFalse(ui_settings_path(root).exists())

    def test_ui_settings_web_action_rejects_disallowed_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = write_ui_settings(root, {"command_line": "codex exec"})

            with self.assertRaises(WebActionError) as raised:
                WebActionExecutor(root, actor="tester").execute(
                    {
                        "action": "ui.settings.set",
                        "confirm": "yes",
                        "key": "some_random_key",
                        "value": "value",
                    }
                )

            self.assertEqual(raised.exception.code, "WEB_UI_SETTING_KEY_NOT_ALLOWED")
            self.assertIn(
                INTERNAL_CHANGE_GATE_BYPASS_SETTING,
                raised.exception.details["allowed_keys"],
            )
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                {"command_line": "codex exec"},
            )

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

    def test_pipeline_web_actions_delegate_to_aictl(self):
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"ok": true, "data": {"session_id": "PSESS-001"}}\n',
            stderr="",
        )

        cases = [
            (
                {
                    "action": "pipeline.session.create",
                    "confirm": "yes",
                    "policy": "supervised",
                    "auto_create_missing_changes": "yes",
                    "owner_approve_required_changes": "yes",
                    "approval_note": "Owner approved session Changes.",
                    "auto_close_note": "Owner approved auto-close.",
                    "task_ref": "PIPE-13",
                    "status_filter": "ready",
                    "max_tasks": "2",
                    "order_by": "execution",
                    "current_task_id": "TASK-064",
                    "current_task_ref": "PIPE-13",
                    "change": "CHG-047",
                    "report": "RPT-001",
                    "status": "planned",
                },
                [
                    "pipeline",
                    "session",
                    "create",
                    "--policy",
                    "supervised",
                    "--auto-create-missing-changes",
                    "--owner-approve-required-changes",
                    "--approval-note",
                    "Owner approved session Changes.",
                    "--auto-close-note",
                    "Owner approved auto-close.",
                    "--task-ref",
                    "PIPE-13",
                    "--status-filter",
                    "ready",
                    "--max-tasks",
                    "2",
                    "--order-by",
                    "execution",
                    "--current-task-id",
                    "TASK-064",
                    "--current-task-ref",
                    "PIPE-13",
                    "--change",
                    "CHG-047",
                    "--report",
                    "RPT-001",
                    "--status",
                    "planned",
                ],
            ),
            (
                {
                    "action": "pipeline.run_next",
                    "confirm": "yes",
                    "session_id": "PSESS-001",
                },
                ["pipeline", "run-next", "PSESS-001"],
            ),
            (
                {
                    "action": "pipeline.run_until_blocker",
                    "confirm": "yes",
                    "session_id": "PSESS-001",
                },
                ["pipeline", "run-until-blocker", "PSESS-001", "--confirm"],
            ),
            (
                {
                    "action": "pipeline.session.stop",
                    "confirm": "yes",
                    "session_id": "PSESS-001",
                    "reason": "Owner stop",
                    "status": "stopped",
                },
                [
                    "pipeline",
                    "session",
                    "stop",
                    "PSESS-001",
                    "--reason",
                    "Owner stop",
                    "--status",
                    "stopped",
                ],
            ),
            (
                {
                    "action": "pipeline.render",
                    "confirm": "yes",
                },
                ["pipeline", "render"],
            ),
        ]

        for fields, expected_tail in cases:
            with self.subTest(action=fields["action"]):
                with patch(
                    "ai_project_ctl.web.actions.subprocess.run",
                    return_value=completed_process,
                ) as run:
                    result = WebActionExecutor("/tmp/project", actor="tester").execute(
                        fields
                    )

                argv = run.call_args.args[0]

                self.assertTrue(result.ok)
                self.assertEqual(Path(argv[1]).name, "aictl.py")
                self.assertEqual(argv[-len(expected_tail) :], expected_tail)

    def test_ui_run_selected_task_web_action_creates_single_task_session(self):
        selected_policy = policy_preset("supervised_executable_local_commit")
        session_result = CommandResult.success(
            command="pipeline.session.create",
            domain="pipeline",
            message="Created pipeline session.",
            data={"session_id": "PSESS-009", "session": {"id": "PSESS-009"}},
        )
        run_result = CommandResult.success(
            command="pipeline.run_until_blocker",
            domain="pipeline",
            message="TOKEN_GATE_BLOCKED: Token evidence required.",
            data={
                "session_id": "PSESS-009",
                "stop_code": "TOKEN_GATE_BLOCKED",
                "stop_reason": "Token evidence required.",
            },
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "legacy_id": "TASK-001",
                        "aliases": ["TASK-001"],
                        "status": "ready",
                        "title": "Ready task",
                        "epic_id": "EPIC-001",
                    }
                ],
                epics=[{"id": "EPIC-001", "status": "active"}],
            )
            resolved_root = root.resolve()
            with patch(
                "ai_project_ctl.web.actions.resolve_ui_pipeline_policy",
                return_value=selected_policy,
            ) as resolve_policy:
                with patch(
                    "ai_project_ctl.web.actions.capture_worktree_dirty_preflight",
                    return_value=WorktreeDirtyPreflight(checked=True, available=True),
                ) as preflight:
                    with patch(
                        "ai_project_ctl.web.actions.create_session",
                        return_value=session_result,
                    ) as create:
                        with patch(
                            "ai_project_ctl.web.actions.run_until_blocker",
                            return_value=run_result,
                        ) as run_until:
                            with patch(
                                "ai_project_ctl.web.actions.subprocess.run"
                            ) as run:
                                result = WebActionExecutor(
                                    root,
                                    actor="tester",
                                ).execute(
                                    {
                                        "action": "ui.run_selected_task",
                                        "confirm": "yes",
                                        "incomplete_run_confirm": "yes",
                                        "task": "APP-01",
                                    }
                                )

        preflight.assert_called_once_with(root=resolved_root)
        resolve_policy.assert_called_once_with(root=resolved_root)
        create.assert_called_once()
        create_kwargs = create.call_args.kwargs
        self.assertEqual(create_kwargs["actor"], "tester")
        self.assertEqual(create_kwargs["policy_name"], selected_policy.name)
        self.assertEqual(create_kwargs["auto_close_note"], "")
        self.assertNotIn("task_refs", create_kwargs)
        self.assertNotIn("max_tasks", create_kwargs)
        self.assertNotIn("order_by", create_kwargs)
        self.assertEqual(
            create_kwargs["selected_queue"],
            {
                "selection": "ready_queue",
                "task_refs": ["APP-01"],
                "epic_ids": [],
                "statuses": [],
                "max_tasks": 1,
                "order_by": "selected",
                "include_blocked_tasks": selected_policy.queue.include_blocked_tasks,
                "created_by_command": "ui.run",
                "ui_run_confirmed": True,
                "allow_internal_change_gate_bypass": False,
            },
        )
        run_until.assert_called_once_with(
            "PSESS-009",
            root=resolved_root,
            actor="tester",
            confirmed=True,
        )
        run.assert_not_called()

        payload = result.to_dict()
        self.assertTrue(result.ok)
        self.assertEqual(payload["command"], "pipeline.run_until_blocker")
        self.assertEqual(payload["result"]["data"]["session_id"], "PSESS-009")
        self.assertEqual(payload["result"]["data"]["created_session"]["id"], "PSESS-009")
        self.assertEqual(
            payload["result"]["data"]["session_href"],
            "/pipeline/sessions/PSESS-009",
        )
        self.assertEqual(
            payload["result"]["data"]["redirect_target"],
            "/pipeline/sessions/PSESS-009",
        )

    def test_ui_run_selected_task_web_action_stops_for_dirty_worktree(self):
        dirty_preflight = WorktreeDirtyPreflight(
            checked=True,
            available=True,
            entries=(
                GitStatusEntry("M", "ai_project_ctl/web/actions.py"),
                GitStatusEntry("??", "tmp/new-artifact.txt"),
            ),
            dirty_paths=(
                "ai_project_ctl/web/actions.py",
                "tmp/new-artifact.txt",
            ),
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "legacy_id": "TASK-001",
                        "aliases": ["TASK-001"],
                        "status": "ready",
                        "title": "Ready task",
                        "epic_id": "EPIC-001",
                    }
                ],
                epics=[{"id": "EPIC-001", "status": "active"}],
            )

            with patch(
                "ai_project_ctl.web.actions.capture_worktree_dirty_preflight",
                return_value=dirty_preflight,
            ) as preflight:
                with patch(
                    "ai_project_ctl.web.actions.resolve_ui_pipeline_policy",
                ) as resolve_policy:
                    with patch(
                        "ai_project_ctl.web.actions.create_session",
                    ) as create:
                        with patch(
                            "ai_project_ctl.web.actions.run_until_blocker",
                        ) as run_until:
                            result = WebActionExecutor(root, actor="tester").execute(
                                {
                                    "action": "ui.run_selected_task",
                                    "confirm": "yes",
                                    "incomplete_run_confirm": "yes",
                                    "task": "APP-01",
                                }
                            )

            pipeline_path = root / "AI_PROJECT" / "state" / "pipeline_sessions.json"
            tasks_state = json.loads(
                (root / "AI_PROJECT" / "state" / "tasks.json").read_text(
                    encoding="utf-8"
                )
            )

        preflight.assert_called_once_with(root=root.resolve())
        resolve_policy.assert_not_called()
        create.assert_not_called()
        run_until.assert_not_called()
        self.assertFalse(pipeline_path.exists())
        self.assertEqual(tasks_state["tasks"][0]["status"], "ready")

        payload = result.to_dict()
        data = payload["result"]["data"]
        self.assertTrue(result.ok)
        self.assertTrue(data["not_run"])
        self.assertEqual(data["task_ref"], "APP-01")
        self.assertEqual(data["task_id"], "TASK-001")
        self.assertEqual(data["selected_task"], "APP-01 (TASK-001)")
        self.assertEqual(data["outcome"], "worktree_dirty")
        self.assertEqual(data["reason"], "worktree_dirty")
        self.assertEqual(data["stop_code"], "WORKTREE_DIRTY")
        self.assertEqual(
            data["dirty_files"],
            ["ai_project_ctl/web/actions.py", "tmp/new-artifact.txt"],
        )
        self.assertEqual(
            data["git_status_entries"],
            [
                {"status": "M", "path": "ai_project_ctl/web/actions.py"},
                {"status": "??", "path": "tmp/new-artifact.txt"},
            ],
        )
        self.assertIn("git add -A", data["suggested_checkpoint_commands"])
        self.assertIn(
            "Web Run must start from a clean worktree",
            payload["result"]["owner_action_required"],
        )
        self.assertIn(
            "Create checkpoint commit for selected task APP-01 (TASK-001).",
            payload["result"]["next_actions"],
        )
        self.assertIn(
            "After checkpoint commit succeeds, run selected task APP-01 (TASK-001) again.",
            payload["result"]["next_actions"],
        )
        self.assertIn(
            "run selected task APP-01 (TASK-001) again",
            data["next_action"],
        )
        self.assertIn(
            "Checkpoint before Web Run",
            " ".join(result.to_dict()["result"]["next_actions"]),
        )
        self.assertIn("worktree is dirty", payload["result"]["message"])

        body = render_action_result(result)
        self.assertIn('<span class="badge warn">NOT RUN</span>', body)
        self.assertIn("Dirty Files", body)
        self.assertIn("ai_project_ctl/web/actions.py", body)
        self.assertIn("Suggested Checkpoint Commands", body)
        self.assertIn("git add -A", body)
        self.assertIn("Create Checkpoint Commit", body)
        self.assertIn("Web Run must start from a clean worktree", body)
        self.assertIn("APP-01 (TASK-001)", body)
        self.assertIn('name="action" value="ui.checkpoint_commit"', body)
        self.assertIn('name="task" value="APP-01"', body)
        self.assertIn('name="task_id" value="TASK-001"', body)

    def test_ui_run_selected_task_web_action_does_not_create_session_for_done_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "legacy_id": "TASK-001",
                        "aliases": ["TASK-001"],
                        "status": "done",
                        "title": "Done task",
                        "epic_id": "EPIC-001",
                    }
                ],
                epics=[{"id": "EPIC-001", "status": "active"}],
            )

            with patch("ai_project_ctl.web.actions.create_session") as create:
                with patch("ai_project_ctl.web.actions.run_until_blocker") as run_until:
                    result = WebActionExecutor(root, actor="tester").execute(
                        {
                            "action": "ui.run_selected_task",
                            "confirm": "yes",
                            "task": "APP-01",
                        }
                    )

            pipeline_path = root / "AI_PROJECT" / "state" / "pipeline_sessions.json"
            pipeline_exists = pipeline_path.exists()

        create.assert_not_called()
        run_until.assert_not_called()
        self.assertFalse(pipeline_exists)
        payload = result.to_dict()
        self.assertTrue(result.ok)
        self.assertEqual(payload["result"]["data"]["outcome"], "not_run")
        self.assertEqual(payload["result"]["data"]["task_status"], "done")
        self.assertEqual(payload["result"]["data"]["session_id"], "")
        self.assertIn("NOT RUN", payload["result"]["message"])

    def test_ui_run_selected_task_web_action_links_existing_session_without_duplicate_run(self):
        pipeline = pipeline_detail_state(
            status="blocked",
            step_status="blocked",
            finished_at="",
            current_step_status="blocked",
            stop_reason="Waiting for owner action.",
            next_action="Resume when ready.",
        )
        session = pipeline["sessions"][0]
        session["id"] = "PSESS-EXISTING"
        session["current_task_id"] = "TASK-001"
        session["current_task_ref"] = "APP-01"
        session["selected_queue"]["task_refs"] = ["APP-01"]
        pipeline["current_session_id"] = "PSESS-EXISTING"

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "legacy_id": "TASK-001",
                        "aliases": ["TASK-001"],
                        "status": "ready",
                        "title": "Ready task with existing session",
                        "epic_id": "EPIC-001",
                    }
                ],
                epics=[{"id": "EPIC-001", "status": "active"}],
                pipeline=pipeline,
            )

            with patch("ai_project_ctl.web.actions.create_session") as create:
                with patch("ai_project_ctl.web.actions.run_until_blocker") as run_until:
                    result = WebActionExecutor(root, actor="tester").execute(
                        {
                            "action": "ui.run_selected_task",
                            "confirm": "yes",
                            "task": "TASK-001",
                        }
                    )

        create.assert_not_called()
        run_until.assert_not_called()
        payload = result.to_dict()
        self.assertTrue(result.ok)
        self.assertEqual(payload["result"]["data"]["outcome"], "existing_session")
        self.assertEqual(payload["result"]["data"]["session_id"], "PSESS-EXISTING")
        self.assertEqual(
            payload["result"]["data"]["session_href"],
            "/pipeline/sessions/PSESS-EXISTING",
        )
        self.assertIn(
            "Open pipeline session PSESS-EXISTING.",
            payload["result"]["next_actions"],
        )

    def test_ui_run_selected_task_web_action_reads_internal_bypass_setting(self):
        selected_policy = policy_preset("supervised_executable_local_commit")
        session_result = CommandResult.success(
            command="pipeline.session.create",
            domain="pipeline",
            message="Created pipeline session.",
            data={"session_id": "PSESS-010", "session": {"id": "PSESS-010"}},
        )
        run_result = CommandResult.success(
            command="pipeline.run_until_blocker",
            domain="pipeline",
            message="Blocked for owner action.",
            data={"session_id": "PSESS-010"},
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            settings_path = ui_settings_path(root)
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            settings_path.write_text(
                json.dumps({INTERNAL_CHANGE_GATE_BYPASS_SETTING: True}),
                encoding="utf-8",
            )
            with patch(
                "ai_project_ctl.web.actions.resolve_ui_pipeline_policy",
                return_value=selected_policy,
            ):
                with patch(
                    "ai_project_ctl.web.actions.create_session",
                    return_value=session_result,
                ) as create:
                    with patch(
                        "ai_project_ctl.web.actions.run_until_blocker",
                        return_value=run_result,
                    ):
                        WebActionExecutor(root, actor="tester").execute(
                            {
                                "action": "ui.run_selected_task",
                                "confirm": "yes",
                                "incomplete_run_confirm": "yes",
                                "task": "TASK-001",
                            }
                        )

        selected_queue = create.call_args.kwargs["selected_queue"]
        self.assertTrue(selected_queue["allow_internal_change_gate_bypass"])
        self.assertEqual(selected_queue["created_by_command"], "ui.run")
        self.assertTrue(selected_queue["ui_run_confirmed"])

    def test_ui_run_selected_task_autoclose_requires_owner_note_before_execution(self):
        selected_policy = policy_preset("supervised_executable_autoclose")

        with patch(
            "ai_project_ctl.web.actions.resolve_ui_pipeline_policy",
            return_value=selected_policy,
        ), patch(
            "ai_project_ctl.web.actions.run_until_blocker",
            side_effect=AssertionError("ui run must not start Codex execution"),
        ) as run_until:
            with self.assertRaises(WebActionError) as raised:
                WebActionExecutor("/tmp/project", actor="tester").execute(
                    {
                        "action": "ui.run_selected_task",
                        "confirm": "yes",
                        "incomplete_run_confirm": "yes",
                        "task": "TASK-001",
                    }
                )

        self.assertEqual(raised.exception.code, "WEB_ACTION_COMMAND_FAILED")
        result = raised.exception.details["result"]
        self.assertFalse(result["ok"])
        self.assertEqual(result["message"], "PIPELINE_AUTO_CLOSE_OWNER_NOTE_REQUIRED")
        self.assertEqual(
            result["owner_action_required"],
            "Provide Human Owner auto-close approval note.",
        )
        self.assertEqual(
            result["errors"][0]["code"],
            "PIPELINE_AUTO_CLOSE_OWNER_NOTE_REQUIRED",
        )
        self.assertEqual(
            result["errors"][0]["details"]["required_argument"],
            "auto_close_note",
        )
        run_until.assert_not_called()

    def test_ui_run_selected_task_autoclose_stores_owner_note_in_session(self):
        note = "Owner approved auto-close for selected UI task."

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "legacy_id": "TASK-001",
                        "aliases": ["TASK-001"],
                        "uid": "uid_task_001",
                        "status": "ready",
                        "title": "Runnable task",
                        "epic_id": "EPIC-001",
                        "allowed_files": ["tests/**"],
                    }
                ],
                initiatives=[{"id": "INIT-001", "status": "active"}],
                epics=[
                    {
                        "id": "EPIC-001",
                        "initiative_id": "INIT-001",
                        "status": "planned",
                        "key": "APP",
                    }
                ],
                changes=[
                    {
                        "id": "CHG-001",
                        "status": "approved",
                        "linked_tasks": ["TASK-001"],
                    }
                ],
            )
            write_ui_settings(
                root,
                {
                    "default_policy": "supervised_executable_autoclose",
                    "command_line": "codex exec",
                },
            )
            run_result = CommandResult.success(
                command="pipeline.run_until_blocker",
                domain="pipeline",
                message="Stopped at first blocker.",
                data={"session_id": "PSESS-001"},
            )

            with patch(
                "ai_project_ctl.web.actions.run_until_blocker",
                return_value=run_result,
            ) as run_until:
                result = WebActionExecutor(root, actor="tester").execute(
                    {
                        "action": "ui.run_selected_task",
                        "confirm": "yes",
                        "incomplete_run_confirm": "yes",
                        "task": "APP-01",
                        "auto_close_note": note,
                    }
                )

            state = json.loads(
                (root / "AI_PROJECT" / "state" / "pipeline_sessions.json").read_text(
                    encoding="utf-8"
                )
            )

        self.assertTrue(result.ok)
        payload = result.to_dict()
        self.assertIn("--auto-close-note", payload["delegate"])
        self.assertIn(note, payload["delegate"])
        run_until.assert_called_once_with(
            "PSESS-001",
            root=root.resolve(),
            actor="tester",
            confirmed=True,
        )
        closure = state["sessions"][0]["policy_snapshot"]["closure"]
        self.assertTrue(closure["auto_close_task"])
        self.assertEqual(closure["owner_approval_note"], note)
        self.assertNotIn("owner_approval_note", state["sessions"][0]["selected_queue"])

    def test_ui_run_selected_task_action_requires_incomplete_run_confirmation(self):
        selected_policy = policy_preset("supervised_executable_local_commit")

        with patch(
            "ai_project_ctl.web.actions.resolve_ui_pipeline_policy",
            return_value=selected_policy,
        ), patch("ai_project_ctl.web.actions.create_session") as create, patch(
            "ai_project_ctl.web.actions.run_until_blocker"
        ) as run_until:
            with self.assertRaises(WebActionError) as raised:
                WebActionExecutor("/tmp/project", actor="tester").execute(
                    {
                        "action": "ui.run_selected_task",
                        "confirm": "yes",
                        "task": "TASK-001",
                    }
                )

        self.assertEqual(
            raised.exception.code,
            "WEB_INCOMPLETE_RUN_CONFIRMATION_REQUIRED",
        )
        self.assertEqual(raised.exception.path, "incomplete_run_confirm")
        self.assertEqual(raised.exception.details["max_steps"], 5)
        self.assertEqual(raised.exception.details["phase_count"], 7)
        self.assertIn("review and close may not run", raised.exception.message)
        self.assertIn("Resume Session can continue", raised.exception.message)
        create.assert_not_called()
        run_until.assert_not_called()

    def test_ui_run_selected_task_action_requires_confirmation(self):
        with patch("ai_project_ctl.web.actions.create_session") as create:
            with self.assertRaises(WebActionError) as raised:
                WebActionExecutor("/tmp/project", actor="tester").execute(
                    {
                        "action": "ui.run_selected_task",
                        "task": "TASK-001",
                    }
                )

        self.assertEqual(raised.exception.code, "WEB_ACTION_CONFIRMATION_REQUIRED")
        create.assert_not_called()

    def test_checkpoint_commit_action_requires_confirmation(self):
        with patch("ai_project_ctl.web.actions.create_checkpoint_commit") as checkpoint:
            with self.assertRaises(WebActionError) as raised:
                WebActionExecutor("/tmp/project", actor="tester").execute(
                    {
                        "action": "ui.checkpoint_commit",
                        "task": "TASK-001",
                    }
                )

        self.assertEqual(raised.exception.code, "WEB_ACTION_CONFIRMATION_REQUIRED")
        checkpoint.assert_not_called()

    def test_checkpoint_commit_action_reports_not_run_for_clean_worktree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(
                ["git", "init"],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )

            result = WebActionExecutor(root, actor="tester").execute(
                {
                    "action": "ui.checkpoint_commit",
                    "confirm": "yes",
                    "task": "APP-01",
                }
            )

        payload = result.to_dict()
        data = payload["result"]["data"]
        self.assertTrue(result.ok)
        self.assertTrue(data["not_run"])
        self.assertEqual(data["outcome"], "worktree_clean")
        self.assertEqual(data["stop_code"], "WORKTREE_CLEAN")
        self.assertEqual(data["commit_hash"], "")
        self.assertEqual(data["dirty_files"], [])

    def test_checkpoint_commit_action_commits_dirty_worktree_and_reports_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(
                ["git", "init"],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "owner@example.invalid"],
                cwd=root,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Human Owner"],
                cwd=root,
                check=True,
            )
            write_web_state(
                root,
                tasks=[
                    {
                        "id": "TASK-001",
                        "ref": "APP-01",
                        "legacy_id": "TASK-001",
                        "aliases": ["TASK-001"],
                        "status": "ready",
                        "title": "Ready task",
                        "epic_id": "EPIC-001",
                    }
                ],
                epics=[{"id": "EPIC-001", "status": "active"}],
            )
            (root / "dirty.txt").write_text("dirty\n", encoding="utf-8")

            with patch("ai_project_ctl.web.actions.create_session") as create:
                with patch("ai_project_ctl.web.actions.run_until_blocker") as run_until:
                    result = WebActionExecutor(root, actor="tester").execute(
                        {
                            "action": "ui.checkpoint_commit",
                            "confirm": "yes",
                            "task": "APP-01",
                            "task_id": "TASK-001",
                        }
                    )

            status_after = subprocess.run(
                ["git", "status", "--short", "--untracked-files=all"],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            tasks_state = json.loads(
                (root / "AI_PROJECT" / "state" / "tasks.json").read_text(
                    encoding="utf-8"
                )
            )

        create.assert_not_called()
        run_until.assert_not_called()
        payload = result.to_dict()
        data = payload["result"]["data"]
        self.assertTrue(result.ok)
        self.assertFalse(data["not_run"])
        self.assertEqual(data["task_ref"], "APP-01")
        self.assertEqual(data["task_id"], "TASK-001")
        self.assertEqual(data["selected_task"], "APP-01 (TASK-001)")
        self.assertEqual(data["outcome"], "checkpoint_commit_created")
        self.assertRegex(data["commit_hash"], r"^[0-9a-f]{40}$")
        self.assertIn("dirty.txt", data["dirty_files"])
        self.assertIn(
            "Run selected task APP-01 (TASK-001) again.",
            payload["result"]["next_actions"],
        )
        self.assertEqual(
            data["next_action"],
            "Run selected task APP-01 (TASK-001) again.",
        )
        self.assertEqual(tasks_state["tasks"][0]["status"], "ready")
        self.assertEqual(status_after.stdout, "")
        command_vectors = [item["command"] for item in data["commands"]]
        self.assertIn(["git", "add", "-A"], command_vectors)
        self.assertIn(
            ["git", "commit", "-m", "Checkpoint before Web Run: APP-01"],
            command_vectors,
        )
        body = render_action_result(result)
        self.assertIn("Selected Task", body)
        self.assertIn("APP-01 (TASK-001)", body)
        self.assertIn("Run selected task APP-01 (TASK-001) again.", body)

    def test_pipeline_run_action_requires_confirmation(self):
        with patch("ai_project_ctl.web.actions.subprocess.run") as run:
            with self.assertRaises(WebActionError) as raised:
                WebActionExecutor("/tmp/project", actor="tester").execute(
                    {
                        "action": "pipeline.run_next",
                        "session_id": "PSESS-001",
                    }
                )

        self.assertEqual(raised.exception.code, "WEB_ACTION_CONFIRMATION_REQUIRED")
        run.assert_not_called()

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

    def test_pipeline_action_result_panel_shows_blockers_refs_and_side_effects(self):
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps(
                {
                    "ok": True,
                    "command": "pipeline.run_until_blocker",
                    "domain": "pipeline",
                    "message": "TOKEN_BUDGET_FAILURE: Token Budget Gate failed.",
                    "data": {
                        "session_id": "PSESS-001",
                        "session_href": "/pipeline/sessions/PSESS-001",
                        "stop_code": "TOKEN_BUDGET_FAILURE",
                        "stop_reason": "Token Budget Gate failed.",
                        "current_task_id": "TASK-064",
                        "current_step": "run_next",
                        "current_step_status": "blocked",
                        "blockers": [
                            {
                                "code": "TOKEN_BUDGET_FAILURE",
                                "reason": "Token Budget Gate failed.",
                            }
                        ],
                        "completed_tasks": [],
                        "changed_tasks": ["TASK-064"],
                        "requested_changes": [],
                        "accepted_changes": ["CHG-047"],
                        "report_ids": ["RPT-001"],
                        "review_ids": ["REV-001"],
                        "commits": ["abc123"],
                        "side_effects": [
                            {
                                "ok": True,
                                "command": "pipeline.run_next",
                                "message": "Stopped on token gate.",
                            }
                        ],
                    },
                    "changed_files": ["AI_PROJECT/state/pipeline_sessions.json"],
                    "generated_files": ["AI_PROJECT/generated/PIPELINE_STATUS.md"],
                    "owner_action_required": "Review the blocked pipeline session.",
                }
            )
            + "\n",
            stderr="",
        )

        with patch("ai_project_ctl.web.actions.subprocess.run", return_value=completed_process):
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "pipeline.run_until_blocker",
                    "confirm": "yes",
                    "session_id": "PSESS-001",
                }
            )

        body = render_action_result(result)

        self.assertIn("Pipeline Result", body)
        self.assertIn('href="/pipeline/sessions/PSESS-001"', body)
        self.assertIn("TOKEN_BUDGET_FAILURE", body)
        self.assertIn("Blockers", body)
        self.assertIn("Pipeline References", body)
        self.assertIn("RPT-001", body)
        self.assertIn("REV-001", body)
        self.assertIn("abc123", body)
        self.assertIn("pipeline.run_next", body)
        self.assertIn("AI_PROJECT/generated/PIPELINE_STATUS.md", body)
        self.assertIn("Review the blocked pipeline session.", body)

    def test_pipeline_action_result_panel_renders_no_executable_task_as_not_run(self):
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps(
                {
                    "ok": True,
                    "command": "pipeline.run_until_blocker",
                    "domain": "pipeline",
                    "message": "NO_EXECUTABLE_TASK: No executable task is available.",
                    "data": {
                        "session_id": "PSESS-EMPTY",
                        "session_href": "/pipeline/sessions/PSESS-EMPTY",
                        "session_status": "blocked",
                        "phase_status": "blocked",
                        "stop_code": "NO_EXECUTABLE_TASK",
                        "stop_reason": "No executable task is available in the selected queue.",
                        "blocked_by": "NO_EXECUTABLE_TASK",
                        "next_action": "Create or unblock a ready task, then rerun prepare.",
                    },
                    "owner_action_required": "Create or unblock a ready task, then rerun prepare.",
                }
            )
            + "\n",
            stderr="",
        )

        with patch("ai_project_ctl.web.actions.subprocess.run", return_value=completed_process):
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "pipeline.run_until_blocker",
                    "confirm": "yes",
                    "session_id": "PSESS-EMPTY",
                }
            )

        body = render_action_result(result)

        self.assertIn('class="panel action-result action-result-warn"', body)
        self.assertIn('<span class="badge warn">NOT RUN</span>', body)
        self.assertNotIn('<span class="badge pass">PASS</span>', body)
        self.assertIn("NO_EXECUTABLE_TASK", body)
        self.assertIn("No executable task is available in the selected queue.", body)
        self.assertIn("Create or unblock a ready task, then rerun prepare.", body)

    def test_pipeline_action_result_panel_renders_commit_readiness_as_commit_blocked(self):
        next_action = "Task is done, but local commit is blocked by commit readiness."
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps(
                {
                    "ok": True,
                    "command": "pipeline.run_until_blocker",
                    "domain": "pipeline",
                    "message": "COMMIT_READINESS_FAILED: local commit is blocked.",
                    "data": {
                        "session_id": "PSESS-COMMIT",
                        "session_href": "/pipeline/sessions/PSESS-COMMIT",
                        "session_status": "blocked",
                        "phase_status": "blocked",
                        "stop_code": "COMMIT_READINESS_FAILED",
                        "stop_reason": "Machine Review FAIL blocks local commit.",
                        "blocked_by": "COMMIT_READINESS_FAILED",
                        "next_action": next_action,
                        "commit_status": "blocked",
                        "commit_code": "COMMIT_READINESS_FAILED",
                    },
                    "next_actions": [next_action],
                }
            )
            + "\n",
            stderr="",
        )

        with patch("ai_project_ctl.web.actions.subprocess.run", return_value=completed_process):
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "pipeline.run_until_blocker",
                    "confirm": "yes",
                    "session_id": "PSESS-COMMIT",
                }
            )

        body = render_action_result(result)

        self.assertIn('class="panel action-result action-result-warn"', body)
        self.assertIn('<span class="badge warn">COMMIT BLOCKED</span>', body)
        self.assertNotIn('<span class="badge pass">PASS</span>', body)
        self.assertIn("COMMIT_READINESS_FAILED", body)
        self.assertIn("Machine Review FAIL blocks local commit.", body)
        self.assertIn(next_action, body)

    def test_pipeline_action_result_panel_keeps_completed_run_as_pass(self):
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps(
                {
                    "ok": True,
                    "command": "pipeline.run_until_blocker",
                    "domain": "pipeline",
                    "message": "QUEUE_COMPLETE: Selected queue completed.",
                    "data": {
                        "session_id": "PSESS-DONE",
                        "session_href": "/pipeline/sessions/PSESS-DONE",
                        "session_status": "completed",
                        "stop_code": "QUEUE_COMPLETE",
                        "stop_reason": "Selected queue completed.",
                    },
                }
            )
            + "\n",
            stderr="",
        )

        with patch("ai_project_ctl.web.actions.subprocess.run", return_value=completed_process):
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "pipeline.run_until_blocker",
                    "confirm": "yes",
                    "session_id": "PSESS-DONE",
                }
            )

        body = render_action_result(result)

        self.assertIn('class="panel action-result action-result-pass"', body)
        self.assertIn('<span class="badge pass">PASS</span>', body)
        self.assertIn("QUEUE_COMPLETE", body)

    def test_pipeline_action_result_panel_treats_committed_close_as_pass(self):
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps(
                {
                    "ok": True,
                    "command": "pipeline.run_until_blocker",
                    "domain": "pipeline",
                    "message": "MAX_STEPS_REACHED: Batch runner reached max_steps 7.",
                    "data": {
                        "session_id": "PSESS-COMMITTED",
                        "session_href": "/pipeline/sessions/PSESS-COMMITTED",
                        "session_status": "stopped",
                        "stop_code": "MAX_STEPS_REACHED",
                        "stop_reason": "Batch runner reached max_steps 7.",
                        "close_status": {
                            "outcome": "closed_with_local_commit",
                            "commit_status": "pass",
                            "commit_code": "LOCAL_COMMIT_CREATED",
                            "commit_hash": "abc1234deadbeef",
                        },
                    },
                }
            )
            + "\n",
            stderr="",
        )

        with patch("ai_project_ctl.web.actions.subprocess.run", return_value=completed_process):
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "pipeline.run_until_blocker",
                    "confirm": "yes",
                    "session_id": "PSESS-COMMITTED",
                }
            )

        body = render_action_result(result)

        self.assertIn('class="panel action-result action-result-pass"', body)
        self.assertIn('<span class="badge pass">PASS</span>', body)
        self.assertNotIn('<span class="badge warn">STOPPED</span>', body)
        self.assertIn("abc1234deadbeef", body)

    def test_pipeline_action_result_hides_recovered_close_warnings_from_warning_panel(self):
        recovered_warning = {
            "code": "WORKFLOW_NON_BLOCKING_STEP_FAILED",
            "message": (
                "Non-blocking workflow step reported a warning: "
                "Check generated context output"
            ),
            "details": {
                "step": "context_generated",
                "command_name": "contextctl.check-generated",
                "returncode": 1,
            },
        }
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps(
                {
                    "ok": True,
                    "command": "pipeline.run_next",
                    "domain": "pipeline",
                    "message": "Close passed.",
                    "warnings": [],
                    "data": {
                        "session_id": "PSESS-RECOVERED",
                        "dispatched_phase": "close",
                        "phase_status": "passed",
                        "phase_result": {
                            "phase": "close",
                            "status": "passed",
                            "reason": "Close passed.",
                            "next_action": "Review completed session.",
                            "artifacts": {
                                "context_refresh": {"ok": True},
                                "close_workflow": {
                                    "warnings": [recovered_warning],
                                },
                                "recovered_close_warnings": [
                                    {
                                        "code": "CLOSE_RECOVERED_NON_BLOCKING_WARNING",
                                        "recovered_by": "pipeline.close.context_refresh",
                                        "source_command": "pipeline.review_close_policy",
                                        "warning": recovered_warning,
                                    }
                                ],
                            },
                        },
                    },
                }
            )
            + "\n",
            stderr="",
        )

        with patch("ai_project_ctl.web.actions.subprocess.run", return_value=completed_process):
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "pipeline.run_next",
                    "confirm": "yes",
                    "session_id": "PSESS-RECOVERED",
                }
            )

        body = render_action_result(result)

        self.assertNotIn("<h3>Warnings</h3>", body)
        self.assertIn("CLOSE_RECOVERED_NON_BLOCKING_WARNING", body)
        self.assertIn("contextctl.check-generated", body)

    def test_pipeline_action_result_keeps_unrecovered_close_warnings_visible(self):
        completed_process = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps(
                {
                    "ok": True,
                    "command": "pipeline.run_next",
                    "domain": "pipeline",
                    "message": "Close blocked.",
                    "warnings": [
                        {
                            "code": "WORKFLOW_NON_BLOCKING_STEP_FAILED",
                            "message": (
                                "Non-blocking workflow step reported a warning: "
                                "Check generated context output"
                            ),
                            "details": {
                                "step": "context_generated",
                                "command_name": "contextctl.check-generated",
                                "returncode": 1,
                            },
                        }
                    ],
                    "data": {
                        "session_id": "PSESS-UNRECOVERED",
                        "dispatched_phase": "close",
                        "phase_status": "blocked",
                        "blocked_by": "CLOSE_CONTEXT_REFRESH_FAILED",
                        "phase_result": {
                            "phase": "close",
                            "status": "blocked",
                            "reason": "Close blocked.",
                            "next_action": "Resolve context refresh.",
                            "artifacts": {
                                "blocked_by": "CLOSE_CONTEXT_REFRESH_FAILED",
                                "context_refresh": {"ok": False},
                            },
                        },
                    },
                }
            )
            + "\n",
            stderr="",
        )

        with patch("ai_project_ctl.web.actions.subprocess.run", return_value=completed_process):
            result = WebActionExecutor("/tmp/project", actor="tester").execute(
                {
                    "action": "pipeline.run_next",
                    "confirm": "yes",
                    "session_id": "PSESS-UNRECOVERED",
                }
            )

        body = render_action_result(result)

        self.assertIn("<h3>Warnings</h3>", body)
        self.assertIn("WORKFLOW_NON_BLOCKING_STEP_FAILED", body)
        self.assertIn("Check generated context output", body)

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


def pipeline_detail_state(
    *,
    status,
    step_status,
    finished_at,
    current_step_status,
    stop_reason="",
    next_action="",
    steps=None,
    gate_outcomes=None,
    phase_history=None,
):
    if gate_outcomes is None:
        gate_outcomes = [
            pipeline_detail_gate("token_budget_gate", "pass"),
            pipeline_detail_gate("codex_execution_adapter", "warn"),
        ]
    if steps is None:
        steps = [
            {
                "name": "run_next",
                "status": step_status,
                "started_at": "2026-06-20T13:11:00Z",
                "finished_at": finished_at,
                "task_id": "TASK-078",
                "gate_outcomes": [
                    pipeline_detail_gate("token_budget_gate", "pass"),
                    pipeline_detail_gate("codex_execution_adapter", "warn"),
                ],
                "result": {},
                "stop_reason": stop_reason,
                "audit_event_ids": ["EVT-100", "EVT-101"],
            }
        ]
    state = {
        "schema_version": 1,
        "revision": 4,
        "created_at": "2026-06-20T13:10:00Z",
        "updated_at": "2026-06-20T13:25:00Z",
        "current_session_id": "PSESS-020",
        "sessions": [
            {
                "id": "PSESS-020",
                "status": status,
                "selected_queue": {
                    "selection": "ready_queue",
                    "task_refs": ["PIPE-27"],
                    "epic_ids": ["EPIC-007"],
                    "statuses": ["ready"],
                    "max_tasks": 1,
                    "order_by": "execution",
                    "include_blocked_tasks": False,
                },
                "policy_snapshot": {
                    "name": "supervised_executable_autoclose",
                    "queue": {
                        "selection": "ready_queue",
                        "max_tasks": 1,
                        "include_blocked_tasks": False,
                    },
                    "evolution": {
                        "create_missing_change": False,
                        "approve_linked_change": False,
                        "accept_linked_change": False,
                        "require_approved_change_for_execution": True,
                        "owner_approve_required_changes_for_session": False,
                        "owner_approval_note": "",
                    },
                    "token_budget": {
                        "require_gate_pass": True,
                        "max_prompt_tokens": 32000,
                        "max_context_tokens": 24000,
                        "min_remaining_tokens": 6000,
                        "reserved_output_tokens": 0,
                    },
                    "codex": {
                        "mode": "run_codex",
                        "require_human_selected_policy": True,
                        "adapter_mode": "local_command",
                        "local_command": ["codex", "exec"],
                        "command_allowlist": ["codex exec"],
                        "timeout_sec": 300,
                        "require_report": True,
                    },
                    "review": {
                        "require_machine_review": True,
                        "required_machine_outcome": "pass",
                        "require_codex_review": True,
                        "required_codex_decision": "approve",
                    },
                    "rework": {
                        "allow_rework_loop": True,
                        "max_rework_attempts": 1,
                        "require_owner_decision_for_rework": True,
                    },
                    "batch": {"max_steps": 5, "max_failures": 1},
                    "closure": {
                        "auto_close_task": True,
                        "owner_approval_note": "Owner approved auto-close.",
                    },
                    "commit": {
                        "create_local_commit": False,
                        "mode": "disabled",
                        "require_commit_readiness": False,
                        "allow_push": False,
                        "allow_merge": False,
                    },
                },
                "current_task_id": "TASK-078",
                "current_task_ref": "PIPE-27",
                "current_step": "run_next",
                "current_step_status": current_step_status,
                "attempt_counters": {"steps": 1, "tasks": 1, "rework": 0},
                "gate_outcomes": gate_outcomes,
                "steps": steps,
                "linked_change_ids": ["CHG-061"],
                "report_ids": ["RPT-001"],
                "review_ids": ["REV-001"],
                "commit_ids": ["abc1234"],
                "audit_event_ids": ["EVT-100", "EVT-101"],
                "stop_reason": stop_reason,
                "next_action": next_action,
                "created_at": "2026-06-20T13:10:00Z",
                "updated_at": "2026-06-20T13:25:00Z",
                "started_at": "2026-06-20T13:11:00Z",
                "finished_at": finished_at,
            }
        ],
    }
    if phase_history is not None:
        session = state["sessions"][0]
        session["phase_history"] = phase_history
        if phase_history:
            current_phase = phase_history[-1]
            session["current_phase"] = current_phase.get("phase") or ""
            session["current_phase_status"] = current_phase.get("status") or ""
            if not session.get("next_action"):
                session["next_action"] = current_phase.get("next_action") or ""
    return state


def report_missing_pipeline_state(stdout="", stdout_log=""):
    stdout = stdout or (
        "Summary:\n"
        "- Recovered report can be submitted.\n"
        "Changed files:\n"
        "- ai_project_ctl/web/actions.py\n"
        "Checks:\n"
        "- focused web tests passed\n"
    )
    runtime_logs = {}
    if stdout_log:
        runtime_logs = {
            "stdout": {
                "path": stdout_log,
                "start_offset": 0,
                "end_offset": len(stdout.encode("utf-8")),
                "bytes": len(stdout.encode("utf-8")),
            }
        }
    return pipeline_detail_state(
        status="blocked",
        step_status="planned",
        finished_at="",
        current_step_status="blocked",
        stop_reason="No task report state exists for selected task.",
        next_action="Submit a report for TASK-078, then rerun collect-report.",
        steps=[],
        gate_outcomes=[],
        phase_history=[
            {
                "phase": "execute",
                "status": "passed",
                "reason": "Codex completed without structured report.",
                "next_action": "Run pipeline phase collect-report.",
                "artifacts": {
                    "runtime_logs": runtime_logs,
                    "execute_evidence": {
                        "code": "CODEX_ADAPTER_REPORT_MISSING",
                        "reason": "structured_execution_report_missing",
                        "stdout_ref": "captured:stdout:sha256:abc",
                        "stdout_snippet": stdout,
                        "runtime_logs": runtime_logs,
                    },
                    "adapter_summary": {
                        "code": "CODEX_ADAPTER_REPORT_MISSING",
                        "stdout_ref": "captured:stdout:sha256:abc",
                        "stdout_snippet": stdout,
                        "runtime_logs": runtime_logs,
                    },
                },
                "changed_files": [],
                "generated_files": [],
                "events": ["EVT-202"],
            },
            {
                "phase": "collect_report",
                "status": "blocked",
                "reason": "No task report state exists for selected task.",
                "next_action": "Submit a report for TASK-078, then rerun collect-report.",
                "artifacts": {
                    "blocked_by": "REPORT_MISSING",
                    "session_id": "PSESS-020",
                    "task_id": "TASK-078",
                },
                "changed_files": [],
                "generated_files": [],
                "events": ["EVT-203"],
            },
        ],
    )


def pipeline_detail_gate(name, status):
    details = {
        "policy": "supervised_executable_autoclose",
        "selected_task": {
            "id": "TASK-078",
            "ref": "PIPE-27",
            "legacy_id": "TASK-078",
            "status": "ready",
            "title": "Persistent session detail page",
            "reasons": [
                {"code": "status_not_executable", "detail": "example skipped task"}
            ],
        },
        "queue_counts": {
            "executable": 1,
            "waiting": 0,
            "blocked": 0,
            "skipped": 1,
        },
        "change_gate": {"required": True, "change_ids": ["CHG-061"]},
        "token_budget": {
            "prompt_path": "AI_PROJECT/generated/CODEX_PROMPT.md",
            "context_pack": {"path": "AI_PROJECT/generated/CONTEXT_PACK.md"},
        },
    }
    if name == "codex_execution_adapter":
        details["adapter"] = {
            "status": "blocked",
            "code": "CODEX_ADAPTER_REPORT_MISSING",
            "stdout_ref": "captured:stdout:sha256:abc",
            "stderr_ref": "captured:stderr:sha256:def",
            "stdout_snippet": "stdout diagnostic",
            "stderr_snippet": "stderr diagnostic",
            "prompt_path": "AI_PROJECT/generated/CODEX_PROMPT.md",
            "report_id": "RPT-001",
        }
        details["changed_files"] = ["ai_project_ctl/web/server.py"]
        details["generated_files"] = ["AI_PROJECT/generated/PIPELINE_STATUS.md"]
    return {
        "name": name,
        "status": status,
        "recorded_at": "2026-06-20T13:20:00Z",
        "details": details,
    }


def pipeline_detail_event(event_id, session_id, command, gate):
    return {
        "event_id": event_id,
        "timestamp": "2026-06-20T13:20:00Z",
        "actor": "tester",
        "command": command,
        "entity_type": "pipeline_session",
        "entity_id": session_id,
        "revision_before": 3,
        "revision_after": 4,
        "payload": {
            "session_id": session_id,
            "step": {"name": "run_next", "status": "running"},
            "gate_outcome": gate,
        },
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
    pipeline=None,
    pipeline_events=None,
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
    if pipeline is not None:
        (state_dir / "pipeline_sessions.json").write_text(
            json.dumps(pipeline),
            encoding="utf-8",
        )
    if pipeline_events is not None:
        events_dir = root / "AI_PROJECT" / "events"
        events_dir.mkdir(parents=True, exist_ok=True)
        (events_dir / "pipeline-events.jsonl").write_text(
            "".join(json.dumps(event) + "\n" for event in pipeline_events),
            encoding="utf-8",
        )


def post_forms(body):
    return re.findall(
        r'<form\b(?=[^>]*method="post")[^>]*>.*?</form>',
        body,
        flags=re.DOTALL,
    )


def summary_grid_metrics(body):
    match = re.search(
        r'<section class="summary-grid"[^>]*>(.*?)</section>',
        body,
        flags=re.DOTALL,
    )
    if not match:
        return {}
    return {
        label: value
        for label, value in re.findall(
            r"<span>(.*?)</span><strong>(.*?)</strong>",
            match.group(1),
            flags=re.DOTALL,
        )
    }


def assert_no_restricted_git_actions(testcase, body):
    for snippet in (
        'name="action" value="git.',
        'name="action" value="project.git',
        "git reset",
        "git clean",
        "git checkout",
        "git restore",
        "git push",
        "git merge",
        "git rebase",
        "reset --hard",
        "clean -fd",
        "checkout --",
        "restore --staged",
        "push origin",
    ):
        testcase.assertNotIn(snippet, body.lower())


def write_ui_settings(root, payload):
    path = ui_settings_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


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

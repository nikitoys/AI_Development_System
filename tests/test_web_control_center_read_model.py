import json
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.web.read_model import ReadOnlyProjectModel, owner_action_queue


TASK_QUEUE_ROW_FIELDS = (
    "task_ref",
    "status",
    "title",
    "next_label",
    "primary_action",
    "detail_key",
)


class WebControlCenterReadModelTests(unittest.TestCase):
    def test_owner_action_queue_groups_available_task_actions(self):
        def queue_task(ref, status, *, label="", action=""):
            task = {
                "id": "TASK-{}".format(ref),
                "ref": ref,
                "status": status,
                "title": ref,
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

        queue = owner_action_queue(
            [
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
                {
                    "id": "TASK-MULTI-01",
                    "ref": "MULTI-01",
                    "status": "ready",
                    "title": "Multiple available actions",
                    "pipeline_hints": {
                        "next_actions": ["Approve Change"],
                        "actions": [
                            {
                                "label": "Prepare for Codex",
                                "action": "task.prepare_for_codex",
                                "available": True,
                                "reason": "",
                            },
                            {
                                "label": "Approve Change",
                                "action": "evolution.approve_change",
                                "available": True,
                                "reason": "",
                            },
                        ],
                    },
                },
                queue_task(
                    "DEFER-01",
                    "deferred",
                    label="Run",
                    action="ui.run_selected_task",
                ),
            ],
            [],
            current_task={"id": "TASK-CUR-01", "ref": "CUR-01"},
            pipeline={},
        )
        refs_by_group = {
            key: {str(item.get("ref") or "") for item in queue[key]}
            for key in ("ready_to_run", "needs_decision", "current", "blocked")
        }

        self.assertEqual(refs_by_group["ready_to_run"], {"PREP-01", "RUN-01"})
        self.assertEqual(
            refs_by_group["needs_decision"],
            {"DECIDE-01", "REVIEW-01", "MULTI-01"},
        )
        self.assertEqual(refs_by_group["current"], {"CUR-01", "PROG-01"})
        self.assertEqual(refs_by_group["blocked"], {"BLOCK-01"})
        self.assertNotIn("DEFER-01", set().union(*refs_by_group.values()))
        multi_item = next(
            item for item in queue["needs_decision"] if item["ref"] == "MULTI-01"
        )
        self.assertEqual(multi_item["primary_next_action"], "Approve Change")
        self.assertEqual(multi_item["action"], "evolution.approve_change")

    def test_task_queue_rows_are_compact_with_keyed_details(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(
                root,
                tasks=[
                    {
                        "id": "TASK-001",
                        "ref": "PLAN-01",
                        "legacy_id": "LEGACY-001",
                        "status": "planned",
                        "title": "Plan compact row",
                        "summary": "Create the first compact row.",
                        "scope": ["Expose compact task rows."],
                        "acceptance_criteria": ["Rows do not include full details."],
                        "verification_mode": "fast",
                        "verification_budget": "120 sec",
                        "allowed_files": ["ai_project_ctl/web/read_model.py"],
                        "epic_id": "EPIC-001",
                        "order": 1,
                    },
                    {
                        "id": "TASK-002",
                        "ref": "BLOCK-01",
                        "status": "blocked",
                        "title": "Blocked compact row",
                        "blockers": ["Waiting on Human Owner decision."],
                        "epic_id": "EPIC-001",
                        "order": 2,
                    },
                    {
                        "id": "TASK-003",
                        "ref": "CHG-01",
                        "status": "ready",
                        "title": "Linked Change compact row",
                        "summary": "Requires an approved Evolution Change.",
                        "epic_id": "EPIC-001",
                        "order": 3,
                    },
                ],
                changes=[
                    {
                        "id": "CHG-001",
                        "status": "approved",
                        "title": "Approve linked read model change",
                        "linked_tasks": ["TASK-003", "CHG-01"],
                    }
                ],
                task_reports={
                    "schema_version": 1,
                    "revision": 1,
                    "latest_by_task": {"TASK-003": "RPT-003"},
                    "reports": [
                        {
                            "id": "RPT-003",
                            "task_id": "TASK-003",
                            "task_ref": "CHG-01",
                            "submitted_at": "2026-06-27T18:00:00Z",
                            "report": {
                                "implementation_summary": "Updated read model.",
                                "generated_files": [
                                    "AI_PROJECT/generated/CODEX_STATUS.md"
                                ],
                                "checks": [],
                                "blockers": [],
                                "warnings": [],
                                "notes": [],
                            },
                        }
                    ],
                },
            )

            data = ReadOnlyProjectModel(root, actor="tester").dashboard()

        queue = data["task_queue"]
        rows_by_ref = {row["task_ref"]: row for row in queue["rows"]}

        self.assertEqual(queue["row_fields"], list(TASK_QUEUE_ROW_FIELDS))
        self.assertEqual(set(rows_by_ref), {"PLAN-01", "BLOCK-01", "CHG-01"})
        for row in queue["rows"]:
            self.assertEqual(set(row), set(TASK_QUEUE_ROW_FIELDS))
            self.assertNotIn("summary", row)
            self.assertNotIn("scope", row)
            self.assertNotIn("acceptance_criteria", row)
            self.assertNotIn("blockers", row)
            self.assertNotIn("health", row)
            self.assertNotIn("recent_events", row)

        planned_row = rows_by_ref["PLAN-01"]
        self.assertEqual(planned_row["next_label"], "Prepare for Codex")
        self.assertEqual(planned_row["primary_action"], "task.prepare_for_codex")

        details = queue["details_by_key"]
        planned_detail = details[planned_row["detail_key"]]
        self.assertEqual(details["TASK-001"], planned_detail)
        self.assertEqual(details["PLAN-01"], planned_detail)
        self.assertEqual(details["LEGACY-001"], planned_detail)
        self.assertEqual(planned_detail["summary"], "Create the first compact row.")
        self.assertEqual(planned_detail["scope"], ["Expose compact task rows."])
        self.assertEqual(
            planned_detail["acceptance_criteria"],
            ["Rows do not include full details."],
        )
        self.assertEqual(planned_detail["policy"]["verification_mode"], "fast")
        self.assertEqual(planned_detail["policy"]["verification_budget"], "120 sec")
        action_details = {
            action["action"]: action for action in planned_detail["actions"]
        }
        self.assertTrue(action_details["task.prepare_for_codex"]["available"])
        self.assertFalse(action_details["task.submit_for_review"]["available"])
        self.assertEqual(
            action_details["task.submit_for_review"]["reason"],
            "task status is planned",
        )

        blocked_detail = details["BLOCK-01"]
        self.assertEqual(rows_by_ref["BLOCK-01"]["next_label"], "Blocked")
        self.assertEqual(
            blocked_detail["blockers"],
            ["Waiting on Human Owner decision."],
        )
        self.assertEqual(blocked_detail["health"]["status"], "blocked")

        linked_detail = details["TASK-003"]
        self.assertEqual(linked_detail["linked_change"]["id"], "CHG-001")
        self.assertEqual(linked_detail["linked_change"]["status"], "approved")
        self.assertEqual(
            linked_detail["generated_files"],
            ["AI_PROJECT/generated/CODEX_STATUS.md"],
        )

        inventory_by_ref = {task["ref"]: task for task in data["tasks"]}
        self.assertIn("summary", inventory_by_ref["PLAN-01"])
        self.assertIn("pipeline_hints", inventory_by_ref["CHG-01"])

    def test_task_queue_detail_payload_uses_empty_values_for_missing_optional_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(
                root,
                tasks=[
                    {
                        "id": "TASK-010",
                        "ref": "MIN-01",
                        "status": "planned",
                        "title": "Minimal task",
                        "epic_id": "EPIC-001",
                    }
                ],
            )

            data = ReadOnlyProjectModel(root, actor="tester").dashboard()

        detail = data["task_queue"]["details_by_key"]["MIN-01"]

        self.assertEqual(detail["summary"], "")
        self.assertEqual(detail["scope"], [])
        self.assertEqual(detail["acceptance_criteria"], [])
        self.assertEqual(detail["blockers"], [])
        self.assertIsInstance(detail["actions"], list)
        self.assertEqual(detail["linked_change"], {})
        self.assertEqual(detail["linked_changes"], [])
        self.assertEqual(detail["generated_files"], [])
        self.assertEqual(detail["recent_events"], [])
        self.assertEqual(
            detail["policy"],
            {
                "verification_mode": "",
                "verification_budget": "",
                "allowed_slow_checks": False,
                "runtime_tracking": "",
                "owner_approved": False,
                "allowed_files": [],
                "out_of_scope": [],
            },
        )
        self.assertEqual(detail["health"]["status"], "ok")


def write_project_state(
    root: Path,
    *,
    tasks: list[dict],
    changes: list[dict] | None = None,
    task_reports: dict | None = None,
) -> None:
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "tasks.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "current_task_id": None,
                "tasks": tasks,
            }
        ),
        encoding="utf-8",
    )
    (state_dir / "plan.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "initiatives": [],
                "epics": [{"id": "EPIC-001", "status": "active", "order": 1}],
            }
        ),
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
    if task_reports is not None:
        (state_dir / "task_reports.json").write_text(
            json.dumps(task_reports),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()

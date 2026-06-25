import unittest

from ai_project_ctl.pipeline.policy import policy_preset
from ai_project_ctl.pipeline.ui_run import build_ui_run_selected_queue


class UIRunQueueTests(unittest.TestCase):
    def test_build_ui_run_selected_queue_with_internal_bypass_disabled(self):
        queue = build_ui_run_selected_queue(
            policy_preset("supervised"),
            "APP-01",
            confirmed=False,
            allow_internal_change_gate_bypass=False,
        )

        self.assertEqual(
            queue,
            {
                "selection": "ready_queue",
                "task_refs": ["APP-01"],
                "epic_ids": [],
                "statuses": [],
                "max_tasks": 1,
                "order_by": "selected",
                "include_blocked_tasks": False,
                "created_by_command": "ui.run",
                "ui_run_confirmed": False,
                "allow_internal_change_gate_bypass": False,
            },
        )

    def test_build_ui_run_selected_queue_with_internal_bypass_enabled(self):
        queue = build_ui_run_selected_queue(
            policy_preset("supervised"),
            "APP-01",
            confirmed=True,
            allow_internal_change_gate_bypass=True,
        )

        self.assertEqual(queue["created_by_command"], "ui.run")
        self.assertTrue(queue["ui_run_confirmed"])
        self.assertEqual(queue["task_refs"], ["APP-01"])
        self.assertEqual(queue["max_tasks"], 1)
        self.assertEqual(queue["order_by"], "selected")
        self.assertFalse(queue["include_blocked_tasks"])
        self.assertTrue(queue["allow_internal_change_gate_bypass"])


if __name__ == "__main__":
    unittest.main()

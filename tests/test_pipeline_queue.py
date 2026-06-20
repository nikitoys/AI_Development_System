import copy
import unittest

from ai_project_ctl.pipeline import (
    PipelinePolicy,
    QueuePlannerRequest,
    QueuePolicy,
    QueueSelection,
    preview_queue,
)


def plan_state():
    return {
        "initiatives": [
            {"id": "INIT-1", "status": "active"},
            {"id": "INIT-2", "status": "archived"},
        ],
        "epics": [
            {
                "id": "EPIC-1",
                "initiative_id": "INIT-1",
                "status": "planned",
                "order": 2,
                "key": "APP",
            },
            {
                "id": "EPIC-2",
                "initiative_id": "INIT-1",
                "status": "planned",
                "order": 1,
                "key": "CTL",
            },
            {
                "id": "EPIC-3",
                "initiative_id": "INIT-2",
                "status": "planned",
                "order": 3,
                "key": "OLD",
            },
        ],
    }


def task(
    task_id,
    *,
    ref,
    epic_id="EPIC-1",
    status="planned",
    priority=1,
    order=1,
    local_seq=1,
    depends_on=None,
):
    return {
        "id": task_id,
        "ref": ref,
        "uid": "uid_{}".format(task_id),
        "legacy_id": task_id,
        "aliases": [task_id],
        "title": "{} title".format(ref),
        "status": status,
        "epic_id": epic_id,
        "priority": priority,
        "order": order,
        "local_seq": local_seq,
        "depends_on": depends_on or [],
    }


def tasks_state(*tasks, current_task_id=None):
    return {
        "revision": 1,
        "current_task_id": current_task_id,
        "tasks": list(tasks),
    }


def ready_queue_policy(max_tasks=10):
    return PipelinePolicy(
        queue=QueuePolicy(
            selection=QueueSelection.READY_QUEUE,
            max_tasks=max_tasks,
            include_blocked_tasks=False,
        )
    )


class PipelineQueueTests(unittest.TestCase):
    def test_manual_empty_queue_has_no_next_task(self):
        preview = preview_queue(tasks_state(), plan_state())

        self.assertIsNone(preview.next_task)
        self.assertEqual(preview.items, ())

    def test_ready_queue_selects_first_executable_task(self):
        first = task("TASK-1", ref="APP-01", epic_id="EPIC-1", priority=2, local_seq=1)
        next_task = task("TASK-2", ref="CTL-01", epic_id="EPIC-2", priority=1, local_seq=1)

        preview = preview_queue(
            tasks_state(first, next_task),
            plan_state(),
            policy=ready_queue_policy(),
        )

        self.assertEqual(preview.next_task.id, "TASK-2")
        self.assertEqual([item.id for item in preview.executable], ["TASK-2", "TASK-1"])

    def test_dependency_blocked_task_waits_and_is_not_selected(self):
        dependency = task("TASK-1", ref="APP-01", status="in_progress")
        blocked = task(
            "TASK-2",
            ref="APP-02",
            depends_on=[{"task_id": "TASK-1", "type": "hard"}],
        )
        executable = task("TASK-3", ref="APP-03", local_seq=3)

        preview = preview_queue(
            tasks_state(dependency, blocked, executable),
            plan_state(),
            policy=ready_queue_policy(),
        )

        self.assertEqual(preview.next_task.id, "TASK-3")
        self.assertEqual([item.id for item in preview.waiting], ["TASK-2"])
        self.assertEqual(preview.waiting[0].reasons[0]["code"], "dependency_not_done")

    def test_parent_state_blocked_task_is_explained(self):
        blocked = task("TASK-1", ref="OLD-01", epic_id="EPIC-3")

        preview = preview_queue(
            tasks_state(blocked),
            plan_state(),
            policy=ready_queue_policy(),
        )

        self.assertIsNone(preview.next_task)
        self.assertEqual([item.id for item in preview.blocked], ["TASK-1"])
        self.assertEqual(
            preview.blocked[0].reasons[0]["code"],
            "parent_epic_not_executable",
        )

    def test_invalid_selected_ref_is_skipped(self):
        preview = preview_queue(
            tasks_state(task("TASK-1", ref="APP-01")),
            plan_state(),
            policy=ready_queue_policy(),
            request=QueuePlannerRequest(task_refs=("MISSING-99",)),
        )

        self.assertIsNone(preview.next_task)
        self.assertEqual(preview.skipped[0].selected_ref, "MISSING-99")
        self.assertEqual(preview.skipped[0].reasons[0]["code"], "task_ref_not_found")

    def test_current_task_conflict_blocks_other_tasks(self):
        current = task("TASK-1", ref="APP-01", status="in_progress")
        candidate = task("TASK-2", ref="APP-02", local_seq=2)

        preview = preview_queue(
            tasks_state(current, candidate, current_task_id="TASK-1"),
            plan_state(),
            policy=ready_queue_policy(),
        )

        self.assertIsNone(preview.next_task)
        self.assertEqual([item.id for item in preview.blocked], ["TASK-2"])
        self.assertEqual(preview.blocked[0].reasons[-1]["code"], "current_task_conflict")

    def test_policy_max_tasks_skips_overflow(self):
        first = task("TASK-1", ref="APP-01", local_seq=1)
        second = task("TASK-2", ref="APP-02", local_seq=2)

        preview = preview_queue(
            tasks_state(first, second),
            plan_state(),
            policy=ready_queue_policy(max_tasks=1),
        )

        self.assertEqual(preview.next_task.id, "TASK-1")
        self.assertEqual([item.id for item in preview.executable], ["TASK-1"])
        self.assertEqual([item.id for item in preview.skipped], ["TASK-2"])
        self.assertEqual(preview.skipped[0].reasons[0]["code"], "policy_max_tasks_exceeded")

    def test_status_and_epic_filters_skip_non_matching_selected_tasks(self):
        first = task("TASK-1", ref="APP-01", epic_id="EPIC-1", status="planned")
        second = task("TASK-2", ref="CTL-01", epic_id="EPIC-2", status="ready")

        preview = preview_queue(
            tasks_state(first, second),
            plan_state(),
            request=QueuePlannerRequest(
                task_refs=("APP-01", "CTL-01"),
                epic_ids=("EPIC-2",),
                statuses=("ready",),
                max_tasks=2,
            ),
        )

        self.assertEqual(preview.next_task.id, "TASK-2")
        self.assertEqual([item.id for item in preview.skipped], ["TASK-1"])
        self.assertEqual(
            [reason["code"] for reason in preview.skipped[0].reasons],
            ["epic_filter_mismatch", "status_filter_mismatch"],
        )

    def test_planner_does_not_mutate_input_state(self):
        state = tasks_state(task("TASK-1", ref="APP-01"))
        original = copy.deepcopy(state)

        preview_queue(state, plan_state(), policy=ready_queue_policy())

        self.assertEqual(state, original)

    def test_selected_order_is_deterministic_when_requested(self):
        first = task("TASK-1", ref="APP-01", local_seq=1)
        second = task("TASK-2", ref="APP-02", local_seq=2)

        preview = preview_queue(
            tasks_state(first, second),
            plan_state(),
            request=QueuePlannerRequest(
                task_refs=("APP-02", "APP-01"),
                max_tasks=2,
                order_by="selected",
            ),
        )

        self.assertEqual([item.id for item in preview.executable], ["TASK-2", "TASK-1"])
        self.assertEqual(preview.next_task.id, "TASK-2")


if __name__ == "__main__":
    unittest.main()

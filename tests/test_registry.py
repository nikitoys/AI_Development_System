import unittest

from ai_project_ctl.core.registry import (
    CommandDescriptor,
    CommandKind,
    CommandRegistry,
    RegistryError,
    command_describe,
    command_list,
    default_command_registry,
)


class RegistryTests(unittest.TestCase):
    def test_default_registry_lists_required_commands(self):
        registry = default_command_registry()

        names = registry.list_command_names()

        self.assertIn("task.list", names)
        self.assertIn("task.show", names)
        self.assertIn("task.create", names)
        self.assertIn("task.import", names)
        self.assertIn("task.report.submit", names)
        self.assertIn("task.prepare_for_codex", names)
        self.assertIn("task.refresh_execution_context", names)
        self.assertIn("task.submit_for_review", names)
        self.assertIn("task.close_reviewed", names)
        self.assertIn("task.request_changes", names)
        self.assertIn("evolution.create_for_task", names)
        self.assertIn("evolution.approve_change", names)
        self.assertIn("evolution.move_to_review", names)
        self.assertIn("evolution.accept_change", names)
        self.assertIn("epic.close_if_complete", names)
        self.assertIn("task.transition", names)
        self.assertIn("current.set", names)
        self.assertIn("current.clear", names)
        self.assertIn("epic.list", names)
        self.assertIn("change.create", names)
        self.assertIn("context.build", names)
        self.assertIn("codex.prompt.build", names)
        self.assertIn("pipeline.status", names)
        self.assertIn("pipeline.validate", names)
        self.assertIn("pipeline.render", names)
        self.assertIn("pipeline.check_generated", names)
        self.assertIn("pipeline.session.create", names)
        self.assertIn("pipeline.run_next", names)
        self.assertIn("pipeline.step.start", names)
        self.assertIn("pipeline.step.result", names)
        self.assertIn("pipeline.session.stop", names)
        self.assertIn("pipeline.session.complete", names)
        self.assertIn("docs.render", names)
        self.assertIn("project.doctor", names)
        self.assertIn("project.protected_check", names)
        self.assertIn("project.render", names)
        self.assertIn("web.serve", names)
        self.assertIn("command.list", names)
        self.assertIn("command.describe", names)
        self.assertIn("workflow.list", names)
        self.assertIn("workflow.describe", names)
        self.assertEqual(names, sorted(names))

    def test_describe_exposes_command_metadata(self):
        descriptor = command_describe("task.transition")

        self.assertEqual(descriptor["name"], "task.transition")
        self.assertEqual(descriptor["domain"], "task")
        self.assertEqual(descriptor["kind"], "write")
        self.assertEqual(descriptor["availability"], "implemented")
        self.assertTrue(descriptor["read_write"]["mutates_state"])
        self.assertTrue(descriptor["read_write"]["writes_events"])
        self.assertTrue(descriptor["read_write"]["renders_generated"])
        self.assertTrue(descriptor["read_write"]["validates"])
        self.assertIn("AI_PROJECT/state/tasks.json", descriptor["writes_state"])
        self.assertIn("AI_PROJECT/events/task-events.jsonl", descriptor["event_logs"])
        self.assertIn("json", descriptor["output"]["formats"])
        self.assertEqual(
            [argument["name"] for argument in descriptor["arguments"]],
            ["task_id", "to"],
        )

    def test_current_set_is_registered_as_controlled_write(self):
        descriptor = command_describe("current.set")

        self.assertEqual(descriptor["domain"], "current")
        self.assertEqual(descriptor["kind"], "write")
        self.assertTrue(descriptor["read_write"]["mutates_state"])
        self.assertTrue(descriptor["read_write"]["writes_events"])
        self.assertTrue(descriptor["read_write"]["renders_generated"])
        self.assertIn("AI_PROJECT/state/tasks.json", descriptor["writes_state"])

    def test_task_workflow_is_registered_as_confirmed_write(self):
        descriptor = command_describe("task.prepare_for_codex")

        self.assertEqual(descriptor["domain"], "task")
        self.assertEqual(descriptor["kind"], "write")
        self.assertTrue(descriptor["read_write"]["mutates_state"])
        self.assertTrue(descriptor["read_write"]["writes_events"])
        self.assertTrue(descriptor["read_write"]["renders_generated"])
        self.assertEqual(descriptor["lock_scope"], "workflow")
        self.assertIn("Explicit confirmation", descriptor["owner_approval"])

    def test_task_create_is_registered_as_create_only_workflow(self):
        descriptor = command_describe("task.create")

        argument_names = [argument["name"] for argument in descriptor["arguments"]]

        self.assertEqual(descriptor["domain"], "task")
        self.assertEqual(descriptor["kind"], "write")
        self.assertEqual(descriptor["lock_scope"], "workflow")
        self.assertIn("depends_on", argument_names)
        self.assertIn("confirm", argument_names)
        self.assertIn("not auto-started", descriptor["owner_approval"])
        self.assertIn("Create-only", " ".join(descriptor["notes"]))

    def test_task_import_is_registered_as_confirmed_bulk_workflow(self):
        descriptor = command_describe("task.import")
        argument_names = [argument["name"] for argument in descriptor["arguments"]]

        self.assertEqual(descriptor["domain"], "task")
        self.assertEqual(descriptor["kind"], "write")
        self.assertEqual(descriptor["lock_scope"], "workflow")
        self.assertTrue(descriptor["dry_run"])
        self.assertIn("text", argument_names)
        self.assertIn("confirm", argument_names)
        self.assertIn("Preview is allowed", descriptor["owner_approval"])
        self.assertIn("Validates all Epic", " ".join(descriptor["notes"]))

    def test_task_report_submit_is_registered_as_separate_report_write(self):
        descriptor = command_describe("task.report.submit")
        argument_names = [argument["name"] for argument in descriptor["arguments"]]

        self.assertEqual(descriptor["domain"], "task")
        self.assertEqual(descriptor["kind"], "write")
        self.assertTrue(descriptor["read_write"]["mutates_state"])
        self.assertTrue(descriptor["read_write"]["writes_events"])
        self.assertFalse(descriptor["read_write"]["renders_generated"])
        self.assertIn("AI_PROJECT/state/task_reports.json", descriptor["writes_state"])
        self.assertNotIn("AI_PROJECT/state/tasks.json", descriptor["writes_state"])
        self.assertIn("AI_PROJECT/events/task-report-events.jsonl", descriptor["event_logs"])
        self.assertEqual(argument_names, ["task", "file", "confirm"])
        self.assertIn("do not approve", descriptor["owner_approval"])
        self.assertIn("Does not modify tasks.json", " ".join(descriptor["notes"]))

    def test_evolution_create_for_task_is_registered_without_approval(self):
        descriptor = command_describe("evolution.create_for_task")

        self.assertEqual(descriptor["domain"], "evolution")
        self.assertEqual(descriptor["kind"], "write")
        self.assertTrue(descriptor["read_write"]["mutates_state"])
        self.assertTrue(descriptor["read_write"]["writes_events"])
        self.assertTrue(descriptor["read_write"]["renders_generated"])
        self.assertIn("AI_PROJECT/state/evolution.json", descriptor["writes_state"])
        self.assertIn("separate Human Owner action", descriptor["owner_approval"])
        self.assertIn("does not approve", " ".join(descriptor["notes"]))

    def test_review_close_helpers_are_registered_with_owner_gates(self):
        close_task = command_describe("task.close_reviewed")
        request_changes = command_describe("task.request_changes")
        approve_change = command_describe("evolution.approve_change")
        move_change = command_describe("evolution.move_to_review")
        accept_change = command_describe("evolution.accept_change")
        close_epic = command_describe("epic.close_if_complete")

        self.assertEqual(close_task["domain"], "task")
        self.assertEqual(close_task["lock_scope"], "workflow")
        self.assertIn("approval notes", close_task["owner_approval"])
        self.assertIn("AI_PROJECT/state/tasks.json", close_task["writes_state"])
        self.assertIn("AI_PROJECT/state/current_execution.json", close_task["writes_state"])
        self.assertIn("AI_PROJECT/events/codex-events.jsonl", close_task["event_logs"])
        self.assertIn("AI_PROJECT/generated/CODEX_STATUS.md", close_task["generated_files"])
        self.assertIn("only when it targets the closed Task", " ".join(close_task["notes"]))

        self.assertEqual(request_changes["domain"], "task")
        self.assertEqual(request_changes["lock_scope"], "workflow")
        self.assertIn("owner notes", request_changes["owner_approval"])
        self.assertIn("AI_PROJECT/state/tasks.json", request_changes["writes_state"])
        self.assertIn("task add-note", " ".join(request_changes["notes"]))

        self.assertEqual(accept_change["domain"], "evolution")
        self.assertIn("linked Tasks must be complete", accept_change["owner_approval"])
        self.assertIn("AI_PROJECT/state/evolution.json", accept_change["writes_state"])
        self.assertIn("Does not use task waivers", " ".join(accept_change["notes"]))

        self.assertEqual(approve_change["domain"], "evolution")
        self.assertIn("approval notes", approve_change["owner_approval"])
        self.assertIn("AI_PROJECT/state/evolution.json", approve_change["writes_state"])
        self.assertIn("change approve", " ".join(approve_change["notes"]))

        self.assertEqual(move_change["domain"], "evolution")
        self.assertIn("in_review", move_change["description"])
        self.assertIn("AI_PROJECT/state/evolution.json", move_change["writes_state"])
        self.assertIn("Does not accept", " ".join(move_change["notes"]))

        self.assertEqual(close_epic["domain"], "epic")
        self.assertIn("active child Tasks block", close_epic["owner_approval"])
        self.assertIn("AI_PROJECT/state/plan.json", close_epic["writes_state"])

    def test_command_list_filters_domain_and_planned_commands(self):
        implemented_names = [
            command["name"]
            for command in command_list(domain="project", include_planned=False)
        ]
        all_project_names = [
            command["name"]
            for command in command_list(domain="project", include_planned=True)
        ]

        self.assertEqual(
            implemented_names,
            ["project.doctor", "project.protected_check", "project.render"],
        )
        self.assertEqual(
            all_project_names,
            ["project.doctor", "project.protected_check", "project.render"],
        )

    def test_health_repair_commands_are_registered_with_safe_effects(self):
        docs_render = command_describe("docs.render")
        protected_check = command_describe("project.protected_check")

        self.assertEqual(docs_render["kind"], "render")
        self.assertTrue(docs_render["read_write"]["renders_generated"])
        self.assertFalse(docs_render["read_write"]["mutates_state"])
        self.assertIn("AI_PROJECT/generated/DOCS_INDEX.md", docs_render["generated_files"])

        self.assertEqual(protected_check["kind"], "validation")
        self.assertTrue(protected_check["read_write"]["validates"])
        self.assertFalse(protected_check["read_write"]["mutates_state"])
        self.assertFalse(protected_check["read_write"]["renders_generated"])

    def test_pipeline_session_commands_are_registered_as_governed_writes(self):
        create = command_describe("pipeline.session.create")
        run_next = command_describe("pipeline.run_next")
        run_until = command_describe("pipeline.run_until_blocker")
        validate = command_describe("pipeline.validate")
        check_generated = command_describe("pipeline.check_generated")

        self.assertEqual(create["domain"], "pipeline")
        self.assertEqual(create["kind"], "write")
        self.assertTrue(create["read_write"]["mutates_state"])
        self.assertTrue(create["read_write"]["writes_events"])
        self.assertTrue(create["read_write"]["renders_generated"])
        self.assertIn("AI_PROJECT/state/pipeline_sessions.json", create["writes_state"])
        self.assertIn("AI_PROJECT/events/pipeline-events.jsonl", create["event_logs"])
        self.assertIn("AI_PROJECT/generated/PIPELINE_STATUS.md", create["generated_files"])
        self.assertIn("does not run Codex", create["owner_approval"])

        self.assertEqual(run_next["kind"], "write")
        self.assertTrue(run_next["read_write"]["mutates_state"])
        self.assertTrue(run_next["read_write"]["writes_events"])
        self.assertTrue(run_next["read_write"]["renders_generated"])
        self.assertIn("AI_PROJECT/state/pipeline_sessions.json", run_next["writes_state"])
        self.assertIn("AI_PROJECT/events/pipeline-events.jsonl", run_next["event_logs"])
        self.assertIn("AI_PROJECT/generated/PIPELINE_STATUS.md", run_next["generated_files"])
        self.assertIn("run-until-blocker", " ".join(run_next["notes"]))

        self.assertEqual(run_until["kind"], "write")
        self.assertTrue(run_until["read_write"]["mutates_state"])
        self.assertTrue(run_until["read_write"]["writes_events"])
        self.assertTrue(run_until["read_write"]["renders_generated"])
        self.assertIn("AI_PROJECT/state/pipeline_sessions.json", run_until["writes_state"])
        self.assertIn("explicit confirmation", run_until["owner_approval"])

        self.assertEqual(validate["kind"], "validation")
        self.assertTrue(validate["read_write"]["validates"])
        self.assertFalse(validate["read_write"]["mutates_state"])

        self.assertEqual(check_generated["kind"], "validation")
        self.assertTrue(check_generated["read_write"]["validates"])

    def test_registry_rejects_duplicate_commands(self):
        descriptor = CommandDescriptor(
            name="demo.show",
            domain="demo",
            description="Show demo metadata.",
            kind=CommandKind.READ,
        )
        registry = CommandRegistry([descriptor])

        with self.assertRaises(RegistryError) as raised:
            registry.register(descriptor)

        self.assertEqual(raised.exception.code, "DUPLICATE_COMMAND")

    def test_registry_rejects_invalid_descriptor(self):
        with self.assertRaises(RegistryError) as raised:
            CommandRegistry(
                [
                    CommandDescriptor(
                        name="task.show",
                        domain="wrong",
                        description="Invalid domain.",
                        kind=CommandKind.READ,
                    )
                ]
            )

        self.assertEqual(raised.exception.code, "COMMAND_DOMAIN_MISMATCH")

    def test_unknown_command_raises_stable_error(self):
        with self.assertRaises(RegistryError) as raised:
            default_command_registry().describe("task.missing")

        self.assertEqual(raised.exception.code, "COMMAND_NOT_FOUND")

    def test_metadata_only_registry_does_not_expose_execute_api(self):
        registry = default_command_registry()

        self.assertFalse(hasattr(registry, "execute"))
        self.assertFalse(hasattr(registry.get("task.create"), "handler"))
        self.assertIn("task_required_fields", registry.get("task.create").validators)


if __name__ == "__main__":
    unittest.main()

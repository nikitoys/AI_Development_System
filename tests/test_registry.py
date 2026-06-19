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
        self.assertIn("task.prepare_for_codex", names)
        self.assertIn("task.refresh_execution_context", names)
        self.assertIn("task.submit_for_review", names)
        self.assertIn("evolution.create_for_task", names)
        self.assertIn("task.transition", names)
        self.assertIn("current.set", names)
        self.assertIn("current.clear", names)
        self.assertIn("epic.list", names)
        self.assertIn("change.create", names)
        self.assertIn("context.build", names)
        self.assertIn("codex.prompt.build", names)
        self.assertIn("project.doctor", names)
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

    def test_command_list_filters_domain_and_planned_commands(self):
        implemented_names = [
            command["name"]
            for command in command_list(domain="project", include_planned=False)
        ]
        all_project_names = [
            command["name"]
            for command in command_list(domain="project", include_planned=True)
        ]

        self.assertEqual(implemented_names, ["project.doctor", "project.render"])
        self.assertEqual(all_project_names, ["project.doctor", "project.render"])

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

import json
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.core.events import AuditLog
from ai_project_ctl.core.locks import FileLock
from ai_project_ctl.core.store import JsonStore
from ai_project_ctl.core.transactions import MutationTransaction, RenderTrigger
from ai_project_ctl.core.validation import ValidationResult


class CoreTransactionsLocksTests(unittest.TestCase):
    def test_transaction_saves_events_and_runs_render_triggers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_path = root / "AI_PROJECT" / "state" / "example.json"
            event_path = root / "AI_PROJECT" / "events" / "example-events.jsonl"
            generated_path = root / "AI_PROJECT" / "generated" / "EXAMPLE.md"
            store = JsonStore(state_path)
            store.save({"schema_version": 1, "revision": 0, "value": 1})

            def mutate(state):
                state["value"] = 2
                state["revision"] = 1
                return {"changed": "value"}

            result = MutationTransaction(
                store,
                event_log=AuditLog(event_path),
            ).run(
                command="example.update",
                domain="example",
                actor="codex",
                entity_type="example",
                entity_id="EXAMPLE-001",
                mutate=mutate,
                renderers=[
                    RenderTrigger(
                        generated_path,
                        lambda state: f"value={state['value']}\n",
                    )
                ],
            )

            self.assertTrue(result.ok)
            self.assertEqual(JsonStore(state_path).load()["value"], 2)
            self.assertIn(str(generated_path), result.generated_files)
            self.assertEqual(generated_path.read_text(encoding="utf-8"), "value=2\n")
            self.assertEqual(json.loads(event_path.read_text(encoding="utf-8"))["command"], "example.update")

    def test_transaction_validation_failure_does_not_write_event_or_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_path = root / "state.json"
            event_path = root / "events.jsonl"
            generated_path = root / "generated.md"
            store = JsonStore(state_path)
            store.save({"schema_version": 1, "revision": 0, "value": 1})

            def validate(_state):
                result = ValidationResult()
                result.add_error("NOPE", "blocked")
                return result

            def mutate(state):
                state["value"] = 99

            result = MutationTransaction(
                store,
                event_log=AuditLog(event_path),
            ).run(
                command="example.update",
                domain="example",
                actor="codex",
                entity_type="example",
                entity_id="EXAMPLE-001",
                mutate=mutate,
                validate_before=validate,
                renderers=[RenderTrigger(generated_path, lambda state: "bad\n")],
            )

            self.assertFalse(result.ok)
            self.assertEqual(JsonStore(state_path).load()["value"], 1)
            self.assertFalse(event_path.exists())
            self.assertFalse(generated_path.exists())

    def test_file_lock_context_marks_held_and_releases(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock = FileLock(Path(tmp) / "locks" / "state.lock")
            with lock:
                self.assertTrue(lock.held)
            self.assertFalse(lock.held)


if __name__ == "__main__":
    unittest.main()


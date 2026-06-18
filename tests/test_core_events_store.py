import json
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.core.events import AuditEvent, AuditLog
from ai_project_ctl.core.store import JsonStore, StoreError, atomic_write_text


class CoreEventsStoreTests(unittest.TestCase):
    def test_json_store_round_trips_with_atomic_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state" / "example.json"
            store = JsonStore(path)

            store.save({"schema_version": 1, "revision": 2, "name": "demo"})

            self.assertEqual(store.load()["revision"], 2)
            self.assertEqual(path.read_text(encoding="utf-8").splitlines()[0], "{")

    def test_invalid_json_raises_stable_store_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.json"
            atomic_write_text(path, "{")

            with self.assertRaises(StoreError) as raised:
                JsonStore(path).load()

            self.assertEqual(raised.exception.code, "INVALID_JSON")

    def test_audit_log_appends_compact_json_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events" / "test-events.jsonl"
            event_id = AuditLog(path).append(
                AuditEvent(
                    actor="codex",
                    command="test.command",
                    entity_type="task",
                    entity_id="TASK-001",
                    revision_before=1,
                    revision_after=2,
                    payload={"field": "value"},
                )
            )

            line = path.read_text(encoding="utf-8")
            parsed = json.loads(line)
            self.assertEqual(parsed["event_id"], event_id)
            self.assertEqual(parsed["command"], "test.command")
            self.assertFalse(line.startswith("{ "))


if __name__ == "__main__":
    unittest.main()


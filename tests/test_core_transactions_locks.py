import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from ai_project_ctl.core.events import AuditLog
from ai_project_ctl.core import locks as locks_mod
from ai_project_ctl.core.locks import FileLock, LockError
from ai_project_ctl.core.store import JsonStore
from ai_project_ctl.core.transactions import MutationTransaction, RenderTrigger
from ai_project_ctl.core.validation import ValidationResult

ROOT = Path(__file__).resolve().parents[1]


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
                self.assertTrue(lock.path.exists())
            self.assertFalse(lock.held)
            if lock.path.exists():
                self.assertEqual(lock.path.read_text(encoding="utf-8"), "")

    def test_file_lock_contention_returns_readable_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock_path = Path(tmp) / "locks" / "state.lock"
            with FileLock(lock_path):
                child = run_lock_child(lock_path)

            self.assertEqual(child.returncode, 7)
            self.assertIn("LOCK_BUSY", child.stdout)
            self.assertIn(str(lock_path), child.stdout)

    def test_file_lock_reports_stale_busy_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock_path = Path(tmp) / "locks" / "state.lock"
            with FileLock(lock_path):
                lock_path.write_text(
                    json.dumps({"pid": 999999, "acquired_at": time.time() - 3600}),
                    encoding="utf-8",
                )
                child = run_lock_child(lock_path, stale_after=0.001)

            self.assertEqual(child.returncode, 7)
            self.assertIn("LOCK_STALE", child.stdout)
            self.assertIn(str(lock_path), child.stdout)

    def test_lockfile_fallback_removes_stale_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock_path = Path(tmp) / "locks" / "state.lock"
            lock_path.parent.mkdir(parents=True)
            lock_path.write_text(
                json.dumps({"pid": 999999, "acquired_at": time.time() - 3600}),
                encoding="utf-8",
            )

            with mock.patch.object(locks_mod, "fcntl", None):
                lock = FileLock(lock_path, stale_after=0.001)
                with lock:
                    self.assertTrue(lock.held)

            self.assertFalse(lock_path.exists())

    def test_lockfile_fallback_reports_busy_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock_path = Path(tmp) / "locks" / "state.lock"
            lock_path.parent.mkdir(parents=True)
            lock_path.write_text(
                json.dumps({"pid": 123, "acquired_at": time.time()}),
                encoding="utf-8",
            )

            with mock.patch.object(locks_mod, "fcntl", None):
                with self.assertRaises(LockError) as raised:
                    FileLock(lock_path, stale_after=60).acquire(blocking=False)

            self.assertEqual(raised.exception.code, "LOCK_BUSY")
            self.assertIn(str(lock_path), raised.exception.message)


def run_lock_child(lock_path, *, stale_after=None):
    code = """
import sys
from pathlib import Path
from ai_project_ctl.core.locks import FileLock, LockError

stale_after = None if sys.argv[2] == "" else float(sys.argv[2])
lock = FileLock(Path(sys.argv[1]), stale_after=stale_after)
try:
    lock.acquire(blocking=False)
except LockError as exc:
    print(f"{exc.code}:{exc.message}")
    raise SystemExit(7)
else:
    lock.release()
    print("acquired")
    raise SystemExit(0)
"""
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-c", code, str(lock_path), "" if stale_after is None else str(stale_after)],
        cwd=str(ROOT),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


if __name__ == "__main__":
    unittest.main()

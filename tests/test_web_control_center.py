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
from ai_project_ctl.web.server import WebServerError, make_handler, route


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
                    payload = json.loads(response.read().decode("utf-8"))

                self.assertEqual(response.status, 200)
                self.assertTrue(payload["ok"])
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

                payload = json.loads(raised.exception.read().decode("utf-8"))
                self.assertEqual(raised.exception.code, 400)
                self.assertEqual(
                    payload["error"]["code"],
                    "WEB_ACTION_CONFIRMATION_REQUIRED",
                )
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
                    payload = json.loads(response.read().decode("utf-8"))

                self.assertEqual(response.status, 200)
                self.assertTrue(payload["ok"])
                self.assertEqual(Path(calls[0][1]).name, "aictl.py")
                self.assertEqual(
                    calls[0][-5:],
                    ["task", "transition", "TASK-001", "--to", "in_review"],
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

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


def write_web_state(root, *, tasks=None, current_task_id=None, epics=None):
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
    (state_dir / "plan.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "epics": epics or [],
            }
        ),
        encoding="utf-8",
    )


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


if __name__ == "__main__":
    unittest.main()

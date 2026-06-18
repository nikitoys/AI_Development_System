import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from ai_project_ctl.core.registry import command_describe
from ai_project_ctl.web.read_model import (
    ReadOnlyProjectModel,
    WebControlError,
    require_read_only_command,
)
from ai_project_ctl.web.server import WebServerError, make_handler, route


class WebControlCenterTests(unittest.TestCase):
    def test_web_registry_command_is_read_only(self):
        descriptor = command_describe("web.serve")

        self.assertEqual(descriptor["kind"], "read")
        self.assertFalse(descriptor["read_write"]["mutates_state"])
        self.assertFalse(descriptor["read_write"]["writes_events"])
        self.assertFalse(descriptor["read_write"]["renders_generated"])
        self.assertIn("read-only", " ".join(descriptor["notes"]))

    def test_read_model_rejects_write_registry_command(self):
        with self.assertRaises(WebControlError) as raised:
            require_read_only_command("task.transition")

        self.assertEqual(raised.exception.code, "WEB_COMMAND_NOT_READ_ONLY")

    def test_dashboard_uses_read_only_facade_commands(self):
        calls = []

        def fake_run(argv, **_kwargs):
            calls.append(argv)
            script = Path(argv[1]).name
            tail = argv[argv.index("--json") + 1 :] if "--json" in argv else argv[-3:]
            if script == "aictl.py" and tail == ["task", "list"]:
                return completed(
                    {
                        "data": {
                            "result": [
                                {
                                    "id": "TASK-001",
                                    "ref": "CTL-01",
                                    "status": "ready",
                                    "title": "Ready task",
                                }
                            ]
                        }
                    }
                )
            if script == "aictl.py" and tail == ["task", "list", "--current"]:
                return completed(
                    {
                        "data": {
                            "result": [
                                {
                                    "id": "TASK-001",
                                    "ref": "CTL-01",
                                    "status": "ready",
                                    "title": "Ready task",
                                }
                            ]
                        }
                    }
                )
            if script == "aictl.py" and tail == ["epic", "list"]:
                return completed({"data": {"result": [{"id": "EPIC-001", "status": "active"}]}})
            if script == "aictl.py" and tail == ["project", "doctor"]:
                return completed(
                    {
                        "data": {
                            "overall_status": "PASS",
                            "summary": {"PASS": 1, "WARN": 0, "FAIL": 0},
                            "findings": [],
                        }
                    }
                )
            if script.endswith("ctl.py"):
                return process(stdout="2026-06-18T00:00:00Z EVT test\n")
            raise AssertionError("unexpected command: {}".format(argv))

        with tempfile.TemporaryDirectory() as tmp:
            model = ReadOnlyProjectModel(tmp, actor="tester")
            with patch("ai_project_ctl.web.read_model.subprocess.run", side_effect=fake_run):
                data = model.dashboard()

        command_names = [Path(call[1]).name for call in calls]

        self.assertEqual(data["doctor"]["overall_status"], "PASS")
        self.assertEqual(data["queue"][0]["id"], "TASK-001")
        self.assertIn("aictl.py", command_names)
        self.assertNotIn("task.transition", " ".join(" ".join(call) for call in calls))

    def test_write_methods_are_rejected_without_model_reads(self):
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

            self.assertEqual(raised.exception.code, 405)
            self.assertEqual(raised.exception.headers["Allow"], "GET, HEAD")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_health_route_is_json_read_only(self):
        status, content_type, body = route("/healthz", object())

        self.assertEqual(status.value, 200)
        self.assertEqual(content_type, "application/json; charset=utf-8")
        self.assertEqual(json.loads(body)["mode"], "read-only")

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


if __name__ == "__main__":
    unittest.main()

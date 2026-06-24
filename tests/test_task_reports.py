import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.task_reports import (
    TaskReportError,
    submit_task_report,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def valid_task():
    return {
        "id": "TASK-001",
        "uid": "tsk_001",
        "ref": "APP-01",
        "legacy_id": "TASK-001",
        "aliases": ["TASK-001"],
    }


def valid_payload(**overrides):
    payload = {
        "schema_version": 1,
        "task_id": "TASK-001",
        "task_ref": "APP-01",
        "implementation_summary": "Implemented task report service.",
        "changed_files": ["ai_project_ctl/task_reports.py"],
        "generated_files": [],
        "checks": [
            {
                "name": "unit",
                "command": "python -m unittest tests.test_task_reports",
                "result": "pass",
                "duration_sec": 0.1,
                "blocking": True,
                "details": "",
            }
        ],
        "warnings": [],
        "blockers": [],
        "notes": [],
        "owner_decision_required": False,
        "token_usage": {
            "prompt_tokens": 1,
            "context_tokens": 1,
            "token_count_strategy": "test_fixture",
            "token_count_estimated": True,
        },
    }
    payload.update(overrides)
    return payload


def read_jsonl(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def run_ctl(script, root, *args):
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / script),
            "--root",
            str(root),
            "--actor",
            "tester",
            *args,
        ],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise AssertionError(
            "{} failed\nstdout:\n{}\nstderr:\n{}".format(
                script,
                completed.stdout,
                completed.stderr,
            )
        )
    return completed


def write_cli_project(root):
    run_ctl("planctl.py", root, "init", "--project-name", "Task Reports")
    run_ctl("planctl.py", root, "initiative", "create", "--title", "Reports")
    run_ctl(
        "planctl.py",
        root,
        "epic",
        "create",
        "--initiative",
        "INIT-001",
        "--title",
        "Report Service",
    )
    run_ctl("taskctl.py", root, "init")
    run_ctl(
        "taskctl.py",
        root,
        "task",
        "create",
        "--epic",
        "EPIC-001",
        "--title",
        "Submit report",
        "--status",
        "ready",
        "--scope",
        "Submit a structured task report.",
        "--allowed-file",
        "ai_project_ctl/task_reports.py",
        "--acceptance",
        "The report is stored.",
        "--verification-mode",
        "standard",
    )


class TaskReportsTests(unittest.TestCase):
    def test_service_submission_updates_latest_by_task_and_writes_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report_file = root / "report.json"
            report_file.write_text("{}", encoding="utf-8")
            task = valid_task()
            tasks_state = {"tasks": [task]}

            result = submit_task_report(
                root=root,
                tasks_state=tasks_state,
                task=task,
                report_payload=valid_payload(),
                source_file=report_file,
                actor="tester",
            )

            state_path = root / "AI_PROJECT" / "state" / "task_reports.json"
            event_path = root / "AI_PROJECT" / "events" / "task-report-events.jsonl"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            events = read_jsonl(event_path)

            self.assertEqual(result.report_id, "RPT-001")
            self.assertEqual(result.task_id, "TASK-001")
            self.assertEqual(result.revision_before, 0)
            self.assertEqual(result.revision_after, 1)
            self.assertEqual(state["latest_by_task"], {"TASK-001": "RPT-001"})
            self.assertEqual(state["reports"][0]["source_file"], str(report_file.resolve()))
            self.assertEqual(events[0]["command"], "task.report.submit")
            self.assertEqual(events[0]["entity_id"], "RPT-001")
            self.assertEqual(events[0]["event_id"], result.event_id)
            self.assertEqual(events[0]["payload"]["task_id"], "TASK-001")

    def test_service_rejects_invalid_report_with_stable_validation_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = valid_task()
            invalid = valid_payload()
            del invalid["implementation_summary"]

            with self.assertRaises(TaskReportError) as caught:
                submit_task_report(
                    root=root,
                    tasks_state={"tasks": [task]},
                    task=task,
                    report_payload=invalid,
                    source_file=root / "report.json",
                    actor="tester",
                )

            self.assertIn("INVALID_REPORT_SCHEMA", str(caught.exception))
            self.assertIn("report missing required field(s): implementation_summary", str(caught.exception))
            self.assertFalse((root / "AI_PROJECT" / "state" / "task_reports.json").exists())

    def test_taskctl_report_submit_cli_uses_compatible_state_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_cli_project(root)
            report_file = root / "report.json"
            report_file.write_text(json.dumps(valid_payload(task_ref="")), encoding="utf-8")

            completed = run_ctl(
                "taskctl.py",
                root,
                "task",
                "report",
                "submit",
                "--task",
                "TASK-001",
                "--file",
                str(report_file),
                "--confirm",
                "--json",
            )
            payload = json.loads(completed.stdout)
            state = json.loads(
                (root / "AI_PROJECT" / "state" / "task_reports.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(payload["report_id"], "RPT-001")
            self.assertEqual(payload["task_id"], "TASK-001")
            self.assertEqual(payload["revision_before"], 0)
            self.assertEqual(payload["revision_after"], 1)
            self.assertEqual(state["latest_by_task"]["TASK-001"], "RPT-001")
            self.assertEqual(state["reports"][0]["report"]["reported_task_id"], "TASK-001")


if __name__ == "__main__":
    unittest.main()

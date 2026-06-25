import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ai_project_ctl.pipeline.report_template import build_report_template
from ai_project_ctl.task_reports import submit_task_report


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"


def task():
    return {
        "id": "TASK-164",
        "uid": "tsk_e663c259db22",
        "ref": "PIPEF-83",
        "legacy_id": "TASK-164",
        "aliases": ["TASK-164"],
    }


def write_tasks_state(root: Path) -> dict:
    tasks_state = {
        "schema_version": 1,
        "revision": 1,
        "current_task_id": "TASK-164",
        "tasks": [task()],
    }
    state_path = root / "AI_PROJECT" / "state" / "tasks.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(tasks_state), encoding="utf-8")
    return tasks_state


class PipelineReportTemplateTests(unittest.TestCase):
    def test_template_uses_submission_input_identity_fields_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_tasks_state(root)

            template = build_report_template("PIPEF-83", root=root)

            self.assertNotIn("reported_task_id", template)
            self.assertNotIn("reported_task_ref", template)
            for field in [
                "schema_version",
                "task_id",
                "task_ref",
                "implementation_summary",
                "changed_files",
                "generated_files",
                "checks",
                "warnings",
                "blockers",
                "notes",
                "owner_decision_required",
                "token_usage",
            ]:
                self.assertIn(field, template)
            self.assertEqual(template["task_id"], "TASK-164")
            self.assertEqual(template["task_ref"], "PIPEF-83")
            self.assertIn("token_count_strategy", template["token_usage"])

    def test_template_payload_submits_and_normalizes_reported_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tasks_state = write_tasks_state(root)
            template = build_report_template("TASK-164", root=root)
            template["implementation_summary"] = "Completed report template fix."
            template["checks"] = [
                {
                    "name": "unit",
                    "command": "python -m unittest tests.pipeline.test_report_template",
                    "result": "pass",
                    "duration_sec": 0.1,
                    "blocking": True,
                    "details": "",
                }
            ]

            submit_task_report(
                root=root,
                tasks_state=tasks_state,
                task=tasks_state["tasks"][0],
                report_payload=template,
                source_file=root / "report.json",
                actor="tester",
            )

            state = json.loads(
                (root / "AI_PROJECT" / "state" / "task_reports.json").read_text(
                    encoding="utf-8"
                )
            )
            report = state["reports"][0]["report"]
            self.assertEqual(report["reported_task_id"], "TASK-164")
            self.assertEqual(report["reported_task_ref"], "PIPEF-83")

    def test_cli_prints_importable_json_for_selected_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_tasks_state(root)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "aictl.py"),
                    "--root",
                    str(root),
                    "pipeline",
                    "report",
                    "template",
                    "--task",
                    "PIPEF-83",
                ],
                cwd=str(ROOT),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            template = json.loads(completed.stdout)
            self.assertEqual(template["task_id"], "TASK-164")
            self.assertEqual(template["task_ref"], "PIPEF-83")
            self.assertNotIn("reported_task_id", template)
            self.assertNotIn("reported_task_ref", template)


if __name__ == "__main__":
    unittest.main()

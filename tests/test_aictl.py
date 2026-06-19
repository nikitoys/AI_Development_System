import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
AICTL_PATH = ROOT / "scripts" / "aictl.py"


def load_aictl():
    spec = importlib.util.spec_from_file_location("aictl_test_module", AICTL_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_project_state(root):
    state_dir = root / "AI_PROJECT" / "state"
    state_dir.mkdir(parents=True)
    (state_dir / "plan.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "epics": [{"id": "EPIC-006", "key": "WFA", "status": "planned"}],
            }
        ),
        encoding="utf-8",
    )
    (state_dir / "tasks.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "current_task_id": None,
                "tasks": [
                    {
                        "id": "TASK-032",
                        "legacy_id": "TASK-032",
                        "ref": "WFA-01",
                        "aliases": ["TASK-032"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


class AictlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aictl = load_aictl()

    def run_main(self, argv, completed=None):
        stdout = io.StringIO()
        if completed is None:
            with redirect_stdout(stdout):
                code = self.aictl.main(argv)
            return code, stdout.getvalue(), None

        with patch.object(self.aictl.subprocess, "run", return_value=completed) as run:
            with redirect_stdout(stdout):
                code = self.aictl.main(argv)
        return code, stdout.getvalue(), run

    def test_command_list_json_uses_registry(self):
        code, stdout, _run = self.run_main(["--json", "command", "list"])

        payload = json.loads(stdout)
        names = [command["name"] for command in payload["data"]["commands"]]

        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertIn("command.describe", names)
        self.assertIn("current.set", names)
        self.assertIn("project.render", names)
        self.assertIn("task.import", names)
        self.assertIn("task.report.submit", names)
        self.assertIn("task.transition", names)
        self.assertIn("workflow.list", names)

    def test_command_describe_human_output(self):
        code, stdout, _run = self.run_main(["command", "describe", "task.transition"])

        self.assertEqual(code, 0)
        self.assertIn("task.transition (write, implemented)", stdout)
        self.assertIn("Transition a Task", stdout)
        self.assertIn("Legacy: python scripts/taskctl.py", stdout)

    def test_workflow_list_json(self):
        code, stdout, _run = self.run_main(["--json", "workflow", "list"])

        payload = json.loads(stdout)
        names = [workflow["name"] for workflow in payload["data"]["workflows"]]

        self.assertEqual(code, 0)
        self.assertIn("task.prepare_for_codex", names)
        self.assertIn("task.refresh_execution_context", names)
        self.assertIn("task.submit_for_review", names)
        self.assertIn("evolution.create_for_task", names)
        self.assertIn("evolution.approve_change", names)
        self.assertIn("evolution.move_to_review", names)
        self.assertIn("task.close_reviewed", names)
        self.assertIn("task.request_changes", names)
        self.assertIn("evolution.accept_change", names)
        self.assertIn("epic.close_if_complete", names)

    def test_workflow_run_without_confirm_returns_preview(self):
        code, stdout, _run = self.run_main(
            [
                "--json",
                "workflow",
                "run",
                "task.refresh_execution_context",
                "--task",
                "WFA-01",
            ]
        )

        payload = json.loads(stdout)

        self.assertEqual(code, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["errors"][0]["code"], "WORKFLOW_CONFIRMATION_REQUIRED")
        self.assertEqual(payload["data"]["task_ref"], "WFA-01")
        self.assertTrue(payload["data"]["steps"])

    def test_evolution_create_for_task_workflow_delegates_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = root / "AI_PROJECT" / "state"
            state.mkdir(parents=True)
            (state / "tasks.json").write_text(
                json.dumps(
                    {
                        "tasks": [
                            {
                                "id": "TASK-033",
                                "ref": "WFA-02",
                                "legacy_id": "TASK-033",
                                "aliases": ["TASK-033"],
                                "status": "in_progress",
                                "title": "WFA-02 Add Evolution Change Wizard",
                                "summary": "Create an Evolution Change wizard.",
                                "description": "Prepare a ready Change Proposal from task fields.",
                                "scope": ["Add workflow evolution.create_for_task."],
                                "out_of_scope": ["Do not auto-approve Evolution Changes."],
                                "allowed_files": [
                                    "ai_project_ctl/core/workflows.py",
                                    "tests/**",
                                ],
                                "acceptance_criteria": [
                                    "Created Change links to the correct legacy task id."
                                ],
                                "review_instructions": [
                                    "Verify owner approval remains separate."
                                ],
                            }
                        ]
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            def fake_run(argv, **_kwargs):
                script = Path(argv[1]).name
                if script == "taskctl.py" and argv[-4:] == [
                    "task",
                    "resolve",
                    "WFA-02",
                    "--json",
                ]:
                    return subprocess.CompletedProcess(
                        argv,
                        0,
                        '{"id": "TASK-033", "ref": "WFA-02", "status": "in_progress"}\n',
                        "",
                    )
                if script == "evolutionctl.py":
                    command_text = " ".join(argv)
                    if " approve " in command_text or " accept " in command_text:
                        raise AssertionError("workflow must not approve or accept changes")
                    if argv[-1] == "check-generated":
                        return subprocess.CompletedProcess(
                            argv,
                            0,
                            "OK: generated evolution file is up to date\n",
                            "",
                        )
                    if argv[-1] == "validate":
                        return subprocess.CompletedProcess(
                            argv,
                            0,
                            "OK: evolution is valid\n",
                            "",
                        )
                    if "create" in argv:
                        return subprocess.CompletedProcess(
                            argv,
                            0,
                            "OK: change.create revision 1 -> 2\nCreated: CHG-099\n",
                            "",
                        )
                    return subprocess.CompletedProcess(argv, 0, "OK\n", "")
                raise AssertionError("unexpected command: {}".format(argv))

            stdout = io.StringIO()
            with patch("ai_project_ctl.core.workflows.subprocess.run", side_effect=fake_run) as run:
                with redirect_stdout(stdout):
                    code = self.aictl.main(
                        [
                            "--root",
                            str(root),
                            "--actor",
                            "tester",
                            "--json",
                            "workflow",
                            "run",
                            "evolution.create_for_task",
                            "--task",
                            "WFA-02",
                            "--confirm",
                        ]
                    )

        payload = json.loads(stdout.getvalue())
        commands = [call.args[0] for call in run.call_args_list]

        self.assertEqual(code, 0)
        self.assertEqual(payload["data"]["change_id"], "CHG-099")
        self.assertEqual(payload["data"]["change_preview"]["linked_task"], "TASK-033")
        self.assertIn("approve explicitly", payload["owner_action_required"])
        self.assertTrue(
            any(command[-5:] == ["change", "link-task", "CHG-099", "--task", "TASK-033"] for command in commands)
        )
        self.assertTrue(
            any(command[-5:] == ["change", "transition", "CHG-099", "--to", "ready"] for command in commands)
        )
        self.assertFalse(any("approve" in command for command in commands))
        self.assertFalse(any("accept" in command for command in commands))

    def test_close_reviewed_task_workflow_requires_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            def fake_run(argv, **_kwargs):
                if Path(argv[1]).name == "taskctl.py" and "resolve" in argv:
                    return subprocess.CompletedProcess(
                        argv,
                        0,
                        '{"id": "TASK-032", "ref": "WFA-01", "status": "in_review"}\n',
                        "",
                    )
                return subprocess.CompletedProcess(argv, 0, "OK\n", "")

            stdout = io.StringIO()
            with patch("ai_project_ctl.core.workflows.subprocess.run", side_effect=fake_run):
                with redirect_stdout(stdout):
                    code = self.aictl.main(
                        [
                            "--root",
                            str(root),
                            "--json",
                            "workflow",
                            "run",
                            "task.close_reviewed",
                            "--task",
                            "WFA-01",
                            "--confirm",
                        ]
                    )

        payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 1)
        self.assertEqual(payload["errors"][0]["code"], "WORKFLOW_APPROVAL_NOTES_REQUIRED")

    def test_accept_change_workflow_delegates_with_change_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = root / "AI_PROJECT" / "state"
            state.mkdir(parents=True)
            (state / "evolution.json").write_text(
                json.dumps(
                    {
                        "changes": [
                            {
                                "id": "CHG-018",
                                "status": "in_review",
                                "linked_tasks": ["TASK-036"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (state / "tasks.json").write_text(
                json.dumps(
                    {
                        "tasks": [
                            {
                                "id": "TASK-036",
                                "legacy_id": "TASK-036",
                                "status": "done",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            def fake_run(argv, **_kwargs):
                return subprocess.CompletedProcess(argv, 0, "OK\n", "")

            stdout = io.StringIO()
            with patch("ai_project_ctl.core.workflows.subprocess.run", side_effect=fake_run) as run:
                with redirect_stdout(stdout):
                    code = self.aictl.main(
                        [
                            "--root",
                            str(root),
                            "--json",
                            "workflow",
                            "run",
                            "evolution.accept_change",
                            "--change",
                            "CHG-018",
                            "--notes",
                            "Accepted after review.",
                            "--confirm",
                        ]
                    )

        payload = json.loads(stdout.getvalue())
        commands = [call.args[0] for call in run.call_args_list]

        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(
            any(command[-5:] == ["change", "accept", "CHG-018", "--notes", "Accepted after review."] for command in commands)
        )

    def test_approve_change_workflow_delegates_with_change_target_and_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = root / "AI_PROJECT" / "state"
            state.mkdir(parents=True)
            (state / "evolution.json").write_text(
                json.dumps({"changes": [{"id": "CHG-041", "status": "ready"}]}),
                encoding="utf-8",
            )

            def fake_run(argv, **_kwargs):
                return subprocess.CompletedProcess(argv, 0, "OK\n", "")

            stdout = io.StringIO()
            with patch("ai_project_ctl.core.workflows.subprocess.run", side_effect=fake_run) as run:
                with redirect_stdout(stdout):
                    code = self.aictl.main(
                        [
                            "--root",
                            str(root),
                            "--json",
                            "workflow",
                            "run",
                            "evolution.approve_change",
                            "--change",
                            "CHG-041",
                            "--notes",
                            "Approved by owner.",
                            "--confirm",
                        ]
                    )

        payload = json.loads(stdout.getvalue())
        commands = [call.args[0] for call in run.call_args_list]

        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(
            any(command[-5:] == ["change", "approve", "CHG-041", "--notes", "Approved by owner."] for command in commands)
        )

    def test_task_list_delegates_with_native_json(self):
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='[{"id": "TASK-001"}]\n',
            stderr="",
        )

        code, stdout, run = self.run_main(
            ["--root", "/tmp/project", "--actor", "tester", "--json", "task", "list", "--status", "ready"],
            completed,
        )

        argv = run.call_args.args[0]
        payload = json.loads(stdout)

        self.assertEqual(code, 0)
        self.assertIn("taskctl.py", argv[1])
        self.assertEqual(argv[2:6], ["--root", "/tmp/project", "--actor", "tester"])
        self.assertEqual(argv[-5:], ["task", "list", "--status", "ready", "--json"])
        self.assertEqual(payload["data"]["result"], [{"id": "TASK-001"}])

    def test_task_transition_delegates_write_without_native_json(self):
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="OK: transitioned CTL-06 from in_progress to in_review\n",
            stderr="",
        )

        code, stdout, run = self.run_main(
            ["--json", "task", "transition", "CTL-06", "--to", "in_review"],
            completed,
        )

        argv = run.call_args.args[0]
        payload = json.loads(stdout)

        self.assertEqual(code, 0)
        self.assertEqual(argv[-5:], ["task", "transition", "CTL-06", "--to", "in_review"])
        self.assertNotIn("--json", argv)
        self.assertTrue(payload["ok"])
        self.assertIn("transitioned CTL-06", payload["data"]["stdout"])

    def test_task_report_submit_delegates_with_native_json(self):
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"report_id": "RPT-001", "task_id": "TASK-046"}\n',
            stderr="",
        )

        code, stdout, run = self.run_main(
            [
                "--json",
                "task",
                "report",
                "submit",
                "--task",
                "WFA-15",
                "--file",
                "/tmp/report.json",
                "--confirm",
            ],
            completed,
        )

        argv = run.call_args.args[0]
        payload = json.loads(stdout)

        self.assertEqual(code, 0)
        self.assertEqual(
            argv[-9:],
            [
                "task",
                "report",
                "submit",
                "--task",
                "WFA-15",
                "--file",
                "/tmp/report.json",
                "--confirm",
                "--json",
            ],
        )
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["data"]["result"]["report_id"], "RPT-001")

    def test_task_create_facade_runs_create_only_workflow(self):
        def fake_run(argv, **_kwargs):
            script = Path(argv[1]).name
            tail = argv[6:]
            if script == "taskctl.py" and list(tail[:2]) == ["task", "create"]:
                return subprocess.CompletedProcess(
                    argv,
                    0,
                    "OK: task.create revision 1 -> 2\nCreated: WFA-07 (TASK-099)\n",
                    "",
                )
            return subprocess.CompletedProcess(argv, 0, "OK\n", "")

        stdout = io.StringIO()
        with patch("ai_project_ctl.core.workflows.subprocess.run", side_effect=fake_run) as run:
            with redirect_stdout(stdout):
                code = self.aictl.main(
                    [
                        "--json",
                        "task",
                        "create",
                        "--epic",
                        "EPIC-006",
                        "--title",
                        "Create from aictl",
                        "--scope",
                        "Do one thing",
                        "--allowed-file",
                        "README.md",
                        "--acceptance",
                        "Validation passes",
                        "--depends-on",
                        "TASK-032",
                        "--dependency-reason",
                        "Needs WFA-01.",
                        "--confirm",
                    ]
                )

        payload = json.loads(stdout.getvalue())
        command_tails = [" ".join(call.args[0][6:]) for call in run.call_args_list]

        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["data"]["created_task_id"], "TASK-099")
        self.assertTrue(payload["data"]["create_only"])
        self.assertTrue(any(tail.startswith("task create --epic EPIC-006") for tail in command_tails))
        self.assertIn(
            "task deps add TASK-099 --after TASK-032 --type hard --reason Needs WFA-01.",
            command_tails,
        )
        self.assertFalse(any("current set" in tail for tail in command_tails))
        self.assertFalse(any("task transition" in tail for tail in command_tails))

    def test_task_import_facade_previews_without_confirmation(self):
        payload = {"tasks": [{"epic": "EPIC-006", "title": "Imported"}]}

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = self.aictl.main(
                    [
                        "--root",
                        str(root),
                        "--json",
                        "task",
                        "import",
                        "--text",
                        json.dumps(payload),
                    ]
                )

        output = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertTrue(output["ok"])
        self.assertTrue(output["data"]["dry_run"])
        self.assertEqual(output["data"]["task_count"], 1)

    def test_task_import_facade_confirm_runs_taskctl_create(self):
        payload = {"tasks": [{"epic": "EPIC-006", "title": "Imported"}]}

        def fake_run(argv, **_kwargs):
            script = Path(argv[1]).name
            tail = argv[6:]
            if script == "taskctl.py" and list(tail[:2]) == ["task", "create"]:
                return subprocess.CompletedProcess(
                    argv,
                    0,
                    "OK: task.create revision 1 -> 2\nCreated: WFA-07 (TASK-099)\n",
                    "",
                )
            return subprocess.CompletedProcess(argv, 0, "OK\n", "")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project_state(root)
            stdout = io.StringIO()
            with patch("ai_project_ctl.core.workflows.subprocess.run", side_effect=fake_run) as run:
                with redirect_stdout(stdout):
                    code = self.aictl.main(
                        [
                            "--root",
                            str(root),
                            "--json",
                            "task",
                            "import",
                            "--text",
                            json.dumps(payload),
                            "--confirm",
                        ]
                    )

        output = json.loads(stdout.getvalue())
        command_tails = [" ".join(call.args[0][6:]) for call in run.call_args_list]

        self.assertEqual(code, 0)
        self.assertTrue(output["ok"])
        self.assertFalse(output["data"]["dry_run"])
        self.assertEqual(output["data"]["created_task_ids"], ["TASK-099"])
        self.assertTrue(any(tail.startswith("task create --epic EPIC-006") for tail in command_tails))

    def test_current_set_delegates_write_without_native_json(self):
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="OK: current.set revision 4 -> 5\n",
            stderr="",
        )

        code, stdout, run = self.run_main(
            ["--json", "current", "set", "CTL-06"],
            completed,
        )

        argv = run.call_args.args[0]
        payload = json.loads(stdout)

        self.assertEqual(code, 0)
        self.assertEqual(argv[-3:], ["current", "set", "CTL-06"])
        self.assertTrue(payload["ok"])
        self.assertIn("current.set", payload["data"]["stdout"])

    def test_current_clear_delegates_write_without_native_json(self):
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="OK: current.clear revision 5 -> 6\n",
            stderr="",
        )

        code, stdout, run = self.run_main(
            ["--json", "current", "clear"],
            completed,
        )

        argv = run.call_args.args[0]
        payload = json.loads(stdout)

        self.assertEqual(code, 0)
        self.assertEqual(argv[-2:], ["current", "clear"])
        self.assertTrue(payload["ok"])
        self.assertIn("current.clear", payload["data"]["stdout"])

    def test_codex_prompt_build_resolves_task_ref_before_delegating(self):
        resolve = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"id": "TASK-024", "ref": "CTL-06"}\n',
            stderr="",
        )
        build = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="OK: CODEX_READY\n",
            stderr="",
        )
        stdout = io.StringIO()

        with patch.object(self.aictl.subprocess, "run", side_effect=[resolve, build]) as run:
            with redirect_stdout(stdout):
                code = self.aictl.main(
                    ["--json", "codex", "prompt", "build", "--task", "CTL-06"]
                )

        first_argv = run.call_args_list[0].args[0]
        second_argv = run.call_args_list[1].args[0]
        payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(first_argv[-4:], ["task", "resolve", "CTL-06", "--json"])
        self.assertEqual(second_argv[-3:], ["build", "--task", "TASK-024"])
        self.assertTrue(payload["ok"])

    def test_project_doctor_reports_pass_warn_fail_json(self):
        def fake_run(argv, **_kwargs):
            script = Path(argv[1]).name
            tail = argv[2:]
            if script == "planctl.py":
                return subprocess.CompletedProcess(argv, 0, "OK: plan is valid\n", "")
            if script == "taskctl.py" and tail[-3:] == ["task", "graph", "validate"]:
                return subprocess.CompletedProcess(argv, 1, "GRAPH_FAILED\n", "")
            if script == "taskctl.py" and tail[-1] == "validate":
                return subprocess.CompletedProcess(argv, 0, "OK: tasks are valid\n", "")
            if script == "taskctl.py" and tail[-1] == "check-generated":
                return subprocess.CompletedProcess(argv, 0, "OK: generated task files are up to date\n", "")
            if script == "taskctl.py" and tail[-3:] == ["current", "show", "--json"]:
                return subprocess.CompletedProcess(
                    argv,
                    0,
                    '{"id": "TASK-026", "status": "in_progress"}\n',
                    "",
                )
            if script == "evolutionctl.py" and tail[-1] == "validate":
                return subprocess.CompletedProcess(argv, 0, "OK: evolution is valid\n", "")
            if script == "evolutionctl.py" and tail[-1] == "check-generated":
                return subprocess.CompletedProcess(argv, 0, "OK: generated evolution file is up to date\n", "")
            if script == "contextctl.py" and tail[-1] == "validate":
                return subprocess.CompletedProcess(argv, 0, "OK: context control files are valid\n", "")
            if script == "contextctl.py" and tail[-1] == "check-generated":
                return subprocess.CompletedProcess(argv, 0, "OK: generated context files are up to date\n", "")
            if script == "contextctl.py" and tail[-1] == "status":
                return subprocess.CompletedProcess(
                    argv,
                    0,
                    "Current context mode: task\nCurrent context task: TASK-025\n",
                    "",
                )
            if script == "codexctl.py":
                return subprocess.CompletedProcess(
                    argv,
                    0,
                    "\n".join(
                        [
                            "CODEX_READY",
                            "Code: CODEX_READY",
                            "Status: READY",
                            "Prompt exists: yes",
                            "Source type: task",
                            "Source ID: TASK-026",
                            "Source status: in_progress",
                        ]
                    )
                    + "\n",
                    "",
                )
            if script == "check-protected-project-files.py":
                return subprocess.CompletedProcess(
                    argv,
                    0,
                    '{"ok": true, "errors": [], "warnings": [], "checked": ["x"]}\n',
                    "",
                )
            raise AssertionError("unexpected command: {}".format(argv))

        stdout = io.StringIO()
        with patch.object(self.aictl.subprocess, "run", side_effect=fake_run) as run:
            with redirect_stdout(stdout):
                code = self.aictl.main(["--json", "project", "doctor"])

        payload = json.loads(stdout.getvalue())
        statuses = {finding["status"] for finding in payload["data"]["findings"]}
        scripts = [Path(call.args[0][1]).name for call in run.call_args_list]

        self.assertEqual(code, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["data"]["overall_status"], "FAIL")
        self.assertIn("PASS", statuses)
        self.assertIn("WARN", statuses)
        self.assertIn("FAIL", statuses)
        self.assertIn("check-protected-project-files.py", scripts)
        protected_argv = [
            call.args[0]
            for call in run.call_args_list
            if Path(call.args[0][1]).name == "check-protected-project-files.py"
        ][0]
        self.assertNotIn("--actor", protected_argv)
        self.assertEqual(protected_argv[-1], "--json")

    def test_project_doctor_human_output_uses_explicit_statuses(self):
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout="OK\n", stderr="")

        def fake_run(argv, **_kwargs):
            script = Path(argv[1]).name
            tail = argv[2:]
            if script == "taskctl.py" and tail[-3:] == ["current", "show", "--json"]:
                return subprocess.CompletedProcess(
                    argv,
                    0,
                    '{"id": "TASK-026", "status": "in_progress"}\n',
                    "",
                )
            if script == "codexctl.py":
                return subprocess.CompletedProcess(
                    argv,
                    0,
                    "Code: CODEX_READY\nStatus: READY\nPrompt exists: yes\nSource ID: TASK-026\n",
                    "",
                )
            if script == "contextctl.py" and tail[-1] == "status":
                return subprocess.CompletedProcess(
                    argv,
                    0,
                    "Current context mode: task\nCurrent context task: TASK-026\n",
                    "",
                )
            if script == "check-protected-project-files.py":
                return subprocess.CompletedProcess(
                    argv,
                    0,
                    '{"ok": true, "errors": [], "warnings": [], "checked": ["x"]}\n',
                    "",
                )
            return completed

        stdout = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AI_PROJECT/state").mkdir(parents=True)
            (root / "AI_PROJECT/generated").mkdir(parents=True)
            (root / "AI_PROJECT/state/current_execution.json").write_text("{}\n", encoding="utf-8")
            (root / "AI_PROJECT/generated/CODEX_STATUS.md").write_text(
                "Source ID: `TASK-026`\nStatus: `READY`\n",
                encoding="utf-8",
            )

            with patch.object(self.aictl.subprocess, "run", side_effect=fake_run):
                with redirect_stdout(stdout):
                    code = self.aictl.main(["--root", str(root), "project", "doctor"])

        output = stdout.getvalue()

        self.assertEqual(code, 0)
        self.assertIn("Project Doctor: PASS", output)
        self.assertIn("PASS  plan validation", output)
        self.assertIn("PASS  protected project files", output)

    def test_project_render_runs_legacy_render_steps(self):
        completed = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="OK: rendered plan\n", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="OK: rendered tasks\n", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="OK: rendered docs\n", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="OK: rendered context\n", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="OK: rendered evolution\n", stderr=""),
        ]
        stdout = io.StringIO()

        with patch.object(self.aictl.subprocess, "run", side_effect=completed) as run:
            with redirect_stdout(stdout):
                code = self.aictl.main(["--json", "project", "render"])

        payload = json.loads(stdout.getvalue())
        scripts = [Path(call.args[0][1]).name for call in run.call_args_list]

        self.assertEqual(code, 0)
        self.assertEqual(
            scripts,
            ["planctl.py", "taskctl.py", "docctl.py", "contextctl.py", "evolutionctl.py"],
        )
        self.assertTrue(payload["ok"])
        self.assertEqual(len(payload["data"]["steps"]), 5)

    def test_web_command_starts_loopback_server_by_default(self):
        with patch("ai_project_ctl.web.server.run_server") as run_server:
            code = self.aictl.main(["--root", "/tmp/project", "--actor", "tester", "web"])

        self.assertEqual(code, 0)
        run_server.assert_called_once_with(
            "/tmp/project",
            host="127.0.0.1",
            port=8765,
            actor="tester",
        )


if __name__ == "__main__":
    unittest.main()

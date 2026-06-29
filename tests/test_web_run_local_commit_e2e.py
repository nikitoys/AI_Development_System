import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from ai_project_ctl.core import workflows as workflow_module
from ai_project_ctl.pipeline import policy_preset
from ai_project_ctl.pipeline.batch import run_until_blocker
from ai_project_ctl.pipeline.git_commit import REQUIRED_MACHINE_CHECKS
from ai_project_ctl.pipeline.machine_review import (
    MachineCheckEvidence,
    MachineReviewResult,
)
from ai_project_ctl.pipeline.policy import BatchPolicy, apply_codex_review_requirement
from ai_project_ctl.pipeline.state import pipeline_state_path
from ai_project_ctl.web.actions import WebActionExecutor
from ai_project_ctl.web.server import render_action_result


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
TASK_ID = "TASK-001"
SECOND_TASK_ID = "TASK-002"
ARTIFACT = "tests/web_run_artifact.txt"
SECOND_ARTIFACT = "tests/web_run_second_artifact.txt"
AUTO_CLOSE_NOTE = "Owner approved auto-close for Web Run smoke."
PIPELINE_BOOKKEEPING_FILES = (
    "AI_PROJECT/events/pipeline-events.jsonl",
    "AI_PROJECT/state/pipeline_sessions.json",
    "AI_PROJECT/generated/PIPELINE_STATUS.md",
    "AI_PROJECT/generated/PIPELINE_AUDIT.md",
)
WEB_RUN_GOVERNED_SIDE_EFFECT_CHANGED_FILES = (
    "AI_PROJECT/events/codex-events.jsonl",
    "AI_PROJECT/events/task-events.jsonl",
    "AI_PROJECT/events/task-report-events.jsonl",
    "AI_PROJECT/state/current_execution.json",
    "AI_PROJECT/state/task_reports.json",
    "AI_PROJECT/state/tasks.json",
)
WEB_RUN_GOVERNED_SIDE_EFFECT_GENERATED_FILES = (
    "AI_PROJECT/generated/CODEX_CURRENT.md",
    "AI_PROJECT/generated/CODEX_STATUS.md",
    "AI_PROJECT/generated/CODEX_TASKS.md",
    "AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md",
)


class WebRunLocalCommitSmokeTests(unittest.TestCase):
    def test_successful_web_run_leaves_clean_worktree_before_next_run(self):
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        root = Path(tmpdir.name)
        _write_temp_project(root)
        policy = _web_run_local_commit_policy()
        original_workflow_result = workflow_module.WorkflowExecutor._result

        def run_selected_session(session_id, **kwargs):
            return run_until_blocker(
                session_id,
                runner=_controlled_pipeline_runner(root),
                **kwargs,
            )

        with (
            mock.patch(
                "ai_project_ctl.web.actions.resolve_ui_pipeline_policy",
                return_value=policy,
            ),
            mock.patch(
                "ai_project_ctl.web.actions.run_until_blocker",
                side_effect=run_selected_session,
            ),
            mock.patch(
                "ai_project_ctl.pipeline.close_phase.evaluate_machine_review",
                side_effect=_passing_machine_review,
            ),
            mock.patch.object(
                workflow_module.WorkflowExecutor,
                "_run_subprocess",
                _workflow_subprocess_for_smoke,
            ),
            mock.patch.object(
                workflow_module.WorkflowExecutor,
                "_result",
                _workflow_result_with_smoke_effects(original_workflow_result),
            ),
        ):
            result = WebActionExecutor(root, actor="tester").execute(
                {
                    "action": "ui.run_selected_task",
                    "confirm": "yes",
                    "task": TASK_ID,
                    "auto_close_note": AUTO_CLOSE_NOTE,
                }
            )

            session_count = len(_pipeline_state(root)["sessions"])
            first_status_lines = _git_status_lines(root)

            second = WebActionExecutor(root, actor="tester").execute(
                {
                    "action": "ui.run_selected_task",
                    "confirm": "yes",
                    "task": SECOND_TASK_ID,
                    "auto_close_note": AUTO_CLOSE_NOTE,
                }
            )
            second_session_count = len(_pipeline_state(root)["sessions"])
            second_status_lines = _git_status_lines(root)

        result_payload = result.to_dict()
        result_data = result_payload["result"]["data"]
        result_body = render_action_result(result)
        self.assertTrue(result.ok)
        self.assertNotEqual(result_data.get("stop_code"), "WORKTREE_DIRTY")
        self.assertNotEqual(result_data.get("blocked_by"), "WORKTREE_DIRTY")
        self.assertNotIn("checkpoint_action", result_data)
        self.assertNotIn("WORKTREE_DIRTY", result_body)
        self.assertNotIn('name="action" value="ui.checkpoint_commit"', result_body)

        tasks = _tasks_state(root)
        self.assertEqual(tasks["tasks"][0]["status"], "done")

        reports = _reports_state(root)["reports"]
        first_report = _latest_report_for_task(reports, TASK_ID)
        self.assertEqual(first_report["report"]["changed_files"], [ARTIFACT])

        session = _pipeline_state(root)["sessions"][0]
        close = _latest_phase(session, "close")
        close_status = close["artifacts"]["close_status"]
        local_commit = close["artifacts"]["local_commit"]
        readiness = local_commit["readiness"]

        self.assertEqual(close_status["outcome"], "closed_with_local_commit")
        self.assertEqual(close_status["task_status"], "done")
        self.assertEqual(close_status["commit_status"], "pass")
        self.assertTrue(close_status["commit_hash"])
        self.assertEqual(local_commit["status"], "pass")
        self.assertEqual(local_commit["code"], "LOCAL_COMMIT_CREATED")
        self.assertEqual(readiness["status"], "pass")
        self.assertEqual(readiness["code"], "COMMIT_READINESS_PASS")
        self.assertEqual(readiness["blockers"], [])
        self.assertIn(ARTIFACT, local_commit["staged_files"])
        self.assertIn(ARTIFACT, readiness["approved_files"])
        self.assertIn("AI_PROJECT/state/pipeline_sessions.json", readiness["approved_files"])
        self.assertIn("AI_PROJECT/events/pipeline-events.jsonl", readiness["approved_files"])
        for path in PIPELINE_BOOKKEEPING_FILES:
            self.assertIn(path, local_commit["staged_files"])
            self.assertIn(path, readiness["approved_files"])

        commit_subject = _git(
            root,
            "log",
            "--format=%s",
            "-1",
        ).stdout.strip()
        self.assertIn(TASK_ID, commit_subject)
        self.assertIn("Web Run local commit smoke", commit_subject)

        _assert_clean_worktree(self, first_status_lines, "after first Web Run")

        second_payload = second.to_dict()
        second_data = second_payload["result"]["data"]
        second_body = render_action_result(second)
        tasks = _tasks_state(root)
        reports = _reports_state(root)["reports"]
        second_report = _latest_report_for_task(reports, SECOND_TASK_ID)

        self.assertEqual(tasks["tasks"][1]["status"], "done")
        self.assertEqual(second_report["report"]["changed_files"], [SECOND_ARTIFACT])
        self.assertTrue(second.ok)
        self.assertEqual(second_session_count, session_count + 1)
        self.assertNotEqual(second_data.get("stop_code"), "WORKTREE_DIRTY")
        self.assertNotEqual(second_data.get("blocked_by"), "WORKTREE_DIRTY")
        self.assertNotIn("checkpoint_action", second_data)
        self.assertNotIn("Create checkpoint commit", second_payload["result"]["message"])
        self.assertNotIn("Create Checkpoint Commit", second_body)
        self.assertNotIn('name="action" value="ui.checkpoint_commit"', second_body)

        second_session = _pipeline_state(root)["sessions"][1]
        second_close = _latest_phase(second_session, "close")
        second_local_commit = second_close["artifacts"]["local_commit"]
        self.assertEqual(second_local_commit["status"], "pass")
        self.assertEqual(second_local_commit["code"], "LOCAL_COMMIT_CREATED")
        self.assertTrue(second_local_commit["commit_hash"])
        self.assertIn(SECOND_ARTIFACT, second_local_commit["staged_files"])
        _assert_clean_worktree(self, second_status_lines, "after second Web Run")


def _write_temp_project(root: Path) -> None:
    _run_script(root, "planctl.py", "init", "--project-name", "Web Run Smoke")
    _run_script(root, "planctl.py", "initiative", "create", "--title", "Web Run")
    _run_script(
        root,
        "planctl.py",
        "epic",
        "create",
        "--initiative",
        "INIT-001",
        "--title",
        "Local Commit",
    )
    _write_docs_fixture(root)
    _run_script(root, "taskctl.py", "init")
    _create_smoke_task(
        root,
        title="Web Run local commit smoke",
        summary="Exercise selected Web Run through artifact, close, and local commit.",
        artifact=ARTIFACT,
    )
    _create_smoke_task(
        root,
        title="Web Run second local commit smoke",
        summary="Exercise a second Web Run after the first local commit.",
        artifact=SECOND_ARTIFACT,
    )
    _write_preaccepted_change(root)
    for script in ("planctl.py", "taskctl.py", "docctl.py"):
        _run_script(root, script, "render")
    (root / ".gitignore").write_text(
        "AI_PROJECT/.locks/\nAI_PROJECT/logs/\n",
        encoding="utf-8",
    )
    _git(root, "init")
    _git(root, "add", ".")
    _git(
        root,
        "-c",
        "user.email=tester@example.com",
        "-c",
        "user.name=Tester",
        "commit",
        "-m",
        "baseline",
    )


def _create_smoke_task(root: Path, *, title: str, summary: str, artifact: str) -> None:
    _run_script(
        root,
        "taskctl.py",
        "task",
        "create",
        "--epic",
        "EPIC-001",
        "--title",
        title,
        "--status",
        "ready",
        "--summary",
        summary,
        "--description",
        "Temporary smoke fixture.",
        "--scope",
        "Create one allowed artifact file.",
        "--out-of-scope",
        "Do not use external Codex.",
        "--allowed-file",
        artifact,
        "--acceptance",
        "Allowed artifact reaches report gate and local commit readiness.",
        "--review-instruction",
        "Check report changed_files and close commit artifacts.",
        "--verification-mode",
        "strict",
    )


def _write_docs_fixture(root: Path) -> None:
    docs_dir = root / "docs"
    state_dir = root / "AI_PROJECT" / "state"
    docs_dir.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "test.md").write_text("# Test Doc\n\nStatus: Active\n", encoding="utf-8")
    now = "2026-06-28T00:00:00Z"
    (state_dir / "docs.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 1,
                "created_at": now,
                "updated_at": now,
                "docs": [
                    {
                        "id": "DOC-001",
                        "path": "docs/test.md",
                        "title": "Test Doc",
                        "type": "guide",
                        "status": "active",
                        "required": True,
                        "owner": "tester",
                        "last_reviewed_at": "",
                        "last_reviewed_by": "",
                        "content_hash": "",
                        "last_reviewed_content_hash": "",
                        "declared_status": "",
                        "declared_status_raw": "",
                        "declared_status_source": "",
                        "notes": [],
                        "created_at": now,
                        "updated_at": now,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    _run_script(root, "docctl.py", "doc", "mark-reviewed", "docs/test.md", "--note", "reviewed")
    _run_script(root, "docctl.py", "render")


def _write_preaccepted_change(root: Path) -> None:
    _run_script(root, "evolutionctl.py", "init")
    _run_script(
        root,
        "evolutionctl.py",
        "change",
        "create",
        "--title",
        "Approve Web Run smoke",
        "--type",
        "tooling",
        "--status",
        "draft",
        "--problem",
        "The temp task needs an accepted Change gate.",
        "--proposal",
        "Approve the isolated temp smoke task.",
    )
    _run_script(
        root,
        "evolutionctl.py",
        "change",
        "add-affected-file",
        "CHG-001",
        "--text",
        ARTIFACT,
    )
    _run_script(
        root,
        "evolutionctl.py",
        "change",
        "add-affected-file",
        "CHG-001",
        "--text",
        SECOND_ARTIFACT,
    )
    _run_script(root, "evolutionctl.py", "change", "link-task", "CHG-001", "--task", TASK_ID)
    _run_script(
        root,
        "evolutionctl.py",
        "change",
        "link-task",
        "CHG-001",
        "--task",
        SECOND_TASK_ID,
    )
    _run_script(root, "evolutionctl.py", "change", "transition", "CHG-001", "--to", "ready")
    _run_script(root, "evolutionctl.py", "change", "approve", "CHG-001", "--notes", "Approved.")
    _run_script(root, "evolutionctl.py", "change", "transition", "CHG-001", "--to", "in_progress")
    _run_script(root, "evolutionctl.py", "change", "transition", "CHG-001", "--to", "in_review")
    _run_script(root, "evolutionctl.py", "render")
    _run_script(
        root,
        "evolutionctl.py",
        "change",
        "accept",
        "CHG-001",
        "--notes",
        "Accepted before smoke execution.",
        "--skip-task-check",
    )


def _web_run_local_commit_policy():
    base = apply_codex_review_requirement(
        policy_preset("supervised_executable_local_commit"),
        require_codex_review=False,
    )
    return replace(
        base,
        name="web_run_local_commit_smoke",
        batch=BatchPolicy(max_steps=10, max_failures=1),
        verify=replace(base.verify, run_git_diff_gates=False),
        closure=replace(base.closure, owner_approval_note=AUTO_CLOSE_NOTE),
    )


def _controlled_pipeline_runner(root: Path):
    def run(argv, prompt_text=None, **_kwargs):
        args = list(argv)
        if args and args[0] == "git":
            return subprocess.run(
                args,
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        if tuple(args[-2:]) in {
            ("project", "doctor"),
            ("project", "protected-check"),
        }:
            return subprocess.CompletedProcess(
                args=args,
                returncode=0,
                stdout=json.dumps({"ok": True, "errors": [], "warnings": [], "findings": []}) + "\n",
                stderr="",
            )
        if args == ["codex", "exec"]:
            task_id, artifact = _task_artifact_from_prompt(prompt_text or "")
            path = root / artifact
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "artifact created by fake codex for {}\n".format(task_id),
                encoding="utf-8",
            )
            summary = {
                "implementation_summary": "Created allowed artifact for {}.".format(
                    task_id
                ),
                "notes": [],
                "warnings": [],
                "blockers": [],
            }
            stdout = "CODEX_EXECUTION_SUMMARY_JSON:\n```json\n{}\n```\n".format(
                json.dumps(summary)
            )
            return subprocess.CompletedProcess(args=args, returncode=0, stdout=stdout, stderr="")
        if len(args) > 1 and Path(args[1]).name in {
            "aictl.py",
            "codexctl.py",
            "contextctl.py",
            "docctl.py",
            "evolutionctl.py",
            "planctl.py",
            "taskctl.py",
        }:
            return subprocess.run(
                args,
                cwd=REPO_ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        raise AssertionError("unexpected command: {}".format(args))

    return run


def _task_artifact_from_prompt(prompt_text: str) -> tuple[str, str]:
    if SECOND_TASK_ID in prompt_text:
        return SECOND_TASK_ID, SECOND_ARTIFACT
    return TASK_ID, ARTIFACT


def _workflow_result_with_smoke_effects(original):
    def wrapped(executor, descriptor, **kwargs):
        result = original(executor, descriptor, **kwargs)
        if descriptor.name == "task.close_reviewed":
            _extend_unique(
                result.changed_files,
                WEB_RUN_GOVERNED_SIDE_EFFECT_CHANGED_FILES,
            )
            _extend_unique(
                result.generated_files,
                WEB_RUN_GOVERNED_SIDE_EFFECT_GENERATED_FILES,
            )
            _extend_unique(
                result.events,
                (
                    "AI_PROJECT/events/codex-events.jsonl",
                    "AI_PROJECT/events/task-events.jsonl",
                    "AI_PROJECT/events/task-report-events.jsonl",
                ),
            )
        return result

    return wrapped


def _workflow_subprocess_for_smoke(_executor, argv):
    args = list(argv)
    script = Path(args[1]).name if len(args) > 1 else ""
    if script == "evolutionctl.py" and any(
        command in args for command in ("validate", "check-generated")
    ):
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout="OK: evolution validation stubbed for Web Run smoke\n",
            stderr="",
        )
    if script == "check-protected-project-files.py":
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=json.dumps({"ok": True, "errors": [], "warnings": []}) + "\n",
            stderr="",
        )
    if script == "aictl.py" and tuple(args[-2:]) == ("project", "doctor"):
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=json.dumps(
                {"ok": True, "errors": [], "warnings": [], "findings": []}
            )
            + "\n",
            stderr="",
        )
    return subprocess.run(
        args,
        cwd=workflow_module.PACKAGE_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _passing_machine_review(root=None, task=None, policy=None, report_gate=None, **_kwargs):
    task_id = str((task or {}).get("id") or TASK_ID)
    report_id = str(getattr(report_gate, "report_id", "") or "")
    checks = tuple(
        MachineCheckEvidence(
            name=name,
            status="pass",
            code="MACHINE_REVIEW_PASS",
            reason="{} passed.".format(name),
        )
        for name in sorted(REQUIRED_MACHINE_CHECKS)
    )
    return MachineReviewResult(
        status="pass",
        code="MACHINE_REVIEW_PASS",
        reason="Machine Review PASS for Web Run smoke.",
        task_id=task_id,
        report_id=report_id,
        checks=checks,
    )


def _run_script(root: Path, script_name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / script_name),
            "--root",
            str(root),
            "--actor",
            "tester",
            *args,
        ],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def _tasks_state(root: Path) -> dict:
    return json.loads((root / "AI_PROJECT" / "state" / "tasks.json").read_text(encoding="utf-8"))


def _pipeline_state(root: Path) -> dict:
    return json.loads(pipeline_state_path(root).read_text(encoding="utf-8"))


def _latest_report(root: Path) -> dict:
    return _reports_state(root)["reports"][-1]


def _latest_report_for_task(reports: list[dict], task_id: str) -> dict:
    for item in reversed(reports):
        if item.get("task_id") == task_id:
            return item
    raise AssertionError("missing report for task: {}".format(task_id))


def _reports_state(root: Path) -> dict:
    return json.loads(
        (root / "AI_PROJECT" / "state" / "task_reports.json").read_text(encoding="utf-8")
    )


def _latest_phase(session: dict, phase: str) -> dict:
    for item in reversed(session["phase_history"]):
        if item.get("phase") == phase:
            return item
    raise AssertionError("missing phase: {}".format(phase))


def _git_status_lines(root: Path) -> list[str]:
    return [
        line.strip()
        for line in _git(
            root,
            "status",
            "--short",
            "--untracked-files=all",
        ).stdout.splitlines()
        if line.strip()
    ]


def _git_status_paths(status_lines: list[str]) -> list[str]:
    return [line[3:].strip() if len(line) > 3 else line for line in status_lines]


def _assert_clean_worktree(
    test_case: unittest.TestCase,
    status_lines: list[str],
    label: str,
) -> None:
    dirty_paths = _git_status_paths(status_lines)
    for path in PIPELINE_BOOKKEEPING_FILES:
        test_case.assertNotIn(path, dirty_paths, "{} left {} dirty".format(label, path))
    test_case.assertEqual(status_lines, [], "{} left dirty files: {}".format(label, status_lines))


def _extend_unique(target: list[str], values) -> None:
    seen = set(target)
    for value in values:
        text = str(value)
        if text and text not in seen:
            target.append(text)
            seen.add(text)


if __name__ == "__main__":
    unittest.main()

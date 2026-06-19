import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
LEGACY_CTL_SCRIPTS = (
    "planctl.py",
    "taskctl.py",
    "docctl.py",
    "contextctl.py",
    "codexctl.py",
    "evolutionctl.py",
)
REQUIRED_DOCS = (
    "ai-system/project-control/01-overview.md",
    "ai-system/project-control/02-domain-model.md",
    "ai-system/project-control/03-state-model.md",
    "ai-system/project-control/04-command-catalog.md",
    "ai-system/project-control/05-lifecycle-rules.md",
    "ai-system/project-control/06-prompt-package-spec.md",
    "ai-system/project-control/07-validation-and-tests.md",
)


def read_jsonl(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_required_docs(root):
    for doc_path in REQUIRED_DOCS:
        path = root / doc_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Fixture\n\nStatus: active\n\nCompatibility fixture.\n", encoding="utf-8")


class LegacyCtlWrapperTests(unittest.TestCase):
    def run_ctl(self, script, root, *args):
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
        self.assertEqual(
            completed.returncode,
            0,
            "{} failed\nstdout:\n{}\nstderr:\n{}".format(
                script,
                completed.stdout,
                completed.stderr,
            ),
        )
        return completed

    def test_legacy_scripts_do_not_delegate_back_to_aictl(self):
        for script in LEGACY_CTL_SCRIPTS:
            with self.subTest(script=script):
                text = (SCRIPTS / script).read_text(encoding="utf-8")
                self.assertNotIn("subprocess", text)
                self.assertNotIn("aictl.py", text)

    def test_legacy_commands_keep_outputs_and_audit_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            self.run_ctl("planctl.py", root, "init", "--project-name", "Wrapper Test")
            self.run_ctl("planctl.py", root, "initiative", "create", "--title", "Project Control")
            self.run_ctl(
                "planctl.py",
                root,
                "epic",
                "create",
                "--initiative",
                "INIT-001",
                "--title",
                "Task Control",
            )

            self.run_ctl("taskctl.py", root, "init")
            created = self.run_ctl(
                "taskctl.py",
                root,
                "task",
                "create",
                "--epic",
                "EPIC-001",
                "--title",
                "Wrapper Task",
                "--status",
                "ready",
                "--scope",
                "Exercise legacy command compatibility.",
                "--allowed-file",
                "README.md",
                "--acceptance",
                "Legacy command output and events remain compatible.",
                "--verification-mode",
                "standard",
            )
            self.assertIn("Created:", created.stdout)

            self.run_ctl("taskctl.py", root, "current", "set", "TASK-001")
            current = self.run_ctl("taskctl.py", root, "current", "show", "--json")
            self.assertEqual(json.loads(current.stdout)["id"], "TASK-001")

            write_required_docs(root)
            self.run_ctl("docctl.py", root, "init")
            self.run_ctl("contextctl.py", root, "pack", "build", "--task", "TASK-001", "--write")
            self.run_ctl("codexctl.py", root, "build", "--task", "TASK-001")
            self.run_ctl("evolutionctl.py", root, "init")
            change = self.run_ctl(
                "evolutionctl.py",
                root,
                "change",
                "create",
                "--title",
                "Wrapper Change",
                "--type",
                "tooling",
                "--problem",
                "Legacy wrappers need compatibility coverage.",
                "--proposal",
                "Keep legacy commands stable while using shared core helpers.",
            )
            self.assertIn("Created: CHG-001", change.stdout)

            events = {
                "plan": read_jsonl(root / "AI_PROJECT/events/plan-events.jsonl"),
                "task": read_jsonl(root / "AI_PROJECT/events/task-events.jsonl"),
                "doc": read_jsonl(root / "AI_PROJECT/events/doc-events.jsonl"),
                "context": read_jsonl(root / "AI_PROJECT/events/context-events.jsonl"),
                "codex": read_jsonl(root / "AI_PROJECT/events/codex-events.jsonl"),
                "evolution": read_jsonl(root / "AI_PROJECT/events/evolution-events.jsonl"),
            }

            self.assertEqual(
                [event["command"] for event in events["plan"]],
                ["plan.init", "initiative.create", "epic.create"],
            )
            self.assertIn("task.create", [event["command"] for event in events["task"]])
            self.assertEqual(events["doc"][0]["command"], "init")
            self.assertEqual(events["context"][0]["command"], "context.pack.build")
            self.assertEqual(events["codex"][0]["command"], "codex.prompt.build")
            self.assertEqual(
                [event["command"] for event in events["evolution"]],
                ["evolution.init", "change.create"],
            )


if __name__ == "__main__":
    unittest.main()

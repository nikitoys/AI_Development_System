import json
import unittest

from ai_project_ctl.pipeline.artifact_bounds import (
    TRUNCATED_TEXT_REASON,
    bound_pipeline_artifact,
)
from ai_project_ctl.pipeline.state import MAX_STORED_STRING_LENGTH


class PipelineArtifactBoundsTests(unittest.TestCase):
    def test_bounds_nested_workflow_stdout_and_stderr(self):
        oversized_stdout = "stdout:" + ("x" * (MAX_STORED_STRING_LENGTH + 1))
        oversized_stderr = "stderr:" + ("y" * (MAX_STORED_STRING_LENGTH + 2))
        payload = {
            "ok": False,
            "command": "pipeline.review_close_policy",
            "message": "Review close workflow failed: task.close_reviewed",
            "data": {
                "failed_workflow": "task.close_reviewed",
                "workflows": [
                    {
                        "command": "task.close_reviewed",
                        "data": {
                            "steps": [
                                {
                                    "id": "task_done",
                                    "command_name": "task.transition",
                                    "returncode": 1,
                                    "stdout": oversized_stdout,
                                    "stderr": oversized_stderr,
                                }
                            ]
                        },
                    }
                ],
            },
            "errors": [
                {
                    "code": "WORKFLOW_STEP_FAILED",
                    "message": "Workflow step failed: Move task to done",
                    "details": {
                        "step": "task_done",
                        "command_name": "task.transition",
                        "returncode": 1,
                        "stdout": oversized_stdout,
                    },
                }
            ],
        }

        bounded = bound_pipeline_artifact(payload)

        step = bounded["data"]["workflows"][0]["data"]["steps"][0]
        self.assertEqual(bounded["data"]["failed_workflow"], "task.close_reviewed")
        self.assertEqual(step["id"], "task_done")
        self.assertEqual(step["command_name"], "task.transition")
        self.assertEqual(step["returncode"], 1)

        stdout = step["stdout"]
        stderr = step["stderr"]
        self.assertEqual(stdout["reason"], TRUNCATED_TEXT_REASON)
        self.assertEqual(stderr["reason"], TRUNCATED_TEXT_REASON)
        self.assertTrue(stdout["truncated"])
        self.assertTrue(stderr["truncated"])
        self.assertEqual(stdout["field"], "stdout")
        self.assertEqual(stderr["field"], "stderr")
        self.assertEqual(stdout["original_size"], len(oversized_stdout))
        self.assertEqual(stderr["original_size"], len(oversized_stderr))
        self.assertLess(stdout["stored_size"], MAX_STORED_STRING_LENGTH)
        self.assertLess(stderr["stored_size"], MAX_STORED_STRING_LENGTH)

        error = bounded["errors"][0]
        self.assertEqual(error["code"], "WORKFLOW_STEP_FAILED")
        self.assertEqual(error["message"], "Workflow step failed: Move task to done")
        self.assertEqual(error["details"]["returncode"], 1)
        self.assertEqual(error["details"]["stdout"]["field"], "stdout")

        encoded = json.dumps(bounded, sort_keys=True)
        self.assertNotIn(oversized_stdout, encoded)
        self.assertNotIn(oversized_stderr, encoded)

    def test_keeps_compact_strings_unchanged(self):
        payload = {"stdout": "short output", "nested": [{"stderr": ""}]}

        self.assertEqual(bound_pipeline_artifact(payload), payload)


if __name__ == "__main__":
    unittest.main()

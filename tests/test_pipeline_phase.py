import json
import unittest

from ai_project_ctl.pipeline.phase import (
    PHASE_STATUSES,
    PhaseResult,
    PhaseStatus,
    PipelinePhaseError,
)


class PipelinePhaseResultTests(unittest.TestCase):
    def test_phase_result_round_trips_all_statuses(self):
        factories = {
            "passed": PhaseResult.passed,
            "blocked": PhaseResult.blocked,
            "failed": PhaseResult.failed,
            "skipped": PhaseResult.skipped,
        }

        self.assertEqual(set(PHASE_STATUSES), set(factories))

        for status, factory in factories.items():
            with self.subTest(status=status):
                result = factory(
                    " prepare ",
                    reason=" done ",
                    next_action=" continue ",
                    artifacts={"status": status, "items": [1, True, None]},
                    changed_files=(" tests/example.py ",),
                    generated_files=(" AI_PROJECT/generated/EXAMPLE.md ",),
                    events=(" EVT-001 ",),
                )

                payload = result.to_dict()

                self.assertEqual(payload["phase"], "prepare")
                self.assertEqual(payload["status"], status)
                self.assertEqual(payload["reason"], "done")
                self.assertEqual(payload["next_action"], "continue")
                self.assertEqual(payload["changed_files"], ["tests/example.py"])
                self.assertEqual(
                    payload["generated_files"],
                    ["AI_PROJECT/generated/EXAMPLE.md"],
                )
                self.assertEqual(payload["events"], ["EVT-001"])
                self.assertEqual(json.loads(json.dumps(payload)), payload)
                self.assertEqual(PhaseResult.from_dict(payload).to_dict(), payload)
                self.assertEqual(
                    result.to_command_data(),
                    {"phase_result": payload},
                )

    def test_phase_result_accepts_enum_status(self):
        result = PhaseResult("execute", PhaseStatus.PASSED)

        self.assertEqual(result.status, PhaseStatus.PASSED)
        self.assertEqual(result.to_dict()["status"], "passed")

    def test_phase_result_rejects_invalid_payloads(self):
        cases = [
            ({}, "PIPELINE_PHASE_REQUIRED_FIELD"),
            ({"phase": "", "status": "passed"}, "PIPELINE_PHASE_NAME_REQUIRED"),
            ({"phase": "bad phase", "status": "passed"}, "PIPELINE_PHASE_INVALID_NAME"),
            ({"phase": "prepare", "status": "unknown"}, "PIPELINE_PHASE_INVALID_STATUS"),
            (
                {"phase": "prepare", "status": "passed", "artifacts": object()},
                "PIPELINE_PHASE_INVALID_ARTIFACTS",
            ),
            (
                {"phase": "prepare", "status": "passed", "changed_files": [""]},
                "PIPELINE_PHASE_INVALID_LIST_ITEM",
            ),
        ]

        for payload, code in cases:
            with self.subTest(code=code):
                with self.assertRaises(PipelinePhaseError) as raised:
                    PhaseResult.from_dict(payload)
                self.assertEqual(raised.exception.code, code)


if __name__ == "__main__":
    unittest.main()

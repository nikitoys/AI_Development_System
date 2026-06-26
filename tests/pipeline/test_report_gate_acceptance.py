import unittest
from dataclasses import replace

from ai_project_ctl.pipeline.policy import PipelinePolicy
from ai_project_ctl.pipeline.report_gate import (
    CODE_BLOCKERS_PRESENT,
    CODE_INVALID_SCHEMA,
    CODE_OUT_OF_SCOPE_FILE,
    CODE_PASS,
    CODE_WARN,
    FAIL,
    PASS,
    WARN,
    ReportGateResult,
    evaluate_report_gate_acceptance,
)


def _policy(*, allow_report_warnings: bool = False) -> PipelinePolicy:
    policy = PipelinePolicy()
    return replace(
        policy,
        verify=replace(policy.verify, allow_report_warnings=allow_report_warnings),
    )


def _report_gate(*, status: str, code: str) -> ReportGateResult:
    return ReportGateResult(
        status=status,
        code=code,
        reason="gate reason",
        report_id="RPT-001",
        task_id="TASK-001",
    )


class ReportGateAcceptanceTests(unittest.TestCase):
    def test_pass_allows_downstream(self):
        result = evaluate_report_gate_acceptance(
            _report_gate(status=PASS, code=CODE_PASS),
            _policy(),
        )

        self.assertTrue(result.allow)
        self.assertEqual(result.report_gate_code, CODE_PASS)

    def test_warn_allows_downstream_when_policy_allows_report_warnings(self):
        result = evaluate_report_gate_acceptance(
            _report_gate(status=WARN, code=CODE_WARN),
            _policy(allow_report_warnings=True),
        )

        self.assertTrue(result.allow)
        self.assertEqual(result.report_gate_code, CODE_WARN)

    def test_warn_blocks_downstream_when_policy_disallows_report_warnings(self):
        result = evaluate_report_gate_acceptance(
            _report_gate(status=WARN, code=CODE_WARN),
            _policy(allow_report_warnings=False),
        )

        self.assertFalse(result.allow)
        self.assertEqual(result.report_gate_code, CODE_WARN)

    def test_fail_blocks_downstream(self):
        for code in (
            CODE_INVALID_SCHEMA,
            CODE_BLOCKERS_PRESENT,
            CODE_OUT_OF_SCOPE_FILE,
        ):
            with self.subTest(code=code):
                result = evaluate_report_gate_acceptance(
                    _report_gate(status=FAIL, code=code),
                    _policy(allow_report_warnings=True),
                )

                self.assertFalse(result.allow)
                self.assertEqual(result.report_gate_code, code)


if __name__ == "__main__":
    unittest.main()

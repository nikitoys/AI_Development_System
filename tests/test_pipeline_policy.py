import unittest
from dataclasses import replace

from ai_project_ctl.pipeline import (
    BatchPolicy,
    CodexAdapterMode,
    CodexExecutionMode,
    CodexReviewDecision,
    CommitMode,
    CommitPolicy,
    EvolutionChangePolicy,
    MachineReviewOutcome,
    PipelinePolicy,
    PromptTransport,
    QueuePolicy,
    ReworkPolicy,
    ReviewPolicy,
    TaskClosurePolicy,
    TokenBudgetPolicy,
    policy_preset,
    preset_names,
)


def error_codes(policy):
    return [issue.code for issue in policy.validate().errors]


class PipelinePolicyTests(unittest.TestCase):
    def test_default_policy_is_safe_and_inert(self):
        policy = PipelinePolicy.default()

        self.assertTrue(policy.validate().ok)
        self.assertEqual(policy.codex.mode, CodexExecutionMode.DISABLED)
        self.assertEqual(policy.codex.adapter_mode, CodexAdapterMode.MANUAL_HANDOFF)
        self.assertEqual(policy.codex.prompt_transport, PromptTransport.STDIN)
        self.assertFalse(policy.closure.auto_close_task)
        self.assertEqual(policy.closure.owner_approval_note, "")
        self.assertFalse(policy.evolution.accept_linked_change)
        self.assertFalse(policy.commit.create_local_commit)
        self.assertFalse(policy.commit.allow_push)
        self.assertFalse(policy.commit.allow_merge)
        self.assertEqual(policy.batch.max_failures, 1)

    def test_safe_presets_validate(self):
        self.assertEqual(
            preset_names(),
            (
                "dry_run",
                "supervised",
                "supervised_executable",
                "supervised_autoclose",
                "supervised_executable_autoclose",
                "supervised_local_commit",
                "supervised_executable_local_commit",
            ),
        )

        for name in preset_names():
            with self.subTest(name=name):
                policy = policy_preset(name)

                self.assertTrue(policy.validate().ok)
                self.assertEqual(policy.name, name)

    def test_autoclose_requires_machine_pass_and_codex_approve(self):
        policy = replace(
            PipelinePolicy.default(),
            closure=TaskClosurePolicy(auto_close_task=True),
        )

        self.assertEqual(
            error_codes(policy),
            [
                "POLICY_AUTO_CLOSE_REQUIRES_MACHINE_REVIEW_PASS",
                "POLICY_AUTO_CLOSE_REQUIRES_CODEX_REVIEW_APPROVE",
            ],
        )

        missing_codex_approve = replace(
            policy,
            review=ReviewPolicy(
                require_machine_review=True,
                required_machine_outcome=MachineReviewOutcome.PASS,
                require_codex_review=True,
                required_codex_decision=CodexReviewDecision.NONE,
            ),
        )

        self.assertEqual(
            error_codes(missing_codex_approve),
            ["POLICY_AUTO_CLOSE_REQUIRES_CODEX_REVIEW_APPROVE"],
        )

    def test_codex_run_requires_token_gate_and_approved_change_gate(self):
        supervised = policy_preset("supervised")
        unsafe = replace(
            supervised,
            codex=replace(supervised.codex, mode=CodexExecutionMode.RUN_CODEX),
            token_budget=replace(supervised.token_budget, require_gate_pass=False),
            evolution=replace(
                supervised.evolution,
                require_approved_change_for_execution=False,
            ),
        )

        self.assertEqual(
            error_codes(unsafe),
            [
                "POLICY_EXECUTION_WITHOUT_APPROVED_CHANGE_GATE",
                "POLICY_EXECUTION_WITHOUT_TOKEN_GATE",
            ],
        )

    def test_local_codex_command_requires_explicit_allowlist_and_report(self):
        supervised = policy_preset("supervised")
        unsafe = replace(
            supervised,
            codex=replace(
                supervised.codex,
                mode=CodexExecutionMode.RUN_CODEX,
                adapter_mode=CodexAdapterMode.LOCAL_COMMAND,
                local_command=("codex", "exec"),
                command_allowlist=(),
                require_report=False,
            ),
        )

        self.assertEqual(
            error_codes(unsafe),
            [
                "POLICY_CODEX_REQUIRES_REPORT",
                "POLICY_CODEX_COMMAND_NOT_ALLOWLISTED",
            ],
        )

        safe = replace(
            unsafe,
            codex=replace(
                unsafe.codex,
                command_allowlist=("codex exec",),
                require_report=True,
            ),
        )

        self.assertTrue(safe.validate().ok)

    def test_executable_presets_use_local_codex_adapter(self):
        executable = policy_preset("supervised_executable")
        autoclose = policy_preset("supervised_executable_autoclose")
        local_commit = policy_preset("supervised_executable_local_commit")

        for policy in (executable, autoclose, local_commit):
            with self.subTest(policy=policy.name):
                self.assertTrue(policy.validate().ok)
                self.assertEqual(policy.codex.mode, CodexExecutionMode.RUN_CODEX)
                self.assertEqual(policy.codex.adapter_mode, CodexAdapterMode.LOCAL_COMMAND)
                self.assertEqual(policy.codex.prompt_transport, PromptTransport.STDIN)
                self.assertEqual(policy.codex.local_command, ("codex", "exec"))
                self.assertEqual(policy.codex.command_allowlist, ("codex exec",))
                self.assertTrue(policy.codex.require_report)

        self.assertFalse(executable.closure.auto_close_task)
        self.assertTrue(autoclose.closure.auto_close_task)
        self.assertTrue(local_commit.closure.auto_close_task)
        self.assertTrue(local_commit.commit.create_local_commit)

    def test_policy_rejects_automatic_change_approval_and_acceptance(self):
        policy = replace(
            PipelinePolicy.default(),
            evolution=EvolutionChangePolicy(
                create_missing_change=True,
                approve_linked_change=True,
                accept_linked_change=True,
                require_approved_change_for_execution=True,
            ),
        )

        self.assertEqual(
            error_codes(policy),
            [
                "POLICY_APPROVES_EVOLUTION_CHANGE",
                "POLICY_ACCEPTS_EVOLUTION_CHANGE",
            ],
        )

    def test_commit_policy_is_local_only_and_readiness_gated(self):
        policy = policy_preset("supervised_local_commit")

        self.assertTrue(policy.validate().ok)
        self.assertEqual(policy.commit.mode, CommitMode.LOCAL_ONLY)
        self.assertTrue(policy.commit.require_commit_readiness)
        self.assertFalse(policy.commit.allow_push)
        self.assertFalse(policy.commit.allow_merge)

        unsafe = replace(
            policy,
            commit=CommitPolicy(
                create_local_commit=True,
                mode=CommitMode.DISABLED,
                require_commit_readiness=False,
                allow_push=True,
                allow_merge=True,
            ),
        )

        self.assertEqual(
            error_codes(unsafe),
            [
                "POLICY_PUSH_FORBIDDEN",
                "POLICY_MERGE_FORBIDDEN",
                "POLICY_COMMIT_MUST_BE_LOCAL_ONLY",
                "POLICY_COMMIT_REQUIRES_COMMIT_READINESS",
            ],
        )

    def test_commit_requires_approved_reviews(self):
        policy = replace(
            PipelinePolicy.default(),
            commit=CommitPolicy(
                create_local_commit=True,
                mode=CommitMode.LOCAL_ONLY,
                require_commit_readiness=True,
            ),
        )

        self.assertEqual(error_codes(policy), ["POLICY_COMMIT_REQUIRES_APPROVED_REVIEWS"])

    def test_rework_loop_must_be_bounded_and_owner_gated(self):
        policy = replace(
            PipelinePolicy.default(),
            rework=ReworkPolicy(
                allow_rework_loop=True,
                max_rework_attempts=0,
                require_owner_decision_for_rework=False,
            ),
        )

        self.assertEqual(
            error_codes(policy),
            [
                "POLICY_REWORK_LOOP_REQUIRES_BOUND",
                "POLICY_REWORK_LOOP_REQUIRES_OWNER_DECISION",
            ],
        )

    def test_queue_and_token_threshold_validation(self):
        policy = replace(
            PipelinePolicy.default(),
            queue=QueuePolicy(max_tasks=0, include_blocked_tasks=True),
            batch=BatchPolicy(max_steps=0, max_failures=0),
            token_budget=TokenBudgetPolicy(
                require_gate_pass=True,
                max_prompt_tokens=100,
                max_context_tokens=200,
                min_remaining_tokens=-1,
            ),
        )

        self.assertEqual(
            error_codes(policy),
            [
                "POLICY_INVALID_QUEUE_LIMIT",
                "POLICY_QUEUE_INCLUDES_BLOCKED_TASKS",
                "POLICY_INVALID_TOKEN_THRESHOLD",
                "POLICY_CONTEXT_EXCEEDS_PROMPT_BUDGET",
                "POLICY_BATCH_INVALID_MAX_STEPS",
                "POLICY_BATCH_INVALID_MAX_FAILURES",
            ],
        )

    def test_policy_serialization_round_trip_includes_explicit_action_values(self):
        policy = policy_preset("supervised_local_commit")

        restored = PipelinePolicy.from_dict(policy.to_dict())

        self.assertEqual(restored, policy)
        self.assertEqual(
            sorted(policy.to_dict()),
            [
                "batch",
                "closure",
                "codex",
                "commit",
                "evolution",
                "name",
                "queue",
                "review",
                "rework",
                "token_budget",
            ],
        )
        self.assertEqual(
            sorted(policy.commit.to_dict()),
            [
                "allow_merge",
                "allow_push",
                "create_local_commit",
                "mode",
                "require_commit_readiness",
            ],
        )
        self.assertEqual(
            sorted(policy.codex.to_dict()),
            [
                "adapter_mode",
                "command_allowlist",
                "local_command",
                "mode",
                "prompt_transport",
                "require_human_selected_policy",
                "require_report",
                "timeout_sec",
            ],
        )
        self.assertEqual(
            sorted(policy.closure.to_dict()),
            [
                "auto_close_task",
                "owner_approval_note",
            ],
        )

    def test_unknown_preset_is_rejected(self):
        with self.assertRaises(ValueError):
            policy_preset("reckless")


if __name__ == "__main__":
    unittest.main()

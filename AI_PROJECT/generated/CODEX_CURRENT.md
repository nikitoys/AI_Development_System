<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `652`

Task: `PIPE-26 (TASK-077)` — **PIPE-26 Fix Codex Adapter Prompt Transport**
Epic: `EPIC-007`
Status: `in_review`
Verification: `strict`
Ref: `PIPE-26`
UID: `tsk_c919ccdc6d07`
Legacy ID: `TASK-077`
Aliases: `TASK-077`
Epic Key / Local Seq: `PIPE` / `26`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Fix local Codex adapter so it passes CODEX_PROMPT.md to codex exec instead of running codex exec with no input.

## Description

The executable pipeline currently runs local_command ['codex', 'exec'] without passing AI_PROJECT/generated/CODEX_PROMPT.md through stdin or as an argument. This causes real codex exec to exit non-zero. Add an explicit prompt transport mechanism, defaulting to stdin, and improve adapter diagnostics.

## Scope

- Inspect ai_project_ctl/pipeline/codex_adapter.py local command execution.
- Add prompt transport support for local Codex execution.
- Default prompt transport should pass AI_PROJECT/generated/CODEX_PROMPT.md content to local_command stdin.
- Keep command allowlist validation intact.
- Keep prompt existence, prompt hash, and task identity validation intact.
- Add policy/session support for prompt_transport if needed, with stdin as the default.
- Optionally support future-safe modes such as file_arg or no_prompt, but only if they are explicitly tested.
- Update local command execution so codex exec receives the generated prompt.
- Capture a short safe stdout/stderr snippet in adapter gate details in addition to sha256 refs.
- Limit captured snippets to a safe bounded size to avoid storing large logs or secrets.
- Preserve existing stdout_ref/stderr_ref hash behavior.
- Update report instruction if needed so Codex knows it must submit a structured execution report.
- Add tests where a fake local command asserts that prompt text is received on stdin.
- Add tests for non-zero exit including readable stderr snippet.
- Add tests proving allowlist, timeout, stale prompt, and wrong-task prompt checks still work.
- Update pipeline docs with the expected real Codex command behavior.
- Allow local_command to include explicit Codex sandbox/approval flags, for example a safer owner-configured command such as codex exec --sandbox <mode> when supported by the installed Codex CLI.
- Add a preflight diagnostic that detects Codex sandbox startup failures such as bubblewrap/user-namespace errors and reports them as CODEX_ADAPTER_SANDBOX_UNAVAILABLE instead of generic local_command_nonzero_exit.
- Document how to verify the local Codex CLI command manually before using it in executable pipeline.
- Do not hardcode danger-full-access; require owner-configured policy/command allowlist for any weaker sandbox mode.
- Support owner-configured Codex sandbox mode through local_command, including commands such as codex exec -s workspace-write, codex exec -s danger-full-access, or explicitly allowed bypass mode when the environment is externally sandboxed.
- Do not hardcode danger-full-access or bypass mode in the adapter; allow only owner-configured commands that are present in command_allowlist.
- Default prompt transport must pass CODEX_PROMPT.md to codex exec through stdin.
- Detect Codex sandbox startup failures, including bwrap, loopback, RTM_NEWADDR, Operation not permitted, user namespace, or bubblewrap errors, and report them as CODEX_ADAPTER_SANDBOX_UNAVAILABLE.
- Add diagnostics that include bounded stderr/stdout snippets for failed local Codex commands without storing full prompt text.
- Document manual preflight commands for local Codex execution: codex exec -s workspace-write < AI_PROJECT/generated/CODEX_PROMPT.md and codex exec -s danger-full-access < AI_PROJECT/generated/CODEX_PROMPT.md.

## Out of Scope

- Do not remove command allowlist enforcement.
- Do not use shell=True.
- Do not bypass Token Budget Gate.
- Do not bypass Change approval gate.
- Do not bypass Report Gate, Machine Review, or Codex Review.
- Do not auto-close tasks in this task.
- Do not create local commits in this task.
- Do not push, merge, reset, rebase, clean, restore, or discard git changes.
- Do not store full prompt text in pipeline state, events, generated files, or gate details.
- Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.

## Allowed Files

- ai_project_ctl/pipeline/codex_adapter.py
- ai_project_ctl/pipeline/policy.py
- ai_project_ctl/pipeline/runner.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- scripts/aictl.py
- tests/test_pipeline_codex_adapter.py
- tests/test_pipeline_runner.py
- tests/test_pipeline_e2e.py
- tests/test_web_control_center.py
- ai-system/project-control/pipeline-runner.md
- ai-system/project-control/10-owner-quickstart.md
- AI_PROJECT/state/tasks.json via governed CLI/service only
- AI_PROJECT/events/task-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/CODEX_TASKS.md via governed CLI/service only

## Acceptance Criteria

- Local Codex adapter passes CODEX_PROMPT.md content to codex exec through stdin by default.
- The command ['codex', 'exec'] no longer runs with empty input.
- Command allowlist still validates the command before execution.
- Prompt hash and task identity validation still happen before execution.
- Adapter result includes bounded stdout/stderr snippets for debugging non-zero exits.
- Adapter still records stdout_ref/stderr_ref hashes.
- Non-zero command exit produces actionable diagnostics including returncode and stderr snippet.
- Fake command test verifies prompt content is received on stdin.
- Existing executable pipeline tests pass.
- Project-control validations pass.
- When codex exec fails because bubblewrap/user namespaces are unavailable, adapter reports a clear sandbox compatibility blocker.
- Owner can configure the local Codex command/allowlist to use a Codex CLI sandbox mode supported by the local environment.
- Adapter still refuses any command not present in command_allowlist.
- Adapter passes CODEX_PROMPT.md content to codex exec through stdin by default.
- Owner can configure local_command and command_allowlist to use codex exec -s danger-full-access when workspace-write sandbox is unavailable.
- Adapter refuses any Codex command that is not present in command_allowlist.
- When Codex fails with bwrap/loopback/user-namespace sandbox errors, adapter reports CODEX_ADAPTER_SANDBOX_UNAVAILABLE instead of generic local_command_nonzero_exit.
- Adapter stores only bounded stdout/stderr snippets and hashes, never full prompt text.
- Tests cover stdin prompt transport, sandbox failure detection, allowlist enforcement, and non-zero stderr diagnostics.

## Review Instructions

- Reproduce the original failure: PSESS-008 failed because codex exec was launched without prompt input and returned local_command_nonzero_exit.
- Verify the fixed adapter sends CODEX_PROMPT.md to stdin.
- Verify stderr snippets are visible in gate details when command exits non-zero.
- Verify no full prompt text is stored in pipeline state or events.
- Verify executable pipeline can proceed past Codex adapter when fake command receives stdin and submits a report.

## Notes

- Observed real failure: supervised_executable_local_commit selected PIPE-18/TASK-069, passed Token Budget Gate, then failed at Codex Execution Adapter with local_command_nonzero_exit.
- Adapter command was ['codex', 'exec']; prompt_path existed but was not passed to the process.
- This is a narrow follow-up fix after PIPE-25.
- Manual check showed codex exec supports sandbox modes: read-only, workspace-write, danger-full-access, plus --dangerously-bypass-approvals-and-sandbox. PIPE-26 must keep weaker modes owner-configured and allowlisted, not hardcoded.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-077 --to in_progress
python scripts/taskctl.py task transition TASK-077 --to in_review
python scripts/taskctl.py task approve TASK-077 --notes "..."
python scripts/taskctl.py task transition TASK-077 --to done
python scripts/aictl.py task report submit --task TASK-077 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

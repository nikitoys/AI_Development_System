<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `529`

Task: `PIPE-07 (TASK-058)` — **PIPE-07 Codex Execution Adapter**
Epic: `EPIC-007`
Status: `in_review`
Verification: `strict`
Ref: `PIPE-07`
UID: `tsk_98b7b78bc079`
Legacy ID: `TASK-058`
Aliases: `TASK-058`
Epic Key / Local Seq: `PIPE` / `7`

## Prompt Control Fields

Active Role: `AI System Maintainer / Codex Integration Engineer`
Active Stage: `Codex Execution Adapter Implementation`
Active Document: `ai_project_ctl/pipeline/codex_adapter.py`
Expected Result: `Pipeline can safely invoke or prepare Codex execution through a controlled adapter only when all pre-execution gates pass.`

## Summary

Launch or hand off Codex Executor only after policy and Token Budget Gate PASS, then capture execution metadata.

## Description

Add a controlled Codex execution adapter with dry-run/manual default behavior, explicit policy enablement, timeout, command allowlist, captured output, and report handoff instructions.

## Scope

- Define Codex Execution Adapter interface with dry-run, manual-handoff, and configured-local-command modes if appropriate.
- Require policy permission before any non-dry-run execution.
- Require Token Budget Gate PASS before execution.
- Pass only the generated Codex prompt path/payload and bounded task context.
- Capture start/end time, return code, stdout/stderr references, timeout, and adapter mode.
- Require Codex to submit a structured execution report through the existing report path before downstream gates can pass.
- Stop safely on timeout, non-zero exit, missing prompt, stale prompt, or missing report.
- Add tests with a fake adapter/runner; do not require real Codex in normal test runs.

## Out of Scope

- Do not bypass task allowed_files.
- Do not give Codex permission to push, merge, or approve owner decisions.
- Do not require external Codex services for local tests.
- Do not auto-close tasks based only on adapter success.

## Allowed Files

- ai_project_ctl/pipeline/codex_adapter.py
- ai_project_ctl/pipeline/runner.py if integration is needed
- ai_project_ctl/pipeline/policy.py if policy compatibility is needed
- ai_project_ctl/core/registry.py if command metadata is needed
- scripts/aictl.py if adapter command routing is needed
- tests/**
- ai-system/project-control/** if adapter documentation is needed

## Acceptance Criteria

- Adapter default mode is safe and does not unexpectedly launch external tools.
- Adapter refuses execution unless policy allows it and Token Budget Gate PASS is present.
- Adapter captures execution metadata and exposes it to pipeline session state.
- Adapter failure stops the pipeline with a clear blocker.
- Normal tests use a fake adapter and do not require a real Codex binary/service.
- Tests and project-control validations pass.

## Review Instructions

- Verify no external execution happens by default.
- Verify adapter cannot run before Token Budget Gate PASS.

## Notes

- Requires approved Evolution Change before execution because this can launch Codex when policy allows.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-058 --to in_progress
python scripts/taskctl.py task transition TASK-058 --to in_review
python scripts/taskctl.py task approve TASK-058 --notes "..."
python scripts/taskctl.py task transition TASK-058 --to done
python scripts/aictl.py task report submit --task TASK-058 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

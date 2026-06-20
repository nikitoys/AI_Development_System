<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `615`

Task: `PIPE-17 (TASK-068)` — **PIPE-17 Add Custom Pipeline Policy Preset Store**
Epic: `EPIC-007`
Status: `in_progress`
Verification: `standard`
Ref: `PIPE-17`
UID: `tsk_02b15df91747`
Legacy ID: `TASK-068`
Aliases: `TASK-068`
Epic Key / Local Seq: `PIPE` / `17`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Add governed storage for user-defined pipeline policy presets while keeping built-in safe presets immutable.

## Description

Introduce a persistent custom policy preset store so the Human Owner can save, validate, list, and delete pipeline policy presets without editing Python source or protected state manually.

## Scope

- Create a governed custom pipeline policy preset storage model.
- Store custom presets separately from built-in presets.
- Keep built-in presets dry_run, supervised, supervised_autoclose, and supervised_local_commit immutable.
- Validate saved presets through the existing PipelinePolicy validation rules.
- Reject unsafe presets with stable error codes.
- Add audit events for preset create/update/delete operations.
- Add generated policy status output if useful for UI and validation.

## Out of Scope

- Do not allow custom presets to authorize push, merge, reset, rebase, clean, or destructive git operations.
- Do not allow custom presets to bypass Token Budget Gate, Machine Review, Codex Review, Human Owner approval, or Evolution Change gates.
- Do not modify built-in preset definitions except for compatibility wiring.
- Do not edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/** manually.

## Allowed Files

- ai_project_ctl/pipeline/policy.py
- ai_project_ctl/pipeline/policy_store.py
- ai_project_ctl/pipeline/__init__.py
- ai_project_ctl/core/registry.py
- scripts/aictl.py
- AI_PROJECT/state/pipeline_policy_presets.json via governed CLI/service only
- AI_PROJECT/events/pipeline-policy-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_POLICIES.md via governed CLI/service only
- tests/**

## Acceptance Criteria

- Custom policy presets can be saved, loaded, validated, listed, and deleted through governed service paths.
- Built-in policy presets remain available and immutable.
- Invalid or unsafe custom presets are rejected before persistence.
- Preset changes create audit events.
- No direct protected-file writes are introduced.
- Tests and project-control validations pass.

## Review Instructions

- Verify that custom presets cannot weaken forbidden safety boundaries.
- Verify that built-in presets cannot be overwritten or deleted.
- Verify that all persistence goes through governed service paths.

## Notes

- Requires approved Evolution Change before execution because this changes pipeline policy behavior.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-068 --to in_progress
python scripts/taskctl.py task transition TASK-068 --to in_review
python scripts/taskctl.py task approve TASK-068 --notes "..."
python scripts/taskctl.py task transition TASK-068 --to done
python scripts/aictl.py task report submit --task TASK-068 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

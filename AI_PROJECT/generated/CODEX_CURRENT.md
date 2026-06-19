<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `327`

Task: `WFA-05 (TASK-036)` — **WFA-05 Add Review And Close Helpers**
Epic: `EPIC-006`
Status: `in_progress`
Verification: `standard`
Ref: `WFA-05`
UID: `tsk_78c014419aa9`
Legacy ID: `TASK-036`
Aliases: `TASK-036`
Epic Key / Local Seq: `WFA` / `5`

## Prompt Control Fields

Active Role: `AI System Maintainer / Codex Executor`
Active Stage: `Review And Close Helpers Implementation`
Active Document: `AI_PROJECT/generated/CODEX_TASKS.md`
Expected Result: `Review and close helpers are implemented without bypassing lifecycle gates or owner confirmation.`

## Summary

Add guarded workflow helpers for closing reviewed tasks, accepting linked Evolution Changes, and optionally closing completed Epics.

## Description

Reduce manual closure steps while preserving explicit Human Owner confirmation and approval gates.

## Scope

- Add close_task workflow for tasks in in_review.
- Require approval notes and explicit confirmation.
- Approve task then transition to done through taskctl/aictl path.
- Add accept_change workflow only for approved/in_review changes whose linked tasks are done.
- Add optional close_epic helper only if all child tasks are done/deferred/archived.
- Add tests for confirmation, invalid states, and blocked closure.

## Out of Scope

- Do not auto-approve without Human Owner confirmation.
- Do not close tasks with failing checks unless explicitly allowed by policy.
- Do not accept Changes with incomplete linked tasks.
- Do not close Epics with active tasks.
- Do not bypass lifecycle gates.

## Allowed Files

- ai_project_ctl/core/workflows.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/core/registry.py
- scripts/aictl.py
- tests/**

## Acceptance Criteria

- Owner can close an in_review task with explicit notes and confirmation.
- Owner can accept an Evolution Change only when linked task completion rules pass.
- Invalid close/accept attempts are rejected with clear messages.
- Existing lifecycle semantics are preserved.
- Tests and validations pass.

## Review Instructions

- Verify lifecycle gate preservation, owner confirmation, invalid-state handling, protected-file policy, tests, and validation output.

## Notes

- Depends on WFA-01.
- Depends on WFA-02.
- Requires approved Evolution Change before execution.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-036 --to in_progress
python scripts/taskctl.py task transition TASK-036 --to in_review
python scripts/taskctl.py task approve TASK-036 --notes "..."
python scripts/taskctl.py task transition TASK-036 --to done
python scripts/taskctl.py prompt build --write
```

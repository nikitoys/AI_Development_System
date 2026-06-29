<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `1816`

Task: `PIPEF-161 (TASK-266)` — **Block dirty Web batch starts**
Epic: `EPIC-009`
Status: `in_progress`
Verification: `strict`
Ref: `PIPEF-161`
UID: `tsk_2377b93b98bc`
Legacy ID: `TASK-266`
Aliases: `TASK-266`
Epic Key / Local Seq: `PIPEF` / `161`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Apply dirty worktree preflight to Web batch runs before any multi-task pipeline session is created or executed.

## Description

A batch run must not start from a dirty worktree caused by task import or other owner-side changes.

## Scope

- Run dirty worktree preflight before ui.run_task_batch creates a normal pipeline session.
- Return a not_run batch result when dirty files exist before batch start.
- Include dirty file paths and checkpoint commit guidance in the batch action result.
- Ensure dirty batch preflight does not run Codex, create a session, or transition tasks.

## Out of Scope

- Do not change dirty handoff behavior after a task commit in this task.
- Do not automatically create a checkpoint commit.
- Do not change selected-task dirty preflight behavior.
- Do not edit protected project-control files manually.

## Allowed Files

- ai_project_ctl/web/actions.py
- ai_project_ctl/pipeline/git_status.py
- tests/test_web_control_center.py
- tests/test_ui_run_command.py

## Acceptance Criteria

- A clean worktree allows ui.run_task_batch to create and run a batch session.
- A dirty worktree returns not_run before session creation and before Codex execution.
- The not_run result includes dirty file paths from git status.
- The not_run result includes owner guidance to create a checkpoint commit or clean the worktree.
- The existing ui.checkpoint_commit action remains usable after the dirty batch result.
- Tests cover clean and dirty batch-start preflight behavior.

## Review Instructions

- Verify that dirty preflight is only a start guard and does not interfere with pipeline-owned changes during execution.

## Notes

- This task protects batch starts after task import or manual state changes.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-266 --to in_progress
python scripts/taskctl.py task transition TASK-266 --to in_review
python scripts/taskctl.py task approve TASK-266 --notes "..."
python scripts/taskctl.py task transition TASK-266 --to done
python scripts/aictl.py task report submit --task TASK-266 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

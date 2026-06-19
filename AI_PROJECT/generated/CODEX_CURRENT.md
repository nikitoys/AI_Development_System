<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `456`

Task: `WFA-19 (TASK-050)` — **UIX-13 Add Epic Close UI Action**
Epic: `EPIC-006`
Status: `in_progress`
Verification: `standard`
Ref: `WFA-19`
UID: `tsk_32b3ecc1372f`
Legacy ID: `TASK-050`
Aliases: `TASK-050`
Epic Key / Local Seq: `WFA` / `19`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Expose the epic.close_if_complete workflow in the Web Control Center with clear incomplete-task blocking reasons.

## Description

Allow the owner to close an epic from the UI when all required child tasks are complete, while showing clear reasons when the epic cannot be closed.

## Scope

- Add Close Epic If Complete action to Epic or Dashboard views.
- Route close action through existing epic.close_if_complete workflow.
- Require explicit confirmation before closing an epic.
- Show incomplete tasks when close is blocked.
- Show linked open Changes if they prevent closure or should be reviewed.
- Show task completion counts by status.
- Use unified result panel for success/failure output.
- Add tests for closable epic, incomplete epic, invalid epic, and no direct state writes.

## Out of Scope

- Do not auto-close epics.
- Do not close epics with incomplete tasks.
- Do not auto-accept linked Changes.
- Do not change epic lifecycle rules.
- Do not directly edit plan.json or task state.

## Allowed Files

- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/workflows.py if epic workflow metadata needs compatible updates
- ai_project_ctl/core/registry.py if command metadata needs compatible updates
- tests/test_web_control_center.py
- tests/test_workflows.py
- tests/test_registry.py

## Acceptance Criteria

- UI shows epic completion status and open task counts.
- Close Epic If Complete is available only when valid or explains why it is blocked.
- Close action requires explicit confirmation.
- Close action routes through epic.close_if_complete workflow.
- Blocked close shows incomplete task refs.
- No direct plan/task state writes are introduced.
- Tests and project-control validations pass.

## Review Instructions

- Verify that incomplete epics cannot be closed.
- Verify that blocking tasks are shown clearly.
- Verify that closing an epic does not auto-close tasks or Changes.

## Notes

- Logical label: UIX-13
- Requires approved Evolution Change before execution because Web epic lifecycle behavior changes.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-050 --to in_progress
python scripts/taskctl.py task transition TASK-050 --to in_review
python scripts/taskctl.py task approve TASK-050 --notes "..."
python scripts/taskctl.py task transition TASK-050 --to done
python scripts/aictl.py task report submit --task TASK-050 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

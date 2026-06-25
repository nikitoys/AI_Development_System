<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `1206`

Task: `PIPEF-57 (TASK-136)` — **PIPE-052 Add pipeline session status JSON endpoint**
Epic: `EPIC-009`
Status: `in_progress`
Verification: `strict`
Ref: `PIPEF-57`
UID: `tsk_3b24331932c4`
Legacy ID: `TASK-136`
Aliases: `TASK-136`
Epic Key / Local Seq: `PIPEF` / `57`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Add a read-only JSON endpoint that returns compact live status for one pipeline session.

## Description

This enables the Web Control Center to refresh session status without reloading the full HTML page.

## Scope

- Add a read-only route for compact pipeline session status JSON.
- Return session id, status, current task, current phase, phase status, stop reason, next action and phase history summary.
- Return stable errors for missing or invalid session ids.
- Add focused tests for successful and missing-session responses.

## Out of Scope

- Do not mutate pipeline session state.
- Do not change pipeline execution behavior.
- Do not add frontend polling in this task.

## Allowed Files

- ai_project_ctl/web/server.py
- ai_project_ctl/web/read_model.py
- tests/test_web_control_center.py

## Acceptance Criteria

- The new endpoint returns JSON for an existing pipeline session.
- The JSON payload contains status, current_phase, current_phase_status, stop_reason, next_action and phase_history summary.
- The endpoint does not render full HTML.
- Missing sessions return a stable non-success response.
- Existing Web Control Center pages continue to render.

## Review Instructions

- Verify that the endpoint is read-only and does not invalidate or mutate caches unnecessarily.

## Notes

- This task supports lightweight status polling every few seconds.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-136 --to in_progress
python scripts/taskctl.py task transition TASK-136 --to in_review
python scripts/taskctl.py task approve TASK-136 --notes "..."
python scripts/taskctl.py task transition TASK-136 --to done
python scripts/aictl.py task report submit --task TASK-136 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

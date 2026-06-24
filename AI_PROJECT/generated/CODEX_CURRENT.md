<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `1014`

Task: `PIPEF-66 (TASK-145)` — **PIPE-061 Add Web Settings page route**
Epic: `EPIC-009`
Status: `in_progress`
Verification: `strict`
Ref: `PIPEF-66`
UID: `tsk_432c3c726e2d`
Legacy ID: `TASK-145`
Aliases: `TASK-145`
Epic Key / Local Seq: `PIPEF` / `66`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Add a Web Control Center Settings page that displays effective UI settings and their source file.

## Description

This creates the read-only Web UI surface for project-local settings before adding write actions.

## Scope

- Add a Settings navigation item and route in the Web Control Center.
- Render effective UI settings including source, path and current values.
- Show settings in a human-readable form without requiring terminal commands.
- Add focused tests that the Settings page renders with default and project-file settings.

## Out of Scope

- Do not add settings mutation in this task.
- Do not change pipeline execution behavior.
- Do not expose non-UI project secrets or environment variables.

## Allowed Files

- ai_project_ctl/web/server.py
- tests/test_web_control_center.py

## Acceptance Criteria

- The Web Control Center navigation includes a Settings page link.
- The Settings page shows the effective UI settings source and path.
- The Settings page renders command_line, default_policy and timeout settings when present.
- The Settings page is read-only in this task.
- Existing Web Control Center tests continue to pass.

## Review Instructions

- Verify that the route is read-only and does not mutate settings.

## Notes

- This is the foundation for owner-editable settings in the browser.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-145 --to in_progress
python scripts/taskctl.py task transition TASK-145 --to in_review
python scripts/taskctl.py task approve TASK-145 --notes "..."
python scripts/taskctl.py task transition TASK-145 --to done
python scripts/aictl.py task report submit --task TASK-145 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

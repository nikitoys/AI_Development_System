<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `582`

Task: `PIPE-13 (TASK-064)` — **PIPE-13 Pipeline UI Dashboard**
Epic: `EPIC-007`
Status: `in_progress`
Verification: `standard`
Ref: `PIPE-13`
UID: `tsk_d4153f05f2bc`
Legacy ID: `TASK-064`
Aliases: `TASK-064`
Epic Key / Local Seq: `PIPE` / `13`

## Prompt Control Fields

Active Role: `Frontend Developer AI / Backend Developer AI`
Active Stage: `Pipeline Dashboard UI`
Active Document: `ai_project_ctl/web/server.py / ai_project_ctl/web/read_model.py`
Expected Result: `Human Owner can inspect and operate supervised pipeline sessions from the local UI with explicit confirmation.`

## Summary

Add a Web Control Center dashboard for pipeline sessions, queue preview, policy selection, run-next, and run-until-blocker.

## Description

Expose supervised pipeline operation in the local Web Control Center without weakening confirmation, policy, or lifecycle gates.

## Scope

- Add Pipeline dashboard/page to the Web Control Center.
- Show policy selector/preset preview, queue selector, queue preview, session status, current step, gates, stop reason, and latest audit entries.
- Expose Create Session, Run Next, Run Until Blocker, Stop Session, and Refresh Status actions where implemented.
- Require explicit confirmation for any write/run action.
- Show action result panel with step status, blockers, changed/generated files, reports, reviews, and next actions.
- Keep UI local-only and route writes through governed commands/workflows.
- Add tests for dashboard rendering, confirmation requirements, and action routing.

## Out of Scope

- Do not add remote hosting.
- Do not bypass pipeline policy.
- Do not auto-start sessions on page load.
- Do not run arbitrary shell commands from UI.
- Do not hide blockers or failed gates.

## Allowed Files

- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/pipeline/** if UI integration requires compatible changes
- ai_project_ctl/core/registry.py if action metadata is needed
- scripts/aictl.py if routing is needed
- tests/test_web_control_center.py
- tests/**
- ai-system/project-control/** if UI documentation is needed

## Acceptance Criteria

- Pipeline dashboard shows sessions, selected policy, queue preview, current step, and stop reason.
- Run actions require explicit confirmation.
- UI writes route through governed commands/workflows.
- Failed gates and blockers are visible.
- UI remains local-only by default.
- Tests and project-control validations pass.

## Review Instructions

- Verify UI cannot start or continue pipeline silently.
- Verify all mutations route through governed command paths.

## Notes

- Requires approved Evolution Change before execution because this adds pipeline UI actions.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-064 --to in_progress
python scripts/taskctl.py task transition TASK-064 --to in_review
python scripts/taskctl.py task approve TASK-064 --notes "..."
python scripts/taskctl.py task transition TASK-064 --to done
python scripts/aictl.py task report submit --task TASK-064 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

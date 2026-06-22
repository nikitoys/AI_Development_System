<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `942`

Task: `PIPEF-50 (TASK-129)` — **Add Codex preflight for UI Run**
Epic: `EPIC-009`
Status: `in_progress`
Verification: `strict`
Ref: `PIPEF-50`
UID: `tsk_e7309de4e114`
Legacy ID: `TASK-129`
Aliases: `TASK-129`
Epic Key / Local Seq: `PIPEF` / `50`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Add a Codex executable preflight that checks the configured command before launching an executable Run.

## Description

This task prevents the Run command from starting executable sessions when the local Codex sandbox is unavailable.

## Scope

- Add a Codex preflight service that reads command_line from effective UI settings.
- Run a minimal prompt through the configured command.
- Detect sandbox-unavailable output such as bwrap or RTM_NEWADDR.
- Expose the preflight through aictl for UI and backend usage.

## Out of Scope

- Do not attempt to repair OS-level sandbox permissions.
- Do not change Codex CLI configuration files.
- Do not mutate task, pipeline, or report state during preflight.

## Allowed Files

- ai_project_ctl/pipeline/codex_preflight.py
- ai_project_ctl/pipeline/codex_adapter.py
- ai_project_ctl/ui_settings.py
- scripts/aictl.py
- tests/pipeline/test_codex_preflight.py

## Acceptance Criteria

- Preflight returns passed when the configured command exits successfully.
- Preflight returns a blocked result when bwrap, RTM_NEWADDR, user namespace, or Operation not permitted appears in output.
- Preflight uses the effective command_line setting.
- Preflight does not write project-control state or generated files.
- UI Run can use the preflight result to block executable execution before starting a session.

## Review Instructions

- Verify that sandbox detection is shared with or consistent with the Codex adapter.

## Notes

- The preflight should diagnose local execution readiness, not modify the environment.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-129 --to in_progress
python scripts/taskctl.py task transition TASK-129 --to in_review
python scripts/taskctl.py task approve TASK-129 --notes "..."
python scripts/taskctl.py task transition TASK-129 --to done
python scripts/aictl.py task report submit --task TASK-129 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `817`

Task: `PIPEF-20 (TASK-099)` — **PIPE-020 Validate report freshness after execute**
Epic: `EPIC-009`
Status: `in_progress`
Verification: `strict`
Ref: `PIPEF-20`
UID: `tsk_9d547d384917`
Legacy ID: `TASK-099`
Aliases: `TASK-099`
Epic Key / Local Seq: `PIPEF` / `20`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Ensure collect-report can distinguish a report created for the current execution from an older report.

## Description

Prevent old task reports from accidentally satisfying a new execute phase.

## Scope

- Record execute start and finish evidence usable by collect-report.
- Compare the collected report timestamp or report id against execute evidence.
- Block stale reports by default with REPORT_STALE.
- Support an explicit allow-existing-report option for supervised recovery.

## Out of Scope

- Do not change behavior unrelated to this task.
- Do not refactor unrelated code.
- Do not edit protected project-control files manually.

## Allowed Files

- ai_project_ctl/pipeline/report_phase.py
- ai_project_ctl/pipeline/execute_phase.py
- scripts/aictl.py

## Acceptance Criteria

- A report submitted after the current execute phase passes freshness checks.
- An older report blocks collect-report unless allow-existing-report is explicitly used.
- The result explains whether freshness was based on timestamp, report id, or recovery override.
- The override is visible in phase artifacts for review.

## Review Instructions

- Check that freshness logic is deterministic and does not rely on local timezone formatting.
- Verify the recovery override cannot silently hide task identity mismatch.

## Notes

- Draft ref: PIPE-020.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-099 --to in_progress
python scripts/taskctl.py task transition TASK-099 --to in_review
python scripts/taskctl.py task approve TASK-099 --notes "..."
python scripts/taskctl.py task transition TASK-099 --to done
python scripts/aictl.py task report submit --task TASK-099 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

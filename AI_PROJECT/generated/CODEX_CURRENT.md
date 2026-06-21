<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `912`

Task: `PIPEF-39 (TASK-118)` — **PIPE-039 Add CI exit-code mode for pipeline**
Epic: `EPIC-009`
Status: `in_progress`
Verification: `strict`
Ref: `PIPEF-39`
UID: `tsk_69240c03bede`
Legacy ID: `TASK-118`
Aliases: `TASK-118`
Epic Key / Local Seq: `PIPEF` / `39`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Add a CI-oriented exit-code mode where blocked and failed pipeline outcomes produce nonzero process exit codes.

## Description

Make pipeline results usable by automation without losing human-readable safe-stop behavior.

## Scope

- Add --ci flag to phase runner commands where appropriate.
- Map passed and completed outcomes to exit code 0.
- Map failed outcomes to exit code 1.
- Map blocked outcomes to exit code 2.

## Out of Scope

- Do not change behavior unrelated to this task.
- Do not refactor unrelated code.
- Do not edit protected project-control files manually.

## Allowed Files

- scripts/aictl.py
- ai_project_ctl/pipeline/phase.py

## Acceptance Criteria

- pipeline run-next --ci exits 0 for passed or completed outcomes.
- pipeline run-next --ci exits 2 for blocked outcomes.
- pipeline run-next --ci exits 1 for failed outcomes.
- Default non-CI behavior remains compatible with human safe-stop usage.

## Review Instructions

- Check that JSON output still includes full outcome details in CI mode.
- Verify exit code mapping is documented in code comments or command help.

## Notes

- Draft ref: PIPE-039.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-118 --to in_progress
python scripts/taskctl.py task transition TASK-118 --to in_review
python scripts/taskctl.py task approve TASK-118 --notes "..."
python scripts/taskctl.py task transition TASK-118 --to done
python scripts/aictl.py task report submit --task TASK-118 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

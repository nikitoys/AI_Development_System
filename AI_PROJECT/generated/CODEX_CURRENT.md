<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `1733`

Task: `PIPEF-149 (TASK-254)` — **Verify Web Run clean commit path**
Epic: `EPIC-009`
Status: `in_progress`
Verification: `light`
Ref: `PIPEF-149`
UID: `tsk_ccbe7708be33`
Legacy ID: `TASK-254`
Aliases: `TASK-254`
Epic Key / Local Seq: `PIPEF` / `149`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Create a deterministic smoke artifact to verify that Web Run reaches local commit from a clean worktree.

## Description

This task validates the fixed Web Run local commit path after the bootstrap repair commit.

## Scope

- Create tmp/run-smoke/web-run-clean-commit-smoke.md.
- Add the exact marker WEB_RUN_CLEAN_COMMIT_OK.
- State that this file is only a smoke artifact for Web Run local commit validation.
- Keep the content deterministic and timestamp-free.

## Out of Scope

- Do not change behavior unrelated to this task.
- Do not refactor unrelated code.
- Do not edit protected project-control files manually.
- Do not change pipeline, Web UI, policy, task, evolution, context, or Codex control behavior.

## Allowed Files

- tmp/run-smoke/web-run-clean-commit-smoke.md

## Acceptance Criteria

- tmp/run-smoke/web-run-clean-commit-smoke.md exists after execution.
- The file contains the exact marker WEB_RUN_CLEAN_COMMIT_OK.
- The file states that it is only a smoke artifact for Web Run local commit validation.
- The generated report evidence includes tmp/run-smoke/web-run-clean-commit-smoke.md as a changed file.
- Web Run reaches local commit without COMMIT_READINESS_FAILED.

## Review Instructions

- Confirm that Web Run creates a local commit from a clean worktree.

## Notes

- Run this only after the Web Run commit-readiness bootstrap fix has been manually committed.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-254 --to in_progress
python scripts/taskctl.py task transition TASK-254 --to in_review
python scripts/taskctl.py task approve TASK-254 --notes "..."
python scripts/taskctl.py task transition TASK-254 --to done
python scripts/aictl.py task report submit --task TASK-254 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

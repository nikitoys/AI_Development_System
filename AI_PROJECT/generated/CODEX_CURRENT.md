<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `1836`

Task: `PIPEF-168 (TASK-273)` — **Add no-checkpoint Web Run regression**
Epic: `EPIC-009`
Status: `in_progress`
Verification: `strict`
Ref: `PIPEF-168`
UID: `tsk_efef4d0e0938`
Legacy ID: `TASK-273`
Aliases: `TASK-273`
Epic Key / Local Seq: `PIPEF` / `168`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Add an end-to-end regression proving that a successful Web Run leaves a clean worktree and the next Web Run does not request a checkpoint commit.

## Description

The owner workflow should be able to run one task, receive a task commit, and start the next task without checkpointing pipeline bookkeeping files.

## Scope

- Create or extend a Web Run local-commit regression test with two sequential planned smoke tasks.
- Assert the first Web Run creates a local commit and leaves git status clean.
- Assert the second Web Run is not blocked by dirty pipeline bookkeeping from the first run.
- Assert no checkpoint prompt is shown when the user made no changes between runs.

## Out of Scope

- Do not implement multi-task batch UI in this task.
- Do not change checkpoint commit action behavior.
- Do not use network or real external Codex execution in tests.
- Do not edit protected project-control files manually.

## Allowed Files

- tests/test_web_run_local_commit_e2e.py
- tests/test_web_control_center.py
- tests/test_pipeline_runner.py

## Acceptance Criteria

- The regression test creates a successful first Web Run with a local commit hash.
- The regression test verifies git status is clean immediately after the first successful Web Run.
- The regression test attempts a second Web Run without manual checkpointing.
- The second Web Run does not return WORKTREE_DIRTY for pipeline bookkeeping files.
- The test fails if pipeline-events.jsonl, pipeline_sessions.json, PIPELINE_STATUS.md, or PIPELINE_AUDIT.md remain dirty after the first run.
- The test uses existing fake or stubbed execution paths and does not require real Codex network execution.

## Review Instructions

- Verify that the regression matches the owner workflow: run task, then run the next task without checkpoint commit.

## Notes

- This test should prove the fix that prevents checkpoint prompts after every successful task.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-273 --to in_progress
python scripts/taskctl.py task transition TASK-273 --to in_review
python scripts/taskctl.py task approve TASK-273 --notes "..."
python scripts/taskctl.py task transition TASK-273 --to done
python scripts/aictl.py task report submit --task TASK-273 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

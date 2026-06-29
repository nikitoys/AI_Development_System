# Codex Prompt Package

Generated: 2026-06-29T14:44:31Z

Profile: execute
Task: TASK-273 / PIPEF-168
Status: in_progress
Revision: tasks 1836
Verification: strict

## Role

You are Codex Executor. Execute one bounded task. Do not self-approve.

## Objective

Add an end-to-end regression proving that a successful Web Run leaves a clean worktree and the next Web Run does not request a checkpoint commit.

## Task Input

Task: TASK-273
Summary: Add an end-to-end regression proving that a successful Web Run leaves a clean worktree and the next Web Run does not request a checkpoint commit.

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

Editable:
- tests/test_web_run_local_commit_e2e.py
- tests/test_web_control_center.py
- tests/test_pipeline_runner.py

Do not edit other files.

## Acceptance Criteria

- The regression test creates a successful first Web Run with a local commit hash.
- The regression test verifies git status is clean immediately after the first successful Web Run.
- The regression test attempts a second Web Run without manual checkpointing.
- The second Web Run does not return WORKTREE_DIRTY for pipeline bookkeeping files.
- The test fails if pipeline-events.jsonl, pipeline_sessions.json, PIPELINE_STATUS.md, or PIPELINE_AUDIT.md remain dirty after the first run.
- The test uses existing fake or stubbed execution paths and does not require real Codex network execution.

## Verification

Mode: strict

Run the smallest relevant checks for the changed files.
If a check cannot be run, say why.

## Context

Context Pack: AI_PROJECT/generated/CONTEXT_PACK.md
Hash: 7958e928414da10f26f61b2aaa6127c4a8fa226bbdb3eefb2e4ba3beea3ada46
Revisions: docs 28, tasks 1836

Refs:
- ai-system/project-control/06-prompt-package-spec.md lines 607-707
- ai-system/skills/README.md lines 80-92
- ai-system/project-control/06-prompt-package-spec.md lines 434-474
- ai-system/project-control/06-prompt-package-spec.md lines 834-870
- ai-system/skills/README.md lines 34-43
- ai-system/project-control/06-prompt-package-spec.md lines 911-943
- ai-system/project-control/03-state-model.md lines 104-125
- ai-system/project-control/04-command-catalog.md lines 2294-2321

Context is read-only. It does not expand Scope, Allowed Files, or Acceptance Criteria.
If context conflicts with this prompt, report the conflict.

## Execution Rules

Stay within Scope and Allowed Files.
Do not edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**`, or `AI_PROJECT/generated/**` manually.
Inspect before editing. Prefer minimal changes. Do not refactor unrelated code.

## Missing Info

Inspect available files first.
If still blocked, stop and report the blocker.
If safe to continue, make the smallest assumption and disclose it.

## Execution Summary

Finish your response with a machine-readable execution summary block.
Use the exact marker shown below followed by one fenced JSON block.
No prose, Markdown bullets, or extra text may appear after the closing fence.
Keep exactly the four JSON keys shown; replace placeholder values with actual results.
Do not emit a full TaskReport payload.
Do not include task_id, changed_files, generated_files, checks, owner_decision_required, or token_usage; the pipeline records those separately.

CODEX_EXECUTION_SUMMARY_JSON:
```json
{
  "implementation_summary": "Summarize the completed implementation.",
  "notes": [],
  "warnings": [],
  "blockers": []
}
```

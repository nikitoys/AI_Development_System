# Codex Prompt Package

Generated: 2026-06-29T13:36:17Z

Profile: execute
Task: TASK-266 / PIPEF-161
Status: in_progress
Revision: tasks 1812
Verification: strict

## Role

You are Codex Executor. Execute one bounded task. Do not self-approve.

## Objective

Apply dirty worktree preflight to Web batch runs before any multi-task pipeline session is created or executed.

## Task Input

Task: TASK-266
Summary: Apply dirty worktree preflight to Web batch runs before any multi-task pipeline session is created or executed.

## Scope

- Run dirty worktree preflight before ui.run_task_batch creates a normal pipeline session.
- Return a not_run batch result when dirty files exist before batch start.
- Include dirty file paths and checkpoint commit guidance in the batch action result.
- Ensure dirty batch preflight does not run Codex, create a session, or transition tasks.

## Out of Scope

- Do not change dirty handoff behavior after a task commit in this task.
- Do not automatically create a checkpoint commit.
- Do not change selected-task dirty preflight behavior.
- Do not edit protected project-control files manually.

## Allowed Files

Editable:
- ai_project_ctl/web/actions.py
- ai_project_ctl/pipeline/git_status.py
- tests/test_web_control_center.py
- tests/test_ui_run_command.py

Do not edit other files.

## Acceptance Criteria

- A clean worktree allows ui.run_task_batch to create and run a batch session.
- A dirty worktree returns not_run before session creation and before Codex execution.
- The not_run result includes dirty file paths from git status.
- The not_run result includes owner guidance to create a checkpoint commit or clean the worktree.
- The existing ui.checkpoint_commit action remains usable after the dirty batch result.
- Tests cover clean and dirty batch-start preflight behavior.

## Verification

Mode: strict

Run the smallest relevant checks for the changed files.
If a check cannot be run, say why.

## Context

Context Pack: AI_PROJECT/generated/CONTEXT_PACK.md
Hash: 1c17670c9533ca17aa0ff684cd3479d85248845c1a5d984dfe5acedc82e9499f
Revisions: docs 28, tasks 1812

Refs:
- ai-system/project-control/06-prompt-package-spec.md lines 607-707
- ai-system/skills/README.md lines 80-92
- ai-system/skills/README.md lines 34-43
- ai-system/project-control/06-prompt-package-spec.md lines 834-870
- ai-system/project-control/06-prompt-package-spec.md lines 911-943
- ai-system/project-control/06-prompt-package-spec.md lines 434-474
- ai-system/project-control/03-state-model.md lines 104-125
- ai-system/project-control/04-command-catalog.md lines 21-64

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

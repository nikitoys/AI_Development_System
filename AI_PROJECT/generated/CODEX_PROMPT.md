# Codex Prompt Package

Generated: 2026-06-28T18:53:14Z

Profile: execute
Task: TASK-254 / PIPEF-149
Status: in_progress
Revision: tasks 1733
Verification: light

## Role

You are Codex Executor. Execute one bounded task. Do not self-approve.

## Objective

Create a deterministic smoke artifact to verify that Web Run reaches local commit from a clean worktree.

## Task Input

Task: TASK-254
Summary: Create a deterministic smoke artifact to verify that Web Run reaches local commit from a clean worktree.

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

Editable:
- tmp/run-smoke/web-run-clean-commit-smoke.md

Do not edit other files.

## Acceptance Criteria

- tmp/run-smoke/web-run-clean-commit-smoke.md exists after execution.
- The file contains the exact marker WEB_RUN_CLEAN_COMMIT_OK.
- The file states that it is only a smoke artifact for Web Run local commit validation.
- The generated report evidence includes tmp/run-smoke/web-run-clean-commit-smoke.md as a changed file.
- Web Run reaches local commit without COMMIT_READINESS_FAILED.

## Verification

Mode: light

Run the smallest relevant checks for the changed files.
If a check cannot be run, say why.

## Context

Context Pack: AI_PROJECT/generated/CONTEXT_PACK.md
Hash: 0b6c3f6db5ddd6501bd152cafe2cf22441b099c8f11ab964ca7fdb49087b7b23
Revisions: docs 28, tasks 1733

Refs:
- ai-system/project-control/06-prompt-package-spec.md lines 607-707
- ai-system/project-control/03-state-model.md lines 104-125
- ai-system/skills/README.md lines 80-92
- ai-system/project-control/06-prompt-package-spec.md lines 434-474
- ai-system/project-control/06-prompt-package-spec.md lines 834-870
- ai-system/skills/README.md lines 34-43
- ai-system/project-control/04-command-catalog.md lines 65-119
- ai-system/project-control/07-validation-and-tests.md lines 1368-1386

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

# Codex Prompt Package

Generated: 2026-06-30T18:28:20Z

Profile: execute
Task: TASK-277 / PIPEF-172
Status: in_progress
Revision: tasks 1880
Verification: strict

## Role

You are Codex Executor. Execute one bounded task. Do not self-approve.

## Objective

Update local commit readiness so current-session governed close side effects can be committed without allowing unrelated AI_PROJECT dirty files.

## Task Input

Task: TASK-277
Summary: Update local commit readiness so current-session governed close side effects can be committed without allowing unrelated AI_PROJECT dirty files.

## Scope

- Extend commit readiness approved-file collection to recognize governed side effects owned by the current pipeline session.
- Keep pre-existing dirty governed files and non-session-owned AI_PROJECT files blocked as unrelated.
- Preserve the existing requirement for non-governed target task artifact evidence before committing governed session side effects.
- Add a regression that covers a successful local commit with task artifact changes plus session-owned task/report/codex/context/evolution/pipeline side effects.
- Add or keep a negative regression proving unrelated governed dirty files still fail with COMMIT_UNRELATED_FILES.

## Out of Scope

- Do not allow blanket commits of all AI_PROJECT/** paths.
- Do not bypass commit readiness, report gate, machine review, or task done requirements.
- Do not edit protected project-control files manually.
- Do not change behavior unrelated to local commit readiness.

## Allowed Files

Editable:
- ai_project_ctl/pipeline/git_commit.py
- ai_project_ctl/pipeline/close_phase.py
- ai_project_ctl/pipeline/session.py
- tests/test_pipeline_runner.py
- tests/test_web_run_local_commit_e2e.py
- tests/test_web_control_center.py

Do not edit other files.

## Acceptance Criteria

- Commit readiness passes for a clean-baseline pipeline session that has target task artifact evidence and current-session governed close side effects.
- Local commit creation stages only approved target artifact files and current-session governed side-effect files.
- Pre-existing dirty governed files that are not owned by the current session still block with COMMIT_UNRELATED_FILES.
- Arbitrary AI_PROJECT/** files that are not approved by report, side effects, or current-session evidence still block with COMMIT_UNRELATED_FILES.
- Commit readiness still blocks governed-only changes when the selected task has no non-governed target artifact evidence.
- python -m pytest tests/test_pipeline_runner.py -q passes.
- python -m pytest tests/test_web_run_local_commit_e2e.py -q passes.

## Verification

Mode: strict

Run the smallest relevant checks for the changed files.
If a check cannot be run, say why.

## Context

Context Pack: AI_PROJECT/generated/CONTEXT_PACK.md
Hash: 1cc200bd903818285a9f3b3539378647fb87349e96e709bee8a707e4b6a77983
Revisions: docs 28, tasks 1880

Refs:
- ai-system/skills/README.md lines 80-92
- ai-system/skills/README.md lines 34-43
- ai-system/project-control/06-prompt-package-spec.md lines 607-707
- ai-system/project-control/06-prompt-package-spec.md lines 911-943
- ai-system/project-control/06-prompt-package-spec.md lines 834-870
- ai-system/project-control/04-command-catalog.md lines 65-119
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

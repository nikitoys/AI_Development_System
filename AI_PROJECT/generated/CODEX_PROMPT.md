# Codex Prompt Package

Generated: 2026-06-25T13:13:47Z

Profile: execute
Task: TASK-136 / PIPEF-57
Status: in_progress
Revision: tasks 1206
Verification: strict

## Role

You are Codex Executor. Execute one bounded task. Do not self-approve.

## Objective

Add a read-only JSON endpoint that returns compact live status for one pipeline session.

## Task Input

Task: TASK-136
Summary: Add a read-only JSON endpoint that returns compact live status for one pipeline session.

## Scope

- Add a read-only route for compact pipeline session status JSON.
- Return session id, status, current task, current phase, phase status, stop reason, next action and phase history summary.
- Return stable errors for missing or invalid session ids.
- Add focused tests for successful and missing-session responses.

## Out of Scope

- Do not mutate pipeline session state.
- Do not change pipeline execution behavior.
- Do not add frontend polling in this task.

## Allowed Files

Editable:
- ai_project_ctl/web/server.py
- ai_project_ctl/web/read_model.py
- tests/test_web_control_center.py

Do not edit other files.

## Acceptance Criteria

- The new endpoint returns JSON for an existing pipeline session.
- The JSON payload contains status, current_phase, current_phase_status, stop_reason, next_action and phase_history summary.
- The endpoint does not render full HTML.
- Missing sessions return a stable non-success response.
- Existing Web Control Center pages continue to render.

## Verification

Mode: strict

Run the smallest relevant checks for the changed files.
If a check cannot be run, say why.

## Context

Context Pack: AI_PROJECT/generated/CONTEXT_PACK.md
Hash: bf492841d0996824b651fab737468be3679df5827be0522d501251a5c2f2a922
Revisions: docs 28, tasks 1206

Refs:
- ai-system/project-control/06-prompt-package-spec.md lines 874-906
- ai-system/project-control/04-command-catalog.md lines 65-119
- ai-system/project-control/03-state-model.md lines 104-125
- ai-system/project-control/04-command-catalog.md lines 2294-2321
- ai-system/project-control/04-command-catalog.md lines 21-64
- ai-system/skills/README.md lines 80-92
- ai-system/project-control/06-prompt-package-spec.md lines 580-670
- ai-system/project-control/06-prompt-package-spec.md lines 797-833

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

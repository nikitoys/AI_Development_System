# Codex Prompt Package

Generated: 2026-06-24T18:22:34Z

Profile: execute
Task: TASK-155 / PIPEF-76
Status: in_progress
Revision: tasks 1087
Verification: strict

## Role

You are Codex Executor. Execute one bounded task. Do not self-approve.

## Objective

Add an end-to-end regression test proving a UI Run session can proceed past collect-report when Codex emits a valid report.

## Task Input

Task: TASK-155
Summary: Add an end-to-end regression test proving a UI Run session can proceed past collect-report when Codex emits a valid report.

## Scope

- Add a pipeline or UI run test with a fake Codex runner that emits the structured report block.
- Assert that execute records the auto-submitted report id.
- Assert that collect-report passes without manual task report submit.
- Assert that missing structured report output still blocks with the expected report-missing code.

## Out of Scope

- Do not run real Codex in tests.
- Do not change production pipeline behavior in this task.
- Do not weaken existing report gate tests.

## Allowed Files

Editable:
- tests/test_ui_run_command.py
- tests/test_pipeline_runner.py
- tests/test_pipeline_report_gate.py
- tests/pipeline/test_codex_adapter.py

Do not edit other files.

## Acceptance Criteria

- The regression test uses a fake local-command runner, not real Codex.
- A valid emitted report allows collect-report to pass.
- The test verifies the report id is stored and linked to the selected task.
- A no-report runner still produces CODEX_ADAPTER_REPORT_MISSING.
- Existing pipeline tests continue to pass.

## Verification

Mode: strict

Run the smallest relevant checks for the changed files.
If a check cannot be run, say why.

## Context

Context Pack: AI_PROJECT/generated/CONTEXT_PACK.md
Hash: 3bc3fb9327cce2baae2f9e2c06f5bcf76790aa01fb0cb692691337f4b6ba66d4
Revisions: docs 28, tasks 1087

Refs:
- ai-system/project-control/06-prompt-package-spec.md lines 874-906
- ai-system/skills/README.md lines 34-43
- ai-system/project-control/06-prompt-package-spec.md lines 797-833
- ai-system/skills/README.md lines 80-92
- ai-system/project-control/07-validation-and-tests.md lines 1368-1386
- ai-system/project-control/06-prompt-package-spec.md lines 580-670
- ai-system/project-control/06-prompt-package-spec.md lines 123-162
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

## Final Report

Finish your response with a machine-readable structured report block.
Use the exact marker shown below followed by one fenced JSON block.
No prose, Markdown bullets, or extra text may appear after the closing fence.
Keep the JSON keys exactly as shown; replace placeholder values with actual results.
Report paths relative to the repository root.
Each `checks` item, when present, must include `name` and `result`; optional fields are `command`, `duration_sec`, `blocking`, and `details`.
Include `token_usage` even when counts are estimated. If exact counts are unavailable, provide the best estimate and set `token_count_estimated` to `true`.

CODEX_REPORT_JSON:
```json
{
  "schema_version": 1,
  "task_id": "TASK-155",
  "task_ref": "PIPEF-76",
  "implementation_summary": "Summarize the completed implementation.",
  "changed_files": [],
  "generated_files": [],
  "checks": [],
  "warnings": [],
  "blockers": [],
  "notes": [],
  "owner_decision_required": false,
  "token_usage": {
    "prompt_tokens": 0,
    "context_tokens": 0,
    "completion_tokens": 0,
    "output_tokens": 0,
    "total_tokens": 0,
    "remaining_tokens": 0,
    "model_context_limit": 0,
    "max_context_tokens": 0,
    "reserved_output_tokens": 0,
    "min_remaining_tokens": 0,
    "token_count_strategy": "codex_reported",
    "token_count_estimated": false,
    "token_count_unavailable": false,
    "token_count_unavailable_reason": ""
  }
}
```

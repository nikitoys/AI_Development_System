<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `1087`

Task: `PIPEF-76 (TASK-155)` — **PIPE-071 Add pipeline regression test for Run report auto-collection**
Epic: `EPIC-009`
Status: `in_progress`
Verification: `strict`
Ref: `PIPEF-76`
UID: `tsk_d572bda0c446`
Legacy ID: `TASK-155`
Aliases: `TASK-155`
Epic Key / Local Seq: `PIPEF` / `76`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Add an end-to-end regression test proving a UI Run session can proceed past collect-report when Codex emits a valid report.

## Description

This protects the Run workflow from returning to CODEX_ADAPTER_REPORT_MISSING after successful Codex execution.

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

- tests/test_ui_run_command.py
- tests/test_pipeline_runner.py
- tests/test_pipeline_report_gate.py
- tests/pipeline/test_codex_adapter.py

## Acceptance Criteria

- The regression test uses a fake local-command runner, not real Codex.
- A valid emitted report allows collect-report to pass.
- The test verifies the report id is stored and linked to the selected task.
- A no-report runner still produces CODEX_ADAPTER_REPORT_MISSING.
- Existing pipeline tests continue to pass.

## Review Instructions

- Check that the regression covers the Run path rather than only the parser unit path.

## Notes

- This task may be done after the implementation tasks or adjusted to the final test layout.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-155 --to in_progress
python scripts/taskctl.py task transition TASK-155 --to in_review
python scripts/taskctl.py task approve TASK-155 --notes "..."
python scripts/taskctl.py task transition TASK-155 --to done
python scripts/aictl.py task report submit --task TASK-155 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

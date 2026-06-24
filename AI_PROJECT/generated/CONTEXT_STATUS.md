<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-155 PIPE-071 Add pipeline regression test for Run report auto-collection Add an end-to-end regression test proving a UI Run session can proceed past collect-report when Codex emits a valid report. This protects the Run workflow from returning to CODEX_ADAPTER_REPORT_MISSING after successful Codex execution. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add a pipeline or UI run test with a fake Codex runner that emits the structured report block. Assert that execute records the auto-submitted report id. Assert that collect-report passes without manual task report submit. Assert that missing structured report output still blocks with the expected report-missing code. Do not run real Codex in tests. Do not change production pipeline behavior in this task. Do not weaken existing report gate tests. tests/test_ui_run_command.py tests/test_pipeline_runner.py tests/test_pipeline_report_gate.py tests/pipeline/test_codex_adapter.py The regression test uses a fake local-command runner, not real Codex. A valid emitted report allows collect-report to pass. The test verifies the report id is stored and linked to the selected task. A no-report runner still produces CODEX_ADAPTER_REPORT_MISSING. Existing pipeline tests continue to pass. Check that the regression covers the Run path rather than only the parser unit path.","schema_version":1,"task_id":"TASK-155"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-155`
Limit: `8`
Docs revision: `28`
Tasks revision: `1087`
Indexed source documents: `10`
Indexed chunks: `891`
Selected chunks: `8`
Excluded registered sources: `135`

## Selected Source Paths

- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/project-control/07-validation-and-tests.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `94`
- template document excluded by default: `41`

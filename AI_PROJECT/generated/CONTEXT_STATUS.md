<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-192 Add close artifact regression coverage Add end-to-end regression tests for close artifact bounding, already-closed close retry, and stale-output pre-execute blocking. This task verifies the recent close and pre-execute safety fixes through focused pipeline tests without changing production behavior. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add a regression test that records close evidence with large nested workflow output and still validates pipeline state. Add a regression test for retrying close after the selected task is already done from a previous partial close attempt. Add a regression test that stale protected generated output blocks before Codex adapter execution. Keep fixtures small and deterministic so the focused tests run quickly. Do not change production pipeline behavior in this test-only task. Do not add slow integration tests. Do not edit protected project-control files manually. tests/test_pipeline_phase_review_close.py tests/test_pipeline_runner.py tests/test_pipeline_e2e.py tests/test_pipeline_artifact_bounds.py Tests fail against the old oversized close artifact behavior and pass after artifact bounding is implemented. Tests cover the already-done close retry path without requiring manual state edits. Tests cover pre-execute stale generated output blocking with Codex adapter not called. Focused test commands complete successfully without running unrelated long test suites. No production source files are modified by this task. Check that tests are deterministic and do not depend on live Codex or external services. Verify that test names describe the specific regression they protect.","schema_version":1,"task_id":"TASK-192"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-192`
Limit: `8`
Docs revision: `28`
Tasks revision: `1367`
Indexed source documents: `10`
Indexed chunks: `891`
Selected chunks: `8`
Excluded registered sources: `135`

## Selected Source Paths

- ai-system/project-control/03-state-model.md
- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `94`
- template document excluded by default: `41`

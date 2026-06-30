<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-282 Update pipeline runner expectations Bring tests/test_pipeline_runner.py in line with the current run-next phase-result model so stale expectations do not produce unrelated blocker noise. The full pipeline runner test file currently contains old stop_code and steps expectations that do not match current phase dispatch behavior. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Identify stale assertions in tests/test_pipeline_runner.py that expect the old run-next result shape. Update those assertions to the current phase_result, phase_status, and queue behavior. Preserve meaningful coverage for blockers, close, local commit, and batch stopping behavior. Run the focused pipeline runner test file. Do not change production pipeline behavior in this task. Do not delete coverage just to make tests pass. Do not edit protected project-control files manually. tests/test_pipeline_runner.py tests/test_pipeline_runner.py no longer fails because of stale run-next stop_code or step-shape expectations. Updated tests assert the current phase_result and phase_status behavior. Tests for real blockers and failures remain meaningful. python -m pytest tests/test_pipeline_runner.py -q passes. No production code files are edited. Review for accidental weakening of tests; updated assertions should match current behavior, not ignore it.","schema_version":1,"task_id":"TASK-282"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-282`
Limit: `8`
Docs revision: `28`
Tasks revision: `1924`
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

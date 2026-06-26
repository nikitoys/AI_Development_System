<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-183 Add verify-to-review advisory warning pipeline regression Add an end-to-end pipeline regression proving advisory report warnings pass verify and do not block review. Guard the complete run-next flow that previously passed verify but blocked review. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Create a pipeline session fixture with a report that contains warnings and no blockers. Use a policy that allows advisory report warnings and relaxed git diff verification. Drive the session through verify and review without invoking external Codex. Assert verify passes with advisory warning evidence. Assert review does not block with REPORT_GATE_NOT_PASSED_AFTER_VERIFY. Do not change runtime pipeline behavior in this task. Do not add external Codex execution to the test. Do not edit protected project-control files manually. tests/test_pipeline_runner.py tests/pipeline/test_review_phase.py The regression fails on the old strict review behavior. The regression passes after review uses the shared report warning policy. The test does not run external Codex. The test asserts both verify and review phase outcomes. Focused pipeline/review tests pass. Confirm the test models the real blocker REPORT_GATE_NOT_PASSED_AFTER_VERIFY. Confirm the test is bounded and deterministic.","schema_version":1,"task_id":"TASK-183"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-183`
Limit: `8`
Docs revision: `28`
Tasks revision: `1303`
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

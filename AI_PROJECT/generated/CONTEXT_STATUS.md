<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-280 Accept confirmed recovery report chain Allow close preflight to accept a verified owner-confirmed recovery report chain that intentionally replaces the original execute report for the same task. Close should still block accidental report drift, but should allow explicit recovery metadata produced by collect-report recovery override. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Update close report consistency logic to recognize explicit recovery report replacement metadata. Allow execute to reference the original report while collect_report, verify, and review reference the recovery report only when recovery metadata is valid. Keep accidental report-id drift blocked with REPORT_EVIDENCE_MISMATCH. Add focused close preflight tests for accepted recovery and rejected accidental mismatch. Do not add a report recovery command in this task. Do not relax task identity checks or review-policy checks. Do not edit protected project-control files manually. ai_project_ctl/pipeline/close_phase.py tests/test_pipeline_phase_review_close.py Close preflight passes when collect_report records owner-confirmed recovery metadata replacing the execute report for the same task. Close preflight still blocks when report ids differ without valid recovery metadata. Close preflight still blocks when recovery metadata references a different session or task. Close preflight still enforces review skipped-by-policy evidence when Codex Review is disabled. Focused close recovery tests pass. Verify that only explicit owner-confirmed recovery paths are accepted.","schema_version":1,"task_id":"TASK-280"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-280`
Limit: `8`
Docs revision: `28`
Tasks revision: `1912`
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

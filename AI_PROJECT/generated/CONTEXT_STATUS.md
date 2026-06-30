<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-279 Record recovery report binding When collect-report uses an owner-confirmed recovery override, record explicit metadata that the recovery report replaces the execute-phase report for the same session and task. Make recovery_override machine-readable so later phases can distinguish intentional owner recovery from accidental report drift. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Extend collect-report artifacts for allow_existing_report with a compact recovery object. Record recovery_report_id, replaced execute report id, session id, task id, owner confirmation flag, and recovery basis. Keep normal non-recovery collect-report behavior unchanged. Add focused tests for collect-report recovery metadata. Do not change close preflight acceptance rules in this task. Do not change report schema validation rules. Do not edit protected project-control files manually. ai_project_ctl/pipeline/report_phase.py tests/test_pipeline_report_phase.py collect-report without allow_existing_report keeps the current artifact shape and freshness behavior. collect-report with allow_existing_report records explicit recovery metadata when the latest report differs from execute report evidence. Recovery metadata identifies the old execute report id and the new recovery report id. Recovery metadata is tied to the current session id and task id. Focused collect-report tests pass. Check that recovery metadata is additive and cannot be confused with normal fresh execute reports.","schema_version":1,"task_id":"TASK-279"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-279`
Limit: `8`
Docs revision: `28`
Tasks revision: `1904`
Indexed source documents: `10`
Indexed chunks: `891`
Selected chunks: `8`
Excluded registered sources: `135`

## Selected Source Paths

- ai-system/project-control/06-prompt-package-spec.md
- ai-system/project-control/07-validation-and-tests.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `94`
- template document excluded by default: `41`

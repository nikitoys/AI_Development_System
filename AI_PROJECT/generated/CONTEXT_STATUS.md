<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-099 PIPE-020 Validate report freshness after execute Ensure collect-report can distinguish a report created for the current execution from an older report. Prevent old task reports from accidentally satisfying a new execute phase. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Record execute start and finish evidence usable by collect-report. Compare the collected report timestamp or report id against execute evidence. Block stale reports by default with REPORT_STALE. Support an explicit allow-existing-report option for supervised recovery. Do not change behavior unrelated to this task. Do not refactor unrelated code. Do not edit protected project-control files manually. ai_project_ctl/pipeline/report_phase.py ai_project_ctl/pipeline/execute_phase.py scripts/aictl.py A report submitted after the current execute phase passes freshness checks. An older report blocks collect-report unless allow-existing-report is explicitly used. The result explains whether freshness was based on timestamp, report id, or recovery override. The override is visible in phase artifacts for review. Check that freshness logic is deterministic and does not rely on local timezone formatting. Verify the recovery override cannot silently hide task identity mismatch.","schema_version":1,"task_id":"TASK-099"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-099`
Limit: `8`
Docs revision: `28`
Tasks revision: `817`
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

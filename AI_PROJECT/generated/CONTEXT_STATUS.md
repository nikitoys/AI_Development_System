<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-281 Add governed report recovery command Provide a governed CLI recovery command that creates a valid owner-confirmed recovery report without requiring manual JSON editing. The command should support report-gate blocker recovery for the current session and produce report fields that pass schema and token-usage validation. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Extend report recovery support beyond REPORT_MISSING to owner-confirmed report-gate blocker triage. Generate required token_usage fields automatically using an explicit estimated strategy. Allow owner-provided recovery reason and nonblocking warning text without silently hiding task-scope blockers. Expose the recovery command through scripts/aictl.py with clear next actions. Do not automatically mark failed in-scope checks as warnings without explicit owner recovery input. Do not change report gate validation rules. Do not edit protected project-control files manually. ai_project_ctl/pipeline/report_recovery.py scripts/aictl.py tests/test_pipeline_report_recovery.py A blocked report-gate session can produce an owner-confirmed recovery report through CLI without hand-written JSON. The generated recovery report includes required token_usage fields and passes report schema validation. The command records enough evidence for collect-report to identify the recovery report. The command refuses recovery when the selected session or task identity is ambiguous. Focused report recovery tests pass. Confirm that the command requires explicit owner intent and does not mask real task blockers.","schema_version":1,"task_id":"TASK-281"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-281`
Limit: `8`
Docs revision: `28`
Tasks revision: `1918`
Indexed source documents: `10`
Indexed chunks: `891`
Selected chunks: `8`
Excluded registered sources: `135`

## Selected Source Paths

- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `94`
- template document excluded by default: `41`

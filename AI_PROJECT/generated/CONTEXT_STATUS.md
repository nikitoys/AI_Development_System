<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-267 Auto-size Web batch max steps Calculate a safe effective max_steps for Web batch runs so normal multi-task execution does not stop immediately after a successful close. The current one-task max_steps setting is too small for multiple task phases and can cause misleading MAX_STEPS_REACHED results. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Compute an effective batch max_steps for ui.run_task_batch from max_tasks and the pipeline phase count. Apply a small reserve so a successful final close can complete the session cleanly. Preserve explicit lower policy settings for non-Web and selected-task runs unless batch action overrides them intentionally. Expose the effective max_steps used in the batch action result or session policy snapshot. Do not change phase order in this task. Do not change Codex execution timeout behavior. Do not change selected-task Run max_steps handling unless required by shared helper safety. Do not edit protected project-control files manually. ai_project_ctl/web/actions.py ai_project_ctl/pipeline/policy.py ai_project_ctl/pipeline/batch.py tests/test_web_control_center.py tests/test_pipeline_runner.py A Web batch run with max_tasks 2 receives enough max_steps to pass two full task phase cycles in tests. A Web batch run with max_tasks 3 receives a larger effective max_steps than a one-task run. The effective max_steps calculation uses the current RUN_NEXT_PHASE_SEQUENCE length. The action result or policy snapshot makes the effective max_steps visible for diagnostics. Existing selected-task and direct pipeline behavior are not unintentionally loosened. Tests cover effective max_steps calculation and avoid false MAX_STEPS_REACHED after successful close. Verify that this task solves the batch sizing issue without hiding real infinite-loop or failure limits.","schema_version":1,"task_id":"TASK-267"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-267`
Limit: `8`
Docs revision: `28`
Tasks revision: `1938`
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

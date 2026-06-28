<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-257 Demote recovered close workflow warnings Hide recovered close-time context/protected check warnings from owner-facing output when post-close context refresh succeeds. During close, contextctl.check-generated and protected.check can temporarily warn because task state changes make generated files stale before post-close refresh repairs them. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Identify non-blocking close workflow warnings from generated context and protected-file checks that are later repaired by post-close context_refresh. Keep recovered warning evidence in technical artifacts or debug details. Remove or demote recovered warnings from owner-facing Action Result and pipeline summary warnings. Ensure unrelated non-blocking warnings still remain visible to the owner. Add regression tests for recovered warnings and unrecovered warnings. Do not remove warning collection entirely. Do not suppress warnings when post-close context_refresh fails or is missing. Do not change task close state transitions. Do not edit protected project-control files manually. ai_project_ctl/pipeline/close_phase.py ai_project_ctl/pipeline/runner.py ai_project_ctl/web/server.py ai_project_ctl/web/read_model.py tests/test_pipeline_phase_review_close.py tests/test_pipeline_runner.py tests/test_web_control_center.py Recovered contextctl.check-generated warnings are not shown as owner-facing warnings when post-close context_refresh succeeds. Recovered protected.check stale context or prompt warnings are not shown as owner-facing warnings when post-close context_refresh succeeds. Technical evidence still records that the non-blocking checks warned during close. Warnings remain owner-facing when post-close context_refresh fails, is missing, or does not repair the stale generated files. Focused close-phase, runner, and Web Control Center tests pass. Check that warning demotion is conditional on successful post-close repair evidence. Confirm that no real blocking warning is hidden.","schema_version":1,"task_id":"TASK-257"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-257`
Limit: `8`
Docs revision: `28`
Tasks revision: `1754`
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

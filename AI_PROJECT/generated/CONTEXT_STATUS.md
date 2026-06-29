<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-262 Continue batch after task commit Allow the existing batch runner to continue to the next queued task after one task closes with a local commit. The batch runner should not complete the whole session after the first committed close when the selected queue still has executable tasks. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Update committed-close handling in the batch runner so it records the completed current task without always completing the whole session. Continue running the existing selected queue when max_tasks allows more tasks and executable queued tasks remain. Complete the session only when the selected queue is exhausted or the selected max_tasks limit is reached. Preserve current single-task behavior where a one-task selected queue still completes after committed close. Do not create a new pipeline engine. Do not change Web UI forms in this task. Do not change dirty worktree preflight behavior in this task. Do not edit protected project-control files manually. ai_project_ctl/pipeline/batch.py ai_project_ctl/pipeline/session.py tests/test_pipeline_runner.py tests/test_pipeline_phase_review_close.py A single-task session still completes after close creates a local commit. A multi-task session does not complete after the first task commit when another queued task remains executable. The batch summary records the first task in completed_tasks and changed_tasks after committed close. The batch runner continues through run_next for the next queued task after the first committed close. Existing blocker and failure behavior remains unchanged. Focused tests cover both single-task and multi-task committed-close behavior. Verify that the change reuses the existing run_next pipeline instead of adding a parallel execution path.","schema_version":1,"task_id":"TASK-262"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-262`
Limit: `8`
Docs revision: `28`
Tasks revision: `1795`
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

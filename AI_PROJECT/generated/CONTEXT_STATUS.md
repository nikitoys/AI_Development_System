<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-263 Enforce clean batch handoff Stop a multi-task batch before the next task when the previous task did not leave a clean worktree after its local commit. Each task in a batch must hand off to the next task from a clean repository state. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Capture git status after each committed task close before starting another queued task. Continue to the next task only when the post-task worktree is clean. Stop the batch with POST_TASK_DIRTY_WORKTREE when dirty files remain after a committed close. Include dirty file paths and the completed task id in the stop result. Do not add Web UI batch controls in this task. Do not ask the owner to manually commit between tasks. Do not change local commit staging rules in this task. Do not edit protected project-control files manually. ai_project_ctl/pipeline/batch.py ai_project_ctl/pipeline/git_status.py tests/test_pipeline_runner.py tests/pipeline/test_git_status_snapshot.py After a committed task close with a clean worktree, the batch may continue to the next queued task. After a committed task close with remaining dirty files, the batch stops before executing the next task. The stop result uses a stable POST_TASK_DIRTY_WORKTREE code. The stop result includes dirty file paths for owner diagnostics. The stop result does not mark the remaining queued task as executed or changed. Tests cover clean handoff and dirty handoff cases. Verify that a dirty handoff is treated as a pipeline safety stop, not as a request for a manual commit between tasks.","schema_version":1,"task_id":"TASK-263"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-263`
Limit: `8`
Docs revision: `28`
Tasks revision: `1800`
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

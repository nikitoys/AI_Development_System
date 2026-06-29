<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-272 Verify clean worktree after Web Run Add a post-success clean-worktree invariant so successful Web Run results fail loudly if tracked files remain dirty after local commit. The pipeline should expose a stable diagnostic when a successful task commit still leaves dirty tracked files. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Capture git status after a successful local task commit and final session completion. Return a stable POST_COMMIT_DIRTY_WORKTREE diagnostic if dirty files remain after a supposedly successful Web Run. Include dirty file paths in the diagnostic for owner and test visibility. Keep genuinely successful clean runs classified as completed. Do not auto-create a checkpoint commit in this task. Do not disable dirty worktree preflight. Do not change Codex execution or report parsing. Do not edit protected project-control files manually. ai_project_ctl/pipeline/batch.py ai_project_ctl/pipeline/git_status.py ai_project_ctl/web/actions.py tests/test_pipeline_runner.py tests/test_web_control_center.py A successful Web Run with clean post-commit git status remains completed. A successful close that leaves dirty tracked files returns POST_COMMIT_DIRTY_WORKTREE instead of silently appearing clean. The diagnostic includes dirty paths such as pipeline_sessions.json or PIPELINE_STATUS.md when present. The next task is not started when the post-commit clean invariant fails. Dirty preflight behavior before a run remains unchanged. Tests cover clean and dirty post-commit outcomes. Verify that this invariant protects future multi-task runs from starting the next task on hidden dirty state.","schema_version":1,"task_id":"TASK-272"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-272`
Limit: `8`
Docs revision: `28`
Tasks revision: `1834`
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

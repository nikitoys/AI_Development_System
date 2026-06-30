<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-259 Add confirmed checkpoint commit action Add an owner-confirmed Web UI action that creates a checkpoint commit before Web Run starts. The owner should be able to explicitly commit current dirty state from the Web UI after reviewing the files that will be committed. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Register a checkpoint commit action that requires explicit owner confirmation. Show the dirty file list that will be included before the commit is created. Run git add -A and git commit with an owner-facing checkpoint message after confirmation. Return the created commit hash and next action to run the selected task again. Do not automatically commit without owner confirmation. Do not start Web Run automatically after checkpoint commit. Do not change commit readiness rules for pipeline close. Do not edit protected project-control files manually. ai_project_ctl/web/actions.py ai_project_ctl/web/server.py ai_project_ctl/pipeline/git_status.py ai_project_ctl/pipeline/git_commit.py tests/test_web_control_center.py tests/test_ui_run_command.py tests/test_pipeline_git_commit.py The checkpoint commit action is rejected when owner confirmation is missing. The checkpoint commit action reports not_run when the worktree is already clean. With confirmation and a dirty worktree, the action stages all current changes and creates a git commit. The action result includes the checkpoint commit hash and a next action to run the selected task again. The action does not execute Codex or transition any selected task. Tests cover missing confirmation, clean worktree, dirty worktree, and successful commit hash reporting. Verify that checkpoint commit is explicit, confirmed, and independent from Web Run execution.","schema_version":1,"task_id":"TASK-259"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-259`
Limit: `8`
Docs revision: `28`
Tasks revision: `1771`
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

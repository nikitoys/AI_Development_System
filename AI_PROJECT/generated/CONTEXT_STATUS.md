<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-266 Block dirty Web batch starts Apply dirty worktree preflight to Web batch runs before any multi-task pipeline session is created or executed. A batch run must not start from a dirty worktree caused by task import or other owner-side changes. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Run dirty worktree preflight before ui.run_task_batch creates a normal pipeline session. Return a not_run batch result when dirty files exist before batch start. Include dirty file paths and checkpoint commit guidance in the batch action result. Ensure dirty batch preflight does not run Codex, create a session, or transition tasks. Do not change dirty handoff behavior after a task commit in this task. Do not automatically create a checkpoint commit. Do not change selected-task dirty preflight behavior. Do not edit protected project-control files manually. ai_project_ctl/web/actions.py ai_project_ctl/pipeline/git_status.py tests/test_web_control_center.py tests/test_ui_run_command.py A clean worktree allows ui.run_task_batch to create and run a batch session. A dirty worktree returns not_run before session creation and before Codex execution. The not_run result includes dirty file paths from git status. The not_run result includes owner guidance to create a checkpoint commit or clean the worktree. The existing ui.checkpoint_commit action remains usable after the dirty batch result. Tests cover clean and dirty batch-start preflight behavior. Verify that dirty preflight is only a start guard and does not interfere with pipeline-owned changes during execution.","schema_version":1,"task_id":"TASK-266"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-266`
Limit: `8`
Docs revision: `28`
Tasks revision: `1812`
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

<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-258 Add dirty worktree preflight for Web Run Prevent Web Run from starting when the repository has uncommitted changes before the selected task is executed. The Web UI should stop before Codex or pipeline execution when a dirty worktree would make local commit readiness unsafe. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Check git status before ui.run_selected_task creates or starts a normal pipeline session. Return a not_run result with a clear owner-facing worktree_dirty reason when uncommitted changes exist. Include the dirty file list and suggested manual checkpoint commit commands in the action result. Ensure dirty preflight does not run Codex, transition the selected task, create an Evolution Change, or mutate task execution state. Do not implement checkpoint commit creation in this task. Do not change local commit readiness rules for already running sessions. Do not refactor unrelated Web UI or pipeline code. Do not edit protected project-control files manually. ai_project_ctl/web/actions.py ai_project_ctl/web/server.py ai_project_ctl/pipeline/git_status.py tests/test_web_control_center.py tests/test_ui_run_command.py A clean worktree still allows ui.run_selected_task to start the selected planned or ready task normally. A dirty worktree returns not_run before Codex execution, before task transition, and before Evolution Change creation. The action result clearly states that Web Run did not start because the worktree is dirty. The action result includes dirty file paths from git status --short --untracked-files=all. The action result includes manual checkpoint commit commands for the owner. Tests cover clean and dirty worktree branches for ui.run_selected_task. Verify that the dirty worktree path is a preflight stop and not a partial pipeline run.","schema_version":1,"task_id":"TASK-258"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-258`
Limit: `8`
Docs revision: `28`
Tasks revision: `1766`
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

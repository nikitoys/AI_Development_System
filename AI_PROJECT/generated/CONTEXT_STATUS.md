<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-260 Link dirty preflight to checkpoint UX Connect the dirty worktree preflight result to the confirmed checkpoint commit action in the Web UI. The dirty preflight page should give the owner a direct, safe path to checkpoint current state and then run the task again. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add a visible checkpoint commit action from the dirty Web Run result when dirty files are present. Preserve the selected task reference in the dirty preflight response so the owner can return to the same task after checkpointing. Show owner-facing guidance that Web Run must start from a clean worktree. After checkpoint commit succeeds, show a clear next action to run the same selected task again. Do not create commits without owner confirmation. Do not automatically rerun the selected task after checkpoint commit. Do not change pipeline close or local commit readiness behavior. Do not edit protected project-control files manually. ai_project_ctl/web/actions.py ai_project_ctl/web/server.py tests/test_web_control_center.py tests/test_ui_run_command.py Dirty Web Run results show a checkpoint commit option when dirty files exist. The selected task remains visible in the dirty preflight result and next-action text. After checkpoint commit success, the result page points the owner back to running the same task. No automatic Web Run is started after checkpoint commit. Tests verify the dirty preflight to checkpoint commit UX path. Verify the owner can understand the sequence: checkpoint first, then run the same task again.","schema_version":1,"task_id":"TASK-260"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-260`
Limit: `8`
Docs revision: `28`
Tasks revision: `1776`
Indexed source documents: `10`
Indexed chunks: `891`
Selected chunks: `8`
Excluded registered sources: `135`

## Selected Source Paths

- ai-system/project-control/03-state-model.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `94`
- template document excluded by default: `41`

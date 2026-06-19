<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-050 UIX-13 Add Epic Close UI Action Expose the epic.close_if_complete workflow in the Web Control Center with clear incomplete-task blocking reasons. Allow the owner to close an epic from the UI when all required child tasks are complete, while showing clear reasons when the epic cannot be closed. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add Close Epic If Complete action to Epic or Dashboard views. Route close action through existing epic.close_if_complete workflow. Require explicit confirmation before closing an epic. Show incomplete tasks when close is blocked. Show linked open Changes if they prevent closure or should be reviewed. Show task completion counts by status. Use unified result panel for success/failure output. Add tests for closable epic, incomplete epic, invalid epic, and no direct state writes. Do not auto-close epics. Do not close epics with incomplete tasks. Do not auto-accept linked Changes. Do not change epic lifecycle rules. Do not directly edit plan.json or task state. ai_project_ctl/web/read_model.py ai_project_ctl/web/server.py ai_project_ctl/web/actions.py ai_project_ctl/core/workflows.py if epic workflow metadata needs compatible updates ai_project_ctl/core/registry.py if command metadata needs compatible updates tests/test_web_control_center.py tests/test_workflows.py tests/test_registry.py UI shows epic completion status and open task counts. Close Epic If Complete is available only when valid or explains why it is blocked. Close action requires explicit confirmation. Close action routes through epic.close_if_complete workflow. Blocked close shows incomplete task refs. No direct plan/task state writes are introduced. Tests and project-control validations pass. Verify that incomplete epics cannot be closed. Verify that blocking tasks are shown clearly. Verify that closing an epic does not auto-close tasks or Changes.","schema_version":1,"task_id":"TASK-050"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-050`
Limit: `8`
Docs revision: `23`
Tasks revision: `456`
Indexed source documents: `10`
Indexed chunks: `890`
Selected chunks: `8`
Excluded registered sources: `134`

## Selected Source Paths

- ai-system/project-control/03-state-model.md
- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `93`
- template document excluded by default: `41`

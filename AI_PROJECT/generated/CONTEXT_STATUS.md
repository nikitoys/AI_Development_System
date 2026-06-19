<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-039 UIX-02 Add task row workflow buttons Add status-aware workflow buttons next to tasks, including Prepare for Codex, Refresh Context, and Submit for Review. Make routine task operation possible from the Tasks page by exposing existing workflow automation actions as row-level buttons. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add status-aware task row buttons. Expose Prepare for Codex for planned/ready tasks. Expose Refresh Context for current/in-progress tasks. Expose Submit for Review for in-progress tasks. Show confirmation preview before workflow execution. Route all actions through existing workflow runner and aictl command paths. Show result summary after execution. Show next Codex instruction after Prepare for Codex. Do not auto-run Codex. Do not auto-approve tasks. Do not auto-close tasks. Do not accept Evolution Changes. Do not add arbitrary shell command execution. Do not directly edit protected project-control files. ai_project_ctl/web/actions.py ai_project_ctl/web/server.py ai_project_ctl/web/read_model.py ai_project_ctl/core/workflows.py if workflow metadata needs compatible updates ai_project_ctl/core/registry.py if workflow metadata needs compatible updates scripts/aictl.py if workflow routing needs compatible updates tests/test_web_control_center.py tests/test_workflows.py tests/test_aictl.py tests/test_registry.py Tasks page shows useful workflow buttons based on task status. Prepare for Codex can be launched from a task row with explicit confirmation. Refresh Context can be launched from a task row with explicit confirmation. Submit for Review can be launched from a task row with explicit confirmation. Workflow actions route through governed workflow/aictl paths. UI displays clear success/failure output and next action hints. No direct protected-file writes are introduced. Tests and project-control validations pass. Verify that buttons are not shown for invalid task states. Verify that every write workflow requires confirmation. Verify that Prepare for Codex produces the instruction to send Codex.","schema_version":1,"task_id":"TASK-039"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-039`
Limit: `8`
Docs revision: `23`
Tasks revision: `364`
Indexed source documents: `10`
Indexed chunks: `890`
Selected chunks: `8`
Excluded registered sources: `134`

## Selected Source Paths

- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `93`
- template document excluded by default: `41`

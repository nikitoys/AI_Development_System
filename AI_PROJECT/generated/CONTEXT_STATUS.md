<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-044 UIX-07 Add Task Review Done Controls Add UI controls for closing reviewed tasks and requesting changes from the Tasks page while preserving Human Owner review gates. Expose the task review completion part of the pipeline in the Web Control Center. The owner should be able to approve a task and move it to done, or request changes, directly from the UI when the task is in_review. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add status-aware review controls for tasks in in_review. Add Approve & Done action routed through the existing task.close_reviewed workflow. Add Request Changes action routed through an existing governed task transition path or a minimal governed workflow wrapper if needed. Require explicit confirmation before any review decision. Require owner notes for Approve & Done and Request Changes. Show clear success/failure result through the unified action result panel. After Approve & Done, show next actions such as accepting the linked Evolution Change or preparing the next task. Do not show Done controls for tasks that are not in_review. Add tests for valid close, invalid status, missing notes, request changes, and no direct state writes. Do not auto-approve tasks. Do not auto-close tasks without explicit Human Owner confirmation. Do not accept linked Evolution Changes automatically. Do not bypass task lifecycle validation. Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**. Do not change task lifecycle semantics except adding a governed UI wrapper if strictly required. ai_project_ctl/web/actions.py ai_project_ctl/web/server.py ai_project_ctl/web/read_model.py ai_project_ctl/core/workflows.py if a minimal review workflow wrapper is needed ai_project_ctl/core/registry.py if workflow/action metadata needs compatible updates scripts/aictl.py if command routing needs compatible updates tests/test_web_control_center.py tests/test_workflows.py tests/test_aictl.py tests/test_registry.py Tasks in in_review show Approve & Done and Request Changes controls. Approve & Done requires explicit confirmation and owner notes. Approve & Done routes through task.close_reviewed or another governed workflow path. Request Changes requires explicit confirmation and owner notes. Review actions are hidden or disabled for invalid task statuses. UI shows clear result summary and next actions after review decisions. Linked Evolution Change is suggested after task completion but is not accepted automatically. No direct protected-file writes are introduced. Tests and project-control validations pass. Verify that Done cannot be applied to planned, ready, in_progress, or already done tasks. Verify that owner notes are required. Verify that all writes route through governed workflows/commands. Verify that linked Change acceptance remains a separate explicit action.","schema_version":1,"task_id":"TASK-044"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-044`
Limit: `8`
Docs revision: `23`
Tasks revision: `404`
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

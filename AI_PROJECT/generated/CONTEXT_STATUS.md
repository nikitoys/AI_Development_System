<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-047 UIX-10 Add Task Review Package View Add a task review view that combines task metadata, linked Change, Codex report, changed files, checks, and owner decision controls. Create a review-oriented UI view for tasks in review. The owner should be able to see what Codex changed, what checks passed, what blockers remain, and then make a review decision from one place. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add a Task Review view or drawer in the Web Control Center. Show task ref, legacy id, title, status, summary, scope, and acceptance criteria. Show linked Evolution Change status when available. Show latest Codex execution report when available. Show changed source files and generated/project-control files from the report. Show checks and their pass/fail/warn status. Show warnings, blockers, and notes from the report. Expose Approve & Done and Request Changes controls when valid. Use the unified action result panel for review decisions. Add tests for review view with report, without report, with linked Change, and invalid states. Do not auto-approve tasks. Do not auto-accept Evolution Changes. Do not replace Human Owner review. Do not execute tests from the review view in this task. Do not edit source or generated files from the review view. ai_project_ctl/web/read_model.py ai_project_ctl/web/server.py ai_project_ctl/web/actions.py ai_project_ctl/core/workflows.py if review action metadata needs compatible updates tests/test_web_control_center.py tests/test_workflows.py Task Review view shows task metadata and acceptance context. Task Review view shows latest Codex execution report when available. Task Review view shows linked Evolution Change status when available. Task Review view shows checks, changed files, warnings, blockers, and notes. Owner can make valid review decisions from the view using governed actions. Review decision controls remain unavailable for invalid statuses. Tests and project-control validations pass. Verify that the owner can understand what is being accepted before pressing Done. Verify that missing Codex report is shown clearly and does not crash the view. Verify that review controls still require confirmation and notes.","schema_version":1,"task_id":"TASK-047"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-047`
Limit: `8`
Docs revision: `23`
Tasks revision: `432`
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

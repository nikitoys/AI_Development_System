<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-045 UIX-08 Add Next Action and Blocked Reason Hints Show actionable next steps and blocked reasons for tasks, changes, and epics in the Web Control Center. Improve the UI pipeline by explaining what the owner can do next and why an action is unavailable. The Tasks page should not silently hide important actions without showing dependency, lifecycle, current-task, or Evolution Change reasons. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add next-action hints for task rows and task focus sections. Show why Prepare for Codex is unavailable, such as unmet dependencies, missing approved Change, invalid status, or another current task. Show why Submit for Review is unavailable, such as task not in_progress or stale context/Codex state. Show why Approve & Done is unavailable, such as task not in_review. Show linked Evolution Change status when available. Show suggested actions such as Create Change, Approve Change, Prepare for Codex, Refresh Context, Submit for Review, Approve & Done, Accept Change, or Close Epic. Add blocked reason hints for Evolution actions where useful. Add blocked reason hints for epic close where useful. Keep hints read-only; actual writes must remain separate confirmed actions. Add tests for dependency-blocked tasks, missing Change, invalid status actions, and next action suggestions. Do not auto-run any suggested action. Do not auto-create or auto-approve Evolution Changes. Do not auto-close tasks or epics. Do not weaken lifecycle gates. Do not introduce arbitrary command execution. Do not directly edit protected project-control files. ai_project_ctl/web/read_model.py ai_project_ctl/web/server.py ai_project_ctl/web/actions.py if action metadata needs compatible updates ai_project_ctl/core/workflows.py if workflow metadata needs compatible updates ai_project_ctl/core/registry.py if command metadata needs compatible updates tests/test_web_control_center.py tests/test_workflows.py tests/test_registry.py Tasks page shows next-action hints for common pipeline states. Unavailable actions show a clear reason instead of disappearing silently. Tasks blocked by dependencies show which dependencies are not done. Tasks requiring an Evolution Change show whether the linked Change is missing, ready, approved, in_review, or accepted. UI suggests the correct next owner action without executing it automatically. Hints are consistent with lifecycle validation and existing workflows. No new unsafe write behavior is introduced. Tests and project-control validations pass. Evolution Change Proposal rows remain readable in normal viewport widths by using compact summaries, collapsed details, or horizontal overflow protection. Long affected files, risks, impacts, and metadata do not make the main Evolution table unusable. Verify that WFA tasks with dependencies show useful blocked reasons. Verify that missing or unapproved Evolution Changes are explained clearly. Verify that hints do not bypass confirmation gates. Verify that suggested actions match the actual valid workflow path.","schema_version":1,"task_id":"TASK-045"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-045`
Limit: `8`
Docs revision: `23`
Tasks revision: `422`
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

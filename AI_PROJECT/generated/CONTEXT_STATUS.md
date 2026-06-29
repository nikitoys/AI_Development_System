<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-264 Build UI batch queue helper Add a Web UI queue builder that can create a selected queue for multiple tasks instead of one selected task. The existing selected-task UI queue builder remains single-task; this task adds a separate batch queue helper. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add a new helper for UI-triggered batch queues without changing the existing selected-task helper. Support task_refs, epic_ids, statuses, max_tasks, order_by, and internal change gate bypass metadata. Validate max_tasks as a positive integer and preserve policy defaults when a field is omitted. Return selected_queue metadata compatible with existing create_session and queue preview behavior. Do not add the Web action in this task. Do not change batch runner execution behavior in this task. Do not change the existing build_ui_run_selected_queue contract. Do not edit protected project-control files manually. ai_project_ctl/pipeline/ui_run.py tests/test_ui_run_command.py The new helper can build a queue with max_tasks greater than 1. The new helper can include epic_ids and statuses without requiring a single selected task_ref. The existing selected-task helper still returns max_tasks equal to 1. The produced queue uses only fields already understood by pipeline session creation and queue preview. Tests cover task_refs, epic/status selection, max_tasks, and order_by behavior. Verify that the helper is a queue builder only and does not execute pipeline phases.","schema_version":1,"task_id":"TASK-264"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-264`
Limit: `8`
Docs revision: `28`
Tasks revision: `1805`
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

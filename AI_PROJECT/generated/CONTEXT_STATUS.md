<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-265 Add Web batch run action Add an owner-confirmed Web action that creates and runs a multi-task pipeline session using the existing batch runner. The new action should be a batch entrypoint over the existing pipeline, not a new execution engine. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Register a ui.run_task_batch Web action with owner confirmation. Accept task_ref, epic, status_filter, max_tasks, order_by, and auto_close_note fields. Create a pipeline session using the new UI batch queue helper and the resolved UI pipeline policy. Run the created session through the existing run_until_blocker batch runner. Do not add visual form layout in this task. Do not change the selected-task Run action behavior. Do not implement dirty preflight in this task. Do not edit protected project-control files manually. ai_project_ctl/web/actions.py ai_project_ctl/pipeline/ui_run.py tests/test_web_control_center.py tests/test_ui_run_command.py The ui.run_task_batch action is listed as an implemented confirmed Web action. The action can create a session with max_tasks greater than 1. The action delegates execution to the existing run_until_blocker function. The action result includes session_id, session_href, selected policy, and requested queue inputs. The selected-task ui.run_selected_task action remains unchanged for one-task runs. Tests cover action registration, argument handling, session creation, and run_until_blocker delegation. Verify that the action does not duplicate batch runner logic and only wires the Web entrypoint.","schema_version":1,"task_id":"TASK-265"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-265`
Limit: `8`
Docs revision: `28`
Tasks revision: `1810`
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

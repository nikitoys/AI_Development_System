<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-163 Propagate UI Run queue metadata in Web action Make the Web Run button create pipeline sessions with the same UI single-task queue metadata as CLI `ui run`. Fixes the Web `ui.run_selected_task` path where internal Change gate bypass settings are not copied into the pipeline session. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Update Web `ui.run_selected_task` session creation to pass selected_queue from the shared UI run queue helper. Read allow_internal_change_gate_bypass from effective UI settings when building the Web Run selected queue. Keep Web Run result shape, redirect target, and session link behavior unchanged. Add Web action regression tests that prove the selected_queue contains UI run metadata and bypass flag. Do not change CLI `ui run` behavior in this task. Do not bypass approved Change gates for non-internal product tasks. Do not disable Machine Review or approved Change gates. Do not edit protected project-control files manually. ai_project_ctl/web/actions.py tests/test_web_control_center.py Posting Web action `ui.run_selected_task` creates a session whose selected_queue includes created_by_command=ui.run and ui_run_confirmed=true. When allow_internal_change_gate_bypass=true in UI settings, Web Run session selected_queue includes allow_internal_change_gate_bypass=true. When allow_internal_change_gate_bypass=false in UI settings, Web Run session selected_queue includes allow_internal_change_gate_bypass=false. Web Run still returns session_href and redirect_target for the created session. Existing Web Control Center tests pass. Reject if Web action creates sessions through task_refs/max_tasks/order_by instead of selected_queue. Reject if bypass behavior is applied globally rather than only through confirmed UI single-task session metadata.","schema_version":1,"task_id":"TASK-163"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-163`
Limit: `8`
Docs revision: `28`
Tasks revision: `1122`
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

<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-136 PIPE-052 Add pipeline session status JSON endpoint Add a read-only JSON endpoint that returns compact live status for one pipeline session. This enables the Web Control Center to refresh session status without reloading the full HTML page. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add a read-only route for compact pipeline session status JSON. Return session id, status, current task, current phase, phase status, stop reason, next action and phase history summary. Return stable errors for missing or invalid session ids. Add focused tests for successful and missing-session responses. Do not mutate pipeline session state. Do not change pipeline execution behavior. Do not add frontend polling in this task. ai_project_ctl/web/server.py ai_project_ctl/web/read_model.py tests/test_web_control_center.py The new endpoint returns JSON for an existing pipeline session. The JSON payload contains status, current_phase, current_phase_status, stop_reason, next_action and phase_history summary. The endpoint does not render full HTML. Missing sessions return a stable non-success response. Existing Web Control Center pages continue to render. Verify that the endpoint is read-only and does not invalidate or mutate caches unnecessarily.","schema_version":1,"task_id":"TASK-136"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-136`
Limit: `8`
Docs revision: `28`
Tasks revision: `1206`
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

<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-239 Replace Tasks metrics with action counts Replace non-actionable /tasks metrics with owner-actionable counts for Needs Decision, Ready To Run, Current, Blocked, and Health Issues. Counts like done and visible are useful for inventory, but the Owner Cockpit default should show work that needs attention. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Compute action queue counts for Needs Decision, Ready To Run, Current, Blocked, and Health Issues. Render these counts in the /tasks default Action Queue view. Keep inventory-style metrics available only in Full Inventory or diagnostic views if they already exist. Add regression coverage for the displayed action counts. Do not remove task inventory data from the system. Do not change task statuses or stored task counts. Do not edit protected project-control files manually. ai_project_ctl/web/read_model.py ai_project_ctl/web/server.py tests/test_web_control_center_read_model.py tests/test_web_control_center.py The default /tasks metrics show Needs Decision, Ready To Run, Current, Blocked, and Health Issues. The default /tasks metrics do not emphasize done count as a primary owner-action metric. Metric counts match the rendered action queue groups. Metrics remain usable when there is no current task. Tests cover the action-count metrics. Compare metric counts with the queue groups rendered below them.","schema_version":1,"task_id":"TASK-239"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-239`
Limit: `8`
Docs revision: `28`
Tasks revision: `1646`
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

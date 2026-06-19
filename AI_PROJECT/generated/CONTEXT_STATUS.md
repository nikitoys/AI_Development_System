<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-038 UIX-01 Improve Tasks filtering grouping and collapse Make the Tasks page usable for large projects by adding initiative/epic/status filters, search, grouping, and collapsible done sections. Improve the Web Control Center Tasks page so the owner can focus on one initiative, one epic, or active tasks only instead of scrolling through the full task history. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add filtering by Initiative. Add filtering by Epic. Add filtering by Status. Add search by task ref, legacy id, title, and summary. Add grouping by Epic and Status. Add collapsible groups. Hide done tasks by default or collapse done groups by default. Show readable task refs such as WFA-04 alongside legacy TASK-XXX ids. Preserve read-only/dashboard performance improvements. Do not add new write actions in this task. Do not change task lifecycle rules. Do not change task identity/ref allocation. Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**. ai_project_ctl/web/read_model.py ai_project_ctl/web/server.py ai_project_ctl/web/actions.py if filter state needs action metadata tests/test_web_control_center.py tests/test_aictl.py if aictl web routing is touched Tasks page can be filtered by initiative, epic, status, and search text. Tasks page can group tasks by epic or status. Done tasks are hidden or collapsed by default. Current task, in-progress tasks, and review tasks remain easy to find. GET / and GET /data.json remain fast and do not run full doctor on every request. No new write behavior is introduced. Tests and project-control validations pass. Verify that filtering and grouping work with EPIC-005/CTL and EPIC-006/WFA. Verify that done tasks no longer dominate the default task view. Verify that Web write safety is unchanged.","schema_version":1,"task_id":"TASK-038"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-038`
Limit: `8`
Docs revision: `23`
Tasks revision: `359`
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

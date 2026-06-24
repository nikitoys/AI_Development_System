<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-145 PIPE-061 Add Web Settings page route Add a Web Control Center Settings page that displays effective UI settings and their source file. This creates the read-only Web UI surface for project-local settings before adding write actions. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add a Settings navigation item and route in the Web Control Center. Render effective UI settings including source, path and current values. Show settings in a human-readable form without requiring terminal commands. Add focused tests that the Settings page renders with default and project-file settings. Do not add settings mutation in this task. Do not change pipeline execution behavior. Do not expose non-UI project secrets or environment variables. ai_project_ctl/web/server.py tests/test_web_control_center.py The Web Control Center navigation includes a Settings page link. The Settings page shows the effective UI settings source and path. The Settings page renders command_line, default_policy and timeout settings when present. The Settings page is read-only in this task. Existing Web Control Center tests continue to pass. Verify that the route is read-only and does not mutate settings.","schema_version":1,"task_id":"TASK-145"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-145`
Limit: `8`
Docs revision: `28`
Tasks revision: `1014`
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

<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-147 PIPE-063 Add internal change-gate bypass UI setting Add a disabled-by-default UI setting for explicitly bypassing approved Change requirements on internal project-control tasks. This introduces the setting data contract without yet changing pipeline execution behavior. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add a default false setting for internal project-control Change gate bypass. Parse boolean string values safely for the new setting. Expose the setting through effective UI settings output. Add tests for default, true, false and invalid values. Do not bypass the Change gate in this task. Do not change built-in pipeline policy presets. Do not enable the setting by default. ai_project_ctl/ui_settings.py tests/test_ui_settings.py Effective UI settings include the new bypass setting with default false. String values such as true, false, 1 and 0 are parsed predictably. Invalid boolean values produce a stable settings error or validation failure. Existing UI settings behavior remains compatible. Tests cover the new setting defaults and parsing. Verify that this task adds only configuration support and does not weaken execution gates.","schema_version":1,"task_id":"TASK-147"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-147`
Limit: `8`
Docs revision: `28`
Tasks revision: `1039`
Indexed source documents: `10`
Indexed chunks: `891`
Selected chunks: `8`
Excluded registered sources: `135`

## Selected Source Paths

- ai-system/project-control/03-state-model.md
- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/project-control/07-validation-and-tests.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `94`
- template document excluded by default: `41`

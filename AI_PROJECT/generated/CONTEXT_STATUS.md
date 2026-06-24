<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-149 PIPE-065 Apply internal Change gate bypass to UI runs Allow confirmed UI runs to skip approved Change requirements only for internal project-control tasks when the bypass setting is enabled. This implements the actual execution behavior behind the Settings checkbox with strict safety boundaries and audit evidence. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Define an internal project-control task predicate for safe bypass eligibility. Apply the bypass only to UI-created single-task sessions when the setting is enabled. Record explicit phase artifacts or audit details when the Change gate is bypassed. Keep approved Change requirements unchanged for non-internal tasks and non-UI execution paths. Do not disable the Change gate globally. Do not bypass token, report, verify, review, close or commit gates. Do not auto-approve or auto-create Evolution Changes. ai_project_ctl/pipeline/prepare_phase.py ai_project_ctl/pipeline/runner.py ai_project_ctl/pipeline/ui_policy.py scripts/aictl.py tests/pipeline/test_prepare_phase.py tests/test_ui_run_command.py When the setting is disabled, UI runs still require an approved linked Change. When the setting is enabled, eligible internal project-control tasks can pass prepare without an approved linked Change. Non-internal tasks still block on missing approved Change even when the setting is enabled. Bypass usage is recorded in phase artifacts or audit details. Tests cover enabled, disabled and non-internal task behavior. Review the internal-task predicate carefully to avoid allowing product-code tasks through the bypass.","schema_version":1,"task_id":"TASK-149"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-149`
Limit: `8`
Docs revision: `28`
Tasks revision: `1062`
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

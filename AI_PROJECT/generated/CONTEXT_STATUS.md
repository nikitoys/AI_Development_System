<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-129 Add Codex preflight for UI Run Add a Codex executable preflight that checks the configured command before launching an executable Run. This task prevents the Run command from starting executable sessions when the local Codex sandbox is unavailable. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add a Codex preflight service that reads command_line from effective UI settings. Run a minimal prompt through the configured command. Detect sandbox-unavailable output such as bwrap or RTM_NEWADDR. Expose the preflight through aictl for UI and backend usage. Do not attempt to repair OS-level sandbox permissions. Do not change Codex CLI configuration files. Do not mutate task, pipeline, or report state during preflight. ai_project_ctl/pipeline/codex_preflight.py ai_project_ctl/pipeline/codex_adapter.py ai_project_ctl/ui_settings.py scripts/aictl.py tests/pipeline/test_codex_preflight.py Preflight returns passed when the configured command exits successfully. Preflight returns a blocked result when bwrap, RTM_NEWADDR, user namespace, or Operation not permitted appears in output. Preflight uses the effective command_line setting. Preflight does not write project-control state or generated files. UI Run can use the preflight result to block executable execution before starting a session. Verify that sandbox detection is shared with or consistent with the Codex adapter.","schema_version":1,"task_id":"TASK-129"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-129`
Limit: `8`
Docs revision: `28`
Tasks revision: `942`
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

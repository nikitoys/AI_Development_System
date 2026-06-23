<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-132 PIPE-048 Render phase execution artifacts and failure evidence Show phase execution artifacts, failure evidence and log snippets for failed phase-based pipeline sessions. When execute fails, the Web UI should expose the useful adapter evidence without requiring the owner to inspect raw JSON. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Render phase artifacts from phase_history entries in the Pipeline details panel. Show execute failure fields including error_code, command_ref, timeout_sec, duration_sec and reason. Show bounded stdout and stderr snippets from execute_evidence or adapter artifacts. Show prompt path, context pack path and report instruction when available. Do not store new execution evidence in pipeline state. Do not increase Codex timeout in this task. Do not expose unbounded logs in the Web UI. ai_project_ctl/web/server.py tests/test_web_control_center.py A CODEX_ADAPTER_TIMEOUT phase shows CODEX_ADAPTER_TIMEOUT in the Web UI. The UI displays timeout_sec and duration_sec for failed execute phases. The UI displays command_ref for local Codex execution. Large stderr snippets are bounded by the existing Web UI log snippet limit. Tests cover rendering of execute_evidence and adapter artifacts. Verify that large log fields are escaped and truncated safely.","schema_version":1,"task_id":"TASK-132"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-132`
Limit: `8`
Docs revision: `28`
Tasks revision: `973`
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

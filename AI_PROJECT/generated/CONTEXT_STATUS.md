<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-049 UIX-12 Add Project Health Repair Actions Add UI health and repair actions for doctor, stale generated artifacts, docs render, context/Codex refresh, and protected-file checks. Turn common project-control warnings into visible UI health signals with safe repair buttons that route through owning CLIs. The owner should be able to diagnose and fix stale generated artifacts without remembering individual commands. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Show project doctor summary in the Web Control Center. Show stale context, Codex, docs, task generated, and evolution generated states where detectable. Add Run Doctor action. Add Refresh Context/Codex action for current or selected task where valid. Add Render Docs action through docctl where valid. Add Check Protected Files action. Show before/after action result through the unified result panel. Reject repair actions when no safe target task exists. Add tests for doctor pass/warn/fail display and safe repair action routing. Do not auto-repair without owner confirmation. Do not manually edit generated files. Do not suppress doctor failures. Do not bypass owning CLIs. Do not add network or external service dependencies. ai_project_ctl/web/read_model.py ai_project_ctl/web/server.py ai_project_ctl/web/actions.py ai_project_ctl/core/workflows.py if repair workflow metadata needs compatible updates ai_project_ctl/core/registry.py if command metadata needs compatible updates scripts/aictl.py if routing needs compatible updates tests/test_web_control_center.py tests/test_workflows.py tests/test_aictl.py tests/test_registry.py UI shows project doctor health summary. UI shows stale generated artifact warnings in a readable way. Run Doctor action works through governed command routing. Safe repair actions require confirmation and use owning CLIs. Failed health checks remain visible and are not hidden as success. No direct generated-file edits are introduced. Tests and project-control validations pass. Verify that repair actions do not run silently. Verify that stale context/Codex and docs cases are shown clearly. Verify that doctor FAIL is not converted into OK by UI formatting.","schema_version":1,"task_id":"TASK-049"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-049`
Limit: `8`
Docs revision: `23`
Tasks revision: `449`
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

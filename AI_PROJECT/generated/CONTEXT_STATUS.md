<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-048 UIX-11 Add Current Execution Status Panel Add a UI panel showing current task, Context Pack status, Codex prompt status, and safe execution-context actions. Make the current execution state visible in the Web Control Center so the owner knows which task is prepared for Codex and whether the context/prompt artifacts are ready or stale. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Show current task ref/id/title/status in the dashboard and task pages. Show Context Pack status: ready, stale, missing, or unknown. Show Codex prompt/status: ready, stale, missing, or blocked. Show generated prompt path and context pack path. Add Copy Codex Instruction action when prompt is ready. Expose safe Refresh Context and Refresh Prompt actions through existing governed workflows. Expose Clear Current action only with explicit confirmation. Show warnings when current task differs from selected task. Add tests for ready, stale, missing, and no-current-task states. Do not auto-run Codex. Do not auto-switch current task without confirmation. Do not directly edit current_execution.json. Do not directly edit generated context or Codex files. Do not weaken protected-file checks. ai_project_ctl/web/read_model.py ai_project_ctl/web/server.py ai_project_ctl/web/actions.py ai_project_ctl/core/workflows.py if execution-context workflow metadata needs compatible updates ai_project_ctl/core/registry.py if action metadata needs compatible updates tests/test_web_control_center.py tests/test_workflows.py tests/test_registry.py UI clearly shows the current task when one is selected. UI clearly shows when no current task exists. UI shows Context Pack and Codex prompt readiness/staleness. Owner can copy the Codex handoff instruction when prompt is ready. Refresh and clear actions route through governed workflows/commands. No direct protected-file writes are introduced. Tests and project-control validations pass. Verify that stale context/prompt states are visible. Verify that the current task cannot be changed silently. Verify that Copy Codex Instruction matches the generated prompt path.","schema_version":1,"task_id":"TASK-048"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-048`
Limit: `8`
Docs revision: `23`
Tasks revision: `442`
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

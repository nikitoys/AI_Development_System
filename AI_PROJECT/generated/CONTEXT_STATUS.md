<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-067 BUG-01 Fix Approve & Done stale execution context handling Fix the Web Control Center / workflow issue where Approve & Done can be blocked by stale Context Pack or Codex prompt state and where closed tasks can leave a stale Codex execution package behind. Implement options B + C from the review: B) Approve & Done must not require Refresh Context when the task is already in review and owner approval notes are provided; stale execution context may be reported as a warning, not a lifecycle blocker. C) after a reviewed task is successfully approved and transitioned to done, clear or invalidate current Codex execution state when it still points to the closed task. AI_PROJECT/generated/CODEX_CURRENT.md Approve & Done closes reviewed tasks without requiring Refresh Context, and stale Codex execution state is cleared after task closure. Adjust task.close_reviewed so stale Context Pack / Codex prompt freshness does not block Human Owner approval and done transition. Keep owner confirmation and non-empty approval notes mandatory for Approve & Done. Keep task lifecycle, task graph, generated task output, evolution, protected-file, and project doctor checks where they are relevant to closure. Preserve visibility of stale context/prompt state as a warning or result detail instead of hiding it. After successful Approve & Done, clear or invalidate current_execution when it targets the task that was just closed. Use an existing governed command such as codexctl.py clear if suitable, or add a small registered/facade workflow step if needed. Update Web Control Center hints so an in_review task can still expose Approve & Done even when execution context is stale. Add or update tests covering stale context in_review close, post-close execution cleanup, required approval notes, invalid status rejection, and no direct protected-file writes. Do not weaken Human Owner approval gates. Do not allow Codex to self-approve tasks. Do not silently accept linked Evolution Changes. Do not hide stale context/prompt warnings from the UI or action result. Do not auto-refresh Context Pack or Codex Prompt as part of approval unless explicitly justified by the implementation. Do not manually edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**. ai_project_ctl/core/workflows.py ai_project_ctl/core/registry.py ai_project_ctl/web/read_model.py ai_project_ctl/web/actions.py scripts/aictl.py scripts/codexctl.py tests/test_workflows.py tests/test_web_control_center.py tests/test_aictl.py tests/test_registry.py ai-system/project-control/08-usage-guide.md if owner-facing workflow documentation needs a small clarification ai-system/project-control/10-owner-quickstart.md if owner-facing workflow documentation needs a small clarification A task in in_review with stale Context Pack or stale Codex prompt can be closed through Approve & Done when explicit owner notes and confirmation are provided. Approve & Done still rejects tasks outside in_review. Approve & Done still requires non-empty owner approval notes. Stale Context Pack / Codex prompt state remains visible as a warning, blocked reason, or action-result detail, but does not force Refresh Context before owner acceptance. After successful Approve & Done, current_execution is cleared or marked non-ready when it points to the closed task. Closing one task does not clear an execution package that points to a different active task. All writes continue to route through governed CLI/workflow paths. Relevant tests pass and project-control validation/check-generated commands pass. Verify that the fix implements options B + C, not option A. Verify that no approval gate was weakened and owner notes remain required. Verify that stale execution context is not hidden, only made non-blocking for closure. Verify that current_execution cleanup is conditional on the closed task identity. Verify that generated files were not edited manually.","schema_version":1,"task_id":"TASK-067"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-067`
Limit: `8`
Docs revision: `24`
Tasks revision: `577`
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

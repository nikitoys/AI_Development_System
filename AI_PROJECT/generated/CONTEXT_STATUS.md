<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-032 WFA-01 Add Task Workflow Automation MVP Add high-level workflow actions for preparing tasks for Codex, refreshing execution context, and submitting tasks for review. Introduce workflow automation that composes existing registered commands without bypassing validation, audit, generated-output rules, protected-file policy, or owner gates. AI_PROJECT/generated/CODEX_TASKS.md Task workflow automation MVP is implemented with protected-file and owner-gate safeguards. Add workflow list/describe support. Add task.prepare_for_codex workflow. Add task.refresh_execution_context workflow. Add task.submit_for_review workflow. Add UI buttons for these workflows if allowed. Show step preview before execution. Require explicit confirmation for write workflows. Route workflow steps through registered commands or existing validated CLI/facade paths. Preserve Web write safety. Add tests for workflow execution, confirmation, failure handling, and cache invalidation if Web UI is touched. Do not auto-run Codex. Do not auto-approve tasks. Do not auto-close tasks. Do not accept Evolution Changes. Do not create task/evolution creation wizards in this task. Do not directly edit protected project-control files. ai_project_ctl/core/workflows.py ai_project_ctl/web/actions.py if workflow actions are exposed in UI ai_project_ctl/web/server.py if workflow routes/buttons are exposed in UI ai_project_ctl/web/read_model.py if UI read model needs workflow metadata ai_project_ctl/core/registry.py if workflow command metadata is needed scripts/aictl.py tests/** AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/CODEX_CURRENT.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only Owner can prepare a task for Codex with one CLI workflow or one UI action. Prepare workflow sets/validates current task, moves task to in_progress when valid, refreshes context, refreshes Codex prompt, and runs doctor. Refresh context workflow rebuilds Context Pack and Codex prompt for a task. Submit-review workflow runs required checks and moves task to in_review only when blocking checks pass. All write workflows require explicit confirmation. Workflows do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**. Existing individual commands still work. Tests and validations pass. Verify command routing, confirmation gates, Web write safety, protected-file policy, tests, and validation output.","schema_version":1,"task_id":"TASK-032"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-032`
Limit: `8`
Docs revision: `22`
Tasks revision: `306`
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

<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-022 Task D - Introduce ai_project_ctl core package Create shared internal services that future CLI and Web UI both use. Implement the core control-plane package for store loading/saving, audit events, validation, rendering triggers, result objects, error model, locking, and atomic writes while preserving existing behavior. ai_project_ctl/core Shared core services exist with tests and existing ctl behavior remains compatible. Create ai_project_ctl/core store, events, validation, registry, renderer, ids, locks, result, and error support as needed. Move shared state loading, saving, event append, validation hooks, rendering triggers, and atomic write helpers into reusable services. Add tests for core package behavior. Preserve current planctl.py, taskctl.py, docctl.py, contextctl.py, codexctl.py, and evolutionctl.py behavior. Do not replace all old ctl scripts in this task. Do not add web UI files. Do not change lifecycle rules beyond approved scope. ai_project_ctl/** tests/** scripts/*ctl.py AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only Existing behavior remains compatible. Core package has tests. No domain command should need to write state directly after migration path is established. State mutation still goes through validated CLI/service paths. Verify behavior compatibility for existing ctl commands. Verify tests cover atomic writes, event append, validation errors, and render trigger behavior where implemented.","schema_version":1,"task_id":"TASK-022"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-022`
Limit: `8`
Docs revision: `19`
Tasks revision: `209`
Indexed source documents: `10`
Indexed chunks: `890`
Selected chunks: `8`
Excluded registered sources: `130`

## Selected Source Paths

- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/project-control/07-validation-and-tests.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `89`
- template document excluded by default: `41`

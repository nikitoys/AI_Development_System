<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-020 Task B - Design unified control-plane architecture Record the target architecture for a shared command/service layer before implementation. Design the future scripts/aictl.py entrypoint and ai_project_ctl package structure, including store, events, validation, registry, renderer, IDs, locks, domain services, and web shell boundaries. ai-system/project-control/control-plane-architecture.md Architecture recorded in an approved design artifact; no implementation yet. Describe scripts/aictl.py as the preferred unified CLI facade. Describe ai_project_ctl/core services for store, events, validation, registry, renderer, ids, and locks. Describe ai_project_ctl/domains services for tasks, epics, changes, reviews, evolution, codex, and context. Describe ai_project_ctl/web as a thin local UI over the same command registry. State the transaction rule: Command -> Validate -> Append Event -> Mutate State -> Regenerate Views -> Return Result. State that generated/*.md is derived and must not be edited manually. Do not create ai_project_ctl package files. Do not create scripts/aictl.py. Do not change existing ctl behavior. Do not bypass evolution approval for future source changes. ai-system/project-control/control-plane-architecture.md AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only Architecture is recorded in the plan/task description or an approved design artifact. Design explicitly states that Web UI cannot bypass the command layer. Design explicitly states generated/*.md is derived and must not be edited manually. No implementation files are created in this design task. Verify that the architecture preserves existing project-control source-of-truth boundaries. Verify that future implementation still requires controlled evolution approval where behavior changes.","schema_version":1,"task_id":"TASK-020"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-020`
Limit: `8`
Docs revision: `19`
Tasks revision: `197`
Indexed source documents: `10`
Indexed chunks: `890`
Selected chunks: `8`
Excluded registered sources: `130`

## Selected Source Paths

- ai-system/project-control/03-state-model.md
- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `89`
- template document excluded by default: `41`

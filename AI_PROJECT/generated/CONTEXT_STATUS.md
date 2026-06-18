<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-021 Task C - Add global ID allocation strategy Define a global ID allocation model that prevents task conflicts across parallel epics and future web actions. Specify whether IDs are globally unique or scoped, prefer globally unique TASK-001 style task IDs, define atomic allocation behavior, and define validation for duplicate task IDs across all epics. ai-system/project-control/control-plane-id-allocation.md ID allocation policy recorded with a clear future implementation path. Define global versus scoped ID policy for tasks, epics, changes, and command registry entities. Prefer globally unique task IDs while preserving existing aliases and epic-scoped refs. Design atomic ID allocation for CLI and future web write actions. Design validation that prevents duplicate task IDs across all epics. Define whether ID allocation should write audit events. Do not implement ids.py. Do not migrate existing task IDs. Do not change taskctl.py behavior in this design task. ai-system/project-control/control-plane-id-allocation.md AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only The plan explicitly resolves cross-epic task ID collision risk. There is a clear future implementation path for ids.py or equivalent. Parallel execution risk is accounted for. No ID migration or code behavior change is performed in this design task. Verify that the design is compatible with existing legacy IDs, task aliases, and epic keys. Verify that protected project-control files were not manually edited.","schema_version":1,"task_id":"TASK-021"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-021`
Limit: `8`
Docs revision: `19`
Tasks revision: `204`
Indexed source documents: `10`
Indexed chunks: `890`
Selected chunks: `8`
Excluded registered sources: `130`

## Selected Source Paths

- ai-system/project-control/03-state-model.md
- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/project-control/07-validation-and-tests.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `89`
- template document excluded by default: `41`

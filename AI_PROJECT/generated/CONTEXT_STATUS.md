<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-027 Task I - Add locking and atomic write protection Make parallel project-control operations safer. Add file locking and atomic write behavior for state, events, and generated outputs so concurrent operations cannot corrupt project-control files or leave partial writes. ai_project_ctl/core/locks.py Concurrent writes are guarded by locks and atomic replace semantics with readable errors. Add file lock support for state mutations. Use atomic write via temp file plus replace for protected outputs where appropriate. Return clear errors if another process is writing. Avoid partial writes to state/events/generated files. Add tests for lock contention and atomic write behavior. Do not introduce a database backend. Do not implement remote or multi-user server locking. Do not change lifecycle semantics. ai_project_ctl/core/locks.py ai_project_ctl/core/store.py ai_project_ctl/core/events.py ai_project_ctl/core/renderer.py tests/** AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only Concurrent writes cannot corrupt state. Locking behavior is tested. Error messages are readable. State/events/generated writes avoid partial output. Verify lock implementation is cross-platform enough for the repository's expected local workflow. Verify tests cover contention and failure cleanup.","schema_version":1,"task_id":"TASK-027"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-027`
Limit: `8`
Docs revision: `19`
Tasks revision: `246`
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

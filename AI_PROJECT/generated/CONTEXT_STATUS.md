<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-026 Task H - Add project doctor command Provide one health check for project-control state. Add a project doctor command that reports PASS/WARN/FAIL for duplicate IDs, invalid statuses, lifecycle residue, missing parents, stale generated files, stale Codex outputs, event/state assumptions, missing generated views, and detectable direct mutation risk. scripts/aictl.py project doctor Project doctor reports useful PASS/WARN/FAIL health output and exits non-zero on FAIL. Implement python scripts/aictl.py project doctor or equivalent command registry route. Check duplicate IDs, invalid task status, invalid lifecycle transition residue, missing parent epic, stale generated files, stale CODEX_PROMPT.md or CODEX_STATUS.md, event/state assumptions, missing generated views, and unsupported direct mutations where detectable. Return useful human-readable and automation-friendly output. Add tests or smoke checks for PASS, WARN, and FAIL scenarios. Do not repair state automatically unless a supported render command is explicitly invoked. Do not edit protected files manually. Do not add web UI in this task. scripts/aictl.py ai_project_ctl/** tests/** scripts/check-protected-project-files.py AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only python scripts/aictl.py project doctor reports PASS/WARN/FAIL. Doctor exits non-zero on FAIL. Output is useful for both humans and CI. Doctor does not bypass owning CLI validation or render commands. Verify doctor failures are deterministic and actionable. Verify doctor does not mutate semantic state unexpectedly.","schema_version":1,"task_id":"TASK-026"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-026`
Limit: `8`
Docs revision: `19`
Tasks revision: `238`
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

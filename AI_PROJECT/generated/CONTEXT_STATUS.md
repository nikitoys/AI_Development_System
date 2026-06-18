<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-029 Task K - Add controlled Web write actions Allow safe project-control state changes from UI only after the read-only MVP is stable. Add controlled web write actions for creating tasks, transitioning tasks, requesting review, marking review result, building Codex prompts, and regenerating generated views, with confirmations and audit events through the command registry. ai_project_ctl/web Web write actions use the same command registry and audit path as CLI writes. Add confirmation-backed web actions for task create, task transition, review request, review result, Codex prompt build, and generated view regeneration where supported. Route every write through command registry and shared services. Ensure every write creates the same kind of event as CLI writes. Block invalid transitions and show clear errors. Add tests for confirmation, invalid transition handling, and audit event behavior. Do not bypass command registry from route handlers. Do not add remote hosted deployment. Do not add multi-user authentication unless separately approved. ai_project_ctl/web/** ai_project_ctl/** scripts/aictl.py tests/** AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only Web write path is identical to CLI write path. Audit events are created. Invalid transitions are blocked. Confirmation and error reporting are present. Verify route handlers do not write protected files directly. Verify every successful write has an audit event and validation path.","schema_version":1,"task_id":"TASK-029"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-029`
Limit: `8`
Docs revision: `19`
Tasks revision: `260`
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

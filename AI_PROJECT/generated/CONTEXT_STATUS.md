<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-028 Task J - Add read-only local Web Control Center MVP Provide initial web visibility without mutation risk. Add a read-only local Control Center, preferably FastAPI + Jinja2 + HTMX unless repository constraints suggest otherwise, launched through python scripts/aictl.py web --host 127.0.0.1 --port 8765 and backed by the same command registry. ai_project_ctl/web Local web dashboard shows project-control state read-only through shared command registry. Add read-only dashboard pages for tasks, epics, current task, reviews, events, Codex prompt/status, and doctor output as available. Expose web command through scripts/aictl.py web --host 127.0.0.1 --port 8765. Use the same command/core layer as CLI for all data access. Clearly show current task, queues, stale generated files, and health status. Add tests or smoke checks for read-only route behavior. Do not add web write actions in this task. Do not add authentication or remote hosted deployment. Do not edit JSON directly from route handlers. scripts/aictl.py ai_project_ctl/web/** ai_project_ctl/** tests/** pyproject.toml requirements*.txt AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only Web UI is read-only. Web UI uses the same command/core layer as CLI. Web UI does not edit JSON directly. Web UI clearly shows current task, queues, stale generated files, and health status. Verify route handlers cannot mutate protected state directly. Verify web dashboard remains local-only by default.","schema_version":1,"task_id":"TASK-028"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-028`
Limit: `8`
Docs revision: `19`
Tasks revision: `253`
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

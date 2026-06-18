[SYSTEM]

Active Role: Frontend Developer AI / Backend Developer AI
Active Stage: Read-Only Web MVP
Active Document: ai_project_ctl/web
Expected Result: Local web dashboard shows project-control state read-only through shared command registry.

Repository: current repository
Task ID: TASK-028
Task Ref: CTL-10
Task UID: tsk_1c8f867e1c2c
Legacy Task ID: TASK-028
Task Aliases: TASK-028
Task Epic Key / Local Seq: CTL / 10
Task Title: Task J - Add read-only local Web Control Center MVP
Task Status: in_review
Verification Mode: standard

Initiative: INIT-002 — Centralized AI Project Control Plane
Epic: EPIC-005 — Implement unified aictl and local Control Center foundation

Context:
Provide initial web visibility without mutation risk.

Details:
Add a read-only local Control Center, preferably FastAPI + Jinja2 + HTMX unless repository constraints suggest otherwise, launched through python scripts/aictl.py web --host 127.0.0.1 --port 8765 and backed by the same command registry.

Scope:
- Add read-only dashboard pages for tasks, epics, current task, reviews, events, Codex prompt/status, and doctor output as available.
- Expose web command through scripts/aictl.py web --host 127.0.0.1 --port 8765.
- Use the same command/core layer as CLI for all data access.
- Clearly show current task, queues, stale generated files, and health status.
- Add tests or smoke checks for read-only route behavior.

Out of Scope:
- Do not add web write actions in this task.
- Do not add authentication or remote hosted deployment.
- Do not edit JSON directly from route handlers.

Allowed Files:
- scripts/aictl.py
- ai_project_ctl/web/**
- ai_project_ctl/**
- tests/**
- pyproject.toml
- requirements*.txt
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only

Acceptance Criteria:
- Web UI is read-only.
- Web UI uses the same command/core layer as CLI.
- Web UI does not edit JSON directly.
- Web UI clearly shows current task, queues, stale generated files, and health status.

Review Instructions:
- Verify route handlers cannot mutate protected state directly.
- Verify web dashboard remains local-only by default.

Execution Rules:
- Do not edit AI_PROJECT/state/*.json manually.
- Do not edit AI_PROJECT/events/*.jsonl manually.
- Do not edit AI_PROJECT/generated/*.md manually unless explicitly instructed; prefer CLI render/build commands.
- Stay within Allowed Files and Scope.
- If task state must change, report the required taskctl command instead of editing state by hand.
- At the end, report changed files, checks run, result, and any unresolved risks.

Suggested lifecycle commands:
```bash
python scripts/taskctl.py task transition TASK-028 --to in_progress
python scripts/taskctl.py task transition TASK-028 --to in_review
python scripts/taskctl.py validate
```

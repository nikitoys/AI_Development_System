[SYSTEM]

Active Role: Backend Developer AI / AI System Maintainer
Active Stage: Core Package Implementation
Active Document: ai_project_ctl/core
Expected Result: Shared core services exist with tests and existing ctl behavior remains compatible.

Repository: current repository
Task ID: TASK-022
Task Ref: CTL-04
Task UID: tsk_568bca24b2ff
Legacy Task ID: TASK-022
Task Aliases: TASK-022
Task Epic Key / Local Seq: CTL / 4
Task Title: Task D - Introduce ai_project_ctl core package
Task Status: in_review
Verification Mode: standard

Initiative: INIT-002 — Centralized AI Project Control Plane
Epic: EPIC-005 — Implement unified aictl and local Control Center foundation

Context:
Create shared internal services that future CLI and Web UI both use.

Details:
Implement the core control-plane package for store loading/saving, audit events, validation, rendering triggers, result objects, error model, locking, and atomic writes while preserving existing behavior.

Scope:
- Create ai_project_ctl/core store, events, validation, registry, renderer, ids, locks, result, and error support as needed.
- Move shared state loading, saving, event append, validation hooks, rendering triggers, and atomic write helpers into reusable services.
- Add tests for core package behavior.
- Preserve current planctl.py, taskctl.py, docctl.py, contextctl.py, codexctl.py, and evolutionctl.py behavior.

Out of Scope:
- Do not replace all old ctl scripts in this task.
- Do not add web UI files.
- Do not change lifecycle rules beyond approved scope.

Allowed Files:
- ai_project_ctl/**
- tests/**
- scripts/*ctl.py
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only

Acceptance Criteria:
- Existing behavior remains compatible.
- Core package has tests.
- No domain command should need to write state directly after migration path is established.
- State mutation still goes through validated CLI/service paths.

Review Instructions:
- Verify behavior compatibility for existing ctl commands.
- Verify tests cover atomic writes, event append, validation errors, and render trigger behavior where implemented.

Execution Rules:
- Do not edit AI_PROJECT/state/*.json manually.
- Do not edit AI_PROJECT/events/*.jsonl manually.
- Do not edit AI_PROJECT/generated/*.md manually unless explicitly instructed; prefer CLI render/build commands.
- Stay within Allowed Files and Scope.
- If task state must change, report the required taskctl command instead of editing state by hand.
- At the end, report changed files, checks run, result, and any unresolved risks.

Suggested lifecycle commands:
```bash
python scripts/taskctl.py task transition TASK-022 --to in_progress
python scripts/taskctl.py task transition TASK-022 --to in_review
python scripts/taskctl.py validate
```

[SYSTEM]

Active Role: AI System Maintainer / Project Control Architect
Active Stage: Control Plane Inventory
Active Document: ai-system/project-control/control-plane-inventory.md
Expected Result: Inventory report produced; no code behavior changed.

Repository: current repository
Task ID: TASK-019
Task UID: tsk_d0e6e78d3c7c
Legacy Task ID: TASK-019
Task Aliases: TASK-019
Task Title: Task A - Inventory existing ctl commands and state mutation paths
Task Status: in_review
Verification Mode: standard

Initiative: INIT-002 — Centralized AI Project Control Plane
Epic: EPIC-005 — Implement unified aictl and local Control Center foundation

Context:
Map current ctl scripts, commands, state files, event logs, generated outputs, and direct mutation risks.

Details:
Inventory all current project-control command surfaces before any unification work. The result should make existing write paths, duplicated lifecycle logic, and unsafe direct mutation paths visible.

Scope:
- Identify all scripts/*ctl.py files and their command domains.
- List supported commands by domain and classify read, write, render, validation, and audit behavior.
- Identify duplicated lifecycle logic and direct state/events/generated mutation paths.
- Identify task ID collision risks across epics and aliases.
- Produce a readable inventory artifact if an approved standard location exists.

Out of Scope:
- Do not implement aictl.py.
- Do not refactor existing ctl scripts.
- Do not create web app files.
- Do not manually edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.

Allowed Files:
- ai-system/project-control/control-plane-inventory.md
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only

Acceptance Criteria:
- Existing ctl surface is documented.
- Write paths are known.
- Gaps and unsafe paths are listed.
- No code behavior changed.

Review Instructions:
- Verify that protected project-control files were changed only through the owning CLI.
- Verify that this is inventory only and does not alter ctl script behavior.

Execution Rules:
- Do not edit AI_PROJECT/state/*.json manually.
- Do not edit AI_PROJECT/events/*.jsonl manually.
- Do not edit AI_PROJECT/generated/*.md manually unless explicitly instructed; prefer CLI render/build commands.
- Stay within Allowed Files and Scope.
- If task state must change, report the required taskctl command instead of editing state by hand.
- At the end, report changed files, checks run, result, and any unresolved risks.

Suggested lifecycle commands:
```bash
python scripts/taskctl.py task transition TASK-019 --to in_progress
python scripts/taskctl.py task transition TASK-019 --to in_review
python scripts/taskctl.py validate
```

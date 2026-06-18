[SYSTEM]

Active Role: AI System Maintainer / Project Control Architect
Active Stage: ID Allocation Design
Active Document: ai-system/project-control/control-plane-id-allocation.md
Expected Result: ID allocation policy recorded with a clear future implementation path.

Repository: current repository
Task ID: TASK-021
Task UID: tsk_c04df4f0310f
Legacy Task ID: TASK-021
Task Aliases: TASK-021
Task Title: Task C - Add global ID allocation strategy
Task Status: in_review
Verification Mode: standard

Initiative: INIT-002 — Centralized AI Project Control Plane
Epic: EPIC-005 — Implement unified aictl and local Control Center foundation

Context:
Define a global ID allocation model that prevents task conflicts across parallel epics and future web actions.

Details:
Specify whether IDs are globally unique or scoped, prefer globally unique TASK-001 style task IDs, define atomic allocation behavior, and define validation for duplicate task IDs across all epics.

Scope:
- Define global versus scoped ID policy for tasks, epics, changes, and command registry entities.
- Prefer globally unique task IDs while preserving existing aliases and epic-scoped refs.
- Design atomic ID allocation for CLI and future web write actions.
- Design validation that prevents duplicate task IDs across all epics.
- Define whether ID allocation should write audit events.

Out of Scope:
- Do not implement ids.py.
- Do not migrate existing task IDs.
- Do not change taskctl.py behavior in this design task.

Allowed Files:
- ai-system/project-control/control-plane-id-allocation.md
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only

Acceptance Criteria:
- The plan explicitly resolves cross-epic task ID collision risk.
- There is a clear future implementation path for ids.py or equivalent.
- Parallel execution risk is accounted for.
- No ID migration or code behavior change is performed in this design task.

Review Instructions:
- Verify that the design is compatible with existing legacy IDs, task aliases, and epic keys.
- Verify that protected project-control files were not manually edited.

Execution Rules:
- Do not edit AI_PROJECT/state/*.json manually.
- Do not edit AI_PROJECT/events/*.jsonl manually.
- Do not edit AI_PROJECT/generated/*.md manually unless explicitly instructed; prefer CLI render/build commands.
- Stay within Allowed Files and Scope.
- If task state must change, report the required taskctl command instead of editing state by hand.
- At the end, report changed files, checks run, result, and any unresolved risks.

Suggested lifecycle commands:
```bash
python scripts/taskctl.py task transition TASK-021 --to in_progress
python scripts/taskctl.py task transition TASK-021 --to in_review
python scripts/taskctl.py validate
```

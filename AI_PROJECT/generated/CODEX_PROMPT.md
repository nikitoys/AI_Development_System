[SYSTEM]

Active Role: Codex Executor
Active Stage: Task Execution
Active Document: AI_PROJECT/generated/CODEX_CURRENT.md
Expected Result: Task completed according to acceptance criteria

Repository: current repository
Task ID: TASK-014
Task Title: TIG-03 Add task uid ref local sequence and aliases
Task Status: in_review
Verification Mode: standard

Initiative: INIT-001 — AI Development System Evolution
Epic: EPIC-004 — Task Identity and Execution Graph

Context:
Extend task state with stable uid, human-readable ref, local sequence inside epic, and aliases for backward compatibility.

Scope:
- Add uid/ref/local_seq/aliases fields to task schema.
- Generate refs from epic key and local sequence.
- Preserve legacy TASK-XXX compatibility.
- Update validation and rendering.

Out of Scope:
- Do not implement dependency graph in this task.

Allowed Files:
- scripts/taskctl.py
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/CODEX_CURRENT.md via taskctl.py only
- AI_PROJECT/generated/CODEX_PROMPT.md via taskctl.py/codexctl.py only

Acceptance Criteria:
- Existing tasks can be migrated or read without losing history.
- New tasks receive readable refs.
- Legacy TASK-XXX references remain resolvable.

Execution Rules:
- Do not edit AI_PROJECT/state/*.json manually.
- Do not edit AI_PROJECT/events/*.jsonl manually.
- Do not edit AI_PROJECT/generated/*.md manually unless explicitly instructed; prefer CLI render/build commands.
- Stay within Allowed Files and Scope.
- If task state must change, report the required taskctl command instead of editing state by hand.
- At the end, report changed files, checks run, result, and any unresolved risks.

Suggested lifecycle commands:
```bash
python scripts/taskctl.py task transition TASK-014 --to in_progress
python scripts/taskctl.py task transition TASK-014 --to in_review
python scripts/taskctl.py validate
```

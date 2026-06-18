[SYSTEM]

Active Role: Codex Executor
Active Stage: Task Execution
Active Document: AI_PROJECT/generated/CODEX_CURRENT.md
Expected Result: Task completed according to acceptance criteria

Repository: current repository
Task ID: TASK-015
Task Title: TIG-04 Add task reference resolver
Task Status: in_review
Verification Mode: standard

Initiative: INIT-001 — AI Development System Evolution
Epic: EPIC-004 — Task Identity and Execution Graph

Context:
Allow taskctl and prompt generation to resolve tasks by new ref, uid, or legacy TASK-XXX alias.

Scope:
- Add a central task reference resolver.
- Use resolver in show, transition, approve, archive, current set, prompt build and list mutation commands.
- Reject ambiguous references.

Out of Scope:
- Do not add dependency scheduling in this task.

Allowed Files:
- scripts/taskctl.py
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/CODEX_CURRENT.md via taskctl.py only
- AI_PROJECT/generated/CODEX_PROMPT.md via taskctl.py/codexctl.py only

Acceptance Criteria:
- Existing CLI commands keep working with legacy TASK-XXX.
- New refs work where task_id was previously required.
- Ambiguous references produce a clear error.

Execution Rules:
- Do not edit AI_PROJECT/state/*.json manually.
- Do not edit AI_PROJECT/events/*.jsonl manually.
- Do not edit AI_PROJECT/generated/*.md manually unless explicitly instructed; prefer CLI render/build commands.
- Stay within Allowed Files and Scope.
- If task state must change, report the required taskctl command instead of editing state by hand.
- At the end, report changed files, checks run, result, and any unresolved risks.

Suggested lifecycle commands:
```bash
python scripts/taskctl.py task transition TASK-015 --to in_progress
python scripts/taskctl.py task transition TASK-015 --to in_review
python scripts/taskctl.py validate
```

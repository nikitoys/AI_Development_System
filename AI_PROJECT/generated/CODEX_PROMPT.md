[SYSTEM]

Active Role: Codex Executor
Active Stage: Task Execution
Active Document: AI_PROJECT/generated/CODEX_CURRENT.md
Expected Result: Task completed according to acceptance criteria

Repository: current repository
Task ID: TASK-017
Task Title: TIG-06 Add migration and generated output update
Task Status: planned
Verification Mode: standard

Initiative: INIT-001 — AI Development System Evolution
Epic: EPIC-004 — Task Identity and Execution Graph

Context:
Provide safe migration/backward compatibility for existing plan and task state and update generated outputs to display readable refs.

Scope:
- Add migration path for existing tasks and epics.
- Preserve auditability and legacy aliases.
- Update CODEX_TASKS.md, CODEX_CURRENT.md and CODEX_PROMPT.md rendering.
- Update validation and generated checks.

Out of Scope:
- Do not remove legacy TASK-XXX compatibility yet.

Allowed Files:
- Not specified. Do not edit files until allowed files are clarified.

Acceptance Criteria:
- Existing AI_PROJECT/state can be validated after migration.
- Generated files display readable refs and legacy IDs where useful.
- Prompt packages still contain enough identity data for Codex execution.
- Validation and generated checks pass.

Execution Rules:
- Do not edit AI_PROJECT/state/*.json manually.
- Do not edit AI_PROJECT/events/*.jsonl manually.
- Do not edit AI_PROJECT/generated/*.md manually unless explicitly instructed; prefer CLI render/build commands.
- Stay within Allowed Files and Scope.
- If task state must change, report the required taskctl command instead of editing state by hand.
- At the end, report changed files, checks run, result, and any unresolved risks.

Suggested lifecycle commands:
```bash
python scripts/taskctl.py task transition TASK-017 --to in_progress
python scripts/taskctl.py task transition TASK-017 --to in_review
python scripts/taskctl.py validate
```

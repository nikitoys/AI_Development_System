[SYSTEM]

Active Role: Codex Executor
Active Stage: Task Execution
Active Document: AI_PROJECT/generated/CODEX_CURRENT.md
Expected Result: Task completed according to acceptance criteria

Repository: current repository
Task ID: TASK-013
Task Title: TIG-02 Add epic keys to plan model
Task Status: planned
Verification Mode: standard

Initiative: INIT-001 — AI Development System Evolution
Epic: EPIC-004 — Task Identity and Execution Graph

Context:
Add stable short epic keys to the plan model so task refs can use readable prefixes such as TIG-01 or ACP-02.

Scope:
- Add epic.key support to plan schema.
- Validate epic.key uniqueness.
- Add --key support to epic creation if appropriate.
- Update plan rendering to show epic keys.
- Preserve compatibility with existing EPIC-XXX IDs.

Out of Scope:
- Do not migrate task refs in this task.

Allowed Files:
- Not specified. Do not edit files until allowed files are clarified.

Acceptance Criteria:
- Existing plan validation still passes.
- Existing epics without keys are handled safely or migrated according to the design.
- New epics can have unique keys.
- Duplicate keys are rejected.

Execution Rules:
- Do not edit AI_PROJECT/state/*.json manually.
- Do not edit AI_PROJECT/events/*.jsonl manually.
- Do not edit AI_PROJECT/generated/*.md manually unless explicitly instructed; prefer CLI render/build commands.
- Stay within Allowed Files and Scope.
- If task state must change, report the required taskctl command instead of editing state by hand.
- At the end, report changed files, checks run, result, and any unresolved risks.

Suggested lifecycle commands:
```bash
python scripts/taskctl.py task transition TASK-013 --to in_progress
python scripts/taskctl.py task transition TASK-013 --to in_review
python scripts/taskctl.py validate
```

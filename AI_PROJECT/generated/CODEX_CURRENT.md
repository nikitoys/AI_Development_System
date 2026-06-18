<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `109`

Task: `TASK-013` — **TIG-02 Add epic keys to plan model**
Epic: `EPIC-004`
Status: `in_review`
Verification: `standard`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Add stable short epic keys to the plan model so task refs can use readable prefixes such as TIG-01 or ACP-02.

## Scope

- Add epic.key support to plan schema.
- Validate epic.key uniqueness.
- Add --key support to epic creation if appropriate.
- Update plan rendering to show epic keys.
- Preserve compatibility with existing EPIC-XXX IDs.

## Out of Scope

- Do not migrate task refs in this task.

## Allowed Files

- scripts/planctl.py
- AI_PROJECT/state/plan.json via planctl.py only
- AI_PROJECT/events/plan-events.jsonl via planctl.py only
- AI_PROJECT/generated/CODEX_PLAN.md via planctl.py only
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/CODEX_CURRENT.md via taskctl.py only
- AI_PROJECT/generated/CODEX_PROMPT.md via taskctl.py/codexctl.py only

## Acceptance Criteria

- Existing plan validation still passes.
- Existing epics without keys are handled safely or migrated according to the design.
- New epics can have unique keys.
- Duplicate keys are rejected.

## Notes

- Logical label: TIG-02

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-013 --to in_progress
python scripts/taskctl.py task transition TASK-013 --to in_review
python scripts/taskctl.py task approve TASK-013 --notes "..."
python scripts/taskctl.py task transition TASK-013 --to done
python scripts/taskctl.py prompt build --write
```

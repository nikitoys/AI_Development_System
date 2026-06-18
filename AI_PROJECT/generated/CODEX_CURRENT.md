<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `147`

Task: `TASK-017` — **TIG-06 Add migration and generated output update**
Epic: `EPIC-004`
Status: `planned`
Verification: `standard`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Provide safe migration/backward compatibility for existing plan and task state and update generated outputs to display readable refs.

## Scope

- Add migration path for existing tasks and epics.
- Preserve auditability and legacy aliases.
- Update CODEX_TASKS.md, CODEX_CURRENT.md and CODEX_PROMPT.md rendering.
- Update validation and generated checks.

## Out of Scope

- Do not remove legacy TASK-XXX compatibility yet.

## Allowed Files

_No allowed files defined._

## Acceptance Criteria

- Existing AI_PROJECT/state can be validated after migration.
- Generated files display readable refs and legacy IDs where useful.
- Prompt packages still contain enough identity data for Codex execution.
- Validation and generated checks pass.

## Notes

- Logical label: TIG-06

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-017 --to in_progress
python scripts/taskctl.py task transition TASK-017 --to in_review
python scripts/taskctl.py task approve TASK-017 --notes "..."
python scripts/taskctl.py task transition TASK-017 --to done
python scripts/taskctl.py prompt build --write
```

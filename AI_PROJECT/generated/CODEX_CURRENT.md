<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `90`

Task: `TASK-012` — **TIG-01 Document task identity and execution graph design**
Epic: `EPIC-004`
Status: `in_review`
Verification: `standard`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Define the target model for task uid, human ref, legacy aliases, epic keys, dependency graph, executable queue, and migration rules before implementation.

## Scope

- Create or update a source design document for task identity and execution graph.
- Define uid/ref/legacy_id/aliases/local_seq semantics.
- Define human ref format <EPIC_KEY>-<LOCAL_SEQ>.
- Define ready vs executable.
- Define cross-epic depends_on behavior.
- Define migration/backward compatibility rules for existing TASK-XXX records.

## Out of Scope

- Do not implement schema migration.
- Do not change taskctl.py behavior yet except if required to create the task records.

## Allowed Files

- ai-system/project-control/09-task-identity-and-execution-graph.md
- ai-system/project-control/README.md if it exists and needs an index/reference update
- ai-system/README.md if it clearly maintains a project-control document index
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/CODEX_CURRENT.md via taskctl.py only
- AI_PROJECT/generated/CODEX_PROMPT.md via taskctl.py/codexctl.py only
- AI_PROJECT/state/docs.json via docctl.py only if the documentation registry is used
- AI_PROJECT/events/doc-events.jsonl via docctl.py only if the documentation registry is used
- AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only if the documentation registry is used
- AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only if the documentation registry is used

## Acceptance Criteria

- A clear source-of-truth design exists.
- The design states that task IDs do not imply execution order.
- The design states that epics may execute in parallel by default.
- The design defines explicit dependencies as the only cross-epic ordering mechanism.
- The design includes migration rules for existing TASK-XXX tasks.
- Generated project-control files are refreshed through CLI.

## Notes

- Logical label: TIG-01

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-012 --to in_progress
python scripts/taskctl.py task transition TASK-012 --to in_review
python scripts/taskctl.py task approve TASK-012 --notes "..."
python scripts/taskctl.py task transition TASK-012 --to done
python scripts/taskctl.py prompt build --write
```

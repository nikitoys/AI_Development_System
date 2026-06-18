<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `276`

Task: `CTL-12 (TASK-030)` — **Task L - Documentation and owner quickstart**
Epic: `EPIC-005`
Status: `in_review`
Verification: `standard`
Ref: `CTL-12`
UID: `tsk_235fab1d1516`
Legacy ID: `TASK-030`
Aliases: `TASK-030`
Epic Key / Local Seq: `CTL` / `12`

## Prompt Control Fields

Active Role: `Technical Writer AI / AI System Maintainer`
Active Stage: `Control Plane Documentation`
Active Document: `ai-system/project-control`
Expected Result: `Owner quickstart and control-plane documentation explain how to use and safely operate the new model.`

## Summary

Make the unified control-plane usable and discoverable.

## Description

Update or create owner-facing documentation for aictl usage, legacy wrapper relationship, project doctor, local web dashboard, web safety model, state/events/generated architecture, and ID allocation policy.

## Scope

- Document how to use aictl.
- Document how legacy ctl wrappers relate to aictl.
- Document how to run project doctor.
- Document how to run the local web dashboard.
- Document the Web UI safety model.
- Document state/events/generated architecture and ID allocation policy.
- Ensure Codex can be pointed to aictl as the preferred interface.

## Out of Scope

- Do not implement new control-plane behavior in documentation task.
- Do not mark documents active without Human Owner acceptance.
- Do not manually edit documentation-control protected files.

## Allowed Files

- ai-system/project-control/**
- README.md
- AGENTS.md
- AI_PROJECT/state/docs.json via docctl.py only
- AI_PROJECT/events/doc-events.jsonl via docctl.py only
- AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only
- AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only
- AI_PROJECT/generated/CONTEXT_PACK.md via contextctl.py/aictl.py only
- AI_PROJECT/generated/CONTEXT_STATUS.md via contextctl.py/aictl.py only
- AI_PROJECT/events/context-events.jsonl via contextctl.py/aictl.py only
- AI_PROJECT/state/context.json via contextctl.py/aictl.py only if the command updates it
- AI_PROJECT/generated/CODEX_PROMPT.md via codexctl.py/aictl.py/taskctl.py only
- AI_PROJECT/generated/CODEX_STATUS.md via codexctl.py/aictl.py only
- AI_PROJECT/events/codex-events.jsonl via codexctl.py/aictl.py only
- AI_PROJECT/state/current_execution.json via codexctl.py/aictl.py only if the command updates it

## Acceptance Criteria

- Owner can discover common commands quickly.
- Codex can be pointed to aictl as the preferred interface.
- Docs clearly say generated files are derived.
- Docs explain legacy ctl wrappers, project doctor, local web dashboard, web safety model, state/events/generated architecture, and ID allocation policy.

## Review Instructions

- Verify docs do not claim generated Markdown is source of truth.
- Verify documentation-control files are updated only through docctl.py.
- Verify Human Owner acceptance remains required before active/accepted states.

## Notes

- Phase 5 - Web write actions and docs.
- Documentation should be updated after implementation details are stable enough to describe.
- Human Owner approved refreshing context/Codex generated execution artifacts for CTL-12 closure only, through owning CLIs. No source behavior changes are allowed.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-030 --to in_progress
python scripts/taskctl.py task transition TASK-030 --to in_review
python scripts/taskctl.py task approve TASK-030 --notes "..."
python scripts/taskctl.py task transition TASK-030 --to done
python scripts/taskctl.py prompt build --write
```

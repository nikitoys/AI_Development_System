<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `16`

Task: `TASK-004` — **Implement codexctl prompt package generator**
Epic: `EPIC-001`
Status: `in_review`
Verification: `standard`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Implementation of approved Evolution Change`
Active Document: `AI_PROJECT/state/evolution.json / AI_PROJECT/generated/EVOLUTION.md`
Expected Result: `Commit-ready implementation of scripts/codexctl.py for CHG-001.`

## Summary

Implement approved CHG-001 by adding a dedicated Codex prompt package control CLI.

## Description

Add scripts/codexctl.py with status, build and clear commands for executable Tasks and Evolution Changes, using existing AI_PROJECT state, generated output and event conventions.

## Scope

- Implement scripts/codexctl.py with status, build --task, build --change and clear commands.
- Generate/update CODEX_PROMPT.md and CODEX_STATUS.md through codexctl.py behavior.
- Use existing task/evolution state schemas, generated prompt conventions and audit-style JSONL events.

## Out of Scope

- Do not implement multi-agent orchestration, SOP runner, autonomous execution, external API integration or CI.
- Do not modify unrelated AI system documents or product source code.

## Allowed Files

- scripts/codexctl.py
- AI_PROJECT/state/current_execution.json
- AI_PROJECT/generated/CODEX_PROMPT.md
- AI_PROJECT/generated/CODEX_STATUS.md
- AI_PROJECT/events/codex-events.jsonl

## Acceptance Criteria

- scripts/codexctl.py exists and uses only Python standard library.
- status works without crashing and reports READY or BLOCKED state with stable codes.
- build --task can generate CODEX_PROMPT.md for an executable task and fails clearly for invalid task IDs or statuses.
- build --change can generate CODEX_PROMPT.md for approved CHG-001 and fails clearly for invalid change IDs or statuses.
- clear invalidates or removes the current Codex prompt package without modifying source-of-truth task or evolution state.
- Required validation commands from the owner prompt pass or any blocker is reported clearly.

## Review Instructions

- Review for lifecycle boundary enforcement, prompt completeness, generated artifact consistency and standard-library-only implementation.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-004 --to in_progress
python scripts/taskctl.py task transition TASK-004 --to in_review
python scripts/taskctl.py task approve TASK-004 --notes "..."
python scripts/taskctl.py task transition TASK-004 --to done
python scripts/taskctl.py prompt build --write
```

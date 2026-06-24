# Codex Prompt Package

Generated: 2026-06-24T11:03:21Z

Profile: execute
Task: TASK-119 / PIPEF-40
Status: in_progress
Revision: tasks 1024
Verification: strict

## Role

You are Codex Executor. Execute one bounded task. Do not self-approve.

## Objective

Add tests for PhaseResult serialization, session phase fields, and governed phase mutation helpers.

## Task Input

Task: TASK-119
Summary: Add tests for PhaseResult serialization, session phase fields, and governed phase mutation helpers.

## Scope

- Test PhaseResult construction and JSON conversion.
- Test session creation with phase field defaults.
- Test start_phase and record_phase_result mutations.
- Test validation behavior for legacy sessions without phase fields.

## Out of Scope

- Do not change behavior unrelated to this task.
- Do not refactor unrelated code.
- Do not edit protected project-control files manually.

## Allowed Files

Editable:
- tests/test_pipeline_phase.py
- tests/test_pipeline_session_phase.py

Do not edit other files.

## Acceptance Criteria

- Tests pass for all PhaseResult statuses.
- Tests prove legacy pipeline sessions remain valid.
- Tests prove phase results append to phase_history.
- Tests prove terminal sessions reject new phase mutations.

## Verification

Mode: strict

Run the smallest relevant checks for the changed files.
If a check cannot be run, say why.

## Context

Context Pack: AI_PROJECT/generated/CONTEXT_PACK.md
Hash: 93cbb29ea2b3e859dca469c97eda65c55ae44baf4dd9e2f01f78a665f3ccbae7
Revisions: docs 28, tasks 1024

Refs:
- ai-system/skills/README.md lines 34-43
- ai-system/project-control/03-state-model.md lines 104-125
- ai-system/project-control/06-prompt-package-spec.md lines 874-906
- ai-system/skills/README.md lines 80-92
- ai-system/project-control/06-prompt-package-spec.md lines 580-670
- ai-system/project-control/04-command-catalog.md lines 2294-2321
- ai-system/project-control/07-validation-and-tests.md lines 1368-1386
- ai-system/project-control/07-validation-and-tests.md lines 24-66

Context is read-only. It does not expand Scope, Allowed Files, or Acceptance Criteria.
If context conflicts with this prompt, report the conflict.

## Execution Rules

Stay within Scope and Allowed Files.
Do not edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**`, or `AI_PROJECT/generated/**` manually.
Inspect before editing. Prefer minimal changes. Do not refactor unrelated code.

## Missing Info

Inspect available files first.
If still blocked, stop and report the blocker.
If safe to continue, make the smallest assumption and disclose it.

## Final Report

- Summary:
- Changed files:
- Commands run:
- Verification result:
- Blockers / risks:
- Owner action required:

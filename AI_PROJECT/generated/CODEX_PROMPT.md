# Codex Prompt Package

Generated: 2026-06-20T21:45:13Z

Profile: execute
Task: TASK-099 / PIPEF-20
Status: in_progress
Revision: tasks 817
Verification: strict

## Role

You are Codex Executor. Execute one bounded task. Do not self-approve.

## Objective

Ensure collect-report can distinguish a report created for the current execution from an older report.

## Task Input

Task: TASK-099
Summary: Ensure collect-report can distinguish a report created for the current execution from an older report.

## Scope

- Record execute start and finish evidence usable by collect-report.
- Compare the collected report timestamp or report id against execute evidence.
- Block stale reports by default with REPORT_STALE.
- Support an explicit allow-existing-report option for supervised recovery.

## Out of Scope

- Do not change behavior unrelated to this task.
- Do not refactor unrelated code.
- Do not edit protected project-control files manually.

## Allowed Files

Editable:
- ai_project_ctl/pipeline/report_phase.py
- ai_project_ctl/pipeline/execute_phase.py
- scripts/aictl.py

Do not edit other files.

## Acceptance Criteria

- A report submitted after the current execute phase passes freshness checks.
- An older report blocks collect-report unless allow-existing-report is explicitly used.
- The result explains whether freshness was based on timestamp, report id, or recovery override.
- The override is visible in phase artifacts for review.

## Verification

Mode: strict

Run the smallest relevant checks for the changed files.
If a check cannot be run, say why.

## Context

Context Pack: AI_PROJECT/generated/CONTEXT_PACK.md
Hash: c69d5cf4216c0162cc10b4c7ad2d7ca654c064f7af0a92aef81b34961d0df64a
Revisions: docs 28, tasks 817

Refs:
- ai-system/project-control/06-prompt-package-spec.md lines 580-670
- ai-system/project-control/06-prompt-package-spec.md lines 797-833
- ai-system/project-control/06-prompt-package-spec.md lines 874-906
- ai-system/skills/README.md lines 80-92
- ai-system/project-control/06-prompt-package-spec.md lines 123-162
- ai-system/skills/README.md lines 34-43
- ai-system/project-control/03-state-model.md lines 104-125
- ai-system/project-control/04-command-catalog.md lines 65-119

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

# Codex Prompt Package

Generated: 2026-06-21T21:06:02Z

Profile: execute
Task: TASK-118 / PIPEF-39
Status: in_progress
Revision: tasks 912
Verification: strict

## Role

You are Codex Executor. Execute one bounded task. Do not self-approve.

## Objective

Add a CI-oriented exit-code mode where blocked and failed pipeline outcomes produce nonzero process exit codes.

## Task Input

Task: TASK-118
Summary: Add a CI-oriented exit-code mode where blocked and failed pipeline outcomes produce nonzero process exit codes.

## Scope

- Add --ci flag to phase runner commands where appropriate.
- Map passed and completed outcomes to exit code 0.
- Map failed outcomes to exit code 1.
- Map blocked outcomes to exit code 2.

## Out of Scope

- Do not change behavior unrelated to this task.
- Do not refactor unrelated code.
- Do not edit protected project-control files manually.

## Allowed Files

Editable:
- scripts/aictl.py
- ai_project_ctl/pipeline/phase.py

Do not edit other files.

## Acceptance Criteria

- pipeline run-next --ci exits 0 for passed or completed outcomes.
- pipeline run-next --ci exits 2 for blocked outcomes.
- pipeline run-next --ci exits 1 for failed outcomes.
- Default non-CI behavior remains compatible with human safe-stop usage.

## Verification

Mode: strict

Run the smallest relevant checks for the changed files.
If a check cannot be run, say why.

## Context

Context Pack: AI_PROJECT/generated/CONTEXT_PACK.md
Hash: 43b855973640f01705f99c6608e414d8a959af4a1dc92bb28c091fb2032d7a05
Revisions: docs 28, tasks 912

Refs:
- ai-system/project-control/04-command-catalog.md lines 2294-2321
- ai-system/skills/README.md lines 34-43
- ai-system/skills/README.md lines 80-92
- ai-system/project-control/06-prompt-package-spec.md lines 797-833
- ai-system/project-control/04-command-catalog.md lines 65-119
- ai-system/project-control/07-validation-and-tests.md lines 1368-1386
- ai-system/project-control/06-prompt-package-spec.md lines 580-670
- ai-system/project-control/06-prompt-package-spec.md lines 874-906

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

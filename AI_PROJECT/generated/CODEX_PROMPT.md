# Codex Prompt Package

Generated: 2026-06-24T10:39:22Z

Profile: execute
Task: TASK-145 / PIPEF-66
Status: in_progress
Revision: tasks 1014
Verification: strict

## Role

You are Codex Executor. Execute one bounded task. Do not self-approve.

## Objective

Add a Web Control Center Settings page that displays effective UI settings and their source file.

## Task Input

Task: TASK-145
Summary: Add a Web Control Center Settings page that displays effective UI settings and their source file.

## Scope

- Add a Settings navigation item and route in the Web Control Center.
- Render effective UI settings including source, path and current values.
- Show settings in a human-readable form without requiring terminal commands.
- Add focused tests that the Settings page renders with default and project-file settings.

## Out of Scope

- Do not add settings mutation in this task.
- Do not change pipeline execution behavior.
- Do not expose non-UI project secrets or environment variables.

## Allowed Files

Editable:
- ai_project_ctl/web/server.py
- tests/test_web_control_center.py

Do not edit other files.

## Acceptance Criteria

- The Web Control Center navigation includes a Settings page link.
- The Settings page shows the effective UI settings source and path.
- The Settings page renders command_line, default_policy and timeout settings when present.
- The Settings page is read-only in this task.
- Existing Web Control Center tests continue to pass.

## Verification

Mode: strict

Run the smallest relevant checks for the changed files.
If a check cannot be run, say why.

## Context

Context Pack: AI_PROJECT/generated/CONTEXT_PACK.md
Hash: 934baacbfa4b9db21b174d0aa7838c60f9920aadf79b3d3bfb175204768e6351
Revisions: docs 28, tasks 1014

Refs:
- ai-system/project-control/03-state-model.md lines 104-125
- ai-system/project-control/04-command-catalog.md lines 65-119
- ai-system/project-control/04-command-catalog.md lines 21-64
- ai-system/project-control/06-prompt-package-spec.md lines 797-833
- ai-system/project-control/06-prompt-package-spec.md lines 874-906
- ai-system/skills/README.md lines 34-43
- ai-system/skills/README.md lines 80-92
- ai-system/project-control/06-prompt-package-spec.md lines 580-670

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

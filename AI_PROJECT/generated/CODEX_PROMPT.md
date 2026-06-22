# Codex Prompt Package

Generated: 2026-06-22T10:38:41Z

Profile: execute
Task: TASK-129 / PIPEF-50
Status: in_progress
Revision: tasks 942
Verification: strict

## Role

You are Codex Executor. Execute one bounded task. Do not self-approve.

## Objective

Add a Codex executable preflight that checks the configured command before launching an executable Run.

## Task Input

Task: TASK-129
Summary: Add a Codex executable preflight that checks the configured command before launching an executable Run.

## Scope

- Add a Codex preflight service that reads command_line from effective UI settings.
- Run a minimal prompt through the configured command.
- Detect sandbox-unavailable output such as bwrap or RTM_NEWADDR.
- Expose the preflight through aictl for UI and backend usage.

## Out of Scope

- Do not attempt to repair OS-level sandbox permissions.
- Do not change Codex CLI configuration files.
- Do not mutate task, pipeline, or report state during preflight.

## Allowed Files

Editable:
- ai_project_ctl/pipeline/codex_preflight.py
- ai_project_ctl/pipeline/codex_adapter.py
- ai_project_ctl/ui_settings.py
- scripts/aictl.py
- tests/pipeline/test_codex_preflight.py

Do not edit other files.

## Acceptance Criteria

- Preflight returns passed when the configured command exits successfully.
- Preflight returns a blocked result when bwrap, RTM_NEWADDR, user namespace, or Operation not permitted appears in output.
- Preflight uses the effective command_line setting.
- Preflight does not write project-control state or generated files.
- UI Run can use the preflight result to block executable execution before starting a session.

## Verification

Mode: strict

Run the smallest relevant checks for the changed files.
If a check cannot be run, say why.

## Context

Context Pack: AI_PROJECT/generated/CONTEXT_PACK.md
Hash: 5c53aafdbe0b65418ba39a4629dfa5e457acea2b97537711272f60b5c5b750f2
Revisions: docs 28, tasks 942

Refs:
- ai-system/project-control/06-prompt-package-spec.md lines 797-833
- ai-system/skills/README.md lines 80-92
- ai-system/project-control/04-command-catalog.md lines 65-119
- ai-system/project-control/04-command-catalog.md lines 21-64
- ai-system/skills/README.md lines 34-43
- ai-system/project-control/06-prompt-package-spec.md lines 874-906
- ai-system/project-control/06-prompt-package-spec.md lines 580-670
- ai-system/project-control/04-command-catalog.md lines 2294-2321

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

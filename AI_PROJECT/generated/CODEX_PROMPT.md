# Codex Prompt Package

Generated: 2026-06-20T15:53:42Z

Profile: execute
Task: TASK-079
Status: in_review
Revision: tasks 669
Verification: standard

## Role

You are Codex Executor. Execute one bounded task. Do not self-approve.

## Objective

Render CODEX_PROMPT.md as a compact execute-profile contract instead of embedding full Context Pack content.

## Task Input

Task: TASK-079
Summary: Render CODEX_PROMPT.md as a compact execute-profile contract instead of embedding full Context Pack content.

## Scope

- Modify scripts/codexctl.py prompt rendering.
- Render Profile: execute as the MVP default; do not implement --profile.
- Use existing task fields only for identity, role, objective, scope, out-of-scope, allowed files, acceptance criteria, and verification mode.
- Render Objective from task.summary with fallback to task.title.
- Render full task.scope and full task.acceptance_criteria without category splitting.
- Omit Execution Steps because task.execution_steps is not part of the current task schema.
- Render Verification mode plus compact default check instruction.
- Render Context as manifest-only when Context Pack is attached, keeping path, hash, docs revision, tasks revision, and selected source refs.
- Do not embed the full AI_PROJECT/generated/CONTEXT_PACK.md body into CODEX_PROMPT.md.
- Keep compact Execution Rules, Missing Info policy, and Final Report format.
- Add or update tests proving compact context rendering.

## Out of Scope

- Do not implement --profile.
- Do not add profile-specific role switching.
- Do not change task schema.
- Do not add execution_steps or verification_checks.
- Do not implement task splitting.
- Do not modify contextctl.py.
- Do not manually edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.

## Allowed Files

Editable:
- scripts/codexctl.py
- tests/test_legacy_ctl_wrappers.py

Do not edit other files.

## Acceptance Criteria

- codexctl.py build --task <TASK> still works without Context Pack.
- codexctl.py build --task <TASK> --with-context produces a compact Context section.
- Generated CODEX_PROMPT.md does not embed the full CONTEXT_PACK.md body.
- Generated CODEX_PROMPT.md includes Context Pack path, hash, docs revision, tasks revision, and selected source refs when context is attached.
- Execution Steps section is omitted for current tasks because task.execution_steps does not exist.
- Verification renders mode plus compact default check instruction.
- Existing wrapper tests still pass.
- Add or update tests to prove compact context rendering.
- Generated CODEX_PROMPT.md omits the legacy full retrieved-context body section.

## Verification

Mode: standard

Run the smallest relevant checks for the changed files.
If a check cannot be run, say why.

## Context

Context Pack: AI_PROJECT/generated/CONTEXT_PACK.md
Hash: 0bdf28caa824796aa71c7dde9aa60cb7352367db459677700ad4a4098f125c80
Revisions: docs 28, tasks 669

Refs:
- ai-system/project-control/06-prompt-package-spec.md lines 580-670
- ai-system/project-control/06-prompt-package-spec.md lines 797-833
- ai-system/project-control/04-command-catalog.md lines 65-119
- ai-system/project-control/06-prompt-package-spec.md lines 874-906
- ai-system/skills/README.md lines 34-43
- ai-system/project-control/03-state-model.md lines 104-125
- ai-system/project-control/06-prompt-package-spec.md lines 123-162
- ai-system/skills/README.md lines 80-92

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

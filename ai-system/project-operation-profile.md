# Project Operation Profile

Status: Draft
Version: v0.1.0

## Purpose

This document defines `PROJECT_OPERATION_PROFILE.md`, a surface-level project behavior profile for repositories that use AI_Development_System.

The profile gives the Human Owner one easy place to adjust how AI roles and Codex should work in a concrete project without editing deeper system documents or asking Codex to rewrite templates.

## Governed Entity

A Project Operation Profile is a project-local control file that records operational defaults for AI-assisted work.

Default foldered path:

```text
AI_PROJECT/PROJECT_OPERATION_PROFILE.md
```

The profile is not a product requirements document, architecture document, backlog or implementation task. It describes how AI Dev System should behave while working with the project.

## What Belongs in the Profile

The profile may record surface-level project preferences such as:

- Human Owner language and answer style;
- prompt language preference;
- default verification mode and budget;
- runtime tracking preference;
- slow, browser, visual, full and release check policy;
- permissions for application code, `AI_PROJECT`, `AI_Development_System`, installs, commits, pushes and pull requests;
- target app directory and read-only paths;
- default review and QA expectations;
- local exceptions or temporary project-level preferences.

Detailed product requirements, technical design, backlog tasks, current task state and session history should stay in their specialized project control files.

## Language Rule

Stable field names should remain in English so AI sessions and future tooling can read the profile predictably.

Field values may use the Human Owner's language.

Example:

```text
Human Owner Language: Russian
Answer Detail Level: Коротко, но с важными деталями
Default Verification Mode: FAST
Can Commit: Только по явной просьбе
```

Mode names, paths, booleans, command names and Human Owner decision keywords should remain stable:

```text
FAST
STANDARD
true / false
APPROVED / REWORK / REJECTED
AI_PROJECT/
app/
```

## Authority and Precedence

For a concrete project, authority is resolved in this order:

1. Explicit Human Owner instruction for the current task.
2. Current approved task, prompt package or decision record.
3. `AI_PROJECT/PROJECT_OPERATION_PROFILE.md`.
4. Specialized `AI_PROJECT` control files, such as `PROJECT_GOAL.md`, `CODEX_CURRENT.md`, `CODEX_TASKS.md`, `CODEX_WORKFLOW.md` and `docs/verification-policy.md`.
5. Root `AGENTS.md` boundary rules.
6. Global AI Development System rules in `AI_Development_System/ai-system`.
7. Templates used only as bootstrap starting points.

The profile provides defaults. It does not authorize execution without an approved task or prompt package.

## Safety Boundary

The profile may restrict or specialize global defaults.

The profile must not weaken:

- Human Owner approval rules;
- lifecycle governance;
- security or privacy rules;
- forbidden actions from global AI Development System rules;
- task scope and allowed-files boundaries.

If the profile conflicts with global safety rules, AI/Codex must report the conflict and stop before execution.

If the profile conflicts with a specialized local control file, AI/Codex should report project-control drift and identify which file should be synchronized.

## Verification Boundary

Verification defaults in the profile do not override the selected task mode.

Browser, visual, slow, full, release and golden-scenario checks remain explicit opt-in unless both the profile and the current approved task allow them.

If a stronger verification mode is recommended, AI/Codex should report the recommendation instead of silently upgrading the mode.

## Update Rules

Human Owner may edit the profile directly.

AI or Codex may update the profile only when the task explicitly targets project control files, project operation preferences, bootstrap, system update or controlled system evolution.

Project system updates must merge profile changes carefully and must not overwrite local profile values blindly.

## Minimal Profile Shape

Recommended sections:

```text
Human Interaction
Verification Defaults
Permissions
Project Layout
Review Defaults
Local Exceptions
```

Projects may add local sections, but local additions must not weaken global safety or approval rules.

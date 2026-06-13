# Project System Update

Status: Draft
Version: v0.1.0

## Purpose

This document defines how to update an existing project that already uses AI_Development_System.

A project system update refreshes the local AI control layer and embedded AI system without changing application code.

## Governed Entity

A project system update is a controlled migration of project AI control files and embedded AI system files.

It applies to projects that already contain one or both of:

```text
AI_Development_System/
AI_PROJECT/
```

or legacy root-level control files such as:

```text
AGENTS.md
CODEX_WORKFLOW.md
CODEX_TASKS.md
```

## Source of Truth

Default source documents:

- `AI_Development_System/ai-system/foldered-integration.md`;
- `AI_Development_System/ai-system/project-control-files.md`;
- `AI_Development_System/ai-system/project-bootstrap.md`;
- `AI_Development_System/ai-system/verification-modes.md`;
- `AI_Development_System/ai-system/templates/foldered/`;
- project-local `AI_PROJECT/` files;
- root `AGENTS.md`.

## When to Run

Run a project system update when:

- upstream AI_Development_System changed;
- a project needs the new foldered architecture;
- local control files are missing;
- verification rules, owner plan intake or operator commands changed;
- project control files drifted or became inconsistent.

Do not use project system update for ordinary product implementation.

## Update Modes

### Embedded System Refresh

Refreshes only:

```text
AI_Development_System/
```

It must not modify:

```text
AI_PROJECT/
<target-app-directory>/
```

### Local Control Layer Migration

Updates only:

```text
AGENTS.md
AI_PROJECT/
```

It must merge changes and preserve project-specific decisions.

### Legacy Root Control Migration

Moves or copies old root-level control files into:

```text
AI_PROJECT/
```

It should preserve root `AGENTS.md` as a thin router.

## Required Process

```text
1. Read root AGENTS.md.
2. Read AI_PROJECT/AGENTS.md if present.
3. Read AI_PROJECT/PROJECT_OPERATION_PROFILE.md if present.
4. Read AI_PROJECT/PROJECT_GOAL.md and AI_PROJECT/docs/verification-policy.md.
5. Read AI_Development_System/ai-system/foldered-integration.md.
6. Read latest templates under AI_Development_System/ai-system/templates/foldered/.
7. Compare existing local control files with templates.
8. Prepare migration report.
9. Stop for Human Owner approval when conflicts or replacements are needed.
10. Apply approved control-layer changes only.
11. Update AI_PROJECT/AI_DEV_SYSTEM_VERSION.md.
12. Run FAST checks only.
```

## Minimal Update Helper

AI_Development_System includes a small Foldered Control Mode update helper:

```bash
python3 scripts/foldered-control-mvp.py update --project-root /path/to/project
```

Dry-run is the default. The helper reports:

- required foldered control files that exist or are missing;
- unresolved template placeholders in existing control files;
- the pending `AI_PROJECT/AI_DEV_SYSTEM_VERSION.md` update.

To refresh `AI_PROJECT/AI_DEV_SYSTEM_VERSION.md` explicitly:

```bash
python3 scripts/foldered-control-mvp.py update \
  --project-root /path/to/project \
  --project-name "My Project" \
  --target-app-directory app \
  --update-method vendor-copy \
  --apply
```

The helper does not update `AI_Development_System/`, run git subtree/submodule operations, merge local project decisions or modify application code. Conflicts and local control-file migrations still require Human Owner review.

## Merge Rules

Do not blindly overwrite local project files.

Preserve:

- project mission;
- target app directory;
- non-goals;
- owner plan;
- current tasks;
- task history;
- local verification restrictions;
- project-specific prompts;
- known constraints.

Add or update:

- missing foldered architecture references;
- `AI_DEV_SYSTEM_VERSION.md`;
- missing `OWNER_PLAN.md`;
- missing verification mode policy;
- new operator commands;
- new browser/visual QA boundaries;
- new read order and path conventions.

## Conflict Handling

Report a conflict when:

- local rules allow browser or visual checks by default;
- local rules conflict with global safety rules;
- target app directory is missing or ambiguous;
- root control files and `AI_PROJECT/` files disagree;
- existing project files would need replacement rather than merge;
- application code would need changes.

Conflicts require Human Owner decision.

## Forbidden Actions

Project system update must not:

- modify application code;
- refactor product directories;
- run browser automation;
- run Playwright or MCP browser sessions;
- capture screenshots;
- inspect browser console;
- run full builds or full test suites unless explicitly approved;
- delete project-local decisions or history;
- overwrite `PROJECT_OPERATION_PROFILE.md`, `OWNER_PLAN.md`, `PROJECT_GOAL.md`, `CODEX_TASKS.md` or `CODEX_SESSION_LOG.md` without explicit approval.

## Verification Mode

Default:

```text
FAST
```

Allowed checks for this process:

```bash
git diff --check
git status --short
```

No browser, Playwright, screenshots or visual QA unless the Human Owner explicitly requests them.

## Migration Report Format

```text
Status:
Current AI System Version:
Target AI System Version:
Detected Integration Mode:
Target Integration Mode:
Target App Directory:
Already Compatible:
Missing Files:
Files to Update:
Preserved Local Rules:
Conflicts:
Application Code Modified: yes/no
Checks:
Next Human Owner Decision:
```

## Closure Rules

A project system update can close when:

- local control files match the approved architecture;
- missing required files are added or explicitly deferred;
- conflicts are resolved or recorded;
- `AI_PROJECT/AI_DEV_SYSTEM_VERSION.md` is updated when present;
- application code was not modified;
- checks are recorded.

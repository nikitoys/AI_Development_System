# Project Bootstrap

Status: Draft
Version: v0.1.0

## Purpose

This document defines how to initialize a concrete project repository so it can be managed through the AI Development System.

Bootstrap creates local project control files, records the target application directory, sets the default verification mode and stops for Human Owner approval before implementation begins.

## Governed Entity

A project bootstrap is a controlled initialization flow that adds or adapts project-level control files in a concrete repository.

Bootstrap is not application implementation. It must not rewrite application code or product behavior unless the Human Owner explicitly approves a separate implementation task.

## Source of Truth

Default source-of-truth documents for bootstrap are:

- `/ai-system/project-control-files.md`;
- `/ai-system/verification-modes.md`;
- `/ai-system/templates/project/`;
- `/ai-system/rules.md`;
- `/ai-system/prompt-lifecycle.md`;
- project-specific Human Owner instructions.

## When to Bootstrap

Bootstrap is appropriate when:

- starting a new project repository;
- adopting AI_Development_System in an existing repository;
- recovering a repository that lacks durable AI/Codex state files;
- standardizing project workflow before Codex implementation work starts.

Bootstrap should not be used to sneak application changes into a documentation or process task.

## Questions for the Human Owner

Before creating project control files, ask or infer only what is necessary:

1. Project name.
2. Human Owner language.
3. Target app directory, or whether the repository root is the application root.
4. Project mission and non-goals.
5. Default verification mode.
6. Whether to create `OWNER_PLAN.md` immediately or leave it as an empty owner-input placeholder.
7. Whether the repository is empty or already contains application code.
7. Whether local rules should be stricter than the global system defaults.

If the Human Owner has already provided these answers, do not ask again.

## Bootstrap for Empty Repositories

For an empty or new repository:

1. Create required project control files.
2. Fill templates with project name, target app directory, language and default verification mode.
3. Record the first planning state in `CODEX_PLAN.md`.
4. Set `CODEX_CURRENT.md` to `status: idle` unless a task is explicitly approved.
5. Initialize `OWNER_PLAN.md` as an owner-input roadmap placeholder unless the Human Owner opts out.
6. Initialize `CODEX_TASKS.md` with a small backlog or `No tasks approved yet`.
7. Initialize `CODEX_SESSION_LOG.md` with a bootstrap entry.
7. Stop and ask the Human Owner to approve the initialized control layer.

## Bootstrap for Existing Repositories

For an existing repository with application code:

1. Inspect the repository structure only enough to identify the target app directory and existing control files.
2. Do not rewrite, reformat, move or refactor application code.
3. Create missing control files or propose updates to stale ones.
4. Preserve existing project-specific instructions unless they conflict with system safety rules.
5. Record target app directory explicitly in `PROJECT_GOAL.md`.
6. Record default verification mode in `docs/verification-policy.md`.
7. Stop before any app implementation work.

## Files to Create

Default bootstrap creates:

```text
AGENTS.md
PROJECT_GOAL.md
CODEX_COMMANDS.md
CODEX_WORKFLOW.md
OWNER_PLAN.md
CODEX_PLAN.md
CODEX_CURRENT.md
CODEX_TASKS.md
CODEX_SESSION_LOG.md
PROMPTS.md
docs/verification-policy.md
```

## Default Verification Mode

Default verification mode should normally be:

```text
CODE_ONLY_FAST
```

A stronger default may be selected only when the Human Owner explicitly asks for it or the project context requires it.

Bootstrap must not silently select `BROWSER_SMOKE` or `VISUAL_QA` as the default.

## Approval Stop Points

Bootstrap must stop for Human Owner approval when:

- required project facts are missing;
- target app directory is ambiguous;
- existing local instructions conflict with global system rules;
- bootstrap would modify application files;
- verification mode stronger than `CODE_ONLY_FAST` is proposed by the AI;
- existing control files would be replaced rather than minimally updated.

## Result Format

A bootstrap result should report:

```text
Status:
Created Files:
Updated Files:
Target App Directory:
Default Verification Mode:
Application Code Modified: yes/no
Open Questions:
Next Required Human Owner Decision:
```

## Boundary Rules

Bootstrap may create or update project control files.

Bootstrap must not modify application code without explicit approval.

Bootstrap must not start implementation immediately after creating control files.

Bootstrap must not treat `OWNER_PLAN.md` as executable scope. Owner plan items must first be converted into approved task records with scope, allowed files, verification mode and acceptance criteria.

Bootstrap must not mark a project ready for Codex execution until the Human Owner approves the local control layer or approves a specific task.

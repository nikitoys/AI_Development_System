# Project Integration Model

Status: Draft
Version: v0.1.0

## Purpose

This document defines how AI_Development_System is embedded into concrete project repositories.

The goal is to keep the reusable AI Development System, local project control files and application code clearly separated so projects can be installed, updated and operated safely.

## Recommended Model

The recommended integration model is `Foldered Control Mode`.

```text
/project-root
├── AGENTS.md
├── AI_Development_System/
├── AI_PROJECT/
└── <target-app-directory>/
```

## Directory Responsibilities

## `/AI_Development_System`

Reusable upstream AI Development System copy.

Contains global rules, lifecycle governance, templates, verification modes, prompt lifecycle and process documentation.

This directory may be updated from the upstream AI_Development_System repository.

Do not store project-specific backlog, current task state, owner plan or local product goals here.

## `/AI_PROJECT`

Local project control layer.

Contains project-specific control files copied or adapted from AI_Development_System templates.

Default files:

```text
AI_PROJECT/AGENTS.md
AI_PROJECT/PROJECT_GOAL.md
AI_PROJECT/OWNER_PLAN.md
AI_PROJECT/CODEX_COMMANDS.md
AI_PROJECT/CODEX_WORKFLOW.md
AI_PROJECT/CODEX_PLAN.md
AI_PROJECT/CODEX_CURRENT.md
AI_PROJECT/CODEX_TASKS.md
AI_PROJECT/CODEX_SESSION_LOG.md
AI_PROJECT/PROMPTS.md
AI_PROJECT/AGENT_PLAN.md
AI_PROJECT/AGENT_TASKS.md
AI_PROJECT/AGENT_ASSIGNMENTS.md
AI_PROJECT/AGENT_LOCKS.md
AI_PROJECT/AGENT_RESULTS.md
AI_PROJECT/AGENT_METRICS.md
AI_PROJECT/AI_DEV_SYSTEM_VERSION.md
AI_PROJECT/docs/verification-policy.md
```

`AI_PROJECT` files are project-specific source of truth after bootstrap. They must not be blindly overwritten by upstream templates.

Agent planning and assignment files are optional planning and manual coordination records for SOP-guided and multi-agent workflows. They do not authorize execution, parallel execution, automatic execution, automatic dispatch, merge or acceptance.

## Root `AGENTS.md`

Small project bootstrap and router file.

It should point AI sessions to:

```text
/AI_PROJECT/AGENTS.md
/AI_PROJECT/PROJECT_GOAL.md
/AI_PROJECT/docs/verification-policy.md
/AI_Development_System/AGENTS.md
/AI_Development_System/ai-system/rules.md
```

The root `AGENTS.md` should also record the target app directory and boundary rules.

## `<target-app-directory>`

Application or product code.

Examples:

```text
.
app
apps/web
frontend
backend
voxel-adventure-mvp
```

The target app directory must be recorded in `AI_PROJECT/PROJECT_GOAL.md` and root `AGENTS.md`.

## Authority and Precedence

For a concrete project in Foldered Control Mode:

1. Explicit Human Owner instruction for the current task.
2. Current approved task or prompt package.
3. `AI_PROJECT` local control files.
4. `AI_PROJECT/docs/verification-policy.md`.
5. Root `AGENTS.md` boundary rules.
6. `AI_Development_System/ai-system` global system rules.
7. `AI_Development_System/ai-system/templates` templates.

Templates are bootstrap inputs, not ongoing authority after local files are created.

## Installation Methods

### Vendor Copy

Simple install for most projects:

```bash
git clone --depth 1 --branch ai-development-system https://github.com/nikitoys/AI_Development_System.git AI_Development_System
rm -rf AI_Development_System/.git
mkdir -p AI_PROJECT
cp -R AI_Development_System/ai-system/templates/foldered/AI_PROJECT/. AI_PROJECT/
cp AI_Development_System/ai-system/templates/foldered/AGENTS.root.md AGENTS.md
```

### Git Subtree

Recommended when the project wants a Git-managed upstream copy without submodule friction:

```bash
git subtree add \
  --prefix=AI_Development_System \
  https://github.com/nikitoys/AI_Development_System.git \
  ai-development-system \
  --squash
mkdir -p AI_PROJECT
cp -R AI_Development_System/ai-system/templates/foldered/AI_PROJECT/. AI_PROJECT/
cp AI_Development_System/ai-system/templates/foldered/AGENTS.root.md AGENTS.md
```

Update later with:

```bash
git subtree pull \
  --prefix=AI_Development_System \
  https://github.com/nikitoys/AI_Development_System.git \
  ai-development-system \
  --squash
```

### Git Submodule

Allowed but not preferred:

```bash
git submodule add -b ai-development-system https://github.com/nikitoys/AI_Development_System.git AI_Development_System
```

Submodules require initialization and may confuse AI/Codex sessions if not checked out.

## Root Control Mode

Root Control Mode remains supported for small or legacy projects.

In Root Control Mode, project control files live directly in the repository root:

```text
AGENTS.md
PROJECT_GOAL.md
OWNER_PLAN.md
CODEX_WORKFLOW.md
CODEX_TASKS.md
```

Foldered Control Mode is preferred when projects need easier system updates, clearer boundaries or less root clutter.

## Update Rule

Updating `/AI_Development_System` is not the same as updating `/AI_PROJECT`.

- `/AI_Development_System` may be replaced, pulled or subtree-updated from upstream.
- `/AI_PROJECT` must be migrated by merge, not overwritten.
- Application code must not be modified during system updates.

Use `/ai-system/project-system-update.md` for the controlled update process.

Use `scripts/agent-plan-mvp.py` only as a dry-run reporting helper for `AI_PROJECT/AGENT_*` files. It must not execute Codex, create branches or worktrees, merge changes, accept results or modify application code.

## Boundary Rules

Do not modify `/AI_Development_System` during ordinary product implementation.

Do not modify application code during AI system bootstrap or update.

Do not treat `AI_PROJECT/OWNER_PLAN.md` as executable scope.

Do not allow local project rules to weaken global approval, safety or lifecycle governance rules.

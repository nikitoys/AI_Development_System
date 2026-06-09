# Foldered Project Integration

Status: Draft
Version: v0.1.0

## Purpose

This document defines the recommended foldered architecture for integrating AI_Development_System into concrete project repositories.

Foldered integration keeps three concerns separate:

```text
AI_Development_System   # upstream AI development operating system
AI_PROJECT              # project-local control layer and state
target app directory    # application, game, service or product code
```

This model is recommended for projects that will be updated over time, because the upstream system can be refreshed without overwriting project-local goals, plans, tasks and decisions.

## Recommended Repository Layout

```text
/project-root
├── AGENTS.md
├── AI_Development_System/
├── AI_PROJECT/
└── <target-app-directory>/
```

Example:

```text
cartoon-voxel-adventure/
├── AGENTS.md
├── AI_Development_System/
├── AI_PROJECT/
└── voxel-adventure-mvp/
```

## Directory Responsibilities

| Path | Purpose | Update Model |
|---|---|---|
| `AGENTS.md` | Thin root bootstrap/router for AI sessions. | Project-specific; edited carefully. |
| `AI_Development_System/` | Embedded upstream AI Development System. | Updated from upstream. Do not edit casually. |
| `AI_PROJECT/` | Local control files, owner plan, task state, prompts and verification policy. | Project-specific source of truth. Merge updates, do not overwrite. |
| `<target-app-directory>/` | Application/game/service code. | Modified only through approved implementation tasks. |

## Root AGENTS.md

The root `AGENTS.md` should be short. It should route AI/Codex sessions to the correct folders and declare boundaries.

It should identify:

- where the embedded AI Development System lives;
- where project-local control files live;
- where application code lives;
- which files to read first;
- that application code must not be modified during bootstrap or system update;
- that `AI_Development_System/` must not be modified unless the task explicitly targets AI system evolution or synchronization.

## AI_Development_System Directory

`AI_Development_System/` is the embedded upstream system. It may be installed by:

- vendor copy from a temporary clone;
- git subtree;
- git submodule, only when the project team accepts submodule complexity.

Recommended default:

```bash
git subtree add \
  --prefix=AI_Development_System \
  https://github.com/nikitoys/AI_Development_System.git \
  ai-development-system \
  --squash
```

Simpler vendor-copy alternative:

```bash
git clone --depth 1 --branch ai-development-system https://github.com/nikitoys/AI_Development_System.git AI_Development_System
rm -rf AI_Development_System/.git
```

## AI_PROJECT Directory

`AI_PROJECT/` stores local project control files. These files are project-specific source of truth after bootstrap.

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

Agent planning and assignment files are project-local planning, manual coordination and review records only. They preserve sequential execution as the default, keep candidate parallel groups informational until approved and do not authorize automatic execution, automatic dispatch, merge or acceptance.

## Installation Flow

For a new or existing project:

```text
1. Add or copy AI_Development_System/ into the project.
2. Create AI_PROJECT/ from AI_Development_System/ai-system/templates/foldered/AI_PROJECT/.
3. Copy AI_Development_System/ai-system/templates/foldered/AGENTS.root.md to /AGENTS.md.
4. Fill placeholders.
5. Record target app directory.
6. Set default verification mode, usually CODE_ONLY_FAST.
7. Stop for Human Owner approval.
```

The minimal helper can prepare this as a dry-run:

```bash
python3 scripts/foldered-control-mvp.py bootstrap --project-root /path/to/project
```

Use `--apply` only after reviewing the planned control-layer changes.

## Update Flow

Do not overwrite `AI_PROJECT/` during upstream system update.

Update flow:

```text
1. Update AI_Development_System/ from upstream.
2. Compare AI_PROJECT/ with new templates and standards.
3. Add missing local control files.
4. Merge new rules into existing local files.
5. Preserve local project decisions and constraints.
6. Record conflicts.
7. Update AI_PROJECT/AI_DEV_SYSTEM_VERSION.md.
8. Stop for Human Owner approval.
```

The minimal update helper can report missing files, unresolved placeholders and pending version tracking:

```bash
python3 scripts/foldered-control-mvp.py update --project-root /path/to/project
```

See `/ai-system/project-system-update.md`.

The minimal agent planning helper can validate project-local agent planning files in dry-run mode:

```bash
python3 scripts/agent-plan-mvp.py validate --project-root /path/to/project
python3 scripts/agent-plan-mvp.py check-locks --project-root /path/to/project
python3 scripts/agent-plan-mvp.py list-parallel-groups --project-root /path/to/project
python3 scripts/agent-plan-mvp.py generate-prompts --project-root /path/to/project
```

This helper only reports planning state and prompt drafts. It does not execute Codex, create branches or worktrees, merge changes, accept results or modify application code.

## Authority Order

For a foldered project, authority is resolved in this order:

1. Explicit Human Owner instruction for the current task.
2. Current approved task or prompt package.
3. `AI_PROJECT/` local control files.
4. `AI_PROJECT/docs/verification-policy.md`.
5. Root `AGENTS.md` routing and boundary rules.
6. `AI_Development_System/ai-system/` global rules.
7. Templates.

Local project rules may restrict or specialize global defaults, but they must not weaken safety, approval or lifecycle governance rules.

## Boundary Rules

Foldered integration must not be used to bypass Human Owner approval.

Updating `AI_Development_System/` must not rewrite `AI_PROJECT/`.

Updating `AI_PROJECT/` must not modify application code.

Application code must not be modified during bootstrap or system update unless the Human Owner explicitly approves a separate implementation task.

Codex must not treat `OWNER_PLAN.md` as executable scope. Owner plan items must first be converted into approved tasks with scope, allowed files, verification mode and acceptance criteria.

Codex must not treat `AGENT_PLAN.md`, `AGENT_TASKS.md`, `AGENT_ASSIGNMENTS.md`, `AGENT_LOCKS.md`, `AGENT_RESULTS.md` or `AGENT_METRICS.md` as execution authority. Agent planning and assignment records must first be converted into approved bounded task or prompt packages.

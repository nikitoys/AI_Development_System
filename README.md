# AI Development System

Languages: [English](README.md) | [Русский](README.ru.md)

Status: Draft
Version: v0.3.0

This repository contains an AI Development System: an operating model for developing projects through AI roles, documentation, lifecycle governance, prompt generation, Codex execution, review and controlled evolution.

It is not a normal application repository. The primary source of truth is `/ai-system`.

## At a Glance

This repository describes a documented AI-assisted development system:

```text
Human Owner sets direction and approves decisions.
ChatGPT Orchestrator routes work, prepares prompts and reviews results.
AI Roles specialize by responsibility.
Codex Executor changes repository files only inside approved scope.
Documentation stores rules, decisions, lifecycles and history.
```

## How Work Moves

```text
Idea
-> Clarification
-> Task or change proposal
-> Prompt package
-> Human approval
-> Codex execution
-> Review
-> QA
-> Human acceptance
-> Documentation update
-> Done
```

## Where to Start

- `/ai-system/README.md` - main AI Development System index.
- `/ai-system/owner-guide.md` - how the Human Owner works with the system.
- `/ai-system/operating-model.md` - what is implemented and how the system is organized.
- `/ai-system/system-schemes.md` - compact text schemes for roles, documents and process flow.

## Quick Start

### Install into a Project

Use the project templates as the starting control layer for a concrete project:

```text
/ai-system/templates/project/
```

A project should have these local control files:

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

During project bootstrap, fill project-specific placeholders such as:

```text
{{PROJECT_NAME}}
{{TARGET_APP_DIRECTORY}}
{{DEFAULT_VERIFICATION_MODE}}
{{HUMAN_OWNER_LANGUAGE}}
```

For an existing repository, bootstrap must create or adapt control files only. It must not rewrite, refactor or move application code unless the Human Owner explicitly approves a separate implementation task.

### Update an Existing Project

Do not re-run bootstrap blindly for a project that already has local control files.

Use a controlled project system update:

```text
read local control files
-> compare with the current AI_Development_System standard and templates
-> add missing files
-> merge new rules into existing files
-> preserve local project rules
-> report conflicts
-> update the local system version record when present
-> stop for Human Owner approval
```

Templates are not authority after bootstrap. Local project control files are the project source of truth, unless they conflict with global safety, approval or lifecycle rules.

Project system updates must not modify application code.

### Use Day to Day

Recommended operator loop:

```text
1. Write goals, roadmap or desired work in OWNER_PLAN.md.
2. Run: Разобрать план
3. Review proposed work in CODEX_PLAN.md and CODEX_TASKS.md.
4. Approve one task: Утверждаю задачу N
5. Execute one task: Выполняй
6. Review the result.
7. Continue with the next task only after approval.
```

`OWNER_PLAN.md` is planning input, not executable scope. Codex must not implement items from it until they are converted into approved tasks with scope, allowed files, verification mode and acceptance criteria.

### Verification Modes

Default for ordinary code-only work:

```text
CODE_ONLY_FAST
```

Operator shortcuts:

```text
Код быстро          -> CODE_ONLY_FAST
Проверка быстро     -> FAST_VALIDATION
Браузер проверить   -> BROWSER_SMOKE
Визуально проверить -> VISUAL_QA
```

Browser automation, Playwright/MCP browser sessions, screenshots, browser console checks and manual visual QA are on-demand only. Do not run them unless the Human Owner explicitly requests them or the current task acceptance criteria require them.

## Purpose

The system helps the Human Owner work with ChatGPT and Codex through clear roles, modes, prompts, review rules and change governance.

Core idea:

```text
Human Owner controls.
ChatGPT Orchestrator routes.
AI roles specialize.
Codex executes scoped repository changes.
Documentation records decisions.
```

## Current Capabilities

- Interaction modes: Free, System, Prompt, Codex, Review, Evolution and Dry Run.
- Role model for product, design, management, implementation, quality, documentation and system evolution.
- Project control file standard and bootstrap workflow for concrete repositories.
- Owner plan intake through `OWNER_PLAN.md` and `Разобрать план`.
- Explicit verification modes for fast code work, standard validation, browser smoke checks and visual QA.
- Codex prompt package format with scope, allowed files, forbidden actions, verification mode and acceptance criteria.
- Review process with severity levels and Human Owner decision keywords.
- Lifecycle governance for managed system entities.
- Language and localization policy for user-facing answers and generated prompts.
- Controlled system evolution through improvement log, AICP and changelog.

## Main Documents

- `/ai-system/README.md` - AI Development System index.
- `/ai-system/owner-guide.md` - how the Human Owner should interact with the system.
- `/ai-system/interaction-modes.md` - supported modes and routing rules.
- `/ai-system/operating-model.md` - implemented, partial and missing system areas.
- `/ai-system/system-structure.md` - high-level role and layer structure.
- `/ai-system/roles.md` - AI role registry.
- `/ai-system/rules.md` - global system rules.
- `/ai-system/prompt-lifecycle.md` - prompt creation, review and execution lifecycle.
- `/ai-system/task-format.md` - standard task format.
- `/ai-system/review-process.md` - review and QA process.
- `/ai-system/change-process.md` - controlled evolution process.
- `/ai-system/lifecycle-governance.md` - shared lifecycle rules.
- `/ai-system/project-control-files.md` - standard local control files for concrete projects.
- `/ai-system/project-bootstrap.md` - how to initialize empty and existing project repositories.
- `/ai-system/verification-modes.md` - explicit verification modes and browser/visual QA boundaries.
- `/ai-system/language-policy.md` - language and localization rules.
- `/ai-system/system-changelog.md` - system version history.
- `/ai-system/improvement-log.md` - observed process problems and improvement ideas.

## Interaction Modes

Use explicit markers when precision matters:

```text
[FREE]       ordinary explanation or discussion
[SYSTEM]     process through AI Development System
[PROMPT]     generate a prompt artifact for review
[CODEX]      prepare a Codex-ready prompt package
[REVIEW]     review Codex output
[EVOLUTION]  analyze or change the AI Development System
[DRY-RUN]    simulate without applying
```

If no marker is provided, ChatGPT Orchestrator infers the mode from the request.

Repository-affecting work must use the AI Development System process and should identify:

```text
Active Role:
Active Stage:
Active Document:
Expected Result:
```

## Language Policy

Human-facing answers should use the Human Owner language by default.

System documents and control structures remain English by default:

- mode markers such as `[SYSTEM]` and `[CODEX]`;
- prompt fields such as `Scope`, `Out of Scope` and `Acceptance Criteria`;
- decision keywords such as `APPROVED`, `REWORK`, `REJECTED`, `DEFERRED` and `EXPERIMENT`;
- file paths, task IDs, branch names and command names.

Generated Codex prompts should usually be English or hybrid: stable English structure with localized explanations when useful.

## Standard Workflow

```text
Human intent
-> ChatGPT Orchestrator classifies mode
-> active role and source documents are selected
-> prompt, task, review or system change is prepared
-> Human Owner approves or requests rework
-> Codex applies approved repository changes when needed
-> result is reviewed
-> changelog or documentation is updated when required
```

## Human Owner Decisions

Use these decision words:

```text
APPROVED   accept result
REWORK     request changes
REJECTED   reject result
DEFERRED   postpone decision
EXPERIMENT test temporarily
```

AI may recommend a decision, but the Human Owner decides.

## Repository Model

```text
/ai-system   # AI Development System rules, roles, workflow and governance
/docs        # product documentation when a product project exists
README.md    # repository entrypoint in English
README.ru.md # Russian repository entrypoint
AGENTS.md    # instructions for future AI sessions
```

Legacy operator-loop files may exist, but `/ai-system` is the current primary source of truth.

## Minimal Safety Rules

- Do not change repository files unless the Human Owner explicitly asks for a repository change or Codex execution task.
- Do not treat AI Development System evolution as ordinary conversation.
- Do not generate Codex prompts without mode markers and execution boundaries.
- Do not accept Codex output automatically without review.
- Do not mix unrelated system, product, implementation and documentation changes unless explicitly approved.
- Do not run browser automation, Playwright/MCP, screenshots, browser console checks or manual visual QA unless explicitly requested or required by acceptance criteria.

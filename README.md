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
- Codex prompt package format with scope, allowed files, forbidden actions and acceptance criteria.
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

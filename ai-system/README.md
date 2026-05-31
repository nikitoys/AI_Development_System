# AI Development System

Status: Draft  
Version: v0.1.0

## Purpose

`/ai-system` describes how this repository is developed through an AI-assisted development process.

This folder does not describe the product itself. It describes the development mechanism: roles, rules, workflow, human interaction, task format, review process and controlled evolution of the system.

## Core Principle

Documentation is the source of truth.

AI roles do not work from inspiration. They work from approved documents, explicit tasks and defined acceptance criteria.

## System Layers

```text
AI Development System
├── Human Owner
├── ChatGPT Orchestrator
├── Codex Executor
├── AI Roles
├── Documentation
├── Workflow
├── Rules
├── Review Process
└── Evolution Process
```

## Repository Model

```text
/project
  /ai-system   # rules, roles, prompts, workflow, evolution of the AI system
  /docs        # product documentation: vision, PRD, architecture, backlog, API, UX
  /backend     # backend implementation
  /frontend    # frontend implementation
  /infra       # deployment and infrastructure
  README.md
```

## Files

- `glossary.md` — all terms used by the system.
- `system-prompt.md` — main controlling prompt for the AI Development System.
- `roles.md` — AI roles and their responsibilities.
- `human-interaction.md` — how the human works with ChatGPT and Codex.
- `language-policy.md` — language and localization rules for responses, prompts and documentation.
- `workflow.md` — development stages and gates.
- `rules.md` — global rules and restrictions.
- `task-format.md` — standard task format for Codex and AI roles.
- `decision-process.md` — decision statuses and ownership.
- `decision-lifecycle.md` — lifecycle rules for Human Owner decisions.
- `review-process.md` — review and QA rules.
- `qa-lifecycle.md` — lifecycle rules for QA work and regression checks.
- `change-process.md` — controlled evolution of the AI Development System.
- `change-lifecycle.md` — lifecycle rules for managed system changes.
- `document-lifecycle.md` — lifecycle rules for source-of-truth documents.
- `process-lifecycle.md` — lifecycle rules for managed processes.
- `task-lifecycle.md` — lifecycle rules for managed tasks.
- `codex-lifecycle.md` — lifecycle rules for Codex execution.
- `aicp-language-policy.md` — approved change proposal for language and localization policy.
- `document-templates.md` — templates for project documents.
- `system-changelog.md` — history of changes to the AI Development System.
- `improvement-log.md` — observations and problems in the system.

## Operating Model

```text
Human Owner sets direction
ChatGPT Orchestrator prepares documents, prompts and reviews
Codex Executor changes repository files
Documentation records decisions
AI Development System controls the process
```

## Minimal Rule

No implementation task should start without:

- a task from the backlog;
- required source documents;
- clear scope and out of scope;
- acceptance criteria;
- expected output;
- review step.

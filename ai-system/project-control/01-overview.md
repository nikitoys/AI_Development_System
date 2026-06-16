# Project Control Gateway Overview

## Status

Draft

## Purpose

Project Control Gateway defines a strict command-controlled layer for managing project state in AI Development System.

The goal is to prevent project management from being performed through manual Markdown edits or free-form AI reasoning. Instead, AI agents must interact with project state only through explicit Python CLI commands.

Core principle:

```text
AI does not edit project control state directly.
AI selects an allowed command.
Python validates the command.
Python updates machine state.
Python writes an audit event.
Python renders human-readable Markdown.
Human Owner keeps final authority.
```

## Problem

AI-assisted development becomes unstable when project state is scattered across Markdown files and updated by free-form model behavior.

Typical risks:

* plan documents drift out of sync;
* task status is changed without lifecycle validation;
* Codex edits generated or control files manually;
* audit history is missing;
* owner approval boundaries become unclear;
* project decisions are hidden inside chat context instead of persistent state.

Project Control Gateway solves this by introducing a narrow, deterministic command interface.

## Self-Hosted Use In This Repository

AI_Development_System now uses root-level `/AI_PROJECT` as its own self-hosted Project Control Layer.

In this repository:

```text
/AI_PROJECT/state/**      machine-readable current state
/AI_PROJECT/events/**     append-only audit history
/AI_PROJECT/generated/**  generated readable output
```

The source documents for AI Development System behavior remain under `/ai-system`. Root `/AI_PROJECT` records controlled project state for this repository's own evolution and generated context for Human Owner, ChatGPT Orchestrator and Codex Executor.

This self-hosted layer is distinct from:

```text
/ai-system/templates/**/AI_PROJECT      reusable templates for external projects
/examples/golden-project/AI_PROJECT     non-runtime reference example
```

## Core Idea

The project is managed as structured state, not as manually edited text.

The state is split into three layers:

```text
AI_PROJECT/state/*.json      — machine-readable current state
AI_PROJECT/events/*.jsonl    — append-only audit history
AI_PROJECT/generated/*.md    — human-readable generated output
```

Only `state/*.json` represents the current source of truth.

`events/*.jsonl` records how the project reached the current state.

`generated/*.md` is derived output for Human Owner, ChatGPT Orchestrator and Codex Executor. Generated files may be read, but must not be edited manually.

## Control Boundary

Project control files are protected.

Protected areas:

```text
AI_PROJECT/state/**
AI_PROJECT/events/**
AI_PROJECT/generated/**
```

AI agents must not modify these files directly.

Allowed mutation path:

```bash
python scripts/projectctl.py <domain> <command>
```

Current repository gateways are domain-specific:

```bash
python scripts/planctl.py <command>
python scripts/taskctl.py <command>
python scripts/docctl.py <command>
python scripts/evolutionctl.py <command>
```

Manual edits to protected files are considered a project control bypass.

## First Managed Domain: Plan

The first implementation domain is project plan control.

The first controlled state file is:

```text
AI_PROJECT/state/plan.json
```

`plan.json` stores the upper-level project plan:

```text
Project
Idea
Goal
Strategy
Initiative[]
Epic[]
```

Tasks are intentionally excluded from `plan.json`.

A Task is an executable unit of work and must later be managed by a separate task control layer:

```text
AI_PROJECT/state/tasks.json
AI_PROJECT/events/task-events.jsonl
AI_PROJECT/generated/CODEX_TASKS.md
AI_PROJECT/generated/CODEX_CURRENT.md
```

## Planning Hierarchy

The target planning hierarchy is:

```text
Goal / Idea
└── Initiative
    └── Epic
        └── Task
```

Meaning:

* Initiative is a strategic planning container.
* Epic is a delivery planning container.
* Task is the smallest executable unit.
* Codex may execute only approved Tasks.
* Initiative and Epic must never be treated as executable scope.

## First CLI Scope

The first CLI script is:

```text
scripts/planctl.py
```

It manages only the upper-level plan:

```text
idea
goal
strategy
initiative
epic
```

Example commands:

```bash
python scripts/planctl.py init
python scripts/planctl.py show
python scripts/planctl.py validate
python scripts/planctl.py render
python scripts/planctl.py audit

python scripts/planctl.py idea set --text "..."
python scripts/planctl.py goal set --text "..."
python scripts/planctl.py strategy set-summary --text "..."

python scripts/planctl.py initiative create --title "..."
python scripts/planctl.py initiative status INIT-001 --to active

python scripts/planctl.py epic create --initiative INIT-001 --title "..."
python scripts/planctl.py epic status EPIC-001 --to active
```

## Mutation Flow

Every mutation command must follow the same sequence:

```text
1. Read current state.
2. Validate current state.
3. Check command preconditions.
4. Apply the allowed mutation.
5. Increase revision.
6. Save updated state.
7. Append audit event.
8. Render generated Markdown.
9. Validate final state.
```

If any step fails, the command must stop and return an explicit error.

## Audit Requirement

Every successful mutation must append one event to an audit log.

For plan control:

```text
AI_PROJECT/events/plan-events.jsonl
```

Each event should record:

```text
event_id
timestamp
actor
command
entity_type
entity_id
revision_before
revision_after
payload
```

Audit events must be append-only.

They must not be manually edited, reordered or deleted.

## Generated Output

Generated Markdown exists for readability only.

For plan control:

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

This file is derived from:

```text
AI_PROJECT/state/plan.json
```

Generated files must include a warning header:

```text
GENERATED FILE. DO NOT EDIT MANUALLY.
```

If generated output becomes outdated, it must be regenerated through the CLI.

## AI Behavior Rule

When operating inside Project Control Gateway, Codex is not a free-form project manager.

Codex may reason only to:

```text
- understand Human Owner intent;
- map intent to an allowed command;
- request missing required arguments;
- execute the command;
- report the result.
```

Codex must not:

```text
- edit protected files manually;
- invent new lifecycle states;
- invent new commands;
- bypass Python validation;
- create ad-hoc scripts to mutate state;
- mark work approved or done without an allowed command;
- treat generated Markdown as source of truth.
```

If no allowed command exists, Codex must stop and report:

```text
NO_ALLOWED_COMMAND
requested_intent: ...
closest_existing_command: ...
missing_capability: ...
required_system_evolution: ...
```

## Human Owner Authority

Human Owner remains the final authority for:

```text
- project goal;
- strategy;
- approval of executable work;
- acceptance of completed work;
- changes to project control rules;
- changes to lifecycle policy;
- changes to command catalog.
```

AI may propose changes, but must not silently evolve the control model.

## MVP Non-Goals

The first Project Control Gateway MVP does not include:

```text
- UI;
- MCP server;
- Codex plugin;
- automatic multi-agent execution;
- automatic merge;
- automatic task acceptance;
- automatic deployment;
- full task lifecycle;
- review lifecycle;
- QA lifecycle;
- decision lifecycle.
```

These may be added later as separate controlled domains.

## Success Criteria

The initial Project Control Gateway is successful when:

```text
- plan.json can be initialized through CLI;
- idea, goal, strategy, initiative and epic can be managed through CLI;
- invalid state transitions are rejected;
- every mutation writes an audit event;
- CODEX_PLAN.md is generated from plan.json;
- protected files are not edited manually;
- Codex can be instructed to use only the CLI for plan changes.
```

## Long-Term Direction

Project Control Gateway should gradually expand from plan control into a full project control kernel:

```text
plan control
task control
current task control
prompt package builder
execution control
review control
QA control
decision control
change control
release control
```

The long-term target is:

```text
LLM selects allowed commands.
Python controls project state.
Generated documents provide readable views.
Audit logs preserve history.
Human Owner makes final decisions.
```

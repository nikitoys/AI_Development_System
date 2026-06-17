# Project Control State Model

## Status

Draft

## Purpose

This document defines how Project Control Gateway stores and manages project state.

The goal is to separate machine-readable state, audit history and human-readable output so that AI agents cannot freely mutate project management documents.

Project state must be controlled through explicit CLI commands, validated by Python and rendered into Markdown for human and AI reading.

## Core Model

Project Control Gateway uses three storage layers:

```text id="udezqd"
AI_PROJECT/state/*.json      — machine-readable current state
AI_PROJECT/events/*.jsonl    — append-only audit history
AI_PROJECT/generated/*.md    — human-readable generated output
```

Meaning:

```text id="7d36zj"
state     = what is currently true
events    = how the state changed over time
generated = how state is presented to humans and AI agents
```

## Source of Truth

For the first MVP:

```text id="lx45e3"
AI_PROJECT/state/*.json is the canonical source of truth.
AI_PROJECT/events/*.jsonl is the append-only audit log.
AI_PROJECT/generated/*.md is derived output.
```

The MVP does not use full event sourcing.

Events are used for audit and traceability, not as the primary state reconstruction mechanism.

A future version may add:

```bash id="9rcw67"
python scripts/projectctl.py state rebuild-from-events
```

But this is out of scope for the first implementation.

## Self-Hosted State In AI_Development_System

This repository now dogfoods the state model through root-level `/AI_PROJECT`.

The self-hosted layer stores:

```text id="self-hosted-layout"
/AI_PROJECT/state/**      current machine state for this repository's project control
/AI_PROJECT/events/**     append-only audit events for project-control mutations
/AI_PROJECT/generated/**  generated readable views and prompt/status outputs
```

Generated Markdown is readable output only. If generated output drifts, rebuild it through the owning CLI. Do not edit it by hand.

The root self-hosted state is distinct from reusable templates under `/ai-system/templates/**/AI_PROJECT` and the non-runtime golden example under `/examples/golden-project/AI_PROJECT`.

## Documentation Control State

Documentation control uses the same state/events/generated model:

```text
AI_PROJECT/state/docs.json
AI_PROJECT/events/doc-events.jsonl
AI_PROJECT/generated/DOCS_INDEX.md
AI_PROJECT/generated/DOCS_GAPS.md
```

`docs.json` is the authoritative registry for managed documentation. Each registered document stores lifecycle metadata plus derived retrieval metadata:

```text
path
title
type
status
required
owner
content_hash
last_reviewed_at
last_reviewed_by
last_reviewed_content_hash
declared_status
declared_status_raw
declared_status_source
```

`content_hash` is the current SHA-256 hash recorded by `docctl.py`. `last_reviewed_content_hash` is the SHA-256 hash reviewed by `docctl.py doc mark-reviewed`. Declared status fields are derived from document frontmatter, `Status:` metadata lines or a `## Status` section when present.

`DOCS_GAPS.md` is generated from `docs.json` and current source files. It groups actionable gaps such as missing files, status mismatch, stale reviews, unresolved placeholders, broken local links and stale content hash metadata.

---

# 1. Directory Layout

## MVP Layout

The first Project Control Gateway MVP uses this structure:

```text id="3iq7tv"
AI_PROJECT/
├── state/
│   └── plan.json
│
├── events/
│   └── plan-events.jsonl
│
└── generated/
    └── CODEX_PLAN.md
```

## Future Layout

Later controlled domains should expand the structure:

```text id="i8urev"
AI_PROJECT/
├── state/
│   ├── plan.json
│   ├── tasks.json
│   ├── current.json
│   ├── prompts.json
│   ├── executions.json
│   ├── reviews.json
│   ├── qa.json
│   ├── decisions.json
│   ├── changes.json
│   └── releases.json
│
├── events/
│   ├── plan-events.jsonl
│   ├── task-events.jsonl
│   ├── current-events.jsonl
│   ├── prompt-events.jsonl
│   ├── execution-events.jsonl
│   ├── review-events.jsonl
│   ├── qa-events.jsonl
│   ├── decision-events.jsonl
│   ├── change-events.jsonl
│   └── release-events.jsonl
│
└── generated/
    ├── CODEX_PLAN.md
    ├── CODEX_TASKS.md
    ├── CODEX_CURRENT.md
    ├── PROMPT_PACKAGE.md
    ├── REVIEW_STATUS.md
    ├── QA_STATUS.md
    ├── DECISION_LOG.md
    ├── CHANGE_LOG.md
    └── PROJECT_DASHBOARD.md
```

---

# 2. State Layer

## Definition

`state/*.json` contains the current machine-readable state of the project.

State files answer the question:

```text id="z2dts4"
What is true right now?
```

## Rules

State files must be:

```text id="2ql5zz"
- valid JSON;
- deterministic in structure;
- schema-validatable;
- updated only through CLI commands;
- protected from manual AI edits;
- rendered into Markdown when needed.
```

## Forbidden

AI agents must not:

```text id="pm0rvk"
- edit state files manually;
- use sed, echo, jq, python -c or ad-hoc scripts to mutate state;
- bypass the official CLI;
- invent fields not defined by the state model;
- silently change lifecycle statuses;
- silently change parent-child relationships.
```

## Allowed Mutation Path

All state changes must go through:

```bash id="jm565m"
python scripts/projectctl.py <domain> <command>
```

For the first MVP:

```bash id="drvf2l"
python scripts/planctl.py <command>
```

## MVP State File

The first state file is:

```text id="45on7a"
AI_PROJECT/state/plan.json
```

It stores:

```text id="hhbnst"
Project
Idea
Goal
Strategy
Initiative[]
Epic[]
```

It does not store Tasks.

Tasks are executable units and must be managed by a separate future state file:

```text id="00s4wb"
AI_PROJECT/state/tasks.json
```

---

# 3. plan.json

## Purpose

`plan.json` stores the upper-level project plan.

It defines where the project is going and how planning containers are organized.

## Example

```json id="dbx9q6"
{
  "schema_version": 1,
  "revision": 0,
  "project": {
    "id": "PROJECT-001",
    "name": "AI Development System",
    "status": "active",
    "created_at": "2026-06-15T12:00:00Z",
    "updated_at": "2026-06-15T12:00:00Z"
  },
  "idea": {
    "text": "Create a controlled AI-assisted development system.",
    "updated_at": "2026-06-15T12:00:00Z"
  },
  "goal": {
    "text": "Build a Project Control Gateway for AI Development System.",
    "success_criteria": [
      "Project state is changed only through CLI.",
      "Every mutation writes an audit event.",
      "Codex receives generated prompt packages."
    ],
    "updated_at": "2026-06-15T12:00:00Z"
  },
  "strategy": {
    "summary": "Implement CLI core first, then add Codex skill/plugin integration.",
    "principles": [
      "Human Owner keeps final authority.",
      "Python validates project state.",
      "Codex does not edit protected files manually."
    ],
    "constraints": [
      "No UI in MVP.",
      "No automatic merge.",
      "No automatic owner acceptance."
    ],
    "updated_at": "2026-06-15T12:00:00Z"
  },
  "initiatives": [],
  "epics": []
}
```

## Required Top-Level Fields

```text id="b5l9i3"
schema_version
revision
project
idea
goal
strategy
initiatives
epics
```

## Revision

`revision` is an integer that increases after every successful mutation.

Example:

```text id="im5f9j"
revision 0 -> init
revision 1 -> idea.set
revision 2 -> initiative.create
revision 3 -> epic.create
```

Revision is used to:

```text id="8xfl80"
- track state changes;
- connect state mutations with audit events;
- detect stale generated output;
- provide simple project state versioning.
```

---

# 4. Entity Storage Rules

## Project

Stored in:

```text id="z91lqe"
plan.project
```

Example:

```json id="9q84ip"
{
  "id": "PROJECT-001",
  "name": "AI Development System",
  "status": "active",
  "created_at": "...",
  "updated_at": "..."
}
```

## Idea

Stored in:

```text id="xwjc3x"
plan.idea
```

Example:

```json id="9gmti8"
{
  "text": "Create a controlled AI-assisted development system.",
  "updated_at": "..."
}
```

## Goal

Stored in:

```text id="xpt91u"
plan.goal
```

Example:

```json id="fn5r50"
{
  "text": "Build a Project Control Gateway.",
  "success_criteria": [],
  "updated_at": "..."
}
```

## Strategy

Stored in:

```text id="5hbkss"
plan.strategy
```

Example:

```json id="b8xazo"
{
  "summary": "Build CLI first, then Codex plugin integration.",
  "principles": [],
  "constraints": [],
  "updated_at": "..."
}
```

## Initiative

Stored in:

```text id="ufjltr"
plan.initiatives[]
```

Example:

```json id="041tmw"
{
  "id": "INIT-001",
  "title": "Project Control Gateway",
  "status": "active",
  "summary": "Create a Python-controlled project state management layer.",
  "priority": 1,
  "order": 1,
  "created_at": "...",
  "updated_at": "..."
}
```

## Epic

Stored in:

```text id="a8za68"
plan.epics[]
```

Example:

```json id="hnt6re"
{
  "id": "EPIC-001",
  "initiative_id": "INIT-001",
  "title": "Plan Control CLI",
  "status": "planned",
  "summary": "Manage project plan through Python CLI.",
  "priority": 1,
  "order": 1,
  "created_at": "...",
  "updated_at": "..."
}
```

---

# 5. Parent Reference Rules

Child entities must reference parent entities by ID.

## Epic Parent Rule

```text id="hrb8fk"
Epic.initiative_id -> Initiative.id
```

An Epic is invalid if:

```text id="yag8gw"
- initiative_id is missing;
- referenced Initiative does not exist;
- referenced Initiative is archived and Epic is active/planned/proposed/blocked.
```

## Future Task Parent Rule

Future Task control must use:

```text id="pyac43"
Task.epic_id -> Epic.id
```

A Task must not be approved if its parent Epic is archived.

---

# 6. Events Layer

## Definition

`events/*.jsonl` contains append-only audit history.

Events answer the question:

```text id="k0uerd"
How did the project reach the current state?
```

## JSONL Format

Each line is one JSON object.

Example:

```jsonl id="7vjhuk"
{"event_id":"EVT-000001","timestamp":"2026-06-15T12:00:00Z","actor":"human_owner","command":"plan.init","entity_type":"plan","entity_id":"PROJECT-001","revision_before":null,"revision_after":0,"payload":{"project_name":"AI Development System"}}
{"event_id":"EVT-000002","timestamp":"2026-06-15T12:05:00Z","actor":"human_owner","command":"initiative.create","entity_type":"initiative","entity_id":"INIT-001","revision_before":0,"revision_after":1,"payload":{"title":"Project Control Gateway"}}
```

## MVP Event File

For plan control:

```text id="bivuhz"
AI_PROJECT/events/plan-events.jsonl
```

## Required Event Fields

Each event must include:

```text id="1hqhr2"
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

## Field Meaning

| Field             | Meaning                        |
| ----------------- | ------------------------------ |
| `event_id`        | Unique event identifier        |
| `timestamp`       | UTC timestamp                  |
| `actor`           | Who performed the command      |
| `command`         | CLI command/action name        |
| `entity_type`     | Type of changed entity         |
| `entity_id`       | ID of changed entity           |
| `revision_before` | State revision before mutation |
| `revision_after`  | State revision after mutation  |
| `payload`         | Command-specific details       |

## Append-Only Rule

Events must be append-only.

AI agents and humans must not:

```text id="q70eco"
- edit past event lines;
- reorder event lines;
- delete event lines;
- rewrite audit history;
- hide failed or inconvenient history.
```

If an incorrect event is discovered, a new corrective event should be appended instead of editing history.

## Failed Commands

The MVP may omit failed command events.

A future version may record failed attempts in a separate file:

```text id="40n9s2"
AI_PROJECT/events/command-failures.jsonl
```

This is out of scope for the first plan control MVP.

---

# 7. Generated Layer

## Definition

`generated/*.md` contains human-readable output derived from state.

Generated files answer the question:

```text id="jjdfrc"
How should humans and AI agents read the current state?
```

Generated files are not source of truth.

## MVP Generated File

For plan control:

```text id="qjde2a"
AI_PROJECT/generated/CODEX_PLAN.md
```

This file is rendered from:

```text id="vwkxjt"
AI_PROJECT/state/plan.json
```

## Required Header

Every generated file must start with a warning header:

```text id="62r87v"
<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/plan.json -->
```

## Rules

Generated files may be:

```text id="z42c8i"
- read by Human Owner;
- read by ChatGPT Orchestrator;
- read by Codex Executor;
- deleted and regenerated;
- used as a short view of project state.
```

Generated files must not be:

```text id="h36wpw"
- manually edited;
- treated as canonical state;
- used to bypass JSON validation;
- used to change lifecycle status;
- used to add hidden scope.
```

## Regeneration

Generated output must be created through CLI:

```bash id="52g8g7"
python scripts/planctl.py render
```

Future unified command:

```bash id="j2qnxb"
python scripts/projectctl.py render all
```

---

# 8. Protected Files Policy

## Protected Areas

The following files and directories are protected:

```text id="j3hyh9"
AI_PROJECT/state/**
AI_PROJECT/events/**
AI_PROJECT/generated/**
```

## Mutation Rule

Protected files may only be changed by official Project Control Gateway commands.

For MVP:

```bash id="qycwdq"
python scripts/planctl.py ...
```

Future:

```bash id="kjbke0"
python scripts/projectctl.py ...
```

## Manual Edit Policy

Manual edits to protected files are considered a control bypass.

If manual edits are detected, the system should report:

```text id="2d80d8"
PROJECT_CONTROL_BYPASS_DETECTED
```

## Future Enforcement

Future enforcement may include:

```text id="z0njz1"
- pre-commit hook;
- CI check;
- protected-file diff check;
- generated-file freshness check;
- command audit verification;
- Codex plugin hook.
```

---

# 9. Mutation Transaction Model

Every successful mutation must follow a predictable transaction sequence.

## Transaction Steps

```text id="2l5av9"
1. Load current state.
2. Validate current state.
3. Parse command arguments.
4. Check command preconditions.
5. Apply mutation in memory.
6. Increase revision.
7. Validate new state.
8. Atomically write state file.
9. Append audit event.
10. Render generated Markdown.
11. Report result.
```

## Failure Rule

If any validation or precondition fails:

```text id="ewm21y"
- state must not be changed;
- audit event must not claim success;
- generated files must not be updated from invalid state;
- command must return an explicit error.
```

## Atomic Write Rule

State files should be written atomically:

```text id="3cpm77"
write temp file
fsync temp file
replace target file
```

This reduces the risk of corrupted JSON if the command is interrupted.

---

# 10. Validation Model

## Validation Scope

Validation must check:

```text id="5o5lyx"
- JSON syntax;
- required top-level fields;
- schema_version;
- revision type;
- valid statuses;
- unique IDs;
- valid parent references;
- allowed status transitions;
- archived parent restrictions;
- generated output freshness where applicable.
```

## MVP Validation Command

```bash id="87sly4"
python scripts/planctl.py validate
```

## Future Validation Command

```bash id="atkw7p"
python scripts/projectctl.py validate all
```

## Validation Failure

Validation failure must be explicit.

Example:

```text id="puq8bu"
VALIDATION_FAILED:
- duplicate initiative id: INIT-001
- epics[0].initiative_id references missing initiative: INIT-999
```

---

# 11. State Change Examples

## Example: Create Initiative

Command:

```bash id="8ofuml"
python scripts/planctl.py initiative create --title "Project Control Gateway"
```

Expected result:

```text id="twqnx3"
AI_PROJECT/state/plan.json is updated.
AI_PROJECT/events/plan-events.jsonl receives one event.
AI_PROJECT/generated/CODEX_PLAN.md is regenerated.
revision increases by 1.
```

## Example Event

```jsonl id="m8qz4n"
{"event_id":"EVT-000010","timestamp":"2026-06-15T12:20:00Z","actor":"human_owner","command":"initiative.create","entity_type":"initiative","entity_id":"INIT-001","revision_before":1,"revision_after":2,"payload":{"title":"Project Control Gateway","status":"active"}}
```

## Example: Create Epic

Command:

```bash id="q9sgtk"
python scripts/planctl.py epic create --initiative INIT-001 --title "Plan Control CLI"
```

Expected checks:

```text id="uj81s1"
- INIT-001 exists;
- INIT-001 is not archived;
- title is not empty;
- generated EPIC ID is unique.
```

Expected result:

```text id="d3ir9t"
EPIC-001 is added to plan.epics[].
revision increases by 1.
one audit event is appended.
CODEX_PLAN.md is regenerated.
```

## Example: Invalid Epic Parent

Command:

```bash id="8yyn34"
python scripts/planctl.py epic create --initiative INIT-999 --title "Invalid Epic"
```

Expected result:

```text id="tsrxcs"
ERROR: ENTITY_NOT_FOUND: INIT-999
```

State must not change.

---

# 12. Generated Markdown Freshness

Generated Markdown should match current state.

A generated file is stale when:

```text id="yx611g"
- state revision changed;
- render command was not run;
- generated content differs from renderer output;
- manual edits changed generated file.
```

Future validation may include:

```bash id="k8k71p"
python scripts/projectctl.py check generated
```

Expected behavior:

```text id="lrtdwb"
- render state into memory;
- compare with generated file on disk;
- fail if different.
```

---

# 13. AI Context Use

AI agents should not read raw state and events unless necessary.

Preferred AI reading path:

```text id="tc5y45"
AI_PROJECT/generated/*.md
```

For execution work, future systems should use:

```bash id="5sh72u"
python scripts/projectctl.py context build --task T-001 --profile codex
```

The AI should receive a short working packet, not the full project database.

## Context Principle

```text id="dvpbty"
State is for Python.
Events are for audit.
Generated Markdown is for humans and AI agents.
Prompt Package is for execution.
```

---

# 14. MVP Boundaries

## Included In MVP

The first state model includes:

```text id="lnthg3"
AI_PROJECT/state/plan.json
AI_PROJECT/events/plan-events.jsonl
AI_PROJECT/generated/CODEX_PLAN.md
```

The first CLI manages:

```text id="6zi9ru"
Project
Idea
Goal
Strategy
Initiative
Epic
```

## Excluded From MVP

The first MVP does not include:

```text id="1hqy14"
tasks.json
current.json
prompts.json
executions.json
reviews.json
qa.json
decisions.json
changes.json
releases.json
```

These are future controlled domains.

---

# 15. Future State Files

## tasks.json

Future file for executable work items.

```text id="9xo3ef"
AI_PROJECT/state/tasks.json
```

Stores:

```text id="6l3kn0"
Task[]
```

## current.json

Future file for the selected execution target.

```text id="xpx2ol"
AI_PROJECT/state/current.json
```

Stores:

```text id="gvb470"
current task id
set by
set at
```

## prompts.json

Future file for generated prompt package metadata.

```text id="eumfjz"
AI_PROJECT/state/prompts.json
```

Stores:

```text id="8iu7ag"
prompt package id
task id
profile
created at
source revision
```

## executions.json

Future file for Codex execution sessions.

```text id="uw3zjz"
AI_PROJECT/state/executions.json
```

Stores:

```text id="bs2xvk"
execution sessions
status
changed files
verification summary
```

## reviews.json

Future file for review lifecycle state.

```text id="3k239q"
AI_PROJECT/state/reviews.json
```

## qa.json

Future file for verification evidence.

```text id="mwymcx"
AI_PROJECT/state/qa.json
```

## decisions.json

Future file for project decisions.

```text id="h4xgcz"
AI_PROJECT/state/decisions.json
```

## changes.json

Future file for controlled system evolution.

```text id="xsy5zp"
AI_PROJECT/state/changes.json
```

## releases.json

Future file for release tracking.

```text id="e58lxw"
AI_PROJECT/state/releases.json
```

---

# 16. Design Principles

## 1. State Must Be Small And Structured

State files should contain current facts, not long prose histories.

Long descriptions may exist, but state should remain machine-validatable.

## 2. Events Must Preserve History

Events should explain how state changed.

State can be overwritten by newer state, but events must preserve the sequence of mutations.

## 3. Generated Files Must Be Disposable

Generated Markdown can be deleted and recreated.

If generated files are lost, they must be recoverable from state.

## 4. Python Owns Validation

AI agents should not be trusted to enforce lifecycle rules.

Python commands must validate every mutation.

## 5. Human Owner Owns Authority

Machine state may represent owner decisions, but must not silently create them.

AI may propose state changes, but owner approval boundaries must remain explicit.

## 6. No Hidden State In Chat

Important project state must not live only in conversation history.

If it matters for project control, it must be represented in state, events or generated output.

---

# Summary

Project Control State Model separates state, history and readable output.

```text id="ywf6pj"
state/*.json      -> current truth
events/*.jsonl    -> mutation history
generated/*.md    -> readable views
```

The first MVP applies this model to plan control:

```text id="7wkpgm"
plan.json
plan-events.jsonl
CODEX_PLAN.md
```

The long-term direction is to expand the same model to:

```text id="rxl8gq"
tasks
current task
prompt packages
executions
reviews
QA
decisions
changes
releases
```

The central rule remains:

```text id="ma2m50"
AI does not edit project state directly.
AI invokes allowed commands.
Python validates and updates state.
Audit logs preserve history.
Generated Markdown provides readable context.
Human Owner keeps final authority.
```

# Project Control Domain Model

## Status

Draft

## Purpose

This document defines the domain model for Project Control Gateway.

The domain model explains which project entities exist, what each entity means, where it is stored, who may change it, and whether it can be executed by Codex.

The goal is to prevent ambiguity between planning containers, executable work, generated prompts, reviews, QA results and project governance records.

## Core Rule

Only a `Task` is executable.

Planning entities such as `Idea`, `Goal`, `Strategy`, `Initiative` and `Epic` help structure the project, but they must never be treated as direct execution scope for Codex.

```text
Idea / Goal
└── Initiative
    └── Epic
        └── Task
            └── Prompt Package / Execution / Review / QA
```

## Domain Layers

Project Control Gateway has three conceptual layers:

```text
Planning Layer
  Project
  Idea
  Goal
  Strategy
  Initiative
  Epic

Execution Layer
  Task
  Current Task
  Prompt Package
  Execution Session

Control Layer
  Review
  QA Result
  Decision
  Change Proposal
  Release
```

The first MVP implemented only the Planning Layer through `planctl.py`.

Current self-hosted control also implements Task, Current Task, Prompt Package, Context Pack, Codex execution prompt/status, Documentation Control and Evolution Change Proposal control through the domain CLIs and `aictl.py` facade. Execution Session, Review, QA, Decision and Release control remain future or partial domains until approved evolution adds them.

## Self-Hosted Project Scope

When this model is applied to AI_Development_System itself, the controlled project is this repository.

Root `/AI_PROJECT` stores the self-hosted project-control state for repository evolution. `/ai-system` remains the source document tree for roles, rules, lifecycle documents, operating model, project-control specifications and evolution records.

The same `AI_PROJECT` name also appears in reusable contexts:

```text
/ai-system/templates/**/AI_PROJECT      templates copied into external projects
/examples/golden-project/AI_PROJECT     non-runtime onboarding and validation example
```

These reusable contexts are not this repository's live project-control state.

---

# 1. Project

## Definition

`Project` is the root entity of the controlled project.

It identifies the project being managed by AI Development System.

## Purpose

Project provides the top-level identity and status for the project control state.

## Stored In

```text
AI_PROJECT/state/plan.json
```

## Suggested Fields

```json
{
  "id": "PROJECT-001",
  "name": "AI Development System",
  "status": "active",
  "created_at": "...",
  "updated_at": "..."
}
```

## Allowed Statuses

```text
active
archived
```

## Executable

No.

The project itself is not executable scope.

## Human Owner Authority

Human Owner owns project identity, project purpose and project-level status.

---

# 2. Idea

## Definition

`Idea` is the short conceptual description of what the project is about.

It is intentionally high-level.

## Purpose

Idea captures the original direction before it is transformed into goals, strategy, initiatives, epics and tasks.

## Stored In

```text
AI_PROJECT/state/plan.json
```

## Suggested Fields

```json
{
  "text": "Create a controlled AI-assisted development system.",
  "updated_at": "..."
}
```

## Executable

No.

Idea must not be executed directly by Codex.

## Allowed Operations

```text
idea show
idea set
```

## Human Owner Authority

Human Owner owns the final wording of the idea.

AI may propose wording, but must not silently redefine the idea.

---

# 3. Goal

## Definition

`Goal` describes the target outcome of the project.

It answers the question:

```text
What are we trying to achieve?
```

## Purpose

Goal turns the idea into a concrete direction with success criteria.

## Stored In

```text
AI_PROJECT/state/plan.json
```

## Suggested Fields

```json
{
  "text": "Build a Project Control Gateway for AI Development System.",
  "success_criteria": [
    "Project state is changed only through CLI.",
    "Every mutation writes an audit event.",
    "Codex receives generated prompt packages."
  ],
  "updated_at": "..."
}
```

## Executable

No.

Goal guides planning but must not be sent to Codex as execution scope.

## Allowed Operations

```text
goal show
goal set
goal add-criterion
goal remove-criterion
```

## Human Owner Authority

Human Owner owns the goal and success criteria.

---

# 4. Strategy

## Definition

`Strategy` describes how the project intends to reach the goal.

It contains planning principles, constraints and a high-level implementation direction.

## Purpose

Strategy prevents Codex and other AI agents from inventing project direction during execution.

## Stored In

```text
AI_PROJECT/state/plan.json
```

## Suggested Fields

```json
{
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
  "updated_at": "..."
}
```

## Executable

No.

Strategy can shape tasks, but must not be executed directly.

## Allowed Operations

```text
strategy show
strategy set-summary
strategy add-principle
strategy remove-principle
strategy add-constraint
strategy remove-constraint
```

## Human Owner Authority

Human Owner owns strategy and may approve changes to project direction.

---

# 5. Initiative

## Definition

`Initiative` is a strategic planning container under the project goal.

It groups related epics that contribute to a meaningful project capability.

## Purpose

Initiative helps organize long-running work into large project directions.

Example:

```text
Project Control Gateway
Codex Plugin Integration
Prompt Package Builder
Review and QA Control
```

## Stored In

```text
AI_PROJECT/state/plan.json
```

## Suggested Fields

```json
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

## ID Format

```text
INIT-001
INIT-002
INIT-003
```

## Allowed Statuses

```text
proposed
planned
active
blocked
done
deferred
archived
```

## Executable

No.

Initiative is not executable scope.

Codex must not receive an Initiative as a task.

## Allowed Operations

```text
initiative list
initiative show
initiative create
initiative rename
initiative summary
initiative status
initiative archive
```

## Relationship Rules

An Initiative may contain many Epics.

```text
Initiative
└── Epic[]
```

An Initiative may be archived only when its active Epics are already inactive, done, deferred or archived.

Force-archiving an Initiative may archive child Epics if explicitly supported by the CLI.

## Human Owner Authority

Human Owner owns Initiative creation, reprioritization and closure.

AI may propose Initiatives, but must not silently create strategic direction without owner intent.

---

# 6. Epic

## Definition

`Epic` is a delivery planning container under an Initiative.

It groups Tasks that together deliver a coherent capability or project milestone.

## Purpose

Epic turns strategic work into manageable delivery areas.

Example:

```text
Plan Control CLI
Task Control CLI
Prompt Package Builder
Protected Files Check
Codex Skill Packaging
```

## Stored In

```text
AI_PROJECT/state/plan.json
```

## Suggested Fields

```json
{
  "id": "EPIC-001",
  "initiative_id": "INIT-001",
  "title": "Plan Control CLI",
  "status": "planned",
  "summary": "Manage idea, goal, strategy, initiatives and epics through Python.",
  "priority": 1,
  "order": 1,
  "created_at": "...",
  "updated_at": "..."
}
```

## ID Format

```text
EPIC-001
EPIC-002
EPIC-003
```

## Allowed Statuses

```text
proposed
planned
active
blocked
done
deferred
archived
```

## Executable

No.

Epic is not executable scope.

Codex must not execute an Epic directly.

An Epic must be decomposed into Tasks before execution.

## Allowed Operations

```text
epic list
epic show
epic create
epic rename
epic summary
epic status
epic archive
```

## Relationship Rules

Each Epic must reference exactly one Initiative.

```text
Epic.initiative_id -> Initiative.id
```

An Epic cannot be created under a missing Initiative.

An Epic cannot be created under an archived Initiative.

An Epic cannot become active under an archived Initiative.

## Human Owner Authority

Human Owner owns Epic approval and prioritization.

AI may propose Epics, but must not treat an Epic as approved executable work.

---

# 7. Task

## Definition

`Task` is the smallest executable unit of project work.

Only a Task may be assigned to Codex for implementation.

## Purpose

Task converts planning intent into bounded executable work with scope, out of scope, allowed files, acceptance criteria and verification expectations.

## Stored In

Future file:

```text
AI_PROJECT/state/tasks.json
```

## Suggested Fields

```json
{
  "id": "T-001",
  "epic_id": "EPIC-001",
  "title": "Create planctl.py",
  "status": "approved",
  "summary": "Create a strict Python CLI for plan control.",
  "description": "...",
  "scope": [],
  "out_of_scope": [],
  "allowed_files": [],
  "acceptance_criteria": [],
  "verification_mode": "standard",
  "owner_approved": true,
  "created_at": "...",
  "updated_at": "..."
}
```

## ID Format

```text
T-001
T-002
T-003
```

## Suggested Statuses

```text
proposed
draft
ready
approved
in_progress
blocked
in_review
rework_required
done
rejected
deferred
archived
```

## Executable

Yes.

Task is the only executable project planning entity.

## Required Before Approval

A Task must not become approved unless it has:

```text
title
epic_id
summary or description
scope
out_of_scope
allowed_files
acceptance_criteria
verification_mode
```

## Relationship Rules

Each Task must reference exactly one Epic.

```text
Task.epic_id -> Epic.id
```

A Task cannot be created under a missing Epic.

A Task cannot be approved if its parent Epic is archived.

## Human Owner Authority

Human Owner must approve a Task before Codex execution.

---

# 8. Current Task

## Definition

`Current Task` identifies the single task currently selected for Codex execution.

## Purpose

Current Task prevents Codex from choosing arbitrary work from the backlog.

## Stored In

Future file:

```text
AI_PROJECT/state/current.json
```

## Suggested Fields

```json
{
  "task_id": "T-001",
  "set_at": "...",
  "set_by": "human_owner"
}
```

## Executable

Indirectly.

Current Task points to the approved Task that may be executed.

## Rules

Only one Current Task may exist at a time.

Current Task must reference an existing Task.

Current Task must not reference an archived, rejected or deferred Task.

Codex must not change Current Task manually.

## Allowed Operations

```text
current show
current set
current clear
```

---

# 9. Prompt Package

## Definition

`Prompt Package` is a generated execution contract for an AI agent.

It is built from approved project state, especially the Current Task.

## Purpose

Prompt Package gives Codex a narrow and explicit working context.

It prevents Codex from reading the entire project and inventing scope.

## Stored In

Future generated file:

```text
AI_PROJECT/generated/PROMPT_PACKAGE.md
```

or future state file:

```text
AI_PROJECT/state/prompts.json
```

## Suggested Content

```text
Active Role
Active Mode
Active Task
Expected Result
Scope
Out of Scope
Allowed Files
Forbidden Actions
Acceptance Criteria
Verification Mode
Stop Conditions
Report Format
```

## Executable

No.

Prompt Package is not a project entity to execute; it is the generated instruction package used for execution.

## Rules

Prompt Package must be generated from approved state.

Prompt Package must not invent scope.

Prompt Package must not include unrelated backlog items.

Prompt Package must not override Human Owner approval.

## Allowed Operations

```text
prompt build --task <TASK_ID>
prompt show --task <TASK_ID>
prompt validate --task <TASK_ID>
```

---

# 10. Execution Session

## Definition

`Execution Session` records an actual Codex work attempt against an approved Task.

## Purpose

Execution Session separates task definition from execution history.

A Task may require multiple execution sessions if rework is needed.

## Stored In

Future file:

```text
AI_PROJECT/state/executions.json
AI_PROJECT/events/execution-events.jsonl
```

## Suggested Fields

```json
{
  "id": "EXEC-001",
  "task_id": "T-001",
  "status": "running",
  "started_at": "...",
  "finished_at": null,
  "actor": "codex",
  "prompt_package_id": "PROMPT-001",
  "changed_files": [],
  "verification_summary": ""
}
```

## Suggested Statuses

```text
planned
running
completed
failed
cancelled
```

## Executable

Execution Session represents execution, but is not itself a planning unit.

## Rules

Execution Session must reference an approved Task.

Execution Session must not exceed the Task scope and allowed files.

Execution Session must record verification output before completion.

---

# 11. Review

## Definition

`Review` records structured evaluation of completed work.

## Purpose

Review prevents unchecked Codex output from being treated as done.

## Stored In

Future file:

```text
AI_PROJECT/state/reviews.json
AI_PROJECT/events/review-events.jsonl
AI_PROJECT/generated/REVIEW_STATUS.md
```

## Suggested Fields

```json
{
  "id": "REV-001",
  "task_id": "T-001",
  "status": "open",
  "review_type": "code_review",
  "findings": [],
  "created_at": "...",
  "updated_at": "..."
}
```

## Suggested Statuses

```text
open
changes_requested
approved
closed
cancelled
```

## Executable

No.

Review is a control entity.

## Rules

Done work should require review or explicit review waiver.

Critical findings must block task completion.

---

# 12. QA Result

## Definition

`QA Result` records verification evidence for a Task or Execution Session.

## Purpose

QA Result separates claims of completion from actual evidence.

## Stored In

Future file:

```text
AI_PROJECT/state/qa.json
AI_PROJECT/events/qa-events.jsonl
AI_PROJECT/generated/QA_STATUS.md
```

## Suggested Fields

```json
{
  "id": "QA-001",
  "task_id": "T-001",
  "execution_id": "EXEC-001",
  "verification_mode": "standard",
  "status": "passed",
  "checks": [],
  "summary": "",
  "created_at": "..."
}
```

## Suggested Statuses

```text
not_run
passed
failed
waived
blocked
```

## Executable

No.

QA Result is verification evidence.

## Rules

A Task must not become Done without verification evidence or explicit Human Owner waiver.

---

# 13. Decision

## Definition

`Decision` records an architectural, product, process or governance decision.

## Purpose

Decision prevents important project choices from being hidden in chat history.

## Stored In

Future file:

```text
AI_PROJECT/state/decisions.json
AI_PROJECT/events/decision-events.jsonl
AI_PROJECT/generated/DECISION_LOG.md
```

## Suggested Fields

```json
{
  "id": "DEC-001",
  "title": "Use JSON state as canonical project state",
  "status": "accepted",
  "context": "",
  "decision": "",
  "consequences": "",
  "created_at": "...",
  "updated_at": "..."
}
```

## Suggested Statuses

```text
proposed
accepted
rejected
superseded
archived
```

## Executable

No.

Decision is governance state.

## Rules

Major project control changes should reference accepted Decisions.

---

# 14. Change Proposal

## Definition

`Change Proposal` describes a proposed change to the AI Development System itself.

## Purpose

Change Proposal controls evolution of rules, lifecycle documents, command catalogs, schemas and prompts.

## Stored In

Future file:

```text
AI_PROJECT/state/changes.json
AI_PROJECT/events/change-events.jsonl
AI_PROJECT/generated/CHANGE_LOG.md
```

## Suggested Fields

```json
{
  "id": "CHG-001",
  "title": "Add task control CLI",
  "status": "proposed",
  "scope": [],
  "out_of_scope": [],
  "impact": [],
  "owner_approved": false,
  "created_at": "...",
  "updated_at": "..."
}
```

## Suggested Statuses

```text
proposed
draft
approved
in_progress
in_review
accepted
rejected
archived
```

## Executable

No.

A Change Proposal may produce Tasks, but is not itself executable by Codex unless converted into an approved Task.

## Rules

Changes to Project Control Gateway rules must go through explicit approval.

AI must not silently evolve the control model.

---

# 15. Release

## Definition

`Release` records a packaged version of AI Development System or a project-local control layer.

## Purpose

Release provides versioned delivery and upgrade tracking.

## Stored In

Future file:

```text
AI_PROJECT/state/releases.json
AI_PROJECT/events/release-events.jsonl
AI_PROJECT/generated/RELEASE_STATUS.md
```

## Suggested Fields

```json
{
  "id": "REL-001",
  "version": "0.1.0",
  "status": "planned",
  "included_changes": [],
  "created_at": "...",
  "released_at": null
}
```

## Suggested Statuses

```text
planned
candidate
released
deprecated
archived
```

## Executable

No.

Release is packaging and tracking state.

---

# Entity Summary

| Entity            | Layer     | Stored In MVP | Executable | Notes                        |
| ----------------- | --------- | ------------: | ---------: | ---------------------------- |
| Project           | Planning  |           Yes |         No | Root project identity        |
| Idea              | Planning  |           Yes |         No | High-level concept           |
| Goal              | Planning  |           Yes |         No | Target outcome               |
| Strategy          | Planning  |           Yes |         No | Direction and constraints    |
| Initiative        | Planning  |           Yes |         No | Strategic container          |
| Epic              | Planning  |           Yes |         No | Delivery container           |
| Task              | Execution |            No |        Yes | Smallest executable unit     |
| Current Task      | Execution |            No |   Indirect | Selects approved Task        |
| Prompt Package    | Execution |            No |         No | Generated execution contract |
| Execution Session | Execution |            No |         No | Records Codex work attempt   |
| Review            | Control   |            No |         No | Structured evaluation        |
| QA Result         | Control   |            No |         No | Verification evidence        |
| Decision          | Control   |            No |         No | Persistent decision record   |
| Change Proposal   | Control   |            No |         No | Controlled system evolution  |
| Release           | Control   |            No |         No | Versioned delivery state     |

---

# Current Implementation Boundary

The first MVP implemented:

```text
Project
Idea
Goal
Strategy
Initiative
Epic
```

Current self-hosted control also implements:

```text
Task
Current Task
Prompt Package
Context Pack
Codex prompt/status
Documentation Control
Change Proposal
```

Current self-hosted control does not yet fully implement:

```text
Execution Session
Review
QA Result
Decision
Release
```

These require approved evolution before they become controlled state domains.

---

# Design Principles

## 1. Separate Planning From Execution

Planning containers must not become execution scope.

```text
Initiative != Task
Epic != Task
Goal != Task
```

Only an approved Task may be executed.

## 2. Keep State Machine-Readable

Domain entities should be stored in JSON state files and validated by Python.

Markdown is a generated view, not source of truth.

## 3. Preserve Audit History

Every mutation must write an append-only event.

The system must be able to explain:

```text
who changed what
when it changed
which command was used
which revision was created
```

## 4. Require Explicit Parent Links

Child entities must reference parents by ID.

```text
Epic.initiative_id -> Initiative.id
Task.epic_id -> Epic.id
```

Missing parent references are invalid.

## 5. Make AI a Command Router

AI should not freely mutate the project.

AI should map owner intent to allowed commands.

```text
Owner intent -> allowed CLI command -> validation -> state mutation
```

## 6. Keep Human Owner Authority

AI may propose, summarize and execute approved work.

Human Owner keeps authority over:

```text
goal
strategy
approval
acceptance
control model changes
```

---

# Long-Term Domain Direction

The final Project Control Gateway should become a project control kernel:

```text
Project Control Gateway
├── Plan Control
├── Task Control
├── Prompt Package Builder
├── Execution Control
├── Review Control
├── QA Control
├── Decision Control
├── Change Control
└── Release Control
```

The long-term operating model is:

```text
Human Owner defines intent.
AI maps intent to commands.
Python validates and updates state.
Audit logs preserve history.
Generated Markdown provides readable views.
Codex executes only approved Tasks.
```

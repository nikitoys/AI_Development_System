# Work Item Hierarchy

Status: Draft
Version: v0.1.0

## Purpose

This document defines the planning hierarchy used by AI_Development_System to connect broad project direction to executable work.

The hierarchy is:

```text
Goal
-> Initiative
-> Epic
-> Task
-> Agent Work Package
```

This hierarchy is for planning, traceability and scope control.

It does not add runtime behavior, automatic execution, automatic acceptance, new task lifecycle states or new parallel execution behavior.

## Core Definitions

## Goal

A goal is a high-level project or system outcome.

Examples:

- make a product usable for its first target audience;
- improve AI_Development_System planning clarity;
- reduce review failures in repeated task types.

Rules:

- A goal explains why work matters.
- A goal may contain zero, one or many initiatives.
- A goal is not an executable unit.
- A goal does not authorize repository changes.

## Initiative

An initiative is a planning container under a goal.

It groups related epics and tasks that contribute to the same meaningful outcome.

Rules:

- An initiative should have a clear purpose and expected outcome.
- An initiative may contain zero, one or many epics.
- An initiative may be shown in `CODEX_PLAN.md`.
- An initiative is not an executable unit.
- An initiative does not authorize repository changes, Codex execution or Agent Work Package execution.

## Epic

An epic is a smaller planning container under an initiative.

It groups related tasks that together deliver a coherent capability, documentation outcome, governance improvement or technical result.

Rules:

- An epic should be small enough to decompose into concrete tasks.
- An epic may contain zero, one or many tasks.
- An epic may be shown in `CODEX_PLAN.md`.
- An epic is not an executable unit.
- An epic does not authorize repository changes, Codex execution or Agent Work Package execution.

## Task

A task is the bounded executable unit of work.

A task must define scope, out of scope, owner role, acceptance criteria, verification expectations and expected output before execution.

Rules:

- A task may optionally reference an initiative and an epic.
- A task may exist without an initiative or epic when the work is small.
- A task remains governed by `task-format.md` and `task-lifecycle.md`.
- A task may be executed only after required Human Owner approval.
- A task may have zero, one or many Agent Work Packages.

## Agent Work Package

An Agent Work Package is a child planning unit under a parent task.

It describes what one role or executor context should contribute to the parent task.

Rules:

- An Agent Work Package must reference a parent task.
- An Agent Work Package must stay inside the parent task scope.
- An Agent Work Package must not expand parent task acceptance criteria.
- An Agent Work Package must not authorize repository changes by itself.
- An Agent Work Package remains governed by `agent-work-package.md`.

## Relationship Rules

The planning hierarchy has two container levels above tasks and one planning decomposition level below tasks.

```text
Goal: why the work matters
Initiative: major planning outcome under the goal
Epic: related task group under the initiative
Task: executable unit
Agent Work Package: child planning contribution inside the task
```

Important boundaries:

- Initiative and Epic are planning containers only.
- Task remains the executable unit.
- Agent Work Package remains a child planning unit under Task.
- Human Owner approval remains required before repository-changing execution.
- The hierarchy does not change task lifecycle states.
- The hierarchy does not replace Agent Work Packages.
- The hierarchy does not enable automatic execution, automatic dispatch, automatic merge or automatic acceptance.
- The hierarchy does not enable parallel execution.

## Relationship to Project Control Files

`CODEX_PLAN.md` may show goals, initiatives and epics so the Human Owner can review direction and sequencing.

`CODEX_TASKS.md` may map each task to an optional initiative and epic.

`CODEX_CURRENT.md` remains the place where a single current task is approved for execution in concrete project control files.

`AGENT_PLAN.md` and `AGENT_TASKS.md` may reference the parent task and its planning path, but Agent Work Packages still depend on the parent task for authority.

## Relationship to Task Lifecycle

Task Lifecycle governs task states, approval, review, rework, acceptance, rejection, deferral and archival.

Initiatives and epics do not have task lifecycle states unless a project chooses to track their planning status locally.

Moving an initiative or epic forward does not move any task to `Approved`, `In Progress`, `In Review` or `Done`.

## Relationship to Codex Execution

Codex may execute only an approved task or approved prompt package with explicit boundaries.

Initiatives and epics may provide planning context in a prompt, but they must not be treated as executable scope.

Before Codex execution, the task or prompt package must still define:

- active role;
- source documents;
- scope;
- out of scope;
- allowed or expected files;
- forbidden actions;
- acceptance criteria;
- verification expectations;
- expected output.

## Example

```text
Goal: G-001 Improve Task Tracker planning clarity
Initiative: INIT-001 Task list usability
Epic: EPIC-001 Due-date filtering
Task: T-003 Plan due-date filtering for Task Tracker
Agent Work Packages:
- AWP-REQ-001 Define requirements and acceptance criteria
- AWP-BE-001 Draft backend/API implementation boundaries
- AWP-FE-001 Draft frontend/UX implementation boundaries
- AWP-QA-001 Draft QA and integration review checks
```

In this example, only `T-003` can become an executable task after approval.

The initiative and epic organize the plan. The Agent Work Packages decompose the task. None of those containers or child packages authorize execution by themselves.

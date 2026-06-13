# Task Lifecycle

Status: Draft
Version: v0.1.0

## Purpose

This document defines how managed tasks are proposed, drafted, refined, approved, started, blocked, resumed, submitted for review, reworked, accepted, rejected, deferred, archived and reopened inside the AI Development System.

It applies the shared governance model from `/ai-system/lifecycle-governance.md` to task execution and task control.

## Governed Entity

A managed task is a bounded unit of work that can change repository files, documentation, product behavior, system behavior, review output or execution state.

Managed tasks include:

- product tasks;
- documentation tasks;
- implementation tasks;
- test and QA tasks;
- infrastructure tasks;
- review and rework tasks;
- AI Development System tasks;
- Codex execution tasks.

Informal discussion, brainstorming and temporary notes are not managed tasks unless they are converted into a task with scope, owner and acceptance criteria.

## Source of Truth

Default source-of-truth locations for managed tasks are:

- `/ai-system/work-item-hierarchy.md` for the relationship between goals, initiatives, epics, tasks and Agent Work Packages;
- `/ai-system/task-format.md` for the standard task template, Definition of Ready and Definition of Done;
- `/docs` for product backlog, requirements and project-specific task records when a product project exists;
- `/ai-system` for AI Development System evolution tasks;
- prompt packages for Codex-ready execution boundaries;
- review reports for review findings and rework decisions.

If a task conflicts with source documents, report the conflict before execution.

## Task Lifecycle States

Managed tasks should use these states where applicable:

- `Proposed` - suggested but not yet shaped into a task.
- `Draft` - written but not yet ready for approval or execution.
- `Ready` - satisfies Definition of Ready from `/ai-system/task-format.md`.
- `Approved` - accepted by the Human Owner or explicitly authorized for execution.
- `In Progress` - currently being executed by an AI role or Codex Executor.
- `Blocked` - cannot continue without missing information, approval or external change.
- `In Review` - submitted for review after execution.
- `Rework Required` - review found issues that must be addressed before acceptance.
- `Done` - accepted after criteria, review and required documentation are satisfied.
- `Rejected` - reviewed or considered and not accepted.
- `Deferred` - postponed without rejection.
- `Archived` - retained for history, not active.

Task status values in specific task documents may be shorter, but they should map back to these states.

## Task Operations

## Read

Goal: understand the current task before planning, execution or review.

Rules:

- Read the task, source documents, scope, out of scope and acceptance criteria.
- Check owner role, expected files and result format.
- Report missing Definition of Ready fields before execution.

## Create

Goal: define a bounded unit of work.

A task should include:

- title or task ID;
- status;
- type;
- optional initiative or epic reference;
- owner role;
- context;
- input documents;
- description;
- scope;
- out of scope;
- expected files;
- acceptance criteria;
- test cases or checks;
- risks;
- result format.

Use `/ai-system/task-format.md` as the source template.

## Refine

Goal: make a draft task ready for execution.

Refinement may add missing context, input documents, scope boundaries, acceptance criteria, test cases, risks or expected output.

Refinement must not silently expand scope beyond the Human Owner request.

## Approve

Goal: authorize a ready task for execution.

Human Owner approval is required when the task can change repository files, product behavior, AI Development System behavior, architecture, roles, workflow, lifecycle rules or system version.

## Start

Goal: move an approved task into execution.

Before start:

- Definition of Ready must be satisfied;
- owner role must be clear;
- allowed files or expected files must be known;
- acceptance criteria must be testable;
- blockers must be resolved or explicitly accepted.

## Block

Goal: pause execution when work cannot continue safely.

A task should be blocked when:

- required source documents are missing;
- scope or acceptance criteria conflict;
- Human Owner approval is missing;
- needed information cannot be inferred safely;
- execution would exceed allowed files or forbidden actions.

The blocker and needed decision should be recorded.

## Resume

Goal: continue a blocked or deferred task after the blocker is resolved.

Resume should confirm:

- what changed;
- which blocker was resolved;
- whether scope or acceptance criteria changed;
- whether new approval is needed.

## Submit for Review

Goal: move completed execution output into review.

Submission should include:

- changed files;
- summary;
- checks or tests;
- errors;
- questions;
- diff or key changes.

This matches the Codex result format in `/ai-system/human-interaction.md`.

## Request Rework

Goal: return a reviewed task for targeted correction.

Rework must be narrower than the original task and address approved review findings only.

Rework should identify:

- review findings;
- severity;
- required changes;
- allowed files;
- acceptance criteria for the rework.

## Accept

Goal: close a task as done.

Only the Human Owner accepts final task results.

A task may be accepted when Definition of Done is satisfied or when the Human Owner explicitly accepts a documented risk.

## Reject

Goal: close a task as not accepted.

Rejection should record why the task was rejected and whether follow-up work is needed.

Rejected tasks must not be treated as source-of-truth changes.

## Defer

Goal: postpone a task without rejecting it.

Deferred tasks should record:

- reason;
- condition for resuming;
- owner or next reviewer;
- whether the task is still valid.

## Archive

Goal: retain inactive task history.

Archived tasks are not active work. They may be referenced for history, audit or lessons learned.

## Reopen

Goal: return a closed task to active handling when new evidence shows the result is incomplete, incorrect or outdated.

Reopen should record:

- why reopening is needed;
- which previous decision is affected;
- whether the task returns to `Draft`, `Ready`, `Approved`, `In Progress` or `Rework Required`;
- whether Human Owner approval is needed.

## Ownership Model

Default ownership:

- Human Owner defines direction, approves execution when needed and accepts or rejects final results.
- ChatGPT Orchestrator routes the task, selects active role, prepares prompts and reviews Codex output.
- Project Manager AI decomposes, orders and tracks tasks.
- Relevant domain role owns task content in its area.
- Codex Executor executes approved repository changes within explicit scope.
- Reviewer role checks the result before final acceptance.

Task ownership may change between lifecycle states, but each state should have a clear owner.

## Definition of Ready

Definition of Ready is defined in `/ai-system/task-format.md`.

A task is ready when it has:

- clear description;
- input documents;
- scope;
- out of scope;
- acceptance criteria;
- owner role;
- no blocking ambiguity.

Task Lifecycle uses Definition of Ready as the gate before `Approved` or `In Progress`.

## Definition of Done

Definition of Done is defined in `/ai-system/task-format.md`.

A task is done when:

- acceptance criteria are satisfied;
- review passed;
- QA passed or test cases are documented;
- documentation is updated if needed;
- Human Owner approved the result.

Task Lifecycle uses Definition of Done as the gate before `Done`.

## Relationship to Work Item Hierarchy

Task Lifecycle operates at the `Task` level of `/ai-system/work-item-hierarchy.md`.

Goals, initiatives and epics are planning containers above tasks. They may provide context, grouping, priority and sequencing, but they are not executable units and do not own task lifecycle states.

Agent Work Packages are child planning units under tasks. They may decompose task work for one role or executor context, but they do not make the parent task `Approved`, `In Progress`, `In Review` or `Done`.

Rules:

- Initiative and Epic fields are optional task metadata.
- Missing Initiative or Epic values do not block Definition of Ready.
- A task remains the executable unit.
- Agent Work Packages must stay inside parent task scope.
- Human Owner approval remains required before repository-changing execution.
- Moving a goal, initiative or epic forward must not bypass task approval, review, QA or acceptance.

## Relationship to Codex Execution

Codex Executor may execute a task only when execution boundaries are explicit.

Before Codex execution, a task or prompt package should define:

- role;
- context;
- input documents;
- scope;
- out of scope;
- allowed or expected files;
- forbidden actions;
- acceptance criteria;
- expected output.

Codex execution does not replace Human Owner approval or review. Codex reports results; ChatGPT Orchestrator and reviewer roles evaluate them; Human Owner decides.

This document defines task state boundaries. It does not define the full Codex execution lifecycle.

## Relationship to Review

A task moves to `In Review` after execution output is submitted.

Review should follow `/ai-system/review-process.md` and check:

- task compliance;
- architecture or process compliance;
- security or safety risks when applicable;
- readability and maintainability when code is involved;
- acceptance criteria;
- negative scenarios and regression risks;
- documentation consistency.

Critical issues block acceptance. Major issues require fix or explicit Human Owner decision.

## Approval Rules

Human Owner approval is required for tasks that:

- change repository files;
- change product scope or behavior;
- change architecture;
- change API contracts;
- change AI Development System behavior;
- change roles, workflow, lifecycle states, prompt requirements or review rules;
- execute Codex against repository files;
- accept final results;
- accept major review risk without rework;
- reopen, reject or archive system-level tasks when the decision affects source of truth.

Small read-only analysis tasks may proceed without approval when they do not change repository state or system behavior.

## AICP Relationship

An AICP is required when a task affects:

- AI Development System behavior;
- role definitions or responsibilities;
- lifecycle governance;
- workflow or approval process;
- prompt requirements;
- review process;
- system version;
- permanent adoption of an experiment;
- rollback of an applied system change.

An AICP is not required for ordinary product, documentation or implementation tasks unless they change the AI Development System itself.

## Version Impact Rules

Use `MAJOR.MINOR.PATCH`.

- Patch: wording, formatting, link correction or task clarification without behavior change.
- Minor: new task lifecycle document, new task state, new task operation, new task gate or meaningful execution rule.
- Major: significant change to task ownership, approval model, workflow, operating model or execution governance.

When uncertain, choose the higher impact and ask the Human Owner to confirm.

## Audit and History Rules

Task history should preserve:

- task identity or title;
- owner role;
- source documents;
- scope and out of scope;
- acceptance criteria;
- state changes;
- blockers;
- review outcome;
- Human Owner decision;
- changed files or affected documents when applicable.

Use:

- task records or backlog documents for task history;
- Codex result output for execution history;
- review reports for review history;
- `system-changelog.md` for applied AI Development System task lifecycle changes;
- AICP documents for proposed system behavior changes;
- git history for exact repository diffs and commits.

## Relationship to Lifecycle Governance

This document specializes `/ai-system/lifecycle-governance.md` for managed tasks.

If this document and lifecycle governance conflict, report the conflict and require Human Owner approval before changing behavior.

## Relationship to Document Lifecycle

Tasks often create or update managed documents.

When a task changes source-of-truth documentation, it must respect `/ai-system/document-lifecycle.md` for documentation status, review, approval, index updates, archival, removal and rollback.

## Relationship to Process Lifecycle

Task Lifecycle is a managed process and must respect `/ai-system/process-lifecycle.md`.

Changes to task states, task gates, task ownership, review flow or task approval rules are process changes and may require Human Owner approval and AICP.

## Boundary Rules

Task lifecycle must not be used to bypass Human Owner control.

Task lifecycle must not change Codex execution behavior beyond documenting task boundaries.

Task lifecycle must not redesign review process, QA process or workflow unless explicitly approved.

Task lifecycle must not combine unrelated product, implementation, documentation and system evolution work unless the task explicitly allows it.

Task lifecycle must not treat a goal, initiative, epic or Agent Work Package as execution authority unless an approved task or prompt package provides explicit execution boundaries.

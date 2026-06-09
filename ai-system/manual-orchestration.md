# Manual Multi-Agent Orchestration Mode

Status: Draft  
Version: v0.1.0

## Purpose

This document defines Manual Multi-Agent Orchestration Mode for AI_Development_System.

Manual orchestration is the current L3 mode in the runtime maturity model. It coordinates multiple logical agents and Agent Work Packages manually while preserving Human Owner control and keeping execution external to orchestration tooling.

This document does not implement runtime behavior.

It does not authorize automatic execution, automatic merge, automatic acceptance or automatic QA/review closure.

## Runtime Maturity Relationship

Current level:

```text
L3 — Manual multi-agent orchestration
```

Next possible target:

```text
L4 — Assisted execution
```

Runtime decision:

```text
DEFERRED
```

L3 is manual-only and current. L4 and higher remain future/not approved.

## Source-of-Truth Documents

Manual orchestration depends on:

- `runtime-maturity-levels.md` for maturity boundaries.
- `sop-model.md` for SOP selection.
- `agent-work-package.md` for Agent Work Package structure and status values.
- `multi-agent-planning.md` for planning-only decomposition and candidate groups.
- `parallel-execution-policy.md` for Human Owner-approved parallel group boundaries.
- `role-agent-assignment.md` for manual assignment of ready packages to logical agents or external agent sessions.
- `l3-role-assigned-parallel-runbook.md` for the practical manual role-assigned parallel orchestration procedure.
- `agent-result-intake.md` for manual result intake.
- `integration-review.md` for manual integration review.
- `task-format.md`, `task-lifecycle.md`, `prompt-lifecycle.md` and `codex-lifecycle.md` for task and execution boundaries.
- `review-process.md`, `review-lifecycle.md` and `qa-lifecycle.md` for review and QA gates.
- `security-policy.md` and `privacy-data-handling-policy.md` for safety boundaries.
- `evolution/evolution-backlog.md` and `system-changelog.md` for system evolution tracking.

If this document conflicts with those source documents, the stricter Human Owner approval and safety boundary wins until a later approved system change updates the source of truth.

## Definition

Manual Multi-Agent Orchestration Mode is a governed workflow for coordinating multiple logical agents or Agent Work Packages without a runtime.

It may use dependency-aware dry-run planning output to decide what is ready next, but every transition, assignment, result intake, review, QA route and approval remains manually controlled.

Candidate parallel groups are planning information. They are not execution approval.

## Allowed L3 Manual Operations

L3 allows:

- create or select an agent plan;
- validate an agent plan;
- list ready Agent Work Package candidates;
- select the next Agent Work Package manually;
- assign an Agent Work Package to a logical or external agent manually;
- prepare or hand off a bounded prompt manually;
- record Agent Work Package status manually according to existing lifecycle conventions;
- record agent result intake manually;
- run integration review manually;
- request Human Owner approval;
- record decisions, follow-ups and blocked states manually;
- recompute the next ready group after manual status changes.

## Forbidden L3 Operations

L3 forbids:

- automatic Codex execution;
- automatic multi-agent execution;
- automatic agent dispatch;
- automatic branch/worktree lifecycle;
- automatic file modification by orchestration tooling;
- automatic merge;
- automatic acceptance;
- automatic QA/review closure;
- bypassing Human Owner approval;
- treating candidate parallel groups as approval to execute automatically.

## Required L3 Artifacts

Manual orchestration requires:

- Agent Plan;
- Agent Work Packages;
- dependency-aware planning output;
- Role-to-Agent Assignment records;
- Agent Result Intake records using the hardened Agent Result schema in `agent-result-intake.md`;
- Integration Review record;
- Human Owner approval record;
- decision, follow-up or blocked-state records when applicable;
- changelog, backlog or evolution records when system behavior or source-of-truth documentation changes.

## L3 Flow

```text
Plan prepared
-> plan validated
-> ready Agent Work Package group identified
-> Human Owner selects next Agent Work Package or approved group
-> package is assigned manually to a logical agent or external agent session
-> bounded prompt draft is prepared for that assignment
-> package is executed manually or externally outside orchestration tooling
-> result is recorded using the hardened Agent Result schema
-> Agent Result Intake is performed manually
-> Integration Review is performed manually when needed
-> Human Owner approves, requests rework, rejects or defers
-> package status is updated manually
-> next ready group is computed
```

## Status Handling

Agent Work Package status changes must follow `agent-work-package.md`.

Manual orchestration may record status changes such as:

- `Ready`;
- `Approved`;
- `Blocked`;
- `In Progress`;
- `Result Submitted`;
- `In Review`;
- `Rework Required`;
- `Accepted`;
- `Rejected`;
- `Deferred`;
- `Archived`.

Status changes must be evidence-based. A package result does not make the parent task accepted. Final parent-task acceptance remains a Human Owner decision.

## Human Owner Gates

Human Owner approval is required before:

- execution scope is treated as approved;
- a candidate parallel group is treated as an approved parallel execution group;
- residual risk is accepted;
- QA is skipped;
- a parent task is accepted;
- any move toward L4 is proposed.

## L3 Readiness Criteria

L3 readiness requires:

- `EVOL-019` through `EVOL-026` are done;
- runtime execution remains `DEFERRED`;
- dependency-aware planning validation passes;
- hardened manual result intake format exists;
- integration review process exists;
- safety boundaries are documented;
- pilot evidence covers documentation-only, small code/tooling and multi-agent parallel planning scenarios;
- pilot records distinguish validated dry-run behavior, manually simulated orchestration behavior and future/not-yet-validated runtime behavior;
- Human Owner approval remains required.

Current assessment:

These readiness criteria are met. L3 is the current maturity level, but it remains manual-only and does not authorize runtime execution.

## L3 Exit Criteria / L4 Readiness

L4 may only be reconsidered after:

- repeated pilot evidence is recorded;
- Agent Work Package state tracking is stable;
- hardened result intake schema is reliable enough for review;
- CI checks exist for specs, templates and planning fixtures;
- no critical safety boundary violations are found;
- Human Owner explicitly approves an L4 assisted-execution proposal.

L4 remains future/not approved until those criteria are met and a separate bounded evolution task is approved.

## Boundary Statement

Manual Multi-Agent Orchestration Mode is coordination, not runtime.

It preserves dry-run planning boundaries, Human Owner control, manual execution handoff, manual result intake, manual integration review and manual acceptance decisions.

It must not be used to introduce automatic execution or automatic acceptance by implication.

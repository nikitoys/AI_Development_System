# SOP and Multi-Agent Implementation Plan

Status: Draft
Version: v0.1.0

## Purpose

This document records the Human Owner's controlled evolution plan for adding a governance-first SOP and optional multi-agent execution layer to AI_Development_System.

This is a master implementation plan, not runtime behavior.

## Source

```text
Source: Human Owner request
Date recorded: 2026-06-09
Plan ID: OWNER-EVOL-SOP-MA-001
Active Role: AI System Maintainer + Technical Writer AI
Active Stage: Record SOP and Multi-Agent Implementation Plan
```

## Goal

Increase project implementation speed and quality through SOP-guided AI development, optional task decomposition into Agent Work Packages and controlled parallel execution when safe.

## Strategic Boundary

AI_Development_System remains a governance-first control plane.

It must not immediately become a full multi-agent runtime.

Sequential execution remains the default.

Parallel execution is opt-in, planned, approved, conflict-checked, reviewed and QA-gated.

The current safe one-task Codex workflow remains valid and must not be replaced by this plan.

## Non-Goals

- Do not implement a runtime in this phase.
- Do not create automatic self-feeding execution.
- Do not replace the current one-task Codex workflow.
- Do not auto-execute Codex tasks.
- Do not auto-accept agent results.
- Do not weaken Human Owner approval, review or QA gates.
- Do not modify application code.

## Target Architecture

Add a SOP / Multi-Agent Layer over the existing governance layer.

Target components:

- SOP Model
- Agent Work Package
- Multi-Agent Planning
- Parallel Execution Policy
- Agent Result Intake
- Integration Review
- Agent Metrics
- Machine-checkable SOP specs

Relationship to existing layers:

```text
Human Owner approval
-> AI Development System governance
-> SOP / Multi-Agent planning layer
-> bounded Codex or agent work packages
-> review and QA
-> Human Owner acceptance
```

The SOP / Multi-Agent Layer must use existing source-of-truth documents, task lifecycle, prompt lifecycle, Codex lifecycle, review process, QA lifecycle, verification modes, project integration model, foldered integration and spec layer.

## Target Process

```text
Human Owner intent
-> ChatGPT Orchestrator
-> SOP selection
-> task decomposition
-> Agent Work Packages
-> dependency / file-lock check
-> Human Owner approval
-> sequential or parallel execution
-> result intake
-> integration review
-> QA
-> Human Owner acceptance
-> metrics / lessons learned
```

## Required Future Documents

- `ai-system/sop-model.md`
- `ai-system/agent-work-package.md`
- `ai-system/multi-agent-planning.md`
- `ai-system/parallel-execution-policy.md`
- `ai-system/agent-result-intake.md`
- `ai-system/integration-review.md`

These documents must be introduced one bounded evolution task at a time.

## Required Future Project Control Files

- `AI_PROJECT/AGENT_PLAN.md`
- `AI_PROJECT/AGENT_TASKS.md`
- `AI_PROJECT/AGENT_LOCKS.md`
- `AI_PROJECT/AGENT_RESULTS.md`
- `AI_PROJECT/AGENT_METRICS.md`

These files must be added through project-control templates only after the relevant system documents exist and are approved.

## Required Future Specs

- `spec/sops.json`
- `spec/agent-work-package.schema.json`
- `spec/agent-result.schema.json`
- `spec/parallel-policy.json`

Specs must follow the existing `spec/README.md` rule: Markdown remains the operational source of truth unless a later approved evolution task changes that relationship.

## Required Future Tooling

Target MVP:

- `scripts/agent-plan-mvp.py`

The MVP must be dry-run by default.

Allowed MVP behavior:

- validate agent plans;
- detect file-lock conflicts;
- list safe parallel groups;
- generate bounded prompts for review.

Forbidden MVP behavior:

- execute Codex automatically;
- create branches;
- merge changes;
- accept results;
- modify application code;
- bypass review, QA or Human Owner approval.

## Parallel Execution Rules

Parallel execution is allowed only when:

- Human Owner approved the parallel group;
- Agent Work Packages are explicit;
- dependencies are clear;
- `allowed_files` and `locked_files` do not conflict;
- outputs of one package are not required inputs of another package;
- verification mode is explicit;
- integration review is planned;
- rollback or rework path is clear.

Parallel execution is not allowed for:

- unresolved architecture decisions;
- security/auth changes unless explicitly approved and isolated;
- broad refactors;
- AI system behavior changes unless handled as a controlled evolution task;
- overlapping locked files;
- unclear acceptance criteria;
- missing Human Owner approval.

## Phased Implementation Plan

### Phase 0 — Record Plan

Record this master plan and decompose future work into evolution backlog items.

Backlog item: `EVOL-008`.

### Phase 1 — SOP Model

Define what an SOP is in AI_Development_System, how SOPs are selected and how SOPs relate to existing workflow and task lifecycle.

Backlog item: `EVOL-009`.

### Phase 2 — Agent Work Package Standard

Define the required structure for a bounded Agent Work Package, including role, task, dependencies, `allowed_files`, `locked_files`, verification mode, acceptance criteria and result format.

Backlog item: `EVOL-010`.

### Phase 3 — Multi-Agent Planning Workflow

Define how ChatGPT Orchestrator decomposes Human Owner intent into Agent Work Packages without execution.

Backlog item: `EVOL-011`.

### Phase 4 — Parallel Execution Policy

Define when parallel execution is allowed, denied or requires explicit isolation and approval.

Backlog item: `EVOL-012`.

### Phase 5 — Result Intake and Integration Review

Define how agent results are received, checked, combined, reviewed and either accepted, reworked or rejected.

Backlog items: `EVOL-013`.

### Phase 6 — Machine-Checkable SOP Specs

Add specs and schemas for SOPs, Agent Work Packages, agent results and parallel execution policy.

Backlog item: `EVOL-014`.

### Phase 7 — Project Templates

Add project-local planning templates for `AI_PROJECT/AGENT_PLAN.md`, `AI_PROJECT/AGENT_TASKS.md`, `AI_PROJECT/AGENT_LOCKS.md`, `AI_PROJECT/AGENT_RESULTS.md` and `AI_PROJECT/AGENT_METRICS.md`.

Backlog item: `EVOL-015`.

### Phase 8 — Dry-Run Agent Planner MVP

Add `scripts/agent-plan-mvp.py` as a dry-run planner and validator only.

Backlog item: `EVOL-016`.

### Phase 9 — Golden Project Example

Extend the existing golden project with a multi-agent planning example.

Backlog item: `EVOL-017`.

### Phase 10 — Pilot Validation

Run controlled pilot validation and record findings before any runtime decision.

Backlog item: `EVOL-018`.

### Phase 11 — Runtime Decision

Decide whether runtime integration is justified based on pilot evidence, not aspiration.

Backlog item: `EVOL-019`.

## Definition of Done for the Whole Initiative

AI_Development_System can:

- select a SOP;
- decompose a task into Agent Work Packages;
- check dependencies and locked files;
- identify safe parallel groups;
- generate bounded prompts;
- intake agent results;
- run integration review;
- pass QA;
- preserve Human Owner final acceptance;
- record metrics.

## Governance Rules

- One bounded evolution task at a time.
- Human Owner approval remains required for behavior-changing system changes.
- Existing one-task Codex execution remains the default.
- Parallel execution is opt-in only.
- Runtime automation requires a separate future decision.
- Metrics and pilot evidence must inform any runtime decision.

## Current Status

```text
Recorded: yes
Runtime implemented: no
Scripts added: no
Specs added: no
Templates added: no
Existing execution behavior changed: no
Next bounded task: EVOL-009 - Add SOP Model document
```

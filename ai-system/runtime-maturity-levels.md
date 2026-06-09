# Runtime Maturity Levels

Status: Draft  
Version: v0.1.0

## Purpose

This document defines runtime maturity levels for AI_Development_System.

The levels separate documentation, specifications, dry-run planning, manual orchestration and future runtime automation so runtime discussions do not collapse into one ambiguous concept.

Runtime maturity levels do not authorize runtime behavior by themselves.

## Current Position

Current project level:

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

L4 and higher are future/not approved. Moving beyond L3 requires explicit Human Owner approval and a bounded evolution task.

## Global Rules

- Human Owner approval is required for progression beyond approved manual orchestration.
- Runtime automation remains forbidden until a later explicit decision changes it.
- Automatic Codex execution is forbidden.
- Automatic multi-agent execution is forbidden.
- Automatic branch/worktree lifecycle is forbidden.
- Automatic merge is forbidden.
- Automatic acceptance is forbidden.
- Automatic QA/review closure is forbidden.
- Candidate parallel groups remain informational until approved under the relevant policy.
- Each level must preserve the safety boundaries of all lower levels.

## Level Summary

| Level | Name | Status |
| --- | --- | --- |
| L0 | Documentation only | Historical baseline |
| L1 | Machine-checkable specs | Implemented |
| L2 | Dry-run planning | Implemented |
| L3 | Manual multi-agent orchestration | Current |
| L4 | Assisted execution | Future / Not approved |
| L5 | Controlled runtime | Future / Not approved |
| L6 | Autonomous runtime | Future / Not approved |

## L0 — Documentation Only

Purpose:

Define the AI Development System as source-of-truth Markdown documents, roles, rules, workflows and lifecycle governance.

Allowed capabilities:

- human-readable roles, rules and process documents;
- structured task, prompt, review and lifecycle documentation;
- manual Human Owner decisions;
- manual Codex prompt preparation and review.

Forbidden capabilities:

- machine-enforced planning validation;
- automatic execution;
- automatic merge;
- automatic acceptance;
- runtime orchestration.

Required safety gates:

- Human Owner approval for system changes;
- documented scope and acceptance criteria before implementation;
- review before Done.

Evidence required to enter this level:

- core system documents exist;
- role and workflow boundaries are documented;
- changelog records system evolution.

Exit/readiness criteria for L1:

- repeated document drift or consistency risk is visible;
- stable entities are ready for machine-checkable representation;
- Markdown remains the operational source of truth.

## L1 — Machine-Checkable Specs

Purpose:

Represent stable system entities in machine-checkable specs while keeping Markdown as operational authority.

Allowed capabilities:

- JSON/YAML specs for roles, modes, lifecycle states, verification modes, SOPs and contracts;
- schema validation by manual command or future CI;
- consistency checks that do not execute project work.

Forbidden capabilities:

- generated runtime behavior from specs;
- automatic Codex execution;
- automatic merge;
- automatic acceptance;
- specs overriding Markdown source-of-truth documents.

Required safety gates:

- explicit source-of-truth relationship between specs and Markdown;
- Human Owner approval for new behavior-changing specs;
- changelog entry for spec layer changes.

Evidence required to enter this level:

- stable documents exist for the represented entities;
- schemas or spec inventories are reviewable;
- validation can run without modifying application code.

Exit/readiness criteria for L2:

- SOP and Agent Work Package concepts are documented;
- project-local planning files can be represented;
- dry-run validation can add value without enabling execution.

## L2 — Dry-Run Planning

Purpose:

Validate and inspect SOP-guided agent planning without executing agents or changing application code.

Allowed capabilities:

- dry-run planning;
- Agent Work Package generation and validation;
- dependency-aware candidate parallel group listing;
- lock conflict checks;
- bounded prompt draft generation for review;
- planning fixture validation.

Forbidden capabilities:

- automatic Codex execution;
- automatic multi-agent execution;
- branch/worktree automation;
- automatic merge;
- automatic acceptance;
- automatic QA/review closure;
- treating candidate parallel groups as executable groups.

Required safety gates:

- Human Owner approval remains required before any execution;
- candidate groups remain informational only;
- validation must preserve dry-run/reporting boundaries;
- runtime decision remains `DEFERRED`.

Evidence required to enter this level:

- SOP Model exists;
- Agent Work Package standard exists;
- Multi-Agent Planning workflow exists;
- Parallel Execution Policy exists;
- dry-run helper exists;
- golden project and planning fixtures validate expected behavior.

Exit/readiness criteria for L3:

- dependency-aware planning is reliable;
- dry-run planning validation tests pass;
- manual orchestration steps are defined;
- result intake and integration review are repeatable manually;
- no critical safety boundary violations are found.

## L3 — Manual Multi-Agent Orchestration

Source document:

```text
manual-orchestration.md
```

Purpose:

Coordinate multi-agent planning manually while keeping all execution, result intake, integration review and Human Owner approval explicit and human-controlled.

Allowed capabilities:

- create or select an agent plan;
- validate an agent plan;
- list ready Agent Work Package candidates;
- manually select the next ready Agent Work Package;
- manually assign an Agent Work Package to a logical or external agent;
- manually assign or prepare bounded prompt packages;
- manually record Role-to-Agent Assignment records;
- manually record submitted agent results;
- manually run Agent Result Intake;
- manually run Integration Review;
- manually record status changes, decisions, follow-ups and blocked states;
- manually route rework, QA and Human Owner decisions.

Forbidden capabilities:

- automatic Codex execution;
- automatic multi-agent execution;
- automatic agent dispatch;
- automatic branch/worktree lifecycle;
- automatic file modification by orchestration tooling;
- automatic merge;
- automatic acceptance;
- automatic QA/review closure;
- bypassing Human Owner approval.

Required safety gates:

- Human Owner approval for execution scope;
- explicit `allowed_files`, `locked_files`, dependencies and verification mode;
- result intake before integration review;
- integration review before QA handoff or parent-task acceptance;
- Human Owner final acceptance.

Evidence required to enter this level:

- L2 validation is stable;
- EVOL-023 defines manual orchestration mode;
- manual orchestration has clear state transitions;
- at least one pilot scenario demonstrates manual orchestration;
- pilots show that manual orchestration is repeatable.

Exit/readiness criteria for L4:

- at least 2-3 pilot scenarios are recorded;
- Agent Work Package state tracking is stable;
- result intake schema is reliable enough for review;
- CI checks exist for specs, templates and planning fixtures;
- no critical safety boundary violations are found;
- manual orchestration is proven repeatable;
- Human Owner explicitly approves a bounded assisted-execution experiment.

## L4 — Assisted Execution

Purpose:

Describe a future mode where tooling may assist execution steps while a human remains in control of approvals, dispatch and acceptance.

Status:

Future / Not approved.

Allowed capabilities:

- none in the current system;
- future proposal may describe assisted prompt handoff or guided execution after approval.

Forbidden capabilities:

- enabling assisted execution without a new approved evolution task;
- automatic execution without Human Owner approval;
- automatic merge;
- automatic acceptance;
- bypassing review or QA.

Required safety gates:

- explicit Human Owner approval for an experiment;
- rollback/rework plan;
- narrow allowed files;
- manual review and QA;
- documented success and stop criteria.

Evidence required to enter this level:

- L3 is implemented and validated;
- pilot evidence shows manual orchestration is repeatable;
- risks and safety controls are documented.

Exit/readiness criteria for L5:

- assisted execution proves useful without boundary violations;
- adapter contracts are reviewed;
- Human Owner approves controlled runtime exploration.

## L5 — Controlled Runtime

Purpose:

Describe a future controlled runtime that may orchestrate bounded execution under strict policy, review and approval gates.

Status:

Future / Not approved.

Allowed capabilities:

- none in the current system;
- future controlled runtime behavior requires a separate approved decision and bounded implementation task.

Forbidden capabilities:

- automatic acceptance;
- automatic merge without an approved gate model;
- unbounded task execution;
- bypassing Human Owner approval;
- runtime behavior based only on roadmap text.

Required safety gates:

- approved runtime decision;
- adapter contracts;
- auditable state transitions;
- isolation and rollback model;
- mandatory review, QA and Human Owner acceptance.

Evidence required to enter this level:

- L4 evidence is successful;
- assisted execution does not violate safety boundaries;
- operational risks are understood and mitigated.

Exit/readiness criteria for L6:

- controlled runtime is proven safe across multiple pilots;
- Human Owner explicitly approves autonomous-runtime research;
- governance and rollback rules are mature.

## L6 — Autonomous Runtime

Purpose:

Describe a possible future autonomous runtime where the system can plan, execute, review and adapt with minimal human intervention.

Status:

Future / Not approved.

Allowed capabilities:

- none in the current system.

Forbidden capabilities:

- autonomous execution;
- autonomous merge;
- autonomous acceptance;
- autonomous closure of QA/review findings;
- autonomous changes to safety boundaries.

Required safety gates:

- not defined for current use;
- must require explicit Human Owner approval and a separate governance model before any experiment.

Evidence required to enter this level:

- L5 is safe and proven;
- strong audit, rollback, policy and oversight mechanisms exist;
- Human Owner explicitly approves research or experimentation.

Exit/readiness criteria:

- no next level is defined.

## Current Decision

AI_Development_System current maturity level is:

```text
L3 — Manual multi-agent orchestration
```

L3 readiness decision:

```text
APPROVED FOR MANUAL-ONLY MATURITY
```

Runtime execution remains:

```text
DEFERRED
```

L3 does not enable automatic execution. It only recognizes that the system has enough documented process, validation, result intake, integration review and pilot evidence to coordinate Agent Work Packages manually under Human Owner control.

L4, L5 and L6 are not approved and must not be implemented without future explicit Human Owner approval.

## L3 Readiness Assessment

Decision:

```text
L3 — Manual multi-agent orchestration is ready to declare as the current maturity level.
```

Criteria reviewed:

| Criterion | Assessment |
| --- | --- |
| `EVOL-019` through `EVOL-026` are Done | Met |
| Runtime is deferred | Met |
| Dependency-aware planning exists | Met |
| Planning fixtures and validation tests exist | Met |
| CI and local validation exist | Met |
| Manual orchestration mode is documented | Met |
| Hardened Agent Result schema exists | Met |
| Integration Review handoff exists | Met |
| Pilot validation includes documentation-only, small code/tooling and multi-agent parallel planning cases | Met |
| Pilot records distinguish dry-run validation, manual simulation and future runtime | Met |
| Human Owner approval remains required | Met |

Evidence:

- `scripts/agent-plan-mvp.py` supports dependency-aware dry-run validation and candidate group reporting.
- `scripts/validate-agent-plan-fixtures.py` covers dependency graph behavior, missing dependencies, cycles, blocked packages and accepted-prerequisite unlocking.
- `scripts/validate-system.py` runs read-only validation for docs, specs, templates, fixtures and the golden project.
- `manual-orchestration.md` defines L3 manual-only flow, artifacts, allowed operations, forbidden automation and Human Owner gates.
- `role-agent-assignment.md` defines manual assignment records for ready Agent Work Packages and logical agents.
- `agent-result-intake.md` defines the hardened Agent Result schema for manual intake.
- `integration-review.md` defines manual integration review handoff and blocking conditions.
- `evolution/sop-multi-agent-pilot-validation.md` records expanded pilot evidence across three scenario types.

Restrictions after declaring L3:

- automatic Codex execution remains forbidden;
- automatic multi-agent execution remains forbidden;
- branch/worktree lifecycle automation remains forbidden;
- automatic file modification by orchestration tooling remains forbidden;
- automatic merge remains forbidden;
- automatic acceptance remains forbidden;
- automatic QA/review closure remains forbidden;
- candidate parallel groups remain informational until Human Owner approval;
- L4+ remains future/not approved.

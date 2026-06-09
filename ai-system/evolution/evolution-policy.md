# System Evolution Policy

Status: Draft  
Version: v0.1.0

## Purpose

This policy defines what the AI Development System may and may not do when evolving itself.

The goal is to allow planned self-improvement while preventing uncontrolled self-modification, scope expansion or governance bypass.

## Core Rule

```text
AI may initiate, analyze, propose and prepare system evolution.
Human Owner approves whether system evolution becomes authoritative.
```

## Allowed Self-Evolution Actions

AI roles may:

- identify gaps and inconsistencies;
- run system health checks;
- add observations to the evolution backlog;
- draft roadmap updates;
- draft AI System Change Proposals;
- prepare bounded evolution tasks;
- prepare documentation changes inside explicit allowed files;
- recommend verification steps;
- recommend review outcomes;
- update changelog drafts after approved changes.

## Restricted Actions

AI roles must not:

- merge system changes without Human Owner approval;
- remove Human Owner approval gates;
- rewrite the evolution policy to grant itself more authority without explicit approval;
- silently expand allowed files;
- modify product code while executing a system evolution task unless explicitly in scope;
- turn every observation into an immediate system change;
- create recursive evolution loops without a closure condition;
- claim a change is validated without evidence;
- treat Draft documentation as production-proven without pilot evidence.

## Human Owner Authority

Human Owner approval is required for:

- changes to roles, authority or ownership;
- changes to lifecycle states or allowed operations;
- changes to review, QA or approval rules;
- changes to system prompt behavior;
- changes to security, privacy or data-handling policy;
- roadmap priority changes;
- versioned system releases;
- acceptance of major AICP proposals.

## Low-Risk Documentation Changes

The system may prepare low-risk documentation improvements without a full AICP when all of the following are true:

- the change does not alter authority, lifecycle states, approval gates or execution boundaries;
- the change clarifies existing rules rather than creating new rules;
- affected files are explicitly listed;
- changelog impact is none or documentation-only;
- review confirms no behavior change.

Examples:

- fixing broken cross-links;
- adding index entries;
- correcting typos;
- clarifying examples;
- adding missing references to already approved documents.

## AICP Required Changes

An AICP is required when the change affects:

- system behavior;
- governance model;
- role ownership;
- lifecycle states;
- approval gates;
- security/privacy policy;
- system prompt rules;
- integration contract;
- versioning policy;
- machine-checkable source-of-truth definitions.

## Scope Boundary

System evolution tasks must distinguish:

```text
System scope: AI_Development_System rules, docs, prompts, templates and specifications.
Project scope: concrete application work governed by AI_PROJECT and product docs.
```

A system evolution task must not change product implementation unless the Human Owner explicitly requests an integration or pilot task that includes product files.

## Evidence Requirements

System evolution may be based on:

- Human Owner instruction;
- analytical report finding;
- system health-check finding;
- pilot validation result;
- repeated review issue;
- repeated QA issue;
- documented task failure;
- external research or analogous system comparison.

Evidence must be referenced in the proposal, backlog item or task package.

## Verification Requirements

Every system evolution task must define a verification mode.

Minimum verification for documentation-only changes:

- affected documents reviewed for consistency;
- links and index references checked manually or by tool;
- no unresolved placeholders introduced;
- changelog impact assessed.

Additional verification may be required for:

- templates;
- specs;
- scripts;
- security/privacy changes;
- integration workflows;
- pilot validation outcomes.

## Review Requirements

Every behavior-changing system evolution task requires review.

Review must check:

- policy compliance;
- lifecycle consistency;
- Human Owner approval requirements;
- whether AICP is required;
- changelog impact;
- version impact;
- security/privacy impact;
- risk of documentation drift.

## Roadmap Relationship

Evolution work should map to one of:

- existing roadmap item;
- evolution backlog item;
- Human Owner request;
- health-check finding;
- pilot validation finding.

If none applies, the system must propose a roadmap or backlog update before executing the change.

## Closure Rule

A self-evolution item is not closed until:

- outcome is recorded;
- affected documents are updated;
- verification result is recorded;
- review result is recorded when required;
- Human Owner decision is recorded when required;
- changelog is updated when version or behavior changed.

# Lifecycle Governance

Status: Draft  
Version: v0.1.0

## Purpose

This document defines common lifecycle governance for managed entities in the AI Development System.

It does not replace specific lifecycle documents. It defines the shared rules that future lifecycle documents should follow.

## Core Principle

Every managed entity in the AI Development System should have:

- owner;
- source document;
- lifecycle states;
- allowed operations;
- approval rules;
- version impact rules;
- history or changelog rule.

Specific lifecycle documents may add details, but they should not contradict this governance model.

## Managed Entity

A managed entity is any system element whose creation, update, approval, deprecation or removal affects the AI Development System.

Managed entities include:

- roles;
- documents;
- processes;
- tasks;
- decisions;
- prompts;
- reviews;
- QA flows;
- Codex executions;
- improvements;
- knowledge entries;
- experiments.

Application code, product features and infrastructure are not governed by this document directly. They are governed by project documentation and task rules, unless they also change the AI Development System.

## Common Lifecycle States

Managed entities should use these states where applicable:

- `Proposed` - suggested but not approved.
- `Draft` - created for review, not yet accepted as active truth.
- `Active` - accepted and currently used.
- `In Review` - being checked before approval or closure.
- `Experimental` - approved temporarily with success criteria.
- `Deprecated` - still documented but no longer recommended for new use.
- `Archived` - retained for history, not active.
- `Rejected` - reviewed and not accepted.
- `Removed` - deleted from active documentation after approval and reference cleanup.

Specific lifecycle documents may use additional states when needed, but they should map back to these common states.

## Common Lifecycle Operations

Managed entities should define which roles may perform these operations:

- Read;
- Create;
- Update;
- Review;
- Approve;
- Reject;
- Deprecate;
- Archive;
- Remove;
- Roll back.

If an operation can change system behavior, it must require Human Owner approval.

## Ownership Model

Every managed entity should have:

- a responsible role;
- an approving authority;
- a source document;
- a review path.

Default ownership:

- Human Owner approves system-level decisions.
- ChatGPT Orchestrator routes the request and prepares prompts or review outputs.
- AI System Maintainer owns AI Development System evolution.
- Technical Writer AI may help with documentation clarity.
- Codex Executor applies approved repository changes only within explicit scope.

Specific lifecycle documents may assign more precise ownership.

## Approval Rules

Human Owner approval is required for:

- adding a new managed entity type;
- changing system rules;
- changing role responsibilities;
- changing workflow or lifecycle states;
- deleting or deprecating active system elements;
- applying an AI System Change Proposal;
- accepting an experiment as permanent;
- rolling back an applied system change.

AI roles may recommend decisions, but they do not approve system changes.

## AICP Relationship

An AI System Change Proposal is required when a change affects:

- AI Development System behavior;
- role definitions;
- lifecycle rules;
- workflow;
- prompt requirements;
- review process;
- approval process;
- system version.

Small wording corrections that do not change behavior may be handled as patch changes, but they should still be recorded when they affect source-of-truth documents.

## Version Impact Rules

Use `MAJOR.MINOR.PATCH`.

- Patch: wording, formatting or clarification that does not change behavior.
- Minor: new document, new lifecycle, new rule, new workflow step or new managed entity type.
- Major: significant operating model, hierarchy, approval model or governance change.

When uncertain, choose the higher impact and ask the Human Owner to confirm.

## Audit and History Rules

System changes should leave enough history to understand:

- what changed;
- why it changed;
- who approved it;
- which files were affected;
- whether the change was experimental, applied, rejected or rolled back.

Use:

- `improvement-log.md` for observed process problems and improvement ideas;
- AICP for proposed system changes;
- `system-changelog.md` for applied system changes and version history;
- specific lifecycle documents for entity-specific history rules.

## Future Lifecycle Documents

Future lifecycle documents should include:

- purpose;
- governed entity;
- source-of-truth document;
- lifecycle states;
- allowed operations;
- owner role;
- approval rules;
- review rules;
- version impact rules;
- audit or history rule;
- relationship to AICP;
- relationship to `system-changelog.md`.

Future lifecycle documents should reference this document instead of redefining common governance from scratch.

## Boundary Rules

Lifecycle governance must not be used to bypass Human Owner control.

Lifecycle governance must not be used to combine unrelated changes.

Lifecycle governance must not turn every small clarification into a heavy process. The amount of process should match the risk and version impact of the change.

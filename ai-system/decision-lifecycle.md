# Decision Lifecycle

Status: Draft
Version: v0.1.0

## Purpose

This document defines how managed decisions are proposed, clarified, reviewed, approved, reworked, rejected, deferred, tested, applied, superseded, rolled back and archived inside the AI Development System.

It applies the shared governance model from `/ai-system/lifecycle-governance.md` to Human Owner decisions.

## Governed Entity

A managed decision is any decision that affects product direction, AI Development System behavior, repository source-of-truth documents, workflow, roles, lifecycle states, prompt requirements, review rules, approval rules, system version or execution scope.

Managed decisions include:

- product direction and scope decisions;
- architecture and workflow decisions;
- AI Development System evolution decisions;
- AICP decisions;
- experiment decisions;
- acceptance, rework, rejection and deferral decisions;
- rollback and supersession decisions.

Informal preferences, brainstorming and temporary comments are not managed decisions unless they affect source-of-truth behavior or repository work.

## Source of Truth

Default source-of-truth locations for managed decisions are:

- `/ai-system/decision-process.md` for decision statuses and decision record format;
- `/ai-system/human-interaction.md` for Human Owner decision control;
- AICP documents or AICP sections for AI Development System change decisions;
- `/ai-system/system-changelog.md` for applied system decision history;
- affected source-of-truth documents in `/ai-system` or `/docs`;
- git history for exact applied repository changes.

If a decision and source document conflict, report the conflict before applying the decision.

## Decision Lifecycle States

Managed decisions should use these states where applicable:

- `Proposed` - decision need or option has been suggested.
- `Draft` - decision record, options or recommendation exists but is not ready for final decision.
- `In Review` - options, risks, scope and affected documents are being checked.
- `Approved` - Human Owner accepted the decision.
- `Rework Requested` - Human Owner or review requires changes before acceptance.
- `Rejected` - Human Owner rejected the decision or recommendation.
- `Deferred` - postponed without rejection.
- `Experimental` - accepted temporarily with success criteria and review conditions.
- `Applied` - approved decision has been reflected in repository files, process or execution state.
- `Superseded` - replaced by a newer decision.
- `Rolled Back` - applied decision was reversed through an approved rollback.
- `Archived` - retained for history, not active decision handling.

Decision keywords in Human Owner-facing control may remain `APPROVED`, `REWORK`, `REJECTED`, `DEFERRED` and `EXPERIMENT` as defined in `/ai-system/decision-process.md` and `/ai-system/human-interaction.md`.

## Decision Operations

## Read

Goal: understand an existing decision before relying on it or changing it.

Read should identify:

- decision status;
- context;
- options considered;
- Human Owner decision;
- reason;
- impact;
- documents to update;
- related AICP, changelog entry or commit when available.

## Propose

Goal: present a decision option or recommendation.

Any AI role may propose a decision inside its responsibility area.

A proposal should include context, options, recommendation, expected impact, risks and affected documents.

## Clarify

Goal: resolve missing context before review or approval.

Clarification should ask only for information needed to make or apply the decision safely.

Clarification must not be treated as approval.

## Review

Goal: check whether the decision is safe and ready for Human Owner action.

Decision review should check:

- whether the decision is inside scope;
- which documents or tasks are affected;
- whether AICP is required;
- whether risks are explicit;
- whether version impact is understood;
- whether the decision conflicts with existing source-of-truth documents;
- whether application path and rollback path are clear.

## Approve

Goal: accept the decision.

Only the Human Owner approves managed decisions.

AI roles and Codex may recommend approval, but they do not approve decisions.

Approval should be explicit when the decision changes repository files, product behavior, AI Development System behavior, roles, workflow, approval rules or system version.

## Request Rework

Goal: return a decision proposal for correction.

Rework should identify:

- what is unclear or incorrect;
- which options or risks need revision;
- what evidence or source documents are missing;
- whether the decision can return to review after rework.

## Reject

Goal: mark a proposed decision as not accepted.

Rejected decisions should record why they were rejected and whether follow-up action is needed.

Rejected decisions must not be applied as source-of-truth behavior.

## Defer

Goal: postpone a decision without rejecting it.

Deferred decisions should record:

- reason;
- condition for resuming;
- owner or next reviewer;
- whether evidence should continue to be collected.

## Start Experiment

Goal: accept a decision temporarily for testing.

Experimental decisions should define:

- hypothesis;
- scope;
- duration or review point;
- success criteria;
- failure criteria;
- rollback or adoption path.

Experiments require Human Owner approval.

## Apply

Goal: reflect an approved decision in repository files, process, task state or execution state.

Application should update affected source-of-truth documents and changelog entries when needed.

Codex may apply approved repository changes, but only within explicit scope.

## Supersede

Goal: replace an earlier decision with a newer decision.

Supersession should record:

- old decision;
- new decision;
- reason for replacement;
- affected documents;
- whether applied changes need update or rollback.

Superseding an active source-of-truth decision requires Human Owner approval.

## Roll Back

Goal: reverse an applied decision after it causes problems or is no longer accepted.

Rollback requires Human Owner approval when it affects source-of-truth documents, product behavior, system behavior, repository state or history.

Rollback should preserve audit history and should not erase the fact that the decision was made and applied.

## Archive

Goal: retain inactive decision history.

Archived decisions are not active guidance unless explicitly restored or referenced as history.

Archival should preserve enough context to understand why the decision is no longer active.

## Ownership Model

Default ownership:

- Human Owner owns final decisions and approval authority.
- ChatGPT Orchestrator frames decision context, options, risks and affected documents.
- AI System Maintainer owns AI Development System decision analysis and AICP-related decisions.
- Relevant domain role proposes and explains decisions inside its responsibility area.
- Codex Executor applies approved repository changes only within explicit scope.

No AI role and no Codex execution may approve managed decisions.

## Relationship to Decision Process

`/ai-system/decision-process.md` defines the core decision principle, decision statuses and decision record format.

Decision Lifecycle extends that document by defining states, operations, revision, supersession, rollback, archival and history rules.

Use the decision record format from `/ai-system/decision-process.md` when recording formal decisions:

```text
Decision ID
Context
Options
Decision
Reason
Impact
Documents to Update
```

## Relationship Between Decisions, Documents, AICP, Changelog and Git

Use each record for a distinct purpose:

- decisions record what the Human Owner chose and why;
- affected source-of-truth documents record the active rule, scope or behavior;
- AICP records proposed AI Development System behavior changes, evidence, risks and version impact;
- `system-changelog.md` records applied AI Development System changes;
- git history records exact repository diffs and commits.

A decision that changes active behavior should be traceable from decision context to affected documents, changelog entry and commit when repository files change.

## Approval Rules

Human Owner approval is required for decisions that:

- approve or reject repository changes;
- change product scope or behavior;
- change AI Development System behavior;
- change roles, workflow, lifecycle states, prompt requirements or review rules;
- accept major review risk;
- start or adopt an experiment;
- supersede an active source-of-truth decision;
- roll back an applied decision;
- close a decision as accepted when it changes active behavior.

AI roles may recommend decisions, but the Human Owner decides.

## AICP Relationship

An AICP is required when a decision affects:

- AI Development System behavior;
- role definitions or responsibilities;
- lifecycle governance;
- workflow or approval process;
- prompt requirements;
- review, QA or Codex execution rules;
- system version;
- permanent adoption of an experiment;
- rollback of an applied system change.

An AICP is not required for ordinary product or task decisions unless they change the AI Development System itself.

## Revision Rules

Decision proposals may be revised while they are `Draft`, `In Review` or `Rework Requested`.

Revisions should preserve the reason for material changes when the decision affects source-of-truth behavior.

Approved decisions should not be silently edited. If meaning changes after approval, create a superseding decision or an approved correction.

## Supersession Rules

A decision may be superseded when a newer approved decision replaces it.

Supersession should update affected documents so users can identify the active decision.

Superseded decisions should remain traceable for history and rollback context.

## Archival Rules

Archive decisions when they are no longer active but remain useful for history.

Before archiving, confirm:

- active documents no longer depend on the decision, or clearly reference it as history;
- superseding or replacement decision is documented when needed;
- rollback or experiment closure is complete when applicable.

## Version Impact Rules

Use `MAJOR.MINOR.PATCH` for AI Development System decisions.

- Patch: wording, clarification or decision record correction without behavior change.
- Minor: new decision lifecycle document, new decision state, new approval rule, new decision record requirement or meaningful governance addition.
- Major: significant change to Human Owner authority, approval model, operating model, role hierarchy or governance model.

When uncertain, choose the higher impact and ask the Human Owner to confirm.

## Audit and History Rules

Decision history should preserve:

- decision ID or title when available;
- context;
- options considered;
- recommendation if any;
- Human Owner decision;
- reason;
- impact;
- affected documents;
- related AICP when applicable;
- changelog entry when applied to AI Development System;
- git commit when repository files changed;
- supersession, rollback or archival status.

## Relationship to Lifecycle Governance

This document specializes `/ai-system/lifecycle-governance.md` for managed decisions.

If this document and lifecycle governance conflict, report the conflict and require Human Owner approval before changing behavior.

## Relationship to Document Lifecycle

Decisions that affect source-of-truth documents must respect `/ai-system/document-lifecycle.md` for documentation status, review, approval, index updates, archival, removal and rollback.

## Relationship to Process Lifecycle

Decision Lifecycle is a managed process and must respect `/ai-system/process-lifecycle.md`.

Changes to decision states, operations, approval rules, supersession rules or archival rules are process changes and may require Human Owner approval and AICP.

## Relationship to Change Lifecycle

Decisions that change the AI Development System should follow `/ai-system/change-lifecycle.md`.

AICP, changelog, verification, rollback and closure rules apply when a decision becomes a managed system change.

## Boundary Rules

Decision lifecycle must not be used to bypass Human Owner authority.

Decision lifecycle must not allow AI roles or Codex to approve decisions.

Decision lifecycle must not turn informal discussion into binding decisions unless the Human Owner explicitly approves the decision.

Decision lifecycle must preserve traceability from decision to affected documents and repository history when changes are applied.

# Change Lifecycle

Status: Draft
Version: v0.1.0

## Purpose

This document defines how managed system changes are observed, proposed, drafted, reviewed, approved, applied, verified, reworked, rolled back, closed and archived inside the AI Development System.

It applies the shared governance model from `/ai-system/lifecycle-governance.md` to AI Development System change control.

## Governed Entity

A managed system change is any change that affects AI Development System behavior, source-of-truth documentation, roles, workflow, lifecycle rules, prompt requirements, review rules, approval rules, system version or governance model.

Managed system changes include:

- new or changed lifecycle documents;
- role additions, edits, splits, merges, deprecations or removals;
- workflow or process changes;
- prompt package requirement changes;
- review, QA or Codex execution rule changes;
- language, documentation or governance policy changes;
- rollback of applied system changes.

Application features, product requirements and infrastructure tasks are not managed system changes unless they also change the AI Development System.

## Source of Truth

Default source-of-truth documents for managed system changes are:

- `/ai-system/change-process.md` for the high-level system evolution flow and AICP template;
- `/ai-system/improvement-log.md` for observed process problems and improvement ideas;
- AICP documents or AICP sections for proposed system changes;
- `/ai-system/system-changelog.md` for applied system version history;
- git history for exact repository diffs and commits;
- relevant lifecycle, role, rule, workflow or prompt documents affected by the change.

If these sources conflict, report the conflict before applying or accepting a change.

## Change Lifecycle States

Managed system changes should use these states where applicable:

- `Observed` - problem, risk or improvement idea has been noticed.
- `Proposed` - a change has been suggested but not drafted in full.
- `Drafted` - AICP, prompt or change plan exists for review.
- `In Review` - proposal or result is being checked for scope, safety and consistency.
- `Approved` - Human Owner approved the change or execution prompt.
- `Deferred` - postponed without rejection.
- `Rejected` - reviewed and not accepted.
- `Applied` - approved repository change has been made.
- `Verified` - applied change passed required review or checks.
- `Rework Required` - review found issues that must be corrected.
- `Rolled Back` - applied change was reverted through an approved rollback.
- `Closed` - change is complete, rejected, deferred intentionally or otherwise resolved.
- `Archived` - retained for history, not active handling.

Specific documents may use shorter state labels, but they should map back to these states.

## Change Operations

## Observe

Goal: record a process problem, risk or improvement idea.

Observations should be recorded in `/ai-system/improvement-log.md` when they may indicate a recurring system issue.

A single unclear task does not automatically require a system change.

## Analyze

Goal: understand whether a system change is justified.

Analysis should check:

- whether the problem repeats;
- whether clarification is enough;
- whether the change improves control, quality or speed;
- which source documents are affected;
- whether the change adds more complexity than value.

## Draft AICP

Goal: prepare an AI System Change Proposal when system behavior may change.

AICP should include:

- problem;
- evidence;
- root cause;
- proposed change;
- affected files;
- expected benefit;
- risks;
- decision;
- version impact.

The template in `/ai-system/change-process.md` is the source format.

## Review

Goal: check the proposed or applied change before acceptance.

Change review should verify:

- scope control;
- consistency with lifecycle governance;
- consistency with affected lifecycle documents;
- Human Owner approval requirements;
- AICP requirement;
- version impact;
- changelog impact;
- rollback risk;
- whether unrelated changes were mixed in.

## Approve

Goal: authorize a system change or its execution.

Only the Human Owner approves system changes.

AI roles may recommend `APPROVED`, `REWORK`, `REJECTED`, `DEFERRED` or `EXPERIMENT`, but they do not make the final decision.

## Defer

Goal: postpone a change without rejecting it.

Deferred changes should record:

- reason;
- condition for resuming;
- owner or next reviewer;
- whether evidence should continue to be collected.

## Reject

Goal: close a proposed change as not accepted.

Rejection should record why the change was rejected and whether any observation remains open.

Rejected changes must not be applied as source-of-truth behavior.

## Apply

Goal: make the approved repository change.

Application should happen through a bounded task or Codex prompt with:

- source documents;
- scope;
- out of scope;
- allowed files;
- forbidden actions;
- acceptance criteria;
- expected output;
- review instructions.

Applied changes must update relevant source documents and `system-changelog.md` when system behavior changes.

## Verify

Goal: confirm that an applied change is complete, consistent and safe to use.

Verification should check:

- changed files match allowed files;
- acceptance criteria are satisfied;
- affected indexes and status summaries are updated;
- `system-changelog.md` records the change;
- version impact is consistent with the change;
- Human Owner approval is preserved;
- AICP requirements were followed;
- no unrelated files or behavior were changed;
- review findings are resolved or explicitly accepted.

## Request Rework

Goal: correct approved review findings after a proposal or applied result is insufficient.

Rework must be narrower than the original change.

Rework should identify:

- review findings;
- severity or risk;
- allowed files;
- forbidden actions;
- expected correction;
- acceptance criteria.

## Roll Back

Goal: revert an applied system change after it causes problems or is rejected after application.

Rollback requires Human Owner approval when it affects source-of-truth documentation, system behavior, version history or active repository state.

Rollback should be handled as a bounded task or Codex prompt and should not include unrelated fixes unless explicitly approved.

Rollback should record:

- change being rolled back;
- reason;
- files affected;
- version or commit reference when available;
- verification performed;
- follow-up work if rollback is partial.

## Close

Goal: finish active handling of the change.

A change may be closed when:

- it was applied and verified;
- it was rejected;
- it was deferred with clear resume conditions;
- it was rolled back and follow-up state is clear;
- it was converted into another tracked change.

Closed changes should have enough history to explain the final decision.

## Archive

Goal: retain inactive change history.

Archived changes are not active work. They may be used for audit, lessons learned, future proposals or rollback context.

## Relationship Between Logs, AICP, Changelog and Git

Use each record for a distinct purpose:

- `improvement-log.md` records observed problems and improvement ideas before they become approved system changes.
- AICP records proposed system behavior changes, evidence, risks, affected files, Human Owner decision and version impact.
- `system-changelog.md` records applied AI Development System changes and version history.
- git history records exact file diffs, commit messages and commit hashes.

A complete system change should be traceable from observation or request, through proposal and approval, to applied files, changelog entry and commit.

Not every change starts in the improvement log. A direct Human Owner request may start at proposal or approval, but system behavior changes still require AICP discipline unless the task is only a non-behavioral patch.

## Verification Criteria

After applying a system change, verify:

- source documents were updated within approved scope;
- indexes and operating model status were updated when needed;
- changelog entry exists for applied system behavior changes;
- no forbidden files were changed;
- no unrelated changes were mixed in;
- review or checks passed;
- version impact matches `MAJOR.MINOR.PATCH` rules;
- Human Owner decision is reflected where required;
- rollback path is understandable.

## Rollback Rules

Rollback is required or should be considered when:

- applied change breaks the operating model;
- source-of-truth documents contradict each other;
- Human Owner rejects an applied result and requests reversal;
- review finds critical issues that cannot be corrected safely with narrow rework;
- experiment fails and should not become permanent behavior.

Rollback must preserve audit history. Do not erase the fact that the change was attempted.

## Closure Criteria

A managed system change can be closed when:

- final state is `Verified`, `Rejected`, `Deferred`, `Rolled Back` or intentionally archived;
- Human Owner decision is clear when required;
- changelog and affected indexes are updated when the change was applied;
- remaining risks or follow-up tasks are documented;
- no active review findings remain unresolved without explicit Human Owner decision.

## Approval Rules

Human Owner approval is required for:

- applying system behavior changes;
- changing roles, workflow, lifecycle states, approval rules or prompt requirements;
- accepting major review risk;
- applying or accepting rollback;
- closing an applied change as accepted;
- adopting an experiment as permanent.

AI roles may recommend actions, but the Human Owner decides.

## AICP Relationship

An AICP is required when a change affects:

- AI Development System behavior;
- role definitions or responsibilities;
- lifecycle governance;
- workflow or approval process;
- prompt requirements;
- review, QA or Codex execution rules;
- system version;
- permanent adoption of an experiment;
- rollback of an applied system change.

An AICP is not required for narrow wording, formatting, link or index corrections that do not change behavior, but applied source-of-truth updates should still be traceable through changelog or git history when appropriate.

## Version Impact Rules

Use `MAJOR.MINOR.PATCH`.

- Patch: wording, formatting, link correction or clarification without behavior change.
- Minor: new source-of-truth document, lifecycle document, rule, template, workflow step or meaningful process addition.
- Major: significant operating model, approval model, role hierarchy, governance model or workflow change.

When uncertain, choose the higher impact and ask the Human Owner to confirm.

## Audit and History Rules

System change history should preserve:

- observed problem or Human Owner request;
- evidence and root cause when available;
- proposed change;
- affected files;
- Human Owner decision;
- version impact;
- applied files and commit reference;
- verification result;
- rollback or closure decision.

Use:

- `improvement-log.md` for observations;
- AICP for proposals and decisions;
- `system-changelog.md` for applied version history;
- git history for exact diffs and commits.

## Relationship to Lifecycle Governance

This document specializes `/ai-system/lifecycle-governance.md` for managed system changes.

If this document and lifecycle governance conflict, report the conflict and require Human Owner approval before changing behavior.

## Relationship to Document Lifecycle

System changes usually create or update source-of-truth documents.

When a system change affects documentation, it must respect `/ai-system/document-lifecycle.md` for documentation status, review, approval, index updates, archival, removal and rollback.

## Relationship to Process Lifecycle

Change Lifecycle is a managed process and must respect `/ai-system/process-lifecycle.md`.

Changes to change states, operations, approval rules, verification rules, rollback rules or closure rules are process changes and may require Human Owner approval and AICP.

## Relationship to Task Lifecycle

Applying a system change should be represented as a managed task or prompt package when repository files change.

Definition of Ready and Definition of Done from `/ai-system/task-format.md` should be respected through `/ai-system/task-lifecycle.md`.

## Relationship to Codex Lifecycle

When Codex applies a system change, execution must follow `/ai-system/codex-lifecycle.md`.

Codex reports results; review checks the result; Human Owner accepts, rejects, requests rework or approves rollback.

## Boundary Rules

Change lifecycle must not be used to bypass Human Owner control.

Change lifecycle must not bypass AICP requirements for behavior-changing system updates.

Change lifecycle must not combine unrelated system evolution, product, implementation or infrastructure changes unless explicitly approved.

Change lifecycle must preserve traceability from decision to applied files and history.

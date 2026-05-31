# Experiment Lifecycle

Status: Draft
Version: v0.1.0

## Purpose

This document defines how experiments are proposed, drafted, reviewed, approved, started, monitored, evaluated, adopted, rejected, rolled back and archived inside the AI Development System.

Experiments need explicit hypotheses, success criteria, evaluation, adoption or rejection rules and rollback plans before they can safely affect the AI Development System.

## Governed Entity

A managed experiment is a timeboxed and explicitly approved trial of a change, practice, prompt, process, role behavior, template or lifecycle adjustment whose outcome is uncertain and must be evaluated before permanent adoption.

An experiment is not permanent system behavior until it is evaluated and adopted through the required approval path.

## What Counts as an Experiment

A change counts as an experiment when:

- the expected result is uncertain;
- the change is intentionally temporary or timeboxed;
- the Human Owner wants evidence before permanent adoption;
- the change may affect future system behavior;
- the change compares a new method against the current method;
- the change has explicit success and failure criteria;
- the change has a rollback or discontinuation plan.

Examples include trying a new Codex prompt package format, testing a new review checklist, piloting a documentation template, trialing a stricter QA gate or evaluating whether a repeated observation should become a rule.

## What Does Not Count as an Experiment

The following do not count as managed experiments by default:

- ordinary task execution with known acceptance criteria;
- one-off implementation choices within approved scope;
- immediate fixes for defects or documentation errors;
- approved permanent changes with no timebox or evaluation plan;
- informal brainstorming or unapproved trial behavior;
- speculative ideas captured as knowledge candidates;
- product feature experiments that belong in product documentation rather than `/ai-system`.

If uncertainty exists but no hypothesis, criteria or rollback plan is defined, the item is a proposal or improvement candidate, not an active experiment.

## Source of Truth

Default source-of-truth documents for experiments are:

- `/ai-system/decision-process.md` for `EXPERIMENT` decision status and Human Owner decision handling;
- `/ai-system/decision-lifecycle.md` for decision states, approval, deferral and archival rules;
- `/ai-system/change-process.md` for experimental system changes;
- `/ai-system/change-lifecycle.md` for applying, verifying, adopting or rolling back managed system changes;
- `/ai-system/knowledge-lifecycle.md` for storing lessons learned from experiments;
- `/ai-system/improvement-log.md` for experiment candidates and post-experiment observations;
- `/ai-system/review-lifecycle.md` for review and re-review of experiment proposals and results;
- `/ai-system/system-changelog.md` for adopted system changes and version history;
- `/ai-system/lifecycle-governance.md` for shared lifecycle governance rules.

If experiment scope conflicts with source documents, Human Owner approval is required before the experiment can start.

## Experiment Lifecycle States

Managed experiments should use these states where applicable:

- `Proposed` - an experiment idea exists but is not yet fully drafted.
- `Drafted` - the experiment proposal is written with hypothesis, scope, criteria and rollback plan.
- `Reviewed` - the proposal was reviewed for safety, clarity, scope and governance consistency.
- `Approved` - the Human Owner approved the experiment before start.
- `Active` - the experiment is running inside its approved scope.
- `Monitoring` - experiment evidence, risks and intermediate signals are being tracked.
- `Evaluation` - results are being compared against success and failure criteria.
- `Adopted` - the experiment is accepted as a permanent or semi-permanent system change.
- `Rejected` - the experiment is not adopted and should not guide future behavior except as a lesson learned.
- `Rolled Back` - active experiment effects were reverted or discontinued.
- `Archived` - experiment records are retained for history and audit.

Specific tools or task records may use shorter labels, but they should map back to these states.

## Allowed Operations

## Propose Experiment

Goal: identify a possible experiment and the reason for testing it.

An experiment proposal may originate from a Human Owner decision, review finding, improvement log entry, repeated issue, knowledge candidate, Codex execution problem or system evolution discussion.

## Draft Experiment Proposal

Goal: create a complete experiment proposal before review.

Drafting does not authorize the experiment to start.

## Review Experiment

Goal: check whether the proposal is safe, clear, evaluable and consistent with governance.

Review should verify hypothesis, scope, affected files or processes, duration, success criteria, failure criteria, risks, rollback plan, Human Owner approval requirements, AICP impact and version impact.

## Approve Experiment

Goal: authorize a drafted and reviewed experiment to start.

Only the Human Owner may approve experiments that affect AI Development System behavior, authority, workflows, prompts, rules, lifecycle documents or risk acceptance.

## Start Experiment

Goal: begin the experiment inside approved scope.

Before start, the proposal must be approved, affected files or processes must be clear, rollback plan must exist, owner and reviewer roles must be assigned, monitoring method must be known and baseline behavior should be recorded where useful.

## Monitor Experiment

Goal: collect evidence while the experiment is active.

Monitoring should track observations, review findings, QA or regression impact, task outcomes, Human Owner feedback, unexpected risks, deviations from scope and early failure signals.

Monitoring must not expand experiment scope without approval.

## Evaluate Experiment

Goal: compare evidence against success and failure criteria.

Evaluation should conclude one of: adopt, adopt with changes, extend timebox with approval, reject, roll back or defer decision because evidence is insufficient.

## Adopt Experiment

Goal: convert a successful experiment into approved system behavior.

Adoption may require updates to rules, prompts, templates, lifecycle documents, process documents, README, changelog or AICP records.

## Reject Experiment

Goal: decide that the experiment should not become active system behavior.

Rejection should record why success criteria were not met, which risks occurred, whether lessons should be captured, whether rollback is required and whether a revised experiment may be proposed later.

## Roll Back Experiment

Goal: revert or discontinue experiment effects when the experiment fails, exceeds scope, creates unacceptable risk or is rejected.

Rollback should follow the approved rollback plan unless the Human Owner approves a different recovery path.

## Archive Experiment

Goal: retain experiment records after adoption, rejection, rollback or closure.

Archived experiment records may be used for audit, knowledge capture, improvement analysis and future experiment design.

## Ownership Model

Default ownership:

- Human Owner approves experiment start, scope changes, risk acceptance, adoption, rejection and rollback decisions.
- ChatGPT Orchestrator drafts proposals, coordinates review, summarizes monitoring evidence and prepares adoption or rollback prompts.
- AI System Maintainer owns governance consistency and system-level safety.
- Technical Writer AI owns documentation, template and changelog consistency.
- Code Reviewer AI reviews code or execution implications when experiments affect repository changes.
- QA Engineer AI reviews QA, regression and validation implications.
- Relevant domain roles own domain-specific experiment correctness.
- Codex Executor applies experiment-related repository changes only through explicit approved task scope.

No role may treat an experiment as permanent system behavior before adoption is approved.

## Experiment Proposal Format

Experiment proposals must use this format:

```text
# Experiment Proposal

Title:

Problem or Opportunity:

Hypothesis:

Proposed Change:

Affected Files or Processes:

Scope:

Out of Scope:

Duration or Review Point:

Success Criteria:

Failure Criteria:

Risks:

Rollback Plan:

Owner Role:

Reviewer Role:

Human Owner Decision:
```

Optional fields may be added only when they clarify evaluation, monitoring or audit.

## Hypothesis Rules

A hypothesis must be testable and specific enough to evaluate.

A good hypothesis should state what change is being tested, what improvement is expected, where the improvement should appear, how evidence will be observed and what comparison or baseline matters.

A vague preference, opinion or goal is not enough to start an experiment.

## Experiment Scope Rules

Experiment scope must define affected files, affected processes, affected roles, allowed changes, forbidden changes, task or time boundaries, whether Codex may modify files and whether Human Owner approval is needed for each execution step.

Experiments must not silently expand beyond approved scope.

## Duration and Timebox Rules

Every experiment must define either a duration, fixed review date, number of tasks or executions, or a specific milestone after which evaluation must happen.

Open-ended experiments are not allowed unless the Human Owner explicitly approves an extended monitoring state.

Expired experiments must be evaluated, extended with approval, rejected, rolled back or archived.

## Success Criteria Rules

Success criteria must describe the conditions under which the experiment should be considered successful.

Success criteria should be observable and tied to the hypothesis.

Examples include fewer repeated review findings, clearer Codex execution reports, fewer rework cycles, improved documentation consistency, reduced ambiguity in Human Owner decisions or safer task closure.

Success criteria must not be changed mid-experiment unless the Human Owner approves a proposal revision.

## Failure Criteria Rules

Failure criteria must describe when the experiment should be rejected, stopped or rolled back.

Failure criteria may include increased review friction without clear benefit, more Codex errors, unclear ownership, broken approval boundaries, documentation inconsistency, Human Owner confusion, inability to collect useful evidence or unacceptable risk.

Failure criteria should prevent experiments from continuing only because they are already active.

## Evaluation Process

Evaluation should follow this flow:

```text
Collect evidence
→ compare against success criteria
→ compare against failure criteria
→ identify side effects and risks
→ capture lessons learned
→ recommend adopt, revise, extend, reject or roll back
→ obtain Human Owner decision when required
→ update source-of-truth documents if adopted
→ archive experiment record
```

Evaluation should include both expected outcomes and unintended consequences.

## Adoption Process

Adoption is required when an experiment becomes active system behavior.

Adoption steps:

1. Summarize evidence and evaluation result.
2. Identify documents, prompts, rules, templates or processes to update.
3. Determine AICP and version impact.
4. Obtain Human Owner approval where required.
5. Apply approved updates through controlled task or Codex execution.
6. Review and verify applied changes.
7. Record changelog and audit history.
8. Archive the experiment record with adoption outcome.

Adoption must not happen silently through repeated use.

## Rejection Process

Rejection is required when an experiment should not become active system behavior.

Rejection steps:

1. Record evaluation result and reason.
2. Identify whether rollback is required.
3. Capture useful lessons through Knowledge Lifecycle.
4. Close or update related improvement entries.
5. Archive the experiment record.

Rejected experiments may be proposed again only with a changed hypothesis, scope or evidence plan.

## Rollback Rules

Rollback is required when experiment effects create unacceptable risk, failure criteria are met and active changes must be reversed, Human Owner rejects the experiment and discontinuation is not enough, experiment scope was exceeded or experiment changes conflict with source-of-truth documents.

Rollback must define what will be reverted, what will remain as historical evidence, affected files or processes, verification steps after rollback, who approves the rollback and whether changelog or AICP updates are required.

Rollback must not delete audit history.

## Relationship to Decision Lifecycle

`/ai-system/decision-process.md` includes `EXPERIMENT` as a decision status.

Experiment Lifecycle defines what must happen after a decision enters experimental handling.

The Human Owner decides whether to approve, extend, adopt, reject or roll back experiments when those decisions affect system behavior or risk.

Decision records should link to experiment proposals and final evaluation outcomes.

## Relationship to Change Lifecycle

Experiments that change the AI Development System are managed system changes.

Experimental changes must follow `/ai-system/change-lifecycle.md` for approval, application, verification, adoption, rollback and archival when they affect source-of-truth behavior.

Permanent adoption of an experiment may require a new AICP or an update to an existing AICP.

## Relationship to Knowledge Lifecycle

Experiments produce knowledge whether they succeed or fail.

Successful experiments may produce rules, templates, prompts or lifecycle updates.

Rejected experiments may still produce lessons learned, stale-knowledge warnings or future improvement candidates.

Knowledge promotion must follow `/ai-system/knowledge-lifecycle.md` and must not automatically convert experiment observations into rules.

## Relationship to Improvement Lifecycle

Improvement entries may become experiment proposals when the improvement is uncertain and should be tested before permanent adoption.

Experiment outcomes may close, update or reopen improvement entries.

Until a dedicated Improvement Lifecycle is implemented, `/ai-system/improvement-log.md` remains the default place to capture experiment candidates and related observations.

## Relationship to Review Lifecycle

Experiment proposals and results should be reviewed before start and before adoption.

Review should check hypothesis clarity, scope, risk, rollback, evidence quality, documentation consistency and Human Owner approval requirements.

Review findings may request proposal rework, block the experiment, require narrower scope or recommend rejection.

## Human Owner Approval Rules

Human Owner approval is required for:

- starting an experiment that affects AI Development System behavior;
- changing experiment scope, duration, success criteria or failure criteria;
- accepting meaningful experiment risk;
- extending an experiment beyond its original timebox;
- adopting an experiment into active system behavior;
- rejecting or rolling back an experiment when it affects source-of-truth documents;
- resolving conflicts between experiment evidence and existing rules or decisions.

AI roles may recommend experiment actions, but Human Owner decides when system behavior or risk changes.

## AICP Relationship

An AICP is required when an experiment or experiment adoption affects:

- AI Development System behavior;
- role definitions or responsibilities;
- lifecycle governance;
- workflow or approval process;
- prompt requirements;
- review, QA or Codex execution rules;
- system version;
- permanent adoption of an experiment;
- rollback of an applied system change.

An AICP is not required for a purely observational experiment unless the experiment changes the system or its source-of-truth documents.

## Version Impact Rules

Use `MAJOR.MINOR.PATCH` for AI Development System experiment changes.

- Patch: wording, formatting, link correction or experiment clarification without behavior change.
- Minor: new experiment lifecycle document, new experiment state, new experiment operation, new approval rule or meaningful experiment governance addition.
- Major: significant change to approval model, experiment authority, rollback rules, workflow or lifecycle governance.

When uncertain, choose the higher impact and ask the Human Owner to confirm.

## Audit and History Rules

Experiment history should preserve:

- experiment proposal;
- Human Owner approval decision;
- hypothesis;
- scope and out of scope;
- duration or review point;
- success and failure criteria;
- risks and rollback plan;
- owner and reviewer roles;
- monitoring evidence;
- evaluation result;
- adoption, rejection or rollback decision;
- related decision, change, knowledge, improvement, review, AICP, changelog entry or commit;
- final archived status.

Audit should make it possible to understand why an experiment started, what it tested, what happened and why it was adopted, rejected or rolled back.

## Relationship to Lifecycle Governance

This document specializes `/ai-system/lifecycle-governance.md` for managed experiments.

If this document and lifecycle governance conflict, report the conflict and require Human Owner approval before changing behavior.

Future experiment lifecycle changes must follow lifecycle governance, document lifecycle and process lifecycle rules.

## Boundary Rules

Experiment lifecycle must not be used to bypass Human Owner approval.

Experiment lifecycle must not silently turn trial behavior into permanent system behavior.

Experiment lifecycle must not hide risk, expand scope or weaken rollback obligations.

Experiment lifecycle must not replace task acceptance, review approval, QA execution, change governance or knowledge validation.

Experiment lifecycle must not allow Codex to modify files unless an approved task or prompt defines scope, allowed files, forbidden actions and acceptance criteria.

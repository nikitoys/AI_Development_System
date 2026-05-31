# Improvement Lifecycle

Status: Draft
Version: v0.1.0

## Purpose

This document defines how improvements are observed, logged, triaged, analyzed, classified, accepted, deferred, rejected, converted, applied, verified, closed and archived inside the AI Development System.

Improvements need triage, recurring issue detection, conversion criteria and closure rules so the system can evolve without turning every observation into an immediate system change.

## Governed Entity

A managed improvement is any observed problem, inefficiency, repeated issue, unclear rule, missing document, weak prompt, workflow gap, review friction, QA gap or other system-level opportunity that may improve the AI Development System.

A managed improvement may become:

- an AICP;
- a knowledge item;
- an experiment;
- a task;
- a documentation update;
- a prompt update;
- a lifecycle or process update;
- a rejected, deferred or archived observation.

An improvement is not automatically a change request. It must be triaged and classified before it changes source-of-truth documents or system behavior.

## What Counts as an Improvement

An item counts as an improvement when it identifies a possible way to make the AI Development System clearer, safer, more consistent, more reliable, easier to operate or easier to review.

Examples:

- repeated review findings;
- recurring Codex execution failures;
- unclear ownership or approval boundaries;
- missing lifecycle states or closure rules;
- confusing terminology;
- repeated QA gaps;
- process friction during Human Owner interaction;
- missing templates or examples;
- outdated documentation references;
- improvement opportunities found during pilot or production use.

## What Does Not Count as an Improvement

The following do not count as managed improvements by default:

- ordinary product backlog work;
- one-off implementation tasks with clear scope;
- personal preferences with no system impact;
- speculative ideas without a problem or opportunity statement;
- raw conversation without summary or classification;
- defects that only need immediate repair and have no reusable lesson;
- product documentation updates that do not affect the AI Development System.

Such items may still be recorded elsewhere, but they should not enter Improvement Lifecycle unless they affect the system itself.

## Source of Truth

Default source-of-truth documents for improvements are:

- `/ai-system/improvement-log.md` for logged observations and improvement candidates;
- `/ai-system/change-process.md` and `/ai-system/change-lifecycle.md` for system changes and AICP conversion;
- `/ai-system/knowledge-lifecycle.md` for lessons learned and reusable knowledge;
- `/ai-system/experiment-lifecycle.md` for uncertain improvements that require testing;
- `/ai-system/review-lifecycle.md` for review-derived improvements and verification;
- `/ai-system/decision-process.md` and `/ai-system/decision-lifecycle.md` for Human Owner decisions;
- `/ai-system/system-changelog.md` for applied improvement history;
- `/ai-system/lifecycle-governance.md` for shared lifecycle governance rules.

If an improvement conflicts with source-of-truth documents, the conflict must be reported before acceptance or conversion.

## Improvement Lifecycle States

Managed improvements should use these states where applicable:

- `Observed` - a possible improvement was noticed but not yet recorded.
- `Logged` - the improvement was recorded in a managed location.
- `Triaged` - the improvement was reviewed for relevance, urgency, ownership and routing.
- `Analyzing` - root cause, impact and options are being examined.
- `Candidate` - the improvement is valid enough to consider for conversion or action.
- `Accepted` - the improvement is approved for action within a defined path.
- `Deferred` - the improvement is valid but postponed.
- `Rejected` - the improvement is not accepted.
- `Converted to AICP` - the improvement became a formal system change proposal.
- `Converted to Knowledge` - the improvement became a managed knowledge item or lesson learned.
- `Converted to Experiment` - the improvement became a managed experiment proposal.
- `Applied` - the accepted improvement was implemented or incorporated.
- `Verified` - the applied improvement was checked against acceptance or closure criteria.
- `Closed` - no active improvement action remains.
- `Archived` - the record is retained for history and audit.

Specific tools or task records may use shorter labels, but they should map back to these states.

## Allowed Operations

## Observe Improvement

Goal: notice a possible problem, gap or opportunity.

Observation may happen during task execution, review, QA, Codex result intake, Human Owner interaction, decision handling, knowledge capture or system evolution.

Observed improvements must not change behavior until they are logged, triaged and accepted or converted.

## Log Improvement

Goal: record the observation in `/ai-system/improvement-log.md` or another approved location.

A logged improvement should include:

- short title;
- source context;
- observed problem or opportunity;
- affected document, process, role or lifecycle;
- evidence or example;
- suspected impact;
- suggested route if known;
- owner or reviewer when known.

## Triage Improvement

Goal: decide whether the logged item is relevant, urgent, duplicate, invalid, task-local, product-local or system-level.

Triage should assign priority, likely owner and likely conversion path.

## Analyze Root Cause

Goal: understand why the issue exists before changing the system.

Root cause analysis should avoid treating symptoms as rules. It should identify whether the problem comes from missing documentation, unclear workflow, weak prompt, role boundary issue, lack of review, lack of QA, stale knowledge, insufficient examples or external constraints.

## Classify Improvement

Goal: route the improvement to the correct next step.

Possible classifications:

- immediate documentation correction;
- AICP candidate;
- knowledge candidate;
- experiment candidate;
- review checklist update;
- prompt update;
- lifecycle or process update;
- deferred item;
- rejected item.

## Accept Improvement

Goal: approve the improvement for action.

Accepted improvements must have a defined target, owner, scope and closure criteria.

## Defer Improvement

Goal: postpone a valid improvement.

Deferral should record reason, revisit trigger or review point.

## Reject Improvement

Goal: mark the improvement as not worth action.

Rejection should record reason and whether any lesson should still be captured.

## Convert to AICP

Goal: turn the improvement into a formal AI System Change Proposal.

Conversion is required when the improvement changes system behavior, governance, approval model, roles, workflow, lifecycle rules, prompt requirements or other source-of-truth behavior.

## Convert to Knowledge

Goal: capture a reusable lesson without making an immediate system change.

Conversion to knowledge is appropriate when the improvement reveals a stable lesson, clarified term, repeated issue, useful pattern or stale knowledge warning.

## Convert to Experiment

Goal: test an uncertain improvement before permanent adoption.

Conversion to experiment is appropriate when the improvement has a plausible benefit but requires evidence, timebox, success criteria, failure criteria and rollback plan.

## Apply Improvement

Goal: implement or incorporate the accepted improvement through the approved path.

Application must follow task, Codex, review, change or document lifecycle rules as applicable.

## Verify Improvement

Goal: confirm the improvement addressed the original issue without creating unacceptable new problems.

Verification may require review, QA, regression checks, documentation consistency checks or Human Owner confirmation.

## Close Improvement

Goal: end active handling after the improvement is applied, converted, rejected, deferred or superseded.

Closure must record outcome and remaining risks or follow-up items.

## Archive Improvement

Goal: retain the improvement record for history and audit.

Archived improvements may be used for recurring issue detection, knowledge capture and future lifecycle improvements.

## Ownership Model

Default ownership:

- Human Owner approves improvements that change system behavior, risk, authority, workflow or source-of-truth rules.
- ChatGPT Orchestrator logs, triages, classifies and routes improvements.
- AI System Maintainer owns improvement governance and system consistency.
- Technical Writer AI owns documentation clarity, templates and changelog consistency.
- Code Reviewer AI owns code-review-derived improvement findings.
- QA Engineer AI owns QA, defect and regression-derived improvement findings.
- Relevant domain roles own domain-specific improvement analysis.
- Codex Executor applies approved repository changes only through explicit task scope.

No role may convert an observation into a system change without required approval.

## Observation Capture Rules

Observations should be captured when they show possible system value, repeated friction, unclear rules, missing documentation, review gaps, QA gaps, prompt issues, role confusion, stale knowledge or failed assumptions.

Capture should be concise, evidence-based and linked to a source when possible.

Raw conversation should be summarized before becoming a managed improvement.

## Triage Rules

Triage should decide:

- whether the item affects `/ai-system` or product `/docs`;
- whether it is duplicate, recurring or new;
- whether it is urgent or can wait;
- whether it requires Human Owner decision;
- whether it should become AICP, knowledge, experiment, task or rejection;
- whether it has enough evidence for action;
- whether it conflicts with existing source-of-truth documents.

Items without enough evidence may remain logged, be deferred or become experiments.

## Severity or Priority Classification

Use simple priority labels unless another task defines more detail:

- `Critical` - blocks safe system operation or risks serious governance failure.
- `High` - repeated or significant issue that should be addressed soon.
- `Medium` - useful improvement with clear benefit but no immediate risk.
- `Low` - minor clarity, convenience or cleanup improvement.
- `Suggestion` - optional idea with uncertain or limited value.

Priority should consider impact, frequency, risk, affected lifecycle, Human Owner burden and cost of delay.

## Recurring Issue Detection Rules

An issue should be treated as recurring when:

- the same or similar finding appears in multiple reviews;
- the same Codex mistake appears in repeated executions;
- the same Human Owner clarification is needed repeatedly;
- multiple documents show the same ambiguity;
- QA or regression checks expose the same class of failure;
- a stale rule or prompt causes repeated rework.

Recurring issues should be considered for knowledge capture, rule clarification, template update, prompt update, AICP or experiment.

## Root Cause Analysis Rules

Root cause analysis should ask:

- what triggered the issue;
- which source-of-truth document was missing, unclear or stale;
- whether the issue came from role ownership, prompt design, workflow, review, QA, Codex execution or Human Owner decision flow;
- whether the issue is isolated or recurring;
- whether the best response is correction, knowledge, experiment or system change;
- what risk appears if no action is taken.

Root cause analysis should not overfit a broad system rule to a single event.

## Conversion Criteria

An improvement may be converted when it has enough evidence, clear scope, expected value and a suitable destination.

Conversion destination should be chosen by effect:

- AICP for system behavior or governance changes;
- knowledge for reusable lessons;
- experiment for uncertain proposals requiring evidence;
- task for bounded implementation or documentation work;
- rejection or deferral when action is not justified now.

## When to Convert an Improvement into AICP

Convert to AICP when the improvement affects:

- AI Development System behavior;
- role definitions or responsibilities;
- lifecycle governance;
- workflow or approval process;
- prompt requirements;
- review, QA or Codex execution rules;
- system version;
- permanent adoption of an experiment;
- rollback of an applied system change.

AICP conversion should include problem, proposed change, affected documents, expected benefit, risks, version impact and Human Owner decision.

## When to Convert an Improvement into Knowledge

Convert to knowledge when the improvement reveals:

- stable lesson learned;
- clarified terminology;
- recurring issue pattern;
- useful prompt or review pattern;
- stale knowledge warning;
- decision guidance that should inform future work.

Knowledge conversion must follow `/ai-system/knowledge-lifecycle.md`.

## When to Convert an Improvement into an Experiment

Convert to experiment when:

- benefit is plausible but uncertain;
- evidence is needed before permanent change;
- success and failure criteria can be defined;
- a timebox or review point can be set;
- rollback or discontinuation is possible.

Experiment conversion must follow `/ai-system/experiment-lifecycle.md`.

## When to Reject or Defer an Improvement

Reject an improvement when it is out of scope, unsupported, duplicate without new value, contrary to Human Owner intent, too speculative, too costly for the benefit or belongs outside `/ai-system`.

Defer an improvement when it is valid but blocked by missing evidence, lower priority, dependency on another lifecycle, lack of pilot data or need for future review.

Deferred improvements should include a revisit trigger.

## Closure Criteria

An improvement can close when:

- it was applied and verified;
- it was converted to AICP, knowledge or experiment and the new lifecycle record exists;
- it was rejected with reason;
- it was deferred with revisit trigger;
- it was superseded by another improvement or system change;
- the Human Owner explicitly closes it.

Closure must record final state, outcome, related records and remaining risks.

## Relationship to improvement-log.md

`/ai-system/improvement-log.md` is the default intake and tracking location for improvement observations.

The log should capture enough context for triage and conversion, but the lifecycle document defines state, ownership, conversion and closure rules.

The log should not become a hidden source of active system behavior without approved conversion.

## Relationship to Change Lifecycle

Improvements that change the AI Development System must follow `/ai-system/change-lifecycle.md`.

Change Lifecycle governs AICP, approval, application, verification, rollback and changelog updates after conversion.

Improvement Lifecycle governs intake, triage, analysis and conversion before the change lifecycle begins.

## Relationship to Knowledge Lifecycle

Improvements often produce knowledge.

Knowledge Lifecycle governs validation, promotion, deprecation and storage of lessons learned.

An improvement may close after conversion to knowledge when the knowledge item has its own lifecycle record or source-of-truth update.

## Relationship to Experiment Lifecycle

Uncertain improvements should become experiments instead of immediate rules or permanent changes.

Experiment Lifecycle governs hypothesis, timebox, success criteria, failure criteria, evaluation, adoption, rejection and rollback.

Experiment outcomes may create new improvements or close the original improvement.

## Relationship to Review Lifecycle

Review findings are a common source of improvements.

Review Lifecycle governs review states, findings, rework and closure. Improvement Lifecycle governs whether review-derived issues become system improvements, knowledge, experiments or AICPs.

Applied improvements should be reviewed before closure when they affect source-of-truth documents or system behavior.

## Relationship to Lifecycle Governance

This document specializes `/ai-system/lifecycle-governance.md` for managed improvements.

If this document and lifecycle governance conflict, report the conflict and require Human Owner approval before changing behavior.

Future improvement lifecycle changes must follow lifecycle governance, document lifecycle and process lifecycle rules.

## Human Owner Approval Rules

Human Owner approval is required for:

- accepting improvements that change system behavior;
- converting improvements into AICP when governance changes are involved;
- rejecting high-impact or disputed improvements;
- accepting risk from unresolved recurring issues;
- applying improvements to rules, prompts, roles, lifecycle documents or approval processes;
- closing improvements with unresolved major risk;
- deciding between AICP, knowledge and experiment when routing is disputed.

AI roles may recommend actions, but Human Owner decides when system behavior or risk changes.

## AICP Relationship

An AICP is required when an improvement affects:

- AI Development System behavior;
- role definitions or responsibilities;
- lifecycle governance;
- workflow or approval process;
- prompt requirements;
- review, QA or Codex execution rules;
- system version;
- permanent adoption of an experiment;
- rollback of an applied system change.

An AICP is not required for a logged observation, rejected item, deferred item, archived lesson or local clarification unless it changes the AI Development System itself.

## Version Impact Rules

Use `MAJOR.MINOR.PATCH` for AI Development System improvement changes.

- Patch: wording, formatting, link correction, log clarification or local improvement without behavior change.
- Minor: new improvement lifecycle document, new improvement state, new operation, new conversion path or meaningful improvement governance addition.
- Major: significant change to approval model, governance model, source-of-truth hierarchy, workflow or role authority.

When uncertain, choose the higher impact and ask the Human Owner to confirm.

## Audit and History Rules

Improvement history should preserve:

- improvement title or identifier;
- source context;
- observation evidence;
- triage result;
- priority or severity;
- root cause summary;
- classification;
- conversion path or final outcome;
- Human Owner decision when required;
- related review, QA flow, knowledge item, experiment, AICP, changelog entry, task or commit;
- closure reason;
- archived status.

Audit should make it possible to understand why an improvement was accepted, rejected, deferred, converted, applied or closed.

## Boundary Rules

Improvement lifecycle must not be used to bypass Human Owner approval.

Improvement lifecycle must not turn every observation into a system change.

Improvement lifecycle must not silently convert observations into rules, prompts or lifecycle changes.

Improvement lifecycle must not replace change lifecycle, knowledge lifecycle, experiment lifecycle, review lifecycle, QA lifecycle or task lifecycle.

Improvement lifecycle must not allow Codex to modify files unless an approved task or prompt defines scope, allowed files, forbidden actions and acceptance criteria.

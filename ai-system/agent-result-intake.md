# Agent Result Intake

Status: Draft
Version: v0.1.0

## Purpose

This document defines Agent Result Intake for AI_Development_System.

Agent Result Intake is the controlled process for receiving, checking and routing the output of an Agent Work Package or Codex execution result before review, QA, integration review or Human Owner acceptance.

It does not accept final task results.

It does not authorize automatic execution, automatic merge or automatic acceptance.

It does not implement runtime behavior.

## Governed Entity

The governed entity is an agent result.

An agent result is a submitted output from one approved Agent Work Package, Codex Prompt Package or bounded execution context.

An agent result may include changed files, summaries, checks, errors, questions, blockers, review notes, QA notes or documentation updates.

An agent result is not accepted until it passes required intake, review and QA gates and the Human Owner accepts the parent task or relevant decision.

## Source-of-Truth Documents

Agent Result Intake depends on these source-of-truth documents:

- `agent-work-package.md` for package fields, boundaries and expected output.
- `sop-model.md` for selected SOP and procedure boundaries.
- `multi-agent-planning.md` for planned package dependencies and file scopes.
- `parallel-execution-policy.md` for parallel group rules, conflict checks and integration review requirements.
- `task-format.md` for task result format and Definition of Done.
- `task-lifecycle.md` for task review, rework, acceptance and rejection states.
- `prompt-lifecycle.md` for prompt package approval and execution flow.
- `codex-lifecycle.md` for Codex result reporting, intake and review.
- `review-process.md` and `review-lifecycle.md` for review requirements and rework routing.
- `qa-lifecycle.md` for QA checks, defects, regression and approval recommendations.
- `verification-modes.md` for verification mode expectations.
- `roles.md` and `system-structure.md` for role boundaries.
- `security-policy.md` and `privacy-data-handling-policy.md` for sensitive output and external tool boundaries.
- `lifecycle-governance.md` for common managed-entity governance.
- `system-changelog.md` for applied system change history.

If an agent result conflicts with the package, task or source documents, intake should report the conflict before review or acceptance.

## Relationship to Agent Work Package

Agent Result Intake checks whether a result matches the Agent Work Package that produced it.

The intake must compare the result with:

- package ID;
- parent task;
- selected SOP;
- role;
- scope and out of scope;
- `allowed_files`;
- `locked_files`;
- `forbidden_actions`;
- dependencies;
- acceptance criteria;
- verification mode;
- expected output;
- review instructions;
- risks and questions/blockers.

The result must not expand the package or parent task scope.

## Relationship to SOP Model

The selected SOP defines the expected procedure and gates.

Intake should check whether the result follows the SOP path and preserves required Human Owner approval, review and QA boundaries.

If the result implies a SOP change, intake should route that as controlled evolution rather than accepting the result silently.

## Relationship to Multi-Agent Planning

When a result belongs to a managed multi-agent plan, intake should check it against the plan.

The intake should verify:

- planned package identity;
- dependency assumptions;
- package order or approved parallel group membership;
- planned file scope;
- planned locked files;
- planned review and QA expectations;
- unresolved blockers from planning.

Multi-Agent Planning output does not authorize acceptance. Intake only checks whether the submitted result matches the approved plan.

## Relationship to Parallel Execution Policy

When a result belongs to a parallel execution group, intake must check compliance with `parallel-execution-policy.md`.

The intake should confirm:

- the group was explicitly approved by the Human Owner;
- the package was part of the approved group;
- dependencies did not require sequencing;
- `allowed_files` and `locked_files` were respected;
- no forbidden actions occurred;
- integration review is still required before parent task acceptance;
- QA or documented QA decision remains required before final acceptance.

Intake does not replace integration review.

## Relationship to Codex Lifecycle

Agent Result Intake extends the result intake step described in `codex-lifecycle.md`.

Codex results should include:

```text
Changed files
Summary
Checks performed
Errors or blockers
Questions
Diff or key changes
```

If a result report is incomplete, intake should block review or request clarification.

## Relationship to Review and QA

Agent Result Intake routes results to review and QA.

It does not perform final review by itself unless the active role is explicitly reviewing intake completeness.

Review should follow `review-process.md` and `review-lifecycle.md`.

QA should follow `qa-lifecycle.md`.

QA may be required before acceptance when the result affects behavior, user-facing flows, data handling, process rules, lifecycle rules or source-of-truth documentation.

## Required Result Fields

Every agent result should include:

- `result_id` - stable result identifier.
- `agent_work_package` - related Agent Work Package ID.
- `parent_task` - parent task ID or title.
- `sop` - selected SOP ID.
- `role` - role or executor context that produced the result.
- `status` - result status.
- `changed_files` - files created, modified, deleted or inspected when relevant.
- `summary` - concise description of what was done.
- `scope_statement` - statement of how the result stayed inside scope.
- `checks_performed` - verification commands, inspections or checks.
- `verification_mode` - verification mode used.
- `errors` - failures or incomplete work.
- `questions` - open questions requiring decision.
- `blockers` - blockers preventing review, QA or acceptance.
- `diff_or_key_changes` - diff summary or key changes.
- `dependency_notes` - dependency assumptions and satisfied prerequisites.
- `review_notes` - review-relevant notes.
- `qa_notes` - QA-relevant notes or skipped QA rationale.
- `security_privacy_notes` - sensitive data, secret, sandbox or external tool considerations.
- `recommended_next_state` - proposed routing such as `Ready for Review`, `Rework Required`, `Rejected` or `Blocked`.

## Result Intake States / Status Values

Agent results should use these status values where applicable:

- `Submitted` - result was provided for intake.
- `Intake In Progress` - intake checks are being performed.
- `Incomplete` - required result fields are missing.
- `Blocked` - result cannot proceed because a blocker or decision is unresolved.
- `Ready for Review` - intake passed enough to start review.
- `Ready for QA` - intake passed enough to start QA where applicable.
- `Ready for Integration Review` - result can join an integrated result set.
- `Rework Required` - targeted correction is needed.
- `Rejected` - result is not acceptable for the parent task or package.
- `Archived` - retained for history, not active.

These states are intake states. They do not mean final parent task acceptance.

## Ownership Model

Default ownership:

- Human Owner accepts final task results and risk.
- ChatGPT Orchestrator coordinates intake routing and summarizes state.
- AI System Maintainer owns Agent Result Intake process evolution.
- The package owner role provides result content and answers clarification questions.
- Code Reviewer AI checks review readiness and later performs review when assigned.
- QA Engineer AI checks QA readiness and later performs QA when assigned.
- Technical Writer AI checks documentation consistency when documentation is affected.
- Codex Executor reports results but does not accept them.

No AI role may accept final task results on behalf of the Human Owner.

## Intake Checks

Agent Result Intake should check:

- required result fields;
- parent task match;
- Agent Work Package match;
- selected SOP match;
- role boundary compliance;
- scope compliance;
- out-of-scope violations;
- `allowed_files` compliance;
- `locked_files` compliance;
- `forbidden_actions` compliance;
- dependency result status;
- verification mode compliance;
- review readiness;
- QA readiness;
- security/privacy notes;
- errors, questions and blockers;
- recommended next state.

## Scope Compliance Checks

Scope compliance checks should verify:

- result matches package `scope`;
- result does not perform `out_of_scope` work;
- result does not add product behavior, system behavior or documentation scope that was not approved;
- result does not change role boundaries or lifecycle states unless explicitly approved;
- result does not require unapproved follow-up to be meaningful.

Scope violations should route to `Rework Required`, `Rejected` or `Blocked` depending on severity.

## `allowed_files` and `locked_files` Compliance Checks

The intake should compare changed files with package `allowed_files`.

Rules:

- files outside `allowed_files` must be reported as a scope violation;
- files inside another package's `locked_files` must be reported as a conflict;
- changes to shared files must be flagged for review or integration review;
- missing changed-file reporting blocks intake;
- file-lock compliance does not mean the result is accepted.

When the result is part of a parallel group, file-lock compliance must be checked before integration review.

## Forbidden Actions Checks

The intake should check whether the result performed forbidden actions from:

- parent task;
- Agent Work Package;
- prompt package;
- SOP;
- security/privacy policy;
- parallel execution policy where applicable.

Forbidden action violations should usually route to `Rejected` or `Rework Required`.

If a forbidden action changed repository state, rollback or rework requires explicit Human Owner approval.

## Dependency Result Checks

The intake should check whether required dependencies were satisfied.

Dependency checks should include:

- parent task decisions;
- Human Owner approvals;
- package prerequisites;
- source documents;
- architecture or product decisions;
- review or QA prerequisites;
- security/privacy approval;
- external environment prerequisites.

If dependency status is unclear, the result should be `Blocked`.

## Verification Mode Compliance Checks

The intake should compare requested verification mode with reported checks.

If checks were skipped, the result should explain why.

If reported checks do not satisfy the requested verification mode, intake should route to `Blocked`, `Rework Required` or review with documented limitation.

Documentation integrity checks may be required for source-of-truth documentation changes.

## Error / Question / Blocker Handling

Errors, questions and blockers must remain visible.

Rules:

- blocking questions should stop acceptance routing;
- unresolved blockers should route to `Blocked`;
- errors affecting acceptance criteria should route to `Rework Required` or `Rejected`;
- minor non-blocking questions may proceed to review only when documented;
- Human Owner decisions must be requested when scope, risk or approval is unclear.

## Rework Routing

Rework should be narrower than the original package.

Rework routing should identify:

- result ID;
- package ID;
- finding or blocker being addressed;
- severity;
- allowed files;
- forbidden actions;
- acceptance criteria for rework;
- verification mode;
- review or QA requirement.

Rework must not add unrelated scope.

## Rejection Routing

Reject a result when it cannot be accepted in its current form and targeted rework is not appropriate or not approved.

Rejection should record:

- reason for rejection;
- affected package and parent task;
- scope or policy violations;
- changed files at issue;
- whether rollback is required;
- whether a new task, package or prompt is needed;
- Human Owner decision requirement.

## Archive / History Rules

Agent results should be archived when intake is complete, rejected, superseded or no longer active.

Archived records should preserve:

- result ID;
- package ID;
- parent task;
- status;
- changed files;
- checks performed;
- review or QA routing;
- final intake decision;
- questions, blockers or lessons learned.

System-level changes should also be recorded in `system-changelog.md` when applicable.

## Boundary Rules

Agent Result Intake does not accept final task results.

Agent Result Intake does not replace review.

Agent Result Intake does not replace QA.

Agent Result Intake does not replace Human Owner final acceptance.

Agent Result Intake does not authorize automatic execution.

Agent Result Intake does not authorize automatic merge.

Agent Result Intake does not authorize automatic acceptance.

Runtime automation remains out of scope.

Human Owner remains final decision maker.

## Open Questions / Future Work

- Define machine-checkable agent result schema in `EVOL-014`.
- Add project-local agent result templates in `EVOL-015`.
- Add dry-run validation tooling in `EVOL-016`.
- Decide how result IDs should be generated in project-local control files.
- Decide how intake records should reference external Codex sessions.
- Decide whether future tooling should compare changed files against `allowed_files` automatically.


# Integration Review

Status: Draft
Version: v0.1.0

## Purpose

This document defines Integration Review for AI_Development_System.

Integration Review checks whether multiple agent results, package outputs or parallel execution outputs form a coherent parent-task result before QA handoff and Human Owner acceptance.

It does not replace QA.

It does not replace Human Owner final acceptance.

It does not authorize automatic execution, automatic merge or automatic acceptance.

It does not implement runtime behavior.

## Governed Entity

The governed entity is an integrated agent result set.

An integrated agent result set is a collection of agent results that belong to one parent task, selected SOP, multi-agent plan or approved parallel execution group.

The set may include backend, frontend, QA, review, documentation or system-governance outputs.

Integration Review evaluates the combined result, not only each individual output.

## Source-of-Truth Documents

Integration Review depends on these source-of-truth documents:

- `agent-result-intake.md` for individual result intake.
- `parallel-execution-policy.md` for parallel execution group requirements.
- `multi-agent-planning.md` for planned packages, dependencies and candidate group assumptions.
- `agent-work-package.md` for package boundaries and expected output.
- `sop-model.md` for selected SOP and procedure gates.
- `task-format.md` for parent task structure and Definition of Done.
- `task-lifecycle.md` for task review, rework and acceptance rules.
- `prompt-lifecycle.md` for prompt package history when repository work was executed.
- `codex-lifecycle.md` for Codex result reporting and intake rules.
- `review-process.md` and `review-lifecycle.md` for review severity, states and re-review.
- `qa-lifecycle.md` for QA handoff, checks, defects and regression.
- `roles.md` and `system-structure.md` for role responsibilities.
- `workflow.md` for the standard development workflow.
- `verification-modes.md` for verification expectations.
- `security-policy.md` and `privacy-data-handling-policy.md` for sensitive work review.
- `lifecycle-governance.md` for common managed-entity governance.
- `system-changelog.md` for applied system change history.

If an integrated result set conflicts with a source-of-truth document, the conflict must be reported before approval or QA handoff.

## Relationship to Agent Result Intake

Integration Review starts after relevant individual agent results pass intake or are explicitly marked as blocked with known risk.

Each result should have:

- result ID;
- package ID;
- parent task;
- changed files;
- scope compliance notes;
- `allowed_files` and `locked_files` compliance notes;
- dependency notes;
- verification notes;
- errors, questions or blockers;
- recommended intake state.

Integration Review should not proceed when required result intake records are missing.

## Relationship to Parallel Execution Policy

Integration Review is mandatory before parent task acceptance for parallel execution groups.

For parallel groups, Integration Review must check:

- every approved package result is present or explicitly blocked;
- package outputs do not conflict;
- file locks were respected;
- dependencies were respected;
- no package output required a same-group package output as input;
- combined result stays inside the parent task scope;
- QA or documented QA decision is ready before final acceptance.

## Relationship to Review Lifecycle

Integration Review is a managed review.

It should follow `review-lifecycle.md` for review states, findings, rework, re-review and closure.

Integration Review may produce:

- `APPROVED`;
- `APPROVED with Notes`;
- `REWORK`;
- `REJECTED`;
- `BLOCKED`.

Integration Review approval does not replace final Human Owner acceptance.

## Relationship to QA Lifecycle

Integration Review prepares QA handoff.

QA should receive:

- integrated result summary;
- changed files;
- known risks;
- review findings;
- accepted limitations;
- regression risks;
- unresolved questions or blockers;
- recommended QA focus.

Integration Review does not replace QA.

If QA is skipped, the reason must be documented and accepted by the Human Owner before final task acceptance.

## Required Integration Review Inputs

Integration Review should start with:

- parent task;
- selected SOP;
- multi-agent plan if one exists;
- approved parallel group if one exists;
- Agent Work Packages;
- agent result intake records;
- changed file list across all results;
- dependency map;
- `allowed_files` and `locked_files` map;
- review requirements;
- QA requirements;
- security/privacy notes;
- rollback or rework expectations;
- open questions and blockers.

Missing required inputs should block Integration Review.

## Integration Review States / Status Values

Integration Review should use these states where applicable:

- `Planned` - review need is identified.
- `Ready for Review` - required inputs are available.
- `In Review` - integrated result set is being checked.
- `Blocked` - required input, decision or result is missing.
- `Changes Requested` - rework is required.
- `Re-review Required` - corrected output must be checked again.
- `Approved` - integrated result set passes review within scope.
- `Approved with Notes` - passes review with documented non-blocking risks.
- `Rejected` - integrated result set is not acceptable.
- `Ready for QA Handoff` - review output can move to QA.
- `Closed` - review is complete and routed.
- `Archived` - retained for history, not active.

These states are review states. They do not mean final task acceptance.

## Ownership Model

Default ownership:

- Human Owner accepts final task results and residual risk.
- ChatGPT Orchestrator routes Integration Review and summarizes findings.
- Code Reviewer AI owns integration review findings for quality, architecture and conflict risks.
- QA Engineer AI owns QA handoff readiness and regression focus.
- System Architect AI checks architecture, API, data and cross-package consistency when needed.
- AI System Maintainer owns Integration Review process evolution.
- Technical Writer AI checks documentation consistency when documentation or system docs are affected.
- Codex Executor does not merge, approve or accept results.

## Cross-Agent Consistency Checks

Integration Review should verify:

- all results belong to the same parent task or approved integration scope;
- package outputs do not contradict each other;
- role outputs stay within role boundaries;
- result assumptions are compatible;
- duplicated work is identified;
- missing package outputs are visible;
- unresolved blockers are not hidden.

## Merged Behavior / Contract Checks

When results affect product or system behavior, Integration Review should check:

- combined behavior satisfies parent task acceptance criteria;
- behavior changes are documented;
- package outputs do not create inconsistent states;
- contracts used by one package are implemented by another when required;
- integration points are covered by review or QA handoff.

## Architecture Consistency Checks

Architecture checks should verify:

- package results follow approved architecture;
- no package introduced unapproved architecture decisions;
- shared modules, boundaries or dependencies remain coherent;
- system-governance changes preserve lifecycle and approval boundaries;
- broad refactors were not introduced without approval.

## API / UX / Data Contract Checks

When applicable, Integration Review should check:

- API request and response contracts;
- frontend assumptions about backend behavior;
- data model and schema assumptions;
- UX states and user-facing behavior;
- error handling and validation contracts;
- documentation of changed contracts.

## Duplicate or Conflicting Work Checks

Integration Review should identify:

- two packages changing the same behavior differently;
- duplicate documentation or inconsistent wording;
- conflicting file edits;
- redundant implementation paths;
- incompatible verification notes;
- conflicting assumptions about dependencies.

Conflicts should route to `Changes Requested`, `Blocked` or `Rejected`.

## Regression Risk Checks

Regression risk checks should identify:

- shared behavior affected by multiple packages;
- changed files with broad impact;
- lifecycle or governance rules changed by documentation work;
- security/privacy surfaces;
- QA gaps;
- skipped verification;
- areas requiring regression checks after rework.

Regression risks should be passed to QA.

## Documentation Consistency Checks

Documentation checks should verify:

- README and index updates where required;
- changelog/version updates where required;
- source-of-truth relationships remain clear;
- new documents are discoverable;
- terminology is consistent;
- documentation does not claim runtime behavior that was not implemented.

## Security / Privacy Checks

Security and privacy checks should verify:

- no secret or private data exposure;
- external LLM/tool boundaries were respected;
- auth, authorization, sandbox or sensitive data changes were explicitly approved;
- security/privacy review is planned when required;
- sensitive changes were isolated as required by policy.

Security/privacy risks should block approval unless the Human Owner explicitly accepts documented risk.

## Integration Review Verdicts

Integration Review may return:

- `APPROVED` - integrated result set is ready for QA handoff or final Human Owner review when QA is not required.
- `APPROVED with Notes` - non-blocking risks are documented.
- `REWORK` - targeted correction is required.
- `REJECTED` - result set is not acceptable in current form.
- `BLOCKED` - required input, decision, result, review or QA path is missing.

Verdicts are recommendations or gates. They do not replace Human Owner acceptance.

## Relationship to QA Handoff

Integration Review should prepare QA handoff by identifying:

- acceptance criteria to verify;
- positive checks;
- negative checks;
- edge cases;
- regression checks;
- changed files and integration points;
- known risks;
- skipped checks;
- defects or rework history.

QA may send the result back for rework or additional integration review.

## Rework and Rollback Expectations

Integration Review should distinguish:

- package-level rework;
- cross-package integration rework;
- parent-task rework;
- rollback need;
- deferred risk.

Rework or rollback must be handled through a separate approved task or prompt when repository files are changed.

Integration Review must not perform rollback automatically.

## Archive / History Rules

Integration Review records should be archived after closure.

Archived records should preserve:

- parent task;
- related package IDs;
- related result IDs;
- changed files;
- review findings;
- QA handoff notes;
- verdict;
- rework or rollback routing;
- Human Owner decisions when recorded;
- lessons learned.

System-level changes should be reflected in `system-changelog.md` when applicable.

## Boundary Rules

Integration Review does not replace QA.

Integration Review does not replace Human Owner final acceptance.

Integration Review does not authorize automatic execution.

Integration Review does not authorize automatic merge.

Integration Review does not authorize automatic acceptance.

Integration Review does not implement runtime behavior.

Integration Review must not bypass:

- Agent Result Intake;
- Review Lifecycle;
- QA Lifecycle;
- Human Owner approval;
- security/privacy policy;
- task scope;
- prompt or Codex execution boundaries.

Human Owner remains final decision maker.

## Open Questions / Future Work

- Define machine-checkable agent result and integration review schemas in `EVOL-014`.
- Add project-local result and integration review templates in `EVOL-015`.
- Add dry-run validation tooling in `EVOL-016`.
- Decide how integrated result sets should be recorded in `AI_PROJECT/`.
- Decide whether future tooling should detect duplicate changed files across results.
- Decide how pilot validation should measure integration review effectiveness.


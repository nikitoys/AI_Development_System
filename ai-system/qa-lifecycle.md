# QA Lifecycle

Status: Draft
Version: v0.1.0

## Purpose

This document defines how managed QA flows are planned, prepared, executed, reported, reworked, regressed, approved, rejected and archived inside the AI Development System.

It applies the shared governance model from `/ai-system/lifecycle-governance.md` to QA work, test planning, test execution, regression checks and QA approval.

## Governed Entity

A managed QA flow is any structured quality verification activity that checks whether a task, implementation, document, process or Codex result satisfies acceptance criteria and avoids important regressions.

Managed QA flows include:

- acceptance criteria checks;
- positive scenario checks;
- negative scenario checks;
- edge case checks;
- regression checks;
- defect reporting;
- QA review after rework;
- QA approval or rejection of task results.

Informal comments and quick observations are not managed QA flows unless they affect task acceptance, rework, rejection or source-of-truth decisions.

## Source of Truth

Default source-of-truth documents for QA are:

- `/ai-system/review-process.md` for QA review checks and severity rules;
- `/ai-system/task-format.md` for acceptance criteria, test cases, Definition of Ready and Definition of Done;
- `/ai-system/task-lifecycle.md` for task states, rework and acceptance boundaries;
- `/ai-system/codex-lifecycle.md` for Codex result intake, review and rework flow;
- `/ai-system/roles.md` for QA Engineer AI and Code Reviewer AI responsibilities;
- approved task documents, prompt packages or review reports for task-specific QA scope.

If QA scope conflicts with source documents or acceptance criteria, report the conflict before approval or rejection.

## QA Lifecycle States

Managed QA flows should use these states where applicable:

- `Not Required` - QA is explicitly not needed for the task or change.
- `Planned` - QA scope, checks or strategy are identified.
- `Test Cases Drafted` - test cases or checks are written but not yet reviewed.
- `Ready for QA` - task output and test cases are ready for execution.
- `In QA` - QA checks are being executed.
- `Passed` - QA checks passed within approved scope.
- `Failed` - QA found defects or unmet criteria.
- `Blocked` - QA cannot continue because required input, environment, result or decision is missing.
- `Regression Required` - regression checks must run before acceptance.
- `Rework Required` - defects require targeted correction.
- `Approved` - QA result is accepted for task closure or next stage.
- `Rejected` - QA result or task output is not accepted.
- `Archived` - retained for history, not active QA handling.

Specific tools or task records may use shorter status labels, but they should map back to these states.

## QA Operations

## Assess QA Need

Goal: decide whether QA is required and what level is appropriate.

QA is usually required when a task changes behavior, user-facing flows, data handling, API contracts, process rules, lifecycle rules or source-of-truth documents.

A task may be marked `Not Required` only when the reason is clear and the Human Owner or task scope accepts that risk.

## Plan QA

Goal: define the checks needed before acceptance.

QA planning should identify:

- acceptance criteria to verify;
- positive scenarios;
- negative scenarios;
- edge cases;
- regression risks;
- required environment or input data;
- owner role;
- blocking assumptions.

## Draft Test Cases

Goal: write concrete test cases or checks.

Test cases should be specific enough for repeatable execution and should map to acceptance criteria or risk areas.

## Review Test Cases

Goal: check whether planned QA is sufficient and in scope.

Review should verify that test cases cover acceptance criteria, negative scenarios, edge cases and regression risk without adding unapproved product scope.

## Start QA

Goal: begin QA execution.

Before starting QA:

- task output should be submitted for review or QA;
- acceptance criteria should be available;
- test cases or checks should be known;
- blocking ambiguities should be resolved or recorded.

## Execute Checks

Goal: run or simulate the planned QA checks.

Execution should record:

- checks performed;
- result of each check;
- defects found;
- skipped checks and reasons;
- environment limitations;
- whether regression is required.

## Report Defects

Goal: document problems found during QA.

Defect reports should include:

- expected behavior;
- actual behavior;
- reproduction steps or evidence when applicable;
- affected acceptance criteria;
- severity or blocking status;
- suggested next state, such as `Rework Required`, `Blocked` or `Rejected`.

## Request Rework

Goal: route QA findings into targeted correction.

Rework must address approved QA findings only and should not silently expand product or implementation scope.

Codex may fix QA issues only when an explicit rework task or prompt defines scope, allowed files and acceptance criteria.

## Run Regression

Goal: verify that fixes did not break previously working behavior or rules.

Regression checks should focus on areas affected by the change, known risk zones and previously failed scenarios.

Regression is required when defects were fixed, shared behavior changed, process rules changed or review identifies meaningful regression risk.

## Approve

Goal: mark QA result as acceptable for task closure or next stage.

QA approval means QA checks passed or remaining risks were explicitly accepted by the Human Owner.

QA approval does not replace final Human Owner acceptance of task results.

## Reject

Goal: mark QA result or task output as not acceptable.

Rejection should record the reason, blocking defects and whether rework, rollback or a new task is needed.

## Block

Goal: pause QA when it cannot continue safely.

QA should be blocked when:

- acceptance criteria are missing or conflicting;
- task output is incomplete;
- environment or dependency is unavailable;
- Human Owner decision is required;
- QA would exceed approved scope.

## Unblock

Goal: resume QA after a blocker is resolved.

Unblock should record what changed, which blocker was resolved and whether QA scope or test cases need revision.

## Archive

Goal: retain QA history after approval, rejection, deferral or closure.

Archived QA records may be used for audit, regression planning and lessons learned.

## Ownership Model

Default ownership:

- Human Owner approves final task result, accepts risk and decides when disputed QA outcomes are accepted or rejected.
- ChatGPT Orchestrator routes QA flow, summarizes findings and prepares rework prompts when needed.
- QA Engineer AI owns QA planning, test cases, QA execution, defect reporting and regression checks.
- Code Reviewer AI owns code review concerns that may inform QA risk and rework.
- Relevant domain role owns domain-specific behavior and expected outcomes.
- Codex Executor fixes QA issues only through an approved task or prompt with explicit scope.

QA Engineer AI may recommend approval or rejection, but Human Owner makes final acceptance decisions.

## Positive, Negative, Edge Case and Regression Checks

QA should consider these check types where applicable:

- Positive checks verify intended successful behavior.
- Negative checks verify invalid input, failure states, permission errors and error handling.
- Edge case checks verify boundary values, empty states, unusual sequences and state transitions.
- Regression checks verify that existing behavior, documentation, workflow or lifecycle rules still work after changes.

The amount of checking should match task risk and scope.

## QA Approval Requirements

QA can recommend approval when:

- acceptance criteria are satisfied;
- required positive, negative, edge case and regression checks passed or were explicitly scoped out;
- defects are resolved or accepted by the Human Owner;
- documentation updates are complete when needed;
- remaining risks are documented.

QA cannot approve product scope changes, system behavior changes or final task acceptance on behalf of the Human Owner.

## Defect Reporting and Rework Flow

Defect flow:

```text
QA finding
→ defect report
→ Human Owner or reviewer decision
→ targeted rework task or prompt
→ Codex or domain role fix
→ re-review
→ regression check when needed
→ QA recommendation
→ Human Owner acceptance or further decision
```

Defects should be handled at the narrowest scope that resolves the issue safely.

## Relationship to Task Lifecycle

QA is part of task completion.

`/ai-system/task-lifecycle.md` requires Definition of Done before `Done`, including review passed, QA passed or test cases documented, documentation updated if needed and Human Owner approval.

QA findings may move a task to `Rework Required`, `Blocked`, `Rejected` or back to `In Review` depending on severity and Human Owner decision.

## Relationship to Codex Lifecycle

When Codex fixes QA issues, execution must follow `/ai-system/codex-lifecycle.md`.

Codex must not fix QA issues without explicit task scope, allowed files, forbidden actions and acceptance criteria.

Codex result reports should feed back into QA review and regression checks.

## Relationship to Review Process

`/ai-system/review-process.md` defines QA Review checks and severity levels.

QA Lifecycle extends that process with QA states, operations, defect handling, regression checks and QA approval boundaries.

Critical issues block acceptance. Major issues require fix or explicit Human Owner decision.

## Approval Rules

Human Owner approval is required for:

- final task acceptance;
- accepting major or critical QA risk without rework;
- marking QA as not required when risk is meaningful;
- expanding QA scope into product or system scope changes;
- approving Codex rework tasks that change repository files;
- rejecting task output based on QA findings when the decision affects source of truth;
- accepting rollback or deferral after QA failure.

QA Engineer AI recommends; Human Owner decides.

## AICP Relationship

An AICP is required when QA findings or QA process changes affect:

- AI Development System behavior;
- role definitions or responsibilities;
- lifecycle governance;
- workflow or approval process;
- prompt requirements;
- review, QA or Codex execution rules;
- system version;
- permanent adoption of an experiment;
- rollback of an applied system change.

An AICP is not required for ordinary task-level defects unless they change the AI Development System itself.

## Version Impact Rules

Use `MAJOR.MINOR.PATCH` for AI Development System QA changes.

- Patch: wording, formatting, link correction or QA clarification without behavior change.
- Minor: new QA lifecycle document, new QA state, new QA operation, new QA approval rule or meaningful QA process addition.
- Major: significant change to approval model, QA ownership, workflow, role hierarchy or governance model.

When uncertain, choose the higher impact and ask the Human Owner to confirm.

## Audit and History Rules

QA history should preserve:

- QA scope;
- acceptance criteria checked;
- test cases or checks performed;
- skipped checks and reasons;
- defects found;
- rework requested;
- regression checks performed;
- QA recommendation;
- Human Owner decision;
- related task, Codex execution or review report;
- affected files or documents when applicable.

## Relationship to Lifecycle Governance

This document specializes `/ai-system/lifecycle-governance.md` for managed QA flows.

If this document and lifecycle governance conflict, report the conflict and require Human Owner approval before changing behavior.

## Relationship to Document Lifecycle

QA flows that create or update source-of-truth documents must respect `/ai-system/document-lifecycle.md`.

## Relationship to Process Lifecycle

QA Lifecycle is a managed process and must respect `/ai-system/process-lifecycle.md`.

Changes to QA states, operations, ownership, approval rules, defect flow or regression rules are process changes and may require Human Owner approval and AICP.

## Boundary Rules

QA lifecycle must not be used to bypass Human Owner approval.

QA lifecycle must not silently expand product scope or system behavior.

QA lifecycle must not allow Codex to fix QA issues without explicit task scope or approval.

QA lifecycle must not combine unrelated QA, implementation, product or system evolution work unless explicitly approved.

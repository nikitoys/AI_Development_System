# Multi-Agent Planning Workflow

Status: Draft
Version: v0.1.0

## Purpose

This document defines the Multi-Agent Planning workflow for AI_Development_System.

Multi-Agent Planning is a planning-only process that decomposes a parent task into explicit Agent Work Packages, dependencies, file-scope boundaries and candidate execution order.

It exists to make complex work easier to reason about before execution.

It does not implement runtime behavior.

It does not authorize execution, parallel execution, automatic Codex invocation or automatic acceptance.

## Governed Entity

The governed entity is a managed multi-agent plan.

A managed multi-agent plan is a structured planning artifact that records:

- parent task and selected SOP;
- proposed Agent Work Packages;
- package dependencies;
- file-scope and locked-file assumptions;
- unresolved questions and blockers;
- candidate sequential order;
- candidate parallel groups as informational planning output only;
- Human Owner approval points;
- review and QA expectations;
- metrics or learning outputs.

A managed multi-agent plan is not an executable queue.

## Source-of-Truth Documents

Multi-Agent Planning depends on these source-of-truth documents:

- `sop-model.md` for SOP selection and procedure boundaries.
- `agent-work-package.md` for Agent Work Package structure.
- `task-format.md` for task fields, Definition of Ready and Definition of Done.
- `task-lifecycle.md` for managed task states and task approval.
- `prompt-lifecycle.md` for prompt package drafting, review and approval.
- `codex-lifecycle.md` for Codex execution boundaries and result reporting.
- `roles.md` and `system-structure.md` for role responsibilities and boundaries.
- `role-agent-assignment.md` for manual L3 assignment after packages are ready.
- `workflow.md` for the standard development workflow.
- `review-process.md` and `review-lifecycle.md` for review requirements and review states.
- `qa-lifecycle.md` for QA planning, checks, defects and approval recommendations.
- `verification-modes.md` for verification mode selection.
- `security-policy.md` and `privacy-data-handling-policy.md` for safety, sandbox and external LLM boundaries.
- `lifecycle-governance.md` for common managed-entity governance.
- `evolution/sop-multi-agent-implementation-plan.md` for the controlled SOP and optional multi-agent initiative.
- `evolution/evolution-backlog.md` for future bounded evolution work.
- `system-changelog.md` for applied system change history.
- `../spec/README.md` for the current Markdown-to-spec relationship.

If a multi-agent plan conflicts with these documents, the source document wins until an approved evolution task changes the source of truth.

## Relationship to SOP Model

The SOP Model defines the procedure for a class of work.

Multi-Agent Planning applies a selected SOP to one parent task and decides whether that task should be represented as one or more Agent Work Packages.

The plan must record the selected SOP ID.

If the SOP is unclear, the plan must stop at `Blocked` or record a question instead of inventing a new active SOP.

## Relationship to Agent Work Package

Agent Work Packages are the decomposition units of a multi-agent plan.

Each planned package must follow `agent-work-package.md`.

The plan may contain:

- package drafts;
- package dependency graph;
- package file scopes;
- package locked files;
- package review and QA expectations;
- package questions and blockers.

The plan must not use packages to expand parent task scope.

## Relationship to Task Lifecycle

The parent task remains the authoritative unit of approved work.

Multi-Agent Planning may happen only after the parent task has enough information to be decomposed safely.

The plan should check that the parent task has:

- clear description;
- source documents;
- scope and out of scope;
- acceptance criteria;
- owner role or coordinating role;
- expected output;
- known risks and blockers.

Multi-Agent Planning completion does not make the parent task `Done`.

The parent task still requires execution, review, QA when required and Human Owner acceptance.

## Relationship to Prompt Lifecycle and Codex Lifecycle

Multi-Agent Planning can prepare information for future prompt packages.

It does not send prompts to Codex.

Each Agent Work Package may later be converted into a Codex Prompt Package only through `prompt-lifecycle.md` and `codex-lifecycle.md`.

Package-to-prompt conversion must preserve:

- parent task;
- package ID;
- active role;
- source documents;
- scope and out of scope;
- allowed files;
- forbidden actions;
- dependencies;
- acceptance criteria;
- verification mode;
- expected output;
- review instructions;
- Human Owner approval requirement.

Codex execution remains sequential by default unless a later approved Parallel Execution Policy and Human Owner approval explicitly allow otherwise.

## Relationship to Review and QA

Multi-Agent Planning should plan review and QA before execution starts.

The plan should identify:

- review type for each package;
- QA need for each package;
- integration or parent-task review need;
- regression risks;
- security/privacy review need;
- expected evidence;
- Human Owner acceptance points.

Review and QA recommendations do not replace Human Owner acceptance.

## Planning Inputs

A multi-agent plan should start from these inputs:

- Human Owner request or approved parent task.
- Selected SOP or SOP selection question.
- Parent task scope and out of scope.
- Source documents.
- Acceptance criteria.
- Expected files or allowed file surface.
- Known risks.
- Verification mode expectations.
- Approval requirements.
- Existing review or QA findings when planning rework.

If required inputs are missing, the plan should record blockers instead of decomposing prematurely.

## Planning Outputs

A multi-agent plan should produce:

- selected SOP;
- parent task summary;
- proposed Agent Work Packages;
- package dependency list or graph;
- package `allowed_files`;
- package `locked_files`;
- package verification modes;
- package review instructions;
- candidate sequential order;
- candidate parallel groups as informational output only;
- proposed manual Role-to-Agent Assignments when L3 orchestration is being planned;
- unresolved questions and blockers;
- Human Owner approval points;
- metrics or learning outputs when useful.

Planning output may be used to prepare one bounded next prompt package.

Planning output must not trigger execution automatically.

## Planning States / Status Values

Managed multi-agent plans should use these status values where applicable:

- `Proposed` - planning is suggested but not started.
- `Draft` - plan exists but is incomplete or not reviewed.
- `Ready for Review` - plan includes required planning outputs.
- `Approved for Sequential Execution Planning` - Human Owner approved using the plan to prepare the next bounded sequential work item.
- `Blocked` - missing input, conflict, dependency, approval or source document prevents safe planning.
- `Rework Required` - plan needs targeted correction.
- `Superseded` - replaced by a newer plan.
- `Deferred` - postponed without rejection.
- `Rejected` - not accepted as a valid plan.
- `Archived` - retained for history, not active.

These states are planning states. They do not represent execution status.

## Ownership Model

Default ownership:

- Human Owner approves the plan, execution approach and final task acceptance.
- ChatGPT Orchestrator coordinates planning and routes roles.
- Project Manager AI decomposes the parent task, identifies dependencies and proposes execution order.
- System Architect AI checks architectural boundaries, dependencies and file-scope risks when needed.
- AI System Maintainer owns Multi-Agent Planning workflow evolution.
- Domain roles own the content of their proposed Agent Work Packages.
- Code Reviewer AI and QA Engineer AI help define review and QA expectations.
- Codex Executor does not execute the plan unless a later approved prompt package is created.
- Technical Writer AI maintains documentation clarity and index consistency.

## Decomposition Rules

Decompose only when decomposition reduces risk, clarifies ownership or isolates independent work.

Do not decompose when a single bounded task is clearer.

Each proposed Agent Work Package should:

- have one primary role;
- map to the selected SOP;
- stay inside parent task scope;
- have clear input and output artifacts;
- have explicit `allowed_files`;
- have explicit `locked_files`;
- have explicit dependencies;
- have testable acceptance criteria;
- have verification mode and review instructions;
- record questions and blockers.

Do not create packages for vague work, unresolved architecture decisions, unclear acceptance criteria or missing Human Owner decisions.

## Dependency Identification Rules

Dependencies should be explicit and conservative.

The planner should identify:

- package output needed by another package;
- shared file or locked-file overlap;
- architecture or product decision dependencies;
- review or QA dependencies;
- security/privacy approval dependencies;
- environment or runtime prerequisites;
- Human Owner approval dependencies.

If package B needs output from package A, package B must not be treated as independent from package A.

If dependencies are uncertain, record a blocker or question.

## File-Scope and Locked-File Planning Rules

Every package should define `allowed_files` and `locked_files`.

`allowed_files` describes the maximum file surface a package may touch if later approved for execution.

`locked_files` describes files or directories reserved for conflict reasoning during planning.

Rules:

- `allowed_files` should be narrower than the parent task scope when possible.
- `locked_files` should include files likely to be modified or used as integration points.
- Overlapping `locked_files` indicate a conflict or sequencing need.
- Broad globs should be avoided unless the task requires them.
- Locked files do not grant execution permission.
- File locks do not replace Human Owner approval.

## Candidate Parallel Groups

The planner may identify candidate parallel groups as planning information only.

A candidate parallel group is a set of Agent Work Packages that appears to have:

- no dependency from one package to another inside the group;
- no overlapping `locked_files`;
- no required output-input chain between packages;
- compatible verification modes;
- clear review and QA expectations;
- no unresolved architecture or approval blocker.

Candidate parallel groups are not executable groups.

Candidate parallel groups remain informational until:

- a Parallel Execution Policy exists;
- Human Owner explicitly approves the group;
- file-lock and dependency checks pass under that policy;
- integration review and QA gates are planned.

Until then, sequential execution remains the default.

## Human Owner Approval Points

Human Owner approval is required for:

- accepting a multi-agent plan as usable planning input;
- approving any repository-changing execution prompt derived from the plan;
- approving any behavior-changing system or product change;
- approving any risk acceptance when dependencies, review or QA are incomplete;
- approving any future parallel group after the Parallel Execution Policy exists;
- accepting final parent task results.

AI roles may recommend. Human Owner decides.

## How a Multi-Agent Plan Becomes Executable Work

A multi-agent plan becomes executable work only through existing lifecycles.

Process:

```text
managed multi-agent plan
-> select one next bounded Agent Work Package
-> prepare Codex Prompt Package or task package
-> Human Owner review and approval
-> sequential Codex execution by default
-> result intake
-> review
-> QA when required
-> Human Owner acceptance
-> next package selection if needed
```

The plan itself must not execute anything.

The plan should prepare only the next bounded work item unless the Human Owner explicitly asks for broader planning output.

## Handling Unresolved Questions and Blockers

Unresolved questions and blockers must be recorded in the plan.

Planning should stop or narrow scope when:

- parent task scope is unclear;
- selected SOP is unclear;
- role ownership is unclear;
- acceptance criteria are missing;
- dependencies are uncertain;
- `allowed_files` or `locked_files` are too broad;
- required Human Owner approval is missing;
- security/privacy review need is unresolved;
- architecture decision is missing;
- candidate parallel grouping is uncertain.

Blocked plans should state what decision, artifact or approval is needed to continue.

## Metrics or Learning Outputs

Multi-Agent Planning may record lightweight learning outputs:

- number of packages proposed;
- number of blockers found before execution;
- dependency conflicts found;
- locked-file conflicts found;
- packages that were later merged or split;
- review or QA defects caused by planning gaps;
- prompt rework caused by unclear package fields;
- candidate improvement-log or evolution-backlog items.

Metrics are learning inputs. They do not trigger automatic execution.

## Boundary Rules

Multi-Agent Planning does not authorize execution.

Multi-Agent Planning does not authorize parallel execution.

Candidate parallel groups are informational until Parallel Execution Policy exists and Human Owner approves them.

Sequential execution remains default.

No automatic execution is allowed.

No automatic acceptance is allowed.

No runtime behavior is introduced by this workflow.

The workflow must not:

- execute Codex;
- create branches;
- merge changes;
- modify product code by itself;
- bypass review or QA;
- bypass Human Owner approval;
- create specs, scripts or templates;
- change role definitions;
- change lifecycle states;
- weaken security, privacy or approval boundaries.

## Change and Evolution Rules

Multi-Agent Planning workflow changes are AI Development System changes.

Changes must follow controlled evolution when they affect:

- planning states;
- decomposition rules;
- dependency rules;
- file-scope or locked-file rules;
- Human Owner approval points;
- prompt or Codex execution boundaries;
- review or QA requirements;
- candidate parallel group rules;
- source-of-truth relationship;
- system version.

Parallel execution policy must be introduced only through a separate bounded evolution task.

## Open Questions / Future Work

- Define the Parallel Execution Policy in `EVOL-012`.
- Define Agent Result Intake and Integration Review in `EVOL-013`.
- Add machine-checkable planning and package specs in `EVOL-014`.
- Add project-local agent planning templates in `EVOL-015`.
- Add dry-run planner validation tooling in `EVOL-016`.
- Decide whether future tooling should render dependency graphs or keep them text-only.
- Decide how local project plans should record accepted, rejected and superseded Agent Work Packages.

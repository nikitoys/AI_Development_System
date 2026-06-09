# Agent Work Package Standard

Status: Draft
Version: v0.1.0

## Purpose

This document defines the Agent Work Package standard for AI_Development_System.

An Agent Work Package is a bounded, reviewable unit of planned work assigned to one AI role or executor context.

It exists to make future SOP-guided and optional multi-agent planning explicit before any execution happens.

It does not implement runtime behavior.

It does not authorize automatic execution, automatic acceptance or parallel execution.

## Governed Entity

The governed entity is a managed Agent Work Package.

A managed Agent Work Package is a structured planning artifact that describes:

- what one role or executor context should do;
- which parent task it belongs to;
- which SOP guides the work;
- which files may be touched;
- which files are locked for conflict reasoning;
- which dependencies must be satisfied;
- which acceptance criteria, verification mode and review instructions apply.

An Agent Work Package is not a product backlog item by itself unless a concrete project explicitly records it that way.

An Agent Work Package is not executable code.

## Source-of-Truth Documents

Agent Work Packages depend on these source-of-truth documents:

- `sop-model.md` for SOP selection and relationship to governed workflows.
- `task-format.md` for task fields, Definition of Ready and Definition of Done.
- `task-lifecycle.md` for managed task states and operations.
- `prompt-lifecycle.md` for prompt package creation and approval.
- `codex-lifecycle.md` for Codex execution boundaries and result reporting.
- `roles.md` and `system-structure.md` for role responsibilities and boundaries.
- `role-agent-assignment.md` for manual L3 assignment of ready packages to logical agents or external sessions.
- `workflow.md` for the standard development workflow.
- `review-process.md` and `review-lifecycle.md` for review requirements and review states.
- `qa-lifecycle.md` for QA planning, checks, defects and approval recommendations.
- `verification-modes.md` for verification mode selection.
- `security-policy.md` and `privacy-data-handling-policy.md` for sensitive work boundaries.
- `lifecycle-governance.md` for common managed-entity governance.
- `evolution/sop-multi-agent-implementation-plan.md` for the controlled SOP and optional multi-agent initiative.
- `evolution/evolution-backlog.md` for future bounded evolution work.
- `system-changelog.md` for applied system change history.
- `../spec/README.md` for the current Markdown-to-spec relationship.

If an Agent Work Package conflicts with a source-of-truth document, the source document wins until an approved evolution task changes the source of truth.

## Relationship Between Task and Agent Work Package

A task is the parent unit of approved work.

An Agent Work Package is a child planning unit inside a parent task.

The parent task defines why the work exists, what outcome is required, what scope is approved and when the task can be accepted.

The Agent Work Package defines what one role or executor context should contribute to that parent task.

Rules:

- A parent task may have zero, one or many Agent Work Packages.
- A task can remain executable through the existing one-task Codex workflow without any Agent Work Package.
- An Agent Work Package must reference a parent task.
- An Agent Work Package must not expand parent task scope.
- An Agent Work Package must not override parent task acceptance criteria.
- An Agent Work Package must not authorize repository changes unless the parent task and prompt package are approved.

## Required Agent Work Package Fields

Every managed Agent Work Package should include these fields:

- `id` - stable package identifier, for example `AWP-BE-001`.
- `parent_task` - parent task ID or title.
- `status` - current Agent Work Package status.
- `sop` - SOP ID guiding the work, for example `SOP-FEATURE-001`.
- `role` - responsible AI role or executor context.
- `action` - short statement of what this package should do.
- `context` - why the package exists and what it depends on.
- `input_artifacts` - documents, decisions, files, task records or prior outputs required before work starts.
- `output_artifacts` - expected files, reports, prompts, review notes, QA notes or documentation outputs.
- `scope` - included work.
- `out_of_scope` - explicitly excluded work.
- `allowed_files` - files or directories this package may create, inspect or modify if execution is later approved.
- `locked_files` - files or directories reserved for this package during planning to prevent conflicting work.
- `forbidden_actions` - actions the role or executor must not perform.
- `dependencies` - package IDs, tasks, decisions, artifacts or approvals that must exist first.
- `acceptance_criteria` - observable criteria for package completion.
- `verification_mode` - required verification mode, such as `CODE_ONLY_FAST`, `FAST_VALIDATION`, `BROWSER_SMOKE` or `VISUAL_QA`.
- `expected_output` - required result report structure.
- `review_instructions` - how the package result should be reviewed.
- `risks` - known risks, uncertainty or safety concerns.
- `questions/blockers` - unresolved items that block execution or acceptance.

## Field Definitions

`allowed_files` defines the maximum file surface for a package.

It should be specific enough to prevent scope drift. Broad directories should be used only when the parent task justifies them.

`locked_files` defines planned file ownership for conflict reasoning.

Locked files do not grant write permission by themselves. They only make overlap visible before execution.

`dependencies` define ordering constraints.

Dependencies may include:

- another Agent Work Package;
- a parent task decision;
- Human Owner approval;
- architecture or product decision;
- required source document;
- review or QA result;
- external environment prerequisite.

`forbidden_actions` should repeat any parent task or system-level restrictions that are relevant to this package.

`expected_output` should follow the Codex result shape when repository work is involved:

```text
Changed files
Summary
Checks performed
Errors or blockers
Questions
Diff or key changes
```

## Lifecycle / Status Values

Agent Work Packages should use these status values where applicable:

- `Proposed` - identified as a possible package.
- `Draft` - written but not ready for approval.
- `Ready` - complete enough for review or approval.
- `Approved` - approved by the Human Owner or approved task scope for execution planning.
- `Blocked` - cannot proceed because input, decision, dependency or approval is missing.
- `In Progress` - being executed through an approved task or prompt.
- `Result Submitted` - output has been returned for intake or review.
- `In Review` - package output is being reviewed.
- `Rework Required` - package output needs targeted correction.
- `Accepted` - package output is accepted as contributing to the parent task.
- `Rejected` - package output is not accepted.
- `Deferred` - postponed without rejection.
- `Archived` - retained for history, not active.

These statuses must map back to task, review, QA and Codex lifecycle states where those lifecycles apply.

## Ownership Model

Default ownership:

- Human Owner approves behavior-changing execution, accepts final parent task results and accepts residual risk.
- ChatGPT Orchestrator selects SOPs, prepares package drafts and routes review.
- Project Manager AI may decompose a parent task into packages after scope is clear.
- The named `role` owns the domain content of the package.
- AI System Maintainer owns Agent Work Package standard evolution.
- Codex Executor may execute a package only through an approved prompt or task boundary.
- Code Reviewer AI and QA Engineer AI review or verify package output when required.
- Technical Writer AI maintains documentation clarity when package output changes documentation.

No role may use an Agent Work Package to claim authority outside its documented role boundary.

## Relationship to SOP Model

The SOP defines the procedure.

The Agent Work Package defines one planned contribution inside that procedure.

The `sop` field should reference the SOP that explains why this package exists and how it fits the larger workflow.

An Agent Work Package must not contradict the selected SOP.

If no SOP applies, the package should either reference a generic parent task flow or stop for SOP selection or future SOP definition.

## Relationship to Roles and Role Boundaries

The `role` field must reference an existing role or executor context.

The package must respect `roles.md` and `system-structure.md`.

Examples:

- Backend Developer AI may implement backend behavior from approved architecture and acceptance criteria.
- Frontend Developer AI may implement UI behavior from approved UX and product requirements.
- QA Engineer AI may define and run checks, but does not accept final task results for the Human Owner.
- Code Reviewer AI may review quality and compliance, but does not expand implementation scope.
- Technical Writer AI may update documentation, but does not change product behavior without an approved task.
- AI System Maintainer may evolve AI_Development_System only through controlled evolution.

## Relationship to Task Lifecycle

Agent Work Packages are subordinate to managed tasks.

Before an Agent Work Package can move to `Ready`, it should have:

- a parent task;
- selected SOP or documented reason for missing SOP;
- clear scope and out of scope;
- role ownership;
- allowed files and locked files;
- dependencies;
- acceptance criteria;
- verification mode;
- review instructions;
- unresolved questions recorded.

Agent Work Package completion does not make the parent task `Done`.

The parent task still requires review, QA when needed and Human Owner acceptance.

## Relationship to Prompt Lifecycle and Codex Lifecycle

An Agent Work Package may be converted into a Codex Prompt Package only when the parent task permits execution.

Prompt creation remains governed by `prompt-lifecycle.md`.

Codex execution remains governed by `codex-lifecycle.md`.

The package-to-prompt conversion should preserve:

- active role;
- source documents;
- task and package ID;
- scope and out of scope;
- allowed files;
- forbidden actions;
- acceptance criteria;
- verification mode;
- expected output;
- review instructions.

An Agent Work Package must not send itself to Codex.

Human Owner approval remains required before repository-changing execution when required by the existing lifecycle documents.

## Relationship to Review and QA

Every Agent Work Package should state review and QA expectations.

Review should check:

- package scope compliance;
- parent task compliance;
- SOP compliance;
- role boundary compliance;
- allowed files and forbidden actions;
- acceptance criteria;
- security/privacy risks when relevant;
- documentation consistency when relevant.

QA should check acceptance criteria, negative scenarios, edge cases and regressions when the package affects behavior, process rules, lifecycle rules or source-of-truth documentation.

Review and QA recommendations do not replace Human Owner acceptance.

## Relationship to Future Multi-Agent Planning

Future Multi-Agent Planning may use Agent Work Packages as decomposition units.

This document defines package structure only.

It does not define the full Multi-Agent Planning workflow. That is reserved for `EVOL-011`.

Until that workflow exists, packages may be written manually or as part of a bounded task, but they do not create an active multi-agent execution process.

## Relationship to Future Parallel Execution Policy

Agent Work Packages can support future conflict checks through `allowed_files`, `locked_files` and `dependencies`.

This does not enable parallel execution.

The full Parallel Execution Policy is reserved for a later bounded evolution task.

Any future parallel execution must require explicit Human Owner approval, clear dependencies, non-overlapping locks, planned integration review and QA gates.

## Default Rule

An Agent Work Package does not imply parallel execution.

Sequential execution remains the default.

Multiple Agent Work Packages may still be executed one at a time through the existing safe Codex workflow.

## Boundary Rule

An Agent Work Package does not authorize:

- automatic execution;
- automatic Codex invocation;
- automatic branch or merge operations;
- automatic result acceptance;
- bypassing review or QA;
- bypassing Human Owner approval;
- modifying files outside `allowed_files`;
- ignoring `locked_files`;
- ignoring dependencies;
- changing role boundaries;
- changing lifecycle states;
- enabling parallel execution.

Any behavior-changing system update must go through controlled evolution and, when required, an AI System Change Proposal.

## Examples

These examples are illustrative planning artifacts. They are not active tasks.

## Example: Backend Work Package

```yaml
id: AWP-BE-001
parent_task: TASK-042 - Add task due-date filtering
status: Draft
sop: SOP-FEATURE-001
role: Backend Developer AI
action: Add API filtering support for due_date.
context: Product requirements request filtering task records by due date.
input_artifacts:
  - docs/prd.md
  - docs/api.md
  - TASK-042
output_artifacts:
  - backend filter implementation
  - verification notes
scope:
  - add due_date query handling
  - update backend tests if present
out_of_scope:
  - frontend filter UI
  - database migration unless separately approved
allowed_files:
  - backend/**
locked_files:
  - backend/api/tasks*
forbidden_actions:
  - change authentication
  - modify frontend files
dependencies:
  - API behavior approved in parent task
acceptance_criteria:
  - due_date filter returns matching tasks
  - existing task listing still works
verification_mode: FAST_VALIDATION
expected_output:
  - Changed files
  - Summary
  - Checks performed
  - Errors or blockers
  - Questions
  - Diff or key changes
review_instructions:
  - review API behavior and regression risk
risks:
  - date parsing ambiguity
questions/blockers:
  - confirm timezone rule before implementation
```

## Example: Frontend Work Package

```yaml
id: AWP-FE-001
parent_task: TASK-042 - Add task due-date filtering
status: Draft
sop: SOP-FEATURE-001
role: Frontend Developer AI
action: Add due-date filter control to the task list UI.
context: Backend filtering exists or is planned as a dependency.
input_artifacts:
  - docs/ux.md
  - docs/api.md
  - TASK-042
output_artifacts:
  - frontend UI changes
  - browser smoke notes when requested
scope:
  - add filter control
  - wire query parameter to task list request
out_of_scope:
  - backend API changes
  - redesign of task list layout
allowed_files:
  - frontend/**
locked_files:
  - frontend/src/tasks/**
forbidden_actions:
  - add unrelated UI components
  - change routing unless approved
dependencies:
  - AWP-BE-001 accepted or API contract approved
acceptance_criteria:
  - user can filter tasks by due date
  - empty and loading states remain usable
verification_mode: BROWSER_SMOKE
expected_output:
  - Changed files
  - Summary
  - Checks performed
  - Errors or blockers
  - Questions
  - Diff or key changes
review_instructions:
  - review UX compliance and visual regression risk
risks:
  - mobile layout overflow
questions/blockers:
  - confirm exact date input format
```

## Example: QA / Review Work Package

```yaml
id: AWP-QA-001
parent_task: TASK-042 - Add task due-date filtering
status: Draft
sop: SOP-FEATURE-001
role: QA Engineer AI
action: Verify due-date filtering behavior and regressions.
context: QA validates accepted implementation output against TASK-042.
input_artifacts:
  - TASK-042
  - Codex result report
  - review notes
output_artifacts:
  - QA report
  - defect list if needed
scope:
  - positive due-date filter checks
  - invalid date and empty result checks
  - regression check for unfiltered task list
out_of_scope:
  - implementing fixes
  - accepting final task result
allowed_files:
  - AI_PROJECT/**
  - docs/**
locked_files:
  - AI_PROJECT/CODEX_SESSION_LOG.md
forbidden_actions:
  - modify product code
  - approve final acceptance for Human Owner
dependencies:
  - implementation result submitted
acceptance_criteria:
  - QA report covers positive, negative and regression checks
verification_mode: FAST_VALIDATION
expected_output:
  - Summary
  - Checks performed
  - Defects
  - Errors or blockers
  - Questions
review_instructions:
  - confirm defects map to acceptance criteria
risks:
  - missing runtime environment
questions/blockers:
  - local app URL required for browser checks if requested
```

## Example: Documentation Work Package

```yaml
id: AWP-DOC-001
parent_task: TASK-051 - Document project update workflow
status: Draft
sop: SOP-SYSTEM-001
role: Technical Writer AI
action: Update documentation for the project update workflow.
context: System update workflow needs reader-facing instructions.
input_artifacts:
  - ai-system/project-system-update.md
  - ai-system/foldered-integration.md
  - TASK-051
output_artifacts:
  - updated README section
  - documentation integrity check result
scope:
  - update documented workflow steps
  - preserve existing approval gates
out_of_scope:
  - add scripts
  - change templates
allowed_files:
  - README.md
  - README.ru.md
  - ai-system/project-system-update.md
locked_files:
  - README.md
  - README.ru.md
forbidden_actions:
  - change execution behavior
  - weaken Human Owner approval
dependencies:
  - update workflow approved
acceptance_criteria:
  - docs explain the update flow clearly
  - version mirrors are updated if changelog version changes
verification_mode: CODE_ONLY_FAST
expected_output:
  - Changed files
  - Summary
  - Checks performed
  - Errors or blockers
  - Questions
  - Diff or key changes
review_instructions:
  - review for index consistency and approval boundary preservation
risks:
  - outdated cross-links
questions/blockers:
  - none
```

## Change and Evolution Rules

Agent Work Package standard changes are AI Development System changes.

Changes must follow controlled evolution when they affect:

- required fields;
- lifecycle/status values;
- role boundaries;
- approval requirements;
- prompt package requirements;
- Codex execution boundaries;
- review or QA requirements;
- parallel execution rules;
- source-of-truth relationship;
- system version.

Small wording corrections may be handled as documentation changes, but changelog impact should be assessed when source-of-truth documents are affected.

Adding machine-checkable schemas for Agent Work Packages is future work and must be handled as a separate bounded evolution task.

## Open Questions / Future Work

- Define Multi-Agent Planning workflow in `EVOL-011`.
- Define the full Parallel Execution Policy in `EVOL-012`.
- Define Agent Result Intake and Integration Review in `EVOL-013`.
- Add machine-checkable Agent Work Package schema in `EVOL-014`.
- Add project-local Agent Work Package templates in `EVOL-015`.
- Decide whether `locked_files` should support glob syntax, exact paths only or both.
- Decide whether future tooling should validate package dependency graphs before prompt generation.

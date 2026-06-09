# Parallel Execution Policy

Status: Draft
Version: v0.1.0

## Purpose

This document defines the Parallel Execution Policy for AI_Development_System.

The policy defines when a set of Agent Work Packages may be considered for parallel execution, when parallel execution is forbidden and which approval, review, QA and conflict checks are required.

This document does not implement runtime behavior.

It does not create branches, worktrees, merge logic, scripts or automation.

It does not authorize automatic execution, automatic merge or automatic acceptance.

## Governed Entity

The governed entity is a managed parallel execution group.

A managed parallel execution group is an approved set of Agent Work Packages that may be executed concurrently only after required checks and Human Owner approval.

A candidate parallel group from Multi-Agent Planning is not a managed parallel execution group until it is explicitly approved.

## Source-of-Truth Documents

Parallel execution depends on these source-of-truth documents:

- `sop-model.md` for SOP selection and governance boundaries.
- `agent-work-package.md` for Agent Work Package structure.
- `multi-agent-planning.md` for planning-only decomposition and candidate parallel group identification.
- `task-format.md` for task fields, Definition of Ready and Definition of Done.
- `task-lifecycle.md` for task approval and closure.
- `prompt-lifecycle.md` for prompt package drafting, review and approval.
- `codex-lifecycle.md` for Codex execution boundaries and result reporting.
- `roles.md` and `system-structure.md` for role responsibilities and boundaries.
- `role-agent-assignment.md` for manual assignment records when approved parallel groups are run as manual work threads.
- `workflow.md` for the standard development workflow.
- `review-process.md` and `review-lifecycle.md` for review requirements and review states.
- `qa-lifecycle.md` for QA planning, checks, defects and approval recommendations.
- `verification-modes.md` for verification mode selection.
- `security-policy.md` and `privacy-data-handling-policy.md` for security, privacy, sandbox and external LLM boundaries.
- `lifecycle-governance.md` for common managed-entity governance.
- `evolution/sop-multi-agent-implementation-plan.md` for the controlled SOP and optional multi-agent initiative.
- `evolution/evolution-backlog.md` for future bounded evolution work.
- `system-changelog.md` for applied system change history.
- `../spec/README.md` for the current Markdown-to-spec relationship.

If this policy conflicts with a higher-level source-of-truth document, the source document wins until an approved evolution task changes the source of truth.

## Relationship to SOP Model

SOPs define the procedure for a class of work.

Parallel execution may be considered only when the selected SOP, parent task and Agent Work Packages make the work boundaries explicit.

An SOP does not authorize parallel execution by itself.

If a SOP or parent task requires sequential gates, parallel execution is not allowed for packages that cross those gates.

## Relationship to Agent Work Package

Parallel execution requires explicit Agent Work Packages.

Each package in a managed parallel execution group must define:

- `id`;
- `parent_task`;
- `sop`;
- `role`;
- `scope`;
- `out_of_scope`;
- `allowed_files`;
- `locked_files`;
- `forbidden_actions`;
- `dependencies`;
- `acceptance_criteria`;
- `verification_mode`;
- `expected_output`;
- `review_instructions`;
- `risks`;
- `questions/blockers`.

Packages with missing required fields are not eligible for parallel execution.

## Relationship to Multi-Agent Planning

Multi-Agent Planning may identify candidate parallel groups as informational planning output.

Parallel execution is never implied by Multi-Agent Planning.

Candidate parallel groups remain non-executable until:

- the group is reviewed against this policy;
- required dependency checks pass;
- required `allowed_files` and `locked_files` checks pass;
- integration review and QA expectations are planned;
- Human Owner explicitly approves the group.

## Relationship to Task Lifecycle

The parent task remains the authoritative unit of approved work and final acceptance.

Parallel execution may occur only inside a parent task that has:

- clear scope and out of scope;
- source documents;
- acceptance criteria;
- owner or coordinating role;
- expected output;
- review and QA expectations;
- explicit Human Owner approval for parallel execution.

Parallel package completion does not make the parent task `Done`.

The parent task still requires result intake, integration review, QA or documented QA decision and Human Owner acceptance.

## Relationship to Prompt Lifecycle and Codex Lifecycle

Every package in a parallel group must still be converted into an approved prompt package or task package before execution.

Prompt creation remains governed by `prompt-lifecycle.md`.

Codex execution remains governed by `codex-lifecycle.md`.

Parallel execution does not authorize:

- automatic prompt dispatch;
- automatic Codex invocation;
- automatic branch or worktree creation;
- automatic merge;
- automatic result acceptance.

Each execution result must report changed files, summary, checks performed, errors or blockers, questions and diff or key changes.

For L3 manual orchestration, each package in an approved parallel group should also have a Role-to-Agent Assignment record before the manual work thread starts.

## Relationship to Review and QA

Parallel execution increases integration risk.

Every managed parallel execution group requires integration review before parent task acceptance.

Each package must have package-level review instructions.

The parent task must have integration review instructions that check:

- combined scope compliance;
- changed files across all packages;
- dependency assumptions;
- conflicts between package outputs;
- architecture and role boundary compliance;
- security/privacy risks;
- review and QA evidence completeness;
- whether rework or rollback is needed.

QA is required when packages affect behavior, user-facing flows, data handling, process rules, lifecycle rules or source-of-truth documentation.

If QA is not run, the reason must be documented and accepted by the Human Owner before final acceptance.

Review and QA recommendations do not replace Human Owner acceptance.

## Default Rule

Sequential execution remains the default operating mode.

The safe one-task Codex workflow remains valid.

Parallel execution is an exception.

## Opt-In Rule

Parallel execution requires explicit Human Owner approval for each parallel execution group.

Approval must identify:

- parent task;
- selected SOP;
- package IDs in the group;
- approved execution boundary;
- allowed files and locked files;
- known dependencies and risks;
- integration review requirement;
- QA requirement or documented QA decision;
- rollback or rework path.

## Parallel Eligibility Criteria

Parallel execution may be considered only when all criteria are satisfied:

- Human Owner explicitly approved the group.
- The parent task is clear and bounded.
- The selected SOP is clear.
- Agent Work Packages are explicit and complete.
- Package dependencies are clear.
- No package output is required input for another package in the same group.
- `allowed_files` are explicit for every package.
- `locked_files` are explicit for every package.
- `locked_files` do not overlap.
- Shared files are absent or explicitly isolated and approved.
- Each package has acceptance criteria.
- Each package has verification mode.
- Each package has review instructions.
- Integration review is planned before parent task acceptance.
- QA is planned or a QA decision is documented.
- Rollback or rework path is clear.
- Security/privacy risks are absent or explicitly approved and isolated.

## Parallel Rejection Criteria

Parallel execution is forbidden when any of these conditions exist:

- unresolved architecture decisions;
- unclear acceptance criteria;
- missing source documents;
- overlapping `locked_files`;
- unsafe shared files;
- security/auth/privacy-sensitive changes unless explicitly approved and isolated;
- broad refactors;
- AI system behavior changes unless handled as controlled evolution with explicit approval;
- one package output is required input for another package;
- missing rollback or rework path;
- missing Human Owner approval;
- missing Agent Work Package definitions;
- missing dependency checks;
- missing `allowed_files` or `locked_files`;
- unclear role ownership;
- unclear verification mode;
- unclear review or QA expectations;
- unresolved questions or blockers that affect package independence;
- broad package scopes that cannot be reviewed independently.

## Dependency Rules

Dependencies must be checked before approval.

The dependency check should identify:

- direct package-to-package dependencies;
- output-input dependencies;
- shared architecture decisions;
- shared product decisions;
- shared data model or API contract changes;
- review or QA dependencies;
- environment dependencies;
- Human Owner decision dependencies.

If package B needs package A's output, A and B must not run in the same parallel group.

If dependency direction is uncertain, parallel execution is rejected until clarified.

## `allowed_files` and `locked_files` Conflict Rules

Every package must define `allowed_files` and `locked_files`.

`allowed_files` define the maximum file surface the package may touch.

`locked_files` define the files or directories reserved for conflict reasoning.

Rules:

- Overlapping `locked_files` reject parallel execution by default.
- A file listed in two packages' `allowed_files` should be treated as a potential conflict.
- A file listed in one package's `locked_files` must not be modified by another package.
- Broad globs should be rejected unless they are explicitly justified and isolated.
- Shared configuration, schema, routing, lifecycle, security and generated files require extra caution.
- Locked files do not grant write permission.
- Allowed files do not bypass prompt approval.

When a conflict exists, packages should be sequenced or re-scoped before execution.

## File-Lock Ownership Rules

File-lock ownership is planning ownership, not repository ownership.

The package that lists a file in `locked_files` owns planned changes to that file for the approved execution group.

Other packages must not modify that file during the same group.

If a later package needs the same file, it should be sequenced after result intake and integration review.

If lock ownership is unclear, the group is blocked.

## Approval Gates

Parallel execution requires these gates:

1. Parent task readiness.
2. SOP selection.
3. Agent Work Package completeness.
4. Dependency check.
5. `allowed_files` and `locked_files` conflict check.
6. Security/privacy boundary check.
7. Integration review plan.
8. QA plan or documented QA decision.
9. Rollback or rework path.
10. Explicit Human Owner approval.

Failure at any gate blocks parallel execution.

## Required Integration Review

Integration review is mandatory before parent task acceptance.

Integration review must check the combined result of all packages, not only individual package results.

Integration review should verify:

- all package outputs are present;
- package results satisfy parent task scope;
- package results do not conflict;
- changed files match approved boundaries;
- dependencies were respected;
- no forbidden actions occurred;
- review and QA evidence is sufficient;
- rework or rollback needs are identified.

This policy defines the requirement for integration review. A fuller Agent Result Intake and Integration Review process is reserved for a later bounded evolution task.

## Required QA Relationship

QA must be planned before parallel execution is approved.

QA may be:

- package-level QA;
- parent-task QA;
- regression-focused QA;
- documentation integrity or lifecycle consistency checks for documentation/system tasks;
- explicitly documented as not required with Human Owner risk acceptance.

QA decision must be visible before final parent task acceptance.

## Rollback / Rework Expectations

Every parallel group must have a rollback or rework path before approval.

The path should describe:

- how package-level failures are isolated;
- how integration conflicts are handled;
- whether rework is package-level or parent-task-level;
- which files may need rollback or correction;
- who decides whether to rework, reject, defer or accept risk;
- which checks must be re-run after rework.

Rollback or rework must use a separate approved task or prompt when repository files are changed.

## Result Intake Expectations

Each package result must be intaken before integration review.

Result intake should check:

- changed files;
- scope compliance;
- allowed files compliance;
- locked files compliance;
- forbidden actions;
- checks performed;
- errors or blockers;
- questions;
- review and QA evidence.

Incomplete package results should be blocked or returned for clarification before integration review.

## Security and Privacy Boundaries

Parallel execution involving security, authentication, authorization, secrets, private data, external services, sandboxing or generated artifacts is rejected by default.

It may be considered only when:

- Human Owner explicitly approves the security/privacy-sensitive parallel group;
- packages are isolated;
- security/privacy review is planned;
- sensitive files do not overlap;
- rollback or rework path is clear;
- external LLM and tool data-sharing boundaries are respected.

Security and privacy policy requirements cannot be weakened by parallel execution.

## Metrics or Learning Outputs

Parallel execution should record lightweight learning outputs when useful:

- candidate groups approved or rejected;
- dependency conflicts found;
- locked-file conflicts found;
- integration review findings;
- QA defects related to parallel execution;
- rework caused by poor package boundaries;
- security/privacy blockers;
- time saved or lost compared with sequential execution;
- candidate improvement-log or evolution-backlog items.

Metrics are learning inputs. They do not trigger automatic execution.

## Boundary Rules

Parallel execution is never implied by Multi-Agent Planning.

Candidate parallel groups remain non-executable until approved.

Parallel execution requires explicit Human Owner approval.

Parallel execution requires explicit Agent Work Packages.

Parallel execution requires dependency checks.

Parallel execution requires `allowed_files` and `locked_files` conflict checks.

Parallel execution requires integration review before acceptance.

Parallel execution requires QA or documented QA decision before final acceptance.

Parallel execution does not authorize automatic execution.

Parallel execution does not authorize automatic merge.

Parallel execution does not authorize automatic acceptance.

Human Owner remains final decision maker.

This policy must not be used to:

- execute Codex automatically;
- create branches or worktrees automatically;
- merge changes automatically;
- bypass review;
- bypass QA;
- bypass Human Owner approval;
- modify product code by itself;
- add specs, scripts or templates;
- change role definitions;
- change lifecycle states;
- weaken security, privacy or approval rules.

## Change and Evolution Rules

Parallel Execution Policy changes are AI Development System changes.

Changes must follow controlled evolution when they affect:

- eligibility criteria;
- rejection criteria;
- dependency rules;
- file-lock rules;
- approval gates;
- integration review requirements;
- QA relationship;
- rollback or rework expectations;
- security/privacy boundaries;
- source-of-truth relationship;
- system version.

Runtime automation, scripts, templates, specs, worktree management or merge logic must be introduced only through separate bounded evolution tasks.

## Open Questions / Future Work

- Define Agent Result Intake and Integration Review in `EVOL-013`.
- Add machine-checkable parallel policy specs in `EVOL-014`.
- Add project-local agent planning templates in `EVOL-015`.
- Add dry-run planner validation tooling in `EVOL-016`.
- Decide whether future tooling should represent `locked_files` as exact paths, globs or structured file-lock records.
- Decide how to record Human Owner approval for each parallel group in project-local control files.
- Decide how pilot validation should measure parallel execution benefit versus integration risk.

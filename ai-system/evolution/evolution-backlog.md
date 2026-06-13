# AI System Evolution Backlog

Status: Draft  
Version: v0.1.0

## Purpose

This backlog tracks actionable improvements for AI_Development_System itself.

It is separate from product backlogs. Product features, bugs and implementation tasks belong in project-level control files. This backlog is only for system governance, documentation, templates, integration, verification and evolution capability.

## Backlog Item Format

```md
## EVOL-000 — Title

Status:
Priority:
Source:
Roadmap item:
Owner:
Type:
Affected documents:
Problem:
Expected outcome:
Acceptance criteria:
Conversion path:
Notes:
```

## Status Values

```text
Proposed
Accepted
Planned
In Progress
Blocked
Done
Deferred
Rejected
Superseded
```

## Priority Values

```text
P0  urgent system integrity or governance gap
P1  high-value productization or safety improvement
P2  important but not blocking
P3  future research or optimization
```

## Type Values

```text
Documentation
Governance
Lifecycle
Template
Integration
Verification
Security
Privacy
Automation
Research
Pilot Validation
```

---

## EVOL-001 — Add controlled self-evolution module

Status: Done  
Priority: P0  
Source: Human Owner request and analytical report recommendations  
Roadmap item: P0 — Self-Evolution Governance  
Owner: AI System Maintainer  
Type: Governance

Affected documents:

- `ai-system/evolution/README.md`
- `ai-system/evolution/roadmap.md`
- `ai-system/evolution/evolution-loop.md`
- `ai-system/evolution/evolution-policy.md`
- `ai-system/evolution/system-health-check.md`
- `ai-system/evolution/evolution-backlog.md`
- `ai-system/README.md`
- `ai-system/operating-model.md`
- `ai-system/system-changelog.md`

Problem:

The system has many lifecycle documents and an evolution mode, but it does not yet have a dedicated, indexed module that makes roadmap-driven self-evolution explicit and bounded.

Expected outcome:

Add an internal `ai-system/evolution/` module that defines how the system evolves according to its own plan while preserving Human Owner approval.

Acceptance criteria:

- evolution module index exists;
- roadmap exists;
- evolution loop exists;
- evolution policy exists;
- health check exists;
- backlog exists;
- proposal and task templates exist;
- analytical report baseline is referenced;
- AI system README and operating model reference the module;
- changelog records the change.

Conversion path:

System change.

Notes:

This item is the initial bootstrap for future roadmap-driven self-evolution.

---

## EVOL-002 — Synchronize versions and document statuses

Status: Done  
Priority: P1  
Source: Analytical report finding  
Roadmap item: P1 — Consistency and Documentation Integrity  
Owner: AI System Maintainer  
Type: Documentation

Problem:

Visible system versions and document statuses can drift between entrypoints and changelog.

Expected outcome:

Define one authoritative version source and update primary entrypoints to avoid conflicting version claims.

Acceptance criteria:

- authoritative version source documented;
- root README and `ai-system/README.md` do not conflict with changelog;
- version/status update rules documented;
- changelog records the fix.

Conversion path:

AICP if versioning policy changes; otherwise documentation task.

Notes:

Completed as a bounded documentation/status synchronization task. The authoritative version source is the top entry in `ai-system/system-changelog.md`; README files mirror it. No AICP was required because this clarified version mirroring and did not change lifecycle states, approval gates or versioning authority.

---

## EVOL-003 — Add documentation integrity checks

Status: Done  
Priority: P1  
Source: Analytical report finding  
Roadmap item: P1 — Consistency and Documentation Integrity  
Owner: AI System Maintainer / DevOps AI  
Type: Verification

Problem:

The repository is documentation-first, but does not yet have automated checks for links, indexes, placeholders or status/version fields.

Expected outcome:

Add a minimal validation workflow or script for documentation integrity.

Acceptance criteria:

- markdown links can be checked;
- unresolved placeholders can be detected;
- index completeness has a documented or automated check;
- status/version fields can be validated for required documents.

Conversion path:

System change and automation task.

Notes:

Completed as a bounded verification task. Added a local documentation integrity checker and GitHub workflow for Markdown links, unresolved placeholder markers outside reusable templates, index completeness and visible status/version consistency. EVOL-004 remains the next recommended phase and was not started.

---

## EVOL-004 — Add security, privacy and data-handling policy

Status: Done  
Priority: P1  
Source: Analytical report finding  
Roadmap item: P2 — Security, Privacy and Data Handling  
Owner: AI System Maintainer / Security Reviewer AI  
Type: Security

Problem:

The system assumes external AI tools and Codex-like execution, but explicit secret-handling, privacy, sandbox and sensitive-data rules are not yet centralized.

Expected outcome:

Add security/privacy/data-handling policy documents and link them from review and verification guidance.

Acceptance criteria:

- secret-handling rules exist;
- external LLM data-sharing rules exist;
- sandbox/execution boundaries exist;
- security review can reference the policy;
- project templates can inherit the policy.

Conversion path:

AICP required.

Notes:

Completed with `ai-system/aicp-security-privacy-policy.md`, centralized security and privacy/data-handling policies, review/rules references and project-template inheritance links. EVOL-005 remains the next recommended phase and was not started.

---

## EVOL-005 — Create golden example project

Status: Done  
Priority: P2  
Source: Analytical report finding  
Roadmap item: P3 — Golden Example and Pilot Validation  
Owner: AI System Maintainer / Technical Writer AI  
Type: Pilot Validation

Problem:

Templates exist, but there is no fully filled example showing a working integration.

Expected outcome:

Create one example repository or example directory with filled project control files.

Acceptance criteria:

- example includes root `AGENTS.md` or foldered equivalent;
- `AI_PROJECT` files are filled;
- verification policy is explicit;
- example workflow can be followed by a new user.

Conversion path:

Experiment or system change depending on repository structure.

Notes:

- Added `examples/golden-project/` as a filled Task Tracker foldered reference with a complete control layer and no application code.
- The example focuses on `AI_PROJECT` control files and foldered bootstrap behavior for onboarding.

---

## EVOL-006 — Introduce machine-checkable specification layer

Status: Done  
Priority: P2  
Source: Analytical report finding  
Roadmap item: P4 — Machine-Checkable Specification Layer  
Owner: AI System Maintainer / System Architect AI  
Type: Automation

Problem:

Roles, modes, lifecycle states and verification rules are currently Markdown-first, which creates drift risk.

Expected outcome:

Introduce `spec/` with YAML/JSON definitions for selected stable system entities and define Markdown/spec source-of-truth rules.

Acceptance criteria:

- first spec area selected;
- schema defined;
- validation process documented;
- generated/derived documentation policy defined.

Conversion path:

AICP required.

Notes:

- Added `spec/` as a minimal JSON-based machine-checkable layer for roles, interaction modes, verification modes and common lifecycle states.
- Added a shared minimal JSON Schema and validation guidance in `spec/README.md`.
- Markdown remains the operational source of truth; EVOL-006 does not regenerate Markdown, add CI schema lint, delete existing docs or start bootstrap/release/research work.

---

## EVOL-007 — Add minimal foldered bootstrap/update tooling MVP

Status: Done  
Priority: P2  
Source: Human Owner request after EVOL-006  
Roadmap item: P5 — Bootstrap and Update Tooling  
Owner: AI System Maintainer / DevOps Engineer AI / Technical Writer AI  
Type: Automation

Problem:

Foldered integration is documented and templated, but there is no minimal local helper for dry-run bootstrap/update planning, placeholder detection or `AI_DEV_SYSTEM_VERSION.md` tracking.

Expected outcome:

Add a small script-level MVP that can inspect or prepare foldered control-layer setup without creating a large CLI, package or release automation system.

Acceptance criteria:

- dry-run is the default mode;
- explicit apply mode exists for bounded file creation/update;
- unresolved placeholders are reported;
- `AI_PROJECT/AI_DEV_SYSTEM_VERSION.md` can be created or refreshed;
- docs explain that application code is not modified;
- changelog records the change.

Conversion path:

System change and automation task.

Notes:

- Added `scripts/foldered-control-mvp.py` with `bootstrap` and `update` commands, dry-run by default and explicit `--apply` for writes.
- The MVP creates missing foldered control files from templates during bootstrap and refreshes `AI_PROJECT/AI_DEV_SYSTEM_VERSION.md` during update.
- Large CLI/package/release automation, upstream clone/subtree management and product-code changes remain out of scope.

---

## EVOL-008 — Record SOP and Multi-Agent Implementation Plan

Status: Done  
Priority: P1  
Source: Human Owner request  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / Technical Writer AI  
Type: Documentation

Problem:

The Human Owner wants AI_Development_System to evolve toward SOP-guided planning and optional multi-agent execution, but the direction must be recorded without implementing runtime behavior or replacing the safe one-task loop.

Expected outcome:

Create a master implementation plan and decompose the initiative into future bounded evolution tasks.

Acceptance criteria:

- implementation plan document exists;
- sequential execution remains the default;
- parallel execution is opt-in and Human Owner-approved;
- planning, specs, tooling, templates, pilot and runtime decision phases are separated;
- future backlog items are added;
- changelog records the change.

Conversion path:

System documentation task.

Notes:

Recorded in `ai-system/evolution/sop-multi-agent-implementation-plan.md`. No runtime, scripts, specs, templates or execution behavior changes were implemented.

---

## EVOL-009 — Add SOP Model document

Status: Done  
Priority: P1  
Source: `sop-multi-agent-implementation-plan.md`  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / Technical Writer AI  
Type: Governance

Problem:

The system does not yet define what a SOP is, how SOPs are selected or how SOPs relate to existing workflow and task lifecycle.

Expected outcome:

Add `ai-system/sop-model.md`.

Acceptance criteria:

- SOP definition exists;
- SOP selection process is documented;
- relationship to existing workflow, task lifecycle and prompt lifecycle is clear;
- sequential execution remains default.

Conversion path:

System change or documentation task depending on behavior impact.

Notes:

Completed with `ai-system/sop-model.md`. The SOP Model defines managed SOPs, required fields, relationships to workflow, roles, task lifecycle, prompt lifecycle, Codex lifecycle, review and QA, and three initial SOPs: `SOP-FEATURE-001`, `SOP-BUGFIX-001` and `SOP-SYSTEM-001`.

Sequential execution remains the default. SOPs do not authorize automatic execution, automatic acceptance, Agent Work Package generation or parallel execution. EVOL-010 remains the next bounded phase and was not started.

---

## EVOL-010 — Add Agent Work Package standard

Status: Done  
Priority: P1  
Source: `sop-multi-agent-implementation-plan.md`  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / Technical Writer AI  
Type: Governance

Problem:

Agent work must be explicit, bounded and reviewable before any multi-agent planning can be safe.

Expected outcome:

Add `ai-system/agent-work-package.md`.

Acceptance criteria:

- required work package fields are defined;
- dependencies, `allowed_files`, `locked_files`, verification mode and acceptance criteria are mandatory;
- result format is defined;
- Human Owner approval remains required before execution.

Conversion path:

System change.

Notes:

Completed with `ai-system/agent-work-package.md`. The standard defines managed Agent Work Packages, required fields, lifecycle/status values, ownership, relationship to SOPs, tasks, prompts, Codex execution, review and QA, and examples for backend, frontend, QA/review and documentation work.

Agent Work Packages do not imply parallel execution and do not authorize automatic execution or automatic acceptance. EVOL-011 remains the next bounded phase and was not started.

---

## EVOL-011 — Add Multi-Agent Planning workflow

Status: Done  
Priority: P1  
Source: `sop-multi-agent-implementation-plan.md`  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / Project Manager AI / Technical Writer AI  
Type: Lifecycle

Problem:

The system needs a planning-only workflow for decomposing owner intent into Agent Work Packages without executing them.

Expected outcome:

Add `ai-system/multi-agent-planning.md`.

Acceptance criteria:

- planning workflow is documented;
- decomposition stops before execution;
- Human Owner approval gate is explicit;
- output can feed existing Codex prompt packages.

Conversion path:

System change.

Notes:

Completed with `ai-system/multi-agent-planning.md`. The workflow defines managed multi-agent plans, planning inputs and outputs, status values, decomposition rules, dependency identification, file-scope and locked-file planning, Human Owner approval points and the path from plan to one next bounded executable work item.

Candidate parallel groups are informational planning output only. Multi-Agent Planning does not authorize execution, parallel execution, automatic execution or automatic acceptance. EVOL-012 remains the next bounded phase and was not started.

---

## EVOL-012 — Add Parallel Execution Policy

Status: Done  
Priority: P1  
Source: `sop-multi-agent-implementation-plan.md`  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / Code Reviewer AI / QA Engineer AI  
Type: Governance

Problem:

Parallel execution can create conflicts unless allowed, denied and approval-required cases are explicit.

Expected outcome:

Add `ai-system/parallel-execution-policy.md`.

Acceptance criteria:

- allowed parallel execution conditions are documented;
- forbidden cases are documented;
- file-lock and dependency conflict rules exist;
- Human Owner approval is required for every parallel group.

Conversion path:

System change.

Notes:

Completed with `ai-system/parallel-execution-policy.md`. The policy defines managed parallel execution groups, default sequential execution, explicit Human Owner approval, eligibility and rejection criteria, dependency checks, `allowed_files` and `locked_files` conflict rules, file-lock ownership, approval gates, mandatory integration review, QA relationship, rollback/rework expectations, result intake expectations and security/privacy boundaries.

Parallel execution does not authorize automatic execution, automatic merge or automatic acceptance. EVOL-013 remains the next bounded phase and was not started.

---

## EVOL-013 — Add Agent Result Intake and Integration Review

Status: Done  
Priority: P1  
Source: `sop-multi-agent-implementation-plan.md`  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / Code Reviewer AI / QA Engineer AI / Technical Writer AI  
Type: Review

Problem:

The system needs a controlled process for receiving agent outputs, integrating them and deciding whether they pass review and QA.

Expected outcome:

Add `ai-system/agent-result-intake.md` and `ai-system/integration-review.md`.

Acceptance criteria:

- result intake process is documented;
- integration review process is documented;
- review, QA, rework and rejection paths are explicit;
- automatic acceptance is forbidden.

Conversion path:

System change.

Notes:

Completed with `ai-system/agent-result-intake.md` and `ai-system/integration-review.md`. Agent Result Intake defines required result fields, intake states, scope checks, `allowed_files` and `locked_files` compliance checks, forbidden action checks, dependency checks, verification mode checks, blocker handling, rework routing, rejection routing and archive/history rules.

Integration Review defines integrated agent result sets, required inputs, review states, cross-agent consistency checks, merged behavior/contract checks, architecture, API/UX/data, duplicate/conflict, regression, documentation and security/privacy checks, verdicts, QA handoff, rework/rollback expectations and archive/history rules.

Intake and integration review do not authorize automatic execution, automatic merge or automatic acceptance and do not replace Human Owner final acceptance. EVOL-014 remains the next bounded phase and was not started.

---

## EVOL-014 — Add machine-checkable SOP and Agent Work Package specs

Status: Done  
Priority: P2  
Source: `sop-multi-agent-implementation-plan.md`  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / System Architect AI  
Type: Automation

Problem:

SOPs, Agent Work Packages, result objects and parallel policy need machine-checkable representations after the Markdown source documents exist.

Expected outcome:

Add `spec/sops.json`, `spec/agent-work-package.schema.json`, `spec/agent-result.schema.json` and `spec/parallel-policy.json`.

Acceptance criteria:

- specs map to approved Markdown source documents;
- schema validation guidance is updated;
- no Markdown generation is introduced unless separately approved.

Conversion path:

System change.

Notes:

Completed with `spec/sops.json`, `spec/agent-work-package.schema.json`, `spec/agent-result.schema.json` and `spec/parallel-policy.json`.

The specs are minimal machine-checkable inventory/contract files derived from Markdown source documents. Markdown remains the operational source of truth. EVOL-014 does not generate Markdown, add schema validation CI, create scripts, modify templates, implement runtime behavior or authorize automatic execution, automatic merge or automatic acceptance. EVOL-015 remains the next bounded phase and was not started.

---

## EVOL-015 — Add AI_PROJECT agent planning templates

Status: Done  
Priority: P2  
Source: `sop-multi-agent-implementation-plan.md`  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / Technical Writer AI  
Type: Template

Problem:

Concrete projects need local files for agent planning, locks, results and metrics only after the system standards exist.

Expected outcome:

Add templates for `AI_PROJECT/AGENT_PLAN.md`, `AI_PROJECT/AGENT_TASKS.md`, `AI_PROJECT/AGENT_LOCKS.md`, `AI_PROJECT/AGENT_RESULTS.md` and `AI_PROJECT/AGENT_METRICS.md`.

Acceptance criteria:

- templates inherit approved SOP and Agent Work Package rules;
- templates preserve one-task default behavior;
- templates do not enable automatic execution.

Conversion path:

System change and template task.

Notes:

Completed with foldered `AI_PROJECT` templates for `AGENT_PLAN.md`, `AGENT_TASKS.md`, `AGENT_LOCKS.md`, `AGENT_RESULTS.md` and `AGENT_METRICS.md`.

Updated project control and foldered integration documentation, and added the templates to the minimal foldered bootstrap/update helper planning list. The templates preserve sequential execution as the default, keep candidate parallel groups informational until approved and do not authorize execution, parallel execution, automatic execution, automatic merge or automatic acceptance. EVOL-016 remains the next bounded phase and was not started.

---

## EVOL-016 — Add dry-run agent planner MVP script

Status: Done  
Priority: P2  
Source: `sop-multi-agent-implementation-plan.md`  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / DevOps Engineer AI  
Type: Automation

Problem:

Agent planning should be validated before runtime execution is considered.

Expected outcome:

Add `scripts/agent-plan-mvp.py` as a dry-run planner and validator.

Acceptance criteria:

- dry-run is default;
- agent plans can be validated;
- file-lock conflicts can be detected;
- safe parallel groups can be listed;
- bounded prompts can be generated for review;
- Codex is not executed automatically.

Conversion path:

Automation task.

Notes:

Completed with `scripts/agent-plan-mvp.py`. The helper supports `validate`, `check-locks`, `list-parallel-groups` and `generate-prompts` commands.

The helper is dry-run/reporting only. It reads `AI_PROJECT/AGENT_*` files, reports missing or incomplete planning files, recognizes simple Agent Work Package table entries, checks locked-file conflicts when data is available, lists candidate parallel groups as informational only and prints bounded prompt drafts when enough package data exists. It does not execute Codex, create branches or worktrees, merge changes, modify application code or accept results. EVOL-017 remains the next bounded phase and was not started.

---

## EVOL-017 — Extend golden project with multi-agent example

Status: Done  
Priority: P2  
Source: `sop-multi-agent-implementation-plan.md`  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / Technical Writer AI  
Type: Pilot Validation

Problem:

The golden project should demonstrate SOP/multi-agent planning only after documents, templates and planner rules exist.

Expected outcome:

Extend `examples/golden-project/` with a non-runtime multi-agent planning example.

Acceptance criteria:

- example includes agent plan files;
- example demonstrates dependency and file-lock reasoning;
- example does not run agents automatically;
- example preserves Human Owner approval.

Conversion path:

Example and pilot-preparation task.

Notes:

Completed by extending `examples/golden-project/` with a filled non-runtime Task Tracker due-date filter planning example.

The example includes `AI_PROJECT/AGENT_PLAN.md`, `AI_PROJECT/AGENT_TASKS.md`, `AI_PROJECT/AGENT_LOCKS.md`, `AI_PROJECT/AGENT_RESULTS.md`, `AI_PROJECT/AGENT_METRICS.md` and a project README. It demonstrates selected SOP, Agent Work Package decomposition, dependencies, `allowed_files`, `locked_files`, candidate parallel groups as informational only, Human Owner approval boundaries, result intake placeholders, integration review status, QA handoff status, metrics and dry-run helper usage.

The example does not add product runtime code and does not authorize execution, parallel execution, automatic execution, automatic merge or automatic acceptance. EVOL-018 remains the next bounded phase and was not started.

---

## EVOL-018 — Run pilot validation and record findings

Status: Done  
Priority: P2  
Source: `sop-multi-agent-implementation-plan.md`  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / QA Engineer AI / Technical Writer AI  
Type: Pilot Validation

Problem:

Runtime decisions should be based on evidence from controlled pilots, not assumptions.

Expected outcome:

Run pilot validation and record findings before deciding whether runtime integration is justified.

Acceptance criteria:

- pilot scope is approved;
- findings are recorded;
- repeated issues are converted into backlog items or policy updates;
- runtime decision remains deferred.

Conversion path:

Pilot validation task.

Notes:

Completed by recording `sop-multi-agent-pilot-validation.md`.

The pilot ran the golden project dry-run validation, lock check, informational parallel group listing, prompt draft generation and documentation integrity check. It confirmed that the golden project demonstrates SOP selection, Agent Work Packages, dependencies, `allowed_files`, `locked_files`, result intake placeholders, integration review status, QA handoff status, metrics and Human Owner approval boundaries.

The pilot recorded a known limitation: `scripts/agent-plan-mvp.py` does not deeply parse dependency graphs from Markdown and may list an over-broad informational candidate parallel group. This limitation is tracked as `IMP-002` and proposed follow-up `EVOL-020`. EVOL-019 remains the next bounded phase and was not started.

---

## EVOL-019 — Runtime Decision Record

Status: Done  
Priority: P1  
Source: `sop-multi-agent-pilot-validation.md` / Human Owner request  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: Human Owner / AI System Maintainer  
Type: Decision Record

Problem:

The system has advanced from documentation-only governance into a SOP-driven control plane with dry-run planning support. It now needs a formal runtime decision before any future runtime work is considered.

Expected outcome:

Record the runtime decision as `DEFERRED`.

Decision:

Runtime execution is `DEFERRED`.

The decision must preserve the current boundary:

- dry-run planning is allowed;
- generation of Agent Work Packages is allowed;
- validation of agent plans is allowed;
- listing candidate parallel groups is allowed as informational output;
- manual orchestration is allowed;
- Human Owner controlled review and approval are required.

The decision must explicitly forbid for now:

- automatic Codex execution;
- automatic multi-agent execution;
- automatic branch/worktree lifecycle;
- automatic merge;
- automatic acceptance;
- automatic closure of QA/review findings;
- bypassing Human Owner approval.

Revisit criteria:

Runtime execution can only be reconsidered after:

- `EVOL-020` is completed;
- dependency graph parsing is reliable;
- dry-run planning validation tests exist;
- golden project validation passes;
- at least 2-3 pilot scenarios are recorded;
- no critical safety boundary violations are found;
- manual orchestration is proven repeatable.

Acceptance criteria:

- pilot evidence is reviewed;
- risks and benefits are documented;
- Human Owner decision is recorded as `DEFERRED`;
- allowed dry-run and manual orchestration capabilities are listed;
- forbidden runtime and automation capabilities are listed;
- revisit criteria are listed;
- any runtime work requires a new bounded backlog item and approval.

Conversion path:

Decision record. No runtime implementation.

Notes:

Completed by formally recording the runtime decision as `DEFERRED`.

The system remains a SOP-driven AI development control plane with dry-run planning support. This closure does not approve or implement runtime execution, automatic Codex execution, automatic multi-agent execution, branch/worktree lifecycle automation, merge automation, automatic acceptance or automatic QA/review closure.

`EVOL-020` remains open as the next proposed technical improvement.

---

## EVOL-020 — Improve dry-run agent planner dependency parsing

Status: Done  
Priority: P2  
Source: `sop-multi-agent-pilot-validation.md` / `IMP-002`  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / DevOps Engineer AI  
Type: Automation

Problem:

`scripts/agent-plan-mvp.py list-parallel-groups` can report over-broad informational candidate groups because it does not deeply parse Agent Work Package dependencies from Markdown planning files.

Expected outcome:

Improve the dry-run helper so candidate parallel group reporting accounts for explicit dependencies from standard `AI_PROJECT/AGENT_PLAN.md` and `AI_PROJECT/AGENT_TASKS.md` formats.

Required behavior:

- parse explicit `depends_on` relationships;
- build a dependency graph;
- perform topological layering;
- detect cycles;
- detect missing dependencies;
- exclude blocked packages and packages with incomplete prerequisites;
- explain why each reported parallel group is valid;
- avoid overly broad candidate groups.

Example:

Given:

- `AWP-REQ-001`
- `AWP-BE-001` depends on `AWP-REQ-001`
- `AWP-FE-001` depends on `AWP-REQ-001`
- `AWP-QA-001` depends on `AWP-BE-001` and `AWP-FE-001`

Correct parallel group after `AWP-REQ-001` is complete:

- `AWP-BE-001`
- `AWP-FE-001`

Incorrect group:

- `AWP-REQ-001`
- `AWP-BE-001`
- `AWP-FE-001`
- `AWP-QA-001`

Acceptance criteria:

- dependency data is parsed from the standard agent planning files where available;
- explicit `depends_on` relationships are represented in a dependency graph;
- topological layering is used to identify ready groups;
- cycles are detected and reported;
- missing dependencies are detected and reported;
- packages with unresolved prerequisites are excluded from the same candidate parallel group;
- blocked packages are excluded from ready candidate groups;
- the output explains why each candidate parallel group is valid;
- lock conflict checks remain dry-run/reporting only;
- candidate parallel groups remain informational only;
- no Codex execution, branch/worktree automation, merge automation or result acceptance is introduced;
- Human Owner approval remains required before any execution.

Conversion path:

Bounded script improvement task after EVOL-019 decision or explicit Human Owner approval.

Notes:

Completed by improving `scripts/agent-plan-mvp.py` dependency parsing and ready parallel group calculation.

The helper now parses explicit dependencies from `AI_PROJECT/AGENT_TASKS.md` package detail fields and `AI_PROJECT/AGENT_PLAN.md` dependency tables, detects missing dependencies, detects dependency cycles, excludes blocked packages, and only reports current ready candidate groups whose AWP prerequisites are complete/satisfied.

Added fixtures under `examples/agent-plan-fixtures/` for accepted prerequisite unlocking, missing dependency, cycle detection and blocked package exclusion.

Runtime remains deferred. The helper remains dry-run/reporting only and does not execute Codex, create branches or worktrees, merge changes, modify application code or accept results.

---

## EVOL-021 — Planning Fixtures and Validation Tests

Status: Done  
Priority: P2  
Source: `EVOL-020` readiness criteria  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / QA Engineer AI / DevOps Engineer AI  
Type: Test

Problem:

Dry-run planning behavior needs repeatable fixtures and tests before it can be treated as reliable planning infrastructure.

Expected outcome:

Add fixtures and validation tests for agent planning and dependency graph behavior.

Recommended fixtures:

- simple linear dependency;
- simple parallel dependency;
- diamond dependency;
- missing dependency;
- cycle detection;
- blocked task;
- completed prerequisite unlocking a parallel group.

Acceptance criteria:

- fixtures cover the recommended dependency shapes;
- dependency graph validation tests can be run manually;
- tests preserve dry-run boundaries;
- tests do not execute Codex, create branches, merge changes or accept results.

Conversion path:

Bounded test/fixture task after `EVOL-020`.

Notes:

Completed by adding and validating dependency-aware planning fixtures under `examples/agent-plan-fixtures/` and the lightweight runner `scripts/validate-agent-plan-fixtures.py`.

The fixtures cover simple linear dependency, simple parallel dependency, diamond dependency, missing dependency, cycle detection, blocked package exclusion and completed prerequisite unlocking a parallel group.

The validation runner executes `scripts/agent-plan-mvp.py` against the fixtures and asserts expected success/failure behavior without executing Codex, creating branches or worktrees, merging changes, modifying application code or accepting results.

---

## EVOL-022 — Runtime Maturity Levels

Status: Done  
Priority: P2  
Source: `EVOL-019` readiness criteria  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / Technical Writer AI  
Type: Governance

Problem:

The system needs explicit maturity levels so future runtime discussions do not collapse dry-run planning, manual orchestration and automated runtime into one ambiguous concept.

Expected outcome:

Define runtime maturity levels:

- `L0` — Documentation only
- `L1` — Machine-checkable specs
- `L2` — Dry-run planning
- `L3` — Manual multi-agent orchestration
- `L4` — Assisted execution
- `L5` — Controlled runtime
- `L6` — Autonomous runtime

Current project level at EVOL-022 completion:

`L2 — Dry-run planning`.

Next target at EVOL-022 completion:

`L3 — Manual multi-agent orchestration`.

Acceptance criteria:

- maturity levels are documented;
- EVOL-022 current level is recorded as `L2`;
- EVOL-022 next target is recorded as `L3`;
- levels do not authorize runtime execution by themselves;
- Human Owner approval remains required for movement between levels.

Conversion path:

Governance documentation task after or alongside `EVOL-019`.

Notes:

Completed by adding `ai-system/runtime-maturity-levels.md` and indexing it from the operating model and `ai-system/README.md`.

The documented levels are `L0 — Documentation only`, `L1 — Machine-checkable specs`, `L2 — Dry-run planning`, `L3 — Manual multi-agent orchestration`, `L4 — Assisted execution`, `L5 — Controlled runtime` and `L6 — Autonomous runtime`.

At EVOL-022 completion, current project level was `L2 — Dry-run planning` and next safe target was `L3 — Manual multi-agent orchestration`. After the post-EVOL-026 readiness assessment, current project level is `L3 — Manual multi-agent orchestration`. Runtime execution remains `DEFERRED`, and `L4+` remains future/not approved.

---

## EVOL-023 — Manual Multi-Agent Orchestration Mode

Status: Done  
Priority: P3  
Source: `EVOL-022` next target  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / Project Manager AI / Technical Writer AI  
Type: Workflow

Problem:

The next safe target after dry-run planning is repeatable manual orchestration, not automatic agent execution.

Expected outcome:

Introduce manual orchestration mode without automatic agent execution.

Allowed examples:

- create plan;
- validate plan;
- list next ready Agent Work Package;
- mark Agent Work Package complete manually;
- intake agent result;
- run integration review manually.

Acceptance criteria:

- manual orchestration workflow is documented;
- every state transition remains Human Owner controlled or explicitly manual;
- no automatic Codex execution is introduced;
- no automatic multi-agent execution is introduced;
- no automatic merge, acceptance or QA/review closure is introduced.

Conversion path:

Workflow documentation task after maturity levels are recorded.

Notes:

Completed by adding `ai-system/manual-orchestration.md` and indexing it from `runtime-maturity-levels.md`, `operating-model.md` and `ai-system/README.md`.

Manual Multi-Agent Orchestration Mode defines L3 as manual-only coordination of Agent Work Packages, dependency-aware planning output, manual assignment, manual result intake, manual integration review and Human Owner decisions.

The document records allowed L3 manual operations, forbidden L3 automation, required L3 artifacts, L3 flow, L3 readiness criteria and L4 readiness criteria.

Runtime remains `DEFERRED`. L3 does not authorize automatic Codex execution, automatic multi-agent execution, branch/worktree automation, automatic merge, automatic acceptance or automatic QA/review closure.

---

## EVOL-024 — Agent Result Schema Hardening

Status: Done  
Priority: P3  
Source: Pilot validation / future manual orchestration needs  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / QA Engineer AI / Technical Writer AI  
Type: Specification

Problem:

Agent results need stricter machine-checkable fields before manual orchestration and integration review can scale reliably.

Expected outcome:

Harden Agent Result structure so results are easier to validate, review and compare.

Required fields should include:

- `awp_id`;
- `agent`;
- `status`;
- `changed_files`;
- `claims`;
- verification performed;
- risks;
- followups.

Acceptance criteria:

- required fields are documented in the Markdown source of truth;
- schema updates are proposed or applied in a bounded follow-up if approved;
- result intake and integration review references remain consistent;
- no automatic acceptance is introduced.

Conversion path:

Bounded schema/documentation hardening task.

Notes:

Completed by hardening `ai-system/agent-result-intake.md`, `spec/agent-result.schema.json`, `ai-system/templates/foldered/AI_PROJECT/AGENT_RESULTS.md` and the golden project result placeholder.

The hardened Agent Result schema defines required fields for `result_id`, `awp_id`, agent identity, status, summary, changed files, claims, verification, risks, blockers, followups, scope compliance, safety boundary compliance, produced artifacts, owner review requirement and integration review requirement.

Integration Review handoff rules now identify which hardened result fields must be inspected and which conditions block acceptance.

Manual orchestration now references the hardened Agent Result schema for L3 manual result intake.

Runtime remains `DEFERRED`. This change does not implement runtime behavior, automatic execution, branch/worktree automation, automatic merge, automatic acceptance or automatic QA/review closure.

---

## EVOL-025 — CI for Specs, Templates and Golden Project

Status: Done  
Priority: P3  
Source: Runtime readiness criteria / roadmap P4 and P6  
Roadmap item: P4 — Machine-Checkable Specification Layer / P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / DevOps Engineer AI / QA Engineer AI  
Type: CI

Problem:

The repository increasingly behaves like a process/specification repository, but validation is still mostly manual.

Expected outcome:

Add CI checks that validate specs, templates and the golden project without enabling runtime behavior.

Implementation:

- Added `.github/workflows/validate-ai-system.yml` with read-only jobs for docs/specs, planning fixtures and golden project validation.
- Added `scripts/validate-system.py` as the local read-only validation entrypoint.
- CI and local validation run documentation integrity checks, JSON spec parse checks, required agent template checks, dependency-aware planning fixture checks and golden project dry-run planning commands.
- The checks do not execute Codex, execute agents, create branches or worktrees, merge changes, accept results or modify files.

Recommended checks:

- YAML/JSON schema validation;
- Markdown link checks;
- placeholder detection;
- template validation;
- golden project validation;
- dependency graph fixture tests;
- safety boundary checks.

Acceptance criteria:

- CI checks are scoped to repository/specification validation;
- checks do not execute Codex;
- checks do not create branches, worktrees, merges or acceptance decisions;
- safety boundary checks preserve Human Owner approval rules.

Conversion path:

Closed by EVOL-025 after adding CI and local validation coverage. Future validation hardening can be tracked as narrower follow-up tasks.

---

## EVOL-026 — Pilot Validation Expansion

Status: Done  
Priority: P3  
Source: `EVOL-019` revisit criteria  
Roadmap item: P3 — Golden Example and Pilot Validation / P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / QA Engineer AI / Technical Writer AI  
Type: Pilot Validation

Problem:

Current pilot evidence is useful but still too narrow to justify runtime execution.

Expected outcome:

Expand pilot evidence beyond one golden example.

Implementation:

- Expanded `ai-system/evolution/sop-multi-agent-pilot-validation.md` with EVOL-026 pilot evidence.
- Recorded three pilot scenarios: documentation-only change, small tooling/code change and multi-agent parallel planning case.
- Distinguished validated dry-run behavior, manually simulated orchestration behavior and future/not-yet-validated runtime behavior.
- Preserved runtime decision `DEFERRED` and kept candidate parallel groups informational only.

Required pilot types:

- documentation-only change;
- small code change;
- multi-agent parallel planning case.

Acceptance criteria:

- at least 2-3 pilot scenarios are recorded;
- each pilot records scope, commands/checks, findings, safety boundary review and follow-up routing;
- no critical safety boundary violations are found or unresolved;
- runtime remains deferred unless a later Human Owner decision changes it.

Conversion path:

Closed by EVOL-026 after expanded pilot evidence was recorded. Future pilot work should focus on repeatable L3 manual orchestration evidence before any assisted execution discussion.

Post-EVOL-026 maturity assessment:

`L3 — Manual multi-agent orchestration` is now the current maturity level.

Assessment basis:

- `EVOL-019` through `EVOL-026` are done;
- runtime execution remains `DEFERRED`;
- dependency-aware planning, planning fixtures and CI/local validation exist;
- Manual Multi-Agent Orchestration Mode is documented;
- hardened Agent Result Intake and Integration Review handoff exist;
- pilot validation covers documentation-only, small code/tooling and multi-agent parallel planning cases;
- pilot records distinguish validated dry-run behavior, manually simulated orchestration behavior and future/not-yet-validated runtime behavior;
- Human Owner approval remains required.

Restrictions:

L3 is manual-only. It does not approve automatic Codex execution, automatic multi-agent execution, branch/worktree automation, automatic file modification by orchestration tooling, automatic merge, automatic acceptance or automatic QA/review closure. `L4+` remains future/not approved.

L3 refinement:

Manual Role-to-Agent Assignment is documented in `ai-system/role-agent-assignment.md`. Ready Agent Work Packages may be assigned manually to logical agents or external agent sessions after dependency-aware planning and Human Owner approval where required. Assignment records do not authorize automatic dispatch, runtime execution, merge or acceptance.

The practical L3 role-assigned parallel runbook is documented in `ai-system/l3-role-assigned-parallel-runbook.md`. The runbook describes the Human Owner / ChatGPT Orchestrator procedure for parent task selection, SOP selection, Agent Plan and AWP preparation, `AGENT_ASSIGNMENTS.md`, validation, candidate group review, bounded prompt handoff, Agent Result Intake, Integration Review, Human Owner decision, status update and recomputing the next ready group. It does not authorize runtime execution or automatic dispatch.

---

## EVOL-027 — Runtime Adapter Contracts

Status: Future / Deferred  
Priority: P5  
Source: Future runtime preparation  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: AI System Maintainer / System Architect AI  
Type: Architecture

Problem:

Future runtime integration may need adapter contracts, but defining those contracts too early could imply runtime approval.

Expected outcome:

Prepare future runtime adapter contract concepts without enabling runtime execution.

Acceptance criteria:

- contracts are conceptual or interface-level only;
- no runtime adapter is implemented;
- no automatic Codex execution is introduced;
- no branch/worktree lifecycle, merge automation or automatic acceptance is introduced;
- status remains `Future / Deferred` until `EVOL-019` revisit criteria are satisfied.

Conversion path:

Future architecture task only after explicit Human Owner approval.

---

## EVOL-028 — Controlled Assisted Execution Prototype

Status: Not Allowed Yet  
Priority: P6  
Source: Future runtime preparation  
Roadmap item: P6 — SOP and Optional Multi-Agent Control Plane  
Owner: Human Owner / AI System Maintainer  
Type: Experiment

Problem:

Assisted execution may become useful later, but it is unsafe to prototype before the deferred runtime readiness criteria are satisfied.

Expected outcome:

Future prototype only after `EVOL-019` through `EVOL-026` are completed and Human Owner explicitly approves a bounded experiment.

Acceptance criteria:

- `EVOL-019` through `EVOL-026` are completed first;
- Human Owner explicitly approves the prototype scope;
- prototype remains controlled and bounded;
- automatic merge and automatic acceptance remain forbidden unless separately approved by a later system decision;
- this item remains not allowed until prerequisites are satisfied.

Conversion path:

Future experiment. Not executable now.

---

## EVOL-029 — Add Work Item Hierarchy

Status: Done
Priority: P2
Source: Human Owner request
Roadmap item: P1 — Consistency and Documentation Integrity / P6 — SOP and Optional Multi-Agent Control Plane
Owner: AI System Maintainer / Project Manager AI / Technical Writer AI
Type: Documentation / Governance

Problem:

AI_Development_System had task lifecycle, roadmap, evolution backlog and Agent Work Packages, but lacked an explicit hierarchy between project goals and executable tasks.

Expected outcome:

Add a planning hierarchy from Goal to Initiative to Epic to Task to Agent Work Package while preserving task execution and Human Owner approval boundaries.

Implementation:

- Added `ai-system/work-item-hierarchy.md` as the source document for the hierarchy.
- Updated task format and task lifecycle so Initiative and Epic are optional planning fields and do not block Definition of Ready.
- Updated Agent Work Package guidance so packages remain child planning units under tasks.
- Updated `CODEX_PLAN.md` and `CODEX_TASKS.md` templates to show Initiative and Epic context.
- Updated the golden project so `T-003` maps to `INIT-001` / `EPIC-001` and remains the parent task for existing Agent Work Packages.
- Recorded traceability in `ai-system/aicp-work-item-hierarchy.md` and `ai-system/system-changelog.md`.

Acceptance criteria:

- Initiative and Epic are planning containers only.
- Task remains the executable unit.
- Agent Work Package remains a child planning unit under Task.
- `CODEX_PLAN.md` can show Initiatives and Epics.
- `CODEX_TASKS.md` can map tasks to Initiative and Epic.
- Human Owner approval remains required before execution.
- No runtime behavior, automatic execution, task lifecycle state change or new parallel execution behavior is introduced.

Conversion path:

Closed by EVOL-029 as a bounded documentation and template update.

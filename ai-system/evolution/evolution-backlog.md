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
Roadmap item: P6 — SOP and Optional Multi-Agent Execution Layer  
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
Roadmap item: P6 — SOP and Optional Multi-Agent Execution Layer  
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
Roadmap item: P6 — SOP and Optional Multi-Agent Execution Layer  
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
Roadmap item: P6 — SOP and Optional Multi-Agent Execution Layer  
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
Roadmap item: P6 — SOP and Optional Multi-Agent Execution Layer  
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
Roadmap item: P6 — SOP and Optional Multi-Agent Execution Layer  
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
Roadmap item: P6 — SOP and Optional Multi-Agent Execution Layer  
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
Roadmap item: P6 — SOP and Optional Multi-Agent Execution Layer  
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
Roadmap item: P6 — SOP and Optional Multi-Agent Execution Layer  
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
Roadmap item: P6 — SOP and Optional Multi-Agent Execution Layer  
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

Status: Proposed  
Priority: P2  
Source: `sop-multi-agent-implementation-plan.md`  
Roadmap item: P6 — SOP and Optional Multi-Agent Execution Layer  
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

---

## EVOL-019 — Decide whether runtime integration is justified

Status: Proposed  
Priority: P3  
Source: `sop-multi-agent-implementation-plan.md`  
Roadmap item: P6 — SOP and Optional Multi-Agent Execution Layer  
Owner: Human Owner / AI System Maintainer  
Type: Research

Problem:

The system should not become a runtime unless pilot evidence shows the governance-first workflow benefits from it.

Expected outcome:

Decide whether to reject, defer, experiment with or approve runtime integration.

Acceptance criteria:

- pilot evidence is reviewed;
- risks and benefits are documented;
- Human Owner decision is recorded;
- any runtime work requires a new bounded backlog item and approval.

Conversion path:

Decision or experiment proposal.

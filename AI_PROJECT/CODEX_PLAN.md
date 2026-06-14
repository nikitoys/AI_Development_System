# Codex Plan - AI Development System

Status: Draft

## Title

L4 Assisted SOP Execution Plan

## Planning Snapshot

This plan records a planning-only roadmap for reaching a future L4 Assisted SOP Execution capability.

Current runtime maturity:

```text
L3 - Manual multi-agent orchestration
```

Runtime decision:

```text
DEFERRED
```

L4 status:

```text
Future / Not approved
```

This plan does not approve L4, implement L4, add runtime behavior, create runner scripts, modify specs, modify lifecycle documents, change current maturity, or enable automatic execution.

## Current State

The repository already provides a governance-first control plane for AI-assisted development.

Implemented L3/manual capabilities:

- interaction modes and explicit repository-affecting mode routing;
- task, prompt, Codex, review, QA and verification lifecycles;
- SOP Model with initial SOPs for feature delivery, bugfix/rework and AI system evolution;
- Agent Work Package standard with allowed files, locked files, dependencies, verification mode and review instructions;
- Multi-Agent Planning workflow with candidate parallel groups as informational output only;
- Parallel Execution Policy requiring explicit Human Owner approval, dependency checks, file-lock checks, integration review and QA;
- Agent Result Intake with hardened result fields, claims, verification, scope compliance and safety boundary compliance;
- Integration Review for combined outputs before QA handoff or parent-task acceptance;
- project-control templates for `AI_PROJECT/AGENT_*` planning, assignment, locks, results and metrics;
- `scripts/agent-plan-mvp.py` as a dry-run/reporting helper only;
- `scripts/validate-system.py` as a read-only validation entrypoint for docs, specs, templates, fixtures and golden project dry-run checks;
- pilot evidence covering documentation-only, small tooling/code and multi-agent parallel planning cases;
- L3 manual orchestration and manual Role-to-Agent Assignment boundaries.

Current boundaries that must remain true:

- Human Owner approval remains required for repository-changing execution and final acceptance;
- candidate parallel groups remain informational until approved under policy;
- Codex executes only bounded, approved tasks or prompts;
- review and QA remain gates before acceptance;
- no automatic Codex execution;
- no automatic multi-agent execution;
- no automatic branch or worktree lifecycle;
- no automatic merge, push or acceptance;
- no automatic QA/review closure;
- no unbounded task discovery;
- no autonomous product, security or architecture decisions.

## Target State

L4 Assisted SOP Execution should mean an assisted, gate-aware operating mode where tooling helps the Human Owner and ChatGPT Orchestrator prepare, validate, sequence, intake and route SOP-guided work while the Human Owner remains in control.

Target L4 may allow a future helper to:

- read a declared SOP Run or Assisted SOP Run record;
- validate that required task, prompt, allowed-files, forbidden-action, verification and approval fields are present;
- recommend the next safe step in a declared run;
- generate bounded prompt packages for review;
- check user-provided Codex result reports against the run scope;
- compare changed-file reports with allowed files and locked files;
- summarize verification and skipped checks;
- recommend next states such as `blocked`, `needs_review`, `ready_for_qa`, `rework_required` or `ready_for_owner_decision`;
- record or propose run-status updates only when a future task explicitly allows that behavior.

Target L4 must not allow:

- autonomous prompt dispatch;
- automatic Codex execution;
- automatic agent dispatch;
- automatic branch/worktree creation or switching;
- automatic commit, push, merge or PR creation;
- automatic review closure;
- automatic QA closure;
- automatic acceptance;
- automatic rollback;
- unbounded task discovery;
- product, security, privacy or architecture decisions by tooling;
- L5 controlled runtime behavior.

## L3, L3.5, L4 and L5 Distinction

| Level | Meaning in this plan | Execution authority | State authority |
|---|---|---|---|
| L3 | Manual multi-agent orchestration. Humans and ChatGPT manually prepare, hand off, intake and review bounded work. | Manual only after approval. | Manual records only. |
| L3.5 | Proposed bridge: SOP-driven delegated sequential batch execution. A Human Owner approves a bounded batch plan, but each Codex prompt is still manually sent, reviewed and accepted. | Manual delegated execution, one bounded item at a time. | Manual records; helper may only validate or draft. |
| L4 | Future assisted execution. A helper may validate gates, prepare next-step artifacts and recommend routing for an approved SOP Run. | Human-approved dispatch remains required. | Helper may assist state handling only within approved boundaries. |
| L5 | Future controlled runtime. A runtime may orchestrate bounded execution under strict policy. | Not approved. Out of scope. | Not approved. Out of scope. |

## Proposed L3.5 Bridge

Introduce L3.5 as:

```text
SOP-driven delegated sequential batch execution
```

Purpose:

- bridge current L3 manual orchestration and future L4 assisted execution;
- prove that SOP Run records, gates and result intake work across more than one sequential Codex handoff;
- preserve the safe one-task Codex workflow inside a larger approved run plan;
- gather evidence before any assisted helper is allowed to recommend or write state.

Why L3.5 is not full L4:

- no helper is trusted to advance run state;
- no helper performs result intake beyond checklist/reporting support;
- no helper recommends dispatch based on live repository state;
- each prompt remains manually reviewed and sent by the Human Owner or operator.

Why L3.5 is not L5:

- no runtime controls execution;
- no queue is executed automatically;
- no branch/worktree lifecycle is automated;
- no acceptance, merge, push, rollback, review or QA closure is automated.

Required L3.5 documents and updates:

- add `SOP-CODEX-002 - Delegated Sequential Batch Execution`;
- add a SOP Run or Assisted SOP Run lifecycle document;
- update project-control guidance to include `AI_PROJECT/SOP_RUNS.md`;
- update prompt/Codex/review/QA references to explain batch context without changing one-prompt approval gates;
- add pilot records before any L4 experiment is proposed.

## Architecture

```text
SOP Definition
-> SOP Run
-> Gate Validation
-> Prompt Package Draft
-> Human Owner Decision
-> Manual Codex Handoff
-> Codex Result Report
-> Result Intake
-> File Boundary Gate
-> Verification Gate
-> Review / QA Gate
-> Human Owner Decision
-> Next-State Recommendation
```

### SOP Definition

The SOP defines the procedure, roles, gates, review requirements and Human Owner approval points. Existing SOPs remain source-of-truth examples. `SOP-CODEX-002` should be added only in a later bounded task.

### SOP Run

A SOP Run is a governed project-control record for one execution attempt of one SOP against one approved parent task or bounded batch.

Required fields:

- `run_id`;
- `status`;
- `sop_id`;
- `parent_task`;
- `active_role`;
- `stage`;
- `source_documents`;
- `scope`;
- `out_of_scope`;
- `allowed_files`;
- `forbidden_actions`;
- `planned_steps`;
- `prompt_packages`;
- `dependencies`;
- `gates`;
- `verification_mode`;
- `verification_budget`;
- `result_records`;
- `review_records`;
- `qa_records`;
- `owner_decisions`;
- `risks`;
- `blockers`;
- `recommended_next_state`;
- `closure_notes`.

Lifecycle states:

- `Proposed`;
- `Draft`;
- `Ready for Review`;
- `Approved for Manual Delegation`;
- `In Progress`;
- `Paused`;
- `Blocked`;
- `Result Submitted`;
- `In Intake`;
- `In Review`;
- `In QA`;
- `Rework Required`;
- `Ready for Owner Decision`;
- `Accepted`;
- `Rejected`;
- `Deferred`;
- `Archived`.

Ownership and approval:

- Human Owner approves run scope, execution, risk acceptance and final closure;
- ChatGPT Orchestrator routes stages and summarizes state;
- Project Manager AI decomposes and sequences bounded run steps;
- AI System Maintainer owns system-governance consistency;
- Technical Writer AI maintains planning and documentation clarity;
- Codex Executor executes only approved prompt packages;
- Code Reviewer AI and QA Engineer AI provide gates and recommendations.

### Assisted Execution Helper

A future helper may assist only after source documents and run records exist.

Allowed helper behavior:

- read SOP Run records;
- validate required fields;
- validate declared file boundaries from reports;
- produce prompt drafts for review;
- show next-step recommendations;
- produce intake checklists;
- produce verification summaries;
- produce status-update proposals for Human Owner review.

Forbidden helper behavior:

- execute Codex;
- dispatch agents;
- create branches, worktrees, commits, pushes, merges or PRs;
- edit product/application code;
- accept results;
- close review or QA;
- infer new tasks outside the declared run;
- change runtime maturity;
- implement L5 controlled runtime behavior.

## Required System Documents

These are future tasks only. They are not added by this planning task.

| File | Purpose | Reason | Risk |
|---|---|---|---|
| `ai-system/assisted-sop-execution.md` | Define L4 assisted execution model, allowed helper behavior and forbidden runtime behavior. | Prevent L4 discussion from implying L5 automation. | High if missing: unsafe runtime ambiguity. |
| `ai-system/sop-run-lifecycle.md` | Define SOP Run as a managed entity with states, operations, ownership and approval. | Needed before any run-tracking helper or project template. | High if missing: state changes become ad hoc. |
| `ai-system/sop-model.md` | Add `SOP-CODEX-002`. | Existing SOP registry needs the delegated sequential batch procedure. | Medium: SOP drift if added only to specs. |
| `ai-system/runtime-maturity-levels.md` | Add L3.5 bridge language if Human Owner approves the bridge. | Clarifies transition without declaring L4. | Medium: must not imply L4 approval. |
| `ai-system/manual-orchestration.md` | Cross-reference L3.5 boundary and SOP Run records. | Keeps L3 manual source aligned. | Medium. |
| `ai-system/codex-lifecycle.md` | Reference SOP Run context in prompt/result reporting. | Codex lifecycle must understand run-level context while preserving prompt-level gates. | Medium. |
| `ai-system/prompt-lifecycle.md` | Add prompt package relationship to SOP Runs. | Batch prompts still need markers, allowed files and approval. | Medium. |
| `ai-system/agent-result-intake.md` | Reference SOP Run result intake fields. | Intake should map results to run steps. | Medium. |
| `ai-system/integration-review.md` | Reference run-level integration review. | Multi-step delegated runs need combined review. | Medium. |
| `ai-system/review-process.md` and `ai-system/review-lifecycle.md` | Clarify review gates for SOP Runs. | Review remains mandatory before acceptance. | Low to medium. |
| `ai-system/qa-lifecycle.md` | Clarify QA gates for SOP Runs. | QA remains a recommendation/gate, not acceptance. | Low to medium. |
| `ai-system/verification-modes.md` | Clarify verification reporting for run steps and skipped checks. | Run-level verification must not claim full validation. | Medium. |
| `ai-system/project-control-files.md` | Add `AI_PROJECT/SOP_RUNS.md`. | Concrete projects need a run registry if L3.5/L4 is piloted. | Medium. |
| `ai-system/templates/foldered/AI_PROJECT/SOP_RUNS.md` | Template for project-local run tracking. | Needed for repeatable pilots. | Medium. |
| `examples/golden-project/AI_PROJECT/SOP_RUNS.md` | Filled non-runtime example. | Needed for validation and onboarding. | Low. |

## Required SOP Changes

Future SOP:

```text
SOP-CODEX-002 - Delegated Sequential Batch Execution
```

Purpose:

- guide a Human Owner-approved sequence of bounded Codex prompt packages under one SOP Run;
- preserve one prompt/result/review/QA gate at a time;
- allow planning of a batch without enabling automatic execution.

Trigger:

- Human Owner asks to run multiple bounded, related Codex tasks under one coordinated plan;
- the parent scope is clear enough to decompose safely;
- the work benefits from a SOP Run record.

Participating roles:

- Human Owner;
- ChatGPT Orchestrator;
- Project Manager AI;
- AI System Maintainer for system tasks;
- Technical Writer AI for documentation clarity;
- Codex Executor;
- Code Reviewer AI;
- QA Engineer AI;
- domain roles when product, architecture, UX, backend, frontend or DevOps work is involved.

Stages:

```text
intent
-> SOP Run draft
-> scope and allowed-files gate
-> prompt package drafting
-> Human Owner approval
-> manual prompt handoff
-> Codex result report
-> result intake
-> review
-> QA when required
-> Human Owner decision for that step
-> next step or stop
-> run closure decision
```

Stop conditions:

- missing Human Owner approval;
- unclear parent task;
- unclear SOP;
- missing allowed files or forbidden actions;
- unresolved dependency or blocker;
- changed files outside allowed files;
- verification failed or skipped without accepted reason;
- review/QA finds critical issues;
- requested action would enable automatic execution, merge, push, acceptance or L5 behavior.

Relationship to existing lifecycles:

- task lifecycle defines the parent executable unit;
- prompt lifecycle defines each generated prompt package;
- Codex lifecycle defines execution and result reporting;
- Agent Result Intake checks result completeness and boundaries;
- Integration Review checks combined run output when needed;
- review and QA lifecycles remain gates before Human Owner acceptance;
- verification modes define allowed checks and reporting.

## Required New Governed Entity

Recommended entity name:

```text
SOP Run
```

Alternative name:

```text
Assisted SOP Run
```

Recommendation:

- Use `SOP Run` for the generic managed entity.
- Use `Assisted SOP Run` only for future L4 runs where an approved helper participates.

Relationship to existing entities:

- a SOP Run references one SOP;
- a SOP Run may reference one parent task and multiple prompt packages;
- prompt packages remain governed by Prompt Lifecycle;
- Codex executions remain governed by Codex Lifecycle;
- agent results remain governed by Agent Result Intake;
- combined outputs remain governed by Integration Review;
- Human Owner decisions remain final.

## Required Specs

These are future tasks only. Markdown remains the operational source of truth.

| File | Purpose | Source-of-truth relationship |
|---|---|---|
| `spec/sops.json` | Add `SOP-CODEX-002` inventory entry after Markdown SOP exists. | Derived from `ai-system/sop-model.md`. |
| `spec/sop-run.schema.json` | Machine-checkable SOP Run contract. | Derived from `ai-system/sop-run-lifecycle.md`. |
| `spec/assisted-sop-execution.json` | Optional policy inventory for L4 helper capabilities and forbidden actions. | Derived from `ai-system/assisted-sop-execution.md`. |
| `ai-system/spec/verification-checks.json` | May add SOP-run validation check IDs later. | Derived from verification docs; no behavior by itself. |

## Tooling Plan

Future proposed MVP:

```text
scripts/sop-runner-mvp.py
```

Phase A should be read-only and dry-run/reporting only.

Proposed commands:

```bash
python3 scripts/sop-runner-mvp.py validate-run --project-root .
python3 scripts/sop-runner-mvp.py next-step --project-root .
python3 scripts/sop-runner-mvp.py generate-prompts --project-root .
python3 scripts/sop-runner-mvp.py intake-result --project-root . --result-file <path>
python3 scripts/sop-runner-mvp.py check-boundaries --project-root . --result-file <path>
python3 scripts/sop-runner-mvp.py recommend-state --project-root .
```

Expected inputs:

- `AI_PROJECT/SOP_RUNS.md`;
- `AI_PROJECT/CODEX_TASKS.md`;
- `AI_PROJECT/CODEX_CURRENT.md`;
- prompt package records or draft prompt blocks;
- Codex result reports;
- optional `AI_PROJECT/AGENT_*` records when a run uses Agent Work Packages.

Expected outputs:

- missing-field report;
- gate status report;
- next-step recommendation;
- prompt drafts for review only;
- changed-file boundary report;
- verification summary report;
- suggested state transition for Human Owner review.

Safety boundaries:

- dry-run by default;
- no Codex execution;
- no agent execution;
- no branch/worktree automation;
- no commit, push, merge or PR creation;
- no automatic acceptance;
- no automatic review/QA closure;
- no product or architecture decisions;
- no writes outside explicitly approved future project-control records;
- no runtime maturity change.

Validation strategy:

- Python syntax check;
- JSON/spec parsing if new specs are added;
- fixture validation for valid, blocked, missing-field, out-of-boundary and failed-verification SOP Run cases;
- golden project dry-run validation;
- `python3 scripts/validate-system.py`;
- manual review that helper output remains advisory.

## Required Project Templates

Recommended new project-control file:

```text
AI_PROJECT/SOP_RUNS.md
```

Expected sections:

- Run Registry;
- Active Run;
- Source Documents;
- Scope and Out of Scope;
- Allowed Files and Locked Files;
- Forbidden Actions;
- Planned Steps;
- Prompt Packages;
- Result Intake Records;
- Review and QA Records;
- Human Owner Decisions;
- Verification Summary;
- Risks, Blockers and Stop Conditions;
- Run History.

Relationship to existing `AI_PROJECT/AGENT_*` files:

- `SOP_RUNS.md` is run-level coordination;
- `AGENT_PLAN.md` and `AGENT_TASKS.md` remain package-level planning;
- `AGENT_ASSIGNMENTS.md` remains manual L3 assignment;
- `AGENT_RESULTS.md` may store package result records;
- `SOP_RUNS.md` may reference those records but should not duplicate all details.

## Gate Model

| Gate | Purpose | Blocks when |
|---|---|---|
| Preflight Gate | Confirm source docs, current maturity, approval boundaries and no dirty/conflicting scope. | Source docs missing, runtime ambiguity, unrelated changes block safe edits. |
| Scope Gate | Confirm parent task, scope, out of scope and allowed files. | Scope unclear or files too broad. |
| Prompt Gate | Confirm each prompt has marker, active role, allowed files, forbidden actions and acceptance criteria. | Prompt incomplete or unapproved. |
| Result Intake Gate | Confirm result report has changed files, summary, checks, errors, questions and key changes. | Result incomplete or blockers unresolved. |
| File Boundary Gate | Compare changed files with allowed and locked files. | Out-of-scope files or lock conflicts appear. |
| Verification Gate | Confirm selected mode, budget, executed checks, skipped checks and limitations. | Failed checks or skipped required checks lack accepted reason. |
| Review / QA Gate | Confirm required review and QA have run or are explicitly scoped out with accepted rationale. | Critical/major findings remain unresolved. |
| Decision Gate | Require Human Owner decision for execution, risk acceptance, step closure and run closure. | Human Owner decision missing. |

## Pilot Validation

Required pilot categories before L4 can be experimental:

1. Documentation-only SOP Run.
   - Example: update one source document and its references through L3.5 delegated sequential prompts.
   - Evidence: SOP Run record, prompt packages, Codex reports, validation output, review notes, Human Owner decision.

2. Small tooling/code SOP Run.
   - Example: add a validation-only fixture or parser improvement after docs exist.
   - Evidence: SOP Run record, focused tests, `validate-system.py`, review of no automatic execution boundary.

3. Delegated Codex batch pilot.
   - Example: two or three related documentation/control-file tasks planned under one SOP Run, manually executed one at a time.
   - Evidence: every step has manual approval, result intake, review/QA routing and explicit next-state decision.

L4 experimental entry criteria:

- L3.5 pilots are recorded;
- no critical safety boundary violations occur;
- result intake and integration review are repeatable;
- helper output remains advisory;
- Human Owner explicitly approves a bounded L4 experiment.

## Roadmap

| Level | ID | Name | Status | Notes |
|---|---|---|---|---|
| Goal | G-L4-001 | Safely prepare future L4 Assisted SOP Execution | proposed | Planning only; does not approve L4. |
| Initiative | INIT-L4-001 | L3.5 Bridge and SOP Run Governance | proposed | Define bridge, SOP and governed entity first. |
| Initiative | INIT-L4-002 | Assisted Helper Boundaries and Tooling | proposed | Design then implement only after docs/gates. |
| Initiative | INIT-L4-003 | Pilot Evidence and L4 Decision | proposed | Validate before any experimental L4 declaration. |
| Epic | EPIC-L4-001 | Plan Review and Decisions | proposed | Challenge this plan before execution. |
| Epic | EPIC-L4-002 | L3.5 and SOP-CODEX-002 | proposed | Add delegated sequential batch execution model. |
| Epic | EPIC-L4-003 | SOP Run Lifecycle | proposed | Add governed entity and project template. |
| Epic | EPIC-L4-004 | L4 Assisted Execution Model | proposed | Define helper permissions and restrictions. |
| Epic | EPIC-L4-005 | Specs and Validation Fixtures | proposed | Add machine-checkable contracts after Markdown. |
| Epic | EPIC-L4-006 | Tooling MVP | proposed | Dry-run/reporting helper only. |
| Epic | EPIC-L4-007 | Pilot Validation | proposed | Gather evidence across three pilot types. |
| Epic | EPIC-L4-008 | L4 Readiness Decision | proposed | Human Owner decision only after evidence. |

## Nearest Valuable Tasks

1. Review this plan in a new Codex review chat and challenge unclear boundaries.
2. If approved, create the first execution task for `T-L4-001` only.
3. Do not start `SOP-CODEX-002`, `SOP Run`, specs or tooling until plan review is accepted.

## Open Questions

- Should the bridge be officially named `L3.5`, or should it remain a descriptive bridge without a maturity label?
- Should the governed entity be named `SOP Run` or `Assisted SOP Run` in source documents?
- Should `AI_PROJECT/SOP_RUNS.md` be required for all foldered projects or only for projects using L3.5/L4 workflows?
- Should the first helper be read-only forever, or should a later approved phase allow writes to `AI_PROJECT/SOP_RUNS.md` only?
- Which pilot should count as sufficient evidence for an initial L4 experiment?
- Should `EVOL-027` and `EVOL-028` remain the roadmap IDs for adapter contracts and assisted prototype, or should the L4 transition add narrower successor items?

## Recommended Next Step

Open a new review chat to challenge this planning package against:

- runtime maturity boundaries;
- Human Owner approval preservation;
- review and QA gates;
- forbidden L5 behavior;
- task decomposition clarity;
- whether the proposed L3.5 bridge is useful or unnecessary.


# L4 Assisted SOP Execution Plan - AI Development System

Status: Draft
Version: v0.1.0

## Title

Revised L4 Assisted SOP Execution Plan

## Planning Snapshot

This system evolution planning document records a planning-only roadmap for preparing a possible future L4 Assisted SOP Execution capability.

It lives under `ai-system/evolution/` because L4 planning belongs to system evolution governance. It is not a project-local `AI_PROJECT` file, and it does not approve L4 or any runtime behavior.

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

This plan does not approve L4, implement L4, add runtime behavior, create runner scripts, modify specs, modify lifecycle documents, change current maturity, enable automatic execution, authorize automatic Codex execution, authorize automatic agent dispatch, authorize automatic merge, authorize automatic PR creation, authorize automatic acceptance or authorize automatic QA/review closure.

## Revision Basis

This revision applies the previous review recommendation:

```text
REVISE
```

The Human Owner decisions applied by this plan are:

- `L3.5` may be used only as a transition mode or execution pattern under current L3, not as a separate runtime maturity level.
- Preferred transition pattern name: `Manual Delegated Sequential SOP Run`.
- Current maturity remains `L3 - Manual multi-agent orchestration`.
- L4 remains `Future / Not approved`.
- `SOP-CODEX-002 - Delegated Sequential Batch Execution` is approved for future planning only.
- The governed entity name is `SOP Run`.
- `Assisted SOP Run` is reserved for future approved L4 helper participation.
- A SOP Run may cover one bounded task or one explicitly delegated bounded sequential batch.
- A SOP Run must not represent an open-ended queue or autonomous task discovery.
- `AI_PROJECT/SOP_RUNS.md` is optional and only for projects that opt into SOP Run, delegated batch or future assisted-execution records.
- `scripts/sop-runner-mvp.py` MVP must be strictly read-only.
- Git diff parsing is deferred unless later explicitly approved.
- Test execution must not be performed by `scripts/sop-runner-mvp.py` in MVP.
- Prompt drafts are allowed only for manual review and manual handoff.
- SOP Run records should store summaries, references and paths, not full copied prompt/result text by default.
- Commit, branch, worktree, push, merge and PR operations remain Human Owner-controlled or separate explicitly approved Codex task behavior.
- L4 experiment requires documentation-only, small tooling/code and delegated sequential batch SOP Run pilot evidence first.

## Scope Reduction

This revised plan intentionally narrows the next work.

Near-term work is:

- record decisions and AICP first;
- define the L3 transition wording without changing current maturity;
- add SOP and SOP Run governance in future bounded tasks;
- add templates/specs only after Markdown source documents exist;
- run at least one manual SOP Run pilot before read-only runner MVP implementation;
- require all pilot evidence before any L4 readiness decision.

Near-term work is not:

- implementing a runner;
- adding runtime adapters;
- approving L4;
- adding L5 controlled runtime behavior;
- changing source-of-truth runtime maturity;
- modifying source-of-truth SOP/lifecycle/runtime documents in this planning task.

## Current Boundaries

These boundaries must remain true:

- Human Owner approval remains required for repository-changing execution and final acceptance.
- Candidate parallel groups remain informational until approved under policy.
- Codex executes only bounded, approved tasks or prompts.
- Review and QA remain gates before acceptance.
- No automatic Codex execution.
- No automatic multi-agent execution.
- No automatic branch or worktree lifecycle.
- No automatic commit, push, merge, PR creation or acceptance.
- No automatic QA/review closure.
- No unbounded task discovery.
- No autonomous product, security, privacy, runtime or architecture decisions.

## L3 / Transition Pattern / L4 / L5 Boundary

| Concept | Meaning in this plan | Execution authority | State authority |
|---|---|---|---|
| L3 | Current manual multi-agent orchestration. Humans and ChatGPT manually prepare, hand off, intake and review bounded work. | Manual only after approval. | Manual records only. |
| Manual Delegated Sequential SOP Run | L3 transition pattern toward future L4. A Human Owner approves one bounded task or one bounded sequential batch, but each Codex prompt is still manually reviewed, sent, intaken, reviewed and accepted. | Manual delegated execution, one bounded item at a time. | Manual records; future helpers may only validate or draft when separately approved. |
| L4 | Future assisted execution. A helper may validate gates, prepare next-step artifacts and recommend routing for an approved SOP Run after explicit approval. | Human-approved dispatch remains required. | Helper may assist state handling only within approved boundaries. |
| L5 | Future controlled runtime. A runtime may orchestrate bounded execution under strict policy. | Not approved. Out of scope. | Not approved. Out of scope. |

`Manual Delegated Sequential SOP Run` is not a runtime maturity level. If later documented in source-of-truth runtime files, it should appear as an L3 bridge pattern only and must not be added to the main L0-L6 maturity table.

## Transition Pattern

Preferred name:

```text
Manual Delegated Sequential SOP Run
```

Purpose:

- bridge current L3 manual orchestration and possible future L4 assisted execution;
- prove that SOP Run records, gates and result intake work across one bounded task or a small delegated sequential batch;
- preserve the safe one-task Codex workflow inside a larger approved run plan;
- gather evidence before any assisted helper is allowed to recommend state.

Why it is not full L4:

- no helper advances run state;
- no helper performs result intake beyond reporting/checklist support;
- no helper recommends dispatch from live repository state;
- each prompt remains manually reviewed and sent by the Human Owner or operator.

Why it is not L5:

- no runtime controls execution;
- no queue is executed automatically;
- no branch/worktree lifecycle is automated;
- no acceptance, merge, push, rollback, review or QA closure is automated.

## SOP Run

Entity name:

```text
SOP Run
```

Reserved future L4 name:

```text
Assisted SOP Run
```

A SOP Run is a governed project-control record for one execution attempt of one SOP against one approved parent task or one explicitly delegated bounded sequential batch.

A SOP Run is not:

- an open-ended queue;
- autonomous task discovery;
- execution authority;
- acceptance authority;
- a replacement for task, prompt, Codex, review, QA or result-intake lifecycles.

Required future SOP Run fields should include:

- `run_id`;
- `status`;
- `sop_id`;
- `parent_task`;
- `run_type` such as `single_task` or `delegated_sequential_batch`;
- `active_role`;
- `stage`;
- `source_documents`;
- `scope`;
- `out_of_scope`;
- `allowed_files`;
- `locked_files`;
- `forbidden_actions`;
- `planned_steps`;
- `prompt_package_references`;
- `result_references`;
- `dependencies`;
- `gates`;
- `verification_mode`;
- `verification_budget`;
- `result_intake_records`;
- `review_records`;
- `qa_records`;
- `owner_decisions`;
- `data_sensitivity`;
- `redaction_guidance`;
- `risks`;
- `blockers`;
- `recommended_next_state`;
- `closure_notes`.

SOP Run records should store summaries, references and paths by default. Full copied prompt/result text should be avoided unless a later task explicitly approves it and security/privacy guidance is satisfied. Secrets, credentials and sensitive values must not be copied into SOP Run records.

## SOP-CODEX-002

Future approved planning item:

```text
SOP-CODEX-002 - Delegated Sequential Batch Execution
```

Purpose:

- guide a Human Owner-approved sequence of bounded Codex prompt packages under one SOP Run;
- preserve one prompt/result/review/QA gate at a time;
- allow planning of a batch without enabling automatic execution.

Required safety rules:

- no automatic prompt dispatch;
- no automatic Codex execution;
- no automatic agent dispatch;
- no automatic branch/worktree lifecycle;
- no automatic commit, push, merge or PR creation;
- no automatic acceptance;
- no automatic review or QA closure;
- no autonomous runtime behavior.

## Future Assisted Helper Boundary

The first helper, if later approved, must be read-only.

Allowed MVP behavior:

- read plans and SOP Run records;
- validate readiness;
- generate prompt drafts for manual review;
- validate user-provided result reports;
- compare reported changed files against allowed files;
- summarize verification evidence;
- recommend next state for Human Owner review.

Forbidden MVP behavior:

- write `AI_PROJECT/SOP_RUNS.md`;
- modify project files;
- launch Codex;
- dispatch agents;
- create branches or worktrees;
- run tests automatically;
- create commits;
- push;
- merge;
- open PRs;
- accept results;
- close review or QA;
- make product/security/architecture/runtime decisions;
- parse git diffs unless later explicitly approved.

Prompt draft generation is allowed only as draft output for manual review and manual handoff. Prompt drafts must not be sent automatically to Codex.

Test execution remains manual or Codex-task-specific under approved verification scope.

## Gate Model

| Gate | Purpose | Blocks when |
|---|---|---|
| Decision / AICP Gate | Confirm Human Owner decisions and controlled-evolution path before source-of-truth changes. | Decisions missing, AICP required but absent, or scope implies runtime approval. |
| Scope Gate | Confirm parent task, run type, scope, out of scope, allowed files and forbidden actions. | Scope is open-ended, files are too broad, or the run resembles an autonomous queue. |
| Prompt Gate | Confirm each prompt has marker, active role, allowed files, forbidden actions, acceptance criteria and manual approval. | Prompt incomplete, unapproved or automatically dispatched. |
| Result Intake Gate | Confirm result report has changed files, summary, checks, errors, questions, key changes and safety-boundary compliance. | Result incomplete or blockers unresolved. |
| File Boundary Gate | Compare user-reported changed files with allowed and locked files. | Out-of-scope files or lock conflicts appear. |
| Verification Gate | Confirm selected mode, budget, executed checks, skipped checks and limitations. | Failed checks or skipped required checks lack accepted reason. |
| Security / Privacy Gate | Confirm logs and generated artifacts do not copy secrets or unnecessary sensitive data. | Secret-like values, credentials or unnecessary sensitive material appear in records. |
| Review / QA Gate | Confirm required review and QA have run or are explicitly scoped out with accepted rationale. | Critical/major findings remain unresolved. |
| Decision Gate | Require Human Owner decision for execution, risk acceptance, step closure and run closure. | Human Owner decision missing. |

## Required Future Documents and Artifacts

These are future tasks only. They are not added by this planning task.

| Artifact | Purpose | Required before |
|---|---|---|
| Decision / AICP record | Record Human Owner decisions and controlled-evolution approval path. | Any source-of-truth documentation change. |
| L3 transition wording | Describe Manual Delegated Sequential SOP Run as an L3 bridge pattern only. | SOP Run pilots. |
| `SOP-CODEX-002` | Define delegated sequential batch procedure. | SOP Run pilots. |
| `ai-system/sop-run-lifecycle.md` | Define SOP Run as a managed entity with states, fields, ownership, approvals and audit rules. | Templates, specs and tooling. |
| Optional `AI_PROJECT/SOP_RUNS.md` template | Provide opt-in project-control run records. | Manual SOP Run pilots. |
| `ai-system/assisted-sop-execution.md` | Define future L4 helper capabilities and forbidden runtime behavior. | Runner contract and L4 decision. |
| SOP Run specs and fixtures | Add machine-checkable contracts and blocking examples after Markdown source docs exist. | Runner command contract and MVP. |
| Runner command contract | Define read-only command behavior before implementation. | Read-only runner MVP. |
| Read-only runner MVP | Validate/report only after manual evidence exists. | Later pilots and L4 readiness review. |

## Pilot Validation

Required before any L4 experiment:

1. Documentation-only SOP Run pilot.
   - Evidence: SOP Run record, approval evidence, prompt/result references, result intake, gate validation, blockers/rework/risk decisions, verification evidence and lessons learned.

2. Small tooling/code SOP Run pilot.
   - Evidence: SOP Run record, focused verification, result intake, review/QA or regression notes, boundary review and lessons learned.

3. Delegated sequential batch SOP Run pilot.
   - Evidence: two or three related manual Codex handoffs, each with manual approval, result intake, review/QA routing, explicit next-state decision and final Human Owner decision.

L4 experimental entry criteria:

- all required pilot categories are recorded or explicitly deferred by the Human Owner with rationale;
- no critical safety boundary violations occur;
- result intake and integration review are repeatable;
- helper output remains advisory;
- Human Owner explicitly approves a bounded L4 experiment.

## Revised Task Sequence

| ID | Name | Status | Purpose |
|---|---|---|---|
| T-L4-001 | Plan Review | done | Challenge the original plan and return `REVISE`. |
| T-L4-002 | Human Owner Decisions + AICP | proposed | Record decisions and controlled-evolution approval before source-of-truth changes. |
| T-L4-003 | L3 Transition Wording | proposed | Define Manual Delegated Sequential SOP Run as an L3 bridge pattern only. |
| T-L4-004 | SOP-CODEX-002 | proposed | Add the delegated sequential batch SOP in a bounded future task. |
| T-L4-005 | SOP Run Lifecycle | proposed | Define SOP Run before templates, specs or tooling. |
| T-L4-006 | SOP_RUNS Template + Golden Example | proposed | Add optional project-control records after lifecycle exists. |
| T-L4-007 | Assisted Execution Model | proposed | Define future L4 helper boundaries without approving L4. |
| T-L4-008 | SOP Run Specs + Fixtures | proposed | Add derived contracts and blocking fixtures after Markdown docs. |
| T-L4-009 | Runner Command Contract | proposed | Design read-only helper commands before implementation. |
| T-L4-010 | Documentation-Only Pilot | proposed | Gather first manual SOP Run evidence before runner implementation. |
| T-L4-011 | Read-Only Runner MVP | proposed | Implement read-only validation/reporting only after governance and first pilot. |
| T-L4-012 | Small Tooling Pilot | proposed | Validate SOP Run handling with a bounded tooling/code task. |
| T-L4-013 | Delegated Sequential Batch Pilot | proposed | Validate multiple manual handoffs under one SOP Run. |
| T-L4-014 | L4 Readiness Decision | proposed | Decide whether to continue, defer or approve a bounded L4 experiment. |

## Suggested Implementation Batches

Batch 1: decisions, AICP and L3 transition wording.

Batch 2: `SOP-CODEX-002` and SOP Run lifecycle.

Batch 3: optional SOP Run template, golden example and assisted-execution model.

Batch 4: SOP Run specs, fixtures and runner command contract.

Batch 5: documentation-only manual pilot.

Batch 6: read-only runner MVP.

Batch 7: small tooling pilot and delegated sequential batch pilot.

Batch 8: L4 readiness decision.

## Non-Blocking Future Questions

- Should the later L4 experiment use `Assisted SOP Run` as a distinct label only when a helper participates?
- Should full copied prompt/result text ever be allowed in SOP Run logs, or should references remain the permanent default?
- Which later task, if any, should approve git diff parsing?

## Recommended Next Step

Prepare `T-L4-002 - Human Owner Decisions + AICP` as the next bounded task before changing source-of-truth runtime, SOP or lifecycle documents.

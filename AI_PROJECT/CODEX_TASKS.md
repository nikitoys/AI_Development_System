# Codex Tasks - AI Development System

## Backlog

| ID | Status | Initiative | Epic | Task | Verification Mode | Notes |
|---|---|---|---|---|---|---|
| T-L4-001 | proposed | INIT-L4-001 | EPIC-L4-001 | Review and clarify the L4 Assisted SOP Execution Plan | FAST | Review-only/planning task. |
| T-L4-002 | proposed | INIT-L4-001 | EPIC-L4-002 | Decide whether to introduce the L3.5 bridge | STANDARD | Documentation/governance decision task. |
| T-L4-003 | proposed | INIT-L4-001 | EPIC-L4-002 | Add `SOP-CODEX-002 - Delegated Sequential Batch Execution` | STANDARD | Future source-doc/spec update after approval. |
| T-L4-004 | proposed | INIT-L4-001 | EPIC-L4-003 | Add SOP Run lifecycle document | STANDARD | Future governed-entity task. |
| T-L4-005 | proposed | INIT-L4-001 | EPIC-L4-003 | Add SOP Run project-control template and golden example | STANDARD | Future template/example task. |
| T-L4-006 | proposed | INIT-L4-002 | EPIC-L4-004 | Add L4 Assisted SOP Execution model document | STANDARD | Defines helper boundaries without implementation. |
| T-L4-007 | proposed | INIT-L4-002 | EPIC-L4-005 | Add SOP Run and assisted-execution specs | STANDARD | Specs derived from Markdown only. |
| T-L4-008 | proposed | INIT-L4-002 | EPIC-L4-006 | Design `scripts/sop-runner-mvp.py` command contract | FAST | Planning/design only; no script implementation. |
| T-L4-009 | proposed | INIT-L4-002 | EPIC-L4-006 | Implement read-only `scripts/sop-runner-mvp.py` MVP | STANDARD | Future tooling; dry-run/reporting only. |
| T-L4-010 | proposed | INIT-L4-003 | EPIC-L4-007 | Run documentation-only L3.5 pilot | STANDARD | Manual delegated sequence; no helper writes. |
| T-L4-011 | proposed | INIT-L4-003 | EPIC-L4-007 | Run small tooling/code L3.5 pilot | STANDARD | Manual delegated sequence; boundary validation required. |
| T-L4-012 | proposed | INIT-L4-003 | EPIC-L4-007 | Run delegated Codex batch pilot | STANDARD | Multiple manual prompt handoffs under one SOP Run. |
| T-L4-013 | proposed | INIT-L4-003 | EPIC-L4-008 | Review L4 readiness and record Human Owner decision | STANDARD | Decision task only; may defer L4. |

## Task Details

### T-L4-001 - Review and clarify the L4 Assisted SOP Execution Plan

Status: proposed

Epic: EPIC-L4-001

Purpose:

- Challenge the planning package before any source-of-truth document changes begin.

Scope:

- Review `AI_PROJECT/CODEX_PLAN.md`, `AI_PROJECT/CODEX_TASKS.md` and `AI_PROJECT/CODEX_CURRENT.md`.
- Identify unclear L3.5/L4/L5 boundaries.
- Identify missing source documents, acceptance criteria, risks or stop conditions.
- Produce a review recommendation: `APPROVED`, `REWORK` or `DEFERRED`.

Out of Scope:

- Do not edit source-of-truth documents.
- Do not add SOPs, specs, scripts or templates.
- Do not implement L4.

Allowed Files:

- `AI_PROJECT/CODEX_PLAN.md`
- `AI_PROJECT/CODEX_TASKS.md`
- `AI_PROJECT/CODEX_CURRENT.md`

Acceptance Criteria:

- Review checks Human Owner approval preservation.
- Review checks automatic execution, merge, push and acceptance remain forbidden.
- Review checks tasks are independently executable.
- Review lists blocking questions before any execution task starts.

Verification:

- Mode: FAST.
- Run `python3 scripts/validate-system.py` if files changed.

Dependencies:

- Current planning files exist.

Risk:

- Low.

Stop Conditions:

- Plan implies L4 approval.
- Plan asks to implement runtime before review.
- Required source documents are missing.

### T-L4-002 - Decide whether to introduce the L3.5 bridge

Status: proposed

Epic: EPIC-L4-002

Purpose:

- Decide whether `L3.5 - SOP-driven delegated sequential batch execution` should become an official bridge concept.

Scope:

- Analyze whether L3.5 is useful or whether existing L3 and future L4 are enough.
- If approved, update runtime and manual-orchestration documentation to describe the bridge without changing current maturity.
- Record that L3 remains current and L4 remains future/not approved.

Out of Scope:

- Do not implement helper tooling.
- Do not add SOP Run lifecycle.
- Do not declare L4 approved.

Allowed Files:

- `ai-system/runtime-maturity-levels.md`
- `ai-system/manual-orchestration.md`
- `ai-system/operating-model.md`
- `ai-system/README.md`
- `README.md`
- `README.ru.md`
- `ai-system/evolution/roadmap.md`
- `ai-system/evolution/evolution-backlog.md`
- `ai-system/system-changelog.md`

Acceptance Criteria:

- Human Owner decision on L3.5 is explicit.
- Current maturity remains `L3 - Manual multi-agent orchestration`.
- Runtime decision remains `DEFERRED`.
- L4+ remains future/not approved.
- No automatic execution behavior is introduced.

Verification:

- Mode: STANDARD.
- Run `python3 scripts/validate-system.py`.

Dependencies:

- T-L4-001 approved or reworked.

Risk:

- Medium, because maturity wording can imply authority if unclear.

Stop Conditions:

- Human Owner does not approve adding L3.5.
- Wording would make L3.5 look like runtime approval.

### T-L4-003 - Add `SOP-CODEX-002 - Delegated Sequential Batch Execution`

Status: proposed

Epic: EPIC-L4-002

Purpose:

- Add a SOP for manually delegated, sequential Codex batch execution under one bounded run plan.

Scope:

- Define purpose, trigger, applicable scope, roles, stages, gates, inputs, outputs, stop conditions and review/QA relationship.
- Explain relationship to task, prompt, Codex, result intake, integration review and verification lifecycles.
- Update SOP inventory only after Markdown SOP exists.

Out of Scope:

- Do not add runner scripts.
- Do not create `AI_PROJECT/SOP_RUNS.md`.
- Do not enable automatic prompt dispatch.
- Do not approve L4.

Allowed Files:

- `ai-system/sop-model.md`
- `spec/sops.json`
- `ai-system/README.md`
- `README.md`
- `README.ru.md`
- `ai-system/evolution/roadmap.md`
- `ai-system/evolution/evolution-backlog.md`
- `ai-system/system-changelog.md`

Acceptance Criteria:

- SOP-CODEX-002 preserves one prompt/result/review/QA gate at a time.
- Human Owner approval points are explicit.
- Stop conditions include file-boundary, verification, review/QA and automation violations.
- Spec entry is derived from Markdown and does not override it.

Verification:

- Mode: STANDARD.
- Run `python3 scripts/validate-system.py`.
- Run JSON parse checks through validation.

Dependencies:

- T-L4-001 approved.
- T-L4-002 approved if L3.5 label is used.

Risk:

- Medium.

Stop Conditions:

- SOP wording implies automatic execution.
- SOP conflicts with prompt or Codex lifecycle.

### T-L4-004 - Add SOP Run lifecycle document

Status: proposed

Epic: EPIC-L4-003

Purpose:

- Define SOP Run as a managed entity before project templates or helper tooling depend on it.

Scope:

- Add lifecycle states, operations, required fields, ownership, approval rules, audit/history rules and relationships to task, prompt, Codex, review, QA, result intake and integration review.

Out of Scope:

- Do not add scripts.
- Do not add project templates.
- Do not enable state writes by tooling.

Allowed Files:

- `ai-system/sop-run-lifecycle.md`
- `ai-system/operating-model.md`
- `ai-system/README.md`
- `README.md`
- `README.ru.md`
- `ai-system/evolution/roadmap.md`
- `ai-system/evolution/evolution-backlog.md`
- `ai-system/system-changelog.md`

Acceptance Criteria:

- SOP Run required fields are defined.
- Lifecycle states do not replace task, prompt or Codex lifecycle states.
- Human Owner approval and final acceptance remain required.
- Boundary rules forbid automatic execution, merge, push and acceptance.

Verification:

- Mode: STANDARD.
- Run `python3 scripts/validate-system.py`.

Dependencies:

- T-L4-001 approved.
- T-L4-003 approved or planned in same reviewed sequence.

Risk:

- Medium.

Stop Conditions:

- Lifecycle states conflict with existing managed entities.
- SOP Run would become execution authority by itself.

### T-L4-005 - Add SOP Run project-control template and golden example

Status: proposed

Epic: EPIC-L4-003

Purpose:

- Make SOP Runs recordable in concrete projects without enabling runtime behavior.

Scope:

- Add `AI_PROJECT/SOP_RUNS.md` template.
- Add golden project example record for a non-runtime SOP Run.
- Update project-control documentation and validation to discover the file if approved.

Out of Scope:

- Do not add helper script behavior.
- Do not automatically create SOP Runs in existing projects.
- Do not mark any run as accepted without Human Owner decision.

Allowed Files:

- `ai-system/project-control-files.md`
- `ai-system/project-control-connectivity.md`
- `ai-system/foldered-integration.md`
- `ai-system/project-bootstrap.md`
- `ai-system/project-system-update.md`
- `ai-system/templates/foldered/AI_PROJECT/SOP_RUNS.md`
- `ai-system/templates/foldered/AI_PROJECT/PROJECT_CONTROL_INDEX.md`
- `ai-system/templates/project/SOP_RUNS.md`
- `ai-system/templates/project/PROJECT_CONTROL_INDEX.md`
- `examples/golden-project/AI_PROJECT/SOP_RUNS.md`
- `examples/golden-project/AI_PROJECT/PROJECT_CONTROL_INDEX.md`
- `scripts/validate-system.py`
- `ai-system/README.md`
- `README.md`
- `README.ru.md`
- `ai-system/system-changelog.md`

Acceptance Criteria:

- Template records run state, gates, prompts, results, review/QA and owner decisions.
- Template states it does not authorize execution or acceptance.
- Golden example is non-runtime.
- Validation remains read-only.

Verification:

- Mode: STANDARD.
- Run `python3 scripts/validate-system.py`.

Dependencies:

- T-L4-004 done.

Risk:

- Medium, because project-control files can be mistaken for execution authority.

Stop Conditions:

- Template suggests automatic dispatch.
- Existing control index behavior is weakened.

### T-L4-006 - Add L4 Assisted SOP Execution model document

Status: proposed

Epic: EPIC-L4-004

Purpose:

- Define future L4 helper capabilities and forbidden behavior before any helper implementation.

Scope:

- Add a source document describing L4 assisted execution, helper permissions, helper prohibitions, gate model, result intake support and next-state recommendation rules.

Out of Scope:

- Do not implement helper scripts.
- Do not approve L4 experiment.
- Do not change current maturity level.

Allowed Files:

- `ai-system/assisted-sop-execution.md`
- `ai-system/runtime-maturity-levels.md`
- `ai-system/operating-model.md`
- `ai-system/README.md`
- `README.md`
- `README.ru.md`
- `ai-system/evolution/roadmap.md`
- `ai-system/evolution/evolution-backlog.md`
- `ai-system/system-changelog.md`

Acceptance Criteria:

- Document explicitly distinguishes L3, L3.5, L4 and L5.
- Helper may recommend, validate and draft only inside approved scope.
- Helper must not execute Codex, dispatch agents, merge, push, accept or close review/QA.
- L4 remains future/not approved unless Human Owner separately approves an experiment.

Verification:

- Mode: STANDARD.
- Run `python3 scripts/validate-system.py`.

Dependencies:

- T-L4-001 approved.
- T-L4-004 done or planned.

Risk:

- High if wording blurs assisted execution and controlled runtime.

Stop Conditions:

- Document creates runtime authority.
- Human Owner has not approved L4 model documentation.

### T-L4-007 - Add SOP Run and assisted-execution specs

Status: proposed

Epic: EPIC-L4-005

Purpose:

- Add machine-checkable contracts after Markdown source documents exist.

Scope:

- Add `spec/sop-run.schema.json`.
- Optionally add `spec/assisted-sop-execution.json`.
- Update `spec/README.md`.
- Update validation to parse the new specs.

Out of Scope:

- Do not generate Markdown from specs.
- Do not allow specs to override Markdown.
- Do not implement runtime behavior.

Allowed Files:

- `spec/sop-run.schema.json`
- `spec/assisted-sop-execution.json`
- `spec/README.md`
- `scripts/validate-system.py`
- `ai-system/README.md`
- `README.md`
- `README.ru.md`
- `ai-system/system-changelog.md`

Acceptance Criteria:

- Specs parse as JSON.
- Specs declare Markdown source documents.
- Specs preserve forbidden automation boundaries.
- Validation remains read-only.

Verification:

- Mode: STANDARD.
- Run `python3 scripts/validate-system.py`.
- Run focused JSON parse if validation output is insufficient.

Dependencies:

- T-L4-004 done.
- T-L4-006 done if assisted-execution policy spec is included.

Risk:

- Medium.

Stop Conditions:

- Spec conflicts with Markdown.
- Spec implies execution authority.

### T-L4-008 - Design `scripts/sop-runner-mvp.py` command contract

Status: proposed

Epic: EPIC-L4-006

Purpose:

- Design helper commands and fixtures before implementation.

Scope:

- Produce a documentation-only command contract for `validate-run`, `next-step`, `generate-prompts`, `intake-result`, `check-boundaries` and `recommend-state`.
- Define inputs, outputs, fixture cases, safety boundaries and validation expectations.

Out of Scope:

- Do not implement `scripts/sop-runner-mvp.py`.
- Do not add runtime adapters.
- Do not write SOP Run state.

Allowed Files:

- `AI_PROJECT/CODEX_PLAN.md`
- `AI_PROJECT/CODEX_TASKS.md`
- `AI_PROJECT/CODEX_CURRENT.md`
- optional future design doc if approved: `ai-system/sop-runner-mvp-plan.md`

Acceptance Criteria:

- Command contract is complete enough for a later implementation task.
- All commands are dry-run/reporting by default.
- Forbidden actions are explicit.
- Fixture strategy covers valid, missing-field, blocked, out-of-scope and failed-verification cases.

Verification:

- Mode: FAST.
- Run `python3 scripts/validate-system.py` if source docs changed.

Dependencies:

- T-L4-004 done.
- T-L4-006 done or reviewed.

Risk:

- Low to medium.

Stop Conditions:

- Design implies automatic execution or state writes without approval.

### T-L4-009 - Implement read-only `scripts/sop-runner-mvp.py` MVP

Status: proposed

Epic: EPIC-L4-006

Purpose:

- Add a dry-run/reporting helper for SOP Run validation and next-step recommendation.

Scope:

- Implement read-only commands from the approved command contract.
- Add fixtures and validation.
- Ensure helper does not modify project files or execute Codex.

Out of Scope:

- Do not implement automatic Codex execution.
- Do not create branches, worktrees, commits, pushes, merges or PRs.
- Do not accept results.
- Do not write `AI_PROJECT/SOP_RUNS.md` unless a separate future task approves that.

Allowed Files:

- `scripts/sop-runner-mvp.py`
- `scripts/validate-system.py`
- `examples/sop-run-fixtures/**`
- `examples/golden-project/AI_PROJECT/SOP_RUNS.md`
- `ai-system/README.md`
- `README.md`
- `README.ru.md`
- `ai-system/evolution/roadmap.md`
- `ai-system/evolution/evolution-backlog.md`
- `ai-system/system-changelog.md`

Acceptance Criteria:

- Helper prints a boundary statement.
- Helper validates required SOP Run fields.
- Helper reports next-step recommendations without executing them.
- Helper checks result reports against allowed files where data exists.
- Fixtures cover success and blocking cases.
- `validate-system.py` remains read-only and passes.

Verification:

- Mode: STANDARD.
- Run `python3 -m py_compile scripts/sop-runner-mvp.py scripts/validate-system.py`.
- Run helper fixture validation.
- Run `python3 scripts/validate-system.py`.

Dependencies:

- T-L4-004 done.
- T-L4-005 done.
- T-L4-007 done if schema validation is required.
- T-L4-008 approved.

Risk:

- High, because helper tooling can be mistaken for runtime.

Stop Conditions:

- Implementation needs writes or execution to be useful.
- Helper cannot preserve no-runtime boundary.

### T-L4-010 - Run documentation-only L3.5 pilot

Status: proposed

Epic: EPIC-L4-007

Purpose:

- Validate SOP Run records and delegated sequential handling on low-risk documentation work.

Scope:

- Select a small documentation-only system task.
- Record a SOP Run.
- Manually execute one bounded prompt at a time.
- Record result intake, review/QA routing, verification and Human Owner decisions.

Out of Scope:

- Do not use automatic execution.
- Do not run product/application code changes.
- Do not declare L4 experimental.

Allowed Files:

- `AI_PROJECT/SOP_RUNS.md`
- selected documentation files approved by the pilot prompt
- required README/index/changelog files for that selected documentation task

Acceptance Criteria:

- Pilot record shows every approval and stop condition.
- Result intake catches missing or skipped verification.
- Review confirms no runtime behavior was introduced.
- Human Owner decision is recorded.

Verification:

- Mode: STANDARD.
- Run `python3 scripts/validate-system.py`.

Dependencies:

- T-L4-003 done.
- T-L4-004 done.
- T-L4-005 done.

Risk:

- Medium.

Stop Conditions:

- Pilot scope requires behavior-changing system edits without approval.
- Manual prompt handoff becomes ambiguous.

### T-L4-011 - Run small tooling/code L3.5 pilot

Status: proposed

Epic: EPIC-L4-007

Purpose:

- Validate SOP Run handling with a small bounded tooling change while preserving dry-run/runtime boundaries.

Scope:

- Select one small validation-only script or fixture improvement.
- Record SOP Run plan, prompt, result, verification, review and QA/regression notes.

Out of Scope:

- Do not implement L4 helper writes.
- Do not add runtime adapters.
- Do not automate Codex execution.

Allowed Files:

- `AI_PROJECT/SOP_RUNS.md`
- selected script/fixture files approved by the pilot prompt
- required docs/changelog/index files for the selected task

Acceptance Criteria:

- SOP Run records changed files and verification evidence.
- Helper or manual checks prove no automatic execution behavior was added.
- Regression checks are documented.
- Human Owner final decision is recorded.

Verification:

- Mode: STANDARD.
- Run focused compile/tests for touched scripts.
- Run `python3 scripts/validate-system.py`.

Dependencies:

- T-L4-010 completed or explicitly deferred.
- T-L4-009 optional if testing helper output; otherwise manual-only.

Risk:

- Medium to high.

Stop Conditions:

- Tooling change requires execution automation.
- Verification fails and no rework is approved.

### T-L4-012 - Run delegated Codex batch pilot

Status: proposed

Epic: EPIC-L4-007

Purpose:

- Validate two or three related manual Codex handoffs under one SOP Run.

Scope:

- Prepare a bounded batch with sequential steps.
- Manually review and send each prompt.
- Intake each result before preparing the next handoff.
- Run integration review before final Human Owner decision.

Out of Scope:

- Do not execute prompts automatically.
- Do not approve parallel execution by implication.
- Do not merge, push or accept automatically.

Allowed Files:

- `AI_PROJECT/SOP_RUNS.md`
- `AI_PROJECT/CODEX_PLAN.md`
- `AI_PROJECT/CODEX_TASKS.md`
- `AI_PROJECT/CODEX_CURRENT.md`
- step-specific files approved in each prompt

Acceptance Criteria:

- Each step has prompt approval, result report, intake, verification and review route.
- The run records blocked/rework states if they occur.
- Integration Review checks combined result before closure.
- Human Owner decides final status.

Verification:

- Mode: STANDARD.
- Run checks required by each step.
- Run `python3 scripts/validate-system.py` for system-documentation batches.

Dependencies:

- T-L4-010 completed.
- T-L4-011 completed or explicitly deferred with rationale.

Risk:

- High, because batch handling can drift toward runtime behavior.

Stop Conditions:

- Any step wants automatic dispatch.
- Changed files exceed approved step scope.
- Review or QA gate is bypassed.

### T-L4-013 - Review L4 readiness and record Human Owner decision

Status: proposed

Epic: EPIC-L4-008

Purpose:

- Decide whether evidence supports a bounded L4 experiment, continued L3.5 pilots, or deferral.

Scope:

- Review pilot evidence.
- Assess safety boundary violations, verification quality, review/QA effectiveness and Human Owner control.
- Record decision: `APPROVED`, `REWORK`, `REJECTED`, `DEFERRED` or `EXPERIMENT`.

Out of Scope:

- Do not implement L4 experiment in this task.
- Do not implement L5 controlled runtime.
- Do not change current maturity unless Human Owner explicitly approves that separate outcome.

Allowed Files:

- `ai-system/evolution/roadmap.md`
- `ai-system/evolution/evolution-backlog.md`
- `ai-system/runtime-maturity-levels.md`
- `ai-system/evolution/sop-multi-agent-pilot-validation.md`
- `ai-system/system-changelog.md`
- `README.md`
- `README.ru.md`
- `ai-system/README.md`
- `AI_PROJECT/SOP_RUNS.md`

Acceptance Criteria:

- Decision is explicit and dated.
- Evidence is listed.
- If decision is `DEFERRED`, next evidence gaps are listed.
- If decision is `EXPERIMENT`, scope, duration, success criteria, failure criteria and rollback/stop rules are defined.
- Automatic acceptance, merge, push, unbounded execution and L5 behavior remain forbidden.

Verification:

- Mode: STANDARD.
- Run `python3 scripts/validate-system.py`.

Dependencies:

- T-L4-010 completed.
- T-L4-011 completed or explicitly deferred.
- T-L4-012 completed or explicitly deferred.

Risk:

- High.

Stop Conditions:

- Pilot evidence is insufficient.
- Human Owner does not approve an experiment.
- L4 readiness would require L5 capabilities.

## Status Values

```text
proposed
approved
in_progress
blocked
review
rework
done
cancelled
deferred
```

## Global L4 Transition Stop Conditions

- Any task claims L4 is approved before Human Owner decision.
- Any task changes current maturity away from L3 without explicit approval.
- Any task enables automatic Codex execution, automatic multi-agent execution, automatic branch/worktree lifecycle, automatic merge, automatic push, automatic acceptance or automatic QA/review closure.
- Any task implements L5 controlled runtime.
- Any task expands allowed files without a new approved prompt.
- Any task bypasses review, QA or Human Owner decision gates.


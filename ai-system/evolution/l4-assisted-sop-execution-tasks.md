# L4 Assisted SOP Execution Tasks - AI Development System

Status: Draft  
Version: v0.1.0

This is a system evolution task board for L4 Assisted SOP Execution planning.
It is not a project-local `AI_PROJECT` task board.

These tasks are child operational tasks under a system evolution campaign. They do not replace `ai-system/evolution/evolution-backlog.md`, do not authorize L4 and still require bounded Human Owner approval before execution.

## Backlog

| ID | Status | Initiative | Epic | Task | Verification Mode | Notes |
|---|---|---|---|---|---|---|
| T-L4-001 | done | INIT-L4-001 | EPIC-L4-001 | Plan Review | NONE | Review completed; recommendation was `REVISE`. |
| T-L4-002 | proposed | INIT-L4-001 | EPIC-L4-001 | Human Owner Decisions + AICP | FAST | Decision/control task before source-of-truth changes. |
| T-L4-003 | proposed | INIT-L4-001 | EPIC-L4-002 | L3 Transition Wording | STANDARD | Describes bridge pattern under L3 only. |
| T-L4-004 | proposed | INIT-L4-001 | EPIC-L4-002 | SOP-CODEX-002 | STANDARD | Future SOP documentation task. |
| T-L4-005 | proposed | INIT-L4-001 | EPIC-L4-003 | SOP Run Lifecycle | STANDARD | Governed entity before templates/specs/tooling. |
| T-L4-006 | proposed | INIT-L4-001 | EPIC-L4-003 | SOP_RUNS Template + Golden Example | STANDARD | Optional project-control records only. |
| T-L4-007 | proposed | INIT-L4-002 | EPIC-L4-004 | Assisted Execution Model | STANDARD | Defines future L4 helper boundaries without approving L4. |
| T-L4-008 | proposed | INIT-L4-002 | EPIC-L4-005 | SOP Run Specs + Fixtures | STANDARD | Specs derived from Markdown only. |
| T-L4-009 | proposed | INIT-L4-002 | EPIC-L4-006 | Runner Command Contract | FAST | Design-only command contract. |
| T-L4-010 | proposed | INIT-L4-003 | EPIC-L4-007 | Documentation-Only Pilot | STANDARD | First manual SOP Run evidence before runner MVP. |
| T-L4-011 | proposed | INIT-L4-002 | EPIC-L4-006 | Read-Only Runner MVP | STANDARD | Read-only validation/reporting only. |
| T-L4-012 | proposed | INIT-L4-003 | EPIC-L4-007 | Small Tooling Pilot | STANDARD | Bounded tooling/code SOP Run pilot. |
| T-L4-013 | proposed | INIT-L4-003 | EPIC-L4-007 | Delegated Sequential Batch Pilot | STANDARD | Multiple manual handoffs under one SOP Run. |
| T-L4-014 | proposed | INIT-L4-003 | EPIC-L4-008 | L4 Readiness Decision | STANDARD | Final decision task; does not implement L4. |

## Task Details

### T-L4-001 - Plan Review

Status: done

Purpose:

- Challenge the original L4 planning package before any source-of-truth document changes begin.

Scope:

- Review `ai-system/evolution/l4-assisted-sop-execution-plan.md`, `ai-system/evolution/l4-assisted-sop-execution-tasks.md` and `ai-system/evolution/current-evolution-task.md`.
- Identify unclear L3 bridge, L4 and L5 boundaries.
- Identify missing source documents, acceptance criteria, risks and stop conditions.
- Produce a review recommendation.

Out of Scope:

- Do not edit source-of-truth documents.
- Do not add SOPs, specs, scripts or templates.
- Do not implement L4.

Allowed Files:

- None for review-only execution.

Acceptance Criteria:

- Review checks Human Owner approval preservation.
- Review checks automatic execution, merge, push and acceptance remain forbidden.
- Review checks tasks are independently executable.
- Review lists blocking questions before any execution task starts.

Verification:

- Mode: NONE.
- Read-only inspection commands may be reported.

Dependencies:

- Current planning files exist.

Risk:

- Low.

Stop Conditions:

- Plan implies L4 approval.
- Plan asks to implement runtime before review.
- Required source documents are missing.

### T-L4-002 - Human Owner Decisions + AICP

Status: proposed

Purpose:

- Record Human Owner decisions and the controlled-evolution approval path before changing source-of-truth runtime, SOP or lifecycle documents.

Scope:

- Create or update a decision/AICP planning artifact for the L3 transition pattern, `SOP-CODEX-002`, SOP Run naming, helper boundaries, pilot requirements and L4 decision gates.
- Confirm that current maturity remains `L3 - Manual multi-agent orchestration`.
- Confirm that L4 remains `Future / Not approved`.

Out of Scope:

- Do not update source-of-truth runtime, SOP, lifecycle or spec documents.
- Do not implement helper tooling.
- Do not add `AI_PROJECT/SOP_RUNS.md`.
- Do not declare L4 approved.

Allowed Files:

- `ai-system/evolution/l4-assisted-sop-execution-plan.md`
- `ai-system/evolution/l4-assisted-sop-execution-tasks.md`
- `ai-system/evolution/current-evolution-task.md`
- future approved AICP or decision artifact if the Human Owner requests it

Acceptance Criteria:

- Human Owner decisions are explicit and traceable.
- AICP requirement is assessed before source-of-truth changes.
- `Manual Delegated Sequential SOP Run` is recorded as a transition pattern under L3, not a separate runtime maturity level.
- Current maturity remains L3.
- L4 remains future/not approved.
- No automatic execution behavior is introduced.

Verification:

- Mode: FAST.
- Run `python3 scripts/validate-system.py` if source documents change.

Dependencies:

- T-L4-001 done.

Risk:

- Medium, because missing decision traceability can make later documentation changes appear approved by implication.

Stop Conditions:

- Human Owner decisions are incomplete.
- AICP or approval requirements are unclear.
- The task would change source-of-truth behavior before decision traceability exists.

### T-L4-003 - L3 Transition Wording

Status: proposed

Purpose:

- Describe `Manual Delegated Sequential SOP Run` as an L3 bridge pattern without changing current maturity or adding a separate L3.5 level.

Scope:

- Update approved runtime/manual-orchestration references only after T-L4-002.
- State that the pattern supports one bounded task or one explicitly delegated bounded sequential batch.
- State that it is not an open-ended queue or autonomous task discovery.

Out of Scope:

- Do not add L3.5 as a separate runtime maturity level in the L0-L6 table.
- Do not approve L4.
- Do not add SOP Run lifecycle or templates.
- Do not implement helper tooling.

Allowed Files:

- `ai-system/runtime-maturity-levels.md`
- `ai-system/manual-orchestration.md`
- `ai-system/README.md`
- `README.md`
- `README.ru.md`
- `ai-system/evolution/roadmap.md`
- `ai-system/evolution/evolution-backlog.md`
- `ai-system/system-changelog.md`

Acceptance Criteria:

- Current maturity remains `L3 - Manual multi-agent orchestration`.
- Runtime decision remains `DEFERRED`.
- L4+ remains future/not approved.
- The main L0-L6 maturity table is not expanded with L3.5.
- No automatic execution behavior is introduced.

Verification:

- Mode: STANDARD.
- Run `python3 scripts/validate-system.py`.

Dependencies:

- T-L4-002 done.

Risk:

- Medium, because transition wording can imply new runtime authority if unclear.

Stop Conditions:

- Wording would make the transition pattern look like runtime approval.
- Wording would change current maturity away from L3.

### T-L4-004 - SOP-CODEX-002

Status: proposed

Purpose:

- Add `SOP-CODEX-002 - Delegated Sequential Batch Execution` as a future SOP for manual, bounded, sequential Codex handoffs under one SOP Run.

Scope:

- Define purpose, trigger, applicable scope, roles, stages, gates, inputs, outputs, stop conditions and review/QA relationship.
- Preserve one prompt/result/review/QA gate at a time.
- Update derived SOP inventory only after Markdown SOP exists.

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

- SOP preserves one prompt/result/review/QA gate at a time.
- Human Owner approval points are explicit.
- Stop conditions include file-boundary, verification, review/QA, security/privacy and automation violations.
- Spec entry is derived from Markdown and does not override it.
- No queue, autonomous discovery or runtime dispatch semantics are introduced.

Verification:

- Mode: STANDARD.
- Run `python3 scripts/validate-system.py`.

Dependencies:

- T-L4-002 done.
- T-L4-003 done or explicitly deferred with rationale.

Risk:

- Medium.

Stop Conditions:

- SOP wording implies automatic execution.
- SOP conflicts with prompt, Codex, review or QA lifecycle.

### T-L4-005 - SOP Run Lifecycle

Status: proposed

Purpose:

- Define SOP Run as a governed entity before project templates, specs, fixtures or helper tooling depend on it.

Scope:

- Add lifecycle states, operations, required fields, ownership, approval rules, audit/history rules and relationships to task, prompt, Codex, review, QA, result intake and integration review.
- Define `single_task` and `delegated_sequential_batch` run types.
- Define data sensitivity and redaction guidance fields.

Out of Scope:

- Do not add scripts.
- Do not add project templates.
- Do not enable state writes by tooling.
- Do not approve L4.

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
- Lifecycle states do not replace task, prompt, Codex, review, QA or result-intake lifecycle states.
- Human Owner approval and final acceptance remain required.
- Boundary rules forbid automatic execution, merge, push, PR creation and acceptance.
- Records store summaries, references and paths by default instead of full copied sensitive text.

Verification:

- Mode: STANDARD.
- Run `python3 scripts/validate-system.py`.

Dependencies:

- T-L4-004 done.

Risk:

- High, because SOP Run can be mistaken for execution authority.

Stop Conditions:

- Lifecycle states conflict with existing managed entities.
- SOP Run would become execution or acceptance authority.

### T-L4-006 - SOP_RUNS Template + Golden Example

Status: proposed

Purpose:

- Make SOP Runs recordable for opt-in projects without enabling runtime behavior.

Scope:

- Add optional `AI_PROJECT/SOP_RUNS.md` templates.
- Add a non-runtime golden project example.
- Update project-control documentation and validation to discover the optional file if approved.

Out of Scope:

- Do not require `SOP_RUNS.md` for all projects.
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

- Template records run state, gates, prompt/result references, result intake, review/QA, owner decisions, sensitivity and redaction guidance.
- Template states it does not authorize execution or acceptance.
- Golden example is non-runtime.
- Validation remains read-only.
- `SOP_RUNS.md` is optional and opt-in.

Verification:

- Mode: STANDARD.
- Run `python3 scripts/validate-system.py`.

Dependencies:

- T-L4-005 done.

Risk:

- Medium, because project-control files can be mistaken for execution authority.

Stop Conditions:

- Template suggests automatic dispatch.
- Template becomes required for all projects without approval.
- Existing control-index behavior is weakened.

### T-L4-007 - Assisted Execution Model

Status: proposed

Purpose:

- Define future L4 helper capabilities and forbidden behavior before any L4 experiment or helper implementation.

Scope:

- Add a source document describing L4 assisted execution, helper permissions, helper prohibitions, gate model, result-intake support and next-state recommendation rules.
- Reserve `Assisted SOP Run` for future approved L4 helper participation.

Out of Scope:

- Do not implement helper scripts.
- Do not approve L4 experiment.
- Do not change current maturity level.
- Do not add runtime adapters.

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

- Document distinguishes current L3, the L3 transition pattern, future L4 and future L5.
- Helper may recommend, validate and draft only inside approved scope.
- Helper must not execute Codex, dispatch agents, run tests, parse git diffs, merge, push, accept or close review/QA.
- L4 remains future/not approved unless Human Owner separately approves an experiment.

Verification:

- Mode: STANDARD.
- Run `python3 scripts/validate-system.py`.

Dependencies:

- T-L4-005 done.

Risk:

- High if wording blurs assisted execution and controlled runtime.

Stop Conditions:

- Document creates runtime authority.
- Human Owner has not approved L4 model documentation.

### T-L4-008 - SOP Run Specs + Fixtures

Status: proposed

Purpose:

- Add machine-checkable SOP Run contracts and blocking fixture cases after Markdown source documents exist.

Scope:

- Add `spec/sop-run.schema.json`.
- Optionally add `spec/assisted-sop-execution.json`.
- Add fixture cases for valid, missing-field, missing-approval, blocked, out-of-scope, failed-verification, secret-like log content and unapproved state transition scenarios.
- Update validation to parse new specs and fixtures.

Out of Scope:

- Do not generate Markdown from specs.
- Do not allow specs to override Markdown.
- Do not implement runtime behavior.
- Do not implement runner behavior.

Allowed Files:

- `spec/sop-run.schema.json`
- `spec/assisted-sop-execution.json`
- `spec/README.md`
- `examples/sop-run-fixtures/**`
- `scripts/validate-system.py`
- `ai-system/README.md`
- `README.md`
- `README.ru.md`
- `ai-system/system-changelog.md`

Acceptance Criteria:

- Specs parse as JSON.
- Specs declare Markdown source documents.
- Specs preserve forbidden automation boundaries.
- Fixtures cover required blocking cases.
- Validation remains read-only.

Verification:

- Mode: STANDARD.
- Run `python3 scripts/validate-system.py`.
- Run focused JSON parse if validation output is insufficient.

Dependencies:

- T-L4-005 done.
- T-L4-007 done if assisted-execution policy spec is included.

Risk:

- Medium.

Stop Conditions:

- Spec conflicts with Markdown.
- Spec implies execution authority.
- Fixture validation requires runtime behavior.

### T-L4-009 - Runner Command Contract

Status: proposed

Purpose:

- Design `scripts/sop-runner-mvp.py` commands and safety fixtures before any implementation.

Scope:

- Produce a documentation-only command contract for `validate-run`, `next-step`, `generate-prompts`, `intake-result`, `check-boundaries` and `recommend-state`.
- Define inputs, outputs, fixture cases, safety boundaries and validation expectations.
- State that all output is advisory.

Out of Scope:

- Do not implement `scripts/sop-runner-mvp.py`.
- Do not add runtime adapters.
- Do not write SOP Run state.
- Do not parse git diffs.
- Do not run tests.

Allowed Files:

- `ai-system/evolution/l4-assisted-sop-execution-plan.md`
- `ai-system/evolution/l4-assisted-sop-execution-tasks.md`
- `ai-system/evolution/current-evolution-task.md`
- optional future design doc if approved: `ai-system/sop-runner-mvp-plan.md`

Acceptance Criteria:

- Command contract is complete enough for a later implementation task.
- All commands are dry-run/reporting by default.
- Forbidden actions are explicit.
- Fixture strategy covers valid, missing-field, missing-approval, blocked, out-of-scope, failed-verification and sensitive-log cases.
- Contract forbids writes, Codex launch, agent dispatch, test execution, git operations and automatic acceptance.

Verification:

- Mode: FAST.
- Run `python3 scripts/validate-system.py` if source docs changed.

Dependencies:

- T-L4-005 done.
- T-L4-008 done or explicitly deferred with rationale.

Risk:

- Medium.

Stop Conditions:

- Design implies automatic execution or state writes.
- Design requires git diff parsing or test execution for MVP.

### T-L4-010 - Documentation-Only Pilot

Status: proposed

Purpose:

- Validate SOP Run records and manual delegated sequential handling on low-risk documentation work before runner implementation.

Scope:

- Select one small documentation-only system task.
- Record a SOP Run manually.
- Manually execute one bounded prompt at a time.
- Record approval evidence, prompt/result references, result intake, gate validation, blockers/rework/risk decisions, verification evidence and lessons learned.

Out of Scope:

- Do not use automatic execution.
- Do not run product/application code changes.
- Do not implement runner tooling.
- Do not declare L4 experimental.

Allowed Files:

- `AI_PROJECT/SOP_RUNS.md`
- exact documentation files approved by the pilot prompt
- exact README/index/changelog files approved by the pilot prompt

Acceptance Criteria:

- Pilot record shows every approval and stop condition.
- Result intake catches missing or skipped verification.
- Review confirms no runtime behavior was introduced.
- Human Owner decision is recorded.
- Lessons learned are recorded.

Verification:

- Mode: STANDARD.
- Run `python3 scripts/validate-system.py`.

Dependencies:

- T-L4-004 done.
- T-L4-005 done.
- T-L4-006 done.

Risk:

- Medium.

Stop Conditions:

- Pilot scope requires behavior-changing system edits without approval.
- Manual prompt handoff becomes ambiguous.
- SOP Run record copies secrets or unnecessary sensitive data.

### T-L4-011 - Read-Only Runner MVP

Status: proposed

Purpose:

- Add a strictly read-only helper for SOP Run validation, prompt draft generation and next-state recommendation after governance and first manual pilot evidence exist.

Scope:

- Implement read-only commands from the approved command contract.
- Read plans and SOP Run records.
- Validate readiness.
- Generate prompt drafts for manual review only.
- Validate user-provided result reports.
- Compare reported changed files against allowed files.
- Summarize verification evidence.
- Recommend next state for Human Owner review.

Out of Scope:

- Do not write `AI_PROJECT/SOP_RUNS.md`.
- Do not modify project files.
- Do not launch Codex.
- Do not dispatch agents.
- Do not create branches or worktrees.
- Do not run tests automatically.
- Do not create commits, push, merge or open PRs.
- Do not accept results.
- Do not close review or QA.
- Do not make product/security/architecture/runtime decisions.
- Do not parse git diffs.

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
- Helper checks user-provided result reports against allowed files where data exists.
- Helper does not write files.
- Helper does not run tests.
- Helper does not parse git diffs.
- Fixtures cover success and blocking cases.
- `validate-system.py` remains read-only and passes.

Verification:

- Mode: STANDARD.
- Run `python3 -m py_compile scripts/sop-runner-mvp.py scripts/validate-system.py`.
- Run helper fixture validation.
- Run `python3 scripts/validate-system.py`.

Dependencies:

- T-L4-006 done.
- T-L4-008 done.
- T-L4-009 done.
- T-L4-010 completed.

Risk:

- High, because helper tooling can be mistaken for runtime.

Stop Conditions:

- Implementation needs writes or execution to be useful.
- Helper cannot preserve read-only/no-runtime boundary.
- Helper needs git diff parsing or test execution to satisfy MVP criteria.

### T-L4-012 - Small Tooling Pilot

Status: proposed

Purpose:

- Validate SOP Run handling with a small bounded tooling/code change while preserving dry-run and runtime boundaries.

Scope:

- Select one small validation-only script or fixture improvement.
- Record SOP Run plan, prompt, result, verification, review and QA/regression notes.
- Use manual checks or read-only helper output as evidence.

Out of Scope:

- Do not implement L4 helper writes.
- Do not add runtime adapters.
- Do not automate Codex execution.
- Do not broaden runner permissions.

Allowed Files:

- `AI_PROJECT/SOP_RUNS.md`
- exact script/fixture files approved by the pilot prompt
- exact docs/changelog/index files approved by the pilot prompt

Acceptance Criteria:

- SOP Run records changed files and verification evidence.
- Checks prove no automatic execution behavior was added.
- Regression checks are documented.
- Human Owner final decision is recorded.
- Lessons learned are recorded.

Verification:

- Mode: STANDARD.
- Run focused compile/tests for touched scripts under the approved task verification scope.
- Run `python3 scripts/validate-system.py`.

Dependencies:

- T-L4-010 completed.
- T-L4-011 completed or explicitly deferred with rationale.

Risk:

- Medium to high.

Stop Conditions:

- Tooling change requires execution automation.
- Verification fails and no rework is approved.
- The pilot expands runner permissions.

### T-L4-013 - Delegated Sequential Batch Pilot

Status: proposed

Purpose:

- Validate two or three related manual Codex handoffs under one SOP Run.

Scope:

- Prepare a bounded sequential batch with exact steps.
- Manually review and send each prompt.
- Intake each result before preparing the next handoff.
- Run integration review before final Human Owner decision.
- Record approval evidence, prompt/result references, gate validation, blockers/rework/risk decisions, verification evidence and lessons learned.

Out of Scope:

- Do not execute prompts automatically.
- Do not approve parallel execution by implication.
- Do not merge, push or accept automatically.
- Do not turn the batch into an open-ended queue.

Allowed Files:

- `AI_PROJECT/SOP_RUNS.md`
- `ai-system/evolution/l4-assisted-sop-execution-plan.md`
- `ai-system/evolution/l4-assisted-sop-execution-tasks.md`
- `ai-system/evolution/current-evolution-task.md`
- exact step-specific files approved in each prompt

Acceptance Criteria:

- Each step has prompt approval, result report, intake, verification and review route.
- The run records blocked/rework states if they occur.
- Integration Review checks combined result before closure.
- Human Owner decides final status.
- Lessons learned are recorded.

Verification:

- Mode: STANDARD.
- Run checks required by each approved step.
- Run `python3 scripts/validate-system.py` for system-documentation batches.

Dependencies:

- T-L4-010 completed.
- T-L4-012 completed or explicitly deferred with rationale.

Risk:

- High, because batch handling can drift toward runtime behavior.

Stop Conditions:

- Any step wants automatic dispatch.
- Changed files exceed approved step scope.
- Review or QA gate is bypassed.
- Batch becomes open-ended or autonomous.

### T-L4-014 - L4 Readiness Decision

Status: proposed

Purpose:

- Decide whether evidence supports a bounded L4 experiment, continued L3 transition pilots, or deferral.

Scope:

- Review documentation-only, small tooling/code and delegated sequential batch pilot evidence.
- Assess safety boundary violations, verification quality, review/QA effectiveness and Human Owner control.
- Record decision: `APPROVED`, `REWORK`, `REJECTED`, `DEFERRED` or `EXPERIMENT`.

Out of Scope:

- Do not implement L4 experiment in this task.
- Do not implement L5 controlled runtime.
- Do not change current maturity unless Human Owner explicitly approves that separate outcome.
- Do not broaden helper permissions.

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
- Required pilot evidence is listed.
- If decision is `DEFERRED`, next evidence gaps are listed.
- If decision is `EXPERIMENT`, scope, duration, success criteria, failure criteria and rollback/stop rules are defined.
- Automatic acceptance, merge, push, unbounded execution and L5 behavior remain forbidden.
- The task does not implement L4 by itself.

Verification:

- Mode: STANDARD.
- Run `python3 scripts/validate-system.py`.

Dependencies:

- T-L4-010 completed.
- T-L4-012 completed.
- T-L4-013 completed.

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
- Any task adds L3.5 as a separate runtime maturity level.
- Any task enables automatic Codex execution, automatic multi-agent execution, automatic branch/worktree lifecycle, automatic merge, automatic push, automatic PR creation, automatic acceptance or automatic QA/review closure.
- Any task implements L5 controlled runtime.
- Any task expands allowed files without a new approved prompt.
- Any task bypasses review, QA or Human Owner decision gates.
- Any helper task writes SOP Run state, runs tests, parses git diffs or performs git operations without later explicit approval.

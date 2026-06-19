<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/evolution.json -->

# AI Development System Evolution

Revision: `825`
Changes: `29`

## Summary

- `accepted`: 28
- `approved`: 1

## Changes

### CHG-001 — Implement Codex prompt package generator

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `compatible`  
Migration required: `false`  

Problem:

Codex prompt package generation is still tied to task-only behavior and does not provide a dedicated command rail for executable Tasks or Evolution Changes.

Proposal:

Add scripts/codexctl.py to generate, report and clear Codex prompt packages from ready or approved Tasks and Evolution Changes using existing project-control state, generated files and audit conventions.

Rationale:

A dedicated Codex execution rail keeps prompt generation explicit, auditable and bounded by project-control validation.

Approved by: `human_owner` at `2026-06-16T15:13:17Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-16T15:38:14Z`  
Acceptance notes: codexctl prompt package generator accepted  

Affected areas:

- Project Control Gateway command rail
- Codex prompt package generation and execution readiness status

Affected files:

- scripts/codexctl.py
- AI_PROJECT/state/current_execution.json
- AI_PROJECT/generated/CODEX_PROMPT.md
- AI_PROJECT/generated/CODEX_STATUS.md
- AI_PROJECT/events/codex-events.jsonl

Risks:

- Prompt generation could bypass lifecycle boundaries if executable statuses or required fields are mapped too loosely.
- Generated Codex artifacts could drift from source state if status and prompt files are not updated consistently.

Impact:

- Adds a dedicated standard-library CLI for Codex prompt package status, build and clear operations.
- Allows future approved Tasks or Evolution Changes to produce pasteable Codex prompt packages with auditable status.

Linked tasks:

- TASK-004

### CHG-002 — Create Documentation Navigation Skill

Status: `accepted`  
Type: `plugin`  
Priority: `1`  
Backward compatibility: `compatible`  
Migration required: `false`  

Problem:

Agents need a compact routing skill that helps them choose the minimal correct documentation set before planning, editing, reviewing or executing AI_Development_System work.

Proposal:

Add .agents/skills/documentation-navigation/SKILL.md and index it in ai-system/skills/README.md as a guidance-only documentation navigation helper.

Rationale:

The skill reduces over-reading and authority confusion while preserving AGENTS.md, /ai-system documents and CLI-controlled /AI_PROJECT state as source of truth.

Approved by: `human_owner` at `2026-06-16T16:12:38Z`  
Approval notes: Approved in attached CODEX prompt for Documentation Navigation Skill.  

Accepted by: `human_owner` at `2026-06-16T16:17:53Z`  
Acceptance notes: Documentation Navigation Skill accepted after validation under attached owner-approved CODEX prompt.  

Affected areas:

- Skills guidance and documentation navigation

Affected files:

- .agents/skills/documentation-navigation/SKILL.md
- ai-system/skills/README.md

Risks:

- Agents could over-treat the skill as authority unless the skill explicitly defers to AGENTS.md, /ai-system source documents and CLI-controlled project state.
- Navigation guidance could accidentally imply runtime, L4, automatic dispatch or acceptance behavior if boundaries are not explicit.

Impact:

- Adds a local skill that routes Codex and subagents to minimal relevant documentation sets by request type.
- Indexes the skill in the Skills Layer Roadmap with purpose, priority, allowed actions and forbidden actions.

Linked tasks:

- TASK-005

### CHG-003 — Add Two-Level Delegated Agent Execution

Status: `accepted`  
Type: `plugin`  
Priority: `1`  
Backward compatibility: `compatible`  
Migration required: `false`  

Problem:

L3 manual orchestration can coordinate Agent Work Packages, but Controller Codex lacks a dedicated documented skill, source document and worker prompt template for precise manual Worker Agent handoffs.

Proposal:

Add a guidance skill, source-of-truth delegation document and reusable Worker Agent Prompt Package template that preserve L3 manual-only boundaries.

Rationale:

The Human Owner approved a bounded documentation/skill/template task to improve Worker Agent handoff quality without enabling automatic dispatch or runtime behavior.

Approved by: `Human Owner` at `2026-06-16T19:00:36Z`  
Approval notes: Approved in attached CODEX request for bounded documentation/skill/template task.  

Accepted by: `Human Owner` at `2026-06-16T19:18:37Z`  
Acceptance notes: Accepted under attached CODEX request after TASK-006 completed and validation checks passed.  

Affected files:

- .agents/skills/agent-delegation/SKILL.md
- ai-system/agent-delegation.md
- ai-system/templates/agent-worker-prompt.md
- ai-system/skills/README.md
- ai-system/README.md
- ai-system/operating-model.md
- ai-system/evolution/roadmap.md
- ai-system/evolution/evolution-backlog.md
- ai-system/system-changelog.md
- README.md
- README.ru.md

Risks:

- Delegation wording could be misread as approval for automatic agent dispatch, L4 assisted execution or runtime behavior unless every source clearly states the L3 manual-only boundary.

Impact:

- Controller Codex can prepare precise Worker Agent Prompt Packages for manual handoff, and Worker Agent Results have clearer intake expectations; current maturity remains L3 and runtime remains DEFERRED.

Linked tasks:

- TASK-006

### CHG-004 — Record L4 Role-Agent Runtime Architecture

Status: `approved`  
Type: `process`  
Priority: `1`  
Backward compatibility: `compatible`  
Migration required: `false`  

Problem:

AI_Development_System still presents L4 role-agent runtime as future or deferred even though the Human Owner has approved L4 as a bounded implementation target.

Proposal:

Add ai-system/l4-role-agent-runtime.md and update source documentation, roadmap references and changelog so L4 is documented as the next approved bounded implementation target while preserving Python control, Controller Codex delegation boundaries, Human Owner acceptance and L5 prohibitions.

Rationale:

A source-of-truth architecture document is needed before implementation work on agentctl.py or assisted role-agent execution can be safely decomposed into bounded tasks.

Approved by: `Human Owner` at `2026-06-16T20:37:03Z`  
Approval notes: Approved  

Affected areas:

- L4 role-agent runtime architecture
- Operating model and evolution roadmap references
- Role-to-agent execution boundaries

Affected files:

- ai-system/l4-role-agent-runtime.md
- ai-system/README.md
- ai-system/operating-model.md
- ai-system/evolution/roadmap.md
- ai-system/evolution/evolution-backlog.md
- ai-system/system-changelog.md
- README.md
- README.ru.md

Risks:

- L4 wording could be misread as approval for L5 autonomous queues, automatic merge, push, PR creation, QA closure, review closure or final task acceptance unless boundaries are explicit.
- Role-agent documentation could conflict with existing L3 manual orchestration docs if the distinction between current maturity and next approved target is not stated clearly.
- Future implementation could bypass Python project-control validation unless this architecture requires Controller Codex and subagents to stay inside CLI/API gates.

Impact:

- Records the Human Owner direction that L4 Role-Agent Runtime is an approved bounded implementation target, while current implementation maturity remains L3 until later tasks are completed.
- Creates the architecture basis for future bounded tasks such as scripts/agentctl.py, dispatch/intake records and role-scoped Codex worker prompts.
- Updates system documentation so operating model, roadmap and changelog can distinguish L3 current maturity, L4 approved target and L5 not approved.

Linked tasks:

- TASK-007

### CHG-005 — Introduce ai_project_ctl core package foundation

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `compatible`  
Migration required: `false`  

Problem:

Project control logic is duplicated across ctl scripts and CTL-04 needs a shared core package foundation before future aictl implementation.

Proposal:

Create a minimal ai_project_ctl core package foundation for shared paths, result, store, events, IDs, locks, validation and transaction primitives without changing existing ctl behavior.

Rationale:

CTL-01 inventory, CTL-02 architecture, and CTL-03 ID allocation strategy require a controlled implementation path before adding shared control-plane code.

Approved by: `human_owner` at `2026-06-18T13:41:39Z`  
Approval notes: Approved for CTL-04 implementation of ai_project_ctl core package foundation. Existing ctl behavior must remain unchanged.  

Accepted by: `human_owner` at `2026-06-18T13:52:58Z`  
Acceptance notes: CTL-04 implemented and accepted. Core package foundation added without changing existing ctl behavior.  

Affected areas:

- Project Control Gateway
- Shared control-plane core
- Future aictl foundation

Affected files:

- ai_project_ctl/__init__.py
- ai_project_ctl/core/__init__.py
- ai_project_ctl/core/paths.py
- ai_project_ctl/core/result.py
- ai_project_ctl/core/store.py
- ai_project_ctl/core/events.py
- ai_project_ctl/core/ids.py
- ai_project_ctl/core/locks.py
- ai_project_ctl/core/validation.py
- ai_project_ctl/core/transactions.py

Risks:

- Shared core package could accidentally change existing ctl behavior if wrappers are migrated too early.
- Transaction, lock and event primitives must remain foundation-only until later tasks wire them into ctl scripts.

Impact:

- Provides controlled foundation for CTL-04 and later aictl/control-plane tasks.
- Does not change existing CLI behavior in this task.

Linked tasks:

- TASK-022

### CHG-006 — Add command registry foundation

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `compatible`  
Migration required: `false`  

Problem:

The future unified control plane needs a shared command registry so CLI, wrappers, automation, and future Web UI can discover and invoke the same allowed commands without duplicating command catalog behavior.

Proposal:

Add a minimal ai_project_ctl/core/registry.py foundation for command metadata, command descriptors, read/write classification, argument schema placeholders, affected files metadata, and registry lookup without migrating existing ctl scripts yet.

Rationale:

CTL-01 inventory found duplicated parser/command behavior, CTL-02 architecture requires a shared command registry, and CTL-05 is the bounded implementation task for that registry foundation.

Approved by: `human_owner` at `2026-06-18T14:41:29Z`  
Approval notes: Approved for CTL-05 command registry foundation. Existing ctl behavior must remain unchanged; no aictl facade or wrapper migration in this task.  

Accepted by: `human_owner` at `2026-06-18T14:54:59Z`  
Acceptance notes: CTL-05 implemented and accepted. Command registry foundation added as metadata-only without changing existing ctl behavior.  

Affected areas:

- Project Control Gateway
- Command registry
- Future aictl facade
- Future Web Control Center command routing

Affected files:

- ai_project_ctl/core/registry.py
- ai_project_ctl/core/__init__.py if registry exports are added
- tests/test_registry.py or equivalent registry tests

Risks:

- Registry metadata could diverge from existing ctl behavior if legacy commands are migrated before parity tests exist.
- Over-scoping CTL-05 could accidentally start aictl or wrapper migration too early.

Impact:

- Adds shared registry foundation required by CTL-05 and later aictl tasks.
- Does not change existing ctl script behavior in CTL-05.
- Provides a future source for command discovery, command metadata, and Web UI action routing.

Linked tasks:

- TASK-023

### CHG-007 — Add unified aictl CLI facade

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `compatible`  
Migration required: `false`  

Problem:

Project control still requires multiple ctl entrypoints; CTL-06 needs an approved evolution change to introduce scripts/aictl.py as the unified facade.

Proposal:

Add scripts/aictl.py as a facade over the existing command registry and shared core primitives without migrating legacy ctl scripts or changing existing command behavior.

Rationale:

CTL-02 defines aictl as the preferred facade, CTL-04 introduced core primitives, and CTL-05 introduced the command registry foundation.

Approved by: `human_owner` at `2026-06-18T14:56:33Z`  
Approval notes: Approved for CTL-06 scripts/aictl.py facade implementation. Must remain facade-only; no wrapper migration or behavior changes.  

Accepted by: `human_owner` at `2026-06-18T15:19:29Z`  
Acceptance notes: Linked CTL task implemented and accepted.  

Affected areas:

- Project Control Gateway
- Unified CLI facade
- Command registry integration

Affected files:

- scripts/aictl.py
- ai_project_ctl/core/registry.py if facade metadata access requires compatible additions
- tests/test_aictl.py or equivalent facade tests

Risks:

- aictl could accidentally become an independent implementation instead of a facade.
- aictl output could diverge from existing ctl behavior if it attempts to execute mutations too early.

Impact:

- Adds the first unified CLI entrypoint for command discovery and safe facade behavior.
- Existing ctl scripts remain unchanged and compatible.

Linked tasks:

- TASK-024

### CHG-008 — Convert legacy ctl scripts into compatibility wrappers

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `compatible`  
Migration required: `false`  

Problem:

Legacy ctl scripts still contain independent command implementations and duplicated control logic; CTL-07 needs an approved evolution change to migrate them toward compatibility wrappers safely.

Proposal:

Convert legacy ctl scripts into compatibility wrappers only where shared core/domain services make it safe, preserving command syntax, output compatibility, lifecycle gates, protected-file rules, and avoiding circular delegation through aictl.

Rationale:

CTL-01 found duplicated ctl logic, CTL-02 defined wrapper migration, CTL-04 introduced shared core primitives, CTL-05 introduced command registry, and CTL-06 introduced the aictl facade.

Approved by: `human_owner` at `2026-06-18T15:22:20Z`  
Approval notes: Approved for CTL-07 compatibility wrapper migration. Must preserve existing ctl behavior and avoid circular delegation through aictl.  

Accepted by: `human_owner` at `2026-06-18T15:38:01Z`  
Acceptance notes: CTL-07 implemented and accepted. Legacy ctl scripts now share compatibility plumbing without changing command behavior or introducing aictl recursion.  

Affected areas:

- Project Control Gateway
- Legacy ctl compatibility wrappers
- Shared core/domain service migration

Affected files:

- scripts/planctl.py if allowed by CTL-07
- scripts/taskctl.py if allowed by CTL-07
- scripts/docctl.py if allowed by CTL-07
- scripts/contextctl.py if allowed by CTL-07
- scripts/codexctl.py if allowed by CTL-07
- scripts/evolutionctl.py if allowed by CTL-07
- ai_project_ctl/core/* if compatible shared helpers are needed
- tests/test_*ctl*.py or equivalent wrapper compatibility tests

Risks:

- Wrapper migration can create circular delegation if old ctl scripts call aictl while aictl still delegates to old ctl scripts.
- Existing command output, exit codes, lifecycle gates, or protected-file behavior could change unintentionally.
- Migrating all ctl scripts in one task may be too broad if shared domain services are not ready.

Impact:

- Moves legacy ctl scripts toward shared control-plane architecture.
- Keeps existing CLI commands compatible for current workflows.
- Prepares safer future aictl and web control integration.

Linked tasks:

- TASK-025

### CHG-009 — Add project doctor diagnostics

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `compatible`  
Migration required: `false`  

Problem:

The existing aictl project doctor command only delegates to protected-file checks and does not provide explicit PASS/WARN/FAIL project health diagnostics required by CTL-08.

Proposal:

Extend project.doctor with structured project health diagnostics for plan/task/evolution validation, dependency graph, generated-output freshness, protected-file checks, prompt/context status, command registry availability, and current task consistency.

Rationale:

CTL-08 is the bounded implementation task for project doctor diagnostics after aictl facade and wrapper compatibility were introduced.

Approved by: `human_owner` at `2026-06-18T15:43:30Z`  
Approval notes: Approved for CTL-08 project doctor diagnostics. Must preserve lifecycle semantics and distinguish PASS, WARN, and FAIL clearly.  

Accepted by: `human_owner` at `2026-06-18T16:38:55Z`  
Acceptance notes: CTL-08 implemented and accepted. Project doctor now reports explicit PASS/WARN/FAIL diagnostics while preserving lifecycle and validation ownership.  

Affected areas:

- Project Control Gateway
- Project doctor diagnostics
- Validation behavior
- aictl project doctor

Affected files:

- scripts/aictl.py
- ai_project_ctl/** if shared doctor helpers are added
- tests/**
- scripts/check-protected-project-files.py only if CTL-08 explicitly requires it

Risks:

- Doctor diagnostics could incorrectly mark warnings as blocking failures.
- Doctor could duplicate validation logic instead of delegating to existing validated CLIs.
- Prompt/context freshness checks may be noisy if ownership between taskctl.py, codexctl.py, and contextctl.py remains ambiguous.

Impact:

- Adds explicit PASS/WARN/FAIL project health diagnostics.
- Improves owner visibility into stale generated files, prompt/context drift, dependency graph status, and protected-file safety.
- Does not change lifecycle state or approval semantics.

Linked tasks:

- TASK-026

### CHG-010 — Add locking and atomic write protection

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `compatible`  
Migration required: `false`  

Problem:

Project-control write operations can still race or partially update state/events/generated outputs without a shared lock and transaction safety model.

Proposal:

Add locking and atomic write protection for shared control-plane write paths, defining safe local lock behavior, stale write protection, and transaction boundaries without changing lifecycle semantics.

Rationale:

CTL-02 architecture and CTL-03 ID allocation strategy require lock-protected mutation before future web writes or broader parallel execution are safe.

Approved by: `human_owner` at `2026-06-18T16:39:46Z`  
Approval notes: Approved for CTL-09 locking and atomic write protection. Must preserve existing lifecycle semantics and avoid broad wrapper behavior changes.  

Accepted by: `human_owner` at `2026-06-18T17:12:06Z`  
Acceptance notes: CTL-09 implemented and accepted. Locking and atomic write protection added without changing lifecycle semantics.  

Affected areas:

- Project Control Gateway
- Locking and atomic writes
- Shared transaction safety

Affected files:

- ai_project_ctl/core/locks.py
- ai_project_ctl/core/store.py
- ai_project_ctl/core/transactions.py
- ai_project_ctl/core/legacy.py if legacy ctl plumbing adopts lock helpers
- tests/**

Risks:

- Locking could deadlock or leave stale lock files if not implemented conservatively.
- Changing existing ctl write paths too broadly could alter behavior or exit codes.
- Transaction ordering between event append, state write, and generated render must be explicit.

Impact:

- Improves safety for parallel local execution and future web write actions.
- Prepares the control plane for lock-aware command execution without changing lifecycle semantics.

Linked tasks:

- TASK-027

### CHG-011 — Add read-only local Web Control Center MVP

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `compatible`  
Migration required: `false`  

Problem:

Project control is now available through ctl scripts and aictl, but there is no local read-only UI for observing current task state, executable queue, health diagnostics, events, and generated project-control status.

Proposal:

Add a read-only local Web Control Center MVP over existing aictl/core/registry/project doctor capabilities. The web UI must not mutate JSON, events, generated files, lifecycle state, or approval status.

Rationale:

CTL-02 architecture defines a future local web shell, CTL-06 introduced aictl, CTL-08 added project doctor diagnostics, and CTL-09 added locking/atomic-write safety. CTL-10 is the bounded read-only UI step before any web write actions.

Approved by: `human_owner` at `2026-06-18T17:30:06Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-18T17:43:17Z`  
Acceptance notes: CTL-10 implemented and accepted. Read-only local Web Control Center MVP added without web write actions or direct protected-file mutation.  

Affected areas:

- Project Control Gateway
- Read-only local Web Control Center
- aictl web/dashboard surface

Affected files:

- scripts/aictl.py if web command routing is added
- ai_project_ctl/web/**
- ai_project_ctl/core/** only if read-only web integration requires compatible helpers
- tests/**

Risks:

- Web UI could accidentally introduce mutation paths if route handlers bypass the command registry.
- Adding web dependencies could make the project harder to run if dependency policy is unclear.
- Dashboard may display stale generated state unless it clearly labels derived outputs and doctor warnings.

Impact:

- Adds local read-only visibility for project-control state.
- Keeps all state changes disabled in CTL-10.
- Prepares CTL-11 web write actions without implementing them.

Linked tasks:

- TASK-028

### CHG-012 — Add controlled Web write actions

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `compatible`  
Migration required: `false`  

Problem:

The local Web Control Center is currently read-only; CTL-11 needs approved governance to add controlled write actions without bypassing command registry, lifecycle validation, locks, audit events, or protected-file rules.

Proposal:

Add a narrow set of confirmed Web write actions routed only through the registered command layer. Web route handlers must not directly edit AI_PROJECT/state, AI_PROJECT/events, or AI_PROJECT/generated files.

Rationale:

CTL-10 established a read-only local Web Control Center. CTL-11 is the bounded next step to add controlled writes using the existing registry, doctor, locking, and protected-file safety model.

Approved by: `human_owner` at `2026-06-18T17:44:20Z`  
Approval notes: Approved for CTL-11 controlled Web write actions. Writes must route through registered commands only; no direct JSON/event/generated edits; no approval/acceptance automation unless explicitly allowed by CTL-11.  

Accepted by: `human_owner` at `2026-06-18T18:01:06Z`  
Acceptance notes: CTL-11 implemented and accepted. Controlled Web write actions added through confirmed POST /actions and registered command routing without direct protected-file mutation.  

Affected areas:

- Project Control Gateway
- Web Control Center write actions
- Command registry routed mutations
- Lifecycle and audit safety

Affected files:

- ai_project_ctl/web/**
- scripts/aictl.py if web command routing changes are needed
- ai_project_ctl/core/registry.py if write-action metadata changes are needed
- ai_project_ctl/core/transactions.py if web action execution uses shared transaction helpers
- tests/**

Risks:

- Web write routes could bypass registered command validation and mutate protected files directly.
- Unsafe web actions could accidentally approve, accept, or close work without Human Owner intent.
- Write actions could weaken loopback-only/read-only safety if method restrictions are not updated carefully.
- Write actions could introduce stale prompt/context artifacts after task state changes.

Impact:

- Adds controlled local web mutations through the approved command layer.
- Preserves audit events, lifecycle validation, locks, and generated-output regeneration.
- Prepares owner-facing project control without direct JSON editing.

Linked tasks:

- TASK-029

### CHG-013 — Optimize Web Control Center performance

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `compatible`  
Migration required: `false`  

Problem:

Web Control Center dashboard and data endpoints are slow because they run full project doctor and heavy CLI checks on normal page/data requests.

Proposal:

Add caching and explicit doctor refresh behavior so normal dashboard/data views are fast while full diagnostics remain available and accurate.

Rationale:

Measured timings show /healthz is fast, while project doctor takes about 3.8s, /data.json about 4.9s, and dashboard about 5.8s. The bottleneck is backend read-model/doctor execution, not networking.

Approved by: `human_owner` at `2026-06-18T18:58:59Z`  
Approval notes: Approved for CTL-13 Web Control Center performance optimization. Must preserve doctor correctness and Web write safety.  

Accepted by: `human_owner` at `2026-06-18T19:20:34Z`  
Acceptance notes: CTL-13 implemented and accepted. Web Control Center dashboard/data performance optimized without weakening doctor diagnostics or write safety.  

Affected areas:

- Web Control Center
- Read model performance
- Project doctor caching
- Controlled Web write cache invalidation

Affected files:

- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py if cache invalidation is needed
- scripts/aictl.py if web/doctor flags require compatible updates
- tests/**

Risks:

- Caching could hide fresh FAIL diagnostics if refresh behavior is unclear.
- Cache invalidation after POST /actions could be incomplete.
- Optimization could accidentally weaken project doctor or protected-file checks.

Impact:

- Makes Dashboard and /data.json usable interactively.
- Keeps heavy project doctor diagnostics available through explicit refresh or cached result.
- Preserves loopback-only and controlled Web write safety.

Linked tasks:

- TASK-031

### CHG-014 — Add task workflow automation MVP

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `compatible`  
Migration required: `false`  

Problem:

Preparing tasks for Codex and submitting tasks for review still requires many manual CLI commands, even though the command registry, aictl facade, context generation, Codex prompt generation, doctor diagnostics, and Web actions already exist.

Proposal:

Add a minimal workflow automation layer that composes existing registered commands for prepare-for-codex, refresh-execution-context, and submit-for-review without bypassing validation, audit, generated-output rules, protected-file policy, or owner gates.

Rationale:

WFA-01 is the bounded first step for reducing manual task execution overhead while preserving the governed command layer introduced by the control plane.

Approved by: `human_owner` at `2026-06-18T19:48:14Z`  
Approval notes: Approved for WFA-01 task workflow automation MVP. Workflows must compose registered/validated commands only and must not directly edit protected project-control files.  

Accepted by: `human_owner` at `2026-06-18T20:07:43Z`  
Acceptance notes: WFA-01 implemented and accepted. Task workflow automation MVP added while preserving validation, generated-output ownership, protected-file rules, and owner gates.  

Affected areas:

- Project Control Gateway
- Workflow automation
- aictl workflow commands
- Web Control Center workflow actions

Affected files:

- ai_project_ctl/core/workflows.py
- ai_project_ctl/web/actions.py if workflow actions are exposed in UI
- ai_project_ctl/web/server.py if workflow routes/buttons are exposed in UI
- ai_project_ctl/web/read_model.py if UI read model needs workflow metadata
- ai_project_ctl/core/registry.py if workflow command metadata is needed
- scripts/aictl.py
- tests/**

Risks:

- Workflow automation could accidentally bypass individual command validation if it writes protected files directly.
- Prepare-for-Codex could hide failures if it continues after a failed step.
- Submit-review could incorrectly move a task to in_review when blocking checks fail.
- Web workflow buttons could weaken confirmation or write-safety guarantees.

Impact:

- Reduces manual command overhead for preparing tasks for Codex and submitting work for review.
- Keeps workflows as compositions of existing registered commands.
- Preserves validation, audit events, generated-output ownership, and protected-file boundaries.

Linked tasks:

- TASK-032

### CHG-015 — Add Evolution Change Wizard

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `compatible`  
Migration required: `false`  

Problem:

Creating Evolution Change records still requires many manual evolutionctl.py commands for affected areas, files, risks, impacts, task linking, and lifecycle preparation.

Proposal:

Add a guided workflow/UI helper that creates and prepares an Evolution Change for a selected task, using task fields to draft problem/proposal/rationale and link the legacy task id, while keeping approval as an explicit Human Owner action.

Rationale:

WFA-02 is the bounded next step after WFA-01 workflow automation, reducing governance overhead without removing owner approval gates.

Approved by: `human_owner` at `2026-06-18T20:09:47Z`  
Approval notes: Approved for WFA-02 Evolution Change Wizard. Wizard may create and prepare Change records, but must not approve or accept them automatically.  

Accepted by: `human_owner` at `2026-06-18T20:34:31Z`  
Acceptance notes: WFA-02 implemented and accepted. Evolution Change Wizard added without bypassing Human Owner approval.  

Affected areas:

- Workflow automation
- Evolution Change Flow
- Web Control Center
- aictl workflow commands

Affected files:

- ai_project_ctl/core/workflows.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/core/registry.py
- scripts/aictl.py
- tests/**

Risks:

- Wizard could over-generate low-quality Change fields if task data is vague.
- Wizard could accidentally approve or accept changes if owner gates are not preserved.
- Wizard must link by legacy task id where evolutionctl.py requires TASK-XXX references.

Impact:

- Reduces manual overhead for controlled self-evolution.
- Keeps approval as explicit Human Owner action.
- Improves consistency of affected files, risks, impact, and linked task records.

Linked tasks:

- TASK-033

### CHG-016 — WFA-03 Add Task Creation Wizard

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `compatible`  
Migration required: `false`  

Problem:

Task WFA-03 requires an explicit Evolution Change Proposal before implementation: Add owner-facing CLI/UI workflow for creating individual tasks without long taskctl.py command lines.

Proposal:

Implement the bounded task scope: Add task creation workflow metadata.; Add UI form or CLI wizard-like command if allowed.; Support Epic selection.; Support scope/out-of-scope/allowed-files/acceptance/review fields.; Support depends_on selection.; Support create-only mode.; Optionally offer next action suggestions: prepare for Codex, create Evolution Change.; Add tests.

Rationale:

Provide a guided task creation form/workflow that routes through taskctl.py/aictl command layer and supports scope, out-of-scope, allowed files, acceptance criteria, review instructions, dependencies, and optional Evolution Change hint.

Approved by: `human_owner` at `2026-06-19T06:23:46Z`  
Approval notes: Approved for WFA-03 Task Creation Wizard. Must create tasks only through governed command paths, preserve validation/protected-file boundaries, and not implement grouped import or auto-start behavior.  

Accepted by: `human_owner` at `2026-06-19T07:09:16Z`  
Acceptance notes: WFA-03 implemented and accepted. Task Creation Wizard added as create-only governed workflow without auto-starting tasks or bypassing protected-file boundaries.  

Affected areas:

- Workflow automation
- Task creation wizard
- Web Control Center
- aictl workflow commands

Affected files:

- ai_project_ctl/core/workflows.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/core/registry.py
- scripts/aictl.py
- tests/**

Risks:

- Boundary risk: Do not implement grouped import in this task.
- Boundary risk: Do not auto-start the created task.
- Boundary risk: Do not auto-create Evolution Change unless explicitly delegated to WFA-02 workflow.
- Boundary risk: Do not bypass taskctl validation.
- Verify taskctl/aictl routing, create-only behavior, dependency support, protected-file policy, tests, and validation output.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-034.
- Keeps Change approval as a separate explicit Human Owner action.
- Add task creation workflow metadata.
- Add UI form or CLI wizard-like command if allowed.
- Support Epic selection.
- Support scope/out-of-scope/allowed-files/acceptance/review fields.
- Support depends_on selection.
- Owner can create a single task through workflow/UI without manually writing a long CLI command.
- Created task is persisted through approved command path.
- Generated task views are refreshed through owning CLI/facade.

Linked tasks:

- TASK-034

### CHG-017 — WFA-04 Add Bulk Task Import UI

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `compatible`  
Migration required: `false`  

Problem:

Task WFA-04 requires an explicit Evolution Change Proposal before implementation: Add a grouped task import interface for importing multiple planned tasks from structured text with preview, validation, and confirmation.

Proposal:

Implement the bounded task scope: Define a simple import format, preferably YAML-like or JSON-like text.; Support multiple tasks in one batch.; Support epic, title, summary, description, scope, out_of_scope, allowed_files, acceptance_criteria, review_instructions, notes, dependencies.; Support dry-run/preview.; Validate references before creating anything.; Show generated command plan before confirmation.; Create tasks only after explicit confirmation.; Add UI import page/form if allowed.; Add tests for valid import, invalid import, dependency references, dry-run, and no direct state writes.

Rationale:

Allow Human Owner to paste or upload a batch of tasks in a simple structured format and preview the generated task records before creation. The importer must route all writes through approved command paths and must not edit tasks.json directly.

Approved by: `human_owner` at `2026-06-19T07:12:06Z`  
Approval notes: Approved for WFA-04 Bulk Task Import UI. Must provide preview/dry-run, validate before writes, create tasks only through governed command paths, and never execute imported content.  

Accepted by: `human_owner` at `2026-06-19T07:45:00Z`  
Acceptance notes: WFA-04 implemented and accepted. Bulk Task Import UI added with preview, validation, confirmation, and governed command-path creation.  

Affected areas:

- Workflow automation
- Bulk task import
- Web Control Center
- aictl workflow commands

Affected files:

- ai_project_ctl/web/actions.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/core/workflows.py
- ai_project_ctl/core/registry.py
- scripts/aictl.py
- tests/**

Risks:

- Boundary risk: Do not import arbitrary Python or shell commands.
- Boundary risk: Do not execute uploaded files.
- Boundary risk: Do not auto-start imported tasks.
- Boundary risk: Do not auto-approve anything.
- Boundary risk: Do not bypass taskctl validation.
- Boundary risk: Do not support unrestricted file editing from import payload.
- Verify parser safety, dry-run behavior, all-or-nothing validation, command-path task creation, protected-file policy, tests, and validation output.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-035.
- Keeps Change approval as a separate explicit Human Owner action.
- Define a simple import format, preferably YAML-like or JSON-like text.
- Support multiple tasks in one batch.
- Support epic, title, summary, description, scope, out_of_scope, allowed_files, acceptance_criteria, review_instructions, notes, dependencies.
- Support dry-run/preview.
- Validate references before creating anything.
- Owner can paste a batch of task definitions and preview them.
- Import preview shows tasks, fields, dependencies, and planned commands.
- Invalid imports fail before any task is created.

Linked tasks:

- TASK-035

### CHG-018 — WFA-05 Add Review And Close Helpers

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task WFA-05 requires an explicit Evolution Change Proposal before implementation: Add guarded workflow helpers for closing reviewed tasks, accepting linked Evolution Changes, and optionally closing completed Epics.

Proposal:

Implement the bounded task scope: Add close_task workflow for tasks in in_review.; Require approval notes and explicit confirmation.; Approve task then transition to done through taskctl/aictl path.; Add accept_change workflow only for approved/in_review changes whose linked tasks are done.; Add optional close_epic helper only if all child tasks are done/deferred/archived.; Add tests for confirmation, invalid states, and blocked closure.

Rationale:

Reduce manual closure steps while preserving explicit Human Owner confirmation and approval gates.

Approved by: `human_owner` at `2026-06-19T07:45:45Z`  
Approval notes: Approved for WFA-05 Review and Close Helpers. Must preserve Human Owner confirmation, lifecycle gates, linked Change completion rules, and reject invalid closure.  

Accepted by: `human_owner` at `2026-06-19T08:10:06Z`  
Acceptance notes: WFA-05 implemented and accepted. Review/close helpers added while preserving Human Owner confirmation and lifecycle gates.  

Affected files:

- ai_project_ctl/core/workflows.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/core/registry.py
- scripts/aictl.py
- tests/**

Risks:

- Boundary risk: Do not auto-approve without Human Owner confirmation.
- Boundary risk: Do not close tasks with failing checks unless explicitly allowed by policy.
- Boundary risk: Do not accept Changes with incomplete linked tasks.
- Boundary risk: Do not close Epics with active tasks.
- Boundary risk: Do not bypass lifecycle gates.
- Verify lifecycle gate preservation, owner confirmation, invalid-state handling, protected-file policy, tests, and validation output.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-036.
- Keeps Change approval as a separate explicit Human Owner action.
- Add close_task workflow for tasks in in_review.
- Require approval notes and explicit confirmation.
- Approve task then transition to done through taskctl/aictl path.
- Add accept_change workflow only for approved/in_review changes whose linked tasks are done.
- Add optional close_epic helper only if all child tasks are done/deferred/archived.
- Owner can close an in_review task with explicit notes and confirmation.
- Owner can accept an Evolution Change only when linked task completion rules pass.
- Invalid close/accept attempts are rejected with clear messages.

Linked tasks:

- TASK-036

### CHG-019 — UIX-01 Improve Tasks filtering grouping and collapse

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task WFA-07 requires an explicit Evolution Change Proposal before implementation: Make the Tasks page usable for large projects by adding initiative/epic/status filters, search, grouping, and collapsible done sections.

Proposal:

Implement the bounded task scope: Add filtering by Initiative.; Add filtering by Epic.; Add filtering by Status.; Add search by task ref, legacy id, title, and summary.; Add grouping by Epic and Status.; Add collapsible groups.; Hide done tasks by default or collapse done groups by default.; Show readable task refs such as WFA-04 alongside legacy TASK-XXX ids.; Preserve read-only/dashboard performance improvements.

Rationale:

Improve the Web Control Center Tasks page so the owner can focus on one initiative, one epic, or active tasks only instead of scrolling through the full task history.

Approved by: `human_owner` at `2026-06-19T09:04:42Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-19T09:20:22Z`  
Acceptance notes: WFA-07 implemented and accepted. Tasks UI filtering, grouping, collapse behavior, and readable task identity display were added while preserving governed write boundaries.  

Affected files:

- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py if filter state needs action metadata
- tests/test_web_control_center.py
- tests/test_aictl.py if aictl web routing is touched

Risks:

- Boundary risk: Do not add new write actions in this task.
- Boundary risk: Do not change task lifecycle rules.
- Boundary risk: Do not change task identity/ref allocation.
- Boundary risk: Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.
- Verify that filtering and grouping work with EPIC-005/CTL and EPIC-006/WFA.
- Verify that done tasks no longer dominate the default task view.
- Verify that Web write safety is unchanged.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-038.
- Keeps Change approval as a separate explicit Human Owner action.
- Add filtering by Initiative.
- Add filtering by Epic.
- Add filtering by Status.
- Add search by task ref, legacy id, title, and summary.
- Add grouping by Epic and Status.
- Tasks page can be filtered by initiative, epic, status, and search text.
- Tasks page can group tasks by epic or status.
- Done tasks are hidden or collapsed by default.

Linked tasks:

- TASK-038

### CHG-020 — UIX-02 Add task row workflow buttons

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task WFA-08 requires an explicit Evolution Change Proposal before implementation: Add status-aware workflow buttons next to tasks, including Prepare for Codex, Refresh Context, and Submit for Review.

Proposal:

Implement the bounded task scope: Add status-aware task row buttons.; Expose Prepare for Codex for planned/ready tasks.; Expose Refresh Context for current/in-progress tasks.; Expose Submit for Review for in-progress tasks.; Show confirmation preview before workflow execution.; Route all actions through existing workflow runner and aictl command paths.; Show result summary after execution.; Show next Codex instruction after Prepare for Codex.

Rationale:

Make routine task operation possible from the Tasks page by exposing existing workflow automation actions as row-level buttons.

Approved by: `human_owner` at `2026-06-19T09:22:31Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-19T09:41:49Z`  
Acceptance notes: WFA-08 implemented and accepted. Task row workflow buttons added while preserving confirmation gates and governed command-path execution.  

Affected files:

- ai_project_ctl/web/actions.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/core/workflows.py if workflow metadata needs compatible updates
- ai_project_ctl/core/registry.py if workflow metadata needs compatible updates
- scripts/aictl.py if workflow routing needs compatible updates
- tests/test_web_control_center.py
- tests/test_workflows.py
- tests/test_aictl.py
- tests/test_registry.py

Risks:

- Boundary risk: Do not auto-run Codex.
- Boundary risk: Do not auto-approve tasks.
- Boundary risk: Do not auto-close tasks.
- Boundary risk: Do not accept Evolution Changes.
- Boundary risk: Do not add arbitrary shell command execution.
- Boundary risk: Do not directly edit protected project-control files.
- Verify that buttons are not shown for invalid task states.
- Verify that every write workflow requires confirmation.
- Verify that Prepare for Codex produces the instruction to send Codex.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-039.
- Keeps Change approval as a separate explicit Human Owner action.
- Add status-aware task row buttons.
- Expose Prepare for Codex for planned/ready tasks.
- Expose Refresh Context for current/in-progress tasks.
- Expose Submit for Review for in-progress tasks.
- Show confirmation preview before workflow execution.
- Tasks page shows useful workflow buttons based on task status.
- Prepare for Codex can be launched from a task row with explicit confirmation.
- Refresh Context can be launched from a task row with explicit confirmation.

Linked tasks:

- TASK-039

### CHG-021 — UIX-03 Add unified workflow action result panel

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task WFA-09 requires an explicit Evolution Change Proposal before implementation: Add a reusable result panel for workflow and Web actions showing step status, changed files, warnings, errors, and next actions.

Proposal:

Implement the bounded task scope: Add a reusable action result view/component.; Show workflow name and target task/change/epic.; Show step-by-step PASS/WARN/FAIL status.; Show changed files when available.; Show generated files when available.; Show warnings and errors clearly.; Show next-action hints such as the Codex prompt instruction.; Support copyable text for the Codex instruction.

Rationale:

Improve owner feedback after UI actions by showing what was executed, what changed, what failed, and what to do next.

Approved by: `human_owner` at `2026-06-19T09:43:37Z`  
Approval notes: Approved for WFA-09 Unified Workflow Action Result Panel. Must make action results human-readable, collapse raw technical details by default, preserve errors/warnings, and not change workflow semantics.  

Accepted by: `human_owner` at `2026-06-19T10:01:38Z`  
Acceptance notes: WFA-09 implemented and accepted. Unified Web action result panel added while preserving workflow semantics, visible failures, and protected-file boundaries.  

Affected files:

- ai_project_ctl/web/server.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/workflows.py if result metadata needs compatible updates
- tests/test_web_control_center.py
- tests/test_workflows.py

Risks:

- Boundary risk: Do not change workflow semantics.
- Boundary risk: Do not add new workflow actions in this task.
- Boundary risk: Do not auto-run Codex.
- Boundary risk: Do not weaken confirmation requirements.
- Boundary risk: Do not directly edit protected project-control files.
- Verify that failed steps are visible and not hidden behind a generic success message.
- Verify that result panel does not expose arbitrary command execution.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-040.
- Keeps Change approval as a separate explicit Human Owner action.
- Add a reusable action result view/component.
- Show workflow name and target task/change/epic.
- Show step-by-step PASS/WARN/FAIL status.
- Show changed files when available.
- Show generated files when available.
- After a workflow action, UI shows a clear action result panel.
- Result panel shows executed steps and status.
- Result panel shows warnings/errors without hiding failures.

Linked tasks:

- TASK-040

### CHG-022 — UIX-07 Add Task Review Done Controls

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task WFA-13 requires an explicit Evolution Change Proposal before implementation: Add UI controls for closing reviewed tasks and requesting changes from the Tasks page while preserving Human Owner review gates.

Proposal:

Implement the bounded task scope: Add status-aware review controls for tasks in in_review.; Add Approve & Done action routed through the existing task.close_reviewed workflow.; Add Request Changes action routed through an existing governed task transition path or a minimal governed workflow wrapper if needed.; Require explicit confirmation before any review decision.; Require owner notes for Approve & Done and Request Changes.; Show clear success/failure result through the unified action result panel.; After Approve & Done, show next actions such as accepting the linked Evolution Change or preparing the next task.; Do not show Done controls for tasks that are not in_review.; Add tests for valid close, invalid status, missing notes, request changes, and no direct state writes.

Rationale:

Expose the task review completion part of the pipeline in the Web Control Center. The owner should be able to approve a task and move it to done, or request changes, directly from the UI when the task is in_review.

Approved by: `human_owner` at `2026-06-19T10:02:24Z`  
Approval notes: Approved for WFA-13 Task Review Done Controls. Must expose Approve & Done and Request Changes through governed workflows, require explicit confirmation and owner notes, and not auto-accept linked Changes.  

Accepted by: `human_owner` at `2026-06-19T10:26:52Z`  
Acceptance notes: Accepted after task WFA-13 review  

Affected files:

- ai_project_ctl/web/actions.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/core/workflows.py if a minimal review workflow wrapper is needed
- ai_project_ctl/core/registry.py if workflow/action metadata needs compatible updates
- scripts/aictl.py if command routing needs compatible updates
- tests/test_web_control_center.py
- tests/test_workflows.py
- tests/test_aictl.py
- tests/test_registry.py

Risks:

- Boundary risk: Do not auto-approve tasks.
- Boundary risk: Do not auto-close tasks without explicit Human Owner confirmation.
- Boundary risk: Do not accept linked Evolution Changes automatically.
- Boundary risk: Do not bypass task lifecycle validation.
- Boundary risk: Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.
- Boundary risk: Do not change task lifecycle semantics except adding a governed UI wrapper if strictly required.
- Verify that Done cannot be applied to planned, ready, in_progress, or already done tasks.
- Verify that owner notes are required.
- Verify that all writes route through governed workflows/commands.
- Verify that linked Change acceptance remains a separate explicit action.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-044.
- Keeps Change approval as a separate explicit Human Owner action.
- Add status-aware review controls for tasks in in_review.
- Add Approve & Done action routed through the existing task.close_reviewed workflow.
- Add Request Changes action routed through an existing governed task transition path or a minimal governed workflow wrapper if needed.
- Require explicit confirmation before any review decision.
- Require owner notes for Approve & Done and Request Changes.
- Tasks in in_review show Approve & Done and Request Changes controls.
- Approve & Done requires explicit confirmation and owner notes.
- Approve & Done routes through task.close_reviewed or another governed workflow path.

Linked tasks:

- TASK-044

### CHG-023 — UIX-04 Add Evolution management UI tab

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task WFA-10 requires an explicit Evolution Change Proposal before implementation: Add an Evolution tab to view and manage Change Proposals, including create-for-task, approve, move to review, and accept actions with confirmation.

Proposal:

Implement the bounded task scope: Add an Evolution tab/page.; List Change Proposals with status, type, title, linked tasks, affected files, risks, and approval/acceptance state.; Add filters by status and type.; Add action to create Change for selected task using existing evolution.create_for_task workflow.; Add action to approve a ready Change with explicit confirmation.; Add action to move approved Change to in_progress/in_review where valid.; Add action to accept a Change only when linked-task rules pass.; Show clear errors for invalid transitions.; Route all mutations through existing governed commands/workflows.

Rationale:

Make Evolution Change Flow manageable from the Web Control Center while preserving Human Owner approval gates and linked-task completion checks.

Approved by: `human_owner` at `2026-06-19T10:29:32Z`  
Approval notes: Approved for WFA-10 Evolution Management UI Tab. Must expose create/approve/accept Change actions through governed workflows, require explicit confirmation, and preserve Human Owner approval gates.  

Accepted by: `human_owner` at `2026-06-19T10:51:20Z`  
Acceptance notes: Accepted after WFA-10 review. Evolution management UI implemented and verified.  

Affected files:

- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/workflows.py if evolution workflow metadata needs compatible updates
- ai_project_ctl/core/registry.py if evolution command metadata needs compatible updates
- scripts/aictl.py if evolution action routing needs compatible updates
- tests/test_web_control_center.py
- tests/test_workflows.py
- tests/test_aictl.py
- tests/test_registry.py

Risks:

- Boundary risk: Do not auto-approve Change Proposals.
- Boundary risk: Do not auto-accept Change Proposals.
- Boundary risk: Do not bypass linked-task completion checks.
- Boundary risk: Do not change evolution lifecycle rules.
- Boundary risk: Do not directly edit AI_PROJECT/state/evolution.json or evolution events.
- Verify that approval and acceptance remain explicit Human Owner actions.
- Verify that accepted Changes cannot link incomplete tasks.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-041.
- Keeps Change approval as a separate explicit Human Owner action.
- Add an Evolution tab/page.
- List Change Proposals with status, type, title, linked tasks, affected files, risks, and approval/acceptance state.
- Add filters by status and type.
- Add action to create Change for selected task using existing evolution.create_for_task workflow.
- Add action to approve a ready Change with explicit confirmation.
- Evolution tab lists Change Proposals with useful metadata.
- Evolution tab can filter by status and type.
- Owner can create a Change for a task through the existing wizard.

Linked tasks:

- TASK-041

### CHG-024 — UIX-08 Add Next Action and Blocked Reason Hints

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task WFA-14 requires an explicit Evolution Change Proposal before implementation: Show actionable next steps and blocked reasons for tasks, changes, and epics in the Web Control Center.

Proposal:

Implement the bounded task scope: Add next-action hints for task rows and task focus sections.; Show why Prepare for Codex is unavailable, such as unmet dependencies, missing approved Change, invalid status, or another current task.; Show why Submit for Review is unavailable, such as task not in_progress or stale context/Codex state.; Show why Approve & Done is unavailable, such as task not in_review.; Show linked Evolution Change status when available.; Show suggested actions such as Create Change, Approve Change, Prepare for Codex, Refresh Context, Submit for Review, Approve & Done, Accept Change, or Close Epic.; Add blocked reason hints for Evolution actions where useful.; Add blocked reason hints for epic close where useful.; Keep hints read-only; actual writes must remain separate confirmed actions.; Add tests for dependency-blocked tasks, missing Change, invalid status actions, and next action suggestions.

Rationale:

Improve the UI pipeline by explaining what the owner can do next and why an action is unavailable. The Tasks page should not silently hide important actions without showing dependency, lifecycle, current-task, or Evolution Change reasons.

Approved by: `human_owner` at `2026-06-19T11:00:27Z`  
Approval notes: Approved for WFA-14 Next Action and Blocked Reason Hints. Must explain unavailable actions, stale context, missing Change, dependency blockers, and preserve confirmation gates.  

Accepted by: `human_owner` at `2026-06-19T13:04:37Z`  
Acceptance notes: Approve Change  

Affected files:

- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py if action metadata needs compatible updates
- ai_project_ctl/core/workflows.py if workflow metadata needs compatible updates
- ai_project_ctl/core/registry.py if command metadata needs compatible updates
- tests/test_web_control_center.py
- tests/test_workflows.py
- tests/test_registry.py

Risks:

- Boundary risk: Do not auto-run any suggested action.
- Boundary risk: Do not auto-create or auto-approve Evolution Changes.
- Boundary risk: Do not auto-close tasks or epics.
- Boundary risk: Do not weaken lifecycle gates.
- Boundary risk: Do not introduce arbitrary command execution.
- Boundary risk: Do not directly edit protected project-control files.
- Verify that WFA tasks with dependencies show useful blocked reasons.
- Verify that missing or unapproved Evolution Changes are explained clearly.
- Verify that hints do not bypass confirmation gates.
- Verify that suggested actions match the actual valid workflow path.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-045.
- Keeps Change approval as a separate explicit Human Owner action.
- Add next-action hints for task rows and task focus sections.
- Show why Prepare for Codex is unavailable, such as unmet dependencies, missing approved Change, invalid status, or another current task.
- Show why Submit for Review is unavailable, such as task not in_progress or stale context/Codex state.
- Show why Approve & Done is unavailable, such as task not in_review.
- Show linked Evolution Change status when available.
- Tasks page shows next-action hints for common pipeline states.
- Unavailable actions show a clear reason instead of disappearing silently.
- Tasks blocked by dependencies show which dependencies are not done.

Linked tasks:

- TASK-045

### CHG-025 — UIX-09 Add Codex Execution Report Submission

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task WFA-15 requires an explicit Evolution Change Proposal before implementation: Add a governed way for Codex to submit structured task execution reports through aictl instead of relying on manual pasted summaries.

Proposal:

Implement the bounded task scope: Define a JSON schema for Codex execution reports.; Support fields for task id/ref, implementation summary, changed files, generated files, checks, warnings, blockers, notes, and owner decision required.; Add a governed command such as aictl task report submit --task <TASK> --file <REPORT> --confirm.; Validate task reference and report shape before storing anything.; Store report data through project-control state/events, not by directly editing tasks.json.; Link the latest report to the task for UI review.; Generate or expose a latest review summary for read models.; Update Codex prompt guidance so Codex knows to submit a structured report when the command exists.; Add tests for valid report, invalid task, invalid schema, missing file, and no direct state writes.

Rationale:

Introduce a machine-readable Codex execution report flow. At the end of task execution, Codex should be able to write a structured JSON report and submit it through a governed CLI command. The report must be validated, stored through project-control state/events, and made available to the Web Control Center for task review.

Approved by: `human_owner` at `2026-06-19T12:47:54Z`  
Approval notes: Approved for this task. Must preserve governed workflows, protected-file boundaries, and Human Owner gates.  

Accepted by: `human_owner` at `2026-06-19T13:13:13Z`  
Acceptance notes: Accept Change  

Affected files:

- ai_project_ctl/core/workflows.py
- ai_project_ctl/core/registry.py
- ai_project_ctl/web/read_model.py
- scripts/aictl.py
- scripts/taskctl.py if a task-domain report command is needed
- AI_PROJECT/state/task_reports.json via governed CLI only
- AI_PROJECT/events/task-report-events.jsonl via governed CLI only
- AI_PROJECT/generated/** via owning render/check commands only
- tests/test_workflows.py
- tests/test_aictl.py
- tests/test_registry.py
- tests/test_web_control_center.py

Risks:

- Boundary risk: Do not allow Codex to edit tasks.json directly.
- Boundary risk: Do not accept arbitrary executable report content.
- Boundary risk: Do not auto-approve or auto-close tasks based on report content.
- Boundary risk: Do not treat a submitted report as Human Owner acceptance.
- Boundary risk: Do not bypass protected-file validation.
- Boundary risk: Do not require external services or databases.
- Verify that reports are submitted through CLI only.
- Verify that tasks.json is not directly edited for full report storage.
- Verify that report submission does not replace Human Owner review.
- Verify that invalid reports create no persistent state.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-046.
- Keeps Change approval as a separate explicit Human Owner action.
- Define a JSON schema for Codex execution reports.
- Support fields for task id/ref, implementation summary, changed files, generated files, checks, warnings, blockers, notes, and owner decision required.
- Add a governed command such as aictl task report submit --task <TASK> --file <REPORT> --confirm.
- Validate task reference and report shape before storing anything.
- Store report data through project-control state/events, not by directly editing tasks.json.
- Codex execution report JSON schema is documented or encoded in validation.
- Report submission command validates task identity and report shape.
- Valid reports are stored through governed state/events only.

Linked tasks:

- TASK-046

### CHG-026 — UIX-10 Add Task Review Package View

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task WFA-16 requires an explicit Evolution Change Proposal before implementation: Add a task review view that combines task metadata, linked Change, Codex report, changed files, checks, and owner decision controls.

Proposal:

Implement the bounded task scope: Add a Task Review view or drawer in the Web Control Center.; Show task ref, legacy id, title, status, summary, scope, and acceptance criteria.; Show linked Evolution Change status when available.; Show latest Codex execution report when available.; Show changed source files and generated/project-control files from the report.; Show checks and their pass/fail/warn status.; Show warnings, blockers, and notes from the report.; Expose Approve & Done and Request Changes controls when valid.; Use the unified action result panel for review decisions.; Add tests for review view with report, without report, with linked Change, and invalid states.

Rationale:

Create a review-oriented UI view for tasks in review. The owner should be able to see what Codex changed, what checks passed, what blockers remain, and then make a review decision from one place.

Approved by: `human_owner` at `2026-06-19T13:16:29Z`  
Approval notes: Approved for WFA-16 Task Review Package View. Must expose review information readably in the UI, preserve Human Owner review gates, and route all write actions through governed workflows.  

Accepted by: `human_owner` at `2026-06-19T13:32:04Z`  
Acceptance notes: Accepted after WFA-16 review. Task Review Package View implemented and accepted; linked task is done and required checks passed.  

Affected files:

- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/workflows.py if review action metadata needs compatible updates
- tests/test_web_control_center.py
- tests/test_workflows.py

Risks:

- Boundary risk: Do not auto-approve tasks.
- Boundary risk: Do not auto-accept Evolution Changes.
- Boundary risk: Do not replace Human Owner review.
- Boundary risk: Do not execute tests from the review view in this task.
- Boundary risk: Do not edit source or generated files from the review view.
- Verify that the owner can understand what is being accepted before pressing Done.
- Verify that missing Codex report is shown clearly and does not crash the view.
- Verify that review controls still require confirmation and notes.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-047.
- Keeps Change approval as a separate explicit Human Owner action.
- Add a Task Review view or drawer in the Web Control Center.
- Show task ref, legacy id, title, status, summary, scope, and acceptance criteria.
- Show linked Evolution Change status when available.
- Show latest Codex execution report when available.
- Show changed source files and generated/project-control files from the report.
- Task Review view shows task metadata and acceptance context.
- Task Review view shows latest Codex execution report when available.
- Task Review view shows linked Evolution Change status when available.

Linked tasks:

- TASK-047

### CHG-027 — UIX-10 Add Task Review Package View

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task WFA-16 requires an explicit Evolution Change Proposal before implementation: Add a task review view that combines task metadata, linked Change, Codex report, changed files, checks, and owner decision controls.

Proposal:

Implement the bounded task scope: Add a Task Review view or drawer in the Web Control Center.; Show task ref, legacy id, title, status, summary, scope, and acceptance criteria.; Show linked Evolution Change status when available.; Show latest Codex execution report when available.; Show changed source files and generated/project-control files from the report.; Show checks and their pass/fail/warn status.; Show warnings, blockers, and notes from the report.; Expose Approve & Done and Request Changes controls when valid.; Use the unified action result panel for review decisions.; Add tests for review view with report, without report, with linked Change, and invalid states.

Rationale:

Create a review-oriented UI view for tasks in review. The owner should be able to see what Codex changed, what checks passed, what blockers remain, and then make a review decision from one place.

Approved by: `human_owner` at `2026-06-19T13:16:38Z`  
Approval notes: Approved for WFA-16 Task Review Package View. Must expose review information readably in the UI, preserve Human Owner review gates, and route all write actions through governed workflows.  

Accepted by: `human_owner` at `2026-06-19T13:32:15Z`  
Acceptance notes: Accepted after WFA-16 review. Task Review Package View implemented and accepted; linked task is done and required checks passed.  

Affected files:

- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/workflows.py if review action metadata needs compatible updates
- tests/test_web_control_center.py
- tests/test_workflows.py

Risks:

- Boundary risk: Do not auto-approve tasks.
- Boundary risk: Do not auto-accept Evolution Changes.
- Boundary risk: Do not replace Human Owner review.
- Boundary risk: Do not execute tests from the review view in this task.
- Boundary risk: Do not edit source or generated files from the review view.
- Verify that the owner can understand what is being accepted before pressing Done.
- Verify that missing Codex report is shown clearly and does not crash the view.
- Verify that review controls still require confirmation and notes.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-047.
- Keeps Change approval as a separate explicit Human Owner action.
- Add a Task Review view or drawer in the Web Control Center.
- Show task ref, legacy id, title, status, summary, scope, and acceptance criteria.
- Show linked Evolution Change status when available.
- Show latest Codex execution report when available.
- Show changed source files and generated/project-control files from the report.
- Task Review view shows task metadata and acceptance context.
- Task Review view shows latest Codex execution report when available.
- Task Review view shows linked Evolution Change status when available.

Linked tasks:

- TASK-047

### CHG-028 — UIX-10 Add Task Review Package View

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task WFA-16 requires an explicit Evolution Change Proposal before implementation: Add a task review view that combines task metadata, linked Change, Codex report, changed files, checks, and owner decision controls.

Proposal:

Implement the bounded task scope: Add a Task Review view or drawer in the Web Control Center.; Show task ref, legacy id, title, status, summary, scope, and acceptance criteria.; Show linked Evolution Change status when available.; Show latest Codex execution report when available.; Show changed source files and generated/project-control files from the report.; Show checks and their pass/fail/warn status.; Show warnings, blockers, and notes from the report.; Expose Approve & Done and Request Changes controls when valid.; Use the unified action result panel for review decisions.; Add tests for review view with report, without report, with linked Change, and invalid states.

Rationale:

Create a review-oriented UI view for tasks in review. The owner should be able to see what Codex changed, what checks passed, what blockers remain, and then make a review decision from one place.

Approved by: `human_owner` at `2026-06-19T13:34:03Z`  
Approval notes: Accept  

Accepted by: `human_owner` at `2026-06-19T13:34:18Z`  
Acceptance notes: Accept  

Affected files:

- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/workflows.py if review action metadata needs compatible updates
- tests/test_web_control_center.py
- tests/test_workflows.py

Risks:

- Boundary risk: Do not auto-approve tasks.
- Boundary risk: Do not auto-accept Evolution Changes.
- Boundary risk: Do not replace Human Owner review.
- Boundary risk: Do not execute tests from the review view in this task.
- Boundary risk: Do not edit source or generated files from the review view.
- Verify that the owner can understand what is being accepted before pressing Done.
- Verify that missing Codex report is shown clearly and does not crash the view.
- Verify that review controls still require confirmation and notes.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-047.
- Keeps Change approval as a separate explicit Human Owner action.
- Add a Task Review view or drawer in the Web Control Center.
- Show task ref, legacy id, title, status, summary, scope, and acceptance criteria.
- Show linked Evolution Change status when available.
- Show latest Codex execution report when available.
- Show changed source files and generated/project-control files from the report.
- Task Review view shows task metadata and acceptance context.
- Task Review view shows latest Codex execution report when available.
- Task Review view shows linked Evolution Change status when available.

Linked tasks:

- TASK-047

### CHG-029 — UIX-11 Add Current Execution Status Panel

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task WFA-17 requires an explicit Evolution Change Proposal before implementation: Add a UI panel showing current task, Context Pack status, Codex prompt status, and safe execution-context actions.

Proposal:

Implement the bounded task scope: Show current task ref/id/title/status in the dashboard and task pages.; Show Context Pack status: ready, stale, missing, or unknown.; Show Codex prompt/status: ready, stale, missing, or blocked.; Show generated prompt path and context pack path.; Add Copy Codex Instruction action when prompt is ready.; Expose safe Refresh Context and Refresh Prompt actions through existing governed workflows.; Expose Clear Current action only with explicit confirmation.; Show warnings when current task differs from selected task.; Add tests for ready, stale, missing, and no-current-task states.

Rationale:

Make the current execution state visible in the Web Control Center so the owner knows which task is prepared for Codex and whether the context/prompt artifacts are ready or stale.

Approved by: `human_owner` at `2026-06-19T13:35:14Z`  
Approval notes: Approved for WFA-17 Current Execution Status Panel. Must expose current task, Context Pack/Codex prompt readiness, stale states, and safe refresh/clear actions through governed workflows while preserving protected-file boundaries and Human Owner gates.  

Accepted by: `human_owner` at `2026-06-19T13:56:08Z`  
Acceptance notes: Accepted after WFA-17 review. Current Execution Status Panel implemented and accepted; linked task is done and required checks passed.  

Affected files:

- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/workflows.py if execution-context workflow metadata needs compatible updates
- ai_project_ctl/core/registry.py if action metadata needs compatible updates
- tests/test_web_control_center.py
- tests/test_workflows.py
- tests/test_registry.py

Risks:

- Boundary risk: Do not auto-run Codex.
- Boundary risk: Do not auto-switch current task without confirmation.
- Boundary risk: Do not directly edit current_execution.json.
- Boundary risk: Do not directly edit generated context or Codex files.
- Boundary risk: Do not weaken protected-file checks.
- Verify that stale context/prompt states are visible.
- Verify that the current task cannot be changed silently.
- Verify that Copy Codex Instruction matches the generated prompt path.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-048.
- Keeps Change approval as a separate explicit Human Owner action.
- Show current task ref/id/title/status in the dashboard and task pages.
- Show Context Pack status: ready, stale, missing, or unknown.
- Show Codex prompt/status: ready, stale, missing, or blocked.
- Show generated prompt path and context pack path.
- Add Copy Codex Instruction action when prompt is ready.
- UI clearly shows the current task when one is selected.
- UI clearly shows when no current task exists.
- UI shows Context Pack and Codex prompt readiness/staleness.

Linked tasks:

- TASK-048

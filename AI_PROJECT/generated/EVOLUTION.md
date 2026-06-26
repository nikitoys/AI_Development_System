<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/evolution.json -->

# AI Development System Evolution

Revision: `2304`
Changes: `74`

## Summary

- `accepted`: 52
- `approved`: 16
- `in_review`: 1
- `ready`: 5

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

Status: `accepted`  
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

Accepted by: `human_owner` at `2026-06-20T08:38:10Z`  
Acceptance notes: Approve  

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

### CHG-030 — UIX-12 Add Project Health Repair Actions

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task WFA-18 requires an explicit Evolution Change Proposal before implementation: Add UI health and repair actions for doctor, stale generated artifacts, docs render, context/Codex refresh, and protected-file checks.

Proposal:

Implement the bounded task scope: Show project doctor summary in the Web Control Center.; Show stale context, Codex, docs, task generated, and evolution generated states where detectable.; Add Run Doctor action.; Add Refresh Context/Codex action for current or selected task where valid.; Add Render Docs action through docctl where valid.; Add Check Protected Files action.; Show before/after action result through the unified result panel.; Reject repair actions when no safe target task exists.; Add tests for doctor pass/warn/fail display and safe repair action routing.

Rationale:

Turn common project-control warnings into visible UI health signals with safe repair buttons that route through owning CLIs. The owner should be able to diagnose and fix stale generated artifacts without remembering individual commands.

Approved by: `human_owner` at `2026-06-19T13:58:24Z`  
Approval notes: Approved for WFA-18 Project Health Repair Actions. Must expose doctor/generated/protected health signals and safe repair actions through governed workflows/commands, require confirmation for repairs, and preserve protected-file boundaries.  

Accepted by: `human_owner` at `2026-06-19T14:29:56Z`  
Acceptance notes: Accept Change  

Affected files:

- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/workflows.py if repair workflow metadata needs compatible updates
- ai_project_ctl/core/registry.py if command metadata needs compatible updates
- scripts/aictl.py if routing needs compatible updates
- tests/test_web_control_center.py
- tests/test_workflows.py
- tests/test_aictl.py
- tests/test_registry.py

Risks:

- Boundary risk: Do not auto-repair without owner confirmation.
- Boundary risk: Do not manually edit generated files.
- Boundary risk: Do not suppress doctor failures.
- Boundary risk: Do not bypass owning CLIs.
- Boundary risk: Do not add network or external service dependencies.
- Verify that repair actions do not run silently.
- Verify that stale context/Codex and docs cases are shown clearly.
- Verify that doctor FAIL is not converted into OK by UI formatting.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-049.
- Keeps Change approval as a separate explicit Human Owner action.
- Show project doctor summary in the Web Control Center.
- Show stale context, Codex, docs, task generated, and evolution generated states where detectable.
- Add Run Doctor action.
- Add Refresh Context/Codex action for current or selected task where valid.
- Add Render Docs action through docctl where valid.
- UI shows project doctor health summary.
- UI shows stale generated artifact warnings in a readable way.
- Run Doctor action works through governed command routing.

Linked tasks:

- TASK-049

### CHG-031 — UIX-05 Add Bulk Task Import from file

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task WFA-11 requires an explicit Evolution Change Proposal before implementation: Extend Bulk Task Import to support uploading JSON files in addition to pasted JSON text.

Proposal:

Implement the bounded task scope: Add file upload support for Bulk Task Import.; Support UTF-8 .json or .txt files containing JSON import payloads.; Enforce conservative file size limit.; Parse file content as data only.; Reuse existing preview/dry-run behavior.; Reuse existing validation before writes.; Reuse existing confirmed command-path task creation.; Show clear parse/validation errors.; Keep paste-based import working.

Rationale:

Allow the owner to import task batches from a local JSON file while preserving preview, validation, confirmation, and governed command-path creation.

Approved by: `human_owner` at `2026-06-19T14:31:08Z`  
Approval notes: Approve  

Accepted by: `human_owner` at `2026-06-19T14:48:32Z`  
Acceptance notes: Extend Bulk Task Import to support uploading JSON files in addition to pasted JSON text.  

Affected files:

- ai_project_ctl/web/actions.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/core/workflows.py if import payload handling needs compatible updates
- scripts/aictl.py if import routing needs compatible updates
- tests/test_web_control_center.py
- tests/test_workflows.py
- tests/test_aictl.py

Risks:

- Boundary risk: Do not execute uploaded files.
- Boundary risk: Do not support Python, shell scripts, or unrestricted executable formats.
- Boundary risk: Do not add YAML dependency unless already allowed by existing project dependency policy.
- Boundary risk: Do not auto-start imported tasks.
- Boundary risk: Do not auto-approve anything.
- Boundary risk: Do not write tasks.json directly.
- Verify that uploaded file content is parsed as data only.
- Verify that no executable content is run.
- Verify that invalid imports create no tasks.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-042.
- Keeps Change approval as a separate explicit Human Owner action.
- Add file upload support for Bulk Task Import.
- Support UTF-8 .json or .txt files containing JSON import payloads.
- Enforce conservative file size limit.
- Parse file content as data only.
- Reuse existing preview/dry-run behavior.
- Owner can import a task batch by uploading a JSON/text file.
- Paste-based JSON import still works.
- Importer shows preview before creation.

Linked tasks:

- TASK-042

### CHG-032 — UIX-06 Update UI workflow documentation

Status: `accepted`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task WFA-12 requires an explicit Evolution Change Proposal before implementation: Update owner-facing documentation for the improved UI cockpit, task filters, workflow buttons, Evolution tab, and bulk file import.

Proposal:

Implement the bounded task scope: Update owner quickstart with UI-first daily workflow.; Document Tasks filtering/grouping/collapse.; Document task row workflow buttons.; Document action result panel.; Document Evolution management tab.; Document Bulk Task Import from paste and file.; Clarify that legacy ctl scripts remain compatibility tools.; Clarify that UI writes route through governed workflows/commands.; Run docctl validation/render/check-generated if documentation registry is used.

Rationale:

Document the new owner workflow after UI cockpit improvements so daily operation is clear and old manual command-heavy instructions are de-emphasized.

Approved by: `human_owner` at `2026-06-19T14:51:12Z`  
Approval notes: Approve Change  

Accepted by: `human_owner` at `2026-06-19T15:39:48Z`  
Acceptance notes: Update owner-facing documentation for the improved UI cockpit, task filters, workflow buttons, Evolution tab, and bulk file import.  

Affected files:

- README.md
- AGENTS.md
- ai-system/project-control/08-usage-guide.md
- ai-system/project-control/10-owner-quickstart.md
- ai-system/project-control/** if documentation index or appendix updates are needed
- AI_PROJECT/state/docs.json via docctl.py only
- AI_PROJECT/events/doc-events.jsonl via docctl.py only
- AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only
- AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only

Risks:

- Boundary risk: Do not change command behavior.
- Boundary risk: Do not add new UI actions.
- Boundary risk: Do not edit generated docs manually.
- Boundary risk: Do not mark docs accepted without Human Owner approval.
- Verify that documentation matches the implemented UI behavior.
- Verify that outdated command-heavy workflow is not presented as the preferred path.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-043.
- Keeps Change approval as a separate explicit Human Owner action.
- Update owner quickstart with UI-first daily workflow.
- Document Tasks filtering/grouping/collapse.
- Document task row workflow buttons.
- Document action result panel.
- Document Evolution management tab.
- Documentation describes the UI-first daily workflow.
- Documentation explains task filters, workflow buttons, Evolution tab, and bulk file import.
- Documentation preserves protected-file and generated-output rules.

Linked tasks:

- TASK-043

### CHG-033 — UIX-13 Add Epic Close UI Action

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task WFA-19 requires an explicit Evolution Change Proposal before implementation: Expose the epic.close_if_complete workflow in the Web Control Center with clear incomplete-task blocking reasons.

Proposal:

Implement the bounded task scope: Add Close Epic If Complete action to Epic or Dashboard views.; Route close action through existing epic.close_if_complete workflow.; Require explicit confirmation before closing an epic.; Show incomplete tasks when close is blocked.; Show linked open Changes if they prevent closure or should be reviewed.; Show task completion counts by status.; Use unified result panel for success/failure output.; Add tests for closable epic, incomplete epic, invalid epic, and no direct state writes.

Rationale:

Allow the owner to close an epic from the UI when all required child tasks are complete, while showing clear reasons when the epic cannot be closed.

Approved by: `human_owner` at `2026-06-19T14:51:19Z`  
Approval notes: Approve Change  

Accepted by: `human_owner` at `2026-06-19T15:07:51Z`  
Acceptance notes: Expose the epic.close_if_complete workflow in the Web Control Center with clear incomplete-task blocking reasons.  

Affected files:

- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/workflows.py if epic workflow metadata needs compatible updates
- ai_project_ctl/core/registry.py if command metadata needs compatible updates
- tests/test_web_control_center.py
- tests/test_workflows.py
- tests/test_registry.py

Risks:

- Boundary risk: Do not auto-close epics.
- Boundary risk: Do not close epics with incomplete tasks.
- Boundary risk: Do not auto-accept linked Changes.
- Boundary risk: Do not change epic lifecycle rules.
- Boundary risk: Do not directly edit plan.json or task state.
- Verify that incomplete epics cannot be closed.
- Verify that blocking tasks are shown clearly.
- Verify that closing an epic does not auto-close tasks or Changes.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-050.
- Keeps Change approval as a separate explicit Human Owner action.
- Add Close Epic If Complete action to Epic or Dashboard views.
- Route close action through existing epic.close_if_complete workflow.
- Require explicit confirmation before closing an epic.
- Show incomplete tasks when close is blocked.
- Show linked open Changes if they prevent closure or should be reviewed.
- UI shows epic completion status and open task counts.
- Close Epic If Complete is available only when valid or explains why it is blocked.
- Close action requires explicit confirmation.

Linked tasks:

- TASK-050

### CHG-034 — UIX-14 Add Commit Readiness View

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task WFA-20 requires an explicit Evolution Change Proposal before implementation: Add a read-only UI view for worktree readiness, changed files, validation status, and suggested commit message.

Proposal:

Implement the bounded task scope: Add Commit Readiness view to the Web Control Center.; Show git status or changed files where safely available.; Show project-control validation status.; Show protected-file check status.; Show stale generated artifact warnings if present.; Show linked completed tasks and accepted Changes since last check where available.; Suggest a commit message based on completed tasks/Changes.; Do not perform git commit, git push, or destructive git commands.; Add tests for read-only rendering and safe command boundaries.

Rationale:

After tasks and Changes are closed, the owner needs a final view that answers whether the worktree is ready to commit. This task adds a read-only commit readiness view without performing git commits automatically.

Approved by: `human_owner` at `2026-06-19T14:51:27Z`  
Approval notes: Approve Change  

Accepted by: `human_owner` at `2026-06-19T15:27:07Z`  
Acceptance notes: Add a read-only UI view for worktree readiness, changed files, validation status, and suggested commit message.  

Affected files:

- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py if read-only command routing is needed
- ai_project_ctl/core/registry.py if read-only command metadata is needed
- scripts/aictl.py if read-only routing is needed
- tests/test_web_control_center.py
- tests/test_aictl.py
- tests/test_registry.py

Risks:

- Boundary risk: Do not run git commit.
- Boundary risk: Do not run git push.
- Boundary risk: Do not stage files automatically.
- Boundary risk: Do not discard or reset changes.
- Boundary risk: Do not hide uncommitted generated/protected-file warnings.
- Boundary risk: Do not require network access.
- Verify that no git write commands are executed.
- Verify that warnings remain visible.
- Verify that suggested commit message is clearly only a suggestion.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-051.
- Keeps Change approval as a separate explicit Human Owner action.
- Add Commit Readiness view to the Web Control Center.
- Show git status or changed files where safely available.
- Show project-control validation status.
- Show protected-file check status.
- Show stale generated artifact warnings if present.
- UI shows a read-only commit readiness view.
- View shows changed files or a safe unavailable message.
- View shows validation/protected-file/generated artifact readiness.

Linked tasks:

- TASK-051

### CHG-035 — PIPE-01 Automation Policy Model

Status: `accepted`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-01 requires an explicit Evolution Change Proposal before implementation: Define the supervised batch pipeline automation policy model and safe presets.

Proposal:

Implement the bounded task scope: Create a policy model for supervised batch pipeline execution.; Define policy fields for queue selection, linked Evolution Change creation/approval/acceptance, token budget thresholds, Codex execution mode, review behavior, rework loop, auto-close behavior, and local commit behavior.; Add safe presets such as dry_run, supervised, supervised_autoclose, and supervised_local_commit if appropriate.; Require explicit policy values for any action that can mutate lifecycle state, launch Codex, close tasks, accept Changes, or create commits.; Reject unsafe combinations such as auto-close without Machine Review PASS and Codex Review APPROVE, commit without commit readiness, push/merge, or execution without Token Budget Gate PASS.; Expose policy validation through a governed command or registry metadata if needed.; Add tests for valid presets, invalid combinations, defaults, and serialization.

Rationale:

Create the policy contract that controls what the Pipeline may do automatically: queue selection, Evolution Change handling, token budget, Codex execution, review, rework, closure, and local commit behavior.

Approved by: `human_owner` at `2026-06-19T20:35:37Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-19T21:02:28Z`  
Acceptance notes: Accept Change  

Affected files:

- ai_project_ctl/pipeline/policy.py
- ai_project_ctl/pipeline/__init__.py
- ai_project_ctl/core/registry.py if command metadata is needed
- scripts/aictl.py if policy command routing is needed
- tests/**
- ai-system/project-control/** if policy documentation is needed

Risks:

- Boundary risk: Do not run tasks.
- Boundary risk: Do not launch Codex.
- Boundary risk: Do not close tasks, accept Changes, or commit.
- Boundary risk: Do not implement queue execution loop.
- Boundary risk: Do not bypass Human Owner policy selection.
- Verify that policy cannot authorize push, merge, unsafe auto-close, lifecycle bypass, or execution without token gate.
- Verify that policy values are explicit enough for audit.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-052.
- Keeps Change approval as a separate explicit Human Owner action.
- Create a policy model for supervised batch pipeline execution.
- Define policy fields for queue selection, linked Evolution Change creation/approval/acceptance, token budget thresholds, Codex execution mode, review behavior, rework loop, auto-close behavior, and local commit behavior.
- Add safe presets such as dry_run, supervised, supervised_autoclose, and supervised_local_commit if appropriate.
- Require explicit policy values for any action that can mutate lifecycle state, launch Codex, close tasks, accept Changes, or create commits.
- Reject unsafe combinations such as auto-close without Machine Review PASS and Codex Review APPROVE, commit without commit readiness, push/merge, or execution without Token Budget Gate PASS.
- Policy schema covers all approved pipeline automation decisions.
- Policy validation rejects unsafe combinations with stable error codes.
- Default policy is safe and does not auto-run Codex, auto-close tasks, accept Changes, or commit.

Linked tasks:

- TASK-052

### CHG-036 — PIPE-02 Pipeline Queue Planner

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-02 requires an explicit Evolution Change Proposal before implementation: Select the next executable task from an owner-selected queue under policy constraints.

Proposal:

Implement the bounded task scope: Create a queue planner for selected task refs, epic filters, status filters, priority/order rules, and max task limits.; Reuse existing task executable queue semantics where possible.; Respect task dependencies, parent Epic/Initiative state, current-task conflicts, terminal statuses, and policy queue constraints.; Return deterministic queue preview with executable, waiting, skipped, and blocked reasons.; Select exactly one next executable task for run-next.; Do not mutate task state during planning.; Add tests for empty queue, executable queue, dependency-blocked tasks, invalid refs, and deterministic ordering.

Rationale:

Implement a deterministic queue planner that reads existing task execution state, owner queue filters, and policy constraints, then returns the next executable task without mutating lifecycle state.

Approved by: `human_owner` at `2026-06-19T20:38:27Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-19T21:01:41Z`  
Acceptance notes: Select the next executable task from an owner-selected queue under policy constraints.  

Affected files:

- ai_project_ctl/pipeline/queue.py
- ai_project_ctl/pipeline/policy.py if compatibility changes are needed
- ai_project_ctl/core/registry.py if command metadata is needed
- scripts/aictl.py if queue preview command routing is needed
- tests/**

Risks:

- Boundary risk: Do not run tasks.
- Boundary risk: Do not create Evolution Changes.
- Boundary risk: Do not modify task lifecycle state.
- Boundary risk: Do not implement batch loop yet.
- Boundary risk: Do not invent new task dependency semantics.
- Verify that queue planning is read-only.
- Verify that existing task executable semantics are preserved.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-053.
- Keeps Change approval as a separate explicit Human Owner action.
- Create a queue planner for selected task refs, epic filters, status filters, priority/order rules, and max task limits.
- Reuse existing task executable queue semantics where possible.
- Respect task dependencies, parent Epic/Initiative state, current-task conflicts, terminal statuses, and policy queue constraints.
- Return deterministic queue preview with executable, waiting, skipped, and blocked reasons.
- Select exactly one next executable task for run-next.
- Queue planner can preview owner-selected queues.
- Queue planner selects the same next task deterministically for the same state and policy.
- Tasks blocked by dependencies or parent state are not selected as executable.

Linked tasks:

- TASK-053

### CHG-037 — PIPE-03 Pipeline Session State

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-03 requires an explicit Evolution Change Proposal before implementation: Persist supervised pipeline sessions, selected queue, policy snapshot, step status, stop reason, and audit references.

Proposal:

Implement the bounded task scope: Define pipeline session state schema with session id, status, selected queue, policy snapshot, current task, current step, attempt counters, gate outcomes, linked Change ids, report ids, review ids, commit ids if any, and stop reason.; Add governed state read/write paths for pipeline_sessions.json.; Append pipeline audit events for session creation, step start, step result, stop, and completion.; Generate a read-only Pipeline Status output if useful.; Support session statuses such as planned, running, stopped, blocked, failed, completed, and archived if appropriate.; Add validation for dangling task/change/report references.; Add tests for session creation, update, validation, and generated output freshness.

Rationale:

Add governed pipeline session state so batch runs are restartable, auditable, and stoppable without relying on transient UI memory or manual notes.

Approved by: `human_owner` at `2026-06-19T20:39:14Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-19T21:20:17Z`  
Acceptance notes: Persist supervised pipeline sessions, selected queue, policy snapshot, step status, stop reason, and audit references.  

Affected files:

- ai_project_ctl/pipeline/session.py
- ai_project_ctl/pipeline/state.py
- ai_project_ctl/core/registry.py if command metadata is needed
- scripts/aictl.py if session command routing is needed
- AI_PROJECT/state/pipeline_sessions.json via governed CLI/service only
- AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only
- tests/**

Risks:

- Boundary risk: Do not run Codex.
- Boundary risk: Do not implement run-next step logic yet.
- Boundary risk: Do not store secrets or raw prompts larger than necessary.
- Boundary risk: Do not treat generated Pipeline Status as source of truth.
- Verify state/events/generated separation.
- Verify no raw secret or unnecessary prompt payload is stored in session state.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-054.
- Keeps Change approval as a separate explicit Human Owner action.
- Define pipeline session state schema with session id, status, selected queue, policy snapshot, current task, current step, attempt counters, gate outcomes, linked Change ids, report ids, review ids, commit ids if any, and stop reason.
- Add governed state read/write paths for pipeline_sessions.json.
- Append pipeline audit events for session creation, step start, step result, stop, and completion.
- Generate a read-only Pipeline Status output if useful.
- Support session statuses such as planned, running, stopped, blocked, failed, completed, and archived if appropriate.
- Pipeline session state is validated before and after mutation.
- Session state records queue, policy snapshot, current task, gate outcomes, and stop reason.
- Pipeline events are appended for session lifecycle mutations.

Linked tasks:

- TASK-054

### CHG-038 — PIPE-04 Run Next Step Action

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-04 requires an explicit Evolution Change Proposal before implementation: Implement a supervised run-next pipeline action that advances exactly one safe step and stops on blockers.

Proposal:

Implement the bounded task scope: Add a run-next action for one pipeline session.; Resolve selected policy and queue.; Choose the next executable task through the queue planner.; Create a linked Evolution Change when required and policy allows.; Approve a linked Change only when policy explicitly allows and lifecycle gates pass.; Prepare task execution by setting current task, moving it to in_progress when valid, building Context Pack, and building Codex prompt.; Call Token Budget Gate before any Codex execution.; Call Codex Execution Adapter only when Token Budget Gate PASS.; Call report, machine review, Codex review, auto-close/rework, Change acceptance, and commit actions only when those components exist and policy allows.; Stop with a clear NOT_IMPLEMENTED, BLOCKED, POLICY_VIOLATION, UNSAFE_CONDITION, or TOKEN_BUDGET_FAILURE result when a required component is unavailable or fails.; Update pipeline session state and audit events for every decision.

Rationale:

Add the one-step pipeline executor. It should compose queue planning, policy checks, lifecycle preparation, gate calls, execution adapter calls, review gates, close/rework/accept/commit decisions, and session updates without running a full loop.

Approved by: `human_owner` at `2026-06-19T20:40:01Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-19T21:39:41Z`  
Acceptance notes: Implement a supervised run-next pipeline action that advances exactly one safe step and stops on blockers.  

Affected files:

- ai_project_ctl/pipeline/runner.py
- ai_project_ctl/pipeline/**
- ai_project_ctl/core/registry.py if command metadata is needed
- ai_project_ctl/core/workflows.py if workflow routing is needed
- ai_project_ctl/web/actions.py if UI action routing is needed
- scripts/aictl.py
- tests/**
- AI_PROJECT/state/pipeline_sessions.json via governed CLI/service only
- AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only

Risks:

- Boundary risk: Do not implement run-until-blocker loop.
- Boundary risk: Do not push or merge.
- Boundary risk: Do not bypass any existing task/evolution lifecycle validation.
- Boundary risk: Do not close tasks unless policy and review gates allow.
- Boundary risk: Do not silently continue after blockers.
- Verify that run-next is a guarded orchestrator, not an unsafe autonomous loop.
- Verify stop-on-first-blocker behavior.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-055.
- Keeps Change approval as a separate explicit Human Owner action.
- Add a run-next action for one pipeline session.
- Resolve selected policy and queue.
- Choose the next executable task through the queue planner.
- Create a linked Evolution Change when required and policy allows.
- Approve a linked Change only when policy explicitly allows and lifecycle gates pass.
- Run-next advances at most one pipeline step.
- Run-next records policy decision, selected task, gate result, and stop reason.
- Run-next stops when a required component is not implemented instead of bypassing it.

Linked tasks:

- TASK-055

### CHG-039 — PIPE-05 Batch Runner Run Until Blocker

Status: `accepted`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-05 requires an explicit Evolution Change Proposal before implementation: Run repeated pipeline run-next steps until first blocker, policy violation, unsafe condition, token failure, or queue completion.

Proposal:

Implement the bounded task scope: Add run-until-blocker action for an existing or newly created pipeline session.; Loop over run-next with max steps, max tasks, max failures, and max rework attempts from policy.; Stop on first blocker, policy violation, unsafe condition, token budget failure, report failure, review failure, commit readiness failure, or queue completion.; Persist each step result to session state and pipeline audit events.; Return a final summary with completed tasks, changed tasks, requested changes, accepted Changes, commits if any, blockers, and next owner action.; Expose CLI command and optional UI action with explicit confirmation.; Add tests for queue completion, blocker stop, policy stop, max-step stop, and session resume behavior if supported.

Rationale:

Add the supervised batch runner loop over run-next. It must honor policy limits, max steps, max tasks, rework limits, and stop-on-blocker semantics.

Approved by: `human_owner` at `2026-06-19T20:40:27Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-20T07:34:26Z`  
Acceptance notes: Accept Change  

Affected files:

- ai_project_ctl/pipeline/batch.py
- ai_project_ctl/pipeline/**
- ai_project_ctl/core/registry.py if command metadata is needed
- ai_project_ctl/web/actions.py if UI action routing is needed
- ai_project_ctl/web/server.py if UI controls are added
- scripts/aictl.py
- tests/**
- AI_PROJECT/state/pipeline_sessions.json via governed CLI/service only
- AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only

Risks:

- Boundary risk: Do not run as a background daemon.
- Boundary risk: Do not continue past blockers.
- Boundary risk: Do not push, merge, or open PRs.
- Boundary risk: Do not create tasks during the batch run unless a bounded policy explicitly supports it later.
- Boundary risk: Do not hide failed step details.
- Verify no background/unsupervised execution is introduced.
- Verify that failed gates are visible and stop the loop.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-056.
- Keeps Change approval as a separate explicit Human Owner action.
- Add run-until-blocker action for an existing or newly created pipeline session.
- Loop over run-next with max steps, max tasks, max failures, and max rework attempts from policy.
- Stop on first blocker, policy violation, unsafe condition, token budget failure, report failure, review failure, commit readiness failure, or queue completion.
- Persist each step result to session state and pipeline audit events.
- Return a final summary with completed tasks, changed tasks, requested changes, accepted Changes, commits if any, blockers, and next owner action.
- Batch runner stops on the first blocker or policy violation.
- Batch runner stops when token budget gate fails.
- Batch runner stops when queue is complete and reports completion.

Linked tasks:

- TASK-056

### CHG-040 — PIPE-06 Token Budget Gate

Status: `accepted`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-06 requires an explicit Evolution Change Proposal before implementation: Gate Codex execution using the actual prompt payload token budget and policy thresholds.

Proposal:

Implement the bounded task scope: Read the actual generated Codex prompt payload and included Context Pack metadata.; Count tokens through an available local/provider strategy or return token_count_unavailable with a stable reason.; Compare prompt size, model context limit, reserved output tokens, and policy remaining-token threshold.; Fail in strict mode when token count is unavailable.; Fail when prompt does not fit, remaining tokens are below threshold, or context requires compact/split.; Return PASS/WARN/FAIL gate result with measured bytes, estimated/measured tokens, thresholds, and reason.; Expose gate result to pipeline session state and audit.; Add tests for pass, oversized prompt, low remaining tokens, unavailable counter in strict mode, and compact/split required.

Rationale:

Implement the Token Budget Gate that counts or estimates the actual Codex payload, checks remaining-token thresholds, detects unavailable token counting in strict mode, and blocks execution when context must be compacted or split.

Approved by: `human_owner` at `2026-06-19T20:40:49Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-19T21:53:38Z`  
Acceptance notes: Gate Codex execution using the actual prompt payload token budget and policy thresholds.  

Affected files:

- ai_project_ctl/pipeline/token_budget.py
- ai_project_ctl/pipeline/policy.py if policy compatibility is needed
- ai_project_ctl/pipeline/runner.py if integration is needed
- ai_project_ctl/core/registry.py if command metadata is needed
- scripts/aictl.py if gate command routing is needed
- tests/**
- ai-system/project-control/** if token gate documentation is needed

Risks:

- Boundary risk: Do not call external token services unless explicitly configured and policy allows.
- Boundary risk: Do not compact or split context in this task.
- Boundary risk: Do not launch Codex.
- Boundary risk: Do not mutate task scope or allowed_files based on retrieved context.
- Verify strict-mode failure behavior.
- Verify token gate cannot be bypassed by run-next before Codex execution.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-057.
- Keeps Change approval as a separate explicit Human Owner action.
- Read the actual generated Codex prompt payload and included Context Pack metadata.
- Count tokens through an available local/provider strategy or return token_count_unavailable with a stable reason.
- Compare prompt size, model context limit, reserved output tokens, and policy remaining-token threshold.
- Fail in strict mode when token count is unavailable.
- Fail when prompt does not fit, remaining tokens are below threshold, or context requires compact/split.
- Token Budget Gate evaluates the actual Codex prompt payload.
- Gate blocks execution when prompt does not fit or remaining tokens are below policy threshold.
- Gate blocks in strict mode when token count is unavailable.

Linked tasks:

- TASK-057

### CHG-041 — PIPE-07 Codex Execution Adapter

Status: `accepted`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-07 requires an explicit Evolution Change Proposal before implementation: Launch or hand off Codex Executor only after policy and Token Budget Gate PASS, then capture execution metadata.

Proposal:

Implement the bounded task scope: Define Codex Execution Adapter interface with dry-run, manual-handoff, and configured-local-command modes if appropriate.; Require policy permission before any non-dry-run execution.; Require Token Budget Gate PASS before execution.; Pass only the generated Codex prompt path/payload and bounded task context.; Capture start/end time, return code, stdout/stderr references, timeout, and adapter mode.; Require Codex to submit a structured execution report through the existing report path before downstream gates can pass.; Stop safely on timeout, non-zero exit, missing prompt, stale prompt, or missing report.; Add tests with a fake adapter/runner; do not require real Codex in normal test runs.

Rationale:

Add a controlled Codex execution adapter with dry-run/manual default behavior, explicit policy enablement, timeout, command allowlist, captured output, and report handoff instructions.

Approved by: `human_owner` at `2026-06-19T20:41:09Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-19T22:14:54Z`  
Acceptance notes: Accepted after task PIPE-07 review  

Affected files:

- ai_project_ctl/pipeline/codex_adapter.py
- ai_project_ctl/pipeline/runner.py if integration is needed
- ai_project_ctl/pipeline/policy.py if policy compatibility is needed
- ai_project_ctl/core/registry.py if command metadata is needed
- scripts/aictl.py if adapter command routing is needed
- tests/**
- ai-system/project-control/** if adapter documentation is needed

Risks:

- Boundary risk: Do not bypass task allowed_files.
- Boundary risk: Do not give Codex permission to push, merge, or approve owner decisions.
- Boundary risk: Do not require external Codex services for local tests.
- Boundary risk: Do not auto-close tasks based only on adapter success.
- Verify no external execution happens by default.
- Verify adapter cannot run before Token Budget Gate PASS.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-058.
- Keeps Change approval as a separate explicit Human Owner action.
- Define Codex Execution Adapter interface with dry-run, manual-handoff, and configured-local-command modes if appropriate.
- Require policy permission before any non-dry-run execution.
- Require Token Budget Gate PASS before execution.
- Pass only the generated Codex prompt path/payload and bounded task context.
- Capture start/end time, return code, stdout/stderr references, timeout, and adapter mode.
- Adapter default mode is safe and does not unexpectedly launch external tools.
- Adapter refuses execution unless policy allows it and Token Budget Gate PASS is present.
- Adapter captures execution metadata and exposes it to pipeline session state.

Linked tasks:

- TASK-058

### CHG-042 — PIPE-08 Codex Report Gate

Status: `accepted`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-08 requires an explicit Evolution Change Proposal before implementation: Validate Codex structured execution reports before review and closure gates.

Proposal:

Implement the bounded task scope: Read the latest structured task execution report for the selected task.; Validate report schema, task id/ref match, implementation summary, changed files, generated files, checks, warnings, blockers, notes, owner decision flag, and token usage fields.; Require blockers to stop the pipeline.; Require token usage evidence when policy requires it.; Reject reports with changed files outside task allowed_files unless explicitly classified as generated or governed state output.; Return PASS/WARN/FAIL with report id and failure reasons.; Add tests for missing report, invalid schema, mismatched task, blockers present, missing token usage, and out-of-scope changed files.

Rationale:

Add a report gate that checks the latest Codex execution report for required fields, task identity, token usage, changed files, generated files, checks, warnings, blockers, and credibility basics.

Approved by: `human_owner` at `2026-06-19T20:41:40Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-19T22:36:04Z`  
Acceptance notes: Validate Codex structured execution reports before review and closure gates.  

Affected files:

- ai_project_ctl/pipeline/report_gate.py
- ai_project_ctl/pipeline/runner.py if integration is needed
- scripts/taskctl.py if report schema compatibility is required
- ai_project_ctl/web/read_model.py if report gate status is surfaced
- tests/**
- ai-system/project-control/** if report gate documentation is needed

Risks:

- Boundary risk: Do not decide semantic acceptance criteria; that belongs to Codex Review Gate.
- Boundary risk: Do not close tasks.
- Boundary risk: Do not edit report state manually.
- Boundary risk: Do not hide blockers as warnings.
- Verify report credibility checks are machine-checkable and do not replace semantic review.
- Verify blockers cannot be downgraded silently.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-059.
- Keeps Change approval as a separate explicit Human Owner action.
- Read the latest structured task execution report for the selected task.
- Validate report schema, task id/ref match, implementation summary, changed files, generated files, checks, warnings, blockers, notes, owner decision flag, and token usage fields.
- Require blockers to stop the pipeline.
- Require token usage evidence when policy requires it.
- Reject reports with changed files outside task allowed_files unless explicitly classified as generated or governed state output.
- Report Gate blocks missing, invalid, mismatched, or blocker-containing reports.
- Report Gate checks changed files against task allowed_files/governed generated files.
- Report Gate checks token usage when policy requires it.

Linked tasks:

- TASK-059

### CHG-043 — PIPE-09 Machine Review Gate

Status: `accepted`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-09 requires an explicit Evolution Change Proposal before implementation: Run deterministic machine checks for tests, doctor, protected files, generated outputs, allowed_files, token usage, and blockers.

Proposal:

Implement the bounded task scope: Run or collect project-control validation checks: task validate, task graph validate, generated checks, evolution validate/check-generated, context validate/check-generated, project doctor, and protected-file check.; Run task/report-declared tests or configured test commands only when policy allows and commands are safe.; Check changed files against task allowed_files and protected-file rules.; Check report blockers and token usage against policy.; Return PASS only when all blocking checks pass.; Return structured evidence with command, result, duration if available, stdout/stderr summaries, and failure reasons.; Add tests with fake command runners and representative pass/fail cases.

Rationale:

Implement the machine review gate that collects deterministic evidence before Codex semantic review or auto-close decisions.

Approved by: `human_owner` at `2026-06-19T20:42:05Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-20T06:12:52Z`  
Acceptance notes: Run deterministic machine checks for tests, doctor, protected files, generated outputs, allowed_files, token usage, and blockers.  

Affected files:

- ai_project_ctl/pipeline/machine_review.py
- ai_project_ctl/pipeline/report_gate.py if integration is needed
- ai_project_ctl/pipeline/runner.py if integration is needed
- ai_project_ctl/core/registry.py if command metadata is needed
- scripts/aictl.py if gate command routing is needed
- tests/**
- ai-system/project-control/** if machine review documentation is needed

Risks:

- Boundary risk: Do not do semantic acceptance review.
- Boundary risk: Do not close tasks.
- Boundary risk: Do not accept Changes.
- Boundary risk: Do not commit.
- Boundary risk: Do not suppress doctor/protected-file failures.
- Verify that deterministic checks are actually blocking.
- Verify that allowed_files/protected-file checks cannot be bypassed by report wording.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-060.
- Keeps Change approval as a separate explicit Human Owner action.
- Run or collect project-control validation checks: task validate, task graph validate, generated checks, evolution validate/check-generated, context validate/check-generated, project doctor, and protected-file check.
- Run task/report-declared tests or configured test commands only when policy allows and commands are safe.
- Check changed files against task allowed_files and protected-file rules.
- Check report blockers and token usage against policy.
- Return PASS only when all blocking checks pass.
- Machine Review PASS requires all blocking checks to pass.
- Machine Review FAIL stops the pipeline.
- Protected-file and allowed_files violations are blocking.

Linked tasks:

- TASK-060

### CHG-044 — PIPE-10 Codex Review Gate

Status: `accepted`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-10 requires an explicit Evolution Change Proposal before implementation: Run a narrow read-only Codex Reviewer prompt for semantic review and structured verdict.

Proposal:

Implement the bounded task scope: Create a narrow review prompt package for Codex Reviewer.; Include task scope, out_of_scope, acceptance criteria, allowed_files, execution report summary, machine review evidence, changed files, and relevant context references.; Require reviewer role to be read-only: no file edits, no lifecycle transitions, no commits.; Support structured verdicts APPROVE, REQUEST_CHANGES, BLOCKED with findings and severity.; Fail the gate if reviewer output is missing, malformed, or contradicts required evidence.; Expose review result to pipeline session state and audit.; Add tests using fake reviewer outputs for approve, request changes, blocked, malformed, and missing verdict.

Rationale:

Add the semantic review gate. It should generate and optionally run a narrow Codex Reviewer prompt that checks acceptance criteria, out_of_scope, hidden risks, and report credibility without changing files or lifecycle state.

Approved by: `human_owner` at `2026-06-19T20:42:35Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-20T06:29:13Z`  
Acceptance notes: Run a narrow read-only Codex Reviewer prompt for semantic review and structured verdict.  

Affected files:

- ai_project_ctl/pipeline/codex_review.py
- ai_project_ctl/pipeline/runner.py if integration is needed
- AI_PROJECT/generated/PIPELINE_REVIEW_PROMPT.md via governed CLI/service only if implemented
- AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only
- tests/**
- ai-system/project-control/** if review gate documentation is needed

Risks:

- Boundary risk: Do not let reviewer edit files.
- Boundary risk: Do not let reviewer move task lifecycle.
- Boundary risk: Do not let reviewer approve as Human Owner.
- Boundary risk: Do not auto-close tasks in this task.
- Boundary risk: Do not run reviewer before Machine Review evidence exists.
- Verify reviewer prompt does not authorize file edits or lifecycle movement.
- Verify semantic verdict cannot override Machine Review FAIL.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-061.
- Keeps Change approval as a separate explicit Human Owner action.
- Create a narrow review prompt package for Codex Reviewer.
- Include task scope, out_of_scope, acceptance criteria, allowed_files, execution report summary, machine review evidence, changed files, and relevant context references.
- Require reviewer role to be read-only: no file edits, no lifecycle transitions, no commits.
- Support structured verdicts APPROVE, REQUEST_CHANGES, BLOCKED with findings and severity.
- Fail the gate if reviewer output is missing, malformed, or contradicts required evidence.
- Codex Review Gate prompt is narrow and read-only.
- Reviewer cannot mutate files, lifecycle, or commits through this gate.
- Gate accepts only structured verdicts APPROVE, REQUEST_CHANGES, or BLOCKED.

Linked tasks:

- TASK-061

### CHG-045 — PIPE-11 Auto Review Auto Close Policy

Status: `accepted`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-11 requires an explicit Evolution Change Proposal before implementation: Apply policy-controlled close/rework decisions only after Machine Review PASS and Codex Review APPROVE.

Proposal:

Implement the bounded task scope: Implement decision logic for Machine Review result plus Codex Review result.; Allow auto-close only if policy allows and Machine Review PASS and Codex Review APPROVE.; Move task to changes_requested or start a bounded rework loop only when policy allows and review verdict requests changes.; Stop when review is blocked, malformed, failing, or policy disallows automatic lifecycle mutation.; Require explicit audit notes that identify policy, machine gate, Codex review verdict, and report id.; Prevent auto-close when task report has blockers or changed files outside allowed_files.; Add tests for approve+pass close, request changes, blocked review, machine fail, policy disabled, and rework-limit reached.

Rationale:

Implement the decision logic that maps review gate results into task done, changes_requested, rework loop, or stop states under explicit automation policy.

Approved by: `human_owner` at `2026-06-19T20:43:02Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-20T06:47:03Z`  
Acceptance notes: Apply policy-controlled close/rework decisions only after Machine Review PASS and Codex Review APPROVE.  

Affected files:

- ai_project_ctl/pipeline/close_policy.py
- ai_project_ctl/pipeline/runner.py if integration is needed
- ai_project_ctl/core/workflows.py if close/request-changes workflow metadata needs compatible updates
- tests/**
- ai-system/project-control/** if auto-close documentation is needed

Risks:

- Boundary risk: Do not bypass task lifecycle transitions.
- Boundary risk: Do not accept linked Evolution Changes.
- Boundary risk: Do not commit.
- Boundary risk: Do not treat Codex Review as Human Owner approval outside the selected policy.
- Boundary risk: Do not continue rework indefinitely.
- Verify auto-close cannot happen on Machine Review FAIL or Codex Review REQUEST_CHANGES.
- Verify lifecycle changes are routed through governed commands.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-062.
- Keeps Change approval as a separate explicit Human Owner action.
- Implement decision logic for Machine Review result plus Codex Review result.
- Allow auto-close only if policy allows and Machine Review PASS and Codex Review APPROVE.
- Move task to changes_requested or start a bounded rework loop only when policy allows and review verdict requests changes.
- Stop when review is blocked, malformed, failing, or policy disallows automatic lifecycle mutation.
- Require explicit audit notes that identify policy, machine gate, Codex review verdict, and report id.
- Auto-close requires policy permission, Machine Review PASS, and Codex Review APPROVE.
- REQUEST_CHANGES moves to changes_requested or starts rework only if policy allows.
- Blocked or failed gates stop the pipeline.

Linked tasks:

- TASK-062

### CHG-046 — PIPE-12 Controlled Git Commit Action

Status: `accepted`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-12 requires an explicit Evolution Change Proposal before implementation: Create local commits only when policy allows and commit readiness is green.

Proposal:

Implement the bounded task scope: Implement read-only commit readiness check reuse or integration with the existing Commit Readiness view.; Implement local commit action only behind explicit policy permission.; Require clean readiness: task done, required Change accepted if policy requires it, machine checks pass, protected-file checks pass, generated outputs fresh, no unrelated dirty files unless policy explicitly allows.; Stage only files approved by policy/session evidence.; Generate commit message from completed task refs, Change ids, and session id.; Run git commit locally only; explicitly forbid push, merge, reset, checkout, rebase, and destructive git commands.; Record commit hash or failure in pipeline session/audit.; Add tests with fake git runner for readiness green, readiness fail, unrelated files, commit success, and forbidden command attempts.

Rationale:

Add a controlled local git commit action for completed pipeline work. It must never push, merge, reset, discard, or create remote changes.

Approved by: `human_owner` at `2026-06-19T20:43:32Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-20T07:03:47Z`  
Acceptance notes: Create local commits only when policy allows and commit readiness is green.  

Affected files:

- ai_project_ctl/pipeline/git_commit.py
- ai_project_ctl/pipeline/runner.py if integration is needed
- ai_project_ctl/web/read_model.py if commit readiness data is reused
- ai_project_ctl/core/registry.py if command metadata is needed
- scripts/aictl.py if commit command routing is needed
- tests/**
- ai-system/project-control/** if git commit policy documentation is needed

Risks:

- Boundary risk: Do not push.
- Boundary risk: Do not merge.
- Boundary risk: Do not open PRs.
- Boundary risk: Do not discard or reset changes.
- Boundary risk: Do not commit when readiness is not green.
- Boundary risk: Do not auto-accept Changes in this task.
- Verify command allowlist forbids push/merge/destructive git actions.
- Verify readiness failure blocks commit.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-063.
- Keeps Change approval as a separate explicit Human Owner action.
- Implement read-only commit readiness check reuse or integration with the existing Commit Readiness view.
- Implement local commit action only behind explicit policy permission.
- Require clean readiness: task done, required Change accepted if policy requires it, machine checks pass, protected-file checks pass, generated outputs fresh, no unrelated dirty files unless policy explicitly allows.
- Stage only files approved by policy/session evidence.
- Generate commit message from completed task refs, Change ids, and session id.
- Commit action is disabled unless policy explicitly allows local commit.
- Commit action refuses when commit readiness is not green.
- Commit action stages only approved files.

Linked tasks:

- TASK-063

### CHG-047 — PIPE-13 Pipeline UI Dashboard

Status: `accepted`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-13 requires an explicit Evolution Change Proposal before implementation: Add a Web Control Center dashboard for pipeline sessions, queue preview, policy selection, run-next, and run-until-blocker.

Proposal:

Implement the bounded task scope: Add Pipeline dashboard/page to the Web Control Center.; Show policy selector/preset preview, queue selector, queue preview, session status, current step, gates, stop reason, and latest audit entries.; Expose Create Session, Run Next, Run Until Blocker, Stop Session, and Refresh Status actions where implemented.; Require explicit confirmation for any write/run action.; Show action result panel with step status, blockers, changed/generated files, reports, reviews, and next actions.; Keep UI local-only and route writes through governed commands/workflows.; Add tests for dashboard rendering, confirmation requirements, and action routing.

Rationale:

Expose supervised pipeline operation in the local Web Control Center without weakening confirmation, policy, or lifecycle gates.

Approved by: `human_owner` at `2026-06-19T20:43:50Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-20T08:53:21Z`  
Acceptance notes: Approve  

Affected files:

- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/pipeline/** if UI integration requires compatible changes
- ai_project_ctl/core/registry.py if action metadata is needed
- scripts/aictl.py if routing is needed
- tests/test_web_control_center.py
- tests/**
- ai-system/project-control/** if UI documentation is needed

Risks:

- Boundary risk: Do not add remote hosting.
- Boundary risk: Do not bypass pipeline policy.
- Boundary risk: Do not auto-start sessions on page load.
- Boundary risk: Do not run arbitrary shell commands from UI.
- Boundary risk: Do not hide blockers or failed gates.
- Verify UI cannot start or continue pipeline silently.
- Verify all mutations route through governed command paths.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-064.
- Keeps Change approval as a separate explicit Human Owner action.
- Add Pipeline dashboard/page to the Web Control Center.
- Show policy selector/preset preview, queue selector, queue preview, session status, current step, gates, stop reason, and latest audit entries.
- Expose Create Session, Run Next, Run Until Blocker, Stop Session, and Refresh Status actions where implemented.
- Require explicit confirmation for any write/run action.
- Show action result panel with step status, blockers, changed/generated files, reports, reviews, and next actions.
- Pipeline dashboard shows sessions, selected policy, queue preview, current step, and stop reason.
- Run actions require explicit confirmation.
- UI writes route through governed commands/workflows.

Linked tasks:

- TASK-064

### CHG-048 — PIPE-14 Pipeline Audit Trail

Status: `accepted`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-14 requires an explicit Evolution Change Proposal before implementation: Record a complete audit trail for pipeline sessions, policy decisions, gates, Codex runs, reviews, stops, and commits.

Proposal:

Implement the bounded task scope: Define pipeline event types for session create, policy selected, queue planned, task selected, Change created/approved/accepted, context built, token gate result, Codex run result, report gate result, machine review, Codex review, close/rework decision, commit readiness, commit result, stop, and completion.; Append events through governed pipeline services only.; Generate a readable Pipeline Audit or Pipeline Status timeline if useful.; Include stable ids for session, task, Change, report, review, gate, and commit references.; Avoid storing secrets or excessive raw prompt contents in audit events.; Add tests for event append, validation, generated output freshness, and redaction/sizing behavior.

Rationale:

Strengthen pipeline observability by adding structured audit events and generated timeline output for all supervised batch decisions.

Approved by: `human_owner` at `2026-06-19T20:44:16Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-20T08:53:06Z`  
Acceptance notes: Approve  

Affected files:

- ai_project_ctl/pipeline/audit.py
- ai_project_ctl/pipeline/session.py
- ai_project_ctl/pipeline/** if integration is needed
- AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_AUDIT.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only
- tests/**
- ai-system/project-control/** if audit documentation is needed

Risks:

- Boundary risk: Do not make audit logs editable from UI.
- Boundary risk: Do not store raw secrets.
- Boundary risk: Do not store full huge prompt payloads when hashes/paths are sufficient.
- Boundary risk: Do not replace existing task/evolution/codex/context event logs.
- Verify event/state/generated separation.
- Verify audit is sufficient to reconstruct why pipeline stopped.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-065.
- Keeps Change approval as a separate explicit Human Owner action.
- Define pipeline event types for session create, policy selected, queue planned, task selected, Change created/approved/accepted, context built, token gate result, Codex run result, report gate result, machine review, Codex review, close/rework decision, commit readiness, commit result, stop, and completion.
- Append events through governed pipeline services only.
- Generate a readable Pipeline Audit or Pipeline Status timeline if useful.
- Include stable ids for session, task, Change, report, review, gate, and commit references.
- Avoid storing secrets or excessive raw prompt contents in audit events.
- Pipeline audit captures every major gate and decision.
- Audit events include stable references and stop reasons.
- Audit avoids raw secrets and oversized prompt payloads.

Linked tasks:

- TASK-065

### CHG-049 — PIPE-15 Pipeline SOP Documentation

Status: `accepted`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-15 requires an explicit Evolution Change Proposal before implementation: Document the supervised batch pipeline runner, policies, gates, UI flow, blockers, and operator responsibilities.

Proposal:

Implement the bounded task scope: Create or update pipeline runner documentation.; Document Queue -> Policy -> Change -> Prepare -> Token Gate -> Codex Execute -> Report -> Machine Review -> Codex Review -> Done/Rework -> Accept Change -> Commit -> Next / Stop on Blocker.; Document policy presets and what each one may or may not automate.; Document token budget gate behavior and strict-mode failure cases.; Document Codex Executor report requirements and Codex Reviewer read-only responsibilities.; Document Machine Review and Codex Review gate meanings.; Document auto-close, rework loop, Change acceptance, and local commit rules.; Document UI dashboard operation and CLI equivalents.; Document common blockers, unsafe conditions, recovery paths, and audit trail interpretation.; Run docctl validation/render/check-generated and project-control checks.

Rationale:

Create owner-facing and system-facing SOP documentation for the PIPE epic after implementation details are stable.

Approved by: `human_owner` at `2026-06-19T20:44:39Z`  
Approval notes: Approved  

Accepted by: `human_owner` at `2026-06-20T09:12:02Z`  
Acceptance notes: Approve  

Affected files:

- ai-system/project-control/pipeline-runner.md
- ai-system/project-control/10-owner-quickstart.md
- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/README.md if index update is needed
- README.md if owner-facing quick links are needed
- AGENTS.md if Codex handoff rules need a pointer
- AI_PROJECT/state/docs.json via docctl.py only
- AI_PROJECT/events/doc-events.jsonl via docctl.py only
- AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only
- AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only

Risks:

- Boundary risk: Do not change pipeline command behavior.
- Boundary risk: Do not mark documentation accepted without Human Owner approval.
- Boundary risk: Do not edit generated documentation manually.
- Boundary risk: Do not document unsupported unsafe automation as available.
- Verify documentation does not overclaim unimplemented behavior.
- Verify generated docs are refreshed only through docctl.py.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-066.
- Keeps Change approval as a separate explicit Human Owner action.
- Create or update pipeline runner documentation.
- Document Queue -> Policy -> Change -> Prepare -> Token Gate -> Codex Execute -> Report -> Machine Review -> Codex Review -> Done/Rework -> Accept Change -> Commit -> Next / Stop on Blocker.
- Document policy presets and what each one may or may not automate.
- Document token budget gate behavior and strict-mode failure cases.
- Document Codex Executor report requirements and Codex Reviewer read-only responsibilities.
- Pipeline SOP documents the approved algorithm and stop conditions.
- Documentation clearly distinguishes policy-selected automation from forbidden autonomy.
- Documentation says Codex Reviewer is read-only and cannot mutate files/lifecycle/commits.

Linked tasks:

- TASK-066

### CHG-050 — BUG-01 Fix Approve & Done stale execution context handling

Status: `accepted`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-16 requires an explicit Evolution Change Proposal before implementation: Fix the Web Control Center / workflow issue where Approve & Done can be blocked by stale Context Pack or Codex prompt state and where closed tasks can leave a stale Codex execution package behind.

Proposal:

Implement the bounded task scope: Adjust task.close_reviewed so stale Context Pack / Codex prompt freshness does not block Human Owner approval and done transition.; Keep owner confirmation and non-empty approval notes mandatory for Approve & Done.; Keep task lifecycle, task graph, generated task output, evolution, protected-file, and project doctor checks where they are relevant to closure.; Preserve visibility of stale context/prompt state as a warning or result detail instead of hiding it.; After successful Approve & Done, clear or invalidate current_execution when it targets the task that was just closed.; Use an existing governed command such as codexctl.py clear if suitable, or add a small registered/facade workflow step if needed.; Update Web Control Center hints so an in_review task can still expose Approve & Done even when execution context is stale.; Add or update tests covering stale context in_review close, post-close execution cleanup, required approval notes, invalid status rejection, and no direct protected-file writes.

Rationale:

Implement options B + C from the review: B) Approve & Done must not require Refresh Context when the task is already in review and owner approval notes are provided; stale execution context may be reported as a warning, not a lifecycle blocker. C) after a reviewed task is successfully approved and transitioned to done, clear or invalidate current Codex execution state when it still points to the closed task.

Approved by: `human_owner` at `2026-06-20T07:35:54Z`  
Approval notes: Approve Change  

Accepted by: `human_owner` at `2026-06-20T08:52:58Z`  
Acceptance notes: Approve  

Affected files:

- ai_project_ctl/core/workflows.py
- ai_project_ctl/core/registry.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/actions.py
- scripts/aictl.py
- scripts/codexctl.py
- tests/test_workflows.py
- tests/test_web_control_center.py
- tests/test_aictl.py
- tests/test_registry.py
- ai-system/project-control/08-usage-guide.md if owner-facing workflow documentation needs a small clarification
- ai-system/project-control/10-owner-quickstart.md if owner-facing workflow documentation needs a small clarification

Risks:

- Boundary risk: Do not weaken Human Owner approval gates.
- Boundary risk: Do not allow Codex to self-approve tasks.
- Boundary risk: Do not silently accept linked Evolution Changes.
- Boundary risk: Do not hide stale context/prompt warnings from the UI or action result.
- Boundary risk: Do not auto-refresh Context Pack or Codex Prompt as part of approval unless explicitly justified by the implementation.
- Boundary risk: Do not manually edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.
- Verify that the fix implements options B + C, not option A.
- Verify that no approval gate was weakened and owner notes remain required.
- Verify that stale execution context is not hidden, only made non-blocking for closure.
- Verify that current_execution cleanup is conditional on the closed task identity.
- Verify that generated files were not edited manually.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-067.
- Keeps Change approval as a separate explicit Human Owner action.
- Adjust task.close_reviewed so stale Context Pack / Codex prompt freshness does not block Human Owner approval and done transition.
- Keep owner confirmation and non-empty approval notes mandatory for Approve & Done.
- Keep task lifecycle, task graph, generated task output, evolution, protected-file, and project doctor checks where they are relevant to closure.
- Preserve visibility of stale context/prompt state as a warning or result detail instead of hiding it.
- After successful Approve & Done, clear or invalidate current_execution when it targets the task that was just closed.
- A task in in_review with stale Context Pack or stale Codex prompt can be closed through Approve & Done when explicit owner notes and confirmation are provided.
- Approve & Done still rejects tasks outside in_review.
- Approve & Done still requires non-empty owner approval notes.

Linked tasks:

- TASK-067

### CHG-051 — PIPE-17 Add Custom Pipeline Policy Preset Store

Status: `approved`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-17 requires an explicit Evolution Change Proposal before implementation: Add governed storage for user-defined pipeline policy presets while keeping built-in safe presets immutable.

Proposal:

Implement the bounded task scope: Create a governed custom pipeline policy preset storage model.; Store custom presets separately from built-in presets.; Keep built-in presets dry_run, supervised, supervised_autoclose, and supervised_local_commit immutable.; Validate saved presets through the existing PipelinePolicy validation rules.; Reject unsafe presets with stable error codes.; Add audit events for preset create/update/delete operations.; Add generated policy status output if useful for UI and validation.

Rationale:

Introduce a persistent custom policy preset store so the Human Owner can save, validate, list, and delete pipeline policy presets without editing Python source or protected state manually.

Approved by: `human_owner` at `2026-06-20T09:47:19Z`  
Approval notes: Approve  

Affected files:

- ai_project_ctl/pipeline/policy.py
- ai_project_ctl/pipeline/policy_store.py
- ai_project_ctl/pipeline/__init__.py
- ai_project_ctl/core/registry.py
- scripts/aictl.py
- AI_PROJECT/state/pipeline_policy_presets.json via governed CLI/service only
- AI_PROJECT/events/pipeline-policy-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_POLICIES.md via governed CLI/service only
- tests/**

Risks:

- Boundary risk: Do not allow custom presets to authorize push, merge, reset, rebase, clean, or destructive git operations.
- Boundary risk: Do not allow custom presets to bypass Token Budget Gate, Machine Review, Codex Review, Human Owner approval, or Evolution Change gates.
- Boundary risk: Do not modify built-in preset definitions except for compatibility wiring.
- Boundary risk: Do not edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/** manually.
- Verify that custom presets cannot weaken forbidden safety boundaries.
- Verify that built-in presets cannot be overwritten or deleted.
- Verify that all persistence goes through governed service paths.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-068.
- Keeps Change approval as a separate explicit Human Owner action.
- Create a governed custom pipeline policy preset storage model.
- Store custom presets separately from built-in presets.
- Keep built-in presets dry_run, supervised, supervised_autoclose, and supervised_local_commit immutable.
- Validate saved presets through the existing PipelinePolicy validation rules.
- Reject unsafe presets with stable error codes.
- Custom policy presets can be saved, loaded, validated, listed, and deleted through governed service paths.
- Built-in policy presets remain available and immutable.
- Invalid or unsafe custom presets are rejected before persistence.

Linked tasks:

- TASK-068

### CHG-052 — PIPE-23 Add Auto-Create Missing Changes Policy Checkbox

Status: `approved`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-23 requires an explicit Evolution Change Proposal before implementation: Add a pipeline policy checkbox that creates missing linked Evolution Changes for the selected pipeline queue before execution.

Proposal:

Implement the bounded task scope: Expose evolution.create_missing_change as an owner-facing policy checkbox in Pipeline policy editor / policy preview.; Add or update a policy preset option such as supervised_auto_create_changes.; When enabled, pipeline should create missing linked Evolution Changes for selected session tasks.; Prefer preflight behavior for the selected queue, not only the first next task, so PIPE-17..PIPE-21 can be prepared in one pipeline session.; Created Changes must be linked to their corresponding tasks.; Created Changes must include enough title/summary/scope metadata for owner review.; Created Changes must be recorded in pipeline session data and audit output.; If only auto-create is enabled and owner approval is not enabled, pipeline must stop in a resumable owner-action-required state after creating Changes.; If both auto-create and owner-approved session Changes are enabled, pipeline may create missing Changes and then pass them to the session approval gate in the same run.; Update Pipeline Policy Preview to show Auto Create Missing Changes = yes/no.; Update Web Control Center Pipeline form to include the checkbox.; Update CLI session create / policy configuration support if needed.; Add tests for creating missing Changes for one task and for multiple selected queue tasks.

Rationale:

Add owner-facing policy support for automatically creating missing Evolution Changes for tasks selected by the pipeline session. This must be controlled by an explicit policy/UI checkbox and must not approve the created Changes unless the separate owner-approved session Changes policy is enabled.

Approved by: `human_owner` at `2026-06-20T09:59:32Z`  
Approval notes: Approve  

Affected files:

- ai_project_ctl/pipeline/policy.py
- ai_project_ctl/pipeline/runner.py
- ai_project_ctl/pipeline/session.py
- ai_project_ctl/pipeline/state.py
- ai_project_ctl/pipeline/batch.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/registry.py
- scripts/aictl.py
- scripts/evolutionctl.py if existing workflow integration is needed
- tests/test_pipeline_runner.py
- tests/test_pipeline_batch.py
- tests/test_web_control_center.py
- tests/test_aictl.py
- tests/test_registry.py
- AI_PROJECT/state/evolution.json via governed CLI/service only
- AI_PROJECT/events/evolution-events.jsonl via governed CLI/service only
- AI_PROJECT/state/pipeline_sessions.json via governed CLI/service only
- AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/EVOLUTION_STATUS.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_AUDIT.md via governed CLI/service only

Risks:

- Boundary risk: Do not approve Evolution Changes in this task unless PIPE-24 policy is also implemented and explicitly enabled.
- Boundary risk: Do not accept Evolution Changes.
- Boundary risk: Do not bypass Human Owner approval semantics.
- Boundary risk: Do not bypass Codex execution, token, report, review, close, or commit gates.
- Boundary risk: Do not push, merge, reset, rebase, clean, restore, or discard git changes.
- Boundary risk: Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.
- Create a pipeline session for PIPE-17..PIPE-21 with Auto-create missing Changes enabled.
- Verify missing Changes are created and linked to the correct tasks.
- Verify pipeline does not approve them unless PIPE-24 session approval is enabled.
- Verify audit and generated views show created Change ids.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-074.
- Keeps Change approval as a separate explicit Human Owner action.
- Expose evolution.create_missing_change as an owner-facing policy checkbox in Pipeline policy editor / policy preview.
- Add or update a policy preset option such as supervised_auto_create_changes.
- When enabled, pipeline should create missing linked Evolution Changes for selected session tasks.
- Prefer preflight behavior for the selected queue, not only the first next task, so PIPE-17..PIPE-21 can be prepared in one pipeline session.
- Created Changes must be linked to their corresponding tasks.
- Pipeline UI has an Auto-create missing Changes checkbox.
- Policy preview clearly shows whether missing Changes will be created automatically.
- When enabled, selected tasks without linked Changes receive newly created linked Evolution Changes.

Linked tasks:

- TASK-074

### CHG-053 — PIPE-24 Add Owner-Approved Session Changes Policy Checkbox

Status: `approved`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-24 requires an explicit Evolution Change Proposal before implementation: Add a pipeline policy checkbox that lets the Human Owner approve all required Changes for the selected session queue as part of the pipeline run.

Proposal:

Implement the bounded task scope: Add a new safe policy field distinct from evolution.approve_linked_change, for example evolution.owner_approve_required_changes_for_session.; Do not reuse approve_linked_change if it represents autonomous policy self-approval.; Require explicit Human Owner confirmation when this checkbox is enabled.; Require an approval note/reason when this checkbox is enabled.; Store owner approval intent in the pipeline session snapshot.; Approve only Changes linked to tasks selected by the current pipeline session queue.; If Auto-create missing Changes is also enabled, allow pipeline to create missing Changes and approve those newly created Changes in the same owner-confirmed session.; If a selected task has an existing ready/proposed linked Change, allow the session approval policy to approve it.; Do not approve Changes outside the selected session queue.; Do not accept Changes automatically.; Do not approve Changes if the owner approval checkbox was not explicitly enabled.; Add Web Control Center checkbox: Owner-approve required Changes for this session.; Add approval note field to Pipeline session create form when checkbox is enabled.; Add Policy Preview rows for Owner Session Change Approval and Approval Note Required.; Add CLI support for equivalent flags, for example --owner-approve-required-changes and --approval-note.; Update pipeline audit to record approved Change ids, linked task refs, actor, approval note, and session id.; After required Changes are approved, pipeline should continue the same session if resume/waiting behavior is available.; Add tests for approving multiple Changes in one owner-confirmed pipeline run.

Rationale:

Add a safe owner-approved policy mode for approving required Evolution Changes across the selected pipeline session. This is not autonomous pipeline self-approval: the Human Owner must explicitly select the policy checkbox, confirm the session, and provide an approval note. The pipeline may then approve only the Changes required by that selected session queue.

Approved by: `human_owner` at `2026-06-20T09:59:40Z`  
Approval notes: Approve  

Affected files:

- ai_project_ctl/pipeline/policy.py
- ai_project_ctl/pipeline/runner.py
- ai_project_ctl/pipeline/session.py
- ai_project_ctl/pipeline/state.py
- ai_project_ctl/pipeline/batch.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/registry.py
- ai_project_ctl/core/workflows.py
- scripts/aictl.py
- scripts/evolutionctl.py if existing approve command integration is needed
- tests/test_pipeline_runner.py
- tests/test_pipeline_batch.py
- tests/test_web_control_center.py
- tests/test_aictl.py
- tests/test_registry.py
- AI_PROJECT/state/evolution.json via governed CLI/service only
- AI_PROJECT/events/evolution-events.jsonl via governed CLI/service only
- AI_PROJECT/state/pipeline_sessions.json via governed CLI/service only
- AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/EVOLUTION_STATUS.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_AUDIT.md via governed CLI/service only

Risks:

- Boundary risk: Do not allow fully autonomous approval without Human Owner confirmation.
- Boundary risk: Do not make evolution.approve_linked_change valid if it means unsafe auto-approval.
- Boundary risk: Do not accept Evolution Changes automatically.
- Boundary risk: Do not approve unrelated Changes outside the selected session queue.
- Boundary risk: Do not bypass Codex execution, token, report, machine review, Codex review, task close, or commit gates.
- Boundary risk: Do not push, merge, reset, rebase, clean, restore, or discard git changes.
- Boundary risk: Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.
- Create a session for PIPE-17..PIPE-21 with both Auto-create missing Changes and Owner-approve required Changes enabled.
- Provide an approval note and confirm.
- Verify missing Changes are created where needed.
- Verify required Changes for the selected queue are approved.
- Verify no unrelated Changes are approved.
- Verify the same session continues after approval.
- Verify audit trail contains owner approval evidence.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-075.
- Keeps Change approval as a separate explicit Human Owner action.
- Add a new safe policy field distinct from evolution.approve_linked_change, for example evolution.owner_approve_required_changes_for_session.
- Do not reuse approve_linked_change if it represents autonomous policy self-approval.
- Require explicit Human Owner confirmation when this checkbox is enabled.
- Require an approval note/reason when this checkbox is enabled.
- Store owner approval intent in the pipeline session snapshot.
- Pipeline UI has an Owner-approve required Changes for this session checkbox.
- Checkbox requires explicit confirmation and approval note.
- Policy preview clearly distinguishes owner-approved session approval from unsafe automatic approval.

Linked tasks:

- TASK-075

### CHG-054 — PIPE-18 Add Pipeline Policy CRUD Commands

Status: `approved`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-18 requires an explicit Evolution Change Proposal before implementation: Expose custom pipeline policy preset operations through aictl and command registry.

Proposal:

Implement the bounded task scope: Add aictl commands for pipeline policy list/show/validate/save/delete.; Support JSON input for custom policy preset save/update.; Support human-readable and --json output.; Add command registry metadata for policy commands.; Require explicit confirmation for save/update/delete.; Block delete/update for built-in presets.; Add tests for valid save, invalid save, delete, built-in protection, and JSON output.

Rationale:

Add owner-facing CLI commands and registry metadata for policy preset list, show, validate, save, and delete operations.

Approved by: `human_owner` at `2026-06-20T12:01:22Z`  
Approval notes: Approve (pipeline session PSESS-008)  

Affected files:

- scripts/aictl.py
- ai_project_ctl/core/registry.py
- ai_project_ctl/pipeline/policy.py
- ai_project_ctl/pipeline/policy_store.py
- ai_project_ctl/pipeline/session.py if preset resolution needs compatibility updates
- ai_project_ctl/pipeline/runner.py if preset resolution needs compatibility updates
- tests/**
- AI_PROJECT/state/pipeline_policy_presets.json via governed CLI/service only
- AI_PROJECT/events/pipeline-policy-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_POLICIES.md via governed CLI/service only

Risks:

- Boundary risk: Do not add Web UI editing in this task.
- Boundary risk: Do not add new automation permissions beyond the policy model.
- Boundary risk: Do not bypass policy validation.
- Boundary risk: Do not change run-next or run-until-blocker behavior except to read custom presets if already supported by PIPE-17.
- Verify CLI UX and --json output.
- Verify confirmation gates for writes.
- Verify policy validation is not bypassed.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-069.
- Keeps Change approval as a separate explicit Human Owner action.
- Add aictl commands for pipeline policy list/show/validate/save/delete.
- Support JSON input for custom policy preset save/update.
- Support human-readable and --json output.
- Add command registry metadata for policy commands.
- Require explicit confirmation for save/update/delete.
- Owner can list built-in and custom presets through aictl.
- Owner can show one preset through aictl.
- Owner can validate a policy JSON before saving.

Linked tasks:

- TASK-069

### CHG-055 — PIPE-19 Add Dynamic Policy Editor To Web Pipeline Dashboard

Status: `ready`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-19 requires an explicit Evolution Change Proposal before implementation: Allow editing, saving, deleting, and previewing pipeline policy presets from the Web Control Center.

Proposal:

Implement the bounded task scope: Add a policy editor panel to the Pipeline page.; Load built-in and custom presets into the policy selector.; Immediately update Policy Preset Preview when the selected policy changes without requiring the Preview Queue button.; Support editing common policy fields: queue selection, max tasks, Codex mode, adapter mode, token gate, review requirements, auto-close, local commit mode.; Show validation errors live or on preview before save.; Add Save as Custom Preset action routed through governed policy save command.; Add Delete Custom Preset action routed through governed policy delete command.; Protect built-in presets from delete/update in the UI.; Keep queue preview button for queue-specific filters, but decouple policy preview from the button.; Add tests for immediate selected-policy preview, custom save, custom delete, invalid policy display, and built-in protection.

Rationale:

Improve the Pipeline page so the Human Owner can select a policy, immediately see its preview, edit policy fields, save custom presets, and delete custom presets without manual JSON editing.

Affected files:

- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/registry.py if Web action metadata needs updates
- scripts/aictl.py if Web routing needs compatibility updates
- tests/test_web_control_center.py
- tests/test_aictl.py
- tests/test_registry.py
- tests/test_pipeline_policy_store.py

Risks:

- Boundary risk: Do not add remote UI access.
- Boundary risk: Do not write policy files directly from route handlers.
- Boundary risk: Do not allow arbitrary Python, shell commands, or executable content in policy fields.
- Boundary risk: Do not allow UI to weaken pipeline safety validation.
- Boundary risk: Do not remove existing CLI policy commands.
- Verify the exact UX issue from the screenshot: selecting another policy updates the preview immediately.
- Verify that Save/Delete buttons are confirmation-gated.
- Verify that Web route handlers do not write JSON directly.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-070.
- Keeps Change approval as a separate explicit Human Owner action.
- Add a policy editor panel to the Pipeline page.
- Load built-in and custom presets into the policy selector.
- Immediately update Policy Preset Preview when the selected policy changes without requiring the Preview Queue button.
- Support editing common policy fields: queue selection, max tasks, Codex mode, adapter mode, token gate, review requirements, auto-close, local commit mode.
- Show validation errors live or on preview before save.
- Changing the policy select immediately updates Policy Preset Preview without pressing Preview Queue.
- Owner can save a custom preset from the UI with explicit confirmation.
- Owner can delete a custom preset from the UI with explicit confirmation.

Linked tasks:

- TASK-070

### CHG-056 — PIPE-20 Document Dynamic Pipeline Policy Presets

Status: `ready`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-20 requires an explicit Evolution Change Proposal before implementation: Update owner-facing SOP and quickstart documentation for custom policy presets and dynamic preview behavior.

Proposal:

Implement the bounded task scope: Update pipeline runner SOP with custom preset storage and safety rules.; Update owner quickstart with Web policy editor flow.; Document CLI commands for policy list/show/validate/save/delete.; Document that built-in presets are immutable.; Document that dynamic preview is read-only and does not create a session or run the pipeline.; Run documentation-control validation, render, and check-generated.

Rationale:

Document how to use built-in and custom pipeline policy presets from CLI and Web Control Center, including save/delete rules, validation, safety boundaries, and immediate preview behavior.

Affected files:

- ai-system/project-control/pipeline-runner.md
- ai-system/project-control/10-owner-quickstart.md
- ai-system/project-control/08-usage-guide.md if needed
- AI_PROJECT/state/docs.json via docctl.py only
- AI_PROJECT/events/doc-events.jsonl via docctl.py only
- AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only
- AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only

Risks:

- Boundary risk: Do not change command behavior.
- Boundary risk: Do not add new policy permissions.
- Boundary risk: Do not edit generated documentation manually.
- Boundary risk: Do not mark docs accepted without Human Owner approval.
- Verify docs match implemented UI and CLI.
- Verify docs do not imply unsafe autonomy or final owner approval bypass.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-071.
- Keeps Change approval as a separate explicit Human Owner action.
- Update pipeline runner SOP with custom preset storage and safety rules.
- Update owner quickstart with Web policy editor flow.
- Document CLI commands for policy list/show/validate/save/delete.
- Document that built-in presets are immutable.
- Document that dynamic preview is read-only and does not create a session or run the pipeline.
- Docs explain how to use custom policy presets in UI.
- Docs explain CLI policy CRUD commands.
- Docs state built-in presets are immutable.

Linked tasks:

- TASK-071

### CHG-057 — PIPE-21 Fix Pipeline Queue Epic Filter Behavior

Status: `ready`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-21 requires an explicit Evolution Change Proposal before implementation: Make Pipeline Queue Preview respect selected Epic filtering by default and avoid showing unrelated tasks from other epics.

Proposal:

Implement the bounded task scope: Inspect ai_project_ctl/pipeline/queue.py filtering behavior.; Inspect ai_project_ctl/web/read_model.py pipeline_dashboard behavior.; Inspect ai_project_ctl/web/server.py Pipeline page rendering.; Change owner-facing Pipeline Queue Preview so selected Epic filters exclude tasks from other Epics by default.; Preserve diagnostic information for skipped/non-matching tasks through an explicit option such as Show skipped, Show non-matching, debug flag, or structured JSON output.; Ensure max_tasks is applied only after Epic/status matching and executable candidate filtering, so old done/skipped tasks do not consume the selected task limit.; Ensure selected Task Refs still work even when Epic filter is empty.; Ensure queue preview still explains why selected in-Epic tasks are waiting, blocked, skipped, or executable.; Update UI labels/help text if needed so the difference between filtered preview and diagnostic skipped rows is clear.; Add or update tests for Epic filtering, status filtering, max_tasks behavior, selected Task Refs, and diagnostic skipped visibility.

Rationale:

Fix the Pipeline Queue Preview behavior where selecting an Epic still renders tasks from other Epics as skipped rows with epic_filter_mismatch. The owner-facing queue preview should focus on the selected Epic by default, while still allowing diagnostic visibility when explicitly requested.

Affected files:

- ai_project_ctl/pipeline/queue.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py if Pipeline form/action fields need compatible updates
- ai_project_ctl/core/registry.py if command metadata needs compatible updates
- scripts/aictl.py if CLI preview/options need compatible updates
- tests/test_pipeline_queue.py
- tests/test_web_control_center.py
- tests/test_aictl.py if CLI behavior is touched
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/CODEX_CURRENT.md via taskctl.py only
- AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only

Risks:

- Boundary risk: Do not change task lifecycle rules.
- Boundary risk: Do not change Pipeline policy safety gates.
- Boundary risk: Do not change Codex execution behavior.
- Boundary risk: Do not auto-run pipeline sessions.
- Boundary risk: Do not hide blockers for tasks inside the selected Epic.
- Boundary risk: Do not remove auditability or JSON/debug visibility for skipped tasks.
- Boundary risk: Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.
- Reproduce the original issue: choose Pipeline page, select Epic EPIC-007, leave Status as Any Status, and verify unrelated CTL/WFA/TIG/TASK rows no longer dominate the default Queue Preview.
- Verify that an explicit diagnostic option can still expose skipped/non-matching tasks if implemented.
- Verify that max_tasks is applied after filtering and no longer blocks PIPE-17 because older done PIPE tasks consumed the limit.
- Verify Web UI and CLI queue preview remain consistent.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-072.
- Keeps Change approval as a separate explicit Human Owner action.
- Inspect ai_project_ctl/pipeline/queue.py filtering behavior.
- Inspect ai_project_ctl/web/read_model.py pipeline_dashboard behavior.
- Inspect ai_project_ctl/web/server.py Pipeline page rendering.
- Change owner-facing Pipeline Queue Preview so selected Epic filters exclude tasks from other Epics by default.
- Preserve diagnostic information for skipped/non-matching tasks through an explicit option such as Show skipped, Show non-matching, debug flag, or structured JSON output.
- When Pipeline Queue Selector has Epic = EPIC-007, the default Queue Preview does not render tasks from EPIC-001, EPIC-002, EPIC-003, EPIC-004, EPIC-005, EPIC-006, or other non-selected Epics.
- Tasks from other Epics may still be visible only through an explicit diagnostic/debug/show-skipped option.
- Selecting Epic = EPIC-007 with Status = planned shows PIPE-17, PIPE-18, PIPE-19, and PIPE-20 or their current imported refs as matching candidates.

Linked tasks:

- TASK-072

### CHG-058 — PIPE-24 Add Owner-Approved Session Changes Policy Checkbox

Status: `ready`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-24 requires an explicit Evolution Change Proposal before implementation: Add a pipeline policy checkbox that lets the Human Owner approve all required Changes for the selected session queue as part of the pipeline run.

Proposal:

Implement the bounded task scope: Add a new safe policy field distinct from evolution.approve_linked_change, for example evolution.owner_approve_required_changes_for_session.; Do not reuse approve_linked_change if it represents autonomous policy self-approval.; Require explicit Human Owner confirmation when this checkbox is enabled.; Require an approval note/reason when this checkbox is enabled.; Store owner approval intent in the pipeline session snapshot.; Approve only Changes linked to tasks selected by the current pipeline session queue.; If Auto-create missing Changes is also enabled, allow pipeline to create missing Changes and approve those newly created Changes in the same owner-confirmed session.; If a selected task has an existing ready/proposed linked Change, allow the session approval policy to approve it.; Do not approve Changes outside the selected session queue.; Do not accept Changes automatically.; Do not approve Changes if the owner approval checkbox was not explicitly enabled.; Add Web Control Center checkbox: Owner-approve required Changes for this session.; Add approval note field to Pipeline session create form when checkbox is enabled.; Add Policy Preview rows for Owner Session Change Approval and Approval Note Required.; Add CLI support for equivalent flags, for example --owner-approve-required-changes and --approval-note.; Update pipeline audit to record approved Change ids, linked task refs, actor, approval note, and session id.; After required Changes are approved, pipeline should continue the same session if resume/waiting behavior is available.; Add tests for approving multiple Changes in one owner-confirmed pipeline run.

Rationale:

Add a safe owner-approved policy mode for approving required Evolution Changes across the selected pipeline session. This is not autonomous pipeline self-approval: the Human Owner must explicitly select the policy checkbox, confirm the session, and provide an approval note. The pipeline may then approve only the Changes required by that selected session queue.

Affected files:

- ai_project_ctl/pipeline/policy.py
- ai_project_ctl/pipeline/runner.py
- ai_project_ctl/pipeline/session.py
- ai_project_ctl/pipeline/state.py
- ai_project_ctl/pipeline/batch.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/registry.py
- ai_project_ctl/core/workflows.py
- scripts/aictl.py
- scripts/evolutionctl.py if existing approve command integration is needed
- tests/test_pipeline_runner.py
- tests/test_pipeline_batch.py
- tests/test_web_control_center.py
- tests/test_aictl.py
- tests/test_registry.py
- AI_PROJECT/state/evolution.json via governed CLI/service only
- AI_PROJECT/events/evolution-events.jsonl via governed CLI/service only
- AI_PROJECT/state/pipeline_sessions.json via governed CLI/service only
- AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/EVOLUTION_STATUS.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_AUDIT.md via governed CLI/service only

Risks:

- Boundary risk: Do not allow fully autonomous approval without Human Owner confirmation.
- Boundary risk: Do not make evolution.approve_linked_change valid if it means unsafe auto-approval.
- Boundary risk: Do not accept Evolution Changes automatically.
- Boundary risk: Do not approve unrelated Changes outside the selected session queue.
- Boundary risk: Do not bypass Codex execution, token, report, machine review, Codex review, task close, or commit gates.
- Boundary risk: Do not push, merge, reset, rebase, clean, restore, or discard git changes.
- Boundary risk: Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.
- Create a session for PIPE-17..PIPE-21 with both Auto-create missing Changes and Owner-approve required Changes enabled.
- Provide an approval note and confirm.
- Verify missing Changes are created where needed.
- Verify required Changes for the selected queue are approved.
- Verify no unrelated Changes are approved.
- Verify the same session continues after approval.
- Verify audit trail contains owner approval evidence.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-075.
- Keeps Change approval as a separate explicit Human Owner action.
- Add a new safe policy field distinct from evolution.approve_linked_change, for example evolution.owner_approve_required_changes_for_session.
- Do not reuse approve_linked_change if it represents autonomous policy self-approval.
- Require explicit Human Owner confirmation when this checkbox is enabled.
- Require an approval note/reason when this checkbox is enabled.
- Store owner approval intent in the pipeline session snapshot.
- Pipeline UI has an Owner-approve required Changes for this session checkbox.
- Checkbox requires explicit confirmation and approval note.
- Policy preview clearly distinguishes owner-approved session approval from unsafe automatic approval.

Linked tasks:

- TASK-075

### CHG-059 — PIPE-25 Add Full Self-Running Pipeline Mode

Status: `accepted`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-25 requires an explicit Evolution Change Proposal before implementation: Turn pipeline from prompt-only orchestration into a real supervised self-running task executor.

Proposal:

Implement the bounded task scope: Add a real executable pipeline policy mode distinct from prompt-only supervised mode.; Add or finalize local Codex RUN_CODEX adapter support.; Allow the pipeline to execute a configured local Codex command against AI_PROJECT/generated/CODEX_PROMPT.md.; Require command allowlist, timeout, prompt freshness, and task identity validation.; Capture Codex stdout, stderr, exit code, started_at, finished_at, timeout status, and adapter result.; Define and implement structured Codex execution report intake.; Report must include task id/ref, summary, changed files, tests run, test results, risks, blockers, and next actions.; Persist accepted reports through governed task report state mutation.; Link report id to pipeline session and selected task.; Make Report Gate validate required report fields and block on missing, malformed, stale, wrong-task, or failed-test reports.; Run Machine Review Gate after Report Gate.; Run Codex Review Gate after Machine Review Gate.; If all required gates pass and owner-approved auto-close is enabled for the session, close the selected task through governed lifecycle commands.; Auto-close only tasks selected by the current pipeline session queue.; Require explicit Human Owner approval intent and note for auto-close behavior.; Do not close tasks if Codex Review requests changes, is blocked, or required evidence is missing.; Support continuing to the next selected task after the current task reaches done.; End run-until-blocker with queue_complete only after all selected tasks are done or no executable selected tasks remain.; Expose policy options in Web Control Center with clear labels: prompt-only vs executable vs auto-close vs local-commit.; Prevent misleading policy combinations such as BUILD_PROMPT_ONLY plus auto-close/local-commit.; Update CLI policy list/describe and session create options if needed.; Add deterministic end-to-end tests using a fake local Codex command.

Rationale:

Implement a real executable pipeline mode that can run selected tasks end-to-end: create/approve required Changes according to explicit owner-approved session policy, prepare Codex context, run local Codex adapter, ingest execution report, run review gates, close tasks, optionally create local commits, and continue to the next task until queue_complete or blocker.

Approved by: `human_owner` at `2026-06-20T11:29:56Z`  
Approval notes: Approve  

Accepted by: `human_owner` at `2026-06-20T11:58:32Z`  
Acceptance notes: Accept  

Affected files:

- ai_project_ctl/pipeline/policy.py
- ai_project_ctl/pipeline/runner.py
- ai_project_ctl/pipeline/batch.py
- ai_project_ctl/pipeline/codex_adapter.py
- ai_project_ctl/pipeline/report_gate.py
- ai_project_ctl/pipeline/machine_review.py
- ai_project_ctl/pipeline/codex_review.py
- ai_project_ctl/pipeline/close_policy.py
- ai_project_ctl/pipeline/git_commit.py
- ai_project_ctl/pipeline/session.py
- ai_project_ctl/pipeline/state.py
- ai_project_ctl/core/registry.py
- ai_project_ctl/core/workflows.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- scripts/aictl.py
- scripts/taskctl.py if governed report or lifecycle integration is needed
- scripts/evolutionctl.py if governed Change integration is needed
- tests/test_pipeline_runner.py
- tests/test_pipeline_batch.py
- tests/test_pipeline_codex_adapter.py
- tests/test_pipeline_report_gate.py
- tests/test_pipeline_e2e.py
- tests/test_web_control_center.py
- tests/test_aictl.py
- tests/test_registry.py
- ai-system/project-control/10-owner-quickstart.md
- ai-system/project-control/pipeline-runner.md
- AI_PROJECT/state/tasks.json via governed CLI/service only
- AI_PROJECT/events/task-events.jsonl via governed CLI/service only
- AI_PROJECT/state/evolution.json via governed CLI/service only
- AI_PROJECT/events/evolution-events.jsonl via governed CLI/service only
- AI_PROJECT/state/task_reports.json via governed CLI/service only
- AI_PROJECT/state/pipeline_sessions.json via governed CLI/service only
- AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/CODEX_TASKS.md via governed CLI/service only
- AI_PROJECT/generated/EVOLUTION_STATUS.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_AUDIT.md via governed CLI/service only

Risks:

- Boundary risk: Do not call remote APIs directly.
- Boundary risk: Do not allow unsafe shell execution.
- Boundary risk: Do not approve Evolution Changes without explicit Human Owner session approval.
- Boundary risk: Do not accept Evolution Changes automatically unless a separate owner-approved accept policy exists.
- Boundary risk: Do not bypass Token Budget Gate.
- Boundary risk: Do not bypass Report Gate.
- Boundary risk: Do not bypass Machine Review.
- Boundary risk: Do not bypass Codex Review.
- Boundary risk: Do not close tasks outside the selected session queue.
- Boundary risk: Do not push or merge.
- Boundary risk: Do not reset, rebase, clean, restore, discard, or otherwise destroy local work.
- Boundary risk: Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.
- Use a fake local Codex command in tests; do not require real Codex or network access.
- Verify old supervised prompt-only behavior still works.
- Verify new executable mode runs through adapter, report gate, machine review, Codex review, and task close.
- Verify negative paths: unsafe command, stale prompt, failed report tests, review request changes, missing owner auto-close note.
- Verify run-until-blocker can complete a two-task selected queue to done and queue_complete.
- Verify UI policy preview clearly distinguishes prompt-only and executable modes.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-076.
- Keeps Change approval as a separate explicit Human Owner action.
- Add a real executable pipeline policy mode distinct from prompt-only supervised mode.
- Add or finalize local Codex RUN_CODEX adapter support.
- Allow the pipeline to execute a configured local Codex command against AI_PROJECT/generated/CODEX_PROMPT.md.
- Require command allowlist, timeout, prompt freshness, and task identity validation.
- Capture Codex stdout, stderr, exit code, started_at, finished_at, timeout status, and adapter result.
- A new executable pipeline mode can run a selected task beyond prompt generation.
- Pipeline can invoke a safe local Codex adapter command using RUN_CODEX mode.
- Adapter refuses unsafe or non-allowlisted commands.

Linked tasks:

- TASK-076

### CHG-060 — PIPE-26 Fix Codex Adapter Prompt Transport

Status: `approved`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-26 requires an explicit Evolution Change Proposal before implementation: Fix local Codex adapter so it passes CODEX_PROMPT.md to codex exec instead of running codex exec with no input.

Proposal:

Implement the bounded task scope: Inspect ai_project_ctl/pipeline/codex_adapter.py local command execution.; Add prompt transport support for local Codex execution.; Default prompt transport should pass AI_PROJECT/generated/CODEX_PROMPT.md content to local_command stdin.; Keep command allowlist validation intact.; Keep prompt existence, prompt hash, and task identity validation intact.; Add policy/session support for prompt_transport if needed, with stdin as the default.; Optionally support future-safe modes such as file_arg or no_prompt, but only if they are explicitly tested.; Update local command execution so codex exec receives the generated prompt.; Capture a short safe stdout/stderr snippet in adapter gate details in addition to sha256 refs.; Limit captured snippets to a safe bounded size to avoid storing large logs or secrets.; Preserve existing stdout_ref/stderr_ref hash behavior.; Update report instruction if needed so Codex knows it must submit a structured execution report.; Add tests where a fake local command asserts that prompt text is received on stdin.; Add tests for non-zero exit including readable stderr snippet.; Add tests proving allowlist, timeout, stale prompt, and wrong-task prompt checks still work.; Update pipeline docs with the expected real Codex command behavior.; Allow local_command to include explicit Codex sandbox/approval flags, for example a safer owner-configured command such as codex exec --sandbox <mode> when supported by the installed Codex CLI.; Add a preflight diagnostic that detects Codex sandbox startup failures such as bubblewrap/user-namespace errors and reports them as CODEX_ADAPTER_SANDBOX_UNAVAILABLE instead of generic local_command_nonzero_exit.; Document how to verify the local Codex CLI command manually before using it in executable pipeline.; Do not hardcode danger-full-access; require owner-configured policy/command allowlist for any weaker sandbox mode.; Support owner-configured Codex sandbox mode through local_command, including commands such as codex exec -s workspace-write, codex exec -s danger-full-access, or explicitly allowed bypass mode when the environment is externally sandboxed.; Do not hardcode danger-full-access or bypass mode in the adapter; allow only owner-configured commands that are present in command_allowlist.; Default prompt transport must pass CODEX_PROMPT.md to codex exec through stdin.; Detect Codex sandbox startup failures, including bwrap, loopback, RTM_NEWADDR, Operation not permitted, user namespace, or bubblewrap errors, and report them as CODEX_ADAPTER_SANDBOX_UNAVAILABLE.; Add diagnostics that include bounded stderr/stdout snippets for failed local Codex commands without storing full prompt text.; Document manual preflight commands for local Codex execution: codex exec -s workspace-write < AI_PROJECT/generated/CODEX_PROMPT.md and codex exec -s danger-full-access < AI_PROJECT/generated/CODEX_PROMPT.md.

Rationale:

The executable pipeline currently runs local_command ['codex', 'exec'] without passing AI_PROJECT/generated/CODEX_PROMPT.md through stdin or as an argument. This causes real codex exec to exit non-zero. Add an explicit prompt transport mechanism, defaulting to stdin, and improve adapter diagnostics.

Approved by: `human_owner` at `2026-06-20T12:32:02Z`  
Approval notes: Approve  

Affected files:

- ai_project_ctl/pipeline/codex_adapter.py
- ai_project_ctl/pipeline/policy.py
- ai_project_ctl/pipeline/runner.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- scripts/aictl.py
- tests/test_pipeline_codex_adapter.py
- tests/test_pipeline_runner.py
- tests/test_pipeline_e2e.py
- tests/test_web_control_center.py
- ai-system/project-control/pipeline-runner.md
- ai-system/project-control/10-owner-quickstart.md
- AI_PROJECT/state/tasks.json via governed CLI/service only
- AI_PROJECT/events/task-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/CODEX_TASKS.md via governed CLI/service only

Risks:

- Boundary risk: Do not remove command allowlist enforcement.
- Boundary risk: Do not use shell=True.
- Boundary risk: Do not bypass Token Budget Gate.
- Boundary risk: Do not bypass Change approval gate.
- Boundary risk: Do not bypass Report Gate, Machine Review, or Codex Review.
- Boundary risk: Do not auto-close tasks in this task.
- Boundary risk: Do not create local commits in this task.
- Boundary risk: Do not push, merge, reset, rebase, clean, restore, or discard git changes.
- Boundary risk: Do not store full prompt text in pipeline state, events, generated files, or gate details.
- Boundary risk: Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.
- Reproduce the original failure: PSESS-008 failed because codex exec was launched without prompt input and returned local_command_nonzero_exit.
- Verify the fixed adapter sends CODEX_PROMPT.md to stdin.
- Verify stderr snippets are visible in gate details when command exits non-zero.
- Verify no full prompt text is stored in pipeline state or events.
- Verify executable pipeline can proceed past Codex adapter when fake command receives stdin and submits a report.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-077.
- Keeps Change approval as a separate explicit Human Owner action.
- Inspect ai_project_ctl/pipeline/codex_adapter.py local command execution.
- Add prompt transport support for local Codex execution.
- Default prompt transport should pass AI_PROJECT/generated/CODEX_PROMPT.md content to local_command stdin.
- Keep command allowlist validation intact.
- Keep prompt existence, prompt hash, and task identity validation intact.
- Local Codex adapter passes CODEX_PROMPT.md content to codex exec through stdin by default.
- The command ['codex', 'exec'] no longer runs with empty input.
- Command allowlist still validates the command before execution.

Linked tasks:

- TASK-077

### CHG-061 — PIPE-27 Add Persistent Pipeline Session Detail Page

Status: `approved`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPE-27 requires an explicit Evolution Change Proposal before implementation: Add a persistent per-session Pipeline page with real-time steps, expandable logs, session actions, artifacts, audit events, and historical availability.

Proposal:

Implement the bounded task scope: Add a persistent route for individual pipeline sessions, for example /pipeline/sessions/<SESSION_ID>.; Add links from the main Pipeline sessions table to each session detail page.; Keep session detail pages available after session completion, blocking, failure, stop, or archive.; Add a top session header with session id, status, policy, current task, current step, stop reason, started/updated/finished timestamps, elapsed time, and auto-refresh status.; Add a Status Overview section with a compact progress indicator for the full pipeline flow.; Add a Current Live Step section for running sessions.; Auto-refresh the session page every 1-2 seconds while the session is running.; Stop auto-refresh automatically when the session reaches a terminal state.; Add a Steps section that lists all pipeline steps in order.; Each step must be expandable/collapsible.; Expanded step view must show status, task id/ref, started_at, finished_at, elapsed time, stop reason, gate outcomes, linked artifacts, and logs.; Step logs must include bounded stdout/stderr snippets when available.; Show pending steps as visible placeholders, not hidden missing data.; Add an Actions section with buttons for safe session actions.; Actions section must include Refresh Session, Run Next, Run Until Blocker, Stop Session, and Resume Session when applicable.; Actions section must show owner approval actions when applicable, including approve required changes, approve auto-close, and close reviewed task.; Dangerous or restricted actions must be separated visually and require explicit confirmation.; Do not expose push, merge, reset, restore, clean, rebase, discard, or destructive git actions.; Add an Artifacts section showing linked task ids, change ids, report ids, review ids, commit ids, Context Pack path, Codex Prompt path, and generated files.; Add a Queue Snapshot section showing selected task, queue counts, skipped tasks, and skip reasons such as status_not_executable.; Add an Audit Events section with latest pipeline events related to the session.; Add a Files Changed During Session section when changed file data is available.; Add a Problems / Blockers section that clearly displays current blocker, previous blockers, and known risks.; Add Raw Debug collapsible sections for session JSON and latest gate details.; Do not render full CODEX_PROMPT.md content on the page.; Do not store or render unbounded logs.; Use bounded snippets, hashes, or safe log references for Codex adapter stdout/stderr.; Use simple polling for MVP; do not require WebSockets or SSE.; Add tests for session detail route rendering.; Add tests for links from main Pipeline page to session detail pages.; Add tests for running-session auto-refresh markup.; Add tests for completed historical session rendering.; Add tests for expandable steps and bounded log display.; Add tests for action buttons and confirmation requirements.; Document the session detail page in the owner quickstart and pipeline runner docs.

Rationale:

Create a dedicated Web Control Center page for each pipeline session, for example /pipeline/sessions/PSESS-012. The page must let the Human Owner watch a running session in real time, inspect all steps and logs, execute safe session actions, and reopen the page later as a permanent execution record.

Approved by: `human_owner` at `2026-06-20T13:06:22Z`  
Approval notes: Approve  

Affected files:

- ai_project_ctl/web/server.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/pipeline/state.py
- ai_project_ctl/pipeline/session.py
- ai_project_ctl/pipeline/audit.py
- ai_project_ctl/pipeline/codex_adapter.py
- ai_project_ctl/core/registry.py
- scripts/aictl.py
- tests/test_web_control_center.py
- tests/test_pipeline_runner.py
- tests/test_aictl.py
- ai-system/project-control/pipeline-runner.md
- ai-system/project-control/10-owner-quickstart.md
- AI_PROJECT/state/pipeline_sessions.json via governed CLI/service only
- AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_AUDIT.md via governed CLI/service only

Risks:

- Boundary risk: Do not add background autonomous execution.
- Boundary risk: Do not bypass pipeline gates.
- Boundary risk: Do not change task lifecycle rules.
- Boundary risk: Do not change queue planner semantics except for display/read-model formatting needed by this page.
- Boundary risk: Do not approve or accept Evolution Changes automatically.
- Boundary risk: Do not auto-close tasks without existing pipeline close gates and owner note.
- Boundary risk: Do not push or merge.
- Boundary risk: Do not expose full prompt text.
- Boundary risk: Do not store full stdout/stderr logs in protected state.
- Boundary risk: Do not add external frontend dependencies.
- Boundary risk: Do not require WebSockets or SSE in the MVP.
- Boundary risk: Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.
- Start a running pipeline session and open /pipeline/sessions/<SESSION_ID>.
- Verify the page updates while the session is running.
- Verify the Steps section displays all known steps and pending placeholders.
- Expand each step and verify logs/gates/details are readable.
- Verify Actions buttons appear only when applicable to the session state.
- Verify mutating Actions require confirmation.
- Verify old completed and blocked PSESS records remain viewable.
- Verify no full CODEX_PROMPT.md content appears in page HTML, state, events, or generated output.
- Verify the main Pipeline dashboard links to the session detail page.
- Run web/control-center tests and project-control validation commands.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-078.
- Keeps Change approval as a separate explicit Human Owner action.
- Add a persistent route for individual pipeline sessions, for example /pipeline/sessions/<SESSION_ID>.
- Add links from the main Pipeline sessions table to each session detail page.
- Keep session detail pages available after session completion, blocking, failure, stop, or archive.
- Add a top session header with session id, status, policy, current task, current step, stop reason, started/updated/finished timestamps, elapsed time, and auto-refresh status.
- Add a Status Overview section with a compact progress indicator for the full pipeline flow.
- Each pipeline session has a stable URL such as /pipeline/sessions/PSESS-012.
- The main Pipeline page links each session id to its detail page.
- The session detail page remains available after the session completes, blocks, fails, stops, or is archived.

Linked tasks:

- TASK-078

### CHG-062 — Compact codexctl execute prompt renderer

Status: `in_review`  
Type: `prompt`  
Priority: `1`  
Backward compatibility: `compatible`  
Migration required: `false`  

Problem:

codexctl.py currently renders runtime CODEX_PROMPT.md as a documentation-heavy prompt that can embed full Context Pack content and prompt-authoring explanations instead of a compact execution contract.

Proposal:

Update codexctl.py prompt rendering so CODEX_PROMPT.md uses the execute-profile MVP shape: Profile: execute, task identity, role, objective, task input, full scope, out-of-scope, allowed files, full acceptance criteria, compact verification text, manifest-only Context section, compact execution rules, missing-info policy, and final report format. Omit Execution Steps and full Context Pack body. Add or update tests proving compact context rendering.

Rationale:

The attached Codex execution request asks for compact runtime prompt generation so Codex receives a bounded execution contract instead of a long documentation dump.

Approved by: `human_owner` at `2026-06-20T15:44:09Z`  
Approval notes: Approved  

Affected files:

- scripts/codexctl.py
- tests/test_legacy_ctl_wrappers.py

Risks:

- Boundary risk: Prompt rendering must not embed the full AI_PROJECT/generated/CONTEXT_PACK.md body into CODEX_PROMPT.md.
- Boundary risk: Do not implement --profile, profile-specific role switching, task schema changes, execution_steps, verification_checks, or task splitting in this change.
- Boundary risk: Do not manually edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**; generated prompt/status output must be produced only through the owning CLI.

Impact:

- Creates a compact execute-profile runtime prompt shape for codexctl.py while keeping profile support postponed.
- CODEX_PROMPT.md with context should keep only Context Pack path, hash, docs/tasks revisions, and selected source refs; it should not render Retrieved Context Pack Content.

Linked tasks:

- TASK-079

### CHG-063 — PIPEF-40 Add tests for phase model and mutations

Status: `approved`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Pipeline phase model and mutation behavior require regression coverage before automated execution.

Proposal:

Add tests for phase model and pipeline mutation behavior required by PIPEF-40.

Rationale:

Execution policy requires an approved linked Evolution Change before Codex implementation.

Approved by: `human_owner` at `2026-06-22T14:10:56Z`  
Approval notes: Approved for PIPEF-40 execution.  

### CHG-064 — PIPE-040 Add tests for phase model and mutations

Status: `approved`  
Type: `process`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPEF-40 requires an explicit Evolution Change Proposal before implementation: Add tests for PhaseResult serialization, session phase fields, and governed phase mutation helpers.

Proposal:

Implement the bounded task scope: Test PhaseResult construction and JSON conversion.; Test session creation with phase field defaults.; Test start_phase and record_phase_result mutations.; Test validation behavior for legacy sessions without phase fields.

Rationale:

Protect the foundational phase state behavior before rewriting the runner.

Approved by: `human_owner` at `2026-06-23T14:34:11Z`  
Approval notes: Approve  

Affected files:

- tests/test_pipeline_phase.py
- tests/test_pipeline_session_phase.py

Risks:

- Boundary risk: Do not change behavior unrelated to this task.
- Boundary risk: Do not refactor unrelated code.
- Boundary risk: Do not edit protected project-control files manually.
- Check tests use temporary state and do not depend on local repository state.
- Verify tests do not require external Codex or network access.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-119.
- Keeps Change approval as a separate explicit Human Owner action.
- Test PhaseResult construction and JSON conversion.
- Test session creation with phase field defaults.
- Test start_phase and record_phase_result mutations.
- Test validation behavior for legacy sessions without phase fields.
- Tests pass for all PhaseResult statuses.
- Tests prove legacy pipeline sessions remain valid.
- Tests prove phase results append to phase_history.

Linked tasks:

- TASK-119

### CHG-065 — PIPE-051 Document phase-based Web Pipeline display behavior

Status: `ready`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPEF-56 requires an explicit Evolution Change Proposal before implementation: Document how the Web Control Center displays phase-based pipeline sessions and timeout settings.

Proposal:

Implement the bounded task scope: Document that Web Pipeline UI uses phase_history for phase-based sessions.; Document the legacy steps and gate_outcomes fallback for older sessions.; Document command_line, preflight_timeout_sec and execution_timeout_sec UI settings.; Add troubleshooting notes for CODEX_ADAPTER_TIMEOUT and missing report evidence.

Rationale:

Owner-facing documentation should explain phase_history display, legacy fallback and UI timeout configuration.

Affected files:

- ai-system/project-control/08-usage-guide.md
- ai-system/project-control/10-owner-quickstart.md

Risks:

- Boundary risk: Do not change generated documentation manually.
- Boundary risk: Do not document unimplemented automation behavior as available.
- Boundary risk: Do not change pipeline code in this documentation task.
- Verify that the docs do not overstate automation maturity.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-135.
- Keeps Change approval as a separate explicit Human Owner action.
- Document that Web Pipeline UI uses phase_history for phase-based sessions.
- Document the legacy steps and gate_outcomes fallback for older sessions.
- Document command_line, preflight_timeout_sec and execution_timeout_sec UI settings.
- Add troubleshooting notes for CODEX_ADAPTER_TIMEOUT and missing report evidence.
- Documentation explains phase_history-based Web Pipeline rendering.
- Documentation explains the difference between command_line and policy local_command.
- Documentation explains preflight timeout versus execution timeout.

Linked tasks:

- TASK-135

### CHG-066 — PIPE-051 Document phase-based Web Pipeline display behavior

Status: `approved`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPEF-56 requires an explicit Evolution Change Proposal before implementation: Document how the Web Control Center displays phase-based pipeline sessions and timeout settings.

Proposal:

Implement the bounded task scope: Document that Web Pipeline UI uses phase_history for phase-based sessions.; Document the legacy steps and gate_outcomes fallback for older sessions.; Document command_line, preflight_timeout_sec and execution_timeout_sec UI settings.; Add troubleshooting notes for CODEX_ADAPTER_TIMEOUT and missing report evidence.

Rationale:

Owner-facing documentation should explain phase_history display, legacy fallback and UI timeout configuration.

Approved by: `human_owner` at `2026-06-24T09:02:41Z`  
Approval notes: Approve  

Affected files:

- ai-system/project-control/08-usage-guide.md
- ai-system/project-control/10-owner-quickstart.md

Risks:

- Boundary risk: Do not change generated documentation manually.
- Boundary risk: Do not document unimplemented automation behavior as available.
- Boundary risk: Do not change pipeline code in this documentation task.
- Verify that the docs do not overstate automation maturity.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-135.
- Keeps Change approval as a separate explicit Human Owner action.
- Document that Web Pipeline UI uses phase_history for phase-based sessions.
- Document the legacy steps and gate_outcomes fallback for older sessions.
- Document command_line, preflight_timeout_sec and execution_timeout_sec UI settings.
- Add troubleshooting notes for CODEX_ADAPTER_TIMEOUT and missing report evidence.
- Documentation explains phase_history-based Web Pipeline rendering.
- Documentation explains the difference between command_line and policy local_command.
- Documentation explains preflight timeout versus execution timeout.

Linked tasks:

- TASK-135

### CHG-067 — PIPE-062 Add confirmed Web actions for UI settings updates

Status: `approved`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPEF-67 requires an explicit Evolution Change Proposal before implementation: Add confirmed Web actions that update allowed project-local UI settings from the Settings page.

Proposal:

Implement the bounded task scope: Add Web actions for updating explicitly allowed UI settings keys.; Require confirmation before writing AI_PROJECT/config/ui_settings.json.; Reuse existing UI settings load and upsert behavior where possible.; Return action results that show changed key, new value and settings file path.

Rationale:

This lets the Human Owner change supported UI settings without running terminal commands.

Approved by: `human_owner` at `2026-06-24T11:28:53Z`  
Approval notes: Approve  

Affected files:

- ai_project_ctl/web/actions.py
- ai_project_ctl/web/server.py
- tests/test_web_control_center.py

Risks:

- Boundary risk: Do not allow arbitrary file writes.
- Boundary risk: Do not allow editing settings outside AI_PROJECT/config/ui_settings.json.
- Boundary risk: Do not add the internal change-gate bypass checkbox in this task.
- Verify that arbitrary setting keys are not accepted through Web actions unless intentionally allowed.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-146.
- Keeps Change approval as a separate explicit Human Owner action.
- Add Web actions for updating explicitly allowed UI settings keys.
- Require confirmation before writing AI_PROJECT/config/ui_settings.json.
- Reuse existing UI settings load and upsert behavior where possible.
- Return action results that show changed key, new value and settings file path.
- Settings update actions require explicit confirmation.
- Only allowlisted setting keys can be updated through the Web UI.
- Successful updates write AI_PROJECT/config/ui_settings.json.

Linked tasks:

- TASK-146

### CHG-068 — PIPE-063 Add internal change-gate bypass UI setting

Status: `approved`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPEF-68 requires an explicit Evolution Change Proposal before implementation: Add a disabled-by-default UI setting for explicitly bypassing approved Change requirements on internal project-control tasks.

Proposal:

Implement the bounded task scope: Add a default false setting for internal project-control Change gate bypass.; Parse boolean string values safely for the new setting.; Expose the setting through effective UI settings output.; Add tests for default, true, false and invalid values.

Rationale:

This introduces the setting data contract without yet changing pipeline execution behavior.

Approved by: `human_owner` at `2026-06-24T11:29:03Z`  
Approval notes: Approve  

Affected files:

- ai_project_ctl/ui_settings.py
- tests/test_ui_settings.py

Risks:

- Boundary risk: Do not bypass the Change gate in this task.
- Boundary risk: Do not change built-in pipeline policy presets.
- Boundary risk: Do not enable the setting by default.
- Verify that this task adds only configuration support and does not weaken execution gates.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-147.
- Keeps Change approval as a separate explicit Human Owner action.
- Add a default false setting for internal project-control Change gate bypass.
- Parse boolean string values safely for the new setting.
- Expose the setting through effective UI settings output.
- Add tests for default, true, false and invalid values.
- Effective UI settings include the new bypass setting with default false.
- String values such as true, false, 1 and 0 are parsed predictably.
- Invalid boolean values produce a stable settings error or validation failure.

Linked tasks:

- TASK-147

### CHG-069 — PIPE-064 Render internal Change gate bypass checkbox

Status: `approved`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPEF-69 requires an explicit Evolution Change Proposal before implementation: Render a confirmed Settings page checkbox for toggling internal project-control Change gate bypass.

Proposal:

Implement the bounded task scope: Add a checkbox control for the internal Change gate bypass setting.; Make the checkbox submit through the confirmed UI settings Web action.; Show a warning that the bypass is for internal project-control tasks only.; Add tests for checked, unchecked and warning text rendering.

Rationale:

The Human Owner should be able to enable or disable the bypass setting from the Web Settings page.

Approved by: `human_owner` at `2026-06-24T11:46:50Z`  
Approval notes: Approve  

Affected files:

- ai_project_ctl/web/server.py
- tests/test_web_control_center.py

Risks:

- Boundary risk: Do not implement bypass execution semantics in this task.
- Boundary risk: Do not enable bypass automatically.
- Boundary risk: Do not hide existing Change approval actions.
- Verify that the warning text is visible near the checkbox.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-148.
- Keeps Change approval as a separate explicit Human Owner action.
- Add a checkbox control for the internal Change gate bypass setting.
- Make the checkbox submit through the confirmed UI settings Web action.
- Show a warning that the bypass is for internal project-control tasks only.
- Add tests for checked, unchecked and warning text rendering.
- The Settings page shows a checkbox for the internal Change gate bypass setting.
- The checkbox reflects the effective current setting value.
- Submitting the checkbox requires confirmation.

Linked tasks:

- TASK-148

### CHG-070 — PIPE-065 Apply internal Change gate bypass to UI runs

Status: `approved`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPEF-70 requires an explicit Evolution Change Proposal before implementation: Allow confirmed UI runs to skip approved Change requirements only for internal project-control tasks when the bypass setting is enabled.

Proposal:

Implement the bounded task scope: Define an internal project-control task predicate for safe bypass eligibility.; Apply the bypass only to UI-created single-task sessions when the setting is enabled.; Record explicit phase artifacts or audit details when the Change gate is bypassed.; Keep approved Change requirements unchanged for non-internal tasks and non-UI execution paths.

Rationale:

This implements the actual execution behavior behind the Settings checkbox with strict safety boundaries and audit evidence.

Approved by: `human_owner` at `2026-06-24T11:47:00Z`  
Approval notes: Approve  

Affected files:

- ai_project_ctl/pipeline/prepare_phase.py
- ai_project_ctl/pipeline/runner.py
- ai_project_ctl/pipeline/ui_policy.py
- scripts/aictl.py
- tests/pipeline/test_prepare_phase.py
- tests/test_ui_run_command.py

Risks:

- Boundary risk: Do not disable the Change gate globally.
- Boundary risk: Do not bypass token, report, verify, review, close or commit gates.
- Boundary risk: Do not auto-approve or auto-create Evolution Changes.
- Review the internal-task predicate carefully to avoid allowing product-code tasks through the bypass.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-149.
- Keeps Change approval as a separate explicit Human Owner action.
- Define an internal project-control task predicate for safe bypass eligibility.
- Apply the bypass only to UI-created single-task sessions when the setting is enabled.
- Record explicit phase artifacts or audit details when the Change gate is bypassed.
- Keep approved Change requirements unchanged for non-internal tasks and non-UI execution paths.
- When the setting is disabled, UI runs still require an approved linked Change.
- When the setting is enabled, eligible internal project-control tasks can pass prepare without an approved linked Change.
- Non-internal tasks still block on missing approved Change even when the setting is enabled.

Linked tasks:

- TASK-149

### CHG-071 — PIPE-074 Allow internal bypass setting in Web settings action

Status: `approved`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPEF-79 requires an explicit Evolution Change Proposal before implementation: Allow the Web UI settings action to update the existing internal Change gate bypass setting.

Proposal:

Implement the bounded task scope: Import or reference the existing internal Change gate bypass setting constant in the Web actions module.; Add allow_internal_change_gate_bypass to the Web UI settings update allowlist.; Ensure ui.settings.set accepts true and false values for the bypass setting through the Web action.; Add focused tests for allowed bypass setting updates and continued rejection of unknown setting keys.

Rationale:

Fix the WEB_UI_SETTING_KEY_NOT_ALLOWED error for allow_internal_change_gate_bypass by adding the existing setting to the Web settings update allowlist.

Approved by: `human_owner` at `2026-06-24T14:08:57Z`  
Approval notes: Approve  

Affected files:

- ai_project_ctl/web/actions.py
- tests/test_web_control_center.py

Risks:

- Boundary risk: Do not implement the actual Change gate bypass execution semantics.
- Boundary risk: Do not change UI settings boolean parsing rules.
- Boundary risk: Do not weaken the Web action allowlist for arbitrary settings.
- Boundary risk: Do not change pipeline policy presets.
- Verify that the fix only expands the allowlist by the one existing setting and does not allow arbitrary settings writes.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-158.
- Keeps Change approval as a separate explicit Human Owner action.
- Import or reference the existing internal Change gate bypass setting constant in the Web actions module.
- Add allow_internal_change_gate_bypass to the Web UI settings update allowlist.
- Ensure ui.settings.set accepts true and false values for the bypass setting through the Web action.
- Add focused tests for allowed bypass setting updates and continued rejection of unknown setting keys.
- The Web settings action no longer rejects allow_internal_change_gate_bypass with WEB_UI_SETTING_KEY_NOT_ALLOWED.
- The Web settings action can persist allow_internal_change_gate_bypass=true.
- The Web settings action can persist allow_internal_change_gate_bypass=false.

Linked tasks:

- TASK-158

### CHG-072 — PIPE-067 Add structured Codex report block to prompt package

Status: `approved`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPEF-72 requires an explicit Evolution Change Proposal before implementation: Update Codex prompt generation so executors must finish with a machine-readable structured report block.

Proposal:

Implement the bounded task scope: Replace the plain bullet-only Final Report prompt section with a structured report contract.; Define a fenced JSON block marker that Codex must emit at the end of execution.; Include required report fields used by task report submission, including token_usage.; Add focused tests or assertions for generated prompt report instructions.

Rationale:

The prompt should still be readable by humans, but it must include a deterministic JSON report contract that the pipeline adapter can parse.

Approved by: `human_owner` at `2026-06-24T15:04:42Z`  
Approval notes: Approve  

Affected files:

- scripts/codexctl.py
- tests/test_codex_prompt_report_contract.py

Risks:

- Boundary risk: Do not implement stdout parsing in this task.
- Boundary risk: Do not submit reports automatically in this task.
- Boundary risk: Do not change task report validation rules.
- Verify that the prompt contract is deterministic enough for a parser and does not ask Codex to edit AI_PROJECT state directly.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-151.
- Keeps Change approval as a separate explicit Human Owner action.
- Replace the plain bullet-only Final Report prompt section with a structured report contract.
- Define a fenced JSON block marker that Codex must emit at the end of execution.
- Include required report fields used by task report submission, including token_usage.
- Add focused tests or assertions for generated prompt report instructions.
- Generated CODEX_PROMPT.md contains a clearly delimited machine-readable report JSON instruction.
- The required JSON fields include task identity, changed_files, generated_files, checks, warnings, blockers and token_usage.
- The prompt still tells Codex not to self-approve.

Linked tasks:

- TASK-151

### CHG-073 — PIPE-059 Keep runtime pipeline logs out of task diff gates

Status: `approved`  
Type: `tooling`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPEF-64 requires an explicit Evolution Change Proposal before implementation: Ensure runtime UI and pipeline log files do not cause task verification diff gates to fail.

Proposal:

Implement the bounded task scope: Review where UI run logs and pipeline runtime logs are written.; Ensure runtime log paths are ignored by Git or excluded from diff gate comparison.; Add tests for diff gate behavior with runtime log files present.; Document the chosen runtime log path in a code comment or focused note.

Rationale:

Runtime logs and local UI run artifacts should not be counted as implementation changes for a task.

Approved by: `human_owner` at `2026-06-25T08:38:45Z`  
Approval notes: Auto-approved by Human Owner for selected UI run (pipeline session PSESS-032)  

Affected files:

- .gitignore
- ai_project_ctl/pipeline/verify_phase.py
- ai_project_ctl/pipeline/diff_gate.py
- tests/pipeline/test_verify_phase.py

Risks:

- Boundary risk: Do not ignore source files, tests or project-control state files.
- Boundary risk: Do not weaken diff gate checks for real task implementation files.
- Boundary risk: Do not delete existing owner logs.
- Verify that this does not hide AI_PROJECT/state changes unintentionally.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-143.
- Keeps Change approval as a separate explicit Human Owner action.
- Review where UI run logs and pipeline runtime logs are written.
- Ensure runtime log paths are ignored by Git or excluded from diff gate comparison.
- Add tests for diff gate behavior with runtime log files present.
- Document the chosen runtime log path in a code comment or focused note.
- Runtime log files under the chosen logs path do not appear as missing_from_report.
- Real source, test and documentation changes still require report coverage.
- Git ignore rules cover generated runtime log artifacts where appropriate.

Linked tasks:

- TASK-143

### CHG-074 — PIPE-045 Update phase pipeline usage guide

Status: `accepted`  
Type: `docs`  
Priority: `1`  
Backward compatibility: `unknown`  
Migration required: `false`  

Problem:

Task PIPEF-45 requires an explicit Evolution Change Proposal before implementation: Add user-facing documentation for the phase-based pipeline commands, outcomes, and common blocked states.

Proposal:

Implement the bounded task scope: Document the phase command sequence from queue preview to close.; Document passed, blocked, failed, and skipped outcomes.; Document manual handoff, missing report, review request changes, and CI exit-code behavior.; Add a compact quickstart with exact aictl commands.

Rationale:

Make the new pipeline usable without reading implementation code.

Approved by: `human_owner` at `2026-06-26T09:01:20Z`  
Approval notes: Auto-approved by Human Owner for selected UI run (pipeline session PSESS-061)  

Accepted by: `human_owner` at `2026-06-26T12:47:54Z`  
Acceptance notes: Approve; linked Change accepted after task TASK-124 close succeeded.  

Affected files:

- ai-system/pipeline-phase-usage.md
- ai-system/README.md

Risks:

- Boundary risk: Do not change behavior unrelated to this task.
- Boundary risk: Do not refactor unrelated code.
- Boundary risk: Do not edit protected project-control files manually.
- Check that documentation does not claim fully autonomous execution where manual gates remain required.
- Verify command examples match actual CLI names.
- Generated Change Proposal fields may need Human Owner review before approval.
- Workflow must delegate all protected project-control mutations to evolutionctl.py.

Impact:

- Creates an Evolution Change Proposal linked to task TASK-124.
- Keeps Change approval as a separate explicit Human Owner action.
- Document the phase command sequence from queue preview to close.
- Document passed, blocked, failed, and skipped outcomes.
- Document manual handoff, missing report, review request changes, and CI exit-code behavior.
- Add a compact quickstart with exact aictl commands.
- The guide shows the command sequence: queue preview, prepare, execute, collect-report, verify, review, close.
- The guide explains blocked outcomes as normal owner-action states.
- The guide documents CI exit codes for passed, blocked, and failed outcomes.

Linked tasks:

- TASK-124

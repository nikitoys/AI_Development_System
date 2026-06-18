<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/evolution.json -->

# AI Development System Evolution

Revision: `278`
Changes: `13`

## Summary

- `accepted`: 12
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

<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Project Tasks

Revision: `424`
Current task: `none`

## Epic `EPIC-001`

### TASK-001 — Write Project Control Usage Guide

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_0c39847a282c`, legacy `TASK-001`, aliases `TASK-001`

Write the missing practical usage guide for the Project Control Gateway.

Acceptance criteria:

- 08-usage-guide.md exists and uses the same practical style as neighboring project-control documents.
- The guide explains role interactions, CLI responsibilities, daily workflow, documentation workflow, protected-file boundaries, troubleshooting, and validation.
- Only supported CLI commands are shown as exact command examples.
- The document is registered through docctl.py and moved no further than review without Human Owner acceptance.
- Plan, task, documentation, smoke, and protected-files validation commands pass.

### TASK-004 — Implement codexctl prompt package generator

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_04d7aa259713`, legacy `TASK-004`, aliases `TASK-004`

Implement approved CHG-001 by adding a dedicated Codex prompt package control CLI.

Acceptance criteria:

- scripts/codexctl.py exists and uses only Python standard library.
- status works without crashing and reports READY or BLOCKED state with stable codes.
- build --task can generate CODEX_PROMPT.md for an executable task and fails clearly for invalid task IDs or statuses.
- build --change can generate CODEX_PROMPT.md for approved CHG-001 and fails clearly for invalid change IDs or statuses.
- clear invalidates or removes the current Codex prompt package without modifying source-of-truth task or evolution state.
- Required validation commands from the owner prompt pass or any blocker is reported clearly.

### TASK-007 — Record L4 Role-Agent Runtime Architecture

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_5b19d4868c96`, legacy `TASK-007`, aliases `TASK-007`

Implement approved CHG-004 by creating the L4 Role-Agent Runtime Architecture source document and updating required README, operating model, roadmap, backlog and changelog references.

Acceptance criteria:

- ai-system/l4-role-agent-runtime.md exists and states L4 is an approved bounded implementation target.
- Document defines Python as strict API/control kernel, Controller Codex as planner/router/delegator/integrator and Codex role subagents as bounded role executors.
- Document maps existing role layers to concrete role-agent IDs.
- Document defines L4 execution flow from approved Task to Human Owner acceptance and conceptual scripts/agentctl.py API surface without implementing it.
- Document distinguishes L3, L4 and L5 and forbids automatic merge, push, PR creation, final acceptance and QA/review closure.
- Operating model, roadmap, backlog, changelog and README/index references are updated.
- Required validation passes and protected AI_PROJECT files are not manually edited.

### TASK-018 — Fix documentation generated drift

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_9ecaaf287358`, legacy `TASK-018`, aliases `TASK-018`

Resolve pre-existing DOCS_GAPS.md generated drift through docctl.py so protected-files validation becomes clean again.

Acceptance criteria:

- python scripts/docctl.py validate passes.
- python scripts/docctl.py render completes successfully.
- python scripts/docctl.py check-generated passes.
- python scripts/check-protected-project-files.py --verbose no longer reports DOCS_GAPS.md drift.
- No protected AI_PROJECT files are manually edited.

## Epic `EPIC-002`

### TASK-002 — Document Skills Layer Roadmap

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_6aa950ac6a24`, legacy `TASK-002`, aliases `TASK-002`

Create a controlled skills layer documentation page that records useful project skills/plugins and recommends next skills to create.

Acceptance criteria:

- ai-system/skills/README.md exists and covers skills/plugins as guidance and routing helpers, not authoritative source documents.
- The document clearly states that Python CLIs and registered source documents remain the source of truth.
- The document lists the two existing useful skills and the eight recommended future skills with purpose, related CLI, priority, allowed actions, and forbidden actions.
- The document includes a recommended skill creation order.
- The document states that every new skill must be created through a controlled Task.
- The document states that subagents may use skills only as guidance and must still obey CLI/source-of-truth rules.
- The document is registered through docctl.py as draft or review, not active.
- Plan, task, documentation, smoke doc-control, and protected-files validation commands pass.

### TASK-003 — Create Clarification Gate Skill

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_2453027a75a4`, legacy `TASK-003`, aliases `TASK-003`

Create a high-priority Clarification Gate Skill for Codex and subagents, defining when to ask the Human Owner versus inspect or proceed with safe assumptions.

Acceptance criteria:

- Skill explains that it prevents premature execution on ambiguous or unsafe requests.
- Skill states the core rule: inspect first, ask only when blocked.
- Skill defines when to ask before task creation, during task execution, and when not to ask.
- Skill includes critical blocker, non-critical ambiguity, and inspectable ambiguity severity model with examples.
- Skill includes a question budget and forbids using clarification questions to avoid normal inspection.
- Skills README recommends the Clarification Gate Skill as high priority if the README exists.
- Required validation commands complete or any blocker is reported.

### TASK-005 — Create Documentation Navigation Skill

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_0b7a2076f7e5`, legacy `TASK-005`, aliases `TASK-005`

Create a guidance-only Documentation Navigation Skill that routes agents to minimal source documents for AI_Development_System work.

Acceptance criteria:

- .agents/skills/documentation-navigation/SKILL.md exists.
- The skill clearly explains source-of-truth hierarchy and distinguishes /ai-system, root /AI_PROJECT, templates and golden example.
- The skill provides minimal read sets by request type and says to read minimal first, expanding only when needed.
- The skill says generated Markdown is readable output, not editable source, and protected AI_PROJECT files are CLI-controlled only.
- The skill references codexctl.py for Codex prompt package state.
- ai-system/skills/README.md lists the new skill with purpose, priority, allowed actions and forbidden actions.
- The skill does not authorize runtime behavior; current maturity remains L3, runtime remains DEFERRED and L4+ remains future/not approved.
- No protected AI_PROJECT files are manually edited and required validation commands pass.

### TASK-006 — Add Two-Level Delegated Agent Execution

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_534107e45648`, legacy `TASK-006`, aliases `TASK-006`

Create L3 manual-only Controller Codex to Worker Agent delegation guidance, source documentation and reusable worker prompt template.

Acceptance criteria:

- Agent Delegation Skill exists and states it is guidance only.
- ai-system/agent-delegation.md exists and defines Two-Level Delegated Agent Execution as L3 manual delegation only.
- Worker Agent Prompt Package template exists and includes minimal read set, scope, allowed files, forbidden actions, verification, result format and return instructions.
- Documentation states Human Owner/operator manually launches Worker Agent sessions and Controller Codex does not automatically launch agents.
- Documentation states Worker Agent must not edit protected AI_PROJECT files manually or approve, accept, merge, push, open PRs or close QA/review.
- Documentation Navigation Skill, Agent Result Intake and Integration Review relationships are clear.
- Current maturity remains L3, runtime remains DEFERRED and L4+ remains future/not approved.
- Required validation commands pass and no protected AI_PROJECT files are manually edited.

## Epic `EPIC-003`

### TASK-008 — P0 Strengthen docctl metadata and documentation gaps

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_6cfac5a41fe8`, legacy `TASK-008`, aliases `TASK-008`

Improve docctl.py so registered documentation becomes a reliable source for future context retrieval.

Acceptance criteria:

- docctl validation detects mismatch between registry status and declared document status/frontmatter when such status is present.
- docctl tracks current document content hash.
- docctl mark-reviewed records the reviewed content hash.
- DOCS_GAPS.md distinguishes at least: missing file, status mismatch, active not reviewed, active review stale, unresolved placeholder, broken local link, stale index or equivalent actionable categories.
- docctl can register or account for root-level documents and skills without treating generated files as authoritative source docs.
- Existing generated documentation outputs are regenerated only through docctl.py.
- Existing plan/task/documentation validation passes or blockers are reported clearly.
- No protected project-control files are edited manually.

### TASK-009 — P1 Implement contextctl deterministic retrieval MVP

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_6fdf835d7ea2`, legacy `TASK-009`, aliases `TASK-009`

Create a new controlled CLI gateway that builds deterministic Context Packs from registered documents without vector search.

Acceptance criteria:

- contextctl.py uses only Python standard library.
- contextctl can build or refresh a deterministic derived index.
- contextctl can search registered source docs by query.
- contextctl can build a Context Pack for a task ID or explicit query.
- Context Pack includes selected documents/sections, reasons, hashes and source metadata.
- Context Pack excludes generated files and inactive/archived docs by default.
- Context Pack clearly states that it is generated output and not source of truth.
- check-generated or equivalent detects stale generated context output.
- Validation/smoke commands pass or blockers are reported.

### TASK-010 — P2 Integrate Context Pack into codexctl prompt generation

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_5640129358e6`, legacy `TASK-010`, aliases `TASK-010`

Allow codexctl.py to include a validated Context Pack in generated Codex prompt packages.

Acceptance criteria:

- codexctl can build a prompt package with an explicit context pack.
- codexctl fails clearly if the context pack is missing, stale or invalid.
- Generated CODEX_PROMPT.md records context pack path/hash and source metadata.
- Prompt explicitly states that retrieved context is read-only.
- Prompt explicitly states that context does not expand allowed files, scope or acceptance criteria.
- codexctl remains able to build prompts without context pack when requested.
- Required validation/smoke commands pass or blockers are reported.

### TASK-011 — P3 Add optional vector backend for contextctl

Status: `planned`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_ef81f7279309`, legacy `TASK-011`, aliases `TASK-011`

Add optional vector or hybrid retrieval backend after deterministic retrieval exists.

Acceptance criteria:

- Keyword backend remains default and works without optional dependencies.
- Vector backend is opt-in.
- External embeddings are disabled by default.
- Vector index stores source path, heading, chunk hash, content hash and embedding metadata.
- Stale vector chunks are detected when source content changes.
- Vector backend is documented as derived cache, not source of truth.
- Validation passes in environments without vector dependencies.
- Required smoke checks pass or blockers are reported.

## Epic `EPIC-004`

### TIG-01 (TASK-012) — TIG-01 Document task identity and execution graph design

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_4e8cdf2de480`, legacy `TASK-012`, aliases `TASK-012`, local `TIG` / `1`

Define the target model for task uid, human ref, legacy aliases, epic keys, dependency graph, executable queue, and migration rules before implementation.

Acceptance criteria:

- A clear source-of-truth design exists.
- The design states that task IDs do not imply execution order.
- The design states that epics may execute in parallel by default.
- The design defines explicit dependencies as the only cross-epic ordering mechanism.
- The design includes migration rules for existing TASK-XXX tasks.
- Generated project-control files are refreshed through CLI.

### TIG-02 (TASK-013) — TIG-02 Add epic keys to plan model

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_3a7566ad482d`, legacy `TASK-013`, aliases `TASK-013`, local `TIG` / `2`

Add stable short epic keys to the plan model so task refs can use readable prefixes such as TIG-01 or ACP-02.

Acceptance criteria:

- Existing plan validation still passes.
- Existing epics without keys are handled safely or migrated according to the design.
- New epics can have unique keys.
- Duplicate keys are rejected.

### TIG-03 (TASK-014) — TIG-03 Add task uid ref local sequence and aliases

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_51b56af6562d`, legacy `TASK-014`, aliases `TASK-014`, local `TIG` / `3`

Extend task state with stable uid, human-readable ref, local sequence inside epic, and aliases for backward compatibility.

Acceptance criteria:

- Existing tasks can be migrated or read without losing history.
- New tasks receive readable refs.
- Legacy TASK-XXX references remain resolvable.

### TIG-04 (TASK-015) — TIG-04 Add task reference resolver

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_b9599c96de80`, legacy `TASK-015`, aliases `TASK-015`, local `TIG` / `4`

Allow taskctl and prompt generation to resolve tasks by new ref, uid, or legacy TASK-XXX alias.

Acceptance criteria:

- Existing CLI commands keep working with legacy TASK-XXX.
- New refs work where task_id was previously required.
- Ambiguous references produce a clear error.

### TIG-05 (TASK-016) — TIG-05 Add task dependencies and executable queue

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_30c62f5c7e30`, legacy `TASK-016`, aliases `TASK-016`, local `TIG` / `5`

Add explicit cross-epic task dependencies and a deterministic executable queue so parallel epics can be scheduled safely.

Acceptance criteria:

- Ready tasks blocked by dependencies are not reported as executable.
- Cross-epic dependencies are supported.
- Cycles are rejected.
- Executable queue output is deterministic.

### TIG-06 (TASK-017) — TIG-06 Add migration and generated output update

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_d9383d8b8e57`, legacy `TASK-017`, aliases `TASK-017`, local `TIG` / `6`

Provide safe migration/backward compatibility for existing plan and task state and update generated outputs to display readable refs.

Acceptance criteria:

- Existing AI_PROJECT/state can be validated after migration.
- Generated files display readable refs and legacy IDs where useful.
- Prompt packages still contain enough identity data for Codex execution.
- Validation and generated checks pass.

## Epic `EPIC-005`

### CTL-01 (TASK-019) — Task A - Inventory existing ctl commands and state mutation paths

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_d0e6e78d3c7c`, legacy `TASK-019`, aliases `TASK-019`, local `CTL` / `1`

Map current ctl scripts, commands, state files, event logs, generated outputs, and direct mutation risks.

Acceptance criteria:

- Existing ctl surface is documented.
- Write paths are known.
- Gaps and unsafe paths are listed.
- No code behavior changed.

### CTL-02 (TASK-020) — Task B - Design unified control-plane architecture

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_49ec70a8f36e`, legacy `TASK-020`, aliases `TASK-020`, local `CTL` / `2`

Record the target architecture for a shared command/service layer before implementation.

Acceptance criteria:

- Architecture is recorded in the plan/task description or an approved design artifact.
- Design explicitly states that Web UI cannot bypass the command layer.
- Design explicitly states generated/*.md is derived and must not be edited manually.
- No implementation files are created in this design task.

### CTL-03 (TASK-021) — Task C - Add global ID allocation strategy

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_c04df4f0310f`, legacy `TASK-021`, aliases `TASK-021`, local `CTL` / `3`

Define a global ID allocation model that prevents task conflicts across parallel epics and future web actions.

Acceptance criteria:

- The plan explicitly resolves cross-epic task ID collision risk.
- There is a clear future implementation path for ids.py or equivalent.
- Parallel execution risk is accounted for.
- No ID migration or code behavior change is performed in this design task.

### CTL-04 (TASK-022) — Task D - Introduce ai_project_ctl core package

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_568bca24b2ff`, legacy `TASK-022`, aliases `TASK-022`, local `CTL` / `4`

Create shared internal services that future CLI and Web UI both use.

Acceptance criteria:

- Existing behavior remains compatible.
- Core package has tests.
- No domain command should need to write state directly after migration path is established.
- State mutation still goes through validated CLI/service paths.

### CTL-05 (TASK-023) — Task E - Add command registry

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_05b8a81cf8cd`, legacy `TASK-023`, aliases `TASK-023`, local `CTL` / `5`

Make project-control operations discoverable and callable through one registry.

Acceptance criteria:

- Commands have names, descriptions, args schema, read/write metadata, and output format metadata.
- CLI can list and describe commands.
- Web UI can later use the registry to render actions/forms.
- Registry does not bypass domain validation.

### CTL-06 (TASK-024) — Task F - Implement unified CLI facade scripts/aictl.py

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_fc72e08b34f0`, legacy `TASK-024`, aliases `TASK-024`, local `CTL` / `6`

Create one preferred entrypoint for project-control operations.

Acceptance criteria:

- aictl can call shared domain services.
- aictl supports human-readable output.
- aictl supports --json for automation.
- Existing taskctl/evolutionctl behavior is not broken.

### CTL-07 (TASK-025) — Task G - Convert old ctl scripts into compatibility wrappers

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_020a6425c9e0`, legacy `TASK-025`, aliases `TASK-025`, local `CTL` / `7`

Keep existing ctl workflows working while centralizing logic.

Acceptance criteria:

- Existing commands still work.
- New code path is centralized.
- No duplicate lifecycle validation remains where avoidable.
- Wrapper compatibility is documented or obvious from implementation.

### CTL-08 (TASK-026) — Task H - Add project doctor command

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_5868b6f775a8`, legacy `TASK-026`, aliases `TASK-026`, local `CTL` / `8`

Provide one health check for project-control state.

Acceptance criteria:

- python scripts/aictl.py project doctor reports PASS/WARN/FAIL.
- Doctor exits non-zero on FAIL.
- Output is useful for both humans and CI.
- Doctor does not bypass owning CLI validation or render commands.

### CTL-09 (TASK-027) — Task I - Add locking and atomic write protection

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_8992616ea198`, legacy `TASK-027`, aliases `TASK-027`, local `CTL` / `9`

Make parallel project-control operations safer.

Acceptance criteria:

- Concurrent writes cannot corrupt state.
- Locking behavior is tested.
- Error messages are readable.
- State/events/generated writes avoid partial output.

### CTL-10 (TASK-028) — Task J - Add read-only local Web Control Center MVP

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_1c8f867e1c2c`, legacy `TASK-028`, aliases `TASK-028`, local `CTL` / `10`

Provide initial web visibility without mutation risk.

Acceptance criteria:

- Web UI is read-only.
- Web UI uses the same command/core layer as CLI.
- Web UI does not edit JSON directly.
- Web UI clearly shows current task, queues, stale generated files, and health status.

### CTL-11 (TASK-029) — Task K - Add controlled Web write actions

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_9bd489501264`, legacy `TASK-029`, aliases `TASK-029`, local `CTL` / `11`

Allow safe project-control state changes from UI only after the read-only MVP is stable.

Acceptance criteria:

- Web write path is identical to CLI write path.
- Audit events are created.
- Invalid transitions are blocked.
- Confirmation and error reporting are present.

### CTL-12 (TASK-030) — Task L - Documentation and owner quickstart

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_235fab1d1516`, legacy `TASK-030`, aliases `TASK-030`, local `CTL` / `12`

Make the unified control-plane usable and discoverable.

Acceptance criteria:

- Owner can discover common commands quickly.
- Codex can be pointed to aictl as the preferred interface.
- Docs clearly say generated files are derived.
- Docs explain legacy ctl wrappers, project doctor, local web dashboard, web safety model, state/events/generated architecture, and ID allocation policy.

### CTL-13 (TASK-031) — CTL-13 Optimize Web Control Center performance

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_c95542f013df`, legacy `TASK-031`, aliases `TASK-031`, local `CTL` / `13`

Make Web Control Center dashboard and data endpoints fast by avoiding full project doctor execution on every request.

Acceptance criteria:

- GET /healthz remains fast and does not run heavy diagnostics.
- GET / and GET /data.json no longer run full project doctor on every request.
- Full project doctor remains available and accurate through explicit refresh or cached diagnostics.
- POST /actions invalidates relevant web caches.
- Web write safety remains unchanged: write actions still route through registered commands and do not directly edit protected files.
- Tests cover dashboard/data performance behavior, doctor refresh, and cache invalidation.
- Required validation, generated checks, project doctor, and protected-file checks pass.

## Epic `EPIC-006`

### WFA-01 (TASK-032) — WFA-01 Add Task Workflow Automation MVP

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_ceea832bf67c`, legacy `TASK-032`, aliases `TASK-032`, local `WFA` / `1`

Add high-level workflow actions for preparing tasks for Codex, refreshing execution context, and submitting tasks for review.

Acceptance criteria:

- Owner can prepare a task for Codex with one CLI workflow or one UI action.
- Prepare workflow sets/validates current task, moves task to in_progress when valid, refreshes context, refreshes Codex prompt, and runs doctor.
- Refresh context workflow rebuilds Context Pack and Codex prompt for a task.
- Submit-review workflow runs required checks and moves task to in_review only when blocking checks pass.
- All write workflows require explicit confirmation.
- Workflows do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.
- Existing individual commands still work.
- Tests and validations pass.

### WFA-02 (TASK-033) — WFA-02 Add Evolution Change Wizard

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_eb70d29e43ed`, legacy `TASK-033`, aliases `TASK-033`, local `WFA` / `2`

Add a guided workflow/UI helper to create and prepare Evolution Change records for tasks that require controlled system evolution approval.

Acceptance criteria:

- Owner can create a Change Proposal for a selected task with preview and confirmation.
- Created Change links to the correct legacy task id.
- Created Change includes affected files, risks, impact, problem/proposal/rationale draft.
- Change approval remains a separate explicit action.
- No direct protected-file edits.
- Tests and validations pass.

### WFA-03 (TASK-034) — WFA-03 Add Task Creation Wizard

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_95ae4203c49f`, legacy `TASK-034`, aliases `TASK-034`, local `WFA` / `3`

Add owner-facing CLI/UI workflow for creating individual tasks without long taskctl.py command lines.

Acceptance criteria:

- Owner can create a single task through workflow/UI without manually writing a long CLI command.
- Created task is persisted through approved command path.
- Generated task views are refreshed through owning CLI/facade.
- Task dependencies can be added where supported.
- No direct protected-file edits.
- Tests and validations pass.

### WFA-04 (TASK-035) — WFA-04 Add Bulk Task Import UI

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_b1b9da9dd270`, legacy `TASK-035`, aliases `TASK-035`, local `WFA` / `4`

Add a grouped task import interface for importing multiple planned tasks from structured text with preview, validation, and confirmation.

Acceptance criteria:

- Owner can paste a batch of task definitions and preview them.
- Import preview shows tasks, fields, dependencies, and planned commands.
- Invalid imports fail before any task is created.
- Confirmed import creates tasks through approved command path only.
- No direct AI_PROJECT/state/** edits from importer.
- Tests and validations pass.

### WFA-05 (TASK-036) — WFA-05 Add Review And Close Helpers

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_78c014419aa9`, legacy `TASK-036`, aliases `TASK-036`, local `WFA` / `5`

Add guarded workflow helpers for closing reviewed tasks, accepting linked Evolution Changes, and optionally closing completed Epics.

Acceptance criteria:

- Owner can close an in_review task with explicit notes and confirmation.
- Owner can accept an Evolution Change only when linked task completion rules pass.
- Invalid close/accept attempts are rejected with clear messages.
- Existing lifecycle semantics are preserved.
- Tests and validations pass.

### WFA-06 (TASK-037) — WFA-06 Documentation Audit And Cleanup

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_c4ef4282293c`, legacy `TASK-037`, aliases `TASK-037`, local `WFA` / `6`

Audit and update documentation after workflow automation and UI improvements are implemented.

Acceptance criteria:

- Documentation reflects the current aictl/web/workflow model.
- Legacy ctl scripts are described as compatibility layer.
- Bulk task import is documented.
- Evolution Change Flow is documented as controlled self-evolution.
- Generated files are clearly described as derived output.
- Protected-file rules are current.
- Documentation checks and project-control checks pass.

### WFA-07 (TASK-038) — UIX-01 Improve Tasks filtering grouping and collapse

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_2b313c6e127e`, legacy `TASK-038`, aliases `TASK-038`, local `WFA` / `7`

Make the Tasks page usable for large projects by adding initiative/epic/status filters, search, grouping, and collapsible done sections.

Acceptance criteria:

- Tasks page can be filtered by initiative, epic, status, and search text.
- Tasks page can group tasks by epic or status.
- Done tasks are hidden or collapsed by default.
- Current task, in-progress tasks, and review tasks remain easy to find.
- GET / and GET /data.json remain fast and do not run full doctor on every request.
- No new write behavior is introduced.
- Tests and project-control validations pass.

### WFA-08 (TASK-039) — UIX-02 Add task row workflow buttons

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_ba9070900730`, legacy `TASK-039`, aliases `TASK-039`, local `WFA` / `8`

Add status-aware workflow buttons next to tasks, including Prepare for Codex, Refresh Context, and Submit for Review.

Acceptance criteria:

- Tasks page shows useful workflow buttons based on task status.
- Prepare for Codex can be launched from a task row with explicit confirmation.
- Refresh Context can be launched from a task row with explicit confirmation.
- Submit for Review can be launched from a task row with explicit confirmation.
- Workflow actions route through governed workflow/aictl paths.
- UI displays clear success/failure output and next action hints.
- No direct protected-file writes are introduced.
- Tests and project-control validations pass.

### WFA-09 (TASK-040) — UIX-03 Add unified workflow action result panel

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_64618b90c44b`, legacy `TASK-040`, aliases `TASK-040`, local `WFA` / `9`

Add a reusable result panel for workflow and Web actions showing step status, changed files, warnings, errors, and next actions.

Acceptance criteria:

- After a workflow action, UI shows a clear action result panel.
- Result panel shows executed steps and status.
- Result panel shows warnings/errors without hiding failures.
- Result panel includes next action hints when available.
- Prepare for Codex result includes a copyable Codex instruction.
- Existing workflow safety is preserved.
- Tests and project-control validations pass.

### WFA-10 (TASK-041) — UIX-04 Add Evolution management UI tab

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_642286708abd`, legacy `TASK-041`, aliases `TASK-041`, local `WFA` / `10`

Add an Evolution tab to view and manage Change Proposals, including create-for-task, approve, move to review, and accept actions with confirmation.

Acceptance criteria:

- Evolution tab lists Change Proposals with useful metadata.
- Evolution tab can filter by status and type.
- Owner can create a Change for a task through the existing wizard.
- Owner can approve a ready Change only with explicit confirmation.
- Owner can accept a Change only when linked task completion rules pass.
- Invalid transitions are rejected clearly.
- All writes route through governed commands/workflows.
- Tests and project-control validations pass.

### WFA-11 (TASK-042) — UIX-05 Add Bulk Task Import from file

Status: `planned`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_82ea27760cf4`, legacy `TASK-042`, aliases `TASK-042`, local `WFA` / `11`

Extend Bulk Task Import to support uploading JSON files in addition to pasted JSON text.

Acceptance criteria:

- Owner can import a task batch by uploading a JSON/text file.
- Paste-based JSON import still works.
- Importer shows preview before creation.
- Invalid file type, invalid JSON, invalid refs, or oversized file fails before creation.
- Confirmed import creates tasks only through governed command paths.
- No direct tasks.json writes are introduced.
- Tests and project-control validations pass.

### WFA-12 (TASK-043) — UIX-06 Update UI workflow documentation

Status: `planned`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_ed5d17298252`, legacy `TASK-043`, aliases `TASK-043`, local `WFA` / `12`

Update owner-facing documentation for the improved UI cockpit, task filters, workflow buttons, Evolution tab, and bulk file import.

Acceptance criteria:

- Documentation describes the UI-first daily workflow.
- Documentation explains task filters, workflow buttons, Evolution tab, and bulk file import.
- Documentation preserves protected-file and generated-output rules.
- Legacy ctl scripts are documented as compatibility layer.
- Documentation checks and project-control checks pass.

### WFA-13 (TASK-044) — UIX-07 Add Task Review Done Controls

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_8995fc393bcb`, legacy `TASK-044`, aliases `TASK-044`, local `WFA` / `13`

Add UI controls for closing reviewed tasks and requesting changes from the Tasks page while preserving Human Owner review gates.

Acceptance criteria:

- Tasks in in_review show Approve & Done and Request Changes controls.
- Approve & Done requires explicit confirmation and owner notes.
- Approve & Done routes through task.close_reviewed or another governed workflow path.
- Request Changes requires explicit confirmation and owner notes.
- Review actions are hidden or disabled for invalid task statuses.
- UI shows clear result summary and next actions after review decisions.
- Linked Evolution Change is suggested after task completion but is not accepted automatically.
- No direct protected-file writes are introduced.
- Tests and project-control validations pass.

### WFA-14 (TASK-045) — UIX-08 Add Next Action and Blocked Reason Hints

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_7280203fb8a8`, legacy `TASK-045`, aliases `TASK-045`, local `WFA` / `14`

Show actionable next steps and blocked reasons for tasks, changes, and epics in the Web Control Center.

Acceptance criteria:

- Tasks page shows next-action hints for common pipeline states.
- Unavailable actions show a clear reason instead of disappearing silently.
- Tasks blocked by dependencies show which dependencies are not done.
- Tasks requiring an Evolution Change show whether the linked Change is missing, ready, approved, in_review, or accepted.
- UI suggests the correct next owner action without executing it automatically.
- Hints are consistent with lifecycle validation and existing workflows.
- No new unsafe write behavior is introduced.
- Tests and project-control validations pass.
- Evolution Change Proposal rows remain readable in normal viewport widths by using compact summaries, collapsed details, or horizontal overflow protection.
- Long affected files, risks, impacts, and metadata do not make the main Evolution table unusable.

### WFA-15 (TASK-046) — UIX-09 Add Codex Execution Report Submission

Status: `planned`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_6a6615a135ce`, legacy `TASK-046`, aliases `TASK-046`, local `WFA` / `15`

Add a governed way for Codex to submit structured task execution reports through aictl instead of relying on manual pasted summaries.

Acceptance criteria:

- Codex execution report JSON schema is documented or encoded in validation.
- Report submission command validates task identity and report shape.
- Valid reports are stored through governed state/events only.
- Invalid reports fail without partial writes.
- Task review read model can access the latest report for a task.
- Submitting a report does not approve, close, or transition the task by itself.
- Tests and project-control validations pass.

### WFA-16 (TASK-047) — UIX-10 Add Task Review Package View

Status: `planned`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_0e3c4d7a0a5d`, legacy `TASK-047`, aliases `TASK-047`, local `WFA` / `16`

Add a task review view that combines task metadata, linked Change, Codex report, changed files, checks, and owner decision controls.

Acceptance criteria:

- Task Review view shows task metadata and acceptance context.
- Task Review view shows latest Codex execution report when available.
- Task Review view shows linked Evolution Change status when available.
- Task Review view shows checks, changed files, warnings, blockers, and notes.
- Owner can make valid review decisions from the view using governed actions.
- Review decision controls remain unavailable for invalid statuses.
- Tests and project-control validations pass.

### WFA-17 (TASK-048) — UIX-11 Add Current Execution Status Panel

Status: `planned`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_2c1b0507ab6b`, legacy `TASK-048`, aliases `TASK-048`, local `WFA` / `17`

Add a UI panel showing current task, Context Pack status, Codex prompt status, and safe execution-context actions.

Acceptance criteria:

- UI clearly shows the current task when one is selected.
- UI clearly shows when no current task exists.
- UI shows Context Pack and Codex prompt readiness/staleness.
- Owner can copy the Codex handoff instruction when prompt is ready.
- Refresh and clear actions route through governed workflows/commands.
- No direct protected-file writes are introduced.
- Tests and project-control validations pass.

### WFA-18 (TASK-049) — UIX-12 Add Project Health Repair Actions

Status: `planned`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_e878d597769a`, legacy `TASK-049`, aliases `TASK-049`, local `WFA` / `18`

Add UI health and repair actions for doctor, stale generated artifacts, docs render, context/Codex refresh, and protected-file checks.

Acceptance criteria:

- UI shows project doctor health summary.
- UI shows stale generated artifact warnings in a readable way.
- Run Doctor action works through governed command routing.
- Safe repair actions require confirmation and use owning CLIs.
- Failed health checks remain visible and are not hidden as success.
- No direct generated-file edits are introduced.
- Tests and project-control validations pass.

### WFA-19 (TASK-050) — UIX-13 Add Epic Close UI Action

Status: `planned`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_32b3ecc1372f`, legacy `TASK-050`, aliases `TASK-050`, local `WFA` / `19`

Expose the epic.close_if_complete workflow in the Web Control Center with clear incomplete-task blocking reasons.

Acceptance criteria:

- UI shows epic completion status and open task counts.
- Close Epic If Complete is available only when valid or explains why it is blocked.
- Close action requires explicit confirmation.
- Close action routes through epic.close_if_complete workflow.
- Blocked close shows incomplete task refs.
- No direct plan/task state writes are introduced.
- Tests and project-control validations pass.

### WFA-20 (TASK-051) — UIX-14 Add Commit Readiness View

Status: `planned`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_d2bb13c07d81`, legacy `TASK-051`, aliases `TASK-051`, local `WFA` / `20`

Add a read-only UI view for worktree readiness, changed files, validation status, and suggested commit message.

Acceptance criteria:

- UI shows a read-only commit readiness view.
- View shows changed files or a safe unavailable message.
- View shows validation/protected-file/generated artifact readiness.
- View suggests a commit message without executing git commit.
- No git write operations are performed.
- No project-control state mutation is introduced by viewing commit readiness.
- Tests and project-control validations pass.

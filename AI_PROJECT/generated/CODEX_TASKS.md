<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Project Tasks

Revision: `942`
Current task: `TASK-129`

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

### TASK-079 — Compact codexctl execute prompt renderer

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_4b2c0921708a`, legacy `TASK-079`, aliases `TASK-079`

Render CODEX_PROMPT.md as a compact execute-profile contract instead of embedding full Context Pack content.

Acceptance criteria:

- codexctl.py build --task <TASK> still works without Context Pack.
- codexctl.py build --task <TASK> --with-context produces a compact Context section.
- Generated CODEX_PROMPT.md does not embed the full CONTEXT_PACK.md body.
- Generated CODEX_PROMPT.md includes Context Pack path, hash, docs revision, tasks revision, and selected source refs when context is attached.
- Execution Steps section is omitted for current tasks because task.execution_steps does not exist.
- Verification renders mode plus compact default check instruction.
- Existing wrapper tests still pass.
- Add or update tests to prove compact context rendering.
- Generated CODEX_PROMPT.md omits the legacy full retrieved-context body section.

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

Status: `done`
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

Status: `done`
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

Status: `done`
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

Status: `done`
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

Status: `done`
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

Status: `done`
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

Status: `done`
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

Status: `done`
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

## Epic `EPIC-007`

### PIPE-01 (TASK-052) — PIPE-01 Automation Policy Model

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_a44362cd6361`, legacy `TASK-052`, aliases `TASK-052`, local `PIPE` / `1`

Define the supervised batch pipeline automation policy model and safe presets.

Acceptance criteria:

- Policy schema covers all approved pipeline automation decisions.
- Policy validation rejects unsafe combinations with stable error codes.
- Default policy is safe and does not auto-run Codex, auto-close tasks, accept Changes, or commit.
- Auto-close is representable only when Machine Review PASS and Codex Review APPROVE are required.
- Commit policy is local-only and explicitly forbids push and merge.
- Tests and project-control validations pass.

### PIPE-02 (TASK-053) — PIPE-02 Pipeline Queue Planner

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_7290d2dfc064`, legacy `TASK-053`, aliases `TASK-053`, local `PIPE` / `2`

Select the next executable task from an owner-selected queue under policy constraints.

Acceptance criteria:

- Queue planner can preview owner-selected queues.
- Queue planner selects the same next task deterministically for the same state and policy.
- Tasks blocked by dependencies or parent state are not selected as executable.
- Planner explains skipped and blocked reasons.
- Planner does not mutate AI_PROJECT/state, events, or generated outputs.
- Tests and project-control validations pass.

### PIPE-03 (TASK-054) — PIPE-03 Pipeline Session State

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_bee07a59c599`, legacy `TASK-054`, aliases `TASK-054`, local `PIPE` / `3`

Persist supervised pipeline sessions, selected queue, policy snapshot, step status, stop reason, and audit references.

Acceptance criteria:

- Pipeline session state is validated before and after mutation.
- Session state records queue, policy snapshot, current task, gate outcomes, and stop reason.
- Pipeline events are appended for session lifecycle mutations.
- Generated Pipeline Status is derived output and can be checked for freshness if implemented.
- No direct protected-file writes are introduced.
- Tests and project-control validations pass.

### PIPE-04 (TASK-055) — PIPE-04 Run Next Step Action

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_77abb2cfe0c1`, legacy `TASK-055`, aliases `TASK-055`, local `PIPE` / `4`

Implement a supervised run-next pipeline action that advances exactly one safe step and stops on blockers.

Acceptance criteria:

- Run-next advances at most one pipeline step.
- Run-next records policy decision, selected task, gate result, and stop reason.
- Run-next stops when a required component is not implemented instead of bypassing it.
- Run-next never launches Codex before Token Budget Gate PASS.
- Run-next never closes a task without Machine Review PASS and Codex Review APPROVE when auto-close is enabled.
- Run-next never accepts a Change or commits unless policy explicitly allows it and readiness gates pass.
- Tests and project-control validations pass.

### PIPE-05 (TASK-056) — PIPE-05 Batch Runner Run Until Blocker

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_06eb9ba3c9a9`, legacy `TASK-056`, aliases `TASK-056`, local `PIPE` / `5`

Run repeated pipeline run-next steps until first blocker, policy violation, unsafe condition, token failure, or queue completion.

Acceptance criteria:

- Batch runner stops on the first blocker or policy violation.
- Batch runner stops when token budget gate fails.
- Batch runner stops when queue is complete and reports completion.
- Batch runner enforces max steps, max tasks, and rework limits.
- Every step is auditable through session state/events.
- CLI/UI action requires explicit confirmation.
- Tests and project-control validations pass.

### PIPE-06 (TASK-057) — PIPE-06 Token Budget Gate

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_c64b6f51da04`, legacy `TASK-057`, aliases `TASK-057`, local `PIPE` / `6`

Gate Codex execution using the actual prompt payload token budget and policy thresholds.

Acceptance criteria:

- Token Budget Gate evaluates the actual Codex prompt payload.
- Gate blocks execution when prompt does not fit or remaining tokens are below policy threshold.
- Gate blocks in strict mode when token count is unavailable.
- Gate blocks when context requires compact or split.
- Gate result includes measurable evidence and stable failure codes.
- Tests and project-control validations pass.

### PIPE-07 (TASK-058) — PIPE-07 Codex Execution Adapter

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_98b7b78bc079`, legacy `TASK-058`, aliases `TASK-058`, local `PIPE` / `7`

Launch or hand off Codex Executor only after policy and Token Budget Gate PASS, then capture execution metadata.

Acceptance criteria:

- Adapter default mode is safe and does not unexpectedly launch external tools.
- Adapter refuses execution unless policy allows it and Token Budget Gate PASS is present.
- Adapter captures execution metadata and exposes it to pipeline session state.
- Adapter failure stops the pipeline with a clear blocker.
- Normal tests use a fake adapter and do not require a real Codex binary/service.
- Tests and project-control validations pass.

### PIPE-08 (TASK-059) — PIPE-08 Codex Report Gate

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_c59152e998be`, legacy `TASK-059`, aliases `TASK-059`, local `PIPE` / `8`

Validate Codex structured execution reports before review and closure gates.

Acceptance criteria:

- Report Gate blocks missing, invalid, mismatched, or blocker-containing reports.
- Report Gate checks changed files against task allowed_files/governed generated files.
- Report Gate checks token usage when policy requires it.
- Report Gate result is stored or exposed for pipeline session audit.
- Tests and project-control validations pass.

### PIPE-09 (TASK-060) — PIPE-09 Machine Review Gate

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_2b44723c1bdb`, legacy `TASK-060`, aliases `TASK-060`, local `PIPE` / `9`

Run deterministic machine checks for tests, doctor, protected files, generated outputs, allowed_files, token usage, and blockers.

Acceptance criteria:

- Machine Review PASS requires all blocking checks to pass.
- Machine Review FAIL stops the pipeline.
- Protected-file and allowed_files violations are blocking.
- Token usage and report blockers are checked according to policy.
- Gate output is structured and auditable.
- Tests and project-control validations pass.

### PIPE-10 (TASK-061) — PIPE-10 Codex Review Gate

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_12dcf6285371`, legacy `TASK-061`, aliases `TASK-061`, local `PIPE` / `10`

Run a narrow read-only Codex Reviewer prompt for semantic review and structured verdict.

Acceptance criteria:

- Codex Review Gate prompt is narrow and read-only.
- Reviewer cannot mutate files, lifecycle, or commits through this gate.
- Gate accepts only structured verdicts APPROVE, REQUEST_CHANGES, or BLOCKED.
- REQUEST_CHANGES and BLOCKED stop auto-close.
- Malformed/missing reviewer output blocks the pipeline.
- Tests and project-control validations pass.

### PIPE-11 (TASK-062) — PIPE-11 Auto Review Auto Close Policy

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_01a078bae3e6`, legacy `TASK-062`, aliases `TASK-062`, local `PIPE` / `11`

Apply policy-controlled close/rework decisions only after Machine Review PASS and Codex Review APPROVE.

Acceptance criteria:

- Auto-close requires policy permission, Machine Review PASS, and Codex Review APPROVE.
- REQUEST_CHANGES moves to changes_requested or starts rework only if policy allows.
- Blocked or failed gates stop the pipeline.
- Rework loop has a policy-controlled maximum.
- Lifecycle mutations route through governed task workflows/commands.
- Tests and project-control validations pass.

### PIPE-12 (TASK-063) — PIPE-12 Controlled Git Commit Action

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_6f7cf68ecdf8`, legacy `TASK-063`, aliases `TASK-063`, local `PIPE` / `12`

Create local commits only when policy allows and commit readiness is green.

Acceptance criteria:

- Commit action is disabled unless policy explicitly allows local commit.
- Commit action refuses when commit readiness is not green.
- Commit action stages only approved files.
- Commit action never pushes, merges, resets, rebases, or discards changes.
- Commit result is recorded in session/audit.
- Tests and project-control validations pass.

### PIPE-13 (TASK-064) — PIPE-13 Pipeline UI Dashboard

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_d4153f05f2bc`, legacy `TASK-064`, aliases `TASK-064`, local `PIPE` / `13`

Add a Web Control Center dashboard for pipeline sessions, queue preview, policy selection, run-next, and run-until-blocker.

Acceptance criteria:

- Pipeline dashboard shows sessions, selected policy, queue preview, current step, and stop reason.
- Run actions require explicit confirmation.
- UI writes route through governed commands/workflows.
- Failed gates and blockers are visible.
- UI remains local-only by default.
- Tests and project-control validations pass.

### PIPE-14 (TASK-065) — PIPE-14 Pipeline Audit Trail

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_b7153a9d28be`, legacy `TASK-065`, aliases `TASK-065`, local `PIPE` / `14`

Record a complete audit trail for pipeline sessions, policy decisions, gates, Codex runs, reviews, stops, and commits.

Acceptance criteria:

- Pipeline audit captures every major gate and decision.
- Audit events include stable references and stop reasons.
- Audit avoids raw secrets and oversized prompt payloads.
- Generated audit/status output is derived and can be refreshed/check-generated if implemented.
- Tests and project-control validations pass.

### PIPE-15 (TASK-066) — PIPE-15 Pipeline SOP Documentation

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_712743bf741e`, legacy `TASK-066`, aliases `TASK-066`, local `PIPE` / `15`

Document the supervised batch pipeline runner, policies, gates, UI flow, blockers, and operator responsibilities.

Acceptance criteria:

- Pipeline SOP documents the approved algorithm and stop conditions.
- Documentation clearly distinguishes policy-selected automation from forbidden autonomy.
- Documentation says Codex Reviewer is read-only and cannot mutate files/lifecycle/commits.
- Documentation says commit is local-only and push/merge remain forbidden.
- Documentation explains token budget strict-mode failures.
- Documentation checks and project-control validations pass.

### PIPE-16 (TASK-067) — BUG-01 Fix Approve & Done stale execution context handling

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_b590f17b8bdd`, legacy `TASK-067`, aliases `TASK-067`, local `PIPE` / `16`

Fix the Web Control Center / workflow issue where Approve & Done can be blocked by stale Context Pack or Codex prompt state and where closed tasks can leave a stale Codex execution package behind.

Acceptance criteria:

- A task in in_review with stale Context Pack or stale Codex prompt can be closed through Approve & Done when explicit owner notes and confirmation are provided.
- Approve & Done still rejects tasks outside in_review.
- Approve & Done still requires non-empty owner approval notes.
- Stale Context Pack / Codex prompt state remains visible as a warning, blocked reason, or action-result detail, but does not force Refresh Context before owner acceptance.
- After successful Approve & Done, current_execution is cleared or marked non-ready when it points to the closed task.
- Closing one task does not clear an execution package that points to a different active task.
- All writes continue to route through governed CLI/workflow paths.
- Relevant tests pass and project-control validation/check-generated commands pass.

### PIPE-17 (TASK-068) — PIPE-17 Add Custom Pipeline Policy Preset Store

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_02b15df91747`, legacy `TASK-068`, aliases `TASK-068`, local `PIPE` / `17`

Add governed storage for user-defined pipeline policy presets while keeping built-in safe presets immutable.

Acceptance criteria:

- Custom policy presets can be saved, loaded, validated, listed, and deleted through governed service paths.
- Built-in policy presets remain available and immutable.
- Invalid or unsafe custom presets are rejected before persistence.
- Preset changes create audit events.
- No direct protected-file writes are introduced.
- Tests and project-control validations pass.

### PIPE-18 (TASK-069) — PIPE-18 Add Pipeline Policy CRUD Commands

Status: `blocked`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_6e53dad1427b`, legacy `TASK-069`, aliases `TASK-069`, local `PIPE` / `18`

Expose custom pipeline policy preset operations through aictl and command registry.

Acceptance criteria:

- Owner can list built-in and custom presets through aictl.
- Owner can show one preset through aictl.
- Owner can validate a policy JSON before saving.
- Owner can save or update a custom preset only with explicit confirmation.
- Owner can delete a custom preset only with explicit confirmation.
- Built-in presets cannot be overwritten or deleted.
- Command registry describes policy commands accurately.
- Tests and project-control validations pass.

### PIPE-19 (TASK-070) — PIPE-19 Add Dynamic Policy Editor To Web Pipeline Dashboard

Status: `planned`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_cd9e8b6d586b`, legacy `TASK-070`, aliases `TASK-070`, local `PIPE` / `19`

Allow editing, saving, deleting, and previewing pipeline policy presets from the Web Control Center.

Acceptance criteria:

- Changing the policy select immediately updates Policy Preset Preview without pressing Preview Queue.
- Owner can save a custom preset from the UI with explicit confirmation.
- Owner can delete a custom preset from the UI with explicit confirmation.
- Built-in presets are visibly locked and cannot be deleted or overwritten.
- Invalid custom policy values show clear validation errors before persistence.
- All Web writes route through governed aictl/registry commands.
- No direct protected-file writes are introduced.
- Tests and project-control validations pass.

### PIPE-20 (TASK-071) — PIPE-20 Document Dynamic Pipeline Policy Presets

Status: `planned`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_4556429523ff`, legacy `TASK-071`, aliases `TASK-071`, local `PIPE` / `20`

Update owner-facing SOP and quickstart documentation for custom policy presets and dynamic preview behavior.

Acceptance criteria:

- Docs explain how to use custom policy presets in UI.
- Docs explain CLI policy CRUD commands.
- Docs state built-in presets are immutable.
- Docs state dynamic preview is read-only and does not run pipeline actions.
- Docs preserve safety boundaries: no push, no merge, no bypass of gates.
- Documentation checks and project-control validations pass.

### PIPE-21 (TASK-072) — PIPE-21 Fix Pipeline Queue Epic Filter Behavior

Status: `planned`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_77eb0582f227`, legacy `TASK-072`, aliases `TASK-072`, local `PIPE` / `21`

Make Pipeline Queue Preview respect selected Epic filtering by default and avoid showing unrelated tasks from other epics.

Acceptance criteria:

- When Pipeline Queue Selector has Epic = EPIC-007, the default Queue Preview does not render tasks from EPIC-001, EPIC-002, EPIC-003, EPIC-004, EPIC-005, EPIC-006, or other non-selected Epics.
- Tasks from other Epics may still be visible only through an explicit diagnostic/debug/show-skipped option.
- Selecting Epic = EPIC-007 with Status = planned shows PIPE-17, PIPE-18, PIPE-19, and PIPE-20 or their current imported refs as matching candidates.
- max_tasks does not get consumed by done tasks or tasks skipped only because of status_not_executable or epic_filter_mismatch.
- Queue Preview selects the first valid matching executable candidate as next task when one exists.
- Queue Preview still shows clear waiting/blocking reasons for tasks inside the selected Epic.
- Selected Task Refs mode remains supported and deterministic.
- No Pipeline safety gate is weakened.
- Tests and project-control validations pass.

### PIPE-22 (TASK-073) — PIPE-22 Add Pipeline Session Resume After Blocker

Status: `planned`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_074ee82806ea`, legacy `TASK-073`, aliases `TASK-073`, local `PIPE` / `22`

Allow a blocked supervised pipeline session to be resumed after the owner resolves the blocker, without creating a new session.

Acceptance criteria:

- A blocked pipeline session can be resumed after the Human Owner resolves the blocker.
- The original PSESS-style scenario works: session blocks on approved Change gate, owner approves linked Change, same session resumes, and run-next proceeds without requiring a new session.
- Resume requires explicit confirmation.
- Resume preserves previous steps, gates, stop reason, and audit trail.
- Resume appends a new audit event.
- Resume does not approve or accept Evolution Changes.
- Resume does not bypass lifecycle, review, token, report, machine-review, Codex-review, or commit gates.
- Run-next either supports resumed sessions safely or produces an actionable message telling the owner to run the resume command first.
- Web Control Center shows a resume/continue action for blocked or stopped sessions when safe.
- Tests and project-control validations pass.

### PIPE-23 (TASK-074) — PIPE-23 Add Auto-Create Missing Changes Policy Checkbox

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_4389d41c9bf7`, legacy `TASK-074`, aliases `TASK-074`, local `PIPE` / `23`

Add a pipeline policy checkbox that creates missing linked Evolution Changes for the selected pipeline queue before execution.

Acceptance criteria:

- Pipeline UI has an Auto-create missing Changes checkbox.
- Policy preview clearly shows whether missing Changes will be created automatically.
- When enabled, selected tasks without linked Changes receive newly created linked Evolution Changes.
- Created Change ids are recorded in the pipeline session and audit trail.
- Auto-create works for a selected queue such as PIPE-17, PIPE-18, PIPE-19, PIPE-20, PIPE-21.
- Auto-create alone does not approve Changes.
- If approval is still required, session remains resumable and shows clear owner action required.
- Existing supervised policies remain backward-compatible.
- Tests pass.

### PIPE-24 (TASK-075) — PIPE-24 Add Owner-Approved Session Changes Policy Checkbox

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_c55990cd59ea`, legacy `TASK-075`, aliases `TASK-075`, local `PIPE` / `24`

Add a pipeline policy checkbox that lets the Human Owner approve all required Changes for the selected session queue as part of the pipeline run.

Acceptance criteria:

- Pipeline UI has an Owner-approve required Changes for this session checkbox.
- Checkbox requires explicit confirmation and approval note.
- Policy preview clearly distinguishes owner-approved session approval from unsafe automatic approval.
- Policy validation still rejects unsafe autonomous evolution.approve_linked_change = true.
- When enabled, pipeline approves only required Changes linked to tasks in the selected session queue.
- When combined with Auto-create missing Changes, pipeline can create and owner-approve required Changes for PIPE-17..PIPE-21 in one confirmed session flow.
- Approved Change ids, task refs, actor, approval note, and session id are recorded in audit.
- Pipeline can continue the same session after approval.
- No Change is accepted automatically.
- No unrelated Change is approved.
- Tests pass.

### PIPE-25 (TASK-076) — PIPE-25 Add Full Self-Running Pipeline Mode

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_652b0a2ad41e`, legacy `TASK-076`, aliases `TASK-076`, local `PIPE` / `25`

Turn pipeline from prompt-only orchestration into a real supervised self-running task executor.

Acceptance criteria:

- A new executable pipeline mode can run a selected task beyond prompt generation.
- Pipeline can invoke a safe local Codex adapter command using RUN_CODEX mode.
- Adapter refuses unsafe or non-allowlisted commands.
- Adapter refuses missing, stale, or wrong-task CODEX_PROMPT.md.
- Pipeline ingests a structured Codex execution report.
- Report Gate passes only for a valid report linked to the selected task.
- Machine Review Gate runs after Report Gate.
- Codex Review Gate runs after Machine Review Gate.
- With explicit owner-approved auto-close enabled, a task can reach done through governed lifecycle commands.
- Pipeline proceeds to the next selected task after the previous selected task reaches done.
- run-until-blocker can process at least two selected tasks using a fake local Codex command and finish with queue_complete.
- Prompt-only supervised mode remains available and clearly labeled.
- Misleading BUILD_PROMPT_ONLY plus auto-close/local-commit combinations are disabled or clearly rejected.
- No task outside the selected queue is closed.
- No push or merge is performed.
- Audit contains execution, report, review, close, and completion evidence.
- Tests pass.

### PIPE-26 (TASK-077) — PIPE-26 Fix Codex Adapter Prompt Transport

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_c919ccdc6d07`, legacy `TASK-077`, aliases `TASK-077`, local `PIPE` / `26`

Fix local Codex adapter so it passes CODEX_PROMPT.md to codex exec instead of running codex exec with no input.

Acceptance criteria:

- Local Codex adapter passes CODEX_PROMPT.md content to codex exec through stdin by default.
- The command ['codex', 'exec'] no longer runs with empty input.
- Command allowlist still validates the command before execution.
- Prompt hash and task identity validation still happen before execution.
- Adapter result includes bounded stdout/stderr snippets for debugging non-zero exits.
- Adapter still records stdout_ref/stderr_ref hashes.
- Non-zero command exit produces actionable diagnostics including returncode and stderr snippet.
- Fake command test verifies prompt content is received on stdin.
- Existing executable pipeline tests pass.
- Project-control validations pass.
- When codex exec fails because bubblewrap/user namespaces are unavailable, adapter reports a clear sandbox compatibility blocker.
- Owner can configure the local Codex command/allowlist to use a Codex CLI sandbox mode supported by the local environment.
- Adapter still refuses any command not present in command_allowlist.
- Adapter passes CODEX_PROMPT.md content to codex exec through stdin by default.
- Owner can configure local_command and command_allowlist to use codex exec -s danger-full-access when workspace-write sandbox is unavailable.
- Adapter refuses any Codex command that is not present in command_allowlist.
- When Codex fails with bwrap/loopback/user-namespace sandbox errors, adapter reports CODEX_ADAPTER_SANDBOX_UNAVAILABLE instead of generic local_command_nonzero_exit.
- Adapter stores only bounded stdout/stderr snippets and hashes, never full prompt text.
- Tests cover stdin prompt transport, sandbox failure detection, allowlist enforcement, and non-zero stderr diagnostics.

### PIPE-27 (TASK-078) — PIPE-27 Add Persistent Pipeline Session Detail Page

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_bc97855d54fb`, legacy `TASK-078`, aliases `TASK-078`, local `PIPE` / `27`

Add a persistent per-session Pipeline page with real-time steps, expandable logs, session actions, artifacts, audit events, and historical availability.

Acceptance criteria:

- Each pipeline session has a stable URL such as /pipeline/sessions/PSESS-012.
- The main Pipeline page links each session id to its detail page.
- The session detail page remains available after the session completes, blocks, fails, stops, or is archived.
- Running sessions auto-refresh without manual page reload.
- Auto-refresh stops after a terminal session state.
- The page has a Steps section with all pipeline steps in execution order.
- Each step can be expanded to inspect status, gates, details, and bounded logs.
- The page has an Actions section with session-level buttons.
- Action buttons require confirmation for mutating operations.
- The page separates safe actions, owner approval actions, and restricted/dangerous actions.
- The page shows session summary, live current step, artifacts, queue snapshot, audit events, files changed, blockers, and raw debug sections.
- Codex adapter stdout/stderr are shown only as bounded snippets or safe references.
- Full CODEX_PROMPT.md content is never rendered on the session page.
- Unbounded stdout/stderr logs are never stored or rendered.
- Historical completed sessions can be opened and inspected.
- Tests and project-control validations pass.

## Epic `EPIC-009`

### PIPEF-01 (TASK-080) — PIPE-001 Add Pipeline PhaseResult model

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_0e3009920745`, legacy `TASK-080`, aliases `TASK-080`, local `PIPEF` / `1`

Add a reusable Pipeline PhaseResult model so every pipeline phase can return one stable, compact outcome contract.

Acceptance criteria:

- PhaseResult can be constructed for passed, blocked, failed, and skipped outcomes.
- PhaseResult serializes to JSON-compatible data with phase, status, reason, next_action, artifacts, changed_files, generated_files, and events.
- Invalid phase names or statuses are rejected with a stable pipeline error.
- No existing pipeline runner behavior is changed by this task.

### PIPEF-02 (TASK-081) — PIPE-002 Extend pipeline sessions with phase fields

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_11c4232541ae`, legacy `TASK-081`, aliases `TASK-081`, local `PIPEF` / `2`

Extend pipeline session state to store the current phase, phase status, blocker reason, next action, and phase history.

Acceptance criteria:

- Newly created pipeline sessions include the phase fields with safe empty defaults.
- Existing sessions without phase fields continue to pass pipeline validation.
- Validation rejects malformed phase_history entries when phase fields are present.
- No generated files are manually edited.

### PIPEF-03 (TASK-082) — PIPE-003 Add phase start and result mutations

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_873cda2f03f6`, legacy `TASK-082`, aliases `TASK-082`, local `PIPEF` / `3`

Add governed mutation helpers for starting a pipeline phase and recording a phase result on a session.

Acceptance criteria:

- Starting a phase records the current phase and running or planned phase status without corrupting step data.
- Recording a passed phase clears blocked_by and stores the next action.
- Recording a blocked or failed phase preserves a stable blocker code or reason.
- All phase mutations write audit events and refresh generated pipeline status through the existing mutation path.

### PIPEF-04 (TASK-083) — PIPE-004 Render phase status in pipeline status output

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_36c75a3cfd8d`, legacy `TASK-083`, aliases `TASK-083`, local `PIPEF` / `4`

Render the current pipeline phase, phase status, blocker, and next action in generated PIPELINE_STATUS.md.

Acceptance criteria:

- PIPELINE_STATUS.md shows Current phase, Phase status, Blocked by, and Next action for the current session.
- Sessions without phase fields render safe fallback values instead of crashing.
- Phase history rendering is deterministic across repeated renders.
- pipeline check-generated can detect stale phase status output.

### PIPEF-05 (TASK-084) — PIPE-005 Register phase pipeline commands

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_cb924136906c`, legacy `TASK-084`, aliases `TASK-084`, local `PIPEF` / `5`

Register the planned phase-based pipeline commands in the command registry and CLI skeleton without implementing phase behavior yet.

Acceptance criteria:

- aictl command list --domain pipeline includes the new phase command names.
- aictl command describe works for each new phase command.
- Calling an unimplemented phase command returns a stable not-implemented result instead of crashing.
- Existing pipeline commands still parse and dispatch as before.

### PIPEF-06 (TASK-085) — PIPE-006 Add pipeline queue preview CLI

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_636788ea2870`, legacy `TASK-085`, aliases `TASK-085`, local `PIPEF` / `6`

Add a read-only pipeline queue preview command that selects the next executable task without mutating project state.

Acceptance criteria:

- pipeline queue preview returns a queue PhaseResult or equivalent read-only payload.
- The command reports next_task when an executable task exists.
- The command returns waiting, blocked, and skipped items with reason data.
- Running the command does not change AI_PROJECT/state, AI_PROJECT/events, or AI_PROJECT/generated.

### PIPEF-07 (TASK-086) — PIPE-007 Normalize queue preview output

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_f7d812720daf`, legacy `TASK-086`, aliases `TASK-086`, local `PIPEF` / `7`

Normalize queue preview output into a compact, stable JSON structure with next task, categories, and reason codes.

Acceptance criteria:

- Queue output contains next_task, executable, waiting, blocked, skipped, and reasons keys.
- Each non-executable item includes at least one stable reason code.
- The output is deterministic for the same task state and filters.
- The normalizer does not mutate QueuePreview or task state.

### PIPEF-08 (TASK-087) — PIPE-008 Return no-task queue outcome

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_883aff079cb5`, legacy `TASK-087`, aliases `TASK-087`, local `PIPEF` / `8`

Return a blocked queue phase outcome when no executable task is available instead of treating an empty queue as a system failure.

Acceptance criteria:

- An empty queue returns a blocked phase outcome with blocked_by NO_EXECUTABLE_TASK.
- A queue with only waiting or blocked tasks includes categorized reasons in artifacts.
- The command exits through the normal phase result path, not an exception.
- No state, events, or generated files are modified.

### PIPEF-09 (TASK-088) — PIPE-009 Narrow Change gate to selected task

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_72da12661a9c`, legacy `TASK-088`, aliases `TASK-088`, local `PIPEF` / `9`

Limit prepare-time Evolution Change approval checks to the selected next task by default.

Acceptance criteria:

- Prepare for one selected task does not create or require Evolution Changes for waiting tasks.
- Prepare for one selected task does not create or require Evolution Changes for blocked tasks.
- Approved linked Change detection still passes when the selected task has an approved, in_progress, in_review, or accepted Change.
- Missing approved Change for the selected task still blocks execution or creates a missing Change according to policy.

### PIPEF-10 (TASK-089) — PIPE-010 Extract prepare phase service

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_9bddf8617da4`, legacy `TASK-089`, aliases `TASK-089`, local `PIPEF` / `10`

Extract a dedicated prepare phase service that sets up the selected task, Context Pack, and Codex prompt without running Codex.

Acceptance criteria:

- pipeline prepare can prepare the selected task without invoking the Codex adapter.
- The task.prepare_for_codex workflow is invoked only after the selected-task Change gate passes or is intentionally satisfied.
- A failed prepare workflow returns a blocked or failed prepare PhaseResult with workflow evidence.
- Successful prepare sets next_action to execute.

### PIPEF-11 (TASK-090) — PIPE-011 Record prepare artifacts

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_709c8d3aac54`, legacy `TASK-090`, aliases `TASK-090`, local `PIPEF` / `11`

Record prepare artifacts on the pipeline session so execute can use the exact generated prompt and context from prepare.

Acceptance criteria:

- A successful prepare result includes task_id, context_pack_path, prompt_path, and prompt_sha256.
- The session phase history records the same prepare artifact metadata.
- Execute can read the prepared prompt path and checksum from session evidence.
- Repeated rendering of pipeline status shows the prepared task and prompt reference without large prompt content.

### PIPEF-12 (TASK-091) — PIPE-012 Add prepare idempotency check

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_4f7a82f8792b`, legacy `TASK-091`, aliases `TASK-091`, local `PIPEF` / `12`

Make repeated prepare calls for the same session and task safe by detecting fresh existing context and prompt artifacts.

Acceptance criteria:

- Running prepare twice for the same unchanged task does not produce conflicting session evidence.
- Prepare rebuilds when the prompt is missing.
- Prepare rebuilds when the selected task differs from stored prepare artifacts.
- The result clearly states whether prepare reused or rebuilt artifacts.

### PIPEF-13 (TASK-092) — PIPE-013 Extract execute phase service

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_6d923b53b481`, legacy `TASK-092`, aliases `TASK-092`, local `PIPEF` / `13`

Extract a dedicated execute phase service that runs or prepares Codex execution without performing report, verify, review, or close work.

Acceptance criteria:

- pipeline execute fails or blocks clearly when prepare evidence is missing.
- pipeline execute calls the Codex adapter only for policies that allow execution.
- pipeline execute does not run report gate, machine review, semantic review, close, or commit.
- Successful execute sets next_action to collect-report.

### PIPEF-14 (TASK-093) — PIPE-014 Decouple report requirement from execute

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_c4834becc0c9`, legacy `TASK-093`, aliases `TASK-093`, local `PIPEF` / `14`

Move structured report presence requirements out of the execute phase so report collection is handled by collect-report.

Acceptance criteria:

- Execute can return passed when the local command succeeds but no report is collected yet.
- Execute result includes before_report_id and after_report_id when available.
- Collect-report remains responsible for blocking on missing required report.
- Existing adapter failures such as timeout, nonzero command, or stale prompt still produce blocked or failed execute outcomes.

### PIPEF-15 (TASK-094) — PIPE-015 Add manual handoff execute mode

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_7a4766c21fbc`, legacy `TASK-094`, aliases `TASK-094`, local `PIPEF` / `15`

Add an explicit manual handoff execute outcome that tells the owner how to run Codex manually and submit a structured report.

Acceptance criteria:

- Manual handoff mode returns status blocked, not failed.
- The result includes enough information to find the generated prompt.
- The result includes the structured report submission command or equivalent instruction.
- No downstream gates are run while manual handoff is unresolved.

### PIPEF-16 (TASK-095) — PIPE-016 Record execute adapter result

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_dc4b0820b89a`, legacy `TASK-095`, aliases `TASK-095`, local `PIPEF` / `16`

Persist Codex adapter execution evidence in the session phase history for debugging and downstream gates.

Acceptance criteria:

- Execute phase history contains adapter evidence after every execute attempt.
- Stored evidence does not contain the full prompt text.
- Stored evidence does not contain unbounded stdout or stderr.
- Downstream phases can determine whether execute passed, blocked, or failed from session evidence.

### PIPEF-17 (TASK-096) — PIPE-017 Add pipeline report template command

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_b759fa4bdb90`, legacy `TASK-096`, aliases `TASK-096`, local `PIPEF` / `17`

Add a pipeline report template command that emits a valid structured report skeleton for the selected task.

Acceptance criteria:

- pipeline report template --task TASK_REF outputs JSON with every required report field.
- The template includes the selected task_id and optional task_ref when resolvable.
- The template includes empty changed_files, generated_files, checks, warnings, blockers, and notes arrays.
- The command does not mutate task_reports.json or any pipeline session state.

### PIPEF-18 (TASK-097) — PIPE-018 Add collect-report phase service

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_1caa1f6c5e32`, legacy `TASK-097`, aliases `TASK-097`, local `PIPEF` / `18`

Add a collect-report phase that finds the latest structured execution report for the current pipeline task.

Acceptance criteria:

- pipeline collect-report returns passed when a structured report exists for the selected task.
- pipeline collect-report returns blocked, not failed, when the report is missing.
- The result includes report_id and task_id when a report is found.
- The phase does not run report schema validation or project tests.

### PIPEF-19 (TASK-098) — PIPE-019 Validate collected report task identity

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_f48405c9bd54`, legacy `TASK-098`, aliases `TASK-098`, local `PIPEF` / `19`

Ensure collect-report accepts only structured reports that belong to the current pipeline task.

Acceptance criteria:

- A report whose task_id differs from the selected task blocks collect-report.
- A report with mismatched reported_task_id blocks collect-report when present.
- A report with matching task_id passes identity collection checks.
- The blocked result includes the expected task id and observed report task id.

### PIPEF-20 (TASK-099) — PIPE-020 Validate report freshness after execute

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_9d547d384917`, legacy `TASK-099`, aliases `TASK-099`, local `PIPEF` / `20`

Ensure collect-report can distinguish a report created for the current execution from an older report.

Acceptance criteria:

- A report submitted after the current execute phase passes freshness checks.
- An older report blocks collect-report unless allow-existing-report is explicitly used.
- The result explains whether freshness was based on timestamp, report id, or recovery override.
- The override is visible in phase artifacts for review.

### PIPEF-21 (TASK-100) — PIPE-021 Extract report schema gate into verify

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_30296d900021`, legacy `TASK-100`, aliases `TASK-100`, local `PIPEF` / `21`

Add a verify phase entry point that runs the structured report gate for the collected report.

Acceptance criteria:

- A valid collected report allows verify to continue to later gates.
- An invalid report schema blocks or fails verify with report gate issue codes.
- Report blockers in the structured report prevent verify from passing.
- Report gate evidence is recorded in the verify phase result.

### PIPEF-22 (TASK-101) — PIPE-022 Add actual git diff gate

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_d73d1dbcef99`, legacy `TASK-101`, aliases `TASK-101`, local `PIPEF` / `22`

Add a git diff gate that reports the actual changed, staged, unstaged, and untracked files in the working tree.

Acceptance criteria:

- The gate returns pass for a clean working tree when no changes are expected.
- The gate lists modified tracked files from actual git state.
- The gate lists untracked files from actual git state.
- The gate returns a stable blocked or failed result if git is unavailable or the path is not a repository.

### PIPEF-23 (TASK-102) — PIPE-023 Compare report files with actual git diff

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_9912805a733c`, legacy `TASK-102`, aliases `TASK-102`, local `PIPEF` / `23`

Block verify when structured report changed_files do not match the actual git diff evidence.

Acceptance criteria:

- Verify blocks when actual changed files are missing from report.changed_files.
- Verify warns or blocks according to policy when report.changed_files includes files not present in actual diff.
- The blocked result lists missing and extra file paths.
- A matching report and actual diff passes this gate.

### PIPEF-24 (TASK-103) — PIPE-024 Enforce allowed files against actual diff

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_fde0437fb3fe`, legacy `TASK-103`, aliases `TASK-103`, local `PIPEF` / `24`

Enforce task allowed_files against the actual git diff instead of relying only on the structured report.

Acceptance criteria:

- Actual changed files inside task.allowed_files pass allowed-files verification.
- Actual changed files outside task.allowed_files block verify.
- Governed generated files are treated according to generated file policy instead of broad allow-all behavior.
- The blocked result lists every out-of-scope path.

### PIPEF-25 (TASK-104) — PIPE-025 Enforce protected files against actual diff

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_be2522d9d039`, legacy `TASK-104`, aliases `TASK-104`, local `PIPEF` / `25`

Block verify when actual git diff includes protected project-control state, event, or ungoverned generated files.

Acceptance criteria:

- Actual changes under AI_PROJECT/state block verify unless made by governed control commands outside executor scope.
- Actual changes under AI_PROJECT/events block verify unless made by governed control commands outside executor scope.
- Ungoverned changes under AI_PROJECT/generated block verify.
- The blocked result lists protected paths and reason codes.

### PIPEF-26 (TASK-105) — PIPE-026 Add project test policy

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_b2b885003472`, legacy `TASK-105`, aliases `TASK-105`, local `PIPEF` / `26`

Add pipeline policy support for explicit project test commands used by the verify phase.

Acceptance criteria:

- Pipeline policy can serialize and deserialize project_tests configuration.
- Invalid timeout or malformed commands fail policy validation.
- Default built-in presets remain valid after the new policy field is added.
- No project test command runs as part of this task.

### PIPEF-27 (TASK-106) — PIPE-027 Record verify evidence

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_9643b73441b8`, legacy `TASK-106`, aliases `TASK-106`, local `PIPEF` / `27`

Record report, git diff, allowed-files, protected-files, and project-test gate evidence in verify phase artifacts.

Acceptance criteria:

- A passed verify phase records report_gate and git_diff_gate evidence.
- A blocked verify phase records the gate that caused the blocker.
- Project test evidence is recorded when project tests are configured.
- The evidence object is compact enough for pipeline status rendering.

### PIPEF-28 (TASK-107) — PIPE-028 Add review prompt build command

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_6375acbf3d8e`, legacy `TASK-107`, aliases `TASK-107`, local `PIPEF` / `28`

Add a review phase mode that builds the semantic Codex review prompt without requiring a reviewer to run immediately.

Acceptance criteria:

- The command builds a review prompt for the selected task after verify evidence exists.
- The command does not approve, request changes, close tasks, or run Codex execution.
- The result includes prompt path or prompt checksum evidence.
- Missing verify evidence blocks review prompt generation with a clear next action.

### PIPEF-29 (TASK-108) — PIPE-029 Accept manual review file

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_6d93844f1bf9`, legacy `TASK-108`, aliases `TASK-108`, local `PIPEF` / `29`

Allow the review phase to accept a manual semantic review JSON file and validate it through the existing Codex review evaluator.

Acceptance criteria:

- A valid manual review file with verdict APPROVE passes the review phase.
- A valid manual review file with verdict REQUEST_CHANGES blocks the review phase.
- Malformed manual review JSON fails or blocks with a stable review output error.
- The review phase records review_id, verdict, findings, and risks in bounded artifacts.

### PIPEF-30 (TASK-109) — PIPE-030 Add reviewer command adapter

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_de35437400fb`, legacy `TASK-109`, aliases `TASK-109`, local `PIPEF` / `30`

Add a reviewer command adapter that sends the review prompt to a local command and parses JSON reviewer output.

Acceptance criteria:

- A reviewer command returning valid APPROVE JSON can pass the review phase.
- A reviewer command returning REQUEST_CHANGES JSON blocks the review phase.
- A reviewer command timeout or nonzero exit returns a stable blocked or failed review outcome.
- Reviewer command evidence is stored without unbounded stdout or stderr.

### PIPEF-31 (TASK-110) — PIPE-031 Handle review request changes outcome

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_9538af470a51`, legacy `TASK-110`, aliases `TASK-110`, local `PIPEF` / `31`

Map semantic review REQUEST_CHANGES into a normal blocked pipeline outcome with a clear rework next action.

Acceptance criteria:

- REQUEST_CHANGES does not produce a failed system result.
- The blocked review result includes reviewer findings.
- The next_action tells the owner how to proceed with rework.
- APPROVE and BLOCKED verdicts continue to map to their intended outcomes.

### PIPEF-32 (TASK-111) — PIPE-032 Add close phase preflight

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_e617943698e4`, legacy `TASK-111`, aliases `TASK-111`, local `PIPEF` / `32`

Add a close phase preflight that requires successful prepare, execute, collect-report, verify, and APPROVE review evidence.

Acceptance criteria:

- pipeline close --confirm blocks when prepare evidence is missing.
- pipeline close --confirm blocks when verify did not pass.
- pipeline close --confirm blocks when review did not return APPROVE.
- A complete approved phase history allows close preflight to pass.

### PIPEF-33 (TASK-112) — PIPE-033 Extract task close action

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_00193f76204e`, legacy `TASK-112`, aliases `TASK-112`, local `PIPEF` / `33`

Implement the close phase task lifecycle action that approves and marks the reviewed task done after preflight passes.

Acceptance criteria:

- The selected task transitions to done only after review APPROVE evidence exists.
- Close records task approval or close workflow evidence.
- Task close failures produce blocked or failed close outcomes with workflow details.
- No Evolution Change acceptance or commit is performed by this task.

### PIPEF-34 (TASK-113) — PIPE-034 Accept linked Evolution Change on close

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_9f4eba5ef15d`, legacy `TASK-113`, aliases `TASK-113`, local `PIPEF` / `34`

Allow the close phase to accept linked Evolution Changes after the selected task has been closed successfully.

Acceptance criteria:

- A linked acceptable Change can move to accepted after the task is done.
- A linked Change is not accepted before the task close action succeeds.
- Non-acceptable Change statuses are reported as blocked or skipped with reason data.
- Close artifacts include accepted_change_ids when acceptance succeeds.

### PIPEF-35 (TASK-114) — PIPE-035 Add optional local commit close step

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_2e14c59cc470`, legacy `TASK-114`, aliases `TASK-114`, local `PIPEF` / `35`

Add an optional local-only commit step to close when policy explicitly allows local commits.

Acceptance criteria:

- No commit is created when commit policy is disabled.
- A local commit is created only when policy enables local-only commit and readiness checks pass.
- The result records the local commit hash when commit succeeds.
- Push and merge are not performed or authorized by this step.

### PIPEF-36 (TASK-115) — PIPE-036 Clear execution state after close

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_16c2364694a6`, legacy `TASK-115`, aliases `TASK-115`, local `PIPEF` / `36`

Clear stale Codex and current execution state after the selected task is closed.

Acceptance criteria:

- After close, current Codex execution no longer targets the closed task.
- Cleanup is skipped with a clear reason if execution state targets another task.
- Generated output is refreshed through existing render or clear commands.
- No protected state or generated file is edited manually.

### PIPEF-37 (TASK-116) — PIPE-037 Rewrite run-next as phase dispatcher

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_fa83e9639822`, legacy `TASK-116`, aliases `TASK-116`, local `PIPEF` / `37`

Rewrite pipeline run-next to dispatch exactly one next required phase instead of executing the full lifecycle monolith.

Acceptance criteria:

- run-next executes at most one phase per call.
- run-next no longer directly performs prepare, execute, verify, review, and close logic in one function body.
- Blocked phase outcomes are returned with blocked_by and next_action.
- Existing tests or smoke checks for run-next are updated to expect phase dispatch behavior.

### PIPEF-38 (TASK-117) — PIPE-038 Rewrite run-until-blocker with phase outcomes

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_78e3f020194d`, legacy `TASK-117`, aliases `TASK-117`, local `PIPEF` / `38`

Rewrite pipeline run-until-blocker to continue across passed phases and stop on blocked, failed, or completed outcomes.

Acceptance criteria:

- run-until-blocker continues after a passed prepare phase.
- run-until-blocker continues after a passed verify phase.
- run-until-blocker stops with clear owner_action_required on blocked collect-report or review outcomes.
- max_steps still stops the batch run safely.

### PIPEF-39 (TASK-118) — PIPE-039 Add CI exit-code mode for pipeline

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_69240c03bede`, legacy `TASK-118`, aliases `TASK-118`, local `PIPEF` / `39`

Add a CI-oriented exit-code mode where blocked and failed pipeline outcomes produce nonzero process exit codes.

Acceptance criteria:

- pipeline run-next --ci exits 0 for passed or completed outcomes.
- pipeline run-next --ci exits 2 for blocked outcomes.
- pipeline run-next --ci exits 1 for failed outcomes.
- Default non-CI behavior remains compatible with human safe-stop usage.

### PIPEF-40 (TASK-119) — PIPE-040 Add tests for phase model and mutations

Status: `planned`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_5bcaf7cb78cb`, legacy `TASK-119`, aliases `TASK-119`, local `PIPEF` / `40`

Add tests for PhaseResult serialization, session phase fields, and governed phase mutation helpers.

Acceptance criteria:

- Tests pass for all PhaseResult statuses.
- Tests prove legacy pipeline sessions remain valid.
- Tests prove phase results append to phase_history.
- Tests prove terminal sessions reject new phase mutations.

### PIPEF-41 (TASK-120) — PIPE-041 Add tests for queue prepare execute report phases

Status: `planned`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_5c3a3cffb80a`, legacy `TASK-120`, aliases `TASK-120`, local `PIPEF` / `41`

Add tests for the queue, prepare, execute, and collect-report phase boundaries using fake state and adapters.

Acceptance criteria:

- Queue tests prove no state or generated files are written by preview.
- Prepare tests verify Codex adapter is not called.
- Execute tests verify report gate is not called.
- Collect-report tests verify task identity and missing report outcomes.

### PIPEF-42 (TASK-121) — PIPE-042 Add tests for git diff gate

Status: `planned`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_5517275e5470`, legacy `TASK-121`, aliases `TASK-121`, local `PIPEF` / `42`

Add focused tests for actual git diff gate and file-scope comparison behavior.

Acceptance criteria:

- The git diff gate detects changed tracked files.
- The git diff gate detects untracked files.
- Verify comparison blocks when actual files are missing from the report.
- Protected file changes are blocked with stable reason codes.

### PIPEF-43 (TASK-122) — PIPE-043 Add fake Codex happy path integration test

Status: `planned`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_6d574d8b0795`, legacy `TASK-122`, aliases `TASK-122`, local `PIPEF` / `43`

Add an integration test where a fake Codex adapter creates a structured report and the pipeline advances through verify.

Acceptance criteria:

- The integration test reaches verify passed with fake Codex execution.
- The test uses only temporary project state and local fake commands.
- The report contains changed_files matching actual diff evidence.
- Phase history includes queue, prepare, execute, collect-report, and verify outcomes.

### PIPEF-44 (TASK-123) — PIPE-044 Add fake reviewer close integration test

Status: `planned`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_99b00cf46e71`, legacy `TASK-123`, aliases `TASK-123`, local `PIPEF` / `44`

Add an integration test where a fake reviewer returns APPROVE and the pipeline reaches close.

Acceptance criteria:

- The integration test reaches review passed with fake reviewer output.
- The close phase runs only after review APPROVE.
- The selected task reaches done or the expected governed close status.
- The test records review_id and close artifacts in phase history.

### PIPEF-45 (TASK-124) — PIPE-045 Update phase pipeline usage guide

Status: `planned`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_925d6a510dc5`, legacy `TASK-124`, aliases `TASK-124`, local `PIPEF` / `45`

Add user-facing documentation for the phase-based pipeline commands, outcomes, and common blocked states.

Acceptance criteria:

- The guide shows the command sequence: queue preview, prepare, execute, collect-report, verify, review, close.
- The guide explains blocked outcomes as normal owner-action states.
- The guide documents CI exit codes for passed, blocked, and failed outcomes.
- ai-system/README.md links to the new usage guide.

### PIPEF-46 (TASK-125) — Add UI settings defaults and loader

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_ca80acf6a7d4`, legacy `TASK-125`, aliases `TASK-125`, local `PIPEF` / `46`

Add a UI settings module that returns built-in defaults and optionally overlays AI_PROJECT/config/ui_settings.json.

Acceptance criteria:

- Effective settings contain command_line set to codex exec by default.
- Effective settings contain default_policy set to supervised_executable_local_commit by default.
- Missing AI_PROJECT/config/ui_settings.json does not produce an error.
- Existing ui_settings.json overrides default values.
- Invalid non-object JSON settings fail with a clear validation error.

### PIPEF-47 (TASK-126) — Add UI settings CLI commands

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_066a06b4cf1f`, legacy `TASK-126`, aliases `TASK-126`, local `PIPEF` / `47`

Add aictl UI settings commands to show, initialize, and upsert project-local UI settings.

Acceptance criteria:

- ui settings show prints effective settings and indicates whether they came from defaults or project file.
- ui settings init --confirm creates AI_PROJECT/config/ui_settings.json with minimal default settings.
- ui settings init without --confirm refuses to write.
- ui settings set command_line "codex exec" writes or updates the command_line key.
- ui settings set some_random_key value adds a new top-level key with string value.
- Settings writes preserve schema_version when present.

### PIPEF-48 (TASK-127) — Resolve pipeline policy from UI settings

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_3a16c86f2cb8`, legacy `TASK-127`, aliases `TASK-127`, local `PIPEF` / `48`

Add a settings-aware policy resolver that applies default_policy and command_line to executable pipeline runs.

Acceptance criteria:

- default_policy resolves to supervised_executable_local_commit when no settings file exists.
- command_line codex exec maps to local command arguments equivalent to codex exec.
- Executable policy allowlist matches the configured command_line.
- Non-executable policies do not require command_line application.
- Invalid or unknown default_policy fails with a clear error.

### PIPEF-49 (TASK-128) — Add settings-backed single-task Run command

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_2cfb601bb104`, legacy `TASK-128`, aliases `TASK-128`, local `PIPEF` / `49`

Add a CLI command that runs one selected task using effective UI settings for policy and command configuration.

Acceptance criteria:

- aictl ui run TASK_REF creates or delegates to a single-task pipeline session.
- The command uses default_policy from effective UI settings.
- The command uses command_line from effective UI settings for executable policies.
- The command requires confirmation before executing run-until-blocker.
- The command returns a clear completed, blocked, or failed result.
- The command does not directly edit AI_PROJECT/state task files outside existing governed pipeline commands.

### PIPEF-50 (TASK-129) — Add Codex preflight for UI Run ⭐

Status: `in_progress`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_e7309de4e114`, legacy `TASK-129`, aliases `TASK-129`, local `PIPEF` / `50`

Add a Codex executable preflight that checks the configured command before launching an executable Run.

Acceptance criteria:

- Preflight returns passed when the configured command exits successfully.
- Preflight returns a blocked result when bwrap, RTM_NEWADDR, user namespace, or Operation not permitted appears in output.
- Preflight uses the effective command_line setting.
- Preflight does not write project-control state or generated files.
- UI Run can use the preflight result to block executable execution before starting a session.

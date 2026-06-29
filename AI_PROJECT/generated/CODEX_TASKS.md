<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Project Tasks

Revision: `1790`
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

### CTL-14 (TASK-159) — Add batch UI settings apply action

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_704047330e84`, legacy `TASK-159`, aliases `TASK-159`, local `CTL` / `14`

Add backend support for saving all Web Control Center UI settings at once, including the new `require_codex_review` setting.

Acceptance criteria:

- `require_codex_review` is present in effective UI settings and defaults to `true`.
- `require_codex_review` accepts boolean values and the strings `true`, `false`, `1`, and `0` consistently with existing boolean settings.
- `ui.settings.apply` saves all submitted allowlisted settings in one state write.
- Unchecked checkbox submissions save `require_codex_review=false` and `allow_internal_change_gate_bypass=false` through hidden field handling.
- `ui.settings.set` remains available and existing behavior is unchanged.
- Relevant UI settings and Web Control Center tests pass.

### CTL-15 (TASK-160) — Render unified Web Settings panel

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_23f8c5181e82`, legacy `TASK-160`, aliases `TASK-160`, local `CTL` / `15`

Replace the fragmented Settings page with one editable panel that exposes all UI settings as rows and saves them with one Apply button.

Acceptance criteria:

- `/settings` renders one visible Settings panel instead of separate Effective UI Settings, Internal Change Gate Bypass, and Update UI Setting panels.
- The one panel contains Pipeline, Review Gates, Timeouts, and Advanced groups.
- The page has exactly one primary Apply Settings button for the Settings form.
- Machine Review is visibly ON or locked and cannot be edited.
- `Require Codex Review before close` is visible as an editable checkbox with helper text about saving tokens.
- `Allow internal Change gate bypass` is moved into the Advanced group.
- Web Control Center tests verify the new layout and absence of the old generic key-value Settings form.

### CTL-16 (TASK-216) — Add shared Web owner shell

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_1634bff488b5`, legacy `TASK-216`, aliases `TASK-216`, local `CTL` / `16`

Introduce a shared Web Control Center shell with grouped sidebar navigation and a consistent main content layout for every route.

Acceptance criteria:

- All existing Web Control Center routes render inside the new shared shell.
- The old long horizontal nav is replaced by grouped sidebar navigation.
- The active route remains visibly highlighted.
- The UI remains usable on narrow screens.
- No state-changing action is introduced by the shell itself.

### CTL-17 (TASK-217) — Add sticky current execution bar

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_e9d5369a0d0c`, legacy `TASK-217`, aliases `TASK-217`, local `CTL` / `17`

Add a sticky owner-facing current execution bar that shows the current task, status, next action, prompt readiness, and safe quick actions.

Acceptance criteria:

- Dashboard and Tasks pages show a sticky current execution bar when current execution data exists.
- The bar degrades to a compact no-current-task state when no current task exists.
- Every visible quick action maps to an existing /actions workflow or a read-only route.
- The current task label matches existing dashboard current_task data.
- No duplicate primary action is shown in both topbar and the same visible row without clear hierarchy.

### CTL-18 (TASK-218) — Add compact health summary panel

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_1b30b9da5168`, legacy `TASK-218`, aliases `TASK-218`, local `CTL` / `18`

Replace large repeated health tables on owner work pages with a compact health summary and expandable detail block.

Acceptance criteria:

- Dashboard and Tasks no longer show a large health table by default.
- A compact health summary is visible above or near owner work queues.
- Detailed health signals remain reachable without navigating away.
- Existing health action forms still post through /actions with confirmation.
- The Doctor page still provides full diagnostic detail.

### CTL-19 (TASK-219) — Build owner action queue read model

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_edfef73a9c2d`, legacy `TASK-219`, aliases `TASK-219`, local `CTL` / `19`

Add a read-only owner action queue that categorizes tasks and changes by the next decision or safe action needed.

Acceptance criteria:

- /data.json includes an owner action queue or equivalent read-only structure.
- Current in-progress task appears in the current category.
- Ready Change Proposals that need owner approval appear in needs_decision.
- Runnable tasks appear in ready_to_run only when existing guards allow a run action.
- Blocked items include one compact owner-facing blocker reason.
- Existing dashboard, tasks, changes, and pipeline data remains backward compatible.

### CTL-20 (TASK-220) — Render Dashboard as Owner Cockpit

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_9a5558850dfe`, legacy `TASK-220`, aliases `TASK-220`, local `CTL` / `20`

Convert the Dashboard into an Owner Cockpit showing current execution, health, action queue, and recent important signals.

Acceptance criteria:

- The root page answers what is current, what needs owner decision, what can run, and what is blocked.
- Non-actionable metrics such as total done tasks are not prominent on the first screen.
- Every visible button either opens details, navigates, copies existing text, or posts an existing confirmed action.
- The page remains readable without horizontal scrolling on normal desktop width.
- Existing Dashboard route remains `/`.

### CTL-21 (TASK-221) — Convert Tasks to action queue

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_af38da388a26`, legacy `TASK-221`, aliases `TASK-221`, local `CTL` / `21`

Convert the Tasks page default view from grouped raw tables to a compact action queue focused on owner work.

Acceptance criteria:

- /tasks defaults to owner-action grouping rather than epic grouping.
- The full task list is still reachable from /tasks via a filter, view mode, or expandable section.
- Rows do not include long unavailable-action lists by default.
- Each visible row has at most one primary action.
- Existing query filters for initiative, epic, status, search, group, and show_done keep working or have a compatible replacement.

### CTL-22 (TASK-222) — Add task details drawer

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_712758fa575f`, legacy `TASK-222`, aliases `TASK-222`, local `CTL` / `22`

Move task summary, stage, blockers, linked change, policy, generated files, and recent events into a details drawer or equivalent progressive detail panel.

Acceptance criteria:

- Default task rows are compact and no longer contain large policy summaries.
- Selecting or expanding a task reveals summary, stage, blockers, linked change, policy, and available actions.
- Full unavailable-action explanations are visible only in details.
- The first matching task can be inspected without relying on browser console behavior.
- No state-changing action is triggered by merely opening details.

### CTL-23 (TASK-223) — Add safe action confirm modal

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_21ea3eac7235`, legacy `TASK-223`, aliases `TASK-223`, local `CTL` / `23`

Add a reusable confirmation modal for owner actions while preserving the existing confirmed POST safety model.

Acceptance criteria:

- Run, Submit, Approve, Resume, Doctor, and repair/check forms can use the confirm modal.
- Action forms still post only to /actions.
- Required owner notes remain required when the underlying workflow requires them.
- The modal does not submit until the owner confirms.
- If JavaScript is unavailable, existing confirmation controls still protect the action.

### CTL-24 (TASK-224) — Redesign Pipeline as run monitor

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_8a19213a6b72`, legacy `TASK-224`, aliases `TASK-224`, local `CTL` / `24`

Redesign the Pipeline page around the current session, phase progress, live logs, next safe action, and compact queue preview.

Acceptance criteria:

- /pipeline first screen shows current session, current phase, next action, and health of the run.
- Running-session live logs remain accessible with existing endpoints.
- Policy and queue details are still available but not the dominant first-screen content.
- Restricted actions remain visually separated and confirmed.
- Pipeline session detail pages remain reachable.

### CTL-25 (TASK-225) — Convert Reviews to decision queue

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_c55c8882bbe7`, legacy `TASK-225`, aliases `TASK-225`, local `CTL` / `25`

Convert Reviews into an owner decision queue focused on approve, request changes, and inspect review packages.

Acceptance criteria:

- /reviews prioritizes tasks that need owner review decisions.
- Approve and Request Changes remain available only for eligible tasks.
- Verbose review data is accessible but not shown in every row by default.
- The review commands table remains available for diagnostics.
- Rows do not present unavailable actions as primary actions.

### CTL-26 (TASK-226) — Convert Evolution to change decision queue

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_42c8de7a2c80`, legacy `TASK-226`, aliases `TASK-226`, local `CTL` / `26`

Convert Evolution into an owner decision queue focused on creating, approving, accepting, rejecting, and inspecting Change Proposals.

Acceptance criteria:

- /evolution highlights ready Change Proposals that need approval.
- Approved and in-review changes show the correct next owner action or blocker.
- Create Change remains available for eligible tasks.
- Existing filters remain available or have a compatible compact replacement.
- Detailed affected files and impacts remain inspectable without bloating rows.

### CTL-27 (TASK-227) — Render Settings as policy control page

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_d130cc75914f`, legacy `TASK-227`, aliases `TASK-227`, local `CTL` / `27`

Refine Settings into a focused policy control page with clear sections, effective policy summary, and safe apply behavior.

Acceptance criteria:

- /settings is visually consistent with the owner shell.
- Existing settings fields and names remain submitted to ui.settings.apply.
- Locked controls remain locked and clearly marked.
- The default policy field is easier to understand than a raw text-only control when policy data is available.
- Apply Settings still requires explicit confirmation.

### CTL-28 (TASK-228) — Render Doctor as health center

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_23b5dc6ce709`, legacy `TASK-228`, aliases `TASK-228`, local `CTL` / `28`

Refine Doctor into a health center with compact status summary, grouped findings, and safe repair/check actions.

Acceptance criteria:

- /doctor remains the complete diagnostic page.
- Failing or warning findings are easier to scan than in the old flat table.
- Refresh Doctor remains a read/check action exposed safely.
- Repair/check actions still use confirmed /actions forms.
- No finding data is lost compared with the old doctor table.

### CTL-29 (TASK-229) — Align inspection pages with owner shell

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_01cba33064a0`, legacy `TASK-229`, aliases `TASK-229`, local `CTL` / `29`

Align Epics, Commit, Events, Generated, Commands, and Actions pages with the shared shell while keeping them as deep inspection pages.

Acceptance criteria:

- All non-primary pages visually match the shared owner shell.
- Each page still exposes the same existing diagnostic or low-level information.
- Actions page continues to use confirmed /actions forms.
- Commit page does not expose push or remote operations.
- No placeholder buttons or nonfunctional UI elements are introduced.

### CTL-30 (TASK-230) — Add owner UI regression tests

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_6528449aa4ee`, legacy `TASK-230`, aliases `TASK-230`, local `CTL` / `30`

Add regression tests that verify the Owner Cockpit shell, action queues, confirmation safety, and key Web Control Center routes.

Acceptance criteria:

- Tests cover at least Dashboard, Tasks, Pipeline, Reviews, Evolution, Settings, and Doctor route rendering.
- Tests verify sidebar or shared shell markers appear on rendered pages.
- Tests verify confirmation safety for at least one state-changing form.
- Tests verify restricted destructive git actions are not exposed.
- The targeted test file can be run locally without network access.

### CTL-31 (TASK-231) — Document Owner Cockpit workflow

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_b6e2538c4606`, legacy `TASK-231`, aliases `TASK-231`, local `CTL` / `31`

Update owner-facing documentation to describe the new Owner Cockpit layout, action queue, details panel, health summary, and safe action confirmation flow.

Acceptance criteria:

- Documentation names Dashboard as the Owner Cockpit daily entry point.
- Documentation explains current execution bar, Action Queue, health summary, details panel, and confirmation modal.
- Documentation does not claim non-MVP features such as command palette are implemented.
- Documentation points users to Tasks, Pipeline, Reviews, Evolution, Doctor, Events, Generated, Commands, Actions, Commit, and Epics for deeper workflows.
- No generated AI_PROJECT files are edited manually.

### CTL-32 (TASK-232) — Remove duplicate Tasks current execution panel

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_5ba735a21a32`, legacy `TASK-232`, aliases `TASK-232`, local `CTL` / `32`

Keep a single Current Execution entry point on /tasks by removing the duplicate full Current Execution panel below the filters.

Acceptance criteria:

- /tasks renders the Current Execution bar once and does not render the old execution-panel block.
- The no-current-task state still shows a clear next owner action in the top bar.
- The current-task state still shows task ref, status, next action, and safe controls in the top bar.
- Existing POST actions still route through /actions with confirmation.
- Web Control Center tests and project-control validations pass.

### CTL-33 (TASK-233) — Build compact task queue read model

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_a35d80fa956d`, legacy `TASK-233`, aliases `TASK-233`, local `CTL` / `33`

Add a compact /tasks queue read model that separates row fields from detailed task inspection data.

Acceptance criteria:

- The read model exposes compact task rows without embedding full task details in each row.
- The read model exposes task detail payloads keyed by task id, ref, or stable detail key.
- Full inventory data remains available for the inventory view.
- Missing optional detail fields render as controlled empty values instead of exceptions.
- Read-model tests cover at least one planned task, one blocked task, and one task with a linked Change.

### CTL-34 (TASK-234) — Render Tasks details drawer

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_0cc4b4b51e35`, legacy `TASK-234`, aliases `TASK-234`, local `CTL` / `34`

Replace inline task table expansion on /tasks with a right-side details drawer that shows selected task details without increasing row height.

Acceptance criteria:

- Opening task details no longer expands a table row into a large inline detail block.
- The action queue table keeps compact rows with only Task, Status, Title, Next, and Primary Action or Details columns.
- The drawer shows the selected task detail sections.
- A fallback path exists for viewing details when JavaScript is unavailable.
- Responsive layout remains usable on narrow screens.

### CTL-35 (TASK-235) — Fix Tasks action queue grouping

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_e07bf8c7ec5b`, legacy `TASK-235`, aliases `TASK-235`, local `CTL` / `35`

Classify /tasks Action Queue groups from available owner actions so runnable tasks do not fall into Other Active.

Acceptance criteria:

- A task with available Prepare for Codex or Run appears in Ready To Run, not Other Active.
- A task with available Approve Change appears in Needs Decision.
- An in_progress or selected current task appears in Current.
- A blocked task appears in Blocked.
- Deferred tasks are hidden from the primary queue by default and remain discoverable through explicit filters.
- Queue classification tests cover available actions rather than only task status.

### CTL-36 (TASK-236) — Add one primary task row action

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_52687710450e`, legacy `TASK-236`, aliases `TASK-236`, local `CTL` / `36`

Render one primary owner action per /tasks row and move unavailable-action explanations into the task details drawer.

Acceptance criteria:

- Each /tasks action queue row has at most one primary action button.
- Approve Change rows show an Approve or Open Change primary action instead of only generic navigation when direct approval is available.
- Ready To Run rows show Run, Prepare, or the existing safe execution action.
- Unavailable actions are not repeated inline in the table row.
- Mutating row actions still require confirmation and submit through the existing governed /actions path.

### CTL-37 (TASK-237) — Move policy summary to drawer and modal

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_5b3da4595c6d`, legacy `TASK-237`, aliases `TASK-237`, local `CTL` / `37`

Stop repeating Effective Policy summaries inside every task row and show policy details only in the drawer and confirmation modal.

Acceptance criteria:

- The /tasks action queue table does not render an Effective Run Policy block inside every row.
- The selected task drawer can show the effective policy summary.
- The confirmation modal shows policy context for mutating run or prepare actions when available.
- Existing policy summary content remains accurate.
- Tests verify policy summary placement.

### CTL-38 (TASK-238) — Consolidate task diagnostics in drawer

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_dfeb243913f6`, legacy `TASK-238`, aliases `TASK-238`, local `CTL` / `38`

Move Generated Files, Health, and Recent Events out of repeated task rows and into collapsed sections of the selected task drawer.

Acceptance criteria:

- Generated Files are not repeated inside every task table row.
- Health is not repeated as a full table for every task row.
- Recent Events are not repeated as a full list for every task row.
- The selected task drawer still provides access to generated files, health signals, and recent events.
- The compact global Project Health panel remains visible once on the page.

### CTL-39 (TASK-239) — Replace Tasks metrics with action counts

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_20a0c26c5bdd`, legacy `TASK-239`, aliases `TASK-239`, local `CTL` / `39`

Replace non-actionable /tasks metrics with owner-actionable counts for Needs Decision, Ready To Run, Current, Blocked, and Health Issues.

Acceptance criteria:

- The default /tasks metrics show Needs Decision, Ready To Run, Current, Blocked, and Health Issues.
- The default /tasks metrics do not emphasize done count as a primary owner-action metric.
- Metric counts match the rendered action queue groups.
- Metrics remain usable when there is no current task.
- Tests cover the action-count metrics.

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

Status: `done`
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

Status: `done`
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

Status: `done`
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

Status: `done`
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

Status: `done`
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

Status: `done`
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

### PIPEF-50 (TASK-129) — Add Codex preflight for UI Run

Status: `done`
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

### PIPEF-51 (TASK-130) — PIPE-046 Add phase history view helpers for Web Pipeline UI

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_548b331d6f92`, legacy `TASK-130`, aliases `TASK-130`, local `PIPEF` / `51`

Add Web UI helpers that normalize phase-based pipeline sessions from phase_history while preserving legacy steps fallback.

Acceptance criteria:

- A session with phase_history renders phase rows from phase_history instead of creating a fake planned step.
- A legacy session without phase_history continues to render through steps and gate_outcomes.
- Phase labels are stable and human-readable in the Web Pipeline UI.
- No existing Web Control Center tests regress.
- Focused tests cover both phase_history and legacy fallback rendering.

### PIPEF-52 (TASK-131) — PIPE-047 Render phase flow and current phase status in Web Pipeline UI

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_8a1c2d07282e`, legacy `TASK-131`, aliases `TASK-131`, local `PIPEF` / `52`

Render the new phase-based pipeline flow and current phase status in the Web Pipeline page.

Acceptance criteria:

- A PSESS-016-like session shows Queue passed, Prepare passed and Codex Execute failed.
- The session summary shows execute as the current failed phase when current_phase is execute.
- The UI no longer shows all checkpoints as planned when phase_history contains real outcomes.
- Legacy sessions still render their old gate flow.
- Tests assert the phase status labels in rendered HTML.

### PIPEF-53 (TASK-132) — PIPE-048 Render phase execution artifacts and failure evidence

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_7ab0576e73fe`, legacy `TASK-132`, aliases `TASK-132`, local `PIPEF` / `53`

Show phase execution artifacts, failure evidence and log snippets for failed phase-based pipeline sessions.

Acceptance criteria:

- A CODEX_ADAPTER_TIMEOUT phase shows CODEX_ADAPTER_TIMEOUT in the Web UI.
- The UI displays timeout_sec and duration_sec for failed execute phases.
- The UI displays command_ref for local Codex execution.
- Large stderr snippets are bounded by the existing Web UI log snippet limit.
- Tests cover rendering of execute_evidence and adapter artifacts.

### PIPEF-54 (TASK-133) — PIPE-049 Apply UI execution timeout settings to effective policy

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_a0392e704045`, legacy `TASK-133`, aliases `TASK-133`, local `PIPEF` / `54`

Allow UI settings to configure Codex execution timeout and preflight timeout for UI runs.

Acceptance criteria:

- UI settings can include execution_timeout_sec and the resolved UI policy uses it as codex.timeout_sec.
- String values such as "3600" are accepted for timeout settings.
- Invalid timeout values produce a stable UI settings or policy error.
- ui run --preflight uses preflight_timeout_sec from settings instead of hard-coded 30 seconds.
- command_line still overrides local_command and command_allowlist for UI runs.
- Existing UI settings and UI run tests pass.

### PIPEF-55 (TASK-134) — PIPE-050 Update Web Pipeline actions for phase-based sessions

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_1c8988bcc50b`, legacy `TASK-134`, aliases `TASK-134`, local `PIPEF` / `55`

Update Web Pipeline page actions and owner guidance for phase-based session states.

Acceptance criteria:

- Failed phase-based sessions do not appear as actively running in action guidance.
- The UI shows owner action guidance from session.next_action or latest phase next_action.
- Stop Session remains available only for stoppable session statuses.
- Resume or Run actions remain guarded by existing confirmation behavior.
- Tests cover action rendering for failed execute and blocked prepare sessions.

### PIPEF-56 (TASK-135) — PIPE-051 Document phase-based Web Pipeline display behavior

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_764223596ec1`, legacy `TASK-135`, aliases `TASK-135`, local `PIPEF` / `56`

Document how the Web Control Center displays phase-based pipeline sessions and timeout settings.

Acceptance criteria:

- Documentation explains phase_history-based Web Pipeline rendering.
- Documentation explains the difference between command_line and policy local_command.
- Documentation explains preflight timeout versus execution timeout.
- Documentation includes a troubleshooting note for CODEX_ADAPTER_TIMEOUT.
- Generated documentation checks can be rerun without manual edits to generated files.

### PIPEF-57 (TASK-136) — PIPE-052 Add pipeline session status JSON endpoint

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_3b24331932c4`, legacy `TASK-136`, aliases `TASK-136`, local `PIPEF` / `57`

Add a read-only JSON endpoint that returns compact live status for one pipeline session.

Acceptance criteria:

- The new endpoint returns JSON for an existing pipeline session.
- The JSON payload contains status, current_phase, current_phase_status, stop_reason, next_action and phase_history summary.
- The endpoint does not render full HTML.
- Missing sessions return a stable non-success response.
- Existing Web Control Center pages continue to render.

### PIPEF-58 (TASK-137) — PIPE-053 Add partial polling refresh to Pipeline session page

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_f9cb256de173`, legacy `TASK-137`, aliases `TASK-137`, local `PIPEF` / `58`

Update the Pipeline session page to poll compact session status and refresh only status-related UI blocks.

Acceptance criteria:

- Pipeline session pages include polling metadata for the current session.
- The page can refresh status from JSON without reloading the whole document.
- Polling interval is approximately two seconds.
- Polling stops for blocked, failed, completed or stopped sessions.
- The implementation uses standard browser APIs only.

### PIPEF-59 (TASK-138) — PIPE-054 Add Web action for single-task UI run

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_877f5512287c`, legacy `TASK-138`, aliases `TASK-138`, local `PIPEF` / `59`

Add a Web action that starts a single selected task through the effective UI run pipeline policy.

Acceptance criteria:

- The new Web action requires explicit confirmation.
- The action creates a single-task pipeline session for the selected task.
- The action uses the effective UI policy configured by UI settings.
- The action response exposes the created session id.
- Existing Web actions continue to pass their tests.

### PIPEF-60 (TASK-139) — PIPE-055 Render Run and Resume controls beside task rows

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_5d977a401b64`, legacy `TASK-139`, aliases `TASK-139`, local `PIPEF` / `60`

Add task-row controls that let the owner start or continue one selected task from the Web Tasks page.

Acceptance criteria:

- Runnable task rows show a confirmed Run form.
- In-progress task rows show continuation guidance or a supported Resume control.
- Terminal or inactive tasks do not show Run controls.
- Task row controls submit the selected task reference.
- Tests assert task-row action visibility for planned, ready, in_progress and done tasks.

### PIPEF-61 (TASK-140) — PIPE-056 Stream Codex adapter output to runtime log files

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_f1d62b78004f`, legacy `TASK-140`, aliases `TASK-140`, local `PIPEF` / `61`

Write Codex local-command stdout and stderr to session runtime log files while execution is running.

Acceptance criteria:

- Codex stdout is written to a per-session runtime stdout log during execution.
- Codex stderr is written to a per-session runtime stderr log during execution.
- Execute phase artifacts include enough metadata for the Web UI to locate log files.
- Existing captured stdout and stderr refs still work after command completion.
- Tests cover log writing for a local-command adapter run.

### PIPEF-62 (TASK-141) — PIPE-057 Add pipeline session live log tail endpoint

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_ed7c7c10d9eb`, legacy `TASK-141`, aliases `TASK-141`, local `PIPEF` / `62`

Add a read-only endpoint that returns appended chunks from a pipeline session runtime log.

Acceptance criteria:

- The endpoint can return the next chunk from a known session runtime log.
- The response includes the new offset and whether the stream is still running when available.
- Invalid stream names are rejected.
- Large responses are bounded by a fixed server-side limit.
- The endpoint cannot read files outside the session runtime log area.

### PIPEF-63 (TASK-142) — PIPE-058 Add live Codex log panel to Pipeline session page

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_163fe8b208a9`, legacy `TASK-142`, aliases `TASK-142`, local `PIPEF` / `63`

Display live stdout and stderr output for the current Codex execute phase in the Web Pipeline session page.

Acceptance criteria:

- A running execute phase shows a visible Codex Execute running status.
- The page can append new stdout or stderr chunks without a full reload.
- The log panel shows command_ref, elapsed time and timeout when available.
- Completed execute phases still show captured snippets.
- Tests assert that live log UI elements render for sessions with runtime log artifacts.

### PIPEF-64 (TASK-143) — PIPE-059 Keep runtime pipeline logs out of task diff gates

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_3b9b49da1c41`, legacy `TASK-143`, aliases `TASK-143`, local `PIPEF` / `64`

Ensure runtime UI and pipeline log files do not cause task verification diff gates to fail.

Acceptance criteria:

- Runtime log files under the chosen logs path do not appear as missing_from_report.
- Real source, test and documentation changes still require report coverage.
- Git ignore rules cover generated runtime log artifacts where appropriate.
- Tests cover runtime log exclusion and normal source diff blocking.
- The behavior is documented near the exclusion logic.

### PIPEF-65 (TASK-144) — PIPE-060 Document Web live status and Codex log behavior

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_065318711223`, legacy `TASK-144`, aliases `TASK-144`, local `PIPEF` / `65`

Document the Web UI live status refresh, task Run controls and Codex live log behavior for the owner.

Acceptance criteria:

- Documentation explains how to tell whether Codex is actually running.
- Documentation explains when to use task-row Run versus Resume Session.
- Documentation explains where live logs appear and what stdout versus stderr means.
- Documentation explains how to respond to REPORT_MISSING.
- Documentation explains that runtime logs should not be reported as implementation files.

### PIPEF-66 (TASK-145) — PIPE-061 Add Web Settings page route

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_432c3c726e2d`, legacy `TASK-145`, aliases `TASK-145`, local `PIPEF` / `66`

Add a Web Control Center Settings page that displays effective UI settings and their source file.

Acceptance criteria:

- The Web Control Center navigation includes a Settings page link.
- The Settings page shows the effective UI settings source and path.
- The Settings page renders command_line, default_policy and timeout settings when present.
- The Settings page is read-only in this task.
- Existing Web Control Center tests continue to pass.

### PIPEF-67 (TASK-146) — PIPE-062 Add confirmed Web actions for UI settings updates

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_644b6c563035`, legacy `TASK-146`, aliases `TASK-146`, local `PIPEF` / `67`

Add confirmed Web actions that update allowed project-local UI settings from the Settings page.

Acceptance criteria:

- Settings update actions require explicit confirmation.
- Only allowlisted setting keys can be updated through the Web UI.
- Successful updates write AI_PROJECT/config/ui_settings.json.
- Action results show the updated key and settings path.
- Tests cover successful update, missing confirmation and disallowed key behavior.

### PIPEF-68 (TASK-147) — PIPE-063 Add internal change-gate bypass UI setting

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_b678836b5b83`, legacy `TASK-147`, aliases `TASK-147`, local `PIPEF` / `68`

Add a disabled-by-default UI setting for explicitly bypassing approved Change requirements on internal project-control tasks.

Acceptance criteria:

- Effective UI settings include the new bypass setting with default false.
- String values such as true, false, 1 and 0 are parsed predictably.
- Invalid boolean values produce a stable settings error or validation failure.
- Existing UI settings behavior remains compatible.
- Tests cover the new setting defaults and parsing.

### PIPEF-69 (TASK-148) — PIPE-064 Render internal Change gate bypass checkbox

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_c3115928f476`, legacy `TASK-148`, aliases `TASK-148`, local `PIPEF` / `69`

Render a confirmed Settings page checkbox for toggling internal project-control Change gate bypass.

Acceptance criteria:

- The Settings page shows a checkbox for the internal Change gate bypass setting.
- The checkbox reflects the effective current setting value.
- Submitting the checkbox requires confirmation.
- The UI includes clear warning text about internal-only use.
- Tests cover checkbox rendering for enabled and disabled states.

### PIPEF-70 (TASK-149) — PIPE-065 Apply internal Change gate bypass to UI runs

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_e84bda130e82`, legacy `TASK-149`, aliases `TASK-149`, local `PIPEF` / `70`

Allow confirmed UI runs to skip approved Change requirements only for internal project-control tasks when the bypass setting is enabled.

Acceptance criteria:

- When the setting is disabled, UI runs still require an approved linked Change.
- When the setting is enabled, eligible internal project-control tasks can pass prepare without an approved linked Change.
- Non-internal tasks still block on missing approved Change even when the setting is enabled.
- Bypass usage is recorded in phase artifacts or audit details.
- Tests cover enabled, disabled and non-internal task behavior.

### PIPEF-71 (TASK-150) — PIPE-066 Document Web Settings and internal bypass behavior

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_98a41c988bbe`, legacy `TASK-150`, aliases `TASK-150`, local `PIPEF` / `71`

Document the Web Settings page and the internal Change gate bypass setting for the Human Owner.

Acceptance criteria:

- Documentation explains how to open and use the Web Settings page.
- Documentation explains the internal Change gate bypass setting and its risks.
- Documentation states that the bypass does not skip token, report, verify, review, close or commit gates.
- Documentation explains that the setting is off by default.
- Documentation validation and generated checks can be rerun after edits.

### PIPEF-72 (TASK-151) — PIPE-067 Add structured Codex report block to prompt package

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_66d6567e4211`, legacy `TASK-151`, aliases `TASK-151`, local `PIPEF` / `72`

Update Codex prompt generation so executors must finish with a machine-readable structured report block.

Acceptance criteria:

- Generated CODEX_PROMPT.md contains a clearly delimited machine-readable report JSON instruction.
- The required JSON fields include task identity, changed_files, generated_files, checks, warnings, blockers and token_usage.
- The prompt still tells Codex not to self-approve.
- Existing prompt sections for scope, allowed files and acceptance criteria remain intact.
- Focused tests verify the new final report contract appears in generated prompts.

### PIPEF-73 (TASK-152) — PIPE-068 Parse structured Codex report from stdout

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_5fa2f77182b7`, legacy `TASK-152`, aliases `TASK-152`, local `PIPEF` / `73`

Add a bounded parser that extracts a structured execution report JSON object from Codex stdout.

Acceptance criteria:

- A valid fenced report JSON block can be extracted from stdout.
- Missing report blocks produce a stable missing-report parse result.
- Duplicate report blocks are rejected rather than guessed.
- Malformed JSON is rejected with a stable error code.
- The parser does not read or write repository state.

### PIPEF-74 (TASK-153) — PIPE-069 Add task report submission service for pipeline use

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_27cdd9a118ba`, legacy `TASK-153`, aliases `TASK-153`, local `PIPEF` / `74`

Extract or add a reusable task report submission service that can be called without shelling out to taskctl.

Acceptance criteria:

- A structured report can be submitted through a reusable Python service.
- The existing task report CLI path continues to work.
- Invalid reports are rejected with stable validation errors.
- Successful submission updates latest_by_task for the selected task.
- Tests cover service submission and the CLI compatibility path.

### PIPEF-75 (TASK-154) — PIPE-070 Auto-submit parsed Codex report in local-command adapter

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_b8872924f7e8`, legacy `TASK-154`, aliases `TASK-154`, local `PIPEF` / `75`

Make the local-command Codex adapter submit a parsed structured report automatically after successful execution.

Acceptance criteria:

- A successful local-command run with a valid structured report auto-submits a task report.
- The adapter result includes the new report_id and passes instead of blocking on report missing.
- A successful local-command run without a structured report still blocks with CODEX_ADAPTER_REPORT_MISSING.
- Malformed structured report output produces a stable blocked or failed adapter result with evidence.
- Tests cover auto-submit success and missing-report fallback.

### PIPEF-76 (TASK-155) — PIPE-071 Add pipeline regression test for Run report auto-collection

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_d572bda0c446`, legacy `TASK-155`, aliases `TASK-155`, local `PIPEF` / `76`

Add an end-to-end regression test proving a UI Run session can proceed past collect-report when Codex emits a valid report.

Acceptance criteria:

- The regression test uses a fake local-command runner, not real Codex.
- A valid emitted report allows collect-report to pass.
- The test verifies the report id is stored and linked to the selected task.
- A no-report runner still produces CODEX_ADAPTER_REPORT_MISSING.
- Existing pipeline tests continue to pass.

### PIPEF-77 (TASK-156) — PIPE-072 Add Web recovery action for report missing sessions

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_4c8053ef44b5`, legacy `TASK-156`, aliases `TASK-156`, local `PIPEF` / `77`

Add a Web owner action that creates a draft structured report from captured Codex output for REPORT_MISSING sessions.

Acceptance criteria:

- REPORT_MISSING session pages show a report recovery action.
- The recovery action requires explicit owner confirmation.
- The generated draft report contains selected task id, task ref, changed_files, checks, warnings and token_usage.
- The UI warns when values are inferred from captured Codex output.
- After submission, the owner is guided to rerun collect-report.

### PIPEF-78 (TASK-157) — PIPE-073 Document Codex structured report auto-submit

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_6ac4e09604aa`, legacy `TASK-157`, aliases `TASK-157`, local `PIPEF` / `78`

Document how Codex structured reports are emitted, parsed, auto-submitted and recovered in Web UI.

Acceptance criteria:

- Documentation explains the final structured report block expected from Codex.
- Documentation explains when the adapter auto-submits a report.
- Documentation explains why free-text summaries are not enough for collect-report.
- Documentation explains the manual or Web recovery path for REPORT_MISSING sessions.
- Documentation validation and generated checks can be rerun after edits.

### PIPEF-79 (TASK-158) — PIPE-074 Allow internal bypass setting in Web settings action

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_183a81f45e29`, legacy `TASK-158`, aliases `TASK-158`, local `PIPEF` / `79`

Allow the Web UI settings action to update the existing internal Change gate bypass setting.

Acceptance criteria:

- The Web settings action no longer rejects allow_internal_change_gate_bypass with WEB_UI_SETTING_KEY_NOT_ALLOWED.
- The Web settings action can persist allow_internal_change_gate_bypass=true.
- The Web settings action can persist allow_internal_change_gate_bypass=false.
- Unknown setting keys are still rejected with WEB_UI_SETTING_KEY_NOT_ALLOWED.
- The allowed keys metadata includes allow_internal_change_gate_bypass.
- Focused Web Control Center tests pass.

### PIPEF-80 (TASK-161) — Make Codex Review optional in pipeline

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_4de2bd4cbb90`, legacy `TASK-161`, aliases `TASK-161`, local `PIPEF` / `80`

Allow the pipeline to skip semantic Codex Review when `require_codex_review` is false while keeping Machine Review required.

Acceptance criteria:

- When `require_codex_review=true`, existing Codex Review APPROVE requirements remain unchanged.
- When `require_codex_review=false`, review phase records `status=skipped` and does not build or return a Codex Review prompt.
- Machine Review remains required before close and cannot be bypassed by disabling Codex Review.
- Close phase accepts skipped Codex Review only when the effective policy disables Codex Review.
- Local commit readiness does not block on missing Codex Review only when the effective policy disables Codex Review.
- Tests prove that disabling Codex Review does not disable Report Gate or Machine Review.

### PIPEF-81 (TASK-162) — Add shared UI run queue builder

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_0cae31448c4c`, legacy `TASK-162`, aliases `TASK-162`, local `PIPEF` / `81`

Create one shared builder for UI single-task pipeline queue metadata so CLI and Web Run paths use the same session contract.

Acceptance criteria:

- An importable helper builds the UI single-task selected_queue payload with created_by_command=ui.run, ui_run_confirmed, task_refs, max_tasks=1, order_by=selected, include_blocked_tasks, and allow_internal_change_gate_bypass.
- `scripts/aictl.py ui run` uses the shared helper instead of maintaining a separate local queue-builder implementation.
- Existing CLI UI run behavior remains unchanged for confirmed and unconfirmed runs.
- Tests verify that the helper returns the expected bypass metadata when allow_internal_change_gate_bypass is true and false.
- Existing UI settings and UI run tests pass.

### PIPEF-82 (TASK-163) — Propagate UI Run queue metadata in Web action

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_1f7e652fa9b0`, legacy `TASK-163`, aliases `TASK-163`, local `PIPEF` / `82`

Make the Web Run button create pipeline sessions with the same UI single-task queue metadata as CLI `ui run`.

Acceptance criteria:

- Posting Web action `ui.run_selected_task` creates a session whose selected_queue includes created_by_command=ui.run and ui_run_confirmed=true.
- When allow_internal_change_gate_bypass=true in UI settings, Web Run session selected_queue includes allow_internal_change_gate_bypass=true.
- When allow_internal_change_gate_bypass=false in UI settings, Web Run session selected_queue includes allow_internal_change_gate_bypass=false.
- Web Run still returns session_href and redirect_target for the created session.
- Existing Web Control Center tests pass.

### PIPEF-83 (TASK-164) — Fix pipeline report template normalized fields

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_e663c259db22`, legacy `TASK-164`, aliases `TASK-164`, local `PIPEF` / `83`

Fix the pipeline report template so generated task report JSON can be submitted without schema errors.

Acceptance criteria:

- pipeline report template output no longer contains reported_task_id or reported_task_ref.
- The generated template still contains schema_version, task_id, task_ref, implementation_summary, changed_files, generated_files, checks, warnings, blockers, notes, owner_decision_required, and token_usage when required by submission/parsing rules.
- Submitting a minimally completed generated template through task report validation no longer fails with unknown reported_task_id or reported_task_ref fields.
- Existing task report normalization continues to persist reported_task_id and reported_task_ref internally after successful submission where applicable.
- Focused tests cover the template output and schema compatibility.
- Relevant project-control validation or focused pytest commands pass.

### PIPEF-84 (TASK-165) — Record running execute state before Codex starts

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_562c6ea22585`, legacy `TASK-165`, aliases `TASK-165`, local `PIPEF` / `84`

Record live execute phase and step state before launching the long-running Codex adapter so Web can display Codex Execute as running.

Acceptance criteria:

- During an active execute phase, the pipeline session records current_phase as execute and current_phase_status as running before Codex adapter completion.
- During an active execute phase, the session records a running current_step or equivalent live-step evidence for the selected task.
- The running execute evidence includes task id, command reference or adapter mode, and expected runtime log path metadata sufficient for Web display.
- After Codex completes, the final execute phase outcome is still recorded as passed, blocked, or failed with existing adapter artifacts preserved.
- Existing prepare, collect-report, verify, and run-until-blocker behavior remains compatible.
- Focused tests cover running-state recording before adapter completion and final-state cleanup after adapter completion.

### PIPEF-85 (TASK-166) — Add Codex execution summary block contract

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_d67b3fc03dcc`, legacy `TASK-166`, aliases `TASK-166`, local `PIPEF` / `85`

Introduce a minimal Codex execution summary block so Codex reports only implementation summary, notes, warnings, and blockers instead of full task reports.

Acceptance criteria:

- Codex prompt output asks for a minimal execution summary block rather than a full structured TaskReport.
- The parser accepts only implementation_summary, notes, warnings, and blockers.
- Malformed or unknown-field summary blocks produce stable parser errors.
- Existing Codex prompt build tests continue to pass.
- Focused parser tests cover the new summary block contract.

### PIPEF-86 (TASK-167) — Add evidence-based task report builder

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_8af8c1dfb7bc`, legacy `TASK-167`, aliases `TASK-167`, local `PIPEF` / `86`

Add a pipeline report builder that creates valid TaskReport payloads from session, task, adapter, summary, and policy evidence.

Acceptance criteria:

- The builder produces a valid TaskReport payload for a successful Codex adapter result.
- The builder uses task state for task_id and task_ref even if AI summary omits them.
- The builder never emits invalid check result values such as not_run.
- The builder defaults token_usage to an allowed object when precise token evidence is unavailable.
- Focused tests validate the generated payload with the existing task report validation service.

### PIPEF-87 (TASK-168) — Wire Codex auto-submit through report builder

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_d47e0c8dbb5a`, legacy `TASK-168`, aliases `TASK-168`, local `PIPEF` / `87`

Change the Codex local-command adapter to auto-submit reports built by code from evidence and the AI summary block.

Acceptance criteria:

- Codex auto-submit succeeds when the AI summary block is valid and adapter evidence is successful.
- Invalid Codex check enums cannot break auto-submit because checks are code-generated.
- Missing or malformed summary blocks produce a clear adapter blocker with a stable code.
- Auto-submit artifacts record the built report id and relevant builder evidence.
- Existing local-command adapter behavior for stdout, stderr, and runtime logs remains intact.

### PIPEF-88 (TASK-169) — Add optional git diff verification gates

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_e4f8444c37a1`, legacy `TASK-169`, aliases `TASK-169`, local `PIPEF` / `88`

Add a pipeline policy switch that can disable git diff, protected-files, and allowed-files verification gates for relaxed runs.

Acceptance criteria:

- Existing policies default to strict git diff verification behavior.
- A policy with git diff gates disabled can pass verify after a valid report without checking the full dirty working tree.
- Strict policies still block on missing_from_report and out-of-scope git diff mismatches.
- Verify artifacts clearly show when git diff based gates were skipped by policy.
- Focused verify tests cover both strict and relaxed policy behavior.

### PIPEF-89 (TASK-170) — Expose relaxed git diff mode for UI runs

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_ff58e46626af`, legacy `TASK-170`, aliases `TASK-170`, local `PIPEF` / `89`

Expose a UI-run setting that can apply relaxed git diff verification to fast-lane Web and UI task runs.

Acceptance criteria:

- The new UI setting is accepted by CLI and Web settings update actions.
- The Web Settings page shows the setting and explains that strict verification remains available.
- Effective UI policy snapshots reflect relaxed git diff verification only when the setting is enabled.
- Non-UI policy resolution keeps strict git diff verification by default.
- Focused Web and UI policy tests cover the setting.

### PIPEF-90 (TASK-171) — Update legacy Codex prompt report contract test

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_88c093931c3e`, legacy `TASK-171`, aliases `TASK-171`, local `PIPEF` / `90`

Update the legacy prompt contract test to match the new minimal Codex execution summary contract.

Acceptance criteria:

- Legacy prompt contract test no longer expects the old full CODEX_REPORT_JSON report block.
- Prompt tests verify the minimal CODEX_EXECUTION_SUMMARY_JSON contract.
- Focused Codex prompt tests pass.

### PIPEF-91 (TASK-172) — Add report warning verify policy

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_09e4331fcf23`, legacy `TASK-172`, aliases `TASK-172`, local `PIPEF` / `91`

Add a pipeline verify policy flag that controls whether structured report warnings block verification.

Acceptance criteria:

- Strict/default policy still blocks verify when the report gate returns CODEX_REPORT_WARN.
- Relaxed policy allows verify to continue when the only report gate issue is a warning.
- Verify artifacts record the report warning status and relaxed warning policy decision.
- Report gate failures remain blocking in both strict and relaxed modes.
- Focused verify phase tests cover strict and relaxed report warning behavior.

### PIPEF-92 (TASK-173) — Wire relaxed report warnings into UI policy

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_0becf52f7359`, legacy `TASK-173`, aliases `TASK-173`, local `PIPEF` / `92`

Add a project-local UI setting that maps relaxed report warning behavior into the effective UI pipeline policy.

Acceptance criteria:

- Default UI settings keep report warning blocking enabled unless explicitly relaxed.
- Setting allow_relaxed_report_warnings to true makes the effective UI policy treat report warnings as advisory.
- The new setting is allowlisted for Web write actions.
- Existing allow_relaxed_git_diff_verification behavior is unchanged.
- Focused UI policy tests pass.

### PIPEF-93 (TASK-174) — Expose relaxed report warnings setting

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_167499a73167`, legacy `TASK-174`, aliases `TASK-174`, local `PIPEF` / `93`

Expose the relaxed report warning setting on the Web Settings page and cover it with Web Control Center tests.

Acceptance criteria:

- Settings page shows allow_relaxed_report_warnings with explanatory copy.
- Unchecked rendering is shown when the setting is false or absent.
- Checked rendering is shown when the setting is true.
- Submitting Settings can update allow_relaxed_report_warnings.
- Focused Web Control Center tests pass.

### PIPEF-94 (TASK-175) — PIPE-094 Add report warning verify policy flag

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_4b64732575a7`, legacy `TASK-175`, aliases `TASK-175`, local `PIPEF` / `94`

Add an explicit verify policy flag that controls whether structured Codex report warnings may pass verify.

Acceptance criteria:

- PipelinePolicy.default().verify.allow_report_warnings is false.
- PipelinePolicy.to_dict() omits verify.allow_report_warnings when it is false by default.
- PipelinePolicy.to_dict() includes verify.allow_report_warnings when it is explicitly true.
- PipelinePolicy.from_dict() restores allow_report_warnings correctly from a policy snapshot.
- Non-boolean verify.allow_report_warnings is rejected by policy validation or parsing.
- Existing run_git_diff_gates tests continue to pass without semantic changes.

### PIPEF-95 (TASK-176) — PIPE-095 Allow report warnings in verify when policy permits

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_a82be276b7a5`, legacy `TASK-176`, aliases `TASK-176`, local `PIPEF` / `95`

Update verify so CODEX_REPORT_WARN can pass only when verify.allow_report_warnings is explicitly enabled.

Acceptance criteria:

- A report with warnings still blocks verify when allow_report_warnings is false.
- A report with warnings passes verify when allow_report_warnings is true and git diff, protected-files, and allowed-files gates pass.
- A report with warnings passes verify when allow_report_warnings is true and git diff gates are skipped by policy.
- A report with warnings still blocks if another enabled gate fails.
- Verify artifacts distinguish report_gate_warn_blocks_verify from report_gate_warnings_allowed_by_policy.
- Focused verify phase tests cover both strict and allowed report-warning paths.

### PIPEF-96 (TASK-177) — PIPE-096 Wire report warning policy into UI settings

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_4ea27c95cccf`, legacy `TASK-177`, aliases `TASK-177`, local `PIPEF` / `96`

Add a UI setting that maps directly to verify.allow_report_warnings without affecting relaxed git-diff verification.

Acceptance criteria:

- Default UI settings include allow_report_warnings=false.
- String and boolean values for allow_report_warnings are normalized consistently with other boolean settings.
- Invalid allow_report_warnings values are rejected with the existing UI boolean error path.
- resolve_pipeline_policy_from_settings sets verify.allow_report_warnings only from allow_report_warnings.
- allow_relaxed_git_diff_verification continues to control only verify.run_git_diff_gates.
- Focused UI policy tests cover true, false, and independence from relaxed git-diff verification.

### PIPEF-97 (TASK-178) — PIPE-097 Expose report warnings toggle in Control Center

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_67327ed51512`, legacy `TASK-178`, aliases `TASK-178`, local `PIPEF` / `97`

Expose allow_report_warnings in the web control surface so UI-created pipeline sessions can opt into report-warning pass behavior.

Acceptance criteria:

- Control Center exposes allow_report_warnings as a separate setting from relaxed git-diff verification.
- Submitting the setting writes allow_report_warnings to the project UI settings file through existing guarded actions.
- The web read model returns the effective allow_report_warnings value.
- Existing allow_relaxed_git_diff_verification behavior is unchanged.
- Web tests cover display and update of allow_report_warnings.
- Focused web control tests pass.

### PIPEF-98 (TASK-179) — PIPE-098 Add report warning pipeline regression coverage

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_0ed311b8994a`, legacy `TASK-179`, aliases `TASK-179`, local `PIPEF` / `98`

Add an end-to-end regression test proving a UI-resolved policy can carry allow_report_warnings into verify and pass a warning report.

Acceptance criteria:

- Regression tests fail against the old behavior where CODEX_REPORT_WARN always blocks verify.
- Regression tests pass when allow_report_warnings=true is carried into the policy snapshot.
- Regression tests confirm allow_relaxed_git_diff_verification alone does not allow report warnings.
- Regression tests confirm allow_report_warnings=false preserves strict blocking behavior.
- The tests are bounded and do not invoke real Codex.
- Focused pipeline tests pass.

### PIPEF-99 (TASK-180) — Add report gate downstream policy helper

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_ff42792e6d6e`, legacy `TASK-180`, aliases `TASK-180`, local `PIPEF` / `99`

Add a shared policy-aware helper that decides whether a report gate result may continue to downstream pipeline phases.

Acceptance criteria:

- A shared helper returns allow=true for CODEX_REPORT_PASS.
- The helper returns allow=true for CODEX_REPORT_WARN only when the policy allows advisory report warnings.
- The helper returns allow=false for CODEX_REPORT_WARN when advisory report warnings are disabled.
- The helper returns allow=false for report gate FAIL results.
- Focused unit tests cover all acceptance branches.

### PIPEF-100 (TASK-181) — Use shared report gate helper in verify phase

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_ae9a87d05290`, legacy `TASK-181`, aliases `TASK-181`, local `PIPEF` / `100`

Refactor verify phase to use the shared report gate acceptance helper without changing existing verify outcomes.

Acceptance criteria:

- Verify still passes a report warning when the policy allows advisory report warnings.
- Verify still blocks a report warning when the policy does not allow advisory report warnings.
- Verify still blocks report gate FAIL results.
- Existing git diff gate skip artifacts remain unchanged.
- Focused verify tests pass.

### PIPEF-101 (TASK-182) — Allow advisory report warnings in review phase

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_b44abaa8f7b7`, legacy `TASK-182`, aliases `TASK-182`, local `PIPEF` / `101`

Update review phase revalidation so a verified advisory report warning does not block review when policy allows it.

Acceptance criteria:

- Review no longer blocks with REPORT_GATE_NOT_PASSED_AFTER_VERIFY for the same verified report when advisory report warnings are allowed.
- Review still blocks with REPORT_GATE_NOT_PASSED_AFTER_VERIFY when advisory report warnings are disabled.
- Review still blocks with REPORT_CHANGED_AFTER_VERIFY when the latest report id differs from the verified report id.
- Review still blocks report gate FAIL results.
- Focused review tests pass.

### PIPEF-102 (TASK-183) — Add verify-to-review advisory warning pipeline regression

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_ae36b784755b`, legacy `TASK-183`, aliases `TASK-183`, local `PIPEF` / `102`

Add an end-to-end pipeline regression proving advisory report warnings pass verify and do not block review.

Acceptance criteria:

- The regression fails on the old strict review behavior.
- The regression passes after review uses the shared report warning policy.
- The test does not run external Codex.
- The test asserts both verify and review phase outcomes.
- Focused pipeline/review tests pass.

### PIPEF-103 (TASK-184) — Require auto-close owner note at session creation

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_ce339d5882a1`, legacy `TASK-184`, aliases `TASK-184`, local `PIPEF` / `103`

Auto-close pipeline sessions must fail before execution when no Human Owner auto-close note is provided.

Acceptance criteria:

- Creating a session with closure.auto_close_task enabled and no auto-close note fails before any phase execution can start.
- The failure uses a stable, explicit code such as AUTO_CLOSE_OWNER_NOTE_REQUIRED or PIPELINE_AUTO_CLOSE_OWNER_NOTE_REQUIRED.
- Creating the same auto-close session with an owner note succeeds and stores the note in policy_snapshot.closure.owner_approval_note.
- Policies without auto-close enabled can still create sessions without an auto-close note.
- Focused tests covering missing and present auto-close notes pass.

### PIPEF-104 (TASK-185) — Add auto-close note to CLI UI run

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_42b9b31f1758`, legacy `TASK-185`, aliases `TASK-185`, local `PIPEF` / `104`

The ui run command must accept a Human Owner auto-close note and pass it into the created pipeline session.

Acceptance criteria:

- python scripts/aictl.py ui run accepts --auto-close-note as an explicit owner-supplied argument.
- When an auto-close policy is selected and the note is blank, ui run stops before session execution and before any Codex adapter call.
- When an auto-close policy is selected and the note is provided, the created session snapshot contains closure.owner_approval_note.
- Existing ui run behavior for non-auto-close policies remains unchanged.
- Focused tests for ui run note handling pass.

### PIPEF-105 (TASK-186) — Expose auto-close note in Web UI run

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_870cdc06115c`, legacy `TASK-186`, aliases `TASK-186`, local `PIPEF` / `105`

The Web Control Center selected-task run action must expose and forward a Human Owner auto-close note.

Acceptance criteria:

- The Web Control Center selected-task run UI exposes a clear auto-close owner note input.
- The ui.run_selected_task action passes auto_close_note into session creation or delegated ui run handling.
- Submitting an auto-close selected-task run without a note fails before Codex execution with a clear owner-action message.
- Submitting an auto-close selected-task run with a note creates a session whose policy snapshot contains the note.
- Existing web selected-task runs for non-auto-close policies remain unchanged.
- Focused Web Control Center tests pass.

### PIPEF-106 (TASK-187) — Cover auto-close owner note close path

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_4dd0cafae529`, legacy `TASK-187`, aliases `TASK-187`, local `PIPEF` / `106`

Regression tests must prove that owner-noted auto-close sessions do not fail close with CLOSE_OWNER_NOTES_REQUIRED.

Acceptance criteria:

- A missing owner note continues to produce CLOSE_OWNER_NOTES_REQUIRED at close.
- A present owner note reaches close without CLOSE_OWNER_NOTES_REQUIRED when all required prior evidence is valid.
- The test fixture does not require invoking the real Codex adapter.
- The test fixture does not require creating a real local git commit.
- Focused close-path regression tests pass.

### PIPEF-107 (TASK-188) — Document auto-close owner note workflow

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_7814abc39b10`, legacy `TASK-188`, aliases `TASK-188`, local `PIPEF` / `107`

Project control docs must explain when and how the Human Owner supplies auto-close notes for pipeline runs.

Acceptance criteria:

- Docs state that auto-close owner notes are explicit Human Owner approval inputs.
- Docs include a current CLI example using --auto-close-note.
- Docs mention the Web Control Center selected-task run owner note field.
- Docs preserve the rule that Codex cannot approve, accept, or fabricate owner notes.
- Documentation changes are limited to the auto-close owner-note workflow.

### PIPEF-108 (TASK-189) — Bound close workflow artifacts

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_3646704f7c34`, legacy `TASK-189`, aliases `TASK-189`, local `PIPEF` / `108`

Prevent close phase workflow evidence from storing oversized stdout or stderr strings in pipeline session state.

Acceptance criteria:

- A nested workflow step stdout or stderr longer than the pipeline state string limit is not stored verbatim in pipeline session state.
- Bounded artifacts retain enough data to identify the failed workflow, step id, command name, return code, and error message.
- Bounded artifacts record that stdout or stderr was truncated and expose original size metadata.
- pipeline validate passes after recording close phase artifacts containing previously oversized nested workflow output.
- Focused tests covering artifact bounding and close phase storage pass.

### PIPEF-109 (TASK-190) — Recover already closed close phase

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_b1678d19812f`, legacy `TASK-190`, aliases `TASK-190`, local `PIPEF` / `109`

Make pipeline close safely recover when a prior close attempt already moved the selected task to done but close evidence or commit did not finish.

Acceptance criteria:

- Retrying close for a task already done with approval notes does not fail only because task.submit_for_review cannot rerun.
- The retry path records an explicit already_closed_by_previous_attempt or equivalent recovery marker in close artifacts.
- The retry path does not re-run task approval workflows when the task is already done.
- The retry path still blocks if the task is done without usable owner approval evidence.
- Focused close phase recovery tests pass.

### PIPEF-110 (TASK-191) — Block execute on stale protected outputs

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_88a4271596df`, legacy `TASK-191`, aliases `TASK-191`, local `PIPEF` / `110`

Run protected/generated freshness checks before Codex execution so stale generated files block before spending Codex quota.

Acceptance criteria:

- If the protected/generated freshness check fails before execute, the execute phase records a blocked result before token budget or Codex adapter execution.
- The blocked execute artifact includes the protected check command, return code, compact stdout or parsed errors, and codex_adapter_called=false.
- If the protected check passes, existing execute phase token budget and Codex adapter behavior remain unchanged.
- A test proves stale generated output prevents Codex adapter invocation.
- Focused execute phase and runner tests pass.

### PIPEF-111 (TASK-192) — Add close artifact regression coverage

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_260eaac36dea`, legacy `TASK-192`, aliases `TASK-192`, local `PIPEF` / `111`

Add end-to-end regression tests for close artifact bounding, already-closed close retry, and stale-output pre-execute blocking.

Acceptance criteria:

- Tests fail against the old oversized close artifact behavior and pass after artifact bounding is implemented.
- Tests cover the already-done close retry path without requiring manual state edits.
- Tests cover pre-execute stale generated output blocking with Codex adapter not called.
- Focused test commands complete successfully without running unrelated long test suites.
- No production source files are modified by this task.

### PIPEF-112 (TASK-193) — Allow advisory report warnings in local commit

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_39229ef813d5`, legacy `TASK-193`, aliases `TASK-193`, local `PIPEF` / `112`

Make local commit readiness accept report gate WARN only when the session policy explicitly allows advisory report warnings.

Acceptance criteria:

- Local commit readiness passes report gate WARN when policy.verify.allow_report_warnings is enabled and all other readiness gates pass.
- Local commit readiness blocks report gate WARN when policy does not allow report warnings.
- Local commit readiness blocks report gate FAIL/BLOCKED regardless of advisory warning policy.
- Machine review, Codex review, task done, linked change acceptance, and dirty-file commit checks remain enforced.
- Focused tests covering allowed WARN and blocked WARN local commit readiness behavior pass.

### PIPEF-113 (TASK-194) — Document advisory warning commit behavior

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_a353ea7dcda0`, legacy `TASK-194`, aliases `TASK-194`, local `PIPEF` / `113`

Document that local commit uses the same advisory report warning policy as verify, review, and close.

Acceptance criteria:

- Documentation states that advisory report WARN can proceed to local commit only when policy explicitly allows it.
- Documentation states that report FAIL/BLOCKED and advisory-disabled WARN still block local commit.
- Documentation explains that COMMIT_REPORT_GATE_NOT_PASS means the commit gate rejected the report gate status.
- Documentation does not imply that Human Owner approval, machine review, Codex review, or dirty-file gates are bypassed.

### PIPEF-114 (TASK-195) — Allow advisory report warnings before local commit

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_1670c8cf4970`, legacy `TASK-195`, aliases `TASK-195`, local `PIPEF` / `114`

Make local commit readiness accept policy-approved advisory report warnings instead of requiring an unconditional Codex Report Gate PASS.

Acceptance criteria:

- Local commit readiness passes the report gate portion when the report gate is PASS.
- Local commit readiness accepts report gate WARN only when the active policy marks that warning advisory.
- Local commit readiness still blocks report gate FAIL and unapproved report gate WARN.
- Tests cover the new report gate acceptance helper or equivalent behavior.
- Existing local commit readiness behavior outside report warning handling remains unchanged.

### PIPEF-115 (TASK-196) — Allow safe Machine Review warnings before local commit

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_e094aa01c94b`, legacy `TASK-196`, aliases `TASK-196`, local `PIPEF` / `115`

Make local commit readiness accept Machine Review WARN only when all commit-critical checks are PASS and the remaining warnings are non-blocking or policy-approved.

Acceptance criteria:

- Machine Review PASS still allows local commit readiness to continue.
- Machine Review WARN can continue only when required commit checks are present and PASS.
- Machine Review WARN from unknown or blocking warning evidence still blocks local commit.
- Machine Review FAIL still blocks local commit.
- The local commit blocker reason distinguishes unsafe warnings from allowed advisory warnings.

### PIPEF-116 (TASK-197) — Cover close local commit with advisory warnings

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_7069b3a32755`, legacy `TASK-197`, aliases `TASK-197`, local `PIPEF` / `116`

Add regression coverage proving close can create a local commit when advisory warnings are policy-approved and all commit-critical checks pass.

Acceptance criteria:

- A close phase regression covers safe Machine Review WARN followed by local commit success.
- A close phase regression covers unsafe Machine Review WARN followed by local commit block.
- The regression does not require running the real Codex adapter.
- The test asserts the absence of COMMIT_MACHINE_REVIEW_NOT_PASS for safe advisory warning cases.
- Existing close phase tests still pass.

### PIPEF-117 (TASK-198) — Document local commit warning policy

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_60f7776130b7`, legacy `TASK-198`, aliases `TASK-198`, local `PIPEF` / `117`

Document when local commit accepts advisory warnings and when it must still block.

Acceptance criteria:

- Documentation states that local commit requires commit-critical checks to pass.
- Documentation explains that only explicit advisory warnings may be accepted before local commit.
- Documentation tells the owner to inspect local_commit.readiness when commit blocks.
- Documentation does not claim that Machine Review FAIL can be committed.
- Documentation generated-output checks pass after the update.

### PIPEF-118 (TASK-199) — Expose Web policy catalog

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_37f751883a93`, legacy `TASK-199`, aliases `TASK-199`, local `PIPEF` / `118`

Expose the registered built-in and custom pipeline policy presets to the Web read model for safe UI selection.

Acceptance criteria:

- The Web read model exposes a deterministic list of selectable pipeline policies.
- The catalog includes built-in presets and any valid custom presets from the policy store.
- Each catalog item includes enough summary data to explain review, close, commit, and batch behavior.
- Invalid custom policy store state still fails through existing validation paths.
- Existing Web Control Center tests continue to pass.

### PIPEF-119 (TASK-200) — Render policy dropdown in Settings

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_9fa89eb78438`, legacy `TASK-200`, aliases `TASK-200`, local `PIPEF` / `119`

Replace the Web Settings free-text default_policy field with a dropdown populated from registered pipeline policies.

Acceptance criteria:

- The Settings page no longer renders default_policy as a free-text input.
- The Settings page renders every registered policy preset as a selectable option.
- Submitting a known policy updates ui_settings.json through the existing settings action.
- Submitting an unknown policy through the Web action returns a controlled error.
- Existing settings such as command_line and review toggles continue to apply normally.

### PIPEF-120 (TASK-201) — Show effective policy summary

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_a4c612206665`, legacy `TASK-201`, aliases `TASK-201`, local `PIPEF` / `120`

Show an owner-facing effective pipeline policy summary in Web Settings and selected-run views.

Acceptance criteria:

- Owners can see the effective batch max_steps before starting a Web run.
- Owners can see whether Codex Review is required or skipped by the effective policy.
- Owners can see whether auto-close and local commit are enabled by the effective policy.
- Owners can see whether report warnings and git diff gates are strict or relaxed.
- The summary updates when the effective selected policy changes.

### PIPEF-121 (TASK-202) — Add Web run batch overrides

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_0ef9ca47e1d6`, legacy `TASK-202`, aliases `TASK-202`, local `PIPEF` / `121`

Add validated Web-run batch limit settings so selected task runs can reach review and close without hidden max_steps stops.

Acceptance criteria:

- A Web run can be configured with max_steps high enough to cover all seven pipeline phases.
- Invalid batch override values are rejected with controlled UI settings errors.
- If no override is set, existing policy defaults remain effective.
- The Settings page displays the configured batch overrides.
- Policy resolution tests cover default behavior and override behavior.

### PIPEF-122 (TASK-203) — Warn on incomplete Web run policy

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_6b1308ecd462`, legacy `TASK-203`, aliases `TASK-203`, local `PIPEF` / `122`

Warn owners before starting a Web run when the effective policy cannot reach review and close in one batch.

Acceptance criteria:

- A policy with max_steps below the full phase count shows a warning before Web Run starts.
- The warning names the expected stopping point risk: review and close may not run.
- The run action can still proceed only after explicit owner confirmation.
- A policy with sufficient max_steps does not show the incomplete-run warning.
- Tests cover both warning and no-warning cases.

### PIPEF-123 (TASK-204) — Document Web policy settings

Status: `done`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_e59dd0c01cbd`, legacy `TASK-204`, aliases `TASK-204`, local `PIPEF` / `123`

Document the improved Web Settings policy selector, effective policy summary, and batch run limit behavior.

Acceptance criteria:

- The usage guide explains that default_policy is selected from registered policy presets.
- The owner quickstart explains how to spot insufficient max_steps before starting a run.
- The docs explain the difference between Run selected task and Resume Session.
- The docs do not claim full autonomous completion when policy limits intentionally stop the session.
- Documentation validation and generated documentation checks pass.

### PIPEF-124 (TASK-205) — Expose Web policy catalog

Status: `planned`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_8f2ba8631f4c`, legacy `TASK-205`, aliases `TASK-205`, local `PIPEF` / `124`

Expose the registered built-in and custom pipeline policy presets to the Web read model for safe UI selection.

Acceptance criteria:

- The Web read model exposes a deterministic list of selectable pipeline policies.
- The catalog includes built-in presets and any valid custom presets from the policy store.
- Each catalog item includes enough summary data to explain review, close, commit, and batch behavior.
- Invalid custom policy store state still fails through existing validation paths.
- Existing Web Control Center tests continue to pass.

### PIPEF-125 (TASK-206) — Render policy dropdown in Settings

Status: `planned`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_f12e091f47df`, legacy `TASK-206`, aliases `TASK-206`, local `PIPEF` / `125`

Replace the Web Settings free-text default_policy field with a dropdown populated from registered pipeline policies.

Acceptance criteria:

- The Settings page no longer renders default_policy as a free-text input.
- The Settings page renders every registered policy preset as a selectable option.
- Submitting a known policy updates ui_settings.json through the existing settings action.
- Submitting an unknown policy through the Web action returns a controlled error.
- Existing settings such as command_line and review toggles continue to apply normally.

### PIPEF-126 (TASK-207) — Show effective policy summary

Status: `planned`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_92e534ba39e2`, legacy `TASK-207`, aliases `TASK-207`, local `PIPEF` / `126`

Show an owner-facing effective pipeline policy summary in Web Settings and selected-run views.

Acceptance criteria:

- Owners can see the effective batch max_steps before starting a Web run.
- Owners can see whether Codex Review is required or skipped by the effective policy.
- Owners can see whether auto-close and local commit are enabled by the effective policy.
- Owners can see whether report warnings and git diff gates are strict or relaxed.
- The summary updates when the effective selected policy changes.

### PIPEF-127 (TASK-208) — Add Web run batch overrides

Status: `planned`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_f0f89049f343`, legacy `TASK-208`, aliases `TASK-208`, local `PIPEF` / `127`

Add validated Web-run batch limit settings so selected task runs can reach review and close without hidden max_steps stops.

Acceptance criteria:

- A Web run can be configured with max_steps high enough to cover all seven pipeline phases.
- Invalid batch override values are rejected with controlled UI settings errors.
- If no override is set, existing policy defaults remain effective.
- The Settings page displays the configured batch overrides.
- Policy resolution tests cover default behavior and override behavior.

### PIPEF-128 (TASK-209) — Warn on incomplete Web run policy

Status: `planned`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_084920753b67`, legacy `TASK-209`, aliases `TASK-209`, local `PIPEF` / `128`

Warn owners before starting a Web run when the effective policy cannot reach review and close in one batch.

Acceptance criteria:

- A policy with max_steps below the full phase count shows a warning before Web Run starts.
- The warning names the expected stopping point risk: review and close may not run.
- The run action can still proceed only after explicit owner confirmation.
- A policy with sufficient max_steps does not show the incomplete-run warning.
- Tests cover both warning and no-warning cases.

### PIPEF-129 (TASK-210) — Document Web policy settings

Status: `deferred`
Priority: `1`
Verification: `standard`
Identity: uid `tsk_c80966a220c5`, legacy `TASK-210`, aliases `TASK-210`, local `PIPEF` / `129`

Document the improved Web Settings policy selector, effective policy summary, and batch run limit behavior.

Acceptance criteria:

- The usage guide explains that default_policy is selected from registered policy presets.
- The owner quickstart explains how to spot insufficient max_steps before starting a run.
- The docs explain the difference between Run selected task and Resume Session.
- The docs do not claim full autonomous completion when policy limits intentionally stop the session.
- Documentation validation and generated documentation checks pass.

### PIPEF-130 (TASK-211) — Preserve report file lists

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_5a0d9fe1d1c7`, legacy `TASK-211`, aliases `TASK-211`, local `PIPEF` / `130`

Preserve Codex summary changed_files and generated_files when building automatic task reports.

Acceptance criteria:

- A parsed Codex summary containing changed_files produces a task report with the same changed files.
- A parsed Codex summary containing generated_files produces a task report with the same generated files.
- Duplicate file paths from summary, session, and policy evidence are stored only once.
- Existing report builder behavior still works when the summary omits file lists.
- Focused report builder and Codex adapter tests pass.

### PIPEF-131 (TASK-212) — Refresh context before commit

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_1caf66c97cb8`, legacy `TASK-212`, aliases `TASK-212`, local `PIPEF` / `131`

Refresh generated Context Pack outputs after task close and before local commit readiness is evaluated.

Acceptance criteria:

- Close phase runs a governed context build for the selected task before attempting local commit.
- Generated context outputs are included as governed side effects for commit readiness file approval.
- If context refresh fails, close records a blocked phase with a clear context refresh blocker code.
- A stale CONTEXT_PACK.md or CONTEXT_STATUS.md no longer causes local commit readiness to fail after successful refresh.
- Focused close phase tests pass.

### PIPEF-132 (TASK-213) — Allow approved review warnings

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_236114b44fed`, legacy `TASK-213`, aliases `TASK-213`, local `PIPEF` / `132`

Allow local commit when Machine Review has only policy-approved report warnings and all commit-critical checks pass.

Acceptance criteria:

- Machine Review FAIL still blocks local commit.
- Machine Review WARN from codex_report_gate is allowed only when policy allows report warnings.
- Unknown blocking Machine Review WARN still blocks local commit.
- Required commit readiness checks still must exist and pass.
- Focused git commit readiness tests pass.

### PIPEF-133 (TASK-214) — Record commit review diagnostics

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_3f12a03cbb4e`, legacy `TASK-214`, aliases `TASK-214`, local `PIPEF` / `133`

Store compact Machine Review diagnostics in local commit readiness evidence when commit is blocked.

Acceptance criteria:

- A local commit blocked by Machine Review includes compact non-pass check diagnostics in local_commit artifacts.
- Diagnostics identify the exact failing check name such as context_check_generated.
- Diagnostics include bounded stdout_summary or stderr_summary without oversized pipeline state strings.
- Existing local commit success artifacts remain compatible.
- Focused pipeline and Web rendering tests pass.

### PIPEF-134 (TASK-215) — Prevent stale context commit regression

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_8b04a750e499`, legacy `TASK-215`, aliases `TASK-215`, local `PIPEF` / `134`

Add regression coverage for close-to-commit flow with context refresh, report file lists, and policy-approved warnings.

Acceptance criteria:

- Tests fail against the old stale-context local commit behavior and pass after the production fixes.
- Tests cover automatic report file lists reaching report gate and commit readiness.
- Tests cover Machine Review WARN allowed by policy without allowing Machine Review FAIL.
- Tests do not require network access or a live Codex process.
- Focused regression test commands complete successfully.

### PIPEF-135 (TASK-240) — Ignore nonblocking review warnings

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_cc7783c67519`, legacy `TASK-240`, aliases `TASK-240`, local `PIPEF` / `135`

Make local commit readiness ignore Machine Review warnings whose evidence is marked blocking=false.

Acceptance criteria:

- A Machine Review with report_declared_test warnings marked blocking=false no longer blocks local commit readiness.
- A Machine Review with codex_report_gate WARN passes commit readiness only when report warnings are accepted by policy.
- A Machine Review with any blocking FAIL still blocks local commit readiness.
- A Machine Review with an unapproved blocking WARN still blocks local commit readiness.
- The blocker reason no longer lists nonblocking warnings as unapproved warning evidence.
- Focused git commit readiness tests pass.

### PIPEF-136 (TASK-241) — Add nonblocking warning regression

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_3da4271deaee`, legacy `TASK-241`, aliases `TASK-241`, local `PIPEF` / `136`

Add regression coverage for close-to-commit flow with policy-approved report warning and nonblocking unsafe test warnings.

Acceptance criteria:

- Regression tests cover nonblocking unsafe report-declared test warnings during commit readiness.
- Regression tests cover policy-approved codex_report_gate WARN plus nonblocking report_declared_test WARN checks passing local commit readiness.
- Regression tests prove that a blocking unsafe test warning still blocks local commit readiness.
- Regression tests use fakes or fixtures and do not invoke a live Codex process.
- Focused pipeline commit and close tests pass.

### PIPEF-137 (TASK-242) — Separate warning diagnostics

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_0a8962b5f17b`, legacy `TASK-242`, aliases `TASK-242`, local `PIPEF` / `137`

Separate blocking and nonblocking Machine Review warning diagnostics in local commit artifacts.

Acceptance criteria:

- Local commit artifacts distinguish blocking non-pass checks from advisory non-pass checks.
- Nonblocking report_declared_test warnings appear as advisory diagnostics, not blocker evidence.
- Blocker reasons include only checks that can actually block commit readiness.
- Artifact strings remain bounded and do not violate pipeline state payload limits.
- Focused commit artifact and Web rendering tests pass.

### PIPEF-138 (TASK-243) — Add Web Run smoke artifact

Status: `done`
Priority: `1`
Verification: `light`
Identity: uid `tsk_47318e97bc6a`, legacy `TASK-243`, aliases `TASK-243`, local `PIPEF` / `138`

Create a tiny deterministic smoke artifact file to verify that the existing Web Run button can execute, close, and commit a simple task.

Acceptance criteria:

- tmp/run-smoke/web-run-smoke.md exists after execution.
- The file contains the exact marker WEB_RUN_SMOKE_OK.
- The file states that it is only a smoke artifact for testing the Web Run flow.
- The file content is deterministic and does not include timestamps, hostnames, random IDs, or environment-specific data.
- The implementation does not modify repository files outside tmp/run-smoke/web-run-smoke.md, excluding governed project-control state/events/generated artifacts produced by the runner itself.
- The task can be reviewed by reading the file and inspecting the final git diff.

### PIPEF-139 (TASK-244) — Add pipeline git status snapshot helper

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_e1ae911006d8`, legacy `TASK-244`, aliases `TASK-244`, local `PIPEF` / `139`

Add a reusable helper that captures, normalizes, and diffs git status snapshots for pipeline session file evidence.

Acceptance criteria:

- The helper can parse git status --short output into normalized repository-relative paths.
- The helper can compute after-minus-before dirty file deltas without including pre-existing dirty files.
- Modified, untracked, deleted, and renamed files are covered by tests.
- Existing commit safety rules are not relaxed by this helper alone.
- Focused tests for the new helper pass.

### PIPEF-140 (TASK-245) — Record Web Run session file baseline

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_2f7e1f3b111b`, legacy `TASK-245`, aliases `TASK-245`, local `PIPEF` / `140`

Store a git status baseline and session-owned file delta evidence for each selected Web Run session.

Acceptance criteria:

- A new selected-task session records the initial git dirty baseline.
- Session evidence can distinguish pre-existing dirty files from files changed during the session.
- Existing pipeline sessions without baseline data remain readable.
- Pipeline status output includes enough evidence for commit readiness to consume session-owned files.
- Focused session and runner tests pass.

### PIPEF-141 (TASK-246) — Capture Codex-created changed files

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_5dfe49a637f3`, legacy `TASK-246`, aliases `TASK-246`, local `PIPEF` / `141`

Make the execute/report path include files created or modified by Codex in structured report evidence.

Acceptance criteria:

- A file created by Codex inside task allowed_files appears in report changed_files evidence.
- A file changed by Codex outside task allowed_files is not silently approved.
- The report gate receives non-empty changed_files for a Codex-created smoke artifact.
- Existing reports that explicitly declare changed files still work.
- Focused execute/report builder tests pass.

### PIPEF-142 (TASK-247) — Approve session-owned control side effects for commit

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_59541eac288b`, legacy `TASK-247`, aliases `TASK-247`, local `PIPEF` / `142`

Allow commit readiness to include governed project-control side effects created by the current pipeline session while still blocking unrelated dirty files.

Acceptance criteria:

- Commit readiness approves governed project-control files that are proven to be changed by the current session.
- Commit readiness blocks project-control files that were dirty before the session baseline.
- Commit readiness blocks unrelated code or test files not owned by the current session.
- The target task artifact remains required through report or allowed file evidence.
- Focused git commit and close phase tests pass.

### PIPEF-143 (TASK-248) — Expose commit-blocked closed task state

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_a668d08766ae`, legacy `TASK-248`, aliases `TASK-248`, local `PIPEF` / `143`

Make the close phase clearly expose when a task was closed but local commit readiness failed.

Acceptance criteria:

- A close phase with local commit blocked leaves the pipeline session blocked with stop code COMMIT_READINESS_FAILED.
- Pipeline status data distinguishes completed-with-commit from done-but-commit-blocked.
- Owner next action tells how to resolve commit readiness blockers.
- Existing auto-close behavior still closes tasks only through governed workflows.
- Focused close phase and runner tests pass.

### PIPEF-144 (TASK-249) — Classify blocked Web Run results correctly

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_ac83675b9c1d`, legacy `TASK-249`, aliases `TASK-249`, local `PIPEF` / `144`

Render Web Action Result badges from pipeline outcome fields instead of only HTTP success or command ok.

Acceptance criteria:

- Action Result does not show PASS when the pipeline result has session_status blocked.
- NO_EXECUTABLE_TASK is displayed as a non-success outcome with a clear reason.
- COMMIT_READINESS_FAILED is displayed as COMMIT BLOCKED with next action text.
- Successful completed runs still display PASS.
- Focused Web Control Center tests pass.

### PIPEF-145 (TASK-250) — Make selected Web Run idempotent

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_859961037176`, legacy `TASK-250`, aliases `TASK-250`, local `PIPEF` / `145`

Prevent repeated Web Run submits from creating misleading sessions for already completed or active selected tasks.

Acceptance criteria:

- Running a done selected task does not create a new pipeline session.
- A repeated Run on an active task points the owner to the existing relevant session.
- A normal planned or ready selected task still creates and runs a session.
- The Web form is guarded against duplicate submit in the browser.
- Focused UI run and Web Control Center tests pass.

### PIPEF-146 (TASK-251) — Add Web Run local commit smoke test

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_c0d7f9739711`, legacy `TASK-251`, aliases `TASK-251`, local `PIPEF` / `146`

Add an end-to-end smoke test for selected Web Run creating an allowed artifact, closing the task, and creating a local commit.

Acceptance criteria:

- The smoke test uses a fake or controlled Codex adapter and does not require network access.
- The test fails if changed_files evidence for the task artifact is empty.
- The test fails if governed session side effects are treated as unrelated dirty files.
- The test fails if a blocked Web Run result renders as PASS.
- The focused smoke test passes locally.

### PIPEF-147 (TASK-252) — Verify Web Run commit smoke path

Status: `done`
Priority: `1`
Verification: `light`
Identity: uid `tsk_f3bdae22a7d9`, legacy `TASK-252`, aliases `TASK-252`, local `PIPEF` / `147`

Create a deterministic smoke artifact to verify that Web Run reaches local commit after pipeline commit fixes.

Acceptance criteria:

- tmp/run-smoke/web-run-final-smoke.md exists after execution.
- The file contains the exact marker WEB_RUN_FINAL_SMOKE_OK.
- The file states that it is only a smoke artifact for Web Run commit validation.
- The generated report evidence includes tmp/run-smoke/web-run-final-smoke.md as a changed file.
- Web Run reaches local commit without COMMIT_READINESS_FAILED.

### PIPEF-148 (TASK-253) — Verify Web Run clean commit path

Status: `done`
Priority: `1`
Verification: `light`
Identity: uid `tsk_dec6f940c56e`, legacy `TASK-253`, aliases `TASK-253`, local `PIPEF` / `148`

Create a deterministic smoke artifact to verify that Web Run reaches local commit from a clean worktree.

Acceptance criteria:

- tmp/run-smoke/web-run-clean-commit-smoke.md exists after execution.
- The file contains the exact marker WEB_RUN_CLEAN_COMMIT_OK.
- The file states that it is only a smoke artifact for Web Run local commit validation.
- The generated report evidence includes tmp/run-smoke/web-run-clean-commit-smoke.md as a changed file.
- Web Run reaches local commit without COMMIT_READINESS_FAILED.

### PIPEF-149 (TASK-254) — Verify Web Run clean commit path

Status: `done`
Priority: `1`
Verification: `light`
Identity: uid `tsk_ccbe7708be33`, legacy `TASK-254`, aliases `TASK-254`, local `PIPEF` / `149`

Create a deterministic smoke artifact to verify that Web Run reaches local commit from a clean worktree.

Acceptance criteria:

- tmp/run-smoke/web-run-clean-commit-smoke.md exists after execution.
- The file contains the exact marker WEB_RUN_CLEAN_COMMIT_OK.
- The file states that it is only a smoke artifact for Web Run local commit validation.
- The generated report evidence includes tmp/run-smoke/web-run-clean-commit-smoke.md as a changed file.
- Web Run reaches local commit without COMMIT_READINESS_FAILED.

### PIPEF-150 (TASK-255) — Verify Web Run clean commit path 2

Status: `done`
Priority: `1`
Verification: `light`
Identity: uid `tsk_9ec7dcfc19be`, legacy `TASK-255`, aliases `TASK-255`, local `PIPEF` / `150`

Create a new deterministic smoke artifact to verify that Web Run reaches local commit from a clean worktree.

Acceptance criteria:

- tmp/run-smoke/web-run-clean-commit-smoke-2.md exists after execution.
- The file contains the exact marker WEB_RUN_CLEAN_COMMIT_2_OK.
- The file states that it is only a smoke artifact for Web Run local commit validation.
- The generated report evidence includes tmp/run-smoke/web-run-clean-commit-smoke-2.md as a changed file.
- Web Run reaches local commit without COMMIT_READINESS_FAILED.

### PIPEF-151 (TASK-256) — Classify successful close after max steps

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_3b73f02c8ed4`, legacy `TASK-256`, aliases `TASK-256`, local `PIPEF` / `151`

Treat a pipeline session as completed when close passed and a local commit hash exists, even if the batch runner reaches max_steps immediately after close.

Acceptance criteria:

- A session with close status passed and a non-empty local commit hash is recorded and rendered as completed, not stopped.
- The user-facing Action Result no longer shows STOPPED for a successful close with a created local commit.
- The old MAX_STEPS_REACHED behavior still applies when max_steps is reached before successful close.
- Regression tests cover the PSESS-131 style case: close passed, commit hash present, max_steps exhausted.
- Focused tests for pipeline runner and Web Control Center pass.

### PIPEF-152 (TASK-257) — Demote recovered close workflow warnings

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_ca082da4761b`, legacy `TASK-257`, aliases `TASK-257`, local `PIPEF` / `152`

Hide recovered close-time context/protected check warnings from owner-facing output when post-close context refresh succeeds.

Acceptance criteria:

- Recovered contextctl.check-generated warnings are not shown as owner-facing warnings when post-close context_refresh succeeds.
- Recovered protected.check stale context or prompt warnings are not shown as owner-facing warnings when post-close context_refresh succeeds.
- Technical evidence still records that the non-blocking checks warned during close.
- Warnings remain owner-facing when post-close context_refresh fails, is missing, or does not repair the stale generated files.
- Focused close-phase, runner, and Web Control Center tests pass.

### PIPEF-153 (TASK-258) — Add dirty worktree preflight for Web Run

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_8b0e3a18a055`, legacy `TASK-258`, aliases `TASK-258`, local `PIPEF` / `153`

Prevent Web Run from starting when the repository has uncommitted changes before the selected task is executed.

Acceptance criteria:

- A clean worktree still allows ui.run_selected_task to start the selected planned or ready task normally.
- A dirty worktree returns not_run before Codex execution, before task transition, and before Evolution Change creation.
- The action result clearly states that Web Run did not start because the worktree is dirty.
- The action result includes dirty file paths from git status --short --untracked-files=all.
- The action result includes manual checkpoint commit commands for the owner.
- Tests cover clean and dirty worktree branches for ui.run_selected_task.

### PIPEF-154 (TASK-259) — Add confirmed checkpoint commit action

Status: `done`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_34590799287f`, legacy `TASK-259`, aliases `TASK-259`, local `PIPEF` / `154`

Add an owner-confirmed Web UI action that creates a checkpoint commit before Web Run starts.

Acceptance criteria:

- The checkpoint commit action is rejected when owner confirmation is missing.
- The checkpoint commit action reports not_run when the worktree is already clean.
- With confirmation and a dirty worktree, the action stages all current changes and creates a git commit.
- The action result includes the checkpoint commit hash and a next action to run the selected task again.
- The action does not execute Codex or transition any selected task.
- Tests cover missing confirmation, clean worktree, dirty worktree, and successful commit hash reporting.

### PIPEF-155 (TASK-260) — Link dirty preflight to checkpoint UX

Status: `done`
Priority: `2`
Verification: `strict`
Identity: uid `tsk_830b7b756514`, legacy `TASK-260`, aliases `TASK-260`, local `PIPEF` / `155`

Connect the dirty worktree preflight result to the confirmed checkpoint commit action in the Web UI.

Acceptance criteria:

- Dirty Web Run results show a checkpoint commit option when dirty files exist.
- The selected task remains visible in the dirty preflight result and next-action text.
- After checkpoint commit success, the result page points the owner back to running the same task.
- No automatic Web Run is started after checkpoint commit.
- Tests verify the dirty preflight to checkpoint commit UX path.

### PIPEF-156 (TASK-261) — Verify Web Run clean commit path 2

Status: `done`
Priority: `1`
Verification: `light`
Identity: uid `tsk_6bc6fb4a9e2a`, legacy `TASK-261`, aliases `TASK-261`, local `PIPEF` / `156`

Create a new deterministic smoke artifact to verify that Web Run reaches local commit from a clean worktree.

Acceptance criteria:

- tmp/run-smoke/web-run-clean-commit-smoke-2.md exists after execution.
- The file contains the exact marker WEB_RUN_CLEAN_COMMIT_2_OK.
- The file states that it is only a smoke artifact for Web Run local commit validation.
- The generated report evidence includes tmp/run-smoke/web-run-clean-commit-smoke-2.md as a changed file.
- Web Run reaches local commit without COMMIT_READINESS_FAILED.

### PIPEF-157 (TASK-262) — Continue batch after task commit

Status: `planned`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_8e16c65812a7`, legacy `TASK-262`, aliases `TASK-262`, local `PIPEF` / `157`

Allow the existing batch runner to continue to the next queued task after one task closes with a local commit.

Acceptance criteria:

- A single-task session still completes after close creates a local commit.
- A multi-task session does not complete after the first task commit when another queued task remains executable.
- The batch summary records the first task in completed_tasks and changed_tasks after committed close.
- The batch runner continues through run_next for the next queued task after the first committed close.
- Existing blocker and failure behavior remains unchanged.
- Focused tests cover both single-task and multi-task committed-close behavior.

### PIPEF-158 (TASK-263) — Enforce clean batch handoff

Status: `planned`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_852064edcb02`, legacy `TASK-263`, aliases `TASK-263`, local `PIPEF` / `158`

Stop a multi-task batch before the next task when the previous task did not leave a clean worktree after its local commit.

Acceptance criteria:

- After a committed task close with a clean worktree, the batch may continue to the next queued task.
- After a committed task close with remaining dirty files, the batch stops before executing the next task.
- The stop result uses a stable POST_TASK_DIRTY_WORKTREE code.
- The stop result includes dirty file paths for owner diagnostics.
- The stop result does not mark the remaining queued task as executed or changed.
- Tests cover clean handoff and dirty handoff cases.

### PIPEF-159 (TASK-264) — Build UI batch queue helper

Status: `planned`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_4ebaac010468`, legacy `TASK-264`, aliases `TASK-264`, local `PIPEF` / `159`

Add a Web UI queue builder that can create a selected queue for multiple tasks instead of one selected task.

Acceptance criteria:

- The new helper can build a queue with max_tasks greater than 1.
- The new helper can include epic_ids and statuses without requiring a single selected task_ref.
- The existing selected-task helper still returns max_tasks equal to 1.
- The produced queue uses only fields already understood by pipeline session creation and queue preview.
- Tests cover task_refs, epic/status selection, max_tasks, and order_by behavior.

### PIPEF-160 (TASK-265) — Add Web batch run action

Status: `planned`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_6dcf7d772c59`, legacy `TASK-265`, aliases `TASK-265`, local `PIPEF` / `160`

Add an owner-confirmed Web action that creates and runs a multi-task pipeline session using the existing batch runner.

Acceptance criteria:

- The ui.run_task_batch action is listed as an implemented confirmed Web action.
- The action can create a session with max_tasks greater than 1.
- The action delegates execution to the existing run_until_blocker function.
- The action result includes session_id, session_href, selected policy, and requested queue inputs.
- The selected-task ui.run_selected_task action remains unchanged for one-task runs.
- Tests cover action registration, argument handling, session creation, and run_until_blocker delegation.

### PIPEF-161 (TASK-266) — Block dirty Web batch starts

Status: `planned`
Priority: `1`
Verification: `strict`
Identity: uid `tsk_2377b93b98bc`, legacy `TASK-266`, aliases `TASK-266`, local `PIPEF` / `161`

Apply dirty worktree preflight to Web batch runs before any multi-task pipeline session is created or executed.

Acceptance criteria:

- A clean worktree allows ui.run_task_batch to create and run a batch session.
- A dirty worktree returns not_run before session creation and before Codex execution.
- The not_run result includes dirty file paths from git status.
- The not_run result includes owner guidance to create a checkpoint commit or clean the worktree.
- The existing ui.checkpoint_commit action remains usable after the dirty batch result.
- Tests cover clean and dirty batch-start preflight behavior.

### PIPEF-162 (TASK-267) — Auto-size Web batch max steps

Status: `planned`
Priority: `2`
Verification: `strict`
Identity: uid `tsk_a45e9597f0ee`, legacy `TASK-267`, aliases `TASK-267`, local `PIPEF` / `162`

Calculate a safe effective max_steps for Web batch runs so normal multi-task execution does not stop immediately after a successful close.

Acceptance criteria:

- A Web batch run with max_tasks 2 receives enough max_steps to pass two full task phase cycles in tests.
- A Web batch run with max_tasks 3 receives a larger effective max_steps than a one-task run.
- The effective max_steps calculation uses the current RUN_NEXT_PHASE_SEQUENCE length.
- The action result or policy snapshot makes the effective max_steps visible for diagnostics.
- Existing selected-task and direct pipeline behavior are not unintentionally loosened.
- Tests cover effective max_steps calculation and avoid false MAX_STEPS_REACHED after successful close.

### PIPEF-163 (TASK-268) — Add Web batch run form

Status: `planned`
Priority: `2`
Verification: `standard`
Identity: uid `tsk_1206afbf5ae2`, legacy `TASK-268`, aliases `TASK-268`, local `PIPEF` / `163`

Add an owner-facing Web form for starting multi-task batch runs from the Pipeline or Owner Cockpit UI.

Acceptance criteria:

- The Web UI exposes a visible Run task batch form.
- The form can submit max_tasks greater than 1 to ui.run_task_batch.
- The form supports epic/status-based batch selection and explicit task refs.
- The existing single-task Run UI remains available.
- Dirty batch preflight results display checkpoint commit guidance in the action result.
- Web rendering tests cover the presence and key fields of the batch form.

### PIPEF-164 (TASK-269) — Render batch run summary

Status: `planned`
Priority: `2`
Verification: `standard`
Identity: uid `tsk_ca7ccafa2696`, legacy `TASK-269`, aliases `TASK-269`, local `PIPEF` / `164`

Show a concise owner-facing summary of tasks, commits, blockers, and dirty handoff state after a Web batch run.

Acceptance criteria:

- A successful batch result shows each completed task and its commit hash when available.
- A partially stopped batch result shows the blocker code, blocker reason, and affected task id.
- POST_TASK_DIRTY_WORKTREE results show dirty handoff files in an owner-readable section.
- Technical JSON details remain available for debugging.
- Existing single-task action result rendering remains compatible.
- Tests cover completed batch, blocked batch, and dirty handoff summary rendering.

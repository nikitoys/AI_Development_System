<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Project Tasks

Revision: `109`
Current task: `TASK-013`

## Epic `EPIC-001`

### TASK-001 — Write Project Control Usage Guide

Status: `done`  
Priority: `1`  
Verification: `standard`  

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

Implement approved CHG-004 by creating the L4 Role-Agent Runtime Architecture source document and updating required README, operating model, roadmap, backlog and changelog references.

Acceptance criteria:

- ai-system/l4-role-agent-runtime.md exists and states L4 is an approved bounded implementation target.
- Document defines Python as strict API/control kernel, Controller Codex as planner/router/delegator/integrator and Codex role subagents as bounded role executors.
- Document maps existing role layers to concrete role-agent IDs.
- Document defines L4 execution flow from approved Task to Human Owner acceptance and conceptual scripts/agentctl.py API surface without implementing it.
- Document distinguishes L3, L4 and L5 and forbids automatic merge, push, PR creation, final acceptance and QA/review closure.
- Operating model, roadmap, backlog, changelog and README/index references are updated.
- Required validation passes and protected AI_PROJECT files are not manually edited.

## Epic `EPIC-002`

### TASK-002 — Document Skills Layer Roadmap

Status: `done`  
Priority: `1`  
Verification: `standard`  

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

### TASK-012 — TIG-01 Document task identity and execution graph design

Status: `done`  
Priority: `1`  
Verification: `standard`  

Define the target model for task uid, human ref, legacy aliases, epic keys, dependency graph, executable queue, and migration rules before implementation.

Acceptance criteria:

- A clear source-of-truth design exists.
- The design states that task IDs do not imply execution order.
- The design states that epics may execute in parallel by default.
- The design defines explicit dependencies as the only cross-epic ordering mechanism.
- The design includes migration rules for existing TASK-XXX tasks.
- Generated project-control files are refreshed through CLI.

### TASK-013 — TIG-02 Add epic keys to plan model ⭐

Status: `in_review`  
Priority: `1`  
Verification: `standard`  

Add stable short epic keys to the plan model so task refs can use readable prefixes such as TIG-01 or ACP-02.

Acceptance criteria:

- Existing plan validation still passes.
- Existing epics without keys are handled safely or migrated according to the design.
- New epics can have unique keys.
- Duplicate keys are rejected.

### TASK-014 — TIG-03 Add task uid ref local sequence and aliases

Status: `planned`  
Priority: `1`  
Verification: `standard`  

Extend task state with stable uid, human-readable ref, local sequence inside epic, and aliases for backward compatibility.

Acceptance criteria:

- Existing tasks can be migrated or read without losing history.
- New tasks receive readable refs.
- Legacy TASK-XXX references remain resolvable.

### TASK-015 — TIG-04 Add task reference resolver

Status: `planned`  
Priority: `1`  
Verification: `standard`  

Allow taskctl and prompt generation to resolve tasks by new ref, uid, or legacy TASK-XXX alias.

Acceptance criteria:

- Existing CLI commands keep working with legacy TASK-XXX.
- New refs work where task_id was previously required.
- Ambiguous references produce a clear error.

### TASK-016 — TIG-05 Add task dependencies and executable queue

Status: `planned`  
Priority: `1`  
Verification: `standard`  

Add explicit cross-epic task dependencies and a deterministic executable queue so parallel epics can be scheduled safely.

Acceptance criteria:

- Ready tasks blocked by dependencies are not reported as executable.
- Cross-epic dependencies are supported.
- Cycles are rejected.
- Executable queue output is deterministic.

### TASK-017 — TIG-06 Add migration and generated output update

Status: `planned`  
Priority: `1`  
Verification: `standard`  

Provide safe migration/backward compatibility for existing plan and task state and update generated outputs to display readable refs.

Acceptance criteria:

- Existing AI_PROJECT/state can be validated after migration.
- Generated files display readable refs and legacy IDs where useful.
- Prompt packages still contain enough identity data for Codex execution.
- Validation and generated checks pass.

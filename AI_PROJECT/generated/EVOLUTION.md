<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/evolution.json -->

# AI Development System Evolution

Revision: `77`
Changes: `4`

## Summary

- `accepted`: 3
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

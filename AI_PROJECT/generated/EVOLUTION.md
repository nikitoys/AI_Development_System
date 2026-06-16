<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/evolution.json -->

# AI Development System Evolution

Revision: `34`
Changes: `2`

## Summary

- `accepted`: 2

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

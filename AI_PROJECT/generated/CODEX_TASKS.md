<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Project Tasks

Revision: `24`
Current task: `none`

## Epic `EPIC-001`

### TASK-001 — Write Project Control Usage Guide

Status: `in_review`  
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

## Epic `EPIC-002`

### TASK-002 — Document Skills Layer Roadmap

Status: `in_review`  
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

Status: `in_review`  
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

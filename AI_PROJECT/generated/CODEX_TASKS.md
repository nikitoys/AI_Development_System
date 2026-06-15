<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Project Tasks

Revision: `8`
Current task: `TASK-002`

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

## Epic `EPIC-002`

### TASK-002 — Document Skills Layer Roadmap ⭐

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

<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `8`

Task: `TASK-002` — **Document Skills Layer Roadmap**
Epic: `EPIC-002`
Status: `in_review`
Verification: `standard`

## Prompt Control Fields

Active Role: `AI System Maintainer + Technical Writer AI`
Active Stage: `Skills Layer Documentation`
Active Document: `ai-system/skills/README.md`
Expected Result: `Skills layer roadmap document created, registered in documentation control, generated prompt package written, validation passed, waiting for Human Owner approval.`

## Summary

Create a controlled skills layer documentation page that records useful project skills/plugins and recommends next skills to create.

## Description

Create ai-system/skills/README.md as a controlled documentation page for skills/plugins in this repository. Register the document with docctl.py in a non-active lifecycle state and validate project-control outputs.

## Scope

- Create ai-system/skills/README.md.
- Explain what skills/plugins are for in this project.
- State that skills/plugins are guidance and routing helpers, not sources of authority.
- State that Python CLI remains the source of truth.
- List existing useful skills: Project Control Gateway Skill and CLI Creator Skill.
- List recommended skills to create: Documentation Control Skill, SOP Authoring Skill, Agent Assignment Skill, Review Gate Skill, QA Evidence Skill, Decision / ADR Skill, Git Safety Skill, Protected Files Skill.
- For each skill, include purpose, related CLI, priority, allowed actions, and forbidden actions.
- Include a recommended creation order.
- Include rules requiring every new skill to be created through a controlled Task and requiring subagents to obey CLI/source-of-truth rules.

## Out of Scope

- Do not implement new skills.
- Do not mark the document active or accepted without Human Owner approval.
- Do not manually edit AI_PROJECT/state/**.
- Do not manually edit AI_PROJECT/events/**.
- Do not manually edit AI_PROJECT/generated/**.
- Do not change project-control CLI behavior.

## Allowed Files

- ai-system/skills/README.md
- AI_PROJECT/state/plan.json via planctl.py only
- AI_PROJECT/events/plan-events.jsonl via planctl.py only
- AI_PROJECT/generated/CODEX_PLAN.md via planctl.py only
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/CODEX_CURRENT.md via taskctl.py only
- AI_PROJECT/generated/CODEX_PROMPT.md via taskctl.py only
- AI_PROJECT/state/docs.json via docctl.py only
- AI_PROJECT/events/doc-events.jsonl via docctl.py only
- AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only
- AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only

## Acceptance Criteria

- ai-system/skills/README.md exists and covers skills/plugins as guidance and routing helpers, not authoritative source documents.
- The document clearly states that Python CLIs and registered source documents remain the source of truth.
- The document lists the two existing useful skills and the eight recommended future skills with purpose, related CLI, priority, allowed actions, and forbidden actions.
- The document includes a recommended skill creation order.
- The document states that every new skill must be created through a controlled Task.
- The document states that subagents may use skills only as guidance and must still obey CLI/source-of-truth rules.
- The document is registered through docctl.py as draft or review, not active.
- Plan, task, documentation, smoke doc-control, and protected-files validation commands pass.

## Review Instructions

- Verify that no protected project-control files were edited manually.
- Verify that no new skills were implemented in this task.
- Verify that the document remains in draft or review status until Human Owner approval.

## Notes

- Human Owner explicitly requested a project-controlled documentation task and allowed completion to review state without self-approval.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-002 --to in_progress
python scripts/taskctl.py task transition TASK-002 --to in_review
python scripts/taskctl.py task approve TASK-002 --notes "..."
python scripts/taskctl.py task transition TASK-002 --to done
python scripts/taskctl.py prompt build --write
```

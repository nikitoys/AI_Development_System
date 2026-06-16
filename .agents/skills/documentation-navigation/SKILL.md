---
name: documentation-navigation
description: Use when working in AI_Development_System to choose the minimal correct documentation and project-control read set before planning, editing, reviewing, or executing repository work.
---

# Documentation Navigation Skill

## Purpose

Help Codex and subagents find the correct source documents without reading the whole repository or treating generated, template, or example files as authority.

Use this skill before planning, editing, reviewing, or executing AI_Development_System work when the correct document set is not already obvious from the task prompt.

## Authority Boundary

This skill is guidance only.

Authority remains in:

- `AGENTS.md`;
- source documents under `/ai-system`;
- CLI-controlled state under root `/AI_PROJECT`;
- Human Owner decisions.

If this skill conflicts with a source document, lifecycle rule, task scope, prompt package, or project-control CLI validation, follow the authoritative source and report the conflict.

This skill does not authorize runtime behavior, automatic execution, automatic dispatch, automatic merge, automatic PR creation, automatic acceptance, or automatic review/QA closure.

## Source-Of-Truth Hierarchy

Read and interpret similarly named paths carefully:

- `/ai-system` is the source-of-truth document tree for AI Development System rules, governance, lifecycles, roles, workflows, templates, skills guidance, and behavior.
- `/AI_PROJECT/state/**` is root machine-readable current project-control state for this repository. It is changed only through the owning CLI.
- `/AI_PROJECT/events/**` is root append-only project-control audit history. It is changed only through the owning CLI.
- `/AI_PROJECT/generated/**` is root generated readable output for humans and AI agents. It may be read, but must not be edited manually or treated as editable source.
- `/ai-system/templates/**/AI_PROJECT` contains reusable templates for external projects. It is not active state for this repository.
- `/examples/golden-project/AI_PROJECT` is a non-runtime reference example. It is not active state for this repository.

## Core Navigation Rules

- Read minimal first, expand only when needed.
- Prefer source documents over generated views when defining rules or behavior.
- Use generated Markdown as a compact view of current project state, not as editable source.
- Do not edit protected `AI_PROJECT` files manually.
- Do not treat templates or golden examples as active project state.
- Ask the Human Owner only when the correct source cannot be determined after inspection, or when authority or approval is unclear.

## Request Routing

### What Should I Do Next?

Read:

- `AGENTS.md`
- `README.md`
- `AI_PROJECT/generated/CODEX_CURRENT.md`
- `AI_PROJECT/generated/CODEX_TASKS.md`
- `AI_PROJECT/generated/EVOLUTION.md`
- `AI_PROJECT/generated/CODEX_STATUS.md` if present

Use generated files only as readable state views. If a state change is needed, use the relevant CLI.

### Documentation Change

Read:

- `AGENTS.md`
- `ai-system/document-lifecycle.md`
- `ai-system/project-control/08-usage-guide.md`
- `AI_PROJECT/generated/DOCS_INDEX.md`
- `AI_PROJECT/generated/DOCS_GAPS.md`

Use:

- `python scripts/docctl.py ...` for documentation-control state
- `python scripts/taskctl.py ...` for executable task state

### Task Execution

Read:

- `AGENTS.md`
- `AI_PROJECT/generated/CODEX_CURRENT.md`
- `AI_PROJECT/generated/CODEX_TASKS.md`
- `AI_PROJECT/generated/CODEX_STATUS.md`
- `AI_PROJECT/generated/CODEX_PROMPT.md` if it exists

Use:

- `python scripts/taskctl.py ...` for Task lifecycle
- `python scripts/codexctl.py ...` for Codex prompt package status, build, and clear when available

### Project Control Gateway Work

Read:

- `AGENTS.md`
- `ai-system/project-control/01-overview.md`
- `ai-system/project-control/04-command-catalog.md`
- `ai-system/project-control/08-usage-guide.md`

Use:

- `python scripts/planctl.py ...`
- `python scripts/taskctl.py ...`
- `python scripts/docctl.py ...`
- `python scripts/evolutionctl.py ...`
- `python scripts/codexctl.py ...` if available

### System Evolution

Read:

- `AGENTS.md`
- `ai-system/evolution/README.md`
- `ai-system/evolution/roadmap.md`
- `ai-system/evolution/evolution-backlog.md`
- `ai-system/change-process.md`
- `ai-system/change-lifecycle.md`
- `ai-system/system-changelog.md`

Use:

- `python scripts/evolutionctl.py ...` for evolution state
- `python scripts/taskctl.py ...` for implementation tasks

System evolution must not be implemented without an approved Evolution Change and bounded executable Task.

### SOP, Multi-Agent, Or Subagent Planning

Read:

- `AGENTS.md`
- `ai-system/sop-model.md`
- `ai-system/agent-work-package.md`
- `ai-system/multi-agent-planning.md`
- `ai-system/parallel-execution-policy.md`
- `ai-system/manual-orchestration.md`
- `ai-system/runtime-maturity-levels.md`

Boundary:

- Current maturity remains `L3`.
- Runtime remains `DEFERRED`.
- `L4+` remains future/not approved.
- No automatic execution, dispatch, merge, PR creation, acceptance, or review/QA closure.

### Review Or QA

Read:

- `AGENTS.md`
- `ai-system/review-process.md`
- `ai-system/review-lifecycle.md`
- `ai-system/qa-lifecycle.md`
- `ai-system/verification-modes.md`
- `AI_PROJECT/generated/CODEX_CURRENT.md`
- `AI_PROJECT/generated/CODEX_STATUS.md`
- the relevant result report or changed files

Use the task scope, allowed files, acceptance criteria, verification mode, and review instructions as the review contract.

## Stop Conditions

Stop and ask or report a blocker when:

- the correct authoritative source cannot be determined after inspection;
- source documents conflict in a way that affects scope, approval, lifecycle, protected files, runtime maturity, or safety;
- the task would require manual edits to `AI_PROJECT/state/**`, `AI_PROJECT/events/**`, or `AI_PROJECT/generated/**`;
- the only available path would approve, accept, activate, or mark work done without Human Owner authority or an explicit delegated approval in the task prompt;
- requested behavior would enable L4+, runtime execution, automatic dispatch, automatic merge, automatic PR creation, automatic acceptance, or automatic review/QA closure.

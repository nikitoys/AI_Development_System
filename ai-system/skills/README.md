# Skills Layer Roadmap

Status: Draft
Version: v0.1.0

## Purpose

This document records useful skills and plugins for the AI Development System and defines which skills should be created next.

Skills and plugins help AI agents route work, remember operating rules and choose the right project-control command. They are guidance and routing helpers. They are not sources of authority.

The source of truth remains:

- Human Owner decisions;
- source documents in `/ai-system`;
- controlled project state in `AI_PROJECT/state/**`;
- Python CLI validation, audit events and generated output produced by `scripts/*ctl.py`.

Generated files under `AI_PROJECT/generated/**` are readable views. They must not be edited manually or treated as source documents.

## Authority Rule

A skill may summarize a workflow, but it must not override source documents, lifecycle rules, task boundaries, Human Owner approval or Python CLI validation.

If a skill and a source document conflict, follow the source document and report the conflict.

If a skill suggests a project-control state change, the change must still go through the relevant CLI:

- `python scripts/planctl.py ...` for Initiative and Epic planning state;
- `python scripts/taskctl.py ...` for executable Tasks, current task and Codex prompt packages;
- `python scripts/docctl.py ...` for registered documentation lifecycle state;
- `python scripts/evolutionctl.py ...` for controlled AI Development System evolution when available and applicable.

## Existing Useful Skills

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Project Control Gateway Skill | Route plan, task, documentation and evolution work through the controlled CLI gateway instead of manual state edits. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Inspect state through CLI, choose allowed commands, run validation and render commands, report unsupported operations. | Manually edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**`; invent lifecycle states or commands; execute Initiative or Epic directly. |
| Clarification Gate Skill | Teach Codex and subagents when to inspect first, proceed with safe assumptions, or stop for Human Owner blocker questions. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Classify blockers, group owner questions, identify safe defaults, preserve task and approval boundaries. | Use questions to avoid normal inspection; ask for approval after every small step; self-approve accepted, approved, active or done states. |
| CLI Creator Skill | Help design or update controlled Python CLI surfaces for project-control operations. | `scripts/*ctl.py`, validation and smoke scripts | P1 | Draft CLI command shape, map commands to state/events/generated outputs, add tests when a controlled Task allows it. | Add or change CLI behavior without a controlled Task and required owner approval; bypass protected files; make generated Markdown authoritative. |

## Recommended Skills To Create

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Documentation Control Skill | Guide documentation registration, status changes, generated indexes and documentation validation. | `docctl.py` | P0 | Register documents, set draft/review status, render/check generated docs, explain documentation lifecycle. | Mark documents active without Human Owner approval; manually edit `docs.json`, doc events or generated doc indexes. |
| Protected Files Skill | Keep agents inside the protected-files boundary and detect unsafe project-control edits. | `check-protected-project-files.py`, `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Explain protected paths, run protected-files checks, route repairs through CLIs. | Edit protected state/events/generated files manually; use ad hoc scripts to mutate protected files; hide drift. |
| Review Gate Skill | Guide review intake before a Task can be accepted or closed. | `taskctl.py`; future review control CLI if approved | P1 | Check scope, allowed files, acceptance criteria, validation output and review status; recommend APPROVED, REWORK, REJECTED or DEFERRED. | Self-approve work; mark a Task done without the required approval path; ignore Critical or Major findings. |
| QA Evidence Skill | Help collect verification evidence for Task completion. | `taskctl.py`, `scripts/verification/run_checks.py`; future QA control CLI if approved | P1 | Select checks from the declared verification mode, record executed and skipped checks, summarize evidence. | Claim tests passed without running them; silently upgrade verification mode; treat missing QA as approval. |
| SOP Authoring Skill | Help write or revise SOP documents while preserving lifecycle and approval boundaries. | `taskctl.py`, `docctl.py`, `evolutionctl.py` | P2 | Draft SOP source documents through controlled Tasks, register docs, identify required evolution approval. | Introduce new workflow rules without controlled evolution; authorize automatic execution or automatic acceptance. |
| Agent Assignment Skill | Guide manual role-to-agent assignment and bounded Agent Work Package routing. | `taskctl.py`, `scripts/agent-plan-mvp.py` | P2 | Prepare manual assignment guidance, check file-scope and dependency boundaries, keep parallel groups informational unless approved. | Dispatch agents automatically; bypass Human Owner approval; let subagents expand allowed files or scope. |
| Decision / ADR Skill | Help capture durable decisions and architecture decision records. | `docctl.py`; future decision control CLI if approved | P2 | Draft decision records, register decision documentation, connect decisions to Tasks or evolution items. | Treat chat-only decisions as durable state; accept or supersede decisions without Human Owner approval. |
| Git Safety Skill | Guide safe git inspection, staging, commit and PR boundaries for controlled work. | `git`, `check-protected-project-files.py` | P3 | Inspect diffs, separate unrelated changes, recommend safe staging/commit scope, run protected-files checks before handoff. | Revert user changes without permission; stage unrelated files; rewrite history or run destructive git commands without explicit request. |

## Recommended Creation Order

1. Clarification Gate Skill.
2. Documentation Control Skill.
3. Protected Files Skill.
4. Review Gate Skill.
5. QA Evidence Skill.
6. SOP Authoring Skill.
7. Agent Assignment Skill.
8. Decision / ADR Skill.
9. Git Safety Skill.

This order strengthens the control boundary first, then improves review and evidence quality, then adds higher-level planning and collaboration guidance.

## New Skill Creation Rule

Every new skill must be created through a controlled Task.

The Task must define:

- active role, stage, document and expected result;
- source documents;
- scope and out of scope;
- allowed files;
- forbidden actions;
- acceptance criteria;
- validation commands;
- review instructions.

If a new skill changes rules, lifecycle behavior, workflow, prompt behavior, protected file policy, CLI behavior or subagent behavior, it must also follow the controlled evolution process before implementation.

## Subagent Rule

Subagents may use skills only as guidance.

Subagents must still obey:

- Human Owner decisions;
- source-of-truth documents in `/ai-system`;
- project-control CLI commands;
- Task scope and allowed files;
- protected-files rules;
- review and QA gates.

A subagent must not treat a skill as permission to execute work, expand scope, change project-control state, approve results, mark documentation active or bypass Python CLI validation.

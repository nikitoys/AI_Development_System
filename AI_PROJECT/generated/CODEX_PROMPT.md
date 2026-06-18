# Codex Prompt Package

Generated: 2026-06-18T18:19:07Z
Source Type: task
Source ID: TASK-030
Source Status: in_review

[SYSTEM]

Active Role:
Technical Writer AI / AI System Maintainer

Active Stage:
Control Plane Documentation

Active Document:
ai-system/project-control

Expected Result:
Owner quickstart and control-plane documentation explain how to use and safely operate the new model.

Repository Context:
This repository is an AI Development System governance control plane.
Project-control state is managed through Python CLI gateways; generated Markdown is derived output.

Source:
Source Task: TASK-030
Task Status: in_review
Title: Task L - Documentation and owner quickstart

Make the unified control-plane usable and discoverable.

Update or create owner-facing documentation for aictl usage, legacy wrapper relationship, project doctor, local web dashboard, web safety model, state/events/generated architecture, and ID allocation policy.

Scope:
- Document how to use aictl.
- Document how legacy ctl wrappers relate to aictl.
- Document how to run project doctor.
- Document how to run the local web dashboard.
- Document the Web UI safety model.
- Document state/events/generated architecture and ID allocation policy.
- Ensure Codex can be pointed to aictl as the preferred interface.

Out of Scope:
- Do not implement new control-plane behavior in documentation task.
- Do not mark documents active without Human Owner acceptance.
- Do not manually edit documentation-control protected files.

Allowed Files:
- ai-system/project-control/**
- README.md
- AGENTS.md
- AI_PROJECT/state/docs.json via docctl.py only
- AI_PROJECT/events/doc-events.jsonl via docctl.py only
- AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only
- AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only
- AI_PROJECT/generated/CONTEXT_PACK.md via contextctl.py/aictl.py only
- AI_PROJECT/generated/CONTEXT_STATUS.md via contextctl.py/aictl.py only
- AI_PROJECT/events/context-events.jsonl via contextctl.py/aictl.py only
- AI_PROJECT/state/context.json via contextctl.py/aictl.py only if the command updates it
- AI_PROJECT/generated/CODEX_PROMPT.md via codexctl.py/aictl.py/taskctl.py only
- AI_PROJECT/generated/CODEX_STATUS.md via codexctl.py/aictl.py only
- AI_PROJECT/events/codex-events.jsonl via codexctl.py/aictl.py only
- AI_PROJECT/state/current_execution.json via codexctl.py/aictl.py only if the command updates it

Implementation Instructions:
- Inspect current files before editing.
- Stay within allowed files.
- Preserve existing conventions.
- Prefer minimal, commit-ready changes.
- Do not perform unrelated refactors.
- Do not edit AI_PROJECT/state/**, AI_PROJECT/events/** or AI_PROJECT/generated/** manually.

Retrieved Context:
- Context Pack path: `AI_PROJECT/generated/CONTEXT_PACK.md`
- Context Pack SHA-256: `f4c95a4f4c004f8b4775dd1a0b654fffa462e1b0a4a9db48e07c682575c2494e`
- Context mode: `task`
- Context task ID: `TASK-030`
- Docs revision: `22`
- Tasks revision: `276`

Retrieved Context Rules:
- Retrieved context is read-only.
- Retrieved context does not expand Allowed Files.
- Retrieved context does not expand Scope or override Out of Scope.
- Retrieved context does not replace Acceptance Criteria.
- If retrieved context conflicts with the source Task, source documents, or Human Owner instructions, report the conflict.

Retrieved Context Source Metadata:
- `ai-system/project-control/04-command-catalog.md` lines 64-116; heading: Project Control Command Catalog > Self-Hosted Command Boundary; content: `a1985ca2f321`; chunk: `b755c971df05`
- `ai-system/skills/README.md` lines 80-92; heading: Skills Layer Roadmap > Recommended Skills To Create; content: `dbf637225bec`; chunk: `eef80c572381`
- `ai-system/skills/README.md` lines 34-43; heading: Skills Layer Roadmap > Existing Useful Skills; content: `dbf637225bec`; chunk: `758bde12e28c`
- `ai-system/project-control/03-state-model.md` lines 104-125; heading: Project Control State Model > Context Control State; content: `b69e6c6ad9ac`; chunk: `0cd80bdf0d55`
- `ai-system/project-control/06-prompt-package-spec.md` lines 874-906; heading: 17. Relationship To taskctl.py And codexctl.py; content: `9304e03cf1dd`; chunk: `6cf68be89257`
- `ai-system/project-control/03-state-model.md` lines 71-103; heading: Project Control State Model > Documentation Control State; content: `b69e6c6ad9ac`; chunk: `c68c7fcfa12b`
- `ai-system/project-control/06-prompt-package-spec.md` lines 797-833; heading: 14. Context Budget Rules > Context Pack Boundary; content: `9304e03cf1dd`; chunk: `24706f89c068`
- `ai-system/project-control/06-prompt-package-spec.md` lines 580-670; heading: 12. Prompt Package Template; content: `9304e03cf1dd`; chunk: `4b3949b96350`

Retrieved Context Pack Content:

````text
<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-030 Task L - Documentation and owner quickstart Make the unified control-plane usable and discoverable. Update or create owner-facing documentation for aictl usage, legacy wrapper relationship, project doctor, local web dashboard, web safety model, state/events/generated architecture, and ID allocation policy. ai-system/project-control Owner quickstart and control-plane documentation explain how to use and safely operate the new model. Document how to use aictl. Document how legacy ctl wrappers relate to aictl. Document how to run project doctor. Document how to run the local web dashboard. Document the Web UI safety model. Document state/events/generated architecture and ID allocation policy. Ensure Codex can be pointed to aictl as the preferred interface. Do not implement new control-plane behavior in documentation task. Do not mark documents active without Human Owner acceptance. Do not manually edit documentation-control protected files. ai-system/project-control/** README.md AGENTS.md AI_PROJECT/state/docs.json via docctl.py only AI_PROJECT/events/doc-events.jsonl via docctl.py only AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only AI_PROJECT/generated/CONTEXT_PACK.md via contextctl.py/aictl.py only AI_PROJECT/generated/CONTEXT_STATUS.md via contextctl.py/aictl.py only AI_PROJECT/events/context-events.jsonl via contextctl.py/aictl.py only AI_PROJECT/state/context.json via contextctl.py/aictl.py only if the command updates it AI_PROJECT/generated/CODEX_PROMPT.md via codexctl.py/aictl.py/taskctl.py only AI_PROJECT/generated/CODEX_STATUS.md via codexctl.py/aictl.py only AI_PROJECT/events/codex-events.jsonl via codexctl.py/aictl.py only AI_PROJECT/state/current_execution.json via codexctl.py/aictl.py only if the command updates it Owner can discover common commands quickly. Codex can be pointed to aictl as the preferred interface. Docs clearly say generated files are derived. Docs explain legacy ctl wrappers, project doctor, local web dashboard, web safety model, state/events/generated architecture, and ID allocation policy. Verify docs do not claim generated Markdown is source of truth. Verify documentation-control files are updated only through docctl.py. Verify Human Owner acceptance remains required before active/accepted states.","schema_version":1,"task_id":"TASK-030"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-030`
Explicit query: `false`
Limit: `8`
Docs revision: `22`
Tasks revision: `276`

## Query

```text
TASK-030 Task L - Documentation and owner quickstart Make the unified control-plane usable and discoverable. Update or create owner-facing documentation for aictl usage, legacy wrapper relationship, project doctor, local web dashboard, web safety model, state/events/generated architecture, and ID allocation policy. ai-system/project-control Owner quickstart and control-plane documentation explain how to use and safely operate the new model. Document how to use aictl. Document how legacy ctl wrappers relate to aictl. Document how to run project doctor. Document how to run the local web dashboard. Document the Web UI safety model. Document state/events/generated architecture and ID allocation policy. Ensure Codex can be pointed to aictl as the preferred interface. Do not implement new control-plane behavior in documentation task. Do not mark documents active without Human Owner acceptance. Do not manually edit documentation-control protected files. ai-system/project-control/** README.md AGENTS.md AI_PROJECT/state/docs.json via docctl.py only AI_PROJECT/events/doc-events.jsonl via docctl.py only AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only AI_PROJECT/generated/CONTEXT_PACK.md via contextctl.py/aictl.py only AI_PROJECT/generated/CONTEXT_STATUS.md via contextctl.py/aictl.py only AI_PROJECT/events/context-events.jsonl via contextctl.py/aictl.py only AI_PROJECT/state/context.json via contextctl.py/aictl.py only if the command updates it AI_PROJECT/generated/CODEX_PROMPT.md via codexctl.py/aictl.py/taskctl.py only AI_PROJECT/generated/CODEX_STATUS.md via codexctl.py/aictl.py only AI_PROJECT/events/codex-events.jsonl via codexctl.py/aictl.py only AI_PROJECT/state/current_execution.json via codexctl.py/aictl.py only if the command updates it Owner can discover common commands quickly. Codex can be pointed to aictl as the preferred interface. Docs clearly say generated files are derived. Docs explain legacy ctl wrappers, project doctor, local web dashboard, web safety model, state/events/generated architecture, and ID allocation policy. Verify docs do not claim generated Markdown is source of truth. Verify documentation-control files are updated only through docctl.py. Verify Human Owner acceptance remains required before active/accepted states.
```

## Task Boundary Snapshot

Task: `TASK-030` - Task L - Documentation and owner quickstart
Status: `in_review`

Scope:
- Document how to use aictl.
- Document how legacy ctl wrappers relate to aictl.
- Document how to run project doctor.
- Document how to run the local web dashboard.
- Document the Web UI safety model.
- Document state/events/generated architecture and ID allocation policy.
- Ensure Codex can be pointed to aictl as the preferred interface.

Allowed Files:
- ai-system/project-control/**
- README.md
- AGENTS.md
- AI_PROJECT/state/docs.json via docctl.py only
- AI_PROJECT/events/doc-events.jsonl via docctl.py only
- AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only
- AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only
- AI_PROJECT/generated/CONTEXT_PACK.md via contextctl.py/aictl.py only
- AI_PROJECT/generated/CONTEXT_STATUS.md via contextctl.py/aictl.py only
- AI_PROJECT/events/context-events.jsonl via contextctl.py/aictl.py only
- AI_PROJECT/state/context.json via contextctl.py/aictl.py only if the command updates it
- AI_PROJECT/generated/CODEX_PROMPT.md via codexctl.py/aictl.py/taskctl.py only
- AI_PROJECT/generated/CODEX_STATUS.md via codexctl.py/aictl.py only
- AI_PROJECT/events/codex-events.jsonl via codexctl.py/aictl.py only
- AI_PROJECT/state/current_execution.json via codexctl.py/aictl.py only if the command updates it

Acceptance Criteria:
- Owner can discover common commands quickly.
- Codex can be pointed to aictl as the preferred interface.
- Docs clearly say generated files are derived.
- Docs explain legacy ctl wrappers, project doctor, local web dashboard, web safety model, state/events/generated architecture, and ID allocation policy.

## Index Summary

Indexed source documents: `10`
Indexed chunks: `890`
Excluded registered sources: `134`
Selected chunks: `8`

Default exclusion policy: generated, inactive, archived, deprecated, template, and example documents are excluded unless explicitly allowed.

## Selected Sources

| Score | Source | Heading | Lines | Content hash | Chunk hash | Reasons |
| ---: | --- | --- | --- | --- | --- | --- |
| 302 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Self-Hosted Command Boundary | 64-116 | `a1985ca2f321` | `b755c971df05` | heading token match: command, project; metadata token match: active, ai-system, command, md, project, project-control; content token match: acceptance, ai-system, ai_project, and, are, as, be, command |
| 226 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | heading token match: create, to; metadata token match: active, ai-system, create, md, readme, to; content token match: acceptance, accepted, active, agents, and, architecture, as, be |
| 222 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | metadata token match: active, ai-system, md, readme; content token match: acceptance, accepted, active, agents, ai_project, and, as, before |
| 212 | `ai-system/project-control/03-state-model.md` | Project Control State Model > Context Control State | 104-125 | `b69e6c6ad9ac` | `0cd80bdf0d55` | heading token match: context, model, project, state; metadata token match: active, ai-system, context, md, model, project, project-control, state; content token match: acceptance, active, ai_project, and, are, be, context, context-events |
| 176 | `ai-system/project-control/06-prompt-package-spec.md` | 17. Relationship To taskctl.py And codexctl.py | 874-906 | `9304e03cf1dd` | `6cf68be89257` | heading token match: and, codexctl, py, relationship, taskctl, to; metadata token match: active, ai-system, and, codexctl, md, project, project-control, py; content token match: and, be, before, can, codex, codex_prompt, codex_status, codexctl |
| 166 | `ai-system/project-control/03-state-model.md` | Project Control State Model > Documentation Control State | 71-103 | `b69e6c6ad9ac` | `c68c7fcfa12b` | heading token match: documentation, model, project, state; metadata token match: active, ai-system, documentation, md, model, project, project-control, state; content token match: ai_project, and, are, as, derived, doc-events, docctl, docs |
| 140 | `ai-system/project-control/06-prompt-package-spec.md` | 14. Context Budget Rules > Context Pack Boundary | 797-833 | `9304e03cf1dd` | `24706f89c068` | heading token match: context; metadata token match: active, ai-system, context, md, project, project-control; content token match: acceptance, and, before, clearly, codex, codex_prompt, codexctl, context |
| 139 | `ai-system/project-control/06-prompt-package-spec.md` | 12. Prompt Package Template | 580-670 | `9304e03cf1dd` | `4b3949b96350` | metadata token match: active, ai-system, md, project, project-control; content token match: acceptance, active, ai_project, and, be, command, commands, context |

## Selected Context

### 1. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Self-Hosted Command Boundary
Lines: `64-116`
Score: `302`
Content hash: `a1985ca2f3219254917601872017052dcfc6ae74f1f636fa6fdbe6a6a3227d32`
Chunk hash: `b755c971df05cf7e6b08835383033a087a162359ce3241ab86018beb96506a9d`
Reasons: heading token match: command, project; metadata token match: active, ai-system, command, md, project, project-control; content token match: acceptance, ai-system, ai_project, and, are, as, be, command

```text
## Self-Hosted Command Boundary

AI_Development_System now uses root `/AI_PROJECT` as its own self-hosted Project Control Layer. All protected state, event and generated files in that directory must be changed only through approved CLI gateways.

Current domain commands include:

```bash
python scripts/planctl.py ...
python scripts/taskctl.py ...
python scripts/docctl.py ...
python scripts/evolutionctl.py ...
python scripts/contextctl.py ...
```

Current documentation-control commands include:

```bash
python scripts/docctl.py init
python scripts/docctl.py scan --scope ai-system
python scripts/docctl.py scan --scope root
python scripts/docctl.py scan --scope skills
python scripts/docctl.py scan --scope all
python scripts/docctl.py doc register --path <path> --title <title> --type <type> --status <status>
python scripts/docctl.py doc status <path> --to <status>
python scripts/docctl.py doc mark-reviewed <path> --note <text>
python scripts/docctl.py validate
python scripts/docctl.py render
python scripts/docctl.py check-generated
python scripts/docctl.py audit --last 20
```

`docctl.py` owns `AI_PROJECT/state/docs.json`, `AI_PROJECT/events/doc-events.jsonl`, `AI_PROJECT/generated/DOCS_INDEX.md` and `AI_PROJECT/generated/DOCS_GAPS.md`. It records current document content hashes, reviewed content hashes and declared-status metadata.

[...truncated by contextctl...]
```

### 2. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Recommended Skills To Create
Lines: `80-92`
Score: `226`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: heading token match: create, to; metadata token match: active, ai-system, create, md, readme, to; content token match: acceptance, accepted, active, agents, and, architecture, as, be

```text
## Recommended Skills To Create

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Documentation Control Skill | Guide documentation registration, status changes, generated indexes and documentation validation. | `docctl.py` | P0 | Register documents, set draft/review status, render/check generated docs, explain documentation lifecycle. | Mark documents active without Human Owner approval; manually edit `docs.json`, doc events or generated doc indexes. |
| Protected Files Skill | Keep agents inside the protected-files boundary and detect unsafe project-control edits. | `check-protected-project-files.py`, `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Explain protected paths, run protected-files checks, route repairs through CLIs. | Edit protected state/events/generated files manually; use ad hoc scripts to mutate protected files; hide drift. |
| Review Gate Skill | Guide review intake before a Task can be accepted or closed. | `taskctl.py`; future review control CLI if approved | P1 | Check scope, allowed files, acceptance criteria, validation output and review status; recommend APPROVED, REWORK, REJECTED or DEFERRED. | Self-approve work; mark a Task done without the required approval path; ignore Critical or Major findings. |

[...truncated by contextctl...]
```

### 3. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Existing Useful Skills
Lines: `34-43`
Score: `222`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: metadata token match: active, ai-system, md, readme; content token match: acceptance, accepted, active, agents, ai_project, and, as, before

```text
## Existing Useful Skills

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Project Control Gateway Skill | Route plan, task, documentation and evolution work through the controlled CLI gateway instead of manual state edits. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Inspect state through CLI, choose allowed commands, run validation and render commands, report unsupported operations. | Manually edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**`; invent lifecycle states or commands; execute Initiative or Epic directly. |
| Clarification Gate Skill | Teach Codex and subagents when to inspect first, proceed with safe assumptions, or stop for Human Owner blocker questions. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Classify blockers, group owner questions, identify safe defaults, preserve task and approval boundaries. | Use questions to avoid normal inspection; ask for approval after every small step; self-approve accepted, approved, active or done states. |
| Documentation Navigation Skill | Route Codex and subagents to the minimal correct documentation and project-control read set before planning, editing, reviewing or executing AI_Development_System work.

[...truncated by contextctl...]
```

### 4. `ai-system/project-control/03-state-model.md`

Title: Project Control State Model
Status: `active`  Type: `reference`
Heading: Project Control State Model > Context Control State
Lines: `104-125`
Score: `212`
Content hash: `b69e6c6ad9acbaf0bb398fd6ad729bb07290b6138e99a3535701e57c750a244d`
Chunk hash: `0cd80bdf0d55e5284fa6355477f50005896398136bf33b7e1a181718f309f8b4`
Reasons: heading token match: context, model, project, state; metadata token match: active, ai-system, context, md, model, project, project-control, state; content token match: acceptance, active, ai_project, and, are, be, context, context-events

```text
## Context Control State

Context control uses the state/events/generated model without adding a new source-of-truth state file:

```text
AI_PROJECT/state/docs.json
AI_PROJECT/state/tasks.json
AI_PROJECT/events/context-events.jsonl
AI_PROJECT/generated/CONTEXT_PACK.md
AI_PROJECT/generated/CONTEXT_STATUS.md
```

`scripts/contextctl.py` builds a deterministic derived index in memory from registered documents in `docs.json` and optional Task context from `tasks.json`.

The derived index and Context Pack are not source of truth. They must not expand Task scope, allowed files, out-of-scope items or acceptance criteria. If retrieved context conflicts with the Task or source documents, the Task and source documents remain authoritative.

By default, context control indexes registered active source documents only. It excludes generated files, inactive documents, archived documents, deprecated documents, templates and examples unless the operator explicitly enables the relevant include flag.

`CONTEXT_PACK.md` includes selected source paths, headings, line ranges, source content hashes, chunk hashes, deterministic keyword scores and selection reasons. `CONTEXT_STATUS.md` summarizes the current generated pack, selected paths and exclusion reasons. Both files are generated output and must be regenerated through `contextctl.py`.

---
```

### 5. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 17. Relationship To taskctl.py And codexctl.py
Lines: `874-906`
Score: `176`
Content hash: `9304e03cf1dd12bb320887a0e1e1c90bb87259f60bf4a86d63a904b4e7e87210`
Chunk hash: `6cf68be892579b77502246852781af90dc2942f367d5af5b0a3c4a4ee727323f`
Reasons: heading token match: and, codexctl, py, relationship, taskctl, to; metadata token match: active, ai-system, and, codexctl, md, project, project-control, py; content token match: and, be, before, can, codex, codex_prompt, codex_status, codexctl

```text
# 17. Relationship To taskctl.py And codexctl.py

Task prompt output can be built by `taskctl.py`.

`taskctl.py` owns:

```text id="d2esmn"
Task state
Current Task
Task generated Markdown
Codex Prompt Package
Task audit events
```

`codexctl.py` owns:

```text
Current Codex execution state
CODEX_STATUS.md
Codex prompt build and clear audit events
Optional read-only Context Pack inclusion in CODEX_PROMPT.md
```

Prompt Package build must not bypass task validation.

Before building the package, task state must be valid.

`contextctl.py` may read Task state to derive a search query for a Context Pack, but it does not mutate Task state and does not make retrieved context executable scope.

`codexctl.py` may validate and include an existing Context Pack, but it must not build the index or refresh Context Pack content itself.

---
```

### 6. `ai-system/project-control/03-state-model.md`

Title: Project Control State Model
Status: `active`  Type: `reference`
Heading: Project Control State Model > Documentation Control State
Lines: `71-103`
Score: `166`
Content hash: `b69e6c6ad9acbaf0bb398fd6ad729bb07290b6138e99a3535701e57c750a244d`
Chunk hash: `c68c7fcfa12b1f98261105372d826707cb0cef9b3340f394ea7dc928123e4bc0`
Reasons: heading token match: documentation, model, project, state; metadata token match: active, ai-system, documentation, md, model, project, project-control, state; content token match: ai_project, and, are, as, derived, doc-events, docctl, docs

```text
## Documentation Control State

Documentation control uses the same state/events/generated model:

```text
AI_PROJECT/state/docs.json
AI_PROJECT/events/doc-events.jsonl
AI_PROJECT/generated/DOCS_INDEX.md
AI_PROJECT/generated/DOCS_GAPS.md
```

`docs.json` is the authoritative registry for managed documentation. Each registered document stores lifecycle metadata plus derived retrieval metadata:

```text
path
title
type
status
required
owner
content_hash
last_reviewed_at
last_reviewed_by
last_reviewed_content_hash
declared_status
declared_status_raw
declared_status_source
```

`content_hash` is the current SHA-256 hash recorded by `docctl.py`. `last_reviewed_content_hash` is the SHA-256 hash reviewed by `docctl.py doc mark-reviewed`. Declared status fields are derived from document frontmatter, `Status:` metadata lines or a `## Status` section when present.

`DOCS_GAPS.md` is generated from `docs.json` and current source files. It groups actionable gaps such as missing files, status mismatch, stale reviews, unresolved placeholders, broken local links and stale content hash metadata.
```

### 7. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 14. Context Budget Rules > Context Pack Boundary
Lines: `797-833`
Score: `140`
Content hash: `9304e03cf1dd12bb320887a0e1e1c90bb87259f60bf4a86d63a904b4e7e87210`
Chunk hash: `24706f89c068bb280d5630a712f0d9b260c02079a14823cc0a350875c71ba831`
Reasons: heading token match: context; metadata token match: active, ai-system, context, md, project, project-control; content token match: acceptance, and, before, clearly, codex, codex_prompt, codexctl, context

```text
## Context Pack Boundary

When Codex needs additional documentation context, use `contextctl.py` to generate a bounded Context Pack:

```bash
python scripts/contextctl.py pack build --task <TASK_ID> --write
```

Context Pack output is derived retrieval context. It may help Codex decide which source sections to inspect, but it must not change the Prompt Package contract.

Context Pack must not:

```text
- expand Task scope;
- add allowed files;
- add acceptance criteria;
- override out-of-scope items;
- replace source documents or Task state;
- include full tasks.json, full docs.json or full audit logs by default.
```

The default retrieval policy excludes generated files, inactive documents, archived documents, deprecated documents, templates and examples unless explicitly allowed by a `contextctl.py` include flag.

Before `codexctl.py` includes a Context Pack in `CODEX_PROMPT.md`, it must validate that the pack:

```text
- exists;
- has the generated-file header;
- has valid Context Pack metadata;
- matches the requested Task when the pack is task-scoped;
- was generated from the current docs/task revisions recorded in project-control state.
```

If validation fails, `codexctl.py` must fail clearly and must not include stale or invalid retrieved context in the prompt package.

---
```

### 8. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 12. Prompt Package Template
Lines: `580-670`
Score: `139`
Content hash: `9304e03cf1dd12bb320887a0e1e1c90bb87259f60bf4a86d63a904b4e7e87210`
Chunk hash: `4b3949b963506d03a8ca61d2f28eb70f0cc2ca715a4c20495bab284ca4d8fcb0`
Reasons: metadata token match: active, ai-system, md, project, project-control; content token match: acceptance, active, ai_project, and, be, command, commands, context

```text
# 12. Prompt Package Template

Canonical structure:

````text id="7p2uqx"
[SYSTEM]

Active Role: <active_role>
Active Stage: <active_stage>
Active Document: <active_document>
Expected Result: <expected_result>

Repository: current repository
Task ID: <task_id>
Task Title: <task_title>
Task Status: <task_status>
Verification Mode: <verification_mode>

Initiative: <initiative_id> — <initiative_title>
Epic: <epic_id> — <epic_title>

Context:
<summary>

Details:
<description>

Scope:
- <scope item>

Out of Scope:
- <out of scope item>

Allowed Files:
- <allowed file>

Retrieved Context:
- Context Pack path: <path>
- Context Pack SHA-256: <hash>
- Context mode: <mode>
- Context task ID: <task_id>
- Docs revision: <revision>
- Tasks revision: <revision>

Retrieved Context Rules:
- Retrieved context is read-only.
- Retrieved context does not expand Allowed Files.
- Retrieved context does not expand Scope or override Out of Scope.
- Retrieved context does not replace Acceptance Criteria.
- Conflicts must be reported.

Retrieved Context Source Metadata:
- <source path, line range, source content hash, chunk hash>

Retrieved Context Pack Content:
<bounded generated context pack>

Acceptance Criteria:
- <acceptance criterion>

Review Instructions:
- <review instruction>

Execution Rules:
- Do not edit AI_PROJECT/state/*.json manually.
- Do not edit AI_PROJECT/events/*.jsonl manually.

[...truncated by contextctl...]
```

## Excluded Source Summary

- inactive document excluded by default: `93`
  - `.agents/skills/agent-delegation/SKILL.md`
  - `.agents/skills/clarification-gate/SKILL.md`
  - `.agents/skills/documentation-navigation/SKILL.md`
  - `.agents/skills/project-control-gateway/SKILL.md`
  - `AGENTS.md`
  - `README.md`
  - `README.ru.md`
  - `ai-system/README.md`
  - `ai-system/agent-result-intake.md`
  - `ai-system/agent-work-package.md`
  - `ai-system/aicp-language-policy.md`
  - `ai-system/aicp-security-privacy-policy.md`
  - `ai-system/aicp-work-item-hierarchy.md`
  - `ai-system/change-lifecycle.md`
  - `ai-system/change-process.md`
  - `ai-system/codex-lifecycle.md`
  - `ai-system/decision-lifecycle.md`
  - `ai-system/decision-process.md`
  - `ai-system/document-lifecycle.md`
  - `ai-system/evolution/README.md`
- template document excluded by default: `41`
  - `ai-system/document-templates.md`
  - `ai-system/evolution/templates/evolution-task.md`
  - `ai-system/evolution/templates/owner-evolution-plan.md`
  - `ai-system/evolution/templates/system-change-proposal.md`
  - `ai-system/templates/agent-worker-prompt.md`
  - `ai-system/templates/foldered/AGENTS.root.md`
  - `ai-system/templates/foldered/AI_PROJECT/AGENTS.md`
  - `ai-system/templates/foldered/AI_PROJECT/AGENT_ASSIGNMENTS.md`
  - `ai-system/templates/foldered/AI_PROJECT/AGENT_LOCKS.md`
  - `ai-system/templates/foldered/AI_PROJECT/AGENT_METRICS.md`
  - `ai-system/templates/foldered/AI_PROJECT/AGENT_PLAN.md`
  - `ai-system/templates/foldered/AI_PROJECT/AGENT_RESULTS.md`
  - `ai-system/templates/foldered/AI_PROJECT/AGENT_TASKS.md`
  - `ai-system/templates/foldered/AI_PROJECT/AI_DEV_SYSTEM_VERSION.md`
  - `ai-system/templates/foldered/AI_PROJECT/CODEX_COMMANDS.md`
  - `ai-system/templates/foldered/AI_PROJECT/CODEX_CURRENT.md`
  - `ai-system/templates/foldered/AI_PROJECT/CODEX_PLAN.md`
  - `ai-system/templates/foldered/AI_PROJECT/CODEX_SESSION_LOG.md`
  - `ai-system/templates/foldered/AI_PROJECT/CODEX_TASKS.md`
  - `ai-system/templates/foldered/AI_PROJECT/CODEX_WORKFLOW.md`
````

Acceptance Criteria:
- Owner can discover common commands quickly.
- Codex can be pointed to aictl as the preferred interface.
- Docs clearly say generated files are derived.
- Docs explain legacy ctl wrappers, project doctor, local web dashboard, web safety model, state/events/generated architecture, and ID allocation policy.

Verification:
- Use verification mode `standard`.
- Run the validation commands required by the task and report results.

Result Format:
- Summary
- Changed files
- Commands run
- Verification result
- Blockers or risks

Review / Result Format Notes:
- Verify docs do not claim generated Markdown is source of truth.
- Verify documentation-control files are updated only through docctl.py.
- Verify Human Owner acceptance remains required before active/accepted states.

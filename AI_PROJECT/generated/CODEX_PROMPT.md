# Codex Prompt Package

Generated: 2026-06-20T08:15:03Z
Source Type: task
Source ID: TASK-064
Source Status: in_progress

[SYSTEM]

Active Role:
Frontend Developer AI / Backend Developer AI

Active Stage:
Pipeline Dashboard UI

Active Document:
ai_project_ctl/web/server.py / ai_project_ctl/web/read_model.py

Expected Result:
Human Owner can inspect and operate supervised pipeline sessions from the local UI with explicit confirmation.

Repository Context:
This repository is an AI Development System governance control plane.
Project-control state is managed through Python CLI gateways; generated Markdown is derived output.

Source:
Source Task: TASK-064
Task Status: in_progress
Title: PIPE-13 Pipeline UI Dashboard

Add a Web Control Center dashboard for pipeline sessions, queue preview, policy selection, run-next, and run-until-blocker.

Expose supervised pipeline operation in the local Web Control Center without weakening confirmation, policy, or lifecycle gates.

Scope:
- Add Pipeline dashboard/page to the Web Control Center.
- Show policy selector/preset preview, queue selector, queue preview, session status, current step, gates, stop reason, and latest audit entries.
- Expose Create Session, Run Next, Run Until Blocker, Stop Session, and Refresh Status actions where implemented.
- Require explicit confirmation for any write/run action.
- Show action result panel with step status, blockers, changed/generated files, reports, reviews, and next actions.
- Keep UI local-only and route writes through governed commands/workflows.
- Add tests for dashboard rendering, confirmation requirements, and action routing.

Out of Scope:
- Do not add remote hosting.
- Do not bypass pipeline policy.
- Do not auto-start sessions on page load.
- Do not run arbitrary shell commands from UI.
- Do not hide blockers or failed gates.

Allowed Files:
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/pipeline/** if UI integration requires compatible changes
- ai_project_ctl/core/registry.py if action metadata is needed
- scripts/aictl.py if routing is needed
- tests/test_web_control_center.py
- tests/**
- ai-system/project-control/** if UI documentation is needed

Implementation Instructions:
- Inspect current files before editing.
- Stay within allowed files.
- Preserve existing conventions.
- Prefer minimal, commit-ready changes.
- Do not perform unrelated refactors.
- Do not edit AI_PROJECT/state/**, AI_PROJECT/events/** or AI_PROJECT/generated/** manually.

Retrieved Context:
- Context Pack path: `AI_PROJECT/generated/CONTEXT_PACK.md`
- Context Pack SHA-256: `3478cd815c10ab7052b7c4152825f8f2e206ca739068bdd583f01f39a7821441`
- Context mode: `task`
- Context task ID: `TASK-064`
- Docs revision: `24`
- Tasks revision: `582`

Retrieved Context Rules:
- Retrieved context is read-only.
- Retrieved context does not expand Allowed Files.
- Retrieved context does not expand Scope or override Out of Scope.
- Retrieved context does not replace Acceptance Criteria.
- If retrieved context conflicts with the source Task, source documents, or Human Owner instructions, report the conflict.

Retrieved Context Source Metadata:
- `ai-system/skills/README.md` lines 80-92; heading: Skills Layer Roadmap > Recommended Skills To Create; content: `dbf637225bec`; chunk: `eef80c572381`
- `ai-system/skills/README.md` lines 34-43; heading: Skills Layer Roadmap > Existing Useful Skills; content: `dbf637225bec`; chunk: `758bde12e28c`
- `ai-system/project-control/04-command-catalog.md` lines 64-118; heading: Project Control Command Catalog > Self-Hosted Command Boundary; content: `d6bfbf03256d`; chunk: `749381be335a`
- `ai-system/project-control/04-command-catalog.md` lines 21-63; heading: Project Control Command Catalog > Scope; content: `d6bfbf03256d`; chunk: `d914c61786e4`
- `ai-system/project-control/03-state-model.md` lines 104-125; heading: Project Control State Model > Context Control State; content: `9e818e514763`; chunk: `0cd80bdf0d55`
- `ai-system/project-control/06-prompt-package-spec.md` lines 874-906; heading: 17. Relationship To taskctl.py And codexctl.py; content: `3444e8d40e40`; chunk: `6cf68be89257`
- `ai-system/project-control/03-state-model.md` lines 71-103; heading: Project Control State Model > Documentation Control State; content: `9e818e514763`; chunk: `c68c7fcfa12b`
- `ai-system/project-control/06-prompt-package-spec.md` lines 123-162; heading: 3. Current Implementation; content: `3444e8d40e40`; chunk: `4fe051d2de08`

Retrieved Context Pack Content:

````text
<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-064 PIPE-13 Pipeline UI Dashboard Add a Web Control Center dashboard for pipeline sessions, queue preview, policy selection, run-next, and run-until-blocker. Expose supervised pipeline operation in the local Web Control Center without weakening confirmation, policy, or lifecycle gates. ai_project_ctl/web/server.py / ai_project_ctl/web/read_model.py Human Owner can inspect and operate supervised pipeline sessions from the local UI with explicit confirmation. Add Pipeline dashboard/page to the Web Control Center. Show policy selector/preset preview, queue selector, queue preview, session status, current step, gates, stop reason, and latest audit entries. Expose Create Session, Run Next, Run Until Blocker, Stop Session, and Refresh Status actions where implemented. Require explicit confirmation for any write/run action. Show action result panel with step status, blockers, changed/generated files, reports, reviews, and next actions. Keep UI local-only and route writes through governed commands/workflows. Add tests for dashboard rendering, confirmation requirements, and action routing. Do not add remote hosting. Do not bypass pipeline policy. Do not auto-start sessions on page load. Do not run arbitrary shell commands from UI. Do not hide blockers or failed gates. ai_project_ctl/web/read_model.py ai_project_ctl/web/server.py ai_project_ctl/web/actions.py ai_project_ctl/pipeline/** if UI integration requires compatible changes ai_project_ctl/core/registry.py if action metadata is needed scripts/aictl.py if routing is needed tests/test_web_control_center.py tests/** ai-system/project-control/** if UI documentation is needed Pipeline dashboard shows sessions, selected policy, queue preview, current step, and stop reason. Run actions require explicit confirmation. UI writes route through governed commands/workflows. Failed gates and blockers are visible. UI remains local-only by default. Tests and project-control validations pass. Verify UI cannot start or continue pipeline silently. Verify all mutations route through governed command paths.","schema_version":1,"task_id":"TASK-064"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-064`
Explicit query: `false`
Limit: `8`
Docs revision: `24`
Tasks revision: `582`

## Query

```text
TASK-064 PIPE-13 Pipeline UI Dashboard Add a Web Control Center dashboard for pipeline sessions, queue preview, policy selection, run-next, and run-until-blocker. Expose supervised pipeline operation in the local Web Control Center without weakening confirmation, policy, or lifecycle gates. ai_project_ctl/web/server.py / ai_project_ctl/web/read_model.py Human Owner can inspect and operate supervised pipeline sessions from the local UI with explicit confirmation. Add Pipeline dashboard/page to the Web Control Center. Show policy selector/preset preview, queue selector, queue preview, session status, current step, gates, stop reason, and latest audit entries. Expose Create Session, Run Next, Run Until Blocker, Stop Session, and Refresh Status actions where implemented. Require explicit confirmation for any write/run action. Show action result panel with step status, blockers, changed/generated files, reports, reviews, and next actions. Keep UI local-only and route writes through governed commands/workflows. Add tests for dashboard rendering, confirmation requirements, and action routing. Do not add remote hosting. Do not bypass pipeline policy. Do not auto-start sessions on page load. Do not run arbitrary shell commands from UI. Do not hide blockers or failed gates. ai_project_ctl/web/read_model.py ai_project_ctl/web/server.py ai_project_ctl/web/actions.py ai_project_ctl/pipeline/** if UI integration requires compatible changes ai_project_ctl/core/registry.py if action metadata is needed scripts/aictl.py if routing is needed tests/test_web_control_center.py tests/** ai-system/project-control/** if UI documentation is needed Pipeline dashboard shows sessions, selected policy, queue preview, current step, and stop reason. Run actions require explicit confirmation. UI writes route through governed commands/workflows. Failed gates and blockers are visible. UI remains local-only by default. Tests and project-control validations pass. Verify UI cannot start or continue pipeline silently. Verify all mutations route through governed command paths.
```

## Task Boundary Snapshot

Task: `TASK-064` - PIPE-13 Pipeline UI Dashboard
Status: `in_progress`

Scope:
- Add Pipeline dashboard/page to the Web Control Center.
- Show policy selector/preset preview, queue selector, queue preview, session status, current step, gates, stop reason, and latest audit entries.
- Expose Create Session, Run Next, Run Until Blocker, Stop Session, and Refresh Status actions where implemented.
- Require explicit confirmation for any write/run action.
- Show action result panel with step status, blockers, changed/generated files, reports, reviews, and next actions.
- Keep UI local-only and route writes through governed commands/workflows.
- Add tests for dashboard rendering, confirmation requirements, and action routing.

Allowed Files:
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/pipeline/** if UI integration requires compatible changes
- ai_project_ctl/core/registry.py if action metadata is needed
- scripts/aictl.py if routing is needed
- tests/test_web_control_center.py
- tests/**
- ai-system/project-control/** if UI documentation is needed

Acceptance Criteria:
- Pipeline dashboard shows sessions, selected policy, queue preview, current step, and stop reason.
- Run actions require explicit confirmation.
- UI writes route through governed commands/workflows.
- Failed gates and blockers are visible.
- UI remains local-only by default.
- Tests and project-control validations pass.

## Index Summary

Indexed source documents: `10`
Indexed chunks: `890`
Excluded registered sources: `134`
Selected chunks: `8`

Default exclusion policy: generated, inactive, archived, deprecated, template, and example documents are excluded unless explicitly allowed.

## Selected Sources

| Score | Source | Heading | Lines | Content hash | Chunk hash | Reasons |
| ---: | --- | --- | --- | --- | --- | --- |
| 153 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | heading token match: create, to; metadata token match: ai-system, create, to; content token match: a, actions, and, bypass, can, changes, commands, control |
| 127 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | metadata token match: ai-system; content token match: a, actions, add, and, blocker, blockers, by, bypass |
| 125 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Self-Hosted Command Boundary | 64-118 | `d6bfbf03256d` | `749381be335a` | heading token match: command, control; metadata token match: ai-system, command, control, project-control; content token match: a, ai-system, aictl, all, and, are, audit, by |
| 113 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Scope | 21-63 | `d6bfbf03256d` | `d914c61786e4` | heading token match: command, control; metadata token match: ai-system, command, control, project-control; content token match: a, actions, add, aictl, and, center, command, control |
| 97 | `ai-system/project-control/03-state-model.md` | Project Control State Model > Context Control State | 104-125 | `9e818e514763` | `0cd80bdf0d55` | heading token match: control; metadata token match: ai-system, control, project-control; content token match: a, and, are, by, control, current, default, files |
| 97 | `ai-system/project-control/06-prompt-package-spec.md` | 17. Relationship To taskctl.py And codexctl.py | 874-906 | `3444e8d40e40` | `6cf68be89257` | heading token match: and, py, to; metadata token match: ai-system, and, control, project-control, py, to; content token match: a, and, audit, by, bypass, can, current, for |
| 96 | `ai-system/project-control/03-state-model.md` | Project Control State Model > Documentation Control State | 71-103 | `9e818e514763` | `c68c7fcfa12b` | heading token match: control, documentation; metadata token match: ai-system, control, documentation, project-control; content token match: a, and, are, by, control, current, documentation, files |
| 94 | `ai-system/project-control/06-prompt-package-spec.md` | 3. Current Implementation | 123-162 | `3444e8d40e40` | `4fe051d2de08` | heading token match: current; metadata token match: ai-system, control, current, project-control; content token match: a, and, are, current, default, explicit, for, generated |

## Selected Context

### 1. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Recommended Skills To Create
Lines: `80-92`
Score: `153`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: heading token match: create, to; metadata token match: ai-system, create, to; content token match: a, actions, and, bypass, can, changes, commands, control

```text
## Recommended Skills To Create

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Documentation Control Skill | Guide documentation registration, status changes, generated indexes and documentation validation. | `docctl.py` | P0 | Register documents, set draft/review status, render/check generated docs, explain documentation lifecycle. | Mark documents active without Human Owner approval; manually edit `docs.json`, doc events or generated doc indexes. |
| Protected Files Skill | Keep agents inside the protected-files boundary and detect unsafe project-control edits. | `check-protected-project-files.py`, `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Explain protected paths, run protected-files checks, route repairs through CLIs. | Edit protected state/events/generated files manually; use ad hoc scripts to mutate protected files; hide drift. |
| Review Gate Skill | Guide review intake before a Task can be accepted or closed. | `taskctl.py`; future review control CLI if approved | P1 | Check scope, allowed files, acceptance criteria, validation output and review status; recommend APPROVED, REWORK, REJECTED or DEFERRED. | Self-approve work; mark a Task done without the required approval path; ignore Critical or Major findings. |

[...truncated by contextctl...]
```

### 2. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Existing Useful Skills
Lines: `34-43`
Score: `127`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: metadata token match: ai-system; content token match: a, actions, add, and, blocker, blockers, by, bypass

```text
## Existing Useful Skills

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Project Control Gateway Skill | Route plan, task, documentation and evolution work through the controlled CLI gateway instead of manual state edits. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Inspect state through CLI, choose allowed commands, run validation and render commands, report unsupported operations. | Manually edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**`; invent lifecycle states or commands; execute Initiative or Epic directly. |
| Clarification Gate Skill | Teach Codex and subagents when to inspect first, proceed with safe assumptions, or stop for Human Owner blocker questions. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Classify blockers, group owner questions, identify safe defaults, preserve task and approval boundaries. | Use questions to avoid normal inspection; ask for approval after every small step; self-approve accepted, approved, active or done states. |
| Documentation Navigation Skill | Route Codex and subagents to the minimal correct documentation and project-control read set before planning, editing, reviewing or executing AI_Development_System work.

[...truncated by contextctl...]
```

### 3. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Self-Hosted Command Boundary
Lines: `64-118`
Score: `125`
Content hash: `d6bfbf03256d4d5a7f005184d36c94434a45640595c0d654fc463065a1428adf`
Chunk hash: `749381be335ac66aa70d957f55a95f190d998afd70c4347643a6c88c059f6587`
Reasons: heading token match: command, control; metadata token match: ai-system, command, control, project-control; content token match: a, ai-system, aictl, all, and, are, audit, by

```text
## Self-Hosted Command Boundary

AI_Development_System now uses root `/AI_PROJECT` as its own self-hosted Project Control Layer. All protected state, event and generated files in that directory must be changed only through approved CLI gateways.

Current domain commands include:

```bash
python scripts/aictl.py ...
python scripts/planctl.py ...
python scripts/taskctl.py ...
python scripts/codexctl.py ...
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

`docctl.py` owns `AI_PROJECT/state/docs.json`, `AI_PROJECT/events/doc-events.jsonl`, `AI_PROJECT/generated/DOCS_INDEX.md` and `AI_PROJECT/generated/DOCS_GAPS.md`.

[...truncated by contextctl...]
```

### 4. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Scope
Lines: `21-63`
Score: `113`
Content hash: `d6bfbf03256d4d5a7f005184d36c94434a45640595c0d654fc463065a1428adf`
Chunk hash: `d914c61786e4b852b59e3a000d5c0b85638a7e8731366116abd8c8b8e9591815`
Reasons: heading token match: command, control; metadata token match: ai-system, command, control, project-control; content token match: a, actions, add, aictl, and, center, command, control

```text
## Scope

This document records the command boundary for Project Control Gateway.

The first implemented command surface was plan control:

```bash
python scripts/planctl.py <command>
```

The current owner-facing facade is:

```bash
python scripts/aictl.py <domain> <command>
```

Current implemented control domains include:

```text
plan        Project, Idea, Goal, Strategy, Initiative, Epic
task        Task, Current Task, generated task views
codex       current Codex prompt/status package
context     deterministic Context Pack generated output
docs        documentation registry and generated doc indexes
evolution   Evolution Change Proposals
web         local loopback Web Control Center
```

`aictl.py` is a facade and command registry. Domain ownership still belongs to the owning scripts such as `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py`, `contextctl.py` and `codexctl.py`.

Still-future or partial domains include:

```text
Execution Session
Review
QA Result
Decision
Release
Unified projectctl.py
```

These must not be invented through free-form AI actions. Add them only through approved system evolution and bounded Tasks.
```

### 5. `ai-system/project-control/03-state-model.md`

Title: Project Control State Model
Status: `active`  Type: `reference`
Heading: Project Control State Model > Context Control State
Lines: `104-125`
Score: `97`
Content hash: `9e818e514763e69aa2f56bb5d9ca080d47b7330db3aa016982c5d3ee0bc2be81`
Chunk hash: `0cd80bdf0d55e5284fa6355477f50005896398136bf33b7e1a181718f309f8b4`
Reasons: heading token match: control; metadata token match: ai-system, control, project-control; content token match: a, and, are, by, control, current, default, files

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

### 6. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 17. Relationship To taskctl.py And codexctl.py
Lines: `874-906`
Score: `97`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `6cf68be892579b77502246852781af90dc2942f367d5af5b0a3c4a4ee727323f`
Reasons: heading token match: and, py, to; metadata token match: ai-system, and, control, project-control, py, to; content token match: a, and, audit, by, bypass, can, current, for

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

### 7. `ai-system/project-control/03-state-model.md`

Title: Project Control State Model
Status: `active`  Type: `reference`
Heading: Project Control State Model > Documentation Control State
Lines: `71-103`
Score: `96`
Content hash: `9e818e514763e69aa2f56bb5d9ca080d47b7330db3aa016982c5d3ee0bc2be81`
Chunk hash: `c68c7fcfa12b1f98261105372d826707cb0cef9b3340f394ea7dc928123e4bc0`
Reasons: heading token match: control, documentation; metadata token match: ai-system, control, documentation, project-control; content token match: a, and, are, by, control, current, documentation, files

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

### 8. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 3. Current Implementation
Lines: `123-162`
Score: `94`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `4fe051d2de08383b0737cc69ca48f864bb8341acd7154ddc8b2d3a70fb1ad30a`
Reasons: heading token match: current; metadata token match: ai-system, control, current, project-control; content token match: a, and, are, current, default, explicit, for, generated

```text
# 3. Current Implementation

Current CLI:

```bash id="55p5jr"
python scripts/taskctl.py prompt build
```

Supported options:

```text id="xuo71y"
--task <TASK_ID>       Build prompt for a specific Task.
--write                Write prompt to AI_PROJECT/generated/CODEX_PROMPT.md.
--out <PATH>           Write prompt to custom output path.
--allow-inactive       Allow prompt build for non-executable statuses.
--skip-plan-check      Validate tasks without checking plan references.
```

Default behavior:

```text id="d56ig6"
If --task is not provided, taskctl.py uses current_task_id.
If no current task exists, prompt build fails.
If task status is not executable and --allow-inactive is not provided, prompt build fails.
```

Dedicated Codex execution CLI:

```bash
python scripts/codexctl.py build --task <TASK_ID>
python scripts/codexctl.py build --task <TASK_ID> --with-context
python scripts/codexctl.py build --task <TASK_ID> --context-pack AI_PROJECT/generated/CONTEXT_PACK.md
python scripts/codexctl.py status
python scripts/codexctl.py clear
```

`--with-context` uses the default generated Context Pack path. `--context-pack` allows an explicit repository-relative or absolute Context Pack path. Both options are read-only with respect to context generation; `contextctl.py` remains responsible for building and refreshing Context Packs.

---
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
- Pipeline dashboard shows sessions, selected policy, queue preview, current step, and stop reason.
- Run actions require explicit confirmation.
- UI writes route through governed commands/workflows.
- Failed gates and blockers are visible.
- UI remains local-only by default.
- Tests and project-control validations pass.

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
- Verify UI cannot start or continue pipeline silently.
- Verify all mutations route through governed command paths.

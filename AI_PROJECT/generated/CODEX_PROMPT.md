# Codex Prompt Package

Generated: 2026-06-19T15:37:29Z
Source Type: task
Source ID: TASK-043
Source Status: in_review

[SYSTEM]

Active Role:
Codex Executor

Active Stage:
Task Execution

Active Document:
AI_PROJECT/generated/CODEX_CURRENT.md

Expected Result:
Task completed according to acceptance criteria

Repository Context:
This repository is an AI Development System governance control plane.
Project-control state is managed through Python CLI gateways; generated Markdown is derived output.

Source:
Source Task: TASK-043
Task Status: in_review
Title: UIX-06 Update UI workflow documentation

Update owner-facing documentation for the improved UI cockpit, task filters, workflow buttons, Evolution tab, and bulk file import.

Document the new owner workflow after UI cockpit improvements so daily operation is clear and old manual command-heavy instructions are de-emphasized.

Scope:
- Update owner quickstart with UI-first daily workflow.
- Document Tasks filtering/grouping/collapse.
- Document task row workflow buttons.
- Document action result panel.
- Document Evolution management tab.
- Document Bulk Task Import from paste and file.
- Clarify that legacy ctl scripts remain compatibility tools.
- Clarify that UI writes route through governed workflows/commands.
- Run docctl validation/render/check-generated if documentation registry is used.

Out of Scope:
- Do not change command behavior.
- Do not add new UI actions.
- Do not edit generated docs manually.
- Do not mark docs accepted without Human Owner approval.

Allowed Files:
- README.md
- AGENTS.md
- ai-system/project-control/08-usage-guide.md
- ai-system/project-control/10-owner-quickstart.md
- ai-system/project-control/** if documentation index or appendix updates are needed
- AI_PROJECT/state/docs.json via docctl.py only
- AI_PROJECT/events/doc-events.jsonl via docctl.py only
- AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only
- AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only

Implementation Instructions:
- Inspect current files before editing.
- Stay within allowed files.
- Preserve existing conventions.
- Prefer minimal, commit-ready changes.
- Do not perform unrelated refactors.
- Do not edit AI_PROJECT/state/**, AI_PROJECT/events/** or AI_PROJECT/generated/** manually.

Retrieved Context:
- Context Pack path: `AI_PROJECT/generated/CONTEXT_PACK.md`
- Context Pack SHA-256: `56f8df540193dba43bf7416800ea76f2cf0f6922d0d7fa198a889bb3b6af5b73`
- Context mode: `task`
- Context task ID: `TASK-043`
- Docs revision: `24`
- Tasks revision: `468`

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
- `ai-system/project-control/03-state-model.md` lines 104-125; heading: Project Control State Model > Context Control State; content: `9e818e514763`; chunk: `0cd80bdf0d55`
- `ai-system/project-control/06-prompt-package-spec.md` lines 580-670; heading: 12. Prompt Package Template; content: `3444e8d40e40`; chunk: `4b3949b96350`
- `ai-system/project-control/03-state-model.md` lines 71-103; heading: Project Control State Model > Documentation Control State; content: `9e818e514763`; chunk: `c68c7fcfa12b`
- `ai-system/project-control/04-command-catalog.md` lines 21-63; heading: Project Control Command Catalog > Scope; content: `d6bfbf03256d`; chunk: `d914c61786e4`
- `ai-system/project-control/06-prompt-package-spec.md` lines 797-833; heading: 14. Context Budget Rules > Context Pack Boundary; content: `3444e8d40e40`; chunk: `24706f89c068`

Retrieved Context Pack Content:

````text
<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-043 UIX-06 Update UI workflow documentation Update owner-facing documentation for the improved UI cockpit, task filters, workflow buttons, Evolution tab, and bulk file import. Document the new owner workflow after UI cockpit improvements so daily operation is clear and old manual command-heavy instructions are de-emphasized. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Update owner quickstart with UI-first daily workflow. Document Tasks filtering/grouping/collapse. Document task row workflow buttons. Document action result panel. Document Evolution management tab. Document Bulk Task Import from paste and file. Clarify that legacy ctl scripts remain compatibility tools. Clarify that UI writes route through governed workflows/commands. Run docctl validation/render/check-generated if documentation registry is used. Do not change command behavior. Do not add new UI actions. Do not edit generated docs manually. Do not mark docs accepted without Human Owner approval. README.md AGENTS.md ai-system/project-control/08-usage-guide.md ai-system/project-control/10-owner-quickstart.md ai-system/project-control/** if documentation index or appendix updates are needed AI_PROJECT/state/docs.json via docctl.py only AI_PROJECT/events/doc-events.jsonl via docctl.py only AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only Documentation describes the UI-first daily workflow. Documentation explains task filters, workflow buttons, Evolution tab, and bulk file import. Documentation preserves protected-file and generated-output rules. Legacy ctl scripts are documented as compatibility layer. Documentation checks and project-control checks pass. Verify that documentation matches the implemented UI behavior. Verify that outdated command-heavy workflow is not presented as the preferred path.","schema_version":1,"task_id":"TASK-043"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-043`
Explicit query: `false`
Limit: `8`
Docs revision: `24`
Tasks revision: `468`

## Query

```text
TASK-043 UIX-06 Update UI workflow documentation Update owner-facing documentation for the improved UI cockpit, task filters, workflow buttons, Evolution tab, and bulk file import. Document the new owner workflow after UI cockpit improvements so daily operation is clear and old manual command-heavy instructions are de-emphasized. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Update owner quickstart with UI-first daily workflow. Document Tasks filtering/grouping/collapse. Document task row workflow buttons. Document action result panel. Document Evolution management tab. Document Bulk Task Import from paste and file. Clarify that legacy ctl scripts remain compatibility tools. Clarify that UI writes route through governed workflows/commands. Run docctl validation/render/check-generated if documentation registry is used. Do not change command behavior. Do not add new UI actions. Do not edit generated docs manually. Do not mark docs accepted without Human Owner approval. README.md AGENTS.md ai-system/project-control/08-usage-guide.md ai-system/project-control/10-owner-quickstart.md ai-system/project-control/** if documentation index or appendix updates are needed AI_PROJECT/state/docs.json via docctl.py only AI_PROJECT/events/doc-events.jsonl via docctl.py only AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only Documentation describes the UI-first daily workflow. Documentation explains task filters, workflow buttons, Evolution tab, and bulk file import. Documentation preserves protected-file and generated-output rules. Legacy ctl scripts are documented as compatibility layer. Documentation checks and project-control checks pass. Verify that documentation matches the implemented UI behavior. Verify that outdated command-heavy workflow is not presented as the preferred path.
```

## Task Boundary Snapshot

Task: `TASK-043` - UIX-06 Update UI workflow documentation
Status: `in_review`

Scope:
- Update owner quickstart with UI-first daily workflow.
- Document Tasks filtering/grouping/collapse.
- Document task row workflow buttons.
- Document action result panel.
- Document Evolution management tab.
- Document Bulk Task Import from paste and file.
- Clarify that legacy ctl scripts remain compatibility tools.
- Clarify that UI writes route through governed workflows/commands.
- Run docctl validation/render/check-generated if documentation registry is used.

Allowed Files:
- README.md
- AGENTS.md
- ai-system/project-control/08-usage-guide.md
- ai-system/project-control/10-owner-quickstart.md
- ai-system/project-control/** if documentation index or appendix updates are needed
- AI_PROJECT/state/docs.json via docctl.py only
- AI_PROJECT/events/doc-events.jsonl via docctl.py only
- AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only
- AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only

Acceptance Criteria:
- Documentation describes the UI-first daily workflow.
- Documentation explains task filters, workflow buttons, Evolution tab, and bulk file import.
- Documentation preserves protected-file and generated-output rules.
- Legacy ctl scripts are documented as compatibility layer.
- Documentation checks and project-control checks pass.

## Index Summary

Indexed source documents: `10`
Indexed chunks: `890`
Excluded registered sources: `134`
Selected chunks: `8`

Default exclusion policy: generated, inactive, archived, deprecated, template, and example documents are excluded unless explicitly allowed.

## Selected Sources

| Score | Source | Heading | Lines | Content hash | Chunk hash | Reasons |
| ---: | --- | --- | --- | --- | --- | --- |
| 177 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | heading token match: layer, to; metadata token match: ai-system, layer, md, readme, to; content token match: acceptance, accepted, actions, agents, and, approval, as, checks |
| 164 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | heading token match: layer; metadata token match: ai-system, layer, md, readme; content token match: acceptance, accepted, actions, add, after, agents, ai_project, and |
| 162 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Self-Hosted Command Boundary | 64-118 | `d6bfbf03256d` | `749381be335a` | heading token match: command; metadata token match: ai-system, command, md, project-control; content token match: acceptance, ai-system, ai_project, and, are, as, check-generated, command |
| 126 | `ai-system/project-control/03-state-model.md` | Project Control State Model > Context Control State | 104-125 | `9e818e514763` | `0cd80bdf0d55` | heading token match: state; metadata token match: ai-system, md, project-control, state; content token match: acceptance, ai_project, and, are, criteria, docs, events, file |
| 123 | `ai-system/project-control/06-prompt-package-spec.md` | 12. Prompt Package Template | 580-670 | `3444e8d40e40` | `4b3949b96350` | metadata token match: ai-system, md, project-control; content token match: acceptance, action, ai_project, and, change, checks, command, commands |
| 117 | `ai-system/project-control/03-state-model.md` | Project Control State Model > Documentation Control State | 71-103 | `9e818e514763` | `c68c7fcfa12b` | heading token match: documentation, state; metadata token match: ai-system, documentation, md, project-control, state; content token match: ai_project, and, are, as, doc-events, docctl, docs, docs_gaps |
| 108 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Scope | 21-63 | `d6bfbf03256d` | `d914c61786e4` | heading token match: command; metadata token match: ai-system, command, md, project-control; content token match: actions, add, and, as, change, command, docctl, docs |
| 102 | `ai-system/project-control/06-prompt-package-spec.md` | 14. Context Budget Rules > Context Pack Boundary | 797-833 | `3444e8d40e40` | `24706f89c068` | heading token match: rules; metadata token match: ai-system, md, project-control, rules; content token match: acceptance, add, and, change, criteria, docs, documentation, from |

## Selected Context

### 1. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Recommended Skills To Create
Lines: `80-92`
Score: `177`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: heading token match: layer, to; metadata token match: ai-system, layer, md, readme, to; content token match: acceptance, accepted, actions, agents, and, approval, as, checks

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
Score: `164`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: heading token match: layer; metadata token match: ai-system, layer, md, readme; content token match: acceptance, accepted, actions, add, after, agents, ai_project, and

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
Score: `162`
Content hash: `d6bfbf03256d4d5a7f005184d36c94434a45640595c0d654fc463065a1428adf`
Chunk hash: `749381be335ac66aa70d957f55a95f190d998afd70c4347643a6c88c059f6587`
Reasons: heading token match: command; metadata token match: ai-system, command, md, project-control; content token match: acceptance, ai-system, ai_project, and, are, as, check-generated, command

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

### 4. `ai-system/project-control/03-state-model.md`

Title: Project Control State Model
Status: `active`  Type: `reference`
Heading: Project Control State Model > Context Control State
Lines: `104-125`
Score: `126`
Content hash: `9e818e514763e69aa2f56bb5d9ca080d47b7330db3aa016982c5d3ee0bc2be81`
Chunk hash: `0cd80bdf0d55e5284fa6355477f50005896398136bf33b7e1a181718f309f8b4`
Reasons: heading token match: state; metadata token match: ai-system, md, project-control, state; content token match: acceptance, ai_project, and, are, criteria, docs, events, file

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
Heading: 12. Prompt Package Template
Lines: `580-670`
Score: `123`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `4b3949b963506d03a8ca61d2f28eb70f0cc2ca715a4c20495bab284ca4d8fcb0`
Reasons: metadata token match: ai-system, md, project-control; content token match: acceptance, action, ai_project, and, change, checks, command, commands

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

### 6. `ai-system/project-control/03-state-model.md`

Title: Project Control State Model
Status: `active`  Type: `reference`
Heading: Project Control State Model > Documentation Control State
Lines: `71-103`
Score: `117`
Content hash: `9e818e514763e69aa2f56bb5d9ca080d47b7330db3aa016982c5d3ee0bc2be81`
Chunk hash: `c68c7fcfa12b1f98261105372d826707cb0cef9b3340f394ea7dc928123e4bc0`
Reasons: heading token match: documentation, state; metadata token match: ai-system, documentation, md, project-control, state; content token match: ai_project, and, are, as, doc-events, docctl, docs, docs_gaps

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

### 7. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Scope
Lines: `21-63`
Score: `108`
Content hash: `d6bfbf03256d4d5a7f005184d36c94434a45640595c0d654fc463065a1428adf`
Chunk hash: `d914c61786e4b852b59e3a000d5c0b85638a7e8731366116abd8c8b8e9591815`
Reasons: heading token match: command; metadata token match: ai-system, command, md, project-control; content token match: actions, add, and, as, change, command, docctl, docs

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

### 8. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 14. Context Budget Rules > Context Pack Boundary
Lines: `797-833`
Score: `102`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `24706f89c068bb280d5630a712f0d9b260c02079a14823cc0a350875c71ba831`
Reasons: heading token match: rules; metadata token match: ai-system, md, project-control, rules; content token match: acceptance, add, and, change, criteria, docs, documentation, from

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
- Documentation describes the UI-first daily workflow.
- Documentation explains task filters, workflow buttons, Evolution tab, and bulk file import.
- Documentation preserves protected-file and generated-output rules.
- Legacy ctl scripts are documented as compatibility layer.
- Documentation checks and project-control checks pass.

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
- Verify that documentation matches the implemented UI behavior.
- Verify that outdated command-heavy workflow is not presented as the preferred path.

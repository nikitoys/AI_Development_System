# Codex Prompt Package

Generated: 2026-06-19T08:10:18Z
Source Type: task
Source ID: TASK-037
Source Status: in_progress

[SYSTEM]

Active Role:
Technical Writer AI / AI System Maintainer

Active Stage:
Workflow Automation Documentation Cleanup

Active Document:
AI_PROJECT/generated/CODEX_TASKS.md

Expected Result:
Documentation is updated after workflow automation features are implemented and checked through documentation/project-control validation.

Repository Context:
This repository is an AI Development System governance control plane.
Project-control state is managed through Python CLI gateways; generated Markdown is derived output.

Source:
Source Task: TASK-037
Task Status: in_progress
Title: WFA-06 Documentation Audit And Cleanup

Audit and update documentation after workflow automation and UI improvements are implemented.

Update owner-facing and system documentation so aictl, Web Control Center, workflows, Evolution Change wizard, task creation wizard, bulk import, review helpers, protected-file rules, and generated-output rules are current and non-contradictory.

Scope:
- Review README.md, AGENTS.md, project-control docs, owner quickstart, and usage guide.
- Make aictl/web/workflows the preferred owner-facing path.
- Keep legacy ctl scripts documented as compatibility tools.
- Remove or mark stale instructions.
- Document bulk task import format.
- Document Evolution Change wizard.
- Document Prepare for Codex workflow.
- Document review/close helpers.
- Run docctl validation/render/check-generated if docs registry is used.

Out of Scope:
- Do not change command behavior.
- Do not add new workflow behavior.
- Do not edit generated docs manually.
- Do not mark docs accepted without owner approval.

Allowed Files:
- README.md
- AGENTS.md
- ai-system/project-control/08-usage-guide.md
- ai-system/project-control/10-owner-quickstart.md
- ai-system/project-control/** if documentation index/appendix updates are needed
- AI_PROJECT/state/docs.json via docctl.py only
- AI_PROJECT/events/doc-events.jsonl via docctl.py only
- AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only
- AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/CODEX_CURRENT.md via taskctl.py only
- AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only

Implementation Instructions:
- Inspect current files before editing.
- Stay within allowed files.
- Preserve existing conventions.
- Prefer minimal, commit-ready changes.
- Do not perform unrelated refactors.
- Do not edit AI_PROJECT/state/**, AI_PROJECT/events/** or AI_PROJECT/generated/** manually.

Retrieved Context:
- Context Pack path: `AI_PROJECT/generated/CONTEXT_PACK.md`
- Context Pack SHA-256: `d8f72566e0a57562b5838603599bb17b43db94daaf414a8260924562a914019b`
- Context mode: `task`
- Context task ID: `TASK-037`
- Docs revision: `22`
- Tasks revision: `332`

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
- `ai-system/project-control/03-state-model.md` lines 71-103; heading: Project Control State Model > Documentation Control State; content: `b69e6c6ad9ac`; chunk: `c68c7fcfa12b`
- `ai-system/project-control/03-state-model.md` lines 104-125; heading: Project Control State Model > Context Control State; content: `b69e6c6ad9ac`; chunk: `0cd80bdf0d55`
- `ai-system/project-control/07-validation-and-tests.md` lines 24-66; heading: Project Control Validation and Tests > Scope; content: `035f37bb15d8`; chunk: `c7628c28ceb9`
- `ai-system/project-control/06-prompt-package-spec.md` lines 580-670; heading: 12. Prompt Package Template; content: `9304e03cf1dd`; chunk: `4b3949b96350`
- `ai-system/project-control/06-prompt-package-spec.md` lines 874-906; heading: 17. Relationship To taskctl.py And codexctl.py; content: `9304e03cf1dd`; chunk: `6cf68be89257`

Retrieved Context Pack Content:

````text
<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-037 WFA-06 Documentation Audit And Cleanup Audit and update documentation after workflow automation and UI improvements are implemented. Update owner-facing and system documentation so aictl, Web Control Center, workflows, Evolution Change wizard, task creation wizard, bulk import, review helpers, protected-file rules, and generated-output rules are current and non-contradictory. AI_PROJECT/generated/CODEX_TASKS.md Documentation is updated after workflow automation features are implemented and checked through documentation/project-control validation. Review README.md, AGENTS.md, project-control docs, owner quickstart, and usage guide. Make aictl/web/workflows the preferred owner-facing path. Keep legacy ctl scripts documented as compatibility tools. Remove or mark stale instructions. Document bulk task import format. Document Evolution Change wizard. Document Prepare for Codex workflow. Document review/close helpers. Run docctl validation/render/check-generated if docs registry is used. Do not change command behavior. Do not add new workflow behavior. Do not edit generated docs manually. Do not mark docs accepted without owner approval. README.md AGENTS.md ai-system/project-control/08-usage-guide.md ai-system/project-control/10-owner-quickstart.md ai-system/project-control/** if documentation index/appendix updates are needed AI_PROJECT/state/docs.json via docctl.py only AI_PROJECT/events/doc-events.jsonl via docctl.py only AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/CODEX_CURRENT.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only Documentation reflects the current aictl/web/workflow model. Legacy ctl scripts are described as compatibility layer. Bulk task import is documented. Evolution Change Flow is documented as controlled self-evolution. Generated files are clearly described as derived output. Protected-file rules are current. Documentation checks and project-control checks pass. Verify documentation consistency, stale instruction cleanup, protected/generated file rules, docctl checks, project-control checks, and no command behavior changes.","schema_version":1,"task_id":"TASK-037"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-037`
Explicit query: `false`
Limit: `8`
Docs revision: `22`
Tasks revision: `332`

## Query

```text
TASK-037 WFA-06 Documentation Audit And Cleanup Audit and update documentation after workflow automation and UI improvements are implemented. Update owner-facing and system documentation so aictl, Web Control Center, workflows, Evolution Change wizard, task creation wizard, bulk import, review helpers, protected-file rules, and generated-output rules are current and non-contradictory. AI_PROJECT/generated/CODEX_TASKS.md Documentation is updated after workflow automation features are implemented and checked through documentation/project-control validation. Review README.md, AGENTS.md, project-control docs, owner quickstart, and usage guide. Make aictl/web/workflows the preferred owner-facing path. Keep legacy ctl scripts documented as compatibility tools. Remove or mark stale instructions. Document bulk task import format. Document Evolution Change wizard. Document Prepare for Codex workflow. Document review/close helpers. Run docctl validation/render/check-generated if docs registry is used. Do not change command behavior. Do not add new workflow behavior. Do not edit generated docs manually. Do not mark docs accepted without owner approval. README.md AGENTS.md ai-system/project-control/08-usage-guide.md ai-system/project-control/10-owner-quickstart.md ai-system/project-control/** if documentation index/appendix updates are needed AI_PROJECT/state/docs.json via docctl.py only AI_PROJECT/events/doc-events.jsonl via docctl.py only AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/CODEX_CURRENT.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only Documentation reflects the current aictl/web/workflow model. Legacy ctl scripts are described as compatibility layer. Bulk task import is documented. Evolution Change Flow is documented as controlled self-evolution. Generated files are clearly described as derived output. Protected-file rules are current. Documentation checks and project-control checks pass. Verify documentation consistency, stale instruction cleanup, protected/generated file rules, docctl checks, project-control checks, and no command behavior changes.
```

## Task Boundary Snapshot

Task: `TASK-037` - WFA-06 Documentation Audit And Cleanup
Status: `in_progress`

Scope:
- Review README.md, AGENTS.md, project-control docs, owner quickstart, and usage guide.
- Make aictl/web/workflows the preferred owner-facing path.
- Keep legacy ctl scripts documented as compatibility tools.
- Remove or mark stale instructions.
- Document bulk task import format.
- Document Evolution Change wizard.
- Document Prepare for Codex workflow.
- Document review/close helpers.
- Run docctl validation/render/check-generated if docs registry is used.

Allowed Files:
- README.md
- AGENTS.md
- ai-system/project-control/08-usage-guide.md
- ai-system/project-control/10-owner-quickstart.md
- ai-system/project-control/** if documentation index/appendix updates are needed
- AI_PROJECT/state/docs.json via docctl.py only
- AI_PROJECT/events/doc-events.jsonl via docctl.py only
- AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only
- AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/CODEX_CURRENT.md via taskctl.py only
- AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only

Acceptance Criteria:
- Documentation reflects the current aictl/web/workflow model.
- Legacy ctl scripts are described as compatibility layer.
- Bulk task import is documented.
- Evolution Change Flow is documented as controlled self-evolution.
- Generated files are clearly described as derived output.
- Protected-file rules are current.
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
| 228 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Self-Hosted Command Boundary | 64-116 | `a1985ca2f321` | `b755c971df05` | heading token match: command, control; metadata token match: ai-system, command, control, md, project-control; content token match: ai-system, ai_project, and, are, as, audit, check-generated, command |
| 215 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | heading token match: layer; metadata token match: ai-system, guide, layer, md, readme; content token match: accepted, agents, and, approval, as, changes, checks, control |
| 187 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | heading token match: layer; metadata token match: ai-system, guide, layer, md, readme; content token match: accepted, add, after, agents, ai_project, and, approval, as |
| 156 | `ai-system/project-control/03-state-model.md` | Project Control State Model > Documentation Control State | 71-103 | `b69e6c6ad9ac` | `c68c7fcfa12b` | heading token match: control, documentation, model, state; metadata token match: ai-system, control, documentation, md, model, project-control, state; content token match: ai_project, and, are, as, control, current, derived, doc-events |
| 153 | `ai-system/project-control/03-state-model.md` | Project Control State Model > Context Control State | 104-125 | `b69e6c6ad9ac` | `0cd80bdf0d55` | heading token match: control, model, state; metadata token match: ai-system, control, md, model, project-control, state; content token match: ai_project, and, are, control, current, derived, docs, events |
| 138 | `ai-system/project-control/07-validation-and-tests.md` | Project Control Validation and Tests > Scope | 24-66 | `035f37bb15d8` | `c7628c28ceb9` | heading token match: and, control, validation; metadata token match: ai-system, and, control, md, project-control, validation; content token match: ai_project, and, audit, codex, codex_current, codex_tasks, control, controlled |
| 132 | `ai-system/project-control/06-prompt-package-spec.md` | 12. Prompt Package Template | 580-670 | `9304e03cf1dd` | `4b3949b96350` | metadata token match: ai-system, control, md, project-control; content token match: ai_project, and, change, checks, command, current, do, docs |
| 122 | `ai-system/project-control/06-prompt-package-spec.md` | 17. Relationship To taskctl.py And codexctl.py | 874-906 | `9304e03cf1dd` | `6cf68be89257` | heading token match: and, py, taskctl; metadata token match: ai-system, and, control, md, project-control, py, taskctl; content token match: and, audit, codex, current, events, for, generated, index |

## Selected Context

### 1. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Self-Hosted Command Boundary
Lines: `64-116`
Score: `228`
Content hash: `a1985ca2f3219254917601872017052dcfc6ae74f1f636fa6fdbe6a6a3227d32`
Chunk hash: `b755c971df05cf7e6b08835383033a087a162359ce3241ab86018beb96506a9d`
Reasons: heading token match: command, control; metadata token match: ai-system, command, control, md, project-control; content token match: ai-system, ai_project, and, are, as, audit, check-generated, command

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
Score: `215`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: heading token match: layer; metadata token match: ai-system, guide, layer, md, readme; content token match: accepted, agents, and, approval, as, changes, checks, control

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
Score: `187`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: heading token match: layer; metadata token match: ai-system, guide, layer, md, readme; content token match: accepted, add, after, agents, ai_project, and, approval, as

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
Heading: Project Control State Model > Documentation Control State
Lines: `71-103`
Score: `156`
Content hash: `b69e6c6ad9acbaf0bb398fd6ad729bb07290b6138e99a3535701e57c750a244d`
Chunk hash: `c68c7fcfa12b1f98261105372d826707cb0cef9b3340f394ea7dc928123e4bc0`
Reasons: heading token match: control, documentation, model, state; metadata token match: ai-system, control, documentation, md, model, project-control, state; content token match: ai_project, and, are, as, control, current, derived, doc-events

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

### 5. `ai-system/project-control/03-state-model.md`

Title: Project Control State Model
Status: `active`  Type: `reference`
Heading: Project Control State Model > Context Control State
Lines: `104-125`
Score: `153`
Content hash: `b69e6c6ad9acbaf0bb398fd6ad729bb07290b6138e99a3535701e57c750a244d`
Chunk hash: `0cd80bdf0d55e5284fa6355477f50005896398136bf33b7e1a181718f309f8b4`
Reasons: heading token match: control, model, state; metadata token match: ai-system, control, md, model, project-control, state; content token match: ai_project, and, are, control, current, derived, docs, events

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

### 6. `ai-system/project-control/07-validation-and-tests.md`

Title: Project Control Validation and Tests
Status: `active`  Type: `process`
Heading: Project Control Validation and Tests > Scope
Lines: `24-66`
Score: `138`
Content hash: `035f37bb15d8f601aff97abc4f3378961d0524d7a96fae5f03239239e9aee12c`
Chunk hash: `c7628c28ceb90b78d021d891a5ed10b1dc2cf8a114509631a433dd7fcc04c70d`
Reasons: heading token match: and, control, validation; metadata token match: ai-system, and, control, md, project-control, validation; content token match: ai_project, and, audit, codex, codex_current, codex_tasks, control, controlled

```text
## Scope

This document covers validation and tests for the current implemented control layers:

```text id="rfm6au"
scripts/planctl.py
scripts/taskctl.py
```

Current controlled state:

```text id="k8l7sl"
AI_PROJECT/state/plan.json
AI_PROJECT/state/tasks.json
```

Current audit logs:

```text id="khg80k"
AI_PROJECT/events/plan-events.jsonl
AI_PROJECT/events/task-events.jsonl
```

Current generated output:

```text id="orptmz"
AI_PROJECT/generated/CODEX_PLAN.md
AI_PROJECT/generated/CODEX_TASKS.md
AI_PROJECT/generated/CODEX_CURRENT.md
AI_PROJECT/generated/CODEX_PROMPT.md
```

This document also defines future validation expectations for:

```text id="btrtt0"
evolutionctl.py
protected-files check
CI integration
Codex plugin/skill integration
```

---
```

### 7. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 12. Prompt Package Template
Lines: `580-670`
Score: `132`
Content hash: `9304e03cf1dd12bb320887a0e1e1c90bb87259f60bf4a86d63a904b4e7e87210`
Chunk hash: `4b3949b963506d03a8ca61d2f28eb70f0cc2ca715a4c20495bab284ca4d8fcb0`
Reasons: metadata token match: ai-system, control, md, project-control; content token match: ai_project, and, change, checks, command, current, do, docs

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

### 8. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 17. Relationship To taskctl.py And codexctl.py
Lines: `874-906`
Score: `122`
Content hash: `9304e03cf1dd12bb320887a0e1e1c90bb87259f60bf4a86d63a904b4e7e87210`
Chunk hash: `6cf68be892579b77502246852781af90dc2942f367d5af5b0a3c4a4ee727323f`
Reasons: heading token match: and, py, taskctl; metadata token match: ai-system, and, control, md, project-control, py, taskctl; content token match: and, audit, codex, current, events, for, generated, index

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
- Documentation reflects the current aictl/web/workflow model.
- Legacy ctl scripts are described as compatibility layer.
- Bulk task import is documented.
- Evolution Change Flow is documented as controlled self-evolution.
- Generated files are clearly described as derived output.
- Protected-file rules are current.
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
- Verify documentation consistency, stale instruction cleanup, protected/generated file rules, docctl checks, project-control checks, and no command behavior changes.

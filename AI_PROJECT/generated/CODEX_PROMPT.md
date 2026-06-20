# Codex Prompt Package

Generated: 2026-06-20T10:49:11Z
Source Type: task
Source ID: TASK-068
Source Status: in_progress

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
Source Task: TASK-068
Task Status: in_progress
Title: PIPE-17 Add Custom Pipeline Policy Preset Store

Add governed storage for user-defined pipeline policy presets while keeping built-in safe presets immutable.

Introduce a persistent custom policy preset store so the Human Owner can save, validate, list, and delete pipeline policy presets without editing Python source or protected state manually.

Scope:
- Create a governed custom pipeline policy preset storage model.
- Store custom presets separately from built-in presets.
- Keep built-in presets dry_run, supervised, supervised_autoclose, and supervised_local_commit immutable.
- Validate saved presets through the existing PipelinePolicy validation rules.
- Reject unsafe presets with stable error codes.
- Add audit events for preset create/update/delete operations.
- Add generated policy status output if useful for UI and validation.

Out of Scope:
- Do not allow custom presets to authorize push, merge, reset, rebase, clean, or destructive git operations.
- Do not allow custom presets to bypass Token Budget Gate, Machine Review, Codex Review, Human Owner approval, or Evolution Change gates.
- Do not modify built-in preset definitions except for compatibility wiring.
- Do not edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/** manually.

Allowed Files:
- ai_project_ctl/pipeline/policy.py
- ai_project_ctl/pipeline/policy_store.py
- ai_project_ctl/pipeline/__init__.py
- ai_project_ctl/core/registry.py
- scripts/aictl.py
- AI_PROJECT/state/pipeline_policy_presets.json via governed CLI/service only
- AI_PROJECT/events/pipeline-policy-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_POLICIES.md via governed CLI/service only
- tests/**

Implementation Instructions:
- Inspect current files before editing.
- Stay within allowed files.
- Preserve existing conventions.
- Prefer minimal, commit-ready changes.
- Do not perform unrelated refactors.
- Do not edit AI_PROJECT/state/**, AI_PROJECT/events/** or AI_PROJECT/generated/** manually.

Retrieved Context:
- Context Pack path: `AI_PROJECT/generated/CONTEXT_PACK.md`
- Context Pack SHA-256: `e94e00074b9ac6629b6fac84a17ddb2bc10c9e475b7c764d7120b23e7232417e`
- Context mode: `task`
- Context task ID: `TASK-068`
- Docs revision: `27`
- Tasks revision: `615`

Retrieved Context Rules:
- Retrieved context is read-only.
- Retrieved context does not expand Allowed Files.
- Retrieved context does not expand Scope or override Out of Scope.
- Retrieved context does not replace Acceptance Criteria.
- If retrieved context conflicts with the source Task, source documents, or Human Owner instructions, report the conflict.

Retrieved Context Source Metadata:
- `ai-system/skills/README.md` lines 34-43; heading: Skills Layer Roadmap > Existing Useful Skills; content: `dbf637225bec`; chunk: `758bde12e28c`
- `ai-system/skills/README.md` lines 80-92; heading: Skills Layer Roadmap > Recommended Skills To Create; content: `dbf637225bec`; chunk: `eef80c572381`
- `ai-system/project-control/04-command-catalog.md` lines 2294-2321; heading: 18. Additional Command Domains > Pipeline Commands; content: `f824429b0a39`; chunk: `efe882b18c98`
- `ai-system/project-control/04-command-catalog.md` lines 65-119; heading: Project Control Command Catalog > Self-Hosted Command Boundary; content: `f824429b0a39`; chunk: `5b78d4503548`
- `ai-system/project-control/03-state-model.md` lines 104-125; heading: Project Control State Model > Context Control State; content: `9e818e514763`; chunk: `0cd80bdf0d55`
- `ai-system/project-control/06-prompt-package-spec.md` lines 874-906; heading: 17. Relationship To taskctl.py And codexctl.py; content: `3444e8d40e40`; chunk: `6cf68be89257`
- `ai-system/project-control/06-prompt-package-spec.md` lines 797-833; heading: 14. Context Budget Rules > Context Pack Boundary; content: `3444e8d40e40`; chunk: `24706f89c068`
- `ai-system/project-control/05-lifecycle-rules.md` lines 67-90; heading: 1. Global Lifecycle Rules > 1.1 State Must Change Only Through CLI; content: `69165d09d150`; chunk: `b097c4666cbb`

Retrieved Context Pack Content:

````text
<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-068 PIPE-17 Add Custom Pipeline Policy Preset Store Add governed storage for user-defined pipeline policy presets while keeping built-in safe presets immutable. Introduce a persistent custom policy preset store so the Human Owner can save, validate, list, and delete pipeline policy presets without editing Python source or protected state manually. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Create a governed custom pipeline policy preset storage model. Store custom presets separately from built-in presets. Keep built-in presets dry_run, supervised, supervised_autoclose, and supervised_local_commit immutable. Validate saved presets through the existing PipelinePolicy validation rules. Reject unsafe presets with stable error codes. Add audit events for preset create/update/delete operations. Add generated policy status output if useful for UI and validation. Do not allow custom presets to authorize push, merge, reset, rebase, clean, or destructive git operations. Do not allow custom presets to bypass Token Budget Gate, Machine Review, Codex Review, Human Owner approval, or Evolution Change gates. Do not modify built-in preset definitions except for compatibility wiring. Do not edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/** manually. ai_project_ctl/pipeline/policy.py ai_project_ctl/pipeline/policy_store.py ai_project_ctl/pipeline/__init__.py ai_project_ctl/core/registry.py scripts/aictl.py AI_PROJECT/state/pipeline_policy_presets.json via governed CLI/service only AI_PROJECT/events/pipeline-policy-events.jsonl via governed CLI/service only AI_PROJECT/generated/PIPELINE_POLICIES.md via governed CLI/service only tests/** Custom policy presets can be saved, loaded, validated, listed, and deleted through governed service paths. Built-in policy presets remain available and immutable. Invalid or unsafe custom presets are rejected before persistence. Preset changes create audit events. No direct protected-file writes are introduced. Tests and project-control validations pass. Verify that custom presets cannot weaken forbidden safety boundaries. Verify that built-in presets cannot be overwritten or deleted. Verify that all persistence goes through governed service paths.","schema_version":1,"task_id":"TASK-068"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-068`
Explicit query: `false`
Limit: `8`
Docs revision: `27`
Tasks revision: `615`

## Query

```text
TASK-068 PIPE-17 Add Custom Pipeline Policy Preset Store Add governed storage for user-defined pipeline policy presets while keeping built-in safe presets immutable. Introduce a persistent custom policy preset store so the Human Owner can save, validate, list, and delete pipeline policy presets without editing Python source or protected state manually. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Create a governed custom pipeline policy preset storage model. Store custom presets separately from built-in presets. Keep built-in presets dry_run, supervised, supervised_autoclose, and supervised_local_commit immutable. Validate saved presets through the existing PipelinePolicy validation rules. Reject unsafe presets with stable error codes. Add audit events for preset create/update/delete operations. Add generated policy status output if useful for UI and validation. Do not allow custom presets to authorize push, merge, reset, rebase, clean, or destructive git operations. Do not allow custom presets to bypass Token Budget Gate, Machine Review, Codex Review, Human Owner approval, or Evolution Change gates. Do not modify built-in preset definitions except for compatibility wiring. Do not edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/** manually. ai_project_ctl/pipeline/policy.py ai_project_ctl/pipeline/policy_store.py ai_project_ctl/pipeline/__init__.py ai_project_ctl/core/registry.py scripts/aictl.py AI_PROJECT/state/pipeline_policy_presets.json via governed CLI/service only AI_PROJECT/events/pipeline-policy-events.jsonl via governed CLI/service only AI_PROJECT/generated/PIPELINE_POLICIES.md via governed CLI/service only tests/** Custom policy presets can be saved, loaded, validated, listed, and deleted through governed service paths. Built-in policy presets remain available and immutable. Invalid or unsafe custom presets are rejected before persistence. Preset changes create audit events. No direct protected-file writes are introduced. Tests and project-control validations pass. Verify that custom presets cannot weaken forbidden safety boundaries. Verify that built-in presets cannot be overwritten or deleted. Verify that all persistence goes through governed service paths.
```

## Task Boundary Snapshot

Task: `TASK-068` - PIPE-17 Add Custom Pipeline Policy Preset Store
Status: `in_progress`

Scope:
- Create a governed custom pipeline policy preset storage model.
- Store custom presets separately from built-in presets.
- Keep built-in presets dry_run, supervised, supervised_autoclose, and supervised_local_commit immutable.
- Validate saved presets through the existing PipelinePolicy validation rules.
- Reject unsafe presets with stable error codes.
- Add audit events for preset create/update/delete operations.
- Add generated policy status output if useful for UI and validation.

Allowed Files:
- ai_project_ctl/pipeline/policy.py
- ai_project_ctl/pipeline/policy_store.py
- ai_project_ctl/pipeline/__init__.py
- ai_project_ctl/core/registry.py
- scripts/aictl.py
- AI_PROJECT/state/pipeline_policy_presets.json via governed CLI/service only
- AI_PROJECT/events/pipeline-policy-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_POLICIES.md via governed CLI/service only
- tests/**

Acceptance Criteria:
- Custom policy presets can be saved, loaded, validated, listed, and deleted through governed service paths.
- Built-in policy presets remain available and immutable.
- Invalid or unsafe custom presets are rejected before persistence.
- Preset changes create audit events.
- No direct protected-file writes are introduced.
- Tests and project-control validations pass.

## Index Summary

Indexed source documents: `10`
Indexed chunks: `891`
Excluded registered sources: `135`
Selected chunks: `8`

Default exclusion policy: generated, inactive, archived, deprecated, template, and example documents are excluded unless explicitly allowed.

## Selected Sources

| Score | Source | Heading | Lines | Content hash | Chunk hash | Reasons |
| ---: | --- | --- | --- | --- | --- | --- |
| 199 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | heading token match: existing, useful; metadata token match: existing, md, useful; content token match: a, acceptance, add, ai_project, allow, and, approval, authorize |
| 191 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | heading token match: create, to; metadata token match: create, md, to; content token match: a, acceptance, and, approval, authorize, be, before, boundaries |
| 147 | `ai-system/project-control/04-command-catalog.md` | 18. Additional Command Domains > Pipeline Commands | 2294-2321 | `f824429b0a39` | `efe882b18c98` | heading token match: pipeline; metadata token match: md, pipeline, project-control; content token match: acceptance, ai_project, ai_project_ctl, aictl, and, approval, are, audit |
| 142 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Self-Hosted Command Boundary | 65-119 | `f824429b0a39` | `5b78d4503548` | metadata token match: md, project-control; content token match: a, acceptance, ai_project, aictl, all, and, are, audit |
| 136 | `ai-system/project-control/03-state-model.md` | Project Control State Model > Context Control State | 104-125 | `9e818e514763` | `0cd80bdf0d55` | heading token match: model, state; metadata token match: md, model, project-control, state; content token match: a, acceptance, ai_project, and, are, be, criteria, events |
| 118 | `ai-system/project-control/06-prompt-package-spec.md` | 17. Relationship To taskctl.py And codexctl.py | 874-906 | `3444e8d40e40` | `6cf68be89257` | heading token match: and, py, to; metadata token match: and, md, project-control, py, to; content token match: a, and, audit, be, before, bypass, can, codex |
| 112 | `ai-system/project-control/06-prompt-package-spec.md` | 14. Context Budget Rules > Context Pack Boundary | 797-833 | `3444e8d40e40` | `24706f89c068` | heading token match: budget, rules; metadata token match: budget, md, project-control, rules; content token match: a, acceptance, add, and, audit, before, change, codex |
| 106 | `ai-system/project-control/05-lifecycle-rules.md` | 1. Global Lifecycle Rules > 1.1 State Must Change Only Through CLI | 67-90 | `69165d09d150` | `b097c4666cbb` | heading token match: change, cli, only, rules, state, through; metadata token match: change, cli, md, only, project-control, rules, state, through; content token match: ai_project, aictl, be, change, cli, events, generated, manually |

## Selected Context

### 1. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Existing Useful Skills
Lines: `34-43`
Score: `199`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: heading token match: existing, useful; metadata token match: existing, md, useful; content token match: a, acceptance, add, ai_project, allow, and, approval, authorize

```text
## Existing Useful Skills

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Project Control Gateway Skill | Route plan, task, documentation and evolution work through the controlled CLI gateway instead of manual state edits. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Inspect state through CLI, choose allowed commands, run validation and render commands, report unsupported operations. | Manually edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**`; invent lifecycle states or commands; execute Initiative or Epic directly. |
| Clarification Gate Skill | Teach Codex and subagents when to inspect first, proceed with safe assumptions, or stop for Human Owner blocker questions. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Classify blockers, group owner questions, identify safe defaults, preserve task and approval boundaries. | Use questions to avoid normal inspection; ask for approval after every small step; self-approve accepted, approved, active or done states. |
| Documentation Navigation Skill | Route Codex and subagents to the minimal correct documentation and project-control read set before planning, editing, reviewing or executing AI_Development_System work.

[...truncated by contextctl...]
```

### 2. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Recommended Skills To Create
Lines: `80-92`
Score: `191`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: heading token match: create, to; metadata token match: create, md, to; content token match: a, acceptance, and, approval, authorize, be, before, boundaries

```text
## Recommended Skills To Create

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Documentation Control Skill | Guide documentation registration, status changes, generated indexes and documentation validation. | `docctl.py` | P0 | Register documents, set draft/review status, render/check generated docs, explain documentation lifecycle. | Mark documents active without Human Owner approval; manually edit `docs.json`, doc events or generated doc indexes. |
| Protected Files Skill | Keep agents inside the protected-files boundary and detect unsafe project-control edits. | `check-protected-project-files.py`, `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Explain protected paths, run protected-files checks, route repairs through CLIs. | Edit protected state/events/generated files manually; use ad hoc scripts to mutate protected files; hide drift. |
| Review Gate Skill | Guide review intake before a Task can be accepted or closed. | `taskctl.py`; future review control CLI if approved | P1 | Check scope, allowed files, acceptance criteria, validation output and review status; recommend APPROVED, REWORK, REJECTED or DEFERRED. | Self-approve work; mark a Task done without the required approval path; ignore Critical or Major findings. |

[...truncated by contextctl...]
```

### 3. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: 18. Additional Command Domains > Pipeline Commands
Lines: `2294-2321`
Score: `147`
Content hash: `f824429b0a394aec9bfe9157302c1059a181374f040adbfb8136d2673f7fb1b6`
Chunk hash: `efe882b18c987d13ed38a60c38d0a9ba2dccd1c95061f72f79901f6f007ad46a`
Reasons: heading token match: pipeline; metadata token match: md, pipeline, project-control; content token match: acceptance, ai_project, ai_project_ctl, aictl, and, approval, are, audit

```text
## Pipeline Commands

```text
pipeline status
pipeline validate
pipeline render
pipeline check-generated
pipeline session create
pipeline session start-step
pipeline session step-result
pipeline session stop
pipeline session complete
pipeline run-next
pipeline run-until-blocker
```

Current implementation entry point:

```bash
python scripts/aictl.py pipeline ...
```

Pipeline commands manage supervised pipeline sessions, selected queues, policy snapshots, gate outcomes, stop reasons, generated pipeline status and generated pipeline audit output. They must route through `aictl.py` and the `ai_project_ctl/pipeline/**` services. They must not manually edit `AI_PROJECT/state/pipeline_sessions.json`, `AI_PROJECT/events/pipeline-events.jsonl`, `AI_PROJECT/generated/PIPELINE_STATUS.md` or `AI_PROJECT/generated/PIPELINE_AUDIT.md`.

`pipeline run-next` advances at most one guarded step. `pipeline run-until-blocker` composes `run-next`, requires `--confirm`, stops on the first blocker or queue completion and does not introduce background execution.

Pipeline policies must not authorize push, merge, automatic Evolution Change approval, automatic Evolution Change acceptance, or Human Owner final acceptance. Local commits, when policy-enabled, are local-only and require passing report, machine review, Codex review and commit-readiness gates.
```

### 4. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Self-Hosted Command Boundary
Lines: `65-119`
Score: `142`
Content hash: `f824429b0a394aec9bfe9157302c1059a181374f040adbfb8136d2673f7fb1b6`
Chunk hash: `5b78d45035483b51a58d0a7bed1cf1402fe3b2e6bc9a7ffcda911c0d12fcb6bc`
Reasons: metadata token match: md, project-control; content token match: a, acceptance, ai_project, aictl, all, and, are, audit

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

### 5. `ai-system/project-control/03-state-model.md`

Title: Project Control State Model
Status: `active`  Type: `reference`
Heading: Project Control State Model > Context Control State
Lines: `104-125`
Score: `136`
Content hash: `9e818e514763e69aa2f56bb5d9ca080d47b7330db3aa016982c5d3ee0bc2be81`
Chunk hash: `0cd80bdf0d55e5284fa6355477f50005896398136bf33b7e1a181718f309f8b4`
Reasons: heading token match: model, state; metadata token match: md, model, project-control, state; content token match: a, acceptance, ai_project, and, are, be, criteria, events

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
Score: `118`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `6cf68be892579b77502246852781af90dc2942f367d5af5b0a3c4a4ee727323f`
Reasons: heading token match: and, py, to; metadata token match: and, md, project-control, py, to; content token match: a, and, audit, be, before, bypass, can, codex

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

### 7. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 14. Context Budget Rules > Context Pack Boundary
Lines: `797-833`
Score: `112`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `24706f89c068bb280d5630a712f0d9b260c02079a14823cc0a350875c71ba831`
Reasons: heading token match: budget, rules; metadata token match: budget, md, project-control, rules; content token match: a, acceptance, add, and, audit, before, change, codex

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

### 8. `ai-system/project-control/05-lifecycle-rules.md`

Title: Project Control Lifecycle Rules
Status: `active`  Type: `lifecycle`
Heading: 1. Global Lifecycle Rules > 1.1 State Must Change Only Through CLI
Lines: `67-90`
Score: `106`
Content hash: `69165d09d150a2b5382e4f64fd813eb6a7c63454a92fa521af931da4d4004d57`
Chunk hash: `b097c4666cbbc6061f445920c53f5229bd91e4421241ad9ad4e0e3d4836d83e8`
Reasons: heading token match: change, cli, only, rules, state, through; metadata token match: change, cli, md, only, project-control, rules, state, through; content token match: ai_project, aictl, be, change, cli, events, generated, manually

```text
## 1.1 State Must Change Only Through CLI

Protected state must not be changed manually.

Protected files:

```text
AI_PROJECT/state/**
AI_PROJECT/events/**
AI_PROJECT/generated/**
```

Allowed mutation path:

```bash
python scripts/planctl.py ...
python scripts/taskctl.py ...
python scripts/evolutionctl.py ...
python scripts/contextctl.py ...
python scripts/codexctl.py ...
```

`aictl.py` may be used as the owner-facing facade when the operation is exposed through the command registry.
```

## Excluded Source Summary

- inactive document excluded by default: `94`
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
- Custom policy presets can be saved, loaded, validated, listed, and deleted through governed service paths.
- Built-in policy presets remain available and immutable.
- Invalid or unsafe custom presets are rejected before persistence.
- Preset changes create audit events.
- No direct protected-file writes are introduced.
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
- Verify that custom presets cannot weaken forbidden safety boundaries.
- Verify that built-in presets cannot be overwritten or deleted.
- Verify that all persistence goes through governed service paths.

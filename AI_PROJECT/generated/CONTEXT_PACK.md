<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-257 Demote recovered close workflow warnings Hide recovered close-time context/protected check warnings from owner-facing output when post-close context refresh succeeds. During close, contextctl.check-generated and protected.check can temporarily warn because task state changes make generated files stale before post-close refresh repairs them. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Identify non-blocking close workflow warnings from generated context and protected-file checks that are later repaired by post-close context_refresh. Keep recovered warning evidence in technical artifacts or debug details. Remove or demote recovered warnings from owner-facing Action Result and pipeline summary warnings. Ensure unrelated non-blocking warnings still remain visible to the owner. Add regression tests for recovered warnings and unrecovered warnings. Do not remove warning collection entirely. Do not suppress warnings when post-close context_refresh fails or is missing. Do not change task close state transitions. Do not edit protected project-control files manually. ai_project_ctl/pipeline/close_phase.py ai_project_ctl/pipeline/runner.py ai_project_ctl/web/server.py ai_project_ctl/web/read_model.py tests/test_pipeline_phase_review_close.py tests/test_pipeline_runner.py tests/test_web_control_center.py Recovered contextctl.check-generated warnings are not shown as owner-facing warnings when post-close context_refresh succeeds. Recovered protected.check stale context or prompt warnings are not shown as owner-facing warnings when post-close context_refresh succeeds. Technical evidence still records that the non-blocking checks warned during close. Warnings remain owner-facing when post-close context_refresh fails, is missing, or does not repair the stale generated files. Focused close-phase, runner, and Web Control Center tests pass. Check that warning demotion is conditional on successful post-close repair evidence. Confirm that no real blocking warning is hidden.","schema_version":1,"task_id":"TASK-257"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-257`
Explicit query: `false`
Limit: `8`
Docs revision: `28`
Tasks revision: `1754`

## Query

```text
TASK-257 Demote recovered close workflow warnings Hide recovered close-time context/protected check warnings from owner-facing output when post-close context refresh succeeds. During close, contextctl.check-generated and protected.check can temporarily warn because task state changes make generated files stale before post-close refresh repairs them. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Identify non-blocking close workflow warnings from generated context and protected-file checks that are later repaired by post-close context_refresh. Keep recovered warning evidence in technical artifacts or debug details. Remove or demote recovered warnings from owner-facing Action Result and pipeline summary warnings. Ensure unrelated non-blocking warnings still remain visible to the owner. Add regression tests for recovered warnings and unrecovered warnings. Do not remove warning collection entirely. Do not suppress warnings when post-close context_refresh fails or is missing. Do not change task close state transitions. Do not edit protected project-control files manually. ai_project_ctl/pipeline/close_phase.py ai_project_ctl/pipeline/runner.py ai_project_ctl/web/server.py ai_project_ctl/web/read_model.py tests/test_pipeline_phase_review_close.py tests/test_pipeline_runner.py tests/test_web_control_center.py Recovered contextctl.check-generated warnings are not shown as owner-facing warnings when post-close context_refresh succeeds. Recovered protected.check stale context or prompt warnings are not shown as owner-facing warnings when post-close context_refresh succeeds. Technical evidence still records that the non-blocking checks warned during close. Warnings remain owner-facing when post-close context_refresh fails, is missing, or does not repair the stale generated files. Focused close-phase, runner, and Web Control Center tests pass. Check that warning demotion is conditional on successful post-close repair evidence. Confirm that no real blocking warning is hidden.
```

## Task Boundary Snapshot

Task: `TASK-257` - Demote recovered close workflow warnings
Status: `done`

Scope:
- Identify non-blocking close workflow warnings from generated context and protected-file checks that are later repaired by post-close context_refresh.
- Keep recovered warning evidence in technical artifacts or debug details.
- Remove or demote recovered warnings from owner-facing Action Result and pipeline summary warnings.
- Ensure unrelated non-blocking warnings still remain visible to the owner.
- Add regression tests for recovered warnings and unrecovered warnings.

Allowed Files:
- ai_project_ctl/pipeline/close_phase.py
- ai_project_ctl/pipeline/runner.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/read_model.py
- tests/test_pipeline_phase_review_close.py
- tests/test_pipeline_runner.py
- tests/test_web_control_center.py

Acceptance Criteria:
- Recovered contextctl.check-generated warnings are not shown as owner-facing warnings when post-close context_refresh succeeds.
- Recovered protected.check stale context or prompt warnings are not shown as owner-facing warnings when post-close context_refresh succeeds.
- Technical evidence still records that the non-blocking checks warned during close.
- Warnings remain owner-facing when post-close context_refresh fails, is missing, or does not repair the stale generated files.
- Focused close-phase, runner, and Web Control Center tests pass.

## Index Summary

Indexed source documents: `10`
Indexed chunks: `891`
Excluded registered sources: `135`
Selected chunks: `8`

Default exclusion policy: generated, inactive, archived, deprecated, template, and example documents are excluded unless explicitly allowed.

## Selected Sources

| Score | Source | Heading | Lines | Content hash | Chunk hash | Reasons |
| ---: | --- | --- | --- | --- | --- | --- |
| 152 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | heading token match: to; metadata token match: md, to; content token match: acceptance, and, as, before, can, changes, check, checks |
| 140 | `ai-system/project-control/06-prompt-package-spec.md` | 12. Prompt Package Template | 607-707 | `f5e4b5e551ae` | `6c704ec11dd6` | heading token match: prompt; metadata token match: control, md, project-control, prompt; content token match: acceptance, ai_project, and, by, change, checks, completed, context |
| 130 | `ai-system/project-control/06-prompt-package-spec.md` | 14. Context Budget Rules > Context Pack Boundary | 834-870 | `f5e4b5e551ae` | `1ed18819b1db` | heading token match: context; metadata token match: context, control, md, project-control, prompt; content token match: acceptance, add, and, before, by, change, context, contextctl |
| 125 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Self-Hosted Command Boundary | 65-119 | `f824429b0a39` | `5b78d4503548` | heading token match: control; metadata token match: control, md, project-control; content token match: acceptance, ai_project, and, are, as, by, check-generated, context |
| 124 | `ai-system/project-control/03-state-model.md` | Project Control State Model > Context Control State | 104-125 | `9e818e514763` | `0cd80bdf0d55` | heading token match: context, control, state; metadata token match: context, control, md, project-control, state; content token match: acceptance, ai_project, and, are, by, context, contextctl, control |
| 124 | `ai-system/project-control/06-prompt-package-spec.md` | 17. Relationship To taskctl.py And codexctl.py | 911-943 | `f5e4b5e551ae` | `1d3f69b9e6a5` | heading token match: and, py, to; metadata token match: and, control, md, project-control, prompt, py, to; content token match: and, before, by, can, context, contextctl, does, for |
| 121 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | metadata token match: md; content token match: acceptance, add, ai_project, and, as, before, by, change |
| 111 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Scope | 21-64 | `f824429b0a39` | `9c998142f16f` | heading token match: control; metadata token match: control, md, project-control; content token match: add, ai_project_ctl, and, as, center, change, context, contextctl |

## Selected Context

### 1. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Recommended Skills To Create
Lines: `80-92`
Score: `152`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: heading token match: to; metadata token match: md, to; content token match: acceptance, and, as, before, can, changes, check, checks

```text
## Recommended Skills To Create

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Documentation Control Skill | Guide documentation registration, status changes, generated indexes and documentation validation. | `docctl.py` | P0 | Register documents, set draft/review status, render/check generated docs, explain documentation lifecycle. | Mark documents active without Human Owner approval; manually edit `docs.json`, doc events or generated doc indexes. |
| Protected Files Skill | Keep agents inside the protected-files boundary and detect unsafe project-control edits. | `check-protected-project-files.py`, `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Explain protected paths, run protected-files checks, route repairs through CLIs. | Edit protected state/events/generated files manually; use ad hoc scripts to mutate protected files; hide drift. |
| Review Gate Skill | Guide review intake before a Task can be accepted or closed. | `taskctl.py`; future review control CLI if approved | P1 | Check scope, allowed files, acceptance criteria, validation output and review status; recommend APPROVED, REWORK, REJECTED or DEFERRED. | Self-approve work; mark a Task done without the required approval path; ignore Critical or Major findings. |

[...truncated by contextctl...]
```

### 2. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 12. Prompt Package Template
Lines: `607-707`
Score: `140`
Content hash: `f5e4b5e551ae157f409a448b3b0eff79c213d02ca5b7b93fa9817d668776bb3f`
Chunk hash: `6c704ec11dd6768d6ef9c65207d80f3aa00e1bf0da58c3d765defabe8ff08815`
Reasons: heading token match: prompt; metadata token match: control, md, project-control, prompt; content token match: acceptance, ai_project, and, by, change, checks, completed, context

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

### 3. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 14. Context Budget Rules > Context Pack Boundary
Lines: `834-870`
Score: `130`
Content hash: `f5e4b5e551ae157f409a448b3b0eff79c213d02ca5b7b93fa9817d668776bb3f`
Chunk hash: `1ed18819b1db2849347b56648bdbea293730ca187154bd5be940636cfe902e79`
Reasons: heading token match: context; metadata token match: context, control, md, project-control, prompt; content token match: acceptance, add, and, before, by, change, context, contextctl

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

### 4. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Self-Hosted Command Boundary
Lines: `65-119`
Score: `125`
Content hash: `f824429b0a394aec9bfe9157302c1059a181374f040adbfb8136d2673f7fb1b6`
Chunk hash: `5b78d45035483b51a58d0a7bed1cf1402fe3b2e6bc9a7ffcda911c0d12fcb6bc`
Reasons: heading token match: control; metadata token match: control, md, project-control; content token match: acceptance, ai_project, and, are, as, by, check-generated, context

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
Score: `124`
Content hash: `9e818e514763e69aa2f56bb5d9ca080d47b7330db3aa016982c5d3ee0bc2be81`
Chunk hash: `0cd80bdf0d55e5284fa6355477f50005896398136bf33b7e1a181718f309f8b4`
Reasons: heading token match: context, control, state; metadata token match: context, control, md, project-control, state; content token match: acceptance, ai_project, and, are, by, context, contextctl, control

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
Lines: `911-943`
Score: `124`
Content hash: `f5e4b5e551ae157f409a448b3b0eff79c213d02ca5b7b93fa9817d668776bb3f`
Chunk hash: `1d3f69b9e6a541b647d67281fe6878bd0cffde8324082ef979a9a7ca2a729d9a`
Reasons: heading token match: and, py, to; metadata token match: and, control, md, project-control, prompt, py, to; content token match: and, before, by, can, context, contextctl, does, for

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

### 7. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Existing Useful Skills
Lines: `34-43`
Score: `121`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: metadata token match: md; content token match: acceptance, add, ai_project, and, as, before, by, change

```text
## Existing Useful Skills

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Project Control Gateway Skill | Route plan, task, documentation and evolution work through the controlled CLI gateway instead of manual state edits. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Inspect state through CLI, choose allowed commands, run validation and render commands, report unsupported operations. | Manually edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**`; invent lifecycle states or commands; execute Initiative or Epic directly. |
| Clarification Gate Skill | Teach Codex and subagents when to inspect first, proceed with safe assumptions, or stop for Human Owner blocker questions. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Classify blockers, group owner questions, identify safe defaults, preserve task and approval boundaries. | Use questions to avoid normal inspection; ask for approval after every small step; self-approve accepted, approved, active or done states. |
| Documentation Navigation Skill | Route Codex and subagents to the minimal correct documentation and project-control read set before planning, editing, reviewing or executing AI_Development_System work.

[...truncated by contextctl...]
```

### 8. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Scope
Lines: `21-64`
Score: `111`
Content hash: `f824429b0a394aec9bfe9157302c1059a181374f040adbfb8136d2673f7fb1b6`
Chunk hash: `9c998142f16f19b020151b13a6a80db5dfffa618771f91cbdd39a8467a7ee582`
Reasons: heading token match: control; metadata token match: control, md, project-control; content token match: add, ai_project_ctl, and, as, center, change, context, contextctl

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
pipeline    supervised batch pipeline sessions, gates and generated pipeline status
```

`aictl.py` is a facade and command registry. Domain ownership still belongs to the owning scripts and packages such as `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py`, `contextctl.py`, `codexctl.py` and `ai_project_ctl/pipeline/**`.

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

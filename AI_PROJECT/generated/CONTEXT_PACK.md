<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-067 BUG-01 Fix Approve & Done stale execution context handling Fix the Web Control Center / workflow issue where Approve & Done can be blocked by stale Context Pack or Codex prompt state and where closed tasks can leave a stale Codex execution package behind. Implement options B + C from the review: B) Approve & Done must not require Refresh Context when the task is already in review and owner approval notes are provided; stale execution context may be reported as a warning, not a lifecycle blocker. C) after a reviewed task is successfully approved and transitioned to done, clear or invalidate current Codex execution state when it still points to the closed task. AI_PROJECT/generated/CODEX_CURRENT.md Approve & Done closes reviewed tasks without requiring Refresh Context, and stale Codex execution state is cleared after task closure. Adjust task.close_reviewed so stale Context Pack / Codex prompt freshness does not block Human Owner approval and done transition. Keep owner confirmation and non-empty approval notes mandatory for Approve & Done. Keep task lifecycle, task graph, generated task output, evolution, protected-file, and project doctor checks where they are relevant to closure. Preserve visibility of stale context/prompt state as a warning or result detail instead of hiding it. After successful Approve & Done, clear or invalidate current_execution when it targets the task that was just closed. Use an existing governed command such as codexctl.py clear if suitable, or add a small registered/facade workflow step if needed. Update Web Control Center hints so an in_review task can still expose Approve & Done even when execution context is stale. Add or update tests covering stale context in_review close, post-close execution cleanup, required approval notes, invalid status rejection, and no direct protected-file writes. Do not weaken Human Owner approval gates. Do not allow Codex to self-approve tasks. Do not silently accept linked Evolution Changes. Do not hide stale context/prompt warnings from the UI or action result. Do not auto-refresh Context Pack or Codex Prompt as part of approval unless explicitly justified by the implementation. Do not manually edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**. ai_project_ctl/core/workflows.py ai_project_ctl/core/registry.py ai_project_ctl/web/read_model.py ai_project_ctl/web/actions.py scripts/aictl.py scripts/codexctl.py tests/test_workflows.py tests/test_web_control_center.py tests/test_aictl.py tests/test_registry.py ai-system/project-control/08-usage-guide.md if owner-facing workflow documentation needs a small clarification ai-system/project-control/10-owner-quickstart.md if owner-facing workflow documentation needs a small clarification A task in in_review with stale Context Pack or stale Codex prompt can be closed through Approve & Done when explicit owner notes and confirmation are provided. Approve & Done still rejects tasks outside in_review. Approve & Done still requires non-empty owner approval notes. Stale Context Pack / Codex prompt state remains visible as a warning, blocked reason, or action-result detail, but does not force Refresh Context before owner acceptance. After successful Approve & Done, current_execution is cleared or marked non-ready when it points to the closed task. Closing one task does not clear an execution package that points to a different active task. All writes continue to route through governed CLI/workflow paths. Relevant tests pass and project-control validation/check-generated commands pass. Verify that the fix implements options B + C, not option A. Verify that no approval gate was weakened and owner notes remain required. Verify that stale execution context is not hidden, only made non-blocking for closure. Verify that current_execution cleanup is conditional on the closed task identity. Verify that generated files were not edited manually.","schema_version":1,"task_id":"TASK-067"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-067`
Explicit query: `false`
Limit: `8`
Docs revision: `24`
Tasks revision: `577`

## Query

```text
TASK-067 BUG-01 Fix Approve & Done stale execution context handling Fix the Web Control Center / workflow issue where Approve & Done can be blocked by stale Context Pack or Codex prompt state and where closed tasks can leave a stale Codex execution package behind. Implement options B + C from the review: B) Approve & Done must not require Refresh Context when the task is already in review and owner approval notes are provided; stale execution context may be reported as a warning, not a lifecycle blocker. C) after a reviewed task is successfully approved and transitioned to done, clear or invalidate current Codex execution state when it still points to the closed task. AI_PROJECT/generated/CODEX_CURRENT.md Approve & Done closes reviewed tasks without requiring Refresh Context, and stale Codex execution state is cleared after task closure. Adjust task.close_reviewed so stale Context Pack / Codex prompt freshness does not block Human Owner approval and done transition. Keep owner confirmation and non-empty approval notes mandatory for Approve & Done. Keep task lifecycle, task graph, generated task output, evolution, protected-file, and project doctor checks where they are relevant to closure. Preserve visibility of stale context/prompt state as a warning or result detail instead of hiding it. After successful Approve & Done, clear or invalidate current_execution when it targets the task that was just closed. Use an existing governed command such as codexctl.py clear if suitable, or add a small registered/facade workflow step if needed. Update Web Control Center hints so an in_review task can still expose Approve & Done even when execution context is stale. Add or update tests covering stale context in_review close, post-close execution cleanup, required approval notes, invalid status rejection, and no direct protected-file writes. Do not weaken Human Owner approval gates. Do not allow Codex to self-approve tasks. Do not silently accept linked Evolution Changes. Do not hide stale context/prompt warnings from the UI or action result. Do not auto-refresh Context Pack or Codex Prompt as part of approval unless explicitly justified by the implementation. Do not manually edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**. ai_project_ctl/core/workflows.py ai_project_ctl/core/registry.py ai_project_ctl/web/read_model.py ai_project_ctl/web/actions.py scripts/aictl.py scripts/codexctl.py tests/test_workflows.py tests/test_web_control_center.py tests/test_aictl.py tests/test_registry.py ai-system/project-control/08-usage-guide.md if owner-facing workflow documentation needs a small clarification ai-system/project-control/10-owner-quickstart.md if owner-facing workflow documentation needs a small clarification A task in in_review with stale Context Pack or stale Codex prompt can be closed through Approve & Done when explicit owner notes and confirmation are provided. Approve & Done still rejects tasks outside in_review. Approve & Done still requires non-empty owner approval notes. Stale Context Pack / Codex prompt state remains visible as a warning, blocked reason, or action-result detail, but does not force Refresh Context before owner acceptance. After successful Approve & Done, current_execution is cleared or marked non-ready when it points to the closed task. Closing one task does not clear an execution package that points to a different active task. All writes continue to route through governed CLI/workflow paths. Relevant tests pass and project-control validation/check-generated commands pass. Verify that the fix implements options B + C, not option A. Verify that no approval gate was weakened and owner notes remain required. Verify that stale execution context is not hidden, only made non-blocking for closure. Verify that current_execution cleanup is conditional on the closed task identity. Verify that generated files were not edited manually.
```

## Task Boundary Snapshot

Task: `TASK-067` - BUG-01 Fix Approve & Done stale execution context handling
Status: `in_progress`

Scope:
- Adjust task.close_reviewed so stale Context Pack / Codex prompt freshness does not block Human Owner approval and done transition.
- Keep owner confirmation and non-empty approval notes mandatory for Approve & Done.
- Keep task lifecycle, task graph, generated task output, evolution, protected-file, and project doctor checks where they are relevant to closure.
- Preserve visibility of stale context/prompt state as a warning or result detail instead of hiding it.
- After successful Approve & Done, clear or invalidate current_execution when it targets the task that was just closed.
- Use an existing governed command such as codexctl.py clear if suitable, or add a small registered/facade workflow step if needed.
- Update Web Control Center hints so an in_review task can still expose Approve & Done even when execution context is stale.
- Add or update tests covering stale context in_review close, post-close execution cleanup, required approval notes, invalid status rejection, and no direct protected-file writes.

Allowed Files:
- ai_project_ctl/core/workflows.py
- ai_project_ctl/core/registry.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/actions.py
- scripts/aictl.py
- scripts/codexctl.py
- tests/test_workflows.py
- tests/test_web_control_center.py
- tests/test_aictl.py
- tests/test_registry.py
- ai-system/project-control/08-usage-guide.md if owner-facing workflow documentation needs a small clarification
- ai-system/project-control/10-owner-quickstart.md if owner-facing workflow documentation needs a small clarification

Acceptance Criteria:
- A task in in_review with stale Context Pack or stale Codex prompt can be closed through Approve & Done when explicit owner notes and confirmation are provided.
- Approve & Done still rejects tasks outside in_review.
- Approve & Done still requires non-empty owner approval notes.
- Stale Context Pack / Codex prompt state remains visible as a warning, blocked reason, or action-result detail, but does not force Refresh Context before owner acceptance.
- After successful Approve & Done, current_execution is cleared or marked non-ready when it points to the closed task.
- Closing one task does not clear an execution package that points to a different active task.
- All writes continue to route through governed CLI/workflow paths.
- Relevant tests pass and project-control validation/check-generated commands pass.

## Index Summary

Indexed source documents: `10`
Indexed chunks: `890`
Excluded registered sources: `134`
Selected chunks: `8`

Default exclusion policy: generated, inactive, archived, deprecated, template, and example documents are excluded unless explicitly allowed.

## Selected Sources

| Score | Source | Heading | Lines | Content hash | Chunk hash | Reasons |
| ---: | --- | --- | --- | --- | --- | --- |
| 280 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | heading token match: existing; metadata token match: active, ai-system, existing, md; content token match: a, acceptance, actions, active, add, after, ai_project, allow |
| 264 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | heading token match: to; metadata token match: active, ai-system, md, to; content token match: a, accept, acceptance, actions, active, and, approval, approved |
| 236 | `ai-system/project-control/06-prompt-package-spec.md` | 12. Prompt Package Template | 580-670 | `3444e8d40e40` | `4b3949b96350` | heading token match: package, prompt; metadata token match: active, ai-system, control, md, package, project, project-control, prompt; content token match: acceptance, action, active, ai_project, and, be, by, checks |
| 233 | `ai-system/project-control/06-prompt-package-spec.md` | 14. Context Budget Rules > Context Pack Boundary | 797-833 | `3444e8d40e40` | `24706f89c068` | heading token match: context, pack; metadata token match: active, ai-system, context, control, md, pack, package, project; content token match: a, acceptance, add, and, before, but, by, codex |
| 230 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Self-Hosted Command Boundary | 64-118 | `d6bfbf03256d` | `749381be335a` | heading token match: command, control, project; metadata token match: active, ai-system, command, control, md, project, project-control; content token match: a, acceptance, ai-system, ai_project, aictl, all, and, approved |
| 225 | `ai-system/project-control/03-state-model.md` | Project Control State Model > Context Control State | 104-125 | `9e818e514763` | `0cd80bdf0d55` | heading token match: context, control, project, state; metadata token match: active, ai-system, context, control, md, project, project-control, state; content token match: a, acceptance, active, ai_project, and, are, be, by |
| 223 | `ai-system/project-control/06-prompt-package-spec.md` | 17. Relationship To taskctl.py And codexctl.py | 874-906 | `3444e8d40e40` | `6cf68be89257` | heading token match: and, codexctl, py, to; metadata token match: active, ai-system, and, codexctl, control, md, package, project; content token match: a, an, and, be, before, but, by, can |
| 198 | `ai-system/project-control/06-prompt-package-spec.md` | 3. Current Implementation | 123-162 | `3444e8d40e40` | `4fe051d2de08` | heading token match: current, implementation; metadata token match: active, ai-system, control, current, implementation, md, package, project; content token match: a, ai_project, allow, an, and, are, clear, cli |

## Selected Context

### 1. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Existing Useful Skills
Lines: `34-43`
Score: `280`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: heading token match: existing; metadata token match: active, ai-system, existing, md; content token match: a, acceptance, actions, active, add, after, ai_project, allow

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
Score: `264`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: heading token match: to; metadata token match: active, ai-system, md, to; content token match: a, accept, acceptance, actions, active, and, approval, approved

```text
## Recommended Skills To Create

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Documentation Control Skill | Guide documentation registration, status changes, generated indexes and documentation validation. | `docctl.py` | P0 | Register documents, set draft/review status, render/check generated docs, explain documentation lifecycle. | Mark documents active without Human Owner approval; manually edit `docs.json`, doc events or generated doc indexes. |
| Protected Files Skill | Keep agents inside the protected-files boundary and detect unsafe project-control edits. | `check-protected-project-files.py`, `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Explain protected paths, run protected-files checks, route repairs through CLIs. | Edit protected state/events/generated files manually; use ad hoc scripts to mutate protected files; hide drift. |
| Review Gate Skill | Guide review intake before a Task can be accepted or closed. | `taskctl.py`; future review control CLI if approved | P1 | Check scope, allowed files, acceptance criteria, validation output and review status; recommend APPROVED, REWORK, REJECTED or DEFERRED. | Self-approve work; mark a Task done without the required approval path; ignore Critical or Major findings. |

[...truncated by contextctl...]
```

### 3. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 12. Prompt Package Template
Lines: `580-670`
Score: `236`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `4b3949b963506d03a8ca61d2f28eb70f0cc2ca715a4c20495bab284ca4d8fcb0`
Reasons: heading token match: package, prompt; metadata token match: active, ai-system, control, md, package, project, project-control, prompt; content token match: acceptance, action, active, ai_project, and, be, by, checks

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

### 4. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 14. Context Budget Rules > Context Pack Boundary
Lines: `797-833`
Score: `233`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `24706f89c068bb280d5630a712f0d9b260c02079a14823cc0a350875c71ba831`
Reasons: heading token match: context, pack; metadata token match: active, ai-system, context, control, md, pack, package, project; content token match: a, acceptance, add, and, before, but, by, codex

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

### 5. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Self-Hosted Command Boundary
Lines: `64-118`
Score: `230`
Content hash: `d6bfbf03256d4d5a7f005184d36c94434a45640595c0d654fc463065a1428adf`
Chunk hash: `749381be335ac66aa70d957f55a95f190d998afd70c4347643a6c88c059f6587`
Reasons: heading token match: command, control, project; metadata token match: active, ai-system, command, control, md, project, project-control; content token match: a, acceptance, ai-system, ai_project, aictl, all, and, approved

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

### 6. `ai-system/project-control/03-state-model.md`

Title: Project Control State Model
Status: `active`  Type: `reference`
Heading: Project Control State Model > Context Control State
Lines: `104-125`
Score: `225`
Content hash: `9e818e514763e69aa2f56bb5d9ca080d47b7330db3aa016982c5d3ee0bc2be81`
Chunk hash: `0cd80bdf0d55e5284fa6355477f50005896398136bf33b7e1a181718f309f8b4`
Reasons: heading token match: context, control, project, state; metadata token match: active, ai-system, context, control, md, project, project-control, state; content token match: a, acceptance, active, ai_project, and, are, be, by

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

### 7. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 17. Relationship To taskctl.py And codexctl.py
Lines: `874-906`
Score: `223`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `6cf68be892579b77502246852781af90dc2942f367d5af5b0a3c4a4ee727323f`
Reasons: heading token match: and, codexctl, py, to; metadata token match: active, ai-system, and, codexctl, control, md, package, project; content token match: a, an, and, be, before, but, by, can

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

### 8. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 3. Current Implementation
Lines: `123-162`
Score: `198`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `4fe051d2de08383b0737cc69ca48f864bb8341acd7154ddc8b2d3a70fb1ad30a`
Reasons: heading token match: current, implementation; metadata token match: active, ai-system, control, current, implementation, md, package, project; content token match: a, ai_project, allow, an, and, are, clear, cli

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

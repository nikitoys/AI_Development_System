<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-026 Task H - Add project doctor command Provide one health check for project-control state. Add a project doctor command that reports PASS/WARN/FAIL for duplicate IDs, invalid statuses, lifecycle residue, missing parents, stale generated files, stale Codex outputs, event/state assumptions, missing generated views, and detectable direct mutation risk. scripts/aictl.py project doctor Project doctor reports useful PASS/WARN/FAIL health output and exits non-zero on FAIL. Implement python scripts/aictl.py project doctor or equivalent command registry route. Check duplicate IDs, invalid task status, invalid lifecycle transition residue, missing parent epic, stale generated files, stale CODEX_PROMPT.md or CODEX_STATUS.md, event/state assumptions, missing generated views, and unsupported direct mutations where detectable. Return useful human-readable and automation-friendly output. Add tests or smoke checks for PASS, WARN, and FAIL scenarios. Do not repair state automatically unless a supported render command is explicitly invoked. Do not edit protected files manually. Do not add web UI in this task. scripts/aictl.py ai_project_ctl/** tests/** scripts/check-protected-project-files.py AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only python scripts/aictl.py project doctor reports PASS/WARN/FAIL. Doctor exits non-zero on FAIL. Output is useful for both humans and CI. Doctor does not bypass owning CLI validation or render commands. Verify doctor failures are deterministic and actionable. Verify doctor does not mutate semantic state unexpectedly.","schema_version":1,"task_id":"TASK-026"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-026`
Explicit query: `false`
Limit: `8`
Docs revision: `19`
Tasks revision: `238`

## Query

```text
TASK-026 Task H - Add project doctor command Provide one health check for project-control state. Add a project doctor command that reports PASS/WARN/FAIL for duplicate IDs, invalid statuses, lifecycle residue, missing parents, stale generated files, stale Codex outputs, event/state assumptions, missing generated views, and detectable direct mutation risk. scripts/aictl.py project doctor Project doctor reports useful PASS/WARN/FAIL health output and exits non-zero on FAIL. Implement python scripts/aictl.py project doctor or equivalent command registry route. Check duplicate IDs, invalid task status, invalid lifecycle transition residue, missing parent epic, stale generated files, stale CODEX_PROMPT.md or CODEX_STATUS.md, event/state assumptions, missing generated views, and unsupported direct mutations where detectable. Return useful human-readable and automation-friendly output. Add tests or smoke checks for PASS, WARN, and FAIL scenarios. Do not repair state automatically unless a supported render command is explicitly invoked. Do not edit protected files manually. Do not add web UI in this task. scripts/aictl.py ai_project_ctl/** tests/** scripts/check-protected-project-files.py AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only python scripts/aictl.py project doctor reports PASS/WARN/FAIL. Doctor exits non-zero on FAIL. Output is useful for both humans and CI. Doctor does not bypass owning CLI validation or render commands. Verify doctor failures are deterministic and actionable. Verify doctor does not mutate semantic state unexpectedly.
```

## Task Boundary Snapshot

Task: `TASK-026` - Task H - Add project doctor command
Status: `in_progress`

Scope:
- Implement python scripts/aictl.py project doctor or equivalent command registry route.
- Check duplicate IDs, invalid task status, invalid lifecycle transition residue, missing parent epic, stale generated files, stale CODEX_PROMPT.md or CODEX_STATUS.md, event/state assumptions, missing generated views, and unsupported direct mutations where detectable.
- Return useful human-readable and automation-friendly output.
- Add tests or smoke checks for PASS, WARN, and FAIL scenarios.

Allowed Files:
- scripts/aictl.py
- ai_project_ctl/**
- tests/**
- scripts/check-protected-project-files.py
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only

Acceptance Criteria:
- python scripts/aictl.py project doctor reports PASS/WARN/FAIL.
- Doctor exits non-zero on FAIL.
- Output is useful for both humans and CI.
- Doctor does not bypass owning CLI validation or render commands.

## Index Summary

Indexed source documents: `10`
Indexed chunks: `890`
Excluded registered sources: `130`
Selected chunks: `8`

Default exclusion policy: generated, inactive, archived, deprecated, template, and example documents are excluded unless explicitly allowed.

## Selected Sources

| Score | Source | Heading | Lines | Content hash | Chunk hash | Reasons |
| ---: | --- | --- | --- | --- | --- | --- |
| 195 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Self-Hosted Command Boundary | 64-116 | `a1985ca2f321` | `b755c971df05` | heading token match: command, project; metadata token match: command, md, project, project-control; content token match: a, ai_project, and, are, cli, command, commands, does |
| 164 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | heading token match: useful; metadata token match: md, useful; content token match: a, add, ai_project, and, assumptions, automatically, bypass, cli |
| 141 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | metadata token match: md; content token match: a, and, automatically, bypass, check, check-protected-project-files, checks, cli |
| 139 | `ai-system/project-control/03-state-model.md` | Project Control State Model > Context Control State | 104-125 | `b69e6c6ad9ac` | `0cd80bdf0d55` | heading token match: project, state; metadata token match: md, project, project-control, state; content token match: a, ai_project, and, are, both, deterministic, events, explicitly |
| 127 | `ai-system/project-control/06-prompt-package-spec.md` | 12. Prompt Package Template | 580-670 | `9304e03cf1dd` | `4b3949b96350` | metadata token match: md, project, project-control; content token match: ai_project, and, checks, cli, command, commands, do, does |
| 125 | `ai-system/project-control/06-prompt-package-spec.md` | 17. Relationship To taskctl.py And codexctl.py | 874-906 | `9304e03cf1dd` | `6cf68be89257` | heading token match: and, py, taskctl; metadata token match: and, md, project, project-control, py, taskctl; content token match: a, and, bypass, codex, codex_prompt, codex_status, does, events |
| 124 | `ai-system/project-control/07-validation-and-tests.md` | 11. Generated Output Drift Tests > 11.1 Task Generated Drift > Command | 956-978 | `035f37bb15d8` | `35d02739836e` | heading token match: command, generated, output, task, tests; metadata token match: and, command, generated, md, output, project, project-control, task; content token match: ai_project, codex_tasks, command, do, edit, epic, generated, is |
| 121 | `ai-system/project-control/07-validation-and-tests.md` | Project Control Validation and Tests > Scope | 24-66 | `035f37bb15d8` | `c7628c28ceb9` | heading token match: and, project, tests, validation; metadata token match: and, md, project, project-control, tests, validation; content token match: ai_project, and, check, ci, codex, codex_prompt, codex_tasks, events |

## Selected Context

### 1. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Self-Hosted Command Boundary
Lines: `64-116`
Score: `195`
Content hash: `a1985ca2f3219254917601872017052dcfc6ae74f1f636fa6fdbe6a6a3227d32`
Chunk hash: `b755c971df05cf7e6b08835383033a087a162359ce3241ab86018beb96506a9d`
Reasons: heading token match: command, project; metadata token match: command, md, project, project-control; content token match: a, ai_project, and, are, cli, command, commands, does

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
Heading: Skills Layer Roadmap > Existing Useful Skills
Lines: `34-43`
Score: `164`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: heading token match: useful; metadata token match: md, useful; content token match: a, add, ai_project, and, assumptions, automatically, bypass, cli

```text
## Existing Useful Skills

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Project Control Gateway Skill | Route plan, task, documentation and evolution work through the controlled CLI gateway instead of manual state edits. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Inspect state through CLI, choose allowed commands, run validation and render commands, report unsupported operations. | Manually edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**`; invent lifecycle states or commands; execute Initiative or Epic directly. |
| Clarification Gate Skill | Teach Codex and subagents when to inspect first, proceed with safe assumptions, or stop for Human Owner blocker questions. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Classify blockers, group owner questions, identify safe defaults, preserve task and approval boundaries. | Use questions to avoid normal inspection; ask for approval after every small step; self-approve accepted, approved, active or done states. |
| Documentation Navigation Skill | Route Codex and subagents to the minimal correct documentation and project-control read set before planning, editing, reviewing or executing AI_Development_System work.

[...truncated by contextctl...]
```

### 3. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Recommended Skills To Create
Lines: `80-92`
Score: `141`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: metadata token match: md; content token match: a, and, automatically, bypass, check, check-protected-project-files, checks, cli

```text
## Recommended Skills To Create

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Documentation Control Skill | Guide documentation registration, status changes, generated indexes and documentation validation. | `docctl.py` | P0 | Register documents, set draft/review status, render/check generated docs, explain documentation lifecycle. | Mark documents active without Human Owner approval; manually edit `docs.json`, doc events or generated doc indexes. |
| Protected Files Skill | Keep agents inside the protected-files boundary and detect unsafe project-control edits. | `check-protected-project-files.py`, `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Explain protected paths, run protected-files checks, route repairs through CLIs. | Edit protected state/events/generated files manually; use ad hoc scripts to mutate protected files; hide drift. |
| Review Gate Skill | Guide review intake before a Task can be accepted or closed. | `taskctl.py`; future review control CLI if approved | P1 | Check scope, allowed files, acceptance criteria, validation output and review status; recommend APPROVED, REWORK, REJECTED or DEFERRED. | Self-approve work; mark a Task done without the required approval path; ignore Critical or Major findings. |

[...truncated by contextctl...]
```

### 4. `ai-system/project-control/03-state-model.md`

Title: Project Control State Model
Status: `active`  Type: `reference`
Heading: Project Control State Model > Context Control State
Lines: `104-125`
Score: `139`
Content hash: `b69e6c6ad9acbaf0bb398fd6ad729bb07290b6138e99a3535701e57c750a244d`
Chunk hash: `0cd80bdf0d55e5284fa6355477f50005896398136bf33b7e1a181718f309f8b4`
Reasons: heading token match: project, state; metadata token match: md, project, project-control, state; content token match: a, ai_project, and, are, both, deterministic, events, explicitly

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
Score: `127`
Content hash: `9304e03cf1dd12bb320887a0e1e1c90bb87259f60bf4a86d63a904b4e7e87210`
Chunk hash: `4b3949b963506d03a8ca61d2f28eb70f0cc2ca715a4c20495bab284ca4d8fcb0`
Reasons: metadata token match: md, project, project-control; content token match: ai_project, and, checks, cli, command, commands, do, does

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

### 6. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 17. Relationship To taskctl.py And codexctl.py
Lines: `874-906`
Score: `125`
Content hash: `9304e03cf1dd12bb320887a0e1e1c90bb87259f60bf4a86d63a904b4e7e87210`
Chunk hash: `6cf68be892579b77502246852781af90dc2942f367d5af5b0a3c4a4ee727323f`
Reasons: heading token match: and, py, taskctl; metadata token match: and, md, project, project-control, py, taskctl; content token match: a, and, bypass, codex, codex_prompt, codex_status, does, events

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

### 7. `ai-system/project-control/07-validation-and-tests.md`

Title: Project Control Validation and Tests
Status: `active`  Type: `process`
Heading: 11. Generated Output Drift Tests > 11.1 Task Generated Drift > Command
Lines: `956-978`
Score: `124`
Content hash: `035f37bb15d8f601aff97abc4f3378961d0524d7a96fae5f03239239e9aee12c`
Chunk hash: `35d02739836ed294dacefe960802fa75a1d06ea39a4e62c872e951eb07b08975`
Reasons: heading token match: command, generated, output, task, tests; metadata token match: and, command, generated, md, output, project, project-control, task; content token match: ai_project, codex_tasks, command, do, edit, epic, generated, is

```text
### Command

```bash id="ee3uio"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init
python scripts/planctl.py --root "$ROOT" initiative create --title "Project Control"
python scripts/planctl.py --root "$ROOT" epic create --initiative INIT-001 --title "Task Control"

python scripts/taskctl.py --root "$ROOT" init

python scripts/taskctl.py --root "$ROOT" task create \
  --epic EPIC-001 \
  --title "Generated Drift Test" \
  --scope "Do one thing" \
  --allowed-file "README.md" \
  --acceptance "Generated drift is detected"

echo "manual edit" >> "$ROOT/AI_PROJECT/generated/CODEX_TASKS.md"

python scripts/taskctl.py --root "$ROOT" check-generated
```
```

### 8. `ai-system/project-control/07-validation-and-tests.md`

Title: Project Control Validation and Tests
Status: `active`  Type: `process`
Heading: Project Control Validation and Tests > Scope
Lines: `24-66`
Score: `121`
Content hash: `035f37bb15d8f601aff97abc4f3378961d0524d7a96fae5f03239239e9aee12c`
Chunk hash: `c7628c28ceb90b78d021d891a5ed10b1dc2cf8a114509631a433dd7fcc04c70d`
Reasons: heading token match: and, project, tests, validation; metadata token match: and, md, project, project-control, tests, validation; content token match: ai_project, and, check, ci, codex, codex_prompt, codex_tasks, events

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

## Excluded Source Summary

- inactive document excluded by default: `89`
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

<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-022 Task D - Introduce ai_project_ctl core package Create shared internal services that future CLI and Web UI both use. Implement the core control-plane package for store loading/saving, audit events, validation, rendering triggers, result objects, error model, locking, and atomic writes while preserving existing behavior. ai_project_ctl/core Shared core services exist with tests and existing ctl behavior remains compatible. Create ai_project_ctl/core store, events, validation, registry, renderer, ids, locks, result, and error support as needed. Move shared state loading, saving, event append, validation hooks, rendering triggers, and atomic write helpers into reusable services. Add tests for core package behavior. Preserve current planctl.py, taskctl.py, docctl.py, contextctl.py, codexctl.py, and evolutionctl.py behavior. Do not replace all old ctl scripts in this task. Do not add web UI files. Do not change lifecycle rules beyond approved scope. ai_project_ctl/** tests/** scripts/*ctl.py AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only Existing behavior remains compatible. Core package has tests. No domain command should need to write state directly after migration path is established. State mutation still goes through validated CLI/service paths. Verify behavior compatibility for existing ctl commands. Verify tests cover atomic writes, event append, validation errors, and render trigger behavior where implemented.","schema_version":1,"task_id":"TASK-022"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-022`
Explicit query: `false`
Limit: `8`
Docs revision: `19`
Tasks revision: `209`

## Query

```text
TASK-022 Task D - Introduce ai_project_ctl core package Create shared internal services that future CLI and Web UI both use. Implement the core control-plane package for store loading/saving, audit events, validation, rendering triggers, result objects, error model, locking, and atomic writes while preserving existing behavior. ai_project_ctl/core Shared core services exist with tests and existing ctl behavior remains compatible. Create ai_project_ctl/core store, events, validation, registry, renderer, ids, locks, result, and error support as needed. Move shared state loading, saving, event append, validation hooks, rendering triggers, and atomic write helpers into reusable services. Add tests for core package behavior. Preserve current planctl.py, taskctl.py, docctl.py, contextctl.py, codexctl.py, and evolutionctl.py behavior. Do not replace all old ctl scripts in this task. Do not add web UI files. Do not change lifecycle rules beyond approved scope. ai_project_ctl/** tests/** scripts/*ctl.py AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only Existing behavior remains compatible. Core package has tests. No domain command should need to write state directly after migration path is established. State mutation still goes through validated CLI/service paths. Verify behavior compatibility for existing ctl commands. Verify tests cover atomic writes, event append, validation errors, and render trigger behavior where implemented.
```

## Task Boundary Snapshot

Task: `TASK-022` - Task D - Introduce ai_project_ctl core package
Status: `in_progress`

Scope:
- Create ai_project_ctl/core store, events, validation, registry, renderer, ids, locks, result, and error support as needed.
- Move shared state loading, saving, event append, validation hooks, rendering triggers, and atomic write helpers into reusable services.
- Add tests for core package behavior.
- Preserve current planctl.py, taskctl.py, docctl.py, contextctl.py, codexctl.py, and evolutionctl.py behavior.

Allowed Files:
- ai_project_ctl/**
- tests/**
- scripts/*ctl.py
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only

Acceptance Criteria:
- Existing behavior remains compatible.
- Core package has tests.
- No domain command should need to write state directly after migration path is established.
- State mutation still goes through validated CLI/service paths.

## Index Summary

Indexed source documents: `10`
Indexed chunks: `890`
Excluded registered sources: `130`
Selected chunks: `8`

Default exclusion policy: generated, inactive, archived, deprecated, template, and example documents are excluded unless explicitly allowed.

## Selected Sources

| Score | Source | Heading | Lines | Content hash | Chunk hash | Reasons |
| ---: | --- | --- | --- | --- | --- | --- |
| 158 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | heading token match: existing; metadata token match: existing, md; content token match: add, after, ai_project, and, approved, as, behavior, change |
| 154 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Self-Hosted Command Boundary | 64-116 | `a1985ca2f321` | `b755c971df05` | heading token match: command; metadata token match: command, md; content token match: ai_project, all, and, approved, as, audit, cli, command |
| 149 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | heading token match: create, to; metadata token match: create, md, to; content token match: and, approved, as, cli, commands, create, docctl, events |
| 132 | `ai-system/project-control/06-prompt-package-spec.md` | 17. Relationship To taskctl.py And codexctl.py | 874-906 | `9304e03cf1dd` | `6cf68be89257` | heading token match: and, codexctl, py, taskctl, to; metadata token match: and, codexctl, md, package, py, taskctl, to; content token match: and, audit, codexctl, contextctl, current, events, existing, for |
| 118 | `ai-system/project-control/07-validation-and-tests.md` | Project Control Validation and Tests > Scope | 24-66 | `035f37bb15d8` | `c7628c28ceb9` | heading token match: and, scope, tests, validation; metadata token match: and, md, scope, tests, validation; content token match: ai_project, and, audit, codex_tasks, current, events, evolutionctl, for |
| 118 | `ai-system/project-control/07-validation-and-tests.md` | 5. Happy Path Test > 5.3 Commands | 395-442 | `035f37bb15d8` | `1e0a62325f1b` | heading token match: commands, path; metadata token match: and, commands, md, path, tests, validation; content token match: ai_project, as, cli, commands, create, current, d, files |
| 115 | `ai-system/project-control/06-prompt-package-spec.md` | 12. Prompt Package Template | 580-670 | `9304e03cf1dd` | `4b3949b96350` | heading token match: package; metadata token match: md, package; content token match: ai_project, and, change, cli, command, commands, current, do |
| 114 | `ai-system/project-control/07-validation-and-tests.md` | 12. Audit Event Tests > 12.2 Task Mutation Writes Event > Command | 1061-1075 | `035f37bb15d8` | `0c285b1b791b` | heading token match: audit, command, event, mutation, task, tests, writes; metadata token match: and, audit, command, event, md, mutation, task, tests; content token match: add, audit, command, create, d, planctl, py, scope |

## Selected Context

### 1. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Existing Useful Skills
Lines: `34-43`
Score: `158`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: heading token match: existing; metadata token match: existing, md; content token match: add, after, ai_project, and, approved, as, behavior, change

```text
## Existing Useful Skills

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Project Control Gateway Skill | Route plan, task, documentation and evolution work through the controlled CLI gateway instead of manual state edits. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Inspect state through CLI, choose allowed commands, run validation and render commands, report unsupported operations. | Manually edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**`; invent lifecycle states or commands; execute Initiative or Epic directly. |
| Clarification Gate Skill | Teach Codex and subagents when to inspect first, proceed with safe assumptions, or stop for Human Owner blocker questions. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Classify blockers, group owner questions, identify safe defaults, preserve task and approval boundaries. | Use questions to avoid normal inspection; ask for approval after every small step; self-approve accepted, approved, active or done states. |
| Documentation Navigation Skill | Route Codex and subagents to the minimal correct documentation and project-control read set before planning, editing, reviewing or executing AI_Development_System work.

[...truncated by contextctl...]
```

### 2. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Self-Hosted Command Boundary
Lines: `64-116`
Score: `154`
Content hash: `a1985ca2f3219254917601872017052dcfc6ae74f1f636fa6fdbe6a6a3227d32`
Chunk hash: `b755c971df05cf7e6b08835383033a087a162359ce3241ab86018beb96506a9d`
Reasons: heading token match: command; metadata token match: command, md; content token match: ai_project, all, and, approved, as, audit, cli, command

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

### 3. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Recommended Skills To Create
Lines: `80-92`
Score: `149`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: heading token match: create, to; metadata token match: create, md, to; content token match: and, approved, as, cli, commands, create, docctl, events

```text
## Recommended Skills To Create

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Documentation Control Skill | Guide documentation registration, status changes, generated indexes and documentation validation. | `docctl.py` | P0 | Register documents, set draft/review status, render/check generated docs, explain documentation lifecycle. | Mark documents active without Human Owner approval; manually edit `docs.json`, doc events or generated doc indexes. |
| Protected Files Skill | Keep agents inside the protected-files boundary and detect unsafe project-control edits. | `check-protected-project-files.py`, `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Explain protected paths, run protected-files checks, route repairs through CLIs. | Edit protected state/events/generated files manually; use ad hoc scripts to mutate protected files; hide drift. |
| Review Gate Skill | Guide review intake before a Task can be accepted or closed. | `taskctl.py`; future review control CLI if approved | P1 | Check scope, allowed files, acceptance criteria, validation output and review status; recommend APPROVED, REWORK, REJECTED or DEFERRED. | Self-approve work; mark a Task done without the required approval path; ignore Critical or Major findings. |

[...truncated by contextctl...]
```

### 4. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 17. Relationship To taskctl.py And codexctl.py
Lines: `874-906`
Score: `132`
Content hash: `9304e03cf1dd12bb320887a0e1e1c90bb87259f60bf4a86d63a904b4e7e87210`
Chunk hash: `6cf68be892579b77502246852781af90dc2942f367d5af5b0a3c4a4ee727323f`
Reasons: heading token match: and, codexctl, py, taskctl, to; metadata token match: and, codexctl, md, package, py, taskctl, to; content token match: and, audit, codexctl, contextctl, current, events, existing, for

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

### 5. `ai-system/project-control/07-validation-and-tests.md`

Title: Project Control Validation and Tests
Status: `active`  Type: `process`
Heading: Project Control Validation and Tests > Scope
Lines: `24-66`
Score: `118`
Content hash: `035f37bb15d8f601aff97abc4f3378961d0524d7a96fae5f03239239e9aee12c`
Chunk hash: `c7628c28ceb90b78d021d891a5ed10b1dc2cf8a114509631a433dd7fcc04c70d`
Reasons: heading token match: and, scope, tests, validation; metadata token match: and, md, scope, tests, validation; content token match: ai_project, and, audit, codex_tasks, current, events, evolutionctl, for

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

### 6. `ai-system/project-control/07-validation-and-tests.md`

Title: Project Control Validation and Tests
Status: `active`  Type: `process`
Heading: 5. Happy Path Test > 5.3 Commands
Lines: `395-442`
Score: `118`
Content hash: `035f37bb15d8f601aff97abc4f3378961d0524d7a96fae5f03239239e9aee12c`
Chunk hash: `1e0a62325f1be7605fee794f04ca79d11e9ce2814319de415744ba4c9868be25`
Reasons: heading token match: commands, path; metadata token match: and, commands, md, path, tests, validation; content token match: ai_project, as, cli, commands, create, current, d, files

```text
## 5.3 Commands

```bash id="pt0ts2"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init \
  --project-name "AI Development System Smoke Test"

python scripts/planctl.py --root "$ROOT" idea set \
  --text "Create a controlled AI-assisted development system."

python scripts/planctl.py --root "$ROOT" goal set \
  --text "Validate Project Control Gateway."

python scripts/planctl.py --root "$ROOT" strategy set-summary \
  --text "Use CLI commands as the only mutation path."

python scripts/planctl.py --root "$ROOT" initiative create \
  --title "Project Control Gateway" \
  --summary "Validate strict project control through CLI."

python scripts/planctl.py --root "$ROOT" epic create \
  --initiative INIT-001 \
  --title "Task Control CLI" \
  --summary "Validate executable task control."

python scripts/taskctl.py --root "$ROOT" init

python scripts/taskctl.py --root "$ROOT" task create \
  --epic EPIC-001 \
  --title "Smoke Task" \
  --summary "Validate end-to-end task workflow." \
  --scope "Create generated prompt package" \
  --out-of-scope "No application code changes" \
  --allowed-file "AI_PROJECT/generated/CODEX_PROMPT.md" \
  --acceptance "Task validation passes" \
  --acceptance "Generated task files are up to date" \
  --verification-mode standard

python scripts/taskctl.py --root "$ROOT" current set TASK-001

[...truncated by contextctl...]
```

### 7. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 12. Prompt Package Template
Lines: `580-670`
Score: `115`
Content hash: `9304e03cf1dd12bb320887a0e1e1c90bb87259f60bf4a86d63a904b4e7e87210`
Chunk hash: `4b3949b963506d03a8ca61d2f28eb70f0cc2ca715a4c20495bab284ca4d8fcb0`
Reasons: heading token match: package; metadata token match: md, package; content token match: ai_project, and, change, cli, command, commands, current, do

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

### 8. `ai-system/project-control/07-validation-and-tests.md`

Title: Project Control Validation and Tests
Status: `active`  Type: `process`
Heading: 12. Audit Event Tests > 12.2 Task Mutation Writes Event > Command
Lines: `1061-1075`
Score: `114`
Content hash: `035f37bb15d8f601aff97abc4f3378961d0524d7a96fae5f03239239e9aee12c`
Chunk hash: `0c285b1b791b719d4ada4da4b37d99e8244020c750c82c96e81dd45d765ef052`
Reasons: heading token match: audit, command, event, mutation, task, tests, writes; metadata token match: and, audit, command, event, md, mutation, task, tests; content token match: add, audit, command, create, d, planctl, py, scope

```text
### Command

```bash id="gnhyx3"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init
python scripts/planctl.py --root "$ROOT" initiative create --title "Audit Test"
python scripts/planctl.py --root "$ROOT" epic create --initiative INIT-001 --title "Audit Epic"

python scripts/taskctl.py --root "$ROOT" init
python scripts/taskctl.py --root "$ROOT" task create --epic EPIC-001 --title "Audit Task"
python scripts/taskctl.py --root "$ROOT" task add-scope TASK-001 --text "Add scope item"
python scripts/taskctl.py --root "$ROOT" audit --last 20
```
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

<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-023 Task E - Add command registry Make project-control operations discoverable and callable through one registry. Introduce command metadata with names, descriptions, argument schema, read/write metadata, and output format metadata so both CLI and future web UI can discover and describe supported operations. ai_project_ctl/core/registry.py Command registry supports listing and describing project-control commands. Implement command registry metadata for task, epic, change, review, context, codex, project, and command domains where available. Support example names such as task.list, task.show, task.create, task.transition, epic.list, change.create, context.build, codex.prompt.build, project.doctor, command.list, and command.describe. Expose command names, descriptions, args schema, read/write metadata, and output format metadata. Add tests for registry listing and command description behavior. Do not implement web forms in this task. Do not remove existing ctl entrypoints. Do not add unsupported lifecycle commands. ai_project_ctl/core/registry.py ai_project_ctl/domains/** tests/** AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only Commands have names, descriptions, args schema, read/write metadata, and output format metadata. CLI can list and describe commands. Web UI can later use the registry to render actions/forms. Registry does not bypass domain validation. Verify that registry metadata cannot execute unsupported or unvalidated operations. Verify command descriptions match implemented behavior.","schema_version":1,"task_id":"TASK-023"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-023`
Explicit query: `false`
Limit: `8`
Docs revision: `19`
Tasks revision: `220`

## Query

```text
TASK-023 Task E - Add command registry Make project-control operations discoverable and callable through one registry. Introduce command metadata with names, descriptions, argument schema, read/write metadata, and output format metadata so both CLI and future web UI can discover and describe supported operations. ai_project_ctl/core/registry.py Command registry supports listing and describing project-control commands. Implement command registry metadata for task, epic, change, review, context, codex, project, and command domains where available. Support example names such as task.list, task.show, task.create, task.transition, epic.list, change.create, context.build, codex.prompt.build, project.doctor, command.list, and command.describe. Expose command names, descriptions, args schema, read/write metadata, and output format metadata. Add tests for registry listing and command description behavior. Do not implement web forms in this task. Do not remove existing ctl entrypoints. Do not add unsupported lifecycle commands. ai_project_ctl/core/registry.py ai_project_ctl/domains/** tests/** AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only Commands have names, descriptions, args schema, read/write metadata, and output format metadata. CLI can list and describe commands. Web UI can later use the registry to render actions/forms. Registry does not bypass domain validation. Verify that registry metadata cannot execute unsupported or unvalidated operations. Verify command descriptions match implemented behavior.
```

## Task Boundary Snapshot

Task: `TASK-023` - Task E - Add command registry
Status: `in_review`

Scope:
- Implement command registry metadata for task, epic, change, review, context, codex, project, and command domains where available.
- Support example names such as task.list, task.show, task.create, task.transition, epic.list, change.create, context.build, codex.prompt.build, project.doctor, command.list, and command.describe.
- Expose command names, descriptions, args schema, read/write metadata, and output format metadata.
- Add tests for registry listing and command description behavior.

Allowed Files:
- ai_project_ctl/core/registry.py
- ai_project_ctl/domains/**
- tests/**
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only

Acceptance Criteria:
- Commands have names, descriptions, args schema, read/write metadata, and output format metadata.
- CLI can list and describe commands.
- Web UI can later use the registry to render actions/forms.
- Registry does not bypass domain validation.

## Index Summary

Indexed source documents: `10`
Indexed chunks: `890`
Excluded registered sources: `130`
Selected chunks: `8`

Default exclusion policy: generated, inactive, archived, deprecated, template, and example documents are excluded unless explicitly allowed.

## Selected Sources

| Score | Source | Heading | Lines | Content hash | Chunk hash | Reasons |
| ---: | --- | --- | --- | --- | --- | --- |
| 158 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | heading token match: existing; metadata token match: existing, md; content token match: actions, add, ai_project, and, as, behavior, bypass, change |
| 157 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Self-Hosted Command Boundary | 64-116 | `a1985ca2f321` | `b755c971df05` | heading token match: command, project; metadata token match: command, md, project, project-control; content token match: ai_project, and, as, build, cli, command, commands, context |
| 145 | `ai-system/project-control/06-prompt-package-spec.md` | 17. Relationship To taskctl.py And codexctl.py | 874-906 | `9304e03cf1dd` | `6cf68be89257` | heading token match: and, py, taskctl, to; metadata token match: and, md, project, project-control, prompt, py, taskctl, to; content token match: and, build, bypass, can, codex, context, does, events |
| 128 | `ai-system/project-control/06-prompt-package-spec.md` | 12. Prompt Package Template | 580-670 | `9304e03cf1dd` | `4b3949b96350` | heading token match: prompt; metadata token match: md, project, project-control, prompt; content token match: ai_project, and, build, change, cli, command, commands, context |
| 123 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | heading token match: create, to; metadata token match: create, md, to; content token match: actions, and, as, bypass, can, cli, commands, create |
| 110 | `ai-system/project-control/07-validation-and-tests.md` | 10. Prompt Package Tests > 10.1 Build Prompt For Current Task > Command | 831-855 | `035f37bb15d8` | `356babef36e6` | heading token match: build, command, for, prompt, task, tests; metadata token match: and, build, command, for, md, project, project-control, prompt; content token match: ai_project, build, codex, command, create, epic, generated, md |
| 110 | `ai-system/project-control/07-validation-and-tests.md` | 11. Generated Output Drift Tests > 11.1 Task Generated Drift > Command | 956-978 | `035f37bb15d8` | `35d02739836e` | heading token match: command, generated, output, task, tests; metadata token match: and, command, generated, md, output, project, project-control, task; content token match: ai_project, codex_tasks, command, create, do, epic, generated, md |
| 108 | `ai-system/project-control/06-prompt-package-spec.md` | 3. Current Implementation | 123-162 | `9304e03cf1dd` | `4fe051d2de08` | metadata token match: md, project, project-control, prompt; content token match: ai_project, and, behavior, both, build, cli, codex, context |

## Selected Context

### 1. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Existing Useful Skills
Lines: `34-43`
Score: `158`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: heading token match: existing; metadata token match: existing, md; content token match: actions, add, ai_project, and, as, behavior, bypass, change

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
Score: `157`
Content hash: `a1985ca2f3219254917601872017052dcfc6ae74f1f636fa6fdbe6a6a3227d32`
Chunk hash: `b755c971df05cf7e6b08835383033a087a162359ce3241ab86018beb96506a9d`
Reasons: heading token match: command, project; metadata token match: command, md, project, project-control; content token match: ai_project, and, as, build, cli, command, commands, context

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

### 3. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 17. Relationship To taskctl.py And codexctl.py
Lines: `874-906`
Score: `145`
Content hash: `9304e03cf1dd12bb320887a0e1e1c90bb87259f60bf4a86d63a904b4e7e87210`
Chunk hash: `6cf68be892579b77502246852781af90dc2942f367d5af5b0a3c4a4ee727323f`
Reasons: heading token match: and, py, taskctl, to; metadata token match: and, md, project, project-control, prompt, py, taskctl, to; content token match: and, build, bypass, can, codex, context, does, events

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

### 4. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 12. Prompt Package Template
Lines: `580-670`
Score: `128`
Content hash: `9304e03cf1dd12bb320887a0e1e1c90bb87259f60bf4a86d63a904b4e7e87210`
Chunk hash: `4b3949b963506d03a8ca61d2f28eb70f0cc2ca715a4c20495bab284ca4d8fcb0`
Reasons: heading token match: prompt; metadata token match: md, project, project-control, prompt; content token match: ai_project, and, build, change, cli, command, commands, context

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

### 5. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Recommended Skills To Create
Lines: `80-92`
Score: `123`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: heading token match: create, to; metadata token match: create, md, to; content token match: actions, and, as, bypass, can, cli, commands, create

```text
## Recommended Skills To Create

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Documentation Control Skill | Guide documentation registration, status changes, generated indexes and documentation validation. | `docctl.py` | P0 | Register documents, set draft/review status, render/check generated docs, explain documentation lifecycle. | Mark documents active without Human Owner approval; manually edit `docs.json`, doc events or generated doc indexes. |
| Protected Files Skill | Keep agents inside the protected-files boundary and detect unsafe project-control edits. | `check-protected-project-files.py`, `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Explain protected paths, run protected-files checks, route repairs through CLIs. | Edit protected state/events/generated files manually; use ad hoc scripts to mutate protected files; hide drift. |
| Review Gate Skill | Guide review intake before a Task can be accepted or closed. | `taskctl.py`; future review control CLI if approved | P1 | Check scope, allowed files, acceptance criteria, validation output and review status; recommend APPROVED, REWORK, REJECTED or DEFERRED. | Self-approve work; mark a Task done without the required approval path; ignore Critical or Major findings. |

[...truncated by contextctl...]
```

### 6. `ai-system/project-control/07-validation-and-tests.md`

Title: Project Control Validation and Tests
Status: `active`  Type: `process`
Heading: 10. Prompt Package Tests > 10.1 Build Prompt For Current Task > Command
Lines: `831-855`
Score: `110`
Content hash: `035f37bb15d8f601aff97abc4f3378961d0524d7a96fae5f03239239e9aee12c`
Chunk hash: `356babef36e651767ac10acc79e2963806b6320220a79f2c26267f44ee69beb6`
Reasons: heading token match: build, command, for, prompt, task, tests; metadata token match: and, build, command, for, md, project, project-control, prompt; content token match: ai_project, build, codex, command, create, epic, generated, md

```text
### Command

```bash id="5tarvp"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init
python scripts/planctl.py --root "$ROOT" initiative create --title "Project Control"
python scripts/planctl.py --root "$ROOT" epic create --initiative INIT-001 --title "Prompt Control"

python scripts/taskctl.py --root "$ROOT" init

python scripts/taskctl.py --root "$ROOT" task create \
  --epic EPIC-001 \
  --title "Prompt Build Test" \
  --summary "Build a Codex prompt package." \
  --scope "Generate prompt" \
  --out-of-scope "No code execution" \
  --allowed-file "AI_PROJECT/generated/CODEX_PROMPT.md" \
  --acceptance "Prompt file is written" \
  --verification-mode standard

python scripts/taskctl.py --root "$ROOT" current set TASK-001
python scripts/taskctl.py --root "$ROOT" prompt build --write
```
```

### 7. `ai-system/project-control/07-validation-and-tests.md`

Title: Project Control Validation and Tests
Status: `active`  Type: `process`
Heading: 11. Generated Output Drift Tests > 11.1 Task Generated Drift > Command
Lines: `956-978`
Score: `110`
Content hash: `035f37bb15d8f601aff97abc4f3378961d0524d7a96fae5f03239239e9aee12c`
Chunk hash: `35d02739836ed294dacefe960802fa75a1d06ea39a4e62c872e951eb07b08975`
Reasons: heading token match: command, generated, output, task, tests; metadata token match: and, command, generated, md, output, project, project-control, task; content token match: ai_project, codex_tasks, command, create, do, epic, generated, md

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

### 8. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 3. Current Implementation
Lines: `123-162`
Score: `108`
Content hash: `9304e03cf1dd12bb320887a0e1e1c90bb87259f60bf4a86d63a904b4e7e87210`
Chunk hash: `4fe051d2de08383b0737cc69ca48f864bb8341acd7154ddc8b2d3a70fb1ad30a`
Reasons: metadata token match: md, project, project-control, prompt; content token match: ai_project, and, behavior, both, build, cli, codex, context

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

<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-025 Task G - Convert old ctl scripts into compatibility wrappers Keep existing ctl workflows working while centralizing logic. Update taskctl.py, evolutionctl.py, planctl.py, docctl.py, contextctl.py, and codexctl.py where practical so they delegate to ai_project_ctl domain services or aictl-compatible services without breaking existing command syntax. scripts/*ctl.py Legacy ctl scripts remain supported while shared services own behavior. Make taskctl.py delegate to ai_project_ctl domains or shared services where practical. Make evolutionctl.py and other ctl scripts delegate where practical. Keep old command syntax compatible unless a separate approved migration says otherwise. Mark wrappers as legacy-compatible but supported in documentation or code comments where appropriate. Reduce duplicate lifecycle validation where avoidable. Do not remove existing ctl scripts. Do not change public command syntax unless explicitly approved. Do not implement web UI in this task. scripts/planctl.py scripts/taskctl.py scripts/docctl.py scripts/evolutionctl.py scripts/contextctl.py scripts/codexctl.py ai_project_ctl/** tests/** AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only Existing commands still work. New code path is centralized. No duplicate lifecycle validation remains where avoidable. Wrapper compatibility is documented or obvious from implementation. Run representative compatibility checks for old ctl commands. Verify protected state mutation still goes only through approved service paths.","schema_version":1,"task_id":"TASK-025"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-025`
Explicit query: `false`
Limit: `8`
Docs revision: `19`
Tasks revision: `232`

## Query

```text
TASK-025 Task G - Convert old ctl scripts into compatibility wrappers Keep existing ctl workflows working while centralizing logic. Update taskctl.py, evolutionctl.py, planctl.py, docctl.py, contextctl.py, and codexctl.py where practical so they delegate to ai_project_ctl domain services or aictl-compatible services without breaking existing command syntax. scripts/*ctl.py Legacy ctl scripts remain supported while shared services own behavior. Make taskctl.py delegate to ai_project_ctl domains or shared services where practical. Make evolutionctl.py and other ctl scripts delegate where practical. Keep old command syntax compatible unless a separate approved migration says otherwise. Mark wrappers as legacy-compatible but supported in documentation or code comments where appropriate. Reduce duplicate lifecycle validation where avoidable. Do not remove existing ctl scripts. Do not change public command syntax unless explicitly approved. Do not implement web UI in this task. scripts/planctl.py scripts/taskctl.py scripts/docctl.py scripts/evolutionctl.py scripts/contextctl.py scripts/codexctl.py ai_project_ctl/** tests/** AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only Existing commands still work. New code path is centralized. No duplicate lifecycle validation remains where avoidable. Wrapper compatibility is documented or obvious from implementation. Run representative compatibility checks for old ctl commands. Verify protected state mutation still goes only through approved service paths.
```

## Task Boundary Snapshot

Task: `TASK-025` - Task G - Convert old ctl scripts into compatibility wrappers
Status: `in_review`

Scope:
- Make taskctl.py delegate to ai_project_ctl domains or shared services where practical.
- Make evolutionctl.py and other ctl scripts delegate where practical.
- Keep old command syntax compatible unless a separate approved migration says otherwise.
- Mark wrappers as legacy-compatible but supported in documentation or code comments where appropriate.
- Reduce duplicate lifecycle validation where avoidable.

Allowed Files:
- scripts/planctl.py
- scripts/taskctl.py
- scripts/docctl.py
- scripts/evolutionctl.py
- scripts/contextctl.py
- scripts/codexctl.py
- ai_project_ctl/**
- tests/**
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only

Acceptance Criteria:
- Existing commands still work.
- New code path is centralized.
- No duplicate lifecycle validation remains where avoidable.
- Wrapper compatibility is documented or obvious from implementation.

## Index Summary

Indexed source documents: `10`
Indexed chunks: `890`
Excluded registered sources: `130`
Selected chunks: `8`

Default exclusion policy: generated, inactive, archived, deprecated, template, and example documents are excluded unless explicitly allowed.

## Selected Sources

| Score | Source | Heading | Lines | Content hash | Chunk hash | Reasons |
| ---: | --- | --- | --- | --- | --- | --- |
| 188 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Self-Hosted Command Boundary | 64-116 | `a1985ca2f321` | `b755c971df05` | heading token match: command; metadata token match: command, md; content token match: a, ai_project, and, approved, as, but, command, commands |
| 160 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | heading token match: to; metadata token match: md, to; content token match: a, and, approved, as, checks, commands, docctl, documentation |
| 158 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | heading token match: existing; metadata token match: existing, md; content token match: a, ai_project, and, approved, as, behavior, change, codexctl |
| 126 | `ai-system/project-control/07-validation-and-tests.md` | 5. Happy Path Test > 5.3 Commands | 395-442 | `035f37bb15d8` | `1e0a62325f1b` | heading token match: commands, path; metadata token match: and, commands, md, path, tests, validation; content token match: a, ai_project, as, code, commands, generated, md, mutation |
| 117 | `ai-system/project-control/06-prompt-package-spec.md` | 17. Relationship To taskctl.py And codexctl.py | 874-906 | `9304e03cf1dd` | `6cf68be89257` | heading token match: and, codexctl, py, taskctl, to; metadata token match: and, codexctl, md, py, taskctl, to; content token match: a, and, but, codexctl, contextctl, events, existing, for |
| 113 | `ai-system/project-control/07-validation-and-tests.md` | 9. Current Task Tests > 9.3 Current Task Auto-Clear > Command | 785-810 | `035f37bb15d8` | `7314519e82ba` | heading token match: command, task, tests; metadata token match: and, command, md, task, tests, validation; content token match: approved, command, do, md, planctl, py, scripts, task |
| 104 | `ai-system/project-control/06-prompt-package-spec.md` | 3. Current Implementation | 123-162 | `9304e03cf1dd` | `4fe051d2de08` | heading token match: implementation; metadata token match: implementation, md; content token match: a, ai_project, and, behavior, codexctl, contextctl, for, generated |
| 103 | `ai-system/project-control/05-lifecycle-rules.md` | 12. Recommended Next Steps > 12.1 Add evolutionctl.py | 1180-1205 | `7ac00bfde39d` | `24bacd517890` | heading token match: evolutionctl, py; metadata token match: evolutionctl, lifecycle, md, py; content token match: ai_project, change, commands, events, evolutionctl, generated, implement, json |

## Selected Context

### 1. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Self-Hosted Command Boundary
Lines: `64-116`
Score: `188`
Content hash: `a1985ca2f3219254917601872017052dcfc6ae74f1f636fa6fdbe6a6a3227d32`
Chunk hash: `b755c971df05cf7e6b08835383033a087a162359ce3241ab86018beb96506a9d`
Reasons: heading token match: command; metadata token match: command, md; content token match: a, ai_project, and, approved, as, but, command, commands

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
Score: `160`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: heading token match: to; metadata token match: md, to; content token match: a, and, approved, as, checks, commands, docctl, documentation

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
Score: `158`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: heading token match: existing; metadata token match: existing, md; content token match: a, ai_project, and, approved, as, behavior, change, codexctl

```text
## Existing Useful Skills

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Project Control Gateway Skill | Route plan, task, documentation and evolution work through the controlled CLI gateway instead of manual state edits. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Inspect state through CLI, choose allowed commands, run validation and render commands, report unsupported operations. | Manually edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**`; invent lifecycle states or commands; execute Initiative or Epic directly. |
| Clarification Gate Skill | Teach Codex and subagents when to inspect first, proceed with safe assumptions, or stop for Human Owner blocker questions. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Classify blockers, group owner questions, identify safe defaults, preserve task and approval boundaries. | Use questions to avoid normal inspection; ask for approval after every small step; self-approve accepted, approved, active or done states. |
| Documentation Navigation Skill | Route Codex and subagents to the minimal correct documentation and project-control read set before planning, editing, reviewing or executing AI_Development_System work.

[...truncated by contextctl...]
```

### 4. `ai-system/project-control/07-validation-and-tests.md`

Title: Project Control Validation and Tests
Status: `active`  Type: `process`
Heading: 5. Happy Path Test > 5.3 Commands
Lines: `395-442`
Score: `126`
Content hash: `035f37bb15d8f601aff97abc4f3378961d0524d7a96fae5f03239239e9aee12c`
Chunk hash: `1e0a62325f1be7605fee794f04ca79d11e9ce2814319de415744ba4c9868be25`
Reasons: heading token match: commands, path; metadata token match: and, commands, md, path, tests, validation; content token match: a, ai_project, as, code, commands, generated, md, mutation

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

### 5. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 17. Relationship To taskctl.py And codexctl.py
Lines: `874-906`
Score: `117`
Content hash: `9304e03cf1dd12bb320887a0e1e1c90bb87259f60bf4a86d63a904b4e7e87210`
Chunk hash: `6cf68be892579b77502246852781af90dc2942f367d5af5b0a3c4a4ee727323f`
Reasons: heading token match: and, codexctl, py, taskctl, to; metadata token match: and, codexctl, md, py, taskctl, to; content token match: a, and, but, codexctl, contextctl, events, existing, for

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

### 6. `ai-system/project-control/07-validation-and-tests.md`

Title: Project Control Validation and Tests
Status: `active`  Type: `process`
Heading: 9. Current Task Tests > 9.3 Current Task Auto-Clear > Command
Lines: `785-810`
Score: `113`
Content hash: `035f37bb15d8f601aff97abc4f3378961d0524d7a96fae5f03239239e9aee12c`
Chunk hash: `7314519e82bacd85027c4b8b8a47af20e31bd880fed9843cce6b388048aff17d`
Reasons: heading token match: command, task, tests; metadata token match: and, command, md, task, tests, validation; content token match: approved, command, do, md, planctl, py, scripts, task

```text
### Command

```bash id="dzvvho"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init
python scripts/planctl.py --root "$ROOT" initiative create --title "Project Control"
python scripts/planctl.py --root "$ROOT" epic create --initiative INIT-001 --title "Task Control"

python scripts/taskctl.py --root "$ROOT" init

python scripts/taskctl.py --root "$ROOT" task create \
  --epic EPIC-001 \
  --title "Auto Clear Test" \
  --status ready \
  --scope "Do one thing" \
  --allowed-file "README.md" \
  --acceptance "Validation passes"

python scripts/taskctl.py --root "$ROOT" current set TASK-001
python scripts/taskctl.py --root "$ROOT" task transition TASK-001 --to in_progress
python scripts/taskctl.py --root "$ROOT" task transition TASK-001 --to in_review
python scripts/taskctl.py --root "$ROOT" task approve TASK-001 --notes "Approved"
python scripts/taskctl.py --root "$ROOT" current show
```
```

### 7. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 3. Current Implementation
Lines: `123-162`
Score: `104`
Content hash: `9304e03cf1dd12bb320887a0e1e1c90bb87259f60bf4a86d63a904b4e7e87210`
Chunk hash: `4fe051d2de08383b0737cc69ca48f864bb8341acd7154ddc8b2d3a70fb1ad30a`
Reasons: heading token match: implementation; metadata token match: implementation, md; content token match: a, ai_project, and, behavior, codexctl, contextctl, for, generated

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

### 8. `ai-system/project-control/05-lifecycle-rules.md`

Title: Project Control Lifecycle Rules
Status: `active`  Type: `lifecycle`
Heading: 12. Recommended Next Steps > 12.1 Add evolutionctl.py
Lines: `1180-1205`
Score: `103`
Content hash: `7ac00bfde39da4bc9527f11ad1dc984b993d860fd4bb664498242a32a8b986e3`
Chunk hash: `24bacd517890b7e9b05a6b060a4f0c901340b7db5aa3bf3ea1de0706254a0213`
Reasons: heading token match: evolutionctl, py; metadata token match: evolutionctl, lifecycle, md, py; content token match: ai_project, change, commands, events, evolutionctl, generated, implement, json

```text
## 12.1 Add evolutionctl.py

Implement:

```text
AI_PROJECT/state/evolution.json
AI_PROJECT/events/evolution-events.jsonl
AI_PROJECT/generated/EVOLUTION.md
```

First commands:

```bash
python scripts/evolutionctl.py init
python scripts/evolutionctl.py change create --title "..."
python scripts/evolutionctl.py change show CHG-001
python scripts/evolutionctl.py change list
python scripts/evolutionctl.py change transition CHG-001 --to ready
python scripts/evolutionctl.py change approve CHG-001
python scripts/evolutionctl.py change link-task CHG-001 --task TASK-001
python scripts/evolutionctl.py change accept CHG-001
python scripts/evolutionctl.py validate
python scripts/evolutionctl.py render
python scripts/evolutionctl.py audit
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

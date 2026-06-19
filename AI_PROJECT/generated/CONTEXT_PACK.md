<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-040 UIX-03 Add unified workflow action result panel Add a reusable result panel for workflow and Web actions showing step status, changed files, warnings, errors, and next actions. Improve owner feedback after UI actions by showing what was executed, what changed, what failed, and what to do next. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add a reusable action result view/component. Show workflow name and target task/change/epic. Show step-by-step PASS/WARN/FAIL status. Show changed files when available. Show generated files when available. Show warnings and errors clearly. Show next-action hints such as the Codex prompt instruction. Support copyable text for the Codex instruction. Do not change workflow semantics. Do not add new workflow actions in this task. Do not auto-run Codex. Do not weaken confirmation requirements. Do not directly edit protected project-control files. ai_project_ctl/web/server.py ai_project_ctl/web/read_model.py ai_project_ctl/web/actions.py ai_project_ctl/core/workflows.py if result metadata needs compatible updates tests/test_web_control_center.py tests/test_workflows.py After a workflow action, UI shows a clear action result panel. Result panel shows executed steps and status. Result panel shows warnings/errors without hiding failures. Result panel includes next action hints when available. Prepare for Codex result includes a copyable Codex instruction. Existing workflow safety is preserved. Tests and project-control validations pass. Verify that failed steps are visible and not hidden behind a generic success message. Verify that result panel does not expose arbitrary command execution.","schema_version":1,"task_id":"TASK-040"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-040`
Explicit query: `false`
Limit: `8`
Docs revision: `23`
Tasks revision: `379`

## Query

```text
TASK-040 UIX-03 Add unified workflow action result panel Add a reusable result panel for workflow and Web actions showing step status, changed files, warnings, errors, and next actions. Improve owner feedback after UI actions by showing what was executed, what changed, what failed, and what to do next. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add a reusable action result view/component. Show workflow name and target task/change/epic. Show step-by-step PASS/WARN/FAIL status. Show changed files when available. Show generated files when available. Show warnings and errors clearly. Show next-action hints such as the Codex prompt instruction. Support copyable text for the Codex instruction. Do not change workflow semantics. Do not add new workflow actions in this task. Do not auto-run Codex. Do not weaken confirmation requirements. Do not directly edit protected project-control files. ai_project_ctl/web/server.py ai_project_ctl/web/read_model.py ai_project_ctl/web/actions.py ai_project_ctl/core/workflows.py if result metadata needs compatible updates tests/test_web_control_center.py tests/test_workflows.py After a workflow action, UI shows a clear action result panel. Result panel shows executed steps and status. Result panel shows warnings/errors without hiding failures. Result panel includes next action hints when available. Prepare for Codex result includes a copyable Codex instruction. Existing workflow safety is preserved. Tests and project-control validations pass. Verify that failed steps are visible and not hidden behind a generic success message. Verify that result panel does not expose arbitrary command execution.
```

## Task Boundary Snapshot

Task: `TASK-040` - UIX-03 Add unified workflow action result panel
Status: `in_review`

Scope:
- Add a reusable action result view/component.
- Show workflow name and target task/change/epic.
- Show step-by-step PASS/WARN/FAIL status.
- Show changed files when available.
- Show generated files when available.
- Show warnings and errors clearly.
- Show next-action hints such as the Codex prompt instruction.
- Support copyable text for the Codex instruction.

Allowed Files:
- ai_project_ctl/web/server.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/workflows.py if result metadata needs compatible updates
- tests/test_web_control_center.py
- tests/test_workflows.py

Acceptance Criteria:
- After a workflow action, UI shows a clear action result panel.
- Result panel shows executed steps and status.
- Result panel shows warnings/errors without hiding failures.
- Result panel includes next action hints when available.
- Prepare for Codex result includes a copyable Codex instruction.
- Existing workflow safety is preserved.
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
| 128 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | heading token match: existing; metadata token match: existing, md; content token match: a, acceptance, actions, add, after, ai_project, and, as |
| 119 | `ai-system/project-control/06-prompt-package-spec.md` | 12. Prompt Package Template | 580-670 | `3444e8d40e40` | `4b3949b96350` | heading token match: prompt; metadata token match: md, project-control, prompt; content token match: acceptance, action, ai_project, and, by, change, changed, command |
| 114 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | heading token match: to; metadata token match: md, to; content token match: a, acceptance, actions, and, as, criteria, edit, executed |
| 111 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Self-Hosted Command Boundary | 64-118 | `d6bfbf03256d` | `749381be335a` | heading token match: command; metadata token match: command, md, project-control; content token match: a, acceptance, ai_project, and, are, as, by, changed |
| 111 | `ai-system/project-control/06-prompt-package-spec.md` | 17. Relationship To taskctl.py And codexctl.py | 874-906 | `3444e8d40e40` | `6cf68be89257` | heading token match: and, py, to; metadata token match: and, md, project-control, prompt, py, to; content token match: a, and, by, clear, codex, does, execution, existing |
| 105 | `ai-system/project-control/06-prompt-package-spec.md` | 14. Context Budget Rules > Context Pack Boundary | 797-833 | `3444e8d40e40` | `24706f89c068` | metadata token match: md, project-control, prompt; content token match: a, acceptance, add, and, by, change, clearly, codex |
| 95 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Scope | 21-63 | `d6bfbf03256d` | `d914c61786e4` | heading token match: command; metadata token match: command, md, project-control; content token match: a, actions, add, and, as, change, codex, command |
| 83 | `ai-system/project-control/07-validation-and-tests.md` | 10. Prompt Package Tests > 10.1 Build Prompt For Current Task > Command | 831-855 | `61710bd7deee` | `356babef36e6` | heading token match: command, for, prompt, task, tests; metadata token match: and, command, for, md, project-control, prompt, task, tests; content token match: a, acceptance, ai_project, codex, command, epic, execution, generated |

## Selected Context

### 1. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Existing Useful Skills
Lines: `34-43`
Score: `128`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: heading token match: existing; metadata token match: existing, md; content token match: a, acceptance, actions, add, after, ai_project, and, as

```text
## Existing Useful Skills

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Project Control Gateway Skill | Route plan, task, documentation and evolution work through the controlled CLI gateway instead of manual state edits. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Inspect state through CLI, choose allowed commands, run validation and render commands, report unsupported operations. | Manually edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**`; invent lifecycle states or commands; execute Initiative or Epic directly. |
| Clarification Gate Skill | Teach Codex and subagents when to inspect first, proceed with safe assumptions, or stop for Human Owner blocker questions. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Classify blockers, group owner questions, identify safe defaults, preserve task and approval boundaries. | Use questions to avoid normal inspection; ask for approval after every small step; self-approve accepted, approved, active or done states. |
| Documentation Navigation Skill | Route Codex and subagents to the minimal correct documentation and project-control read set before planning, editing, reviewing or executing AI_Development_System work.

[...truncated by contextctl...]
```

### 2. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 12. Prompt Package Template
Lines: `580-670`
Score: `119`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `4b3949b963506d03a8ca61d2f28eb70f0cc2ca715a4c20495bab284ca4d8fcb0`
Reasons: heading token match: prompt; metadata token match: md, project-control, prompt; content token match: acceptance, action, ai_project, and, by, change, changed, command

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

### 3. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Recommended Skills To Create
Lines: `80-92`
Score: `114`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: heading token match: to; metadata token match: md, to; content token match: a, acceptance, actions, and, as, criteria, edit, executed

```text
## Recommended Skills To Create

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Documentation Control Skill | Guide documentation registration, status changes, generated indexes and documentation validation. | `docctl.py` | P0 | Register documents, set draft/review status, render/check generated docs, explain documentation lifecycle. | Mark documents active without Human Owner approval; manually edit `docs.json`, doc events or generated doc indexes. |
| Protected Files Skill | Keep agents inside the protected-files boundary and detect unsafe project-control edits. | `check-protected-project-files.py`, `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Explain protected paths, run protected-files checks, route repairs through CLIs. | Edit protected state/events/generated files manually; use ad hoc scripts to mutate protected files; hide drift. |
| Review Gate Skill | Guide review intake before a Task can be accepted or closed. | `taskctl.py`; future review control CLI if approved | P1 | Check scope, allowed files, acceptance criteria, validation output and review status; recommend APPROVED, REWORK, REJECTED or DEFERRED. | Self-approve work; mark a Task done without the required approval path; ignore Critical or Major findings. |

[...truncated by contextctl...]
```

### 4. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Self-Hosted Command Boundary
Lines: `64-118`
Score: `111`
Content hash: `d6bfbf03256d4d5a7f005184d36c94434a45640595c0d654fc463065a1428adf`
Chunk hash: `749381be335ac66aa70d957f55a95f190d998afd70c4347643a6c88c059f6587`
Reasons: heading token match: command; metadata token match: command, md, project-control; content token match: a, acceptance, ai_project, and, are, as, by, changed

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

### 5. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 17. Relationship To taskctl.py And codexctl.py
Lines: `874-906`
Score: `111`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `6cf68be892579b77502246852781af90dc2942f367d5af5b0a3c4a4ee727323f`
Reasons: heading token match: and, py, to; metadata token match: and, md, project-control, prompt, py, to; content token match: a, and, by, clear, codex, does, execution, existing

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

### 6. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 14. Context Budget Rules > Context Pack Boundary
Lines: `797-833`
Score: `105`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `24706f89c068bb280d5630a712f0d9b260c02079a14823cc0a350875c71ba831`
Reasons: metadata token match: md, project-control, prompt; content token match: a, acceptance, add, and, by, change, clearly, codex

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

### 7. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Scope
Lines: `21-63`
Score: `95`
Content hash: `d6bfbf03256d4d5a7f005184d36c94434a45640595c0d654fc463065a1428adf`
Chunk hash: `d914c61786e4b852b59e3a000d5c0b85638a7e8731366116abd8c8b8e9591815`
Reasons: heading token match: command; metadata token match: command, md, project-control; content token match: a, actions, add, and, as, change, codex, command

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

### 8. `ai-system/project-control/07-validation-and-tests.md`

Title: Project Control Validation and Tests
Status: `active`  Type: `process`
Heading: 10. Prompt Package Tests > 10.1 Build Prompt For Current Task > Command
Lines: `831-855`
Score: `83`
Content hash: `61710bd7deeed5b710aa500acaf478c77f7ad43ffcd3943c0245da65015ff2c9`
Chunk hash: `356babef36e651767ac10acc79e2963806b6320220a79f2c26267f44ee69beb6`
Reasons: heading token match: command, for, prompt, task, tests; metadata token match: and, command, for, md, project-control, prompt, task, tests; content token match: a, acceptance, ai_project, codex, command, epic, execution, generated

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

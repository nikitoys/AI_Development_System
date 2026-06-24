<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-149 PIPE-065 Apply internal Change gate bypass to UI runs Allow confirmed UI runs to skip approved Change requirements only for internal project-control tasks when the bypass setting is enabled. This implements the actual execution behavior behind the Settings checkbox with strict safety boundaries and audit evidence. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Define an internal project-control task predicate for safe bypass eligibility. Apply the bypass only to UI-created single-task sessions when the setting is enabled. Record explicit phase artifacts or audit details when the Change gate is bypassed. Keep approved Change requirements unchanged for non-internal tasks and non-UI execution paths. Do not disable the Change gate globally. Do not bypass token, report, verify, review, close or commit gates. Do not auto-approve or auto-create Evolution Changes. ai_project_ctl/pipeline/prepare_phase.py ai_project_ctl/pipeline/runner.py ai_project_ctl/pipeline/ui_policy.py scripts/aictl.py tests/pipeline/test_prepare_phase.py tests/test_ui_run_command.py When the setting is disabled, UI runs still require an approved linked Change. When the setting is enabled, eligible internal project-control tasks can pass prepare without an approved linked Change. Non-internal tasks still block on missing approved Change even when the setting is enabled. Bypass usage is recorded in phase artifacts or audit details. Tests cover enabled, disabled and non-internal task behavior. Review the internal-task predicate carefully to avoid allowing product-code tasks through the bypass.","schema_version":1,"task_id":"TASK-149"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-149`
Explicit query: `false`
Limit: `8`
Docs revision: `28`
Tasks revision: `1062`

## Query

```text
TASK-149 PIPE-065 Apply internal Change gate bypass to UI runs Allow confirmed UI runs to skip approved Change requirements only for internal project-control tasks when the bypass setting is enabled. This implements the actual execution behavior behind the Settings checkbox with strict safety boundaries and audit evidence. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Define an internal project-control task predicate for safe bypass eligibility. Apply the bypass only to UI-created single-task sessions when the setting is enabled. Record explicit phase artifacts or audit details when the Change gate is bypassed. Keep approved Change requirements unchanged for non-internal tasks and non-UI execution paths. Do not disable the Change gate globally. Do not bypass token, report, verify, review, close or commit gates. Do not auto-approve or auto-create Evolution Changes. ai_project_ctl/pipeline/prepare_phase.py ai_project_ctl/pipeline/runner.py ai_project_ctl/pipeline/ui_policy.py scripts/aictl.py tests/pipeline/test_prepare_phase.py tests/test_ui_run_command.py When the setting is disabled, UI runs still require an approved linked Change. When the setting is enabled, eligible internal project-control tasks can pass prepare without an approved linked Change. Non-internal tasks still block on missing approved Change even when the setting is enabled. Bypass usage is recorded in phase artifacts or audit details. Tests cover enabled, disabled and non-internal task behavior. Review the internal-task predicate carefully to avoid allowing product-code tasks through the bypass.
```

## Task Boundary Snapshot

Task: `TASK-149` - PIPE-065 Apply internal Change gate bypass to UI runs
Status: `in_progress`

Scope:
- Define an internal project-control task predicate for safe bypass eligibility.
- Apply the bypass only to UI-created single-task sessions when the setting is enabled.
- Record explicit phase artifacts or audit details when the Change gate is bypassed.
- Keep approved Change requirements unchanged for non-internal tasks and non-UI execution paths.

Allowed Files:
- ai_project_ctl/pipeline/prepare_phase.py
- ai_project_ctl/pipeline/runner.py
- ai_project_ctl/pipeline/ui_policy.py
- scripts/aictl.py
- tests/pipeline/test_prepare_phase.py
- tests/test_ui_run_command.py

Acceptance Criteria:
- When the setting is disabled, UI runs still require an approved linked Change.
- When the setting is enabled, eligible internal project-control tasks can pass prepare without an approved linked Change.
- Non-internal tasks still block on missing approved Change even when the setting is enabled.
- Bypass usage is recorded in phase artifacts or audit details.
- Tests cover enabled, disabled and non-internal task behavior.

## Index Summary

Indexed source documents: `10`
Indexed chunks: `891`
Excluded registered sources: `135`
Selected chunks: `8`

Default exclusion policy: generated, inactive, archived, deprecated, template, and example documents are excluded unless explicitly allowed.

## Selected Sources

| Score | Source | Heading | Lines | Content hash | Chunk hash | Reasons |
| ---: | --- | --- | --- | --- | --- | --- |
| 126 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | heading token match: to; metadata token match: md, to; content token match: acceptance, and, approved, boundaries, bypass, can, changes, commit |
| 111 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | metadata token match: md; content token match: acceptance, ai_project, allow, and, approved, avoid, behavior, boundaries |
| 94 | `ai-system/project-control/06-prompt-package-spec.md` | 17. Relationship To taskctl.py And codexctl.py | 874-906 | `3444e8d40e40` | `6cf68be89257` | heading token match: and, py, to; metadata token match: and, md, project-control, py, to; content token match: an, and, audit, bypass, can, execution, for, generated |
| 91 | `ai-system/project-control/04-command-catalog.md` | 18. Additional Command Domains > Pipeline Commands | 2294-2321 | `f824429b0a39` | `efe882b18c98` | heading token match: pipeline; metadata token match: md, pipeline, project-control; content token match: acceptance, ai_project, ai_project_ctl, aictl, and, audit, change, evolution |
| 90 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Scope | 21-64 | `f824429b0a39` | `9c998142f16f` | metadata token match: md, project-control; content token match: ai_project_ctl, aictl, and, approved, change, evolution, execution, for |
| 88 | `ai-system/project-control/06-prompt-package-spec.md` | 14. Context Budget Rules > Context Pack Boundary | 797-833 | `3444e8d40e40` | `24706f89c068` | metadata token match: md, project-control; content token match: acceptance, and, audit, change, criteria, generated, in, is |
| 80 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Self-Hosted Command Boundary | 65-119 | `f824429b0a39` | `5b78d4503548` | metadata token match: md, project-control; content token match: acceptance, ai_project, aictl, and, approved, audit, criteria, generated |
| 80 | `ai-system/project-control/06-prompt-package-spec.md` | 3. Current Implementation | 123-162 | `3444e8d40e40` | `4fe051d2de08` | metadata token match: md, project-control; content token match: ai_project, allow, an, and, behavior, execution, explicit, for |

## Selected Context

### 1. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Recommended Skills To Create
Lines: `80-92`
Score: `126`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: heading token match: to; metadata token match: md, to; content token match: acceptance, and, approved, boundaries, bypass, can, changes, commit

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
Score: `111`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: metadata token match: md; content token match: acceptance, ai_project, allow, and, approved, avoid, behavior, boundaries

```text
## Existing Useful Skills

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Project Control Gateway Skill | Route plan, task, documentation and evolution work through the controlled CLI gateway instead of manual state edits. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Inspect state through CLI, choose allowed commands, run validation and render commands, report unsupported operations. | Manually edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**`; invent lifecycle states or commands; execute Initiative or Epic directly. |
| Clarification Gate Skill | Teach Codex and subagents when to inspect first, proceed with safe assumptions, or stop for Human Owner blocker questions. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Classify blockers, group owner questions, identify safe defaults, preserve task and approval boundaries. | Use questions to avoid normal inspection; ask for approval after every small step; self-approve accepted, approved, active or done states. |
| Documentation Navigation Skill | Route Codex and subagents to the minimal correct documentation and project-control read set before planning, editing, reviewing or executing AI_Development_System work.

[...truncated by contextctl...]
```

### 3. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 17. Relationship To taskctl.py And codexctl.py
Lines: `874-906`
Score: `94`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `6cf68be892579b77502246852781af90dc2942f367d5af5b0a3c4a4ee727323f`
Reasons: heading token match: and, py, to; metadata token match: and, md, project-control, py, to; content token match: an, and, audit, bypass, can, execution, for, generated

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

### 4. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: 18. Additional Command Domains > Pipeline Commands
Lines: `2294-2321`
Score: `91`
Content hash: `f824429b0a394aec9bfe9157302c1059a181374f040adbfb8136d2673f7fb1b6`
Chunk hash: `efe882b18c987d13ed38a60c38d0a9ba2dccd1c95061f72f79901f6f007ad46a`
Reasons: heading token match: pipeline; metadata token match: md, pipeline, project-control; content token match: acceptance, ai_project, ai_project_ctl, aictl, and, audit, change, evolution

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

### 5. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Scope
Lines: `21-64`
Score: `90`
Content hash: `f824429b0a394aec9bfe9157302c1059a181374f040adbfb8136d2673f7fb1b6`
Chunk hash: `9c998142f16f19b020151b13a6a80db5dfffa618771f91cbdd39a8467a7ee582`
Reasons: metadata token match: md, project-control; content token match: ai_project_ctl, aictl, and, approved, change, evolution, execution, for

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

### 6. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 14. Context Budget Rules > Context Pack Boundary
Lines: `797-833`
Score: `88`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `24706f89c068bb280d5630a712f0d9b260c02079a14823cc0a350875c71ba831`
Reasons: metadata token match: md, project-control; content token match: acceptance, and, audit, change, criteria, generated, in, is

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
Heading: Project Control Command Catalog > Self-Hosted Command Boundary
Lines: `65-119`
Score: `80`
Content hash: `f824429b0a394aec9bfe9157302c1059a181374f040adbfb8136d2673f7fb1b6`
Chunk hash: `5b78d45035483b51a58d0a7bed1cf1402fe3b2e6bc9a7ffcda911c0d12fcb6bc`
Reasons: metadata token match: md, project-control; content token match: acceptance, ai_project, aictl, and, approved, audit, criteria, generated

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

### 8. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 3. Current Implementation
Lines: `123-162`
Score: `80`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `4fe051d2de08383b0737cc69ca48f864bb8341acd7154ddc8b2d3a70fb1ad30a`
Reasons: metadata token match: md, project-control; content token match: ai_project, allow, an, and, behavior, execution, explicit, for

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

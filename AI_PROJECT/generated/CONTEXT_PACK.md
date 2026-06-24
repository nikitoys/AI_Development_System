<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-119 PIPE-040 Add tests for phase model and mutations Add tests for PhaseResult serialization, session phase fields, and governed phase mutation helpers. Protect the foundational phase state behavior before rewriting the runner. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Test PhaseResult construction and JSON conversion. Test session creation with phase field defaults. Test start_phase and record_phase_result mutations. Test validation behavior for legacy sessions without phase fields. Do not change behavior unrelated to this task. Do not refactor unrelated code. Do not edit protected project-control files manually. tests/test_pipeline_phase.py tests/test_pipeline_session_phase.py Tests pass for all PhaseResult statuses. Tests prove legacy pipeline sessions remain valid. Tests prove phase results append to phase_history. Tests prove terminal sessions reject new phase mutations. Check tests use temporary state and do not depend on local repository state. Verify tests do not require external Codex or network access.","schema_version":1,"task_id":"TASK-119"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-119`
Explicit query: `false`
Limit: `8`
Docs revision: `28`
Tasks revision: `1024`

## Query

```text
TASK-119 PIPE-040 Add tests for phase model and mutations Add tests for PhaseResult serialization, session phase fields, and governed phase mutation helpers. Protect the foundational phase state behavior before rewriting the runner. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Test PhaseResult construction and JSON conversion. Test session creation with phase field defaults. Test start_phase and record_phase_result mutations. Test validation behavior for legacy sessions without phase fields. Do not change behavior unrelated to this task. Do not refactor unrelated code. Do not edit protected project-control files manually. tests/test_pipeline_phase.py tests/test_pipeline_session_phase.py Tests pass for all PhaseResult statuses. Tests prove legacy pipeline sessions remain valid. Tests prove phase results append to phase_history. Tests prove terminal sessions reject new phase mutations. Check tests use temporary state and do not depend on local repository state. Verify tests do not require external Codex or network access.
```

## Task Boundary Snapshot

Task: `TASK-119` - PIPE-040 Add tests for phase model and mutations
Status: `in_progress`

Scope:
- Test PhaseResult construction and JSON conversion.
- Test session creation with phase field defaults.
- Test start_phase and record_phase_result mutations.
- Test validation behavior for legacy sessions without phase fields.

Allowed Files:
- tests/test_pipeline_phase.py
- tests/test_pipeline_session_phase.py

Acceptance Criteria:
- Tests pass for all PhaseResult statuses.
- Tests prove legacy pipeline sessions remain valid.
- Tests prove phase results append to phase_history.
- Tests prove terminal sessions reject new phase mutations.

## Index Summary

Indexed source documents: `10`
Indexed chunks: `891`
Excluded registered sources: `135`
Selected chunks: `8`

Default exclusion policy: generated, inactive, archived, deprecated, template, and example documents are excluded unless explicitly allowed.

## Selected Sources

| Score | Source | Heading | Lines | Content hash | Chunk hash | Reasons |
| ---: | --- | --- | --- | --- | --- | --- |
| 91 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | metadata token match: md; content token match: acceptance, add, ai_project, and, before, behavior, change, codex |
| 88 | `ai-system/project-control/03-state-model.md` | Project Control State Model > Context Control State | 104-125 | `9e818e514763` | `0cd80bdf0d55` | heading token match: model, state; metadata token match: md, model, project-control, state; content token match: acceptance, ai_project, and, criteria, files, generated, json, md |
| 88 | `ai-system/project-control/06-prompt-package-spec.md` | 17. Relationship To taskctl.py And codexctl.py | 874-906 | `3444e8d40e40` | `6cf68be89257` | heading token match: and, py, to; metadata token match: and, md, project-control, py, to; content token match: and, before, codex, for, generated, md, not, or |
| 84 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | heading token match: to; metadata token match: md, to; content token match: acceptance, and, before, check, criteria, edit, files, for |
| 74 | `ai-system/project-control/06-prompt-package-spec.md` | 12. Prompt Package Template | 580-670 | `3444e8d40e40` | `4b3949b96350` | metadata token match: md, project-control; content token match: acceptance, ai_project, and, change, criteria, do, edit, files |
| 73 | `ai-system/project-control/04-command-catalog.md` | 18. Additional Command Domains > Pipeline Commands | 2294-2321 | `f824429b0a39` | `efe882b18c98` | heading token match: pipeline; metadata token match: md, pipeline, project-control; content token match: acceptance, ai_project, and, change, codex, edit, generated, json |
| 72 | `ai-system/project-control/07-validation-and-tests.md` | 20. Acceptance Criteria For Validation Layer | 1368-1386 | `61710bd7deee` | `9ed7e5fda92c` | heading token match: acceptance, criteria, for, validation; metadata token match: acceptance, and, criteria, for, md, project-control, tests, validation; content token match: acceptance, and, criteria, do, for, generated, mutations, not |
| 71 | `ai-system/project-control/07-validation-and-tests.md` | Project Control Validation and Tests > Scope | 24-66 | `61710bd7deee` | `c7628c28ceb9` | heading token match: and, tests, validation; metadata token match: and, md, project-control, tests, validation; content token match: ai_project, and, check, codex, codex_current, for, generated, json |

## Selected Context

### 1. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Existing Useful Skills
Lines: `34-43`
Score: `91`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: metadata token match: md; content token match: acceptance, add, ai_project, and, before, behavior, change, codex

```text
## Existing Useful Skills

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Project Control Gateway Skill | Route plan, task, documentation and evolution work through the controlled CLI gateway instead of manual state edits. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Inspect state through CLI, choose allowed commands, run validation and render commands, report unsupported operations. | Manually edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**`; invent lifecycle states or commands; execute Initiative or Epic directly. |
| Clarification Gate Skill | Teach Codex and subagents when to inspect first, proceed with safe assumptions, or stop for Human Owner blocker questions. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Classify blockers, group owner questions, identify safe defaults, preserve task and approval boundaries. | Use questions to avoid normal inspection; ask for approval after every small step; self-approve accepted, approved, active or done states. |
| Documentation Navigation Skill | Route Codex and subagents to the minimal correct documentation and project-control read set before planning, editing, reviewing or executing AI_Development_System work.

[...truncated by contextctl...]
```

### 2. `ai-system/project-control/03-state-model.md`

Title: Project Control State Model
Status: `active`  Type: `reference`
Heading: Project Control State Model > Context Control State
Lines: `104-125`
Score: `88`
Content hash: `9e818e514763e69aa2f56bb5d9ca080d47b7330db3aa016982c5d3ee0bc2be81`
Chunk hash: `0cd80bdf0d55e5284fa6355477f50005896398136bf33b7e1a181718f309f8b4`
Reasons: heading token match: model, state; metadata token match: md, model, project-control, state; content token match: acceptance, ai_project, and, criteria, files, generated, json, md

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

### 3. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 17. Relationship To taskctl.py And codexctl.py
Lines: `874-906`
Score: `88`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `6cf68be892579b77502246852781af90dc2942f367d5af5b0a3c4a4ee727323f`
Reasons: heading token match: and, py, to; metadata token match: and, md, project-control, py, to; content token match: and, before, codex, for, generated, md, not, or

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

### 4. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Recommended Skills To Create
Lines: `80-92`
Score: `84`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: heading token match: to; metadata token match: md, to; content token match: acceptance, and, before, check, criteria, edit, files, for

```text
## Recommended Skills To Create

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Documentation Control Skill | Guide documentation registration, status changes, generated indexes and documentation validation. | `docctl.py` | P0 | Register documents, set draft/review status, render/check generated docs, explain documentation lifecycle. | Mark documents active without Human Owner approval; manually edit `docs.json`, doc events or generated doc indexes. |
| Protected Files Skill | Keep agents inside the protected-files boundary and detect unsafe project-control edits. | `check-protected-project-files.py`, `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Explain protected paths, run protected-files checks, route repairs through CLIs. | Edit protected state/events/generated files manually; use ad hoc scripts to mutate protected files; hide drift. |
| Review Gate Skill | Guide review intake before a Task can be accepted or closed. | `taskctl.py`; future review control CLI if approved | P1 | Check scope, allowed files, acceptance criteria, validation output and review status; recommend APPROVED, REWORK, REJECTED or DEFERRED. | Self-approve work; mark a Task done without the required approval path; ignore Critical or Major findings. |

[...truncated by contextctl...]
```

### 5. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 12. Prompt Package Template
Lines: `580-670`
Score: `74`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `4b3949b963506d03a8ca61d2f28eb70f0cc2ca715a4c20495bab284ca4d8fcb0`
Reasons: metadata token match: md, project-control; content token match: acceptance, ai_project, and, change, criteria, do, edit, files

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

### 6. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: 18. Additional Command Domains > Pipeline Commands
Lines: `2294-2321`
Score: `73`
Content hash: `f824429b0a394aec9bfe9157302c1059a181374f040adbfb8136d2673f7fb1b6`
Chunk hash: `efe882b18c987d13ed38a60c38d0a9ba2dccd1c95061f72f79901f6f007ad46a`
Reasons: heading token match: pipeline; metadata token match: md, pipeline, project-control; content token match: acceptance, ai_project, and, change, codex, edit, generated, json

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

### 7. `ai-system/project-control/07-validation-and-tests.md`

Title: Project Control Validation and Tests
Status: `active`  Type: `process`
Heading: 20. Acceptance Criteria For Validation Layer
Lines: `1368-1386`
Score: `72`
Content hash: `61710bd7deeed5b710aa500acaf478c77f7ad43ffcd3943c0245da65015ff2c9`
Chunk hash: `9ed7e5fda92cce9da485202d3c05867d3fcf000f7ab294fcf2397088db94d3cf`
Reasons: heading token match: acceptance, criteria, for, validation; metadata token match: acceptance, and, criteria, for, md, project-control, tests, validation; content token match: acceptance, and, criteria, do, for, generated, mutations, not

```text
# 20. Acceptance Criteria For Validation Layer

Validation and tests are acceptable when:

```text id="xnp5jd"
- happy path passes in a temp root;
- invalid lifecycle transitions fail;
- missing parent references fail;
- generated task drift is detected;
- prompt build requires selected or explicit Task;
- audit events are written for successful mutations;
- failed commands do not write success events;
- task validation checks plan references by default;
- generated Markdown can be regenerated;
- smoke test can run locally and in CI.
```

---
```

### 8. `ai-system/project-control/07-validation-and-tests.md`

Title: Project Control Validation and Tests
Status: `active`  Type: `process`
Heading: Project Control Validation and Tests > Scope
Lines: `24-66`
Score: `71`
Content hash: `61710bd7deeed5b710aa500acaf478c77f7ad43ffcd3943c0245da65015ff2c9`
Chunk hash: `c7628c28ceb90b78d021d891a5ed10b1dc2cf8a114509631a433dd7fcc04c70d`
Reasons: heading token match: and, tests, validation; metadata token match: and, md, project-control, tests, validation; content token match: ai_project, and, check, codex, codex_current, for, generated, json

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

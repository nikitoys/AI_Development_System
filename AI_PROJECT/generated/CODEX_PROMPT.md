# Codex Prompt Package

Generated: 2026-06-20T06:44:47Z
Source Type: task
Source ID: TASK-062
Source Status: in_review

[SYSTEM]

Active Role:
AI System Maintainer / QA Lead AI

Active Stage:
Auto Review and Close Policy

Active Document:
ai_project_ctl/pipeline/close_policy.py

Expected Result:
Pipeline can safely close or request changes for tasks only when policy and review gates allow it.

Repository Context:
This repository is an AI Development System governance control plane.
Project-control state is managed through Python CLI gateways; generated Markdown is derived output.

Source:
Source Task: TASK-062
Task Status: in_review
Title: PIPE-11 Auto Review Auto Close Policy

Apply policy-controlled close/rework decisions only after Machine Review PASS and Codex Review APPROVE.

Implement the decision logic that maps review gate results into task done, changes_requested, rework loop, or stop states under explicit automation policy.

Scope:
- Implement decision logic for Machine Review result plus Codex Review result.
- Allow auto-close only if policy allows and Machine Review PASS and Codex Review APPROVE.
- Move task to changes_requested or start a bounded rework loop only when policy allows and review verdict requests changes.
- Stop when review is blocked, malformed, failing, or policy disallows automatic lifecycle mutation.
- Require explicit audit notes that identify policy, machine gate, Codex review verdict, and report id.
- Prevent auto-close when task report has blockers or changed files outside allowed_files.
- Add tests for approve+pass close, request changes, blocked review, machine fail, policy disabled, and rework-limit reached.

Out of Scope:
- Do not bypass task lifecycle transitions.
- Do not accept linked Evolution Changes.
- Do not commit.
- Do not treat Codex Review as Human Owner approval outside the selected policy.
- Do not continue rework indefinitely.

Allowed Files:
- ai_project_ctl/pipeline/close_policy.py
- ai_project_ctl/pipeline/runner.py if integration is needed
- ai_project_ctl/core/workflows.py if close/request-changes workflow metadata needs compatible updates
- tests/**
- ai-system/project-control/** if auto-close documentation is needed

Implementation Instructions:
- Inspect current files before editing.
- Stay within allowed files.
- Preserve existing conventions.
- Prefer minimal, commit-ready changes.
- Do not perform unrelated refactors.
- Do not edit AI_PROJECT/state/**, AI_PROJECT/events/** or AI_PROJECT/generated/** manually.

Retrieved Context:
- Context Pack path: `AI_PROJECT/generated/CONTEXT_PACK.md`
- Context Pack SHA-256: `e51ce1cf7614b3c4e41b15cc098a609cd3b817ce7133c2644eb26bbd996e4e3f`
- Context mode: `task`
- Context task ID: `TASK-062`
- Docs revision: `24`
- Tasks revision: `552`

Retrieved Context Rules:
- Retrieved context is read-only.
- Retrieved context does not expand Allowed Files.
- Retrieved context does not expand Scope or override Out of Scope.
- Retrieved context does not replace Acceptance Criteria.
- If retrieved context conflicts with the source Task, source documents, or Human Owner instructions, report the conflict.

Retrieved Context Source Metadata:
- `ai-system/skills/README.md` lines 80-92; heading: Skills Layer Roadmap > Recommended Skills To Create; content: `dbf637225bec`; chunk: `eef80c572381`
- `ai-system/skills/README.md` lines 34-43; heading: Skills Layer Roadmap > Existing Useful Skills; content: `dbf637225bec`; chunk: `758bde12e28c`
- `ai-system/project-control/06-prompt-package-spec.md` lines 874-906; heading: 17. Relationship To taskctl.py And codexctl.py; content: `3444e8d40e40`; chunk: `6cf68be89257`
- `ai-system/project-control/06-prompt-package-spec.md` lines 797-833; heading: 14. Context Budget Rules > Context Pack Boundary; content: `3444e8d40e40`; chunk: `24706f89c068`
- `ai-system/agent-delegation.md` lines 164-188; heading: Agent Delegation > Controller Codex Responsibilities; content: `32bd223e6d3c`; chunk: `f8c99caf941d`
- `ai-system/project-control/04-command-catalog.md` lines 64-118; heading: Project Control Command Catalog > Self-Hosted Command Boundary; content: `d6bfbf03256d`; chunk: `749381be335a`
- `ai-system/agent-delegation.md` lines 146-155; heading: Agent Delegation > Relationship To Task Lifecycle; content: `32bd223e6d3c`; chunk: `fc167b5e741f`
- `ai-system/project-control/06-prompt-package-spec.md` lines 580-670; heading: 12. Prompt Package Template; content: `3444e8d40e40`; chunk: `4b3949b96350`

Retrieved Context Pack Content:

````text
<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-062 PIPE-11 Auto Review Auto Close Policy Apply policy-controlled close/rework decisions only after Machine Review PASS and Codex Review APPROVE. Implement the decision logic that maps review gate results into task done, changes_requested, rework loop, or stop states under explicit automation policy. ai_project_ctl/pipeline/close_policy.py Pipeline can safely close or request changes for tasks only when policy and review gates allow it. Implement decision logic for Machine Review result plus Codex Review result. Allow auto-close only if policy allows and Machine Review PASS and Codex Review APPROVE. Move task to changes_requested or start a bounded rework loop only when policy allows and review verdict requests changes. Stop when review is blocked, malformed, failing, or policy disallows automatic lifecycle mutation. Require explicit audit notes that identify policy, machine gate, Codex review verdict, and report id. Prevent auto-close when task report has blockers or changed files outside allowed_files. Add tests for approve+pass close, request changes, blocked review, machine fail, policy disabled, and rework-limit reached. Do not bypass task lifecycle transitions. Do not accept linked Evolution Changes. Do not commit. Do not treat Codex Review as Human Owner approval outside the selected policy. Do not continue rework indefinitely. ai_project_ctl/pipeline/close_policy.py ai_project_ctl/pipeline/runner.py if integration is needed ai_project_ctl/core/workflows.py if close/request-changes workflow metadata needs compatible updates tests/** ai-system/project-control/** if auto-close documentation is needed Auto-close requires policy permission, Machine Review PASS, and Codex Review APPROVE. REQUEST_CHANGES moves to changes_requested or starts rework only if policy allows. Blocked or failed gates stop the pipeline. Rework loop has a policy-controlled maximum. Lifecycle mutations route through governed task workflows/commands. Tests and project-control validations pass. Verify auto-close cannot happen on Machine Review FAIL or Codex Review REQUEST_CHANGES. Verify lifecycle changes are routed through governed commands.","schema_version":1,"task_id":"TASK-062"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-062`
Explicit query: `false`
Limit: `8`
Docs revision: `24`
Tasks revision: `552`

## Query

```text
TASK-062 PIPE-11 Auto Review Auto Close Policy Apply policy-controlled close/rework decisions only after Machine Review PASS and Codex Review APPROVE. Implement the decision logic that maps review gate results into task done, changes_requested, rework loop, or stop states under explicit automation policy. ai_project_ctl/pipeline/close_policy.py Pipeline can safely close or request changes for tasks only when policy and review gates allow it. Implement decision logic for Machine Review result plus Codex Review result. Allow auto-close only if policy allows and Machine Review PASS and Codex Review APPROVE. Move task to changes_requested or start a bounded rework loop only when policy allows and review verdict requests changes. Stop when review is blocked, malformed, failing, or policy disallows automatic lifecycle mutation. Require explicit audit notes that identify policy, machine gate, Codex review verdict, and report id. Prevent auto-close when task report has blockers or changed files outside allowed_files. Add tests for approve+pass close, request changes, blocked review, machine fail, policy disabled, and rework-limit reached. Do not bypass task lifecycle transitions. Do not accept linked Evolution Changes. Do not commit. Do not treat Codex Review as Human Owner approval outside the selected policy. Do not continue rework indefinitely. ai_project_ctl/pipeline/close_policy.py ai_project_ctl/pipeline/runner.py if integration is needed ai_project_ctl/core/workflows.py if close/request-changes workflow metadata needs compatible updates tests/** ai-system/project-control/** if auto-close documentation is needed Auto-close requires policy permission, Machine Review PASS, and Codex Review APPROVE. REQUEST_CHANGES moves to changes_requested or starts rework only if policy allows. Blocked or failed gates stop the pipeline. Rework loop has a policy-controlled maximum. Lifecycle mutations route through governed task workflows/commands. Tests and project-control validations pass. Verify auto-close cannot happen on Machine Review FAIL or Codex Review REQUEST_CHANGES. Verify lifecycle changes are routed through governed commands.
```

## Task Boundary Snapshot

Task: `TASK-062` - PIPE-11 Auto Review Auto Close Policy
Status: `in_review`

Scope:
- Implement decision logic for Machine Review result plus Codex Review result.
- Allow auto-close only if policy allows and Machine Review PASS and Codex Review APPROVE.
- Move task to changes_requested or start a bounded rework loop only when policy allows and review verdict requests changes.
- Stop when review is blocked, malformed, failing, or policy disallows automatic lifecycle mutation.
- Require explicit audit notes that identify policy, machine gate, Codex review verdict, and report id.
- Prevent auto-close when task report has blockers or changed files outside allowed_files.
- Add tests for approve+pass close, request changes, blocked review, machine fail, policy disabled, and rework-limit reached.

Allowed Files:
- ai_project_ctl/pipeline/close_policy.py
- ai_project_ctl/pipeline/runner.py if integration is needed
- ai_project_ctl/core/workflows.py if close/request-changes workflow metadata needs compatible updates
- tests/**
- ai-system/project-control/** if auto-close documentation is needed

Acceptance Criteria:
- Auto-close requires policy permission, Machine Review PASS, and Codex Review APPROVE.
- REQUEST_CHANGES moves to changes_requested or starts rework only if policy allows.
- Blocked or failed gates stop the pipeline.
- Rework loop has a policy-controlled maximum.
- Lifecycle mutations route through governed task workflows/commands.
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
| 166 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | heading token match: to; metadata token match: ai-system, to; content token match: a, accept, and, approval, as, automatic, bounded, bypass |
| 155 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | metadata token match: ai-system; content token match: a, add, after, allow, allows, and, approval, approve |
| 100 | `ai-system/project-control/06-prompt-package-spec.md` | 17. Relationship To taskctl.py And codexctl.py | 874-906 | `3444e8d40e40` | `6cf68be89257` | heading token match: and, py, to; metadata token match: ai-system, and, project-control, py, to; content token match: a, and, audit, bypass, can, codex, for, id |
| 98 | `ai-system/project-control/06-prompt-package-spec.md` | 14. Context Budget Rules > Context Pack Boundary | 797-833 | `3444e8d40e40` | `24706f89c068` | metadata token match: ai-system, project-control; content token match: a, add, and, audit, bounded, codex, documentation, fail |
| 96 | `ai-system/agent-delegation.md` | Agent Delegation > Controller Codex Responsibilities | 164-188 | `32bd223e6d3c` | `f8c99caf941d` | heading token match: codex; metadata token match: ai-system, codex; content token match: accept, after, and, approval, approve, bounded, codex, files |
| 94 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Self-Hosted Command Boundary | 64-118 | `d6bfbf03256d` | `749381be335a` | metadata token match: ai-system, project-control; content token match: a, ai-system, and, are, as, audit, bounded, changed |
| 90 | `ai-system/agent-delegation.md` | Agent Delegation > Relationship To Task Lifecycle | 146-155 | `32bd223e6d3c` | `fc167b5e741f` | heading token match: lifecycle, task, to; metadata token match: ai-system, lifecycle, task, to; content token match: a, allow, and, approval, bounded, codex, done, human |
| 88 | `ai-system/project-control/06-prompt-package-spec.md` | 12. Prompt Package Template | 580-670 | `3444e8d40e40` | `4b3949b96350` | metadata token match: ai-system, project-control; content token match: and, bounded, changed, commands, do, files, id, if |

## Selected Context

### 1. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Recommended Skills To Create
Lines: `80-92`
Score: `166`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: heading token match: to; metadata token match: ai-system, to; content token match: a, accept, and, approval, as, automatic, bounded, bypass

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
Score: `155`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: metadata token match: ai-system; content token match: a, add, after, allow, allows, and, approval, approve

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
Score: `100`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `6cf68be892579b77502246852781af90dc2942f367d5af5b0a3c4a4ee727323f`
Reasons: heading token match: and, py, to; metadata token match: ai-system, and, project-control, py, to; content token match: a, and, audit, bypass, can, codex, for, id

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
Heading: 14. Context Budget Rules > Context Pack Boundary
Lines: `797-833`
Score: `98`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `24706f89c068bb280d5630a712f0d9b260c02079a14823cc0a350875c71ba831`
Reasons: metadata token match: ai-system, project-control; content token match: a, add, and, audit, bounded, codex, documentation, fail

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

### 5. `ai-system/agent-delegation.md`

Title: Agent Delegation
Status: `active`  Type: `reference`
Heading: Agent Delegation > Controller Codex Responsibilities
Lines: `164-188`
Score: `96`
Content hash: `32bd223e6d3cdc201f8f6ec84470fd443185ed819cbd3def36af2d50e78caf67`
Chunk hash: `f8c99caf941dd8b28489293eb096bc89f67d332e2aa1ce7eb3283c6a486abb46`
Reasons: heading token match: codex; metadata token match: ai-system, codex; content token match: accept, after, and, approval, approve, bounded, codex, files

```text
## Controller Codex Responsibilities

Controller Codex is responsible for:

- reading project-control state and source documents;
- selecting the minimal source context;
- checking that the parent Task or Agent Work Package is bounded;
- preparing the Worker Agent Prompt Package;
- stating scope, out of scope, allowed files and forbidden actions;
- requiring structured result output;
- receiving the Worker Agent Result;
- performing Agent Result Intake;
- routing Integration Review, review or QA when needed;
- updating lifecycle state only through CLI gateways;
- preserving Human Owner approval boundaries.

Controller Codex must not:

- launch Worker Agent sessions automatically;
- approve Worker Agent output automatically;
- accept final task results for the Human Owner;
- edit protected `AI_PROJECT` files manually;
- imply that L4 or runtime behavior is approved;
- widen Worker Agent scope after the handoff without owner-controlled task updates.
```

### 6. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Self-Hosted Command Boundary
Lines: `64-118`
Score: `94`
Content hash: `d6bfbf03256d4d5a7f005184d36c94434a45640595c0d654fc463065a1428adf`
Chunk hash: `749381be335ac66aa70d957f55a95f190d998afd70c4347643a6c88c059f6587`
Reasons: metadata token match: ai-system, project-control; content token match: a, ai-system, and, are, as, audit, bounded, changed

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

### 7. `ai-system/agent-delegation.md`

Title: Agent Delegation
Status: `active`  Type: `reference`
Heading: Agent Delegation > Relationship To Task Lifecycle
Lines: `146-155`
Score: `90`
Content hash: `32bd223e6d3cdc201f8f6ec84470fd443185ed819cbd3def36af2d50e78caf67`
Chunk hash: `fc167b5e741f55e7bac5c8b0ce6fbf8a50f60d8059372ee1bbc62c20b5e51496`
Reasons: heading token match: lifecycle, task, to; metadata token match: ai-system, lifecycle, task, to; content token match: a, allow, and, approval, bounded, codex, done, human

```text
## Relationship To Task Lifecycle

A Worker Agent prompt must be tied to one bounded Task or one bounded Agent Work Package under a Task.

Task state remains controlled by `taskctl.py`.

Controller Codex may update task lifecycle state only through `taskctl.py` and only when the task scope, review state and Human Owner approval allow it.

Worker Agent must not mark tasks done.
```

### 8. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 12. Prompt Package Template
Lines: `580-670`
Score: `88`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `4b3949b963506d03a8ca61d2f28eb70f0cc2ca715a4c20495bab284ca4d8fcb0`
Reasons: metadata token match: ai-system, project-control; content token match: and, bounded, changed, commands, do, files, id, if

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
````

Acceptance Criteria:
- Auto-close requires policy permission, Machine Review PASS, and Codex Review APPROVE.
- REQUEST_CHANGES moves to changes_requested or starts rework only if policy allows.
- Blocked or failed gates stop the pipeline.
- Rework loop has a policy-controlled maximum.
- Lifecycle mutations route through governed task workflows/commands.
- Tests and project-control validations pass.

Verification:
- Use verification mode `strict`.
- Run the validation commands required by the task and report results.

Result Format:
- Summary
- Changed files
- Commands run
- Verification result
- Blockers or risks

Review / Result Format Notes:
- Verify auto-close cannot happen on Machine Review FAIL or Codex Review REQUEST_CHANGES.
- Verify lifecycle changes are routed through governed commands.

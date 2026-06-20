# Codex Prompt Package

Generated: 2026-06-20T06:47:12Z
Source Type: task
Source ID: TASK-063
Source Status: in_progress

[SYSTEM]

Active Role:
DevOps Engineer AI / Git Safety Reviewer

Active Stage:
Controlled Local Commit Action

Active Document:
ai_project_ctl/pipeline/git_commit.py

Expected Result:
Pipeline can optionally create a local commit only when commit policy allows and readiness checks are green.

Repository Context:
This repository is an AI Development System governance control plane.
Project-control state is managed through Python CLI gateways; generated Markdown is derived output.

Source:
Source Task: TASK-063
Task Status: in_progress
Title: PIPE-12 Controlled Git Commit Action

Create local commits only when policy allows and commit readiness is green.

Add a controlled local git commit action for completed pipeline work. It must never push, merge, reset, discard, or create remote changes.

Scope:
- Implement read-only commit readiness check reuse or integration with the existing Commit Readiness view.
- Implement local commit action only behind explicit policy permission.
- Require clean readiness: task done, required Change accepted if policy requires it, machine checks pass, protected-file checks pass, generated outputs fresh, no unrelated dirty files unless policy explicitly allows.
- Stage only files approved by policy/session evidence.
- Generate commit message from completed task refs, Change ids, and session id.
- Run git commit locally only; explicitly forbid push, merge, reset, checkout, rebase, and destructive git commands.
- Record commit hash or failure in pipeline session/audit.
- Add tests with fake git runner for readiness green, readiness fail, unrelated files, commit success, and forbidden command attempts.

Out of Scope:
- Do not push.
- Do not merge.
- Do not open PRs.
- Do not discard or reset changes.
- Do not commit when readiness is not green.
- Do not auto-accept Changes in this task.

Allowed Files:
- ai_project_ctl/pipeline/git_commit.py
- ai_project_ctl/pipeline/runner.py if integration is needed
- ai_project_ctl/web/read_model.py if commit readiness data is reused
- ai_project_ctl/core/registry.py if command metadata is needed
- scripts/aictl.py if commit command routing is needed
- tests/**
- ai-system/project-control/** if git commit policy documentation is needed

Implementation Instructions:
- Inspect current files before editing.
- Stay within allowed files.
- Preserve existing conventions.
- Prefer minimal, commit-ready changes.
- Do not perform unrelated refactors.
- Do not edit AI_PROJECT/state/**, AI_PROJECT/events/** or AI_PROJECT/generated/** manually.

Retrieved Context:
- Context Pack path: `AI_PROJECT/generated/CONTEXT_PACK.md`
- Context Pack SHA-256: `add556f80f57dc0139d7c85c012e585269f7f4f768fdd52d0286728920ead1e5`
- Context mode: `task`
- Context task ID: `TASK-063`
- Docs revision: `24`
- Tasks revision: `556`

Retrieved Context Rules:
- Retrieved context is read-only.
- Retrieved context does not expand Allowed Files.
- Retrieved context does not expand Scope or override Out of Scope.
- Retrieved context does not replace Acceptance Criteria.
- If retrieved context conflicts with the source Task, source documents, or Human Owner instructions, report the conflict.

Retrieved Context Source Metadata:
- `ai-system/skills/README.md` lines 80-92; heading: Skills Layer Roadmap > Recommended Skills To Create; content: `dbf637225bec`; chunk: `eef80c572381`
- `ai-system/skills/README.md` lines 34-43; heading: Skills Layer Roadmap > Existing Useful Skills; content: `dbf637225bec`; chunk: `758bde12e28c`
- `ai-system/project-control/04-command-catalog.md` lines 64-118; heading: Project Control Command Catalog > Self-Hosted Command Boundary; content: `d6bfbf03256d`; chunk: `749381be335a`
- `ai-system/project-control/06-prompt-package-spec.md` lines 797-833; heading: 14. Context Budget Rules > Context Pack Boundary; content: `3444e8d40e40`; chunk: `24706f89c068`
- `ai-system/project-control/04-command-catalog.md` lines 21-63; heading: Project Control Command Catalog > Scope; content: `d6bfbf03256d`; chunk: `d914c61786e4`
- `ai-system/project-control/06-prompt-package-spec.md` lines 874-906; heading: 17. Relationship To taskctl.py And codexctl.py; content: `3444e8d40e40`; chunk: `6cf68be89257`
- `ai-system/project-control/06-prompt-package-spec.md` lines 580-670; heading: 12. Prompt Package Template; content: `3444e8d40e40`; chunk: `4b3949b96350`
- `ai-system/project-control/07-validation-and-tests.md` lines 1113-1133; heading: 13. Done And Archived Immutability Tests > 13.1 Done Task Mutation > Command; content: `61710bd7deee`; chunk: `693e8700b033`

Retrieved Context Pack Content:

````text
<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-063 PIPE-12 Controlled Git Commit Action Create local commits only when policy allows and commit readiness is green. Add a controlled local git commit action for completed pipeline work. It must never push, merge, reset, discard, or create remote changes. ai_project_ctl/pipeline/git_commit.py Pipeline can optionally create a local commit only when commit policy allows and readiness checks are green. Implement read-only commit readiness check reuse or integration with the existing Commit Readiness view. Implement local commit action only behind explicit policy permission. Require clean readiness: task done, required Change accepted if policy requires it, machine checks pass, protected-file checks pass, generated outputs fresh, no unrelated dirty files unless policy explicitly allows. Stage only files approved by policy/session evidence. Generate commit message from completed task refs, Change ids, and session id. Run git commit locally only; explicitly forbid push, merge, reset, checkout, rebase, and destructive git commands. Record commit hash or failure in pipeline session/audit. Add tests with fake git runner for readiness green, readiness fail, unrelated files, commit success, and forbidden command attempts. Do not push. Do not merge. Do not open PRs. Do not discard or reset changes. Do not commit when readiness is not green. Do not auto-accept Changes in this task. ai_project_ctl/pipeline/git_commit.py ai_project_ctl/pipeline/runner.py if integration is needed ai_project_ctl/web/read_model.py if commit readiness data is reused ai_project_ctl/core/registry.py if command metadata is needed scripts/aictl.py if commit command routing is needed tests/** ai-system/project-control/** if git commit policy documentation is needed Commit action is disabled unless policy explicitly allows local commit. Commit action refuses when commit readiness is not green. Commit action stages only approved files. Commit action never pushes, merges, resets, rebases, or discards changes. Commit result is recorded in session/audit. Tests and project-control validations pass. Verify command allowlist forbids push/merge/destructive git actions. Verify readiness failure blocks commit.","schema_version":1,"task_id":"TASK-063"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-063`
Explicit query: `false`
Limit: `8`
Docs revision: `24`
Tasks revision: `556`

## Query

```text
TASK-063 PIPE-12 Controlled Git Commit Action Create local commits only when policy allows and commit readiness is green. Add a controlled local git commit action for completed pipeline work. It must never push, merge, reset, discard, or create remote changes. ai_project_ctl/pipeline/git_commit.py Pipeline can optionally create a local commit only when commit policy allows and readiness checks are green. Implement read-only commit readiness check reuse or integration with the existing Commit Readiness view. Implement local commit action only behind explicit policy permission. Require clean readiness: task done, required Change accepted if policy requires it, machine checks pass, protected-file checks pass, generated outputs fresh, no unrelated dirty files unless policy explicitly allows. Stage only files approved by policy/session evidence. Generate commit message from completed task refs, Change ids, and session id. Run git commit locally only; explicitly forbid push, merge, reset, checkout, rebase, and destructive git commands. Record commit hash or failure in pipeline session/audit. Add tests with fake git runner for readiness green, readiness fail, unrelated files, commit success, and forbidden command attempts. Do not push. Do not merge. Do not open PRs. Do not discard or reset changes. Do not commit when readiness is not green. Do not auto-accept Changes in this task. ai_project_ctl/pipeline/git_commit.py ai_project_ctl/pipeline/runner.py if integration is needed ai_project_ctl/web/read_model.py if commit readiness data is reused ai_project_ctl/core/registry.py if command metadata is needed scripts/aictl.py if commit command routing is needed tests/** ai-system/project-control/** if git commit policy documentation is needed Commit action is disabled unless policy explicitly allows local commit. Commit action refuses when commit readiness is not green. Commit action stages only approved files. Commit action never pushes, merges, resets, rebases, or discards changes. Commit result is recorded in session/audit. Tests and project-control validations pass. Verify command allowlist forbids push/merge/destructive git actions. Verify readiness failure blocks commit.
```

## Task Boundary Snapshot

Task: `TASK-063` - PIPE-12 Controlled Git Commit Action
Status: `in_progress`

Scope:
- Implement read-only commit readiness check reuse or integration with the existing Commit Readiness view.
- Implement local commit action only behind explicit policy permission.
- Require clean readiness: task done, required Change accepted if policy requires it, machine checks pass, protected-file checks pass, generated outputs fresh, no unrelated dirty files unless policy explicitly allows.
- Stage only files approved by policy/session evidence.
- Generate commit message from completed task refs, Change ids, and session id.
- Run git commit locally only; explicitly forbid push, merge, reset, checkout, rebase, and destructive git commands.
- Record commit hash or failure in pipeline session/audit.
- Add tests with fake git runner for readiness green, readiness fail, unrelated files, commit success, and forbidden command attempts.

Allowed Files:
- ai_project_ctl/pipeline/git_commit.py
- ai_project_ctl/pipeline/runner.py if integration is needed
- ai_project_ctl/web/read_model.py if commit readiness data is reused
- ai_project_ctl/core/registry.py if command metadata is needed
- scripts/aictl.py if commit command routing is needed
- tests/**
- ai-system/project-control/** if git commit policy documentation is needed

Acceptance Criteria:
- Commit action is disabled unless policy explicitly allows local commit.
- Commit action refuses when commit readiness is not green.
- Commit action stages only approved files.
- Commit action never pushes, merges, resets, rebases, or discards changes.
- Commit result is recorded in session/audit.
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
| 160 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | heading token match: create; metadata token match: ai-system, create; content token match: a, accepted, actions, and, approved, can, changes, check |
| 134 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | heading token match: existing; metadata token match: ai-system, existing; content token match: a, accepted, actions, add, allows, and, approved, by |
| 119 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Self-Hosted Command Boundary | 64-118 | `d6bfbf03256d` | `749381be335a` | heading token match: command; metadata token match: ai-system, command, project-control; content token match: a, ai-system, aictl, and, approved, are, audit, by |
| 104 | `ai-system/project-control/06-prompt-package-spec.md` | 14. Context Budget Rules > Context Pack Boundary | 797-833 | `3444e8d40e40` | `24706f89c068` | metadata token match: ai-system, project-control; content token match: a, add, and, audit, by, change, documentation, explicitly |
| 96 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Scope | 21-63 | `d6bfbf03256d` | `d914c61786e4` | heading token match: command; metadata token match: ai-system, command, project-control; content token match: a, actions, add, aictl, and, approved, change, command |
| 95 | `ai-system/project-control/06-prompt-package-spec.md` | 17. Relationship To taskctl.py And codexctl.py | 874-906 | `3444e8d40e40` | `6cf68be89257` | heading token match: and, py; metadata token match: ai-system, and, project-control, py; content token match: a, and, audit, by, can, existing, for, generated |
| 94 | `ai-system/project-control/06-prompt-package-spec.md` | 12. Prompt Package Template | 580-670 | `3444e8d40e40` | `4b3949b96350` | metadata token match: ai-system, project-control; content token match: action, and, by, change, checks, command, commands, do |
| 83 | `ai-system/project-control/07-validation-and-tests.md` | 13. Done And Archived Immutability Tests > 13.1 Done Task Mutation > Command | 1113-1133 | `61710bd7deee` | `693e8700b033` | heading token match: and, command, done, task, tests; metadata token match: ai-system, and, command, done, project-control, task, tests; content token match: approved, command, create, done, fail, id, py, scripts |

## Selected Context

### 1. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Recommended Skills To Create
Lines: `80-92`
Score: `160`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: heading token match: create; metadata token match: ai-system, create; content token match: a, accepted, actions, and, approved, can, changes, check

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
Score: `134`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: heading token match: existing; metadata token match: ai-system, existing; content token match: a, accepted, actions, add, allows, and, approved, by

```text
## Existing Useful Skills

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Project Control Gateway Skill | Route plan, task, documentation and evolution work through the controlled CLI gateway instead of manual state edits. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Inspect state through CLI, choose allowed commands, run validation and render commands, report unsupported operations. | Manually edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**`; invent lifecycle states or commands; execute Initiative or Epic directly. |
| Clarification Gate Skill | Teach Codex and subagents when to inspect first, proceed with safe assumptions, or stop for Human Owner blocker questions. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Classify blockers, group owner questions, identify safe defaults, preserve task and approval boundaries. | Use questions to avoid normal inspection; ask for approval after every small step; self-approve accepted, approved, active or done states. |
| Documentation Navigation Skill | Route Codex and subagents to the minimal correct documentation and project-control read set before planning, editing, reviewing or executing AI_Development_System work.

[...truncated by contextctl...]
```

### 3. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Self-Hosted Command Boundary
Lines: `64-118`
Score: `119`
Content hash: `d6bfbf03256d4d5a7f005184d36c94434a45640595c0d654fc463065a1428adf`
Chunk hash: `749381be335ac66aa70d957f55a95f190d998afd70c4347643a6c88c059f6587`
Reasons: heading token match: command; metadata token match: ai-system, command, project-control; content token match: a, ai-system, aictl, and, approved, are, audit, by

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

### 4. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 14. Context Budget Rules > Context Pack Boundary
Lines: `797-833`
Score: `104`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `24706f89c068bb280d5630a712f0d9b260c02079a14823cc0a350875c71ba831`
Reasons: metadata token match: ai-system, project-control; content token match: a, add, and, audit, by, change, documentation, explicitly

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
Heading: Project Control Command Catalog > Scope
Lines: `21-63`
Score: `96`
Content hash: `d6bfbf03256d4d5a7f005184d36c94434a45640595c0d654fc463065a1428adf`
Chunk hash: `d914c61786e4b852b59e3a000d5c0b85638a7e8731366116abd8c8b8e9591815`
Reasons: heading token match: command; metadata token match: ai-system, command, project-control; content token match: a, actions, add, aictl, and, approved, change, command

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

### 6. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 17. Relationship To taskctl.py And codexctl.py
Lines: `874-906`
Score: `95`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `6cf68be892579b77502246852781af90dc2942f367d5af5b0a3c4a4ee727323f`
Reasons: heading token match: and, py; metadata token match: ai-system, and, project-control, py; content token match: a, and, audit, by, can, existing, for, generated

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

### 7. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 12. Prompt Package Template
Lines: `580-670`
Score: `94`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `4b3949b963506d03a8ca61d2f28eb70f0cc2ca715a4c20495bab284ca4d8fcb0`
Reasons: metadata token match: ai-system, project-control; content token match: action, and, by, change, checks, command, commands, do

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
Heading: 13. Done And Archived Immutability Tests > 13.1 Done Task Mutation > Command
Lines: `1113-1133`
Score: `83`
Content hash: `61710bd7deeed5b710aa500acaf478c77f7ad43ffcd3943c0245da65015ff2c9`
Chunk hash: `693e8700b03322e1bb4be11a59bb811e48b5cc92275c4712bfd152ad57902cb3`
Reasons: heading token match: and, command, done, task, tests; metadata token match: ai-system, and, command, done, project-control, task, tests; content token match: approved, command, create, done, fail, id, py, scripts

```text
### Command

```bash id="ybpx2n"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init
python scripts/planctl.py --root "$ROOT" initiative create --title "Project Control"
python scripts/planctl.py --root "$ROOT" epic create --initiative INIT-001 --title "Task Control"

python scripts/taskctl.py --root "$ROOT" init

python scripts/taskctl.py --root "$ROOT" task create \
  --epic EPIC-001 \
  --title "Done Task Test" \
  --status in_review

python scripts/taskctl.py --root "$ROOT" task approve TASK-001 --notes "Approved"
python scripts/taskctl.py --root "$ROOT" task transition TASK-001 --to done
python scripts/taskctl.py --root "$ROOT" task update-summary TASK-001 --text "Should fail"
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
````

Acceptance Criteria:
- Commit action is disabled unless policy explicitly allows local commit.
- Commit action refuses when commit readiness is not green.
- Commit action stages only approved files.
- Commit action never pushes, merges, resets, rebases, or discards changes.
- Commit result is recorded in session/audit.
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
- Verify command allowlist forbids push/merge/destructive git actions.
- Verify readiness failure blocks commit.

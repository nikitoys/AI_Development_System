# Codex Prompt Package

Generated: 2026-06-20T10:42:39Z
Source Type: task
Source ID: TASK-075
Source Status: in_review

[SYSTEM]

Active Role:
Codex Executor

Active Stage:
Task Execution

Active Document:
AI_PROJECT/generated/CODEX_CURRENT.md

Expected Result:
Task completed according to acceptance criteria

Repository Context:
This repository is an AI Development System governance control plane.
Project-control state is managed through Python CLI gateways; generated Markdown is derived output.

Source:
Source Task: TASK-075
Task Status: in_review
Title: PIPE-24 Add Owner-Approved Session Changes Policy Checkbox

Add a pipeline policy checkbox that lets the Human Owner approve all required Changes for the selected session queue as part of the pipeline run.

Add a safe owner-approved policy mode for approving required Evolution Changes across the selected pipeline session. This is not autonomous pipeline self-approval: the Human Owner must explicitly select the policy checkbox, confirm the session, and provide an approval note. The pipeline may then approve only the Changes required by that selected session queue.

Scope:
- Add a new safe policy field distinct from evolution.approve_linked_change, for example evolution.owner_approve_required_changes_for_session.
- Do not reuse approve_linked_change if it represents autonomous policy self-approval.
- Require explicit Human Owner confirmation when this checkbox is enabled.
- Require an approval note/reason when this checkbox is enabled.
- Store owner approval intent in the pipeline session snapshot.
- Approve only Changes linked to tasks selected by the current pipeline session queue.
- If Auto-create missing Changes is also enabled, allow pipeline to create missing Changes and approve those newly created Changes in the same owner-confirmed session.
- If a selected task has an existing ready/proposed linked Change, allow the session approval policy to approve it.
- Do not approve Changes outside the selected session queue.
- Do not accept Changes automatically.
- Do not approve Changes if the owner approval checkbox was not explicitly enabled.
- Add Web Control Center checkbox: Owner-approve required Changes for this session.
- Add approval note field to Pipeline session create form when checkbox is enabled.
- Add Policy Preview rows for Owner Session Change Approval and Approval Note Required.
- Add CLI support for equivalent flags, for example --owner-approve-required-changes and --approval-note.
- Update pipeline audit to record approved Change ids, linked task refs, actor, approval note, and session id.
- After required Changes are approved, pipeline should continue the same session if resume/waiting behavior is available.
- Add tests for approving multiple Changes in one owner-confirmed pipeline run.

Out of Scope:
- Do not allow fully autonomous approval without Human Owner confirmation.
- Do not make evolution.approve_linked_change valid if it means unsafe auto-approval.
- Do not accept Evolution Changes automatically.
- Do not approve unrelated Changes outside the selected session queue.
- Do not bypass Codex execution, token, report, machine review, Codex review, task close, or commit gates.
- Do not push, merge, reset, rebase, clean, restore, or discard git changes.
- Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.

Allowed Files:
- ai_project_ctl/pipeline/policy.py
- ai_project_ctl/pipeline/runner.py
- ai_project_ctl/pipeline/session.py
- ai_project_ctl/pipeline/state.py
- ai_project_ctl/pipeline/batch.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/registry.py
- ai_project_ctl/core/workflows.py
- scripts/aictl.py
- scripts/evolutionctl.py if existing approve command integration is needed
- tests/test_pipeline_runner.py
- tests/test_pipeline_batch.py
- tests/test_web_control_center.py
- tests/test_aictl.py
- tests/test_registry.py
- AI_PROJECT/state/evolution.json via governed CLI/service only
- AI_PROJECT/events/evolution-events.jsonl via governed CLI/service only
- AI_PROJECT/state/pipeline_sessions.json via governed CLI/service only
- AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/EVOLUTION_STATUS.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_AUDIT.md via governed CLI/service only

Implementation Instructions:
- Inspect current files before editing.
- Stay within allowed files.
- Preserve existing conventions.
- Prefer minimal, commit-ready changes.
- Do not perform unrelated refactors.
- Do not edit AI_PROJECT/state/**, AI_PROJECT/events/** or AI_PROJECT/generated/** manually.

Retrieved Context:
- Context Pack path: `AI_PROJECT/generated/CONTEXT_PACK.md`
- Context Pack SHA-256: `422ef58124ee5b2f15321904e12a90c0ea02211ba64d9d316c1d7f87e40d900e`
- Context mode: `task`
- Context task ID: `TASK-075`
- Docs revision: `27`
- Tasks revision: `611`

Retrieved Context Rules:
- Retrieved context is read-only.
- Retrieved context does not expand Allowed Files.
- Retrieved context does not expand Scope or override Out of Scope.
- Retrieved context does not replace Acceptance Criteria.
- If retrieved context conflicts with the source Task, source documents, or Human Owner instructions, report the conflict.

Retrieved Context Source Metadata:
- `ai-system/skills/README.md` lines 80-92; heading: Skills Layer Roadmap > Recommended Skills To Create; content: `dbf637225bec`; chunk: `eef80c572381`
- `ai-system/skills/README.md` lines 34-43; heading: Skills Layer Roadmap > Existing Useful Skills; content: `dbf637225bec`; chunk: `758bde12e28c`
- `ai-system/project-control/04-command-catalog.md` lines 65-119; heading: Project Control Command Catalog > Self-Hosted Command Boundary; content: `f824429b0a39`; chunk: `5b78d4503548`
- `ai-system/project-control/04-command-catalog.md` lines 2294-2321; heading: 18. Additional Command Domains > Pipeline Commands; content: `f824429b0a39`; chunk: `efe882b18c98`
- `ai-system/project-control/03-state-model.md` lines 104-125; heading: Project Control State Model > Context Control State; content: `9e818e514763`; chunk: `0cd80bdf0d55`
- `ai-system/project-control/04-command-catalog.md` lines 21-64; heading: Project Control Command Catalog > Scope; content: `f824429b0a39`; chunk: `9c998142f16f`
- `ai-system/project-control/06-prompt-package-spec.md` lines 797-833; heading: 14. Context Budget Rules > Context Pack Boundary; content: `3444e8d40e40`; chunk: `24706f89c068`
- `ai-system/project-control/06-prompt-package-spec.md` lines 874-906; heading: 17. Relationship To taskctl.py And codexctl.py; content: `3444e8d40e40`; chunk: `6cf68be89257`

Retrieved Context Pack Content:

````text
<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-075 PIPE-24 Add Owner-Approved Session Changes Policy Checkbox Add a pipeline policy checkbox that lets the Human Owner approve all required Changes for the selected session queue as part of the pipeline run. Add a safe owner-approved policy mode for approving required Evolution Changes across the selected pipeline session. This is not autonomous pipeline self-approval: the Human Owner must explicitly select the policy checkbox, confirm the session, and provide an approval note. The pipeline may then approve only the Changes required by that selected session queue. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add a new safe policy field distinct from evolution.approve_linked_change, for example evolution.owner_approve_required_changes_for_session. Do not reuse approve_linked_change if it represents autonomous policy self-approval. Require explicit Human Owner confirmation when this checkbox is enabled. Require an approval note/reason when this checkbox is enabled. Store owner approval intent in the pipeline session snapshot. Approve only Changes linked to tasks selected by the current pipeline session queue. If Auto-create missing Changes is also enabled, allow pipeline to create missing Changes and approve those newly created Changes in the same owner-confirmed session. If a selected task has an existing ready/proposed linked Change, allow the session approval policy to approve it. Do not approve Changes outside the selected session queue. Do not accept Changes automatically. Do not approve Changes if the owner approval checkbox was not explicitly enabled. Add Web Control Center checkbox: Owner-approve required Changes for this session. Add approval note field to Pipeline session create form when checkbox is enabled. Add Policy Preview rows for Owner Session Change Approval and Approval Note Required. Add CLI support for equivalent flags, for example --owner-approve-required-changes and --approval-note. Update pipeline audit to record approved Change ids, linked task refs, actor, approval note, and session id. After required Changes are approved, pipeline should continue the same session if resume/waiting behavior is available. Add tests for approving multiple Changes in one owner-confirmed pipeline run. Do not allow fully autonomous approval without Human Owner confirmation. Do not make evolution.approve_linked_change valid if it means unsafe auto-approval. Do not accept Evolution Changes automatically. Do not approve unrelated Changes outside the selected session queue. Do not bypass Codex execution, token, report, machine review, Codex review, task close, or commit gates. Do not push, merge, reset, rebase, clean, restore, or discard git changes. Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**. ai_project_ctl/pipeline/policy.py ai_project_ctl/pipeline/runner.py ai_project_ctl/pipeline/session.py ai_project_ctl/pipeline/state.py ai_project_ctl/pipeline/batch.py ai_project_ctl/web/read_model.py ai_project_ctl/web/server.py ai_project_ctl/web/actions.py ai_project_ctl/core/registry.py ai_project_ctl/core/workflows.py scripts/aictl.py scripts/evolutionctl.py if existing approve command integration is needed tests/test_pipeline_runner.py tests/test_pipeline_batch.py tests/test_web_control_center.py tests/test_aictl.py tests/test_registry.py AI_PROJECT/state/evolution.json via governed CLI/service only AI_PROJECT/events/evolution-events.jsonl via governed CLI/service only AI_PROJECT/state/pipeline_sessions.json via governed CLI/service only AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only AI_PROJECT/generated/EVOLUTION_STATUS.md via governed CLI/service only AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only AI_PROJECT/generated/PIPELINE_AUDIT.md via governed CLI/service only Pipeline UI has an Owner-approve required Changes for this session checkbox. Checkbox requires explicit confirmation and approval note. Policy preview clearly distinguishes owner-approved session approval from unsafe automatic approval. Policy validation still rejects unsafe autonomous evolution.approve_linked_change = true. When enabled, pipeline approves only required Changes linked to tasks in the selected session queue. When combined with Auto-create missing Changes, pipeline can create and owner-approve required Changes for PIPE-17..PIPE-21 in one confirmed session flow. Approved Change ids, task refs, actor, approval note, and session id are recorded in audit. Pipeline can continue the same session after approval. No Change is accepted automatically. No unrelated Change is approved. Tests pass. Create a session for PIPE-17..PIPE-21 with both Auto-create missing Changes and Owner-approve required Changes enabled. Provide an approval note and confirm. Verify missing Changes are created where needed. Verify required Changes for the selected queue are approved. Verify no unrelated Changes are approved. Verify the same session continues after approval. Verify audit trail contains owner approval evidence.","schema_version":1,"task_id":"TASK-075"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-075`
Explicit query: `false`
Limit: `8`
Docs revision: `27`
Tasks revision: `611`

## Query

```text
TASK-075 PIPE-24 Add Owner-Approved Session Changes Policy Checkbox Add a pipeline policy checkbox that lets the Human Owner approve all required Changes for the selected session queue as part of the pipeline run. Add a safe owner-approved policy mode for approving required Evolution Changes across the selected pipeline session. This is not autonomous pipeline self-approval: the Human Owner must explicitly select the policy checkbox, confirm the session, and provide an approval note. The pipeline may then approve only the Changes required by that selected session queue. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add a new safe policy field distinct from evolution.approve_linked_change, for example evolution.owner_approve_required_changes_for_session. Do not reuse approve_linked_change if it represents autonomous policy self-approval. Require explicit Human Owner confirmation when this checkbox is enabled. Require an approval note/reason when this checkbox is enabled. Store owner approval intent in the pipeline session snapshot. Approve only Changes linked to tasks selected by the current pipeline session queue. If Auto-create missing Changes is also enabled, allow pipeline to create missing Changes and approve those newly created Changes in the same owner-confirmed session. If a selected task has an existing ready/proposed linked Change, allow the session approval policy to approve it. Do not approve Changes outside the selected session queue. Do not accept Changes automatically. Do not approve Changes if the owner approval checkbox was not explicitly enabled. Add Web Control Center checkbox: Owner-approve required Changes for this session. Add approval note field to Pipeline session create form when checkbox is enabled. Add Policy Preview rows for Owner Session Change Approval and Approval Note Required. Add CLI support for equivalent flags, for example --owner-approve-required-changes and --approval-note. Update pipeline audit to record approved Change ids, linked task refs, actor, approval note, and session id. After required Changes are approved, pipeline should continue the same session if resume/waiting behavior is available. Add tests for approving multiple Changes in one owner-confirmed pipeline run. Do not allow fully autonomous approval without Human Owner confirmation. Do not make evolution.approve_linked_change valid if it means unsafe auto-approval. Do not accept Evolution Changes automatically. Do not approve unrelated Changes outside the selected session queue. Do not bypass Codex execution, token, report, machine review, Codex review, task close, or commit gates. Do not push, merge, reset, rebase, clean, restore, or discard git changes. Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**. ai_project_ctl/pipeline/policy.py ai_project_ctl/pipeline/runner.py ai_project_ctl/pipeline/session.py ai_project_ctl/pipeline/state.py ai_project_ctl/pipeline/batch.py ai_project_ctl/web/read_model.py ai_project_ctl/web/server.py ai_project_ctl/web/actions.py ai_project_ctl/core/registry.py ai_project_ctl/core/workflows.py scripts/aictl.py scripts/evolutionctl.py if existing approve command integration is needed tests/test_pipeline_runner.py tests/test_pipeline_batch.py tests/test_web_control_center.py tests/test_aictl.py tests/test_registry.py AI_PROJECT/state/evolution.json via governed CLI/service only AI_PROJECT/events/evolution-events.jsonl via governed CLI/service only AI_PROJECT/state/pipeline_sessions.json via governed CLI/service only AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only AI_PROJECT/generated/EVOLUTION_STATUS.md via governed CLI/service only AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only AI_PROJECT/generated/PIPELINE_AUDIT.md via governed CLI/service only Pipeline UI has an Owner-approve required Changes for this session checkbox. Checkbox requires explicit confirmation and approval note. Policy preview clearly distinguishes owner-approved session approval from unsafe automatic approval. Policy validation still rejects unsafe autonomous evolution.approve_linked_change = true. When enabled, pipeline approves only required Changes linked to tasks in the selected session queue. When combined with Auto-create missing Changes, pipeline can create and owner-approve required Changes for PIPE-17..PIPE-21 in one confirmed session flow. Approved Change ids, task refs, actor, approval note, and session id are recorded in audit. Pipeline can continue the same session after approval. No Change is accepted automatically. No unrelated Change is approved. Tests pass. Create a session for PIPE-17..PIPE-21 with both Auto-create missing Changes and Owner-approve required Changes enabled. Provide an approval note and confirm. Verify missing Changes are created where needed. Verify required Changes for the selected queue are approved. Verify no unrelated Changes are approved. Verify the same session continues after approval. Verify audit trail contains owner approval evidence.
```

## Task Boundary Snapshot

Task: `TASK-075` - PIPE-24 Add Owner-Approved Session Changes Policy Checkbox
Status: `in_review`

Scope:
- Add a new safe policy field distinct from evolution.approve_linked_change, for example evolution.owner_approve_required_changes_for_session.
- Do not reuse approve_linked_change if it represents autonomous policy self-approval.
- Require explicit Human Owner confirmation when this checkbox is enabled.
- Require an approval note/reason when this checkbox is enabled.
- Store owner approval intent in the pipeline session snapshot.
- Approve only Changes linked to tasks selected by the current pipeline session queue.
- If Auto-create missing Changes is also enabled, allow pipeline to create missing Changes and approve those newly created Changes in the same owner-confirmed session.
- If a selected task has an existing ready/proposed linked Change, allow the session approval policy to approve it.
- Do not approve Changes outside the selected session queue.
- Do not accept Changes automatically.
- Do not approve Changes if the owner approval checkbox was not explicitly enabled.
- Add Web Control Center checkbox: Owner-approve required Changes for this session.
- Add approval note field to Pipeline session create form when checkbox is enabled.
- Add Policy Preview rows for Owner Session Change Approval and Approval Note Required.
- Add CLI support for equivalent flags, for example --owner-approve-required-changes and --approval-note.
- Update pipeline audit to record approved Change ids, linked task refs, actor, approval note, and session id.
- After required Changes are approved, pipeline should continue the same session if resume/waiting behavior is available.
- Add tests for approving multiple Changes in one owner-confirmed pipeline run.

Allowed Files:
- ai_project_ctl/pipeline/policy.py
- ai_project_ctl/pipeline/runner.py
- ai_project_ctl/pipeline/session.py
- ai_project_ctl/pipeline/state.py
- ai_project_ctl/pipeline/batch.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/registry.py
- ai_project_ctl/core/workflows.py
- scripts/aictl.py
- scripts/evolutionctl.py if existing approve command integration is needed
- tests/test_pipeline_runner.py
- tests/test_pipeline_batch.py
- tests/test_web_control_center.py
- tests/test_aictl.py
- tests/test_registry.py
- AI_PROJECT/state/evolution.json via governed CLI/service only
- AI_PROJECT/events/evolution-events.jsonl via governed CLI/service only
- AI_PROJECT/state/pipeline_sessions.json via governed CLI/service only
- AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/EVOLUTION_STATUS.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_AUDIT.md via governed CLI/service only

Acceptance Criteria:
- Pipeline UI has an Owner-approve required Changes for this session checkbox.
- Checkbox requires explicit confirmation and approval note.
- Policy preview clearly distinguishes owner-approved session approval from unsafe automatic approval.
- Policy validation still rejects unsafe autonomous evolution.approve_linked_change = true.
- When enabled, pipeline approves only required Changes linked to tasks in the selected session queue.
- When combined with Auto-create missing Changes, pipeline can create and owner-approve required Changes for PIPE-17..PIPE-21 in one confirmed session flow.
- Approved Change ids, task refs, actor, approval note, and session id are recorded in audit.
- Pipeline can continue the same session after approval.
- No Change is accepted automatically.
- No unrelated Change is approved.
- Tests pass.

## Index Summary

Indexed source documents: `10`
Indexed chunks: `891`
Excluded registered sources: `135`
Selected chunks: `8`

Default exclusion policy: generated, inactive, archived, deprecated, template, and example documents are excluded unless explicitly allowed.

## Selected Sources

| Score | Source | Heading | Lines | Content hash | Chunk hash | Reasons |
| ---: | --- | --- | --- | --- | --- | --- |
| 265 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | heading token match: create, to; metadata token match: create, md, to; content token match: a, accept, acceptance, accepted, actions, and, approval, approved |
| 258 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | heading token match: existing; metadata token match: existing, md; content token match: a, acceptance, accepted, actions, add, after, ai_project, allow |
| 213 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Self-Hosted Command Boundary | 65-119 | `f824429b0a39` | `5b78d4503548` | heading token match: command, control; metadata token match: command, control, md; content token match: a, acceptance, ai_project, aictl, all, and, approved, are |
| 208 | `ai-system/project-control/04-command-catalog.md` | 18. Additional Command Domains > Pipeline Commands | 2294-2321 | `f824429b0a39` | `efe882b18c98` | heading token match: command, pipeline; metadata token match: command, control, md, pipeline; content token match: acceptance, ai_project, ai_project_ctl, aictl, and, approval, are, audit |
| 177 | `ai-system/project-control/03-state-model.md` | Project Control State Model > Context Control State | 104-125 | `9e818e514763` | `0cd80bdf0d55` | heading token match: control, state; metadata token match: control, md, state; content token match: a, acceptance, ai_project, and, are, both, by, control |
| 161 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Scope | 21-64 | `f824429b0a39` | `9c998142f16f` | heading token match: command, control; metadata token match: command, control, md; content token match: a, actions, add, ai_project_ctl, aictl, and, approved, as |
| 156 | `ai-system/project-control/06-prompt-package-spec.md` | 14. Context Budget Rules > Context Pack Boundary | 797-833 | `3444e8d40e40` | `24706f89c068` | metadata token match: control, md; content token match: a, acceptance, add, and, audit, by, change, clearly |
| 148 | `ai-system/project-control/06-prompt-package-spec.md` | 17. Relationship To taskctl.py And codexctl.py | 874-906 | `3444e8d40e40` | `6cf68be89257` | heading token match: and, py, to; metadata token match: and, control, md, py, to; content token match: a, an, and, audit, by, bypass, can, codex |

## Selected Context

### 1. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Recommended Skills To Create
Lines: `80-92`
Score: `265`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: heading token match: create, to; metadata token match: create, md, to; content token match: a, accept, acceptance, accepted, actions, and, approval, approved

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
Score: `258`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: heading token match: existing; metadata token match: existing, md; content token match: a, acceptance, accepted, actions, add, after, ai_project, allow

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
Lines: `65-119`
Score: `213`
Content hash: `f824429b0a394aec9bfe9157302c1059a181374f040adbfb8136d2673f7fb1b6`
Chunk hash: `5b78d45035483b51a58d0a7bed1cf1402fe3b2e6bc9a7ffcda911c0d12fcb6bc`
Reasons: heading token match: command, control; metadata token match: command, control, md; content token match: a, acceptance, ai_project, aictl, all, and, approved, are

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

### 4. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: 18. Additional Command Domains > Pipeline Commands
Lines: `2294-2321`
Score: `208`
Content hash: `f824429b0a394aec9bfe9157302c1059a181374f040adbfb8136d2673f7fb1b6`
Chunk hash: `efe882b18c987d13ed38a60c38d0a9ba2dccd1c95061f72f79901f6f007ad46a`
Reasons: heading token match: command, pipeline; metadata token match: command, control, md, pipeline; content token match: acceptance, ai_project, ai_project_ctl, aictl, and, approval, are, audit

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

### 5. `ai-system/project-control/03-state-model.md`

Title: Project Control State Model
Status: `active`  Type: `reference`
Heading: Project Control State Model > Context Control State
Lines: `104-125`
Score: `177`
Content hash: `9e818e514763e69aa2f56bb5d9ca080d47b7330db3aa016982c5d3ee0bc2be81`
Chunk hash: `0cd80bdf0d55e5284fa6355477f50005896398136bf33b7e1a181718f309f8b4`
Reasons: heading token match: control, state; metadata token match: control, md, state; content token match: a, acceptance, ai_project, and, are, both, by, control

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

### 6. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Scope
Lines: `21-64`
Score: `161`
Content hash: `f824429b0a394aec9bfe9157302c1059a181374f040adbfb8136d2673f7fb1b6`
Chunk hash: `9c998142f16f19b020151b13a6a80db5dfffa618771f91cbdd39a8467a7ee582`
Reasons: heading token match: command, control; metadata token match: command, control, md; content token match: a, actions, add, ai_project_ctl, aictl, and, approved, as

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

### 7. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 14. Context Budget Rules > Context Pack Boundary
Lines: `797-833`
Score: `156`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `24706f89c068bb280d5630a712f0d9b260c02079a14823cc0a350875c71ba831`
Reasons: metadata token match: control, md; content token match: a, acceptance, add, and, audit, by, change, clearly

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

### 8. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 17. Relationship To taskctl.py And codexctl.py
Lines: `874-906`
Score: `148`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `6cf68be892579b77502246852781af90dc2942f367d5af5b0a3c4a4ee727323f`
Reasons: heading token match: and, py, to; metadata token match: and, control, md, py, to; content token match: a, an, and, audit, by, bypass, can, codex

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
````

Acceptance Criteria:
- Pipeline UI has an Owner-approve required Changes for this session checkbox.
- Checkbox requires explicit confirmation and approval note.
- Policy preview clearly distinguishes owner-approved session approval from unsafe automatic approval.
- Policy validation still rejects unsafe autonomous evolution.approve_linked_change = true.
- When enabled, pipeline approves only required Changes linked to tasks in the selected session queue.
- When combined with Auto-create missing Changes, pipeline can create and owner-approve required Changes for PIPE-17..PIPE-21 in one confirmed session flow.
- Approved Change ids, task refs, actor, approval note, and session id are recorded in audit.
- Pipeline can continue the same session after approval.
- No Change is accepted automatically.
- No unrelated Change is approved.
- Tests pass.

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
- Create a session for PIPE-17..PIPE-21 with both Auto-create missing Changes and Owner-approve required Changes enabled.
- Provide an approval note and confirm.
- Verify missing Changes are created where needed.
- Verify required Changes for the selected queue are approved.
- Verify no unrelated Changes are approved.
- Verify the same session continues after approval.
- Verify audit trail contains owner approval evidence.

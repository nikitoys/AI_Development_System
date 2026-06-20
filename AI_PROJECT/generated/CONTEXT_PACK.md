<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-078 PIPE-27 Add Persistent Pipeline Session Detail Page Add a persistent per-session Pipeline page with real-time steps, expandable logs, session actions, artifacts, audit events, and historical availability. Create a dedicated Web Control Center page for each pipeline session, for example /pipeline/sessions/PSESS-012. The page must let the Human Owner watch a running session in real time, inspect all steps and logs, execute safe session actions, and reopen the page later as a permanent execution record. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add a persistent route for individual pipeline sessions, for example /pipeline/sessions/<SESSION_ID>. Add links from the main Pipeline sessions table to each session detail page. Keep session detail pages available after session completion, blocking, failure, stop, or archive. Add a top session header with session id, status, policy, current task, current step, stop reason, started/updated/finished timestamps, elapsed time, and auto-refresh status. Add a Status Overview section with a compact progress indicator for the full pipeline flow. Add a Current Live Step section for running sessions. Auto-refresh the session page every 1-2 seconds while the session is running. Stop auto-refresh automatically when the session reaches a terminal state. Add a Steps section that lists all pipeline steps in order. Each step must be expandable/collapsible. Expanded step view must show status, task id/ref, started_at, finished_at, elapsed time, stop reason, gate outcomes, linked artifacts, and logs. Step logs must include bounded stdout/stderr snippets when available. Show pending steps as visible placeholders, not hidden missing data. Add an Actions section with buttons for safe session actions. Actions section must include Refresh Session, Run Next, Run Until Blocker, Stop Session, and Resume Session when applicable. Actions section must show owner approval actions when applicable, including approve required changes, approve auto-close, and close reviewed task. Dangerous or restricted actions must be separated visually and require explicit confirmation. Do not expose push, merge, reset, restore, clean, rebase, discard, or destructive git actions. Add an Artifacts section showing linked task ids, change ids, report ids, review ids, commit ids, Context Pack path, Codex Prompt path, and generated files. Add a Queue Snapshot section showing selected task, queue counts, skipped tasks, and skip reasons such as status_not_executable. Add an Audit Events section with latest pipeline events related to the session. Add a Files Changed During Session section when changed file data is available. Add a Problems / Blockers section that clearly displays current blocker, previous blockers, and known risks. Add Raw Debug collapsible sections for session JSON and latest gate details. Do not render full CODEX_PROMPT.md content on the page. Do not store or render unbounded logs. Use bounded snippets, hashes, or safe log references for Codex adapter stdout/stderr. Use simple polling for MVP; do not require WebSockets or SSE. Add tests for session detail route rendering. Add tests for links from main Pipeline page to session detail pages. Add tests for running-session auto-refresh markup. Add tests for completed historical session rendering. Add tests for expandable steps and bounded log display. Add tests for action buttons and confirmation requirements. Document the session detail page in the owner quickstart and pipeline runner docs. Do not add background autonomous execution. Do not bypass pipeline gates. Do not change task lifecycle rules. Do not change queue planner semantics except for display/read-model formatting needed by this page. Do not approve or accept Evolution Changes automatically. Do not auto-close tasks without existing pipeline close gates and owner note. Do not push or merge. Do not expose full prompt text. Do not store full stdout/stderr logs in protected state. Do not add external frontend dependencies. Do not require WebSockets or SSE in the MVP. Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**. ai_project_ctl/web/server.py ai_project_ctl/web/read_model.py ai_project_ctl/web/actions.py ai_project_ctl/pipeline/state.py ai_project_ctl/pipeline/session.py ai_project_ctl/pipeline/audit.py ai_project_ctl/pipeline/codex_adapter.py ai_project_ctl/core/registry.py scripts/aictl.py tests/test_web_control_center.py tests/test_pipeline_runner.py tests/test_aictl.py ai-system/project-control/pipeline-runner.md ai-system/project-control/10-owner-quickstart.md AI_PROJECT/state/pipeline_sessions.json via governed CLI/service only AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only AI_PROJECT/generated/PIPELINE_AUDIT.md via governed CLI/service only Each pipeline session has a stable URL such as /pipeline/sessions/PSESS-012. The main Pipeline page links each session id to its detail page. The session detail page remains available after the session completes, blocks, fails, stops, or is archived. Running sessions auto-refresh without manual page reload. Auto-refresh stops after a terminal session state. The page has a Steps section with all pipeline steps in execution order. Each step can be expanded to inspect status, gates, details, and bounded logs. The page has an Actions section with session-level buttons. Action buttons require confirmation for mutating operations. The page separates safe actions, owner approval actions, and restricted/dangerous actions. The page shows session summary, live current step, artifacts, queue snapshot, audit events, files changed, blockers, and raw debug sections. Codex adapter stdout/stderr are shown only as bounded snippets or safe references. Full CODEX_PROMPT.md content is never rendered on the session page. Unbounded stdout/stderr logs are never stored or rendered. Historical completed sessions can be opened and inspected. Tests and project-control validations pass. Start a running pipeline session and open /pipeline/sessions/<SESSION_ID>. Verify the page updates while the session is running. Verify the Steps section displays all known steps and pending placeholders. Expand each step and verify logs/gates/details are readable. Verify Actions buttons appear only when applicable to the session state. Verify mutating Actions require confirmation. Verify old completed and blocked PSESS records remain viewable. Verify no full CODEX_PROMPT.md content appears in page HTML, state, events, or generated output. Verify the main Pipeline dashboard links to the session detail page. Run web/control-center tests and project-control validation commands.","schema_version":1,"task_id":"TASK-078"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-078`
Explicit query: `false`
Limit: `8`
Docs revision: `28`
Tasks revision: `664`

## Query

```text
TASK-078 PIPE-27 Add Persistent Pipeline Session Detail Page Add a persistent per-session Pipeline page with real-time steps, expandable logs, session actions, artifacts, audit events, and historical availability. Create a dedicated Web Control Center page for each pipeline session, for example /pipeline/sessions/PSESS-012. The page must let the Human Owner watch a running session in real time, inspect all steps and logs, execute safe session actions, and reopen the page later as a permanent execution record. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add a persistent route for individual pipeline sessions, for example /pipeline/sessions/<SESSION_ID>. Add links from the main Pipeline sessions table to each session detail page. Keep session detail pages available after session completion, blocking, failure, stop, or archive. Add a top session header with session id, status, policy, current task, current step, stop reason, started/updated/finished timestamps, elapsed time, and auto-refresh status. Add a Status Overview section with a compact progress indicator for the full pipeline flow. Add a Current Live Step section for running sessions. Auto-refresh the session page every 1-2 seconds while the session is running. Stop auto-refresh automatically when the session reaches a terminal state. Add a Steps section that lists all pipeline steps in order. Each step must be expandable/collapsible. Expanded step view must show status, task id/ref, started_at, finished_at, elapsed time, stop reason, gate outcomes, linked artifacts, and logs. Step logs must include bounded stdout/stderr snippets when available. Show pending steps as visible placeholders, not hidden missing data. Add an Actions section with buttons for safe session actions. Actions section must include Refresh Session, Run Next, Run Until Blocker, Stop Session, and Resume Session when applicable. Actions section must show owner approval actions when applicable, including approve required changes, approve auto-close, and close reviewed task. Dangerous or restricted actions must be separated visually and require explicit confirmation. Do not expose push, merge, reset, restore, clean, rebase, discard, or destructive git actions. Add an Artifacts section showing linked task ids, change ids, report ids, review ids, commit ids, Context Pack path, Codex Prompt path, and generated files. Add a Queue Snapshot section showing selected task, queue counts, skipped tasks, and skip reasons such as status_not_executable. Add an Audit Events section with latest pipeline events related to the session. Add a Files Changed During Session section when changed file data is available. Add a Problems / Blockers section that clearly displays current blocker, previous blockers, and known risks. Add Raw Debug collapsible sections for session JSON and latest gate details. Do not render full CODEX_PROMPT.md content on the page. Do not store or render unbounded logs. Use bounded snippets, hashes, or safe log references for Codex adapter stdout/stderr. Use simple polling for MVP; do not require WebSockets or SSE. Add tests for session detail route rendering. Add tests for links from main Pipeline page to session detail pages. Add tests for running-session auto-refresh markup. Add tests for completed historical session rendering. Add tests for expandable steps and bounded log display. Add tests for action buttons and confirmation requirements. Document the session detail page in the owner quickstart and pipeline runner docs. Do not add background autonomous execution. Do not bypass pipeline gates. Do not change task lifecycle rules. Do not change queue planner semantics except for display/read-model formatting needed by this page. Do not approve or accept Evolution Changes automatically. Do not auto-close tasks without existing pipeline close gates and owner note. Do not push or merge. Do not expose full prompt text. Do not store full stdout/stderr logs in protected state. Do not add external frontend dependencies. Do not require WebSockets or SSE in the MVP. Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**. ai_project_ctl/web/server.py ai_project_ctl/web/read_model.py ai_project_ctl/web/actions.py ai_project_ctl/pipeline/state.py ai_project_ctl/pipeline/session.py ai_project_ctl/pipeline/audit.py ai_project_ctl/pipeline/codex_adapter.py ai_project_ctl/core/registry.py scripts/aictl.py tests/test_web_control_center.py tests/test_pipeline_runner.py tests/test_aictl.py ai-system/project-control/pipeline-runner.md ai-system/project-control/10-owner-quickstart.md AI_PROJECT/state/pipeline_sessions.json via governed CLI/service only AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only AI_PROJECT/generated/PIPELINE_AUDIT.md via governed CLI/service only Each pipeline session has a stable URL such as /pipeline/sessions/PSESS-012. The main Pipeline page links each session id to its detail page. The session detail page remains available after the session completes, blocks, fails, stops, or is archived. Running sessions auto-refresh without manual page reload. Auto-refresh stops after a terminal session state. The page has a Steps section with all pipeline steps in execution order. Each step can be expanded to inspect status, gates, details, and bounded logs. The page has an Actions section with session-level buttons. Action buttons require confirmation for mutating operations. The page separates safe actions, owner approval actions, and restricted/dangerous actions. The page shows session summary, live current step, artifacts, queue snapshot, audit events, files changed, blockers, and raw debug sections. Codex adapter stdout/stderr are shown only as bounded snippets or safe references. Full CODEX_PROMPT.md content is never rendered on the session page. Unbounded stdout/stderr logs are never stored or rendered. Historical completed sessions can be opened and inspected. Tests and project-control validations pass. Start a running pipeline session and open /pipeline/sessions/<SESSION_ID>. Verify the page updates while the session is running. Verify the Steps section displays all known steps and pending placeholders. Expand each step and verify logs/gates/details are readable. Verify Actions buttons appear only when applicable to the session state. Verify mutating Actions require confirmation. Verify old completed and blocked PSESS records remain viewable. Verify no full CODEX_PROMPT.md content appears in page HTML, state, events, or generated output. Verify the main Pipeline dashboard links to the session detail page. Run web/control-center tests and project-control validation commands.
```

## Task Boundary Snapshot

Task: `TASK-078` - PIPE-27 Add Persistent Pipeline Session Detail Page
Status: `in_progress`

Scope:
- Add a persistent route for individual pipeline sessions, for example /pipeline/sessions/<SESSION_ID>.
- Add links from the main Pipeline sessions table to each session detail page.
- Keep session detail pages available after session completion, blocking, failure, stop, or archive.
- Add a top session header with session id, status, policy, current task, current step, stop reason, started/updated/finished timestamps, elapsed time, and auto-refresh status.
- Add a Status Overview section with a compact progress indicator for the full pipeline flow.
- Add a Current Live Step section for running sessions.
- Auto-refresh the session page every 1-2 seconds while the session is running.
- Stop auto-refresh automatically when the session reaches a terminal state.
- Add a Steps section that lists all pipeline steps in order.
- Each step must be expandable/collapsible.
- Expanded step view must show status, task id/ref, started_at, finished_at, elapsed time, stop reason, gate outcomes, linked artifacts, and logs.
- Step logs must include bounded stdout/stderr snippets when available.
- Show pending steps as visible placeholders, not hidden missing data.
- Add an Actions section with buttons for safe session actions.
- Actions section must include Refresh Session, Run Next, Run Until Blocker, Stop Session, and Resume Session when applicable.
- Actions section must show owner approval actions when applicable, including approve required changes, approve auto-close, and close reviewed task.
- Dangerous or restricted actions must be separated visually and require explicit confirmation.
- Do not expose push, merge, reset, restore, clean, rebase, discard, or destructive git actions.
- Add an Artifacts section showing linked task ids, change ids, report ids, review ids, commit ids, Context Pack path, Codex Prompt path, and generated files.
- Add a Queue Snapshot section showing selected task, queue counts, skipped tasks, and skip reasons such as status_not_executable.
- Add an Audit Events section with latest pipeline events related to the session.
- Add a Files Changed During Session section when changed file data is available.
- Add a Problems / Blockers section that clearly displays current blocker, previous blockers, and known risks.
- Add Raw Debug collapsible sections for session JSON and latest gate details.
- Do not render full CODEX_PROMPT.md content on the page.
- Do not store or render unbounded logs.
- Use bounded snippets, hashes, or safe log references for Codex adapter stdout/stderr.
- Use simple polling for MVP; do not require WebSockets or SSE.
- Add tests for session detail route rendering.
- Add tests for links from main Pipeline page to session detail pages.
- Add tests for running-session auto-refresh markup.
- Add tests for completed historical session rendering.
- Add tests for expandable steps and bounded log display.
- Add tests for action buttons and confirmation requirements.
- Document the session detail page in the owner quickstart and pipeline runner docs.

Allowed Files:
- ai_project_ctl/web/server.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/pipeline/state.py
- ai_project_ctl/pipeline/session.py
- ai_project_ctl/pipeline/audit.py
- ai_project_ctl/pipeline/codex_adapter.py
- ai_project_ctl/core/registry.py
- scripts/aictl.py
- tests/test_web_control_center.py
- tests/test_pipeline_runner.py
- tests/test_aictl.py
- ai-system/project-control/pipeline-runner.md
- ai-system/project-control/10-owner-quickstart.md
- AI_PROJECT/state/pipeline_sessions.json via governed CLI/service only
- AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_AUDIT.md via governed CLI/service only

Acceptance Criteria:
- Each pipeline session has a stable URL such as /pipeline/sessions/PSESS-012.
- The main Pipeline page links each session id to its detail page.
- The session detail page remains available after the session completes, blocks, fails, stops, or is archived.
- Running sessions auto-refresh without manual page reload.
- Auto-refresh stops after a terminal session state.
- The page has a Steps section with all pipeline steps in execution order.
- Each step can be expanded to inspect status, gates, details, and bounded logs.
- The page has an Actions section with session-level buttons.
- Action buttons require confirmation for mutating operations.
- The page separates safe actions, owner approval actions, and restricted/dangerous actions.
- The page shows session summary, live current step, artifacts, queue snapshot, audit events, files changed, blockers, and raw debug sections.
- Codex adapter stdout/stderr are shown only as bounded snippets or safe references.
- Full CODEX_PROMPT.md content is never rendered on the session page.
- Unbounded stdout/stderr logs are never stored or rendered.
- Historical completed sessions can be opened and inspected.
- Tests and project-control validations pass.

## Index Summary

Indexed source documents: `10`
Indexed chunks: `891`
Excluded registered sources: `135`
Selected chunks: `8`

Default exclusion policy: generated, inactive, archived, deprecated, template, and example documents are excluded unless explicitly allowed.

## Selected Sources

| Score | Source | Heading | Lines | Content hash | Chunk hash | Reasons |
| ---: | --- | --- | --- | --- | --- | --- |
| 289 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | heading token match: existing; metadata token match: ai-system, existing, md; content token match: a, acceptance, actions, add, after, ai_project, and, approval |
| 284 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | heading token match: create, to; metadata token match: ai-system, create, md, to; content token match: a, accept, acceptance, actions, and, approval, as, automatically |
| 268 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Self-Hosted Command Boundary | 65-119 | `f824429b0a39` | `5b78d4503548` | heading token match: control; metadata token match: ai-system, control, md, project-control; content token match: a, acceptance, ai-system, ai_project, aictl, all, and, are |
| 242 | `ai-system/project-control/04-command-catalog.md` | 18. Additional Command Domains > Pipeline Commands | 2294-2321 | `f824429b0a39` | `efe882b18c98` | heading token match: commands, pipeline; metadata token match: ai-system, commands, control, md, pipeline, project-control; content token match: acceptance, ai_project, ai_project_ctl, aictl, and, approval, are, audit |
| 224 | `ai-system/project-control/06-prompt-package-spec.md` | 14. Context Budget Rules > Context Pack Boundary | 797-833 | `3444e8d40e40` | `24706f89c068` | heading token match: context, pack, rules; metadata token match: ai-system, context, control, md, pack, project-control, prompt, rules; content token match: a, acceptance, add, and, archived, audit, bounded, by |
| 216 | `ai-system/project-control/03-state-model.md` | Project Control State Model > Context Control State | 104-125 | `9e818e514763` | `0cd80bdf0d55` | heading token match: context, control, state; metadata token match: ai-system, context, control, md, project-control, state; content token match: a, acceptance, ai_project, and, archived, are, be, by |
| 202 | `ai-system/project-control/06-prompt-package-spec.md` | 12. Prompt Package Template | 580-670 | `3444e8d40e40` | `4b3949b96350` | heading token match: prompt; metadata token match: ai-system, control, md, project-control, prompt; content token match: acceptance, action, ai_project, and, be, bounded, by, change |
| 185 | `ai-system/project-control/06-prompt-package-spec.md` | 17. Relationship To taskctl.py And codexctl.py | 874-906 | `3444e8d40e40` | `6cf68be89257` | heading token match: and, py, to; metadata token match: ai-system, and, control, md, project-control, prompt, py, to; content token match: a, an, and, audit, be, by, bypass, can |

## Selected Context

### 1. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Existing Useful Skills
Lines: `34-43`
Score: `289`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: heading token match: existing; metadata token match: ai-system, existing, md; content token match: a, acceptance, actions, add, after, ai_project, and, approval

```text
## Existing Useful Skills

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Project Control Gateway Skill | Route plan, task, documentation and evolution work through the controlled CLI gateway instead of manual state edits. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Inspect state through CLI, choose allowed commands, run validation and render commands, report unsupported operations. | Manually edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**`; invent lifecycle states or commands; execute Initiative or Epic directly. |
| Clarification Gate Skill | Teach Codex and subagents when to inspect first, proceed with safe assumptions, or stop for Human Owner blocker questions. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Classify blockers, group owner questions, identify safe defaults, preserve task and approval boundaries. | Use questions to avoid normal inspection; ask for approval after every small step; self-approve accepted, approved, active or done states. |
| Documentation Navigation Skill | Route Codex and subagents to the minimal correct documentation and project-control read set before planning, editing, reviewing or executing AI_Development_System work.

[...truncated by contextctl...]
```

### 2. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Recommended Skills To Create
Lines: `80-92`
Score: `284`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: heading token match: create, to; metadata token match: ai-system, create, md, to; content token match: a, accept, acceptance, actions, and, approval, as, automatically

```text
## Recommended Skills To Create

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Documentation Control Skill | Guide documentation registration, status changes, generated indexes and documentation validation. | `docctl.py` | P0 | Register documents, set draft/review status, render/check generated docs, explain documentation lifecycle. | Mark documents active without Human Owner approval; manually edit `docs.json`, doc events or generated doc indexes. |
| Protected Files Skill | Keep agents inside the protected-files boundary and detect unsafe project-control edits. | `check-protected-project-files.py`, `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Explain protected paths, run protected-files checks, route repairs through CLIs. | Edit protected state/events/generated files manually; use ad hoc scripts to mutate protected files; hide drift. |
| Review Gate Skill | Guide review intake before a Task can be accepted or closed. | `taskctl.py`; future review control CLI if approved | P1 | Check scope, allowed files, acceptance criteria, validation output and review status; recommend APPROVED, REWORK, REJECTED or DEFERRED. | Self-approve work; mark a Task done without the required approval path; ignore Critical or Major findings. |

[...truncated by contextctl...]
```

### 3. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Self-Hosted Command Boundary
Lines: `65-119`
Score: `268`
Content hash: `f824429b0a394aec9bfe9157302c1059a181374f040adbfb8136d2673f7fb1b6`
Chunk hash: `5b78d45035483b51a58d0a7bed1cf1402fe3b2e6bc9a7ffcda911c0d12fcb6bc`
Reasons: heading token match: control; metadata token match: ai-system, control, md, project-control; content token match: a, acceptance, ai-system, ai_project, aictl, all, and, are

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
Score: `242`
Content hash: `f824429b0a394aec9bfe9157302c1059a181374f040adbfb8136d2673f7fb1b6`
Chunk hash: `efe882b18c987d13ed38a60c38d0a9ba2dccd1c95061f72f79901f6f007ad46a`
Reasons: heading token match: commands, pipeline; metadata token match: ai-system, commands, control, md, pipeline, project-control; content token match: acceptance, ai_project, ai_project_ctl, aictl, and, approval, are, audit

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

### 5. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 14. Context Budget Rules > Context Pack Boundary
Lines: `797-833`
Score: `224`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `24706f89c068bb280d5630a712f0d9b260c02079a14823cc0a350875c71ba831`
Reasons: heading token match: context, pack, rules; metadata token match: ai-system, context, control, md, pack, project-control, prompt, rules; content token match: a, acceptance, add, and, archived, audit, bounded, by

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

### 6. `ai-system/project-control/03-state-model.md`

Title: Project Control State Model
Status: `active`  Type: `reference`
Heading: Project Control State Model > Context Control State
Lines: `104-125`
Score: `216`
Content hash: `9e818e514763e69aa2f56bb5d9ca080d47b7330db3aa016982c5d3ee0bc2be81`
Chunk hash: `0cd80bdf0d55e5284fa6355477f50005896398136bf33b7e1a181718f309f8b4`
Reasons: heading token match: context, control, state; metadata token match: ai-system, context, control, md, project-control, state; content token match: a, acceptance, ai_project, and, archived, are, be, by

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

### 7. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 12. Prompt Package Template
Lines: `580-670`
Score: `202`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `4b3949b963506d03a8ca61d2f28eb70f0cc2ca715a4c20495bab284ca4d8fcb0`
Reasons: heading token match: prompt; metadata token match: ai-system, control, md, project-control, prompt; content token match: acceptance, action, ai_project, and, be, bounded, by, change

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

### 8. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 17. Relationship To taskctl.py And codexctl.py
Lines: `874-906`
Score: `185`
Content hash: `3444e8d40e40cf20b4ec3bcdb6b1509741fe88fb0a35430a00b200bb2894c9ac`
Chunk hash: `6cf68be892579b77502246852781af90dc2942f367d5af5b0a3c4a4ee727323f`
Reasons: heading token match: and, py, to; metadata token match: ai-system, and, control, md, project-control, prompt, py, to; content token match: a, an, and, audit, be, by, bypass, can

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

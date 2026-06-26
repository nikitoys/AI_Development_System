# Project Control Usage Guide

## Status

Review

## Purpose

This guide explains how to use Project Control Gateway in daily work.

It is practical by design. Use it when you need to decide which CLI owns a change, when a Task is required, how `CODEX_PROMPT.md` fits into execution, how the local Web Control Center stays safe, or what Codex must never edit manually.

For the short owner-facing path, start with:

```text
ai-system/project-control/10-owner-quickstart.md
```

That quickstart is UI-first. This guide keeps both the Web Control Center workflow and the command-line compatibility details.

Core rule:

```text
Human Owner decides.
ChatGPT Orchestrator routes.
Codex Executor executes bounded Tasks.
Python CLIs mutate project-control state.
Generated Markdown is readable output, not source of truth.
```

## Control Boundary

Project Control Gateway separates source documents from controlled project state.

Source documents may be edited directly only when the Task allows it.

In AI_Development_System itself, root `/AI_PROJECT` is the self-hosted Project Control Layer. It stores machine-readable state, append-only audit events and generated readable outputs for this repository's own controlled evolution.

Protected project-control files must not be edited directly:

```text
AI_PROJECT/state/**
AI_PROJECT/events/**
AI_PROJECT/generated/**
```

Use the CLI that owns the domain:

```text
aictl.py       preferred facade for discovery, health checks, supported commands and web
planctl.py      Initiative, Epic, project plan
taskctl.py      executable Task, current Task, CODEX_PROMPT.md
codexctl.py     current Codex execution package and optional Context Pack inclusion
docctl.py       documentation registry, document status, docs index
evolutionctl.py AI Development System change proposals
contextctl.py   deterministic Context Packs from registered docs and Task state
```

If a requested operation has no supported command, stop and report the missing command. Do not patch protected state by hand.

Keep these `AI_PROJECT` contexts separate:

```text
/AI_PROJECT
  Self-hosted project-control layer for this repository.

/ai-system/templates/**/AI_PROJECT
  Reusable templates for external projects.

/examples/golden-project/AI_PROJECT
  Non-runtime reference example for onboarding and validation.
```

## Role Interaction

The Human Owner owns direction, approval and acceptance.

ChatGPT Orchestrator classifies the request, chooses the active role, identifies source documents and maps intent to the correct CLI.

Codex Executor works only on a bounded Task. Codex may edit allowed source files, run supported commands and report results. Codex must not approve its own work.

Python CLIs own project-control mutation. They validate input, update JSON state, append audit events and render generated Markdown.

Generated Markdown is context for humans and AI agents. It must not be treated as editable state.

Context Packs are generated retrieval context. They help focus reading, but they do not replace Task state, source documents or Human Owner decisions.

## CLI Responsibilities

## `aictl.py`

Use `aictl.py` as the preferred owner and Codex-facing facade for command discovery, common project-control commands, project health checks, generated view rendering, Context Pack builds, Codex prompt builds and the local Web Control Center.

Common commands:

```bash
python scripts/aictl.py command list
python scripts/aictl.py command describe task.transition
python scripts/aictl.py workflow list
python scripts/aictl.py workflow describe task.prepare_for_codex
python scripts/aictl.py task list --current
python scripts/aictl.py task show CTL-12
python scripts/aictl.py task create --confirm --epic EPIC-005 --title "Bounded Task Title"
python scripts/aictl.py task import --file tasks.json --preview
python scripts/aictl.py current set CTL-12
python scripts/aictl.py task transition CTL-12 --to in_review
python scripts/aictl.py context build --task CTL-12 --write
python scripts/aictl.py codex prompt build --task CTL-12 --with-context
python scripts/aictl.py workflow run task.prepare_for_codex --task CTL-12 --confirm
python scripts/aictl.py workflow run task.submit_for_review --task CTL-12 --confirm
python scripts/aictl.py project doctor
python scripts/aictl.py project render
python scripts/aictl.py web --host 127.0.0.1 --port 8765
```

Use `--json` when another tool needs machine-readable output:

```bash
python scripts/aictl.py --json command list
python scripts/aictl.py --json project doctor
```

`aictl.py` does not replace domain ownership. If a needed command is not exposed by the facade parser, use the owning legacy script and keep the same protected-file rules. For example, use `docctl.py` for document registry state, `evolutionctl.py` for Change Proposals and detailed evolution gates, and `taskctl.py` for task creation or task validation commands that are not exposed through `aictl.py`.

The command registry may describe commands that are implemented by a legacy script before they are exposed as an `aictl.py` subcommand. In that case, command discovery tells you the owner and safety metadata; execution still uses the available facade command or the listed legacy command.

## Workflow Automation

Workflow automation is exposed through `aictl.py workflow`.

Use it for multi-step owner-facing operations that already have a registered command contract:

```bash
python scripts/aictl.py workflow list
python scripts/aictl.py workflow describe task.prepare_for_codex
python scripts/aictl.py workflow describe task.refresh_execution_context
python scripts/aictl.py workflow describe task.submit_for_review
python scripts/aictl.py workflow describe task.close_reviewed
python scripts/aictl.py workflow describe evolution.create_for_task
```

Run workflows only with explicit confirmation:

```bash
python scripts/aictl.py workflow run task.prepare_for_codex --task CTL-12 --confirm
python scripts/aictl.py workflow run task.refresh_execution_context --task CTL-12 --confirm
python scripts/aictl.py workflow run task.submit_for_review --task CTL-12 --confirm
python scripts/aictl.py workflow run task.close_reviewed --task CTL-12 --notes "APPROVED by Human Owner" --confirm
python scripts/aictl.py workflow run evolution.create_for_task --task CTL-12 --confirm
```

`task.prepare_for_codex` sets current Task, validates task state and graph, moves the Task to `in_progress` when needed, builds task context, builds the Codex prompt with context and runs `project doctor`.

`task.refresh_execution_context` rebuilds the task Context Pack and Codex prompt package without changing task lifecycle.

`task.submit_for_review` runs blocking task, context, evolution and protected-file checks before moving the Task to `in_review`.

`task.close_reviewed` is an owner-facing close helper. It requires approval notes, rejects Tasks outside `in_review`, delegates approval to `taskctl.py task approve` and then transitions the Task to `done`.

`evolution.create_for_task` drafts an Evolution Change from a selected Task, adds derived affected files, risks and impact, links the Task, validates evolution state and moves the Change only to `ready`. It does not approve or accept the Change.

## `planctl.py`

Use `planctl.py` for upper-level planning:

```text
Project
Idea
Goal
Strategy
Initiative
Epic
```

Initiatives and Epics organize work. They are not executable.

Common commands:

```bash
python scripts/planctl.py init --project-name "AI Development System"
python scripts/planctl.py initiative create --title "AI Development System Evolution"
python scripts/planctl.py epic create --initiative INIT-001 --title "Documentation Rails"
python scripts/planctl.py validate
python scripts/planctl.py render
python scripts/planctl.py audit --last 20
```

Use `planctl.py render` to regenerate `AI_PROJECT/generated/CODEX_PLAN.md`.

## `taskctl.py`

Use `taskctl.py` for executable work:

```text
Task
Current Task
CODEX_TASKS.md
CODEX_CURRENT.md
CODEX_PROMPT.md
```

Only a Task is executable by Codex.

Common commands:

```bash
python scripts/taskctl.py init
python scripts/taskctl.py task create --epic EPIC-001 --title "Write Project Control Usage Guide"
python scripts/taskctl.py task transition TASK-001 --to ready
python scripts/taskctl.py current set TASK-001
python scripts/taskctl.py prompt build --write
python scripts/taskctl.py task transition TASK-001 --to in_progress
python scripts/taskctl.py task transition TASK-001 --to in_review
python scripts/taskctl.py validate
python scripts/taskctl.py render
python scripts/taskctl.py check-generated
```

Do not use `task approve` or transition to `done` unless the Human Owner or approved review process has accepted the result.

## `codexctl.py`

Use `codexctl.py` for the current Codex execution package:

```text
CODEX_PROMPT.md
CODEX_STATUS.md
current_execution.json
codex-events.jsonl
```

Common commands:

```bash
python scripts/codexctl.py status
python scripts/codexctl.py build --task TASK-001
python scripts/codexctl.py build --task TASK-001 --with-context
python scripts/codexctl.py build --task TASK-001 --context-pack AI_PROJECT/generated/CONTEXT_PACK.md
python scripts/codexctl.py clear
```

`--with-context` uses the default `AI_PROJECT/generated/CONTEXT_PACK.md`. `--context-pack` includes an explicit Context Pack after validation.

`codexctl.py` validates that the Context Pack exists, has Context Pack metadata, matches the requested Task when task-scoped, and was generated from the current docs/task revisions. It does not build or refresh Context Packs; use `contextctl.py` for that.

Retrieved context in `CODEX_PROMPT.md` is read-only. It does not expand allowed files, task scope, out-of-scope items or acceptance criteria, and conflicts must be reported.

## `docctl.py`

Use `docctl.py` for documentation lifecycle control:

```text
registered documentation
document status
documentation review records
DOCS_INDEX.md
DOCS_GAPS.md
```

Common commands:

```bash
python scripts/docctl.py init
python scripts/docctl.py scan --scope all
python scripts/docctl.py doc register --path ai-system/project-control/08-usage-guide.md --title "Project Control Usage Guide" --type guide --status planned
python scripts/docctl.py doc status ai-system/project-control/08-usage-guide.md --to draft
python scripts/docctl.py doc status ai-system/project-control/08-usage-guide.md --to review
python scripts/docctl.py doc mark-reviewed ai-system/project-control/08-usage-guide.md --note "Reviewed for project-control consistency."
python scripts/docctl.py validate
python scripts/docctl.py render
python scripts/docctl.py check-generated
```

`scan` refreshes derived document metadata such as `content_hash` and declared status. Its scopes are:

```text
ai-system  source documents under /ai-system
root       root entrypoint documents such as AGENTS.md and README*.md
skills     repository skill documents
all        all supported source-document scopes
```

`DOCS_GAPS.md` groups actionable documentation gaps by category, including missing files, declared-status mismatch, active documents without review, stale reviewed content hash, unresolved placeholders, broken local links and stale content hash metadata.

Do not move a document to `active` unless the Human Owner has accepted it.

## `evolutionctl.py`

Use `evolutionctl.py` when the work changes AI Development System behavior:

```text
rules
roles
lifecycle policy
workflow
prompt behavior
command catalog
protected-files policy
scripts/*ctl.py behavior
```

Common commands:

```bash
python scripts/evolutionctl.py init
python scripts/evolutionctl.py change create --title "Add protected-files check" --type tooling --problem "Protected files need drift detection." --proposal "Add a validation command for protected project-control files."
python scripts/evolutionctl.py change transition CHG-001 --to ready
python scripts/evolutionctl.py change approve CHG-001 --notes "Approved"
python scripts/evolutionctl.py change link-task CHG-001 --task TASK-001
python scripts/evolutionctl.py validate
python scripts/evolutionctl.py render
python scripts/evolutionctl.py check-generated
```

Codex must not approve or accept an evolution change on behalf of the Human Owner.

## `contextctl.py`

Use `contextctl.py` for deterministic retrieval context:

```text
registered source docs
derived Markdown chunks
keyword and metadata search
CONTEXT_PACK.md
CONTEXT_STATUS.md
context-events.jsonl
```

Common commands:

```bash
python scripts/contextctl.py status
python scripts/contextctl.py index build
python scripts/contextctl.py search --query "prompt package context retrieval"
python scripts/contextctl.py pack build --task TASK-001 --write
python scripts/contextctl.py pack build --query "prompt package context retrieval" --write
python scripts/contextctl.py validate
python scripts/contextctl.py render
python scripts/contextctl.py check-generated
python scripts/contextctl.py audit --last 20
```

`contextctl.py` reads `docs.json` and `tasks.json`, writes `CONTEXT_PACK.md` and `CONTEXT_STATUS.md`, and appends `context-events.jsonl` when generated context output is written. It does not mutate documentation state or task state.

Default retrieval excludes generated, inactive, archived, deprecated, template and example documents. Use explicit include flags only when the Task or Human Owner requires those sources.

Context Packs must never expand Task scope, allowed files, out-of-scope items or acceptance criteria. If retrieved context conflicts with the Task, the Task remains authoritative.

## Legacy Scripts Versus `aictl.py`

Prefer `aictl.py` for:

```text
command discovery
project doctor
local Web Control Center
supported task list/show/transition commands
current task set/clear
Context Pack build
Codex prompt build
project render
```

Use legacy domain scripts for:

```text
plan mutations not exposed through aictl.py
advanced task mutations and detailed task validation
documentation registry changes
evolution Change Proposal approval gates
domain-specific audit and generated-output checks
commands explicitly required by a Task or lifecycle document
```

Do not use direct file edits to work around a missing facade command. Use the owning CLI or report an unsupported operation.

## Web Control Center

Run the local Web Control Center with:

```bash
python scripts/aictl.py web --host 127.0.0.1 --port 8765
```

Then open:

```text
http://127.0.0.1:8765/
```

The Web Control Center is a local loopback surface. Read views display dashboard state, tasks, epics, review information, recent events, generated output previews, project doctor results, command metadata and available actions.

Controlled write actions are submitted only through confirmed `POST` requests to `/actions`. Web route handlers must not edit protected files directly. A Web write action must route through a registered command, delegate through `aictl.py`, and rely on the owning CLI for validation, audit events and generated-output updates.

Use the Web Control Center as the normal daily cockpit:

```text
Dashboard  current execution, queue and project doctor summary
Tasks      filtered Task workflow cockpit
Evolution  Change Proposal management
Pipeline   supervised batch pipeline cockpit and session detail pages
Actions    Task creation, Bulk Task Import, repair/check and workflow forms
Doctor     detailed project health findings
Generated  read-only generated output previews
Commands   registered command metadata
```

The UI does not make protected state editable. It submits governed actions and then shows the resulting command evidence.

## Tasks Cockpit

The `Tasks` view is designed for large task sets. It has filters for Initiative, Epic, Status and search text. It can group by `Epic`, `Status` or `None`; done Tasks are hidden by default unless `Show done` is selected or a done status filter is active. Grouped results are rendered as collapsible sections. Done status groups start collapsed.

The `Focus Tasks` section keeps the current Task plus ready, in-progress, review and changes-requested Tasks near the top. Use it for the owner loop when a Task is being prepared, executed, reviewed or sent back for rework.

Task rows expose status-aware workflow controls. They show only actions that the Task status and pipeline hints allow:

```text
Run                selected ready or planned Tasks through the effective UI pipeline policy
Prepare for Codex  planned, ready or changes_requested Tasks
Refresh Context    current or in_progress Tasks when available
Submit for Review  in_progress Tasks
Approve & Done     in_review Tasks with Human Owner approval notes
Request Changes    in_review Tasks with rework notes
No row workflows   done or otherwise unavailable actions
```

Row workflow buttons are convenience wrappers around registered workflows. They do not create a new lifecycle path. They still route through `aictl.py`, the owning `*ctl.py` script, validation, audit events and generated-output rendering.

Use task-row `Run` when the owner wants to start a new selected-task pipeline run for a ready or planned Task through the current UI pipeline policy. `Run` creates or uses the selected-task run path; it is not the right control for continuing an already blocked session.

Use `Resume` or `Resume Session` only after an existing pipeline session is `blocked` or `stopped` and the owner has resolved the blocker or intentionally wants to continue that same session. Resume submits `pipeline.run_next` for the existing session, preserving its session history, selected queue, policy snapshot and artifacts. For a running session, use the session page controls such as `Run Next`, `Run Until Blocker` or `Stop Session` as shown by the current status.

Codex may use `Submit for Review` after satisfying a Task contract when the Task scope permits it. Codex must not use `Approve & Done` or provide Human Owner approval notes unless the Human Owner explicitly gave the approval decision.

## Action Result Panel

Every Web write action returns an Action Result panel. Read it before taking the next step.

The panel reports:

```text
PASS or FAIL
registered command
workflow name
target Task, Change or Epic
return code
workflow step results
changed files
generated files
warnings and errors
next actions
Codex instruction when a prompt package is prepared
technical details
```

The Action Result panel is evidence, not approval. A passing action result does not mean Human Owner acceptance, review closure or permission to edit protected files manually.

## Evolution Management Tab

Use the `Evolution` tab for Change Proposal management. It provides Status, Type and search filters; a create-change-for-task form; Change Proposal rows with linked Tasks, affected files, risks, approval state, acceptance state and next-action hints; and lifecycle-aware row actions.

Available row actions depend on Change status:

```text
ready                 Approve Change
approved/in_progress  Move to Review
approved/in_review    Accept Change
```

These actions are owner-facing workflow helpers. Approval and acceptance still require explicit Human Owner notes and still route through registered workflows and `evolutionctl.py`. Codex must not approve, accept, archive or supersede Evolution Changes on behalf of the Human Owner.

## Pipeline Cockpit And Session Details

Use the `Pipeline` page for supervised queue runs. It shows queue preview, effective policy selection, current session state, stop reasons, gate outcomes, `run-next`, `run-until-blocker` and recent pipeline audit entries. Pipeline commands still route through `aictl.py` and the pipeline services. They do not approve Evolution Changes, accept final work, push, merge or bypass review gates.

Current phase-based sessions store phase progress in `phase_history`. The Web Pipeline session detail page uses `phase_history` first and renders each entry as an expandable phase panel with phase label, status, reason, next action, blocker, changed/generated file counts, event counts, execution evidence and bounded log snippets when those artifacts exist. The most recent phase opens by default. When `phase_history` is present, the detail page does not fabricate a legacy `run_next` step.

Older sessions may not have `phase_history`. For those sessions, the detail page falls back to the legacy `steps` records and their `gate_outcomes`, showing the Gate Flow, Gate Outcomes, linked artifacts and logs. If an older session has no step records at all, the page may show a planned `run_next` placeholder so the detail page remains readable.

### Live Status Refresh

A Pipeline session detail page performs partial status refresh while the session status is `running`. The page polls:

```text
/pipeline/sessions/<SESSION_ID>/status.json
```

every two seconds and updates the status badge, current phase, current phase status, stop reason, next action, phase overview and owner guidance without reloading the whole page. This is a live status indicator, not a full historical rerender.

When the session changes to `blocked`, `failed`, `completed` or `stopped`, polling stops and the page shows `Auto-refresh stopped`. At that point Codex is not actively running from that session page. Read the stop reason, next action and phase evidence before pressing any run control.

The quickest way to tell whether Codex is actually running is to check the live status fields:

```text
session status is running
current phase is execute
current phase status is running
the page says Status polling active
```

When runtime logs are available, the `Codex Execute running` panel gives additional evidence: stdout or stderr offsets may increase as output arrives.

If the session is `blocked`, `failed`, `completed` or `stopped`, Codex execution is not currently active for that session even if old stdout or stderr snippets remain visible.

### Live Codex Log Panels

During a running `execute` phase, the session detail page can show a `Codex Execute running` panel with separate `STDOUT` and `STDERR` streams. These panels tail bounded chunks from runtime log files under `AI_PROJECT/logs/codex/...` through the Web route:

```text
/pipeline/sessions/<SESSION_ID>/logs/execute/stdout
/pipeline/sessions/<SESSION_ID>/logs/execute/stderr
```

`stdout` is the local Codex command's normal output. It may include assistant progress, final execution summaries or structured report text emitted by the command. `stderr` is the command's diagnostic/error stream. It may include sandbox, timeout, warning or traceback information depending on the local command.

The live panels and runtime log files are execution evidence only. Do not list `AI_PROJECT/logs/codex/**` or `AI_PROJECT/logs/ui_run/**` as implementation files in a structured Codex report. Only report source files intentionally changed by the Task and generated files that the governed CLIs produced as part of the Task.

Pipeline UI settings are project-local settings in `AI_PROJECT/config/ui_settings.json`. Manage them through `aictl.py`, not by editing protected project-control state:

```bash
python scripts/aictl.py ui settings show
python scripts/aictl.py ui settings init --confirm
python scripts/aictl.py ui settings set command_line "codex exec --json"
python scripts/aictl.py ui settings set default_policy supervised_executable_local_commit
python scripts/aictl.py ui settings set batch_max_steps 7
python scripts/aictl.py ui settings set batch_max_failures 1
python scripts/aictl.py ui settings set preflight_timeout_sec 45
python scripts/aictl.py ui settings set execution_timeout_sec 1800
python scripts/aictl.py ui preflight
```

`command_line` is the owner-facing, shell-style command string for local Codex execution. For executable policy presets, the UI policy resolver parses `command_line` into the effective policy `codex.local_command` tuple and sets `codex.command_allowlist` to that exact command string. `codex.local_command` is the lower-level policy field enforced by the adapter. Non-executable/prompt-only policies do not require `command_line`.

The Settings page shows `Default Policy` as a dropdown. The dropdown is populated from registered pipeline policy presets: built-in presets plus any governed custom presets in the policy preset store. Saving `default_policy` stores the selected preset name; it does not store an arbitrary policy object. When the UI starts a selected-task run, it resolves that preset and then applies supported UI settings such as Codex Review, report-warning, git-diff, batch-limit and timeout overrides.

The Settings page also shows a read-only `Effective Policy Summary` for the policy that would be used by Web runs. It includes:

```text
Policy
batch.max_steps
batch.max_failures
Machine Review
Codex Review
Auto-close
Local Commit
Report Warnings
Git Diff Gates
```

Use this summary before starting a Web run. It reflects the selected preset after UI overrides, so `batch.max_steps` and `batch.max_failures` may differ from the base preset when `Max Steps Override` or `Max Failures Override` is set.

`Max Steps Override` maps to the effective policy `batch.max_steps`. It is optional; leave it blank to use the selected policy preset. Accepted values are `1` through `50`. `Max Failures Override` maps to `batch.max_failures`, is also optional, and accepts `1` through `10`.

The current phase-based selected-task run has seven `run-next` phases:

```text
queue_preview
prepare
execute
collect_report
verify
review
close
```

For a full single-task Web run in one confirmed batch, set the effective `batch.max_steps` to at least `7`. If it is lower, the Web UI shows an `Incomplete Web Run` warning and selected-task `Run` requires `Confirm this partial Web run`. That warning means the session may stop before review or close by policy; it is not a claim that the Task has autonomously completed.

When a low `max_steps` is intentional, let the selected-task run stop, inspect the session detail page, then use `Resume Session` for that same `blocked` or `stopped` session after the blocker is resolved or after deciding to continue the partial run. Do not press task-row `Run` to continue a stopped partial session, because `Run` starts a new selected-task run path with a new policy snapshot instead of continuing the existing session artifacts.

`preflight_timeout_sec` controls only the UI Codex readiness check used by `aictl.py ui preflight` and by `aictl.py ui run --preflight` before a confirmed executable run creates a pipeline session. `execution_timeout_sec` controls the actual local Codex adapter execution timeout by replacing the resolved policy `codex.timeout_sec`. Both values are optional integer seconds from `1` through `3600`; preflight timeout does not change execution timeout, and execution timeout does not change preflight.

## Bulk Task Import In The UI

Use `Actions` -> `Bulk Task Import` when several bounded Tasks already have clear scope. The form accepts pasted JSON in `JSON Payload` or one uploaded `.json` or `.txt` file. Use only one input method per submission.

Leave Confirm unchecked to preview the import. Check Confirm only when the preview is ready to create Tasks. The Web action delegates to `aictl.py task import --text ...` with either `--preview` or `--confirm`.

Bulk import still rejects unknown fields, invalid statuses, invalid Epic references and invalid dependency references before creating anything. It does not set current Task, start work, approve Tasks or execute imported content.

Current controlled Web actions:

```text
task.create
task.import
task.transition
current.set
current.clear
project.render
project.doctor
project.protected_check
docs.render
context.build
codex.prompt.build
task.prepare_for_codex
task.refresh_execution_context
task.submit_for_review
task.close_reviewed
task.request_changes
evolution.create_for_task
evolution.approve_change
evolution.move_to_review
evolution.accept_change
epic.close_if_complete
ui.run_selected_task
pipeline.session.create
pipeline.run_next
pipeline.run_until_blocker
pipeline.session.stop
pipeline.render
```

Web task transitions are limited to non-acceptance statuses:

```text
planned
ready
in_progress
blocked
in_review
changes_requested
deferred
```

The Web surface must not directly edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**`. It must not silently approve tasks, move tasks to `done`, accept evolution changes, or mark documents active. Owner-facing approval and acceptance actions require explicit notes, route through registered commands and remain Human Owner decisions.

## When Do I Need A Task?

Create a Task when the work can change repository files or controlled state.

Examples that need a Task:

```text
create or edit an ai-system document
change a workflow, rule, lifecycle or prompt package
write implementation code
update project-control generated outputs
run a Codex execution package
perform bounded documentation cleanup with acceptance criteria
```

A Task should include:

```text
title
epic_id
summary or description
scope
out_of_scope
allowed_files
acceptance_criteria
verification_mode
active role, stage, document and expected result when useful
```

Do not execute an Initiative or Epic directly. If the Human Owner asks for an Epic to be implemented, create one or more Tasks under that Epic.

## Daily Workflow

Use this UI-first flow for ordinary controlled work:

1. Start the local Web Control Center.

```bash
python scripts/aictl.py web --host 127.0.0.1 --port 8765
```

2. Open `http://127.0.0.1:8765/`, check `Dashboard` and `Doctor`, and use `Tasks` to find the current work by Initiative, Epic, Status or search.

3. Create or import bounded Tasks from `Actions` when needed. Use Bulk Task Import preview before confirming creation.

4. Prepare an executable Task from its row workflow button or from `Actions`:

```text
Prepare for Codex
```

5. Execute only the Task scope from `AI_PROJECT/generated/CODEX_PROMPT.md`.

6. Use the Action Result panel and generated prompt package to decide the next step. Refresh context if the current Task or source documents changed.

7. Validate and submit for review from the Task row:

```text
Submit for Review
```

8. Wait for review and Human Owner acceptance. If the Human Owner accepts the reviewed result, use `Approve & Done` with explicit owner notes. If the Human Owner requests rework, use `Request Changes` with the required notes.

Do not mark the Task approved, done or archived as accepted unless the Human Owner explicitly accepts the result.

The CLI compatibility flow remains available:

1. Inspect current status.

```bash
python scripts/aictl.py task list --current
python scripts/aictl.py project doctor
```

2. Create or reuse an Initiative and Epic.

```bash
python scripts/planctl.py initiative list
python scripts/planctl.py epic list
python scripts/planctl.py initiative create --title "AI Development System Evolution"
python scripts/planctl.py epic create --initiative INIT-001 --title "Documentation Rails"
```

3. Create a bounded Task.

```bash
python scripts/aictl.py task create --confirm --epic EPIC-001 --title "Write Project Control Usage Guide" --scope "Create ai-system/project-control/08-usage-guide.md" --allowed-file "ai-system/project-control/08-usage-guide.md" --acceptance "Documentation validation passes"
```

4. Prepare the Task for Codex.

```bash
python scripts/aictl.py workflow run task.prepare_for_codex --task TASK-001 --confirm
```

5. Execute only the Task scope from `AI_PROJECT/generated/CODEX_PROMPT.md`.

6. Validate and submit for review.

```bash
python scripts/docctl.py validate
python scripts/docctl.py render
python scripts/docctl.py check-generated
python scripts/aictl.py workflow run task.submit_for_review --task TASK-001 --confirm
```

7. Wait for Human Owner acceptance.

If the Human Owner accepts the reviewed result, close it with explicit owner notes:

```bash
python scripts/aictl.py workflow run task.close_reviewed --task TASK-001 --notes "APPROVED by Human Owner" --confirm
```

Do not mark the Task approved, done or archived as accepted unless the Human Owner explicitly accepts the result.

## Bulk Task Import

Use bulk import only when each imported item is already a bounded Task, not an Epic or open-ended idea.

The preferred owner path is the Web Control Center `Actions` page. Paste the JSON payload or upload a `.json` or `.txt` file, preview first, then confirm only after the preview is correct.

Preview first:

```bash
python scripts/aictl.py task import --file tasks.json --preview
python scripts/aictl.py task import --file tasks.json --confirm
```

Accepted JSON shapes are:

```text
single task object with epic and title
array of task objects
object with a tasks array
```

Task object fields are intentionally limited:

```text
epic
title
summary
description
priority
status
active_role
active_stage
active_document
expected_result
verification_mode
scope
out_of_scope
allowed_file / allowed_files
acceptance / acceptance_criteria
review / review_instruction / review_instructions
notes
dependencies / depends_on
dependency_reason
```

Example:

```json
{
  "tasks": [
    {
      "epic": "EPIC-006",
      "title": "Document workflow helper",
      "summary": "Update owner-facing workflow docs.",
      "scope": ["Update project-control guidance"],
      "out_of_scope": ["No command behavior changes"],
      "allowed_files": ["ai-system/project-control/08-usage-guide.md"],
      "acceptance_criteria": ["Documentation validation passes"],
      "dependencies": ["WFA-01"],
      "verification_mode": "standard",
      "status": "planned"
    }
  ]
}
```

Bulk import rejects unknown fields, accepts only `proposed`, `planned` or `ready` status, validates Epic and dependency references before creating anything, and delegates each created Task to the same create-only workflow. It does not set current Task, start execution, approve Tasks or execute imported content.

## Writing Or Changing Documentation

Use this flow for managed documentation:

1. Check whether the document is already registered.

```bash
python scripts/docctl.py show
```

2. Register the document if it is not registered.

```bash
python scripts/docctl.py doc register --path ai-system/project-control/08-usage-guide.md --title "Project Control Usage Guide" --type guide --status planned
```

3. Create or update the source document inside the Task's allowed files.

4. Move the document to draft after the file exists.

```bash
python scripts/docctl.py doc status ai-system/project-control/08-usage-guide.md --to draft
```

5. Move the document to review after writing and validation.

```bash
python scripts/docctl.py doc status ai-system/project-control/08-usage-guide.md --to review
```

6. Render and check generated documentation outputs.

```bash
python scripts/docctl.py scan --scope all
python scripts/docctl.py validate
python scripts/docctl.py render
python scripts/docctl.py check-generated
```

Only move a document to `active` after Human Owner acceptance.

## How CODEX_PROMPT.md Fits Into Execution

`CODEX_PROMPT.md` is generated by `taskctl.py` from the selected Task.

It is written to:

```text
AI_PROJECT/generated/CODEX_PROMPT.md
```

Build it with:

```bash
python scripts/aictl.py current set TASK-001
python scripts/aictl.py codex prompt build --task TASK-001
python scripts/aictl.py workflow run task.prepare_for_codex --task TASK-001 --confirm
python scripts/taskctl.py current set TASK-001
python scripts/taskctl.py prompt build --write
```

When using the dedicated Codex execution package gateway, build it with:

```bash
python scripts/codexctl.py build --task TASK-001
```

If a Context Pack should be included, generate or refresh it first, then build the prompt with explicit context:

```bash
python scripts/aictl.py context build --task TASK-001 --write
python scripts/aictl.py codex prompt build --task TASK-001 --with-context
python scripts/contextctl.py pack build --task TASK-001 --write
python scripts/codexctl.py build --task TASK-001 --context-pack AI_PROJECT/generated/CONTEXT_PACK.md
```

Codex should treat the generated prompt package as the execution contract:

```text
use the active role and stage
work only on the Task ID
stay inside Scope
avoid Out of Scope
edit only Allowed Files
run the requested verification mode
report changed files, checks, risks and owner action required
```

If `CODEX_PROMPT.md` contains a Retrieved Context section, treat that context as read-only. It can point Codex to relevant source sections, but it cannot add scope, allowed files or acceptance criteria.

If the prompt is wrong, do not edit `CODEX_PROMPT.md` manually. Update the Task through `taskctl.py`, then rebuild the prompt.

## Common Flows

## Add A Documentation Guide

```bash
python scripts/planctl.py initiative create --title "AI Development System Evolution"
python scripts/planctl.py epic create --initiative INIT-001 --title "Documentation Rails"
python scripts/taskctl.py task create --epic EPIC-001 --title "Write New Guide" --scope "Create ai-system/example-guide.md" --allowed-file "ai-system/example-guide.md" --acceptance "docctl validation passes"
python scripts/taskctl.py current set TASK-001
python scripts/taskctl.py prompt build --write
python scripts/docctl.py doc register --path ai-system/example-guide.md --title "Example Guide" --type guide --status planned
```

After the file exists:

```bash
python scripts/docctl.py doc status ai-system/example-guide.md --to draft
python scripts/docctl.py doc status ai-system/example-guide.md --to review
```

## Prepare System Evolution

```bash
python scripts/evolutionctl.py change create --title "Clarify prompt package rules" --type prompt --problem "Prompt package rules are unclear." --proposal "Clarify prompt package generation and review boundaries."
python scripts/evolutionctl.py change transition CHG-001 --to ready
```

Stop at `ready` until the Human Owner approves the Change Proposal.

When a bounded Task already describes the intended system evolution, use the guided workflow to draft and prepare the Change Proposal:

```bash
python scripts/aictl.py workflow run evolution.create_for_task --task TASK-001 --confirm
```

This workflow stops at `ready`. It does not approve, accept or close the Change Proposal.

## Repair Generated Task Output

```bash
python scripts/taskctl.py render
python scripts/taskctl.py check-generated
```

## Inspect Recent Audit Events

```bash
python scripts/planctl.py audit --last 20
python scripts/taskctl.py audit --last 20
python scripts/docctl.py audit --last 20
```

## What Codex Must Never Do

Codex must never:

```text
edit AI_PROJECT/state/*.json manually
edit AI_PROJECT/events/*.jsonl manually
edit AI_PROJECT/generated/*.md manually
use sed, echo, jq, python -c or ad-hoc scripts to mutate protected state
invent lifecycle states
invent CLI commands
execute an Initiative or Epic directly
approve its own Task
mark a document active without Human Owner acceptance
accept or archive an evolution change on behalf of the Human Owner
treat generated Markdown as source of truth
```

If Codex needs a project-control mutation, it must run the owning CLI command.

## Troubleshooting

## `PLAN_NOT_INITIALIZED`

Plan control has not been initialized.

```bash
python scripts/planctl.py init --project-name "AI Development System"
```

## `TASKS_NOT_INITIALIZED`

Task control has not been initialized.

```bash
python scripts/taskctl.py init
```

## `DOCS_NOT_INITIALIZED`

Documentation control has not been initialized.

```bash
python scripts/docctl.py init
```

## `NO_TASK_SELECTED`

No current Task is selected for prompt generation.

```bash
python scripts/taskctl.py current set TASK-001
python scripts/taskctl.py prompt build --write
```

## `TASK_IS_NOT_EXECUTABLE`

The selected Task is inactive or not allowed for prompt generation.

Use an executable Task status such as `ready`, `in_progress` or `changes_requested`, or use `--allow-inactive` only for inspection.

## `VALIDATION_FAILED`

Read the listed errors and fix the source problem through the owning CLI or source document.

Examples:

```text
missing parent Epic -> create or select a valid Epic through planctl.py
generated task output is stale -> run taskctl.py render
registered draft document is missing -> create the document source file
```

## Generated Output Drift

For task generated output:

```bash
python scripts/taskctl.py render
python scripts/taskctl.py check-generated
```

For documentation generated output:

```bash
python scripts/docctl.py render
python scripts/docctl.py check-generated
```

For context generated output:

```bash
python scripts/contextctl.py render
python scripts/contextctl.py check-generated
```

`planctl.py` currently supports `render`, but does not expose a `check-generated` command.

## `CODEX_ADAPTER_TIMEOUT`

The local Codex adapter exceeded the effective execution timeout. Inspect the Pipeline session detail page for the failed `execute` phase. Its Execution Evidence can show `CODEX_ADAPTER_TIMEOUT`, command, timeout, duration, prompt path, Context Pack path and bounded stdout/stderr snippets or log references.

Use `execution_timeout_sec` only for the actual executable Codex run. If the readiness check is timing out before a session starts, adjust `preflight_timeout_sec` or pass the explicit preflight timeout flag. If execution times out, either reduce the Task scope, fix the configured `command_line` or sandbox behavior, or increase `execution_timeout_sec` only when the Human Owner accepts the longer local run.

## Missing Codex Report Evidence

Executable pipeline policies require a structured Codex execution report after the local command finishes. If no report exists, the Codex Report Gate fails and auto-close or local commit gates remain blocked. Review pages may show this as:

```text
No Codex execution report submitted for this task.
```

Pipeline sessions may also show this blocker as:

```text
REPORT_MISSING
```

Submit the report through the governed command:

```bash
python scripts/aictl.py task report submit --task TASK-001 --file REPORT.json --confirm
```

Do not treat stdout, chat text or generated prompt content as report evidence unless it has been submitted through the report command.

If the report was only shown in the Codex live log panel or pasted in chat, create a structured report file from the actual task result and submit it through `task report submit`. Then rerun the blocked report or close gate through the governed Pipeline or Task workflow. Runtime log files are evidence sources for diagnosis; they are not implementation files and should not be added to the report's changed file lists.

## Git Diff Gate `missing_from_report`

If a verify or close gate reports `missing_from_report`, the current git diff contains paths that are not declared in the structured execution report. This usually means either the report omitted a real Task change or the working tree contains unrelated/generated/runtime changes.

Respond by comparing the gate's missing paths with the Task contract:

```text
real Task source change        add it to the structured report and resubmit
governed generated output      include it only when it was intentionally regenerated by the Task
runtime logs or UI run logs    do not report as implementation files
unrelated dirty file           resolve or separate it before rerunning the gate
protected state/event output   do not edit manually; regenerate or mutate only through the owning CLI
```

After correcting the report or working tree, rerun the governed verify, close or pipeline step that produced the diff gate result.

## Unsupported Operation

If no allowed command exists, report:

```text
NO_ALLOWED_COMMAND
requested_intent: ...
closest_existing_command: ...
missing_capability: ...
required_system_evolution: ...
```

Do not mutate protected files to work around a missing command.

## Final Validation Checklist

Before reporting a project-controlled documentation task as ready for Human Owner acceptance, run:

```bash
python scripts/planctl.py validate
python scripts/planctl.py render
python scripts/taskctl.py validate
python scripts/taskctl.py render
python scripts/taskctl.py check-generated
python scripts/docctl.py validate
python scripts/docctl.py render
python scripts/docctl.py check-generated
python scripts/contextctl.py validate
python scripts/contextctl.py check-generated
python scripts/smoke-context-control.py
python scripts/smoke-doc-control.py
python scripts/check-protected-project-files.py --verbose
```

If evolution state was changed, also run:

```bash
python scripts/evolutionctl.py validate
python scripts/evolutionctl.py render
python scripts/evolutionctl.py check-generated
```

Final state should be:

```text
source changes complete
generated outputs current
validation passed
Task in review or equivalent non-accepted state
document in review or equivalent non-active state
Human Owner acceptance still pending
```

# Project Control Owner Quickstart

## Status

Review

## Purpose

This quickstart gives the Human Owner and Codex Executor a short operating path for the completed centralized Project Control Gateway.

Use it when you need to inspect current work, discover commands, run health checks, open the local Web Control Center, build context, build a Codex prompt package, or submit a bounded Task for review.

This document is operational guidance only. It does not add command behavior, approve work, accept work, or weaken protected-file rules.

Core rule:

```text
Prefer aictl.py for discovery, health checks, supported facade commands and the local Web Control Center.
Use the domain ctl scripts when a command is not exposed by aictl.py or when a lifecycle document explicitly names the owning script.
Never edit protected AI_PROJECT files directly.
```

## Five-Minute Start

1. Open the local Web Control Center.

```bash
python scripts/aictl.py web --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765/`. The Web Control Center is local and loopback-only. Use it as the daily cockpit; use command lines when a runbook requires an exact command or when the UI does not expose the needed operation.

2. Check the dashboard and health.

```text
Dashboard  current execution, queue, project doctor summary
Doctor     detailed PASS, WARN and FAIL findings
Generated  read-only generated outputs
Commands   registered command metadata
```

`project doctor` aggregates registered command checks, plan/task/evolution validation, task graph validation, generated-output freshness, context and Codex prompt status, and protected-file checks. It reports explicit `PASS`, `WARN` and `FAIL` findings and does not mutate project-control state.

3. Work from the Tasks cockpit.

Use `Tasks` to filter by Initiative, Epic, Status and search text. Choose Group by `Epic`, `Status` or `None`; `done` Tasks are hidden by default unless `Show done` is selected or `status=done` is selected. Task groups are collapsible, and done status groups start collapsed.

The `Focus Tasks` section keeps the current Task plus ready, in-progress, review and changes-requested Tasks visible. Task references such as `CTL-12` are human-readable aliases. The same Task may also resolve by legacy ID such as `TASK-030`, immutable UID, or alias when `taskctl.py` supports that resolver. Use the readable ref in chat and prompts, but remember that state in `AI_PROJECT/state/tasks.json` remains the source of truth.

4. Use row workflow buttons for normal Task movement.

Task rows show only workflows that apply to the current status and pipeline hints:

```text
Run                selected ready or planned Tasks through the effective UI pipeline policy
Prepare for Codex  planned, ready or changes_requested Tasks
Refresh Context    current or in_progress Tasks when available
Submit for Review  in_progress Tasks
Approve & Done     in_review Tasks with Human Owner approval notes
Request Changes    in_review Tasks with rework notes
No row workflows   done or otherwise unavailable actions
```

When a selected-task `Run` form shows `Auto-close Owner Note`, fill it only with an explicit Human Owner approval note for that run. Leave it blank for non-auto-close policies. Codex may point out that the field is required by an auto-close policy, but Codex must not invent or provide the note.

Use task-row `Run` to start a new selected-task pipeline run for a ready or planned Task. Use `Resume` or `Resume Session` only for an existing `blocked` or `stopped` session after resolving the blocker or deciding to continue that same session. Resume continues the existing session with its current policy snapshot and artifacts; it does not start fresh work.

Before pressing `Run`, open `Settings` and check `Effective Policy Summary`. If `batch.max_steps` is below `7`, the selected-task run cannot traverse all seven current phases in one batch: queue preview, prepare, execute, collect report, verify, review and close. The UI will show `Incomplete Web Run` and require `Confirm this partial Web run`. Use `Max Steps Override` to set `batch.max_steps` to at least `7` when the owner wants a full single-task run in one batch; leave the lower value only when a deliberate partial run is acceptable.

Each workflow posts to `/actions`, delegates through registered `aictl.py` workflows and owning `*ctl.py` scripts, and then opens an Action Result panel. Read that panel before continuing. It shows PASS/FAIL, registered command, workflow, target, return code, step results, changed and generated files, warnings, errors, next actions, any Codex instruction to copy into a session, and technical details.

5. Use Evolution and Actions when needed.

`Evolution` lets you filter Change Proposals by Status, Type and search text, create a Change for a Task, and run owner-facing change workflows such as approve, move to review and accept when the proposal state allows them. Human Owner approval or acceptance notes are still required where the lifecycle requires them; Codex must not provide those notes on its own.

`Pipeline` shows the supervised batch pipeline cockpit for queue preview, policy selection, current session state, gate outcomes, run-next, run-until-blocker and recent pipeline audit entries. It is supervised automation only; it does not approve Evolution Changes, accept final work, push, merge, or bypass review gates.

Pipeline session IDs link to persistent detail pages such as `http://127.0.0.1:8765/pipeline/sessions/PSESS-012`. Use a session detail page to watch a running session, inspect expandable phase or step records, bounded Codex stdout/stderr snippets, artifacts, queue snapshot, related audit events, changed files and blockers, or reopen completed, blocked, failed, stopped and archived sessions later. Current phase-based sessions render from `phase_history`; older sessions without `phase_history` fall back to legacy `steps` and `gate_outcomes`. The page uses simple polling while a session is `running` and stops polling in terminal or owner-action states. It does not render full `CODEX_PROMPT.md` content and does not expose destructive git actions.

Codex is actually running only when the session status is `running`, the current phase is `execute`, the current phase status is `running`, and the page shows active status polling or a `Codex Execute running` log panel. If the page says `Auto-refresh stopped`, the session is terminal or waiting for owner action.

Live Codex logs appear on the Pipeline session detail page during the `execute` phase as separate `STDOUT` and `STDERR` panels. `stdout` is normal command output; `stderr` is diagnostics or error output. These runtime logs are execution evidence and troubleshooting context, not implementation files to list in a structured report.

`Actions` contains direct forms for Task creation, Bulk Task Import, health and repair checks, Task workflows, Task transitions, current Task changes, generated-output refreshes, and Codex/context builds. Bulk Task Import supports pasted JSON and `.json` or `.txt` file upload; leave Confirm unchecked for preview and check Confirm only when the preview is ready to create Tasks.

## Command-Line Equivalents

The UI is the preferred daily path, but the same control plane remains available from the shell.

Inspect current work:

```bash
python scripts/aictl.py task list --current
python scripts/aictl.py task show CTL-12
```

Discover commands and workflows:

```bash
python scripts/aictl.py command list
python scripts/aictl.py command describe project.doctor
python scripts/aictl.py command describe web.serve
python scripts/aictl.py command describe task.transition
python scripts/aictl.py workflow list
python scripts/aictl.py workflow describe task.prepare_for_codex
```

Use `--json` when another tool needs machine-readable output:

```bash
python scripts/aictl.py --json command list
```

Run the owner health check:

```bash
python scripts/aictl.py project doctor
```

Build task context and a Codex prompt package:

```bash
python scripts/aictl.py context build --task CTL-12 --write
python scripts/aictl.py codex prompt build --task CTL-12 --with-context
```

The Context Pack and Codex prompt package are generated output. They are read-only context and execution instructions. They do not expand Task scope, allowed files, out-of-scope items or acceptance criteria.

## Task Lifecycle Commands

Only a Task is executable. Initiative and Epic organize work; they are not execution scope.

For daily operation, prefer the Tasks cockpit and its row workflow buttons. Use these commands as compatibility tools, automation targets or recovery paths.

Common `aictl.py` task commands:

```bash
python scripts/aictl.py task list
python scripts/aictl.py task list --epic EPIC-005
python scripts/aictl.py task list --status in_progress
python scripts/aictl.py task show CTL-12
python scripts/aictl.py task create --confirm --epic EPIC-005 --title "Bounded Task Title"
python scripts/aictl.py task import --file tasks.json --preview
python scripts/aictl.py current set CTL-12
python scripts/aictl.py task transition CTL-12 --to in_progress
python scripts/aictl.py task transition CTL-12 --to in_review
python scripts/aictl.py current clear
```

Use `taskctl.py` when the needed task operation is not exposed through the `aictl.py` parser or when you need detailed task validation/audit commands:

```bash
python scripts/taskctl.py task show CTL-12
python scripts/taskctl.py current show --json
python scripts/taskctl.py validate
python scripts/taskctl.py task graph validate
python scripts/taskctl.py render
python scripts/taskctl.py check-generated
```

Codex may transition a completed execution task to `in_review` when the Task scope says to do so. Codex must not approve a Task, move it to `done`, or treat validation success as Human Owner acceptance.

## Workflow Automation Helpers

Use `workflow list` to discover confirmed composed workflows:

```bash
python scripts/aictl.py workflow list
python scripts/aictl.py workflow describe task.prepare_for_codex
python scripts/aictl.py workflow describe task.submit_for_review
python scripts/aictl.py workflow describe task.close_reviewed
python scripts/aictl.py workflow describe evolution.create_for_task
```

Common workflow runs:

```bash
python scripts/aictl.py workflow run task.prepare_for_codex --task CTL-12 --confirm
python scripts/aictl.py workflow run task.refresh_execution_context --task CTL-12 --confirm
python scripts/aictl.py workflow run task.submit_for_review --task CTL-12 --confirm
python scripts/aictl.py workflow run task.close_reviewed --task CTL-12 --notes "APPROVED by Human Owner" --confirm
python scripts/aictl.py workflow run evolution.create_for_task --task CTL-12 --confirm
```

`task.prepare_for_codex` sets the current Task, moves it to `in_progress` when needed, rebuilds the Context Pack, rebuilds the Codex prompt with context and runs `project doctor`.

`task.refresh_execution_context` rebuilds only the task Context Pack and Codex prompt package.

`task.submit_for_review` runs blocking validation and freshness checks before moving the Task to `in_review`.

`task.close_reviewed` is an owner-facing close helper. It requires explicit approval notes, rejects Tasks that are not `in_review`, delegates approval to `taskctl.py task approve` and then moves the Task to `done`.

`evolution.create_for_task` drafts an Evolution Change from a bounded Task, adds derived affected files, risks and impact, links the Task, validates evolution state and moves the Change only to `ready`. It does not approve or accept the Change.

## Supervised Pipeline Runner

Use the Pipeline page when the Human Owner wants a supervised queue runner instead of manually pressing one task workflow at a time.

The implemented pipeline flow is:

```text
Queue -> Policy -> Change -> Prepare -> Token Gate -> Codex Execute -> Report -> Machine Review -> Codex Review -> Done/Rework -> Accept Change -> Commit -> Next / Stop on Blocker
```

Policy presets decide what is allowed, but they do not remove owner gates:

- `dry_run` keeps Codex execution, auto-close and commit disabled.
- `supervised` selects from the ready queue and builds a Codex prompt package, then stops before Codex execution.
- `supervised_executable` runs the allowlisted local Codex adapter after Token Budget Gate PASS and requires a structured Codex execution report.
- `supervised_autoclose` is a prompt-only legacy preset; it blocks before close because Codex execution evidence is missing.
- `supervised_executable_autoclose` runs the allowlisted local Codex adapter, then may close only after Codex Report Gate PASS, Machine Review PASS, Codex Review APPROVE and an explicit owner auto-close note on the session.
- `supervised_local_commit` is a prompt-only legacy preset; local commit is blocked before commit because close evidence is missing.
- `supervised_executable_local_commit` adds local-only commit policy after executable run, approved review gates, auto-close and commit-readiness gates pass. A report `WARN` may reach commit readiness only when policy explicitly allows advisory report warnings; Machine Review `WARN` may reach local commit only when every warning is non-blocking advisory evidence or explicitly policy-approved report-warning evidence. Report `FAIL`, report `BLOCKED`, advisory-disabled report `WARN`, unsafe Machine Review `WARN` and Machine Review `FAIL` still block. Push and merge remain forbidden.

Auto-close owner notes are explicit Human Owner approval inputs. Supply them only when the Human Owner has approved auto-close for the selected task or queue. Codex must not draft, fabricate, reuse, or paste approval notes on the owner's behalf.

Executable pipeline policies pass `AI_PROJECT/generated/CODEX_PROMPT.md` to the local Codex command through stdin by default. The configured command must exactly match the policy allowlist. Owner-configured sandbox flags are allowed only when both `local_command` and `command_allowlist` include the exact command.

UI settings provide the owner-facing command and timeout values:

```bash
python scripts/aictl.py ui settings show
python scripts/aictl.py ui settings set command_line "codex exec --json"
python scripts/aictl.py ui settings set default_policy supervised_executable_local_commit
python scripts/aictl.py ui settings set batch_max_steps 7
python scripts/aictl.py ui settings set batch_max_failures 1
python scripts/aictl.py ui settings set preflight_timeout_sec 45
python scripts/aictl.py ui settings set execution_timeout_sec 1800
python scripts/aictl.py ui preflight
```

`Default Policy` is selected from registered policy presets shown in the Settings dropdown. Built-in and governed custom presets may appear there. The `Effective Policy Summary` shows the selected preset after UI overrides, including `batch.max_steps`, `batch.max_failures`, Machine Review, Codex Review, Auto-close, Local Commit, Report Warnings and Git Diff Gates.

`command_line` is the shell-style UI setting. For executable policies, it is parsed into the resolved policy `codex.local_command` and exact `codex.command_allowlist`; those policy fields are what the local adapter enforces. `batch_max_steps` and `batch_max_failures` are optional Web-run overrides; blank values use the selected policy preset, while explicit values must stay within the Settings bounds. `preflight_timeout_sec` applies to the UI readiness check before session creation. `execution_timeout_sec` applies to the actual local Codex adapter run. Do not use one timeout as evidence for the other.

If a session blocks with `CODEX_ADAPTER_TIMEOUT`, inspect the session detail `execute` phase for timeout, duration, command and bounded stdout/stderr evidence. If a close or commit gate says report evidence is missing, submit a structured report with `python scripts/aictl.py task report submit --task TASK-001 --file REPORT.json --confirm`; stdout or chat text is not report evidence until submitted through that command.

If the blocker is `REPORT_MISSING`, submit the structured execution report through `task report submit`, then rerun the blocked collect-report, close or pipeline step. Do not treat live stdout, stderr, chat text or runtime log files as a submitted report.

If a diff gate reports `missing_from_report`, compare the missing paths with the Task contract. Add omitted real Task source changes to the structured report, include governed generated output only when the Task intentionally regenerated it, and leave runtime logs such as `AI_PROJECT/logs/codex/**` or `AI_PROJECT/logs/ui_run/**` out of implementation file lists. Resolve unrelated dirty files before rerunning the gate.

If close succeeds but local commit blocks with `COMMIT_REPORT_GATE_NOT_PASS`, the commit gate rejected the report gate status. For report `WARN`, confirm whether the selected policy intentionally enables advisory report warnings and rerun the governed gates; strict mode still blocks `WARN` when advisory report warnings are disabled. For report `FAIL` or `BLOCKED`, fix and resubmit the structured report before trying commit again.

If local commit blocks with `COMMIT_READINESS_FAILED`, inspect `local_commit.readiness` in the Action Result panel or session artifacts. For Machine Review `WARN`, only explicit advisory warnings are acceptable before local commit: non-blocking Machine Review warnings, or a policy-approved `codex_report_gate` warning. Blocking or unapproved warnings, missing required commit-readiness checks, required checks that are not `PASS`, and Machine Review `FAIL` must be fixed and rerun before commit.

Manual local Codex preflight examples:

```bash
codex exec -s workspace-write < AI_PROJECT/generated/CODEX_PROMPT.md
codex exec -s danger-full-access < AI_PROJECT/generated/CODEX_PROMPT.md
```

Prefer `workspace-write` when it works. Configure `danger-full-access` or bypass modes only when the local environment is already externally sandboxed and the owner intentionally allowlists that command.

CLI equivalents:

```bash
python scripts/aictl.py pipeline status
python scripts/aictl.py pipeline session create --policy supervised --task-ref PIPE-15
python scripts/aictl.py pipeline session create --policy supervised_executable_autoclose --task-ref PIPE-25 --auto-close-note "APPROVED by Human Owner for this selected session"
python scripts/aictl.py ui run PIPE-25 --auto-close-note "APPROVED by Human Owner for this selected task run" --confirm
python scripts/aictl.py pipeline run-next
python scripts/aictl.py pipeline run-until-blocker --confirm
python scripts/aictl.py pipeline render
python scripts/aictl.py pipeline check-generated
```

Read the full SOP before running batches:

```text
ai-system/project-control/pipeline-runner.md
```

## Bulk Task Import

Use bulk import when several bounded Tasks already have clear scope. In the Web Control Center, open `Actions`, use `Bulk Task Import`, and either paste JSON into `JSON Payload` or upload a `.json` or `.txt` file. Use one input method at a time.

Leave Confirm unchecked to preview the import. Check Confirm only after the preview is ready to create Tasks. The Action Result panel reports the registered command, step status, warnings, errors and created or generated files.

The CLI compatibility path is still available:

```bash
python scripts/aictl.py task import --file tasks.json --preview
python scripts/aictl.py task import --file tasks.json --confirm
```

Accepted JSON shapes are either an array of task objects, a single task object with `epic` and `title`, or an object with a `tasks` array:

```json
{
  "tasks": [
    {
      "epic": "EPIC-006",
      "title": "Document workflow helper",
      "summary": "Update owner-facing workflow docs.",
      "scope": ["Update project-control guidance"],
      "out_of_scope": ["No command behavior changes"],
      "allowed_files": ["ai-system/project-control/10-owner-quickstart.md"],
      "acceptance_criteria": ["Documentation validation passes"],
      "dependencies": ["WFA-01"],
      "verification_mode": "standard",
      "status": "planned"
    }
  ]
}
```

Bulk import accepts only known task fields, allows `proposed`, `planned` or `ready` statuses, validates Epic and dependency references before creating anything, and delegates every created Task to the same create-only workflow. It does not set current Task, start work, approve Tasks or execute imported content.

## ID Allocation And Task References

Project-control IDs are allocated by the owning CLI and recorded in machine state. Do not invent IDs by editing JSON.

The active Task identity model uses:

```text
uid        immutable machine identity
ref        human-readable reference, such as CTL-12
legacy_id  backward-compatible TASK-030 style ID
aliases    additional resolvable references
epic_id    parent Epic ID, such as EPIC-005
epic_key   readable Epic key, such as CTL
local_seq  sequence number inside the Epic key
```

Use the human ref in owner conversation and Codex prompts:

```bash
python scripts/aictl.py task show CTL-12
python scripts/taskctl.py task show CTL-12
```

Use the parent Epic ID for filters that require an Epic identifier:

```bash
python scripts/aictl.py task list --epic EPIC-005
```

Task references do not create execution order by themselves. Dependency records and lifecycle status determine executable order. Generated task files display refs for readability, but `AI_PROJECT/state/tasks.json` remains the source of truth and must be changed only through `taskctl.py` or supported registered facade commands.

## Evolution Approval Gates

Use `evolutionctl.py` for AI Development System changes, including rules, lifecycle documents, workflow, prompt behavior, command catalog, protected-file policy, ctl scripts, `AGENTS.md`, `ai-system/**`, templates, skills and plugins.

In the Web Control Center, use the `Evolution` tab for day-to-day Change Proposal management. It shows counts, Status and Type filters, search, linked Tasks, affected files, risks, approval state, acceptance state, next-action hints and available owner-facing row actions. Available actions depend on lifecycle status:

```text
ready                 Approve Change
approved/in_progress  Move to Review
approved/in_review    Accept Change
```

Approval and acceptance actions require explicit Human Owner notes. They route through registered workflows and `evolutionctl.py`; the UI must not bypass the lifecycle, and Codex must not provide owner approval or acceptance on its own.

Create and prepare a Change Proposal:

```bash
python scripts/evolutionctl.py change create --title "Clarify project-control behavior" --type docs --problem "The documented behavior is unclear." --proposal "Clarify the owner-facing usage guide."
python scripts/evolutionctl.py change add-affected-file CHG-001 --text "ai-system/project-control/08-usage-guide.md"
python scripts/evolutionctl.py change transition CHG-001 --to draft
python scripts/evolutionctl.py change transition CHG-001 --to ready
```

Stop at `ready` until the Human Owner approves:

```bash
python scripts/evolutionctl.py change approve CHG-001 --notes "Approved"
```

After approval, link a bounded Task and execute only that Task:

```bash
python scripts/evolutionctl.py change link-task CHG-001 --task TASK-001
python scripts/evolutionctl.py validate
python scripts/evolutionctl.py render
python scripts/evolutionctl.py check-generated
```

Codex must not approve, accept, archive or supersede evolution changes for the Human Owner.

For a Task that already describes a system evolution item, the guided wizard can draft and prepare a Change Proposal:

```bash
python scripts/aictl.py workflow run evolution.create_for_task --task CTL-12 --confirm
```

The wizard stops at `ready`. The Human Owner must still approve or reject the Change Proposal with `evolutionctl.py`; Codex must not treat the wizard result as approval.

## Legacy Scripts Versus aictl.py

Use `aictl.py` first for:

- command discovery with `command list` and `command describe`;
- task list/show/transition when exposed by the facade;
- current task set/clear;
- task-scoped Context Pack build;
- Codex prompt package build;
- `project doctor`;
- `project render`;
- local Web Control Center startup.

Use legacy domain scripts when:

- the domain command is not exposed through the `aictl.py` parser;
- a lifecycle document names the owner CLI, such as `docctl.py` for documentation state or `evolutionctl.py` for Change Proposals;
- you need detailed audit, status, validation, render or check-generated commands for one domain;
- you are preserving compatibility with existing prompts, tests or owner runbooks.

Do not bypass a missing facade command by editing protected files. Use the owning legacy CLI or report:

```text
NO_ALLOWED_COMMAND
requested_intent: ...
closest_existing_command: ...
missing_capability: ...
required_system_evolution: ...
```

## Web Control Center Safety Model

The Web Control Center is a local control surface served by:

```bash
python scripts/aictl.py web --host 127.0.0.1 --port 8765
```

Read views are loaded through `GET` routes. Controlled write actions use confirmed `POST` requests to `/actions`.

Current controlled Web actions are:

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

Every Web write action must:

- require explicit confirmation;
- route through a registered command and the `aictl.py` facade;
- rely on the owning CLI for validation, audit events and generated-output updates;
- reject arbitrary file write fields such as `path`, `file`, `filename` or `content`;
- preserve protected-file rules.

Web task transitions are intentionally limited to non-acceptance workflow states:

```text
planned
ready
in_progress
blocked
in_review
changes_requested
deferred
```

The Web surface must not directly edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**`. It must not silently approve tasks, accept tasks, accept evolution changes, or mark documents active. Owner-facing approval and acceptance actions require explicit notes, route through registered commands and remain Human Owner decisions.

For selected-task runs, the Web Control Center exposes an `Auto-close Owner Note` field on the Task row `Run` form and the `Actions` selected-task run form. That field is the Web equivalent of `--auto-close-note`; use it only for an explicit Human Owner approval note for that selected run. If an auto-close policy is selected and the field is empty, the run must block for owner input. Codex must not fill the field or provide placeholder approval text.

## Protected Files And Generated Output

Root `/AI_PROJECT` is the self-hosted project-control layer for this repository:

```text
AI_PROJECT/state/**      machine-readable current state
AI_PROJECT/events/**     append-only audit events
AI_PROJECT/generated/**  generated readable output
```

Generated files are derived output. They may be read by the Human Owner, ChatGPT Orchestrator, Codex Executor and Web Control Center, but they are not source of truth and must not be edited manually.

If generated output is stale, regenerate it through the owning command:

```bash
python scripts/aictl.py project render
python scripts/taskctl.py render
python scripts/docctl.py render
python scripts/contextctl.py render
python scripts/evolutionctl.py render
python scripts/aictl.py pipeline render
```

Then check freshness:

```bash
python scripts/taskctl.py check-generated
python scripts/docctl.py check-generated
python scripts/contextctl.py check-generated
python scripts/evolutionctl.py check-generated
python scripts/aictl.py pipeline check-generated
python scripts/check-protected-project-files.py --verbose
```

## Context And Codex Prompt Builds

Build Context Packs with `aictl.py`:

```bash
python scripts/aictl.py context build --task CTL-12 --write
python scripts/aictl.py context build --query "project doctor web write safety" --write
```

Or use the owning legacy CLI:

```bash
python scripts/contextctl.py pack build --task CTL-12 --write
python scripts/contextctl.py validate
python scripts/contextctl.py check-generated
```

Build Codex prompt packages with `aictl.py`:

```bash
python scripts/aictl.py codex prompt build --task CTL-12
python scripts/aictl.py codex prompt build --task CTL-12 --with-context
python scripts/aictl.py codex prompt build --task CTL-12 --context-pack AI_PROJECT/generated/CONTEXT_PACK.md
```

Or use the owning legacy CLI:

```bash
python scripts/codexctl.py build --task CTL-12
python scripts/codexctl.py build --task CTL-12 --context-pack AI_PROJECT/generated/CONTEXT_PACK.md
python scripts/codexctl.py status
```

If the generated prompt is wrong, update the underlying Task through `taskctl.py` or the relevant source document through an approved Task. Do not edit `CODEX_PROMPT.md` manually.

## Final Owner Review Path

Before submitting a bounded Task for review, run the Task's required checks and the project doctor:

```bash
python -m unittest discover tests
python scripts/planctl.py validate
python scripts/evolutionctl.py validate
python scripts/taskctl.py validate
python scripts/taskctl.py task graph validate
python scripts/contextctl.py validate
python scripts/aictl.py project doctor
python scripts/check-protected-project-files.py --verbose
```

For documentation changes, also run:

```bash
python scripts/docctl.py validate
python scripts/docctl.py render
python scripts/docctl.py check-generated
```

If acceptance criteria are satisfied, submit the Task for review:

```bash
python scripts/aictl.py workflow run task.submit_for_review --task CTL-12 --confirm
```

Stop there until review and Human Owner decision. If the Human Owner decides `APPROVED`, close the reviewed Task with explicit notes:

```bash
python scripts/aictl.py workflow run task.close_reviewed --task CTL-12 --notes "APPROVED by Human Owner" --confirm
```

The Human Owner decides `APPROVED`, `REWORK`, `REJECTED`, `DEFERRED` or `EXPERIMENT`.

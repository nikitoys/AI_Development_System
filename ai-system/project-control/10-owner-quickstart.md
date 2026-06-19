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

1. Inspect the current task.

```bash
python scripts/aictl.py task list --current
python scripts/aictl.py task show CTL-12
```

Task references such as `CTL-12` are human-readable aliases. The same Task may also resolve by legacy ID such as `TASK-030`, immutable UID, or alias when `taskctl.py` supports that resolver. Use the readable ref in chat and prompts, but remember that state in `AI_PROJECT/state/tasks.json` remains the source of truth.

2. Discover the command surface.

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

3. Run the owner health check.

```bash
python scripts/aictl.py project doctor
```

`project doctor` aggregates registered command checks, plan/task/evolution validation, task graph validation, generated-output freshness, context and Codex prompt status, and protected-file checks. It reports explicit `PASS`, `WARN` and `FAIL` findings and does not mutate project-control state.

4. Open the local Web Control Center.

```bash
python scripts/aictl.py web --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765/` in a browser. The Web Control Center is local and loopback-only. Its read views show dashboard, tasks, epics, review state, recent events, generated output, doctor status, registered commands and actions.

5. Build task context and a Codex prompt package.

```bash
python scripts/aictl.py context build --task CTL-12 --write
python scripts/aictl.py codex prompt build --task CTL-12 --with-context
```

The Context Pack and Codex prompt package are generated output. They are read-only context and execution instructions. They do not expand Task scope, allowed files, out-of-scope items or acceptance criteria.

## Task Lifecycle Commands

Only a Task is executable. Initiative and Epic organize work; they are not execution scope.

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

## Bulk Task Import

Use bulk import when several bounded Tasks already have clear scope. Preview first:

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
context.build
codex.prompt.build
task.prepare_for_codex
task.refresh_execution_context
task.submit_for_review
task.close_reviewed
evolution.create_for_task
evolution.accept_change
epic.close_if_complete
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

The Web surface must not directly edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**`. It must not approve tasks, accept tasks, accept evolution changes, or mark documents active without Human Owner approval.

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
```

Then check freshness:

```bash
python scripts/taskctl.py check-generated
python scripts/docctl.py check-generated
python scripts/contextctl.py check-generated
python scripts/evolutionctl.py check-generated
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

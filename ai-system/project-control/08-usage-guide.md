# Project Control Usage Guide

## Status

Draft

## Purpose

This guide explains how to use Project Control Gateway in daily work.

It is practical by design. Use it when you need to decide which CLI owns a change, when a Task is required, how `CODEX_PROMPT.md` fits into execution, or what Codex must never edit manually.

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
planctl.py      Initiative, Epic, project plan
taskctl.py      executable Task, current Task, CODEX_PROMPT.md
docctl.py       documentation registry, document status, docs index
evolutionctl.py AI Development System change proposals
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

## CLI Responsibilities

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
python scripts/docctl.py doc register --path ai-system/project-control/08-usage-guide.md --title "Project Control Usage Guide" --type guide --status planned
python scripts/docctl.py doc status ai-system/project-control/08-usage-guide.md --to draft
python scripts/docctl.py doc status ai-system/project-control/08-usage-guide.md --to review
python scripts/docctl.py doc mark-reviewed ai-system/project-control/08-usage-guide.md --note "Reviewed for project-control consistency."
python scripts/docctl.py validate
python scripts/docctl.py render
python scripts/docctl.py check-generated
```

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

Use this flow for ordinary controlled work:

1. Inspect current status.

```bash
python scripts/planctl.py status
python scripts/taskctl.py status
python scripts/docctl.py status
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
python scripts/taskctl.py task create --epic EPIC-001 --title "Write Project Control Usage Guide" --scope "Create ai-system/project-control/08-usage-guide.md" --allowed-file "ai-system/project-control/08-usage-guide.md" --acceptance "Documentation validation passes"
```

4. Select the Task and build the prompt package.

```bash
python scripts/taskctl.py current set TASK-001
python scripts/taskctl.py prompt build --write
```

5. Execute only the Task scope.

```bash
python scripts/taskctl.py task transition TASK-001 --to in_progress
```

6. Validate and submit for review.

```bash
python scripts/planctl.py validate
python scripts/planctl.py render
python scripts/taskctl.py validate
python scripts/taskctl.py render
python scripts/taskctl.py check-generated
python scripts/docctl.py validate
python scripts/docctl.py render
python scripts/docctl.py check-generated
python scripts/taskctl.py task transition TASK-001 --to in_review
```

7. Wait for Human Owner acceptance.

Do not mark the Task approved, done or archived as accepted unless the Human Owner explicitly accepts the result.

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
python scripts/taskctl.py current set TASK-001
python scripts/taskctl.py prompt build --write
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

`planctl.py` currently supports `render`, but does not expose a `check-generated` command.

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

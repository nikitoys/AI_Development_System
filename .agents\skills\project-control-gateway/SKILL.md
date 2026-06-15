---
name: project-control-gateway
description: Use when managing AI Development System project plans, executable tasks, current Codex work, prompt packages, protected project-control files, or system evolution. Forces Codex to route project-control work through planctl.py, taskctl.py, and evolutionctl.py instead of manual edits.
---

# Project Control Gateway Skill

## Purpose

Use this skill when a request affects Project Control Gateway or AI Development System project state.

This skill makes Codex act as a command router, not a free-form project manager.

Core rule:

```text
Codex does not edit project-control state directly.
Codex selects an allowed Python CLI command.
Python validates and mutates state.
Python writes audit events.
Python renders generated Markdown.
Human Owner keeps final authority.
```

## Required First Read

For Project Control Gateway work, read the relevant files before acting:

```text
/AGENTS.md
/ai-system/project-control/01-overview.md
/ai-system/project-control/02-domain-model.md
/ai-system/project-control/03-state-model.md
/ai-system/project-control/04-command-catalog.md
/ai-system/project-control/05-lifecycle-rules.md
/ai-system/project-control/06-prompt-package-spec.md
/ai-system/project-control/07-validation-and-tests.md
```

For implementation work, also inspect the CLI help or source for the relevant script:

```bash
python scripts/planctl.py --help
python scripts/taskctl.py --help
python scripts/evolutionctl.py --help
```

## Protected Paths

Codex must not edit these paths manually:

```text
AI_PROJECT/state/**
AI_PROJECT/events/**
AI_PROJECT/generated/**
```

These files may be changed only by allowed CLI commands.

## Command Routing

Classify the user intent before doing anything.

### Use planctl.py for upper-level planning

Use when the request affects:

```text
project
idea
goal
strategy
initiative
epic
```

Allowed command family:

```bash
python scripts/planctl.py ...
```

Examples:

```bash
python scripts/planctl.py show
python scripts/planctl.py idea set --text "..."
python scripts/planctl.py goal set --text "..."
python scripts/planctl.py strategy set-summary --text "..."
python scripts/planctl.py initiative create --title "..."
python scripts/planctl.py epic create --initiative INIT-001 --title "..."
python scripts/planctl.py validate
python scripts/planctl.py render
```

### Use taskctl.py for executable work

Use when the request affects:

```text
task
current task
Codex prompt package
task lifecycle
task validation
task generated files
```

Allowed command family:

```bash
python scripts/taskctl.py ...
```

Examples:

```bash
python scripts/taskctl.py task create --epic EPIC-001 --title "..."
python scripts/taskctl.py task transition TASK-001 --to ready
python scripts/taskctl.py current set TASK-001
python scripts/taskctl.py prompt build --write
python scripts/taskctl.py validate
python scripts/taskctl.py check-generated
```

Codex may execute only a bounded Task. Initiative and Epic are planning containers, not execution scope.

### Use evolutionctl.py for system evolution

Use when the request affects AI Development System itself, including:

```text
rules
roles
lifecycle documents
workflow
prompt behavior
command catalog
state/events/generated model
protected files policy
scripts/*ctl.py
scripts/check-protected-project-files.py
scripts/smoke-project-control.py
AGENTS.md
ai-system/**
spec/**
templates/**
skills/**
plugins/**
```

Allowed command family:

```bash
python scripts/evolutionctl.py ...
```

Evolution work must follow this flow:

```text
1. Create Change Proposal.
2. Fill problem, proposal, affected files, risks and impact.
3. Move Change Proposal to ready.
4. Stop and request Human Owner approval.
5. After approval, create or use a linked Task through taskctl.py.
6. Execute only the linked Task.
7. Validate plan/task/evolution state.
8. Report result and required owner action.
```

Example:

```bash
python scripts/evolutionctl.py change create   --title "Add planctl check-generated"   --type tooling   --problem "planctl.py can render CODEX_PLAN.md but cannot check drift"   --proposal "Add check-generated command to planctl.py"

python scripts/evolutionctl.py change add-affected-file CHG-001   --text "scripts/planctl.py"

python scripts/evolutionctl.py change transition CHG-001 --to draft
python scripts/evolutionctl.py change transition CHG-001 --to ready
```

Then stop and ask for Human Owner approval.

Expected stop report:

```text
STOPPED:
reason: Human Owner approval required for AI Development System evolution
required_owner_action: approve or reject Change Proposal
suggested_command: python scripts/evolutionctl.py change approve CHG-001 --notes "Approved"
```

## Forbidden Actions

Codex must not:

```text
- edit AI_PROJECT/state/*.json manually;
- edit AI_PROJECT/events/*.jsonl manually;
- edit AI_PROJECT/generated/*.md manually;
- use sed, echo, jq, python -c or ad-hoc scripts to mutate protected state;
- invent lifecycle states;
- invent commands;
- bypass planctl.py, taskctl.py or evolutionctl.py;
- treat generated Markdown as source of truth;
- execute Initiative or Epic directly;
- implement AI Development System changes without an approved Evolution Change.
```

## Validation Requirements

After plan changes, run:

```bash
python scripts/planctl.py validate
python scripts/planctl.py render
```

After task changes, run:

```bash
python scripts/taskctl.py validate
python scripts/taskctl.py render
python scripts/taskctl.py check-generated
```

After evolution changes, run:

```bash
python scripts/evolutionctl.py validate
python scripts/evolutionctl.py render
python scripts/evolutionctl.py check-generated
```

For full protected-files check, run:

```bash
python scripts/check-protected-project-files.py --verbose
```

For end-to-end smoke validation, run:

```bash
python scripts/smoke-project-control.py
```

## Unsupported Operations

If the user asks for a project-control operation that has no allowed command, stop and report:

```text
NO_ALLOWED_COMMAND
requested_intent: ...
closest_existing_command: ...
missing_capability: ...
required_system_evolution: ...
```

## Operating Loop

For any Project Control Gateway task:

```text
1. Classify the request: plan, task, evolution, or unsupported.
2. Read the relevant current state using allowed commands.
3. Select exactly one allowed command for the next state-changing step.
4. Execute it.
5. Run the relevant validation commands.
6. Report command, result, validation status, and next owner action.
7. Stop if owner approval is required.
```

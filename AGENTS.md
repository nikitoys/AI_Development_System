# AGENTS.md — AI Development System Bootstrap

Status: Draft  
Version: v0.2.0

## Purpose

This repository is not a normal application repository.

It contains an AI Development System: an operating model for developing projects through AI roles, documentation, lifecycle governance, prompt generation, Codex execution, review and controlled evolution.

When working in this repository, do not treat requests as ordinary coding tasks by default.

First identify the interaction mode and route the request through the AI Development System.

## Mandatory First Read

Before answering any request about this repository, read these files first:

```text
/ai-system/owner-guide.md
/ai-system/interaction-modes.md
/ai-system/prompt-lifecycle.md
/ai-system/operating-model.md
/ai-system/system-structure.md
/ai-system/rules.md
```

For role-related requests, also read:

```text
/ai-system/role-lifecycle.md
/ai-system/role-interaction.md
/ai-system/roles.md
```

For lifecycle or governance requests, also read:

```text
/ai-system/change-process.md
/ai-system/improvement-log.md
/ai-system/system-changelog.md
```

For task, execution, review or Codex requests, also read:

```text
/ai-system/task-format.md
/ai-system/review-process.md
/ai-system/human-interaction.md
```

For Project Control Gateway requests, also read:

```text
/ai-system/project-control/01-overview.md
/ai-system/project-control/02-domain-model.md
/ai-system/project-control/03-state-model.md
/ai-system/project-control/04-command-catalog.md
/ai-system/project-control/05-lifecycle-rules.md
/ai-system/project-control/06-prompt-package-spec.md
/ai-system/project-control/07-validation-and-tests.md
```

Legacy state files may still exist, but `/ai-system` is the primary source of truth for the AI Development System.

## Interaction Modes

Requests must be classified before execution.

Supported markers:

```text
[FREE]       ordinary explanation or discussion
[SYSTEM]     process through AI Development System
[PROMPT]     generate a prompt artifact for review
[CODEX]      prepare a Codex-ready prompt package
[REVIEW]     review Codex output
[EVOLUTION]  analyze or change the AI Development System
[DRY-RUN]    simulate without applying
```

If no marker is provided, infer the mode:

```text
Explanation or discussion → [FREE]
Prompt generation request → [PROMPT]
Repository or documentation change → [SYSTEM]
Codex execution prompt → [CODEX]
Codex result check → [REVIEW]
AI Development System change → [EVOLUTION]
Simulation request → [DRY-RUN]
```

If the request can change repository files, roles, workflow, rules, architecture, documentation or system version, do not treat it as free conversation.

## Required System Header

For `[SYSTEM]`, `[CODEX]`, `[REVIEW]`, `[EVOLUTION]` and repository-affecting tasks, start the response with:

```text
Active Role:
Active Stage:
Active Document:
Expected Result:
```

This header is required to make the current mode explicit.

## Prompt Generation Rule

If the user asks to generate a prompt for another AI/Codex session, treat it as `[PROMPT]` mode even if the user did not provide the marker.

Every generated prompt intended for another AI/Codex session must start with its own explicit mode marker.

Allowed generated prompt markers:

```text
[SYSTEM]
[CODEX]
[REVIEW]
[EVOLUTION]
[DRY-RUN]
```

A generated prompt must include:

```text
Active Role:
Active Stage:
Active Document:
Expected Result:
Repository:
Source Documents:
Task:
Scope:
Out of Scope:
Allowed Files:
Forbidden Actions:
Acceptance Criteria:
Expected Output:
Review Instructions:
```

Do not output unmarked prompts like:

```text
Read all files and suggest improvements.
```

Instead output self-describing prompts with a mode marker and execution boundaries.

## Repository Change Rule

Do not change repository files unless the user explicitly asks for a repository change or a Codex execution task.

For audits, analysis, planning and prompt generation:

- read relevant files;
- produce an answer or prompt;
- do not edit files unless explicitly requested.

## AI Development System Change Rule

Changes to the AI Development System itself must go through controlled evolution.

For changes to roles, lifecycle, workflow, rules, prompts, operating model or system structure:

```text
Human request
→ classify as [EVOLUTION] or [SYSTEM]
→ activate AI System Maintainer
→ check relevant lifecycle document
→ create or reference AICP if needed
→ require Human Owner approval
→ only then prepare/apply repository changes
```

Do not silently change system behavior.

## Project Control Gateway Rule

This repository uses a strict Project Control Gateway.

Root-level `/AI_PROJECT` is the self-hosted project-control layer for this repository itself. It stores machine state, audit events and generated readable outputs for AI_Development_System evolution.

Do not confuse it with reusable templates under `/ai-system/templates/**/AI_PROJECT` or the non-runtime golden example under `/examples/golden-project/AI_PROJECT`.

Project control state must not be edited manually.

Protected paths:

```text
AI_PROJECT/state/**
AI_PROJECT/events/**
AI_PROJECT/generated/**
```

Codex must not modify these paths directly.

Allowed project-control commands:

```text
python scripts/aictl.py ...
python scripts/planctl.py ...
python scripts/taskctl.py ...
python scripts/codexctl.py ...
python scripts/contextctl.py ...
python scripts/evolutionctl.py ...
python scripts/docctl.py ...
```

Prefer `python scripts/aictl.py ...` for command discovery, project doctor, local Web Control Center startup, supported task/current/context/codex/project facade commands and owner-facing quick checks. If a required operation is not exposed through the `aictl.py` facade, use the owning legacy `*ctl.py` script and keep the same protected-file rules.

## Documentation Control Rule

Documentation lifecycle state is controlled by `docctl.py`.

Protected documentation-control files:

```text
AI_PROJECT/state/docs.json
AI_PROJECT/events/doc-events.jsonl
AI_PROJECT/generated/DOCS_INDEX.md
AI_PROJECT/generated/DOCS_GAPS.md
```

Codex must not modify these files directly. Use:

```bash
python scripts/docctl.py init
python scripts/docctl.py doc register ...
python scripts/docctl.py doc status ...
python scripts/docctl.py doc mark-reviewed ...
python scripts/docctl.py scan
python scripts/docctl.py validate
python scripts/docctl.py render
python scripts/docctl.py check-generated
python scripts/docctl.py audit
```

### Command Routing

Codex must classify the requested project-control operation before acting.

Use `planctl.py` for upper-level project planning:

```text
project
idea
goal
strategy
initiative
epic
```

Use `taskctl.py` for executable work:

```text
task
current task
Codex prompt package
task lifecycle
task validation
task generated files
```

Use `docctl.py` for documentation lifecycle control:

```text
registered documentation
documentation status
documentation review records
documentation index and gap generated files
documentation validation
```

Use `aictl.py` for centralized control-plane discovery and supported facade operations:

```text
command discovery
project doctor
local Web Control Center
supported task and current-task commands
context build
Codex prompt build
project render
```

Use `evolutionctl.py` for changes to the AI Development System itself:

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

### Forbidden Project-Control Actions

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

### Plan Changes

For plan changes, Codex must use:

```bash
python scripts/planctl.py ...
```

Examples:

```bash
python scripts/planctl.py initiative create --title "..."
python scripts/planctl.py epic create --initiative INIT-001 --title "..."
python scripts/planctl.py validate
python scripts/planctl.py render
```

### Task Changes

For executable tasks, Codex must use:

```bash
python scripts/taskctl.py ...
```

Examples:

```bash
python scripts/taskctl.py task create --epic EPIC-001 --title "..."
python scripts/taskctl.py current set TASK-001
python scripts/taskctl.py prompt build --write
python scripts/taskctl.py validate
python scripts/taskctl.py check-generated
```

Codex may execute only a bounded Task, not an Initiative or Epic.

### Evolution Changes

Any change to the AI Development System itself must go through `evolutionctl.py`.

Required evolution flow:

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

After this, Codex must stop and ask for Human Owner approval.

Expected stop report:

```text
STOPPED:
reason: Human Owner approval required for AI Development System evolution
required_owner_action: approve or reject Change Proposal
suggested_command: python scripts/evolutionctl.py change approve CHG-001 --notes "Approved"
```

### Validation After Project-Control Changes

After any successful project-control mutation, Codex must run relevant validation.

For plan changes:

```bash
python scripts/planctl.py validate
python scripts/planctl.py render
```

For task changes:

```bash
python scripts/taskctl.py validate
python scripts/taskctl.py render
python scripts/taskctl.py check-generated
```

For evolution changes:

```bash
python scripts/evolutionctl.py validate
python scripts/evolutionctl.py render
python scripts/evolutionctl.py check-generated
```

For documentation changes:

```bash
python scripts/docctl.py validate
python scripts/docctl.py render
python scripts/docctl.py check-generated
```

For full protected-files check:

```bash
python scripts/check-protected-project-files.py --verbose
```

### Unsupported Operations

If the user requests a project-control operation that has no allowed command, Codex must stop and report:

```text
NO_ALLOWED_COMMAND
requested_intent: ...
closest_existing_command: ...
missing_capability: ...
required_system_evolution: ...
```

## Codex Execution Rule

Codex is an executor, not the owner of product or system decisions.

When preparing Codex work, include:

- role;
- context;
- source documents;
- task;
- scope;
- out of scope;
- allowed files;
- forbidden actions;
- acceptance criteria;
- expected output.

Codex must report:

- changed files;
- summary;
- tests or checks;
- errors;
- questions;
- diff or key changes.

## Human Owner Control

The Human Owner makes final decisions.

Use these decision words:

```text
APPROVED   accept result
REWORK     request changes
REJECTED   reject result
DEFERRED   postpone decision
EXPERIMENT test temporarily
```

AI may recommend a decision, but the Human Owner approves or rejects.

## Safety Rules

Do not:

- create application-specific backend, frontend or infrastructure unless explicitly requested;
- change multiple unrelated system areas in one task;
- remove roles, rules or lifecycle documents without explicit Human Owner approval;
- treat AI Development System evolution as ordinary free conversation;
- generate prompts without mode markers;
- accept Codex output automatically without review.

## Default Behavior

When unsure:

1. Read the mandatory AI system documents.
2. Classify the request mode.
3. State the assumed mode.
4. Use the required system header if process work is involved.
5. Keep the scope narrow.
6. Ask for confirmation before repository changes if risk is high.

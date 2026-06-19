# Project Control Command Catalog

## Status

Draft

## Purpose

This document defines the allowed command interface for Project Control Gateway.

The command catalog is the formal boundary between AI reasoning and project state mutation.

AI agents must not freely edit project control files. They may only map Human Owner intent to one of the allowed commands defined in this catalog.

Core rule:

```text
Owner intent -> allowed command -> Python validation -> state mutation -> audit event -> generated Markdown
```

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

`docctl.py` owns `AI_PROJECT/state/docs.json`, `AI_PROJECT/events/doc-events.jsonl`, `AI_PROJECT/generated/DOCS_INDEX.md` and `AI_PROJECT/generated/DOCS_GAPS.md`. It records current document content hashes, reviewed content hashes and declared-status metadata. Generated documentation gaps must be repaired through source documents or `docctl.py`, not by editing generated Markdown.

Current context-control commands include:

```bash
python scripts/contextctl.py status
python scripts/contextctl.py index build
python scripts/contextctl.py search --query <text>
python scripts/contextctl.py pack build --task <TASK_ID> --write
python scripts/contextctl.py pack build --query <text> --write
python scripts/contextctl.py validate
python scripts/contextctl.py render
python scripts/contextctl.py check-generated
python scripts/contextctl.py audit --last 20
```

`contextctl.py` owns `AI_PROJECT/events/context-events.jsonl`, `AI_PROJECT/generated/CONTEXT_PACK.md` and `AI_PROJECT/generated/CONTEXT_STATUS.md`. It reads `AI_PROJECT/state/docs.json` and `AI_PROJECT/state/tasks.json`, but does not mutate them. Context Packs are generated retrieval output only; they must not be treated as source of truth and must not expand Task scope, allowed files or acceptance criteria.

The command catalog boundary applies to this repository's root `/AI_PROJECT` state. Reusable templates under `/ai-system/templates/**/AI_PROJECT` and the golden project under `/examples/golden-project/AI_PROJECT` are separate documentation/template fixtures unless a bounded task explicitly edits them.

---

# 1. Command Boundary

## Allowed Mutation Path

Project-control state may be changed only through approved gateway commands:

```bash
python scripts/aictl.py ...
python scripts/planctl.py ...
python scripts/taskctl.py ...
python scripts/codexctl.py ...
python scripts/docctl.py ...
python scripts/evolutionctl.py ...
python scripts/contextctl.py ...
```

## Protected Files

The following files are protected:

```text
AI_PROJECT/state/plan.json
AI_PROJECT/events/plan-events.jsonl
AI_PROJECT/generated/CODEX_PLAN.md
```

AI agents must not edit these files manually.

## Forbidden Bypasses

The following actions are forbidden:

```text
- manual JSON edits;
- manual generated Markdown edits;
- manual audit log edits;
- sed/echo/jq mutations against protected files;
- python -c mutations against protected files;
- ad-hoc scripts that mutate protected files;
- lifecycle status changes outside planctl.py;
- creating Epic without an Initiative;
- treating Initiative or Epic as executable scope.
```

If no allowed command exists for an owner request, AI must stop and report:

```text
NO_ALLOWED_COMMAND
requested_intent: ...
closest_existing_command: ...
missing_capability: ...
required_system_evolution: ...
```

---

# 2. Command Classes

Commands are divided into three classes:

```text
Read commands       — inspect state, do not mutate files
Mutation commands   — change state, write audit events, render generated Markdown
Utility commands    — validate, render, audit
```

## Read Commands

Read commands must not:

```text
- increase revision;
- write events;
- modify state;
- render generated files.
```

## Mutation Commands

Mutation commands must:

```text
- validate current state;
- check command preconditions;
- apply exactly one logical mutation;
- increase revision;
- write updated state;
- append an audit event;
- regenerate CODEX_PLAN.md;
- validate final state.
```

## Utility Commands

Utility commands support validation, rendering and audit inspection.

They may read state and generated output. They must not silently mutate semantic project state.

---

# 3. Common Options

All commands may support common options.

## `--root`

Specifies repository/project root.

```bash
python scripts/planctl.py --root . show
```

Default:

```text
.
```

## `--actor`

Specifies the actor written to audit events.

```bash
python scripts/planctl.py --actor codex initiative create --title "..."
```

Default:

```text
human_owner
```

The value may also be read from:

```text
AI_DEV_ACTOR
```

Suggested actor values:

```text
human_owner
chatgpt_orchestrator
codex
system
```

---

# 4. Command Result Rules

## Successful Read Command

A successful read command should print the requested state and exit with code `0`.

## Successful Mutation Command

A successful mutation command should print:

```text
OK: <command> revision <before> -> <after>
```

It may also print the created entity ID when applicable:

```text
Created: INIT-001
Created: EPIC-001
```

## Failed Command

A failed command should:

```text
- not change state;
- not append success audit event;
- not render generated Markdown from invalid state;
- print explicit error;
- exit with non-zero status.
```

Example:

```text
ERROR: ENTITY_NOT_FOUND: INIT-999
```

---

# 5. Error Codes

The CLI should use stable error names.

Suggested errors:

```text
PLAN_NOT_INITIALIZED
PLAN_ALREADY_EXISTS
INVALID_JSON
VALIDATION_FAILED
ENTITY_NOT_FOUND
DUPLICATE_ID
INVALID_STATUS
INVALID_STATUS_TRANSITION
ARCHIVED_ENTITY_IS_IMMUTABLE
CANNOT_CREATE_EPIC_UNDER_ARCHIVED_INITIATIVE
CANNOT_ACTIVATE_EPIC_UNDER_ARCHIVED_INITIATIVE
INITIATIVE_HAS_ACTIVE_EPICS
INDEX_OUT_OF_RANGE
MISSING_REQUIRED_ARGUMENT
PROJECT_CONTROL_BYPASS_DETECTED
```

Errors should be readable by both humans and AI agents.

---

# 6. State and Event Files

The MVP command catalog operates on:

```text
AI_PROJECT/state/plan.json
AI_PROJECT/events/plan-events.jsonl
AI_PROJECT/generated/CODEX_PLAN.md
```

## State File

```text
AI_PROJECT/state/plan.json
```

Stores:

```text
Project
Idea
Goal
Strategy
Initiative[]
Epic[]
```

## Event File

```text
AI_PROJECT/events/plan-events.jsonl
```

Stores append-only audit events.

## Generated File

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

Stores a generated Markdown view of the plan.

---

# 7. Mutation Transaction

Every mutation command must follow this transaction model:

```text
1. Load current state.
2. Validate current state.
3. Parse command arguments.
4. Check preconditions.
5. Apply mutation in memory.
6. Increase revision.
7. Validate new state.
8. Atomically write state.
9. Append audit event.
10. Render CODEX_PLAN.md.
11. Report result.
```

If any step fails, the command must stop and preserve previous state.

---

# 8. Root Commands

## 8.1 `init`

Initializes plan control state.

### Syntax

```bash
python scripts/planctl.py init
python scripts/planctl.py init --project-name "AI Development System"
python scripts/planctl.py init --project-id PROJECT-001 --project-name "AI Development System"
python scripts/planctl.py init --force
```

### Purpose

Creates the initial plan control files.

### Input

```text
project_id
project_name
force
```

### Preconditions

```text
- AI_PROJECT/state/plan.json does not exist
```

If `--force` is provided, existing plan state may be overwritten.

### State Changes

Creates:

```text
AI_PROJECT/state/plan.json
```

Initial state includes:

```text
schema_version
revision
project
idea
goal
strategy
initiatives
epics
```

Initial revision:

```text
0
```

### Events Written

```text
plan.init
```

### Generated Files Updated

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

### Possible Errors

```text
PLAN_ALREADY_EXISTS
VALIDATION_FAILED
```

---

## 8.2 `show`

Shows a short plan summary.

### Syntax

```bash
python scripts/planctl.py show
python scripts/planctl.py show --json
```

### Purpose

Displays current project plan summary.

### Preconditions

```text
- plan.json exists
- plan.json is valid
```

### State Changes

None.

### Events Written

None.

### Generated Files Updated

None.

### Possible Errors

```text
PLAN_NOT_INITIALIZED
INVALID_JSON
VALIDATION_FAILED
```

---

## 8.3 `status`

Shows file paths and validation status.

### Syntax

```bash
python scripts/planctl.py status
```

### Purpose

Helps Human Owner or Codex inspect whether plan control files exist and validate correctly.

### State Changes

None.

### Events Written

None.

### Generated Files Updated

None.

### Possible Errors

```text
PLAN_NOT_INITIALIZED
INVALID_JSON
```

---

## 8.4 `validate`

Validates `plan.json`.

### Syntax

```bash
python scripts/planctl.py validate
```

### Purpose

Checks that current plan state is valid.

### Validation Checks

```text
- required top-level fields exist;
- schema_version is supported;
- revision is a non-negative integer;
- project status is valid;
- initiatives is a list;
- epics is a list;
- Initiative IDs are unique;
- Epic IDs are unique;
- statuses are valid;
- Epic parent Initiative exists;
- active Epic is not under archived Initiative.
```

### State Changes

None.

### Events Written

None.

### Generated Files Updated

None.

### Possible Errors

```text
VALIDATION_FAILED
INVALID_JSON
PLAN_NOT_INITIALIZED
```

---

## 8.5 `render`

Renders generated Markdown from state.

### Syntax

```bash
python scripts/planctl.py render
```

### Purpose

Regenerates:

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

from:

```text
AI_PROJECT/state/plan.json
```

### Preconditions

```text
- plan.json exists
- plan.json is valid
```

### State Changes

None to semantic state.

### Events Written

None.

### Generated Files Updated

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

### Possible Errors

```text
PLAN_NOT_INITIALIZED
INVALID_JSON
VALIDATION_FAILED
```

---

## 8.6 `audit`

Shows audit events.

### Syntax

```bash
python scripts/planctl.py audit
python scripts/planctl.py audit --last 20
python scripts/planctl.py audit --entity INIT-001
```

### Purpose

Displays plan control mutation history.

### State Changes

None.

### Events Written

None.

### Generated Files Updated

None.

### Possible Errors

```text
INVALID_EVENT_LINE
```

---

# 9. Idea Commands

## 9.1 `idea show`

Shows current idea text.

### Syntax

```bash
python scripts/planctl.py idea show
```

### Purpose

Reads `plan.idea.text`.

### State Changes

None.

### Events Written

None.

### Possible Errors

```text
PLAN_NOT_INITIALIZED
INVALID_JSON
VALIDATION_FAILED
```

---

## 9.2 `idea set`

Sets project idea text.

### Syntax

```bash
python scripts/planctl.py idea set --text "Create a controlled AI-assisted development system."
```

### Purpose

Updates the project idea.

### Input

```text
text
```

### Preconditions

```text
- text is provided
- plan.json exists
- current state is valid
```

### State Changes

```text
plan.idea.text = text
plan.idea.updated_at = now
plan.revision += 1
plan.project.updated_at = now
```

### Events Written

```text
idea.set
```

### Event Payload

```json
{
  "text": "..."
}
```

### Generated Files Updated

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

### Possible Errors

```text
PLAN_NOT_INITIALIZED
MISSING_REQUIRED_ARGUMENT
VALIDATION_FAILED
```

---

# 10. Goal Commands

## 10.1 `goal show`

Shows current project goal and success criteria.

### Syntax

```bash
python scripts/planctl.py goal show
```

### State Changes

None.

### Events Written

None.

---

## 10.2 `goal set`

Sets project goal text.

### Syntax

```bash
python scripts/planctl.py goal set --text "Build Project Control Gateway."
```

### Input

```text
text
```

### Preconditions

```text
- text is provided
- plan.json exists
- current state is valid
```

### State Changes

```text
plan.goal.text = text
plan.goal.updated_at = now
plan.revision += 1
plan.project.updated_at = now
```

### Events Written

```text
goal.set
```

### Event Payload

```json
{
  "text": "..."
}
```

### Generated Files Updated

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

### Possible Errors

```text
PLAN_NOT_INITIALIZED
MISSING_REQUIRED_ARGUMENT
VALIDATION_FAILED
```

---

## 10.3 `goal add-criterion`

Adds a success criterion.

### Syntax

```bash
python scripts/planctl.py goal add-criterion --text "Every mutation writes an audit event."
```

### Input

```text
text
```

### Preconditions

```text
- text is provided
- plan.goal.success_criteria is a list
```

### State Changes

```text
append text to plan.goal.success_criteria
plan.goal.updated_at = now
plan.revision += 1
```

### Events Written

```text
goal.add_criterion
```

### Event Payload

```json
{
  "text": "..."
}
```

### Generated Files Updated

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

### Possible Errors

```text
MISSING_REQUIRED_ARGUMENT
VALIDATION_FAILED
```

---

## 10.4 `goal remove-criterion`

Removes a success criterion by 1-based index.

### Syntax

```bash
python scripts/planctl.py goal remove-criterion --index 1
```

### Input

```text
index
```

### Preconditions

```text
- index is provided
- index is within range
```

### State Changes

```text
remove item from plan.goal.success_criteria
plan.goal.updated_at = now
plan.revision += 1
```

### Events Written

```text
goal.remove_criterion
```

### Event Payload

```json
{
  "index": 1
}
```

### Generated Files Updated

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

### Possible Errors

```text
INDEX_OUT_OF_RANGE
VALIDATION_FAILED
```

---

# 11. Strategy Commands

## 11.1 `strategy show`

Shows strategy summary, principles and constraints.

### Syntax

```bash
python scripts/planctl.py strategy show
```

### State Changes

None.

### Events Written

None.

---

## 11.2 `strategy set-summary`

Sets strategy summary.

### Syntax

```bash
python scripts/planctl.py strategy set-summary --text "Implement CLI core first, then add Codex plugin."
```

### Input

```text
text
```

### State Changes

```text
plan.strategy.summary = text
plan.strategy.updated_at = now
plan.revision += 1
```

### Events Written

```text
strategy.set_summary
```

### Generated Files Updated

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

---

## 11.3 `strategy add-principle`

Adds a strategy principle.

### Syntax

```bash
python scripts/planctl.py strategy add-principle --text "Python validates project state."
```

### State Changes

```text
append text to plan.strategy.principles
plan.strategy.updated_at = now
plan.revision += 1
```

### Events Written

```text
strategy.add_principle
```

### Generated Files Updated

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

---

## 11.4 `strategy remove-principle`

Removes a strategy principle by 1-based index.

### Syntax

```bash
python scripts/planctl.py strategy remove-principle --index 1
```

### Preconditions

```text
- index is within range
```

### State Changes

```text
remove item from plan.strategy.principles
plan.strategy.updated_at = now
plan.revision += 1
```

### Events Written

```text
strategy.remove_principle
```

### Possible Errors

```text
INDEX_OUT_OF_RANGE
```

---

## 11.5 `strategy add-constraint`

Adds a strategy constraint.

### Syntax

```bash
python scripts/planctl.py strategy add-constraint --text "No automatic merge in MVP."
```

### State Changes

```text
append text to plan.strategy.constraints
plan.strategy.updated_at = now
plan.revision += 1
```

### Events Written

```text
strategy.add_constraint
```

---

## 11.6 `strategy remove-constraint`

Removes a strategy constraint by 1-based index.

### Syntax

```bash
python scripts/planctl.py strategy remove-constraint --index 1
```

### Preconditions

```text
- index is within range
```

### State Changes

```text
remove item from plan.strategy.constraints
plan.strategy.updated_at = now
plan.revision += 1
```

### Events Written

```text
strategy.remove_constraint
```

### Possible Errors

```text
INDEX_OUT_OF_RANGE
```

---

# 12. Initiative Commands

## 12.1 `initiative list`

Lists initiatives.

### Syntax

```bash
python scripts/planctl.py initiative list
python scripts/planctl.py initiative list --json
```

### Purpose

Displays all initiatives.

### State Changes

None.

### Events Written

None.

---

## 12.2 `initiative show`

Shows one initiative.

### Syntax

```bash
python scripts/planctl.py initiative show INIT-001
```

### Input

```text
initiative_id
```

### Preconditions

```text
- initiative exists
```

### State Changes

None.

### Events Written

None.

### Possible Errors

```text
ENTITY_NOT_FOUND
```

---

## 12.3 `initiative create`

Creates an Initiative.

### Syntax

```bash
python scripts/planctl.py initiative create --title "Project Control Gateway"
python scripts/planctl.py initiative create --title "Project Control Gateway" --summary "Create Python-controlled project state."
python scripts/planctl.py initiative create --title "Project Control Gateway" --priority 1 --status active
```

### Input

```text
title
summary
priority
status
```

### Defaults

```text
summary = ""
priority = 1
status = active
```

### Preconditions

```text
- title is provided
- status is valid
- generated Initiative ID is unique
```

### State Changes

Adds new item to:

```text
plan.initiatives[]
```

New Initiative fields:

```text
id
title
status
summary
priority
order
created_at
updated_at
```

### ID Generation

```text
INIT-001
INIT-002
INIT-003
```

### Events Written

```text
initiative.create
```

### Event Payload

```json
{
  "title": "...",
  "summary": "...",
  "priority": 1,
  "status": "active"
}
```

### Generated Files Updated

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

### Possible Errors

```text
MISSING_REQUIRED_ARGUMENT
INVALID_STATUS
VALIDATION_FAILED
```

---

## 12.4 `initiative rename`

Renames an Initiative.

### Syntax

```bash
python scripts/planctl.py initiative rename INIT-001 --title "New title"
```

### Input

```text
initiative_id
title
```

### Preconditions

```text
- Initiative exists
- Initiative is not archived
- title is provided
```

### State Changes

```text
initiative.title = title
initiative.updated_at = now
plan.revision += 1
```

### Events Written

```text
initiative.rename
```

### Event Payload

```json
{
  "title": "..."
}
```

### Generated Files Updated

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

### Possible Errors

```text
ENTITY_NOT_FOUND
ARCHIVED_ENTITY_IS_IMMUTABLE
MISSING_REQUIRED_ARGUMENT
```

---

## 12.5 `initiative summary`

Updates Initiative summary.

### Syntax

```bash
python scripts/planctl.py initiative summary INIT-001 --text "Create a Python-controlled state layer."
```

### Preconditions

```text
- Initiative exists
- Initiative is not archived
- text is provided
```

### State Changes

```text
initiative.summary = text
initiative.updated_at = now
plan.revision += 1
```

### Events Written

```text
initiative.summary
```

### Generated Files Updated

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

---

## 12.6 `initiative status`

Changes Initiative status.

### Syntax

```bash
python scripts/planctl.py initiative status INIT-001 --to planned
python scripts/planctl.py initiative status INIT-001 --to active
python scripts/planctl.py initiative status INIT-001 --to archived
python scripts/planctl.py initiative status INIT-001 --to archived --force
```

### Input

```text
initiative_id
to
force
```

### Preconditions

```text
- Initiative exists
- target status is valid
- transition is allowed
```

### Additional Archive Rule

An Initiative cannot be archived if it has active child Epics unless `--force` is provided.

Blocking child Epic statuses:

```text
proposed
planned
active
blocked
```

Inactive child Epic statuses:

```text
done
deferred
archived
```

If `--force` is provided, active child Epics may be archived by the command.

### State Changes

```text
initiative.status = to
initiative.updated_at = now
plan.revision += 1
```

If `--force` is used for archiving:

```text
child epic.status = archived
child epic.updated_at = now
```

### Events Written

```text
initiative.status
```

### Event Payload

```json
{
  "to": "archived",
  "force": false
}
```

### Generated Files Updated

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

### Possible Errors

```text
ENTITY_NOT_FOUND
INVALID_STATUS
INVALID_STATUS_TRANSITION
INITIATIVE_HAS_ACTIVE_EPICS
VALIDATION_FAILED
```

---

## 12.7 `initiative archive`

Archives an Initiative.

### Syntax

```bash
python scripts/planctl.py initiative archive INIT-001
python scripts/planctl.py initiative archive INIT-001 --force
```

### Purpose

Shortcut for:

```bash
python scripts/planctl.py initiative status INIT-001 --to archived
```

### Preconditions

Same as `initiative status --to archived`.

### Events Written

```text
initiative.status
```

or future stable event name:

```text
initiative.archive
```

### Possible Errors

Same as `initiative status`.

---

# 13. Epic Commands

## 13.1 `epic list`

Lists Epics.

### Syntax

```bash
python scripts/planctl.py epic list
python scripts/planctl.py epic list --initiative INIT-001
python scripts/planctl.py epic list --json
```

### Purpose

Displays all Epics or Epics under a specific Initiative.

### State Changes

None.

### Events Written

None.

---

## 13.2 `epic show`

Shows one Epic.

### Syntax

```bash
python scripts/planctl.py epic show EPIC-001
```

### Input

```text
epic_id
```

### Preconditions

```text
- Epic exists
```

### State Changes

None.

### Events Written

None.

### Possible Errors

```text
ENTITY_NOT_FOUND
```

---

## 13.3 `epic create`

Creates an Epic under an Initiative.

### Syntax

```bash
python scripts/planctl.py epic create --initiative INIT-001 --title "Plan Control CLI"
python scripts/planctl.py epic create --initiative INIT-001 --title "Plan Control CLI" --summary "Manage plan through Python."
python scripts/planctl.py epic create --initiative INIT-001 --title "Plan Control CLI" --priority 1 --status planned
```

### Input

```text
initiative
title
summary
priority
status
```

### Defaults

```text
summary = ""
priority = 1
status = planned
```

### Preconditions

```text
- title is provided
- Initiative exists
- Initiative is not archived
- status is valid
- generated Epic ID is unique
```

### State Changes

Adds new item to:

```text
plan.epics[]
```

New Epic fields:

```text
id
initiative_id
title
status
summary
priority
order
created_at
updated_at
```

### ID Generation

```text
EPIC-001
EPIC-002
EPIC-003
```

### Events Written

```text
epic.create
```

### Event Payload

```json
{
  "initiative_id": "INIT-001",
  "title": "...",
  "summary": "...",
  "priority": 1,
  "status": "planned"
}
```

### Generated Files Updated

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

### Possible Errors

```text
ENTITY_NOT_FOUND
CANNOT_CREATE_EPIC_UNDER_ARCHIVED_INITIATIVE
INVALID_STATUS
MISSING_REQUIRED_ARGUMENT
VALIDATION_FAILED
```

---

## 13.4 `epic rename`

Renames an Epic.

### Syntax

```bash
python scripts/planctl.py epic rename EPIC-001 --title "New epic title"
```

### Input

```text
epic_id
title
```

### Preconditions

```text
- Epic exists
- Epic is not archived
- title is provided
```

### State Changes

```text
epic.title = title
epic.updated_at = now
plan.revision += 1
```

### Events Written

```text
epic.rename
```

### Generated Files Updated

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

### Possible Errors

```text
ENTITY_NOT_FOUND
ARCHIVED_ENTITY_IS_IMMUTABLE
MISSING_REQUIRED_ARGUMENT
```

---

## 13.5 `epic summary`

Updates Epic summary.

### Syntax

```bash
python scripts/planctl.py epic summary EPIC-001 --text "Manage plan through strict Python CLI."
```

### Preconditions

```text
- Epic exists
- Epic is not archived
- text is provided
```

### State Changes

```text
epic.summary = text
epic.updated_at = now
plan.revision += 1
```

### Events Written

```text
epic.summary
```

### Generated Files Updated

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

### Possible Errors

```text
ENTITY_NOT_FOUND
ARCHIVED_ENTITY_IS_IMMUTABLE
MISSING_REQUIRED_ARGUMENT
```

---

## 13.6 `epic status`

Changes Epic status.

### Syntax

```bash
python scripts/planctl.py epic status EPIC-001 --to planned
python scripts/planctl.py epic status EPIC-001 --to active
python scripts/planctl.py epic status EPIC-001 --to blocked
python scripts/planctl.py epic status EPIC-001 --to done
python scripts/planctl.py epic status EPIC-001 --to archived
```

### Input

```text
epic_id
to
```

### Preconditions

```text
- Epic exists
- target status is valid
- transition is allowed
- parent Initiative exists
```

### Parent Rule

An Epic cannot become active/planned/proposed/blocked under an archived Initiative.

Allowed Epic statuses under archived Initiative:

```text
done
deferred
archived
```

### State Changes

```text
epic.status = to
epic.updated_at = now
plan.revision += 1
```

### Events Written

```text
epic.status
```

### Event Payload

```json
{
  "to": "active"
}
```

### Generated Files Updated

```text
AI_PROJECT/generated/CODEX_PLAN.md
```

### Possible Errors

```text
ENTITY_NOT_FOUND
INVALID_STATUS
INVALID_STATUS_TRANSITION
CANNOT_ACTIVATE_EPIC_UNDER_ARCHIVED_INITIATIVE
VALIDATION_FAILED
```

---

## 13.7 `epic archive`

Archives an Epic.

### Syntax

```bash
python scripts/planctl.py epic archive EPIC-001
```

### Purpose

Shortcut for:

```bash
python scripts/planctl.py epic status EPIC-001 --to archived
```

### Preconditions

Same as `epic status --to archived`.

### Events Written

```text
epic.status
```

or future stable event name:

```text
epic.archive
```

### Possible Errors

Same as `epic status`.

---

# 14. Status Model

The MVP uses the same statuses for Initiative and Epic.

## Statuses

```text
proposed
planned
active
blocked
done
deferred
archived
```

## Transition Rules

```text
proposed -> planned / active / deferred / archived
planned  -> active / blocked / deferred / archived
active   -> blocked / done / deferred / archived
blocked  -> active / deferred / archived
done     -> archived
deferred -> planned / active / archived
archived -> no outgoing transitions
```

## Status Meaning

| Status     | Meaning                           |
| ---------- | --------------------------------- |
| `proposed` | Suggested but not planned         |
| `planned`  | Accepted into plan but not active |
| `active`   | Currently being pursued           |
| `blocked`  | Cannot progress due to blocker    |
| `done`     | Completed                         |
| `deferred` | Intentionally postponed           |
| `archived` | Closed and inactive               |

## Immutable Archived Rule

Archived entities should be treated as immutable for content mutation.

Forbidden for archived entities:

```text
rename
summary update
activation without explicit future restore command
```

---

# 15. Event Naming

Command names and event names should be stable.

## MVP Event Names

```text
plan.init

idea.set

goal.set
goal.add_criterion
goal.remove_criterion

strategy.set_summary
strategy.add_principle
strategy.remove_principle
strategy.add_constraint
strategy.remove_constraint

initiative.create
initiative.rename
initiative.summary
initiative.status

epic.create
epic.rename
epic.summary
epic.status
```

Future versions may add shortcut-specific event names:

```text
initiative.archive
epic.archive
```

But shortcuts may also reuse the status event if they are implemented as status transitions.

---

# 16. Command-to-State Matrix

| Command                      |     Mutates State | Writes Event | Renders Markdown |
| ---------------------------- | ----------------: | -----------: | ---------------: |
| `init`                       |               Yes |          Yes |              Yes |
| `show`                       |                No |           No |               No |
| `status`                     |                No |           No |               No |
| `validate`                   |                No |           No |               No |
| `render`                     | No semantic state |           No |              Yes |
| `audit`                      |                No |           No |               No |
| `idea set`                   |               Yes |          Yes |              Yes |
| `goal set`                   |               Yes |          Yes |              Yes |
| `goal add-criterion`         |               Yes |          Yes |              Yes |
| `goal remove-criterion`      |               Yes |          Yes |              Yes |
| `strategy set-summary`       |               Yes |          Yes |              Yes |
| `strategy add-principle`     |               Yes |          Yes |              Yes |
| `strategy remove-principle`  |               Yes |          Yes |              Yes |
| `strategy add-constraint`    |               Yes |          Yes |              Yes |
| `strategy remove-constraint` |               Yes |          Yes |              Yes |
| `initiative create`          |               Yes |          Yes |              Yes |
| `initiative rename`          |               Yes |          Yes |              Yes |
| `initiative summary`         |               Yes |          Yes |              Yes |
| `initiative status`          |               Yes |          Yes |              Yes |
| `initiative archive`         |               Yes |          Yes |              Yes |
| `epic create`                |               Yes |          Yes |              Yes |
| `epic rename`                |               Yes |          Yes |              Yes |
| `epic summary`               |               Yes |          Yes |              Yes |
| `epic status`                |               Yes |          Yes |              Yes |
| `epic archive`               |               Yes |          Yes |              Yes |

---

# 17. AI Command Selection Rules

When operating under Project Control Gateway, AI must follow this loop:

```text
1. Understand Human Owner intent.
2. Check whether the intent maps to an allowed command.
3. If arguments are missing, ask for them.
4. Execute exactly one logical command.
5. Report the result.
6. Stop unless the owner requested the next command.
```

AI must not perform hidden multi-step project changes unless a single allowed command explicitly supports them.

## Example: Valid Mapping

Owner says:

```text
Create an Epic for plan control CLI under Project Control Gateway.
```

AI should map to:

```bash
python scripts/planctl.py epic create --initiative INIT-001 --title "Plan Control CLI"
```

Only if `INIT-001` is known.

If Initiative ID is unknown, AI should first use:

```bash
python scripts/planctl.py initiative list
```

## Example: Missing Command

Owner says:

```text
Approve this task for Codex execution.
```

Approval and close actions exist, but they are owner-gated.

AI must not self-approve. If Human Owner approval is missing, AI must stop or report the owner action needed:

```text
STOPPED:
reason: Human Owner approval required before task approval/close
required_owner_action: provide APPROVED decision and approval notes, or request rework
suggested_command: python scripts/aictl.py workflow run task.close_reviewed --task <TASK> --notes "APPROVED by Human Owner" --confirm
```

---

# 18. Additional Command Domains

The owner-facing facade uses:

```bash
python scripts/aictl.py <domain> <command>
```

Implemented facade/domain areas include:

```text
command
workflow
task
current
epic
context
codex
project
web
```

The legacy domain CLIs remain the compatibility layer and source of domain-specific validation:

```text
planctl.py
taskctl.py
codexctl.py
docctl.py
evolutionctl.py
contextctl.py
```

Future domains such as execution sessions, review records, QA records, decision records and release records require approved evolution before implementation.

## Task Commands

```text
task create
task show
task list
task update-summary
task update-description
task set-scope
task set-out-of-scope
task set-allowed-files
task add-acceptance-criterion
task transition
task approve
task archive
task import
```

## Current Task Commands

```text
current show
current set
current clear
```

## Prompt Commands

```text
prompt build --task <TASK_ID>
prompt show --task <TASK_ID>
prompt validate --task <TASK_ID>
```

## Context Commands

```text
context status
context index build
context search --query <text>
context pack build --task <TASK_ID>
context pack build --query <text>
context validate
context render
context check-generated
context audit
```

Current implementation entry point:

```bash
python scripts/contextctl.py ...
```

Context commands build deterministic, derived Context Packs from registered documentation and optional Task context. They do not create source state, do not use vector search or external APIs, and do not change the Task execution contract.

## Future Execution Commands

```text
execution start --task <TASK_ID>
execution finish --task <TASK_ID>
execution fail --task <TASK_ID>
```

## Future Review Commands

```text
review open --task <TASK_ID>
review finding add --review <REV_ID>
review approve --review <REV_ID>
review request-changes --review <REV_ID>
review close --review <REV_ID>
```

## Future QA Commands

```text
qa record --task <TASK_ID>
qa pass --task <TASK_ID>
qa fail --task <TASK_ID>
qa waive --task <TASK_ID>
```

## Future Decision Commands

```text
decision propose
decision accept
decision reject
decision supersede
decision archive
```

## Future Change Commands

```text
change propose
change approve
change apply
change reject
change archive
```

---

# 19. MVP Success Criteria

The command catalog MVP is successful when:

```text
- all plan changes are represented as explicit commands;
- plan.json is never edited manually;
- each mutation increases revision;
- each mutation writes an audit event;
- CODEX_PLAN.md is generated from plan.json;
- invalid transitions fail;
- missing parent references fail;
- Codex can map plan-related owner intent to allowed commands;
- unsupported intents produce NO_ALLOWED_COMMAND.
```

---

# Summary

This command catalog defines the first strict command surface for Project Control Gateway.

The first controlled domain is plan management:

```text
Project
Idea
Goal
Strategy
Initiative
Epic
```

The allowed mutation path is:

```bash
python scripts/planctl.py ...
```

The core operating model is:

```text
AI maps intent to command.
Python validates command.
Python mutates state.
Python writes audit event.
Python renders Markdown.
Human Owner keeps final authority.
```

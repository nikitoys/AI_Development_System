# Project Control Lifecycle Rules

## Status

Draft

## Purpose

This document defines lifecycle rules for Project Control Gateway.

Lifecycle rules describe:

```text
- which statuses are allowed;
- which transitions are allowed;
- which entities can be executed;
- which transitions require validation;
- which transitions require Human Owner approval;
- when AI/Codex must stop;
- how Plan, Task and Evolution lifecycles relate to each other.
```

The goal is to prevent AI agents from changing project state freely or treating planning containers as executable work.

## Core Principle

```text
AI does not decide lifecycle state by itself.
AI invokes an allowed command.
Python validates lifecycle transition.
Human Owner keeps final authority over approval and acceptance.
```

## Controlled Lifecycles

Project Control Gateway has three main lifecycle domains:

```text
Plan Lifecycle
  Initiative
  Epic

Task Lifecycle
  Task
  Current Task
  Prompt Package

Evolution Lifecycle
  Change Proposal
  System Evolution
```

Current implemented CLIs:

```text
scripts/planctl.py
scripts/taskctl.py
```

Future planned CLI:

```text
scripts/evolutionctl.py
```

---

# 1. Global Lifecycle Rules

## 1.1 State Must Change Only Through CLI

Protected state must not be changed manually.

Protected files:

```text
AI_PROJECT/state/**
AI_PROJECT/events/**
AI_PROJECT/generated/**
```

Allowed mutation path:

```bash
python scripts/planctl.py ...
python scripts/taskctl.py ...
python scripts/evolutionctl.py ...
```

`evolutionctl.py` is planned for future system evolution control.

## 1.2 Generated Markdown Is Not State

Generated Markdown must not define lifecycle state.

Generated files are readable views only:

```text
AI_PROJECT/generated/CODEX_PLAN.md
AI_PROJECT/generated/CODEX_TASKS.md
AI_PROJECT/generated/CODEX_CURRENT.md
AI_PROJECT/generated/CODEX_PROMPT.md
```

If generated Markdown is stale, it must be regenerated through CLI.

## 1.3 Planning Containers Are Not Executable

The following entities are not executable:

```text
Project
Idea
Goal
Strategy
Initiative
Epic
Change Proposal
Decision
Review
QA Result
Release
```

Only `Task` is executable.

## 1.4 Parent Must Exist Before Child

Child entities must reference existing parents.

```text
Epic.initiative_id -> Initiative.id
Task.epic_id       -> Epic.id
```

Invalid parent references must fail validation.

## 1.5 Archived Entities Are Inactive

Archived entities are terminal or near-terminal.

General rule:

```text
archived -> no outgoing transitions
```

Archived entities should not be renamed, edited, activated or used as parents for active work unless a future explicit restore command is introduced.

---

# 2. Plan Lifecycle

Plan lifecycle applies to:

```text
Initiative
Epic
```

It is currently controlled by:

```bash
python scripts/planctl.py ...
```

## 2.1 Plan Statuses

Allowed statuses:

```text
proposed
planned
active
blocked
done
deferred
archived
```

## 2.2 Status Meaning

| Status     | Meaning                                        |
| ---------- | ---------------------------------------------- |
| `proposed` | Suggested but not yet accepted into the plan   |
| `planned`  | Accepted into the plan but not actively worked |
| `active`   | Currently being pursued                        |
| `blocked`  | Cannot progress because of a blocker           |
| `done`     | Completed                                      |
| `deferred` | Intentionally postponed                        |
| `archived` | Closed and inactive                            |

## 2.3 Allowed Plan Transitions

```text
proposed -> planned
proposed -> active
proposed -> deferred
proposed -> archived

planned -> active
planned -> blocked
planned -> deferred
planned -> archived

active -> blocked
active -> done
active -> deferred
active -> archived

blocked -> active
blocked -> deferred
blocked -> archived

done -> archived

deferred -> planned
deferred -> active
deferred -> archived

archived -> no outgoing transitions
```

## 2.4 Initiative Lifecycle Rules

An Initiative is a strategic planning container.

It may contain many Epics:

```text
Initiative
└── Epic[]
```

An Initiative must not be treated as executable scope.

Allowed commands:

```bash
python scripts/planctl.py initiative create --title "..."
python scripts/planctl.py initiative status INIT-001 --to active
python scripts/planctl.py initiative archive INIT-001
```

## 2.5 Initiative Archive Rule

An Initiative must not be archived while it has active child Epics unless the command explicitly supports forced archival.

Active child Epic statuses:

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

Expected behavior:

```text
If active child Epics exist:
  initiative archive -> fail

If --force is provided:
  child Epics may be archived by the command
```

## 2.6 Epic Lifecycle Rules

An Epic is a delivery planning container.

It belongs to exactly one Initiative:

```text
Epic.initiative_id -> Initiative.id
```

An Epic must not be treated as executable scope.

Allowed commands:

```bash
python scripts/planctl.py epic create --initiative INIT-001 --title "..."
python scripts/planctl.py epic status EPIC-001 --to active
python scripts/planctl.py epic archive EPIC-001
```

## 2.7 Epic Parent Rule

An Epic cannot be created under a missing Initiative.

An Epic cannot be created under an archived Initiative.

An Epic cannot become active, planned, proposed or blocked under an archived Initiative.

Allowed Epic statuses under archived Initiative:

```text
done
deferred
archived
```

## 2.8 Plan Completion Rule

An Initiative or Epic may become `done` only when it is no longer expected to produce active work.

Recommended rule:

```text
Epic should become done only after all related Tasks are done, deferred or archived.
Initiative should become done only after all child Epics are done, deferred or archived.
```

This rule may require task-aware validation in a future unified `projectctl.py`.

---

# 3. Task Lifecycle

Task lifecycle applies to:

```text
Task
Current Task
Prompt Package
```

It is currently controlled by:

```bash
python scripts/taskctl.py ...
```

## 3.1 Task Statuses

Allowed statuses:

```text
proposed
planned
ready
in_progress
blocked
in_review
changes_requested
approved
done
deferred
archived
```

## 3.2 Task Status Meaning

| Status              | Meaning                                       |
| ------------------- | --------------------------------------------- |
| `proposed`          | Suggested task, not yet planned               |
| `planned`           | Accepted into backlog but not ready           |
| `ready`             | Ready for execution or selection              |
| `in_progress`       | Work is being executed                        |
| `blocked`           | Work cannot continue due to blocker           |
| `in_review`         | Work is submitted for review                  |
| `changes_requested` | Review found required changes                 |
| `approved`          | Review/approval passed and task can be closed |
| `done`              | Task completed                                |
| `deferred`          | Task postponed                                |
| `archived`          | Task closed and inactive                      |

## 3.3 Allowed Task Transitions

```text
proposed -> planned
proposed -> ready
proposed -> deferred
proposed -> archived

planned -> ready
planned -> in_progress
planned -> blocked
planned -> deferred
planned -> archived

ready -> in_progress
ready -> blocked
ready -> deferred
ready -> archived

in_progress -> blocked
in_progress -> in_review
in_progress -> deferred
in_progress -> archived

blocked -> ready
blocked -> in_progress
blocked -> deferred
blocked -> archived

in_review -> changes_requested
in_review -> approved
in_review -> in_progress
in_review -> deferred
in_review -> archived

changes_requested -> in_progress
changes_requested -> blocked
changes_requested -> deferred
changes_requested -> archived

approved -> done
approved -> archived

done -> archived

deferred -> planned
deferred -> ready
deferred -> archived

archived -> no outgoing transitions
```

## 3.4 Task Is The Only Executable Unit

Only a Task may be executed by Codex.

The following must never be executed directly:

```text
Goal
Strategy
Initiative
Epic
Change Proposal
Review
QA Result
Decision
```

## 3.5 Task Parent Rule

Every Task must belong to an Epic.

```text
Task.epic_id -> Epic.id
```

A Task is invalid if:

```text
- epic_id is missing;
- referenced Epic does not exist;
- referenced Epic is inactive while Task is active;
- referenced Epic belongs to an archived Initiative while Task is active.
```

Inactive parent statuses:

```text
done
deferred
archived
```

If parent Epic is inactive, only inactive Task statuses are allowed:

```text
done
deferred
archived
```

## 3.6 Task Required Fields

A Task must have the following fields:

```text
id
epic_id
title
status
summary
description
priority
order
active_role
active_stage
active_document
expected_result
verification_mode
scope
out_of_scope
allowed_files
acceptance_criteria
review_instructions
notes
created_at
updated_at
```

## 3.7 Ready Rule

A Task should become `ready` only when it is clear enough to execute.

Recommended required fields before `ready`:

```text
title
epic_id
summary or description
scope
out_of_scope
allowed_files
acceptance_criteria
verification_mode
```

If any of these are missing, Codex should ask Human Owner for clarification instead of guessing.

## 3.8 In Progress Rule

A Task should become `in_progress` only when:

```text
- Task exists;
- parent Epic exists;
- parent Epic is not inactive;
- Task has enough scope to execute;
- allowed files are clear;
- Human Owner has selected or approved the work.
```

Current implementation allows `planned -> in_progress`.

Recommended stricter future policy:

```text
planned -> ready -> in_progress
```

## 3.9 Review Rule

A Task should become `in_review` when implementation work has finished and review is needed.

Before `in_review`, Codex should report:

```text
changed files
commands run
validation result
known risks
unresolved issues
```

## 3.10 Changes Requested Rule

A Task becomes `changes_requested` when review finds required changes.

Allowed next states:

```text
changes_requested -> in_progress
changes_requested -> blocked
changes_requested -> deferred
changes_requested -> archived
```

Codex must not mark `changes_requested` work as `done` directly.

## 3.11 Approved Rule

The `approved` status means review/acceptance gate has passed and the task is eligible to become `done`.

Current implementation requires approved tasks to have:

```text
approved_by
approved_at
```

The approval transition must use:

```bash
python scripts/taskctl.py task approve TASK-001
```

Direct transition to `approved` through generic transition command should be rejected.

## 3.12 Done Rule

A Task may become `done` only after approval.

Current implemented path:

```text
in_review -> approved -> done
```

Recommended future requirements before `done`:

```text
- verification summary exists;
- generated files are up to date;
- review is approved or explicitly waived;
- acceptance criteria are satisfied;
- Human Owner accepts result or delegates acceptance rule.
```

## 3.13 Done Task Immutability

A `done` Task should not be edited.

If additional work is needed, create a follow-up Task.

Allowed action for done Task:

```text
done -> archived
```

## 3.14 Archived Task Rule

An archived Task is terminal.

```text
archived -> no outgoing transitions
```

An archived Task must not be current.

---

# 4. Current Task Lifecycle

Current Task is not a separate executable entity.

It is a pointer to one selected Task:

```text
AI_PROJECT/state/tasks.json.current_task_id
```

## 4.1 Current Task Purpose

Current Task prevents Codex from choosing arbitrary work from the backlog.

Codex should work only on the selected current Task.

## 4.2 Current Task Allowed Statuses

Current implementation allows current task in these statuses:

```text
planned
ready
in_progress
blocked
in_review
changes_requested
```

Recommended stricter future policy:

```text
ready
in_progress
in_review
changes_requested
```

## 4.3 Current Task Rules

Current Task must:

```text
- reference an existing Task;
- not reference done/deferred/archived Task;
- not reference Task under inactive Epic;
- not reference Task under archived Initiative;
- be changed only through taskctl.py.
```

Allowed commands:

```bash
python scripts/taskctl.py current set TASK-001
python scripts/taskctl.py current show
python scripts/taskctl.py current clear
```

## 4.4 Auto-Clear Rule

If current Task moves to a non-current status, current task pointer should be cleared.

Non-current statuses:

```text
approved
done
deferred
archived
```

---

# 5. Prompt Package Lifecycle

Prompt Package is generated execution context for Codex.

It is built from Task state.

## 5.1 Prompt Package Is Derived Output

Prompt Package must not be manually written as source of truth.

It should be generated by:

```bash
python scripts/taskctl.py prompt build --write
```

Generated file:

```text
AI_PROJECT/generated/CODEX_PROMPT.md
```

## 5.2 Prompt Build Rule

Prompt Package may be built for:

```text
- explicitly selected Task via --task;
- current Task if no --task is provided.
```

If no Task is selected, command must fail.

## 5.3 Executable Prompt Rule

By default, prompt package should be built only for executable/current-compatible Task statuses.

Current implementation allows:

```text
planned
ready
in_progress
blocked
in_review
changes_requested
```

Recommended stricter future policy:

```text
ready
in_progress
changes_requested
```

Prompt package for inactive statuses should require explicit override.

## 5.4 Prompt Package Must Not Invent Scope

Prompt Package must derive from Task fields:

```text
active_role
active_stage
active_document
expected_result
summary
description
scope
out_of_scope
allowed_files
acceptance_criteria
review_instructions
notes
verification_mode
```

Prompt Package must not add hidden scope, hidden files or hidden acceptance criteria.

---

# 6. Evolution Lifecycle

Evolution lifecycle applies to changes of AI Development System itself.

It should be controlled by future:

```bash
python scripts/evolutionctl.py ...
```

## 6.1 Evolution Entity

The core evolution entity is:

```text
Change Proposal
```

ID format:

```text
CHG-001
CHG-002
CHG-003
```

## 6.2 What Counts As Evolution

A Change Proposal is required for changes affecting:

```text
- AI Development System rules;
- lifecycle documents;
- command catalogs;
- planctl.py;
- taskctl.py;
- evolutionctl.py;
- state/events/generated structure;
- prompt package behavior;
- Codex skill/plugin behavior;
- AGENTS.md rules;
- protected files policy;
- templates;
- schemas;
- review lifecycle;
- QA lifecycle;
- security/privacy/sandbox policy.
```

## 6.3 Evolution Statuses

Planned statuses:

```text
proposed
draft
ready
approved
in_progress
in_review
changes_requested
accepted
rejected
deferred
superseded
archived
```

## 6.4 Evolution Status Meaning

| Status              | Meaning                                 |
| ------------------- | --------------------------------------- |
| `proposed`          | Change idea exists                      |
| `draft`             | Change is being specified               |
| `ready`             | Change is ready for owner approval      |
| `approved`          | Human Owner approved the change         |
| `in_progress`       | Linked implementation work is active    |
| `in_review`         | Change implementation is being reviewed |
| `changes_requested` | Review requires changes                 |
| `accepted`          | Change is implemented and accepted      |
| `rejected`          | Change will not be done                 |
| `deferred`          | Change postponed                        |
| `superseded`        | Replaced by another Change Proposal     |
| `archived`          | Closed and inactive                     |

## 6.5 Allowed Evolution Transitions

```text
proposed -> draft
proposed -> rejected
proposed -> deferred

draft -> ready
draft -> rejected
draft -> deferred

ready -> approved
ready -> rejected
ready -> deferred

approved -> in_progress
approved -> deferred
approved -> superseded

in_progress -> in_review
in_progress -> changes_requested
in_progress -> deferred

in_review -> accepted
in_review -> changes_requested

changes_requested -> in_progress
changes_requested -> deferred

accepted -> archived
rejected -> archived
deferred -> draft
deferred -> ready
deferred -> archived
superseded -> archived
archived -> no outgoing transitions
```

## 6.6 Evolution Approval Rule

Codex must not implement system evolution directly.

Before implementation, Change Proposal must be approved:

```bash
python scripts/evolutionctl.py change approve CHG-001
```

Only after approval may implementation be represented as Task work through `taskctl.py`.

## 6.7 Evolution To Task Rule

Evolution Change Proposal is not executable by itself.

Correct chain:

```text
Change Proposal created
-> Change Proposal approved
-> Implementation Task created
-> Task linked to Change Proposal
-> Task executed through taskctl.py
-> Change Proposal reviewed
-> Change Proposal accepted
```

Example future commands:

```bash
python scripts/evolutionctl.py change create --title "Add protected files check" --type tooling
python scripts/evolutionctl.py change approve CHG-001
python scripts/taskctl.py task create --epic EPIC-001 --title "Implement CHG-001"
python scripts/evolutionctl.py change link-task CHG-001 --task TASK-001
```

## 6.8 Evolution Acceptance Rule

A Change Proposal may become `accepted` only when:

```text
- linked Tasks are done or explicitly waived;
- generated documentation is updated;
- validation passes;
- migration impact is documented;
- Human Owner accepts the system change.
```

## 6.9 Evolution Superseded Rule

A Change Proposal may become `superseded` when another Change Proposal replaces it.

A superseded change must reference replacement Change Proposal.

Future field:

```text
superseded_by: CHG-002
```

---

# 7. Cross-Lifecycle Rules

## 7.1 Plan To Task Rule

Task must be created under Epic.

```text
Plan: Initiative -> Epic
Task: Epic -> Task
```

A Task cannot exist without an Epic.

## 7.2 Task To Prompt Rule

Prompt Package must be built from Task.

```text
Task -> Prompt Package
```

Prompt Package cannot exist as independent project state.

## 7.3 Evolution To Task Rule

Evolution Change Proposal may produce Tasks, but does not replace Tasks.

```text
Change Proposal -> Task[]
```

Codex executes Tasks, not Change Proposals.

## 7.4 Inactive Parent Rule

If a parent becomes inactive, active children must be resolved.

Parent inactive statuses:

```text
done
deferred
archived
```

Children under inactive parents must be:

```text
done
deferred
archived
```

This applies to:

```text
Initiative -> Epic
Epic -> Task
```

## 7.5 No Silent Lifecycle Evolution

AI must not silently change:

```text
- allowed statuses;
- allowed transitions;
- meaning of approval;
- meaning of done;
- command catalog;
- validation rules;
- prompt package behavior.
```

Any such change requires Evolution Change Proposal.

---

# 8. Human Owner Gates

Human Owner approval is required for:

```text
- changing project goal;
- changing strategy;
- approving executable work;
- accepting completed work;
- changing lifecycle rules;
- changing command catalog;
- changing protected files policy;
- changing prompt package behavior;
- accepting evolution changes.
```

AI may propose and prepare changes, but must not silently approve them.

---

# 9. Codex Stop Conditions

Codex must stop if:

```text
- requested operation has no allowed command;
- required parent entity is missing;
- lifecycle transition is invalid;
- task has unclear scope;
- allowed files are missing or too broad;
- owner approval is required but missing;
- generated files are stale and cannot be regenerated;
- validation fails;
- requested work changes lifecycle/system rules without approved Change Proposal.
```

Expected report format:

```text
STOPPED:
reason: ...
blocked_by: ...
required_owner_action: ...
suggested_command: ...
```

If no allowed command exists:

```text
NO_ALLOWED_COMMAND
requested_intent: ...
closest_existing_command: ...
missing_capability: ...
required_system_evolution: ...
```

---

# 10. Validation Requirements

Lifecycle validation must check:

```text
- status is known;
- transition is allowed;
- archived entity is immutable;
- parent references exist;
- parent status allows child status;
- current task points to allowed status;
- approved task has approval metadata;
- done task follows required closure path;
- generated files are up to date;
- no protected files were manually edited.
```

Current commands:

```bash
python scripts/planctl.py validate
python scripts/taskctl.py validate
python scripts/taskctl.py check-generated
```

Future command:

```bash
python scripts/projectctl.py validate all
```

---

# 11. MVP Lifecycle Coverage

Current MVP covers:

```text
Plan Lifecycle:
  Initiative
  Epic

Task Lifecycle:
  Task
  Current Task
  Prompt Package
```

Current MVP does not yet fully cover:

```text
Evolution Change Proposal
Review lifecycle
QA lifecycle
Decision lifecycle
Release lifecycle
Protected files enforcement
Unified projectctl.py
```

---

# 12. Recommended Next Steps

## 12.1 Add evolutionctl.py

Implement:

```text
AI_PROJECT/state/evolution.json
AI_PROJECT/events/evolution-events.jsonl
AI_PROJECT/generated/EVOLUTION.md
```

First commands:

```bash
python scripts/evolutionctl.py init
python scripts/evolutionctl.py change create --title "..."
python scripts/evolutionctl.py change show CHG-001
python scripts/evolutionctl.py change list
python scripts/evolutionctl.py change transition CHG-001 --to ready
python scripts/evolutionctl.py change approve CHG-001
python scripts/evolutionctl.py change link-task CHG-001 --task TASK-001
python scripts/evolutionctl.py change accept CHG-001
python scripts/evolutionctl.py validate
python scripts/evolutionctl.py render
python scripts/evolutionctl.py audit
```

## 12.2 Tighten Current Task Rules

Recommended future change:

```text
Remove planned and blocked from default current-task executable statuses.
```

Preferred current statuses:

```text
ready
in_progress
in_review
changes_requested
```

## 12.3 Add Verification Evidence

Before Task becomes `done`, require:

```text
verification_summary
checks_run
review_status
acceptance_result
```

## 12.4 Add Protected Files Check

Implement:

```bash
python scripts/check-protected-project-files.py
```

Purpose:

```text
Detect direct edits to:
AI_PROJECT/state/**
AI_PROJECT/events/**
AI_PROJECT/generated/**
```

---

# Summary

Project Control Gateway uses lifecycle rules to keep AI-assisted development controlled and auditable.

Current implemented lifecycle control:

```text
planctl.py:
  Initiative / Epic lifecycle

taskctl.py:
  Task / Current Task / Prompt Package lifecycle
```

Planned next lifecycle control:

```text
evolutionctl.py:
  Change Proposal / System Evolution lifecycle
```

The main operating rule is:

```text
Plan containers organize work.
Tasks are the only executable units.
Prompt Packages are generated from Tasks.
Evolution Changes govern modifications to the system itself.
Python validates lifecycle transitions.
Human Owner keeps final authority.
```

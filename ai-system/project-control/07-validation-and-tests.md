# Project Control Validation and Tests

## Status

Draft

## Purpose

This document defines how Project Control Gateway must be validated and tested.

The goal is to prove that project control is not just documented, but actually enforced by CLI commands, validation rules, generated output checks and repeatable test scenarios.

Project Control Gateway is valid only if:

```text id="c2hb7h"
state changes happen through CLI;
invalid states are rejected;
audit events are written;
generated Markdown can be rebuilt;
Codex can operate from generated prompt packages;
manual or accidental drift can be detected.
```

## Scope

This document covers validation and tests for the current implemented control layers:

```text id="rfm6au"
scripts/planctl.py
scripts/taskctl.py
```

Current controlled state:

```text id="k8l7sl"
AI_PROJECT/state/plan.json
AI_PROJECT/state/tasks.json
```

Current audit logs:

```text id="khg80k"
AI_PROJECT/events/plan-events.jsonl
AI_PROJECT/events/task-events.jsonl
```

Current generated output:

```text id="orptmz"
AI_PROJECT/generated/CODEX_PLAN.md
AI_PROJECT/generated/CODEX_TASKS.md
AI_PROJECT/generated/CODEX_CURRENT.md
AI_PROJECT/generated/CODEX_PROMPT.md
```

This document also defines future validation expectations for:

```text id="btrtt0"
evolutionctl.py
protected-files check
CI integration
Codex plugin/skill integration
```

---

# 1. Validation Philosophy

Validation must protect the project from invalid state, lifecycle drift and uncontrolled AI behavior.

Core rule:

```text id="vmx7im"
Python validates project control state.
AI does not validate by reasoning alone.
```

AI may reason about what command to run, but the command must enforce correctness.

## Validation Must Catch

Validation must catch:

```text id="hdfk7q"
- invalid JSON;
- missing required fields;
- duplicate IDs;
- invalid status values;
- invalid lifecycle transitions;
- broken parent references;
- tasks under inactive epics;
- tasks under archived initiatives;
- current task pointing to invalid task;
- generated Markdown drift;
- prompt build without selected task;
- prompt build for inactive task unless explicitly allowed;
- attempts to mutate archived or done entities;
- unsupported owner intent with no allowed command.
```

## Validation Must Not Depend On Chat

Important state must not live only in chat history.

If it matters, it must be represented in:

```text id="68ndx5"
state/*.json
events/*.jsonl
generated/*.md
```

---

# 2. Validation Layers

Project Control Gateway uses multiple validation layers.

```text id="jytlf2"
CLI validation
State validation
Lifecycle validation
Parent-reference validation
Generated-output validation
Audit validation
Smoke workflow validation
Protected-files validation
```

## 2.1 CLI Validation

Checks whether a requested command and arguments are valid.

Examples:

```text id="gxvazh"
missing --title
missing --epic
invalid --to status
invalid --verification-mode
unknown command
```

## 2.2 State Validation

Checks whether JSON state has the expected structure.

Examples:

```text id="235wdf"
schema_version exists
revision is integer
tasks is a list
epics is a list
required task fields exist
```

## 2.3 Lifecycle Validation

Checks whether status transitions are allowed.

Examples:

```text id="u1afvx"
proposed -> done must fail
archived -> active must fail
done task mutation must fail
generic transition to approved must fail if taskctl requires approve command
```

## 2.4 Parent-Reference Validation

Checks parent-child relationships.

Examples:

```text id="k14jh9"
Epic.initiative_id -> Initiative.id
Task.epic_id -> Epic.id
```

## 2.5 Generated-Output Validation

Checks whether generated Markdown is up to date with state.

Current implemented check:

```bash id="o3nvcm"
python scripts/taskctl.py check-generated
```

Plan generated output can be rebuilt with:

```bash id="gq5cu2"
python scripts/planctl.py render
```

Future improvement:

```bash id="fetm67"
python scripts/planctl.py check-generated
```

## 2.6 Audit Validation

Checks whether mutations write audit events.

Audit files:

```text id="rwgr08"
AI_PROJECT/events/plan-events.jsonl
AI_PROJECT/events/task-events.jsonl
```

Every successful mutation should append exactly one success event.

## 2.7 Smoke Workflow Validation

Runs a complete valid workflow in a temporary project root.

This proves that the control system works end-to-end.

## 2.8 Protected-Files Validation

Future validation layer.

Purpose:

```text id="8la65o"
Detect manual edits to protected state, event and generated files.
```

Protected paths:

```text id="3v34ep"
AI_PROJECT/state/**
AI_PROJECT/events/**
AI_PROJECT/generated/**
```

---

# 3. Current Validation Commands

## 3.1 Plan Validation

```bash id="9g53qw"
python scripts/planctl.py validate
```

Expected success output:

```text id="0818ai"
OK: plan is valid
```

Expected failure output:

```text id="gkssoz"
VALIDATION_FAILED:
- ...
```

## 3.2 Plan Render

```bash id="5cpl6k"
python scripts/planctl.py render
```

Expected result:

```text id="940qke"
AI_PROJECT/generated/CODEX_PLAN.md is regenerated from AI_PROJECT/state/plan.json
```

## 3.3 Plan Audit

```bash id="q75h0s"
python scripts/planctl.py audit --last 20
```

Expected result:

```text id="eyaoeu"
recent plan mutation events are printed
```

## 3.4 Task Validation

```bash id="yy4blm"
python scripts/taskctl.py validate
```

Expected success output:

```text id="msb59x"
OK: tasks are valid
```

Expected failure output:

```text id="ufqxf1"
VALIDATION_FAILED:
- ...
```

## 3.5 Task Render

```bash id="525luq"
python scripts/taskctl.py render
```

Expected result:

```text id="393auq"
AI_PROJECT/generated/CODEX_TASKS.md is regenerated
AI_PROJECT/generated/CODEX_CURRENT.md is regenerated
```

## 3.6 Task Generated Check

```bash id="t2859z"
python scripts/taskctl.py check-generated
```

Expected success output:

```text id="z8f6yk"
OK: generated task files are up to date
```

Expected failure output:

```text id="q3m0mu"
GENERATED_CHECK_FAILED:
- outdated generated file: ...
```

## 3.7 Prompt Build

```bash id="5z5hzs"
python scripts/taskctl.py prompt build --write
```

Expected result:

```text id="50jevo"
AI_PROJECT/generated/CODEX_PROMPT.md is written
task-events.jsonl receives prompt.build event
```

---

# 4. Test Categories

Project Control Gateway must be tested with these categories:

```text id="d6z3ry"
1. Happy path tests
2. Invalid command tests
3. Invalid lifecycle transition tests
4. Invalid parent-reference tests
5. Archived parent tests
6. Current task tests
7. Prompt package tests
8. Generated output drift tests
9. Audit event tests
10. Idempotency and isolation tests
11. Future protected-files tests
```

---

# 5. Happy Path Test

## 5.1 Purpose

Prove that the full control flow works from plan initialization to Codex prompt generation.

## 5.2 Scenario

```text id="wycbrn"
plan init
initiative create
epic create
task init
task create
current set
prompt build
plan validate
task validate
task check-generated
```

## 5.3 Commands

```bash id="pt0ts2"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init \
  --project-name "AI Development System Smoke Test"

python scripts/planctl.py --root "$ROOT" idea set \
  --text "Create a controlled AI-assisted development system."

python scripts/planctl.py --root "$ROOT" goal set \
  --text "Validate Project Control Gateway."

python scripts/planctl.py --root "$ROOT" strategy set-summary \
  --text "Use CLI commands as the only mutation path."

python scripts/planctl.py --root "$ROOT" initiative create \
  --title "Project Control Gateway" \
  --summary "Validate strict project control through CLI."

python scripts/planctl.py --root "$ROOT" epic create \
  --initiative INIT-001 \
  --title "Task Control CLI" \
  --summary "Validate executable task control."

python scripts/taskctl.py --root "$ROOT" init

python scripts/taskctl.py --root "$ROOT" task create \
  --epic EPIC-001 \
  --title "Smoke Task" \
  --summary "Validate end-to-end task workflow." \
  --scope "Create generated prompt package" \
  --out-of-scope "No application code changes" \
  --allowed-file "AI_PROJECT/generated/CODEX_PROMPT.md" \
  --acceptance "Task validation passes" \
  --acceptance "Generated task files are up to date" \
  --verification-mode standard

python scripts/taskctl.py --root "$ROOT" current set TASK-001

python scripts/taskctl.py --root "$ROOT" prompt build --write

python scripts/planctl.py --root "$ROOT" validate
python scripts/taskctl.py --root "$ROOT" validate
python scripts/taskctl.py --root "$ROOT" check-generated
```

## 5.4 Expected Result

All commands succeed.

Expected files exist:

```text id="m4rxfx"
AI_PROJECT/state/plan.json
AI_PROJECT/state/tasks.json
AI_PROJECT/events/plan-events.jsonl
AI_PROJECT/events/task-events.jsonl
AI_PROJECT/generated/CODEX_PLAN.md
AI_PROJECT/generated/CODEX_TASKS.md
AI_PROJECT/generated/CODEX_CURRENT.md
AI_PROJECT/generated/CODEX_PROMPT.md
```

Expected validation result:

```text id="o8p7we"
plan is valid
tasks are valid
generated task files are up to date
```

---

# 6. Invalid Parent Tests

## 6.1 Task With Missing Epic

### Purpose

Task must not be created under a missing Epic.

### Command

```bash id="i5sxav"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init
python scripts/taskctl.py --root "$ROOT" init

python scripts/taskctl.py --root "$ROOT" task create \
  --epic EPIC-999 \
  --title "Invalid Task"
```

### Expected Result

Command fails.

Expected error:

```text id="yy28et"
EPIC_NOT_FOUND
```

or equivalent parent-reference error.

State must not contain the invalid task.

## 6.2 Epic With Missing Initiative

### Purpose

Epic must not be created under a missing Initiative.

### Command

```bash id="qbyh9f"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init

python scripts/planctl.py --root "$ROOT" epic create \
  --initiative INIT-999 \
  --title "Invalid Epic"
```

### Expected Result

Command fails.

Expected error:

```text id="1umc1h"
ENTITY_NOT_FOUND: INIT-999
```

---

# 7. Invalid Lifecycle Transition Tests

## 7.1 Plan Invalid Transition

### Purpose

Invalid plan status transition must fail.

### Scenario

```text id="y2esk2"
proposed -> done
```

### Command

```bash id="qsvb6z"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init

python scripts/planctl.py --root "$ROOT" initiative create \
  --title "Invalid Transition Test" \
  --status proposed

python scripts/planctl.py --root "$ROOT" initiative status INIT-001 \
  --to done
```

### Expected Result

Command fails.

Expected error:

```text id="g27j5x"
INVALID_STATUS_TRANSITION
```

## 7.2 Task Invalid Transition

### Purpose

Invalid task status transition must fail.

### Scenario

```text id="1biz9l"
proposed -> done
```

### Command

```bash id="h19u19"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init
python scripts/planctl.py --root "$ROOT" initiative create --title "Project Control"
python scripts/planctl.py --root "$ROOT" epic create --initiative INIT-001 --title "Task Control"

python scripts/taskctl.py --root "$ROOT" init

python scripts/taskctl.py --root "$ROOT" task create \
  --epic EPIC-001 \
  --title "Invalid Task Transition" \
  --status proposed

python scripts/taskctl.py --root "$ROOT" task transition TASK-001 \
  --to done
```

### Expected Result

Command fails.

Expected error:

```text id="qm7lhe"
INVALID_STATUS_TRANSITION
```

## 7.3 Generic Transition To Approved

### Purpose

Task approval must go through `task approve`, not generic transition.

### Command

```bash id="nv3p2s"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init
python scripts/planctl.py --root "$ROOT" initiative create --title "Project Control"
python scripts/planctl.py --root "$ROOT" epic create --initiative INIT-001 --title "Task Control"

python scripts/taskctl.py --root "$ROOT" init

python scripts/taskctl.py --root "$ROOT" task create \
  --epic EPIC-001 \
  --title "Approval Test" \
  --status in_review

python scripts/taskctl.py --root "$ROOT" task transition TASK-001 \
  --to approved
```

### Expected Result

Command fails.

Expected error:

```text id="6huqv5"
USE_TASK_APPROVE_COMMAND_FOR_APPROVAL
```

---

# 8. Archived Parent Tests

## 8.1 Epic Under Archived Initiative

### Purpose

An active Epic must not exist under an archived Initiative.

### Command

```bash id="zdaint"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init
python scripts/planctl.py --root "$ROOT" initiative create --title "Parent Initiative"
python scripts/planctl.py --root "$ROOT" initiative archive INIT-001
python scripts/planctl.py --root "$ROOT" epic create --initiative INIT-001 --title "Invalid Epic"
```

### Expected Result

Epic creation fails.

Expected error:

```text id="lbt5x7"
CANNOT_CREATE_EPIC_UNDER_ARCHIVED_INITIATIVE
```

## 8.2 Task Under Inactive Epic

### Purpose

A live Task must not be created under inactive Epic.

### Command

```bash id="doh8dg"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init
python scripts/planctl.py --root "$ROOT" initiative create --title "Project Control"
python scripts/planctl.py --root "$ROOT" epic create --initiative INIT-001 --title "Inactive Epic"
python scripts/planctl.py --root "$ROOT" epic status EPIC-001 --to deferred

python scripts/taskctl.py --root "$ROOT" init

python scripts/taskctl.py --root "$ROOT" task create \
  --epic EPIC-001 \
  --title "Invalid Task Under Deferred Epic"
```

### Expected Result

Command fails.

Expected error:

```text id="oqws2p"
CANNOT_USE_INACTIVE_EPIC
```

---

# 9. Current Task Tests

## 9.1 Set Current Task

### Purpose

Current task must point to an existing executable/current-compatible task.

### Command

```bash id="ptxaaf"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init
python scripts/planctl.py --root "$ROOT" initiative create --title "Project Control"
python scripts/planctl.py --root "$ROOT" epic create --initiative INIT-001 --title "Task Control"

python scripts/taskctl.py --root "$ROOT" init

python scripts/taskctl.py --root "$ROOT" task create \
  --epic EPIC-001 \
  --title "Current Task Test" \
  --status ready \
  --scope "Do one thing" \
  --out-of-scope "Everything else" \
  --allowed-file "README.md" \
  --acceptance "Validation passes"

python scripts/taskctl.py --root "$ROOT" current set TASK-001
python scripts/taskctl.py --root "$ROOT" current show
```

### Expected Result

Current task is set to:

```text id="xjj2qt"
TASK-001
```

## 9.2 Set Missing Current Task

### Command

```bash id="tu5q19"
ROOT="$(mktemp -d)"

python scripts/taskctl.py --root "$ROOT" init
python scripts/taskctl.py --root "$ROOT" current set TASK-999
```

### Expected Result

Command fails.

Expected error:

```text id="0h664e"
ENTITY_NOT_FOUND
```

## 9.3 Current Task Auto-Clear

### Purpose

Current task should clear when task moves to non-current status.

### Command

```bash id="dzvvho"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init
python scripts/planctl.py --root "$ROOT" initiative create --title "Project Control"
python scripts/planctl.py --root "$ROOT" epic create --initiative INIT-001 --title "Task Control"

python scripts/taskctl.py --root "$ROOT" init

python scripts/taskctl.py --root "$ROOT" task create \
  --epic EPIC-001 \
  --title "Auto Clear Test" \
  --status ready \
  --scope "Do one thing" \
  --allowed-file "README.md" \
  --acceptance "Validation passes"

python scripts/taskctl.py --root "$ROOT" current set TASK-001
python scripts/taskctl.py --root "$ROOT" task transition TASK-001 --to in_progress
python scripts/taskctl.py --root "$ROOT" task transition TASK-001 --to in_review
python scripts/taskctl.py --root "$ROOT" task approve TASK-001 --notes "Approved"
python scripts/taskctl.py --root "$ROOT" current show
```

### Expected Result

After approval, current task should be cleared because `approved` is not a current-compatible status.

Expected output:

```text id="rg8nhs"
No current task.
```

---

# 10. Prompt Package Tests

## 10.1 Build Prompt For Current Task

### Purpose

Prompt package should be generated from current task.

### Command

```bash id="5tarvp"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init
python scripts/planctl.py --root "$ROOT" initiative create --title "Project Control"
python scripts/planctl.py --root "$ROOT" epic create --initiative INIT-001 --title "Prompt Control"

python scripts/taskctl.py --root "$ROOT" init

python scripts/taskctl.py --root "$ROOT" task create \
  --epic EPIC-001 \
  --title "Prompt Build Test" \
  --summary "Build a Codex prompt package." \
  --scope "Generate prompt" \
  --out-of-scope "No code execution" \
  --allowed-file "AI_PROJECT/generated/CODEX_PROMPT.md" \
  --acceptance "Prompt file is written" \
  --verification-mode standard

python scripts/taskctl.py --root "$ROOT" current set TASK-001
python scripts/taskctl.py --root "$ROOT" prompt build --write
```

### Expected Result

File exists:

```text id="tzjxaa"
AI_PROJECT/generated/CODEX_PROMPT.md
```

Prompt contains:

```text id="v3dhgr"
[SYSTEM]
Active Role
Active Stage
Task ID: TASK-001
Scope
Out of Scope
Allowed Files
Acceptance Criteria
Execution Rules
```

Audit contains:

```text id="05fxv3"
prompt.build
```

## 10.2 Prompt Build Without Current Task

### Command

```bash id="hpvqd1"
ROOT="$(mktemp -d)"

python scripts/taskctl.py --root "$ROOT" init
python scripts/taskctl.py --root "$ROOT" prompt build
```

### Expected Result

Command fails.

Expected error:

```text id="ew5bf0"
NO_TASK_SELECTED
```

## 10.3 Prompt Build For Inactive Task

### Purpose

Prompt build must fail for inactive task unless explicitly allowed.

### Command

```bash id="3c1hn4"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init
python scripts/planctl.py --root "$ROOT" initiative create --title "Project Control"
python scripts/planctl.py --root "$ROOT" epic create --initiative INIT-001 --title "Prompt Control"

python scripts/taskctl.py --root "$ROOT" init

python scripts/taskctl.py --root "$ROOT" task create \
  --epic EPIC-001 \
  --title "Inactive Prompt Test" \
  --status deferred

python scripts/taskctl.py --root "$ROOT" prompt build --task TASK-001
```

### Expected Result

Command fails.

Expected error:

```text id="ldfy0c"
TASK_IS_NOT_EXECUTABLE
```

Override for inspection:

```bash id="o40kar"
python scripts/taskctl.py --root "$ROOT" prompt build --task TASK-001 --allow-inactive
```

---

# 11. Generated Output Drift Tests

## 11.1 Task Generated Drift

### Purpose

Manual changes to generated task files should be detected.

### Command

```bash id="ee3uio"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init
python scripts/planctl.py --root "$ROOT" initiative create --title "Project Control"
python scripts/planctl.py --root "$ROOT" epic create --initiative INIT-001 --title "Task Control"

python scripts/taskctl.py --root "$ROOT" init

python scripts/taskctl.py --root "$ROOT" task create \
  --epic EPIC-001 \
  --title "Generated Drift Test" \
  --scope "Do one thing" \
  --allowed-file "README.md" \
  --acceptance "Generated drift is detected"

echo "manual edit" >> "$ROOT/AI_PROJECT/generated/CODEX_TASKS.md"

python scripts/taskctl.py --root "$ROOT" check-generated
```

### Expected Result

Command fails.

Expected error:

```text id="cct2pi"
GENERATED_CHECK_FAILED
```

## 11.2 Generated Repair

### Purpose

Render command should repair generated task output.

### Command

```bash id="a1i0qv"
python scripts/taskctl.py --root "$ROOT" render
python scripts/taskctl.py --root "$ROOT" check-generated
```

### Expected Result

Generated check passes.

## 11.3 Plan Generated Drift

### Current State

`planctl.py` can render `CODEX_PLAN.md`, but does not yet have a `check-generated` command.

### Recommended Future Test

```bash id="q6mntw"
python scripts/planctl.py --root "$ROOT" check-generated
```

Expected behavior:

```text id="ate2ci"
- render expected CODEX_PLAN.md in memory;
- compare with file on disk;
- fail if different.
```

---

# 12. Audit Event Tests

## 12.1 Plan Mutation Writes Event

### Purpose

Every plan mutation should append an audit event.

### Command

```bash id="v8uq5i"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init
python scripts/planctl.py --root "$ROOT" initiative create --title "Audit Test"
python scripts/planctl.py --root "$ROOT" audit --last 10
```

### Expected Result

Audit output includes:

```text id="k2abb7"
plan.init
initiative.create
```

## 12.2 Task Mutation Writes Event

### Purpose

Every task mutation should append an audit event.

### Command

```bash id="gnhyx3"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init
python scripts/planctl.py --root "$ROOT" initiative create --title "Audit Test"
python scripts/planctl.py --root "$ROOT" epic create --initiative INIT-001 --title "Audit Epic"

python scripts/taskctl.py --root "$ROOT" init
python scripts/taskctl.py --root "$ROOT" task create --epic EPIC-001 --title "Audit Task"
python scripts/taskctl.py --root "$ROOT" task add-scope TASK-001 --text "Add scope item"
python scripts/taskctl.py --root "$ROOT" audit --last 20
```

### Expected Result

Audit output includes:

```text id="8yjtd6"
tasks.init
task.create
task.add_scope
```

## 12.3 Failed Command Must Not Write Success Event

### Purpose

Failed validation must not append a success audit event.

### Scenario

```text id="s2j8px"
Try invalid transition.
Check audit does not contain successful invalid transition.
```

### Expected Result

Audit log should not claim the invalid mutation succeeded.

---

# 13. Done And Archived Immutability Tests

## 13.1 Done Task Mutation

### Purpose

A done Task should not be edited.

### Command

```bash id="ybpx2n"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init
python scripts/planctl.py --root "$ROOT" initiative create --title "Project Control"
python scripts/planctl.py --root "$ROOT" epic create --initiative INIT-001 --title "Task Control"

python scripts/taskctl.py --root "$ROOT" init

python scripts/taskctl.py --root "$ROOT" task create \
  --epic EPIC-001 \
  --title "Done Task Test" \
  --status in_review

python scripts/taskctl.py --root "$ROOT" task approve TASK-001 --notes "Approved"
python scripts/taskctl.py --root "$ROOT" task transition TASK-001 --to done
python scripts/taskctl.py --root "$ROOT" task update-summary TASK-001 --text "Should fail"
```

### Expected Result

Command fails.

Expected error:

```text id="xwmjqy"
DONE_TASK_IS_IMMUTABLE
```

## 13.2 Archived Task Mutation

### Purpose

Archived Task should not be edited.

### Expected error:

```text id="1y2dr6"
ARCHIVED_ENTITY_IS_IMMUTABLE
```

## 13.3 Archived Initiative Mutation

### Purpose

Archived Initiative should not be renamed or summarized.

### Expected error:

```text id="6xbonv"
ARCHIVED_ENTITY_IS_IMMUTABLE
```

---

# 14. Skip Plan Check Tests

## 14.1 Purpose

`--skip-plan-check` is useful for isolated task-state testing, but must not be the default execution path.

## 14.2 Valid Use

Allowed in tests where no `plan.json` exists:

```bash id="qqazgm"
python scripts/taskctl.py --root "$ROOT" validate --skip-plan-check
```

## 14.3 Risk

Using `--skip-plan-check` in normal work may hide broken Task -> Epic references.

## 14.4 Policy

Codex must not use `--skip-plan-check` during normal project execution unless explicitly instructed by Human Owner.

---

# 15. Smoke Test Script

## 15.1 Recommended Script

Create:

```text id="2p3f7h"
scripts/smoke-project-control.py
```

## 15.2 Purpose

Run an end-to-end test in a temporary directory.

## 15.3 Required Behavior

The smoke script should:

```text id="ulg0eg"
- create a temporary root;
- run planctl.py init;
- create Initiative;
- create Epic;
- run taskctl.py init;
- create Task;
- set Current Task;
- build Prompt Package;
- validate Plan;
- validate Tasks;
- check generated task files;
- assert expected files exist;
- assert audit logs contain expected events;
- exit 0 on success;
- exit non-zero on failure.
```

## 15.4 Suggested Command

```bash id="dgxci6"
python scripts/smoke-project-control.py
```

## 15.5 Expected Output

```text id="fpifid"
OK: project control smoke test passed
```

---

# 16. Manual Test Checklist

Before accepting changes to `planctl.py` or `taskctl.py`, run:

```bash id="cihzyy"
python scripts/planctl.py validate
python scripts/planctl.py render

python scripts/taskctl.py validate
python scripts/taskctl.py render
python scripts/taskctl.py check-generated
```

If current task exists:

```bash id="9ohzvc"
python scripts/taskctl.py current show
python scripts/taskctl.py prompt build --write
```

Also inspect recent audit:

```bash id="p94tq6"
python scripts/planctl.py audit --last 20
python scripts/taskctl.py audit --last 20
```

---

# 17. CI Recommendations

## 17.1 Minimum CI

Add a CI job that runs:

```bash id="afwqph"
python scripts/smoke-project-control.py
```

## 17.2 Repository-State CI

For real repository state, CI should run:

```bash id="i8q1vk"
python scripts/planctl.py validate
python scripts/taskctl.py validate
python scripts/taskctl.py check-generated
```

## 17.3 Future CI

Future CI should also run:

```bash id="k9w3aq"
python scripts/check-protected-project-files.py
python scripts/evolutionctl.py validate
python scripts/evolutionctl.py check-generated
```

---

# 18. Protected Files Check

## 18.1 Purpose

Protected files check should detect direct manual edits to control state.

Protected paths:

```text id="d48syx"
AI_PROJECT/state/**
AI_PROJECT/events/**
AI_PROJECT/generated/**
```

## 18.2 Future Script

```bash id="yx5ck0"
python scripts/check-protected-project-files.py
```

## 18.3 Expected Checks

The script should check:

```text id="hrssvo"
- generated files are up to date;
- state files are valid;
- event logs are valid JSONL;
- protected file changes are expected;
- generated output was not manually drifted;
- state changes have corresponding audit events where feasible.
```

## 18.4 Failure

Expected error:

```text id="ohexfr"
PROJECT_CONTROL_BYPASS_DETECTED
```

---

# 19. Test Data Policy

Tests should use temporary directories whenever possible.

Preferred:

```bash id="g8z5gd"
ROOT="$(mktemp -d)"
```

Tests must not mutate real project state unless explicitly intended.

Tests must not require network access.

Tests must not require Codex.

Tests should be deterministic.

---

# 20. Acceptance Criteria For Validation Layer

Validation and tests are acceptable when:

```text id="xnp5jd"
- happy path passes in a temp root;
- invalid lifecycle transitions fail;
- missing parent references fail;
- generated task drift is detected;
- prompt build requires selected or explicit Task;
- audit events are written for successful mutations;
- failed commands do not write success events;
- task validation checks plan references by default;
- generated Markdown can be regenerated;
- smoke test can run locally and in CI.
```

---

# 21. Known Gaps

Current known gaps:

```text id="c59tai"
- planctl.py does not yet have check-generated;
- done task does not yet require verification evidence;
- prompt build does not yet require non-empty scope/allowed_files/acceptance_criteria;
- current task allowed statuses are still broad;
- no unified projectctl.py exists yet;
- no CI job is defined yet.
- dedicated review and QA state domains are not implemented yet.
```

These gaps should be tracked as future Tasks or Evolution Change Proposals.

---

# 22. Recommended Next Tasks

Recommended implementation tasks:

```text id="ydl81h"
1. Add planctl.py check-generated.
2. Add CI job for project-control smoke and generated-output checks.
3. Add stricter prompt build validation.
4. Add dedicated review and QA control domains after approved evolution.
5. Add unified projectctl.py only after facade and domain command coverage is stable.
```

---

# Summary

Validation and tests turn Project Control Gateway from a concept into an enforceable system.

Current enforceable CLIs:

```text id="s8a1a2"
planctl.py
taskctl.py
```

Required validation loop:

```text id="evn5v9"
create/change state through CLI
validate state
render generated Markdown
check generated output
inspect audit events
run smoke tests
```

The long-term target is:

```text id="vqrym1"
Codex cannot safely bypass the CLI.
Invalid state cannot be committed unnoticed.
Generated Markdown cannot drift silently.
Every meaningful project-control mutation is auditable.
Human Owner keeps final authority.
```

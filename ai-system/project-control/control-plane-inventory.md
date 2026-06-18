# Centralized Control Plane Inventory

Status: Draft

## Summary

This document records the current `*ctl.py` command surface, state mutation paths, generated-output paths, duplicated control logic, task identity behavior, and risks that should be considered before designing a unified `aictl` control plane.

This is inventory only. It does not implement `scripts/aictl.py`, create `ai_project_ctl/`, refactor existing scripts, create web files, or change command behavior.

## Selected Task Identity

The inventory was executed from the registered executable task selected by local project-control state.

```text
id: TASK-019
ref: none
uid: tsk_d0e6e78d3c7c
legacy_id: TASK-019
aliases: TASK-019
epic_id: EPIC-005
epic_key: none
local_seq: none
title: Task A - Inventory existing ctl commands and state mutation paths
status_at_selection: planned
status_during_inventory: in_progress
```

`TASK-019` was selected because `python scripts/taskctl.py task next --json` returned it as the next executable task, and it belongs to `EPIC-005`, the centralized control-plane epic. The task scope explicitly asks for an inventory of existing ctl commands and mutation paths with no implementation.

## Loaded Task Fields

```text
active_role: AI System Maintainer / Project Control Architect
active_stage: Control Plane Inventory
active_document: ai-system/project-control/control-plane-inventory.md
expected_result: Inventory report produced; no code behavior changed.
verification_mode: standard
```

Scope:

- Identify all `scripts/*ctl.py` files and their command domains.
- List supported commands by domain and classify read, write, render, validation, and audit behavior.
- Identify duplicated lifecycle logic and direct state/events/generated mutation paths.
- Identify task ID collision risks across epics and aliases.
- Produce a readable inventory artifact if an approved standard location exists.

Out of scope:

- Do not implement `aictl.py`.
- Do not refactor existing ctl scripts.
- Do not create web app files.
- Do not manually edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**`, or `AI_PROJECT/generated/**`.

Acceptance criteria:

- Existing ctl surface is documented.
- Write paths are known.
- Gaps and unsafe paths are listed.
- No code behavior changed.

## Existing Ctl Scripts

Current repository ctl scripts:

```text
scripts/codexctl.py
scripts/contextctl.py
scripts/docctl.py
scripts/evolutionctl.py
scripts/planctl.py
scripts/taskctl.py
```

Current size snapshot:

```text
scripts/planctl.py       1566 lines
scripts/taskctl.py       3271 lines
scripts/docctl.py        1184 lines
scripts/contextctl.py    1112 lines
scripts/codexctl.py      1258 lines
scripts/evolutionctl.py  1560 lines
```

No `scripts/aictl.py` entrypoint exists yet. No `ai_project_ctl/` package exists yet.

## Command Inventory By Script

## `scripts/planctl.py`

Domain: planning containers.

Source of truth:

- `AI_PROJECT/state/plan.json`

Events:

- `AI_PROJECT/events/plan-events.jsonl`

Generated output:

- `AI_PROJECT/generated/CODEX_PLAN.md`

Command groups:

```text
init
show
status
validate
render
audit
idea show
idea set
goal show
goal set
goal add-criterion
goal remove-criterion
strategy show
strategy set-summary
strategy add-principle
strategy remove-principle
strategy add-constraint
strategy remove-constraint
initiative list
initiative show
initiative create
initiative rename
initiative summary
initiative status
initiative archive
epic list
epic show
epic create
epic rename
epic summary
epic set-key
epic status
epic archive
```

Read commands:

- `show`, `status`, `audit`
- `idea show`, `goal show`, `strategy show`
- `initiative list`, `initiative show`
- `epic list`, `epic show`

Write commands:

- `init`
- `idea set`
- `goal set`, `goal add-criterion`, `goal remove-criterion`
- `strategy set-summary`, `strategy add-principle`, `strategy remove-principle`, `strategy add-constraint`, `strategy remove-constraint`
- `initiative create`, `initiative rename`, `initiative summary`, `initiative status`, `initiative archive`
- `epic create`, `epic rename`, `epic summary`, `epic set-key`, `epic status`, `epic archive`

Validation and generated-output commands:

- `validate`
- `render`

Gap:

- There is no `planctl.py check-generated` command, so plan generated drift is detected indirectly by the protected-files check, not by a dedicated plan command.

## `scripts/taskctl.py`

Domain: executable tasks, current task, task identity, dependency graph, execution queue, and task-derived prompt package.

Source of truth:

- `AI_PROJECT/state/tasks.json`
- Reads `AI_PROJECT/state/plan.json` for plan reference checks.

Events:

- `AI_PROJECT/events/task-events.jsonl`

Generated output:

- `AI_PROJECT/generated/CODEX_TASKS.md`
- `AI_PROJECT/generated/CODEX_CURRENT.md`
- `AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md`
- `AI_PROJECT/generated/CODEX_PROMPT.md` through `prompt build --write`

Command groups:

```text
init
show
status
validate
render
check-generated
audit
migrate identity
task list
task show
task resolve
task deps list
task deps add
task deps remove
task graph validate
task executable
task next
task create
task rename
task update-summary
task update-description
task set-prompt-fields
task transition
task approve
task archive
task add-scope
task remove-scope
task add-out-of-scope
task remove-out-of-scope
task add-allowed-file
task remove-allowed-file
task add-acceptance
task remove-acceptance
task add-review-instruction
task remove-review-instruction
task add-note
task remove-note
current show
current set
current clear
prompt build
```

Read commands:

- `show`, `status`, `audit`
- `task list`, `task show`, `task resolve`
- `task deps list`, `task graph validate`, `task executable`, `task next`
- `current show`
- `prompt build` without `--write` or `--out`
- `migrate identity --dry-run`

Write commands:

- `init`
- `migrate identity` without `--dry-run`
- `task create`, `task rename`, `task update-summary`, `task update-description`, `task set-prompt-fields`
- `task transition`, `task approve`, `task archive`
- task list-field add/remove commands
- `task deps add`, `task deps remove`
- `current set`, `current clear`
- `prompt build --write` and `prompt build --out`

Validation and generated-output commands:

- `validate`
- `task graph validate`
- `render`
- `check-generated`
- `prompt build`

Important behavior:

- `task next --json` and `task executable --json` expose queue state for automation.
- `task resolve` accepts `id`, `uid`, `ref`, `legacy_id`, and aliases.
- `current set` writes `current_task_id` in `tasks.json`.
- Moving a current task to a non-current-compatible status clears the current pointer.
- `task approve` is separate from generic transition to `approved`.

## `scripts/docctl.py`

Domain: registered documentation lifecycle and documentation generated views.

Source of truth:

- `AI_PROJECT/state/docs.json`

Events:

- `AI_PROJECT/events/doc-events.jsonl`

Generated output:

- `AI_PROJECT/generated/DOCS_INDEX.md`
- `AI_PROJECT/generated/DOCS_GAPS.md`

Command groups:

```text
init
show
status
scan
validate
render
check-generated
audit
doc register
doc status
doc mark-reviewed
```

Read commands:

- `show`, `status`, `audit`
- `validate`, `check-generated`

Write commands:

- `init`
- `scan`
- `doc register`
- `doc status`
- `doc mark-reviewed`
- `render` writes generated documentation views

Important behavior:

- `scan` can register untracked Markdown and refresh derived metadata.
- `validate` currently reports warnings for several registry/status/content-hash mismatches but exits successfully in the current state.

## `scripts/contextctl.py`

Domain: deterministic context retrieval and Context Pack output.

Source of truth:

- Reads `AI_PROJECT/state/docs.json`
- Reads `AI_PROJECT/state/tasks.json`
- Does not own a source-of-truth JSON state file.

Events:

- `AI_PROJECT/events/context-events.jsonl`

Generated output:

- `AI_PROJECT/generated/CONTEXT_PACK.md`
- `AI_PROJECT/generated/CONTEXT_STATUS.md`

Command groups:

```text
status
index build
search
pack build
validate
render
check-generated
audit
```

Read commands:

- `status`
- `index build`
- `search`
- `pack build` without `--write`
- `validate`, `check-generated`, `audit`

Write commands:

- `pack build --write`
- `render`

Important behavior:

- The current Context Pack is task-scoped to `TASK-010`.
- `codexctl.py build --task TASK-019 --with-context` correctly rejected that stale/mismatched Context Pack.

## `scripts/codexctl.py`

Domain: current Codex prompt package and Codex prompt status.

Source of truth:

- `AI_PROJECT/state/current_execution.json`
- Reads `AI_PROJECT/state/tasks.json`
- Reads `AI_PROJECT/state/evolution.json`
- Reads `AI_PROJECT/state/docs.json` when validating Context Pack freshness.

Events:

- `AI_PROJECT/events/codex-events.jsonl`

Generated output:

- `AI_PROJECT/generated/CODEX_PROMPT.md`
- `AI_PROJECT/generated/CODEX_STATUS.md`

Command groups:

```text
status
build
clear
```

Read commands:

- `status`

Write commands:

- `build --task`
- `build --change`
- `clear`

Important behavior:

- `build --task <TASK_ID> --with-context` validates the existing Context Pack before including it.
- When context validation fails, `codexctl.py` records a blocked status in `current_execution.json` and `CODEX_STATUS.md`.
- In this run, `codexctl.py` blocked with `CODEX_CONTEXT_PACK_INVALID` because the existing Context Pack expected `TASK-010`, while the selected task was `TASK-019`.
- The fallback `taskctl.py prompt build --task TASK-019 --write` produced `CODEX_PROMPT.md`, but `CODEX_STATUS.md` remains blocked from the failed `codexctl.py` attempt.

## `scripts/evolutionctl.py`

Domain: AI Development System Change Proposals.

Source of truth:

- `AI_PROJECT/state/evolution.json`
- Reads `AI_PROJECT/state/tasks.json` for linked task checks.

Events:

- `AI_PROJECT/events/evolution-events.jsonl`

Generated output:

- `AI_PROJECT/generated/EVOLUTION.md`

Command groups:

```text
init
show
status
validate
render
check-generated
audit
change list
change show
change create
change rename
change set-problem
change set-rationale
change set-proposal
change set-compatibility
change set-migration
change transition
change approve
change link-task
change unlink-task
change waive-tasks
change accept
change archive
change add-affected-area
change remove-affected-area
change add-affected-file
change remove-affected-file
change add-risk
change remove-risk
change add-impact
change remove-impact
change add-note
change remove-note
```

Read commands:

- `show`, `status`, `validate`, `check-generated`, `audit`
- `change list`, `change show`

Write commands:

- `init`
- `render`
- all change create/update/transition/approval/link/waive/accept/archive/list-field mutation commands

Important behavior:

- Evolution approval and acceptance are explicit commands.
- This inventory task does not approve or implement any evolution change.

## State Files And Mutation Paths

Current state files:

```text
AI_PROJECT/state/plan.json
AI_PROJECT/state/tasks.json
AI_PROJECT/state/docs.json
AI_PROJECT/state/evolution.json
AI_PROJECT/state/current_execution.json
```

Mutation owners:

| State file | Owning command path | Notes |
| --- | --- | --- |
| `plan.json` | `planctl.py` | Owns project, idea, goal, strategy, initiatives, epics, epic keys. |
| `tasks.json` | `taskctl.py` | Owns tasks, current task pointer, dependencies, identity metadata, task prompt fields. |
| `docs.json` | `docctl.py` | Owns registered documentation, lifecycle status, hashes, review metadata. |
| `evolution.json` | `evolutionctl.py` | Owns Change Proposals and linked task metadata. |
| `current_execution.json` | `codexctl.py` | Owns current Codex prompt package status. |

All state-writing scripts use local `write_json()` and `atomic_write_text()` helpers with temp-file plus `os.replace()`. There is no shared store service yet.

## Event Logs And Append Paths

Current event logs:

```text
AI_PROJECT/events/plan-events.jsonl
AI_PROJECT/events/task-events.jsonl
AI_PROJECT/events/doc-events.jsonl
AI_PROJECT/events/evolution-events.jsonl
AI_PROJECT/events/context-events.jsonl
AI_PROJECT/events/codex-events.jsonl
```

Append owners:

| Event log | Appender | Revision model |
| --- | --- | --- |
| `plan-events.jsonl` | `planctl.py append_event()` | Uses plan revision before/after. |
| `task-events.jsonl` | `taskctl.py append_event()` | Uses task revision before/after. Prompt builds may keep revision unchanged. |
| `doc-events.jsonl` | `docctl.py append_event()` | Uses docs revision before/after. |
| `evolution-events.jsonl` | `evolutionctl.py append_event()` | Uses evolution revision before/after. |
| `context-events.jsonl` | `contextctl.py append_event()` | Uses a local event revision model, not a state revision. |
| `codex-events.jsonl` | `codexctl.py append_event()` | Uses current execution revision before/after. |

Events are appended with `open(..., "a")`. There is no shared event service, no file lock, and no single transaction envelope spanning state save, event append, and generated render.

## Generated Files And Render Paths

Current generated files:

```text
AI_PROJECT/generated/CODEX_PLAN.md
AI_PROJECT/generated/CODEX_TASKS.md
AI_PROJECT/generated/CODEX_CURRENT.md
AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md
AI_PROJECT/generated/CODEX_PROMPT.md
AI_PROJECT/generated/CODEX_STATUS.md
AI_PROJECT/generated/DOCS_INDEX.md
AI_PROJECT/generated/DOCS_GAPS.md
AI_PROJECT/generated/EVOLUTION.md
AI_PROJECT/generated/CONTEXT_PACK.md
AI_PROJECT/generated/CONTEXT_STATUS.md
```

Render owners:

| Generated file | Owner |
| --- | --- |
| `CODEX_PLAN.md` | `planctl.py render` and plan mutations. |
| `CODEX_TASKS.md` | `taskctl.py render` and task mutations. |
| `CODEX_CURRENT.md` | `taskctl.py render` and task mutations. |
| `TASK_EXECUTION_QUEUE.md` | `taskctl.py render` and task mutations. |
| `CODEX_PROMPT.md` | `taskctl.py prompt build --write` or `codexctl.py build`. |
| `CODEX_STATUS.md` | `codexctl.py status/build/clear` behavior. |
| `DOCS_INDEX.md` | `docctl.py render` and docs mutations. |
| `DOCS_GAPS.md` | `docctl.py render` and docs mutations. |
| `EVOLUTION.md` | `evolutionctl.py render` and evolution mutations. |
| `CONTEXT_PACK.md` | `contextctl.py pack build --write`. |
| `CONTEXT_STATUS.md` | `contextctl.py pack build --write` or `contextctl.py render`. |

## Validation And Check Commands

Available validation/check commands:

```text
python scripts/planctl.py validate
python scripts/taskctl.py validate
python scripts/taskctl.py task graph validate
python scripts/taskctl.py check-generated
python scripts/docctl.py validate
python scripts/docctl.py check-generated
python scripts/contextctl.py validate
python scripts/contextctl.py check-generated
python scripts/evolutionctl.py validate
python scripts/evolutionctl.py check-generated
python scripts/check-protected-project-files.py --verbose
```

Available render commands:

```text
python scripts/planctl.py render
python scripts/taskctl.py render
python scripts/docctl.py render
python scripts/contextctl.py render
python scripts/evolutionctl.py render
```

`codexctl.py` has no `validate`, `render`, or `check-generated` command. It exposes `status`, `build`, and `clear`.

## Duplicated Logic

The current ctl scripts duplicate several control-plane concerns:

- Path helpers for `AI_PROJECT/state`, `AI_PROJECT/events`, and `AI_PROJECT/generated`.
- `atomic_write_text()` implementations.
- JSON read/write helpers.
- Event append helpers and event field construction.
- Revision handling and mutation transaction shape.
- Generated Markdown rendering and generated-header checks.
- CLI parser construction and command metadata.
- Status transition tables in plan, task, and evolution domains.
- Error formatting and stable error-code conventions.

This duplication is functional today, but it makes a future Web Control Center risky unless all writes are moved behind a shared command/service layer.

## ID, Ref, UID Allocation And Collision Risks

Current identity behavior:

- Plan IDs are allocated by scanning existing IDs with a prefix and choosing the next numeric suffix, for example `INIT-002` or `EPIC-005`.
- Task IDs are allocated by scanning existing `TASK-*` IDs and choosing the next numeric suffix.
- Task `uid` values use `tsk_` plus a UUID-derived suffix.
- Task `legacy_id` preserves the original `TASK-*` identifier.
- Task `aliases` include the legacy task ID.
- Task `ref`, `epic_key`, and `local_seq` are populated only when the parent Epic has a key and identity migration or creation rules apply.
- `EPIC-004` currently has key `TIG`, producing refs such as `TIG-01`.
- `EPIC-005` currently has no key, so `TASK-019` has no `ref`, `epic_key`, or `local_seq`.

Validation behavior:

- `taskctl.py validate` checks duplicate task IDs.
- It checks duplicate task UIDs, refs, aliases, and duplicate local sequences for keyed epics.
- `taskctl.py task resolve` can resolve by `id`, `uid`, `ref`, `legacy_id`, or alias.
- Ambiguous refs are rejected with `AMBIGUOUS_TASK_REF`.
- Missing refs are rejected with `TASK_REF_NOT_FOUND`.

Collision risks:

- ID allocation is scan-based and not locked. Parallel task creation can race.
- Event append is not locked. Parallel writes can interleave audit lines even if JSON remains valid.
- State save, event append, and generated render are not one atomic transaction.
- Unkeyed epics do not get short local refs, so humans and agents fall back to global `TASK-*` IDs.
- If future web writes call command code concurrently, the current scan-based allocation is not sufficient.

## Parallel Execution Risks

Current risks for parallel operations:

- No file lock around protected state mutation.
- No central transaction boundary across state/events/generated.
- No shared command registry that declares read/write behavior.
- No unified dry-run or preflight path for every command.
- Context Pack and Codex prompt/status can drift from the selected current task if context is not refreshed.
- `planctl.py` lacks a dedicated generated-output freshness command.
- Multiple scripts independently implement validation and rendering, so future behavior can drift across domains.

## Unsafe Or Ambiguous Paths

No manual protected-file edits were required for this inventory. The risky paths are architectural:

- Each ctl script directly writes its own JSON, JSONL, and generated Markdown paths instead of calling a shared store/event/render service.
- `contextctl.py` has no state JSON but writes generated files and audit events derived from docs/tasks state, which makes freshness sensitive to both docs and tasks revisions.
- `codexctl.py build --with-context` can leave `CODEX_STATUS.md` in a blocked state when the Context Pack is stale for the requested task. That happened during this inventory for `TASK-019` because the existing pack was for `TASK-010`.
- `taskctl.py prompt build --write` can refresh `CODEX_PROMPT.md` independently of `codexctl.py`, leaving `CODEX_PROMPT.md` and `CODEX_STATUS.md` with different status semantics.
- Documentation control can validate with warnings. Some warnings are legitimate documentation lifecycle drift, but they do not currently block task execution.

## Recommended Migration Order Toward `aictl`

1. Keep legacy ctl scripts as the compatibility contract until shared services are proven.
2. Extract shared read/write/event/render primitives into a core package.
3. Add a shared result/error model with stable codes.
4. Add a command registry with command name, domain, read/write classification, argument schema, output mode, and affected files.
5. Add global ID allocation and locking before any web write actions.
6. Add `scripts/aictl.py` as a facade over the registry and services.
7. Convert legacy ctl scripts to wrappers over the shared services.
8. Add `project doctor` only after shared validation metadata can inspect all domains.
9. Add the read-only Web Control Center.
10. Add controlled web write actions only after registry, locking, audit, and doctor paths are stable.

## Open Questions For Next Design And ID-Allocation Tasks

- Should `EPIC-005` receive a short key before more control-plane tasks are executed, so tasks can use refs such as `ACP-01` or `CTL-01`?
- Should global task IDs remain the canonical machine IDs while human-facing refs become epic-scoped aliases?
- Should ID allocation write explicit audit events separate from entity creation?
- Should every write command expose a dry-run mode before web integration?
- Should `codexctl.py` become the only writer of `CODEX_PROMPT.md`, with `taskctl.py prompt build --write` kept as a compatibility wrapper?
- Should `contextctl.py` provide a task-aware refresh command that `codexctl.py --with-context` can call, or should stale context always be a blocker?
- Should `planctl.py` gain `check-generated` before or during the unified doctor work?
- What is the first acceptable locking primitive for local-only use: lock file, `fcntl`, or a standard-library cross-platform fallback?

## Commands Used

Selection and lifecycle:

```bash
python scripts/taskctl.py validate
python scripts/taskctl.py task graph validate
python scripts/taskctl.py task executable --json
python scripts/taskctl.py task next --json
python scripts/taskctl.py task list --json
python scripts/taskctl.py current show --json
python scripts/taskctl.py task resolve TASK-019 --json
python scripts/taskctl.py task show TASK-019
python scripts/taskctl.py current set TASK-019
python scripts/taskctl.py task transition TASK-019 --to in_progress
python scripts/codexctl.py build --task TASK-019 --with-context
python scripts/taskctl.py prompt build --task TASK-019 --write
```

Inventory:

```bash
python scripts/planctl.py --help
python scripts/taskctl.py --help
python scripts/taskctl.py task --help
python scripts/taskctl.py task deps --help
python scripts/taskctl.py task graph --help
python scripts/codexctl.py --help
python scripts/contextctl.py --help
python scripts/evolutionctl.py --help
python scripts/docctl.py --help
ls scripts/*ctl.py
find AI_PROJECT/state -maxdepth 1 -type f -name "*.json" -print
find AI_PROJECT/events -maxdepth 1 -type f -name "*.jsonl" -print
find AI_PROJECT/generated -maxdepth 1 -type f -name "*.md" -print
rg "add_parser\\(" scripts/*.py
rg "atomic_write_text|write_json|append_event|render_" scripts/*ctl.py
python scripts/taskctl.py migrate identity --dry-run
python scripts/taskctl.py task resolve tsk_d0e6e78d3c7c --json
python scripts/taskctl.py task deps list TASK-019 --json
python scripts/planctl.py epic list
python scripts/contextctl.py status
python scripts/codexctl.py status
```

## Files Changed

Source report:

- `ai-system/project-control/control-plane-inventory.md`

Protected files changed only through CLI lifecycle and prompt-package commands:

- `AI_PROJECT/state/tasks.json`
- `AI_PROJECT/events/task-events.jsonl`
- `AI_PROJECT/generated/CODEX_CURRENT.md`
- `AI_PROJECT/generated/CODEX_TASKS.md`
- `AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md`
- `AI_PROJECT/generated/CODEX_PROMPT.md`

The attempted `codexctl.py build --task TASK-019 --with-context` also updated Codex execution status through `codexctl.py` before reporting the context mismatch:

- `AI_PROJECT/state/current_execution.json`
- `AI_PROJECT/events/codex-events.jsonl`
- `AI_PROJECT/generated/CODEX_STATUS.md`

## Acceptance Criteria Status

- Existing ctl surface is documented: satisfied.
- Write paths are known: satisfied.
- Gaps and unsafe paths are listed: satisfied.
- No code behavior changed: satisfied.

## Review Notes

- This report is a source document and was edited directly because it is the selected task's allowed file.
- Protected state, event, and generated files were not edited manually.
- `CODEX_STATUS.md` remains blocked because the preferred context-aware `codexctl.py` build detected that the current Context Pack belongs to `TASK-010`, not `TASK-019`.

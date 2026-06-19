# Unified Project Control Plane Architecture

## Status

Draft

## Purpose

This document defines the target architecture for a unified local control plane for
AI Development System project control.

It began as the design artifact for `TASK-020`. Later bounded Tasks implemented
`scripts/aictl.py`, the `ai_project_ctl/` package, command registry support,
workflow helpers and the local Web Control Center. This document remains an
architecture reference and does not authorize future behavior change without
controlled evolution approval.

## Source Documents

This design is based on:

- `ai-system/project-control/01-overview.md`
- `ai-system/project-control/02-domain-model.md`
- `ai-system/project-control/03-state-model.md`
- `ai-system/project-control/04-command-catalog.md`
- `ai-system/project-control/05-lifecycle-rules.md`
- `ai-system/project-control/06-prompt-package-spec.md`
- `ai-system/project-control/07-validation-and-tests.md`
- `ai-system/project-control/08-usage-guide.md`
- `ai-system/project-control/09-task-identity-and-execution-graph.md`
- `ai-system/project-control/control-plane-inventory.md`

## Scope

This architecture covers:

- `scripts/aictl.py` as the preferred unified CLI facade.
- `ai_project_ctl/core` as the shared command, store, event, validation,
  rendering, ID, lock, result, and transaction layer.
- `ai_project_ctl/domains` as domain services for plan, epics, tasks, docs,
  changes, reviews, evolution, Codex execution, and context.
- A shared command registry used by CLI wrappers, the unified facade, tests,
  workflows and the local Web Control Center.
- A shared state, event, generated-output, validation, error/result, locking,
  and atomic-write model.
- A compatibility strategy for the existing `planctl.py`, `taskctl.py`,
  `docctl.py`, `contextctl.py`, `codexctl.py`, and `evolutionctl.py` scripts.
- Boundaries for the local Web Control Center.

## Out Of Scope

This reference does not authorize:

- new command behavior outside registered commands;
- refactoring existing ctl scripts outside approved Tasks;
- changing lifecycle states or approval semantics;
- changing protected file policy;
- changing task identity behavior;
- changing who writes `CODEX_PROMPT.md`;
- automatic execution, dispatch, merge, pull request creation, review closure,
  QA closure, approval, acceptance, or task completion.

Any future expansion of this architecture must be represented as approved
Evolution Change and bounded executable Tasks before source behavior changes.

## Current Inventory Summary

The existing control plane is split across:

```text
scripts/planctl.py
scripts/taskctl.py
scripts/docctl.py
scripts/contextctl.py
scripts/codexctl.py
scripts/evolutionctl.py
```

Those scripts currently own separate state, events, generated files, parser
definitions, validation logic, renderers, event appenders, JSON writers, and
result formatting.

The inventory found these key risks:

- State, event, and generated-output helpers are duplicated per script.
- ID allocation is scan-based and not protected by a shared lock.
- Event append and state write are not managed by one shared transaction layer.
- Render paths are domain-specific and can drift.
- `planctl.py` has no dedicated `check-generated` command.
- `taskctl.py` and `codexctl.py` can both write `CODEX_PROMPT.md`.
- Context Pack freshness can block `codexctl.py` while other prompt paths still
  remain available.
- Shared command registry coverage now exists for `aictl.py`, workflow helpers
  and Web Control Center actions, but future domains still need explicit
  registered command contracts.

The target architecture keeps current scripts stable while moving future writes
behind one shared control kernel.

## Source Of Truth Boundary

The unified control plane preserves the existing source-of-truth model:

```text
AI_PROJECT/state/*.json      = canonical current machine state
AI_PROJECT/events/*.jsonl    = append-only audit history
AI_PROJECT/generated/*.md    = derived readable output
```

`AI_PROJECT/generated/*.md` is derived output. Generated Markdown may be read by
humans and AI agents, deleted, and regenerated through the owning command, but it
must not be edited manually and must not be treated as source of truth.

The source documents under `ai-system/**` continue to define system rules,
processes, lifecycles, and architecture. Root `AI_PROJECT/**` continues to store
self-hosted project-control state for this repository.

Reusable templates under `ai-system/templates/**/AI_PROJECT` and examples under
`examples/golden-project/AI_PROJECT` are not live state for this repository.

## Architectural Overview

Target structure:

```text
scripts/
  aictl.py                    # unified CLI facade
  planctl.py                  # legacy-compatible wrapper
  taskctl.py                  # legacy-compatible wrapper
  docctl.py                   # legacy-compatible wrapper
  contextctl.py               # legacy-compatible wrapper
  codexctl.py                 # legacy-compatible wrapper
  evolutionctl.py             # legacy-compatible wrapper

ai_project_ctl/
  core/
    paths.py                  # root and protected-path resolution
    registry.py               # command registry and metadata
    result.py                 # stable command result and error model
    store.py                  # JSON state loading and atomic writes
    events.py                 # event IDs and append-only audit writes
    generated.py              # generated-output rendering contracts
    validation.py             # state, lifecycle, cross-domain validation
    transactions.py           # shared mutation pipeline
    locks.py                  # lock acquisition and stale write protection
    ids.py                    # ID, UID, ref, alias allocation and resolution
    schemas.py                # schema adapters and version checks
    output.py                 # human and JSON output formatting

  domains/
    plan.py                   # project, idea, goal, strategy
    epics.py                  # initiatives, epics, epic keys
    tasks.py                  # tasks, current task, dependencies, queue
    docs.py                   # registered documentation lifecycle
    context.py                # deterministic Context Pack services
    codex.py                  # Codex execution package/status services
    evolution.py              # Change Proposal services
    changes.py                # future shared change domain facade
    reviews.py                # future review lifecycle services
    qa.py                     # future QA lifecycle services
    decisions.py              # future decision records
    releases.py               # future release records

  web/
    server.py                 # local-only Web Control Center
    views.py                  # read models over registry queries
    actions.py                # write actions routed through registry
```

This tree is both the original target design and, for implemented areas, the
current package layout. New domains or behavior still require bounded Tasks.

## `scripts/aictl.py` Facade

`scripts/aictl.py` is the preferred unified entrypoint for command discovery,
project doctor, supported task/current/context/Codex commands, workflow helpers
and local Web Control Center startup.

Responsibilities:

- Parse common global options such as `--root`, `--actor`, `--json`,
  `--dry-run`, and `--verbose`.
- Resolve command paths through the command registry.
- Invoke domain services through the shared transaction layer.
- Return stable human-readable or JSON command results.
- Provide discoverability for domains, commands, affected files, validation
  requirements, and generated outputs.
- Expose cross-domain utility commands such as validation, render, doctor, audit,
  and status once those commands are backed by registry metadata.

Example target shapes:

```bash
python scripts/aictl.py task show TASK-020
python scripts/aictl.py task transition TASK-020 --to in_review
python scripts/aictl.py plan validate
python scripts/aictl.py generated check --domain task
python scripts/aictl.py project doctor
```

The facade must not create new lifecycle behavior by itself. It is only a
router over registered commands.

## Core Package

`ai_project_ctl/core` is the control kernel shared by every future entrypoint.

### Paths Service

The paths service owns repository-root resolution and protected file locations.

It should expose stable path objects for:

- `AI_PROJECT/state`
- `AI_PROJECT/events`
- `AI_PROJECT/generated`
- source-document roots such as `ai-system`
- lock files
- temporary write files

The paths service must keep live root `AI_PROJECT` separate from templates and
examples.

### Store Service

The store service owns JSON state reads and writes.

Responsibilities:

- Load state by domain.
- Reject invalid JSON with stable errors.
- Track state revision before and after mutation.
- Write state atomically with temp-file, fsync, and replace.
- Never write generated Markdown or event logs as state.
- Support in-memory snapshots for validation and dry-run.

### Event Service

The event service owns audit event construction and append.

Responsibilities:

- Allocate stable event IDs.
- Append JSONL audit records.
- Use one event schema per command result.
- Preserve append-only history.
- Reject invalid event payloads before append.
- Run under the same lock as related state mutation.

Events are audit history, not editable state. Incorrect history must be
corrected by a new event, never by rewriting old events.

### Generated Output Service

The generated-output service owns renderer registration and freshness checks.

Responsibilities:

- Map each generated file to its source state and renderer.
- Render generated Markdown from current state.
- Include standard generated-file warning headers.
- Compare expected generated output with files on disk.
- Report drift with stable errors.

Generated output is disposable and derived from state. If a generated file is
wrong, the owning command must regenerate it; humans, AI agents, and Web UI must
not edit it manually.

### Validation Service

The validation service owns shared validation mechanics.

Validation layers:

- JSON syntax validation.
- Schema and required-field validation.
- Lifecycle status validation.
- Lifecycle transition validation.
- Parent-reference validation.
- Task dependency graph validation.
- Task identity, UID, ref, alias, and local sequence validation.
- Current task compatibility validation.
- Generated-output freshness validation.
- Context Pack freshness validation.
- Protected-file bypass detection.
- Cross-domain consistency validation.

Validation should produce structured blocking errors and non-blocking warnings.
Warnings must not silently become approval.

### ID And Resolver Service

The ID service owns allocation and reference resolution.

Responsibilities:

- Allocate IDs under lock.
- Allocate immutable task UIDs.
- Allocate event IDs.
- Allocate or validate epic-scoped human refs when the identity model requires
  them.
- Resolve task references through one shared resolver.
- Reject duplicate IDs, UIDs, refs, aliases, and ambiguous references.

Scan-based allocation may remain as compatibility behavior inside wrappers, but
future write paths must allocate IDs while holding the relevant lock.

### Lock Service

The lock service owns concurrency protection.

Minimum target behavior:

- Acquire locks before reading a mutable state snapshot for a write command.
- Use deterministic lock ordering for multi-domain commands.
- Hold locks through validation, event append, state mutation, generated render,
  and result construction.
- Fail clearly if a lock cannot be acquired.
- Keep locks local to the repository.

Initial local implementation may use a lock file plus platform-appropriate file
locking. The exact primitive is an implementation decision for a later task.

### Transaction Service

The transaction service owns the shared mutation pipeline.

Required mutation flow:

```text
Command -> Validate -> Append Event -> Mutate State -> Regenerate Views -> Return Result
```

Meaning:

1. Command: resolve a registered command, parse arguments, identify actor,
   domain, lock scope, affected state, event log, generated outputs, and output
   mode.
2. Validate: load current state, validate current state, validate command
   arguments, check lifecycle rules, check parent references, and check command
   preconditions.
3. Append Event: construct and append the success audit event for the accepted
   mutation under the transaction lock.
4. Mutate State: apply the mutation through the domain service and atomically
   write the updated JSON state.
5. Regenerate Views: regenerate affected `AI_PROJECT/generated/*.md` outputs
   from the new valid state.
6. Return Result: return a stable `CommandResult` containing revisions, event
   IDs, changed files, generated files, warnings, and next actions.

The transaction service must ensure failed validation does not append a success
event, does not mutate state, and does not render generated output from invalid
state.

Because this design requires event append before state mutation, the future
implementation must protect the event/state/render sequence with a lock and a
clear recovery strategy. If implementation evidence later shows that physical
commit order should differ while preserving the external command contract, that
must be approved as controlled evolution.

## Command Registry

The command registry is the single catalog of allowed commands.

Every command should register metadata:

- command path, for example `task.show`;
- owning domain;
- read, write, render, validation, audit, or utility classification;
- argument schema;
- required state files;
- event log path;
- generated files affected;
- renderer functions affected;
- validators required before execution;
- validators required after execution;
- lifecycle transitions allowed;
- owner approval gate, if any;
- lock scope;
- dry-run support;
- JSON output support;
- legacy command compatibility mapping;
- final result shape.

The registry must be authoritative for future CLI facade and Web UI actions. If
a requested operation is not registered, the system must report
`NO_ALLOWED_COMMAND` rather than editing protected files directly.

## Domain Services

Domain services own business behavior. They should not parse command-line
arguments directly and should not write files directly. They receive validated
input and snapshots from core services, then return proposed state changes,
events, generated-output requests, and results.

### Plan And Epic Services

Plan services own:

- project identity;
- idea;
- goal;
- strategy;
- initiatives;
- epics;
- future epic keys.

Epics and initiatives remain planning containers. They are not executable work.

### Task Service

Task services own:

- task creation and updates;
- task lifecycle;
- current task pointer;
- task prompt fields;
- dependencies;
- executable queue;
- task identity, UID, ref, legacy ID, alias, and local sequence rules.

Only Tasks are executable. The task service must preserve the rule that
Initiatives, Epics, Change Proposals, Reviews, QA Results, Decisions, and
Releases are not executable units.

### Documentation Service

Documentation services own:

- documentation registry state;
- document lifecycle status;
- document content hashes;
- declared status metadata;
- document review records;
- `DOCS_INDEX.md`;
- `DOCS_GAPS.md`.

Generated docs views remain derived output and must not be manually edited.

### Context Service

Context services own deterministic retrieval context:

- source document indexing from registered docs;
- task-scoped or query-scoped context selection;
- `CONTEXT_PACK.md`;
- `CONTEXT_STATUS.md`;
- context events.

Context Packs are read-only derived retrieval output. They do not expand Task
scope, allowed files, out-of-scope items, or acceptance criteria.

### Codex Service

Codex services own:

- current execution state;
- Codex prompt package status;
- `CODEX_PROMPT.md` when routed through Codex execution package behavior;
- `CODEX_STATUS.md`;
- optional validation of existing Context Packs before prompt inclusion.

The architecture should resolve the current dual-writer ambiguity for
`CODEX_PROMPT.md` in a later approved implementation task. Until then, existing
`taskctl.py prompt build --write` and `codexctl.py build` behavior must remain
compatible.

### Evolution And Change Services

Evolution services own:

- Change Proposal lifecycle;
- approval gates;
- affected files, risks, impact, migration, compatibility, and rationale;
- linked tasks;
- `EVOLUTION.md`;
- evolution audit events.

Changes to AI Development System behavior still require controlled evolution.
The unified control plane must not make system evolution automatic.

### Review And QA Services

Review and QA services are future domains.

They should eventually own:

- review records;
- review findings;
- review status;
- QA evidence;
- verification summaries;
- waivers;
- generated review and QA views.

They must not approve, accept, or close work on behalf of the Human Owner unless
a future approved policy explicitly delegates a narrow operation.

## Validation Model

Validation should be explicit, layered, and reusable.

Target command classes:

- `validate domain`: validate one domain state.
- `validate all`: validate all registered domains.
- `generated check`: check generated output freshness for registered renderers.
- `graph validate`: validate task dependencies.
- `doctor`: run cross-domain diagnostics and protected-file checks.

Blocking validation failures should stop write commands before events, state, or
generated output are changed.

Non-blocking warnings should be returned in the command result with stable
codes. Warnings must not change lifecycle status or imply owner acceptance.

Cross-domain validation should include:

- Task parent Epic exists.
- Parent Initiative is not incompatible with child status.
- Current Task points to an allowed status.
- Generated task files match task state.
- Context Pack metadata matches current docs/tasks revisions when used.
- Codex status and prompt package state are consistent where applicable.
- Evolution Changes reference existing linked Tasks.
- Documentation generated files match docs state.

## Error And Result Model

All command entrypoints should return a shared result shape.

Target JSON structure:

```json
{
  "ok": true,
  "command": "task.transition",
  "domain": "task",
  "message": "OK: task transition TASK-020 in_progress -> in_review",
  "data": {},
  "warnings": [],
  "errors": [],
  "changed_files": [],
  "generated_files": [],
  "events": [],
  "revision_before": 42,
  "revision_after": 43,
  "owner_action_required": null,
  "next_actions": []
}
```

Failure shape:

```json
{
  "ok": false,
  "command": "task.transition",
  "domain": "task",
  "message": "VALIDATION_FAILED",
  "data": {},
  "warnings": [],
  "errors": [
    {
      "code": "INVALID_STATUS_TRANSITION",
      "message": "Cannot transition proposed -> done.",
      "path": "tasks[0].status"
    }
  ],
  "changed_files": [],
  "generated_files": [],
  "events": [],
  "revision_before": 42,
  "revision_after": 42,
  "owner_action_required": null,
  "next_actions": []
}
```

Stable error codes should be preserved across CLI, JSON output, tests, and Web
UI. Human-readable wording may improve, but machine-readable codes should remain
stable unless a controlled migration is approved.

## Locking And Atomic Writes

Future write commands must be safe for local concurrent use before web writes
are enabled.

Target rules:

- Every write command declares a lock scope in the registry.
- Multi-domain commands acquire locks in deterministic order.
- ID allocation happens under lock.
- State snapshots are validated after lock acquisition.
- JSON state writes use temp files, fsync, and atomic replace.
- Event append happens under lock.
- Generated Markdown writes use temp files and atomic replace.
- The result reports every protected file changed by the command.
- Failed commands leave previous valid state intact.

Recommended lock scopes:

```text
project          cross-domain operation
plan             plan.json and plan-events/generated
task             tasks.json and task-events/generated
docs             docs.json and doc-events/generated
context          context events/generated
codex            current_execution.json and codex events/generated
evolution        evolution.json and evolution events/generated
```

Locking must protect local repository state only. It does not authorize remote
automation, external services, or autonomous execution.

## Legacy Ctl Wrapper Strategy

The existing ctl scripts are the compatibility contract and must remain usable
while the unified control plane is introduced.

Migration strategy:

1. Preserve current script names and command syntax.
2. Add shared core services behind the existing behavior in bounded tasks.
3. Move one domain at a time to call shared services.
4. Keep output compatible unless an approved change explicitly updates output.
5. Add tests proving wrapper behavior before and after migration.
6. Add `scripts/aictl.py` only after enough registry coverage exists.
7. Make `aictl.py` the preferred facade through documentation after parity.
8. Keep legacy wrappers as stable aliases until Human Owner approves
   deprecation.

Wrapper constraints:

- Wrappers must not keep independent write paths after migration.
- Wrappers must not bypass the registry.
- Wrappers must not edit protected files directly.
- Wrappers must not invent behavior that `aictl.py` cannot invoke.
- Wrappers must preserve Human Owner gates.

## Local Web Control Center

The Web Control Center is a local loopback UI over the same command registry
and facade commands.

It should provide readable views for:

- current Task;
- executable queue;
- plan and Epics;
- task dependency graph;
- Codex prompt/status;
- Context Pack status;
- documentation gaps;
- evolution Change Proposals;
- review and QA status when those domains exist.

The Web UI must not edit JSON directly.

The Web UI must not edit `AI_PROJECT/state/*.json`,
`AI_PROJECT/events/*.jsonl`, or `AI_PROJECT/generated/*.md` directly. All write
actions must route through the same command registry used by `aictl.py` and the
legacy wrappers.

Controlled Web write actions must:

- show the registered command that will run;
- validate preconditions before mutation;
- write the same audit events;
- regenerate the same generated views;
- return the same structured results;
- keep owner approval and acceptance gates explicit.

Generated Markdown displayed in the Web UI must be read-only and labeled as
derived output. If it is stale, the UI may offer a registered regenerate command,
but it must not patch generated Markdown directly.

The implemented Web Control Center has read views and confirmed write actions
for registered commands such as task creation/import, task transitions, current
task selection, project render, context build, Codex prompt build, Prepare for
Codex, submit/close review helpers, Evolution Change creation/acceptance and
Epic close-if-complete. It must continue to reject arbitrary file write fields.

## Security And Authority Boundaries

The unified control plane remains local-first project control.

It must not authorize:

- autonomous task execution;
- automatic Worker Agent dispatch;
- automatic branch or worktree creation;
- automatic merge;
- automatic push;
- automatic pull request creation;
- automatic review closure;
- automatic QA closure;
- automatic Human Owner acceptance.

Human Owner authority remains required for:

- project direction;
- strategy;
- approval of executable work;
- acceptance of completed work;
- lifecycle changes;
- command catalog changes;
- protected file policy changes;
- Web Control Center write capability policy;
- AI Development System evolution.

## Migration Order

Recommended migration order:

1. Keep current ctl scripts unchanged and add regression tests around current
   behavior.
2. Extract shared path, JSON store, atomic write, event, generated-output, and
   result helpers.
3. Add command registry metadata without changing public behavior.
4. Add shared validation adapters and generated-output freshness metadata.
5. Add shared ID allocation and task reference resolver under lock.
6. Add transaction service with lock-aware command execution.
7. Convert `planctl.py` to shared services.
8. Convert `taskctl.py` to shared services.
9. Convert `docctl.py`, `contextctl.py`, `codexctl.py`, and `evolutionctl.py`.
10. Keep expanding `scripts/aictl.py` facade coverage after registry coverage is sufficient.
11. Keep cross-domain doctor and generated checks current.
12. Maintain the local Web Control Center as a command-gated surface.
13. Add new controlled web write actions only after Human Owner approval and
    after audit, validation and protected-file checks prove stable for the
    underlying command.

Each implementation phase must be a separate bounded Task or task group under an
approved Evolution Change.

## Design Decisions

1. `aictl.py` should be a facade, not a new independent control implementation.
2. `ai_project_ctl/core` should own shared infrastructure for all command
   entrypoints.
3. Domain services should own project-control behavior without parsing CLI
   arguments or writing files directly.
4. The command registry should be the allowed-command catalog for CLI, wrappers,
   tests, workflows and Web UI actions.
5. `AI_PROJECT/state/*.json` remains canonical current state.
6. `AI_PROJECT/events/*.jsonl` remains append-only audit history.
7. `AI_PROJECT/generated/*.md` remains derived output and must not be edited
   manually.
8. The required mutation flow is:

```text
Command -> Validate -> Append Event -> Mutate State -> Regenerate Views -> Return Result
```

9. Locking and atomic writes are required before concurrent or web write paths
   are safe.
10. Existing ctl scripts remain compatibility wrappers during migration.
11. The Web Control Center must route all mutations through the command registry.
12. The Web UI must not edit JSON directly.
13. Future expansion still requires controlled evolution approval where
    command behavior, lifecycle rules, protected-file policy, or system behavior
    changes.

## Risks And Open Questions

- The exact local lock primitive must be selected in a later implementation
  task.
- The event-before-state mutation flow requires careful transaction and recovery
  design.
- `CODEX_PROMPT.md` currently has two write paths; future ownership should be
  settled before wrapper migration.
- `planctl.py` still lacks a dedicated `check-generated` command.
- New or unregistered Web write actions should remain disabled until audit,
  result, validation and protected-file behavior are proven by tests.
- Review, QA, decision and release domains still need separate approved designs
  before implementation.

## Review Checklist

Review should verify that this document:

- preserves existing project-control source-of-truth boundaries;
- keeps generated Markdown as derived output only;
- states that Web UI cannot bypass the command layer;
- states that Web UI must not edit JSON directly;
- defines the required mutation flow;
- defines `scripts/aictl.py` as a facade, not an implementation shortcut;
- defines shared core services, domain services, command registry, validation,
  result/error model, locks, and atomic writes;
- keeps existing ctl scripts as compatibility wrappers;
- does not implement code or create package/web files;
- states that future implementation still requires controlled evolution approval
  where behavior changes.

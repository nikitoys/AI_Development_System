# Global ID Allocation Strategy

## Status

Draft

## Purpose

This document defines the global ID allocation strategy for the future unified
Project Control Gateway control plane.

It is the design artifact for `TASK-021`. It does not implement `ids.py`,
create `ai_project_ctl/`, implement `scripts/aictl.py`, refactor existing
`*ctl.py` scripts, change command behavior, migrate existing task IDs, create
web files, or authorize concurrent web write actions.

## Source Documents

This design is based on:

- `ai-system/project-control/control-plane-inventory.md`
- `ai-system/project-control/control-plane-architecture.md`
- `ai-system/project-control/09-task-identity-and-execution-graph.md`
- TASK-021 fields from `python scripts/taskctl.py task show TASK-021`

## Scope

This document covers:

- global versus scoped ID policy for project-control entities;
- task `id`, `uid`, `legacy_id`, `aliases`, `epic_key`, `local_seq`, and `ref`;
- event ID expectations;
- entity ID prefixes for initiatives, epics, tasks, changes, documents, reviews,
  QA results, and related future control entities;
- uniqueness, allocation, locking, validation, and audit-event rules;
- the future responsibilities of `ai_project_ctl/core/ids.py`;
- parallel task and epic creation collision prevention;
- migration expectations for existing tasks.

## Out Of Scope

This document does not authorize:

- implementing `ai_project_ctl/core/ids.py`;
- implementing `scripts/aictl.py`;
- creating `ai_project_ctl/`;
- refactoring existing ctl scripts;
- changing current `planctl.py`, `taskctl.py`, `docctl.py`, `contextctl.py`,
  `codexctl.py`, or `evolutionctl.py` behavior;
- creating web files;
- migrating existing task IDs;
- manually editing `AI_PROJECT/state/**`, `AI_PROJECT/events/**`, or
  `AI_PROJECT/generated/**`.

## Current State Summary

The current repository already has a partial identity model:

- Plan IDs are allocated by scanning existing IDs and choosing the next numeric
  suffix, such as `INIT-002` or `EPIC-005`.
- Task IDs are allocated by scanning existing `TASK-*` IDs and choosing the next
  numeric suffix.
- Task `uid` values use a `tsk_` prefix plus a generated suffix.
- Task `legacy_id` preserves the original `TASK-*` identifier.
- Task `aliases` include the legacy task ID.
- `taskctl.py task resolve` resolves tasks by `id`, `uid`, `ref`, `legacy_id`,
  and aliases.
- `taskctl.py validate` checks duplicate task IDs, UIDs, refs, aliases, and
  duplicate local sequences for keyed epics.
- `EPIC-004` currently has key `TIG`, producing refs such as `TIG-01`.
- `EPIC-005` currently has no key, so `TASK-021` has no `ref`, `epic_key`, or
  `local_seq`.

The collision risk is that current allocation is scan-based without one shared
lock or transaction layer. Parallel CLI or future web writes can race unless ID
allocation happens under the same lock that protects validation, state writes,
event append, and generated-output rendering.

## Allocation Principles

1. Every durable project-control entity must have one stable primary `id`.
2. Task IDs remain globally unique `TASK-XXX` identifiers across all epics.
3. Epic-scoped task refs are readable aliases, not scoped machine IDs.
4. `uid` is the immutable machine identity for durable references where a stable
   opaque identifier is safer than a readable ID.
5. Existing `TASK-XXX` references remain valid indefinitely.
6. No ID, UID, ref, legacy ID, or alias may resolve ambiguously.
7. ID allocation must happen while holding the relevant project-control lock.
8. A dry run may show a candidate ID, but it must not reserve that ID.
9. IDs, refs, aliases, and event IDs must never be reused after archival.
10. Generated Markdown may display identities, but it is not used for allocation
    or resolution.

## ID And Reference Taxonomy

| Field | Applies to | Meaning | Uniqueness |
| --- | --- | --- | --- |
| `id` | Durable entities | Primary command-visible entity ID, such as `TASK-021`. | Unique in its entity family and prefix namespace. |
| `uid` | Tasks and future durable entities where needed | Immutable opaque machine identity. | Globally unique within the project. |
| `legacy_id` | Migrated or compatibility entities | Historical ID that must keep resolving. | Unique in the resolver for that entity type. |
| `aliases` | Resolvable entities | Additional accepted references for the same entity. | Globally unique in that entity resolver. |
| `epic_key` | Epics and tasks | Stable readable epic prefix, such as `TIG`. | Unique across active and historical epics. |
| `local_seq` | Tasks under keyed epics | Integer sequence within one `epic_key`. | Unique within one `epic_key`. |
| `ref` | Tasks and future human-facing child entities | Primary human-readable reference, such as `TIG-01`. | Globally unique in that entity resolver. |
| `event_id` | Audit events | Unique audit-event identifier. | Globally unique across project-control events. |

### `id`

`id` is the primary command-visible identity for an entity.

Examples:

```text
INIT-001
EPIC-005
TASK-021
CHG-001
```

Rules:

- `id` uses an entity-specific uppercase prefix and zero-padded numeric suffix.
- `id` is allocated by the owning command service.
- `id` must not be scoped by Epic or parent entity.
- `id` must not imply execution order or priority.
- `id` must not be reused after an entity is done, archived, rejected, or
  superseded.

For Tasks, `TASK-XXX` remains globally unique across all Epics. It is not
replaced by epic-local numbering.

### `uid`

`uid` is an immutable opaque identity for durable machine references.

Current task examples use:

```text
tsk_c04df4f0310f
```

Rules:

- `uid` is generated once at creation time.
- `uid` never changes after creation.
- `uid` is globally unique inside the project.
- `uid` does not carry execution order, priority, or status.
- `uid` is preferred for internal durable references when a human-facing ID or
  ref may be renamed, migrated, hidden, or reformatted later.

Future entity families may use typed UID prefixes if implementation evidence
shows they are useful, for example `tsk_`, `epc_`, `chg_`, `doc_`, `rev_`, or
`qa_`. This document does not require adding those fields to existing state.

### `legacy_id`

`legacy_id` preserves an older accepted ID after an identity migration.

For current Tasks:

```text
id: TASK-021
legacy_id: TASK-021
aliases: TASK-021
```

Rules:

- existing `TASK-XXX` values remain accepted references indefinitely;
- a legacy ID must not be reassigned to another entity;
- a legacy ID must be included in the resolver uniqueness index;
- generated compact views may prefer `ref`, but detailed views, audit history,
  prompt packages, and resolver behavior must preserve legacy IDs.

### `aliases`

`aliases` are additional references that resolve to the same entity.

Rules:

- aliases must be globally unique inside the entity resolver;
- aliases must not collide with another entity's `id`, `uid`, `ref`, or
  `legacy_id`;
- aliases must not be silently removed while old prompts, audit events, or
  generated views may still reference them;
- aliases are compatibility references, not canonical scheduling data.

### `epic_key`

`epic_key` is the readable key used as a prefix for task refs.

Example:

```text
EPIC-004 / TIG
```

Rules:

- epic keys are uppercase ASCII letters and digits;
- epic keys start with a letter;
- epic keys are unique across active and historical epics;
- archived epic keys remain reserved forever;
- an epic key is immutable after the first task is created under the epic;
- unkeyed epics may continue using global `TASK-XXX` references until a future
  approved task assigns a key.

### `local_seq`

`local_seq` is the integer sequence inside one epic key.

Rules:

- `local_seq` is unique only within one `epic_key`;
- `local_seq` is not globally unique by itself;
- `local_seq` does not imply cross-epic execution order;
- `local_seq` is allocated under the task lock from the latest task snapshot;
- `local_seq` must not be reused after a task is archived or superseded.

### `ref`

`ref` is the primary human-readable task reference.

Canonical task ref format:

```text
<EPIC_KEY>-<LOCAL_SEQ>
```

Examples:

```text
TIG-01
TIG-02
```

Rules:

- `ref` is generated from `epic_key` and `local_seq`;
- canonical display uses at least two digits for the local sequence;
- `TIG-01` and `TIG-1` must not both be canonical references;
- `ref` is globally unique because epic keys are globally reserved;
- `ref` must not imply execution order;
- if an Epic has no key, new Tasks may continue with `ref: null` while resolving
  by global `TASK-XXX`, `uid`, `legacy_id`, or alias.

### `event_id`

`event_id` identifies one audit event.

Rules:

- future unified event IDs should be globally unique across all
  `AI_PROJECT/events/*.jsonl` files;
- event IDs are allocated under the same lock as the enclosing command event;
- event IDs are audit metadata and are not resolver aliases for project
  entities;
- failed commands must not write success events or consume externally visible
  semantic entity IDs;
- incorrect audit history must be corrected by appending a new event, never by
  editing an old event.

## Entity ID Prefixes

Target entity ID prefixes:

| Entity | Prefix | Example | Notes |
| --- | --- | --- | --- |
| Project | `PROJECT` | `PROJECT-001` | Usually initialized once. |
| Initiative | `INIT` | `INIT-002` | Global planning container ID. |
| Epic | `EPIC` | `EPIC-005` | Global planning container ID; `epic_key` is separate. |
| Task | `TASK` | `TASK-021` | Globally unique executable work ID. |
| Prompt package | `PROMPT` | `PROMPT-001` | Future prompt metadata ID if prompt state is added. |
| Execution session | `EXEC` | `EXEC-001` | Future execution attempt ID. |
| Change Proposal | `CHG` | `CHG-001` | Existing evolution-control style. |
| Document registry item | `DOC` | `DOC-001` | Future optional ID; current docs remain path-based. |
| Review | `REV` | `REV-001` | Future review lifecycle ID. |
| QA result | `QA` | `QA-001` | Future QA evidence ID. |
| Decision | `DEC` | `DEC-001` | Future decision record ID. |
| Release | `REL` | `REL-001` | Future release record ID. |
| Audit event | `EVT` | `EVT-000001` | Future global audit event ID. |

These prefixes are reserved. A future implementation must not introduce another
entity family using an existing prefix unless a controlled migration updates the
catalog and validators.

## Global Uniqueness Rules

Global uniqueness is enforced at two levels.

### Prefix Namespace Uniqueness

Every primary `id` must be unique inside its prefix namespace:

```text
INIT-001 unique among initiatives
EPIC-005 unique among epics
TASK-021 unique among tasks
CHG-001 unique among changes
```

Because prefixes are reserved per entity family, these IDs are also unambiguous
to humans and command routers.

### Resolver Token Uniqueness

Within any resolver that accepts flexible references, every accepted token must
resolve to exactly one entity.

For the Task resolver, the uniqueness index includes:

- `id`
- `uid`
- `ref`
- `legacy_id`
- every alias in `aliases`

Validation must fail if any token maps to more than one Task or if one Task's
alias conflicts with another Task's `id`, `uid`, `ref`, or `legacy_id`.

The same rule should be used by future resolvers for changes, documents,
reviews, QA results, executions, and releases if they accept aliases or legacy
references.

## Epic-Scoped Readable Ref Rules

Task refs are readable labels scoped by Epic key, but they remain globally
unambiguous because epic keys are globally reserved.

Rules:

1. A Task under a keyed Epic receives `epic_key`, `local_seq`, and `ref`.
2. `local_seq` is allocated from the maximum historical sequence for that
   `epic_key` plus one.
3. Archived and superseded Tasks still reserve their old `local_seq`.
4. The canonical ref is `EPIC_KEY` plus a hyphen plus zero-padded sequence.
5. A Task under an unkeyed Epic may have `ref: null`.
6. Adding a key to an Epic with existing Tasks is a migration operation and must
   be performed through a future bounded task, not by this design task.
7. Task refs do not define dependency order, execution order, priority, or
   parent Epic status.

Example:

```text
id: TASK-012
uid: tsk_...
legacy_id: TASK-012
epic_id: EPIC-004
epic_key: TIG
local_seq: 1
ref: TIG-01
aliases: TASK-012
```

## Legacy `TASK-XXX` Compatibility Rules

Existing `TASK-XXX` references must remain resolvable indefinitely.

Compatibility rules:

- `TASK-XXX` remains the global Task `id` in current state.
- `TASK-XXX` must also be stored as `legacy_id` for migrated Tasks.
- `TASK-XXX` should remain in `aliases` when useful for compatibility.
- CLI commands, prompt packages, generated reports, audit events, and review
  records may continue to show `TASK-XXX`.
- Compact generated views may show `ref (TASK-XXX)` when a human ref exists.
- No new Task may claim a legacy ID that already belongs to another Task.
- Removal or hiding of legacy IDs from generated views requires a separate
  approved system evolution decision.

## Allocation Under Lock

Future write commands must allocate IDs only inside the shared mutation
transaction.

Minimum flow:

```text
1. Resolve command metadata from the registry.
2. Determine required lock scopes.
3. Acquire locks in deterministic order.
4. Reload current state after locks are held.
5. Validate current state and command preconditions.
6. Allocate IDs, UIDs, refs, local sequences, and event IDs from the locked snapshot.
7. Validate the proposed identity index.
8. Append the success audit event under lock.
9. Atomically write updated state under lock.
10. Regenerate generated views under lock.
11. Return a structured command result with allocated identities and event IDs.
```

For commands that read plan state while mutating task state, such as task
creation under a keyed Epic, the lock order should be deterministic:

```text
plan -> task
```

Recommended lock scopes:

| Command | Lock scope |
| --- | --- |
| Initiative create | `plan` |
| Epic create | `plan` |
| Epic key assignment | `plan`, and `task` if child-task checks are required |
| Task create | `plan`, then `task` |
| Task identity migration | `plan`, then `task` |
| Change create | `evolution` |
| Review create | `review`, and `task` if task linkage is validated under lock |
| QA record create | `qa`, and `task` if task linkage is validated under lock |
| Prompt build with write | `task` or `codex`, depending on the owning command |

Initial implementation may keep scan-based numeric allocation if the scan is
performed after locks are acquired and against the latest state snapshot. A
future counter state, such as `AI_PROJECT/state/ids.json`, may be introduced only
through a separate approved evolution task.

Dry-run commands must not reserve identities. They may report candidate IDs with
a warning that candidates can change before a real write command acquires the
lock.

## Parallel Creation Collision Avoidance

Parallel task and epic creation must route through the same registry, locks, and
ID service.

### Parallel Epic Creation

Two concurrent Epic creates both require the `plan` lock.

Expected behavior:

1. The first command acquires the `plan` lock, reloads `plan.json`, allocates
   `EPIC-NNN`, writes state, appends an event, renders generated output, and
   releases the lock.
2. The second command then acquires the `plan` lock, reloads the updated
   `plan.json`, sees the newly allocated Epic, and allocates the next ID.

No two commands should ever allocate the same `EPIC-XXX`.

### Parallel Task Creation In Different Epics

Two concurrent Task creates under different Epics both require the `task` lock
and may also require the `plan` lock for stable parent and epic-key reads.

Expected behavior:

1. Both commands acquire locks in the same order: `plan -> task`.
2. Only one command allocates from `TASK-*` at a time.
3. The second command reloads task state after the first command commits.
4. The second command allocates the next global `TASK-XXX`.
5. If both Epics are keyed, each command also allocates the next `local_seq`
   within its own `epic_key`.

Global `TASK-XXX` IDs cannot collide because allocation is serialized by the
task lock. Epic-local refs cannot collide because `local_seq` is calculated from
the locked task snapshot for that `epic_key`.

### Parallel Task Creation In The Same Epic

Two concurrent Task creates under the same keyed Epic also serialize through the
task lock. The first receives the next `local_seq`; the second reloads and
receives the following `local_seq`.

## Validation Requirements

Future validation must reject:

- duplicate primary IDs inside any entity prefix namespace;
- duplicate Task `id`;
- duplicate Task `uid`;
- duplicate Task `ref`;
- duplicate Task `legacy_id`;
- duplicate Task alias;
- alias conflicting with another Task's `id`, `uid`, `ref`, or `legacy_id`;
- legacy ID conflicting with another Task's `id`, `uid`, `ref`, or alias;
- duplicate `epic_key`, including archived keys;
- duplicate `local_seq` inside one `epic_key`;
- `ref` that does not match `epic_key` and `local_seq`;
- invalid ID, UID, or ref format;
- missing `uid` where the schema requires it;
- missing `legacy_id` for migrated legacy Tasks;
- ambiguous task resolver tokens;
- duplicate `event_id` across project-control event logs;
- generated output that displays an identity not present in state;
- dependencies that reference missing or ambiguous task identities.

Validation must build an identity index from state, not generated Markdown.

For Tasks, a validation pass should conceptually build:

```text
token -> task uid
```

for every `id`, `uid`, `ref`, `legacy_id`, and alias. If a token maps to more
than one Task, validation fails before any write command can proceed.

## Future `ai_project_ctl/core/ids.py`

The future `ids.py` module should be a shared identity and resolver service.

It should not parse CLI arguments, write files directly, append events directly,
or bypass the transaction layer.

Target responsibilities:

- declare reserved entity prefixes;
- allocate numeric IDs for registered entity families;
- allocate immutable UIDs;
- allocate event IDs;
- allocate task `local_seq` and `ref` for keyed Epics;
- normalize input references where safe;
- build resolver indexes from locked state snapshots;
- resolve entity references to exactly one entity;
- validate duplicate IDs, UIDs, refs, aliases, legacy IDs, and local sequences;
- return stable structured errors for missing, duplicate, invalid, or ambiguous
  references;
- expose dry-run candidate allocation without reservation;
- preserve compatibility mappings for existing legacy IDs.

Suggested function boundaries:

```text
allocate_id(snapshot, entity_type) -> id
allocate_uid(entity_type) -> uid
allocate_event_id(event_snapshot) -> event_id
allocate_task_ref(plan_snapshot, task_snapshot, epic_id) -> epic_key, local_seq, ref
build_task_identity_index(task_snapshot) -> IdentityIndex
resolve_task(reference, task_snapshot) -> TaskIdentity
validate_task_identities(plan_snapshot, task_snapshot) -> ValidationResult
```

These names are illustrative only. A later implementation task may choose
different names if the responsibilities remain intact.

## Audit Event Policy

Ordinary ID allocation should not emit a separate audit event.

Instead, the enclosing successful mutation event should include the allocated
identity fields in its payload or structured result.

Examples:

- `task.create` event includes `id`, `uid`, `legacy_id`, `epic_key`,
  `local_seq`, `ref`, and aliases that were assigned.
- `epic.create` event includes `id` and `key` when a key is assigned at create
  time.
- `change.create` event includes `id` and optional `uid` if future change UIDs
  are added.

Rationale:

- allocation is part of one logical mutation;
- separate allocation events would create audit noise;
- failed commands must not leave committed entity-ID reservations;
- current project-control events already describe the command that created or
  updated the entity.

Separate reservation events should exist only if a future approved command
explicitly reserves IDs without creating entities. This design does not propose
such a command.

`event_id` allocation is different: every successful audit event receives an
event ID, but the act of assigning an event ID does not itself create another
audit event.

## Migration Expectations For Existing Tasks

TASK-021 does not migrate existing tasks.

Future migration must follow these expectations:

1. Preserve every existing `TASK-XXX` as the Task `id`.
2. Preserve every existing `TASK-XXX` as `legacy_id`.
3. Keep `TASK-XXX` in `aliases` where current compatibility requires it.
4. Preserve existing task `uid` values.
5. Preserve existing refs such as `TIG-01`.
6. Do not assign refs to unkeyed Epics until an approved task assigns an
   `epic_key`.
7. Reserve archived and historical epic keys forever.
8. Validate the complete identity index before writing migrated state.
9. Mutate task state only through the owning CLI or future shared transaction
   service.
10. Render generated task output only through the owning CLI.
11. Include migration details in the audit event.

Current `EPIC-005` Tasks, including `TASK-021`, may remain unkeyed for now:

```text
id: TASK-021
uid: tsk_c04df4f0310f
legacy_id: TASK-021
aliases: TASK-021
ref: none
epic_key: none
local_seq: none
```

If a later task assigns a key to `EPIC-005`, the migration must allocate
`local_seq` values and refs deterministically under lock, without changing the
existing global `TASK-XXX` IDs.

## Design Decisions

1. Task `id` remains globally unique `TASK-XXX` across all Epics.
2. Epic-scoped `ref` values are human-readable references, not scoped machine
   IDs.
3. `uid` is the immutable machine identity for durable references.
4. Existing `TASK-XXX` references remain stored and resolvable indefinitely.
5. Epic keys are globally reserved and archived keys are never reused.
6. `local_seq` is unique only inside one epic key.
7. ID allocation must run under the relevant lock and transaction layer.
8. Scan-based allocation is acceptable only when performed under lock against
   the latest state snapshot.
9. Dry-run allocation does not reserve identities.
10. Ordinary allocation is audited through the enclosing mutation event, not a
    separate allocation event.
11. Future web write actions must route through the same ID service and locks as
    CLI commands.

## Risks And Open Questions

- The exact lock primitive remains an implementation decision for a later task.
- If a future counter state file is introduced, it must be covered by protected
  file rules, validation, rendering policy if applicable, and migration tests.
- `EPIC-005` has no key today, so control-plane tasks currently rely on global
  `TASK-XXX` references only.
- Event ID unification across existing per-domain event logs may require a
  compatibility migration or a forward-only rule for new events.
- Existing generated views may continue to display mixed formats while some
  Epics are keyed and others are unkeyed.

## Review Checklist

Review should verify that this document:

- resolves cross-epic task ID collision risk by keeping `TASK-XXX` globally
  unique and requiring locked allocation;
- defines epic-scoped refs as readable aliases, not replacement machine IDs;
- preserves legacy `TASK-XXX` compatibility;
- defines duplicate validation for IDs, UIDs, refs, aliases, legacy IDs, local
  sequences, epic keys, and event IDs;
- defines how future `ai_project_ctl/core/ids.py` should work;
- accounts for parallel task and epic creation;
- clearly states that no ID migration or command behavior change is performed
  by this design task;
- confirms protected project-control files are not manually edited.

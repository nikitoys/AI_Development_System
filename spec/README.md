# Machine-Checkable Specification Layer

Status: Draft
Version: v0.1.0

## Purpose

This directory contains the first minimal machine-checkable specification layer for AI_Development_System.

The spec layer represents stable system entities as JSON so tools can inspect, validate and compare them without parsing prose.

## Current Scope

- `roles.json` — AI role registry snapshot.
- `interaction-modes.json` — explicit interaction mode markers and routing intent.
- `verification-modes.json` — supported verification modes and execution boundaries.
- `lifecycle-states.json` — common managed lifecycle states.
- `schemas/system-spec.schema.json` — shared minimal JSON Schema for spec files.

## Source-of-Truth Relationship

Markdown remains the operational source of truth for Human Owner-facing policy, process and explanatory rules.

The `spec/` files are a machine-checkable inventory and contract layer derived from stable Markdown documents.

Spec files must not silently override Markdown rules. If a spec disagrees with its source Markdown document, treat that as drift and resolve it through controlled system evolution.

## Source Documents

| Spec file | Markdown source |
| --- | --- |
| `roles.json` | `ai-system/roles.md` |
| `interaction-modes.json` | `ai-system/interaction-modes.md`, root `AGENTS.md` |
| `verification-modes.json` | `ai-system/verification-modes.md` |
| `lifecycle-states.json` | `ai-system/lifecycle-governance.md` |

## Generated or Derived Documentation Policy

No Markdown is generated from these specs in EVOL-006.

Future generation or Markdown synchronization requires a separate bounded evolution task and Human Owner approval because it can change source-of-truth behavior.

## Schema and Validation Guidance

Each spec file should conform to `schemas/system-spec.schema.json`.

Minimum validation checks:

- JSON parses successfully.
- `spec_id`, `spec_version`, `status`, `markdown_sources` and `items` exist.
- `status` is one of `Draft`, `Active`, `Deprecated` or `Archived`.
- every item has a unique `id`;
- every item has a `name`.

Recommended manual validation commands:

```bash
python3 -m json.tool spec/roles.json >/dev/null
python3 -m json.tool spec/interaction-modes.json >/dev/null
python3 -m json.tool spec/verification-modes.json >/dev/null
python3 -m json.tool spec/lifecycle-states.json >/dev/null
```

Schema lint may be added in a later bounded task. EVOL-006 does not add CI, generated Markdown or bootstrap tooling.

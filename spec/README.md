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
- `sops.json` — SOP inventory for the initial SOP Model entries.
- `agent-work-package.schema.json` — JSON Schema contract for Agent Work Packages.
- `agent-result.schema.json` — JSON Schema contract for Agent Results.
- `role-agent-assignment.schema.json` — JSON Schema contract for manual L3 Role-to-Agent Assignments.
- `parallel-policy.json` — policy inventory for core parallel execution constraints.
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
| `sops.json` | `ai-system/sop-model.md` |
| `agent-work-package.schema.json` | `ai-system/agent-work-package.md` |
| `agent-result.schema.json` | `ai-system/agent-result-intake.md` |
| `role-agent-assignment.schema.json` | `ai-system/role-agent-assignment.md` |
| `parallel-policy.json` | `ai-system/parallel-execution-policy.md` |

## Generated or Derived Documentation Policy

No Markdown is generated from these specs in EVOL-006 or EVOL-014.

Future generation or Markdown synchronization requires a separate bounded evolution task and Human Owner approval because it can change source-of-truth behavior.

EVOL-014 does not implement runtime behavior, automatic execution, automatic merge, automatic acceptance, schema validation CI, scripts or project templates.

## Schema and Validation Guidance

Inventory spec files should conform to `schemas/system-spec.schema.json`.

JSON Schema contract files such as `agent-work-package.schema.json` and `agent-result.schema.json` should conform to JSON Schema draft 2020-12 and should parse as JSON.

Minimum validation checks:

- JSON parses successfully.
- `spec_id`, `spec_version`, `status`, `markdown_sources` and `items` exist.
- `status` is one of `Draft`, `Active`, `Deprecated` or `Archived`.
- every item has a unique `id`;
- every item has a `name`.

Recommended manual validation commands:

```bash
python3 scripts/validate-system.py
python3 -m json.tool spec/roles.json >/dev/null
python3 -m json.tool spec/interaction-modes.json >/dev/null
python3 -m json.tool spec/verification-modes.json >/dev/null
python3 -m json.tool spec/lifecycle-states.json >/dev/null
python3 -m json.tool spec/sops.json >/dev/null
python3 -m json.tool spec/agent-work-package.schema.json >/dev/null
python3 -m json.tool spec/agent-result.schema.json >/dev/null
python3 -m json.tool spec/role-agent-assignment.schema.json >/dev/null
python3 -m json.tool spec/parallel-policy.json >/dev/null
```

`scripts/validate-system.py` is the preferred local entrypoint for EVOL-025 and includes JSON parse validation for all `spec/**/*.json` files, documentation integrity checks, template checks, dependency-aware planning fixture validation and golden project dry-run validation.

Schema lint may be added in a later bounded task. EVOL-006 and EVOL-014 do not add generated Markdown, runtime behavior or bootstrap tooling.

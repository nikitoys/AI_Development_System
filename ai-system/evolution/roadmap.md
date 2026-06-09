# AI Development System Roadmap

Status: Draft  
Version: v0.1.0

## Purpose

This document defines the development plan for AI_Development_System itself.

The roadmap is the primary planning source for controlled system evolution. New evolution work should either map to an existing roadmap item or explicitly propose a roadmap change through the evolution loop.

## Strategic Goal

Turn AI_Development_System from a documentation-first governance framework into a validated, versioned and partially machine-checkable control plane for AI-assisted software development.

## Current Phase

```text
Phase: Productization and self-governance hardening
Focus: make system evolution explicit, bounded, reviewable and owner-approved
```

## Roadmap Principles

- Prefer validation and consistency over adding more lifecycle documents.
- Convert repeated friction into backlog items, then into AICP only when justified.
- Keep Human Owner approval as the final authority for system evolution.
- Keep Markdown readable, but gradually introduce machine-checkable specifications where they reduce drift.
- Treat real project pilots as the main evidence source for maturity.

## Priority Roadmap

### P0 — Self-Evolution Governance

Goal: make the system capable of evolving itself according to an explicit plan and lifecycle.

Items:

1. Add `ai-system/evolution/` module.
2. Define the system evolution loop.
3. Define evolution policy and anti-runaway boundaries.
4. Add a system health-check checklist.
5. Add evolution backlog and proposal/task templates.
6. Reference the analytical repository report as a baseline input.

Exit criteria:

- evolution module is indexed in `ai-system/README.md`;
- operating model references system evolution governance;
- changelog records the new module;
- future self-evolution work can be expressed as bounded tasks.

### P1 — Consistency and Documentation Integrity

Goal: reduce documentation drift and make source-of-truth integrity visible.

Items:

1. Synchronize visible system versions across root README, `ai-system/README.md` and `system-changelog.md`.
2. Define one authoritative version source.
3. Add document status/version conventions.
4. Add link and index completeness checks.
5. Add placeholder detection for production-ready templates.

Exit criteria:

- no known version drift in primary entrypoints;
- documentation integrity checks can be run manually or in CI;
- new documents have consistent status/version fields.

### P2 — Security, Privacy and Data Handling

Goal: define a minimum safety baseline for using external LLMs, Codex-like executors and repository automation.

Items:

1. Add `SECURITY.md` or equivalent system security policy.
2. Add privacy and data-handling policy.
3. Define secret-handling rules for AI-assisted workflows.
4. Define sandbox and execution boundaries for Codex/OpenHands-like executors.
5. Define sensitive-code and external-LLM disclosure rules.

Exit criteria:

- system has explicit guidance for secrets, private code and external tools;
- review process can reference the policy during security review;
- project templates can inherit or link to the policy.

### P3 — Golden Example and Pilot Validation

Goal: validate the system against real project work instead of only internal documentation completeness.

Items:

1. Create one fully filled golden example project.
2. Run pilot validation on 2–3 real repositories.
3. Capture failures in `improvement-log.md`.
4. Convert repeated failures into improvements, AICP, knowledge or experiments.
5. Update owner-facing quickstart based on pilot friction.

Exit criteria:

- at least one complete example exists;
- pilot outcomes are documented;
- repeated issues produce concrete system improvements.

### P4 — Machine-Checkable Specification Layer

Goal: reduce duplication and open the path to tool integration.

Items:

1. Introduce `spec/` for roles, modes, lifecycle states and verification rules.
2. Define schemas for common status/version fields.
3. Generate or validate Markdown from machine-readable definitions where practical.
4. Add schema lint to CI.
5. Use specs as a control contract for Codex/OpenHands/Copilot-like executors.

Exit criteria:

- at least one core system area is represented in machine-checkable form;
- docs and specs have an explicit source-of-truth relationship;
- schema validation can run without manual interpretation.

### P5 — Bootstrap and Update Tooling

Goal: make integration into external repositories repeatable.

Items:

1. Add bootstrap/update CLI or script.
2. Support foldered integration by default.
3. Detect unresolved placeholders.
4. Track integrated version and update method.
5. Add golden tests for bootstrap/update scenarios.

Exit criteria:

- new repositories can install the control layer with minimal manual copying;
- existing integrated repositories can update predictably;
- update behavior is documented and testable.

### P6 — Research and Benchmarking

Goal: turn the system into a practical and researchable governance methodology.

Items:

1. Define benchmark tasks for document-governed AI development.
2. Compare document-governed and tool-first modes.
3. Measure verification mode impact on speed, cost and defect rate.
4. Measure effect of explicit allowed-files contracts.
5. Document case studies from pilots.

Exit criteria:

- methodology can be evaluated, not only described;
- results can inform roadmap priorities;
- research artifacts are separated from operational rules.

## Roadmap Change Rules

Roadmap changes require:

- reason for change;
- affected priority or phase;
- expected benefit;
- risk of not doing it;
- owner approval when priorities change;
- changelog update if roadmap changes affect system behavior.

## Relationship to Evolution Backlog

The roadmap defines direction. The evolution backlog defines actionable items.

```text
Roadmap item → Backlog item → AICP or evolution task → Execution → Review → Approval → Changelog
```

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
- Dogfood Project Control Gateway through root `/AI_PROJECT` while keeping `/ai-system/templates/**/AI_PROJECT` templates and the golden project example distinct.

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

### P6 — SOP and Optional Multi-Agent Control Plane

Goal: increase implementation speed and quality through SOP-guided planning, optional task decomposition into Agent Work Packages, dry-run plan validation and controlled manual orchestration when safe.

Current position:

AI_Development_System is currently a SOP-driven AI development control plane with dry-run planning support.

AI_Development_System now uses root `/AI_PROJECT` as a self-hosted Project Control Layer for its own controlled evolution.

It is not a real runtime. It does not provide agent execution orchestration, automatic Codex execution, automatic branch/worktree lifecycle, automatic merge or automatic acceptance.

Items:

1. Record the SOP and multi-agent implementation plan.
2. Add SOP Model and Agent Work Package standards.
3. Add multi-agent planning and parallel execution policy.
4. Add agent result intake and integration review.
5. Add machine-checkable SOP and Agent Work Package specs.
6. Add AI_PROJECT agent planning templates.
7. Add dry-run agent planner MVP.
8. Extend the golden project with a multi-agent planning example.
9. Run pilot validation.
10. Record runtime decision as deferred until readiness criteria are met.
11. Improve dependency-aware dry-run planning.
12. Add planning fixtures and validation tests.
13. Define runtime maturity levels.
14. Introduce manual multi-agent orchestration mode without automatic execution.
15. Harden agent result schemas.
16. Add CI checks for specs, templates and golden project validation.
17. Expand pilot validation evidence.
18. Add manual Role-to-Agent Assignment for L3 orchestration.
19. Add a practical L3 role-assigned parallel runbook.
20. Add Two-Level Delegated Agent Execution for precise manual Worker Agent handoffs.
21. Prepare future runtime adapter contracts without enabling runtime.
22. Consider assisted execution only after the deferred runtime criteria are satisfied.

Exit criteria:

- SOP-guided planning is documented;
- Agent Work Packages can be planned without automatic execution;
- safe parallel groups can be identified only after approval and file-lock checks;
- agent results can be intaken, reviewed, QA-checked and accepted or rejected by Human Owner;
- ready Agent Work Packages can be assigned manually to logical agents or external sessions without automatic dispatch;
- runtime integration is explicitly deferred until readiness criteria are met;
- manual orchestration is repeatable before assisted or controlled runtime work is reconsidered.

Immediate priorities:

1. `EVOL-019` — completed; runtime decision recorded as `DEFERRED`.
2. `EVOL-020` — completed; dependency graph parsing improved while keeping `scripts/agent-plan-mvp.py` dry-run/reporting only.
3. `EVOL-021` — completed; planning fixtures and validation runner added for dependency-aware dry-run planning.
4. `EVOL-022` — completed; runtime maturity levels documented.
5. `EVOL-023` — completed; manual multi-agent orchestration mode documented.
6. `EVOL-024` — completed; Agent Result Schema hardened.
7. `EVOL-025` — completed; CI and local validation added for specs, templates, planning fixtures and golden project.
8. `EVOL-026` — completed; pilot validation evidence expanded across documentation-only, small tooling/code and multi-agent parallel planning cases.
9. L3 refinement — completed; manual Role-to-Agent Assignment model added without automatic dispatch.
10. L3 refinement — completed; practical role-assigned parallel runbook added.
11. `EVOL-031` — completed; Two-Level Delegated Agent Execution added for manual Worker Agent prompt handoffs without automatic dispatch.
12. `EVOL-027` — future/deferred: prepare runtime adapter contracts without enabling runtime.

Runtime maturity target:

Current level: `L3 — Manual multi-agent orchestration`.

Next possible target: `L4 — Assisted execution`, future/not approved.

### P7 — Research and Benchmarking

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

# AI System Evolution Module

Status: Draft  
Version: v0.1.0

## Purpose

This directory defines how the AI Development System evolves itself in a controlled, reviewable and owner-approved way.

The evolution module exists to prevent uncontrolled self-modification. The system may observe gaps, propose improvements, prepare bounded changes and verify them, but Human Owner approval remains required before changes become authoritative.

## Scope

This module governs evolution of the AI Development System itself, including:

- roadmap management;
- system health checks;
- evolution backlog triage;
- self-improvement loops;
- conversion of observations into AICP proposals;
- bounded evolution tasks for Codex Executor;
- review, approval, release and learning after system changes.

It does not govern product feature work in a target application. Product work remains governed by project-level control files, task lifecycle, Codex lifecycle, review lifecycle and QA lifecycle.

## Documents

- `roadmap.md` — strategic and tactical development plan for AI_Development_System.
- `evolution-loop.md` — controlled observe → diagnose → propose → plan → execute → verify → review → approve → release → learn loop.
- `evolution-policy.md` — boundaries, permissions and anti-runaway rules for self-evolution.
- `owner-evolution-plan.md` — Human Owner-authored intake place for broad system evolution plans.
- `owner-plan-intake.md` — workflow for recording owner plans, mapping them to roadmap/backlog items and preparing one bounded next task.
- `system-health-check.md` — repeatable checklist for assessing documentation, lifecycle, version, security, integration and validation health.
- `evolution-backlog.md` — managed backlog of system evolution items.
- `analysis-report-baseline.md` — baseline findings from the analytical repository report used as an input to the roadmap.
- `templates/system-change-proposal.md` — template for AI System Change Proposals.
- `templates/evolution-task.md` — template for bounded evolution tasks.
- `templates/owner-evolution-plan.md` — reusable template for owner-authored evolution plans.
- `../../spec/README.md` — machine-checkable spec layer introduced by EVOL-006.

## Operating Principle

```text
The system may recommend and prepare its own evolution.
The Human Owner approves whether that evolution is accepted.
```

## Relationship to Existing Lifecycles

System evolution uses existing lifecycle documents instead of bypassing them:

- observations and recurring issues enter `improvement-log.md` and `improvement-lifecycle.md`;
- approved system changes follow `change-process.md` and `change-lifecycle.md`;
- owner-authored evolution plans enter through `owner-evolution-plan.md` and are processed by `owner-plan-intake.md`;
- changes to source-of-truth documents follow `document-lifecycle.md`;
- Codex execution follows `codex-lifecycle.md`;
- review and QA follow `review-lifecycle.md` and `qa-lifecycle.md`;
- significant changes are recorded in `system-changelog.md`.

## Minimal Rule

No self-evolution change is valid unless it has:

- a source observation, roadmap item, backlog item or Human Owner request;
- owner plan mapping when the source is a broad Human Owner plan;
- explicit scope and out-of-scope;
- allowed files;
- acceptance criteria;
- verification mode;
- review step;
- Human Owner approval requirement;
- changelog or history update rule.

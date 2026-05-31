# Decision Process

Status: Draft

## Purpose

This document defines how decisions are made in the AI Development System.

## Principle

AI can recommend. Human Owner decides.

## Decision Statuses

- `APPROVED` — accepted and can move forward.
- `REWORK` — needs changes before acceptance.
- `REJECTED` — not accepted.
- `DEFERRED` — postponed.
- `EXPERIMENT` — temporarily accepted for testing.

## Who Can Propose

Any AI role may propose a decision if it is inside its responsibility area.

Examples:

- Architect AI may propose a technical option.
- QA AI may propose blocking release because of failed criteria.
- AI System Maintainer may propose a system change.

## Who Approves

Only the Human Owner gives final approval.

## Decision Record Format

```md
## Decision ID
DEC-000

## Context
Why is this decision needed?

## Options
What options were considered?

## Decision
APPROVED / REWORK / REJECTED / DEFERRED / EXPERIMENT

## Reason
Why was this decision made?

## Impact
What changes because of this decision?

## Documents to Update
Which files must be updated?
```

## Rule

If a decision changes product behavior, update `/docs`.

If a decision changes development process, update `/ai-system` through the change process.

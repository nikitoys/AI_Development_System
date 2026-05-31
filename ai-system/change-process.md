# Change Process

Status: Draft

## Purpose

This document defines how the AI Development System evolves.

The system must not change randomly. It changes through a controlled process.

## Core Flow

```text
Process problem
→ Improvement log entry
→ Root cause analysis
→ AI System Change Proposal
→ Human decision
→ Codex applies approved change
→ System changelog update
→ New system version
```

## When to Change the System

A system change may be needed when:

- the same problem repeats;
- Codex often goes outside task scope;
- roles overlap or conflict;
- documentation becomes outdated;
- review misses important issues;
- workflow is too heavy or too loose;
- prompts are ambiguous;
- quality decreases because of process gaps.

## When Not to Change the System

Do not change the system when:

- the issue happened once;
- the task input was unclear;
- a simple task clarification is enough;
- the change adds more complexity than value.

## AICP Template

```md
# AICP-000: Title

## Status
Proposed / Accepted / Rejected / Experimental / Deferred / Applied / Rolled Back

## Problem
What does not work?

## Evidence
Where did it happen?

## Root Cause
Why did it happen?

## Proposed Change
What should change?

## Affected Files
Which files in /ai-system will change?

## Expected Benefit
What improves?

## Risks
What may become worse?

## Decision
Human decision.

## Version Impact
Patch / Minor / Major
```

## Versioning

Use `MAJOR.MINOR.PATCH`.

- Patch: small wording, prompt or format correction.
- Minor: new role, rule, document or workflow step.
- Major: significant workflow or operating model change.

## Rule

Do not mix AI Development System changes with application implementation tasks unless explicitly approved by the Human Owner.

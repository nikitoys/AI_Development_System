# Task Format

Status: Draft

## Purpose

This document defines the standard task format used by the AI Development System.

## Template

```md
# TASK-000: Task Title

## Status
Planned / In Progress / Review / Done / Rejected

## Type
Feature / Bug / Refactor / Docs / Infra / Test / System

## Initiative
Optional initiative ID or title.

## Epic
Optional epic ID or title.

## Owner Role
Backend Developer AI / Frontend Developer AI / QA Engineer AI / etc.

## Context
Short explanation of why this task exists.

## Input Documents
- /docs/prd.md
- /docs/architecture.md
- /docs/api.md

## Description
What needs to be done.

## Scope
What is included in this task.

## Out of Scope
What must not be done in this task.

## Expected Files
Files that may be created or changed.

## Verification Mode
NONE / SMOKE / FAST / STANDARD / FULL / RELEASE / MANUAL

## Verification Budget
Maximum total verification time, such as `120 sec` or `5 min`.

## Allowed Slow Checks
true / false

## Runtime Tracking
enabled / disabled

## Acceptance Criteria
- Criterion 1
- Criterion 2
- Criterion 3

## Test Cases
- Test case 1
- Test case 2

## Risks
Known risks or unclear areas.

## Result Format
- Changed files
- Summary
- Verification Summary:
  - Mode
  - Budget
  - Used time
  - Overall result
- Checks:
  - check_id: result, duration_sec, blocking/advisory
- Skipped:
  - check_id: reason_for_skip
- Runtime Warnings:
  - checks that exceeded expected time
  - checks that should be reclassified
  - slow checks not run
- Errors
- Questions
- Diff
```

## Definition of Ready

A task is ready when it has:

- clear description;
- input documents;
- scope;
- out of scope;
- acceptance criteria;
- verification mode;
- verification budget;
- allowed slow-check decision;
- runtime tracking decision;
- owner role;
- no blocking ambiguity.

Initiative and Epic are optional planning fields. Missing Initiative or Epic values do not block Definition of Ready when the task is otherwise bounded, approved and executable.

## Definition of Done

A task is done when:

- acceptance criteria are satisfied;
- review passed;
- QA passed or test cases are documented;
- verification summary reports mode, budget, used time, checks, skipped checks and runtime warnings;
- documentation is updated if needed;
- Human Owner approved the result.

Do not say "all tests passed" unless all relevant tests for the selected mode actually ran.

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
- Tests
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
- owner role;
- no blocking ambiguity.

## Definition of Done

A task is done when:

- acceptance criteria are satisfied;
- review passed;
- QA passed or test cases are documented;
- documentation is updated if needed;
- Human Owner approved the result.

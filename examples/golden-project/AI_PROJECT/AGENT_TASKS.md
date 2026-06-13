# Agent Tasks — Task Tracker

Status: Draft

## Purpose

This file is the Agent Work Package registry for the golden Task Tracker multi-agent planning example.

Agent Work Packages are planning artifacts only.

They do not authorize execution, parallel execution, automatic execution, automatic merge or automatic acceptance.

Human Owner remains the final decision maker.

## Planning Path

```text
Goal: G-001 Make Task Tracker planning execution-ready
Initiative: INIT-001 Task list usability planning
Epic: EPIC-001 Due-date filtering
Parent Task: T-003 Plan due-date filtering for Task Tracker
```

The Agent Work Packages below remain child planning units under `T-003`.

## Agent Work Package Registry

| ID | Status | SOP | Role | Parent Task | Verification Mode | Notes |
|---|---|---|---|---|---|---|
| AWP-REQ-001 | ready | SOP-FEATURE-001 | Business Analyst AI | T-003 | FAST_VALIDATION | Define requirements and acceptance criteria for due-date filtering. |
| AWP-BE-001 | ready | SOP-FEATURE-001 | Backend Developer AI | T-003 | FAST_VALIDATION | Draft backend/API implementation boundaries only; no execution approved. |
| AWP-FE-001 | ready | SOP-FEATURE-001 | Frontend Developer AI | T-003 | FAST_VALIDATION | Draft frontend/UX implementation boundaries only; no execution approved. |
| AWP-QA-001 | ready | SOP-FEATURE-001 | QA Engineer AI | T-003 | FAST_VALIDATION | Draft QA, regression and integration review checks. |

## Package Details

## AWP-REQ-001

```text
action: Define due-date filter requirements and acceptance criteria.
context: Human Owner is considering a Task Tracker enhancement.
input_artifacts: AI_PROJECT/OWNER_PLAN.md, AI_PROJECT/PROJECT_GOAL.md
output_artifacts: requirements notes, acceptance criteria, QA focus
scope: due-date filter requirements only
out_of_scope: product implementation, UI code, API code
forbidden_actions: modify product code, approve execution
dependencies: Human Owner scope confirmation
acceptance_criteria: requirements are clear, acceptance criteria are testable
questions_or_blockers: Human Owner approval required before execution
```

## AWP-BE-001

```text
action: Draft backend/API implementation prompt boundaries for due-date filtering.
context: Backend work would be future implementation after requirements approval.
input_artifacts: AWP-REQ-001 result, AI_PROJECT/CODEX_WORKFLOW.md
output_artifacts: bounded prompt draft, allowed files, locked files
scope: backend/API boundary planning only
out_of_scope: code changes, database migration, auth changes
forbidden_actions: execute Codex, modify app files, approve merge
dependencies: AWP-REQ-001
acceptance_criteria: prompt boundaries are scoped and reviewable
questions_or_blockers: API contract needs Human Owner approval before execution
```

## AWP-FE-001

```text
action: Draft frontend/UX implementation prompt boundaries for due-date filtering.
context: Frontend work would be future implementation after requirements approval.
input_artifacts: AWP-REQ-001 result, AI_PROJECT/CODEX_WORKFLOW.md
output_artifacts: bounded prompt draft, allowed files, locked files
scope: frontend/UX boundary planning only
out_of_scope: code changes, backend behavior, broad redesign
forbidden_actions: execute Codex, modify app files, approve merge
dependencies: AWP-REQ-001
acceptance_criteria: UI prompt boundaries are scoped and reviewable
questions_or_blockers: UX behavior needs Human Owner approval before execution
```

## AWP-QA-001

```text
action: Draft QA and integration review checks for due-date filtering.
context: QA planning prepares future review without executing implementation.
input_artifacts: AWP-REQ-001, AWP-BE-001, AWP-FE-001
output_artifacts: QA checklist, regression focus, integration review focus
scope: QA planning only
out_of_scope: executing product tests, accepting results, modifying code
forbidden_actions: accept final result, skip Human Owner approval
dependencies: AWP-REQ-001, AWP-BE-001, AWP-FE-001
acceptance_criteria: QA handoff is clear and maps to acceptance criteria
questions_or_blockers: runtime test environment is not part of this example
```

## Status Values

```text
proposed
draft
ready
approved
blocked
in_progress
result_submitted
in_review
rework_required
accepted
rejected
deferred
archived
```

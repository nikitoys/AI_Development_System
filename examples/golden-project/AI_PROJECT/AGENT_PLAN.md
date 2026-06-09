# Agent Plan — Task Tracker

Status: Draft

## Purpose

This file records a filled multi-agent planning example for the golden Task Tracker project.

It is a planning artifact only.

It does not authorize execution, parallel execution, automatic execution, automatic merge or automatic acceptance.

Human Owner remains the final decision maker.

## Example Scenario

Task Tracker feature enhancement: plan a due-date filter for the task list.

This example does not create product runtime code. It only demonstrates how AI_PROJECT agent planning records can represent a future feature before execution approval.

## Selected SOP

```text
SOP ID: SOP-FEATURE-001
SOP Name: Feature Delivery SOP
Source: AI_Development_System/ai-system/sop-model.md
```

## Parent Task

```text
Parent Task ID: T-003
Parent Task Status: proposed
Parent Task Title: Plan due-date filtering for Task Tracker
Verification Mode: FAST_VALIDATION
Execution Approved: no
Parallel Execution Approved: no
```

## Decomposition Summary

| Agent Work Package | Role | Purpose | Status |
|---|---|---|---|
| AWP-REQ-001 | Business Analyst AI | Define due-date filter requirements and acceptance criteria. | ready |
| AWP-BE-001 | Backend Developer AI | Draft backend/API implementation prompt boundaries. | ready |
| AWP-FE-001 | Frontend Developer AI | Draft frontend/UX implementation prompt boundaries. | ready |
| AWP-QA-001 | QA Engineer AI | Draft QA and integration review checks. | ready |

## Dependencies

| Package | Depends On | Reason |
|---|---|---|
| AWP-REQ-001 | Human Owner scope confirmation | Requirements must match owner intent. |
| AWP-BE-001 | AWP-REQ-001 | Backend/API behavior needs accepted requirements. |
| AWP-FE-001 | AWP-REQ-001 | UI behavior needs accepted requirements. |
| AWP-QA-001 | AWP-REQ-001, AWP-BE-001, AWP-FE-001 | QA checks need planned behavior and implementation boundaries. |

## Candidate Sequential Order

| Order | Agent Work Package | Reason | Status |
|---|---|---|---|
| 1 | AWP-REQ-001 | Requirements are the dependency root. | recommended |
| 2 | AWP-BE-001 | Backend/API planning after requirements. | recommended |
| 3 | AWP-FE-001 | Frontend/UX planning after requirements. | recommended |
| 4 | AWP-QA-001 | QA planning after implementation boundaries are known. | recommended |

## Candidate Parallel Groups

Candidate parallel groups are informational only.

| Group | Packages | Dependency Check | Locked File Check | Approval Status |
|---|---|---|---|---|
| CPG-001 | AWP-BE-001, AWP-FE-001 | Candidate only after AWP-REQ-001 is accepted. | No overlap in planned locked files. | not approved |

## Human Owner Approval Status

```text
Plan approved: no
Sequential execution approved: no
Parallel execution approved: no
Next bounded task approved: no
Final acceptance: not reached
```

## Dry-Run Helper Usage

```bash
python3 scripts/agent-plan-mvp.py validate --project-root examples/golden-project
python3 scripts/agent-plan-mvp.py check-locks --project-root examples/golden-project
python3 scripts/agent-plan-mvp.py list-parallel-groups --project-root examples/golden-project
python3 scripts/agent-plan-mvp.py generate-prompts --project-root examples/golden-project
```

The helper reports planning state only. It does not execute Codex or approve work.

## Open Questions / Blockers

- Human Owner must confirm whether due-date filtering is an approved product enhancement.
- Human Owner must approve any future execution task before product files are changed.
- Candidate parallel group `CPG-001` is not executable until explicitly approved under the Parallel Execution Policy.


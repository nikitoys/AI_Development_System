# Agent Tasks — Simple Linear Fixture

Status: Draft

## Purpose

Fixture for a simple linear dependency chain.

## Agent Work Package Registry

| ID | Status | SOP | Role | Parent Task | Verification Mode | Notes |
|---|---|---|---|---|---|---|
| AWP-REQ-001 | accepted | SOP-FEATURE-001 | Business Analyst AI | T-021 | FAST_VALIDATION | Requirements are complete. |
| AWP-BE-001 | ready | SOP-FEATURE-001 | Backend Developer AI | T-021 | FAST_VALIDATION | Backend planning waits for requirements. |
| AWP-QA-001 | ready | SOP-FEATURE-001 | QA Engineer AI | T-021 | FAST_VALIDATION | QA planning waits for backend planning. |

## AWP-REQ-001

```text
dependencies: none
```

## AWP-BE-001

```text
dependencies: AWP-REQ-001
```

## AWP-QA-001

```text
dependencies: AWP-BE-001
```

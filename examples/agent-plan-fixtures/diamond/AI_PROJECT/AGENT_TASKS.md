# Agent Tasks — Diamond Dependency Fixture

Status: Draft

## Purpose

Fixture for a diamond dependency shape where one accepted root unlocks two parallel packages and the final package waits for both.

## Agent Work Package Registry

| ID | Status | SOP | Role | Parent Task | Verification Mode | Notes |
|---|---|---|---|---|---|---|
| AWP-REQ-001 | accepted | SOP-FEATURE-001 | Business Analyst AI | T-021 | FAST_VALIDATION | Requirements are complete. |
| AWP-BE-001 | ready | SOP-FEATURE-001 | Backend Developer AI | T-021 | FAST_VALIDATION | Backend planning waits for requirements. |
| AWP-FE-001 | ready | SOP-FEATURE-001 | Frontend Developer AI | T-021 | FAST_VALIDATION | Frontend planning waits for requirements. |
| AWP-QA-001 | ready | SOP-FEATURE-001 | QA Engineer AI | T-021 | FAST_VALIDATION | QA waits for backend and frontend planning. |

## AWP-REQ-001

```text
dependencies: none
```

## AWP-BE-001

```text
dependencies: AWP-REQ-001
```

## AWP-FE-001

```text
dependencies: AWP-REQ-001
```

## AWP-QA-001

```text
dependencies: AWP-BE-001, AWP-FE-001
```

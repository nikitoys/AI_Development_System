# Agent Metrics — Task Tracker

Status: Draft

## Purpose

This file records placeholder metrics for the golden Task Tracker multi-agent planning example.

Metrics are learning inputs only.

Metrics do not authorize execution, parallel execution, automatic execution, automatic merge or automatic acceptance.

## Planning Metrics

| Metric | Value | Notes |
|---|---|---|
| Agent Work Packages proposed | 4 | Requirements, backend/API planning, frontend/UX planning, QA planning. |
| Blockers found before execution | 2 | Human Owner feature approval and execution approval are missing. |
| Dependency conflicts found | 0 | Dependencies are sequenced. |
| Locked-file conflicts found | 0 | No overlapping locked files in candidate group. |

## Execution / Review Metrics

| Metric | Value | Notes |
|---|---|---|
| Packages executed sequentially | 0 | No execution authorized. |
| Parallel groups approved | 0 | CPG-001 is informational only. |
| Results requiring rework | 0 | No results submitted. |
| Integration review findings | 0 | Integration review not started. |

## QA Metrics

| Metric | Value | Notes |
|---|---|---|
| QA checks planned | 1 | QA planning package exists. |
| QA defects found | 0 | No implementation or QA execution occurred. |
| Regression checks required | 1 | Would be required for future due-date filter implementation. |
| Risks accepted by Human Owner | 0 | No risk acceptance recorded. |

## Lessons Learned

- The example shows that backend/API and frontend/UX planning can be candidate parallel work only after requirements are accepted.
- The example keeps QA sequenced after implementation-boundary planning.
- The example does not create product runtime files.


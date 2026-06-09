# Agent Locks — Task Tracker

Status: Draft

## Purpose

This file records file-scope and locked-file planning for the golden Task Tracker multi-agent example.

Locks are planning records only. They do not grant write permission.

This file does not authorize execution, parallel execution, automatic execution, automatic merge or automatic acceptance.

## File-Scope Registry

| Package ID | allowed_files | locked_files | Conflict Status | Notes |
|---|---|---|---|---|
| AWP-REQ-001 | AI_PROJECT/OWNER_PLAN.md, AI_PROJECT/CODEX_TASKS.md | AI_PROJECT/CODEX_TASKS.md | no conflict | Requirements planning only. |
| AWP-BE-001 | task-tracker-app/backend/**, AI_PROJECT/AGENT_RESULTS.md | task-tracker-app/backend/tasks-api.md | no conflict | Hypothetical backend/API files; no runtime code exists in this example. |
| AWP-FE-001 | task-tracker-app/frontend/**, AI_PROJECT/AGENT_RESULTS.md | task-tracker-app/frontend/task-list-ui.md | no conflict | Hypothetical frontend/UX files; no runtime code exists in this example. |
| AWP-QA-001 | AI_PROJECT/docs/verification-policy.md, AI_PROJECT/AGENT_RESULTS.md, AI_PROJECT/AGENT_METRICS.md | AI_PROJECT/AGENT_RESULTS.md | no conflict | QA and integration review planning only. |

## Conflict Checklist

- `AWP-BE-001` and `AWP-FE-001` have no overlapping `locked_files`.
- `AWP-QA-001` depends on `AWP-BE-001` and `AWP-FE-001`, so it should be sequenced after them.
- Candidate parallel group `CPG-001` includes only `AWP-BE-001` and `AWP-FE-001`.
- Candidate parallel group `CPG-001` remains informational only and is not approved.
- Human Owner approval is required before any package becomes executable.

## Parallel Group Notes

```text
Parallel group: CPG-001
Packages: AWP-BE-001, AWP-FE-001
Dependency check passed: candidate only after AWP-REQ-001 is accepted
Locked-file check passed: yes, no overlap in planned locked files
Integration review planned: placeholder only
QA decision recorded: placeholder only
Parallel execution approved: no
Execution authorized: no
```


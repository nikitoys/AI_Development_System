# Agent Plan Fixtures

Status: Draft

## Purpose

These fixtures validate dependency-aware dry-run behavior in `scripts/agent-plan-mvp.py`.

They are planning fixtures only. They do not authorize execution, automatic Codex execution, branch/worktree automation, merge automation or automatic acceptance.

## Fixtures

- `accepted-prerequisite` — `AWP-REQ-001` is accepted, so `AWP-BE-001` and `AWP-FE-001` are the valid ready parallel group.
- `simple-linear` — accepted root package unlocks one next package while the final package remains blocked by an incomplete prerequisite.
- `simple-parallel` — independent ready packages are listed together.
- `diamond` — accepted root unlocks backend/frontend parallel planning while QA waits for both.
- `missing-dependency` — package references an AWP dependency that is not defined.
- `cycle` — two packages depend on each other.
- `blocked-package` — blocked package is excluded from the ready dependency layer.

## Verification Commands

```bash
python3 scripts/validate-agent-plan-fixtures.py
python3 scripts/agent-plan-mvp.py list-parallel-groups --project-root examples/agent-plan-fixtures/accepted-prerequisite
python3 scripts/agent-plan-mvp.py validate --project-root examples/agent-plan-fixtures/missing-dependency
python3 scripts/agent-plan-mvp.py validate --project-root examples/agent-plan-fixtures/cycle
python3 scripts/agent-plan-mvp.py list-parallel-groups --project-root examples/agent-plan-fixtures/blocked-package
```

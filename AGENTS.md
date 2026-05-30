# AGENTS.md

Instructions for future AI/Codex sessions in this repository.

## Start Here

Read these first, in order:

1. `PROJECT_GOAL.md` for mission, constraints, success criteria, and non-goals.
2. `CODEX_WORKFLOW.md` for operator commands and One-Task Loop rules.
3. `CODEX_COMMANDS.md` for the short operator command cheat sheet.
4. `CODEX_PLAN.md` for the current planning snapshot.
5. `CODEX_CURRENT.md` for the active task state.
6. `CODEX_SESSION_LOG.md` for recent cycles.
7. `CODEX_TASKS.md` for the compact project board.
8. `PROMPTS.md` for reusable prompts.

## Work Rules

- Keep changes small and scoped.
- Do not expand scope without explicit operator approval.
- Do not take the next task automatically.
- Update state files when task status changes.
- Run relevant checks for the files changed.
- If checks fail for unclear reasons, stop and report the exact command and
  failure.
- Do not commit secrets, credentials, local config, generated artifacts, or
  private data.
- Do not run destructive git commands unless the operator explicitly requests
  them.

## Documentation Rules

- Keep project memory compact and current.
- Mark unverified facts as `TBD` or `requires verification`.
- Prefer durable state in `CODEX_CURRENT.md`, `CODEX_TASKS.md`, and
  `CODEX_SESSION_LOG.md` over long chat-only context.

## Checks

Define project-specific checks here.

- Normal changes: TBD
- Build/package check: TBD
- Smoke check: TBD
- Documentation-only changes: markdown/link checks or explicit skip rationale.

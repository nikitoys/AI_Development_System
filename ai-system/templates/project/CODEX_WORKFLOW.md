# Codex Workflow — {{PROJECT_NAME}}

## Purpose

This workflow controls one scoped Codex task at a time.

## State Files

- `AGENTS.md`
- `PROJECT_GOAL.md`
- `docs/verification-policy.md`
- `CODEX_COMMANDS.md`
- `CODEX_WORKFLOW.md`
- `CODEX_PLAN.md`
- `CODEX_CURRENT.md`
- `CODEX_TASKS.md`
- `CODEX_SESSION_LOG.md`
- `PROMPTS.md`

## One-Task Loop

```text
1. Read project control files.
2. Confirm approved task and scope.
3. Implement only allowed changes.
4. Run checks allowed by verification mode.
5. Report changed files, checks, errors and questions.
6. Commit only when instructed and allowed.
7. Stop.
```

## Owner Plan Intake

`OWNER_PLAN.md` is a Human Owner-authored input file. It may describe broad desired work, but Codex must not implement it directly.

Plan intake converts owner plan items into `CODEX_PLAN.md` and `CODEX_TASKS.md` proposals, then stops for Human Owner approval.

## Checks Policy

Default Verification Mode: `{{DEFAULT_VERIFICATION_MODE}}`

Browser automation, Playwright/MCP browser sessions, screenshots, manual visual inspections and browser console checks are on-demand only.

Do not run them unless the Human Owner explicitly requests them or acceptance criteria require them.

Do not mark a task `PARTIAL` only because browser or visual checks were skipped unless those checks were explicitly required.

## Security and Privacy Policy

When AI_Development_System policies are available, this project inherits the security and privacy baseline for secrets, private data, external LLM sharing, sandbox boundaries and generated artifacts.

Project-local rules may be stricter, but must not weaken the inherited baseline without explicit Human Owner approval.

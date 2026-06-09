# Codex Workflow — Task Tracker

## Purpose

This workflow controls one scoped task at a time in Foldered Control Mode.

## State Files

- `AI_PROJECT/AGENTS.md`
- `AI_PROJECT/PROJECT_GOAL.md`
- `AI_PROJECT/OWNER_PLAN.md`
- `AI_PROJECT/docs/verification-policy.md`
- `AI_PROJECT/CODEX_COMMANDS.md`
- `AI_PROJECT/CODEX_WORKFLOW.md`
- `AI_PROJECT/CODEX_PLAN.md`
- `AI_PROJECT/CODEX_CURRENT.md`
- `AI_PROJECT/CODEX_TASKS.md`
- `AI_PROJECT/CODEX_SESSION_LOG.md`
- `AI_PROJECT/PROMPTS.md`
- `AI_PROJECT/AI_DEV_SYSTEM_VERSION.md`

## One-Task Loop

```text
1. Read root AGENTS.md and AI_PROJECT control files.
2. Confirm approved task and scope.
3. Implement only allowed changes.
4. Run checks allowed by verification mode.
5. Report changed files, checks, errors and questions.
6. Commit only when instructed and allowed.
7. Stop.
```

## Owner Plan Intake

`AI_PROJECT/OWNER_PLAN.md` is Human Owner planning input.

Plan intake converts owner plan items into `AI_PROJECT/CODEX_PLAN.md` and `AI_PROJECT/CODEX_TASKS.md` proposals, then stops for approval.

## Checks Policy

Default Verification Mode: `FAST_VALIDATION`

Browser automation, Playwright/MCP browser sessions, screenshots, manual visual inspections and browser console checks are on-demand only.

Do not run them unless the Human Owner explicitly requests them or acceptance criteria require them.

Do not mark a task `PARTIAL` only because browser or visual checks were skipped unless those checks were explicitly required.

## Security and Privacy Policy

This project inherits:

- `AI_Development_System/ai-system/security-policy.md`
- `AI_Development_System/ai-system/privacy-data-handling-policy.md`

Project-local rules may be stricter, but must not weaken the inherited baseline without explicit Human Owner approval.

## System Update Boundary

`AI_Development_System/` may be updated only during explicit system update or evolution work.

`AI_PROJECT/` must be merged, not overwritten, when the upstream system changes.

Application code in `task-tracker-app/` is out of scope during system update.

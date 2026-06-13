# AI_PROJECT/AGENTS.md — {{PROJECT_NAME}}

Status: Draft

## Purpose

This file defines local AI/Codex instructions for this project.

## Project Context

Project: `{{PROJECT_NAME}}`
Target App Directory: `{{TARGET_APP_DIRECTORY}}`
Human Owner Language: `{{HUMAN_OWNER_LANGUAGE}}`
Default Verification Mode: `{{DEFAULT_VERIFICATION_MODE}}`
Operation Profile: `AI_PROJECT/PROJECT_OPERATION_PROFILE.md`

## Start Here

Read in order:

1. `AI_PROJECT/PROJECT_OPERATION_PROFILE.md`
2. `AI_PROJECT/PROJECT_GOAL.md`
3. `AI_PROJECT/OWNER_PLAN.md` when doing plan intake
4. `AI_PROJECT/docs/verification-policy.md`
5. `AI_Development_System/ai-system/security-policy.md`
6. `AI_Development_System/ai-system/privacy-data-handling-policy.md`
7. `AI_PROJECT/CODEX_WORKFLOW.md`
8. `AI_PROJECT/CODEX_CURRENT.md`
9. `AI_PROJECT/CODEX_TASKS.md`
10. `AI_PROJECT/CODEX_PLAN.md`
11. `AI_PROJECT/AGENT_ASSIGNMENTS.md` when doing L3 manual orchestration
12. `AI_PROJECT/CODEX_SESSION_LOG.md` when continuing prior work
13. `AI_Development_System/AGENTS.md` when system-level rules are needed

## Core Rules

- Human Owner makes final decisions.
- Codex is an executor, not a product decision maker.
- `OWNER_PLAN.md` is planning input, not executable scope.
- Do not implement without an approved task and acceptance criteria.
- Do not touch files outside approved scope.
- Follow `PROJECT_OPERATION_PROFILE.md` for project-local operating defaults.
- Follow `docs/verification-policy.md` before running checks.
- Follow inherited AI_Development_System security and privacy baselines.
- Browser, Playwright, screenshots, console checks and visual QA are on-demand only.

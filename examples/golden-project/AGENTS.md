# AGENTS.md — Task Tracker

This project uses AI_Development_System through the foldered integration model.

## Start Here

Before repository-affecting work, read:

```text
AI_PROJECT/AGENTS.md
AI_PROJECT/PROJECT_GOAL.md
AI_PROJECT/docs/verification-policy.md
AI_Development_System/ai-system/security-policy.md
AI_Development_System/ai-system/privacy-data-handling-policy.md
AI_Development_System/AGENTS.md
AI_Development_System/ai-system/rules.md
```

## Repository Boundaries

```text
AI_Development_System/   # embedded upstream AI Development System
AI_PROJECT/              # project-local control files and task state
task-tracker-app/        # example application directory placeholder
```

Do not modify `AI_Development_System/` unless the task explicitly targets AI system update, synchronization or evolution.

Do not modify `AI_PROJECT/` unless the task explicitly targets planning, state, prompts, verification policy or project control files.

Do not modify `task-tracker-app/` in this example repository.

## Interaction Modes

Use the embedded AI Development System modes:

```text
[FREE]
[SYSTEM]
[PROMPT]
[CODEX]
[REVIEW]
[EVOLUTION]
[DRY-RUN]
```

## Required Header for Process Work

```text
Active Role:
Active Stage:
Active Document:
Expected Result:
```

## Default Verification

Default Verification Mode: `FAST_VALIDATION`

Browser automation, Playwright/MCP browser sessions, screenshots, browser console checks and manual visual QA are on-demand only.

Security and privacy work inherits `AI_Development_System/ai-system/security-policy.md` and `AI_Development_System/ai-system/privacy-data-handling-policy.md`.

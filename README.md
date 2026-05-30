# AI Project Operator Loop

This repository is a generic template for running projects with AI assistants
through a short operator API, durable project memory, and a One-Task Loop.

It is meant for projects where the human operator chooses direction and the AI
assistant executes one scoped task at a time, records state, runs checks, makes
one commit, and stops.

## Quick Start

1. Copy this template into a new repository.
2. Fill in `PROJECT_GOAL.md` with the mission, constraints, success criteria,
   and non-goals.
3. Review `CODEX_WORKFLOW.md` and adapt checks, commit rules, and safety
   constraints to the project.
4. Fill `CODEX_PLAN.md` with the first 3-5 tasks.
5. Start a fresh AI session with the prompt in `PROMPTS.md`.
6. Use short operator commands instead of long prompts.

## Operator Commands

- `Старт`: read the core project memory and report readiness.
- `Статус`: show current task state, changed files, checks, blockers, and next
  action.
- `Советник`: assess project direction and recommend one next operator step.
- `Аудит`: check consistency across workflow state files.
- `План`: propose 3-5 next tasks sorted by value.
- `План подробнее N`: expand task `N` into scope, checks, and done criteria.
- `Утверждаю задачу N`: record the selected task as approved.
- `Выполняй`: run the approved task through the One-Task Loop and commit.
- `Выполняй без коммита`: run the approved task and checks, then stop before
  commit.
- `Коммить`: commit already-checked approved changes.
- `Стоп`: stop current work and mark it stopped.
- `Продолжай текущую`: resume only the current approved or stopped task.
- `Отмени текущую`: cancel the current task without deleting changes.

## Basic Workflow

```text
Старт -> Статус -> Советник -> План -> План подробнее N -> Утверждаю задачу N -> Выполняй
```

Core principle:

```text
one task -> scoped implementation -> checks -> one commit -> stop
```

The assistant must not automatically move from planning to execution, and must
not automatically take the next task after finishing one.

## State Files

- `AGENTS.md`: instructions for future AI sessions.
- `PROJECT_GOAL.md`: mission, constraints, success criteria, and non-goals.
- `CODEX_COMMANDS.md`: short command cheat sheet.
- `CODEX_WORKFLOW.md`: full operator workflow.
- `CODEX_PLAN.md`: current planning snapshot.
- `CODEX_CURRENT.md`: current task state.
- `CODEX_SESSION_LOG.md`: journal of cycles.
- `CODEX_TASKS.md`: compact project board.
- `PROMPTS.md`: reusable prompts for fresh sessions and modes.

## Adapt For A New Project

- Replace `TBD` placeholders with project-specific information.
- Define the normal check commands in `CODEX_WORKFLOW.md` and `AGENTS.md`.
- Add project-specific safety constraints and non-goals to `PROJECT_GOAL.md`.
- Keep state files short enough to be read at the start of every session.
- Update templates in `templates/` if your project needs extra approval fields.

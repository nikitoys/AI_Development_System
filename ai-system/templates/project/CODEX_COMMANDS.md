# Codex Operator Commands

Short operator commands must be interpreted through `CODEX_WORKFLOW.md`.

## Planning and State

- `Разобрать план` — read `OWNER_PLAN.md`, compare it with current state and propose backlog/task updates without implementation.
- `Старт` — read project memory and report readiness.
- `Статус` — report current task, blockers and next action.
- `Советник` — assess project direction and recommend one next step.
- `Аудит` — check consistency across control files.
- `План` — propose 3-5 next tasks.
- `План подробнее N` — expand task `N`.
- `Утверждаю задачу N` — approve task `N`.

## Execution

- `Выполняй` — execute approved task, run allowed checks, commit once and stop.
- `Выполняй без коммита` — execute approved task and stop before commit.
- `Коммить` — commit approved scoped changes.
- `Стоп` — stop current work.
- `Продолжай текущую` — continue current approved or stopped task.
- `Отмени текущую` — cancel current task.

## Verification Mode Commands

- `Код быстро` — use `CODE_ONLY_FAST`.
- `Проверка быстро` — use `FAST_VALIDATION`.
- `Браузер проверить` — use `BROWSER_SMOKE`.
- `Визуально проверить` — use `VISUAL_QA`.

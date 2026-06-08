# Codex Workflow

## Purpose

This workflow defines a generic operator API for AI-assisted project work. The
operator chooses direction. The assistant executes one scoped task at a time,
updates durable state, runs checks, makes at most one commit, and stops.

## State Files

- `AGENTS.md`: instructions for future AI sessions.
- `PROJECT_GOAL.md`: mission, constraints, success criteria, and non-goals.
- `CODEX_COMMANDS.md`: short operator command cheat sheet.
- `CODEX_WORKFLOW.md`: full operator workflow.
- `OWNER_PLAN.md`: Human Owner-authored roadmap and desired work; planning input only.
- `CODEX_PLAN.md`: current planning snapshot and nearest tasks.
- `CODEX_CURRENT.md`: current approved/stopped/cancelled/idle task state.
- `CODEX_SESSION_LOG.md`: short journal of One-Task Loop cycles.
- `CODEX_TASKS.md`: compact project board.
- `PROMPTS.md`: reusable prompts.
- `docs/verification-policy.md`: local verification mode and check policy.

## Operator Commands

Short operator commands are authoritative. If the operator writes one of the
commands in `CODEX_COMMANDS.md`, interpret it according to this workflow.

If a command is unclear, ask one short clarifying question before starting
implementation. If a command may expand scope, stop and ask for confirmation.
Do not automatically move from `План` to `Выполняй`, and do not automatically
move from one task to the next.

## Planning Mode

### `Разобрать план`

Codex or ChatGPT Orchestrator must:

- read `OWNER_PLAN.md` if present;
- read `PROJECT_GOAL.md`, `CODEX_PLAN.md`, `CODEX_TASKS.md`, `CODEX_CURRENT.md` and `CODEX_SESSION_LOG.md`;
- compare the owner plan with current project state;
- classify items as `Already Done`, `Partially Done`, `Missing`, `Unclear`, `Out of Scope` or `Recommended Next Tasks`;
- propose updates to `CODEX_PLAN.md` and `CODEX_TASKS.md`;
- not modify application code;
- not start implementation;
- stop and wait for Human Owner approval.

`OWNER_PLAN.md` is planning input, not executable scope.

### `План`

Codex must:

- read `PROJECT_GOAL.md`, `CODEX_PLAN.md`, `CODEX_CURRENT.md`,
  `CODEX_TASKS.md`, `CODEX_SESSION_LOG.md`, and `CODEX_WORKFLOW.md`;
- not change files;
- propose 3-5 next tasks;
- sort them by project value;
- for each task, include goal, expected result, why it is not work for work's
  sake, files likely touched, definition of done, main check, negative checks,
  and risk;
- stop and wait for the operator's choice.

### `План подробнее N`

Codex must expand task `N` without changing files:

- exact task statement;
- scope boundaries;
- what not to do;
- files that may be touched;
- criteria for completion;
- checks;
- expected commit message.

### `Утверждаю задачу N`

Codex must:

- write the selected task to `CODEX_CURRENT.md`;
- set `status: approved`;
- record allowed files, definition of done, checks, and stop conditions;
- update `CODEX_TASKS.md` if useful;
- not start implementation until the operator says `Выполняй`.

## Execution Mode

### `Выполняй`

Codex must execute the approved task through the One-Task Loop, update state
files, make exactly one commit, describe the result briefly, and stop.

### `Выполняй без коммита`

Codex must execute the approved task and checks, but stop before committing.
The final message must include what changed, which checks passed, whether the
commit is ready, and a suggested commit message.

### `Коммить`

Codex may commit only if there is an approved task, changes match scope, and
checks have passed or skipped checks are explicitly explained.

### `Стоп`

Codex must stop current work, update `CODEX_CURRENT.md` with
`status: stopped`, describe what was done and what remains, and not commit
unfinished work without a separate command.

### `Продолжай текущую`

Codex must read `CODEX_CURRENT.md`, continue only the current approved or
stopped task, avoid taking a new task, and follow the One-Task Loop.

### `Отмени текущую`

Codex must move `CODEX_CURRENT.md` to `status: cancelled`, explain what was
cancelled, and not delete changes automatically unless explicitly instructed.

## Advisory Mode

### `Старт`

Codex must read the Start Here files from `AGENTS.md`, report current state,
identify whether a task is active, show known checks, recommend one next
operator action, and stop without changing files.

### `Статус`

Codex must briefly show current status, approved task, current phase, files
changed, checks already run, blockers, and next required operator action
without changing files.

### `Советник`

Codex must:

- read `PROJECT_GOAL.md`, `CODEX_PLAN.md`, `CODEX_CURRENT.md`,
  `CODEX_TASKS.md`, `CODEX_SESSION_LOG.md`, and `CODEX_WORKFLOW.md`;
- not change files;
- assess project state;
- say whether the current task appears stalled;
- say whether work is drifting into work for work's sake;
- propose 3 management or research suggestions;
- propose one best next operator step;
- stop.

## Audit Mode

### `Аудит`

Codex must:

- not change files;
- check consistency across `AGENTS.md`, `CODEX_COMMANDS.md`,
  `CODEX_WORKFLOW.md`, `CODEX_PLAN.md`, `CODEX_CURRENT.md`,
  `CODEX_TASKS.md`, `CODEX_SESSION_LOG.md`, `OWNER_PLAN.md`,
  `docs/verification-policy.md`, and `PROMPTS.md`;
- find contradictions, stale status, bloated backlog, missing checks, or
  unfinished cycles;
- give a short report and recommendations;
- stop.

## One-Task Loop

```text
1. Уточнить цель.
2. Быстро прикинуть решение.
3. Реализовать.
4. Проверить основной сценарий.
5. Проверить пару негативных сценариев.
6. Закоммитить.
7. Коротко описать результат.
8. Остановиться.
```

## Stop Conditions

Stop when:

- the approved task is complete and committed;
- a check fails for unclear reasons;
- scope needs to expand;
- required information is missing;
- the operator sends `Стоп` or `Отмени текущую`;
- continuing would require touching files outside allowed scope.

## Scope Control

- Record allowed files before implementation.
- Do not touch files outside scope without confirmation.
- Avoid incidental refactors.
- Do not change public behavior as cleanup.
- Do not commit secrets, local config, or generated artifacts.

## Checks Policy

Verification mode is authoritative for allowed checks.

Default mode for ordinary code-only work and fast bugfixes:

```text
CODE_ONLY_FAST
```

Modes:

- `CODE_ONLY_FAST` — run only fast code/diff checks such as `git diff --check` and `git status --short`; optional `npm run typecheck` only when source files changed and practical.
- `FAST_VALIDATION` — run standard validation such as `npm run typecheck`, `npm run test:run` and `npm run build`; no browser unless explicitly requested.
- `BROWSER_SMOKE` — run limited browser/runtime checks only when explicitly requested.
- `VISUAL_QA` — run screenshots, visual inspection or Playwright visual checks only when explicitly requested or required by acceptance criteria.

Browser automation, Playwright/MCP browser sessions, screenshots, manual visual inspections and browser console checks are on-demand QA only. Do not run them unless the Human Owner explicitly requests them or the current task explicitly lists them in acceptance criteria.

Do not mark a task `PARTIAL` only because browser checks, screenshots, visual inspection or console checks were skipped, unless those checks were explicitly required for that task.

If a check cannot run, report the exact command and reason.

Negative checks should verify the work did not affect excluded paths, behavior, outputs, or contracts.

## Commit Policy

- Make one commit per approved task.
- Commit only after scope and checks are satisfied or skipped checks are
  explicitly justified.
- Use a clear message that names the actual change.
- Do not push unless explicitly instructed.

## Default Rule

If the operator writes a short command from `CODEX_COMMANDS.md`, Codex must
interpret it through this workflow.

If the command is unclear, ask a short clarifying question instead of starting
implementation.

If the command can expand scope, stop and ask for confirmation.

Do not automatically move from `План` to `Выполняй`.

Do not automatically move from one task to the next.

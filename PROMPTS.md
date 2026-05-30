# Reusable Prompts

Copy and adapt these prompts for future sessions.

## Fresh Session Start

```text
Read AGENTS.md first, then obey CODEX_COMMANDS.md and CODEX_WORKFLOW.md. If the user writes a short operator command, interpret it through Operator Commands. Read PROJECT_GOAL.md, CODEX_PLAN.md, CODEX_CURRENT.md, CODEX_TASKS.md, and CODEX_SESSION_LOG.md before changing files.
```

## Planning Mode

```text
План
```

## Execution Mode

```text
Выполняй
```

## Advisor Mode

```text
Советник
```

## Audit Mode

```text
Аудит
```

## Safe Refactor

```text
Make a small, behavior-preserving refactor within the approved scope. Read the relevant files first. Do not change public behavior, output contracts, or unrelated files unless explicitly approved. Run the relevant checks and stop after one commit.
```

## Verify Run

```text
Run the safe checks documented for this project. If dependencies are missing or a command fails, report the exact command, failure, and likely cause. Do not claim success for checks that did not run.
```

## Update Documentation

```text
Update documentation only for the approved change. Keep docs concise, update state files, run documentation-appropriate checks, make one commit, and stop.
```

# Verification Modes

Status: Draft
Version: v0.1.0

## Purpose

This document defines explicit verification modes for Codex execution, review and QA inside projects managed by the AI Development System.

Verification mode is part of scope control. It defines which checks are allowed, which checks are optional and which checks are forbidden unless explicitly requested.

## Core Rule

Browser automation, Playwright/MCP browser sessions, screenshots, manual visual inspections and browser console checks are on-demand QA only.

Do not run them unless the Human Owner explicitly requests them or the current task explicitly lists them in acceptance criteria.

Do not mark a task `PARTIAL` only because browser checks, screenshots, visual inspection or console checks were skipped, unless those checks were explicitly required for that task.

For ordinary code-only implementation and bugfix tasks, use `CODE_ONLY_FAST` by default.

Codex must not silently upgrade verification mode.

## Mode: CODE_ONLY_FAST

Default for small code-only changes, documentation changes and fast bugfixes.

Allowed:

```bash
git diff --check
git status --short
```

Optional only when TypeScript or source files changed and the command is practical:

```bash
npm run typecheck
```

Forbidden unless explicitly requested:

```text
dev server
preview server
browser tabs
Playwright
MCP browser sessions
screenshots
manual visual QA
browser console inspection
full build
full test suite
```

Use this mode when speed and scope discipline matter more than exhaustive validation.

## Mode: FAST_VALIDATION

Use when the prompt explicitly asks for standard validation.

Typical checks:

```bash
npm run typecheck
npm run test:run
npm run build
```

No browser, Playwright, screenshots, console inspection or manual visual QA unless explicitly requested.

If a repository does not define one of these commands, Codex should report the missing command rather than invent a substitute.

## Mode: BROWSER_SMOKE

Use only when the Human Owner explicitly requests a browser/runtime check or when task acceptance criteria require it.

May include:

```bash
npm run dev -- --host 127.0.0.1
```

and limited browser open or console check.

The browser smoke check must be narrow and must not expand into visual QA unless visual acceptance criteria are explicitly present.

## Mode: VISUAL_QA

Use only by explicit Human Owner request or when task acceptance criteria require visual validation.

May include:

- screenshots;
- visual inspection;
- Playwright visual checks;
- browser snapshots;
- UI, sprite or layout visual review.

Visual QA should define exactly what should be inspected and what evidence should be returned.

## Mode Selection Rules

- If no verification mode is specified, use `CODE_ONLY_FAST`.
- If the task says `Проверка быстро` or `FAST_VALIDATION`, use `FAST_VALIDATION`.
- If the task says `Браузер проверить` or `BROWSER_SMOKE`, use `BROWSER_SMOKE`.
- If the task says `Визуально проверить` or `VISUAL_QA`, use `VISUAL_QA`.
- Do not infer browser or visual QA from the word `check` alone.
- Do not run slower checks because they are available.

## Prompt Package Relationship

Codex prompt packages should include:

```text
Verification Mode:
```

The verification mode must align with allowed checks and forbidden actions.

If a task needs stronger checks, the prompt must explicitly say so.

## Review Relationship

Reviewers must evaluate whether Codex obeyed the declared verification mode.

Skipping browser or visual checks is not a review failure when the declared mode does not allow or require those checks.

Running browser, Playwright, screenshots, console inspection or manual visual QA outside the declared mode is a scope violation unless explicitly approved by the Human Owner.

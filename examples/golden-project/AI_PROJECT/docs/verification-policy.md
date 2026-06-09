# Verification Policy — Task Tracker

Status: Draft

## Default Verification Mode

```text
FAST_VALIDATION
```

## Modes

- `CODE_ONLY_FAST` — fast code-only or documentation changes.
- `FAST_VALIDATION` — standard typecheck/test/build without browser.
- `BROWSER_SMOKE` — browser runtime check only by explicit request.
- `VISUAL_QA` — screenshots and visual inspection only by explicit request.

## On-Demand Browser and Visual QA Rule

Browser automation, Playwright/MCP browser sessions, screenshots, manual visual inspections and browser console checks are on-demand only.

Do not run them unless the Human Owner explicitly requests them or the current task explicitly lists them in acceptance criteria.

Do not mark a task `PARTIAL` only because browser checks, screenshots, visual inspection or console checks were skipped, unless those checks were explicitly required.

## System Update Checks

For AI system bootstrap or update, use `CODE_ONLY_FAST` unless explicitly instructed otherwise.

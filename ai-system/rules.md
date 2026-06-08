# Rules

Status: Draft

## Core Rules

1. Documentation is the source of truth.
2. The Human Owner makes final decisions.
3. AI roles work only inside their responsibility area.
4. Codex is an executor, not a product decision maker.
5. MVP focus has priority over unnecessary completeness.

## Documentation Rules

1. Product decisions must be reflected in `/docs`.
2. System decisions must be reflected in `/ai-system`.
3. If implementation changes behavior, relevant documentation must be updated.
4. If documentation and code conflict, the conflict must be reported.

## Language Rules

1. Human Owner-facing responses should use the Human Owner's language by default.
2. System source-of-truth documents in `/ai-system` use English by default.
3. Prompt package structure, mode markers, decision keywords, file paths, task IDs and command names must not be translated unless an approved system change explicitly requires it.
4. Localization must not change scope, acceptance criteria, forbidden actions, approval status or repository paths.


## Implementation Rules

1. Do not implement without a backlog task.
2. Do not implement without acceptance criteria.
3. Do not add functionality outside task scope.
4. Do not change architecture without approval.
5. Do not change API contracts without updating API Documentation.
6. Do not mix unrelated backend, frontend, infrastructure and documentation work unless the task explicitly allows it.

## Review Rules

1. Every implementation task must pass review.
2. Review must check task scope, architecture, security, readability and error handling.
3. QA must check acceptance criteria and negative scenarios.
4. Critical issues block acceptance.
5. Major issues require fix or explicit human decision.

## Evolution Rules

1. AI Development System cannot be changed directly.
2. Every system change requires an AI System Change Proposal.
3. System changes must be recorded in `system-changelog.md`.
4. System changes should not be mixed with application implementation tasks.
5. Experiments must have success criteria and a final decision.

## Verification Rules

1. For ordinary code-only implementation and bugfix tasks, use `CODE_ONLY_FAST` by default.
2. Browser automation, Playwright/MCP browser sessions, screenshots, manual visual inspections and browser console checks are on-demand QA only.
3. Do not run browser or visual checks unless the Human Owner explicitly requests them or the current task explicitly lists them in acceptance criteria.
4. Do not mark a task `PARTIAL` only because browser checks, screenshots, visual inspection or console checks were skipped, unless those checks were explicitly required for that task.
5. Codex must not silently upgrade verification mode.

## Codex Rules

Every Codex prompt should include:

- role;
- context;
- input documents;
- task ID;
- scope;
- out of scope;
- expected files;
- acceptance criteria;
- result format;
- verification mode.

Codex must report:

- changed files;
- summary;
- tests;
- errors;
- questions;
- diff or key changes.

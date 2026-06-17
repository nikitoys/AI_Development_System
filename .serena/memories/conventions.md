# Conventions

- Always classify repository work by the AI Development System mode. For `[SYSTEM]`, `[CODEX]`, `[REVIEW]`, `[EVOLUTION]`, and repository-affecting tasks, report the header fields: Active Role, Active Stage, Active Document, Expected Result.
- Use CLI gateways for protected project-control mutations. Never edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**`, or `AI_PROJECT/generated/**` manually, and do not use ad-hoc scripts to mutate those paths.
- Generated Markdown is readable output, not source of truth. If generated output drifts, run the owning `render`, `build`, or `check-generated` command.
- Keep tasks narrow: work only within the Task's allowed files, scope, out-of-scope constraints, verification mode, and acceptance criteria.
- Source docs and prompt structures keep stable English markers/fields, even when user-facing explanation may be localized.
- For Python CLI scripts, preserve existing standard-library style, stable error codes/messages, deterministic rendering, audit-event behavior, and temp-root smoke tests. Prefer small helpers over broad refactors.
- Context Packs are derived read-only retrieval context; they may guide reading but cannot expand allowed files, task scope, out-of-scope items, or acceptance criteria. Conflicts are reported with Task/source docs authoritative.
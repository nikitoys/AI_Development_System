<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `57`

Task: `TASK-010` — **P2 Integrate Context Pack into codexctl prompt generation**
Epic: `EPIC-003`
Status: `ready`
Verification: `standard`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Prompt-package integration implementation`
Active Document: `scripts/codexctl.py / AI_PROJECT/generated/CODEX_PROMPT.md`
Expected Result: `codexctl can optionally include a validated read-only Context Pack in generated prompt packages.`

## Summary

Allow codexctl.py to include a validated Context Pack in generated Codex prompt packages.

## Description

Extend codexctl.py so CODEX_PROMPT.md can include a read-only retrieved context section produced by contextctl.py. The Context Pack must help Codex read the right source documents but must not expand task scope, allowed files or acceptance criteria.

## Scope

- Inspect scripts/codexctl.py and scripts/contextctl.py.
- Add explicit context-pack integration option to codexctl.py, using supported CLI design.
- Validate context pack existence and freshness before including it.
- Include context pack path/hash/source metadata in CODEX_PROMPT.md.
- Add prompt rules stating that retrieved context is read-only and does not expand allowed files or task scope.
- Add clear errors for missing, stale or invalid context pack.
- Update prompt package documentation if needed.
- Add smoke/validation coverage.

## Out of Scope

- Do not implement vector search.
- Do not change task lifecycle rules.
- Do not make codexctl.py responsible for document indexing.
- Do not allow retrieved context to override task fields.
- Do not manually edit generated CODEX_PROMPT.md.

## Allowed Files

- scripts/codexctl.py
- scripts/contextctl.py only if needed for compatibility fixes
- scripts/smoke-context-control.py
- scripts/smoke-project-control.py
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/project-control/08-usage-guide.md
- AI_PROJECT/generated/CODEX_PROMPT.md only through codexctl.py
- AI_PROJECT/generated/CONTEXT_PACK.md only through contextctl.py
- AI_PROJECT/events/codex-events.jsonl only through codexctl.py
- AI_PROJECT/events/context-events.jsonl only through contextctl.py

## Acceptance Criteria

- codexctl can build a prompt package with an explicit context pack.
- codexctl fails clearly if the context pack is missing, stale or invalid.
- Generated CODEX_PROMPT.md records context pack path/hash and source metadata.
- Prompt explicitly states that retrieved context is read-only.
- Prompt explicitly states that context does not expand allowed files, scope or acceptance criteria.
- codexctl remains able to build prompts without context pack when requested.
- Required validation/smoke commands pass or blockers are reported.

## Review Instructions

- Report new codexctl options, failure modes, generated prompt changes and compatibility with existing prompt generation.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-010 --to in_progress
python scripts/taskctl.py task transition TASK-010 --to in_review
python scripts/taskctl.py task approve TASK-010 --notes "..."
python scripts/taskctl.py task transition TASK-010 --to done
python scripts/taskctl.py prompt build --write
```

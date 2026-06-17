# Codex Prompt Package

Generated: 2026-06-17T22:13:54Z
Source Type: task
Source ID: TASK-010
Source Status: ready

[SYSTEM]

Active Role:
Codex Executor

Active Stage:
Prompt-package integration implementation

Active Document:
scripts/codexctl.py / AI_PROJECT/generated/CODEX_PROMPT.md

Expected Result:
codexctl can optionally include a validated read-only Context Pack in generated prompt packages.

Repository Context:
This repository is an AI Development System governance control plane.
Project-control state is managed through Python CLI gateways; generated Markdown is derived output.

Source:
Source Task: TASK-010
Task Status: ready
Title: P2 Integrate Context Pack into codexctl prompt generation

Allow codexctl.py to include a validated Context Pack in generated Codex prompt packages.

Extend codexctl.py so CODEX_PROMPT.md can include a read-only retrieved context section produced by contextctl.py. The Context Pack must help Codex read the right source documents but must not expand task scope, allowed files or acceptance criteria.

Scope:
- Inspect scripts/codexctl.py and scripts/contextctl.py.
- Add explicit context-pack integration option to codexctl.py, using supported CLI design.
- Validate context pack existence and freshness before including it.
- Include context pack path/hash/source metadata in CODEX_PROMPT.md.
- Add prompt rules stating that retrieved context is read-only and does not expand allowed files or task scope.
- Add clear errors for missing, stale or invalid context pack.
- Update prompt package documentation if needed.
- Add smoke/validation coverage.

Out of Scope:
- Do not implement vector search.
- Do not change task lifecycle rules.
- Do not make codexctl.py responsible for document indexing.
- Do not allow retrieved context to override task fields.
- Do not manually edit generated CODEX_PROMPT.md.

Allowed Files:
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

Implementation Instructions:
- Inspect current files before editing.
- Stay within allowed files.
- Preserve existing conventions.
- Prefer minimal, commit-ready changes.
- Do not perform unrelated refactors.
- Do not edit AI_PROJECT/state/**, AI_PROJECT/events/** or AI_PROJECT/generated/** manually.

Acceptance Criteria:
- codexctl can build a prompt package with an explicit context pack.
- codexctl fails clearly if the context pack is missing, stale or invalid.
- Generated CODEX_PROMPT.md records context pack path/hash and source metadata.
- Prompt explicitly states that retrieved context is read-only.
- Prompt explicitly states that context does not expand allowed files, scope or acceptance criteria.
- codexctl remains able to build prompts without context pack when requested.
- Required validation/smoke commands pass or blockers are reported.

Verification:
- Use verification mode `standard`.
- Run the validation commands required by the task and report results.

Result Format:
- Summary
- Changed files
- Commands run
- Verification result
- Blockers or risks

Review / Result Format Notes:
- Report new codexctl options, failure modes, generated prompt changes and compatibility with existing prompt generation.

# Codex Prompt Package

Generated: 2026-06-17T21:39:29Z
Source Type: task
Source ID: TASK-008
Source Status: ready

[SYSTEM]

Active Role:
Codex Executor

Active Stage:
Documentation-control implementation

Active Document:
scripts/docctl.py / AI_PROJECT/generated/DOCS_INDEX.md / AI_PROJECT/generated/DOCS_GAPS.md

Expected Result:
docctl metadata and gap detection are strengthened for future context retrieval.

Repository Context:
This repository is an AI Development System governance control plane.
Project-control state is managed through Python CLI gateways; generated Markdown is derived output.

Source:
Source Task: TASK-008
Task Status: ready
Title: P0 Strengthen docctl metadata and documentation gaps

Improve docctl.py so registered documentation becomes a reliable source for future context retrieval.

Add stricter documentation-control capabilities before implementing retrieval. The documentation registry must be able to detect status drift, content changes after review, stale indexes and root-level documentation coverage gaps.

Scope:
- Inspect scripts/docctl.py and current docs state.
- Add or specify document status/frontmatter synchronization checks.
- Add content hash tracking for registered documents.
- Add last reviewed content hash tracking.
- Improve DOCS_GAPS.md categories so gaps are actionable.
- Extend registration/scanning model to include root docs and skills where appropriate.
- Keep AI_PROJECT/state/docs.json authoritative and mutable only through docctl.py.
- Update related project-control documentation if needed.

Out of Scope:
- Do not implement contextctl.py.
- Do not implement vector search.
- Do not change codexctl.py behavior.
- Do not manually edit AI_PROJECT/state/**, AI_PROJECT/events/** or AI_PROJECT/generated/**.
- Do not mark documents active without Human Owner approval.

Allowed Files:
- scripts/docctl.py
- ai-system/project-control/08-usage-guide.md
- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/03-state-model.md
- ai-system/document-lifecycle.md
- scripts/smoke-doc-control.py
- AI_PROJECT/state/docs.json only through docctl.py
- AI_PROJECT/events/doc-events.jsonl only through docctl.py
- AI_PROJECT/generated/DOCS_INDEX.md only through docctl.py
- AI_PROJECT/generated/DOCS_GAPS.md only through docctl.py

Implementation Instructions:
- Inspect current files before editing.
- Stay within allowed files.
- Preserve existing conventions.
- Prefer minimal, commit-ready changes.
- Do not perform unrelated refactors.
- Do not edit AI_PROJECT/state/**, AI_PROJECT/events/** or AI_PROJECT/generated/** manually.

Acceptance Criteria:
- docctl validation detects mismatch between registry status and declared document status/frontmatter when such status is present.
- docctl tracks current document content hash.
- docctl mark-reviewed records the reviewed content hash.
- DOCS_GAPS.md distinguishes at least: missing file, status mismatch, active not reviewed, active review stale, unresolved placeholder, broken local link, stale index or equivalent actionable categories.
- docctl can register or account for root-level documents and skills without treating generated files as authoritative source docs.
- Existing generated documentation outputs are regenerated only through docctl.py.
- Existing plan/task/documentation validation passes or blockers are reported clearly.
- No protected project-control files are edited manually.

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
- Report changed files, commands run, validation results, generated files updated and any remaining documentation-control risks.

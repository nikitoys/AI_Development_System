# Document Lifecycle

Status: Draft
Version: v0.1.0

## Purpose

This document defines how source-of-truth documents are created, read, updated, reviewed, approved, deprecated, archived, removed and rolled back inside the AI Development System.

It applies the shared governance model from `/ai-system/lifecycle-governance.md` to documentation.

## Governed Entity

A managed document is any repository document whose content affects the AI Development System, product direction, architecture, task execution, review, approval, lifecycle governance or repository operation.

Managed documents include:

- AI Development System documents in `/ai-system`;
- product documents in `/docs` when a product project exists;
- repository entrypoint documents such as `README.md` and localized README variants;
- task, prompt, review, changelog and decision documents;
- approved templates that shape future work.

Temporary notes, scratch files and generated outputs are not managed documents unless they are accepted as source-of-truth documents.

## Source of Truth

Documentation is the source of truth for system and product decisions.

Default source-of-truth locations:

- `/ai-system` for AI Development System rules, roles, workflow, prompt lifecycle, review process and governance;
- `/docs` for product vision, requirements, architecture, UX, API, backlog and project-specific decisions;
- root `README.md` and localized README variants for repository entrypoint information.

If documentation and implementation conflict, the conflict must be reported before the document or implementation is treated as authoritative.

## Document Lifecycle States

Managed documents should use these states where applicable:

- `Proposed` - suggested but not yet drafted or approved.
- `Draft` - written for review, not yet accepted as active source of truth.
- `In Review` - being checked for scope, consistency, clarity and governance impact.
- `Active` - accepted and currently used as source of truth.
- `Experimental` - approved temporarily with explicit success criteria and review date.
- `Deprecated` - still retained, but no longer recommended for new work.
- `Archived` - retained for history, not used for active decisions.
- `Rejected` - reviewed and not accepted.
- `Removed` - deleted from active documentation after approval and reference cleanup.

A document may omit an explicit status field only when the surrounding repository convention already defines its status. For AI Development System documents, a visible `Status` field is preferred.

When a managed document declares status in YAML frontmatter, a `Status:` metadata line or a `## Status` section, the declaration should stay synchronized with the project-control registry status managed by `docctl.py`.

## Document Operations

## Read

Goal: understand the current documented truth before acting.

Rules:

- Read source documents listed by the task or mode.
- Prefer `/ai-system` for system behavior and `/docs` for product behavior.
- Report conflicts, missing documents or stale references before relying on unclear content.

## Create

Goal: add a new managed document when existing documents cannot safely hold the needed information.

Creation is appropriate when:

- a recurring concept needs its own source of truth;
- existing documents would become too broad;
- a lifecycle, rule, role, process or template must be reusable;
- Human Owner approval or an approved task authorizes the document.

Creation should define purpose, governed entity or topic, ownership, status and relationship to existing documents.

## Update

Goal: change an existing managed document while preserving traceability.

Updates must be scoped to the approved task or Human Owner request.

If an update changes system behavior, role responsibilities, workflow, approval rules, prompt structure, review rules or version impact, it must follow the change process and may require AICP.

## Review

Goal: verify that the document is clear, consistent and safe to use.

Documentation review should check:

- consistency with source documents;
- conflicts with existing rules or decisions;
- scope control;
- language and localization policy;
- broken references or missing index updates;
- whether changelog or improvement log updates are needed.

When review is recorded through `docctl.py doc mark-reviewed`, the review record should include the content hash that was reviewed so later edits can be detected as stale review evidence.

## Approve

Goal: accept a document as active source of truth.

Only the Human Owner approves system-level document changes.

AI roles may recommend `APPROVED`, `REWORK`, `REJECTED`, `DEFERRED` or `EXPERIMENT`, but they do not make the final decision.

## Reject

Goal: mark a proposed or draft document as not accepted.

Rejected documents should either be removed before becoming source of truth or retained only when useful for history.

If retained, the reason for rejection should be clear.

## Deprecate

Goal: mark an active document as no longer recommended while preserving history.

Deprecation requires Human Owner approval when the document is an active source of truth.

A deprecation note should include:

- reason;
- replacement document or process;
- date or version;
- removal condition.

## Archive

Goal: keep an inactive document for historical reference.

Archived documents must not be used for new decisions unless explicitly restored or referenced as history.

Archive actions should update indexes or references that could otherwise route users to inactive guidance.

## Remove

Goal: delete a managed document after it is no longer needed.

Removal requires Human Owner approval when the document was active or referenced.

Before removal:

- references must be found and updated;
- replacement documents must be identified if needed;
- changelog or audit history must preserve the reason.

## Roll Back

Goal: restore a previous document state after an applied change causes problems.

Rollback requires Human Owner approval for system-level source-of-truth documents.

Rollback should record:

- what changed back;
- why rollback was needed;
- which version or commit was restored;
- follow-up work if partial rollback leaves gaps.

## Ownership Model

Default ownership:

- Human Owner approves system-level and product-level source-of-truth changes.
- ChatGPT Orchestrator routes document requests and selects relevant source documents.
- AI System Maintainer owns AI Development System document evolution.
- Technical Writer AI owns clarity, structure, consistency and index updates.
- Product, architecture, implementation or quality roles may own content in their domain.
- Codex Executor applies approved document edits only within explicit scope.

Each specific lifecycle or workflow document may define more precise ownership.

## Approval Rules

Human Owner approval is required for document changes that:

- create or remove source-of-truth documents;
- change AI Development System behavior;
- change roles, workflows, lifecycle states or approval rules;
- change prompt package requirements;
- change review, QA or Codex execution rules;
- deprecate or archive active system documents;
- roll back applied system documentation changes;
- change repository documentation language policy.

Small wording, typo, formatting or link corrections may be handled as patch-level documentation updates when they do not change behavior.

## AICP Relationship

An AICP is required when a document change affects:

- AI Development System behavior;
- role definitions or responsibilities;
- lifecycle governance;
- workflow or approval process;
- prompt requirements;
- review process;
- system version;
- permanent adoption of an experiment.

An AICP is not required for narrow wording corrections, index updates or documentation clarifications that do not change behavior, but those changes should still be recorded when they affect source-of-truth documents.

## Version Impact Rules

Use `MAJOR.MINOR.PATCH`.

- Patch: typo, wording, formatting, link correction or clarification without behavior change.
- Minor: new source-of-truth document, new lifecycle document, new rule, new template or meaningful process addition.
- Major: significant documentation model, approval model, role hierarchy, workflow or governance change.

When uncertain, choose the higher impact and ask the Human Owner to confirm.

## Audit and History Rules

Document changes should leave enough history to understand:

- what changed;
- why it changed;
- who approved it;
- which documents were affected;
- whether the change was proposed, applied, rejected, experimental, deprecated, archived, removed or rolled back.

Use:

- `system-changelog.md` for applied AI Development System document changes;
- `improvement-log.md` for observed documentation process problems and improvement ideas;
- AICP documents for proposed system behavior changes;
- git history for exact diffs and commits.

## Index and Reference Rules

When a managed document is created, deprecated, archived, removed or renamed, update relevant index and status documents within the approved scope.

Common index documents include:

- `/ai-system/README.md`;
- `/ai-system/operating-model.md`;
- root `README.md` when the repository entrypoint changes.

Do not leave stale references to missing or inactive source-of-truth documents.

## Boundary Rules

Document lifecycle must not be used to bypass Human Owner control.

Document lifecycle must not combine unrelated documentation, product, implementation or system evolution changes unless explicitly approved.

Documentation updates must not silently change product scope, system behavior, architecture, prompt requirements or acceptance criteria.

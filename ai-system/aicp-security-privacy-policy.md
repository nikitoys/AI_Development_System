# AICP-002: Add Security, Privacy and Data-Handling Policy

## Status
Applied

## Problem

AI_Development_System assumes external AI tools, Codex-like executors and repository automation, but security, privacy and data-handling rules were not centralized.

## Evidence

`EVOL-004` in `ai-system/evolution/evolution-backlog.md` identifies this as a P1 security/privacy gap derived from analytical report findings.

## Root Cause

Security expectations were distributed across review, execution and verification guidance instead of being expressed as a source-of-truth policy.

## Proposed Change

Add centralized policy documents for:

- secret handling;
- external LLM data sharing;
- sandbox and execution boundaries;
- sensitive-code handling;
- security/privacy review references;
- project-template inheritance.

## Affected Files

- `ai-system/security-policy.md`
- `ai-system/privacy-data-handling-policy.md`
- `ai-system/review-process.md`
- `ai-system/rules.md`
- `ai-system/README.md`
- `ai-system/templates/project/AGENTS.md`
- `ai-system/templates/foldered/AGENTS.root.md`
- `ai-system/templates/foldered/AI_PROJECT/AGENTS.md`
- `ai-system/templates/project/CODEX_WORKFLOW.md`
- `ai-system/templates/foldered/AI_PROJECT/CODEX_WORKFLOW.md`
- `ai-system/evolution/evolution-backlog.md`
- `ai-system/evolution/owner-evolution-plan.md`
- `ai-system/system-changelog.md`
- `README.md`
- `README.ru.md`

## Expected Benefit

AI-assisted work has a clear baseline for secrets, private data, external model sharing and execution boundaries.

## Risks

The policy may be conservative for some projects. Concrete projects may add stricter local rules, but must not weaken the inherited baseline without explicit Human Owner approval.

## Decision

Approved by Human Owner request to execute `EVOL-004`.

## Version Impact

Minor.

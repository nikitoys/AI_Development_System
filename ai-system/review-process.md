# Review Process

Status: Draft

## Purpose

This document defines how implementation results are reviewed.

## Review Types

## Code Review

Performed by Code Reviewer AI.

Checks:

- task compliance;
- architecture compliance;
- readability;
- security;
- performance risks;
- error handling;
- unnecessary scope expansion.

## QA Review

Performed by QA Engineer AI.

Checks:

- acceptance criteria;
- positive scenarios;
- negative scenarios;
- edge cases;
- user-facing errors;
- regression risks.

## Documentation Review

Performed by Technical Writer AI or ChatGPT Orchestrator.

Checks:

- README updates;
- API documentation updates;
- changelog updates;
- consistency between code and docs.

## Severity Levels

- `Critical` — blocks acceptance.
- `Major` — should be fixed before acceptance unless Human Owner explicitly accepts risk.
- `Minor` — non-blocking issue.
- `Suggestion` — optional improvement.

## Review Output Format

```md
# Review Report

## Summary

## Critical Issues

## Major Issues

## Minor Issues

## Suggestions

## Final Verdict
APPROVED / REWORK / REJECTED
```

## Rule

A task cannot be considered Done until review is completed and Human Owner approves the result.

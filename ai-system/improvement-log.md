# Improvement Log

Status: Draft

This file records observed process problems and improvement ideas.

Entries here do not change the AI Development System directly.

System changes must go through `change-process.md` and an AI System Change Proposal.

## Template

```md
## IMP-000: Title

### Status
Observed / Proposed / Converted to AICP / Closed

### Problem
What happened?

### Evidence
Where did it happen?

### Impact
What was affected?

### Possible Cause
Why might it have happened?

### Next Step
Observe / Create AICP / Close
```

## Entries

## IMP-001: Unstable Response and Prompt Language

### Status
Converted to AICP

### Problem
AI Development System responses and generated prompts may appear in English when the Human Owner expects Russian output.

### Evidence
The Human Owner reported periodic English answers and prompt artifacts during repository work.

### Impact
Human-facing output becomes less predictable, and generated prompt artifacts may mix review language with execution language without a clear rule.

### Possible Cause
The system did not define a separate language policy for Human Owner-facing responses, prompt package structure and repository documentation.

### Next Step
Converted to `/ai-system/aicp-language-policy.md` and addressed by `/ai-system/language-policy.md`.

## IMP-002: Agent Planner Dependency Graph Parsing Is Shallow

### Status
Proposed

### Problem
`scripts/agent-plan-mvp.py list-parallel-groups` may list all non-blocked Agent Work Packages as one informational candidate group instead of excluding packages with unresolved dependencies.

### Evidence
During EVOL-018 pilot validation, the golden project intended `CPG-001` as `AWP-BE-001 + AWP-FE-001` only after `AWP-REQ-001`, but the helper reported `AWP-REQ-001`, `AWP-BE-001`, `AWP-FE-001` and `AWP-QA-001` as one informational candidate group.

### Impact
The helper remains useful for dry-run reporting, but its candidate parallel group output must be manually reviewed and should not be treated as dependency-aware planning.

### Possible Cause
The MVP intentionally uses simple Markdown-oriented parsing and does not deeply parse dependency graphs from `AGENT_PLAN.md` or `AGENT_TASKS.md`.

### Next Step
Track as proposed `EVOL-020 — Improve dry-run agent planner dependency parsing`. Do not fix during EVOL-018.

# SOP / Multi-Agent Pilot Validation

Status: Draft  
Version: v0.1.0

## Purpose

This document records pilot validation findings for the SOP-guided and optional multi-agent layer.

The goal is to test whether the current documents, templates, golden project example and dry-run planning helper provide enough evidence to support the next runtime decision step.

This document does not approve runtime implementation.

## Scope

In scope:

- validate the filled `examples/golden-project/` multi-agent planning example;
- run dry-run agent planning commands;
- run documentation integrity validation;
- manually review SOP, Agent Work Package, dependency, lock, result, review, QA and metric coverage;
- manually review safety boundaries;
- record findings, limitations and recommended follow-ups.

Out of scope:

- no runtime implementation;
- no Codex execution;
- no branch, worktree, merge or acceptance automation;
- no script fixes;
- no spec changes;
- no template changes;
- no product or application code changes.

## Source Documents and Artifacts

- `ai-system/evolution/sop-multi-agent-implementation-plan.md`
- `ai-system/sop-model.md`
- `ai-system/agent-work-package.md`
- `ai-system/multi-agent-planning.md`
- `ai-system/parallel-execution-policy.md`
- `ai-system/agent-result-intake.md`
- `ai-system/integration-review.md`
- `spec/sops.json`
- `spec/agent-work-package.schema.json`
- `spec/agent-result.schema.json`
- `spec/parallel-policy.json`
- `ai-system/templates/foldered/AI_PROJECT/AGENT_PLAN.md`
- `ai-system/templates/foldered/AI_PROJECT/AGENT_TASKS.md`
- `ai-system/templates/foldered/AI_PROJECT/AGENT_LOCKS.md`
- `ai-system/templates/foldered/AI_PROJECT/AGENT_RESULTS.md`
- `ai-system/templates/foldered/AI_PROJECT/AGENT_METRICS.md`
- `examples/golden-project/`
- `scripts/agent-plan-mvp.py`
- `scripts/check-docs-integrity.py`

## Pilot Scenarios

### 1. Golden Project Dry-Run Validation

Commands:

```bash
python3 scripts/agent-plan-mvp.py validate --project-root examples/golden-project
python3 scripts/agent-plan-mvp.py check-locks --project-root examples/golden-project
python3 scripts/agent-plan-mvp.py list-parallel-groups --project-root examples/golden-project
python3 scripts/agent-plan-mvp.py generate-prompts --project-root examples/golden-project
```

Observed results:

- `validate` found all five `AI_PROJECT/AGENT_*` files.
- `validate` recognized four Agent Work Packages: `AWP-REQ-001`, `AWP-BE-001`, `AWP-FE-001` and `AWP-QA-001`.
- Each package was reported as ready and complete enough for planning.
- `check-locks` read `AI_PROJECT/AGENT_LOCKS.md` and detected no lock conflicts from available data.
- `list-parallel-groups` listed one informational candidate group containing all four packages.
- `generate-prompts` printed four bounded prompt drafts for review only and did not execute them.

### 2. Documentation Integrity Validation

Command:

```bash
python3 scripts/check-docs-integrity.py
```

Observed result:

- Documentation integrity check passed before recording this EVOL-018 document and passed again after documentation updates.

### 3. Manual Golden Example Review

The golden example demonstrates:

- selected SOP: `SOP-FEATURE-001`;
- Agent Work Package decomposition;
- dependencies between requirements, backend, frontend and QA packages;
- `allowed_files` and `locked_files`;
- candidate parallel group `CPG-001` as informational only;
- Human Owner approval boundary;
- result intake placeholders;
- integration review placeholder/status;
- QA handoff placeholder/status;
- metrics placeholder/status;
- dry-run helper usage.

### 4. Manual Safety Boundary Review

The current SOP / optional multi-agent layer preserves these boundaries:

- no automatic execution;
- no automatic merge;
- no automatic acceptance;
- Human Owner approval remains required;
- candidate parallel groups are informational until approved under the Parallel Execution Policy;
- sequential execution remains the default.

### 5. Tool Limitation Review

`scripts/agent-plan-mvp.py` currently performs useful Markdown-oriented dry-run reporting but does not deeply parse dependency graphs from the planning files.

As a result, `list-parallel-groups` may list all non-blocked packages as one informational candidate group. In the golden example, the intended candidate group is narrower: `CPG-001` is `AWP-BE-001 + AWP-FE-001` only after `AWP-REQ-001` has been accepted.

## Findings

### FINDING-001: Golden Project Planning Files Are Discoverable

- Finding ID: `FINDING-001`
- Type: Success
- Severity: Minor
- Evidence: `validate` reported all five `AI_PROJECT/AGENT_*` files as present.
- Impact: The foldered example is usable as a pilot artifact for agent planning validation.
- Recommended follow-up: Keep the golden project as the primary non-runtime example for future pilot checks.
- Suggested target EVOL or future backlog item: Covered by `EVOL-017`; no new backlog item required.

### FINDING-002: Agent Work Packages Are Recognized

- Finding ID: `FINDING-002`
- Type: Success
- Severity: Minor
- Evidence: `validate` recognized `AWP-REQ-001`, `AWP-BE-001`, `AWP-FE-001` and `AWP-QA-001`.
- Impact: The current template and example format is sufficient for simple package discovery.
- Recommended follow-up: Preserve table-based package entries unless future parser work introduces a stricter format.
- Suggested target EVOL or future backlog item: No new backlog item required.

### FINDING-003: Lock Conflict Check Works for Available Data

- Finding ID: `FINDING-003`
- Type: Success
- Severity: Minor
- Evidence: `check-locks` read `AI_PROJECT/AGENT_LOCKS.md` and reported no detected lock conflicts.
- Impact: The helper can support early file-scope conflict review when lock data is present.
- Recommended follow-up: Continue using `AGENT_LOCKS.md` as the explicit lock registry for pilot examples.
- Suggested target EVOL or future backlog item: No new backlog item required.

### FINDING-004: Candidate Parallel Group Reporting Is Over-Broad

- Finding ID: `FINDING-004`
- Type: Limitation
- Severity: Major
- Evidence: `list-parallel-groups` reported `candidate_group_1: AWP-REQ-001, AWP-BE-001, AWP-FE-001, AWP-QA-001`, while the golden example records intended `CPG-001` as `AWP-BE-001 + AWP-FE-001` only after `AWP-REQ-001`.
- Impact: The dry-run helper is useful for visibility, but it should not be treated as a reliable dependency-aware parallel planner yet.
- Recommended follow-up: Add a future bounded script improvement to parse dependencies from standard planning files and exclude packages with unresolved prerequisites from candidate parallel groups.
- Suggested target EVOL or future backlog item: Add `EVOL-020 — Improve dry-run agent planner dependency parsing`; record as `IMP-002`.

### FINDING-005: Prompt Draft Generation Preserves Execution Boundaries

- Finding ID: `FINDING-005`
- Type: Success
- Severity: Minor
- Evidence: `generate-prompts` printed four prompt drafts and explicitly stated they were generated for review only and not sent to Codex.
- Impact: The helper can prepare bounded prompt drafts without becoming an execution runtime.
- Recommended follow-up: Keep prompt generation dry-run only unless a future approved evolution task changes the boundary.
- Suggested target EVOL or future backlog item: No new backlog item required.

### FINDING-006: Documentation Integrity Passed

- Finding ID: `FINDING-006`
- Type: Success
- Severity: Minor
- Evidence: `python3 scripts/check-docs-integrity.py` passed before EVOL-018 documentation was recorded and passed again after documentation updates.
- Impact: The current documentation baseline is coherent enough for pilot recording and updated index/version references remain consistent.
- Recommended follow-up: Continue running the integrity check after each bounded evolution task.
- Suggested target EVOL or future backlog item: No new backlog item required.

### FINDING-007: Runtime Integration Is Not Justified Yet

- Finding ID: `FINDING-007`
- Type: Risk
- Severity: Major
- Evidence: The governance layer, templates, specs and dry-run helper work as documentation and reporting artifacts, but dependency-aware planning remains limited and no live execution pilot has been approved.
- Impact: Starting runtime automation now would exceed the evidence gathered by this pilot and could weaken the one-task, approval-gated workflow.
- Recommended follow-up: Use `EVOL-019` to record a runtime decision. Current evidence supports deferring runtime integration and continuing with bounded dry-run improvements.
- Suggested target EVOL or future backlog item: `EVOL-019`; possible follow-up `EVOL-020`.

## Follow-Up Routing

| Finding | Route | Notes |
| --- | --- | --- |
| `FINDING-001` | No new item | Success covered by `EVOL-017`. |
| `FINDING-002` | No new item | Current examples are parseable enough for simple discovery. |
| `FINDING-003` | No new item | Lock checks work with available data. |
| `FINDING-004` | Backlog item + improvement-log entry + script improvement | Track as `EVOL-020` and `IMP-002`. No fix in EVOL-018. |
| `FINDING-005` | No new item | Prompt drafts remain dry-run only. |
| `FINDING-006` | No new item | Re-run after documentation updates. |
| `FINDING-007` | EVOL-019 decision input | Recommendation is to defer runtime integration. |

No AICP, spec change or template change is required by this pilot record.

## Recommendation for EVOL-019 Runtime Decision

Recommended EVOL-019 decision: `DEFERRED`.

Reasoning:

- the governance-first SOP / optional multi-agent layer is coherent as documentation, templates, specs and dry-run reporting;
- the golden project can demonstrate bounded planning without product runtime code;
- the dry-run helper preserves safety boundaries;
- dependency-aware parallel group calculation is not mature enough to justify runtime execution;
- Human Owner approval, review, QA and final acceptance must remain manual gates.

EVOL-019 should record the Human Owner runtime decision. It should not start runtime implementation unless the Human Owner explicitly approves a new bounded runtime experiment.

## Remaining Risks

- Markdown-oriented parsing may miss malformed dependencies, ambiguous package relationships or hidden lock conflicts.
- Candidate parallel groups require manual review until dependency parsing improves.
- Future runtime proposals could accidentally weaken the one-task loop unless EVOL-019 keeps the governance-first boundary explicit.
- Golden project coverage is useful but still a single example, not broad validation across multiple project types.

## Next-Step Recommendation

Next bounded phase: `EVOL-019 — Decide whether runtime integration is justified`.

Recommended outcome for EVOL-019: record a `DEFERRED` runtime decision and allow only bounded dry-run improvements unless the Human Owner explicitly approves a separate experiment.

Recommended follow-up after EVOL-019: consider `EVOL-020 — Improve dry-run agent planner dependency parsing`.

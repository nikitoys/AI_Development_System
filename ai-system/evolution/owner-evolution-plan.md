# Owner Evolution Plan

Status: Draft  
Version: v0.1.0

## Purpose

This document is the Human Owner-authored intake place for high-level plans to evolve AI_Development_System.

The plan may be broad, strategic or incomplete. It is not an executable task by itself.

## Intake Rule

The Human Owner may paste a system evolution plan in this document.

Codex and AI roles may use the plan only to:

- preserve the owner-authored intent;
- extract candidate roadmap items;
- extract candidate evolution backlog items;
- identify the next bounded evolution task;
- prepare a reviewable task or proposal for Human Owner approval.

Codex and AI roles must not implement the whole plan automatically.

## Current Owner Plan

```text
Source: GitHub issue #7, "Add owner-authored evolution plan intake workflow"
URL: https://github.com/nikitoys/AI_Development_System/issues/7
Opened: 2026-06-09

Goal:
Make AI_Development_System usable in the mode where the Human Owner writes a
high-level plan, and Codex records it, decomposes it into evolution backlog
items, and implements approved bounded tasks step by step.

Example Human Owner plan:
1. Synchronize versions.
2. Add docs CI.
3. Add security/privacy policy.
4. Add golden example project.

Desired Codex behavior:
1. Record the plan without silently rewriting intent.
2. Map plan items to ai-system/evolution/roadmap.md.
3. Create or update items in ai-system/evolution/evolution-backlog.md.
4. Select only the next approved bounded item.
5. Prepare a scoped task using ai-system/evolution/templates/evolution-task.md.
6. Modify only allowed files.
7. Update changelog/history when required.
8. Report what was done and what remains.

Governance boundary:
Owner plan -> recorded plan -> roadmap/backlog mapping -> one bounded task ->
review -> owner approval -> next task.
```

## Plan Metadata

```text
Plan ID: OWNER-EVOL-001
Plan title: Owner-authored evolution plan intake workflow
Author: Human Owner
Date recorded: 2026-06-09
Status: Partially Planned
Related roadmap items: P1, P2, P3, P4
Related backlog items: EVOL-002, EVOL-003, EVOL-004, EVOL-005, EVOL-006
Next bounded task: No active OWNER-EVOL-001 task remains; future P5 bootstrap/update tooling requires a separate bounded backlog item and approval.
```

## Owner Goals

- Let the Human Owner provide a high-level evolution plan once.
- Preserve the plan without silently rewriting owner intent.
- Map plan items to roadmap and evolution backlog items.
- Execute approved bounded evolution tasks step by step.

## Constraints

- One evolution task at a time.
- Human Owner approval remains required for behavior-changing system changes.
- Product code changes are out of scope unless explicitly approved as a separate integration or pilot task.
- Roadmap priority changes require Human Owner approval.
- AICP is required when the plan changes governance, roles, lifecycle states, approval gates, security/privacy policy, integration contracts or system prompt behavior.

## Extracted Roadmap Candidates

| Candidate | Existing roadmap item | Proposed action | Approval required |
| --- | --- | --- | --- |
| Synchronize versions | P1 - Consistency and Documentation Integrity | Map to existing roadmap item | No new roadmap approval required |
| Add docs CI | P1 - Consistency and Documentation Integrity | Map to existing roadmap item | No new roadmap approval required |
| Add security/privacy policy | P2 - Security, Privacy and Data Handling | Map to existing roadmap item | Human Owner approval required before behavior-changing policy work |
| Add golden example project | P3 - Golden Example and Pilot Validation | Map to existing roadmap item | Human Owner approval required before pilot/example scope execution |

## Extracted Backlog Candidates

| Candidate | Roadmap item | Priority | Type | Conversion path |
| --- | --- | --- | --- | --- |
| Synchronize versions | P1 - Consistency and Documentation Integrity | P1 | Documentation | Existing backlog item `EVOL-002`; bounded documentation task |
| Add docs CI | P1 - Consistency and Documentation Integrity | P1 | Verification | Existing backlog item `EVOL-003`; system change and automation task |
| Add security/privacy policy | P2 - Security, Privacy and Data Handling | P1 | Security / Privacy | Existing backlog item `EVOL-004`; AICP required |
| Add golden example project | P3 - Golden Example and Pilot Validation | P2 | Pilot Validation | Existing backlog item `EVOL-005`; experiment or system change depending on scope |

## Completed Bounded Task

```text
Task title: Synchronize versions and document statuses
Source plan section: 1. Synchronize versions.
Roadmap item: P1 - Consistency and Documentation Integrity
Backlog item: EVOL-002 - Synchronize versions and document statuses
Active Role: AI System Maintainer + Technical Writer AI
Active Stage: System Evolution Release
Active Document: ai-system/evolution/evolution-backlog.md
Expected Result: Version/status synchronization completed locally
Allowed files: README.md, README.ru.md, ai-system/README.md, ai-system/evolution/evolution-backlog.md, ai-system/evolution/owner-evolution-plan.md, ai-system/system-changelog.md
Out of scope: Docs CI, security/privacy policy, golden example project, product code
Acceptance criteria: Authoritative version source documented; README versions synchronized; changelog updated; EVOL-002 status updated
Verification mode: CODE_ONLY_FAST
Human Owner approval required: Human Owner reviews local result before commit/push
```

## Completed Bounded Task

```text
Task title: Add documentation integrity checks
Source plan section: 2. Add docs CI.
Roadmap item: P1 - Consistency and Documentation Integrity
Backlog item: EVOL-003 - Add documentation integrity checks
Active Role: AI System Maintainer + DevOps AI
Active Stage: System Evolution Release
Active Document: ai-system/evolution/evolution-backlog.md
Expected Result: Documentation integrity checks added
Allowed files: scripts/check-docs-integrity.py, .github/workflows/docs-integrity.yml, README.md, README.ru.md, ai-system/README.md, ai-system/evolution/evolution-backlog.md, ai-system/evolution/owner-evolution-plan.md, ai-system/system-changelog.md
Out of scope: security/privacy policy, golden example project, product code
Acceptance criteria: Markdown links checked; unresolved placeholders checked; index completeness checked; version/status consistency checked; changelog updated; EVOL-004 recommended next
Verification mode: FAST_VALIDATION
Human Owner approval required: Human Owner reviews local result before commit/push
```

## Completed Bounded Task

```text
Task title: Add security, privacy and data-handling policy
Source plan section: 3. Add security/privacy policy.
Roadmap item: P2 - Security, Privacy and Data Handling
Backlog item: EVOL-004 - Add security, privacy and data-handling policy
Active Role: AI System Maintainer + Security Reviewer AI
Active Stage: System Evolution Release
Active Document: ai-system/evolution/evolution-backlog.md
Expected Result: Security/privacy/data-handling policy added
Allowed files: ai-system/aicp-security-privacy-policy.md, ai-system/security-policy.md, ai-system/privacy-data-handling-policy.md, ai-system/review-process.md, ai-system/rules.md, ai-system/README.md, ai-system/templates/project/AGENTS.md, ai-system/templates/foldered/AGENTS.root.md, ai-system/templates/foldered/AI_PROJECT/AGENTS.md, ai-system/templates/project/CODEX_WORKFLOW.md, ai-system/templates/foldered/AI_PROJECT/CODEX_WORKFLOW.md, ai-system/evolution/evolution-backlog.md, ai-system/evolution/owner-evolution-plan.md, ai-system/system-changelog.md, README.md, README.ru.md
Out of scope: golden example project, machine-checkable spec layer, product code
Acceptance criteria: Secret-handling rules exist; external LLM data-sharing rules exist; sandbox/execution boundaries exist; security review can reference policy; project templates inherit policy
Verification mode: FAST_VALIDATION
Human Owner approval required: Human Owner reviews local result before commit/push
```

## Completed Bounded Task

```text
Task title: Create golden example project
Source plan section: 4. Add golden example project.
Roadmap item: P3 - Golden Example and Pilot Validation
Backlog item: EVOL-005 - Create golden example project
Active Role: AI System Maintainer + Technical Writer AI
Active Stage: System Evolution Release
Active Document: ai-system/evolution/evolution-backlog.md
Expected Result: A fully filled Task Tracker foldered example exists in `examples/golden-project/`
Allowed files: examples/golden-project/AGENTS.md, examples/golden-project/AI_PROJECT/AGENTS.md, examples/golden-project/AI_PROJECT/PROJECT_GOAL.md, examples/golden-project/AI_PROJECT/OWNER_PLAN.md, examples/golden-project/AI_PROJECT/CODEX_COMMANDS.md, examples/golden-project/AI_PROJECT/CODEX_WORKFLOW.md, examples/golden-project/AI_PROJECT/CODEX_PLAN.md, examples/golden-project/AI_PROJECT/CODEX_CURRENT.md, examples/golden-project/AI_PROJECT/CODEX_TASKS.md, examples/golden-project/AI_PROJECT/CODEX_SESSION_LOG.md, examples/golden-project/AI_PROJECT/PROMPTS.md, examples/golden-project/AI_PROJECT/AI_DEV_SYSTEM_VERSION.md, examples/golden-project/AI_PROJECT/docs/verification-policy.md, ai-system/README.md, ai-system/evolution/evolution-backlog.md, ai-system/evolution/owner-evolution-plan.md, ai-system/system-changelog.md
Out of scope: machine-checkable spec layer, bootstrap tooling, security/privacy policy, product code
Acceptance criteria: Golden example includes root AGENTS and filled AI_PROJECT control files; explicit verification policy; zero product implementation files in example
Verification mode: FAST_VALIDATION
Human Owner approval required: Human Owner reviews local result before commit/push
```

## Completed Bounded Task

```text
Task title: Introduce machine-checkable specification layer
Source plan section: Follow-up bounded phase after golden example completion.
Roadmap item: P4 - Machine-Checkable Specification Layer
Backlog item: EVOL-006 - Introduce machine-checkable specification layer
Active Role: AI System Maintainer + Technical Writer AI
Active Stage: System Evolution Release
Active Document: ai-system/evolution/evolution-backlog.md
Expected Result: Minimal machine-checkable `spec/` layer exists for roles, interaction modes, verification modes and lifecycle states
Allowed files: spec/README.md, spec/roles.json, spec/interaction-modes.json, spec/verification-modes.json, spec/lifecycle-states.json, spec/schemas/system-spec.schema.json, README.md, README.ru.md, ai-system/README.md, ai-system/evolution/evolution-backlog.md, ai-system/evolution/owner-evolution-plan.md, ai-system/system-changelog.md
Out of scope: Markdown regeneration, deleting existing docs, CI schema lint, bootstrap tooling, release packaging, research work
Acceptance criteria: First spec area selected; schema defined; validation process documented; generated/derived documentation policy defined
Verification mode: FAST_VALIDATION
Human Owner approval required: Human Owner reviews local result before commit/push
```

## Next Bounded Task Candidate

```text
Task title: Define next approved system evolution backlog item
Source plan section: Post-OWNER-EVOL-001 continuation.
Roadmap item: P5 - Bootstrap and Update Tooling or another Human Owner-approved roadmap item
Backlog item: To be created only after Human Owner approval
Active Role: AI System Maintainer + Technical Writer AI
Active Stage: System Evolution Planning
Active Document: ai-system/evolution/evolution-backlog.md
Expected Result: Prepare one bounded next evolution item without starting implementation
Allowed files: To be defined in the bounded task package before execution
Out of scope: unapproved bootstrap work, release packaging, research work, product implementation
Acceptance criteria: To be defined before execution
Verification mode: CODE_ONLY_FAST unless spec validation requires stronger checks
Human Owner approval required: Yes before creating or executing the next backlog item
```

## Intake Notes

- Record assumptions separately from owner-authored text.
- Keep unresolved questions visible.
- Do not rewrite owner intent into a decision unless the Human Owner approves it.
- Move only one bounded task into execution at a time.

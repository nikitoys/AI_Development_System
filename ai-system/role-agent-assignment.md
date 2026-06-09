# Role-to-Agent Assignment Model

Status: Draft  
Version: v0.1.0

## Purpose

This document defines the Role-to-Agent Assignment Model for `L3 — Manual multi-agent orchestration`.

The model lets the Human Owner or ChatGPT Orchestrator manually assign ready Agent Work Packages to logical agents or external agent sessions while preserving L3 boundaries.

This document does not implement runtime behavior.

It does not authorize automatic Codex execution, automatic agent dispatch, automatic multi-agent execution, branch/worktree automation, automatic file modification by orchestration tooling, automatic merge, automatic acceptance or automatic QA/review closure.

## Runtime Maturity Relationship

Current level:

```text
L3 — Manual multi-agent orchestration
```

Runtime decision:

```text
DEFERRED
```

L4 and higher remain future/not approved.

## Source-of-Truth Documents

Role-to-Agent Assignment depends on:

- `runtime-maturity-levels.md` for maturity boundaries.
- `manual-orchestration.md` for L3 manual flow and gates.
- `l3-role-assigned-parallel-runbook.md` for practical manual role-assigned parallel orchestration steps.
- `agent-work-package.md` for package structure and package states.
- `multi-agent-planning.md` for dependency-aware planning and candidate groups.
- `parallel-execution-policy.md` for candidate/approved parallel group boundaries.
- `agent-result-intake.md` for hardened Agent Result records.
- `integration-review.md` for combined result review.
- `roles.md` and `system-structure.md` for role boundaries.
- `prompt-lifecycle.md` and `codex-lifecycle.md` for bounded prompt and Codex execution boundaries.
- `security-policy.md` and `privacy-data-handling-policy.md` for safety constraints.

If this document conflicts with those documents, the stricter Human Owner approval and safety boundary wins until a later approved system change updates the source of truth.

## Assignment Entity

A Role-to-Agent Assignment is a manual record that maps one ready Agent Work Package to one logical agent or external agent session.

Required fields:

- `agent_id` - stable logical agent identifier.
- `role` - AI Development System role or external executor role.
- `assigned_awp_id` - assigned Agent Work Package.
- `allowed_awp_types` - package types this agent may receive.
- `allowed_operations` - operations the agent may perform.
- `forbidden_operations` - operations the agent must not perform.
- `required_inputs` - artifacts that must be provided to the agent.
- `required_outputs` - artifacts the agent must return.
- `result_intake_required` - whether hardened Agent Result Intake is required.
- `integration_review_required` - whether Integration Review is required.
- `parallel_eligible` - whether this assignment may be part of an approved parallel group.
- `human_owner_approval_required` - whether Human Owner approval is required before dispatch or acceptance.

Recommended fields:

- `assignment_id`;
- `parent_task`;
- `sop`;
- `candidate_group`;
- `approval_status`;
- `verification_mode`;
- `allowed_files`;
- `locked_files`;
- `dependencies`;
- `prompt_package_reference`;
- `result_reference`;
- `notes`.

## Default Logical Agents

| Agent ID | Role | Allowed AWP Types | Parallel Eligible |
| --- | --- | --- | --- |
| `product_owner_agent` | Product Owner AI | product vision, scope, value, success criteria | no by default |
| `business_analyst_agent` | Business Analyst AI | requirements, user stories, acceptance criteria | yes when dependencies allow |
| `system_architect_agent` | System Architect AI | architecture, interfaces, risks, technical decisions | yes when isolated from implementation dependencies |
| `backend_engineer_agent` | Backend Developer AI | backend implementation planning or approved backend execution packages | yes when dependencies and file locks allow |
| `frontend_engineer_agent` | Frontend Developer AI | frontend implementation planning or approved frontend execution packages | yes when dependencies and file locks allow |
| `devops_agent` | DevOps Engineer AI | environment, CI, deployment, operational tooling | yes only when infrastructure scope is isolated and approved |
| `qa_agent` | QA Engineer AI | QA planning, test design, verification, regression checks | no when QA depends on implementation outputs |
| `reviewer_agent` | Code Reviewer AI | code review, compliance review, integration review support | no when review depends on submitted results |
| `technical_writer_agent` | Technical Writer AI | README, changelog, onboarding and source-of-truth documentation | yes when documentation dependencies allow |
| `ai_system_maintainer_agent` | AI System Maintainer | controlled evolution of AI Development System documents and specs | no by default; parallel only with explicit Human Owner approval |

## Default Operation Boundaries

Allowed operations may include:

- inspect assigned source documents;
- inspect assigned files within `allowed_files`;
- prepare or execute the assigned bounded prompt manually when separately approved;
- produce a hardened Agent Result;
- report blockers, risks, questions and follow-ups;
- recommend review, QA or rework.

Forbidden operations always include:

- expanding parent task scope;
- accepting parent task results;
- bypassing Human Owner approval;
- executing a different Agent Work Package;
- modifying files outside `allowed_files`;
- ignoring `locked_files`;
- treating a candidate parallel group as execution approval;
- automatic Codex execution;
- automatic multi-agent execution;
- automatic branch/worktree lifecycle;
- automatic merge;
- automatic acceptance;
- automatic QA/review closure.

## Assignment Rules

An Agent Work Package may be assigned only when:

- dependency-aware planning reports the package as ready or the Human Owner explicitly records why a manual exception is safe;
- required dependencies are complete or otherwise satisfied;
- package status is compatible with manual assignment, such as `Ready` or `Approved`;
- `allowed_files` are explicit;
- `forbidden_actions` are explicit;
- required source documents and input artifacts are available;
- Human Owner approval is recorded when execution or parallel work is being approved.

Candidate parallel groups are informational until the Human Owner approves the group under `parallel-execution-policy.md`.

Each agent receives only its bounded prompt or package. The agent must not infer permission from the parent plan, adjacent packages or another agent assignment.

Each agent must return a hardened Agent Result according to `agent-result-intake.md`. A submitted result does not imply acceptance.

Integration Review is required when parallel results touch related behavior, interfaces, data contracts, file boundaries, user flows, security/privacy assumptions, deployment behavior or documentation consistency.

## Manual Multi-Thread Flow

```text
Plan prepared
-> plan validated
-> ready Agent Work Package candidates listed
-> Human Owner selects one AWP or approves a candidate group
-> AWP assigned to logical agents or external agent sessions
-> bounded prompt drafts prepared
-> agents run manually outside orchestration tooling
-> Agent Results collected
-> Agent Result Intake performed manually
-> Integration Review performed when required
-> Human Owner approves, rejects, defers or requests rework
-> AWP statuses updated manually
-> next ready group recomputed
```

Manual multi-threading means multiple bounded agent sessions may be run by the Human Owner or ChatGPT Orchestrator as separate manual work threads. It does not mean automatic dispatch or runtime scheduling.

## Assignment Record Template

```text
assignment_id:
agent_id:
role:
assigned_awp_id:
parent_task:
sop:
approval_status:
allowed_awp_types:
allowed_operations:
forbidden_operations:
required_inputs:
required_outputs:
result_intake_required:
integration_review_required:
parallel_eligible:
human_owner_approval_required:
allowed_files:
locked_files:
dependencies:
verification_mode:
prompt_package_reference:
result_reference:
notes:
```

## Review and Acceptance

Assignment review should check:

- the assigned agent role matches the AWP role and scope;
- dependencies are satisfied;
- `allowed_files`, `locked_files` and `forbidden_actions` are explicit;
- required inputs are present;
- result output requirements match the hardened Agent Result schema;
- Human Owner approval is recorded where required;
- no assignment implies automatic execution, merge or acceptance.

Agent Result Intake and Integration Review remain separate gates. Assignment approval does not accept an agent result and does not accept the parent task.

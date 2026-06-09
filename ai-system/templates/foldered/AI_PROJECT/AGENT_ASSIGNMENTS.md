# Agent Assignments — {{PROJECT_NAME}}

Status: Draft

## Purpose

This file records manual Role-to-Agent Assignments for L3 Manual Multi-Agent Orchestration.

Assignments map ready Agent Work Packages to logical agents or external agent sessions.

This file is a manual coordination record only.

It does not authorize automatic execution, automatic agent dispatch, automatic multi-agent execution, branch/worktree automation, automatic file modification by orchestration tooling, automatic merge, automatic acceptance or automatic QA/review closure.

Human Owner remains the final decision maker.

## Safety Boundaries

- Runtime remains deferred.
- L4 and higher remain future/not approved.
- Candidate parallel groups are informational until Human Owner approval.
- Each agent receives only its bounded package or prompt.
- Agent Results are required before intake, review or acceptance.
- Agent Result Intake and Integration Review remain manual gates.

## Assignment Registry

| Assignment ID | Agent ID | Role | Assigned AWP | Approval Status | Parallel Eligible | Result Intake Required | Integration Review Required |
|---|---|---|---|---|---|---|---|
| ASSIGN-001 | TBD | TBD | AWP-001 | not approved | no | yes | TBD |

## Default Logical Agents

| Agent ID | Role | Notes |
|---|---|---|
| product_owner_agent | Product Owner AI | Product value, scope and success criteria. |
| business_analyst_agent | Business Analyst AI | Requirements, user stories and acceptance criteria. |
| system_architect_agent | System Architect AI | Architecture, interfaces and technical risks. |
| backend_engineer_agent | Backend Developer AI | Backend implementation planning or approved backend execution packages. |
| frontend_engineer_agent | Frontend Developer AI | Frontend implementation planning or approved frontend execution packages. |
| devops_agent | DevOps Engineer AI | Environment, CI, deployment and operational tooling. |
| qa_agent | QA Engineer AI | QA planning, verification and regression checks. |
| reviewer_agent | Code Reviewer AI | Code review, compliance review and integration review support. |
| technical_writer_agent | Technical Writer AI | README, changelog and source-of-truth documentation. |
| ai_system_maintainer_agent | AI System Maintainer | Controlled evolution of AI Development System documents and specs. |

## Required Assignment Fields

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

## Manual Multi-Thread Flow

```text
Plan validated
-> ready Agent Work Package candidates listed
-> Human Owner selects one AWP or approves a candidate group
-> AWP assigned to logical agents or external sessions
-> bounded prompt drafts prepared
-> agents run manually outside orchestration tooling
-> Agent Results collected
-> Agent Result Intake performed manually
-> Integration Review performed when required
-> Human Owner approves, rejects, defers or requests rework
-> next ready group recomputed
```

## Open Questions / Blockers

- Define assignments only after Agent Work Packages are ready.
- Record Human Owner approval before treating any candidate group as approved for parallel manual work.

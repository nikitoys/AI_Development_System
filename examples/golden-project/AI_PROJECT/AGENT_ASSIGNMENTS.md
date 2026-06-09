# Agent Assignments — Task Tracker

Status: Draft

## Purpose

This file records a filled manual Role-to-Agent Assignment example for the golden Task Tracker project.

It is a coordination artifact only.

It does not authorize automatic execution, automatic agent dispatch, automatic multi-agent execution, branch/worktree automation, automatic file modification by orchestration tooling, automatic merge, automatic acceptance or automatic QA/review closure.

Human Owner remains the final decision maker.

## Assignment Registry

| Assignment ID | Agent ID | Role | Assigned AWP | Approval Status | Parallel Eligible | Result Intake Required | Integration Review Required |
|---|---|---|---|---|---|---|---|
| ASSIGN-REQ-001 | business_analyst_agent | Business Analyst AI | AWP-REQ-001 | not approved | no | yes | no |
| ASSIGN-BE-001 | backend_engineer_agent | Backend Developer AI | AWP-BE-001 | not approved | yes after AWP-REQ-001 | yes | yes |
| ASSIGN-FE-001 | frontend_engineer_agent | Frontend Developer AI | AWP-FE-001 | not approved | yes after AWP-REQ-001 | yes | yes |
| ASSIGN-QA-001 | qa_agent | QA Engineer AI | AWP-QA-001 | not approved | no | yes | yes |

## Assignment Details

## ASSIGN-REQ-001

```text
agent_id: business_analyst_agent
role: Business Analyst AI
assigned_awp_id: AWP-REQ-001
parent_task: T-003
sop: SOP-FEATURE-001
allowed_awp_types: requirements, acceptance criteria
allowed_operations: inspect owner plan, draft requirements, draft acceptance criteria
forbidden_operations: modify product code, approve execution, accept final result
required_inputs: AI_PROJECT/OWNER_PLAN.md, AI_PROJECT/PROJECT_GOAL.md
required_outputs: hardened Agent Result with requirements notes and acceptance criteria claims
result_intake_required: yes
integration_review_required: no
parallel_eligible: no
human_owner_approval_required: yes
dependencies: Human Owner scope confirmation
verification_mode: FAST_VALIDATION
```

## ASSIGN-BE-001

```text
agent_id: backend_engineer_agent
role: Backend Developer AI
assigned_awp_id: AWP-BE-001
parent_task: T-003
sop: SOP-FEATURE-001
allowed_awp_types: backend planning, approved backend execution package
allowed_operations: draft backend/API prompt boundaries, identify allowed files, report backend risks
forbidden_operations: execute Codex, modify app files, approve merge, accept final result
required_inputs: AWP-REQ-001 result, AI_PROJECT/CODEX_WORKFLOW.md
required_outputs: hardened Agent Result with backend boundary claims and verification notes
result_intake_required: yes
integration_review_required: yes
parallel_eligible: yes after AWP-REQ-001 is accepted
human_owner_approval_required: yes
dependencies: AWP-REQ-001
verification_mode: FAST_VALIDATION
```

## ASSIGN-FE-001

```text
agent_id: frontend_engineer_agent
role: Frontend Developer AI
assigned_awp_id: AWP-FE-001
parent_task: T-003
sop: SOP-FEATURE-001
allowed_awp_types: frontend planning, approved frontend execution package
allowed_operations: draft frontend/UX prompt boundaries, identify allowed files, report UX risks
forbidden_operations: execute Codex, modify app files, broad redesign, accept final result
required_inputs: AWP-REQ-001 result, AI_PROJECT/CODEX_WORKFLOW.md
required_outputs: hardened Agent Result with frontend boundary claims and verification notes
result_intake_required: yes
integration_review_required: yes
parallel_eligible: yes after AWP-REQ-001 is accepted
human_owner_approval_required: yes
dependencies: AWP-REQ-001
verification_mode: FAST_VALIDATION
```

## ASSIGN-QA-001

```text
agent_id: qa_agent
role: QA Engineer AI
assigned_awp_id: AWP-QA-001
parent_task: T-003
sop: SOP-FEATURE-001
allowed_awp_types: QA planning, integration review support
allowed_operations: draft QA checklist, draft regression focus, inspect submitted Agent Results
forbidden_operations: accept final result, skip Human Owner approval, close review findings automatically
required_inputs: AWP-REQ-001, AWP-BE-001, AWP-FE-001 results
required_outputs: hardened Agent Result with QA and integration review focus
result_intake_required: yes
integration_review_required: yes
parallel_eligible: no
human_owner_approval_required: yes
dependencies: AWP-REQ-001, AWP-BE-001, AWP-FE-001
verification_mode: FAST_VALIDATION
```

## Manual Parallel Note

After `AWP-REQ-001` is accepted, `AWP-BE-001` and `AWP-FE-001` may be assigned as an informational candidate parallel group.

The group is not executable until the Human Owner explicitly approves it under the Parallel Execution Policy.

`AWP-QA-001` remains blocked until backend and frontend results are submitted and intaken.

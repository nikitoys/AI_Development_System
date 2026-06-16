# L4 Role-Agent Runtime Architecture

Status: Review
Version: v0.1.0

## Purpose

This document defines the target architecture for L4 Role-Agent Runtime in AI_Development_System.

L4 Role-Agent Runtime is now an approved bounded implementation target.

This document does not implement L4. It defines the required architecture, control boundaries, agent mapping and execution flow for later bounded implementation tasks.

## Human Owner Decision

The Human Owner approved moving from:

```text
L4 is future/not approved
```

to:

```text
L4 Role-Agent Runtime is an approved bounded implementation target
```

This approval authorizes designing and later implementing L4 assisted role-agent execution where:

- Python acts as the strict API and control kernel;
- Controller Codex plans, routes, delegates and integrates;
- Codex role subagents become concrete execution agents for the existing role model;
- all state, validation, audit and lifecycle transitions remain controlled through Python CLI/API gateways;
- Human Owner remains final acceptance authority.

This approval does not authorize L5 controlled runtime, autonomous task discovery, unbounded queues, automatic merge, automatic push, automatic pull request creation, automatic task acceptance, automatic QA closure or automatic review closure.

## Runtime Maturity Position

Current implementation maturity:

```text
L3 - Manual multi-agent orchestration
```

Next approved implementation target:

```text
L4 - Role-Agent Runtime
```

L5 remains:

```text
Future / Not approved
```

L4 implementation must be decomposed into bounded Tasks. Each Task must preserve protected-file rules, source-of-truth documentation, project-control CLI/API gates, review/QA gates and Human Owner final acceptance.

## Core L4 Model

```text
Human Owner
-> ChatGPT Orchestrator
-> Python Control API
-> Controller Codex
-> Codex Role Subagents
-> Agent Result Intake
-> Review / QA
-> Human Owner Acceptance
```

Responsibilities:

- Python = strict API / control kernel.
- Controller Codex = planner, router, delegator and integrator.
- Codex role subagents = concrete executors of the existing AI roles.
- `AI_PROJECT` = state, audit and generated readable outputs.
- Human Owner = final acceptance authority.

## Architecture Components

## Human Owner

Human Owner approves direction, scope, residual risk and final task acceptance.

Human Owner approval is required for:

- system evolution Changes;
- bounded Tasks that implement L4 capabilities;
- any residual risk acceptance;
- final task acceptance;
- any future move toward L5.

## ChatGPT Orchestrator

ChatGPT Orchestrator routes Human Owner intent through the AI Development System, selects active roles and prepares or reviews bounded work.

ChatGPT Orchestrator does not bypass Project Control Gateway and does not approve final results for the Human Owner.

## Python Control API

Python Control API is the strict L4 control kernel.

The first conceptual entrypoint is:

```text
scripts/agentctl.py
```

This task does not implement `scripts/agentctl.py`.

## Controller Codex

Controller Codex is the coordinating Codex session.

Controller Codex plans, routes, delegates and integrates work only inside Python-approved boundaries.

## Codex Role Subagents

Codex role subagents are concrete executor sessions for existing AI roles.

A role subagent receives a bounded assignment, performs only that role-scoped work and returns a structured Agent Result.

Role subagents are not autonomous project owners and do not accept final results.

## Agent Result Intake

Agent Result Intake receives and checks role-subagent output before review, QA, integration review or Human Owner acceptance.

Intake must check:

- task/package identity;
- role eligibility;
- scope compliance;
- allowed-file compliance;
- forbidden-action compliance;
- verification evidence;
- blockers, risks and follow-ups.

## Review / QA

Review and QA gates remain mandatory where required by task scope, source-document changes, process changes, lifecycle changes or verification mode.

Review and QA recommendations do not replace Human Owner final acceptance.

## Role-To-Agent Mapping

L4 maps the existing role model to concrete role-agent IDs.

Product Layer:

- `product_owner_agent`
- `business_analyst_agent`

Design Layer:

- `system_architect_agent`
- `ux_ui_designer_agent`

Management Layer:

- `project_manager_agent`

Implementation Layer:

- `backend_engineer_agent`
- `frontend_engineer_agent`
- `devops_agent`

Quality Layer:

- `reviewer_agent`
- `qa_agent`

Documentation Layer:

- `technical_writer_agent`

System Evolution Layer:

- `ai_system_maintainer_agent`

Each role-agent ID inherits the responsibilities and limits of the corresponding role in `roles.md` and `system-structure.md`.

## L4 Execution Flow

1. Human Owner or ChatGPT Orchestrator selects or approves a bounded Task.
2. Controller Codex reads current state through Python CLI/API.
3. Controller Codex calls Python API to plan and route.
4. Python validates task status, allowed files, dependencies, role eligibility and protected-file boundaries.
5. Controller Codex delegates work to one or more Codex role subagents.
6. Subagents execute only their bounded role-scoped work.
7. Python records execution/result metadata and checks changed files against allowed files.
8. Controller Codex performs Agent Result Intake and Integration Review routing.
9. Review/QA gates run where required.
10. Human Owner makes final acceptance decision.

## Conceptual `agentctl.py` API Surface

Future L4 implementation may introduce:

```text
python scripts/agentctl.py status
python scripts/agentctl.py plan
python scripts/agentctl.py route
python scripts/agentctl.py build-prompt
python scripts/agentctl.py dispatch
python scripts/agentctl.py intake
python scripts/agentctl.py review-state
python scripts/agentctl.py clear
```

These commands are conceptual in this document.

No command exists until a later approved Task implements it.

## Python Control Permissions

In L4, Python may control:

- read controlled state;
- validate task and Agent Work Package readiness;
- validate role-agent eligibility;
- generate compact prompts;
- launch approved Codex worker/subagent execution through a configured runner;
- capture stdout, stderr, exit code and result metadata;
- inspect changed files;
- detect allowed-files and protected-files violations;
- write controlled execution/result records;
- recommend next state for review.

## Python Prohibitions

In L4, Python must not:

- autonomously discover tasks;
- run unbounded queues;
- accept task results;
- close QA;
- close review;
- merge;
- push;
- open pull requests;
- make product, security or architecture decisions;
- silently expand scope;
- bypass Human Owner approval.

## Controller Codex Permissions

In L4, Controller Codex may:

- plan;
- route work;
- choose role-agents within Python-approved boundaries;
- delegate to Codex subagents;
- integrate returned results;
- request review/QA;
- call Python APIs for state and validation.

## Controller Codex Prohibitions

In L4, Controller Codex must not:

- manually edit protected `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**` files;
- bypass Python control APIs;
- approve its own result as final;
- treat subagent completion as Human Owner acceptance;
- dispatch agents outside approved scope.

## Codex Role Subagent Permissions

Codex role subagents may:

- read only assigned minimal context;
- edit only assigned allowed files;
- perform one bounded role-scoped task;
- report changed files, checks, blockers, risks and follow-ups;
- return a structured Agent Result.

## Codex Role Subagent Prohibitions

Codex role subagents must not:

- change protected `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**` files manually;
- execute another agent's package;
- expand scope;
- commit;
- push;
- merge;
- open pull requests;
- accept results;
- close QA/review;
- change runtime maturity.

## L3 / L4 / L5 Distinction

| Level | Execution model | Control boundary | Approval boundary |
| --- | --- | --- | --- |
| L3 | Manual handoff, manual worker launch and manual result return. | Humans and Controller Codex coordinate manually through existing docs and CLIs. | Human Owner acceptance remains required. |
| L4 | Python-assisted dispatch/execution; Controller Codex delegates to real Codex role subagents; Python validates, records and checks boundaries. | Python Control API owns state, validation, audit and result metadata. | Human Owner acceptance remains required. |
| L5 | Future controlled runtime with stronger runtime orchestration. | Not approved. | Not approved. |

L4 is not L5.

L4 does not authorize autonomous queues, autonomous scheduling, automatic merge, automatic push, automatic pull request creation, automatic task acceptance, automatic QA closure or automatic review closure.

## Minimal Example Flow

Example:

1. `TASK-007` requires a documentation update.
2. Controller Codex calls `python scripts/agentctl.py route --task TASK-007`.
3. Python recommends `technical_writer_agent`.
4. Controller Codex calls `python scripts/agentctl.py dispatch --task TASK-007 --agent technical_writer_agent --execute`.
5. `technical_writer_agent` edits only allowed docs.
6. Python detects changed files.
7. Controller Codex performs intake.
8. `reviewer_agent` or `qa_agent` may be called if needed.
9. Human Owner accepts or requests rework.

This is an L4 target example. It is not executable until `scripts/agentctl.py` and the related runner/control records are implemented through later approved Tasks.

## Implementation Requirements For Future Tasks

Every L4 implementation task must:

- reference this document;
- name the active role and approved Task;
- define allowed files and forbidden actions;
- preserve Python as the control kernel;
- preserve protected-file rules;
- include validation and review instructions;
- leave final acceptance to the Human Owner.

Future tasks must not implement L5 behavior by implication.

## Related Documents

- `runtime-maturity-levels.md`
- `manual-orchestration.md`
- `agent-delegation.md`
- `agent-work-package.md`
- `agent-result-intake.md`
- `integration-review.md`
- `role-agent-assignment.md`
- `task-format.md`
- `review-process.md`
- `roles.md`
- `system-structure.md`
- `project-control/01-overview.md`
- `project-control/04-command-catalog.md`
- `evolution/roadmap.md`
- `evolution/evolution-backlog.md`
- `system-changelog.md`

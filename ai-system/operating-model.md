# AI Development Operating Model

Status: Draft  
Version: v0.1.0

## Purpose

This document describes the layered operating model of the AI Development System.

It shows which parts are already implemented as documentation, which parts are missing, and which parts require further work.

## Status Legend

```text
Implemented           documented and usable as a system rule/process
Partially Implemented documented indirectly or incompletely
Missing               not yet documented as a separate mechanism
Needs Improvement     exists, but should be expanded or connected better
```

---

# 1. Foundation Layer

The Foundation Layer defines the basic structure, language and interaction boundaries of the AI Development System.

## 1.1 Interaction Modes

Status: Implemented

Existing documents:

```text
/ai-system/interaction-modes.md
/ai-system/owner-guide.md
```

Covers:

- Free Mode;
- System Mode;
- Codex Mode;
- Review Mode;
- Evolution Mode;
- Dry Run Mode;
- automatic mode detection;
- explicit request markers.

Needs improvement:

- add examples for mixed-mode requests;
- add short command examples to Owner Guide if needed.

## 1.2 System Structure

Status: Implemented

Existing documents:

```text
/ai-system/system-structure.md
/ai-system/README.md
```

Covers:

- Human Owner;
- ChatGPT Orchestrator;
- Codex Executor;
- role hierarchy;
- system layers;
- main operating loop.

Needs improvement:

- keep synchronized with role changes;
- update when roles are added, merged or removed.

## 1.3 Glossary

Status: Implemented

Existing documents:

```text
/ai-system/glossary.md
/ai-system/glossary-core.md
/ai-system/glossary-project.md
/ai-system/glossary-execution.md
/ai-system/glossary-evolution.md
```

Covers:

- core terms;
- project terms;
- execution terms;
- evolution terms;
- lifecycle term navigation and source document references.

Needs improvement:

- add new terms whenever new lifecycle documents are created;
- keep lifecycle term definitions synchronized with lifecycle documents.

## 1.4 Language and Localization

Status: Implemented

Existing documents:

```text
/ai-system/language-policy.md
/ai-system/aicp-language-policy.md
```

Covers:

- default Human Owner-facing response language;
- stable system and repository documentation language;
- prompt package language rules;
- fixed mode markers, decision keywords and control fields;
- localization boundary rules.

Needs improvement:

- add examples if multilingual prompt packages become difficult to review;
- revisit when project documents in `/docs` define their own localization needs.

---

# 2. Governance Layer

The Governance Layer defines how decisions, changes and lifecycle control are managed.

## 2.1 Decision Lifecycle

Status: Implemented

Existing documents:

```text
/ai-system/decision-process.md
/ai-system/decision-lifecycle.md
/ai-system/owner-guide.md
```

Covers:

- managed decision definition;
- decision lifecycle states and operations;
- ownership model;
- relationship between decisions, affected documents, AICP, changelog and git history;
- Human Owner approval rules;
- AICP relationship;
- revision, supersession, archival, version impact and audit rules.

Needs improvement:

- add examples for product, architecture and system evolution decisions when decision records become frequent;
- add decision state transition diagram if decision tracking becomes difficult.

## 2.2 Change Lifecycle

Status: Implemented

Existing documents:

```text
/ai-system/change-process.md
/ai-system/change-lifecycle.md
/ai-system/improvement-log.md
/ai-system/system-changelog.md
```

Covers:

- managed system change definition;
- change lifecycle states and operations;
- relationship between improvement log, AICP, system changelog and git history;
- verification, rollback and closure rules;
- Human Owner approval rules;
- AICP relationship;
- version impact and audit rules.

Needs improvement:

- add examples for common change types if review friction appears;
- add change state transition diagram if change tracking becomes difficult.

## 2.3 Lifecycle Governance

Status: Implemented

Existing documents:

```text
/ai-system/lifecycle-governance.md
```

Covers:

- common governance model for managed entities;
- common lifecycle states, operations, ownership and approval rules;
- AICP relationship;
- version impact, audit and history rules;
- rules for future lifecycle documents.

Needs improvement:

- keep synchronized with future lifecycle documents;
- add examples if repeated lifecycle design mistakes appear.

## 2.4 System Evolution Governance

Status: Implemented

Existing documents:

```text
/ai-system/evolution/README.md
/ai-system/evolution/roadmap.md
/ai-system/evolution/evolution-loop.md
/ai-system/evolution/evolution-policy.md
/ai-system/evolution/owner-evolution-plan.md
/ai-system/evolution/owner-plan-intake.md
/ai-system/evolution/system-health-check.md
/ai-system/evolution/evolution-backlog.md
/ai-system/evolution/analysis-report-baseline.md
```

Covers:

- roadmap-driven evolution of AI_Development_System itself;
- controlled observe → diagnose → propose → plan → execute → verify → review → approve → release → learn loop;
- self-evolution permissions and anti-runaway rules;
- owner-authored evolution plan recording and intake mapping;
- Human Owner approval boundary for system changes;
- health-check dimensions for system maturity;
- evolution backlog format and initial backlog items;
- preservation of analytical report findings as a roadmap baseline;
- relationship between owner plans, roadmap items, backlog items, AICP, bounded Codex execution, review, approval and changelog.

Needs improvement:

- connect future machine-checkable specs to the evolution module;
- add health-check reports during pilot validation;
- add examples of completed evolution cycles after first real use.

## 2.5 SOP Model

Status: Implemented

Existing documents:

```text
/ai-system/sop-model.md
/ai-system/evolution/sop-multi-agent-implementation-plan.md
```

Covers:

- managed SOP definition;
- required SOP fields;
- SOP selection and relationship to the existing workflow;
- role, task, prompt, Codex, review and QA lifecycle relationships;
- sequential execution as the default rule;
- boundary rule that SOPs do not authorize automatic execution or automatic acceptance;
- initial Feature Delivery, Bugfix / Rework and AI System Evolution SOPs.

Needs improvement:

- add Agent Work Package standard in a separate bounded evolution task;
- add multi-agent planning and parallel execution policy only after approval;
- add machine-checkable SOP specs after the Markdown source documents exist.

## 2.6 Agent Work Package Standard

Status: Implemented

Existing documents:

```text
/ai-system/agent-work-package.md
/ai-system/sop-model.md
/ai-system/evolution/sop-multi-agent-implementation-plan.md
```

Covers:

- managed Agent Work Package definition;
- relationship between parent tasks and child Agent Work Packages;
- required fields including `allowed_files`, `locked_files`, `dependencies`, verification mode and review instructions;
- package lifecycle/status values;
- ownership model and role boundary rules;
- relationship to SOP Model, task lifecycle, prompt lifecycle, Codex lifecycle, review and QA;
- default rule that Agent Work Packages do not imply parallel execution;
- boundary rule that Agent Work Packages do not authorize automatic execution or automatic acceptance.

Needs improvement:

- add Multi-Agent Planning workflow in a separate bounded evolution task;
- add Parallel Execution Policy only after approval;
- add machine-checkable Agent Work Package specs after the Markdown source documents exist.

## 2.7 Multi-Agent Planning Workflow

Status: Implemented

Existing documents:

```text
/ai-system/multi-agent-planning.md
/ai-system/agent-work-package.md
/ai-system/sop-model.md
/ai-system/evolution/sop-multi-agent-implementation-plan.md
```

Covers:

- managed multi-agent plan definition;
- planning inputs and outputs;
- planning states/status values;
- decomposition rules for parent tasks into Agent Work Packages;
- dependency, file-scope and locked-file planning rules;
- candidate parallel groups as informational planning output only;
- Human Owner approval points;
- path from plan to one next bounded executable work item through existing task, prompt and Codex lifecycles;
- boundary rule that planning does not authorize execution, parallel execution, automatic execution or automatic acceptance.

Needs improvement:

- add Parallel Execution Policy in a separate bounded evolution task;
- add Agent Result Intake and Integration Review after planning and execution boundaries are approved;
- add machine-checkable planning specs after Markdown source documents exist.

## 2.8 Parallel Execution Policy

Status: Implemented

Existing documents:

```text
/ai-system/parallel-execution-policy.md
/ai-system/multi-agent-planning.md
/ai-system/agent-work-package.md
/ai-system/sop-model.md
/ai-system/evolution/sop-multi-agent-implementation-plan.md
```

Covers:

- managed parallel execution group definition;
- sequential execution as the default rule;
- opt-in Human Owner approval requirement for every parallel group;
- parallel eligibility and rejection criteria;
- dependency, `allowed_files` and `locked_files` conflict rules;
- file-lock ownership rules;
- approval gates;
- mandatory integration review before parent task acceptance;
- QA requirement or documented QA decision before final acceptance;
- rollback, rework, result intake, security/privacy and learning-output expectations;
- boundary rule that parallel execution does not authorize automatic execution, automatic merge or automatic acceptance.

Needs improvement:

- add Agent Result Intake and Integration Review in a separate bounded evolution task;
- add machine-checkable parallel policy specs after Markdown source documents exist;
- validate the policy through controlled pilot work before any runtime decision.

## 2.9 Agent Result Intake and Integration Review

Status: Implemented

Existing documents:

```text
/ai-system/agent-result-intake.md
/ai-system/integration-review.md
/ai-system/parallel-execution-policy.md
/ai-system/multi-agent-planning.md
/ai-system/agent-work-package.md
```

Covers:

- agent result governed entity and required result fields;
- hardened Agent Result schema with structured changed files, claims, verification, risks, blockers, followups, scope compliance, safety boundary compliance and review requirements;
- result intake states/status values;
- intake checks for scope, `allowed_files`, `locked_files`, `forbidden_actions`, dependencies and verification mode;
- error, question, blocker, rework, rejection and archive routing;
- integrated agent result set governed entity;
- integration review states/status values;
- cross-agent consistency, behavior/contract, architecture, API/UX/data, duplicate/conflict, regression, documentation and security/privacy checks;
- QA handoff relationship;
- boundary rules that intake and integration review do not authorize automatic execution, automatic merge or automatic acceptance and do not replace Human Owner final acceptance.

Needs improvement:

- validate hardened Agent Result records through manual orchestration pilots;
- validate intake and integration review through controlled pilot work.

## 2.10 Machine-Checkable SOP and Agent Specs

Status: Implemented

Existing documents:

```text
/spec/sops.json
/spec/agent-work-package.schema.json
/spec/agent-result.schema.json
/spec/parallel-policy.json
/spec/README.md
```

Covers:

- initial SOP inventory derived from `sop-model.md`;
- JSON Schema contract for Agent Work Packages derived from `agent-work-package.md`;
- JSON Schema contract for Agent Results derived from `agent-result-intake.md`;
- policy inventory for core parallel execution constraints derived from `parallel-execution-policy.md`;
- source-of-truth rule that Markdown remains operational authority;
- boundary rule that specs do not generate Markdown, implement runtime behavior or authorize automatic execution, merge or acceptance.

Needs improvement:

- add schema validation CI in a separate bounded evolution task if justified;
- add project-local templates after approved specs and planning documents stabilize;
- validate specs through controlled pilot work before runtime decisions.

## 2.11 Self-Hosted Project Control Layer and Agent Planning Templates

Status: Implemented

Existing documents:

```text
/ai-system/project-control/01-overview.md
/ai-system/project-control/02-domain-model.md
/ai-system/project-control/03-state-model.md
/ai-system/project-control/04-command-catalog.md
/ai-system/project-control/08-usage-guide.md
/ai-system/project-control-connectivity.md
/ai-system/project-operation-profile.md
/ai-system/templates/foldered/AI_PROJECT/PROJECT_CONTROL_INDEX.md
/ai-system/templates/foldered/AI_PROJECT/PROJECT_OPERATION_PROFILE.md
/ai-system/templates/foldered/AI_PROJECT/AGENT_PLAN.md
/ai-system/templates/foldered/AI_PROJECT/AGENT_TASKS.md
/ai-system/templates/foldered/AI_PROJECT/AGENT_ASSIGNMENTS.md
/ai-system/templates/foldered/AI_PROJECT/AGENT_LOCKS.md
/ai-system/templates/foldered/AI_PROJECT/AGENT_RESULTS.md
/ai-system/templates/foldered/AI_PROJECT/AGENT_METRICS.md
```

Covers:

- root `/AI_PROJECT` as the self-hosted Project Control Layer for AI_Development_System itself;
- strict separation between `/ai-system` source documents and `/AI_PROJECT` controlled state, audit events and generated readable outputs;
- protected-file rules for `/AI_PROJECT/state/**`, `/AI_PROJECT/events/**` and `/AI_PROJECT/generated/**`;
- Project Control Gateway dogfooding through `planctl.py`, `taskctl.py`, `docctl.py` and `evolutionctl.py`;
- compact project-control read order with importance levels and read policies;
- drift reporting when root or local read order does not lead agents to standard control files;
- Human Owner-editable surface-level operating defaults for language, answer style, verification, permissions, layout and review;
- project-local SOP and agent planning snapshot;
- explicit distinction between root `/AI_PROJECT`, reusable `AI_PROJECT` templates and `examples/golden-project/AI_PROJECT`;
- Agent Work Package registry;
- manual Role-to-Agent Assignment registry;
- file-scope and locked-file planning registry;
- Agent Result intake and integration review references;
- planning, execution, review and QA metrics for pilot validation;
- safety boundaries that preserve sequential execution as the default and forbid automatic execution, merge or acceptance.

Needs improvement:

- add machine-readable connectivity validation only after the Markdown index proves stable;
- add machine-readable profile schema only after the Markdown profile proves stable;
- extend the golden project with a non-runtime multi-agent example;
- add dry-run planner validation tooling only in a separate bounded evolution task;
- validate template usefulness through controlled pilot work.

## 2.12 Dry-Run Agent Planner MVP

Status: Implemented

Existing documents:

```text
/scripts/agent-plan-mvp.py
/ai-system/templates/foldered/AI_PROJECT/AGENT_PLAN.md
/ai-system/templates/foldered/AI_PROJECT/AGENT_TASKS.md
/ai-system/templates/foldered/AI_PROJECT/AGENT_ASSIGNMENTS.md
/ai-system/templates/foldered/AI_PROJECT/AGENT_LOCKS.md
/ai-system/templates/foldered/AI_PROJECT/AGENT_RESULTS.md
/ai-system/templates/foldered/AI_PROJECT/AGENT_METRICS.md
```

Covers:

- dry-run validation of project-local agent planning files;
- missing `AI_PROJECT/AGENT_*` file reporting;
- simple Agent Work Package table recognition;
- locked-file conflict reporting when lock data is available;
- candidate parallel group reporting as informational only;
- bounded prompt draft generation for review when enough package data exists;
- boundary rule that the helper does not execute Codex, create branches or worktrees, merge changes, modify application code or accept results.

Needs improvement:

- extend the golden project with a non-runtime multi-agent example;
- add richer parsing only after pilot evidence shows it is useful;
- keep runtime decisions deferred until controlled pilot validation.

## 2.13 Runtime Maturity Levels

Status: Implemented

Existing documents:

```text
/ai-system/runtime-maturity-levels.md
/ai-system/evolution/roadmap.md
/ai-system/evolution/evolution-backlog.md
```

Covers:

- maturity levels `L0` through `L6`;
- current level `L3 — Manual multi-agent orchestration`;
- next possible target `L4 — Assisted execution`, future/not approved;
- L4+ as future/not approved;
- allowed and forbidden capabilities at each level;
- required safety gates, evidence and readiness criteria;
- boundary rule that maturity levels do not authorize runtime behavior by themselves.

Needs improvement:

- keep runtime execution deferred until explicit future approval;
- do not propose L4 assisted execution without a separate Human Owner-approved evolution task.

## 2.14 Manual Multi-Agent Orchestration Mode

Status: Implemented

Existing documents:

```text
/ai-system/manual-orchestration.md
/ai-system/l3-role-assigned-parallel-runbook.md
/ai-system/runtime-maturity-levels.md
/ai-system/agent-work-package.md
/ai-system/agent-result-intake.md
/ai-system/integration-review.md
```

Covers:

- L3 manual-only orchestration purpose and boundaries;
- allowed manual operations for plan selection, validation, AWP selection, manual assignment, result intake and integration review;
- practical role-assigned parallel runbook for Human Owner / ChatGPT Orchestrator use;
- forbidden automatic execution, branch/worktree automation, merge, acceptance and QA/review closure;
- required L3 artifacts;
- manual orchestration flow;
- L3 readiness criteria and L4 readiness criteria;
- boundary rule that L3 is coordination, not runtime.

Needs improvement:

- continue collecting repeatable L3 manual orchestration evidence;
- use hardened Agent Result records during future manual orchestration pilots.

## 2.15 Two-Level Delegated Agent Execution

Status: Implemented

Existing documents:

```text
/ai-system/agent-delegation.md
/ai-system/templates/agent-worker-prompt.md
/.agents/skills/agent-delegation/SKILL.md
/ai-system/manual-orchestration.md
/ai-system/agent-work-package.md
/ai-system/agent-result-intake.md
/ai-system/integration-review.md
/ai-system/runtime-maturity-levels.md
```

Covers:

- Controller Codex preparation of precise Worker Agent Prompt Packages;
- Human Owner or operator manual Worker Agent launch;
- Worker Agent execution of one bounded task or Agent Work Package;
- structured Worker Agent Result return;
- Controller Codex result intake, review routing and CLI-controlled state updates;
- relationship to Documentation Navigation Skill for minimal read sets;
- explicit L3 manual-only boundary.

Needs improvement:

- validate Worker Agent prompt quality during future manual orchestration pilots;
- add machine-checkable handoff metadata only after repeated manual evidence shows it is useful.

## 2.16 Work Item Hierarchy

Status: Implemented

Existing documents:

```text
/ai-system/work-item-hierarchy.md
/ai-system/task-format.md
/ai-system/task-lifecycle.md
/ai-system/agent-work-package.md
```

Covers:

- Goal, Initiative, Epic, Task and Agent Work Package relationship;
- Initiative and Epic as planning containers only;
- Task as the executable unit;
- Agent Work Package as a child planning unit under Task;
- optional Initiative and Epic task fields;
- `CODEX_PLAN.md` and `CODEX_TASKS.md` planning hierarchy usage;
- boundary rule that the hierarchy does not authorize runtime behavior, automatic execution, new lifecycle states or new parallel execution behavior.

Needs improvement:

- validate hierarchy usefulness during future concrete project planning;
- add machine-checkable hierarchy metadata only if repeated manual drift appears.

---

# 3. Entity Lifecycle Layer

The Entity Lifecycle Layer defines how managed system entities are created, read, updated, deprecated and removed.

## 3.1 Role Lifecycle

Status: Implemented

Existing document:

```text
/ai-system/role-lifecycle.md
```

Covers:

- role lifecycle operations;
- role change proposal template;
- role version impact rules.

Needs improvement:

- add role state diagram;
- define active/inactive/deprecated role registry format;
- add examples for merging and splitting roles.

## 3.2 Document Lifecycle

Status: Implemented

Existing document:

```text
/ai-system/document-lifecycle.md
```

Covers:

- managed document definition;
- source-of-truth locations;
- document lifecycle states and operations;
- document ownership model;
- Human Owner approval rules;
- AICP relationship;
- version impact, audit, history, index and reference update rules.

Needs improvement:

- add examples for product documents in `/docs` when a product project exists;
- add document state transition diagram if review friction appears.

## 3.3 Process Lifecycle

Status: Implemented

Existing document:

```text
/ai-system/process-lifecycle.md
```

Covers:

- managed process definition;
- process source-of-truth locations;
- process lifecycle states and operations;
- process ownership model;
- Human Owner approval rules;
- AICP relationship;
- version impact, audit and history rules;
- relationship to lifecycle governance and document lifecycle.

Needs improvement:

- add examples for splitting and merging processes if process overlap appears;
- add process state transition diagram if process review becomes difficult.

## 3.4 Task Lifecycle

Status: Implemented

Existing documents:

```text
/ai-system/task-format.md
/ai-system/task-lifecycle.md
```

Covers:

- managed task definition;
- task lifecycle states and operations;
- task ownership model;
- Definition of Ready and Definition of Done relationship;
- relationship between task lifecycle, execution and review;
- Human Owner approval rules;
- AICP relationship;
- version impact, audit and history rules.

Needs improvement:

- add task state transition diagram if task tracking becomes difficult;
- add examples for product backlog tasks when a product project exists.

---

# 4. Execution Layer

The Execution Layer defines how work is executed, reviewed and validated.

## 4.1 Codex Execution Lifecycle

Status: Implemented

Existing document:

```text
/ai-system/codex-lifecycle.md
```

Covers:

- Codex execution definition;
- source-of-truth documents for execution;
- execution lifecycle states and operations;
- ownership model;
- prompt package requirements;
- result intake and required report format;
- failure handling, rework prompt flow and rollback handling;
- relationships to task format, prompt lifecycle, review process, lifecycle governance, document lifecycle and process lifecycle.

Needs improvement:

- add examples for common failure cases if execution reviews repeat the same issues;
- add execution state transition diagram if execution tracking becomes difficult.

## 4.2 Review Lifecycle

Status: Implemented

Existing documents:

```text
/ai-system/review-process.md
/ai-system/review-lifecycle.md
```

Covers:

- managed review definition;
- review lifecycle states and operations;
- reviewer ownership model;
- relationship to review types and severity levels;
- re-review process;
- review closure rules;
- relationship to task lifecycle, execution lifecycle and QA lifecycle;
- Human Owner approval rules;
- AICP relationship;
- version impact, audit, history and boundary rules.

Needs improvement:

- add review state transition diagram if review tracking becomes difficult;
- add examples for multi-review tasks when pilot or production usage increases.

## 4.3 QA Lifecycle

Status: Implemented

Existing document:

```text
/ai-system/qa-lifecycle.md
```

Covers:

- managed QA flow definition;
- QA lifecycle states and operations;
- QA ownership model;
- positive, negative, edge case and regression checks;
- QA approval requirements;
- defect reporting and rework flow;
- relationship to task lifecycle, Codex lifecycle and review process;
- Human Owner approval rules;
- AICP relationship;
- version impact, audit and history rules.

Needs improvement:

- add examples for product-specific QA flows when product projects exist;
- add QA state transition diagram if QA tracking becomes difficult.

## 4.4 Verification Cost and Runtime Tracking

Status: Implemented

Existing documents and artifacts:

```text
/ai-system/verification-modes.md
/ai-system/verification-cost-model.md
/ai-system/test-runtime-tracking.md
/ai-system/spec/verification-checks.json
/scripts/verification/run_checks.py
```

Covers:

- explicit verification budgets for `NONE`, `SMOKE`, `FAST`, `STANDARD`, `FULL`, `RELEASE` and `MANUAL`;
- speed classes, value classes, result types and blocking/advisory impact;
- rule that Codex Executor must not silently upgrade verification mode;
- rule that slow/full/release checks are not default;
- runtime history fields for executed and skipped checks;
- local-only runtime history boundaries;
- dry-run-capable lightweight check selection and JSONL recording.

Needs improvement:

- implement standalone commands for registry checks only after bounded follow-up tasks;
- add aggregate runtime warning reports after real local history exists;
- keep slow/golden checks opt-in until release workflows justify them.

---

# 5. Learning Layer

The Learning Layer defines how the system learns, improves and experiments.

## 5.1 Improvement Lifecycle

Status: Implemented

Existing documents:

```text
/ai-system/improvement-log.md
/ai-system/improvement-lifecycle.md
```

Covers:

- managed improvement definition;
- what counts as an improvement and what does not;
- improvement source-of-truth documents;
- improvement lifecycle states;
- Observe Improvement, Log Improvement, Triage Improvement, Analyze Root Cause, Classify Improvement, Accept Improvement, Defer Improvement, Reject Improvement, Convert to AICP, Convert to Knowledge, Convert to Experiment, Apply Improvement, Verify Improvement, Close Improvement and Archive Improvement operations;
- ownership model across Human Owner, ChatGPT Orchestrator, AI System Maintainer, Technical Writer AI, Code Reviewer AI, QA Engineer AI, domain roles and Codex Executor;
- observation capture and triage rules;
- severity or priority classification;
- recurring issue detection rules;
- root cause analysis rules;
- conversion criteria for AICP, knowledge and experiment paths;
- rejection, deferral and closure criteria;
- relationship to improvement log, change lifecycle, knowledge lifecycle, experiment lifecycle, review lifecycle and lifecycle governance;
- Human Owner approval rules;
- AICP relationship;
- version impact rules;
- audit and history rules;
- boundary rules.

Needs improvement:

- add examples for common improvement conversion paths during pilot validation;
- add improvement state transition diagram if improvement tracking becomes difficult.

## 5.2 Knowledge Lifecycle

Status: Implemented

Existing document:

```text
/ai-system/knowledge-lifecycle.md
```

Covers:

- managed knowledge item definition;
- knowledge source-of-truth documents;
- knowledge lifecycle states and operations;
- ownership, capture, validation and promotion rules;
- relationship to glossary, rules, prompts, improvement lifecycle, change lifecycle and review lifecycle;
- stale knowledge, deprecation, removal and lesson storage rules;
- Human Owner approval rules;
- AICP relationship;
- version impact, audit, history and boundary rules.

Needs improvement:

- add examples for knowledge promotion paths when repeated observations become frequent;
- add knowledge state transition diagram if knowledge tracking becomes difficult.

## 5.3 Experiment Lifecycle

Status: Implemented

Existing document:

```text
/ai-system/experiment-lifecycle.md
```

Covers:

- managed experiment definition;
- experiment source-of-truth documents;
- experiment lifecycle states and operations;
- ownership model;
- experiment proposal format;
- hypothesis, scope, duration, success criteria and failure criteria rules;
- evaluation, adoption, rejection and rollback processes;
- relationship to decision lifecycle, change lifecycle, knowledge lifecycle, improvement lifecycle and review lifecycle;
- Human Owner approval rules;
- AICP relationship;
- version impact, audit, history and boundary rules.

Needs improvement:

- add examples for experiment proposal and evaluation records when experiments become frequent;
- add experiment state transition diagram if experiment tracking becomes difficult.

---

# Summary

## Implemented

```text
Interaction Modes
System Structure
Glossary
Change Lifecycle
Decision Lifecycle
Role Lifecycle
Document Lifecycle
Process Lifecycle
Task Lifecycle
Codex Execution Lifecycle
Review Lifecycle
QA Lifecycle
Verification Cost and Runtime Tracking
Project Operation Profile
Knowledge Lifecycle
Experiment Lifecycle
Improvement Lifecycle
Lifecycle Governance
Language and Localization
System Evolution Governance
Two-Level Delegated Agent Execution
Work Item Hierarchy
```

## Partially Implemented

```text
```

## Missing

```text
```

## Highest Priority Next Steps

1. Run the first system health check and record findings in the evolution backlog.
2. Synchronize visible system versions and document statuses across primary entrypoints.
3. Add documentation integrity checks for links, placeholders, indexes and status/version fields.
4. Add security, privacy and data-handling policy.
5. Run pilot validation against real repository tasks and record follow-up improvements.

## Main Principle

```text
Every managed entity in the AI Development System should have:
- owner;
- source document;
- lifecycle states;
- allowed operations;
- approval rules;
- version impact rules;
- changelog or history rule.

Every system evolution item should also have:
- roadmap, backlog, health-check, analytical report or Human Owner source;
- explicit allowed files;
- verification mode;
- review requirement;
- Human Owner approval requirement assessment;
- closure outcome.
```

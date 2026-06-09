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
Knowledge Lifecycle
Experiment Lifecycle
Improvement Lifecycle
Lifecycle Governance
Language and Localization
System Evolution Governance
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

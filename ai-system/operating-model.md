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
- evolution terms.

Needs improvement:

- add new terms whenever new lifecycle documents are created;
- add cross-links between terms and lifecycle documents.

---

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
- decision source-of-truth locations;
- decision lifecycle states;
- Read, Propose, Clarify, Review, Approve, Request Rework, Reject, Defer, Start Experiment, Apply, Supersede, Roll Back and Archive operations;
- ownership model across Human Owner, ChatGPT Orchestrator, AI System Maintainer, domain roles and Codex Executor;
- relationship to decision process;
- relationship between decisions, affected documents, AICP, changelog and git history;
- Human Owner approval rules;
- AICP relationship;
- revision, supersession and archival rules;
- version impact rules;
- audit and history rules.

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
- change lifecycle states;
- Observe, Analyze, Draft AICP, Review, Approve, Defer, Reject, Apply, Verify, Request Rework, Roll Back, Close and Archive operations;
- relationship between improvement log, AICP, system changelog and git history;
- verification criteria after applying a system change;
- rollback rules;
- closure criteria;
- Human Owner approval rules;
- AICP relationship;
- version impact rules;
- audit and history rules.

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
- common lifecycle states;
- common lifecycle operations;
- common ownership model;
- common approval rules;
- AICP relationship;
- version impact rules;
- audit and history rules;
- rules for future lifecycle documents.

Needs improvement:

- keep synchronized with future lifecycle documents;
- add examples if repeated lifecycle design mistakes appear.

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

- Read Role;
- Add Role;
- Edit Role;
- Split Role;
- Merge Roles;
- Deprecate Role;
- Delete Role;
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
- document lifecycle states;
- Read, Create, Update, Review, Approve, Reject, Deprecate, Archive, Remove and Roll Back operations;
- document ownership model;
- Human Owner approval rules;
- AICP relationship;
- version impact rules;
- audit and history rules;
- index and reference update rules.

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
- process lifecycle states;
- Read, Create, Update, Review, Approve, Reject, Split, Merge, Deprecate, Archive, Remove, Roll Back and Audit operations;
- process ownership model;
- Human Owner approval rules;
- AICP relationship;
- version impact rules;
- audit and history rules;
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
- task source-of-truth locations;
- task lifecycle states;
- Read, Create, Refine, Approve, Start, Block, Resume, Submit for Review, Request Rework, Accept, Reject, Defer, Archive and Reopen operations;
- task ownership model;
- Definition of Ready and Definition of Done relationship to `/ai-system/task-format.md`;
- relationship between task lifecycle, Codex execution and review;
- Human Owner approval rules;
- AICP relationship;
- version impact rules;
- audit and history rules;
- relationship to lifecycle governance, document lifecycle and process lifecycle.

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
- source-of-truth documents for Codex execution;
- Codex execution lifecycle states;
- Prepare Prompt, Review Prompt, Approve Prompt, Execute, Report Result, Intake Result, Review Result, Request Rework, Accept Result, Reject Result, Roll Back and Archive operations;
- ownership model across Human Owner, ChatGPT Orchestrator, Codex Executor, domain roles, Code Reviewer AI, QA Engineer AI and AI System Maintainer;
- prompt package requirements;
- result intake and required report format;
- failure handling;
- rework prompt flow;
- rollback handling;
- relationships to task format, prompt lifecycle, review process, lifecycle governance, document lifecycle and process lifecycle.

Needs improvement:

- add examples for common failure cases if Codex execution reviews repeat the same issues;
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
- review source-of-truth documents;
- review lifecycle states;
- Assess Review Need, Plan Review, Open Review, Assign Reviewer, Execute Review, Report Findings, Request Rework, Submit Rework for Re-review, Re-review, Approve, Reject, Block, Unblock, Close Review and Archive operations;
- reviewer ownership model across Human Owner, ChatGPT Orchestrator, Code Reviewer AI, QA Engineer AI, Technical Writer AI, AI System Maintainer, domain roles and Codex Executor;
- relationship to review types and severity levels from `/ai-system/review-process.md`;
- re-review process;
- review closure rules;
- relationship to task lifecycle, Codex execution lifecycle and QA lifecycle;
- Human Owner approval rules;
- AICP relationship;
- version impact rules;
- audit and history rules;
- boundary rules.

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
- QA source-of-truth documents;
- QA lifecycle states;
- Assess QA Need, Plan QA, Draft Test Cases, Review Test Cases, Start QA, Execute Checks, Report Defects, Request Rework, Run Regression, Approve, Reject, Block, Unblock and Archive operations;
- QA ownership model across Human Owner, ChatGPT Orchestrator, QA Engineer AI, Code Reviewer AI, domain roles and Codex Executor;
- positive, negative, edge case and regression checks;
- QA approval requirements;
- defect reporting and rework flow;
- relationship to task lifecycle, Codex lifecycle and review process;
- Human Owner approval rules;
- AICP relationship;
- version impact rules;
- audit and history rules.

Needs improvement:

- add examples for product-specific QA flows when product projects exist;
- add QA state transition diagram if QA tracking becomes difficult.

---

# 5. Learning Layer

The Learning Layer defines how the system learns, improves and experiments.

## 5.1 Improvement Lifecycle

Status: Partially Implemented

Existing document:

```text
/ai-system/improvement-log.md
```

Current coverage:

- improvement log template exists;
- observations can be recorded;
- entries may be converted to AICP.

Missing:

- improvement states;
- triage rules;
- conversion criteria;
- closure criteria;
- recurring issue detection;
- relationship with knowledge lifecycle and change lifecycle.

Needs improvement:

- expand `improvement-log.md` or create `improvement-lifecycle.md`.

## 5.2 Knowledge Lifecycle

Status: Implemented

Existing document:

```text
/ai-system/knowledge-lifecycle.md
```

Covers:

- managed knowledge item definition;
- what counts as knowledge and what does not;
- knowledge source-of-truth documents;
- knowledge lifecycle states;
- Observe Knowledge, Capture Knowledge, Classify Knowledge, Validate Knowledge, Promote to Glossary, Promote to Rule, Promote to Template, Promote to Prompt, Link to Source, Deprecate Knowledge, Remove Knowledge, Archive Knowledge and Audit Knowledge operations;
- ownership model across Human Owner, ChatGPT Orchestrator, AI System Maintainer, Technical Writer AI, Code Reviewer AI, QA Engineer AI, domain roles and Codex Executor;
- knowledge capture, validation and promotion rules;
- relationship to glossary, rules, prompts, improvement lifecycle, change lifecycle and review lifecycle;
- stale knowledge detection;
- deprecation and removal rules;
- lesson learned storage rules;
- Human Owner approval rules;
- AICP relationship;
- version impact rules;
- audit and history rules;
- boundary rules.

Needs improvement:

- add examples for knowledge promotion paths when repeated observations become frequent;
- add knowledge state transition diagram if knowledge tracking becomes difficult.

## 5.3 Experiment Lifecycle

Status: Missing

Existing related documents:

```text
/ai-system/change-process.md
/ai-system/decision-process.md
```

Current coverage:

- `EXPERIMENT` decision status exists;
- experimental changes are mentioned in the change process.

Missing:

- experiment proposal format;
- hypothesis;
- duration;
- success criteria;
- failure criteria;
- evaluation process;
- adoption/rejection process;
- rollback rules.

Need to create:

```text
/ai-system/experiment-lifecycle.md
```

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
Lifecycle Governance
Language and Localization
```

## Partially Implemented

```text
Improvement Lifecycle
```

## Missing

```text
Experiment Lifecycle
```

## Highest Priority Next Steps

1. Create `experiment-lifecycle.md` because experiments need hypothesis, success criteria and rollback rules.
2. Expand `improvement-log.md` or create `improvement-lifecycle.md` to define triage, conversion and closure.
3. Create `glossary` cross-links for lifecycle terms if terminology drift appears.

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
```

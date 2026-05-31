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

# 2. Governance Layer

The Governance Layer defines how decisions, changes and lifecycle control are managed.

## 2.1 Decision Lifecycle

Status: Missing

Existing related documents:

```text
/ai-system/decision-process.md
/ai-system/owner-guide.md
```

Current coverage:

- decision statuses exist;
- Human Owner approval rule exists;
- decision process is partially described.

Missing:

- full lifecycle of a decision;
- decision states;
- decision ownership;
- decision revision process;
- decision archival rules;
- links between decisions and affected documents.

Need to create:

```text
/ai-system/decision-lifecycle.md
```

## 2.2 Change Lifecycle

Status: Partially Implemented

Existing documents:

```text
/ai-system/change-process.md
/ai-system/improvement-log.md
/ai-system/system-changelog.md
```

Current coverage:

- change process exists;
- AICP template exists;
- versioning rules exist;
- improvement log exists;
- system changelog exists.

Missing or incomplete:

- explicit lifecycle states for a change;
- verification after applying a change;
- rollback lifecycle;
- closure criteria;
- relationship between AICP, experiment and changelog.

Needs improvement:

- expand `change-process.md` or create `change-lifecycle.md`.

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

Status: Missing

Existing related documents:

```text
/ai-system/document-templates.md
/ai-system/rules.md
/ai-system/workflow.md
/ai-system/review-process.md
```

Current coverage:

- document templates exist;
- documentation update rules exist;
- documentation is treated as source of truth.

Missing:

- Create Document;
- Read Document;
- Update Document;
- Review Document;
- Approve Document;
- Deprecate Document;
- Archive Document;
- Delete Document;
- document statuses;
- document ownership;
- document review rules;
- document versioning rules.

Need to create:

```text
/ai-system/document-lifecycle.md
```

## 3.3 Process Lifecycle

Status: Missing

Existing related documents:

```text
/ai-system/workflow.md
/ai-system/change-process.md
/ai-system/review-process.md
/ai-system/interaction-modes.md
```

Current coverage:

- several processes are described;
- workflow exists;
- review process exists;
- change process exists.

Missing:

- Read Process;
- Create Process;
- Update Process;
- Split Process;
- Merge Processes;
- Deprecate Process;
- Delete Process;
- Audit Process;
- process ownership;
- process versioning;
- process effectiveness review.

Need to create:

```text
/ai-system/process-lifecycle.md
```

## 3.4 Task Lifecycle

Status: Partially Implemented

Existing document:

```text
/ai-system/task-format.md
```

Current coverage:

- task format exists;
- Definition of Ready exists;
- Definition of Done exists.

Missing:

- full task states;
- transition rules;
- owner changes;
- rework flow;
- blocked state;
- task archive rules;
- relationship between task, Codex execution and review.

Need to create:

```text
/ai-system/task-lifecycle.md
```

---

# 4. Execution Layer

The Execution Layer defines how work is executed, reviewed and validated.

## 4.1 Codex Execution Lifecycle

Status: Missing

Existing related documents:

```text
/ai-system/human-interaction.md
/ai-system/rules.md
/ai-system/task-format.md
```

Current coverage:

- Codex Executor concept exists;
- prompt package requirements exist;
- expected Codex output format exists.

Missing:

- full Codex execution lifecycle;
- prompt preparation states;
- execution constraints;
- result intake process;
- failure handling;
- rework prompt flow;
- rollback handling.

Need to create:

```text
/ai-system/codex-lifecycle.md
```

## 4.2 Review Lifecycle

Status: Partially Implemented

Existing document:

```text
/ai-system/review-process.md
```

Current coverage:

- review types exist;
- severity levels exist;
- review output format exists.

Missing:

- review states;
- transition rules;
- re-review process;
- reviewer ownership;
- review closure rules;
- relationship between review and task lifecycle.

Needs improvement:

- expand `review-process.md` or create `review-lifecycle.md`.

## 4.3 QA Lifecycle

Status: Missing

Existing related documents:

```text
/ai-system/review-process.md
/ai-system/task-format.md
```

Current coverage:

- QA role exists;
- QA checks are mentioned;
- test cases are part of task format.

Missing:

- QA states;
- test planning flow;
- test execution flow;
- bug reporting flow;
- regression flow;
- QA approval rules.

Need to create:

```text
/ai-system/qa-lifecycle.md
```

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

Status: Missing

Existing related documents:

```text
/ai-system/glossary.md
/ai-system/system-changelog.md
/ai-system/improvement-log.md
```

Current coverage:

- glossary exists;
- changelog exists;
- improvement log exists.

Missing:

- what counts as knowledge;
- how knowledge is captured;
- how knowledge is validated;
- how knowledge becomes a rule, glossary term or template;
- how outdated knowledge is removed;
- how lessons learned are stored.

Need to create:

```text
/ai-system/knowledge-lifecycle.md
```

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
Role Lifecycle
Lifecycle Governance
```

## Partially Implemented

```text
Change Lifecycle
Task Lifecycle
Review Lifecycle
Improvement Lifecycle
```

## Missing

```text
Decision Lifecycle
Document Lifecycle
Process Lifecycle
Codex Execution Lifecycle
QA Lifecycle
Knowledge Lifecycle
Experiment Lifecycle
```

## Highest Priority Next Steps

1. Create `document-lifecycle.md` because documentation is the source of truth.
2. Create `process-lifecycle.md` because processes must be changeable like roles.
3. Create `task-lifecycle.md` because execution depends on tasks.
4. Create `codex-lifecycle.md` because Codex is the execution boundary.
5. Improve `change-process.md` or create `change-lifecycle.md` to define verification, rollback and closure.

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

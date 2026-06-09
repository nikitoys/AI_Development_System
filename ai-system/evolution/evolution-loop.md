# System Evolution Loop

Status: Draft  
Version: v0.1.0

## Purpose

This document defines the controlled loop by which AI_Development_System can improve itself without bypassing governance, review or Human Owner approval.

## Governed Entity

The governed entity is a system evolution item: any observation, proposal, task or change that affects AI_Development_System rules, roles, workflows, lifecycle documents, templates, prompts, project integration model or verification expectations.

## Source-of-Truth Documents

System evolution is governed by:

- `ai-system/evolution/roadmap.md`;
- `ai-system/evolution/evolution-policy.md`;
- `ai-system/evolution/evolution-backlog.md`;
- `ai-system/evolution/system-health-check.md`;
- `ai-system/improvement-lifecycle.md`;
- `ai-system/change-process.md`;
- `ai-system/change-lifecycle.md`;
- `ai-system/document-lifecycle.md`;
- `ai-system/codex-lifecycle.md`;
- `ai-system/review-lifecycle.md`;
- `ai-system/qa-lifecycle.md`;
- `ai-system/system-changelog.md`.

## Loop Overview

```text
Observe
  ↓
Diagnose
  ↓
Propose
  ↓
Plan
  ↓
Execute
  ↓
Verify
  ↓
Review
  ↓
Approve
  ↓
Release
  ↓
Learn
```

## Loop Stages

### 1. Observe

Purpose: detect a possible system improvement.

Allowed inputs:

- Human Owner request;
- analytical report;
- pilot validation result;
- repeated review issue;
- failed task or rework loop;
- version drift;
- missing policy;
- inconsistent documentation;
- broken integration template;
- security or privacy gap.

Output:

- observation record in `improvement-log.md` or `evolution-backlog.md`.

### 2. Diagnose

Purpose: understand the root cause and classify the observation.

Classification examples:

- documentation drift;
- missing lifecycle rule;
- duplicate process;
- missing template;
- unclear owner instruction;
- missing verification rule;
- security/privacy gap;
- integration friction;
- pilot validation failure.

Output:

- diagnosis summary;
- affected documents;
- risk if unchanged;
- proposed conversion path.

### 3. Propose

Purpose: decide whether the observation should become a system change.

Allowed proposal paths:

- add to evolution backlog;
- convert to AICP;
- convert to knowledge item;
- convert to experiment;
- defer;
- reject.

Output:

- system change proposal when behavior, governance or source-of-truth documents change.

### 4. Plan

Purpose: convert an accepted proposal into a bounded task.

Required planning fields:

- Active Role;
- Active Stage;
- Active Document;
- Expected Result;
- Source Documents;
- Scope;
- Out of Scope;
- Allowed Files;
- Acceptance Criteria;
- Verification Mode;
- Review Requirements.

Output:

- evolution task package for Codex Executor or documentation maintainer.

### 5. Execute

Purpose: perform the approved bounded change.

Execution rules:

- only listed files may be modified;
- no silent scope expansion;
- no automatic merge into main;
- no removal of approval gates;
- no escalation of verification mode without explicit reason.

Output:

- branch, diff or prepared file changes;
- execution report.

### 6. Verify

Purpose: check that the change meets acceptance criteria.

Verification may include:

- markdown readability review;
- link and index checks;
- placeholder checks;
- version/status consistency checks;
- template completeness checks;
- schema lint when specs exist;
- manual review for governance consistency.

Output:

- verification result;
- unresolved issues or pass statement.

### 7. Review

Purpose: independently assess the proposed change.

Review must check:

- scope compliance;
- consistency with lifecycle governance;
- affected document references;
- approval boundaries;
- security/privacy impact;
- changelog requirements;
- risk of documentation drift.

Output:

- review report using the review process format.

### 8. Approve

Purpose: Human Owner decides whether the system change is accepted.

Rules:

- Human Owner approval is required for behavior-changing system evolution;
- AI may recommend approval but cannot grant it;
- unresolved critical review findings block approval;
- major roadmap or governance changes require explicit approval.

Output:

- approved, rejected or changes-requested decision.

### 9. Release

Purpose: make the approved change part of the system history.

Required updates when applicable:

- `system-changelog.md`;
- affected indexes;
- roadmap status;
- backlog status;
- version markers;
- templates or integration notes.

Output:

- merged change or release record.

### 10. Learn

Purpose: capture what the system learned from the evolution cycle.

Output may include:

- improvement log entry;
- knowledge item;
- updated roadmap item;
- new experiment;
- updated health-check criterion.

## Loop Entry Rules

A system evolution cycle may start from:

- explicit Human Owner instruction;
- roadmap item;
- backlog item;
- health-check finding;
- pilot validation finding;
- analytical report finding;
- repeated failure in execution, review or QA.

## Loop Exit Rules

A system evolution cycle ends when one of the following is true:

- change is approved, released and recorded;
- change is rejected with reason;
- change is deferred with revisit trigger;
- item is converted to knowledge or experiment;
- item is superseded by another approved item.

## Anti-Runaway Rule

The system must not recursively create new evolution work without a stopping condition.

Each evolution cycle must produce one bounded outcome:

```text
release | reject | defer | convert | close
```

If the system detects additional issues during execution, they must be logged separately unless they block the current task.

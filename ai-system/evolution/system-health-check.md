# AI System Health Check

Status: Draft  
Version: v0.1.0

## Purpose

This document defines a repeatable checklist for assessing the health of AI_Development_System.

The health check is used to identify evolution backlog items, roadmap updates, AICP candidates and pilot validation gaps.

## Health Dimensions

```text
1. Source-of-truth integrity
2. Version and status consistency
3. Lifecycle completeness
4. Review and QA readiness
5. Integration readiness
6. Security and privacy readiness
7. Automation and machine-checkability
8. Pilot validation evidence
9. Owner usability
10. Changelog and audit trail
```

## 1. Source-of-Truth Integrity

Check:

- primary entrypoints point to the same system model;
- `ai-system/README.md` indexes all active source-of-truth documents;
- lifecycle documents reference their governing documents;
- templates reference current workflow rules;
- obsolete documents are deprecated or archived;
- no critical rule exists only in an unindexed file.

Output:

- pass;
- minor drift;
- major drift;
- blocking drift.

## 2. Version and Status Consistency

Check:

- root README, AI system README and changelog do not contradict each other;
- new documents have `Status` and `Version` fields;
- Draft documents are not represented as production-proven;
- version-impacting changes are recorded in `system-changelog.md`;
- integrated project templates can track adopted system version.

Output:

- version synchronized;
- version drift detected;
- status drift detected;
- changelog update required.

## 3. Lifecycle Completeness

Check each managed lifecycle for:

- governed entity;
- source-of-truth documents;
- states;
- allowed operations;
- ownership model;
- approval rules;
- AICP relationship;
- version impact;
- audit/history rules;
- boundary rules.

Output:

- implemented;
- partially implemented;
- missing;
- needs improvement.

## 4. Review and QA Readiness

Check:

- review process is clear enough to evaluate system changes;
- review lifecycle defines closure and re-review;
- QA lifecycle can handle documentation, template and integration checks;
- severity levels are usable for system evolution;
- blocking findings prevent release.

Output:

- review-ready;
- QA-ready;
- review friction detected;
- QA gap detected.

## 5. Integration Readiness

Check:

- foldered integration templates are complete;
- root-mode templates remain coherent;
- placeholders are documented;
- project control files are indexed;
- update workflow is clear;
- example project exists or is planned;
- bootstrap/update automation exists or is tracked.

Output:

- integration-ready;
- manual-only integration;
- missing example;
- automation gap.

## 6. Security and Privacy Readiness

Check:

- secret-handling rules exist;
- external LLM disclosure rules exist;
- sandbox boundaries are documented;
- sensitive code/data guidance exists;
- security review can reference a policy;
- browser/visual QA boundaries are explicit.

Output:

- baseline defined;
- policy missing;
- sensitive-data risk;
- sandbox gap.

## 7. Automation and Machine-Checkability

Check:

- link checking exists or is tracked;
- placeholder detection exists or is tracked;
- status/version schema exists or is tracked;
- machine-readable specs exist or are planned;
- generated docs policy exists if specs are introduced;
- CI can validate documentation integrity.

Output:

- machine-checkable;
- partially checkable;
- manual-only;
- automation gap.

## 8. Pilot Validation Evidence

Check:

- real repository pilots are documented;
- failures are logged;
- repeated issues are triaged;
- pilot outcomes inform roadmap;
- golden example exists;
- research or benchmark findings are separated from operational rules.

Output:

- pilot-proven;
- pilot in progress;
- no pilot evidence;
- evidence insufficient.

## 9. Owner Usability

Check:

- Human Owner can understand where to start;
- owner-facing commands are documented;
- mode selection is understandable;
- Russian owner-facing interaction remains supported when system docs stay English;
- prompts for Codex are easy to generate from templates;
- roadmap is understandable without reading every lifecycle document.

Output:

- owner-friendly;
- heavy onboarding;
- unclear mode usage;
- localization friction.

## 10. Changelog and Audit Trail

Check:

- behavior changes are recorded;
- new documents are listed;
- reasons for changes are documented;
- changelog entries map to versioned releases;
- important decisions can be traced to source documents;
- system evolution items can be traced to roadmap, backlog or Human Owner request.

Output:

- audit-ready;
- changelog update needed;
- traceability gap;
- release packaging gap.

## Health Check Output Format

```md
# AI System Health Check Report

Date:
Reviewer:
Scope:

## Summary

Overall status:
Top risks:
Recommended next actions:

## Findings

### Finding 1
Dimension:
Severity:
Evidence:
Recommendation:
Conversion path: backlog | AICP | knowledge | experiment | reject | defer

## Closure

Required owner decision:
Required changelog update:
Required follow-up task:
```

## Severity Levels

```text
Critical  blocks safe system use or removes governance control
High      creates serious drift, security risk or integration failure
Medium    creates friction or maintainability risk
Low       cosmetic, clarity or minor consistency issue
```

## Recommended Cadence

Run a health check:

- before major releases;
- after adding or changing lifecycle documents;
- after pilot validation cycles;
- after security/privacy changes;
- when repeated review or QA issues appear;
- when the Human Owner requests system evolution planning.

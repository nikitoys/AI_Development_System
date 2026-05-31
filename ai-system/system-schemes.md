# AI Development System Schemes

Status: Draft
Version: v0.1.0

## Purpose

This document gives compact text-based schemes for understanding the AI Development System at a glance.

It is an onboarding aid. Detailed rules remain in the source documents listed in `/ai-system/README.md` and `/ai-system/operating-model.md`.

## Role Scheme

```text
Human Owner
  sets direction
  approves decisions
  accepts or rejects results

ChatGPT Orchestrator
  understands the request
  selects mode and active role
  prepares prompts and task packages
  reviews Codex output
  routes work to the right lifecycle

AI Roles
  Product Manager AI
  System Analyst AI
  Architect AI
  UX/UI Designer AI
  Backend Developer AI
  Frontend Developer AI
  DevOps Engineer AI
  QA Engineer AI
  Code Reviewer AI
  Technical Writer AI
  AI System Maintainer

Codex Executor
  changes repository files
  works only inside approved scope
  reports changed files, tests, errors and questions

Documentation
  stores rules
  stores decisions
  stores lifecycles
  stores prompts, templates and history
```

## Document Scheme

```text
Root repository
  README.md
    first-time overview in English
  README.ru.md
    first-time overview in Russian
  AGENTS.md
    instructions for future AI sessions

/ai-system
  README.md
    AI Development System index
  owner-guide.md
    Human Owner interaction guide
  operating-model.md
    implemented system layers and next improvements
  system-structure.md
    high-level system structure
  roles.md
    role registry
  rules.md
    global rules
  glossary.md
    term navigation
  workflow.md
    development stages and gates
  task-format.md
    standard task format
  review-process.md
    review types, severity and output format
  change-process.md
    controlled system evolution process
  lifecycle documents
    governance, decision, change, document, process, task, Codex, review, QA, knowledge, experiment and improvement rules
  system-changelog.md
    AI Development System history
```

## Process Scheme

```text
Idea or request
  -> clarify intent
  -> choose mode
  -> select active role and source documents
  -> create task, decision or change proposal
  -> prepare prompt package when repository execution is needed
  -> Human Owner approves scope
  -> Codex Executor changes files only inside approved scope
  -> ChatGPT Orchestrator performs result intake
  -> review checks the result
  -> QA checks behavior or documentation consistency when needed
  -> Human Owner accepts, rejects, defers or requests rework
  -> documentation and changelog are updated when required
  -> task, review, change or lifecycle record is closed or archived
```

## Compact Summary

```text
Human Owner controls direction.
ChatGPT Orchestrator controls routing and prompts.
AI Roles provide specialization.
Codex Executor performs scoped repository edits.
Documentation is the source of truth.
Lifecycles keep tasks, reviews, QA, decisions, changes and improvements controlled.
```

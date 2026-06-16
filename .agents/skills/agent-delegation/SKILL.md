---
name: agent-delegation
description: Use when Controller Codex needs to prepare precise Worker Agent handoff prompts for bounded delegated work in AI_Development_System L3 manual orchestration. Keeps delegation manual-only and forbids automatic dispatch, runtime behavior and Worker Agent self-acceptance.
---

# Agent Delegation Skill

## Purpose

Help Controller Codex prepare precise Worker Agent handoff prompts for bounded delegated work.

This skill is for `Two-Level Delegated Agent Execution`, where Controller Codex prepares a Worker Agent Prompt Package and the Human Owner or operator manually starts the Worker Agent session.

## Authority Boundary

This skill is guidance only.

It does not authorize:

- runtime behavior;
- automatic dispatch;
- automatic execution;
- automatic Codex invocation;
- automatic Worker Agent launch;
- automatic branch or worktree lifecycle;
- automatic commit, push, merge or pull request creation;
- automatic result approval;
- automatic review or QA closure;
- movement from L3 to L4.

Authority remains in:

- Human Owner decisions;
- `AGENTS.md`;
- source documents under `/ai-system`;
- controlled project state under root `/AI_PROJECT`;
- validation and lifecycle commands in `scripts/*ctl.py`.

If this skill conflicts with a source document, lifecycle rule, task scope, prompt package or Human Owner decision, follow the authoritative source and report the conflict.

## Required Flow

```text
Human Owner request
-> Controller Codex classifies work
-> Controller Codex reads minimal docs
-> Controller Codex creates Worker Agent Prompt Package
-> Human Owner manually launches Worker Agent session
-> Worker Agent returns Agent Result
-> Controller Codex performs intake/review
-> CLI-controlled state updates only after approval/checks
```

Controller Codex may prepare the prompt package. It must not launch the Worker Agent automatically.

## Worker Prompt Requirements

Every Worker Agent prompt must include:

- mode marker;
- Worker Agent role;
- active stage;
- active document;
- expected result;
- repository context;
- minimal read set;
- task;
- scope;
- out of scope;
- allowed files;
- forbidden actions;
- verification instructions;
- result format;
- return instructions.

Use `/ai-system/templates/agent-worker-prompt.md` as the reusable template when it fits the task.

## Controller Rules

Controller Codex must:

- read minimal docs first;
- use the Documentation Navigation Skill to choose the read set;
- include only necessary context;
- prefer one Worker Agent prompt per bounded work item;
- preserve parent Task and Agent Work Package scope;
- list exact allowed files or conservative path patterns;
- include forbidden actions explicitly;
- require a structured Agent Result;
- perform result intake before review, QA routing or state updates;
- use project-control CLIs for state updates.

Controller Codex must never:

- delegate vague or open-ended work;
- allow protected `AI_PROJECT` manual edits;
- imply that Worker Agents may approve or accept their own work;
- imply L4, assisted execution or runtime approval;
- automatically dispatch a Worker Agent;
- accept Worker Agent output without review and Human Owner control;
- broaden scope based on Worker Agent questions or suggestions.

## Worker Rules

Worker Agent must:

- stay inside the prompt scope;
- edit only allowed files;
- read only the specified minimal docs unless blocked;
- report any needed extra context before expanding scope;
- respect parent Task and Agent Work Package boundaries;
- return a structured Agent Result.

Worker Agent must not:

- edit `AI_PROJECT/state/**`;
- edit `AI_PROJECT/events/**`;
- edit `AI_PROJECT/generated/**`;
- commit;
- push;
- merge;
- open pull requests;
- approve or accept its own work;
- mark tasks done;
- close review or QA;
- change runtime maturity;
- approve L4;
- perform automatic dispatch;
- modify files outside allowed files.

## Stop Conditions

Stop and ask the Human Owner, or return a blocker, when:

- scope is unclear;
- allowed files are missing or too broad;
- source-of-truth document is unclear;
- the task requires a Human Owner decision;
- the Worker Agent would need protected-file mutation;
- the Worker Agent would need automatic dispatch or runtime behavior;
- security or privacy risk is detected;
- the work would change lifecycle rules, prompt behavior or system maturity outside an approved evolution task;
- the Worker Agent result violates scope, allowed files or forbidden actions.

## Result Intake

After Worker Agent output returns, Controller Codex should check the result against:

- the Worker Agent Prompt Package;
- parent Task scope and allowed files;
- Agent Work Package boundaries when applicable;
- `agent-result-intake.md`;
- `integration-review.md` when multiple results or cross-package consistency matter;
- review and QA instructions.

Controller Codex may recommend `APPROVED`, `REWORK`, `REJECTED` or `DEFERRED`, but the Human Owner remains the final authority.

## Boundary Statement

Two-Level Delegated Agent Execution is L3 manual delegation only.

It improves prompt precision for manually launched Worker Agent sessions. It does not approve L4 Assisted Execution, runtime automation or automatic acceptance.

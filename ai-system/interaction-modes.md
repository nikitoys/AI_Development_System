# Interaction Modes and System Boundary

Status: Draft  
Version: v0.1.0

## Purpose

This document defines when the AI Development System must be used and when a request may be answered outside the system process.

Not every user request is a system-managed development task.

The system must separate:

1. ordinary conversation;
2. AI Development System work.

## Core Principle

The AI Development System is mandatory only for requests that affect the repository, project documentation, application architecture, implementation workflow, role model or the AI Development System itself.

For simple explanations, brainstorming or informal questions, ChatGPT may answer normally without activating the full workflow.

## Two Interaction Modes

## 1. Free Conversation Mode

Free Conversation Mode is used for general discussion, explanation and thinking.

Examples:

```text
Explain what an AICP is.
What is the difference between QA and Code Review?
Can this system be smaller?
Give me examples of role names.
Explain this concept more simply.
```

In this mode:

- no formal workflow is required;
- no active role header is required unless useful;
- no repository changes are made;
- no Codex prompt is produced unless requested;
- no system changelog update is required;
- no AICP is required.

Output may be conversational.

## 2. AI Development System Mode

AI Development System Mode is used when the request affects controlled project work.

This mode is mandatory when the request involves:

- creating or editing files in `/ai-system`;
- creating or editing files in `/docs`;
- changing role definitions;
- changing workflow;
- changing system rules;
- changing task format;
- changing review process;
- changing application architecture;
- preparing a Codex prompt;
- reviewing Codex output;
- accepting, rejecting or reworking repository changes;
- creating AICP;
- applying an approved system change.

In this mode, ChatGPT Orchestrator must identify:

```text
Active Role:
Active Stage:
Active Document:
Expected Result:
```

## Mode Detection

ChatGPT Orchestrator must classify each request before acting.

## Free Conversation Indicators

A request likely belongs to Free Conversation Mode if it asks to:

- explain;
- compare;
- discuss;
- brainstorm;
- clarify;
- think through an idea;
- give examples;
- answer conceptually.

## AI Development System Indicators

A request belongs to AI Development System Mode if it asks to:

- add something to the repository;
- update a document;
- prepare a prompt for Codex;
- check Codex output;
- change a role;
- change workflow;
- change rules;
- approve or reject a task;
- create an AICP;
- change system version;
- perform review or QA.

## Explicit Mode Commands

The Human Owner may force the mode.

```text
Free mode: explain this without changing the system.
System mode: process this through AI Development System.
```

Aliases:

```text
/ free
/ system
```

## Boundary Rule

If a request may change repository state or system rules, it must be handled in AI Development System Mode.

If a request only asks for explanation, it may be handled in Free Conversation Mode.

## Escalation Rule

A request may start in Free Conversation Mode and then escalate to AI Development System Mode.

Example:

```text
Human: Can roles be dynamic?
ChatGPT: Yes, conceptually...
Human: Good, record this in the repository.
ChatGPT: Switches to AI Development System Mode.
```

## Downgrade Rule

A request may start as a system topic but remain Free Conversation Mode if no action is requested.

Example:

```text
Human: What is role lifecycle?
```

This does not require AICP or file changes unless the Human Owner asks to update documentation.

## Strict System Mode Requirements

When AI Development System Mode is active, ChatGPT Orchestrator must:

1. identify active role;
2. identify active stage;
3. identify active document;
4. identify expected result;
5. check whether Human Approval is required;
6. check whether Codex is needed;
7. avoid unrelated changes;
8. respect source-of-truth documents.

## Role of ChatGPT Orchestrator

ChatGPT Orchestrator is responsible for mode routing.

It must decide whether to answer directly or process the request through the AI Development System.

If unclear, it should state the assumed mode and continue, or ask for confirmation when the risk is high.

## Examples

## Example 1 — Free Conversation

Request:

```text
Explain why we need a Project Manager AI.
```

Mode:

```text
Free Conversation Mode
```

Reason:

No repository or system change is requested.

## Example 2 — System Mode

Request:

```text
Add a document describing Project Manager AI.
```

Mode:

```text
AI Development System Mode
```

Reason:

Repository documentation will change.

## Example 3 — Free First, Then System

Request:

```text
Can QA and Reviewer be merged?
```

Mode:

```text
Free Conversation Mode
```

Possible answer:

Yes, conceptually.

If the Human Owner says:

```text
Apply this change.
```

Then switch to:

```text
AI Development System Mode
```

## Example 4 — Role Change

Request:

```text
Remove UX/UI Designer AI from the active role set.
```

Mode:

```text
AI Development System Mode
```

Required process:

```text
ChatGPT Orchestrator
→ AI System Maintainer
→ Role Lifecycle
→ AICP
→ Human Approval
→ Codex updates /ai-system
→ system-changelog update
```

## Main Rule

Do not force every conversation through the system.

Do force every repository, role, workflow, documentation, architecture or implementation change through the system.

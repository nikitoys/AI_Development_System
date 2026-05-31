# Human Owner Guide

Status: Draft  
Version: v0.1.0

## Purpose

This document explains how the Human Owner should interact with the AI Development System.

The Human Owner does not need to know every internal role or document. The Human Owner can speak naturally, but may also mark requests with explicit mode tags when precision is needed.

## Core Rule

```text
Human Owner controls.
ChatGPT Orchestrator routes.
AI roles specialize.
Codex executes.
Documentation records.
```

## Two Main Modes

## 1. Free Mode

Use Free Mode for explanation, thinking, comparison or informal discussion.

Marker:

```text
[FREE]
```

Alias:

```text
/free
```

Example:

```text
[FREE]
Explain why we need AI System Maintainer.
```

Free Mode means:

- no repository changes;
- no Codex prompt unless explicitly requested;
- no AICP;
- no system changelog update;
- no formal workflow required.

## 2. System Mode

Use System Mode when the request should be handled through the AI Development System.

Marker:

```text
[SYSTEM]
```

Alias:

```text
/system
```

Example:

```text
[SYSTEM]
Check whether the current role structure should be simplified.
```

System Mode means ChatGPT Orchestrator must identify:

```text
Active Role:
Active Stage:
Active Document:
Expected Result:
```

System Mode is required when the request may affect:

- `/ai-system`;
- `/docs`;
- repository files;
- roles;
- workflow;
- rules;
- task format;
- review process;
- architecture;
- Codex execution;
- system version.

## Additional Markers

## Codex Mode

Use when you need a prompt package for Codex.

```text
[CODEX]
Prepare a Codex prompt to update /ai-system/roles.md.
```

This means ChatGPT should not apply the change directly unless explicitly allowed. It should prepare a structured Codex prompt with scope, restrictions and expected output.

## Review Mode

Use when Codex has already produced a result and you want it checked.

```text
[REVIEW]
Codex changed these files:
...
Check the result.
```

This means ChatGPT should activate review logic and classify issues as Critical, Major, Minor or Suggestion.

## Evolution Mode

Use when the request is about changing the AI Development System itself.

```text
[EVOLUTION]
Developer AI is too broad. Check whether it should be split.
```

This means ChatGPT should route the request to:

```text
System Evolution Layer
→ AI System Maintainer
→ relevant lifecycle process
```

If a real change is needed, it should go through AICP and Human Approval.

## Dry Run Mode

Use when you want to simulate a change without applying it.

```text
[DRY-RUN]
Show what would happen if we merged QA Engineer AI and Code Reviewer AI.
```

This means:

- analyze consequences;
- do not change files;
- do not prepare an apply prompt unless asked;
- do not update changelog.

## Recommended Marker Set

```text
[FREE]       ordinary explanation or discussion
[SYSTEM]     process through AI Development System
[CODEX]      prepare prompt package for Codex
[REVIEW]     review Codex output
[EVOLUTION]  analyze or change the AI Development System
[DRY-RUN]    simulate without applying
```

## If No Marker Is Provided

ChatGPT Orchestrator should auto-detect the mode.

Default behavior:

```text
Explanation or discussion → Free Mode
Repository or documentation change → System Mode
Codex result check → Review Mode
AI Development System change → Evolution Mode
Simulation request → Dry Run Mode
```

If the request is ambiguous and could change repository state or system rules, ChatGPT should either:

- state the assumed mode; or
- ask for confirmation.

## Examples

## Free Example

```text
[FREE]
What is the difference between role and layer?
```

Expected behavior:

- answer directly;
- no repository changes.

## System Example

```text
[SYSTEM]
Check whether the role hierarchy is understandable for a new owner.
```

Expected behavior:

- identify active role;
- inspect relevant documents;
- provide structured result;
- suggest updates if needed.

## Codex Example

```text
[CODEX]
Prepare a prompt for Codex to add command-reference.md.
```

Expected behavior:

- produce a Codex prompt package;
- define allowed files;
- define forbidden actions;
- define expected output.

## Review Example

```text
[REVIEW]
Codex updated /ai-system/roles.md. Here is the diff: ...
```

Expected behavior:

- review scope;
- check consistency;
- identify issues;
- recommend APPROVED, REWORK or REJECTED.

## Evolution Example

```text
[EVOLUTION]
Can we remove UX/UI Designer AI from the minimal role set?
```

Expected behavior:

- analyze through AI System Maintainer;
- check role lifecycle;
- decide whether this is a discussion or requires AICP;
- do not apply changes without Human Approval.

## Owner Decision Words

The Human Owner may use these decision words:

```text
APPROVED   accept result
REWORK     request changes
REJECTED   reject result
DEFERRED   postpone decision
EXPERIMENT test temporarily
```

## Main Safety Rule

Free discussion may happen outside the system process.

Any change to repository files, roles, workflow, rules, architecture, documentation or system version must go through System Mode.

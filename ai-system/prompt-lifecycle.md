# Prompt Lifecycle and Codex Prompt Factory

Status: Draft  
Version: v0.1.0

## Purpose

This document defines how prompts are created, reviewed, approved, executed and improved inside the AI Development System.

Prompts are managed artifacts. They should not be treated as random chat messages when they affect repository work, Codex execution or the AI Development System itself.

## Core Idea

The Human Owner should not manually write detailed Codex prompts every time.

Instead:

```text
Human Intent
→ ChatGPT Orchestrator
→ Prompt Draft
→ Human Review
→ Approved Prompt Package
→ Codex Execution
→ Result Review
→ Prompt Improvement if needed
```

## Codex Prompt Factory

Codex Prompt Factory is the mechanism that turns a Human Owner intent into a structured prompt package for Codex.

It is operated by ChatGPT Orchestrator.

## Prompt Types

## 1. System Prompt

Defines the behavior of the whole AI Development System.

Source document:

```text
/ai-system/system-prompt.md
```

## 2. Role Prompt

Defines behavior of a specific AI role.

Source document:

```text
/ai-system/roles.md
```

## 3. Codex Prompt Package

A structured prompt prepared for Codex to change repository files.

Used when the Human Owner asks to create, update, review or apply repository changes.

## 4. Review Prompt

A prompt used to review Codex output.

Usually activates Code Reviewer AI, QA Engineer AI or AI System Maintainer.

## 5. Rework Prompt

A prompt used to correct issues found during review.

It must be narrower than the original task and must only address approved review findings.

## 6. Evolution Prompt

A prompt used to analyze or change the AI Development System itself.

It usually routes to AI System Maintainer and may require AICP before any repository changes.

## Prompt Lifecycle States

```text
Intent
→ Draft
→ Reviewed
→ Approved
→ Sent to Codex
→ Executed
→ Result Reviewed
→ Closed
```

Optional states:

```text
Rejected
Rework Required
Archived
Improved
```

## State Definitions

## Intent

The Human Owner describes what they want in natural language.

Example:

```text
We need to create document-lifecycle.md.
```

## Draft

ChatGPT Orchestrator creates a structured prompt.

The draft is not yet approved for Codex execution.

## Reviewed

The Human Owner or ChatGPT checks whether the prompt is safe, scoped and complete.

## Approved

The Human Owner approves the prompt for Codex.

## Sent to Codex

The approved prompt is pasted into Codex or sent through an automation.

## Executed

Codex performs repository changes and returns output.

## Result Reviewed

ChatGPT reviews the Codex result using Review Mode.

## Closed

The execution result is accepted or the task is intentionally stopped.

## Required Structure of a Codex Prompt Package

Every Codex Prompt Package should include:

```text
Mode Marker:
Mode:
Role:
Repository:
Context:
Source Documents:
Task:
Scope:
Out of Scope:
Allowed Files:
Forbidden Actions:
Acceptance Criteria:
Expected Output:
Review Instructions:
```

## Mode Marker Requirement

Every generated prompt that is intended for another AI/Codex session must start with an explicit mode marker.

Examples:

```text
[SYSTEM]
```

```text
[CODEX]
```

```text
[REVIEW]
```

```text
[EVOLUTION]
```

The first line of a generated prompt should be the mode marker.

If the prompt will be sent to Codex to work on repository files, prefer:

```text
[SYSTEM]
```

or:

```text
[CODEX]
```

If the prompt is only a reusable prompt draft, use:

```text
[PROMPT]
```

## Prompt Header Requirement

After the mode marker, generated prompts should include a short operating header:

```text
Active Role:
Active Stage:
Active Document:
Expected Result:
```

This makes the prompt self-describing and prevents the receiving AI session from treating the task as ordinary free conversation.

## Bad Example

```text
Read all files in /ai-system and suggest improvements.
```

Problem:

- no mode marker;
- no active role;
- no scope;
- no explicit prohibition against file changes;
- no expected result format.

## Good Example

```text
[SYSTEM]

Active Role: AI System Maintainer + Technical Writer AI
Active Stage: System Audit
Active Document: /ai-system
Expected Result: audit report only, no file changes

Repository: nikitoys/AI_Development_System

Task:
Read /ai-system and audit the current AI Development System.

Scope:
- identify useful documents;
- identify missing lifecycle documents;
- identify duplicated or conflicting rules;
- propose 3-5 next tasks.

Out of Scope:
- do not create application code;
- do not edit files;
- do not create new documents;
- do not change system rules.

Expected Output:
- Current State
- Missing Parts
- Duplicates / Conflicts
- Next 3-5 Tasks
- Recommendation
```

## Prompt Marker

Use this marker when the Human Owner wants ChatGPT to create a prompt but not execute anything directly:

```text
[PROMPT]
```

Alias:

```text
/prompt
```

Example:

```text
[PROMPT]
Create a Codex prompt to add /ai-system/document-lifecycle.md.
```

Expected behavior:

- ChatGPT creates a prompt package;
- no repository changes are made unless explicitly requested;
- the prompt should include allowed files and forbidden actions;
- the generated prompt must include its own mode marker;
- the prompt waits for Human Owner approval.

## Difference Between [PROMPT] and [CODEX]

`[PROMPT]` means:

```text
Generate a prompt artifact for review.
Do not assume immediate execution.
```

`[CODEX]` means:

```text
Prepare a Codex-ready prompt package for execution.
The Human Owner may send it to Codex after review.
```

Both modes should keep Human Owner approval in the loop.

## Prompt Storage

Prompts may be stored when they are reusable, important or part of system evolution.

Recommended location:

```text
/ai-system/prompts/
```

Recommended files:

```text
/ai-system/prompts/README.md
/ai-system/prompts/codex-prompt-template.md
/ai-system/prompts/review-prompt-template.md
/ai-system/prompts/rework-prompt-template.md
/ai-system/prompts/evolution-prompt-template.md
```

Generated one-off prompts do not need to be committed unless they represent a reusable pattern.

## Automation Boundary

The system may later automate prompt execution, but only with explicit safeguards.

Safe automation sequence:

```text
Human Intent
→ ChatGPT generates prompt
→ Human approves prompt
→ Automation sends prompt to Codex
→ Codex returns result
→ ChatGPT reviews result
→ Human approves repository changes
```

Unsafe automation:

```text
ChatGPT generates prompt
→ Codex executes automatically
→ changes are accepted automatically
```

This is not allowed by default.

## Self-Feeding Automation

Self-feeding means a system generates a prompt and feeds it into Codex or another executor automatically.

This may be allowed only for low-risk operations after explicit Human Owner approval and clear constraints.

Allowed only if:

- operation scope is narrow;
- allowed files are explicit;
- forbidden actions are explicit;
- rollback is possible;
- review is mandatory;
- Human Owner approval is required before final acceptance.

Not allowed for:

- deleting roles;
- changing workflow structure;
- changing system rules;
- changing architecture;
- changing security-related behavior;
- applying major version changes;
- accepting Codex output without review.

## Prompt Improvement

If Codex repeatedly makes the same mistake, the issue may indicate a weak prompt.

Process:

```text
Review issue
→ Identify prompt weakness
→ Record improvement if recurring
→ Update prompt template if needed
→ Update system changelog if system behavior changes
```

## Main Rule

Prompts that affect repository state are controlled artifacts.

They may be generated by AI, but they should be reviewed by the Human Owner before execution and reviewed again after Codex produces a result.

A generated prompt must carry its own mode marker so the next AI/Codex session knows whether it is free conversation, system work, execution, review or evolution.

# AGENTS.md — AI Development System Bootstrap

Status: Draft  
Version: v0.2.0

## Purpose

This repository is not a normal application repository.

It contains an AI Development System: an operating model for developing projects through AI roles, documentation, lifecycle governance, prompt generation, Codex execution, review and controlled evolution.

When working in this repository, do not treat requests as ordinary coding tasks by default.

First identify the interaction mode and route the request through the AI Development System.

## Mandatory First Read

Before answering any request about this repository, read these files first:

```text
/ai-system/owner-guide.md
/ai-system/interaction-modes.md
/ai-system/prompt-lifecycle.md
/ai-system/operating-model.md
/ai-system/system-structure.md
/ai-system/rules.md
```

For role-related requests, also read:

```text
/ai-system/role-lifecycle.md
/ai-system/role-interaction.md
/ai-system/roles.md
```

For lifecycle or governance requests, also read:

```text
/ai-system/change-process.md
/ai-system/improvement-log.md
/ai-system/system-changelog.md
```

For task, execution, review or Codex requests, also read:

```text
/ai-system/task-format.md
/ai-system/review-process.md
/ai-system/human-interaction.md
```

Legacy state files may still exist, but `/ai-system` is the primary source of truth for the AI Development System.

## Interaction Modes

Requests must be classified before execution.

Supported markers:

```text
[FREE]       ordinary explanation or discussion
[SYSTEM]     process through AI Development System
[PROMPT]     generate a prompt artifact for review
[CODEX]      prepare a Codex-ready prompt package
[REVIEW]     review Codex output
[EVOLUTION]  analyze or change the AI Development System
[DRY-RUN]    simulate without applying
```

If no marker is provided, infer the mode:

```text
Explanation or discussion → [FREE]
Prompt generation request → [PROMPT]
Repository or documentation change → [SYSTEM]
Codex execution prompt → [CODEX]
Codex result check → [REVIEW]
AI Development System change → [EVOLUTION]
Simulation request → [DRY-RUN]
```

If the request can change repository files, roles, workflow, rules, architecture, documentation or system version, do not treat it as free conversation.

## Required System Header

For `[SYSTEM]`, `[CODEX]`, `[REVIEW]`, `[EVOLUTION]` and repository-affecting tasks, start the response with:

```text
Active Role:
Active Stage:
Active Document:
Expected Result:
```

This header is required to make the current mode explicit.

## Prompt Generation Rule

If the user asks to generate a prompt for another AI/Codex session, treat it as `[PROMPT]` mode even if the user did not provide the marker.

Every generated prompt intended for another AI/Codex session must start with its own explicit mode marker.

Allowed generated prompt markers:

```text
[SYSTEM]
[CODEX]
[REVIEW]
[EVOLUTION]
[DRY-RUN]
```

A generated prompt must include:

```text
Active Role:
Active Stage:
Active Document:
Expected Result:
Repository:
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

Do not output unmarked prompts like:

```text
Read all files and suggest improvements.
```

Instead output self-describing prompts with a mode marker and execution boundaries.

## Repository Change Rule

Do not change repository files unless the user explicitly asks for a repository change or a Codex execution task.

For audits, analysis, planning and prompt generation:

- read relevant files;
- produce an answer or prompt;
- do not edit files unless explicitly requested.

## AI Development System Change Rule

Changes to the AI Development System itself must go through controlled evolution.

For changes to roles, lifecycle, workflow, rules, prompts, operating model or system structure:

```text
Human request
→ classify as [EVOLUTION] or [SYSTEM]
→ activate AI System Maintainer
→ check relevant lifecycle document
→ create or reference AICP if needed
→ require Human Owner approval
→ only then prepare/apply repository changes
```

Do not silently change system behavior.

## Codex Execution Rule

Codex is an executor, not the owner of product or system decisions.

When preparing Codex work, include:

- role;
- context;
- source documents;
- task;
- scope;
- out of scope;
- allowed files;
- forbidden actions;
- acceptance criteria;
- expected output.

Codex must report:

- changed files;
- summary;
- tests or checks;
- errors;
- questions;
- diff or key changes.

## Human Owner Control

The Human Owner makes final decisions.

Use these decision words:

```text
APPROVED   accept result
REWORK     request changes
REJECTED   reject result
DEFERRED   postpone decision
EXPERIMENT test temporarily
```

AI may recommend a decision, but the Human Owner approves or rejects.

## Safety Rules

Do not:

- create application-specific backend, frontend or infrastructure unless explicitly requested;
- change multiple unrelated system areas in one task;
- remove roles, rules or lifecycle documents without explicit Human Owner approval;
- treat AI Development System evolution as ordinary free conversation;
- generate prompts without mode markers;
- accept Codex output automatically without review.

## Default Behavior

When unsure:

1. Read the mandatory AI system documents.
2. Classify the request mode.
3. State the assumed mode.
4. Use the required system header if process work is involved.
5. Keep the scope narrow.
6. Ask for confirmation before repository changes if risk is high.

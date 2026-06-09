# Privacy and Data-Handling Policy

Status: Draft  
Version: v0.1.0

## Purpose

This policy defines how AI_Development_System handles private, sensitive and project-specific data when working with AI assistants, Codex-like executors and external LLM services.

## Core Rule

Only share the minimum data needed for the approved task.

Human Owner approval is required before sharing sensitive personal data, customer data, secrets, proprietary datasets or confidential project material with external services beyond the tools already approved for the task.

## Data Categories

Public data:

- public documentation;
- public source code;
- non-sensitive examples;
- already published project information.

Project-private data:

- private repository code;
- internal architecture;
- unpublished product plans;
- private issue context;
- non-public business logic.

Sensitive data:

- personal data;
- customer data;
- credentials and secrets;
- payment or financial data;
- production logs with user identifiers;
- health, legal or regulated information;
- security findings before owner-approved disclosure.

## External LLM Sharing Rules

AI roles and Codex-like executors must:

- avoid sending secrets or sensitive data to external LLMs;
- redact personal and customer identifiers unless they are necessary and approved;
- summarize sensitive files when full content is not required;
- keep prompt context limited to source documents and files needed for the task;
- disclose when external research or external tools are used for high-impact decisions.

## Data Minimization

Before using repository data in prompts or reports:

1. Identify the minimum source documents needed.
2. Prefer paths, summaries and targeted excerpts over broad file dumps.
3. Redact secrets and personal identifiers.
4. Keep unrelated project files out of scope.
5. Record open questions instead of guessing from private data that is not needed.

## Logs and Generated Artifacts

Generated artifacts must not include:

- raw secrets;
- unredacted customer data;
- unnecessary personal identifiers;
- private production logs;
- full sensitive datasets;
- vulnerability details beyond the approved review audience.

Allowed examples must use obvious non-production values.

## Project Template Inheritance

Concrete projects using AI_Development_System inherit this policy as a baseline.

Project-local control files may add stricter privacy or data-handling rules. They must not weaken this baseline without explicit Human Owner approval.

## Review Requirements

Reviewers must check whether a task:

- uses only necessary source documents;
- exposes private or sensitive data;
- sends data to external tools without approval;
- introduces logs or generated artifacts containing sensitive data;
- needs Human Owner approval before continuing.

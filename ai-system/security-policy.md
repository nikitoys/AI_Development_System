# Security Policy

Status: Draft  
Version: v0.1.0

## Purpose

This policy defines the minimum security baseline for AI-assisted work using AI_Development_System, ChatGPT, Codex-like executors, repository automation and external tools.

## Core Rule

Security boundaries are part of task scope.

Codex and AI roles must not access, expose, copy, generate or execute sensitive material unless the task explicitly permits it and the Human Owner has approved the scope.

## Secret Handling

Secrets include:

- API keys;
- tokens;
- passwords;
- private keys;
- session cookies;
- database URLs with credentials;
- production credentials;
- signing keys;
- recovery codes;
- unredacted `.env` values.

Rules:

- Do not paste secrets into prompts, logs, generated documentation or issue text.
- Do not commit secrets or secret-like placeholders with real values.
- Do not invent fake credentials that look usable in production.
- Use redacted examples such as `REDACTED`, `example-token` or documented placeholder syntax.
- If a secret is found, stop repository-affecting work and report the file path and risk without repeating the secret value.
- Secret rotation is a Human Owner decision unless the current task explicitly includes rotation.

## Repository Automation

Automation must not:

- run destructive commands without explicit approval;
- upload repository contents to unapproved services;
- exfiltrate files, logs or environment variables;
- change sandbox or permission boundaries silently;
- bypass Human Owner approval gates.

Automation may:

- run documented local checks;
- inspect files needed for the approved task;
- report security findings with sensitive values redacted.

## Sandbox and Execution Boundaries

Codex-like executors must follow the current task's allowed files, verification mode and forbidden actions.

If a command may read secrets, modify credentials, change deployment state or contact external systems, it requires explicit Human Owner approval unless the task already authorizes that exact action.

## Sensitive Code and Private Repositories

Sensitive code includes proprietary business logic, customer data handling, authentication, authorization, payment flows, security controls and production infrastructure.

Rules:

- Treat sensitive code as confidential by default.
- Summarize sensitive code instead of copying large excerpts into external prompts when possible.
- Do not disclose repository-specific vulnerabilities publicly before Human Owner review.
- Keep security findings concrete enough to fix, but redact exploit details when disclosure would increase risk.

## Security Review

Security review must check:

- secret exposure;
- unsafe command execution;
- permission or sandbox boundary changes;
- authentication and authorization impact;
- data exposure risk;
- external service or LLM disclosure risk;
- whether Human Owner approval is required.

## Incident Handling

If a possible security incident is detected:

1. Stop scope-expanding work.
2. Preserve evidence without copying secret values.
3. Report affected files, commands or workflow steps.
4. Recommend containment and rotation steps.
5. Wait for Human Owner decision before remediation that changes credentials, infrastructure or production state.

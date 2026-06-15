---
name: clarification-gate
description: Use before and during controlled repository tasks when ambiguity, safety risk, owner approval, or missing execution context may block task creation or task execution. Teaches Codex and subagents to inspect first, ask only when blocked, and keep Human Owner decisions explicit.
---

# Clarification Gate Skill

## Purpose

Use this skill when a request may be ambiguous, unsafe, under-scoped, over-broad, or dependent on a Human Owner decision.

The Clarification Gate prevents premature execution. It helps Codex and future subagents decide when to stop and ask the Human Owner, when to inspect the repository or CLI first, and when to proceed with an explicit safe assumption.

This skill is guidance. It does not override source-of-truth documents, task scope, protected-file rules, lifecycle rules, Human Owner decisions, or project-control CLI validation.

## Core Rule

```text
Inspect first.
Ask only when blocked.
Proceed with explicit safe assumptions when ambiguity is non-critical.
Stop for Human Owner decisions when approval, acceptance, destructive action, protected state, architecture, credentials, or scope authority is missing.
```

Codex must not use clarification questions to avoid normal repository inspection. If the answer can be discovered by reading allowed source files, generated control views, CLI help, current state, tests, logs, or existing documentation, inspect first.

Codex must not ask for approval after every small step. Ask only at real decision gates, critical blockers, or owner-only lifecycle transitions.

## Blocker Severity Model

### Critical Blocker

A critical blocker means Codex must stop and ask the Human Owner before proceeding.

Critical blockers include:

- unclear target files where inspection cannot safely identify the intended files;
- destructive changes such as deletion, irreversible migration, history rewrite, broad cleanup, or data loss risk;
- scope expansion beyond the current Task, prompt package, or allowed files;
- protected file edits that would require manual changes to `AI_PROJECT/state/**`, `AI_PROJECT/events/**`, or `AI_PROJECT/generated/**`;
- architecture decisions, API contract changes, workflow changes, lifecycle changes, or rules changes without owner authority;
- approval, acceptance, active, done, or approved-state decisions that represent Human Owner acceptance;
- missing secrets, credentials, tokens, private keys, production access, or other owner-held inputs;
- validation failure where the available fixes imply a policy decision, scope change, owner risk acceptance, or unsupported command;
- conflicting source-of-truth documents where choosing one would change system behavior.

Critical blocker response format:

```text
BLOCKED:
reason: <why execution cannot safely continue>
needed_owner_decision: <specific decision or missing input>
safe_default_if_any: <conservative default, or "none">
work_completed_so_far: <brief status>
```

### Non-Critical Ambiguity

A non-critical ambiguity does not block execution. Codex may proceed with a conservative assumption when:

- the ambiguity does not change scope, architecture, protected files, lifecycle state, owner acceptance, security posture, or public behavior;
- the assumption is reversible;
- the assumption follows existing repository patterns;
- the final report clearly states the assumption.

Use this format in the work log or final report:

```text
Assumption: <what Codex assumed>
Reason: <why this was safe>
Impact: <what changes if the assumption is wrong>
```

### Inspectable Ambiguity

An inspectable ambiguity must be investigated before asking the Human Owner.

Inspect first when the answer may exist in:

- `AGENTS.md`;
- relevant `/ai-system` source documents;
- `AI_PROJECT/generated/**` readable views;
- CLI help from `scripts/planctl.py`, `scripts/taskctl.py`, `scripts/docctl.py`, or `scripts/evolutionctl.py`;
- existing task, plan, documentation, or evolution state read through the CLI;
- local files, tests, logs, or nearby implementation patterns;
- the current git diff.

If inspection resolves the ambiguity, proceed. If inspection exposes a critical blocker, stop and ask.

## Before Task Creation

Ask the Human Owner before creating a Task when:

- the requested outcome is unclear after inspecting available docs and state;
- no safe Initiative or Epic mapping can be identified;
- allowed files cannot be bounded;
- acceptance criteria are missing and cannot be derived without owner intent;
- the request would create, change, approve, or activate AI Development System rules, lifecycle behavior, workflow, roles, prompts, skills, plugins, protected-file policy, or CLI behavior without an approved path;
- the work would require secrets, credentials, production resources, or private external data;
- the request is an Initiative or Epic and has not been decomposed into a bounded executable Task.

Do not ask before task creation when:

- the Human Owner already supplied a bounded task, allowed files, acceptance criteria, and gateway steps;
- the correct Initiative, Epic, or existing Task can be discovered through `planctl.py` or `taskctl.py`;
- missing details can be represented as conservative out-of-scope items;
- the task can be created in a non-acceptance state such as `planned`, `ready`, or `review`.

## During Task Execution

Ask the Human Owner during execution when:

- continuing would require changing files outside the allowed files;
- a required source file is missing and creating an alternative would change scope;
- validation fails and the fix requires owner risk acceptance, new scope, protected state repair, or an unsupported command;
- implementation reveals an architecture, security, privacy, lifecycle, approval, or workflow decision;
- required credentials or external access are missing;
- source documents conflict and the conflict affects behavior, scope, or acceptance;
- the only available path would manually edit protected project-control state, events, or generated output.

Do not ask during execution when:

- a CLI command or source document can answer the question;
- a small wording or formatting choice follows existing style;
- a missing optional detail can be safely omitted and reported;
- validation can be fixed within scope and allowed files;
- the next step is routine inspection, rendering, formatting, or running required checks.

## Question Budget

When a blocker requires Human Owner input:

- group questions into one `Blocker Questions` section;
- ask no more than 3-5 questions unless safety requires more;
- explain why each answer is needed;
- propose a safe default when possible;
- separate owner-only decisions from information Codex can inspect itself.

Question format:

```text
Blocker Questions:
1. <question>
   why_needed: <why this blocks safe execution>
   safe_default: <default if the owner agrees, or "none">
```

## Approval Boundaries

Human Owner approval is required for any lifecycle state that represents owner acceptance, including accepted, approved, active, done, or equivalent states when those states mean the Human Owner accepted direction, quality, completion, release, or system behavior.

Codex may recommend a decision, prepare evidence, move work to review if the CLI and task scope support it, and report suggested commands. Codex must not self-approve results, mark owner acceptance, or treat validation success as owner approval.

## Subagent Use

Subagents may use this skill to decide when to inspect, proceed, or ask for help.

Subagents must still obey:

- Human Owner decisions;
- `AGENTS.md`;
- source-of-truth documents in `/ai-system`;
- generated prompt package scope;
- allowed files and locked files;
- project-control CLI commands;
- protected-file rules;
- review and QA gates.

A subagent must not use this skill as permission to expand scope, bypass the CLI, edit protected state manually, approve work, mark documentation active, or override a parent task.

## Quick Decision Checklist

Before asking:

1. Did I inspect the relevant source documents, CLI help, state, generated views, and nearby files?
2. Is the ambiguity critical, non-critical, or inspectable?
3. Would a safe assumption change scope, architecture, lifecycle, approval, security, or protected state?
4. Can I proceed within allowed files and report the assumption?
5. If blocked, can I ask one grouped set of necessary questions with safe defaults?

If the answer is still owner-only, stop and ask.

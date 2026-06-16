# Agent Delegation

Status: Draft  
Version: v0.1.0

## Purpose

This document defines `Two-Level Delegated Agent Execution` for AI_Development_System.

Two-Level Delegated Agent Execution is a manual L3 mechanism for preparing precise Worker Agent Prompt Packages. It helps Controller Codex hand one bounded work item to a manually started Worker Agent session, then receive and review the returned Agent Result.

This document does not implement runtime behavior.

It does not authorize automatic dispatch, automatic execution, automatic merge, automatic acceptance, automatic QA/review closure or L4 Assisted Execution.

## Governed Concept

The governed concept is manual two-level delegation:

```text
Controller Codex
-> prepares Worker Agent Prompt Package
-> Human Owner or operator manually starts Worker Agent session
-> Worker Agent performs one bounded task
-> Worker Agent returns Agent Result
-> Controller Codex performs intake/review
-> state updates happen only through CLI gateways
```

The two levels are:

1. Controller Codex - the coordinating Codex session that reads state, selects context, prepares the prompt, receives results and routes review.
2. Worker Agent - the manually launched AI session that receives a bounded handoff prompt and returns a structured result.

Controller Codex and Worker Agent are execution responsibilities, not new permanent entries in the AI role registry. A Worker Agent prompt still names the active AI role for the delegated work, such as Technical Writer AI, Code Reviewer AI, QA Engineer AI or System Architect AI.

## Definition

Two-Level Delegated Agent Execution is a manual handoff pattern for L3 work.

It is used when a parent Task or Agent Work Package is clear enough to delegate a narrow piece of work to another AI session, but the system must preserve Human Owner control, source-document boundaries, protected-file rules and manual result intake.

It is not a runtime. It is not a queue. It is not automatic multi-agent execution.

## Relationship To Manual Multi-Agent Orchestration

Manual Multi-Agent Orchestration defines the current L3 mode.

This document adds a concrete L3 prompt-handoff mechanism inside that mode. It preserves the existing L3 rule:

```text
manual handoff only
manual result return
manual intake and review
Human Owner final acceptance
```

Worker Agent sessions are started manually by the Human Owner or operator. Controller Codex must not start them automatically.

## Relationship To Agent Work Package

An Agent Work Package may provide the natural scope for a Worker Agent handoff.

The Worker Agent Prompt Package should preserve:

- parent task;
- Agent Work Package ID when available;
- role;
- scope;
- out of scope;
- allowed files;
- locked files when relevant;
- dependencies;
- acceptance criteria;
- verification mode;
- review instructions;
- forbidden actions.

A Worker Agent Prompt Package must not expand an Agent Work Package or parent Task. If the package is vague, Controller Codex must stop and ask for clarification or narrow the prompt.

## Relationship To Agent Result Intake

Worker Agent output is an Agent Result.

Controller Codex must check returned results against `agent-result-intake.md` before treating them as ready for review, QA, integration review or lifecycle updates.

The result must include enough structure to check:

- scope compliance;
- allowed-file compliance;
- forbidden-action compliance;
- verification evidence;
- risks;
- blockers;
- follow-up recommendations;
- whether Human Owner review is required.

## Relationship To Integration Review

Integration Review is required when multiple Worker Agent results, parallel group results or cross-package outputs must be checked together before QA handoff or parent-task acceptance.

Controller Codex must route to Integration Review when:

- multiple Worker Agent results affect the same parent task;
- results touch shared files or concepts;
- package outputs depend on each other;
- parallel execution policy requires integration review;
- documentation or system behavior could become inconsistent.

Integration Review does not replace Human Owner acceptance.

## Relationship To Parallel Execution Policy

Two-Level Delegated Agent Execution can prepare prompts for work that may be performed in separate manually launched sessions.

Parallel execution remains opt-in and Human Owner-approved.

Candidate parallel groups remain informational until approved under `parallel-execution-policy.md`. The presence of Worker Agent prompts does not approve parallel execution, automatic dispatch or automatic merge.

## Relationship To Runtime Maturity Levels

Current maturity remains:

```text
L3 - Manual multi-agent orchestration
```

Runtime remains:

```text
DEFERRED
```

L4 and higher remain future/not approved.

This document is an L3 refinement only. It does not approve L4 Assisted Execution.

## Relationship To Codex Lifecycle

Controller Codex follows Codex lifecycle rules when it executes repository work or prepares handoff prompts.

Worker Agent results must be reported back to Controller Codex. Controller Codex then handles intake, review routing and project-control updates through the relevant CLI gateways.

Neither Controller Codex nor Worker Agent may approve final results on behalf of the Human Owner unless an explicit Human Owner decision has been recorded and the relevant CLI path supports the state update.

## Relationship To Task Lifecycle

A Worker Agent prompt must be tied to one bounded Task or one bounded Agent Work Package under a Task.

Task state remains controlled by `taskctl.py`.

Controller Codex may update task lifecycle state only through `taskctl.py` and only when the task scope, review state and Human Owner approval allow it.

Worker Agent must not mark tasks done.

## Relationship To Documentation Navigation Skill

Controller Codex must use the Documentation Navigation Skill to choose the minimal read set for the Worker Agent prompt.

Worker Agent prompts should include only necessary source documents. They should not dump the whole repository or ask the Worker Agent to infer scope from broad context.

If the Worker Agent needs more context, it should report the missing source and reason rather than expanding scope silently.

## Controller Codex Responsibilities

Controller Codex is responsible for:

- reading project-control state and source documents;
- selecting the minimal source context;
- checking that the parent Task or Agent Work Package is bounded;
- preparing the Worker Agent Prompt Package;
- stating scope, out of scope, allowed files and forbidden actions;
- requiring structured result output;
- receiving the Worker Agent Result;
- performing Agent Result Intake;
- routing Integration Review, review or QA when needed;
- updating lifecycle state only through CLI gateways;
- preserving Human Owner approval boundaries.

Controller Codex must not:

- launch Worker Agent sessions automatically;
- approve Worker Agent output automatically;
- accept final task results for the Human Owner;
- edit protected `AI_PROJECT` files manually;
- imply that L4 or runtime behavior is approved;
- widen Worker Agent scope after the handoff without owner-controlled task updates.

## Worker Agent Responsibilities

Worker Agent is responsible for:

- reading only the specified minimal docs unless blocked;
- performing one bounded task;
- staying inside scope and allowed files;
- avoiding out-of-scope work;
- avoiding all forbidden actions;
- reporting verification performed and skipped checks;
- reporting blockers, questions, risks and follow-up recommendations;
- returning a structured Agent Result to Controller Codex.

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
- perform automatic dispatch.

## Delegation Lifecycle

## 1. Candidate Selection

Controller Codex identifies whether a Task or Agent Work Package is suitable for delegation.

Delegation is suitable when:

- scope is narrow;
- allowed files are explicit;
- acceptance criteria are clear;
- source documents are known;
- Worker Agent output can be reviewed;
- no Human Owner decision is required before starting.

Delegation is not suitable when the task is vague, cross-cutting, owner-decision-heavy or dependent on protected-file mutation.

## 2. Source Context Selection

Controller Codex uses the Documentation Navigation Skill to choose the minimal read set.

The read set should include:

- `AGENTS.md` when repository rules matter;
- relevant `/ai-system` source documents;
- parent Task or Agent Work Package context;
- only the source files needed for the work.

Generated project-control files may be included as readable state views, but they must not be presented as editable source.

## 3. Worker Prompt Package Creation

Controller Codex creates a Worker Agent Prompt Package using `ai-system/templates/agent-worker-prompt.md` or an equivalent structure.

The prompt must make the Worker Agent's role, scope, files, forbidden actions, verification and result format explicit.

## 4. Manual Handoff

The Human Owner or operator manually starts the Worker Agent session and provides the prompt.

Controller Codex must not dispatch the Worker Agent automatically.

## 5. Worker Execution

The Worker Agent performs only the bounded task.

If scope, source documents, allowed files, credentials, security/privacy handling or owner decisions are unclear, the Worker Agent stops and returns a blocker.

## 6. Worker Result Return

The Worker Agent returns a structured Agent Result to Controller Codex.

The result should include changed files, commands run, verification result, questions, blockers, risks and follow-up recommendations.

## 7. Controller Intake

Controller Codex checks the result against:

- the Worker Agent Prompt Package;
- parent Task or Agent Work Package;
- allowed files and forbidden actions;
- requested verification;
- `agent-result-intake.md`;
- security and privacy boundaries.

If intake fails, Controller Codex routes to rework, rejection or blocker handling.

## 8. Review / QA Routing

Controller Codex routes the result to review, QA or Integration Review when required.

Review and QA recommendations do not replace Human Owner acceptance.

## 9. Human Owner Acceptance

Human Owner accepts, rejects, defers or requests rework for final task outcomes and residual risk.

Controller Codex may record the decision only through allowed CLI gateways.

## 10. Learning / Follow-Up

Controller Codex records follow-up tasks, improvement ideas or evolution changes only through approved channels.

Recurring prompt weaknesses may be routed to skills, templates or prompt lifecycle updates through controlled evolution.

## Required Worker Prompt Package Fields

Every Worker Agent Prompt Package must include:

- mode marker;
- Worker Agent role;
- active stage;
- active document;
- expected result;
- repository context;
- minimal read set;
- task summary;
- scope;
- out of scope;
- allowed files;
- forbidden actions;
- verification instructions;
- result format;
- return instructions.

Recommended fields:

- parent Task ID;
- Agent Work Package ID when available;
- dependencies;
- locked files;
- verification mode;
- security/privacy notes;
- stop conditions.

## Required Worker Agent Result Fields

Every Worker Agent Result should include:

- summary;
- changed files;
- commands run;
- verification result;
- questions;
- blockers;
- risks;
- follow-up recommendations.

For managed Agent Work Package results, use the hardened Agent Result fields from `agent-result-intake.md`.

## Safety Boundaries

Two-Level Delegated Agent Execution must preserve these boundaries:

- L3 manual delegation only;
- runtime remains deferred;
- L4+ remains future/not approved;
- no automatic Worker Agent dispatch;
- no automatic Codex execution;
- no automatic branch/worktree lifecycle;
- no automatic commit, push, merge or pull request creation;
- no automatic acceptance;
- no automatic review or QA closure;
- no manual edits to protected root `AI_PROJECT` state, events or generated files;
- Worker Agent output must be reviewed before lifecycle closure.

## Stop Conditions

Controller Codex or Worker Agent must stop when:

- scope is unclear;
- allowed files are missing or too broad;
- source-of-truth document is unclear;
- a Human Owner decision is required;
- protected-file mutation would be required;
- automatic dispatch or runtime behavior would be required;
- credentials, secrets or private data are required and not approved;
- verification cannot be performed and no acceptable limitation is documented;
- a result violates scope, allowed files or forbidden actions.

## Examples

## Documentation Worker

Use a Documentation Worker when a bounded documentation update can be isolated to specific files.

Example scope:

- read `ai-system/document-lifecycle.md`;
- update one documentation source file;
- return changed files and documentation checks.

The Documentation Worker must not update `AI_PROJECT/generated/**` manually or mark documents active.

## Reviewer Worker

Use a Reviewer Worker when a completed result needs an independent review against task scope.

Example scope:

- read the Task, changed files and review process;
- identify Critical, Major, Minor and Suggestion findings;
- return a review report.

The Reviewer Worker must not accept the result for the Human Owner.

## QA Worker

Use a QA Worker when acceptance criteria need verification evidence.

Example scope:

- read the Task, verification mode and result report;
- run or inspect requested checks;
- report passed, failed and skipped checks.

The QA Worker must not close QA or mark the Task done.

## System Architect Worker

Use a System Architect Worker when a bounded architecture or process consistency check is needed.

Example scope:

- read the source document and related lifecycle boundaries;
- check consistency with system structure and operating model;
- report risks and needed rework.

The System Architect Worker must not change architecture, workflow or runtime maturity without an approved evolution task.

## Boundary Statement

This is L3 manual delegation only.

It does not approve L4 Assisted Execution.

It does not implement runtime behavior, automatic Worker Agent launch, automatic Codex execution, automatic merge, automatic acceptance or automatic review/QA closure.

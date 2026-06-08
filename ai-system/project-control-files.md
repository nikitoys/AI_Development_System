# Project Control Files

Status: Draft
Version: v0.1.0

## Purpose

This document defines the standard set of project-level control files used by concrete repositories that adopt the AI Development System.

AI_Development_System provides the global operating model, lifecycle rules and reusable templates. A concrete project repository stores local project control files that describe the project goal, local workflow, current task state, backlog, reusable prompts and verification policy.

## Governed Entity

A project control file is a local source-of-truth file inside a concrete project repository that guides Human Owner, ChatGPT Orchestrator, Codex Executor and AI roles while working on that project.

Project control files are not application code. They define how work is controlled, not the product implementation itself.

## Source of Truth

Default source-of-truth documents for project control files are:

- `/ai-system/project-control-files.md` for the standard file set and authority rules;
- `/ai-system/project-bootstrap.md` for initialization workflow;
- `/ai-system/verification-modes.md` for verification modes;
- `/ai-system/prompt-lifecycle.md` for prompt package requirements;
- `/ai-system/task-format.md` for task shape and acceptance criteria;
- `/ai-system/rules.md` for global safety rules;
- project-local control files for project-specific decisions and constraints.

## Authority and Precedence

For a concrete project repository, authority is resolved in this order:

1. Explicit Human Owner instruction for the current task.
2. Current approved task, prompt package or decision record.
3. Project-local control files.
4. Project-local `docs/verification-policy.md`.
5. Global AI Development System rules in `/ai-system`.
6. Templates used only as bootstrap starting points.

Local project rules may narrow or specialize global defaults. They must not weaken Human Owner approval rules, lifecycle governance, safety boundaries or explicit forbidden actions from the AI Development System.

If a local project rule conflicts with a global system rule, the conflict must be reported before execution unless the global rule explicitly allows local override.

## Required Project Control Files

Concrete project repositories should contain these required control files:

```text
AGENTS.md
PROJECT_GOAL.md
CODEX_COMMANDS.md
CODEX_WORKFLOW.md
OWNER_PLAN.md
CODEX_PLAN.md
CODEX_CURRENT.md
CODEX_TASKS.md
CODEX_SESSION_LOG.md
PROMPTS.md
docs/verification-policy.md
```

## File Responsibilities

| File | Purpose | Read When | Updated By |
|---|---|---|---|
| `AGENTS.md` | Local AI instructions, Start Here list, repository-specific rules and required reading order. | First file for every AI or Codex session in the project. | Human Owner, ChatGPT Orchestrator, AI System Maintainer or Technical Writer AI with approval. |
| `PROJECT_GOAL.md` | Mission, constraints, non-goals, target app directory and success criteria. | Before planning, implementation, review or scope decisions. | Human Owner, Product Manager AI or Technical Writer AI with approval. |
| `CODEX_COMMANDS.md` | Short Human Owner command cheat sheet and command-to-workflow mappings. | When interpreting operator commands. | Human Owner, Project Manager AI or AI System Maintainer with approval. |
| `CODEX_WORKFLOW.md` | Local Codex execution workflow, gates, result format and check policy. | Before preparing or executing Codex tasks. | AI System Maintainer or Technical Writer AI with approval. |
| `OWNER_PLAN.md` | Human Owner-authored external plan, roadmap, priorities and desired work. Planning input only, not executable scope. | During plan intake, backlog refresh, project audit and task discovery. | Human Owner; ChatGPT Orchestrator or Project Manager AI may summarize or convert into task proposals with approval. |
| `CODEX_PLAN.md` | Planning snapshot, milestones and nearest valuable tasks. | During planning and task selection. | Project Manager AI, Product Manager AI or Human Owner. |
| `CODEX_CURRENT.md` | Current approved, stopped, cancelled or idle task state. | Before starting or resuming work. | Human Owner, ChatGPT Orchestrator or Codex Executor through approved task flow. |
| `CODEX_TASKS.md` | Compact backlog or project board with task IDs, states and acceptance notes. | Before selecting or creating implementation tasks. | Project Manager AI, ChatGPT Orchestrator or Human Owner. |
| `CODEX_SESSION_LOG.md` | Journal of Codex task cycles, results, checks, errors and decisions. | During review, audit, handoff and continuation. | Codex Executor for reports; ChatGPT Orchestrator or reviewer for summaries. |
| `PROMPTS.md` | Reusable project prompts and prompt fragments. | When preparing repeated project work. | ChatGPT Orchestrator, Technical Writer AI or Human Owner. |
| `docs/verification-policy.md` | Local verification mode policy and allowed checks. | Before running checks, QA, browser sessions or visual validation. | QA Engineer AI, AI System Maintainer or Human Owner with approval. |

## Target App Directory Rule

If application code lives in a subfolder, the target application directory must be recorded in `PROJECT_GOAL.md` and referenced from `AGENTS.md` and `CODEX_WORKFLOW.md`.

Example:

```text
Target App Directory: apps/web
```

Codex must not assume the repository root is the application root when a target app directory is declared.

## Read Order for AI and Codex Sessions

A new project session should read files in this order:

1. `AGENTS.md`
2. `PROJECT_GOAL.md`
3. `OWNER_PLAN.md` when present or when doing plan intake
4. `docs/verification-policy.md`
5. `CODEX_WORKFLOW.md`
6. `CODEX_CURRENT.md`
7. `CODEX_TASKS.md`
8. `CODEX_PLAN.md`
9. `CODEX_COMMANDS.md`
10. `PROMPTS.md` when reusable prompts are needed
11. `CODEX_SESSION_LOG.md` when continuing or reviewing prior work

## Template Relationship

AI_Development_System provides reusable templates for project control files under:

```text
/ai-system/templates/project/
```

Templates are bootstrap artifacts. After copied into a project repository, the local files become the project source of truth.

Templates should use placeholders such as:

```text
{{PROJECT_NAME}}
{{TARGET_APP_DIRECTORY}}
{{DEFAULT_VERIFICATION_MODE}}
{{HUMAN_OWNER_LANGUAGE}}
```

## Owner Plan Intake Rule

`OWNER_PLAN.md` may contain broad, incomplete or informal Human Owner plans. It is an input document, not direct implementation permission.

Before Codex implements anything from `OWNER_PLAN.md`, ChatGPT Orchestrator or Project Manager AI must convert relevant plan items into `CODEX_PLAN.md`, `CODEX_TASKS.md` or `CODEX_CURRENT.md` entries with scope, allowed files, verification mode and acceptance criteria.

Plan intake should classify items as:

```text
Already Done
Partially Done
Missing
Unclear
Out of Scope
Recommended Next Tasks
```

## Optional Project Control Files

Projects may add more local control files when needed, for example:

```text
docs/architecture.md
docs/decisions.md
docs/release-policy.md
docs/security-policy.md
```

Optional files must be referenced from `AGENTS.md` or another required control file when they affect execution.

## Boundary Rules

Project control files must not be used to bypass Human Owner approval.

Project control files must not silently expand implementation scope.

Project control files must not authorize Codex to modify application code during bootstrap unless the Human Owner explicitly approves application changes.

Local project rules may restrict global defaults, but they must not weaken safety, approval or lifecycle governance rules.

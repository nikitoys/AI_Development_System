# Project Control Files

Status: Draft
Version: v0.2.0

## Purpose

This document defines the standard set of project-level control files used by concrete repositories that adopt the AI Development System.

AI_Development_System provides the global operating model, lifecycle rules and reusable templates. A concrete project repository stores local project control files that describe the project goal, local workflow, current task state, backlog, reusable prompts and verification policy.

## Integration Modes

AI_Development_System supports two project integration modes.

## Foldered Control Mode

Recommended default for new projects.

```text
/project-root
├── AGENTS.md
├── AI_Development_System/
├── AI_PROJECT/
└── <target-app-directory>/
```

Responsibilities:

- `AGENTS.md` is a small root bootstrap/router file.
- `AI_Development_System/` stores the reusable upstream AI Development System copy.
- `AI_PROJECT/` stores local project control files and project-specific state.
- `<target-app-directory>/` stores application or product code.

Foldered Control Mode is preferred because it makes updates easier, reduces root clutter and keeps system, project control and application code boundaries explicit.

## Root Control Mode

Supported for small or legacy projects.

In Root Control Mode, project control files live directly in the repository root.

Root Control Mode remains valid, but new projects should use Foldered Control Mode unless the Human Owner explicitly chooses otherwise.

## Governed Entity

A project control file is a local source-of-truth file inside a concrete project repository that guides Human Owner, ChatGPT Orchestrator, Codex Executor and AI roles while working on that project.

Project control files are not application code. They define how work is controlled, not the product implementation itself.

## Source of Truth

Default source-of-truth documents for project control files are:

- `/ai-system/project-integration-model.md` for integration modes and directory boundaries;
- `/ai-system/project-control-files.md` for the standard file set and authority rules;
- `/ai-system/project-bootstrap.md` for initialization workflow;
- `/ai-system/project-system-update.md` for updating already integrated projects;
- `/ai-system/project-operation-profile.md` for surface-level project behavior defaults;
- `/ai-system/verification-modes.md` for verification modes;
- `/ai-system/prompt-lifecycle.md` for prompt package requirements;
- `/ai-system/task-format.md` for task shape and acceptance criteria;
- `/ai-system/rules.md` for global safety rules;
- project-local control files for project-specific decisions and constraints.

## Authority and Precedence

For a concrete project in Foldered Control Mode, authority is resolved in this order:

1. Explicit Human Owner instruction for the current task.
2. Current approved task, prompt package or decision record.
3. `AI_PROJECT/PROJECT_OPERATION_PROFILE.md`.
4. Specialized `AI_PROJECT/` local control files.
5. `AI_PROJECT/docs/verification-policy.md`.
6. Root `AGENTS.md` boundary rules.
7. Global AI Development System rules in `AI_Development_System/ai-system`.
8. Templates used only as bootstrap starting points.

For Root Control Mode, root-local control files take the place of `AI_PROJECT/` files.

Local project rules may narrow or specialize global defaults. They must not weaken Human Owner approval rules, lifecycle governance, safety boundaries or explicit forbidden actions from the AI Development System.

If a local project rule conflicts with a global system rule, the conflict must be reported before execution unless the global rule explicitly allows local override.

## Required Project Control Files

In Foldered Control Mode, concrete project repositories should contain:

```text
AGENTS.md
AI_Development_System/
AI_PROJECT/AGENTS.md
AI_PROJECT/PROJECT_OPERATION_PROFILE.md
AI_PROJECT/PROJECT_GOAL.md
AI_PROJECT/OWNER_PLAN.md
AI_PROJECT/CODEX_COMMANDS.md
AI_PROJECT/CODEX_WORKFLOW.md
AI_PROJECT/CODEX_PLAN.md
AI_PROJECT/CODEX_CURRENT.md
AI_PROJECT/CODEX_TASKS.md
AI_PROJECT/CODEX_SESSION_LOG.md
AI_PROJECT/PROMPTS.md
AI_PROJECT/AGENT_PLAN.md
AI_PROJECT/AGENT_TASKS.md
AI_PROJECT/AGENT_ASSIGNMENTS.md
AI_PROJECT/AGENT_LOCKS.md
AI_PROJECT/AGENT_RESULTS.md
AI_PROJECT/AGENT_METRICS.md
AI_PROJECT/AI_DEV_SYSTEM_VERSION.md
AI_PROJECT/docs/verification-policy.md
```

In Root Control Mode, equivalent files may live in the repository root:

```text
AGENTS.md
PROJECT_OPERATION_PROFILE.md
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
| `AGENTS.md` | Root bootstrap/router and repository boundary instructions. | First file for every AI or Codex session in the project. | Human Owner, ChatGPT Orchestrator, AI System Maintainer or Technical Writer AI with approval. |
| `AI_PROJECT/AGENTS.md` | Local AI instructions, Start Here list and project-specific rules. | After root `AGENTS.md`. | Human Owner, ChatGPT Orchestrator, AI System Maintainer or Technical Writer AI with approval. |
| `AI_PROJECT/PROJECT_OPERATION_PROFILE.md` | Surface-level AI Dev System behavior defaults for language, verification, permissions, layout and review expectations. | Immediately after `AI_PROJECT/AGENTS.md`, before lower-level project control files. | Human Owner directly; ChatGPT Orchestrator, AI System Maintainer or Technical Writer AI with approval. |
| `AI_PROJECT/PROJECT_GOAL.md` | Mission, constraints, non-goals, target app directory and success criteria. | Before planning, implementation, review or scope decisions. | Human Owner, Product Manager AI or Technical Writer AI with approval. |
| `AI_PROJECT/OWNER_PLAN.md` | Human Owner-authored external plan, roadmap, priorities and desired work. Planning input only, not executable scope. | During plan intake, backlog refresh, project audit and task discovery. | Human Owner; ChatGPT Orchestrator or Project Manager AI may summarize or convert into task proposals with approval. |
| `AI_PROJECT/CODEX_COMMANDS.md` | Short Human Owner command cheat sheet and command-to-workflow mappings. | When interpreting operator commands. | Human Owner, Project Manager AI or AI System Maintainer with approval. |
| `AI_PROJECT/CODEX_WORKFLOW.md` | Local Codex execution workflow, gates, result format and check policy. | Before preparing or executing Codex tasks. | AI System Maintainer or Technical Writer AI with approval. |
| `AI_PROJECT/CODEX_PLAN.md` | Planning snapshot, milestones and nearest valuable tasks. | During planning and task selection. | Project Manager AI, Product Manager AI or Human Owner. |
| `AI_PROJECT/CODEX_CURRENT.md` | Current approved, stopped, cancelled or idle task state. | Before starting or resuming work. | Human Owner, ChatGPT Orchestrator or Codex Executor through approved task flow. |
| `AI_PROJECT/CODEX_TASKS.md` | Compact backlog or project board with task IDs, states and acceptance notes. | Before selecting or creating implementation tasks. | Project Manager AI, ChatGPT Orchestrator or Human Owner. |
| `AI_PROJECT/CODEX_SESSION_LOG.md` | Journal of Codex task cycles, results, checks, errors and decisions. | During review, audit, handoff and continuation. | Codex Executor for reports; ChatGPT Orchestrator or reviewer for summaries. |
| `AI_PROJECT/PROMPTS.md` | Reusable project prompts and prompt fragments. | When preparing repeated project work. | ChatGPT Orchestrator, Technical Writer AI or Human Owner. |
| `AI_PROJECT/AGENT_PLAN.md` | SOP-guided agent planning snapshot, decomposition assumptions, candidate sequential/parallel groups and approval status. | During multi-agent planning and before preparing Agent Work Packages. | Project Manager AI, ChatGPT Orchestrator or Human Owner with approval. |
| `AI_PROJECT/AGENT_TASKS.md` | Agent Work Package registry. Planning only, not execution authority. | Before preparing package-level prompts or reviewing planned decomposition. | Project Manager AI, ChatGPT Orchestrator or Human Owner with approval. |
| `AI_PROJECT/AGENT_ASSIGNMENTS.md` | Manual Role-to-Agent Assignment registry for L3 orchestration. Coordination only, not automatic dispatch. | After ready Agent Work Packages are identified and before manual agent sessions are run. | ChatGPT Orchestrator or Human Owner with approval. |
| `AI_PROJECT/AGENT_LOCKS.md` | File-scope and locked-file planning registry for Agent Work Packages. | Before dependency, conflict or parallel eligibility checks. | Project Manager AI, Code Reviewer AI, QA Engineer AI or Human Owner with approval. |
| `AI_PROJECT/AGENT_RESULTS.md` | Agent Result intake log and integration review status references. | During result intake, integration review and QA handoff. | ChatGPT Orchestrator, Code Reviewer AI, QA Engineer AI or Technical Writer AI with approval. |
| `AI_PROJECT/AGENT_METRICS.md` | Lightweight planning, execution, review and QA metrics for pilot validation and lessons learned. | During pilot validation, review and process improvement. | Project Manager AI, QA Engineer AI, AI System Maintainer or Human Owner. |
| `AI_PROJECT/AI_DEV_SYSTEM_VERSION.md` | Local record of installed AI_Development_System source, version, branch, commit and update method. | During system update, audit and migration. | AI System Maintainer or Human Owner with approval. |
| `AI_PROJECT/docs/verification-policy.md` | Local verification mode policy and allowed checks. | Before running checks, QA, browser sessions or visual validation. | QA Engineer AI, AI System Maintainer or Human Owner with approval. |

Root Control Mode uses the same responsibilities with paths adjusted to the root.

## Target App Directory Rule

If application code lives in a subfolder, the target application directory must be recorded in `AI_PROJECT/PROJECT_GOAL.md` and referenced from root `AGENTS.md` and `AI_PROJECT/CODEX_WORKFLOW.md`.

Example:

```text
Target App Directory: voxel-adventure-mvp
```

Codex must not assume the repository root is the application root when a target app directory is declared.

## Read Order for AI and Codex Sessions

A new project session in Foldered Control Mode should read files in this order:

1. `AGENTS.md`
2. `AI_PROJECT/AGENTS.md`
3. `AI_PROJECT/PROJECT_OPERATION_PROFILE.md`
4. `AI_PROJECT/PROJECT_GOAL.md`
5. `AI_PROJECT/OWNER_PLAN.md` when present or when doing plan intake
6. `AI_PROJECT/docs/verification-policy.md`
7. `AI_PROJECT/CODEX_WORKFLOW.md`
8. `AI_PROJECT/CODEX_CURRENT.md`
9. `AI_PROJECT/CODEX_TASKS.md`
10. `AI_PROJECT/CODEX_PLAN.md`
11. `AI_PROJECT/CODEX_COMMANDS.md`
12. `AI_PROJECT/PROMPTS.md` when reusable prompts are needed
13. `AI_PROJECT/CODEX_SESSION_LOG.md` when continuing or reviewing prior work
14. `AI_Development_System/AGENTS.md` and relevant `/AI_Development_System/ai-system` source documents when system rules are needed

## Template Relationship

AI_Development_System provides reusable templates for project control files under:

```text
/ai-system/templates/foldered/
/ai-system/templates/project/
```

`templates/foldered` is recommended for new projects.

`templates/project` remains available for Root Control Mode and compatibility.

Templates are bootstrap artifacts. After copied into a project repository, the local files become the project source of truth.

Templates should use placeholders such as:

```text
{{PROJECT_NAME}}
{{TARGET_APP_DIRECTORY}}
{{DEFAULT_VERIFICATION_MODE}}
{{DEFAULT_VERIFICATION_BUDGET}}
{{HUMAN_OWNER_LANGUAGE}}
{{AI_DEV_SYSTEM_SOURCE_BRANCH}}
{{AI_DEV_SYSTEM_SOURCE_COMMIT}}
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

## Boundary Rules

Project control files must not be used to bypass Human Owner approval.

Project control files must not silently expand implementation scope.

Project control files must not authorize Codex to modify application code during bootstrap unless the Human Owner explicitly approves application changes.

Agent planning and assignment files must not authorize execution, parallel execution, automatic execution, automatic dispatch, automatic merge or automatic acceptance.

The minimal `scripts/agent-plan-mvp.py` helper may read `AI_PROJECT/AGENT_*` files to report missing files, recognizable Agent Work Packages, locked-file conflicts, informational candidate parallel groups and prompt drafts. `AGENT_ASSIGNMENTS.md` records manual L3 coordination and must not be treated as automatic dispatch authority. The helper must not modify project files, execute Codex, create branches, merge changes or accept results.

Updating `AI_Development_System/` must not overwrite `AI_PROJECT/`.

Local project rules may restrict global defaults, but they must not weaken safety, approval or lifecycle governance rules.

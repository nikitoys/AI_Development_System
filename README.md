# AI Development System

Languages: [English](README.md) | [Русский](README.ru.md)

Status: Draft
Version: v0.51.0

This repository contains an AI Development System: an operating model for developing projects through AI roles, documentation, lifecycle governance, prompt generation, Codex execution, review and controlled evolution.

It is not a normal application repository. The primary source of truth for system behavior is `/ai-system`.

This repository now intentionally uses root-level `/AI_PROJECT` as its self-hosted Project Control Layer. It stores machine-readable state, append-only audit events and generated readable outputs for AI_Development_System's own controlled evolution. Protected files under `/AI_PROJECT/state/**`, `/AI_PROJECT/events/**` and `/AI_PROJECT/generated/**` must be changed only through the project-control CLI gateways.

Owner quickstart for the centralized control plane:

```bash
python scripts/aictl.py command list
python scripts/aictl.py workflow list
python scripts/aictl.py project doctor
python scripts/aictl.py web --host 127.0.0.1 --port 8765
```

Use `/ai-system/project-control/10-owner-quickstart.md` for the practical command guide and `/ai-system/project-control/08-usage-guide.md` for the full Project Control Gateway usage guide.

`AI_PROJECT` appears in three distinct contexts:

- `/AI_PROJECT` — the self-hosted project-control layer for this repository itself.
- `/ai-system/templates/**/AI_PROJECT` — reusable project-control templates for external projects.
- `/examples/golden-project/AI_PROJECT` — a non-runtime reference example for onboarding and validation.

Version source: the current AI_Development_System version is the top entry in `/ai-system/system-changelog.md`. README files mirror that version and must not claim a newer or different version.

Documentation integrity checks can be run with:

```bash
python3 scripts/check-docs-integrity.py
```

Full read-only system validation can be run locally with:

```bash
python3 scripts/validate-system.py
```

Security and privacy baselines are defined in `/ai-system/security-policy.md` and `/ai-system/privacy-data-handling-policy.md`.

Machine-checkable specs for stable system entities are stored in `/spec`.

SOP and agent planning specs are derived machine-checkable inventory/contract files. Markdown remains the operational source of truth, and specs do not authorize runtime behavior, automatic execution, merge or acceptance.

Minimal foldered bootstrap/update dry-runs can be run with `scripts/foldered-control-mvp.py`.

Dry-run agent planning checks can be run with `scripts/agent-plan-mvp.py`.

Lightweight verification check selection can be run with `scripts/verification/run_checks.py`. The runner supports dry-run, explicit budgets, per-check timeouts and local JSONL runtime history.

`AI_PROJECT/PROJECT_OPERATION_PROFILE.md` provides surface-level project behavior defaults for language, answer style, verification, permissions, layout and review expectations.

`AI_PROJECT/PROJECT_CONTROL_INDEX.md` provides a compact read-order map so agents can discover project control files by importance without loading every document by default.

The Work Item Hierarchy is defined in `/ai-system/work-item-hierarchy.md`: Goal -> Initiative -> Epic -> Task -> Agent Work Package. Initiative and Epic are planning containers only; Task remains the executable unit.

The SOP and optional multi-agent implementation plan is recorded in `/ai-system/evolution/sop-multi-agent-implementation-plan.md`.

Earlier L4 Assisted SOP Execution planning records live under `/ai-system/evolution/current-evolution-task.md`, `/ai-system/evolution/l4-assisted-sop-execution-plan.md` and `/ai-system/evolution/l4-assisted-sop-execution-tasks.md`. The approved L4 target architecture is now `/ai-system/l4-role-agent-runtime.md`.

L4 Role-Agent Runtime is an approved bounded implementation target. It keeps Python as the strict API/control kernel, Controller Codex as planner/router/delegator/integrator, Codex role subagents as bounded executors of existing AI roles and Human Owner as final acceptance authority. It does not implement `scripts/agentctl.py`, approve L5, or authorize automatic merge, push, pull request creation, task acceptance or QA/review closure.

The legacy conceptual baseline for early system evolution is archived at `/ai-system/evolution/concept-baseline.md`; it is historical context only and not the current source of truth.

The SOP Model is defined in `/ai-system/sop-model.md`. SOPs are governance procedures only; they do not authorize automatic execution or automatic acceptance.

The Agent Work Package standard is defined in `/ai-system/agent-work-package.md`. Agent Work Packages are bounded planning artifacts and do not imply parallel execution.

The Multi-Agent Planning workflow is defined in `/ai-system/multi-agent-planning.md`. It is planning-only and does not authorize execution or parallel execution.

The Parallel Execution Policy is defined in `/ai-system/parallel-execution-policy.md`. Parallel execution is opt-in, Human Owner-approved and does not authorize automatic execution, merge or acceptance.

Agent Result Intake and Integration Review are defined in `/ai-system/agent-result-intake.md` and `/ai-system/integration-review.md`. They check results before review, QA and Human Owner acceptance without authorizing automatic execution, merge or acceptance.

Foldered `AI_PROJECT` templates now include agent planning files for plans, packages, assignments, locks, results and metrics. These are planning and manual coordination records only and do not authorize execution, parallel execution, merge or acceptance. They are reusable templates, distinct from this repository's root `/AI_PROJECT` self-hosted control state.

The golden project includes a filled non-runtime multi-agent planning example for Task Tracker under `examples/golden-project/`.

The SOP / optional multi-agent pilot validation record is stored in `/ai-system/evolution/sop-multi-agent-pilot-validation.md`.

Expanded pilot validation evidence covers documentation-only, small tooling/code and multi-agent parallel planning scenarios while preserving dry-run boundaries.

Runtime maturity levels are defined in `/ai-system/runtime-maturity-levels.md`. Current implementation maturity is `L3 — Manual multi-agent orchestration`; next approved implementation target is `L4 — Role-Agent Runtime`; `L5+` remains future/not approved.

Manual Multi-Agent Orchestration Mode is defined in `/ai-system/manual-orchestration.md`. L3 is manual-only and does not authorize automatic execution, merge or acceptance.

Role-to-Agent Assignment is defined in `/ai-system/role-agent-assignment.md`. Assignments map ready Agent Work Packages to logical agents or external sessions manually and do not authorize automatic dispatch or runtime execution.

Agent Delegation is defined in `/ai-system/agent-delegation.md`. Controller Codex may prepare precise Worker Agent Prompt Packages for manual handoff, but the Human Owner or operator manually launches Worker Agent sessions and results still go through intake, review and Human Owner control.

The L3 role-assigned parallel runbook is defined in `/ai-system/l3-role-assigned-parallel-runbook.md`.

## At a Glance

This repository describes a documented AI-assisted development system:

```text
Human Owner sets direction and approves decisions.
ChatGPT Orchestrator routes work, prepares prompts and reviews results.
AI Roles specialize by responsibility.
Codex Executor changes repository files only inside approved scope.
Documentation stores rules, decisions, lifecycles and history.
```

## Recommended Project Integration

For concrete projects, use Foldered Control Mode:

```text
/project-root
├── AGENTS.md
├── AI_Development_System/
├── AI_PROJECT/
└── <target-app-directory>/
```

- `AGENTS.md` is a small root bootstrap/router file.
- `AI_Development_System/` is the reusable upstream system copy.
- `AI_PROJECT/` stores local project control files and project state.
- `<target-app-directory>/` stores application or product code.

This model keeps updates easier and prevents system files, project control files and application code from being mixed.

## Quick Start

### Install into a Project

Recommended vendor-copy install:

```bash
git clone --depth 1 --branch ai-development-system https://github.com/nikitoys/AI_Development_System.git AI_Development_System
rm -rf AI_Development_System/.git
mkdir -p AI_PROJECT
cp -R AI_Development_System/ai-system/templates/foldered/AI_PROJECT/. AI_PROJECT/
cp AI_Development_System/ai-system/templates/foldered/AGENTS.root.md AGENTS.md
```

Alternative Git-managed install with subtree:

```bash
git subtree add \
  --prefix=AI_Development_System \
  https://github.com/nikitoys/AI_Development_System.git \
  ai-development-system \
  --squash
mkdir -p AI_PROJECT
cp -R AI_Development_System/ai-system/templates/foldered/AI_PROJECT/. AI_PROJECT/
cp AI_Development_System/ai-system/templates/foldered/AGENTS.root.md AGENTS.md
```

Then edit generated files and replace placeholders such as:

```text
{{PROJECT_NAME}}
{{TARGET_APP_DIRECTORY}}
{{DEFAULT_VERIFICATION_MODE}}
{{DEFAULT_VERIFICATION_BUDGET}}
{{HUMAN_OWNER_LANGUAGE}}
{{ANSWER_DETAIL_LEVEL}}
{{PROMPT_LANGUAGE}}
{{AI_DEV_SYSTEM_SOURCE_BRANCH}}
{{AI_DEV_SYSTEM_SOURCE_COMMIT}}
```

A foldered project should have:

```text
AGENTS.md
AI_Development_System/
AI_PROJECT/AGENTS.md
AI_PROJECT/PROJECT_CONTROL_INDEX.md
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
AI_PROJECT/AI_DEV_SYSTEM_VERSION.md
AI_PROJECT/docs/verification-policy.md
```

For onboarding, a concrete Task Tracker example is available at:

- `examples/golden-project/` — a fully filled foldered control-layer example without product code.

Minimal dry-run bootstrap helper:

```bash
python3 scripts/foldered-control-mvp.py bootstrap --project-root /path/to/project
```

Minimal dry-run update helper:

```bash
python3 scripts/foldered-control-mvp.py update --project-root /path/to/project
```

For an existing repository, bootstrap must create or adapt control files only. It must not rewrite, refactor or move application code unless the Human Owner explicitly approves a separate implementation task.

### Update an Existing Project

If the project uses vendor copy:

```bash
rm -rf AI_Development_System
git clone --depth 1 --branch ai-development-system https://github.com/nikitoys/AI_Development_System.git AI_Development_System
rm -rf AI_Development_System/.git
```

If the project uses subtree:

```bash
git subtree pull \
  --prefix=AI_Development_System \
  https://github.com/nikitoys/AI_Development_System.git \
  ai-development-system \
  --squash
```

Then run a controlled project system update:

```text
read local AI_PROJECT control files
-> compare with the current AI_Development_System standard and templates
-> add missing files
-> merge new rules into existing files
-> preserve local project rules
-> report conflicts
-> update AI_PROJECT/AI_DEV_SYSTEM_VERSION.md
-> stop for Human Owner approval
```

Do not re-run bootstrap blindly for a project that already has local control files.

Templates are not authority after bootstrap. In external projects, local `AI_PROJECT/` files become that project's control layer, unless they conflict with global safety, approval or lifecycle rules.

Project system updates must not modify application code.

### Use Day to Day

Recommended operator loop:

```bash
python scripts/aictl.py task list --current
python scripts/aictl.py task create --confirm --epic EPIC-006 --title "Bounded Task"
python scripts/aictl.py task import --file tasks.json --preview
python scripts/aictl.py workflow run task.prepare_for_codex --task WFA-06 --confirm
python scripts/aictl.py workflow run task.submit_for_review --task WFA-06 --confirm
python scripts/aictl.py workflow run task.close_reviewed --task WFA-06 --notes "APPROVED by Human Owner" --confirm
```

Use `workflow list` and `workflow describe <name>` before running a composed workflow. Confirmed workflows route through registered commands and owning `*ctl.py` scripts; they do not authorize automatic owner acceptance.

`OWNER_PLAN.md` is planning input, not executable scope. Codex must not implement items from it until they are converted into approved tasks with scope, allowed files, verification mode and acceptance criteria.

### Verification Modes

Default for ordinary code-only work:

```text
FAST
```

Operator shortcuts:

```text
Код быстро          -> FAST
Проверка быстро     -> STANDARD
Браузер проверить   -> on-demand browser QA
Визуально проверить -> on-demand visual QA
```

Browser automation, Playwright/MCP browser sessions, screenshots, browser console checks and manual visual QA are on-demand only. Do not run them unless the Human Owner explicitly requests them or the current task acceptance criteria require them.

Slow, full, release and golden-scenario checks are not default. Codex must not silently upgrade verification mode.

## How Work Moves

```text
Idea
-> Clarification
-> Task or change proposal
-> Prompt package
-> Human approval
-> Codex execution
-> Review
-> QA
-> Human acceptance
-> Documentation update
-> Done
```

## Where to Start

- `/ai-system/README.md` - main AI Development System index.
- `/ai-system/owner-guide.md` - how the Human Owner works with the system.
- `/ai-system/operating-model.md` - what is implemented and how the system is organized.
- `/ai-system/system-schemes.md` - compact text schemes for roles, documents and process flow.
- `/ai-system/project-integration-model.md` - foldered and root integration modes for concrete projects.
- `/ai-system/foldered-integration.md` - recommended foldered architecture.
- `/ai-system/project-control-connectivity.md` - project-control index, read policies and drift reporting.
- `/ai-system/project-operation-profile.md` - surface-level project behavior profile for AI Dev System defaults.
- `/ai-system/project-system-update.md` - how to update already integrated projects.
- `/spec/README.md` - machine-checkable spec layer for roles, modes, verification modes and lifecycle states.

## Purpose

The system helps the Human Owner work with ChatGPT and Codex through clear roles, modes, prompts, review rules and change governance.

Core idea:

```text
Human Owner controls.
ChatGPT Orchestrator routes.
AI roles specialize.
Codex executes scoped repository changes.
Documentation records decisions.
```

## Current Capabilities

- Interaction modes: Free, System, Prompt, Codex, Review, Evolution and Dry Run.
- Role model for product, design, management, implementation, quality, documentation and system evolution.
- Foldered project integration model with separate `AI_Development_System/`, `AI_PROJECT/` and target app directories.
- Project control file standard and bootstrap workflow for concrete repositories.
- Centralized `aictl.py` facade for command discovery, project doctor, task/current/context/Codex prompt commands and local Web Control Center startup.
- Confirmed workflow automation for preparing Codex execution context, refreshing context, submitting work for review, closing reviewed tasks with owner notes and creating Evolution Changes from bounded Tasks.
- Bulk Task import through validated JSON preview/confirm flow.
- Local loopback Web Control Center that delegates controlled actions through registered `aictl.py` commands.
- Project Control Index for discoverable read order, importance levels and drift reporting in concrete projects.
- Project Operation Profile for shallow Human Owner-editable AI Dev System behavior defaults.
- Work Item Hierarchy for connecting goals, initiatives and epics to executable tasks and child Agent Work Packages.
- Project system update process for refreshing already integrated projects.
- Owner plan intake through `AI_PROJECT/OWNER_PLAN.md` and `Разобрать план`.
- Explicit verification modes for fast code work, standard validation, browser smoke checks and visual QA.
- Codex prompt package format with scope, allowed files, forbidden actions, verification mode and acceptance criteria.
- Review process with severity levels and Human Owner decision keywords.
- Lifecycle governance for managed system entities.
- Language and localization policy for user-facing answers and generated prompts.
- Controlled system evolution through improvement log, AICP and changelog.

## Main Documents

- `/ai-system/README.md` - AI Development System index.
- `/ai-system/owner-guide.md` - how the Human Owner should interact with the system.
- `/ai-system/interaction-modes.md` - supported modes and routing rules.
- `/ai-system/operating-model.md` - implemented, partial and missing system areas.
- `/ai-system/system-structure.md` - high-level role and layer structure.
- `/ai-system/roles.md` - AI role registry.
- `/ai-system/rules.md` - global system rules.
- `/ai-system/prompt-lifecycle.md` - prompt creation, review and execution lifecycle.
- `/ai-system/work-item-hierarchy.md` - planning hierarchy from Goal to Initiative to Epic to Task to Agent Work Package.
- `/ai-system/task-format.md` - standard task format.
- `/ai-system/review-process.md` - review and QA process.
- `/ai-system/change-process.md` - controlled evolution process.
- `/ai-system/lifecycle-governance.md` - shared lifecycle rules.
- `/ai-system/project-integration-model.md` - foldered and root project integration modes.
- `/ai-system/foldered-integration.md` - recommended foldered architecture for project repositories.
- `/ai-system/project-control-files.md` - standard local control files for concrete projects.
- `/ai-system/project-operation-profile.md` - surface-level project behavior profile.
- `/ai-system/project-bootstrap.md` - how to initialize empty and existing project repositories.
- `/ai-system/project-system-update.md` - how to update already integrated project repositories.
- `/ai-system/verification-modes.md` - explicit verification modes, budgets and browser/visual QA boundaries.
- `/ai-system/verification-cost-model.md` - cost/value model for bounded verification check selection.
- `/ai-system/test-runtime-tracking.md` - runtime history model for executed and skipped checks.
- `/ai-system/language-policy.md` - language and localization rules.
- `/ai-system/system-changelog.md` - system version history.
- `/ai-system/improvement-log.md` - observed process problems and improvement ideas.

## Interaction Modes

Use explicit markers when precision matters:

```text
[FREE]       ordinary explanation or discussion
[SYSTEM]     process through AI Development System
[PROMPT]     generate a prompt artifact for review
[CODEX]      prepare a Codex-ready prompt package
[REVIEW]     review Codex output
[EVOLUTION]  analyze or change the AI Development System
[DRY-RUN]    simulate without applying
```

If no marker is provided, ChatGPT Orchestrator infers the mode from the request.

Repository-affecting work must use the AI Development System process and should identify:

```text
Active Role:
Active Stage:
Active Document:
Expected Result:
```

## Language Policy

Human-facing answers should use the Human Owner language by default.

System documents and control structures remain English by default:

- mode markers such as `[SYSTEM]` and `[CODEX]`;
- prompt fields such as `Scope`, `Out of Scope` and `Acceptance Criteria`;
- decision keywords such as `APPROVED`, `REWORK`, `REJECTED`, `DEFERRED` and `EXPERIMENT`;
- file paths, task IDs, branch names and command names.

Generated Codex prompts should usually be English or hybrid: stable English structure with localized explanations when useful.

## Standard Workflow

```text
Human intent
-> ChatGPT Orchestrator classifies mode
-> active role and source documents are selected
-> prompt, task, review or system change is prepared
-> Human Owner approves or requests rework
-> Codex applies approved repository changes when needed
-> result is reviewed
-> changelog or documentation is updated when required
```

## Human Owner Decisions

Use these decision words:

```text
APPROVED   accept result
REWORK     request changes
REJECTED   reject result
DEFERRED   postpone decision
EXPERIMENT test temporarily
```

AI may recommend a decision, but the Human Owner decides.

## Repository Model

```text
/ai-system   # AI Development System rules, roles, workflow and governance
/docs        # product documentation when a product project exists
README.md    # repository entrypoint in English
README.ru.md # Russian repository entrypoint
AGENTS.md    # instructions for future AI sessions
```

Legacy operator-loop files may exist, but `/ai-system` is the current primary source of truth.

## Minimal Safety Rules

- Do not change repository files unless the Human Owner explicitly asks for a repository change or Codex execution task.
- Do not treat AI Development System evolution as ordinary conversation.
- Do not generate Codex prompts without mode markers and execution boundaries.
- Do not accept Codex output automatically without review.
- Do not mix unrelated system, product, implementation and documentation changes unless explicitly approved.
- Do not run browser automation, Playwright/MCP, screenshots, browser console checks or manual visual QA unless explicitly requested or required by acceptance criteria.

# AI Development System

Status: Draft  
Version: v0.49.0

## Purpose

`/ai-system` describes how this repository is developed through an AI-assisted development process.

This folder does not describe the product itself. It describes the development mechanism: roles, rules, workflow, human interaction, task format, review process and controlled evolution of the system.

AI_Development_System now dogfoods Project Control Gateway through root-level `/AI_PROJECT`. That directory is the repository's self-hosted project-control layer for machine state, audit events and generated readable outputs. `/ai-system` remains the source-of-truth documentation for system behavior.

## Core Principle

Documentation is the source of truth.

AI roles do not work from inspiration. They work from approved documents, explicit tasks and defined acceptance criteria.

## Version Source

The current AI_Development_System version is the top version entry in `system-changelog.md`.

Primary README files mirror that changelog version and must be updated whenever the top changelog version changes.

## Relationship Between `/ai-system` And `/AI_PROJECT`

`/ai-system` stores source documents: roles, rules, lifecycle policy, operating model, evolution guidance and project-control specifications.

`/AI_PROJECT` stores this repository's self-hosted project-control state:

```text
/AI_PROJECT/state/**      machine-readable current state
/AI_PROJECT/events/**     append-only audit history
/AI_PROJECT/generated/**  generated readable views
```

Protected files under `/AI_PROJECT/state/**`, `/AI_PROJECT/events/**` and `/AI_PROJECT/generated/**` must not be edited manually. Use `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` or later approved gateway commands.

The reusable project templates remain separate:

- `/ai-system/templates/**/AI_PROJECT` — templates for external projects.
- `../examples/golden-project/AI_PROJECT` — non-runtime reference example for onboarding and validation.

## Documentation Integrity Checks

Run the repository documentation integrity checks with:

```bash
python3 scripts/check-docs-integrity.py
```

The check covers internal Markdown links, unresolved placeholders outside reusable templates, index completeness for system documents and visible status/version consistency.

Run the full read-only system validation with:

```bash
python3 scripts/validate-system.py
```

The full validation entrypoint compiles planning scripts, checks documentation integrity, parses JSON specs, validates required agent planning templates, runs dependency-aware planning fixtures and validates the golden project dry-run plan.

Run lightweight verification check selection with:

```bash
python3 scripts/verification/run_checks.py --mode FAST --budget-sec 120 --dry-run
python3 scripts/verification/run_checks.py --mode STANDARD --budget-sec 300 --dry-run
```

The lightweight runner records executed and skipped checks as local JSONL history. It does not treat unimplemented check commands as passed.

## Foldered Bootstrap/Update Helper

Run minimal dry-run planning for Foldered Control Mode with:

```bash
python3 scripts/foldered-control-mvp.py bootstrap --project-root /path/to/project
python3 scripts/foldered-control-mvp.py update --project-root /path/to/project
```

The helper reports planned control-layer changes, unresolved placeholders, project-control connectivity drift and `AI_PROJECT/AI_DEV_SYSTEM_VERSION.md` tracking. Writes require explicit `--apply`.

Foldered projects include `AI_PROJECT/PROJECT_OPERATION_PROFILE.md` as a Human Owner-editable surface profile for language, answer style, verification defaults, permissions, layout and review expectations.

Foldered projects also include `AI_PROJECT/PROJECT_CONTROL_INDEX.md` as a compact read-order map with importance levels, read policies and project-control drift reporting.

Run dry-run agent planning checks with:

```bash
python3 scripts/agent-plan-mvp.py validate --project-root /path/to/project
python3 scripts/agent-plan-mvp.py check-locks --project-root /path/to/project
python3 scripts/agent-plan-mvp.py list-parallel-groups --project-root /path/to/project
python3 scripts/agent-plan-mvp.py generate-prompts --project-root /path/to/project
```

The helper only reads `AI_PROJECT/AGENT_*` files and prints reports or prompt drafts. It does not execute Codex, create branches, merge changes, accept results or modify application code.

## Machine-Checkable Specs

Minimal machine-checkable specs are stored in `../spec/`.

Current spec files:

- `../spec/roles.json` — AI role registry snapshot.
- `../spec/interaction-modes.json` — explicit interaction modes and markers.
- `../spec/verification-modes.json` — supported verification modes and execution boundaries.
- `../spec/lifecycle-states.json` — common managed lifecycle states.
- `../spec/sops.json` — SOP inventory for initial SOP Model entries.
- `../spec/agent-work-package.schema.json` — JSON Schema contract for Agent Work Packages.
- `../spec/agent-result.schema.json` — JSON Schema contract for Agent Results.
- `../spec/role-agent-assignment.schema.json` — JSON Schema contract for manual L3 Role-to-Agent Assignments.
- `../spec/parallel-policy.json` — policy inventory for core parallel execution constraints.
- `../spec/schemas/system-spec.schema.json` — shared minimal schema for spec files.

Markdown remains the operational source of truth. Specs are derived inventory and contract files unless a later approved evolution task changes the source-of-truth relationship. Specs do not authorize runtime behavior, automatic execution, automatic merge or automatic acceptance.

## Verification Check Registry

`spec/verification-checks.json` under this `/ai-system` folder defines machine-readable check metadata for the lightweight verification runner.

It records check IDs, value classes, speed classes, expected durations, timeouts, default modes, tags and command availability. Markdown policy remains the source of truth.

## Work Item Hierarchy

`work-item-hierarchy.md` defines the Goal, Initiative, Epic, Task and Agent Work Package relationship.

Initiatives and epics are planning containers only. Task remains the executable unit, and Agent Work Package remains a child planning unit under Task.

## SOP Model

`sop-model.md` defines managed SOPs as governance-first planning procedures for repeated classes of work.

Sequential execution remains the default. SOPs do not authorize automatic execution, automatic acceptance or parallel execution.

## Agent Work Package Standard

`agent-work-package.md` defines bounded Agent Work Packages for future SOP-guided planning.

Agent Work Packages do not imply parallel execution and do not authorize automatic execution or automatic acceptance.

## Multi-Agent Planning

`multi-agent-planning.md` defines planning-only decomposition into Agent Work Packages.

Candidate parallel groups are informational only until a future Parallel Execution Policy exists and Human Owner approves them.

## Parallel Execution Policy

`parallel-execution-policy.md` defines when parallel execution is allowed, rejected and approved.

Sequential execution remains the default. Parallel execution is opt-in, Human Owner-approved and requires dependency, file-lock, integration review and QA gates.

## Agent Result Intake and Integration Review

`agent-result-intake.md` defines how individual Agent Work Package results are received and checked before review, QA or integration review.

`integration-review.md` defines how combined agent result sets are checked before QA handoff and Human Owner acceptance.

Intake and integration review do not authorize automatic execution, automatic merge or automatic acceptance.

Agent Result Intake defines the hardened Agent Result schema for manual orchestration, including structured changed files, claims, verification, risks, blockers, followups, scope compliance, safety boundary compliance and review requirements.

## Runtime Maturity Levels

`runtime-maturity-levels.md` defines runtime maturity levels from `L0 — Documentation only` through `L6 — Autonomous runtime`.

The current level is `L3 — Manual multi-agent orchestration`. Runtime execution remains `DEFERRED`; `L4+` is future/not approved.

## Manual Multi-Agent Orchestration

`manual-orchestration.md` defines the L3 manual orchestration workflow.

Manual orchestration coordinates Agent Work Packages, result intake and integration review by hand. It does not authorize automatic Codex execution, automatic multi-agent execution, branch/worktree automation, merge automation, automatic acceptance or automatic QA/review closure.

`role-agent-assignment.md` defines manual Role-to-Agent Assignments for L3. Assignments map ready Agent Work Packages to logical agents or external sessions and do not authorize automatic dispatch or runtime execution.

`l3-role-assigned-parallel-runbook.md` provides the practical Human Owner / ChatGPT Orchestrator procedure for manual role-assigned parallel orchestration.

## AI_PROJECT Control and Agent Planning Templates

This repository has a root `/AI_PROJECT` self-hosted control layer for its own evolution. References to `templates/**/AI_PROJECT` in this section describe reusable templates for concrete external projects that embed AI_Development_System.

Foldered project templates include `PROJECT_CONTROL_INDEX.md`, `PROJECT_OPERATION_PROFILE.md`, `AGENT_PLAN.md`, `AGENT_TASKS.md`, `AGENT_ASSIGNMENTS.md`, `AGENT_LOCKS.md`, `AGENT_RESULTS.md` and `AGENT_METRICS.md`.

These files are planning and review records only. They preserve sequential execution as the default and do not authorize execution, parallel execution, automatic merge or automatic acceptance.

The golden project includes a filled multi-agent planning example under `../examples/golden-project/AI_PROJECT/AGENT_*`.

The SOP / optional multi-agent pilot validation record is stored in `evolution/sop-multi-agent-pilot-validation.md`.

## Security and Privacy Baseline

AI-assisted work must follow:

- `security-policy.md` for secrets, sandbox boundaries, sensitive code and security review;
- `privacy-data-handling-policy.md` for private data, external LLM sharing and data minimization.

## Verification Cost and Runtime Tracking

`verification-cost-model.md` defines speed classes, value classes, check results, blocking/advisory impact and budget-based check selection.

`test-runtime-tracking.md` defines JSONL runtime history fields, local-only history boundaries and runtime degradation warnings.

Slow, full, release, browser, visual and golden-scenario checks remain opt-in unless the selected verification mode explicitly allows them.

## System Layers

```text
AI Development System
├── Human Owner
├── ChatGPT Orchestrator
├── Codex Executor
├── AI Roles
├── Documentation
├── Workflow
├── Rules
├── Review Process
├── Evolution Process
└── System Evolution Module
```

## Repository Model

```text
/project
  /ai-system   # rules, roles, prompts, workflow, evolution of the AI system
  /docs        # product documentation: vision, PRD, architecture, backlog, API, UX
  /backend     # backend implementation
  /frontend    # frontend implementation
  /infra       # deployment and infrastructure
  README.md
```

## Files

- `glossary.md` — all terms used by the system.
- `system-prompt.md` — main controlling prompt for the AI Development System.
- `roles.md` — AI roles and their responsibilities.
- `human-interaction.md` — how the human works with ChatGPT and Codex.
- `language-policy.md` — language and localization rules for responses, prompts and documentation.
- `workflow.md` — development stages and gates.
- `work-item-hierarchy.md` — planning hierarchy from Goal to Initiative to Epic to Task to Agent Work Package.
- `sop-model.md` — SOP model for governance-first repeatable procedures.
- `agent-work-package.md` — standard for bounded Agent Work Packages used in future SOP-guided planning.
- `multi-agent-planning.md` — planning-only workflow for decomposing parent tasks into Agent Work Packages.
- `parallel-execution-policy.md` — opt-in policy for Human Owner-approved parallel execution groups.
- `agent-result-intake.md` — intake process for Agent Work Package and Codex execution results.
- `integration-review.md` — review process for combined agent result sets before QA handoff and acceptance.
- `runtime-maturity-levels.md` — runtime maturity levels and progression gates from documentation-only work to future runtime modes.
- `manual-orchestration.md` — L3 manual-only coordination workflow for Agent Work Packages, result intake and integration review.
- `role-agent-assignment.md` — L3 manual Role-to-Agent Assignment model for logical agents and external sessions.
- `l3-role-assigned-parallel-runbook.md` — practical L3 runbook for manual role-assigned parallel orchestration.
- `rules.md` — global rules and restrictions.
- `system-schemes.md` — compact text schemes for roles, documents and process flow.
- `task-format.md` — standard task format for Codex and AI roles.
- `decision-process.md` — decision statuses and ownership.
- `decision-lifecycle.md` — lifecycle rules for Human Owner decisions.
- `review-process.md` — review and QA rules.
- `review-lifecycle.md` — lifecycle rules for managed reviews and re-review flow.
- `qa-lifecycle.md` — lifecycle rules for QA work and regression checks.
- `knowledge-lifecycle.md` — lifecycle rules for managed knowledge and lessons learned.
- `experiment-lifecycle.md` — lifecycle rules for managed experiments and rollback.
- `improvement-lifecycle.md` — lifecycle rules for managed improvements and conversion paths.
- `change-process.md` — controlled evolution of the AI Development System.
- `change-lifecycle.md` — lifecycle rules for managed system changes.
- `lifecycle-governance.md` — shared governance model for managed lifecycle documents.
- `document-lifecycle.md` — lifecycle rules for source-of-truth documents.
- `process-lifecycle.md` — lifecycle rules for managed processes.
- `task-lifecycle.md` — lifecycle rules for managed tasks.
- `codex-lifecycle.md` — lifecycle rules for Codex execution.
- `prompt-lifecycle.md` — lifecycle rules for prompts and prompt packages.
- `project-integration-model.md` — foldered and root integration modes for concrete projects.
- `foldered-integration.md` — recommended foldered architecture for embedding AI_Development_System into concrete projects.
- `project-control-files.md` — standard project-level control files for concrete repositories.
- `project-control-connectivity.md` — project control index, importance levels, read policies and drift reporting.
- `project-operation-profile.md` — surface-level project behavior profile for AI Dev System defaults.
- `project-bootstrap.md` — workflow for initializing new and existing project repositories.
- `project-system-update.md` — workflow for updating already integrated project control layers.
- `verification-modes.md` — explicit check modes, budgets and on-demand browser/visual QA rules.
- `verification-cost-model.md` — cost/value model for bounded verification check selection.
- `test-runtime-tracking.md` — JSONL runtime tracking model for executed and skipped checks.
- `security-policy.md` — security baseline for secrets, sandbox boundaries, sensitive code and automation.
- `privacy-data-handling-policy.md` — privacy and data-handling rules for private data, external LLMs and generated artifacts.
- `aicp-language-policy.md` — approved change proposal for language and localization policy.
- `aicp-security-privacy-policy.md` — approved change proposal for security, privacy and data-handling policy.
- `aicp-work-item-hierarchy.md` — approved change proposal for the planning hierarchy.
- `document-templates.md` — templates for project documents.
- `system-changelog.md` — history of changes to the AI Development System.
- `improvement-log.md` — observations and problems in the system.
- `../scripts/check-docs-integrity.py` — documentation integrity check for links, placeholders, indexes and version/status fields.
- `../scripts/validate-system.py` — read-only validation entrypoint for docs, specs, templates, planning fixtures and the golden project.
- `../scripts/verification/run_checks.py` — lightweight verification runner with dry-run, budgets, timeouts and JSONL history.
- `../scripts/foldered-control-mvp.py` — minimal dry-run bootstrap/update helper for Foldered Control Mode.
- `../scripts/agent-plan-mvp.py` — minimal dry-run helper for AI_PROJECT agent planning validation, lock checks, candidate parallel group reporting and prompt drafts.
- `../spec/README.md` — machine-checkable spec layer policy and validation guidance.

## Evolution Module

The `evolution/` directory defines roadmap-driven self-evolution of AI_Development_System.

- `evolution/README.md` — index and operating principle for the system evolution module.
- `evolution/roadmap.md` — strategic and tactical roadmap for AI_Development_System.
- `evolution/sop-multi-agent-implementation-plan.md` — master plan for SOP-guided planning and optional multi-agent execution.
- `evolution/current-evolution-task.md` — current system evolution task record; not a project-local `AI_PROJECT` file.
- `evolution/l4-assisted-sop-execution-plan.md` — planning-only roadmap for possible future L4 Assisted SOP Execution.
- `evolution/l4-assisted-sop-execution-tasks.md` — child operational task board for the L4 planning campaign.
- `evolution/sop-multi-agent-pilot-validation.md` — pilot validation findings for the SOP / optional multi-agent layer.
- `evolution/evolution-loop.md` — observe → diagnose → propose → plan → execute → verify → review → approve → release → learn loop.
- `evolution/evolution-policy.md` — permissions, boundaries and anti-runaway rules for self-evolution.
- `evolution/owner-evolution-plan.md` — Human Owner-authored intake place for broad system evolution plans.
- `evolution/owner-plan-intake.md` — workflow for mapping owner plans to roadmap, backlog and one bounded next task.
- `evolution/system-health-check.md` — repeatable system health-check checklist.
- `evolution/evolution-backlog.md` — managed backlog of system evolution items.
- `evolution/analysis-report-baseline.md` — baseline findings from the analytical repository report.
- `evolution/concept-baseline.md` — legacy conceptual baseline preserved for historical context; not the current source of truth.
- `evolution/templates/system-change-proposal.md` — AI System Change Proposal template.
- `evolution/templates/evolution-task.md` — bounded system evolution task template.
- `evolution/templates/owner-evolution-plan.md` — reusable owner plan intake template.
- `examples/golden-project/` — filled foldered Task Tracker example for onboarding foldered integration and non-runtime multi-agent planning.

## Templates

- `templates/foldered/` — recommended templates for `AGENTS.md`, `AI_Development_System/` and `AI_PROJECT/` integration.
- `templates/project/` — root-mode templates for simple or legacy projects.

## Operating Model

```text
Human Owner sets direction
ChatGPT Orchestrator prepares documents, prompts and reviews
Codex Executor changes repository files
Documentation records decisions
AI Development System controls the process
System Evolution Module controls roadmap-driven self-improvement
```

## Minimal Rule

No implementation task should start without:

- a task from the backlog;
- required source documents;
- clear scope and out of scope;
- acceptance criteria;
- expected output;
- review step.

No system evolution task should start without:

- a roadmap item, backlog item, health-check finding, analytical report finding or Human Owner request;
- owner plan intake and mapping when the source is a broad Human Owner evolution plan;
- explicit allowed files;
- verification mode;
- review requirements;
- Human Owner approval requirement assessment;
- changelog impact assessment.

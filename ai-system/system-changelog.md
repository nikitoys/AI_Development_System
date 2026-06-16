# AI Development System Changelog

Status: Draft

## v0.49.0

### Updated

- Reconciled primary documentation with the Human Owner decision to use root `/AI_PROJECT` as AI_Development_System's self-hosted Project Control Layer.
- Updated README mirrors, `ai-system/README.md`, evolution documentation, operating model and Project Control Gateway docs to distinguish root `/AI_PROJECT`, reusable `AI_PROJECT` templates and the golden project example.
- Clarified that `/ai-system` remains the source-of-truth document tree for system behavior, while root `/AI_PROJECT` stores protected state, audit events and generated readable outputs.
- Reaffirmed that `/AI_PROJECT/state/**`, `/AI_PROJECT/events/**` and `/AI_PROJECT/generated/**` must be changed only through project-control CLI gateways.
- Updated README version mirrors to `v0.49.0`.

### Reason

The Human Owner chose Option A: AI_Development_System intentionally dogfoods Project Control Gateway through root `/AI_PROJECT` for its own controlled evolution. This documentation-only reconciliation does not implement L4, approve assisted execution, add runtime behavior, add a SOP runner, weaken protected-file rules, or change the current maturity boundary: current maturity remains `L3`, runtime remains `DEFERRED`, and `L4+` remains future/not approved.

## v0.48.2

### Added

- Added `ai-system/evolution/current-evolution-task.md` as the current system evolution task record.
- Added `ai-system/evolution/l4-assisted-sop-execution-plan.md` as the L4 Assisted SOP Execution planning record.
- Added `ai-system/evolution/l4-assisted-sop-execution-tasks.md` as the child task board for the L4 planning campaign.
- Added `EVOL-030` to track alignment of L4 Assisted SOP Execution planning with evolution governance.

### Updated

- Moved useful L4 planning content out of the root-level `AI_PROJECT` folder and into `ai-system/evolution/`.
- Updated README and evolution index references so the moved planning records are discoverable.
- Recorded the then-current cleanup decision that free-form root-level L4 planning records should not replace source evolution documents under `ai-system/evolution/`.

### Removed

- Removed the then-existing free-form root-level `AI_PROJECT` planning folder from AI_Development_System.

### Reason

System evolution planning source documents belong under `ai-system/evolution/`, not in free-form root project-control files. This change preserved the L4 planning records, kept templates and golden examples untouched, and did not introduce runtime behavior, automatic execution, automatic dispatch, automatic merge, automatic PR creation, automatic acceptance or automatic QA/review closure.

## v0.48.1

### Updated

- Moved the legacy root-level evolution concept draft to `ai-system/evolution/concept-baseline.md`.
- Added legacy/source-of-truth notice to the moved concept baseline.
- Updated README/index references so the archived baseline is discoverable without presenting it as the active evolution plan.

### Reason

The root-level concept draft looked like a current top-level source of truth even though active evolution planning already lives under `ai-system/evolution/`. This documentation-only cleanup preserves historical context while keeping the authoritative evolution model in roadmap, owner plan, intake, backlog and policy documents.

## v0.48.0

### Added

- Added `ai-system/work-item-hierarchy.md` to define the Goal, Initiative, Epic, Task and Agent Work Package relationship.
- Added `ai-system/aicp-work-item-hierarchy.md` and `EVOL-029` traceability for the hierarchy change.

### Updated

- Updated task format and task lifecycle documentation so Initiative and Epic are optional planning fields and do not block Definition of Ready.
- Updated Agent Work Package guidance to reference the hierarchy while preserving the parent-task-only authority model.
- Updated `CODEX_PLAN.md` and `CODEX_TASKS.md` templates so plans can show initiatives and epics, and task boards can map tasks to them.
- Updated the golden project so `T-003` maps to `INIT-001` / `EPIC-001` while existing Agent Work Packages remain children of `T-003`.
- Updated glossary, operating model and README/index references.

### Reason

Planning needed an explicit bridge between broad goals and executable tasks. The new hierarchy adds Goal, Initiative and Epic as planning context while preserving the existing execution model: Task remains the executable unit, Agent Work Package remains a child planning unit under Task, and Human Owner approval remains required before repository-changing execution. This change does not add runtime behavior, automatic execution, new task lifecycle states or new parallel execution behavior.

## v0.47.0

### Added

- Added `ai-system/project-control-connectivity.md` to define Project Control Index, importance levels, read policies and project-control drift reporting.
- Added `ai-system/templates/foldered/AI_PROJECT/PROJECT_CONTROL_INDEX.md` and `ai-system/templates/project/PROJECT_CONTROL_INDEX.md` as compact local read-order manifests.
- Added `examples/golden-project/AI_PROJECT/PROJECT_CONTROL_INDEX.md` and `examples/golden-project/AI_PROJECT/PROJECT_OPERATION_PROFILE.md` so the golden project reflects the current control layer.

### Updated

- Updated foldered and root-mode `AGENTS.md` and `CODEX_WORKFLOW.md` templates so agents read `PROJECT_CONTROL_INDEX.md` before lower-level control files and report `Control Context`.
- Updated project integration, foldered integration, project control, bootstrap and system update documents to include project-control connectivity and read-order drift handling.
- Updated `scripts/foldered-control-mvp.py` so bootstrap/update include `AI_PROJECT/PROJECT_CONTROL_INDEX.md` and report connectivity drift without overwriting existing local files.
- Updated system validation to require the control index and operation profile in templates and the golden project.
- Updated README/index references and version mirrors to `v0.47.0`.

### Reason

Existing project agents can miss newer project-control files when stale `AGENTS.md` files do not mention them. The Project Control Index gives every project a shallow, discoverable map of local control files with importance and read policies, while the update helper makes stale read order visible as drift without automatically rewriting Human Owner-edited local files.

## v0.46.0

### Added

- Added `ai-system/project-operation-profile.md` to define the Project Operation Profile as a surface-level behavior profile for concrete projects.
- Added `ai-system/templates/foldered/AI_PROJECT/PROJECT_OPERATION_PROFILE.md` and `ai-system/templates/project/PROJECT_OPERATION_PROFILE.md` as project templates for Human Owner-editable operating preferences.

### Updated

- Updated project integration, foldered integration, project control and bootstrap documents so `PROJECT_OPERATION_PROFILE.md` is part of the standard local control layer and read order.
- Updated foldered and root-mode `AGENTS.md` and `CODEX_WORKFLOW.md` templates to read the operation profile before lower-level project workflow files.
- Updated `scripts/foldered-control-mvp.py` so bootstrap and update include `AI_PROJECT/PROJECT_OPERATION_PROFILE.md`, create missing control files on `update --apply` and preserve existing local profiles.
- Updated README/index references and version mirrors to `v0.46.0`.

### Reason

Concrete projects need a shallow, Human Owner-editable place for operational AI Dev System preferences such as response language, answer detail level, verification defaults, permissions, project layout and review defaults. The profile provides defaults only; it does not authorize execution without an approved task and cannot weaken global safety, approval or lifecycle rules.

## v0.45.0

### Added

- Added `ai-system/verification-cost-model.md` to define verification speed classes, value classes, result types, blocking/advisory impact and budget-based check selection.
- Added `ai-system/test-runtime-tracking.md` to define JSONL runtime history fields, local-only history boundaries, aggregate metrics and runtime degradation warnings.
- Added `ai-system/spec/verification-checks.json` as the lightweight verification check registry.
- Added `scripts/verification/run_checks.py` as a Python standard-library verification runner with dry-run, explicit budgets, per-check timeouts, slow-check gating and JSONL event recording.
- Added `ai-system/templates/foldered/AI_PROJECT/verification-history.example.jsonl` as example runtime history.

### Updated

- Updated `ai-system/verification-modes.md` to define `NONE`, `SMOKE`, `FAST`, `STANDARD`, `FULL`, `RELEASE` and `MANUAL` with explicit budgets and no silent upgrade rule.
- Updated `ai-system/codex-lifecycle.md` and `ai-system/task-format.md` so Codex tasks and final reports include verification budget, slow-check permission, runtime tracking, check durations, skipped checks and runtime warnings.
- Updated `ai-system/operating-model.md`, `ai-system/README.md`, root README files and `spec/README.md` to index the new verification cost/runtime tracking model.
- Updated `spec/verification-modes.json` to mirror the new verification mode set.
- Updated `scripts/validate-system.py` to compile the new runner and parse JSON files under `ai-system/spec/`.
- Updated `.gitignore` to keep local verification runtime history out of commits.

### Reason

Verification now follows an explicit cost/value model instead of encouraging broad test runs by default. Codex tasks can declare mode, budget, slow-check permission and runtime tracking, while final reports must distinguish executed checks from skipped checks and avoid claiming full verification without measured runtime. Slow, full, release, browser, visual and golden-scenario checks remain opt-in.

## v0.44.0

### Added

- Added `ai-system/l3-role-assigned-parallel-runbook.md` as the practical L3 runbook for manual role-assigned parallel orchestration.

### Updated

- Updated `ai-system/manual-orchestration.md`, `ai-system/role-agent-assignment.md`, `ai-system/operating-model.md`, `ai-system/evolution/roadmap.md`, `ai-system/evolution/evolution-backlog.md` and README/index references to link the runbook.
- Updated README version mirrors to `v0.44.0`.

### Reason

L3 now has a practical runbook for Human Owner / ChatGPT Orchestrator operation of manual role-assigned multi-agent work: choose parent task, select SOP, prepare Agent Plan and Agent Work Packages, prepare `AGENT_ASSIGNMENTS.md`, validate, review candidate groups, manually hand bounded prompts to external sessions, collect Agent Results, perform Agent Result Intake, run Integration Review, record Human Owner decisions, update statuses and recompute the next ready group. Runtime remains `DEFERRED`; the runbook does not add automatic Codex execution, automatic agent dispatch, runtime implementation, branch/worktree automation, automatic merge, automatic acceptance or automatic QA/review closure.

## v0.43.0

### Added

- Added `ai-system/role-agent-assignment.md` as the L3 Role-to-Agent Assignment source document.
- Added `ai-system/templates/foldered/AI_PROJECT/AGENT_ASSIGNMENTS.md` as the project-local manual assignment template.
- Added `examples/golden-project/AI_PROJECT/AGENT_ASSIGNMENTS.md` as a filled manual assignment example.
- Added `spec/role-agent-assignment.schema.json` as the machine-checkable assignment contract.

### Updated

- Updated Manual Multi-Agent Orchestration, Runtime Maturity Levels, Agent Work Package, Multi-Agent Planning and Parallel Execution Policy references for L3 assignment records.
- Updated foldered integration/project control docs, bootstrap planning, CI/local validation and README/index references to include `AGENT_ASSIGNMENTS.md`.
- Updated README version mirrors to `v0.43.0`.

### Reason

L3 manual orchestration needs an explicit way to assign ready Agent Work Packages to logical agents or external agent sessions without implying runtime dispatch. The assignment model enables manual multi-threaded coordination while preserving Human Owner approval, hardened Agent Result Intake, Integration Review and all deferred-runtime boundaries. Runtime execution remains `DEFERRED`; L4+ remains future/not approved. This change does not add automatic Codex execution, automatic agent dispatch, automatic multi-agent execution, branch/worktree automation, automatic file modification by orchestration tooling, automatic merge, automatic acceptance or automatic QA/review closure.

## v0.42.0

### Updated

- Added an L3 readiness assessment to `ai-system/runtime-maturity-levels.md`.
- Updated the current maturity level to `L3 — Manual multi-agent orchestration`.
- Updated `ai-system/manual-orchestration.md`, `ai-system/operating-model.md`, `ai-system/evolution/roadmap.md`, `ai-system/evolution/evolution-backlog.md` and README version mirrors to reflect the L3 maturity decision.

### Reason

After `EVOL-019` through `EVOL-026`, the system has the documented process, dependency-aware dry-run planning, fixtures, read-only CI/local validation, hardened Agent Result Intake, Integration Review handoff and expanded pilot evidence required for `L3 — Manual multi-agent orchestration`. Runtime execution remains `DEFERRED`; L3 is manual-only and does not add automatic Codex execution, automatic multi-agent execution, branch/worktree automation, automatic file modification by orchestration tooling, automatic merge, automatic acceptance or automatic QA/review closure. `L4+` remains future/not approved.

## v0.41.0

### Updated

- Expanded `ai-system/evolution/sop-multi-agent-pilot-validation.md` with EVOL-026 pilot evidence.
- Recorded pilot scenarios for a documentation-only change, a small tooling/code change and a multi-agent parallel planning case.
- Marked `EVOL-026 — Pilot Validation Expansion` as `Done`.
- Updated roadmap P6 immediate priorities so `EVOL-026` is completed and `EVOL-027` remains future/deferred.
- Updated README version mirrors to `v0.41.0`.

### Reason

`EVOL-026` expands pilot evidence beyond the original golden example while keeping the system at `L2 — Dry-run planning`. The pilot record distinguishes validated dry-run behavior, manually simulated orchestration behavior and future/not-yet-validated runtime behavior. Runtime execution remains `DEFERRED`; this change does not add automatic Codex execution, automatic multi-agent execution, branch/worktree automation, automatic file modification by orchestration tooling, automatic merge, automatic acceptance or automatic QA/review closure.

## v0.40.0

### Added

- Added `.github/workflows/validate-ai-system.yml` to run read-only validation for docs/specs, dependency-aware planning fixtures and the golden project.
- Added `scripts/validate-system.py` as the local validation entrypoint for documentation integrity, JSON specs, agent planning templates, fixtures and golden project dry-run checks.

### Updated

- Updated `spec/README.md`, `README.md`, `README.ru.md` and `ai-system/README.md` with the local full validation command.
- Marked `EVOL-025 — CI for Specs, Templates and Golden Project` as `Done`.
- Updated roadmap P6 immediate priorities so `EVOL-025` is completed and `EVOL-026` is the next proposed follow-up.
- Updated README version mirrors to `v0.40.0`.

### Reason

`EVOL-025` makes repository validation repeatable in CI and locally for specs, templates, planning fixtures and the golden project. The checks are read-only and do not add runtime execution, automatic Codex execution, automatic multi-agent execution, branch/worktree automation, automatic merge, automatic acceptance or automatic QA/review closure.

## v0.39.0

### Updated

- Hardened the Agent Result schema in `ai-system/agent-result-intake.md`.
- Updated `spec/agent-result.schema.json` to match the hardened Agent Result contract.
- Updated `ai-system/templates/foldered/AI_PROJECT/AGENT_RESULTS.md` and `examples/golden-project/AI_PROJECT/AGENT_RESULTS.md` with hardened result fields.
- Updated `ai-system/manual-orchestration.md` so L3 manual result intake uses the hardened Agent Result schema.
- Updated `ai-system/integration-review.md` with hardened Agent Result handoff checks.
- Marked `EVOL-024 — Agent Result Schema Hardening` as `Done`.
- Updated roadmap P6 immediate priorities so `EVOL-024` is completed and `EVOL-025` is the next proposed follow-up.
- Updated README version mirrors to `v0.39.0`.

### Reason

`EVOL-024` makes agent results more machine-checkable and reviewable for future L3 manual orchestration. Runtime execution remains `DEFERRED`; this change does not add automatic Codex execution, automatic multi-agent execution, branch/worktree automation, automatic file modification by orchestration tooling, automatic merge, automatic acceptance or automatic QA/review closure.

## v0.38.0

### Added

- Added `ai-system/manual-orchestration.md` to define Manual Multi-Agent Orchestration Mode for L3 readiness.

### Updated

- Updated `ai-system/runtime-maturity-levels.md` to reference the L3 manual orchestration source document.
- Updated `ai-system/README.md` and `ai-system/operating-model.md` to index Manual Multi-Agent Orchestration Mode.
- Marked `EVOL-023 — Manual Multi-Agent Orchestration Mode` as `Done`.
- Updated roadmap P6 immediate priorities so `EVOL-023` is completed and `EVOL-024` is the next proposed follow-up.
- Updated README version mirrors to `v0.38.0`.

### Reason

`EVOL-023` defines L3 as manual-only orchestration after dry-run planning. It allows manual plan validation, manual AWP selection and assignment, manual result intake, manual integration review and Human Owner decisions while forbidding automatic Codex execution, automatic multi-agent execution, branch/worktree automation, automatic merge, automatic acceptance and automatic QA/review closure. Runtime remains `DEFERRED`; L4+ remains future/not approved.

## v0.37.0

### Added

- Added `ai-system/runtime-maturity-levels.md` to define runtime maturity levels `L0` through `L6`.

### Updated

- Marked `EVOL-022 — Runtime Maturity Levels` as `Done`.
- Updated `ai-system/README.md` and `ai-system/operating-model.md` to index the Runtime Maturity Levels document.
- Updated roadmap P6 immediate priorities so `EVOL-022` is completed and `EVOL-023` is the next proposed follow-up.
- Updated README version mirrors to `v0.37.0`.

### Reason

`EVOL-022` separates documentation, specs, dry-run planning, manual orchestration and future runtime modes. The current level is `L2 — Dry-run planning`; the next safe target is `L3 — Manual multi-agent orchestration`. Runtime execution remains `DEFERRED`, and `L4+` remains future/not approved without explicit Human Owner approval.

## v0.36.0

### Added

- Added `scripts/validate-agent-plan-fixtures.py` as a lightweight validation runner for dependency-aware dry-run planning fixtures.
- Added `simple-linear`, `simple-parallel` and `diamond` planning fixtures under `examples/agent-plan-fixtures/`.

### Updated

- Expanded `examples/agent-plan-fixtures/README.md` with the new fixtures and validation command.
- Marked `EVOL-021 — Planning Fixtures and Validation Tests` as `Done`.
- Updated roadmap P6 immediate priorities so `EVOL-021` is completed and `EVOL-022` is the next proposed follow-up.
- Updated README version mirrors to `v0.36.0`.

### Reason

`EVOL-021` adds repeatable fixture coverage for dependency-aware dry-run planning, including simple linear dependency, simple parallel dependency, diamond dependency, missing dependency, cycle detection, blocked package exclusion and completed prerequisite unlocking a parallel group. The validation runner only executes local dry-run checks and does not authorize runtime behavior, automatic Codex execution, branch/worktree automation, merge automation or automatic acceptance.

## v0.35.0

### Added

- Added `examples/agent-plan-fixtures/` with dry-run planning fixtures for accepted prerequisites, missing dependencies, cycle detection and blocked package exclusion.

### Updated

- Improved `scripts/agent-plan-mvp.py list-parallel-groups` so candidate groups are dependency-aware.
- Added parsing for explicit AWP dependencies from `AI_PROJECT/AGENT_TASKS.md` package detail fields and `AI_PROJECT/AGENT_PLAN.md` dependency tables.
- Added missing dependency and dependency cycle validation.
- Added ready dependency layer output and exclusion explanations for blocked packages or incomplete prerequisites.
- Marked `EVOL-020 — Improve dry-run agent planner dependency parsing` as `Done`.
- Updated roadmap P6 immediate priorities so `EVOL-020` is completed and `EVOL-021` is the next proposed follow-up.
- Updated README version mirrors to `v0.35.0`.

### Reason

`EVOL-020` fixes over-broad candidate parallel group reporting while preserving dry-run safety boundaries. The helper still does not execute Codex, create branches or worktrees, merge changes, modify application code, accept results or change the deferred runtime decision.

## v0.34.0

### Updated

- Marked `EVOL-019 — Runtime Decision Record` as `Done`.
- Recorded the runtime decision as `DEFERRED` in `ai-system/evolution/evolution-backlog.md`.
- Updated roadmap P6 immediate priorities so `EVOL-019` is completed and `EVOL-020` remains the next proposed technical improvement.
- Updated README version mirrors to `v0.34.0`.

### Reason

`EVOL-019` formally closes the runtime decision step. Runtime execution remains deferred. Dry-run planning, Agent Work Package generation, agent plan validation, candidate parallel group listing, manual orchestration and Human Owner-controlled review remain allowed. Automatic Codex execution, automatic multi-agent execution, branch/worktree lifecycle automation, automatic merge, automatic acceptance, automatic QA/review closure and bypassing Human Owner approval remain forbidden. No runtime or automation behavior was implemented.

## v0.33.0

### Added

- Added the post-`EVOL-018` development plan to `ai-system/evolution/evolution-backlog.md`.
- Added proposed backlog items `EVOL-021` through `EVOL-028`.
- Added explicit runtime maturity direction to the P6 roadmap: current level `L2 — Dry-run planning`, next target `L3 — Manual multi-agent orchestration`.

### Updated

- Expanded `EVOL-019` as the required Runtime Decision Record with decision `DEFERRED`, allowed dry-run/manual capabilities, forbidden runtime automation and revisit criteria.
- Expanded `EVOL-020` with dependency graph parsing requirements, topological layering, cycle/missing dependency detection and the `AWP-REQ-001` / `AWP-BE-001` / `AWP-FE-001` / `AWP-QA-001` example.
- Updated roadmap P6 from optional multi-agent execution language to a SOP and optional multi-agent control-plane plan.
- Updated README version mirrors to `v0.33.0`.

### Reason

The next development plan after `EVOL-008` through `EVOL-018` must be explicit before runtime discussions continue. Runtime execution remains deferred. Immediate priorities are `EVOL-019` and `EVOL-020`; future work targets dependency-aware dry-run planning, manual orchestration, stronger schemas, validation CI and broader pilot evidence before any assisted or controlled runtime is reconsidered.

## v0.32.0

### Added

- Added `ai-system/evolution/sop-multi-agent-pilot-validation.md` to record EVOL-018 pilot validation findings for the SOP / optional multi-agent layer.
- Added `IMP-002` to track shallow dependency graph parsing in `scripts/agent-plan-mvp.py`.
- Added proposed follow-up `EVOL-020 — Improve dry-run agent planner dependency parsing`.

### Updated

- Updated README version mirrors to `v0.32.0`.
- Updated `ai-system/README.md` to index the pilot validation record.
- Updated `evolution-backlog.md` to mark `EVOL-018` as completed.

### Reason

`EVOL-018` records pilot evidence before the EVOL-019 runtime decision. The pilot confirms that the current SOP / optional multi-agent layer works as governance-first documentation, templates, specs and dry-run reporting, while recording that runtime integration is not justified yet and dependency-aware parallel group reporting needs a future bounded improvement.

## v0.31.0

### Added

- Extended `examples/golden-project/` with a filled non-runtime multi-agent planning example for a Task Tracker due-date filter enhancement.
- Added golden-project `AI_PROJECT/AGENT_PLAN.md`, `AGENT_TASKS.md`, `AGENT_LOCKS.md`, `AGENT_RESULTS.md`, `AGENT_METRICS.md` and a local example README.

### Updated

- Updated README version mirrors to `v0.31.0`.
- Updated `ai-system/README.md` to note the filled golden-project multi-agent planning example.
- Updated `evolution-backlog.md` to mark `EVOL-017` as completed.

### Reason

`EVOL-017` validates the SOP and agent planning documentation with a filled golden project example. The example remains non-runtime and does not authorize execution, parallel execution, automatic execution, automatic merge or automatic acceptance.

## v0.30.0

### Added

- Added `scripts/agent-plan-mvp.py` as a minimal dry-run helper for `AI_PROJECT/AGENT_*` planning files.
- Added support for `validate`, `check-locks`, `list-parallel-groups` and `generate-prompts` reporting commands.

### Updated

- Updated README version mirrors to `v0.30.0`.
- Updated `ai-system/README.md`, `project-control-files.md`, `foldered-integration.md` and `project-integration-model.md` with agent planner MVP usage and safety boundaries.
- Updated `evolution-backlog.md` to mark `EVOL-016` as completed.

### Reason

`EVOL-016` adds dry-run agent planning validation and reporting. The helper does not execute Codex, create branches or worktrees, merge changes, modify application code, accept results or turn candidate parallel groups into executable groups.

## v0.29.0

### Added

- Added foldered `AI_PROJECT` agent planning templates: `AGENT_PLAN.md`, `AGENT_TASKS.md`, `AGENT_LOCKS.md`, `AGENT_RESULTS.md` and `AGENT_METRICS.md`.

### Updated

- Updated README version mirrors to `v0.29.0`.
- Updated project control, foldered integration, project integration and bootstrap documentation to reference the new agent planning files.
- Updated `scripts/foldered-control-mvp.py` so bootstrap/update planning includes the new templates.
- Updated `ai-system/README.md` and `ai-system/operating-model.md` to index the new templates.
- Updated `evolution-backlog.md` to mark `EVOL-015` as completed.

### Reason

`EVOL-015` adds project-local planning templates for SOP-guided and optional multi-agent workflows. The templates are planning and review records only; they preserve sequential execution as the default and do not authorize runtime behavior, automatic execution, automatic merge or automatic acceptance.

## v0.28.0

### Added

- Added `spec/sops.json` with the initial SOP inventory for `SOP-FEATURE-001`, `SOP-BUGFIX-001` and `SOP-SYSTEM-001`.
- Added `spec/agent-work-package.schema.json` as a minimal JSON Schema contract for Agent Work Packages.
- Added `spec/agent-result.schema.json` as a minimal JSON Schema contract for Agent Results.
- Added `spec/parallel-policy.json` as a policy inventory for core parallel execution constraints.

### Updated

- Updated README version mirrors to `v0.28.0`.
- Updated `spec/README.md` with new spec files, Markdown source documents, validation guidance and EVOL-014 boundaries.
- Updated `ai-system/README.md` and `ai-system/operating-model.md` to index the new specs.
- Updated `evolution-backlog.md` to mark `EVOL-014` as completed.

### Reason

`EVOL-014` adds minimal machine-checkable SOP and agent planning specs derived from Markdown source documents. Markdown remains the operational source of truth. This change does not generate Markdown, add schema validation CI, create scripts, modify templates, implement runtime behavior or authorize automatic execution, automatic merge or automatic acceptance.

## v0.27.0

### Added

- Added `ai-system/agent-result-intake.md` to define controlled intake of Agent Work Package and Codex execution results.
- Added `ai-system/integration-review.md` to define review of integrated agent result sets before QA handoff and Human Owner acceptance.
- Added intake checks for scope, `allowed_files`, `locked_files`, `forbidden_actions`, dependencies, verification mode, errors, questions and blockers.
- Added integration review checks for cross-agent consistency, behavior/contracts, architecture, API/UX/data, conflicts, regression, documentation and security/privacy.

### Updated

- Updated README version mirrors to `v0.27.0`.
- Updated `ai-system/README.md` and `ai-system/operating-model.md` to index Agent Result Intake and Integration Review.
- Updated `evolution-backlog.md` to mark `EVOL-013` as completed.

### Reason

`EVOL-013` defines result intake and integration review gates for SOP-guided and optional multi-agent workflows. This change does not implement runtime behavior, branch/worktree/merge automation, scripts, specs, templates, automatic execution, automatic merge or automatic acceptance.

## v0.26.0

### Added

- Added `ai-system/parallel-execution-policy.md` to define opt-in parallel execution governance.
- Added eligibility, rejection, dependency, file-lock, approval, integration review, QA, rollback/rework, result intake and security/privacy rules for managed parallel execution groups.

### Updated

- Updated README version mirrors to `v0.26.0`.
- Updated `ai-system/README.md` and `ai-system/operating-model.md` to index the Parallel Execution Policy.
- Updated `evolution-backlog.md` to mark `EVOL-012` as completed.

### Reason

`EVOL-012` defines parallel execution as an opt-in, Human Owner-approved policy layer while preserving sequential execution as the default. This change does not implement runtime behavior, branches, worktrees, merge logic, scripts, specs, templates, automatic execution, automatic merge or automatic acceptance.

## v0.25.0

### Added

- Added `ai-system/multi-agent-planning.md` to define planning-only decomposition of parent tasks into Agent Work Packages.
- Added Multi-Agent Planning states, inputs, outputs, decomposition rules, dependency rules, file-scope rules and locked-file planning guidance.

### Updated

- Updated README version mirrors to `v0.25.0`.
- Updated `ai-system/README.md` and `ai-system/operating-model.md` to index the Multi-Agent Planning workflow.
- Updated `evolution-backlog.md` to mark `EVOL-011` as completed.

### Reason

`EVOL-011` defines Multi-Agent Planning as planning-only workflow. Candidate parallel groups are informational only until a future Parallel Execution Policy exists and Human Owner approves them. This change avoids runtime automation, parallel execution enablement, specs, scripts, templates, automatic execution and automatic acceptance.

## v0.24.0

### Added

- Added `ai-system/agent-work-package.md` to define bounded Agent Work Packages for future SOP-guided planning.
- Added Agent Work Package required fields, lifecycle/status values, ownership model and examples for backend, frontend, QA/review and documentation work.

### Updated

- Updated README version mirrors to `v0.24.0`.
- Updated `ai-system/README.md` and `ai-system/operating-model.md` to index the Agent Work Package standard.
- Updated `evolution-backlog.md` to mark `EVOL-010` as completed.

### Reason

`EVOL-010` defines the Agent Work Package standard while preserving sequential execution as the default and avoiding Multi-Agent Planning workflow, Parallel Execution Policy, specs, scripts, templates, runtime automation, automatic execution or automatic acceptance.

## v0.23.0

### Added

- Added `ai-system/sop-model.md` to define managed SOPs as governance-first planning procedures.
- Added three initial SOPs: `SOP-FEATURE-001`, `SOP-BUGFIX-001` and `SOP-SYSTEM-001`.

### Updated

- Updated README version mirrors to `v0.23.0`.
- Updated `ai-system/README.md` and `ai-system/operating-model.md` to index the SOP Model.
- Updated `evolution-backlog.md` to mark `EVOL-009` as completed.

### Reason

`EVOL-009` defines the SOP Model from the SOP / optional multi-agent master plan while preserving sequential execution as the default and avoiding Agent Work Package standards, scripts, specs, templates, runtime automation, automatic execution or automatic acceptance.

## v0.22.0

### Added

- Added `ai-system/evolution/sop-multi-agent-implementation-plan.md` to record the Human Owner's SOP and optional multi-agent implementation plan.
- Added `EVOL-008` through `EVOL-019` to `evolution-backlog.md` to decompose the initiative into bounded future tasks.
- Added roadmap priority `P6 — SOP and Optional Multi-Agent Execution Layer`.

### Updated

- Updated README version mirrors to `v0.22.0`.
- Updated `ai-system/README.md` and `ai-system/evolution/README.md` to index the new plan.
- Renumbered Research and Benchmarking roadmap priority from P6 to P7 to make room for the SOP / Multi-Agent Layer.

### Reason

The Human Owner wants a governance-first SOP and optional multi-agent execution direction recorded before implementation. This change records the plan and future task decomposition without creating runtime automation, scripts, specs, templates or changes to the existing one-task Codex workflow.

## v0.21.0

### Added

- Added `scripts/foldered-control-mvp.py` as a minimal Foldered Control Mode bootstrap/update helper.
- Added dry-run bootstrap planning for root `AGENTS.md` and `AI_PROJECT/` control files.
- Added dry-run update reporting for required control files, unresolved placeholders and `AI_PROJECT/AI_DEV_SYSTEM_VERSION.md` tracking.

### Updated

- Updated README version mirrors to `v0.21.0`.
- Updated bootstrap, project-system-update and foldered-integration docs to reference the helper and its dry-run-first boundary.
- Updated `ai-system/README.md` and `ai-system/evolution/README.md` indexes.
- Added and completed `EVOL-007` in `evolution-backlog.md`.

### Reason

`EVOL-007` starts P5 bootstrap/update tooling with a small script-level MVP for dry-run planning, placeholder detection and version tracking while avoiding a large CLI, package, release automation, upstream git management or product-code changes.

## v0.20.0

### Added

- Added `spec/README.md` to define the first machine-checkable specification layer and the spec-to-Markdown relationship.
- Added `spec/roles.json`, `spec/interaction-modes.json`, `spec/verification-modes.json` and `spec/lifecycle-states.json` as minimal JSON specs for stable system entities.
- Added `spec/schemas/system-spec.schema.json` as a shared minimal schema for spec files.

### Updated

- Updated README version mirrors to `v0.20.0`.
- Updated `ai-system/README.md` and `ai-system/evolution/README.md` to index the spec layer.
- Updated `evolution-backlog.md` to mark `EVOL-006` as completed.
- Updated `owner-evolution-plan.md` with the EVOL-006 completion record and post-plan next-task boundary.

### Reason

`EVOL-006` introduces a minimal machine-checkable contract layer for roles, interaction modes, verification modes and lifecycle states while keeping Markdown as the operational source of truth and avoiding Markdown generation, CI schema lint, bootstrap, release or research work.

## v0.19.0

### Added

- Added `examples/golden-project/` as a fully filled foldered example for Task Tracker with an explicit Task Tracker mission, owner plan, control file set and verification policy.

### Updated

- Updated `README.md` and `README.ru.md` version to `v0.19.0`.
- Updated `ai-system/README.md` to index the golden example.
- Updated `evolution-backlog.md` to mark `EVOL-005` as completed.
- Updated `owner-evolution-plan.md` with the EVOL-005 completion record and next bounded task recommendation.

### Reason

`EVOL-005` adds one complete, minimal example of foldered integration for onboarding, with no real product code and explicit focus on control-layer files.

## v0.18.0

### Added

- Added `ai-system/aicp-security-privacy-policy.md` for the approved EVOL-004 system change.
- Added `ai-system/security-policy.md` with secret-handling, automation, sandbox, sensitive-code and incident-handling rules.
- Added `ai-system/privacy-data-handling-policy.md` with private-data, sensitive-data, external LLM sharing, data minimization and generated-artifact rules.

### Updated

- Updated README version mirrors to `v0.18.0`.
- Updated `rules.md` and `review-process.md` to reference security and privacy policies.
- Updated project templates so concrete projects inherit the AI_Development_System security and privacy baseline.
- Updated the owner evolution plan and evolution backlog to mark `EVOL-004` as completed and recommend `EVOL-005` as the next bounded phase.

### Reason

`EVOL-004` centralizes the minimum security, privacy and data-handling baseline for AI-assisted development without starting golden example work or the machine-checkable specification layer.

## v0.17.2

### Added

- Added `scripts/check-docs-integrity.py` for local documentation integrity validation.
- Added `.github/workflows/docs-integrity.yml` to run documentation integrity checks on push and pull request.

### Updated

- Updated README version mirrors to `v0.17.2`.
- Updated the owner evolution plan and evolution backlog to mark `EVOL-003` as completed and recommend `EVOL-004` as the next bounded phase.
- Documented the documentation integrity check command in the root README files and AI system README.

### Reason

`EVOL-003` adds practical documentation integrity checks for Markdown links, unresolved placeholders, index completeness and status/version consistency without starting security/privacy policy work, golden example work or the machine-checkable specification layer.

## v0.17.1

### Updated

- Synchronized visible AI_Development_System versions in the root README files and `ai-system/README.md`.
- Documented `ai-system/system-changelog.md` as the authoritative version source for AI_Development_System.
- Updated the owner evolution plan and evolution backlog to mark `EVOL-002` as completed and recommend `EVOL-003` as the next bounded phase.

### Reason

Visible version fields had drifted between repository entrypoints and the changelog. `EVOL-002` resolves that drift without changing lifecycle states, approval gates, CI, security/privacy policy, specs, bootstrap tooling or product code.

## v0.17.0

### Added

- Added `evolution/owner-evolution-plan.md` as the Human Owner-authored intake place for high-level AI_Development_System evolution plans.
- Added `evolution/owner-plan-intake.md` to define how owner plans are recorded, preserved, mapped to roadmap/backlog items and converted into one bounded next task.
- Added `evolution/templates/owner-evolution-plan.md` as a reusable owner plan template.
- Recorded the owner plan from GitHub issue #7 as `OWNER-EVOL-001` with roadmap and evolution backlog mappings.

### Updated

- Updated the evolution module README and AI system README to index the owner plan intake workflow and template.
- Updated the operating model to include owner-authored evolution plan intake in System Evolution Governance.

### Reason

The Human Owner needs a clear place to provide broad system evolution direction while preserving roadmap/backlog discipline, one-task-at-a-time execution and Human Owner approval for behavior-changing system changes.

## v0.16.0

### Added

- Added `ai-system/evolution/` as an internal module for roadmap-driven self-evolution of AI_Development_System.
- Added `evolution/roadmap.md` to define strategic and tactical development priorities for the system itself.
- Added `evolution/evolution-loop.md` to define the controlled observe → diagnose → propose → plan → execute → verify → review → approve → release → learn loop.
- Added `evolution/evolution-policy.md` to define self-evolution boundaries, Human Owner approval requirements and anti-runaway rules.
- Added `evolution/system-health-check.md` as a repeatable system maturity and drift assessment checklist.
- Added `evolution/evolution-backlog.md` with initial evolution backlog items derived from owner direction and repository analysis findings.
- Added `evolution/analysis-report-baseline.md` to preserve the owner-provided analytical report as a roadmap input.
- Added system change proposal and bounded evolution task templates under `evolution/templates/`.

### Updated

- Updated AI system README to index the system evolution module and its templates.
- Updated operating model to mark System Evolution Governance as implemented.
- Updated highest-priority next steps to start from health check, version/status consistency, documentation integrity, security/privacy policy and pilot validation.

### Reason

AI_Development_System needs an explicit internal mechanism for evolving according to its own roadmap while preserving bounded execution, review, verification, changelog discipline and Human Owner approval.

## v0.15.0

### Added

- Added project control file standard for concrete repositories using AI_Development_System.
- Added project bootstrap workflow for empty and existing repositories.
- Added project integration model with Foldered Control Mode and Root Control Mode.
- Added project system update workflow for already integrated repositories.
- Added `OWNER_PLAN.md` as a Human Owner-authored plan intake file for concrete projects.
- Added explicit verification modes: `CODE_ONLY_FAST`, `FAST_VALIDATION`, `BROWSER_SMOKE` and `VISUAL_QA`.
- Added reusable root-mode project control file templates under `/ai-system/templates/project/`.
- Added reusable foldered templates under `/ai-system/templates/foldered/` for root `AGENTS.md`, `AI_Development_System/` and `AI_PROJECT/` integration.
- Added `AI_DEV_SYSTEM_VERSION.md` template for tracking local system adoption and update method.
- Added root README Quick Start guidance for installing, updating and using AI_Development_System in concrete projects.

### Updated

- Updated project control file standard to recommend Foldered Control Mode by default.
- Updated project bootstrap workflow with vendor-copy and git subtree installation commands.
- Updated prompt lifecycle guidance to include `Verification Mode:` in Codex prompt packages.
- Updated global rules and Codex workflow with on-demand browser and visual QA boundaries.
- Updated operator command documentation with verification mode shortcuts and `Разобрать план`.
- Updated root `README.md` with foldered install, update, day-to-day usage and verification mode summaries.
- Updated AI system README index to reference foldered integration docs and templates.

### Reason

Concrete project repositories need durable local control files, owner-authored planning input, explicit verification modes and a clean foldered integration model so AI_Development_System can be updated independently from local project state and application code.

## v0.14.2

### Added

- Added visible repository overview sections to the English and Russian root README files.
- Added text-based AI Development System schemes for roles, documents and process flow.

### Updated

- Updated root `README.md` with At a Glance, How Work Moves and Where to Start sections.
- Updated root `README.ru.md` with the same reader-facing overview in Russian.
- Updated AI system README to list `system-schemes.md`.

### Reason

Improves first-time repository onboarding and makes the system understandable at a glance for new readers.

## v0.14.1

### Added

- Added lifecycle glossary cross-links and simple lifecycle term definitions across the main glossary, execution glossary and evolution glossary.

### Updated

- Updated operating model next-step priorities after lifecycle glossary cross-links were added.

### Reason

Reduces terminology drift after implementing all lifecycle documents by linking major lifecycle terms to their glossary sections and source documents.

## v0.14.0

### Added

- Added Improvement Lifecycle for managed improvements, triage, recurring issue detection, root cause analysis, conversion criteria and closure rules.

### Updated

- Updated operating model to mark Improvement Lifecycle as implemented.
- Updated AI system README to list `improvement-lifecycle.md`.
- Updated next-step priorities after Improvement Lifecycle was added.

### Reason

Improvements need triage, recurring issue detection, conversion criteria and closure rules so the system can evolve without turning every observation into an immediate system change.

## v0.13.0

### Added

- Added Experiment Lifecycle for managed experiments, hypotheses, timeboxes, success and failure criteria, evaluation, adoption, rejection and rollback.

### Updated

- Updated operating model to mark Experiment Lifecycle as implemented.
- Updated AI system README to list `experiment-lifecycle.md`.
- Updated next-step priorities after Experiment Lifecycle was added.

### Reason

Experiments need explicit hypotheses, success criteria, evaluation, adoption, rejection and rollback before they can safely affect the AI Development System.

## v0.12.0

### Added

- Added Knowledge Lifecycle for managed knowledge, lessons learned, validation, promotion, deprecation, removal and archival.

### Updated

- Updated operating model to mark Knowledge Lifecycle as implemented.
- Updated AI system README to list `knowledge-lifecycle.md`.
- Updated next-step priorities after Knowledge Lifecycle was added.

### Reason

Enables the AI Development System to learn from reviews, improvements, repeated issues and decisions without turning every observation into an immediate rule.

## v0.11.0

### Added

- Added Review Lifecycle for managed reviews, review states, reviewer ownership, re-review flow and review closure rules.

### Updated

- Updated operating model to mark Review Lifecycle as implemented.
- Updated AI system README to list `review-lifecycle.md`, `lifecycle-governance.md` and `prompt-lifecycle.md`.
- Updated next-step priorities after Review Lifecycle was added.

### Reason

Closes the review governance gap before stronger pilot or production use by making review states, transition rules, ownership, re-review, closure and lifecycle relationships explicit.

## v0.10.0

### Added

- Added QA lifecycle for managed QA flows, test planning, test execution, regression checks and QA approval.

### Updated

- Updated operating model to mark QA Lifecycle as implemented.
- Updated AI system README to list `qa-lifecycle.md`.
- Updated next-step priorities after QA Lifecycle was added.

### Reason

Defines QA states, operations, ownership, defect reporting, rework flow, regression checks, QA approval, Human Owner approval requirements and AICP relationship.

## v0.9.0

### Added

- Added decision lifecycle for managed Human Owner decisions.

### Updated

- Updated operating model to mark Decision Lifecycle as implemented.
- Updated AI system README to list `decision-lifecycle.md`.
- Updated next-step priorities after Decision Lifecycle was added.

### Reason

Defines decision states, operations, ownership, revision, supersession, archival, Human Owner approval, AICP relationship and traceability across affected documents, changelog and git history.

## v0.8.0

### Added

- Added change lifecycle for managed AI Development System changes.

### Updated

- Updated operating model to mark Change Lifecycle as implemented.
- Updated AI system README to list `change-lifecycle.md`.
- Updated next-step priorities after Change Lifecycle was added.

### Reason

Defines system change states, operations, verification criteria, rollback rules, closure criteria, approval requirements, AICP relationship and audit history across improvement log, AICP, changelog and git history.

## v0.7.0

### Added

- Added Codex execution lifecycle for controlled repository execution.

### Updated

- Updated operating model to mark Codex Execution Lifecycle as implemented.
- Updated AI system README to list `codex-lifecycle.md`.
- Updated next-step priorities after Codex Execution Lifecycle was added.

### Reason

Defines Codex execution states, prompt approval, result intake, failure handling, rework flow, rollback handling and review boundaries while preserving Human Owner control.

## v0.6.0

### Added

- Added task lifecycle for managed AI Development System tasks.

### Updated

- Updated operating model to mark Task Lifecycle as implemented.
- Updated AI system README to list `task-lifecycle.md`.
- Updated next-step priorities after Task Lifecycle was added.

### Reason

Defines task states, operations, ownership, Definition of Ready and Definition of Done relationship, approval, AICP relationship, version impact and audit rules before adding Codex and QA lifecycles.

## v0.5.0

### Added

- Added process lifecycle for managed AI Development System processes.

### Updated

- Updated operating model to mark Process Lifecycle as implemented.
- Updated AI system README to list `process-lifecycle.md`.
- Updated next-step priorities after Process Lifecycle was added.

### Reason

Defines process states, operations, ownership, approval, AICP relationship, version impact and audit rules before adding task, Codex and QA lifecycles.

## v0.4.0

### Added

- Added document lifecycle for source-of-truth documents.

### Updated

- Updated operating model to mark Document Lifecycle as implemented.
- Updated AI system README to list `document-lifecycle.md`.

### Reason

Defines document states, operations, ownership, approval, AICP relationship, version impact and audit rules before adding more lifecycle documents.

## v0.3.0

### Added

- Added language and localization policy for Human Owner-facing responses, prompt packages and repository documentation.
- Added AICP-001 for the approved language policy change.
- Added Russian root README with language links from the English README.

### Updated

- Updated owner guide, prompt lifecycle, global rules, README, operating model and improvement log to reference the language policy.

### Reason

Makes output language predictable while keeping system control structures, prompt fields, mode markers and decision keywords stable.

## v0.2.0

### Added

- Added lifecycle governance as the common governance model for managed AI Development System entities.

### Updated

- Updated the operating model to register lifecycle governance as implemented.
- Updated the next-step priorities after lifecycle governance was added.

### Reason

Adds shared lifecycle states, ownership, approval, version impact, audit and history rules before creating more specific lifecycle documents.

## v0.1.0

### Added

- Added initial `/ai-system` documentation structure.
- Added system entrypoint.
- Added glossary index and glossary sections.
- Added system prompt.
- Added roles documentation.
- Added human interaction model.
- Added workflow.
- Added rules.
- Added task format.
- Added decision process.
- Added review process.
- Added change process.
- Added document templates.
- Added improvement log.

### Reason

Initial setup of the AI Development System as a documented part of the repository.

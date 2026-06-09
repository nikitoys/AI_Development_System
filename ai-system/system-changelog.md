# AI Development System Changelog

Status: Draft

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

# AI Development System Changelog

Status: Draft

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

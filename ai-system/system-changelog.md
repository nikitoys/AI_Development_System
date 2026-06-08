# AI Development System Changelog

Status: Draft

## v0.15.0

### Added

- Added project control file standard for concrete repositories using AI_Development_System.
- Added project bootstrap workflow for empty and existing repositories.
- Added `OWNER_PLAN.md` as a Human Owner-authored plan intake file for concrete projects.
- Added explicit verification modes: `CODE_ONLY_FAST`, `FAST_VALIDATION`, `BROWSER_SMOKE` and `VISUAL_QA`.
- Added reusable project control file templates under `/ai-system/templates/project/`.

### Updated

- Updated prompt lifecycle guidance to include `Verification Mode:` in Codex prompt packages.
- Updated global rules and Codex workflow with on-demand browser and visual QA boundaries.
- Updated operator command documentation with verification mode shortcuts and `Разобрать план`.

### Reason

Concrete project repositories need durable local control files, owner-authored planning input and explicit verification modes so Codex sessions can stay fast, scoped and predictable without running browser, Playwright, screenshot or manual visual QA checks unless explicitly requested.

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

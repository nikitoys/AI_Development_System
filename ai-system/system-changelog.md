# AI Development System Changelog

Status: Draft

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

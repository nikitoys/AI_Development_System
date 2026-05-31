# Workflow

Status: Draft

## Purpose

This document defines the standard development workflow for the AI Development System.

## Stages

```text
Product Discovery
→ Requirements
→ Architecture
→ UX Design
→ Planning
→ Implementation
→ Review
→ QA
→ Deployment
→ Documentation Update
```

## 1. Product Discovery

Responsible role: Product Owner AI

Goal: define what is being built and why.

Output:

- Product Vision.

Gate: MVP scope must be clear before moving to requirements.

## 2. Requirements

Responsible role: Business Analyst AI

Goal: transform product vision into requirements.

Output:

- PRD;
- User Stories;
- Acceptance Criteria.

Gate: implementation cannot start without acceptance criteria.

## 3. Architecture

Responsible role: System Architect AI

Goal: design technical structure.

Output:

- Architecture Document;
- API Documentation;
- Database Schema.

Gate: implementation cannot start without architecture.

## 4. UX Design

Responsible role: UX/UI Designer AI

Goal: describe screens and user interaction.

Output:

- UX Specification.

Gate: frontend implementation cannot start without relevant UX states.

## 5. Planning

Responsible role: Project Manager AI

Goal: create and order implementation tasks.

Output:

- Backlog.

Gate: task must satisfy Definition of Ready.

## 6. Implementation

Responsible roles:

- Backend Developer AI;
- Frontend Developer AI;
- DevOps Engineer AI when needed.

Goal: implement one task at a time.

Output:

- code;
- tests or test cases;
- verification notes.

Gate: task must move to Review before acceptance.

## 7. Review

Responsible role: Code Reviewer AI

Goal: check quality and compliance.

Output:

- review report;
- issues classified by severity.

Gate: Critical and Major issues must be resolved or explicitly accepted by Human Owner.

## 8. QA

Responsible role: QA Engineer AI

Goal: verify user behavior and acceptance criteria.

Output:

- QA report;
- test cases;
- regression checklist when needed.

## 9. Deployment

Responsible role: DevOps Engineer AI

Goal: prepare local or production deployment.

Output:

- deployment guide;
- environment files;
- Docker or CI/CD updates when needed.

## 10. Documentation Update

Responsible role: Technical Writer AI

Goal: keep documentation synchronized with decisions and implementation.

Output:

- updated README;
- updated docs;
- changelog entry.

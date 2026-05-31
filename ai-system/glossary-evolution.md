# Glossary — Evolution Terms

Status: Draft

## AI System Maintainer

A meta-role responsible for improving the AI Development System itself.

It analyzes process problems, proposes changes and prevents unnecessary complexity.

## Evolution

Controlled change of the AI Development System.

Can affect roles, rules, workflow, prompts, task format, templates or review process.

## Lifecycle Governance

The shared governance model for managed lifecycle documents.

Defined in `/ai-system/lifecycle-governance.md`.

## Managed Entity

An item controlled by a lifecycle, such as a task, review, decision, change, document, process, knowledge item, experiment or improvement.

## Lifecycle State

A named status that describes where a managed entity is in its lifecycle.

Examples: `Drafted`, `Approved`, `Active`, `Closed`, `Archived`.

## Lifecycle Operation

An allowed action that moves or updates a managed entity within its lifecycle.

Examples: review, approve, reject, defer, archive or roll back.

## Source of Truth

The approved document or record that controls the current meaning, rule or state of a system item.

If documents conflict, the source-of-truth document for that area controls the detailed rule.

## AICP

AI System Change Proposal.

A formal proposal to change the AI Development System.

## Change Proposal

A structured request to change the system.

Includes problem, evidence, root cause, proposed change, affected files, risks, decision and version impact.

## Version Impact

The expected version change caused by a system change:

- Patch;
- Minor;
- Major.

## Audit Rule

A rule that defines what evidence must be preserved to explain why a lifecycle action happened.

Audit rules support later review and accountability.

## History Rule

A rule that defines where lifecycle history is recorded, such as changelog, AICP, decision record, review report, task output or git history.

## Improvement Log

A log of observed process problems and improvement ideas.

It does not change the system directly.

## Improvement Lifecycle

The lifecycle for logged system improvements, including triage, root cause analysis, conversion, verification and closure.

Defined in `/ai-system/improvement-lifecycle.md`.

## Knowledge Lifecycle

The lifecycle for managed knowledge and lessons learned, including capture, validation, promotion, deprecation, removal and archival.

Defined in `/ai-system/knowledge-lifecycle.md`.

## Experiment Lifecycle

The lifecycle for managed experiments, including hypothesis, timebox, success criteria, failure criteria, evaluation, adoption, rejection and rollback.

Defined in `/ai-system/experiment-lifecycle.md`.

## Change Lifecycle

The lifecycle for managed AI Development System changes, including AICP, approval, application, verification, rollback and closure.

Defined in `/ai-system/change-lifecycle.md`.

## Decision Lifecycle

The lifecycle for Human Owner decisions, including proposal, clarification, approval, rejection, deferral, supersession and archival.

Defined in `/ai-system/decision-lifecycle.md`.

## Experiment

A temporary system change tested before permanent adoption.

## Experimental

A lifecycle status or condition where a change is being tested and has not yet become permanent system behavior.

Experimental work must have scope, approval, evaluation and rollback expectations.

## Pilot Validation

A controlled check of the AI Development System against real or realistic repository tasks before stronger production use.

Pilot validation is used to find missing examples, unclear transitions, documentation gaps and repeated process issues.

## System Changelog

History of changes to the AI Development System.

## System Version

Version of the AI Development System using `MAJOR.MINOR.PATCH`.

## Patch Version

Small correction to wording, prompts or formats.

## Minor Version

Addition of a role, rule, document or process step.

## Major Version

Significant workflow or operating model change.

## Deprecated

Still retained for context, but no longer recommended for new work.

A deprecated item should point to its replacement when one exists.

## Archived

Kept for history and audit only.

An archived item is not active guidance.

## Removed

Intentionally deleted from active source-of-truth locations.

Removal should preserve audit history when the item affected prior system behavior.

## Applied

A change proposal has been implemented in the repository.

## Rolled Back

A change proposal or experiment has been reverted.

## System Gate

A control point before changing the AI Development System.

The default system gate is: no system change without an accepted AICP.

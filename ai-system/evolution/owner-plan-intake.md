# Owner Plan Intake Workflow

Status: Draft  
Version: v0.1.0

## Purpose

This workflow defines how a high-level Human Owner evolution plan is recorded, mapped and converted into bounded AI_Development_System evolution work.

It exists to let the Human Owner provide direction without allowing Codex or AI roles to implement a broad plan automatically.

## Source Documents

Owner plan intake is governed by:

- `ai-system/evolution/owner-evolution-plan.md`;
- `ai-system/evolution/evolution-loop.md`;
- `ai-system/evolution/evolution-policy.md`;
- `ai-system/evolution/roadmap.md`;
- `ai-system/evolution/evolution-backlog.md`;
- `ai-system/evolution/templates/evolution-task.md`;
- `ai-system/evolution/templates/system-change-proposal.md`;
- `ai-system/change-process.md`;
- `ai-system/system-changelog.md`.

## Active Roles

Primary roles:

- AI System Maintainer;
- Technical Writer AI;
- Project Manager AI when task decomposition or sequencing is needed.

Decision owner:

- Human Owner.

Executor:

- Codex Executor, only for approved bounded tasks with explicit allowed files.

## Intake Flow

```text
Human Owner plan
  ->
Record plan
  ->
Preserve owner intent
  ->
Classify plan sections
  ->
Map to roadmap
  ->
Map to evolution backlog
  ->
Select one next bounded task
  ->
Prepare AICP or evolution task
  ->
Human Owner approval
  ->
Execute only the approved bounded task
```

## Step 1: Record Plan

Record the Human Owner plan in `owner-evolution-plan.md`.

Rules:

- preserve the original owner-authored wording where practical;
- do not silently remove constraints, priorities or uncertainty;
- add metadata separately from the owner-authored plan;
- do not treat the plan as approved implementation scope.

Output:

- owner plan recorded;
- plan metadata initialized.

## Step 2: Preserve Owner Intent

Separate the Human Owner's actual intent from AI interpretation.

Allowed additions:

- short intake notes;
- assumptions;
- open questions;
- candidate roadmap mappings;
- candidate backlog mappings.

Forbidden additions:

- invented requirements presented as owner decisions;
- hidden scope expansion;
- automatic approval of behavior-changing changes;
- implementation instructions for the whole plan.

Output:

- owner goals and constraints identified;
- unresolved questions visible.

## Step 3: Classify Plan Sections

Classify each meaningful plan section as one or more of:

- roadmap direction;
- evolution backlog candidate;
- AICP candidate;
- bounded evolution task candidate;
- experiment candidate;
- knowledge or lesson candidate;
- out-of-scope product work;
- duplicate of existing roadmap or backlog item;
- deferred idea.

Output:

- classification table in `owner-evolution-plan.md` or a linked intake note.

## Step 4: Map to Roadmap

Map each valid system evolution candidate to `roadmap.md`.

Rules:

- prefer mapping to an existing roadmap item when one fits;
- propose a roadmap update only when the plan introduces a direction not already covered;
- roadmap priority changes require Human Owner approval;
- roadmap updates that change system behavior must follow `evolution-policy.md` and `change-process.md`.

Output:

- roadmap mapping for each candidate;
- proposed roadmap changes, if needed.

## Step 5: Map to Evolution Backlog

Convert actionable candidates into `evolution-backlog.md` items.

Rules:

- one backlog item must describe one coherent improvement;
- each backlog item must reference a roadmap item or Human Owner request;
- each backlog item must include priority, owner, type, affected documents, expected outcome and acceptance criteria;
- behavior-changing backlog items must identify whether AICP is required;
- product implementation work must not be added to the system evolution backlog.

Output:

- proposed or updated evolution backlog items.

## Step 6: Select One Next Bounded Task

Select exactly one next task for execution.

Selection criteria:

- highest approved priority;
- smallest useful change;
- clear allowed files;
- clear acceptance criteria;
- no unresolved approval dependency;
- no dependency on implementing the whole owner plan.

Output:

- one next bounded task candidate.

## Step 7: Prepare Task or AICP

Use the correct path:

- use `templates/evolution-task.md` for bounded documentation, template, index or verification changes;
- use `templates/system-change-proposal.md` when governance, roles, lifecycle states, approval gates, security/privacy policy, integration contracts or system prompt behavior change.

The prepared package must include:

- Active Role;
- Active Stage;
- Active Document;
- Expected Result;
- source documents;
- scope and out of scope;
- allowed files;
- acceptance criteria;
- verification mode;
- review requirements;
- Human Owner approval requirement;
- changelog impact.

Output:

- one reviewable AICP or bounded evolution task.

## Step 8: Approval Gate

Human Owner approval is required before executing behavior-changing system changes.

Valid decision words:

- `APPROVED`;
- `REWORK`;
- `REJECTED`;
- `DEFERRED`;
- `EXPERIMENT`.

Output:

- Human Owner decision recorded or task held for review.

## Step 9: Execute Only the Approved Task

Codex Executor may modify only the approved allowed files for the selected bounded task.

Codex must not:

- implement the entire owner plan;
- modify product code;
- add unrelated system changes;
- remove approval gates;
- silently expand the allowed file list;
- mark future plan items as done.

Output:

- changed files for the approved task only;
- verification result;
- review notes;
- changelog or history update when required.

## Completion Criteria

Owner plan intake is complete when:

- the plan is recorded in `owner-evolution-plan.md`;
- plan sections are mapped to roadmap and/or evolution backlog candidates;
- one next bounded task or AICP is prepared;
- approval requirements are explicit;
- no unapproved plan items are executed.

## Minimal Rule

An owner-authored evolution plan creates direction, not permission to implement everything.

The system must convert the plan into roadmap, backlog and one bounded next task before execution.

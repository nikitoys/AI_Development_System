# Agent Results — {{PROJECT_NAME}}

Status: Draft

## Purpose

This file records project-local Agent Result intake and integration review status references.

Agent Result Intake does not accept final task results.

Integration Review does not replace QA or Human Owner final acceptance.

This file does not authorize execution, automatic merge or automatic acceptance.

## Safety Boundaries

- Sequential execution remains the default unless a Human Owner-approved parallel group exists.
- Results must be checked against scope, `allowed_files`, `locked_files`, `forbidden_actions`, dependencies and verification mode.
- Integration Review is required before acceptance for approved parallel execution groups.
- QA or documented QA decision is required before final acceptance when applicable.
- Human Owner remains the final decision maker.

## Result Intake Log

| Result ID | AWP ID | Agent Role | Status | Owner Review Required | Integration Review Required | Next Review Step |
|---|---|---|---|---|---|---|
| RES-001 | AWP-001 | TBD | needs_review | yes | unknown | Not ready. |

## Required Result Fields

Each result should include:

```text
result_id:
awp_id:
agent_id:
agent_role:
status:
summary:
changed_files:
  - path:
    action:
    reason:
    within_allowed_files:
claims:
  - claim:
    evidence:
    verification_status:
verification:
  mode:
  commands_run:
  result:
  limitations:
  not_run_reason:
risks:
blockers:
followups:
scope_compliance:
safety_boundary_compliance:
produced_artifacts:
owner_review_required:
integration_review_required:
parent_task:
sop:
verification_mode:
diff_or_key_changes:
dependency_notes:
review_notes:
qa_notes:
security_privacy_notes:
recommended_next_state:
```

Allowed result statuses:

```text
completed
partial
blocked
failed
needs_review
rejected
```

## Integration Review References

| Parent Task | Result Set | Integration Review Status | QA Handoff Status | Human Owner Acceptance |
|---|---|---|---|---|
| TBD | TBD | not started | not ready | not reached |

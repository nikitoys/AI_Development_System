<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `587`

Task: `PIPE-14 (TASK-065)` — **PIPE-14 Pipeline Audit Trail**
Epic: `EPIC-007`
Status: `in_progress`
Verification: `standard`
Ref: `PIPE-14`
UID: `tsk_b7153a9d28be`
Legacy ID: `TASK-065`
Aliases: `TASK-065`
Epic Key / Local Seq: `PIPE` / `14`

## Prompt Control Fields

Active Role: `AI System Maintainer / QA Engineer AI`
Active Stage: `Pipeline Audit Trail`
Active Document: `AI_PROJECT/events/pipeline-events.jsonl`
Expected Result: `Every pipeline decision and stop condition is auditable and visible in generated read-only output.`

## Summary

Record a complete audit trail for pipeline sessions, policy decisions, gates, Codex runs, reviews, stops, and commits.

## Description

Strengthen pipeline observability by adding structured audit events and generated timeline output for all supervised batch decisions.

## Scope

- Define pipeline event types for session create, policy selected, queue planned, task selected, Change created/approved/accepted, context built, token gate result, Codex run result, report gate result, machine review, Codex review, close/rework decision, commit readiness, commit result, stop, and completion.
- Append events through governed pipeline services only.
- Generate a readable Pipeline Audit or Pipeline Status timeline if useful.
- Include stable ids for session, task, Change, report, review, gate, and commit references.
- Avoid storing secrets or excessive raw prompt contents in audit events.
- Add tests for event append, validation, generated output freshness, and redaction/sizing behavior.

## Out of Scope

- Do not make audit logs editable from UI.
- Do not store raw secrets.
- Do not store full huge prompt payloads when hashes/paths are sufficient.
- Do not replace existing task/evolution/codex/context event logs.

## Allowed Files

- ai_project_ctl/pipeline/audit.py
- ai_project_ctl/pipeline/session.py
- ai_project_ctl/pipeline/** if integration is needed
- AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_AUDIT.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only
- tests/**
- ai-system/project-control/** if audit documentation is needed

## Acceptance Criteria

- Pipeline audit captures every major gate and decision.
- Audit events include stable references and stop reasons.
- Audit avoids raw secrets and oversized prompt payloads.
- Generated audit/status output is derived and can be refreshed/check-generated if implemented.
- Tests and project-control validations pass.

## Review Instructions

- Verify event/state/generated separation.
- Verify audit is sufficient to reconstruct why pipeline stopped.

## Notes

- Requires approved Evolution Change before execution because this adds pipeline audit behavior.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-065 --to in_progress
python scripts/taskctl.py task transition TASK-065 --to in_review
python scripts/taskctl.py task approve TASK-065 --notes "..."
python scripts/taskctl.py task transition TASK-065 --to done
python scripts/aictl.py task report submit --task TASK-065 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

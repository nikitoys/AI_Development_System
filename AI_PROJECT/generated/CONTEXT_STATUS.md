<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-065 PIPE-14 Pipeline Audit Trail Record a complete audit trail for pipeline sessions, policy decisions, gates, Codex runs, reviews, stops, and commits. Strengthen pipeline observability by adding structured audit events and generated timeline output for all supervised batch decisions. AI_PROJECT/events/pipeline-events.jsonl Every pipeline decision and stop condition is auditable and visible in generated read-only output. Define pipeline event types for session create, policy selected, queue planned, task selected, Change created/approved/accepted, context built, token gate result, Codex run result, report gate result, machine review, Codex review, close/rework decision, commit readiness, commit result, stop, and completion. Append events through governed pipeline services only. Generate a readable Pipeline Audit or Pipeline Status timeline if useful. Include stable ids for session, task, Change, report, review, gate, and commit references. Avoid storing secrets or excessive raw prompt contents in audit events. Add tests for event append, validation, generated output freshness, and redaction/sizing behavior. Do not make audit logs editable from UI. Do not store raw secrets. Do not store full huge prompt payloads when hashes/paths are sufficient. Do not replace existing task/evolution/codex/context event logs. ai_project_ctl/pipeline/audit.py ai_project_ctl/pipeline/session.py ai_project_ctl/pipeline/** if integration is needed AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only AI_PROJECT/generated/PIPELINE_AUDIT.md via governed CLI/service only AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only tests/** ai-system/project-control/** if audit documentation is needed Pipeline audit captures every major gate and decision. Audit events include stable references and stop reasons. Audit avoids raw secrets and oversized prompt payloads. Generated audit/status output is derived and can be refreshed/check-generated if implemented. Tests and project-control validations pass. Verify event/state/generated separation. Verify audit is sufficient to reconstruct why pipeline stopped.","schema_version":1,"task_id":"TASK-065"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-065`
Limit: `8`
Docs revision: `24`
Tasks revision: `587`
Indexed source documents: `10`
Indexed chunks: `890`
Selected chunks: `8`
Excluded registered sources: `134`

## Selected Source Paths

- ai-system/project-control/03-state-model.md
- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `93`
- template document excluded by default: `41`

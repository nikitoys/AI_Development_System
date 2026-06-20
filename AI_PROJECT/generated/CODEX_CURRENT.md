<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `611`

Task: `PIPE-24 (TASK-075)` — **PIPE-24 Add Owner-Approved Session Changes Policy Checkbox**
Epic: `EPIC-007`
Status: `in_review`
Verification: `strict`
Ref: `PIPE-24`
UID: `tsk_c55990cd59ea`
Legacy ID: `TASK-075`
Aliases: `TASK-075`
Epic Key / Local Seq: `PIPE` / `24`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Add a pipeline policy checkbox that lets the Human Owner approve all required Changes for the selected session queue as part of the pipeline run.

## Description

Add a safe owner-approved policy mode for approving required Evolution Changes across the selected pipeline session. This is not autonomous pipeline self-approval: the Human Owner must explicitly select the policy checkbox, confirm the session, and provide an approval note. The pipeline may then approve only the Changes required by that selected session queue.

## Scope

- Add a new safe policy field distinct from evolution.approve_linked_change, for example evolution.owner_approve_required_changes_for_session.
- Do not reuse approve_linked_change if it represents autonomous policy self-approval.
- Require explicit Human Owner confirmation when this checkbox is enabled.
- Require an approval note/reason when this checkbox is enabled.
- Store owner approval intent in the pipeline session snapshot.
- Approve only Changes linked to tasks selected by the current pipeline session queue.
- If Auto-create missing Changes is also enabled, allow pipeline to create missing Changes and approve those newly created Changes in the same owner-confirmed session.
- If a selected task has an existing ready/proposed linked Change, allow the session approval policy to approve it.
- Do not approve Changes outside the selected session queue.
- Do not accept Changes automatically.
- Do not approve Changes if the owner approval checkbox was not explicitly enabled.
- Add Web Control Center checkbox: Owner-approve required Changes for this session.
- Add approval note field to Pipeline session create form when checkbox is enabled.
- Add Policy Preview rows for Owner Session Change Approval and Approval Note Required.
- Add CLI support for equivalent flags, for example --owner-approve-required-changes and --approval-note.
- Update pipeline audit to record approved Change ids, linked task refs, actor, approval note, and session id.
- After required Changes are approved, pipeline should continue the same session if resume/waiting behavior is available.
- Add tests for approving multiple Changes in one owner-confirmed pipeline run.

## Out of Scope

- Do not allow fully autonomous approval without Human Owner confirmation.
- Do not make evolution.approve_linked_change valid if it means unsafe auto-approval.
- Do not accept Evolution Changes automatically.
- Do not approve unrelated Changes outside the selected session queue.
- Do not bypass Codex execution, token, report, machine review, Codex review, task close, or commit gates.
- Do not push, merge, reset, rebase, clean, restore, or discard git changes.
- Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.

## Allowed Files

- ai_project_ctl/pipeline/policy.py
- ai_project_ctl/pipeline/runner.py
- ai_project_ctl/pipeline/session.py
- ai_project_ctl/pipeline/state.py
- ai_project_ctl/pipeline/batch.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/registry.py
- ai_project_ctl/core/workflows.py
- scripts/aictl.py
- scripts/evolutionctl.py if existing approve command integration is needed
- tests/test_pipeline_runner.py
- tests/test_pipeline_batch.py
- tests/test_web_control_center.py
- tests/test_aictl.py
- tests/test_registry.py
- AI_PROJECT/state/evolution.json via governed CLI/service only
- AI_PROJECT/events/evolution-events.jsonl via governed CLI/service only
- AI_PROJECT/state/pipeline_sessions.json via governed CLI/service only
- AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/EVOLUTION_STATUS.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_AUDIT.md via governed CLI/service only

## Acceptance Criteria

- Pipeline UI has an Owner-approve required Changes for this session checkbox.
- Checkbox requires explicit confirmation and approval note.
- Policy preview clearly distinguishes owner-approved session approval from unsafe automatic approval.
- Policy validation still rejects unsafe autonomous evolution.approve_linked_change = true.
- When enabled, pipeline approves only required Changes linked to tasks in the selected session queue.
- When combined with Auto-create missing Changes, pipeline can create and owner-approve required Changes for PIPE-17..PIPE-21 in one confirmed session flow.
- Approved Change ids, task refs, actor, approval note, and session id are recorded in audit.
- Pipeline can continue the same session after approval.
- No Change is accepted automatically.
- No unrelated Change is approved.
- Tests pass.

## Review Instructions

- Create a session for PIPE-17..PIPE-21 with both Auto-create missing Changes and Owner-approve required Changes enabled.
- Provide an approval note and confirm.
- Verify missing Changes are created where needed.
- Verify required Changes for the selected queue are approved.
- Verify no unrelated Changes are approved.
- Verify the same session continues after approval.
- Verify audit trail contains owner approval evidence.

## Notes

- This implements the desired checkbox-based approval UX.
- The key distinction: policy may carry owner approval intent for this session, but must not become autonomous pipeline self-approval.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-075 --to in_progress
python scripts/taskctl.py task transition TASK-075 --to in_review
python scripts/taskctl.py task approve TASK-075 --notes "..."
python scripts/taskctl.py task transition TASK-075 --to done
python scripts/aictl.py task report submit --task TASK-075 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

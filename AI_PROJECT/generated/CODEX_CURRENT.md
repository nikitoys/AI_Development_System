<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `552`

Task: `PIPE-11 (TASK-062)` — **PIPE-11 Auto Review Auto Close Policy**
Epic: `EPIC-007`
Status: `in_review`
Verification: `strict`
Ref: `PIPE-11`
UID: `tsk_01a078bae3e6`
Legacy ID: `TASK-062`
Aliases: `TASK-062`
Epic Key / Local Seq: `PIPE` / `11`

## Prompt Control Fields

Active Role: `AI System Maintainer / QA Lead AI`
Active Stage: `Auto Review and Close Policy`
Active Document: `ai_project_ctl/pipeline/close_policy.py`
Expected Result: `Pipeline can safely close or request changes for tasks only when policy and review gates allow it.`

## Summary

Apply policy-controlled close/rework decisions only after Machine Review PASS and Codex Review APPROVE.

## Description

Implement the decision logic that maps review gate results into task done, changes_requested, rework loop, or stop states under explicit automation policy.

## Scope

- Implement decision logic for Machine Review result plus Codex Review result.
- Allow auto-close only if policy allows and Machine Review PASS and Codex Review APPROVE.
- Move task to changes_requested or start a bounded rework loop only when policy allows and review verdict requests changes.
- Stop when review is blocked, malformed, failing, or policy disallows automatic lifecycle mutation.
- Require explicit audit notes that identify policy, machine gate, Codex review verdict, and report id.
- Prevent auto-close when task report has blockers or changed files outside allowed_files.
- Add tests for approve+pass close, request changes, blocked review, machine fail, policy disabled, and rework-limit reached.

## Out of Scope

- Do not bypass task lifecycle transitions.
- Do not accept linked Evolution Changes.
- Do not commit.
- Do not treat Codex Review as Human Owner approval outside the selected policy.
- Do not continue rework indefinitely.

## Allowed Files

- ai_project_ctl/pipeline/close_policy.py
- ai_project_ctl/pipeline/runner.py if integration is needed
- ai_project_ctl/core/workflows.py if close/request-changes workflow metadata needs compatible updates
- tests/**
- ai-system/project-control/** if auto-close documentation is needed

## Acceptance Criteria

- Auto-close requires policy permission, Machine Review PASS, and Codex Review APPROVE.
- REQUEST_CHANGES moves to changes_requested or starts rework only if policy allows.
- Blocked or failed gates stop the pipeline.
- Rework loop has a policy-controlled maximum.
- Lifecycle mutations route through governed task workflows/commands.
- Tests and project-control validations pass.

## Review Instructions

- Verify auto-close cannot happen on Machine Review FAIL or Codex Review REQUEST_CHANGES.
- Verify lifecycle changes are routed through governed commands.

## Notes

- Requires approved Evolution Change before execution because this adds automated lifecycle decisions.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-062 --to in_progress
python scripts/taskctl.py task transition TASK-062 --to in_review
python scripts/taskctl.py task approve TASK-062 --notes "..."
python scripts/taskctl.py task transition TASK-062 --to done
python scripts/aictl.py task report submit --task TASK-062 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

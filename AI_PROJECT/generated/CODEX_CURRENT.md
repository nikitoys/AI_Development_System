<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `556`

Task: `PIPE-12 (TASK-063)` — **PIPE-12 Controlled Git Commit Action**
Epic: `EPIC-007`
Status: `in_progress`
Verification: `strict`
Ref: `PIPE-12`
UID: `tsk_6f7cf68ecdf8`
Legacy ID: `TASK-063`
Aliases: `TASK-063`
Epic Key / Local Seq: `PIPE` / `12`

## Prompt Control Fields

Active Role: `DevOps Engineer AI / Git Safety Reviewer`
Active Stage: `Controlled Local Commit Action`
Active Document: `ai_project_ctl/pipeline/git_commit.py`
Expected Result: `Pipeline can optionally create a local commit only when commit policy allows and readiness checks are green.`

## Summary

Create local commits only when policy allows and commit readiness is green.

## Description

Add a controlled local git commit action for completed pipeline work. It must never push, merge, reset, discard, or create remote changes.

## Scope

- Implement read-only commit readiness check reuse or integration with the existing Commit Readiness view.
- Implement local commit action only behind explicit policy permission.
- Require clean readiness: task done, required Change accepted if policy requires it, machine checks pass, protected-file checks pass, generated outputs fresh, no unrelated dirty files unless policy explicitly allows.
- Stage only files approved by policy/session evidence.
- Generate commit message from completed task refs, Change ids, and session id.
- Run git commit locally only; explicitly forbid push, merge, reset, checkout, rebase, and destructive git commands.
- Record commit hash or failure in pipeline session/audit.
- Add tests with fake git runner for readiness green, readiness fail, unrelated files, commit success, and forbidden command attempts.

## Out of Scope

- Do not push.
- Do not merge.
- Do not open PRs.
- Do not discard or reset changes.
- Do not commit when readiness is not green.
- Do not auto-accept Changes in this task.

## Allowed Files

- ai_project_ctl/pipeline/git_commit.py
- ai_project_ctl/pipeline/runner.py if integration is needed
- ai_project_ctl/web/read_model.py if commit readiness data is reused
- ai_project_ctl/core/registry.py if command metadata is needed
- scripts/aictl.py if commit command routing is needed
- tests/**
- ai-system/project-control/** if git commit policy documentation is needed

## Acceptance Criteria

- Commit action is disabled unless policy explicitly allows local commit.
- Commit action refuses when commit readiness is not green.
- Commit action stages only approved files.
- Commit action never pushes, merges, resets, rebases, or discards changes.
- Commit result is recorded in session/audit.
- Tests and project-control validations pass.

## Review Instructions

- Verify command allowlist forbids push/merge/destructive git actions.
- Verify readiness failure blocks commit.

## Notes

- Requires approved Evolution Change before execution because this adds git mutation behavior.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-063 --to in_progress
python scripts/taskctl.py task transition TASK-063 --to in_review
python scripts/taskctl.py task approve TASK-063 --notes "..."
python scripts/taskctl.py task transition TASK-063 --to done
python scripts/aictl.py task report submit --task TASK-063 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

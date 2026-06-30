<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `1880`

Task: `PIPEF-172 (TASK-277)` — **Allow governed close side effects in local commit readiness**
Epic: `EPIC-009`
Status: `in_progress`
Verification: `strict`
Ref: `PIPEF-172`
UID: `tsk_8163c89f10e7`
Legacy ID: `TASK-277`
Aliases: `TASK-277`
Epic Key / Local Seq: `PIPEF` / `172`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Update local commit readiness so current-session governed close side effects can be committed without allowing unrelated AI_PROJECT dirty files.

## Description

Fix the PSESS-151 class of failures where task gates pass but local commit blocks with COMMIT_UNRELATED_FILES because governed close side effects are not included in approved evidence.

## Scope

- Extend commit readiness approved-file collection to recognize governed side effects owned by the current pipeline session.
- Keep pre-existing dirty governed files and non-session-owned AI_PROJECT files blocked as unrelated.
- Preserve the existing requirement for non-governed target task artifact evidence before committing governed session side effects.
- Add a regression that covers a successful local commit with task artifact changes plus session-owned task/report/codex/context/evolution/pipeline side effects.
- Add or keep a negative regression proving unrelated governed dirty files still fail with COMMIT_UNRELATED_FILES.

## Out of Scope

- Do not allow blanket commits of all AI_PROJECT/** paths.
- Do not bypass commit readiness, report gate, machine review, or task done requirements.
- Do not edit protected project-control files manually.
- Do not change behavior unrelated to local commit readiness.

## Allowed Files

- ai_project_ctl/pipeline/git_commit.py
- ai_project_ctl/pipeline/close_phase.py
- ai_project_ctl/pipeline/session.py
- tests/test_pipeline_runner.py
- tests/test_web_run_local_commit_e2e.py
- tests/test_web_control_center.py

## Acceptance Criteria

- Commit readiness passes for a clean-baseline pipeline session that has target task artifact evidence and current-session governed close side effects.
- Local commit creation stages only approved target artifact files and current-session governed side-effect files.
- Pre-existing dirty governed files that are not owned by the current session still block with COMMIT_UNRELATED_FILES.
- Arbitrary AI_PROJECT/** files that are not approved by report, side effects, or current-session evidence still block with COMMIT_UNRELATED_FILES.
- Commit readiness still blocks governed-only changes when the selected task has no non-governed target artifact evidence.
- python -m pytest tests/test_pipeline_runner.py -q passes.
- python -m pytest tests/test_web_run_local_commit_e2e.py -q passes.

## Review Instructions

- Review that approved governed paths are derived from current-session evidence or explicit side effects, not from a broad AI_PROJECT/** allowlist.
- Check both positive and negative tests for COMMIT_UNRELATED_FILES behavior.

## Notes

- Observed evidence: PSESS-151 reached close with TASK-273 gates passed, then blocked on COMMIT_READINESS_FAILED / COMMIT_UNRELATED_FILES.
- Current git_commit.py only treats the four pipeline bookkeeping files as session-owned governed files, which misses task, report, codex, context, and evolution close side effects.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-277 --to in_progress
python scripts/taskctl.py task transition TASK-277 --to in_review
python scripts/taskctl.py task approve TASK-277 --notes "..."
python scripts/taskctl.py task transition TASK-277 --to done
python scripts/aictl.py task report submit --task TASK-277 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

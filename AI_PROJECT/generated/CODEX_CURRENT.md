<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `539`

Task: `PIPE-09 (TASK-060)` — **PIPE-09 Machine Review Gate**
Epic: `EPIC-007`
Status: `in_progress`
Verification: `strict`
Ref: `PIPE-09`
UID: `tsk_2b44723c1bdb`
Legacy ID: `TASK-060`
Aliases: `TASK-060`
Epic Key / Local Seq: `PIPE` / `9`

## Prompt Control Fields

Active Role: `QA Engineer AI / Project Control Maintainer`
Active Stage: `Machine Review Gate Implementation`
Active Document: `ai_project_ctl/pipeline/machine_review.py`
Expected Result: `Pipeline has a deterministic Machine Review PASS/WARN/FAIL gate before semantic review and auto-close.`

## Summary

Run deterministic machine checks for tests, doctor, protected files, generated outputs, allowed_files, token usage, and blockers.

## Description

Implement the machine review gate that collects deterministic evidence before Codex semantic review or auto-close decisions.

## Scope

- Run or collect project-control validation checks: task validate, task graph validate, generated checks, evolution validate/check-generated, context validate/check-generated, project doctor, and protected-file check.
- Run task/report-declared tests or configured test commands only when policy allows and commands are safe.
- Check changed files against task allowed_files and protected-file rules.
- Check report blockers and token usage against policy.
- Return PASS only when all blocking checks pass.
- Return structured evidence with command, result, duration if available, stdout/stderr summaries, and failure reasons.
- Add tests with fake command runners and representative pass/fail cases.

## Out of Scope

- Do not do semantic acceptance review.
- Do not close tasks.
- Do not accept Changes.
- Do not commit.
- Do not suppress doctor/protected-file failures.

## Allowed Files

- ai_project_ctl/pipeline/machine_review.py
- ai_project_ctl/pipeline/report_gate.py if integration is needed
- ai_project_ctl/pipeline/runner.py if integration is needed
- ai_project_ctl/core/registry.py if command metadata is needed
- scripts/aictl.py if gate command routing is needed
- tests/**
- ai-system/project-control/** if machine review documentation is needed

## Acceptance Criteria

- Machine Review PASS requires all blocking checks to pass.
- Machine Review FAIL stops the pipeline.
- Protected-file and allowed_files violations are blocking.
- Token usage and report blockers are checked according to policy.
- Gate output is structured and auditable.
- Tests and project-control validations pass.

## Review Instructions

- Verify that deterministic checks are actually blocking.
- Verify that allowed_files/protected-file checks cannot be bypassed by report wording.

## Notes

- Requires approved Evolution Change before execution because this adds a pipeline review gate.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-060 --to in_progress
python scripts/taskctl.py task transition TASK-060 --to in_review
python scripts/taskctl.py task approve TASK-060 --notes "..."
python scripts/taskctl.py task transition TASK-060 --to done
python scripts/aictl.py task report submit --task TASK-060 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

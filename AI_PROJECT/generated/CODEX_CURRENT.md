<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `451`

Task: `WFA-11 (TASK-042)` — **UIX-05 Add Bulk Task Import from file**
Epic: `EPIC-006`
Status: `in_progress`
Verification: `standard`
Ref: `WFA-11`
UID: `tsk_82ea27760cf4`
Legacy ID: `TASK-042`
Aliases: `TASK-042`
Epic Key / Local Seq: `WFA` / `11`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Extend Bulk Task Import to support uploading JSON files in addition to pasted JSON text.

## Description

Allow the owner to import task batches from a local JSON file while preserving preview, validation, confirmation, and governed command-path creation.

## Scope

- Add file upload support for Bulk Task Import.
- Support UTF-8 .json or .txt files containing JSON import payloads.
- Enforce conservative file size limit.
- Parse file content as data only.
- Reuse existing preview/dry-run behavior.
- Reuse existing validation before writes.
- Reuse existing confirmed command-path task creation.
- Show clear parse/validation errors.
- Keep paste-based import working.

## Out of Scope

- Do not execute uploaded files.
- Do not support Python, shell scripts, or unrestricted executable formats.
- Do not add YAML dependency unless already allowed by existing project dependency policy.
- Do not auto-start imported tasks.
- Do not auto-approve anything.
- Do not write tasks.json directly.

## Allowed Files

- ai_project_ctl/web/actions.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/core/workflows.py if import payload handling needs compatible updates
- scripts/aictl.py if import routing needs compatible updates
- tests/test_web_control_center.py
- tests/test_workflows.py
- tests/test_aictl.py

## Acceptance Criteria

- Owner can import a task batch by uploading a JSON/text file.
- Paste-based JSON import still works.
- Importer shows preview before creation.
- Invalid file type, invalid JSON, invalid refs, or oversized file fails before creation.
- Confirmed import creates tasks only through governed command paths.
- No direct tasks.json writes are introduced.
- Tests and project-control validations pass.

## Review Instructions

- Verify that uploaded file content is parsed as data only.
- Verify that no executable content is run.
- Verify that invalid imports create no tasks.

## Notes

- Logical label: UIX-05
- Depends logically on WFA-04 and UIX-03.
- Requires approved Evolution Change before execution because Web import behavior changes.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-042 --to in_progress
python scripts/taskctl.py task transition TASK-042 --to in_review
python scripts/taskctl.py task approve TASK-042 --notes "..."
python scripts/taskctl.py task transition TASK-042 --to done
python scripts/aictl.py task report submit --task TASK-042 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-046 UIX-09 Add Codex Execution Report Submission Add a governed way for Codex to submit structured task execution reports through aictl instead of relying on manual pasted summaries. Introduce a machine-readable Codex execution report flow. At the end of task execution, Codex should be able to write a structured JSON report and submit it through a governed CLI command. The report must be validated, stored through project-control state/events, and made available to the Web Control Center for task review. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Define a JSON schema for Codex execution reports. Support fields for task id/ref, implementation summary, changed files, generated files, checks, warnings, blockers, notes, and owner decision required. Add a governed command such as aictl task report submit --task <TASK> --file <REPORT> --confirm. Validate task reference and report shape before storing anything. Store report data through project-control state/events, not by directly editing tasks.json. Link the latest report to the task for UI review. Generate or expose a latest review summary for read models. Update Codex prompt guidance so Codex knows to submit a structured report when the command exists. Add tests for valid report, invalid task, invalid schema, missing file, and no direct state writes. Do not allow Codex to edit tasks.json directly. Do not accept arbitrary executable report content. Do not auto-approve or auto-close tasks based on report content. Do not treat a submitted report as Human Owner acceptance. Do not bypass protected-file validation. Do not require external services or databases. ai_project_ctl/core/workflows.py ai_project_ctl/core/registry.py ai_project_ctl/web/read_model.py scripts/aictl.py scripts/taskctl.py if a task-domain report command is needed AI_PROJECT/state/task_reports.json via governed CLI only AI_PROJECT/events/task-report-events.jsonl via governed CLI only AI_PROJECT/generated/** via owning render/check commands only tests/test_workflows.py tests/test_aictl.py tests/test_registry.py tests/test_web_control_center.py Codex execution report JSON schema is documented or encoded in validation. Report submission command validates task identity and report shape. Valid reports are stored through governed state/events only. Invalid reports fail without partial writes. Task review read model can access the latest report for a task. Submitting a report does not approve, close, or transition the task by itself. Tests and project-control validations pass. Verify that reports are submitted through CLI only. Verify that tasks.json is not directly edited for full report storage. Verify that report submission does not replace Human Owner review. Verify that invalid reports create no persistent state.","schema_version":1,"task_id":"TASK-046"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-046`
Limit: `8`
Docs revision: `23`
Tasks revision: `427`
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

<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-040 UIX-03 Add unified workflow action result panel Add a reusable result panel for workflow and Web actions showing step status, changed files, warnings, errors, and next actions. Improve owner feedback after UI actions by showing what was executed, what changed, what failed, and what to do next. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add a reusable action result view/component. Show workflow name and target task/change/epic. Show step-by-step PASS/WARN/FAIL status. Show changed files when available. Show generated files when available. Show warnings and errors clearly. Show next-action hints such as the Codex prompt instruction. Support copyable text for the Codex instruction. Do not change workflow semantics. Do not add new workflow actions in this task. Do not auto-run Codex. Do not weaken confirmation requirements. Do not directly edit protected project-control files. ai_project_ctl/web/server.py ai_project_ctl/web/read_model.py ai_project_ctl/web/actions.py ai_project_ctl/core/workflows.py if result metadata needs compatible updates tests/test_web_control_center.py tests/test_workflows.py After a workflow action, UI shows a clear action result panel. Result panel shows executed steps and status. Result panel shows warnings/errors without hiding failures. Result panel includes next action hints when available. Prepare for Codex result includes a copyable Codex instruction. Existing workflow safety is preserved. Tests and project-control validations pass. Verify that failed steps are visible and not hidden behind a generic success message. Verify that result panel does not expose arbitrary command execution.","schema_version":1,"task_id":"TASK-040"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-040`
Limit: `8`
Docs revision: `23`
Tasks revision: `379`
Indexed source documents: `10`
Indexed chunks: `890`
Selected chunks: `8`
Excluded registered sources: `134`

## Selected Source Paths

- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/project-control/07-validation-and-tests.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `93`
- template document excluded by default: `41`

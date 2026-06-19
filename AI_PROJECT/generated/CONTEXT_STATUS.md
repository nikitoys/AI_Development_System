<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-034 WFA-03 Add Task Creation Wizard Add owner-facing CLI/UI workflow for creating individual tasks without long taskctl.py command lines. Provide a guided task creation form/workflow that routes through taskctl.py/aictl command layer and supports scope, out-of-scope, allowed files, acceptance criteria, review instructions, dependencies, and optional Evolution Change hint. AI_PROJECT/generated/CODEX_TASKS.md Task creation wizard is implemented through approved command paths. Add task creation workflow metadata. Add UI form or CLI wizard-like command if allowed. Support Epic selection. Support scope/out-of-scope/allowed-files/acceptance/review fields. Support depends_on selection. Support create-only mode. Optionally offer next action suggestions: prepare for Codex, create Evolution Change. Add tests. Do not implement grouped import in this task. Do not auto-start the created task. Do not auto-create Evolution Change unless explicitly delegated to WFA-02 workflow. Do not bypass taskctl validation. ai_project_ctl/core/workflows.py ai_project_ctl/web/actions.py ai_project_ctl/web/server.py ai_project_ctl/web/read_model.py ai_project_ctl/core/registry.py scripts/aictl.py tests/** Owner can create a single task through workflow/UI without manually writing a long CLI command. Created task is persisted through approved command path. Generated task views are refreshed through owning CLI/facade. Task dependencies can be added where supported. No direct protected-file edits. Tests and validations pass. Verify taskctl/aictl routing, create-only behavior, dependency support, protected-file policy, tests, and validation output.","schema_version":1,"task_id":"TASK-034"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-034`
Limit: `8`
Docs revision: `22`
Tasks revision: `317`
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

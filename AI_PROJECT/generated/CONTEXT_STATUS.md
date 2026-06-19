<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-036 WFA-05 Add Review And Close Helpers Add guarded workflow helpers for closing reviewed tasks, accepting linked Evolution Changes, and optionally closing completed Epics. Reduce manual closure steps while preserving explicit Human Owner confirmation and approval gates. AI_PROJECT/generated/CODEX_TASKS.md Review and close helpers are implemented without bypassing lifecycle gates or owner confirmation. Add close_task workflow for tasks in in_review. Require approval notes and explicit confirmation. Approve task then transition to done through taskctl/aictl path. Add accept_change workflow only for approved/in_review changes whose linked tasks are done. Add optional close_epic helper only if all child tasks are done/deferred/archived. Add tests for confirmation, invalid states, and blocked closure. Do not auto-approve without Human Owner confirmation. Do not close tasks with failing checks unless explicitly allowed by policy. Do not accept Changes with incomplete linked tasks. Do not close Epics with active tasks. Do not bypass lifecycle gates. ai_project_ctl/core/workflows.py ai_project_ctl/web/actions.py ai_project_ctl/web/server.py ai_project_ctl/web/read_model.py ai_project_ctl/core/registry.py scripts/aictl.py tests/** Owner can close an in_review task with explicit notes and confirmation. Owner can accept an Evolution Change only when linked task completion rules pass. Invalid close/accept attempts are rejected with clear messages. Existing lifecycle semantics are preserved. Tests and validations pass. Verify lifecycle gate preservation, owner confirmation, invalid-state handling, protected-file policy, tests, and validation output.","schema_version":1,"task_id":"TASK-036"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-036`
Limit: `8`
Docs revision: `22`
Tasks revision: `327`
Indexed source documents: `10`
Indexed chunks: `890`
Selected chunks: `8`
Excluded registered sources: `134`

## Selected Source Paths

- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/05-lifecycle-rules.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/project-control/07-validation-and-tests.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `93`
- template document excluded by default: `41`

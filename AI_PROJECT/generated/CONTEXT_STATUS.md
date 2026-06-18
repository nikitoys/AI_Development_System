<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-024 Task F - Implement unified CLI facade scripts/aictl.py Create one preferred entrypoint for project-control operations. Add scripts/aictl.py as a unified CLI facade over shared domain services, supporting human-readable output and --json automation output while preserving existing taskctl/evolutionctl/docctl/contextctl/codexctl behavior. scripts/aictl.py aictl facade works through shared services and existing ctl scripts remain functional. Implement commands such as task list, task show, task transition, epic list, context build, codex prompt build, project doctor, project render, command list, and command describe as supported by shared services. Support human-readable output. Support --json output for automation. Ensure aictl calls shared domain services and command registry instead of duplicating lifecycle logic. Add tests or smoke coverage for representative read and write commands. Do not remove legacy ctl scripts. Do not add web UI in this task. Do not implement unsupported commands without validation. scripts/aictl.py ai_project_ctl/** tests/** AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only aictl can call shared domain services. aictl supports human-readable output. aictl supports --json for automation. Existing taskctl/evolutionctl behavior is not broken. Verify aictl delegates to validated shared services and does not mutate protected files directly. Verify existing ctl command compatibility after aictl is introduced.","schema_version":1,"task_id":"TASK-024"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-024`
Limit: `8`
Docs revision: `19`
Tasks revision: `225`
Indexed source documents: `10`
Indexed chunks: `890`
Selected chunks: `8`
Excluded registered sources: `130`

## Selected Source Paths

- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/project-control/07-validation-and-tests.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `89`
- template document excluded by default: `41`

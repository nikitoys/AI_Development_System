<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-023 Task E - Add command registry Make project-control operations discoverable and callable through one registry. Introduce command metadata with names, descriptions, argument schema, read/write metadata, and output format metadata so both CLI and future web UI can discover and describe supported operations. ai_project_ctl/core/registry.py Command registry supports listing and describing project-control commands. Implement command registry metadata for task, epic, change, review, context, codex, project, and command domains where available. Support example names such as task.list, task.show, task.create, task.transition, epic.list, change.create, context.build, codex.prompt.build, project.doctor, command.list, and command.describe. Expose command names, descriptions, args schema, read/write metadata, and output format metadata. Add tests for registry listing and command description behavior. Do not implement web forms in this task. Do not remove existing ctl entrypoints. Do not add unsupported lifecycle commands. ai_project_ctl/core/registry.py ai_project_ctl/domains/** tests/** AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only Commands have names, descriptions, args schema, read/write metadata, and output format metadata. CLI can list and describe commands. Web UI can later use the registry to render actions/forms. Registry does not bypass domain validation. Verify that registry metadata cannot execute unsupported or unvalidated operations. Verify command descriptions match implemented behavior.","schema_version":1,"task_id":"TASK-023"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-023`
Limit: `8`
Docs revision: `19`
Tasks revision: `220`
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

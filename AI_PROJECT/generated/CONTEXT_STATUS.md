<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-025 Task G - Convert old ctl scripts into compatibility wrappers Keep existing ctl workflows working while centralizing logic. Update taskctl.py, evolutionctl.py, planctl.py, docctl.py, contextctl.py, and codexctl.py where practical so they delegate to ai_project_ctl domain services or aictl-compatible services without breaking existing command syntax. scripts/*ctl.py Legacy ctl scripts remain supported while shared services own behavior. Make taskctl.py delegate to ai_project_ctl domains or shared services where practical. Make evolutionctl.py and other ctl scripts delegate where practical. Keep old command syntax compatible unless a separate approved migration says otherwise. Mark wrappers as legacy-compatible but supported in documentation or code comments where appropriate. Reduce duplicate lifecycle validation where avoidable. Do not remove existing ctl scripts. Do not change public command syntax unless explicitly approved. Do not implement web UI in this task. scripts/planctl.py scripts/taskctl.py scripts/docctl.py scripts/evolutionctl.py scripts/contextctl.py scripts/codexctl.py ai_project_ctl/** tests/** AI_PROJECT/state/tasks.json via taskctl.py only AI_PROJECT/events/task-events.jsonl via taskctl.py only AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only Existing commands still work. New code path is centralized. No duplicate lifecycle validation remains where avoidable. Wrapper compatibility is documented or obvious from implementation. Run representative compatibility checks for old ctl commands. Verify protected state mutation still goes only through approved service paths.","schema_version":1,"task_id":"TASK-025"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-025`
Limit: `8`
Docs revision: `19`
Tasks revision: `232`
Indexed source documents: `10`
Indexed chunks: `890`
Selected chunks: `8`
Excluded registered sources: `130`

## Selected Source Paths

- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/05-lifecycle-rules.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/project-control/07-validation-and-tests.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `89`
- template document excluded by default: `41`

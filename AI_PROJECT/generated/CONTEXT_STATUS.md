<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-042 UIX-05 Add Bulk Task Import from file Extend Bulk Task Import to support uploading JSON files in addition to pasted JSON text. Allow the owner to import task batches from a local JSON file while preserving preview, validation, confirmation, and governed command-path creation. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add file upload support for Bulk Task Import. Support UTF-8 .json or .txt files containing JSON import payloads. Enforce conservative file size limit. Parse file content as data only. Reuse existing preview/dry-run behavior. Reuse existing validation before writes. Reuse existing confirmed command-path task creation. Show clear parse/validation errors. Keep paste-based import working. Do not execute uploaded files. Do not support Python, shell scripts, or unrestricted executable formats. Do not add YAML dependency unless already allowed by existing project dependency policy. Do not auto-start imported tasks. Do not auto-approve anything. Do not write tasks.json directly. ai_project_ctl/web/actions.py ai_project_ctl/web/server.py ai_project_ctl/web/read_model.py ai_project_ctl/core/workflows.py if import payload handling needs compatible updates scripts/aictl.py if import routing needs compatible updates tests/test_web_control_center.py tests/test_workflows.py tests/test_aictl.py Owner can import a task batch by uploading a JSON/text file. Paste-based JSON import still works. Importer shows preview before creation. Invalid file type, invalid JSON, invalid refs, or oversized file fails before creation. Confirmed import creates tasks only through governed command paths. No direct tasks.json writes are introduced. Tests and project-control validations pass. Verify that uploaded file content is parsed as data only. Verify that no executable content is run. Verify that invalid imports create no tasks.","schema_version":1,"task_id":"TASK-042"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-042`
Limit: `8`
Docs revision: `23`
Tasks revision: `451`
Indexed source documents: `10`
Indexed chunks: `890`
Selected chunks: `8`
Excluded registered sources: `134`

## Selected Source Paths

- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `93`
- template document excluded by default: `41`

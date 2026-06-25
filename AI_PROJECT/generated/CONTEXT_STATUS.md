<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-121 PIPE-042 Add tests for git diff gate Add focused tests for actual git diff gate and file-scope comparison behavior. Protect verify from accepting incomplete or dishonest structured reports. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Test clean working tree behavior. Test reported changed file matching actual diff. Test actual changed file missing from report. Test out-of-scope and protected file detection. Do not change behavior unrelated to this task. Do not refactor unrelated code. Do not edit protected project-control files manually. tests/test_pipeline_git_diff_gate.py The git diff gate detects changed tracked files. The git diff gate detects untracked files. Verify comparison blocks when actual files are missing from the report. Protected file changes are blocked with stable reason codes. Check tests create isolated temporary git repositories. Verify tests do not modify the real project working tree.","schema_version":1,"task_id":"TASK-121"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-121`
Limit: `8`
Docs revision: `28`
Tasks revision: `1239`
Indexed source documents: `10`
Indexed chunks: `891`
Selected chunks: `8`
Excluded registered sources: `135`

## Selected Source Paths

- ai-system/project-control/03-state-model.md
- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/project-control/07-validation-and-tests.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `94`
- template document excluded by default: `41`

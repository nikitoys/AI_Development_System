<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-118 PIPE-039 Add CI exit-code mode for pipeline Add a CI-oriented exit-code mode where blocked and failed pipeline outcomes produce nonzero process exit codes. Make pipeline results usable by automation without losing human-readable safe-stop behavior. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Add --ci flag to phase runner commands where appropriate. Map passed and completed outcomes to exit code 0. Map failed outcomes to exit code 1. Map blocked outcomes to exit code 2. Do not change behavior unrelated to this task. Do not refactor unrelated code. Do not edit protected project-control files manually. scripts/aictl.py ai_project_ctl/pipeline/phase.py pipeline run-next --ci exits 0 for passed or completed outcomes. pipeline run-next --ci exits 2 for blocked outcomes. pipeline run-next --ci exits 1 for failed outcomes. Default non-CI behavior remains compatible with human safe-stop usage. Check that JSON output still includes full outcome details in CI mode. Verify exit code mapping is documented in code comments or command help.","schema_version":1,"task_id":"TASK-118"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-118`
Limit: `8`
Docs revision: `28`
Tasks revision: `912`
Indexed source documents: `10`
Indexed chunks: `891`
Selected chunks: `8`
Excluded registered sources: `135`

## Selected Source Paths

- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/project-control/07-validation-and-tests.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `94`
- template document excluded by default: `41`

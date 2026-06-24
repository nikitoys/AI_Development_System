<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-119 PIPE-040 Add tests for phase model and mutations Add tests for PhaseResult serialization, session phase fields, and governed phase mutation helpers. Protect the foundational phase state behavior before rewriting the runner. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Test PhaseResult construction and JSON conversion. Test session creation with phase field defaults. Test start_phase and record_phase_result mutations. Test validation behavior for legacy sessions without phase fields. Do not change behavior unrelated to this task. Do not refactor unrelated code. Do not edit protected project-control files manually. tests/test_pipeline_phase.py tests/test_pipeline_session_phase.py Tests pass for all PhaseResult statuses. Tests prove legacy pipeline sessions remain valid. Tests prove phase results append to phase_history. Tests prove terminal sessions reject new phase mutations. Check tests use temporary state and do not depend on local repository state. Verify tests do not require external Codex or network access.","schema_version":1,"task_id":"TASK-119"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-119`
Limit: `8`
Docs revision: `28`
Tasks revision: `1024`
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

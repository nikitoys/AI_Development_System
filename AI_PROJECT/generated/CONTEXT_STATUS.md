<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-273 Add no-checkpoint Web Run regression Add an end-to-end regression proving that a successful Web Run leaves a clean worktree and the next Web Run does not request a checkpoint commit. The owner workflow should be able to run one task, receive a task commit, and start the next task without checkpointing pipeline bookkeeping files. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Create or extend a Web Run local-commit regression test with two sequential planned smoke tasks. Assert the first Web Run creates a local commit and leaves git status clean. Assert the second Web Run is not blocked by dirty pipeline bookkeeping from the first run. Assert no checkpoint prompt is shown when the user made no changes between runs. Do not implement multi-task batch UI in this task. Do not change checkpoint commit action behavior. Do not use network or real external Codex execution in tests. Do not edit protected project-control files manually. tests/test_web_run_local_commit_e2e.py tests/test_web_control_center.py tests/test_pipeline_runner.py The regression test creates a successful first Web Run with a local commit hash. The regression test verifies git status is clean immediately after the first successful Web Run. The regression test attempts a second Web Run without manual checkpointing. The second Web Run does not return WORKTREE_DIRTY for pipeline bookkeeping files. The test fails if pipeline-events.jsonl, pipeline_sessions.json, PIPELINE_STATUS.md, or PIPELINE_AUDIT.md remain dirty after the first run. The test uses existing fake or stubbed execution paths and does not require real Codex network execution. Verify that the regression matches the owner workflow: run task, then run the next task without checkpoint commit.","schema_version":1,"task_id":"TASK-273"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-273`
Limit: `8`
Docs revision: `28`
Tasks revision: `1877`
Indexed source documents: `10`
Indexed chunks: `891`
Selected chunks: `8`
Excluded registered sources: `135`

## Selected Source Paths

- ai-system/project-control/03-state-model.md
- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `94`
- template document excluded by default: `41`

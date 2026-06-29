<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-270 Eliminate post-commit pipeline writes Prevent successful Web Run completion from writing tracked pipeline state or generated files after the local task commit has already been created. A successful close must not leave pipeline bookkeeping files dirty after local commit; completion bookkeeping must be committed or made non-mutating after commit. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Inspect the committed-close path in the batch runner and identify tracked writes that happen after local_commit.commit_hash is created. Change successful committed-close handling so it does not mutate tracked AI_PROJECT pipeline files after the task local commit. Preserve existing single-task Web Run completion semantics and owner-facing session completion result. Add focused tests proving the committed-close success path does not perform post-commit tracked writes. Do not remove local task commit creation. Do not weaken dirty worktree preflight. Do not implement multi-task batch UI in this task. Do not edit protected project-control files manually. ai_project_ctl/pipeline/batch.py ai_project_ctl/pipeline/session.py tests/test_pipeline_runner.py tests/test_pipeline_phase_review_close.py After a successful committed close, the batch runner does not write AI_PROJECT/state/pipeline_sessions.json after local commit creation. After a successful committed close, the batch runner does not render PIPELINE_STATUS.md or PIPELINE_AUDIT.md after local commit creation. Single-task Web Run still reports a completed session when local_commit.commit_hash exists. The result still includes the local commit hash and completed task information. Existing blocked, failed, and max_steps behavior remains unchanged. Focused tests cover the no-post-commit-tracked-writes behavior. Verify that this fixes the source of dirty pipeline bookkeeping after a successful task commit instead of bypassing dirty preflight.","schema_version":1,"task_id":"TASK-270"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-270`
Limit: `8`
Docs revision: `28`
Tasks revision: `1824`
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

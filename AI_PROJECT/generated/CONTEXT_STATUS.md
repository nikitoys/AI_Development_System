<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-276 Pass no-checkpoint Web Run regression Make the existing no-checkpoint Web Run local-commit regression pass against the fixed committed-close Web action lifecycle. The regression should prove that one successful Web Run leaves a clean worktree and the next selected task starts without checkpoint_commit guidance. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Run the existing tests/test_web_run_local_commit_e2e.py regression and keep its clean-worktree assertion meaningful. Adjust the regression only if needed to match the final intended committed-close lifecycle contract. Assert the first Web Run creates a local commit and leaves git status clean after WebActionExecutor returns. Assert the second Web Run does not return WORKTREE_DIRTY or checkpoint_commit guidance when no owner changes were made. Do not loosen the regression by ignoring pipeline bookkeeping files. Do not change production pipeline behavior in this validation task unless a tiny test-support hook is unavoidable. Do not remove the second-run no-checkpoint assertion. Do not edit protected project-control files manually. tests/test_web_run_local_commit_e2e.py tests/test_web_control_center.py tests/test_pipeline_runner.py python -m py_compile tests/test_web_run_local_commit_e2e.py passes. python -m pytest tests/test_web_run_local_commit_e2e.py -q passes. The regression fails if AI_PROJECT/events/pipeline-events.jsonl remains dirty after the first Web Run. The regression fails if AI_PROJECT/state/pipeline_sessions.json remains dirty after the first Web Run. The regression fails if PIPELINE_STATUS.md or PIPELINE_AUDIT.md remain dirty after the first Web Run. The regression verifies the second Web Run starts without WORKTREE_DIRTY or ui.checkpoint_commit guidance. Verify that the test remains a real guard for clean worktree behavior and is not weakened to pass artificially.","schema_version":1,"task_id":"TASK-276"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-276`
Limit: `8`
Docs revision: `28`
Tasks revision: `1865`
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

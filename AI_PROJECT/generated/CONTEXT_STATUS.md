<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-274 Stop post-commit session completion writes Prevent the committed Web Run close path from writing pipeline session state, events, or generated pipeline files after the local task commit exists. The failing Web Run regression shows that pipeline.session.complete and related bookkeeping still dirty tracked files after LOCAL_COMMIT_CREATED. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Trace the successful committed-close path from run_until_blocker through session completion after LOCAL_COMMIT_CREATED. Change the committed-close completion path so completed session status can be returned without calling mutating session completion after the local commit. Preserve normal persisted completion behavior for sessions that finish without a local commit and for blocked, failed, or stopped sessions. Add focused coverage proving no tracked pipeline bookkeeping files are written after local commit creation. Do not remove local task commit creation. Do not weaken dirty worktree preflight or post-commit dirty checks. Do not change report, review, or close gate semantics unrelated to committed-close completion. Do not edit protected project-control files manually. ai_project_ctl/pipeline/batch.py ai_project_ctl/pipeline/session.py tests/test_pipeline_runner.py tests/test_web_run_local_commit_e2e.py After LOCAL_COMMIT_CREATED, the committed-close path does not append a new pipeline.session.complete event to AI_PROJECT/events/pipeline-events.jsonl. After LOCAL_COMMIT_CREATED, the committed-close path does not mutate AI_PROJECT/state/pipeline_sessions.json. After LOCAL_COMMIT_CREATED, the committed-close path does not render AI_PROJECT/generated/PIPELINE_STATUS.md or AI_PROJECT/generated/PIPELINE_AUDIT.md. The returned batch result still reports completed status, completed task information, and the local commit hash for successful single-task Web Run sessions. Non-local-commit queue completion behavior remains persisted and unchanged. Focused tests cover committed-close completion and non-local-commit queue completion. Verify that the fix removes post-commit writes rather than hiding dirty files from git status.","schema_version":1,"task_id":"TASK-274"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-274`
Limit: `8`
Docs revision: `28`
Tasks revision: `1855`
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

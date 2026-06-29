<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-275 Make committed Web action result read-only Ensure ui.run_selected_task builds its successful committed-close action result without triggering tracked pipeline render or refresh writes after the commit. The Web action should display completed status and commit evidence from the returned pipeline result rather than mutating pipeline status artifacts after completion. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Trace ui.run_selected_task result handling after run_until_blocker returns a committed close result. Avoid any post-commit calls that persist pipeline session completion, pipeline events, or generated pipeline status/audit files for committed-close success. Build the owner-facing action result from in-memory session/result data when the local commit already exists. Keep dirty-start preflight, checkpoint guidance, and blocked action results unchanged. Do not redesign the Web Control Center UI layout. Do not change non-Web CLI pipeline session behavior unless required by the shared read-only completion helper. Do not auto-create checkpoint commits. Do not edit protected project-control files manually. ai_project_ctl/web/actions.py ai_project_ctl/web/server.py ai_project_ctl/pipeline/batch.py tests/test_web_control_center.py tests/test_web_run_local_commit_e2e.py A successful ui.run_selected_task response still shows completed outcome, session id, task id, and local commit hash. Rendering the Web action result after a committed close does not mutate pipeline_sessions.json, pipeline-events.jsonl, PIPELINE_STATUS.md, or PIPELINE_AUDIT.md. Dirty-start WORKTREE_DIRTY responses and checkpoint_commit guidance remain unchanged. Blocked and failed pipeline action results still render their owner guidance correctly. Focused Web tests cover committed-close action rendering without post-commit tracked writes. No UI action path hides real dirty worktree state from safety checks. Verify that the Web layer consumes committed-close evidence read-only and does not call a mutating render just to build the response.","schema_version":1,"task_id":"TASK-275"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-275`
Limit: `8`
Docs revision: `28`
Tasks revision: `1860`
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

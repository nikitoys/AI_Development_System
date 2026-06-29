<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-271 Commit final pipeline close artifacts Ensure final close-phase pipeline state, events, and generated status artifacts are written before local commit readiness is evaluated. Files such as pipeline_sessions.json, pipeline-events.jsonl, PIPELINE_STATUS.md, and PIPELINE_AUDIT.md must be part of the task commit when they are produced by the closing session. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Move or trigger final pipeline status and audit rendering before local commit readiness in the successful close path. Ensure close-phase side effects include session-owned pipeline state, pipeline events, and generated pipeline status files. Approve only current-session pipeline bookkeeping files for local commit readiness. Keep pre-existing unrelated dirty files blocked by commit readiness. Do not approve arbitrary dirty files. Do not change report gate semantics. Do not change checkpoint commit behavior. Do not edit protected project-control files manually. ai_project_ctl/pipeline/close_phase.py ai_project_ctl/pipeline/git_commit.py ai_project_ctl/pipeline/session.py tests/test_pipeline_git_commit.py tests/test_pipeline_phase_review_close.py Session-owned AI_PROJECT/state/pipeline_sessions.json changes created during close are eligible for the local task commit. Session-owned AI_PROJECT/events/pipeline-events.jsonl changes created during close are eligible for the local task commit. Session-owned AI_PROJECT/generated/PIPELINE_STATUS.md and AI_PROJECT/generated/PIPELINE_AUDIT.md changes created during close are eligible for the local task commit. Pre-existing dirty pipeline files from before the session still block unless explicitly owned by the current session. The local commit stages only approved task files and current-session governed bookkeeping files. Focused tests cover approved final pipeline artifacts and unrelated dirty blockers. Verify that commit readiness stays safe and does not become git add -A for arbitrary files.","schema_version":1,"task_id":"TASK-271"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-271`
Limit: `8`
Docs revision: `28`
Tasks revision: `1829`
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

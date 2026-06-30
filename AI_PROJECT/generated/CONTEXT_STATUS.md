<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-277 Allow governed close side effects in local commit readiness Update local commit readiness so current-session governed close side effects can be committed without allowing unrelated AI_PROJECT dirty files. Fix the PSESS-151 class of failures where task gates pass but local commit blocks with COMMIT_UNRELATED_FILES because governed close side effects are not included in approved evidence. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Extend commit readiness approved-file collection to recognize governed side effects owned by the current pipeline session. Keep pre-existing dirty governed files and non-session-owned AI_PROJECT files blocked as unrelated. Preserve the existing requirement for non-governed target task artifact evidence before committing governed session side effects. Add a regression that covers a successful local commit with task artifact changes plus session-owned task/report/codex/context/evolution/pipeline side effects. Add or keep a negative regression proving unrelated governed dirty files still fail with COMMIT_UNRELATED_FILES. Do not allow blanket commits of all AI_PROJECT/** paths. Do not bypass commit readiness, report gate, machine review, or task done requirements. Do not edit protected project-control files manually. Do not change behavior unrelated to local commit readiness. ai_project_ctl/pipeline/git_commit.py ai_project_ctl/pipeline/close_phase.py ai_project_ctl/pipeline/session.py tests/test_pipeline_runner.py tests/test_web_run_local_commit_e2e.py tests/test_web_control_center.py Commit readiness passes for a clean-baseline pipeline session that has target task artifact evidence and current-session governed close side effects. Local commit creation stages only approved target artifact files and current-session governed side-effect files. Pre-existing dirty governed files that are not owned by the current session still block with COMMIT_UNRELATED_FILES. Arbitrary AI_PROJECT/** files that are not approved by report, side effects, or current-session evidence still block with COMMIT_UNRELATED_FILES. Commit readiness still blocks governed-only changes when the selected task has no non-governed target artifact evidence. python -m pytest tests/test_pipeline_runner.py -q passes. python -m pytest tests/test_web_run_local_commit_e2e.py -q passes. Review that approved governed paths are derived from current-session evidence or explicit side effects, not from a broad AI_PROJECT/** allowlist. Check both positive and negative tests for COMMIT_UNRELATED_FILES behavior.","schema_version":1,"task_id":"TASK-277"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-277`
Limit: `8`
Docs revision: `28`
Tasks revision: `1891`
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

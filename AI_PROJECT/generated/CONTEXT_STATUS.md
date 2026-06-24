<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-161 Make Codex Review optional in pipeline Allow the pipeline to skip semantic Codex Review when `require_codex_review` is false while keeping Machine Review required. This task implements the behavior behind the Settings checkbox without weakening deterministic review gates. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Resolve `require_codex_review=false` into an effective pipeline policy that does not require Codex Review APPROVE. Record the review phase as skipped without building a Codex Review prompt when Codex Review is disabled by policy. Allow close phase to proceed without Codex Review only when policy explicitly disables it and Machine Review evidence passes. Allow local commit readiness to skip Codex Review approval only when policy explicitly disables it. Preserve current Codex Review requirements when `require_codex_review=true`. Add tests for skipped review, close preflight, and local commit readiness with Codex Review disabled. Do not disable Machine Review. Do not remove or weaken Report Gate checks. Do not change Codex Review behavior when `require_codex_review=true`. Do not change unrelated pipeline phases. ai_project_ctl/pipeline/ui_policy.py ai_project_ctl/pipeline/policy.py ai_project_ctl/pipeline/review_phase.py ai_project_ctl/pipeline/close_phase.py ai_project_ctl/pipeline/git_commit.py tests/test_pipeline_codex_review_toggle.py When `require_codex_review=true`, existing Codex Review APPROVE requirements remain unchanged. When `require_codex_review=false`, review phase records `status=skipped` and does not build or return a Codex Review prompt. Machine Review remains required before close and cannot be bypassed by disabling Codex Review. Close phase accepts skipped Codex Review only when the effective policy disables Codex Review. Local commit readiness does not block on missing Codex Review only when the effective policy disables Codex Review. Tests prove that disabling Codex Review does not disable Report Gate or Machine Review. Reject if Codex Review disabling also disables Machine Review. Reject if close can proceed without Machine Review PASS. Reject if Codex Review is skipped when `require_codex_review=true`. Reject if local commit ignores Codex Review when policy still requires it.","schema_version":1,"task_id":"TASK-161"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-161`
Limit: `8`
Docs revision: `28`
Tasks revision: `1105`
Indexed source documents: `10`
Indexed chunks: `891`
Selected chunks: `8`
Excluded registered sources: `135`

## Selected Source Paths

- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `94`
- template document excluded by default: `41`

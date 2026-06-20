<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-063 PIPE-12 Controlled Git Commit Action Create local commits only when policy allows and commit readiness is green. Add a controlled local git commit action for completed pipeline work. It must never push, merge, reset, discard, or create remote changes. ai_project_ctl/pipeline/git_commit.py Pipeline can optionally create a local commit only when commit policy allows and readiness checks are green. Implement read-only commit readiness check reuse or integration with the existing Commit Readiness view. Implement local commit action only behind explicit policy permission. Require clean readiness: task done, required Change accepted if policy requires it, machine checks pass, protected-file checks pass, generated outputs fresh, no unrelated dirty files unless policy explicitly allows. Stage only files approved by policy/session evidence. Generate commit message from completed task refs, Change ids, and session id. Run git commit locally only; explicitly forbid push, merge, reset, checkout, rebase, and destructive git commands. Record commit hash or failure in pipeline session/audit. Add tests with fake git runner for readiness green, readiness fail, unrelated files, commit success, and forbidden command attempts. Do not push. Do not merge. Do not open PRs. Do not discard or reset changes. Do not commit when readiness is not green. Do not auto-accept Changes in this task. ai_project_ctl/pipeline/git_commit.py ai_project_ctl/pipeline/runner.py if integration is needed ai_project_ctl/web/read_model.py if commit readiness data is reused ai_project_ctl/core/registry.py if command metadata is needed scripts/aictl.py if commit command routing is needed tests/** ai-system/project-control/** if git commit policy documentation is needed Commit action is disabled unless policy explicitly allows local commit. Commit action refuses when commit readiness is not green. Commit action stages only approved files. Commit action never pushes, merges, resets, rebases, or discards changes. Commit result is recorded in session/audit. Tests and project-control validations pass. Verify command allowlist forbids push/merge/destructive git actions. Verify readiness failure blocks commit.","schema_version":1,"task_id":"TASK-063"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-063`
Limit: `8`
Docs revision: `24`
Tasks revision: `556`
Indexed source documents: `10`
Indexed chunks: `890`
Selected chunks: `8`
Excluded registered sources: `134`

## Selected Source Paths

- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/project-control/07-validation-and-tests.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `93`
- template document excluded by default: `41`

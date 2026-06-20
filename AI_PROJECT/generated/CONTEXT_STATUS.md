<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-079 Compact codexctl execute prompt renderer Render CODEX_PROMPT.md as a compact execute-profile contract instead of embedding full Context Pack content. Implement approved CHG-062 by updating scripts/codexctl.py prompt rendering and focused tests so context-aware Codex prompt packages remain compact and bounded. scripts/codexctl.py Compact CODEX_PROMPT.md renderer implemented for execute-profile MVP Modify scripts/codexctl.py prompt rendering. Render Profile: execute as the MVP default; do not implement --profile. Use existing task fields only for identity, role, objective, scope, out-of-scope, allowed files, acceptance criteria, and verification mode. Render Objective from task.summary with fallback to task.title. Render full task.scope and full task.acceptance_criteria without category splitting. Omit Execution Steps because task.execution_steps is not part of the current task schema. Render Verification mode plus compact default check instruction. Render Context as manifest-only when Context Pack is attached, keeping path, hash, docs revision, tasks revision, and selected source refs. Do not embed the full AI_PROJECT/generated/CONTEXT_PACK.md body into CODEX_PROMPT.md. Keep compact Execution Rules, Missing Info policy, and Final Report format. Add or update tests proving compact context rendering. Do not implement --profile. Do not add profile-specific role switching. Do not change task schema. Do not add execution_steps or verification_checks. Do not implement task splitting. Do not modify contextctl.py. Do not manually edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**. scripts/codexctl.py tests/test_legacy_ctl_wrappers.py codexctl.py build --task <TASK> still works without Context Pack. codexctl.py build --task <TASK> --with-context produces a compact Context section. Generated CODEX_PROMPT.md does not embed the full CONTEXT_PACK.md body. Generated CODEX_PROMPT.md includes Context Pack path, hash, docs revision, tasks revision, and selected source refs when context is attached. Execution Steps section is omitted for current tasks because task.execution_steps does not exist. Verification renders mode plus compact default check instruction. Existing wrapper tests still pass. Add or update tests to prove compact context rendering. Generated CODEX_PROMPT.md omits the legacy full retrieved-context body section. Run python -m py_compile scripts/codexctl.py. Run relevant tests for legacy ctl wrappers. Run a local codex prompt build with context if fixtures allow it.","schema_version":1,"task_id":"TASK-079"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-079`
Limit: `8`
Docs revision: `28`
Tasks revision: `669`
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

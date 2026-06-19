<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-058 PIPE-07 Codex Execution Adapter Launch or hand off Codex Executor only after policy and Token Budget Gate PASS, then capture execution metadata. Add a controlled Codex execution adapter with dry-run/manual default behavior, explicit policy enablement, timeout, command allowlist, captured output, and report handoff instructions. ai_project_ctl/pipeline/codex_adapter.py Pipeline can safely invoke or prepare Codex execution through a controlled adapter only when all pre-execution gates pass. Define Codex Execution Adapter interface with dry-run, manual-handoff, and configured-local-command modes if appropriate. Require policy permission before any non-dry-run execution. Require Token Budget Gate PASS before execution. Pass only the generated Codex prompt path/payload and bounded task context. Capture start/end time, return code, stdout/stderr references, timeout, and adapter mode. Require Codex to submit a structured execution report through the existing report path before downstream gates can pass. Stop safely on timeout, non-zero exit, missing prompt, stale prompt, or missing report. Add tests with a fake adapter/runner; do not require real Codex in normal test runs. Do not bypass task allowed_files. Do not give Codex permission to push, merge, or approve owner decisions. Do not require external Codex services for local tests. Do not auto-close tasks based only on adapter success. ai_project_ctl/pipeline/codex_adapter.py ai_project_ctl/pipeline/runner.py if integration is needed ai_project_ctl/pipeline/policy.py if policy compatibility is needed ai_project_ctl/core/registry.py if command metadata is needed scripts/aictl.py if adapter command routing is needed tests/** ai-system/project-control/** if adapter documentation is needed Adapter default mode is safe and does not unexpectedly launch external tools. Adapter refuses execution unless policy allows it and Token Budget Gate PASS is present. Adapter captures execution metadata and exposes it to pipeline session state. Adapter failure stops the pipeline with a clear blocker. Normal tests use a fake adapter and do not require a real Codex binary/service. Tests and project-control validations pass. Verify no external execution happens by default. Verify adapter cannot run before Token Budget Gate PASS.","schema_version":1,"task_id":"TASK-058"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-058`
Limit: `8`
Docs revision: `24`
Tasks revision: `529`
Indexed source documents: `10`
Indexed chunks: `890`
Selected chunks: `8`
Excluded registered sources: `134`

## Selected Source Paths

- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `93`
- template document excluded by default: `41`

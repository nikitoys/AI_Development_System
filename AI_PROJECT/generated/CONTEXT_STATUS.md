<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-060 PIPE-09 Machine Review Gate Run deterministic machine checks for tests, doctor, protected files, generated outputs, allowed_files, token usage, and blockers. Implement the machine review gate that collects deterministic evidence before Codex semantic review or auto-close decisions. ai_project_ctl/pipeline/machine_review.py Pipeline has a deterministic Machine Review PASS/WARN/FAIL gate before semantic review and auto-close. Run or collect project-control validation checks: task validate, task graph validate, generated checks, evolution validate/check-generated, context validate/check-generated, project doctor, and protected-file check. Run task/report-declared tests or configured test commands only when policy allows and commands are safe. Check changed files against task allowed_files and protected-file rules. Check report blockers and token usage against policy. Return PASS only when all blocking checks pass. Return structured evidence with command, result, duration if available, stdout/stderr summaries, and failure reasons. Add tests with fake command runners and representative pass/fail cases. Do not do semantic acceptance review. Do not close tasks. Do not accept Changes. Do not commit. Do not suppress doctor/protected-file failures. ai_project_ctl/pipeline/machine_review.py ai_project_ctl/pipeline/report_gate.py if integration is needed ai_project_ctl/pipeline/runner.py if integration is needed ai_project_ctl/core/registry.py if command metadata is needed scripts/aictl.py if gate command routing is needed tests/** ai-system/project-control/** if machine review documentation is needed Machine Review PASS requires all blocking checks to pass. Machine Review FAIL stops the pipeline. Protected-file and allowed_files violations are blocking. Token usage and report blockers are checked according to policy. Gate output is structured and auditable. Tests and project-control validations pass. Verify that deterministic checks are actually blocking. Verify that allowed_files/protected-file checks cannot be bypassed by report wording.","schema_version":1,"task_id":"TASK-060"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-060`
Limit: `8`
Docs revision: `24`
Tasks revision: `539`
Indexed source documents: `10`
Indexed chunks: `890`
Selected chunks: `8`
Excluded registered sources: `134`

## Selected Source Paths

- ai-system/project-control/03-state-model.md
- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `93`
- template document excluded by default: `41`

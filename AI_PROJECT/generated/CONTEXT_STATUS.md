<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-033 WFA-02 Add Evolution Change Wizard Add a guided workflow/UI helper to create and prepare Evolution Change records for tasks that require controlled system evolution approval. Reduce manual evolutionctl command overhead by generating a draft/ready Change Proposal from a selected task's fields, then linking it to the task. Approval remains an explicit Human Owner action. AI_PROJECT/generated/CODEX_TASKS.md Evolution Change wizard is implemented without bypassing Human Owner approval. Add workflow evolution.create_for_task. Derive initial problem/proposal/rationale/affected_files/risks/impact from task fields where possible. Link the Change Proposal to the selected task legacy id. Move created Change Proposal to ready if validation passes. Provide UI form/preview if allowed. Keep approve as separate explicit owner action. Add tests. Do not auto-approve Evolution Changes. Do not auto-accept Evolution Changes. Do not guess high-risk changes silently. Do not bypass evolutionctl.py validation. ai_project_ctl/core/workflows.py ai_project_ctl/web/actions.py ai_project_ctl/web/server.py ai_project_ctl/web/read_model.py ai_project_ctl/core/registry.py scripts/aictl.py tests/** Owner can create a Change Proposal for a selected task with preview and confirmation. Created Change links to the correct legacy task id. Created Change includes affected files, risks, impact, problem/proposal/rationale draft. Change approval remains a separate explicit action. No direct protected-file edits. Tests and validations pass. Verify evolutionctl routing, owner approval boundary, Change-to-task linking, protected-file policy, tests, and validation output.","schema_version":1,"task_id":"TASK-033"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-033`
Limit: `8`
Docs revision: `22`
Tasks revision: `311`
Indexed source documents: `10`
Indexed chunks: `890`
Selected chunks: `8`
Excluded registered sources: `134`

## Selected Source Paths

- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/05-lifecycle-rules.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/project-control/07-validation-and-tests.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `93`
- template document excluded by default: `41`

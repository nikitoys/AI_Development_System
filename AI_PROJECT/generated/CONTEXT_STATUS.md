<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-068 PIPE-17 Add Custom Pipeline Policy Preset Store Add governed storage for user-defined pipeline policy presets while keeping built-in safe presets immutable. Introduce a persistent custom policy preset store so the Human Owner can save, validate, list, and delete pipeline policy presets without editing Python source or protected state manually. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Create a governed custom pipeline policy preset storage model. Store custom presets separately from built-in presets. Keep built-in presets dry_run, supervised, supervised_autoclose, and supervised_local_commit immutable. Validate saved presets through the existing PipelinePolicy validation rules. Reject unsafe presets with stable error codes. Add audit events for preset create/update/delete operations. Add generated policy status output if useful for UI and validation. Do not allow custom presets to authorize push, merge, reset, rebase, clean, or destructive git operations. Do not allow custom presets to bypass Token Budget Gate, Machine Review, Codex Review, Human Owner approval, or Evolution Change gates. Do not modify built-in preset definitions except for compatibility wiring. Do not edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/** manually. ai_project_ctl/pipeline/policy.py ai_project_ctl/pipeline/policy_store.py ai_project_ctl/pipeline/__init__.py ai_project_ctl/core/registry.py scripts/aictl.py AI_PROJECT/state/pipeline_policy_presets.json via governed CLI/service only AI_PROJECT/events/pipeline-policy-events.jsonl via governed CLI/service only AI_PROJECT/generated/PIPELINE_POLICIES.md via governed CLI/service only tests/** Custom policy presets can be saved, loaded, validated, listed, and deleted through governed service paths. Built-in policy presets remain available and immutable. Invalid or unsafe custom presets are rejected before persistence. Preset changes create audit events. No direct protected-file writes are introduced. Tests and project-control validations pass. Verify that custom presets cannot weaken forbidden safety boundaries. Verify that built-in presets cannot be overwritten or deleted. Verify that all persistence goes through governed service paths.","schema_version":1,"task_id":"TASK-068"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-068`
Limit: `8`
Docs revision: `27`
Tasks revision: `615`
Indexed source documents: `10`
Indexed chunks: `891`
Selected chunks: `8`
Excluded registered sources: `135`

## Selected Source Paths

- ai-system/project-control/03-state-model.md
- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/05-lifecycle-rules.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `94`
- template document excluded by default: `41`

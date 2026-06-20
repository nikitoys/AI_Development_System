<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-066 PIPE-15 Pipeline SOP Documentation Document the supervised batch pipeline runner, policies, gates, UI flow, blockers, and operator responsibilities. Create owner-facing and system-facing SOP documentation for the PIPE epic after implementation details are stable. ai-system/project-control/pipeline-runner.md Human Owner and Codex can operate the supervised batch pipeline safely using documented SOPs. Create or update pipeline runner documentation. Document Queue -> Policy -> Change -> Prepare -> Token Gate -> Codex Execute -> Report -> Machine Review -> Codex Review -> Done/Rework -> Accept Change -> Commit -> Next / Stop on Blocker. Document policy presets and what each one may or may not automate. Document token budget gate behavior and strict-mode failure cases. Document Codex Executor report requirements and Codex Reviewer read-only responsibilities. Document Machine Review and Codex Review gate meanings. Document auto-close, rework loop, Change acceptance, and local commit rules. Document UI dashboard operation and CLI equivalents. Document common blockers, unsafe conditions, recovery paths, and audit trail interpretation. Run docctl validation/render/check-generated and project-control checks. Do not change pipeline command behavior. Do not mark documentation accepted without Human Owner approval. Do not edit generated documentation manually. Do not document unsupported unsafe automation as available. ai-system/project-control/pipeline-runner.md ai-system/project-control/10-owner-quickstart.md ai-system/project-control/04-command-catalog.md ai-system/project-control/README.md if index update is needed README.md if owner-facing quick links are needed AGENTS.md if Codex handoff rules need a pointer AI_PROJECT/state/docs.json via docctl.py only AI_PROJECT/events/doc-events.jsonl via docctl.py only AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only Pipeline SOP documents the approved algorithm and stop conditions. Documentation clearly distinguishes policy-selected automation from forbidden autonomy. Documentation says Codex Reviewer is read-only and cannot mutate files/lifecycle/commits. Documentation says commit is local-only and push/merge remain forbidden. Documentation explains token budget strict-mode failures. Documentation checks and project-control validations pass. Verify documentation does not overclaim unimplemented behavior. Verify generated docs are refreshed only through docctl.py.","schema_version":1,"task_id":"TASK-066"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-066`
Limit: `8`
Docs revision: `27`
Tasks revision: `593`
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

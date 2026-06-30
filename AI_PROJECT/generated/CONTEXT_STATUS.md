<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-278 Show close preflight gate details Make pipeline close failures expose the exact missing gate codes and report-id evidence instead of only the generic CLOSE_PREFLIGHT_INCOMPLETE message. Improve close preflight diagnostics so owner can immediately see whether the blocker is missing review evidence, task mismatch, report mismatch, or policy mismatch. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Update close preflight blocked output to include compact missing_gates details in the phase reason, next_action, or result data. Include observed report ids per phase when the blocker is REPORT_EVIDENCE_MISMATCH. Keep existing strict close preflight gating behavior unchanged. Add or update focused tests for close preflight diagnostics. Do not relax close preflight gate rules. Do not implement report recovery acceptance in this task. Do not edit protected project-control files manually. ai_project_ctl/pipeline/close_phase.py tests/test_pipeline_phase_review_close.py A close blocked by missing phase evidence reports the specific missing gate code(s) in a user-visible result path. A close blocked by report id mismatch reports observed report ids for execute, collect_report, verify, and review when available. Existing close preflight pass and fail behavior remains unchanged except for clearer diagnostics. Focused close preflight tests pass. No protected project-control state or generated files are edited manually. Review that the change improves diagnostics only and does not weaken close safety.","schema_version":1,"task_id":"TASK-278"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-278`
Limit: `8`
Docs revision: `28`
Tasks revision: `1898`
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

<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-283 Add recovery close regression Add an end-to-end regression covering owner recovery report submission followed by collect-report, verify, skipped review, close, and local commit readiness. The regression should prove that a task can close cleanly after owner-confirmed report recovery without manual recovery commits. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Create a focused regression scenario where execute records an original report and owner recovery records a replacement report. Verify collect-report, verify, review, and close can complete through the recovery path. Assert accidental report mismatch without recovery metadata still blocks close. Assert the final working tree behavior remains clean after local commit when commit policy is enabled. Do not implement production recovery behavior in this task unless the regression requires only minimal test fixtures. Do not broaden the regression into unrelated Web UI behavior. Do not edit protected project-control files manually. tests/test_pipeline_recovery_close.py tests/test_pipeline_runner.py The regression covers old execute report id plus new owner recovery report id for the same task. The positive recovery scenario reaches close without CLOSE_PREFLIGHT_INCOMPLETE. The negative accidental mismatch scenario still blocks with REPORT_EVIDENCE_MISMATCH. The regression verifies skipped-review-by-policy evidence remains valid. The focused recovery close tests pass. Check that the test would have caught the PSESS-152 recovery-close failure.","schema_version":1,"task_id":"TASK-283"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-283`
Limit: `8`
Docs revision: `28`
Tasks revision: `1931`
Indexed source documents: `10`
Indexed chunks: `891`
Selected chunks: `8`
Excluded registered sources: `135`

## Selected Source Paths

- ai-system/project-control/03-state-model.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/project-control/07-validation-and-tests.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `94`
- template document excluded by default: `41`

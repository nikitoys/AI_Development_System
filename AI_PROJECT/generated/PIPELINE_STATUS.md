<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/pipeline_sessions.json -->

# Pipeline Status

Revision: `58`
Current session: `PSESS-016`
Sessions: `16`

## Current Session

- ID: `PSESS-016`
- Status: `failed`
- Policy: `supervised_executable_local_commit`
- Current task: `TASK-119`
- Current phase: `execute`
- Phase status: `failed`
- Blocked by: `none`
- Next action: `In local-command mode, Codex receives AI_PROJECT/generated/CODEX_PROMPT.md on stdin. Submit a structured execution report before downstream gates can pass: python scripts/aictl.py task report submit --task TASK-119 --file <REPORT.json> --confirm`
- Current step: `none`
- Step status: `planned`
- Stop reason: `Codex execution adapter failed: local_command_timeout (status=failed, code=CODEX_ADAPTER_TIMEOUT, returncode=none)`

## Sessions

| Session | Status | Policy | Current Task | Current Phase | Phase Status | Blocked By | Next Action | Current Step | Stop Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `PSESS-001` | `completed` | `dry_run` | `TASK-055` | `none` | `none` | none | none | `run_next` | queue_complete |
| `PSESS-002` | `blocked` | `supervised_local_commit` | `TASK-068` | `none` | `none` | none | none | `run_next` | BLOCKED: Approved linked Evolution Change is required before execution. |
| `PSESS-003` | `completed` | `supervised` | `` | `none` | `none` | none | none | `run_next` | queue_complete |
| `PSESS-004` | `blocked` | `supervised` | `` | `none` | `none` | none | none | `run_next` | BLOCKED: Evolution Changes were created and now require Human Owner approval. |
| `PSESS-005` | `blocked` | `supervised_local_commit` | `TASK-068` | `none` | `none` | none | none | `run_next` | NOT_IMPLEMENTED: Auto-close requires Codex execution, Codex Report, Machine Review, Codex Review and a close action. |
| `PSESS-006` | `completed` | `supervised` | `TASK-068` | `none` | `none` | none | none | `run_next` | queue_complete |
| `PSESS-007` | `stopped` | `supervised_executable_local_commit` | `TASK-076` | `none` | `none` | none | none | `` | Owner stop |
| `PSESS-008` | `failed` | `supervised_executable_local_commit` | `TASK-069` | `none` | `none` | none | none | `run_next` | UNSAFE_CONDITION: Codex Execution Adapter stopped: local_command_nonzero_exit |
| `PSESS-009` | `completed` | `supervised_executable_local_commit` | `TASK-077` | `none` | `none` | none | none | `run_next` | queue_complete |
| `PSESS-010` | `completed` | `supervised_executable_local_commit` | `TASK-069` | `none` | `none` | none | none | `run_next` | queue_complete |
| `PSESS-011` | `completed` | `supervised_executable_local_commit` | `TASK-069` | `none` | `none` | none | none | `run_next` | queue_complete |
| `PSESS-012` | `blocked` | `supervised_executable_local_commit` | `TASK-069` | `close` | `blocked` | CLOSE_PREFLIGHT_INCOMPLETE | Resolve required phase evidence for: prepare, execute, collect_report, verify, review; then rerun pipeline close --confirm. | `run_next` | Close preflight blocked: required phase evidence is incomplete. |
| `PSESS-013` | `blocked` | `supervised_executable_local_commit` | `` | `queue_preview` | `blocked` | NO_EXECUTABLE_TASK | Create or unblock a ready task, then rerun queue preview. | `` | No executable task is available in the selected queue. |
| `PSESS-014` | `blocked` | `supervised_executable_local_commit` | `` | `queue_preview` | `blocked` | NO_EXECUTABLE_TASK | Create or unblock a ready task, then rerun queue preview. | `` | No executable task is available in the selected queue. |
| `PSESS-015` | `blocked` | `supervised_executable_local_commit` | `TASK-119` | `prepare` | `blocked` | BLOCKED | Satisfy the selected-task Change gate, then rerun prepare. | `` | Approved linked Evolution Changes are required before execution. |
| `PSESS-016` | `failed` | `supervised_executable_local_commit` | `TASK-119` | `execute` | `failed` | none | In local-command mode, Codex receives AI_PROJECT/generated/CODEX_PROMPT.md on stdin. Submit a structured execution report before downstream gates can pass: python scripts/aictl.py task report submit --task TASK-119 --file <REPORT.json> --confirm | `` | Codex execution adapter failed: local_command_timeout (status=failed, code=CODEX_ADAPTER_TIMEOUT, returncode=none) |

## Phase History

| Session | # | Phase | Status | Reason | Next Action | Changed | Generated | Events |
| --- | ---: | --- | --- | --- | --- | ---: | ---: | ---: |
| `PSESS-012` | 1 | `review` | `blocked` | Verify phase evidence is missing for this session. | Run pipeline phase verify before building the review prompt. | 0 | 0 | 1 |
| `PSESS-012` | 2 | `review` | `blocked` | Verify phase evidence is missing for this session. | Run pipeline phase verify before building the review prompt. | 0 | 0 | 1 |
| `PSESS-012` | 3 | `close` | `blocked` | Close preflight blocked: required phase evidence is incomplete. | Resolve required phase evidence for: prepare, execute, collect_report, verify, review; then rerun pipeline close --confirm. | 0 | 0 | 1 |
| `PSESS-013` | 1 | `queue_preview` | `blocked` | No executable task is available in the selected queue. | Create or unblock a ready task, then rerun queue preview. | 0 | 0 | 1 |
| `PSESS-014` | 1 | `queue_preview` | `blocked` | No executable task is available in the selected queue. | Create or unblock a ready task, then rerun queue preview. | 0 | 0 | 1 |
| `PSESS-015` | 1 | `queue_preview` | `passed` | Next executable task is available. | Run pipeline run-next when ready. | 0 | 0 | 1 |
| `PSESS-015` | 2 | `prepare` | `blocked` | Approved linked Evolution Changes are required before execution. | Satisfy the selected-task Change gate, then rerun prepare. | 0 | 0 | 1 |
| `PSESS-016` | 1 | `queue_preview` | `passed` | Next executable task is available. | Run pipeline run-next when ready. | 0 | 0 | 1 |
| `PSESS-016` | 2 | `prepare` | `blocked` | Approved linked Evolution Changes are required before execution. | Satisfy the selected-task Change gate, then rerun prepare. | 0 | 0 | 1 |
| `PSESS-016` | 3 | `prepare` | `passed` | Task preparation rebuilt artifacts; Codex execution has not been started. | Run pipeline phase execute using AI_PROJECT/generated/CODEX_PROMPT.md (sha256 81b5ba2818abb4904b0e8a2259fb87e02eecf7ce3a8b674e3b0fdb4e6899f232). | 0 | 0 | 1 |
| `PSESS-016` | 4 | `execute` | `failed` | Codex execution adapter failed: local_command_timeout (status=failed, code=CODEX_ADAPTER_TIMEOUT, returncode=none) | In local-command mode, Codex receives AI_PROJECT/generated/CODEX_PROMPT.md on stdin. Submit a structured execution report before downstream gates can pass: python scripts/aictl.py task report submit --task TASK-119 --file <REPORT.json> --confirm | 0 | 0 | 1 |

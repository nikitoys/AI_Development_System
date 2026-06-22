<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/pipeline_sessions.json -->

# Pipeline Status

Revision: `46`
Current session: `PSESS-012`
Sessions: `12`

## Current Session

- ID: `PSESS-012`
- Status: `blocked`
- Policy: `supervised_executable_local_commit`
- Current task: `TASK-069`
- Current phase: `close`
- Phase status: `blocked`
- Blocked by: `CLOSE_PREFLIGHT_INCOMPLETE`
- Next action: `Resolve required phase evidence for: prepare, execute, collect_report, verify, review; then rerun pipeline close --confirm.`
- Current step: `run_next`
- Step status: `blocked`
- Stop reason: `Close preflight blocked: required phase evidence is incomplete.`

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

## Phase History

| Session | # | Phase | Status | Reason | Next Action | Changed | Generated | Events |
| --- | ---: | --- | --- | --- | --- | ---: | ---: | ---: |
| `PSESS-012` | 1 | `review` | `blocked` | Verify phase evidence is missing for this session. | Run pipeline phase verify before building the review prompt. | 0 | 0 | 1 |
| `PSESS-012` | 2 | `review` | `blocked` | Verify phase evidence is missing for this session. | Run pipeline phase verify before building the review prompt. | 0 | 0 | 1 |
| `PSESS-012` | 3 | `close` | `blocked` | Close preflight blocked: required phase evidence is incomplete. | Resolve required phase evidence for: prepare, execute, collect_report, verify, review; then rerun pipeline close --confirm. | 0 | 0 | 1 |

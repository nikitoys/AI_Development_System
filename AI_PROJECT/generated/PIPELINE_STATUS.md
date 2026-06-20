<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/pipeline_sessions.json -->

# Pipeline Status

Revision: `27`
Current session: `PSESS-008`
Sessions: `8`

## Current Session

- ID: `PSESS-008`
- Status: `failed`
- Policy: `supervised_executable_local_commit`
- Current task: `TASK-069`
- Current step: `run_next`
- Step status: `failed`
- Stop reason: `UNSAFE_CONDITION: Codex Execution Adapter stopped: local_command_nonzero_exit`

## Sessions

| Session | Status | Policy | Current Task | Current Step | Stop Reason |
| --- | --- | --- | --- | --- | --- |
| `PSESS-001` | `completed` | `dry_run` | `TASK-055` | `run_next` | queue_complete |
| `PSESS-002` | `blocked` | `supervised_local_commit` | `TASK-068` | `run_next` | BLOCKED: Approved linked Evolution Change is required before execution. |
| `PSESS-003` | `completed` | `supervised` | `` | `run_next` | queue_complete |
| `PSESS-004` | `blocked` | `supervised` | `` | `run_next` | BLOCKED: Evolution Changes were created and now require Human Owner approval. |
| `PSESS-005` | `blocked` | `supervised_local_commit` | `TASK-068` | `run_next` | NOT_IMPLEMENTED: Auto-close requires Codex execution, Codex Report, Machine Review, Codex Review and a close action. |
| `PSESS-006` | `completed` | `supervised` | `TASK-068` | `run_next` | queue_complete |
| `PSESS-007` | `stopped` | `supervised_executable_local_commit` | `TASK-076` | `` | Owner stop |
| `PSESS-008` | `failed` | `supervised_executable_local_commit` | `TASK-069` | `run_next` | UNSAFE_CONDITION: Codex Execution Adapter stopped: local_command_nonzero_exit |

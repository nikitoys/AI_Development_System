<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/events/pipeline-events.jsonl -->

# Pipeline Audit

Events: `46`
State revision: `46`
Current session: `PSESS-012`

## Timeline

| Time | Event Type | Command | Session | Task | Gate | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `2026-06-19T21:27:58Z` | `session.create` | `pipeline.session.create` | `PSESS-001` | `TASK-055` | `` | PSESS-001 |
| `2026-06-19T21:35:13Z` | `step.started` | `pipeline.step.start` | `PSESS-001` | `` | `` | PSESS-001 |
| `2026-06-19T21:35:14Z` | `queue.planned` | `pipeline.step.result` | `PSESS-001` | `` | `queue_planner` | queue_planner blocked \| No executable task is available in the selected queue. |
| `2026-06-19T21:35:14Z` | `completion` | `pipeline.session.complete` | `PSESS-001` | `` | `` | completed |
| `2026-06-20T09:43:30Z` | `session.create` | `pipeline.session.create` | `PSESS-002` | `` | `` | PSESS-002 |
| `2026-06-20T09:45:28Z` | `step.started` | `pipeline.step.start` | `PSESS-002` | `` | `` | PSESS-002 |
| `2026-06-20T09:45:28Z` | `change.approved` | `pipeline.step.result` | `PSESS-002` | `TASK-068` | `evolution_change_gate` | evolution_change_gate blocked \| Approved linked Evolution Change is required before execution. |
| `2026-06-20T10:16:08Z` | `session.create` | `pipeline.session.create` | `PSESS-003` | `` | `` | PSESS-003 |
| `2026-06-20T10:16:12Z` | `step.started` | `pipeline.step.start` | `PSESS-003` | `` | `` | PSESS-003 |
| `2026-06-20T10:16:13Z` | `queue.planned` | `pipeline.step.result` | `PSESS-003` | `` | `queue_planner` | queue_planner blocked \| No executable task is available in the selected queue. |
| `2026-06-20T10:16:13Z` | `completion` | `pipeline.session.complete` | `PSESS-003` | `` | `` | completed |
| `2026-06-20T10:18:30Z` | `session.create` | `pipeline.session.create` | `PSESS-004` | `` | `` | PSESS-004 |
| `2026-06-20T10:18:35Z` | `step.started` | `pipeline.step.start` | `PSESS-004` | `` | `` | PSESS-004 |
| `2026-06-20T10:20:25Z` | `change.approved` | `pipeline.step.result` | `PSESS-004` | `` | `evolution_change_gate` | evolution_change_gate blocked \| changes=CHG-051,CHG-054,CHG-055,CHG-056,CHG-057 \| Evolution Changes were created and now require Human Owner approval. |
| `2026-06-20T10:48:33Z` | `session.create` | `pipeline.session.create` | `PSESS-005` | `` | `` | PSESS-005 |
| `2026-06-20T10:49:07Z` | `step.started` | `pipeline.step.start` | `PSESS-005` | `` | `` | PSESS-005 |
| `2026-06-20T10:49:14Z` | `close_rework.decision` | `pipeline.step.result` | `PSESS-005` | `TASK-068` | `review_close_gate` | review_close_gate blocked \| changes=CHG-051 \| Auto-close requires Codex execution, Codex Report, Machine Review, Codex Review and a close action. |
| `2026-06-20T10:51:37Z` | `session.create` | `pipeline.session.create` | `PSESS-006` | `TASK-068` | `` | PSESS-006 |
| `2026-06-20T10:51:46Z` | `step.started` | `pipeline.step.start` | `PSESS-006` | `` | `` | PSESS-006 |
| `2026-06-20T10:51:46Z` | `queue.planned` | `pipeline.step.result` | `PSESS-006` | `` | `queue_planner` | queue_planner blocked \| No executable task is available in the selected queue. |
| `2026-06-20T10:51:46Z` | `completion` | `pipeline.session.complete` | `PSESS-006` | `` | `` | completed |
| `2026-06-20T11:55:35Z` | `session.create` | `pipeline.session.create` | `PSESS-007` | `TASK-076` | `` | PSESS-007 |
| `2026-06-20T11:59:11Z` | `stop` | `pipeline.session.stop` | `PSESS-007` | `` | `` | stopped \| Owner stop |
| `2026-06-20T12:00:15Z` | `session.create` | `pipeline.session.create` | `PSESS-008` | `` | `` | PSESS-008 |
| `2026-06-20T12:01:22Z` | `step.started` | `pipeline.step.start` | `PSESS-008` | `` | `` | PSESS-008 |
| `2026-06-20T12:01:29Z` | `token_gate.result` | `pipeline.step.result` | `PSESS-008` | `TASK-069` | `token_budget_gate` | token_budget_gate pass \| changes=CHG-054 |
| `2026-06-20T12:01:31Z` | `codex_run.result` | `pipeline.step.result` | `PSESS-008` | `TASK-069` | `codex_execution_adapter` | codex_execution_adapter fail \| changes=CHG-054 \| Codex Execution Adapter stopped: local_command_nonzero_exit |
| `2026-06-20T12:50:23Z` | `session.create` | `pipeline.session.create` | `PSESS-009` | `TASK-077` | `` | PSESS-009 |
| `2026-06-20T12:50:37Z` | `step.started` | `pipeline.step.start` | `PSESS-009` | `` | `` | PSESS-009 |
| `2026-06-20T12:50:37Z` | `queue.planned` | `pipeline.step.result` | `PSESS-009` | `` | `queue_planner` | queue_planner blocked \| No executable task is available in the selected queue. |
| `2026-06-20T12:50:37Z` | `completion` | `pipeline.session.complete` | `PSESS-009` | `` | `` | completed |
| `2026-06-20T12:52:27Z` | `session.create` | `pipeline.session.create` | `PSESS-010` | `TASK-069` | `` | PSESS-010 |
| `2026-06-20T12:52:36Z` | `step.started` | `pipeline.step.start` | `PSESS-010` | `` | `` | PSESS-010 |
| `2026-06-20T12:52:36Z` | `queue.planned` | `pipeline.step.result` | `PSESS-010` | `` | `queue_planner` | queue_planner blocked \| No executable task is available in the selected queue. |
| `2026-06-20T12:52:36Z` | `completion` | `pipeline.session.complete` | `PSESS-010` | `` | `` | completed |
| `2026-06-20T12:53:13Z` | `session.create` | `pipeline.session.create` | `PSESS-011` | `TASK-069` | `` | PSESS-011 |
| `2026-06-20T12:53:19Z` | `step.started` | `pipeline.step.start` | `PSESS-011` | `` | `` | PSESS-011 |
| `2026-06-20T12:53:19Z` | `queue.planned` | `pipeline.step.result` | `PSESS-011` | `` | `queue_planner` | queue_planner blocked \| No executable task is available in the selected queue. |
| `2026-06-20T12:53:19Z` | `completion` | `pipeline.session.complete` | `PSESS-011` | `` | `` | completed |
| `2026-06-20T12:56:47Z` | `session.create` | `pipeline.session.create` | `PSESS-012` | `` | `` | PSESS-012 |
| `2026-06-20T12:57:00Z` | `step.started` | `pipeline.step.start` | `PSESS-012` | `` | `` | PSESS-012 |
| `2026-06-20T12:57:07Z` | `token_gate.result` | `pipeline.step.result` | `PSESS-012` | `TASK-069` | `token_budget_gate` | token_budget_gate pass \| changes=CHG-054 |
| `2026-06-20T13:01:33Z` | `codex_run.result` | `pipeline.step.result` | `PSESS-012` | `TASK-069` | `codex_execution_adapter` | codex_execution_adapter blocked \| changes=CHG-054 \| Codex Execution Adapter stopped: structured_execution_report_missing |
| `2026-06-21T18:08:51Z` | `step.result` | `pipeline.phase.review` | `PSESS-012` | `` | `` | PSESS-012 |
| `2026-06-21T18:25:30Z` | `step.result` | `pipeline.phase.review` | `PSESS-012` | `` | `` | PSESS-012 |
| `2026-06-21T19:21:51Z` | `step.result` | `pipeline.phase.close` | `PSESS-012` | `` | `` | PSESS-012 |

## Event Type Coverage

- `change.approved`
- `close_rework.decision`
- `codex_run.result`
- `completion`
- `policy.selected`
- `queue.planned`
- `session.create`
- `step.result`
- `step.started`
- `stop`
- `task.selected`
- `token_gate.result`

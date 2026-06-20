<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/events/pipeline-events.jsonl -->

# Pipeline Audit

Events: `21`
State revision: `21`
Current session: `none`

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

## Event Type Coverage

- `change.approved`
- `close_rework.decision`
- `completion`
- `policy.selected`
- `queue.planned`
- `session.create`
- `step.started`
- `stop`
- `task.selected`

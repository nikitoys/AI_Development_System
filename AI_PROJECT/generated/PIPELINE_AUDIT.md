<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/events/pipeline-events.jsonl -->

# Pipeline Audit

Events: `179`
State revision: `179`
Current session: `PSESS-038`

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
| `2026-06-22T14:04:28Z` | `session.create` | `pipeline.session.create` | `PSESS-013` | `` | `` | PSESS-013 |
| `2026-06-22T14:04:28Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-013` | `` | `` | PSESS-013 |
| `2026-06-22T14:05:22Z` | `session.create` | `pipeline.session.create` | `PSESS-014` | `` | `` | PSESS-014 |
| `2026-06-22T14:05:22Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-014` | `` | `` | PSESS-014 |
| `2026-06-22T14:07:26Z` | `session.create` | `pipeline.session.create` | `PSESS-015` | `` | `` | PSESS-015 |
| `2026-06-22T14:07:26Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-015` | `` | `` | PSESS-015 |
| `2026-06-22T14:07:26Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-015` | `` | `` | PSESS-015 |
| `2026-06-22T14:11:00Z` | `session.create` | `pipeline.session.create` | `PSESS-016` | `` | `` | PSESS-016 |
| `2026-06-22T14:11:00Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-016` | `` | `` | PSESS-016 |
| `2026-06-22T14:11:00Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-016` | `` | `` | PSESS-016 |
| `2026-06-23T14:35:24Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-016` | `` | `` | changes=CHG-064 |
| `2026-06-23T14:41:27Z` | `step.result` | `pipeline.phase.execute` | `PSESS-016` | `` | `` | PSESS-016 |
| `2026-06-24T09:01:02Z` | `session.create` | `pipeline.session.create` | `PSESS-017` | `` | `` | PSESS-017 |
| `2026-06-24T09:01:03Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-017` | `` | `` | PSESS-017 |
| `2026-06-24T09:01:03Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-017` | `` | `` | PSESS-017 |
| `2026-06-24T09:03:07Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-017` | `` | `` | changes=CHG-065,CHG-066 |
| `2026-06-24T09:18:34Z` | `step.result` | `pipeline.phase.execute` | `PSESS-017` | `` | `` | PSESS-017 |
| `2026-06-24T09:18:34Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-017` | `` | `` | PSESS-017 |
| `2026-06-24T09:54:38Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-017` | `` | `` | reports=RPT-006 |
| `2026-06-24T09:56:49Z` | `step.result` | `pipeline.phase.verify` | `PSESS-017` | `` | `` | reports=RPT-006 |
| `2026-06-24T10:00:23Z` | `step.result` | `pipeline.phase.verify` | `PSESS-017` | `` | `` | reports=RPT-007,RPT-006 |
| `2026-06-24T10:12:37Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-017` | `` | `` | reports=RPT-007 |
| `2026-06-24T10:12:46Z` | `step.result` | `pipeline.phase.verify` | `PSESS-017` | `` | `` | reports=RPT-007 |
| `2026-06-24T11:03:18Z` | `session.create` | `pipeline.session.create` | `PSESS-018` | `` | `` | PSESS-018 |
| `2026-06-24T11:03:18Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-018` | `` | `` | PSESS-018 |
| `2026-06-24T11:03:25Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-018` | `` | `` | changes=CHG-064 |
| `2026-06-24T11:08:06Z` | `step.result` | `pipeline.phase.execute` | `PSESS-018` | `` | `` | PSESS-018 |
| `2026-06-24T11:08:06Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-018` | `` | `` | PSESS-018 |
| `2026-06-24T11:15:53Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-018` | `` | `` | reports=RPT-008 |
| `2026-06-24T11:15:59Z` | `step.result` | `pipeline.phase.verify` | `PSESS-018` | `` | `` | reports=RPT-008 |
| `2026-06-24T11:26:30Z` | `session.create` | `pipeline.session.create` | `PSESS-019` | `` | `` | PSESS-019 |
| `2026-06-24T11:26:30Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-019` | `` | `` | PSESS-019 |
| `2026-06-24T11:26:30Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-019` | `` | `` | PSESS-019 |
| `2026-06-24T11:29:12Z` | `session.create` | `pipeline.session.create` | `PSESS-020` | `` | `` | PSESS-020 |
| `2026-06-24T11:29:12Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-020` | `` | `` | PSESS-020 |
| `2026-06-24T11:29:19Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-020` | `` | `` | changes=CHG-067 |
| `2026-06-24T11:36:41Z` | `step.result` | `pipeline.phase.execute` | `PSESS-020` | `` | `` | PSESS-020 |
| `2026-06-24T11:36:41Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-020` | `` | `` | PSESS-020 |
| `2026-06-24T11:37:42Z` | `session.create` | `pipeline.session.create` | `PSESS-021` | `` | `` | PSESS-021 |
| `2026-06-24T11:37:42Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-021` | `` | `` | PSESS-021 |
| `2026-06-24T11:37:49Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-021` | `` | `` | changes=CHG-068 |
| `2026-06-24T11:42:49Z` | `step.result` | `pipeline.phase.execute` | `PSESS-021` | `` | `` | PSESS-021 |
| `2026-06-24T11:42:50Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-021` | `` | `` | PSESS-021 |
| `2026-06-24T11:45:52Z` | `session.create` | `pipeline.session.create` | `PSESS-022` | `` | `` | PSESS-022 |
| `2026-06-24T11:45:52Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-022` | `` | `` | PSESS-022 |
| `2026-06-24T11:45:52Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-022` | `` | `` | PSESS-022 |
| `2026-06-24T11:47:14Z` | `session.create` | `pipeline.session.create` | `PSESS-023` | `` | `` | PSESS-023 |
| `2026-06-24T11:47:14Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-023` | `` | `` | PSESS-023 |
| `2026-06-24T11:47:22Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-023` | `` | `` | changes=CHG-069 |
| `2026-06-24T11:54:26Z` | `step.result` | `pipeline.phase.execute` | `PSESS-023` | `` | `` | PSESS-023 |
| `2026-06-24T11:54:26Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-023` | `` | `` | PSESS-023 |
| `2026-06-24T11:55:46Z` | `session.create` | `pipeline.session.create` | `PSESS-024` | `` | `` | PSESS-024 |
| `2026-06-24T11:55:46Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-024` | `` | `` | PSESS-024 |
| `2026-06-24T11:55:53Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-024` | `` | `` | changes=CHG-070 |
| `2026-06-24T12:07:06Z` | `step.result` | `pipeline.phase.execute` | `PSESS-024` | `` | `` | PSESS-024 |
| `2026-06-24T12:07:06Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-024` | `` | `` | PSESS-024 |
| `2026-06-24T12:25:31Z` | `session.create` | `pipeline.session.create` | `PSESS-025` | `` | `` | PSESS-025 |
| `2026-06-24T12:25:31Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-025` | `` | `` | PSESS-025 |
| `2026-06-24T12:27:39Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-025` | `` | `` | PSESS-025 |
| `2026-06-24T13:35:55Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-024` | `` | `` | PSESS-024 |
| `2026-06-24T13:36:16Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-024` | `` | `` | PSESS-024 |
| `2026-06-24T13:38:04Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-024` | `` | `` | reports=RPT-009 |
| `2026-06-24T13:38:09Z` | `step.result` | `pipeline.phase.verify` | `PSESS-024` | `` | `` | reports=RPT-009 |
| `2026-06-24T13:43:43Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-025` | `` | `` | PSESS-025 |
| `2026-06-24T14:07:53Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-025` | `` | `` | PSESS-025 |
| `2026-06-24T14:09:13Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-025` | `` | `` | changes=CHG-071 |
| `2026-06-24T14:27:02Z` | `stop` | `pipeline.session.stop` | `PSESS-025` | `` | `` | stopped \| MAX_STEPS_REACHED: Batch runner reached max_steps 5. |
| `2026-06-24T14:33:50Z` | `step.result` | `pipeline.phase.execute` | `PSESS-025` | `` | `` | PSESS-025 |
| `2026-06-24T14:36:38Z` | `step.result` | `pipeline.phase.verify` | `PSESS-024` | `` | `` | reports=RPT-009 |
| `2026-06-24T14:52:29Z` | `session.create` | `pipeline.session.create` | `PSESS-026` | `` | `` | PSESS-026 |
| `2026-06-24T14:52:29Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-026` | `` | `` | PSESS-026 |
| `2026-06-24T14:52:29Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-026` | `` | `` | PSESS-026 |
| `2026-06-24T15:04:55Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-026` | `` | `` | changes=CHG-072 |
| `2026-06-24T15:12:54Z` | `step.result` | `pipeline.phase.execute` | `PSESS-026` | `` | `` | PSESS-026 |
| `2026-06-24T15:12:54Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-026` | `` | `` | PSESS-026 |
| `2026-06-24T21:38:57Z` | `session.create` | `pipeline.session.create` | `PSESS-027` | `` | `` | PSESS-027 |
| `2026-06-24T21:38:57Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-027` | `` | `` | PSESS-027 |
| `2026-06-24T21:38:57Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-027` | `` | `` | PSESS-027 |
| `2026-06-24T21:46:41Z` | `session.create` | `pipeline.session.create` | `PSESS-028` | `` | `` | PSESS-028 |
| `2026-06-24T21:46:42Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-028` | `` | `` | PSESS-028 |
| `2026-06-24T21:46:49Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-028` | `` | `` | PSESS-028 |
| `2026-06-24T21:57:59Z` | `step.result` | `pipeline.phase.execute` | `PSESS-028` | `` | `` | reports=RPT-010 |
| `2026-06-24T21:58:00Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-028` | `` | `` | reports=RPT-010 |
| `2026-06-24T21:58:00Z` | `step.result` | `pipeline.phase.verify` | `PSESS-028` | `` | `` | reports=RPT-010 |
| `2026-06-25T06:46:29Z` | `session.create` | `pipeline.session.create` | `PSESS-029` | `` | `` | PSESS-029 |
| `2026-06-25T06:46:30Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-029` | `` | `` | PSESS-029 |
| `2026-06-25T06:48:00Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-029` | `` | `` | PSESS-029 |
| `2026-06-25T06:48:19Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-029` | `` | `` | PSESS-029 |
| `2026-06-25T07:22:25Z` | `session.create` | `pipeline.session.create` | `PSESS-030` | `` | `` | PSESS-030 |
| `2026-06-25T07:22:26Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-030` | `` | `` | PSESS-030 |
| `2026-06-25T07:22:32Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-030` | `` | `` | PSESS-030 |
| `2026-06-25T07:33:50Z` | `step.result` | `pipeline.phase.execute` | `PSESS-030` | `` | `` | PSESS-030 |
| `2026-06-25T07:44:58Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-030` | `` | `` | reports=RPT-011 |
| `2026-06-25T07:44:59Z` | `step.result` | `pipeline.phase.verify` | `PSESS-030` | `` | `` | reports=RPT-011 |
| `2026-06-25T08:23:19Z` | `session.create` | `pipeline.session.create` | `PSESS-031` | `` | `` | PSESS-031 |
| `2026-06-25T08:23:19Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-031` | `` | `` | PSESS-031 |
| `2026-06-25T08:23:26Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-031` | `` | `` | PSESS-031 |
| `2026-06-25T08:33:26Z` | `step.result` | `pipeline.phase.execute` | `PSESS-031` | `` | `` | reports=RPT-012 |
| `2026-06-25T08:33:27Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-031` | `` | `` | reports=RPT-012 |
| `2026-06-25T08:33:27Z` | `step.result` | `pipeline.phase.verify` | `PSESS-031` | `` | `` | reports=RPT-012 |
| `2026-06-25T08:38:39Z` | `session.create` | `pipeline.session.create` | `PSESS-032` | `` | `` | PSESS-032 |
| `2026-06-25T08:38:39Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-032` | `` | `` | PSESS-032 |
| `2026-06-25T08:38:51Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-032` | `` | `` | changes=CHG-073 |
| `2026-06-25T09:32:57Z` | `step.result` | `pipeline.phase.execute` | `PSESS-032` | `` | `` | reports=RPT-013 |
| `2026-06-25T09:32:57Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-032` | `` | `` | reports=RPT-013 |
| `2026-06-25T09:32:57Z` | `step.result` | `pipeline.phase.verify` | `PSESS-032` | `` | `` | reports=RPT-013 |
| `2026-06-25T09:35:59Z` | `session.create` | `pipeline.session.create` | `PSESS-033` | `` | `` | PSESS-033 |
| `2026-06-25T09:36:00Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-033` | `` | `` | PSESS-033 |
| `2026-06-25T09:36:07Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-033` | `` | `` | PSESS-033 |
| `2026-06-25T09:48:52Z` | `step.result` | `pipeline.phase.execute` | `PSESS-033` | `` | `` | reports=RPT-014 |
| `2026-06-25T09:48:52Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-033` | `` | `` | reports=RPT-014 |
| `2026-06-25T09:48:53Z` | `step.result` | `pipeline.phase.verify` | `PSESS-033` | `` | `` | reports=RPT-014 |
| `2026-06-25T09:54:26Z` | `session.create` | `pipeline.session.create` | `PSESS-034` | `` | `` | PSESS-034 |
| `2026-06-25T09:54:26Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-034` | `` | `` | PSESS-034 |
| `2026-06-25T09:54:34Z` | `session.create` | `pipeline.session.create` | `PSESS-035` | `` | `` | PSESS-035 |
| `2026-06-25T09:54:35Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-035` | `` | `` | PSESS-035 |
| `2026-06-25T09:54:38Z` | `session.create` | `pipeline.session.create` | `PSESS-036` | `` | `` | PSESS-036 |
| `2026-06-25T09:54:38Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-036` | `` | `` | PSESS-036 |
| `2026-06-25T09:55:44Z` | `session.create` | `pipeline.session.create` | `PSESS-037` | `` | `` | PSESS-037 |
| `2026-06-25T09:55:44Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-037` | `` | `` | PSESS-037 |
| `2026-06-25T09:55:50Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-037` | `` | `` | PSESS-037 |
| `2026-06-25T10:06:11Z` | `step.result` | `pipeline.phase.execute` | `PSESS-037` | `` | `` | PSESS-037 |
| `2026-06-25T10:10:54Z` | `step.result` | `pipeline.phase.execute` | `PSESS-037` | `` | `` | PSESS-037 |
| `2026-06-25T10:11:35Z` | `stop` | `pipeline.session.stop` | `PSESS-037` | `` | `` | stopped \| Owner stop |
| `2026-06-25T10:12:04Z` | `step.result` | `pipeline.phase.execute` | `PSESS-037` | `` | `` | reports=RPT-015 |
| `2026-06-25T10:12:17Z` | `stop` | `pipeline.session.stop` | `PSESS-037` | `` | `` | stopped \| Owner stop |
| `2026-06-25T13:13:44Z` | `session.create` | `pipeline.session.create` | `PSESS-038` | `` | `` | PSESS-038 |
| `2026-06-25T13:13:44Z` | `step.result` | `pipeline.phase.queue_preview` | `PSESS-038` | `` | `` | PSESS-038 |
| `2026-06-25T13:13:51Z` | `step.result` | `pipeline.phase.prepare` | `PSESS-038` | `` | `` | PSESS-038 |
| `2026-06-25T13:13:51Z` | `step.result` | `pipeline.phase.execute` | `PSESS-038` | `` | `` | PSESS-038 |
| `2026-06-25T13:21:41Z` | `step.result` | `pipeline.phase.execute` | `PSESS-038` | `` | `` | reports=RPT-016 |
| `2026-06-25T13:21:41Z` | `step.result` | `pipeline.phase.collect_report` | `PSESS-038` | `` | `` | reports=RPT-016 |
| `2026-06-25T13:21:42Z` | `step.result` | `pipeline.phase.verify` | `PSESS-038` | `` | `` | reports=RPT-016 |

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

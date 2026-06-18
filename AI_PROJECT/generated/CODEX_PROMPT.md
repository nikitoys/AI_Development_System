[SYSTEM]

Active Role: Codex Executor / Web Control Center Performance Engineer
Active Stage: Web Control Center Performance Optimization
Active Document: ai_project_ctl/web/read_model.py / ai_project_ctl/web/server.py
Expected Result: Dashboard and data endpoints become fast without weakening Web write safety or project doctor diagnostics.

Repository: current repository
Task ID: TASK-031
Task Ref: CTL-13
Task UID: tsk_c95542f013df
Legacy Task ID: TASK-031
Task Aliases: TASK-031
Task Epic Key / Local Seq: CTL / 13
Task Title: CTL-13 Optimize Web Control Center performance
Task Status: in_review
Verification Mode: standard

Initiative: INIT-002 — Centralized AI Project Control Plane
Epic: EPIC-005 — Implement unified aictl and local Control Center foundation

Context:
Make Web Control Center dashboard and data endpoints fast by avoiding full project doctor execution on every request.

Details:
Optimize the local Web Control Center read model so normal GET / and GET /data.json requests are fast, while full project doctor diagnostics remain available through explicit refresh or cached results.

Scope:
- Measure current dashboard, data.json, healthz, and project doctor timings.
- Avoid running full project doctor on every GET / and GET /data.json request.
- Add short-lived read-model cache if needed.
- Add doctor result cache with explicit refresh behavior.
- Invalidate relevant caches after POST /actions write actions.
- Keep /healthz fast.
- Show doctor result age or stale indicator if practical.
- Add tests for cache behavior, doctor refresh, and POST /actions cache invalidation.

Out of Scope:
- Do not remove project doctor diagnostics.
- Do not hide FAIL diagnostics.
- Do not weaken Web write safety.
- Do not allow LAN/remote binding.
- Do not add external dependencies.
- Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.

Allowed Files:
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py if cache invalidation is needed after write actions
- scripts/aictl.py if web command routing or doctor refresh flags require compatible updates
- ai_project_ctl/core/registry.py if command metadata requires compatible updates
- tests/test_web_control_center.py
- tests/test_aictl.py if aictl behavior is touched
- tests/test_registry.py if registry metadata is touched
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/CODEX_CURRENT.md via taskctl.py only
- AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only

Acceptance Criteria:
- GET /healthz remains fast and does not run heavy diagnostics.
- GET / and GET /data.json no longer run full project doctor on every request.
- Full project doctor remains available and accurate through explicit refresh or cached diagnostics.
- POST /actions invalidates relevant web caches.
- Web write safety remains unchanged: write actions still route through registered commands and do not directly edit protected files.
- Tests cover dashboard/data performance behavior, doctor refresh, and cache invalidation.
- Required validation, generated checks, project doctor, and protected-file checks pass.

Review Instructions:
- Report before/after timings for project doctor, GET /, GET /data.json, and GET /healthz.
- Verify that project doctor diagnostics were not weakened.
- Verify that Web write actions still require confirmation and route through registered commands.

Execution Rules:
- Do not edit AI_PROJECT/state/*.json manually.
- Do not edit AI_PROJECT/events/*.jsonl manually.
- Do not edit AI_PROJECT/generated/*.md manually unless explicitly instructed; prefer CLI render/build commands.
- Stay within Allowed Files and Scope.
- If task state must change, report the required taskctl command instead of editing state by hand.
- At the end, report changed files, checks run, result, and any unresolved risks.

Suggested lifecycle commands:
```bash
python scripts/taskctl.py task transition TASK-031 --to in_progress
python scripts/taskctl.py task transition TASK-031 --to in_review
python scripts/taskctl.py validate
```

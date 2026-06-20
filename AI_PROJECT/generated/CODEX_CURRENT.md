<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `664`

Task: `PIPE-27 (TASK-078)` — **PIPE-27 Add Persistent Pipeline Session Detail Page**
Epic: `EPIC-007`
Status: `in_progress`
Verification: `strict`
Ref: `PIPE-27`
UID: `tsk_bc97855d54fb`
Legacy ID: `TASK-078`
Aliases: `TASK-078`
Epic Key / Local Seq: `PIPE` / `27`

## Prompt Control Fields

Active Role: `Codex Executor`
Active Stage: `Task Execution`
Active Document: `AI_PROJECT/generated/CODEX_CURRENT.md`
Expected Result: `Task completed according to acceptance criteria`

## Summary

Add a persistent per-session Pipeline page with real-time steps, expandable logs, session actions, artifacts, audit events, and historical availability.

## Description

Create a dedicated Web Control Center page for each pipeline session, for example /pipeline/sessions/PSESS-012. The page must let the Human Owner watch a running session in real time, inspect all steps and logs, execute safe session actions, and reopen the page later as a permanent execution record.

## Scope

- Add a persistent route for individual pipeline sessions, for example /pipeline/sessions/<SESSION_ID>.
- Add links from the main Pipeline sessions table to each session detail page.
- Keep session detail pages available after session completion, blocking, failure, stop, or archive.
- Add a top session header with session id, status, policy, current task, current step, stop reason, started/updated/finished timestamps, elapsed time, and auto-refresh status.
- Add a Status Overview section with a compact progress indicator for the full pipeline flow.
- Add a Current Live Step section for running sessions.
- Auto-refresh the session page every 1-2 seconds while the session is running.
- Stop auto-refresh automatically when the session reaches a terminal state.
- Add a Steps section that lists all pipeline steps in order.
- Each step must be expandable/collapsible.
- Expanded step view must show status, task id/ref, started_at, finished_at, elapsed time, stop reason, gate outcomes, linked artifacts, and logs.
- Step logs must include bounded stdout/stderr snippets when available.
- Show pending steps as visible placeholders, not hidden missing data.
- Add an Actions section with buttons for safe session actions.
- Actions section must include Refresh Session, Run Next, Run Until Blocker, Stop Session, and Resume Session when applicable.
- Actions section must show owner approval actions when applicable, including approve required changes, approve auto-close, and close reviewed task.
- Dangerous or restricted actions must be separated visually and require explicit confirmation.
- Do not expose push, merge, reset, restore, clean, rebase, discard, or destructive git actions.
- Add an Artifacts section showing linked task ids, change ids, report ids, review ids, commit ids, Context Pack path, Codex Prompt path, and generated files.
- Add a Queue Snapshot section showing selected task, queue counts, skipped tasks, and skip reasons such as status_not_executable.
- Add an Audit Events section with latest pipeline events related to the session.
- Add a Files Changed During Session section when changed file data is available.
- Add a Problems / Blockers section that clearly displays current blocker, previous blockers, and known risks.
- Add Raw Debug collapsible sections for session JSON and latest gate details.
- Do not render full CODEX_PROMPT.md content on the page.
- Do not store or render unbounded logs.
- Use bounded snippets, hashes, or safe log references for Codex adapter stdout/stderr.
- Use simple polling for MVP; do not require WebSockets or SSE.
- Add tests for session detail route rendering.
- Add tests for links from main Pipeline page to session detail pages.
- Add tests for running-session auto-refresh markup.
- Add tests for completed historical session rendering.
- Add tests for expandable steps and bounded log display.
- Add tests for action buttons and confirmation requirements.
- Document the session detail page in the owner quickstart and pipeline runner docs.

## Out of Scope

- Do not add background autonomous execution.
- Do not bypass pipeline gates.
- Do not change task lifecycle rules.
- Do not change queue planner semantics except for display/read-model formatting needed by this page.
- Do not approve or accept Evolution Changes automatically.
- Do not auto-close tasks without existing pipeline close gates and owner note.
- Do not push or merge.
- Do not expose full prompt text.
- Do not store full stdout/stderr logs in protected state.
- Do not add external frontend dependencies.
- Do not require WebSockets or SSE in the MVP.
- Do not directly edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.

## Allowed Files

- ai_project_ctl/web/server.py
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/pipeline/state.py
- ai_project_ctl/pipeline/session.py
- ai_project_ctl/pipeline/audit.py
- ai_project_ctl/pipeline/codex_adapter.py
- ai_project_ctl/core/registry.py
- scripts/aictl.py
- tests/test_web_control_center.py
- tests/test_pipeline_runner.py
- tests/test_aictl.py
- ai-system/project-control/pipeline-runner.md
- ai-system/project-control/10-owner-quickstart.md
- AI_PROJECT/state/pipeline_sessions.json via governed CLI/service only
- AI_PROJECT/events/pipeline-events.jsonl via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_STATUS.md via governed CLI/service only
- AI_PROJECT/generated/PIPELINE_AUDIT.md via governed CLI/service only

## Acceptance Criteria

- Each pipeline session has a stable URL such as /pipeline/sessions/PSESS-012.
- The main Pipeline page links each session id to its detail page.
- The session detail page remains available after the session completes, blocks, fails, stops, or is archived.
- Running sessions auto-refresh without manual page reload.
- Auto-refresh stops after a terminal session state.
- The page has a Steps section with all pipeline steps in execution order.
- Each step can be expanded to inspect status, gates, details, and bounded logs.
- The page has an Actions section with session-level buttons.
- Action buttons require confirmation for mutating operations.
- The page separates safe actions, owner approval actions, and restricted/dangerous actions.
- The page shows session summary, live current step, artifacts, queue snapshot, audit events, files changed, blockers, and raw debug sections.
- Codex adapter stdout/stderr are shown only as bounded snippets or safe references.
- Full CODEX_PROMPT.md content is never rendered on the session page.
- Unbounded stdout/stderr logs are never stored or rendered.
- Historical completed sessions can be opened and inspected.
- Tests and project-control validations pass.

## Review Instructions

- Start a running pipeline session and open /pipeline/sessions/<SESSION_ID>.
- Verify the page updates while the session is running.
- Verify the Steps section displays all known steps and pending placeholders.
- Expand each step and verify logs/gates/details are readable.
- Verify Actions buttons appear only when applicable to the session state.
- Verify mutating Actions require confirmation.
- Verify old completed and blocked PSESS records remain viewable.
- Verify no full CODEX_PROMPT.md content appears in page HTML, state, events, or generated output.
- Verify the main Pipeline dashboard links to the session detail page.
- Run web/control-center tests and project-control validation commands.

## Notes

- Observed need: a session such as PSESS-012 can remain running with no dedicated live page showing what is happening.
- Observed UX issue: the current Pipeline page is a dashboard snapshot and not a persistent execution record.
- The MVP should prefer simple polling over WebSockets/SSE to keep implementation small and dependency-free.
- The page should be useful both as a live monitor and as a historical post-mortem view.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-078 --to in_progress
python scripts/taskctl.py task transition TASK-078 --to in_review
python scripts/taskctl.py task approve TASK-078 --notes "..."
python scripts/taskctl.py task transition TASK-078 --to done
python scripts/aictl.py task report submit --task TASK-078 --file /path/to/report.json --confirm
python scripts/taskctl.py prompt build --write
```

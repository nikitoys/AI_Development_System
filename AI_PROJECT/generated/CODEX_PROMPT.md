[SYSTEM]

Active Role: Codex Executor
Active Stage: Task Execution
Active Document: AI_PROJECT/generated/CODEX_CURRENT.md
Expected Result: Task completed according to acceptance criteria

Repository: current repository
Task ID: TASK-049
Task Ref: WFA-18
Task UID: tsk_e878d597769a
Legacy Task ID: TASK-049
Task Aliases: TASK-049
Task Epic Key / Local Seq: WFA / 18
Task Title: UIX-12 Add Project Health Repair Actions
Task Status: in_review
Verification Mode: standard

Initiative: INIT-002 — Centralized AI Project Control Plane
Epic: EPIC-006 — Control Plane Workflow Automation

Context:
Add UI health and repair actions for doctor, stale generated artifacts, docs render, context/Codex refresh, and protected-file checks.

Details:
Turn common project-control warnings into visible UI health signals with safe repair buttons that route through owning CLIs. The owner should be able to diagnose and fix stale generated artifacts without remembering individual commands.

Scope:
- Show project doctor summary in the Web Control Center.
- Show stale context, Codex, docs, task generated, and evolution generated states where detectable.
- Add Run Doctor action.
- Add Refresh Context/Codex action for current or selected task where valid.
- Add Render Docs action through docctl where valid.
- Add Check Protected Files action.
- Show before/after action result through the unified result panel.
- Reject repair actions when no safe target task exists.
- Add tests for doctor pass/warn/fail display and safe repair action routing.

Out of Scope:
- Do not auto-repair without owner confirmation.
- Do not manually edit generated files.
- Do not suppress doctor failures.
- Do not bypass owning CLIs.
- Do not add network or external service dependencies.

Allowed Files:
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/workflows.py if repair workflow metadata needs compatible updates
- ai_project_ctl/core/registry.py if command metadata needs compatible updates
- scripts/aictl.py if routing needs compatible updates
- tests/test_web_control_center.py
- tests/test_workflows.py
- tests/test_aictl.py
- tests/test_registry.py

Acceptance Criteria:
- UI shows project doctor health summary.
- UI shows stale generated artifact warnings in a readable way.
- Run Doctor action works through governed command routing.
- Safe repair actions require confirmation and use owning CLIs.
- Failed health checks remain visible and are not hidden as success.
- No direct generated-file edits are introduced.
- Tests and project-control validations pass.

Review Instructions:
- Verify that repair actions do not run silently.
- Verify that stale context/Codex and docs cases are shown clearly.
- Verify that doctor FAIL is not converted into OK by UI formatting.

Execution Rules:
- Do not edit AI_PROJECT/state/*.json manually.
- Do not edit AI_PROJECT/events/*.jsonl manually.
- Do not edit AI_PROJECT/generated/*.md manually unless explicitly instructed; prefer CLI render/build commands.
- Stay within Allowed Files and Scope.
- If task state must change, report the required taskctl command instead of editing state by hand.
- If `python scripts/aictl.py task report submit --task TASK-049 --file <REPORT.json> --confirm` exists, submit a structured execution report through it instead of editing report state directly.
- At the end, report changed files, checks run, result, and any unresolved risks.

Suggested lifecycle commands:
```bash
python scripts/taskctl.py task transition TASK-049 --to in_progress
python scripts/taskctl.py task transition TASK-049 --to in_review
python scripts/aictl.py task report submit --task TASK-049 --file /path/to/report.json --confirm
python scripts/taskctl.py validate
```

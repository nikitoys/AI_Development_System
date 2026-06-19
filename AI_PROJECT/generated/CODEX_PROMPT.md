[SYSTEM]

Active Role: Codex Executor
Active Stage: Task Execution
Active Document: AI_PROJECT/generated/CODEX_CURRENT.md
Expected Result: Task completed according to acceptance criteria

Repository: current repository
Task ID: TASK-047
Task Ref: WFA-16
Task UID: tsk_0e3c4d7a0a5d
Legacy Task ID: TASK-047
Task Aliases: TASK-047
Task Epic Key / Local Seq: WFA / 16
Task Title: UIX-10 Add Task Review Package View
Task Status: in_review
Verification Mode: standard

Initiative: INIT-002 — Centralized AI Project Control Plane
Epic: EPIC-006 — Control Plane Workflow Automation

Context:
Add a task review view that combines task metadata, linked Change, Codex report, changed files, checks, and owner decision controls.

Details:
Create a review-oriented UI view for tasks in review. The owner should be able to see what Codex changed, what checks passed, what blockers remain, and then make a review decision from one place.

Scope:
- Add a Task Review view or drawer in the Web Control Center.
- Show task ref, legacy id, title, status, summary, scope, and acceptance criteria.
- Show linked Evolution Change status when available.
- Show latest Codex execution report when available.
- Show changed source files and generated/project-control files from the report.
- Show checks and their pass/fail/warn status.
- Show warnings, blockers, and notes from the report.
- Expose Approve & Done and Request Changes controls when valid.
- Use the unified action result panel for review decisions.
- Add tests for review view with report, without report, with linked Change, and invalid states.

Out of Scope:
- Do not auto-approve tasks.
- Do not auto-accept Evolution Changes.
- Do not replace Human Owner review.
- Do not execute tests from the review view in this task.
- Do not edit source or generated files from the review view.

Allowed Files:
- ai_project_ctl/web/read_model.py
- ai_project_ctl/web/server.py
- ai_project_ctl/web/actions.py
- ai_project_ctl/core/workflows.py if review action metadata needs compatible updates
- tests/test_web_control_center.py
- tests/test_workflows.py

Acceptance Criteria:
- Task Review view shows task metadata and acceptance context.
- Task Review view shows latest Codex execution report when available.
- Task Review view shows linked Evolution Change status when available.
- Task Review view shows checks, changed files, warnings, blockers, and notes.
- Owner can make valid review decisions from the view using governed actions.
- Review decision controls remain unavailable for invalid statuses.
- Tests and project-control validations pass.

Review Instructions:
- Verify that the owner can understand what is being accepted before pressing Done.
- Verify that missing Codex report is shown clearly and does not crash the view.
- Verify that review controls still require confirmation and notes.

Execution Rules:
- Do not edit AI_PROJECT/state/*.json manually.
- Do not edit AI_PROJECT/events/*.jsonl manually.
- Do not edit AI_PROJECT/generated/*.md manually unless explicitly instructed; prefer CLI render/build commands.
- Stay within Allowed Files and Scope.
- If task state must change, report the required taskctl command instead of editing state by hand.
- If `python scripts/aictl.py task report submit --task TASK-047 --file <REPORT.json> --confirm` exists, submit a structured execution report through it instead of editing report state directly.
- At the end, report changed files, checks run, result, and any unresolved risks.

Suggested lifecycle commands:
```bash
python scripts/taskctl.py task transition TASK-047 --to in_progress
python scripts/taskctl.py task transition TASK-047 --to in_review
python scripts/aictl.py task report submit --task TASK-047 --file /path/to/report.json --confirm
python scripts/taskctl.py validate
```

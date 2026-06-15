[SYSTEM]

Active Role: AI System Maintainer + Technical Writer AI
Active Stage: Project Control Usage Guide
Active Document: ai-system/project-control/08-usage-guide.md
Expected Result: Usage guide implemented, validation passed, waiting for Human Owner acceptance.

Repository: current repository
Task ID: TASK-001
Task Title: Write Project Control Usage Guide
Task Status: in_review
Verification Mode: standard

Initiative: INIT-001 — AI Development System Evolution
Epic: EPIC-001 — Documentation Rails

Context:
Write the missing practical usage guide for the Project Control Gateway.

Details:
Create ai-system/project-control/08-usage-guide.md and reconcile it through plan, task, prompt and documentation controls.

Scope:
- Create ai-system/project-control/08-usage-guide.md.
- Explain how Human Owner, ChatGPT Orchestrator, Codex Executor, and Python CLIs interact.
- Explain daily usage of planctl.py, taskctl.py, docctl.py, and evolutionctl.py.
- Explain when to create Initiative, Epic, and Task records.
- Explain when to use docctl.py and how CODEX_PROMPT.md fits into execution.
- Explain protected files and what Codex must never edit manually.
- Include practical command examples, common flows, troubleshooting, and final validation checklist.

Out of Scope:
- Do not implement SOP orchestration.
- Do not implement subagents.
- Do not refactor evolutionctl.py.
- Do not add new docctl.py features.
- Do not manually edit AI_PROJECT/state/**.
- Do not manually edit AI_PROJECT/events/**.
- Do not manually edit AI_PROJECT/generated/**.

Allowed Files:
- ai-system/project-control/08-usage-guide.md
- AI_PROJECT/state/plan.json via planctl.py only
- AI_PROJECT/events/plan-events.jsonl via planctl.py only
- AI_PROJECT/generated/CODEX_PLAN.md via planctl.py only
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/CODEX_CURRENT.md via taskctl.py only
- AI_PROJECT/generated/CODEX_PROMPT.md via taskctl.py only
- AI_PROJECT/state/docs.json via docctl.py only
- AI_PROJECT/events/doc-events.jsonl via docctl.py only
- AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only
- AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only

Acceptance Criteria:
- 08-usage-guide.md exists and uses the same practical style as neighboring project-control documents.
- The guide explains role interactions, CLI responsibilities, daily workflow, documentation workflow, protected-file boundaries, troubleshooting, and validation.
- Only supported CLI commands are shown as exact command examples.
- The document is registered through docctl.py and moved no further than review without Human Owner acceptance.
- Plan, task, documentation, smoke, and protected-files validation commands pass.

Review Instructions:
- Verify that no protected project-control files were edited manually.
- Verify that the task and document are not marked Human-approved or active/accepted.
- Verify that unsupported commands are not presented as executable examples.

Execution Rules:
- Do not edit AI_PROJECT/state/*.json manually.
- Do not edit AI_PROJECT/events/*.jsonl manually.
- Do not edit AI_PROJECT/generated/*.md manually unless explicitly instructed; prefer CLI render/build commands.
- Stay within Allowed Files and Scope.
- If task state must change, report the required taskctl command instead of editing state by hand.
- At the end, report changed files, checks run, result, and any unresolved risks.

Suggested lifecycle commands:
```bash
python scripts/taskctl.py task transition TASK-001 --to in_progress
python scripts/taskctl.py task transition TASK-001 --to in_review
python scripts/taskctl.py validate
```

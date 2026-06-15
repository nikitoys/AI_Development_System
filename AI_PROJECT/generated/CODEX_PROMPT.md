[SYSTEM]

Active Role: AI System Maintainer + Prompt/Skill Engineer
Active Stage: Clarification Gate Skill
Active Document: .agents/skills/clarification-gate/SKILL.md
Expected Result: Clarification Gate Skill created; skills README updated if available; validation completed; result remains awaiting Human Owner acceptance.

Repository: current repository
Task ID: TASK-003
Task Title: Create Clarification Gate Skill
Task Status: in_review
Verification Mode: standard

Initiative: INIT-001 — AI Development System Evolution
Epic: EPIC-002 — Skills Layer

Context:
Create a high-priority Clarification Gate Skill for Codex and subagents, defining when to ask the Human Owner versus inspect or proceed with safe assumptions.

Details:
Create .agents/skills/clarification-gate/SKILL.md and update the skills README if present. Route project-control state changes through CLI commands only. Do not self-approve the task, document, or skill as accepted or active.

Scope:
- Create .agents/skills/clarification-gate/SKILL.md with blocker severity, question budget, and subagent guidance.
- Update ai-system/skills/README.md if it exists to recommend the Clarification Gate Skill as high priority.
- Use docctl.py registration only if the documentation registry is intended to track .agents/skills files.
- Run required planctl.py, taskctl.py, docctl.py, smoke, and protected-files validations.

Out of Scope:
- Manual edits to AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.
- Implementation changes to planctl.py, taskctl.py, docctl.py, or evolutionctl.py unless blocked.
- Self-approving the task, document, or skill as accepted, approved, done, or active.

Allowed Files:
- .agents/skills/clarification-gate/SKILL.md
- ai-system/skills/README.md

Acceptance Criteria:
- Skill explains that it prevents premature execution on ambiguous or unsafe requests.
- Skill states the core rule: inspect first, ask only when blocked.
- Skill defines when to ask before task creation, during task execution, and when not to ask.
- Skill includes critical blocker, non-critical ambiguity, and inspectable ambiguity severity model with examples.
- Skill includes a question budget and forbids using clarification questions to avoid normal inspection.
- Skills README recommends the Clarification Gate Skill as high priority if the README exists.
- Required validation commands complete or any blocker is reported.

Review Instructions:
- Review for compliance with Human Owner approval boundaries and protected project-control rules.
- Do not mark accepted, approved, active, or done without Human Owner decision.

Execution Rules:
- Do not edit AI_PROJECT/state/*.json manually.
- Do not edit AI_PROJECT/events/*.jsonl manually.
- Do not edit AI_PROJECT/generated/*.md manually unless explicitly instructed; prefer CLI render/build commands.
- Stay within Allowed Files and Scope.
- If task state must change, report the required taskctl command instead of editing state by hand.
- At the end, report changed files, checks run, result, and any unresolved risks.

Suggested lifecycle commands:
```bash
python scripts/taskctl.py task transition TASK-003 --to in_progress
python scripts/taskctl.py task transition TASK-003 --to in_review
python scripts/taskctl.py validate
```

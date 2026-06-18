[SYSTEM]

Active Role: Codex Executor + Documentation Control Maintainer
Active Stage: Documentation Generated Drift Cleanup
Active Document: AI_PROJECT/generated/DOCS_GAPS.md / scripts/docctl.py
Expected Result: DOCS_GAPS.md drift resolved through docctl.py, generated docs checks pass, protected-files check is clean.

Repository: current repository
Task ID: TASK-018
Task UID: tsk_9ecaaf287358
Legacy Task ID: TASK-018
Task Aliases: TASK-018
Task Title: Fix documentation generated drift
Task Status: in_review
Verification Mode: standard

Initiative: INIT-001 — AI Development System Evolution
Epic: EPIC-001 — Documentation Rails

Context:
Resolve pre-existing DOCS_GAPS.md generated drift through docctl.py so protected-files validation becomes clean again.

Scope:
- Inspect docctl.py behavior and documentation registry state to identify why DOCS_GAPS.md is stale.
- Refresh documentation generated files through docctl.py only.
- Run documentation generated checks and protected-files validation.

Out of Scope:
- Do not change task identity, dependency graph, execution queue, epic keys, or task resolver behavior.
- Do not manually edit AI_PROJECT/state/**, AI_PROJECT/events/**, or AI_PROJECT/generated/**.

Allowed Files:
- AI_PROJECT/state/docs.json via docctl.py only
- AI_PROJECT/events/doc-events.jsonl via docctl.py only
- AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only
- AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only
- scripts/docctl.py only if the drift is caused by a docctl rendering bug

Acceptance Criteria:
- python scripts/docctl.py validate passes.
- python scripts/docctl.py render completes successfully.
- python scripts/docctl.py check-generated passes.
- python scripts/check-protected-project-files.py --verbose no longer reports DOCS_GAPS.md drift.
- No protected AI_PROJECT files are manually edited.

Review Instructions:
- Verify that DOCS_GAPS.md was updated only through docctl.py unless a docctl rendering bug required a scoped scripts/docctl.py fix.
- Verify that TIG/task identity behavior was not modified.

Execution Rules:
- Do not edit AI_PROJECT/state/*.json manually.
- Do not edit AI_PROJECT/events/*.jsonl manually.
- Do not edit AI_PROJECT/generated/*.md manually unless explicitly instructed; prefer CLI render/build commands.
- Stay within Allowed Files and Scope.
- If task state must change, report the required taskctl command instead of editing state by hand.
- At the end, report changed files, checks run, result, and any unresolved risks.

Suggested lifecycle commands:
```bash
python scripts/taskctl.py task transition TASK-018 --to in_progress
python scripts/taskctl.py task transition TASK-018 --to in_review
python scripts/taskctl.py validate
```

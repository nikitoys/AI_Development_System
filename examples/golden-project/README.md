# Golden Project — Task Tracker

Status: Draft

## Purpose

This example demonstrates Foldered Control Mode for a simple Task Tracker project.

It contains project-local control files only. It does not contain product runtime code.

## Multi-Agent Planning Example

The `AI_PROJECT/AGENT_*` files contain a filled non-runtime example for planning a Task Tracker due-date filter enhancement.

The example demonstrates:

- selected SOP;
- Agent Work Package decomposition;
- dependencies;
- `allowed_files` and `locked_files`;
- candidate parallel groups as informational only;
- Human Owner approval boundary;
- result intake, integration review and QA handoff placeholders;
- metrics placeholders;
- dry-run helper usage.

## Safety Boundaries

- Sequential execution remains the default.
- Candidate parallel groups are informational only.
- This example does not authorize execution.
- This example does not authorize parallel execution.
- This example does not authorize automatic execution, merge or acceptance.
- Human Owner approval remains required before any execution.

## Dry-Run Helper

From the AI_Development_System repository root:

```bash
python3 scripts/agent-plan-mvp.py validate --project-root examples/golden-project
python3 scripts/agent-plan-mvp.py check-locks --project-root examples/golden-project
python3 scripts/agent-plan-mvp.py list-parallel-groups --project-root examples/golden-project
python3 scripts/agent-plan-mvp.py generate-prompts --project-root examples/golden-project
```

The helper only reads planning files and prints reports or prompt drafts. It does not execute Codex, create branches or worktrees, merge changes, accept results or modify application code.


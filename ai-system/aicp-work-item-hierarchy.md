# AICP-003: Add Work Item Hierarchy

## Status
Applied

## Problem

AI_Development_System had task lifecycle, roadmap, evolution backlog and Agent Work Packages, but no explicit planning hierarchy between broad goals and executable tasks.

## Evidence

The Human Owner requested an Initiative / Epic / Task hierarchy so `CODEX_PLAN.md` can show planning containers and `CODEX_TASKS.md` can map executable tasks to Initiative and Epic context.

## Root Cause

The system defined tasks as executable units and Agent Work Packages as child planning units, but it did not define the planning containers above tasks.

This made it harder to connect project goals, roadmap direction and grouped work to bounded executable tasks without implying execution authority.

## Proposed Change

Add a Work Item Hierarchy source document defining:

- Goal;
- Initiative;
- Epic;
- Task;
- Agent Work Package.

Update task format, task lifecycle, Agent Work Package documentation, project templates and the golden project so:

- Initiative and Epic are planning containers only;
- Task remains the executable unit;
- Agent Work Package remains a child planning unit under Task;
- Human Owner approval remains required before repository-changing execution.

## Affected Files

- `ai-system/work-item-hierarchy.md`
- `ai-system/task-format.md`
- `ai-system/task-lifecycle.md`
- `ai-system/agent-work-package.md`
- `ai-system/glossary-project.md`
- `ai-system/templates/project/CODEX_PLAN.md`
- `ai-system/templates/project/CODEX_TASKS.md`
- `ai-system/templates/foldered/AI_PROJECT/CODEX_PLAN.md`
- `ai-system/templates/foldered/AI_PROJECT/CODEX_TASKS.md`
- `CODEX_PLAN.md`
- `CODEX_TASKS.md`
- `templates/CODEX_PLAN.template.md`
- `examples/golden-project/AI_PROJECT/CODEX_PLAN.md`
- `examples/golden-project/AI_PROJECT/CODEX_TASKS.md`
- `examples/golden-project/AI_PROJECT/AGENT_PLAN.md`
- `examples/golden-project/AI_PROJECT/AGENT_TASKS.md`
- `examples/golden-project/README.md`
- `ai-system/evolution/evolution-backlog.md`
- `ai-system/system-changelog.md`
- `ai-system/README.md`
- `README.md`
- `README.ru.md`

## Expected Benefit

Planning can now express the path from goal-level direction to concrete execution without confusing planning containers with executable scope.

The hierarchy also makes the relationship between tasks and Agent Work Packages easier to review.

## Risks

The hierarchy could be misunderstood as adding extra approval gates or executable levels.

This risk is mitigated by explicitly documenting that Initiative and Epic are planning containers only, and that Task remains the executable unit.

## Decision

APPROVED by Human Owner request to implement the Work Item Hierarchy plan.

## Version Impact

Minor.

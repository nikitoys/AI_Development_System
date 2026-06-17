<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `34`

Task: `TASK-007` — **Record L4 Role-Agent Runtime Architecture**
Epic: `EPIC-001`
Status: `in_review`
Verification: `standard`

## Prompt Control Fields

Active Role: `AI System Maintainer + System Architect AI + Technical Writer AI`
Active Stage: `Implement approved CHG-004`
Active Document: `CHG-004 / ai-system/l4-role-agent-runtime.md`
Expected Result: `Documentation update ready for review and Human Owner acceptance`

## Summary

Implement approved CHG-004 by creating the L4 Role-Agent Runtime Architecture source document and updating required README, operating model, roadmap, backlog and changelog references.

## Description

Create ai-system/l4-role-agent-runtime.md and update approved source documentation so L4 is documented as an approved bounded implementation target while current implementation maturity remains L3 until future implementation tasks complete. Preserve Python control-kernel boundaries, Controller Codex delegation responsibilities, Codex role-subagent limits, Human Owner final acceptance and L5 prohibitions.

## Scope

- Create ai-system/l4-role-agent-runtime.md defining L4 Role-Agent Runtime Architecture.
- Update approved index, roadmap, operating-model, backlog, changelog and README references.
- Keep L4 bounded by Python control APIs, Controller Codex routing/integration and Human Owner final acceptance.

## Out of Scope

- Do not implement scripts/agentctl.py or any runner/runtime adapter.
- Do not approve L5, autonomous queues, automatic merge, push, PR creation, task acceptance or QA/review closure.

## Allowed Files

- ai-system/l4-role-agent-runtime.md
- ai-system/README.md
- ai-system/operating-model.md
- ai-system/evolution/roadmap.md
- ai-system/evolution/evolution-backlog.md
- ai-system/system-changelog.md
- README.md
- README.ru.md

## Acceptance Criteria

- ai-system/l4-role-agent-runtime.md exists and states L4 is an approved bounded implementation target.
- Document defines Python as strict API/control kernel, Controller Codex as planner/router/delegator/integrator and Codex role subagents as bounded role executors.
- Document maps existing role layers to concrete role-agent IDs.
- Document defines L4 execution flow from approved Task to Human Owner acceptance and conceptual scripts/agentctl.py API surface without implementing it.
- Document distinguishes L3, L4 and L5 and forbids automatic merge, push, PR creation, final acceptance and QA/review closure.
- Operating model, roadmap, backlog, changelog and README/index references are updated.
- Required validation passes and protected AI_PROJECT files are not manually edited.

## Review Instructions

- Review against CHG-004 scope, allowed files, L3/L4/L5 boundaries and protected-file handling.
- Verify source docs do not imply L5 approval or automatic acceptance, merge, push, PR creation, QA closure or review closure.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-007 --to in_progress
python scripts/taskctl.py task transition TASK-007 --to in_review
python scripts/taskctl.py task approve TASK-007 --notes "..."
python scripts/taskctl.py task transition TASK-007 --to done
python scripts/taskctl.py prompt build --write
```

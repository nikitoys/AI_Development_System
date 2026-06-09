# L3 Role-Assigned Parallel Runbook

Status: Draft  
Version: v0.1.0

## Purpose

This runbook explains how the Human Owner or ChatGPT Orchestrator performs a manual role-assigned multi-agent run at `L3 — Manual multi-agent orchestration`.

It is a practical operating guide for using Agent Work Packages, Role-to-Agent Assignments, dependency-aware planning, bounded prompt drafts, Agent Result Intake and Integration Review.

This runbook does not implement runtime behavior.

It does not authorize automatic Codex execution, automatic agent dispatch, automatic multi-agent execution, branch/worktree automation, automatic file modification by orchestration tooling, automatic merge, automatic acceptance or automatic QA/review closure.

## Source Documents

- `runtime-maturity-levels.md`
- `manual-orchestration.md`
- `role-agent-assignment.md`
- `agent-work-package.md`
- `multi-agent-planning.md`
- `parallel-execution-policy.md`
- `agent-result-intake.md`
- `integration-review.md`
- `prompt-lifecycle.md`
- `codex-lifecycle.md`

## Safety Rules

- Runtime remains `DEFERRED`.
- L4 and higher remain future/not approved.
- Sequential execution remains the default.
- Candidate parallel groups are informational only.
- Human Owner approval is required before any candidate group is treated as approved for manual parallel work.
- Agents run manually or externally to orchestration tooling.
- Each agent receives only its bounded prompt or package.
- An agent must not expand parent task scope.
- An Agent Result does not imply acceptance.
- Agent Result Intake is required before review, QA handoff, integration review or acceptance.
- Integration Review is required for parallel results touching related behavior, interfaces, data contracts, file boundaries, user flows, security/privacy assumptions or documentation consistency.
- Human Owner remains the final acceptance authority.

## Required Project Files

For a foldered project, the relevant project-local files are:

```text
AI_PROJECT/AGENT_PLAN.md
AI_PROJECT/AGENT_TASKS.md
AI_PROJECT/AGENT_ASSIGNMENTS.md
AI_PROJECT/AGENT_LOCKS.md
AI_PROJECT/AGENT_RESULTS.md
AI_PROJECT/AGENT_METRICS.md
```

These files are planning, coordination, intake and review records. They are not executable queues.

## Full Manual Flow

1. Choose the parent task.
   - Confirm the task has scope, out of scope, source documents, acceptance criteria and verification expectations.
   - Stop if the parent task is not ready for decomposition.

2. Select the SOP.
   - Record the selected SOP in `AI_PROJECT/AGENT_PLAN.md`.
   - If no SOP applies, record the blocker instead of inventing new behavior.

3. Prepare the Agent Plan.
   - Record the parent task summary.
   - Record decomposition assumptions.
   - Record candidate sequential order and candidate parallel groups.
   - Keep candidate groups informational.

4. Prepare Agent Work Packages.
   - Record packages in `AI_PROJECT/AGENT_TASKS.md`.
   - Each package needs clear scope, out of scope, dependencies, `allowed_files`, `locked_files`, `forbidden_actions`, verification mode and expected output.

5. Prepare `AGENT_ASSIGNMENTS.md`.
   - Assign ready or expected-ready packages to logical agents.
   - Use `role-agent-assignment.md` fields.
   - Confirm each agent receives only its bounded assignment.

6. Run validation.

```bash
python3 scripts/validate-system.py
python3 scripts/agent-plan-mvp.py validate --project-root <project-root>
```

7. List ready Agent Work Package candidates.

```bash
python3 scripts/agent-plan-mvp.py list-parallel-groups --project-root <project-root>
```

8. Review candidate parallel groups.
   - Confirm dependencies are satisfied.
   - Confirm packages do not require each other as same-group inputs.
   - Confirm `allowed_files` and `locked_files` are explicit.
   - Confirm integration review and QA expectations are planned.

9. Human Owner approves one AWP or a candidate group.
   - Approval must identify package IDs, parent task, SOP, allowed files, locked files, known risks and review/QA expectations.
   - Without Human Owner approval, candidate groups remain informational.

10. Generate bounded prompt drafts.

```bash
python3 scripts/agent-plan-mvp.py generate-prompts --project-root <project-root>
```

11. Manually hand prompts to external agent sessions.
   - Use one bounded prompt per assigned agent.
   - Do not let one agent execute another package.
   - Do not use orchestration tooling for automatic dispatch.

12. Collect Agent Results.
   - Each agent result must follow the hardened Agent Result schema in `agent-result-intake.md`.
   - Record results in `AI_PROJECT/AGENT_RESULTS.md` or the project-approved result record.

13. Run Agent Result Intake.
   - Check package identity, scope compliance, `allowed_files`, `forbidden_actions`, verification evidence, risks, blockers and follow-ups.
   - Block review if required result fields are missing.

14. Run Integration Review.
   - Required when parallel outputs touch related behavior, interfaces, data contracts, documentation consistency or other shared assumptions.
   - Check combined scope compliance, dependency assumptions, file conflicts, result claims, verification evidence, review findings and QA readiness.

15. Human Owner decides.
   - Valid decisions: `APPROVED`, `REWORK`, `REJECTED`, `DEFERRED`.
   - Approval of an agent result does not automatically approve the parent task unless the Human Owner explicitly accepts the parent task.

16. Update AWP statuses.
   - Update package status manually according to `agent-work-package.md`.
   - Record rework, blockers, follow-ups and accepted limitations.

17. Recompute the next ready group.

```bash
python3 scripts/agent-plan-mvp.py list-parallel-groups --project-root <project-root>
```

## Example: Backend and Frontend Manual Parallel Work

Starting state:

- `AWP-REQ-001` is completed or accepted.
- `AWP-BE-001` depends on `AWP-REQ-001`.
- `AWP-FE-001` depends on `AWP-REQ-001`.
- `AWP-QA-001` depends on `AWP-BE-001` and `AWP-FE-001`.
- `AWP-REV-001` waits for Integration Review.

Ready group after requirements:

```text
AWP-BE-001
AWP-FE-001
```

Manual assignments:

```text
AWP-BE-001 -> backend_engineer_agent
AWP-FE-001 -> frontend_engineer_agent
```

Waiting packages:

```text
AWP-QA-001 waits for AWP-BE-001 and AWP-FE-001.
AWP-REV-001 waits for Integration Review inputs.
```

Human Owner approval required:

```text
Approve manual parallel work for AWP-BE-001 and AWP-FE-001 under the recorded package scopes, allowed files, locked files, dependencies, verification mode and Integration Review requirement.
```

After manual agent sessions:

1. Collect backend and frontend Agent Results.
2. Run Agent Result Intake for both results.
3. Run Integration Review because backend and frontend may touch related behavior, interfaces, data contracts or user-facing consistency.
4. Human Owner decides whether to approve, request rework, reject or defer.
5. If both results are accepted for their packages, recompute the next ready group. `AWP-QA-001` may become ready after backend and frontend prerequisites are satisfied.

## Stop Conditions

Stop and request Human Owner decision when:

- dependency-aware planning reports missing dependencies or cycles;
- the ready group conflicts with the recorded assignment plan;
- `allowed_files`, `locked_files` or `forbidden_actions` are missing;
- a candidate parallel group has not been approved;
- an agent result is missing required hardened result fields;
- result claims are unverified or contradict the assigned package;
- Integration Review finds conflicting outputs;
- a package tries to expand parent task scope;
- any step implies runtime automation, automatic dispatch, automatic merge or automatic acceptance.

## Boundary Statement

This runbook enables manual multi-threaded coordination only.

It does not create a runtime, dispatcher, scheduler, branch manager, merge tool or acceptance engine.

Runtime remains `DEFERRED`.

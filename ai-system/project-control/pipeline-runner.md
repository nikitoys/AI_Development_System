# Supervised Pipeline Runner SOP

Status: Review

## Purpose

This document explains how the Human Owner, ChatGPT Orchestrator and Codex Executor operate the supervised batch pipeline runner.

The pipeline runner is a controlled project-operation helper. It can plan a queue, prepare a Codex execution context, run guarded pipeline steps, collect review evidence, and stop on blockers. It does not replace Human Owner authority.

Core rule:

```text
Pipeline policy may select automation.
Python enforces the gates.
Codex executes only bounded Tasks.
Human Owner keeps approval and acceptance authority.
```

## Source Files And Generated Output

Runtime implementation:

```text
ai_project_ctl/pipeline/policy.py
ai_project_ctl/pipeline/queue.py
ai_project_ctl/pipeline/session.py
ai_project_ctl/pipeline/runner.py
ai_project_ctl/pipeline/batch.py
ai_project_ctl/pipeline/token_budget.py
ai_project_ctl/pipeline/codex_adapter.py
ai_project_ctl/pipeline/report_gate.py
ai_project_ctl/pipeline/machine_review.py
ai_project_ctl/pipeline/codex_review.py
ai_project_ctl/pipeline/close_policy.py
ai_project_ctl/pipeline/git_commit.py
ai_project_ctl/pipeline/audit.py
```

CLI and UI entry points:

```text
scripts/aictl.py
ai_project_ctl/web/server.py
ai_project_ctl/web/actions.py
ai_project_ctl/web/read_model.py
```

Controlled state and generated output:

```text
AI_PROJECT/state/pipeline_sessions.json
AI_PROJECT/events/pipeline-events.jsonl
AI_PROJECT/generated/PIPELINE_STATUS.md
AI_PROJECT/generated/PIPELINE_AUDIT.md
```

These `AI_PROJECT` files are protected. They must be changed only through governed commands such as `python scripts/aictl.py pipeline ...`.

## Operator Responsibilities

Human Owner:

- chooses the queue and policy preset;
- confirms run actions;
- approves Evolution Changes when approval is required;
- decides whether to accept completed work, request rework, stop the session, or commit locally;
- never treats pipeline success as automatic final acceptance.

ChatGPT Orchestrator:

- helps choose a bounded queue and safe policy;
- explains blockers and next owner actions;
- reviews Codex output when asked;
- does not approve or accept work for the Human Owner.

Codex Executor:

- executes only the generated prompt package for one bounded Task;
- edits only allowed files;
- submits a structured execution report when the pipeline policy requires it;
- does not approve tasks, accept Evolution Changes, push, merge, or mark final acceptance.

Codex Reviewer:

- performs a narrow read-only semantic review;
- returns only a structured verdict: `APPROVE`, `REQUEST_CHANGES`, or `BLOCKED`;
- cannot mutate files, lifecycle state, generated output, commits, or Human Owner decisions;
- cannot override Machine Review failure evidence with semantic approval.

## Safety Boundary

The pipeline must not:

- run an Initiative, Epic, Change Proposal, Review, QA result, Decision, or Release as execution scope;
- edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**`, or `AI_PROJECT/generated/**` manually;
- approve or accept an Evolution Change automatically;
- mark a Task done without the governed review/close path;
- run Codex before Token Budget Gate passes when execution policy requires it;
- close a Task automatically unless policy permits auto-close and both Machine Review and Codex Review gates pass;
- create commits unless policy permits local-only commit and commit readiness is green;
- push, merge, reset, rebase, switch branches, restore files, clean files, or discard changes.

## Policy Presets

Policy is a declarative safety contract. A policy can allow specific automation, but it does not by itself make owner-only decisions.

| Preset | Queue | Codex behavior | Review gates | Close behavior | Commit behavior |
| --- | --- | --- | --- | --- | --- |
| `dry_run` | Manual, max 1 | Disabled | Not required by preset | Disabled | Disabled |
| `supervised` | Ready queue, max 1 | Build prompt only | Machine Review PASS and Codex Review APPROVE are configured for later gates | Disabled | Disabled |
| `supervised_executable` | Ready queue, max 1 | Run local allowlisted Codex command | Requires Codex Report Gate PASS, Machine Review PASS and Codex Review APPROVE | Disabled | Disabled |
| `supervised_autoclose` | Same as `supervised` | Build prompt only by default | Requires Machine Review PASS and Codex Review APPROVE for auto-close policy validity | Auto-close enabled, but real close requires Codex execution and review evidence | Disabled |
| `supervised_executable_autoclose` | Ready queue, max 1 | Run local allowlisted Codex command | Requires Codex Report Gate PASS, Machine Review PASS and Codex Review APPROVE | Auto-close enabled; requires explicit owner auto-close note on the session | Disabled |
| `supervised_local_commit` | Same as `supervised_autoclose` | Build prompt only by default | Requires approved review gates | Auto-close enabled, but blocked before close because Codex execution evidence is missing | Local-only commit policy is blocked before commit |
| `supervised_executable_local_commit` | Same as `supervised_executable_autoclose` | Run local allowlisted Codex command | Requires approved review gates | Auto-close enabled; requires explicit owner auto-close note on the session | Local-only commit enabled after commit readiness |

Important details:

- `RUN_CODEX` policy mode is stricter than prompt-only mode. It requires Token Budget Gate PASS, a human-selected policy, an approved linked Evolution Change when the policy requires it, and a structured execution report.
- `supervised_autoclose` and `supervised_local_commit` do not magically execute Codex. With their default prompt-only Codex mode, they stop before auto-close or commit because the execution and review evidence does not exist.
- Executable presets use the local-command adapter with an exact allowlist for `codex exec`. The adapter validates prompt freshness and task identity before invoking the command, passes `AI_PROJECT/generated/CODEX_PROMPT.md` to `codex exec` through stdin by default, then requires a newly submitted structured execution report before downstream gates can pass.
- Owner-configured Codex sandbox flags belong in `local_command` and must exactly match `command_allowlist`, for example `codex exec -s workspace-write`. The adapter does not hardcode `danger-full-access` or bypass modes.
- Auto-close requires an explicit owner approval note on the session. Use `--auto-close-note "..."` when creating an executable auto-close session.
- Commit policy is always local-only when enabled. Push and merge are forbidden by policy validation.

## Session Lifecycle

A pipeline session is the audit container for one supervised run.

Session statuses:

```text
planned
running
stopped
blocked
failed
completed
archived
```

Active runnable session statuses:

```text
planned
running
stopped
blocked
failed
```

The session stores:

- selected queue;
- policy snapshot;
- current task;
- current step;
- attempt counters;
- gate outcomes;
- linked Change IDs;
- report IDs;
- review IDs;
- commit IDs;
- audit event IDs;
- stop reason.

Create sessions through:

```bash
python scripts/aictl.py pipeline session create --policy supervised --task-ref PIPE-15
```

or for an Epic queue:

```bash
python scripts/aictl.py pipeline session create --policy supervised --epic EPIC-007 --status-filter ready --max-tasks 3
```

Create an executable auto-close session only when the Human Owner explicitly approved auto-close for the selected queue:

```bash
python scripts/aictl.py pipeline session create --policy supervised_executable_autoclose --task-ref PIPE-25 --auto-close-note "APPROVED by Human Owner for this selected session"
```

Do not create or edit `pipeline_sessions.json` manually.

## Queue Planner

The queue planner is read-only. It narrows the existing executable task queue with owner-selected task refs, Epic filters, status filters, max task count, ordering, and policy constraints.

Queue categories:

```text
executable
waiting
blocked
skipped
```

Common blocker and skip reasons include:

- dependency is not done;
- dependency is missing;
- parent Epic is not executable;
- another current task conflicts;
- status is not executable;
- status filter does not match;
- Epic filter does not match;
- policy max tasks was exceeded.

The runner selects the first executable item as the next task. If no executable task is available, `run-next` records a queue-planner blocker and completes the session as queue complete when appropriate.

## Run-Next Algorithm

`pipeline.run_next` advances at most one supervised step.

The implemented order is:

```text
1. Resolve session.
2. Start run_next step.
3. Validate policy snapshot.
4. Preview selected queue.
5. Select next executable Task.
6. Check Codex execution policy.
7. Check linked approved Evolution Change when policy requires it.
8. Run task.prepare_for_codex.
9. If policy is build_prompt_only, stop after prompt build.
10. If policy is run_codex, evaluate Token Budget Gate.
11. Call Codex Execution Adapter only after Token Budget Gate PASS.
12. Evaluate Codex Report Gate.
13. Evaluate Machine Review Gate.
14. Evaluate read-only Codex Review Gate.
15. Apply close or rework policy if enabled.
16. Apply local commit policy if enabled.
17. Record stop reason, gate outcome, side effects and audit references.
```

Run one step:

```bash
python scripts/aictl.py pipeline run-next PSESS-001
```

If no session ID is passed, the current session is used.

## Run-Until-Blocker Algorithm

`pipeline.run_until_blocker` composes `run-next`. It does not introduce background execution or new gate behavior.

It requires explicit confirmation:

```bash
python scripts/aictl.py pipeline run-until-blocker PSESS-001 --confirm
```

The batch runner stops when:

- no session is selected;
- confirmation is missing;
- session policy is invalid;
- session disappears during the run;
- the selected queue completes;
- `max_steps` is reached;
- a `run-next` command fails;
- the first blocker or unsafe condition appears;
- Token Budget Gate fails;
- Codex Report Gate fails;
- Machine Review fails;
- Codex Review requests changes or blocks;
- rework limit is reached;
- close workflow fails;
- commit readiness or git command fails.

Only these stop codes allow the loop to continue to another task:

```text
TASK_AUTO_CLOSED
LOCAL_COMMIT_CREATED
```

Everything else is treated as a blocker or completion condition for the batch.

## Token Budget Gate

The Token Budget Gate evaluates the actual generated Codex prompt payload:

```text
AI_PROJECT/generated/CODEX_PROMPT.md
```

It records:

- prompt path;
- prompt SHA-256;
- prompt byte count;
- prompt token count;
- retrieved context byte count;
- retrieved context token count;
- token-counting strategy;
- whether token count is estimated;
- remaining tokens;
- context-pack metadata;
- compact/split requirement reasons.

Default local counting uses a deterministic byte estimate. A stricter counter can be supplied by implementation code.

In strict mode, the gate fails when token count is unavailable.

Failure codes include:

```text
TOKEN_BUDGET_PROMPT_MISSING
TOKEN_BUDGET_COUNT_UNAVAILABLE
TOKEN_BUDGET_PROMPT_TOO_LARGE
TOKEN_BUDGET_LOW_REMAINING
TOKEN_BUDGET_CONTEXT_REQUIRES_COMPACT_SPLIT
```

If the gate fails, Codex Execution Adapter is not called.

## Codex Execution Adapter

The adapter is called only when policy mode is `run_codex` and Token Budget Gate passes.

Adapter modes:

```text
dry_run
manual_handoff
local_command
```

Behavior:

- `dry_run` blocks with `CODEX_ADAPTER_DRY_RUN`.
- `manual_handoff` blocks with `CODEX_ADAPTER_MANUAL_HANDOFF_REQUIRED`.
- `local_command` runs only an exact command listed in the policy allowlist.
- `local_command` passes `AI_PROJECT/generated/CODEX_PROMPT.md` to the command through stdin by default. The command `codex exec` is never launched with empty input after Token Budget Gate passes.

The adapter validates that the prompt still exists, still hashes to the token-gated payload, and still references the selected Task. If the prompt changes after the token gate, execution stops with `CODEX_ADAPTER_PROMPT_STALE`.

The adapter records stdout/stderr byte counts and SHA-256 refs. For failed local commands it also records short bounded stdout/stderr snippets for diagnostics. It must not store the full prompt text in pipeline state, events or generated output.

If local Codex startup fails because the host sandbox is unavailable, such as `bwrap`, `bubblewrap`, loopback setup, `RTM_NEWADDR`, `Operation not permitted`, user namespace or `unshare` errors, the adapter reports `CODEX_ADAPTER_SANDBOX_UNAVAILABLE` instead of the generic nonzero-exit reason.

When report evidence is required, the adapter expects a newer structured execution report for the task after the local command finishes.

Submit a report with:

```bash
python scripts/aictl.py task report submit --task TASK-066 --file REPORT.json --confirm
```

Before using a local Codex command in an executable pipeline, verify it manually from the repository root:

```bash
codex exec -s workspace-write < AI_PROJECT/generated/CODEX_PROMPT.md
codex exec -s danger-full-access < AI_PROJECT/generated/CODEX_PROMPT.md
```

Use the weakest sandbox that works in the local environment. If `danger-full-access` or a bypass mode is needed because the environment is externally sandboxed, it must be explicitly owner configured in both `local_command` and `command_allowlist`; the adapter does not infer or add it.

## Codex Execution Report Requirements

The report gate validates the latest structured report for the selected Task.

Required report fields:

```text
task_id
implementation_summary
changed_files
generated_files
checks
warnings
blockers
notes
owner_decision_required
```

Optional identity and token fields include:

```text
schema_version
task_ref
reported_task_id
reported_task_ref
token_usage
```

When policy requires token evidence, `token_usage` must include:

```text
prompt_tokens
context_tokens
token_count_strategy
token_count_estimated
```

The report gate blocks:

- missing report state;
- invalid schema;
- task mismatch;
- blockers listed in the report;
- missing required token usage;
- changed files outside task `allowed_files`;
- governed generated output reported incorrectly;
- blocking failed checks.

Warnings do not equal approval. They remain evidence for Machine Review and Human Owner review.

## Machine Review Gate

Machine Review is deterministic. It evaluates:

- Codex Report Gate result;
- reported protected file changes;
- allowed-file scope;
- token usage evidence when required;
- project-control validation commands;
- safe test commands declared in the report.

Built-in project-control checks include:

```bash
python scripts/taskctl.py validate
python scripts/taskctl.py task graph validate
python scripts/taskctl.py check-generated
python scripts/evolutionctl.py validate
python scripts/evolutionctl.py check-generated
python scripts/contextctl.py validate
python scripts/contextctl.py check-generated
python scripts/aictl.py project doctor
python scripts/aictl.py project protected-check
```

Machine Review PASS requires all blocking checks to pass. Blocking failures stop the pipeline before semantic review can approve anything.

## Codex Review Gate

Codex Review is a semantic read-only gate.

The generated review prompt starts with:

```text
[REVIEW]
```

It provides:

- task metadata;
- execution report summary;
- report gate evidence;
- Machine Review evidence;
- context references for generated prompt and Context Pack.

Forbidden actions for the reviewer:

- edit files;
- run lifecycle transitions;
- commit;
- approve as Human Owner;
- override Machine Review failure or warning evidence;
- expand task scope, allowed files, or acceptance criteria.

Expected verdicts:

```text
APPROVE
REQUEST_CHANGES
BLOCKED
```

`APPROVE` means semantic review found no required changes. It is not Human Owner approval.

`REQUEST_CHANGES` means required implementation or evidence fixes were found.

`BLOCKED` means review cannot be completed from available evidence.

Critical or Major findings cannot be combined with `APPROVE`.

## Auto-Close And Rework

Auto-close is policy-controlled and guarded.

Auto-close may run only when:

- policy enables `auto_close_task`;
- Codex Report Gate is PASS;
- Machine Review is PASS;
- Codex Review status is PASS and verdict is `APPROVE`.

The close path delegates to governed workflows:

```text
task.submit_for_review
task.close_reviewed
```

If Codex Review returns `REQUEST_CHANGES`, the policy may move the task through:

```text
task.submit_for_review
task.request_changes
```

Rework is bounded by `max_rework_attempts`, and the Human Owner remains in the loop.

## Evolution Change Gate And Acceptance

When policy requires an approved Change before execution, the selected Task must have a linked Change whose status is one of:

```text
approved
in_progress
in_review
accepted
```

If no approved linked Change exists, the pipeline stops with an owner action requirement. If policy allows creating a missing Change, the pipeline may run the governed `evolution.create_for_task` workflow and then stops until the Human Owner approves the Change.

The pipeline policy must not approve or accept Evolution Changes automatically. Change approval and acceptance remain explicit Human Owner gates.

## Local Commit Policy

Local commit is optional and disabled unless policy explicitly enables it.

When enabled, commit mode must be:

```text
local_only
```

Push and merge are forbidden.

Commit readiness requires:

- safe commit policy;
- Codex Report Gate PASS;
- Machine Review PASS;
- Codex Review APPROVE;
- required Machine Review checks present and PASS;
- selected Task is `done`;
- linked Evolution Change is accepted when one exists;
- dirty files are exactly the approved files from report or session evidence.

Allowed git commands are narrowly constrained:

```text
git status --short --untracked-files=all
git add -- <explicit file paths>
git commit -m <message>
git rev-parse --verify HEAD
```

Forbidden git subcommands include:

```text
push
merge
reset
checkout
rebase
switch
restore
clean
rm
```

The generated commit message includes Task ID, readable Task ref and Pipeline Session ID.

## Web Control Center SOP

Start the local Web Control Center:

```bash
python scripts/aictl.py web --host 127.0.0.1 --port 8765
```

Open:

```text
http://127.0.0.1:8765/pipeline
```

The Pipeline page shows:

- current session;
- selected policy preset;
- executable queue count;
- current step;
- stop reason;
- queue selector;
- policy preset preview;
- queue preview;
- current session gates and steps;
- links to persistent per-session pages such as `/pipeline/sessions/PSESS-012`;
- recent pipeline audit entries.

Each session detail page remains available after the session completes, blocks, fails, stops or is archived. Running sessions poll every two seconds and stop polling when the session leaves `running`. The detail page shows the session header, progress overview, live step, expandable step records, bounded stdout/stderr snippets, artifacts, queue snapshot, related audit events, changed files when report or gate data exists, blockers and bounded raw debug data. It must not render full `CODEX_PROMPT.md` content or expose push, merge, reset, restore, clean, rebase or discard actions.

Normal UI flow:

```text
1. Choose policy, task refs, Epic, status filter, max tasks and order.
2. Preview queue.
3. Create Session.
4. Run Next for one guarded step, or Run Until Blocker for confirmed batch flow.
5. Read the action result panel.
6. If blocked, resolve the owner action before running again.
7. Open the session ID link when you need the persistent live or historical execution record.
8. Refresh Status when generated pipeline output should be updated.
9. Stop Session when the owner intentionally ends a run.
```

UI write actions route through registered `aictl.py` commands. The UI does not write protected JSON, JSONL or generated Markdown directly.

## CLI SOP

Inspect status:

```bash
python scripts/aictl.py pipeline status
python scripts/aictl.py pipeline validate
python scripts/aictl.py pipeline check-generated
```

Render generated pipeline status and audit:

```bash
python scripts/aictl.py pipeline render
```

Create a session:

```bash
python scripts/aictl.py pipeline session create --policy supervised --task-ref PIPE-15
```

Run one step:

```bash
python scripts/aictl.py pipeline run-next
```

Run until blocker:

```bash
python scripts/aictl.py pipeline run-until-blocker --confirm
```

Stop a session:

```bash
python scripts/aictl.py pipeline session stop PSESS-001 --reason "Owner stop" --status stopped
```

Record manual session evidence only when operating a recovery procedure:

```bash
python scripts/aictl.py pipeline session start-step PSESS-001 --step run_next --task TASK-066
python scripts/aictl.py pipeline session step-result PSESS-001 --step run_next --result blocked --gate-name owner_gate --gate-status blocked --stop-reason "Owner stopped for review"
```

Prefer `run-next` and `run-until-blocker` for normal operation.

## Common Blockers And Recovery

| Blocker | Meaning | Recovery |
| --- | --- | --- |
| `PIPELINE_NO_SESSION_SELECTED` | No current session exists and no session ID was passed. | Create a session or pass a session ID. |
| `POLICY_VIOLATION` | Policy snapshot is invalid or unsafe. | Select a valid preset or create a new session. |
| `UNSAFE_CONDITION` | Queue or session state cannot be resolved safely. | Run validation and inspect project-control state through CLIs. |
| `BLOCKED: Codex execution is disabled` | Policy does not permit Codex execution. | Use the prompt/manual handoff path or choose an approved execution policy. |
| `PIPELINE_APPROVED_CHANGE_REQUIRED` | Task requires an approved linked Evolution Change. | Human Owner approves the linked Change, or create/approve the required Change. |
| `TOKEN_BUDGET_FAILURE` | Prompt is missing, too large, unavailable to count in strict mode, low on remaining tokens, or requires compact/split. | Rebuild or reduce context, split the task, or use a policy that still preserves the required gate. |
| `CODEX_REPORT_GATE_FAILURE` | Structured report is missing, mismatched, out of scope or contains blockers. | Submit a valid report with correct task identity, files, checks and token evidence. |
| `MACHINE_REVIEW_FAILURE` | Deterministic checks failed. | Fix validation/generated/protected-file/test failures and rerun. |
| `CODEX_REVIEW_REQUEST_CHANGES` | Semantic review found required changes. | Prepare bounded rework through governed task workflow. |
| `CODEX_REVIEW_BLOCKED` | Semantic review lacks enough evidence or found a blocking condition. | Add missing evidence or resolve the blocker. |
| `REWORK_LIMIT_REACHED` | Policy rework attempt limit is exhausted. | Human Owner decides whether to create a follow-up task or stop. |
| `COMMIT_READINESS_FAILED` | Local commit prerequisites are not green. | Close/accept required state, clear unrelated dirty files, or leave commit disabled. |

## Audit Trail Interpretation

Pipeline audit output is generated from:

```text
AI_PROJECT/events/pipeline-events.jsonl
```

and rendered to:

```text
AI_PROJECT/generated/PIPELINE_AUDIT.md
```

Audit events classify major session lifecycle operations, policy decisions, gates, stops and commits. They keep stable references to sessions, tasks, linked Changes, reports, reviews, commits and event IDs.

Audit payloads must avoid raw secrets and oversized prompt payloads. Validation rejects forbidden payload keys such as raw prompt text, API keys, passwords, secrets and credentials.

Use:

```bash
python scripts/aictl.py pipeline render
python scripts/aictl.py pipeline check-generated
```

to refresh and verify pipeline generated output.

## Validation Checklist

After documentation or pipeline-control work, run the checks required by the current Task. For pipeline SOP documentation, use:

```bash
python scripts/docctl.py validate
python scripts/docctl.py render
python scripts/docctl.py check-generated
python scripts/aictl.py pipeline validate
python scripts/aictl.py pipeline render
python scripts/aictl.py pipeline check-generated
python scripts/taskctl.py validate
python scripts/taskctl.py task graph validate
python scripts/taskctl.py render
python scripts/taskctl.py check-generated
python scripts/evolutionctl.py validate
python scripts/evolutionctl.py render
python scripts/evolutionctl.py check-generated
python scripts/aictl.py project doctor
python scripts/check-protected-project-files.py --verbose
```

Do not run slow or unrelated checks unless the Task requires them or the Human Owner asks for them.

## Final Rule

The pipeline runner is supervised automation.

It can reduce repeated manual steps, but it cannot remove the controlled gates:

```text
bounded Task
approved policy
approved Change when required
token gate
structured report
machine review
read-only semantic review
Human Owner approval and acceptance
local-only commit policy
audit trail
```

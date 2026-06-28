# Pipeline Phase Usage

Status: Draft  
Version: v0.51.0

## Purpose

This guide explains the owner-facing phase-based pipeline commands for supervised Task execution.

The phase pipeline is a guarded command sequence. It prepares one selected Task, executes or hands off Codex work, collects the structured execution report, verifies the result, runs review, and closes only through governed workflow gates.

It does not authorize automatic acceptance, push, merge, deployment, or Human Owner final approval bypass.

## Quickstart

Preview the queue before creating or running a session:

```bash
python scripts/aictl.py pipeline queue preview --task-ref <TASK_REF>
```

Create a session for one Task:

```bash
python scripts/aictl.py pipeline session create --policy supervised_executable_autoclose --task-ref <TASK_REF> --auto-close-note "Owner approved close after review passes"
```

Run the phases explicitly:

```bash
python scripts/aictl.py pipeline phase queue-preview
python scripts/aictl.py pipeline phase prepare
python scripts/aictl.py pipeline phase execute
python scripts/aictl.py pipeline phase collect-report
python scripts/aictl.py pipeline phase verify
python scripts/aictl.py pipeline phase review --build-prompt-only
python scripts/aictl.py pipeline phase review --manual-review-file <REVIEW.json>
python scripts/aictl.py pipeline phase close --confirm
```

`review --build-prompt-only` returns a read-only review prompt. `close` requires an `APPROVE` review verdict recorded through `--manual-review-file` or `--reviewer-command`, unless the selected policy explicitly disables Codex Review and records skipped review evidence.

For one guarded step at a time:

```bash
python scripts/aictl.py pipeline run-next
```

For guarded steps until the first blocker or queue completion:

```bash
python scripts/aictl.py pipeline run-until-blocker --confirm
```

## Phase Sequence

| Phase | Command | Purpose |
| --- | --- | --- |
| Queue preview | `python scripts/aictl.py pipeline phase queue-preview` | Reads the selected queue and identifies the next executable Task. |
| Prepare | `python scripts/aictl.py pipeline phase prepare` | Checks selected Task and Change gates, then prepares context and prompt artifacts. |
| Execute | `python scripts/aictl.py pipeline phase execute` | Runs the configured Codex adapter or stops for manual handoff. |
| Collect report | `python scripts/aictl.py pipeline phase collect-report` | Finds the latest structured execution report for the selected Task. |
| Verify | `python scripts/aictl.py pipeline phase verify` | Runs report, git diff, protected-file, and allowed-file gates according to policy. |
| Review | `python scripts/aictl.py pipeline phase review --manual-review-file <REVIEW.json>` | Builds a read-only Codex review prompt, or evaluates a manual/reviewer JSON verdict when configured. |
| Close | `python scripts/aictl.py pipeline phase close --confirm` | Runs close preflight and governed close workflow after required review evidence. |

The same sequence is used by `pipeline run-next`. `run-next` advances at most one required phase and records the result in the governed pipeline session.

## Outcome Statuses

Every phase result uses one of these stable statuses:

| Status | Meaning | Typical owner action |
| --- | --- | --- |
| `passed` | The phase gate succeeded and the next phase may run. | Continue with the next phase. |
| `blocked` | The pipeline reached a controlled safe stop. This is a normal owner-action state, not automatically a failed task. | Read `blocked_by`, `reason`, and `next_action`; resolve the required owner or workflow action; rerun the phase or next allowed phase. |
| `failed` | The command, input, local tool, policy, or review JSON failed in a way the pipeline cannot treat as an owner-action gate. | Fix the failing input/tool/configuration, then rerun the phase. |
| `skipped` | A phase or gate was intentionally skipped by policy and recorded as evidence. | Continue only if the policy and next phase allow it. |

Blocked outcomes are expected in supervised operation. They preserve control when the system needs an owner decision, a structured report, a review verdict, rework planning, a valid policy, or explicit close evidence.

## Common Blocked States

### Manual Codex Handoff

`execute` can block with `MANUAL_HANDOFF_REQUIRED` or `CODEX_ADAPTER_MANUAL_HANDOFF_REQUIRED` when the selected policy requires a human-operated Codex session.

The phase output includes the prepared prompt path and a task-specific report submission command. Run Codex manually with that prompt, then submit the structured execution report:

```bash
python scripts/aictl.py pipeline report template --task <TASK_REF>
python scripts/aictl.py task report submit --task <TASK_REF> --file <REPORT.json> --confirm
```

After the report is submitted, continue with:

```bash
python scripts/aictl.py pipeline phase collect-report
```

When `run-next` sees an `execute` blocker caused by manual handoff, the next runnable phase is `collect-report` after the owner supplies the report.

### Missing Report

`collect-report` blocks with `REPORT_MISSING` when no structured execution report exists for the selected Task.

Submit a report through the governed report command, then rerun collection:

```bash
python scripts/aictl.py task report submit --task <TASK_REF> --file <REPORT.json> --confirm
python scripts/aictl.py pipeline phase collect-report
```

Use the recovery override only when supervised recovery intentionally accepts an existing matching report:

```bash
python scripts/aictl.py pipeline phase collect-report --allow-existing-report
```

Do not skip `verify` after report recovery. Run:

```bash
python scripts/aictl.py pipeline phase verify
```

### Review Requests Changes

`review` can block when the reviewer verdict is `REQUEST_CHANGES`. The result records `rework_required` and the reviewer findings/risks.

Route the owner decision through a governed workflow before continuing:

```bash
python scripts/aictl.py workflow run task.request_changes --task <TASK_REF> --notes "<review findings>" --confirm
```

After rework, rerun the relevant phase sequence from preparation or verification as appropriate. Do not close a Task directly from `changes_requested`.

### Close Requires Owner Evidence

`close` can block when close policy is disabled, required phase evidence is incomplete, owner close notes are missing, linked Evolution Change acceptance is blocked, or local commit readiness is blocked.

Resolve the reported `blocked_by` reason and rerun:

```bash
python scripts/aictl.py pipeline phase close --confirm
```

## CI Exit Codes

CI-style exit codes apply when `--ci` is used with `run-next` or `run-until-blocker`:

```bash
python scripts/aictl.py pipeline run-next --ci
python scripts/aictl.py pipeline run-until-blocker --confirm --ci
```

Exit codes:

| Pipeline outcome | Exit code |
| --- | --- |
| `passed` or queue `completed` | `0` |
| `failed` | `1` |
| `blocked` | `2` |

Without `--ci`, human safe-stop behavior is unchanged. A blocked result should be treated as "owner action required" rather than a task failure unless the recorded reason says otherwise.

## Useful Inspection Commands

```bash
python scripts/aictl.py pipeline status
python scripts/aictl.py pipeline validate
python scripts/aictl.py pipeline check-generated
python scripts/aictl.py pipeline policy list
python scripts/aictl.py pipeline policy show <POLICY_NAME>
```

Use these commands to inspect governed state and generated status. Do not edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**`, or `AI_PROJECT/generated/**` manually.

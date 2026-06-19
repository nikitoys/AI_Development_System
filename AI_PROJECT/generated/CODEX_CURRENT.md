<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/tasks.json -->

# Current Codex Task

Revision: `332`

Task: `WFA-06 (TASK-037)` — **WFA-06 Documentation Audit And Cleanup**
Epic: `EPIC-006`
Status: `in_progress`
Verification: `standard`
Ref: `WFA-06`
UID: `tsk_c4ef4282293c`
Legacy ID: `TASK-037`
Aliases: `TASK-037`
Epic Key / Local Seq: `WFA` / `6`

## Prompt Control Fields

Active Role: `Technical Writer AI / AI System Maintainer`
Active Stage: `Workflow Automation Documentation Cleanup`
Active Document: `AI_PROJECT/generated/CODEX_TASKS.md`
Expected Result: `Documentation is updated after workflow automation features are implemented and checked through documentation/project-control validation.`

## Summary

Audit and update documentation after workflow automation and UI improvements are implemented.

## Description

Update owner-facing and system documentation so aictl, Web Control Center, workflows, Evolution Change wizard, task creation wizard, bulk import, review helpers, protected-file rules, and generated-output rules are current and non-contradictory.

## Scope

- Review README.md, AGENTS.md, project-control docs, owner quickstart, and usage guide.
- Make aictl/web/workflows the preferred owner-facing path.
- Keep legacy ctl scripts documented as compatibility tools.
- Remove or mark stale instructions.
- Document bulk task import format.
- Document Evolution Change wizard.
- Document Prepare for Codex workflow.
- Document review/close helpers.
- Run docctl validation/render/check-generated if docs registry is used.

## Out of Scope

- Do not change command behavior.
- Do not add new workflow behavior.
- Do not edit generated docs manually.
- Do not mark docs accepted without owner approval.

## Allowed Files

- README.md
- AGENTS.md
- ai-system/project-control/08-usage-guide.md
- ai-system/project-control/10-owner-quickstart.md
- ai-system/project-control/** if documentation index/appendix updates are needed
- AI_PROJECT/state/docs.json via docctl.py only
- AI_PROJECT/events/doc-events.jsonl via docctl.py only
- AI_PROJECT/generated/DOCS_INDEX.md via docctl.py only
- AI_PROJECT/generated/DOCS_GAPS.md via docctl.py only
- AI_PROJECT/state/tasks.json via taskctl.py only
- AI_PROJECT/events/task-events.jsonl via taskctl.py only
- AI_PROJECT/generated/CODEX_TASKS.md via taskctl.py only
- AI_PROJECT/generated/CODEX_CURRENT.md via taskctl.py only
- AI_PROJECT/generated/TASK_EXECUTION_QUEUE.md via taskctl.py only

## Acceptance Criteria

- Documentation reflects the current aictl/web/workflow model.
- Legacy ctl scripts are described as compatibility layer.
- Bulk task import is documented.
- Evolution Change Flow is documented as controlled self-evolution.
- Generated files are clearly described as derived output.
- Protected-file rules are current.
- Documentation checks and project-control checks pass.

## Review Instructions

- Verify documentation consistency, stale instruction cleanup, protected/generated file rules, docctl checks, project-control checks, and no command behavior changes.

## Notes

- Depends on WFA-01.
- Depends on WFA-02.
- Depends on WFA-03.
- Depends on WFA-04.
- Depends on WFA-05.
- Documentation cleanup should happen after workflow features are implemented.

## Useful CLI

```bash
python scripts/taskctl.py task transition TASK-037 --to in_progress
python scripts/taskctl.py task transition TASK-037 --to in_review
python scripts/taskctl.py task approve TASK-037 --notes "..."
python scripts/taskctl.py task transition TASK-037 --to done
python scripts/taskctl.py prompt build --write
```

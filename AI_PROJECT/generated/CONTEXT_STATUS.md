<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-062 PIPE-11 Auto Review Auto Close Policy Apply policy-controlled close/rework decisions only after Machine Review PASS and Codex Review APPROVE. Implement the decision logic that maps review gate results into task done, changes_requested, rework loop, or stop states under explicit automation policy. ai_project_ctl/pipeline/close_policy.py Pipeline can safely close or request changes for tasks only when policy and review gates allow it. Implement decision logic for Machine Review result plus Codex Review result. Allow auto-close only if policy allows and Machine Review PASS and Codex Review APPROVE. Move task to changes_requested or start a bounded rework loop only when policy allows and review verdict requests changes. Stop when review is blocked, malformed, failing, or policy disallows automatic lifecycle mutation. Require explicit audit notes that identify policy, machine gate, Codex review verdict, and report id. Prevent auto-close when task report has blockers or changed files outside allowed_files. Add tests for approve+pass close, request changes, blocked review, machine fail, policy disabled, and rework-limit reached. Do not bypass task lifecycle transitions. Do not accept linked Evolution Changes. Do not commit. Do not treat Codex Review as Human Owner approval outside the selected policy. Do not continue rework indefinitely. ai_project_ctl/pipeline/close_policy.py ai_project_ctl/pipeline/runner.py if integration is needed ai_project_ctl/core/workflows.py if close/request-changes workflow metadata needs compatible updates tests/** ai-system/project-control/** if auto-close documentation is needed Auto-close requires policy permission, Machine Review PASS, and Codex Review APPROVE. REQUEST_CHANGES moves to changes_requested or starts rework only if policy allows. Blocked or failed gates stop the pipeline. Rework loop has a policy-controlled maximum. Lifecycle mutations route through governed task workflows/commands. Tests and project-control validations pass. Verify auto-close cannot happen on Machine Review FAIL or Codex Review REQUEST_CHANGES. Verify lifecycle changes are routed through governed commands.","schema_version":1,"task_id":"TASK-062"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-062`
Limit: `8`
Docs revision: `24`
Tasks revision: `549`
Indexed source documents: `10`
Indexed chunks: `890`
Selected chunks: `8`
Excluded registered sources: `134`

## Selected Source Paths

- ai-system/agent-delegation.md
- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `93`
- template document excluded by default: `41`

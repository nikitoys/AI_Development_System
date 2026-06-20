<execute|review|verify|repair>
- Source: prompt build argument `--profile`.
- Default: `execute`.

<TASK_ID>
- Source: `task.id` from `AI_PROJECT/state/tasks.json`.

<TASK_REF>
- Source: `task.ref` from `AI_PROJECT/state/tasks.json`.
- If missing: omit `/ <TASK_REF>`.

<TASK_STATUS>
- Source: `task.status` from `AI_PROJECT/state/tasks.json`.

<TASKS_REVISION>
- Source: top-level `revision` from `AI_PROJECT/state/tasks.json`.

<none|manual|light|standard|strict>
- Source: `task.verification_mode`.
- Default: `standard`.

<ROLE_LINE>
- Source: selected prompt profile.
- execute: `Codex Executor. Execute one bounded task. Do not self-approve.`
- review: `Codex Reviewer. Check work against acceptance criteria. Do not modify files.`
- verify: `Verifier. Return pass, retry, or fail with evidence.`
- repair: `Codex Executor. Fix only requested changes. Do not expand scope.`

<ONE_SENTENCE_MAIN_OBJECTIVE>
- Source priority:
  1. `compiled_contract.objective`
  2. `task.goal`
  3. `task.summary`
  4. `task.title`
- Rule: one sentence only.

<SHORT_TASK_SUMMARY>
- Source priority:
  1. `task.summary`
  2. `task.title`

<ACTION_TO_PERFORM>
- Source: items from `task.scope`.
- Rule: each item should be an action.

<BEHAVIOR_OR_CONSTRAINT_TO_PRESERVE>
- Source priority:
  1. specific preservation item from `task.scope`
  2. relevant item derived from `task.acceptance_criteria`
  3. omit if not available

<EDITABLE_PATH>
- Source: `task.allowed_files`.
- Rule: only files Codex may edit.

<READ_ONLY_REF_PATH>
- Source priority:
  1. selected sources from `CONTEXT_PACK.md`
  2. `compiled_contract.context_refs`
  3. documentation refs selected by Context Resolver
- Rule: read-only refs are never editable.

<IMPLEMENTATION_STEP>
- Source: enabled items from `task.execution_steps`.
- Fallback: `compiled_contract.execution_steps`.
- If no specific steps exist: omit `Execution Steps` section.

<EXPECTED_WORKING_RESULT>
- Source: item from `task.acceptance_criteria`.
- Prefer criterion describing main expected result.

<IMPORTANT_BEHAVIOR_THAT_MUST_NOT_BREAK>
- Source: item from `task.acceptance_criteria`.
- Fallback: derived from `task.out_of_scope` or existing behavior mentioned in `task.scope`.

<HOW_TO_VERIFY_THE_RESULT>
- Source priority:
  1. verification-related item from `task.acceptance_criteria`
  2. `task.verification`
  3. derived check from allowed files / changed area

<VERIFICATION_MODE>
- Source: `task.verification_mode`.
- Default: `standard`.

<CHECK_OR_COMMAND>
- Source priority:
  1. `task.verification`
  2. `compiled_contract.verification_checks`
  3. derived command from changed files
  4. fallback text: `Run the smallest relevant checks for the changed files.`

<CONTEXT_PACK_SHA256>
- Source: computed SHA-256 of `AI_PROJECT/generated/CONTEXT_PACK.md`.
- Or: `current_execution.context_pack.sha256`.

<DOCS_REVISION>
- Source: Context Pack metadata `docs_revision`.
- Fallback: `AI_PROJECT/state/docs.json` revision.

<CONTEXT_TASKS_REVISION>
- Source: Context Pack metadata `tasks_revision`.

<SOURCE_PATH>
- Source: selected source path from Context Pack selected sources.

<START>
- Source: selected source start line from Context Pack selected sources.

<END>
- Source: selected source end line from Context Pack selected sources.
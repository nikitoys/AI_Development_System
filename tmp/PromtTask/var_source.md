<PROFILE> — build command argument; for MVP default: execute.
<TASK_ID> — task.id from AI_PROJECT/state/tasks.json.
<REFERENCE_ID> — task.ref from AI_PROJECT/state/tasks.json; if missing, omit.
<TASK_STATUS> — task.status from AI_PROJECT/state/tasks.json.
<TASKS_REVISION> — top-level revision from AI_PROJECT/state/tasks.json.
<VERIFICATION_MODE> — task.verification_mode; default: standard.
<CODEX_ROLE> — task.active_role for MVP; future source: compiler profile role map.
<ROLE_MAIN_RULE> — compiler policy default for selected role; for MVP: Execute one bounded task. Do not self-approve.
<PROFILE_NAME> — compiler profile map; future-only, do not render into runtime prompt for MVP.
<ROLE_NAME> — compiler profile map; future-only, do not render into runtime prompt for MVP.
<ROLE_RULE> — compiler profile map; future-only, do not render into runtime prompt for MVP.
<OBJECTIVE> — task.summary; fallback: task.title; render as one short sentence.
<TASK_SUMMARY> — task.summary; fallback: task.title.
<MAIN_ACTION> — do not generate separately; use task.scope items.
<IMPORTANT_RELATED_ACTION> — do not generate separately; use task.scope items.
<WHAT_MUST_BE_PRESERVED_OR_NOT_BROKEN> — do not generate separately; use task.scope or task.acceptance_criteria items.
<EDITABLE_FILE_PATH> — task.allowed_files.
<READ_ONLY_REF_PATH> — Context Pack selected source path; if no Context Pack, omit Read-only refs.
<EXECUTION_STEP> — future task.execution_steps; currently missing, so omit Execution Steps section for MVP.
<WHAT_MUST_WORK> — do not generate separately; use task.acceptance_criteria items.
<WHAT_MUST_NOT_BREAK> — do not generate separately; use task.acceptance_criteria items.
<HOW_TO_VERIFY_IT> — do not generate separately; use task.acceptance_criteria items or default verification text.
<CHECK_COMMAND> — future task.verification_checks; currently missing, so use compiler default check instruction.
<CONTEXT_PACK_PATH> — current_execution.context_pack.relative_path or default AI_PROJECT/generated/CONTEXT_PACK.md when context is attached.
<CONTEXT_PACK_SHA256> — current_execution.context_pack.sha256 or computed sha256 of AI_PROJECT/generated/CONTEXT_PACK.md.
<DOCS_REVISION> — Context Pack metadata docs_revision.
<REFERENCE_FILE_PATH> — Context Pack selected source path.
<START_LINE> — Context Pack selected source start_line.
<END_LINE> — Context Pack selected source end_line.
<PROTECTED_PATH> — compiler policy default; render fixed paths: AI_PROJECT/state/**, AI_PROJECT/events/**, AI_PROJECT/generated/**.

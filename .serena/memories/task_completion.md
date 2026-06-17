# Task Completion

- For project-control/task work, run relevant validation after mutations: `python scripts/taskctl.py validate`, `python scripts/taskctl.py render`, `python scripts/taskctl.py check-generated`; for plans also `python scripts/planctl.py validate` and `python scripts/planctl.py render`.
- For documentation-affecting tasks, run `python scripts/docctl.py validate`, `python scripts/docctl.py render`, and `python scripts/docctl.py check-generated`.
- For context-affecting tasks, run `python scripts/contextctl.py validate`, `python scripts/contextctl.py check-generated`, and usually `python scripts/smoke-context-control.py`.
- For code changes, at minimum run `python -m py_compile` for touched Python scripts and the task-specific smoke scripts listed in the prompt.
- Run `python scripts/check-protected-project-files.py --verbose` before final reporting when protected project-control outputs may have changed through CLIs.
- Move the Task to `in_review` through `taskctl.py` only after implementation and checks are complete. Do not mark approved/done; Human Owner acceptance is required.
- Final report should include changed files, commands/checks run, validation result, generated outputs updated by CLI, behavior changes, risks/blockers, and owner action required. Mention that `serena memories check` can verify onboarding memory references when relevant.
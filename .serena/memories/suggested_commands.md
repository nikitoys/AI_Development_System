# Suggested Commands

- Inspect current task state: `python scripts/taskctl.py show`; `python scripts/taskctl.py current show`; `python scripts/taskctl.py validate`.
- Task lifecycle: `python scripts/taskctl.py task transition TASK-### --to in_progress`; later `--to in_review`. Do not use approval/done transitions without Human Owner authority.
- Task generated outputs: `python scripts/taskctl.py render`; `python scripts/taskctl.py check-generated`; prompt package via `python scripts/taskctl.py prompt build --write` or `python scripts/codexctl.py build ...` when codexctl owns the operation.
- Plan validation/render: `python scripts/planctl.py validate`; `python scripts/planctl.py render`.
- Docs control: `python scripts/docctl.py scan --scope all`; `python scripts/docctl.py validate`; `python scripts/docctl.py render`; `python scripts/docctl.py check-generated`.
- Context control: `python scripts/contextctl.py status`; `python scripts/contextctl.py pack build --task TASK-### --write`; `python scripts/contextctl.py validate`; `python scripts/contextctl.py check-generated`.
- Codex prompt control: `python scripts/codexctl.py status`; `python scripts/codexctl.py build --task TASK-###`; `python scripts/codexctl.py clear`.
- Smoke/protection checks: `python scripts/smoke-project-control.py`; `python scripts/smoke-doc-control.py`; `python scripts/smoke-context-control.py`; `python scripts/check-protected-project-files.py --verbose`.
- Python syntax checks are direct: `python -m py_compile scripts/<file>.py`.
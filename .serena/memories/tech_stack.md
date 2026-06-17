# Tech Stack

- Primary implementation language: Python scripts under `scripts/`, using only the Python standard library unless a task explicitly permits otherwise.
- No project package manifest was present during onboarding (`pyproject.toml`, `requirements*.txt`, `package.json`, `Makefile`, `pytest.ini`, `setup.cfg`, `tox.ini` absent). Validation is command/script based.
- Main CLI gateways: `scripts/planctl.py`, `scripts/taskctl.py`, `scripts/docctl.py`, `scripts/evolutionctl.py`, `scripts/contextctl.py`, `scripts/codexctl.py`.
- Additional validation/smoke helpers include `scripts/smoke-project-control.py`, `scripts/smoke-doc-control.py`, `scripts/smoke-context-control.py`, `scripts/check-protected-project-files.py`, `scripts/check-docs-integrity.py`, `scripts/validate-system.py`, and `scripts/verification/run_checks.py`.
- Documentation source is Markdown under `/ai-system`; machine-checkable specs live under `/spec`; skills live under `.agents/skills/**/SKILL.md`.
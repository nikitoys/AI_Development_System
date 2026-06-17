# Core

- Repository is an AI Development System control plane, not a product app. `/ai-system` is the primary source-of-truth document tree for behavior, governance, lifecycles, roles, workflows, templates, skills guidance, and system evolution.
- Root `/AI_PROJECT` is this repository's self-hosted project-control layer. It is distinct from reusable templates under `/ai-system/templates/**/AI_PROJECT` and non-runtime examples under `/examples/golden-project/AI_PROJECT`.
- Protected paths must not be edited manually: `AI_PROJECT/state/**`, `AI_PROJECT/events/**`, `AI_PROJECT/generated/**`. Mutate them only through the owning CLI gateways.
- Executable work is bounded by `Task`; Initiatives and Epics are planning containers only. Codex executes current/approved/ready tasks and must not self-approve or mark owner acceptance.
- Read routing: for repo work start with `AGENTS.md` and the mandatory `/ai-system` docs. For current execution, inspect `AI_PROJECT/generated/CODEX_CURRENT.md`, `CODEX_TASKS.md`, `CODEX_STATUS.md`, and `CODEX_PROMPT.md` as readable generated views.
- Related memories: CLI/tooling in `mem:tech_stack`; useful commands in `mem:suggested_commands`; local conventions in `mem:conventions`; done checks in `mem:task_completion`.
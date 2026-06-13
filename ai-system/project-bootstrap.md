# Project Bootstrap

Status: Draft
Version: v0.2.0

## Purpose

This document defines how to initialize a concrete project repository so it can be managed through the AI Development System.

Bootstrap creates a local control layer, records the target application directory, sets the default verification mode and stops for Human Owner approval before implementation begins.

## Recommended Bootstrap Model

Use Foldered Control Mode by default:

```text
/project-root
├── AGENTS.md
├── AI_Development_System/
├── AI_PROJECT/
└── <target-app-directory>/
```

Root Control Mode remains supported for small or legacy projects, but new projects should use Foldered Control Mode unless the Human Owner explicitly chooses otherwise.

## Governed Entity

A project bootstrap is a controlled initialization flow that adds or adapts project-level control files in a concrete repository.

Bootstrap is not application implementation. It must not rewrite application code or product behavior unless the Human Owner explicitly approves a separate implementation task.

## Source of Truth

Default source-of-truth documents for bootstrap are:

- `/ai-system/project-integration-model.md`;
- `/ai-system/project-control-files.md`;
- `/ai-system/project-operation-profile.md`;
- `/ai-system/verification-modes.md`;
- `/ai-system/templates/foldered/`;
- `/ai-system/templates/project/` for Root Control Mode compatibility;
- `/ai-system/rules.md`;
- `/ai-system/prompt-lifecycle.md`;
- project-specific Human Owner instructions.

## When to Bootstrap

Bootstrap is appropriate when:

- starting a new project repository;
- adopting AI_Development_System in an existing repository;
- recovering a repository that lacks durable AI/Codex state files;
- standardizing project workflow before Codex implementation work starts.

Bootstrap should not be used to sneak application changes into a documentation or process task.

## Questions for the Human Owner

Before creating project control files, ask or infer only what is necessary:

1. Project name.
2. Human Owner language.
3. Target app directory, or whether the repository root is the application root.
4. Project mission and non-goals.
5. Default verification mode.
6. Default answer style and verification budget, if the Human Owner wants non-default behavior.
7. Integration mode: Foldered Control Mode or Root Control Mode.
8. Update method for `AI_Development_System/`: vendor copy, git subtree or submodule.
9. Whether to create `OWNER_PLAN.md` immediately or leave it as an empty owner-input placeholder.
10. Whether the repository is empty or already contains application code.
11. Whether local rules should be stricter than the global system defaults.

If the Human Owner has already provided these answers, do not ask again.

## Bootstrap for Empty Repositories

For an empty or new repository in Foldered Control Mode:

1. Add or copy `AI_Development_System/` from upstream.
2. Create root `AGENTS.md` from `templates/foldered/AGENTS.root.md`.
3. Create `AI_PROJECT/` from `templates/foldered/AI_PROJECT/`.
4. Fill templates with project name, target app directory, language, operation profile defaults and default verification mode.
5. Initialize `AI_PROJECT/PROJECT_OPERATION_PROFILE.md` with surface-level operating defaults.
6. Record the first planning state in `AI_PROJECT/CODEX_PLAN.md`.
7. Set `AI_PROJECT/CODEX_CURRENT.md` to `status: idle` unless a task is explicitly approved.
8. Initialize `AI_PROJECT/OWNER_PLAN.md` as an owner-input roadmap placeholder unless the Human Owner opts out.
9. Initialize `AI_PROJECT/CODEX_TASKS.md` with a small backlog or `No tasks approved yet`.
10. Initialize `AI_PROJECT/CODEX_SESSION_LOG.md` with a bootstrap entry.
11. Create `AI_PROJECT/AI_DEV_SYSTEM_VERSION.md` with source branch, version, commit when known and update method.
12. Stop and ask the Human Owner to approve the initialized control layer.

## Bootstrap for Existing Repositories

For an existing repository with application code:

1. Inspect the repository structure only enough to identify the target app directory and existing control files.
2. Do not rewrite, reformat, move or refactor application code.
3. Add or update root `AGENTS.md` as a thin router.
4. Add or refresh `AI_Development_System/` according to the chosen update method.
5. Create `AI_PROJECT/` if missing.
6. Create missing control files or propose updates to stale ones.
7. Preserve existing project-specific instructions unless they conflict with system safety rules.
8. Record target app directory explicitly in `AI_PROJECT/PROJECT_GOAL.md`.
9. Record default verification mode in `AI_PROJECT/docs/verification-policy.md`.
10. Record surface-level operating defaults in `AI_PROJECT/PROJECT_OPERATION_PROFILE.md`.
11. Stop before any app implementation work.

## Files to Create

Default Foldered Control Mode bootstrap creates:

```text
AGENTS.md
AI_Development_System/
AI_PROJECT/AGENTS.md
AI_PROJECT/PROJECT_OPERATION_PROFILE.md
AI_PROJECT/PROJECT_GOAL.md
AI_PROJECT/OWNER_PLAN.md
AI_PROJECT/CODEX_COMMANDS.md
AI_PROJECT/CODEX_WORKFLOW.md
AI_PROJECT/CODEX_PLAN.md
AI_PROJECT/CODEX_CURRENT.md
AI_PROJECT/CODEX_TASKS.md
AI_PROJECT/CODEX_SESSION_LOG.md
AI_PROJECT/PROMPTS.md
AI_PROJECT/AGENT_PLAN.md
AI_PROJECT/AGENT_TASKS.md
AI_PROJECT/AGENT_ASSIGNMENTS.md
AI_PROJECT/AGENT_LOCKS.md
AI_PROJECT/AGENT_RESULTS.md
AI_PROJECT/AGENT_METRICS.md
AI_PROJECT/AI_DEV_SYSTEM_VERSION.md
AI_PROJECT/docs/verification-policy.md
```

Root Control Mode may create equivalent files directly in the project root.

## Install Commands

Vendor copy install:

```bash
git clone --depth 1 --branch ai-development-system https://github.com/nikitoys/AI_Development_System.git AI_Development_System
rm -rf AI_Development_System/.git
mkdir -p AI_PROJECT
cp -R AI_Development_System/ai-system/templates/foldered/AI_PROJECT/. AI_PROJECT/
cp AI_Development_System/ai-system/templates/foldered/AGENTS.root.md AGENTS.md
```

## Minimal Bootstrap Helper

AI_Development_System includes a small local helper for Foldered Control Mode:

```bash
python3 scripts/foldered-control-mvp.py bootstrap --project-root /path/to/project
```

The helper runs in dry-run mode by default. It reports which control files would be created and whether unresolved placeholders remain.

To apply the bootstrap control-layer files explicitly:

```bash
python3 scripts/foldered-control-mvp.py bootstrap \
  --project-root /path/to/project \
  --project-name "My Project" \
  --target-app-directory app \
  --owner-language English \
  --verification-mode FAST \
  --apply
```

This helper only creates or reports foldered control files:

```text
AGENTS.md
AI_PROJECT/
```

The helper includes project-local agent planning templates under `AI_PROJECT/`, but it does not generate Agent Work Packages automatically and does not authorize execution, parallel execution, automatic merge or automatic acceptance.

It does not clone upstream, create packages, manage releases, update git subtree state or modify application code.

Git subtree install:

```bash
git subtree add \
  --prefix=AI_Development_System \
  https://github.com/nikitoys/AI_Development_System.git \
  ai-development-system \
  --squash
mkdir -p AI_PROJECT
cp -R AI_Development_System/ai-system/templates/foldered/AI_PROJECT/. AI_PROJECT/
cp AI_Development_System/ai-system/templates/foldered/AGENTS.root.md AGENTS.md
```

## Default Verification Mode

Default verification mode should normally be:

```text
FAST
```

A stronger default may be selected only when the Human Owner explicitly asks for it or the project context requires it.

Bootstrap must not silently select `STANDARD`, `FULL`, `RELEASE`, browser QA or visual QA as the default.

## Approval Stop Points

Bootstrap must stop for Human Owner approval when:

- required project facts are missing;
- target app directory is ambiguous;
- existing local instructions conflict with global system rules;
- bootstrap would modify application files;
- verification mode stronger than `FAST` is proposed by the AI;
- existing control files would be replaced rather than minimally updated;
- update method for `AI_Development_System/` is unclear.

## Result Format

A bootstrap result should report:

```text
Status:
Integration Mode:
Update Method:
Created Files:
Updated Files:
Target App Directory:
Default Verification Mode:
Project Operation Profile:
Application Code Modified: yes/no
Open Questions:
Next Required Human Owner Decision:
```

## Boundary Rules

Bootstrap may create or update project control files.

Bootstrap may create or refresh `AI_Development_System/` only as the reusable system copy.

Bootstrap must not modify application code without explicit approval.

Bootstrap must not start implementation immediately after creating control files.

Bootstrap must not treat `OWNER_PLAN.md` as executable scope. Owner plan items must first be converted into approved task records with scope, allowed files, verification mode and acceptance criteria.

Bootstrap must not treat agent planning or assignment files as executable scope. Agent planning and assignment records must first be converted into approved bounded task or prompt packages.

Bootstrap must not mark a project ready for Codex execution until the Human Owner approves the local control layer or approves a specific task.

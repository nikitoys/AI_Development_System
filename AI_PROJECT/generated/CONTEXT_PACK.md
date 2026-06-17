<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/docs.json + AI_PROJECT/state/tasks.json -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-010 P2 Integrate Context Pack into codexctl prompt generation Allow codexctl.py to include a validated Context Pack in generated Codex prompt packages. Extend codexctl.py so CODEX_PROMPT.md can include a read-only retrieved context section produced by contextctl.py. The Context Pack must help Codex read the right source documents but must not expand task scope, allowed files or acceptance criteria. scripts/codexctl.py / AI_PROJECT/generated/CODEX_PROMPT.md codexctl can optionally include a validated read-only Context Pack in generated prompt packages. Inspect scripts/codexctl.py and scripts/contextctl.py. Add explicit context-pack integration option to codexctl.py, using supported CLI design. Validate context pack existence and freshness before including it. Include context pack path/hash/source metadata in CODEX_PROMPT.md. Add prompt rules stating that retrieved context is read-only and does not expand allowed files or task scope. Add clear errors for missing, stale or invalid context pack. Update prompt package documentation if needed. Add smoke/validation coverage. Do not implement vector search. Do not change task lifecycle rules. Do not make codexctl.py responsible for document indexing. Do not allow retrieved context to override task fields. Do not manually edit generated CODEX_PROMPT.md. scripts/codexctl.py scripts/contextctl.py only if needed for compatibility fixes scripts/smoke-context-control.py scripts/smoke-project-control.py ai-system/project-control/06-prompt-package-spec.md ai-system/project-control/08-usage-guide.md AI_PROJECT/generated/CODEX_PROMPT.md only through codexctl.py AI_PROJECT/generated/CONTEXT_PACK.md only through contextctl.py AI_PROJECT/events/codex-events.jsonl only through codexctl.py AI_PROJECT/events/context-events.jsonl only through contextctl.py codexctl can build a prompt package with an explicit context pack. codexctl fails clearly if the context pack is missing, stale or invalid. Generated CODEX_PROMPT.md records context pack path/hash and source metadata. Prompt explicitly states that retrieved context is read-only. Prompt explicitly states that context does not expand allowed files, scope or acceptance criteria. codexctl remains able to build prompts without context pack when requested. Required validation/smoke commands pass or blockers are reported. Report new codexctl options, failure modes, generated prompt changes and compatibility with existing prompt generation.","schema_version":1,"task_id":"TASK-010"} -->

# Context Pack

This generated Context Pack is derived output only. It is not source of truth.
It does not expand task scope, allowed files, out-of-scope items, or acceptance criteria.

Mode: `task`
Task ID: `TASK-010`
Explicit query: `false`
Limit: `8`
Docs revision: `18`
Tasks revision: `57`

## Query

```text
TASK-010 P2 Integrate Context Pack into codexctl prompt generation Allow codexctl.py to include a validated Context Pack in generated Codex prompt packages. Extend codexctl.py so CODEX_PROMPT.md can include a read-only retrieved context section produced by contextctl.py. The Context Pack must help Codex read the right source documents but must not expand task scope, allowed files or acceptance criteria. scripts/codexctl.py / AI_PROJECT/generated/CODEX_PROMPT.md codexctl can optionally include a validated read-only Context Pack in generated prompt packages. Inspect scripts/codexctl.py and scripts/contextctl.py. Add explicit context-pack integration option to codexctl.py, using supported CLI design. Validate context pack existence and freshness before including it. Include context pack path/hash/source metadata in CODEX_PROMPT.md. Add prompt rules stating that retrieved context is read-only and does not expand allowed files or task scope. Add clear errors for missing, stale or invalid context pack. Update prompt package documentation if needed. Add smoke/validation coverage. Do not implement vector search. Do not change task lifecycle rules. Do not make codexctl.py responsible for document indexing. Do not allow retrieved context to override task fields. Do not manually edit generated CODEX_PROMPT.md. scripts/codexctl.py scripts/contextctl.py only if needed for compatibility fixes scripts/smoke-context-control.py scripts/smoke-project-control.py ai-system/project-control/06-prompt-package-spec.md ai-system/project-control/08-usage-guide.md AI_PROJECT/generated/CODEX_PROMPT.md only through codexctl.py AI_PROJECT/generated/CONTEXT_PACK.md only through contextctl.py AI_PROJECT/events/codex-events.jsonl only through codexctl.py AI_PROJECT/events/context-events.jsonl only through contextctl.py codexctl can build a prompt package with an explicit context pack. codexctl fails clearly if the context pack is missing, stale or invalid. Generated CODEX_PROMPT.md records context pack path/hash and source metadata. Prompt explicitly states that retrieved context is read-only. Prompt explicitly states that context does not expand allowed files, scope or acceptance criteria. codexctl remains able to build prompts without context pack when requested. Required validation/smoke commands pass or blockers are reported. Report new codexctl options, failure modes, generated prompt changes and compatibility with existing prompt generation.
```

## Task Boundary Snapshot

Task: `TASK-010` - P2 Integrate Context Pack into codexctl prompt generation
Status: `ready`

Scope:
- Inspect scripts/codexctl.py and scripts/contextctl.py.
- Add explicit context-pack integration option to codexctl.py, using supported CLI design.
- Validate context pack existence and freshness before including it.
- Include context pack path/hash/source metadata in CODEX_PROMPT.md.
- Add prompt rules stating that retrieved context is read-only and does not expand allowed files or task scope.
- Add clear errors for missing, stale or invalid context pack.
- Update prompt package documentation if needed.
- Add smoke/validation coverage.

Allowed Files:
- scripts/codexctl.py
- scripts/contextctl.py only if needed for compatibility fixes
- scripts/smoke-context-control.py
- scripts/smoke-project-control.py
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/project-control/08-usage-guide.md
- AI_PROJECT/generated/CODEX_PROMPT.md only through codexctl.py
- AI_PROJECT/generated/CONTEXT_PACK.md only through contextctl.py
- AI_PROJECT/events/codex-events.jsonl only through codexctl.py
- AI_PROJECT/events/context-events.jsonl only through contextctl.py

Acceptance Criteria:
- codexctl can build a prompt package with an explicit context pack.
- codexctl fails clearly if the context pack is missing, stale or invalid.
- Generated CODEX_PROMPT.md records context pack path/hash and source metadata.
- Prompt explicitly states that retrieved context is read-only.
- Prompt explicitly states that context does not expand allowed files, scope or acceptance criteria.
- codexctl remains able to build prompts without context pack when requested.
- Required validation/smoke commands pass or blockers are reported.

## Index Summary

Indexed source documents: `10`
Indexed chunks: `890`
Excluded registered sources: `129`
Selected chunks: `8`

Default exclusion policy: generated, inactive, archived, deprecated, template, and example documents are excluded unless explicitly allowed.

## Selected Sources

| Score | Source | Heading | Lines | Content hash | Chunk hash | Reasons |
| ---: | --- | --- | --- | --- | --- | --- |
| 241 | `ai-system/project-control/04-command-catalog.md` | Project Control Command Catalog > Self-Hosted Command Boundary | 64-116 | `a1985ca2f321` | `b755c971df05` | metadata token match: ai-system, md, project-control; content token match: a, acceptance, ai-system, ai_project, allowed, and, are, build |
| 229 | `ai-system/skills/README.md` | Skills Layer Roadmap > Existing Useful Skills | 34-43 | `dbf637225bec` | `758bde12e28c` | heading token match: existing; metadata token match: ai-system, existing, md; content token match: a, acceptance, add, ai_project, allow, allowed, and, before |
| 199 | `ai-system/skills/README.md` | Skills Layer Roadmap > Recommended Skills To Create | 80-92 | `dbf637225bec` | `eef80c572381` | heading token match: to; metadata token match: ai-system, md, to; content token match: a, acceptance, allowed, and, before, can, changes, cli |
| 178 | `ai-system/project-control/06-prompt-package-spec.md` | 14. Context Budget Rules > Context Pack Boundary | 751-775 | `4b4fd2e79be3` | `feaa321dd2dd` | heading token match: context, pack, rules; metadata token match: 06-prompt-package-spec, ai-system, context, md, pack, package, project-control, prompt; content token match: a, acceptance, add, allowed, and, build, but, by |
| 174 | `ai-system/project-control/03-state-model.md` | Project Control State Model > Context Control State | 104-125 | `b69e6c6ad9ac` | `0cd80bdf0d55` | heading token match: context; metadata token match: ai-system, context, md, project-control; content token match: a, acceptance, ai_project, allowed, and, are, by, context |
| 156 | `ai-system/project-control/06-prompt-package-spec.md` | 12. Prompt Package Template | 555-624 | `4b4fd2e79be3` | `0bbeea588055` | heading token match: package, prompt; metadata token match: 06-prompt-package-spec, ai-system, md, package, project-control, prompt; content token match: acceptance, ai_project, allowed, and, build, by, change, cli |
| 133 | `ai-system/project-control/07-validation-and-tests.md` | 5. Happy Path Test > 5.3 Commands | 395-442 | `035f37bb15d8` | `1e0a62325f1b` | heading token match: commands, path; metadata token match: ai-system, and, commands, md, path, project-control, validation; content token match: a, acceptance, ai_project, are, build, changes, cli, codex_prompt |
| 124 | `ai-system/project-control/06-prompt-package-spec.md` | 17. Relationship To taskctl.py | 816-837 | `4b4fd2e79be3` | `2d16cd4388c9` | heading token match: py, to; metadata token match: 06-prompt-package-spec, ai-system, md, package, project-control, prompt, py, to; content token match: a, and, before, build, but, by, codex, context |

## Selected Context

### 1. `ai-system/project-control/04-command-catalog.md`

Title: Project Control Command Catalog
Status: `active`  Type: `reference`
Heading: Project Control Command Catalog > Self-Hosted Command Boundary
Lines: `64-116`
Score: `241`
Content hash: `a1985ca2f3219254917601872017052dcfc6ae74f1f636fa6fdbe6a6a3227d32`
Chunk hash: `b755c971df05cf7e6b08835383033a087a162359ce3241ab86018beb96506a9d`
Reasons: metadata token match: ai-system, md, project-control; content token match: a, acceptance, ai-system, ai_project, allowed, and, are, build

```text
## Self-Hosted Command Boundary

AI_Development_System now uses root `/AI_PROJECT` as its own self-hosted Project Control Layer. All protected state, event and generated files in that directory must be changed only through approved CLI gateways.

Current domain commands include:

```bash
python scripts/planctl.py ...
python scripts/taskctl.py ...
python scripts/docctl.py ...
python scripts/evolutionctl.py ...
python scripts/contextctl.py ...
```

Current documentation-control commands include:

```bash
python scripts/docctl.py init
python scripts/docctl.py scan --scope ai-system
python scripts/docctl.py scan --scope root
python scripts/docctl.py scan --scope skills
python scripts/docctl.py scan --scope all
python scripts/docctl.py doc register --path <path> --title <title> --type <type> --status <status>
python scripts/docctl.py doc status <path> --to <status>
python scripts/docctl.py doc mark-reviewed <path> --note <text>
python scripts/docctl.py validate
python scripts/docctl.py render
python scripts/docctl.py check-generated
python scripts/docctl.py audit --last 20
```

`docctl.py` owns `AI_PROJECT/state/docs.json`, `AI_PROJECT/events/doc-events.jsonl`, `AI_PROJECT/generated/DOCS_INDEX.md` and `AI_PROJECT/generated/DOCS_GAPS.md`. It records current document content hashes, reviewed content hashes and declared-status metadata.

[...truncated by contextctl...]
```

### 2. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Existing Useful Skills
Lines: `34-43`
Score: `229`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `758bde12e28c5003117d6958a636e205773bec7f8a29c54b5cb4e41ac103355a`
Reasons: heading token match: existing; metadata token match: ai-system, existing, md; content token match: a, acceptance, add, ai_project, allow, allowed, and, before

```text
## Existing Useful Skills

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Project Control Gateway Skill | Route plan, task, documentation and evolution work through the controlled CLI gateway instead of manual state edits. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Inspect state through CLI, choose allowed commands, run validation and render commands, report unsupported operations. | Manually edit `AI_PROJECT/state/**`, `AI_PROJECT/events/**` or `AI_PROJECT/generated/**`; invent lifecycle states or commands; execute Initiative or Epic directly. |
| Clarification Gate Skill | Teach Codex and subagents when to inspect first, proceed with safe assumptions, or stop for Human Owner blocker questions. | `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Classify blockers, group owner questions, identify safe defaults, preserve task and approval boundaries. | Use questions to avoid normal inspection; ask for approval after every small step; self-approve accepted, approved, active or done states. |
| Documentation Navigation Skill | Route Codex and subagents to the minimal correct documentation and project-control read set before planning, editing, reviewing or executing AI_Development_System work.

[...truncated by contextctl...]
```

### 3. `ai-system/skills/README.md`

Title: Skills Layer Roadmap
Status: `active`  Type: `guide`
Heading: Skills Layer Roadmap > Recommended Skills To Create
Lines: `80-92`
Score: `199`
Content hash: `dbf637225bec85ce3cc9b8456c3714c12e4590eb0c7f3402506c05fa751795f6`
Chunk hash: `eef80c572381162a83f631b204ebabb9a4355ca6f9f2cabf4415075c34d8b797`
Reasons: heading token match: to; metadata token match: ai-system, md, to; content token match: a, acceptance, allowed, and, before, can, changes, cli

```text
## Recommended Skills To Create

| Skill | Purpose | Related CLI | Priority | Allowed Actions | Forbidden Actions |
| --- | --- | --- | --- | --- | --- |
| Documentation Control Skill | Guide documentation registration, status changes, generated indexes and documentation validation. | `docctl.py` | P0 | Register documents, set draft/review status, render/check generated docs, explain documentation lifecycle. | Mark documents active without Human Owner approval; manually edit `docs.json`, doc events or generated doc indexes. |
| Protected Files Skill | Keep agents inside the protected-files boundary and detect unsafe project-control edits. | `check-protected-project-files.py`, `planctl.py`, `taskctl.py`, `docctl.py`, `evolutionctl.py` | P0 | Explain protected paths, run protected-files checks, route repairs through CLIs. | Edit protected state/events/generated files manually; use ad hoc scripts to mutate protected files; hide drift. |
| Review Gate Skill | Guide review intake before a Task can be accepted or closed. | `taskctl.py`; future review control CLI if approved | P1 | Check scope, allowed files, acceptance criteria, validation output and review status; recommend APPROVED, REWORK, REJECTED or DEFERRED. | Self-approve work; mark a Task done without the required approval path; ignore Critical or Major findings. |

[...truncated by contextctl...]
```

### 4. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 14. Context Budget Rules > Context Pack Boundary
Lines: `751-775`
Score: `178`
Content hash: `4b4fd2e79be39e8958eef6fadadbf60c31b72bf0a22fad4f5ce222db7fa7fd7a`
Chunk hash: `feaa321dd2dd51d7051c8766980624700352ab9cbbe40b25b42864d2cf593e4f`
Reasons: heading token match: context, pack, rules; metadata token match: 06-prompt-package-spec, ai-system, context, md, pack, package, project-control, prompt; content token match: a, acceptance, add, allowed, and, build, but, by

```text
## Context Pack Boundary

When Codex needs additional documentation context, use `contextctl.py` to generate a bounded Context Pack:

```bash
python scripts/contextctl.py pack build --task <TASK_ID> --write
```

Context Pack output is derived retrieval context. It may help Codex decide which source sections to inspect, but it must not change the Prompt Package contract.

Context Pack must not:

```text
- expand Task scope;
- add allowed files;
- add acceptance criteria;
- override out-of-scope items;
- replace source documents or Task state;
- include full tasks.json, full docs.json or full audit logs by default.
```

The default retrieval policy excludes generated files, inactive documents, archived documents, deprecated documents, templates and examples unless explicitly allowed by a `contextctl.py` include flag.

---
```

### 5. `ai-system/project-control/03-state-model.md`

Title: Project Control State Model
Status: `active`  Type: `reference`
Heading: Project Control State Model > Context Control State
Lines: `104-125`
Score: `174`
Content hash: `b69e6c6ad9acbaf0bb398fd6ad729bb07290b6138e99a3535701e57c750a244d`
Chunk hash: `0cd80bdf0d55e5284fa6355477f50005896398136bf33b7e1a181718f309f8b4`
Reasons: heading token match: context; metadata token match: ai-system, context, md, project-control; content token match: a, acceptance, ai_project, allowed, and, are, by, context

```text
## Context Control State

Context control uses the state/events/generated model without adding a new source-of-truth state file:

```text
AI_PROJECT/state/docs.json
AI_PROJECT/state/tasks.json
AI_PROJECT/events/context-events.jsonl
AI_PROJECT/generated/CONTEXT_PACK.md
AI_PROJECT/generated/CONTEXT_STATUS.md
```

`scripts/contextctl.py` builds a deterministic derived index in memory from registered documents in `docs.json` and optional Task context from `tasks.json`.

The derived index and Context Pack are not source of truth. They must not expand Task scope, allowed files, out-of-scope items or acceptance criteria. If retrieved context conflicts with the Task or source documents, the Task and source documents remain authoritative.

By default, context control indexes registered active source documents only. It excludes generated files, inactive documents, archived documents, deprecated documents, templates and examples unless the operator explicitly enables the relevant include flag.

`CONTEXT_PACK.md` includes selected source paths, headings, line ranges, source content hashes, chunk hashes, deterministic keyword scores and selection reasons. `CONTEXT_STATUS.md` summarizes the current generated pack, selected paths and exclusion reasons. Both files are generated output and must be regenerated through `contextctl.py`.

---
```

### 6. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 12. Prompt Package Template
Lines: `555-624`
Score: `156`
Content hash: `4b4fd2e79be39e8958eef6fadadbf60c31b72bf0a22fad4f5ce222db7fa7fd7a`
Chunk hash: `0bbeea58805544e5602d01cadc927ceab81c2f4bc3886e3f733dba5efcd568a4`
Reasons: heading token match: package, prompt; metadata token match: 06-prompt-package-spec, ai-system, md, package, project-control, prompt; content token match: acceptance, ai_project, allowed, and, build, by, change, cli

```text
# 12. Prompt Package Template

Canonical structure:

````text id="7p2uqx"
[SYSTEM]

Active Role: <active_role>
Active Stage: <active_stage>
Active Document: <active_document>
Expected Result: <expected_result>

Repository: current repository
Task ID: <task_id>
Task Title: <task_title>
Task Status: <task_status>
Verification Mode: <verification_mode>

Initiative: <initiative_id> — <initiative_title>
Epic: <epic_id> — <epic_title>

Context:
<summary>

Details:
<description>

Scope:
- <scope item>

Out of Scope:
- <out of scope item>

Allowed Files:
- <allowed file>

Acceptance Criteria:
- <acceptance criterion>

Review Instructions:
- <review instruction>

Execution Rules:
- Do not edit AI_PROJECT/state/*.json manually.
- Do not edit AI_PROJECT/events/*.jsonl manually.
- Do not edit AI_PROJECT/generated/*.md manually unless explicitly instructed; prefer CLI render/build commands.
- Stay within Allowed Files and Scope.
- If task state must change, report the required taskctl command instead of editing state by hand.
- At the end, report changed files, checks run, result, and unresolved risks.

Suggested lifecycle commands:
```bash
python scripts/taskctl.py task transition <TASK_ID> --to in_progress
python scripts/taskctl.py task transition <TASK_ID> --to in_review
python scripts/taskctl.py validate
````

Final Report:

* Changed files:
* Commands run:
* Validation result:

[...truncated by contextctl...]
```

### 7. `ai-system/project-control/07-validation-and-tests.md`

Title: Project Control Validation and Tests
Status: `active`  Type: `process`
Heading: 5. Happy Path Test > 5.3 Commands
Lines: `395-442`
Score: `133`
Content hash: `035f37bb15d8f601aff97abc4f3378961d0524d7a96fae5f03239239e9aee12c`
Chunk hash: `1e0a62325f1be7605fee794f04ca79d11e9ce2814319de415744ba4c9868be25`
Reasons: heading token match: commands, path; metadata token match: ai-system, and, commands, md, path, project-control, validation; content token match: a, acceptance, ai_project, are, build, changes, cli, codex_prompt

```text
## 5.3 Commands

```bash id="pt0ts2"
ROOT="$(mktemp -d)"

python scripts/planctl.py --root "$ROOT" init \
  --project-name "AI Development System Smoke Test"

python scripts/planctl.py --root "$ROOT" idea set \
  --text "Create a controlled AI-assisted development system."

python scripts/planctl.py --root "$ROOT" goal set \
  --text "Validate Project Control Gateway."

python scripts/planctl.py --root "$ROOT" strategy set-summary \
  --text "Use CLI commands as the only mutation path."

python scripts/planctl.py --root "$ROOT" initiative create \
  --title "Project Control Gateway" \
  --summary "Validate strict project control through CLI."

python scripts/planctl.py --root "$ROOT" epic create \
  --initiative INIT-001 \
  --title "Task Control CLI" \
  --summary "Validate executable task control."

python scripts/taskctl.py --root "$ROOT" init

python scripts/taskctl.py --root "$ROOT" task create \
  --epic EPIC-001 \
  --title "Smoke Task" \
  --summary "Validate end-to-end task workflow." \
  --scope "Create generated prompt package" \
  --out-of-scope "No application code changes" \
  --allowed-file "AI_PROJECT/generated/CODEX_PROMPT.md" \
  --acceptance "Task validation passes" \
  --acceptance "Generated task files are up to date" \
  --verification-mode standard

python scripts/taskctl.py --root "$ROOT" current set TASK-001

[...truncated by contextctl...]
```

### 8. `ai-system/project-control/06-prompt-package-spec.md`

Title: Project Control Prompt Package Specification
Status: `active`  Type: `reference`
Heading: 17. Relationship To taskctl.py
Lines: `816-837`
Score: `124`
Content hash: `4b4fd2e79be39e8958eef6fadadbf60c31b72bf0a22fad4f5ce222db7fa7fd7a`
Chunk hash: `2d16cd4388c9aeb0923a869e717230444322c4ff27ae1dce21e95a3e6662fa3a`
Reasons: heading token match: py, to; metadata token match: 06-prompt-package-spec, ai-system, md, package, project-control, prompt, py, to; content token match: a, and, before, build, but, by, codex, context

```text
# 17. Relationship To taskctl.py

Prompt Package is built by `taskctl.py`.

`taskctl.py` owns:

```text id="d2esmn"
Task state
Current Task
Task generated Markdown
Codex Prompt Package
Task audit events
```

Prompt Package build must not bypass task validation.

Before building the package, task state must be valid.

`contextctl.py` may read Task state to derive a search query for a Context Pack, but it does not mutate Task state and does not make retrieved context executable scope.

---
```

## Excluded Source Summary

- inactive document excluded by default: `88`
  - `.agents/skills/agent-delegation/SKILL.md`
  - `.agents/skills/clarification-gate/SKILL.md`
  - `.agents/skills/documentation-navigation/SKILL.md`
  - `.agents/skills/project-control-gateway/SKILL.md`
  - `AGENTS.md`
  - `README.md`
  - `README.ru.md`
  - `ai-system/README.md`
  - `ai-system/agent-result-intake.md`
  - `ai-system/agent-work-package.md`
  - `ai-system/aicp-language-policy.md`
  - `ai-system/aicp-security-privacy-policy.md`
  - `ai-system/aicp-work-item-hierarchy.md`
  - `ai-system/change-lifecycle.md`
  - `ai-system/change-process.md`
  - `ai-system/codex-lifecycle.md`
  - `ai-system/decision-lifecycle.md`
  - `ai-system/decision-process.md`
  - `ai-system/document-lifecycle.md`
  - `ai-system/evolution/README.md`
- template document excluded by default: `41`
  - `ai-system/document-templates.md`
  - `ai-system/evolution/templates/evolution-task.md`
  - `ai-system/evolution/templates/owner-evolution-plan.md`
  - `ai-system/evolution/templates/system-change-proposal.md`
  - `ai-system/templates/agent-worker-prompt.md`
  - `ai-system/templates/foldered/AGENTS.root.md`
  - `ai-system/templates/foldered/AI_PROJECT/AGENTS.md`
  - `ai-system/templates/foldered/AI_PROJECT/AGENT_ASSIGNMENTS.md`
  - `ai-system/templates/foldered/AI_PROJECT/AGENT_LOCKS.md`
  - `ai-system/templates/foldered/AI_PROJECT/AGENT_METRICS.md`
  - `ai-system/templates/foldered/AI_PROJECT/AGENT_PLAN.md`
  - `ai-system/templates/foldered/AI_PROJECT/AGENT_RESULTS.md`
  - `ai-system/templates/foldered/AI_PROJECT/AGENT_TASKS.md`
  - `ai-system/templates/foldered/AI_PROJECT/AI_DEV_SYSTEM_VERSION.md`
  - `ai-system/templates/foldered/AI_PROJECT/CODEX_COMMANDS.md`
  - `ai-system/templates/foldered/AI_PROJECT/CODEX_CURRENT.md`
  - `ai-system/templates/foldered/AI_PROJECT/CODEX_PLAN.md`
  - `ai-system/templates/foldered/AI_PROJECT/CODEX_SESSION_LOG.md`
  - `ai-system/templates/foldered/AI_PROJECT/CODEX_TASKS.md`
  - `ai-system/templates/foldered/AI_PROJECT/CODEX_WORKFLOW.md`

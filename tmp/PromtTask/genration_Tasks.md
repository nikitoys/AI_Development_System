# Executable Task Generation Rule v1

Use this as an instruction file when asking GPT to generate executable task draft JSON for the AI Development System.

The goal is to generate tasks that can later produce a compact `CODEX_PROMPT.md` without Codex inventing scope, editable files, acceptance criteria, or safety boundaries.

Return **JSON only**. Do not return Markdown. Do not add comments.

---

## 1. Output Shape

Return exactly this top-level shape:

```json
{
  "split_recommended": false,
  "reason": "",
  "task": {
    "epic": "",
    "title": "",
    "summary": "",
    "description": "",
    "priority": 1,
    "verification_mode": "standard",
    "scope": [],
    "out_of_scope": [],
    "allowed_files": [],
    "acceptance_criteria": [],
    "review_instructions": [],
    "notes": [],
    "depends_on": []
  },
  "proposed_splits": []
}
```

If the requested work is too broad, set `split_recommended` to `true`, explain why in `reason`, leave `task` as the best parent task draft, and put smaller executable task drafts into `proposed_splits`.

Each item in `proposed_splits` must use the same task fields as `task`, without nested `split_recommended`.

---

## 2. Required Task Fields

### `epic`

Use the provided Epic ID.
If no Epic ID is provided, leave it empty and make the missing Epic clear in `reason`.

### `title`

Required.
Short executable task title.
Do not write a vague planning title.

Good title:
`Add compact Codex prompt template`

Bad title:
`Improve prompts`

### `summary`

Required.
One sentence.
This becomes the prompt Objective.
It must state the concrete expected result.

### `description`

Optional.
Keep short.
Use only if `summary` and `scope` are not enough.

### `priority`

Default: `1`.
Use an integer.

### `verification_mode`

Required.
Allowed values:

```text
none
manual
light
standard
strict
```

Default: `standard`.
Use `strict` for code, pipeline, state, security, or prompt-generation behavior changes.

### `scope`

Required.
Concrete actions only.

Rules:

```text
minimum: 1 item
preferred: 2-4 items
maximum: 7 items
```

If more than 7 scope items are needed, recommend splitting.

### `out_of_scope`

Required logically.
If not provided by the user, generate compact defaults:

```text
Do not change behavior unrelated to this task.
Do not refactor unrelated code.
Do not edit protected project-control files manually.
```

Keep this section short.

### `allowed_files`

Required for write tasks.
Contains only files the executor may edit.

Rules:

```text
preferred: 1-8 editable files
warning: more than 8 editable files
split recommendation: more than 10-12 editable files
```

For read-only tasks, use an empty array and state read-only intent in `scope` and `acceptance_criteria`.

Do not put read-only documentation references here.
Context references are generated separately by Context Pack.

### `acceptance_criteria`

Required.
Testable or reviewable criteria only.

Rules:

```text
minimum: 3 items
maximum: 7 items
```

Criteria should cover:

```text
main expected result
important behavior that must not break
how completion can be verified
```

Do not split criteria into separate fields.
Use one flat list.

---

## 3. Optional Task Fields

### `review_instructions`

Optional.
Use only short review hints.
Do not duplicate all acceptance criteria.

### `notes`

Optional.
Use only relevant constraints, assumptions, or owner notes.
Do not put long analysis here.

### `depends_on`

Optional.
List task IDs or task refs that must be completed first.
Use an empty array if there are no dependencies.

---

## 4. Do Not Generate These Fields Yet

Do not include these fields in the task JSON for MVP:

```text
profile
role
context_refs
context_hash
docs_revision
tasks_revision
execution_rules
missing_info_policy
final_report_format
executor_prompt
verifier_prompt
compiled_contract
execution_steps
verification_checks
```

Reason:

```text
profile is selected by prompt build command;
role/final report/execution rules/missing info come from compiler policy;
context refs/hash/revisions come from Context Pack;
execution_steps and verification_checks are future task-schema fields.
```

---

## 5. Split Recommendation Rules

Set `split_recommended` to `true` if any condition is true:

```text
scope has more than 7 items;
allowed_files has more than 10-12 editable files;
acceptance_criteria has more than 7 items;
the task mixes unrelated artifacts;
the task mixes implementation, architecture, documentation, tests, and review in one unit;
the task cannot be verified by one coherent verification path;
the task would need more than 8 execution steps.
```

Main decomposition rule:

```text
One executable task = one bounded, reviewable change with clear editable files and clear acceptance criteria.
```

Do not split infinitely.
Each proposed split must have standalone value.

---

## 6. Quality Checklist

Before returning JSON, verify:

```text
title is concrete;
summary is one sentence;
scope contains actions;
allowed_files contains only editable files;
acceptance_criteria has 3-7 items;
out_of_scope prevents unrelated work;
verification_mode is valid;
JSON has no comments;
JSON has no Markdown wrapper;
no future fields are included.
```

---

## 7. Prompt Compatibility

The generated task must be sufficient to fill these compact prompt sections:

```text
Metadata: task id/ref/status/revision/verification mode
Objective: task summary
Scope: task scope
Out of Scope: task out_of_scope or defaults
Allowed Files: task allowed_files
Acceptance Criteria: task acceptance_criteria
Verification: task verification_mode plus compiler default check instruction
```

Other prompt sections are not stored in the task:

```text
Role: compiler profile
Context: Context Pack
Execution Rules: compiler policy
Missing Info: compiler policy
Final Report: compiler profile
```

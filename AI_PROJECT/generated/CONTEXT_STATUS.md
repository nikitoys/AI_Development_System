<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-194 Document advisory warning commit behavior Document that local commit uses the same advisory report warning policy as verify, review, and close. Clarify the owner-facing troubleshooting path for COMMIT_REPORT_GATE_NOT_PASS after close succeeds. AI_PROJECT/generated/CODEX_CURRENT.md Task completed according to acceptance criteria Update the pipeline runner SOP to describe report PASS versus policy-accepted advisory WARN behavior through local commit. Clarify that strict mode still blocks report WARN when advisory report warnings are disabled. Add a troubleshooting note for COMMIT_REPORT_GATE_NOT_PASS after close succeeds. Do not change runtime pipeline behavior. Do not refactor unrelated documentation. Do not edit protected project-control files manually. ai-system/project-control/pipeline-runner.md ai-system/project-control/10-owner-quickstart.md Documentation states that advisory report WARN can proceed to local commit only when policy explicitly allows it. Documentation states that report FAIL/BLOCKED and advisory-disabled WARN still block local commit. Documentation explains that COMMIT_REPORT_GATE_NOT_PASS means the commit gate rejected the report gate status. Documentation does not imply that Human Owner approval, machine review, Codex review, or dirty-file gates are bypassed. Review the wording for safety: advisory warnings must not be described as unconditional commit permission.","schema_version":1,"task_id":"TASK-194"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-194`
Limit: `8`
Docs revision: `28`
Tasks revision: `1379`
Indexed source documents: `10`
Indexed chunks: `891`
Selected chunks: `8`
Excluded registered sources: `135`

## Selected Source Paths

- ai-system/agent-delegation.md
- ai-system/project-control/03-state-model.md
- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `94`
- template document excluded by default: `41`

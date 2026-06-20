<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/generated/CONTEXT_PACK.md -->
<!-- Context: {"explicit_query":false,"filters":{"include_archived":false,"include_deprecated":false,"include_examples":false,"include_generated":false,"include_inactive":false,"include_templates":false},"limit":8,"mode":"task","query":"TASK-064 PIPE-13 Pipeline UI Dashboard Add a Web Control Center dashboard for pipeline sessions, queue preview, policy selection, run-next, and run-until-blocker. Expose supervised pipeline operation in the local Web Control Center without weakening confirmation, policy, or lifecycle gates. ai_project_ctl/web/server.py / ai_project_ctl/web/read_model.py Human Owner can inspect and operate supervised pipeline sessions from the local UI with explicit confirmation. Add Pipeline dashboard/page to the Web Control Center. Show policy selector/preset preview, queue selector, queue preview, session status, current step, gates, stop reason, and latest audit entries. Expose Create Session, Run Next, Run Until Blocker, Stop Session, and Refresh Status actions where implemented. Require explicit confirmation for any write/run action. Show action result panel with step status, blockers, changed/generated files, reports, reviews, and next actions. Keep UI local-only and route writes through governed commands/workflows. Add tests for dashboard rendering, confirmation requirements, and action routing. Do not add remote hosting. Do not bypass pipeline policy. Do not auto-start sessions on page load. Do not run arbitrary shell commands from UI. Do not hide blockers or failed gates. ai_project_ctl/web/read_model.py ai_project_ctl/web/server.py ai_project_ctl/web/actions.py ai_project_ctl/pipeline/** if UI integration requires compatible changes ai_project_ctl/core/registry.py if action metadata is needed scripts/aictl.py if routing is needed tests/test_web_control_center.py tests/** ai-system/project-control/** if UI documentation is needed Pipeline dashboard shows sessions, selected policy, queue preview, current step, and stop reason. Run actions require explicit confirmation. UI writes route through governed commands/workflows. Failed gates and blockers are visible. UI remains local-only by default. Tests and project-control validations pass. Verify UI cannot start or continue pipeline silently. Verify all mutations route through governed command paths.","schema_version":1,"task_id":"TASK-064"} -->

# Context Status

Context pack exists: `true`
Mode: `task`
Task ID: `TASK-064`
Limit: `8`
Docs revision: `24`
Tasks revision: `582`
Indexed source documents: `10`
Indexed chunks: `890`
Selected chunks: `8`
Excluded registered sources: `134`

## Selected Source Paths

- ai-system/project-control/03-state-model.md
- ai-system/project-control/04-command-catalog.md
- ai-system/project-control/06-prompt-package-spec.md
- ai-system/skills/README.md

## Exclusion Reasons

- inactive document excluded by default: `93`
- template document excluded by default: `41`

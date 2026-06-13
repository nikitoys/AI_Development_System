# Project Operation Profile — {{PROJECT_NAME}}

Status: Draft

## Purpose

This file defines surface-level operating preferences for AI_Development_System inside this project.

It is for behavior defaults, not product requirements or implementation scope.

## Human Interaction

Human Owner Language: {{HUMAN_OWNER_LANGUAGE}}
Answer Language: {{HUMAN_OWNER_LANGUAGE}}
Answer Detail Level: {{ANSWER_DETAIL_LEVEL}}
Prompt Language: {{PROMPT_LANGUAGE}}

## Verification Defaults

Default Verification Mode: {{DEFAULT_VERIFICATION_MODE}}
Default Verification Budget: {{DEFAULT_VERIFICATION_BUDGET}}
Allowed Slow Checks: {{ALLOWED_SLOW_CHECKS}}
Runtime Tracking: {{RUNTIME_TRACKING}}
Browser Checks: {{BROWSER_CHECKS}}
Visual QA: {{VISUAL_QA}}
Full Checks: explicit request only
Release Checks: explicit request only

## Permissions

Can Modify Application Code: {{CAN_MODIFY_APPLICATION_CODE}}
Can Modify AI_PROJECT: {{CAN_MODIFY_AI_PROJECT}}
Can Modify AI_Development_System: {{CAN_MODIFY_AI_DEVELOPMENT_SYSTEM}}
Can Install Dependencies: {{CAN_INSTALL_DEPENDENCIES}}
Can Commit: {{CAN_COMMIT}}
Can Push / Create PR: {{CAN_PUSH_PR}}

## Project Layout

Target App Directory: {{TARGET_APP_DIRECTORY}}
Project Control Directory: AI_PROJECT/
AI System Directory: AI_Development_System/

Application Code Paths:
- {{TARGET_APP_DIRECTORY}}

Read Only Paths:
- secrets/
- production config

## Review Defaults

Review Required: true
QA Required: when behavior changes or acceptance criteria require it
Blocking Severity: Critical, Major
Advisory Failures: allowed only when reported

## Local Exceptions

None

## Rules

- This profile provides defaults only.
- It does not authorize execution without an approved task or prompt package.
- It may restrict global AI Development System rules, but must not weaken them.
- If this profile conflicts with global safety rules, report the conflict and stop.
- If this profile conflicts with specialized local control files, report project-control drift.

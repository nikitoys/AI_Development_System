# Foldered Project Templates

These templates install AI_Development_System into a concrete project using the recommended foldered architecture.

Default target layout:

```text
/project-root
├── AGENTS.md
├── AI_Development_System/
├── AI_PROJECT/
└── {{TARGET_APP_DIRECTORY}}/
```

Use `AGENTS.root.md` as the project root `AGENTS.md`.

Copy the `AI_PROJECT/` directory into the project root and fill placeholders:

```text
{{PROJECT_NAME}}
{{TARGET_APP_DIRECTORY}}
{{DEFAULT_VERIFICATION_MODE}}
{{HUMAN_OWNER_LANGUAGE}}
{{AI_DEV_SYSTEM_SOURCE}}
{{AI_DEV_SYSTEM_BRANCH}}
{{AI_DEV_SYSTEM_VERSION}}
{{AI_DEV_SYSTEM_COMMIT}}
```

`AI_PROJECT/` is project-local source of truth after bootstrap. Do not overwrite it during upstream system updates.

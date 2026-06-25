<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/pipeline_policy_presets.json -->

# Pipeline Policy Presets

Revision: `2`
Custom presets: `2`

## Built-In Presets

| Name | Immutable | Behavior | Codex Mode | Project Tests | Token Gate | Reviews | Auto Close | Local Commit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `dry_run` | `yes` | `dry-run` | `disabled` | `none` | `no` | `no-machine / no-codex` | `no` | `no` |
| `supervised` | `yes` | `prompt-only` | `build_prompt_only` | `none` | `yes` | `machine / codex` | `no` | `no` |
| `supervised_executable` | `yes` | `executable` | `run_codex` | `none` | `yes` | `machine / codex` | `no` | `no` |
| `supervised_autoclose` | `yes` | `prompt-only / auto-close blocked` | `build_prompt_only` | `none` | `yes` | `machine / codex` | `yes` | `no` |
| `supervised_executable_autoclose` | `yes` | `executable / auto-close needs note` | `run_codex` | `none` | `yes` | `machine / codex` | `yes` | `no` |
| `supervised_local_commit` | `yes` | `prompt-only / auto-close blocked / local-commit blocked` | `build_prompt_only` | `none` | `yes` | `machine / codex` | `yes` | `yes` |
| `supervised_executable_local_commit` | `yes` | `executable / auto-close needs note / local-commit` | `run_codex` | `none` | `yes` | `machine / codex` | `yes` | `yes` |

## Custom Presets

| Name | Updated | Behavior | Codex Mode | Project Tests | Token Gate | Reviews | Auto Close | Local Commit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `supervised_executable_local_commit_1h` | `2026-06-23T14:50:27Z` | `executable / auto-close needs note / local-commit` | `run_codex` | `none` | `yes` | `machine / codex` | `yes` | `yes` |
| `supervised_executable_local_commit_1h_auto_change` | `2026-06-25T07:18:57Z` | `executable / auto-close needs note / local-commit` | `run_codex` | `none` | `yes` | `machine / codex` | `yes` | `yes` |

<!-- GENERATED FILE. DO NOT EDIT MANUALLY. -->
<!-- Source: AI_PROJECT/state/pipeline_policy_presets.json -->

# Pipeline Policy Presets

Revision: `0`
Custom presets: `0`

## Built-In Presets

| Name | Immutable | Behavior | Codex Mode | Token Gate | Reviews | Auto Close | Local Commit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `dry_run` | `yes` | `dry-run` | `disabled` | `no` | `no-machine / no-codex` | `no` | `no` |
| `supervised` | `yes` | `prompt-only` | `build_prompt_only` | `yes` | `machine / codex` | `no` | `no` |
| `supervised_executable` | `yes` | `executable` | `run_codex` | `yes` | `machine / codex` | `no` | `no` |
| `supervised_autoclose` | `yes` | `prompt-only / auto-close blocked` | `build_prompt_only` | `yes` | `machine / codex` | `yes` | `no` |
| `supervised_executable_autoclose` | `yes` | `executable / auto-close needs note` | `run_codex` | `yes` | `machine / codex` | `yes` | `no` |
| `supervised_local_commit` | `yes` | `prompt-only / auto-close blocked / local-commit blocked` | `build_prompt_only` | `yes` | `machine / codex` | `yes` | `yes` |
| `supervised_executable_local_commit` | `yes` | `executable / auto-close needs note / local-commit` | `run_codex` | `yes` | `machine / codex` | `yes` | `yes` |

## Custom Presets

_No custom pipeline policy presets recorded._

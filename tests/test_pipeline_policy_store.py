import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ai_project_ctl.pipeline import (
    CommitMode,
    CommitPolicy,
    policy_preset,
)
from ai_project_ctl.pipeline.policy_store import (
    check_generated,
    delete_policy_preset,
    load_policy_preset,
    pipeline_policy_events_path,
    pipeline_policy_status_path,
    pipeline_policy_store_path,
    read_policy_events,
    render_policy_store,
    save_policy_preset,
    status_payload,
    validate_policy_store,
)


class PipelinePolicyStoreTests(unittest.TestCase):
    def test_save_load_update_delete_custom_policy_preset(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            custom = replace(policy_preset("supervised"), name="owner_supervised")

            created = save_policy_preset("owner_supervised", custom, root=root, actor="tester")

            self.assertTrue(created.ok)
            self.assertEqual(created.data["action"], "created")
            self.assertTrue(pipeline_policy_store_path(root).exists())
            self.assertTrue(pipeline_policy_events_path(root).exists())
            self.assertTrue(pipeline_policy_status_path(root).exists())
            self.assertEqual(load_policy_preset("owner_supervised", root=root), custom)
            self.assertTrue(validate_policy_store(root=root).ok)
            self.assertTrue(check_generated(root=root).ok)

            payload = status_payload(root=root)
            self.assertEqual([item["name"] for item in payload["builtins"]], [
                "dry_run",
                "supervised",
                "supervised_executable",
                "supervised_autoclose",
                "supervised_executable_autoclose",
                "supervised_local_commit",
                "supervised_executable_local_commit",
            ])
            self.assertEqual(
                payload["builtins"][1]["behavior_label"],
                "prompt-only",
            )
            self.assertEqual(
                payload["builtins"][2]["behavior_label"],
                "executable",
            )
            self.assertEqual([item["name"] for item in payload["custom"]], ["owner_supervised"])
            events = read_policy_events(root)
            self.assertEqual(events[0]["command"], "pipeline.policy.save")
            self.assertEqual(events[0]["payload"]["event_type"], "policy_preset.created")

            updated_policy = replace(custom, batch=replace(custom.batch, max_steps=7))
            updated = save_policy_preset("owner_supervised", updated_policy, root=root, actor="tester")

            self.assertTrue(updated.ok)
            self.assertEqual(updated.data["action"], "updated")
            self.assertEqual(load_policy_preset("owner_supervised", root=root), updated_policy)

            deleted = delete_policy_preset("owner_supervised", root=root, actor="tester")

            self.assertTrue(deleted.ok)
            self.assertEqual(deleted.data["action"], "deleted")
            self.assertEqual(len(status_payload(root=root)["custom"]), 0)
            self.assertEqual(
                [event["payload"]["event_type"] for event in read_policy_events(root)],
                [
                    "policy_preset.created",
                    "policy_preset.updated",
                    "policy_preset.deleted",
                ],
            )

    def test_builtin_policy_presets_are_immutable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            save_result = save_policy_preset("dry_run", policy_preset("dry_run"), root=root)
            delete_result = delete_policy_preset("supervised", root=root)

            self.assertFalse(save_result.ok)
            self.assertEqual(save_result.errors[0].code, "POLICY_PRESET_BUILTIN_IMMUTABLE")
            self.assertFalse(delete_result.ok)
            self.assertEqual(delete_result.errors[0].code, "POLICY_PRESET_BUILTIN_IMMUTABLE")
            self.assertFalse(pipeline_policy_store_path(root).exists())

    def test_unsafe_policy_is_rejected_before_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            supervised = policy_preset("supervised")
            unsafe = replace(
                supervised,
                name="unsafe_push",
                commit=CommitPolicy(
                    create_local_commit=True,
                    mode=CommitMode.LOCAL_ONLY,
                    require_commit_readiness=True,
                    allow_push=True,
                    allow_merge=False,
                ),
            )

            result = save_policy_preset("unsafe_push", unsafe, root=root)

            self.assertFalse(result.ok)
            self.assertEqual(result.errors[0].code, "POLICY_PUSH_FORBIDDEN")
            self.assertFalse(pipeline_policy_store_path(root).exists())

    def test_check_generated_detects_pipeline_policies_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            custom = replace(policy_preset("supervised"), name="owner_supervised")
            save_policy_preset("owner_supervised", custom, root=root, actor="tester")

            render_policy_store(root=root)
            self.assertTrue(check_generated(root=root).ok)

            pipeline_policy_status_path(root).write_text("manual drift\n", encoding="utf-8")
            result = check_generated(root=root)

            self.assertFalse(result.ok)
            self.assertEqual(result.errors[0].code, "PIPELINE_POLICIES_OUTDATED")

    def test_invalid_store_state_reports_stable_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = pipeline_policy_store_path(root)
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "revision": 1,
                        "created_at": "2026-06-20T00:00:00Z",
                        "updated_at": "2026-06-20T00:00:00Z",
                        "presets": [
                            {
                                "name": "dry_run",
                                "policy": policy_preset("dry_run").to_dict(),
                                "created_at": "2026-06-20T00:00:00Z",
                                "updated_at": "2026-06-20T00:00:00Z",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = validate_policy_store(root=root)

            self.assertFalse(result.ok)
            self.assertEqual(result.errors[0].code, "POLICY_PRESET_BUILTIN_IMMUTABLE")


if __name__ == "__main__":
    unittest.main()

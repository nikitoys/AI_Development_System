import unittest

from ai_project_ctl.core.ids import (
    IdentityError,
    allocate_numeric_id,
    allocate_uid,
    build_identity_index,
    format_scoped_ref,
)
from ai_project_ctl.core.validation import require_fields


class CoreIdsValidationTests(unittest.TestCase):
    def test_allocate_numeric_id_uses_highest_matching_suffix(self):
        self.assertEqual(
            allocate_numeric_id(["TASK-001", "TASK-009", "OTHER-999"], "TASK"),
            "TASK-010",
        )

    def test_allocate_uid_and_scoped_ref(self):
        self.assertEqual(allocate_uid("tsk_", suffix="abc123"), "tsk_abc123")
        self.assertEqual(format_scoped_ref("CTL", 4), "CTL-04")

    def test_identity_index_resolves_aliases_and_rejects_duplicates(self):
        index = build_identity_index(
            [
                {"id": "TASK-001", "uid": "tsk_a", "ref": "CTL-01", "aliases": ["OLD-1"]},
                {"id": "TASK-002", "uid": "tsk_b", "ref": "CTL-02", "aliases": []},
            ]
        )

        self.assertEqual(index.resolve("OLD-1"), "TASK-001")
        self.assertEqual(index.resolve("CTL-02"), "TASK-002")

        with self.assertRaises(IdentityError) as raised:
            build_identity_index(
                [
                    {"id": "TASK-001", "uid": "tsk_a", "aliases": ["SAME"]},
                    {"id": "TASK-002", "uid": "tsk_b", "aliases": ["SAME"]},
                ]
            )

        self.assertEqual(raised.exception.code, "DUPLICATE_IDENTITY_TOKEN")

    def test_require_fields_reports_missing_fields(self):
        result = require_fields({"id": "TASK-001"}, ["id", "status"], prefix="task")

        self.assertFalse(result.ok)
        self.assertEqual(result.errors[0].code, "MISSING_REQUIRED_FIELD")
        self.assertEqual(result.errors[0].path, "task.status")


if __name__ == "__main__":
    unittest.main()


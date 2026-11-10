import sqlite3
import unittest

from tests.helpers import DatabaseTestCase
from time_balance.database import get_database, set_database
from time_balance.database.manager import DatabaseManager


class TestSettingsAndActiveProject(DatabaseTestCase):
    def test_a_missing_setting_returns_the_given_default(self):
        self.assertEqual(self.db.get_setting("missing", "fallback"), "fallback")

    def test_the_first_run_creates_a_default_project_and_settings(self):
        self.assertEqual([project["name"] for project in self.db.get_projects()], ["General"])
        self.assertEqual(self.db.get_setting("language", ""), "auto")
        self.assertEqual(self.db.get_active_project()["name"], "General")

    def test_a_deleted_active_project_falls_back_to_an_existing_one(self):
        other = self.db.create_project("Other", 8, 0)
        self.db.set_active_project_id(other)
        self.db.delete_project(other)
        self.assertEqual(self.db.get_active_project()["id"], self.project_id)
        self.assertEqual(self.db.get_active_project_id(), self.project_id)


class TestRecords(DatabaseTestCase):
    def test_deleting_a_project_deletes_its_records(self):
        other = self.db.create_project("Other", 8, 0)
        self.db.upsert_record(other, "2026-04-24", 8, 0, 0)
        self.db.delete_project(other)
        with self.db._get_connection() as connection:
            remaining = connection.execute("SELECT COUNT(*) FROM records").fetchone()[0]
        self.assertEqual(remaining, 0)

    def test_pagination_returns_distinct_pages_newest_first(self):
        for day in range(1, 8):
            self.db.upsert_record(self.project_id, f"2026-04-{day:02d}", 8, 0, 0)
        first = self.db.get_records(self.project_id, limit=3)
        second = self.db.get_records(self.project_id, limit=3, offset=3)
        self.assertEqual([r["date"] for r in first], ["2026-04-07", "2026-04-06", "2026-04-05"])
        self.assertEqual([r["date"] for r in second], ["2026-04-04", "2026-04-03", "2026-04-02"])

    def test_import_into_a_project_with_records_leaves_a_correct_balance(self):
        self.db.upsert_record(self.project_id, "2026-04-23", 8, 0, 15)
        self.db.upsert_record(self.project_id, "2026-04-25", 9, 0, 75)
        self.db.reset_project_balance(self.project_id)
        imported = self.db.import_records(
            self.project_id, {"2026-04-23": {"hours": 8, "minutes": 0, "difference": 15}}
        )
        self.assertEqual(imported, 1)
        self.assertEqual(self.db.get_total_balance(self.project_id), 15 + 75)

    def test_a_failed_write_is_rolled_back(self):
        self.db.upsert_record(self.project_id, "2026-04-24", 8, 0, 15)
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.create_project("General", 8, 0)
        self.assertEqual(len(self.db.get_projects()), 1)
        self.assertEqual(self.db.get_total_balance(self.project_id), 15)

    def test_a_record_cannot_point_to_a_missing_project(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.upsert_record(999, "2026-04-24", 8, 0, 0)


class TestSharedDatabase(unittest.TestCase):
    def tearDown(self):
        set_database(None)

    def test_the_shared_instance_is_opened_lazily_and_reused(self):
        import pathlib
        import tempfile
        from unittest import mock

        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / "shared.db"
            with mock.patch("time_balance.config.DATABASE_PATH", path):
                set_database(None)
                self.assertFalse(path.exists())
                first = get_database()
                self.assertTrue(path.exists())
                self.assertIs(get_database(), first)
                self.assertIsInstance(first, DatabaseManager)


if __name__ == "__main__":
    unittest.main()

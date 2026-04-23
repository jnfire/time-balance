import unittest
import tempfile
import pathlib
import os
from time_balance.storage import DatabaseManager
from time_balance import constants

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = pathlib.Path(self.tmp_dir.name) / "test.db"
        self.db = DatabaseManager(self.db_path)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_initialization(self):
        """Should create 'General' project and initial settings by default."""
        projects = self.db.get_projects()
        # Initial seeding creates 'General'
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]['name'], "General")
        
        # Should set active project id to 1 by default
        self.assertEqual(self.db.get_active_project_id(), 1)
        
        # Should set default language
        self.assertEqual(self.db.get_setting("language"), "auto")

    def test_create_and_get_projects(self):
        """Verify project creation and retrieval."""
        new_id = self.db.create_project("Side Hustle", 2, 30)
        self.assertGreater(new_id, 1)
        
        projects = self.db.get_projects()
        self.assertEqual(len(projects), 2)
        
        project = self.db.get_project_by_id(new_id)
        self.assertEqual(project['name'], "Side Hustle")
        self.assertEqual(project['base_hours'], 2)
        self.assertEqual(project['base_minutes'], 30)

    def test_upsert_and_get_records(self):
        """Verify record creation, update and retrieval sorting."""
        project_id = 1
        self.db.upsert_record(project_id, "2026-04-20", 8, 0, 15)
        self.db.upsert_record(project_id, "2026-04-21", 7, 45, 0)
        
        records = self.db.get_records(project_id)
        self.assertEqual(len(records), 2)
        # Records should be sorted by date DESC by default
        self.assertEqual(records[0]['date'], "2026-04-21")
        
        # Test update (UPSERT)
        self.db.upsert_record(project_id, "2026-04-21", 9, 0, 75)
        records = self.db.get_records(project_id)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]['hours'], 9)
        self.assertEqual(records[0]['difference'], 75)

    def test_total_balance(self):
        """Verify calculation of total balance for a project."""
        project_id = 1
        self.db.upsert_record(project_id, "2026-04-20", 8, 0, 15)
        self.db.upsert_record(project_id, "2026-04-21", 9, 0, 75)
        self.db.upsert_record(project_id, "2026-04-22", 7, 0, -45)
        
        balance = self.db.get_total_balance(project_id)
        self.assertEqual(balance, 15 + 75 - 45)

    def test_settings_persistence(self):
        """Verify global settings can be saved and retrieved."""
        self.db.set_setting("language", "es")
        self.assertEqual(self.db.get_setting("language"), "es")
        
        self.db.set_setting("last_run", "2026-04-24")
        self.assertEqual(self.db.get_setting("last_run"), "2026-04-24")

if __name__ == "__main__":
    unittest.main()

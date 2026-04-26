"""
Tests for COALESCE NULL balance handling.

This test module verifies that the cache update operations (upsert_record and delete_record)
correctly handle NULL total_balance values using COALESCE, ensuring the cache is always
updated regardless of its initial state.

Background: Previously, UPDATE queries included "WHERE total_balance IS NOT NULL",
which meant that if balance was NULL (due to import, restore, or other operations),
the cache would not be updated, leading to inconsistencies.
"""

import unittest
import tempfile
import pathlib
from time_balance.database.manager import DatabaseManager


class TestCoalesceNullBalance(unittest.TestCase):
    """Tests for COALESCE NULL balance handling in upsert and delete operations."""

    def setUp(self):
        """Create a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = pathlib.Path(self.temp_dir) / "test.db"
        self.db = DatabaseManager(db_path=self.temp_db)

    def tearDown(self):
        """Clean up temporary database."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def _set_balance_to_null(self, project_id: int):
        """Helper to manually set total_balance to NULL (simulating corrupted/imported data)."""
        with self.db._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE projects SET total_balance = NULL WHERE id = ?", (project_id,))

    def _get_cached_balance(self, project_id: int) -> int:
        """Helper to get the cached balance directly from DB (not recalculated)."""
        with self.db._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT total_balance FROM projects WHERE id = ?", (project_id,))
            result = cur.fetchone()
            return result[0] if result else None

    def test_upsert_initializes_null_balance_to_positive(self):
        """
        Verify that upsert_record correctly initializes a NULL balance to a positive value.
        This tests COALESCE(total_balance, 0) in the upsert operation.
        """
        project_id = self.db.create_project("Test Project", 8, 0)
        
        # Set balance to NULL to simulate imported data
        self._set_balance_to_null(project_id)
        self.assertIsNone(self._get_cached_balance(project_id), "Balance should be NULL initially")
        
        # Add first record with +45m
        self.db.upsert_record(project_id, "2026-04-01", 8, 45, 45)
        
        # Verify balance was updated from NULL to 45
        cached_balance = self._get_cached_balance(project_id)
        self.assertEqual(cached_balance, 45, "Balance should be 45 after upsert from NULL")

    def test_upsert_initializes_null_balance_to_negative(self):
        """
        Verify that upsert_record correctly initializes a NULL balance to a negative value.
        """
        project_id = self.db.create_project("Test Project", 8, 0)
        self._set_balance_to_null(project_id)
        
        # Add first record with -30m
        self.db.upsert_record(project_id, "2026-04-01", 7, 30, -30)
        
        # Verify balance was updated from NULL to -30
        cached_balance = self._get_cached_balance(project_id)
        self.assertEqual(cached_balance, -30, "Balance should be -30 after upsert from NULL")

    def test_delete_from_null_balance(self):
        """
        Verify that delete_record correctly subtracts from a NULL balance.
        This tests COALESCE(total_balance, 0) in the delete operation.
        """
        project_id = self.db.create_project("Test Project", 8, 0)
        
        # Add a record normally
        self.db.upsert_record(project_id, "2026-04-01", 8, 30, 30)
        self.assertEqual(self._get_cached_balance(project_id), 30)
        
        # Manually set balance to NULL (corrupted cache)
        self._set_balance_to_null(project_id)
        self.assertIsNone(self._get_cached_balance(project_id))
        
        # Delete the record - should subtract 30 from NULL (treated as 0)
        self.db.delete_record(project_id, "2026-04-01")
        
        # Verify balance was updated from NULL to -30
        cached_balance = self._get_cached_balance(project_id)
        self.assertEqual(cached_balance, -30, "Balance should be -30 after delete from NULL")

    def test_sequential_operations_starting_from_null(self):
        """
        Verify that a series of operations work correctly when starting from NULL balance.
        This tests the cache consistency across multiple incremental updates.
        """
        project_id = self.db.create_project("Test Project", 8, 0)
        self._set_balance_to_null(project_id)
        
        # Operation 1: Add +60m
        self.db.upsert_record(project_id, "2026-04-01", 9, 0, 60)
        self.assertEqual(self._get_cached_balance(project_id), 60, "After first +60m")
        
        # Operation 2: Add +30m
        self.db.upsert_record(project_id, "2026-04-02", 8, 30, 30)
        self.assertEqual(self._get_cached_balance(project_id), 90, "After second +30m")
        
        # Operation 3: Delete first record (-60m)
        self.db.delete_record(project_id, "2026-04-01")
        self.assertEqual(self._get_cached_balance(project_id), 30, "After deleting -60m")
        
        # Operation 4: Update second record (was +30m, now -15m = -45m change)
        self.db.upsert_record(project_id, "2026-04-02", 7, 45, -15)
        self.assertEqual(self._get_cached_balance(project_id), -15, "After updating to -15m")

    def test_update_existing_record_from_null_base(self):
        """
        Verify that updating (replacing) an existing record works correctly when base balance was NULL.
        """
        project_id = self.db.create_project("Test Project", 8, 0)
        
        # Add first record
        self.db.upsert_record(project_id, "2026-04-01", 8, 30, 30)
        self.assertEqual(self._get_cached_balance(project_id), 30)
        
        # Set balance to NULL
        self._set_balance_to_null(project_id)
        self.assertIsNone(self._get_cached_balance(project_id))
        
        # Update the record (old: +30m, new: +60m = +30m change)
        self.db.upsert_record(project_id, "2026-04-01", 9, 0, 60)
        
        # Should be 0 (NULL) - 30 (old) + 60 (new) = 30
        cached_balance = self._get_cached_balance(project_id)
        self.assertEqual(cached_balance, 30, "After updating record from NULL base")

    def test_multiple_projects_null_isolation(self):
        """
        Verify that NULL balance handling in one project doesn't affect another project.
        """
        proj1 = self.db.create_project("Project 1", 8, 0)
        proj2 = self.db.create_project("Project 2", 8, 0)
        
        # Set both to NULL
        self._set_balance_to_null(proj1)
        self._set_balance_to_null(proj2)
        
        # Add to project 1
        self.db.upsert_record(proj1, "2026-04-01", 8, 30, 30)
        
        # Verify project 1 is updated, project 2 is still NULL
        self.assertEqual(self._get_cached_balance(proj1), 30)
        self.assertIsNone(self._get_cached_balance(proj2))
        
        # Add to project 2
        self.db.upsert_record(proj2, "2026-04-01", 7, 0, -60)
        
        # Verify both are now updated correctly and independently
        self.assertEqual(self._get_cached_balance(proj1), 30)
        self.assertEqual(self._get_cached_balance(proj2), -60)

    def test_null_balance_consistency_with_get_total_balance(self):
        """
        Verify that after NULL is handled correctly, get_total_balance returns the right value
        and that recalculate_project_balance works correctly after COALESCE updates.
        """
        project_id = self.db.create_project("Test Project", 8, 0)
        self._set_balance_to_null(project_id)
        
        # Add records starting from NULL
        self.db.upsert_record(project_id, "2026-04-01", 8, 15, 15)
        self.db.upsert_record(project_id, "2026-04-02", 9, 0, 60)
        self.db.delete_record(project_id, "2026-04-01")
        
        # Get balance (should come from cache now)
        balance = self.db.get_total_balance(project_id)
        self.assertEqual(balance, 60, "get_total_balance should return 60")
        
        # Recalculate and verify it still matches
        recalc_balance = self.db.recalculate_project_balance(project_id)
        self.assertEqual(recalc_balance, 60, "recalculate should also return 60")

    def test_coalesce_with_zero_records(self):
        """
        Verify that COALESCE works correctly when project has zero records (sum is NULL).
        """
        project_id = self.db.create_project("Test Project", 8, 0)
        
        # Add and delete a record to test COALESCE path
        self.db.upsert_record(project_id, "2026-04-01", 8, 0, 0)
        self.assertEqual(self._get_cached_balance(project_id), 0)
        
        # Delete it
        self.db.delete_record(project_id, "2026-04-01")
        
        # Should be 0 (from COALESCE) - 0 (deleted) = 0
        self.assertEqual(self._get_cached_balance(project_id), 0)

    def test_rapid_operations_on_null_balance(self):
        """
        Verify that rapid add/delete/add operations work correctly starting from NULL.
        This tests robustness under stress conditions.
        """
        project_id = self.db.create_project("Test Project", 8, 0)
        self._set_balance_to_null(project_id)
        
        # Rapid operations
        self.db.upsert_record(project_id, "2026-04-01", 8, 30, 30)
        self.db.delete_record(project_id, "2026-04-01")
        self.db.upsert_record(project_id, "2026-04-02", 9, 0, 60)
        self.db.upsert_record(project_id, "2026-04-03", 7, 0, -45)
        self.db.delete_record(project_id, "2026-04-02")
        self.db.upsert_record(project_id, "2026-04-04", 8, 45, 45)
        
        # Final state: -45 + 45 = 0
        expected_balance = -45 + 45
        actual_balance = self.db.get_total_balance(project_id)
        self.assertEqual(actual_balance, expected_balance, "Balance after rapid operations")


if __name__ == "__main__":
    unittest.main()

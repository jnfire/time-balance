import unittest
import tempfile
import pathlib
from time_balance.database.manager import DatabaseManager


class TestDeleteRecordAndBalance(unittest.TestCase):
    """Tests for delete_record functionality and time balance calculations."""

    def setUp(self):
        """Create a temporary database for each test."""
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = pathlib.Path(self.tmp_dir.name) / "test.db"
        self.db = DatabaseManager(self.db_path)

    def tearDown(self):
        """Clean up temporary directory."""
        self.tmp_dir.cleanup()

    def test_delete_single_record_updates_balance(self):
        """Verify that deleting a record correctly updates the project balance."""
        project_id = 1
        
        # Add initial records
        self.db.upsert_record(project_id, "2026-01-10", 7, 30, 30)   # +30m
        self.db.upsert_record(project_id, "2026-01-11", 8, 30, 90)   # +90m
        self.db.upsert_record(project_id, "2026-01-12", 7, 0, -45)   # -45m
        
        # Verify initial balance: 30 + 90 - 45 = 75
        initial_balance = self.db.get_total_balance(project_id)
        self.assertEqual(initial_balance, 75, "Initial balance should be 75 minutes")
        
        # Delete middle record (90m)
        self.db.delete_record(project_id, "2026-01-11")
        
        # Verify balance after deletion: 75 - 90 = -15
        after_delete_balance = self.db.get_total_balance(project_id)
        self.assertEqual(after_delete_balance, -15, 
                        "Balance should be -15 after deleting +90m record")
        
        # Verify record is gone
        deleted_record = self.db.get_record_by_date(project_id, "2026-01-11")
        self.assertIsNone(deleted_record, "Deleted record should not exist")
        
        # Verify other records remain
        remaining_records = self.db.get_records(project_id)
        self.assertEqual(len(remaining_records), 2, "Should have 2 records left")

    def test_delete_positive_difference_record(self):
        """Verify deleting a record with positive difference reduces total balance."""
        project_id = 1
        
        self.db.upsert_record(project_id, "2026-02-01", 9, 0, 60)   # +60m
        self.db.upsert_record(project_id, "2026-02-02", 8, 0, 15)   # +15m
        
        balance_before = self.db.get_total_balance(project_id)
        self.assertEqual(balance_before, 75)
        
        # Delete positive record
        self.db.delete_record(project_id, "2026-02-01")
        
        balance_after = self.db.get_total_balance(project_id)
        self.assertEqual(balance_after, 15, 
                        "Balance should decrease by 60 minutes")

    def test_delete_negative_difference_record(self):
        """Verify deleting a record with negative difference increases total balance."""
        project_id = 1
        
        self.db.upsert_record(project_id, "2026-02-03", 7, 0, -30)  # -30m
        self.db.upsert_record(project_id, "2026-02-04", 8, 0, 15)   # +15m
        
        balance_before = self.db.get_total_balance(project_id)
        self.assertEqual(balance_before, -15)
        
        # Delete negative record
        self.db.delete_record(project_id, "2026-02-03")
        
        balance_after = self.db.get_total_balance(project_id)
        self.assertEqual(balance_after, 15, 
                        "Balance should increase by 30 minutes when deleting -30m")

    def test_delete_zero_difference_record(self):
        """Verify deleting a record with zero difference doesn't change balance."""
        project_id = 1
        
        self.db.upsert_record(project_id, "2026-02-05", 7, 45, 0)   # 0m
        self.db.upsert_record(project_id, "2026-02-06", 8, 0, 15)   # +15m
        
        balance_before = self.db.get_total_balance(project_id)
        self.assertEqual(balance_before, 15)
        
        # Delete zero-difference record
        self.db.delete_record(project_id, "2026-02-05")
        
        balance_after = self.db.get_total_balance(project_id)
        self.assertEqual(balance_after, 15, 
                        "Balance should remain 15m after deleting 0m record")

    def test_delete_all_records_clears_balance(self):
        """Verify that deleting all records results in zero balance."""
        project_id = 1
        
        # Add multiple records
        for i in range(5):
            self.db.upsert_record(project_id, f"2026-03-{10+i:02d}", 8, 0, 30)
        
        self.assertEqual(self.db.count_records(project_id), 5)
        self.assertEqual(self.db.get_total_balance(project_id), 150)
        
        # Delete all records
        for i in range(5):
            self.db.delete_record(project_id, f"2026-03-{10+i:02d}")
        
        self.assertEqual(self.db.count_records(project_id), 0)
        self.assertEqual(self.db.get_total_balance(project_id), 0, 
                        "Balance should be 0 after deleting all records")

    def test_delete_nonexistent_record_no_error(self):
        """Verify that deleting a non-existent record doesn't cause errors."""
        project_id = 1
        
        self.db.upsert_record(project_id, "2026-03-20", 8, 0, 30)
        balance_before = self.db.get_total_balance(project_id)
        
        # Try to delete non-existent record
        self.db.delete_record(project_id, "2099-12-31")
        
        # Balance should remain unchanged
        balance_after = self.db.get_total_balance(project_id)
        self.assertEqual(balance_before, balance_after, 
                        "Balance should not change when deleting non-existent record")
        
        # Original record should still exist
        self.assertIsNotNone(self.db.get_record_by_date(project_id, "2026-03-20"))

    def test_delete_updates_cached_balance(self):
        """Verify that delete_record updates the cached balance in projects table."""
        project_id = 1
        
        self.db.upsert_record(project_id, "2026-04-01", 8, 0, 45)
        
        # Access balance to ensure it's cached
        balance = self.db.get_total_balance(project_id)
        self.assertEqual(balance, 45)
        
        # Delete record
        self.db.delete_record(project_id, "2026-04-01")
        
        # Balance should be updated in cache immediately
        balance_after = self.db.get_total_balance(project_id)
        self.assertEqual(balance_after, 0)
        
        # Verify it's actually cached by checking projects table directly
        with self.db._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT total_balance FROM projects WHERE id = ?", (project_id,))
            cached_balance = cursor.fetchone()[0]
            self.assertEqual(cached_balance, 0, "Cached balance should be 0")


class TestRecalculateProjectBalance(unittest.TestCase):
    """Tests for project balance recalculation with multi-project isolation."""

    def setUp(self):
        """Create a temporary database for each test."""
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = pathlib.Path(self.tmp_dir.name) / "test.db"
        self.db = DatabaseManager(self.db_path)

    def tearDown(self):
        """Clean up temporary directory."""
        self.tmp_dir.cleanup()

    def test_recalculate_single_project_no_contamination(self):
        """Verify that recalculating one project doesn't affect other projects."""
        # Create two projects
        proj1_id = 1
        proj2_id = self.db.create_project("Project2", 8, 0)
        
        # Add records to both
        self.db.upsert_record(proj1_id, "2026-01-01", 7, 30, -15)
        self.db.upsert_record(proj1_id, "2026-01-02", 8, 30, 45)
        
        self.db.upsert_record(proj2_id, "2026-01-01", 8, 30, 30)
        self.db.upsert_record(proj2_id, "2026-01-02", 7, 0, -45)
        
        # Verify initial balances
        balance_proj1 = self.db.get_total_balance(proj1_id)
        balance_proj2 = self.db.get_total_balance(proj2_id)
        self.assertEqual(balance_proj1, 30)   # -15 + 45
        self.assertEqual(balance_proj2, -15)  # 30 - 45
        
        # Corrupt proj1 balance
        with self.db._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE projects SET total_balance = 999 WHERE id = ?", (proj1_id,))
        
        # Recalculate ONLY proj1
        recalculated_balance = self.db.recalculate_project_balance(proj1_id)
        self.assertEqual(recalculated_balance, 30, 
                        "Recalculated balance should be 30")
        
        # Verify proj2 balance is unchanged
        balance_proj2_after = self.db.get_total_balance(proj2_id)
        self.assertEqual(balance_proj2_after, -15, 
                        "Project2 balance should not be affected by recalculating Project1")

    def test_recalculate_corrects_corrupted_balance(self):
        """Verify that recalculate corrects a corrupted balance cache."""
        project_id = 1
        
        # Add records
        self.db.upsert_record(project_id, "2026-01-10", 8, 0, 60)
        self.db.upsert_record(project_id, "2026-01-11", 7, 0, -30)
        self.db.upsert_record(project_id, "2026-01-12", 8, 30, 45)
        
        correct_balance = self.db.get_total_balance(project_id)
        self.assertEqual(correct_balance, 75)  # 60 - 30 + 45
        
        # Corrupt the cache
        with self.db._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE projects SET total_balance = 12345 WHERE id = ?", (project_id,))
        
        # Verify corruption
        corrupted_balance = self.db.get_total_balance(project_id)
        self.assertEqual(corrupted_balance, 12345)
        
        # Recalculate
        recalculated = self.db.recalculate_project_balance(project_id)
        self.assertEqual(recalculated, 75, 
                        "Recalculation should return correct balance")
        
        # Verify fix persists
        verified_balance = self.db.get_total_balance(project_id)
        self.assertEqual(verified_balance, 75, 
                        "Balance should remain correct after recalculation")

    def test_recalculate_with_many_records(self):
        """Verify recalculate works correctly with many records."""
        project_id = 1
        
        # Add many records
        total_diff = 0
        for i in range(1, 101):
            diff = (i % 3) * 30 - 15  # Creates varying positive/negative values
            total_diff += diff
            self.db.upsert_record(project_id, f"2026-01-{i:02d}", 8, 0, diff)
        
        correct_balance = total_diff
        
        # Corrupt balance
        with self.db._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE projects SET total_balance = 0 WHERE id = ?", (project_id,))
        
        # Recalculate
        recalculated = self.db.recalculate_project_balance(project_id)
        self.assertEqual(recalculated, correct_balance, 
                        f"Recalculation should correctly sum all {100} records")

    def test_recalculate_mixed_positive_negative(self):
        """Verify recalculate correctly handles mixed positive and negative differences."""
        project_id = 1
        
        # Add mix of records
        records = [
            ("2026-02-01", 8, 0, 60),
            ("2026-02-02", 7, 0, -45),
            ("2026-02-03", 8, 30, 75),
            ("2026-02-04", 6, 30, -120),
            ("2026-02-05", 9, 0, 105),
        ]
        
        total = 0
        for date, hours, minutes, diff in records:
            self.db.upsert_record(project_id, date, hours, minutes, diff)
            total += diff
        
        # Verify initial correct balance
        balance = self.db.get_total_balance(project_id)
        self.assertEqual(balance, total)
        
        # Reset cache to NULL (simulate need to recalculate)
        self.db.reset_project_balance(project_id)
        
        # Recalculate
        recalculated = self.db.recalculate_project_balance(project_id)
        self.assertEqual(recalculated, total, 
                        "Recalculation should handle mixed positive/negative values")

    def test_recalculate_does_not_affect_other_projects(self):
        """Verify recalculate_all_balances affects all, while single affects only one."""
        # Create 3 projects
        proj1_id = 1
        proj2_id = self.db.create_project("Project2", 7, 45)
        proj3_id = self.db.create_project("Project3", 8, 0)
        
        # Add records to each
        self.db.upsert_record(proj1_id, "2026-03-01", 8, 0, 30)
        self.db.upsert_record(proj2_id, "2026-03-01", 7, 0, -15)
        self.db.upsert_record(proj3_id, "2026-03-01", 9, 0, 60)
        
        # Get initial balances
        b1_initial = self.db.get_total_balance(proj1_id)
        b2_initial = self.db.get_total_balance(proj2_id)
        b3_initial = self.db.get_total_balance(proj3_id)
        
        self.assertEqual(b1_initial, 30)
        self.assertEqual(b2_initial, -15)
        self.assertEqual(b3_initial, 60)
        
        # Corrupt all balances
        with self.db._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE projects SET total_balance = 999 WHERE id IN (?, ?, ?)", 
                         (proj1_id, proj2_id, proj3_id))
        
        # Recalculate only proj2
        self.db.recalculate_project_balance(proj2_id)
        
        # Verify only proj2 was fixed
        b1_after = self.db.get_total_balance(proj1_id)
        b2_after = self.db.get_total_balance(proj2_id)
        b3_after = self.db.get_total_balance(proj3_id)
        
        self.assertEqual(b1_after, 999, "Project1 should still be corrupted")
        self.assertEqual(b2_after, -15, "Project2 should be recalculated")
        self.assertEqual(b3_after, 999, "Project3 should still be corrupted")

    def test_reset_balance_forces_recalculation_on_next_access(self):
        """Verify that reset_project_balance forces recalculation on next access."""
        project_id = 1
        
        self.db.upsert_record(project_id, "2026-04-01", 8, 0, 45)
        
        # Get balance (caches it)
        balance = self.db.get_total_balance(project_id)
        self.assertEqual(balance, 45)
        
        # Reset cache
        self.db.reset_project_balance(project_id)
        
        # Verify cache is NULL
        with self.db._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT total_balance FROM projects WHERE id = ?", (project_id,))
            cached = cursor.fetchone()[0]
            self.assertIsNone(cached, "Balance should be NULL after reset")
        
        # Access balance again - should recalculate
        balance_after = self.db.get_total_balance(project_id)
        self.assertEqual(balance_after, 45, 
                        "Should recalculate and return correct balance")
        
        # Verify it's cached again
        with self.db._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT total_balance FROM projects WHERE id = ?", (project_id,))
            cached_again = cursor.fetchone()[0]
            self.assertEqual(cached_again, 45, "Balance should be cached again")


class TestDeleteAndRecalculateIntegration(unittest.TestCase):
    """Integration tests for delete and recalculate working together."""

    def setUp(self):
        """Create a temporary database for each test."""
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = pathlib.Path(self.tmp_dir.name) / "test.db"
        self.db = DatabaseManager(self.db_path)

    def tearDown(self):
        """Clean up temporary directory."""
        self.tmp_dir.cleanup()

    def test_delete_and_recalculate_consistency(self):
        """Verify delete and recalculate produce consistent results."""
        project_id = 1
        
        # Add records
        records = [
            ("2026-05-01", 8, 0, 60),
            ("2026-05-02", 7, 0, -30),
            ("2026-05-03", 8, 30, 75),
            ("2026-05-04", 6, 30, -45),
        ]
        
        for date, h, m, diff in records:
            self.db.upsert_record(project_id, date, h, m, diff)
        
        # Get initial balance via normal calculation
        balance_before = self.db.get_total_balance(project_id)
        expected_after_delete = balance_before - 60  # Deleting first record
        
        # Delete a record
        self.db.delete_record(project_id, "2026-05-01")
        
        # Get balance after delete
        balance_after_delete = self.db.get_total_balance(project_id)
        self.assertEqual(balance_after_delete, expected_after_delete)
        
        # Corrupt and recalculate
        self.db.reset_project_balance(project_id)
        recalculated = self.db.recalculate_project_balance(project_id)
        
        # Should match the delete result
        self.assertEqual(recalculated, balance_after_delete, 
                        "Recalculated balance should match post-delete balance")

    def test_multiple_deletes_and_recalculate(self):
        """Verify multiple deletes followed by recalculate remain consistent."""
        project_id = 1
        
        # Add 10 records
        for i in range(10):
            self.db.upsert_record(project_id, f"2026-06-{i+1:02d}", 8, 0, 30)
        
        initial_balance = 300  # 10 * 30
        self.assertEqual(self.db.get_total_balance(project_id), initial_balance)
        
        # Delete 3 records
        deleted_dates = ["2026-06-02", "2026-06-05", "2026-06-08"]
        for date in deleted_dates:
            self.db.delete_record(project_id, date)
        
        balance_after_deletes = self.db.get_total_balance(project_id)
        expected = initial_balance - (3 * 30)
        self.assertEqual(balance_after_deletes, expected)
        
        # Corrupt the cache
        with self.db._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE projects SET total_balance = 999 WHERE id = ?", (project_id,))
        
        # Recalculate
        recalculated = self.db.recalculate_project_balance(project_id)
        
        # Should match the delete result
        self.assertEqual(recalculated, balance_after_deletes, 
                        "Recalculation should account for all previous deletes")


if __name__ == "__main__":
    unittest.main()

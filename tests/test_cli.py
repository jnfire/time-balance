import unittest
import tempfile
import os
import io
import pathlib
from unittest import mock
import time_balance as ch

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = pathlib.Path(self.tmpdir.name) / "test_cli.db"
        
        # We need to re-initialize a DatabaseManager for tests
        from time_balance.storage import DatabaseManager
        self.db = DatabaseManager(self.db_path)
        
        # Patch the global db instance in all modules where it's used
        self.patchers = [
            mock.patch('time_balance.cli.db', self.db),
            mock.patch('time_balance.storage.db', self.db)
        ]
        for patcher in self.patchers:
            patcher.start()

    def tearDown(self):
        for patcher in self.patchers:
            patcher.stop()
        self.tmpdir.cleanup()

    def test_register_day_overwrite_cancel(self):
        """Verify that cancelling an overwrite does not change the record."""
        # Initial record
        self.db.upsert_record(1, "2026-01-01", 7, 0, -45)
        
        # inputs: date, confirmation 'n' (cancel)
        with mock.patch('builtins.input', side_effect=["2026-01-01", "n"]):
            ch.register_day(lang="en")
        
        record = self.db.get_record_by_date(1, "2026-01-01")
        self.assertEqual(record["hours"], 7)

    def test_register_day_overwrite_confirm(self):
        """Verify that confirming an overwrite updates the record in DB."""
        # Initial record
        self.db.upsert_record(1, "2026-01-01", 7, 0, -45)
        
        # inputs: date, confirmation 'y', hours '8', minutes '0'
        with mock.patch('builtins.input', side_effect=["2026-01-01", "y", "8", "0"]):
            ch.register_day(lang="en")
        
        record = self.db.get_record_by_date(1, "2026-01-01")
        self.assertEqual(record["hours"], 8)
        self.assertEqual(record["difference"], 15) # 8h vs 7h 45m

    def test_view_history_output(self):
        """Verify that view_history prints the correct number of records."""
        for i in range(1, 6):
            self.db.upsert_record(1, f"2026-01-0{i}", 8, 0, 15)
            
        buf = io.StringIO()
        with mock.patch('sys.stdout', buf):
            ch.view_history(limit=5, lang="en")
        out = buf.getvalue()
        
        self.assertIn("--- Last 5 records ---", out)
        count_dates = sum(1 for line in out.splitlines() if line.startswith("2026-"))
        self.assertEqual(count_dates, 5)

    def test_cli_args_status(self):
        """Verify the --status CLI argument output."""
        self.db.update_project(1, "ProyA", 7, 45)
        self.db.upsert_record(1, "2026-01-01", 8, 0, 15)
        
        buf = io.StringIO()
        with mock.patch('sys.stdout', buf):
            with mock.patch('sys.argv', ['time-balance', '--status', '--lang', 'en']):
                ch.main()
        out = buf.getvalue()
        
        self.assertIn("Project: ProyA", out)
        self.assertIn("Accumulated balance: 0h 15m", out)

if __name__ == "__main__":
    unittest.main()

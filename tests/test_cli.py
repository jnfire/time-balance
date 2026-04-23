import unittest
import tempfile
import io as python_io
import pathlib
from unittest import mock
from rich.console import Console
import time_balance as ch

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = pathlib.Path(self.tmpdir.name) / "test_cli.db"
        
        from time_balance.storage import DatabaseManager
        self.db = DatabaseManager(self.db_path)
        
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
        """Verify that cancelling an overwrite does not change the record using Rich prompts."""
        self.db.upsert_record(1, "2026-01-01", 7, 0, -45)
        
        # Patch request_date to return specific date and Confirm.ask for 'n'
        with mock.patch('time_balance.cli.request_date', return_value="2026-01-01"):
            with mock.patch('rich.prompt.Confirm.ask', return_value=False):
                ch.register_day(lang="en")
        
        record = self.db.get_record_by_date(1, "2026-01-01")
        self.assertEqual(record["hours"], 7)

    def test_register_day_overwrite_confirm(self):
        """Verify that confirming an overwrite updates the record in DB using Rich prompts."""
        self.db.upsert_record(1, "2026-01-01", 7, 0, -45)
        
        # Patch request_date, Confirm.ask for 'y', and Prompt.ask for hours/minutes
        with mock.patch('time_balance.cli.request_date', return_value="2026-01-01"):
            with mock.patch('rich.prompt.Confirm.ask', return_value=True):
                with mock.patch('rich.prompt.Prompt.ask', side_effect=["8", "0"]):
                    ch.register_day(lang="en")
        
        record = self.db.get_record_by_date(1, "2026-01-01")
        self.assertEqual(record["hours"], 8)
        self.assertEqual(record["difference"], 15)

    def test_view_history_table(self):
        """Verify that view_history renders a Rich table with records."""
        for i in range(1, 4):
            self.db.upsert_record(1, f"2026-01-0{i}", 8, 0, 15)
            
        # Capture rich output
        test_console = Console(file=python_io.StringIO(), force_terminal=False, width=100)
        with mock.patch('time_balance.cli.console', test_console):
            ch.view_history(limit=5, lang="en")
        
        output = test_console.file.getvalue()
        self.assertIn("2026-01-01", output)
        self.assertIn("2026-01-02", output)
        self.assertIn("2026-01-03", output)
        self.assertIn("8h 0m", output)

    def test_cli_args_status_rich(self):
        """Verify the --status CLI argument output with Rich formatting."""
        self.db.update_project(1, "ProyA", 7, 45)
        self.db.upsert_record(1, "2026-01-01", 8, 0, 15)
        
        test_console = Console(file=python_io.StringIO(), force_terminal=False, width=100)
        with mock.patch('time_balance.cli.console', test_console):
            with mock.patch('sys.argv', ['time-balance', '--status', '--lang', 'en']):
                ch.main()
        
        output = test_console.file.getvalue()
        self.assertIn("Project: ProyA", output)
        self.assertIn("Accumulated balance: +0h 15m", output)

if __name__ == "__main__":
    unittest.main()

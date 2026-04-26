import unittest
import tempfile
import io as python_io
import pathlib
from unittest import mock
from rich.console import Console

# Modular imports
from time_balance.database.manager import DatabaseManager
from time_balance.cli.main import main
from time_balance.cli.registration import register_day
from time_balance.cli.history import view_history
from time_balance.cli.config_menu import config_menu

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = pathlib.Path(self.tmpdir.name) / "test_cli.db"
        
        self.db = DatabaseManager(self.db_path)
        
        # We still use a Rich Console for some internal tests, but we mock the UI interface
        self.test_console = Console(file=python_io.StringIO(), force_terminal=False, width=100)

        # Patch the db instance in all relevant modules
        self.patchers = [
            mock.patch('time_balance.database.manager.db', self.db),
            mock.patch('time_balance.cli.main.db', self.db),
            mock.patch('time_balance.cli.registration.db', self.db),
            mock.patch('time_balance.cli.history.db', self.db),
            mock.patch('time_balance.cli.config_menu.db', self.db),
            mock.patch('time_balance.cli.projects.db', self.db),
        ]
        for patcher in self.patchers:
            patcher.start()

    def tearDown(self):
        for patcher in self.patchers:
            patcher.stop()
        self.tmpdir.cleanup()

    def test_register_day_overwrite_cancel(self):
        """Verify that cancelling an overwrite does not change the record."""
        self.db.upsert_record(1, "2026-01-01", 7, 0, -45)
        
        # Mocking UI interface instead of Rich directly
        with mock.patch('time_balance.cli.registration.request_date', return_value="2026-01-01"):
            with mock.patch('time_balance.ui.interface.ask_confirm', return_value=False):
                register_day(lang="en")
        
        record = self.db.get_record_by_date(1, "2026-01-01")
        self.assertEqual(record["hours"], 7)

    def test_register_day_overwrite_confirm(self):
        """Verify that confirming an overwrite updates the record in DB."""
        self.db.upsert_record(1, "2026-01-01", 7, 0, -45)
        
        # Mocking UI interface
        with mock.patch('time_balance.cli.registration.request_date', return_value="2026-01-01"):
            with mock.patch('time_balance.ui.interface.ask_confirm', return_value=True):
                with mock.patch('time_balance.ui.interface.ask_string', side_effect=["8", "0"]):
                    register_day(lang="en")
        
        record = self.db.get_record_by_date(1, "2026-01-01")
        self.assertEqual(record["hours"], 8)
        self.assertEqual(record["difference"], 15)

    def test_view_history_table(self):
        """Verify that view_history calls render_table with records."""
        for i in range(1, 4):
            self.db.upsert_record(1, f"2026-01-0{i}", 8, 0, 15)
            
        with mock.patch('time_balance.ui.interface.render_table') as mock_render:
            view_history(limit=5, lang="en")
        
        # Check if render_table was called
        self.assertTrue(mock_render.called)
        # Check if 3 rows were prepared (args[2] of render_table call)
        rows = mock_render.call_args[0][2]
        self.assertEqual(len(rows), 3)

    def test_view_history_pagination(self):
        """Verify that view_history handles interactive pagination navigation."""
        # Create 15 records to have 2 pages
        for i in range(1, 16):
            self.db.upsert_record(1, f"2026-01-{i:02d}", 8, 0, 15)
            
        # Mock inputs: 'n' (next page), then 'v' (back to menu)
        with mock.patch('time_balance.ui.interface.ask_string', side_effect=["n", "v"]):
            with mock.patch('time_balance.ui.interface.render_table') as mock_render:
                view_history(lang="en")
        
        # Should have called render_table twice (page 1 then page 2)
        self.assertEqual(mock_render.call_count, 2)

    def test_config_menu_v_navigation(self):
        """Verify that config_menu uses 'v' for navigation."""
        # Mock input: 'v' to exit config menu immediately
        with mock.patch('time_balance.ui.interface.ask_string', side_effect=["v"]):
            config_menu(lang="en")

    def test_cli_args_status_logic(self):
        """Verify the --status CLI argument logic using UI mocks."""
        self.db.update_project(1, "ProyA", 7, 45)
        self.db.upsert_record(1, "2026-01-01", 8, 0, 15)
        
        with mock.patch('time_balance.ui.interface.print_message') as mock_print:
            with mock.patch('sys.argv', ['time-balance', '--status', '--lang', 'en']):
                main()
        
        # Check if project name and balance were printed
        calls = [call[0][0] for call in mock_print.call_args_list]
        self.assertTrue(any("ProyA" in str(c) for c in calls))
        self.assertTrue(any("+0h 15m" in str(c) for c in calls))

if __name__ == "__main__":
    unittest.main()

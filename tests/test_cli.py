import unittest
import tempfile
import os
import io
import json
from unittest import mock
import time_balance as ch

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self._orig_cwd = os.getcwd()
        os.chdir(self.tmpdir.name)
        self._orig_archivo = ch.constants.DATA_FILE
        self.data_file = os.path.join(self.tmpdir.name, 'history.json')
        ch.constants.DATA_FILE = self.data_file

    def tearDown(self):
        os.chdir(self._orig_cwd)
        ch.constants.DATA_FILE = self._orig_archivo
        self.tmpdir.cleanup()

    def test_register_day_overwrite_cancel(self):
        datos = {
            "metadata": {"project_name": "Test", "hours_base": 7, "minutes_base": 45, "version": "1.0", "language": "en"},
            "records": {"2026-01-01": {"hours": 7, "minutes": 0, "difference": -45}}
        }
        # inputs: date, confirmation 'n' (cancel)
        with mock.patch('builtins.input', side_effect=["2026-01-01", "n"]):
            ch.register_day(datos, lang="en")
        self.assertEqual(datos["records"]["2026-01-01"]["hours"], 7)

    def test_register_day_overwrite_confirm(self):
        datos = {
            "metadata": {"project_name": "Test", "hours_base": 7, "minutes_base": 45, "version": "1.0", "language": "en"},
            "records": {"2026-01-01": {"hours": 7, "minutes": 0, "difference": -45}}
        }
        # inputs: date, confirmation 'y', hours '8', minutes '0'
        with mock.patch('builtins.input', side_effect=["2026-01-01", "y", "8", "0"]):
            ch.register_day(datos, lang="en")
        self.assertEqual(datos["records"]["2026-01-01"]["hours"], 8)
        self.assertEqual(ch.load_data()["records"]["2026-01-01"]["hours"], 8)

    def test_view_history_output(self):
        datos = {
            "metadata": {"project_name": "Test", "hours_base": 7, "minutes_base": 45, "version": "1.0", "language": "en"},
            "records": {
                "2026-01-01": {"hours": 8, "minutes": 0, "difference": 15},
                "2026-01-02": {"hours": 7, "minutes": 0, "difference": -45},
                "2026-01-03": {"hours": 9, "minutes": 0, "difference": 75},
                "2026-01-04": {"hours": 6, "minutes": 30, "difference": -75},
                "2026-01-05": {"hours": 7, "minutes": 45, "difference": 0}
            }
        }
        buf = io.StringIO()
        with mock.patch('sys.stdout', buf):
            ch.view_history(datos, lang="en")
        out = buf.getvalue()
        self.assertIn("--- Last 5 records ---", out)
        self.assertIn("2026-01-05", out)
        count_dates = sum(1 for line in out.splitlines() if line.startswith("2026-"))
        self.assertEqual(count_dates, 5)

    def test_cli_args_status(self):
        datos = {
            "metadata": {"project_name": "ProyA", "hours_base": 7, "minutes_base": 45, "version": "1.0", "language": "en"},
            "records": {"2026-01-01": {"hours": 8, "minutes": 0, "difference": 15}}
        }
        ch.save_data(datos)
        buf = io.StringIO()
        with mock.patch('sys.stdout', buf):
            with mock.patch('sys.argv', ['time-balance', '--status', '--lang', 'en']):
                ch.main()
        out = buf.getvalue()
        self.assertIn("Project: ProyA", out)
        self.assertIn("Accumulated balance: 0h 15m", out)

if __name__ == "__main__":
    unittest.main()

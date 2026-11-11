import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from tests.helpers import DatabaseTestCase, ScriptedTerminal
from time_balance import config
from time_balance.cli.main import build_parser, display_dashboard, interactive_menu, main


class TestParser(unittest.TestCase):
    def test_defaults(self):
        args = build_parser().parse_args([])
        self.assertFalse(args.status)
        self.assertIsNone(args.list)
        self.assertEqual(args.lang, "auto")

    def test_list_takes_an_optional_count(self):
        self.assertEqual(build_parser().parse_args(["--list"]).list, 5)
        self.assertEqual(build_parser().parse_args(["--list", "12"]).list, 12)

    def test_unknown_language_is_rejected(self):
        with self.assertRaises(SystemExit), mock.patch("sys.stderr"):
            build_parser().parse_args(["--lang", "fr"])


class TestMain(DatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.db.upsert_record(self.project_id, "2026-04-24", 8, 15, 30)

    def run_main(self, argv, answers=()):
        with ScriptedTerminal(answers).active() as terminal:
            code = main(argv)
        return code, terminal

    def test_version(self):
        code, terminal = self.run_main(["--version"])
        self.assertEqual(code, 0)
        self.assertIn(config.VERSION, terminal.output)

    def test_status_shows_the_project_and_the_balance(self):
        code, terminal = self.run_main(["--status", "--lang", "en"])
        self.assertEqual(code, 0)
        self.assertIn("Project: General", terminal.output)
        self.assertIn("+30m", terminal.output)

    def test_status_in_spanish(self):
        _, terminal = self.run_main(["--status", "--lang", "es"])
        self.assertIn("Proyecto: General", terminal.output)

    def test_list(self):
        _, terminal = self.run_main(["--list", "5", "--lang", "en"])
        self.assertIn("2026-04-24", terminal.output)
        self.assertIn("8h 15m", terminal.output)

    def test_the_stored_language_is_used_when_none_is_forced(self):
        self.db.set_setting("language", "es")
        _, terminal = self.run_main(["--status"])
        self.assertIn("Saldo acumulado", terminal.output)

    def test_the_forced_language_applies_to_the_interactive_menu(self):
        _, terminal = self.run_main(["--lang", "es"], answers=["5"])
        self.assertIn("Registrar jornada", terminal.output)

    def test_ctrl_c_ends_the_menu_cleanly(self):
        with ScriptedTerminal([KeyboardInterrupt()]).active() as terminal:
            code = main(["--lang", "en"])
        self.assertEqual(code, 0)
        self.assertIn("cancelled", terminal.output.lower())


class TestInteractiveMenu(DatabaseTestCase):
    def test_exit_option(self):
        with ScriptedTerminal(["5"]).active() as terminal:
            interactive_menu(self.ctx)
        self.assertIn("DASHBOARD", terminal.output)

    def test_registering_a_day_from_the_menu(self):
        with ScriptedTerminal(["1", "2026-04-24", "8", "0", "", "5"]).active():
            interactive_menu(self.ctx)
        self.assertEqual(self.db.count_records(self.project_id), 1)

    def test_a_language_change_in_settings_reaches_the_menu(self):
        with ScriptedTerminal(["3", "3", "es", "v", "5"]).active() as terminal:
            interactive_menu(self.ctx)
        self.assertIn("Registrar jornada", terminal.output)

    def test_the_other_screens_are_reachable(self):
        with ScriptedTerminal(["2", "", "4", "v", "5"]).active() as terminal:
            interactive_menu(self.ctx)
        self.assertIn("No records", terminal.output)


class TestDashboard(DatabaseTestCase):
    def test_without_records_there_is_no_last_record_line(self):
        with ScriptedTerminal().active() as terminal:
            display_dashboard(self.ctx)
        self.assertNotIn("Last record", terminal.output)
        self.assertIn("Total accumulated balance: 0m", terminal.output)

    def test_shows_the_last_record(self):
        self.db.upsert_record(self.project_id, "2026-04-23", 8, 0, 15)
        self.db.upsert_record(self.project_id, "2026-04-24", 7, 0, -45)
        with ScriptedTerminal().active() as terminal:
            display_dashboard(self.ctx)
        self.assertIn("Last record: 2026-04-24 · 7h · -45m", terminal.output)

    def test_a_project_name_with_markup_is_shown_literally(self):
        self.db.update_project(self.project_id, "[red]Acme[/red]", 8, 0)
        with ScriptedTerminal().active() as terminal:
            display_dashboard(self.ctx)
        self.assertIn("[red]Acme[/red]", terminal.output)

    def test_the_active_project_is_recovered_if_it_no_longer_exists(self):
        other = self.db.create_project("Other", 8, 0)
        self.db.set_active_project_id(other)
        self.db.delete_project(other)
        with ScriptedTerminal().active() as terminal:
            display_dashboard(self.ctx)
        self.assertIn("General", terminal.output)


class TestNoSideEffects(unittest.TestCase):
    def run_python(self, code, data_dir):
        environment = {**os.environ, "XDG_DATA_HOME": data_dir, "APPDATA": data_dir}
        return subprocess.run(
            [sys.executable, "-c", code],
            env=environment,
            capture_output=True,
            text=True,
            check=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )

    def test_importing_the_package_and_asking_for_the_version_never_creates_the_database(self):
        with tempfile.TemporaryDirectory() as data_dir:
            self.run_python("import time_balance", data_dir)
            self.run_python("from time_balance import main; main(['--version'])", data_dir)
            self.assertEqual(os.listdir(data_dir), [])

    def test_the_first_real_command_creates_it(self):
        with tempfile.TemporaryDirectory() as data_dir:
            self.run_python("from time_balance import main; main(['--status'])", data_dir)
            self.assertTrue(
                os.path.exists(os.path.join(data_dir, "time-balance", "time_balance.db"))
            )


if __name__ == "__main__":
    unittest.main()

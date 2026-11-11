import json
import unittest

from tests.helpers import DatabaseTestCase, ScriptedTerminal
from time_balance.cli.config_menu import config_menu
from time_balance.cli.projects import find_deletable_project, name_is_taken, project_menu
from time_balance.utils.validation import InputError


class TestProjectRules(DatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.second = self.db.create_project("Client B", 8, 0)
        self.projects = self.db.get_projects()

    def test_name_is_taken_ignores_case_and_the_project_itself(self):
        self.assertTrue(name_is_taken(self.projects, "client b"))
        self.assertTrue(name_is_taken(self.projects, "  GENERAL "))
        self.assertFalse(name_is_taken(self.projects, "Client B", ignore_id=self.second))
        self.assertFalse(name_is_taken(self.projects, "Client C"))

    def test_the_active_project_cannot_be_deleted(self):
        with self.assertRaises(InputError) as caught:
            find_deletable_project(self.projects, self.project_id, self.project_id)
        self.assertEqual(caught.exception.message_key, "cannot_delete_active")

    def test_an_unknown_id_is_reported(self):
        with self.assertRaises(InputError) as caught:
            find_deletable_project(self.projects, self.project_id, 999)
        self.assertEqual(caught.exception.message_key, "project_not_found")

    def test_another_project_can_be_deleted(self):
        project = find_deletable_project(self.projects, self.project_id, self.second)
        self.assertEqual(project["name"], "Client B")


class TestProjectMenu(DatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.second = self.db.create_project("Client B", 8, 0)

    def run_menu(self, answers):
        with ScriptedTerminal(answers).active() as terminal:
            project_menu(self.ctx)
        return terminal

    def test_choosing_an_id_switches_the_project(self):
        self.run_menu([str(self.second)])
        self.assertEqual(self.db.get_active_project_id(), self.second)

    def test_back_changes_nothing(self):
        self.run_menu(["v"])
        self.assertEqual(self.db.get_active_project_id(), self.project_id)

    def test_creating_a_project_makes_it_active(self):
        self.run_menu(["c", "Client C", "6", "30"])
        project = self.db.get_active_project()
        self.assertEqual(
            (project["name"], project["base_hours"], project["base_minutes"]), ("Client C", 6, 30)
        )

    def test_a_duplicate_name_is_refused_instead_of_crashing(self):
        terminal = self.run_menu(["c", "client b", "", "v"])
        self.assertIn("already exists", terminal.output)
        self.assertEqual(len(self.db.get_projects()), 2)

    def test_an_invalid_base_creates_nothing(self):
        self.run_menu(["c", "Client C", "30", "0", "", "v"])
        self.assertEqual(len(self.db.get_projects()), 2)

    def test_deleting_needs_the_exact_name(self):
        self.run_menu(["d", str(self.second), "wrong name", "", "v"])
        self.assertIsNotNone(self.db.get_project_by_id(self.second))
        self.run_menu(["d", str(self.second), "Client B", "", "v"])
        self.assertIsNone(self.db.get_project_by_id(self.second))

    def test_the_active_project_cannot_be_deleted_from_the_menu(self):
        terminal = self.run_menu(["d", str(self.project_id), "", "v"])
        self.assertIn("cannot delete the active project", terminal.output.lower())

    def test_names_with_square_brackets_do_not_break_the_screen(self):
        self.db.create_project("[bold]oops[/", 8, 0)
        terminal = self.run_menu(["v"])
        self.assertIn("[bold]oops[/", terminal.output)


class TestConfigMenu(DatabaseTestCase):
    def run_menu(self, answers):
        with ScriptedTerminal(answers).active() as terminal:
            ctx = config_menu(self.ctx)
        return terminal, ctx

    def test_edit_name(self):
        self.run_menu(["1", "Renamed", "v"])
        self.assertEqual(self.db.get_active_project()["name"], "Renamed")

    def test_edit_name_refuses_a_name_in_use(self):
        self.db.create_project("Client B", 8, 0)
        terminal, _ = self.run_menu(["1", "Client B", "", "v"])
        self.assertIn("already exists", terminal.output)
        self.assertEqual(self.db.get_active_project()["name"], "General")

    def test_edit_base(self):
        self.run_menu(["2", "8", "30", "v"])
        project = self.db.get_active_project()
        self.assertEqual((project["base_hours"], project["base_minutes"]), (8, 30))

    def test_edit_base_rejects_invalid_values(self):
        self.run_menu(["2", "8", "99", "", "v"])
        project = self.db.get_active_project()
        self.assertEqual((project["base_hours"], project["base_minutes"]), (7, 45))

    def test_changing_the_language_is_stored_and_returned(self):
        _, ctx = self.run_menu(["3", "es", "v"])
        self.assertEqual(self.db.get_setting("language", ""), "es")
        self.assertEqual(ctx.lang, "es")

    def test_repair_rebuilds_the_balance(self):
        self.db.upsert_record(self.project_id, "2026-04-24", 8, 0, 15)
        with self.db._get_connection() as connection:
            connection.execute("UPDATE projects SET total_balance = 999")
        self.run_menu(["6", "y", "", "v"])
        self.assertEqual(self.db.get_total_balance(self.project_id), 15)


class TestImportExport(DatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.db.upsert_record(self.project_id, "2026-04-23", 8, 0, 15)
        self.db.upsert_record(self.project_id, "2026-04-24", 7, 0, -45)
        self.export_path = self.tmp_path / "out" / "history.json"

    def export(self):
        with ScriptedTerminal(["5", str(self.export_path), "", "v"]).active() as terminal:
            config_menu(self.ctx)
        return terminal

    def test_export_writes_the_documented_format(self):
        terminal = self.export()
        data = json.loads(self.export_path.read_text(encoding="utf-8"))
        self.assertEqual(data["metadata"]["project_name"], "General")
        self.assertEqual(data["metadata"]["hours_base"], 7)
        self.assertEqual(
            data["records"]["2026-04-24"], {"hours": 7, "minutes": 0, "difference": -45}
        )
        self.assertIn("exported", terminal.output.lower())

    def test_merge_import_keeps_existing_days(self):
        self.export()
        self.db.upsert_record(self.project_id, "2026-04-25", 9, 0, 75)
        with ScriptedTerminal(["4", str(self.export_path), "merge", "", "v"]).active():
            config_menu(self.ctx)
        self.assertEqual(self.db.count_records(self.project_id), 3)
        self.assertEqual(self.db.get_total_balance(self.project_id), 15 - 45 + 75)

    def test_overwrite_import_replaces_everything(self):
        self.export()
        self.db.upsert_record(self.project_id, "2026-04-25", 9, 0, 75)
        with ScriptedTerminal(["4", str(self.export_path), "overwrite", "", "v"]).active():
            config_menu(self.ctx)
        self.assertEqual(self.db.count_records(self.project_id), 2)
        self.assertEqual(self.db.get_total_balance(self.project_id), 15 - 45)

    def test_a_bad_file_is_reported_and_changes_nothing(self):
        bad = self.tmp_path / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        with ScriptedTerminal(["4", str(bad), "overwrite", "", "v"]).active() as terminal:
            config_menu(self.ctx)
        self.assertIn("Invalid JSON", terminal.output)
        self.assertEqual(self.db.count_records(self.project_id), 2)

    def test_a_missing_file_is_reported(self):
        with ScriptedTerminal(
            ["4", str(self.tmp_path / "nope.json"), "merge", "", "v"]
        ).active() as terminal:
            config_menu(self.ctx)
        self.assertIn("File not found", terminal.output)

    def test_export_to_an_unwritable_place_is_reported(self):
        blocker = self.tmp_path / "file"
        blocker.write_text("x")
        with ScriptedTerminal(["5", str(blocker / "history.json"), "", "v"]).active() as terminal:
            config_menu(self.ctx)
        self.assertIn("Error exporting", terminal.output)


if __name__ == "__main__":
    unittest.main()

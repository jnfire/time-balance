import unittest
from unittest import mock

from tests.helpers import DatabaseTestCase, ScriptedTerminal
from time_balance.cli.history import PAGE_SIZE, browse_history, delete_record_flow, list_records
from time_balance.cli.registration import register_day


class TestRegisterDay(DatabaseTestCase):
    def test_stores_the_day_and_the_difference_against_the_base(self):
        # The default project has a base of 7h 45m.
        with ScriptedTerminal(["2026-04-24", "8", "15"]).active() as terminal:
            register_day(self.ctx)
        record = self.db.get_record_by_date(self.project_id, "2026-04-24")
        self.assertEqual((record["hours"], record["minutes"], record["difference"]), (8, 15, 30))
        self.assertEqual(self.db.get_total_balance(self.project_id), 30)
        self.assertIn("+30m", terminal.output)

    def test_an_invalid_date_cancels_instead_of_using_today(self):
        with ScriptedTerminal(["not a date"]).active() as terminal:
            register_day(self.ctx)
        self.assertEqual(self.db.count_records(self.project_id), 0)
        self.assertIn("Invalid date", terminal.output)

    def test_invalid_time_stores_nothing(self):
        for hours, minutes in (("x", "0"), ("8", "75"), ("-2", "0")):
            with self.subTest(hours=hours, minutes=minutes):
                with ScriptedTerminal(["2026-04-24", hours, minutes]).active():
                    register_day(self.ctx)
                self.assertEqual(self.db.count_records(self.project_id), 0)

    def test_cancelling_an_overwrite_keeps_the_record(self):
        self.db.upsert_record(self.project_id, "2026-04-24", 7, 0, -45)
        with ScriptedTerminal(["2026-04-24", "n"]).active() as terminal:
            register_day(self.ctx)
        self.assertEqual(self.db.get_record_by_date(self.project_id, "2026-04-24")["hours"], 7)
        self.assertIn("cancelled", terminal.output.lower())

    def test_confirming_an_overwrite_replaces_it_and_fixes_the_balance(self):
        self.db.upsert_record(self.project_id, "2026-04-24", 7, 0, -45)
        with ScriptedTerminal(["2026-04-24", "y", "8", "0"]).active():
            register_day(self.ctx)
        self.assertEqual(self.db.get_record_by_date(self.project_id, "2026-04-24")["hours"], 8)
        self.assertEqual(self.db.get_total_balance(self.project_id), 15)

    def test_the_confirmation_letters_follow_the_language(self):
        self.db.upsert_record(self.project_id, "2026-04-24", 7, 0, -45)
        spanish = self.ctx.with_lang("es")
        with ScriptedTerminal(["2026-04-24", "s", "8", "0"]).active():
            register_day(spanish)
        self.assertEqual(self.db.get_record_by_date(self.project_id, "2026-04-24")["hours"], 8)


class TestListRecords(DatabaseTestCase):
    def setUp(self):
        super().setUp()
        for day in range(1, 13):
            self.db.upsert_record(self.project_id, f"2026-04-{day:02d}", 8, 0, 15)

    def test_lists_only_the_requested_number_newest_first(self):
        with ScriptedTerminal().active() as terminal:
            list_records(self.ctx, 3)
        self.assertIn("2026-04-12", terminal.output)
        self.assertIn("2026-04-10", terminal.output)
        self.assertNotIn("2026-04-09", terminal.output)

    def test_zero_lists_everything(self):
        with ScriptedTerminal().active() as terminal:
            list_records(self.ctx, 0)
        self.assertIn("2026-04-01", terminal.output)

    def test_says_so_when_there_is_nothing(self):
        self.db.clear_project_records(self.project_id)
        with ScriptedTerminal().active() as terminal:
            list_records(self.ctx, 5)
        self.assertIn("No records", terminal.output)


class TestBrowseHistory(DatabaseTestCase):
    def setUp(self):
        super().setUp()
        for day in range(1, 26):
            self.db.upsert_record(self.project_id, f"2026-04-{day:02d}", 8, 0, 15)

    def test_pages_forward_and_back(self):
        self.assertEqual(PAGE_SIZE, 10)
        with ScriptedTerminal(["n", "n", "p", "v"]).active() as terminal:
            browse_history(self.ctx)
        self.assertIn("Page 1 of 3", terminal.output)
        self.assertIn("Page 3 of 3", terminal.output)

    def test_the_navigation_only_offers_pages_that_exist(self):
        terminal = ScriptedTerminal(["v"])
        with terminal.active():
            browse_history(self.ctx)
        self.assertNotIn("Previous", terminal.output)

    def test_deleting_from_the_history_updates_the_balance(self):
        with ScriptedTerminal(["d", "2026-04-25", "y", "", "v"]).active():
            browse_history(self.ctx)
        self.assertIsNone(self.db.get_record_by_date(self.project_id, "2026-04-25"))
        self.assertEqual(self.db.get_total_balance(self.project_id), 24 * 15)

    def test_an_empty_history_returns_after_a_pause(self):
        self.db.clear_project_records(self.project_id)
        with ScriptedTerminal([""]).active() as terminal:
            browse_history(self.ctx)
        self.assertIn("No records", terminal.output)


class TestDeleteRecordFlow(DatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.db.upsert_record(self.project_id, "2026-04-24", 9, 0, 75)

    def delete(self, answers):
        with ScriptedTerminal(answers).active() as terminal:
            delete_record_flow(self.ctx, self.project_id)
        return terminal

    def test_confirming_deletes(self):
        terminal = self.delete(["2026-04-24", "y", ""])
        self.assertIsNone(self.db.get_record_by_date(self.project_id, "2026-04-24"))
        self.assertIn("deleted", terminal.output.lower())

    def test_declining_keeps_the_record(self):
        self.delete(["2026-04-24", "n", ""])
        self.assertIsNotNone(self.db.get_record_by_date(self.project_id, "2026-04-24"))

    def test_a_blank_date_cancels(self):
        self.delete(["", ""])
        self.assertEqual(self.db.count_records(self.project_id), 1)

    def test_an_unknown_or_malformed_date_is_reported(self):
        for typed in ("2026-01-01", "[bold]oops"):
            with self.subTest(typed=typed):
                terminal = self.delete([typed, ""])
                self.assertIn("No record", terminal.output)
        self.assertEqual(self.db.count_records(self.project_id), 1)

    def test_nothing_to_delete(self):
        self.db.clear_project_records(self.project_id)
        terminal = self.delete([""])
        self.assertIn("No records", terminal.output)


if __name__ == "__main__":
    with mock.patch("sys.argv", ["x"]):
        unittest.main()

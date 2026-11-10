import json
import os
import tempfile
import unittest

import time_balance.utils.files as io


class TestImportExport(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_export_history_creates_file(self):
        """Verify that export_history correctly writes the provided dictionary to a JSON file."""
        data = {
            "metadata": {"project_name": "Test", "hours_base": 8, "minutes_base": 0},
            "records": {},
        }
        dest = os.path.join(self.tmpdir.name, "export.json")
        result_path = io.export_history(data, dest)

        self.assertTrue(os.path.exists(result_path))
        with open(result_path, encoding="utf-8") as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data["metadata"]["project_name"], "Test")

    def test_read_history_file_validates(self):
        """Verify that read_history_file loads and validates a standard JSON history file."""
        data = {
            "metadata": {"project_name": "Valid", "hours_base": 7, "minutes_base": 45},
            "records": {"2026-01-01": {"hours": 8, "minutes": 0, "difference": 15}},
        }
        path = os.path.join(self.tmpdir.name, "valid.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        loaded = io.read_history_file(path)
        self.assertEqual(loaded["metadata"]["project_name"], "Valid")

    def test_read_invalid_json_raises(self):
        """Verify that reading a corrupted JSON file raises a ValueError."""
        path = os.path.join(self.tmpdir.name, "bad.json")
        with open(path, "w") as f:
            f.write("{ invalid json")

        with self.assertRaises(ValueError):
            io.read_history_file(path)

    def test_validate_history_schema(self):
        """Verify strict schema validation for history structure."""
        # Missing metadata
        with self.assertRaises(ValueError):
            io.validate_history({"records": {}})

        # Invalid base hours
        bad_data = {
            "metadata": {"project_name": "X", "hours_base": -1, "minutes_base": 0},
            "records": {},
        }
        with self.assertRaises(ValueError):
            io.validate_history(bad_data)


if __name__ == "__main__":
    unittest.main()


class TestHistoryValidation(unittest.TestCase):
    def valid(self):
        return {
            "metadata": {"project_name": "P", "hours_base": 8, "minutes_base": 0},
            "records": {"2026-04-24": {"hours": 8, "minutes": 0, "difference": 0}},
        }

    def assert_rejected(self, data, fragment):
        with self.assertRaises(ValueError) as caught:
            io.validate_history(data)
        self.assertIn(fragment, str(caught.exception))

    def test_a_valid_history_passes(self):
        io.validate_history(self.valid())

    def test_each_rule_names_the_problem(self):
        cases = []
        data = self.valid()
        data["metadata"]["hours_base"] = -1
        cases.append((data, "hours_base"))
        data = self.valid()
        data["metadata"]["minutes_base"] = 60
        cases.append((data, "minutes_base"))
        data = self.valid()
        data["metadata"]["hours_base"] = True
        cases.append((data, "must be an integer"))
        data = self.valid()
        del data["metadata"]["project_name"]
        cases.append((data, "project_name"))
        data = self.valid()
        data["records"]["24/04/2026"] = {"hours": 1, "minutes": 0, "difference": 0}
        cases.append((data, "Invalid date key"))
        data = self.valid()
        data["records"]["2026-04-24"] = [8, 0]
        cases.append((data, "must be an object"))
        data = self.valid()
        del data["records"]["2026-04-24"]["difference"]
        cases.append((data, "missing required key: difference"))
        data = self.valid()
        data["records"]["2026-04-24"]["hours"] = "8"
        cases.append((data, "must be an integer"))
        data = self.valid()
        data["records"] = []
        cases.append((data, "Records must be an object"))
        cases.append(([], "must be a JSON object"))
        for data, fragment in cases:
            with self.subTest(fragment=fragment):
                self.assert_rejected(data, fragment)


class TestAtomicExport(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.data = {
            "metadata": {"project_name": "P", "hours_base": 8, "minutes_base": 0},
            "records": {},
        }

    def test_creates_missing_folders_and_leaves_no_temporary_file(self):
        destination = os.path.join(self.tmpdir.name, "a", "b", "history.json")
        io.export_history(self.data, destination)
        self.assertEqual(os.listdir(os.path.dirname(destination)), ["history.json"])

    def test_replaces_an_existing_file(self):
        destination = os.path.join(self.tmpdir.name, "history.json")
        with open(destination, "w", encoding="utf-8") as existing:
            existing.write("old")
        io.export_history(self.data, destination)
        with open(destination, encoding="utf-8") as written:
            self.assertEqual(json.load(written)["metadata"]["project_name"], "P")

    def test_an_invalid_history_is_never_written(self):
        destination = os.path.join(self.tmpdir.name, "history.json")
        with self.assertRaises(ValueError):
            io.export_history({"records": {}}, destination)
        self.assertFalse(os.path.exists(destination))

    def test_reading_a_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            io.read_history_file(os.path.join(self.tmpdir.name, "none.json"))

    def test_export_then_read_round_trips(self):
        destination = os.path.join(self.tmpdir.name, "history.json")
        io.export_history(self.data, destination)
        self.assertEqual(io.read_history_file(destination), self.data)

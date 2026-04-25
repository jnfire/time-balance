import unittest
import tempfile
import os
import json
import time_balance.utils.files as io

class TestImportExport(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_export_history_creates_file(self):
        """Verify that export_history correctly writes the provided dictionary to a JSON file."""
        data = {
            "metadata": {
                "project_name": "Test",
                "hours_base": 8,
                "minutes_base": 0
            },
            "records": {}
        }
        dest = os.path.join(self.tmpdir.name, "export.json")
        result_path = io.export_history(data, dest)
        
        self.assertTrue(os.path.exists(result_path))
        with open(result_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data["metadata"]["project_name"], "Test")

    def test_read_history_file_validates(self):
        """Verify that read_history_file loads and validates a standard JSON history file."""
        data = {
            "metadata": {"project_name": "Valid", "hours_base": 7, "minutes_base": 45},
            "records": {
                "2026-01-01": {"hours": 8, "minutes": 0, "difference": 15}
            }
        }
        path = os.path.join(self.tmpdir.name, "valid.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
            
        loaded = io.read_history_file(path)
        self.assertEqual(loaded["metadata"]["project_name"], "Valid")

    def test_read_invalid_json_raises(self):
        """Verify that reading a corrupted JSON file raises a ValueError."""
        path = os.path.join(self.tmpdir.name, "bad.json")
        with open(path, 'w') as f:
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
            "records": {}
        }
        with self.assertRaises(ValueError):
            io.validate_history(bad_data)

if __name__ == "__main__":
    unittest.main()

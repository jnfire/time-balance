import unittest
import tempfile
import os
import json
import time_balance as ch

class TestImportExport(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_export_history_creates_file(self):
        """Verify that export_history correctly writes the provided dictionary to a JSON file."""
        datos = {
            "metadata": {
                "project_name": "P1", 
                "hours_base": 7, 
                "minutes_base": 45, 
                "version": "1.0", 
                "language": "auto"
            },
            "records": {
                "2026-04-01": {"hours": 8, "minutes": 0, "difference": 15}
            }
        }
        export_path = os.path.join(self.tmpdir.name, 'export.json')
        written = ch.export_history(datos, export_path)
        
        self.assertTrue(os.path.exists(written))
        with open(written, 'r', encoding='utf-8') as f:
            contenido = json.load(f)
        self.assertEqual(contenido, datos)

    def test_read_history_file_validates(self):
        """Verify that read_history_file loads and validates a standard JSON history file."""
        datos = {
            "metadata": {
                "project_name": "Source", 
                "hours_base": 7, 
                "minutes_base": 45, 
                "version": "1.0", 
                "language": "auto"
            },
            "records": {
                "2026-04-01": {"hours": 9, "minutes": 0, "difference": 75}
            }
        }
        src_path = os.path.join(self.tmpdir.name, 'source.json')
        with open(src_path, 'w', encoding='utf-8') as f:
            json.dump(datos, f)

        res = ch.read_history_file(src_path)
        self.assertEqual(res, datos)

    def test_read_invalid_json_raises(self):
        """Verify that reading a corrupted JSON file raises a ValueError."""
        src_path = os.path.join(self.tmpdir.name, 'bad.json')
        with open(src_path, 'w', encoding='utf-8') as f:
            f.write('{ invalid json')
        with self.assertRaises(ValueError):
            ch.read_history_file(src_path)

    def test_validate_history_schema(self):
        """Verify strict schema validation for history structure."""
        # Missing required keys
        with self.assertRaisesRegex(ValueError, "missing required structured keys"):
            ch.io.validate_history({"records": {}})
        
        # Invalid hours_base type (string instead of int)
        bad_meta = {
            "metadata": {
                "project_name": "P", 
                "hours_base": "8", 
                "minutes_base": 0, 
                "version": "1.0"
            },
            "records": {}
        }
        with self.assertRaisesRegex(ValueError, "must be an integer"):
            ch.io.validate_history(bad_meta)
        
        # Invalid minutes range
        bad_minutes = {
            "metadata": {
                "project_name": "P", 
                "hours_base": 8, 
                "minutes_base": 60, 
                "version": "1.0"
            },
            "records": {}
        }
        with self.assertRaisesRegex(ValueError, "between 0 and 59"):
            ch.io.validate_history(bad_minutes)

if __name__ == '__main__':
    unittest.main()

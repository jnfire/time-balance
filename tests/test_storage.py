import unittest
import tempfile
import os
import json
import time_balance as ch

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self._orig_cwd = os.getcwd()
        os.chdir(self.tmpdir.name)
        # Patch constants for tests
        self._orig_archivo = ch.constants.ARCHIVO_DATOS
        self.data_file = os.path.join(self.tmpdir.name, 'historial_horas.json')
        ch.constants.ARCHIVO_DATOS = self.data_file
        
        # Clear env var
        self._orig_env = os.environ.get('HISTORIAL_PATH')
        if 'HISTORIAL_PATH' in os.environ:
            del os.environ['HISTORIAL_PATH']

    def tearDown(self):
        os.chdir(self._orig_cwd)
        ch.constants.ARCHIVO_DATOS = self._orig_archivo
        if self._orig_env:
            os.environ['HISTORIAL_PATH'] = self._orig_env
        self.tmpdir.cleanup()

    def test_load_data_no_file(self):
        fake = os.path.join(self.tmpdir.name, "non_existent.json")
        ch.constants.ARCHIVO_DATOS = fake
        res = ch.load_data()
        self.assertIn("metadata", res)
        self.assertEqual(res["records"], {})

    def test_save_and_load_roundtrip(self):
        data = {
            "metadata": {
                "project_name": "Test Project",
                "hours_base": 8,
                "minutes_base": 0,
                "version": "1.0",
                "language": "auto"
            },
            "records": {
                "2026-01-01": {"hours": 8, "minutes": 0, "difference": 0}
            }
        }
        ch.save_data(data)
        loaded = ch.load_data()
        self.assertEqual(loaded, data)

    def test_resolve_file_path_priorities(self):
        # 1. Argument
        arg_path = os.path.join(self.tmpdir.name, "arg.json")
        self.assertEqual(ch._resolve_file_path(arg_path), os.path.abspath(arg_path))
        
        # 2. Env Var
        env_path = os.path.join(self.tmpdir.name, "env.json")
        os.environ['HISTORIAL_PATH'] = env_path
        self.assertEqual(ch._resolve_file_path(), os.path.abspath(env_path))
        del os.environ['HISTORIAL_PATH']
        
        # 3. Default
        self.assertEqual(ch._resolve_file_path(), os.path.abspath(self.data_file))

if __name__ == "__main__":
    unittest.main()

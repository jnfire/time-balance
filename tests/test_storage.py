import unittest
import tempfile
import os
from datetime import datetime
import time_balance as ch

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self._orig_cwd = os.getcwd()
        os.chdir(self.tmpdir.name)
        # Parchear constante para tests
        self._orig_archivo = ch.constants.ARCHIVO_DATOS
        self.data_file = os.path.join(self.tmpdir.name, 'historial_horas.json')
        ch.constants.ARCHIVO_DATOS = self.data_file
        
        # Limpiar env var
        self._orig_env = os.environ.get('HISTORIAL_PATH')
        if 'HISTORIAL_PATH' in os.environ:
            del os.environ['HISTORIAL_PATH']

    def tearDown(self):
        os.chdir(self._orig_cwd)
        ch.constants.ARCHIVO_DATOS = self._orig_archivo
        if self._orig_env:
            os.environ['HISTORIAL_PATH'] = self._orig_env
        self.tmpdir.cleanup()

    def test_cargar_no_file(self):
        fake = os.path.join(self.tmpdir.name, "non_existent.json")
        ch.constants.ARCHIVO_DATOS = fake
        self.assertEqual(ch.cargar_datos(), {})

    def test_cargar_invalid_json(self):
        fname = os.path.join(self.tmpdir.name, "invalid.json")
        with open(fname, "w") as f:
            f.write("{ bad json")
        ch.constants.ARCHIVO_DATOS = fname
        self.assertEqual(ch.cargar_datos(), {})

    def test_guardar_and_load_roundtrip(self):
        data = {"2026-01-01": {"horas": 8, "minutos": 0, "diferencia": 15}}
        ch.guardar_datos(data)
        loaded = ch.cargar_datos()
        self.assertEqual(loaded, data)

    def test_resolver_archivo_prioridades(self):
        # 1. Argumento
        arg_path = os.path.join(self.tmpdir.name, "arg.json")
        self.assertEqual(ch._resolver_archivo(arg_path), os.path.abspath(arg_path))
        
        # 2. Env Var
        env_path = os.path.join(self.tmpdir.name, "env.json")
        os.environ['HISTORIAL_PATH'] = env_path
        self.assertEqual(ch._resolver_archivo(), os.path.abspath(env_path))
        del os.environ['HISTORIAL_PATH']
        
        # 3. Default
        self.assertEqual(ch._resolver_archivo(), os.path.abspath(self.data_file))

if __name__ == "__main__":
    unittest.main()

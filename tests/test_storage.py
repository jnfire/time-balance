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
        res = ch.cargar_datos()
        self.assertIn("metadata", res)
        self.assertEqual(res["registros"], {})

    def test_migracion_formato_antiguo(self):
        # Creamos un archivo con el formato plano antiguo
        datos_viejos = {"2026-01-01": {"horas": 8, "minutos": 0, "diferencia": 15}}
        with open(self.data_file, "w") as f:
            json.dump(datos_viejos, f)
        
        res = ch.cargar_datos()
        self.assertEqual(res["metadata"]["project_name"], "General")
        self.assertEqual(res["registros"], datos_viejos)

    def test_guardar_and_load_roundtrip(self):
        data = {
            "metadata": {
                "project_name": "Test Project",
                "horas_base": 8,
                "minutos_base": 0,
                "version": "1.0"
            },
            "registros": {
                "2026-01-01": {"horas": 8, "minutos": 0, "diferencia": 0}
            }
        }
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

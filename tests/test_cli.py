import unittest
import tempfile
import os
import io
from unittest import mock
import time_balance as ch

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self._orig_cwd = os.getcwd()
        os.chdir(self.tmpdir.name)
        self._orig_archivo = ch.constants.ARCHIVO_DATOS
        self.data_file = os.path.join(self.tmpdir.name, 'historial_horas.json')
        ch.constants.ARCHIVO_DATOS = self.data_file

    def tearDown(self):
        os.chdir(self._orig_cwd)
        ch.constants.ARCHIVO_DATOS = self._orig_archivo
        self.tmpdir.cleanup()

    def test_registrar_jornada_overwrite_cancel(self):
        datos = {"2026-01-01": {"horas": 7, "minutos": 0, "diferencia": -45}}
        # inputs: date, confirmation 'n' (cancel)
        with mock.patch('builtins.input', side_effect=["2026-01-01", "n"]):
            ch.registrar_jornada(datos)
        self.assertEqual(datos["2026-01-01"]["horas"], 7)

    def test_registrar_jornada_overwrite_confirm(self):
        datos = {"2026-01-01": {"horas": 7, "minutos": 0, "diferencia": -45}}
        # inputs: date, confirmation 's', horas '8', minutos '0'
        with mock.patch('builtins.input', side_effect=["2026-01-01", "s", "8", "0"]):
            ch.registrar_jornada(datos)
        self.assertEqual(datos["2026-01-01"]["horas"], 8)
        self.assertEqual(ch.cargar_datos()["2026-01-01"]["horas"], 8)

    def test_ver_historial_output(self):
        datos = {
            "2026-01-01": {"horas": 8, "minutos": 0, "diferencia": 15},
            "2026-01-02": {"horas": 7, "minutos": 0, "diferencia": -45},
            "2026-01-03": {"horas": 9, "minutos": 0, "diferencia": 75},
            "2026-01-04": {"horas": 6, "minutos": 30, "diferencia": -75},
            "2026-01-05": {"horas": 7, "minutos": 45, "diferencia": 0}
        }
        buf = io.StringIO()
        with mock.patch('sys.stdout', buf):
            ch.ver_historial(datos)
        out = buf.getvalue()
        self.assertIn("--- Últimos 5 registros ---", out)
        self.assertIn("2026-01-05", out)
        count_dates = sum(1 for line in out.splitlines() if line.startswith("2026-"))
        self.assertEqual(count_dates, 5)

if __name__ == "__main__":
    unittest.main()

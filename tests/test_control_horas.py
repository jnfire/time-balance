import unittest
import tempfile
import os
import io
from unittest import mock

import time_balance as ch

class TestControlHoras(unittest.TestCase):
    def setUp(self):
        # Crear un directorio temporal y usarlo como cwd y como lugar del archivo de datos
        self._orig_cwd = os.getcwd()
        self._orig_archivo = getattr(ch, 'ARCHIVO_DATOS', None)
        self.tmpdir = tempfile.TemporaryDirectory()
        os.chdir(self.tmpdir.name)
        # Archivo de datos en el tempdir
        self.data_file = os.path.join(self.tmpdir.name, 'historial_horas.json')
        ch.ARCHIVO_DATOS = self.data_file

    def tearDown(self):
        # Restaurar cwd y ARCHIVO_DATOS
        os.chdir(self._orig_cwd)
        if self._orig_archivo is not None:
            ch.ARCHIVO_DATOS = self._orig_archivo
        self.tmpdir.cleanup()

    def test_formatear_tiempo_positive(self):
        self.assertEqual(ch.formatear_tiempo(125), "2h 5m")

    def test_formatear_tiempo_zero(self):
        self.assertEqual(ch.formatear_tiempo(0), "0h 0m")

    def test_formatear_tiempo_negative(self):
        self.assertEqual(ch.formatear_tiempo(-75), "-1h 15m")

    def test_calcular_saldo_total(self):
        data = {"a":{"diferencia": 10}, "b":{"diferencia": -5}}
        self.assertEqual(ch.calcular_saldo_total(data), 5)

    def test_cargar_no_file(self):
        with tempfile.TemporaryDirectory() as d:
            fake = os.path.join(d, "nope.json")
            ch.ARCHIVO_DATOS = fake
            self.assertEqual(ch.cargar_datos(), {})

    def test_cargar_invalid_json(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
            f.write("{ invalid json")
            fname = f.name
        try:
            ch.ARCHIVO_DATOS = fname
            self.assertEqual(ch.cargar_datos(), {})
        finally:
            if os.path.exists(fname):
                os.remove(fname)

    def test_guardar_and_load_roundtrip(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
            fname = f.name
        if os.path.exists(fname):
            os.remove(fname)
        try:
            ch.ARCHIVO_DATOS = fname
            data = {"2026-01-01":{"horas":8,"minutos":0,"diferencia":15}}
            ch.guardar_datos(data)
            loaded = ch.cargar_datos()
            self.assertEqual(loaded, data)
        finally:
            if os.path.exists(fname):
                os.remove(fname)

    def test_registrar_jornada_overwrite_cancel(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
            fname = f.name
        if os.path.exists(fname):
            os.remove(fname)
        ch.ARCHIVO_DATOS = fname
        datos = {"2026-01-01":{"horas":7,"minutos":0,"diferencia":-45}}
        # inputs: date, confirmation 'n' (cancel)
        with mock.patch('builtins.input', side_effect=["2026-01-01", "n"]):
            ch.registrar_jornada(datos)
        # should remain unchanged
        self.assertEqual(datos["2026-01-01"]["horas"] , 7)

    def test_registrar_jornada_overwrite_confirm(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
            fname = f.name
        if os.path.exists(fname):
            os.remove(fname)
        ch.ARCHIVO_DATOS = fname
        datos = {"2026-01-01":{"horas":7,"minutos":0,"diferencia":-45}}
        # inputs: date, confirmation 's', horas '8', minutos '0'
        with mock.patch('builtins.input', side_effect=["2026-01-01", "s", "8", "0"]):
            ch.registrar_jornada(datos)
        # check updated
        self.assertEqual(datos["2026-01-01"]["horas"], 8)
        # and file persisted
        loaded = ch.cargar_datos()
        self.assertEqual(loaded["2026-01-01"]["horas"], 8)

    def test_ver_historial_output(self):
        datos = {
            "2026-01-01":{"horas":8,"minutos":0,"diferencia":15},
            "2026-01-02":{"horas":7,"minutos":0,"diferencia":-45},
            "2026-01-03":{"horas":9,"minutos":0,"diferencia":75},
            "2026-01-04":{"horas":6,"minutos":30,"diferencia":-75},
            "2026-01-05":{"horas":7,"minutos":45,"diferencia":0},
            "2026-01-06":{"horas":8,"minutos":30,"diferencia":45}
        }
        buf = io.StringIO()
        with mock.patch('sys.stdout', buf):
            ch.ver_historial(datos)
        out = buf.getvalue()
        # Should include header and five most recent dates (sorted reverse)
        self.assertIn("--- Últimos 5 registros ---", out)
        # most recent should be 2026-01-06
        self.assertIn("2026-01-06", out)
        # count lines with dates (simple check)
        count_dates = sum(1 for line in out.splitlines() if line.startswith("2026-"))
        self.assertEqual(count_dates, 5)

if __name__ == "__main__":
    unittest.main()

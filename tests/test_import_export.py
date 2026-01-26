import unittest
import tempfile
import os
import json
import glob

import time_balance as ch

class TestImportExport(unittest.TestCase):
    def setUp(self):
        # directorio temporal por test
        self.tmpdir = tempfile.TemporaryDirectory()
        self.orig_archivo = getattr(ch, 'ARCHIVO_DATOS', None)
        self.dest_file = os.path.join(self.tmpdir.name, 'historial_horas.json')
        ch.ARCHIVO_DATOS = self.dest_file

    def tearDown(self):
        # restaurar
        if self.orig_archivo is not None:
            ch.ARCHIVO_DATOS = self.orig_archivo
        self.tmpdir.cleanup()

    def test_exportar_historial_crea_archivo(self):
        # Preparar datos en archivo destino
        datos = {"2026-01-01": {"horas": 8, "minutos": 0, "diferencia": 15}}
        ch.guardar_datos(datos)

        # Exportar a un archivo concreto
        export_path = os.path.join(self.tmpdir.name, 'export.json')
        written = ch.exportar_historial(export_path)
        self.assertTrue(os.path.exists(written))
        with open(written, 'r', encoding='utf-8') as f:
            contenido = json.load(f)
        self.assertEqual(contenido, datos)

    def test_importar_merge_prefiere_fuente(self):
        # Destino: tiene una fecha A y B
        destino = {"2026-01-01": {"horas": 7, "minutos": 0, "diferencia": -45},
                   "2026-01-02": {"horas": 6, "minutos": 30, "diferencia": -75}}
        ch.guardar_datos(destino)

        # Fuente: tiene fecha A (conflicto) and C (nuevo)
        fuente = {"2026-01-01": {"horas": 9, "minutos": 0, "diferencia": 75},
                  "2026-01-03": {"horas": 8, "minutos": 15, "diferencia": 30}}
        src_path = os.path.join(self.tmpdir.name, 'fuente.json')
        with open(src_path, 'w', encoding='utf-8') as f:
            json.dump(fuente, f)

        # Importar en modo merge -> la fuente sobrescribe en conflicto
        res = ch.importar_historial(src_path, modo='merge')

        # Comprobaciones
        self.assertIn('2026-01-03', res)
        self.assertEqual(res['2026-01-01']['horas'], 9)  # valor de la fuente
        # Y archivo destino refleja el merge
        loaded = ch.cargar_datos()
        self.assertEqual(loaded['2026-01-01']['horas'], 9)
        self.assertIn('2026-01-02', loaded)

    def test_importar_overwrite_crea_backup_y_sobreescribe(self):
        # Destino inicial
        destino = {"2026-01-01": {"horas": 7, "minutos": 0, "diferencia": -45}}
        ch.guardar_datos(destino)

        # Fuente nueva
        fuente = {"2026-02-01": {"horas": 8, "minutos": 0, "diferencia": 15}}
        src_path = os.path.join(self.tmpdir.name, 'fuente2.json')
        with open(src_path, 'w', encoding='utf-8') as f:
            json.dump(fuente, f)

        # Import overwrite
        res = ch.importar_historial(src_path, modo='overwrite')

        # Now backup should exist in tmpdir (archivo.bak.*)
        bak_pattern = self.dest_file + '.bak.*'
        bak_files = glob.glob(bak_pattern)
        self.assertTrue(len(bak_files) >= 1, f"No se encontró backup con patrón {bak_pattern}")

        # El archivo destino ahora debe ser igual a la fuente
        loaded = ch.cargar_datos()
        self.assertEqual(loaded, fuente)

    def test_importar_json_invalido_lanza(self):
        src_path = os.path.join(self.tmpdir.name, 'bad.json')
        with open(src_path, 'w', encoding='utf-8') as f:
            f.write('{ invalid json')
        with self.assertRaises(ValueError):
            ch.importar_historial(src_path, modo='overwrite')

if __name__ == '__main__':
    unittest.main()

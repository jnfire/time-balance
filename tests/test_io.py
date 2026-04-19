import unittest
import tempfile
import os
import json
import glob

import time_balance as ch

class TestImportExport(unittest.TestCase):
    def setUp(self):
        # directory per test
        self.tmpdir = tempfile.TemporaryDirectory()
        self.orig_archivo = getattr(ch.constants, 'ARCHIVO_DATOS', None)
        # Clear env var to avoid CI flakes
        self._orig_historial_path = os.environ.get('HISTORIAL_PATH')
        os.environ.pop('HISTORIAL_PATH', None)
        self.dest_file = os.path.join(self.tmpdir.name, 'historial_horas.json')
        ch.constants.ARCHIVO_DATOS = self.dest_file

    def tearDown(self):
        if self.orig_archivo is not None:
            ch.constants.ARCHIVO_DATOS = self.orig_archivo
        if self._orig_historial_path is not None:
            os.environ['HISTORIAL_PATH'] = self._orig_historial_path
        else:
            os.environ.pop('HISTORIAL_PATH', None)
        self.tmpdir.cleanup()

    def test_export_history_creates_file(self):
        datos = {
            "metadata": {"project_name": "P1", "hours_base": 7, "minutes_base": 45, "version": "1.0", "language": "auto"},
            "records": {"2026-04-01": {"hours": 8, "minutes": 0, "difference": 15}}
        }
        ch.save_data(datos)

        export_path = os.path.join(self.tmpdir.name, 'export.json')
        written = ch.export_history(export_path)
        self.assertTrue(os.path.exists(written))
        with open(written, 'r', encoding='utf-8') as f:
            contenido = json.load(f)
        self.assertEqual(contenido, datos)

    def test_import_merge_prefers_source(self):
        destino = {
            "metadata": {"project_name": "Dest", "hours_base": 7, "minutes_base": 45, "version": "1.0", "language": "auto"},
            "records": {
                "2026-04-01": {"hours": 7, "minutes": 0, "difference": -45},
                "2026-04-02": {"hours": 6, "minutes": 30, "difference": -75}
            }
        }
        ch.save_data(destino)

        # Source: Correct v2 format
        fuente_v2 = {
            "metadata": {"project_name": "Source", "hours_base": 7, "minutes_base": 45, "version": "1.0"},
            "records": {
                "2026-04-01": {"hours": 9, "minutes": 0, "difference": 75},
                "2026-04-03": {"hours": 8, "minutes": 15, "difference": 30}
            }
        }
        src_path = os.path.join(self.tmpdir.name, 'source.json')
        with open(src_path, 'w', encoding='utf-8') as f:
            json.dump(fuente_v2, f)

        res = ch.import_history(src_path, mode=ch.MODE_MERGE)

        self.assertIn('2026-04-03', res["records"])
        self.assertEqual(res["records"]['2026-04-01']['hours'], 9)
        loaded = ch.load_data()
        self.assertEqual(loaded["records"]['2026-04-01']['hours'], 9)
        self.assertIn('2026-04-02', loaded["records"])

    def test_import_overwrite_creates_backup(self):
        destino = {
            "metadata": {"project_name": "Dest", "hours_base": 7, "minutes_base": 45, "version": "1.0", "language": "auto"},
            "records": {"2026-04-01": {"hours": 7, "minutes": 0, "difference": -45}}
        }
        ch.save_data(destino)

        fuente = {
            "metadata": {"project_name": "New", "hours_base": 8, "minutes_base": 0, "version": "1.0", "language": "auto"},
            "records": {"2026-05-01": {"hours": 8, "minutes": 0, "difference": 15}}
        }
        src_path = os.path.join(self.tmpdir.name, 'source2.json')
        with open(src_path, 'w', encoding='utf-8') as f:
            json.dump(fuente, f)

        ch.import_history(src_path, mode=ch.MODE_OVERWRITE)

        bak_pattern = self.dest_file + '.bak.*'
        bak_files = glob.glob(bak_pattern)
        self.assertTrue(len(bak_files) >= 1)

        loaded = ch.load_data()
        self.assertEqual(loaded, fuente)

    def test_import_invalid_json_raises(self):
        src_path = os.path.join(self.tmpdir.name, 'bad.json')
        with open(src_path, 'w', encoding='utf-8') as f:
            f.write('{ invalid json')
        with self.assertRaises(ValueError):
            ch.import_history(src_path, mode=ch.MODE_OVERWRITE)

if __name__ == '__main__':
    unittest.main()

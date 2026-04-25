import unittest
import tempfile
import pathlib
import sqlite3
from time_balance.database.manager import DatabaseManager

class TestBalanceCache(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = pathlib.Path(self.tmp_dir.name) / "test_cache.db"
        self.db = DatabaseManager(self.db_path)
        self.project_id = 1

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_cache_activation_on_first_read(self):
        """Verifica que el balance pasa de NULL a valor real tras la primera lectura."""
        # 1. Insertamos registro directamente por SQL para no disparar el cache update del Manager
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO records (project_id, date, hours, minutes, difference) VALUES (1, '2026-01-01', 8, 0, 15)")
        conn.commit()
        conn.close()

        # 2. Verificamos que el cache es NULL
        projects = self.db.get_projects()
        self.assertIsNone(projects[0]['total_balance'])

        # 3. Llamamos a get_total_balance (debe calcular y cachear)
        balance = self.db.get_total_balance(self.project_id)
        self.assertEqual(balance, 15)

        # 4. Verificamos que ahora el cache NO es NULL
        project = self.db.get_project_by_id(self.project_id)
        self.assertEqual(project['total_balance'], 15)

    def test_cache_update_on_upsert(self):
        """Verifica que el balance se actualiza atómicamente al insertar o actualizar."""
        # Forzamos cache a 0
        self.db.recalculate_project_balance(self.project_id)
        
        # Insertamos nuevo (0 + 15 = 15)
        self.db.upsert_record(self.project_id, "2026-01-01", 8, 0, 15)
        self.assertEqual(self.db.get_project_by_id(self.project_id)['total_balance'], 15)

        # Actualizamos existente (15 - 15 + 30 = 30)
        self.db.upsert_record(self.project_id, "2026-01-01", 8, 15, 30)
        self.assertEqual(self.db.get_project_by_id(self.project_id)['total_balance'], 30)

    def test_cache_update_on_delete(self):
        """Verifica que el balance se actualiza correctamente al borrar registros."""
        self.db.upsert_record(self.project_id, "2026-01-01", 8, 15, 30)
        self.db.recalculate_project_balance(self.project_id) # Cache en 30
        
        self.db.delete_record(self.project_id, "2026-01-01")
        self.assertEqual(self.db.get_project_by_id(self.project_id)['total_balance'], 0)

    def test_manual_recalculate(self):
        """Verifica que el recálculo forzado corrige discrepancias."""
        self.db.upsert_record(self.project_id, "2026-01-01", 8, 0, 15)
        
        # Corrompemos el cache manualmente por SQL
        conn = sqlite3.connect(self.db_path)
        conn.execute("UPDATE projects SET total_balance = 999 WHERE id = 1")
        conn.commit()
        conn.close()
        
        self.assertEqual(self.db.get_total_balance(self.project_id), 999)
        
        # Recalculamos
        self.db.recalculate_project_balance(self.project_id)
        self.assertEqual(self.db.get_total_balance(self.project_id), 15)

    def test_reset_balance(self):
        """Verifica que reset_project_balance vuelve a poner el estado en NULL."""
        self.db.upsert_record(self.project_id, "2026-01-01", 8, 0, 15)
        self.db.recalculate_project_balance(self.project_id)
        
        self.db.reset_project_balance(self.project_id)
        project = self.db.get_project_by_id(self.project_id)
        self.assertIsNone(project['total_balance'])

    def test_incremental_update_safety(self):
        """Escenario: Tenemos un balance acumulado de muchos días."""
        for i in range(1, 11):
            self.db.upsert_record(self.project_id, f"2026-01-{i:02d}", 8, 0, 15)
        
        expected = 15 * 10
        self.assertEqual(self.db.get_total_balance(self.project_id), expected)
        
        # Borramos el último
        self.db.delete_record(self.project_id, "2026-01-10")
        self.assertEqual(self.db.get_total_balance(self.project_id), expected - 15)

    def test_sign_flip_safety(self):
        """Verifica que el balance se mantiene correcto incluso cuando un registro
        pasa de positivo a negativo o viceversa."""
        self.db.recalculate_project_balance(self.project_id) # Cache 0
        
        # +15
        self.db.upsert_record(self.project_id, "2026-01-01", 8, 0, 15)
        self.assertEqual(self.db.get_total_balance(self.project_id), 15)
        
        # -45 (Cambio: 15 -> -45 => delta de -60)
        self.db.upsert_record(self.project_id, "2026-01-01", 7, 0, -45)
        self.assertEqual(self.db.get_total_balance(self.project_id), -45)

if __name__ == "__main__":
    unittest.main()

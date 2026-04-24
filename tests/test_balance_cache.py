import unittest
import tempfile
import pathlib
import sqlite3
from time_balance.storage import DatabaseManager

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
        # Insertamos registros directamente para que total_balance siga siendo NULL
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO records (project_id, date, hours, minutes, difference) VALUES (?, ?, ?, ?, ?)",
                         (self.project_id, "2026-04-01", 8, 0, 15))
            conn.execute("INSERT INTO records (project_id, date, hours, minutes, difference) VALUES (?, ?, ?, ?, ?)",
                         (self.project_id, "2026-04-02", 9, 0, 75))
            
            # Verificamos que en la DB está a NULL
            cursor = conn.execute("SELECT total_balance FROM projects WHERE id = ?", (self.project_id,))
            self.assertIsNone(cursor.fetchone()[0])

        # Al pedir el balance, debe calcularse y activarse la caché
        balance = self.db.get_total_balance(self.project_id)
        self.assertEqual(balance, 90)

        # Verificamos que ahora ya no es NULL en la DB
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT total_balance FROM projects WHERE id = ?", (self.project_id,))
            self.assertEqual(cursor.fetchone()[0], 90)

    def test_cache_update_on_upsert(self):
        """Verifica que el balance se actualiza atómicamente al insertar o actualizar."""
        # Forzamos activación de caché (debería ser 0 inicialmente)
        self.db.get_total_balance(self.project_id)
        
        # Insertar nuevo registro
        self.db.upsert_record(self.project_id, "2026-04-01", 8, 0, 15)
        self.assertEqual(self.db.get_total_balance(self.project_id), 15)
        
        # Insertar otro
        self.db.upsert_record(self.project_id, "2026-04-02", 9, 0, 75)
        self.assertEqual(self.db.get_total_balance(self.project_id), 90)
        
        # Actualizar uno existente (de 15 a -10, diferencia delta de -25)
        self.db.upsert_record(self.project_id, "2026-04-01", 7, 0, -10)
        # Total debería ser: 90 (anterior) - 15 (viejo) + (-10) (nuevo) = 65
        self.assertEqual(self.db.get_total_balance(self.project_id), 65)

    def test_cache_update_on_delete(self):
        """Verifica que el balance se actualiza correctamente al borrar registros."""
        self.db.upsert_record(self.project_id, "2026-04-01", 8, 0, 20)
        self.db.upsert_record(self.project_id, "2026-04-02", 8, 0, 30)
        self.assertEqual(self.db.get_total_balance(self.project_id), 50)
        
        # Borrar uno
        self.db.delete_record(self.project_id, "2026-04-01")
        self.assertEqual(self.db.get_total_balance(self.project_id), 30)
        
        # Borrar el último
        self.db.delete_record(self.project_id, "2026-04-02")
        self.assertEqual(self.db.get_total_balance(self.project_id), 0)

    def test_manual_recalculate(self):
        """Verifica que el recálculo forzado corrige discrepancias."""
        self.db.upsert_record(self.project_id, "2026-04-01", 8, 0, 100)
        self.assertEqual(self.db.get_total_balance(self.project_id), 100)
        
        # Simulamos una corrupción de datos manual en la caché
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE projects SET total_balance = 999 WHERE id = ?", (self.project_id,))
        
        self.assertEqual(self.db.get_total_balance(self.project_id), 999) # La caché manda
        
        # Ejecutamos auditoría
        corrected = self.db.recalculate_project_balance(self.project_id)
        self.assertEqual(corrected, 100)
        self.assertEqual(self.db.get_total_balance(self.project_id), 100)

    def test_reset_balance(self):
        """Verifica que reset_project_balance vuelve a poner el estado en NULL."""
        self.db.upsert_record(self.project_id, "2026-04-01", 8, 0, 100)
        self.db.get_total_balance(self.project_id) # Activamos caché
        
        # Verificamos que no es NULL
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT total_balance FROM projects WHERE id = ?", (self.project_id,))
            self.assertIsNotNone(cursor.fetchone()[0])
            
        # Reseteamos
        self.db.reset_project_balance(self.project_id)
        
        # Verificamos que vuelve a ser NULL
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT total_balance FROM projects WHERE id = ?", (self.project_id,))
            self.assertIsNone(cursor.fetchone()[0])

    def test_incremental_update_safety(self):
        """
        Escenario: Tenemos un balance acumulado de muchos días.
        Añadimos un día nuevo, lo editamos varias veces y verificamos que 
        el balance previo se mantiene constante y solo cambia el delta del día editado.
        """
        # 1. Creamos un histórico sólido (10 días con 10 min de extra cada uno = 100 min)
        base_days = 10
        for i in range(base_days):
            self.db.upsert_record(self.project_id, f"2026-01-{i+1:02d}", 8, 0, 10)
        
        base_balance = self.db.get_total_balance(self.project_id)
        self.assertEqual(base_balance, 100)
        
        # 2. Añadimos el día "objetivo"
        target_date = "2026-02-01"
        self.db.upsert_record(self.project_id, target_date, 8, 0, 50) # +50 min
        self.assertEqual(self.db.get_total_balance(self.project_id), 150)
        
        # 3. Editamos el día objetivo VARIAS veces
        # Cambio a +20 min (el total debería bajar 30 min -> 120)
        self.db.upsert_record(self.project_id, target_date, 8, 0, 20)
        self.assertEqual(self.db.get_total_balance(self.project_id), 120)
        
        # Cambio a -10 min (el total debería bajar otros 30 min -> 90)
        self.db.upsert_record(self.project_id, target_date, 8, 0, -10)
        self.assertEqual(self.db.get_total_balance(self.project_id), 90)
        
        # 4. Verificación final de integridad:
        # Borramos el día objetivo. El balance debería volver EXACTAMENTE a los 100 iniciales.
        # Si hubiera cualquier error de arrastre, este número bailaría.
        self.db.delete_record(self.project_id, target_date)
        self.assertEqual(self.db.get_total_balance(self.project_id), 100)

    def test_sign_flip_safety(self):
        """
        Verifica que el balance se mantiene correcto incluso cuando un registro
        cambia de signo (de positivo a negativo y viceversa).
        """
        # 1. Estado inicial
        self.db.upsert_record(self.project_id, "2026-03-01", 8, 0, 100)
        self.assertEqual(self.db.get_total_balance(self.project_id), 100)
        
        # 2. Añadimos un día muy positivo (+60 min)
        target_date = "2026-03-02"
        self.db.upsert_record(self.project_id, target_date, 9, 0, 60)
        self.assertEqual(self.db.get_total_balance(self.project_id), 160)
        
        # 3. Flip: Cambiamos ese día a muy negativo (-40 min)
        # Debería ser: 160 - 60 (quitar positivo) - 40 (poner negativo) = 60
        self.db.upsert_record(self.project_id, target_date, 7, 0, -40)
        self.assertEqual(self.db.get_total_balance(self.project_id), 60)
        
        # 4. Flip de vuelta: Cambiamos a positivo moderado (+10 min)
        # Debería ser: 60 - (-40) (anular deuda) + 10 (poner nuevo) = 110
        self.db.upsert_record(self.project_id, target_date, 8, 0, 10)
        self.assertEqual(self.db.get_total_balance(self.project_id), 110)
        
        # 5. Borrado final: Volver al estado inicial
        self.db.delete_record(self.project_id, target_date)
        self.assertEqual(self.db.get_total_balance(self.project_id), 100)

if __name__ == "__main__":
    unittest.main()

import unittest
import time_balance as ch

class TestCore(unittest.TestCase):
    def test_formatear_tiempo_positive(self):
        self.assertEqual(ch.formatear_tiempo(125), "2h 5m")

    def test_formatear_tiempo_zero(self):
        self.assertEqual(ch.formatear_tiempo(0), "0h 0m")

    def test_formatear_tiempo_negative(self):
        self.assertEqual(ch.formatear_tiempo(-75), "-1h 15m")

    def test_calcular_saldo_total(self):
        data = {"a": {"diferencia": 10}, "b": {"diferencia": -5}}
        self.assertEqual(ch.calcular_saldo_total(data), 5)

if __name__ == "__main__":
    unittest.main()

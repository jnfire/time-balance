import unittest
import time_balance as ch

class TestCore(unittest.TestCase):
    def test_format_time_positive(self):
        self.assertEqual(ch.format_time(125), "2h 5m")

    def test_format_time_zero(self):
        self.assertEqual(ch.format_time(0), "0h 0m")

    def test_format_time_negative(self):
        self.assertEqual(ch.format_time(-75), "-1h 15m")

    def test_calculate_total_balance(self):
        # Updated key from 'diferencia' to 'difference'
        data = {"a": {"difference": 10}, "b": {"difference": -5}}
        self.assertEqual(ch.calculate_total_balance(data), 5)

if __name__ == "__main__":
    unittest.main()

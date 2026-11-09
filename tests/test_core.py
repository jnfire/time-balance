import unittest
import time_balance.utils.calculations as core

class TestCore(unittest.TestCase):
    def test_format_time_positive(self):
        self.assertEqual(core.format_time(60), "+1h")
        self.assertEqual(core.format_time(125), "+2h 5m")

    def test_format_time_negative(self):
        self.assertEqual(core.format_time(-60), "-1h")
        self.assertEqual(core.format_time(-5), "-5m")

    def test_format_duration(self):
        self.assertEqual(core.format_duration(8, 0), "8h")
        self.assertEqual(core.format_duration(7, 45), "7h 45m")
        self.assertEqual(core.format_duration(0, 25), "25m")
        self.assertEqual(core.format_duration(0, 0), "0m")

    def test_format_time_zero(self):
        self.assertEqual(core.format_time(0), "0m")

    def test_calculate_total_balance(self):
        records = {
            "2026-01-01": {"difference": 15},
            "2026-01-02": {"difference": -10}
        }
        self.assertEqual(core.calculate_total_balance_from_records(records), 5)

if __name__ == "__main__":
    unittest.main()

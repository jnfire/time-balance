import unittest

from time_balance.utils.pagination import clamp_page, page_count
from time_balance.utils.validation import InputError, parse_date, parse_duration


class TestParseDate(unittest.TestCase):
    def test_accepts_iso_dates(self):
        self.assertEqual(parse_date("2026-04-24"), "2026-04-24")
        self.assertEqual(parse_date("  2026-04-24 "), "2026-04-24")

    def test_normalizes_unpadded_parts(self):
        self.assertEqual(parse_date("2026-4-5"), "2026-04-05")

    def test_rejects_everything_else(self):
        for text in ("", "tomorrow", "24-04-2026", "2026-02-30", "2026-13-01"):
            with self.subTest(text=text):
                self.assertIsNone(parse_date(text))


class TestParseDuration(unittest.TestCase):
    def test_valid_durations(self):
        self.assertEqual(parse_duration("8", "15"), (8, 15))
        self.assertEqual(parse_duration("0", "0"), (0, 0))
        self.assertEqual(parse_duration("24", "0"), (24, 0))

    def test_non_integers_are_reported(self):
        for hours, minutes in (("a", "0"), ("8", ""), ("7.5", "0")):
            with (
                self.subTest(hours=hours, minutes=minutes),
                self.assertRaises(InputError) as caught,
            ):
                parse_duration(hours, minutes)
            self.assertEqual(caught.exception.message_key, "error_integers")

    def test_out_of_range_is_reported(self):
        for hours, minutes in (("-1", "0"), ("8", "60"), ("8", "-5"), ("24", "1"), ("99", "0")):
            with (
                self.subTest(hours=hours, minutes=minutes),
                self.assertRaises(InputError) as caught,
            ):
                parse_duration(hours, minutes)
            self.assertEqual(caught.exception.message_key, "error_range")


class TestPagination(unittest.TestCase):
    def test_page_count(self):
        self.assertEqual(page_count(0, 10), 0)
        self.assertEqual(page_count(1, 10), 1)
        self.assertEqual(page_count(10, 10), 1)
        self.assertEqual(page_count(11, 10), 2)

    def test_page_size_must_be_positive(self):
        with self.assertRaises(ValueError):
            page_count(5, 0)

    def test_clamp_page(self):
        self.assertEqual(clamp_page(5, 25, 10), 2)
        self.assertEqual(clamp_page(-1, 25, 10), 0)
        self.assertEqual(clamp_page(1, 25, 10), 1)
        self.assertEqual(clamp_page(3, 0, 10), 0)


if __name__ == "__main__":
    unittest.main()

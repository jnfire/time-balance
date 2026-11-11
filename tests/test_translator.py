import contextlib
import json
import pathlib
import string
import unittest
from unittest import mock

from time_balance.i18n import translator

LOCALES = pathlib.Path(translator.__file__).parent / "locales"


def placeholders(template: str) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(template) if name}


class TestLocaleFiles(unittest.TestCase):
    def setUp(self):
        self.english = json.loads((LOCALES / "en.json").read_text(encoding="utf-8"))
        self.spanish = json.loads((LOCALES / "es.json").read_text(encoding="utf-8"))

    def test_both_languages_define_the_same_keys(self):
        self.assertEqual(sorted(set(self.english) - set(self.spanish)), [])
        self.assertEqual(sorted(set(self.spanish) - set(self.english)), [])

    def test_the_translations_use_the_same_placeholders(self):
        for key, template in self.english.items():
            with self.subTest(key=key):
                self.assertEqual(placeholders(template), placeholders(self.spanish[key]))

    def test_no_translation_is_empty(self):
        for language in (self.english, self.spanish):
            for key, text in language.items():
                with self.subTest(key=key):
                    self.assertTrue(text.strip())


class TestTranslate(unittest.TestCase):
    def test_fills_placeholders(self):
        self.assertEqual(translator.translate("status_project", lang="en", name="X"), "Project: X")

    def test_unknown_key_returns_the_key(self):
        self.assertEqual(translator.translate("no_such_key", lang="en"), "no_such_key")

    def test_unknown_language_falls_back_to_english(self):
        self.assertEqual(translator.translate("status_project", lang="xx", name="X"), "Project: X")

    def test_missing_values_return_the_template(self):
        self.assertEqual(translator.translate("status_project", lang="en"), "Project: {name}")


class TestSystemLanguage(unittest.TestCase):
    def detect(self, locale_code, environment):
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch("locale.getlocale", return_value=(locale_code, "UTF-8")))
            stack.enter_context(mock.patch.dict("os.environ", environment, clear=True))
            return translator.get_system_language()

    def test_spanish_locale(self):
        self.assertEqual(self.detect("es_ES", {}), "es")

    def test_other_locales_use_english(self):
        self.assertEqual(self.detect("de_DE", {}), "en")

    def test_environment_variables_are_used_without_a_locale(self):
        self.assertEqual(self.detect(None, {"LANG": "es_MX.UTF-8"}), "es")
        self.assertEqual(self.detect(None, {}), "en")

    def test_resolve_language(self):
        self.assertEqual(translator.resolve_language("es"), "es")
        with mock.patch.object(translator, "get_system_language", return_value="es"):
            self.assertEqual(translator.resolve_language("auto"), "es")


if __name__ == "__main__":
    unittest.main()

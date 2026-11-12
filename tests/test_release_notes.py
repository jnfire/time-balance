import contextlib
import importlib.util
import io
import pathlib
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "release_notes.py"
spec = importlib.util.spec_from_file_location("release_notes", SCRIPT)
release_notes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release_notes)

CHANGELOG = """# Changelog

## [0.7.0] - 2026-12-01

### Added
- Newer thing.

## [0.6.0] - 2026-11-10

Intro line.

### Fixed
- Older thing.

## [0.5.0] - 2026-04-26

- Oldest thing.
"""


class TestExtractNotes(unittest.TestCase):
    def test_returns_only_the_requested_section(self):
        notes = release_notes.extract_notes(CHANGELOG, "0.6.0")
        self.assertTrue(notes.startswith("Intro line."))
        self.assertIn("Older thing.", notes)
        self.assertNotIn("Newer thing.", notes)
        self.assertNotIn("Oldest thing.", notes)

    def test_the_last_section_runs_to_the_end(self):
        self.assertEqual(release_notes.extract_notes(CHANGELOG, "0.5.0"), "- Oldest thing.\n")

    def test_an_unknown_or_empty_section_gives_nothing(self):
        self.assertEqual(release_notes.extract_notes(CHANGELOG, "9.9.9"), "")
        self.assertEqual(
            release_notes.extract_notes("## [1.0.0]\n\n## [0.9.0]\n- x\n", "1.0.0"), ""
        )


class TestMain(unittest.TestCase):
    def run_main(self, version, changelog, argv):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            (root / "time_balance").mkdir()
            (root / "time_balance" / "VERSION").write_text(version + "\n")
            (root / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = release_notes.main(argv, root=root)
        return code, out.getvalue(), err.getvalue()

    def test_prints_the_notes_of_the_current_version(self):
        code, out, _ = self.run_main("0.6.0", CHANGELOG, ["--tag", "v0.6.0"])
        self.assertEqual(code, 0)
        self.assertIn("Older thing.", out)

    def test_a_tag_that_does_not_match_the_version_fails(self):
        code, out, err = self.run_main("0.6.0", CHANGELOG, ["--tag", "v0.6.1"])
        self.assertEqual((code, out), (1, ""))
        self.assertIn("does not match", err)

    def test_a_missing_changelog_entry_fails(self):
        code, _, err = self.run_main("0.8.0", CHANGELOG, [])
        self.assertEqual(code, 1)
        self.assertIn("No section for 0.8.0", err)


class TestTheRealRepository(unittest.TestCase):
    def test_the_current_version_has_release_notes(self):
        self.assertEqual(release_notes.main([]), 0)


if __name__ == "__main__":
    unittest.main()

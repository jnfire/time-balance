# Developer Guide

Technical notes for `time-balance` v0.6.x. The project is finished, so this guide is a reference, not an invitation to contribute. The design is described in [ARCHITECTURE.md](ARCHITECTURE.md).

## Philosophy

- **Layers that only depend downwards**: flows (`cli/`) use the database, the terminal layer, translations and pure helpers; nothing below knows about the flows.
- **Pure logic outside the screens**: parsing, formatting and page arithmetic are plain functions with unit tests.
- **Typed code**: public functions are annotated and `mypy` passes with no exceptions.
- **No hidden side effects**: importing the package never touches the disk or the terminal.
- **Descriptive names**: no single-letter variables outside comprehensions.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
./main.py          # or: time-balance
```

## Checks

CI runs all of these on every push and pull request:

```bash
ruff check .                  # lint
ruff format --check .         # formatting
mypy time_balance             # types
python -m unittest discover   # tests
coverage run -m unittest discover && coverage report --fail-under=90
```

`ruff format .` and `ruff check --fix .` fix most findings on their own.

## Testing flows

`tests/helpers.py` gives each test a temporary database and a terminal whose answers are scripted:

```python
class TestRegisterDay(DatabaseTestCase):
    def test_stores_the_day(self):
        with ScriptedTerminal(["2026-04-24", "8", "15"]).active() as terminal:
            register_day(self.ctx)
        record = self.db.get_record_by_date(self.project_id, "2026-04-24")
        self.assertEqual(record["difference"], 30)
        self.assertIn("+30m", terminal.output)
```

Each question the flow asks consumes the next answer; an empty answer takes the default. A flow that asks for more than was scripted, or a test that leaves answers unused, fails.

## Adding a flow

1. Put the logic that does not need a terminal in `utils/` as a pure function, and test it.
2. Write the flow in `cli/` as a function that takes a `Context`. Use `ctx.t(...)`, `ctx.pause()` and `ctx.confirm(...)`, and pass anything the user typed through `ui.escape` before printing it.
3. Add the translation keys to **both** `en.json` and `es.json`. A test checks that they match, placeholders included.
4. Register it in the menu or in `build_parser()` in `cli/main.py`, and test it with `ScriptedTerminal`.

## Database

The schema is in `database/manager.py`. The data folder is `~/.local/share/time-balance/` on Linux (or `$XDG_DATA_HOME`), `~/Library/Application Support/time-balance/` on macOS and `%APPDATA%\time-balance\` on Windows. All writes go through `DatabaseManager`, which keeps the balance cache consistent in the same transaction.

## Releasing

1. Update `time_balance/VERSION` and add a `## [x.y.z] - date` section to `CHANGELOG.md`.
2. Merge to `main`, then push the tag `vx.y.z`.
3. The Release workflow checks that the tag matches `VERSION`, builds the wheel and the source distribution and creates the release with the changelog section as its notes.

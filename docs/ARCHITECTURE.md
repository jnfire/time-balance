# Project Architecture

## Overview

`time-balance` registers workdays and keeps an hour balance from the terminal. The code is split into layers that only depend downwards, so each layer can be tested without the ones above it.

```
cli ──► database, ui, i18n, utils
 ui ──► Rich (and nothing else)
database ──► SQLite
```

## Project structure

```
time-balance/
├── main.py                   # Run from a checkout, without installing
├── pyproject.toml            # Packaging, ruff and mypy configuration
├── time_balance/
│   ├── cli/                  # The flows the user sees
│   │   ├── main.py           # Argument parser, dashboard and the control-center loop
│   │   ├── context.py        # Context: database + language, passed to every flow
│   │   ├── registration.py   # Registering a day
│   │   ├── history.py        # Listing, browsing and deleting days
│   │   ├── projects.py       # Switching, creating and deleting projects
│   │   └── config_menu.py    # Project settings, language, import and export
│   ├── database/
│   │   ├── manager.py        # DatabaseManager: all the SQL
│   │   ├── models.py         # Project, Record and RecordData (typed rows)
│   │   └── __init__.py       # get_database(): opens the database on first use
│   ├── ui/interface.py       # The only module that talks to Rich
│   ├── i18n/                 # Translator and the en/es JSON files
│   ├── utils/
│   │   ├── calculations.py   # Differences, formatting, balance colors (pure)
│   │   ├── validation.py     # Parsing what the user types (pure)
│   │   ├── pagination.py     # Page arithmetic (pure)
│   │   └── files.py          # The history file: validation and atomic export
│   ├── config.py             # Version, data folder, defaults
│   └── VERSION               # Single source of truth for the version
├── tests/
└── docs/
```

## Principles

### Flows receive a context
Every interactive flow takes a `Context` (the database and the language) instead of reaching for globals. `ctx.t("key")` translates, `ctx.pause()` waits for Enter and `ctx.confirm(...)` asks yes/no with the letters of the session language. A flow can therefore be tested with a temporary database and a scripted terminal, without patching anything.

### The database opens when it is needed
`get_database()` creates the SQLite file the first time something asks for it. Importing the package, or running `time-balance --version`, never touches the disk. Tests install their own instance with `set_database()`.

### Logic lives outside the screens
Parsing dates and durations (`validation.py`), page arithmetic (`pagination.py`) and the rules for deleting a project (`projects.find_deletable_project`) are plain functions. The flows only ask, call them and print.

### One module talks to the terminal library
`ui/interface.py` is the only place that imports Rich. Text typed by the user (project names, file paths) goes through `ui.escape` before it is placed in a message, because Rich reads square brackets as markup.

### Typed rows
The database returns `Project` and `Record` typed dictionaries. `get_active_project()` always returns a project: if the stored id no longer exists, the first project becomes the active one.

## Balance cache

`projects.total_balance` caches the sum of the differences of a project.
- A write that changes a record adjusts the cache in the same transaction.
- A NULL cache means "unknown" and is rebuilt from the records the next time it is read.
- `import_records` and the repair option rebuild it from the records.

## Testing

- `tests/helpers.py` provides `DatabaseTestCase` (a temporary database and a context) and `ScriptedTerminal`, which answers the prompts from a list and records what is printed. A flow that asks for more input than scripted fails the test.
- Flows are tested end to end through that terminal; pure functions with plain unit tests; `test_translator.py` checks that both languages define the same keys and placeholders.
- `tests/test_main.py` runs the program in a subprocess to check that nothing is created on disk by importing it or asking for the version.

## Distribution

The project is a Python package defined entirely in `pyproject.toml`. The translations and the `VERSION` file are package data, and CI checks that they end up inside the wheel. A `v*` tag builds the wheel and the source distribution and attaches them to a GitHub release.

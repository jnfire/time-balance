# Changelog

All notable changes to this project will be documented in this file.

## [0.6.0] - 2026-11-10

The final release. time-balance was the first sketch of what became time-tracker, a web application. This version cleans the code up, documents it and closes the project.

### Added
- The dashboard shows the last registered day.
- Input validation: hours from 0 to 24 and minutes from 0 to 59 everywhere a duration is typed (registering a day, creating a project, editing the base).
- A release workflow: pushing a `v*` tag builds the wheel and the source distribution and creates the GitHub release with the notes of this changelog.
- Documentation of the export format (`docs/DATA-FORMAT.md`), in English and Spanish.
- Quality tooling: ruff (lint and format) and mypy, run in CI together with a coverage floor of 90%. Coverage went from 63% to 96% and the tests from 51 to 144.

### Changed
- **Architecture.** Flows receive a `Context` (database and language) instead of using globals, so they are tested with a temporary database and a scripted terminal. The database is opened the first time it is needed: importing the package or running `--version` no longer creates files. Rows are typed (`Project`, `Record`), the validation and the page arithmetic are pure functions, and `files.py` uses `pathlib` and types.
- `main()` takes the arguments and returns the exit code, so it can be called and tested without patching `sys.argv`.
- Balances and durations drop the empty parts: `+1h 15m`, `-25m`, `+2h` and `0m` instead of `-0h 25m`, `+2h 0m` and `0h 0m`. Labels are in sentence case and project names are shown as typed.
- Packaging is `pyproject.toml` alone, with a real author, the repository URL and Python 3.9 as the minimum. The command is defined in one place and `setup.py` and `MANIFEST.in` are gone.
- CI runs on every push to `main` and on pull requests, on Python 3.9 to 3.13, and checks that the translations end up inside the wheel.
- The README is rewritten in English and Spanish, with screenshots, installation from the release files and a note that the project is finished and that time-tracker continues it.

### Fixed
- Creating or renaming a project to a name that already exists crashed the program with a database error. It now says so.
- Hours and minutes outside a valid range (negative hours, 75 minutes) were accepted and stored.
- Merging an import into a project that already had records left a wrong balance. The balance is now rebuilt from the records after every import.
- A project whose name contains square brackets, such as `[bold]`, broke the screen. Text typed by the user is now escaped.
- An invalid date when registering a day silently used today's date. The registration is cancelled instead.
- `--lang` had no effect in the interactive menu.
- If the active project no longer existed, the program crashed. The first project becomes the active one.
- Table headers, the language label, the repair option, the whole project-deletion flow and the yes/no answers were hard-coded in one language. They are translated now.

### Removed
- The contribution guides: the project is finished and no longer accepts changes.

## [0.5.0] - 2026-04-26

### Added
- **Project Balance in Overview**: The project selection table now displays the total accumulated balance for each project in real-time.
- **Project Deletion Safeguard**: Added a secure project deletion flow requiring the user to type the exact project name to confirm.
- **Data Integrity Maintenance**: New "Repair/Recalculate balances" option in the configuration menu to force a full cache rebuild from history.
- **Unified Navigation Help**: Redesigned navigation options (V, N, P, etc.) to be vertical and enclosed by horizontal rules for better readability on all terminal sizes.
- **Database Integrity**: Enabled SQLite foreign keys support (`PRAGMA foreign_keys = ON`) to ensure `ON DELETE CASCADE` consistency.
- **Domain-Driven Modularization**: The application has been completely restructured into functional domains: `cli/`, `database/`, `ui/`, `i18n/`, and `utils/`.
- **UI Abstraction Layer**: Created a dedicated `ui/interface.py` to decouple the application from the `Rich` library, allowing for future frontend flexibility.
- **JSON-Based Localization**: Migrated all translations to external JSON files (`en.json`, `es.json`) located in `i18n/locales/` for easier management and expansion.
- **Delete Workday Feature**: Users can now delete daily time records from the history view with confirmation display showing date, hours worked, and balance impact. Feature is fully project-isolated.
- **COALESCE NULL Balance Handling**: Replaced `WHERE total_balance IS NOT NULL` conditions with `COALESCE(total_balance, 0)` to ensure cache updates work correctly even when importing or restoring data with NULL balances.

### Changed
- **Simplified Project Management**: Users can now switch projects directly by entering their ID from the overview table, removing unnecessary menu steps.
- **Professional Time Formatting**: Updated `format_time` to use a more readable and consistent format (`+1h 5m` instead of `+01h 05m`) across the entire application.
- **Enhanced I18N Fallback**: Replaced the deprecated `locale.getdefaultlocale()` with a modern approach using `locale.getlocale()` and environment variable detection (`LC_ALL`, `LANG`).
- **Improved UX Prompts**: Set `case_sensitive=False` for all navigation prompts, allowing both uppercase and lowercase inputs (V/v, N/n, etc.).
- **Naming Excellence**: System-wide refactor to eliminate single-letter variables and adopt descriptive, professional naming conventions.
- **Clean CLI Architecture**: Divided the monolithic `cli.py` into specialized modules (`history`, `registration`, `projects`, `config_menu`, `migration`).
- **Project-Isolated Recalculation**: The balance recalculation now only affects the active project, preventing unintended side effects on other projects.
- **Delete Flow UX**: Improved delete workflow to display recent records as reference context before requesting the date to delete.

### Fixed
- **Double Sign Formatting**: Resolved an issue where time balances were displayed with double signs (e.g., `++0h 09m`) in the dashboard and history views.
- **UI Spacing & Consistency**: Resolved issues with redundant dash decorations and excessive whitespace in submenus.
- **Import Errors on Installation**: Fixed a regression in `__init__.py` that caused `ImportError` when running as a globally installed tool.
- **Cross-Project Balance Contamination**: Fixed bug where recalculating balances would affect all projects instead of just the active one.
- **Delete Flow Context**: Removed automatic screen clear during delete operation to maintain visual context of available records.
- **Cache Inconsistency on Import**: Fixed issue where NULL `total_balance` values (from imports or restores) would prevent proper cache updates during record operations.

### Testing
- **Comprehensive Delete & Recalculate Tests**: Added 15 new tests verifying balance calculations square correctly and projects remain isolated.
- **COALESCE NULL Balance Tests**: Added 9 tests specifically targeting the NULL balance handling to ensure cache resilience during imports and data restoration.

### Quality Assurance
- All changes validated against project standards defined in `docs/ARCHITECTURE.md` and `docs/DEVELOPMENT.md`.
- 51 total tests passing with zero regressions.
- Full compliance with UI Abstraction Layer, Domain-Driven Modularization, and Naming Standards.


## [0.4.2] - 2026-04-24

### Fixed
- **NameError in Migration**: Fixed missing `migrate_from_json` function reported in code review.
- **SQLite Connection Leaks**: Implemented a robust context manager in `DatabaseManager` to ensure all database connections are properly closed after use.
- **Redundant Schema Alterations**: Integrated `total_balance` directly into the initial table creation for cleaner database initialization.
- **Smooth Exit Flow**: Improved `KeyboardInterrupt` handling to exit immediately without requiring extra prompts.

### Changed
- **Higher-Level Storage API**: Refactored CLI code to use `DatabaseManager` methods instead of raw SQL queries for better separation of concerns.

## [0.4.1] - 2026-04-24

### Added
- **High-Performance Balance Cache**: Added `total_balance` column to projects table to avoid $O(N)$ calculations.
- **Atomic Balance Updates**: Balance is now updated incrementally on each record creation, modification, or deletion.
- **Balance Audit Tool**: New internal methods to recalculate and validate the total balance.
- **Automated Balance Tests**: Added comprehensive test suite for the balance cache engine.

### Changed
- **Optimized CLI Performance**: The status command and main menu now display the balance instantly.
- **Clean Test Output**: Silenced CLI print statements during automated testing for professional output.

## [0.3.0] - 2026-04-24
### Added
- **Global Installation**: The app now stores data in standard system paths (XDG compliant), making it truly global.
- **SQLite Backend**: Replaced JSON storage with SQLite for improved performance and data integrity.
- **Multi-project Support**: New project management menu allows creating, switching, and editing multiple work contexts.
- **Migration Tool**: New `--migrate <file.json>` command to import legacy history files into the new system.
- **Active Project Context**: The application now remembers the last used project globally.

### Changed
- Refactored `storage.py` to use `DatabaseManager`.
- Updated `cli.py` to support project management submenus.
- Decoupled `io.py` from storage logic for better testability.

## [0.2.0] - 2026-04-20
### Added
- **Globalization (i18n)**: Fully translated UI with automatic language detection (English and Spanish supported).
- **Data Context**: Each history file now stores its own project name and base workday configuration.
- **English Source Code**: All internal functions, variables, and comments renamed to English for international collaboration.
- **CLI Arguments**: New command-line flags `--status`, `--list`, `--lang`, and `--version`.
- **Modular Architecture**: Code decoupled into `core`, `constants`, `storage`, `io`, `cli`, and `i18n`.
- **New Modular Test Suite**: 17 automated tests validating all logic and translations.
- **Support for Module Execution**: Can now be run using `python -m time_balance`.

### Changed
- `README.md` and all documentation files migrated to English.
- Updated project structure for better maintainability.
### Fixed
- Fixed directory fsync for better crash-safety on atomic writes.

## [0.1.1] - 2026-01-26
### Changed
- Removed compatibility shim `control_horas.py`; consumers should import directly from `time_balance`.
- Updated README to reflect the removal of the shim and usage examples.

## [0.1.0] - initial release
- Initial implementation with interactive UI and basic JSON storage.

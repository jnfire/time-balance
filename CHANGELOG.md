# Changelog

All notable changes to this project will be documented in this file.

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

# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-04-19
### Added
- New modular architecture for better maintainability.
- `time_balance/constants.py`: Centralized configuration and constants (removed magic strings).
- `time_balance/core.py`: Business logic for time calculations and formatting.
- `time_balance/storage.py`: Dedicated persistence and file resolution logic.
- `time_balance/io.py`: Data validation, import, and export logic.
- `time_balance/cli.py`: User interface and interactive menu.
- `time_balance/__main__.py`: Support for running the package as a module (`python -m time_balance`).
- New modular test suite in `tests/` (`test_core.py`, `test_storage.py`, `test_io.py`, `test_cli.py`).

### Changed
- `time_balance/__init__.py` now acts as a clean facade re-exporting the public API.
- Updated documentation and README to reflect the new architecture.

## [0.1.1] - 2026-01-26
### Changed
- Removed compatibility shim `control_horas.py`; consumers should import directly from `time_balance`.
- Updated README to reflect the removal of the shim and usage examples.
- Bumped package version to 0.1.1.

### Fixed
- Updated tests to import `time_balance` directly and ensured backup creation during import/overwrite works as expected.

## [0.1.0] - initial release
- Initial implementation with interactive UI, import/export and compatibility shim.

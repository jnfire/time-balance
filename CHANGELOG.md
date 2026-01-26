# Changelog

All notable changes to this project will be documented in this file.

## [0.1.1] - 2026-01-26
### Changed
- Removed compatibility shim `control_horas.py`; consumers should import directly from `time_balance`.
- Replaced argparse subcommands with a single interactive UI entrypoint (`main`).
- Updated README to reflect the removal of the shim and usage examples.
- Bumped package version to 0.1.1.

### Fixed
- Updated tests to import `time_balance` directly and ensured backup creation during import/overwrite works as expected.

## [0.1.0] - initial release
- Initial implementation with interactive UI, import/export and compatibility shim.

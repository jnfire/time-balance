# Project Architecture

## Overview

`time-balance` is a terminal application to track working hours and manage accumulated balances. It is designed under principles of modularity, data integrity, and ease of use.

## Project Structure

```
time-balance/
├── time_balance/              # Main package
│   ├── __init__.py           # Facade (re-exports public API)
│   ├── __main__.py           # Entry point for module execution
│   ├── constants.py          # Centralized configuration and constants
│   ├── core.py               # Business logic (formatting, calculations)
│   ├── storage.py            # Persistence and schema migrations
│   ├── io.py                 # Validation, import, and export
│   ├── cli.py                # User interface and arguments
│   └── i18n.py               # Internationalization system
├── tests/                    # Modular test suite
│   ├── test_core.py
│   ├── test_storage.py
│   ├── test_io.py
│   └── test_cli.py
├── docs/                     # Documentation
├── README.md                 # User guide
└── CHANGELOG.md              # Change history
```

## Modules and Components

### 1. **`core.py` (Business Logic)**
Contains the mathematical "brain" of the system, independent of I/O.
- `format_time()`: Converts minutes to readable format +/- Xh Ym.
- `calculate_total_balance()`: Sums differences from a list of records.

### 2. **`storage.py` (Persistence Layer)**
Manages the history file lifecycle and physical integrity.
- `load_data()`: Loads JSON and applies **automatic migration** to the new structured schema.
- `save_data()`: **Atomic** (crash-safe) writing using temporary files and replacement.
- `_create_backup()`: Generates versioned backups before critical operations.

### 3. **`cli.py` (Presentation Layer)**
Handles final user interaction.
- Supports **command arguments** (`--status`, `--list`, `--version`, `--lang`) for quick queries.
- Provides an **interactive menu** for daily management.
- Allows dynamic project configuration (name and base workday).

### 4. **`io.py` (Data Exchange)**
Logic to import and export histories between different systems.
- Rigorous JSON schema validation (supports legacy formats).
- Support for history merging (`merge`) or total replacement (`overwrite`).

### 5. **`i18n.py` (Internationalization)**
Simple translation system supporting multiple languages (English and Spanish included).
- Automatically detects system language.
- Provides the `translate()` utility for the CLI.

## Data Schema (JSON)

Each project is saved with its own configuration context to allow future multi-project support.

```json
{
    "metadata": {
        "project_name": "My Project",
        "hours_base": 7,
        "minutos_base": 45,
        "version": "1.0",
        "language": "auto"
    },
    "registros": {
        "2026-04-19": {
            "hours": 8,
            "minutos": 0,
            "diferencia": 15
        }
    }
}
```

## Reliability and Safety

- **Integrity**: All writes are atomic. If the program closes unexpectedly, data is not corrupted.
- **Resilience**: Transparent migration of old formats.
- **Privacy**: 100% local storage in plain text (JSON).

## Testing

The test suite is divided to match the package architecture:
- `test_core`: Validates calculation algorithms.
- `test_storage`: Validates persistence, backups, and schema migration.
- `test_io`: Validates import/export and legacy compatibility.
- `test_cli`: Validates UI and command arguments.

## Future Extensibility (Technical Evolution)

The system is designed to evolve into a professional time management solution:

1. **Relational Storage (SQLite)**:
   - Migrate internal persistence from JSON to SQLite.
   - JSON format will remain exclusively for import/export flows (portability).

2. **Centralized Multi-project Support**:
   - Implement a global project registry to switch contexts without changing directories.

3. **Cloud Sync**:
   - Allow database location in cloud storage services for automatic synchronization.

4. **Modern UI (Rich UI)**:
   - Integrate libraries like `rich` to improve the presentation of tables and colors.

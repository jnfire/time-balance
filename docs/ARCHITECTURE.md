# Project Architecture

## Overview

`time-balance` is a terminal application to track working hours and manage accumulated balances. In version 0.3.0, the application evolved into a **global** and **multi-project** tool, using **SQLite** as the persistence engine and following XDG standards for data storage.

## Project Structure

```
time-balance/
├── time_balance/              # Main package
│   ├── __init__.py           # Facade (re-exports public API)
│   ├── __main__.py           # Entry point for module execution
│   ├── constants.py          # Global path configuration and constants
│   ├── core.py               # Business logic (formatting, calculations)
│   ├── storage.py            # Persistence (SQLite) and DatabaseManager
│   ├── io.py                 # External file validation and reading (JSON)
│   ├── cli.py                # User interface (Menu and Submenus)
│   └── i18n.py               # Internationalization system
├── tests/                    # Modular test suite
│   ├── test_core.py
│   ├── test_storage.py       # Validates SQLite transactions
│   ├── test_io.py            # Validates JSON schema reading
│   └── test_cli.py           # Validates menus and interaction
├── docs/                     # Documentation
├── README.md                 # User guide
└── CHANGELOG.md              # Change history
```

## Modules and Components

### 1. **`core.py` (Business Logic)**
Contains mathematical and formatting functions independent of persistence.
- `format_time()`: Converts minutes to readable format `+/- Xh Ym`.
- `calculate_total_balance()`: Used mainly during imports to validate balances.

### 2. **`storage.py` (SQLite Persistence Layer)**
Implements the `DatabaseManager` class which centralizes all SQL operations.
- **Project Management**: CRUD for multiple work contexts.
- **Records**: Efficient storage of workdays by project ID.
- **Global Settings**: `settings` table to remember the active project and language.
- **Standard Location**: Uses `pathlib` to comply with XDG (Application Support on macOS, .local/share on Linux).

### 3. **`cli.py` (Presentation Layer)**
Handles user interaction.
- **Main Menu**: Logging and viewing operations for the active project.
- **Project Management**: Submenu to create, switch, and edit projects.
- **Migration Command**: `--migrate` flag to import data from legacy JSON files.

### 4. **`io.py` (Data Exchange)**
Logic to validate and read external JSON files.
- `read_history_file()`: Validates schemas from previous versions (v0.2.x).
- `export_history()`: Generates a JSON dump of the active project.

### 5. **`i18n.py` (Internationalization)**
Simple translation engine supporting English and Spanish.

## Database Schema (SQLite)

### `projects` table
| Column | Type | Description |
| :--- | :--- | :--- |
| id | INTEGER PK | Unique identifier |
| name | TEXT UNIQUE | Project name |
| base_hours | INTEGER | Base workday (hours) |
| base_minutes | INTEGER | Base workday (minutes) |

### `records` table
| Column | Type | Description |
| :--- | :--- | :--- |
| id | INTEGER PK | Unique identifier |
| project_id | INTEGER FK | Reference to project |
| date | TEXT | Date (YYYY-MM-DD) |
| hours | INTEGER | Hours worked |
| minutes | INTEGER | Minutes worked |
| difference | INTEGER | Balance in minutes |

## Reliability and Safety

- **Transactions**: All critical database operations are protected by SQLite transactions.
- **Atomic Export**: JSON dumps still use atomic writing for safety.
- **Privacy**: All data is stored locally on the user's machine.

## Testing

The test suite has been adapted to use temporary databases:
- `test_storage`: Verifies the schema and `DatabaseManager` behavior.
- `test_cli`: Uses patching (mocking) to simulate user input over database logic.

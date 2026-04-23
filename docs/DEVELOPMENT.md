# Developer Guide

This guide provides technical details for developers who want to contribute to version 0.3.x of `time-balance`.

## Project Philosophy

- **Standard Library Only**: The core and persistence must rely solely on native Python libraries (like `sqlite3`).
- **Clean Code**: Descriptive naming (minimum 3 characters), modularity, and high test coverage.
- **Transactionality**: All database writes must be consistent and secure.

## Layer Structure

### 1. Persistence Logic (`storage.py`)
Manages the global SQLite database.
- `DatabaseManager`: Central class for project and record CRUD.
- `db`: Global instance used by the rest of the application.

### 2. Presentation Layer (`cli.py`)
Controls menu flow and user interaction.
- `manage_projects()`: Logic for the multi-project management submenu.
- `register_day()`: Interacts with `db` to save workdays in the active project.

### 3. Data Exchange (`io.py`)
Functions for reading legacy JSON and exporting dumps.
- `read_history_file(path)`: Reads a JSON and validates it against the old schema.

## Running Tests

It is essential to keep tests updated. A temporary database is used to avoid messing with the developer's real data.

```bash
# Run all tests
python3 -m unittest discover -v tests
```

## Database Management

The database is initialized automatically on the first run. The schema is defined in the `_initialize_database()` method of `DatabaseManager`.

### Data Paths (XDG)
- macOS: `~/Library/Application Support/time-balance/`
- Linux: `~/.local/share/time-balance/`

## How to add a CLI command

1. Modify the `main()` function in `cli.py`.
2. Add the new flag in `argparse`.
3. Implement the corresponding logic, using `db` if it requires data access or `translate()` for output.

## Record Schema Reference
Workdays are saved as difference minutes (`worked_minutes - base_minutes`).
- Example: If the base is 7h 45m (465 min) and 8h (480 min) are worked, the saved difference is `+15`.

# Developer Guide

This guide provides technical details for developers contributing to `time-balance` v0.5.x.

## Project Philosophy

- **Domain-Driven Modularization**: The application is divided into functional domains to ensure scalability and maintainability.
- **UI Abstraction**: Business logic is decoupled from terminal rendering libraries.
- **Strict Naming Standards**: No single-letter variables (except in obvious list comprehensions). Minimum 3 characters.

## Layer Structure

### 1. Persistence Domain (`database/`)
- `DatabaseManager`: Centralizes all SQLite operations. Handles transactions, atomic balance updates, and bulk imports.
- Global `db` instance: Used as a singleton throughout the application.

### 2. Presentation Domain (`cli/`)
- Orchestrated by `cli/main.py`.
- Divided into themed modules: `registration.py`, `history.py`, `projects.py`, etc.
- Uses `ui/interface.py` for all console I/O.

### 3. UI Abstraction Layer (`ui/`)
- `ui/interface.py`: The only module allowed to import visual libraries (like `Rich`). 
- Provides generic components: `render_header`, `render_table`, `render_navigation_help`.

### 4. Localization Domain (`i18n/`)
- `i18n/translator.py`: Caching translation engine.
- `i18n/locales/*.json`: Externalized strings.

## Execution for Development

During development, use the direct entry point in the root directory:

```bash
chmod +x main.py
./main.py
```

## Running Tests

We use temporary SQLite databases for testing to ensure environment isolation.

```bash
# Run all tests
python3 -m unittest discover -v tests
```

## How to add a new CLI command

1. If it's a new flow, create a file in `time_balance/cli/`.
2. Register the command in the `main()` function in `time_balance/cli/main.py`.
3. Use the `ui.interface` for any user interaction.
4. Ensure the new logic follows the naming and DRY standards.

## Database Management

The database follows XDG standards. The schema is defined in `DatabaseManager._initialize_database()`.
- macOS: `~/Library/Application Support/time-balance/`
- Linux: `~/.local/share/time-balance/`

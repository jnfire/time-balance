# Developer Guide

This guide provides technical details for developers contributing to `time-balance` v0.5.x.

## Project Philosophy

- **Domain-Driven Modularization**: The application is divided into functional domains to ensure scalability and maintainability.
- **UI Abstraction**: Business logic is decoupled from terminal rendering libraries.
- **Strict Naming Standards**: No single-letter variables (except in obvious list comprehensions). Minimum 3 characters.

## Layer Structure

### 1. Persistence Domain (`database/`)
- `DatabaseManager`: Centralizes all SQLite operations. Handles transactions, atomic balance updates, and bulk imports.
- Key methods for timer integration:
  - `get_or_create_today_record(project_id)`: Creates or retrieves today's record; initializes the `total_balance` cache.
  - `update_record_time(record_id, hours, minutes)`: Updates record and increments the project's `total_balance` cache atomically.
- Global `db` instance: Used as a singleton throughout the application.

### 2. Presentation Domain (`cli/`)
- Orchestrated by `cli/main.py`.
- Divided into themed modules: `registration.py`, `timer.py`, `history.py`, `projects.py`, etc.
- `timer.py` demonstrates the full workflow: **menu** → **active timer** → **pause** → **save**.
  - `show_timer_menu()`: Main loop showing timer display and menu options.
  - `_timer_loop()`: Runs the active timer, auto-saves every 60 seconds, waits for ENTER to stop.
  - Both call the UI layer for rendering.
- Uses `ui/interface.py` for all console I/O.

### 3. UI Abstraction Layer (`ui/`)
- `ui/interface.py`: The only module allowed to import visual libraries (like `Rich`). 
- Timer-specific components:
  - `render_timer_running(hours, minutes, seconds, project_name, base_time, balance, lang)`: Shows active timer with colors and labels.
  - `render_timer_menu_with_display(hours, minutes, seconds, project_name, base_time, balance, lang)`: Shows paused timer with same visual format.
  - Both use `clear_screen()` to prevent terminal scrolling and apply dynamic coloring (green/red for balance).
- Provides generic components: `render_header`, `render_table`, `render_navigation_help`.

### 4. Localization Domain (`i18n/`)
- `i18n/translator.py`: Caching translation engine.
- `i18n/locales/*.json`: Externalized strings.
- Timer translation keys (new in v0.6.0):
  - `timer_label_elapsed`: Descriptive label for elapsed time.
  - `timer_label_status`: Descriptive label for timer status.
  - `timer_label_balance`: Descriptive label for balance display.

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

## Balance Cache Atomicity

As of v0.6.0, the balance cache (`projects.total_balance`) is updated atomically during real-time operations:

- **Timer Integration**: When the timer updates a record (every 60 seconds or on ENTER), `update_record_time()` immediately updates the project's `total_balance` cache using `COALESCE` for NULL-safe initialization.
- **Record Creation**: When a new daily record is created via `get_or_create_today_record()`, the project's cache is initialized if NULL.
- **Incremental Updates**: The cache uses delta-math: `balance = COALESCE(balance, 0) - old_difference + new_difference`, ensuring O(1) access without full recalculation.
- **Safety**: All updates use `_get_connection()` context manager for transactional integrity with automatic COMMIT on success.

## How to add a new CLI command

1. If it's a new flow, create a file in `time_balance/cli/`.
2. Register the command in the `main()` function in `time_balance/cli/main.py`.
3. Use the `ui.interface` for any user interaction.
4. Ensure the new logic follows the naming and DRY standards.

## Database Management

The database follows XDG standards. The schema is defined in `DatabaseManager._initialize_database()`.
- macOS: `~/Library/Application Support/time-balance/`
- Linux: `~/.local/share/time-balance/`

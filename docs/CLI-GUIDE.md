# Usage Guide: CLI Interface

`time-balance` offers a dual interface: an interactive menu for daily use and direct commands for quick queries. In version 0.3.0, the application is **global** and supports **multiple projects**.

## Direct Commands (Fast Mode)

You can query information or perform actions without entering the interactive menu using flags:

```bash
# View current accumulated balance of the active project
time-balance --status

# List last 10 records of the active project
time-balance --list 10

# Migrate a legacy JSON history file to a new global project
time-balance --migrate ./path/to/history.json

# Force language (en/es)
time-balance --lang en

# Check version
time-balance --version
```

## Interactive Interface

To start the full control center:

```bash
time-balance
```

### Main Menu

The interface automatically detects your system language. It shows the status of the **active project**.

```
==================================================
   PROJECT: MY WORK PROJECT
   TOTAL ACCUMULATED BALANCE: +2h 15m
   (Daily base: 7h 45m)
==================================================

Options:
1. Register workday (or correct day)
2. View recent records
3. Manage projects (switch/create/edit)
4. Export history to file
5. Import history from file
6. Exit

Choose option: _
```

## Detailed Options

### 1. Register Workday
Record worked hours for a specific date (defaults to today). It calculates the difference against the base workday of the **current active project**.

### 2. View Recent Records
Displays the last 5 records (or as many as specified) for the active project.

### 3. Manage Projects
Opens a submenu to:
- **Switch project**: Change which project is currently active globally.
- **Create new project**: Initialize a new work context with its own base workday.
- **Edit project**: Change the name or base workday of the current project.

### 4. Export History
Exports the active project's data to a structured JSON file.

### 5. Import History
Imports data from a JSON file into the **current active project**.
- **Merge Mode**: Adds new records and updates existing ones.
- **Overwrite Mode**: Clears all current records before importing.

---

## Data Persistence
Data is stored in a centralized SQLite database. You no longer need to worry about `historial_hours.json` files in your project folders unless you want to export or migrate them.

### Default Paths
- **macOS**: `~/Library/Application Support/time-balance/`
- **Linux**: `~/.local/share/time-balance/`
- **Windows**: `%APPDATA%/time-balance/`

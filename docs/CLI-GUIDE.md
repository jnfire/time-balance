# Usage Guide: CLI Interface

`time-balance` offers a dual interface: an interactive menu for daily use and direct commands for quick queries. In the current version, the application is **global** and supports **multiple projects** with optimized navigation.

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

### Standard Navigation
For a smooth experience, `time-balance` uses a hybrid system:
- **Numbers (1-5)**: To select actions and configuration options.
- **Letters**: For navigation and movement.
  - `V`: Go Back to previous menu.
  - `N`: Next page (in history).
  - `P`: Previous page (in history).

---

### Main Menu

The main menu is sober and direct, always showing the **Dashboard** of the active project at the top.

```
1. Register workday
2. View records
3. Configuration
4. Change project
5. Exit
```

## Detailed Sections

### 1. Register Workday
Record worked hours for a specific date (defaults to today). It calculates the difference against the base workday of the active project.

### 2. View Records (Paginated)
Displays the complete project history in tables of 10 records.
- Use `N` and `P` to navigate between pages.
- Use `V` to go back to the main menu.

### 3. Configuration
Submenu divided into sections for clear management:
- **Project Settings**: Edit name, adjust daily base (hours/minutes), and language.
- **Data Management**: Import and Export options for JSON files.
- Use `V` to go back.

### 4. Change Project
Dedicated section for multi-tenancy management.
- Allows selecting an existing project from the list.
- Allows creating a new project from scratch.
- Use `V` to go back.

---

## Data Persistence
Data is stored in a centralized SQLite database. You no longer need to worry about local files in your project folders.

### Default Paths
- **macOS**: `~/Library/Application Support/time-balance/`
- **Linux**: `~/.local/share/time-balance/`
- **Windows**: `%APPDATA%/time-balance/`

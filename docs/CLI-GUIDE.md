# Usage Guide: CLI Interface

`time-balance` offers a dual interface: an interactive menu for daily use and direct commands for quick queries.

## Direct Commands (Fast Mode)

You can query information without entering the interactive menu using flags:

```bash
# View current accumulated balance
time-balance --status

# List last 10 records
time-balance --list 10

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

The interface automatically detects your system language, but you can change it in the project configuration.

```
==================================================
   PROJECT: PROJECT NAME
   TOTAL ACCUMULATED BALANCE: +2h 15m
   (Daily base: 7h 45m)
==================================================

Options:
1. Register workday (or correct day)
2. View recent records
3. Configure project (name/hours)
4. Export history to file
5. Import history from file
6. Exit

Choose option: _
```

## Detailed Options

### 1. Register Workday
Allows you to record worked hours. If the day already exists, it will ask for confirmation to overwrite. It automatically calculates the difference against the base workday configured for **that project**.

### 2. View Recent Records
Displays a table with the 5 most recent records, including hours worked and the impact on the balance (positive or negative).

### 3. Configure Project
Allows you to customize the project name and the base workday (hours/minutes) for the current file. This is saved in the JSON metadata.

### 4. Export History
Creates a backup copy in structured JSON format at the path of your choice.

### 5. Import History
- **Merge Mode**: Combines external data with the current one. Imported data wins in case of a date conflict.
- **Overwrite Mode**: Replaces the entire file (metadata and records) with the new one. It creates an automatic backup before proceeding.

## Environment Variables Configuration

You can centralize your history by defining the path in your shell configuration file (`.bashrc` or `.zshrc`):

```bash
export HISTORIAL_PATH="~/.config/time-balance/main_history.json"
```

---

## Usage Tips
- Press **ENTER** in the date field to use today quickly.
- Use `--status` in your automation scripts to see your balance when starting the terminal.
- Export your data regularly if you are not using a synchronized folder.

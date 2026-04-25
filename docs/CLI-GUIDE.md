# Usage Guide: CLI Interface

`time-balance` offers a dual interface: an interactive control center and direct flags for quick status checks.

## Direct Flags (Fast Mode)

You can query your status or perform migrations without entering the menu:

```bash
# View status of active project
time-balance --status

# List last 5 records
time-balance --list

# Migrate legacy history.json
time-balance --migrate ./history.json

# Force UI language
time-balance --lang es
```

## Interactive Interface

To start the control center:

```bash
time-balance
```

### Standard Navigation
The application uses a consistent navigation standard:
- **Numbers (1-5)**: To select actions and configuration options.
- **Capital Letters (V, N, P)**: For movement and navigation.
  - `V`: **V**olver / Back.
  - `N`: **N**ext page.
  - `P`: **P**revious page.

---

### Main Dashboard
Every time you enter a menu, a central dashboard displays the current project context, base workday, and your current accumulated balance.

## Submenus

### 1. Register Workday
Interactive flow to log your hours. It automatically calculates the difference against your base workday. If a record already exists, it will ask for confirmation before overwriting.

### 2. View History (Paginated)
Displays your records in professional tables.
- Use `N` and `P` to browse through your work history.
- Use `V` to return to the main menu.

### 3. Configuration
Manage your project and data:
- **Project Settings**: Edit name, adjust base time, and language.
- **Data Management**: Bulk import and Export to JSON.

### 4. Project Management
Dedicated section to manage multiple work contexts:
- Switch between existing projects.
- Create new projects with custom base workdays.

---

## Data and Persistence
All information is stored in a centralized SQLite database.

### System Paths (XDG)
- **macOS**: `~/Library/Application Support/time-balance/`
- **Linux**: `~/.local/share/time-balance/`
- **Windows**: `%APPDATA%/time-balance/`

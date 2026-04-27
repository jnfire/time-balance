# Usage Guide: CLI Interface

`time-balance` offers a dual interface: an interactive control center and direct flags for quick status checks.

## Direct Flags (Fast Mode)

You can query your status or perform migrations without entering the menu:

```bash
# View status of active project
time-balance --status

# List last 5 records
time-balance --list

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

### 1. Real-Time Timer
A simplified, minimal interface for tracking your work in real-time:
- **Activation**: Press `1` from the main menu to start the timer.
- **Interface**: Shows elapsed time, current status (ACTIVE/PAUSED), and estimated balance.
- **Colors**: Green for positive balance, red for negative balance; easily readable on both dark and light terminals.
- **Workflow**:
  - Press `1` to activate and start counting.
  - Timer automatically saves progress every 60 seconds (saves only minutes; seconds precision isn't stored).
  - Press `ENTER` to stop and save the current session, returning to the main menu.
  - The timer persists today's record in the database automatically.
- **Design**: Unified visual design across active and paused states with explanatory labels.

### 2. Register Workday
Interactive flow to log your hours. It automatically calculates the difference against your base workday. If a record already exists, it will ask for confirmation before overwriting.

### 3. View History (Paginated)
Displays your records in professional tables.
- Use `N` and `P` to browse through your work history.
- Use `V` to return to the main menu.

### 4. Configuration
Manage your project and data:
- **Project Settings**: Edit name, adjust base time, and language.
- **Data Management**: Bulk import and Export to JSON.

### 5. Project Management
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

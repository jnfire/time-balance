# time-balance 🕒

> A professional, global terminal tool to manage multiple projects, track workdays, and manage your hour balance.

[Leer en español 🇪🇸](README.es.md)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Description

`time-balance` is now a **global** console application. It no longer depends on where you run it; your projects and records are stored in a centralized SQLite database on your machine. It automatically calculates the daily difference against a base workday and maintains an accumulated balance for each project independently.

---

## Global Installation

To install the application so it's available in any terminal:

```bash
# Clone and enter directory
git clone <repo-url>
cd time-balance

# Install globally for your user
pip install .
```

---

## Usage

### 1. Control Center (Interactive Menu)
Simply run the command from any folder to open the manager:

```bash
time-balance
```

### 2. Multi-Project Management
Inside the menu, **option 3** allows you to create new projects (e.g., "Client A", "Personal") and switch between them. The app remembers your last active project globally.

### 3. Migrating Legacy Data (v0.2.x)
If you have `historial_hours.json` files from previous versions, you can easily import them into a new project in the global database:

```bash
time-balance --migrate ./path/to/historial_hours.json
```

### 4. Quick Commands
Check your status without entering the menu:

```bash
# Show balance for the active project
time-balance --status

# List last 10 records for the active project
time-balance --list 10

# Force a specific language (en/es)
time-balance --lang en
```

---

## Version 0.3.0 Features

- ✅ **SQLite Backend**: Robust and professional persistence in standard paths (XDG).
- ✅ **Multi-project**: Manage different work contexts from a single installation.
- ✅ **Global Installation**: Access your data from any terminal location.
- ✅ **Migration Tool**: Dedicated command to bring your data from the JSON era.
- ✅ **Privacy-Focused**: All data remains 100% local on your machine.

---

## Data Location
The database is automatically saved in:
- **macOS**: `~/Library/Application Support/time-balance/time_balance.db`
- **Linux**: `~/.local/share/time-balance/time_balance.db`
- **Windows**: `%APPDATA%/time-balance/time_balance.db`

---

## Development and Contributions

If you want to contribute or understand how it works internally:
- [**ARCHITECTURE.md**](docs/ARCHITECTURE.md): System design and modules.
- [**DEVELOPMENT.md**](docs/DEVELOPMENT.md): Technical guide for developers.
- [**CONTRIBUTING.md**](docs/CONTRIBUTING.md): How to submit improvements and translations.

## License

This project is Open Source under the [GPL-3.0](LICENSE) license.

---

## Development and Contributions

If you want to contribute or understand how it works internally:
- [**ARCHITECTURE.md**](docs/ARCHITECTURE.md): System design and modules.
- [**DEVELOPMENT.md**](docs/DEVELOPMENT.md): Technical guide for developers.
- [**CONTRIBUTING.md**](docs/CONTRIBUTING.md): How to submit improvements and translations.

## License

This project is Open Source under the [GPL-3.0](LICENSE) license.

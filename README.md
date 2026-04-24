# time-balance 🕒

> A professional, global terminal tool to manage multiple projects, track workdays, and manage your hour balance.

[Leer en español 🇪🇸](README.es.md)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Description

`time-balance` is a **global** console application. It no longer depends on where you run it; your projects and records are stored in a centralized SQLite database on your machine. It automatically calculates the daily difference against a base workday and maintains an accumulated balance for each project independently.

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

### 2. Intuitive Navigation
The interface uses a clear standard:
- **Numbers (1-5)** to select actions.
- **Letters** for navigation: `V` to go back, `N`/`P` to navigate history pages.

### 3. Project Management and Configuration
- **Option 3 (Configuration)**: Adjust the name, base workday, or language of the active project. Also allows data import/export.
- **Option 4 (Change Project)**: Switch between different work contexts or create a new one.

### 4. Quick Commands
Check your status without entering the menu:

```bash
# Show balance for the active project
time-balance --status

# List last 10 records for the active project
time-balance --list 10
```

---

## Main Features

- ✅ **High-Performance Caching**: Atomic balance updates for instant results, even with years of data.
- ✅ **Paginated History**: Comfortably browse your records, no matter how many you have.
- ✅ **SQLite Backend**: Robust and professional persistence in standard paths (XDG).
- ✅ **Multi-project**: Manage different work contexts independently.
- ✅ **Standardized Navigation**: Consistent use of keys for a better user experience.
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

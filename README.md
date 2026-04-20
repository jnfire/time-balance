# time-balance 🕒

> A lightweight, professional command-line tool to track your working hours and manage your accumulated balance.

[Leer en español 🇪🇸](README.es.md)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Description

`time-balance` is a CLI application designed for people who need rigorous control over their worked time. It automatically calculates the daily difference against a base workday (7h 45m by default) and maintains an accumulated balance so you always know if you "owe" hours or have a surplus.

---

## Quick Installation

```bash
# Clone and enter directory
git clone <repo-url>
cd time-balance

# Install the application
python3 -m pip install .
```

---

## Usage

### 1. Interactive Menu (Recommended)
Simply run the command to open the control center:

```bash
time-balance
```

The interface automatically detects your system language (supports English and Spanish). You can register new days, view recent history, or import/export your data.

### 2. Quick Commands (Direct Mode)
Consult your status without entering the menu:

```bash
# Show current accumulated balance only
time-balance --status

# List last 10 recorded days
time-balance --list 10

# Force a specific language
time-balance --lang en

# Check installed version
time-balance --version
```

---

## Key Features

- ✅ **Agile Registration**: Input hours and minutes easily.
- ✅ **Safety First**: Atomic data writing and automatic backups for critical operations.
- ✅ **Multi-language**: Seamlessly switch between English and Spanish.
- ✅ **Flexible Import**: Merge histories from different devices or restore full copies.
- ✅ **Zero Dependencies**: 100% Standard Python. Works on Windows, macOS, and Linux.
- ✅ **Privacy-Focused**: All data is stored locally in a readable JSON file.

---

## Advanced Configuration

### History Location
By default, the app creates `historial_hours.json` in the current folder. To centralize it, define the environment variable:

```bash
export HISTORIAL_PATH="~/.config/time-balance/my_history.json"
```

### Base Workday
The app defaults to **7h 45m**. If your workday is different, you can modify the constants in `time_balance/constants.py` and reinstall, or configure it via the interactive menu.

---

## Future Steps (Roadmap) 🚀

We are working to take `time-balance` to the next level:

- 🗄️ **SQLite Migration**: Evolving internal storage to a robust database for better integrity and speed, keeping JSON as the standard for import/export.
- 📂 **Multi-project Management**: Switch between different work contexts from a single centralized installation.
- ☁️ **Smart Sync**: Simplified data location settings for cloud folders (Dropbox, iCloud, Drive) and automatic backups.
- 🎨 **Rich UI**: Enhanced terminal experience using modern libraries for clearer tables, colors, and better usability.

---

## Development and Contributions

If you want to contribute or understand how it works internally:
- [**ARCHITECTURE.md**](docs/ARCHITECTURE.md): System design and modules.
- [**DEVELOPMENT.md**](docs/DEVELOPMENT.md): Technical guide for developers.
- [**CONTRIBUTING.md**](docs/CONTRIBUTING.md): How to submit improvements and translations.

## License

This project is Open Source under the [GPL-3.0](LICENSE) license.

# time-balance 🕒

> A professional, global terminal tool to manage multiple projects, track workdays, and manage your hour balance.

[Leer en español 🇪🇸](README.es.md)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Description

`time-balance` is a **global** console application designed for productivity. It no longer depends on local files; all your projects and records are stored in a centralized SQLite database. It features a domain-driven modular architecture, a decoupled UI layer, and a robust localization system.

---

## Installation

### From Distribution Files (Release)
If you have downloaded the release files (e.g., `time_balance-0.5.0-py3-none-any.whl`), you can install it directly:

```bash
# Install the Wheel file
pip install time_balance-0.5.0-py3-none-any.whl
```

### From Source
To install the application from the source code:

```bash
# Clone and enter directory
git clone <repo-url>
cd time-balance

# Install globally
pip install .
```

### For Developers
If you want to contribute, we recommend using the direct entry point:

```bash
# Run without installing
./main.py --version
```

---

## Usage

### 1. Control Center (Interactive Menu)
Simply run the command from any folder to open the manager:

```bash
time-balance
```

### 2. Intuitive Navigation
The interface uses a standardized navigation system:
- **Numbers (1-5)** to select main actions.
- **Letters (V, N, P)** for navigation: `V` to go back, `N`/`P` to navigate history pages.

### 3. Quick Commands
Check your status without entering the menu:

```bash
# Show balance for the active project
time-balance --status

# List last 10 records for the active project
time-balance --list 10
```

---

## Main Features

- ✅ **Domain-Driven Architecture**: Clean separation between CLI, Database, and UI logic.
- ✅ **UI Abstraction**: Decoupled from visual libraries for maximum flexibility.
- ✅ **JSON-Based Localization**: Easily add new languages via external JSON files.
- ✅ **High-Performance Caching**: Atomic balance updates for instant results.
- ✅ **SQLite Backend**: Robust persistence following XDG standards.
- ✅ **Multi-project**: Manage different work contexts independently.

---

## Development and Contributions

If you want to contribute or understand the internals:
- [**ARCHITECTURE.md**](docs/ARCHITECTURE.md): System design, modules, and domain structure.
- [**DEVELOPMENT.md**](docs/DEVELOPMENT.md): Technical guide for developers.
- [**CONTRIBUTING.md**](docs/CONTRIBUTING.md): How to submit improvements and translations.

## License

This project is Open Source under the [GPL-3.0](LICENSE) license.

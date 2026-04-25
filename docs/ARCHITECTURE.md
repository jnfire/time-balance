# Project Architecture

## Overview

`time-balance` is a professional terminal application designed to track working hours and manage accumulated balances. As of version 0.5.0, the application features a **domain-driven modular architecture**, a decoupled UI layer, and a robust JSON-based localization system.

## Project Structure

The application has been restructured from a monolithic package into specialized functional domains:

```
time-balance/
├── main.py                   # Direct entry point for development
├── setup.py                  # Packaging and distribution configuration
├── time_balance/             # Core application source
│   ├── cli/                  # Presentation domain (Menu logic)
│   │   ├── main.py           # CLI orchestrator and entry point
│   │   ├── registration.py   # Workday entry flows
│   │   ├── history.py        # Record visualization and pagination
│   │   └── ...               # Submenus (projects, config, migration)
│   ├── database/             # Persistence domain
│   │   └── manager.py        # SQLite DatabaseManager (DRY logic)
│   ├── i18n/                 # Localization domain
│   │   ├── translator.py     # Caching translation engine
│   │   └── locales/*.json    # Externalized string definitions
│   ├── ui/                   # UI Abstraction layer
│   │   └── interface.py      # Decoupling bridge (Rich implementation)
│   ├── utils/                # Cross-cutting concerns
│   │   ├── calculations.py   # Math and formatting
│   │   └── files.py          # Atomic I/O operations
│   ├── config.py             # Application-wide configuration
│   └── VERSION               # Single source of truth for versioning
├── tests/                    # Domain-aware test suite
└── docs/                     # Technical documentation
```

## Architectural Principles

### 1. **UI Decoupling (Abstration Layer)**
The application is decoupled from the `Rich` library via `ui/interface.py`. All visual components (headers, tables, prompts) are called through generic methods. This allows for future frontend migrations (e.g., to Textual or a web API) without touching business logic.

### 2. **Domain-Driven Modularization**
- **`cli/`**: Handles user flow and input validation. Divided into small, themed files.
- **`database/`**: Centralizes all persistence logic. The `DatabaseManager` handles atomic updates and balance caching.
- **`i18n/`**: A standalone domain for localization. Supports dynamic JSON loading, caching, and automatic fallback to English.

### 3. **Clean Code & Naming Standards**
- **Descriptive Naming**: All variables and functions follow a strict "No single-letter" rule (minimum 3 characters).
- **DRY (Don't Repeat Yourself)**: Bulk operations (like record imports) are centralized in the database layer.

## Data Flow and Performance

The application uses an **incremental caching strategy** for total balances:
- **O(1) Access**: The `total_balance` is cached in the `projects` table.
- **Atomic Updates**: Each record operation triggers a delta-update to the project balance.
- **Persistence**: Powered by SQLite with standard system path resolution (XDG compliance).

## Testing Strategy

The test suite follows the modular architecture:
- **Unit Tests**: Mathematical logic in `test_core`.
- **Integration Tests**: Database transactions in `test_storage` and `test_balance_cache`.
- **UI Mocking**: `test_cli` uses the UI Abstraction Layer to simulate interactions without requiring a real terminal.

## Distribution

As a professional tool, `time-balance` is distributed as a Python package but functions as a standalone executable. The `setup.py` and `MANIFEST.in` ensure that all non-Python assets (JSON locales, version files) are correctly bundled.

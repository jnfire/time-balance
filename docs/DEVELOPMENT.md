# Developer Guide

This guide provides technical details for developers who want to integrate with `time-balance` or contribute to its development.

## Project Philosophy

- **Standard Library Only**: No external dependencies allowed for the core functionality.
- **Clean Code**: Descriptive naming, modularity, and high test coverage.
- **Safety**: Atomic writes and defensive data validation.

## Module Structure

The project is organized into logical layers:

### 1. Business Logic (`core.py`)
Pure functions for time calculations.
- `format_time(minutes)`: Returns strings like `"-1h 30m"`.
- `calculate_total_balance(records)`: Sums differences from the data dictionary.

### 2. Persistence (`storage.py`)
Handles disk I/O and schema migrations.
- `load_data(path)`: Returns a structured dict with `metadata` and `registros`.
- `save_data(data, path)`: Atomic write via temporary files.

### 3. Data Exchange (`io.py`)
Logic for moving data between systems.
- `export_history(dest)`: Exports the full structured JSON.
- `import_history(src, mode)`: Validates and merges/overwrites data.

### 4. User Interface (`cli.py`)
The presentation layer using `argparse` and a loop-based menu.

### 5. Internationalization (`i18n.py`)
Simple translation engine. Uses `translate(key, lang)` to fetch strings.

## Running Tests

We use the standard `unittest` framework:

```bash
# Run all tests
python3 -m unittest discover -v tests
```

## Adding a New Language

1. Open `time_balance/i18n.py`.
2. Add a new entry to the `STRINGS` dictionary with the ISO 639-1 code (e.g., `"fr"` for French).
3. Translate all keys from the `"en"` template.
4. Update the `--lang` choices in `cli.py` (if needed, though it accepts any string).

## Data Schema Reference

```json
{
    "metadata": {
        "project_name": "string",
        "hours_base": "int",
        "minutos_base": "int",
        "version": "string",
        "language": "string (en|es|auto)"
    },
    "registros": {
        "YYYY-MM-DD": {
            "horas": "int",
            "minutos": "int",
            "diferencia": "int (worked_minutes - base_minutes)"
        }
    }
}
```

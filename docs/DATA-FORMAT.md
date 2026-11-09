# Data format

`time-balance` exports the history of the active project as a JSON file, and imports the same format. The file is plain text and can be edited by hand.

## Example

```json
{
    "metadata": {
        "project_name": "Example Project",
        "hours_base": 7,
        "minutes_base": 45,
        "version": "1.0",
        "language": "en"
    },
    "records": {
        "2026-04-15": { "hours": 8, "minutes": 0, "difference": 15 },
        "2026-04-16": { "hours": 7, "minutes": 45, "difference": 0 },
        "2026-04-17": { "hours": 6, "minutes": 30, "difference": -75 }
    }
}
```

A complete file is in [`examples/history_example.json`](../examples/history_example.json).

## Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `metadata.project_name` | text | Name of the project. Required. |
| `metadata.hours_base` | integer, 0 or more | Hours of the daily base. Required. |
| `metadata.minutes_base` | integer, 0 to 59 | Minutes of the daily base. Required. |
| `metadata.version`, `metadata.language` | text | Informational. |
| `records` | object | One entry per day, keyed by date as `YYYY-MM-DD`. Required. |
| `records.<date>.hours` | integer | Hours worked that day. |
| `records.<date>.minutes` | integer | Minutes worked that day. |
| `records.<date>.difference` | integer | Minutes above (positive) or below (negative) the daily base: `hours * 60 + minutes - base`. |

Every value of a record is required and must be an integer. A file that does not follow this is rejected, and the message names the problem.

## Import rules

- Records go into the **active project**. The name and the daily base of the file are not applied to it: they stay as they are.
- Two modes: **merge** (the default) replaces the days that already exist and keeps the rest, and **overwrite** deletes all the records of the project first.
- `difference` is stored as it comes in the file. It is not recalculated against the base of the project, so check it if the base differs.
- The accumulated balance is rebuilt from the records after the import.

"""Reading and writing the history file (see docs/DATA-FORMAT.md)."""

from __future__ import annotations

import contextlib
import errno
import json
import os
import pathlib
import shutil
import tempfile
from typing import Any

from .validation import parse_date

FORMAT_VERSION = "1.0"


def _require_int(
    value: Any, label: str, minimum: int | None = None, maximum: int | None = None
) -> None:
    """Checks that ``value`` is an integer (a bool is not one) inside the optional bounds."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{label} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be greater than or equal to {minimum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{label} must be less than or equal to {maximum}")


def _validate_metadata(metadata: Any) -> None:
    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be an object")
    for key in ("project_name", "hours_base", "minutes_base"):
        if key not in metadata:
            raise ValueError(f"Metadata missing required key: {key}")
    _require_int(metadata["hours_base"], "Metadata 'hours_base'", minimum=0)
    _require_int(metadata["minutes_base"], "Metadata 'minutes_base'", minimum=0, maximum=59)


def _validate_record(date_key: Any, info: Any) -> None:
    if not isinstance(date_key, str) or parse_date(date_key) != date_key:
        raise ValueError(f"Invalid date key: {date_key}. Must be YYYY-MM-DD")
    if not isinstance(info, dict):
        raise ValueError(f"Entry for {date_key} must be an object with hour/minute data.")
    for key in ("hours", "minutes", "difference"):
        if key not in info:
            raise ValueError(f"Entry for {date_key} is missing required key: {key}")
        _require_int(info[key], f"'{key}' in {date_key}")


def validate_history(data: Any) -> None:
    """Raises ``ValueError``, with a message naming the problem, if ``data`` is not valid."""
    if not isinstance(data, dict):
        raise ValueError("History must be a JSON object/dict")
    if "metadata" not in data or "records" not in data:
        raise ValueError("History missing required structured keys (metadata, records)")
    _validate_metadata(data["metadata"])
    if not isinstance(data["records"], dict):
        raise ValueError("Records must be an object")
    for date_key, info in data["records"].items():
        _validate_record(date_key, info)


def _fsync_directory(directory: pathlib.Path) -> None:
    """Best effort: not every platform lets a directory be opened and synced."""
    with contextlib.suppress(AttributeError, OSError):
        directory_fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)


def export_history(data: dict[str, Any], dest_path: str | os.PathLike[str]) -> pathlib.Path:
    """Writes ``data`` as JSON and returns the final path.

    The file is written next to the destination and then renamed over it, so an
    interrupted export never leaves a half-written file behind.
    """
    validate_history(data)
    destination = pathlib.Path(dest_path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    content = json.dumps(data, indent=4, ensure_ascii=False)
    descriptor, temp_name = tempfile.mkstemp(
        prefix="export_", suffix=".json", dir=destination.parent
    )
    temp_path = pathlib.Path(temp_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as temp_file:
            temp_file.write(content)
            temp_file.flush()
            with contextlib.suppress(OSError):
                os.fsync(temp_file.fileno())
        try:
            os.replace(temp_path, destination)
        except OSError as error:
            if error.errno != errno.EXDEV:
                raise
            shutil.copy2(temp_path, destination)
        _fsync_directory(destination.parent)
    finally:
        with contextlib.suppress(OSError):
            temp_path.unlink()
    return destination


def read_history_file(source_path: str | os.PathLike[str]) -> dict[str, Any]:
    """Reads and validates a history file. Raises ``FileNotFoundError`` or ``ValueError``."""
    source = pathlib.Path(source_path).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"File not found: {source}")
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in file: {error}") from error
    validate_history(data)
    return data

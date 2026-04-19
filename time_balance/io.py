import os
import json
import tempfile
import shutil
import errno
from datetime import datetime
from . import storage
from . import constants


def validate_history(data):
    """Validates basic history structure."""
    if not isinstance(data, dict):
        raise ValueError("History must be a JSON object/dict")
    
    if "metadata" not in data or "records" not in data:
        raise ValueError("History missing required structured keys (metadata, records)")

    # Validate metadata
    metadata = data["metadata"]
    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be an object")
    
    required_meta = ("project_name", "hours_base", "minutes_base")
    for key in required_meta:
        if key not in metadata:
            raise ValueError(f"Metadata missing required key: {key}")

    # Validate records
    records = data["records"]
    if not isinstance(records, dict):
        raise ValueError("Records must be an object")
    for date_key, info in records.items():
        _validate_record_entry(date_key, info)


def _validate_record_entry(date_key, info):
    """Validates a single record entry."""
    if not isinstance(date_key, str):
        raise ValueError("History keys must be strings (YYYY-MM-DD)")

    try:
        datetime.strptime(date_key, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date key: {date_key}. Must be YYYY-MM-DD")

    if not isinstance(info, dict):
        raise ValueError(f"Entry for {date_key} must be an object with hour/minute data.")

    required_keys = ('hours', 'minutes', 'difference')
    for key in required_keys:
        if key not in info:
            raise ValueError(f"Entry for {date_key} is missing required key: {key}")
        if not isinstance(info[key], int):
            raise ValueError(f"'{key}' in {date_key} must be an integer")


def export_history(dest_path, file_path=None):
    """Exports current history to external JSON."""
    data = storage.load_data(file_path)
    dest = os.path.expanduser(dest_path)
    dest = os.path.abspath(dest)
    dest_dir = os.path.dirname(dest)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    content = json.dumps(data, indent=4, ensure_ascii=False)
    file_descriptor, temp_path = tempfile.mkstemp(prefix="export_", suffix=".json", dir=dest_dir or ".")
    try:
        with os.fdopen(file_descriptor, 'w', encoding='utf-8') as temp_file:
            temp_file.write(content)
            try:
                temp_file.flush()
                os.fsync(temp_file.fileno())
            except Exception:
                pass

        try:
            os.replace(temp_path, dest)
        except OSError as error:
            if getattr(error, 'errno', None) == errno.EXDEV:
                shutil.copy2(temp_path, dest)
                os.remove(temp_path)
            else:
                raise
    finally:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

    return dest


def import_history(source_path, mode=constants.MODE_MERGE, file_path=None):
    """Imports history from external file."""
    source = os.path.expanduser(source_path)
    source = os.path.abspath(source)
    if not os.path.exists(source):
        raise FileNotFoundError(f"Import file not found: {source}")

    try:
        with open(source, 'r', encoding='utf-8') as json_file:
            source_data = json.load(json_file)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in import file: {error}")

    validate_history(source_data)
    
    target_path = storage._resolve_file_path(file_path)
    if mode == constants.MODE_OVERWRITE:
        storage._create_backup(target_path)
        storage.save_data(source_data, target_path)
        return source_data
    elif mode == constants.MODE_MERGE:
        storage._create_backup(target_path)
        current_data = storage.load_data(target_path)
        current_data["records"].update(source_data["records"])
        storage.save_data(current_data, target_path)
        return current_data
    else:
        raise ValueError(f"Unknown mode. Use {constants.MODOS_IMPORTACION_VALIDOS}.")

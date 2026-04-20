import os
import json
import tempfile
import shutil
import errno
from datetime import datetime
from . import constants


def _resolve_file_path(file_path=None):
    """Resolves the final history file path."""
    if file_path:
        path = file_path
    elif constants.ENV_HISTORIAL in os.environ and os.environ[constants.ENV_HISTORIAL].strip():
        path = os.environ[constants.ENV_HISTORIAL]
    else:
        path = constants.DATA_FILE

    path = os.path.expanduser(path)
    return os.path.abspath(path)


def _empty_data_skeleton():
    """Returns a fresh empty history structure."""
    return {
        "metadata": {
            "project_name": "General",
            "hours_base": constants.BASE_HOURS,
            "minutes_base": constants.BASE_MINUTES,
            "version": "1.0",
            "language": "auto"
        },
        "records": {}
    }


def _normalize_legacy_record(record):
    """Normalizes a single record, mapping legacy Spanish keys to current English names."""
    if not isinstance(record, dict):
        return record

    key_map = {
        "horas": "hours",
        "minutos": "minutes",
        "diferencia": "difference",
        "comentario": "comment",
        "nota": "comment",
    }

    normalized = {}
    for key, value in record.items():
        normalized[key_map.get(key, key)] = value
    return normalized


def _normalize_loaded_data(data):
    """Returns data in the current structured schema, migrating legacy formats."""
    default_data = _empty_data_skeleton()

    if not isinstance(data, dict):
        return default_data

    # Case 1: Already structured (v0.2+)
    if "metadata" in data or "records" in data:
        metadata = data.get("metadata", {})
        records = data.get("records", {})

        if not isinstance(metadata, dict):
            metadata = {}
        if not isinstance(records, dict):
            records = {}

        # Normalize metadata keys (e.g. minutos_base -> minutes_base)
        meta_key_map = {
            "minutos_base": "minutes_base",
            "idioma": "language",
            "nombre_proyecto": "project_name",
        }
        
        normalized_metadata = default_data["metadata"].copy()
        for key, value in metadata.items():
            normalized_metadata[meta_key_map.get(key, key)] = value

        normalized_records = {}
        for key, value in records.items():
            normalized_records[key] = _normalize_legacy_record(value)

        return {
            "metadata": normalized_metadata,
            "records": normalized_records
        }

    # Case 2: Legacy flat history (v0.1)
    legacy_records = {}
    for key, value in data.items():
        legacy_records[key] = _normalize_legacy_record(value)

    return {
        "metadata": default_data["metadata"].copy(),
        "records": legacy_records
    }


def load_data(file_path=None):
    """Loads history from the structured JSON file with automatic migration."""
    path = _resolve_file_path(file_path)
    
    # Return empty skeleton if file doesn't exist
    if not os.path.exists(path):
        return _empty_data_skeleton()
        
    try:
        with open(path, "r", encoding="utf-8") as json_file:
            return _normalize_loaded_data(json.load(json_file))
    except (ValueError, json.JSONDecodeError):
        # On error, return an empty structure safely without recursion
        return _empty_data_skeleton()


def save_data(data, file_path=None):
    """Saves complete history using atomic writing and directory fsync."""
    path = _resolve_file_path(file_path)
    dest_dir = os.path.dirname(path) or "."
    if dest_dir != "." and not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    content = json.dumps(data, indent=4, ensure_ascii=False)
    fd, temp_path = tempfile.mkstemp(prefix="history_", suffix=".json", dir=dest_dir)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as temp_file:
            temp_file.write(content)
            temp_file.flush()
            try:
                os.fsync(temp_file.fileno())
            except OSError:
                pass # Some platforms/filesystems don't support fsync on files

        try:
            os.replace(temp_path, path)
        except OSError as error:
            if getattr(error, 'errno', None) == errno.EXDEV:
                shutil.copy2(temp_path, path)
                os.remove(temp_path)
            else:
                raise

        # Best-effort directory fsync for crash-safety
        try:
            dir_fd = os.open(dest_dir, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except (AttributeError, OSError):
            pass # Windows or some older Unixes might not support fsync on directories

    finally:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


def _create_backup(file_path):
    """Creates a timestamped backup of the given file."""
    if not os.path.exists(file_path):
        return None
    timestamp = datetime.now().strftime('%Y%m%dT%H%M%S')
    backup = f"{file_path}.bak.{timestamp}"
    shutil.copy2(file_path, backup)
    try:
        shutil.copy2(file_path, f"{file_path}.bak")
    except Exception:
        pass
    return backup
